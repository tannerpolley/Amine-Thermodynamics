from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

import numpy as np
from scipy.optimize import least_squares

import epcsaft
from epcsaft import equilibrium

import generate as study
from MEA.common.analysis_io import write_csv_rows as _write_csv
from MEA.epcsaft_ionic.preregistration import load_gate0_preregistration
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results" / "ion_diameter_fit"
FIXED_STATES = ANALYSIS / "results" / "state_results.csv"
ACTIVE_IDENTITIES = (
    "component/protonated-monoethanolamine/segment_diameter",
    "component/carbamate-anion/segment_diameter",
)
MINIMUM_LIQUID_DENSITY_KG_M3 = 500.0


def _fixed_state_rows() -> list[dict[str, str]]:
    with FIXED_STATES.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _fit_is_admissible(configuration_id: str, rows: list[dict[str, str]]) -> bool:
    selected = [row for row in rows if row["configuration_id"] == configuration_id]
    return len(selected) == len(study.LOADINGS) and all(
        row["status"] == "evaluated"
        and float(row["mass_density_kg_m3"]) >= MINIMUM_LIQUID_DENSITY_KG_M3
        for row in selected
    )


def _direct_rows(state: dict[str, object]) -> tuple[tuple[object, ...], np.ndarray]:
    rows = []
    observed = []
    for source in state["rows"]:
        species = source["species"]
        if (
            source["measurement_role"] != "direct_positive"
            or species not in study.SPECIES_COEFFICIENTS
            or float(source["value_mole_fraction"]) <= 0.0
        ):
            continue
        coefficients = study.SPECIES_COEFFICIENTS[species]
        rows.append(
            equilibrium.HomogeneousReactiveObservationRow(
                source["record_id"],
                "mole_fraction",
                tuple(
                    coefficients.get(component_id, 0.0)
                    for component_id in study.COMPONENT_IDS
                ),
                support="positive",
            )
        )
        observed.append(float(source["value_mole_fraction"]))
    return tuple(rows), np.asarray(observed, dtype=float)


def _fit_configuration(
    configuration: tuple[str, str, str, float, float, bool],
    source_states: list[dict[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    (
        configuration_id,
        configuration_name,
        permittivity,
        c_shell,
        c_dielectric,
        induced,
    ) = configuration
    parameters, mapping = study._configuration(
        permittivity, c_shell, c_dielectric, induced
    )
    active = epcsaft.ActiveParameterSet(parameters, ACTIVE_IDENTITIES)
    preregistered = load_gate0_preregistration()["tracer"]["active_coordinates"]
    lower = np.asarray([row["bounds"][0] for row in preregistered], dtype=float)
    upper = np.asarray([row["bounds"][1] for row in preregistered], dtype=float)
    prepared = []
    previous_reference = None
    for state in source_states:
        loading = float(state["loading"])
        for start_budget, initial_reference in ((2, previous_reference), (5, None)):
            try:
                problem = build_homogeneous_reactive_problem(
                    parameters,
                    identity=f"ion-diameter-fit-{configuration_id}-{loading:g}",
                    phase_identity="mea-nine-species-liquid",
                    continuation_identity=f"ion-diameter-fit-{configuration_id}-branch",
                    temperature_k=study.TEMPERATURE_K,
                    pressure_pa=study.PRESSURE_PA,
                    mea_mass_fraction_unloaded=study.MEA_MASS_FRACTION,
                    loading_mol_co2_per_mol_mea=loading,
                    maximum_log_composition_distance=2.0,
                    maximum_log_volume_distance=2.0,
                    solver_options={
                        "maximum_iterations": 100,
                        "convergence_tolerance": 1.0e-6,
                        "primary_start_budget": start_budget,
                    },
                    initial_reference=initial_reference,
                )
                break
            except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError):
                if initial_reference is None:
                    raise
        rows, observed = _direct_rows(state)
        descriptor = equilibrium.homogeneous_reactive_observation_descriptor(
            problem, rows, active_parameters=active
        )
        prepared.append((loading, problem, descriptor, observed, rows))
        previous_reference = problem.continuation_reference

    cache: dict[str, object] = {}
    evaluation_count = 0

    def evaluate(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[object]]:
        nonlocal evaluation_count
        key = tuple(float(value) for value in values)
        if cache.get("key") == key:
            return cache["value"]
        residuals = []
        jacobians = []
        evaluations = []
        trial = epcsaft.ActiveParameterSet(parameters, ACTIVE_IDENTITIES, values=key)
        for loading, problem, descriptor, observed, _ in prepared:
            result = equilibrium.evaluate_homogeneous_reactive_observations(
                problem,
                study.TEMPERATURE_K * epcsaft.unit_registry.kelvin,
                study.PRESSURE_PA * epcsaft.unit_registry.pascal,
                descriptor,
                active_parameters=trial,
            )
            if result.status != "evaluated":
                raise RuntimeError(
                    f"{configuration_id} became non-evaluable at loading {loading:g}: "
                    f"{result.failure}"
                )
            predicted = np.asarray(result.values, dtype=float)
            residuals.append(np.log(predicted / observed))
            jacobians.append(
                np.asarray(result.jacobian, dtype=float) / predicted[:, None]
            )
            evaluations.append(result)
        value = (np.concatenate(residuals), np.vstack(jacobians), evaluations)
        evaluation_count += 1
        cache.update(key=key, value=value)
        return value

    started = time.monotonic()
    base_residual, _, _ = evaluate(np.asarray(active.values, dtype=float))
    fit = least_squares(
        lambda values: evaluate(values)[0],
        np.asarray(active.values, dtype=float),
        jac=lambda values: evaluate(values)[1],
        bounds=(lower, upper),
        ftol=1.0e-6,
        gtol=1.0e-6,
        xtol=1.0e-6,
        max_nfev=10,
        x_scale="jac",
    )
    final_residual, final_jacobian, final_evaluations = evaluate(fit.x)
    singular_values = np.linalg.svd(final_jacobian, compute_uv=False)
    prediction_rows = []
    for (loading, _, _, observed, rows), evaluated in zip(
        prepared, final_evaluations, strict=True
    ):
        for row, observation, prediction in zip(
            rows, observed, evaluated.values, strict=True
        ):
            prediction_rows.append(
                {
                    "configuration_id": configuration_id,
                    "configuration_name": configuration_name,
                    "loading_mol_co2_per_mol_mea": loading,
                    "record_id": row.identity,
                    "observed_mole_fraction": observation,
                    "predicted_mole_fraction": prediction,
                    "log_model_over_observed": math.log(prediction / observation),
                }
            )
    parameter_rows = [
        {
            "configuration_id": configuration_id,
            "configuration_name": configuration_name,
            "parameter_identity": identity,
            "unit": "angstrom",
            "origin": origin,
            "fitted": fitted,
            "lower_bound": lo,
            "upper_bound": hi,
            "at_bound": math.isclose(fitted, lo, abs_tol=1.0e-6)
            or math.isclose(fitted, hi, abs_tol=1.0e-6),
        }
        for identity, origin, fitted, lo, hi in zip(
            ACTIVE_IDENTITIES, active.values, fit.x, lower, upper, strict=True
        )
    ]
    summary = {
        "configuration_id": configuration_id,
        "configuration_name": configuration_name,
        "status": "completed" if fit.success else "iteration_limit",
        "induced_association": induced,
        "relative_permittivity_formulation": permittivity,
        "born_c_shell": c_shell,
        "born_c_dielectric": c_dielectric,
        "parameter_mapping_sha256": study._canonical_sha256(mapping),
        "observation_count": int(final_residual.size),
        "state_count": len(prepared),
        "base_log_sse": float(base_residual @ base_residual),
        "final_log_sse": float(final_residual @ final_residual),
        "typical_speciation_factor": math.exp(
            statistics.median(abs(float(value)) for value in final_residual)
        ),
        "log_rmse": float(np.sqrt(np.mean(final_residual**2))),
        "evaluation_count": evaluation_count,
        "solver_status": int(fit.status),
        "solver_message": fit.message,
        "optimality": float(fit.optimality),
        "jacobian_singular_values": singular_values.tolist(),
        "jacobian_condition_number": float(singular_values[0] / singular_values[-1]),
        "runtime_seconds": time.monotonic() - started,
    }
    return summary, parameter_rows, prediction_rows


def main() -> None:
    started = time.monotonic()
    fixed_rows = _fixed_state_rows()
    source_states = study._source_states()
    summaries = []
    parameters = []
    predictions = []
    for configuration in study.CONFIGURATIONS:
        configuration_id, configuration_name, *rest = configuration
        if not _fit_is_admissible(configuration_id, fixed_rows):
            summaries.append(
                {
                    "configuration_id": configuration_id,
                    "configuration_name": configuration_name,
                    "status": "not_fitted_no_liquid_base_branch",
                    "induced_association": rest[-1],
                    "relative_permittivity_formulation": rest[0],
                    "born_c_shell": rest[1],
                    "born_c_dielectric": rest[2],
                    "observation_count": 0,
                    "state_count": 0,
                }
            )
            continue
        summary, parameter_rows, prediction_rows = _fit_configuration(
            configuration, source_states
        )
        summaries.append(summary)
        parameters.extend(parameter_rows)
        predictions.extend(prediction_rows)
    RESULTS.mkdir(parents=True, exist_ok=True)
    _write_csv(RESULTS / "fit_summary.csv", summaries)
    _write_csv(RESULTS / "fitted_parameters.csv", parameters)
    _write_csv(RESULTS / "fit_predictions.csv", predictions)
    engine_lock = json.loads(study.ENGINE_LOCK.read_text(encoding="utf-8"))
    module_path = Path(epcsaft.__file__).resolve()
    result = {
        "schema": "mea.born-induced-association-ion-diameter-fit.v1",
        "status": "completed",
        "active_parameters": list(ACTIVE_IDENTITIES),
        "residual": "unweighted natural-log model/observation for direct-positive Jakobsen rows",
        "aggregate_rows_excluded": True,
        "minimum_liquid_density_kg_m3": MINIMUM_LIQUID_DENSITY_KG_M3,
        "engine_wheel_sha256": engine_lock["wheel_sha256"],
        "installed_epcsaft_module_sha256": hashlib.sha256(
            module_path.read_bytes()
        ).hexdigest(),
        "runtime_seconds": time.monotonic() - started,
        "configurations": summaries,
        "claim": "two-ion-diameter sensitivity fit; no parameter promotion",
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
