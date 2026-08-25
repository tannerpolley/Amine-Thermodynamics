from __future__ import annotations

import csv
from concurrent.futures import ProcessPoolExecutor
import json
import math

import numpy as np

from generate import ANALYSIS
from run_final_shared_refinement import _pressure_rows
from run_full_predictive_refinement import _compile_pressure, _speciation_states
from screen_reaction_temperature_corrections import STEP, _evaluate, _temperature_scale
from MEA.common.analysis_io import read_diagnostic_rows
from MEA.epcsaft_ionic.parameter_document import materialize_parameter_candidate


RESULTS = ANALYSIS / "results/joint_reaction_temperature_screen"
PARAMETERS = ANALYSIS / "results/predictive_training_refinement/summary.json"
SPEC_SCREEN = ANALYSIS / "results/reaction_temperature_sensitivity/perturbation_rows.csv"
PRESSURE_BASE = ANALYSIS / "results/predictive_temperature_challenge/compile_diagnostics.csv"


def _pressure(payload: tuple[dict[str, object], dict[str, object], str, float, float]) -> tuple[str, dict[str, object]]:
    mapping, source, case, r4, r5 = payload
    row = dict(source)
    scale = _temperature_scale(float(row["temperature_K"]))
    row["reaction_ln_k_adjustments"] = {"R4": r4 * scale, "R5": r5 * scale}
    _, diagnostic = _compile_pressure((mapping, row))
    diagnostic["case"] = case
    return case, diagnostic


def _residual(row: dict[str, object]) -> float:
    return math.log(float(row["predicted"]) / float(row["observed"]))


def _metrics(rows: list[dict[str, object]]) -> dict[str, float | int]:
    values = [_residual(row) for row in rows]
    rmse = math.sqrt(math.fsum(value * value for value in values) / len(values))
    return {"target_count": len(rows), "log_rmse": rmse, "rms_factor": math.exp(rmse)}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    mapping = materialize_parameter_candidate(PARAMETERS)
    source_rows = [
        row for row in _pressure_rows()
        if row["analysis_role"] == "non_scoring_domain_challenge"
    ]
    selected = []
    for temperature in (333.15, 353.15):
        rows = sorted(
            (row for row in source_rows if float(row["temperature_K"]) == temperature),
            key=lambda row: float(row["co2_loading_mol_per_mol_mea"]),
        )
        selected.extend(rows[index] for index in (0, len(rows) // 2, -1))
    base_pressure = {
        row["identity"]: row
        for row in read_diagnostic_rows(PRESSURE_BASE, nested=True)
        if row["identity"] in {source["observation_id"] for source in selected}
    }
    perturb_payloads = [
        (mapping, row, case, r4, r5)
        for case, r4, r5 in (("r4_plus", STEP, 0.0), ("r5_plus", 0.0, STEP))
        for row in selected
    ]
    perturbed: dict[str, list[dict[str, object]]] = {"r4_plus": [], "r5_plus": []}
    with ProcessPoolExecutor(max_workers=2) as pool:
        for case, diagnostic in pool.map(_pressure, perturb_payloads):
            perturbed[case].append(diagnostic)
    if any(row["status"] != "evaluated" for rows in perturbed.values() for row in rows):
        raise RuntimeError("joint reaction pressure perturbation was non-evaluable")
    pressure_by_case = {
        case: {row["identity"]: row for row in rows} for case, rows in perturbed.items()
    }

    spec: dict[str, dict[str, dict[str, object]]] = {}
    with SPEC_SCREEN.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["case"] not in {"baseline", "r4_minus", "r4_plus", "r5_minus", "r5_plus"}:
                continue
            spec.setdefault(row["case"], {})[row["identity"]] = {
                "identity": row["identity"],
                "observed": float(row["observed"]),
                "predicted": float(row["predicted"]),
            }
    spec_ids = sorted(spec["baseline"])
    pressure_ids = sorted(base_pressure)
    spec_residual = np.array([_residual(spec["baseline"][identity]) for identity in spec_ids])
    pressure_residual = np.array([_residual(base_pressure[identity]) for identity in pressure_ids])
    spec_jacobian = np.column_stack([
        np.array([
            _residual(spec[plus][identity]) - _residual(spec[minus][identity])
            for identity in spec_ids
        ]) / (2.0 * STEP)
        for minus, plus in (("r4_minus", "r4_plus"), ("r5_minus", "r5_plus"))
    ])
    pressure_jacobian = np.column_stack([
        np.array([
            _residual(pressure_by_case[case][identity]) - _residual(base_pressure[identity])
            for identity in pressure_ids
        ]) / STEP
        for case in ("r4_plus", "r5_plus")
    ])
    jacobian = np.vstack((spec_jacobian / math.sqrt(len(spec_ids)), pressure_jacobian / math.sqrt(len(pressure_ids))))
    residual = np.concatenate((spec_residual / math.sqrt(len(spec_ids)), pressure_residual / math.sqrt(len(pressure_ids))))
    correction, *_ = np.linalg.lstsq(jacobian, -residual, rcond=None)
    correction = np.clip(correction, -2.0, 2.0)

    high_states = [
        state for state in _speciation_states("active_training")
        if float(state["temperature_k"]) in {333.15, 353.15}
    ]
    with ProcessPoolExecutor(max_workers=2) as pool:
        spec_candidate = [
            diagnostic for _, diagnostic in pool.map(
                _evaluate,
                ((mapping, state, "joint_candidate", float(correction[0]), float(correction[1])) for state in high_states),
            )
        ]
        pressure_candidate = [
            diagnostic for _, diagnostic in pool.map(
                _pressure,
                ((mapping, row, "joint_candidate", float(correction[0]), float(correction[1])) for row in selected),
            )
        ]
    if any(row["status"] != "evaluated" for row in [*spec_candidate, *pressure_candidate]):
        raise RuntimeError("joint reaction candidate was non-evaluable")
    spec_candidate_rows = [target for state in spec_candidate for target in state["targets"]]
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    summary = {
        "schema": "mea.joint-reaction-temperature-screen.v1",
        "status": "completed",
        "pressure_sample_ids": pressure_ids,
        "candidate_r4_delta_ln_k_at_353_15_k": float(correction[0]),
        "candidate_r5_delta_ln_k_at_353_15_k": float(correction[1]),
        "baseline_high_temperature_speciation": _metrics(list(spec["baseline"].values())),
        "candidate_high_temperature_speciation": _metrics(spec_candidate_rows),
        "baseline_pressure_sample": _metrics(list(base_pressure.values())),
        "candidate_pressure_sample": _metrics(pressure_candidate),
        "jacobian_singular_values": singular_values.tolist(),
        "jacobian_condition_number": float(singular_values[0] / singular_values[-1]),
        "evaluated_state_count": len(perturb_payloads) + len(spec_candidate) + len(pressure_candidate),
        "failed_or_omitted_states": 0,
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
