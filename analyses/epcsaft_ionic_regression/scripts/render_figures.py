from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.epcsaft_ionic.plot_results import plot_pressure, plot_speciation  # noqa: E402

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PRESSURE_CSV = ANALYSIS_DIR / "results" / "pressure" / "ionic_pressure_comparison.csv"
SPECIATION_CSV = ANALYSIS_DIR / "results" / "speciation" / "ionic_speciation_activity_residuals.csv"


def main() -> int:
    missing = [path for path in (PRESSURE_CSV, SPECIATION_CSV) if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing ionic plot snapshot: {path}")
        print("Run `uv run python analyses\\epcsaft_ionic_regression\\scripts\\generate_data.py` first.")
        return 1
    pressure_rows = pd.read_csv(PRESSURE_CSV).to_dict("records")
    speciation_rows = pd.read_csv(SPECIATION_CSV).to_dict("records")
    pressure_plot = plot_pressure(pressure_rows)
    speciation_plot = plot_speciation(speciation_rows)
    print(f"Ionic pressure plot: {pressure_plot}")
    print(f"Ionic speciation plot: {speciation_plot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
