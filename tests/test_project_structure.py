from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from MEA.common.analysis_io import file_sha256, repo_relative_path
from MEA.common.plot_style import write_mpl_sidecar


ROOT = Path(__file__).resolve().parents[1]
PATH_CHECK_PATH = ROOT / "scripts" / "check_no_local_paths.py"


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

    def test_phase1_and_phase2_have_no_tracked_processed_result_mirrors(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "analyses/phase1/**/data/processed/**", "analyses/phase2/**/data/processed/**"],
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


if __name__ == "__main__":
    unittest.main()
