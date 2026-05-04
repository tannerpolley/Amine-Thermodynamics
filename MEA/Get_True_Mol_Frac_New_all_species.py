from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from convex_optimization_gekko import get_x_guess, solve_ChEq
from plot_export import default_output_dir, save_plot


DATA_ROOT = Path(__file__).resolve().parents[1] / "data" / "MEA"
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
            [1, 0, 0, 0, 1, -1, 1, 0, 0],
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
    balance_keys = ("model_carbon_balance", "mea_balance", "water_balance", "charge_balance")
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


def _json_safe(value):
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def write_diagnostics(results: list[AllSpeciesChemistryResult], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = result_rows(results)
    csv_path = output_dir / "all_species_solver_diagnostics.csv"
    json_path = output_dir / "all_species_solver_summary.json"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    failures = [row for row in rows if not bool(row["success"])]
    payload = {
        "n_points": len(rows),
        "n_success": len(rows) - len(failures),
        "n_failed": len(failures),
        "failed_loadings": [row["CO2_loading"] for row in failures],
        "failures": failures,
    }
    json_path.write_text(json.dumps(_json_safe(payload), indent=2, allow_nan=False), encoding="utf-8")
    return csv_path, json_path


def _plot_failed_loadings(ax, results: list[AllSpeciesChemistryResult], y_value: float) -> None:
    failed_loadings = [result.loading for result in results if not result.success]
    if failed_loadings:
        ax.scatter(
            failed_loadings,
            np.full(len(failed_loadings), y_value),
            marker="x",
            color="black",
            label="solver failed",
            zorder=5,
        )


def main() -> int:
    w_MEA = 0.3
    temperature_K = 273.15 + 40.0
    colors = [
        "tab:green",
        "tab:blue",
        "tab:orange",
        "tab:olive",
        "tab:red",
        "tab:cyan",
        "tab:purple",
        "tab:brown",
        "tab:gray",
        "tab:pink",
    ]

    alpha = np.linspace(0.001, 0.8, 101)
    results = solve_all_species_series(alpha, w_MEA, temperature_K)
    output_dir = default_output_dir(__file__)
    csv_path, json_path = write_diagnostics(results, output_dir)

    x_rows = []
    for result in results:
        x_rows.append(result.x if result.success else np.full(len(SPECIES), np.nan, dtype=float))
    x_true_arr = np.asarray(x_rows, dtype=float).T
    x_true_arr = np.vstack([x_true_arr, x_true_arr[1] + x_true_arr[3]])

    fig, ax = plt.subplots(figsize=(10, 10))
    for species, x_true, color in zip(PLOT_SPECIES, x_true_arr, colors):
        if species == "H2O":
            continue
        ax.semilogy(alpha, x_true, "--", color=color, label=PLOT_LABELS[species])

    df = pd.read_csv(DATA_ROOT / "ChEq" / "Combined_ChEq.csv")
    df = df[(df["temperature"] == (temperature_K - 273.15)) & (df["MEA_weight_fraction"] == 0.30)]
    data_species = list(df.columns[3:-1])
    for species, color in zip(PLOT_SPECIES, colors):
        if species in data_species:
            ax.semilogy(df["CO2_loading"].to_numpy(), df[species].to_numpy(), "o", color=color)

    finite_positive = x_true_arr[np.isfinite(x_true_arr) & (x_true_arr > 0.0)]
    y_floor = 1e-12 if finite_positive.size == 0 else 10.0 ** np.floor(np.log10(float(np.min(finite_positive))))
    _plot_failed_loadings(ax, results, y_floor)

    ax.legend(loc="lower center")
    x_range = np.linspace(0.0, float(np.max(alpha)), 11)
    y_range = np.logspace(np.log10(y_floor), 0, int(abs(np.log10(y_floor))) + 1)
    ax.set_xlim(x_range[0], x_range[-1])
    ax.set_ylim(y_range[0], y_range[-1])
    ax.set_xticks(x_range)
    ax.set_yticks(y_range)
    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    plt.tick_params(labelsize=12)
    plot_path = save_plot(fig, __file__)

    n_failed = sum(not result.success for result in results)
    print(f"All-species diagnostics: {csv_path}")
    print(f"All-species summary: {json_path}")
    print(f"All-species plot: {plot_path}")
    print(f"All-species solver points: {len(results) - n_failed}/{len(results)} successful, {n_failed} failed")
    return 0 if any(result.success for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
