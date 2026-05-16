from __future__ import annotations

from generate_data import (
    PROCESSED_DIR,
    RESULTS_DIR,
    SOURCE_RESIDUAL_SUMMARY_FIELDNAMES,
    read_csv,
    source_residual_summary_rows,
    write_csv,
)


def main() -> int:
    pressure_rows = read_csv(RESULTS_DIR / "phase2_pressure_results.csv")
    speciation_rows = read_csv(RESULTS_DIR / "phase2_equilibrium_results.csv")
    rows = source_residual_summary_rows(pressure_rows, speciation_rows)
    write_csv(PROCESSED_DIR / "phase2_source_residual_summary.csv", rows, SOURCE_RESIDUAL_SUMMARY_FIELDNAMES)
    write_csv(RESULTS_DIR / "phase2_source_residual_summary.csv", rows, SOURCE_RESIDUAL_SUMMARY_FIELDNAMES)
    print(f"Wrote {len(rows)} Phase 2 source-residual summary rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
