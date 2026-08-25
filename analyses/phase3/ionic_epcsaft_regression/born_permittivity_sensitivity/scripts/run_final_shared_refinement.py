from __future__ import annotations

import argparse
import csv
from copy import deepcopy
import hashlib
import json
import math
from importlib.metadata import distribution
from pathlib import Path
import re
import statistics

import epcsaft
from epcsaft import equilibrium, regression

from generate import ANALYSIS, COMPONENT_IDS, SOURCE, SPECIES_COEFFICIENTS, _source_states
from run_broader_candidate import PRESSURE_PACKET, _read
from MEA.common.analysis_io import read_diagnostic_rows, write_diagnostic_rows
from MEA.epcsaft_ionic.parameter_document import (
    expand_parameter_domain,
    set_parameter_values,
)
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


RESULTS = ANALYSIS / "results" / "final_shared_refinement"
FULL_PACKET_CACHE = ANALYSIS / "results" / "full_packet_diagnostic"
RAW_RESULTS = ANALYSIS / "results/runs/final_shared_refinement"
FULL_PACKET_RAW = ANALYSIS / "results/runs/full_packet_diagnostic"
START_PARAMETERS = (
    ANALYSIS / "results/broader_candidate/best_fixed_candidate_parameters.json"
)
ACTIVE = (
    "pair/carbon-dioxide/monoethanolamine/k_ij",
    "component/protonated-monoethanolamine/segment_diameter",
    "component/carbamate-anion/segment_diameter",
)
START_VALUES = (0.0, 3.48508556586, 3.53543525721)
BOUNDS = ((-1.0, 1.0), (1.5, 5.8), (1.5, 5.8))
SCALES = (0.5, 2.15, 2.15)
PRIMARY_TEMPERATURES_K = (313.15, 333.15, 353.15)


def _all_pressure_rows() -> list[dict[str, str]]:
    return sorted(
        _read(PRESSURE_PACKET),
        key=lambda row: (
            float(row["mea_mass_fraction"]),
            float(row["temperature_K"]),
            row["source_key"],
            float(row["co2_loading_mol_per_mol_mea"]),
        ),
    )


def _pressure_rows() -> list[dict[str, str]]:
    return [
        row
        for row in _all_pressure_rows()
        if math.isclose(float(row["mea_mass_fraction"]), 0.30, abs_tol=1.0e-8)
        and any(
            math.isclose(float(row["temperature_K"]), temperature_k, abs_tol=1.0e-6)
            for temperature_k in PRIMARY_TEMPERATURES_K
        )
    ]


def _cached_observations() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    cached = json.loads((FULL_PACKET_RAW / "fit_input.json").read_text(encoding="utf-8"))
    selected_ids = {row["observation_id"] for row in _pressure_rows()}
    observations = [
        deepcopy(observation)
        for observation in cached["observations"]
        if observation["targets"][0]["unit"] == "dimensionless"
        or observation["targets"][0]["identity"] in selected_ids
    ]
    pressure = [
        observation
        for observation in observations
        if observation["targets"][0]["unit"] == "pascal"
    ]
    pressure_weight = 1.0 / math.sqrt(len(pressure))
    for observation in pressure:
        observation["targets"][0]["multiplier"] = pressure_weight
    speciation_targets = [
        target
        for observation in observations
        for target in observation["targets"]
        if target["unit"] == "dimensionless"
    ]
    speciation_weight = 1.0 / math.sqrt(len(speciation_targets))
    for target in speciation_targets:
        target["multiplier"] = speciation_weight
    failures = read_diagnostic_rows(
        FULL_PACKET_CACHE / "compile_failures.csv", nested=True
    )
    return observations, [
        failure
        for failure in failures
        if failure["block"] == "speciation" or failure["identity"] in selected_ids
    ]


def _sha256(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _output(identity: str, coefficients: dict[str, float]) -> equilibrium.EquilibriumOutput:
    return equilibrium.EquilibriumOutput(
        identity,
        "phase.mole_fraction",
        "dimensionless",
        "true-species-liquid-mole-fraction",
        "mea-nine-species-liquid",
        tuple(coefficients.get(component_id, 0.0) for component_id in COMPONENT_IDS),
        support="positive",
    )


def _problem(
    parameters: epcsaft.Parameters,
    *,
    identity: str,
    continuation_identity: str,
    temperature_k: float,
    pressure_pa: float,
    mea_mass_fraction: float,
    loading: float,
    outputs: tuple[equilibrium.EquilibriumOutput, ...],
    initial_reference: object | None,
) -> tuple[equilibrium.GeneralReactiveEquilibriumProblem, object]:
    attempts = ((2, initial_reference), (5, None))
    for attempt, (budget, reference) in enumerate(attempts):
        try:
            liquid = build_homogeneous_reactive_problem(
                parameters,
                identity=f"{identity}-liquid",
                phase_identity="mea-nine-species-liquid",
                continuation_identity=continuation_identity,
                temperature_k=temperature_k,
                pressure_pa=pressure_pa,
                mea_mass_fraction_unloaded=mea_mass_fraction,
                loading_mol_co2_per_mol_mea=loading,
                maximum_log_composition_distance=2.0,
                maximum_log_volume_distance=2.0,
                solver_options={
                    "maximum_iterations": 50,
                    "convergence_tolerance": 1.0e-6,
                    "primary_start_budget": budget,
                },
                allow_reaction_extrapolation=True,
                initial_reference=reference,
            )
            break
        except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError):
            if attempt == len(attempts) - 1:
                raise
    phase = equilibrium.ReactivePhase(
        liquid.phase_identity,
        "liquid",
        "finite",
        equilibrium.AllComponents(),
        equilibrium.ProviderModel(
            liquid.phase.admissible_packing_fraction_interval,
            "installed-provider-eos",
        ),
        liquid.continuation_identity,
        liquid.branch_policy,
        liquid.continuation_reference,
    )
    return (
        equilibrium.GeneralReactiveEquilibriumProblem(
            identity,
            equilibrium.Fixed(temperature_k * epcsaft.unit_registry.kelvin),
            equilibrium.Fixed(pressure_pa * epcsaft.unit_registry.pascal),
            (phase,),
            liquid.reaction_system,
            (liquid.phase_identity,),
            outputs,
        ),
        liquid.continuation_reference,
    )


def _target(
    *,
    identity: str,
    prediction_identity: str,
    observed: float,
    unit: str,
    basis: str,
    source_identity: str,
    source_hash: str,
    multiplier: float,
    classification: str,
) -> dict[str, object]:
    return {
        "identity": identity,
        "prediction_identity": prediction_identity,
        "observed": observed,
        "unit": unit,
        "residual": "log_ratio",
        "scale": 1.0,
        "multiplier": multiplier,
        "role": "active_training",
        "measurement_classification": classification,
        "basis": basis,
        "source_identity": source_identity,
        "source_hash": source_hash,
        "included": True,
        "drop_reason": None,
        "aggregate_identity": None,
        "covariance_identity": None,
    }


def _observations(
    parameters: epcsaft.Parameters,
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    pressure_rows = _pressure_rows()
    speciation_states = _source_states()
    observations: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    pressure_observations: list[dict[str, object]] = []
    previous: dict[str, object] = {}
    pressure_output = equilibrium.EquilibriumOutput(
        "co2-liquid-fugacity",
        "phase.fugacity",
        "pascal",
        "liquid-molecular-co2-fugacity-as-pco2-surrogate",
        "mea-nine-species-liquid",
        (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        support="positive",
    )
    for row in pressure_rows:
        temperature_k = float(row["temperature_K"])
        mea_mass_fraction = float(row["mea_mass_fraction"])
        branch = f"final-shared-pressure-{temperature_k:g}-{mea_mass_fraction:g}"
        try:
            problem, previous[branch] = _problem(
                parameters,
                identity=f"final-shared-{row['observation_id']}",
                continuation_identity=branch,
                temperature_k=temperature_k,
                pressure_pa=float(row["state_pressure_pa"]),
                mea_mass_fraction=mea_mass_fraction,
                loading=float(row["co2_loading_mol_per_mol_mea"]),
                outputs=(pressure_output,),
                initial_reference=previous.get(branch),
            )
        except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError) as error:
            skipped.append(
                {
                    "identity": row["observation_id"],
                    "block": "pressure",
                    "reason": str(error),
                }
            )
            print(
                json.dumps(
                    {"skipped": "pressure", "identity": row["observation_id"]},
                    sort_keys=True,
                ),
                flush=True,
            )
            continue
        pressure_observations.append(
            {
                "family": "equilibrium",
                "identity": f"pressure-{row['observation_id']}",
                "request": equilibrium.general_reactive_equilibrium_problem_to_mapping(problem),
                "targets": [
                    _target(
                        identity=row["observation_id"],
                        prediction_identity="co2-liquid-fugacity",
                        observed=float(row["observed_pco2_pa"]),
                        unit="pascal",
                        basis="liquid-molecular-co2-fugacity-as-pco2-surrogate",
                        source_identity=row["source_row_identity"],
                        source_hash=f"sha256:{row['source_file_sha256']}",
                        multiplier=1.0,
                        classification=row["measurement_role"],
                    )
                ],
                "multiplier": 1.0,
            }
        )
        print(
            json.dumps(
                {"prepared": "pressure", "identity": row["observation_id"]},
                sort_keys=True,
            ),
            flush=True,
        )
    pressure_weight = 1.0 / math.sqrt(len(pressure_observations))
    for observation in pressure_observations:
        observation["targets"][0]["multiplier"] = pressure_weight
    observations.extend(pressure_observations)
    source_hash = _sha256(SOURCE.read_bytes())
    previous_reference = None
    speciation_observations: list[dict[str, object]] = []
    for state in speciation_states:
        rows = [
            row
            for row in state["rows"]
            if row["measurement_role"] == "direct_positive"
            and row["species"] in SPECIES_COEFFICIENTS
            and float(row["value_mole_fraction"]) > 0.0
        ]
        outputs = tuple(
            _output(f"speciation-{row['species']}", SPECIES_COEFFICIENTS[row["species"]])
            for row in rows
        )
        try:
            problem, previous_reference = _problem(
                parameters,
                identity=f"final-shared-speciation-{state['loading']:g}",
                continuation_identity="final-shared-speciation-313.15",
                temperature_k=313.15,
                pressure_pa=101_325.0,
                mea_mass_fraction=0.30,
                loading=float(state["loading"]),
                outputs=outputs,
                initial_reference=previous_reference,
            )
        except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError) as error:
            skipped.append(
                {
                    "identity": f"speciation-{state['loading']:g}",
                    "block": "speciation",
                    "reason": str(error),
                }
            )
            print(
                json.dumps(
                    {"skipped": "speciation", "loading": state["loading"]},
                    sort_keys=True,
                ),
                flush=True,
            )
            continue
        speciation_observations.append(
            {
                "family": "equilibrium",
                "identity": f"speciation-{state['loading']:g}",
                "request": equilibrium.general_reactive_equilibrium_problem_to_mapping(problem),
                "targets": [
                    _target(
                        identity=row["record_id"],
                        prediction_identity=f"speciation-{row['species']}",
                        observed=float(row["value_mole_fraction"]),
                        unit="dimensionless",
                        basis="true-species-liquid-mole-fraction",
                        source_identity=row["record_id"],
                        source_hash=source_hash,
                        multiplier=1.0,
                        classification="direct",
                    )
                    for row in rows
                ],
                "multiplier": 1.0,
            }
        )
        print(
            json.dumps(
                {"prepared": "speciation", "loading": state["loading"]},
                sort_keys=True,
            ),
            flush=True,
        )
    speciation_count = sum(
        len(observation["targets"]) for observation in speciation_observations
    )
    speciation_weight = 1.0 / math.sqrt(speciation_count)
    for observation in speciation_observations:
        for target in observation["targets"]:
            target["multiplier"] = speciation_weight
    observations.extend(speciation_observations)
    return observations, skipped


def _postprocess(
    result: dict[str, object],
    mapping: dict[str, object],
    parameter_payload: bytes,
) -> dict[str, object]:
    fitted = {row["identity"]: row["value"] for row in result["fitted_values"]}
    rows = result["evaluated_rows"]
    accepted_index = result["best_usable_start"]
    accepted = None if accepted_index is None else result["starts"][accepted_index]
    final_mapping = deepcopy(mapping)
    set_parameter_values(final_mapping, fitted)
    final_payload = json.dumps(final_mapping, indent=2, sort_keys=True) + "\n"
    with (RESULTS / "fit_rows.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = (
            "identity", "observed", "predicted", "scaled_residual", "unit", "basis",
            "source_identity", "measurement_classification",
        )
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **{field: row[field] for field in fields[:-1]},
                    "measurement_classification": row["series_metadata"][
                        "measurement_classification"
                    ],
                }
            )
    with (RESULTS / "parameter_table.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("identity", "start", "fitted", "lower", "upper"))
        for identity, start, bounds in zip(ACTIVE, START_VALUES, BOUNDS, strict=True):
            writer.writerow((identity, start, fitted.get(identity), *bounds))
    wheel_url = json.loads(distribution("epcsaft").read_text("direct_url.json"))["url"]
    wheel_path = Path(wheel_url.removeprefix("file://"))
    pressure_rows = [row for row in rows if row["unit"] == "pascal"]
    speciation_rows = [row for row in rows if row["unit"] == "dimensionless"]
    selected_ids = {row["observation_id"] for row in _pressure_rows()}
    domain_excluded = [
        {
            "identity": row["observation_id"],
            "temperature_k": float(row["temperature_K"]),
            "mea_mass_fraction": float(row["mea_mass_fraction"]),
            "reason": "outside primary 30 wt% MEA, 40/60/80 degC fit domain",
        }
        for row in _all_pressure_rows()
        if row["observation_id"] not in selected_ids
    ]
    (RESULTS / "domain_excluded_pressure_rows.json").write_text(
        json.dumps(domain_excluded, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    def metrics(selected: list[dict[str, object]]) -> dict[str, float]:
        if not selected:
            return {}
        residuals = [
            math.log(float(row["predicted"]) / float(row["observed"]))
            for row in selected
        ]
        log_rmse = math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
        return {
            "log_rmse": log_rmse,
            "rms_factor": math.exp(log_rmse),
            "median_factor": math.exp(statistics.median(map(abs, residuals))),
            "mean_log_bias": statistics.fmean(residuals),
        }

    initial_match = None if accepted is None else re.search(
        r"Initial cost: ([0-9.eE+-]+)", accepted["solver_status"]
    )
    initial_cost = None if initial_match is None else float(initial_match.group(1))
    summary = {
        "schema": "mea.final-shared-pressure-speciation-refinement.v1",
        "status": "completed" if accepted is not None else "no_usable_start",
        "fit_result_digest": result["digest"],
        "engine_wheel_path": str(wheel_path),
        "engine_wheel_sha256": hashlib.sha256(wheel_path.read_bytes()).hexdigest(),
        "start_parameter_mapping_sha256": _sha256(parameter_payload),
        "active_parameters": list(ACTIVE),
        "retained_start_identity": None if accepted is None else accepted["start_identity"],
        "retained_start_values": None if accepted is None else accepted["initial_physical"],
        "start_identity_note": (
            "retained label says prior-informed, but exact initial values are the source geometry"
            if accepted is not None and accepted["start_identity"] == "prior-informed"
            else None
        ),
        "fitted_values": fitted,
        "parameter_candidate": {
            "base_parameter_mapping": str(
                START_PARAMETERS.relative_to(ANALYSIS.parents[3])
            ),
            "domain": {
                "temperature_range_k": [
                    final_mapping["domains"][0]["temperature_min"]["magnitude"],
                    final_mapping["domains"][0]["temperature_max"]["magnitude"],
                ],
                "pressure_range_pa": [
                    final_mapping["domains"][0]["pressure_min"]["magnitude"],
                    final_mapping["domains"][0]["pressure_max"]["magnitude"],
                ],
            },
            "sha256": _sha256(final_payload.encode()),
        },
        "pressure_row_count": len(pressure_rows),
        "speciation_row_count": len(speciation_rows),
        "compile_failure_count": len(
            read_diagnostic_rows(RESULTS / "compile_failures.csv", nested=True)
        ),
        "domain_excluded_pressure_row_count": len(domain_excluded),
        "declared_pressure_row_count": len(_pressure_rows()),
        "available_pressure_packet_row_count": len(_all_pressure_rows()),
        "fit_domain": {
            "mea_mass_fraction": 0.30,
            "temperature_k": list(PRIMARY_TEMPERATURES_K),
        },
        "pressure_packet_sha256": _sha256(PRESSURE_PACKET.read_bytes()),
        "pressure_metrics": metrics(pressure_rows),
        "speciation_metrics": metrics(speciation_rows),
        "objective": "equal-block-weighted natural-log residual SSE",
        "pressure_formulation": "fixed-TP one-liquid GREPE molecular-CO2 fugacity surrogate",
        "final_cost": None if accepted is None else accepted["cost"],
        "initial_cost": initial_cost,
        "relative_cost_reduction": (
            None
            if initial_cost is None or accepted is None
            else 1.0 - float(accepted["cost"]) / initial_cost
        ),
        "termination": None if accepted is None else accepted["solver_status"],
        "usable": None if accepted is None else accepted["usable"],
        "jacobian_singular_values": None if accepted is None else accepted["singular_values"],
        "jacobian_condition_number": None if accepted is None else accepted["condition_number"],
        "accounting": result["accounting"],
        "optimizer_wall_seconds": (
            (RAW_RESULTS / "fit_result.json").stat().st_mtime
            - (RAW_RESULTS / "fit_input.json").stat().st_mtime
        ),
        "claim": "shared-parameter refinement; coupled bubble confirmation required before phase-equilibrium promotion",
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--postprocess-existing", action="store_true")
    parser.add_argument("--resume-existing", action="store_true")
    parser.add_argument("--maximum-iterations", type=int, default=5)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    RAW_RESULTS.mkdir(parents=True, exist_ok=True)
    use_cache = (FULL_PACKET_RAW / "fit_input.json").exists()
    parameter_source = (
        FULL_PACKET_RAW / "start_parameters.json" if use_cache else START_PARAMETERS
    )
    mapping = deepcopy(json.loads(parameter_source.read_text(encoding="utf-8")))
    pressure_rows = _pressure_rows()
    if not use_cache:
        mapping = expand_parameter_domain(
            mapping,
            temperatures_k=tuple(float(row["temperature_K"]) for row in pressure_rows),
            pressures_pa=tuple(float(row["state_pressure_pa"]) for row in pressure_rows),
        )
    parameter_payload = (
        json.dumps(mapping, separators=(",", ":"), sort_keys=True) + "\n"
    ).encode()
    if args.postprocess_existing:
        result = json.loads((RAW_RESULTS / "fit_result.json").read_text(encoding="utf-8"))
        summary = _postprocess(result, mapping, parameter_payload)
        print(json.dumps(summary, sort_keys=True), flush=True)
        return
    if args.resume_existing:
        fit_mapping = json.loads((RAW_RESULTS / "fit_input.json").read_text(encoding="utf-8"))
        prior = json.loads((RAW_RESULTS / "fit_result.json").read_text(encoding="utf-8"))
        fitted = {row["identity"]: row["value"] for row in prior["fitted_values"]}
        fit_mapping["solver"]["multistart"]["starts"] = [
            {
                "identity": "complete-pass-continuation",
                "values": [fitted[identity] for identity in ACTIVE],
            }
        ]
        fit_mapping["solver"]["controls"]["maximum_iterations"] = args.maximum_iterations
        (RAW_RESULTS / "fit_input.json").write_text(
            json.dumps(fit_mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        result = regression.fit(fit_mapping, base_path=ANALYSIS.parents[3])
        result.to_json(RAW_RESULTS / "fit_result.json")
        summary = _postprocess(result.to_mapping(), mapping, parameter_payload)
        print(json.dumps(summary, sort_keys=True), flush=True)
        return
    if use_cache:
        observations, skipped = _cached_observations()
    else:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        observations, skipped = _observations(parameters)
    write_diagnostic_rows(RESULTS / "compile_failures.csv", skipped)
    parameter_path = RAW_RESULTS / "start_parameters.json"
    parameter_path.write_bytes(parameter_payload)
    fit_mapping = {
        "schema_version": 2,
        "parameters": {"path": str(parameter_path), "sha256": _sha256(parameter_payload)},
        "model": {"kind": "mixture"},
        "active": {
            "identities": list(ACTIVE),
            "coordinates": {
                identity: {"bounds": list(bounds), "origin": origin, "scale": scale}
                for identity, bounds, origin, scale in zip(
                    ACTIVE, BOUNDS, START_VALUES, SCALES, strict=True
                )
            },
            "ties": [],
        },
        "observations": observations,
        "solver": {
            "multistart": {
                "starts": [{"identity": "source-origin", "values": list(START_VALUES)}],
                "affine_bound_margin": 1.0e-7,
            },
            "controls": {
                "maximum_iterations": args.maximum_iterations,
                "function_tolerance": 1.0e-6,
                "gradient_tolerance": 1.0e-6,
                "parameter_tolerance": 1.0e-6,
            },
        },
    }
    (RAW_RESULTS / "fit_input.json").write_text(
        json.dumps(fit_mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result = regression.fit(fit_mapping, base_path=ANALYSIS.parents[3])
    result.to_json(RAW_RESULTS / "fit_result.json")
    summary = _postprocess(result.to_mapping(), mapping, parameter_payload)
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
