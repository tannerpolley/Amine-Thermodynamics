from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import matplotlib.pyplot as plt

from MEA.common.analysis_io import file_sha256, repo_relative_path
from MEA.common.plot_style import save_figure_bundle, write_mpl_sidecar


ROOT = Path(__file__).resolve().parents[1]
PATH_CHECK_PATH = ROOT / "scripts" / "check_no_local_paths.py"
ANALYSIS_MANIFESTS = sorted((ROOT / "analyses").glob("**/analysis.yaml"))


def _load_path_check():
    spec = importlib.util.spec_from_file_location("check_no_local_paths", PATH_CHECK_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load path checker: {PATH_CHECK_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PortableArtifactTests(unittest.TestCase):
    def test_repo_relative_path_rejects_external_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside repository"):
            repo_relative_path(Path("/tmp/external-result.csv"))

    def test_json_escaped_windows_path_is_rejected(self) -> None:
        module = _load_path_check()
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "summary.json"
            path.write_text('{"artifact":"C:\\\\Users\\\\Tanner\\\\result.csv"}\n', encoding="utf-8")

            self.assertTrue(module.scan_file(path))

    def test_sidecar_records_repo_relative_data_path_and_hash(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary_directory:
            directory = Path(temporary_directory)
            data_path = directory / "plot_data.csv"
            sidecar_path = directory / "plot.mpl.yaml"
            data_path.write_text("x,y\n1,2\n", encoding="utf-8")

            write_mpl_sidecar(
                sidecar_path,
                png_name="plot.png",
                svg_name="plot.svg",
                pdf_name="plot.pdf",
                title="Plot",
                description="Test plot.",
                data_path=data_path,
            )
            sidecar = sidecar_path.read_text(encoding="utf-8")

            self.assertIn(f"data_path: {repo_relative_path(data_path)}", sidecar)
            self.assertIn(f"data_sha256: {file_sha256(data_path)}", sidecar)

    def test_figure_bundle_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary_directory:
            directory = Path(temporary_directory)
            fig, ax = plt.subplots()
            ax.plot([0.0, 1.0], [1.0, 0.0])
            first = save_figure_bundle(fig, directory / "first")
            second = save_figure_bundle(fig, directory / "second")
            plt.close(fig)

            self.assertEqual([file_sha256(path) for path in first], [file_sha256(path) for path in second])


class ArtifactOwnershipTests(unittest.TestCase):
    def test_phase1_and_phase2_sidecars_match_plotted_data(self) -> None:
        sidecars = [
            *sorted((ROOT / "analyses" / "phase1").rglob("*.mpl.yaml")),
            *sorted((ROOT / "analyses" / "phase2").rglob("*.mpl.yaml")),
        ]
        self.assertTrue(sidecars)
        for sidecar in sidecars:
            with self.subTest(sidecar=sidecar):
                text = sidecar.read_text(encoding="utf-8")
                data_match = re.search(r"^\s*data_path:\s*(.+)$", text, flags=re.MULTILINE)
                hash_match = re.search(r"^\s*data_sha256:\s*([0-9a-f]{64})$", text, flags=re.MULTILINE)
                self.assertIsNotNone(data_match)
                self.assertIsNotNone(hash_match)
                data_path = ROOT / data_match.group(1).strip()
                self.assertTrue(data_path.is_file(), data_path)
                self.assertEqual(hash_match.group(1), file_sha256(data_path))

    def test_active_phases_have_no_tracked_processed_result_mirrors(self) -> None:
        result = subprocess.run(
            [
                "git",
                "ls-files",
                "analyses/phase1/**/data/processed/**",
                "analyses/phase2/**/data/processed/**",
                "analyses/phase3/**/data/processed/**",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "")

    def test_figure_outputs_do_not_mirror_whole_calculation_tables(self) -> None:
        redundant_paths = (
            ROOT
            / "analyses"
            / "phase1"
            / "smith_missen_baseline"
            / "figures"
            / "speciation"
            / "output"
            / "phase1_speciation_curve.csv",
            ROOT
            / "analyses"
            / "phase1"
            / "smith_missen_baseline"
            / "figures"
            / "speciation"
            / "output"
            / "phase1_speciation_reference_points.csv",
            ROOT
            / "analyses"
            / "phase2"
            / "activity_epcsaft"
            / "figures"
            / "pressure"
            / "output"
            / "phase2_pressure_results.csv",
            ROOT
            / "analyses"
            / "phase2"
            / "activity_epcsaft"
            / "figures"
            / "pressure"
            / "output"
            / "phase2_pressure_metrics.csv",
            ROOT
            / "analyses"
            / "phase2"
            / "activity_epcsaft"
            / "figures"
            / "speciation"
            / "output"
            / "phase2_speciation_activity_curves.csv",
            ROOT
            / "analyses"
            / "phase2"
            / "activity_epcsaft"
            / "figures"
            / "speciation"
            / "output"
            / "phase2_speciation_reference_points.csv",
        )

        self.assertEqual([path.relative_to(ROOT).as_posix() for path in redundant_paths if path.exists()], [])

    def test_phase2_generator_writes_only_canonical_results(self) -> None:
        source = (
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "scripts" / "generate_data.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("write_dual", source)
        self.assertNotIn("PROCESSED_DIR", source)


class AnalysisManifestTests(unittest.TestCase):
    def test_all_analysis_manifests_use_the_complete_contract(self) -> None:
        self.assertEqual(len(ANALYSIS_MANIFESTS), 7)
        required_top_level = (
            "id:",
            "title:",
            "status:",
            "summary:",
            "owner:",
            "inputs:",
            "outputs:",
            "commands:",
            "runtime:",
            "manuscript_consumers:",
            "results_policy:",
        )
        for path in ANALYSIS_MANIFESTS:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                top_level = {line.split(":", 1)[0] + ":" for line in text.splitlines() if line and not line[0].isspace()}
                self.assertTrue(set(required_top_level).issubset(top_level))
                self.assertRegex(text, r"(?m)^  - path: .+$")
                self.assertRegex(text, r"(?m)^    kind: .+$")
                self.assertRegex(text, r"(?m)^  class: (quick|standard|expensive)$")

    def test_plot_registry_matches_current_svg_bundles_exactly(self) -> None:
        manifest = (ROOT / ".mplgallery" / "manifest.yaml").read_text(encoding="utf-8")
        registered_svgs = {
            match.group(1).strip()
            for match in re.finditer(r"(?m)^  svg_path:\s*(.+)$", manifest)
        }
        registered_sidecars = {
            match.group(1).strip()
            for match in re.finditer(r"(?m)^  sidecar_path:\s*(.+)$", manifest)
        }
        data_paths = [
            match.group(1).strip()
            for match in re.finditer(r"(?m)^  data_path:\s*(.+)$", manifest)
        ]
        expected_svgs = {
            path.relative_to(ROOT).as_posix() for path in (ROOT / "analyses").rglob("*.svg")
        }
        expected_sidecars = {str(Path(path).with_suffix(".mpl.yaml")) for path in expected_svgs}

        self.assertEqual(registered_svgs, expected_svgs)
        self.assertEqual(registered_sidecars, expected_sidecars)
        self.assertEqual(len(data_paths), len(expected_svgs))
        self.assertTrue(all((ROOT / path).is_file() for path in data_paths))

    def test_phase3_generator_writes_only_canonical_results(self) -> None:
        source = (
            ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "scripts" / "generate_data.py"
        ).read_text(encoding="utf-8")

        self.assertIn("PRESSURE_DIR", source)
        self.assertIn("SPECIATION_DIR", source)
        self.assertIn("_load_fixed_values", source)
        self.assertNotIn("_load_fitted_values", source)
        self.assertNotIn("PROCESSED_DIR", source)


if __name__ == "__main__":
    unittest.main()
