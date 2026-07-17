from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LATEX = ROOT / "docs/latex"


def test_manuscript_numbers_match_computed_comparison() -> None:
    comparison = json.loads(
        (ROOT / "analyses/phase2/activity_epcsaft/results/controlled_comparison/metrics.json").read_text(
            encoding="utf-8"
        )
    )
    overall = {
        row["model"]: row
        for row in comparison["metrics"]
        if row["scope"] == "paired" and row["group_type"] == "overall"
    }
    table = (LATEX / "tables/residual_summary.tex").read_text(encoding="utf-8-sig")
    abstract = (LATEX / "main.tex").read_text(encoding="utf-8-sig")
    results = (LATEX / "sections/mea_system_modeling_results.tex").read_text(encoding="utf-8-sig")

    for model in ("ideal_baseline", "activity_model"):
        for metric in ("median_log10_residual", "median_abs_log10_error", "rmse_log10_error"):
            assert f'{overall[model][metric]:.3f}' in table
    assert comparison["summary"]["paired_row_count"] == 31
    assert comparison["summary"]["reported_zero_target_count"] == 15
    assert "0.160 for the ideal baseline and 0.495 for the activity model" in abstract
    assert "642 of 644" in results
