from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from MEA.common.data_access import regression_split_hash
from MEA.epcsaft_ionic.model import (
    BOUNDS,
    DEFAULT_INITIAL_GUESS,
    FIT_DATASET_DIR,
    SPECIES_INDEX,
    SpeciationTarget,
    load_speciation_targets,
    load_vle_targets,
    reactive_bubble_acceptance,
    solve_activity_speciation,
    solve_reactive_bubble_targets,
    state_for_x,
)
from MEA.epcsaft_runtime import diagnostic_composition, load_epcsaft


REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = REPO_ROOT / "analyses" / "phase3" / "ionic_epcsaft_regression"
OUTPUT_DIR = ANALYSIS_ROOT / "results" / "scipy_regression_experiment"
VOLUMETRIC_CONTRACT = (
    REPO_ROOT
    / "data"
    / "reference"
    / "MEA"
    / "manifests"
    / "ionic_volumetric_observation_contract.csv"
)
VOLUMETRIC_SPLIT = (
    REPO_ROOT
    / "data"
    / "reference"
    / "MEA"
    / "manifests"
    / "volumetric_grouped_split_manifest.csv"
)

SHARED_SIGMA_NAME = "shared_ion_sigma"
SHARED_SIGMA_BOUNDS = BOUNDS["MEAH+__s"]
HISTORICAL_VALUES = {
    "MEAH+__s": 3.48508556586174,
    "MEACOO-__s": 3.535435257213276,
}
FAMILY_WEIGHT = 0.5
FAILURE_RESIDUAL = 8.0
FINITE_DIFFERENCE_STEP = 1.0e-3
NEIGHBORHOOD_STEP = 1.0e-4
BOUND_DISTANCE_TOLERANCE = 1.0e-4
NEAR_BEST_COST_FRACTION = 0.01
MAX_NEAR_BEST_SCALED_SPREAD = 0.02
EQUILIBRIUM_MAX_ITERATIONS = 240


@dataclass(frozen=True)
class DensityTarget:
    observation_id: str
    temperature_K: float
    mea_weight_fraction: float
    loading: float
    density_kg_m3: float
    uncertainty_kg_m3: float
    group_id: str
    split: str


@dataclass(frozen=True)
class Evaluation:
    residuals: np.ndarray
    rows: pd.DataFrame
    summary: dict[str, Any]


class CandidateEvaluator:
    def __init__(
        self,
        speciation_targets: list[SpeciationTarget],
        density_targets: list[DensityTarget],
    ) -> None:
        self.speciation_targets = speciation_targets
        self.density_targets = density_targets
        self._cache: dict[tuple[float, ...], Evaluation] = {}
        self.evaluation_count = 0

        source_counts = Counter(target.source for target in speciation_targets)
        self.speciation_scales = {
            target.row_id: math.sqrt(
                FAMILY_WEIGHT
                / max(len(source_counts), 1)
                / source_counts[target.source]
                / max(len(_positive_targets(target)), 1)
            )
            for target in speciation_targets
        }
        group_counts = Counter(target.group_id for target in density_targets)
        self.density_scales = {
            target.observation_id: math.sqrt(
                FAMILY_WEIGHT
                / max(len(group_counts), 1)
                / group_counts[target.group_id]
            )
            for target in density_targets
        }

    def evaluate_scaled(self, scaled: Iterable[float]) -> Evaluation:
        vector = np.asarray(tuple(scaled), dtype=float)
        key = tuple(np.round(vector, decimals=12))
        if key not in self._cache:
            self._cache[key] = evaluate_values(
                scaled_to_values(vector),
                self.speciation_targets,
                self.density_targets,
                self.speciation_scales,
                self.density_scales,
            )
            self.evaluation_count += 1
        return self._cache[key]

    def residuals(self, scaled: Iterable[float]) -> np.ndarray:
        return self.evaluate_scaled(scaled).residuals


def solve_speciation_with_retries(
    *,
    loading: float,
    temperature_K: float,
    pressure_Pa: float,
    initial_x: np.ndarray,
    mea_weight_fraction: float,
    values: dict[str, float],
):
    seeds = [np.asarray(initial_x, dtype=float)]
    diagnostic_seed = diagnostic_composition(loading)
    if not np.allclose(seeds[0], diagnostic_seed, rtol=0.0, atol=1.0e-14):
        seeds.append(diagnostic_seed)
    attempts = (
        (EQUILIBRIUM_MAX_ITERATIONS, 0.5),
        (400, 0.2),
        (400, 0.7),
    )
    failures: list[str] = []
    last_prediction = None
    for seed in seeds:
        for max_iterations, damping in attempts:
            try:
                prediction = solve_activity_speciation(
                    loading,
                    temperature_K,
                    pressure_Pa,
                    seed,
                    values,
                    FIT_DATASET_DIR,
                    mea_weight_fraction,
                    max_iterations=max_iterations,
                    damping=damping,
                )
                last_prediction = prediction
                if prediction.accepted:
                    return prediction, ""
                failures.append(
                    prediction.rejection_reason
                    or prediction.message
                    or "rejected equilibrium state"
                )
            except Exception as exc:
                failures.append(f"{type(exc).__name__}: {str(exc).splitlines()[0]}")
    return last_prediction, "; ".join(dict.fromkeys(failures))


def _positive_targets(target: SpeciationTarget) -> dict[str, float]:
    values = dict(target.target_speciation)
    values.update(target.aggregate_targets)
    return values


def load_density_targets(role: str) -> list[DensityTarget]:
    contract = pd.read_csv(VOLUMETRIC_CONTRACT)
    split = pd.read_csv(VOLUMETRIC_SPLIT)
    rows = contract.merge(
        split[["observation_id", "split", "role"]],
        on="observation_id",
        validate="one_to_one",
    )
    rows = rows[
        (rows["data_family"] == "reactive_mea_density")
        & (rows["source_key"] == "Amundsen2009")
        & (rows["target_eligible"] == "yes")
        & (rows["role"] == role)
    ].copy()
    targets = [
        DensityTarget(
            observation_id=str(row.observation_id),
            temperature_K=float(row.temperature_K),
            mea_weight_fraction=float(row.mea_mass_fraction),
            loading=float(row.co2_loading_mol_per_mol_mea),
            density_kg_m3=1000.0 * float(row.value_reported),
            uncertainty_kg_m3=1000.0 * float(row.uncertainty_value),
            group_id=str(row.group_id),
            split=str(row.split),
        )
        for row in rows.itertuples()
    ]
    if not targets:
        raise RuntimeError(f"No reactive MEA density targets have role {role!r}")
    return targets


def scaled_to_values(
    scaled: Iterable[float],
) -> dict[str, float]:
    vector = np.asarray(tuple(scaled), dtype=float)
    if vector.shape != (1,):
        raise ValueError("The experiment fits exactly one shared ion diameter.")
    lower, upper = SHARED_SIGMA_BOUNDS
    sigma = float(lower + vector[0] * (upper - lower))
    values = dict(DEFAULT_INITIAL_GUESS)
    values["MEAH+__s"] = sigma
    values["MEACOO-__s"] = sigma
    values[SHARED_SIGMA_NAME] = sigma
    return values


def values_to_scaled(
    values: Mapping[str, float],
) -> np.ndarray:
    sigma = 0.5 * (float(values["MEAH+__s"]) + float(values["MEACOO-__s"]))
    lower, upper = SHARED_SIGMA_BOUNDS
    return np.asarray([(sigma - lower) / (upper - lower)], dtype=float)


def _prediction_value(prediction_x: np.ndarray, name: str) -> float:
    if name == "MEA + MEAH+":
        return float(
            prediction_x[SPECIES_INDEX["MEA"]] + prediction_x[SPECIES_INDEX["MEAH+"]]
        )
    return float(prediction_x[SPECIES_INDEX[name]])


def evaluate_values(
    values: dict[str, float],
    speciation_targets: list[SpeciationTarget],
    density_targets: list[DensityTarget],
    speciation_scales: Mapping[str, float],
    density_scales: Mapping[str, float],
) -> Evaluation:
    residuals: list[float] = []
    rows: list[dict[str, Any]] = []
    failure_states: set[str] = set()

    for target in speciation_targets:
        observed_targets = _positive_targets(target)
        scale = speciation_scales[target.row_id]
        prediction = None
        reason = ""
        try:
            prediction, reason = solve_speciation_with_retries(
                loading=target.loading,
                temperature_K=target.T,
                pressure_Pa=target.P,
                initial_x=target.x,
                mea_weight_fraction=target.mea_weight_fraction,
                values=values,
            )
            if prediction is None or not prediction.accepted:
                prediction = None
        except Exception as exc:
            reason = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"

        if prediction is None:
            failure_states.add(target.row_id)
        for name, observed in observed_targets.items():
            predicted = (
                np.nan if prediction is None else _prediction_value(prediction.x, name)
            )
            raw = (
                math.log10(max(predicted, 1.0e-30) / observed)
                if np.isfinite(predicted) and predicted >= 0.0
                else FAILURE_RESIDUAL
            )
            residuals.append(scale * raw)
            rows.append(
                {
                    "target_family": "speciation",
                    "record_id": target.row_id,
                    "source": target.source,
                    "group_id": target.group_id,
                    "split": target.split,
                    "observable": name,
                    "observed": observed,
                    "predicted": predicted,
                    "unit": "mole_fraction",
                    "raw_residual": raw,
                    "scaled_residual": scale * raw,
                    "accepted": prediction is not None,
                    "failure_reason": reason,
                }
            )

    for target in density_targets:
        scale = density_scales[target.observation_id]
        prediction = None
        density = np.nan
        reason = ""
        try:
            initial_x = diagnostic_composition(target.loading)
            prediction, reason = solve_speciation_with_retries(
                loading=target.loading,
                temperature_K=target.temperature_K,
                pressure_Pa=101325.0,
                initial_x=initial_x,
                mea_weight_fraction=target.mea_weight_fraction,
                values=values,
            )
            if prediction is None or not prediction.accepted:
                prediction = None
            else:
                density = float(
                    state_for_x(
                        prediction.x,
                        target.temperature_K,
                        101325.0,
                        values,
                        FIT_DATASET_DIR,
                    ).mass_density()
                )
                if not np.isfinite(density) or density <= 0.0:
                    reason = "nonfinite or nonpositive mass density"
                    prediction = None
        except Exception as exc:
            reason = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"

        if prediction is None:
            failure_states.add(target.observation_id)
            raw = FAILURE_RESIDUAL
        else:
            raw = math.log10(density / target.density_kg_m3)
        residuals.append(scale * raw)
        rows.append(
            {
                "target_family": "density",
                "record_id": target.observation_id,
                "source": "Amundsen2009",
                "group_id": target.group_id,
                "split": target.split,
                "observable": "mass_density",
                "observed": target.density_kg_m3,
                "predicted": density,
                "unit": "kg/m^3",
                "uncertainty": target.uncertainty_kg_m3,
                "raw_residual": raw,
                "scaled_residual": scale * raw,
                "accepted": prediction is not None,
                "failure_reason": reason,
            }
        )

    frame = pd.DataFrame(rows)
    summary = summarize_predictions(frame)
    summary["failure_state_count"] = len(failure_states)
    summary["failure_states"] = sorted(failure_states)
    return Evaluation(np.asarray(residuals, dtype=float), frame, summary)


def summarize_predictions(frame: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for family, family_rows in frame.groupby("target_family"):
        accepted = family_rows[family_rows["accepted"].astype(bool)]
        raw = accepted["raw_residual"].astype(float).to_numpy()
        metrics: dict[str, Any] = {
            "record_count": int(family_rows["record_id"].nunique()),
            "residual_count": int(len(family_rows)),
            "accepted_residual_count": int(len(accepted)),
            "failure_residual_count": int(len(family_rows) - len(accepted)),
            "rmse_log10": float(np.sqrt(np.mean(raw * raw))) if raw.size else None,
            "median_abs_log10": float(np.median(np.abs(raw))) if raw.size else None,
            "max_abs_log10": float(np.max(np.abs(raw))) if raw.size else None,
        }
        if family == "density" and not accepted.empty:
            relative = (
                accepted["predicted"].astype(float).to_numpy()
                / accepted["observed"].astype(float).to_numpy()
                - 1.0
            )
            standardized = (
                accepted["predicted"].astype(float).to_numpy()
                - accepted["observed"].astype(float).to_numpy()
            ) / accepted["uncertainty"].astype(float).to_numpy()
            metrics.update(
                {
                    "rmse_relative_percent": float(
                        100.0 * np.sqrt(np.mean(relative * relative))
                    ),
                    "median_abs_relative_percent": float(
                        100.0 * np.median(np.abs(relative))
                    ),
                    "rmse_standardized": float(
                        np.sqrt(np.mean(standardized * standardized))
                    ),
                }
            )
        summary[str(family)] = metrics
    return summary


def _objective_cost(residuals: np.ndarray) -> float:
    return float(0.5 * np.dot(residuals, residuals))


def deterministic_starts() -> list[tuple[str, float]]:
    return [
        ("literature_seed", values_to_scaled(DEFAULT_INITIAL_GUESS)[0]),
        ("historical_fit", values_to_scaled(HISTORICAL_VALUES)[0]),
        ("intermediate_size", values_to_scaled({"MEAH+__s": 4.5, "MEACOO-__s": 4.5})[0]),
        ("coarse_minimum", values_to_scaled({"MEAH+__s": 5.25, "MEACOO-__s": 5.25})[0]),
    ]


def run_multistart(
    evaluator: CandidateEvaluator,
    *,
    max_nfev: int,
) -> tuple[Any, pd.DataFrame]:
    attempts: list[dict[str, Any]] = []
    results: list[Any] = []
    for label, start_scaled in deterministic_starts():
        start = np.asarray([start_scaled], dtype=float)
        started = time.monotonic()
        result = least_squares(
            evaluator.residuals,
            start,
            bounds=(np.zeros(len(start)), np.ones(len(start))),
            jac="2-point",
            diff_step=FINITE_DIFFERENCE_STEP,
            loss="linear",
            x_scale="jac",
            ftol=1.0e-7,
            xtol=1.0e-7,
            gtol=1.0e-7,
            max_nfev=max_nfev,
        )
        evaluation = evaluator.evaluate_scaled(result.x)
        fitted = scaled_to_values(result.x)
        attempts.append(
            {
                "start": label,
                "optimizer_success": bool(result.success),
                "status": int(result.status),
                "message": str(result.message),
                "nfev": int(result.nfev),
                "njev": int(result.njev) if result.njev is not None else None,
                "elapsed_seconds": time.monotonic() - started,
                "cost": _objective_cost(evaluation.residuals),
                "failure_state_count": int(evaluation.summary["failure_state_count"]),
                SHARED_SIGMA_NAME: fitted[SHARED_SIGMA_NAME],
            }
        )
        print(
            f"{label}: cost={attempts[-1]['cost']:.8g}, "
            f"failures={attempts[-1]['failure_state_count']}, "
            f"nfev={attempts[-1]['nfev']}",
            file=sys.stderr,
            flush=True,
        )
        results.append(result)

    attempt_frame = (
        pd.DataFrame(attempts)
        .sort_values(["failure_state_count", "cost", "start"])
        .reset_index(drop=True)
    )
    best_label = str(attempt_frame.iloc[0]["start"])
    best_result = results[
        [label for label, _ in deterministic_starts()].index(best_label)
    ]
    return best_result, attempt_frame


def multistart_stability(
    attempts: pd.DataFrame,
) -> dict[str, Any]:
    best_cost = float(attempts.iloc[0]["cost"])
    near = attempts[
        (attempts["failure_state_count"] == 0)
        & (attempts["cost"] <= best_cost * (1.0 + NEAR_BEST_COST_FRACTION))
    ]
    lower, upper = SHARED_SIGMA_BOUNDS
    spread = (
        float(
            (near[SHARED_SIGMA_NAME].max() - near[SHARED_SIGMA_NAME].min())
            / (upper - lower)
        )
        if len(near)
        else float("inf")
    )
    return {
        "near_best_attempt_count": int(len(near)),
        "near_best_cost_fraction": NEAR_BEST_COST_FRACTION,
        "scaled_parameter_spread": spread,
    }


def neighborhood_robustness(
    evaluator: CandidateEvaluator,
    scaled: np.ndarray,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    step = min(NEIGHBORHOOD_STEP, scaled[0] / 2.0, (1.0 - scaled[0]) / 2.0)
    for direction in (-1.0, 1.0):
        point = scaled.copy()
        point[0] += direction * step
        evaluation = evaluator.evaluate_scaled(point)
        rows.append(
            {
                "direction": "lower" if direction < 0.0 else "upper",
                "scaled_step": step,
                "cost": _objective_cost(evaluation.residuals),
                "failure_state_count": int(
                    evaluation.summary["failure_state_count"]
                ),
            }
        )
    return {
        "scaled_step": NEIGHBORHOOD_STEP,
        "evaluations": rows,
        "all_states_accepted": all(row["failure_state_count"] == 0 for row in rows),
    }


def evaluate_pressure(
    values: dict[str, float],
    *,
    role: str,
    parameter_set: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    targets = load_vle_targets(role=role)
    results = solve_reactive_bubble_targets(targets, values, FIT_DATASET_DIR)
    rows: list[dict[str, Any]] = []
    for target, result in zip(targets, results):
        predicted = np.nan
        accepted = False
        reason = ""
        try:
            if isinstance(result, Exception):
                raise result
            decision = reactive_bubble_acceptance(result)
            predicted = float(result.partial_pressures.get("CO2", np.nan)) / 1000.0
            accepted = bool(
                decision.accepted and np.isfinite(predicted) and predicted > 0.0
            )
            reason = (
                "" if accepted else decision.rejection_reason or str(result.message)
            )
        except Exception as exc:
            reason = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        residual = (
            math.log10(predicted / target.pressure_kPa)
            if accepted
            else FAILURE_RESIDUAL
        )
        rows.append(
            {
                "parameter_set": parameter_set,
                "role": role,
                "record_id": target.row_id,
                "source": target.source_key,
                "group_id": target.group_id,
                "temperature_K": target.T,
                "mea_weight_fraction": target.mea_weight_fraction,
                "co2_loading_mol_per_mol_mea": target.loading,
                "observed_co2_pressure_kPa": target.pressure_kPa,
                "predicted_co2_pressure_kPa": predicted,
                "log10_model_over_data": residual,
                "accepted": accepted,
                "failure_reason": reason,
            }
        )
    frame = pd.DataFrame(rows)
    accepted_rows = frame[frame["accepted"].astype(bool)]
    residuals = accepted_rows["log10_model_over_data"].astype(float).to_numpy()
    summary = {
        "record_count": len(frame),
        "accepted_count": len(accepted_rows),
        "failure_count": len(frame) - len(accepted_rows),
        "rmse_log10": float(np.sqrt(np.mean(residuals * residuals)))
        if residuals.size
        else None,
        "median_abs_log10": float(np.median(np.abs(residuals)))
        if residuals.size
        else None,
        "max_abs_log10": float(np.max(np.abs(residuals))) if residuals.size else None,
    }
    return frame, summary


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.bool_, np.integer)):
        return value.item()
    if isinstance(value, np.floating):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Cannot encode {type(value).__name__}")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old_output in OUTPUT_DIR.iterdir():
        if old_output.is_file():
            old_output.unlink()
    training_speciation = load_speciation_targets(role="active_training")
    validation_speciation = load_speciation_targets(role="reserved_validation")
    training_density = load_density_targets("future_training")
    validation_density = load_density_targets("reserved_validation")

    fit_evaluator = CandidateEvaluator(
        training_speciation,
        training_density,
    )
    baseline_scaled = values_to_scaled(DEFAULT_INITIAL_GUESS)
    baseline_training = fit_evaluator.evaluate_scaled(baseline_scaled)
    best_result, attempts = run_multistart(fit_evaluator, max_nfev=args.max_nfev)
    candidate_values = scaled_to_values(best_result.x)
    candidate_training = fit_evaluator.evaluate_scaled(best_result.x)
    jacobian_norm = float(np.linalg.norm(np.asarray(best_result.jac, dtype=float)))
    stability = multistart_stability(attempts)
    neighborhood = neighborhood_robustness(fit_evaluator, best_result.x)

    validation_source_counts = Counter(
        target.source for target in validation_speciation
    )
    validation_speciation_scales = {
        target.row_id: math.sqrt(
            FAMILY_WEIGHT
            / max(len(validation_source_counts), 1)
            / validation_source_counts[target.source]
            / max(len(_positive_targets(target)), 1)
        )
        for target in validation_speciation
    }
    validation_group_counts = Counter(target.group_id for target in validation_density)
    validation_density_scales = {
        target.observation_id: math.sqrt(
            FAMILY_WEIGHT
            / max(len(validation_group_counts), 1)
            / validation_group_counts[target.group_id]
        )
        for target in validation_density
    }
    baseline_validation = evaluate_values(
        dict(DEFAULT_INITIAL_GUESS),
        validation_speciation,
        validation_density,
        validation_speciation_scales,
        validation_density_scales,
    )
    candidate_validation = evaluate_values(
        candidate_values,
        validation_speciation,
        validation_density,
        validation_speciation_scales,
        validation_density_scales,
    )

    pressure_frames: list[pd.DataFrame] = []
    pressure_summary: dict[str, Any] = {}
    if not args.skip_pressure:
        for parameter_set, values in (
            ("baseline", dict(DEFAULT_INITIAL_GUESS)),
            ("candidate", candidate_values),
        ):
            for role in ("active_training", "reserved_validation"):
                frame, metrics = evaluate_pressure(
                    values,
                    role=role,
                    parameter_set=parameter_set,
                )
                pressure_frames.append(frame)
                pressure_summary[f"{parameter_set}_{role}"] = metrics
                print(
                    f"pressure {parameter_set} {role}: "
                    f"failures={metrics['failure_count']}, "
                    f"median_abs_log10={metrics['median_abs_log10']:.6g}",
                    file=sys.stderr,
                    flush=True,
                )

    active_bound = min(best_result.x[0], 1.0 - best_result.x[0]) <= BOUND_DISTANCE_TOLERANCE
    validation_improved = _objective_cost(
        candidate_validation.residuals
    ) < _objective_cost(baseline_validation.residuals)
    pressure_preserved = False
    if pressure_summary:
        candidate_training_pressure = pressure_summary["candidate_active_training"]
        baseline_pressure = pressure_summary["baseline_reserved_validation"]
        candidate_pressure = pressure_summary["candidate_reserved_validation"]
        pressure_preserved = bool(
            candidate_training_pressure["failure_count"] == 0
            and candidate_pressure["failure_count"] == 0
            and candidate_pressure["median_abs_log10"]
            <= 1.05 * baseline_pressure["median_abs_log10"]
        )
    gates = {
        "optimizer_success": bool(best_result.success),
        "training_failure_free": candidate_training.summary["failure_state_count"] == 0,
        "validation_failure_free": candidate_validation.summary["failure_state_count"]
        == 0,
        "active_jacobian_nonzero": jacobian_norm > 1.0e-6,
        "no_active_parameter_bound": not active_bound,
        "multistart_stable": stability["near_best_attempt_count"] >= 2
        and stability["scaled_parameter_spread"] <= MAX_NEAR_BEST_SCALED_SPREAD,
        "local_neighborhood_failure_free": neighborhood["all_states_accepted"],
        "reserved_validation_objective_improved": validation_improved,
        "reserved_pressure_evaluated": bool(pressure_summary),
        "reserved_pressure_preserved": pressure_preserved,
    }
    accepted = all(gates.values())
    summary = {
        "schema_version": 1,
        "status": (
            "accepted_experimental_candidate"
            if accepted
            else "experiment_did_not_establish_publishable_parameters"
        ),
        "claim_boundary": (
            "This is an MEA-owned SciPy identifiability and regression experiment. "
            "It does not satisfy the production native-regression gate or promote a parameter bundle."
        ),
        "fixed_contract": {
            "training_counts": {
                "speciation_states": len(training_speciation),
                "loaded_density_rows": len(training_density),
            },
            "validation_counts": {
                "speciation_states": len(validation_speciation),
                "loaded_density_rows": len(validation_density),
            },
            "pressure_speciation_split_sha256": regression_split_hash(),
            "volumetric_split_path": str(VOLUMETRIC_SPLIT.relative_to(REPO_ROOT)),
            "fit_parameters": [SHARED_SIGMA_NAME],
            "active_set_rationale": (
                "Fit one shared effective segment diameter for MEAH+ and MEACOO-. Bulk "
                "electroneutral density cannot separately identify the cation and anion "
                "diameters. Keep dispersion energies, Born diameters, reaction constants, "
                "and ion-pair interactions fixed because the admitted evidence does not "
                "independently identify them."
            ),
            "fixed_parameters": [
                name
                for name in DEFAULT_INITIAL_GUESS
                if name not in {"MEAH+__s", "MEACOO-__s"}
            ],
            "objective": (
                "Equal density/speciation family weights; speciation sources, states, and measured "
                "positive targets are normalized equally; density groups and rows are normalized equally."
            ),
            "zero_observation_policy": (
                "Reported zeros remain validation diagnostics but are not optimized because the sources "
                "do not provide numerical detection limits."
            ),
            "failed_state_policy": (
                f"Each failed state receives fixed residual {FAILURE_RESIDUAL:g}; any final training "
                "or validation failure rejects the candidate."
            ),
        },
        "runtime": {
            "epcsaft_version": str(load_epcsaft().__version__),
            "fit_objective_evaluations": fit_evaluator.evaluation_count,
        },
        "active_parameter_identifiability": {
            "parameter": SHARED_SIGMA_NAME,
            "scaled_jacobian_norm": jacobian_norm,
        },
        "multistart_stability": stability,
        "local_neighborhood_robustness": neighborhood,
        "optimizer": {
            "success": bool(best_result.success),
            "status": int(best_result.status),
            "message": str(best_result.message),
            "nfev": int(best_result.nfev),
            "njev": int(best_result.njev) if best_result.njev is not None else None,
            "baseline_cost": _objective_cost(baseline_training.residuals),
            "candidate_cost": _objective_cost(candidate_training.residuals),
        },
        "candidate_values": {
            SHARED_SIGMA_NAME: candidate_values[SHARED_SIGMA_NAME]
        },
        "candidate_eos_values": {
            "MEAH+__s": candidate_values["MEAH+__s"],
            "MEACOO-__s": candidate_values["MEACOO-__s"],
        },
        "training": {
            "baseline": baseline_training.summary,
            "candidate": candidate_training.summary,
        },
        "validation": {
            "baseline": baseline_validation.summary,
            "candidate": candidate_validation.summary,
            "baseline_cost": _objective_cost(baseline_validation.residuals),
            "candidate_cost": _objective_cost(candidate_validation.residuals),
        },
        "pressure": pressure_summary,
        "acceptance_gates": gates,
    }

    attempts.to_csv(OUTPUT_DIR / "multistart_attempts.csv", index=False)
    pd.concat(
        [
            baseline_training.rows.assign(parameter_set="baseline"),
            candidate_training.rows.assign(parameter_set="candidate"),
        ],
        ignore_index=True,
    ).to_csv(OUTPUT_DIR / "training_predictions.csv", index=False)
    pd.concat(
        [
            baseline_validation.rows.assign(parameter_set="baseline"),
            candidate_validation.rows.assign(parameter_set="candidate"),
        ],
        ignore_index=True,
    ).to_csv(OUTPUT_DIR / "validation_predictions.csv", index=False)
    if pressure_frames:
        pd.concat(pressure_frames, ignore_index=True).to_csv(
            OUTPUT_DIR / "pressure_predictions.csv",
            index=False,
        )
    write_json(OUTPUT_DIR / "experiment_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the bounded downstream SciPy reactive-regression experiment."
    )
    parser.add_argument(
        "--max-nfev",
        type=int,
        default=24,
        help="Maximum residual evaluations per deterministic optimizer start.",
    )
    parser.add_argument(
        "--skip-pressure",
        action="store_true",
        help="Skip the expensive full frozen pressure evaluation.",
    )
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2, sort_keys=True, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
