from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile

from MEA.common.config import REPO_ROOT

from run_analysis import (
    ANALYSIS_PARTITION,
    BASE_BUNDLE,
    CANONICAL_SPLIT,
    FIGURE_OUTPUT,
    RESULTS,
    SOURCE_REFERENCE_CONVERGENCE_TOLERANCE,
    _fit_rows,
    _prepare_fit_bundle,
    _sha256,
    _tree_hashes,
)


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    receipt = json.loads(
        (RESULTS / "r4_correlation_fit_receipt.json").read_text(encoding="utf-8")
    )
    rows = _fit_rows()
    assert sum(row.role == "active_training" for row in rows) == 72
    assert sum(row.role == "reserved_validation" for row in rows) == 49
    assert receipt["canonical_split_sha256"] == _sha256(CANONICAL_SPLIT)
    assert receipt["analysis_partition_sha256"] == _sha256(ANALYSIS_PARTITION)
    assert receipt["base_bundle_files"] == _tree_hashes(BASE_BUNDLE)
    for relative_path, expected in receipt["source_files"].items():
        assert _sha256(REPO_ROOT / relative_path) == expected

    with tempfile.TemporaryDirectory(prefix="mea-r4-validation-") as temporary:
        bundle = Path(temporary) / "bundle"
        _prepare_fit_bundle(bundle)
        assert receipt["generated_bundle_files"] == _tree_hashes(bundle)

    fit_rows = _rows(FIGURE_OUTPUT / "r4_correlation_fit_rows.csv")
    failures = _rows(RESULTS / "r4_state_failures.csv")
    assert len(fit_rows) == 232
    assert len(failures) == receipt["row_counts"]["failure_records"] == 10
    assert {row["certification"] for row in fit_rows} == {"LOCAL_EQUILIBRIUM"}
    assert {row["evidence_stage"] for row in failures} == {
        "literature-R4 all-row evaluation",
        "fitted-R4 all-row evaluation",
    }
    transfer = receipt["source_reference_transfer"]
    assert transfer["convergence_tolerance"] == SOURCE_REFERENCE_CONVERGENCE_TOLERANCE
    assert (
        transfer["maximum_reference_convergence_error"]
        <= transfer["convergence_tolerance"]
    )
    assert receipt["promotion_allowed"] is False
    assert receipt["identifiability"]["scaled_jacobian_condition_number"] > 1.0e5
    print("R4 retained-result contract: passed")


if __name__ == "__main__":
    main()
