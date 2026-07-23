from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def test_volumetric_evidence_package_is_scientifically_consistent() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/validate_volumetric_evidence.py"],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
