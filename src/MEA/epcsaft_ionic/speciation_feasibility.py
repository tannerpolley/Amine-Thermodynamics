"""MEA-owned reactive-state solver used only by the provider feasibility experiment."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Protocol

import numpy as np
from scipy.optimize import least_squares

from MEA.smith_missen.ideal_speciation import (
    REACTION_IDS,
    REACTION_MATRIX,
    SOLVER_TOLERANCE,
    SPECIES_9,
    SPECIES_INDEX,
    _component_totals,
    _named_residuals,
    equilibrium_log_constants,
    solve_ideal_speciation,
    unloaded_water_to_amine_ratio,
)

ACTIVITY_CONVENTION = "mole_fraction_activity"


@dataclass(frozen=True)
class ActivityState:
    """Provider output admitted by the fixed MEA reaction catalog."""

    log_activities: np.ndarray
    convention: str
    diagnostics: dict[str, Any]


class ActivityEvaluator(Protocol):
    def evaluate(
        self,
        temperature_K: float,
        pressure_Pa: float,
        mole_fractions: np.ndarray,
    ) -> ActivityState: ...


@dataclass(frozen=True)
class ActivitySpeciationResult:
    species: tuple[str, ...]
    mole_fractions: np.ndarray
    residuals: dict[str, float]
    max_abs_residual: float
    success: bool
    message: str
    provider_evaluations: int
    elapsed_seconds: float
    activity_diagnostics: dict[str, Any]


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = np.asarray(values, dtype=float)
    shifted -= float(np.max(shifted))
    exp_values = np.exp(shifted)
    return exp_values / float(np.sum(exp_values))


def _charge_balanced_composition(reduced_variables: np.ndarray) -> np.ndarray:
    """Map seven log ratios to the interior of the charge-balanced simplex."""

    y = np.asarray(reduced_variables, dtype=float)
    if y.shape != (7,):
        raise ValueError(f"expected seven charge-balanced variables; got {y.shape}")
    neutral = np.exp(np.clip(np.array([y[0], y[1], 0.0]), -700.0, 700.0))
    charge_amount = float(np.exp(np.clip(y[2], -700.0, 700.0)))
    cation_fractions = _softmax(np.array([y[3], 0.0]))
    anion_charge_fractions = _softmax(np.array([y[4], y[5], y[6], 0.0]))

    amounts = np.zeros(len(SPECIES_9), dtype=float)
    amounts[[SPECIES_INDEX[name] for name in ("CO2", "MEA", "H2O")]] = neutral
    amounts[SPECIES_INDEX["MEAH+"]] = charge_amount * cation_fractions[0]
    amounts[SPECIES_INDEX["H3O+"]] = charge_amount * cation_fractions[1]
    amounts[SPECIES_INDEX["MEACOO-"]] = charge_amount * anion_charge_fractions[0]
    amounts[SPECIES_INDEX["HCO3-"]] = charge_amount * anion_charge_fractions[1]
    amounts[SPECIES_INDEX["CO3^2-"]] = charge_amount * anion_charge_fractions[2] / 2.0
    amounts[SPECIES_INDEX["OH-"]] = charge_amount * anion_charge_fractions[3]
    return amounts / float(np.sum(amounts))


def _to_charge_balanced_variables(mole_fractions: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(mole_fractions, dtype=float), 1.0e-300, None)
    x /= float(np.sum(x))
    water = x[SPECIES_INDEX["H2O"]]
    positive_charge = x[SPECIES_INDEX["MEAH+"]] + x[SPECIES_INDEX["H3O+"]]
    negative_charge = (
        x[SPECIES_INDEX["MEACOO-"]]
        + x[SPECIES_INDEX["HCO3-"]]
        + 2.0 * x[SPECIES_INDEX["CO3^2-"]]
        + x[SPECIES_INDEX["OH-"]]
    )
    charge_amount = 0.5 * (positive_charge + negative_charge)
    return np.array(
        [
            np.log(x[SPECIES_INDEX["CO2"]] / water),
            np.log(x[SPECIES_INDEX["MEA"]] / water),
            np.log(charge_amount / water),
            np.log(x[SPECIES_INDEX["MEAH+"]] / x[SPECIES_INDEX["H3O+"]]),
            np.log(x[SPECIES_INDEX["MEACOO-"]] / x[SPECIES_INDEX["OH-"]]),
            np.log(x[SPECIES_INDEX["HCO3-"]] / x[SPECIES_INDEX["OH-"]]),
            np.log(2.0 * x[SPECIES_INDEX["CO3^2-"]] / x[SPECIES_INDEX["OH-"]]),
        ],
        dtype=float,
    )


def _validate_activity_state(state: ActivityState) -> np.ndarray:
    if state.convention != ACTIVITY_CONVENTION:
        raise ValueError(
            f"activity evaluator must prove convention={ACTIVITY_CONVENTION!r}; got {state.convention!r}"
        )
    log_activities = np.asarray(state.log_activities, dtype=float)
    if log_activities.shape != (len(SPECIES_9),):
        raise ValueError(f"activity evaluator returned shape {log_activities.shape}; expected {(len(SPECIES_9),)}")
    if not np.all(np.isfinite(log_activities)):
        raise ValueError("activity evaluator returned nonfinite log activities")
    return log_activities


def _raw_residuals(
    reduced_variables: np.ndarray,
    *,
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    pressure_Pa: float,
    evaluator: ActivityEvaluator,
) -> tuple[np.ndarray, ActivityState]:
    x = _charge_balanced_composition(reduced_variables)
    activity_state = evaluator.evaluate(temperature_K, pressure_Pa, x)
    log_activities = _validate_activity_state(activity_state)
    reaction_residuals = REACTION_MATRIX @ log_activities - equilibrium_log_constants(temperature_K)
    carbon_total, amine_total, water_total, charge = _component_totals(x)
    water_per_amine = unloaded_water_to_amine_ratio(mea_weight_fraction)
    balance_residuals = np.array(
        [
            (carbon_total - loading * amine_total) / max(amine_total, 1.0e-300),
            (water_total - water_per_amine * amine_total) / max(water_total, 1.0e-300),
            charge / max(amine_total, 1.0e-300),
        ],
        dtype=float,
    )
    return np.concatenate([reaction_residuals, balance_residuals]), activity_state


def solve_activity_speciation(
    *,
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    pressure_Pa: float,
    evaluator: ActivityEvaluator,
    initial_mole_fractions: np.ndarray | None = None,
    max_nfev: int = 1000,
) -> ActivitySpeciationResult:
    """Solve the fixed MEA reaction system over an admitted activity evaluator."""

    if initial_mole_fractions is None:
        initial_mole_fractions = solve_ideal_speciation(
            loading,
            mea_weight_fraction,
            temperature_K,
        ).mole_fractions
    start = _to_charge_balanced_variables(np.asarray(initial_mole_fractions, dtype=float))
    provider_evaluations = 0
    latest_diagnostics: dict[str, Any] = {}

    def scaled_residuals(reduced_variables: np.ndarray) -> np.ndarray:
        nonlocal provider_evaluations, latest_diagnostics
        raw, activity_state = _raw_residuals(
            reduced_variables,
            loading=float(loading),
            mea_weight_fraction=float(mea_weight_fraction),
            temperature_K=float(temperature_K),
            pressure_Pa=float(pressure_Pa),
            evaluator=evaluator,
        )
        provider_evaluations += 1
        latest_diagnostics = dict(activity_state.diagnostics)
        scaled = raw.copy()
        scaled[: len(REACTION_IDS)] /= 10.0
        scaled[len(REACTION_IDS) :] *= 10.0
        return scaled[:-1]

    started = perf_counter()
    solution = least_squares(
        scaled_residuals,
        start,
        max_nfev=max_nfev,
        ftol=1.0e-11,
        xtol=1.0e-11,
        gtol=1.0e-11,
    )
    mole_fractions = _charge_balanced_composition(solution.x)
    raw, activity_state = _raw_residuals(
        solution.x,
        loading=float(loading),
        mea_weight_fraction=float(mea_weight_fraction),
        temperature_K=float(temperature_K),
        pressure_Pa=float(pressure_Pa),
        evaluator=evaluator,
    )
    provider_evaluations += 1
    latest_diagnostics = dict(activity_state.diagnostics)
    elapsed_seconds = perf_counter() - started
    max_abs_residual = float(np.max(np.abs(raw)))
    success = bool(solution.success and max_abs_residual <= SOLVER_TOLERANCE)
    return ActivitySpeciationResult(
        species=SPECIES_9,
        mole_fractions=mole_fractions,
        residuals=_named_residuals(raw),
        max_abs_residual=max_abs_residual,
        success=success,
        message=str(solution.message),
        provider_evaluations=provider_evaluations,
        elapsed_seconds=elapsed_seconds,
        activity_diagnostics=latest_diagnostics,
    )
