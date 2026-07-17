from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from MEA.common.model_comparison import build_controlled_comparison


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "analyses/phase2/activity_epcsaft/results"
CONTROLLED = RESULTS / "controlled_comparison"


def test_controlled_comparison_recomputes_persisted_metrics() -> None:
    bundle = build_controlled_comparison(
        pd.read_csv(ROOT / "data/reference/MEA/VLE/Combined_VLE.csv"),
        pd.read_csv(ROOT / "analyses/phase1/smith_missen_baseline/results/phase1_pressure_results.csv"),
        pd.read_csv(RESULTS / "phase2_pressure_results.csv"),
        pd.read_csv(RESULTS / "phase2_speciation_target_roles.csv"),
    )
    persisted_pairs = pd.read_csv(CONTROLLED / "paired_pressure_rows.csv")
    persisted_pairs["rejection_reason"] = persisted_pairs["rejection_reason"].fillna("")
    pd.testing.assert_frame_equal(
        persisted_pairs,
        bundle.paired_rows,
        check_dtype=False,
        check_exact=False,
        rtol=1.0e-12,
        atol=1.0e-12,
    )
    pd.testing.assert_frame_equal(
        pd.read_csv(CONTROLLED / "metrics.csv"),
        bundle.metrics,
        check_dtype=False,
        check_exact=False,
        rtol=1.0e-12,
        atol=1.0e-12,
    )

    overall = bundle.metrics.query("scope == 'paired' and group_type == 'overall'").set_index("model")
    assert bundle.summary["paired_row_count"] == 31
    assert bundle.summary["reported_zero_target_count"] == 15
    assert overall.loc["ideal_baseline", "median_abs_log10_error"] == pytest.approx(0.160073413900411)
    assert overall.loc["activity_model", "median_abs_log10_error"] == pytest.approx(0.4952820148412579)
