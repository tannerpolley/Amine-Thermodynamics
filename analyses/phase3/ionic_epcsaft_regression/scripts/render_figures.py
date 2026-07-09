from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.analysis_io import copy_file_as  # noqa: E402
from MEA.common.plot_style import finish_axes, save_figure_bundle, species_color, species_label, write_mpl_sidecar  # noqa: E402
from MEA.epcsaft_ionic.global_regression import (  # noqa: E402
    GLOBAL_RESULTS_DIR,
    SENSITIVITY_DIR,
    SENSITIVITY_METRICS,
    TRAIN_VALIDATION_DIR,
    write_pressure_parity,
    write_sensitivity_heatmap,
    write_speciation_parity,
    write_train_validation_plot,
)
from MEA.epcsaft_ionic.ion_parameter_regression import (  # noqa: E402
    OUT_DIR as ION_PARAMETER_DIR,
    plot_loading_curves,
    plot_pressure_placeholder,
    plot_speciation_parity,
)
from MEA.epcsaft_ionic.plot_results import plot_pressure, plot_speciation  # noqa: E402
from fit_trace_carbonate_born import OUT_DIR as TRACE_CARBONATE_DIR  # noqa: E402

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
PRESSURE_CSV = PROCESSED_DIR / "ionic_pressure_comparison.csv"
SPECIATION_CSV = PROCESSED_DIR / "ionic_speciation_activity_residuals.csv"
PRESSURE_DIR = ANALYSIS_DIR / "results" / "pressure"
SPECIATION_DIR = ANALYSIS_DIR / "results" / "speciation"
LATEX_FIGURES_DIR = REPO_ROOT / "docs" / "latex" / "figures"


def write_pressure_residual_plot(pressure_rows: list[dict[str, object]]) -> tuple[Path, Path, Path]:
    frame = pd.DataFrame(pressure_rows)
    residual_frame = frame[["row_id", "paper", "temperature_C", "CO2_loading", "raw_log10_model_over_data"]].rename(
        columns={"paper": "source", "raw_log10_model_over_data": "log10_model_over_data"}
    )
    residual_csv = PRESSURE_DIR / "ionic_pressure_residuals_by_loading.csv"
    residual_frame.to_csv(residual_csv, index=False)
    title = "Full-ionic pressure residuals by loading"
    description = (
        "Logarithmic carbon-dioxide pressure residuals are plotted against loading, "
        "with marker shape keyed to nominal temperature and color keyed to data source."
    )
    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    markers = {40: "o", 60: "s", 80: "^", 100: "D", 120: "P"}
    for source, subset in residual_frame.groupby("source"):
        ax.scatter(
            subset["CO2_loading"],
            subset["log10_model_over_data"],
            label=str(source),
            alpha=0.7,
            marker=markers.get(int(round(float(subset["temperature_C"].median()))), "o"),
        )
    ax.axhline(0.0, color="black", linestyle=":", linewidth=1.0)
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("$\\log_{10}$(model/data) pressure residual")
    finish_axes(ax, title=title)
    ax.legend(fontsize=8, title="Literature source")
    fig.tight_layout()
    figure_stem = PRESSURE_DIR / "ionic_pressure_residuals_by_loading"
    png, svg, pdf = save_figure_bundle(fig, figure_stem)
    plt.close(fig)
    write_mpl_sidecar(
        PRESSURE_DIR / "ionic_pressure_residuals_by_loading.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        style_source="analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py",
    )
    return png, svg, pdf


def write_speciation_residual_plot(speciation_rows: list[dict[str, object]]) -> tuple[Path, Path, Path]:
    frame = pd.DataFrame(speciation_rows)
    melted_rows = []
    species_names = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
    for row in frame.to_dict("records"):
        for species in species_names:
            melted_rows.append(
                {
                    "row_id": row["row_id"],
                    "source": row["source"],
                    "species": species,
                    "temperature_C": row["temperature_C"],
                    "CO2_loading": row["CO2_loading"],
                    "abs_log10_residual": abs(float(row[f"log10_model_over_target_{species}"])),
                }
            )
    residual_frame = pd.DataFrame(melted_rows)
    residual_csv = SPECIATION_DIR / "ionic_speciation_residuals_by_species.csv"
    residual_frame.to_csv(residual_csv, index=False)
    title = "Full-ionic speciation residual distribution by species"
    description = (
        "Absolute log10 true-species residuals are shown by species; black bars mark species medians."
    )
    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    order = list(species_names)
    positions = {species: idx for idx, species in enumerate(order)}
    for species, subset in residual_frame.groupby("species"):
        x = np.full(len(subset), positions[str(species)], dtype=float)
        ax.scatter(
            x,
            subset["abs_log10_residual"],
            color=species_color(str(species)),
            alpha=0.3,
            edgecolor="none",
        )
        median = float(np.median(subset["abs_log10_residual"]))
        ax.hlines(median, positions[str(species)] - 0.3, positions[str(species)] + 0.3, colors="black", linewidth=2.0)
    ax.set_xticks(range(len(order)), [species_label(species) for species in order], rotation=30, ha="right")
    ax.set_ylabel("Absolute $\\log_{10}$(model/data) residual")
    finish_axes(ax, title=title, grid_axis="y")
    fig.tight_layout()
    figure_stem = SPECIATION_DIR / "ionic_speciation_residuals_by_species"
    png, svg, pdf = save_figure_bundle(fig, figure_stem)
    plt.close(fig)
    write_mpl_sidecar(
        SPECIATION_DIR / "ionic_speciation_residuals_by_species.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        style_source="analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py",
    )
    return png, svg, pdf


def write_trace_carbonate_plot(frame: pd.DataFrame) -> None:
    title = "Trace-carbonate Born diagnostic parity"
    description = (
        "Trace bicarbonate and carbonate model mole fractions are compared against observed targets "
        "for the carbonate Born-diameter diagnostic."
    )
    final = frame[frame["fit_stage"] == "final"]
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    for species, subset in final.groupby("species"):
        ax.scatter(
            subset["observed_mole_fraction"],
            subset["model_mole_fraction"],
            label=species_label(species),
            color=species_color(species),
            edgecolor="black",
            linewidth=0.35,
            alpha=0.8,
        )
    finite = final[["observed_mole_fraction", "model_mole_fraction"]].replace([np.inf, -np.inf], np.nan).dropna()
    lo = max(1.0e-8, float(finite.min().min()) * 0.7) if not finite.empty else 1.0e-8
    hi = min(1.0, float(finite.max().max()) * 1.3) if not finite.empty else 1.0
    ax.plot([lo, hi], [lo, hi], color="black", linestyle=":", label="1:1")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Observed true-species mole fraction")
    ax.set_ylabel("Model true-species mole fraction")
    finish_axes(ax, title=title)
    ax.legend(fontsize=8, title="Species")
    fig.tight_layout()
    figure_stem = TRACE_CARBONATE_DIR / "trace_carbonate_born_parity"
    png, svg, pdf = save_figure_bundle(fig, figure_stem)
    plt.close(fig)
    write_mpl_sidecar(
        TRACE_CARBONATE_DIR / "trace_carbonate_born_parity.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        style_source="analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py",
    )
    copy_file_as(pdf, LATEX_FIGURES_DIR / "trace_carbonate_born_parity.pdf")


def render_ion_parameter_evidence() -> None:
    fit_data = ION_PARAMETER_DIR / "ion_parameter_speciation_fit_data.csv"
    if not fit_data.exists():
        return
    frame = pd.read_csv(fit_data)
    speciation_png = plot_speciation_parity(frame, ION_PARAMETER_DIR)
    loading_png = plot_loading_curves(frame, ION_PARAMETER_DIR)
    plot_pressure_placeholder(ION_PARAMETER_DIR)
    copy_file_as(speciation_png.with_suffix(".pdf"), LATEX_FIGURES_DIR / "meah_meacoo_speciation_parity.pdf")
    copy_file_as(loading_png.with_suffix(".pdf"), LATEX_FIGURES_DIR / "meah_meacoo_loading_curves.pdf")


def render_optional_global_diagnostics() -> None:
    pressure_residuals = GLOBAL_RESULTS_DIR / "global_regression_pressure_residuals.csv"
    speciation_residuals = GLOBAL_RESULTS_DIR / "global_regression_speciation_residuals.csv"
    train_validation_pressure = TRAIN_VALIDATION_DIR / "train_validation_pressure_residuals.csv"
    sensitivity_matrix = SENSITIVITY_DIR / "parameter_sensitivity_matrix.csv"
    trace_carbonate = TRACE_CARBONATE_DIR / "trace_carbonate_born_fit_data.csv"
    if pressure_residuals.exists():
        write_pressure_parity(pd.read_csv(pressure_residuals), GLOBAL_RESULTS_DIR)
    if speciation_residuals.exists():
        write_speciation_parity(pd.read_csv(speciation_residuals), GLOBAL_RESULTS_DIR)
    if train_validation_pressure.exists():
        write_train_validation_plot(pd.read_csv(train_validation_pressure))
    if sensitivity_matrix.exists():
        matrix = pd.read_csv(sensitivity_matrix)
        if not matrix.empty:
            parameters = list(dict.fromkeys(matrix["parameter"].astype(str).tolist()))
            vectors = {
                parameter: [
                    float(
                        matrix[
                            (matrix["parameter"].astype(str) == parameter)
                            & (matrix["metric"].astype(str) == metric)
                        ]["sensitivity"].iloc[0]
                    )
                    for metric in SENSITIVITY_METRICS
                ]
                for parameter in parameters
            }
            write_sensitivity_heatmap(parameters, vectors)
    if trace_carbonate.exists():
        write_trace_carbonate_plot(pd.read_csv(trace_carbonate))


def main() -> int:
    missing = [path for path in (PRESSURE_CSV, SPECIATION_CSV) if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing ionic plot snapshot: {path}")
        print("Run `uv run python analyses/phase3/ionic_epcsaft_regression/scripts/generate_data.py` first.")
        return 1
    pressure_rows = pd.read_csv(PRESSURE_CSV).to_dict("records")
    speciation_rows = pd.read_csv(SPECIATION_CSV).to_dict("records")
    pd.DataFrame(pressure_rows).to_csv(PRESSURE_DIR / "ionic_pressure_comparison.csv", index=False)
    pd.DataFrame(speciation_rows).to_csv(SPECIATION_DIR / "ionic_speciation_activity_residuals.csv", index=False)
    pressure_plot = plot_pressure(pressure_rows)
    speciation_plot = plot_speciation(speciation_rows)
    pressure_residual_png, _, _ = write_pressure_residual_plot(pressure_rows)
    speciation_residual_png, _, _ = write_speciation_residual_plot(speciation_rows)
    render_ion_parameter_evidence()
    render_optional_global_diagnostics()
    print(f"Ionic pressure plot: {pressure_plot}")
    print(f"Ionic speciation plot: {speciation_plot}")
    print(f"Ionic pressure residual plot: {pressure_residual_png}")
    print(f"Ionic speciation residual plot: {speciation_residual_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
