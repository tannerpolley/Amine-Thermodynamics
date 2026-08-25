from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
import json
import math

import epcsaft
import matplotlib.pyplot as plt
import pandas as pd

from evaluate_anchored_co2_water_kij import _mapping as _anchored_mapping
from generate import ANALYSIS, COMPONENT_IDS
from run_full_predictive_refinement import _liquid
from MEA.common.analysis_io import write_csv_rows as _write_csv
from MEA.common.plot_style import finish_axes, save_figure_bundle
from MEA.epcsaft_ionic.parameter_document import (
    expand_parameter_domain,
    materialize_parameter_candidate,
)


REPO = ANALYSIS.parents[3]
SOURCE = (
    REPO / "data/reference/MEA/observations/liquid_speciation/"
    "Wong_2016_physical_CO2_solubility_30wt.csv"
)
PARAMETERS = ANALYSIS / "results/predictive_training_refinement/summary.json"
BALANCED = ANALYSIS / "results/calorimetry_balanced_reaction_validation/summary.json"
SETTINGS = ANALYSIS / "results/retained_predictive_parameter_settings.json"
RESULTS = ANALYSIS / "results/wong_free_co2_external_challenge"
FIGURES = ANALYSIS / "figures"
REFERENCE_TEMPERATURE_K = 313.15
HIGH_TEMPERATURE_K = 353.15


def _adjustments(temperature_k: float, r4: float, r5: float) -> dict[str, float]:
    scale = ((1.0 / temperature_k) - (1.0 / REFERENCE_TEMPERATURE_K)) / (
        (1.0 / HIGH_TEMPERATURE_K) - (1.0 / REFERENCE_TEMPERATURE_K)
    )
    return {"R4": r4 * scale, "R5": r5 * scale}


def _solve(
    payload: tuple[str, dict[str, object], dict[str, str], dict[str, float]],
) -> dict[str, object]:
    candidate, mapping, row, adjustments = payload
    try:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        liquid = _liquid(
            parameters,
            identity=f"{candidate}-{row['observation_id']}",
            temperature_k=float(row["temperature_K"]),
            pressure_pa=float(row["pressure_Pa"]),
            loading=float(row["co2_loading_mol_per_mol_mea"]),
            reaction_ln_k_adjustments=adjustments,
        )
        reference = liquid.continuation_reference
        concentration = (
            float(reference.mole_fractions[0])
            / float(reference.molar_volume_m3_per_mol)
            / 1000.0
        )
        return {
            "candidate": candidate,
            **row,
            "status": "evaluated",
            "predicted_free_co2_concentration_mol_L": concentration,
            "predicted_henry_constant_kPa_L_per_mol": (
                float(row["pressure_Pa"]) / 1000.0 / concentration
            ),
            "predicted_free_co2_mole_fraction": reference.mole_fractions[0],
            "predicted_molar_volume_m3_per_mol": reference.molar_volume_m3_per_mol,
            "delta_ln_k_r4": adjustments.get("R4", 0.0),
            "delta_ln_k_r5": adjustments.get("R5", 0.0),
        }
    except Exception as error:
        return {"candidate": candidate, **row, "status": "failed", "reason": str(error)}


def _metrics(
    rows: list[dict[str, object]], predicted: str, observed: str
) -> dict[str, float | int]:
    residuals = [math.log(float(row[predicted]) / float(row[observed])) for row in rows]
    rmse = math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
    return {
        "target_count": len(rows),
        "log_rmse": rmse,
        "rms_factor": math.exp(rmse),
        "mean_log_bias": math.fsum(residuals) / len(residuals),
        "absolute_average_relative_deviation_percent": 100.0
        * math.fsum(
            abs(float(row[predicted]) / float(row[observed]) - 1.0) for row in rows
        )
        / len(rows),
    }


def _plot(rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    _write_csv(FIGURES / "wong_free_co2_external_challenge_plot_data.csv", rows)
    frame = pd.DataFrame(rows)
    colors = {303.15: "#0072B2", 313.15: "#009E73", 323.15: "#D55E00"}
    styles = {
        "retained": "-",
        "calorimetry_balanced": "--",
    }
    figure, axes = plt.subplots(1, 2, figsize=(12.5, 5.2), constrained_layout=True)
    panels = (
        (
            axes[0],
            "free_co2_concentration_mol_L",
            "predicted_free_co2_concentration_mol_L",
            r"Free molecular CO$_2$ (mol L$^{-1}$)",
        ),
        (
            axes[1],
            "henry_constant_kPa_L_per_mol",
            "predicted_henry_constant_kPa_L_per_mol",
            r"$H_{CO_2}$ (kPa L mol$^{-1}$)",
        ),
    )
    for axis, observed, predicted, ylabel in panels:
        for temperature, color in colors.items():
            measured = frame.loc[
                (frame["candidate"] == "retained")
                & (frame["temperature_K"].astype(float) == temperature)
            ].sort_values("co2_loading_mol_per_mol_mea")
            axis.scatter(
                measured["co2_loading_mol_per_mol_mea"].astype(float),
                measured[observed].astype(float),
                facecolors="none",
                edgecolors=color,
                s=42,
                zorder=3,
                label=f"{temperature:.2f} K data",
            )
            for candidate, linestyle in styles.items():
                model = frame.loc[
                    (frame["candidate"] == candidate)
                    & (frame["temperature_K"].astype(float) == temperature)
                ].sort_values("co2_loading_mol_per_mol_mea")
                axis.plot(
                    model["co2_loading_mol_per_mol_mea"].astype(float),
                    model[predicted].astype(float),
                    color=color,
                    linestyle=linestyle,
                    linewidth=1.5,
                    label=f"{temperature:.2f} K {candidate.replace('_', ' ')}",
                )
        axis.set_yscale("log")
        axis.set_xlabel(r"CO$_2$ loading (mol mol$^{-1}$ MEA)")
        axis.set_ylabel(ylabel)
        finish_axes(axis)
    axes[1].legend(fontsize=7.5, ncol=2, frameon=False, loc="best")
    metrics = summary["candidate_metrics"]
    figure.suptitle(
        "Wong et al. (2016) 30 wt% MEA free-CO₂ external challenge\n"
        f"RMS concentration factor: retained {metrics['retained']['free_co2']['rms_factor']:.2f}, "
        f"balanced {metrics['calorimetry_balanced']['free_co2']['rms_factor']:.2f}",
        fontsize=13,
    )
    save_figure_bundle(figure, FIGURES / "wong_free_co2_external_challenge", dpi=220)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        parser.error("--workers must be 1 or 2")

    with SOURCE.open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    mapping = materialize_parameter_candidate(PARAMETERS)
    evidence_pressure_max_pa = max(
        float(domain["pressure_max"]["magnitude"]) for domain in mapping["domains"]
    )
    mapping = expand_parameter_domain(
        mapping,
        temperatures_k=tuple(float(row["temperature_K"]) for row in source_rows),
        pressures_pa=tuple(float(row["pressure_Pa"]) for row in source_rows),
    )
    execution_pressure_max_pa = max(
        float(domain["pressure_max"]["magnitude"]) for domain in mapping["domains"]
    )
    balanced = json.loads(BALANCED.read_text(encoding="utf-8"))
    r4 = float(balanced["candidate_r4_delta_ln_k_at_353_15_k"])
    r5 = float(balanced["candidate_r5_delta_ln_k_at_353_15_k"])
    payloads = []
    for row in source_rows:
        temperature = float(row["temperature_K"])
        state_mapping = _anchored_mapping(mapping, temperature)
        payloads.append(("retained", state_mapping, row, {}))
        if not math.isclose(temperature, REFERENCE_TEMPERATURE_K):
            payloads.append(
                (
                    "calorimetry_balanced",
                    state_mapping,
                    row,
                    _adjustments(temperature, r4, r5),
                )
            )

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(_solve, payloads))
    failures = [row for row in rows if row["status"] != "evaluated"]
    evaluated = [row for row in rows if row["status"] == "evaluated"]
    anchor_rows = [
        {**row, "candidate": "calorimetry_balanced"}
        for row in evaluated
        if row["candidate"] == "retained"
        and math.isclose(float(row["temperature_K"]), REFERENCE_TEMPERATURE_K)
    ]
    evaluated.extend(anchor_rows)
    evaluated.sort(
        key=lambda row: (
            str(row["candidate"]),
            float(row["temperature_K"]),
            float(row["pressure_bar"]),
        )
    )

    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    _write_csv(RESULTS / "predictions.csv", evaluated)
    (RESULTS / "excluded_source_rows.csv").unlink(missing_ok=True)
    if failures:
        _write_csv(RESULTS / "failures.csv", failures)
    else:
        (RESULTS / "failures.csv").unlink(missing_ok=True)
    candidate_metrics = {}
    for candidate in ("retained", "calorimetry_balanced"):
        selected = [row for row in evaluated if row["candidate"] == candidate]
        candidate_metrics[candidate] = {
            "free_co2": _metrics(
                selected,
                "predicted_free_co2_concentration_mol_L",
                "free_co2_concentration_mol_L",
            ),
            "henry_constant": _metrics(
                selected,
                "predicted_henry_constant_kPa_L_per_mol",
                "henry_constant_kPa_L_per_mol",
            ),
        }
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    summary = {
        "schema": "mea.wong-free-co2-external-challenge.v1",
        "status": "completed" if not failures else "completed_with_failures",
        "source": "Wong et al. (2016), DOI 10.1016/j.jngse.2016.10.029, Table 3",
        "analysis_role": "external_challenge_omitted_internal_standard_salt",
        "reason_not_scoring": "all source solutions contain 0.517 mol/kg NaClO4, absent from the current nine-species model",
        "source_row_count": len(source_rows),
        "evidence_pressure_max_pa": evidence_pressure_max_pa,
        "execution_pressure_max_pa": execution_pressure_max_pa,
        "execution_domain_policy": "input-state union; values above the evidence range are reported as extrapolation rather than rejected",
        "evaluated_candidate_state_count": len(evaluated),
        "failed_candidate_state_count": len(failures),
        "candidate_metrics": candidate_metrics,
        "balanced_reaction_corrections": {
            "delta_ln_k_r4_at_353_15_k": r4,
            "delta_ln_k_r5_at_353_15_k": r5,
            "zero_anchor_temperature_k": REFERENCE_TEMPERATURE_K,
        },
        "shared_parameter_settings": settings,
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _plot(evaluated, summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
