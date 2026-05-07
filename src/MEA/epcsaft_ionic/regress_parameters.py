from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from MEA.epcsaft_ionic.model import (
    ADVANCED_BORN_USER_OPTIONS,
    FIT_DATASET_DIR,
    OUT_DIR,
    bounds_arrays,
    evaluate_values,
    initial_theta,
    load_speciation_targets,
    load_vle_targets,
    theta_to_map,
    write_csv,
    write_fitted_dataset,
    write_json,
)


def run_regression(args: argparse.Namespace) -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vle_targets = load_vle_targets(args.max_vle_records)
    spec_targets = load_speciation_targets(args.max_speciation_records)
    if not vle_targets:
        raise RuntimeError("No VLE targets were available for ionic ePC-SAFT regression.")
    if not spec_targets:
        raise RuntimeError("No speciation targets were available for ionic ePC-SAFT regression.")

    theta0 = initial_theta()
    lower, upper = bounds_arrays()
    theta0 = np.clip(theta0, lower, upper)

    initial_residuals, initial_metrics = evaluate_values(theta_to_map(theta0), vle_targets, spec_targets)
    result = least_squares(
        lambda theta: evaluate_values(theta_to_map(np.asarray(theta, dtype=float)), vle_targets, spec_targets)[0],
        theta0,
        bounds=(lower, upper),
        loss="soft_l1",
        f_scale=1.0,
        x_scale=np.maximum(np.abs(theta0), 1.0),
        max_nfev=int(args.max_nfev),
        verbose=2 if args.verbose else 0,
    )
    fitted = theta_to_map(result.x)
    final_residuals, final_metrics = evaluate_values(fitted, vle_targets, spec_targets)
    written_dataset_paths = write_fitted_dataset(fitted, reset=True)

    summary = {
        "dataset": str(FIT_DATASET_DIR),
        "source_dataset": "data/reference/epcsaft_datasets/MEA_CO2_H2O_draft",
        "advanced_born_user_options": ADVANCED_BORN_USER_OPTIONS,
        "target_counts": {"vle": len(vle_targets), "speciation": len(spec_targets)},
        "optimizer": {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "nfev": int(result.nfev),
            "cost": float(result.cost),
            "initial_residual_norm": float(np.linalg.norm(initial_residuals)),
            "final_residual_norm": float(np.linalg.norm(final_residuals)),
        },
        "initial_values": theta_to_map(theta0),
        "fitted_values": fitted,
        "initial_metrics": initial_metrics,
        "final_metrics": final_metrics,
        "written_dataset_paths": [str(path) for path in written_dataset_paths],
        "method_note": (
            "Bounded scipy least-squares around public ePC-SAFT state/activity/fugacity APIs. "
            "The fit uses fixed/reconciled liquid speciation targets, CO2 fugacity-pressure residuals, "
            "activity-based reaction residuals, Born SSM+DS user options, and regularization to literature/legacy seeds."
        ),
    }
    write_json(OUT_DIR / "ionic_parameter_regression_summary.json", summary)
    write_csv(
        OUT_DIR / "ionic_parameter_regression_values.csv",
        [{"parameter": key, "initial": theta_to_map(theta0)[key], "fitted": value} for key, value in fitted.items()],
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Regress full ionic MEA-CO2-H2O ePC-SAFT parameters.")
    parser.add_argument("--max-nfev", type=int, default=24)
    parser.add_argument("--max-vle-records", type=int, default=18)
    parser.add_argument("--max-speciation-records", type=int, default=18)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    summary = run_regression(args)
    print(f"Ionic ePC-SAFT dataset: {summary['dataset']}")
    print(f"Targets: {summary['target_counts']}")
    print(f"Optimizer success: {summary['optimizer']['success']} ({summary['optimizer']['message']})")
    print(
        "Residual norm: "
        f"{summary['optimizer']['initial_residual_norm']:.6g} -> {summary['optimizer']['final_residual_norm']:.6g}"
    )
    print(
        "VLE median |log10(model/data)|: "
        f"{summary['initial_metrics']['vle_median_abs_log10_error']:.6g} -> "
        f"{summary['final_metrics']['vle_median_abs_log10_error']:.6g}"
    )
    print("Fitted parameters:")
    for key, value in summary["fitted_values"].items():
        print(f"  {key} = {value:.12g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

