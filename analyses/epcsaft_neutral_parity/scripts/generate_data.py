from __future__ import annotations

import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

MODULES = ['MEA.epcsaft_neutral.plot_pressure']


def main() -> int:
    status = 0
    for module in MODULES:
        print(f"== {module} ==")
        try:
            runpy.run_module(module, run_name="__main__")
        except SystemExit as exc:
            code = int(exc.code or 0) if isinstance(exc.code, int) else 1
            status = max(status, code)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
