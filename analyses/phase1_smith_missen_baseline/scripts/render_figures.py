from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.plot_style import (
    EPCSAFT_NEUTRAL_LINESTYLE,
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    LEGACY_PCSAFT_LINESTYLE,
    MODEL_LINEWIDTH,
    REFERENCE_LINEWIDTH,
    SPECIATION_MODEL_LINESTYLE,
    SPECIATION_TARGET_ALPHA,
    SPECIATION_TARGET_MARKER,
    SPECIATION_TARGET_MARKERSIZE,
    apply_pressure_axes,
    finish_axes,
    species_color,
    species_label,
    temperature_color,
    write_mpl_sidecar,
)

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
OUT_DIR = ANALYSIS_DIR / "results"
PRESSURE_MODEL_LABELS = {
    "legacy_pcsaft_smith_missen": ("Legacy PC-SAFT Smith-Missen", LEGACY_PCSAFT_LINESTYLE, REFERENCE_LINEWIDTH),
    "neutral_epcsaft_parity": ("Neutral ePC-SAFT parity", EPCSAFT_NEUTRAL_LINESTYLE, MODEL_LINEWIDTH),
}
MAJOR_SPECIATION_SPECIES = ("MEA + MEAH+", "MEACOO-", "HCO3-")
PHASE1_PRESSURE_FIGSIZE = (9.2, 5.4)
PHASE1_SPECIATION_FIGSIZE = (10.8, 4.8)


def _data_xlim(frame: pd.DataFrame, column: str, *, pad: float = 0.035) -> tuple[float, float]:
    values = frame[column].dropna().astype(float)
    if values.empty:
        return (0.0, 0.8)
    lo = max(0.0, float(values.min()) - pad)
    hi = min(0.8, float(values.max()) + pad)
    return (lo, hi)


def require_csv(name: str) -> pd.DataFrame:
    path = PROCESSED_DIR / name
    if not path.exists():
        raise RuntimeError(
            f"Missing {path}. Run `uv run python analyses\\phase1_smith_missen_baseline\\scripts\\generate_data.py` first."
        )
    return pd.read_csv(path)


def normalize_svg(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def _write_curated_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pressure_results = require_csv("phase1_pressure_results.csv")
    pressure_metrics = require_csv("phase1_pressure_metrics.csv")
    speciation_results = require_csv("phase1_speciation_results.csv")
    speciation_metrics = require_csv("phase1_speciation_metrics.csv")
    parameter_table = require_csv("phase1_parameter_table.csv")
    reaction_table = require_csv("phase1_reaction_constant_table.csv")
    for frame, name in (
        (pressure_results, "phase1_pressure_results.csv"),
        (pressure_metrics, "phase1_pressure_metrics.csv"),
        (speciation_results, "phase1_speciation_results.csv"),
        (speciation_metrics, "phase1_speciation_metrics.csv"),
        (parameter_table, "phase1_parameter_table.csv"),
        (reaction_table, "phase1_reaction_constant_table.csv"),
    ):
        frame.to_csv(OUT_DIR / name, index=False)
    return pressure_results, speciation_results


def plot_pressure(pressure_results: pd.DataFrame) -> None:
    title = "Phase 1 Smith-Missen baseline pressure reproduction"
    description = (
        "Observed 30 wt% MEA CO2 partial-pressure data are compared against the retained legacy Smith-Missen "
        "pressure baseline and the neutral ePC-SAFT parity route."
    )
    fig, ax = plt.subplots(figsize=PHASE1_PRESSURE_FIGSIZE)
    temperatures = sorted(pressure_results["temperature_C"].dropna().unique())
    for temperature_C in temperatures:
        color = temperature_color(temperature_C)
        t_df = pressure_results[pressure_results["temperature_C"] == temperature_C]
        observed = t_df[["CO2_loading", "observed_CO2_pressure_kPa"]].drop_duplicates().sort_values("CO2_loading")
        if not observed.empty:
            ax.plot(
                observed["CO2_loading"],
                observed["observed_CO2_pressure_kPa"],
                linestyle="none",
                marker=JOU_DATA_MARKER,
                markersize=JOU_DATA_MARKERSIZE,
                color=color,
                alpha=0.9,
            )
        for model_family, (label, linestyle, linewidth) in PRESSURE_MODEL_LABELS.items():
            subset = t_df[t_df["model_family"] == model_family].sort_values("CO2_loading")
            if subset.empty:
                continue
            ax.plot(
                subset["CO2_loading"],
                subset["predicted_CO2_pressure_kPa"],
                linestyle,
                color=color,
                linewidth=linewidth,
                alpha=0.9 if model_family == "neutral_epcsaft_parity" else 0.65,
            )
    apply_pressure_axes(ax, title=title)
    ax.set_xlim(*_data_xlim(pressure_results, "CO2_loading"))
    ax.set_ylim(1.0e-3, 2.0e3)
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
            label="Jou data",
        ),
        Line2D(
            [0],
            [0],
            linestyle=LEGACY_PCSAFT_LINESTYLE,
            color="0.25",
            linewidth=REFERENCE_LINEWIDTH,
            label="Legacy PC-SAFT",
        ),
        Line2D(
            [0],
            [0],
            linestyle=EPCSAFT_NEUTRAL_LINESTYLE,
            color="0.25",
            linewidth=MODEL_LINEWIDTH,
            label="Neutral ePC-SAFT parity",
        ),
    ]
    temperature_legend = ax.legend(
        handles=temperature_handles,
        title="Temperature",
        ncol=1,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
    )
    ax.add_artist(temperature_legend)
    ax.legend(handles=role_handles, title="Role", ncol=1, loc="lower left", bbox_to_anchor=(1.02, 0.0))
    fig.subplots_adjust(right=0.72)
    png = OUT_DIR / "phase1_pressure_vs_loading.png"
    svg = OUT_DIR / "phase1_pressure_vs_loading.svg"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    normalize_svg(svg)
    plt.close(fig)
    write_mpl_sidecar(
        OUT_DIR / "phase1_pressure_vs_loading.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        title=title,
        description=description,
        style_source="analyses/phase1_smith_missen_baseline/scripts/render_figures.py",
    )


def plot_speciation(speciation_results: pd.DataFrame) -> None:
    title = "Phase 1 Smith-Missen baseline speciation reproduction"
    description = (
        "Measured 30 wt% MEA speciation points at 20 C and 40 C are compared against the retained ideal/apparent "
        "Smith-Missen baseline for the major apparent species. Trace-species diagnostics are reported in the metrics table."
    )
    temperatures = sorted(speciation_results["temperature_C"].dropna().unique())
    fig, axes = plt.subplots(1, len(temperatures), figsize=PHASE1_SPECIATION_FIGSIZE, sharey=True)
    if len(temperatures) == 1:
        axes = [axes]
    xlim = _data_xlim(speciation_results, "CO2_loading")
    for ax, temperature_C in zip(axes, temperatures):
        subset = speciation_results[speciation_results["temperature_C"] == temperature_C]
        for species in MAJOR_SPECIATION_SPECIES:
            species_df = subset[subset["species"] == species].sort_values("CO2_loading")
            if species_df.empty:
                continue
            color = species_color(species)
            ax.semilogy(
                species_df["CO2_loading"],
                species_df["model_mole_fraction"],
                SPECIATION_MODEL_LINESTYLE,
                color=color,
                linewidth=MODEL_LINEWIDTH,
            )
            ax.semilogy(
                species_df["CO2_loading"],
                species_df["observed_mole_fraction"],
                SPECIATION_TARGET_MARKER,
                color=color,
                alpha=SPECIATION_TARGET_ALPHA,
                markersize=SPECIATION_TARGET_MARKERSIZE,
                linestyle="none",
            )
        ax.set_xlim(*xlim)
        ax.set_ylim(1.0e-3, 2.0e-1)
        ax.set_yscale("log")
        ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
        if ax is axes[0]:
            ax.set_ylabel("Mole fraction")
        finish_axes(ax, title=f"{temperature_C:g} C")
    species_handles = [
        Line2D(
            [0],
            [0],
            color=species_color(species),
            linestyle=SPECIATION_MODEL_LINESTYLE,
            marker=SPECIATION_TARGET_MARKER,
            markersize=SPECIATION_TARGET_MARKERSIZE,
            linewidth=MODEL_LINEWIDTH,
            label=species_label(species),
        )
        for species in MAJOR_SPECIATION_SPECIES
    ]
    fig.suptitle(title, y=0.98, fontsize=13, fontweight="semibold")
    fig.legend(
        handles=species_handles,
        title="Lines are model curves; markers are reference data",
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.82, bottom=0.26, wspace=0.12)
    png = OUT_DIR / "phase1_speciation_vs_loading.png"
    svg = OUT_DIR / "phase1_speciation_vs_loading.svg"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    normalize_svg(svg)
    plt.close(fig)
    write_mpl_sidecar(
        OUT_DIR / "phase1_speciation_vs_loading.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        title=title,
        description=description,
        style_source="analyses/phase1_smith_missen_baseline/scripts/render_figures.py",
    )


def main() -> int:
    pressure_results, speciation_results = _write_curated_tables()
    plot_pressure(pressure_results)
    plot_speciation(speciation_results)
    print(f"Phase 1 curated artifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
