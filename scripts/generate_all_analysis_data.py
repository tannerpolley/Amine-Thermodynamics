from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAST_COMMANDS = [
    [sys.executable, "analyses/six_species_legacy/scripts/generate_data.py"],
    [sys.executable, "analyses/epcsaft_neutral_parity/scripts/generate_data.py"],
    [sys.executable, "analyses/2015_baygi/scripts/generate_data.py"],
]
IONIC_FULL_COMMANDS = [
    [sys.executable, "analyses/epcsaft_ionic_regression/scripts/generate_data.py"],
]
EXPENSIVE_DIAGNOSTIC_COMMANDS = [
    [sys.executable, "analyses/epcsaft_ionic_regression/scripts/evaluate_train_validation_split.py"],
    [sys.executable, "analyses/epcsaft_ionic_regression/scripts/compute_parameter_sensitivity.py"],
    [sys.executable, "analyses/epcsaft_ionic_regression/scripts/fit_trace_carbonate_born.py"],
    [sys.executable, "analyses/epcsaft_ionic_regression/scripts/derive_oh_born_parameter.py"],
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
    parser.add_argument("--include-ionic-full", action="store_true", help="Regenerate full ionic pressure/speciation CSVs; this can take many minutes.")
    parser.add_argument("--include-expensive", action="store_true", help="Also regenerate slow ionic diagnostic CSV/JSON tables used by optional plots.")
    args = parser.parse_args()
    commands = list(FAST_COMMANDS)
    if args.include_ionic_full:
        commands.extend(IONIC_FULL_COMMANDS)
    if args.include_expensive:
        commands.extend(EXPENSIVE_DIAGNOSTIC_COMMANDS)
    return run_commands(commands)


if __name__ == "__main__":
    raise SystemExit(main())
