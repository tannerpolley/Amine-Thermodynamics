from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "reference" / "MEA"
INVENTORY = LIBRARY / "manifests" / "data_library_inventory.csv"
MODEL_CONFIGURATIONS = LIBRARY / "manifests" / "reactive_vle_model_configurations.json"
PARAMETER_STAGES = LIBRARY / "manifests" / "reactive_vle_parameter_stages.json"
CROSS_VALIDATION = LIBRARY / "manifests" / "reactive_vle_cross_validation.csv"
READINESS = ROOT / "analyses/reactive_epcsaft_parameter_evidence/results/readiness/regression_readiness_summary.json"
SPLIT = LIBRARY / "manifests/grouped_split_manifest.csv"
ADMISSION_BASELINE = None
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
)
EXPECTED_ROWS = {
    "observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv": 327,
    "observations/vapor_liquid_equilibrium/Combined_VLE.csv": 162,
    "observations/liquid_speciation/Canonical_Combined_ChEq.csv": 639,
    "observations/ionic_analog_volumetrics/ethanolammonium_carboxylate_density.csv": 128,
    "observations/ionic_analog_volumetrics/ethanolammonium_carboxylate_excess_molar_volume.csv": 44,
}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".tex", ".txt", ".yaml", ".yml"}
LONG_TEXT_WORDS = {
    "diisopropanolamine",
    "dimethylethanolamines",
    "hydroxyethylammonium",
    "methyldiethanolamine",
    "monoethanolammonium",
    "monoethyleneglycol",
    "multiconcentration",
    "piperidinemethanol",
}
STALE_PATHS = (
    "data/reference/MEA/VLE",
    "data/reference/MEA/ChEq",
    "data/reference/MEA/density_viscosity",
    "data/reference/MEA/dielectric",
    "data/reference/MEA/ionic_activity",
    "data/reference/MEA/pH",
    "data/reference/MEA/volumetric",
)
CROSS_VALIDATION_FIELDS = (
    "observation_id",
    "observable_family",
    "source_key",
    "source_file",
    "source_file_sha256",
    "source_row_identity",
    "source_locator",
    "temperature_K",
    "temperature_reported_C",
    "temperature_conversion",
    "mea_mass_fraction",
    "co2_loading_mol_per_mol_mea",
    "measurement_role",
    "measurement_identity",
    "observed_value",
    "reported_basis",
    "linear_coefficients",
    "state_pressure_pa",
    "uncertainty_status",
    "covariance_status",
    "campaign_block_id",
    "cross_validation_fold",
    "domain_role",
    "model_selection_role",
    "final_fit_role",
    "eligibility_contract",
    "admission_status",
    "admission_blockers",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def _classification(relative: Path) -> tuple[str, str, str]:
    parts = relative.parts
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


def _resolve_source_file(source_file: str, observation_family: str) -> Path:
    family_root = LIBRARY / "observations" / observation_family
    declared = ROOT / source_file
    if not declared.is_file() and Path(source_file).name == source_file:
        declared = family_root / source_file
    if not declared.is_file() or not declared.resolve().is_relative_to(
        family_root.resolve()
    ):
        raise ValueError(
            f"Source file does not exist in its declared observation family: {source_file}"
        )
    return declared


def _domain_role(temperature_c: str) -> str:
    temperature = float(temperature_c)
    if temperature < 40.0:
        return "low_temperature_support"
    if temperature <= 50.0:
        return "current_R4_R5_source_domain"
    if temperature <= 80.0:
        return "planned_absorber_domain_requires_R4_R5_extension"
    return "high_temperature_challenge"


def baseline_directory() -> Path:
    path = ADMISSION_BASELINE or ROOT / json.loads(READINESS.read_text())["baseline_dir"]
    preflight = json.loads((path.parent / "preflight.json").read_text())
    if any(_sha256(path / name) != expected for name, expected in preflight["baseline_file_hashes"].items()):
        raise ValueError("Frozen admission baseline hash drift")
    return path


def cross_validation_rows() -> list[dict[str, str]]:
    vle_rows = {
        row["observation_id"]: row
        for row in _read_dicts(
            LIBRARY
            / "observations"
            / "vapor_liquid_equilibrium"
            / "Canonical_VLE_Observations.csv"
        )
    }
    speciation_rows = {
        row["record_id"]: row
        for row in _read_dicts(
            LIBRARY
            / "observations"
            / "liquid_speciation"
            / "Canonical_Combined_ChEq.csv"
        )
    }
    rows: list[dict[str, str]] = []
    for metrology in _read_dicts(LIBRARY / "manifests" / "pco2_metrology_manifest.csv"):
        if metrology["target_eligible"] != "yes":
            continue
        observation = vle_rows[metrology["observation_id"]]
        source_path = _resolve_source_file(
            observation["source_file"], "vapor_liquid_equilibrium"
        )
        temperature_c = observation["temperature_reported_C"]
        rows.append(
            {
                "observation_id": observation["observation_id"],
                "observable_family": "pco2",
                "source_key": observation["source_key"],
                "source_file": source_path.relative_to(ROOT).as_posix(),
                "source_file_sha256": _sha256(source_path),
                "source_row_identity": observation["source_row"],
                "source_locator": metrology["source_locator"],
                "temperature_K": str(float(temperature_c) + 273.15),
                "temperature_reported_C": temperature_c,
                "temperature_conversion": "T_K=T_C+273.15",
                "mea_mass_fraction": observation["MEA_weight_fraction"],
                "co2_loading_mol_per_mol_mea": observation["CO2_loading"],
                "measurement_role": metrology["measurement_origin"],
                "measurement_identity": metrology["measured_primitive"],
                "observed_value": metrology["observed_pco2_kpa"],
                "reported_basis": "kPa",
                "linear_coefficients": "",
                "state_pressure_pa": metrology["state_pressure_pa"],
                "uncertainty_status": metrology["uncertainty_status"],
                "covariance_status": metrology["covariance_status"],
                "campaign_block_id": f"pco2|{observation['replicate_group']}",
                "domain_role": _domain_role(temperature_c),
                "eligibility_contract": "pco2_metrology_manifest.csv",
                "admission_status": "candidate_not_executable",
                "admission_blockers": "residual_scale_missing;immutable_data_packet_missing",
            }
        )
    for membership in _read_dicts(
        LIBRARY / "manifests" / "speciation_target_membership.csv"
    ):
        if membership["target_eligible"] != "yes":
            continue
        source_path = _resolve_source_file(
            membership["source_file"], "liquid_speciation"
        )
        measurement = speciation_rows[membership["measurement_identity"]]
        temperature_c = membership["temperature_C"]
        rows.append(
            {
                "observation_id": membership["membership_id"],
                "observable_family": "speciation",
                "source_key": membership["source_key"],
                "source_file": source_path.relative_to(ROOT).as_posix(),
                "source_file_sha256": _sha256(source_path),
                "source_row_identity": membership["source_row_index"],
                "source_locator": f"{membership['source_file']}:row={membership['source_row_index']}",
                "temperature_K": measurement["temperature_K"],
                "temperature_reported_C": temperature_c,
                "temperature_conversion": "canonical_source_temperature_K",
                "mea_mass_fraction": membership["mea_mass_fraction"],
                "co2_loading_mol_per_mol_mea": membership[
                    "co2_loading_mol_per_mol_mea"
                ],
                "measurement_role": membership["measurement_role"],
                "measurement_identity": membership["measurement_identity"],
                "observed_value": measurement["reported_value"],
                "reported_basis": membership["reported_basis"],
                "linear_coefficients": membership["linear_coefficients"],
                "state_pressure_pa": (
                    f"{float(measurement['pressure_bar']) * 100000:.12g}"
                    if measurement["pressure_bar"]
                    else ""
                ),
                "uncertainty_status": "source_uncertainty_not_bound_in_membership_contract",
                "covariance_status": membership["covariance_status"],
                "campaign_block_id": (
                    f"speciation|{membership['source_key']}|w={membership['mea_mass_fraction']}|T={temperature_c}"
                ),
                "domain_role": _domain_role(temperature_c),
                "eligibility_contract": "speciation_target_membership.csv",
                "admission_status": "candidate_not_executable",
                "admission_blockers": (
                    "residual_scale_missing;state_pressure_contract_missing;immutable_data_packet_missing"
                ),
            }
        )

    baseline = {row["observation_id"]: row for row in _read_dicts(baseline_directory() / CROSS_VALIDATION.name)}
    group_fold = {row["campaign_block_id"]: int(row["cross_validation_fold"].split("_")[-1]) for row in baseline.values()}
    for row in rows:
        if row["observation_id"] in baseline:
            row["campaign_block_id"] = baseline[row["observation_id"]]["campaign_block_id"]
    for family in sorted({row["observable_family"] for row in rows}):
        grouped = Counter(
            row["campaign_block_id"]
            for row in rows
            if row["observable_family"] == family
        )
        fold_load = [sum(size for group, size in grouped.items() if group_fold.get(group) == fold + 1) for fold in range(5)]
        for group, size in sorted(
            grouped.items(), key=lambda item: (-item[1], item[0])
        ):
            if group in group_fold:
                continue
            fold = min(
                range(5), key=lambda candidate: (fold_load[candidate], candidate)
            )
            group_fold[group] = fold + 1
            fold_load[fold] += size
    for row in rows:
        row["cross_validation_fold"] = f"fold_{group_fold[row['campaign_block_id']]}"
        row["model_selection_role"] = (
            "candidate_partition_only_pending_residual_scale"
            if row["domain_role"]
            in {"low_temperature_support", "current_R4_R5_source_domain"}
            else "non_scoring_domain_extension"
        )
        row["final_fit_role"] = {
            "low_temperature_support": "all_admissible_current_source_domain",
            "current_R4_R5_source_domain": "all_admissible_current_source_domain",
            "planned_absorber_domain_requires_R4_R5_extension": "after_R4_R5_domain_extension",
            "high_temperature_challenge": "future_high_temperature_extension",
        }[row["domain_role"]]
    return sorted(
        rows, key=lambda row: (row["observable_family"], row["observation_id"])
    )


def cross_validation_bytes(rows=None) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=CROSS_VALIDATION_FIELDS, lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(cross_validation_rows() if rows is None else rows)
    return stream.getvalue().encode()


def grouped_split_rows() -> list[dict[str, str]]:
    baseline = _read_dicts(baseline_directory() / SPLIT.name)
    current = {}
    for family, path, identity, temperature, fraction in (
        ("vle_pressure", LIBRARY / "observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv", "observation_id", "temperature_reported_C", "MEA_weight_fraction"),
        ("speciation", LIBRARY / "manifests/speciation_target_membership.csv", "state_id", "temperature_C", "mea_mass_fraction"),
    ):
        for row in _read_dicts(path):
            if row["lifecycle_status"] in {"active_v1", "validation_reserved_candidate", "canonical_eligible", "validation_reserved"}:
                current.setdefault((family, row[identity]), (row, temperature, fraction))
    if set(current) != {(row["target_family"], row["record_id"]) for row in baseline}:
        raise ValueError("Unapproved grouped-split state membership change")
    for row in baseline:
        source, temperature, fraction = current[(row["target_family"], row["record_id"])]
        row.update(mea_mass_fraction=source[fraction], temperature_C=source[temperature], lifecycle_status=source["lifecycle_status"], source_hash=_sha256(ROOT / row["source_path"]))
    return baseline


def readiness_summary(cv, split, outputs) -> dict:
    summary = json.loads(READINESS.read_text())
    sources = set(summary["source_hashes"]) | {row["source_file"] for row in cv}
    sources.update((LIBRARY / "observations/vapor_liquid_equilibrium" / row["source_file"]).relative_to(ROOT).as_posix() for row in _read_dicts(LIBRARY / "observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv"))
    sources.update(row["source_file"] for row in _read_dicts(LIBRARY / "observations/liquid_speciation/Canonical_Combined_ChEq.csv"))
    sources.update(path.relative_to(ROOT).as_posix() for path in baseline_directory().iterdir() if path.is_file())
    sources.update(["data/reference/MEA/manifests/speciation_linear_coefficient_rules.csv", "data/reference/MEA/manifests/target_admission_manifest.csv", "analyses/mea_parameter_bundle/results/source-corrections-152/current-volumetric-admission.json"])
    summary.update(source_hashes={name: _sha256(ROOT / name) for name in sorted(sources)},
                   baseline_dir=baseline_directory().relative_to(ROOT).as_posix(), target_admission=_read_dicts(LIBRARY / "manifests/target_admission_manifest.csv"),
                   row_counts=dict(Counter(row["target_family"] for row in split)), role_counts=dict(Counter(row["role"] for row in split)),
                   lifecycle_counts=dict(Counter(row["lifecycle_status"] for row in split)), candidate_counts=dict(Counter(row["observable_family"] for row in cv)),
                   executable_observation_counts={"speciation": 0, "vle_pressure": 0}, admitted_target_families=[], upstream_execution_admitted=False,
                   capability_metadata_status="retained/unrequalified; no Engine import or capability probe",
                   blocking_conditions={"application_admission": "Candidate views only; execution not admitted; immutable qualification/scales and source-pressure/uncertainty contracts incomplete. Calorimetry admission/path repair remains147-owned."})
    partitions = {}
    for row in split:
        partitions.setdefault(row["group_id"], set()).add(row["split"])
    summary["leakage_findings"] = sorted(group for group, assignments in partitions.items() if len(assignments) != 1)
    summary["uncertainty_coverage"] = {"speciation_rows_with_numeric_uncertainty": 0, "vle_rows_with_reported_loading_or_pressure_uncertainty": sum(bool(row["CO2_loading_uncertainty"] or row["CO2_pressure_uncertainty"]) for row in _read_dicts(LIBRARY / "observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv"))}
    summary["output_hashes"] = {path.relative_to(ROOT).as_posix(): hashlib.sha256(data).hexdigest() for path, data in outputs.items()}
    summary["source_hashes"].update(summary["output_hashes"])
    summary["split_hash"] = summary["output_hashes"][SPLIT.relative_to(ROOT).as_posix()]
    return summary


def write_admission_outputs(*, check=False) -> list[str]:
    cv, split = cross_validation_rows(), grouped_split_rows()
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(split[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(split)
    outputs = {CROSS_VALIDATION: cross_validation_bytes(cv), SPLIT: stream.getvalue().encode()}
    summary = readiness_summary(cv, split, outputs)
    outputs[READINESS] = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    stale = [path.relative_to(ROOT).as_posix() for path, data in outputs.items() if check and path.read_bytes() != data]
    if not check:
        for path, data in outputs.items():
            path.write_bytes(data)
    return stale


def validate() -> list[str]:
    errors: list[str] = []
    for path in sorted(LIBRARY.rglob("*.csv")):
        for line, row in enumerate(_read_dicts(path), start=2):
            for column, value in row.items():
                for token in re.findall(
                    r"(?<![A-Za-z0-9_])[a-z]{18,}(?![A-Za-z0-9_])", value or ""
                ):
                    if token not in LONG_TEXT_WORDS:
                        errors.append(
                            f"Possible missing spaces in {path.relative_to(LIBRARY)}:"
                            f"{line} column {column}: {token!r}"
                        )
    for relative in REQUIRED_DIRECTORIES:
        if not (LIBRARY / relative).is_dir():
            errors.append(f"Missing required evidence-library directory: {relative}")

    if not INVENTORY.is_file():
        errors.append(f"Missing generated inventory: {INVENTORY.relative_to(ROOT)}")
    elif INVENTORY.read_bytes() != inventory_bytes():
        errors.append(
            "data_library_inventory.csv is stale; run this script with --write"
        )

    for relative, expected in EXPECTED_ROWS.items():
        path = LIBRARY / relative
        if not path.is_file():
            errors.append(f"Missing row-count sentinel: {relative}")
        elif _csv_rows(path) != expected:
            errors.append(
                f"Scientific row-count drift in {relative}: expected {expected}, found {_csv_rows(path)}"
            )

    if not MODEL_CONFIGURATIONS.is_file():
        errors.append("Missing predictive reactive-VLE model-configuration contract")
    else:
        configurations = json.loads(MODEL_CONFIGURATIONS.read_text(encoding="utf-8"))
        if (
            configurations.get("execution_status")
            != "ENGINE_OBSERVATIONS_ADMITTED_APPLICATION_INPUTS_INCOMPLETE"
        ):
            errors.append(
                "Model-configuration contract must distinguish admitted Engine "
                "support from incomplete application inputs"
            )
        variants = configurations.get("configurations", [])
        variant_ids = [variant.get("configuration_id") for variant in variants]
        if variant_ids != [
            "SHELL_BORN_SOLVENT_ONLY_INDUCED",
            "SHELL_BORN_ION_SUPPRESSED_INDUCED",
        ]:
            errors.append(
                "Model-configuration identities must be the two retained "
                f"induced-association Born formulations: {variant_ids}"
            )
        if any(
            variant.get("association")
            != "Schick-Pabsch reciprocal CO2-water 2B topology"
            for variant in variants
        ):
            errors.append(
                "Every retained configuration must use the fixed induced-association topology"
            )
        if any(variant.get("promotion_eligible") is not False for variant in variants):
            errors.append(
                "No retained configuration may be promotion-eligible before row admission"
            )

    if not PARAMETER_STAGES.is_file():
        errors.append("Missing predictive reactive-VLE parameter-stage contract")
    else:
        stages = json.loads(PARAMETER_STAGES.read_text(encoding="utf-8"))
        stage_ids = [stage["stage_id"] for stage in stages.get("stages", [])]
        if stage_ids != [f"S{index}" for index in range(8)]:
            errors.append(
                f"Parameter-stage identities must be S0 through S7 in order: {stage_ids}"
            )

    if not CROSS_VALIDATION.is_file():
        errors.append("Missing campaign-blocked reactive-VLE cross-validation manifest")
    elif CROSS_VALIDATION.read_bytes() != cross_validation_bytes():
        errors.append(
            "reactive_vle_cross_validation.csv is stale; run this script with --write"
        )
    else:
        cross_validation = _read_dicts(CROSS_VALIDATION)
        family_counts = Counter(row["observable_family"] for row in cross_validation)
        if any(
            not row["source_locator"] or not row["source_file_sha256"]
            for row in cross_validation
        ):
            errors.append(
                "Every cross-validation row must retain a source locator and source-file hash"
            )
        if any(
            not row["observed_value"] or not row["reported_basis"]
            for row in cross_validation
        ):
            errors.append(
                "Every cross-validation row must retain the observed value and reported basis"
            )
        if any(
            row["model_selection_role"] == "campaign_blocked_cross_validation"
            for row in cross_validation
        ):
            errors.append(
                "Candidate observations cannot become scoring rows before residual scales are frozen"
            )
        if any(
            row["admission_status"] != "candidate_not_executable"
            for row in cross_validation
        ):
            errors.append(
                "Cross-validation candidates cannot be marked executable before admission gates close"
            )
        group_folds: dict[str, set[str]] = {}
        for row in cross_validation:
            group_folds.setdefault(row["campaign_block_id"], set()).add(
                row["cross_validation_fold"]
            )
        leaking = sorted(
            group for group, folds in group_folds.items() if len(folds) != 1
        )
        if leaking:
            errors.append(
                f"Campaign blocks leak across cross-validation folds: {leaking}"
            )
        family_folds = {
            family: {
                row["cross_validation_fold"]
                for row in cross_validation
                if row["observable_family"] == family
            }
            for family in family_counts
        }
        expected_folds = {f"fold_{index}" for index in range(1, 6)}
        incomplete_families = {
            family: folds
            for family, folds in family_folds.items()
            if folds != expected_folds
        }
        if incomplete_families:
            errors.append(
                f"Every observable family must span all five campaign folds: {incomplete_families}"
            )

    split = _read_dicts(LIBRARY / "manifests" / "grouped_split_manifest.csv")
    split_roles = Counter(row["role"] for row in split)
    if split_roles != Counter(row["role"] for row in grouped_split_rows()):
        errors.append(f"Frozen regression split drift: {dict(split_roles)}")
    volumetric_split = _read_dicts(
        LIBRARY / "manifests" / "volumetric_grouped_split_manifest.csv"
    )
    volumetric_roles = Counter(row["role"] for row in volumetric_split)
    if volumetric_roles != Counter(json.loads((baseline_directory().parent / "current-volumetric-admission.json").read_text())["role_counts"]):
        errors.append(f"Frozen volumetric split drift: {dict(volumetric_roles)}")

    for path in ROOT.rglob("*"):
        if any(part in {"tmp", ".venv", ".git", "baseline"} for part in path.relative_to(ROOT).parts):
            continue
        if (
            not path.is_file()
            or path == Path(__file__)
            or path.suffix.lower() not in TEXT_SUFFIXES
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for stale in STALE_PATHS:
            if stale in text:
                errors.append(
                    f"Stale evidence path {stale!r} in {path.relative_to(ROOT)}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or validate the MEA evidence-library inventory."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate the machine-readable file inventory.",
    )
    parser.add_argument("--write-admission", action="store_true")
    parser.add_argument("--check-admission", action="store_true")
    parser.add_argument("--write-inventory", action="store_true")
    parser.add_argument("--baseline-dir", type=Path)
    args = parser.parse_args()
    global ADMISSION_BASELINE
    ADMISSION_BASELINE = (ROOT / args.baseline_dir).resolve() if args.baseline_dir else None
    if args.write_admission or args.check_admission:
        return bool(write_admission_outputs(check=args.check_admission))
    if args.write_inventory:
        INVENTORY.write_bytes(inventory_bytes())
        return 0
    if args.write:
        write_admission_outputs()
        INVENTORY.write_bytes(inventory_bytes())
        print(
            f"Wrote {CROSS_VALIDATION.relative_to(ROOT)} with {len(cross_validation_rows())} observations."
        )
        print(
            f"Wrote {INVENTORY.relative_to(ROOT)} with {len(inventory_rows())} artifacts."
        )
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("MEA evidence-library validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
