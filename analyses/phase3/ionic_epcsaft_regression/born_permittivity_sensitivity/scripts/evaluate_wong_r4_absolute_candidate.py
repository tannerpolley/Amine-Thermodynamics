from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json

from evaluate_anchored_co2_water_kij import _mapping as _anchored_mapping
from evaluate_anchored_co2_water_kij import (
    ANCHOR_TEMPERATURE_K,
    K_SLOPE_PER_K,
    PAIR_IDENTITY,
)
from evaluate_wong_free_co2_challenge import (
    BALANCED,
    PARAMETERS,
    SOURCE,
    _metrics,
    _plot,
    _solve,
    _write_csv,
)
from generate import ANALYSIS
from validate_reaction_temperature_candidate import _adjustments
from MEA.epcsaft_ionic.parameter_document import (
    expand_parameter_domain,
    materialize_parameter_candidate,
    set_parameter_values,
)


BASE_RESULTS = ANALYSIS / "results/wong_free_co2_external_challenge"


def render_completed_candidates() -> None:
    with (BASE_RESULTS / "predictions.csv").open(newline="", encoding="utf-8") as stream:
        combined_rows: list[dict[str, object]] = list(csv.DictReader(stream))
    combined_summary = deepcopy(
        json.loads((BASE_RESULTS / "summary.json").read_text(encoding="utf-8"))
    )
    for directory in sorted(ANALYSIS.glob("results/wong_*_candidate")):
        predictions = directory / "predictions.csv"
        candidate_summary = directory / "summary.json"
        if not predictions.is_file() or not candidate_summary.is_file():
            continue
        with predictions.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        if not rows:
            continue
        combined_rows.extend(rows)
        combined_summary["candidate_metrics"][str(rows[0]["candidate"])] = json.loads(
            candidate_summary.read_text(encoding="utf-8")
        )["metrics"]
    _plot(combined_rows, combined_summary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-id", default="r4_absolute_candidate")
    parser.add_argument("--results-label", default="wong_r4_absolute_candidate")
    parser.add_argument("--r4-offset", type=float, default=-1.85)
    parser.add_argument("--co2-water-offset", type=float, default=0.0)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    results = ANALYSIS / "results" / args.results_label
    if not 1 <= args.workers <= 2:
        parser.error("--workers must be 1 or 2")

    with SOURCE.open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    mapping = materialize_parameter_candidate(PARAMETERS)
    mapping = expand_parameter_domain(
        mapping,
        temperatures_k=tuple(float(row["temperature_K"]) for row in source_rows),
        pressures_pa=tuple(float(row["pressure_Pa"]) for row in source_rows),
    )
    balanced = json.loads(BALANCED.read_text(encoding="utf-8"))
    r4 = float(balanced["candidate_r4_delta_ln_k_at_353_15_k"])
    r5 = float(balanced["candidate_r5_delta_ln_k_at_353_15_k"])
    payloads = []
    for row in source_rows:
        temperature = float(row["temperature_K"])
        adjustments = _adjustments(temperature, r4, r5)
        adjustments["R4"] += args.r4_offset
        state_mapping = _anchored_mapping(mapping, temperature)
        set_parameter_values(
            state_mapping,
            {
                PAIR_IDENTITY: args.co2_water_offset
                + K_SLOPE_PER_K * (temperature - ANCHOR_TEMPERATURE_K)
            },
        )
        payloads.append(
            (
                args.candidate_id,
                state_mapping,
                row,
                adjustments,
            )
        )

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(_solve, payloads))
    failures = [row for row in rows if row["status"] != "evaluated"]
    evaluated = [row for row in rows if row["status"] == "evaluated"]
    results.mkdir(parents=True, exist_ok=True)
    _write_csv(results / "predictions.csv", evaluated)
    if failures:
        _write_csv(results / "failures.csv", failures)
    else:
        (results / "failures.csv").unlink(missing_ok=True)

    metrics = {
        "free_co2": _metrics(
            evaluated,
            "predicted_free_co2_concentration_mol_L",
            "free_co2_concentration_mol_L",
        ),
        "henry_constant": _metrics(
            evaluated,
            "predicted_henry_constant_kPa_L_per_mol",
            "henry_constant_kPa_L_per_mol",
        ),
    }
    summary = {
        "schema": "mea.wong-r4-absolute-candidate.v1",
        "status": "completed" if not failures else "completed_with_failures",
        "r4_absolute_delta_ln_k": args.r4_offset,
        "co2_water_k_ij_offset": args.co2_water_offset,
        "temperature_corrections": {
            "delta_ln_k_r4_at_353_15_k": r4,
            "delta_ln_k_r5_at_353_15_k": r5,
        },
        "source_row_count": len(source_rows),
        "evaluated_state_count": len(evaluated),
        "failed_state_count": len(failures),
        "metrics": metrics,
        "scientific_status": "direct-free-co2-diagnostic; NaClO4 omitted from model",
    }
    (results / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    render_completed_candidates()
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
