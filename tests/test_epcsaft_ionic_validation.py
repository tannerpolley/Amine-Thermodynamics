from __future__ import annotations

import copy
import math
import unittest

from MEA.epcsaft_ionic import native_regression, validation
from MEA.epcsaft_ionic.model import DEFAULT_INITIAL_GUESS
from MEA.epcsaft_ionic.preregistration import canonical_sha256


def candidate_fixture() -> tuple[dict[str, object], dict[str, object], tuple[str, ...]]:
    names = tuple(spec["name"] for spec in native_regression.build_parameter_specs())
    selected_values = dict(DEFAULT_INITIAL_GUESS)
    selected_values.update({name: float(index + 1) for index, name in enumerate(names)})
    summary: dict[str, object] = {
        "completion_status": "completed",
        "selected_parameter_set": "global_regression",
        "fit_parameters": list(names),
        "selected_values": selected_values,
        "preregistration_sha256": "a" * 64,
        "native_regression_summary": {"fit_success": True, "failure_count": 0},
    }
    approval = {
        "approved": True,
        "preregistration_sha256": "a" * 64,
        "candidate_sha256": canonical_sha256(summary),
    }
    return summary, approval, names


class ReservedValidationContractTests(unittest.TestCase):
    def test_candidate_requires_approved_immutable_preregistered_fit(self) -> None:
        summary, approval, names = candidate_fixture()
        candidate = validation.validate_candidate_summary(
            summary,
            approval=approval,
            preregistration_sha256="a" * 64,
            parameter_names=names,
        )
        self.assertEqual(candidate.sha256, canonical_sha256(summary))
        self.assertEqual(candidate.fit_parameter_names, names)
        self.assertEqual(set(candidate.values), set(DEFAULT_INITIAL_GUESS))

        cases = {
            "not_completed": ("summary", "completion_status", "package_fit_not_completed"),
            "wrong_parameter_order": ("summary", "fit_parameters", list(reversed(names))),
            "nonfinite_parameter": ("summary", "selected_values", {**summary["selected_values"], names[0]: math.nan}),
            "missing_fixed_parameter": (
                "summary",
                "selected_values",
                {key: value for key, value in summary["selected_values"].items() if key != "MEA__m"},
            ),
            "unapproved": ("approval", "approved", False),
            "candidate_hash_drift": ("approval", "candidate_sha256", "0" * 64),
            "preregistration_hash_drift": ("summary", "preregistration_sha256", "0" * 64),
        }
        for label, (owner, key, value) in cases.items():
            with self.subTest(label=label):
                changed_summary = copy.deepcopy(summary)
                changed_approval = copy.deepcopy(approval)
                target = changed_summary if owner == "summary" else changed_approval
                target[key] = value
                with self.assertRaises(validation.ValidationContractError):
                    validation.validate_candidate_summary(
                        changed_summary,
                        approval=changed_approval,
                        preregistration_sha256="a" * 64,
                        parameter_names=names,
                    )

    def test_reserved_contract_is_complete_and_group_disjoint(self) -> None:
        contract = validation.build_reserved_validation_contract()

        self.assertEqual(contract.target_counts, {"pressure": 167, "speciation": 53})
        self.assertEqual(len(contract.record_ids), 220)
        self.assertEqual(contract.target_role, "reserved_validation")
        self.assertEqual(set(contract.row_splits.values()), {"validation"})
        for family in ("pressure", "speciation"):
            self.assertTrue(contract.validation_groups[family])
            self.assertTrue(contract.training_groups[family])
            self.assertTrue(contract.validation_groups[family].isdisjoint(contract.training_groups[family]))

    def test_failure_accounting_cannot_drop_or_hide_reserved_states(self) -> None:
        contract = validation.ReservedValidationContract.for_testing(
            rows=(
                {"record_id": "pressure-1", "target_family": "pressure", "source": "A", "target_count": 1},
                {"record_id": "speciation-1", "target_family": "speciation", "source": "B", "target_count": 2},
            )
        )
        records = [
            {
                "record_id": "pressure-1",
                "target_family": "pressure",
                "source": "A",
                "split": "validation",
                "role": "reserved_validation",
                "status": "success",
                "failure_reason": "",
                "target_count": 1,
                "evaluated_target_count": 1,
                "failed_target_count": 0,
                "log10_residuals": [0.1],
            },
            {
                "record_id": "speciation-1",
                "target_family": "speciation",
                "source": "B",
                "split": "validation",
                "role": "reserved_validation",
                "status": "failed_prediction",
                "failure_reason": "solver_rejected",
                "target_count": 2,
                "evaluated_target_count": 0,
                "failed_target_count": 2,
                "log10_residuals": [],
            },
        ]

        summary, metrics = validation.summarize_validation_records(
            records,
            contract=contract,
            candidate_sha256="c" * 64,
            preregistration_sha256="a" * 64,
            expected_split_hash="test-split",
            source_hashes={"source.csv": "b" * 64},
        )

        self.assertEqual(summary["state_count"], 2)
        self.assertEqual(summary["failed_state_count"], 1)
        self.assertEqual(summary["target_observation_count"], 3)
        self.assertEqual(summary["failed_target_observation_count"], 2)
        self.assertEqual(sum(row["state_count"] for row in metrics), 2)
        self.assertEqual(sum(row["failed_state_count"] for row in metrics), 1)

        with self.assertRaisesRegex(validation.ValidationContractError, "missing reserved records"):
            validation.summarize_validation_records(
                records[:1],
                contract=contract,
                candidate_sha256="c" * 64,
                preregistration_sha256="a" * 64,
                expected_split_hash="test-split",
                source_hashes={"source.csv": "b" * 64},
            )

        with self.assertRaisesRegex(validation.ValidationContractError, "split hash"):
            validation.summarize_validation_records(
                records,
                contract=contract,
                candidate_sha256="c" * 64,
                preregistration_sha256="a" * 64,
                expected_split_hash="different-split",
                source_hashes={"source.csv": "b" * 64},
            )


if __name__ == "__main__":
    unittest.main()
