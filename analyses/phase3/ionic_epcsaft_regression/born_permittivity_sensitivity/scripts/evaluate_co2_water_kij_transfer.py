from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from importlib.metadata import distribution
import hashlib
import json
import os
from pathlib import Path

import epcsaft

from generate import ANALYSIS, COMPONENT_IDS
from MEA.common.analysis_io import write_csv_rows as _write_csv
from run_full_predictive_refinement import (
    ACTIVE,
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


RESULTS = ANALYSIS / "results/co2_water_kij_transfer"
PARAMETERS = ANALYSIS / "results/predictive_training_refinement/summary.json"
T_REFERENCE_K = 298.15
K_REFERENCE = 0.0122
K_SLOPE_PER_K = 3.016e-4
PAIR_IDENTITY = "pair/carbon-dioxide/water/k_ij"


def _mapping_at_temperature(
    mapping: dict[str, object], temperature_k: float
) -> dict[str, object]:
    state_mapping = deepcopy(mapping)
    set_parameter_values(
        state_mapping,
        {PAIR_IDENTITY: K_REFERENCE + K_SLOPE_PER_K * (temperature_k - T_REFERENCE_K)},
    )
    return state_mapping


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-label", default="co2_water_kij_transfer")
    parser.add_argument("--meah-sigma", type=float)
    parser.add_argument("--meacoo-sigma", type=float)
    parser.add_argument("--workers", type=int, default=os.process_cpu_count() or 1)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    results_directory = ANALYSIS / "results" / args.results_label
    mapping = materialize_parameter_candidate(PARAMETERS)
    if (args.meah_sigma is None) != (args.meacoo_sigma is None):
        raise ValueError("both ion diameters must be supplied together")
    if args.meah_sigma is not None:
        set_parameter_values(
            mapping,
            {
                "component/protonated-monoethanolamine/segment_diameter": args.meah_sigma,
                "component/carbamate-anion/segment_diameter": args.meacoo_sigma,
            },
        )
    pressure_rows = [
        dict(
            row,
            pressure_interval_pa=(10.0, 3_000_000.0),
            pressure_starts_pa=(float(row["state_pressure_pa"]),),
            maximum_log_pressure_distance=2.0,
        )
        for row in _pressure_rows()
    ]
    pressure_partitions = {
        "training": [
            row for row in pressure_rows if row["analysis_role"] == "training"
        ],
        "reserved": [
            row for row in pressure_rows if row["analysis_role"] == "reserved"
        ],
        "temperature_challenge": [
            row
            for row in pressure_rows
            if row["analysis_role"] == "non_scoring_domain_challenge"
        ],
    }
    speciation_partitions = {
        "training": _speciation_states("active_training"),
        "reserved": _speciation_states("reserved_validation"),
    }

    pressure_payloads = [
        (_mapping_at_temperature(mapping, float(row["temperature_K"])), row)
        for rows in pressure_partitions.values()
        for row in rows
    ]
    speciation_payloads = [
        (_mapping_at_temperature(mapping, float(state["temperature_k"])), state)
        for states in speciation_partitions.values()
        for state in states
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pressure_results = list(
            pool.map(_evaluate_pressure_reference, pressure_payloads)
        )
        speciation_results = list(
            pool.map(_evaluate_speciation_reference, speciation_payloads)
        )

    pressure_partition_by_id = {
        str(row["observation_id"]): partition
        for partition, rows in pressure_partitions.items()
        for row in rows
    }
    speciation_partition_by_id = {
        str(state["identity"]): partition
        for partition, states in speciation_partitions.items()
        for state in states
    }
    diagnostics = [*pressure_results, *speciation_results]
    failures = [row for row in diagnostics if row["status"] != "evaluated"]
    if failures:
        results_directory.mkdir(parents=True, exist_ok=True)
        (results_directory / "failures.json").write_text(
            json.dumps(failures, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        raise RuntimeError(f"{len(failures)} source states were not evaluated")

    predictions: list[dict[str, object]] = []
    for row in pressure_results:
        temperature_k = float(row["temperature_k"])
        predictions.append(
            {
                "partition": pressure_partition_by_id[str(row["identity"])],
                "block": "pressure",
                "state_identity": row["identity"],
                "target_identity": row["identity"],
                "temperature_k": temperature_k,
                "loading": row["loading"],
                "observed": row["observed"],
                "predicted": row["predicted"],
                "unit": "pascal",
                "k_co2_water": K_REFERENCE
                + K_SLOPE_PER_K * (temperature_k - T_REFERENCE_K),
            }
        )
    for state in speciation_results:
        temperature_k = float(state["temperature_k"])
        for target in state["targets"]:
            predictions.append(
                {
                    "partition": speciation_partition_by_id[str(state["identity"])],
                    "block": "speciation",
                    "state_identity": state["identity"],
                    "target_identity": target["identity"],
                    "temperature_k": temperature_k,
                    "loading": state["loading"],
                    "observed": target["observed"],
                    "predicted": target["predicted"],
                    "unit": "dimensionless",
                    "k_co2_water": K_REFERENCE
                    + K_SLOPE_PER_K * (temperature_k - T_REFERENCE_K),
                }
            )

    metric_rows: list[dict[str, object]] = []
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

    parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
    active_values = dict(
        zip(ACTIVE, epcsaft.ActiveParameterSet(parameters, ACTIVE).values)
    )
    wheel_path = Path(
        json.loads(distribution("epcsaft").read_text("direct_url.json"))[
            "url"
        ].removeprefix("file://")
    )
    summary = {
        "schema": "mea.co2-water-kij-transfer.v1",
        "status": "completed",
        "source": "Pabsch et al. (2020), Tables 2 and 6, DOI 10.1021/acs.jced.0c00704",
        "binary_qualification": "Kiepe et al. (2002), Table 1, DOI 10.1021/ie020154i",
        "k_ij": {
            "form": "k_ref + slope * (T - 298.15 K)",
            "reference": K_REFERENCE,
            "slope_per_k": K_SLOPE_PER_K,
        },
        "fixed_fitted_values": active_values,
        "state_count": len(diagnostics),
        "target_count": len(predictions),
        "failure_count": 0,
        "metrics": metric_rows,
        "engine_wheel_path": str(wheel_path),
        "engine_wheel_sha256": hashlib.sha256(wheel_path.read_bytes()).hexdigest(),
    }
    results_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(results_directory / "predictions.csv", predictions)
    _write_csv(results_directory / "metrics.csv", metric_rows)
    _write_csv(
        results_directory / "parameter_table.csv",
        [
            {"identity": identity, "value": value, "unit": "dimensionless"}
            for identity, value in active_values.items()
        ]
        + [
            {
                "identity": "pair/carbon-dioxide/water/k_ij@298.15K",
                "value": K_REFERENCE,
                "unit": "dimensionless",
            },
            {
                "identity": "pair/carbon-dioxide/water/k_ij/slope",
                "value": K_SLOPE_PER_K,
                "unit": "1/K",
            },
        ],
    )
    (results_directory / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
