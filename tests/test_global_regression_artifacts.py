from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = ROOT / "analyses" / "epcsaft_ionic_regression" / "results" / "global_regression"
TRAIN_VALIDATION = ROOT / "analyses" / "epcsaft_ionic_regression" / "results" / "train_validation"
SENSITIVITY = ROOT / "analyses" / "epcsaft_ionic_regression" / "results" / "sensitivity"


class GlobalRegressionArtifactTests(unittest.TestCase):
    def test_global_regression_artifacts_exist(self) -> None:
        required = [
            "global_regression_summary.json",
            "global_regression_values.csv",
            "global_regression_pressure_fit_data.csv",
            "global_regression_speciation_fit_data.csv",
            "global_regression_pressure_residuals.csv",
            "global_regression_speciation_residuals.csv",
            "global_regression_pressure_parity.mpl.yaml",
            "global_regression_pressure_parity.png",
            "global_regression_pressure_parity.svg",
            "global_regression_speciation_parity.mpl.yaml",
            "global_regression_speciation_parity.png",
            "global_regression_speciation_parity.svg",
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
            self.assertEqual(summary["selected_parameter_set"], "promoted_ionic_fit")
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


class TrainValidationArtifactTests(unittest.TestCase):
    def test_train_validation_artifacts_exist(self) -> None:
        required = [
            "train_validation_summary.json",
            "train_validation_pressure_residuals.csv",
            "train_validation_speciation_residuals.csv",
            "train_validation_pressure_by_source.csv",
            "train_validation_speciation_by_species.csv",
            "train_validation_pressure_residuals.mpl.yaml",
            "train_validation_pressure_residuals.png",
            "train_validation_pressure_residuals.svg",
        ]
        missing = [name for name in required if not (TRAIN_VALIDATION / name).exists()]
        self.assertEqual(missing, [])

    def test_train_validation_has_both_splits(self) -> None:
        summary = json.loads((TRAIN_VALIDATION / "train_validation_summary.json").read_text(encoding="utf-8"))
        self.assertIn("train", summary["pressure"])
        self.assertIn("validation", summary["pressure"])
        self.assertIn("train", summary["speciation"])
        self.assertIn("validation", summary["speciation"])


class SensitivityArtifactTests(unittest.TestCase):
    def test_sensitivity_artifacts_exist(self) -> None:
        required = [
            "parameter_sensitivity_summary.json",
            "parameter_sensitivity_matrix.csv",
            "parameter_identifiability.csv",
            "parameter_sensitivity_heatmap.mpl.yaml",
            "parameter_sensitivity_heatmap.png",
            "parameter_sensitivity_heatmap.svg",
        ]
        missing = [name for name in required if not (SENSITIVITY / name).exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()

