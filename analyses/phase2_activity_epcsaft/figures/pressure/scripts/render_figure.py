from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[3]
REPO_ROOT = Path(__file__).resolve().parents[5]
for path in (REPO_ROOT / "src", ANALYSIS_DIR / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import render_figures as phase2_render  # noqa: E402


def main() -> int:
    pressure_results = phase2_render.require_csv("phase2_pressure_results.csv")
    phase2_render.plot_pressure(pressure_results)
    print(f"Phase 2 pressure figure artifacts: {phase2_render.PRESSURE_FIGURE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
