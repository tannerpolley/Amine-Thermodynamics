from __future__ import annotations

import tomllib
import unittest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectToolingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    def test_runtime_dependencies_are_minimal_and_reproducible(self) -> None:
        dependencies = {item.split("[", 1)[0].split(">", 1)[0].split("=", 1)[0] for item in self.pyproject["project"]["dependencies"]}
        self.assertEqual(dependencies, {"epcsaft", "matplotlib", "numpy", "pandas", "pcsaft", "scipy"})
        pcsaft_source = self.pyproject["tool"]["uv"]["sources"]["pcsaft"]
        self.assertEqual(pcsaft_source["git"], "https://github.com/tannerpolley/PC-SAFT.git")
        self.assertRegex(pcsaft_source["rev"], r"^[0-9a-f]{40}$")

    def test_ruff_targets_python_313_and_all_source_roots(self) -> None:
        ruff = self.pyproject["tool"]["ruff"]
        self.assertEqual(ruff["target-version"], "py313")
        self.assertEqual(set(ruff["src"]), {"src", "scripts", "analyses", "tests"})
        ignored = ruff["lint"]["per-file-ignores"]
        self.assertTrue(ignored)
        self.assertTrue(all(errors == ["E402"] for errors in ignored.values()))
        self.assertTrue(all("scripts/" in path and "*" not in path for path in ignored))

    def test_manuscript_build_inputs_and_ci_are_tracked(self) -> None:
        required = (
            ROOT / "scripts" / "build_manuscript.sh",
            ROOT / "scripts" / "check_manuscript_freshness.py",
            ROOT / ".github" / "workflows" / "validate.yml",
            ROOT / "docs" / "latex" / "manuscript_references.bib",
        )
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), path)

        main = (ROOT / "docs" / "latex" / "main.tex").read_text(encoding="utf-8")
        self.assertIn("manuscript_references", main)
        self.assertNotIn("bibliography{references,", main)

        build_script = (ROOT / "scripts" / "build_manuscript.sh").read_text(encoding="utf-8")
        self.assertIn("latexmk -g -pdf", build_script)
        self.assertIn("SOURCE_DATE_EPOCH", build_script)

        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        for command in (
            "uv sync --locked --group test",
            "uv run ruff check src scripts analyses tests",
            "uv run python scripts/validate_project.py quick",
            "uv run python scripts/check_epcsaft_integration.py --mode final",
            "bash scripts/build_manuscript.sh",
            "uv run python scripts/check_manuscript_freshness.py",
        ):
            self.assertIn(command, workflow)
        self.assertIn("manual final-release gate", workflow)

    def test_every_manuscript_citation_has_a_tracked_bibliography_entry(self) -> None:
        latex = ROOT / "docs" / "latex"
        tex = "\n".join(path.read_text(encoding="utf-8") for path in latex.rglob("*.tex") if "builds" not in path.parts)
        cited = {
            key.strip()
            for group in re.findall(r"\\cite[a-zA-Z]*\{([^}]+)\}", tex)
            for key in group.split(",")
        }
        bibliography = "\n".join(
            (latex / name).read_text(encoding="utf-8")
            for name in ("manuscript_references.bib", "project_sources.bib", "official_sources.bib")
        )
        available = set(re.findall(r"(?m)^@[^({]+[({]\s*([^,\s]+)", bibliography))
        self.assertEqual(cited - available, set())


if __name__ == "__main__":
    unittest.main()
