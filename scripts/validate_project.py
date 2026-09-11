from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
RUFF = str(Path(PY).with_name("ruff"))
MAX_TRACKED_JSON_BYTES = 100 * 1024
MAX_TRACKED_JSON_LINES = 3_000
MAX_TRACKED_TEXT_BYTES = 1024 * 1024
MAX_TRACKED_FILE_BYTES = 5 * 1024 * 1024
TEXT_SUFFIXES = {".bib", ".csv", ".md", ".py", ".svg", ".tex", ".toml", ".tsv", ".txt", ".yaml", ".yml"}

QUICK_COMMANDS = [
    [RUFF, "check", "src", "scripts", "analyses", "tests"],
    [PY, "scripts/doctor.py"],
    [PY, "scripts/check_no_local_paths.py"],
    [PY, "scripts/validate_mea_data_library.py"],
    [PY, "-m", "compileall", "-x", r"results[\\/]+runs", "src", "tests", "scripts", "analyses"],
    [PY, "-m", "pytest", "-q", "--ignore=upstream"],
]

PLOT_COMMANDS = [
    [PY, "scripts/render_all_plots.py"],
]


def plot_bundle(stem: str) -> list[str]:
    return [f"{stem}.mpl.yaml", f"{stem}.png", f"{stem}.svg", f"{stem}.pdf"]


CURATED_REQUIREMENTS = {
    "analyses/six_species_solubility_reference/results/pressure": [
        "legacy_pcsaft_jou_fit_curves.csv",
        *plot_bundle("legacy_pcsaft_jou_recomputed_fit"),
    ],
    "analyses/six_species_solubility_reference/results/speciation": [
        "speciation_plot_data.csv",
        *plot_bundle("speciation"),
    ],
    "analyses/paper_validation/2015_baygi/results/neutral_parity": [
        "baygi_neutral_epcsaft_pcsaft_pressure_parity_plot_data.csv",
        *plot_bundle("baygi_neutral_epcsaft_pcsaft_pressure_parity"),
    ],
    "analyses/ideal_reaction_equilibrium/results": [
        "ideal_reference_pressure_results.csv",
        "ideal_reference_pressure_metrics.csv",
        "ideal_reference_speciation_results.csv",
        "ideal_reference_speciation_metrics.csv",
        "ideal_reference_speciation_curve.csv",
        "ideal_reference_speciation_reference_points.csv",
        "ideal_reference_parameter_table.csv",
        "ideal_reference_reaction_constant_table.csv",
        "ideal_reference_residual_acceptance_audit.csv",
        "ideal_reference_model_lineage.md",
        "ideal_reference_claim_boundary.md",
    ],
    "analyses/ideal_reaction_equilibrium/figures/pressure/input": ["source_manifest.csv"],
    "analyses/ideal_reaction_equilibrium/figures/pressure/output": [
        "ideal_reference_pressure_plot_data.csv",
        *plot_bundle("ideal_reference_pressure_vs_loading"),
    ],
    "analyses/ideal_reaction_equilibrium/figures/speciation/input": ["source_manifest.csv"],
    "analyses/ideal_reaction_equilibrium/figures/speciation/output": [
        *plot_bundle("ideal_reference_speciation_20C"),
        "ideal_reference_speciation_20C_plot_data.csv",
        *plot_bundle("ideal_reference_speciation_40C"),
        "ideal_reference_speciation_40C_plot_data.csv",
    ],
    "analyses/historical_fixed_parameter_epcsaft_evaluation/results": [
        "historical_activity_evaluation_activity_speciation_problem.json",
        "historical_activity_evaluation_solver_claim_boundary_report.md",
        "historical_activity_evaluation_required_output_status.csv",
        "historical_activity_evaluation_speciation_reference_points.csv",
        "historical_activity_evaluation_speciation_target_roles.csv",
        "historical_activity_evaluation_equilibrium_results.csv",
        "historical_activity_evaluation_pressure_results.csv",
        "historical_activity_evaluation_pressure_speciation_parity.csv",
        "historical_activity_evaluation_pressure_metrics.csv",
        "historical_activity_evaluation_speciation_metrics.csv",
        "historical_activity_evaluation_solver_diagnostics.csv",
        "historical_activity_evaluation_residual_acceptance_audit.csv",
        "historical_activity_evaluation_speciation_activity_curves.csv",
    ],
    "analyses/historical_fixed_parameter_epcsaft_evaluation/figures/pressure/output": [
        "historical_activity_evaluation_pressure_plot_data.csv",
        *plot_bundle("historical_activity_evaluation_pressure_vs_loading"),
    ],
    "analyses/historical_fixed_parameter_epcsaft_evaluation/figures/controlled_comparison/input": [
        "source_manifest.csv",
    ],
    "analyses/historical_fixed_parameter_epcsaft_evaluation/figures/controlled_comparison/output": [
        "controlled_pressure_comparison_plot_data.csv",
        *plot_bundle("controlled_pressure_comparison"),
    ],
    "analyses/historical_fixed_parameter_epcsaft_evaluation/figures/speciation/input": ["source_manifest.csv"],
    "analyses/historical_fixed_parameter_epcsaft_evaluation/figures/speciation/output": [
        *plot_bundle("historical_activity_evaluation_speciation_20C"),
        "historical_activity_evaluation_speciation_20C_plot_data.csv",
        *plot_bundle("historical_activity_evaluation_speciation_40C"),
        "historical_activity_evaluation_speciation_40C_plot_data.csv",
        *plot_bundle("historical_activity_evaluation_speciation_60C"),
        "historical_activity_evaluation_speciation_60C_plot_data.csv",
        *plot_bundle("historical_activity_evaluation_speciation_80C"),
        "historical_activity_evaluation_speciation_80C_plot_data.csv",
        "historical_activity_evaluation_speciation_figure_family.mpl.yaml",
    ],
    "analyses/speciation_evidence_harmonization/figures/speciation/input": ["source_manifest.csv"],
    "analyses/speciation_evidence_harmonization/figures/speciation/output": [
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


def tracked_size_problem(path: Path) -> str | None:
    byte_count = path.stat().st_size
    if path.suffix == ".json" and byte_count > MAX_TRACKED_JSON_BYTES:
        return f"{byte_count} bytes > {MAX_TRACKED_JSON_BYTES}"
    if path.suffix == ".json":
        with path.open("rb") as stream:
            line_count = sum(1 for _ in stream)
        if line_count > MAX_TRACKED_JSON_LINES:
            return f"{line_count} lines > {MAX_TRACKED_JSON_LINES}"
    if path.suffix.lower() in TEXT_SUFFIXES and byte_count > MAX_TRACKED_TEXT_BYTES:
        return f"{byte_count} bytes > {MAX_TRACKED_TEXT_BYTES}"
    if byte_count > MAX_TRACKED_FILE_BYTES:
        return f"{byte_count} bytes > {MAX_TRACKED_FILE_BYTES}"
    return None


def verify_tracked_file_size() -> int:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\0")
    oversized: list[str] = []
    for relative in filter(None, tracked):
        path = ROOT / relative
        if not path.is_file():
            continue
        if problem := tracked_size_problem(path):
            oversized.append(f"{relative}: {problem}")
    if oversized:
        print("Oversized tracked files:")
        for problem in oversized:
            print(f"  {problem}")
        print("Remove generated files; compact or split durable evidence.")
        return 1
    print("Tracked file size contract passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the MEA-Thermodynamics project layout and analysis artifacts.")
    parser.add_argument("mode", choices=["quick", "confidence"], help="quick runs structural/tests checks; confidence also regenerates curated plots")
    args = parser.parse_args()

    commands = list(QUICK_COMMANDS)
    if args.mode == "confidence":
        commands.extend(PLOT_COMMANDS)
    status = verify_tracked_file_size()
    if status:
        return status
    for command in commands:
        status = max(status, run(command))
        if status:
            return status
    if args.mode == "confidence":
        status = max(status, verify_artifacts())
    return status


if __name__ == "__main__":
    raise SystemExit(main())
