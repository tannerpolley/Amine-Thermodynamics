"""Bounded R1--R5 reaction-enthalpy fit (retired until Engine #84 and #61).

Every fit mode -- screen, candidate, parity, benchmark, full replay, partial
summary and adoption -- depends on heat evaluations or on candidate and heat
records that only the thermal stages write, and those stages need the reaction
reference temperature derivative the pinned Engine does not expose (see
``evaluate_direct_absorption_heat``).  The sensitivity check needs reaction
coefficient equilibrium actions (Engine #61).  Only ``--self-check`` remains:
it verifies the reaction-enthalpy shift algebra, cohort roles and the recovery
attempt plan without an Engine solve.  The retired modes are in Git history.
"""

from __future__ import annotations

import argparse
import copy
import csv
import math
from pathlib import Path

from evaluate_direct_absorption_heat import THERMAL_REFERENCE_UNAVAILABLE
from shared_evaluation import (
    Anchor,
    attempt_plan,
    corrected_request,
    EXPECTED_REACTION_CORRELATIONS,
    _selected_reactions,
)
from run_direct_parameter_campaign import pressure_catalog


ANALYSIS = Path(__file__).resolve().parents[1]
HEAT_OBSERVATIONS = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
PIVOT_K = 313.15
R = 8.31446261815324
STEP_KJ_MOL = 2.5
# Independent holdout: Xu 2011 pressure rows never enter the objective.
HOLDOUT_PRESSURE_SOURCES = ("Xu2011",)
# Kim et al. 2014 is model-selection comparison only; fitted heat rows are
# Kim--Svendsen 2007 calibration rows.
PRESSURE_IDS = (
    "vle_obs_0206",
    "vle_obs_0208",
    "vle_obs_0211",
    "vle_obs_0227",
    "vle_obs_0228",
    "vle_obs_0232",
)
HEAT_IDS = (
    "kim2007_t40_r1_0.124",
    "kim2007_t40_r2_0.375",
    "kim2007_t40_r2_0.543",
    "kim2007_t80_r2_0.137",
    "kim2007_t80_r2_0.375",
    "kim2007_t80_r2_0.570",
)
REACTIONS = ("R1", "R2", "R3", "R4", "R5")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def baseline_reactions() -> dict[str, float]:
    values = _selected_reactions()
    for reaction in ("R1", "R3"):
        source = EXPECTED_REACTION_CORRELATIONS[reaction]
        for coefficient in ("a", "b_k", "c", "d_per_k"):
            values[f"reaction:{reaction}:correlation:{coefficient}"] = float(
                source[coefficient]
            )
    return values


def shifted_reactions(shifts_kj_mol: dict[str, float]) -> dict[str, float]:
    values = baseline_reactions()
    for reaction, shift_kj in shifts_kj_mol.items():
        shift = 1000.0 * shift_kj
        if reaction == "R5":
            values["reaction:R5:correlation:a_k"] += shift / (R * math.log(10.0))
            values["reaction:R5:correlation:b"] -= shift / (
                R * PIVOT_K * math.log(10.0)
            )
        else:
            values[f"reaction:{reaction}:correlation:a"] += shift / (R * PIVOT_K)
            values[f"reaction:{reaction}:correlation:b_k"] -= shift / R
    return values


def pivot_check(values: dict[str, float]) -> None:
    request = pressure_catalog(True)[0]["request"]
    base = corrected_request(request, baseline_reactions())
    trial = corrected_request(request, values)
    for old, new in zip(
        base["reaction_system"]["equilibrium_constants"],
        trial["reaction_system"]["equilibrium_constants"],
        strict=True,
    ):
        if not math.isclose(float(old[0]), float(new[0]), rel_tol=0.0, abs_tol=2e-12):
            raise AssertionError(f"pivot changed for {new[6]['reaction_id']}")


def pivot_rows(
    state: dict[str, object],
    baseline: dict[tuple[str, str], float],
    extra: dict[str, object],
) -> list[dict[str, object]]:
    """40 C rows: every ln K is pivot-preserved, so the baseline value is exact."""
    rows = []
    for target in state["targets"]:
        key = (state["observation_id"], target["identity"])
        present = key in baseline
        rows.append(
            {
                **extra,
                "family": state["family"],
                "observation_id": state["observation_id"],
                "source": state["source"],
                "temperature_C": 40,
                "loading": state["loading"],
                "target": target["identity"],
                "observed": target["observed"],
                "predicted": baseline[key] if present else "",
                "status": "pivot_reuse" if present else "non_evaluable",
                "failure_code": "" if present else "baseline_non_evaluable",
                "failure_diagnostic": "",
                "attempt_count": 0,
                "wall_s": 0.0,
                "cache_hit": True,
            }
        )
    return rows


def self_check() -> None:
    base = baseline_reactions()
    assert all(base[identity] == value for identity, value in _selected_reactions().items())
    for reaction in REACTIONS:
        trial = shifted_reactions({reaction: STEP_KJ_MOL})
        pivot_check(trial)
        assert trial != base
        for temperature_k in (293.15, 313.15, 353.15, 393.15):
            request = copy.deepcopy(pressure_catalog(True)[0]["request"])
            request["temperature"]["value"] = temperature_k
            old = corrected_request(request, base)["reaction_system"]["engine_reactions"]
            new = corrected_request(request, trial)["reaction_system"]["engine_reactions"]
            for index, (before, after) in enumerate(
                zip(old, new, strict=True), start=1
            ):
                expected = 1000.0 * STEP_KJ_MOL if reaction == f"R{index}" else 0.0
                before_correlation = before["engine_correlation"]
                after_correlation = after["engine_correlation"]
                actual = (
                    R
                    * temperature_k**2
                    * (
                        -after_correlation["b"] / temperature_k**2
                        + after_correlation["c"] / temperature_k
                        + after_correlation["d"]
                        + before_correlation["b"] / temperature_k**2
                        - before_correlation["c"] / temperature_k
                        - before_correlation["d"]
                    )
                )
                assert math.isclose(actual, expected, rel_tol=2e-12, abs_tol=2e-8)
    # Cohort roles.
    heat = {row["record_id"]: row for row in read_csv(HEAT_OBSERVATIONS)}
    assert all(heat[k]["campaign_partition"] == "calibration" for k in HEAT_IDS)
    pressure = {row["observation_id"]: row for row in pressure_catalog(True)}
    assert all(
        pressure[k]["source"] not in HOLDOUT_PRESSURE_SOURCES for k in PRESSURE_IDS
    )
    # Status can never be "evaluated" without a prediction.
    fake_state = {
        "family": "pressure",
        "observation_id": "x",
        "source": "s",
        "temperature_c": 40,
        "loading": 0.1,
        "targets": [
            {
                "identity": "pCO2",
                "prediction_identity": "co2-partial-pressure",
                "observed": 1.0,
                "unit_scale": 1.0,
            }
        ],
    }
    assert pivot_rows(fake_state, {}, {})[0]["status"] == "non_evaluable"
    # Duplicate starts collapse in the attempt plan.
    a = Anchor(120, 0.1, 1.0e5, (0.5, 0.5), 1e-5)
    kinds = [k for k, _ in attempt_plan(120, 0.12, [a, a])]
    assert sorted(kinds) == [
        "cold-packet-start",
        "same-temperature-anchor",
    ]
    print("self-check passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--sensitivity-check", action="store_true")
    # Retired modes stay parseable so they stop with the reason below.
    for flag in (
        "--parity", "--benchmark", "--adopt", "--candidate", "--full", "--summarize-partial"
    ):
        parser.add_argument(flag, action="store_true")
    parser.add_argument("--groups", nargs="+")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--budget-s", type=float, default=900.0)
    args = parser.parse_args()
    if args.self_check:
        self_check()
    elif args.sensitivity_check:
        raise RuntimeError(
            "reaction-coefficient equilibrium actions are unavailable in the pinned "
            "Engine (active parameters address EOS families only; "
            "tannerpolley/ePC-SAFT#61); the retained sensitivity-check results are "
            "left unchanged"
        )
    else:
        # The candidate, adoption and full-replay modes all depend on heat and
        # candidate records that only the #84-blocked stages write.
        raise RuntimeError(THERMAL_REFERENCE_UNAVAILABLE)


if __name__ == "__main__":
    main()
