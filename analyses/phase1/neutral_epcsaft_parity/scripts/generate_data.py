from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.epcsaft_neutral.plot_pressure import compute_neutral_parity, write_neutral_dataset

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"


def main() -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dataset_paths = write_neutral_dataset()
    metrics, summary, curves = compute_neutral_parity()
    metrics.to_csv(PROCESSED_DIR / "epcsaft_neutral_jou_parity_metrics.csv", index=False)
    summary.to_csv(PROCESSED_DIR / "epcsaft_neutral_jou_parity_summary.csv", index=False)
    curves.to_csv(PROCESSED_DIR / "epcsaft_neutral_jou_parity_curves.csv", index=False)
    print(f"Neutral ePC-SAFT dataset files: {[str(path) for path in dataset_paths]}")
    print(f"Processed neutral parity tables: {PROCESSED_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
