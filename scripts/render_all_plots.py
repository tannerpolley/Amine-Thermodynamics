from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "analyses/six_species_legacy/scripts/render_figures.py"],
    [sys.executable, "analyses/epcsaft_neutral_parity/scripts/render_figures.py"],
    [sys.executable, "analyses/epcsaft_ionic_regression/scripts/render_figures.py"],
    [sys.executable, "analyses/2015_baygi/scripts/render_figures.py"],
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
