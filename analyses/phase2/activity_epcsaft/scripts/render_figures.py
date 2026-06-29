from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.analysis_io import copy_file_as, copy_files, normalize_svg, read_required_csv, remove_matching_files  # noqa: E402
from MEA.common.plot_style import (  # noqa: E402
    EPCSAFT_IONIC_LINESTYLE,
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    MODEL_LINEWIDTH,
    PRESSURE_FIGSIZE,
    apply_pressure_axes,
    save_figure_bundle,
    temperature_color,
    write_mpl_sidecar,
)
from MEA.common.speciation_figures import write_speciation_plot  # noqa: E402

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
RESULTS_DIR = ANALYSIS_DIR / "results"
PRESSURE_FIGURE_OUT = ANALYSIS_DIR / "figures" / "pressure" / "output"
SPECIATION_FIGURE_OUT = ANALYSIS_DIR / "figures" / "speciation" / "output"
LATEX_FIGURES_DIR = REPO_ROOT / "docs" / "latex" / "figures"
STALE_SCAFFOLD_PATTERNS = (
    "phase2_speciation_scaffold_curve.csv",
    "phase2_speciation_scaffold_*C.png",
    "phase2_speciation_scaffold_*C.svg",
    "phase2_speciation_scaffold_*C.pdf",
    "phase2_speciation_scaffold_*C.mpl.yaml",
    "phase2_speciation_scaffold_*C_plot_data.csv",
)


def require_csv(name: str) -> pd.DataFrame:
    return read_required_csv(
        PROCESSED_DIR / name,
        hint="Run `uv run python analyses\\activity_epcsaft\\scripts\\generate_data.py` first",
    )


def remove_stale_scaffold_outputs() -> None:
    remove_matching_files((RESULTS_DIR, PRESSURE_FIGURE_OUT, SPECIATION_FIGURE_OUT), STALE_SCAFFOLD_PATTERNS)


def _numeric_pressure_frame(pressure_results: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "temperature_C",
        "CO2_loading",
        "observed_CO2_pressure_kPa",
        "model_CO2_pressure_kPa",
        "solver_success",
        "source",
    ]
    missing = [column for column in columns if column not in pressure_results.columns]
    if missing:
        raise RuntimeError(f"Phase 2 pressure plot is missing required columns: {missing}")
    frame = pressure_results[columns].copy()
    for column in ("temperature_C", "CO2_loading", "observed_CO2_pressure_kPa", "model_CO2_pressure_kPa"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["solver_success"] = frame["solver_success"].astype(str).str.lower() == "true"
    frame = frame.dropna(subset=["temperature_C", "CO2_loading", "observed_CO2_pressure_kPa", "model_CO2_pressure_kPa"])
    frame = frame[frame["solver_success"]]
    if frame.empty:
        raise RuntimeError("Phase 2 pressure plot has no solver-success rows.")
    return frame.sort_values(["temperature_C", "CO2_loading", "source"]).reset_index(drop=True)


def plot_pressure(pressure_results: pd.DataFrame) -> None:
    title = "Activity-based ePC-SAFT CO2 solubility"
    description = (
        "Observed 30 wt% MEA CO2 partial-pressure data are compared with activity-coupled ePC-SAFT "
        "reactive-bubble solubility-pressure rows from the fixed parameter set."
    )
    PRESSURE_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    frame = _numeric_pressure_frame(pressure_results)
    plot_data = frame.copy()
    plot_data["plot_role"] = "solver_success_pressure_row"
    plot_data.to_csv(RESULTS_DIR / "phase2_pressure_plot_data.csv", index=False)
    plot_data.to_csv(PRESSURE_FIGURE_OUT / "phase2_pressure_plot_data.csv", index=False)

    fig, ax = plt.subplots(figsize=PRESSURE_FIGSIZE)
    temperatures = sorted(frame["temperature_C"].dropna().unique())
    for temperature_C in temperatures:
        color = temperature_color(temperature_C)
        subset = frame[frame["temperature_C"] == temperature_C].sort_values("CO2_loading")
        observed = subset[["CO2_loading", "observed_CO2_pressure_kPa", "source"]].drop_duplicates()
        ax.plot(
            observed["CO2_loading"],
            observed["observed_CO2_pressure_kPa"],
            linestyle="none",
            marker=JOU_DATA_MARKER,
            markersize=JOU_DATA_MARKERSIZE,
            color=color,
            alpha=0.72,
        )
        ax.plot(
            subset["CO2_loading"],
            subset["model_CO2_pressure_kPa"],
            EPCSAFT_IONIC_LINESTYLE,
            color=color,
            linewidth=MODEL_LINEWIDTH,
            alpha=0.92,
        )

    apply_pressure_axes(ax, title=title)
    ax.set_xlim(0.0, 0.8)
    ax.set_ylim(1.0e-4, 5.0e3)
    temperature_handles = [
        Line2D([0], [0], color=temperature_color(temperature_C), linewidth=MODEL_LINEWIDTH, label=f"{temperature_C:g} C")
        for temperature_C in temperatures
    ]
    role_handles = [
        Line2D(
            [0],
            [0],
            marker=JOU_DATA_MARKER,
            linestyle="none",
            color="0.25",
            markersize=JOU_DATA_MARKERSIZE,
            label="Literature pressure",
        ),
        Line2D(
            [0],
            [0],
            linestyle=EPCSAFT_IONIC_LINESTYLE,
            color="0.25",
            linewidth=MODEL_LINEWIDTH,
            label="ePC-SAFT activity",
        ),
    ]
    temperature_legend = ax.legend(handles=temperature_handles, title="Temperature", ncol=1, loc="upper left")
    ax.add_artist(temperature_legend)
    ax.legend(handles=role_handles, title="Role", ncol=1, loc="lower right")
    fig.tight_layout()

    figure_stem = RESULTS_DIR / "phase2_pressure_vs_loading"
    png, svg, pdf = save_figure_bundle(fig, figure_stem)
    normalize_svg(svg)
    plt.close(fig)
    write_mpl_sidecar(
        RESULTS_DIR / "phase2_pressure_vs_loading.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        style_source="analyses/phase2/activity_epcsaft/scripts/render_figures.py",
    )
    copy_files((png, svg, pdf, RESULTS_DIR / "phase2_pressure_vs_loading.mpl.yaml"), PRESSURE_FIGURE_OUT)
    copy_file_as(pdf, LATEX_FIGURES_DIR / "mea_activity_pressure_vs_loading.pdf")


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PRESSURE_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    SPECIATION_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    remove_stale_scaffold_outputs()
    pressure = require_csv("phase2_pressure_results.csv")
    pressure_metrics = require_csv("phase2_pressure_metrics.csv")
    points = require_csv("phase2_speciation_reference_points.csv")
    target_roles = require_csv("phase2_speciation_target_roles.csv")
    curves = require_csv("phase2_speciation_activity_curves.csv")
    pressure.to_csv(PRESSURE_FIGURE_OUT / "phase2_pressure_results.csv", index=False)
    pressure_metrics.to_csv(PRESSURE_FIGURE_OUT / "phase2_pressure_metrics.csv", index=False)
    points.to_csv(SPECIATION_FIGURE_OUT / "phase2_speciation_reference_points.csv", index=False)
    points.to_csv(RESULTS_DIR / "phase2_speciation_reference_points.csv", index=False)
    target_roles.to_csv(SPECIATION_FIGURE_OUT / "phase2_speciation_target_roles.csv", index=False)
    target_roles.to_csv(RESULTS_DIR / "phase2_speciation_target_roles.csv", index=False)
    curves.to_csv(SPECIATION_FIGURE_OUT / "phase2_speciation_activity_curves.csv", index=False)
    curves.to_csv(RESULTS_DIR / "phase2_speciation_activity_curves.csv", index=False)
    plot_pressure(pressure)
    write_speciation_plot(
        curve_frame=curves,
        point_frame=points,
        output_dir=RESULTS_DIR,
        stem="phase2_speciation_activity_plot",
        title="Activity-based ePC-SAFT speciation, 40 C",
        description=(
            "Continuous curves are activity-coupled ePC-SAFT equilibrium solutions from the fixed "
            "parameter set; markers are measured reference points. Residual acceptance is controlled "
            "by phase2_residual_acceptance_audit.csv."
        ),
        style_source="analyses/phase2/activity_epcsaft/scripts/render_figures.py",
        temperature_C=40.0,
    )
    for temperature_C in sorted(curves["temperature_C"].dropna().unique()):
        png, svg, pdf, sidecar = write_speciation_plot(
            curve_frame=curves,
            point_frame=points,
            output_dir=SPECIATION_FIGURE_OUT,
            stem=f"phase2_speciation_{int(round(float(temperature_C)))}C",
            title=f"Activity-based ePC-SAFT speciation, {float(temperature_C):g} C",
            description=(
                "Continuous curves are activity-coupled ePC-SAFT equilibrium solutions from the fixed "
                "parameter set; markers are measured reference points. Claim status is controlled by "
                "the residual acceptance audit."
            ),
            style_source="analyses/phase2/activity_epcsaft/scripts/render_figures.py",
            temperature_C=float(temperature_C),
        )
        copy_file_as(pdf, LATEX_FIGURES_DIR / f"mea_activity_speciation_{int(round(float(temperature_C)))}C.pdf")
    write_mpl_sidecar(
        SPECIATION_FIGURE_OUT / "phase2_speciation_figure_family.mpl.yaml",
        png_name="phase2_speciation_40C.png",
        svg_name="phase2_speciation_40C.svg",
        pdf_name="phase2_speciation_40C.pdf",
        title="Activity-based ePC-SAFT speciation figure family",
        description="Figure-owned activity-coupled ePC-SAFT equilibrium speciation outputs; one full-coverage plot is generated per temperature.",
        style_source="analyses/phase2/activity_epcsaft/scripts/render_figures.py",
    )
    print(f"Phase 2 activity-speciation plot artifacts: {SPECIATION_FIGURE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
