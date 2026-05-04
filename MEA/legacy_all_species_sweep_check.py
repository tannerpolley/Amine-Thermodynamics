from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from plot_all_species_diagnostic import result_rows, solve_all_species_series


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data" / "MEA"
OUTPUT_DIR = REPO_ROOT / "out" / "legacy_baseline"
TEMPERATURES_C = (40, 60, 80, 100, 120)


def _jou_range_loadings(temperature_C: float, n_points: int = 31) -> np.ndarray:
    df = pd.read_csv(DATA_ROOT / "VLE" / "Combined_VLE.csv")
    subset = df[
        (df["temperature"] == temperature_C)
        & (df["MEA_weight_fraction"] == 0.3)
        & (df["CO2_loading"] < 0.6)
    ]
    if subset.empty:
        raise ValueError(f"no Jou VLE data for T={temperature_C} C, w_MEA=0.3")
    return np.linspace(float(subset["CO2_loading"].min()), float(subset["CO2_loading"].max()), n_points)


def main() -> int:
    rows = []
    for temperature_C in TEMPERATURES_C:
        results = solve_all_species_series(_jou_range_loadings(temperature_C), 0.3, 273.15 + temperature_C)
        rows.extend(result_rows(results))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "all_species_sweep_diagnostics.csv"
    json_path = OUTPUT_DIR / "all_species_sweep_summary.json"
    frame = pd.DataFrame(rows)
    frame.to_csv(csv_path, index=False)

    failures = frame[frame["success"] == False]
    summary = {
        "n_points": int(len(frame)),
        "n_success": int((frame["success"] == True).sum()),
        "n_failed": int(len(failures)),
        "failures": failures[["temperature_C", "CO2_loading", "message"]].to_dict("records"),
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"All-species sweep diagnostics: {csv_path}")
    print(f"All-species sweep summary: {json_path}")
    print(
        "All-species sweep points: "
        f"{summary['n_success']}/{summary['n_points']} successful, {summary['n_failed']} failed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
