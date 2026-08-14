from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import epcsaft
import numpy as np
from epcsaft import equilibrium

from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, parameter_mapping
from MEA.epcsaft_ionic.reactive_problem import build_reactive_bubble_problem


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
PACKET = ANALYSIS / "results/pressure_candidate_packet.csv"
ENGINE_LOCK = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def _parameters(config: dict[str, Any]) -> epcsaft.Parameters:
    polar = cast(str, config.get("polar_formulation", "none"))
    mapping = cast(dict[str, Any], deepcopy(parameter_mapping(polar=polar)))
    fixed_overrides = cast(
        dict[str, dict[str, dict[str, object]]],
        config.get("fixed_component_overrides", {}),
    )
    coefficient_record_overrides = cast(
        dict[str, dict[str, object]],
        config.get("coefficient_record_overrides", {}),
    )
    mapping["sources"].extend(deepcopy(config.get("additional_sources", [])))
    mapping["domains"].extend(deepcopy(config.get("additional_domains", [])))
    for component in mapping["components"]:
        component_id = cast(str, component["component_id"])
        if component_id in fixed_overrides:
            component["fixed"].update(deepcopy(fixed_overrides[component_id]))
        for coefficient in component["coefficients"]:
            identity = cast(str, coefficient["identity"])
            if identity in coefficient_record_overrides:
                coefficient.update(deepcopy(coefficient_record_overrides[identity]))
    origins = {
        item["identity"]: float(item["origin"])
        for item in config["coordinate_screen"]
    }
    found: set[str] = set()
    for component in mapping["components"]:
        for coefficient in component["coefficients"]:
            identity = coefficient["identity"]
            if identity in origins:
                coefficient["value"]["magnitude"] = origins[identity]
                found.add(identity)
    for pair in mapping["pairs"]:
        for coefficient in pair["coefficients"]:
            identity = coefficient["identity"]
            if identity in origins:
                coefficient["value"]["magnitude"] = origins[identity]
                found.add(identity)
    if found != set(origins):
        raise RuntimeError(f"unresolved parameter coordinates: {sorted(set(origins) - found)}")
    return epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)


def _solve(
    row: dict[str, str],
    parameters: epcsaft.Parameters,
    active: epcsaft.ActiveParameterSet,
) -> dict[str, object]:
    started = time.monotonic()
    temperature = float(row["temperature_K"])
    observed_total = float(row["state_pressure_pa"])
    try:
        problem = build_reactive_bubble_problem(
            parameters,
            identity=f"pressure-direction-screen-{row['observation_id']}",
            liquid_phase_identity="mea-nine-species-liquid",
            vapor_phase_identity="mea-three-neutral-vapor",
            liquid_continuation_identity=f"liquid-screen-{row['observation_id']}",
            bubble_continuation_identity=f"bubble-screen-{row['observation_id']}",
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
        descriptor = equilibrium.reactive_bubble_observation_descriptor(
            problem,
            (
                equilibrium.ReactiveBubbleObservationRow(
                    "predicted-carbon-dioxide-partial-pressure",
                    "vapor_partial_pressure_pa",
                    (1.0, 0.0, 0.0),
                ),
            ),
            active_parameters=active,
        )
        result = equilibrium.evaluate_reactive_bubble_observations(
            problem,
            temperature * epcsaft.unit_registry.kelvin,
            descriptor,
            active_parameters=active,
        )
    except (equilibrium.ChemicalEquilibriumError, RuntimeError, TypeError, ValueError) as error:
        return {
            "observation_id": row["observation_id"],
            "status": "failed",
            "failure_code": "exception_before_typed_result",
            "diagnostic": str(error),
            "runtime_seconds": time.monotonic() - started,
        }
    if result.status != "evaluated":
        code = None if result.failure is None else result.failure.code
        detail = None if result.failure is None else result.failure.diagnostic
        return {
            "observation_id": row["observation_id"],
            "status": "non_evaluable",
            "failure_code": code,
            "diagnostic": detail,
            "runtime_seconds": time.monotonic() - started,
        }
    predicted = result.values[0]
    jacobian = result.jacobian[0]
    if predicted is None or jacobian is None or result.certification is None:
        raise RuntimeError("evaluated pressure direction row is incomplete")
    observed = float(row["observed_pco2_pa"])
    pressure_scale = math.sqrt(
        0.02**2 + (640.0 / observed_total) ** 2
    ) / math.log(10.0)
    return {
        "observation_id": row["observation_id"],
        "status": "evaluated",
        "failure_code": None,
        "diagnostic": None,
        "loading_mol_co2_per_mol_mea": float(row["co2_loading_mol_per_mol_mea"]),
        "observed_total_pressure_pa": observed_total,
        "observed_pco2_pa": observed,
        "predicted_pco2_pa": predicted,
        "residual_log10": math.log10(predicted / observed),
        "source_scale_log10": pressure_scale,
        "pco2_parameter_jacobian_pa": list(jacobian),
        "residual_parameter_jacobian": [
            value / (predicted * math.log(10.0)) for value in jacobian
        ],
        "bubble_closure_abs": result.certification.bubble_log_closure_abs,
        "attempted_starts": len(result.search.attempts),
        "accepted_starts": result.search.accepted_candidate_count,
        "distinct_branches": result.search.distinct_branch_count,
        "runtime_seconds": time.monotonic() - started,
    }


def _block_diagnostic(
    results: list[dict[str, object]],
    coordinate_ids: list[str],
    all_coordinate_ids: list[str],
    coordinate_scales: dict[str, float],
    coordinate_origins: dict[str, float],
    coordinate_bounds: dict[str, tuple[float, float]],
) -> dict[str, object]:
    indices = [all_coordinate_ids.index(identity) for identity in coordinate_ids]
    residual = np.asarray([row["residual_log10"] for row in results], dtype=float)
    weights = np.asarray([row["source_scale_log10"] for row in results], dtype=float)
    loading = np.asarray(
        [row["loading_mol_co2_per_mol_mea"] for row in results], dtype=float
    )
    jacobian = np.asarray(
        [row["residual_parameter_jacobian"] for row in results], dtype=float
    )[:, indices]
    scales = np.asarray([coordinate_scales[identity] for identity in coordinate_ids])
    weighted_scaled_jacobian = jacobian * scales[np.newaxis, :] / weights[:, None]
    weighted_residual = residual / weights
    singular_values = np.linalg.svd(weighted_scaled_jacobian, compute_uv=False)
    rank = int(np.linalg.matrix_rank(weighted_scaled_jacobian))
    condition = (
        math.inf
        if not len(singular_values) or singular_values[-1] == 0.0
        else float(singular_values[0] / singular_values[-1])
    )
    affine_step, *_ = np.linalg.lstsq(
        weighted_scaled_jacobian, -weighted_residual, rcond=None
    )
    physical_step = affine_step * scales
    candidate = np.asarray(
        [coordinate_origins[identity] for identity in coordinate_ids]
    ) + physical_step
    predicted_residual = residual + jacobian @ physical_step
    initial_slope = float(np.polyfit(loading, residual, 1)[0])
    candidate_slope = float(np.polyfit(loading, predicted_residual, 1)[0])
    initial_quadratic = float(np.polyfit(loading, residual, 2)[0])
    candidate_quadratic = float(np.polyfit(loading, predicted_residual, 2)[0])
    bounds_ok = all(
        coordinate_bounds[identity][0] < value < coordinate_bounds[identity][1]
        for identity, value in zip(coordinate_ids, candidate, strict=True)
    )
    return {
        "coordinate_identities": coordinate_ids,
        "rank": rank,
        "singular_values": singular_values.tolist(),
        "condition_number": condition,
        "linearized_affine_step": affine_step.tolist(),
        "linearized_physical_step": physical_step.tolist(),
        "linearized_candidate": candidate.tolist(),
        "linearized_candidate_inside_bounds": bounds_ok,
        "initial_weighted_sum_squares": float(weighted_residual @ weighted_residual),
        "linearized_weighted_sum_squares": float(
            np.sum((predicted_residual / weights) ** 2)
        ),
        "initial_log10_rmse": float(np.sqrt(np.mean(residual**2))),
        "linearized_log10_rmse": float(np.sqrt(np.mean(predicted_residual**2))),
        "initial_loading_slope_log10_per_loading": initial_slope,
        "linearized_loading_slope_log10_per_loading": candidate_slope,
        "absolute_loading_slope_improved": abs(candidate_slope) < abs(initial_slope),
        "initial_loading_quadratic_log10_per_loading_squared": initial_quadratic,
        "linearized_loading_quadratic_log10_per_loading_squared": (
            candidate_quadratic
        ),
        "absolute_loading_quadratic_improved": (
            abs(candidate_quadratic) < abs(initial_quadratic)
        ),
        "initial_residual_range_log10": float(np.ptp(residual)),
        "linearized_residual_range_log10": float(np.ptp(predicted_residual)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ANALYSIS / "config/pressure_block_ladder.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ANALYSIS / "results/pressure_parameter_direction_screen.json",
    )
    parser.add_argument(
        "--table",
        type=Path,
        default=ANALYSIS / "results/pressure_parameter_direction_screen.csv",
    )
    args = parser.parse_args()
    config_path = args.config.resolve()
    output_path = args.output.resolve()
    table_path = args.table.resolve()
    config = cast(
        dict[str, Any], json.loads(config_path.read_text(encoding="utf-8"))
    )
    parameters = _parameters(config)
    coordinate_ids = [item["identity"] for item in config["coordinate_screen"]]
    active = epcsaft.ActiveParameterSet(parameters, tuple(coordinate_ids))
    packet = {
        row["observation_id"]: row
        for row in csv.DictReader(PACKET.open(newline="", encoding="utf-8"))
    }
    rows = [packet[identity] for identity in config["training_screen"]["row_ids"]]
    results: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        result = _solve(row, parameters, active)
        results.append(result)
        print(
            f"[{index}/{len(rows)}] {row['observation_id']} "
            f"{result['status']} {result['runtime_seconds']:.2f} s",
            flush=True,
        )
    evaluated = [row for row in results if row["status"] == "evaluated"]
    coordinate_scales = {
        item["identity"]: float(item["scale"])
        for item in config["coordinate_screen"]
    }
    coordinate_origins = {
        item["identity"]: float(item["origin"])
        for item in config["coordinate_screen"]
    }
    coordinate_bounds = {
        item["identity"]: (float(item["bounds"][0]), float(item["bounds"][1]))
        for item in config["coordinate_screen"]
    }
    blocks: list[list[str]] = [list(block) for block in config["nested_blocks"]]
    baseline = coordinate_ids[0]
    blocks.extend([[baseline, identity] for identity in coordinate_ids[2:]])
    diagnostics = (
        []
        if len(evaluated) != len(rows)
        else [
            _block_diagnostic(
                evaluated,
                block,
                coordinate_ids,
                coordinate_scales,
                coordinate_origins,
                coordinate_bounds,
            )
            for block in blocks
        ]
    )
    payload: dict[str, object] = {
        "schema_version": 1,
        "identity": f"{config['identity']}-result",
        "claim_status": "exact_jacobian_screen_not_a_parameter_fit",
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "engine": json.loads(ENGINE_LOCK.read_text(encoding="utf-8")),
        "active_parameter_fingerprint": active.fingerprint,
        "coordinate_identities": coordinate_ids,
        "accounting": {
            "input_rows": len(rows),
            "evaluated_rows": len(evaluated),
            "non_evaluable_rows": len(rows) - len(evaluated),
        },
        "block_diagnostics": diagnostics,
        "results": results,
    }
    payload["receipt_sha256"] = _canonical_sha256(payload)
    output_path.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    columns = (
        "observation_id",
        "status",
        "loading_mol_co2_per_mol_mea",
        "observed_total_pressure_pa",
        "observed_pco2_pa",
        "predicted_pco2_pa",
        "residual_log10",
        "source_scale_log10",
        "bubble_closure_abs",
        "runtime_seconds",
        "failure_code",
    )
    with table_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in results:
            writer.writerow({identity: row.get(identity) for identity in columns})
    print(output_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
