from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.epcsaft_ionic.plot_results import _load_fixed_values, pressure_rows, speciation_rows

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PRESSURE_DIR = ANALYSIS_DIR / "results" / "pressure"
SPECIATION_DIR = ANALYSIS_DIR / "results" / "speciation"


def main() -> int:
    PRESSURE_DIR.mkdir(parents=True, exist_ok=True)
    SPECIATION_DIR.mkdir(parents=True, exist_ok=True)
    values = _load_fixed_values()
    pressure = pressure_rows(values)
    speciation = speciation_rows(values)
    import pandas as pd

    pd.DataFrame(pressure).to_csv(PRESSURE_DIR / "ionic_pressure_comparison.csv", index=False)
    pd.DataFrame(speciation).to_csv(SPECIATION_DIR / "ionic_speciation_activity_residuals.csv", index=False)
    print(f"Canonical ionic pressure/speciation result tables: {ANALYSIS_DIR / 'results'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
