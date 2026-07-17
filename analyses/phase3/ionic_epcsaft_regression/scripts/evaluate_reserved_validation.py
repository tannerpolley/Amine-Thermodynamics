from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.epcsaft_ionic.preregistration import load_preregistration, validate_preregistration  # noqa: E402
from MEA.epcsaft_ionic.validation import (  # noqa: E402
    ValidationContractError,
    build_reserved_validation_contract,
    evaluate_reserved_predictions,
    summarize_validation_records,
    validate_candidate_summary,
    write_validation_bundle,
)


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValidationContractError(f"expected a JSON object in {path}")
    return payload


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an immutable promoted candidate on reserved MEA evidence.")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--approval", type=Path, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "analyses/phase3/ionic_epcsaft_regression/results/validation",
    )
    args = parser.parse_args()

    approval_path = args.approval or args.candidate.with_name("global_regression_approval.json")
    preregistration = validate_preregistration(load_preregistration(args.preregistration))
    summary = _load_json(args.candidate)
    approval = _load_json(approval_path)
    parameter_names = tuple(parameter["name"] for parameter in preregistration.payload["parameters"])
    candidate = validate_candidate_summary(
        summary,
        approval=approval,
        preregistration_sha256=preregistration.sha256,
        parameter_names=parameter_names,
    )
    candidate_file_sha256 = _file_sha256(args.candidate)
    contract = build_reserved_validation_contract()
    records = evaluate_reserved_predictions(candidate.values)
    if _file_sha256(args.candidate) != candidate_file_sha256:
        raise ValidationContractError("candidate file changed during reserved validation")
    validation_summary, metrics = summarize_validation_records(
        records,
        contract=contract,
        candidate_sha256=candidate.sha256,
        preregistration_sha256=preregistration.sha256,
        expected_split_hash=preregistration.payload["readiness"]["split_hash"],
        source_hashes=preregistration.payload["readiness"]["source_hashes"],
    )
    validation_summary["candidate_file_sha256"] = candidate_file_sha256
    write_validation_bundle(records=records, summary=validation_summary, metrics=metrics, output_dir=args.output_dir)
    print(json.dumps(validation_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
