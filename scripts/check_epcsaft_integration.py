from __future__ import annotations

import argparse
import ast
import importlib
import importlib.metadata
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CONTRACT_PATH = REPO_ROOT / "integration" / "epcsaft_contract.json"
IMPORT_PATTERN = re.compile(r"^\s*(?:from\s+epcsaft(?:\.[\w.]+)?\s+import\b|import\s+epcsaft\b)")


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _distribution(name: str):
    try:
        return importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _direct_url_payload(dist) -> dict[str, Any] | None:
    if dist is None:
        return None
    text = dist.read_text("direct_url.json")
    if not text:
        return None
    return json.loads(text)


def resolve_epcsaft(contract: dict[str, Any]) -> dict[str, Any]:
    runtime_module = importlib.import_module(contract["smoke"]["runtime_module"])
    getattr(runtime_module, contract["smoke"]["runtime_callable"])()
    epcsaft = importlib.import_module("epcsaft")
    dist = _distribution(contract["package"]["name"])
    direct_url = _direct_url_payload(dist)
    module_path = Path(epcsaft.__file__).resolve()
    version = getattr(epcsaft, "__version__", None)

    source_kind = "release"
    source_detail = str(module_path)
    if direct_url and "vcs_info" in direct_url:
        source_kind = "pinned_git"
        source_detail = json.dumps(direct_url, sort_keys=True)
    elif direct_url and direct_url.get("url"):
        source_kind = "local_file" if str(direct_url["url"]).startswith("file:") else "direct_url"
        source_detail = json.dumps(direct_url, sort_keys=True)

    return {
        "module_path": str(module_path),
        "version": version,
        "source_kind": source_kind,
        "source_detail": source_detail,
    }


def _iter_python_files(scan_roots: list[str]):
    for root in scan_roots:
        path = REPO_ROOT / root
        if not path.exists():
            continue
        yield from path.rglob("*.py")


def _is_import_module_call(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Attribute):
        return isinstance(func.value, ast.Name) and func.value.id == "importlib" and func.attr == "import_module"
    return isinstance(func, ast.Name) and func.id == "import_module"


def _is_spec_from_file_location_call(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Attribute):
        return (
            isinstance(func.value, ast.Attribute)
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == "importlib"
            and func.value.attr == "util"
            and func.attr == "spec_from_file_location"
        )
    return False


def _string_arg(node: ast.Call) -> str | None:
    if not node.args:
        return None
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def scan_direct_imports(contract: dict[str, Any]) -> list[str]:
    allowlist = {entry.replace("\\", "/") for entry in contract.get("allowed_direct_import_paths", [])}
    private_exceptions = {entry.replace("\\", "/") for entry in contract.get("private_import_exception_paths", [])}
    forbidden_prefixes = tuple(contract.get("forbidden_import_prefixes", []))
    failures: list[str] = []
    for path in _iter_python_files(contract.get("scan_roots", [])):
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError as exc:
            failures.append(f"{rel}:{exc.lineno}: could not parse Python for import scanning")
            continue

        if rel not in private_exceptions:
            for node in ast.walk(tree):
                module_name = None
                line_no = getattr(node, "lineno", 1)
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(alias.name.startswith(prefix) for prefix in forbidden_prefixes):
                            module_name = alias.name
                            break
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(node.module.startswith(prefix) for prefix in forbidden_prefixes):
                        module_name = node.module
                elif isinstance(node, ast.Call) and (_is_import_module_call(node) or _is_spec_from_file_location_call(node)):
                    candidate = _string_arg(node)
                    if candidate and any(candidate.startswith(prefix) for prefix in forbidden_prefixes):
                        module_name = candidate

                if module_name is not None:
                    failures.append(f"{rel}:{line_no}: uses forbidden private epcsaft module {module_name}")
                    break

        if rel in allowlist:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if IMPORT_PATTERN.search(line):
                failures.append(f"{rel}:{line_no}: direct epcsaft import outside allowlist")
    return failures


def run_smoke(contract: dict[str, Any]) -> dict[str, Any]:
    module = importlib.import_module(contract["smoke"]["module"])
    payload = getattr(module, contract["smoke"]["callable"])()
    pressure = float(payload["required"]["pressure_Pa"])
    density = float(payload["required"]["mass_density_kg_m3"])
    if not (math.isfinite(pressure) and pressure > 0.0):
        raise RuntimeError(f"Non-finite or non-positive smoke pressure: {pressure}")
    if not (math.isfinite(density) and density > 0.0):
        raise RuntimeError(f"Non-finite or non-positive smoke density: {density}")
    return {
        "pressure_Pa": pressure,
        "mass_density_kg_m3": density,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check MEA-Thermodynamics ePC-SAFT integration contract.")
    parser.add_argument("--mode", choices=("stable", "dev", "final"), default=None, help="Select the package source lane.")
    parser.add_argument("--self-only", action="store_true", help="Skip the repo-specific smoke step.")
    args = parser.parse_args(argv)

    contract = load_contract()
    mode = args.mode or contract["package"].get("default_mode", "stable")
    resolved = resolve_epcsaft(contract)
    allowed_sources = set(contract["package"]["allowed_sources"][mode])
    errors: list[str] = []

    if resolved["source_kind"] not in allowed_sources:
        errors.append(
            f"Resolved epcsaft source kind {resolved['source_kind']!r} from {resolved['source_detail']} "
            f"is not allowed for {mode} mode."
        )

    try:
        version = tuple(int(part) for part in str(resolved["version"]).split(".")[:3])
        minimum = tuple(int(part) for part in contract["package"]["minimum_version"].split("."))
        if version < minimum:
            errors.append(
                f"Resolved epcsaft version {resolved['version']} is below minimum {contract['package']['minimum_version']}."
            )
    except Exception:
        errors.append(f"Could not compare resolved epcsaft version {resolved['version']!r}.")

    epcsaft = importlib.import_module("epcsaft")
    for symbol in contract.get("required_public_symbols", []):
        if not hasattr(epcsaft, symbol):
            errors.append(f"Missing required public symbol: {symbol}")

    errors.extend(scan_direct_imports(contract))

    smoke_payload = None
    if not args.self_only:
        try:
            smoke_payload = run_smoke(contract)
        except Exception as exc:
            errors.append(f"Smoke check failed: {exc}")

    print(f"contract mode: {mode}")
    print(f"epcsaft module path: {resolved['module_path']}")
    print(f"epcsaft version: {resolved['version']}")
    print(f"epcsaft source kind: {resolved['source_kind']}")
    print(f"epcsaft source detail: {resolved['source_detail']}")
    if smoke_payload is not None:
        print(f"smoke pressure Pa: {smoke_payload['pressure_Pa']:.6g}")
        print(f"smoke density kg/m3: {smoke_payload['mass_density_kg_m3']:.6g}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
