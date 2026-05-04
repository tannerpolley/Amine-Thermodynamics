from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from legacy_chemical_equilibrium import LEGACY_SPECIES_6, legacy_true_mole_fractions
from plot_export import save_plot


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data" / "MEA"
TEMPERATURE_C = 40.0
TEMPERATURE_K = TEMPERATURE_C + 273.15
MEA_WEIGHT_FRACTION = 0.3
ALPHA_GRID = np.linspace(0.002, 0.8, 101)
PLOT_SPECIES = LEGACY_SPECIES_6 + ("MEA + MEAH+",)
DATA_SPECIES_MAP = {
    "CO2": "CO2",
    "MEA": "MEA",
    "MEAH+": "MEAH^+",
    "MEACOO-": "MEACOO^-",
    "HCO3-": "HCO3^-",
    "MEA + MEAH+": "MEA + MEAH^+",
}
PLOT_LABELS = {
    "CO2": "$CO_2$",
    "MEA": "$MEA$",
    "H2O": "$H_2O$",
    "MEAH+": "$MEAH^+$",
    "MEACOO-": "$MEACOO_-$",
    "HCO3-": "$HCO_3^-$",
    "MEA + MEAH+": "$MEA + MEAH^+$",
}


def compute_legacy_speciation_grid() -> pd.DataFrame:
    rows = []
    for loading in ALPHA_GRID:
        x = legacy_true_mole_fractions(float(loading), MEA_WEIGHT_FRACTION, TEMPERATURE_K)
        row = {
            "temperature_C": TEMPERATURE_C,
            "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
            "CO2_loading": float(loading),
        }
        row.update({species: float(x[idx]) for idx, species in enumerate(LEGACY_SPECIES_6)})
        row["MEA + MEAH+"] = row["MEA"] + row["MEAH+"]
        rows.append(row)
    return pd.DataFrame(rows)


def load_speciation_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_ROOT / "ChEq" / "Combined_ChEq.csv")
    return df[
        (df["temperature"] == TEMPERATURE_C)
        & (df["MEA_weight_fraction"] == MEA_WEIGHT_FRACTION)
    ].sort_values("CO2_loading")


def plot_legacy_speciation(curves: pd.DataFrame, data: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = {
        "CO2": "tab:green",
        "MEA": "tab:blue",
        "MEAH+": "tab:olive",
        "MEACOO-": "tab:red",
        "HCO3-": "tab:cyan",
        "MEA + MEAH+": "tab:pink",
    }

    for species in PLOT_SPECIES:
        if species == "H2O":
            continue
        color = colors[species]
        ax.semilogy(
            curves["CO2_loading"],
            curves[species],
            "--",
            color=color,
            label=PLOT_LABELS[species],
        )
        data_column = DATA_SPECIES_MAP.get(species)
        if data_column in data:
            measured = data[["CO2_loading", data_column]].dropna()
            if not measured.empty:
                ax.semilogy(
                    measured["CO2_loading"],
                    measured[data_column],
                    "o",
                    color=color,
                    markersize=4,
                )

    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_xlim(0.0, 0.8)
    ax.set_ylim(1e-8, 1.0)
    ax.set_xticks(np.linspace(0.0, 0.8, 9))
    ax.set_yticks(np.logspace(-8, 0, 9))
    ax.legend(loc="lower center", ncol=2)
    fig.tight_layout()
    return save_plot(fig, __file__)


def main() -> int:
    curves = compute_legacy_speciation_grid()
    data = load_speciation_data()
    plot_path = plot_legacy_speciation(curves, data)
    print(f"Legacy six-species speciation plot: {plot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
