from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json
import math
import os
from pathlib import Path

from generate import ANALYSIS
from run_final_shared_refinement import _pressure_rows
from evaluate_anchored_co2_water_kij import (
    ANCHOR_TEMPERATURE_K,
    K_SLOPE_PER_K,
    PAIR_IDENTITY,
    _mapping as _anchored_mapping,
)
from run_full_predictive_refinement import (
    _evaluate_pressure_reference,
    _evaluate_speciation_reference,
    _speciation_states,
)
from MEA.common.analysis_io import read_diagnostic_rows, write_diagnostic_rows
from MEA.epcsaft_ionic.parameter_document import (
    expand_parameter_domain,
    materialize_parameter_candidate,
    set_parameter_values,
)


BASE = ANALYSIS / "results"
PARAMETERS = BASE / "predictive_training_refinement/summary.json"
DEFAULT_SCREEN = BASE / "reaction_temperature_sensitivity/summary.json"
REFERENCE_TEMPERATURE_K = 313.15
HIGH_TEMPERATURE_K = 353.15


def _scale(temperature_k: float) -> float:
    return ((1.0 / temperature_k) - (1.0 / REFERENCE_TEMPERATURE_K)) / (
        (1.0 / HIGH_TEMPERATURE_K) - (1.0 / REFERENCE_TEMPERATURE_K)
    )


def _adjustments(temperature_k: float, r4: float, r5: float) -> dict[str, float]:
    scale = _scale(temperature_k)
    return {"R4": r4 * scale, "R5": r5 * scale}


def _log_metrics(rows: list[dict[str, object]]) -> dict[str, float | int]:
    residuals = [
        math.log(float(row["predicted"]) / float(row["observed"])) for row in rows
    ]
    rmse = math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
    return {
        "target_count": len(rows),
        "log_rmse": rmse,
        "rms_factor": math.exp(rmse),
        "mean_log_bias": math.fsum(residuals) / len(residuals),
    }


def _pressure_metrics_by_partition(
    results: list[dict[str, object]], sources: list[dict[str, object]]
) -> dict[str, dict[str, float | int]]:
    partition = {str(row["observation_id"]): str(row["analysis_role"]) for row in sources}
    roles = {partition[str(row["identity"])] for row in results}
    return {
        role: _log_metrics(
            [row for row in results if partition[str(row["identity"])] == role]
        )
        for role in sorted(roles)
    }


def _fit_rows() -> list[dict[str, object]]:
    with (BASE / "predictive_training_refinement/fit_rows.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        return [
            {
                "identity": row["identity"],
                "observed": float(row["observed"]),
                "predicted": float(row["predicted"]),
            }
            for row in csv.DictReader(stream)
            if row["unit"] == "dimensionless"
        ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-summary", type=Path, default=DEFAULT_SCREEN)
    parser.add_argument("--results-label", default="reaction_temperature_validation")
    parser.add_argument("--anchored-co2-water", action="store_true")
    parser.add_argument("--r4-offset", type=float, default=0.0)
    parser.add_argument("--co2-water-offset", type=float, default=0.0)
    parser.add_argument(
        "--speciation-scope", choices=("none", "all"), default="all"
    )
    parser.add_argument(
        "--pressure-scope", choices=("none", "challenge", "all"), default="challenge"
    )
    parser.add_argument("--pressure-bounds-pa", type=float, nargs=2)
    parser.add_argument("--pressure-starts-pa", type=float, nargs="+")
    parser.add_argument("--maximum-log-pressure-distance", type=float, default=2.0)
    parser.add_argument("--resume-diagnostics", type=Path)
    parser.add_argument("--postprocess-diagnostics", action="store_true")
    parser.add_argument("--workers", type=int, default=os.process_cpu_count() or 1)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    pressure_interval_pa = (
        None if args.pressure_bounds_pa is None else tuple(args.pressure_bounds_pa)
    )
    if args.pressure_scope != "none" and pressure_interval_pa is None:
        parser.error("--pressure-bounds-pa is required when pressure rows are selected")
    if pressure_interval_pa is not None and not (
        0.0 < pressure_interval_pa[0] < pressure_interval_pa[1]
    ):
        parser.error("--pressure-bounds-pa must be positive and increasing")
    if args.maximum_log_pressure_distance <= 0.0:
        parser.error("--maximum-log-pressure-distance must be positive")
    if args.postprocess_diagnostics and args.resume_diagnostics is None:
        parser.error("--postprocess-diagnostics requires --resume-diagnostics")
    pressure_starts_pa = tuple(args.pressure_starts_pa or ())
    if pressure_interval_pa is not None and any(
        not pressure_interval_pa[0] <= value <= pressure_interval_pa[1]
        for value in pressure_starts_pa
    ):
        parser.error("--pressure-starts-pa must lie inside --pressure-bounds-pa")
    results = BASE / args.results_label
    results.mkdir(parents=True, exist_ok=True)
    mapping = materialize_parameter_candidate(PARAMETERS)
    if pressure_interval_pa is not None:
        mapping = expand_parameter_domain(mapping, pressures_pa=pressure_interval_pa)
    screen = json.loads(args.candidate_summary.read_text(encoding="utf-8"))
    r4 = float(screen["candidate_r4_delta_ln_k_at_353_15_k"])
    r5 = float(screen["candidate_r5_delta_ln_k_at_353_15_k"])

    speciation_states = []
    for role in (() if args.speciation_scope == "none" else ("active_training", "reserved_validation")):
        for source in _speciation_states(role):
            if (
                args.r4_offset == 0.0
                and args.co2_water_offset == 0.0
                and float(source["temperature_k"]) == REFERENCE_TEMPERATURE_K
            ):
                continue
            state = deepcopy(source)
            state["partition"] = role
            adjustments = _adjustments(
                float(source["temperature_k"]), r4, r5
            )
            adjustments["R4"] += args.r4_offset
            state["reaction_ln_k_adjustments"] = adjustments
            speciation_states.append(state)
    pressure_rows = []
    for source in _pressure_rows():
        if args.pressure_scope == "none" or (
            args.pressure_scope == "challenge"
            and source["analysis_role"] != "non_scoring_domain_challenge"
        ):
            continue
        row: dict[str, object] = dict(source)
        assert pressure_interval_pa is not None
        row["pressure_interval_pa"] = pressure_interval_pa
        row["pressure_starts_pa"] = (
            float(row["state_pressure_pa"]),
            *pressure_starts_pa,
        )
        row["maximum_log_pressure_distance"] = args.maximum_log_pressure_distance
        adjustments = _adjustments(
            float(source["temperature_K"]), r4, r5
        )
        adjustments["R4"] += args.r4_offset
        row["reaction_ln_k_adjustments"] = adjustments
        pressure_rows.append(row)

    prior_diagnostics: list[dict[str, object]] = []
    if args.resume_diagnostics is not None:
        prior = read_diagnostic_rows(args.resume_diagnostics, nested=True)
        if args.postprocess_diagnostics:
            prior_diagnostics = prior
            pressure_rows = []
        else:
            retry = {
                str(row["identity"]) for row in prior if row["status"] != "evaluated"
            }
            prior_diagnostics = [row for row in prior if row["status"] == "evaluated"]
            pressure_rows = [
                row for row in pressure_rows if str(row["observation_id"]) in retry
            ]

    def state_mapping(temperature_k: float) -> dict[str, object]:
        state = (
            _anchored_mapping(mapping, temperature_k)
            if args.anchored_co2_water
            else deepcopy(mapping)
        )
        if args.co2_water_offset != 0.0:
            set_parameter_values(
                state,
                {
                    PAIR_IDENTITY: args.co2_water_offset
                    + (
                        K_SLOPE_PER_K
                        * (temperature_k - ANCHOR_TEMPERATURE_K)
                        if args.anchored_co2_water
                        else 0.0
                    )
                },
            )
        return state

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        speciation = list(
            pool.map(
                _evaluate_speciation_reference,
                (
                    (state_mapping(float(state["temperature_k"])), state)
                    for state in speciation_states
                ),
            )
        )
        pressure = list(
            pool.map(
                _evaluate_pressure_reference,
                (
                    (state_mapping(float(row["temperature_K"])), row)
                    for row in pressure_rows
                ),
            )
        )
    diagnostics = [*prior_diagnostics, *speciation, *pressure]
    write_diagnostic_rows(results / "compile_diagnostics.csv", diagnostics)
    failures = [row for row in diagnostics if row["status"] != "evaluated"]

    candidate_training = {row["identity"]: row for row in _fit_rows()}
    candidate_reserved = {
        str(target["identity"]): target
        for state in read_diagnostic_rows(
            BASE / "predictive_reserved_validation/compile_diagnostics.csv",
            nested=True,
        )
        if state["block"] == "speciation"
        for target in state["targets"]
    }
    training_ids = {
        state["identity"]
        for state in speciation_states
        if state["partition"] == "active_training"
    }
    reserved_ids = {
        state["identity"]
        for state in speciation_states
        if state["partition"] == "reserved_validation"
    }
    for state in speciation:
        target = (
            candidate_training
            if state["identity"] in training_ids
            else candidate_reserved
        )
        if state["identity"] not in training_ids | reserved_ids:
            raise RuntimeError("candidate validation state has no frozen partition")
        for row in state["targets"]:
            target[str(row["identity"])] = row

    pressure_results = [row for row in diagnostics if "observed" in row]
    summary = {
        "schema": "mea.reaction-temperature-validation.v1",
        "status": "completed" if not failures else "completed_with_failures",
        "candidate_r4_delta_ln_k_at_353_15_k": r4,
        "candidate_r5_delta_ln_k_at_353_15_k": r5,
        "r4_absolute_delta_ln_k": args.r4_offset,
        "co2_water_k_ij_offset": args.co2_water_offset,
        "anchored_co2_water_interaction": args.anchored_co2_water,
        "pressure_scope": args.pressure_scope,
        "speciation_scope": args.speciation_scope,
        "training_speciation_metrics": (
            _log_metrics(list(candidate_training.values()))
            if args.speciation_scope == "all"
            else None
        ),
        "reserved_speciation_metrics": (
            _log_metrics(list(candidate_reserved.values()))
            if args.speciation_scope == "all"
            else None
        ),
        "temperature_challenge_pressure_metrics": (
            _log_metrics(pressure) if args.pressure_scope == "challenge" else None
        ),
        "selected_pressure_metrics": (
            _log_metrics(pressure_results)
            if args.pressure_scope != "none"
            else None
        ),
        "pressure_metrics_by_partition": (
            _pressure_metrics_by_partition(
                pressure_results, _pressure_rows()
            )
            if args.pressure_scope != "none"
            else None
        ),
        "evaluated_state_count": len(diagnostics),
        "failed_or_omitted_states": len(failures),
    }
    (results / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)
    if failures:
        raise RuntimeError(f"{len(failures)} candidate validation states failed")


if __name__ == "__main__":
    main()
