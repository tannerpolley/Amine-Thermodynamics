from __future__ import annotations

import csv
import hashlib
import json
import time
from dataclasses import replace
from pathlib import Path

import epcsaft
from epcsaft import equilibrium, regression

from MEA.epcsaft_ionic.reduced_tracer import build_reduced_tracer_input


ROOT = Path(__file__).resolve().parents[5]
OUTPUT = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first/results/grepe_gate0"
RAW_OUTPUT = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first/results/runs/grepe_gate0"


def _sha256(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _grepe_problem(source: object) -> equilibrium.GeneralReactiveEquilibriumProblem:
    liquid = source.problem
    temperature = source.temperature_k * epcsaft.unit_registry.kelvin
    pressure = source.pressure_pa * epcsaft.unit_registry.pascal
    return equilibrium.GeneralReactiveEquilibriumProblem(
        identity="mea-grepe-gate0-pressure-speciation",
        temperature=equilibrium.Fixed(temperature),
        pressure=equilibrium.Solved(
            pressure,
            (
                6105.45 * epcsaft.unit_registry.pascal,
                300_000.0 * epcsaft.unit_registry.pascal,
            ),
            (pressure,),
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
            equilibrium.EquilibriumOutput(
                "carbamate-liquid-mole-fraction",
                "phase.mole_fraction",
                "dimensionless",
                "true-species-liquid-mole-fraction",
                liquid.phase_identity,
                (0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0),
                support="positive",
            ),
        ),
        continuation_identity="mea-grepe-gate0-coupled-branch",
    )


def main() -> None:
    started = time.monotonic()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    RAW_OUTPUT.mkdir(parents=True, exist_ok=True)
    source = build_reduced_tracer_input()
    active = epcsaft.ActiveParameterSet(
        source.parameters, source.active_parameter_identities
    )
    model = epcsaft.Mixture(source.parameters)
    problem = _grepe_problem(source)
    reference = equilibrium.certify_general_reactive_equilibrium_continuation_reference(
        model,
        problem,
        active_parameters=active,
        maximum_log_pressure_distance=2.0,
        maximum_log_composition_distance=2.0,
        maximum_log_volume_distance=2.0,
    )
    problem = replace(problem, continuation_reference=reference)
    center = equilibrium.phase_equilibrium(model, problem, active_parameters=active)
    if center.status != "evaluated":
        raise RuntimeError(f"GREPE center was non-evaluable: {center.failure}")

    parameter_payload = json.dumps(
        source.parameters.to_mapping(), separators=(",", ":"), sort_keys=True
    ).encode()
    parameter_path = RAW_OUTPUT / "base_parameters.json"
    parameter_path.write_bytes(parameter_payload + b"\n")
    observations = source.observed_values
    fit_mapping = {
        "schema_version": 2,
        "parameters": {
            "path": str(parameter_path),
            "sha256": _sha256(parameter_payload + b"\n"),
        },
        "model": {"kind": "mixture"},
        "active": {
            "identities": list(source.active_parameter_identities),
            "coordinates": {
                identity: {
                    "bounds": [lower, upper],
                    "origin": origin,
                    "scale": scale,
                }
                for identity, lower, upper, origin, scale in zip(
                    source.active_parameter_identities,
                    source.lower_bounds,
                    source.upper_bounds,
                    source.affine_origins,
                    source.affine_scales,
                    strict=True,
                )
            },
            "ties": [],
        },
        "observations": [
            {
                "family": "equilibrium",
                "identity": "mea-source-backed-grepe-gate0",
                "request": equilibrium.general_reactive_equilibrium_problem_to_mapping(
                    problem
                ),
                "targets": [
                    {
                        "identity": "Hilliard2008-vle-0036-pco2",
                        "prediction_identity": "carbon-dioxide-partial-pressure",
                        "observed": observations[0],
                        "unit": "pascal",
                        "residual": "log_ratio",
                        "scale": 1.0,
                        "multiplier": 1.0,
                        "role": "active_training",
                        "measurement_classification": "calibration_derived",
                        "basis": "true-species-vapor-partial-pressure",
                        "source_identity": "Hilliard2008-vle-0036",
                        "source_hash": "sha256:4039394233367cbe491f6f97c3e5adcd5f6975fc696a3fde00cd4ca5af44da6c",
                        "included": True,
                        "drop_reason": None,
                        "aggregate_identity": None,
                        "covariance_identity": None,
                    },
                    {
                        "identity": "Bottinger2008-state-049-carbamate",
                        "prediction_identity": "carbamate-liquid-mole-fraction",
                        "observed": observations[1],
                        "unit": "dimensionless",
                        "residual": "log_ratio",
                        "scale": 1.0,
                        "multiplier": 1.0,
                        "role": "active_training",
                        "measurement_classification": "direct",
                        "basis": "true-species-liquid-mole-fraction",
                        "source_identity": "Bottinger2008-state-049",
                        "source_hash": "sha256:6c4c1e14c2a417bcbd2ff54c5f3978cb1560e7c831a9f931178d021d71b003f5",
                        "included": True,
                        "drop_reason": None,
                        "aggregate_identity": None,
                        "covariance_identity": None,
                    },
                ],
                "multiplier": 1.0,
            }
        ],
        "solver": {
            "multistart": {
                "starts": [
                    {"identity": "source-origin", "values": list(active.values)}
                ],
                "affine_bound_margin": 1.0e-7,
            },
            "controls": {
                "maximum_iterations": 1,
                "function_tolerance": 1.0e-6,
                "gradient_tolerance": 1.0e-6,
                "parameter_tolerance": 1.0e-6,
            },
        },
    }
    (RAW_OUTPUT / "fit_input.json").write_text(
        json.dumps(fit_mapping, indent=2, sort_keys=True) + "\n"
    )
    result = regression.fit(fit_mapping, base_path=ROOT)
    result.to_json(RAW_OUTPUT / "fit_result.json")
    accepted = result.best_usable_start
    rows = result.evaluated_rows
    with (OUTPUT / "fit_table.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "identity",
                "observed",
                "predicted",
                "scaled_residual",
                "unit",
                "basis",
            ),
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "identity": row.identity,
                    "observed": row.observed,
                    "predicted": row.predicted,
                    "scaled_residual": row.scaled_residual,
                    "unit": row.unit,
                    "basis": row.basis,
                }
            )
    summary = {
        "status": "completed" if accepted is not None else "no_usable_start",
        "runtime_seconds": time.monotonic() - started,
        "center_values": list(center.values),
        "center_jacobian": [list(row or ()) for row in center.jacobian],
        "source_observed_values": list(observations),
        "solved_pressure_pa": reference.pressure_pa,
        "solved_vapor_mole_fractions": list(reference.vapor_mole_fractions),
        "fitted_values": [list(row) for row in result.fitted_values()],
        "final_cost": None if accepted is None else accepted.cost,
        "termination": None if accepted is None else accepted.solver_status,
        "usable": None if accepted is None else accepted.usable,
        "accounting": result.accounting.to_mapping(),
        "fit_result_digest": result.digest,
    }
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
