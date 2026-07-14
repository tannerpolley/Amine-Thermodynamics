from __future__ import annotations

import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_ROOT = ROOT / "data" / "reference" / "MEA" / "manifests"


def _rows(name: str) -> list[dict[str, str]]:
    with (MANIFEST_ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class ReferenceSourceManifestTests(unittest.TestCase):
    def test_search_log_has_frozen_schema_and_unique_keys(self) -> None:
        rows = _rows("source_search_log.csv")
        expected = {
            "search_id",
            "parameter_family",
            "observable",
            "query_or_source",
            "database_or_repository",
            "searched_at",
            "access_status",
            "primary_source_status",
            "si_status",
            "extraction_decision",
            "target_path",
            "notes",
        }
        self.assertTrue(rows)
        self.assertEqual(set(rows[0]), expected)
        self.assertEqual(len({row["search_id"] for row in rows}), len(rows))
        self.assertTrue(all(row["parameter_family"] and row["extraction_decision"] for row in rows))

    def test_every_pending_extraction_target_has_search_decision(self) -> None:
        pending = {
            "source_pending",
            "source_lead_only",
            "external_source_pending",
            "external_fulltext_required",
            "metadata_resolution_required",
        }
        targets = [row for row in _rows("extraction_target_manifest.csv") if row["status"] in pending]
        search_targets = {row["target_path"] for row in _rows("source_search_log.csv")}

        self.assertTrue(targets)
        for row in targets:
            with self.subTest(target_id=row["target_id"]):
                self.assertTrue(row["target_path"])
                self.assertIn(row["target_path"], search_targets)

    def test_approved_leads_are_recorded(self) -> None:
        text = "\n".join(row["query_or_source"] for row in _rows("source_search_log.csv"))
        for lead in (
            "Cai 1996",
            "Park and Lee 1997",
            "Kim 2008",
            "Posey 1996",
            "Touhara 1982",
            "Jiru 2012",
            "Hartono 2014",
            "Hajj 2024",
            "Fan 2009",
            "Du Preez 2019",
            "Kim and Svendsen 2007",
            "Kim 2014",
            "Idris 2014",
        ):
            with self.subTest(lead=lead):
                self.assertIn(lead, text)

    def test_metadata_only_sources_cannot_admit_numeric_extraction(self) -> None:
        allowed_without_verified_full_text = {
            "metadata_only_no_numeric_extraction",
            "fulltext_review_pending",
            "lead_identity_resolution_pending",
            "negative_search_no_extraction",
            "screened_out_no_extraction",
            "local_completion_review_pending",
        }
        for row in _rows("source_search_log.csv"):
            if row["primary_source_status"] != "full_text_verified":
                with self.subTest(search_id=row["search_id"]):
                    self.assertIn(row["extraction_decision"], allowed_without_verified_full_text)

    def test_parameter_coverage_names_every_movable_family(self) -> None:
        rows = _rows("parameter_observable_coverage.csv")
        expected_fields = {
            "parameter_family",
            "direct_evidence",
            "indirect_evidence",
            "current_hole",
            "priority",
            "promotion_restriction",
            "owner",
        }
        expected_families = {
            "MEA_pure_and_association",
            "k_ij_MEA_H2O",
            "k_ij_CO2_MEA",
            "MEAH_MEACOO_segment_parameters",
            "Born_solvation_and_dielectric",
            "ion_interaction_parameters",
            "reaction_constants",
        }
        self.assertTrue(rows)
        self.assertEqual(set(rows[0]), expected_fields)
        self.assertEqual({row["parameter_family"] for row in rows}, expected_families)
        for row in rows:
            with self.subTest(parameter_family=row["parameter_family"]):
                self.assertTrue(all(row[field] for field in expected_fields))


if __name__ == "__main__":
    unittest.main()
