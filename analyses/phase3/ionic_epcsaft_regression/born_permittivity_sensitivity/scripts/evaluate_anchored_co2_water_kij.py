from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json
import math
import os

from evaluate_co2_water_kij_transfer import PARAMETERS, _write_csv
from run_full_predictive_refinement import (
    _evaluate_pressure_reference,
    _evaluate_speciation_reference,
    _metrics,
    _pressure_rows,
    _speciation_states,
)
from MEA.epcsaft_ionic.parameter_document import (
    materialize_parameter_candidate,
    set_parameter_values,
)


OUTPUT = PARAMETERS.parents[1] / "co2_water_kij_anchored_transfer"
BASELINE = PARAMETERS.parents[2] / "figures/predictive_partition_plot_data.csv"
PAIR_IDENTITY = "pair/carbon-dioxide/water/k_ij"
ANCHOR_TEMPERATURE_K = 313.15
K_SLOPE_PER_K = 3.016e-4


def _mapping(mapping: dict[str, object], temperature_k: float) -> dict[str, object]:
    state_mapping = deepcopy(mapping)
    set_parameter_values(
        state_mapping,
        {PAIR_IDENTITY: K_SLOPE_PER_K * (temperature_k - ANCHOR_TEMPERATURE_K)},
    )
    return state_mapping


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=os.process_cpu_count() or 1)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    mapping = materialize_parameter_candidate(PARAMETERS)
    pressure_rows = [
        dict(
            row,
            pressure_interval_pa=(10.0, 3_000_000.0),
            pressure_starts_pa=(float(row["state_pressure_pa"]),),
            maximum_log_pressure_distance=2.0,
        )
        for row in _pressure_rows()
        if row["analysis_role"] == "non_scoring_domain_challenge"
    ]
    speciation = {
        "training": [
            state
            for state in _speciation_states("active_training")
            if not math.isclose(float(state["temperature_k"]), ANCHOR_TEMPERATURE_K)
        ],
        "reserved": [
            state
            for state in _speciation_states("reserved_validation")
            if not math.isclose(float(state["temperature_k"]), ANCHOR_TEMPERATURE_K)
        ],
    }
    pressure_payloads = [
        (_mapping(mapping, float(row["temperature_K"])), row) for row in pressure_rows
    ]
    speciation_payloads = [
        (_mapping(mapping, float(state["temperature_k"])), state)
        for states in speciation.values()
        for state in states
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pressure_results = list(
            pool.map(_evaluate_pressure_reference, pressure_payloads)
        )
        speciation_results = list(
            pool.map(_evaluate_speciation_reference, speciation_payloads)
        )
    diagnostics = [*pressure_results, *speciation_results]
    failures = [row for row in diagnostics if row["status"] != "evaluated"]
    if failures:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "failures.json").write_text(
            json.dumps(failures, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        raise RuntimeError(f"{len(failures)} changed states were not evaluated")

    with BASELINE.open(newline="", encoding="utf-8") as stream:
        baseline = [
            row
            for row in csv.DictReader(stream)
            if math.isclose(float(row["temperature_k"]), ANCHOR_TEMPERATURE_K)
        ]
    predictions: list[dict[str, object]] = [
        {
            "partition": row["partition"].replace(
                "temperature challenge", "temperature_challenge"
            ),
            "block": row["block"],
            "state_identity": row["identity"],
            "target_identity": row["target"],
            "temperature_k": float(row["temperature_k"]),
            "loading": float(row["loading_mol_co2_per_mol_mea"]),
            "observed": float(row["observed"]),
            "predicted": float(row["predicted"]),
            "unit": row["unit"],
            "k_co2_water": 0.0,
        }
        for row in baseline
    ]
    for row in pressure_results:
        temperature_k = float(row["temperature_k"])
        predictions.append(
            {
                "partition": "temperature_challenge",
                "block": "pressure",
                "state_identity": row["identity"],
                "target_identity": row["identity"],
                "temperature_k": temperature_k,
                "loading": row["loading"],
                "observed": row["observed"],
                "predicted": row["predicted"],
                "unit": "pascal",
                "k_co2_water": K_SLOPE_PER_K * (temperature_k - ANCHOR_TEMPERATURE_K),
            }
        )
    partition_by_state = {
        str(state["identity"]): partition
        for partition, states in speciation.items()
        for state in states
    }
    for state in speciation_results:
        temperature_k = float(state["temperature_k"])
        for target in state["targets"]:
            predictions.append(
                {
                    "partition": partition_by_state[str(state["identity"])],
                    "block": "speciation",
                    "state_identity": state["identity"],
                    "target_identity": target["identity"],
                    "temperature_k": temperature_k,
                    "loading": state["loading"],
                    "observed": target["observed"],
                    "predicted": target["predicted"],
                    "unit": "dimensionless",
                    "k_co2_water": K_SLOPE_PER_K
                    * (temperature_k - ANCHOR_TEMPERATURE_K),
                }
            )

    metric_rows = []
    for partition in ("training", "reserved", "temperature_challenge"):
        for block in ("pressure", "speciation"):
            rows = [
                row
                for row in predictions
                if row["partition"] == partition and row["block"] == block
            ]
            if rows:
                metric_rows.append(
                    {"partition": partition, "block": block, "target_count": len(rows)}
                    | _metrics(rows)
                )
    summary = {
        "schema": "mea.co2-water-kij-anchored-transfer.v1",
        "status": "completed",
        "form": "k_CO2,H2O(T) = 3.016e-4 K^-1 * (T - 313.15 K)",
        "slope_source": "Pabsch et al. (2020), Table 6, DOI 10.1021/acs.jced.0c00704",
        "anchor_basis": "zero interaction retained at the 313.15 K MEA calibration temperature",
        "state_count": 119,
        "recomputed_state_count": len(diagnostics),
        "target_count": len(predictions),
        "failure_count": 0,
        "metrics": metric_rows,
    }
    if len(predictions) != 257:
        raise RuntimeError(f"expected 257 targets, found {len(predictions)}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT / "predictions.csv", predictions)
    _write_csv(OUTPUT / "metrics.csv", metric_rows)
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
