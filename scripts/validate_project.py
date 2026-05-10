from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

QUICK_COMMANDS = [
    [PY, "scripts/doctor.py"],
    [PY, "-m", "compileall", "-x", r"results[\\/]+runs", "src", "tests", "scripts", "analyses"],
    [PY, "-m", "unittest", "discover", "tests", "-v"],
]

PLOT_COMMANDS = [
    [PY, "analyses/six_species_legacy/scripts/render_figures.py"],
    [PY, "analyses/epcsaft_neutral_parity/scripts/render_figures.py"],
    [PY, "analyses/epcsaft_ionic_regression/scripts/render_figures.py"],
    [PY, "analyses/2015_baygi/scripts/generate_data.py"],
    [PY, "analyses/2015_baygi/scripts/render_figures.py"],
]

CURATED_REQUIREMENTS = {
    "analyses/six_species_legacy/results/pressure": ["legacy_pcsaft_jou_fit_curves.csv", "legacy_pcsaft_jou_recomputed_fit.mpl.yaml", "legacy_pcsaft_jou_recomputed_fit.png", "legacy_pcsaft_jou_recomputed_fit.svg"],
    "analyses/six_species_legacy/results/speciation": ["speciation_plot_data.csv", "speciation.mpl.yaml", "speciation.png", "speciation.svg"],
    "analyses/epcsaft_neutral_parity/results/pressure": ["epcsaft_neutral_jou_parity_curves.csv", "epcsaft_neutral_pcsaft_parity.mpl.yaml", "epcsaft_neutral_pcsaft_parity.png", "epcsaft_neutral_pcsaft_parity.svg"],
    "analyses/epcsaft_ionic_regression/results/pressure": ["ionic_pressure_comparison.csv", "ionic_epcsaft_co2_pressure.mpl.yaml", "ionic_epcsaft_co2_pressure.png", "ionic_epcsaft_co2_pressure.svg"],
    "analyses/epcsaft_ionic_regression/results/speciation": ["ionic_speciation_activity_residuals.csv", "ionic_speciation_plot_data.csv", "ionic_epcsaft_speciation_activity.mpl.yaml", "ionic_epcsaft_speciation_activity.png", "ionic_epcsaft_speciation_activity.svg"],
    "analyses/epcsaft_ionic_regression/results/ion_parameter_regression": ["ion_parameter_fit_summary.json", "ion_parameter_fit_values.csv", "ion_parameter_fit_statistics.csv", "ion_parameter_speciation_fit_data.csv", "meah_meacoo_speciation_parity.mpl.yaml", "meah_meacoo_speciation_parity.png", "meah_meacoo_speciation_parity.svg", "meah_meacoo_loading_curves.mpl.yaml", "meah_meacoo_loading_curves.png", "meah_meacoo_loading_curves.svg"],
    "analyses/2015_baygi/results/neutral_parity": ["baygi_neutral_epcsaft_pcsaft_pressure_parity_plot_data.csv", "baygi_neutral_epcsaft_pcsaft_pressure_parity.mpl.yaml", "baygi_neutral_epcsaft_pcsaft_pressure_parity.png", "baygi_neutral_epcsaft_pcsaft_pressure_parity.svg"],
}


def run(command: list[str]) -> int:
    print("\n$ " + " ".join(command))
    return subprocess.run(command, cwd=ROOT).returncode


def verify_artifacts() -> int:
    missing: list[Path] = []
    for folder, names in CURATED_REQUIREMENTS.items():
        root = ROOT / folder
        for name in names:
            path = root / name
            if not path.exists():
                missing.append(path)
    if missing:
        print("Missing curated artifacts:")
        for path in missing:
            print(f"  {path}")
        return 1
    print("Curated artifact contract passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the MEA-Thermodynamics project layout and analysis artifacts.")
    parser.add_argument("mode", choices=["quick", "confidence"], help="quick runs structural/tests checks; confidence also regenerates curated plots")
    args = parser.parse_args()

    commands = list(QUICK_COMMANDS)
    if args.mode == "confidence":
        commands.extend(PLOT_COMMANDS)
    status = 0
    for command in commands:
        status = max(status, run(command))
        if status:
            return status
    if args.mode == "confidence":
        status = max(status, verify_artifacts())
    return status


if __name__ == "__main__":
    raise SystemExit(main())
