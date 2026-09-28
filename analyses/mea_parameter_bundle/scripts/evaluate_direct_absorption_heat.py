"""Finite-dose heat of CO2 absorption from the Engine's record-anchored total enthalpy.

Each retained calorimetry interval (prior loading a1 to loading a2 at fixed T, 30 mass %
MEA, 1 mol MEA) is scored as the heat released per mole of CO2 absorbed,

    Q = -[H_L(a2) - H_L(a1) - (a2 - a1) h_CO2^ig(T)] / (a2 - a1),

where H_L is the Engine total enthalpy of the equilibrium liquid at its bubble point
(EqID reference_species_calorics, ePC-SAFT #84/#138). CO2, water and MEA carry the
ideal-gas records of ``verify_reference_calorics.record``; the Engine completes the
ions from the R1-R5 reaction enthalpies. Assumptions: zero calorimeter vapor inventory
and ideal-gas CO2 feed at T. Q is independent of the neutral cp and formation
constants: each interval adds only CO2, so they cancel between the endpoints.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import statistics
from pathlib import Path
from time import perf_counter

import epcsaft
import matplotlib.pyplot as plt

import verify_reference_calorics as vrc
from refresh_results import bounded_main
from result_freshness import source_hashes, stamp_results
from run_direct_parameter_campaign import load_packet, pressure_templates
from shared_evaluation import (
    ENGINE_WHEEL_SHA256,
    PARAMETERS,
    STATE_PACKET,
    EvaluationLimits,
    anchor_from,
    cached_anchors,
    evaluate_state,
    load_parameters,
    parameter_fingerprint,
    parameter_mapping,
    reaction_values,
    sha256,
    verify_wheel,
)

ANALYSIS = Path(__file__).resolve().parents[1]
OBSERVATIONS = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
RESULTS = ANALYSIS / "results/calorimetry"
FIGURES = ANALYSIS / "figures/calorimetry/output"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def thermal_model() -> tuple[epcsaft.Mixture, str]:
    """Adopted parameters with MEA's physical ideal-gas records; its cache identity includes both."""
    fingerprint = parameter_fingerprint({"parameters": parameter_mapping(),
                                         "thermal_sha256": sha256(vrc.PHYSICAL_CALORICS)})
    return epcsaft.Mixture(load_parameters(), thermochemistry=vrc.record()), fingerprint


def heat_request(templates: dict, temperature_c: int, loading: float) -> dict[str, object]:
    """The nearest-loading packet pressure request at T with CO2 feed = loading (1 mol MEA)."""
    request = copy.deepcopy(min(templates[temperature_c], key=lambda item: abs(item[0] - loading))[1])
    system = request["reaction_system"]
    system["feed_amounts_mol"][0] = loading
    system["conserved_totals"] = [
        math.fsum(c * n for c, n in zip(balance, system["feed_amounts_mol"], strict=True))
        for balance in system["balance_matrix"]
    ]
    return request


def interval_heat(h_prior: float, h_current: float, prior: float, current: float, temperature_k: float) -> float:
    """Heat released per mol CO2, kJ/mol, for an ideal-gas CO2 dose from prior to current loading."""
    gas = vrc.co2_gas_enthalpy(temperature_k)
    return -((h_current - h_prior) - (current - prior) * gas) / (current - prior) / 1000.0


def metrics(rows: list[dict[str, object]]) -> dict[str, object]:
    residuals = [float(r["residual_kj_per_mol_CO2"]) for r in rows if r["status"] == "evaluated"]
    return {
        "attempted": len(rows),
        "evaluated": len(residuals),
        "failed": len(rows) - len(residuals),
        "rmse_kj_per_mol_CO2": math.sqrt(statistics.fmean(v * v for v in residuals)) if residuals else None,
        "mean_bias_kj_per_mol_CO2": statistics.fmean(residuals) if residuals else None,
        "median_absolute_error_kj_per_mol_CO2": statistics.median(map(abs, residuals)) if residuals else None,
    }


def score(reactions: dict[str, float], model: epcsaft.Mixture, fingerprint: str, observations: list[dict[str, str]],
          limits: EvaluationLimits, label: str = "calorimetry") -> tuple[list[dict], list[dict], list[dict]]:
    """Solve every interval endpoint once and score each observation; failures are kept, never dropped."""
    templates = pressure_templates(load_packet())
    endpoints: dict[int, set[float]] = {}
    for row in observations:
        endpoints.setdefault(round(float(row["temperature_C"])), set()).update(
            (float(row["previous_loading_mol_per_mol_mea"]), float(row["co2_loading_mol_per_mol_mea"])))
    anchors = cached_anchors(set(endpoints))
    states, attempts, enthalpy = [], [], {}
    for temperature_c in sorted(endpoints):
        # High to low loading: the pinned Engine's cold start fails below loading ~0.04 at 40 C
        # (fixed by ePC-SAFT #154/#157), so low-loading endpoints start from a same-temperature anchor.
        for loading in sorted(endpoints[temperature_c], reverse=True):
            record = evaluate_state(model, heat_request(templates, temperature_c, loading), reactions,
                                    f"{label}-{temperature_c}C-{loading:.6f}", anchors, limits=limits,
                                    model_fingerprint=fingerprint)
            attempts += [{"temperature_C": temperature_c, "loading_mol_CO2_per_mol_MEA": loading, "attempt": i,
                          "start_kind": a.get("kind", ""), "status": a.get("status", ""),
                          "failure_code": a.get("failure_code", ""), "wall_s": a.get("wall_s", 0.0)}
                         for i, a in enumerate(record["attempts"], start=1)]
            evaluated = record["status"] == "evaluated" and record["total_enthalpy_j"] is not None
            if evaluated:
                enthalpy[(temperature_c, loading)] = float(record["total_enthalpy_j"])
                anchors.append(anchor_from(record))
            states.append({"temperature_C": temperature_c, "loading_mol_CO2_per_mol_MEA": loading,
                           "status": "evaluated" if evaluated else "failed",
                           "failure_code": "" if evaluated else record["failure_code"] or "enthalpy_unavailable",
                           "system_pressure_pa": record["predictions"].get("system-pressure", ""),
                           "total_liquid_enthalpy_j": record["total_enthalpy_j"] or "",
                           "liquid_amount_mol": record["amount_mol"] or ""})
    comparison = []
    for row in observations:
        temperature_c = round(float(row["temperature_C"]))
        prior, current = float(row["previous_loading_mol_per_mol_mea"]), float(row["co2_loading_mol_per_mol_mea"])
        pair = enthalpy.get((temperature_c, prior)), enthalpy.get((temperature_c, current))
        observed = float(row["dh_kj_per_mol_co2"])
        predicted = None if None in pair else interval_heat(*pair, prior, current, temperature_c + 273.15)
        comparison.append({
            "record_id": row["record_id"], "source": row["source"], "temperature_C": temperature_c,
            "campaign_partition": row["campaign_partition"], "prior_loading_mol_CO2_per_mol_MEA": prior,
            "loading_mol_CO2_per_mol_MEA": current, "observed_heat_release_kj_per_mol_CO2": observed,
            "predicted_heat_release_kj_per_mol_CO2": "" if predicted is None else predicted,
            "residual_kj_per_mol_CO2": "" if predicted is None else predicted - observed,
            "status": "evaluated" if predicted is not None else "endpoint_failed",
        })
    return states, attempts, comparison


def render(comparison: list[dict[str, object]]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    for (temperature_c, color) in ((40, "#0072B2"), (80, "#009E73"), (120, "#D55E00")):
        rows = sorted((r for r in comparison if r["temperature_C"] == temperature_c),
                      key=lambda r: r["loading_mol_CO2_per_mol_MEA"])
        ax.scatter([r["loading_mol_CO2_per_mol_MEA"] for r in rows], [r["observed_heat_release_kj_per_mol_CO2"] for r in rows],
                   facecolors="none", edgecolors=color, s=24, label=f"Kim calorimetry, {temperature_c} °C")
        model = [r for r in rows if r["status"] == "evaluated" and r["source"] == "Kim and Svendsen 2007"]
        ax.plot([r["loading_mol_CO2_per_mol_MEA"] for r in model], [r["predicted_heat_release_kj_per_mol_CO2"] for r in model],
                "--", color=color, lw=1.2, label=f"Model intervals, {temperature_c} °C")
    ax.set(xlabel="CO$_2$ loading (mol mol$^{-1}$ MEA)", ylabel="Heat released (kJ mol$^{-1}$ CO$_2$)")
    ax.legend(ncol=2, fontsize=7)
    fig.tight_layout()
    for suffix in (".svg", ".pdf"):
        fig.savefig(FIGURES / f"current-selected-direct-enthalpy{suffix}",
                    metadata={"Date": None} if suffix == ".svg" else {"CreationDate": None})
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-timeout-s", type=float, default=60.0)
    parser.add_argument("--overall-timeout-s", type=float, default=1800.0)
    args = parser.parse_args()
    verify_wheel()
    inputs = source_hashes(OBSERVATIONS, STATE_PACKET, Path(__file__), Path(__file__).with_name("shared_evaluation.py"),
                           Path(__file__).with_name("verify_reference_calorics.py"), vrc.PHYSICAL_CALORICS)
    limits = EvaluationLimits(args.state_timeout_s, args.overall_timeout_s, perf_counter() + args.overall_timeout_s)
    model, fingerprint = thermal_model()
    observations = [r for r in read_rows(OBSERVATIONS) if r["regression_eligible"] == "true"]
    states, attempts, comparison = score(reaction_values(parameter_mapping()), model, fingerprint, observations, limits)
    summary = {
        "schema": "mea.selected-bundle-direct-total-enthalpy-calorimetry.v2",
        "method": __doc__.strip().splitlines()[0],
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "parameter_document_sha256": sha256(PARAMETERS),
        "observations_sha256": sha256(OBSERVATIONS),
        "physical_calorics_sha256": sha256(vrc.PHYSICAL_CALORICS),
        "assumptions": ["zero calorimeter vapor inventory", "ideal-gas CO2 feed at the calorimeter temperature",
                        "each observation is scored on its declared finite loading interval"],
        "endpoint_states": {"attempted": len(states), "evaluated": sum(s["status"] == "evaluated" for s in states)},
        "solver_attempts": {"total": len(attempts), "failed_before_recovery": sum(a["status"] != "evaluated" for a in attempts)},
        **metrics(comparison),
        "by_temperature_C": {str(t): metrics([r for r in comparison if r["temperature_C"] == t])
                             for t in sorted({r["temperature_C"] for r in comparison})},
        "by_campaign_partition": {p: metrics([r for r in comparison if r["campaign_partition"] == p])
                                  for p in sorted({r["campaign_partition"] for r in comparison})},
        "claim_limit": "Calorimetry intervals at 40/80 C are calibration-labelled and six entered the reaction-temperature "
                       "fit; 120 C Kim-Svendsen rows are a temperature holdout; Kim 2014 rows are model-selection "
                       "comparison. Numerical qualification of the Engine calorics is separate (ePC-SAFT #61 analysis).",
    }
    write_rows(RESULTS / "current-selected-direct-enthalpy-states.csv", states)
    write_rows(RESULTS / "current-selected-direct-enthalpy-attempts.csv", attempts)
    write_rows(RESULTS / "current-selected-direct-enthalpy-comparison.csv", comparison)
    (RESULTS / "current-selected-direct-enthalpy-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    render(comparison)
    stamp_results(RESULTS / "current-selected-direct-enthalpy-summary.json",
                  [RESULTS / f"current-selected-direct-enthalpy-{n}.csv" for n in ("states", "attempts", "comparison")]
                  + [FIGURES / "current-selected-direct-enthalpy.svg"], inputs=inputs)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("assumptions",)}, indent=2))


if __name__ == "__main__":
    bounded_main(main)
