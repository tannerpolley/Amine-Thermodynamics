from __future__ import annotations

import json
import unittest

from MEA.common import data_access
from MEA.epcsaft_ionic import native_regression


class NativeRegressionProblemTests(unittest.TestCase):
    def test_native_problem_serializes_nine_species_rows(self) -> None:
        problem = native_regression.build_native_regression_problem(
            max_pressure_records=2,
            max_speciation_records=2,
        )
        payload = problem.to_dict()
        encoded = json.dumps(payload)
        decoded = json.loads(encoded)

        self.assertEqual(
            decoded["species"],
            ["CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"],
        )
        self.assertEqual(decoded["metadata"]["pressure_row_count"], 2)
        self.assertEqual(decoded["metadata"]["speciation_row_count"], 2)
        self.assertEqual(decoded["metadata"]["optimizer_owner"], "epcsaft")
        self.assertEqual(decoded["metadata"]["requested_optimizer_backend"], "native_ceres")
        self.assertEqual(
            decoded["metadata"]["requested_derivative_backend"],
            "production_autodiff_and_implicit",
        )
        self.assertFalse(decoded["metadata"]["execution_admitted"])
        self.assertEqual(decoded["metadata"]["execution_gate"], "issue_12_split_package_contract")
        self.assertEqual(len(decoded["rows"]), 4)
        self.assertEqual({row["split"] for row in decoded["rows"]}, {"training"})
        self.assertEqual(decoded["metadata"]["target_role"], "active_training")
        self.assertIn("advanced_born_user_options", decoded)
        self.assertIn("split_hash", decoded["metadata"])
        self.assertEqual(decoded["metadata"]["split_source"], "grouped_split_manifest.csv")

        pressure = next(row for row in decoded["rows"] if row["mode"] == "bubble")
        speciation = next(row for row in decoded["rows"] if row["mode"] == "speciation")
        for row in (pressure, speciation):
            self.assertIn("row_id", row)
            self.assertIn("source", row)
            self.assertIn("split", row)
            self.assertIn(row["split"], {"training", "validation"})
            self.assertIn("group_id", row["metadata"])
            self.assertIn("loading", row)
            self.assertEqual(set(row["initial_x"]), set(decoded["species"]))
            self.assertEqual(row["vapor_species"], ["CO2", "H2O", "MEA"])
            self.assertEqual(row["nonvolatile_species"], ["MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"])
            self.assertIn("carbon_total", row["apparent_totals"])
            self.assertIn("reactions", row)

        self.assertIn("target_partial_pressures", pressure)
        self.assertIn("CO2", pressure["target_partial_pressures"])
        self.assertIn("target_speciation", speciation)
        self.assertTrue(speciation["target_speciation"])
        self.assertTrue(all(value > 0.0 for value in speciation["target_speciation"].values()))
        self.assertTrue(
            all(speciation["target_roles"][species] == "direct_positive" for species in speciation["target_speciation"])
        )
        self.assertTrue(set(speciation["target_speciation"]).isdisjoint(speciation["zero_upper_bound_species"]))
        self.assertIn("aggregate_targets", speciation["metadata"])
        self.assertNotIn("MEA + MEAH+", speciation["target_speciation"])

    def test_parameter_specs_include_carbonate_born_window(self) -> None:
        problem = native_regression.build_native_regression_problem(
            max_pressure_records=1,
            max_speciation_records=1,
            include_carbonate_born=True,
        )
        specs = {spec["name"]: spec for spec in problem.to_dict()["parameter_specs"]}
        for name in (
            "MEAH+__s",
            "MEAH+__e",
            "MEAH+__d_born",
            "MEACOO-__s",
            "MEACOO-__e",
            "MEACOO-__d_born",
            "HCO3-__d_born",
            "CO3^2-__d_born",
            "k_ij__CO2__MEA",
            "k_ij__MEA__H2O",
            "k_ij__MEAH+__MEACOO-",
            "k_ij__MEAH+__HCO3-",
        ):
            self.assertIn(name, specs)
            self.assertLess(specs[name]["lower"], specs[name]["initial"])
            self.assertGreater(specs[name]["upper"], specs[name]["initial"])
            self.assertGreater(specs[name]["scale"], 0.0)

    def test_epcsaft_batch_can_be_constructed_without_optimizer(self) -> None:
        problem = native_regression.build_native_regression_problem(
            max_pressure_records=1,
            max_speciation_records=1,
        )
        batch = native_regression.to_epcsaft_batch(problem)
        self.assertEqual(batch.species, problem.species)
        self.assertEqual(len(batch.rows), 2)
        self.assertEqual(batch.rows[0].source, problem.rows[0]["source"])

    def test_validation_problem_uses_only_reserved_validation_rows(self) -> None:
        problem = native_regression.build_native_regression_problem(
            max_pressure_records=2,
            max_speciation_records=None,
            target_role="reserved_validation",
        )

        self.assertEqual({row["split"] for row in problem.rows}, {"validation"})
        self.assertEqual(problem.metadata["target_role"], "reserved_validation")
        self.assertTrue(any(row["metadata"]["mea_weight_fraction"] != 0.3 for row in problem.rows))
        self.assertEqual(problem.metadata["direct_targetless_speciation_row_count"], 1)
        self.assertGreater(problem.metadata["aggregate_target_row_count"], 0)
        self.assertGreater(problem.metadata["zero_bound_row_count"], 0)

    def test_execution_gate_fails_closed_before_upstream_fit(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "upstream execution is blocked"):
            data_access.require_regression_execution_admitted({"upstream_execution_admitted": False})

        data_access.require_regression_execution_admitted({"upstream_execution_admitted": True})

if __name__ == "__main__":
    unittest.main()
