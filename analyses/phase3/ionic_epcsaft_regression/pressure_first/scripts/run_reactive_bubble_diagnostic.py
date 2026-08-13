from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import epcsaft
from epcsaft import equilibrium

from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, parameter_mapping
from MEA.epcsaft_ionic.reactive_problem import (
    VAPOR_COMPONENT_IDS,
    build_reactive_bubble_problem,
)


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
RESULTS = ANALYSIS / "results"
PACKET = RESULTS / "pressure_candidate_packet.csv"
FIT_RESULT = RESULTS / "fixed_pressure_fugacity_screen_result.json"
OUTPUT = RESULTS / "reactive_bubble_pressure_diagnostic.json"
TABLE = RESULTS / "figures/reactive_bubble_pressure_plot_data.csv"
ENGINE_LOCK = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"

PARAMETER_IDENTITY = "pair/carbon-dioxide/water/k_ij"
CLAIM_STATUS = "diagnostic_non_promotable_exact_reactive_bubble"


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def _parameters_at(value: float) -> epcsaft.Parameters:
    mapping = cast(dict[str, Any], deepcopy(parameter_mapping()))
    matches = 0
    for pair in mapping["pairs"]:
        for coefficient in pair["coefficients"]:
            if coefficient["identity"] == PARAMETER_IDENTITY:
                coefficient["value"]["magnitude"] = value
                matches += 1
    if matches != 1:
        raise RuntimeError(f"expected one parameter coordinate {PARAMETER_IDENTITY}")
    return epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)


def _failure_row(
    row: dict[str, str], *, started: float, failure: str
) -> dict[str, object]:
    return {
        "observation_id": row["observation_id"],
        "status": "non_evaluable_diagnostic",
        "failure": failure,
        "temperature_K": float(row["temperature_K"]),
        "mea_mass_fraction": float(row["mea_mass_fraction"]),
        "loading_mol_co2_per_mol_mea": float(row["co2_loading_mol_per_mol_mea"]),
        "observed_pco2_pa": float(row["observed_pco2_pa"]),
        "observed_total_pressure_pa": float(row["state_pressure_pa"]),
        "predicted_total_pressure_pa": None,
        "predicted_pco2_pa": None,
        "residual_log10_predicted_over_observed": None,
        "pressure_parameter_derivative_pa": None,
        "pco2_parameter_derivative_pa": None,
        "bubble_closure_abs": None,
        "vapor_mole_fractions": None,
        "search": None,
        "runtime_seconds": time.monotonic() - started,
    }


def _solve_row(
    row: dict[str, str], parameters: epcsaft.Parameters
) -> dict[str, object]:
    started = time.monotonic()
    temperature = float(row["temperature_K"])
    observed_total = float(row["state_pressure_pa"])
    try:
        problem = build_reactive_bubble_problem(
            parameters,
            identity=f"pressure-diagnostic-{row['observation_id']}",
            liquid_phase_identity="mea-nine-species-liquid",
            vapor_phase_identity="mea-three-neutral-vapor",
            liquid_continuation_identity=f"liquid-{row['observation_id']}",
            bubble_continuation_identity=f"bubble-{row['observation_id']}",
            temperature_k=temperature,
            liquid_reference_pressure_pa=observed_total,
            mea_mass_fraction_unloaded=float(row["mea_mass_fraction"]),
            loading_mol_co2_per_mol_mea=float(row["co2_loading_mol_per_mol_mea"]),
            pressure_interval_pa=(
                max(100.0, 0.45 * observed_total),
                max(25_000.0, 2.2 * observed_total),
            ),
            pressure_starts_pa=(observed_total,),
            maximum_log_composition_distance=2.0,
            maximum_log_volume_distance=2.0,
        )
        active = epcsaft.ActiveParameterSet(parameters, (PARAMETER_IDENTITY,))
        rows = (
            equilibrium.ReactiveBubbleObservationRow(
                "predicted-total-pressure", "bubble_pressure_pa"
            ),
            equilibrium.ReactiveBubbleObservationRow(
                "predicted-carbon-dioxide-partial-pressure",
                "vapor_partial_pressure_pa",
                (1.0, 0.0, 0.0),
            ),
        )
        descriptor = equilibrium.reactive_bubble_observation_descriptor(
            problem, rows, active_parameters=active
        )
        result = equilibrium.evaluate_reactive_bubble_observations(
            problem,
            temperature * epcsaft.unit_registry.kelvin,
            descriptor,
            active_parameters=active,
        )
    except (
        equilibrium.ChemicalEquilibriumError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        return _failure_row(row, started=started, failure=str(error))
    if result.status != "evaluated":
        diagnostic = "reactive bubble is non-evaluable"
        if result.failure is not None:
            diagnostic = f"{result.failure.code}: {result.failure.diagnostic}"
        return _failure_row(row, started=started, failure=diagnostic)
    pressure, pco2 = result.values
    pressure_jacobian, pco2_jacobian = result.jacobian
    if (
        pressure is None
        or pco2 is None
        or pressure_jacobian is None
        or pco2_jacobian is None
        or result.certification is None
        or len(result.phases) != 2
    ):
        return _failure_row(
            row, started=started, failure="evaluated bubble result is incomplete"
        )
    return {
        "observation_id": row["observation_id"],
        "status": "evaluated_diagnostic",
        "failure": None,
        "temperature_K": temperature,
        "mea_mass_fraction": float(row["mea_mass_fraction"]),
        "loading_mol_co2_per_mol_mea": float(row["co2_loading_mol_per_mol_mea"]),
        "observed_pco2_pa": float(row["observed_pco2_pa"]),
        "observed_total_pressure_pa": observed_total,
        "predicted_total_pressure_pa": pressure,
        "predicted_pco2_pa": pco2,
        "residual_log10_predicted_over_observed": math.log10(
            pco2 / float(row["observed_pco2_pa"])
        ),
        "pressure_parameter_derivative_pa": pressure_jacobian[0],
        "pco2_parameter_derivative_pa": pco2_jacobian[0],
        "bubble_closure_abs": result.certification.bubble_log_closure_abs,
        "vapor_mole_fractions": result.phases[1].mole_fractions,
        "search": {
            "attempted": len(result.search.attempts),
            "accepted": result.search.accepted_candidate_count,
            "distinct_branches": result.search.distinct_branch_count,
            "closure_evaluations": result.search.closure_evaluation_count,
            "provider_evaluations": result.search.provider_evaluation_count,
            "attempts": [
                {
                    "start_identity": attempt.start_identity,
                    "start_pressure_pa": attempt.start_pressure_pa,
                    "status": attempt.status,
                    "iterations": attempt.iteration_count,
                    "failure_code": attempt.failure_code,
                }
                for attempt in result.search.attempts
            ],
        },
        "runtime_seconds": time.monotonic() - started,
    }


def main() -> None:
    fit = json.loads(FIT_RESULT.read_text(encoding="utf-8"))
    accepted = fit["starts"][int(fit["accepted_start"])]
    fitted_value = float(accepted["final_physical"][0])
    parameters = _parameters_at(fitted_value)
    candidates = [
        row
        for row in csv.DictReader(PACKET.open(newline="", encoding="utf-8"))
        if row["source_key"] == "Hilliard2008"
        and float(row["temperature_reported_C"]) == 40.0
        and float(row["mea_mass_fraction"]) == 0.17
    ]
    results = [_solve_row(row, parameters) for row in candidates]
    evaluated_residuals = [
        float(result["residual_log10_predicted_over_observed"])
        for result in results
        if result["status"] == "evaluated_diagnostic"
    ]
    metrics = {
        "input_rows": len(results),
        "evaluated_rows": len(evaluated_residuals),
        "failed_rows": len(results) - len(evaluated_residuals),
        "log10_bias": (
            None
            if not evaluated_residuals
            else math.fsum(evaluated_residuals) / len(evaluated_residuals)
        ),
        "log10_rmse": (
            None
            if not evaluated_residuals
            else math.sqrt(
                math.fsum(value * value for value in evaluated_residuals)
                / len(evaluated_residuals)
            )
        ),
        "log10_mae": (
            None
            if not evaluated_residuals
            else math.fsum(abs(value) for value in evaluated_residuals)
            / len(evaluated_residuals)
        ),
    }
    payload: dict[str, object] = {
        "schema_version": 1,
        "identity": "mea-exact-reactive-bubble-pressure-diagnostic-v1",
        "claim_status": CLAIM_STATUS,
        "engine": json.loads(ENGINE_LOCK.read_text(encoding="utf-8")),
        "parameter": {
            "identity": PARAMETER_IDENTITY,
            "value": fitted_value,
            "unit": "dimensionless",
            "provenance": "fixed_pressure_diagnostic_fit_non_promotable",
        },
        "topology": {
            "phase_count": 2,
            "liquid": "one_certified_reacting_nine_species_branch",
            "vapor": "one_declared_incipient_three-neutral_nonideal_branch",
            "vapor_component_ids": VAPOR_COMPONENT_IDS,
            "phase_count_search": "not_performed",
            "liquid_branch_rediscovery": "not_performed",
        },
        "method": (
            "The observed total pressure is used only to certify the local liquid "
            "continuation anchor and declare a bounded pressure start. The reported "
            "prediction is the independently closed reactive bubble root. Exact Engine "
            "implicit derivatives are retained. The fitted parameter remains diagnostic "
            "because it originated in the fixed-pressure screening lane."
        ),
        "metrics": metrics,
        "results": results,
    }
    payload["receipt_sha256"] = _canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    columns = (
        "observation_id",
        "temperature_K",
        "mea_mass_fraction",
        "loading_mol_co2_per_mol_mea",
        "observed_pco2_pa",
        "observed_total_pressure_pa",
        "predicted_pco2_pa",
        "predicted_total_pressure_pa",
        "residual_log10_predicted_over_observed",
        "status",
        "failure",
        "claim_status",
    )
    with TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    **{identity: result[identity] for identity in columns[:-1]},
                    "claim_status": CLAIM_STATUS,
                }
            )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
