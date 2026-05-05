from __future__ import annotations

import pandas as pd

from .config import CANONICAL_MEA_WEIGHT_FRACTION, DATA_ROOT


def load_speciation_data(
    *,
    temperature_C: float,
    mea_weight_fraction: float = CANONICAL_MEA_WEIGHT_FRACTION,
) -> pd.DataFrame:
    df = pd.read_csv(DATA_ROOT / "ChEq" / "Combined_ChEq.csv")
    return df[
        (df["temperature"] == temperature_C)
        & (df["MEA_weight_fraction"] == mea_weight_fraction)
    ].sort_values("CO2_loading")


def load_jou_vle_data(
    *,
    mea_weight_fraction: float = CANONICAL_MEA_WEIGHT_FRACTION,
    loading_min: float = 0.1,
    loading_max: float = 0.6,
) -> pd.DataFrame:
    df = pd.read_csv(DATA_ROOT / "VLE" / "Jou_1995_VLE.csv")
    return df[
        (df["MEA_weight_fraction"] == mea_weight_fraction)
        & (df["CO2_loading"] > loading_min)
        & (df["CO2_loading"] < loading_max)
    ].copy()


def load_combined_vle_data(
    *,
    temperature_C: float,
    mea_weight_fraction: float = CANONICAL_MEA_WEIGHT_FRACTION,
    loading_max: float | None = None,
) -> pd.DataFrame:
    df = pd.read_csv(DATA_ROOT / "VLE" / "Combined_VLE.csv")
    filtered = df[
        (df["temperature"] == temperature_C)
        & (df["MEA_weight_fraction"] == mea_weight_fraction)
    ]
    if loading_max is not None:
        filtered = filtered[filtered["CO2_loading"] < loading_max]
    return filtered.sort_values("CO2_loading")
