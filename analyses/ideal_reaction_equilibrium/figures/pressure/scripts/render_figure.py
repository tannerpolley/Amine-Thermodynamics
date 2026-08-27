from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[3]
REPO_ROOT = Path(__file__).resolve().parents[5]
for path in (REPO_ROOT / "src", ANALYSIS_DIR / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import render_figures as ideal_reference_render  # noqa: E402


def main() -> int:
    pressure_results, *_ = ideal_reference_render._write_curated_tables()
    ideal_reference_render.plot_pressure(pressure_results)
    print(f"ideal reaction-equilibrium reference pressure figure artifacts: {ideal_reference_render.PRESSURE_FIGURE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
