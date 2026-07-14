from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ANALYSIS_DIR = Path(__file__).resolve().parents[3]
REPO_ROOT = Path(__file__).resolve().parents[6]
for path in (REPO_ROOT / "src", ANALYSIS_DIR / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import render_figures as phase2_render  # noqa: E402


def main() -> int:
    paired_rows = pd.read_csv(phase2_render.CONTROLLED_COMPARISON_INPUT)
    phase2_render.plot_controlled_comparison(paired_rows)
    print(
        "Controlled pressure-comparison figure artifacts: "
        f"{phase2_render.CONTROLLED_COMPARISON_FIGURE_OUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
