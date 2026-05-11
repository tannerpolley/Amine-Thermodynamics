from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.plot_style import species_color, species_label  # noqa: E402
from MEA.epcsaft_ionic.global_regression import copy_manuscript_residual_figures  # noqa: E402
from MEA.epcsaft_ionic.plot_results import plot_pressure, plot_speciation  # noqa: E402

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PRESSURE_CSV = ANALYSIS_DIR / "results" / "pressure" / "ionic_pressure_comparison.csv"
SPECIATION_CSV = ANALYSIS_DIR / "results" / "speciation" / "ionic_speciation_activity_residuals.csv"
PRESSURE_DIR = ANALYSIS_DIR / "results" / "pressure"
SPECIATION_DIR = ANALYSIS_DIR / "results" / "speciation"
LATEX_FIGURES_DIR = REPO_ROOT / "docs" / "latex" / "figures"


def write_pressure_residual_plot(pressure_rows: list[dict[str, object]]) -> tuple[Path, Path]:
    frame = pd.DataFrame(pressure_rows)
    residual_frame = frame[["row_id", "paper", "temperature_C", "CO2_loading", "raw_log10_model_over_data"]].rename(
        columns={"paper": "source", "raw_log10_model_over_data": "log10_model_over_data"}
    )
    residual_csv = PRESSURE_DIR / "ionic_pressure_residuals_by_loading.csv"
    residual_frame.to_csv(residual_csv, index=False)
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
    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("log10(model/data) pressure residual")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    png = PRESSURE_DIR / "ionic_pressure_residuals_by_loading.png"
    svg = PRESSURE_DIR / "ionic_pressure_residuals_by_loading.svg"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    (PRESSURE_DIR / "ionic_pressure_residuals_by_loading.mpl.yaml").write_text(
        "figure:\n  png: ionic_pressure_residuals_by_loading.png\n  svg: ionic_pressure_residuals_by_loading.svg\n  dpi: 300\n",
        encoding="utf-8",
    )
    return png, svg


def write_speciation_residual_plot(speciation_rows: list[dict[str, object]]) -> tuple[Path, Path]:
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
    ax.set_ylabel("Absolute log10(model/data) residual")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    png = SPECIATION_DIR / "ionic_speciation_residuals_by_species.png"
    svg = SPECIATION_DIR / "ionic_speciation_residuals_by_species.svg"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    (SPECIATION_DIR / "ionic_speciation_residuals_by_species.mpl.yaml").write_text(
        "figure:\n  png: ionic_speciation_residuals_by_species.png\n  svg: ionic_speciation_residuals_by_species.svg\n  dpi: 300\n",
        encoding="utf-8",
    )
    return png, svg


def main() -> int:
    missing = [path for path in (PRESSURE_CSV, SPECIATION_CSV) if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing ionic plot snapshot: {path}")
        print("Run `uv run python analyses\\epcsaft_ionic_regression\\scripts\\generate_data.py` first.")
        return 1
    pressure_rows = pd.read_csv(PRESSURE_CSV).to_dict("records")
    speciation_rows = pd.read_csv(SPECIATION_CSV).to_dict("records")
    pressure_plot = plot_pressure(pressure_rows)
    speciation_plot = plot_speciation(speciation_rows)
    pressure_residual_png, pressure_residual_svg = write_pressure_residual_plot(pressure_rows)
    speciation_residual_png, speciation_residual_svg = write_speciation_residual_plot(speciation_rows)
    copy_manuscript_residual_figures(
        pressure_residual_png,
        pressure_residual_svg,
        speciation_residual_png,
        speciation_residual_svg,
        LATEX_FIGURES_DIR,
    )
    print(f"Ionic pressure plot: {pressure_plot}")
    print(f"Ionic speciation plot: {speciation_plot}")
    print(f"Ionic pressure residual plot: {pressure_residual_png}")
    print(f"Ionic speciation residual plot: {speciation_residual_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
