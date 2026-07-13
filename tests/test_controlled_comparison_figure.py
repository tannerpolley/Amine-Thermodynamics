from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PAIRED_ROWS = (
    ROOT
    / "analyses"
    / "phase2"
    / "activity_epcsaft"
    / "results"
    / "controlled_comparison"
    / "paired_pressure_rows.csv"
)
RENDER_PATH = (
    ROOT
    / "analyses"
    / "phase2"
    / "activity_epcsaft"
    / "scripts"
    / "render_figures.py"
)


def _load_renderer():
    spec = importlib.util.spec_from_file_location(
        "phase2_activity_render_figures_for_comparison_test", RENDER_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load Phase 2 renderer: {RENDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ControlledComparisonFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.render = _load_renderer()
        cls.rows = pd.read_csv(PAIRED_ROWS)

    def test_prepared_plot_data_reproduces_paired_outcomes(self) -> None:
        plot_data = self.render.prepare_controlled_comparison_plot_data(self.rows)

        self.assertEqual(len(plot_data), 31)
        self.assertEqual(
            plot_data["comparison_outcome"].value_counts().to_dict(),
            {"worsened": 27, "improved": 4},
        )
        self.assertTrue((plot_data["ideal_abs_log10_error"] >= 0.0).all())
        self.assertTrue((plot_data["activity_abs_log10_error"] >= 0.0).all())
        self.assertEqual(plot_data["source"].unique().tolist(), ["Jou1995"])

    def test_nonpositive_pressure_is_rejected(self) -> None:
        rows = self.rows.copy()
        rows.loc[0, "observed_CO2_pressure_kPa"] = 0.0

        with self.assertRaisesRegex(ValueError, "positive finite pressure"):
            self.render.prepare_controlled_comparison_plot_data(rows)

    def test_ineligible_paired_row_is_rejected(self) -> None:
        rows = self.rows.copy()
        rows.loc[0, "comparison_eligible"] = False

        with self.assertRaisesRegex(ValueError, "accepted and eligible"):
            self.render.prepare_controlled_comparison_plot_data(rows)


if __name__ == "__main__":
    unittest.main()
