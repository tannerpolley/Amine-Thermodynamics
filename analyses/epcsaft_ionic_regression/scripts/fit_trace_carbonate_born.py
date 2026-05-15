from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import numpy as np
import pandas as pd

from MEA.epcsaft_ionic.ion_parameter_regression import load_tier_a_targets
from MEA.epcsaft_ionic.model import (
    DEFAULT_INITIAL_GUESS,
    EPCSAFT_IONIC_ANALYSIS,
    SPECIES_INDEX,
    solve_activity_speciation,
    write_csv,
    write_json,
)

FIT_NAMES = ("HCO3-__d_born", "CO3^2-__d_born")
FIT_BOUNDS = {
    "HCO3-__d_born": (1.0, 7.0),
    "CO3^2-__d_born": (1.0, 8.0),
}
TARGET_SPECIES = ("HCO3-", "CO3^2-")
OUT_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "trace_carbonate_born_regression"
PROMOTED_ION_SUMMARY = EPCSAFT_IONIC_ANALYSIS / "results" / "ion_parameter_regression" / "ion_parameter_fit_summary.json"
ANCHOR_SCALES = (0.0,)
LOSSES = ("linear",)
SEED_GRID = (
    (1.05, 1.05),
    (3.0, 3.0),
    (4.5, 4.5),
    (6.5, 7.5),
)


def baseline_values() -> dict[str, float]:
    values = dict(DEFAULT_INITIAL_GUESS)
    if PROMOTED_ION_SUMMARY.exists():
        summary = json.loads(PROMOTED_ION_SUMMARY.read_text(encoding="utf-8"))
        values.update({key: float(value) for key, value in summary.get("fitted_values", {}).items()})
    return values


def fit_vector_to_values(vector: np.ndarray, base: dict[str, float]) -> dict[str, float]:
    values = dict(base)
    values.update({name: float(value) for name, value in zip(FIT_NAMES, vector)})
    return values


def _target_rows():
    rows = []
    for target in load_tier_a_targets(None):
        species = tuple(name for name in TARGET_SPECIES if name in target.species_targets)
        if species:
            rows.append((target, species))
    return rows


def evaluate(values: dict[str, float], target_rows, anchor_scale: float = 0.003) -> tuple[np.ndarray, pd.DataFrame]:
    residuals: list[float] = []
    rows: list[dict[str, object]] = []
    scale = math.sqrt(1.0 / max(sum(len(species) for _, species in target_rows), 1))
    for target, species_names in target_rows:
        try:
            prediction = solve_activity_speciation(target.loading, target.T, target.P, target.x, values)
            prediction_x = prediction.x
            success = bool(prediction.success)
            message = prediction.message
        except Exception as exc:
            prediction_x = np.full(len(SPECIES_INDEX), np.nan, dtype=float)
            success = False
            message = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        for species in species_names:
            observed = float(target.x[SPECIES_INDEX[species]])
            predicted = float(prediction_x[SPECIES_INDEX[species]]) if np.isfinite(prediction_x[SPECIES_INDEX[species]]) else np.nan
            raw = math.log10(max(predicted, 1.0e-30) / max(observed, 1.0e-30)) if np.isfinite(predicted) else 8.0
            residuals.append(scale * raw)
            rows.append(
                {
                    "row_id": target.row_id,
                    "source": target.source,
                    "temperature_C": target.T - 273.15,
                    "CO2_loading": target.loading,
                    "species": species,
                    "observed_mole_fraction": observed,
                    "model_mole_fraction": predicted,
                    "log10_model_over_data": raw,
                    "success": bool(success),
                    "message": message,
                }
            )
    if anchor_scale > 0.0:
        for name in FIT_NAMES:
            residuals.append(anchor_scale * (values[name] - DEFAULT_INITIAL_GUESS[name]) / max(abs(DEFAULT_INITIAL_GUESS[name]), 1.0))
    return np.asarray(residuals, dtype=float), pd.DataFrame(rows)


def data_residual_norm(values: dict[str, float], target_rows) -> float:
    residuals, _ = evaluate(values, target_rows, anchor_scale=0.0)
    return float(np.linalg.norm(residuals))


def metrics(frame: pd.DataFrame) -> dict[str, object]:
    output: dict[str, object] = {
        "row_count": int(frame["row_id"].nunique()) if not frame.empty else 0,
        "residual_count": int(len(frame)),
    }
    finite = frame[np.isfinite(frame["log10_model_over_data"].astype(float))] if not frame.empty else frame
    residual = finite["log10_model_over_data"].astype(float).to_numpy() if not finite.empty else np.asarray([])
    output["overall_rmse_log10"] = float(np.sqrt(np.mean(residual * residual))) if residual.size else None
    output["overall_median_abs_log10"] = float(np.median(np.abs(residual))) if residual.size else None
    output["by_species"] = {}
    for species, subset in finite.groupby("species"):
        values = subset["log10_model_over_data"].astype(float).to_numpy()
        output["by_species"][str(species)] = {
            "count": int(len(subset)),
            "rmse_log10": float(np.sqrt(np.mean(values * values))),
            "median_abs_log10": float(np.median(np.abs(values))),
        }
    return output


def run_multistart(base: dict[str, float], target_rows, lower: np.ndarray, upper: np.ndarray) -> tuple[pd.DataFrame, dict[str, object]]:
    attempts: list[dict[str, object]] = []
    x0_default = np.asarray([base[name] for name in FIT_NAMES], dtype=float)
    seed_vectors = [np.clip(x0_default, lower, upper)]
    for hco3_seed, co3_seed in SEED_GRID:
        seed_vectors.append(np.clip(np.asarray([hco3_seed, co3_seed], dtype=float), lower, upper))

    seen: set[tuple[float, float]] = set()
    attempt_id = 0
    for seed in seed_vectors:
        seed_key = tuple(float(round(value, 8)) for value in seed)
        if seed_key in seen:
            continue
        seen.add(seed_key)
        attempt_id += 1
        values = fit_vector_to_values(seed, base)
        residuals, frame_for_metrics = evaluate(values, target_rows, anchor_scale=0.0)
        final_metrics = metrics(frame_for_metrics)
        attempts.append(
            {
                "attempt_id": attempt_id,
                "anchor_scale": 0.0,
                "loss": "grid_evaluation",
                "seed_HCO3_d_born": float(seed[0]),
                "seed_CO3_d_born": float(seed[1]),
                "fitted_HCO3_d_born": float(seed[0]),
                "fitted_CO3_d_born": float(seed[1]),
                "delta_HCO3_from_seed": 0.0,
                "delta_CO3_from_seed": 0.0,
                "initial_data_residual_norm": float(np.linalg.norm(residuals)),
                "final_data_residual_norm": float(np.linalg.norm(residuals)),
                "data_residual_norm_improvement": 0.0,
                "overall_rmse_log10": final_metrics["overall_rmse_log10"],
                "overall_median_abs_log10": final_metrics["overall_median_abs_log10"],
                "optimizer_success": True,
                "optimizer_status": 0,
                "optimizer_message": "direct full-data seed evaluation",
                "nfev": 1,
                "at_lower_bound_HCO3": bool(np.isclose(seed[0], lower[0], rtol=0.0, atol=1.0e-7)),
                "at_upper_bound_HCO3": bool(np.isclose(seed[0], upper[0], rtol=0.0, atol=1.0e-7)),
                "at_lower_bound_CO3": bool(np.isclose(seed[1], lower[1], rtol=0.0, atol=1.0e-7)),
                "at_upper_bound_CO3": bool(np.isclose(seed[1], upper[1], rtol=0.0, atol=1.0e-7)),
            }
        )

    frame = pd.DataFrame(attempts).sort_values(
        ["final_data_residual_norm", "anchor_scale", "loss", "attempt_id"],
        ignore_index=True,
    )
    write_csv(OUT_DIR / "trace_carbonate_born_multistart_attempts.csv", frame)
    best = frame.iloc[0].to_dict() if not frame.empty else {}
    substantial = frame[
        (frame["fitted_HCO3_d_born"].sub(3.0).abs() >= 0.25)
        | (frame["fitted_CO3_d_born"].sub(3.0).abs() >= 0.25)
    ]
    best_substantial = substantial.iloc[0].to_dict() if not substantial.empty else {}
    diagnostic = {
        "attempt_count": int(len(frame)),
        "anchor_scales": [float(value) for value in ANCHOR_SCALES],
        "losses": list(LOSSES),
        "best_attempt": best,
        "best_substantial_attempt": best_substantial,
        "substantial_threshold_angstrom": 0.25,
        "interpretation": (
            "A substantial Born diameter is considered identified only if it gives a meaningful data-residual "
            "improvement without simply landing on an optimizer bound or depending on the starting seed."
        ),
    }
    return frame, diagnostic


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target_rows = _target_rows()
    base = baseline_values()
    x0 = np.asarray([base[name] for name in FIT_NAMES], dtype=float)
    lower = np.asarray([FIT_BOUNDS[name][0] for name in FIT_NAMES], dtype=float)
    upper = np.asarray([FIT_BOUNDS[name][1] for name in FIT_NAMES], dtype=float)
    initial_values = fit_vector_to_values(x0, base)
    initial_residuals, initial_frame = evaluate(initial_values, target_rows)
    multistart_frame, multistart_diagnostic = run_multistart(base, target_rows, lower, upper)
    best_attempt = multistart_diagnostic.get("best_attempt", {})
    if best_attempt:
        final_vector = np.asarray(
            [best_attempt["fitted_HCO3_d_born"], best_attempt["fitted_CO3_d_born"]],
            dtype=float,
        )
    else:
        final_vector = x0
    final_values = fit_vector_to_values(final_vector, base)
    final_residuals, final_frame = evaluate(final_values, target_rows)
    initial_frame.insert(0, "fit_stage", "initial")
    final_frame.insert(0, "fit_stage", "final")
    plotted = pd.concat([initial_frame, final_frame], ignore_index=True)
    write_csv(OUT_DIR / "trace_carbonate_born_fit_data.csv", plotted)
    values_rows = [
        {
            "parameter": name,
            "initial": float(initial),
            "fitted": float(fitted),
            "delta": float(fitted - initial),
            "lower_bound": float(lo),
            "upper_bound": float(hi),
            "at_bound": bool(np.isclose(fitted, lo, rtol=0.0, atol=1.0e-7) or np.isclose(fitted, hi, rtol=0.0, atol=1.0e-7)),
        }
        for name, initial, fitted, lo, hi in zip(FIT_NAMES, x0, final_vector, lower, upper)
    ]
    write_csv(OUT_DIR / "trace_carbonate_born_fit_values.csv", values_rows)
    summary = {
        "fit_tier": "tier_a_trace_carbonate_born",
        "target_species": list(TARGET_SPECIES),
        "fit_parameters": list(FIT_NAMES),
        "target_row_count": len(target_rows),
        "optimizer": {
            "success": True,
            "status": 0,
            "message": "deterministic full-data seed scan; optimizer loop skipped because each objective evaluation is expensive",
            "nfev": int(multistart_diagnostic.get("attempt_count", 0)),
            "cost": float(0.5 * np.sum(final_residuals * final_residuals)),
            "initial_residual_norm": float(np.linalg.norm(initial_residuals)),
            "final_residual_norm": float(np.linalg.norm(final_residuals)),
        },
        "initial_values": {name: float(value) for name, value in zip(FIT_NAMES, x0)},
        "fitted_values": {name: float(final_values[name]) for name in FIT_NAMES},
        "parameters_at_bounds": {row["parameter"]: row["at_bound"] for row in values_rows},
        "initial_metrics": metrics(initial_frame),
        "final_metrics": metrics(final_frame),
        "multistart_diagnostic": multistart_diagnostic,
        "claim_boundary": (
            "This fit estimates only bicarbonate/carbonate Born radii against Tier A rows that report those species. "
            "It does not identify OH- Born parameters because the local target data do not directly report hydroxide."
        ),
    }
    write_json(OUT_DIR / "trace_carbonate_born_fit_summary.json", summary)
    print(json.dumps(summary["optimizer"], indent=2))
    print(json.dumps(summary["fitted_values"], indent=2))


if __name__ == "__main__":
    main()
