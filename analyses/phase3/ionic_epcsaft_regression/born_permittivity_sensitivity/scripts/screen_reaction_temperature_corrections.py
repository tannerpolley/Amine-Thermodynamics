from __future__ import annotations

import csv
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from importlib.metadata import distribution
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from generate import ANALYSIS
from run_full_predictive_refinement import _compile_speciation, _speciation_states
from MEA.epcsaft_ionic.parameter_document import materialize_parameter_candidate


RESULTS = ANALYSIS / "results" / "reaction_temperature_sensitivity"
PARAMETERS = ANALYSIS / "results/predictive_training_refinement/summary.json"
REFERENCE_TEMPERATURE_K = 313.15
HIGH_TEMPERATURE_K = 353.15
STEP = 0.25
CASES = {
    "baseline": (0.0, 0.0),
    "r4_minus": (-STEP, 0.0),
    "r4_plus": (STEP, 0.0),
    "r5_minus": (0.0, -STEP),
    "r5_plus": (0.0, STEP),
}


def _temperature_scale(temperature_k: float) -> float:
    return ((1.0 / temperature_k) - (1.0 / REFERENCE_TEMPERATURE_K)) / (
        (1.0 / HIGH_TEMPERATURE_K) - (1.0 / REFERENCE_TEMPERATURE_K)
    )


def _evaluate(payload: tuple[dict[str, object], dict[str, object], str, float, float]) -> tuple[str, dict[str, object]]:
    mapping, source_state, case, r4_at_high, r5_at_high = payload
    state = deepcopy(source_state)
    scale = _temperature_scale(float(state["temperature_k"]))
    state["reaction_ln_k_adjustments"] = {
        "R4": r4_at_high * scale,
        "R5": r5_at_high * scale,
    }
    _, diagnostic = _compile_speciation((mapping, state))
    diagnostic["case"] = case
    diagnostic["r4_delta_ln_k_at_353_15_k"] = r4_at_high
    diagnostic["r5_delta_ln_k_at_353_15_k"] = r5_at_high
    return case, diagnostic


def _rows(diagnostics: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {
        str(target["identity"]): target
        for diagnostic in diagnostics
        for target in diagnostic["targets"]
    }


def _metrics(rows: dict[str, dict[str, object]]) -> dict[str, float | int]:
    residuals = [
        math.log(float(row["predicted"]) / float(row["observed"]))
        for row in rows.values()
    ]
    rmse = math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
    return {
        "target_count": len(residuals),
        "log_rmse": rmse,
        "rms_factor": math.exp(rmse),
        "mean_log_bias": math.fsum(residuals) / len(residuals),
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    mapping = materialize_parameter_candidate(PARAMETERS)
    states = [
        state for state in _speciation_states("active_training")
        if float(state["temperature_k"]) in {333.15, 353.15}
    ]
    if len(states) != 10:
        raise RuntimeError(f"expected 10 high-temperature training states, found {len(states)}")
    payloads = [
        (mapping, state, case, r4, r5)
        for case, (r4, r5) in CASES.items()
        for state in states
    ]
    grouped: dict[str, list[dict[str, object]]] = {case: [] for case in CASES}
    with ProcessPoolExecutor(max_workers=2) as pool:
        for case, diagnostic in pool.map(_evaluate, payloads):
            grouped[case].append(diagnostic)
    failures = [
        diagnostic for diagnostics in grouped.values() for diagnostic in diagnostics
        if diagnostic["status"] != "evaluated"
    ]
    if failures:
        (RESULTS / "failures.json").write_text(json.dumps(failures, indent=2) + "\n")
        raise RuntimeError(f"{len(failures)} reaction-sensitivity states failed")

    case_rows = {case: _rows(diagnostics) for case, diagnostics in grouped.items()}
    identities = sorted(case_rows["baseline"])
    if any(sorted(rows) != identities for rows in case_rows.values()):
        raise RuntimeError("reaction-sensitivity cases do not contain identical targets")
    residual = np.array([
        math.log(float(case_rows["baseline"][identity]["predicted"]) /
                 float(case_rows["baseline"][identity]["observed"]))
        for identity in identities
    ])
    jacobian = np.column_stack(
        [
            np.array([
                math.log(float(case_rows[plus][identity]["predicted"]) /
                         float(case_rows[plus][identity]["observed"]))
                - math.log(float(case_rows[minus][identity]["predicted"]) /
                           float(case_rows[minus][identity]["observed"]))
                for identity in identities
            ]) / (2.0 * STEP)
            for minus, plus in (("r4_minus", "r4_plus"), ("r5_minus", "r5_plus"))
        ]
    )
    correction, *_ = np.linalg.lstsq(jacobian, -residual, rcond=None)
    correction = np.clip(correction, -2.0, 2.0)

    candidate_payloads = [
        (mapping, state, "linear_candidate", float(correction[0]), float(correction[1]))
        for state in states
    ]
    with ProcessPoolExecutor(max_workers=2) as pool:
        candidate = [diagnostic for _, diagnostic in pool.map(_evaluate, candidate_payloads)]
    if any(row["status"] != "evaluated" for row in candidate):
        raise RuntimeError("linearized reaction-correction candidate was non-evaluable")
    candidate_rows = _rows(candidate)

    with (RESULTS / "perturbation_rows.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = (
            "case", "identity", "temperature_k", "loading", "observed", "predicted",
            "r4_delta_ln_k_at_353_15_k", "r5_delta_ln_k_at_353_15_k",
        )
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for case, diagnostics in (*grouped.items(), ("linear_candidate", candidate)):
            for diagnostic in diagnostics:
                for target in diagnostic["targets"]:
                    writer.writerow({
                        "case": case,
                        "identity": target["identity"],
                        "temperature_k": diagnostic["temperature_k"],
                        "loading": diagnostic["loading"],
                        "observed": target["observed"],
                        "predicted": target["predicted"],
                        "r4_delta_ln_k_at_353_15_k": diagnostic["r4_delta_ln_k_at_353_15_k"],
                        "r5_delta_ln_k_at_353_15_k": diagnostic["r5_delta_ln_k_at_353_15_k"],
                    })
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    wheel = Path(json.loads(distribution("epcsaft").read_text("direct_url.json"))["url"].removeprefix("file://"))
    summary = {
        "schema": "mea.reaction-temperature-sensitivity.v1",
        "status": "completed",
        "training_state_count": len(states),
        "training_target_count": len(identities),
        "reference_temperature_k": REFERENCE_TEMPERATURE_K,
        "correction_coordinate": "delta ln(K) at 353.15 K, zero at 313.15 K, linear in reciprocal temperature",
        "finite_difference_step": STEP,
        "baseline_metrics": _metrics(case_rows["baseline"]),
        "candidate_metrics": _metrics(candidate_rows),
        "candidate_r4_delta_ln_k_at_353_15_k": float(correction[0]),
        "candidate_r5_delta_ln_k_at_353_15_k": float(correction[1]),
        "jacobian_singular_values": singular_values.tolist(),
        "jacobian_condition_number": float(singular_values[0] / singular_values[-1]),
        "failed_or_omitted_states": 0,
        "engine_wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
