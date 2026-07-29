#!/usr/bin/env python3
"""Validate the issue 39 volumetric evidence and preregistration contract."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

from MEA.epcsaft_ionic.preregistration import (
    PreregistrationError,
    validate_gate0_preregistration,
)


ROOT = Path(__file__).resolve().parents[1]
DENSITY = ROOT / "data/reference/MEA/observations/ionic_analog_volumetrics/ethanolammonium_carboxylate_density.csv"
DERIVED = ROOT / "data/reference/MEA/observations/ionic_analog_volumetrics/ethanolammonium_carboxylate_excess_molar_volume.csv"
SOURCES = ROOT / "data/reference/MEA/observations/ionic_analog_volumetrics/volumetric_source_manifest.csv"
AMUNDSEN = ROOT / "data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv"
SPECIATION = ROOT / "data/reference/MEA/manifests/speciation_target_membership.csv"
CONTRACT = ROOT / "data/reference/MEA/manifests/ionic_volumetric_observation_contract.csv"
SPLIT = ROOT / "data/reference/MEA/manifests/volumetric_grouped_split_manifest.csv"
PARAMETER_MAP = ROOT / "data/reference/MEA/manifests/ionic_parameter_observable_map.csv"
PREREGISTRATION = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/ionic_volumetric_fit_preregistration.json"
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    density = rows(DENSITY)
    required_density = {
        "record_id",
        "source_key",
        "temperature_K",
        "solute_mole_fraction",
        "composition_basis",
        "density_g_cm3",
        "uncertainty_value",
        "uncertainty_unit",
        "uncertainty_type",
        "measurement_role",
        "lifecycle_status",
        "source_locator",
    }
    if len(density) != 128:
        errors.append(f"analog density row count is {len(density)}, expected 128")
    if len({row["record_id"] for row in density}) != len(density):
        errors.append("analog density record_id values are not unique")
    for index, row in enumerate(density, start=2):
        missing = [field for field in required_density if not row.get(field, "").strip()]
        if missing:
            errors.append(f"{DENSITY.name}:{index} missing {missing}")
        if row["uncertainty_unit"] not in {"relative", "g/cm^3"}:
            errors.append(f"{DENSITY.name}:{index} invalid uncertainty unit")
        if row["measurement_role"] != "analog":
            errors.append(f"{DENSITY.name}:{index} invalid evidence role")
        try:
            if not 0.0 <= float(row["solute_mole_fraction"]) <= 1.0:
                errors.append(f"{DENSITY.name}:{index} composition outside [0, 1]")
            if float(row["density_g_cm3"]) <= 0.0:
                errors.append(f"{DENSITY.name}:{index} nonpositive density")
        except ValueError:
            errors.append(f"{DENSITY.name}:{index} nonnumeric state or density")

    source_counts = Counter(row["source_key"] for row in density)
    if source_counts != {"Augusto2022": 84, "Dhage2026": 44}:
        errors.append(f"unexpected analog source counts: {dict(source_counts)}")

    derived = rows(DERIVED)
    if len(derived) != 44:
        errors.append(f"derived volume row count is {len(derived)}, expected 44")
    density_ids = {row["record_id"] for row in density}
    for index, row in enumerate(derived, start=2):
        if row["density_record_id"] not in density_ids:
            errors.append(f"{DERIVED.name}:{index} missing parent density")
            continue
        try:
            x = float(row["solute_mole_fraction"])
            mw = float(row["water_molar_mass_g_mol"])
            ms = float(row["solute_molar_mass_g_mol"])
            rho = float(row["mixture_density_g_cm3"])
            rho_w = float(row["water_density_g_cm3"])
            rho_s = float(row["solute_density_g_cm3"])
            reported = float(row["reported_excess_molar_volume_cm3_mol"])
            recalculated = (
                ((1.0 - x) * mw + x * ms) / rho
                - (1.0 - x) * mw / rho_w
                - x * ms / rho_s
            )
            if abs(recalculated - reported) > 0.01:
                errors.append(
                    f"{DERIVED.name}:{index} excess volume differs by "
                    f"{abs(recalculated - reported):.6g} cm^3/mol"
                )
        except ValueError:
            errors.append(f"{DERIVED.name}:{index} nonnumeric derivation input")
        if (
            row["measurement_role"] != "model_derived"
            or row["lifecycle_status"] != "diagnostic_only"
        ):
            errors.append(f"{DERIVED.name}:{index} derived evidence is target-eligible")

    for index, row in enumerate(rows(SOURCES), start=2):
        artifact_hash = row["acquired_artifact_sha256"]
        if artifact_hash and (
            len(artifact_hash) != 64
            or any(character not in "0123456789abcdef" for character in artifact_hash)
        ):
            errors.append(f"{SOURCES.name}:{index} invalid artifact SHA-256")
        if not row["source_key"] or not row["citation"] or not row["access_status"]:
            errors.append(f"{SOURCES.name}:{index} incomplete source identity")

    contract = rows(CONTRACT)
    family_counts = Counter(row["data_family"] for row in contract)
    expected_families = {
        "unloaded_mea_density": 35,
        "reactive_mea_density": 68,
        "ethanolammonium_carboxylate_density": 128,
        "speciation": 1070,
    }
    if family_counts != expected_families:
        errors.append(f"unexpected contract family counts: {dict(family_counts)}")
    if len({row["observation_id"] for row in contract}) != len(contract):
        errors.append("combined observation IDs are not unique")

    amundsen_density = [row for row in rows(AMUNDSEN) if row["property"] == "density"]
    amundsen_contract = [
        row
        for row in contract
        if row["data_family"] in {"unloaded_mea_density", "reactive_mea_density"}
    ]
    for source, bound in zip(amundsen_density, amundsen_contract, strict=True):
        preserved = (
            source["value"] == bound["value_reported"]
            and source["value_unit"] == bound["reported_unit"]
            and source["uncertainty_value"] == bound["uncertainty_value"]
            and source["uncertainty_unit"] == bound["uncertainty_unit"]
            and source["measurement_role"] == bound["measurement_role"]
            and source["lifecycle_status"] == bound["source_lifecycle_status"]
        )
        if not preserved:
            errors.append(f"Amundsen round trip failed for {bound['observation_id']}")

    membership = {row["membership_id"]: row for row in rows(SPECIATION)}
    speciation_contract = [row for row in contract if row["data_family"] == "speciation"]
    for bound in speciation_contract:
        source = membership.get(bound["observation_id"])
        if not source:
            errors.append(f"missing speciation membership {bound['observation_id']}")
            continue
        if (
            source["measurement_role"] != bound["measurement_role"]
            or source["lifecycle_status"] != bound["contract_lifecycle_status"]
            or source["target_eligible"] != bound["target_eligible"]
        ):
            errors.append(f"speciation role round trip failed for {bound['observation_id']}")

    objective_roles = {row["objective_role"] for row in speciation_contract}
    required_roles = {
        "direct_measurement",
        "aggregate_measurement",
        "inferred_not_independent",
        "calibration_contextual",
        "contextual",
        "held_out",
    }
    if not required_roles <= objective_roles:
        errors.append(f"speciation objective-role coverage is incomplete: {objective_roles}")
    executable_zeros = [
        row["observation_id"]
        for row in speciation_contract
        if "zero" in row["measurement_role"] and row["target_eligible"] == "yes"
    ]
    if executable_zeros:
        errors.append(f"speciation zeros lack source-backed censor bounds: {executable_zeros}")

    split = rows(SPLIT)
    if len(split) != 231:
        errors.append(f"volumetric split row count is {len(split)}, expected 231")
    split_counts = Counter(row["split"] for row in split)
    if split_counts != {"training": 153, "validation": 78}:
        errors.append(f"unexpected volumetric split counts: {dict(split_counts)}")
    group_splits: dict[str, set[str]] = defaultdict(set)
    for row in split:
        group_splits[row["group_id"]].add(row["split"])
    leaking = [group for group, assignments in group_splits.items() if len(assignments) != 1]
    if leaking:
        errors.append(f"split leakage across complete groups: {leaking}")
    shared_water = [
        row
        for row in contract
        if row["group_id"] == "Dhage2026|shared_water_endpoint|T=298"
    ]
    if len(shared_water) != 4 or any(
        row["target_eligible"] != "no"
        or row["contract_lifecycle_status"] != "diagnostic_only"
        for row in shared_water
    ):
        errors.append("repeated Dhage pure-water endpoint is not contextualized")

    parameter_map = rows(PARAMETER_MAP)
    active = {
        row["parameter_identity"]
        for row in parameter_map
        if row["initial_disposition"] in {"future_fitted", "future_regularized_correction"}
    }
    if active != {"MEAH+::sigma", "MEAH+::epsilon_over_k", "MEACOO-::sigma"}:
        errors.append(f"unexpected preregistered active parameter map: {active}")

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    try:
        validate_gate0_preregistration(preregistration)
    except PreregistrationError as exc:
        errors.append(f"canonical Gate 0 preregistration failed: {exc}")
    if (
        preregistration["status"] != "GATE_0_FROZEN_EXECUTION_BLOCKED"
        or preregistration["execution_admission"]["admitted"] is not False
    ):
        errors.append("preregistration does not fail closed")
    if [row["identity"] for row in preregistration["active_coordinates"]] != [
        "MEAH+::sigma",
        "MEAH+::epsilon_over_k",
        "MEACOO-::sigma",
    ]:
        errors.append("Gate 0 active coordinate order has drifted")
    if preregistration["regularization"]["scale"] is not None:
        errors.append("Gate 0 invents an unsupported regularization scale")
    tracer = preregistration["tracer"]
    if tracer["selected_state_ids"] != [
        "vle_obs_0137",
        "Bottinger2008_state_049",
    ]:
        errors.append("Gate 0 reduced tracer identities have drifted")
    if [row["identity"] for row in tracer["active_coordinates"]] != [
        "MEAH+::sigma",
        "MEACOO-::sigma",
    ]:
        errors.append("Gate 0 reduced tracer coordinate order has drifted")
    if tracer["regularization"] != {
        "status": "NOT_REQUIRED_FOR_REDUCED_TRACER",
        "scale": None,
    }:
        errors.append("Gate 0 reduced tracer invents or requires regularization")
    if (
        tracer["provider_regression_input"]["status"]
        != "REGRESSION_INPUT_EXECUTABLE"
        or tracer["observations"][1]["evaluation_pressure_pa"] != 7326.7
        or tracer["observations"][1][
            "evaluation_pressure_source_observation_id"
        ]
        != "vle_obs_0137"
        or tracer["observations"][0]["source_observed_unit"] != "kPa"
        or tracer["observations"][0]["observed_unit"] != "Pa"
        or tracer["observations"][0]["source_to_residual_factor"] != 1000.0
        or tracer["observations"][1]["observed_unit"] != "mole_fraction"
    ):
        errors.append("Gate 0 reduced tracer Provider input has drifted")
    if [
        (row["family"], row["state_id"])
        for row in tracer["observations"]
    ] != [
        ("pco2", "vle_obs_0137"),
        ("speciation", "Bottinger2008_state_049"),
    ]:
        errors.append("Gate 0 reduced tracer observation contract has drifted")
    if tracer["numerical_acceptance"]["required_row_accounting"] != {
        "input": 2,
        "evaluated": 2,
        "dropped": 0,
        "skipped": 0,
        "failed": 0,
    }:
        errors.append("Gate 0 reduced tracer accounting has drifted")
    if preregistration["execution_admission"]["blockers"] != [
        "composed_homogeneous_liquid_observable_receipt_missing",
        "regression_mixed_observation_receipt_missing",
        "tracer_rank_preflight_pending",
    ]:
        errors.append("Gate 0 retains a resolved reduced-tracer blocker")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "Volumetric evidence valid: 128 analog densities, 44 derived diagnostics, "
        "103 Amundsen densities, 1070 speciation memberships, "
        "and frozen 153/78 volumetric split."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
