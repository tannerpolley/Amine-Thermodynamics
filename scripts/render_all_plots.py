from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "analyses/six_species_solubility_reference/scripts/render_figures.py"],
    [sys.executable, "analyses/reactive_epcsaft_parameter_evidence/scripts/render_figures.py"],
    [sys.executable, "analyses/paper_validation/2015_baygi/scripts/render_figures.py"],
    [sys.executable, "analyses/ideal_reaction_equilibrium/scripts/render_figures.py"],
    [sys.executable, "analyses/speciation_evidence_harmonization/scripts/render_figures.py"],
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
