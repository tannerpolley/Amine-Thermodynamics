from __future__ import annotations

import json
import math
from pathlib import Path

from render_predictive_partitions import _load_rows
from MEA.common.analysis_io import read_diagnostic_rows, write_csv_rows as _write


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results"
OUTPUT = RESULTS / "candidate_speciation_comparison"
CANDIDATES = {
    "retained": (None, 0.0, 0.0),
    "full_r4_r5": (
        RESULTS / "anchored_joint_reaction_temperature_validation/compile_diagnostics.csv",
        0.053848175222989375,
        0.9642695898871344,
    ),
    "calorimetry_balanced": (
        RESULTS / "calorimetry_balanced_reaction_validation/compile_diagnostics.csv",
        0.029877891836457147,
        0.5350291330862538,
    ),
}


def _metrics(rows: list[dict[str, object]]) -> tuple[float, float]:
    residuals = [
        math.log(float(row["predicted"]) / float(row["observed"])) for row in rows
    ]
    rmse = math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
    return rmse, math.exp(rmse)


def main() -> None:
    retained = [
        row
        for row in _load_rows()
        if row["block"] == "speciation" and row["partition"] in {"training", "reserved"}
    ]
    retained_by_identity = {str(row["identity"]): row for row in retained}
    predictions = []
    for candidate, (path, r4, r5) in CANDIDATES.items():
        predicted = {
            identity: float(row["predicted"])
            for identity, row in retained_by_identity.items()
        }
        if path is not None:
            for state in read_diagnostic_rows(path, nested=True):
                for target in state.get("targets", []):
                    predicted[str(target["identity"])] = float(target["predicted"])
        if set(predicted) != set(retained_by_identity):
            raise RuntimeError(f"{candidate} does not preserve the frozen target set")
        for identity, source in retained_by_identity.items():
            predictions.append(
                {
                    "candidate": candidate,
                    "candidate_r4_delta_ln_k_at_353_15_k": r4,
                    "candidate_r5_delta_ln_k_at_353_15_k": r5,
                    **{key: value for key, value in source.items() if key != "predicted"},
                    "predicted": predicted[identity],
                }
            )

    metric_rows = []
    for candidate in CANDIDATES:
        candidate_rows = [row for row in predictions if row["candidate"] == candidate]
        for partition in ("training", "reserved"):
            partition_rows = [row for row in candidate_rows if row["partition"] == partition]
            for target in ("all", *sorted({str(row["target"]) for row in partition_rows})):
                selected = (
                    partition_rows
                    if target == "all"
                    else [row for row in partition_rows if row["target"] == target]
                )
                if selected:
                    rmse, factor = _metrics(selected)
                    metric_rows.append(
                        {
                            "candidate": candidate,
                            "partition": partition,
                            "target": target,
                            "target_count": len(selected),
                            "log_rmse": rmse,
                            "rms_factor": factor,
                        }
                    )
    summary = {
        "schema": "mea.candidate-speciation-comparison.v1",
        "status": "completed",
        "candidate_count": len(CANDIDATES),
        "target_count_per_candidate": len(retained),
        "candidate_reaction_temperature_corrections": {
            key: {"r4_delta_ln_k_at_353_15_k": value[1], "r5_delta_ln_k_at_353_15_k": value[2]}
            for key, value in CANDIDATES.items()
        },
        "failed_or_omitted_targets": 0,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _write(OUTPUT / "predictions.csv", predictions)
    _write(OUTPUT / "metrics.csv", metric_rows)
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
