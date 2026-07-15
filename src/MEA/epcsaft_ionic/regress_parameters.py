from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from MEA.common.analysis_io import repo_relative_path
from MEA.common.data_access import require_regression_execution_admitted
from MEA.epcsaft_ionic import native_regression
from MEA.epcsaft_ionic.model import (
    ADVANCED_BORN_USER_OPTIONS,
    FIT_DATASET_DIR,
    OUT_DIR,
    load_epcsaft,
    to_jsonable,
    write_csv,
    write_fitted_dataset,
    write_json,
)


def _result_payload(result: Any) -> dict[str, Any]:
    if hasattr(result, "to_dict"):
        return to_jsonable(result.to_dict())
    payload: dict[str, Any] = {}
    for name in (
        "success",
        "message",
        "iterations",
        "parameter_map",
        "seed_map",
        "lower_bounds",
        "upper_bounds",
        "active_bounds",
        "covariance_available",
        "identifiability_status",
        "diagnostics",
    ):
        if hasattr(result, name):
            payload[name] = getattr(result, name)
    return to_jsonable(payload)


def _fit_summary(epcsaft: Any, result: Any) -> dict[str, Any]:
    if hasattr(epcsaft, "summarize_regression_result"):
        return to_jsonable(epcsaft.summarize_regression_result(result))
    payload = _result_payload(result)
    return {
        "fit_success": payload.get("success"),
        "fit_message": payload.get("message", ""),
        "fit_iterations": payload.get("iterations"),
        "parameter_map": payload.get("parameter_map", {}),
        "seed_map": payload.get("seed_map", {}),
        "active_bounds": payload.get("active_bounds", {}),
        "identifiability_status": payload.get("identifiability_status", "unavailable"),
        "diagnostics": payload.get("diagnostics", {}),
        "schema_fallback": True,
    }


def _package_status(summary: dict[str, Any], result_payload: dict[str, Any]) -> dict[str, Any]:
    explicit_status = result_payload.get("status") or summary.get("status")
    termination_reason = result_payload.get("termination_reason") or summary.get("termination_reason")
    has_issue3_status_schema = explicit_status is not None and termination_reason is not None
    return {
        "owner": "epcsaft",
        "native_function": "fit_reactive_electrolyte_parameters",
        "fit_success": summary.get("fit_success", result_payload.get("success")),
        "fit_message": summary.get("fit_message", result_payload.get("message", "")),
        "fit_iterations": summary.get("fit_iterations", result_payload.get("iterations")),
        "identifiability_status": summary.get(
            "identifiability_status", result_payload.get("identifiability_status", "unavailable")
        ),
        "residual_norm": summary.get("residual_norm"),
        "active_bounds": summary.get("active_bounds", result_payload.get("active_bounds", {})),
        "status": explicit_status if explicit_status is not None else "package_status_schema_unavailable",
        "termination_reason": termination_reason if termination_reason is not None else "package_status_schema_unavailable",
        "has_issue3_status_schema": has_issue3_status_schema,
    }


def _write_package_tables(epcsaft: Any, result: Any, output_dir: Path) -> list[Path]:
    writers = [
        ("write_regression_summary", output_dir / "native_regression_package_summary.json"),
        ("write_regression_row_table", output_dir / "native_regression_rows.csv"),
        ("write_regression_residual_table", output_dir / "native_regression_residuals.csv"),
        ("write_regression_parameter_table", output_dir / "native_regression_parameters.csv"),
    ]
    written: list[Path] = []
    for writer_name, path in writers:
        writer = getattr(epcsaft, writer_name, None)
        if writer is None:
            continue
        writer(result, path)
        written.append(path)
    return written


def run_regression(args: argparse.Namespace) -> dict[str, object]:
    problem = native_regression.build_native_regression_problem(
        max_pressure_records=args.max_vle_records,
        max_speciation_records=args.max_speciation_records,
        include_carbonate_born=not bool(getattr(args, "exclude_carbonate_born", False)),
    )
    if not problem.rows:
        raise RuntimeError("No pressure or speciation targets were available for native ePC-SAFT regression.")
    require_regression_execution_admitted()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    initial, lower, upper = native_regression.parameter_maps(problem)
    batch = native_regression.to_epcsaft_batch(problem)
    epcsaft = load_epcsaft()
    fit = getattr(epcsaft, "fit_reactive_electrolyte_parameters", None)
    if fit is None:
        raise RuntimeError("Installed epcsaft package does not expose fit_reactive_electrolyte_parameters.")

    result = fit(
        batch,
        initial_parameters=initial,
        lower_bounds=lower,
        upper_bounds=upper,
        max_iterations=int(getattr(args, "max_iterations", getattr(args, "max_nfev", 6))),
        tolerance=float(getattr(args, "tolerance", 1.0e-6)),
        damping=float(getattr(args, "damping", 1.0)),
    )

    result_payload = _result_payload(result)
    package_summary = _fit_summary(epcsaft, result)
    status = _package_status(package_summary, result_payload)
    fitted = dict(package_summary.get("parameter_map") or result_payload.get("parameter_map") or initial)
    written_dataset_paths = (
        write_fitted_dataset({key: float(value) for key, value in fitted.items()}, reset=True)
        if status["fit_success"] is True
        else []
    )

    artifact_paths = [
        write_json(OUT_DIR / "native_regression_problem.json", problem.to_dict()),
        write_json(OUT_DIR / "native_regression_result.json", result_payload),
        write_json(OUT_DIR / "native_regression_summary.json", package_summary),
    ]
    artifact_paths.extend(_write_package_tables(epcsaft, result, OUT_DIR))

    values_path = write_csv(
        OUT_DIR / "ionic_parameter_regression_values.csv",
        [
            {
                "parameter": key,
                "initial": float(initial.get(key, value)),
                "fitted": float(value),
                "lower": lower.get(key),
                "upper": upper.get(key),
                "active_bound": bool(status["active_bounds"].get(key, False))
                if isinstance(status.get("active_bounds"), dict)
                else False,
            }
            for key, value in fitted.items()
        ],
    )
    artifact_paths.append(values_path)

    summary = {
        "dataset": repo_relative_path(FIT_DATASET_DIR),
        "source_dataset": "data/reference/epcsaft_datasets/MEA_CO2_H2O_draft",
        "advanced_born_user_options": ADVANCED_BORN_USER_OPTIONS,
        "target_counts": {
            "pressure": problem.metadata["pressure_row_count"],
            "vle": problem.metadata["pressure_row_count"],
            "speciation": problem.metadata["speciation_row_count"],
        },
        "native_regression": status,
        "package_summary": package_summary,
        "initial_values": initial,
        "fitted_values": fitted,
        "written_dataset_paths": [repo_relative_path(path) for path in written_dataset_paths],
        "written_artifacts": [repo_relative_path(path) for path in artifact_paths],
        "method_note": (
            "MEA constructs pressure/speciation target rows, parameter bounds, and artifacts, but production "
            "parameter optimization is delegated to epcsaft.fit_reactive_electrolyte_parameters. No local "
            "SciPy optimizer is used in this entrypoint. Package status fields are consumed when available; "
            "older package schemas are recorded as package_status_schema_unavailable for downstream approval gates."
        ),
    }
    write_json(OUT_DIR / "ionic_parameter_regression_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Delegate full ionic MEA-CO2-H2O regression to native ePC-SAFT.")
    parser.add_argument("--target-set", choices=("reduced", "full"), default="reduced")
    parser.add_argument("--max-iterations", "--max-nfev", dest="max_iterations", type=int, default=6)
    parser.add_argument("--max-vle-records", type=int, default=18)
    parser.add_argument("--max-speciation-records", type=int, default=18)
    parser.add_argument("--exclude-carbonate-born", action="store_true")
    parser.add_argument("--backend", choices=("ceres",), default="ceres")
    parser.add_argument("--derivative-backend", choices=("autodiff",), default="autodiff")
    parser.add_argument("--tolerance", type=float, default=1.0e-6)
    parser.add_argument("--damping", type=float, default=1.0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if args.target_set == "full":
        args.max_vle_records = None
        args.max_speciation_records = None

    summary = run_regression(args)
    native_status = summary["native_regression"]
    print(f"Ionic ePC-SAFT dataset: {summary['dataset']}")
    print(f"Targets: {summary['target_counts']}")
    print(
        "Native ePC-SAFT fit: "
        f"success={native_status['fit_success']} status={native_status['status']} "
        f"message={native_status['fit_message']}"
    )
    print(f"Residual norm: {native_status['residual_norm']}")
    print("Fitted parameters:")
    for key, value in summary["fitted_values"].items():
        print(f"  {key} = {float(value):.12g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
