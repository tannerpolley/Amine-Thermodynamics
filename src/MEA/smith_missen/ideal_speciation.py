from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.optimize import least_squares

from MEA.six_species.chemistry import MW_H2O_G_PER_MOL, MW_MEA_G_PER_MOL

SPECIES_9 = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
SPECIES_INDEX = {species: index for index, species in enumerate(SPECIES_9)}
REACTION_IDS = (
    "R1_water_autoionization",
    "R2_CO2_to_HCO3",
    "R3_HCO3_to_CO3",
    "R4_MEACOO_hydrolysis",
    "R5_MEAH_dissociation",
)
REACTION_CONSTANTS = np.array(
    [
        (132.899, -13445.9, -22.4773, 0.0),
        (231.465, -12092.10, -36.7816, 0.0),
        (216.049, -12431.70, -35.4819, 0.0),
        (-1.8652, -1545.3, 0.0, 0.0),
        (2.1211, -8189.38, 0.0, -0.007484),
    ],
    dtype=float,
)
REACTION_MATRIX = np.array(
    [
        [0, 0, -2, 0, 0, 0, 0, 1, 1],
        [-1, 0, -2, 0, 0, 1, 0, 1, 0],
        [0, 0, -1, 0, 0, -1, 1, 1, 0],
        [0, 1, -1, 0, -1, 1, 0, 0, 0],
        [0, 1, -1, -1, 0, 0, 0, 1, 0],
    ],
    dtype=float,
)
MIN_LOADING = 1.0e-6
SOLVER_TOLERANCE = 1.0e-8


@dataclass(frozen=True)
class SmithMissenIdealSpeciationResult:
    loading: float
    effective_loading: float
    mea_weight_fraction: float
    temperature_K: float
    mole_fractions: np.ndarray
    residuals: dict[str, float]
    max_abs_residual: float
    success: bool
    message: str

    def species_map(self) -> dict[str, float]:
        values = {species: float(self.mole_fractions[index]) for index, species in enumerate(SPECIES_9)}
        values["MEA + MEAH+"] = values["MEA"] + values["MEAH+"]
        return values


def equilibrium_log_constants(temperature_K: float) -> np.ndarray:
    """Return mole-fraction-basis log equilibrium constants for ideal reaction-equilibrium reference."""
    constants = REACTION_CONSTANTS
    a, b, c, d = constants.T
    temperature = float(temperature_K)
    return a + b / temperature + c * np.log(temperature) + d * temperature


def unloaded_water_to_amine_ratio(mea_weight_fraction: float) -> float:
    n_mea = float(mea_weight_fraction) / MW_MEA_G_PER_MOL
    n_h2o = (1.0 - float(mea_weight_fraction)) / MW_H2O_G_PER_MOL
    return n_h2o / n_mea


def _softmax(reduced_variables: np.ndarray) -> np.ndarray:
    shifted = np.concatenate([np.asarray(reduced_variables, dtype=float), np.array([0.0])])
    shifted = shifted - float(np.max(shifted))
    exp_values = np.exp(shifted)
    return exp_values / float(np.sum(exp_values))


def _to_reduced_variables(mole_fractions: Iterable[float]) -> np.ndarray:
    x = np.clip(np.asarray(mole_fractions, dtype=float), 1.0e-300, None)
    x = x / float(np.sum(x))
    return np.log(x[:-1] / x[-1])


def _default_initial_mole_fractions(loading: float, mea_weight_fraction: float) -> np.ndarray:
    water_per_amine = unloaded_water_to_amine_ratio(mea_weight_fraction)
    amine_total = 1.0 / (1.0 + water_per_amine + loading)
    carbon_total = loading * amine_total
    water_total = water_per_amine * amine_total

    values = np.full(len(SPECIES_9), 1.0e-16, dtype=float)
    carbamate = min(0.85 * carbon_total, 0.45 * amine_total)
    bicarbonate = max(carbon_total - carbamate, 1.0e-16)
    protonated_amine = min(carbamate + bicarbonate, 0.49 * amine_total)
    values[SPECIES_INDEX["MEACOO-"]] = max(carbamate, 1.0e-16)
    values[SPECIES_INDEX["HCO3-"]] = bicarbonate
    values[SPECIES_INDEX["MEAH+"]] = protonated_amine
    values[SPECIES_INDEX["MEA"]] = max(amine_total - protonated_amine - carbamate, 1.0e-12)
    values[SPECIES_INDEX["H2O"]] = max(water_total - bicarbonate, 1.0e-12)
    values[SPECIES_INDEX["CO2"]] = max(carbon_total - carbamate - bicarbonate, 1.0e-16)
    values[SPECIES_INDEX["CO3^2-"]] = 1.0e-12
    values[SPECIES_INDEX["H3O+"]] = 1.0e-12
    values[SPECIES_INDEX["OH-"]] = 1.0e-12
    return values / float(np.sum(values))


def _component_totals(x: np.ndarray) -> tuple[float, float, float, float]:
    carbon_total = (
        x[SPECIES_INDEX["CO2"]]
        + x[SPECIES_INDEX["MEACOO-"]]
        + x[SPECIES_INDEX["HCO3-"]]
        + x[SPECIES_INDEX["CO3^2-"]]
    )
    amine_total = x[SPECIES_INDEX["MEA"]] + x[SPECIES_INDEX["MEAH+"]] + x[SPECIES_INDEX["MEACOO-"]]
    water_total = (
        x[SPECIES_INDEX["H2O"]]
        + x[SPECIES_INDEX["HCO3-"]]
        + x[SPECIES_INDEX["CO3^2-"]]
        + x[SPECIES_INDEX["H3O+"]]
        + x[SPECIES_INDEX["OH-"]]
    )
    charge = (
        x[SPECIES_INDEX["MEAH+"]]
        + x[SPECIES_INDEX["H3O+"]]
        - x[SPECIES_INDEX["MEACOO-"]]
        - x[SPECIES_INDEX["HCO3-"]]
        - 2.0 * x[SPECIES_INDEX["CO3^2-"]]
        - x[SPECIES_INDEX["OH-"]]
    )
    return float(carbon_total), float(amine_total), float(water_total), float(charge)


def _raw_residuals(
    reduced_variables: np.ndarray,
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
) -> np.ndarray:
    x = _softmax(reduced_variables)
    log_x = np.log(np.clip(x, 1.0e-300, None))
    reaction_residuals = REACTION_MATRIX @ log_x - equilibrium_log_constants(temperature_K)
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
    return np.concatenate([reaction_residuals, balance_residuals])


def _solver_residuals(
    reduced_variables: np.ndarray,
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
) -> np.ndarray:
    raw = _raw_residuals(reduced_variables, loading, mea_weight_fraction, temperature_K)
    scaled = raw.copy()
    scaled[: len(REACTION_IDS)] /= 10.0
    scaled[len(REACTION_IDS) :] *= 10.0
    return scaled


def _named_residuals(raw_residuals: np.ndarray) -> dict[str, float]:
    rows = {f"{reaction_id}_ln_residual": float(value) for reaction_id, value in zip(REACTION_IDS, raw_residuals[:5])}
    rows["carbon_loading_residual"] = float(raw_residuals[5])
    rows["water_amine_ratio_residual"] = float(raw_residuals[6])
    rows["electroneutrality_residual"] = float(raw_residuals[7])
    return rows


def solve_ideal_speciation(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    *,
    initial_mole_fractions: Iterable[float] | None = None,
) -> SmithMissenIdealSpeciationResult:
    effective_loading = max(float(loading), MIN_LOADING)
    if initial_mole_fractions is None:
        start = _to_reduced_variables(_default_initial_mole_fractions(effective_loading, mea_weight_fraction))
    else:
        start = _to_reduced_variables(initial_mole_fractions)

    solution = least_squares(
        _solver_residuals,
        start,
        args=(effective_loading, float(mea_weight_fraction), float(temperature_K)),
        max_nfev=1000,
        ftol=1.0e-11,
        xtol=1.0e-11,
        gtol=1.0e-11,
    )
    mole_fractions = _softmax(solution.x)
    raw = _raw_residuals(solution.x, effective_loading, float(mea_weight_fraction), float(temperature_K))
    max_abs_residual = float(np.max(np.abs(raw)))
    success = bool(solution.success and max_abs_residual <= SOLVER_TOLERANCE)
    message = str(solution.message)
    if not success:
        raise RuntimeError(
            "ideal reaction-equilibrium reference ideal Smith-Missen speciation solve failed "
            f"at loading={loading:g}, T={temperature_K:g} K, max_abs_residual={max_abs_residual:.3e}: {message}"
        )
    return SmithMissenIdealSpeciationResult(
        loading=float(loading),
        effective_loading=effective_loading,
        mea_weight_fraction=float(mea_weight_fraction),
        temperature_K=float(temperature_K),
        mole_fractions=mole_fractions,
        residuals=_named_residuals(raw),
        max_abs_residual=max_abs_residual,
        success=success,
        message=message,
    )


def solve_ideal_speciation_grid(
    loadings: Iterable[float],
    mea_weight_fraction: float,
    temperature_K: float,
) -> list[SmithMissenIdealSpeciationResult]:
    results: list[SmithMissenIdealSpeciationResult] = []
    previous_x: np.ndarray | None = None
    for loading in loadings:
        result = solve_ideal_speciation(
            float(loading),
            float(mea_weight_fraction),
            float(temperature_K),
            initial_mole_fractions=previous_x,
        )
        results.append(result)
        previous_x = result.mole_fractions
    return results


SPECIES_6 = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-")
REDUCED_REACTION_IDS = (
    "R_carbamate_formation_combo",
    "R_bicarbonate_formation_combo",
)
REDUCED_REACTION_MATRIX = np.array(
    [
        [-1, -2, 0, 1, 1, 0],
        [-1, -1, -1, 1, 0, 1],
    ],
    dtype=float,
)


@dataclass(frozen=True)
class ReducedIdealSpeciationResult:
    loading: float
    effective_loading: float
    mea_weight_fraction: float
    temperature_K: float
    mole_fractions: np.ndarray
    residuals: dict[str, float]
    max_abs_residual: float
    success: bool
    message: str

    def species_map(self) -> dict[str, float]:
        values = {
            species: float(self.mole_fractions[index])
            for index, species in enumerate(SPECIES_6)
        }
        values["MEA + MEAH+"] = values["MEA"] + values["MEAH+"]
        return values


def reduced_equilibrium_log_constants(
    temperature_K: float, coefficients: np.ndarray
) -> np.ndarray:
    """Return log(K) for the two-reaction reduced true-species basis."""
    values = np.asarray(coefficients, dtype=float)
    if values.shape != (2, 4):
        raise ValueError(f"reduced reaction coefficients must have shape (2, 4), got {values.shape}")
    a, b, c, d = values.T
    temperature = float(temperature_K)
    return a + b / temperature + c * np.log(temperature) + d * temperature


def _reduced_default_initial_mole_fractions(
    loading: float, mea_weight_fraction: float
) -> np.ndarray:
    water_per_amine = unloaded_water_to_amine_ratio(mea_weight_fraction)
    amine_total = 1.0 / (1.0 + water_per_amine + loading)
    carbon_total = loading * amine_total
    water_total = water_per_amine * amine_total

    values = np.full(len(SPECIES_6), 1.0e-16, dtype=float)
    carbamate = min(0.85 * carbon_total, 0.45 * amine_total)
    bicarbonate = max(carbon_total - carbamate, 1.0e-16)
    protonated_amine = min(carbamate + bicarbonate, 0.49 * amine_total)
    values[3] = max(protonated_amine, 1.0e-16)
    values[4] = max(carbamate, 1.0e-16)
    values[5] = bicarbonate
    values[1] = max(amine_total - protonated_amine - carbamate, 1.0e-12)
    values[2] = max(water_total - bicarbonate, 1.0e-12)
    values[0] = max(carbon_total - carbamate - bicarbonate, 1.0e-16)
    return values / float(np.sum(values))


def _reduced_component_totals(x: np.ndarray) -> tuple[float, float, float, float]:
    carbon_total = x[0] + x[4] + x[5]
    amine_total = x[1] + x[3] + x[4]
    water_total = x[2] + x[5]
    charge = x[3] - x[4] - x[5]
    return float(carbon_total), float(amine_total), float(water_total), float(charge)


def _reduced_raw_residuals(
    reduced_variables: np.ndarray,
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    coefficients: np.ndarray,
) -> np.ndarray:
    x = _softmax(reduced_variables)
    log_x = np.log(np.clip(x, 1.0e-300, None))
    reaction_residuals = REDUCED_REACTION_MATRIX @ log_x - reduced_equilibrium_log_constants(
        temperature_K, coefficients
    )
    carbon_total, amine_total, water_total, charge = _reduced_component_totals(x)
    water_per_amine = unloaded_water_to_amine_ratio(mea_weight_fraction)
    balance_residuals = np.array(
        [
            (carbon_total - loading * amine_total) / max(amine_total, 1.0e-300),
            (water_total - water_per_amine * amine_total) / max(water_total, 1.0e-300),
            charge / max(amine_total, 1.0e-300),
        ],
        dtype=float,
    )
    return np.concatenate([reaction_residuals, balance_residuals])


def solve_reduced_ideal_speciation(
    loading: float,
    mea_weight_fraction: float,
    temperature_K: float,
    coefficients: np.ndarray,
    *,
    initial_mole_fractions: Iterable[float] | None = None,
) -> ReducedIdealSpeciationResult:
    """Solve the ideal six-species combo-reaction equilibrium system."""
    effective_loading = max(float(loading), MIN_LOADING)
    values = np.asarray(coefficients, dtype=float)
    if values.shape != (2, 4):
        raise ValueError(f"reduced reaction coefficients must have shape (2, 4), got {values.shape}")
    start_x = (
        _reduced_default_initial_mole_fractions(effective_loading, mea_weight_fraction)
        if initial_mole_fractions is None
        else np.asarray(initial_mole_fractions, dtype=float)
    )
    if start_x.shape != (len(SPECIES_6),):
        raise ValueError(f"initial reduced mole fractions must have shape (6,), got {start_x.shape}")
    start = _to_reduced_variables(start_x)

    def solver_residuals(reduced_variables: np.ndarray) -> np.ndarray:
        raw = _reduced_raw_residuals(
            reduced_variables,
            effective_loading,
            float(mea_weight_fraction),
            float(temperature_K),
            values,
        )
        scaled = raw.copy()
        scaled[:2] /= 10.0
        scaled[2:] *= 10.0
        return scaled

    solution = least_squares(
        solver_residuals,
        start,
        max_nfev=1000,
        ftol=1.0e-11,
        xtol=1.0e-11,
        gtol=1.0e-11,
    )
    mole_fractions = _softmax(solution.x)
    raw = _reduced_raw_residuals(
        solution.x,
        effective_loading,
        float(mea_weight_fraction),
        float(temperature_K),
        values,
    )
    residuals = {
        f"{reaction_id}_ln_residual": float(value)
        for reaction_id, value in zip(REDUCED_REACTION_IDS, raw[:2], strict=True)
    }
    residuals.update(
        {
            "carbon_loading_residual": float(raw[2]),
            "water_amine_ratio_residual": float(raw[3]),
            "electroneutrality_residual": float(raw[4]),
            "normalization_residual": float(np.sum(mole_fractions) - 1.0),
        }
    )
    max_abs_residual = float(np.max(np.abs(raw)))
    success = bool(solution.success and max_abs_residual <= SOLVER_TOLERANCE)
    message = str(solution.message)
    if not success:
        raise RuntimeError(
            "ideal reduced six-species speciation solve failed "
            f"at loading={loading:g}, T={temperature_K:g} K, "
            f"max_abs_residual={max_abs_residual:.3e}: {message}"
        )
    return ReducedIdealSpeciationResult(
        loading=float(loading),
        effective_loading=effective_loading,
        mea_weight_fraction=float(mea_weight_fraction),
        temperature_K=float(temperature_K),
        mole_fractions=mole_fractions,
        residuals=residuals,
        max_abs_residual=max_abs_residual,
        success=success,
        message=message,
    )


def solve_reduced_ideal_speciation_grid(
    loadings: Iterable[float],
    mea_weight_fraction: float,
    temperature_K: float,
    coefficients: np.ndarray,
) -> list[ReducedIdealSpeciationResult]:
    results: list[ReducedIdealSpeciationResult] = []
    previous_x: np.ndarray | None = None
    for loading in loadings:
        result = solve_reduced_ideal_speciation(
            float(loading),
            float(mea_weight_fraction),
            float(temperature_K),
            coefficients,
            initial_mole_fractions=previous_x,
        )
        results.append(result)
        previous_x = result.mole_fractions
    return results
