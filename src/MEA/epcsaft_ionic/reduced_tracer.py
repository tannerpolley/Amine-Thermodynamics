from __future__ import annotations

import csv
import math
from dataclasses import dataclass, replace
from pathlib import Path
import numpy as np

from MEA.common.mea_source_contracts import (
    common_source_ln_k,
    load_reaction_contract,
)
from MEA.epcsaft_ionic.preregistration import load_gate0_preregistration
from MEA.epcsaft_ionic.parameter_document import (
    COMPONENT_IDS,
    PARAMETER_ROOT,
    load_parameters,
)


@dataclass(frozen=True)
class ReducedTracerInput:
    """Source-bound CAP-12 problem and numerical contract for Gate 0."""

    parameters: object
    problem: object
    rows: tuple[object, ...]
    active_parameter_identities: tuple[str, str]
    temperature_k: float
    pressure_pa: float
    observed_values: tuple[float, float]
    natural_log_scales: tuple[float, float]
    affine_origins: tuple[float, float]
    affine_scales: tuple[float, float]
    lower_bounds: tuple[float, float]
    upper_bounds: tuple[float, float]
    primary_start: tuple[float, float]
    confirmation_start: tuple[float, float]


def _reaction_consistent_molar_masses(
    bundle: Path,
    component_ids: tuple[str, ...],
    balance_matrix: tuple[tuple[float, ...], ...],
) -> tuple[float, ...]:
    """Project source-rounded masses onto the exact elemental-balance space.

    The Engine bundle remains the EOS owner. This application-side vector is
    used only by Equilibrium's redundant mass-conservation certificate.
    """

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


def build_reduced_tracer_input() -> ReducedTracerInput:
    """Build the two-row homogeneous-liquid evaluator from frozen MEA inputs."""

    import epcsaft
    from epcsaft import equilibrium

    preregistration = load_gate0_preregistration()
    reaction_contract = load_reaction_contract()

    tracer = preregistration["tracer"]
    observations = tracer["observations"]
    coordinates = tracer["active_coordinates"]
    temperature_k = float(observations[0]["temperature_k"])
    pressure_pa = float(observations[0]["state_pressure_pa"])
    if temperature_k != float(observations[1]["temperature_k"]) or pressure_pa != float(
        observations[1]["evaluation_pressure_pa"]
    ):
        raise ValueError("reduced tracer rows do not share the frozen fixed state")

    component_ids = COMPONENT_IDS
    parameters = load_parameters()
    model = epcsaft.Mixture(parameters)

    source_species = reaction_contract["species"]
    element_order = tuple(reaction_contract["balance_row_order"])
    elemental_balance_matrix = tuple(
        tuple(float(species["formula"][element]) for species in source_species)
        for element in element_order
    )
    # Equilibrium seeds molar mass and charge itself. Carbon and nitrogen are
    # the two additional independent conserved rows needed for this 9x5 system.
    balance_matrix = (
        elemental_balance_matrix[element_order.index("C")],
        elemental_balance_matrix[element_order.index("N")],
    )
    loading = float(observations[0]["loading_mol_co2_per_mol_mea"])
    mass_fraction = float(observations[0]["mea_mass_fraction_unloaded"])
    molar_mass = _reported_molar_masses(PARAMETER_ROOT)
    water_amount = (
        (1.0 - mass_fraction)
        / mass_fraction
        * molar_mass["monoethanolamine"]
        / molar_mass["water"]
    )
    source_feed_amounts = (
        loading,
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
        source_reference_component_ids=component_ids,
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
    ln_k = common_source_ln_k(temperature_k, reaction_contract)
    reaction_matrix = tuple(
        tuple(float(value) for value in reaction["stoichiometry"])
        for reaction in reaction_contract["reactions"]
    )
    # The source feed defines the conserved totals. The equivalent strictly
    # positive seed below is generated only by declared reaction extents so
    # CAP-13 can form its exact fixed-support derivative chart without an
    # epsilon floor or changed material state.
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
    problem = equilibrium.ChemicalEquilibriumProblem(
        species_ids=component_ids,
        charges=tuple(int(species["charge"]) for species in source_species),
        molar_masses_kg_per_mol=_reaction_consistent_molar_masses(
            PARAMETER_ROOT,
            component_ids,
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
    phase = equilibrium.ProviderPhase(model, (1.0e-6, 0.74))
    unanchored = equilibrium.HomogeneousReactiveObservationProblem(
        identity="mea-gate0-stage3-homogeneous-tracer",
        phase_identity="mea-nine-species-liquid",
        phase_role="liquid",
        phase=phase,
        reaction_system=problem,
        continuation_identity="mea-gate0-local-liquid-branch",
        branch_policy="local_certified_role_selected_state",
    )
    continuation_reference = equilibrium.certify_homogeneous_continuation_reference(
        unanchored,
        temperature_k * epcsaft.unit_registry.kelvin,
        pressure_pa * epcsaft.unit_registry.pascal,
        maximum_log_composition_distance=0.5,
        maximum_log_volume_distance=0.5,
    )
    observation_problem = replace(
        unanchored, continuation_reference=continuation_reference
    )
    rows = (
        equilibrium.HomogeneousReactiveObservationRow(
            tracer["residual_vector"]["order"][0],
            "fugacity_pa",
            (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            support="positive",
        ),
        equilibrium.HomogeneousReactiveObservationRow(
            tracer["residual_vector"]["order"][1],
            "mole_fraction",
            (0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0),
            support="positive",
        ),
    )
    active_parameter_identities = (
        "component/protonated-monoethanolamine/segment_diameter",
        "component/carbamate-anion/segment_diameter",
    )
    active = epcsaft.ActiveParameterSet(parameters, active_parameter_identities)
    equilibrium.homogeneous_reactive_observation_descriptor(
        observation_problem, rows, active_parameters=active
    )
    starts = tracer["numerical_acceptance"]["declared_starts"]
    return ReducedTracerInput(
        parameters=parameters,
        problem=observation_problem,
        rows=rows,
        active_parameter_identities=active_parameter_identities,
        temperature_k=temperature_k,
        pressure_pa=pressure_pa,
        observed_values=tuple(float(row["observed_value"]) for row in observations),
        natural_log_scales=tuple(
            float(row["residual_scale"]) * math.log(10.0) for row in observations
        ),
        affine_origins=tuple(float(row["affine_origin"]) for row in coordinates),
        affine_scales=tuple(float(row["affine_scale"]) for row in coordinates),
        lower_bounds=tuple(float(row["bounds"][0]) for row in coordinates),
        upper_bounds=tuple(float(row["bounds"][1]) for row in coordinates),
        primary_start=tuple(float(value) for value in starts[0]["parameter_values"]),
        confirmation_start=tuple(
            float(value) for value in starts[1]["parameter_values"]
        ),
    )
