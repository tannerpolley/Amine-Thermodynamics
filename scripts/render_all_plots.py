from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "analyses/phase1/six_species_baseline/scripts/render_figures.py"],
    [sys.executable, "analyses/phase1/neutral_epcsaft_parity/scripts/render_figures.py"],
    [sys.executable, "analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py"],
    [sys.executable, "analyses/paper_validation/2015_baygi/scripts/render_figures.py"],
    [sys.executable, "analyses/phase1/smith_missen_baseline/scripts/render_figures.py"],
    [sys.executable, "analyses/phase2/activity_epcsaft/scripts/render_figures.py"],
    [sys.executable, "analyses/phase2/canonical_speciation_sources/scripts/render_figures.py"],
]


def main() -> int:
    status = 0
    for command in COMMANDS:
        print("\n$ " + " ".join(command))
        status = max(status, subprocess.run(command, cwd=ROOT).returncode)
        if status:
            return status
    return status


if __name__ == "__main__":
    raise SystemExit(main())
