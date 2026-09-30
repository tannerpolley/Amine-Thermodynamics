"""Score every active speciation observation, nondetections and failures included.

The calibration statistics (``generate_figure_data``) score positive packet targets only.
This stage covers what they leave out, on the adopted model:
- every active 30 mass % Böttinger 2008, Jakobsen 2005 and Matin 2012 row in its reported
  true-species liquid mole-fraction basis, including states outside the calibration packet
  (Böttinger above loading 0.5 at 20-80 C, all Jakobsen), marked by ``in_packet``;
- reported zeros (nondetections) as censored rows: the model value is compared with two
  thresholds frozen before scoring, the half-unit of the fourth decimal the tables report
  (5e-5) and the smallest positive value the same source reports for that species
  among its active 30 mass % rows;
- the pressure rows of ``current-best-fit-residuals.csv`` by role (Xu 2011 is the holdout),
  counting failed or non-positive predictions instead of dropping them.
Each row is scored on the model basis its membership row's ``linear_coefficients`` give
(``speciation_target_membership.csv``, keyed by the row's record id); a blank cell means the
reported species alone.
"""

from __future__ import annotations

import copy
import csv
import json
import math
import statistics
from pathlib import Path

import epcsaft

from generate_figure_data import SPECIES_LABELS
from refresh_results import bounded_main
from run_direct_parameter_campaign import speciation_catalog
from shared_evaluation import (
    CANONICAL_SPECIATION,
    COMPONENT_IDS,
    ENGINE_WHEEL_SHA256,
    PARAMETERS,
    EvaluationLimits,
    anchor_from,
    evaluate_state,
    load_parameters,
    parameter_mapping,
    reaction_values,
    sha256,
    verify_wheel,
)

ANALYSIS = Path(__file__).resolve().parents[1]
OUTPUT = ANALYSIS / "results/observation-coverage"
PRESSURE = ANALYSIS / "results/current-best-fit-residuals.csv"
MEMBERSHIP = ANALYSIS.parents[1] / "data/reference/MEA/manifests/speciation_target_membership.csv"
SOURCES = ("Bottinger2008", "Jakobsen2005", "Matin2012")
REPORTING_HALF_UNIT = 5e-5
HOLDOUT_PRESSURE_SOURCES = ("Xu2011",)
MODEL_SPECIES = {label: (component,) for component, label in SPECIES_LABELS.items()}
MODEL_SPECIES["MEA + MEAH+"] = ("monoethanolamine", "protonated-monoethanolamine")
CARBON_SEEDS = [COMPONENT_IDS.index(c) for c in ("carbamate-anion", "bicarbonate-anion", "carbonate-anion")]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def state_key(source: str, temperature_c: float, loading: float) -> tuple[str, int, float]:
    return source, round(temperature_c), round(loading, 4)


def requests() -> dict[tuple[str, int, float], tuple[dict, bool]]:
    """Packet requests where they exist; other active states from the nearest-temperature packet template."""
    catalog = speciation_catalog()
    packet = {}
    for state in catalog:
        feed = state["request"]["reaction_system"]["feed_amounts_mol"]
        loading = feed[0] + sum(feed[i] for i in CARBON_SEEDS)
        packet[state_key(state["source"], state["temperature_c"], loading)] = (state["request"], True)
    states = {}
    for row in read(CANONICAL_SPECIATION):
        if row["source_key"] not in SOURCES or row["target_membership"] != "active_v1" or float(row["mea_mass_fraction"]) != 0.3:
            continue
        temperature_c, loading = float(row["temperature_C"]), float(row["co2_loading_mol_per_mol_mea"])
        key = state_key(row["source_key"], temperature_c, loading)
        if key in states:
            continue
        if key in packet:
            states[key] = packet[key]
            continue
        template = copy.deepcopy(min(catalog, key=lambda s: abs(s["temperature_c"] - temperature_c))["request"])
        system = template["reaction_system"]
        template["temperature"]["value"] = temperature_c + 273.15
        system["feed_amounts_mol"][0] = loading - sum(system["feed_amounts_mol"][i] for i in CARBON_SEEDS)
        system["conserved_totals"] = [math.fsum(c * n for c, n in zip(b, system["feed_amounts_mol"], strict=True))
                                      for b in system["balance_matrix"]]
        states[key] = (template, False)
    return states


def speciation_rows(limits: EvaluationLimits) -> list[dict[str, object]]:
    model, reactions = epcsaft.Mixture(load_parameters()), reaction_values(parameter_mapping())
    canonical = [r for r in read(CANONICAL_SPECIATION) if r["source_key"] in SOURCES
                 and r["target_membership"] == "active_v1" and float(r["mea_mass_fraction"]) == 0.3]
    coefficients_by_record = {r["measurement_identity"]: r["linear_coefficients"] for r in read(MEMBERSHIP)
                              if r["measurement_identity"]}
    floor = {}
    for r in canonical:
        if r["measurement_role"] == "direct_positive":
            key = (r["source_key"], r["species"])
            floor[key] = min(floor.get(key, math.inf), float(r["value_mole_fraction"]))
    solved, anchors = {}, []
    for key, (request, in_packet) in sorted(requests().items()):
        record = evaluate_state(model, request, reactions, f"coverage-{key[0]}-{key[1]}C-{key[2]:.4f}", anchors, limits=limits)
        liquid = None
        if record["status"] == "evaluated":
            anchors.append(anchor_from(record))
            phase = next(p for p in record["phases"] if p["role"] == "liquid")
            liquid = dict(zip(phase["support"], phase["mole_fractions"], strict=True))
        solved[key] = (liquid, in_packet, record["failure_code"])
    rows = []
    for r in canonical:
        key = state_key(r["source_key"], float(r["temperature_C"]), float(r["co2_loading_mol_per_mol_mea"]))
        liquid, in_packet, failure = solved[key]
        species = r["species"]
        raw_coefficients = coefficients_by_record[r["record_id"]]
        coefficients = json.loads(raw_coefficients) if raw_coefficients else {species: 1.0}
        components = [(component, coefficient) for label, coefficient in coefficients.items()
                      for component in MODEL_SPECIES[label]]
        predicted = None if liquid is None else math.fsum(liquid[c] * coefficient for c, coefficient in components)
        observed = float(r["value_mole_fraction"])
        zero = r["measurement_role"] == "direct_zero"
        limit = floor.get((r["source_key"], species))
        rows.append({
            "record_id": r["record_id"], "source": r["source_key"], "temperature_C": r["temperature_C"],
            "loading_mol_CO2_per_mol_MEA": r["co2_loading_mol_per_mol_mea"], "species": species,
            "model_basis": "+".join(c for c, _ in components), "measurement_role": r["measurement_role"], "in_packet": in_packet,
            "observed_mole_fraction": observed, "predicted_mole_fraction": "" if predicted is None else predicted,
            "status": "failed" if predicted is None else ("nondetection" if zero else "scored"),
            "failure_code": failure if predicted is None else "",
            "ln_pred_over_obs": "" if predicted is None or zero or predicted <= 0 else math.log(predicted / observed),
            "below_reporting_half_unit": "" if predicted is None or not zero else predicted < REPORTING_HALF_UNIT,
            "source_smallest_positive": "" if limit is None else limit,
            "below_source_smallest_positive": "" if predicted is None or not zero or limit is None else predicted < limit,
        })
    return rows


def ln_stats(rows: list[dict[str, object]]) -> dict[str, object]:
    errors = [float(r["ln_pred_over_obs"]) for r in rows if r["ln_pred_over_obs"] != ""]
    return {"attempted": len(rows), "scored": len(errors),
            "failed": sum(r["status"] == "failed" for r in rows),
            "aard_percent": 100 * statistics.fmean(abs(math.exp(e) - 1) for e in errors) if errors else None,
            "mean_ln": statistics.fmean(errors) if errors else None,
            "rms_ln": math.sqrt(statistics.fmean(e * e for e in errors)) if errors else None}


def nondetection_stats(rows: list[dict[str, object]]) -> dict[str, object]:
    values = [float(r["predicted_mole_fraction"]) for r in rows if r["predicted_mole_fraction"] != ""]
    return {"attempted": len(rows), "failed": len(rows) - len(values),
            "below_reporting_half_unit": sum(r["below_reporting_half_unit"] is True for r in rows),
            "below_source_smallest_positive": sum(r["below_source_smallest_positive"] is True for r in rows),
            "median_model_mole_fraction": statistics.median(values) if values else None,
            "max_model_mole_fraction": max(values) if values else None}


def pressure_summary() -> dict[str, object]:
    rows = [r for r in read(PRESSURE) if r["family"] == "pressure"]
    groups = {"historical calibration-source rows (broad assessment)": [r for r in rows if r["source"] not in HOLDOUT_PRESSURE_SOURCES],
              "previously accessed Xu 2011 comparison (outside working range)": [r for r in rows if r["source"] in HOLDOUT_PRESSURE_SOURCES]}
    out = {}
    for name, members in groups.items():
        usable = [r for r in members if r["predicted"] and float(r["predicted"]) > 0 and float(r["observed"]) > 0]
        errors = [math.log(float(r["predicted"]) / float(r["observed"])) for r in usable]
        out[name] = {"attempted": len(members), "scored": len(usable), "failed_or_nonpositive": len(members) - len(usable),
                     "observed_zero": sum(float(r["observed"]) == 0 for r in members),
                     "aard_percent": 100 * statistics.fmean(abs(math.exp(e) - 1) for e in errors),
                     "mean_ln": statistics.fmean(errors), "rms_ln": math.sqrt(statistics.fmean(e * e for e in errors))}
    return out


def main() -> None:
    verify_wheel()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = speciation_rows(EvaluationLimits(60.0, 1800.0))
    write(OUTPUT / "speciation-rows.csv", rows)
    scored = [r for r in rows if r["measurement_role"] != "direct_zero"]
    zeros = [r for r in rows if r["measurement_role"] == "direct_zero"]
    summary = {
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256, "parameter_sha256": sha256(PARAMETERS),
        "canonical_speciation_sha256": sha256(CANONICAL_SPECIATION), "membership_sha256": sha256(MEMBERSHIP),
        "pressure_residuals_sha256": sha256(PRESSURE),
        "speciation": {
            "all_positive": ln_stats(scored),
            "by_source_and_packet": {f"{s} | {'packet' if p else 'outside packet'}": ln_stats(
                [r for r in scored if r["source"] == s and r["in_packet"] == p])
                for s in SOURCES for p in (True, False) if any(r["source"] == s and r["in_packet"] == p for r in scored)},
            "by_species": {sp: ln_stats([r for r in scored if r["species"] == sp]) for sp in sorted({r["species"] for r in scored})},
            "nondetections": {f"{s} | {sp}": nondetection_stats([r for r in zeros if r["source"] == s and r["species"] == sp])
                              for s, sp in sorted({(r["source"], r["species"]) for r in zeros})},
        },
        "pressure": pressure_summary(),
        "thresholds": {"reporting_half_unit": REPORTING_HALF_UNIT,
                       "source_smallest_positive": "smallest positive mole fraction the same source reports for the species"},
        "claim_limit": "Calibration and outside-packet rows share one adopted model; outside-packet rows were not fitted but "
                       "the sources were previously accessed. Nondetection thresholds are data-derived bounds: Böttinger "
                       "2008 states no detection limit (carbonate 'practically not present').",
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    bounded_main(main)
