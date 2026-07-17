from __future__ import annotations

import numpy as np
import pandas as pd

from MEA.common.config import (
    CANONICAL_MEA_WEIGHT_FRACTION,
    JOU_TEMPERATURES_C,
)
from MEA.common.data_access import load_jou_vle_data
from MEA.six_species.chemistry import (
    APPARENT_SPECIES_3,
    LEGACY_SPECIES_6,
    collapse_to_apparent_ternary,
    legacy_true_mole_fractions,
)

try:
    from pcsaft import flashTQ
except ImportError as exc:
    raise RuntimeError(
        "The legacy Jou pressure baseline requires the locked pcsaft dependency. Run `uv sync --locked`, then "
        "`uv run python analyses/phase1/six_species_baseline/scripts/generate_data.py`."
    ) from exc


K_CO2_MEA = 0.16
K_CO2_H2O = 0.15
K_MEA_H2O = -0.18
TEMPERATURES_C = JOU_TEMPERATURES_C
EXPECTED_MEDIAN_ABS_LOG10_ERROR = {
    40: 0.39155729207995144,
    60: 0.3060402645017894,
    80: 0.15416556579951093,
    100: 0.05503532221359544,
    120: 0.07842251498018801,
}


def legacy_pcsaft_params() -> dict[str, np.ndarray]:
    return {
        "m": np.array([2.079, 3.0353, 1.9599], dtype=float),
        "s": np.array([2.7852, 3.0435, 2.363], dtype=float),
        "e": np.array([169.21, 277.174, 279.42], dtype=float),
        "vol_a": np.array([0.0, 0.037470, 0.1750], dtype=float),
        "e_assoc": np.array([0.0, 2586.3, 2059.28], dtype=float),
        "k_ij": np.array(
            [
                [0.0, K_CO2_MEA, K_CO2_H2O],
                [K_CO2_MEA, 0.0, K_MEA_H2O],
                [K_CO2_H2O, K_MEA_H2O, 0.0],
            ],
            dtype=float,
        ),
    }


def predict_co2_pressure_kpa(loading: float, mea_weight_fraction: float, temperature_C: float) -> dict[str, object]:
    temperature_K = float(temperature_C) + 273.15
    x6 = legacy_true_mole_fractions(loading, mea_weight_fraction, temperature_K)
    x_liquid = collapse_to_apparent_ternary(x6)
    pressure_pa, _, y_vapor = flashTQ(temperature_K, 0, x_liquid, params=legacy_pcsaft_params())
    y_vapor = np.asarray(y_vapor, dtype=float)
    return {
        "pressure_kPa": float(pressure_pa * y_vapor[0] / 1000.0),
        "total_pressure_Pa": float(pressure_pa),
        "y_vapor": y_vapor,
        "x_apparent_liquid": x_liquid,
        "x6": x6,
    }


def _load_jou_data() -> pd.DataFrame:
    return load_jou_vle_data(mea_weight_fraction=CANONICAL_MEA_WEIGHT_FRACTION)


def compute_jou_metrics() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = _load_jou_data()
    rows = []
    curve_rows = []
    for temperature_C in TEMPERATURES_C:
        t_df = df[df["temperature"] == temperature_C].sort_values("CO2_loading")
        if t_df.empty:
            continue
        loadings = np.linspace(float(t_df["CO2_loading"].iloc[0]), float(t_df["CO2_loading"].iloc[-1]), 21)
        curve_pressures = []
        for loading in loadings:
            pred = predict_co2_pressure_kpa(float(loading), CANONICAL_MEA_WEIGHT_FRACTION, float(temperature_C))
            curve_pressures.append(pred["pressure_kPa"])
            curve_rows.append(
                {
                    "temperature_C": temperature_C,
                    "CO2_loading": loading,
                    "pred_CO2_pressure_kPa": pred["pressure_kPa"],
                    **{
                        f"x6_{name}": float(pred["x6"][i])
                        for i, name in enumerate(LEGACY_SPECIES_6)
                    },
                    **{
                        f"x_apparent_{name}": float(pred["x_apparent_liquid"][i])
                        for i, name in enumerate(APPARENT_SPECIES_3)
                    },
                }
            )

        interp = np.interp(t_df["CO2_loading"].to_numpy(dtype=float), loadings, np.asarray(curve_pressures, dtype=float))
        for data_row, predicted in zip(t_df.to_dict("records"), interp):
            observed = float(data_row["CO2_pressure"])
            log_error = np.log10(predicted / observed) if predicted > 0.0 and observed > 0.0 else np.nan
            rows.append(
                {
                    "temperature_C": temperature_C,
                    "MEA_weight_fraction": float(data_row["MEA_weight_fraction"]),
                    "CO2_loading": float(data_row["CO2_loading"]),
                    "observed_CO2_pressure_kPa": observed,
                    "pred_CO2_pressure_kPa": float(predicted),
                    "log10_pred_over_obs": float(log_error),
                    "abs_log10_error": float(abs(log_error)) if np.isfinite(log_error) else np.nan,
                }
            )

    metrics = pd.DataFrame(rows)
    summary = (
        metrics.groupby("temperature_C")
        .agg(
            n=("abs_log10_error", "size"),
            rmse_kPa=(
                "pred_CO2_pressure_kPa",
                lambda s: float(np.sqrt(np.mean((s - metrics.loc[s.index, "observed_CO2_pressure_kPa"]) ** 2))),
            ),
            mae_kPa=(
                "pred_CO2_pressure_kPa",
                lambda s: float(np.mean(np.abs(s - metrics.loc[s.index, "observed_CO2_pressure_kPa"]))),
            ),
            median_abs_log10_error=("abs_log10_error", "median"),
            median_log10_pred_over_obs=("log10_pred_over_obs", "median"),
        )
        .reset_index()
    )
    summary["expected_legacy_median_abs_log10_error"] = summary["temperature_C"].map(
        EXPECTED_MEDIAN_ABS_LOG10_ERROR
    )
    summary["delta_vs_expected"] = (
        summary["median_abs_log10_error"] - summary["expected_legacy_median_abs_log10_error"]
    )
    return metrics, summary, pd.DataFrame(curve_rows)
