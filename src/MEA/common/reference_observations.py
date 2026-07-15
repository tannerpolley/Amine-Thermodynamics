from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any


MEASUREMENT_ROLES = frozenset(
    {
        "direct_positive",
        "direct_zero",
        "below_detection",
        "aggregate_direct_positive",
        "aggregate_direct_zero",
        "balance_inferred",
        "model_derived",
        "analog",
        "ambiguous",
    }
)

LIFECYCLE_STATUSES = frozenset(
    {
        "raw",
        "qa_pending",
        "canonical_eligible",
        "validation_reserved",
        "diagnostic_only",
        "excluded",
    }
)

REQUIRED_PROVENANCE_FIELDS = (
    "record_id",
    "source_key",
    "source_file",
    "source_locator",
    "data_family",
    "observed_quantity",
    "phase",
)

UNCERTAINTY_FIELDS = (
    "uncertainty_value",
    "uncertainty_type",
    "uncertainty_coverage",
)


@dataclass(frozen=True)
class ObservationValidationReport:
    ok: bool
    row_count: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, float):
        return math.isnan(value)
    return False


def validate_observation_records(
    rows: Sequence[Mapping[str, Any]],
    family: str,
) -> ObservationValidationReport:
    """Validate provenance and evidence semantics without changing source rows."""
    if not family.strip():
        raise ValueError("family must be a non-empty string")

    errors: list[str] = []
    warnings: list[str] = []
    for index, row in enumerate(rows, start=1):
        prefix = f"row {index}"
        for field in REQUIRED_PROVENANCE_FIELDS:
            if _is_missing(row.get(field)):
                errors.append(f"{prefix}: {field} is required")

        row_family = row.get("data_family")
        if not _is_missing(row_family) and str(row_family) != family:
            errors.append(f"{prefix}: data_family {row_family!r} does not match {family!r}")

        role = row.get("measurement_role")
        if role not in MEASUREMENT_ROLES:
            errors.append(f"{prefix}: invalid measurement_role {role!r}")

        status = row.get("lifecycle_status")
        if status not in LIFECYCLE_STATUSES:
            errors.append(f"{prefix}: invalid lifecycle_status {status!r}")

        reported_value = row.get("value_reported")
        normalized_value = row.get("value_normalized")
        if not _is_missing(normalized_value):
            if _is_missing(reported_value) or _is_missing(row.get("reported_basis")):
                errors.append(f"{prefix}: normalized value requires reported value and basis")
            if _is_missing(row.get("normalization_method")):
                errors.append(f"{prefix}: normalized value requires a normalization method")

        uncertainty_value = row.get("uncertainty_value")
        if not _is_missing(uncertainty_value) and _is_missing(row.get("uncertainty_type")):
            errors.append(f"{prefix}: uncertainty value requires uncertainty type")

        if role in {
            "direct_positive",
            "direct_zero",
            "below_detection",
            "aggregate_direct_positive",
            "aggregate_direct_zero",
        } and _is_missing(reported_value):
            errors.append(f"{prefix}: direct measurement role requires a reported value")

        if status == "excluded" and _is_missing(row.get("exclusion_reason")):
            errors.append(f"{prefix}: excluded lifecycle status requires an exclusion reason")

        if _is_missing(uncertainty_value) and row.get("uncertainty_coverage") == "not_reported":
            warnings.append(f"{prefix}: source does not report measurement uncertainty")

    return ObservationValidationReport(
        ok=not errors,
        row_count=len(rows),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _source_locator(row: Mapping[str, Any]) -> str:
    table = str(row.get("source_table_or_figure", "")).strip()
    line_start = str(row.get("source_line_start", "")).strip()
    line_end = str(row.get("source_line_end", "")).strip()
    source_row = str(row.get("source_row") or row.get("source_row_index", "")).strip()
    parts = [part for part in (table, f"lines {line_start}-{line_end}" if line_start else "", f"row {source_row}" if source_row else "") if part]
    return ", ".join(parts) or "source table row retained in repository artifact"


def adapt_speciation_rows(
    rows: Sequence[Mapping[str, Any]], *, source_file: str
) -> list[dict[str, Any]]:
    adapted: list[dict[str, Any]] = []
    for row in rows:
        normalized = row.get("value_mole_fraction", "")
        normalization_method = ""
        if not _is_missing(normalized):
            normalization_method = str(row.get("conversion_basis", "")).strip()
            if not normalization_method and row.get("reported_basis") == "mole_fraction":
                normalization_method = "reported mole fraction retained"
        adapted.append(
            {
                "record_id": row.get("record_id"),
                "source_key": row.get("source_key"),
                "source_file": source_file,
                "source_locator": _source_locator(row),
                "data_family": "speciation",
                "observed_quantity": "liquid species composition",
                "species": row.get("species"),
                "phase": "liquid",
                "value_reported": row.get("reported_value"),
                "reported_unit": row.get("reported_unit"),
                "reported_basis": row.get("reported_basis"),
                "value_normalized": normalized,
                "normalization_method": normalization_method,
                "uncertainty_value": "",
                "uncertainty_type": "",
                "uncertainty_coverage": "not_reported",
                "measurement_role": row.get("measurement_role"),
                "lifecycle_status": row.get("lifecycle_status"),
                "replicate_group": "",
                "normalization_group": "",
                "exclusion_reason": "",
                "reviewer_decision": row.get("target_membership", ""),
            }
        )
    return adapted


def adapt_vle_pressure_rows(
    rows: Sequence[Mapping[str, Any]], *, source_file: str
) -> list[dict[str, Any]]:
    status_map = {
        "active_v1": "canonical_eligible",
        "validation_reserved_candidate": "validation_reserved",
        "qa_pending_domain_review": "qa_pending",
    }
    return [
        {
            "record_id": row.get("observation_id"),
            "source_key": row.get("source_key"),
            "source_file": source_file,
            "source_locator": _source_locator(row),
            "data_family": "vle_pressure",
            "observed_quantity": "CO2 partial pressure over loaded MEA",
            "phase": "vapor-liquid-equilibrium",
            "value_reported": row.get("CO2_pressure"),
            "reported_unit": "kPa",
            "reported_basis": "CO2 partial pressure",
            "value_normalized": "",
            "normalization_method": "",
            "uncertainty_value": row.get("CO2_pressure_uncertainty", ""),
            "uncertainty_type": "reported_absolute" if not _is_missing(row.get("CO2_pressure_uncertainty")) else "",
            "uncertainty_coverage": "reported" if not _is_missing(row.get("CO2_pressure_uncertainty")) else "not_reported",
            "measurement_role": "direct_positive",
            "lifecycle_status": status_map.get(str(row.get("lifecycle_status")), "qa_pending"),
            "replicate_group": row.get("replicate_group", ""),
            "normalization_group": row.get("normalization_group", ""),
            "exclusion_reason": row.get("disposition_reason", "") if row.get("lifecycle_status") == "excluded" else "",
            "reviewer_decision": row.get("disposition_reason", ""),
        }
        for row in rows
    ]


def adapt_loaded_property_rows(
    rows: Sequence[Mapping[str, Any]], *, source_file: str
) -> list[dict[str, Any]]:
    status_map = {"property_target_candidate": "qa_pending", "validation_only": "diagnostic_only"}
    adapted: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        uncertainty = row.get("uncertainty_value", "")
        adapted.append(
            {
                "record_id": f"{row.get('source_key')}|{row.get('property')}|{index:04d}",
                "source_key": row.get("source_key"),
                "source_file": source_file,
                "source_locator": _source_locator(row),
                "data_family": "loaded_property",
                "observed_quantity": row.get("property"),
                "phase": "liquid",
                "value_reported": row.get("value"),
                "reported_unit": row.get("value_unit"),
                "reported_basis": "loaded MEA solution",
                "value_normalized": "",
                "normalization_method": "",
                "uncertainty_value": uncertainty,
                "uncertainty_type": row.get("uncertainty_type", "") if not _is_missing(uncertainty) else "",
                "uncertainty_coverage": "reported" if not _is_missing(uncertainty) else "not_reported",
                "measurement_role": row.get("measurement_role"),
                "lifecycle_status": status_map.get(str(row.get("lifecycle_status")), "qa_pending"),
                "replicate_group": "",
                "normalization_group": "",
                "exclusion_reason": "",
                "reviewer_decision": row.get("notes", ""),
            }
        )
    return adapted


def adapt_paired_loading_rows(
    rows: Sequence[Mapping[str, Any]], *, source_file: str
) -> list[dict[str, Any]]:
    status_map = {"validation_candidate": "validation_reserved", "non_capacity_batch_observation": "diagnostic_only"}
    adapted: list[dict[str, Any]] = []
    for row in rows:
        for method in ("calculated", "predicted"):
            adapted.append(
                {
                    "record_id": f"{row.get('record_id')}|{method}",
                    "source_key": row.get("source_key"),
                    "source_file": source_file,
                    "source_locator": _source_locator(row),
                    "data_family": "loading_cross_method",
                    "observed_quantity": f"CO2 loading ({row.get(f'{method}_method')})",
                    "phase": "liquid",
                    "value_reported": row.get(f"{method}_loading"),
                    "reported_unit": row.get("loading_unit"),
                    "reported_basis": "mol CO2 per mol MEA",
                    "value_normalized": "",
                    "normalization_method": "",
                    "uncertainty_value": "",
                    "uncertainty_type": "",
                    "uncertainty_coverage": "not_reported",
                    "measurement_role": "direct_positive",
                    "lifecycle_status": status_map.get(str(row.get("lifecycle_status")), "qa_pending"),
                    "replicate_group": row.get("record_id"),
                    "normalization_group": "",
                    "exclusion_reason": "",
                    "reviewer_decision": row.get("caveat", ""),
                }
            )
    return adapted
