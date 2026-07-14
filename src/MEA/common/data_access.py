from __future__ import annotations

import hashlib
import json

import pandas as pd

from .config import CANONICAL_MEA_WEIGHT_FRACTION, DATA_ROOT


MANIFEST_ROOT = DATA_ROOT / "manifests"
READINESS_SUMMARY = (
    DATA_ROOT.parents[2]
    / "analyses"
    / "phase3"
    / "ionic_epcsaft_regression"
    / "results"
    / "readiness"
    / "regression_readiness_summary.json"
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regression_split_hash() -> str:
    split_path = MANIFEST_ROOT / "grouped_split_manifest.csv"
    summary = load_regression_readiness_summary()
    actual = _sha256(split_path)
    expected = str(summary["split_hash"])
    if actual != expected:
        raise RuntimeError(f"Regression split hash drift: expected {expected}, actual {actual}")
    return actual


def load_regression_readiness_summary() -> dict[str, object]:
    return json.loads(READINESS_SUMMARY.read_text(encoding="utf-8"))


def load_regression_split_manifest(*, target_family: str | None = None) -> pd.DataFrame:
    regression_split_hash()
    frame = pd.read_csv(MANIFEST_ROOT / "grouped_split_manifest.csv", dtype=str, keep_default_na=False)
    required = {
        "target_family",
        "record_id",
        "source_key",
        "group_id",
        "lifecycle_status",
        "split",
        "role",
        "source_path",
        "source_hash",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise RuntimeError(f"Grouped split manifest is missing columns: {sorted(missing)}")
    if target_family is not None:
        frame = frame.loc[frame["target_family"] == target_family].copy()
    for source_path, expected_hash in frame[["source_path", "source_hash"]].drop_duplicates().itertuples(index=False):
        path = DATA_ROOT.parents[2] / source_path
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise RuntimeError(f"Regression source hash drift for {source_path}: expected {expected_hash}, actual {actual_hash}")
    return frame


def load_regression_vle_view() -> pd.DataFrame:
    split = load_regression_split_manifest(target_family="vle_pressure")
    split = split.loc[split["lifecycle_status"] == "active_v1"].copy()
    canonical = pd.read_csv(DATA_ROOT / "VLE" / "Canonical_VLE_Observations.csv", dtype=str, keep_default_na=False)
    identity = canonical.loc[
        canonical["active_view_member"] == "yes",
        ["observation_id", "active_row_id"],
    ]
    membership = split.merge(identity, left_on="record_id", right_on="observation_id", validate="one_to_one")
    active = pd.read_csv(DATA_ROOT / "VLE" / "Combined_VLE.csv")
    view = active.merge(
        membership[["observation_id", "active_row_id", "group_id", "split", "role"]],
        left_on="row_id",
        right_on="active_row_id",
        validate="one_to_one",
    )
    if len(view) != len(active):
        raise RuntimeError(f"Active VLE membership mismatch: manifest={len(view)}, active_view={len(active)}")
    return view.drop(columns=["active_row_id"]).sort_values("row_id").reset_index(drop=True)


def load_regression_speciation_view() -> pd.DataFrame:
    split = load_regression_split_manifest(target_family="speciation")
    split = split.loc[split["lifecycle_status"] == "canonical_eligible"].copy()
    membership = pd.read_csv(
        MANIFEST_ROOT / "speciation_target_membership.csv",
        dtype=str,
        keep_default_na=False,
    )
    states = membership.loc[
        membership["state_id"].isin(split["record_id"]),
        ["state_id", "source_key", "mea_mass_fraction", "temperature_C", "co2_loading_mol_per_mol_mea"],
    ].drop_duplicates()
    states = states.merge(
        split[["record_id", "group_id", "split", "role"]],
        left_on="state_id",
        right_on="record_id",
        validate="one_to_one",
    )

    source_keys = {"Bottinger": "Bottinger2008", "Jakobsen": "Jakobsen2005", "Matin": "Matin2012"}
    active = pd.read_csv(DATA_ROOT / "ChEq" / "Combined_ChEq.csv")
    active["source_key"] = active["source"].map(source_keys)
    if active["source_key"].isna().any():
        unknown = sorted(active.loc[active["source_key"].isna(), "source"].unique())
        raise RuntimeError(f"Unmapped active speciation sources: {unknown}")
    active["_mea"] = active["MEA_weight_fraction"].map(lambda value: f"{float(value):.12g}")
    active["_temperature"] = active["temperature"].map(lambda value: f"{float(value):.12g}")
    active["_loading"] = active["CO2_loading"].map(lambda value: f"{float(value):.12g}")
    states["_mea"] = states["mea_mass_fraction"].map(lambda value: f"{float(value):.12g}")
    states["_temperature"] = states["temperature_C"].map(lambda value: f"{float(value):.12g}")
    states["_loading"] = states["co2_loading_mol_per_mol_mea"].map(lambda value: f"{float(value):.12g}")
    view = active.merge(
        states[["state_id", "source_key", "_mea", "_temperature", "_loading", "group_id", "split", "role"]],
        on=["source_key", "_mea", "_temperature", "_loading"],
        validate="one_to_one",
    )
    if len(view) != len(active):
        raise RuntimeError(f"Active speciation membership mismatch: manifest={len(view)}, active_view={len(active)}")
    return view.drop(columns=["record_id", "_mea", "_temperature", "_loading"], errors="ignore").sort_values("state_id").reset_index(drop=True)


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
