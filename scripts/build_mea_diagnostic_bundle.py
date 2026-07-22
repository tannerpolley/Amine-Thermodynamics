from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlparse

from epcsaft import ParameterBundle
from epcsaft.records import SingleParameterRecord

from MEA.epcsaft_ionic.diagnostic_bundle import (
    COMPONENT_IDS,
    SOURCE_PATHS,
    build_mea_diagnostic_bundle,
)


PROVIDER_COMMIT = "b4499ed05f90511dc984a29f1cfb32f139600501"
EXPECTED_CHARGES = (0, 0, 0, 1, -1, -1, -2, 1, -1)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_hashes(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): _sha256(item)
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def _charges(bundle: ParameterBundle) -> tuple[int, ...]:
    selected = bundle.select(COMPONENT_IDS)
    values = {
        record.component_id: int(record.value)
        for record in selected.records
        if isinstance(record, SingleParameterRecord)
        and record.family == "charge_number"
    }
    return tuple(values[component_id] for component_id in COMPONENT_IDS)


def _installed_wheel() -> Path:
    direct_url = metadata.distribution("epcsaft").read_text("direct_url.json")
    if direct_url is None:
        raise RuntimeError("installed Provider has no direct_url.json identity")
    url = str(json.loads(direct_url).get("url", ""))
    parsed = urlparse(url)
    if parsed.scheme != "file":
        raise RuntimeError("installed Provider is not bound to a local wheel artifact")
    return Path(unquote(parsed.path)).resolve()


def _git_head(repo_root: Path) -> str:
    return subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def build_artifact(*, output: Path, receipt: Path, provider_wheel: Path) -> None:
    output = output.resolve()
    receipt = receipt.resolve()
    provider_wheel = provider_wheel.resolve()
    if output.exists() or receipt.exists():
        raise FileExistsError("bundle output and receipt must not already exist")
    if not provider_wheel.is_file():
        raise FileNotFoundError(provider_wheel)
    if _installed_wheel() != provider_wheel:
        raise RuntimeError("running interpreter is not installed from --provider-wheel")

    bundle = build_mea_diagnostic_bundle(purpose="user-provided")
    output.parent.mkdir(parents=True, exist_ok=True)
    bundle.to_path(output)
    loaded = ParameterBundle.from_path(output)
    selected = loaded.select(COMPONENT_IDS)
    if loaded.fingerprint != bundle.fingerprint:
        raise RuntimeError("bundle fingerprint changed after persistence")
    if _charges(loaded) != EXPECTED_CHARGES:
        raise RuntimeError("persisted bundle charge contract changed")

    repo_root = Path(__file__).resolve().parents[1]
    record = {
        "schema_version": 1,
        "status": "diagnostic_nonpredictive",
        "bundle_path": output.relative_to(repo_root).as_posix(),
        "bundle_fingerprint": loaded.fingerprint,
        "selected_parameter_fingerprint": selected.fingerprint,
        "component_ids": list(COMPONENT_IDS),
        "charges": list(EXPECTED_CHARGES),
        "provider": {
            "commit": PROVIDER_COMMIT,
            "version": metadata.version("epcsaft"),
            "wheel_path": str(provider_wheel),
            "wheel_sha256": _sha256(provider_wheel),
        },
        "mea_source_commit": _git_head(repo_root),
        "source_hashes": {
            path.relative_to(repo_root).as_posix(): _sha256(path) for path in SOURCE_PATHS
        },
        "emitted_file_hashes": _file_hashes(output),
        "scientific_limits": [
            "MEAH+ and MEACOO- parameters remain provisional historical evaluation inputs",
            "transferred trace-ion values are diagnostic rather than MEA-system fits",
            "the bundle is not source-complete or predictive",
        ],
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--provider-wheel", type=Path, required=True)
    args = parser.parse_args()
    build_artifact(
        output=args.output,
        receipt=args.receipt,
        provider_wheel=args.provider_wheel,
    )


if __name__ == "__main__":
    main()
