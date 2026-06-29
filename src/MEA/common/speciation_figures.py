from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from MEA.common.analysis_io import normalize_svg
from MEA.common.plot_style import (
    MODEL_LINEWIDTH,
    SPECIATION_MODEL_LINESTYLE,
    SPECIATION_TARGET_ALPHA,
    SPECIATION_TARGET_MARKER,
    SPECIATION_TARGET_MARKERSIZE,
    SPECIATION_XLIM,
    SPECIATION_YLIM,
    apply_plot_theme,
    species_color,
    species_label,
    save_figure_bundle,
    write_mpl_sidecar,
)

SPECIES_PLOT_ORDER = (
    "CO2",
    "MEA",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
    "MEA + MEAH+",
)


def _prepare_axes(ax, *, ylabel: str = "True-species mole fraction") -> None:
    apply_plot_theme()
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xlim(*SPECIATION_XLIM)
    ax.set_ylim(*SPECIATION_YLIM)
    ax.set_yscale("log")
    ax.set_xticks(np.linspace(SPECIATION_XLIM[0], SPECIATION_XLIM[1], 11))
    ax.set_yticks(np.logspace(-14, 0, 15))
    ax.grid(False)
    ax.tick_params(axis="both", which="major", labelsize=10.5, length=4.5, width=0.9)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.9)
        spine.set_color("black")


def _ordered_present_species(
    curves: pd.DataFrame,
    points: pd.DataFrame,
    plot_order: Sequence[str] | None,
) -> list[str]:
    present = set(curves["species"].dropna().astype(str)) | set(points["species"].dropna().astype(str))
    ordered = [species for species in (plot_order or SPECIES_PLOT_ORDER) if species in present]
    extras = sorted(present.difference(ordered))
    return [*ordered, *extras]


def write_speciation_plot(
    *,
    curve_frame: pd.DataFrame,
    point_frame: pd.DataFrame,
    output_dir: Path,
    stem: str,
    title: str,
    description: str,
    style_source: str,
    temperature_C: float | None = None,
    plot_order: Sequence[str] | None = None,
    ylabel: str = "True-species mole fraction",
    dpi: int = 300,
) -> tuple[Path, Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    curves = curve_frame.copy()
    points = point_frame.copy()
    if temperature_C is not None:
        curves = curves[np.isclose(curves["temperature_C"].astype(float), float(temperature_C))]
        points = points[np.isclose(points["temperature_C"].astype(float), float(temperature_C))]

    ordered_species = _ordered_present_species(curves, points, plot_order)
    curve_species = set(curves["species"].dropna().astype(str))
    point_species = set(points["species"].dropna().astype(str))

    plot_rows: list[dict[str, object]] = []
    fig, ax = plt.subplots(figsize=(11.3, 7.6))
    for species in ordered_species:
        color = species_color(species)
        species_curve = curves[curves["species"] == species].sort_values("CO2_loading")
        if not species_curve.empty:
            ax.semilogy(
                species_curve["CO2_loading"],
                species_curve["mole_fraction"].clip(lower=1.0e-30),
                SPECIATION_MODEL_LINESTYLE,
                color=color,
                linewidth=MODEL_LINEWIDTH,
                solid_capstyle="round",
            )
            for row in species_curve.to_dict("records"):
                plot_rows.append(
                    {
                        "role": "curve",
                        "temperature_C": row["temperature_C"],
                        "species": species,
                        "CO2_loading": row["CO2_loading"],
                        "mole_fraction": row["mole_fraction"],
                    }
                )
        species_points = points[points["species"] == species].sort_values("CO2_loading")
        if not species_points.empty:
            ax.semilogy(
                species_points["CO2_loading"],
                species_points["mole_fraction"].clip(lower=1.0e-30),
                SPECIATION_TARGET_MARKER,
                color=color,
                alpha=SPECIATION_TARGET_ALPHA,
                markersize=SPECIATION_TARGET_MARKERSIZE,
                markeredgewidth=0.0,
                linestyle="none",
            )
            for row in species_points.to_dict("records"):
                plot_rows.append(
                    {
                        "role": "reference_point",
                        "temperature_C": row["temperature_C"],
                        "species": species,
                        "CO2_loading": row["CO2_loading"],
                        "mole_fraction": row["mole_fraction"],
                    }
                )

    _prepare_axes(ax, ylabel=ylabel)
    handles = []
    for species in ordered_species:
        has_curve = species in curve_species
        has_points = species in point_species
        handles.append(
            Line2D(
                [0],
                [0],
                linestyle=SPECIATION_MODEL_LINESTYLE if has_curve else "none",
                marker=SPECIATION_TARGET_MARKER if has_points and not has_curve else None,
                color=species_color(species),
                linewidth=MODEL_LINEWIDTH if has_curve else 0.0,
                markersize=SPECIATION_TARGET_MARKERSIZE if has_points and not has_curve else 0.0,
                markeredgewidth=0.0,
                label=species_label(species),
            )
        )
    legend = ax.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=1,
        fontsize=9.0,
        frameon=True,
        fancybox=True,
        borderpad=0.45,
        handlelength=2.3,
    )
    legend.get_frame().set_alpha(0.88)
    fig.subplots_adjust(left=0.11, right=0.985, top=0.985, bottom=0.12)
    figure_stem = output_dir / stem
    png = figure_stem.with_suffix(".png")
    svg = figure_stem.with_suffix(".svg")
    pdf = figure_stem.with_suffix(".pdf")
    sidecar = output_dir / f"{stem}.mpl.yaml"
    plot_data = output_dir / f"{stem}_plot_data.csv"
    pd.DataFrame(plot_rows).to_csv(plot_data, index=False)
    save_figure_bundle(fig, figure_stem, dpi=dpi)
    normalize_svg(svg)
    plt.close(fig)
    write_mpl_sidecar(
        sidecar,
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        style_source=style_source,
        dpi=dpi,
    )
    return png, svg, pdf, sidecar
