from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D


ANALYSIS_DIR = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_DIR.parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.analysis_io import normalize_svg, read_required_csv  # noqa: E402
from MEA.common.plot_style import (  # noqa: E402
    apply_plot_theme,
    save_figure_bundle,
    species_color,
    species_label,
    write_mpl_sidecar,
)

OUTPUT_DIR = ANALYSIS_DIR / "figures" / "speciation" / "output"
MOLE_FRACTION_PLOT_DATA = OUTPUT_DIR / "canonical_speciation_mole_fraction_grid_plot_data.csv"
LOADED_MOLKG_PLOT_DATA = OUTPUT_DIR / "canonical_speciation_loaded_molkg_grid_plot_data.csv"
WONG_MOLKG_PLOT_DATA = OUTPUT_DIR / "canonical_speciation_wong_source_molkg_plot_data.csv"

GRID_XLIM = (0.0, 1.22)
MOLE_FRACTION_YLIM = (5.0e-5, 2.0e-1)
MOLKG_YLIM = (5.0e-3, 8.0)
SOURCE_MARKERS = {
    "Bottinger2008": "s",
    "Jakobsen2005": "o",
    "Matin2012": "^",
    "Wong2015": "o",
}
SOURCE_LABELS = {
    "Bottinger2008": "Böttinger 2008",
    "Jakobsen2005": "Jakobsen 2005",
    "Matin2012": "Matin 2012",
    "Wong2015": "Wong 2015",
}
SPECIES_ORDER = ["CO2", "MEA", "MEAH+", "MEA + MEAH+", "MEACOO-", "HCO3-", "CO3^2-"]


def _read_plot_data(path: Path) -> pd.DataFrame:
    frame = read_required_csv(path, hint="Run the canonical speciation source generate_data.py script first.")
    numeric = ["temperature_C", "mea_mass_fraction", "mea_mass_percent", "co2_loading_mol_per_mol_mea", "plot_value"]
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["temperature_C", "mea_mass_percent", "co2_loading_mol_per_mol_mea", "plot_value"])


def _style_axes(ax, *, ylim: tuple[float, float]) -> None:
    ax.set_xlim(*GRID_XLIM)
    ax.set_ylim(*ylim)
    ax.set_yscale("log")
    ax.set_xticks(np.arange(0.0, 1.21, 0.3))
    ax.grid(True, which="major", alpha=0.22, linewidth=0.8)
    ax.tick_params(length=4.0, width=0.8, labelsize=9.0)


def _species_handles(species_values: list[str]) -> list[Line2D]:
    return [
        Line2D(
            [0],
            [0],
            color=species_color(species),
            marker="o",
            linestyle="none",
            markersize=6.2,
            label=species_label(species),
        )
        for species in species_values
    ]


def _source_handles(source_values: list[str]) -> list[Line2D]:
    return [
        Line2D(
            [0],
            [0],
            color="#2b2b2b",
            marker=SOURCE_MARKERS[source],
            linestyle="none",
            markersize=6.2,
            label=SOURCE_LABELS[source],
        )
        for source in source_values
    ]


def _plot_grid(frame: pd.DataFrame, *, stem: str, title: str, ylabel: str, ylim: tuple[float, float], description: str) -> tuple[Path, Path, Path, Path]:
    apply_plot_theme()
    panels = (
        frame[["mea_mass_percent", "temperature_C"]]
        .drop_duplicates()
        .sort_values(["mea_mass_percent", "temperature_C"], kind="stable")
        .to_records(index=False)
    )
    panel_keys = [(float(mass_percent), float(temperature_C)) for mass_percent, temperature_C in panels]
    if not panel_keys:
        raise RuntimeError(f"No positive canonical speciation rows are available for {stem}.")

    columns = min(4, len(panel_keys))
    rows = int(np.ceil(len(panel_keys) / columns))
    fig, axes = plt.subplots(
        rows,
        columns,
        figsize=(3.55 * columns, 2.7 * rows),
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    flat_axes = axes.ravel()
    for ax, (mass_percent, temperature_C) in zip(flat_axes, panel_keys, strict=False):
        subset = frame[
            np.isclose(frame["mea_mass_percent"], mass_percent)
            & np.isclose(frame["temperature_C"], temperature_C)
        ].copy()
        for species in SPECIES_ORDER:
            species_rows = subset[subset["species"] == species]
            if species_rows.empty:
                continue
            for source in sorted(species_rows["source_key"].astype(str).unique()):
                source_rows = species_rows[species_rows["source_key"].astype(str) == source]
                ax.plot(
                    source_rows["co2_loading_mol_per_mol_mea"],
                    source_rows["plot_value"],
                    linestyle="none",
                    marker=SOURCE_MARKERS.get(source, "o"),
                    markersize=5.4,
                    markerfacecolor=species_color(species),
                    markeredgecolor="white",
                    markeredgewidth=0.45,
                    alpha=0.88,
                )
        ax.set_title(f"{mass_percent:g} wt% MEA, {temperature_C:g} °C", fontsize=10.5)
        _style_axes(ax, ylim=ylim)
    for ax in flat_axes[len(panel_keys) :]:
        ax.set_axis_off()

    species_values = [species for species in SPECIES_ORDER if species in set(frame["species"].astype(str))]
    source_values = [source for source in SOURCE_LABELS if source in set(frame["source_key"].astype(str))]
    fig.legend(
        handles=_species_handles(species_values),
        loc="lower center",
        bbox_to_anchor=(0.5, 0.045),
        ncol=min(len(species_values), 7),
        frameon=False,
        fontsize=9.0,
    )
    fig.legend(
        handles=_source_handles(source_values),
        loc="lower center",
        bbox_to_anchor=(0.5, 0.005),
        ncol=min(len(source_values), 4),
        frameon=False,
        fontsize=8.6,
    )
    fig.suptitle(title, fontsize=13.5, fontweight="semibold", y=0.985)
    fig.supxlabel("$CO_2$ loading, mol $CO_2$/mol MEA", fontsize=11.0, y=0.102)
    fig.supylabel(ylabel, fontsize=11.0, x=0.012)
    fig.subplots_adjust(left=0.075, right=0.995, top=0.93, bottom=0.18, wspace=0.08, hspace=0.28)
    return _save_bundle(fig, stem=stem, title=title, description=description)


def _plot_wong(frame: pd.DataFrame) -> tuple[Path, Path, Path, Path]:
    apply_plot_theme()
    fig, ax = plt.subplots(figsize=(10.4, 6.8))
    for species in SPECIES_ORDER:
        species_rows = frame[frame["species"] == species].sort_values("co2_loading_mol_per_mol_mea")
        if species_rows.empty:
            continue
        extracted = species_rows[species_rows["row_status"] != "ambiguous"]
        ambiguous = species_rows[species_rows["row_status"] == "ambiguous"]
        if not extracted.empty:
            ax.plot(
                extracted["co2_loading_mol_per_mol_mea"],
                extracted["plot_value"],
                linestyle="none",
                marker="o",
                markersize=6.0,
                color=species_color(species),
                markeredgecolor="white",
                markeredgewidth=0.45,
                alpha=0.9,
            )
        if not ambiguous.empty:
            ax.plot(
                ambiguous["co2_loading_mol_per_mol_mea"],
                ambiguous["plot_value"],
                linestyle="none",
                marker="x",
                markersize=7.2,
                color=species_color(species),
                markeredgewidth=1.3,
                alpha=0.95,
            )
    ax.set_xlim(*GRID_XLIM)
    ax.set_ylim(*MOLKG_YLIM)
    ax.set_yscale("log")
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA", fontsize=11)
    ax.set_ylabel("Reported species concentration, mol/kg", fontsize=11)
    ax.set_title("Wong 2015 Raman speciation, 30 wt% MEA at 30 °C", fontsize=13, fontweight="semibold")
    ax.grid(True, which="major", alpha=0.22, linewidth=0.8)
    species_values = [species for species in SPECIES_ORDER if species in set(frame["species"].astype(str))]
    species_legend = ax.legend(
        handles=_species_handles(species_values),
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        ncol=1,
        frameon=False,
        fontsize=9.0,
    )
    ax.add_artist(species_legend)
    status_handles = [
        Line2D([0], [0], color="#2b2b2b", marker="o", linestyle="none", markersize=6.0, label="extracted"),
        Line2D([0], [0], color="#2b2b2b", marker="x", linestyle="none", markersize=7.2, label="ambiguous"),
    ]
    ax.legend(handles=status_handles, loc="lower left", bbox_to_anchor=(1.01, 0.0), frameon=False, fontsize=9.0)
    fig.subplots_adjust(left=0.1, right=0.82, top=0.92, bottom=0.11)
    return _save_bundle(
        fig,
        stem="canonical_speciation_wong_source_molkg",
        title="Wong 2015 Raman Speciation Source Molkg",
        description="Source-reported Wong 2015 Raman species concentrations digitized from Fig. 8; ambiguous marker rows are shown with crosses.",
    )


def _save_bundle(fig, *, stem: str, title: str, description: str) -> tuple[Path, Path, Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem_path = OUTPUT_DIR / stem
    png, svg, pdf = save_figure_bundle(fig, stem_path)
    normalize_svg(svg)
    sidecar = OUTPUT_DIR / f"{stem}.mpl.yaml"
    write_mpl_sidecar(
        sidecar,
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        style_source="src/MEA/common/plot_style.py",
    )
    plt.close(fig)
    return png, svg, pdf, sidecar


def main() -> int:
    mole_fraction = _read_plot_data(MOLE_FRACTION_PLOT_DATA)
    loaded_molkg = _read_plot_data(LOADED_MOLKG_PLOT_DATA)
    wong_molkg = _read_plot_data(WONG_MOLKG_PLOT_DATA)
    outputs = [
        _plot_grid(
            mole_fraction,
            stem="canonical_speciation_mole_fraction_grid",
            title="Canonical MEA Speciation Sources, Mole-Fraction Basis",
            ylabel="True-species liquid mole fraction",
            ylim=MOLE_FRACTION_YLIM,
            description="Böttinger, Jakobsen, Matin, and Wong source rows from the canonical combined speciation dataset on a liquid mole-fraction basis.",
        ),
        _plot_grid(
            loaded_molkg,
            stem="canonical_speciation_loaded_molkg_grid",
            title="Canonical MEA Speciation Sources, Loaded-Solution mol/kg",
            ylabel="Computed species amount, mol/kg loaded solution",
            ylim=MOLKG_YLIM,
            description="Böttinger, Jakobsen, Matin, and Wong source rows from the canonical combined speciation dataset on a loaded-solution mol/kg basis.",
        ),
        _plot_wong(wong_molkg),
    ]
    for bundle in outputs:
        png, svg, pdf, sidecar = bundle
        print(f"Saved PNG: {png}")
        print(f"Saved SVG: {svg}")
        print(f"Saved PDF: {pdf}")
        print(f"Saved sidecar: {sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
