from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
RUFF = str(Path(PY).with_name("ruff"))

QUICK_COMMANDS = [
    [RUFF, "check", "src", "scripts", "analyses", "tests"],
    [PY, "scripts/doctor.py"],
    [PY, "scripts/check_no_local_paths.py"],
    [PY, "scripts/validate_mea_data_library.py"],
    [PY, "-m", "compileall", "-x", r"results[\\/]+runs", "src", "tests", "scripts", "analyses"],
    [PY, "-m", "pytest", "-q"],
]

PLOT_COMMANDS = [
    [PY, "scripts/render_all_plots.py"],
]


def plot_bundle(stem: str) -> list[str]:
    return [f"{stem}.mpl.yaml", f"{stem}.png", f"{stem}.svg", f"{stem}.pdf"]


CURATED_REQUIREMENTS = {
    "analyses/phase1/six_species_baseline/results/pressure": [
        "legacy_pcsaft_jou_fit_curves.csv",
        *plot_bundle("legacy_pcsaft_jou_recomputed_fit"),
    ],
    "analyses/phase1/six_species_baseline/results/speciation": [
        "speciation_plot_data.csv",
        *plot_bundle("speciation"),
    ],
    "analyses/phase1/neutral_epcsaft_parity/results/pressure": [
        "epcsaft_neutral_jou_parity_curves.csv",
        *plot_bundle("epcsaft_neutral_pcsaft_parity"),
    ],
    "analyses/phase3/ionic_epcsaft_regression/results/pressure": [
        "ionic_pressure_comparison.csv",
        *plot_bundle("ionic_epcsaft_co2_pressure"),
        "ionic_pressure_residuals_by_loading.csv",
        *plot_bundle("ionic_pressure_residuals_by_loading"),
    ],
    "analyses/phase3/ionic_epcsaft_regression/results/speciation": [
        "ionic_speciation_activity_residuals.csv",
        "ionic_speciation_plot_data.csv",
        *plot_bundle("ionic_epcsaft_speciation_activity"),
        "ionic_speciation_residuals_by_species.csv",
        *plot_bundle("ionic_speciation_residuals_by_species"),
    ],
    "analyses/phase3/ionic_epcsaft_regression/results/global_regression": [
        "global_regression_summary.json",
        "global_regression_values.csv",
        "global_regression_pressure_fit_data.csv",
        "global_regression_speciation_fit_data.csv",
        "global_regression_pressure_residuals.csv",
        "global_regression_speciation_residuals.csv",
        *plot_bundle("global_regression_pressure_parity"),
        *plot_bundle("global_regression_speciation_parity"),
    ],
    "analyses/phase3/ionic_epcsaft_regression/results/sensitivity": [
        "parameter_sensitivity_summary.json",
        "parameter_sensitivity_matrix.csv",
        "parameter_identifiability.csv",
        *plot_bundle("parameter_sensitivity_heatmap"),
    ],
    "analyses/paper_validation/2015_baygi/results/neutral_parity": [
        "baygi_neutral_epcsaft_pcsaft_pressure_parity_plot_data.csv",
        *plot_bundle("baygi_neutral_epcsaft_pcsaft_pressure_parity"),
    ],
    "analyses/phase1/smith_missen_baseline/results": [
        "phase1_pressure_results.csv",
        "phase1_pressure_metrics.csv",
        "phase1_speciation_results.csv",
        "phase1_speciation_metrics.csv",
        "phase1_speciation_curve.csv",
        "phase1_speciation_reference_points.csv",
        "phase1_parameter_table.csv",
        "phase1_reaction_constant_table.csv",
        "phase1_residual_acceptance_audit.csv",
        "phase1_model_lineage.md",
        "phase1_claim_boundary.md",
    ],
    "analyses/phase1/smith_missen_baseline/figures/pressure/input": ["source_manifest.csv"],
    "analyses/phase1/smith_missen_baseline/figures/pressure/output": [
        "phase1_pressure_plot_data.csv",
        *plot_bundle("phase1_pressure_vs_loading"),
    ],
    "analyses/phase1/smith_missen_baseline/figures/speciation/input": ["source_manifest.csv"],
    "analyses/phase1/smith_missen_baseline/figures/speciation/output": [
        *plot_bundle("phase1_speciation_20C"),
        "phase1_speciation_20C_plot_data.csv",
        *plot_bundle("phase1_speciation_40C"),
        "phase1_speciation_40C_plot_data.csv",
    ],
    "analyses/phase2/activity_epcsaft/results": [
        "phase2_activity_speciation_problem.json",
        "phase2_solver_claim_boundary_report.md",
        "phase2_required_output_status.csv",
        "phase2_speciation_reference_points.csv",
        "phase2_speciation_target_roles.csv",
        "phase2_equilibrium_results.csv",
        "phase2_pressure_results.csv",
        "phase2_pressure_speciation_parity.csv",
        "phase2_pressure_metrics.csv",
        "phase2_speciation_metrics.csv",
        "phase2_solver_diagnostics.csv",
        "phase2_residual_acceptance_audit.csv",
        "phase2_speciation_activity_curves.csv",
    ],
    "analyses/phase2/activity_epcsaft/figures/pressure/output": [
        "phase2_pressure_plot_data.csv",
        *plot_bundle("phase2_pressure_vs_loading"),
    ],
    "analyses/phase2/activity_epcsaft/figures/controlled_comparison/input": [
        "source_manifest.csv",
    ],
    "analyses/phase2/activity_epcsaft/figures/controlled_comparison/output": [
        "controlled_pressure_comparison_plot_data.csv",
        *plot_bundle("controlled_pressure_comparison"),
    ],
    "analyses/phase2/activity_epcsaft/figures/speciation/input": ["source_manifest.csv"],
    "analyses/phase2/activity_epcsaft/figures/speciation/output": [
        *plot_bundle("phase2_speciation_20C"),
        "phase2_speciation_20C_plot_data.csv",
        *plot_bundle("phase2_speciation_40C"),
        "phase2_speciation_40C_plot_data.csv",
        *plot_bundle("phase2_speciation_60C"),
        "phase2_speciation_60C_plot_data.csv",
        *plot_bundle("phase2_speciation_80C"),
        "phase2_speciation_80C_plot_data.csv",
        "phase2_speciation_figure_family.mpl.yaml",
    ],
    "analyses/phase2/canonical_speciation_sources/figures/speciation/input": ["source_manifest.csv"],
    "analyses/phase2/canonical_speciation_sources/figures/speciation/output": [
        "canonical_speciation_mole_fraction_grid_plot_data.csv",
        *plot_bundle("canonical_speciation_mole_fraction_grid"),
        "canonical_speciation_loaded_molkg_grid_plot_data.csv",
        *plot_bundle("canonical_speciation_loaded_molkg_grid"),
        "canonical_speciation_wong_source_molkg_plot_data.csv",
        *plot_bundle("canonical_speciation_wong_source_molkg"),
        "canonical_speciation_source_summary.csv",
    ],
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
