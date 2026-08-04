from __future__ import annotations

import importlib
from importlib import metadata
import json
from pathlib import Path
import re


def main() -> int:
    errors: list[str] = []
    distribution = metadata.distribution("epcsaft")
    direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
    if direct_url.get("dir_info", {}).get("editable", False):
        errors.append("Editable Engine installs are forbidden.")
    if "vcs_info" in direct_url:
        errors.append("Git-source Engine installs are forbidden.")

    stale = []
    for candidate in metadata.distributions():
        name = candidate.metadata.get("Name", "")
        normalized = re.sub(r"[-_.]+", "-", name).lower()
        if normalized.startswith("epcsaft") and normalized != "epcsaft":
            stale.append(name)
    if stale:
        errors.append(f"Retired ePC-SAFT distributions are installed: {sorted(stale)}")

    installed_root = Path(distribution.locate_file("")).resolve()
    for name in ("epcsaft", "epcsaft.equilibrium", "epcsaft.regression"):
        module = importlib.import_module(name)
        module_path = Path(module.__file__).resolve()
        if installed_root not in module_path.parents:
            errors.append(f"{name} does not originate from the Engine wheel.")

    print(f"epcsaft version: {distribution.version}")
    print(f"epcsaft module root: {installed_root}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
