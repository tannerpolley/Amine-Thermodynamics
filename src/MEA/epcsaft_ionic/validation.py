from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from MEA.epcsaft_ionic import native_regression
from MEA.epcsaft_ionic.model import (
    FIT_DATASET_DIR,
    DEFAULT_INITIAL_GUESS,
    SPECIES_INDEX,
    load_speciation_targets,
    load_vle_targets,
    reactive_bubble_acceptance,
    solve_activity_speciation,
    solve_reactive_bubble_targets,
    write_csv,
    write_json,
)
from MEA.epcsaft_ionic.preregistration import canonical_sha256


class ValidationContractError(RuntimeError):
    """Raised when held-out validation evidence violates its frozen contract."""


@dataclass(frozen=True)
class ValidatedCandidate:
    sha256: str
    preregistration_sha256: str
    fit_parameter_names: tuple[str, ...]
    values: dict[str, float]


@dataclass(frozen=True)
class ReservedValidationContract:
    rows: tuple[dict[str, Any], ...]
    record_ids: tuple[str, ...]
    target_counts: dict[str, int]
    row_splits: dict[str, str]
    validation_groups: dict[str, frozenset[str]]
    training_groups: dict[str, frozenset[str]]
    split_hash: str
    target_role: str = "reserved_validation"

    @classmethod
    def for_testing(cls, *, rows: tuple[dict[str, Any], ...]) -> ReservedValidationContract:
        normalized = tuple(dict(row) for row in rows)
        record_ids = tuple(str(row["record_id"]) for row in normalized)
        return cls(
            rows=normalized,
            record_ids=record_ids,
            target_counts={
                family: sum(str(row["target_family"]) == family for row in normalized)
                for family in ("pressure", "speciation")
            },
            row_splits={record_id: "validation" for record_id in record_ids},
            validation_groups={"pressure": frozenset(), "speciation": frozenset()},
            training_groups={"pressure": frozenset(), "speciation": frozenset()},
            split_hash="test-split",
        )


def validate_candidate_summary(
    summary: Mapping[str, Any],
    *,
    approval: Mapping[str, Any],
    preregistration_sha256: str,
    parameter_names: Iterable[str],
) -> ValidatedCandidate:
    names = tuple(parameter_names)
    candidate_sha256 = canonical_sha256(summary)
    if summary.get("completion_status") != "completed":
        raise ValidationContractError("candidate fit is not completed")
    if summary.get("selected_parameter_set") != "global_regression":
        raise ValidationContractError("candidate parameter set was not promoted")
    if tuple(summary.get("fit_parameters", ())) != names:
        raise ValidationContractError("candidate parameter order differs from preregistration")
    if summary.get("preregistration_sha256") != preregistration_sha256:
        raise ValidationContractError("candidate preregistration hash differs from the validated contract")
    native = summary.get("native_regression_summary")
    if not isinstance(native, dict) or native.get("fit_success") is not True or native.get("failure_count") != 0:
        raise ValidationContractError("candidate native fit diagnostics are incomplete or unsuccessful")
    if approval.get("approved") is not True:
        raise ValidationContractError("candidate promotion was not approved")
    if approval.get("preregistration_sha256") != preregistration_sha256:
        raise ValidationContractError("approval preregistration hash differs from the validated contract")
    if approval.get("candidate_sha256") != candidate_sha256:
        raise ValidationContractError("candidate summary hash differs from its approval receipt")

    selected = summary.get("selected_values")
    if not isinstance(selected, dict) or set(selected) != set(DEFAULT_INITIAL_GUESS):
        raise ValidationContractError("candidate selected values do not cover the complete thermodynamic parameter map")
    values: dict[str, float] = {}
    for name in DEFAULT_INITIAL_GUESS:
        try:
            value = float(selected[name])
        except (TypeError, ValueError) as exc:
            raise ValidationContractError(f"candidate parameter {name!r} is not numeric") from exc
        if not math.isfinite(value):
            raise ValidationContractError(f"candidate parameter {name!r} is not finite")
        values[name] = value
    return ValidatedCandidate(
        sha256=candidate_sha256,
        preregistration_sha256=preregistration_sha256,
        fit_parameter_names=names,
        values=values,
    )


def _family(row: Mapping[str, Any]) -> str:
    family = str(row.get("metadata", {}).get("target_family", ""))
    if family not in {"pressure", "speciation"}:
        raise ValidationContractError(f"unsupported validation target family {family!r}")
    return family


def _target_count(row: Mapping[str, Any], family: str) -> int:
    if family == "pressure":
        return len(row.get("targets", {}).get("partial_pressures", {}))
    direct = len(row.get("targets", {}).get("speciation", {}))
    aggregate = len(row.get("metadata", {}).get("aggregate_targets", {}))
    zero_bounds = len(row.get("zero_upper_bound_species", ()))
    return direct + aggregate + zero_bounds


def build_reserved_validation_contract() -> ReservedValidationContract:
    training = native_regression.build_native_regression_problem(target_role="active_training")
    reserved = native_regression.build_native_regression_problem(target_role="reserved_validation")
    if reserved.metadata.get("target_role") != "reserved_validation":
        raise ValidationContractError("native validation problem is not reserved-validation only")

    rows: list[dict[str, Any]] = []
    record_ids: list[str] = []
    row_splits: dict[str, str] = {}
    validation_groups: dict[str, set[str]] = {"pressure": set(), "speciation": set()}
    training_groups: dict[str, set[str]] = {"pressure": set(), "speciation": set()}
    for row in training.rows:
        family = _family(row)
        training_groups[family].add(str(row["metadata"]["group_id"]))
    for row in reserved.rows:
        family = _family(row)
        record_id = str(row["row_id"])
        split = str(row.get("split", ""))
        if split != "validation":
            raise ValidationContractError(f"reserved record {record_id!r} is not in the validation split")
        count = _target_count(row, family)
        if count <= 0:
            raise ValidationContractError(f"reserved record {record_id!r} has no accounted target observation")
        rows.append(
            {
                "record_id": record_id,
                "target_family": family,
                "source": str(row.get("source", "")),
                "target_count": count,
                "group_id": str(row["metadata"]["group_id"]),
            }
        )
        record_ids.append(record_id)
        row_splits[record_id] = split
        validation_groups[family].add(str(row["metadata"]["group_id"]))

    if len(record_ids) != len(set(record_ids)):
        raise ValidationContractError("reserved validation record identifiers are not unique")
    target_counts = {
        "pressure": int(reserved.metadata["pressure_row_count"]),
        "speciation": int(reserved.metadata["speciation_row_count"]),
    }
    if target_counts != {"pressure": 167, "speciation": 53} or len(record_ids) != 220:
        raise ValidationContractError("reserved validation state counts differ from the frozen 167/53 contract")
    for family in ("pressure", "speciation"):
        overlap = validation_groups[family].intersection(training_groups[family])
        if overlap:
            raise ValidationContractError(f"training/validation group leakage for {family}: {sorted(overlap)}")
    if reserved.metadata.get("split_hash") != training.metadata.get("split_hash"):
        raise ValidationContractError("training and validation problems use different split hashes")

    return ReservedValidationContract(
        rows=tuple(rows),
        record_ids=tuple(record_ids),
        target_counts=target_counts,
        row_splits=row_splits,
        validation_groups={family: frozenset(groups) for family, groups in validation_groups.items()},
        training_groups={family: frozenset(groups) for family, groups in training_groups.items()},
        split_hash=str(reserved.metadata["split_hash"]),
    )


def _failure_record(
    *,
    record_id: str,
    family: str,
    source: str,
    group_id: str,
    target_count: int,
    reason: str,
    observed: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "target_family": family,
        "source": source,
        "group_id": group_id,
        "split": "validation",
        "role": "reserved_validation",
        "status": "failed_prediction",
        "failure_reason": reason,
        "target_count": target_count,
        "evaluated_target_count": 0,
        "failed_target_count": target_count,
        "log10_residuals": [],
        "observed": dict(observed),
        "predicted": {},
    }


def evaluate_reserved_predictions(values: Mapping[str, float]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    pressure_targets = load_vle_targets(role="reserved_validation")
    pressure_results = solve_reactive_bubble_targets(pressure_targets, dict(values), FIT_DATASET_DIR)
    for target, result in zip(pressure_targets, pressure_results):
        observed_pa = float(target.pressure_kPa) * 1000.0
        observed = {"CO2_partial_pressure_Pa": observed_pa}
        try:
            if isinstance(result, Exception):
                raise result
            predicted_pa = float(result.partial_pressures.get("CO2", np.nan))
            decision = reactive_bubble_acceptance(result)
            if not decision.accepted or not np.isfinite(predicted_pa) or predicted_pa <= 0.0:
                raise RuntimeError(decision.rejection_reason or str(result.message))
            records.append(
                {
                    "record_id": target.row_id,
                    "target_family": "pressure",
                    "source": target.source_key,
                    "group_id": target.group_id,
                    "split": "validation",
                    "role": "reserved_validation",
                    "status": "success",
                    "failure_reason": "",
                    "target_count": 1,
                    "evaluated_target_count": 1,
                    "failed_target_count": 0,
                    "log10_residuals": [math.log10(predicted_pa / observed_pa)],
                    "observed": observed,
                    "predicted": {"CO2_partial_pressure_Pa": predicted_pa},
                }
            )
        except Exception as exc:
            records.append(
                _failure_record(
                    record_id=target.row_id,
                    family="pressure",
                    source=target.source_key,
                    group_id=target.group_id,
                    target_count=1,
                    reason=f"{type(exc).__name__}: {str(exc).splitlines()[0]}",
                    observed=observed,
                )
            )

    for target in load_speciation_targets(role="reserved_validation"):
        observed: dict[str, float] = dict(target.target_speciation)
        observed.update(target.aggregate_targets)
        observed.update({f"{species}__upper_bound": 0.0 for species in target.zero_upper_bound_species})
        target_count = len(observed)
        try:
            prediction = solve_activity_speciation(target.loading, target.T, target.P, target.x, dict(values), FIT_DATASET_DIR)
            if not prediction.accepted:
                raise RuntimeError(prediction.rejection_reason or prediction.message)
            predicted: dict[str, float] = {
                species: float(prediction.x[SPECIES_INDEX[species]])
                for species in target.target_speciation
            }
            if "MEA + MEAH+" in target.aggregate_targets:
                predicted["MEA + MEAH+"] = float(
                    prediction.x[SPECIES_INDEX["MEA"]] + prediction.x[SPECIES_INDEX["MEAH+"]]
                )
            predicted.update(
                {
                    f"{species}__upper_bound": float(prediction.x[SPECIES_INDEX[species]])
                    for species in target.zero_upper_bound_species
                }
            )
            if len(predicted) != target_count or not all(np.isfinite(value) for value in predicted.values()):
                raise RuntimeError("validation prediction is incomplete or nonfinite")
            residuals = [
                math.log10(max(predicted[name], 1.0e-30) / value)
                for name, value in {**target.target_speciation, **target.aggregate_targets}.items()
                if value > 0.0
            ]
            records.append(
                {
                    "record_id": target.row_id,
                    "target_family": "speciation",
                    "source": target.source,
                    "group_id": target.group_id,
                    "split": "validation",
                    "role": "reserved_validation",
                    "status": "success",
                    "failure_reason": "",
                    "target_count": target_count,
                    "evaluated_target_count": target_count,
                    "failed_target_count": 0,
                    "log10_residuals": residuals,
                    "observed": observed,
                    "predicted": predicted,
                }
            )
        except Exception as exc:
            records.append(
                _failure_record(
                    record_id=target.row_id,
                    family="speciation",
                    source=target.source,
                    group_id=target.group_id,
                    target_count=target_count,
                    reason=f"{type(exc).__name__}: {str(exc).splitlines()[0]}",
                    observed=observed,
                )
            )
    return records


def _validate_prediction_accounting(
    records: list[dict[str, Any]],
    contract: ReservedValidationContract,
) -> None:
    expected = {str(row["record_id"]): row for row in contract.rows}
    actual: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for record in records:
        record_id = str(record.get("record_id", ""))
        if record_id in actual:
            duplicates.append(record_id)
        actual[record_id] = record
    if duplicates:
        raise ValidationContractError(f"duplicate reserved records: {sorted(set(duplicates))}")
    missing = sorted(set(expected).difference(actual))
    extra = sorted(set(actual).difference(expected))
    if missing:
        raise ValidationContractError(f"missing reserved records: {missing}")
    if extra:
        raise ValidationContractError(f"unexpected validation records: {extra}")

    for record_id, record in actual.items():
        expected_row = expected[record_id]
        if record.get("target_family") != expected_row["target_family"] or record.get("source") != expected_row["source"]:
            raise ValidationContractError(f"reserved record identity drift for {record_id}")
        if record.get("split") != "validation" or record.get("role") != "reserved_validation":
            raise ValidationContractError(f"reserved record role drift for {record_id}")
        status = record.get("status")
        if status not in {"success", "failed_prediction"}:
            raise ValidationContractError(f"invalid prediction status for {record_id}")
        target_count = int(record.get("target_count", -1))
        evaluated = int(record.get("evaluated_target_count", -1))
        failed = int(record.get("failed_target_count", -1))
        if target_count != int(expected_row["target_count"]) or evaluated + failed != target_count:
            raise ValidationContractError(f"target accounting drift for {record_id}")
        if status == "success" and (failed != 0 or record.get("failure_reason")):
            raise ValidationContractError(f"successful record has failure accounting for {record_id}")
        if status == "failed_prediction" and (failed != target_count or not record.get("failure_reason")):
            raise ValidationContractError(f"failed record is not fully accounted for {record_id}")
        residuals = record.get("log10_residuals")
        if not isinstance(residuals, list) or len(residuals) > evaluated:
            raise ValidationContractError(f"residual accounting drift for {record_id}")
        if not all(math.isfinite(float(value)) for value in residuals):
            raise ValidationContractError(f"nonfinite validation residual for {record_id}")


def _metric_row(family: str, source: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    residuals = np.asarray(
        [float(value) for record in records for value in record["log10_residuals"]],
        dtype=float,
    )
    return {
        "target_family": family,
        "source": source,
        "state_count": len(records),
        "successful_state_count": sum(record["status"] == "success" for record in records),
        "failed_state_count": sum(record["status"] == "failed_prediction" for record in records),
        "target_observation_count": sum(int(record["target_count"]) for record in records),
        "evaluated_target_observation_count": sum(int(record["evaluated_target_count"]) for record in records),
        "failed_target_observation_count": sum(int(record["failed_target_count"]) for record in records),
        "scored_residual_count": int(residuals.size),
        "median_abs_log10": float(np.median(np.abs(residuals))) if residuals.size else None,
        "rmse_log10": float(np.sqrt(np.mean(residuals * residuals))) if residuals.size else None,
    }


def summarize_validation_records(
    records: list[dict[str, Any]],
    *,
    contract: ReservedValidationContract,
    candidate_sha256: str,
    preregistration_sha256: str,
    expected_split_hash: str,
    source_hashes: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if contract.split_hash != expected_split_hash:
        raise ValidationContractError("reserved validation split hash differs from preregistration")
    _validate_prediction_accounting(records, contract)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault((str(record["target_family"]), str(record["source"])), []).append(record)
    metrics = [_metric_row(family, source, grouped[(family, source)]) for family, source in sorted(grouped)]
    summary = {
        "schema_version": 1,
        "candidate_sha256": candidate_sha256,
        "preregistration_sha256": preregistration_sha256,
        "split_hash": contract.split_hash,
        "source_hashes": dict(source_hashes),
        "target_role": contract.target_role,
        "target_counts": dict(contract.target_counts),
        "state_count": len(records),
        "successful_state_count": sum(record["status"] == "success" for record in records),
        "failed_state_count": sum(record["status"] == "failed_prediction" for record in records),
        "target_observation_count": sum(int(record["target_count"]) for record in records),
        "evaluated_target_observation_count": sum(int(record["evaluated_target_count"]) for record in records),
        "failed_target_observation_count": sum(int(record["failed_target_count"]) for record in records),
        "failure_accounting_complete": True,
        "claim_boundary": (
            "Held-out prediction accounting is complete. Predictive-validity and identifiability claims require "
            "the preregistered acceptance decision and candidate-bound sensitivity receipt."
        ),
    }
    return summary, metrics


def write_validation_bundle(
    *,
    records: list[dict[str, Any]],
    summary: Mapping[str, Any],
    metrics: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_records = []
    for record in records:
        row = dict(record)
        for key in ("observed", "predicted", "log10_residuals"):
            row[key] = json.dumps(row[key], sort_keys=True, separators=(",", ":"))
        csv_records.append(row)
    write_csv(output_dir / "validation_predictions.csv", csv_records)
    write_csv(output_dir / "validation_metrics_by_source.csv", metrics)
    write_json(output_dir / "validation_summary.json", dict(summary))
