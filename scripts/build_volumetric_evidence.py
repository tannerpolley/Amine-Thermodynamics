#!/usr/bin/env python3
"""Build the frozen row contract and grouped split for issue 39 evidence."""

from __future__ import annotations

import argparse
import csv
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
                "composition_basis": "MEA mass fraction in unloaded solution",
                "value_reported": row["value"],
                "reported_unit": row["value_unit"],
                "uncertainty_value": row["uncertainty_value"],
                "uncertainty_unit": row["uncertainty_unit"],
                "uncertainty_type": row["uncertainty_type"],
                "measurement_role": row["measurement_role"],
                "source_lifecycle_status": row["lifecycle_status"],
                "contract_lifecycle_status": "canonical_eligible",
                "objective_role": "direct_measurement",
                "target_eligible": "yes",
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
                "contract_lifecycle_status": (
                    "diagnostic_only" if shared_water_endpoint else row["lifecycle_status"]
                ),
                "objective_role": (
                    "contextual" if shared_water_endpoint else "analog_measurement"
                ),
                "target_eligible": "no" if shared_water_endpoint else "yes",
                "group_id": group_id,
            }
        )

    canonical = {row["record_id"]: row for row in read_rows(CANONICAL)}
    for row in read_rows(SPECIATION):
        source = canonical.get(row["membership_id"], {})
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
                "group_id": (
                    f"{row['source_key']}|w={row['mea_mass_fraction']}|"
                    f"T={row['temperature_C']}"
                ),
            }
        )
    return rows


def build_split(contract: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
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
    args = parser.parse_args()
    contract = build_contract()
    outputs = {
        CONTRACT: csv_text(contract, CONTRACT_FIELDS),
        SPLIT: csv_text(build_split(contract), SPLIT_FIELDS),
    }
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
