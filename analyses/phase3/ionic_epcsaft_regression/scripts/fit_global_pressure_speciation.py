from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.epcsaft_ionic.approval_check import write_global_regression_approval
from MEA.epcsaft_ionic.global_regression import GLOBAL_RESULTS_DIR, attempt_global_regression, write_global_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Attempt coupled pressure/speciation regression for full-ionic MEA ePC-SAFT.")
    parser.add_argument("--max-pressure-records", type=int, default=None)
    parser.add_argument("--max-speciation-records", type=int, default=None)
    parser.add_argument("--max-nfev", type=int, default=12)
    parser.add_argument("--output-label", type=str, default=None)
    parser.add_argument("--pressure-weight", type=float, default=1.0)
    parser.add_argument("--speciation-weight", type=float, default=1.0)
    parser.add_argument("--regularization-scale", type=float, default=0.003)
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    payload = attempt_global_regression(
        max_pressure_records=args.max_pressure_records,
        max_speciation_records=args.max_speciation_records,
        max_nfev=args.max_nfev,
        pressure_weight=args.pressure_weight,
        speciation_weight=args.speciation_weight,
        regularization_scale=args.regularization_scale,
        verbose=args.verbose,
    )
    output_dir = GLOBAL_RESULTS_DIR.parent / "runs" / "global_regression" / (args.output_label or "smoke")
    summary = write_global_artifacts(payload, output_dir)
    approval = write_global_regression_approval(summary, output_dir)
    if args.promote:
        if not approval["approved"]:
            print(json.dumps(approval, indent=2, sort_keys=True))
            print(json.dumps({"promotion": "rejected", "candidate_dir": str(output_dir)}, indent=2))
            return 2
        if GLOBAL_RESULTS_DIR.exists():
            shutil.rmtree(GLOBAL_RESULTS_DIR)
        shutil.copytree(output_dir, GLOBAL_RESULTS_DIR)
        output_dir = GLOBAL_RESULTS_DIR
    print(json.dumps(summary["optimizer"], indent=2))
    print(
        json.dumps(
            {
                "completion_status": summary["completion_status"],
                "selected_parameter_set": summary["selected_parameter_set"],
                "promotion_approval": approval["decision"],
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
