from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from MEA.common.config import REPO_ROOT
from MEA.common.mea_source_contracts import (
    common_source_ln_k,
    load_reaction_contract,
    load_sentinel_contract,
    validate_reaction_contract,
    validate_sentinel_contract,
)
from MEA.epcsaft_ionic.preregistration import load_gate0_preregistration


@dataclass(frozen=True)
class ReducedTracerInput:
    """The source-bound evaluator handle and numerical contract for Gate 0."""

    evaluator: Any
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

    The Provider bundle remains the EOS owner. This application-side vector is
    used only by Equilibrium's redundant mass-conservation certificate.
    """

    with (bundle / "single.csv").open(newline="", encoding="utf-8") as handle:
        records = {
            row["component_id"]: float(row["value"])
            for row in csv.DictReader(handle)
            if row["family"] == "molar_mass"
    }
    if set(records) != set(component_ids):
        raise ValueError("Provider bundle does not contain one molar mass per component")
    reported = np.asarray(
        [records[component_id] for component_id in component_ids], dtype=float
    )
    balances = np.asarray(balance_matrix, dtype=float)
    elemental_masses, *_ = np.linalg.lstsq(balances.T, reported, rcond=None)
    projected = balances.T @ elemental_masses
    return tuple(float(value) for value in projected)


def build_reduced_tracer_input() -> ReducedTracerInput:
    """Build the two-row homogeneous-liquid evaluator from frozen MEA inputs."""

    import epcsaft
    import epcsaft_equilibrium

    preregistration = load_gate0_preregistration()
    reaction_contract = load_reaction_contract()
    sentinel_contract = load_sentinel_contract()
    validate_reaction_contract(reaction_contract)
    validate_sentinel_contract(sentinel_contract, reaction_contract)

    tracer = preregistration["tracer"]
    observations = tracer["observations"]
    coordinates = tracer["active_coordinates"]
    temperature_k = float(observations[0]["temperature_k"])
    pressure_pa = float(observations[0]["state_pressure_pa"])
    if (
        temperature_k != float(observations[1]["temperature_k"])
        or pressure_pa != float(observations[1]["evaluation_pressure_pa"])
    ):
        raise ValueError("reduced tracer rows do not share the frozen fixed state")

    provider_input = sentinel_contract["provider_regression_input"]
    immutable = provider_input["immutable_identities"]
    component_ids = tuple(sentinel_contract["provider_component_order"])
    bundle = REPO_ROOT / provider_input["bundle_path"]
    parameters = epcsaft.Parameters.from_bundle(bundle, components=component_ids)
    model = epcsaft.Mixture(parameters)
    if model.parameter_fingerprint != immutable["parameter_fingerprint"]:
        raise ValueError("installed Provider model differs from the frozen input")

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
    molar_mass = sentinel_contract["molar_mass_basis"]["values"]
    water_amount = (
        (1.0 - mass_fraction)
        / mass_fraction
        * float(molar_mass["MEA"])
        / float(molar_mass["H2O"])
    )
    feed_amounts = (loading, 1.0, water_amount, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    conserved_totals = tuple(
        math.fsum(
            row[index] * feed_amounts[index] for index in range(len(feed_amounts))
        )
        for row in balance_matrix
    )

    common = reaction_contract["common_source_standard_state"]
    standard_state = epcsaft_equilibrium.ChemicalStandardState(
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
    )
    ln_k = common_source_ln_k(temperature_k, reaction_contract)
    problem = epcsaft_equilibrium.ChemicalEquilibriumProblem(
        species_ids=component_ids,
        charges=tuple(int(species["charge"]) for species in source_species),
        molar_masses_kg_per_mol=_reaction_consistent_molar_masses(
            bundle,
            component_ids,
            elemental_balance_matrix,
        ),
        balance_matrix=balance_matrix,
        conserved_totals=conserved_totals,
        reaction_matrix=tuple(
            tuple(float(value) for value in reaction["stoichiometry"])
            for reaction in reaction_contract["reactions"]
        ),
        feed_amounts_mol=feed_amounts,
        equilibrium_constants=tuple(
            epcsaft_equilibrium.ChemicalEquilibriumConstant(
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
        strict_interior_amount_floor_mol=1.0e-18,
        source_standard_state=standard_state,
    )
    phase = epcsaft_equilibrium.ProviderPhase(
        model=model,
        expected_parameter_fingerprint=immutable["parameter_fingerprint"],
        admissible_packing_fraction_interval=(1.0e-6, 0.74),
    )
    rows = (
        epcsaft_equilibrium.ChemicalObservationRow(
            row_id=tracer["residual_vector"]["order"][0],
            state_id=observations[0]["state_id"],
            state_schema_id="fixed_TP_homogeneous_liquid_v1",
            source_id=observations[0]["source_id"],
            transform_id="natural_log",
            temperature=temperature_k * epcsaft.unit_registry.kelvin,
            pressure=pressure_pa * epcsaft.unit_registry.pascal,
            problem=problem,
            primitive=epcsaft_equilibrium.ChemicalObservationPrimitive(
                kind="neutral_component_fugacity_pa",
                component_id="carbon-dioxide",
            ),
        ),
        epcsaft_equilibrium.ChemicalObservationRow(
            row_id=tracer["residual_vector"]["order"][1],
            state_id=observations[1]["state_id"],
            state_schema_id="fixed_TP_homogeneous_liquid_v1",
            source_id=observations[1]["source_id"],
            transform_id="natural_log",
            temperature=temperature_k * epcsaft.unit_registry.kelvin,
            pressure=pressure_pa * epcsaft.unit_registry.pascal,
            problem=problem,
            primitive=epcsaft_equilibrium.ChemicalObservationPrimitive(
                kind="species_mole_fraction",
                component_id="carbamate-anion",
            ),
        ),
    )
    active_parameters = tuple(
        epcsaft_equilibrium.ChemicalEquilibriumActiveParameter(
            family="segment_diameter",
            identity="component",
            component_ids=(
                (
                    "protonated-monoethanolamine"
                    if coordinate["identity"] == "MEAH+::sigma"
                    else "carbamate-anion"
                ),
            ),
            value=float(coordinate["start"]),
            unit="angstrom",
        )
        for coordinate in coordinates
    )
    evaluator = epcsaft_equilibrium.chemical_observation_context(
        phase,
        rows=rows,
        active_parameters=active_parameters,
    )
    expected_parameter_ids = (
        "segment_diameter;component;protonated-monoethanolamine",
        "segment_diameter;component;carbamate-anion",
    )
    if evaluator.parameter_ids != expected_parameter_ids:
        raise ValueError("installed evaluator changed the frozen parameter order")
    starts = tracer["numerical_acceptance"]["declared_starts"]
    return ReducedTracerInput(
        evaluator=evaluator,
        observed_values=tuple(float(row["observed_value"]) for row in observations),
        natural_log_scales=tuple(
            float(row["residual_scale"]) * math.log(10.0)
            for row in observations
        ),
        affine_origins=tuple(float(row["affine_origin"]) for row in coordinates),
        affine_scales=tuple(float(row["affine_scale"]) for row in coordinates),
        lower_bounds=tuple(float(row["bounds"][0]) for row in coordinates),
        upper_bounds=tuple(float(row["bounds"][1]) for row in coordinates),
        primary_start=tuple(float(value) for value in starts[0]["parameter_values"]),
        confirmation_start=tuple(float(value) for value in starts[1]["parameter_values"]),
    )
