from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.six_species.plot_pressure import compute_jou_metrics
from MEA.six_species.plot_speciation import compute_legacy_speciation_grid, load_speciation_data

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PRESSURE_RESULTS_DIR = ANALYSIS_DIR / "results" / "pressure"
SPECIATION_RESULTS_DIR = ANALYSIS_DIR / "results" / "speciation"


def main() -> int:
    PRESSURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SPECIATION_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics, summary, curves = compute_jou_metrics()
    speciation_curves = compute_legacy_speciation_grid()
    speciation_data = load_speciation_data()

    metrics.to_csv(PRESSURE_RESULTS_DIR / "legacy_pcsaft_jou_fit_metrics.csv", index=False)
    summary.to_csv(PRESSURE_RESULTS_DIR / "legacy_pcsaft_jou_fit_summary.csv", index=False)
    curves.to_csv(PRESSURE_RESULTS_DIR / "legacy_pcsaft_jou_fit_curves.csv", index=False)
    speciation_curves.to_csv(SPECIATION_RESULTS_DIR / "six_species_speciation_curves.csv", index=False)
    speciation_data.to_csv(SPECIATION_RESULTS_DIR / "six_species_speciation_reference.csv", index=False)

    print(f"Canonical six-species result tables: {ANALYSIS_DIR / 'results'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
