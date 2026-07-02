from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "reference" / "MEA" / "ChEq" / "Canonical_Combined_ChEq.csv"
SCHEMA_PATH = ROOT / "data" / "reference" / "MEA" / "ChEq" / "Canonical_Combined_ChEq_schema.csv"
GENERATOR_PATH = ROOT / "scripts" / "build_canonical_cheq_dataset.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("build_canonical_cheq_dataset", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CanonicalChEqDatasetTests(unittest.TestCase):
    def test_canonical_dataset_contains_all_machine_readable_speciation_sources(self) -> None:
        dataset = pd.read_csv(DATASET_PATH)
        self.assertEqual(
            set(dataset["source_key"]),
            {"Bottinger2008", "Jakobsen2005", "Matin2012", "Wong2015"},
        )
        self.assertEqual(len(dataset), 571)
        self.assertEqual(
            dataset.groupby("source_key").size().to_dict(),
            {
                "Bottinger2008": 272,
                "Jakobsen2005": 152,
                "Matin2012": 76,
                "Wong2015": 71,
            },
        )

    def test_unit_columns_are_populated_by_source_basis(self) -> None:
        dataset = pd.read_csv(DATASET_PATH)
        legacy = dataset[dataset["reported_basis"] == "mole_fraction"]
        wong = dataset[dataset["source_key"] == "Wong2015"]

        self.assertEqual(set(legacy["source_key"]), {"Bottinger2008", "Jakobsen2005", "Matin2012"})
        self.assertTrue(legacy["value_mole_fraction"].notna().all())
        self.assertTrue(legacy["value_mol_per_kg_unloaded_solution"].notna().all())
        self.assertTrue(legacy["value_mol_per_kg_initial_water"].notna().all())
        self.assertTrue(legacy["value_mol_per_kg_loaded_solution"].notna().all())

        self.assertEqual(set(wong["reported_basis"]), {"mol_per_kg_source_basis"})
        self.assertTrue(wong["value_mol_per_kg_source_basis"].notna().all())
        self.assertTrue(wong["value_mole_fraction"].isna().all())
        self.assertTrue(wong["value_mol_per_kg_unloaded_solution"].isna().all())

    def test_generator_reproduces_tracked_schema_and_row_shape(self) -> None:
        module = _load_generator()
        generated = module.build_dataset()
        tracked = pd.read_csv(DATASET_PATH)
        schema = pd.read_csv(SCHEMA_PATH)

        self.assertEqual(list(generated.columns), list(tracked.columns))
        self.assertEqual(len(generated), len(tracked))
        self.assertEqual(list(schema["column"]), list(tracked.columns))

    def test_jakobsen_reported_zero_is_retained_as_zero_across_unit_columns(self) -> None:
        dataset = pd.read_csv(DATASET_PATH)
        selected = dataset[
            (dataset["source_key"] == "Jakobsen2005")
            & (dataset["temperature_C"] == 20.0)
            & (dataset["mea_mass_fraction"] == 0.3)
            & (dataset["co2_loading_mol_per_mol_mea"] == 0.11)
            & (dataset["species"] == "HCO3-")
        ]
        self.assertEqual(len(selected), 1)
        row = selected.iloc[0]
        self.assertEqual(row["measurement_role"], "direct_zero")
        self.assertEqual(float(row["reported_value"]), 0.0)
        self.assertEqual(float(row["value_mole_fraction"]), 0.0)
        self.assertEqual(float(row["value_mol_per_kg_unloaded_solution"]), 0.0)


if __name__ == "__main__":
    unittest.main()
