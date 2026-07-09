from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class ActivityReactionCatalogTests(unittest.TestCase):
    def test_runtime_activity_coefficients_equal_verified_manifest(self) -> None:
        from MEA.common.reaction_catalog import activity_coefficient_map, load_activity_reaction_catalog
        from MEA.epcsaft_ionic import model

        rows = load_activity_reaction_catalog()
        self.assertEqual([row.reaction_id for row in rows], ["R1", "R2", "R3", "R4", "R5"])
        self.assertEqual(
            activity_coefficient_map()["R4_MEACOO_hydrolysis"],
            (2.8898, -3635.09, 0.0, 0.0),
        )
        self.assertEqual(model.activity_coefficient_map(), activity_coefficient_map())

    def test_catalog_rejects_unverified_duplicate_rows(self) -> None:
        from MEA.common.reaction_catalog import load_activity_reaction_catalog

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.csv"
            path.write_text(
                "reaction_id,source_key,source_value_A,source_value_B,source_value_C,source_value_D,source_verified,source_status\n"
                "R1,source,1,2,3,4,no,unverified\n"
                "R1,source,1,2,3,4,no,unverified\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "verified unique R1-R5"):
                load_activity_reaction_catalog(path)

    def test_catalog_hash_is_stable_and_content_derived(self) -> None:
        from MEA.common.reaction_catalog import reaction_catalog_sha256

        first = reaction_catalog_sha256()
        second = reaction_catalog_sha256()
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
