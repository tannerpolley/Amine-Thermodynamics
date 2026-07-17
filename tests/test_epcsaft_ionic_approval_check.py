from __future__ import annotations

import unittest

from MEA.epcsaft_ionic.approval_check import evaluate_global_regression_approval
from MEA.epcsaft_ionic.preregistration import canonical_sha256


def completed_summary() -> dict[str, object]:
    return {
        "completion_status": "completed",
        "selected_parameter_set": "global_regression",
        "optimizer": {
            "owner": "epcsaft",
            "native_function": "fit_reactive_electrolyte_parameters",
        },
        "native_regression_summary": {
            "fit_success": True,
            "failure_count": 0,
            "active_bounds": {
                "MEAH+__s": False,
                "MEACOO-__s": False,
                "HCO3-__d_born": False,
                "CO3^2-__d_born": False,
            },
            "by_target_type": {
                "partial_pressure": {"count": 10},
                "speciation": {"count": 10},
            },
        },
        "parameters_at_bounds": {
            "MEAH+__s": False,
            "MEACOO-__s": False,
            "HCO3-__d_born": False,
            "CO3^2-__d_born": False,
        },
        "baseline_pressure_metrics": {"median_abs_log10": 0.9},
        "pressure_metrics": {"median_abs_log10": 0.7},
        "speciation_metrics": {
            "MEAH+": {"median_abs_log10": 0.10},
            "MEACOO-": {"median_abs_log10": 0.08},
        },
        "fitted_values": {
            "MEAH+__s": 3.2,
            "MEACOO-__s": 3.3,
            "HCO3-__d_born": 3.0,
            "CO3^2-__d_born": 3.0,
        },
    }


class EpcsaftIonicApprovalCheckTests(unittest.TestCase):
    def test_rejects_package_fit_not_completed_curated_summary(self) -> None:
        summary = completed_summary()
        summary["completion_status"] = "package_fit_not_completed"
        summary["selected_parameter_set"] = "fixed_provisional_parameter_set"
        approval = evaluate_global_regression_approval(summary)
        self.assertFalse(approval["approved"])
        self.assertIn("completion_status_not_completed", approval["reasons"])
        self.assertIn("selected_parameter_set_not_global_regression", approval["reasons"])

    def test_rejects_missing_native_package_status_and_row_counts(self) -> None:
        summary = completed_summary()
        summary["native_regression_summary"] = {}
        approval = evaluate_global_regression_approval(summary)
        self.assertFalse(approval["approved"])
        self.assertIn("native_fit_success_not_true", approval["reasons"])
        self.assertIn("native_row_failure_count_missing", approval["reasons"])

    def test_rejects_active_bounds(self) -> None:
        summary = completed_summary()
        summary["parameters_at_bounds"] = {"MEAH+__s": True}
        approval = evaluate_global_regression_approval(summary)
        self.assertFalse(approval["approved"])
        self.assertIn("parameters_at_active_bounds", approval["reasons"])

    def test_rejects_trace_only_carbonate_movement(self) -> None:
        summary = completed_summary()
        summary["fitted_values"] = {
            "HCO3-__d_born": 6.80294,
            "CO3^2-__d_born": 2.99744,
        }
        summary["native_regression_summary"]["by_target_type"] = {"speciation": {"count": 10}}
        approval = evaluate_global_regression_approval(summary)
        self.assertFalse(approval["approved"])
        self.assertIn("carbonate_movement_without_coupled_pressure_speciation_evidence", approval["reasons"])

    def test_approves_completed_coupled_package_fit(self) -> None:
        summary = completed_summary()
        approval = evaluate_global_regression_approval(summary)
        self.assertTrue(approval["approved"])
        self.assertEqual(approval["decision"], "approve_global_regression_promotion")
        self.assertEqual(approval["candidate_sha256"], canonical_sha256(summary))

    def test_final_candidate_requires_matching_preregistration_hash(self) -> None:
        summary = completed_summary()
        contract = {
            "parameters": [{"name": name} for name in summary["fitted_values"]],
            "target_counts": {"pressure": 10, "speciation": 10},
            "objective": {
                "target_weights": {"pressure": 1.0, "speciation": 1.0},
                "regularization_scale": 0.003,
            },
        }
        contract_sha256 = canonical_sha256(contract)
        summary["preregistration_contract"] = contract
        summary["preregistration_sha256"] = contract_sha256
        summary["fit_parameters"] = list(summary["fitted_values"])
        summary["target_counts"] = contract["target_counts"]
        summary["objective_weights"] = {
            "pressure_weight": 1.0,
            "speciation_weight": 1.0,
            "regularization_scale": 0.003,
        }
        summary["wall_time_seconds"] = 10.0
        summary["wall_time_ceiling_seconds"] = 20.0

        missing = evaluate_global_regression_approval(summary, require_preregistration=True)
        mismatch = evaluate_global_regression_approval(
            summary,
            require_preregistration=True,
            expected_preregistration_sha256="0" * 64,
        )
        matching = evaluate_global_regression_approval(
            summary,
            require_preregistration=True,
            expected_preregistration_sha256=contract_sha256,
        )

        self.assertIn("validated_preregistration_hash_missing", missing["reasons"])
        self.assertIn("preregistration_hash_mismatch", mismatch["reasons"])
        self.assertTrue(matching["approved"])
        self.assertEqual(matching["preregistration_sha256"], contract_sha256)


if __name__ == "__main__":
    unittest.main()

