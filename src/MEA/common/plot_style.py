from __future__ import annotations

from collections.abc import Iterable

import numpy as np


PRESSURE_FIGSIZE = (10, 7)
SPECIATION_FIGSIZE = (10, 7)
PRESSURE_XLIM = (0.0, 0.8)
PRESSURE_YLIM = (1.0e-4, 5.0e3)
SPECIATION_XLIM = (0.0, 0.8)
SPECIATION_YLIM = (1.0e-12, 1.0)

JOU_TEMPERATURE_COLORS: dict[int, str] = {
    40: "tab:blue",
    60: "tab:orange",
    80: "tab:green",
    100: "tab:red",
    120: "tab:purple",
}

JOU_DATA_MARKER = "x"
LEGACY_PCSAFT_LINESTYLE = ":"
EPCSAFT_NEUTRAL_LINESTYLE = "-"
EPCSAFT_IONIC_LINESTYLE = "-"
SPECIATION_MODEL_LINESTYLE = "--"
SPECIATION_TARGET_MARKER = "o"
SPECIATION_TARGET_ALPHA = 0.55
SPECIATION_TARGET_MARKERSIZE = 5

TRUE_SPECIES_COLORS: dict[str, str] = {
    "CO2": "tab:green",
    "MEA": "tab:blue",
    "H2O": "tab:gray",
    "MEAH+": "tab:orange",
    "MEAH^+": "tab:orange",
    "MEACOO-": "tab:red",
    "MEACOO^-": "tab:red",
    "HCO3-": "tab:cyan",
    "HCO3^-": "tab:cyan",
    "CO3^2-": "tab:purple",
    "H3O+": "tab:brown",
    "OH-": "tab:olive",
    "MEA + MEAH+": "tab:pink",
    "MEA + MEAH^+": "tab:pink",
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


def temperature_color(temperature_C: float | int) -> str:
    return JOU_TEMPERATURE_COLORS[int(round(float(temperature_C)))]


def temperature_color_items(temperatures_C: Iterable[float | int]) -> list[tuple[float | int, str]]:
    return [(temperature_C, temperature_color(temperature_C)) for temperature_C in temperatures_C]


def species_color(species: str) -> str:
    return TRUE_SPECIES_COLORS[species]


def species_label(species: str) -> str:
    return TRUE_SPECIES_LABELS.get(species, species)


def apply_pressure_axes(ax, *, ylabel: str = "CO2 partial pressure, kPa") -> None:
    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel(ylabel)
    ax.set_xlim(*PRESSURE_XLIM)
    ax.set_ylim(*PRESSURE_YLIM)
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.25)


def apply_speciation_axes(ax) -> None:
    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_xlim(*SPECIATION_XLIM)
    ax.set_ylim(*SPECIATION_YLIM)
    ax.set_xticks(np.linspace(SPECIATION_XLIM[0], SPECIATION_XLIM[1], 9))
    ax.set_yticks(np.logspace(-12, 0, 13))
    ax.grid(True, which="both", alpha=0.25)
