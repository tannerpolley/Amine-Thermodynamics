from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "reference" / "MEA"
INVENTORY = LIBRARY / "manifests" / "data_library_inventory.csv"
INVENTORY_FIELDS = (
    "library_tier",
    "scientific_family",
    "path",
    "format",
    "rows",
    "bytes",
    "sha256",
    "regression_admission",
)
REQUIRED_DIRECTORIES = (
    "observations/vapor_liquid_equilibrium",
    "observations/liquid_speciation",
    "observations/density_viscosity",
    "observations/dielectric",
    "observations/ionic_activity",
    "observations/ph",
    "observations/ionic_analog_volumetrics",
    "parameters",
    "manifests",
    "quarantine/chatgpt_audits/audit_2026-07-23_a",
    "quarantine/chatgpt_audits/audit_2026-07-23_b",
)
EXPECTED_ROWS = {
    "observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv": 327,
    "observations/vapor_liquid_equilibrium/Combined_VLE.csv": 161,
    "observations/liquid_speciation/Canonical_Combined_ChEq.csv": 571,
    "observations/ionic_analog_volumetrics/ethanolammonium_carboxylate_density.csv": 128,
    "observations/ionic_analog_volumetrics/ethanolammonium_carboxylate_excess_molar_volume.csv": 44,
}
ARCHIVE_RECEIPTS = {
    "audit_2026-07-23_a": (
        "3b3a081ec884d52107168fb19cbe66e0b7f3840b381ef5af6ddf7a160444a1b7",
        "8",
        "608",
    ),
    "audit_2026-07-23_b": (
        "da55f7a970b2fe67fed127523666c692de01a862e78e2d1d50d4ff1e95558efb",
        "20",
        "434",
    ),
}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".tex", ".txt", ".yaml", ".yml"}
STALE_PATHS = (
    "data/reference/MEA/VLE",
    "data/reference/MEA/ChEq",
    "data/reference/MEA/density_viscosity",
    "data/reference/MEA/dielectric",
    "data/reference/MEA/ionic_activity",
    "data/reference/MEA/pH",
    "data/reference/MEA/volumetric",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def _classification(relative: Path) -> tuple[str, str, str]:
    parts = relative.parts
    if parts[0] == "quarantine":
        family = "/".join(parts[:3]) if len(parts) >= 3 else "quarantine"
        return "quarantine", family, "prohibited"
    if parts[0] == "observations":
        return "verified_observation", "/".join(parts[:2]), "manifest_governed"
    if parts[0] == "parameters":
        return "parameter_evidence", "parameters", "manifest_governed"
    if parts[0] == "manifests":
        return "contract", "manifests", "not_applicable"
    return "documentation", "library", "not_applicable"


def inventory_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(LIBRARY.rglob("*")):
        if not path.is_file() or path == INVENTORY:
            continue
        relative = path.relative_to(LIBRARY)
        tier, family, admission = _classification(relative)
        rows.append(
            {
                "library_tier": tier,
                "scientific_family": family,
                "path": relative.as_posix(),
                "format": path.suffix.lower().lstrip(".") or "none",
                "rows": str(_csv_rows(path)) if path.suffix.lower() == ".csv" else "",
                "bytes": str(path.stat().st_size),
                "sha256": _sha256(path),
                "regression_admission": admission,
            }
        )
    return rows


def inventory_bytes() -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=INVENTORY_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(inventory_rows())
    return stream.getvalue().encode()


def _read_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def validate() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_DIRECTORIES:
        if not (LIBRARY / relative).is_dir():
            errors.append(f"Missing required evidence-library directory: {relative}")

    if not INVENTORY.is_file():
        errors.append(f"Missing generated inventory: {INVENTORY.relative_to(ROOT)}")
    elif INVENTORY.read_bytes() != inventory_bytes():
        errors.append("data_library_inventory.csv is stale; run this script with --write")

    for relative, expected in EXPECTED_ROWS.items():
        path = LIBRARY / relative
        if not path.is_file():
            errors.append(f"Missing row-count sentinel: {relative}")
        elif _csv_rows(path) != expected:
            errors.append(f"Scientific row-count drift in {relative}: expected {expected}, found {_csv_rows(path)}")

    split = _read_dicts(LIBRARY / "manifests" / "grouped_split_manifest.csv")
    split_roles = Counter(row["role"] for row in split)
    if split_roles != Counter({"active_training": 147, "reserved_validation": 220}):
        errors.append(f"Frozen regression split drift: {dict(split_roles)}")
    volumetric_split = _read_dicts(LIBRARY / "manifests" / "volumetric_grouped_split_manifest.csv")
    volumetric_roles = Counter(row["role"] for row in volumetric_split)
    if volumetric_roles != Counter({"future_training": 153, "reserved_validation": 78}):
        errors.append(f"Frozen volumetric split drift: {dict(volumetric_roles)}")

    receipts = {
        row["archive_id"]: (row["sha256"], row["artifact_count"], row["principal_row_ledger_rows"])
        for row in _read_dicts(LIBRARY / "quarantine" / "chatgpt_audits" / "archive_receipts.csv")
    }
    if receipts != ARCHIVE_RECEIPTS:
        errors.append("Quarantine archive receipts do not match the supplied ZIP hashes and artifact counts")

    audit_root = LIBRARY / "quarantine" / "chatgpt_audits"
    audit_a = audit_root / "audit_2026-07-23_a"
    for row in _read_dicts(audit_a / "mea_epcsaft_manifest_sha256.csv"):
        artifact = audit_a / row["artifact_filename"]
        if not artifact.is_file() or _sha256(artifact) != row["sha256"] or str(artifact.stat().st_size) != row["bytes"]:
            errors.append(f"Audit A artifact integrity failure: {row['artifact_filename']}")
    audit_b = audit_root / "audit_2026-07-23_b"
    audit_b_manifest = json.loads((audit_b / "manifest.json").read_text(encoding="utf-8"))
    for row in audit_b_manifest["files"]:
        artifact = audit_b / row["path"]
        if (
            not artifact.is_file()
            or _sha256(artifact) != row["sha256"]
            or artifact.stat().st_size != row["bytes"]
        ):
            errors.append(f"Audit B artifact integrity failure: {row['path']}")

    if INVENTORY.is_file():
        inventory = _read_dicts(INVENTORY)
        admitted_quarantine = [
            row["path"]
            for row in inventory
            if row["library_tier"] == "quarantine" and row["regression_admission"] != "prohibited"
        ]
        if admitted_quarantine:
            errors.append(f"Quarantine artifacts escaped zero-admission policy: {admitted_quarantine}")

    quarantine = LIBRARY / "quarantine"
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or path == Path(__file__)
            or path.is_relative_to(quarantine)
            or path.suffix.lower() not in TEXT_SUFFIXES
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for stale in STALE_PATHS:
            if stale in text:
                errors.append(f"Stale evidence path {stale!r} in {path.relative_to(ROOT)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or validate the MEA evidence-library inventory.")
    parser.add_argument("--write", action="store_true", help="Regenerate the machine-readable file inventory.")
    args = parser.parse_args()
    if args.write:
        INVENTORY.write_bytes(inventory_bytes())
        print(f"Wrote {INVENTORY.relative_to(ROOT)} with {len(inventory_rows())} artifacts.")
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("MEA evidence-library validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
