from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from MEA.common import data_access


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = ROOT / "data" / "reference" / "MEA"
GENERATOR = ROOT / "scripts" / "build_regression_readiness.py"
ADMISSION = REFERENCE_ROOT / "manifests" / "target_admission_manifest.csv"
SPLIT = REFERENCE_ROOT / "manifests" / "grouped_split_manifest.csv"
SUMMARY = (
    ROOT
    / "analyses"
    / "phase3"
    / "ionic_epcsaft_regression"
    / "results"
    / "readiness"
    / "regression_readiness_summary.json"
)


def _load_generator():
    spec = importlib.util.spec_from_file_location("build_regression_readiness", GENERATOR)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load generator: {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _capability_receipt() -> dict[str, object]:
    return {
        "package": {"version": "fixture"},
        "capabilities": {
            "regression": {
                "reactive_electrolyte_batch_context": {
                    "bounded_mixed_pressure_speciation_regression": {
                        "available": True,
                        "status": "production",
                        "supports_pressure_targets": True,
                        "supports_speciation_targets": True,
                        "supports_density_targets": True,
                        "supports_relative_permittivity_targets": True,
                        "supports_activity_targets": True,
                    }
                }
            }
        },
    }


class RegressionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_generator()

    def test_unsupported_and_unimplemented_families_fail_closed(self) -> None:
        bundle = self.module.build_regression_readiness(REFERENCE_ROOT, _capability_receipt())
        admission = {row["target_family"]: row for row in bundle.target_admission}

        self.assertEqual(admission["vle_pressure"]["admitted"], "yes")
        self.assertEqual(admission["speciation"]["admitted"], "yes")
        for family in ("density", "viscosity", "relative_permittivity", "loaded_ph", "ionic_activity", "calorimetry"):
            with self.subTest(family=family):
                self.assertEqual(admission[family]["admitted"], "no")
                self.assertTrue(admission[family]["admission_reason"])

    def test_grouped_split_has_no_curve_or_replicate_leakage(self) -> None:
        bundle = self.module.build_regression_readiness(REFERENCE_ROOT, _capability_receipt())
        self.assertEqual(bundle.leakage_findings, ())
        by_group: dict[tuple[str, str], set[str]] = {}
        for row in bundle.grouped_split:
            by_group.setdefault((row["target_family"], row["group_id"]), set()).add(row["split"])
        self.assertTrue(by_group)
        self.assertTrue(all(len(splits) == 1 for splits in by_group.values()))

        broken = [dict(row) for row in bundle.grouped_split]
        group = next(row["group_id"] for row in broken if row["target_family"] == "vle_pressure")
        members = [row for row in broken if row["target_family"] == "vle_pressure" and row["group_id"] == group]
        if len(members) < 2:
            self.skipTest("fixture has no multi-row VLE group")
        members[0]["split"] = "validation" if members[1]["split"] == "training" else "training"
        findings = self.module.find_split_leakage(broken)
        self.assertTrue(any(group in finding for finding in findings))

    def test_reserved_composition_transfer_groups_are_frozen(self) -> None:
        bundle = self.module.build_regression_readiness(REFERENCE_ROOT, _capability_receipt())
        reserved = [row for row in bundle.grouped_split if row["role"] == "reserved_validation"]
        self.assertTrue(any(row["target_family"] == "vle_pressure" and row["mea_mass_fraction"] != "0.3" for row in reserved))
        self.assertTrue(any(row["target_family"] == "speciation" and row["mea_mass_fraction"] == "0.15" for row in reserved))
        self.assertTrue(any(row["target_family"] == "speciation" and row["mea_mass_fraction"] == "0.2" for row in reserved))

    def test_source_hash_drift_is_explicit(self) -> None:
        bundle = self.module.build_regression_readiness(REFERENCE_ROOT, _capability_receipt())
        expected = dict(bundle.source_hashes)
        expected[next(iter(expected))] = "0" * 64
        findings = self.module.find_source_hash_drift(REFERENCE_ROOT, expected)
        self.assertTrue(findings)
        self.assertIn("source hash drift", findings[0])

    def test_runtime_verifies_every_readiness_source_hash(self) -> None:
        verified = data_access.verify_regression_readiness_sources()
        expected = json.loads(SUMMARY.read_text(encoding="utf-8"))["source_hashes"]

        self.assertEqual(verified, expected)

    def test_runtime_source_hash_verification_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source.csv"
            source.write_text("value\n1\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Regression readiness source hash drift"):
                data_access.verify_source_hashes({"source.csv": "0" * 64}, repo_root=root)

    def test_readiness_builder_validates_real_observation_contract(self) -> None:
        row_counts = self.module.validate_reference_observation_contract(REFERENCE_ROOT)

        self.assertEqual(
            row_counts,
            {"speciation": 571, "vle_pressure": 327, "loaded_property": 213, "loading_cross_method": 82},
        )

    def test_generator_reproduces_all_tracked_outputs_byte_for_byte(self) -> None:
        bundle = self.module.build_regression_readiness(REFERENCE_ROOT, self.module.public_capability_receipt())
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            admission = root / ADMISSION.name
            split = root / SPLIT.name
            summary = root / SUMMARY.name
            self.module.write_bundle(bundle, admission_path=admission, split_path=split, summary_path=summary)

            self.assertEqual(admission.read_bytes(), ADMISSION.read_bytes())
            self.assertEqual(split.read_bytes(), SPLIT.read_bytes())
            self.assertEqual(summary.read_bytes(), SUMMARY.read_bytes())
            self.assertEqual(
                hashlib.sha256(split.read_bytes()).hexdigest(),
                json.loads(summary.read_text(encoding="utf-8"))["split_hash"],
            )

    def test_tracked_summary_is_fail_closed_and_auditable(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(payload["leakage_findings"], [])
        self.assertEqual(payload["readiness_decision"], "preregistration_ready_upstream_execution_blocked")
        self.assertIn("upstream_admission", payload["blocking_conditions"])
        self.assertGreater(payload["role_counts"]["active_training"], 0)
        self.assertGreater(payload["role_counts"]["reserved_validation"], 0)


if __name__ == "__main__":
    unittest.main()
