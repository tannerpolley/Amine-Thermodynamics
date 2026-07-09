from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.config import JOU_TEMPERATURES_C
from MEA.common.plot_style import (
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    LEGACY_PCSAFT_LINESTYLE,
    MODEL_LINEWIDTH,
    PRESSURE_FIGSIZE,
    SPECIATION_FIGSIZE,
    SPECIATION_MODEL_LINESTYLE,
    SPECIATION_TARGET_ALPHA,
    SPECIATION_TARGET_MARKER,
    SPECIATION_TARGET_MARKERSIZE,
    apply_pressure_axes,
    apply_speciation_axes,
    save_figure_bundle,
    species_color,
    species_label,
    temperature_color,
    write_mpl_sidecar,
)
from MEA.six_species.plot_speciation import DATA_SPECIES_MAP, PLOT_SPECIES

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
PRESSURE_DIR = ANALYSIS_DIR / "results" / "pressure"
SPECIATION_DIR = ANALYSIS_DIR / "results" / "speciation"


def require(path: Path) -> Path:
    if not path.exists():
        raise RuntimeError(f"Missing {path}. Run analyses/phase1/six_species_baseline/scripts/generate_data.py first.")
    return path


def render_pressure() -> Path:
    metrics = pd.read_csv(require(PROCESSED_DIR / "legacy_pcsaft_jou_fit_metrics.csv"))
    summary = pd.read_csv(require(PROCESSED_DIR / "legacy_pcsaft_jou_fit_summary.csv"))
    curves = pd.read_csv(require(PROCESSED_DIR / "legacy_pcsaft_jou_fit_curves.csv"))
    PRESSURE_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(PRESSURE_DIR / "legacy_pcsaft_jou_fit_metrics.csv", index=False)
    summary.to_csv(PRESSURE_DIR / "legacy_pcsaft_jou_fit_summary.csv", index=False)
    curves.to_csv(PRESSURE_DIR / "legacy_pcsaft_jou_fit_curves.csv", index=False)

    title = "Six-species PC-SAFT reproduction against Jou $CO_2$ pressure data"
    description = "Recomputed six-species legacy PC-SAFT curves are compared against Jou et al. 30 wt% MEA carbon-dioxide partial-pressure data at five temperatures."
    fig, ax = plt.subplots(figsize=PRESSURE_FIGSIZE)
    for temperature_C in JOU_TEMPERATURES_C:
        color = temperature_color(temperature_C)
        t_data = metrics[metrics["temperature_C"] == temperature_C].sort_values("CO2_loading")
        t_curve = curves[curves["temperature_C"] == temperature_C].sort_values("CO2_loading")
        if t_data.empty or t_curve.empty:
            continue
        ax.plot(t_data["CO2_loading"], t_data["observed_CO2_pressure_kPa"], linestyle="none", marker=JOU_DATA_MARKER, markersize=JOU_DATA_MARKERSIZE, color=color, alpha=0.9, label=f"{temperature_C} C Jou data")
        summary_row = summary[summary["temperature_C"] == temperature_C].iloc[0]
        ax.plot(t_curve["CO2_loading"], t_curve["pred_CO2_pressure_kPa"], LEGACY_PCSAFT_LINESTYLE, color=color, linewidth=MODEL_LINEWIDTH, label=f"{temperature_C} C PC-SAFT, med |log10 err|={summary_row['median_abs_log10_error']:.2f}")
    apply_pressure_axes(ax, title=title)
    ax.legend(ncol=2, title="Temperature and role")
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(fig, PRESSURE_DIR / "legacy_pcsaft_jou_recomputed_fit")
    plt.close(fig)
    write_mpl_sidecar(
        PRESSURE_DIR / "legacy_pcsaft_jou_recomputed_fit.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
    )
    return png


def render_speciation() -> Path:
    curves = pd.read_csv(require(PROCESSED_DIR / "six_species_speciation_curves.csv"))
    data = pd.read_csv(require(PROCESSED_DIR / "six_species_speciation_reference.csv"))
    SPECIATION_DIR.mkdir(parents=True, exist_ok=True)
    title = "Six-species chemical-equilibrium speciation at 40 C"
    description = "Six-species legacy chemical-equilibrium model curves and measured true-species speciation points are shown on a shared semilog mole-fraction axis."
    fig, ax = plt.subplots(figsize=SPECIATION_FIGSIZE)
    loading_min = float(data["CO2_loading"].min()) if not data.empty else float(curves["CO2_loading"].min())
    loading_max = min(0.8, float(data["CO2_loading"].max()) if not data.empty else float(curves["CO2_loading"].max()))
    visible_curves = curves[(curves["CO2_loading"] >= loading_min) & (curves["CO2_loading"] <= loading_max)]
    snapshot_rows = []
    for species in PLOT_SPECIES:
        color = species_color(species)
        ax.semilogy(visible_curves["CO2_loading"], visible_curves[species], SPECIATION_MODEL_LINESTYLE, color=color, linewidth=MODEL_LINEWIDTH, label=species_label(species))
        for row in visible_curves[["CO2_loading", species]].to_dict("records"):
            snapshot_rows.append({"source": "model", "species": species, "CO2_loading": row["CO2_loading"], "mole_fraction": row[species]})
        data_column = DATA_SPECIES_MAP.get(species)
        if data_column in data:
            measured = data[["CO2_loading", data_column]].dropna()
            measured = measured[(measured["CO2_loading"] >= loading_min) & (measured["CO2_loading"] <= loading_max)]
            if not measured.empty:
                ax.semilogy(measured["CO2_loading"], measured[data_column], SPECIATION_TARGET_MARKER, color=color, alpha=SPECIATION_TARGET_ALPHA, markersize=SPECIATION_TARGET_MARKERSIZE)
                for row in measured.to_dict("records"):
                    snapshot_rows.append({"source": "reference", "species": species, "CO2_loading": row["CO2_loading"], "mole_fraction": row[data_column]})
    pd.DataFrame(snapshot_rows).to_csv(SPECIATION_DIR / "speciation_plot_data.csv", index=False)
    apply_speciation_axes(ax, title=title)
    ax.legend(loc="lower center", ncol=2, title="Model curves; markers are reference data")
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(fig, SPECIATION_DIR / "speciation")
    plt.close(fig)
    write_mpl_sidecar(
        SPECIATION_DIR / "speciation.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
    )
    return png


def main() -> int:
    print(f"Six-species pressure plot: {render_pressure()}")
    print(f"Six-species speciation plot: {render_speciation()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
