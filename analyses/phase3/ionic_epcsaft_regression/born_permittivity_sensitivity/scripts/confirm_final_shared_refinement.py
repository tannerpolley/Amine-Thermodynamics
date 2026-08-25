from __future__ import annotations

import csv
from dataclasses import replace
import json
import math
import time
from types import SimpleNamespace

import epcsaft
from epcsaft import equilibrium

from fit_grepe_gate0 import _grepe_problem
from generate import ANALYSIS, COMPONENT_IDS
from run_final_shared_refinement import _pressure_rows
from MEA.epcsaft_ionic.parameter_document import materialize_parameter_candidate
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


RESULTS = ANALYSIS / "results" / "final_shared_refinement"


def _evaluate(
    row: dict[str, str],
    parameters: epcsaft.Parameters,
) -> dict[str, object]:
    started = time.monotonic()
    identity = row["observation_id"]
    temperature_k = float(row["temperature_K"])
    pressure_pa = float(row["state_pressure_pa"])
    observed = float(row["observed_pco2_pa"])
    loading = float(row["co2_loading_mol_per_mol_mea"])
    for budget in (5, 10):
        try:
            liquid = build_homogeneous_reactive_problem(
                parameters,
                identity=f"final-shared-confirm-{identity}-liquid",
                phase_identity="mea-nine-species-liquid",
                continuation_identity=f"final-shared-confirm-{identity}-liquid",
                temperature_k=temperature_k,
                pressure_pa=pressure_pa,
                mea_mass_fraction_unloaded=float(row["mea_mass_fraction"]),
                loading_mol_co2_per_mol_mea=loading,
                maximum_log_composition_distance=2.0,
                maximum_log_volume_distance=2.0,
                solver_options={
                    "maximum_iterations": 100,
                    "convergence_tolerance": 1.0e-6,
                    "primary_start_budget": budget,
                },
                allow_reaction_extrapolation=True,
            )
            break
        except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError):
            if budget == 10:
                raise
    problem = _grepe_problem(
        SimpleNamespace(problem=liquid, temperature_k=temperature_k, pressure_pa=pressure_pa)
    )
    model = epcsaft.Mixture(parameters)
    reference = equilibrium.certify_general_reactive_equilibrium_continuation_reference(
        model,
        problem,
        maximum_log_pressure_distance=2.0,
        maximum_log_composition_distance=2.0,
        maximum_log_volume_distance=2.0,
    )
    result = equilibrium.phase_equilibrium(
        model,
        replace(problem, continuation_reference=reference),
    )
    if result.status != "evaluated" or result.values[0] is None:
        raise RuntimeError(str(result.failure or "coupled bubble solve was non-evaluable"))
    predicted = float(result.values[0])
    return {
        "observation_id": identity,
        "status": "evaluated",
        "temperature_k": temperature_k,
        "loading_mol_co2_per_mol_mea": loading,
        "observed_pco2_pa": observed,
        "predicted_pco2_pa": predicted,
        "log_model_over_observed": math.log(predicted / observed),
        "solved_total_pressure_pa": reference.pressure_pa,
        "vapor_co2_mole_fraction": reference.vapor_mole_fractions[0],
        "certificate_scope": result.certificate_scope,
        "numerical_status": result.numerical_status,
        "physical_status": result.physical_status,
        "diagnostic": "",
        "runtime_seconds": time.monotonic() - started,
    }


def main() -> None:
    mapping = materialize_parameter_candidate(RESULTS / "summary.json")
    parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
    candidates = [
        row
        for row in _pressure_rows()
        if math.isclose(float(row["temperature_K"]), 313.15)
        and math.isclose(float(row["mea_mass_fraction"]), 0.30)
        and row["source_key"] == "Hilliard2008"
    ]
    rows = [candidates[index] for index in (0, len(candidates) // 2, len(candidates) - 1)]
    results = []
    for row in rows:
        try:
            evaluated = _evaluate(row, parameters)
        except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError) as error:
            evaluated = {
                "observation_id": row["observation_id"],
                "status": "non_evaluable",
                "temperature_k": float(row["temperature_K"]),
                "loading_mol_co2_per_mol_mea": float(
                    row["co2_loading_mol_per_mol_mea"]
                ),
                "observed_pco2_pa": float(row["observed_pco2_pa"]),
                "predicted_pco2_pa": None,
                "log_model_over_observed": None,
                "solved_total_pressure_pa": None,
                "vapor_co2_mole_fraction": None,
                "certificate_scope": None,
                "numerical_status": None,
                "physical_status": None,
                "diagnostic": str(error),
                "runtime_seconds": None,
            }
        results.append(evaluated)
        print(json.dumps(evaluated, sort_keys=True), flush=True)
    path = RESULTS / "coupled_bubble_confirmation.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(results[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    evaluated_rows = [row for row in results if row["status"] == "evaluated"]
    residuals = [float(row["log_model_over_observed"]) for row in evaluated_rows]
    summary = {
        "status": "completed",
        "row_count": len(results),
        "evaluated_row_count": len(evaluated_rows),
        "failed_row_count": len(results) - len(evaluated_rows),
        "log_rmse": math.sqrt(math.fsum(value * value for value in residuals) / len(residuals)),
        "typical_pressure_factor": math.exp(
            math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
        ),
        "maximum_absolute_log_residual": max(map(abs, residuals)),
        "all_numerically_passed": all(
            row["numerical_status"] == "passed" for row in evaluated_rows
        ),
        "all_physically_passed": all(
            row["physical_status"] == "passed" for row in evaluated_rows
        ),
    }
    (RESULTS / "coupled_bubble_confirmation.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
