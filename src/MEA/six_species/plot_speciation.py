from __future__ import annotations

import pandas as pd

from MEA.common.config import (
    CANONICAL_MEA_WEIGHT_FRACTION,
    CANONICAL_TEMPERATURE_C,
    CANONICAL_TEMPERATURE_K,
    SIX_SPECIES_ALPHA_GRID,
)
from MEA.common.data_access import load_speciation_data as load_measured_speciation_data
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
