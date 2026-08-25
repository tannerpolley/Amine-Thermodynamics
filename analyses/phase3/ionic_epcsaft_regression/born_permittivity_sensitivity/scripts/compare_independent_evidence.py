from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from MEA.common.analysis_io import write_csv_rows as _write_csv


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results"
OUTPUT = RESULTS / "independent_evidence_comparison"


def _retained_metrics() -> dict[tuple[str, str], dict[str, str]]:
    with (RESULTS / "retained_predictive_candidate_metrics.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        return {
            (row["partition"], row["block"]): row for row in csv.DictReader(stream)
        }


def main() -> None:
    retained = _retained_metrics()
    balanced = json.loads(
        (RESULTS / "calorimetry_balanced_reaction_validation/summary.json").read_text(
            encoding="utf-8"
        )
    )
    calorimetry = json.loads(
        (RESULTS / "calorimetry_consistency/summary.json").read_text(
            encoding="utf-8"
        )
    )
    heat = {row["configuration"]: row for row in calorimetry["metrics"]}
    domains = [
        {
            "domain": "pressure_challenge",
            "quantity": "natural-log pressure RMSE",
            "target_count": 27,
            "retained_error": float(
                retained[("temperature challenge", "pressure")]["log_rmse"]
            ),
            "balanced_error": float(
                balanced["temperature_challenge_pressure_metrics"]["log_rmse"]
            ),
            "unit": "dimensionless",
        },
        {
            "domain": "reserved_speciation",
            "quantity": "natural-log mole-fraction RMSE",
            "target_count": 67,
            "retained_error": float(retained[("reserved", "speciation")]["log_rmse"]),
            "balanced_error": float(balanced["reserved_speciation_metrics"]["log_rmse"]),
            "unit": "dimensionless",
        },
        {
            "domain": "calorimetry",
            "quantity": "heat-release RMSE",
            "target_count": calorimetry["evaluated_observation_count_per_configuration"],
            "retained_error": float(heat["retained"]["rmse_kj_per_mol_co2"]),
            "balanced_error": float(
                heat["calorimetry_balanced_exact"]["rmse_kj_per_mol_co2"]
            ),
            "unit": "kJ/mol CO2",
        },
    ]
    for row in domains:
        row["balanced_to_retained_error_ratio"] = (
            row["balanced_error"] / row["retained_error"]
        )
    ratios = {row["domain"]: row["balanced_to_retained_error_ratio"] for row in domains}
    if not (
        ratios["pressure_challenge"] < 1.0
        and ratios["reserved_speciation"] > 1.0
        and ratios["calorimetry"] < 1.0
    ):
        raise RuntimeError("completed evidence no longer has the expected tradeoff")

    profiles = [
        ("equal_domains", 1 / 3, 1 / 3, 1 / 3),
        ("pressure_focused", 0.50, 0.25, 0.25),
        ("speciation_focused", 0.25, 0.50, 0.25),
        ("calorimetry_focused", 0.25, 0.25, 0.50),
    ]
    profile_rows = []
    for name, pressure_weight, speciation_weight, calorimetry_weight in profiles:
        score = math.exp(
            pressure_weight * math.log(ratios["pressure_challenge"])
            + speciation_weight * math.log(ratios["reserved_speciation"])
            + calorimetry_weight * math.log(ratios["calorimetry"])
        )
        profile_rows.append(
            {
                "profile": name,
                "pressure_weight": pressure_weight,
                "reserved_speciation_weight": speciation_weight,
                "calorimetry_weight": calorimetry_weight,
                "balanced_to_retained_geometric_score": score,
                "preferred_configuration": "calorimetry_balanced" if score < 1 else "retained",
            }
        )

    grid = []
    for pressure_percent in range(101):
        for speciation_percent in range(101 - pressure_percent):
            calorimetry_percent = 100 - pressure_percent - speciation_percent
            weights = (
                pressure_percent / 100,
                speciation_percent / 100,
                calorimetry_percent / 100,
            )
            score = math.exp(
                weights[0] * math.log(ratios["pressure_challenge"])
                + weights[1] * math.log(ratios["reserved_speciation"])
                + weights[2] * math.log(ratios["calorimetry"])
            )
            grid.append(
                {
                    "pressure_weight": weights[0],
                    "reserved_speciation_weight": weights[1],
                    "calorimetry_weight": weights[2],
                    "balanced_to_retained_geometric_score": score,
                    "preferred_configuration": "calorimetry_balanced" if score < 1 else "retained",
                }
            )

    threshold = []
    for pressure_share_percent in range(101):
        pressure_share = pressure_share_percent / 100
        non_speciation_log_ratio = (
            pressure_share * math.log(ratios["pressure_challenge"])
            + (1 - pressure_share) * math.log(ratios["calorimetry"])
        )
        speciation_weight = -non_speciation_log_ratio / (
            math.log(ratios["reserved_speciation"]) - non_speciation_log_ratio
        )
        threshold.append(
            {
                "pressure_share_of_non_speciation_weight": pressure_share,
                "maximum_speciation_weight_preferring_balanced": speciation_weight,
            }
        )

    candidate_grid_count = sum(
        row["preferred_configuration"] == "calorimetry_balanced" for row in grid
    )
    summary = {
        "schema": "mea.independent-evidence-comparison.v1",
        "status": "completed",
        "method": "geometric mean of domain error ratios relative to the retained parameter set",
        "domains": domains,
        "equal_domain_balanced_to_retained_score": profile_rows[0][
            "balanced_to_retained_geometric_score"
        ],
        "candidate_preferred_grid_fraction": candidate_grid_count / len(grid),
        "weight_grid_step": 0.01,
        "weight_grid_count": len(grid),
        "interpretation_limit": "domain weights are engineering priorities, not measurement-uncertainty weights",
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT / "domain_metrics.csv", domains)
    _write_csv(OUTPUT / "priority_profiles.csv", profile_rows)
    _write_csv(OUTPUT / "preference_threshold.csv", threshold)
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
