from __future__ import annotations

import csv
import unittest
from pathlib import Path

from MEA.common import reference_observations
from MEA.common.reference_observations import (
    LIFECYCLE_STATUSES,
    MEASUREMENT_ROLES,
    validate_observation_records,
)


ROOT = Path(__file__).resolve().parents[1]


def valid_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "record_id": "fixture-001",
        "source_key": "Fixture2026",
        "source_file": "data/reference/MEA/fixture.csv",
        "source_locator": "Table 1, row 1",
        "data_family": "speciation",
        "observed_quantity": "liquid species composition",
        "species": "MEACOO-",
        "phase": "liquid",
        "value_reported": 0.1,
        "reported_unit": "mole_fraction",
        "reported_basis": "loaded_liquid_total_moles",
        "value_normalized": "",
        "normalization_method": "",
        "uncertainty_value": "",
        "uncertainty_type": "",
        "uncertainty_coverage": "not_reported",
        "measurement_role": "direct_positive",
        "lifecycle_status": "canonical_eligible",
        "replicate_group": "",
        "normalization_group": "",
        "exclusion_reason": "",
        "reviewer_decision": "accepted",
    }
    row.update(overrides)
    return row


class ReferenceObservationContractTests(unittest.TestCase):
    def test_normalized_value_requires_reported_value_and_basis(self) -> None:
        row = valid_row(value_normalized=0.1, value_reported="", reported_basis="")

        report = validate_observation_records([row], "speciation")

        self.assertFalse(report.ok)
        self.assertTrue(
            any("normalized value requires reported value and basis" in error for error in report.errors)
        )

    def test_normalized_value_requires_named_conversion(self) -> None:
        report = validate_observation_records(
            [valid_row(value_normalized=0.02, normalization_method="")],
            "speciation",
        )

        self.assertFalse(report.ok)
        self.assertTrue(any("normalization method" in error for error in report.errors))

    def test_reported_zero_is_not_missing(self) -> None:
        row = valid_row(value_reported=0.0, measurement_role="direct_zero")

        self.assertTrue(validate_observation_records([row], "speciation").ok)

    def test_uncertainty_value_requires_type(self) -> None:
        report = validate_observation_records(
            [valid_row(uncertainty_value=0.01, uncertainty_type="")],
            "speciation",
        )

        self.assertFalse(report.ok)
        self.assertTrue(any("uncertainty value requires uncertainty type" in error for error in report.errors))

    def test_missing_source_identity_and_invalid_enums_are_rejected(self) -> None:
        report = validate_observation_records(
            [valid_row(source_key="", measurement_role="measured", lifecycle_status="ready")],
            "speciation",
        )

        self.assertFalse(report.ok)
        self.assertTrue(any("source_key is required" in error for error in report.errors))
        self.assertTrue(any("invalid measurement_role" in error for error in report.errors))
        self.assertTrue(any("invalid lifecycle_status" in error for error in report.errors))

    def test_validator_does_not_mutate_input_and_reports_all_rows(self) -> None:
        rows = [valid_row(record_id=""), valid_row(source_locator="")]
        before = [dict(row) for row in rows]

        report = validate_observation_records(rows, "speciation")

        self.assertEqual(rows, before)
        self.assertEqual(report.row_count, 2)
        self.assertEqual(len(report.errors), 2)

    def test_contract_enums_and_manifest_are_frozen(self) -> None:
        self.assertIn("direct_zero", MEASUREMENT_ROLES)
        self.assertIn("balance_inferred", MEASUREMENT_ROLES)
        self.assertIn("analog", MEASUREMENT_ROLES)
        self.assertIn("validation_reserved", LIFECYCLE_STATUSES)
        contract = ROOT / "data" / "reference" / "MEA" / "manifests" / "observation_contract.csv"
        self.assertTrue(contract.is_file())
        text = contract.read_text(encoding="utf-8")
        for field in (
            "source_locator",
            "value_reported",
            "value_normalized",
            "uncertainty_type",
            "measurement_role",
            "lifecycle_status",
        ):
            self.assertIn(field, text)

    def test_real_reference_tables_adapt_to_the_common_observation_contract(self) -> None:
        cases = (
            (
                ROOT / "data/reference/MEA/ChEq/Canonical_Combined_ChEq.csv",
                "adapt_speciation_rows",
                "speciation",
                571,
            ),
            (
                ROOT / "data/reference/MEA/VLE/Canonical_VLE_Observations.csv",
                "adapt_vle_pressure_rows",
                "vle_pressure",
                327,
            ),
            (
                ROOT / "data/reference/MEA/density_viscosity/Amundsen_2009_density_viscosity.csv",
                "adapt_loaded_property_rows",
                "loaded_property",
                213,
            ),
            (
                ROOT / "data/reference/MEA/VLE/Wong_2015_high_pressure_loading.csv",
                "adapt_paired_loading_rows",
                "loading_cross_method",
                82,
            ),
        )
        for path, adapter_name, family, expected_count in cases:
            with self.subTest(path=path):
                with path.open(newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                adapter = getattr(reference_observations, adapter_name)
                adapted = adapter(rows, source_file=path.relative_to(ROOT).as_posix())
                report = validate_observation_records(adapted, family)

                self.assertTrue(report.ok, report.errors[:5])
                self.assertEqual(report.row_count, expected_count)

    def test_analysis_manifests_name_live_runtime_sources(self) -> None:
        manifests = [
            ROOT / "analyses" / "phase1" / "six_species_baseline" / "analysis.yaml",
            ROOT / "analyses" / "phase2" / "activity_epcsaft" / "analysis.yaml",
            ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression" / "analysis.yaml",
        ]
        for manifest in manifests:
            with self.subTest(manifest=manifest):
                text = manifest.read_text(encoding="utf-8")
                self.assertIn("data/reference/MEA/VLE/Combined_VLE.csv", text)
                self.assertIn("data/reference/MEA/ChEq/Combined_ChEq.csv", text)
                self.assertIn(
                    "data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv",
                    text,
                )
                self.assertNotIn("Canonical_Combined_VLE.csv", text)
                self.assertNotIn("reaction_equilibrium_catalog.csv", text)
                for line in text.splitlines():
                    if line.strip().startswith("- path: data/"):
                        self.assertTrue((ROOT / line.split(":", 1)[1].strip()).exists(), line)


if __name__ == "__main__":
    unittest.main()
