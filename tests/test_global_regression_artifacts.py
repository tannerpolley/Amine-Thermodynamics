from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "results" / "global_regression"
SENSITIVITY = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "results" / "sensitivity"


class GlobalRegressionArtifactTests(unittest.TestCase):
    def test_global_regression_artifacts_exist(self) -> None:
        required = [
            "global_regression_summary.json",
            "global_regression_values.csv",
            "global_regression_pressure_fit_data.csv",
            "global_regression_speciation_fit_data.csv",
            "global_regression_pressure_residuals.csv",
            "global_regression_speciation_residuals.csv",
        ]
        missing = [name for name in required if not (GLOBAL / name).exists()]
        self.assertEqual(missing, [])

    def test_global_regression_summary_has_submission_metrics(self) -> None:
        summary = json.loads((GLOBAL / "global_regression_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["fit_tier"], "pressure_speciation_global")
        self.assertIn(summary["completion_status"], {"completed", "package_fit_not_completed"})
        self.assertIn("fit_parameters", summary)
        self.assertIn("objective_weights", summary)
        self.assertIn("pressure_metrics", summary)
        self.assertIn("speciation_metrics", summary)
        self.assertIn("parameters_at_bounds", summary)
        self.assertGreaterEqual(summary["pressure_metrics"]["row_count"], 100)
        self.assertGreaterEqual(summary["speciation_metrics"]["row_count"], 50)
        if summary["completion_status"] == "completed":
            self.assertLessEqual(
                summary["pressure_metrics"]["median_abs_log10"],
                summary["baseline_pressure_metrics"]["median_abs_log10"],
            )
            self.assertLessEqual(summary["speciation_metrics"]["MEAH+"]["median_abs_log10"], 0.15)
            self.assertLessEqual(summary["speciation_metrics"]["MEACOO-"]["median_abs_log10"], 0.10)
        else:
            self.assertEqual(summary["selected_parameter_set"], "fixed_provisional_parameter_set")
            self.assertIn("workflow", summary["claim_boundary"].lower())

    def test_global_regression_values_are_not_seed_only_when_completed(self) -> None:
        summary = json.loads((GLOBAL / "global_regression_summary.json").read_text(encoding="utf-8"))
        with (GLOBAL / "global_regression_values.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        moved = [row for row in rows if abs(float(row["fitted"]) - float(row["initial"])) > 1.0e-6]
        if summary["completion_status"] == "completed":
            self.assertGreaterEqual(len(moved), 3)
        else:
            self.assertGreaterEqual(len(rows), 10)


class SensitivityArtifactTests(unittest.TestCase):
    def test_sensitivity_artifacts_exist(self) -> None:
        required = [
            "parameter_sensitivity_summary.json",
            "parameter_sensitivity_matrix.csv",
            "parameter_identifiability.csv",
        ]
        missing = [name for name in required if not (SENSITIVITY / name).exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()

