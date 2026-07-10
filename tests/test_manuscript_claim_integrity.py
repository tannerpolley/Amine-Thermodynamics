from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
