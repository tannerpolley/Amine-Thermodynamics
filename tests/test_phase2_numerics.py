from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "analyses/phase2/activity_epcsaft/results"


def _rows(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_phase2_solver_grid_respects_reaction_tolerance() -> None:
    rows = _rows("phase2_solver_diagnostics.csv")
    accepted = [row for row in rows if row["solver_success"] == "True"]
    rejected = [row for row in rows if row["solver_success"] == "False"]

    assert (len(rows), len(accepted), len(rejected)) == (644, 642, 2)
    residuals = [abs(float(row["max_abs_reaction_residual"])) for row in accepted]
    assert all(math.isfinite(value) for value in residuals)
    assert max(residuals) <= 1.0e-7
    assert all("reaction_residual_exceeds_tolerance" in row["rejection_reason"] for row in rejected)


def test_phase2_reported_metrics_match_declared_tolerances() -> None:
    rows = _rows("phase2_residual_acceptance_audit.csv")
    assert rows
    for row in rows:
        threshold = float(row["threshold"])
        actual = float(row["actual_value"])
        assert math.isfinite(actual)
        within_tolerance = actual >= threshold if row["metric"] == "success_fraction" else actual <= threshold
        assert (row["passes"] == "true") is within_tolerance

    by_metric = {(row["species_or_property"], row["metric"]): row for row in rows}
    assert by_metric[("curve_grid_success_fraction", "success_fraction")]["claim_allowed"] == "false"
    for key in (
        ("MEA", "direct_positive_median_abs_log10_error"),
        ("MEAH+", "direct_positive_median_abs_log10_error"),
        ("MEACOO-", "direct_positive_median_abs_log10_error"),
        ("HCO3-", "direct_positive_median_abs_log10_error"),
        ("HCO3-", "reported_zero_max_model_mole_fraction"),
        ("MEA + MEAH+", "direct_positive_median_abs_log10_error"),
        ("CO2_pressure", "median_abs_log10_error"),
    ):
        assert by_metric[key]["claim_allowed"] == "true"
