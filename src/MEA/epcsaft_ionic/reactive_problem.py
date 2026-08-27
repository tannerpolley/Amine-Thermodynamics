from __future__ import annotations

import csv
import math
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Literal

import numpy as np

from MEA.common.mea_source_contracts import (
    common_source_ln_k,
    load_reaction_contract,
)
from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, PARAMETER_ROOT

VAPOR_COMPONENT_IDS = ("carbon-dioxide", "monoethanolamine", "water")


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
    reaction_ln_k_adjustments: Mapping[str, float] | None = None,
    allow_reaction_extrapolation: bool = False,
    branch_policy: Literal[
        "local_certified_role_selected_state"
    ] = "local_certified_role_selected_state",
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
        raise ValueError(
            "reactive liquid state inputs are outside their physical support"
        )

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
    ln_k = common_source_ln_k(
        temperature_k,
        reaction_contract,
        allow_extrapolation=allow_reaction_extrapolation,
    )
    adjustments = dict(reaction_ln_k_adjustments or {})
    reaction_ids = {str(reaction["reaction_id"]) for reaction in reaction_contract["reactions"]}
    if set(adjustments) - reaction_ids or not all(
        math.isfinite(float(value)) for value in adjustments.values()
    ):
        raise ValueError("reaction ln(K) adjustments must be finite and keyed by R1-R5")
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
                ln_value=value + float(adjustments.get(reaction["reaction_id"], 0.0)),
                source_id="+".join(reaction["source_record_ids"])
                + (
                    f"+ln-k-adjustment:{float(adjustments[reaction['reaction_id']]):+.17g}"
                    if reaction["reaction_id"] in adjustments
                    else ""
                ),
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
        branch_policy=branch_policy,
    )
    reference = equilibrium.certify_homogeneous_continuation_reference(
        unanchored,
        temperature_k * epcsaft.unit_registry.kelvin,
        pressure_pa * epcsaft.unit_registry.pascal,
        maximum_log_composition_distance=maximum_log_composition_distance,
        maximum_log_volume_distance=maximum_log_volume_distance,
    )
    return replace(unanchored, continuation_reference=reference)


def build_reactive_bubble_problem(
    parameters: object,
    *,
    identity: str,
    liquid_phase_identity: str,
    vapor_phase_identity: str,
    liquid_continuation_identity: str,
    bubble_continuation_identity: str,
    temperature_k: float,
    liquid_reference_pressure_pa: float,
    mea_mass_fraction_unloaded: float,
    loading_mol_co2_per_mol_mea: float,
    pressure_interval_pa: tuple[float, float],
    pressure_starts_pa: tuple[float, ...],
    maximum_log_composition_distance: float = 0.5,
    maximum_log_volume_distance: float = 0.5,
    reaction_ln_k_adjustments: Mapping[str, float] | None = None,
) -> object:
    """Build the declared one-liquid/one-vapor reactive bubble problem.

    The homogeneous owner certifies the reacting liquid branch. The bubble
    owner consumes that exact state and solves only the declared neutral vapor
    and pressure closure; it does not perform phase-count or liquid-root search.
    """

    from epcsaft import equilibrium

    liquid = build_homogeneous_reactive_problem(
        parameters,
        identity=f"{identity}-liquid",
        phase_identity=liquid_phase_identity,
        continuation_identity=liquid_continuation_identity,
        temperature_k=temperature_k,
        pressure_pa=liquid_reference_pressure_pa,
        mea_mass_fraction_unloaded=mea_mass_fraction_unloaded,
        loading_mol_co2_per_mol_mea=loading_mol_co2_per_mol_mea,
        maximum_log_composition_distance=maximum_log_composition_distance,
        maximum_log_volume_distance=maximum_log_volume_distance,
        reaction_ln_k_adjustments=reaction_ln_k_adjustments,
    )
    return equilibrium.ReactiveBubbleVLEProblem(
        identity=identity,
        liquid_problem=liquid,
        vapor_phase_identity=vapor_phase_identity,
        vapor_component_ids=VAPOR_COMPONENT_IDS,
        vapor_model=equilibrium.ProviderNonidealVapor("installed-provider-eos"),
        pressure_interval_pa=pressure_interval_pa,
        pressure_starts_pa=pressure_starts_pa,
        continuation_identity=bubble_continuation_identity,
    )


__all__ = (
    "VAPOR_COMPONENT_IDS",
    "build_homogeneous_reactive_problem",
    "build_reactive_bubble_problem",
)
