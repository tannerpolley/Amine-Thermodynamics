"""Run nested Engine regressions for the live MEA parameter bundle.

The calibration set is a deterministic four-of-five split within each
family/source/temperature group.  Baseline non-evaluable states are excluded
from optimization but remain part of the later full-domain validation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import epcsaft
from epcsaft import equilibrium, regression

from shared_evaluation import corrected_request, verify_wheel


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/best-in-slot-campaign"
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
STATE_PACKET = ANALYSIS / "data/input/state-packet.json"
BASELINE_RESIDUALS = ANALYSIS / "results/current-best-fit-residuals.csv"

COORDINATES = {
    "co2_epsilon": {
        "identity": "component/carbon-dioxide/dispersion_energy_over_k",
        "bounds": [160.0, 190.0],
        "scale": 15.0,
    },
    "r4_a": {
        "identity": "reaction:R4:correlation:a",
        "bounds": [1.0, 3.5],
        "scale": 1.25,
    },
    "r4_b": {
        "identity": "reaction:R4:correlation:b_k",
        "bounds": [-1900.0, -1300.0],
        "scale": 300.0,
    },
    "r5_a": {
        "identity": "reaction:R5:correlation:a_k",
        "bounds": [2400.0, 3000.0],
        "scale": 300.0,
    },
    "hco3_fsolv": {
        "identity": "component/bicarbonate-anion/solvation_factor",
        "bounds": [0.5, 1.5],
        "scale": 0.5,
    },
    "hco3_born": {
        "identity": "component/bicarbonate-anion/born_diameter",
        "bounds": [2.5, 3.5],
        "scale": 0.5,
    },
}

CANDIDATES = {
    "co2-epsilon": ("co2_epsilon",),
    "r4-b": ("r4_b",),
    "co2-epsilon-r4-b": ("co2_epsilon", "r4_b"),
    "co2-epsilon-r4-ab": ("co2_epsilon", "r4_a", "r4_b"),
    "co2-epsilon-r4-ab-r5-a": ("co2_epsilon", "r4_a", "r4_b", "r5_a"),
    "co2-epsilon-r4-ab-hco3-fsolv": (
        "co2_epsilon",
        "r4_a",
        "r4_b",
        "hco3_fsolv",
    ),
    "co2-epsilon-r4-ab-hco3-born": (
        "co2_epsilon",
        "r4_a",
        "r4_b",
        "hco3_born",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric(value: object, unit: str) -> float:
    return float(value.to(unit).magnitude) if hasattr(value, "to") else float(value)


def parameter_origins() -> dict[str, float]:
    parameters = epcsaft.Parameters.from_json(PARAMETERS)
    specs = {spec.identity: spec for spec in parameters.parameter_specs}
    return {
        name: numeric(specs[record["identity"]].value, specs[record["identity"]].unit)
        for name, record in COORDINATES.items()
    }


def baseline_evaluable() -> set[str]:
    with BASELINE_RESIDUALS.open(newline="", encoding="utf-8") as stream:
        return {
            row["observation_id"]
            for row in csv.DictReader(stream)
            if row["predicted"] != ""
        }


def prepared_observations() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    packet = json.loads(STATE_PACKET.read_text(encoding="utf-8"))
    evaluable = baseline_evaluable()
    grouped: dict[tuple[str, str, int], list[tuple[float, dict[str, object]]]] = defaultdict(list)
    excluded: list[dict[str, object]] = []
    for observation in packet["observations"]:
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            corrected_request(observation["request"])
        )
        temperature_k = float(problem.temperature.value.to("kelvin").magnitude)
        loading = float(problem.reaction_system.feed_amounts_mol[0])
        family = "pressure" if len(observation["targets"]) == 1 else "speciation"
        source = str(observation["targets"][0]["source_identity"])
        if observation["identity"] not in evaluable:
            excluded.append(
                {
                    "observation_id": observation["identity"],
                    "family": family,
                    "source": source,
                    "temperature_k": temperature_k,
                    "loading": loading,
                    "reason": "baseline_non_evaluable",
                }
            )
            continue
        item = dict(observation)
        item["request"] = corrected_request(observation["request"])
        grouped[(family, source, round(temperature_k))].append((loading, item))

    prepared: list[dict[str, object]] = []
    split_rows: list[dict[str, object]] = []
    for (family, source, temperature_k), members in sorted(grouped.items()):
        for index, (loading, observation) in enumerate(sorted(members), start=1):
            partition = "holdout" if index % 5 == 0 else "calibration"
            split_rows.append(
                {
                    "observation_id": observation["identity"],
                    "family": family,
                    "source": source,
                    "temperature_k": temperature_k,
                    "loading": loading,
                    "partition": partition,
                }
            )
            if partition == "calibration":
                prepared.append(observation)
    return prepared, [*split_rows, *excluded]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = tuple(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def candidate_fit_mapping(candidate: str, smoke: bool) -> dict[str, object]:
    observations, split_rows = prepared_observations()
    if smoke:
        by_family: dict[str, list[dict[str, object]]] = defaultdict(list)
        for item in observations:
            family = "pressure" if len(item["targets"]) == 1 else "speciation"
            if len(by_family[family]) < 3:
                by_family[family].append(item)
        observations = [*by_family["pressure"], *by_family["speciation"]]
    write_csv(RESULTS / "state-partitions.csv", split_rows)

    origins = parameter_origins()
    names = CANDIDATES[candidate]
    coordinate_records = {}
    origin_values = []
    directional_values = []
    for name in names:
        record = COORDINATES[name]
        origin = origins[name]
        coordinate_records[record["identity"]] = {
            "bounds": record["bounds"],
            "origin": origin,
            "scale": record["scale"],
        }
        origin_values.append(origin)
        if name == "co2_epsilon":
            trial = origin * 1.05
        elif name == "r4_b":
            trial = origin * 1.10
        elif name == "r4_a":
            trial = origin - 0.2
        elif name == "r5_a":
            trial = origin * 1.03
        elif name == "hco3_fsolv":
            trial = origin + 0.10
        else:
            trial = origin + 0.10
        directional_values.append(
            min(max(trial, record["bounds"][0] + 1e-6), record["bounds"][1] - 1e-6)
        )
    identities = [COORDINATES[name]["identity"] for name in names]
    return {
        "schema_version": 2,
        "parameters": {
            "path": str(PARAMETERS.resolve()),
            "sha256": f"sha256:{sha256(PARAMETERS)}",
        },
        "model": {"kind": "mixture"},
        "active": {
            "identities": identities,
            "coordinates": coordinate_records,
            "ties": [],
        },
        "observations": observations,
        "solver": {
            "evaluation_strategy": "reduced_space",
            "controls": {
                "maximum_iterations": 2 if smoke else 80,
                "optimizer_tolerance": 1e-7,
            },
            "multistart": {
                "affine_bound_margin": 1e-7,
                "starts": [
                    {"identity": "current-bundle", "values": origin_values},
                    {"identity": "directional-screen", "values": directional_values},
                ],
            },
        },
    }


def run_candidate(candidate: str, smoke: bool) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    fit_mapping = candidate_fit_mapping(candidate, smoke)
    suffix = "-smoke" if smoke else ""
    input_path = RESULTS / f"{candidate}{suffix}-fit-input.json"
    input_path.write_text(json.dumps(fit_mapping, indent=2) + "\n", encoding="utf-8")
    result = regression.fit(fit_mapping, base_path=ANALYSIS)
    result_path = RESULTS / f"{candidate}{suffix}-fit-result.json"
    result.to_json(result_path)
    summary = {
        "candidate": candidate,
        "smoke": smoke,
        "fit_input_sha256": sha256(input_path),
        "fit_result_sha256": sha256(result_path),
        "best_usable_start": (
            None if result.best_usable_start is None else result.best_usable_start.index
        ),
        "fitted_values": [
            {"identity": identity, "value": value, "unit": unit}
            for identity, value, unit in result.fitted_values()
        ],
        "accounting": result.accounting.to_mapping(),
        "outcomes": result.outcomes,
    }
    if result.best_usable_start is not None:
        candidate_parameters = result.export_candidate_parameters()
        parameter_path = RESULTS / f"{candidate}{suffix}-parameters.json"
        parameter_path.write_text(
            json.dumps(candidate_parameters.to_mapping(), indent=2) + "\n",
            encoding="utf-8",
        )
        summary.update(
            {
                "parameter_path": str(parameter_path.relative_to(ANALYSIS)),
                "parameter_sha256": sha256(parameter_path),
                "cost": result.best_usable_start.cost,
                "condition_number": result.best_usable_start.condition_number,
                "rank": result.best_usable_start.rank,
                "free_subspace_rank": result.best_usable_start.free_subspace_rank,
                "active_bounds": list(result.best_usable_start.active_bounds),
            }
        )
    summary_path = RESULTS / f"{candidate}{suffix}-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> None:
    verify_wheel()
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", choices=tuple(CANDIDATES))
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    run_candidate(args.candidate, args.smoke)


if __name__ == "__main__":
    from refresh_results import bounded_main
    bounded_main(main)
