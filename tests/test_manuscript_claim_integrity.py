from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LATEX_ROOT = ROOT / "docs" / "latex"
PHASE3_ROOT = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression"


class ManuscriptClaimIntegrityTests(unittest.TestCase):
    def test_manuscript_does_not_promote_historical_local_fit(self) -> None:
        manuscript = "\n".join(path.read_text(encoding="utf-8-sig") for path in LATEX_ROOT.rglob("*.tex"))
        lowered = manuscript.lower()
        for phrase in (
            "direct amine-ion regression",
            "retained fit decreases",
            "train-validation split",
            "directly fitted amine-family",
            "regression results for the",
            "fitted to \\mea speciation data",
        ):
            self.assertNotIn(phrase, lowered)
        self.assertIn("provisional fixed input", lowered)
        self.assertIn("coupled native regression was not completed", lowered)

    def test_parameter_table_exposes_source_status_without_this_work_label(self) -> None:
        table = (LATEX_ROOT / "tables" / "full_ionic_ssm_ds_parameters.tex").read_text(encoding="utf-8-sig")
        self.assertNotIn("This work", table)
        self.assertIn("Source/status", table)
        self.assertIn("Provisional fixed input", table)

    def test_obsolete_local_fit_contract_is_removed(self) -> None:
        obsolete = (
            LATEX_ROOT / "tables" / "regression_bounds.tex",
            LATEX_ROOT / "figures" / "meah_meacoo_speciation_parity.pdf",
            LATEX_ROOT / "figures" / "meah_meacoo_loading_curves.pdf",
            PHASE3_ROOT / "scripts" / "fit_ion_parameters.py",
            PHASE3_ROOT / "results" / "ion_parameter_regression",
            ROOT / "src" / "MEA" / "epcsaft_ionic" / "ion_parameter_regression.py",
        )
        self.assertEqual([str(path.relative_to(ROOT)) for path in obsolete if path.exists()], [])

    def test_posthoc_split_is_not_presented_as_train_validation(self) -> None:
        self.assertFalse((PHASE3_ROOT / "scripts" / "evaluate_train_validation_split.py").exists())
        self.assertFalse((PHASE3_ROOT / "results" / "train_validation").exists())

    def test_single_author_and_loading_symbol_are_consistent(self) -> None:
        main = (LATEX_ROOT / "main.tex").read_text(encoding="utf-8-sig")
        nomenclature = (LATEX_ROOT / "sections" / "nomenclature.tex").read_text(encoding="utf-8-sig")

        self.assertIn(r"\shortauthors{Polley}", main)
        self.assertNotIn(r"\shortauthors{Polley et al.}", main)
        self.assertIn(r"\(\alpha\) & \COtwo loading", nomenclature)
        self.assertNotIn(r"\(L\) & \COtwo loading", nomenclature)

    def test_controlled_comparison_claims_match_generated_evidence(self) -> None:
        comparison = json.loads(
            (
                ROOT
                / "analyses/phase2/activity_epcsaft/results/controlled_comparison/metrics.json"
            ).read_text(encoding="utf-8")
        )
        summary = comparison["summary"]
        overall = {
            row["model"]: row
            for row in comparison["metrics"]
            if row["scope"] == "paired" and row["group_type"] == "overall"
        }
        table = (LATEX_ROOT / "tables" / "residual_summary.tex").read_text(
            encoding="utf-8-sig"
        )
        results = (
            LATEX_ROOT / "sections" / "mea_system_modeling_results.tex"
        ).read_text(encoding="utf-8-sig")
        abstract = (LATEX_ROOT / "main.tex").read_text(encoding="utf-8-sig")
        conclusion = (LATEX_ROOT / "sections" / "conclusion.tex").read_text(
            encoding="utf-8-sig"
        )

        self.assertEqual(summary["paired_row_count"], 31)
        self.assertEqual(summary["reported_zero_target_count"], 15)
        self.assertIn("Same-record", table)
        self.assertIn("Full-set context", table)
        for model in ("ideal_baseline", "activity_model"):
            for metric in (
                "median_log10_residual",
                "median_abs_log10_error",
                "rmse_log10_error",
            ):
                self.assertIn(f'{overall[model][metric]:.3f}', table)
        self.assertIn("Reported-zero targets & 15", table)
        self.assertNotIn("Reported-zero targets & 14", table)
        self.assertIn("same 31 Jou1995 records", results)
        self.assertIn("improves 4 of the 31 paired rows and worsens 27", results)
        self.assertIn("No pressure uncertainty is reported", results)
        self.assertIn("Wong", results)
        self.assertIn("excluded from the residual metrics", results)
        self.assertIn("642 of 644", results)
        self.assertIn("diagnostic only", results)
        self.assertIn("On the 31-record intersection", abstract)
        self.assertIn("0.160 for the ideal baseline and 0.495 for the activity model", abstract)
        self.assertIn("controlled 31-row pressure comparison", conclusion)
        self.assertIn("the activity model is less accurate", conclusion)
        self.assertIn("15 reported-zero targets", conclusion)


if __name__ == "__main__":
    unittest.main()
