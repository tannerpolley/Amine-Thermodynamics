"""Bounded R1--R5 reaction-enthalpy screen with exact Engine replay.

One shared recovery policy (the retained baseline replay's ordering) serves the
screen, the candidate replay, the heat endpoints, parity, and the benchmark.
Every exact solve is cached per state under the ignored ``results/runs/``
directory with atomic writes, timing, and the attempt list that produced it.
"""

from __future__ import annotations

import os

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import argparse  # noqa: E402
import copy  # noqa: E402
import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402
from pathlib import Path  # noqa: E402
from time import perf_counter  # noqa: E402

import epcsaft  # noqa: E402
import numpy as np  # noqa: E402
from scipy.optimize import lsq_linear  # noqa: E402

from evaluate_direct_absorption_heat import (  # noqa: E402
    build_thermochemistry,
)
from shared_evaluation import (  # noqa: E402
    ENGINE_WHEEL_SHA256,
    PARAMETERS,
    Anchor,
    attempt_plan,
    cached_anchors,
    corrected_request,
    evaluate_state,
    anchor_from,
    EXPECTED_REACTION_CORRELATIONS,
    load_parameters,
    provenance as shared_provenance,
    sha256,
    _selected_reactions,
    _problem_from_request,
    _solve_in_child,
    verify_wheel as shared_verify_wheel,
)
from run_direct_parameter_campaign import pressure_catalog, speciation_catalog  # noqa: E402
from refresh_results import bounded_main  # noqa: E402
from result_freshness import FIGURE_DATA, HEAT, require_results  # noqa: E402


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/reaction-temperature-fit"
RUNS = ANALYSIS / "results/runs/reaction-temperature-fit"
HEAT_OBSERVATIONS = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
BASELINE_RESIDUALS = ANALYSIS / "results/current-best-fit-residuals.csv"
BASELINE_HEAT_STATES = (
    ANALYSIS / "results/calorimetry/current-selected-direct-enthalpy-states.csv"
)
PIVOT_K = 313.15
R = 8.31446261815324
STEP_KJ_MOL = 2.5
POLICY = "baseline-replay-recovery-v1"
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
SPECIATION_IDS = (
    "Bottinger2008_state_030",
    "Bottinger2008_state_033",
    "Matin2012_state_019",
    "Bottinger2008_state_042",
    "Bottinger2008_state_046",
    "Bottinger2008_state_050",
    "Bottinger2008_state_055",
    "Bottinger2008_state_057",
    "Bottinger2008_state_059",
    "Bottinger2008_state_063",
    "Bottinger2008_state_065",
    "Bottinger2008_state_067",
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


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = tuple(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def verify_wheel() -> None:
    shared_verify_wheel()


def driver_sha256() -> str:
    return sha256(Path(__file__).with_name("shared_evaluation.py"))


def quarter_cpu_affinity() -> tuple[int, ...]:
    available = sorted(os.sched_getaffinity(0))
    chosen = tuple(available[:1])
    os.sched_setaffinity(0, chosen)
    return chosen


def provenance(thermochemistry: object | None = None) -> dict[str, object]:
    return {
        **shared_provenance(thermochemistry),
        "driver_sha256": driver_sha256(),
        "policy": POLICY,
    }


# --- reaction shifts -------------------------------------------------------


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


# --- catalogs ----------------------------------------------------------------


def selected_catalog() -> list[dict[str, object]]:
    pressure = {row["observation_id"]: row for row in pressure_catalog(True)}
    speciation = {row["observation_id"]: row for row in speciation_catalog()}
    return [
        *(pressure[key] for key in PRESSURE_IDS),
        *(speciation[key] for key in SPECIATION_IDS),
    ]


def heat_rows() -> list[dict[str, str]]:
    rows = {row["record_id"]: row for row in read_csv(HEAT_OBSERVATIONS)}
    return [rows[key] for key in HEAT_IDS]


def pressure_templates() -> dict[int, list[tuple[float, dict[str, object]]]]:
    output: dict[int, list[tuple[float, dict[str, object]]]] = {}
    for row in pressure_catalog(True):
        output.setdefault(round(float(row["temperature_c"])), []).append(
            (float(row["loading"]), row["request"])
        )
    return output


def heat_request(temperature_c: int, loading: float) -> dict[str, object]:
    templates = pressure_templates()[temperature_c]
    request = copy.deepcopy(min(templates, key=lambda item: abs(item[0] - loading))[1])
    system = request["reaction_system"]
    system["feed_amounts_mol"][0] = loading
    system["conserved_totals"] = [
        math.fsum(
            c * n for c, n in zip(balance, system["feed_amounts_mol"], strict=True)
        )
        for balance in system["balance_matrix"]
    ]
    request["pressure"]["starts"] = [request["pressure"]["initial"]]
    return request


def require_current_baseline() -> None:
    """Screening and adoption must compare one identified incumbent."""
    selected = sha256(PARAMETERS)
    for receipt in (FIGURE_DATA, HEAT):
        require_results(receipt)
        if json.loads(receipt.read_text()).get("parameter_document_sha256") != selected:
            raise ValueError(
                "Baseline belongs to another selection; refresh before screening or adoption"
            )


def baseline_lookup() -> dict[tuple[str, str], float]:
    require_current_baseline()
    return {
        (row["observation_id"], row["target"]): float(row["predicted"])
        for row in read_csv(BASELINE_RESIDUALS)
        if row["predicted"] != ""
    }


def target_rows(
    state: dict[str, object], record: dict[str, object], extra: dict[str, object]
) -> list[dict[str, object]]:
    rows = []
    for target in state["targets"]:
        predicted = record["predictions"].get(target["prediction_identity"])
        rows.append(
            {
                **extra,
                "family": state["family"],
                "observation_id": state["observation_id"],
                "source": state["source"],
                "temperature_C": round(float(state["temperature_c"])),
                "loading": state["loading"],
                "target": target["identity"],
                "observed": target["observed"],
                "predicted": ""
                if predicted is None
                else predicted * float(target["unit_scale"]),
                "status": record["status"],
                "failure_code": record["failure_code"],
                "failure_diagnostic": record["failure_diagnostic"],
                "attempt_count": record.get("attempt_count", 0),
                "wall_s": record.get("wall_s", 0.0),
                "cache_hit": record.get("cache_hit", False),
            }
        )
    return rows


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


# --- heat ---------------------------------------------------------------------


def heat_endpoints(
    observations: list[dict[str, str]], temperature_c: int
) -> list[float]:
    return sorted(
        {
            loading
            for row in observations
            if round(float(row["temperature_C"])) == temperature_c
            for loading in (
                float(row["previous_loading_mol_per_mol_mea"]),
                float(row["co2_loading_mol_per_mol_mea"]),
            )
        }
    )


def solve_heat_endpoints(
    model: epcsaft.Mixture,
    reactions: dict[str, float],
    thermochemistry: object,
    temperature_c: int,
    loadings: list[float],
    anchors: list[Anchor],
    budget_s: float,
) -> tuple[
    dict[float, float], dict[float, dict[str, object]], dict[float, tuple[str, str]]
]:
    enthalpies: dict[float, float] = {}
    phases: dict[float, dict[str, object]] = {}
    failures: dict[float, tuple[str, str]] = {}
    for loading in loadings:
        record = evaluate_state(
            model,
            heat_request(temperature_c, loading),
            reactions,
            f"reaction-temperature-fit-{temperature_c}C-{loading:.6f}",
            anchors,
            thermochemistry,
            budget_s,
        )
        if record["status"] == "evaluated":
            enthalpies[loading] = float(record["total_enthalpy_j"])
            phases[loading] = {
                "temperature_C": temperature_c,
                "loading": loading,
                "molar_density_mol_m3": record["molar_density_mol_m3"],
                "mole_fractions": list(record["anchor"]["mole_fractions"]),
                "amount_mol": record["amount_mol"],
            }
            anchors.append(anchor_from(record))
        else:
            failures[loading] = (record["failure_code"], record["failure_diagnostic"])
    return enthalpies, phases, failures


def reused_enthalpy(
    model: epcsaft.Mixture, thermochemistry: object, phase: dict[str, object]
) -> float:
    state = model.state(
        T=(float(phase["temperature_C"]) + 273.15) * epcsaft.unit_registry.kelvin,
        rho=float(phase["molar_density_mol_m3"])
        * epcsaft.unit_registry.mole
        / epcsaft.unit_registry.meter**3,
        x=phase["mole_fractions"],
    )
    molar_h = float(state.h(thermochemistry).to("joule / mole").magnitude)
    return float(phase["amount_mol"]) * molar_h


def heat_release(
    thermochemistry: object,
    model: epcsaft.Mixture,
    temperature_c: int,
    prior: float,
    current: float,
    enthalpies: dict[float, float],
) -> float:
    feed_h = thermochemistry.enthalpies_j_per_mol(
        temperature_c + 273.15, model.component_ids
    )[0]
    return (
        -((enthalpies[current] - enthalpies[prior]) - (current - prior) * feed_h)
        / (current - prior)
        / 1000.0
    )


def heat_row(
    row: dict[str, str],
    predicted: object,
    status: str,
    code: str,
    diagnostic: str,
    extra: dict[str, object],
) -> dict[str, object]:
    return {
        **extra,
        "family": "heat",
        "observation_id": row["record_id"],
        "source": row["source"],
        "temperature_C": round(float(row["temperature_C"])),
        "loading": float(row["co2_loading_mol_per_mol_mea"]),
        "target": "heat_release",
        "observed": float(row["dh_kj_per_mol_co2"]),
        "predicted": predicted,
        "status": status,
        "failure_code": code,
        "failure_diagnostic": diagnostic,
        "partition": row["campaign_partition"],
    }


def make_pivot_phases() -> dict[str, dict[str, object]]:
    path = RESULTS / "cache/pivot-phases.json"
    receipt_path = RESULTS / "cache/pivot-phases-receipt.json"
    expected = {
        "parameter_sha256": sha256(PARAMETERS),
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
    }
    if path.exists():
        if json.loads(receipt_path.read_text(encoding="utf-8")) != expected:
            raise ValueError("pivot phase cache does not match the selected bundle")
        return json.loads(path.read_text(encoding="utf-8"))
    model = epcsaft.Mixture(load_parameters())
    reactions = shifted_reactions({})
    thermochemistry, _ = build_thermochemistry(model, pressure_templates(), reactions)
    _, phases, failures = solve_heat_endpoints(
        model,
        reactions,
        thermochemistry,
        40,
        heat_endpoints(heat_rows(), 40),
        [],
        math.inf,
    )
    if failures:
        raise RuntimeError(f"pivot endpoints failed: {failures}")
    write_json(path, {f"40:{loading:.6f}": phase for loading, phase in phases.items()})
    write_json(receipt_path, expected)
    return json.loads(path.read_text(encoding="utf-8"))


# --- screen ---------------------------------------------------------------------


def evaluate_scenario(
    task: tuple[str, dict[str, float], dict[str, dict[str, object]], float],
) -> tuple[str, list[dict[str, object]]]:
    scenario, shifts, pivot_phases, budget_s = task
    model = epcsaft.Mixture(load_parameters())
    reactions = shifted_reactions(shifts)
    pivot_check(reactions)
    thermochemistry, _ = build_thermochemistry(model, pressure_templates(), reactions)
    baseline = baseline_lookup()
    extra = {"scenario": scenario}
    rows: list[dict[str, object]] = []
    anchors: list[Anchor] = []
    states = sorted(
        selected_catalog(),
        key=lambda s: (
            s["family"] != "pressure",
            float(s["temperature_c"]),
            float(s["loading"]),
        ),
    )
    for state in states:
        temperature_c = round(float(state["temperature_c"]))
        if temperature_c == 40:
            rows.extend(pivot_rows(state, baseline, extra))
            continue
        record = evaluate_state(
            model,
            state["request"],
            reactions,
            f"{state['observation_id']}-{scenario}",
            anchors if state["family"] == "pressure" else [],
            None,
            budget_s,
        )
        rows.extend(target_rows(state, record, extra))
        if state["family"] == "pressure" and record["status"] == "evaluated":
            anchors.append(anchor_from(record))
    endpoint_h: dict[tuple[int, float], float] = {}
    for temperature_c in sorted(
        {round(float(r["temperature_C"])) for r in heat_rows()}
    ):
        loadings = heat_endpoints(heat_rows(), temperature_c)
        if temperature_c == 40:
            for loading in loadings:
                endpoint_h[(40, loading)] = reused_enthalpy(
                    model, thermochemistry, pivot_phases[f"40:{loading:.6f}"]
                )
            continue
        enthalpies, _, failures = solve_heat_endpoints(
            model,
            reactions,
            thermochemistry,
            temperature_c,
            loadings,
            anchors,
            budget_s,
        )
        if failures:
            raise RuntimeError(f"{scenario}: heat endpoints failed: {failures}")
        endpoint_h.update({(temperature_c, k): v for k, v in enthalpies.items()})
    for row in heat_rows():
        temperature_c = round(float(row["temperature_C"]))
        prior = float(row["previous_loading_mol_per_mol_mea"])
        current = float(row["co2_loading_mol_per_mol_mea"])
        predicted = heat_release(
            thermochemistry,
            model,
            temperature_c,
            prior,
            current,
            {k[1]: v for k, v in endpoint_h.items() if k[0] == temperature_c},
        )
        rows.append(heat_row(row, float(predicted), "evaluated", "", "", extra))
    return scenario, rows


def residual(row: dict[str, object]) -> float:
    predicted, observed = float(row["predicted"]), float(row["observed"])
    return (
        predicted - observed
        if row["family"] == "heat"
        else math.log10(predicted / observed)
    )


def fit_row(row: dict[str, object]) -> bool:
    if row["family"] == "pressure" and row["source"] in HOLDOUT_PRESSURE_SOURCES:
        return False
    if row["family"] == "heat" and row.get("partition", "calibration") != "calibration":
        return False
    return (
        row["predicted"] != ""
        and float(row["predicted"]) > 0.0
        and float(row["observed"]) > 0.0
    )


def analyze(outputs: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    aligned = {
        name: {
            (row["family"], row["observation_id"], row["target"]): row for row in rows
        }
        for name, rows in outputs.items()
    }
    order = [
        key
        for key in aligned["baseline"]
        if all(key in rows and fit_row(rows[key]) for rows in aligned.values())
    ]
    base = np.asarray([residual(aligned["baseline"][key]) for key in order])
    groups: dict[str, dict[tuple[str, int, str], list[tuple[str, str, str]]]] = {}
    for key in order:
        row = aligned["baseline"][key]
        group = (str(row["source"]), int(row["temperature_C"]), str(row["target"]))
        groups.setdefault(str(key[0]), {}).setdefault(group, []).append(key)
    within_family = {
        key: 1.0 / (len(family_groups) * len(members))
        for family_groups in groups.values()
        for members in family_groups.values()
        for key in members
    }
    scales = {
        family: math.sqrt(
            math.fsum(
                within_family[key] * residual(aligned["baseline"][key]) ** 2
                for key in order
                if key[0] == family
            )
        )
        for family in groups
    }
    counts = {family: sum(key[0] == family for key in order) for family in scales}
    weights = np.asarray(
        [math.sqrt(within_family[key] / len(scales)) / scales[key[0]] for key in order]
    )
    columns = []
    for reaction in REACTIONS:
        plus = np.asarray([residual(aligned[f"{reaction}-plus"][key]) for key in order])
        minus = np.asarray(
            [residual(aligned[f"{reaction}-minus"][key]) for key in order]
        )
        columns.append(weights * (plus - minus) / (2.0 * STEP_KJ_MOL))
    jacobian = np.column_stack(columns)
    _, singular_values, vt = np.linalg.svd(jacobian, full_matrices=False)
    rank = int(
        np.sum(
            singular_values
            > max(jacobian.shape) * np.finfo(float).eps * singular_values[0]
        )
    )
    directions = vt[: min(2, rank)].T
    reduced = jacobian @ directions
    fit = lsq_linear(reduced, -(weights * base), bounds=(-5.0, 5.0))
    unbounded = np.linalg.lstsq(reduced, -(weights * base), rcond=None)[0]
    shifts = directions @ fit.x
    return {
        "row_count": len(order),
        "excluded_row_count": len(aligned["baseline"]) - len(order),
        "family_scales": scales,
        "family_counts": counts,
        "temperature_counts": {
            family: sorted(
                {
                    int(aligned["baseline"][k]["temperature_C"])
                    for k in order
                    if k[0] == family
                }
            )
            for family in scales
        },
        "common_targets": [list(key) for key in order],
        "target_weights": weights.tolist(),
        "column_norms_per_kj_mol": dict(
            zip(REACTIONS, np.linalg.norm(jacobian, axis=0).tolist(), strict=True)
        ),
        "singular_values": singular_values.tolist(),
        "numerical_rank": rank,
        "retained_direction_count": directions.shape[1],
        "directions": directions.T.tolist(),
        "direction_coordinates_kj_mol": fit.x.tolist(),
        "unbounded_direction_coordinates_kj_mol": unbounded.tolist(),
        "bounds_active": bool(np.any(np.abs(fit.x) > 5.0 - 1e-6)),
        "candidate_shifts_kj_mol": {
            reaction: float(value)
            for reaction, value in zip(REACTIONS, shifts, strict=True)
        },
        "baseline_weighted_norm": float(np.linalg.norm(weights * base)),
        "linear_candidate_weighted_norm": float(
            np.linalg.norm(weights * base + jacobian @ shifts)
        ),
        "weighting": "equal family weight; equal source/temperature/species groups within each family; equal rows within groups; family-scaled by the correspondingly weighted sparse baseline RMS; Xu 2011 pressure and non-calibration heat rows excluded from the objective",
    }


def run_screen(workers: int, budget_s: float) -> None:
    affinity = quarter_cpu_affinity()
    workers = min(workers, len(affinity), 3)
    phases = make_pivot_phases()
    scenarios = [("baseline", {})]
    for reaction in REACTIONS:
        scenarios.extend(
            (
                (f"{reaction}-minus", {reaction: -STEP_KJ_MOL}),
                (f"{reaction}-plus", {reaction: STEP_KJ_MOL}),
            )
        )
    outputs: dict[str, list[dict[str, object]]] = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(evaluate_scenario, (name, shifts, phases, budget_s)): name
            for name, shifts in scenarios
        }
        for future in as_completed(futures):
            name, rows = future.result()
            outputs[name] = rows
            print(f"screen: {name} complete", flush=True)
    ordered_rows = [row for name, _ in scenarios for row in outputs[name]]
    write_csv(RESULTS / "screen-targets.csv", ordered_rows)
    analysis = analyze(outputs)
    analysis.update(
        {
            "scenarios": len(scenarios),
            "workers": workers,
            "cpu_affinity": affinity,
            **provenance(),
            "pivot_temperature_k": PIVOT_K,
            "central_step_kj_mol": STEP_KJ_MOL,
            "holdout_pressure_sources": list(HOLDOUT_PRESSURE_SOURCES),
        }
    )
    write_json(RESULTS / "screen-receipt.json", analysis)
    print(json.dumps(analysis, indent=2))


def run_candidate(budget_s: float) -> None:
    """Exact sparse check of the bounded proposal and, as the single permitted
    recenter, of the unbounded direction solution; the lower exact weighted
    norm becomes the candidate for the full replay."""
    receipt = json.loads((RESULTS / "screen-receipt.json").read_text(encoding="utf-8"))
    directions = np.asarray(receipt["directions"]).T
    proposals = {
        "bounded": receipt["candidate_shifts_kj_mol"],
        "unbounded": dict(
            zip(
                REACTIONS,
                (
                    directions
                    @ np.asarray(receipt["unbounded_direction_coordinates_kj_mol"])
                ).tolist(),
                strict=True,
            )
        ),
    }
    exact = {
        name: _candidate_receipt(name, shifts, receipt, budget_s)
        for name, shifts in proposals.items()
    }
    chosen = min(exact, key=lambda name: exact[name]["exact_weighted_norm"])
    result = {
        **exact[chosen],
        "proposal": chosen,
        "recenter_used": chosen == "unbounded",
        "alternatives": {
            n: {
                "shifts_kj_mol": proposals[n],
                "exact_weighted_norm": exact[n]["exact_weighted_norm"],
            }
            for n in exact
        },
    }
    write_json(RESULTS / "candidate-receipt.json", result)
    print(json.dumps(result, indent=2))


def _candidate_receipt(
    name: str, shifts: dict[str, float], receipt: dict[str, object], budget_s: float
) -> dict[str, object]:
    _, rows = evaluate_scenario(
        (f"candidate-{name}", shifts, make_pivot_phases(), budget_s)
    )
    write_csv(RESULTS / f"candidate-{name}-targets.csv", rows)
    screen = {}
    for row in read_csv(RESULTS / "screen-targets.csv"):
        screen.setdefault(row["scenario"], {})[
            (row["family"], row["observation_id"], row["target"])
        ] = row
    candidate = {
        (row["family"], row["observation_id"], row["target"]): row for row in rows
    }
    common = [tuple(key) for key in receipt["common_targets"]]
    if any(candidate[key]["predicted"] == "" for key in common):
        raise RuntimeError("candidate lost a screen-common target")
    weight_by_key = dict(
        zip(common, map(float, receipt["target_weights"]), strict=True)
    )
    weighted = np.asarray(
        [residual(candidate[key]) * weight_by_key[key] for key in common]
    )
    family_metrics = {}
    for family in ("pressure", "speciation", "heat"):
        values = [residual(candidate[key]) for key in common if key[0] == family]
        family_metrics[family] = {
            "count": len(values),
            "rmse": math.sqrt(statistics.fmean(value * value for value in values)),
            "bias": statistics.fmean(values),
        }
    return {
        "candidate_shifts_kj_mol": shifts,
        "common_target_count": len(common),
        "exact_weighted_norm": float(np.linalg.norm(weighted)),
        "linear_weighted_norm": receipt["linear_candidate_weighted_norm"],
        "baseline_weighted_norm": receipt["baseline_weighted_norm"],
        "local_model_improved_exact_objective": float(np.linalg.norm(weighted))
        < float(receipt["baseline_weighted_norm"]),
        "family_metrics": family_metrics,
        **provenance(),
    }


# --- full replay -----------------------------------------------------------------


def full_group(
    task: tuple[str, str, tuple[int, ...], dict[str, float], float],
) -> tuple[str, list[dict[str, object]]]:
    group, family, temperatures, shifts, budget_s = task
    model = epcsaft.Mixture(load_parameters())
    reactions = shifted_reactions(shifts)
    baseline = baseline_lookup()
    rows: list[dict[str, object]] = []
    extra = {"partition": ""}
    anchors: list[Anchor] = []
    if family in ("pressure", "speciation"):
        catalog = (
            pressure_catalog(True) if family == "pressure" else speciation_catalog()
        )
        states = sorted(
            (
                row
                for row in catalog
                if round(float(row["temperature_c"])) in temperatures
            ),
            key=lambda row: (float(row["temperature_c"]), float(row["loading"])),
        )
        for state in states:
            if round(float(state["temperature_c"])) == 40:
                rows.extend(pivot_rows(state, baseline, extra))
                continue
            record = evaluate_state(
                model,
                state["request"],
                reactions,
                f"full-{state['observation_id']}-candidate",
                anchors if family == "pressure" else [],
                None,
                budget_s,
            )
            rows.extend(target_rows(state, record, extra))
            if family == "pressure" and record["status"] == "evaluated":
                anchors.append(anchor_from(record))
        return group, rows
    thermochemistry, _ = build_thermochemistry(model, pressure_templates(), reactions)
    (temperature_c,) = temperatures
    anchors = cached_anchors({80, 100, 120} - {temperature_c})
    observations = sorted(
        (
            row
            for row in read_csv(HEAT_OBSERVATIONS)
            if round(float(row["temperature_C"])) == temperature_c
            and row["regression_eligible"] == "true"
        ),
        key=lambda row: float(row["co2_loading_mol_per_mol_mea"]),
    )
    enthalpies, _, failures = solve_heat_endpoints(
        model,
        reactions,
        thermochemistry,
        temperature_c,
        heat_endpoints(observations, temperature_c),
        anchors,
        budget_s,
    )
    for row in observations:
        prior = float(row["previous_loading_mol_per_mol_mea"])
        current = float(row["co2_loading_mol_per_mol_mea"])
        if prior in enthalpies and current in enthalpies:
            predicted = heat_release(
                thermochemistry, model, temperature_c, prior, current, enthalpies
            )
            rows.append(heat_row(row, float(predicted), "evaluated", "", "", {}))
        else:
            code, diagnostic = failures.get(
                current if current not in enthalpies else prior,
                ("missing_endpoint", ""),
            )
            rows.append(heat_row(row, "", "endpoint_failed", code, diagnostic, {}))
    return group, rows


def run_full(
    workers: int,
    budget_s: float,
    summarize_only: bool = False,
    groups: list[str] | None = None,
) -> None:
    candidate = json.loads(
        (RESULTS / "candidate-receipt.json").read_text(encoding="utf-8")
    )
    shifts = candidate["candidate_shifts_kj_mol"]
    if (
        candidate["parameter_sha256"] != sha256(PARAMETERS)
        or candidate["engine_wheel_sha256"] != ENGINE_WHEEL_SHA256
    ):
        raise ValueError("candidate receipt does not match the selected bundle")
    affinity = quarter_cpu_affinity()
    workers = min(workers, len(affinity), 3)
    # Pressure runs as one ascending-temperature task so cross-temperature
    # anchors exist, exactly as in the retained baseline replay.
    tasks = [
        ("pressure-all", "pressure", (40, 60, 80, 100, 120), shifts, budget_s),
        *(
            (f"speciation-{t}", "speciation", (t,), shifts, budget_s)
            for t in (20, 40, 60, 80)
        ),
        *((f"heat-{t}", "heat", (t,), shifts, budget_s) for t in (40, 80, 120)),
    ]
    selected = (
        [] if summarize_only else [t for t in tasks if groups is None or t[0] in groups]
    )
    rows: list[dict[str, object]] = []
    done: set[str] = set()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(full_group, task): task for task in selected}
        for future in as_completed(futures):
            group, group_rows = future.result()
            rows.extend(group_rows)
            done.add(group)
            write_json(
                RUNS / "groups" / f"{group}.json",
                {"group": group, "rows": group_rows, **provenance()},
            )
            print(f"full: {group} complete", flush=True)
    for task in tasks:
        path = RUNS / "groups" / f"{task[0]}.json"
        if task[0] not in done and path.exists():
            cached = json.loads(path.read_text(encoding="utf-8"))
            if (
                cached["parameter_sha256"] == sha256(PARAMETERS)
                and cached["engine_wheel_sha256"] == ENGINE_WHEEL_SHA256
            ):
                rows.extend(cached["rows"])
                done.add(task[0])
    missing_groups = [task[0] for task in tasks if task[0] not in done]
    rows.sort(
        key=lambda row: (
            str(row["family"]),
            float(row["temperature_C"]),
            str(row["observation_id"]),
            str(row["target"]),
        )
    )
    write_csv(RESULTS / "full-validation-targets.csv", rows)
    summary: dict[str, object] = {}

    def metrics(members: list[dict[str, object]]) -> dict[str, object]:
        evaluated = [row for row in members if row["predicted"] != ""]
        positive = [
            row
            for row in evaluated
            if row["family"] == "heat"
            or (float(row["predicted"]) > 0 and float(row["observed"]) > 0)
        ]
        errors = [residual(row) for row in positive]
        return {
            "attempted": len(members),
            "evaluated": len(evaluated),
            "metric_target_count": len(positive),
            "rmse": math.sqrt(statistics.fmean(v * v for v in errors))
            if errors
            else None,
            "bias": statistics.fmean(errors) if errors else None,
            "median_absolute_error": statistics.median(abs(v) for v in errors)
            if errors
            else None,
        }

    for family in ("pressure", "speciation", "heat"):
        members = [row for row in rows if row["family"] == family]
        if family == "pressure":
            summary["pressure_calibration"] = metrics(
                [r for r in members if r["source"] not in HOLDOUT_PRESSURE_SOURCES]
            )
            summary["pressure_holdout"] = {
                "sources": list(HOLDOUT_PRESSURE_SOURCES),
                **metrics(
                    [r for r in members if r["source"] in HOLDOUT_PRESSURE_SOURCES]
                ),
            }
        elif family == "heat":
            summary["heat_by_partition"] = {
                partition: metrics([r for r in members if r["partition"] == partition])
                for partition in sorted({str(r["partition"]) for r in members})
            }
        else:
            summary[family] = metrics(members)
        summary[f"{family}_by_temperature"] = {
            str(t): metrics([r for r in members if int(r["temperature_C"]) == t])
            for t in sorted({int(r["temperature_C"]) for r in members})
        }
    receipt = {
        "candidate_shifts_kj_mol": shifts,
        "workers": workers,
        "cpu_affinity": affinity,
        **provenance(),
        "validation_complete": not missing_groups,
        "missing_groups": missing_groups,
        "summary": summary,
    }
    write_json(RESULTS / "full-validation-receipt.json", receipt)
    print(json.dumps(receipt, indent=2))


# --- parity and benchmark ----------------------------------------------------------


PARITY_PRESSURE_IDS = (
    "vle_obs_0206",  # 80 C
    "vle_obs_0211",  # 80 C
    "vle_obs_0224",  # 120 C low loading
    "vle_obs_0227",  # 120 C
    "vle_obs_0228",  # 120 C, first loading the candidate replay lost
    "vle_obs_0232",  # 120 C
)
PARITY_SPECIATION_IDS = (
    "Bottinger2008_state_030",
    "Bottinger2008_state_059",
    "Bottinger2008_state_067",
)
PARITY_HEAT = ((80, 0.137), (80, 0.375))


def run_parity(budget_s: float) -> list[Anchor]:
    """Stage 1: the baseline scenario must reproduce retained values."""
    model = epcsaft.Mixture(load_parameters())
    reactions = shifted_reactions({})
    baseline = baseline_lookup()
    pressure = {row["observation_id"]: row for row in pressure_catalog(True)}
    speciation = {row["observation_id"]: row for row in speciation_catalog()}
    templates = pressure_templates()
    # 100 C anchors first so 120 C can recover cross-temperature, as the baseline did.
    order = [pressure[k] for k in PARITY_PRESSURE_IDS]
    order.insert(
        2,
        sorted(
            pressure_catalog(True),
            key=lambda r: (
                round(float(r["temperature_c"])) != 100,
                float(r["loading"]),
            ),
        )[0],
    )
    order.sort(key=lambda s: (float(s["temperature_c"]), float(s["loading"])))
    anchors: list[Anchor] = []
    rows: list[dict[str, object]] = []
    for state in order + [speciation[k] for k in PARITY_SPECIATION_IDS]:
        record = evaluate_state(
            model,
            state["request"],
            reactions,
            f"parity-{state['observation_id']}",
            anchors if state["family"] == "pressure" else [],
            None,
            budget_s,
        )
        if state["family"] == "pressure" and record["status"] == "evaluated":
            anchors.append(anchor_from(record))
        for row in target_rows(state, record, {}):
            retained = baseline.get((row["observation_id"], row["target"]))
            row["retained"] = "" if retained is None else retained
            row["relative_difference"] = (
                ""
                if retained is None or row["predicted"] == ""
                else abs(float(row["predicted"]) - retained) / abs(retained)
            )
            rows.append(row)
    thermochemistry, _ = build_thermochemistry(model, templates, reactions)
    retained_states = {
        (
            round(float(r["temperature_C"])),
            float(r["loading_mol_CO2_per_mol_MEA"]),
        ): float(r["total_liquid_enthalpy_j"])
        for r in read_csv(BASELINE_HEAT_STATES)
        if r["status"] == "evaluated"
    }
    for temperature_c, loading in PARITY_HEAT:
        record = evaluate_state(
            model,
            heat_request(temperature_c, loading),
            reactions,
            f"parity-heat-{temperature_c}C-{loading:.6f}",
            anchors,
            thermochemistry,
            budget_s,
        )
        retained = retained_states.get((temperature_c, loading))
        rows.append(
            {
                "family": "heat_endpoint",
                "observation_id": f"{temperature_c}C-{loading}",
                "source": "Kim2007",
                "temperature_C": temperature_c,
                "loading": loading,
                "target": "total_liquid_enthalpy_j",
                "observed": "",
                "predicted": ""
                if record["total_enthalpy_j"] is None
                else record["total_enthalpy_j"],
                "status": record["status"],
                "failure_code": record["failure_code"],
                "failure_diagnostic": record["failure_diagnostic"],
                "attempt_count": record["attempt_count"],
                "wall_s": record["wall_s"],
                "cache_hit": record["cache_hit"],
                "retained": "" if retained is None else retained,
                "relative_difference": ""
                if retained is None or record["total_enthalpy_j"] is None
                else abs(record["total_enthalpy_j"] - retained) / abs(retained),
            }
        )
    write_csv(RESULTS / "parity-targets.csv", rows)
    diffs = [
        float(r["relative_difference"]) for r in rows if r["relative_difference"] != ""
    ]
    receipt = {
        **provenance(thermochemistry),
        "rows": len(rows),
        "evaluated": sum(r["status"] == "evaluated" for r in rows),
        "compared": len(diffs),
        "max_relative_difference": max(diffs) if diffs else None,
        "total_wall_s": math.fsum(float(r["wall_s"]) for r in rows),
        "passed": bool(diffs)
        and max(diffs) < 1e-6
        and all(r["status"] == "evaluated" for r in rows),
    }
    write_json(RESULTS / "parity-receipt.json", receipt)
    print(json.dumps(receipt, indent=2))
    return anchors


def timed_solve(
    model: epcsaft.Mixture, problem: object, active: object | None = None
) -> dict[str, object]:
    clock = perf_counter()
    try:
        result = _solve_in_child(model, problem, 60.0, active)
        status, code, diagnostic = (
            result.status,
            result.failure_code,
            result.failure_diagnostic,
        )
    except Exception as exc:
        return {
            "wall_s": perf_counter() - clock,
            "status": "exception",
            "failure_diagnostic": f"{type(exc).__name__}: {exc}",
        }
    out: dict[str, object] = {
        "wall_s": perf_counter() - clock,
        "status": status,
        "failure_code": code,
        "failure_diagnostic": diagnostic,
        "evidence": {str(n): v for n, v in result.evidence},
        "pressure_pa": next(
            (
                float(r["value"])
                for r in result.rows
                if r["identity"] == "system-pressure" and r["value"] is not None
            ),
            None,
        ),
        "pco2_pa": next(
            (
                float(r["value"])
                for r in result.rows
                if r["identity"] == "co2-partial-pressure" and r["value"] is not None
            ),
            None,
        ),
    }
    if active is not None:
        row = next(
            (r for r in result.rows if r["identity"] == "co2-partial-pressure"), None
        )
        out["jacobian"] = None if row is None else row["jacobian"]
        out["jacobian_status"] = None if row is None else str(row["status"])
    return out


def run_benchmark(anchors: list[Anchor], budget_s: float) -> None:
    """Stage 2: one easy state and one hard 120 C state, matched inputs."""
    clock = perf_counter()
    parameters = load_parameters()
    model = epcsaft.Mixture(parameters)
    construction_s = perf_counter() - clock
    reactions = shifted_reactions({})
    baseline = baseline_lookup()
    pressure = {row["observation_id"]: row for row in pressure_catalog(True)}
    cases: dict[str, object] = {"model_construction_s": construction_s, **provenance()}
    for label, observation_id in (("easy", "vle_obs_0206"), ("hard", "vle_obs_0279")):
        state = pressure[observation_id]
        base = corrected_request(state["request"], reactions)
        temperature_c = round(float(state["temperature_c"]))
        loading = float(state["loading"])
        retained = baseline[(observation_id, "pCO2")] * 1000.0
        variants: dict[str, object] = {
            "observation_id": observation_id,
            "temperature_C": temperature_c,
            "loading": loading,
            "retained_pco2_pa": retained,
        }
        plan = attempt_plan(temperature_c, loading, anchors)
        chosen = {"cold-packet-start": None}
        for kind, anchor in plan:
            if anchor is not None and kind not in chosen:
                chosen[kind] = anchor
        for kind, anchor in chosen.items():
            candidate = copy.deepcopy(base)
            if anchor is not None:
                candidate["pressure"]["initial"] = anchor.pressure_pa
                candidate["pressure"]["starts"] = [anchor.pressure_pa]
            problem = _problem_from_request(candidate, anchor)
            variants[kind] = timed_solve(model, problem)
        # Two pressure starts inside one Engine call versus the cold single start.
        candidate = copy.deepcopy(base)
        p0 = float(candidate["pressure"]["initial"])
        candidate["pressure"]["starts"] = [p0, 1.5 * p0]
        problem = _problem_from_request(candidate)
        variants["two-pressure-starts-one-call"] = timed_solve(model, problem)
        if label == "easy":
            identities = tuple(
                identity
                for identity in baseline_reactions()
                if identity.split(":")[1:2] in (["R2"], ["R4"], ["R5"])
            )
            try:
                active = epcsaft.ActiveParameterSet(parameters, identities)
                problem = _problem_from_request(copy.deepcopy(base))
                variants["cold-with-sensitivities"] = {
                    "identities": list(identities),
                    **timed_solve(model, problem, active),
                }
            except Exception as exc:
                variants["cold-with-sensitivities"] = {
                    "status": "unsupported",
                    "failure_diagnostic": f"{type(exc).__name__}: {exc}",
                }
        for value in variants.values():
            if isinstance(value, dict) and value.get("pco2_pa") is not None:
                value["relative_difference_to_retained"] = (
                    abs(value["pco2_pa"] - retained) / retained
                )
        cases[label] = variants
    write_json(RESULTS / "benchmark-receipt.json", cases)
    print(json.dumps(cases, indent=2))


def run_sensitivity_check(budget_s: float) -> None:
    """Compare finite-difference R4/R5 screen columns with native Engine sensitivities.

    The chain rule maps typed coefficient derivatives to the constant
    enthalpy-shift coordinate: for R4, d/d(delta h) = (1/(R T_p)) d/da - (1/R) d/db_k;
    for R5, d/d(delta h) = (1/(R ln 10)) d/da_k - (1/(R T_p ln 10)) d/db, with
    delta h in J/mol.  Only pressure and speciation rows are compared: the heat
    rows also depend on the reference thermochemistry, whose derivative with
    respect to the shift is not exposed by the Engine.
    """
    screen = {}
    for row in read_csv(RESULTS / "screen-targets.csv"):
        screen.setdefault(row["scenario"], {})[
            (row["observation_id"], row["target"])
        ] = row
    parameters = load_parameters()
    model = epcsaft.Mixture(parameters)
    reactions = shifted_reactions({})
    identities = {
        "R4": ("reaction:R4:correlation:a", "reaction:R4:correlation:b_k"),
        "R5": ("reaction:R5:correlation:a_k", "reaction:R5:correlation:b"),
    }
    chain = {
        "R4": (1000.0 / (R * PIVOT_K), -1000.0 / R),
        "R5": (1000.0 / (R * math.log(10.0)), -1000.0 / (R * PIVOT_K * math.log(10.0))),
    }
    active = epcsaft.ActiveParameterSet(parameters, identities["R4"] + identities["R5"])
    rows: list[dict[str, object]] = []
    anchors: list[Anchor] = []
    for state in sorted(
        selected_catalog(),
        key=lambda s: (
            s["family"] != "pressure",
            float(s["temperature_c"]),
            float(s["loading"]),
        ),
    ):
        if round(float(state["temperature_c"])) == 40:
            continue
        # Warm start from the cached baseline solution of the same state.
        cached = evaluate_state(
            model,
            state["request"],
            reactions,
            f"{state['observation_id']}-baseline",
            anchors if state["family"] == "pressure" else [],
            None,
            budget_s,
        )
        if cached["status"] != "evaluated":
            continue
        warm = anchor_from(cached)
        if state["family"] == "pressure":
            anchors.append(warm)
        request = corrected_request(state["request"], reactions)
        if state["family"] == "pressure":
            request["pressure"]["initial"] = warm.pressure_pa
            request["pressure"]["starts"] = [warm.pressure_pa]
        problem = _problem_from_request(request, warm)
        clock = perf_counter()
        try:
            result = _solve_in_child(model, problem, min(60.0, budget_s), active)
        except Exception as exc:
            rows.append(
                {
                    "observation_id": state["observation_id"],
                    "status": "exception",
                    "diagnostic": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        wall = perf_counter() - clock
        by_identity = {row["identity"]: row for row in result.rows}
        for target in state["targets"]:
            row = by_identity.get(target["prediction_identity"])
            key = (state["observation_id"], target["identity"])
            entry: dict[str, object] = {
                "family": state["family"],
                "observation_id": state["observation_id"],
                "temperature_C": round(float(state["temperature_c"])),
                "target": target["identity"],
                "status": result.status,
                "jacobian_status": None if row is None else str(row["status"]),
                "wall_s": wall,
            }
            if (
                result.status == "evaluated"
                and row is not None
                and row["jacobian"] is not None
                and float(row["value"]) > 0
            ):
                jac = [float(v) for v in row["jacobian"]]
                for reaction, (ca, cb) in chain.items():
                    offset = 0 if reaction == "R4" else 2
                    native = (ca * jac[offset] + cb * jac[offset + 1]) / (
                        float(row["value"]) * math.log(10.0)
                    )
                    plus, minus = (
                        screen[f"{reaction}-plus"].get(key),
                        screen[f"{reaction}-minus"].get(key),
                    )
                    fd = None
                    if (
                        plus
                        and minus
                        and plus["predicted"] != ""
                        and minus["predicted"] != ""
                    ):
                        fd = (
                            math.log10(
                                float(plus["predicted"]) / float(plus["observed"])
                            )
                            - math.log10(
                                float(minus["predicted"]) / float(minus["observed"])
                            )
                        ) / (2.0 * STEP_KJ_MOL)
                    entry[f"{reaction}_native_dlog10_per_kj_mol"] = native
                    entry[f"{reaction}_finite_difference_dlog10_per_kj_mol"] = fd
                    entry[f"{reaction}_relative_deviation"] = (
                        None if fd in (None, 0.0) else abs(native - fd) / abs(fd)
                    )
            rows.append(entry)
    write_csv(RESULTS / "sensitivity-check.csv", rows)
    deviations = {
        reaction: [
            r[f"{reaction}_relative_deviation"]
            for r in rows
            if r.get(f"{reaction}_relative_deviation") is not None
        ]
        for reaction in chain
    }
    receipt = {
        **provenance(),
        "compared_rows": {k: len(v) for k, v in deviations.items()},
        "max_relative_deviation": {
            k: (max(v) if v else None) for k, v in deviations.items()
        },
        "median_relative_deviation": {
            k: (statistics.median(v) if v else None) for k, v in deviations.items()
        },
        "central_difference_step_kj_mol": STEP_KJ_MOL,
        "missing_for_production_use": [
            "R1-R3 correlation coefficients are not parameter specs in the selected parameter document, so ActiveParameterSet cannot address them; declare reaction:R2:correlation:{a,b_k} (and R1/R3 if ever opened) as typed parameters to expose their sensitivities",
            "EquilibriumEnthalpy carries no active-parameter Jacobian; heat rows need d(total enthalpy)/d(theta) at fixed reference plus the reference-term derivative sum_i n_i dh_i^ref/d(theta), which MEA can supply analytically from the anchored construction once the Engine exposes the first term",
        ],
    }
    write_json(RESULTS / "sensitivity-check-receipt.json", receipt)
    print(json.dumps(receipt, indent=2))


HISTORY = ANALYSIS / "results/parameter-record-history.csv"
HOLDOUT_LEDGER = ANALYSIS / "results/holdout-evaluations.csv"


def paired_metrics(rows_a: dict, rows_b: dict, keys: list) -> dict[str, float | int]:
    errors_a = [residual(rows_a[k]) for k in keys]
    errors_b = [residual(rows_b[k]) for k in keys]
    rms = lambda v: math.sqrt(statistics.fmean(x * x for x in v)) if v else None  # noqa: E731
    return {
        "count": len(keys),
        "baseline_rmse": rms(errors_a),
        "candidate_rmse": rms(errors_b),
        "baseline_bias": statistics.fmean(errors_a) if errors_a else None,
        "candidate_bias": statistics.fmean(errors_b) if errors_b else None,
    }


def run_adopt() -> None:
    """Compare the replayed candidate with the incumbent on comparable cohorts,
    apply the adoption rules, and on acceptance write the new parameter record."""
    require_current_baseline()
    full = json.loads(
        (RESULTS / "full-validation-receipt.json").read_text(encoding="utf-8")
    )
    if not full["validation_complete"]:
        raise RuntimeError(f"full replay incomplete: {full['missing_groups']}")
    candidate = json.loads(
        (RESULTS / "candidate-receipt.json").read_text(encoding="utf-8")
    )
    shifts = candidate["candidate_shifts_kj_mol"]
    cand = {
        (r["family"], r["observation_id"], r["target"]): r
        for r in read_csv(RESULTS / "full-validation-targets.csv")
    }
    base_rows = {}
    for r in read_csv(BASELINE_RESIDUALS):
        base_rows[(r["family"], r["observation_id"], r["target"])] = {
            "family": r["family"],
            "source": r["source"],
            "observed": r["observed"],
            "predicted": r["predicted"],
        }
    for r in read_csv(
        ANALYSIS / "results/calorimetry/current-selected-direct-enthalpy-comparison.csv"
    ):
        base_rows[("heat", r["record_id"], "heat_release")] = {
            "family": "heat",
            "source": r["source"],
            "observed": r["observed_heat_release_kj_per_mol_CO2"],
            "predicted": r["predicted_heat_release_kj_per_mol_CO2"],
            "partition": r["campaign_partition"],
        }

    def usable(row):
        return (
            row["predicted"] != ""
            and float(row["observed"]) > 0
            and (row["family"] == "heat" or float(row["predicted"]) > 0)
        )

    common = [
        k for k in cand if k in base_rows and usable(cand[k]) and usable(base_rows[k])
    ]
    cohorts = {
        "pressure_calibration": [
            k
            for k in common
            if k[0] == "pressure" and cand[k]["source"] not in HOLDOUT_PRESSURE_SOURCES
        ],
        "pressure_holdout_xu2011": [
            k
            for k in common
            if k[0] == "pressure" and cand[k]["source"] in HOLDOUT_PRESSURE_SOURCES
        ],
        "speciation": [k for k in common if k[0] == "speciation"],
        "heat_calibration_40_80": [
            k
            for k in common
            if k[0] == "heat" and cand[k]["partition"] == "calibration"
        ],
        "heat_holdout_120": [
            k
            for k in common
            if k[0] == "heat" and cand[k]["partition"] == "temperature_holdout"
        ],
        "heat_model_selection_kim2014": [
            k
            for k in common
            if k[0] == "heat" and cand[k]["partition"] == "model_selection_comparison"
        ],
    }
    comparison = {
        name: paired_metrics(base_rows, cand, keys) for name, keys in cohorts.items()
    }
    evaluability = {
        "pressure": {
            "baseline": sum(
                1 for k in base_rows if k[0] == "pressure" and usable(base_rows[k])
            ),
            "candidate": sum(1 for k in cand if k[0] == "pressure" and usable(cand[k])),
        },
        "speciation": {
            "baseline": sum(
                1 for k in base_rows if k[0] == "speciation" and usable(base_rows[k])
            ),
            "candidate": sum(
                1 for k in cand if k[0] == "speciation" and usable(cand[k])
            ),
        },
        "heat": {
            "baseline": sum(
                1 for k in base_rows if k[0] == "heat" and usable(base_rows[k])
            ),
            "candidate": sum(1 for k in cand if k[0] == "heat" and usable(cand[k])),
        },
    }
    held_out = ("pressure_holdout_xu2011", "heat_holdout_120")
    improved_held_out = [
        n
        for n in held_out
        if comparison[n]["count"]
        and comparison[n]["candidate_rmse"] < comparison[n]["baseline_rmse"]
    ]
    degraded = [
        n
        for n, m in comparison.items()
        if m["count"] and m["candidate_rmse"] > m["baseline_rmse"]
    ]
    rules = {
        "evaluability_not_below_incumbent": all(
            v["candidate"] >= v["baseline"] for v in evaluability.values()
        ),
        "held_out_blocks_improved": improved_held_out,
        "no_cohort_degraded": not degraded,
        "degraded_cohorts": degraded,
        "interior_solution": candidate["proposal"] == "unbounded",
    }
    accepted = (
        rules["evaluability_not_below_incumbent"]
        and len(improved_held_out) == len(held_out)
        and rules["no_cohort_degraded"]
        and rules["interior_solution"]
    )
    decision = {
        "decision": "adopted_as_exploratory_incumbent" if accepted else "not_adopted",
        "candidate_shifts_kj_mol": shifts,
        "comparison": comparison,
        "evaluability": evaluability,
        "rules": rules,
        "incumbent_parameter_sha256": sha256(PARAMETERS),
        **provenance(),
    }
    ledger_rows = [
        {
            "date": "2026-09-03",
            "candidate": "reaction-temperature-fit unbounded",
            "holdout_block": n,
            "baseline_rmse": comparison[n]["baseline_rmse"],
            "candidate_rmse": comparison[n]["candidate_rmse"],
            "count": comparison[n]["count"],
            "decision": decision["decision"],
        }
        for n in held_out
    ]
    _append_csv(HOLDOUT_LEDGER, ledger_rows)
    if accepted:
        new_sha = write_adopted_parameters(shifts, candidate)
        decision["adopted_parameter_sha256"] = new_sha
    _append_csv(
        HISTORY,
        [
            {
                "date": "2026-09-03",
                "incumbent_sha256": sha256(PARAMETERS)
                if not accepted
                else decision["incumbent_parameter_sha256"],
                "candidate": "reaction-temperature-fit unbounded R2/R4/R5 enthalpy shifts",
                "candidate_sha256": decision.get("adopted_parameter_sha256", ""),
                "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
                "decision": decision["decision"],
                "reason": "; ".join(
                    f"{n}: {m['baseline_rmse']:.4f}->{m['candidate_rmse']:.4f} (n={m['count']})"
                    for n, m in comparison.items()
                    if m["count"]
                ),
                "evidence": "analyses/mea_parameter_bundle/results/reaction-temperature-fit/adoption-receipt.json",
            }
        ],
    )
    write_json(RESULTS / "adoption-receipt.json", decision)
    print(json.dumps(decision, indent=2))


def _append_csv(path: Path, rows: list[dict[str, object]]) -> None:
    existing = read_csv(path) if path.exists() else []
    write_csv(path, existing + rows)


def write_adopted_parameters(
    shifts: dict[str, float], candidate: dict[str, object]
) -> str:
    """Write the shifted R2/R4/R5 correlations into a new parameter document."""
    document = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    values = shifted_reactions(shifts)
    receipt_sha = "sha256:" + sha256(RESULTS / "candidate-receipt.json")
    source = {
        "domain_id": "mea-diagnostic-293-15-to-393-15-k",
        "locator": "analyses/mea_parameter_bundle/results/reaction-temperature-fit/candidate-receipt.json:proposal=unbounded; constant reaction-enthalpy shift preserving ln K at 313.15 K",
        "source_id": "mea-reaction-temperature-fit-2026-09-03",
    }
    units = {
        "a": "dimensionless",
        "b_k": "kelvin",
        "c": "dimensionless",
        "d_per_k": "1 / kelvin",
        "a_k": "kelvin",
        "b": "dimensionless",
        "c_per_k": "1 / kelvin",
    }
    template = next(
        r for r in document["reaction_correlations"] if r["reaction_id"] == "R4"
    )
    kept = [
        r
        for r in document["reaction_correlations"]
        if r["reaction_id"] not in ("R2", "R4", "R5")
    ]
    for reaction_id, names, kind in (
        (
            "R2",
            ("a", "b_k", "c", "d_per_k"),
            "ln-k-a-plus-b-over-t-plus-c-ln-t-plus-d-t",
        ),
        ("R4", ("a", "b_k"), "ln-k-a-plus-b-over-t"),
        ("R5", ("a_k", "b", "c_per_k"), "negative-log10-temperature-polynomial"),
    ):
        old = next(
            (
                r
                for r in document["reaction_correlations"]
                if r["reaction_id"] == reaction_id
            ),
            None,
        )
        entry = copy.deepcopy(old or template)
        entry.update(
            {
                "reaction_id": reaction_id,
                "kind": kind,
                "source": source,
                "source_sha256": receipt_sha,
                "qualification": "candidate_extrapolation",
            }
        )
        domains = {
            c["name"]: c.get("optimizer_domain", {"lower": -1.0e6, "upper": 1.0e6})
            for c in (old or {}).get("coefficients", [])
        }
        entry["coefficients"] = [
            {
                "identity": f"reaction:{reaction_id}:correlation:{n}",
                "name": n,
                "optimizer_domain": domains.get(n, {"lower": -1.0e6, "upper": 1.0e6}),
                "value": {
                    "magnitude": values[f"reaction:{reaction_id}:correlation:{n}"],
                    "unit": units[n],
                },
            }
            for n in names
        ]
        if reaction_id == "R2":
            entry["source"] = {
                **source,
                "locator": source["locator"]
                + "; R2 base: Austgen 1991 converted to the common aqueous-molality standard state (ln K offset +4.0165349923); supersedes the source-contract R2 for this record",
            }
        kept.append(entry)
    document["reaction_correlations"] = sorted(kept, key=lambda r: r["reaction_id"])
    if all(item["source_id"] != source["source_id"] for item in document["sources"]):
        document["sources"].append(
            {
                "citation": "MEA-Thermodynamics reaction-temperature fit, 2026-09-03 (analyses/mea_parameter_bundle/results/reaction-temperature-fit)",
                "source_id": source["source_id"],
                "use_basis": "constant R2/R4/R5 reaction-enthalpy shifts fitted to pressure, speciation, and 40/80 C calorimetry with Xu 2011 pressure and 120 C calorimetry held out; ln K preserved at 313.15 K",
            }
        )
    document["document_version"] = int(document.get("document_version", 1)) + 1
    PARAMETERS.write_text(
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    for identity, value in _selected_reactions().items():
        assert math.isclose(value, values[identity], rel_tol=0, abs_tol=1e-12), identity
    return sha256(PARAMETERS)


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--parity", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--sensitivity-check", action="store_true")
    parser.add_argument("--adopt", action="store_true")
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--summarize-partial", action="store_true")
    parser.add_argument("--groups", nargs="+")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--budget-s",
        type=float,
        default=900.0,
        help="per-state wall budget across attempts",
    )
    args = parser.parse_args()
    quarter_cpu_affinity()
    verify_wheel()
    if args.self_check:
        self_check()
    elif args.parity or args.benchmark:
        quarter_cpu_affinity()
        anchors = run_parity(args.budget_s)
        if args.benchmark:
            run_benchmark(anchors, args.budget_s)
    elif args.adopt:
        run_adopt()
    elif args.sensitivity_check:
        quarter_cpu_affinity()
        run_sensitivity_check(args.budget_s)
    elif args.summarize_partial:
        run_full(args.workers, args.budget_s, summarize_only=True)
    elif args.full:
        run_full(args.workers, args.budget_s, groups=args.groups)
    elif args.candidate:
        run_candidate(args.budget_s)
    else:
        run_screen(args.workers, args.budget_s)


if __name__ == "__main__":
    bounded_main(main)
