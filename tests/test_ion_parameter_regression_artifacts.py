from __future__ import annotations

import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "results" / "ion_parameter_regression"
TRACE_BORN_RESULTS = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "results" / "trace_carbonate_born_regression"
OH_BORN_RESULTS = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "results" / "oh_born_derivation"
RUNTIME = ROOT / "src" / "MEA" / "epcsaft_runtime.py"
SPECIES_EVIDENCE = ROOT / "data" / "reference" / "MEA" / "epcsaft_species_parameter_evidence.csv"
IONIC_PARAMETER_CSV = (
    ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_ionic_fit" / "pure" / "any_solvent.csv"
)
IONIC_KIJ_CSV = (
    ROOT
    / "data"
    / "reference"
    / "epcsaft_datasets"
    / "MEA_CO2_H2O_ionic_fit"
    / "mixed"
    / "binary_interaction"
    / "k_ij.csv"
)
FULL_SPECIES = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
IONIC_SPECIES = ("MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
PRESSURE_RESULTS = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "results" / "pressure"
SPECIATION_RESULTS = ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "results" / "speciation"
LATEX_ROOT = ROOT / "docs" / "latex"
LATEX_MAIN = LATEX_ROOT / "main.tex"


class IonParameterRegressionArtifactTests(unittest.TestCase):
    def test_real_data_source_manifest_is_present(self) -> None:
        path = ROOT / "data" / "reference" / "MEA" / "ion_parameter_regression_sources.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 7)
        by_id = {row["source_id"]: row for row in rows}
        self.assertEqual(by_id["matin_2012_speciation"]["meah_direct"], "yes")
        self.assertEqual(by_id["matin_2012_speciation"]["meacoo_direct"], "yes")
        self.assertEqual(by_id["bottinger_2008_online_nmr"]["meah_direct"], "no")
        self.assertEqual(by_id["bottinger_2008_online_nmr"]["meacoo_direct"], "yes")

    def test_promoted_ion_fit_is_not_seed_only(self) -> None:
        summary = json.loads((RESULTS / "ion_parameter_fit_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["fit_tier"], "tier_a_local_speciation")
        self.assertGreaterEqual(summary["target_row_count"], 8)
        self.assertIn("Matin", summary["target_sources"])
        self.assertIn("Jakobsen", summary["target_sources"])
        self.assertTrue(summary["optimizer"]["success"])
        self.assertLess(
            summary["optimizer"]["final_residual_norm"],
            summary["optimizer"]["initial_residual_norm"],
        )
        changed = [
            name
            for name, initial in summary["initial_values"].items()
            if abs(float(summary["fitted_values"][name]) - float(initial)) > 1.0e-6
        ]
        self.assertIn("MEAH+__s", changed)
        self.assertIn("MEACOO-__s", changed)
        self.assertIn("MEAH+__d_born", changed)
        self.assertIn("MEACOO-__e", changed)
        self.assertFalse(any(summary["parameters_at_bounds"].values()))

    def test_promoted_ion_fit_artifact_contract(self) -> None:
        required = [
            "ion_parameter_fit_summary.json",
            "ion_parameter_fit_values.csv",
            "ion_parameter_fit_statistics.csv",
            "ion_parameter_speciation_fit_data.csv",
            "ion_parameter_pressure_fit_data.csv",
            "meah_meacoo_speciation_parity.mpl.yaml",
            "meah_meacoo_speciation_parity.png",
            "meah_meacoo_speciation_parity.svg",
            "meah_meacoo_speciation_parity.pdf",
            "meah_meacoo_loading_curves.mpl.yaml",
            "meah_meacoo_loading_curves.png",
            "meah_meacoo_loading_curves.svg",
            "meah_meacoo_loading_curves.pdf",
            "ion_parameter_pressure_parity.mpl.yaml",
            "ion_parameter_pressure_parity.png",
            "ion_parameter_pressure_parity.svg",
            "ion_parameter_pressure_parity.pdf",
        ]
        missing = [name for name in required if not (RESULTS / name).exists()]
        self.assertEqual(missing, [])

    def test_trace_carbonate_born_fit_artifact_contract(self) -> None:
        required = [
            "trace_carbonate_born_fit_summary.json",
            "trace_carbonate_born_fit_values.csv",
            "trace_carbonate_born_fit_data.csv",
            "trace_carbonate_born_multistart_attempts.csv",
            "trace_carbonate_born_parity.mpl.yaml",
            "trace_carbonate_born_parity.png",
            "trace_carbonate_born_parity.svg",
            "trace_carbonate_born_parity.pdf",
        ]
        missing = [name for name in required if not (TRACE_BORN_RESULTS / name).exists()]
        self.assertEqual(missing, [])

        summary = json.loads((TRACE_BORN_RESULTS / "trace_carbonate_born_fit_summary.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["optimizer"]["success"])
        self.assertGreaterEqual(summary["target_row_count"], 8)
        self.assertLessEqual(
            summary["optimizer"]["final_residual_norm"],
            summary["optimizer"]["initial_residual_norm"],
        )
        self.assertFalse(any(summary["parameters_at_bounds"].values()))
        self.assertEqual(set(summary["fit_parameters"]), {"HCO3-__d_born", "CO3^2-__d_born"})
        # The promoted/canonical trace-carbonate fit remains regularized near the
        # Held/Uyan 3.0 Angstrom value, while the multistart diagnostic is allowed
        # to expose lower-residual unanchored candidates for manuscript discussion.
        fitted = summary["fitted_values"]
        self.assertAlmostEqual(float(fitted["HCO3-__d_born"]), 3.0, places=4)
        self.assertAlmostEqual(float(fitted["CO3^2-__d_born"]), 3.0, places=4)
        diagnostic = summary["multistart_diagnostic"]
        self.assertGreaterEqual(diagnostic["attempt_count"], 4)
        best = diagnostic["best_attempt"]
        self.assertTrue(best["optimizer_success"])
        self.assertLessEqual(
            float(best["final_data_residual_norm"]),
            float(summary["optimizer"]["initial_residual_norm"]),
        )
        substantial = diagnostic["best_substantial_attempt"]
        if substantial:
            threshold = float(diagnostic["substantial_threshold_angstrom"])
            self.assertTrue(
                abs(float(substantial["fitted_HCO3_d_born"]) - 3.0) >= threshold
                or abs(float(substantial["fitted_CO3_d_born"]) - 3.0) >= threshold
            )
            self.assertTrue(substantial["optimizer_success"])
            self.assertFalse(substantial["at_lower_bound_HCO3"] or substantial["at_upper_bound_HCO3"])
            self.assertFalse(substantial["at_lower_bound_CO3"] or substantial["at_upper_bound_CO3"])

    def test_oh_born_derivation_artifact_contract(self) -> None:
        required = [
            "oh_born_derivation.json",
            "oh_born_derivation.csv",
            "oh_born_derivation.mpl.yaml",
        ]
        missing = [name for name in required if not (OH_BORN_RESULTS / name).exists()]
        self.assertEqual(missing, [])

        summary = json.loads((OH_BORN_RESULTS / "oh_born_derivation.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["species"], "OH-")
        self.assertEqual(summary["parameter"], "d_born")
        self.assertAlmostEqual(float(summary["promoted_d_born"]), 3.08107689400404, places=8)
        self.assertIn("not an MEA-system regression", summary["source_basis"])

    def test_full_species_and_parameter_scope_is_complete(self) -> None:
        def normalized_scope(scope_text: str) -> set[str]:
            fields = {field.strip() for field in scope_text.split(",") if field.strip()}
            normalized: set[str] = set()
            for field in fields:
                if field == "s(T)":
                    normalized.add("s")
                else:
                    normalized.add(field)
            return normalized

        with SPECIES_EVIDENCE.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        by_species: dict[str, set[str]] = {}
        for row in rows:
            species = row["species"]
            by_species.setdefault(species, set()).update(normalized_scope(row["parameter_scope"]))

        self.assertEqual(set(by_species.keys()), set(FULL_SPECIES))

        required_by_species: dict[str, set[str]] = {
            "CO2": {"m", "s", "e", "dielc", "MW"},
            "MEA": {"m", "s", "e", "e_assoc", "vol_a", "assoc_scheme", "MW"},
            "H2O": {"m", "s", "e", "e_assoc", "vol_a", "dielc", "f_solv", "MW"},
            "MEAH+": {"s", "e", "d_born", "dielc", "f_solv", "z", "MW"},
            "MEACOO-": {"s", "e", "d_born", "dielc", "f_solv", "z", "MW"},
            "HCO3-": {"s", "e", "d_born", "dielc", "f_solv", "z", "MW"},
            "CO3^2-": {"s", "e", "d_born", "dielc", "f_solv", "z", "MW"},
            "H3O+": {"s", "e", "d_born", "dielc", "f_solv", "z", "MW"},
            "OH-": {"s", "e", "d_born", "dielc", "f_solv", "z", "MW"},
        }
        for species, required in required_by_species.items():
            present = by_species[species]
            missing = sorted(required - present)
            self.assertEqual(missing, [], msg=f"{species} missing fields: {missing}")

    def test_active_runtime_species_are_complete(self) -> None:
        runtime_text = RUNTIME.read_text(encoding="utf-8")
        match = re.search(r"SPECIES\s*=\s*\((.*?)\)", runtime_text, re.S)
        self.assertIsNotNone(match, "SPECIES declaration missing from runtime module")
        tuple_body = match.group(1)
        runtime_species = tuple(re.findall(r'"([^"]+)"', tuple_body))
        self.assertCountEqual(runtime_species, FULL_SPECIES)
        for species in IONIC_SPECIES:
            self.assertIn(species, runtime_species)

    def test_trace_ion_literature_values_are_promoted(self) -> None:
        with IONIC_PARAMETER_CSV.open(encoding="utf-8", newline="") as handle:
            rows = {row["component"]: row for row in csv.DictReader(handle)}

        expected = {
            "HCO3-": {"s": 2.9296, "e": 70.0, "d_born": 3.0},
            "CO3^2-": {"s": 2.4422, "e": 249.26, "d_born": 3.0},
            "H3O+": {"s": 3.4654, "e": 500.0, "d_born": 1.218},
            "OH-": {"s": 2.0177, "e": 650.0, "d_born": 3.08107689400404},
        }
        for species, values in expected.items():
            for field, expected_value in values.items():
                self.assertAlmostEqual(
                    float(rows[species][field]),
                    expected_value,
                    places=6,
                    msg=f"{species} {field} should match the audited literature-backed promoted value",
                )

        with IONIC_KIJ_CSV.open(encoding="utf-8", newline="") as handle:
            kij_rows = {row["component"]: row for row in csv.DictReader(handle)}
        expected_kij = {
            ("H2O", "HCO3-"): 0.0,
            ("H2O", "CO3^2-"): -0.25,
            ("H2O", "H3O+"): 0.25,
            ("H2O", "OH-"): -0.25,
        }
        for (left, right), expected_value in expected_kij.items():
            self.assertAlmostEqual(float(kij_rows[left][right]), expected_value, places=6)
            self.assertAlmostEqual(float(kij_rows[right][left]), expected_value, places=6)

    def test_full_ionic_plot_artifacts_include_expected_formats(self) -> None:
        required_with_formats = {
            "meah_meacoo_speciation_parity": ("csv", "png", "svg", "pdf", "mpl.yaml"),
            "meah_meacoo_loading_curves": ("csv", "png", "svg", "pdf", "mpl.yaml"),
            "ion_parameter_pressure_parity": ("csv", "png", "svg", "pdf", "mpl.yaml"),
            "ionic_epcsaft_co2_pressure": ("csv", "png", "svg", "pdf", "mpl.yaml"),
            "ionic_epcsaft_speciation_activity": ("csv", "png", "svg", "pdf", "mpl.yaml"),
        }
        csv_by_stem = {
            "meah_meacoo_speciation_parity": "ion_parameter_speciation_fit_data.csv",
            "meah_meacoo_loading_curves": "ion_parameter_speciation_fit_data.csv",
            "ion_parameter_pressure_parity": "ion_parameter_pressure_fit_data.csv",
            "ionic_epcsaft_co2_pressure": "ionic_pressure_comparison.csv",
            "ionic_epcsaft_speciation_activity": "ionic_speciation_plot_data.csv",
        }

        for stem, exts in required_with_formats.items():
            base_dir = RESULTS
            if stem.startswith("ionic_epcsaft_co2_pressure"):
                base_dir = PRESSURE_RESULTS
            elif stem.startswith("ionic_epcsaft_speciation_activity"):
                base_dir = SPECIATION_RESULTS

            csv_name = csv_by_stem[stem]
            for ext in exts:
                if ext == "csv":
                    artifact = (base_dir / csv_name)
                else:
                    artifact = base_dir / f"{stem}.{ext}"
                self.assertTrue(
                    artifact.exists(),
                    msg=f"Missing {stem} artifact {artifact.relative_to(ROOT)}",
                )

    def test_latex_source_and_output_conventions(self) -> None:
        self.assertTrue(LATEX_MAIN.exists(), msg="Missing docs/latex/main.tex")
        self.assertTrue(LATEX_ROOT.joinpath(".latexmkrc").exists())
        self.assertTrue(LATEX_ROOT.joinpath("builds").exists())
        self.assertTrue(LATEX_ROOT.joinpath("tables", "literature_model_comparison.tex").exists())
        self.assertTrue(LATEX_ROOT.joinpath("tables", "regression_bounds.tex").exists())
        self.assertTrue(LATEX_ROOT.joinpath("sections", "data_code_availability.tex").exists())

        latex_text = LATEX_MAIN.read_text(encoding="utf-8")
        self.assertIn(r"\documentclass", latex_text)
        self.assertIn(r"\begin{document}", latex_text)
        self.assertIn(r"\end{document}", latex_text)
        self.assertIn(r"\input{sections/", latex_text)
        self.assertIn(r"\input{sections/data_code_availability}", latex_text)

        latexmkrc = LATEX_ROOT.joinpath(".latexmkrc").read_text(encoding="utf-8")
        self.assertIn("out_dir = 'builds'", latexmkrc)
        self.assertIn("aux_dir = 'builds'", latexmkrc)

        root_pdf = LATEX_ROOT / "main.pdf"
        builds_pdf = LATEX_ROOT / "builds" / "main.pdf"
        self.assertFalse(root_pdf.exists(), msg="main.pdf should not be written at docs/latex root")
        self.assertTrue(builds_pdf.exists(), msg="docs/latex/builds/main.pdf is missing")

        intro_text = LATEX_ROOT.joinpath("sections", "introduction.tex").read_text(encoding="utf-8")
        self.assertIn(r"\input{tables/literature_model_comparison}", intro_text)


if __name__ == "__main__":
    unittest.main()
