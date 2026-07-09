from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from MEA.epcsaft_ionic import global_regression, regress_parameters


class FakeReactiveFitResult:
    def __init__(self) -> None:
        self.success = True
        self.message = "native smoke fit"
        self.iterations = 1
        self.parameter_map = {
            "MEAH+__s": 3.1,
            "MEAH+__e": 251.0,
            "MEAH+__d_born": 4.1,
            "MEACOO-__s": 3.2,
            "MEACOO-__e": 252.0,
            "MEACOO-__d_born": 4.2,
            "HCO3-__d_born": 6.2,
            "CO3^2-__d_born": 3.1,
            "k_ij__CO2__MEA": 0.01,
            "k_ij__MEA__H2O": -0.02,
            "k_ij__MEAH+__MEACOO-": 0.03,
            "k_ij__MEAH+__HCO3-": 0.04,
        }
        self.seed_map = dict(self.parameter_map)
        self.active_bounds = {key: False for key in self.parameter_map}
        self.lower_bounds = {key: 0.0 for key in self.parameter_map}
        self.upper_bounds = {key: 10.0 for key in self.parameter_map}
        self.identifiability_status = "smoke"
        self.diagnostics = {"test_double": True}

    def to_dict(self) -> dict[str, object]:
        return {
            "success": self.success,
            "message": self.message,
            "iterations": self.iterations,
            "parameter_map": self.parameter_map,
            "seed_map": self.seed_map,
            "active_bounds": self.active_bounds,
            "lower_bounds": self.lower_bounds,
            "upper_bounds": self.upper_bounds,
            "identifiability_status": self.identifiability_status,
            "diagnostics": self.diagnostics,
        }


class FakeEpcsaft:
    def __init__(self, result: FakeReactiveFitResult) -> None:
        self.result = result
        self.fit_reactive_electrolyte_parameters = Mock(return_value=result)

    def summarize_regression_result(self, result: FakeReactiveFitResult) -> dict[str, object]:
        return {
            "fit_success": result.success,
            "fit_message": result.message,
            "fit_iterations": result.iterations,
            "parameter_map": result.parameter_map,
            "seed_map": result.seed_map,
            "active_bounds": result.active_bounds,
            "identifiability_status": result.identifiability_status,
            "residual_norm": 1.25,
        }

    def write_regression_summary(self, result: FakeReactiveFitResult, path: str | Path) -> Path:
        target = Path(path)
        target.write_text('{"fit_success": true}\n', encoding="utf-8")
        return target

    def write_regression_row_table(self, result: FakeReactiveFitResult, path: str | Path) -> Path:
        target = Path(path)
        target.write_text("row_id,residual_norm\nrow-1,0.1\n", encoding="utf-8")
        return target

    def write_regression_residual_table(self, result: FakeReactiveFitResult, path: str | Path) -> Path:
        target = Path(path)
        target.write_text("residual,value\nr1,0.1\n", encoding="utf-8")
        return target

    def write_regression_parameter_table(self, result: FakeReactiveFitResult, path: str | Path) -> Path:
        target = Path(path)
        target.write_text("parameter,value\nMEAH+__s,3.1\n", encoding="utf-8")
        return target


class EpcsaftIonicArtifactPromotionTests(unittest.TestCase):
    def test_regression_entrypoint_delegates_to_native_epcsaft_fit(self) -> None:
        result = FakeReactiveFitResult()
        fake_epcsaft = FakeEpcsaft(result)
        args = SimpleNamespace(
            max_iterations=1,
            max_vle_records=1,
            max_speciation_records=1,
            exclude_carbonate_born=False,
            backend="ceres",
            derivative_backend="autodiff",
            tolerance=1.0e-6,
            damping=1.0,
            verbose=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            with (
                patch.object(regress_parameters, "OUT_DIR", output_dir),
                patch.object(regress_parameters, "FIT_DATASET_DIR", output_dir / "dataset"),
                patch.object(regress_parameters.native_regression, "to_epcsaft_batch", return_value="batch-sentinel"),
                patch.object(regress_parameters, "load_epcsaft", return_value=fake_epcsaft),
                patch.object(
                    regress_parameters,
                    "write_fitted_dataset",
                    return_value=[output_dir / "dataset" / "pure" / "any_solvent.csv"],
                ),
            ):
                summary = regress_parameters.run_regression(args)

                fake_epcsaft.fit_reactive_electrolyte_parameters.assert_called_once()
                _, kwargs = fake_epcsaft.fit_reactive_electrolyte_parameters.call_args
                self.assertEqual(kwargs["max_iterations"], 1)
                self.assertNotIn("optimizer_backend", kwargs)
                self.assertNotIn("derivative_backend", kwargs)
                self.assertNotIn("log_parameters", kwargs)
                self.assertNotIn("jacobian_mode", kwargs)
                self.assertNotIn("relative_step", kwargs)
                self.assertIn("HCO3-__d_born", kwargs["initial_parameters"])
                self.assertIn("CO3^2-__d_born", kwargs["initial_parameters"])
                self.assertEqual(summary["native_regression"]["owner"], "epcsaft")
                self.assertEqual(summary["native_regression"]["status"], "package_status_schema_unavailable")
                self.assertEqual(summary["fitted_values"]["HCO3-__d_born"], 6.2)
                for name in (
                    "native_regression_problem.json",
                    "native_regression_result.json",
                    "native_regression_summary.json",
                    "native_regression_parameters.csv",
                    "ionic_parameter_regression_summary.json",
                    "ionic_parameter_regression_values.csv",
                ):
                    self.assertTrue((output_dir / name).exists(), name)

    def test_production_regression_modules_do_not_import_or_call_scipy_optimizers(self) -> None:
        for module in (regress_parameters, global_regression):
            with self.subTest(module=module.__name__):
                source_path = Path(module.__file__)
                tree = ast.parse(source_path.read_text(encoding="utf-8-sig"))
                forbidden_imports: list[str] = []
                forbidden_calls: list[str] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module == "scipy.optimize":
                        forbidden_imports.extend(alias.name for alias in node.names)
                    if isinstance(node, ast.Call):
                        func = node.func
                        if isinstance(func, ast.Name) and func.id in {
                            "least_squares",
                            "minimize",
                            "differential_evolution",
                        }:
                            forbidden_calls.append(func.id)
                        if isinstance(func, ast.Attribute) and func.attr in {
                            "least_squares",
                            "minimize",
                            "differential_evolution",
                        }:
                            forbidden_calls.append(func.attr)
                self.assertEqual(forbidden_imports, [])
                self.assertEqual(forbidden_calls, [])


if __name__ == "__main__":
    unittest.main()

