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
