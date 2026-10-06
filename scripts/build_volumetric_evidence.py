#!/usr/bin/env python3
"""Build the frozen row contract and grouped split for issue 39 evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMUNDSEN = ROOT / "data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv"
ANALOG = ROOT / "data/reference/MEA/observations/ionic_analog_volumetrics/ethanolammonium_carboxylate_density.csv"
SPECIATION = ROOT / "data/reference/MEA/manifests/speciation_target_membership.csv"
CANONICAL = ROOT / "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
CONTRACT = ROOT / "data/reference/MEA/manifests/ionic_volumetric_observation_contract.csv"
SPLIT = ROOT / "data/reference/MEA/manifests/volumetric_grouped_split_manifest.csv"

CONTRACT_FIELDS = [
    "observation_id",
    "data_family",
    "source_key",
    "source_file",
    "source_row_id",
    "observed_quantity",
    "temperature_K",
    "mea_mass_fraction",
    "co2_loading_mol_per_mol_mea",
    "composition_value",
    "composition_basis",
    "value_reported",
    "reported_unit",
    "uncertainty_value",
    "uncertainty_unit",
    "uncertainty_type",
    "measurement_role",
    "source_lifecycle_status",
    "contract_lifecycle_status",
    "objective_role",
    "target_eligible",
    "group_id",
]

CONTRACT_FIELDS += ["system", "uncertainty_status", "uncertainty_scope", "admission_reason", "measurement_identity", "linear_coefficients"]

SPLIT_FIELDS = [
    "observation_id",
    "data_family",
    "source_key",
    "group_id",
    "split",
    "role",
    "source_path",
    "reason",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def objective_role(
    role: str, lifecycle: str, target_eligible: str, source_key: str
) -> str:
    if lifecycle == "excluded":
        return "excluded"
    if role == "balance_inferred":
        return "inferred_not_independent"
    if role == "ambiguous":
        return "calibration_contextual"
    if lifecycle == "validation_reserved":
        return "held_out"
    if lifecycle == "diagnostic_only" and source_key == "Wong2015":
        return "calibration_contextual"
    if lifecycle in {"diagnostic_only", "qa_pending"}:
        return "contextual"
    if target_eligible != "yes":
        return "contextual"
    return {
        "direct_positive": "direct_measurement",
        "direct_zero": "upper_bound_or_reported_zero",
        "below_detection": "upper_bound_or_reported_zero",
        "aggregate_direct_positive": "aggregate_measurement",
        "aggregate_direct_zero": "aggregate_measurement",
        "balance_inferred": "inferred_not_independent",
        "model_derived": "calibration_or_model_derived",
        "analog": "analog_measurement",
        "ambiguous": "excluded",
    }[role]


def build_contract() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    density_index = 0
    for source_index, row in enumerate(read_rows(AMUNDSEN), start=1):
        if row["property"] != "density":
            continue
        density_index += 1
        loaded = bool(row["co2_loading_mol_per_mol_mea"])
        group_id = (
            f"Amundsen2009|{'loaded' if loaded else 'unloaded'}|"
            f"w={row['mea_mass_fraction']}|T={row['temperature_C']}"
        )
        rows.append(
            {
                "observation_id": f"AMU-DENS-{density_index:03d}",
                "data_family": "reactive_mea_density" if loaded else "unloaded_mea_density",
                "source_key": row["source_key"],
                "source_file": AMUNDSEN.relative_to(ROOT).as_posix(),
                "source_row_id": str(source_index),
                "observed_quantity": "density",
                "temperature_K": f"{float(row['temperature_C']) + 273.15:g}",
                "mea_mass_fraction": row["mea_mass_fraction"],
                "co2_loading_mol_per_mol_mea": row["co2_loading_mol_per_mol_mea"],
                "composition_value": row["mea_mass_fraction"],
                "composition_basis": "pure MEA endpoint" if row["system"] == "pure_mea" else "MEA mass fraction in unloaded solution",
                **{field: row[field] for field in ("system", "uncertainty_status", "uncertainty_scope")},
                "admission_reason": "Measurement pressure unreported; loaded uncertainty scope unbound.",
                "value_reported": row["value"],
                "reported_unit": row["value_unit"],
                "uncertainty_value": row["uncertainty_value"],
                "uncertainty_unit": row["uncertainty_unit"],
                "uncertainty_type": row["uncertainty_type"],
                "measurement_role": row["measurement_role"],
                "source_lifecycle_status": row["lifecycle_status"],
                "contract_lifecycle_status": "diagnostic_only",
                "objective_role": "contextual",
                "target_eligible": "no",
                "group_id": group_id,
            }
        )

    for row in read_rows(ANALOG):
        shared_water_endpoint = (
            row["source_key"] == "Dhage2026"
            and float(row["solute_mole_fraction"]) == 0.0
        )
        group_id = (
            f"{row['source_key']}|shared_water_endpoint|T={row['temperature_K']}"
            if shared_water_endpoint
            else f"{row['source_key']}|{row['anion']}|T={row['temperature_K']}"
        )
        rows.append(
            {
                "observation_id": row["record_id"],
                "data_family": "ethanolammonium_carboxylate_density",
                "source_key": row["source_key"],
                "source_file": ANALOG.relative_to(ROOT).as_posix(),
                "source_row_id": row["record_id"],
                "observed_quantity": "density",
                "temperature_K": row["temperature_K"],
                "mea_mass_fraction": "",
                "co2_loading_mol_per_mol_mea": "",
                "composition_value": row["solute_mole_fraction"],
                "composition_basis": row["composition_basis"],
                "value_reported": row["density_g_cm3"],
                "reported_unit": "g/cm^3",
                "uncertainty_value": row["uncertainty_value"],
                "uncertainty_unit": row["uncertainty_unit"],
                "uncertainty_type": row["uncertainty_type"],
                "measurement_role": row["measurement_role"],
                "source_lifecycle_status": row["lifecycle_status"],
                "contract_lifecycle_status": "diagnostic_only",
                "objective_role": "contextual",
                "target_eligible": "no",
                "admission_reason": "source binding unverified",
                "uncertainty_scope": "Legacy estimates retained; exact PDF/salt-to-row binding unverified.",
                "group_id": group_id,
            }
        )

    canonical = {row["record_id"]: row for row in read_rows(CANONICAL)}
    for row in read_rows(SPECIATION):
        source = canonical.get(row["measurement_identity"], {})
        if row["target_eligible"] == "yes" and not source:
            raise ValueError(f"Missing measured speciation identity: {row['membership_id']}")
        lifecycle = row["lifecycle_status"]
        rows.append(
            {
                "observation_id": row["membership_id"],
                "data_family": "speciation",
                "source_key": row["source_key"],
                "source_file": row["source_file"],
                "source_row_id": row["source_row_index"],
                "observed_quantity": row["species"],
                "temperature_K": f"{float(row['temperature_C']) + 273.15:g}",
                "mea_mass_fraction": row["mea_mass_fraction"],
                "co2_loading_mol_per_mol_mea": row["co2_loading_mol_per_mol_mea"],
                "composition_value": source.get("reported_value", ""),
                "composition_basis": row["reported_basis"],
                "value_reported": source.get("reported_value", ""),
                "reported_unit": source.get("reported_unit", ""),
                "uncertainty_value": "",
                "uncertainty_unit": "",
                "uncertainty_type": "not_reported",
                "measurement_role": row["measurement_role"],
                "source_lifecycle_status": lifecycle,
                "contract_lifecycle_status": lifecycle,
                "objective_role": objective_role(
                    row["measurement_role"],
                    lifecycle,
                    row["target_eligible"],
                    row["source_key"],
                ),
                "target_eligible": row["target_eligible"],
                **{field: row[field] for field in ("measurement_identity", "linear_coefficients")},
                "admission_reason": row["eligibility_reason"],
                "group_id": (
                    f"{row['source_key']}|w={row['mea_mass_fraction']}|"
                    f"T={row['temperature_C']}"
                ),
            }
        )
    for row in rows:
        for field in CONTRACT_FIELDS:
            row.setdefault(field, "")
    return rows


def build_split(contract: list[dict[str, str]], baseline_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    baseline = {row["observation_id"]: row for row in read_rows(baseline_dir / SPLIT.name)}
    source_paths = {
        "ethanolammonium_carboxylate_density": ANALOG.relative_to(ROOT).as_posix(),
        "unloaded_mea_density": AMUNDSEN.relative_to(ROOT).as_posix(),
        "reactive_mea_density": AMUNDSEN.relative_to(ROOT).as_posix(),
    }
    for row in contract:
        family = row["data_family"]
        if family == "speciation":
            continue
        group = row["group_id"]
        if family == "ethanolammonium_carboxylate_density":
            held_out = (
                ("Augusto2022" in group and ("T=303.15" in group or "T=348.15" in group))
                or ("Dhage2026|pentanoate" in group)
            )
            reason = (
                "Complete source/salt/temperature composition curve reserved."
                if held_out
                else "Complete source/salt/temperature composition curve admitted for future calibration."
            )
        else:
            held_out = group.endswith("T=40") or group.endswith("T=80")
            reason = (
                "Complete MEA-fraction/temperature loading curve reserved."
                if held_out
                else "Complete MEA-fraction/temperature loading curve admitted for future calibration."
            )
        rows.append(
            {
                "observation_id": row["observation_id"],
                "data_family": family,
                "source_key": row["source_key"],
                "group_id": group,
                "split": "validation" if held_out else "training",
                "role": "reserved_validation" if held_out else "future_training",
                "source_path": source_paths[family],
                "reason": reason,
            }
        )
    if set(baseline) != {row["observation_id"] for row in rows}:
        raise ValueError("Volumetric split IDs changed")
    for row in rows:
        previous = baseline[row["observation_id"]]
        row.update({field: previous[field] for field in ("group_id", "split", "role")})
        row["reason"] = "Frozen partition provenance only; current execution blocked."
        if row["data_family"] == "ethanolammonium_carboxylate_density":
            row.update(role="context_only", reason="source binding unverified")
    return rows


def csv_text(rows: list[dict[str, str]], fields: list[str]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--admission-receipt", type=Path, required=True)
    args = parser.parse_args()
    preflight = json.loads((args.baseline_dir.parent / "preflight.json").read_text())
    for name, expected in preflight["baseline_file_hashes"].items():
        if hashlib.sha256((args.baseline_dir / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Frozen baseline hash drift: {name}")
    contract = build_contract()
    split = build_split(contract, args.baseline_dir)
    outputs = {CONTRACT: csv_text(contract, CONTRACT_FIELDS), SPLIT: csv_text(split, SPLIT_FIELDS)}
    frozen = [ROOT / "analyses/reactive_epcsaft_parameter_evidence/ionic_volumetric_fit_preregistration.json", ROOT / "src/MEA/epcsaft_ionic/preregistration.py"]
    if any(hashlib.sha256(path.read_bytes()).hexdigest() != preflight["protected_file_hashes"][path.relative_to(ROOT).as_posix()] for path in frozen):
        raise ValueError("Immutable preregistration/guard drift")
    analogs = [row for row in contract if row["data_family"] == "ethanolammonium_carboxylate_density"]
    if len(analogs) != 128 or any(row["target_eligible"] != "no" or row["objective_role"] != "contextual" for row in analogs):
        raise ValueError("All128 analogs must remain context-only")
    baseline = read_rows(args.baseline_dir / SPLIT.name)
    receipt = {
        "base_commit": preflight["base_commit"], "baseline_dir": args.baseline_dir.relative_to(ROOT) .as_posix() if args.baseline_dir.is_absolute() else args.baseline_dir.as_posix(),
        "baseline_assignment_sha256": preflight["baseline_file_hashes"][SPLIT.name],
        "source_hashes": {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in (AMUNDSEN, ANALOG, SPECIATION, CANONICAL, *frozen)},
        "output_hashes": {path.relative_to(ROOT).as_posix(): hashlib.sha256(text.encode()).hexdigest() for path, text in outputs.items()},
        "family_counts": dict(Counter(row["data_family"] for row in contract)), "role_counts": dict(Counter(row["role"] for row in split)),
        "role_diffs": [{"observation_id": row["observation_id"], "old": previous["role"], "new": row["role"]} for row, previous in zip(split, baseline, strict=True) if row["role"] != previous["role"]],
        "analog_context_only_count": len(analogs), "execution_admitted": False,
        "frozen_preregistration_disposition": "superseded for current-data execution; retained as immutable provenance",
        "blockers": ["source binding unverified", "Amundsen pressure unreported; loaded uncertainty scope unbound", "application qualification absent"],
    }
    outputs[args.admission_receipt] = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    stale = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit("stale generated volumetric evidence: " + ", ".join(stale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
