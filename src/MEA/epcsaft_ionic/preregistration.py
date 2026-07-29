from __future__ import annotations

import csv
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
GATE0_PREREGISTRATION_PATH = (
    Path(__file__).resolve().parents[3]
    / "analyses"
    / "phase3"
    / "ionic_epcsaft_regression"
    / "ionic_volumetric_fit_preregistration.json"
)
EXPECTED_GATE0_CANONICAL_SHA256 = (
    "3c81025fafcbe3d593e1feb268e49400c4ff3681f9fc05194cdc152e096f93dc"
)
GATE0_REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_TRACER_SOURCES = {
    "pressure": {
        "canonical_path": (
            "data/reference/MEA/observations/vapor_liquid_equilibrium/"
            "Canonical_VLE_Observations.csv"
        ),
        "canonical_sha256": (
            "9e7d9ba5fead8bfa83a311dad341e3e2e8df1806d5249642a23562e99a72cb73"
        ),
        "raw_path": (
            "data/reference/MEA/observations/vapor_liquid_equilibrium/"
            "Hilliard_2008_VLE.csv"
        ),
        "raw_sha256": (
            "4039394233367cbe491f6f97c3e5adcd5f6975fc696a3fde00cd4ca5af44da6c"
        ),
        "manifest_path": "data/reference/MEA/manifests/pco2_metrology_manifest.csv",
        "manifest_sha256": (
            "0d14803873a60534ec5d7df382cfbd0ae03e4aaeba68bb5d54be7e4def8397cc"
        ),
    },
    "speciation": {
        "canonical_path": (
            "data/reference/MEA/observations/liquid_speciation/"
            "Canonical_Combined_ChEq.csv"
        ),
        "canonical_sha256": (
            "8c07df9efd1c1ecbd775ccdd42791e0cef1880b3837e5749a60d2142aa85809e"
        ),
        "raw_path": (
            "data/reference/MEA/observations/liquid_speciation/"
            "Bottinger_2007_ChEq.csv"
        ),
        "raw_sha256": (
            "6c4c1e14c2a417bcbd2ff54c5f3978cb1560e7c831a9f931178d021d71b003f5"
        ),
        "manifest_path": (
            "data/reference/MEA/manifests/speciation_target_membership.csv"
        ),
        "manifest_sha256": (
            "a89a3f0373a86813482158f180939cf57f74be038cd59f244dfadcb689923190"
        ),
    },
}


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


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _one_csv_row(path: Path, key: str, value: str) -> dict[str, str]:
    rows = [row for row in _csv_rows(path) if row.get(key) == value]
    if len(rows) != 1:
        raise PreregistrationError(
            f"Gate 0 source binding expected one {key}={value!r} row in {path}"
        )
    return rows[0]


def _validate_gate0_tracer_sources(tracer: Mapping[str, Any]) -> None:
    observations = tracer.get("observations", [])
    if not isinstance(observations, list) or len(observations) != 2:
        raise PreregistrationError("Gate 0 tracer must bind exactly two source rows")
    pressure, speciation = observations
    pressure_sources = EXPECTED_TRACER_SOURCES["pressure"]
    speciation_sources = EXPECTED_TRACER_SOURCES["speciation"]
    for sources in (pressure_sources, speciation_sources):
        for path_key, hash_key in (
            ("canonical_path", "canonical_sha256"),
            ("raw_path", "raw_sha256"),
            ("manifest_path", "manifest_sha256"),
        ):
            path = GATE0_REPO_ROOT / sources[path_key]
            if _file_sha256(path) != sources[hash_key]:
                raise PreregistrationError(f"Gate 0 tracer source artifact drifted: {path}")

    pressure_canonical = _one_csv_row(
        GATE0_REPO_ROOT / pressure_sources["canonical_path"],
        "observation_id",
        "vle_obs_0137",
    )
    pressure_metrology = _one_csv_row(
        GATE0_REPO_ROOT / pressure_sources["manifest_path"],
        "observation_id",
        "vle_obs_0137",
    )
    pressure_raw = _csv_rows(GATE0_REPO_ROOT / pressure_sources["raw_path"])[30]
    pressure_source_kpa = float(pressure_canonical["CO2_pressure"])
    pressure_value_pa = pressure_source_kpa * 1000.0
    if (
        pressure.get("source_file") != pressure_sources["canonical_path"]
        or pressure.get("source_file_sha256") != pressure_sources["canonical_sha256"]
        or pressure.get("canonical_record_id") != "vle_obs_0137"
        or pressure.get("raw_source_file") != pressure_sources["raw_path"]
        or pressure.get("raw_source_file_sha256") != pressure_sources["raw_sha256"]
        or pressure.get("raw_source_row_index") != 31
        or pressure.get("metrology_manifest") != pressure_sources["manifest_path"]
        or pressure.get("metrology_manifest_sha256")
        != pressure_sources["manifest_sha256"]
        or pressure_canonical.get("source_key") != "Hilliard2008"
        or pressure_canonical.get("source_file") != "Hilliard_2008_VLE.csv"
        or pressure_canonical.get("source_row") != "31"
        or pressure_canonical.get("active_row_id") != "vle_0036"
        or pressure_canonical.get("active_view_member") != "yes"
        or float(pressure_canonical["MEA_weight_fraction"]) != 0.3
        or float(pressure_canonical["temperature_canonical_C"]) != 40.0
        or float(pressure_canonical["CO2_loading"]) != 0.466
        or pressure_source_kpa != 0.574
        or float(pressure_canonical["total_pressure"]) != 7.3267
        or pressure_raw != {
            "MEA_weight_fraction": "0.3",
            "temperature": "40",
            "CO2_loading": "0.466",
            "CO2_pressure": "0.574",
            "MEA_pressure": "0.0027",
            "H2O_pressure": "6.75",
            "total_pressure": "7.3267",
        }
        or pressure_metrology.get("measurement_origin")
        != "calibration_derived_partial_pressure"
        or pressure_metrology.get("observed_pco2_kpa") != "0.574"
        or pressure_metrology.get("state_pressure_pa") != "7326.7"
        or pressure_metrology.get("pressure_specification")
        != "row_reported_total_pressure"
        or pressure_metrology.get("target_eligible") != "yes"
        or pressure.get("source_observed_value") != pressure_source_kpa
        or pressure.get("source_observed_unit") != "kPa"
        or pressure.get("source_to_residual_factor") != 1000.0
        or pressure.get("observed_value") != pressure_value_pa
        or pressure.get("observed_unit") != "Pa"
        or pressure.get("state_pressure_pa")
        != float(pressure_metrology["state_pressure_pa"])
    ):
        raise PreregistrationError("Gate 0 pressure source row or unit conversion drifted")

    speciation_canonical = _one_csv_row(
        GATE0_REPO_ROOT / speciation_sources["canonical_path"],
        "record_id",
        "cheq_canon_00194",
    )
    speciation_membership = _one_csv_row(
        GATE0_REPO_ROOT / speciation_sources["manifest_path"],
        "membership_id",
        "Bottinger2008_state_049|MEACOO-",
    )
    speciation_raw = _csv_rows(GATE0_REPO_ROOT / speciation_sources["raw_path"])[48]
    if (
        speciation.get("source_file") != speciation_sources["canonical_path"]
        or speciation.get("source_file_sha256")
        != speciation_sources["canonical_sha256"]
        or speciation.get("canonical_record_id") != "cheq_canon_00194"
        or speciation.get("raw_source_file") != speciation_sources["raw_path"]
        or speciation.get("raw_source_file_sha256")
        != speciation_sources["raw_sha256"]
        or speciation.get("raw_source_row_index") != 49
        or speciation.get("membership_manifest")
        != speciation_sources["manifest_path"]
        or speciation.get("membership_manifest_sha256")
        != speciation_sources["manifest_sha256"]
        or speciation_canonical.get("source_key") != "Bottinger2008"
        or speciation_canonical.get("source_row_index") != "49"
        or speciation_canonical.get("species") != "MEACOO-"
        or speciation_canonical.get("measurement_role") != "direct_positive"
        or speciation_canonical.get("reported_value") != "0.0502"
        or speciation_canonical.get("reported_unit") != "mole_fraction"
        or speciation_raw.get("MEACOO^-") != "0.0502"
        or speciation_membership.get("measurement_identity") != "cheq_canon_00194"
        or speciation_membership.get("reported_basis") != "mole_fraction"
        or speciation_membership.get("target_eligible") != "yes"
        or speciation.get("observed_value") != 0.0502
        or speciation.get("reported_basis") != "mole_fraction"
        or speciation.get("observed_unit") != "mole_fraction"
    ):
        raise PreregistrationError("Gate 0 speciation source row or unit drifted")


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


def load_gate0_preregistration(
    path: Path = GATE0_PREREGISTRATION_PATH,
) -> dict[str, Any]:
    return validate_gate0_preregistration(load_preregistration(path))


def validate_gate0_preregistration(payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    if (
        payload.get("schema_version") != 2
        or payload.get("identity") != "mea-gate0-v2-mixed-observation-preregistration"
        or payload.get("status") != "GATE_0_FROZEN_EXECUTION_BLOCKED"
    ):
        raise PreregistrationError("Gate 0 v2 preregistration identity is invalid")
    coordinates = payload.get("active_coordinates", [])
    expected = (
        ("MEAH+::sigma", 3.48508556586, [2.0, 5.8], 1.9),
        ("MEAH+::epsilon_over_k", 232.687201645, [50.0, 950.0], 450.0),
        ("MEACOO-::sigma", 3.53543525721, [2.0, 5.8], 1.9),
    )
    actual = tuple(
        (
            row.get("identity"),
            row.get("start"),
            row.get("bounds"),
            row.get("affine_scale"),
        )
        for row in coordinates
    )
    if actual != expected:
        raise PreregistrationError("Gate 0 active coordinate order or scaling drifted")
    if payload.get("state_partition", {}).get("grouped_split_sha256") != (
        "af205ad5968667cf25dc9205d780738035769664a94cc9a421cd3c67148ff804"
    ):
        raise PreregistrationError("Gate 0 grouped split identity drifted")
    if payload.get("execution_admission", {}).get("admitted") is not False:
        raise PreregistrationError("Gate 0 must not admit regression execution")
    if payload.get("regularization", {}).get("scale") is not None:
        raise PreregistrationError("Gate 0 may not invent a regularization scale")
    tracer = payload.get("tracer", {})
    observations = tracer.get("observations", [])
    _validate_gate0_tracer_sources(tracer)
    tracer_coordinates = [
        {
            "identity": "MEAH+::sigma",
            "unit": "angstrom",
            "start": 3.48508556586,
            "bounds": [2.0, 5.8],
            "affine_origin": 3.48508556586,
            "affine_scale": 1.9,
        },
        {
            "identity": "MEACOO-::sigma",
            "unit": "angstrom",
            "start": 3.53543525721,
            "bounds": [2.0, 5.8],
            "affine_origin": 3.53543525721,
            "affine_scale": 1.9,
        },
    ]
    expected_residual_vector = {
        "order": [
            "vle_obs_0137::pco2",
            "Bottinger2008_state_049::MEACOO-",
        ],
        "definition": [
            "log10(predicted_pco2_pa/574.0)/1.0",
            "log10(predicted_meacoo_mole_fraction/0.0502)/1.0",
        ],
        "jacobian_columns": ["MEAH+::sigma", "MEACOO-::sigma"],
    }
    expected_numerical_acceptance = {
        "rank": 2,
        "condition_number_kind": "singular_value_2_norm",
        "maximum_condition_number": 1_000_000.0,
        "active_bound_margin_affine": 1.0e-7,
        "active_bound_rule": (
            "reject if either fitted affine coordinate is within 1e-7 "
            "of either affine bound"
        ),
        "declared_starts": [
            {
                "role": "primary",
                "affine_coordinates": [0.0, 0.0],
                "parameter_values": [3.48508556586, 3.53543525721],
            },
            {
                "role": "confirmation",
                "affine_coordinates": [-0.5, 0.5],
                "parameter_values": [2.53508556586, 4.48543525721],
            },
        ],
        "confirmation_rule": {
            "maximum_affine_parameter_infinity_norm": 1.0e-6,
            "maximum_residual_vector_infinity_norm": 1.0e-8,
            "require_same_active_set": True,
        },
        "required_row_accounting": {
            "input": 2,
            "evaluated": 2,
            "dropped": 0,
            "skipped": 0,
            "failed": 0,
        },
        "failure_rule": (
            "any rank, conditioning, active-bound, confirmation, "
            "or row-accounting failure rejects the tracer"
        ),
    }
    owner_reference = {
        "path": (
            "data/reference/MEA/manifests/"
            "homogeneous_speciation_sentinel_contract.json"
        ),
        "identity": "mea-homogeneous-fixed-tp-sentinel-contract-v1",
        "field": "provider_regression_input",
    }
    provider_input = tracer.get("provider_regression_input", {})
    owner = provider_input.get("canonical_owner", {})
    owner_contract = json.loads(
        (GATE0_REPO_ROOT / owner_reference["path"]).read_text(encoding="utf-8")
    )
    owner_input = owner_contract.get(owner_reference["field"], {})
    if (
        tracer.get("status")
        != "FROZEN_PROVIDER_INPUT_EXECUTABLE_EQUILIBRIUM_PENDING"
        or tracer.get("selected_state_ids")
        != ["vle_obs_0137", "Bottinger2008_state_049"]
        or tracer.get("active_coordinates") != tracer_coordinates
        or [row.get("state_id") for row in observations]
        != ["vle_obs_0137", "Bottinger2008_state_049"]
        or tracer.get("regularization")
        != {"status": "NOT_REQUIRED_FOR_REDUCED_TRACER", "scale": None}
        or observations[1].get("paired_pressure_observation_id")
        != "vle_obs_0137"
        or observations[1].get("search_bounds_pa") != [6105.45, 300_000.0]
        or observations[0].get("residual") != "log10(predicted_pco2_pa/574.0)"
        or observations[0].get("residual_scale") != 1.0
        or observations[1].get("residual")
        != "log10(predicted_meacoo_mole_fraction/0.0502)"
        or observations[1].get("residual_scale") != 1.0
        or tracer.get("residual_vector") != expected_residual_vector
        or tracer.get("numerical_acceptance") != expected_numerical_acceptance
        or provider_input.get("status") != "REGRESSION_INPUT_EXECUTABLE"
        or owner != owner_reference
        or owner_contract.get("identity") != owner_reference["identity"]
        or owner_input.get("identity") != "mea-nine-species-regression-input-v1"
        or owner_input.get("status") != "REGRESSION_INPUT_EXECUTABLE"
        or provider_input.get("domain_fingerprint")
        != owner_input.get("immutable_identities", {}).get("domain_fingerprint")
        or owner_input.get("immutable_identities", {}).get("temperature_k")
        != [313.15, 313.15]
    ):
        raise PreregistrationError("Gate 0 tracer evidence or typed blocker drifted")
    blockers = payload.get("execution_admission", {}).get("blockers", [])
    if (
        blockers
        != [
            "equilibrium_coupled_derivative_receipt_missing",
            "regression_mixed_observation_receipt_missing",
            "tracer_rank_preflight_pending",
        ]
    ):
        raise PreregistrationError("Gate 0 execution blockers are inconsistent")
    actual_sha256 = canonical_sha256(payload)
    if actual_sha256 != EXPECTED_GATE0_CANONICAL_SHA256:
        raise PreregistrationError(
            f"Gate 0 frozen contract drifted: expected {EXPECTED_GATE0_CANONICAL_SHA256}, "
            f"actual {actual_sha256}"
        )
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
