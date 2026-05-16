from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.plot_style import (  # noqa: E402
    EPCSAFT_IONIC_LINESTYLE,
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    MODEL_LINEWIDTH,
    PRESSURE_FIGSIZE,
    apply_pressure_axes,
    temperature_color,
    write_mpl_sidecar,
)
from MEA.common.speciation_figures import write_speciation_plot  # noqa: E402

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
RESULTS_DIR = ANALYSIS_DIR / "results"
PRESSURE_FIGURE_OUT = ANALYSIS_DIR / "figures" / "pressure" / "output"
SPECIATION_FIGURE_OUT = ANALYSIS_DIR / "figures" / "speciation" / "output"
STALE_SCAFFOLD_PATTERNS = (
    "phase2_speciation_scaffold_curve.csv",
    "phase2_speciation_scaffold_*C.png",
    "phase2_speciation_scaffold_*C.svg",
    "phase2_speciation_scaffold_*C.mpl.yaml",
    "phase2_speciation_scaffold_*C_plot_data.csv",
)


def require_csv(name: str) -> pd.DataFrame:
    path = PROCESSED_DIR / name
    if not path.exists():
        raise RuntimeError(
            f"Missing {path}. Run `uv run python analyses\\phase2_activity_epcsaft\\scripts\\generate_data.py` first."
        )
    return pd.read_csv(path)


def normalize_svg(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def remove_stale_scaffold_outputs() -> None:
    for root in (RESULTS_DIR, PRESSURE_FIGURE_OUT, SPECIATION_FIGURE_OUT):
        root.mkdir(parents=True, exist_ok=True)
        for pattern in STALE_SCAFFOLD_PATTERNS:
            for path in root.glob(pattern):
                path.unlink()


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
    title = "Phase 2 ePC-SAFT activity pressure evaluation"
    description = (
        "Observed 30 wt% MEA CO2 partial-pressure data are compared with native ePC-SAFT "
        "reactive-bubble pressure rows from the Phase 2 parameter artifact."
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

    png = RESULTS_DIR / "phase2_pressure_vs_loading.png"
    svg = RESULTS_DIR / "phase2_pressure_vs_loading.svg"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    normalize_svg(svg)
    plt.close(fig)
    write_mpl_sidecar(
        RESULTS_DIR / "phase2_pressure_vs_loading.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        title=title,
        description=description,
        style_source="analyses/phase2_activity_epcsaft/scripts/render_figures.py",
    )
    for path in (png, svg, RESULTS_DIR / "phase2_pressure_vs_loading.mpl.yaml"):
        shutil.copy2(path, PRESSURE_FIGURE_OUT / path.name)


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
        title="Phase 2 ePC-SAFT activity speciation, 40 C",
        description=(
            "Continuous curves are native ePC-SAFT activity-equilibrium solutions from the Phase 2 "
            "parameter artifact; markers are measured reference points. Residual acceptance is controlled "
            "by phase2_residual_acceptance_audit.csv."
        ),
        style_source="analyses/phase2_activity_epcsaft/scripts/render_figures.py",
        temperature_C=40.0,
    )
    for temperature_C in sorted(curves["temperature_C"].dropna().unique()):
        write_speciation_plot(
            curve_frame=curves,
            point_frame=points,
            output_dir=SPECIATION_FIGURE_OUT,
            stem=f"phase2_speciation_{int(round(float(temperature_C)))}C",
            title=f"Phase 2 ePC-SAFT activity speciation, {float(temperature_C):g} C",
            description=(
                "Continuous curves are native ePC-SAFT activity-equilibrium solutions from the Phase 2 "
                "parameter artifact; markers are measured reference points. Claim status is controlled by "
                "the residual acceptance audit."
            ),
            style_source="analyses/phase2_activity_epcsaft/scripts/render_figures.py",
            temperature_C=float(temperature_C),
        )
    write_mpl_sidecar(
        SPECIATION_FIGURE_OUT / "phase2_speciation_figure_family.mpl.yaml",
        png_name="phase2_speciation_40C.png",
        svg_name="phase2_speciation_40C.svg",
        title="Phase 2 ePC-SAFT activity speciation figure family",
        description="Figure-owned Phase 2 native ePC-SAFT activity-equilibrium speciation outputs; one full-coverage plot is generated per temperature.",
        style_source="analyses/phase2_activity_epcsaft/scripts/render_figures.py",
    )
    print(f"Phase 2 activity-speciation plot artifacts: {SPECIATION_FIGURE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
