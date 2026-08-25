from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import math
import os
from importlib.metadata import distribution
from pathlib import Path
import statistics

import epcsaft
from epcsaft import equilibrium, regression

from generate import ANALYSIS, COMPONENT_IDS, SPECIES_COEFFICIENTS
from run_broader_candidate import PRESSURE_PACKET, _read
from MEA.common.analysis_io import write_diagnostic_rows
from MEA.common.data_access import load_regression_speciation_view
from MEA.epcsaft_ionic.model import load_speciation_targets
from MEA.epcsaft_ionic.parameter_document import (
    expand_parameter_domain,
    materialize_parameter_candidate,
    set_parameter_values,
)
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


RESULTS = ANALYSIS / "results" / "full_predictive_refinement"
START_PARAMETERS = ANALYSIS / "results/final_shared_refinement/summary.json"
BASE_PARAMETER_MAPPING = (
    ANALYSIS / "results/broader_candidate/best_fixed_candidate_parameters.json"
)
SPEC_SOURCE_FILES = {
    "Bottinger": ANALYSIS.parents[3]
    / "data/reference/MEA/observations/liquid_speciation/Bottinger_2007_ChEq.csv",
    "Matin": ANALYSIS.parents[3]
    / "data/reference/MEA/observations/liquid_speciation/Matin_2012_ChEq.csv",
    "Jakobsen": ANALYSIS.parents[3]
    / "data/reference/MEA/observations/liquid_speciation/Jakobsen_2005_ChEq.csv",
}
ACTIVE = (
    "pair/carbon-dioxide/monoethanolamine/k_ij",
    "component/protonated-monoethanolamine/segment_diameter",
    "component/carbamate-anion/segment_diameter",
)
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
            math.isclose(float(row["temperature_K"]), value, abs_tol=1.0e-6)
            for value in PRIMARY_TEMPERATURES_K
        )
    ]


def _sha256(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _output(
    identity: str, coefficients: dict[str, float]
) -> equilibrium.EquilibriumOutput:
    return equilibrium.EquilibriumOutput(
        identity,
        "phase.mole_fraction",
        "dimensionless",
        "true-species-liquid-mole-fraction",
        "mea-nine-species-liquid",
        tuple(coefficients.get(component_id, 0.0) for component_id in COMPONENT_IDS),
        support="positive",
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


def _liquid(
    parameters: epcsaft.Parameters,
    *,
    identity: str,
    temperature_k: float,
    pressure_pa: float,
    loading: float,
    mea_mass_fraction: float = 0.30,
    outputs: tuple[equilibrium.EquilibriumOutput, ...] = (),
    reaction_ln_k_adjustments: dict[str, float] | None = None,
) -> object:
    error: Exception | None = None
    for budget, maximum_iterations in ((2, 50), (10, 100)):
        try:
            return build_homogeneous_reactive_problem(
                parameters,
                identity=f"{identity}-liquid",
                phase_identity="mea-nine-species-liquid",
                continuation_identity=f"{identity}-liquid",
                temperature_k=temperature_k,
                pressure_pa=pressure_pa,
                mea_mass_fraction_unloaded=mea_mass_fraction,
                loading_mol_co2_per_mol_mea=loading,
                maximum_log_composition_distance=2.0,
                maximum_log_volume_distance=2.0,
                solver_options={
                    "maximum_iterations": maximum_iterations,
                    "convergence_tolerance": 1.0e-6,
                    "primary_start_budget": budget,
                },
                reaction_ln_k_adjustments=reaction_ln_k_adjustments,
                allow_reaction_extrapolation=True,
            )
        except (
            RuntimeError,
            ValueError,
            equilibrium.ChemicalEquilibriumError,
        ) as caught:
            error = caught
    assert error is not None
    raise error


def _bubble_problem(parameters: epcsaft.Parameters, row: dict[str, object]) -> object:
    identity = f"full-predictive-{row['observation_id']}"
    temperature_k = float(row["temperature_K"])
    pressure_pa = float(row["state_pressure_pa"])
    pressure_interval_pa = tuple(float(value) for value in row["pressure_interval_pa"])
    pressure_starts_pa = tuple(float(value) for value in row["pressure_starts_pa"])
    liquid = _liquid(
        parameters,
        identity=identity,
        temperature_k=temperature_k,
        pressure_pa=pressure_pa,
        loading=float(row["co2_loading_mol_per_mol_mea"]),
        reaction_ln_k_adjustments=dict(row.get("reaction_ln_k_adjustments", {})),
    )
    return equilibrium.GeneralReactiveEquilibriumProblem(
        identity=identity,
        temperature=equilibrium.Fixed(temperature_k * epcsaft.unit_registry.kelvin),
        pressure=equilibrium.Solved(
            pressure_pa * epcsaft.unit_registry.pascal,
            tuple(
                value * epcsaft.unit_registry.pascal for value in pressure_interval_pa
            ),
            tuple(value * epcsaft.unit_registry.pascal for value in pressure_starts_pa),
        ),
        phases=(
            equilibrium.ReactivePhase(
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
            ),
            equilibrium.ReactivePhase(
                "mea-three-neutral-vapor",
                "vapor",
                "incipient",
                equilibrium.DeclaredNeutralComponents(
                    ("carbon-dioxide", "monoethanolamine", "water")
                ),
                equilibrium.IdealGasModel("provider-helmholtz-coordinate-basis"),
            ),
        ),
        reaction_system=liquid.reaction_system,
        reaction_phase_ids=(liquid.phase_identity,),
        outputs=(
            equilibrium.EquilibriumOutput(
                "carbon-dioxide-partial-pressure",
                "phase.partial_pressure",
                "pascal",
                "true-species-vapor-partial-pressure",
                "mea-three-neutral-vapor",
                (1.0, 0.0, 0.0),
                support="positive",
            ),
        ),
        continuation_identity=f"{identity}-bubble",
    )


def _compile_pressure(
    payload: tuple[dict[str, object], dict[str, str]],
) -> tuple[dict[str, object] | None, dict[str, object]]:
    mapping, row = payload
    identity = row["observation_id"]
    try:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        active = epcsaft.ActiveParameterSet(parameters, ACTIVE)
        model = epcsaft.Mixture(parameters)
        problem = _bubble_problem(parameters, row)
        reference = (
            equilibrium.certify_general_reactive_equilibrium_continuation_reference(
                model,
                problem,
                active_parameters=active,
                maximum_log_pressure_distance=float(
                    row["maximum_log_pressure_distance"]
                ),
                maximum_log_composition_distance=2.0,
                maximum_log_volume_distance=2.0,
            )
        )
        problem = replace(problem, continuation_reference=reference)
        result = equilibrium.phase_equilibrium(model, problem, active_parameters=active)
        if result.status != "evaluated" or result.values[0] is None:
            raise RuntimeError(
                str(result.failure or "reactive bubble state was non-evaluable")
            )
        observation = {
            "family": "equilibrium",
            "identity": f"pressure-{identity}",
            "request": equilibrium.general_reactive_equilibrium_problem_to_mapping(
                problem
            ),
            "targets": [
                _target(
                    identity=identity,
                    prediction_identity="carbon-dioxide-partial-pressure",
                    observed=float(row["observed_pco2_pa"]),
                    unit="pascal",
                    basis="true-species-vapor-partial-pressure",
                    source_identity=row["source_row_identity"],
                    source_hash=f"sha256:{row['source_file_sha256']}",
                    multiplier=1.0,
                    classification=row["measurement_role"],
                )
            ],
            "multiplier": 1.0,
        }
        return observation, {
            "identity": identity,
            "block": "pressure",
            "status": "evaluated",
            "predicted": float(result.values[0]),
            "jacobian": list(result.jacobian[0] or ()),
            "observed": float(row["observed_pco2_pa"]),
            "solved_total_pressure_pa": reference.pressure_pa,
            "temperature_k": float(row["temperature_K"]),
            "loading": float(row["co2_loading_mol_per_mol_mea"]),
            "source_identity": row["source_row_identity"],
            "analysis_role": row["analysis_role"],
        }
    except Exception as error:
        return None, {
            "identity": identity,
            "block": "pressure",
            "status": "failed",
            "reason": str(error),
        }


def _evaluate_pressure_reference(
    payload: tuple[dict[str, object], dict[str, object]],
) -> dict[str, object]:
    mapping, row = payload
    try:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        active = epcsaft.ActiveParameterSet(parameters, ACTIVE)
        model = epcsaft.Mixture(parameters)
        reference = (
            equilibrium.certify_general_reactive_equilibrium_continuation_reference(
                model,
                _bubble_problem(parameters, row),
                active_parameters=active,
                maximum_log_pressure_distance=float(
                    row["maximum_log_pressure_distance"]
                ),
                maximum_log_composition_distance=2.0,
                maximum_log_volume_distance=2.0,
            )
        )
        return {
            "identity": row["observation_id"],
            "status": "evaluated",
            "predicted": reference.pressure_pa * reference.vapor_mole_fractions[0],
            "observed": float(row["observed_pco2_pa"]),
            "temperature_k": float(row["temperature_K"]),
            "loading": float(row["co2_loading_mol_per_mol_mea"]),
        }
    except Exception as error:
        return {
            "identity": row["observation_id"],
            "status": "failed",
            "reason": str(error),
        }


def _compile_speciation(
    payload: tuple[dict[str, object], dict[str, object]],
) -> tuple[dict[str, object] | None, dict[str, object]]:
    mapping, state = payload
    identity = str(state["identity"])
    try:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        active = epcsaft.ActiveParameterSet(parameters, ACTIVE)
        model = epcsaft.Mixture(parameters)
        outputs = tuple(
            replace(
                _output(
                    str(target["prediction_identity"]), dict(target["coefficients"])
                ),
                basis=str(target["basis"]),
                aggregate_identity=(
                    str(target["prediction_identity"])
                    if target["classification"] == "aggregate_direct"
                    else None
                ),
                covariance_identity=(
                    str(state["group_id"])
                    if target["classification"] == "aggregate_direct"
                    else None
                ),
            )
            for target in state["targets"]
        )
        liquid = _liquid(
            parameters,
            identity=f"full-predictive-{identity}",
            temperature_k=float(state["temperature_k"]),
            pressure_pa=float(state["pressure_pa"]),
            loading=float(state["loading"]),
            outputs=outputs,
            reaction_ln_k_adjustments=dict(state.get("reaction_ln_k_adjustments", {})),
        )
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
        problem = equilibrium.GeneralReactiveEquilibriumProblem(
            f"full-predictive-{identity}",
            equilibrium.Fixed(
                float(state["temperature_k"]) * epcsaft.unit_registry.kelvin
            ),
            equilibrium.Fixed(
                float(state["pressure_pa"]) * epcsaft.unit_registry.pascal
            ),
            (phase,),
            liquid.reaction_system,
            (liquid.phase_identity,),
            outputs,
        )
        result = equilibrium.phase_equilibrium(model, problem, active_parameters=active)
        if result.status != "evaluated" or any(
            value is None for value in result.values
        ):
            raise RuntimeError(
                str(result.failure or "reactive speciation state was non-evaluable")
            )
        observation = {
            "family": "equilibrium",
            "identity": identity,
            "request": equilibrium.general_reactive_equilibrium_problem_to_mapping(
                problem
            ),
            "targets": [
                _target(
                    identity=str(target["identity"]),
                    prediction_identity=str(target["prediction_identity"]),
                    observed=float(target["observed"]),
                    unit="dimensionless",
                    basis=str(target["basis"]),
                    source_identity=identity,
                    source_hash=str(state["source_hash"]),
                    multiplier=1.0,
                    classification=str(target["classification"]),
                )
                | {
                    "aggregate_identity": (
                        str(target["prediction_identity"])
                        if target["classification"] == "aggregate_direct"
                        else None
                    ),
                    "covariance_identity": (
                        str(state["group_id"])
                        if target["classification"] == "aggregate_direct"
                        else None
                    ),
                }
                for target in state["targets"]
            ],
            "multiplier": 1.0,
        }
        return observation, {
            "identity": identity,
            "block": "speciation",
            "status": "evaluated",
            "target_count": len(state["targets"]),
            "temperature_k": float(state["temperature_k"]),
            "loading": float(state["loading"]),
            "group_id": str(state["group_id"]),
            "targets": [
                {
                    "identity": target["identity"],
                    "predicted": float(predicted),
                    "jacobian": list(jacobian or ()),
                    "observed": float(target["observed"]),
                    "basis": target["basis"],
                    "classification": target["classification"],
                }
                for target, predicted, jacobian in zip(
                    state["targets"], result.values, result.jacobian, strict=True
                )
            ],
        }
    except Exception as error:
        return None, {
            "identity": identity,
            "block": "speciation",
            "status": "failed",
            "reason": str(error),
        }


def _evaluate_speciation_reference(
    payload: tuple[dict[str, object], dict[str, object]],
) -> dict[str, object]:
    mapping, state = payload
    try:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        liquid = _liquid(
            parameters,
            identity=f"predictive-reference-{state['identity']}",
            temperature_k=float(state["temperature_k"]),
            pressure_pa=float(state["pressure_pa"]),
            loading=float(state["loading"]),
            reaction_ln_k_adjustments=dict(state.get("reaction_ln_k_adjustments", {})),
        )
        composition = liquid.continuation_reference.mole_fractions
        return {
            "identity": state["identity"],
            "status": "evaluated",
            "temperature_k": float(state["temperature_k"]),
            "loading": float(state["loading"]),
            "targets": [
                {
                    "identity": target["identity"],
                    "observed": target["observed"],
                    "predicted": math.fsum(
                        float(target["coefficients"].get(component_id, 0.0)) * value
                        for component_id, value in zip(
                            COMPONENT_IDS, composition, strict=True
                        )
                    ),
                }
                for target in state["targets"]
            ],
        }
    except Exception as error:
        return {
            "identity": state["identity"],
            "status": "failed",
            "reason": str(error),
        }


def _speciation_states(role: str) -> list[dict[str, object]]:
    targets = load_speciation_targets(None, role=role)
    view = load_regression_speciation_view(role=role).set_index("state_id")
    states: list[dict[str, object]] = []
    for state in targets:
        source_path = SPEC_SOURCE_FILES[state.source]
        target_rows = [
            {
                "identity": f"{state.row_id}::{species}",
                "prediction_identity": f"speciation-{species}",
                "observed": observed,
                "coefficients": SPECIES_COEFFICIENTS[species],
                "basis": "true-species-liquid-mole-fraction",
                "classification": "direct",
            }
            for species, observed in state.target_speciation.items()
        ]
        target_rows.extend(
            {
                "identity": f"{state.row_id}::{aggregate}",
                "prediction_identity": f"speciation-{aggregate}",
                "observed": observed,
                "coefficients": SPECIES_COEFFICIENTS[aggregate],
                "basis": "true-species-liquid-mole-fraction-linear-aggregate",
                "classification": "aggregate_direct",
            }
            for aggregate, observed in state.aggregate_targets.items()
        )
        states.append(
            {
                "identity": state.row_id,
                "temperature_k": state.T,
                "pressure_pa": state.P,
                "loading": state.loading,
                "source_hash": _sha256(source_path.read_bytes()),
                "group_id": str(view.loc[state.row_id, "group_id"]),
                "targets": target_rows,
            }
        )
    return states


def _compile(
    mapping: dict[str, object],
    workers: int,
    pressure_role: str,
    speciation_role: str,
    pressure_interval_pa: tuple[float, float] | None,
    pressure_starts_pa: tuple[float, ...],
    maximum_log_pressure_distance: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    pressure_rows = (
        []
        if pressure_role == "none"
        else [
            row
            for row in _pressure_rows()
            if pressure_role == "all" or row["analysis_role"] == pressure_role
        ]
    )
    if pressure_rows:
        assert pressure_interval_pa is not None
        pressure_rows = [
            dict(
                row,
                pressure_interval_pa=pressure_interval_pa,
                pressure_starts_pa=(
                    float(row["state_pressure_pa"]),
                    *pressure_starts_pa,
                ),
                maximum_log_pressure_distance=maximum_log_pressure_distance,
            )
            for row in pressure_rows
        ]
    speciation_states = (
        [] if speciation_role == "none" else _speciation_states(speciation_role)
    )
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pressure = list(
            pool.map(_compile_pressure, ((mapping, row) for row in pressure_rows))
        )
        speciation = list(
            pool.map(
                _compile_speciation, ((mapping, state) for state in speciation_states)
            )
        )
    observations = [item for item, _ in (*pressure, *speciation) if item is not None]
    diagnostics = [item for _, item in (*pressure, *speciation)]
    pressure_weight = 1.0 if not pressure_rows else 1.0 / math.sqrt(len(pressure_rows))
    speciation_count = sum(
        len(item["targets"]) for item, _ in speciation if item is not None
    )
    speciation_weight = (
        1.0 if not speciation_count else 1.0 / math.sqrt(speciation_count)
    )
    for observation in observations:
        for target in observation["targets"]:
            target["multiplier"] = (
                pressure_weight if target["unit"] == "pascal" else speciation_weight
            )
    return observations, diagnostics


def _metrics(rows: list[dict[str, object]]) -> dict[str, float]:
    residuals = [
        math.log(float(row["predicted"]) / float(row["observed"])) for row in rows
    ]
    rmse = math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
    return {
        "log_rmse": rmse,
        "rms_factor": math.exp(rmse),
        "median_factor": math.exp(statistics.median(map(abs, residuals))),
        "mean_log_bias": statistics.fmean(residuals),
    }


def _write_result(
    result: object,
    mapping: dict[str, object],
    origins: tuple[float, ...],
    results: Path,
    raw_results: Path,
    fit_mapping: dict[str, object],
) -> None:
    result.to_json(raw_results / "fit_result.json")
    payload = result.to_mapping()
    fitted = {row["identity"]: row["value"] for row in payload["fitted_values"]}
    final_mapping = deepcopy(mapping)
    set_parameter_values(final_mapping, fitted)
    final_payload = (
        json.dumps(final_mapping, indent=2, sort_keys=True) + "\n"
    ).encode()
    rows = payload["evaluated_rows"]
    with (results / "fit_rows.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = (
            "identity",
            "observed",
            "predicted",
            "scaled_residual",
            "unit",
            "basis",
            "source_identity",
        )
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)
    with (results / "parameter_table.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("identity", "start", "fitted", "lower", "upper"))
        for identity, start, fitted_value, bounds in zip(
            ACTIVE, origins, (fitted[x] for x in ACTIVE), BOUNDS, strict=True
        ):
            writer.writerow((identity, start, fitted_value, *bounds))
    accepted = (
        None
        if payload["best_usable_start"] is None
        else payload["starts"][payload["best_usable_start"]]
    )
    wheel_path = Path(
        json.loads(distribution("epcsaft").read_text("direct_url.json"))[
            "url"
        ].removeprefix("file://")
    )
    summary = {
        "schema": "mea.full-predictive-pressure-speciation-refinement.v1",
        "status": "completed" if accepted is not None else "no_usable_start",
        "engine_wheel_path": str(wheel_path),
        "engine_wheel_sha256": hashlib.sha256(wheel_path.read_bytes()).hexdigest(),
        "pressure_row_count": sum(row["unit"] == "pascal" for row in rows),
        "speciation_target_count": sum(row["unit"] == "dimensionless" for row in rows),
        "pressure_metrics": _metrics([row for row in rows if row["unit"] == "pascal"]),
        "speciation_metrics": _metrics(
            [row for row in rows if row["unit"] == "dimensionless"]
        ),
        "fitted_values": fitted,
        "final_cost": None if accepted is None else accepted["cost"],
        "termination": None if accepted is None else accepted["solver_status"],
        "jacobian_singular_values": None
        if accepted is None
        else accepted["singular_values"],
        "jacobian_condition_number": None
        if accepted is None
        else accepted["condition_number"],
        "accounting": payload["accounting"],
        "pressure_formulation": "full specified liquid-plus-incipient-vapor reactive bubble GREPE",
        "parameter_candidate": {
            "base_parameter_mapping": str(
                BASE_PARAMETER_MAPPING.relative_to(ANALYSIS.parents[3])
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
            "sha256": _sha256(final_payload),
        },
        "active": fit_mapping["active"],
        "solver": fit_mapping["solver"],
        "fit_result_identity": {
            key: payload[key]
            for key in (
                "schema",
                "schema_version",
                "digest",
                "artifact_fingerprint",
                "package_fingerprint",
                "candidate_parameter_identity",
                "evaluated_row_table_hash",
            )
        },
    }
    (results / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=os.process_cpu_count() or 1)
    parser.add_argument("--maximum-iterations", type=int, default=3)
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--fit-existing", action="store_true")
    parser.add_argument("--results-label", default="full_predictive_refinement")
    parser.add_argument("--pressure-bounds-pa", type=float, nargs=2)
    parser.add_argument("--pressure-starts-pa", type=float, nargs="+")
    parser.add_argument("--maximum-log-pressure-distance", type=float, default=2.0)
    parser.add_argument(
        "--pressure-role",
        choices=("none", "all", "training", "reserved", "non_scoring_domain_challenge"),
        default="all",
    )
    parser.add_argument(
        "--speciation-role",
        choices=("none", "active_training", "reserved_validation"),
        default="active_training",
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    pressure_interval_pa = (
        None if args.pressure_bounds_pa is None else tuple(args.pressure_bounds_pa)
    )
    if args.pressure_role != "none" and pressure_interval_pa is None:
        parser.error("--pressure-bounds-pa is required when pressure rows are selected")
    if pressure_interval_pa is not None and not (
        0.0 < pressure_interval_pa[0] < pressure_interval_pa[1]
    ):
        parser.error("--pressure-bounds-pa must be positive and increasing")
    if args.maximum_log_pressure_distance <= 0.0:
        parser.error("--maximum-log-pressure-distance must be positive")
    pressure_starts_pa = tuple(args.pressure_starts_pa or ())
    if pressure_interval_pa is not None and any(
        not pressure_interval_pa[0] <= value <= pressure_interval_pa[1]
        for value in pressure_starts_pa
    ):
        parser.error("--pressure-starts-pa must lie inside --pressure-bounds-pa")
    results = ANALYSIS / "results" / args.results_label
    raw_results = ANALYSIS / "results/runs" / args.results_label
    results.mkdir(parents=True, exist_ok=True)
    raw_results.mkdir(parents=True, exist_ok=True)
    mapping = materialize_parameter_candidate(START_PARAMETERS)
    if pressure_interval_pa is not None:
        mapping = expand_parameter_domain(mapping, pressures_pa=pressure_interval_pa)
    parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
    origins = tuple(epcsaft.ActiveParameterSet(parameters, ACTIVE).values)
    parameter_payload = (
        json.dumps(mapping, separators=(",", ":"), sort_keys=True) + "\n"
    ).encode()
    parameter_path = raw_results / "start_parameters.json"
    parameter_path.write_bytes(parameter_payload)
    if args.fit_existing:
        fit_mapping = json.loads(
            (raw_results / "fit_input.json").read_text(encoding="utf-8")
        )
        result_path = raw_results / "fit_result.json"
        if result_path.exists():
            prior = json.loads(result_path.read_text(encoding="utf-8"))
            fitted = {row["identity"]: row["value"] for row in prior["fitted_values"]}
            fit_mapping["solver"]["multistart"]["starts"] = [
                {
                    "identity": "complete-row-continuation",
                    "values": [fitted[identity] for identity in ACTIVE],
                }
            ]
        fit_mapping["solver"]["controls"]["maximum_iterations"] = (
            args.maximum_iterations
        )
    else:
        observations, diagnostics = _compile(
            mapping,
            args.workers,
            args.pressure_role,
            args.speciation_role,
            pressure_interval_pa,
            pressure_starts_pa,
            args.maximum_log_pressure_distance,
        )
        write_diagnostic_rows(results / "compile_diagnostics.csv", diagnostics)
        failures = [row for row in diagnostics if row["status"] != "evaluated"]
        if failures:
            print(
                json.dumps(
                    {"status": "compile_failed", "failures": failures}, sort_keys=True
                ),
                flush=True,
            )
            raise SystemExit(2)
        fit_mapping = {
            "schema_version": 2,
            "parameters": {
                "path": str(parameter_path),
                "sha256": _sha256(parameter_payload),
            },
            "model": {"kind": "mixture"},
            "active": {
                "identities": list(ACTIVE),
                "coordinates": {
                    identity: {"bounds": list(bounds), "origin": origin, "scale": scale}
                    for identity, bounds, origin, scale in zip(
                        ACTIVE, BOUNDS, origins, SCALES, strict=True
                    )
                },
                "ties": [],
            },
            "observations": observations,
            "solver": {
                "multistart": {
                    "starts": [
                        {
                            "identity": "best-structure-warm-start",
                            "values": list(origins),
                        }
                    ],
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
    (raw_results / "fit_input.json").write_text(
        json.dumps(fit_mapping, indent=2, sort_keys=True) + "\n"
    )
    if args.compile_only:
        print(
            json.dumps(
                {
                    "status": "compiled",
                    "observation_count": len(fit_mapping["observations"]),
                    "target_count": sum(
                        len(x["targets"]) for x in fit_mapping["observations"]
                    ),
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return
    result = regression.fit(fit_mapping, base_path=ANALYSIS.parents[3])
    _write_result(result, mapping, origins, results, raw_results, fit_mapping)


if __name__ == "__main__":
    main()
