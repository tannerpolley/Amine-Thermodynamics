from __future__ import annotations

import math
from dataclasses import dataclass

from MEA.epcsaft_ionic.preregistration import load_gate0_preregistration
from MEA.epcsaft_ionic.parameter_document import load_parameters
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


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


def build_reduced_tracer_input() -> ReducedTracerInput:
    """Build the two-row homogeneous-liquid evaluator from frozen MEA inputs."""

    import epcsaft
    from epcsaft import equilibrium

    preregistration = load_gate0_preregistration()
    tracer = preregistration["tracer"]
    observations = tracer["observations"]
    coordinates = tracer["active_coordinates"]
    temperature_k = float(observations[0]["temperature_k"])
    pressure_pa = float(observations[0]["state_pressure_pa"])
    if temperature_k != float(observations[1]["temperature_k"]) or pressure_pa != float(
        observations[1]["evaluation_pressure_pa"]
    ):
        raise ValueError("reduced tracer rows do not share the frozen fixed state")

    parameters = load_parameters()
    loading = float(observations[0]["loading_mol_co2_per_mol_mea"])
    mass_fraction = float(observations[0]["mea_mass_fraction_unloaded"])
    observation_problem = build_homogeneous_reactive_problem(
        parameters,
        identity="mea-gate0-stage3-homogeneous-tracer",
        phase_identity="mea-nine-species-liquid",
        continuation_identity="mea-gate0-local-liquid-branch",
        temperature_k=temperature_k,
        pressure_pa=pressure_pa,
        mea_mass_fraction_unloaded=mass_fraction,
        loading_mol_co2_per_mol_mea=loading,
        maximum_log_composition_distance=0.5,
        maximum_log_volume_distance=0.5,
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
