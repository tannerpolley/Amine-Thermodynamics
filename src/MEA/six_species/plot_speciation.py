from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MEA.common.config import (
    CANONICAL_MEA_WEIGHT_FRACTION,
    CANONICAL_TEMPERATURE_C,
    CANONICAL_TEMPERATURE_K,
    SIX_SPECIES_ALPHA_GRID,
)
from MEA.common.data_access import load_speciation_data as load_measured_speciation_data
from MEA.common.plot_export import default_output_dir
from MEA.common.plot_export import save_plot
from MEA.common.plot_style import (
    SPECIATION_FIGSIZE,
    SPECIATION_MODEL_LINESTYLE,
    SPECIATION_TARGET_ALPHA,
    SPECIATION_TARGET_MARKER,
    SPECIATION_TARGET_MARKERSIZE,
    apply_speciation_axes,
    species_color,
    species_label,
)
from MEA.common.reporting import write_csv_report
from MEA.six_species.chemistry import LEGACY_SPECIES_6, legacy_true_mole_fractions


TEMPERATURE_C = CANONICAL_TEMPERATURE_C
TEMPERATURE_K = CANONICAL_TEMPERATURE_K
MEA_WEIGHT_FRACTION = CANONICAL_MEA_WEIGHT_FRACTION
ALPHA_GRID = SIX_SPECIES_ALPHA_GRID
PLOT_SPECIES = LEGACY_SPECIES_6 + ("MEA + MEAH+",)
DATA_SPECIES_MAP = {
    "CO2": "CO2",
    "MEA": "MEA",
    "MEAH+": "MEAH^+",
    "MEACOO-": "MEACOO^-",
    "HCO3-": "HCO3^-",
    "MEA + MEAH+": "MEA + MEAH^+",
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
    return load_measured_speciation_data(
        temperature_C=TEMPERATURE_C,
        mea_weight_fraction=MEA_WEIGHT_FRACTION,
    )


def plot_legacy_speciation(curves: pd.DataFrame, data: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=SPECIATION_FIGSIZE)
    loading_min = float(data["CO2_loading"].min()) if not data.empty else float(curves["CO2_loading"].min())
    loading_max = min(0.8, float(data["CO2_loading"].max()) if not data.empty else float(curves["CO2_loading"].max()))
    visible_curves = curves[(curves["CO2_loading"] >= loading_min) & (curves["CO2_loading"] <= loading_max)]
    snapshot_rows = []

    for species in PLOT_SPECIES:
        color = species_color(species)
        ax.semilogy(
            visible_curves["CO2_loading"],
            visible_curves[species],
            SPECIATION_MODEL_LINESTYLE,
            color=color,
            label=species_label(species),
        )
        for row in visible_curves[["CO2_loading", species]].to_dict("records"):
            snapshot_rows.append({"source": "model", "species": species, "CO2_loading": row["CO2_loading"], "mole_fraction": row[species]})
        data_column = DATA_SPECIES_MAP.get(species)
        if data_column in data:
            measured = data[["CO2_loading", data_column]].dropna()
            measured = measured[(measured["CO2_loading"] >= loading_min) & (measured["CO2_loading"] <= loading_max)]
            if not measured.empty:
                ax.semilogy(
                    measured["CO2_loading"],
                    measured[data_column],
                    SPECIATION_TARGET_MARKER,
                    color=color,
                    alpha=SPECIATION_TARGET_ALPHA,
                    markersize=SPECIATION_TARGET_MARKERSIZE,
                )
                for row in measured.to_dict("records"):
                    snapshot_rows.append({"source": "reference", "species": species, "CO2_loading": row["CO2_loading"], "mole_fraction": row[data_column]})

    apply_speciation_axes(ax)
    ax.legend(loc="lower center", ncol=2)
    fig.tight_layout()
    write_csv_report(default_output_dir(__file__) / "speciation_plot_data.csv", snapshot_rows)
    return save_plot(fig, __file__, "speciation")


def main() -> int:
    curves = compute_legacy_speciation_grid()
    data = load_speciation_data()
    plot_path = plot_legacy_speciation(curves, data)
    print(f"Legacy six-species speciation plot: {plot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
