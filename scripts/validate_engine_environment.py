from __future__ import annotations

import importlib
from importlib import metadata
import hashlib
import inspect
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    distribution = metadata.distribution("epcsaft")
    direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
    if direct_url.get("dir_info", {}).get("editable", False):
        errors.append("Editable Engine installs are forbidden.")
    if "vcs_info" in direct_url:
        errors.append("Git-source Engine installs are forbidden.")
    wheel_url = str(direct_url.get("url", ""))
    parsed = urlparse(wheel_url)
    wheel_path = (
        Path(unquote(parsed.path)).resolve() if parsed.scheme == "file" else None
    )
    if wheel_path is None or not wheel_path.is_file():
        errors.append("Engine direct_url does not identify a readable local wheel.")
    else:
        if wheel_path.name != lock["wheel_filename"]:
            errors.append("Installed Engine wheel filename differs from the lock.")
        if _sha256(wheel_path) != lock["wheel_sha256"]:
            errors.append("Installed Engine wheel SHA-256 differs from the lock.")
    if distribution.version != lock["version"]:
        errors.append("Installed Engine version differs from the lock.")

    stale = []
    for candidate in metadata.distributions():
        name = candidate.metadata.get("Name", "")
        normalized = re.sub(r"[-_.]+", "-", name).lower()
        if normalized.startswith("epcsaft") and normalized != "epcsaft":
            stale.append(name)
    if stale:
        errors.append(f"Retired ePC-SAFT distributions are installed: {sorted(stale)}")

    installed_root = Path(distribution.locate_file("")).resolve()
    modules = {}
    for name in ("epcsaft", "epcsaft.equilibrium", "epcsaft.regression"):
        module = importlib.import_module(name)
        modules[name] = module
        module_path = Path(module.__file__).resolve()
        if installed_root not in module_path.parents:
            errors.append(f"{name} does not originate from the Engine wheel.")
        expected_header = lock["public_header_sha256"][name]
        if _sha256(module_path) != expected_header:
            errors.append(f"{name} public header differs from the lock.")

    signatures = {
        "evaluate_reactive_bubble_observations": str(
            inspect.signature(
                modules["epcsaft.equilibrium"].evaluate_reactive_bubble_observations
            )
        ),
        "certify_reactive_bubble_continuation_reference": str(
            inspect.signature(
                modules[
                    "epcsaft.equilibrium"
                ].certify_reactive_bubble_continuation_reference
            )
        ),
        "regression.fit": str(inspect.signature(modules["epcsaft.regression"].fit)),
    }
    signature_identity = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(signatures, separators=(",", ":"), sort_keys=True).encode()
        ).hexdigest()
    )
    if signature_identity != lock["public_api_signature_identity"]:
        errors.append("Installed Engine public API signature differs from the lock.")

    print(f"epcsaft version: {distribution.version}")
    print(f"epcsaft module root: {installed_root}")
    print(f"epcsaft wheel SHA-256: {lock['wheel_sha256']}")
    print(f"epcsaft public API identity: {signature_identity}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
