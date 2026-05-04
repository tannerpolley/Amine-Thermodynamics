from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from legacy_chemical_equilibrium import (
    APPARENT_SPECIES_3,
    LEGACY_SPECIES_6,
    collapse_to_apparent_ternary,
    legacy_true_mole_fractions,
    smoke_check,
)
from plot_export import save_plot


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[0]
DATA_ROOT = REPO_ROOT / "data" / "MEA"
BASELINE_OUT = REPO_ROOT / "out" / "legacy_baseline"
LEGACY_MAIN_CLONE = Path(
    os.environ.get("MEA_LEGACY_PCSAFT_PATH", str(Path(__file__).resolve().parents[2] / "MEA-Thermodynamics-main-clone"))
)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if LEGACY_MAIN_CLONE.exists() and str(LEGACY_MAIN_CLONE) not in sys.path:
    sys.path.insert(0, str(LEGACY_MAIN_CLONE))

try:
    from pcsaft import flashTQ

    PCSAFT_SOURCE = "compiled pcsaft"
except ImportError:
    from pcsaft_models_polley import pcsaft_electrolyte as local_pcsaft_core

    PCSAFT_SOURCE = "repo-local pure Python fallback"

    def flashTQ(t, q, x, params):
        if q != 0:
            raise NotImplementedError("Local PC-SAFT fallback only supports bubble-pressure q=0.")
        x = np.asarray(x, dtype=float)
        bubble_p, y = local_pcsaft_core.pcsaft_bubbleP(
            101325.0,
            x.copy(),
            x,
            np.asarray(params["m"], dtype=float),
            np.asarray(params["s"], dtype=float),
            np.asarray(params["e"], dtype=float),
            float(t),
            k_ij=np.asarray(params["k_ij"], dtype=float),
            e_assoc=np.asarray(params["e_assoc"], dtype=float),
            vol_a=np.asarray(params["vol_a"], dtype=float),
            dipm=np.zeros_like(x, dtype=float),
            dip_num=np.zeros_like(x, dtype=float),
        )
        return float(np.asarray(bubble_p).reshape(-1)[0]), x, np.asarray(y, dtype=float)


K_CO2_MEA = 0.16
K_CO2_H2O = 0.15
K_MEA_H2O = -0.18
TEMPERATURES_C = (40, 60, 80, 100, 120)
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
    df = pd.read_csv(DATA_ROOT / "VLE" / "Jou_1995_VLE.csv")
    return df[(df["MEA_weight_fraction"] == 0.3) & (df["CO2_loading"] > 0.1) & (df["CO2_loading"] < 0.6)].copy()


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
            pred = predict_co2_pressure_kpa(float(loading), 0.3, float(temperature_C))
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


def write_smoke_result() -> Path:
    check = smoke_check()
    BASELINE_OUT.mkdir(parents=True, exist_ok=True)
    path = BASELINE_OUT / "legacy_chemistry_smoke.json"
    payload = {
        "case": {"MEA_weight_fraction": 0.3, "temperature_C": 40.0, "CO2_loading": 0.3},
        "species": list(LEGACY_SPECIES_6),
        "mole_fractions": [float(v) for v in check.mole_fractions],
        "apparent_ternary_x": [float(v) for v in check.apparent_ternary_x],
        "initial_concentrations_mol_m3": [float(v) for v in check.initial_concentrations],
        "true_concentrations_mol_m3": [float(v) for v in check.concentrations],
        "residuals": check.residuals,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def plot_jou_comparison(curves: pd.DataFrame, summary: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = {
        40: "tab:orange",
        60: "tab:blue",
        80: "tab:green",
        100: "tab:red",
        120: "tab:purple",
    }
    data = _load_jou_data()
    for temperature_C in TEMPERATURES_C:
        t_data = data[data["temperature"] == temperature_C]
        t_curve = curves[curves["temperature_C"] == temperature_C]
        if t_data.empty or t_curve.empty:
            continue
        color = colors[temperature_C]
        ax.plot(t_data["CO2_loading"], t_data["CO2_pressure"], "x", color=color)
        summary_row = summary[summary["temperature_C"] == temperature_C].iloc[0]
        label = f"{temperature_C} C, med |log10 err|={summary_row['median_abs_log10_error']:.2f}"
        ax.plot(t_curve["CO2_loading"], t_curve["pred_CO2_pressure_kPa"], ":", color=color, label=label)

    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("CO2 pressure, kPa")
    ax.set_yscale("log")
    ax.legend()
    fig.tight_layout()
    return save_plot(fig, __file__, "legacy_pcsaft_jou_recomputed_fit")


def main() -> int:
    BASELINE_OUT.mkdir(parents=True, exist_ok=True)
    smoke_path = write_smoke_result()
    metrics, summary, curves = compute_jou_metrics()

    metrics_path = BASELINE_OUT / "legacy_pcsaft_jou_fit_metrics.csv"
    summary_path = BASELINE_OUT / "legacy_pcsaft_jou_fit_summary.csv"
    curves_path = BASELINE_OUT / "legacy_pcsaft_jou_fit_curves.csv"
    metrics.to_csv(metrics_path, index=False)
    summary.to_csv(summary_path, index=False)
    curves.to_csv(curves_path, index=False)
    plot_path = plot_jou_comparison(curves, summary)

    print("Legacy chemical-equilibrium smoke:", smoke_path)
    print("PC-SAFT source:", PCSAFT_SOURCE)
    print("Legacy Jou metrics:", metrics_path)
    print("Legacy Jou summary:", summary_path)
    print("Legacy Jou curves:", curves_path)
    print("Legacy Jou plot:", plot_path)
    print(summary.to_string(index=False))

    max_delta = float(summary["delta_vs_expected"].abs().max())
    if max_delta > 0.03:
        print(f"ERROR: legacy metrics drifted by {max_delta:.4f}, above +/-0.03 acceptance.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
