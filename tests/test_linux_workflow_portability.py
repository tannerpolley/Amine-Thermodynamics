from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DOCS = (
    ROOT / "README.md",
    *sorted((ROOT / "analyses").glob("**/README.md")),
    *sorted((ROOT / "docs" / "ePC-SAFT").glob("*.md")),
    *sorted((ROOT / "docs" / "coordination").glob("*.md")),
    *sorted((ROOT / "docs" / "superpowers").glob("**/*.md")),
)
WINDOWS_WORKFLOW_TOKENS = ("powershell", ".ps1", "cmd.exe", ".bat", ".cmd")


class LinuxWorkflowPortabilityTests(unittest.TestCase):
    def test_tracked_workflow_documents_do_not_advertise_windows_commands(self) -> None:
        offenders: list[str] = []
        for path in WORKFLOW_DOCS:
            text = path.read_text(encoding="utf-8").lower()
            for token in WINDOWS_WORKFLOW_TOKENS:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)}: {token}")
        self.assertEqual(offenders, [])

    def test_manuscript_sync_is_a_bash_entrypoint(self) -> None:
        sync_script = ROOT / "docs" / "latex" / "scripts" / "sync_to_overleaf_mirror.sh"
        self.assertTrue(sync_script.exists())
        self.assertFalse((ROOT / "docs" / "latex" / "sync_to_overleaf_mirror.ps1").exists())
        self.assertTrue(sync_script.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash\n"))


if __name__ == "__main__":
    unittest.main()
