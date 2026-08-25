from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import epcsaft
from epcsaft import equilibrium

from MEA.epcsaft_ionic.parameter_document import load_parameters
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem

from fit_grepe_gate0 import _grepe_problem


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
PACKET = ANALYSIS / "results/pressure_candidate_packet.csv"
OUTPUT = ANALYSIS / "results/grepe_gate0"
FIT_SUMMARY = OUTPUT / "summary.json"
TABLE = OUTPUT / "grepe_hilliard_curve.csv"
SUMMARY = OUTPUT / "grepe_hilliard_curve_summary.json"
ACTIVE_IDENTITIES = (
    "component/protonated-monoethanolamine/segment_diameter",
    "component/carbamate-anion/segment_diameter",
)


def _selected_rows() -> list[dict[str, str]]:
    with PACKET.open(newline="", encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["source_key"] == "Hilliard2008"
            and math.isclose(float(row["temperature_K"]), 313.15)
            and math.isclose(float(row["mea_mass_fraction"]), 0.30)
        ]
    return sorted(rows, key=lambda row: float(row["co2_loading_mol_per_mol_mea"]))


def _candidate_values() -> tuple[float, ...]:
    payload = json.loads(FIT_SUMMARY.read_text(encoding="utf-8"))
    values = {
        identity: float(value) for identity, value, _unit in payload["fitted_values"]
    }
    if set(values) != set(ACTIVE_IDENTITIES):
        raise RuntimeError("fit result does not contain the expected two-coordinate candidate")
    return tuple(values[identity] for identity in ACTIVE_IDENTITIES)


def _evaluate(
    row: dict[str, str],
    parameters: epcsaft.Parameters,
    candidate_values: tuple[float, ...],
) -> dict[str, object]:
    started = time.monotonic()
    observation_id = row["observation_id"]
    temperature_k = float(row["temperature_K"])
    observed_total_pressure_pa = float(row["state_pressure_pa"])
    observed_pco2_pa = float(row["observed_pco2_pa"])
    loading = float(row["co2_loading_mol_per_mol_mea"])
    base_active = epcsaft.ActiveParameterSet(parameters, ACTIVE_IDENTITIES)
    candidate_active = epcsaft.ActiveParameterSet(
        parameters, ACTIVE_IDENTITIES, values=candidate_values
    )
    stage = "liquid_continuation_certification"
    start_budget_used = 2
    try:
        try:
            liquid = _liquid_problem(
                row, parameters, observation_id=observation_id, start_budget=2
            )
        except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError):
            start_budget_used = 5
            liquid = _liquid_problem(
                row, parameters, observation_id=observation_id, start_budget=5
            )
        source = SimpleNamespace(
            problem=liquid,
            temperature_k=temperature_k,
            pressure_pa=observed_total_pressure_pa,
        )
        problem = _grepe_problem(source)
        model = epcsaft.Mixture(parameters)
        stage = "general_coupled_continuation_certification"
        reference = equilibrium.certify_general_reactive_equilibrium_continuation_reference(
            model,
            problem,
            active_parameters=base_active,
            maximum_log_pressure_distance=2.0,
            maximum_log_composition_distance=2.0,
            maximum_log_volume_distance=2.0,
        )
        baseline_pco2_pa = reference.pressure_pa * reference.vapor_mole_fractions[0]
        stage = "candidate_phase_equilibrium"
        result = equilibrium.phase_equilibrium(
            model,
            replace(problem, continuation_reference=reference),
            active_parameters=candidate_active,
        )
    except (RuntimeError, TypeError, ValueError, equilibrium.ChemicalEquilibriumError) as error:
        return {
            "observation_id": observation_id,
            "status": "failed",
            "failure_stage": stage,
            "liquid_start_budget_used": start_budget_used,
            "diagnostic": str(error),
            "loading_mol_co2_per_mol_mea": loading,
            "observed_total_pressure_pa": observed_total_pressure_pa,
            "observed_pco2_pa": observed_pco2_pa,
            "baseline_pco2_pa": None,
            "candidate_pco2_pa": None,
            "baseline_log10_ratio": None,
            "candidate_log10_ratio": None,
            "runtime_seconds": time.monotonic() - started,
        }
    if result.status != "evaluated" or result.values[0] is None:
        diagnostic = "candidate result is non-evaluable"
        if result.failure is not None:
            diagnostic = f"{result.failure.code}: {result.failure.diagnostic}"
        return {
            "observation_id": observation_id,
            "status": "non_evaluable",
            "failure_stage": "candidate_phase_equilibrium",
            "liquid_start_budget_used": start_budget_used,
            "diagnostic": diagnostic,
            "loading_mol_co2_per_mol_mea": loading,
            "observed_total_pressure_pa": observed_total_pressure_pa,
            "observed_pco2_pa": observed_pco2_pa,
            "baseline_pco2_pa": baseline_pco2_pa,
            "candidate_pco2_pa": None,
            "baseline_log10_ratio": math.log10(baseline_pco2_pa / observed_pco2_pa),
            "candidate_log10_ratio": None,
            "runtime_seconds": time.monotonic() - started,
        }
    candidate_pco2_pa = float(result.values[0])
    return {
        "observation_id": observation_id,
        "status": "evaluated",
        "failure_stage": "",
        "liquid_start_budget_used": start_budget_used,
        "diagnostic": "",
        "loading_mol_co2_per_mol_mea": loading,
        "observed_total_pressure_pa": observed_total_pressure_pa,
        "observed_pco2_pa": observed_pco2_pa,
        "baseline_pco2_pa": baseline_pco2_pa,
        "candidate_pco2_pa": candidate_pco2_pa,
        "baseline_log10_ratio": math.log10(baseline_pco2_pa / observed_pco2_pa),
        "candidate_log10_ratio": math.log10(candidate_pco2_pa / observed_pco2_pa),
        "candidate_solver_status": result.solver_status,
        "candidate_numerical_status": result.numerical_status,
        "candidate_physical_status": result.physical_status,
        "candidate_provider_domain_status": result.provider_domain_status,
        "candidate_certificate_scope": result.certificate_scope,
        "runtime_seconds": time.monotonic() - started,
    }


def _liquid_problem(
    row: dict[str, str],
    parameters: epcsaft.Parameters,
    *,
    observation_id: str,
    start_budget: int,
) -> object:
    return build_homogeneous_reactive_problem(
        parameters,
        identity=f"hilliard-grepe-curve-{observation_id}-liquid",
        phase_identity="mea-nine-species-liquid",
        continuation_identity=f"hilliard-grepe-curve-{observation_id}-liquid-branch",
        temperature_k=float(row["temperature_K"]),
        pressure_pa=float(row["state_pressure_pa"]),
        mea_mass_fraction_unloaded=float(row["mea_mass_fraction"]),
        loading_mol_co2_per_mol_mea=float(row["co2_loading_mol_per_mol_mea"]),
        maximum_log_composition_distance=2.0,
        maximum_log_volume_distance=2.0,
        solver_options={
            "maximum_iterations": 100,
            "convergence_tolerance": 1.0e-6,
            "primary_start_budget": start_budget,
        },
    )


def _rmse(rows: list[dict[str, object]], field: str) -> float | None:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    if not values:
        return None
    return math.sqrt(math.fsum(value * value for value in values) / len(values))


def _mean(rows: list[dict[str, object]], field: str) -> float | None:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    return None if not values else math.fsum(values) / len(values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--retry-failures",
        action="store_true",
        help="reuse evaluated rows and recompute only failed or non-evaluable rows",
    )
    args = parser.parse_args()
    started = time.monotonic()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_rows = _selected_rows()
    parameters = load_parameters()
    candidate_values = _candidate_values()
    previous: dict[str, dict[str, object]] = {}
    if args.retry_failures and TABLE.exists():
        with TABLE.open(newline="", encoding="utf-8") as handle:
            previous = {
                row["observation_id"]: dict(row) for row in csv.DictReader(handle)
            }
        for row in previous.values():
            if row["status"] == "evaluated" and not row.get("liquid_start_budget_used"):
                row["liquid_start_budget_used"] = 2
    pending = [
        row
        for row in source_rows
        if row["observation_id"] not in previous
        or previous[row["observation_id"]]["status"] != "evaluated"
    ]
    replacements: dict[str, dict[str, object]] = {}
    for index, row in enumerate(pending, start=1):
        result = _evaluate(row, parameters, candidate_values)
        replacements[row["observation_id"]] = result
        print(
            json.dumps(
                {
                    "completed": index,
                    "total": len(pending),
                    "observation_id": result["observation_id"],
                    "status": result["status"],
                    "runtime_seconds": result["runtime_seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    results = [
        (
            replacements[row["observation_id"]]
            if row["observation_id"] in replacements
            else previous[row["observation_id"]]
        )
        for row in source_rows
    ]
    fieldnames = tuple(dict.fromkeys(key for row in results for key in row))
    with TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    evaluated = [row for row in results if row["status"] == "evaluated"]
    baseline_rmse = _rmse(results, "baseline_log10_ratio")
    candidate_rmse = _rmse(results, "candidate_log10_ratio")
    summary = {
        "status": "completed",
        "source": "Hilliard2008",
        "temperature_k": 313.15,
        "mea_mass_fraction_unloaded": 0.30,
        "input_row_count": len(source_rows),
        "evaluated_candidate_row_count": len(evaluated),
        "failed_candidate_row_count": len(source_rows) - len(evaluated),
        "candidate_parameter_identities": list(ACTIVE_IDENTITIES),
        "candidate_parameter_values_angstrom": list(candidate_values),
        "baseline_log10_rmse": baseline_rmse,
        "candidate_log10_rmse": candidate_rmse,
        "baseline_typical_pressure_factor": (
            None if baseline_rmse is None else 10.0**baseline_rmse
        ),
        "candidate_typical_pressure_factor": (
            None if candidate_rmse is None else 10.0**candidate_rmse
        ),
        "candidate_mean_log10_bias": _mean(results, "candidate_log10_ratio"),
        "last_command_runtime_seconds": time.monotonic() - started,
        "total_row_runtime_seconds": math.fsum(
            float(row["runtime_seconds"]) for row in results
        ),
        "claim": "diagnostic one-iteration candidate; not a promoted parameter set",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
