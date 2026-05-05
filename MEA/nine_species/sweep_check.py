from __future__ import annotations

import numpy as np
import pandas as pd

from MEA.common.config import CANONICAL_MEA_WEIGHT_FRACTION, JOU_TEMPERATURES_C, LEGACY_BASELINE_OUT
from MEA.common.data_access import load_combined_vle_data
from MEA.common.reporting import write_csv_report, write_json_report
from MEA.nine_species.chemistry import result_rows, solve_all_species_series


OUTPUT_DIR = LEGACY_BASELINE_OUT
TEMPERATURES_C = JOU_TEMPERATURES_C


def _jou_range_loadings(temperature_C: float, n_points: int = 31) -> np.ndarray:
    subset = load_combined_vle_data(
        temperature_C=temperature_C,
        mea_weight_fraction=CANONICAL_MEA_WEIGHT_FRACTION,
        loading_max=0.6,
    )
    if subset.empty:
        raise ValueError(
            f"no Jou VLE data for T={temperature_C} C, w_MEA={CANONICAL_MEA_WEIGHT_FRACTION}"
        )
    return np.linspace(float(subset["CO2_loading"].min()), float(subset["CO2_loading"].max()), n_points)


def main() -> int:
    rows = []
    for temperature_C in TEMPERATURES_C:
        results = solve_all_species_series(
            _jou_range_loadings(temperature_C),
            CANONICAL_MEA_WEIGHT_FRACTION,
            273.15 + temperature_C,
        )
        rows.extend(result_rows(results))

    csv_path = OUTPUT_DIR / "all_species_sweep_diagnostics.csv"
    json_path = OUTPUT_DIR / "all_species_sweep_summary.json"
    frame = pd.DataFrame(rows)
    write_csv_report(csv_path, frame)

    failures = frame[frame["success"] == False]
    summary = {
        "n_points": int(len(frame)),
        "n_success": int((frame["success"] == True).sum()),
        "n_failed": int(len(failures)),
        "failures": failures[["temperature_C", "CO2_loading", "message"]].to_dict("records"),
    }
    write_json_report(json_path, summary)

    print(f"All-species sweep diagnostics: {csv_path}")
    print(f"All-species sweep summary: {json_path}")
    print(
        "All-species sweep points: "
        f"{summary['n_success']}/{summary['n_points']} successful, {summary['n_failed']} failed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
