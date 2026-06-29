from __future__ import annotations

import csv
import unittest
from pathlib import Path

from MEA.smith_missen.ideal_speciation import SPECIES_9, solve_ideal_speciation

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase1CompletionGateTests(unittest.TestCase):
    def test_phase1_reaction_constant_signs_match_source_values(self) -> None:
        path = ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "results" / "phase1_reaction_constant_table.csv"
        by_id = {row["reaction_id"]: row for row in _rows(path)}
        self.assertAlmostEqual(float(by_id["R1"]["C"]), -22.4773, places=4)
        self.assertAlmostEqual(float(by_id["R2"]["A"]), 231.465, places=3)
        self.assertAlmostEqual(float(by_id["R3"]["C"]), -35.4819, places=4)
        self.assertAlmostEqual(float(by_id["R5"]["D"]), -0.007484, places=6)

    def test_phase1_residual_audit_records_pass_and_claim_gates(self) -> None:
        path = ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "results" / "phase1_residual_acceptance_audit.csv"
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
        major_species = {"MEA", "MEAH+", "MEACOO-", "HCO3-", "MEA + MEAH+"}
        major_median_rows = [
            row
            for row in rows
            if row["target_family"] == "speciation"
            and row["species_or_property"] in major_species
            and row["temperature_C"] == "overall"
            and row["metric"] == "median_abs_log10_error"
        ]
        self.assertEqual({row["species_or_property"] for row in major_median_rows}, major_species)
        self.assertTrue(all(row["claim_allowed"] == "true" for row in major_median_rows))

    def test_phase1_ideal_solver_solves_full_reaction_basis(self) -> None:
        result = solve_ideal_speciation(0.4, 0.3, 313.15)
        self.assertEqual(SPECIES_9, ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"))
        self.assertLess(result.max_abs_residual, 1.0e-8)

    def test_phase1_claim_boundary_keeps_status_bounded(self) -> None:
        lineage = (
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "results" / "phase1_model_lineage.md"
        ).read_text(encoding="utf-8")
        claim_boundary = (
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "results" / "phase1_claim_boundary.md"
        ).read_text(encoding="utf-8")
        self.assertIn("lineage_status: explicit_ideal_smith_missen_reproduction", lineage)
        self.assertIn("phase1_status: validated_major_species_speciation_with_pressure_limits", claim_boundary)
        self.assertIn("explicit five-reaction, nine-species ideal Smith-Missen", claim_boundary)
        self.assertNotIn("phase1_status: model_ran_but_" + "failed_validation", claim_boundary)

    def test_phase1_speciation_figure_is_full_ideal_equilibrium_output(self) -> None:
        result_dir = ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "results"
        self.assertTrue((result_dir / "phase1_speciation_vs_loading.png").exists())
        self.assertTrue((result_dir / "phase1_speciation_vs_loading.svg").exists())
        self.assertTrue((result_dir / "phase1_speciation_vs_loading.pdf").exists())
        self.assertTrue((result_dir / "phase1_speciation_vs_loading.mpl.yaml").exists())
        self.assertTrue((result_dir / "phase1_speciation_vs_loading_plot_data.csv").exists())
        self.assertFalse((result_dir / "phase1_speciation_vs_loading_diagnostic.png").exists())
        self.assertFalse((result_dir / "phase1_speciation_vs_loading_diagnostic.svg").exists())
        self.assertFalse((result_dir / "phase1_speciation_vs_loading_diagnostic.pdf").exists())
        self.assertFalse((result_dir / "phase1_speciation_vs_loading_diagnostic.mpl.yaml").exists())

    def test_phase1_speciation_output_has_full_continuous_species_curves(self) -> None:
        output = ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "figures" / "speciation" / "output"
        rows = _rows(output / "phase1_speciation_curve.csv")
        selected = [row for row in rows if row["temperature_C"] == "40.0" and row["species"] == "MEA + MEAH+"]
        self.assertGreaterEqual(len(selected), 150)
        loadings = [float(row["CO2_loading"]) for row in selected]
        self.assertAlmostEqual(min(loadings), 0.0, places=6)
        self.assertAlmostEqual(max(loadings), 0.8, places=6)
        plot_rows = _rows(output / "phase1_speciation_40C_plot_data.csv")
        curve_species = {row["species"] for row in plot_rows if row["role"] == "curve"}
        self.assertIn("H3O+", curve_species)
        self.assertIn("OH-", curve_species)


if __name__ == "__main__":
    unittest.main()
