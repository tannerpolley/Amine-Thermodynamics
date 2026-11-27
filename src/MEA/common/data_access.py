from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from .config import CANONICAL_MEA_WEIGHT_FRACTION, DATA_ROOT



def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source_hashes(source_hashes: Mapping[str, object], *, repo_root: Path) -> dict[str, str]:
    root = repo_root.resolve()
    verified: dict[str, str] = {}
    for source_path, expected in source_hashes.items():
        path = (root / source_path).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise RuntimeError(f"Regression readiness source escapes repository root: {source_path}") from exc
        if not path.is_file():
            raise RuntimeError(f"Regression readiness source is missing: {source_path}")
        actual = _sha256(path)
        if actual != str(expected):
            raise RuntimeError(
                f"Regression readiness source hash drift for {source_path}: expected {expected}, actual {actual}"
            )
        verified[str(source_path)] = actual
    return verified


def load_speciation_data(
    *,
    temperature_C: float,
    mea_weight_fraction: float = CANONICAL_MEA_WEIGHT_FRACTION,
) -> pd.DataFrame:
    df = pd.read_csv(DATA_ROOT / "observations" / "liquid_speciation" / "Combined_ChEq.csv")
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
    df = pd.read_csv(DATA_ROOT / "observations" / "vapor_liquid_equilibrium" / "Jou_1995_VLE.csv")
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
    df = pd.read_csv(DATA_ROOT / "observations" / "vapor_liquid_equilibrium" / "Combined_VLE.csv")
    required_columns = {
        "row_id",
        "source_key",
        "source_file",
        "source_row",
        "MEA_weight_fraction",
        "temperature",
        "CO2_loading",
        "CO2_pressure",
        "paper",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise RuntimeError(f"Canonical VLE data set is missing columns: {sorted(missing_columns)}")
    filtered = df[
        (df["temperature"] == temperature_C)
        & (df["MEA_weight_fraction"] == mea_weight_fraction)
    ]
    if loading_max is not None:
        filtered = filtered[filtered["CO2_loading"] < loading_max]
    return filtered.sort_values("CO2_loading")
