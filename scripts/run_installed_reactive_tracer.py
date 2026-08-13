from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

import epcsaft
from epcsaft import equilibrium

from MEA.epcsaft_ionic.reduced_tracer import build_reduced_tracer_input


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/results/reactive_vle_vertical_slice"
    / "installed_homogeneous_tracer_receipt.json"
)
LOCK = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> None:
    started = time.monotonic()
    source = build_reduced_tracer_input()
    identities = source.active_parameter_identities
    base = epcsaft.ActiveParameterSet(source.parameters, identities)
    descriptor = equilibrium.homogeneous_reactive_observation_descriptor(
        source.problem, source.rows, active_parameters=base
    )
    temperature = source.temperature_k * epcsaft.unit_registry.kelvin
    pressure = source.pressure_pa * epcsaft.unit_registry.pascal

    timings: list[float] = []

    def evaluate(
        values: tuple[float, ...],
    ) -> equilibrium.HomogeneousReactiveObservationResult:
        tick = time.monotonic()
        result = equilibrium.evaluate_homogeneous_reactive_observations(
            source.problem,
            temperature,
            pressure,
            descriptor,
            active_parameters=epcsaft.ActiveParameterSet(
                source.parameters, identities, values=values
            ),
        )
        timings.append(time.monotonic() - tick)
        return result

    center = evaluate(base.values)
    if center.status != "evaluated":
        raise RuntimeError(f"center tracer trial was non-evaluable: {center.failure}")
    step = 1.0e-5
    numerical = np.full((len(source.rows), len(identities)), np.nan)
    difference_schemes: list[str] = []
    perturbations: list[dict[str, object]] = []
    branches = []
    for column, identity in enumerate(identities):
        values = list(base.values)
        values[column] -= step
        lower = evaluate(tuple(values))
        values[column] += 2.0 * step
        upper = evaluate(tuple(values))
        for direction, result in (("lower", lower), ("upper", upper)):
            perturbations.append(
                {
                    "coordinate": identity,
                    "direction": direction,
                    "status": result.status,
                    "failure": None
                    if result.failure is None
                    else asdict(result.failure),
                }
            )
            if result.status == "evaluated":
                assert result.physical_branch is not None
                branches.append(result.physical_branch.branch_family_identity)
        if lower.status == "evaluated" and upper.status == "evaluated":
            numerical[:, column] = (
                np.log(np.asarray(upper.values, dtype=float))
                - np.log(np.asarray(lower.values, dtype=float))
            ) / (2.0 * step)
            difference_schemes.append("central")
        elif upper.status == "evaluated":
            numerical[:, column] = (
                np.log(np.asarray(upper.values, dtype=float)) - np.log(center.values)
            ) / step
            difference_schemes.append("forward_support_boundary")
        elif lower.status == "evaluated":
            numerical[:, column] = (
                np.log(center.values) - np.log(np.asarray(lower.values, dtype=float))
            ) / step
            difference_schemes.append("backward_support_boundary")
        else:
            difference_schemes.append("unavailable_support_boundary")

    values = np.asarray(center.values, dtype=float)
    exact_raw = np.asarray(center.jacobian, dtype=float)
    exact = exact_raw / values[:, None]
    error = np.abs(exact - numerical) / np.maximum(1.0, np.abs(numerical))
    finite_derivative_entries = np.isfinite(error)
    singular_values = np.linalg.svd(exact, compute_uv=False)
    condition = float(singular_values[0] / singular_values[-1])
    observed = np.asarray(source.observed_values, dtype=float)
    residual = np.log(values / observed)
    linearized_step = np.linalg.solve(exact, -residual)
    linearized_values = np.asarray(base.values) + linearized_step
    bounds = np.asarray(
        tuple(zip(source.lower_bounds, source.upper_bounds, strict=True)), dtype=float
    )
    center_branch = center.physical_branch
    state = center.state
    diagnostics = center.diagnostics
    assert center_branch is not None and state is not None and diagnostics is not None

    result: dict[str, object] = {
        "schema_version": 1,
        "identity": "mea-installed-cap12-homogeneous-tracer-v1",
        "engine": json.loads(LOCK.read_text()),
        "scope": "stage_3_mathematical_and_sensitivity_tracer_not_parameter_fit",
        "status": "evaluated",
        "state": {
            "temperature_k": source.temperature_k,
            "pressure_pa": source.pressure_pa,
            "component_ids": list(descriptor.component_ids),
            "amounts_mol": list(state.amounts_mol),
            "mole_fractions": list(state.mole_fractions),
            "volume_m3": state.volume_m3,
            "state_identity": state.state_identity,
            "physical_branch_identity": center_branch.identity,
            "branch_family_identity": center_branch.branch_family_identity,
            "branch_family_invariant_for_perturbations": all(
                branch == center_branch.branch_family_identity for branch in branches
            ),
            "globality_claim": "not_established",
        },
        "observation": {
            "row_identities": list(descriptor.row_identities),
            "row_units": list(descriptor.row_units),
            "observed_values": list(source.observed_values),
            "predicted_values": list(center.values),
            "active_parameter_identities": list(identities),
            "active_parameter_units": list(descriptor.active_parameter_units),
            "active_parameter_values": list(base.values),
            "exact_raw_total_jacobian": exact_raw.tolist(),
            "exact_log_residual_jacobian": exact.tolist(),
            "central_difference_log_residual_jacobian": numerical.tolist(),
            "central_difference_step": step,
            "difference_schemes": difference_schemes,
            "maximum_scaled_derivative_error": (
                float(np.max(error[finite_derivative_entries]))
                if np.any(finite_derivative_entries)
                else None
            ),
            "independent_difference_status": (
                "all_coordinates_checked"
                if all(
                    scheme != "unavailable_support_boundary"
                    for scheme in difference_schemes
                )
                else "partially_unavailable_at_certified_support_boundary"
            ),
            "perturbation_trials": perturbations,
        },
        "certification": {
            "numerical_status": diagnostics.numerical_status,
            "physical_status": diagnostics.physical_status,
            "local_minimum_status": diagnostics.local_minimum_status,
            "trace_status": diagnostics.trace_status,
            "globality_status": diagnostics.globality_status,
            "balance_inf_norm": diagnostics.balance_inf_norm,
            "charge_inf_norm": diagnostics.charge_inf_norm,
            "pressure_relative_residual": diagnostics.pressure_relative_residual,
            "reaction_affinity_inf_norm": diagnostics.reaction_affinity_inf_norm,
            "kkt_stationarity_inf_norm": diagnostics.kkt_stationarity_inf_norm,
            "reduced_hessian_status": diagnostics.reduced_hessian_status,
            "search_basin_count": len(diagnostics.search.basins),
        },
        "identifiability": {
            "rank": int(np.linalg.matrix_rank(exact)),
            "singular_values": singular_values.tolist(),
            "condition_number_2": condition,
            "linearized_unconstrained_step": linearized_step.tolist(),
            "linearized_parameter_values": linearized_values.tolist(),
            "bounds": bounds.tolist(),
            "linearized_step_inside_bounds": bool(
                np.all(linearized_values > bounds[:, 0])
                and np.all(linearized_values < bounds[:, 1])
            ),
            "promotion_status": "not_applicable_tracer_only",
        },
        "accounting": {
            "input_rows": len(source.rows),
            "evaluated_rows": len(center.rows),
            "rejected_rows": 0,
            "failed_rows": 0,
            "dropped_rows": 0,
            "evaluated_trials": 1
            + sum(row["status"] == "evaluated" for row in perturbations),
            "non_evaluable_trials": sum(
                row["status"] != "evaluated" for row in perturbations
            ),
        },
        "fingerprints": {
            "descriptor": descriptor.fingerprint,
            "parameter": descriptor.parameter_fingerprint,
            "topology": descriptor.topology_fingerprint,
            "reference": descriptor.reference_fingerprint,
            "domain": descriptor.domain_fingerprint,
            "problem": descriptor.problem_fingerprint,
            "reaction": descriptor.reaction_fingerprint,
            "active_trial": center.trial.fingerprint if center.trial else None,
            "certified_state": state.fingerprint,
            "physical_branch": center_branch.identity,
        },
        "runtime": {
            "evaluation_seconds": timings,
            "total_seconds": time.monotonic() - started,
        },
        "scientific_decision": (
            "The installed CAP-12 path evaluates the exact nine-species state and total "
            "Jacobian on one stable local branch. This tracer does not qualify parameters; "
            "its source rows lack experimental uncertainty and the unconstrained linearized "
            "two-row correction leaves the declared physical bounds."
        ),
    }
    result["receipt_sha256"] = _canonical_sha256(result)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(OUTPUT.relative_to(ROOT))
    print(result["receipt_sha256"])


if __name__ == "__main__":
    main()
