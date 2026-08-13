from __future__ import annotations

import csv
import math
from dataclasses import replace
from pathlib import Path

import numpy as np

from MEA.common.mea_source_contracts import (
    common_source_ln_k,
    load_reaction_contract,
)
from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, PARAMETER_ROOT


def _reaction_consistent_molar_masses(
    bundle: Path,
    component_ids: tuple[str, ...],
    balance_matrix: tuple[tuple[float, ...], ...],
) -> tuple[float, ...]:
    """Project source-rounded masses onto the exact elemental-balance space."""

    with (bundle / "single.csv").open(newline="", encoding="utf-8") as handle:
        records = {
            row["component_id"]: float(row["value"])
            for row in csv.DictReader(handle)
            if row["family"] == "molar_mass"
        }
    if set(records) != set(component_ids):
        raise ValueError("Engine bundle does not contain one molar mass per component")
    reported = np.asarray(
        [records[component_id] for component_id in component_ids], dtype=float
    )
    balances = np.asarray(balance_matrix, dtype=float)
    elemental_masses, *_ = np.linalg.lstsq(balances.T, reported, rcond=None)
    projected = balances.T @ elemental_masses
    return tuple(float(value) for value in projected)


def _reported_molar_masses(bundle: Path) -> dict[str, float]:
    with (bundle / "single.csv").open(newline="", encoding="utf-8") as handle:
        return {
            row["component_id"]: float(row["value"])
            for row in csv.DictReader(handle)
            if row["family"] == "molar_mass"
        }


def build_homogeneous_reactive_problem(
    parameters: object,
    *,
    identity: str,
    phase_identity: str,
    continuation_identity: str,
    temperature_k: float,
    pressure_pa: float,
    mea_mass_fraction_unloaded: float,
    loading_mol_co2_per_mol_mea: float,
    maximum_log_composition_distance: float = 0.5,
    maximum_log_volume_distance: float = 0.5,
) -> object:
    """Build and anchor the canonical nine-species fixed-``T,P`` liquid problem."""

    import epcsaft
    from epcsaft import equilibrium

    if not (
        math.isfinite(temperature_k)
        and temperature_k > 0.0
        and math.isfinite(pressure_pa)
        and pressure_pa > 0.0
        and math.isfinite(mea_mass_fraction_unloaded)
        and 0.0 < mea_mass_fraction_unloaded < 1.0
        and math.isfinite(loading_mol_co2_per_mol_mea)
        and loading_mol_co2_per_mol_mea > 0.0
    ):
        raise ValueError("reactive liquid state inputs are outside their physical support")

    reaction_contract = load_reaction_contract()
    source_species = reaction_contract["species"]
    element_order = tuple(reaction_contract["balance_row_order"])
    elemental_balance_matrix = tuple(
        tuple(float(species["formula"][element]) for species in source_species)
        for element in element_order
    )
    # Equilibrium supplies mass and charge constraints; carbon and nitrogen
    # are the two additional independent conserved rows for this 9x5 system.
    balance_matrix = (
        elemental_balance_matrix[element_order.index("C")],
        elemental_balance_matrix[element_order.index("N")],
    )
    molar_mass = _reported_molar_masses(PARAMETER_ROOT)
    water_amount = (
        (1.0 - mea_mass_fraction_unloaded)
        / mea_mass_fraction_unloaded
        * molar_mass["monoethanolamine"]
        / molar_mass["water"]
    )
    source_feed_amounts = (
        loading_mol_co2_per_mol_mea,
        1.0,
        water_amount,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )
    conserved_totals = tuple(
        math.fsum(
            row[index] * source_feed_amounts[index]
            for index in range(len(source_feed_amounts))
        )
        for row in balance_matrix
    )
    common = reaction_contract["common_source_standard_state"]
    standard_state = equilibrium.ChemicalStandardState(
        id=common["identity"],
        activity_scale_id=common["identity"],
        log_activity_scale_factors=tuple(
            common["log_activity_scale_factors_by_species"]
        ),
        reference_pressure_pa=float(
            reaction_contract["provider_transform"]["deterministic_payload"][
                "source_standard_reference_pressure_pa"
            ]
        ),
        source_reference_component_ids=COMPONENT_IDS,
        source_reference_solvent_composition=(
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ),
        source_reference_ion_pairs=(
            epcsaft.SourceReferenceIonPair(
                ("protonated-monoethanolamine", "carbamate-anion"), (1, 1)
            ),
            epcsaft.SourceReferenceIonPair(
                ("protonated-monoethanolamine", "bicarbonate-anion"), (1, 1)
            ),
            epcsaft.SourceReferenceIonPair(
                ("protonated-monoethanolamine", "carbonate-anion"), (2, 1)
            ),
            epcsaft.SourceReferenceIonPair(
                ("protonated-monoethanolamine", "hydroxide-anion"), (1, 1)
            ),
            epcsaft.SourceReferenceIonPair(
                ("hydronium-cation", "carbamate-anion"), (1, 1)
            ),
        ),
        source_reference_phase="liquid",
        source_reference_convention="molality-infinite-dilution",
        source_reference_activity_convention_id="molality-infinite-dilution-v1",
        source_reference_standard_molality_mol_per_kg=float(
            common["solute_standard_molality_mol_per_kg"]
        ),
    )
    reaction_matrix = tuple(
        tuple(float(value) for value in reaction["stoichiometry"])
        for reaction in reaction_contract["reactions"]
    )
    # This strictly positive seed is generated only through declared reaction
    # extents, so it preserves the source feed's conserved totals exactly.
    seed_extents = (1.0e-5, 1.0e-4, 1.0e-5, -1.0e-5, -1.0e-5)
    feed_amounts = tuple(
        source_feed_amounts[species_index]
        + math.fsum(
            reaction_matrix[reaction_index][species_index] * extent
            for reaction_index, extent in enumerate(seed_extents)
        )
        for species_index in range(len(source_feed_amounts))
    )
    if any(value <= 0.0 for value in feed_amounts):
        raise ValueError("reaction-generated solver seed is not strictly positive")
    ln_k = common_source_ln_k(temperature_k, reaction_contract)
    reaction_system = equilibrium.ChemicalEquilibriumProblem(
        species_ids=COMPONENT_IDS,
        charges=tuple(int(species["charge"]) for species in source_species),
        molar_masses_kg_per_mol=_reaction_consistent_molar_masses(
            PARAMETER_ROOT,
            COMPONENT_IDS,
            elemental_balance_matrix,
        ),
        balance_matrix=balance_matrix,
        conserved_totals=conserved_totals,
        reaction_matrix=reaction_matrix,
        feed_amounts_mol=feed_amounts,
        equilibrium_constants=tuple(
            equilibrium.ChemicalEquilibriumConstant(
                ln_value=value,
                source_id="+".join(reaction["source_record_ids"]),
                reference_id=common["identity"],
                reaction_orientation="products_positive",
                conversion_id="source-standard-state-to-provider-neutral-reference",
                dimensionless=True,
            )
            for reaction, value in zip(
                reaction_contract["reactions"], ln_k, strict=True
            )
        ),
        strict_interior_amount_floor_mol=1.0e-12,
        source_standard_state=standard_state,
    )
    model = epcsaft.Mixture(parameters)
    unanchored = equilibrium.HomogeneousReactiveObservationProblem(
        identity=identity,
        phase_identity=phase_identity,
        phase_role="liquid",
        phase=equilibrium.ProviderPhase(model, (1.0e-6, 0.74)),
        reaction_system=reaction_system,
        continuation_identity=continuation_identity,
        branch_policy="local_certified_role_selected_state",
    )
    reference = equilibrium.certify_homogeneous_continuation_reference(
        unanchored,
        temperature_k * epcsaft.unit_registry.kelvin,
        pressure_pa * epcsaft.unit_registry.pascal,
        maximum_log_composition_distance=maximum_log_composition_distance,
        maximum_log_volume_distance=maximum_log_volume_distance,
    )
    return replace(unanchored, continuation_reference=reference)


__all__ = ("build_homogeneous_reactive_problem",)
