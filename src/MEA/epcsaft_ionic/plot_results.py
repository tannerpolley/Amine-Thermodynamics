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
    JOU_DATA_MARKERSIZE,
    MODEL_LINEWIDTH,
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
    DEFAULT_INITIAL_GUESS,
    PRESSURE_OUT_DIR,
    SPECIATION_OUT_DIR,
    SUMMARY_OUT_DIR,
    SPECIES,
    SPECIES_INDEX,
    load_speciation_targets,
    load_vle_targets,
    reactive_bubble_acceptance,
    solve_reactive_bubble_targets,
    solve_activity_speciation,
    write_csv,
    write_json,
)


def _load_fixed_values() -> dict[str, float]:
    return dict(DEFAULT_INITIAL_GUESS)


def _accepted_mask(frame: pd.DataFrame) -> pd.Series:
    if "accepted" not in frame:
        return pd.Series(False, index=frame.index)
    return frame["accepted"].astype(str).str.lower().isin({"true", "1", "yes"})


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
            "source_key": target.source_key,
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
            decision = reactive_bubble_acceptance(result)
            for species in SPECIES:
                x_value = result.x_liq.get(species, np.nan)
                row[f"model_x_{species}"] = float(x_value)
            for species, y_value in result.y_vap.items():
                row[f"y_{species}"] = float(y_value)
            row["solver_returned"] = bool(result.success)
            row["accepted"] = decision.accepted
            row["rejection_reason"] = decision.rejection_reason
            row["message"] = result.message
        except Exception as exc:
            row["raw_pred_CO2_pressure_kPa"] = np.nan
            row["raw_log10_model_over_data"] = np.nan
            row["solver_returned"] = False
            row["accepted"] = False
            row["rejection_reason"] = "exception"
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
            row["solver_returned"] = chemistry.solver_returned_success
            row["accepted"] = chemistry.accepted
            row["rejection_reason"] = chemistry.rejection_reason
            row["model_role"] = "activity_equilibrium" if chemistry.accepted else "rejected_best_effort_diagnostic"
            row["message"] = chemistry.message
        except Exception as exc:
            row["solver_returned"] = False
            row["accepted"] = False
            row["rejection_reason"] = "exception"
            row["model_role"] = "rejected_exception"
            row["message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        rows.append(row)
    return rows


def plot_pressure(rows: list[dict[str, object]]):
    title = "Full-ionic ePC-SAFT $CO_2$ pressure validation"
    description = (
        "Full-ionic ePC-SAFT pressure predictions are compared with 30 wt% MEA literature "
        "carbon-dioxide partial pressures across the Jou temperature set."
    )
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
            ax.plot(
                data["CO2_loading"],
                data["CO2_pressure"],
                linestyle="none",
                marker=JOU_DATA_MARKER,
                markersize=JOU_DATA_MARKERSIZE,
                color=color,
                alpha=0.9,
                label=f"{temperature_C} C literature data",
            )
        subset = frame[np.isclose(frame["temperature_C"].astype(float), float(temperature_C))].sort_values("CO2_loading")
        ok = subset[subset["accepted"].astype(bool)]
        if not ok.empty:
            med = float(np.nanmedian(np.abs(ok["raw_log10_model_over_data"].astype(float))))
            ax.plot(
                ok["CO2_loading"],
                ok["raw_pred_CO2_pressure_kPa"],
                EPCSAFT_IONIC_LINESTYLE,
                color=color,
                linewidth=MODEL_LINEWIDTH,
                label=f"{temperature_C} C, med |log10 err|={med:.2f}",
            )
    apply_pressure_axes(ax, title=title)
    ax.legend(ncol=2, title="Temperature and role")
    fig.tight_layout()
    return save_plot(
        fig,
        __file__,
        "ionic_epcsaft_co2_pressure",
        workflow_name="epcsaft_ionic/pressure",
        title=title,
        description=description,
    )


def plot_speciation(rows: list[dict[str, object]]):
    title = "Full-ionic ePC-SAFT true-species speciation at 40 C"
    description = (
        "Full-ionic ePC-SAFT true-species activity-equilibrium predictions are compared "
        "with measured speciation targets at 40 C using shared species colors."
    )
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
    accepted = _accepted_mask(subset)

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
                snapshot_rows.append(
                    {
                        "source": "reference",
                        "species": species,
                        "CO2_loading": row["CO2_loading"],
                        "mole_fraction": row[target_column],
                        "accepted": "",
                        "message": "",
                    }
                )
        if model_column in subset:
            model = subset[["CO2_loading", model_column, "message"]].copy()
            model["accepted"] = accepted
            model.loc[~model["accepted"], model_column] = np.nan
            ax.semilogy(
                model["CO2_loading"],
                model[model_column],
                SPECIATION_MODEL_LINESTYLE,
                color=color,
                linewidth=MODEL_LINEWIDTH,
                label=species_label(species),
            )
            for row in model.to_dict("records"):
                snapshot_rows.append(
                    {
                        "source": "model",
                        "species": species,
                        "CO2_loading": row["CO2_loading"],
                        "mole_fraction": row[model_column],
                        "accepted": bool(row["accepted"]),
                        "message": row.get("message", ""),
                    }
                )
    apply_speciation_axes(ax, title=title)
    write_csv(SPECIATION_OUT_DIR / "ionic_speciation_plot_data.csv", snapshot_rows)
    ax.legend(loc="lower center", ncol=3, title="Model curves; markers are targets")
    fig.tight_layout()
    return save_plot(
        fig,
        __file__,
        "ionic_epcsaft_speciation_activity",
        workflow_name="epcsaft_ionic/speciation",
        title=title,
        description=description,
    )


def main() -> int:
    values = _load_fixed_values()
    IONIC_PLOT_ROOT.mkdir(parents=True, exist_ok=True)
    p_rows = pressure_rows(values)
    s_rows = speciation_rows(values)
    pressure_csv = write_csv(PRESSURE_OUT_DIR / "ionic_pressure_comparison.csv", p_rows)
    speciation_csv = write_csv(SPECIATION_OUT_DIR / "ionic_speciation_activity_residuals.csv", s_rows)
    pressure_plot = plot_pressure(p_rows)
    speciation_plot = plot_speciation(s_rows)
    p_frame = pd.DataFrame(p_rows)
    s_frame = pd.DataFrame(s_rows)
    ok_pressure = p_frame[p_frame["accepted"].astype(bool)]
    ok_speciation = s_frame[s_frame["accepted"].astype(bool)]
    reaction_cols = [name for name in s_frame.columns if name.startswith("reaction_")]
    speciation_cols = [name for name in s_frame.columns if name.startswith("log10_model_over_target_")]
    summary = {
        "dataset": str(FIT_DATASET_DIR),
        "pressure_csv": str(pressure_csv),
        "speciation_csv": str(speciation_csv),
        "pressure_plot": str(pressure_plot),
        "speciation_plot": str(speciation_plot),
        "pressure_method": "ePC-SAFT reactive speciation plus electrolyte bubble pressure",
        "pressure_accepted_count": int(p_frame["accepted"].astype(bool).sum()),
        "pressure_count": int(len(p_frame)),
        "raw_pressure_median_abs_log10_error": float(np.nanmedian(np.abs(ok_pressure["raw_log10_model_over_data"].astype(float)))) if not ok_pressure.empty else None,
        "raw_pressure_max_abs_log10_error": float(np.nanmax(np.abs(ok_pressure["raw_log10_model_over_data"].astype(float)))) if not ok_pressure.empty else None,
        "speciation_accepted_count": int(s_frame["accepted"].astype(bool).sum()),
        "speciation_count": int(len(s_frame)),
        "reaction_median_abs_ln_residuals": {
            col: float(np.nanmedian(np.abs(ok_speciation[col].astype(float))))
            for col in reaction_cols
            if col in ok_speciation
        },
        "speciation_median_abs_log10_model_over_target": {
            col.replace("log10_model_over_target_", ""): float(
                np.nanmedian(np.abs(ok_speciation[col].astype(float)))
            )
            for col in speciation_cols
            if col in ok_speciation
        },
    }
    write_json(SUMMARY_OUT_DIR / "ionic_evaluation_summary.json", summary)
    print(f"Ionic pressure comparison: {pressure_csv}")
    print(f"Ionic speciation activity residuals: {speciation_csv}")
    print(f"Ionic pressure plot: {pressure_plot}")
    print(f"Ionic speciation plot: {speciation_plot}")
    print(f"Raw pressure median |log10(model/data)|: {summary['raw_pressure_median_abs_log10_error']}")
    print(f"Pressure accepted: {summary['pressure_accepted_count']}/{summary['pressure_count']}")
    print(f"Speciation activity accepted: {summary['speciation_accepted_count']}/{summary['speciation_count']}")
    return 0 if summary["pressure_success_count"] > 0 and summary["speciation_success_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
