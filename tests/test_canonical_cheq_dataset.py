from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "reference" / "MEA" / "ChEq" / "Canonical_Combined_ChEq.csv"
SCHEMA_PATH = ROOT / "data" / "reference" / "MEA" / "ChEq" / "Canonical_Combined_ChEq_schema.csv"
MEMBERSHIP_PATH = ROOT / "data" / "reference" / "MEA" / "manifests" / "speciation_target_membership.csv"
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

    def test_unit_columns_are_populated_only_when_basis_is_verified(self) -> None:
        dataset = pd.read_csv(DATASET_PATH, keep_default_na=False)
        legacy = dataset[dataset["reported_basis"] == "mole_fraction"]
        wong = dataset[dataset["source_key"] == "Wong2015"]

        self.assertEqual(set(legacy["source_key"]), {"Bottinger2008", "Jakobsen2005", "Matin2012"})
        self.assertTrue(legacy["value_mole_fraction"].notna().all())
        self.assertTrue(legacy["value_mol_per_kg_unloaded_solution"].notna().all())
        self.assertTrue(legacy["value_mol_per_kg_initial_water"].notna().all())
        self.assertTrue(legacy["value_mol_per_kg_loaded_solution"].notna().all())

        self.assertEqual(set(wong["reported_basis"]), {"mol_per_kg_source_basis"})
        self.assertTrue((wong["value_mol_per_kg_source_basis"] != "").all())
        self.assertTrue((wong["conversion_eligible"].astype(str).str.lower() == "false").all())
        for column in (
            "value_mole_fraction",
            "value_mol_per_kg_unloaded_solution",
            "value_mol_per_kg_initial_water",
            "value_mol_per_kg_loaded_solution",
            "conversion_total_moles_per_kg_unloaded_solution",
        ):
            self.assertTrue((wong[column] == "").all(), column)
        self.assertEqual(set(wong["conversion_basis"]), {"not_converted_unverified_source_kg_denominator"})

    def test_generator_reproduces_tracked_schema_and_row_shape(self) -> None:
        module = _load_generator()
        generated = module.build_dataset()
        tracked = pd.read_csv(DATASET_PATH)
        schema = pd.read_csv(SCHEMA_PATH)

        self.assertEqual(list(generated.columns), list(tracked.columns))
        self.assertEqual(len(generated), len(tracked))
        self.assertEqual(list(schema["column"]), list(tracked.columns))

    def test_generator_reproduces_tracked_outputs_byte_for_byte(self) -> None:
        module = _load_generator()
        dataset = module.build_dataset()
        schema = module.build_schema()
        membership = module.build_membership(dataset)
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            generated_dataset = root / DATASET_PATH.name
            generated_schema = root / SCHEMA_PATH.name
            generated_membership = root / MEMBERSHIP_PATH.name
            dataset.to_csv(generated_dataset, index=False, float_format="%.12g")
            schema.to_csv(generated_schema, index=False)
            membership.to_csv(generated_membership, index=False, float_format="%.12g")

            self.assertEqual(generated_dataset.read_bytes(), DATASET_PATH.read_bytes())
            self.assertEqual(generated_schema.read_bytes(), SCHEMA_PATH.read_bytes())
            self.assertEqual(generated_membership.read_bytes(), MEMBERSHIP_PATH.read_bytes())

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

    def test_membership_preserves_active_and_transferability_state_groups(self) -> None:
        membership = pd.read_csv(MEMBERSHIP_PATH, keep_default_na=False)
        legacy = membership[membership["source_key"] != "Wong2015"]
        active = legacy[legacy["target_membership"] == "active_v1"]
        reserved = legacy[legacy["target_membership"] == "transferability_candidate"]

        self.assertEqual(legacy["state_id"].nunique(), 111)
        self.assertEqual(active["state_id"].nunique(), 74)
        self.assertEqual(reserved["state_id"].nunique(), 37)
        self.assertEqual(
            reserved.groupby("source_key")["state_id"].nunique().to_dict(),
            {"Bottinger2008": 29, "Jakobsen2005": 8},
        )
        self.assertEqual((active["measurement_role"] == "balance_inferred").sum(), 358)
        self.assertFalse(
            ((membership["measurement_role"] == "balance_inferred") & (membership["target_eligible"] == "yes")).any()
        )

    def test_wong_membership_is_source_basis_only_and_fail_closed(self) -> None:
        membership = pd.read_csv(MEMBERSHIP_PATH, keep_default_na=False)
        wong = membership[membership["source_key"] == "Wong2015"]

        self.assertEqual(len(wong), 71)
        self.assertEqual(wong["row_status"].value_counts().to_dict(), {"extracted": 66, "ambiguous": 5})
        self.assertTrue((wong["conversion_eligible"].astype(str).str.lower() == "false").all())
        self.assertTrue((wong["target_eligible"] == "no").all())
        self.assertEqual(set(wong["target_membership"]), {"diagnostic_only_basis_unverified"})


if __name__ == "__main__":
    unittest.main()
