from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.analysis_io import copy_file_as, normalize_svg, read_required_csv, remove_matching_files  # noqa: E402
from MEA.common.plot_style import (  # noqa: E402
    EPCSAFT_IONIC_LINESTYLE,
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    MODEL_LINEWIDTH,
    PRESSURE_FIGSIZE,
    apply_pressure_axes,
    finish_axes,
    save_figure_bundle,
    temperature_color,
    write_mpl_sidecar,
)
from MEA.common.speciation_figures import write_speciation_plot  # noqa: E402

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ANALYSIS_DIR / "results"
PRESSURE_FIGURE_OUT = ANALYSIS_DIR / "figures" / "pressure" / "output"
SPECIATION_FIGURE_OUT = ANALYSIS_DIR / "figures" / "speciation" / "output"
CONTROLLED_COMPARISON_INPUT = (
    RESULTS_DIR / "controlled_comparison" / "paired_pressure_rows.csv"
)
CONTROLLED_COMPARISON_FIGURE_OUT = (
    ANALYSIS_DIR / "figures" / "controlled_comparison" / "output"
)
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
        RESULTS_DIR / name,
        hint="Run `uv run python analyses/phase2/activity_epcsaft/scripts/generate_data.py` first",
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


def _strict_boolean(series: pd.Series, *, column: str) -> pd.Series:
    normalized = series.astype(str).str.strip().str.lower()
    invalid = ~normalized.isin({"true", "false"})
    if invalid.any():
        values = sorted(series.loc[invalid].astype(str).unique())
        raise ValueError(f"Controlled comparison {column} contains invalid booleans: {values}")
    return normalized == "true"


def prepare_controlled_comparison_plot_data(rows: pd.DataFrame) -> pd.DataFrame:
    required = (
        "row_id",
        "source",
        "temperature_C",
        "MEA_weight_fraction",
        "CO2_loading",
        "observed_CO2_pressure_kPa",
        "phase1_model_pressure_kPa",
        "phase1_log10_residual",
        "phase1_accepted",
        "phase2_model_pressure_kPa",
        "phase2_log10_residual",
        "phase2_accepted",
        "comparison_eligible",
        "preferred_model_on_row",
    )
    missing = [column for column in required if column not in rows.columns]
    if missing:
        raise ValueError(f"Controlled comparison plot is missing required columns: {missing}")

    plot_data = rows.loc[:, required].copy()
    numeric_columns = (
        "temperature_C",
        "MEA_weight_fraction",
        "CO2_loading",
        "observed_CO2_pressure_kPa",
        "phase1_model_pressure_kPa",
        "phase1_log10_residual",
        "phase2_model_pressure_kPa",
        "phase2_log10_residual",
    )
    for column in numeric_columns:
        plot_data[column] = pd.to_numeric(plot_data[column], errors="coerce")

    finite_columns = list(numeric_columns)
    if not np.isfinite(plot_data[finite_columns].to_numpy(dtype=float)).all():
        raise ValueError("Controlled comparison plot requires finite numeric values")

    pressure_columns = (
        "observed_CO2_pressure_kPa",
        "phase1_model_pressure_kPa",
        "phase2_model_pressure_kPa",
    )
    if (plot_data.loc[:, pressure_columns] <= 0.0).to_numpy().any():
        raise ValueError("Controlled comparison plot requires positive finite pressure values")

    accepted = (
        _strict_boolean(plot_data["phase1_accepted"], column="phase1_accepted")
        & _strict_boolean(plot_data["phase2_accepted"], column="phase2_accepted")
        & _strict_boolean(plot_data["comparison_eligible"], column="comparison_eligible")
    )
    if not accepted.all():
        rejected = plot_data.loc[~accepted, "row_id"].astype(str).tolist()
        raise ValueError(
            "Controlled comparison plot requires every row to be accepted and eligible; "
            f"rejected rows: {rejected}"
        )
    if len(plot_data) != 31:
        raise ValueError(
            "Controlled comparison plot requires the 31 accepted paired Jou1995 rows; "
            f"received {len(plot_data)}"
        )
    if set(plot_data["source"].astype(str)) != {"Jou1995"}:
        raise ValueError("Controlled comparison plot requires only Jou1995 paired rows")

    plot_data["ideal_abs_log10_error"] = plot_data["phase1_log10_residual"].abs()
    plot_data["activity_abs_log10_error"] = plot_data["phase2_log10_residual"].abs()
    difference = (
        plot_data["activity_abs_log10_error"]
        - plot_data["ideal_abs_log10_error"]
    )
    if np.isclose(difference.to_numpy(dtype=float), 0.0, rtol=0.0, atol=1.0e-12).any():
        raise ValueError("Controlled comparison plot does not permit tied row residuals")
    plot_data["comparison_outcome"] = np.where(
        difference < 0.0,
        "improved",
        "worsened",
    )
    expected_preference = plot_data["comparison_outcome"].map(
        {"improved": "activity_model", "worsened": "ideal_baseline"}
    )
    if not expected_preference.equals(plot_data["preferred_model_on_row"].astype(str)):
        raise ValueError(
            "Controlled comparison preferred-model labels disagree with paired residuals"
        )
    counts = plot_data["comparison_outcome"].value_counts().to_dict()
    if counts != {"worsened": 27, "improved": 4}:
        raise ValueError(
            "Controlled comparison plot expected 4 improved and 27 worsened rows; "
            f"received {counts}"
        )

    output_columns = (
        "row_id",
        "source",
        "temperature_C",
        "MEA_weight_fraction",
        "CO2_loading",
        "observed_CO2_pressure_kPa",
        "phase1_model_pressure_kPa",
        "phase2_model_pressure_kPa",
        "phase1_log10_residual",
        "phase2_log10_residual",
        "ideal_abs_log10_error",
        "activity_abs_log10_error",
        "comparison_outcome",
    )
    return plot_data.loc[:, output_columns].sort_values(
        ["temperature_C", "CO2_loading", "row_id"]
    ).reset_index(drop=True)


def plot_controlled_comparison(
    rows: pd.DataFrame,
) -> tuple[Path, Path, Path, Path, Path]:
    title = "Controlled ideal and activity-model pressure comparison"
    description = (
        "Observed pressure parity and paired absolute log-residual comparison for the same "
        "31 Jou1995 records evaluated by the ideal and fixed activity-based models."
    )
    output = CONTROLLED_COMPARISON_FIGURE_OUT
    output.mkdir(parents=True, exist_ok=True)
    LATEX_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_data = prepare_controlled_comparison_plot_data(rows)
    plot_data_path = output / "controlled_pressure_comparison_plot_data.csv"
    plot_data.to_csv(plot_data_path, index=False, lineterminator="\n")

    fig, (pressure_ax, residual_ax) = plt.subplots(1, 2, figsize=(12.0, 5.2))
    observed = plot_data["observed_CO2_pressure_kPa"]
    pressure_ax.scatter(
        observed,
        plot_data["phase1_model_pressure_kPa"],
        marker="o",
        facecolors="none",
        edgecolors="#1f5aa6",
        linewidths=1.3,
        s=46,
        label="Ideal baseline",
        zorder=3,
    )
    pressure_ax.scatter(
        observed,
        plot_data["phase2_model_pressure_kPa"],
        marker="^",
        color="#c65f00",
        edgecolors="#6f3500",
        linewidths=0.5,
        s=48,
        label="Activity model",
        zorder=3,
    )
    pressure_values = plot_data[
        [
            "observed_CO2_pressure_kPa",
            "phase1_model_pressure_kPa",
            "phase2_model_pressure_kPa",
        ]
    ].to_numpy(dtype=float)
    pressure_min = 10.0 ** np.floor(np.log10(pressure_values.min()))
    pressure_max = 10.0 ** np.ceil(np.log10(pressure_values.max()))
    pressure_ax.plot(
        [pressure_min, pressure_max],
        [pressure_min, pressure_max],
        linestyle="--",
        color="0.35",
        linewidth=1.3,
        label="One-to-one",
        zorder=1,
    )
    pressure_ax.set_xscale("log")
    pressure_ax.set_yscale("log")
    pressure_ax.set_xlim(pressure_min, pressure_max)
    pressure_ax.set_ylim(pressure_min, pressure_max)
    pressure_ax.set_xlabel("Observed $CO_2$ pressure, kPa")
    pressure_ax.set_ylabel("Predicted $CO_2$ pressure, kPa")
    finish_axes(pressure_ax, title="(a) Pressure parity")
    pressure_ax.legend(loc="upper left")

    outcome_styles = {
        "improved": ("o", "#16805a", "Activity residual smaller"),
        "worsened": ("^", "#b6312c", "Activity residual larger"),
    }
    for outcome, (marker, color, label) in outcome_styles.items():
        subset = plot_data[plot_data["comparison_outcome"] == outcome]
        residual_ax.scatter(
            subset["ideal_abs_log10_error"],
            subset["activity_abs_log10_error"],
            marker=marker,
            color=color,
            edgecolors="white",
            linewidths=0.55,
            s=52,
            label=label,
            zorder=3,
        )
    residual_max = 1.1 * max(
        float(plot_data["ideal_abs_log10_error"].max()),
        float(plot_data["activity_abs_log10_error"].max()),
    )
    residual_ax.plot(
        [0.0, residual_max],
        [0.0, residual_max],
        linestyle="--",
        color="0.35",
        linewidth=1.3,
        label="Equal absolute residual",
        zorder=1,
    )
    residual_ax.set_xlim(0.0, residual_max)
    residual_ax.set_ylim(0.0, residual_max)
    residual_ax.set_xlabel("Ideal absolute $\\log_{10}$ residual")
    residual_ax.set_ylabel("Activity absolute $\\log_{10}$ residual")
    finish_axes(residual_ax, title="(b) Paired residual change")
    residual_ax.legend(loc="upper left")
    residual_ax.text(
        0.97,
        0.04,
        "4 improved; 27 worsened",
        transform=residual_ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9.5,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "0.75"},
    )

    fig.suptitle("Controlled pressure comparison", fontsize=14, fontweight="semibold")
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    stem = output / "controlled_pressure_comparison"
    png, svg, pdf = save_figure_bundle(fig, stem)
    normalize_svg(svg)
    plt.close(fig)
    sidecar = output / "controlled_pressure_comparison.mpl.yaml"
    write_mpl_sidecar(
        sidecar,
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=plot_data_path,
        style_source="analyses/phase2/activity_epcsaft/scripts/render_figures.py",
    )
    copy_file_as(
        pdf,
        LATEX_FIGURES_DIR / "mea_controlled_pressure_comparison.pdf",
    )
    return png, svg, pdf, plot_data_path, sidecar


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
    plot_data_path = PRESSURE_FIGURE_OUT / "phase2_pressure_plot_data.csv"
    plot_data.to_csv(plot_data_path, index=False)

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

    figure_stem = PRESSURE_FIGURE_OUT / "phase2_pressure_vs_loading"
    png, svg, pdf = save_figure_bundle(fig, figure_stem)
    normalize_svg(svg)
    plt.close(fig)
    write_mpl_sidecar(
        PRESSURE_FIGURE_OUT / "phase2_pressure_vs_loading.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=plot_data_path,
        style_source="analyses/phase2/activity_epcsaft/scripts/render_figures.py",
    )
    copy_file_as(pdf, LATEX_FIGURES_DIR / "mea_activity_pressure_vs_loading.pdf")


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PRESSURE_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    SPECIATION_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    remove_stale_scaffold_outputs()
    pressure = require_csv("phase2_pressure_results.csv")
    controlled_comparison = read_required_csv(
        CONTROLLED_COMPARISON_INPUT,
        hint="Run `uv run python analyses/phase2/activity_epcsaft/scripts/generate_data.py` first",
    )
    points = require_csv("phase2_speciation_reference_points.csv")
    curves = require_csv("phase2_speciation_activity_curves.csv")
    plot_pressure(pressure)
    plot_controlled_comparison(controlled_comparison)
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
        data_path=SPECIATION_FIGURE_OUT / "phase2_speciation_40C_plot_data.csv",
        style_source="analyses/phase2/activity_epcsaft/scripts/render_figures.py",
    )
    print(f"Phase 2 activity-speciation plot artifacts: {SPECIATION_FIGURE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
