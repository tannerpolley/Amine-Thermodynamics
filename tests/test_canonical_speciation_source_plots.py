from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "analyses" / "phase2" / "canonical_speciation_sources" / "figures" / "speciation" / "output"
CANONICAL = ROOT / "data" / "reference" / "MEA" / "ChEq" / "Canonical_Combined_ChEq.csv"


def _plot_bundle(stem: str) -> list[Path]:
    return [
        OUTPUT / f"{stem}_plot_data.csv",
        OUTPUT / f"{stem}.png",
        OUTPUT / f"{stem}.svg",
        OUTPUT / f"{stem}.pdf",
        OUTPUT / f"{stem}.mpl.yaml",
    ]


class CanonicalSpeciationSourcePlotTests(unittest.TestCase):
    def test_canonical_speciation_plot_bundles_exist(self) -> None:
        required = [
            *_plot_bundle("canonical_speciation_mole_fraction_grid"),
            *_plot_bundle("canonical_speciation_loaded_molkg_grid"),
            *_plot_bundle("canonical_speciation_wong_source_molkg"),
            OUTPUT / "canonical_speciation_source_summary.csv",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)

    def test_plot_data_are_sourced_from_canonical_dataset(self) -> None:
        canonical = pd.read_csv(CANONICAL)
        mole = pd.read_csv(OUTPUT / "canonical_speciation_mole_fraction_grid_plot_data.csv")
        loaded = pd.read_csv(OUTPUT / "canonical_speciation_loaded_molkg_grid_plot_data.csv")
        wong = pd.read_csv(OUTPUT / "canonical_speciation_wong_source_molkg_plot_data.csv")

        self.assertEqual(set(mole["source_key"]), {"Bottinger2008", "Jakobsen2005", "Matin2012"})
        self.assertEqual(set(loaded["source_key"]), {"Bottinger2008", "Jakobsen2005", "Matin2012"})
        self.assertEqual(set(wong["source_key"]), {"Wong2015"})
        self.assertEqual(len(mole), 400)
        self.assertEqual(len(loaded), 400)
        self.assertEqual(len(wong), 71)
        self.assertEqual(len(canonical), 571)

        self.assertTrue((mole["plot_basis"] == "liquid_mole_fraction").all())
        self.assertTrue((loaded["plot_basis"] == "mol_per_kg_loaded_solution").all())
        self.assertTrue((wong["plot_basis"] == "source_reported_mol_per_kg").all())
        self.assertFalse((loaded["source_key"] == "Wong2015").any())
        self.assertFalse((mole["source_key"] == "Wong2015").any())
        self.assertGreaterEqual(int((wong["row_status"] == "ambiguous").sum()), 1)


if __name__ == "__main__":
    unittest.main()
