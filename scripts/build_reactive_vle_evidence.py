from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from MEA.epcsaft_ionic.parameter_document import load_parameters


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data/reference/MEA/manifests"
OUTPUT = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/results/reactive_vle_vertical_slice"
    / "campaign_admission_receipt.json"
)
HOMOGENEOUS_TRACER = OUTPUT.parent / "installed_homogeneous_tracer_receipt.json"
BUBBLE_TRACER = OUTPUT.parent / "installed_reactive_bubble_tracer_receipt.json"
PARAMETER_TABLE = OUTPUT.parent / "diagnostic_parameter_table.csv"
REACTION_TABLE = OUTPUT.parent / "reaction_correlation_table.csv"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _write_parameter_table() -> None:
    fieldnames = (
        "parameter_identity",
        "family",
        "value",
        "unit",
        "fit_role",
        "transform",
        "lower_bound",
        "upper_bound",
        "start_value",
        "fitted_value",
        "source_id",
        "source_locator",
        "domain_id",
    )
    rows = []
    for spec in load_parameters().parameter_specs:
        value = getattr(spec.value, "magnitude", spec.value)
        rows.append(
            {
                "parameter_identity": spec.identity,
                "family": spec.family,
                "value": str(value),
                "unit": spec.unit,
                "fit_role": "fixed_diagnostic_not_promoted",
                "transform": "none",
                "lower_bound": "",
                "upper_bound": "",
                "start_value": "",
                "fitted_value": "",
                "source_id": spec.source_id,
                "source_locator": spec.locator,
                "domain_id": spec.domain_id,
            }
        )
    with PARAMETER_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_reaction_table() -> None:
    contract = json.loads(
        (MANIFESTS / "chemical_reaction_source_contract.json").read_text()
    )
    common = contract["common_source_standard_state"]
    fieldnames = (
        "reaction_id",
        "stoichiometry_in_declared_species_order",
        "correlation_kind",
        "correlation_coefficients",
        "source_record_ids",
        "temperature_min_k",
        "temperature_max_k",
        "activity_convention",
        "standard_molality_mol_per_kg",
        "fit_role",
    )
    rows = []
    for reaction in contract["reactions"]:
        temperature_min, temperature_max = reaction["temperature_range_k"]
        rows.append(
            {
                "reaction_id": reaction["reaction_id"],
                "stoichiometry_in_declared_species_order": json.dumps(
                    reaction["stoichiometry"], separators=(",", ":")
                ),
                "correlation_kind": reaction["correlation"]["kind"],
                "correlation_coefficients": json.dumps(
                    {
                        key: value
                        for key, value in reaction["correlation"].items()
                        if key != "kind"
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                "source_record_ids": ";".join(reaction["source_record_ids"]),
                "temperature_min_k": temperature_min,
                "temperature_max_k": temperature_max,
                "activity_convention": common["identity"],
                "standard_molality_mol_per_kg": common[
                    "solute_standard_molality_mol_per_kg"
                ],
                "fit_role": "retained_source_fixed_not_fitted",
            }
        )
    with REACTION_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_receipt() -> dict[str, object]:
    cross_path = MANIFESTS / "reactive_vle_cross_validation.csv"
    cross = _rows(cross_path)
    identity_fields = (
        "observation_id",
        "observable_family",
        "source_key",
        "source_file_sha256",
        "source_row_identity",
        "campaign_block_id",
        "cross_validation_fold",
        "domain_role",
        "model_selection_role",
        "final_fit_role",
        "admission_status",
        "admission_blockers",
    )
    partition_packet = [
        {field: row[field] for field in identity_fields}
        for row in sorted(cross, key=lambda item: item["observation_id"])
    ]
    family_counts = Counter(row["observable_family"] for row in cross)
    role_counts = Counter(
        (row["observable_family"], row["measurement_role"]) for row in cross
    )
    domain_counts = Counter(
        (row["observable_family"], row["domain_role"]) for row in cross
    )
    blocker_counts: Counter[str] = Counter()
    for row in cross:
        for blocker in row["admission_blockers"].split(";"):
            if blocker.strip():
                blocker_counts[blocker.strip()] += 1

    files = (
        cross_path,
        MANIFESTS / "pco2_metrology_manifest.csv",
        MANIFESTS / "speciation_target_membership.csv",
        MANIFESTS / "chemical_reaction_source_contract.json",
        MANIFESTS / "homogeneous_speciation_sentinel_contract.json",
        MANIFESTS / "reactive_vle_model_configurations.json",
        MANIFESTS / "reactive_vle_parameter_stages.json",
        MANIFESTS / "engine_artifact_lock.json",
        HOMOGENEOUS_TRACER,
        BUBBLE_TRACER,
        PARAMETER_TABLE,
        REACTION_TABLE,
    )
    engine_lock = json.loads((MANIFESTS / "engine_artifact_lock.json").read_text())
    homogeneous_tracer = json.loads(HOMOGENEOUS_TRACER.read_text())
    bubble_tracer = json.loads(BUBBLE_TRACER.read_text())
    models = json.loads(
        (MANIFESTS / "reactive_vle_model_configurations.json").read_text()
    )["configurations"]
    source_pressure = sum(
        row["observable_family"] == "pco2" and bool(row["state_pressure_pa"])
        for row in cross
    )
    executable = sum(row["admission_status"] == "executable" for row in cross)
    result: dict[str, object] = {
        "schema_version": 1,
        "identity": "mea-reactive-vle-campaign-admission-v1",
        "engine": engine_lock,
        "input_packet": {
            "file_hashes": {
                path.relative_to(ROOT).as_posix(): _sha256(path) for path in files
            },
            "candidate_row_count": len(cross),
            "candidate_counts_by_family": dict(sorted(family_counts.items())),
            "candidate_counts_by_family_and_measurement_role": {
                f"{family}|{role}": count
                for (family, role), count in sorted(role_counts.items())
            },
            "candidate_counts_by_family_and_domain_role": {
                f"{family}|{role}": count
                for (family, role), count in sorted(domain_counts.items())
            },
            "rows_with_state_pressure": source_pressure,
            "executable_row_count": executable,
            "partition_packet_sha256": _canonical_sha256(partition_packet),
            "cross_validation_manifest_sha256": _sha256(cross_path),
            "admission_blocker_counts": dict(sorted(blocker_counts.items())),
        },
        "staged_estimation": {
            "S1": "blocked_missing_pure_MEA_measurement_packet_and_source_fixed_moments",
            "S2": "not_started_S1_gate_not_passed",
            "S3": "installed_wheel_diagnostic_tracer_only",
            "S4": "not_started_no_executable_speciation_rows_or_qualified_parameter_block",
            "S5": "not_started_no_executable_reactive_bubble_scoring_rows",
            "S6": "not_started_S5_gate_not_passed",
            "S7": "not_started_no_identifiable_promotable_block",
        },
        "installed_execution_evidence": {
            "homogeneous_reactive_observation": {
                "status": homogeneous_tracer["status"],
                "receipt_sha256": homogeneous_tracer["receipt_sha256"],
                "physical_branch_identity": homogeneous_tracer["state"][
                    "physical_branch_identity"
                ],
                "exact_total_jacobian": homogeneous_tracer["observation"][
                    "exact_raw_total_jacobian"
                ],
            },
            "reactive_bubble_vle": {
                "status": bubble_tracer["status"],
                "failure_code": (
                    None
                    if bubble_tracer["failure"] is None
                    else bubble_tracer["failure"]["code"]
                ),
                "receipt_sha256": bubble_tracer["receipt_sha256"],
                "search": bubble_tracer["search"],
            },
        },
        "model_comparison": [
            {
                "configuration_id": model["configuration_id"],
                "scoring_status": "not_scored",
                "reason": model["execution_status"],
                "training_row_count": 0,
                "cross_validation_row_count": 0,
                "reserved_row_count": 0,
            }
            for model in models
        ],
        "regression_diagnostics": {
            "objective_definition": "not_assembled_zero_admitted_rows",
            "residual_scale_count": 0,
            "family_source_temperature_residual_summaries": "unavailable_no_evaluated_scoring_rows",
            "jacobian_rank": "unavailable_no_regression_jacobian",
            "singular_values": [],
            "condition_estimate": "unavailable_no_regression_jacobian",
            "covariance_or_profile": "unavailable_no_identifiable_fitted_block",
            "active_bounds": [],
            "optimizer_multistart": "not_run_no_objective",
            "numeric_failure_penalties": 0,
        },
        "scoring_metrics": {
            "training": "not_scored",
            "cross_validation": "not_scored",
            "reserved_validation": "untouched_not_scored",
        },
        "promotion_decision": {
            "status": "not_promoted",
            "reason": "no_executable_observation_rows_and_stage_1_not_qualified",
            "fitted_parameters": [],
            "fixed_parameters": "retained diagnostic inputs only; see parameter source audit",
            "manuscript_changed": False,
        },
        "scientific_blockers": [
            "All 319 candidate rows lack a preregistered executable residual scale or uncertainty.",
            "All 198 candidate speciation rows lack a source-backed same-state pressure contract.",
            "The immutable predictive parameter packet required by Stage 1 has not been qualified.",
            "M1-M3 source-fixed molecular moments, M4 induced-association topology, and M5 dielectric/target-ion evidence are absent.",
        ],
        "claim_boundary": (
            "This receipt proves installed Engine integration, immutable candidate partitions, "
            "and a fail-closed scientific decision. It is not a parameter fit, model score, "
            "predictive parameterization, or manuscript result."
        ),
    }
    result["receipt_sha256"] = _canonical_sha256(result)
    return result


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _write_parameter_table()
    _write_reaction_table()
    result = build_receipt()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(OUTPUT.relative_to(ROOT))
    print(result["receipt_sha256"])


if __name__ == "__main__":
    main()
