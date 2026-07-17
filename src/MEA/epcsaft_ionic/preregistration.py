from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from MEA.common.data_access import load_regression_readiness_summary
from MEA.epcsaft_ionic.native_regression import build_native_regression_problem


EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "created_date",
    "readiness",
    "target_role",
    "target_counts",
    "parameters",
    "objective",
    "solver",
    "upstream",
    "policies",
    "gates",
    "command",
}
EXPECTED_POLICIES = {
    "zero_bounds": "preserve_membership_manifest_upper_bounds",
    "aggregate_targets": "membership_approved_targets_only",
    "row_failures": "count_as_failed_prediction_no_omission",
    "active_bounds": "reject_any_active_bound",
    "promotion": "atomic_all_gates_required",
}
EXPECTED_DIAGNOSTICS = ["fit_success", "failure_count", "active_bounds", "by_target_type"]
EXPECTED_MAJOR_SPECIATION_GATES = {"MEAH+": 0.15, "MEACOO-": 0.10}
EXPECTED_ENTRYPOINT = "analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py"


class PreregistrationError(RuntimeError):
    """Raised when a final-fit preregistration does not match frozen evidence."""


@dataclass(frozen=True)
class ValidatedPreregistration:
    payload: dict[str, Any]
    sha256: str
    target_role: str
    target_counts: dict[str, int]
    pressure_weight: float
    speciation_weight: float
    regularization_scale: float
    max_iterations: int
    wall_time_ceiling_seconds: float


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mapping(payload: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise PreregistrationError(f"preregistration field {key!r} must be an object")
    return dict(value)


def _positive_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise PreregistrationError(f"preregistration field {key!r} must be a positive integer")
    return value


def _positive_float(payload: Mapping[str, Any], key: str) -> float:
    try:
        value = float(payload[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise PreregistrationError(f"preregistration field {key!r} must be positive") from exc
    if value <= 0.0:
        raise PreregistrationError(f"preregistration field {key!r} must be positive")
    return value


def load_preregistration(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreregistrationError(f"cannot load final-fit preregistration {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PreregistrationError("final-fit preregistration must be a JSON object")
    return payload


@lru_cache(maxsize=1)
def _native_training_contract() -> tuple[dict[str, int], list[dict[str, Any]]]:
    problem = build_native_regression_problem(target_role="active_training")
    target_counts = {
        "pressure": int(problem.metadata["pressure_row_count"]),
        "speciation": int(problem.metadata["speciation_row_count"]),
    }
    return target_counts, list(problem.parameter_specs)


def validate_preregistration(
    payload: Mapping[str, Any],
    *,
    readiness: Mapping[str, Any] | None = None,
) -> ValidatedPreregistration:
    frozen = dict(payload)
    if set(frozen) != EXPECTED_TOP_LEVEL_KEYS:
        missing = sorted(EXPECTED_TOP_LEVEL_KEYS.difference(frozen))
        extra = sorted(set(frozen).difference(EXPECTED_TOP_LEVEL_KEYS))
        raise PreregistrationError(f"preregistration keys differ: missing={missing}, extra={extra}")
    if frozen["schema_version"] != 1:
        raise PreregistrationError("unsupported preregistration schema_version")
    try:
        date.fromisoformat(str(frozen["created_date"]))
    except ValueError as exc:
        raise PreregistrationError("created_date must be an ISO calendar date") from exc

    current_readiness = dict(readiness or load_regression_readiness_summary())
    readiness_record = _mapping(frozen, "readiness")
    expected_readiness_record = {
        "summary_sha256": canonical_sha256(current_readiness),
        "split_hash": current_readiness.get("split_hash"),
        "source_hashes": current_readiness.get("source_hashes"),
        "role_counts": current_readiness.get("role_counts"),
    }
    if readiness_record != expected_readiness_record:
        raise PreregistrationError("preregistration readiness hashes or frozen role counts have drifted")
    if current_readiness.get("role_counts") != {"active_training": 147, "reserved_validation": 220}:
        raise PreregistrationError("frozen regression role counts are not 147 training and 220 validation")

    if frozen["target_role"] != "active_training":
        raise PreregistrationError("final fitting may use only target_role='active_training'")
    expected_target_counts, expected_parameters = _native_training_contract()
    if frozen["target_counts"] != expected_target_counts or sum(expected_target_counts.values()) != 147:
        raise PreregistrationError("training target counts differ from the frozen native problem")
    if frozen["parameters"] != expected_parameters:
        raise PreregistrationError("parameter order, bounds, scales, initial values, or regularization have drifted")

    objective = _mapping(frozen, "objective")
    expected_objective_keys = {"definition", "target_weights", "regularization_scale"}
    if set(objective) != expected_objective_keys:
        raise PreregistrationError("objective definition is incomplete or contains mutable fields")
    if objective["definition"] != "family_normalized_log10_residuals_plus_scaled_regularization":
        raise PreregistrationError("objective definition has drifted")
    weights = _mapping(objective, "target_weights")
    if set(weights) != {"pressure", "speciation"}:
        raise PreregistrationError("target weights must contain exactly pressure and speciation")
    pressure_weight = _positive_float(weights, "pressure")
    speciation_weight = _positive_float(weights, "speciation")
    regularization_scale = _positive_float(objective, "regularization_scale")
    if regularization_scale != 0.003:
        raise PreregistrationError("regularization scale differs from the frozen parameter contract")

    solver = _mapping(frozen, "solver")
    if {
        "owner": solver.get("owner"),
        "native_function": solver.get("native_function"),
        "backend": solver.get("backend"),
        "derivative_backend": solver.get("derivative_backend"),
    } != {
        "owner": "epcsaft",
        "native_function": "fit_reactive_electrolyte_parameters",
        "backend": "native_ceres",
        "derivative_backend": "production_autodiff_and_implicit",
    }:
        raise PreregistrationError("solver ownership or derivative contract has drifted")
    max_iterations = _positive_int(solver, "max_iterations")
    wall_time_ceiling_seconds = _positive_float(solver, "wall_time_ceiling_seconds")

    upstream = _mapping(frozen, "upstream")
    if current_readiness.get("upstream_execution_admitted") is not True or upstream.get("execution_admitted") is not True:
        raise PreregistrationError("upstream execution is not admitted")
    if upstream.get("capability_receipt_hash") != current_readiness.get("capability_receipt_hash"):
        raise PreregistrationError("upstream capability receipt hash has drifted")

    if _mapping(frozen, "policies") != EXPECTED_POLICIES:
        raise PreregistrationError("zero-bound, aggregate-target, failure, bound, or promotion policy has drifted")
    gates = _mapping(frozen, "gates")
    if gates.get("pressure_median_abs_log10_max_baseline_ratio") != 1.0:
        raise PreregistrationError("pressure acceptance threshold has drifted")
    if gates.get("major_speciation_median_abs_log10_max") != EXPECTED_MAJOR_SPECIATION_GATES:
        raise PreregistrationError("major-speciation acceptance thresholds have drifted")
    if gates.get("minimum_moved_parameter_count") != 3:
        raise PreregistrationError("minimum parameter-movement gate has drifted")
    if gates.get("required_diagnostics") != EXPECTED_DIAGNOSTICS:
        raise PreregistrationError("required native diagnostics are incomplete or reordered")
    if gates.get("plausibility") != "all_preregistered_parameter_and_phase_checks":
        raise PreregistrationError("plausibility gate has drifted")

    command = _mapping(frozen, "command")
    if command.get("entrypoint") != EXPECTED_ENTRYPOINT:
        raise PreregistrationError("final-fit entrypoint has drifted")
    arguments = command.get("arguments")
    if not isinstance(arguments, list) or arguments != [
        "--preregistration",
        "analyses/phase3/ionic_epcsaft_regression/config/final_fit_preregistration.json",
        "--output-label",
        "final_candidate",
        "--promote",
    ]:
        raise PreregistrationError("final-fit command arguments have drifted")

    return ValidatedPreregistration(
        payload=frozen,
        sha256=canonical_sha256(frozen),
        target_role="active_training",
        target_counts=expected_target_counts,
        pressure_weight=pressure_weight,
        speciation_weight=speciation_weight,
        regularization_scale=regularization_scale,
        max_iterations=max_iterations,
        wall_time_ceiling_seconds=wall_time_ceiling_seconds,
    )
