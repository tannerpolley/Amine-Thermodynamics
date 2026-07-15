from __future__ import annotations

import json
import math
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MEA.common.data_access import require_regression_execution_admitted
from MEA.common.plot_style import finish_axes, save_figure_bundle, species_color, species_label, write_mpl_sidecar
from MEA.epcsaft_ionic import native_regression
from MEA.epcsaft_ionic.model import (
    BOUNDS,
    DEFAULT_INITIAL_GUESS,
    EPCSAFT_IONIC_ANALYSIS,
    FIT_DATASET_DIR,
    SPECIES_INDEX,
    VLETarget,
    SpeciationTarget,
    load_epcsaft,
    load_speciation_targets,
    load_vle_targets,
    reactive_bubble_acceptance,
    solve_activity_speciation,
    solve_reactive_bubble_targets,
    write_csv,
    write_json,
)

GLOBAL_RESULTS_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "global_regression"
GLOBAL_RUNS_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "runs" / "global_regression"
SENSITIVITY_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "sensitivity"
BASELINE_PRESSURE_CSV = EPCSAFT_IONIC_ANALYSIS / "results" / "pressure" / "ionic_pressure_comparison.csv"
BASELINE_SPECIATION_CSV = EPCSAFT_IONIC_ANALYSIS / "results" / "speciation" / "ionic_speciation_activity_residuals.csv"
IONIC_EVALUATION_SUMMARY = EPCSAFT_IONIC_ANALYSIS / "results" / "summary" / "ionic_evaluation_summary.json"
GLOBAL_SUMMARY_PATH = GLOBAL_RESULTS_DIR / "global_regression_summary.json"

GLOBAL_FIT_NAMES = (
    "MEAH+__s",
    "MEAH+__e",
    "MEAH+__d_born",
    "MEACOO-__s",
    "MEACOO-__e",
    "MEACOO-__d_born",
    "k_ij__CO2__MEA",
    "k_ij__MEA__H2O",
    "k_ij__MEAH+__MEACOO-",
    "k_ij__MEAH+__HCO3-",
)
GLOBAL_SPECIATION_SPECIES = ("MEAH+", "MEACOO-", "HCO3-", "CO3^2-")
SENSITIVITY_PARAMETERS = GLOBAL_FIT_NAMES + (
    "HCO3-__d_born",
    "CO3^2-__d_born",
    "H3O+__d_born",
    "OH-__d_born",
)
SENSITIVITY_METRICS = (
    "pressure_median_abs_log10",
    "MEAH+_median_abs_log10",
    "MEACOO-_median_abs_log10",
    "HCO3-_median_abs_log10",
    "CO3^2-_median_abs_log10",
)


def _run_dir(root: Path, label: str | None, promote: bool) -> Path:
    if promote:
        return root
    stamp = label or time.strftime("%Y%m%d-%H%M%S")
    return GLOBAL_RUNS_DIR / stamp


def _select_evenly(items: list[Any], limit: int | None) -> list[Any]:
    if limit is None or limit <= 0 or len(items) <= limit:
        return items
    positions = np.linspace(0, len(items) - 1, limit)
    return [items[int(round(position))] for position in positions]


def load_initial_values() -> dict[str, float]:
    return dict(DEFAULT_INITIAL_GUESS)


def load_working_parameter_set() -> tuple[str, dict[str, float]]:
    values = load_initial_values()
    label = "fixed_provisional_parameter_set"
    if GLOBAL_SUMMARY_PATH.exists():
        summary = json.loads(GLOBAL_SUMMARY_PATH.read_text(encoding="utf-8"))
        selected = summary.get("selected_values")
        if isinstance(selected, dict) and selected:
            values.update({key: float(value) for key, value in selected.items()})
            label = str(summary.get("selected_parameter_set", "global_regression"))
    return label, values


def fit_bounds(fit_names: Iterable[str] = GLOBAL_FIT_NAMES) -> tuple[np.ndarray, np.ndarray]:
    names = tuple(fit_names)
    lower = np.asarray([BOUNDS[name][0] for name in names], dtype=float)
    upper = np.asarray([BOUNDS[name][1] for name in names], dtype=float)
    return lower, upper


def fit_vector_to_values(vector: Iterable[float], fit_names: Iterable[str] = GLOBAL_FIT_NAMES, base: dict[str, float] | None = None) -> dict[str, float]:
    values = dict(base or load_initial_values())
    values.update({name: float(value) for name, value in zip(tuple(fit_names), vector)})
    return values


def load_global_targets(max_pressure_records: int | None = None, max_speciation_records: int | None = None) -> tuple[list[VLETarget], list[SpeciationTarget]]:
    return (
        _select_evenly(load_vle_targets(None, role="active_training"), max_pressure_records),
        _select_evenly(load_speciation_targets(None, role="active_training"), max_speciation_records),
    )


def pressure_rows(values: dict[str, float], targets: list[VLETarget]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    results = solve_reactive_bubble_targets(targets, values, FIT_DATASET_DIR)
    for target, result in zip(targets, results):
        row: dict[str, Any] = {
            "row_id": target.row_id,
            "source": target.source_key,
            "temperature_C": target.T - 273.15,
            "MEA_weight_fraction": float(target.x[1]),
            "CO2_loading": target.loading,
            "observed_pressure_Pa": target.pressure_kPa * 1000.0,
        }
        try:
            if isinstance(result, Exception):
                raise result
            predicted_pa = float(result.partial_pressures.get("CO2", np.nan))
            if not np.isfinite(predicted_pa) or predicted_pa <= 0.0:
                raise RuntimeError(result.message)
            decision = reactive_bubble_acceptance(result)
            row["model_pressure_Pa"] = predicted_pa
            row["log10_model_over_data"] = math.log10(max(predicted_pa, 1.0e-30) / max(row["observed_pressure_Pa"], 1.0e-30))
            row["solver_returned"] = bool(result.success)
            row["accepted"] = decision.accepted
            row["rejection_reason"] = decision.rejection_reason
            row["message"] = result.message
        except Exception as exc:
            row["model_pressure_Pa"] = np.nan
            row["log10_model_over_data"] = np.nan
            row["solver_returned"] = False
            row["accepted"] = False
            row["rejection_reason"] = "exception"
            row["message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        rows.append(row)
    return pd.DataFrame(rows)


def speciation_rows(values: dict[str, float], targets: list[SpeciationTarget], species_names: Iterable[str] = GLOBAL_SPECIATION_SPECIES) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    species_tuple = tuple(species_names)
    for target in targets:
        try:
            prediction = solve_activity_speciation(target.loading, target.T, target.P, target.x, values, FIT_DATASET_DIR)
            prediction_x = prediction.x
            solver_returned = prediction.solver_returned_success
            accepted = prediction.accepted
            rejection_reason = prediction.rejection_reason
            message = prediction.message
        except Exception as exc:
            prediction_x = np.full(len(SPECIES_INDEX), np.nan, dtype=float)
            solver_returned = False
            accepted = False
            rejection_reason = "exception"
            message = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        for species in species_tuple:
            observed = float(target.x[SPECIES_INDEX[species]])
            predicted = float(prediction_x[SPECIES_INDEX[species]]) if np.isfinite(prediction_x[SPECIES_INDEX[species]]) else np.nan
            rows.append(
                {
                    "row_id": target.row_id,
                    "source": target.source,
                    "temperature_C": target.T - 273.15,
                    "CO2_loading": target.loading,
                    "species": species,
                    "observed_mole_fraction": observed,
                    "model_mole_fraction": predicted,
                    "log10_model_over_data": (
                        math.log10(max(predicted, 1.0e-30) / max(observed, 1.0e-30)) if np.isfinite(predicted) else np.nan
                    ),
                    "solver_returned": solver_returned,
                    "accepted": accepted,
                    "rejection_reason": rejection_reason,
                    "message": message,
                }
            )
    return pd.DataFrame(rows)


def _bool_value(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def cached_pressure_rows() -> pd.DataFrame:
    frame = pd.read_csv(BASELINE_PRESSURE_CSV)
    return pd.DataFrame(
        {
            "row_id": frame["row_id"],
            "source": frame["source_key"],
            "temperature_C": frame["temperature_C"],
            "MEA_weight_fraction": np.nan,
            "CO2_loading": frame["CO2_loading"],
            "observed_pressure_Pa": frame["observed_CO2_pressure_kPa"].astype(float) * 1000.0,
            "model_pressure_Pa": frame["raw_pred_CO2_pressure_kPa"].astype(float) * 1000.0,
            "log10_model_over_data": frame["raw_log10_model_over_data"].astype(float),
            "solver_returned": frame["solver_returned"].map(_bool_value),
            "accepted": frame["accepted"].map(_bool_value),
            "rejection_reason": frame["rejection_reason"].astype(str),
            "message": frame["message"].astype(str),
        }
    )


def cached_speciation_rows(species_names: Iterable[str] = GLOBAL_SPECIATION_SPECIES) -> pd.DataFrame:
    frame = pd.read_csv(BASELINE_SPECIATION_CSV)
    rows: list[dict[str, Any]] = []
    for species in tuple(species_names):
        rows.extend(
            {
                "row_id": row["row_id"],
                "source": row["source"],
                "temperature_C": row["temperature_C"],
                "CO2_loading": row["CO2_loading"],
                "species": species,
                "observed_mole_fraction": row[f"target_x_{species}"],
                "model_mole_fraction": row[f"model_x_{species}"],
                "log10_model_over_data": row[f"log10_model_over_target_{species}"],
                "solver_returned": _bool_value(row["solver_returned"]),
                "accepted": _bool_value(row["accepted"]),
                "rejection_reason": str(row["rejection_reason"]),
                "message": str(row["message"]),
            }
            for row in frame.to_dict("records")
        )
    return pd.DataFrame(rows)


def pressure_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    accepted = frame[frame["accepted"].astype(bool)] if not frame.empty else frame
    finite = accepted[np.isfinite(accepted["log10_model_over_data"].astype(float))] if not accepted.empty else accepted
    residual = finite["log10_model_over_data"].astype(float).to_numpy() if not finite.empty else np.asarray([])
    return {
        "row_count": int(frame["row_id"].nunique()) if not frame.empty else 0,
        "accepted_count": int(frame["accepted"].astype(bool).sum()) if not frame.empty else 0,
        "median_abs_log10": float(np.median(np.abs(residual))) if residual.size else None,
        "max_abs_log10": float(np.max(np.abs(residual))) if residual.size else None,
        "rmse_log10": float(np.sqrt(np.mean(residual * residual))) if residual.size else None,
    }


def speciation_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    accepted = frame[frame["accepted"].astype(bool)] if not frame.empty else frame
    finite = accepted[np.isfinite(accepted["log10_model_over_data"].astype(float))] if not accepted.empty else accepted
    output: dict[str, Any] = {
        "row_count": int(frame["row_id"].nunique()) if not frame.empty else 0,
        "residual_count": int(len(frame)),
    }
    by_species: dict[str, Any] = {}
    for species, subset in finite.groupby("species"):
        residual = subset["log10_model_over_data"].astype(float).to_numpy()
        by_species[str(species)] = {
            "count": int(len(subset)),
            "median_abs_log10": float(np.median(np.abs(residual))),
            "rmse_log10": float(np.sqrt(np.mean(residual * residual))),
        }
    output.update(by_species)
    return output


def objective_residuals(
    values: dict[str, float],
    vle_targets: list[VLETarget],
    spec_targets: list[SpeciationTarget],
    *,
    pressure_weight: float = 1.0,
    speciation_weight: float = 1.0,
    regularization_scale: float = 0.003,
) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
    pressure_frame = pressure_rows(values, vle_targets)
    speciation_frame = speciation_rows(values, spec_targets)
    residuals: list[float] = []
    pressure_scale = math.sqrt(max(float(pressure_weight), 0.0) / max(len(pressure_frame), 1))
    speciation_scale = math.sqrt(max(float(speciation_weight), 0.0) / max(len(speciation_frame), 1))
    for row in pressure_frame.to_dict("records"):
        raw = float(row["log10_model_over_data"])
        residuals.append(pressure_scale * (raw if bool(row["accepted"]) and np.isfinite(raw) else 8.0))
    for row in speciation_frame.to_dict("records"):
        raw = float(row["log10_model_over_data"])
        residuals.append(speciation_scale * (raw if bool(row["accepted"]) and np.isfinite(raw) else 8.0))
    for name in GLOBAL_FIT_NAMES:
        seed = DEFAULT_INITIAL_GUESS[name]
        residuals.append(regularization_scale * (float(values[name]) - seed) / max(abs(seed), 1.0))
    return np.asarray(residuals, dtype=float), pressure_frame, speciation_frame


def attempt_global_regression(
    *,
    max_pressure_records: int | None,
    max_speciation_records: int | None,
    max_nfev: int,
    pressure_weight: float,
    speciation_weight: float,
    regularization_scale: float,
    verbose: bool = False,
) -> dict[str, Any]:
    vle_targets, spec_targets = load_global_targets(max_pressure_records=max_pressure_records, max_speciation_records=max_speciation_records)
    base = load_initial_values()
    x0 = np.asarray([base[name] for name in GLOBAL_FIT_NAMES], dtype=float)
    initial_values = fit_vector_to_values(x0, base=base)
    attempted_optimization = int(max_nfev) >= 1 and len(vle_targets) <= 3 and len(spec_targets) <= 3
    if attempted_optimization:
        require_regression_execution_admitted()
    if attempted_optimization:
        initial_residuals, initial_pressure, initial_speciation = objective_residuals(
            initial_values,
            vle_targets,
            spec_targets,
            pressure_weight=pressure_weight,
            speciation_weight=speciation_weight,
            regularization_scale=regularization_scale,
        )
    else:
        initial_pressure = cached_pressure_rows()
        initial_speciation = cached_speciation_rows()
        initial_residuals = np.asarray([], dtype=float)
    if attempted_optimization:
        problem = native_regression.build_native_regression_problem(
            max_pressure_records=max_pressure_records,
            max_speciation_records=max_speciation_records,
            include_carbonate_born=True,
        )
        native_initial, native_lower, native_upper = native_regression.parameter_maps(problem)
        native_initial.update({key: float(base[key]) for key in native_initial if key in base})
        batch = native_regression.to_epcsaft_batch(problem)
        epcsaft = load_epcsaft()
        native_result = epcsaft.fit_reactive_electrolyte_parameters(
            batch,
            initial_parameters=native_initial,
            lower_bounds=native_lower,
            upper_bounds=native_upper,
            optimizer_backend="ceres",
            derivative_backend="autodiff",
            max_iterations=int(max_nfev),
            tolerance=1.0e-6,
            damping=1.0,
            log_parameters=True,
        )
        native_summary = epcsaft.summarize_regression_result(native_result)
        package_values = dict(getattr(native_result, "parameter_map", native_summary.get("parameter_map", {})))
        fitted_values = dict(base)
        fitted_values.update({key: float(value) for key, value in package_values.items() if key in BOUNDS})
        final_residuals, final_pressure, final_speciation = objective_residuals(
            fitted_values,
            vle_targets,
            spec_targets,
            pressure_weight=pressure_weight,
            speciation_weight=speciation_weight,
            regularization_scale=regularization_scale,
        )
        result = SimpleNamespace(
            success=bool(native_summary.get("fit_success", getattr(native_result, "success", False))),
            status=1 if bool(native_summary.get("fit_success", getattr(native_result, "success", False))) else 0,
            message=str(native_summary.get("fit_message", getattr(native_result, "message", ""))),
            nfev=int(native_summary.get("fit_iterations", getattr(native_result, "iterations", 0)) or 0),
            cost=float(0.5 * np.sum(final_residuals * final_residuals)),
            x=np.asarray([fitted_values[name] for name in GLOBAL_FIT_NAMES], dtype=float),
            native_summary=native_summary,
            native_result=(
                native_result.to_dict()
                if hasattr(native_result, "to_dict")
                else {"parameter_map": package_values}
            ),
        )
    else:
        result = SimpleNamespace(
            success=False,
            status=0,
            message=(
                "package native fit not completed: full coupled native ePC-SAFT regression was skipped because objective "
                "evaluations remain too expensive for routine execution in this repository state"
            ),
            nfev=0,
            cost=float(0.5 * np.sum(initial_residuals * initial_residuals)),
            x=x0,
            native_summary={},
            native_result={},
        )
        fitted_values = dict(initial_values)
        final_residuals = initial_residuals
        final_pressure = initial_pressure
        final_speciation = initial_speciation
    baseline_pressure_metrics = pressure_metrics(initial_pressure)
    final_pressure_metrics = pressure_metrics(final_pressure)
    baseline_speciation_metrics = speciation_metrics(initial_speciation)
    final_speciation_metrics = speciation_metrics(final_speciation)
    pressure_improved = (
        final_pressure_metrics["median_abs_log10"] is not None
        and baseline_pressure_metrics["median_abs_log10"] is not None
        and float(final_pressure_metrics["median_abs_log10"]) <= float(baseline_pressure_metrics["median_abs_log10"])
    )
    meah_ok = float(final_speciation_metrics.get("MEAH+", {}).get("median_abs_log10", np.inf)) <= 0.15
    meacoo_ok = float(final_speciation_metrics.get("MEACOO-", {}).get("median_abs_log10", np.inf)) <= 0.10
    moved_count = sum(abs(float(fitted_values[name]) - float(initial_values[name])) > 1.0e-6 for name in GLOBAL_FIT_NAMES)
    completed = bool(result.success) and pressure_improved and meah_ok and meacoo_ok and moved_count >= 3
    completion_status = "completed" if completed else "package_fit_not_completed"
    selected_values = dict(fitted_values if completed else initial_values)
    selected_parameter_set = "global_regression" if completed else "fixed_provisional_parameter_set"
    claim_boundary = (
        "Coupled pressure plus speciation regression completed with a selected fitted parameter set."
        if completed
        else (
            "A coupled pressure plus speciation regression was not completed. The selected parameter set remains the "
            "fixed provisional input set, and its results are reported only as fixed-parameter residual diagnostics."
        )
    )
    return {
        "vle_targets": vle_targets,
        "spec_targets": spec_targets,
        "result": result,
        "initial_values": initial_values,
        "fitted_values": fitted_values,
        "selected_values": selected_values,
        "selected_parameter_set": selected_parameter_set,
        "initial_residuals": initial_residuals,
        "final_residuals": final_residuals,
        "initial_pressure": initial_pressure,
        "final_pressure": final_pressure,
        "initial_speciation": initial_speciation,
        "final_speciation": final_speciation,
        "baseline_pressure_metrics": baseline_pressure_metrics,
        "pressure_metrics": final_pressure_metrics,
        "baseline_speciation_metrics": baseline_speciation_metrics,
        "speciation_metrics": final_speciation_metrics,
        "pressure_improved": pressure_improved,
        "meah_ok": meah_ok,
        "meacoo_ok": meacoo_ok,
        "moved_count": moved_count,
        "completion_status": completion_status,
        "claim_boundary": claim_boundary,
        "objective_weights": {
            "pressure_weight": float(pressure_weight),
            "speciation_weight": float(speciation_weight),
            "regularization_scale": float(regularization_scale),
        },
        "attempted_optimization": attempted_optimization,
    }


def write_global_artifacts(payload: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    lower, upper = fit_bounds()
    initial_pressure = payload["initial_pressure"].copy()
    initial_pressure.insert(0, "fit_stage", "initial")
    final_pressure = payload["final_pressure"].copy()
    final_pressure.insert(0, "fit_stage", "final")
    pressure_fit = pd.concat([initial_pressure, final_pressure], ignore_index=True)
    selected_pressure = payload["final_pressure"] if payload["selected_parameter_set"] == "global_regression" else payload["initial_pressure"]
    write_csv(output_dir / "global_regression_pressure_fit_data.csv", pressure_fit)
    write_csv(output_dir / "global_regression_pressure_residuals.csv", selected_pressure)

    initial_speciation = payload["initial_speciation"].copy()
    initial_speciation.insert(0, "fit_stage", "initial")
    final_speciation = payload["final_speciation"].copy()
    final_speciation.insert(0, "fit_stage", "final")
    speciation_fit = pd.concat([initial_speciation, final_speciation], ignore_index=True)
    selected_speciation = payload["final_speciation"] if payload["selected_parameter_set"] == "global_regression" else payload["initial_speciation"]
    write_csv(output_dir / "global_regression_speciation_fit_data.csv", speciation_fit)
    write_csv(output_dir / "global_regression_speciation_residuals.csv", selected_speciation)

    values_rows = []
    for name, lo, hi in zip(GLOBAL_FIT_NAMES, lower, upper):
        initial = float(payload["initial_values"][name])
        fitted = float(payload["fitted_values"][name])
        values_rows.append(
            {
                "parameter": name,
                "initial": initial,
                "fitted": fitted,
                "delta": fitted - initial,
                "lower_bound": float(lo),
                "upper_bound": float(hi),
                "at_bound": bool(np.isclose(fitted, lo, atol=1.0e-7) or np.isclose(fitted, hi, atol=1.0e-7)),
                "source_status": "selected" if payload["selected_parameter_set"] == "global_regression" else "attempted_only",
            }
        )
    write_csv(output_dir / "global_regression_values.csv", values_rows)

    summary = {
        "fit_tier": "pressure_speciation_global",
        "completion_status": payload["completion_status"],
        "fit_parameters": list(GLOBAL_FIT_NAMES),
        "objective_weights": payload["objective_weights"],
        "target_counts": {
            "pressure": len(payload["vle_targets"]),
            "speciation": len(payload["spec_targets"]),
        },
        "optimizer": {
            "owner": "epcsaft",
            "native_function": "fit_reactive_electrolyte_parameters",
            "success": bool(payload["result"].success),
            "status": int(payload["result"].status),
            "message": str(payload["result"].message),
            "nfev": int(payload["result"].nfev),
            "cost": float(payload["result"].cost),
        },
        "native_regression_summary": getattr(payload["result"], "native_summary", {}),
        "native_regression_result": getattr(payload["result"], "native_result", {}),
        "attempted_optimization": bool(payload["attempted_optimization"]),
        "initial_values": {name: float(payload["initial_values"][name]) for name in GLOBAL_FIT_NAMES},
        "fitted_values": {name: float(payload["fitted_values"][name]) for name in GLOBAL_FIT_NAMES},
        "selected_values": {key: float(value) for key, value in payload["selected_values"].items()},
        "selected_parameter_set": payload["selected_parameter_set"],
        "parameters_at_bounds": {row["parameter"]: row["at_bound"] for row in values_rows},
        "baseline_pressure_metrics": payload["baseline_pressure_metrics"],
        "pressure_metrics": payload["pressure_metrics"],
        "baseline_speciation_metrics": payload["baseline_speciation_metrics"],
        "speciation_metrics": payload["speciation_metrics"],
        "claim_boundary": payload["claim_boundary"],
    }
    write_json(output_dir / "global_regression_summary.json", summary)
    return summary


def write_pressure_parity(frame: pd.DataFrame, output_dir: Path) -> None:
    title = "Global pressure parity for selected full-ionic parameter set"
    description = (
        "Observed and model carbon-dioxide partial pressures are compared on log axes for the "
        "selected full-ionic parameter set."
    )
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    finite = frame[["observed_pressure_Pa", "model_pressure_Pa", "source"]].replace([np.inf, -np.inf], np.nan).dropna()
    for source, subset in finite.groupby("source"):
        ax.scatter(
            subset["observed_pressure_Pa"],
            subset["model_pressure_Pa"],
            label=str(source),
            alpha=0.7,
            edgecolor="black",
            linewidth=0.3,
        )
    if not finite.empty:
        lo = float(finite[["observed_pressure_Pa", "model_pressure_Pa"]].min().min()) * 0.7
        hi = float(finite[["observed_pressure_Pa", "model_pressure_Pa"]].max().max()) * 1.3
        ax.plot([lo, hi], [lo, hi], "k:")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
    ax.set_xlabel("Observed $CO_2$ pressure, Pa")
    ax.set_ylabel("Model $CO_2$ pressure, Pa")
    finish_axes(ax, title=title)
    ax.legend(fontsize=8, title="Literature source")
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(fig, output_dir / "global_regression_pressure_parity")
    plt.close(fig)
    write_mpl_sidecar(
        output_dir / "global_regression_pressure_parity.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=output_dir / "global_regression_pressure_fit_data.csv",
        style_source="src/MEA/epcsaft_ionic/global_regression.py",
    )


def write_speciation_parity(frame: pd.DataFrame, output_dir: Path) -> None:
    title = "Global speciation parity for selected full-ionic parameter set"
    description = (
        "Observed and model true-species mole fractions are compared on log axes for the "
        "selected full-ionic parameter set."
    )
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    finite = frame[["observed_mole_fraction", "model_mole_fraction", "species"]].replace([np.inf, -np.inf], np.nan).dropna()
    for species, subset in finite.groupby("species"):
        ax.scatter(
            subset["observed_mole_fraction"],
            subset["model_mole_fraction"],
            label=species_label(str(species)),
            color=species_color(str(species)),
            alpha=0.75,
            edgecolor="black",
            linewidth=0.3,
        )
    if not finite.empty:
        lo = max(1.0e-8, float(finite[["observed_mole_fraction", "model_mole_fraction"]].min().min()) * 0.7)
        hi = min(1.0, float(finite[["observed_mole_fraction", "model_mole_fraction"]].max().max()) * 1.3)
        ax.plot([lo, hi], [lo, hi], "k:")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
    ax.set_xlabel("Observed true-species mole fraction")
    ax.set_ylabel("Model true-species mole fraction")
    finish_axes(ax, title=title)
    ax.legend(fontsize=8, title="Species")
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(fig, output_dir / "global_regression_speciation_parity")
    plt.close(fig)
    write_mpl_sidecar(
        output_dir / "global_regression_speciation_parity.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=output_dir / "global_regression_speciation_fit_data.csv",
        style_source="src/MEA/epcsaft_ionic/global_regression.py",
    )


def compute_summary_metrics(values: dict[str, float], live_subset: tuple[int, int] | None = None) -> dict[str, float]:
    if live_subset is None:
        parameter_set, _ = load_working_parameter_set()
    else:
        parameter_set = "live_subset"
    if parameter_set == "fixed_provisional_parameter_set":
        pressure = cached_pressure_rows()
        speciation = cached_speciation_rows()
    else:
        max_pressure, max_speciation = live_subset if live_subset is not None else (None, None)
        pressure = pressure_rows(values, load_vle_targets(max_pressure))
        speciation = speciation_rows(values, load_speciation_targets(max_speciation))
    spec_metrics = speciation_metrics(speciation)
    return {
        "pressure_median_abs_log10": float(pressure_metrics(pressure)["median_abs_log10"] or np.nan),
        "MEAH+_median_abs_log10": float(spec_metrics.get("MEAH+", {}).get("median_abs_log10", np.nan)),
        "MEACOO-_median_abs_log10": float(spec_metrics.get("MEACOO-", {}).get("median_abs_log10", np.nan)),
        "HCO3-_median_abs_log10": float(spec_metrics.get("HCO3-", {}).get("median_abs_log10", np.nan)),
        "CO3^2-_median_abs_log10": float(spec_metrics.get("CO3^2-", {}).get("median_abs_log10", np.nan)),
    }


def write_sensitivity_artifacts() -> dict[str, Any]:
    parameter_set, base_values = load_working_parameter_set()
    baseline = compute_summary_metrics(base_values, live_subset=(2, 2))
    rows: list[dict[str, Any]] = []
    vectors: dict[str, list[float]] = {}
    for parameter in SENSITIVITY_PARAMETERS:
        trial = dict(base_values)
        value = float(trial[parameter])
        if parameter.startswith("k_ij__"):
            step = 1.0e-3
            role = "fitted" if parameter in GLOBAL_FIT_NAMES else "fixed_diagnostic"
        else:
            step = max(abs(value), 1.0) * 1.0e-3
            role = "fitted" if parameter in GLOBAL_FIT_NAMES else "fixed_diagnostic"
        trial[parameter] = value + step
        perturbed = compute_summary_metrics(trial, live_subset=(2, 2))
        vectors[parameter] = []
        for metric_name in SENSITIVITY_METRICS:
            derivative = (perturbed[metric_name] - baseline[metric_name]) / step
            vectors[parameter].append(float(derivative))
            rows.append(
                {
                    "parameter": parameter,
                    "role": role,
                    "metric": metric_name,
                    "baseline_value": baseline[metric_name],
                    "perturbed_value": perturbed[metric_name],
                    "step_size": step,
                    "sensitivity": derivative,
                }
            )
    SENSITIVITY_DIR.mkdir(parents=True, exist_ok=True)
    matrix = pd.DataFrame(rows)
    write_csv(SENSITIVITY_DIR / "parameter_sensitivity_matrix.csv", matrix)

    correlations: dict[str, float] = {}
    ordered = list(vectors)
    for idx, parameter in enumerate(ordered):
        for other in ordered[idx + 1 :]:
            left = np.asarray(vectors[parameter], dtype=float)
            right = np.asarray(vectors[other], dtype=float)
            if np.all(np.isfinite(left)) and np.all(np.isfinite(right)) and np.std(left) > 0.0 and np.std(right) > 0.0:
                correlations[f"{parameter}::{other}"] = float(np.corrcoef(left, right)[0, 1])
    ident_rows = []
    norms = {parameter: float(np.linalg.norm(np.asarray(vectors[parameter], dtype=float))) for parameter in ordered}
    max_norm = max(norms.values()) if norms else 1.0
    ranks = {parameter: rank + 1 for rank, parameter in enumerate(sorted(ordered, key=lambda item: norms[item], reverse=True))}
    for parameter in ordered:
        norm = norms[parameter]
        correlated = any(abs(value) > 0.98 and (parameter in key.split("::")) for key, value in correlations.items())
        near_zero = norm < 1.0e-4
        if near_zero:
            interpretation = "Near-zero sensitivity on the tracked metrics."
        elif correlated:
            interpretation = "Material sensitivity, but vector is highly correlated with another parameter."
        else:
            interpretation = "Material standalone sensitivity on the tracked metrics."
        ident_rows.append(
            {
                "parameter": parameter,
                "norm_sensitivity": norm,
                "relative_rank": ranks[parameter],
                "near_zero_sensitivity": near_zero,
                "high_correlation_risk": correlated,
                "interpretation": interpretation,
            }
        )
    write_csv(SENSITIVITY_DIR / "parameter_identifiability.csv", ident_rows)
    summary = {
        "parameter_set": parameter_set,
        "baseline_metrics": baseline,
        "parameters": list(SENSITIVITY_PARAMETERS),
        "metric_names": list(SENSITIVITY_METRICS),
        "max_norm_sensitivity": max_norm,
    }
    write_json(SENSITIVITY_DIR / "parameter_sensitivity_summary.json", summary)
    return summary


def write_sensitivity_heatmap(parameters: list[str], vectors: dict[str, list[float]]) -> None:
    title = "Local parameter sensitivity across reported metrics"
    description = (
        "Finite-difference local sensitivities are displayed by parameter and reported metric "
        "to screen dominant pressure and speciation directions."
    )
    matrix = np.asarray([vectors[name] for name in parameters], dtype=float)
    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    image = ax.imshow(matrix, aspect="auto", cmap="coolwarm")
    ax.set_yticks(range(len(parameters)), parameters)
    ax.set_xticks(range(len(SENSITIVITY_METRICS)), SENSITIVITY_METRICS, rotation=35, ha="right")
    ax.set_xlabel("Reported metric")
    ax.set_ylabel("Parameter")
    ax.set_title(title)
    fig.colorbar(image, ax=ax, label="Finite-difference sensitivity")
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(fig, SENSITIVITY_DIR / "parameter_sensitivity_heatmap")
    plt.close(fig)
    write_mpl_sidecar(
        SENSITIVITY_DIR / "parameter_sensitivity_heatmap.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=SENSITIVITY_DIR / "parameter_sensitivity_matrix.csv",
        style_source="src/MEA/epcsaft_ionic/global_regression.py",
    )
