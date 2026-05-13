from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MEA.common.config import CANONICAL_MEA_WEIGHT_FRACTION, EPCSAFT_NEUTRAL_ANALYSIS, JOU_TEMPERATURES_C
from MEA.common.data_access import load_jou_vle_data
from MEA.common.plot_export import save_plot
from MEA.common.plot_style import (
    EPCSAFT_NEUTRAL_LINESTYLE,
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    LEGACY_PCSAFT_LINESTYLE,
    MODEL_LINEWIDTH,
    REFERENCE_LINEWIDTH,
    PRESSURE_FIGSIZE,
    apply_pressure_axes,
    temperature_color,
)
from MEA.common.reporting import write_csv_report, write_json_report
from MEA.epcsaft_neutral.parameters import DATASET_DIR, SPECIES, legacy_neutral_dataset_rows
from MEA.epcsaft_neutral.pressure import NeutralPressureResult, predict_co2_pressure_kpa
from MEA.six_species.chemistry import LEGACY_SPECIES_6, collapse_to_apparent_ternary, legacy_true_mole_fractions
from MEA.six_species.plot_pressure import EXPECTED_MEDIAN_ABS_LOG10_ERROR
from MEA.six_species.plot_pressure import predict_co2_pressure_kpa as predict_legacy_pcsaft_pressure_kpa


OUT_DIR = EPCSAFT_NEUTRAL_ANALYSIS / "results" / "pressure"
TEMPERATURES_C = JOU_TEMPERATURES_C


def write_neutral_dataset() -> list[Path]:
    rows, k_ij = legacy_neutral_dataset_rows()
    pure_dir = DATASET_DIR / "pure"
    mixed_dir = DATASET_DIR / "mixed" / "binary_interaction"
    pure_dir.mkdir(parents=True, exist_ok=True)
    mixed_dir.mkdir(parents=True, exist_ok=True)

    pure_path = pure_dir / "any_solvent.csv"
    fieldnames = ["component", "m", "s", "e", "e_assoc", "vol_a", "assoc_scheme", "z", "dielc", "d_born", "f_solv", "MW"]
    with pure_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    written = [pure_path]
    for name, matrix in {"k_ij.csv": k_ij, "k_hb_ij.csv": np.zeros_like(k_ij), "l_ij.csv": np.zeros_like(k_ij)}.items():
        path = mixed_dir / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["component", *SPECIES])
            for component, values in zip(SPECIES, matrix):
                writer.writerow([component, *[f"{float(value):.12g}" for value in values]])
        written.append(path)
    return written


def _jou_data() -> pd.DataFrame:
    return load_jou_vle_data(mea_weight_fraction=CANONICAL_MEA_WEIGHT_FRACTION)


def _result_payload(result: NeutralPressureResult) -> dict[str, object]:
    return {
        "epcsaft_success": result.success,
        "epcsaft_message": result.message,
        "epcsaft_CO2_pressure_kPa": result.pressure_kPa,
        "epcsaft_total_pressure_Pa": result.total_pressure_Pa,
        "epcsaft_y_CO2": float(result.y_vapor[0]),
        "epcsaft_y_MEA": float(result.y_vapor[1]),
        "epcsaft_y_H2O": float(result.y_vapor[2]),
        "epcsaft_bubble_residual": result.bubble_residual,
        "epcsaft_max_fugacity_residual": float(np.nanmax(np.abs(result.fugacity_residual))),
        "epcsaft_iterations": result.iterations,
        "epcsaft_method": result.method,
        "epcsaft_equilibrium_split_detected": result.equilibrium_split_detected,
        "epcsaft_equilibrium_message": result.equilibrium_message,
        "epcsaft_liquid_fugacity_pressure_kPa": result.liquid_fugacity_pressure_kPa,
    }


def compute_neutral_parity() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = _jou_data()
    rows: list[dict[str, object]] = []
    curve_rows: list[dict[str, object]] = []
    for temperature_C in TEMPERATURES_C:
        t_df = data[data["temperature"] == temperature_C].sort_values("CO2_loading")
        if t_df.empty:
            continue
        loadings = np.linspace(float(t_df["CO2_loading"].iloc[0]), float(t_df["CO2_loading"].iloc[-1]), 21)
        curve_pressures = []
        legacy_curve_pressures = []
        for loading in loadings:
            temperature_K = float(temperature_C) + 273.15
            x6 = legacy_true_mole_fractions(float(loading), CANONICAL_MEA_WEIGHT_FRACTION, temperature_K)
            x_liquid = collapse_to_apparent_ternary(x6)
            legacy = predict_legacy_pcsaft_pressure_kpa(float(loading), CANONICAL_MEA_WEIGHT_FRACTION, float(temperature_C))
            result = predict_co2_pressure_kpa(temperature_K, x_liquid)
            curve_pressures.append(result.pressure_kPa)
            legacy_curve_pressures.append(legacy["pressure_kPa"])
            curve_rows.append(
                {
                    "temperature_C": temperature_C,
                    "CO2_loading": float(loading),
                    "legacy_pcsaft_CO2_pressure_kPa": legacy["pressure_kPa"],
                    "legacy_pcsaft_total_pressure_Pa": legacy["total_pressure_Pa"],
                    "legacy_pcsaft_y_CO2": float(np.asarray(legacy["y_vapor"], dtype=float)[0]),
                    **_result_payload(result),
                    **{f"x6_{name}": float(x6[i]) for i, name in enumerate(LEGACY_SPECIES_6)},
                    **{f"x_apparent_{name}": float(x_liquid[i]) for i, name in enumerate(SPECIES)},
                }
            )

        interp_epcsaft = np.interp(t_df["CO2_loading"].to_numpy(dtype=float), loadings, np.asarray(curve_pressures, dtype=float))
        interp_legacy = np.interp(t_df["CO2_loading"].to_numpy(dtype=float), loadings, np.asarray(legacy_curve_pressures, dtype=float))
        for data_row, epcsaft_pred, legacy_pred in zip(t_df.to_dict("records"), interp_epcsaft, interp_legacy):
            observed = float(data_row["CO2_pressure"])
            rows.append(
                {
                    "temperature_C": temperature_C,
                    "MEA_weight_fraction": float(data_row["MEA_weight_fraction"]),
                    "CO2_loading": float(data_row["CO2_loading"]),
                    "observed_CO2_pressure_kPa": observed,
                    "legacy_pcsaft_CO2_pressure_kPa": float(legacy_pred),
                    "epcsaft_CO2_pressure_kPa": float(epcsaft_pred),
                    "legacy_log10_pred_over_obs": float(np.log10(legacy_pred / observed)) if legacy_pred > 0.0 and observed > 0.0 else np.nan,
                    "epcsaft_log10_pred_over_obs": float(np.log10(epcsaft_pred / observed)) if epcsaft_pred > 0.0 and observed > 0.0 else np.nan,
                    "epcsaft_minus_legacy_log10": float(np.log10(epcsaft_pred / legacy_pred)) if epcsaft_pred > 0.0 and legacy_pred > 0.0 else np.nan,
                }
            )

    metrics = pd.DataFrame(rows)
    summary = (
        metrics.groupby("temperature_C")
        .agg(
            n=("epcsaft_log10_pred_over_obs", "size"),
            epcsaft_median_abs_log10_error=("epcsaft_log10_pred_over_obs", lambda s: float(np.nanmedian(np.abs(s)))),
            legacy_median_abs_log10_error=("legacy_log10_pred_over_obs", lambda s: float(np.nanmedian(np.abs(s)))),
            median_abs_epcsaft_minus_legacy_log10=("epcsaft_minus_legacy_log10", lambda s: float(np.nanmedian(np.abs(s)))),
            max_abs_epcsaft_minus_legacy_log10=("epcsaft_minus_legacy_log10", lambda s: float(np.nanmax(np.abs(s)))),
        )
        .reset_index()
    )
    summary["expected_legacy_median_abs_log10_error"] = summary["temperature_C"].map(EXPECTED_MEDIAN_ABS_LOG10_ERROR)
    summary["epcsaft_delta_vs_expected"] = summary["epcsaft_median_abs_log10_error"] - summary["expected_legacy_median_abs_log10_error"]
    summary["legacy_delta_vs_expected"] = summary["legacy_median_abs_log10_error"] - summary["expected_legacy_median_abs_log10_error"]
    return metrics, summary, pd.DataFrame(curve_rows)


def plot_parity(curves: pd.DataFrame) -> Path:
    title = "Neutral ePC-SAFT parity against legacy PC-SAFT pressure curves"
    description = (
        "Neutral ePC-SAFT and legacy PC-SAFT pressure curves are compared against Jou et al. "
        "30 wt% MEA carbon-dioxide partial-pressure data using a shared temperature palette."
    )
    data = _jou_data()
    fig, ax = plt.subplots(figsize=PRESSURE_FIGSIZE)
    for temperature_C in TEMPERATURES_C:
        color = temperature_color(temperature_C)
        t_data = data[data["temperature"] == temperature_C]
        t_curve = curves[curves["temperature_C"] == temperature_C]
        if t_data.empty or t_curve.empty:
            continue
        ax.plot(
            t_data["CO2_loading"],
            t_data["CO2_pressure"],
            linestyle="none",
            marker=JOU_DATA_MARKER,
            markersize=JOU_DATA_MARKERSIZE,
            color=color,
            alpha=0.9,
            label=f"{temperature_C} C Jou data",
        )
        ax.plot(
            t_curve["CO2_loading"],
            t_curve["legacy_pcsaft_CO2_pressure_kPa"],
            LEGACY_PCSAFT_LINESTYLE,
            color=color,
            alpha=0.65,
            linewidth=REFERENCE_LINEWIDTH,
            label=f"{temperature_C} C legacy PC-SAFT",
        )
        ax.plot(
            t_curve["CO2_loading"],
            t_curve["epcsaft_CO2_pressure_kPa"],
            EPCSAFT_NEUTRAL_LINESTYLE,
            color=color,
            linewidth=MODEL_LINEWIDTH,
            label=f"{temperature_C} C ePC-SAFT neutral",
        )
    apply_pressure_axes(ax, title=title)
    ax.legend(ncol=2, title="Temperature and role")
    fig.tight_layout()
    return save_plot(
        fig,
        __file__,
        "epcsaft_neutral_pcsaft_parity",
        workflow_name="epcsaft_neutral/pressure",
        title=title,
        description=description,
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset_paths = write_neutral_dataset()
    metrics, summary, curves = compute_neutral_parity()
    metrics_path = OUT_DIR / "epcsaft_neutral_jou_parity_metrics.csv"
    summary_path = OUT_DIR / "epcsaft_neutral_jou_parity_summary.csv"
    curves_path = OUT_DIR / "epcsaft_neutral_jou_parity_curves.csv"
    write_csv_report(metrics_path, metrics)
    write_csv_report(summary_path, summary)
    write_csv_report(curves_path, curves)
    plot_path = plot_parity(curves)
    summary_json_path = OUT_DIR / "epcsaft_neutral_jou_parity_summary.json"
    write_json_report(
        summary_json_path,
        {
            "dataset_paths": [str(path) for path in dataset_paths],
            "metrics": str(metrics_path),
            "summary": str(summary_path),
            "curves": str(curves_path),
            "plot": str(plot_path),
            "acceptance": {
                "max_abs_epcsaft_delta_vs_expected_limit": 0.03,
                "max_abs_epcsaft_delta_vs_expected": float(summary["epcsaft_delta_vs_expected"].abs().max()),
                "all_curve_points_solved": bool((curves["epcsaft_success"] == True).all()) if not curves.empty else False,
            },
        },
    )

    print(f"Neutral ePC-SAFT dataset: {DATASET_DIR}")
    print(f"Neutral ePC-SAFT metrics: {metrics_path}")
    print(f"Neutral ePC-SAFT summary: {summary_path}")
    print(f"Neutral ePC-SAFT curves: {curves_path}")
    print(f"Neutral ePC-SAFT plot: {plot_path}")
    print(summary.to_string(index=False))

    max_delta = float(summary["epcsaft_delta_vs_expected"].abs().max())
    all_solved = bool((curves["epcsaft_success"] == True).all()) if not curves.empty else False
    if not all_solved:
        print("ERROR: not all neutral ePC-SAFT curve points solved.")
        return 1
    if max_delta > 0.03:
        print(f"ERROR: neutral ePC-SAFT metrics drifted by {max_delta:.4f}, above +/-0.03 acceptance.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
