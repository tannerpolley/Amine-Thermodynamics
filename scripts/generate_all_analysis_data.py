from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAST_COMMANDS = [
    [sys.executable, "analyses/phase1/six_species_baseline/scripts/generate_data.py"],
    [sys.executable, "analyses/phase1/smith_missen_baseline/scripts/generate_data.py"],
    [sys.executable, "analyses/phase2/canonical_speciation_sources/scripts/generate_data.py"],
]


def run_commands(commands: list[list[str]]) -> int:
    status = 0
    for command in commands:
        print("\n$ " + " ".join(command), flush=True)
        status = max(status, subprocess.run(command, cwd=ROOT).returncode)
        if status:
            return status
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate analysis CSV/JSON data tables without rendering figures.")
    parser.parse_args()
    commands = list(FAST_COMMANDS)
    return run_commands(commands)


if __name__ == "__main__":
    raise SystemExit(main())
