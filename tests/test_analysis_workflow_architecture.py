from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATE_SCRIPTS = [
    ROOT / "analyses" / "phase1" / "six_species_baseline" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "phase1" / "neutral_epcsaft_parity" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "paper_validation" / "2015_baygi" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "phase2" / "activity_epcsaft" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "scripts" / "compute_parameter_sensitivity.py",
    ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "scripts" / "fit_trace_carbonate_born.py",
    ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "scripts" / "derive_oh_born_parameter.py",
]

RENDER_SCRIPTS = [
    ROOT / "analyses" / "phase1" / "six_species_baseline" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "phase1" / "neutral_epcsaft_parity" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "paper_validation" / "2015_baygi" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "phase2" / "activity_epcsaft" / "scripts" / "render_figures.py",
    ROOT
    / "analyses"
    / "phase2"
    / "canonical_speciation_sources"
    / "figures"
    / "speciation"
    / "scripts"
    / "render_figure.py",
]


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assigned_string_constants(source: str, name: str) -> list[str]:
    module = ast.parse(source)
    assigned = next(node for node in module.body if isinstance(node, ast.Assign) and node.targets[0].id == name)
    return [node.value.replace("\\", "/") for node in ast.walk(assigned.value) if isinstance(node, ast.Constant) and isinstance(node.value, str)]


class AnalysisWorkflowArchitectureTests(unittest.TestCase):
    def test_render_all_plots_only_runs_render_scripts(self) -> None:
        command_paths = _assigned_string_constants(_source(ROOT / "scripts" / "render_all_plots.py"), "COMMANDS")
        self.assertGreaterEqual(len(command_paths), 4)
        self.assertTrue(all(path.endswith("/render_figures.py") for path in command_paths))
        self.assertFalse(any("generate_data.py" in path for path in command_paths))

    def test_generate_all_analysis_data_keeps_expensive_ionic_generation_opt_in(self) -> None:
        source = _source(ROOT / "scripts" / "generate_all_analysis_data.py")
        self.assertIn("--include-ionic-full", source)
        self.assertIn("--include-expensive", source)
        fast_paths = _assigned_string_constants(source, "FAST_COMMANDS")
        self.assertFalse(any("ionic_epcsaft_regression/scripts/generate_data.py" in path for path in fast_paths))

    def test_generation_scripts_do_not_render_figures(self) -> None:
        forbidden = ("fig.savefig", ".savefig(", "save_plot(", "write_mpl_sidecar(", "plt.subplots(")
        for path in GENERATE_SCRIPTS:
            with self.subTest(path=path):
                source = _source(path)
                self.assertFalse(any(token in source for token in forbidden), f"{path} mixes generation with rendering")

    def test_render_scripts_use_canonical_results_and_write_plot_snapshots(self) -> None:
        for path in RENDER_SCRIPTS:
            with self.subTest(path=path):
                source = _source(path)
                self.assertIn("write_mpl_sidecar", source)
                self.assertIn("data_path=", source)
                if "canonical_speciation_sources" in str(path):
                    self.assertIn("plot_data", source)
                    self.assertIn("save_figure_bundle", source)
                    self.assertIn("read_required_csv", source)
                else:
                    self.assertIn("results", source)
                    if "/paper_validation/" not in path.as_posix():
                        self.assertNotIn("PROCESSED_DIR", source)

    def test_phase3_residual_rendering_excludes_rejected_states(self) -> None:
        source = _source(
            ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "scripts" / "render_figures.py"
        )

        self.assertEqual(source.count('frame = frame.loc[frame["accepted"]].copy()'), 2)

    def test_confidence_validation_uses_render_orchestrator_not_data_generation(self) -> None:
        source = _source(ROOT / "scripts" / "validate_project.py")
        self.assertIn('"scripts/render_all_plots.py"', source)
        plot_section = source.split("PLOT_COMMANDS = [", 1)[1].split("]", 1)[0]
        self.assertNotIn("generate_data.py", plot_section)

    def test_phase1_generation_reuses_canonical_pressure_results(self) -> None:
        source = _source(ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "scripts" / "generate_data.py")
        self.assertIn("six_species_baseline", source)
        self.assertIn("neutral_epcsaft_parity", source)
        self.assertIn("RESULTS_DIR", source)
        self.assertNotIn("compute_jou_metrics", source)
        self.assertNotIn("compute_neutral_parity", source)

    def test_phase1_phase2_figures_have_architecture_owned_io_folders(self) -> None:
        required = [
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "figures" / "pressure" / "input" / "source_manifest.csv",
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "figures" / "pressure" / "output" / "phase1_pressure_plot_data.csv",
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "figures" / "pressure" / "scripts" / "render_figure.py",
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "figures" / "speciation" / "input" / "source_manifest.csv",
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "figures" / "speciation" / "output" / "phase1_speciation_40C_plot_data.csv",
            ROOT / "analyses" / "phase1" / "smith_missen_baseline" / "figures" / "speciation" / "scripts" / "render_figure.py",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "figures" / "speciation" / "input" / "source_manifest.csv",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "figures" / "speciation" / "output" / "phase2_speciation_40C_plot_data.csv",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "figures" / "speciation" / "output" / "phase2_speciation_40C.png",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "figures" / "speciation" / "output" / "phase2_speciation_40C.svg",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "figures" / "speciation" / "output" / "phase2_speciation_40C.pdf",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "figures" / "speciation" / "output" / "phase2_speciation_40C.mpl.yaml",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "figures" / "speciation" / "scripts" / "render_figure.py",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "input" / "source_manifest.csv",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "output" / "canonical_speciation_mole_fraction_grid_plot_data.csv",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "output" / "canonical_speciation_mole_fraction_grid.png",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "output" / "canonical_speciation_mole_fraction_grid.svg",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "output" / "canonical_speciation_mole_fraction_grid.pdf",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "output" / "canonical_speciation_mole_fraction_grid.mpl.yaml",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "scripts" / "generate_data.py",
            ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "scripts" / "render_figure.py",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)

    def test_analysis_scripts_use_category_depth_repo_roots(self) -> None:
        forbidden_root_assignments = (
            "REPO_ROOT = Path(__file__).resolve().parents[3]",
            "REPO_ROOT = Path(__file__).resolve().parents[5]",
            "REPO_ROOT = ANALYSIS_DIR.parents[1]",
        )
        for path in (ROOT / "analyses").rglob("*.py"):
            with self.subTest(path=path):
                source = _source(path)
                self.assertFalse(any(assignment in source for assignment in forbidden_root_assignments), path)

    def test_rendering_does_not_create_analysis_local_docs_tree(self) -> None:
        self.assertFalse((ROOT / "analyses" / "docs").exists())


if __name__ == "__main__":
    unittest.main()
