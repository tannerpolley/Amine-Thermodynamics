from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


PHASE1_MODEL_FAMILY = "legacy_pcsaft_smith_missen"
CANONICAL_IDENTITY_COLUMNS = (
    "temperature_C",
    "MEA_weight_fraction",
    "CO2_loading",
    "observed_CO2_pressure_kPa",
)
UNCERTAINTY_COLUMNS = (
    "CO2_pressure_uncertainty_kPa",
    "pressure_uncertainty_kPa",
    "uncertainty_kPa",
)
ZERO_TARGET_ROLES = frozenset({"direct_zero", "aggregate_direct_zero"})


@dataclass(frozen=True)
class ComparisonBundle:
    paired_rows: pd.DataFrame
    metrics: pd.DataFrame
    uncertainty_coverage: pd.DataFrame
    role_counts: pd.DataFrame
    summary: dict[str, Any]


def _require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def _canonical_frame(canonical_vle: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        canonical_vle,
        {
            "row_id",
            "source_key",
            "temperature",
            "MEA_weight_fraction",
            "CO2_loading",
            "CO2_pressure",
        },
        "canonical VLE data",
    )
    canonical = canonical_vle.rename(
        columns={
            "source_key": "source",
            "temperature": "temperature_C",
            "CO2_pressure": "observed_CO2_pressure_kPa",
        }
    ).copy()
    if canonical["row_id"].duplicated().any():
        raise ValueError("canonical VLE data contain duplicate row_id values")
    if canonical.duplicated(list(CANONICAL_IDENTITY_COLUMNS)).any():
        raise ValueError("canonical comparison identity is ambiguous")

    uncertainty_column = next(
        (column for column in UNCERTAINTY_COLUMNS if column in canonical.columns), None
    )
    if uncertainty_column is None:
        canonical["uncertainty_kPa"] = np.nan
    else:
        canonical["uncertainty_kPa"] = pd.to_numeric(
            canonical[uncertainty_column], errors="coerce"
        )
    canonical["uncertainty_available"] = (
        np.isfinite(canonical["uncertainty_kPa"])
        & (canonical["uncertainty_kPa"] > 0.0)
    )
    return canonical


def _map_phase1_to_canonical(
    canonical: pd.DataFrame, phase1_pressure: pd.DataFrame
) -> pd.DataFrame:
    _require_columns(
        phase1_pressure,
        {
            "model_family",
            *CANONICAL_IDENTITY_COLUMNS,
            "predicted_CO2_pressure_kPa",
            "log10_pred_over_obs",
        },
        "Phase 1 pressure data",
    )
    phase1 = phase1_pressure.loc[
        phase1_pressure["model_family"] == PHASE1_MODEL_FAMILY
    ].copy()
    if phase1.empty:
        raise ValueError(f"Phase 1 model family is missing: {PHASE1_MODEL_FAMILY}")
    if phase1.duplicated(list(CANONICAL_IDENTITY_COLUMNS)).any():
        raise ValueError("duplicate Phase 1 comparison identity")

    canonical_columns = [
        "row_id",
        "source",
        *CANONICAL_IDENTITY_COLUMNS,
        "uncertainty_kPa",
        "uncertainty_available",
    ]
    mapped = phase1.merge(
        canonical[canonical_columns],
        on=list(CANONICAL_IDENTITY_COLUMNS),
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    unmatched = mapped.loc[mapped["_merge"] != "both", list(CANONICAL_IDENTITY_COLUMNS)]
    if not unmatched.empty:
        raise ValueError(f"unmatched Phase 1 records: {unmatched.to_dict('records')}")
    return mapped.drop(columns="_merge").sort_values("row_id").reset_index(drop=True)


def _truthy(value: object) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes"}


def _validated_phase2(canonical: pd.DataFrame, phase2_pressure: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        phase2_pressure,
        {
            "row_id",
            "source",
            "temperature_C",
            "MEA_weight_fraction",
            "CO2_loading",
            "observed_CO2_pressure_kPa",
            "model_CO2_pressure_kPa",
            "log10_model_over_data",
            "solver_success",
            "message",
        },
        "Phase 2 pressure data",
    )
    if phase2_pressure["row_id"].duplicated().any():
        raise ValueError("duplicate Phase 2 row_id")

    checked = phase2_pressure.merge(
        canonical[
            [
                "row_id",
                "source",
                *CANONICAL_IDENTITY_COLUMNS,
                "uncertainty_kPa",
                "uncertainty_available",
            ]
        ],
        on="row_id",
        how="left",
        validate="one_to_one",
        suffixes=("", "_canonical"),
        indicator=True,
    )
    if (checked["_merge"] != "both").any():
        missing = checked.loc[checked["_merge"] != "both", "row_id"].tolist()
        raise ValueError(f"Phase 2 row IDs are absent from canonical VLE data: {missing}")

    mismatched = checked["source"] != checked["source_canonical"]
    for column in CANONICAL_IDENTITY_COLUMNS:
        mismatched |= ~np.isclose(
            pd.to_numeric(checked[column], errors="coerce"),
            pd.to_numeric(checked[f"{column}_canonical"], errors="coerce"),
            rtol=0.0,
            atol=1.0e-12,
            equal_nan=False,
        )
    if mismatched.any():
        raise ValueError(
            "Phase 2 values do not match canonical records: "
            f"{checked.loc[mismatched, 'row_id'].tolist()}"
        )
    return checked.drop(columns="_merge").sort_values("row_id").reset_index(drop=True)


def _valid_residual(
    observed: pd.Series, predicted: pd.Series, residual: pd.Series
) -> pd.Series:
    observed_values = pd.to_numeric(observed, errors="coerce")
    predicted_values = pd.to_numeric(predicted, errors="coerce")
    residual_values = pd.to_numeric(residual, errors="coerce")
    return (
        np.isfinite(observed_values)
        & np.isfinite(predicted_values)
        & np.isfinite(residual_values)
        & (observed_values > 0.0)
        & (predicted_values > 0.0)
    )


def _metric_values(residual: pd.Series) -> dict[str, float | None]:
    values = pd.to_numeric(residual, errors="coerce").dropna().to_numpy(dtype=float)
    if values.size == 0:
        return {
            "mean_log10_residual": None,
            "median_log10_residual": None,
            "median_abs_log10_error": None,
            "rmse_log10_error": None,
            "q90_abs_log10_error": None,
            "max_abs_log10_error": None,
        }
    absolute = np.abs(values)
    return {
        "mean_log10_residual": float(np.mean(values)),
        "median_log10_residual": float(np.median(values)),
        "median_abs_log10_error": float(np.median(absolute)),
        "rmse_log10_error": float(np.sqrt(np.mean(values**2))),
        "q90_abs_log10_error": float(np.quantile(absolute, 0.90)),
        "max_abs_log10_error": float(np.max(absolute)),
    }


def _metric_rows(
    frame: pd.DataFrame,
    *,
    scope: str,
    model: str,
    residual_column: str,
    accepted_column: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    groups: list[tuple[str, str, pd.DataFrame]] = [("overall", "all", frame)]
    groups.extend(
        ("source", str(value), subset)
        for value, subset in frame.groupby("source", sort=True, dropna=False)
    )
    groups.extend(
        ("temperature_C", str(value), subset)
        for value, subset in frame.groupby("temperature_C", sort=True, dropna=False)
    )
    for group_type, group_value, subset in groups:
        accepted = subset[accepted_column].fillna(False).astype(bool)
        attempted_count = int(len(subset))
        accepted_count = int(accepted.sum())
        row = {
            "scope": scope,
            "model": model,
            "group_type": group_type,
            "group_value": group_value,
            "attempted_count": attempted_count,
            "accepted_count": accepted_count,
            "failure_count": attempted_count - accepted_count,
            "coverage_fraction": (
                float(accepted_count / attempted_count) if attempted_count else None
            ),
        }
        row.update(_metric_values(subset.loc[accepted, residual_column]))
        rows.append(row)
    return rows


def _uncertainty_rows(
    canonical: pd.DataFrame, paired: pd.DataFrame
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scope, frame in (("paired", paired), ("full_context", canonical)):
        for source, subset in frame.groupby("source", sort=True, dropna=False):
            available = subset["uncertainty_available"].fillna(False).astype(bool)
            rows.append(
                {
                    "scope": scope,
                    "source": str(source),
                    "row_count": int(len(subset)),
                    "uncertainty_available_count": int(available.sum()),
                    "uncertainty_coverage_fraction": float(available.mean()),
                    "uncertainty_status": (
                        "reported" if bool(available.all()) else "not_reported_for_all_rows"
                    ),
                }
            )
    return rows


def build_controlled_comparison(
    canonical_vle: pd.DataFrame,
    phase1_pressure: pd.DataFrame,
    phase2_pressure: pd.DataFrame,
    speciation_roles: pd.DataFrame,
) -> ComparisonBundle:
    """Build a same-record ideal/activity pressure comparison with explicit coverage."""
    canonical = _canonical_frame(canonical_vle)
    phase1 = _map_phase1_to_canonical(canonical, phase1_pressure)
    phase2 = _validated_phase2(canonical, phase2_pressure)
    _require_columns(
        speciation_roles,
        {"target_role", "validation_use"},
        "speciation target roles",
    )

    phase1_valid = _valid_residual(
        phase1["observed_CO2_pressure_kPa"],
        phase1["predicted_CO2_pressure_kPa"],
        phase1["log10_pred_over_obs"],
    )
    phase1["phase1_status"] = np.where(phase1_valid, "accepted", "rejected")
    phase1["phase1_accepted"] = phase1_valid

    phase2_valid = _valid_residual(
        phase2["observed_CO2_pressure_kPa"],
        phase2["model_CO2_pressure_kPa"],
        phase2["log10_model_over_data"],
    ) & phase2["solver_success"].map(_truthy)
    phase2["phase2_status"] = np.where(phase2_valid, "accepted", "rejected")
    phase2["phase2_accepted"] = phase2_valid

    phase1_for_pair = phase1.rename(
        columns={
            "predicted_CO2_pressure_kPa": "phase1_model_pressure_kPa",
            "log10_pred_over_obs": "phase1_log10_residual",
        }
    )[
        [
            "row_id",
            "source",
            *CANONICAL_IDENTITY_COLUMNS,
            "uncertainty_kPa",
            "uncertainty_available",
            "phase1_model_pressure_kPa",
            "phase1_log10_residual",
            "phase1_status",
            "phase1_accepted",
        ]
    ]
    phase2_for_pair = phase2.rename(
        columns={
            "model_CO2_pressure_kPa": "phase2_model_pressure_kPa",
            "log10_model_over_data": "phase2_log10_residual",
            "message": "phase2_message",
        }
    )[
        [
            "row_id",
            "phase2_model_pressure_kPa",
            "phase2_log10_residual",
            "phase2_status",
            "phase2_accepted",
            "phase2_message",
        ]
    ]
    paired = phase1_for_pair.merge(
        phase2_for_pair,
        on="row_id",
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    missing_phase2 = paired["_merge"] != "both"
    paired.loc[missing_phase2, "phase2_status"] = "missing"
    paired["phase2_accepted"] = paired["phase2_accepted"].fillna(False).astype(bool)
    paired["comparison_eligible"] = (
        paired["phase1_accepted"].astype(bool) & paired["phase2_accepted"]
    )

    def rejection_reason(row: pd.Series) -> str:
        reasons: list[str] = []
        if not bool(row["phase1_accepted"]):
            reasons.append("phase1: invalid or nonfinite pressure result")
        if row["phase2_status"] == "missing":
            reasons.append("phase2: prediction missing")
        elif not bool(row["phase2_accepted"]):
            message = str(row.get("phase2_message") or "invalid or nonfinite pressure result")
            reasons.append(f"phase2: {message}")
        return "; ".join(reasons)

    paired["rejection_reason"] = paired.apply(rejection_reason, axis=1)
    paired["activity_minus_ideal_abs_log10_error"] = (
        paired["phase2_log10_residual"].abs()
        - paired["phase1_log10_residual"].abs()
    ).where(paired["comparison_eligible"])
    paired["preferred_model_on_row"] = np.where(
        ~paired["comparison_eligible"],
        "not_comparable",
        np.where(
            paired["activity_minus_ideal_abs_log10_error"] < 0.0,
            "activity_model",
            np.where(
                paired["activity_minus_ideal_abs_log10_error"] > 0.0,
                "ideal_baseline",
                "tie",
            ),
        ),
    )
    paired = paired.drop(columns="_merge").sort_values("row_id").reset_index(drop=True)

    phase2_context = phase2.rename(
        columns={
            "log10_model_over_data": "phase2_log10_residual",
            "temperature_C_canonical": "temperature_C_context",
        }
    ).copy()
    metrics = pd.DataFrame(
        _metric_rows(
            paired,
            scope="paired",
            model="ideal_baseline",
            residual_column="phase1_log10_residual",
            accepted_column="comparison_eligible",
        )
        + _metric_rows(
            paired,
            scope="paired",
            model="activity_model",
            residual_column="phase2_log10_residual",
            accepted_column="comparison_eligible",
        )
        + _metric_rows(
            phase1.rename(columns={"log10_pred_over_obs": "phase1_log10_residual"}),
            scope="full_context",
            model="ideal_baseline",
            residual_column="phase1_log10_residual",
            accepted_column="phase1_accepted",
        )
        + _metric_rows(
            phase2_context,
            scope="full_context",
            model="activity_model",
            residual_column="phase2_log10_residual",
            accepted_column="phase2_accepted",
        )
    ).sort_values(["scope", "model", "group_type", "group_value"], kind="stable")
    metrics = metrics.reset_index(drop=True)

    role_counts = (
        speciation_roles.groupby(["target_role", "validation_use"], dropna=False)
        .size()
        .rename("target_count")
        .reset_index()
        .sort_values(["target_role", "validation_use"])
        .reset_index(drop=True)
    )
    zero_count = int(speciation_roles["target_role"].isin(ZERO_TARGET_ROLES).sum())
    eligible = paired.loc[paired["comparison_eligible"]]
    preferences = eligible["preferred_model_on_row"].value_counts()
    summary = {
        "comparison_basis": "same_canonical_vle_record_intersection",
        "phase1_model_family": PHASE1_MODEL_FAMILY,
        "paired_row_count": int(len(paired)),
        "paired_eligible_count": int(paired["comparison_eligible"].sum()),
        "paired_rejected_or_missing_count": int((~paired["comparison_eligible"]).sum()),
        "activity_better_row_count": int(preferences.get("activity_model", 0)),
        "ideal_better_row_count": int(preferences.get("ideal_baseline", 0)),
        "tied_row_count": int(preferences.get("tie", 0)),
        "phase2_full_context_row_count": int(len(phase2)),
        "reported_zero_target_count": zero_count,
        "pressure_uncertainty_available_count": int(
            canonical["uncertainty_available"].sum()
        ),
    }
    uncertainty_coverage = pd.DataFrame(_uncertainty_rows(canonical, paired))
    return ComparisonBundle(
        paired_rows=paired,
        metrics=metrics,
        uncertainty_coverage=uncertainty_coverage,
        role_counts=role_counts,
        summary=summary,
    )
