from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MEA.common.config import CANONICAL_MEA_WEIGHT_FRACTION, JOU_TEMPERATURES_C
from MEA.common.data_access import load_combined_vle_data
from MEA.common.plot_export import save_plot
from MEA.common.plot_style import (
    EPCSAFT_IONIC_LINESTYLE,
    JOU_DATA_MARKER,
    PRESSURE_FIGSIZE,
    SPECIATION_FIGSIZE,
    apply_pressure_axes,
    apply_speciation_axes,
    species_color,
    species_label,
    SPECIATION_MODEL_LINESTYLE,
    SPECIATION_TARGET_ALPHA,
    SPECIATION_TARGET_MARKER,
    SPECIATION_TARGET_MARKERSIZE,
    temperature_color,
)
from MEA.epcsaft_ionic.model import (
    FIT_DATASET_DIR,
    IONIC_PLOT_ROOT,
    OUT_DIR,
    PRESSURE_OUT_DIR,
    SPECIATION_OUT_DIR,
    SUMMARY_OUT_DIR,
    SPECIES,
    SPECIES_INDEX,
    load_speciation_targets,
    load_vle_targets,
    predict_bubble_pressure,
    predict_co2_pressure_kPa,
    solve_reactive_bubble_targets,
    solve_activity_speciation,
    theta_to_map,
    write_csv,
    write_json,
)


def _load_fitted_values() -> dict[str, float]:
    values_path = OUT_DIR / "ionic_parameter_regression_values.csv"
    if not values_path.exists():
        raise RuntimeError(
            "Missing ionic regression values. Run `uv run python -m MEA.epcsaft_ionic.regress_parameters` first."
        )
    frame = pd.read_csv(values_path)
    values = {str(row["parameter"]): float(row["fitted"]) for _, row in frame.iterrows()}
    promoted_ion_values = IONIC_PLOT_ROOT / "ion_parameter_regression" / "ion_parameter_fit_values.csv"
    if promoted_ion_values.exists():
        ion_frame = pd.read_csv(promoted_ion_values)
        values.update({str(row["parameter"]): float(row["fitted"]) for _, row in ion_frame.iterrows()})
    return values


def pressure_rows(values: dict[str, float]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    targets = load_vle_targets(None)
    results = solve_reactive_bubble_targets(targets, values, FIT_DATASET_DIR)
    for target, result in zip(targets, results):
        row: dict[str, object] = {
            "row_id": target.row_id,
            "temperature_C": target.T - 273.15,
            "CO2_loading": target.loading,
            "observed_CO2_pressure_kPa": target.pressure_kPa,
            "paper": target.paper,
        }
        try:
            if isinstance(result, Exception):
                raise result
            predicted = float(result.partial_pressures.get("CO2", np.nan)) / 1000.0
            if not np.isfinite(predicted) or predicted <= 0.0:
                raise RuntimeError(result.message)
            row["raw_pred_CO2_pressure_kPa"] = predicted
            row["raw_log10_model_over_data"] = math.log10(max(predicted, 1.0e-30) / target.pressure_kPa)
            row["bubble_total_pressure_kPa"] = float(result.P_total) / 1000.0
            row["bubble_fugacity_residual_norm"] = result.fugacity_residual_norm
            row["chemical_charge_residual"] = result.charge_residual
            row["chemical_max_reaction_residual"] = max((abs(value) for value in result.named_reaction_residuals.values()), default=np.nan)
            row["penalty_residual_count"] = len(result.penalty_residuals)
            row["diagnostic_success"] = bool(result.success)
            for species in SPECIES:
                x_value = result.x_liq.get(species, np.nan)
                row[f"model_x_{species}"] = float(x_value)
            for species, y_value in result.y_vap.items():
                row[f"y_{species}"] = float(y_value)
            row["success"] = bool(result.success)
            row["message"] = result.message
        except Exception as exc:
            row["raw_pred_CO2_pressure_kPa"] = np.nan
            row["raw_log10_model_over_data"] = np.nan
            row["success"] = False
            row["message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        rows.append(row)
    return rows


def speciation_rows(values: dict[str, float]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in load_speciation_targets(None):
        row: dict[str, object] = {
            "row_id": target.row_id,
            "temperature_C": target.T - 273.15,
            "CO2_loading": target.loading,
            "source": target.source,
        }
        for species, x_value in zip(SPECIES, target.x):
            row[f"target_x_{species}"] = float(x_value)
        try:
            chemistry = solve_activity_speciation(target.loading, target.T, target.P, target.x, values, FIT_DATASET_DIR)
            for species, x_value in zip(SPECIES, chemistry.x):
                row[f"model_x_{species}"] = float(x_value)
                row[f"log10_model_over_target_{species}"] = math.log10(
                    max(float(x_value), 1.0e-30) / max(float(target.x[SPECIES_INDEX[species]]), 1.0e-30)
                )
            for name, value in chemistry.reaction_residuals.items():
                row[f"reaction_{name}"] = float(value)
            for name, value in chemistry.mass_balance_residuals.items():
                row[f"mass_balance_{name}"] = float(value)
            row["charge_residual"] = chemistry.charge_residual
            row["state_failure_count"] = chemistry.state_failure_count
            row["success"] = True
            row["message"] = chemistry.message
        except Exception as exc:
            row["success"] = False
            row["message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        rows.append(row)
    return rows


def plot_pressure(rows: list[dict[str, object]]):
    frame = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=PRESSURE_FIGSIZE)
    for temperature_C in JOU_TEMPERATURES_C:
        data = load_combined_vle_data(
            temperature_C=temperature_C,
            mea_weight_fraction=CANONICAL_MEA_WEIGHT_FRACTION,
            loading_max=0.62,
        )
        color = temperature_color(temperature_C)
        if not data.empty:
            ax.plot(data["CO2_loading"], data["CO2_pressure"], JOU_DATA_MARKER, color=color)
        subset = frame[np.isclose(frame["temperature_C"].astype(float), float(temperature_C))].sort_values("CO2_loading")
        ok = subset[subset["success"] == True]
        if not ok.empty:
            med = float(np.nanmedian(np.abs(ok["raw_log10_model_over_data"].astype(float))))
            ax.plot(
                ok["CO2_loading"],
                ok["raw_pred_CO2_pressure_kPa"],
                EPCSAFT_IONIC_LINESTYLE,
                color=color,
                label=f"{temperature_C} C, med |log10 err|={med:.2f}",
            )
    apply_pressure_axes(ax)
    ax.legend()
    fig.tight_layout()
    return save_plot(fig, __file__, "ionic_epcsaft_co2_pressure", workflow_name="epcsaft_ionic/pressure")


def plot_speciation(rows: list[dict[str, object]]):
    frame = pd.DataFrame(rows)
    subset = frame[np.isclose(frame["temperature_C"].astype(float), 40.0)].sort_values("CO2_loading")
    fig, ax = plt.subplots(figsize=SPECIATION_FIGSIZE)
    loading_min = float(subset["CO2_loading"].min()) if not subset.empty else 0.0
    loading_max = min(0.8, float(subset["CO2_loading"].max()) if not subset.empty else 0.8)
    subset = subset[(subset["CO2_loading"] >= loading_min) & (subset["CO2_loading"] <= loading_max)]
    snapshot_rows = []
    subset = subset.copy()
    if {"target_x_MEA", "target_x_MEAH+"}.issubset(subset.columns):
        subset["target_x_MEA + MEAH+"] = subset["target_x_MEA"].astype(float) + subset["target_x_MEAH+"].astype(float)
    if {"model_x_MEA", "model_x_MEAH+"}.issubset(subset.columns):
        subset["model_x_MEA + MEAH+"] = subset["model_x_MEA"].astype(float) + subset["model_x_MEAH+"].astype(float)

    for species in ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-", "MEA + MEAH+"):
        color = species_color(species)
        target_column = f"target_x_{species}"
        model_column = f"model_x_{species}"
        if target_column in subset:
            target = subset[["CO2_loading", target_column]].dropna()
            ax.semilogy(
                target["CO2_loading"],
                target[target_column],
                SPECIATION_TARGET_MARKER,
                color=color,
                alpha=SPECIATION_TARGET_ALPHA,
                markersize=SPECIATION_TARGET_MARKERSIZE,
            )
            for row in target.to_dict("records"):
                snapshot_rows.append({"source": "reference", "species": species, "CO2_loading": row["CO2_loading"], "mole_fraction": row[target_column]})
        if model_column in subset:
            model = subset[["CO2_loading", model_column]].dropna()
            ax.semilogy(
                model["CO2_loading"],
                model[model_column],
                SPECIATION_MODEL_LINESTYLE,
                color=color,
                label=species_label(species),
            )
            for row in model.to_dict("records"):
                snapshot_rows.append({"source": "model", "species": species, "CO2_loading": row["CO2_loading"], "mole_fraction": row[model_column]})
    apply_speciation_axes(ax)
    write_csv(SPECIATION_OUT_DIR / "ionic_speciation_plot_data.csv", snapshot_rows)
    ax.legend(loc="lower center", ncol=3)
    fig.tight_layout()
    return save_plot(fig, __file__, "ionic_epcsaft_speciation_activity", workflow_name="epcsaft_ionic/speciation")


def main() -> int:
    values = _load_fitted_values()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    IONIC_PLOT_ROOT.mkdir(parents=True, exist_ok=True)
    p_rows = pressure_rows(values)
    s_rows = speciation_rows(values)
    pressure_csv = write_csv(PRESSURE_OUT_DIR / "ionic_pressure_comparison.csv", p_rows)
    speciation_csv = write_csv(SPECIATION_OUT_DIR / "ionic_speciation_activity_residuals.csv", s_rows)
    pressure_plot = plot_pressure(p_rows)
    speciation_plot = plot_speciation(s_rows)
    p_frame = pd.DataFrame(p_rows)
    s_frame = pd.DataFrame(s_rows)
    ok_pressure = p_frame[p_frame["success"] == True]
    reaction_cols = [name for name in s_frame.columns if name.startswith("reaction_")]
    speciation_cols = [name for name in s_frame.columns if name.startswith("log10_model_over_target_")]
    summary = {
        "dataset": str(FIT_DATASET_DIR),
        "pressure_csv": str(pressure_csv),
        "speciation_csv": str(speciation_csv),
        "pressure_plot": str(pressure_plot),
        "speciation_plot": str(speciation_plot),
        "pressure_method": "ePC-SAFT reactive speciation plus electrolyte bubble pressure",
        "pressure_success_count": int((p_frame["success"] == True).sum()),
        "pressure_count": int(len(p_frame)),
        "raw_pressure_median_abs_log10_error": float(np.nanmedian(np.abs(ok_pressure["raw_log10_model_over_data"].astype(float)))) if not ok_pressure.empty else None,
        "raw_pressure_max_abs_log10_error": float(np.nanmax(np.abs(ok_pressure["raw_log10_model_over_data"].astype(float)))) if not ok_pressure.empty else None,
        "speciation_success_count": int((s_frame["success"] == True).sum()),
        "speciation_count": int(len(s_frame)),
        "reaction_median_abs_ln_residuals": {
            col: float(np.nanmedian(np.abs(s_frame[col].astype(float)))) for col in reaction_cols if col in s_frame
        },
        "speciation_median_abs_log10_model_over_target": {
            col.replace("log10_model_over_target_", ""): float(np.nanmedian(np.abs(s_frame[col].astype(float))))
            for col in speciation_cols
            if col in s_frame
        },
    }
    write_json(SUMMARY_OUT_DIR / "ionic_evaluation_summary.json", summary)
    print(f"Ionic pressure comparison: {pressure_csv}")
    print(f"Ionic speciation activity residuals: {speciation_csv}")
    print(f"Ionic pressure plot: {pressure_plot}")
    print(f"Ionic speciation plot: {speciation_plot}")
    print(f"Raw pressure median |log10(model/data)|: {summary['raw_pressure_median_abs_log10_error']}")
    print(f"Pressure successes: {summary['pressure_success_count']}/{summary['pressure_count']}")
    print(f"Speciation activity successes: {summary['speciation_success_count']}/{summary['speciation_count']}")
    return 0 if summary["pressure_success_count"] > 0 and summary["speciation_success_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
