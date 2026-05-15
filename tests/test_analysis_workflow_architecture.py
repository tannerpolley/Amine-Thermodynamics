from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATE_SCRIPTS = [
    ROOT / "analyses" / "six_species_legacy" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "epcsaft_neutral_parity" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "epcsaft_ionic_regression" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "2015_baygi" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "phase1_smith_missen_baseline" / "scripts" / "generate_data.py",
    ROOT / "analyses" / "epcsaft_ionic_regression" / "scripts" / "evaluate_train_validation_split.py",
    ROOT / "analyses" / "epcsaft_ionic_regression" / "scripts" / "compute_parameter_sensitivity.py",
    ROOT / "analyses" / "epcsaft_ionic_regression" / "scripts" / "fit_trace_carbonate_born.py",
    ROOT / "analyses" / "epcsaft_ionic_regression" / "scripts" / "derive_oh_born_parameter.py",
]

RENDER_SCRIPTS = [
    ROOT / "analyses" / "six_species_legacy" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "epcsaft_neutral_parity" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "epcsaft_ionic_regression" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "2015_baygi" / "scripts" / "render_figures.py",
    ROOT / "analyses" / "phase1_smith_missen_baseline" / "scripts" / "render_figures.py",
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
        self.assertFalse(any("epcsaft_ionic_regression/scripts/generate_data.py" in path for path in fast_paths))

    def test_generation_scripts_do_not_render_figures(self) -> None:
        forbidden = ("fig.savefig", ".savefig(", "save_plot(", "write_mpl_sidecar(", "plt.subplots(")
        for path in GENERATE_SCRIPTS:
            with self.subTest(path=path):
                source = _source(path)
                self.assertFalse(any(token in source for token in forbidden), f"{path} mixes generation with rendering")

    def test_render_scripts_use_processed_data_and_snapshot_results(self) -> None:
        for path in RENDER_SCRIPTS:
            with self.subTest(path=path):
                source = _source(path)
                self.assertIn("data", source)
                self.assertIn("processed", source)
                self.assertIn("results", source)
                self.assertIn(".to_csv", source)

    def test_confidence_validation_uses_render_orchestrator_not_data_generation(self) -> None:
        source = _source(ROOT / "scripts" / "validate_project.py")
        self.assertIn('"scripts/render_all_plots.py"', source)
        plot_section = source.split("PLOT_COMMANDS = [", 1)[1].split("]", 1)[0]
        self.assertNotIn("generate_data.py", plot_section)

    def test_phase1_generation_reuses_processed_pressure_artifacts(self) -> None:
        source = _source(ROOT / "analyses" / "phase1_smith_missen_baseline" / "scripts" / "generate_data.py")
        self.assertIn("six_species_legacy", source)
        self.assertIn("epcsaft_neutral_parity", source)
        self.assertNotIn("compute_jou_metrics", source)
        self.assertNotIn("compute_neutral_parity", source)


if __name__ == "__main__":
    unittest.main()
