from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RENDERERS = (
    ROOT / "analyses/reactive_epcsaft_parameter_evidence/born_permittivity_sensitivity/scripts/render.py",
    ROOT / "analyses/reactive_epcsaft_parameter_evidence/pressure_first/scripts/render_figures.py",
)


def main() -> int:
    for renderer in RENDERERS:
        if renderer.exists():
            status = subprocess.run([sys.executable, str(renderer)], cwd=ROOT).returncode
            if status:
                return status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
