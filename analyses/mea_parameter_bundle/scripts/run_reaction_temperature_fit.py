"""Bounded R1--R5 reaction-enthalpy screen and candidate replay on the Engine calorics.

Each reaction gets a constant reaction-enthalpy shift dh anchored at the 313.15 K pivot,
so every ln K is unchanged at the pivot (``shifted_reactions``). The screen solves the
sparse cohort (6 pressure, 12 speciation states, 6 Kim--Svendsen 2007 heat intervals) at the
adopted values and at dh = +-2.5 kJ/mol per reaction, forms the central-difference Jacobian of
the weighted residuals, and proposes the bounded linear least-squares step on the directions
with singular value >= 0.1 of the largest. ``--candidate`` replays the proposal exactly.
Xu 2011 pressure and the 120 C heat holdout never enter the objective. The proposal is
reported, not adopted (adoption is owned by MEA #107). Scenario differences are recorded
application-side re-solves; the Engine has no reaction-coefficient actions (ePC-SAFT #61 limit).
"""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
from time import perf_counter

import epcsaft
import numpy as np
from scipy.optimize import lsq_linear

from evaluate_direct_absorption_heat import read_rows, score, thermal_model, write_rows
from refresh_results import bounded_main
from run_direct_parameter_campaign import pressure_catalog, speciation_catalog
from shared_evaluation import (
    ENGINE_WHEEL_SHA256,
    EXPECTED_REACTION_CORRELATIONS,
    PARAMETERS,
    EvaluationLimits,
    anchor_from,
    corrected_request,
    evaluate_state,
    load_parameters,
    sha256,
    verify_wheel,
    _selected_reactions,
)

ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/reaction-temperature-fit"
HEAT_OBSERVATIONS = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
PIVOT_K = 313.15
R = 8.31446261815324
STEP_KJ_MOL = 2.5
BOUND_KJ_MOL = 5.0
SINGULAR_FLOOR = 0.1
HOLDOUT_PRESSURE_SOURCES = ("Xu2011",)
PRESSURE_IDS = ("vle_obs_0206", "vle_obs_0208", "vle_obs_0211", "vle_obs_0227", "vle_obs_0228", "vle_obs_0232")
SPECIATION_IDS = (
    "Bottinger2008_state_030", "Bottinger2008_state_033", "Matin2012_state_019", "Bottinger2008_state_042",
    "Bottinger2008_state_046", "Bottinger2008_state_050", "Bottinger2008_state_055", "Bottinger2008_state_057",
    "Bottinger2008_state_059", "Bottinger2008_state_063", "Bottinger2008_state_065", "Bottinger2008_state_067",
)
HEAT_IDS = ("kim2007_t40_r1_0.124", "kim2007_t40_r2_0.375", "kim2007_t40_r2_0.543",
            "kim2007_t80_r2_0.137", "kim2007_t80_r2_0.375", "kim2007_t80_r2_0.570")
REACTIONS = ("R1", "R2", "R3", "R4", "R5")


def baseline_reactions() -> dict[str, float]:
    values = _selected_reactions()
    for reaction in ("R1", "R3"):
        source = EXPECTED_REACTION_CORRELATIONS[reaction]
        for coefficient in ("a", "b_k", "c", "d_per_k"):
            values[f"reaction:{reaction}:correlation:{coefficient}"] = float(source[coefficient])
    return values


def shifted_reactions(shifts_kj_mol: dict[str, float]) -> dict[str, float]:
    values = baseline_reactions()
    for reaction, shift_kj in shifts_kj_mol.items():
        shift = 1000.0 * shift_kj
        if reaction == "R5":
            values["reaction:R5:correlation:a_k"] += shift / (R * math.log(10.0))
            values["reaction:R5:correlation:b"] -= shift / (R * PIVOT_K * math.log(10.0))
        else:
            values[f"reaction:{reaction}:correlation:a"] += shift / (R * PIVOT_K)
            values[f"reaction:{reaction}:correlation:b_k"] -= shift / R
    return values


def pivot_check(values: dict[str, float]) -> None:
    request = pressure_catalog(True)[0]["request"]
    base = corrected_request(request, baseline_reactions())
    trial = corrected_request(request, values)
    for old, new in zip(base["reaction_system"]["equilibrium_constants"],
                        trial["reaction_system"]["equilibrium_constants"], strict=True):
        if not math.isclose(float(old[0]), float(new[0]), rel_tol=0.0, abs_tol=2e-12):
            raise AssertionError(f"pivot changed for {new[6]['reaction_id']}")


def evaluate(label: str, shifts: dict[str, float], limits: EvaluationLimits) -> list[dict[str, object]]:
    """Sparse-cohort rows at one shift vector; a failed state keeps its row with no prediction."""
    reactions = shifted_reactions(shifts)
    model, anchors, rows = epcsaft.Mixture(load_parameters()), [], []
    catalog = {s["observation_id"]: s for s in (*pressure_catalog(True), *speciation_catalog())}
    for identity in (*PRESSURE_IDS, *SPECIATION_IDS):
        state = catalog[identity]
        record = evaluate_state(model, state["request"], reactions, f"{identity}-fit-{label}", anchors, limits=limits)
        if record["status"] == "evaluated" and state["family"] == "pressure":
            anchors.append(anchor_from(record))
        for target in state["targets"]:
            predicted = record["predictions"].get(target["prediction_identity"])
            rows.append({"family": state["family"], "key": f"{identity}:{target['identity']}",
                         "observed": float(target["observed"]),
                         "predicted": None if predicted is None else predicted * float(target["unit_scale"])})
    heat_model, fingerprint = thermal_model()
    heat = {r["record_id"]: r for r in read_rows(HEAT_OBSERVATIONS)}
    _, _, comparison = score(reactions, heat_model, fingerprint, [heat[k] for k in HEAT_IDS], limits, f"fit-{label}")
    rows += [{"family": "heat", "key": r["record_id"], "observed": r["observed_heat_release_kj_per_mol_CO2"],
              "predicted": r["predicted_heat_release_kj_per_mol_CO2"] if r["status"] == "evaluated" else None}
             for r in comparison]
    return [{"scenario": label, **{f"dh_{k}": shifts.get(k, 0.0) for k in REACTIONS}, **row} for row in rows]


def residual(row: dict[str, object]) -> float:
    """log10 ratio for pressure and speciation; kJ/mol difference for heat."""
    if row["family"] == "heat":
        return float(row["predicted"]) - float(row["observed"])
    return math.log10(float(row["predicted"]) / float(row["observed"]))


def scenarios() -> list[tuple[str, dict[str, float]]]:
    return [("baseline", {})] + [(f"{r}{sign}", {r: sign_value * STEP_KJ_MOL})
                                 for r in REACTIONS for sign, sign_value in (("+", 1.0), ("-", -1.0))]


def weights(base: dict[str, dict], keys: list[str]) -> np.ndarray:
    # ponytail: equal family weight, equal rows within a family; per-source grouping if a family is dominated by one source
    families = [base[k]["family"] for k in keys]
    scale = {f: math.sqrt(np.mean([residual(base[k]) ** 2 for k in keys if base[k]["family"] == f])) for f in set(families)}
    count = {f: families.count(f) for f in set(families)}
    return np.asarray([1.0 / (scale[f] * math.sqrt(count[f] * len(scale))) for f in families])


def run_screen(limits: EvaluationLimits) -> dict[str, object]:
    rows = [row for label, shifts in scenarios() for row in evaluate(label, shifts, limits)]
    write_rows(RESULTS / "screen-targets.csv", rows)
    by = {(r["scenario"], r["key"]): r for r in rows}
    labels = [label for label, _ in scenarios()]
    keys = sorted({r["key"] for r in rows if all(by[(s, r["key"])]["predicted"] not in (None, "") for s in labels)})
    base = {k: by[("baseline", k)] for k in keys}
    w = weights(base, keys)
    r0 = w * np.asarray([residual(base[k]) for k in keys])
    jacobian = np.column_stack([
        w * (np.asarray([residual(by[(f"{r}+", k)]) for k in keys]) - np.asarray([residual(by[(f"{r}-", k)]) for k in keys]))
        / (2 * STEP_KJ_MOL) for r in REACTIONS])
    u, s, vt = np.linalg.svd(jacobian, full_matrices=False)
    kept = vt[s >= SINGULAR_FLOOR * s[0]]
    reduced = lsq_linear(jacobian @ kept.T, -r0, bounds=(-BOUND_KJ_MOL, BOUND_KJ_MOL))
    proposal = kept.T @ reduced.x
    record = {
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256, "parameter_sha256": sha256(PARAMETERS),
        "scenarios": labels, "step_kj_per_mol": STEP_KJ_MOL, "common_targets": len(keys),
        "excluded_targets": len({r["key"] for r in rows}) - len(keys),
        "family_counts": {f: sum(base[k]["family"] == f for k in keys) for f in ("pressure", "speciation", "heat")},
        "family_rms": {f: math.sqrt(np.mean([residual(base[k]) ** 2 for k in keys if base[k]["family"] == f]))
                       for f in ("pressure", "speciation", "heat")},
        "singular_values": s.tolist(), "kept_directions": len(kept),
        "baseline_objective": float(r0 @ r0), "predicted_objective": float(np.sum((r0 + jacobian @ proposal) ** 2)),
        "proposed_shifts_kj_per_mol": dict(zip(REACTIONS, proposal.tolist(), strict=True)),
        "objective": "sum of squared residuals, equal family weight, each family scaled by its baseline RMS",
    }
    (RESULTS / "screen-record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def run_candidate(limits: EvaluationLimits) -> dict[str, object]:
    screen = json.loads((RESULTS / "screen-record.json").read_text())
    shifts = screen["proposed_shifts_kj_per_mol"]
    rows = evaluate("candidate", shifts, limits)
    by = {r["key"]: r for r in rows}
    base = {r["key"]: r for r in read_rows(RESULTS / "screen-targets.csv") if r["scenario"] == "baseline"}
    keys = sorted(k for k in base if base[k]["predicted"] and by[k]["predicted"] not in (None, ""))
    w = weights(base, keys)
    exact = w * np.asarray([residual(by[k]) for k in keys])
    receipt = {"shifts_kj_per_mol": shifts, "evaluated": len(keys), "attempted": len(rows),
               "baseline_objective": screen["baseline_objective"], "predicted_objective": screen["predicted_objective"],
               "exact_objective": float(exact @ exact),
               "family_rms": {f: math.sqrt(np.mean([residual(by[k]) ** 2 for k in keys if by[k]["family"] == f]))
                              for f in ("pressure", "speciation", "heat")},
               "decision": "reported; adoption belongs to MEA #107"}
    write_rows(RESULTS / "candidate-targets.csv", rows)
    (RESULTS / "candidate-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def self_check() -> None:
    base = baseline_reactions()
    assert all(base[identity] == value for identity, value in _selected_reactions().items())
    for reaction in REACTIONS:
        trial = shifted_reactions({reaction: STEP_KJ_MOL})
        pivot_check(trial)
        for temperature_k in (293.15, 313.15, 353.15, 393.15):
            request = copy.deepcopy(pressure_catalog(True)[0]["request"])
            request["temperature"]["value"] = temperature_k
            old = corrected_request(request, base)["reaction_system"]["engine_reactions"]
            new = corrected_request(request, trial)["reaction_system"]["engine_reactions"]
            for index, (before, after) in enumerate(zip(old, new, strict=True), start=1):
                expected = 1000.0 * STEP_KJ_MOL if reaction == f"R{index}" else 0.0
                b, a = before["engine_correlation"], after["engine_correlation"]
                actual = R * temperature_k**2 * (-(a["b"] - b["b"]) / temperature_k**2 + (a["c"] - b["c"]) / temperature_k
                                                 + a["d"] - b["d"])
                assert math.isclose(actual, expected, rel_tol=2e-12, abs_tol=2e-8)
    heat = {row["record_id"]: row for row in read_rows(HEAT_OBSERVATIONS)}
    assert all(heat[k]["campaign_partition"] == "calibration" for k in HEAT_IDS)
    pressure = {row["observation_id"]: row for row in pressure_catalog(True)}
    assert all(pressure[k]["source"] not in HOLDOUT_PRESSURE_SOURCES for k in PRESSURE_IDS)
    print("self-check passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument("--budget-s", type=float, default=3600.0)
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    verify_wheel()
    limits = EvaluationLimits(60.0, args.budget_s, perf_counter() + args.budget_s)
    print(json.dumps(run_candidate(limits) if args.candidate else run_screen(limits), indent=2))


if __name__ == "__main__":
    bounded_main(main)
