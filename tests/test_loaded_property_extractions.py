from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AMUNDSEN = (
    ROOT
    / "data"
    / "reference"
    / "MEA"
    / "density_viscosity"
    / "Amundsen_2009_density_viscosity.csv"
)
WONG = ROOT / "data" / "reference" / "MEA" / "VLE" / "Wong_2015_high_pressure_loading.csv"
GENERATOR = ROOT / "scripts" / "build_loaded_property_evidence.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("build_loaded_property_evidence", GENERATOR)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load generator: {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LoadedPropertyExtractionTests(unittest.TestCase):
    def test_amundsen_family_counts_and_roles(self) -> None:
        data = pd.read_csv(AMUNDSEN, keep_default_na=False)
        unloaded = data[data["co2_loading_mol_per_mol_mea"] == ""]
        loaded = data[data["co2_loading_mol_per_mol_mea"] != ""]

        self.assertEqual(len(data), 213)
        self.assertEqual(len(unloaded), 70)
        self.assertEqual(
            loaded.groupby("property").size().to_dict(),
            {"density": 68, "dynamic_viscosity": 75},
        )
        self.assertEqual(set(loaded.loc[loaded["property"] == "density", "lifecycle_status"]), {"property_target_candidate"})
        self.assertEqual(set(loaded.loc[loaded["property"] == "dynamic_viscosity", "lifecycle_status"]), {"validation_only"})

    def test_amundsen_table_boundaries_and_blank_cells(self) -> None:
        data = pd.read_csv(AMUNDSEN, keep_default_na=False)
        loaded = data[data["co2_loading_mol_per_mol_mea"] != ""]

        def value(table: str, temperature: int, loading: float) -> float:
            selected = loaded[
                (loaded["source_table_or_figure"] == table)
                & (loaded["temperature_C"] == temperature)
                & (loaded["co2_loading_mol_per_mol_mea"].astype(float) == loading)
            ]
            self.assertEqual(len(selected), 1, (table, temperature, loading))
            return float(selected.iloc[0]["value"])

        self.assertEqual(value("Table 2", 25, 0.1), 1.0188)
        self.assertEqual(value("Table 2", 80, 0.4), 1.0360)
        self.assertEqual(value("Table 3", 80, 0.4), 1.0660)
        self.assertEqual(value("Table 4", 80, 0.4), 1.0977)
        self.assertEqual(value("Table 6", 25, 0.1), 1.8)
        self.assertEqual(value("Table 6", 80, 0.5), 0.8)
        self.assertEqual(value("Table 7", 25, 0.1), 2.6)
        self.assertEqual(value("Table 8", 80, 0.5), 1.9)
        self.assertFalse(
            (
                (loaded["source_table_or_figure"] == "Table 2")
                & (loaded["temperature_C"] == 80)
                & (loaded["co2_loading_mol_per_mol_mea"].astype(float) == 0.5)
            ).any()
        )

    def test_amundsen_loaded_uncertainty_is_retained(self) -> None:
        data = pd.read_csv(AMUNDSEN, keep_default_na=False)
        loaded = data[data["co2_loading_mol_per_mol_mea"] != ""]
        density = loaded[loaded["property"] == "density"]
        viscosity = loaded[loaded["property"] == "dynamic_viscosity"]

        self.assertTrue((density["uncertainty_value"].astype(float) == 0.002).all())
        self.assertEqual(set(density["uncertainty_unit"]), {"g/cm^3"})
        self.assertTrue((viscosity["uncertainty_value"].astype(float) == 3.0).all())
        self.assertEqual(set(viscosity["uncertainty_unit"]), {"percent"})
        self.assertTrue((loaded["temperature_uncertainty_K"].astype(float) == 0.03).all())
        self.assertTrue((loaded["co2_loading_relative_uncertainty_percent"].astype(float) == 2.0).all())

    def test_wong_table_five_counts_boundaries_and_methods(self) -> None:
        data = pd.read_csv(WONG, keep_default_na=False)

        self.assertEqual(len(data), 41)
        self.assertEqual(data.groupby("temperature_K").size().to_dict(), {303.15: 13, 313.15: 15, 323.15: 13})
        self.assertEqual(float(data.iloc[0]["pressure_bar"]), 1.0)
        self.assertEqual(float(data.iloc[0]["calculated_loading"]), 0.170)
        self.assertEqual(float(data.iloc[0]["predicted_loading"]), 0.167)
        self.assertEqual(float(data.iloc[-1]["pressure_bar"]), 60.0)
        self.assertEqual(float(data.iloc[-1]["calculated_loading"]), 0.916)
        self.assertEqual(float(data.iloc[-1]["predicted_loading"]), 0.904)
        self.assertEqual(set(data["calculated_method"]), {"gas_phase_pressure_drop"})
        self.assertEqual(set(data["predicted_method"]), {"raman_carbon_species_sum"})
        self.assertTrue(
            np.allclose(data["mse"].astype(float), data["mse_x_1e3"].astype(float) * 1.0e-3)
        )

    def test_wong_one_bar_batches_are_not_capacity_points(self) -> None:
        data = pd.read_csv(WONG, keep_default_na=False)
        one_bar = data[data["pressure_bar"] == 1.0]

        self.assertEqual(len(one_bar), 15)
        self.assertEqual(set(one_bar["lifecycle_status"]), {"non_capacity_batch_observation"})
        self.assertTrue(one_bar["caveat"].str.contains("not maximum absorption capacity").all())

    def test_repo_local_table_parser_reproduces_both_outputs_byte_for_byte(self) -> None:
        module = _load_generator()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            amundsen = temporary_root / AMUNDSEN.name
            wong = temporary_root / WONG.name
            module.write_csv_rows(amundsen, module._amundsen_rows(), fieldnames=module.AMUNDSEN_FIELDS)
            module.write_csv_rows(wong, module._wong_rows(), fieldnames=module.WONG_FIELDS)

            self.assertEqual(amundsen.read_bytes(), AMUNDSEN.read_bytes())
            self.assertEqual(wong.read_bytes(), WONG.read_bytes())


if __name__ == "__main__":
    unittest.main()
