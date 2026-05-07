from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import brentq

from MEA.epcsaft_neutral.runtime import build_neutral_mixture, normalize_composition


R_GAS = 8.31446261815324


@dataclass(frozen=True)
class NeutralPressureResult:
    success: bool
    message: str
    pressure_kPa: float
    total_pressure_Pa: float
    y_vapor: np.ndarray
    x_liquid: np.ndarray
    fugacity_residual: np.ndarray
    bubble_residual: float
    iterations: int
    method: str
    equilibrium_split_detected: bool | None
    equilibrium_message: str | None
    liquid_fugacity_pressure_kPa: float


def _ln_phi(mixture: Any, T: float, P: float, composition: np.ndarray, phase: str) -> np.ndarray:
    state = mixture.state(T, composition, P=P, phase=phase)
    return np.asarray(state.fugacity_coefficient(natural_log=True), dtype=float)


def liquid_fugacity_pressure_kpa(T: float, x_liquid: np.ndarray, pressure_Pa: float = 101325.0) -> float:
    mixture = build_neutral_mixture()
    x = normalize_composition(x_liquid)
    ln_phi_liq = _ln_phi(mixture, T, float(pressure_Pa), x, "liq")
    return float(x[0] * np.exp(ln_phi_liq[0]) * pressure_Pa / 1000.0)


def _bubble_eval(
    mixture: Any,
    T: float,
    P: float,
    x_liquid: np.ndarray,
    y_seed: np.ndarray | None,
    max_inner_iterations: int,
    tolerance: float,
) -> tuple[float, np.ndarray, np.ndarray, int]:
    x = normalize_composition(x_liquid)
    y = normalize_composition(y_seed if y_seed is not None else np.array([0.98, 0.01, 0.01], dtype=float))
    ln_phi_liq = _ln_phi(mixture, T, P, x, "liq")
    residual = np.full_like(x, np.nan)
    for iteration in range(1, max_inner_iterations + 1):
        ln_phi_vap = _ln_phi(mixture, T, P, y, "vap")
        ln_k = ln_phi_liq - ln_phi_vap
        k_values = np.exp(np.clip(ln_k, -80.0, 80.0))
        bubble_sum = float(np.dot(x, k_values))
        y_new = normalize_composition(x * k_values)
        residual = np.log(np.maximum(y_new, 1.0e-300)) + ln_phi_vap - np.log(np.maximum(x, 1.0e-300)) - ln_phi_liq
        if np.max(np.abs(y_new - y)) <= tolerance:
            return bubble_sum - 1.0, y_new, residual, iteration
        y = 0.5 * y + 0.5 * y_new
        y = normalize_composition(y)
    return bubble_sum - 1.0, y, residual, max_inner_iterations


def _bracket_pressure(
    mixture: Any,
    T: float,
    x_liquid: np.ndarray,
    y_seed: np.ndarray | None,
    pressure_guess_Pa: float | None,
) -> tuple[float, float]:
    candidates = np.geomspace(1.0, 5.0e7, 40).tolist()
    values: list[tuple[float, float]] = []
    for pressure in sorted({float(max(1.0, item)) for item in candidates}):
        try:
            value, _, _, _ = _bubble_eval(mixture, T, pressure, x_liquid, y_seed, 80, 1.0e-10)
        except Exception:
            continue
        if np.isfinite(value):
            values.append((pressure, float(value)))
    for (p0, f0), (p1, f1) in zip(values, values[1:]):
        if f0 == 0.0:
            return p0, p0
        if f0 * f1 < 0.0:
            return p0, p1
    raise RuntimeError("could not bracket neutral ePC-SAFT bubble pressure")


def predict_co2_pressure_kpa(
    T: float,
    x_liquid: np.ndarray,
    *,
    pressure_guess_Pa: float | None = None,
    y_seed: np.ndarray | None = None,
) -> NeutralPressureResult:
    mixture = build_neutral_mixture()
    x = normalize_composition(x_liquid)
    fallback_kpa = float("nan")
    try:
        fallback_kpa = liquid_fugacity_pressure_kpa(T, x)
        p_low, p_high = _bracket_pressure(mixture, T, x, y_seed, pressure_guess_Pa)
        if p_low == p_high:
            pressure = p_low
        else:
            pressure = float(
                brentq(
                    lambda p: _bubble_eval(mixture, T, p, x, y_seed, 80, 1.0e-10)[0],
                    p_low,
                    p_high,
                    xtol=1.0e-5,
                    rtol=1.0e-10,
                    maxiter=80,
                )
            )
        bubble_residual, y_vapor, fugacity_residual, iterations = _bubble_eval(mixture, T, pressure, x, y_seed, 120, 1.0e-11)
        equilibrium_split_detected: bool | None = None
        equilibrium_message: str | None = None
        try:
            epcsaft = __import__("epcsaft")
            options = epcsaft.EquilibriumOptions(max_iterations=100, tolerance=1.0e-6, stability_precheck=False)
            result = mixture.equilibrium(kind="tp_flash", T=T, P=pressure, z=x, options=options)
            equilibrium_split_detected = bool(result.split_detected)
            equilibrium_message = str(result.diagnostics.get("message", result.diagnostics.get("point_solver_message", "")))
        except Exception as exc:
            equilibrium_message = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        pressure_kpa = float(pressure * y_vapor[0] / 1000.0)
        success = bool(np.isfinite(pressure_kpa) and pressure_kpa > 0.0 and abs(bubble_residual) <= 5.0e-6)
        return NeutralPressureResult(
            success=success,
            message="solved" if success else "bubble residual above tolerance",
            pressure_kPa=pressure_kpa,
            total_pressure_Pa=float(pressure),
            y_vapor=y_vapor,
            x_liquid=x,
            fugacity_residual=fugacity_residual,
            bubble_residual=float(bubble_residual),
            iterations=int(iterations),
            method="bubble_pressure_phi_iteration",
            equilibrium_split_detected=equilibrium_split_detected,
            equilibrium_message=equilibrium_message,
            liquid_fugacity_pressure_kPa=fallback_kpa,
        )
    except Exception as exc:
        return NeutralPressureResult(
            success=False,
            message=f"{type(exc).__name__}: {str(exc).splitlines()[0]}",
            pressure_kPa=float("nan"),
            total_pressure_Pa=float("nan"),
            y_vapor=np.full(3, np.nan),
            x_liquid=x,
            fugacity_residual=np.full(3, np.nan),
            bubble_residual=float("nan"),
            iterations=0,
            method="bubble_pressure_phi_iteration",
            equilibrium_split_detected=None,
            equilibrium_message=None,
            liquid_fugacity_pressure_kPa=fallback_kpa,
        )
