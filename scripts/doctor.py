from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
REFERENCE = ROOT / "data" / "reference"
ANALYSES = ROOT / "analyses"


def check(label: str, ok: bool, detail: str = "") -> bool:
    status = "OK" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"[{status}] {label}{suffix}")
    return ok


def main() -> int:
    checks = [
        check("src package", (SRC / "MEA" / "__init__.py").exists(), str(SRC / "MEA")),
        check("reference MEA data", (REFERENCE / "MEA" / "VLE" / "Jou_1995_VLE.csv").exists(), str(REFERENCE / "MEA")),
        check("reference ePC-SAFT datasets", (REFERENCE / "epcsaft_datasets").exists(), str(REFERENCE / "epcsaft_datasets")),
        check("analyses root", ANALYSES.exists(), str(ANALYSES)),
        check("MEA import spec", importlib.util.find_spec("MEA") is not None),
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
