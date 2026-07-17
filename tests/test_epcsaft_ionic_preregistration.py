from __future__ import annotations

import copy
import unittest
from functools import lru_cache

from MEA.common.data_access import load_regression_readiness_summary
from MEA.epcsaft_ionic import native_regression, preregistration


def admitted_readiness() -> dict[str, object]:
    readiness = copy.deepcopy(load_regression_readiness_summary())
    readiness["upstream_execution_admitted"] = True
    return readiness


@lru_cache(maxsize=1)
def _valid_payload_template() -> dict[str, object]:
    readiness = admitted_readiness()
    problem = native_regression.build_native_regression_problem()
    return {
        "schema_version": 1,
        "created_date": "2026-07-18",
        "readiness": {
            "summary_sha256": preregistration.canonical_sha256(readiness),
            "split_hash": readiness["split_hash"],
            "source_hashes": readiness["source_hashes"],
            "role_counts": readiness["role_counts"],
        },
        "target_role": "active_training",
        "target_counts": {
            "pressure": problem.metadata["pressure_row_count"],
            "speciation": problem.metadata["speciation_row_count"],
        },
        "parameters": list(problem.parameter_specs),
        "objective": {
            "definition": "family_normalized_log10_residuals_plus_scaled_regularization",
            "target_weights": {"pressure": 1.0, "speciation": 1.0},
            "regularization_scale": 0.003,
        },
        "solver": {
            "owner": "epcsaft",
            "native_function": "fit_reactive_electrolyte_parameters",
            "backend": "native_ceres",
            "derivative_backend": "production_autodiff_and_implicit",
            "max_iterations": 20,
            "wall_time_ceiling_seconds": 7200,
        },
        "upstream": {
            "execution_admitted": True,
            "capability_receipt_hash": readiness["capability_receipt_hash"],
        },
        "policies": {
            "zero_bounds": "preserve_membership_manifest_upper_bounds",
            "aggregate_targets": "membership_approved_targets_only",
            "row_failures": "count_as_failed_prediction_no_omission",
            "active_bounds": "reject_any_active_bound",
            "promotion": "atomic_all_gates_required",
        },
        "gates": {
            "pressure_median_abs_log10_max_baseline_ratio": 1.0,
            "major_speciation_median_abs_log10_max": {"MEAH+": 0.15, "MEACOO-": 0.10},
            "minimum_moved_parameter_count": 3,
            "required_diagnostics": ["fit_success", "failure_count", "active_bounds", "by_target_type"],
            "plausibility": "all_preregistered_parameter_and_phase_checks",
        },
        "command": {
            "entrypoint": "analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py",
            "arguments": [
                "--preregistration",
                "analyses/phase3/ionic_epcsaft_regression/config/final_fit_preregistration.json",
                "--output-label",
                "final_candidate",
                "--promote",
            ],
        },
    }


def valid_payload() -> dict[str, object]:
    return copy.deepcopy(_valid_payload_template())


class FinalFitPreregistrationTests(unittest.TestCase):
    def test_valid_contract_is_deterministic_and_training_only(self) -> None:
        payload = valid_payload()
        first = preregistration.validate_preregistration(payload, readiness=admitted_readiness())
        second = preregistration.validate_preregistration(copy.deepcopy(payload), readiness=admitted_readiness())

        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.target_role, "active_training")
        self.assertEqual(first.target_counts, {"pressure": 89, "speciation": 58})
        self.assertEqual(first.max_iterations, 20)

    def test_readiness_parameter_and_policy_drift_fail_closed(self) -> None:
        cases: dict[str, tuple[tuple[str, ...], object]] = {
            "split": (("readiness", "split_hash"), "0" * 64),
            "source": (("readiness", "source_hashes"), {"changed.csv": "0" * 64}),
            "order": (("parameters",), list(reversed(valid_payload()["parameters"]))),
            "validation": (("target_role",), "reserved_validation"),
            "zero_policy": (("policies", "zero_bounds"), None),
            "diagnostics": (("gates", "required_diagnostics"), ["fit_success"]),
            "threshold": (("gates", "major_speciation_median_abs_log10_max", "MEAH+"), 0.16),
        }
        for label, (path, replacement) in cases.items():
            with self.subTest(label=label):
                payload = valid_payload()
                cursor = payload
                for key in path[:-1]:
                    cursor = cursor[key]  # type: ignore[index]
                cursor[path[-1]] = replacement  # type: ignore[index]
                with self.assertRaises(preregistration.PreregistrationError):
                    preregistration.validate_preregistration(payload, readiness=admitted_readiness())

    def test_current_nonadmitted_readiness_cannot_authorize_execution(self) -> None:
        payload = valid_payload()
        current = load_regression_readiness_summary()
        payload["readiness"]["summary_sha256"] = preregistration.canonical_sha256(current)  # type: ignore[index]
        payload["upstream"]["execution_admitted"] = False  # type: ignore[index]

        with self.assertRaisesRegex(preregistration.PreregistrationError, "upstream execution is not admitted"):
            preregistration.validate_preregistration(payload, readiness=current)


if __name__ == "__main__":
    unittest.main()
