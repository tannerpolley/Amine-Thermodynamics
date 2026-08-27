from __future__ import annotations

import csv
import json
import math
import statistics

import numpy as np

from evaluate_co2_water_kij_transfer import _write_csv
from generate import ANALYSIS
from MEA.common.analysis_io import read_diagnostic_rows


REPO = ANALYSIS.parents[2]
PREDICTIONS = ANALYSIS / "results/co2_water_kij_anchored_transfer/predictions.csv"
JOINT_CANDIDATE = ANALYSIS / "results/anchored_joint_reaction_temperature_validation/compile_diagnostics.csv"
BALANCED_CANDIDATE = ANALYSIS / "results/calorimetry_balanced_reaction_validation/compile_diagnostics.csv"
SOURCE = REPO / "data/reference/MEA/observations/calorimetry/MEA_heat_of_absorption_observations.csv"
OUTPUT = ANALYSIS / "results/calorimetry_consistency"
TEMPERATURES_K = (313.15, 333.15, 353.15)
R_J_MOL_K = 8.31446261815324


def _isotherms(configuration: str) -> dict[float, tuple[np.ndarray, np.ndarray]]:
    with PREDICTIONS.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row["block"] == "pressure"]
    candidate_path = {
        "joint_r4_r5_temperature_candidate": JOINT_CANDIDATE,
        "calorimetry_balanced_exact": BALANCED_CANDIDATE,
    }.get(configuration)
    if candidate_path is not None:
        candidate = read_diagnostic_rows(candidate_path, nested=True)
        rows = [
            *[row for row in rows if math.isclose(float(row["temperature_k"]), 313.15)],
            *[row for row in candidate if "observed" in row],
        ]
    isotherms = {}
    for temperature_k in TEMPERATURES_K:
        grouped: dict[float, list[float]] = {}
        for row in rows:
            if math.isclose(float(row["temperature_k"]), temperature_k):
                grouped.setdefault(float(row["loading"]), []).append(
                    math.log(float(row["predicted"]))
                )
        loading = np.asarray(sorted(grouped), dtype=float)
        log_pressure = np.asarray(
            [statistics.fmean(grouped[value]) for value in loading], dtype=float
        )
        isotherms[temperature_k] = loading, log_pressure
    return isotherms


def main() -> None:
    configurations = (
        "retained",
        "joint_r4_r5_temperature_candidate",
        "calorimetry_balanced_exact",
    )
    all_isotherms = {
        configuration: _isotherms(configuration) for configuration in configurations
    }
    lower = max(
        values[0][0]
        for isotherms in all_isotherms.values()
        for values in isotherms.values()
    )
    upper = min(
        values[0][-1]
        for isotherms in all_isotherms.values()
        for values in isotherms.values()
    )
    loading_grid = np.linspace(lower, upper, 80)
    inverse_temperature = 1.0 / np.asarray(TEMPERATURES_K)
    curve = []
    for configuration, isotherms in all_isotherms.items():
        for loading in loading_grid:
            log_fugacity = np.asarray(
                [
                    np.interp(loading, *isotherms[temperature_k])
                    for temperature_k in TEMPERATURES_K
                ]
            )
            slope, intercept = np.polyfit(inverse_temperature, log_fugacity, 1)
            fitted = slope * inverse_temperature + intercept
            curve.append(
                {
                    "configuration": configuration,
                    "loading": float(loading),
                    "model_heat_release_kj_per_mol_co2": float(-R_J_MOL_K * slope / 1000.0),
                    "ln_fugacity_fit_rmse": float(np.sqrt(np.mean((fitted - log_fugacity) ** 2))),
                }
            )

    with SOURCE.open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    direct = [
        row
        for row in source_rows
        if row["regression_eligible"] == "true"
        and row["source_role"] == "primary_direct_calorimetry"
        and row["mea_mass_fraction"] == "0.30"
        and row["temperature_K"] in {"313.15", "353.15"}
        and row["enthalpy_semantics"].startswith("temperature-differential")
    ]
    comparisons = []
    for configuration in configurations:
        selected_curve = [row for row in curve if row["configuration"] == configuration]
        grid_x = np.asarray([row["loading"] for row in selected_curve])
        grid_y = np.asarray(
            [row["model_heat_release_kj_per_mol_co2"] for row in selected_curve]
        )
        for row in direct:
            loading = float(row["co2_loading_mol_per_mol_mea"])
            admitted = lower <= loading <= upper
            predicted = float(np.interp(loading, grid_x, grid_y)) if admitted else None
            observed = float(row["dh_kj_per_mol_co2"])
            comparisons.append(
                {
                    "configuration": configuration,
                    "record_id": row["record_id"],
                    "source": row["source"],
                    "temperature_k": float(row["temperature_K"]),
                    "loading": loading,
                    "observed_heat_release_kj_per_mol_co2": observed,
                    "model_heat_release_kj_per_mol_co2": predicted,
                    "residual_kj_per_mol_co2": None if predicted is None else predicted - observed,
                    "status": "evaluated" if admitted else "outside_common_vle_loading_interval",
                }
            )
    evaluated = [row for row in comparisons if row["status"] == "evaluated"]
    metrics = []
    for configuration in configurations:
        residuals = [
            float(row["residual_kj_per_mol_co2"])
            for row in evaluated
            if row["configuration"] == configuration
        ]
        metrics.append(
            {
                "configuration": configuration,
                "rmse_kj_per_mol_co2": math.sqrt(
                    math.fsum(value * value for value in residuals) / len(residuals)
                ),
                "mean_bias_kj_per_mol_co2": statistics.fmean(residuals),
                "median_absolute_error_kj_per_mol_co2": statistics.median(map(abs, residuals)),
            }
        )
    paired = {
        (row["configuration"], row["record_id"]): row for row in evaluated
    }
    identities = sorted({row["record_id"] for row in evaluated})
    retained_residual = np.asarray(
        [float(paired[("retained", identity)]["residual_kj_per_mol_co2"]) for identity in identities]
    )
    heat_effect = np.asarray(
        [
            float(
                paired[("joint_r4_r5_temperature_candidate", identity)][
                    "model_heat_release_kj_per_mol_co2"
                ]
            )
            - float(paired[("retained", identity)]["model_heat_release_kj_per_mol_co2"])
            for identity in identities
        ]
    )
    scale = float(
        np.clip(
            -np.dot(retained_residual, heat_effect) / np.dot(heat_effect, heat_effect),
            0.0,
            1.0,
        )
    )
    balanced_residual = retained_residual + scale * heat_effect
    balanced_r4 = scale * 0.053848175222989375
    balanced_r5 = scale * 0.9642695898871344
    balanced_metrics = {
        "configuration": "calorimetry_balanced_linearized",
        "rmse_kj_per_mol_co2": float(np.sqrt(np.mean(balanced_residual**2))),
        "mean_bias_kj_per_mol_co2": float(np.mean(balanced_residual)),
        "median_absolute_error_kj_per_mol_co2": float(np.median(np.abs(balanced_residual))),
    }
    summary = {
        "schema": "mea.calorimetry-consistency.v1",
        "status": "completed",
        "method": "common Gibbs-Helmholtz f-term from a linear fit of model ln(f_CO2) versus 1/T at fixed apparent loading",
        "temperature_isotherms_k": TEMPERATURES_K,
        "common_loading_interval": [float(lower), float(upper)],
        "direct_observation_count": len(direct),
        "evaluated_observation_count_per_configuration": len(evaluated) // len(configurations),
        "held_out_observation_count_per_configuration": (len(comparisons) - len(evaluated)) // len(configurations),
        "metrics": metrics,
        "calorimetry_balanced_linearized": {
            "scale_between_retained_and_joint_candidate": scale,
            "candidate_r4_delta_ln_k_at_353_15_k": balanced_r4,
            "candidate_r5_delta_ln_k_at_353_15_k": balanced_r5,
            "metrics": balanced_metrics,
        },
        "limitations": [
            "the pressure-volume correction term is neglected; Mathias and O'Connell (2012) show it is small for aqueous MEA",
            "the curve is a 313.15-353.15 K average temperature derivative rather than a local derivative at each calorimeter temperature",
            "the derivative uses interpolation of completed model bubble predictions and performs no parameter fitting",
        ],
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT / "model_heat_curve.csv", curve)
    _write_csv(OUTPUT / "calorimetry_comparison.csv", comparisons)
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUTPUT / "reaction_temperature_candidate.json").write_text(
        json.dumps(
            {
                "schema": "mea.calorimetry-balanced-reaction-temperature-candidate.v1",
                "candidate_r4_delta_ln_k_at_353_15_k": balanced_r4,
                "candidate_r5_delta_ln_k_at_353_15_k": balanced_r5,
                "coordinate": "zero at 313.15 K and linear in reciprocal temperature to the reported 353.15 K value",
                "role": "linearized candidate pending exact nonlinear validation",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
