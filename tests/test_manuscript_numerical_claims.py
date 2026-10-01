from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LATEX = ROOT / "docs/scientific/latex"


def test_manuscript_numbers_match_computed_comparison() -> None:
    retained = ROOT / "analyses/mea_parameter_bundle/model-d/sensitivity-current/ranking-refit/fitted-costs.csv"
    with retained.open(newline="") as handle:
        baselines = {row["model_form"]: row for row in csv.DictReader(handle) if row["input"] == "baseline"}
    table = (LATEX / "tables/residual_summary.tex").read_text(encoding="utf-8-sig")
    results = (LATEX / "sections/mea_system_modeling_results.tex").read_text(encoding="utf-8-sig")
    assert r"\input{tables/residual_summary}" in results
    assert r"Group & Role & \(n\) & SSM+DS & Original Born" in table
    assert table.index(r"\emph{Weighted cost}") < table.index("Current objective") < table.index(r"\emph{AARD, \%}") < table.index("Pressure, 40/")
    for prefix, quantity, count, digits in (
        ("Current objective", "cost", "fitted_targets", 6),
        ("Pressure, 40/", "pressure_aard_percent", "pressure_aard_n", 2),
        ("Species, 20/40/", "species_aard_percent", "species_aard_n", 2),
    ):
        row = next(line.strip() for line in table.splitlines() if line.strip().startswith(prefix))
        cells = [cell.strip().removesuffix(r"\\").strip() for cell in row.split("&")]
        expected = [baselines[form] for form in ("SSM+DS", "Original Born")]
        assert cells[2] == expected[0][count] == expected[1][count]
        assert cells[3:] == [f"{float(item[quantity]):.{digits}f}" for item in expected]
