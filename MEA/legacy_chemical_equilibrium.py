from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import root


LEGACY_SPECIES_6 = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-")
APPARENT_SPECIES_3 = ("CO2", "MEA", "H2O")

MW_MEA_G_PER_MOL = 61.084
MW_H2O_G_PER_MOL = 18.02
LEGACY_INITIAL_GUESS = np.array(
    [1.32885319e-10, 4.85942087e3, 3.92196901e4, 4.95855464e1, 4.95482234e1, 3.73230850e-2],
    dtype=float,
)


@dataclass(frozen=True)
class LegacyChemistryResult:
    loading: float
    mea_weight_fraction: float
    temperature_K: float
    apparent_x: np.ndarray
    initial_concentrations: np.ndarray
    concentrations: np.ndarray
    mole_fractions: np.ndarray
    apparent_ternary_x: np.ndarray
    residuals: dict[str, float]
    success: bool
    message: str


def apparent_feed_mole_fractions(loading: float, mea_weight_fraction: float) -> np.ndarray:
    """Return apparent CO2/MEA/H2O mole fractions from unloaded MEA wt fraction and loading."""
    x_mea_unloaded = mea_weight_fraction / (
        MW_MEA_G_PER_MOL / MW_H2O_G_PER_MOL
        + mea_weight_fraction * (1.0 - MW_MEA_G_PER_MOL / MW_H2O_G_PER_MOL)
    )
    x_h2o_unloaded = 1.0 - x_mea_unloaded

    n_mea = 100.0 * x_mea_unloaded
    n_h2o = 100.0 * x_h2o_unloaded
    n_co2 = n_mea * loading
    n_total = n_co2 + n_mea + n_h2o
    return np.array([n_co2 / n_total, n_mea / n_total, n_h2o / n_total], dtype=float)


def legacy_liquid_density_molar(temperature_K: float, apparent_x: Iterable[float]) -> tuple[float, float]:
    """Legacy empirical liquid density, returned as mol/m3 and kg/m3."""
    x_co2, x_mea, x_h2o = np.asarray(apparent_x, dtype=float)
    molecular_weights = np.array([44.01, 61.08, 18.02], dtype=float) / 1000.0
    mixture_mw = float(np.dot([x_co2, x_mea, x_h2o], molecular_weights))

    a1, b1, c1 = [-5.35162e-7, -4.51417e-4, 1.19451]
    a2, b2, c2 = [-3.2484e-6, 0.00165, 0.793]
    v_mea = molecular_weights[1] * 1000.0 / (a1 * temperature_K**2 + b1 * temperature_K + c1)
    v_h2o = molecular_weights[2] * 1000.0 / (a2 * temperature_K**2 + b2 * temperature_K + c2)

    a, b, c, d, e = 10.57920122, -2.020494157, 3.15067933, 192.0126008, -695.3848617
    v_co2 = a + (b + c * x_mea) * x_mea * x_h2o + (d + e * x_mea) * x_mea * x_co2

    molar_volume_m3_mol = (v_co2 * x_co2 + v_mea * x_mea + v_h2o * x_h2o) * 1e-6
    rho_mol_m3 = molar_volume_m3_mol**-1
    rho_mass_kg_m3 = rho_mol_m3 * mixture_mw
    return float(rho_mol_m3), float(rho_mass_kg_m3)


def legacy_equilibrium_constants(temperature_K: float) -> tuple[float, float]:
    """Concentration-basis constants from the legacy main-branch solver."""
    a1, b1, c1, d1 = 234.2, -1434.4, -36.8, -0.0074
    a2, b2, c2, d2 = 176.8, -991.2, -29.5, 0.0129
    k1 = np.exp(a1 + b1 / temperature_K + c1 * np.log(temperature_K) + d1 * temperature_K) / 1000.0
    k2 = np.exp(a2 + b2 / temperature_K + c2 * np.log(temperature_K) + d2 * temperature_K) / 1000.0
    return float(k1), float(k2)


def _scaled_residuals(concentrations: np.ndarray, initial_concentrations: np.ndarray, temperature_K: float) -> np.ndarray:
    co2_0, mea_0, h2o_0 = np.asarray(initial_concentrations, dtype=float)
    co2, mea, h2o, meah, meacoo, hco3 = np.asarray(concentrations, dtype=float)
    k1, k2 = legacy_equilibrium_constants(temperature_K)

    floor = 1e-30
    kee1 = (meah * meacoo) / (max(co2, floor) * max(mea, floor) ** 2)
    kee2 = (meah * hco3) / (max(co2, floor) * max(mea, floor) * max(h2o, floor))

    co2_scale = 20.0 if co2_0 > 3800.0 else 5.0
    return np.array(
        [
            kee1 / 100.0 - k1 / 100.0,
            kee2 / 100.0 - k2 / 100.0,
            co2_0 / co2_scale - (co2 + meah) / co2_scale,
            mea_0 / 3000.0 - (mea + meah + meacoo) / 3000.0,
            h2o_0 / 10000.0 - (h2o + meah - meacoo) / 10000.0,
            meah - (meacoo + hco3),
        ],
        dtype=float,
    )


def _solve_one_loading(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    initial_guess: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, bool, str]:
    apparent_x = apparent_feed_mole_fractions(loading, mea_weight_fraction)
    rho_mol_m3, _ = legacy_liquid_density_molar(temperature_K, apparent_x)
    initial_concentrations = apparent_x * rho_mol_m3
    solution = root(_scaled_residuals, initial_guess, args=(initial_concentrations, temperature_K))
    return (
        np.asarray(solution.x, dtype=float),
        initial_concentrations,
        bool(solution.success),
        str(solution.message),
    )


def solve_legacy_concentrations(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    initial_guess: Iterable[float] | None = None,
) -> LegacyChemistryResult:
    guess = np.asarray(initial_guess if initial_guess is not None else LEGACY_INITIAL_GUESS, dtype=float)
    concentrations, initial_concentrations, success, message = _solve_one_loading(
        loading, mea_weight_fraction, temperature_K, guess
    )
    return _build_result(
        loading,
        mea_weight_fraction,
        temperature_K,
        concentrations,
        initial_concentrations,
        success,
        message,
    )


def solve_legacy_continuation(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    alpha_grid: Iterable[float] | None = None,
) -> LegacyChemistryResult:
    """Warm-start a loading sweep and return the exact requested loading solve."""
    grid = np.asarray(list(alpha_grid) if alpha_grid is not None else np.linspace(0.002, 1.0, 100), dtype=float)
    if loading < float(grid.min()) or loading > float(grid.max()):
        raise ValueError(f"loading {loading} is outside interpolation grid [{grid.min()}, {grid.max()}]")

    guess = LEGACY_INITIAL_GUESS.copy()
    success = True
    message = "warm-started legacy loading grid"
    solve_grid = np.unique(np.concatenate([grid[grid < loading], np.array([loading], dtype=float)]))
    target_concentrations = None
    target_initial_concentrations = None
    for alpha in solve_grid:
        concentrations, initial_concentrations, step_success, step_message = _solve_one_loading(
            float(alpha), mea_weight_fraction, temperature_K, guess
        )
        guess = concentrations
        if not step_success:
            success = False
            message = step_message
        target_concentrations = concentrations
        target_initial_concentrations = initial_concentrations

    return _build_result(
        loading,
        mea_weight_fraction,
        temperature_K,
        np.asarray(target_concentrations, dtype=float),
        np.asarray(target_initial_concentrations, dtype=float),
        success,
        message,
    )


def legacy_interpolated_mole_fractions(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    alpha_grid: Iterable[float] | None = None,
) -> np.ndarray:
    """Return mole fractions by reproducing the legacy main-branch interpolation workflow."""
    grid = np.asarray(list(alpha_grid) if alpha_grid is not None else np.linspace(0.002, 1.0, 100), dtype=float)
    if loading < float(grid.min()) or loading > float(grid.max()):
        raise ValueError(f"loading {loading} is outside interpolation grid [{grid.min()}, {grid.max()}]")

    guess = LEGACY_INITIAL_GUESS.copy()
    mole_fraction_rows = []
    for alpha in grid:
        concentrations, _, _, _ = _solve_one_loading(float(alpha), mea_weight_fraction, temperature_K, guess)
        guess = concentrations
        mole_fraction_rows.append(concentrations / np.sum(concentrations))

    mole_fraction_rows = np.asarray(mole_fraction_rows, dtype=float)
    return np.array(
        [float(interp1d(grid, mole_fraction_rows[:, i], kind="linear")(loading)) for i in range(len(LEGACY_SPECIES_6))],
        dtype=float,
    )


def legacy_true_mole_fractions(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    *,
    continuation: bool = True,
) -> np.ndarray:
    if continuation:
        return legacy_interpolated_mole_fractions(loading, mea_weight_fraction, temperature_K)
    return solve_legacy_concentrations(loading, mea_weight_fraction, temperature_K).mole_fractions.copy()


def collapse_to_apparent_ternary(mole_fractions_6: Iterable[float]) -> np.ndarray:
    ternary = np.asarray(mole_fractions_6, dtype=float)[:3]
    total = float(np.sum(ternary))
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError("cannot collapse six-species composition with nonpositive apparent ternary total")
    return ternary / total


def balance_residuals(
    concentrations: Iterable[float],
    initial_concentrations: Iterable[float],
    temperature_K: float,
) -> dict[str, float]:
    concentrations = np.asarray(concentrations, dtype=float)
    initial_concentrations = np.asarray(initial_concentrations, dtype=float)
    co2_0, mea_0, h2o_0 = initial_concentrations
    co2, mea, h2o, meah, meacoo, hco3 = concentrations
    k1, k2 = legacy_equilibrium_constants(temperature_K)
    kee1 = (meah * meacoo) / (co2 * mea**2)
    kee2 = (meah * hco3) / (co2 * mea * h2o)
    return {
        "carbamate_K_residual": float(kee1 - k1),
        "bicarbonate_K_residual": float(kee2 - k2),
        "co2_balance_legacy": float(co2_0 - (co2 + meah)),
        "co2_balance_expanded": float(co2_0 - (co2 + meacoo + hco3)),
        "mea_balance": float(mea_0 - (mea + meah + meacoo)),
        "water_balance": float(h2o_0 - (h2o + meah - meacoo)),
        "electroneutrality": float(meah - (meacoo + hco3)),
    }


def _build_result(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    concentrations: np.ndarray,
    initial_concentrations: np.ndarray,
    success: bool,
    message: str,
) -> LegacyChemistryResult:
    concentrations = np.asarray(concentrations, dtype=float)
    mole_fractions = concentrations / np.sum(concentrations)
    residuals = balance_residuals(concentrations, initial_concentrations, temperature_K)
    return LegacyChemistryResult(
        loading=float(loading),
        mea_weight_fraction=float(mea_weight_fraction),
        temperature_K=float(temperature_K),
        apparent_x=apparent_feed_mole_fractions(loading, mea_weight_fraction),
        initial_concentrations=np.asarray(initial_concentrations, dtype=float),
        concentrations=concentrations,
        mole_fractions=mole_fractions,
        apparent_ternary_x=collapse_to_apparent_ternary(mole_fractions),
        residuals=residuals,
        success=success,
        message=message,
    )


def smoke_check() -> LegacyChemistryResult:
    result = solve_legacy_continuation(0.3, 0.3, 313.15)
    if not result.success:
        raise AssertionError(result.message)
    if not np.all(np.isfinite(result.mole_fractions)):
        raise AssertionError("legacy six-species mole fractions are not finite")
    if np.any(result.mole_fractions < -1e-10):
        raise AssertionError(f"legacy six-species mole fractions include negative values: {result.mole_fractions}")

    scales = {
        "co2_balance_legacy": max(1.0, result.initial_concentrations[0]),
        "co2_balance_expanded": max(1.0, result.initial_concentrations[0]),
        "mea_balance": max(1.0, result.initial_concentrations[1]),
        "water_balance": max(1.0, result.initial_concentrations[2]),
        "electroneutrality": 1.0,
    }
    for name, scale in scales.items():
        if abs(result.residuals[name]) / scale > 1e-5:
            raise AssertionError(f"{name} failed: {result.residuals[name]}")
    if abs(result.residuals["carbamate_K_residual"]) > 1e-6:
        raise AssertionError(f"carbamate K residual failed: {result.residuals['carbamate_K_residual']}")
    if abs(result.residuals["bicarbonate_K_residual"]) > 1e-7:
        raise AssertionError(f"bicarbonate K residual failed: {result.residuals['bicarbonate_K_residual']}")
    return result


if __name__ == "__main__":
    check = smoke_check()
    print("Legacy six-species smoke check passed")
    print("species:", ", ".join(LEGACY_SPECIES_6))
    print("mole_fractions:", np.array2string(check.mole_fractions, precision=8))
    print("apparent_ternary_x:", np.array2string(check.apparent_ternary_x, precision=8))
