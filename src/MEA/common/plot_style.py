from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib as mpl
import numpy as np


PRESSURE_FIGSIZE = (10, 7)
SPECIATION_FIGSIZE = (10, 7)
PRESSURE_XLIM = (0.0, 0.8)
PRESSURE_YLIM = (1.0e-4, 5.0e3)
SPECIATION_XLIM = (0.0, 0.8)
SPECIATION_YLIM = (1.0e-14, 1.0)

JOU_TEMPERATURE_COLORS: dict[int, str] = {
    40: "#1f5aa6",
    60: "#d47a00",
    80: "#16805a",
    100: "#b6312c",
    120: "#6f4aa8",
}

JOU_DATA_MARKER = "x"
JOU_DATA_MARKERSIZE = 6
MODEL_LINEWIDTH = 2.2
REFERENCE_LINEWIDTH = 1.7
LEGACY_PCSAFT_LINESTYLE = ":"
EPCSAFT_NEUTRAL_LINESTYLE = "-"
EPCSAFT_IONIC_LINESTYLE = "-"
SPECIATION_MODEL_LINESTYLE = "--"
SPECIATION_TARGET_MARKER = "o"
SPECIATION_TARGET_ALPHA = 0.78
SPECIATION_TARGET_MARKERSIZE = 6.8

TRUE_SPECIES_COLORS: dict[str, str] = {
    "CO2": "#16805a",
    "MEA": "#1f5aa6",
    "H2O": "#707070",
    "MEAH+": "#bcbd22",
    "MEAH^+": "#bcbd22",
    "MEACOO-": "#d62728",
    "MEACOO^-": "#d62728",
    "HCO3-": "#17becf",
    "HCO3^-": "#17becf",
    "CO3^2-": "#9467bd",
    "H3O+": "#8c564b",
    "OH-": "#7f7f7f",
    "MEA + MEAH+": "#e377c2",
    "MEA + MEAH^+": "#e377c2",
}

TRUE_SPECIES_LABELS: dict[str, str] = {
    "CO2": "$CO_2$",
    "MEA": "$MEA$",
    "H2O": "$H_2O$",
    "MEAH+": "$MEAH^+$",
    "MEAH^+": "$MEAH^+$",
    "MEACOO-": "$MEACOO^-$",
    "MEACOO^-": "$MEACOO^-$",
    "HCO3-": "$HCO_3^-$",
    "HCO3^-": "$HCO_3^-$",
    "CO3^2-": "$CO_3^{2-}$",
    "H3O+": "$H_3O^+$",
    "OH-": "$OH^-$",
    "MEA + MEAH+": "$MEA + MEAH^+$",
    "MEA + MEAH^+": "$MEA + MEAH^+$",
}


def apply_plot_theme() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Cambria", "Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "dejavuserif",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "semibold",
            "axes.titlepad": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 13,
            "legend.frameon": False,
            "legend.fontsize": 8.5,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "savefig.facecolor": "white",
        }
    )


def temperature_color(temperature_C: float | int) -> str:
    return JOU_TEMPERATURE_COLORS[int(round(float(temperature_C)))]


def temperature_color_items(temperatures_C: Iterable[float | int]) -> list[tuple[float | int, str]]:
    return [(temperature_C, temperature_color(temperature_C)) for temperature_C in temperatures_C]


def species_color(species: str) -> str:
    return TRUE_SPECIES_COLORS[species]


def species_label(species: str) -> str:
    return TRUE_SPECIES_LABELS.get(species, species)


def finish_axes(ax, *, title: str | None = None, grid_axis: str = "both") -> None:
    apply_plot_theme()
    if title:
        ax.set_title(title)
    ax.grid(True, which="major", axis=grid_axis, alpha=0.22, linewidth=0.8)
    ax.tick_params(length=4.0, width=0.8)


def apply_pressure_axes(ax, *, ylabel: str = "$CO_2$ partial pressure, kPa", title: str | None = None) -> None:
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel(ylabel)
    ax.set_xlim(*PRESSURE_XLIM)
    ax.set_ylim(*PRESSURE_YLIM)
    ax.set_yscale("log")
    finish_axes(ax, title=title)


def apply_speciation_axes(ax, *, title: str | None = None) -> None:
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_xlim(*SPECIATION_XLIM)
    ax.set_ylim(*SPECIATION_YLIM)
    ax.set_yscale("log")
    ax.set_xticks(np.linspace(SPECIATION_XLIM[0], SPECIATION_XLIM[1], 9))
    ax.set_yticks(np.logspace(-12, 0, 13))
    finish_axes(ax, title=title)


def write_mpl_sidecar(
    path: Path,
    *,
    png_name: str,
    svg_name: str,
    pdf_name: str | None = None,
    title: str,
    description: str,
    style_source: str = "src/MEA/common/plot_style.py",
    dpi: int = 300,
) -> None:
    lines = [
        "figure:",
        f"  title: {title}",
        f"  description: {description}",
        f"  png: {png_name}",
        f"  svg: {svg_name}",
    ]
    if pdf_name is not None:
        lines.append(f"  pdf: {pdf_name}")
    lines.extend(
        [
            f"  dpi: {dpi}",
            "style:",
            f"  source: {style_source}",
            "",
        ]
    )
    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def save_figure_bundle(fig: Any, stem_path: Path, *, dpi: int = 300) -> tuple[Path, Path, Path]:
    png = stem_path.with_suffix(".png")
    svg = stem_path.with_suffix(".svg")
    pdf = stem_path.with_suffix(".pdf")
    fig.savefig(png, dpi=dpi, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    svg_lines = svg.read_text(encoding="utf-8").splitlines()
    svg.write_text("\n".join(line.rstrip() for line in svg_lines) + "\n", encoding="utf-8")
    return png, svg, pdf


apply_plot_theme()
