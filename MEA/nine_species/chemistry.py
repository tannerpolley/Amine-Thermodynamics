from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from MEA.nine_species.gekko_solver import get_x_guess, solve_ChEq


TRACE_FLOOR = 1e-14
RESIDUAL_TOL = 1e-3
LOG_RESIDUAL_TOL = 5e-2

SPECIES = (
    "CO2",
    "MEA",
    "H2O",
    "MEAH^+",
    "MEACOO^-",
    "HCO3^-",
    "CO3^2-",
    "H3O^+",
    "OH^-",
)
PLOT_SPECIES = SPECIES + ("MEA + MEAH^+",)
PLOT_LABELS = {
    "CO2": "$CO_2$",
    "MEA": "$MEA$",
    "H2O": "$H_2O$",
    "MEAH^+": "$MEAH^+$",
    "MEACOO^-": "$MEACOO_-$",
    "HCO3^-": "$HCO_3^-$",
    "CO3^2-": "$CO_3^{2-}$",
    "H3O^+": "$H_3O^+$",
    "OH^-": "$OH^-$",
    "MEA + MEAH^+": "$MEA + MEAH^+$",
}


@dataclass(frozen=True)
class AllSpeciesChemistryResult:
    loading: float
    mea_weight_fraction: float
    temperature_K: float
    species: tuple[str, ...]
    x: np.ndarray
    residuals: dict[str, float]
    success: bool
    message: str
    attempts: int


def equilibrium_log_constants(temperature_K: float) -> np.ndarray:
    """Return log equilibrium constants for the nine-species legacy model."""
    constants = np.array(
        [
            (132.899, -13445.9, -22.4773, 0.0),
            (231.465, -12092.1, -36.7816, 0.0),
            (216.049, -12431.0, -35.4891, 0.0),
            (-1.8652, -1543.3, 0.0, 0.0),
            (2.1211, -8189.38, 0.0, -0.007484),
        ],
        dtype=float,
    )
    a, b, c, d = constants.T
    return a + b / temperature_K + c * np.log(temperature_K) + d * temperature_K


def reaction_matrix() -> np.ndarray:
    return np.array(
        [
            [0, 0, -2, 0, 0, 0, 0, 1, 1],
            [-1, 0, -2, 0, 0, 1, 0, 1, 0],
            [0, 0, -1, 0, 0, -1, 1, 1, 0],
            [0, 1, -1, 0, -1, 1, 0, 0, 0],
            [0, 1, -1, -1, 0, 0, 0, 1, 0],
        ],
        dtype=float,
    )


def balance_matrix() -> np.ndarray:
    return np.array(
        [
            [1, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, -1, -1, -2, 1, -1],
        ],
        dtype=float,
    )


def initial_apparent_mole_fractions(alpha: float, w_MEA_unloaded: float) -> np.ndarray:
    mw_ratio = 0.06108 / 0.01802
    x_mea_unloaded = w_MEA_unloaded / (mw_ratio + w_MEA_unloaded * (1.0 - mw_ratio))
    x_h2o_unloaded = 1.0 - x_mea_unloaded
    n_mea = x_mea_unloaded
    n_h2o = x_h2o_unloaded
    n_co2 = n_mea * alpha
    total = n_co2 + n_mea + n_h2o
    return np.array([n_co2 / total, n_mea / total, n_h2o / total], dtype=float)


def initial_all_species_mole_fractions(alpha: float, w_MEA_unloaded: float) -> np.ndarray:
    return np.concatenate([initial_apparent_mole_fractions(alpha, w_MEA_unloaded), np.zeros(6)])


def _normalize_start(x: np.ndarray) -> np.ndarray:
    start = np.asarray(x, dtype=float).copy()
    start[~np.isfinite(start)] = TRACE_FLOOR
    start = np.maximum(start, TRACE_FLOOR)
    total = float(np.sum(start))
    if total <= 0.0:
        raise ValueError("all-species initial guess has nonpositive total")
    return start / total


def all_species_residuals(x: np.ndarray, x_0: np.ndarray, log_k: np.ndarray, v_ij: np.ndarray) -> dict[str, float]:
    x = np.asarray(x, dtype=float)
    safe_x = np.maximum(x, TRACE_FLOOR)
    log_reaction_residuals = v_ij @ np.log(safe_x) - log_k

    model_carbon = x_0[0] - (x[0] + x[4] - x[5] + x[6])
    physical_carbon = x_0[0] - (x[0] + x[4] + x[5] + x[6])
    mea_balance = x_0[1] - (x[1] + x[3] + x[4])
    water_balance = x_0[2] - (x[2] + x[5] + x[6] + x[7] + x[8])
    charge_balance = (x[3] + x[7]) - (x[4] + x[5] + 2.0 * x[6] + x[8])

    residuals = {
        "sum_minus_one": float(np.sum(x) - 1.0),
        "model_carbon_balance": float(model_carbon),
        "physical_carbon_balance": float(physical_carbon),
        "mea_balance": float(mea_balance),
        "water_balance": float(water_balance),
        "charge_balance": float(charge_balance),
    }
    for idx, value in enumerate(log_reaction_residuals, start=1):
        residuals[f"logK_residual_{idx}"] = float(value)
    return residuals


def _residual_success(x: np.ndarray, residuals: dict[str, float]) -> tuple[bool, str]:
    if not np.all(np.isfinite(x)):
        return False, "nonfinite species mole fraction"
    if np.any(x < -1e-12):
        return False, "negative species mole fraction"
    balance_keys = ("physical_carbon_balance", "mea_balance", "water_balance", "charge_balance")
    max_balance = max(abs(residuals[key]) for key in balance_keys)
    max_log = max(abs(value) for key, value in residuals.items() if key.startswith("logK_residual_"))
    if max_balance > RESIDUAL_TOL:
        return False, f"balance residual {max_balance:.3e} exceeds {RESIDUAL_TOL:.1e}"
    if max_log > LOG_RESIDUAL_TOL:
        return False, f"logK residual {max_log:.3e} exceeds {LOG_RESIDUAL_TOL:.1e}"
    return True, "solved"


def _solve_once(
    loading: float,
    w_MEA_unloaded: float,
    temperature_K: float,
    start_x: np.ndarray | None,
    attempt_label: str,
) -> AllSpeciesChemistryResult:
    x_0 = initial_all_species_mole_fractions(loading, w_MEA_unloaded)
    log_k = equilibrium_log_constants(temperature_K)
    v_ij = reaction_matrix()
    s_ij = balance_matrix()

    try:
        if start_x is None:
            default_guess = np.asarray(get_x_guess(x_0, log_k, v_ij)[0], dtype=float)
            start = _normalize_start(default_guess)
        else:
            start = _normalize_start(start_x)
        scales = np.maximum(start, TRACE_FLOOR)
        scaled_guess = start / scales
        x = np.asarray(solve_ChEq(
            x_0,
            scaled_guess,
            log_k,
            v_ij,
            s_ij,
            scales,
            lower_bound=1e-10,
            max_iter=5000,
            rtol=1e-2,
            otol=1e-2,
        ), dtype=float)
        residuals = all_species_residuals(x, x_0, log_k, v_ij)
        success, message = _residual_success(x, residuals)
        return AllSpeciesChemistryResult(
            float(loading),
            float(w_MEA_unloaded),
            float(temperature_K),
            SPECIES,
            x,
            residuals,
            success,
            f"{message} ({attempt_label})",
            1,
        )
    except Exception as exc:
        return AllSpeciesChemistryResult(
            float(loading),
            float(w_MEA_unloaded),
            float(temperature_K),
            SPECIES,
            np.full(len(SPECIES), np.nan, dtype=float),
            {},
            False,
            f"{type(exc).__name__}: {str(exc).splitlines()[0]} ({attempt_label})",
            1,
        )


def solve_all_species_result(
    loading: float,
    w_MEA_unloaded: float,
    temperature_K: float,
    start_x: np.ndarray | None = None,
) -> AllSpeciesChemistryResult:
    first = _solve_once(loading, w_MEA_unloaded, temperature_K, start_x, "warm-start" if start_x is not None else "default")
    if first.success or start_x is None:
        return first
    second = _solve_once(loading, w_MEA_unloaded, temperature_K, None, "default-retry")
    if second.success:
        return AllSpeciesChemistryResult(
            second.loading,
            second.mea_weight_fraction,
            second.temperature_K,
            second.species,
            second.x,
            second.residuals,
            True,
            second.message,
            first.attempts + second.attempts,
        )
    return AllSpeciesChemistryResult(
        first.loading,
        first.mea_weight_fraction,
        first.temperature_K,
        first.species,
        first.x,
        first.residuals,
        False,
        f"{first.message}; retry: {second.message}",
        first.attempts + second.attempts,
    )


def solve_all_species_series(
    loadings: np.ndarray,
    w_MEA_unloaded: float,
    temperature_K: float,
) -> list[AllSpeciesChemistryResult]:
    ordered_loadings = [float(value) for value in loadings]
    results: list[AllSpeciesChemistryResult] = []
    previous_success: np.ndarray | None = None
    for loading in ordered_loadings:
        result = solve_all_species_result(loading, w_MEA_unloaded, temperature_K, previous_success)
        if result.success:
            previous_success = result.x
        results.append(result)

    next_success: np.ndarray | None = None
    for idx in range(len(results) - 1, -1, -1):
        result = results[idx]
        if result.success:
            next_success = result.x
            continue
        if next_success is None:
            continue
        retry = _solve_once(result.loading, w_MEA_unloaded, temperature_K, next_success, "backward-retry")
        if retry.success:
            results[idx] = AllSpeciesChemistryResult(
                retry.loading,
                retry.mea_weight_fraction,
                retry.temperature_K,
                retry.species,
                retry.x,
                retry.residuals,
                True,
                retry.message,
                result.attempts + retry.attempts,
            )
    return results


def get_true_mol_frac(alpha, w_MEA_unloaded, Tl):
    result = solve_all_species_result(float(alpha), float(w_MEA_unloaded), float(Tl))
    if not result.success:
        raise RuntimeError(f"all-species chemistry failed at loading {alpha}: {result.message}")
    return result.x.copy()


def result_rows(results: list[AllSpeciesChemistryResult]) -> list[dict[str, float | str | bool]]:
    rows = []
    for result in results:
        row: dict[str, float | str | bool] = {
            "temperature_C": result.temperature_K - 273.15,
            "MEA_weight_fraction": result.mea_weight_fraction,
            "CO2_loading": result.loading,
            "success": result.success,
            "message": result.message,
            "attempts": result.attempts,
        }
        for idx, species in enumerate(result.species):
            row[species] = float(result.x[idx]) if np.isfinite(result.x[idx]) else np.nan
        for key, value in result.residuals.items():
            row[key] = value
        rows.append(row)
    return rows
