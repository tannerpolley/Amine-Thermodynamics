from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_CLAIMS = (
    "phase 1 complete",
    "phase 1 is complete",
    "phase 2 complete",
    "phase 2 is complete",
    "final globally optimized",
    "final coupled regression",
    "predictive final parameter set",
    "newly regressed final parameter set",
    "publication-ready phase 2",
)
CLAIM_SCAN_TARGETS = (
    "docs/roadmaps",
    "docs/latex",
    "analyses/phase1/smith_missen_baseline",
    "analyses/phase2/activity_epcsaft",
)


class CompletionClaimGuardTests(unittest.TestCase):
    def test_tracked_artifacts_do_not_contain_local_user_paths(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/check_no_local_paths.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout)

    def test_phase1_phase2_docs_do_not_make_forbidden_completion_claims(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "--", *CLAIM_SCAN_TARGETS],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        offenders: list[str] = []
        for rel in result.stdout.splitlines():
            path = ROOT / rel
            if not path.exists():
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf", ".svg"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for phrase in FORBIDDEN_CLAIMS:
                if phrase in text:
                    offenders.append(f"{rel}: {phrase}")
        self.assertEqual(offenders, [], msg="\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
