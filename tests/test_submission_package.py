from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/submission/fluid_phase_equilibria/submission_metadata.yml"
REQUIRED_FIELDS = {
    "venue",
    "article_type",
    "submission_date",
    "authors",
    "corresponding_author",
    "affiliations",
    "orcid_policy",
    "funding",
    "acknowledgments",
    "competing_interest",
    "credit",
    "ai_disclosure",
    "license",
    "archive",
    "reviewer_preferences",
}


class SubmissionPackageMetadataTests(unittest.TestCase):
    def test_author_approved_fpe_ledger_is_complete_and_placeholder_free(self) -> None:
        payload = json.loads(LEDGER.read_text(encoding="utf-8"))

        self.assertEqual(set(payload), REQUIRED_FIELDS)
        self.assertEqual(payload["venue"], "Fluid Phase Equilibria")
        self.assertEqual(payload["article_type"], "Original Research Article")
        self.assertEqual(payload["submission_date"], "2026-07-24")
        self.assertEqual(len(payload["authors"]), 1)
        author = payload["authors"][0]
        self.assertEqual(author["full_name"], "Tanner W. Polley")
        self.assertEqual(author["orcid"], "0009-0008-5957-4152")
        self.assertTrue(author["corresponding"])
        self.assertEqual(author["email"], "tpolley3@byu.edu")
        self.assertEqual(payload["corresponding_author"]["email"], author["email"])
        self.assertEqual(payload["archive"]["provider"], "Zenodo")
        self.assertEqual(payload["license"]["software"], "MIT")
        self.assertEqual(payload["license"]["original_documentation_and_data"], "CC-BY-4.0")

        manuscript = (ROOT / "docs/latex/main.tex").read_text(encoding="utf-8-sig")
        declarations = (ROOT / "docs/latex/sections/data_code_availability.tex").read_text(encoding="utf-8-sig")
        normalized_declarations = " ".join(declarations.split())
        self.assertIn(r"\author[1]{Tanner W. Polley}[orcid=0009-0008-5957-4152]", manuscript)
        self.assertIn(r"\ead{tpolley3@byu.edu}", manuscript)
        self.assertIn("Department of Chemical Engineering, Brigham Young University", manuscript)
        self.assertIn(payload["funding"]["statement"], normalized_declarations)
        self.assertIn(payload["competing_interest"]["statement"], normalized_declarations)
        self.assertIn(payload["ai_disclosure"]["statement"], normalized_declarations)

        serialized = json.dumps(payload).lower()
        for placeholder in ("todo", "tbd", "placeholder", "example", "add before submission", "unknown"):
            self.assertNotIn(placeholder, serialized)


if __name__ == "__main__":
    unittest.main()
