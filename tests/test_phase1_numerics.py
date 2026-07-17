from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from MEA.smith_missen.ideal_speciation import solve_ideal_speciation


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "analyses/phase1/smith_missen_baseline/results"


def _rows(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_ideal_solver_converges_across_manuscript_domain() -> None:
    for temperature_K in (293.15, 313.15):
        for loading in (0.05, 0.40, 0.75):
            result = solve_ideal_speciation(loading, 0.30, temperature_K)
            assert result.success, (temperature_K, loading, result.message)
            assert result.max_abs_residual < 1.0e-8, (temperature_K, loading)
            assert np.all(np.isfinite(result.mole_fractions))
            assert np.all(result.mole_fractions > 0.0)
            assert abs(float(np.sum(result.mole_fractions)) - 1.0) < 1.0e-12


def test_phase1_reported_metrics_obey_declared_tolerances() -> None:
    rows = _rows("phase1_residual_acceptance_audit.csv")
    overall = [row for row in rows if row["temperature_C"] == "overall"]

    pressure = [row for row in overall if row["target_family"] == "pressure"]
    for model in {row["source_or_model"] for row in pressure}:
        metrics = {row["metric"]: float(row["actual_value"]) for row in pressure if row["source_or_model"] == model}
        assert all(math.isfinite(value) for value in metrics.values())
        assert metrics["AAD_percent"] <= 50.0 or metrics["median_abs_log10_error"] <= 0.25

    major_species = {"MEA", "MEAH+", "MEACOO-", "HCO3-", "MEA + MEAH+"}
    speciation = [
        row
        for row in overall
        if row["target_family"] == "speciation" and row["species_or_property"] in major_species
    ]
    assert {row["species_or_property"] for row in speciation} == major_species
    for row in speciation:
        value = float(row["actual_value"])
        assert math.isfinite(value)
        if row["metric"] == "median_abs_log10_error":
            assert value <= 0.50
        elif row["metric"] == "mae_log10":
            assert value <= 0.75
        assert row["claim_allowed"] == "true"
