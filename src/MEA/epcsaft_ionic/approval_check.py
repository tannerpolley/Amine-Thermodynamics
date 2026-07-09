from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from MEA.epcsaft_ionic.model import write_json

CARBONATE_BORN_PARAMETERS = ("HCO3-__d_born", "CO3^2-__d_born")
MAJOR_SPECIATION_GATES = {
    "MEAH+": 0.15,
    "MEACOO-": 0.10,
}
CARBONATE_REFERENCE_DBORN = {
    "HCO3-__d_born": 3.0,
    "CO3^2-__d_born": 3.0,
}
CARBONATE_MOVEMENT_THRESHOLD = 0.25


def _as_float(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _active_bounds(summary: dict[str, Any]) -> dict[str, bool]:
    native = summary.get("native_regression_summary", {})
    candidates = [
        summary.get("parameters_at_bounds", {}),
        summary.get("native_regression", {}).get("active_bounds", {}),
        native.get("active_bounds", {}) if isinstance(native, dict) else {},
    ]
    merged: dict[str, bool] = {}
    for candidate in candidates:
        if isinstance(candidate, dict):
            for key, value in candidate.items():
                name = str(key)
                merged[name] = bool(value) or merged.get(name, False)
    return merged


def _fit_values(summary: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    for source_key in ("fitted_values", "selected_values"):
        source = summary.get(source_key, {})
        if isinstance(source, dict):
            values.update({str(key): float(value) for key, value in source.items()})
    return values


def _native_summary(summary: dict[str, Any]) -> dict[str, Any]:
    native = summary.get("native_regression_summary", {})
    return native if isinstance(native, dict) else {}


def evaluate_global_regression_approval(summary: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    warnings: list[str] = []
    native = _native_summary(summary)
    optimizer = summary.get("optimizer", {}) if isinstance(summary.get("optimizer"), dict) else {}
    active_bounds = _active_bounds(summary)
    values = _fit_values(summary)

    if summary.get("completion_status") != "completed":
        reasons.append("completion_status_not_completed")
    if summary.get("selected_parameter_set") != "global_regression":
        reasons.append("selected_parameter_set_not_global_regression")
    if optimizer.get("owner") != "epcsaft":
        reasons.append("optimizer_owner_not_epcsaft")
    if optimizer.get("native_function") != "fit_reactive_electrolyte_parameters":
        reasons.append("native_fit_function_missing")
    if native.get("fit_success") is not True:
        reasons.append("native_fit_success_not_true")

    failure_count = native.get("failure_count", summary.get("failure_count"))
    if failure_count is None:
        reasons.append("native_row_failure_count_missing")
    elif int(failure_count) != 0:
        reasons.append("native_row_failures_present")

    if any(active_bounds.values()):
        reasons.append("parameters_at_active_bounds")

    pressure_metrics = summary.get("pressure_metrics", {}) if isinstance(summary.get("pressure_metrics"), dict) else {}
    baseline_pressure_metrics = (
        summary.get("baseline_pressure_metrics", {})
        if isinstance(summary.get("baseline_pressure_metrics"), dict)
        else {}
    )
    final_pressure = _as_float(pressure_metrics.get("median_abs_log10"))
    baseline_pressure = _as_float(baseline_pressure_metrics.get("median_abs_log10"))
    if final_pressure is None or baseline_pressure is None:
        reasons.append("pressure_metric_missing")
    elif final_pressure > baseline_pressure:
        reasons.append("pressure_metric_worse_than_baseline")

    speciation = summary.get("speciation_metrics", {}) if isinstance(summary.get("speciation_metrics"), dict) else {}
    for species, threshold in MAJOR_SPECIATION_GATES.items():
        species_metrics = speciation.get(species, {}) if isinstance(speciation.get(species), dict) else {}
        value = _as_float(species_metrics.get("median_abs_log10"))
        if value is None:
            reasons.append(f"{species}_speciation_metric_missing")
        elif value > threshold:
            reasons.append(f"{species}_speciation_metric_above_gate")

    carbonate_moved = []
    for name in CARBONATE_BORN_PARAMETERS:
        value = values.get(name)
        if value is None:
            continue
        if abs(value - CARBONATE_REFERENCE_DBORN[name]) >= CARBONATE_MOVEMENT_THRESHOLD:
            carbonate_moved.append(name)
            if active_bounds.get(name):
                reasons.append(f"{name}_carbonate_active_bound")
    if carbonate_moved:
        target_types = native.get("by_target_type", {}) if isinstance(native.get("by_target_type"), dict) else {}
        has_pressure = "partial_pressure" in target_types or "partial_pressures" in target_types or "pressure" in target_types
        has_speciation = "speciation" in target_types
        if not (has_pressure and has_speciation):
            reasons.append("carbonate_movement_without_coupled_pressure_speciation_evidence")
        warnings.append("carbonate_born_moved_from_regularized_reference")

    return {
        "approved": not reasons,
        "decision": "approve_global_regression_promotion" if not reasons else "reject_global_regression_promotion",
        "reasons": reasons,
        "warnings": warnings,
        "carbonate_movement_threshold": CARBONATE_MOVEMENT_THRESHOLD,
        "required_major_speciation_gates": MAJOR_SPECIATION_GATES,
    }


def assert_global_regression_promotion_allowed(summary: dict[str, Any]) -> dict[str, Any]:
    approval = evaluate_global_regression_approval(summary)
    if not approval["approved"]:
        raise RuntimeError("Global regression promotion rejected: " + ", ".join(approval["reasons"]))
    return approval


def write_global_regression_approval(summary: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    approval = evaluate_global_regression_approval(summary)
    write_json(output_dir / "global_regression_approval.json", approval)
    return approval


def main() -> int:
    parser = argparse.ArgumentParser(description="Check full-ionic ePC-SAFT MEA global-regression promotion gates.")
    parser.add_argument("summary", type=Path, nargs="?", default=Path("analyses/phase3/ionic_epcsaft_regression/results/global_regression/global_regression_summary.json"))
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    approval = evaluate_global_regression_approval(summary)
    print(json.dumps(approval, indent=2, sort_keys=True))
    return 0 if approval["approved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
