from __future__ import annotations

import csv
import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from MEA.common.config import CANONICAL_MEA_WEIGHT_FRACTION, EPCSAFT_DATASET_ROOT, EPCSAFT_IONIC_ANALYSIS
from MEA.epcsaft_present_plots import _as_float, load_cheq_rows, load_vle_rows, reconcile_speciation_row
from MEA.epcsaft_runtime import ADVANCED_BORN_USER_OPTIONS, DATASET_DIR, SPECIES, load_epcsaft, to_jsonable

SPECIES_INDEX = {name: idx for idx, name in enumerate(SPECIES)}
FIT_DATASET_DIR = EPCSAFT_DATASET_ROOT / "MEA_CO2_H2O_ionic_fit"
OUT_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "parameter_regression"
IONIC_PLOT_ROOT = EPCSAFT_IONIC_ANALYSIS / "results"
PRESSURE_OUT_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "pressure"
SPECIATION_OUT_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "speciation"
SUMMARY_OUT_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "summary"
PARAMETER_CSV = FIT_DATASET_DIR / "pure" / "any_solvent.csv"
K_IJ_CSV = FIT_DATASET_DIR / "mixed" / "binary_interaction" / "k_ij.csv"


REACTION_CONSTANTS = {
    "R1_water_autoionization": (132.899, -13445.9, -22.4773, 0.0),
    "R2_CO2_to_HCO3": (231.465, -12092.1, -36.7816, 0.0),
    "R3_HCO3_to_CO3": (216.049, -12431.0, -35.4891, 0.0),
    "R4_MEACOO_hydrolysis": (-1.8652, -1543.3, 0.0, 0.0),
    "R5_MEAH_dissociation": (2.1211, -8189.38, 0.0, -0.007484),
}


def equilibrium_log_constants(temperature_K: float) -> np.ndarray:
    """Return log equilibrium constants for the true-species MEA reactions."""
    constants = np.array(list(REACTION_CONSTANTS.values()), dtype=float)
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


def initial_all_species_mole_fractions(loading: float, mea_weight_fraction: float) -> np.ndarray:
    mw_ratio = 0.06108 / 0.01802
    x_mea_unloaded = mea_weight_fraction / (mw_ratio + mea_weight_fraction * (1.0 - mw_ratio))
    x_h2o_unloaded = 1.0 - x_mea_unloaded
    n_mea = x_mea_unloaded
    n_h2o = x_h2o_unloaded
    n_co2 = n_mea * loading
    total = n_co2 + n_mea + n_h2o
    return np.array([n_co2 / total, n_mea / total, n_h2o / total, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)

DIAGNOSTIC_REACTION_CONSTANTS = {
    "R2_CO2_to_HCO3": (216.049, -12431.70, -35.4819, 0.0),
    "R3_HCO3_to_CO3": (-1.8652, -1545.3, 0.0, 0.0),
    "R4_MEACOO_hydrolysis": (-1.8652, -1545.3, 0.0, 0.0),
    "R5_MEAH_dissociation": (2.1211, -8189.38, 0.0, -0.007484),
}

FIT_COMPONENTS = ("MEA", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
BINARY_FIT_PAIRS = (
    ("CO2", "MEA"),
    ("CO2", "MEAH+"),
    ("CO2", "MEACOO-"),
    ("MEA", "H2O"),
    ("MEAH+", "MEACOO-"),
    ("MEAH+", "HCO3-"),
)

DEFAULT_INITIAL_GUESS = {
    "MEA__m": 3.0353,
    "MEA__s": 3.0435,
    "MEA__e": 277.174,
    "MEAH+__s": 3.5630,
    "MEAH+__e": 228.71,
    "MEAH+__d_born": 3.5630,
    "MEACOO-__s": 3.5605,
    "MEACOO-__e": 533.11,
    "MEACOO-__d_born": 3.5605,
    "HCO3-__s": 2.9296,
    "HCO3-__e": 70.0,
    "HCO3-__d_born": 3.0,
    "CO3^2-__s": 2.4422,
    "CO3^2-__e": 249.26,
    "CO3^2-__d_born": 3.0,
    "H3O+__s": 3.4654,
    "H3O+__e": 500.0,
    "H3O+__d_born": 1.218,
    "OH-__s": 2.0177,
    "OH-__e": 650.0,
    "OH-__d_born": 3.08107689400404,
    "k_ij__CO2__MEA": 0.0,
    "k_ij__CO2__MEAH+": 0.0,
    "k_ij__CO2__MEACOO-": 0.0,
    "k_ij__MEA__H2O": -0.0520,
    "k_ij__MEAH+__MEACOO-": 0.0,
    "k_ij__MEAH+__HCO3-": 0.0,
}

BOUNDS = {
    "MEA__m": (2.0, 5.8),
    "MEA__s": (2.25, 3.9),
    "MEA__e": (120.0, 500.0),
    "MEAH+__s": (2.0, 5.8),
    "MEAH+__e": (50.0, 950.0),
    "MEAH+__d_born": (1.0, 7.0),
    "MEACOO-__s": (2.0, 5.8),
    "MEACOO-__e": (50.0, 1000.0),
    "MEACOO-__d_born": (1.0, 7.0),
    "HCO3-__s": (2.0, 5.8),
    "HCO3-__e": (50.0, 900.0),
    "HCO3-__d_born": (1.0, 7.0),
    "CO3^2-__s": (2.0, 5.8),
    "CO3^2-__e": (50.0, 1200.0),
    "CO3^2-__d_born": (1.0, 8.0),
    "H3O+__s": (1.0, 5.8),
    "H3O+__e": (50.0, 1200.0),
    "H3O+__d_born": (0.5, 5.0),
    "OH-__s": (1.0, 5.8),
    "OH-__e": (50.0, 1200.0),
    "OH-__d_born": (1.0, 7.0),
    "k_ij__CO2__MEA": (-2.0, 2.0),
    "k_ij__CO2__MEAH+": (-2.0, 2.0),
    "k_ij__CO2__MEACOO-": (-2.0, 2.0),
    "k_ij__MEA__H2O": (-2.0, 2.0),
    "k_ij__MEAH+__MEACOO-": (-2.0, 2.0),
    "k_ij__MEAH+__HCO3-": (-2.0, 2.0),
}


@dataclass(frozen=True)
class VLETarget:
    row_id: str
    T: float
    P: float
    loading: float
    pressure_kPa: float
    x: np.ndarray
    paper: str


@dataclass(frozen=True)
class SpeciationTarget:
    row_id: str
    T: float
    P: float
    loading: float
    x: np.ndarray
    source: str


@dataclass(frozen=True)
class ReactiveSpeciationPrediction:
    x: np.ndarray
    activity_coefficients: dict[str, float]
    mass_balance_residuals: dict[str, float]
    charge_residual: float
    reaction_residuals: dict[str, float]
    state_failure_count: int
    message: str


@dataclass(frozen=True)
class BubblePressurePrediction:
    pressure_kPa: float
    total_pressure_kPa: float
    vapor_composition: dict[str, float]
    partial_pressures_kPa: dict[str, float]
    fugacity_residual_norm: float
    charge_residual: float
    message: str


def reactive_electrolyte_options(initial_pressure: float):
    epcsaft = load_epcsaft()
    return epcsaft.ReactiveElectrolyteBubbleOptions(
        speciation_options=epcsaft.ReactiveSpeciationOptions(
            max_iterations=80,
            tolerance=1.0e-7,
            damping=0.5,
            min_mole_fraction=1.0e-14,
            return_best_effort=True,
            mass_tolerance=1.0e-7,
            charge_tolerance=1.0e-6,
            reaction_tolerance=1.0e-7,
        ),
        bubble_options=epcsaft.ElectrolyteBubbleOptions(
            initial_pressure=max(float(initial_pressure), 1.0e3),
            min_pressure=1.0e-3,
            max_pressure=1.0e8,
            max_iterations=120,
            tolerance=1.0e-6,
            charge_tolerance=1.0e-6,
            return_best_effort=True,
        ),
        error_mode="result",
        penalty_value=8.0,
    )


def ensure_fit_dataset(reset: bool = False) -> Path:
    if reset and FIT_DATASET_DIR.exists():
        shutil.rmtree(FIT_DATASET_DIR)
    if not FIT_DATASET_DIR.exists():
        shutil.copytree(DATASET_DIR, FIT_DATASET_DIR)
    return FIT_DATASET_DIR


def theta_names() -> tuple[str, ...]:
    return tuple(DEFAULT_INITIAL_GUESS)


def initial_theta() -> np.ndarray:
    return np.asarray([DEFAULT_INITIAL_GUESS[name] for name in theta_names()], dtype=float)


def theta_to_map(theta: Iterable[float]) -> dict[str, float]:
    return {name: float(value) for name, value in zip(theta_names(), theta)}


def bounds_arrays() -> tuple[np.ndarray, np.ndarray]:
    lower = np.asarray([BOUNDS[name][0] for name in theta_names()], dtype=float)
    upper = np.asarray([BOUNDS[name][1] for name in theta_names()], dtype=float)
    return lower, upper


def _select_evenly(rows: list[dict[str, str]], limit: int | None) -> list[dict[str, str]]:
    if limit is None or limit <= 0 or len(rows) <= limit:
        return rows
    positions = np.linspace(0, len(rows) - 1, limit)
    return [rows[int(round(position))] for position in positions]


def _speciation_interpolator(cheq_rows: list[dict[str, str]], temperature_C: float, loading: float) -> np.ndarray:
    candidates = [
        row
        for row in cheq_rows
        if abs(_as_float(row, "MEA_weight_fraction") - CANONICAL_MEA_WEIGHT_FRACTION) < 1.0e-9
        and np.isfinite(_as_float(row, "temperature"))
        and np.isfinite(_as_float(row, "CO2_loading"))
    ]
    exact = [row for row in candidates if abs(_as_float(row, "temperature") - temperature_C) <= 1.0e-9]
    by_temperature = exact if len(exact) >= 2 else sorted(candidates, key=lambda row: abs(_as_float(row, "temperature") - temperature_C))
    if not exact and by_temperature:
        nearest_temperature = _as_float(by_temperature[0], "temperature")
        by_temperature = [row for row in candidates if abs(_as_float(row, "temperature") - nearest_temperature) <= 1.0e-9]
    reconciled = sorted(
        (
            (float(_as_float(row, "CO2_loading")), reconcile_speciation_row(row))
            for row in by_temperature
            if np.isfinite(_as_float(row, "CO2_loading"))
        ),
        key=lambda item: item[0],
    )
    if len(reconciled) < 2:
        raise RuntimeError(f"not enough speciation records to interpolate T={temperature_C}, loading={loading}")
    loading_grid = np.asarray([item[0] for item in reconciled], dtype=float)
    values = np.asarray([item[1] for item in reconciled], dtype=float)
    x = np.asarray([np.interp(float(loading), loading_grid, values[:, idx]) for idx in range(values.shape[1])], dtype=float)
    return np.clip(x / float(np.sum(x)), 1.0e-30, None)


def load_vle_targets(limit: int | None = None) -> list[VLETarget]:
    cheq_rows = load_cheq_rows()
    rows = [
        row
        for row in load_vle_rows()
        if abs(_as_float(row, "MEA_weight_fraction") - CANONICAL_MEA_WEIGHT_FRACTION) < 1.0e-9
        and np.isfinite(_as_float(row, "temperature"))
        and np.isfinite(_as_float(row, "CO2_loading"))
        and np.isfinite(_as_float(row, "CO2_pressure"))
        and _as_float(row, "CO2_pressure") > 1.0e-4
    ]
    rows = _select_evenly(sorted(rows, key=lambda row: (_as_float(row, "temperature"), _as_float(row, "CO2_loading"))), limit)
    targets = []
    for idx, row in enumerate(rows):
        temperature_C = float(_as_float(row, "temperature"))
        pressure_kPa = float(_as_float(row, "CO2_pressure"))
        loading = float(_as_float(row, "CO2_loading"))
        targets.append(
            VLETarget(
                row_id=f"vle_{idx:04d}",
                T=temperature_C + 273.15,
                P=max(101325.0, pressure_kPa * 1000.0),
                loading=loading,
                pressure_kPa=pressure_kPa,
                x=_speciation_interpolator(cheq_rows, temperature_C, loading),
                paper=str(row.get("paper", "")),
            )
        )
    return targets


def load_speciation_targets(limit: int | None = None) -> list[SpeciationTarget]:
    rows = [
        row
        for row in load_cheq_rows()
        if abs(_as_float(row, "MEA_weight_fraction") - CANONICAL_MEA_WEIGHT_FRACTION) < 1.0e-9
        and np.isfinite(_as_float(row, "temperature"))
        and np.isfinite(_as_float(row, "CO2_loading"))
    ]
    rows = _select_evenly(sorted(rows, key=lambda row: (_as_float(row, "temperature"), _as_float(row, "CO2_loading"), row.get("source", ""))), limit)
    return [
        SpeciationTarget(
            row_id=f"cheq_{idx:04d}",
            T=float(_as_float(row, "temperature")) + 273.15,
            P=101325.0,
            loading=float(_as_float(row, "CO2_loading")),
            x=reconcile_speciation_row(row),
            source=str(row.get("source", "")),
        )
        for idx, row in enumerate(rows)
    ]


def _base_params(x: np.ndarray, T: float, dataset: Path = DATASET_DIR) -> dict[str, Any]:
    epcsaft = load_epcsaft()
    return epcsaft.get_prop_dict(dataset, SPECIES, np.asarray(x, dtype=float), float(T), user_options=ADVANCED_BORN_USER_OPTIONS)


def override_params(params: dict[str, Any], values: dict[str, float]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in params.items():
        out[key] = np.asarray(value, dtype=float).copy() if isinstance(value, np.ndarray) else list(value) if isinstance(value, list) else value
    for component in FIT_COMPONENTS:
        idx = SPECIES_INDEX[component]
        for field in ("m", "s", "e", "d_born"):
            key = f"{component}__{field}"
            if key in values:
                arr = np.asarray(out[field], dtype=float).copy()
                arr[idx] = float(values[key])
                out[field] = arr
    k_ij = np.asarray(out["k_ij"], dtype=float).copy()
    for left, right in BINARY_FIT_PAIRS:
        key = f"k_ij__{left}__{right}"
        if key in values:
            i = SPECIES_INDEX[left]
            j = SPECIES_INDEX[right]
            k_ij[i, j] = k_ij[j, i] = float(values[key])
    out["k_ij"] = k_ij
    return out


def mixture_for_x(x: np.ndarray, T: float, values: dict[str, float], dataset: Path = DATASET_DIR):
    epcsaft = load_epcsaft()
    params = override_params(_base_params(x, T, dataset), values)
    return epcsaft.ePCSAFTMixture.from_params(params, species=SPECIES)


def state_for_x(x: np.ndarray, T: float, P: float, values: dict[str, float], dataset: Path = DATASET_DIR):
    return mixture_for_x(x, T, values, dataset).state(T, x, P=P, phase="liq")


def reaction_definitions(T: float):
    epcsaft = load_epcsaft()
    log_k = equilibrium_log_constants(T)
    rows = reaction_matrix()
    names = tuple(REACTION_CONSTANTS)
    return [
        epcsaft.ReactionDefinition(
            stoichiometry={species: float(coeff) for species, coeff in zip(SPECIES, row) if abs(float(coeff)) > 0.0},
            log_equilibrium_constant=float(log_k[idx]),
            name=names[idx],
        )
        for idx, row in enumerate(rows)
    ]


def apparent_totals(loading: float) -> dict[str, float]:
    apparent = initial_all_species_mole_fractions(float(loading), CANONICAL_MEA_WEIGHT_FRACTION)
    return {
        "carbon_total": float(apparent[0]),
        "mea_total": float(apparent[1]),
        "water_total": float(apparent[2]),
    }


def reactive_balances() -> dict[str, dict[str, float]]:
    return {
        "carbon_total": {"CO2": 1.0, "MEACOO-": 1.0, "HCO3-": 1.0, "CO3^2-": 1.0},
        "mea_total": {"MEA": 1.0, "MEAH+": 1.0, "MEACOO-": 1.0},
        "water_total": {"H2O": 1.0, "HCO3-": 1.0, "CO3^2-": 1.0, "H3O+": 1.0, "OH-": 1.0},
    }


def solve_activity_speciation(
    loading: float,
    T: float,
    P: float,
    initial_x: np.ndarray,
    values: dict[str, float],
    dataset: Path = DATASET_DIR,
) -> ReactiveSpeciationPrediction:
    epcsaft = load_epcsaft()

    def make_mixture(x: np.ndarray, temperature: float, pressure: float):
        return mixture_for_x(np.asarray(x, dtype=float), float(temperature), values, dataset)

    result = epcsaft.solve_reactive_speciation(
        species=SPECIES,
        mixture_factory=make_mixture,
        T=float(T),
        P=float(P),
        balances=reactive_balances(),
        totals=apparent_totals(float(loading)),
        reactions=reaction_definitions(float(T)),
        initial_x=np.asarray(initial_x, dtype=float),
        options=epcsaft.ReactiveSpeciationOptions(
            max_iterations=80,
            tolerance=1.0e-7,
            damping=0.5,
            min_mole_fraction=1.0e-14,
            return_best_effort=True,
            mass_tolerance=1.0e-7,
            charge_tolerance=1.0e-6,
            reaction_tolerance=1.0e-7,
        ),
    )
    return ReactiveSpeciationPrediction(
        x=np.asarray([result.x[species] for species in SPECIES], dtype=float),
        activity_coefficients=dict(result.activity_coefficients),
        mass_balance_residuals=dict(result.mass_balance_residuals),
        charge_residual=float(result.charge_residual),
        reaction_residuals={reaction.name or f"R{idx + 1}": float(value) for idx, (reaction, value) in enumerate(zip(reaction_definitions(float(T)), result.reaction_residuals))},
        state_failure_count=int(result.state_failure_count),
        message=str(result.message),
    )


def predict_bubble_pressure(
    x: np.ndarray,
    T: float,
    pressure_seed: float,
    values: dict[str, float],
    dataset: Path = DATASET_DIR,
) -> BubblePressurePrediction:
    epcsaft = load_epcsaft()
    result = mixture_for_x(x, T, values, dataset).equilibrium(
        kind="electrolyte_bubble_pressure",
        T=float(T),
        x_liq=np.asarray(x, dtype=float),
        volatile_species=["CO2", "H2O", "MEA"],
        vapor_species=["CO2", "H2O", "MEA"],
        nonvolatile_species=["MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"],
        options=epcsaft.ElectrolyteBubbleOptions(
            initial_pressure=max(float(pressure_seed), 1.0e3),
            min_pressure=1.0e-3,
            max_pressure=1.0e8,
            max_iterations=120,
            tolerance=1.0e-6,
            return_best_effort=True,
        ),
    )
    partial_pressures_kPa = {key: float(value) / 1000.0 for key, value in result.partial_pressures.items()}
    return BubblePressurePrediction(
        pressure_kPa=float(partial_pressures_kPa.get("CO2", 0.0)),
        total_pressure_kPa=float(result.P) / 1000.0,
        vapor_composition=dict(result.y_vap),
        partial_pressures_kPa=partial_pressures_kPa,
        fugacity_residual_norm=float(result.fugacity_residual_norm),
        charge_residual=float(result.charge_residual),
        message=str(result.message),
    )


def predict_co2_pressure_kPa(x: np.ndarray, T: float, P: float, values: dict[str, float], dataset: Path = DATASET_DIR) -> float:
    return predict_bubble_pressure(x, T, P, values, dataset).pressure_kPa


def predict_target_co2_pressure_kPa(target: VLETarget, values: dict[str, float], dataset: Path = DATASET_DIR) -> float:
    result = solve_reactive_bubble_target(target, values, dataset)
    return float(result.partial_pressures.get("CO2", 0.0)) / 1000.0


def solve_reactive_bubble_target(target: VLETarget, values: dict[str, float], dataset: Path = DATASET_DIR):
    epcsaft = load_epcsaft()

    def make_mixture(x: np.ndarray, temperature: float, pressure: float):
        return mixture_for_x(np.asarray(x, dtype=float), float(temperature), values, dataset)

    pressure_seed = max(target.P, target.pressure_kPa * 1000.0, 1.0e3)
    return epcsaft.solve_reactive_electrolyte_bubble(
        species=SPECIES,
        mixture_factory=make_mixture,
        T=target.T,
        P_seed=pressure_seed,
        balances=reactive_balances(),
        totals=apparent_totals(target.loading),
        reactions=reaction_definitions(target.T),
        initial_x=target.x,
        vapor_species=["CO2", "H2O", "MEA"],
        nonvolatile_species=["MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"],
        options=reactive_electrolyte_options(pressure_seed),
    )


def solve_reactive_bubble_targets(targets: list[VLETarget], values: dict[str, float], dataset: Path = DATASET_DIR):
    epcsaft = load_epcsaft()

    def make_mixture(x: np.ndarray, temperature: float, pressure: float):
        return mixture_for_x(np.asarray(x, dtype=float), float(temperature), values, dataset)

    results = []
    for temperature in sorted({round(target.T, 8) for target in targets}):
        group = [target for target in targets if round(target.T, 8) == temperature]
        points = []
        for target in group:
            pressure_seed = max(target.P, target.pressure_kPa * 1000.0, 1.0e3)
            points.append(
                {
                    "T": target.T,
                    "P_seed": pressure_seed,
                    "totals": apparent_totals(target.loading),
                    "initial_x": target.x,
                    "options": reactive_electrolyte_options(pressure_seed),
                }
            )
        try:
            results.extend(
                epcsaft.solve_reactive_electrolyte_bubble_sweep(
                    species=SPECIES,
                    mixture_factory=make_mixture,
                    points=points,
                    balances=reactive_balances(),
                    reactions=reaction_definitions(float(temperature)),
                    vapor_species=["CO2", "H2O", "MEA"],
                    nonvolatile_species=["MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"],
                    options=reactive_electrolyte_options(1.0e5),
                    continuation="auto",
                )
            )
        except Exception:
            for target in group:
                try:
                    results.append(solve_reactive_bubble_target(target, values, dataset))
                except Exception as exc:
                    results.append(exc)
    return results


def _ln_k(name: str, T: float) -> float:
    a, b, c, d = DIAGNOSTIC_REACTION_CONSTANTS[name]
    return float(a + b / T + c * math.log(T) + d * T)


def activity_reaction_residuals(x: np.ndarray, T: float, P: float, values: dict[str, float], dataset: Path = DATASET_DIR) -> dict[str, float]:
    state = state_for_x(x, T, P, values, dataset)
    gamma = state.activity_coefficient(species=SPECIES)

    def log_activity(species: str) -> float:
        return math.log(max(float(x[SPECIES_INDEX[species]]) * float(gamma[species]), 1.0e-30))

    logs = {name: log_activity(name) for name in SPECIES}
    return {
        "R2_CO2_to_HCO3": logs["H3O+"] + logs["HCO3-"] - logs["CO2"] - 2.0 * logs["H2O"] - _ln_k("R2_CO2_to_HCO3", T),
        "R3_HCO3_to_CO3": logs["H3O+"] + logs["CO3^2-"] - logs["HCO3-"] - logs["H2O"] - _ln_k("R3_HCO3_to_CO3", T),
        "R4_MEACOO_hydrolysis": logs["HCO3-"] + logs["MEA"] - logs["MEACOO-"] - logs["H2O"] - _ln_k("R4_MEACOO_hydrolysis", T),
        "R5_MEAH_dissociation": logs["H3O+"] + logs["MEA"] - logs["MEAH+"] - logs["H2O"] - _ln_k("R5_MEAH_dissociation", T),
    }


def evaluate_values(values: dict[str, float], vle_targets: list[VLETarget], spec_targets: list[SpeciationTarget], dataset: Path = DATASET_DIR) -> tuple[np.ndarray, dict[str, Any]]:
    residuals: list[float] = []
    vle_raw: list[float] = []
    reaction_raw: dict[str, list[float]] = {name: [] for name in REACTION_CONSTANTS}
    speciation_raw: dict[str, list[float]] = {name: [] for name in ("CO2", "MEA", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-")}
    failures: list[str] = []

    vle_scale = math.sqrt(1.0 / max(len(vle_targets), 1))
    reaction_scale = math.sqrt(0.20 / max(len(spec_targets), 1))
    regularization_scale = 0.015

    for target in vle_targets:
        try:
            predicted = predict_target_co2_pressure_kPa(target, values, dataset)
            raw = math.log10(max(predicted, 1.0e-30) / target.pressure_kPa)
        except Exception as exc:
            failures.append(f"{target.row_id}: {type(exc).__name__}: {str(exc).splitlines()[0]}")
            raw = 8.0
        vle_raw.append(raw)
        residuals.append(vle_scale * raw)

    for target in spec_targets:
        chemistry: ReactiveSpeciationPrediction | None = None
        try:
            chemistry = solve_activity_speciation(target.loading, target.T, target.P, target.x, values, dataset)
            rxn = chemistry.reaction_residuals
        except Exception as exc:
            failures.append(f"{target.row_id}: {type(exc).__name__}: {str(exc).splitlines()[0]}")
            rxn = {name: 20.0 for name in REACTION_CONSTANTS}
        for name, raw in rxn.items():
            reaction_raw[name].append(float(raw))
            residuals.append(reaction_scale * float(raw))
        if chemistry is not None:
            for species, rows in speciation_raw.items():
                raw = math.log10(max(float(chemistry.x[SPECIES_INDEX[species]]), 1.0e-30) / max(float(target.x[SPECIES_INDEX[species]]), 1.0e-30))
                rows.append(raw)
                residuals.append(reaction_scale * 0.35 * raw)
        else:
            for species, rows in speciation_raw.items():
                raw = 8.0
                rows.append(raw)
                residuals.append(reaction_scale * 0.35 * raw)

    for name, value in values.items():
        seed = DEFAULT_INITIAL_GUESS[name]
        scale = 0.006 if name.startswith("k_ij__") else regularization_scale
        residuals.append(scale * (float(value) - seed) / max(abs(seed), 1.0))

    metrics = {
        "vle_log10_rmse": _rmse(vle_raw),
        "vle_median_abs_log10_error": float(np.nanmedian(np.abs(np.asarray(vle_raw, dtype=float)))) if vle_raw else float("nan"),
        "vle_max_abs_log10_error": float(np.nanmax(np.abs(np.asarray(vle_raw, dtype=float)))) if vle_raw else float("nan"),
        "reaction_ln_rmse": {name: _rmse(rows) for name, rows in reaction_raw.items()},
        "reaction_ln_median_abs": {
            name: float(np.nanmedian(np.abs(np.asarray(rows, dtype=float)))) if rows else float("nan")
            for name, rows in reaction_raw.items()
        },
        "speciation_log10_rmse": {name: _rmse(rows) for name, rows in speciation_raw.items()},
        "speciation_log10_median_abs": {
            name: float(np.nanmedian(np.abs(np.asarray(rows, dtype=float)))) if rows else float("nan")
            for name, rows in speciation_raw.items()
        },
        "failure_count": len(failures),
        "failures": failures[:30],
    }
    return np.asarray(residuals, dtype=float), metrics


def _rmse(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    return float(np.sqrt(np.nanmean(arr * arr))) if arr.size else float("nan")


def write_fitted_dataset(values: dict[str, float], reset: bool = True) -> list[Path]:
    ensure_fit_dataset(reset=reset)
    written: list[Path] = []
    with PARAMETER_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        fieldnames = list(reader.fieldnames or [])
    for row in rows:
        component = str(row.get("component", ""))
        if component not in FIT_COMPONENTS:
            continue
        for field in ("m", "s", "e", "d_born"):
            key = f"{component}__{field}"
            if key in values:
                row[field] = f"{values[key]:.12g}"
    with PARAMETER_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    written.append(PARAMETER_CSV)

    with K_IJ_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        fieldnames = list(reader.fieldnames or [])
    for left, right in BINARY_FIT_PAIRS:
        key = f"k_ij__{left}__{right}"
        if key not in values:
            continue
        rendered = f"{values[key]:.12g}"
        for row in rows:
            if row.get("component") == left:
                row[right] = rendered
            if row.get("component") == right:
                row[left] = rendered
    with K_IJ_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    written.append(K_IJ_CSV)
    return written


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(payload), indent=2) + "\n", encoding="utf-8")
    return path


def write_csv(path: Path, rows: list[dict[str, Any]] | pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    frame.to_csv(path, index=False)
    return path
