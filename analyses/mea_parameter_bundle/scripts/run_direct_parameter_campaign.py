"""Evaluate bounded MEA parameter candidates with coupled Engine solves."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
import statistics
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

import epcsaft
from shared_evaluation import (
    CANONICAL_VLE,
    ENGINE_WHEEL_SHA256,
    STATE_PACKET,
    STATE_PACKET_SHA256,
    load_state_packet,
    parameter_fingerprint,
    parameter_mapping,
    parameter_values,
    reaction_values,
    sha256,
    evaluate_state,
    anchor_from,
    verify_wheel,
    with_parameter_values,
)

ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/best-in-slot-campaign"
BASELINE = ANALYSIS / "results/selected-current-best-parameters.json"
BASELINE_RESIDUALS = ANALYSIS / "results/current-best-fit-residuals.csv"
COORDINATES = {
    "co2_epsilon": "component/carbon-dioxide/dispersion_energy_over_k",
    "r4_a": "reaction:R4:correlation:a",
    "r4_b": "reaction:R4:correlation:b_k",
    "r5_a": "reaction:R5:correlation:a_k",
    "hco3_fsolv": "component/bicarbonate-anion/solvation_factor",
    "hco3_born": "component/bicarbonate-anion/born_diameter",
}
BOUNDS = {
    "co2_epsilon": (160.0, 190.0),
    "r4_a": (1.0, 3.5),
    "r4_b": (-1900.0, -1300.0),
    "r5_a": (2400.0, 3000.0),
    "hco3_fsolv": (0.5, 1.5),
    "hco3_born": (2.5, 3.5),
}


def quarter_cpu_affinity() -> tuple[int, ...]:
    """Restrict this process and inherited workers to one logical CPU."""
    available = sorted(os.sched_getaffinity(0))
    limit = 1
    selected = tuple(available[:limit])
    os.sched_setaffinity(0, selected)
    return selected


@lru_cache(maxsize=1)
def origins() -> dict[str, float]:
    values = parameter_values(parameter_mapping(BASELINE))
    return {name: values[identity] for name, identity in COORDINATES.items()}


def component_values(mapping: dict[str, float]) -> dict[str, float]:
    return {
        COORDINATES[name]: value
        for name, value in mapping.items()
        if not name.startswith(("r4_", "r5_"))
    }


def scenario_reactions(values: dict[str, float]) -> dict[str, float]:
    reactions = reaction_values(parameter_mapping(BASELINE))
    reactions.update(
        {
            "reaction:R4:correlation:a": values.get("r4_a", origins()["r4_a"]),
            "reaction:R4:correlation:b_k": values.get("r4_b", origins()["r4_b"]),
            "reaction:R5:correlation:a_k": values.get("r5_a", origins()["r5_a"]),
        }
    )
    return reactions


def load_packet() -> dict[str, object]:
    return load_state_packet(STATE_PACKET)


def pressure_templates(
    packet: dict[str, object],
) -> dict[int, list[tuple[float, dict[str, object]]]]:
    templates: dict[int, list[tuple[float, dict[str, object]]]] = defaultdict(list)
    for observation in packet["observations"]:
        if len(observation["targets"]) != 1:
            continue
        request = observation["request"]
        temperature_c = round(float(request["temperature"]["value"]) - 273.15)
        loading = float(request["reaction_system"]["feed_amounts_mol"][0])
        templates[temperature_c].append((loading, request))
    return templates


def pressure_catalog(full: bool) -> list[dict[str, object]]:
    packet = load_packet()
    templates = pressure_templates(packet)
    with CANONICAL_VLE.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream) if row["active_view_member"] == "yes"
        ]
    if not full:
        selected = []
        by_temperature: dict[int, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            by_temperature[round(float(row["temperature_canonical_C"]))].append(row)
        for temperature_c, members in sorted(by_temperature.items()):
            ordered = sorted(members, key=lambda row: float(row["CO2_loading"]))
            indices = {round(index * (len(ordered) - 1) / 4) for index in range(5)}
            selected.extend(ordered[index] for index in sorted(indices))
        rows = selected
    catalog = []
    for row in rows:
        temperature_c = round(float(row["temperature_canonical_C"]))
        loading = float(row["CO2_loading"])
        _, template = min(
            templates[temperature_c], key=lambda item: abs(item[0] - loading)
        )
        request = copy.deepcopy(template)
        system = request["reaction_system"]
        system["feed_amounts_mol"][0] = loading
        system["conserved_totals"] = [
            math.fsum(
                c * n for c, n in zip(balance, system["feed_amounts_mol"], strict=True)
            )
            for balance in system["balance_matrix"]
        ]
        catalog.append(
            {
                "family": "pressure",
                "observation_id": row["observation_id"],
                "source": row["source_key"],
                "temperature_c": temperature_c,
                "loading": loading,
                "request": request,
                "targets": [
                    {
                        "identity": "pCO2",
                        "prediction_identity": "co2-partial-pressure",
                        "observed": float(row["CO2_pressure"]),
                        "unit_scale": 0.001,
                    }
                ],
            }
        )
    return catalog


def speciation_catalog() -> list[dict[str, object]]:
    catalog = []
    for observation in load_packet()["observations"]:
        if len(observation["targets"]) == 1:
            continue
        request = observation["request"]
        catalog.append(
            {
                "family": "speciation",
                "observation_id": observation["identity"],
                "source": observation["targets"][0]["source_identity"],
                "temperature_c": float(request["temperature"]["value"]) - 273.15,
                "loading": float(request["reaction_system"]["feed_amounts_mol"][0]),
                "request": request,
                "targets": [
                    {
                        "identity": target["identity"].split("::")[-1],
                        "prediction_identity": target["prediction_identity"],
                        "observed": float(target["observed"]),
                        "unit_scale": 1.0,
                    }
                    for target in observation["targets"]
                ],
            }
        )
    return catalog


def evaluate_scenario(
    task: tuple[str, dict[str, float], bool],
) -> tuple[str, dict[str, float], list[dict[str, object]]]:
    scenario, values, full = task
    mapping = with_parameter_values(parameter_mapping(BASELINE), component_values(values))
    fingerprint = parameter_fingerprint(mapping)
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    rows: list[dict[str, object]] = []
    anchors = []
    reactions = scenario_reactions(values)
    for state in [*pressure_catalog(full), *speciation_catalog()]:
        record = evaluate_state(
            model,
            state["request"],
            reactions,
            f"{state['observation_id']}-{scenario}",
            anchors,
            budget_s=45,
            model_fingerprint=fingerprint,
        )
        status = record["status"]
        code, diagnostic = record["failure_code"], record["failure_diagnostic"]
        predictions = record["predictions"]
        if status == "evaluated" and state["family"] == "pressure":
            anchors.append(anchor_from(record))
        for target in state["targets"]:
            predicted = predictions.get(target["prediction_identity"])
            scale = float(target["unit_scale"])
            rows.append(
                {
                    "scenario": scenario,
                    "family": state["family"],
                    "observation_id": state["observation_id"],
                    "source": state["source"],
                    "temperature_C": state["temperature_c"],
                    "loading_mol_CO2_per_mol_MEA": state["loading"],
                    "target": target["identity"],
                    "observed": float(target["observed"]),
                    "predicted": "" if predicted is None else predicted * scale,
                    "status": status,
                    "failure_code": code,
                    "failure_diagnostic": diagnostic,
                    "parameter_fingerprint": fingerprint,
                    "cache_hit": record["cache_hit"],
                    **values,
                }
            )
    return scenario, values, rows


def summarize(
    scenario: str, values: dict[str, float], rows: list[dict[str, object]]
) -> dict[str, object]:
    result: dict[str, object] = {"scenario": scenario, **values}
    for family in ("pressure", "speciation"):
        members = [row for row in rows if row["family"] == family]
        evaluated = [row for row in members if row["predicted"] != ""]
        logs = [
            math.log10(float(row["predicted"]) / float(row["observed"]))
            for row in evaluated
            if float(row["predicted"]) > 0 and float(row["observed"]) > 0
        ]
        result[f"{family}_attempted"] = len(members)
        result[f"{family}_evaluated"] = len(evaluated)
        result[f"{family}_coverage"] = (
            len(evaluated) / len(members) if members else None
        )
        result[f"{family}_log10_rmse"] = (
            math.sqrt(statistics.fmean(x * x for x in logs)) if logs else None
        )
        result[f"{family}_mae"] = (
            statistics.fmean(
                abs(float(row["predicted"]) - float(row["observed"]))
                for row in evaluated
            )
            if evaluated
            else None
        )
        temperature_rmses = []
        for temperature in sorted({float(row["temperature_C"]) for row in evaluated}):
            errors = [
                math.log10(float(row["predicted"]) / float(row["observed"]))
                for row in evaluated
                if float(row["temperature_C"]) == temperature
                and float(row["predicted"]) > 0
                and float(row["observed"]) > 0
            ]
            if errors:
                temperature_rmses.append(
                    math.sqrt(statistics.fmean(x * x for x in errors))
                )
        result[f"{family}_temperature_balanced_log10_rmse"] = (
            math.sqrt(statistics.fmean(x * x for x in temperature_rmses))
            if temperature_rmses
            else None
        )
    for target in ("MEAH+", "MEACOO-", "HCO3-", "MEA", "MEA + MEAH+"):
        members = [
            row for row in rows if row["target"] == target and row["predicted"] != ""
        ]
        if not members:
            continue
        errors = [
            math.log10(float(row["predicted"]) / float(row["observed"]))
            for row in members
            if float(row["predicted"]) > 0 and float(row["observed"]) > 0
        ]
        result[f"{target}_mae"] = statistics.fmean(
            abs(float(row["predicted"]) - float(row["observed"])) for row in members
        )
        result[f"{target}_log10_rmse"] = (
            math.sqrt(statistics.fmean(x * x for x in errors)) if errors else None
        )
    return result


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = tuple(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def scenario_preset(name: str) -> list[tuple[str, dict[str, float]]]:
    """Build one named campaign from compact data and a shared filter."""
    center = origins()
    pivot_temperature = 333.15
    if name == "sensitivity":
        steps = {"co2_epsilon": 0.05 * center["co2_epsilon"], "r4_a": 0.10,
                 "r4_b": 0.05 * abs(center["r4_b"]), "r5_a": 0.03 * center["r5_a"],
                 "hco3_fsolv": 0.10, "hco3_born": 0.10}
        return [("baseline", {})] + [
            (f"{key}-{label}", {key: min(max(center[key] + sign * step, BOUNDS[key][0]), BOUNDS[key][1])})
            for key, step in steps.items()
            for sign, label in ((-1.0, "minus"), (1.0, "plus"))
        ]
    if name in {"r4-pivot", "validation"}:
        scenarios = [("baseline", {})] + [
            (
                f"r4-p{pivot:.2f}-db{shift:+.0f}",
                {"r4_a": center["r4_a"] + pivot - shift / pivot_temperature,
                 "r4_b": center["r4_b"] + shift},
            )
            for pivot in (0.10, 0.20, 0.30, 0.40)
            for shift in (-150.0, 0.0, 150.0)
        ]
        selected = {"r4-p0.10-db+150", "r4-p0.20-db-150", "r4-p0.30-db-150", "r4-p0.40-db-150"}
        return [item for item in scenarios if name == "r4-pivot" or item[0] == "baseline" or item[0] in selected]
    if name in {"refinement", "refinement-validation"}:
        scenarios = [("baseline", {})] + [
            (f"r4-refine-p{pivot:.2f}-db{shift:+.0f}",
             {"r4_a": center["r4_a"] + pivot - shift / pivot_temperature,
              "r4_b": center["r4_b"] + shift})
            for pivot in (0.10, 0.20, 0.30, 0.40) for shift in (-300.0, -350.0)
        ]
        best = {"r4_a": center["r4_a"] + 0.20 + 300.0 / pivot_temperature, "r4_b": center["r4_b"] - 300.0}
        scenarios += [(f"r4-refine-p0.20-db-300-eps{fraction:+.3f}", {**best, "co2_epsilon": center["co2_epsilon"] * (1 + fraction)}) for fraction in (-0.05, -0.025, 0.025, 0.05)]
        selected = {"r4-refine-p0.20-db-350", "r4-refine-p0.20-db-300-eps+0.025", "r4-refine-p0.30-db-300", "r4-refine-p0.40-db-350"}
        return scenarios if name == "refinement" else [item for item in scenarios if item[0] in selected]
    if name in {"local-best", "final-validation"}:
        points = {(0.15, -300.0, 0.025), (0.20, -300.0, 0.025), (0.25, -300.0, 0.025), (0.20, -250.0, 0.025), (0.20, -350.0, 0.025), (0.20, -300.0, 0.015), (0.20, -300.0, 0.035), (0.15, -350.0, 0.025), (0.25, -250.0, 0.025)}
        scenarios = [(f"local-p{pivot:.2f}-db{shift:+.0f}-eps{fraction:+.3f}", {"r4_a": center["r4_a"] + pivot - shift / pivot_temperature, "r4_b": center["r4_b"] + shift, "co2_epsilon": center["co2_epsilon"] * (1 + fraction)}) for pivot, shift, fraction in sorted(points)]
        selected = {"local-p0.20-db-250-eps+0.025", "local-p0.20-db-300-eps+0.035", "local-p0.25-db-250-eps+0.025", "local-p0.15-db-350-eps+0.025"}
        return scenarios if name == "local-best" else [item for item in scenarios if item[0] in selected]
    raise ValueError(f"unknown scenario preset: {name}")


def load_scenarios(path: Path) -> list[tuple[str, dict[str, float]]]:
    values = json.loads(path.read_text(encoding="utf-8"))
    return [(item["scenario"], item["values"]) for item in values]


def run(
    scenarios: list[tuple[str, dict[str, float]]], phase: str, full: bool, workers: int
) -> None:
    assert sha256(STATE_PACKET) == STATE_PACKET_SHA256
    verify_wheel()
    cpu_affinity = quarter_cpu_affinity()
    workers = min(workers, len(cpu_affinity))
    tasks = [(scenario, values, full) for scenario, values in scenarios]
    outputs = []
    with ProcessPoolExecutor(max_workers=min(workers, len(tasks))) as pool:
        futures = {pool.submit(evaluate_scenario, task): task[0] for task in tasks}
        for future in as_completed(futures):
            scenario, values, rows = future.result()
            outputs.append((scenario, values, rows))
            print(f"{phase}: {scenario} complete", flush=True)
    outputs.sort(key=lambda item: item[0])
    result_rows = [row for _, _, rows in outputs for row in rows]
    summaries = [
        summarize(scenario, values, rows) for scenario, values, rows in outputs
    ]
    write_csv(RESULTS / f"{phase}-evaluations.csv", result_rows)
    write_csv(RESULTS / f"{phase}-summary.csv", summaries)
    receipt = {
        "phase": phase,
        "full_pressure_catalog": full,
        "pressure_state_count": len(pressure_catalog(full)),
        "speciation_state_count": len(speciation_catalog()),
        "scenario_count": len(scenarios),
        "workers": min(workers, len(tasks)),
        "cpu_affinity": cpu_affinity,
        "cpu_limit_count": 1,
        "parameter_path": str(BASELINE.relative_to(ANALYSIS)),
        "parameter_sha256": sha256(BASELINE),
        "state_packet_sha256": sha256(STATE_PACKET),
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "method": "Direct coupled Engine reactive equilibrium solve at every sampled state.",
    }
    (RESULTS / f"{phase}-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--scenarios", type=Path)
    parser.add_argument(
        "--preset",
        choices=(
            "sensitivity",
            "r4-pivot",
            "validation",
            "refinement",
            "refinement-validation",
            "local-best",
            "final-validation",
        ),
        default="sensitivity",
    )
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if args.scenarios:
        scenarios = load_scenarios(args.scenarios)
    else:
        scenarios = scenario_preset(args.preset)
    run(scenarios, args.phase, args.full, args.workers)


if __name__ == "__main__":
    from refresh_results import bounded_main

    bounded_main(main)
