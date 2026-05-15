from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase1CompletionGateTests(unittest.TestCase):
    def test_phase1_reaction_constant_signs_match_source_values(self) -> None:
        path = ROOT / "analyses" / "phase1_smith_missen_baseline" / "results" / "phase1_reaction_constant_table.csv"
        by_id = {row["reaction_id"]: row for row in _rows(path)}
        self.assertAlmostEqual(float(by_id["R1"]["C"]), -22.4773, places=4)
        self.assertAlmostEqual(float(by_id["R2"]["A"]), 231.465, places=3)
        self.assertAlmostEqual(float(by_id["R3"]["C"]), -35.4819, places=4)
        self.assertAlmostEqual(float(by_id["R5"]["D"]), -0.007484, places=6)

    def test_phase1_residual_audit_records_pass_and_claim_gates(self) -> None:
        path = ROOT / "analyses" / "phase1_smith_missen_baseline" / "results" / "phase1_residual_acceptance_audit.csv"
        rows = _rows(path)
        self.assertTrue(rows)
        required_columns = {
            "target_family",
            "source_or_model",
            "temperature_C",
            "species_or_property",
            "metric",
            "threshold",
            "actual_value",
            "passes",
            "claim_allowed",
            "failure_reason",
            "recommended_manuscript_use",
        }
        self.assertTrue(required_columns.issubset(rows[0].keys()))
        pressure_overall = [
            row
            for row in rows
            if row["target_family"] == "pressure"
            and row["temperature_C"] == "overall"
            and row["metric"] == "median_abs_log10_error"
        ]
        self.assertTrue(pressure_overall)
        self.assertTrue(all(row["passes"] == "true" for row in pressure_overall))
        failed_or_diagnostic = [row for row in rows if row["claim_allowed"] != "true"]
        self.assertTrue(failed_or_diagnostic)
        self.assertTrue(any(row["species_or_property"] == "CO3^2-" for row in failed_or_diagnostic))
        self.assertTrue(any(row["species_or_property"] == "H3O+" for row in failed_or_diagnostic))

    def test_phase1_claim_boundary_keeps_status_bounded(self) -> None:
        lineage = (
            ROOT / "analyses" / "phase1_smith_missen_baseline" / "results" / "phase1_model_lineage.md"
        ).read_text(encoding="utf-8")
        claim_boundary = (
            ROOT / "analyses" / "phase1_smith_missen_baseline" / "results" / "phase1_claim_boundary.md"
        ).read_text(encoding="utf-8")
        self.assertIn("lineage_status: retained_baseline_audit", lineage)
        self.assertIn("phase1_status: model_ran_but_failed_validation", claim_boundary)
        self.assertIn("Do not claim Phase 1 has passed validation.", claim_boundary)
        self.assertNotIn("phase1_status: validated", claim_boundary)

    def test_phase1_speciation_figure_is_labeled_diagnostic(self) -> None:
        result_dir = ROOT / "analyses" / "phase1_smith_missen_baseline" / "results"
        self.assertTrue((result_dir / "phase1_speciation_vs_loading_diagnostic.png").exists())
        self.assertTrue((result_dir / "phase1_speciation_vs_loading_diagnostic.svg").exists())
        self.assertTrue((result_dir / "phase1_speciation_vs_loading_diagnostic.mpl.yaml").exists())
        self.assertFalse((result_dir / "phase1_speciation_vs_loading.png").exists())
        self.assertFalse((result_dir / "phase1_speciation_vs_loading.svg").exists())
        self.assertFalse((result_dir / "phase1_speciation_vs_loading.mpl.yaml").exists())


if __name__ == "__main__":
    unittest.main()
