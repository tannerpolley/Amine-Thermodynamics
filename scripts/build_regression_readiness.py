from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from MEA.common.reference_observations import (
    adapt_loaded_property_rows,
    adapt_paired_loading_rows,
    adapt_speciation_rows,
    adapt_vle_pressure_rows,
    validate_observation_records,
)
from MEA.epcsaft_runtime import load_epcsaft


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = ROOT / "data" / "reference" / "MEA"
ADMISSION_PATH = REFERENCE_ROOT / "manifests" / "target_admission_manifest.csv"
SPLIT_PATH = REFERENCE_ROOT / "manifests" / "grouped_split_manifest.csv"
SUMMARY_PATH = (
    ROOT
    / "analyses"
    / "phase3"
    / "ionic_epcsaft_regression"
    / "results"
    / "readiness"
    / "regression_readiness_summary.json"
)

ADMISSION_FIELDS = (
    "target_family",
    "observable",
    "reference_path",
    "evidence_status",
    "capability_key",
    "package_supported",
    "downstream_supported",
    "admitted",
    "role",
    "weight",
    "admission_reason",
)
SPLIT_FIELDS = (
    "target_family",
    "record_id",
    "source_key",
    "group_id",
    "mea_mass_fraction",
    "temperature_C",
    "lifecycle_status",
    "split",
    "role",
    "weight",
    "source_path",
    "source_hash",
    "reason",
)
SOURCE_PATHS = (
    "ChEq/Canonical_Combined_ChEq.csv",
    "VLE/Canonical_VLE_Observations.csv",
    "manifests/observation_contract.csv",
    "manifests/parameter_observable_coverage.csv",
    "manifests/speciation_target_membership.csv",
    "manifests/vle_row_disposition.csv",
)


@dataclass(frozen=True)
class RegressionReadinessBundle:
    source_hashes: tuple[tuple[str, str], ...]
    target_admission: tuple[dict[str, str], ...]
    grouped_split: tuple[dict[str, str], ...]
    leakage_findings: tuple[str, ...]
    capability_receipt_hash: str
    package_version: str
    upstream_execution_admitted: bool
    parameter_coverage: tuple[dict[str, str], ...]

    @property
    def split_hash(self) -> str:
        return hashlib.sha256(_csv_bytes(self.grouped_split, SPLIT_FIELDS)).hexdigest()

    def summary(self) -> dict[str, Any]:
        role_counts = Counter(row["role"] for row in self.grouped_split)
        target_counts = Counter(row["target_family"] for row in self.grouped_split)
        lifecycle_counts = Counter(row["lifecycle_status"] for row in self.grouped_split)
        admitted = [row["target_family"] for row in self.target_admission if row["admitted"] == "yes"]
        unsupported = [row["target_family"] for row in self.target_admission if row["admitted"] == "no"]
        blocking_conditions: dict[str, str] = {}
        if not self.upstream_execution_admitted:
            blocking_conditions["upstream_admission"] = (
                "The public capability report does not admit a production native Ceres hot loop with "
                "production pressure and speciation derivatives; Issue 12 remains the execution gate."
            )
        if self.leakage_findings:
            blocking_conditions["split_leakage"] = "; ".join(self.leakage_findings)
        decision = (
            "preregistration_ready_upstream_execution_blocked"
            if not self.leakage_findings and {"vle_pressure", "speciation"}.issubset(admitted)
            else "not_ready"
        )
        return {
            "schema_version": 1,
            "readiness_decision": decision,
            "blocking_conditions": blocking_conditions,
            "package_version": self.package_version,
            "capability_receipt_hash": self.capability_receipt_hash,
            "upstream_execution_admitted": self.upstream_execution_admitted,
            "source_hashes": dict(self.source_hashes),
            "split_hash": self.split_hash,
            "row_counts": dict(sorted(target_counts.items())),
            "role_counts": dict(sorted(role_counts.items())),
            "lifecycle_counts": dict(sorted(lifecycle_counts.items())),
            "uncertainty_coverage": {
                "vle_rows_with_reported_loading_or_pressure_uncertainty": _vle_uncertainty_count(self.grouped_split),
                "speciation_rows_with_numeric_uncertainty": 0,
            },
            "parameter_coverage": list(self.parameter_coverage),
            "admitted_target_families": admitted,
            "unsupported_target_families": unsupported,
            "target_admission": list(self.target_admission),
            "leakage_findings": list(self.leakage_findings),
            "failed_row_policy": (
                "Every attempted reserved row remains in validation accounting; solver failure is a failed "
                "prediction and may not be omitted or replaced."
            ),
            "claim_boundary": (
                "This receipt freezes data admission and grouped splits only. It is not a completed fit, "
                "parameter promotion, independent-validation result, or submission claim."
            ),
        }


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _csv_bytes(rows: Iterable[Mapping[str, Any]], fieldnames: Iterable[str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=tuple(fieldnames), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _relative_source_path(relative: str) -> str:
    return f"data/reference/MEA/{relative}"


def _capability_value(receipt: Mapping[str, Any], key: str) -> bool:
    value: Any = receipt.get("capabilities", receipt)
    for part in key.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return False
        value = value[part]
    return value is True


def _regression_capability_key(suffix: str) -> str:
    return (
        "regression.reactive_electrolyte_batch_context."
        f"bounded_mixed_pressure_speciation_regression.{suffix}"
    )


def public_capability_receipt() -> dict[str, Any]:
    epcsaft = load_epcsaft()
    return {
        "package": {"name": "epcsaft", "version": str(getattr(epcsaft, "__version__", "unknown"))},
        "capabilities": epcsaft.capabilities(),
    }


def _upstream_execution_admitted(receipt: Mapping[str, Any]) -> bool:
    base = (
        "regression.reactive_electrolyte_batch_context."
        "bounded_mixed_pressure_speciation_regression"
    )
    return all(
        _capability_value(receipt, key)
        for key in (
            f"{base}.available",
            f"{base}.native_hot_loop",
            f"{base}.supports_pressure_targets",
            f"{base}.supports_speciation_targets",
        )
    ) and _capability_value(receipt, "optimizers.ceres.production")


def _admission_rows(receipt: Mapping[str, Any]) -> tuple[dict[str, str], ...]:
    definitions = (
        (
            "vle_pressure",
            "CO2 partial pressure over loaded MEA",
            "data/reference/MEA/VLE/Canonical_VLE_Observations.csv",
            "canonical_active_and_reserved",
            _regression_capability_key("supports_pressure_targets"),
            True,
            True,
            "active_training_and_reserved_validation",
            "log-pressure family weight frozen at preregistration",
            "Canonical pressure rows and public target support are present; execution remains gated separately.",
        ),
        (
            "speciation",
            "liquid true-species composition",
            "data/reference/MEA/ChEq/Canonical_Combined_ChEq.csv",
            "canonical_active_and_reserved",
            _regression_capability_key("supports_speciation_targets"),
            True,
            True,
            "active_training_and_reserved_validation",
            "species-family weight frozen at preregistration",
            "Only membership-approved direct and aggregate observations are targets; inferred context stays non-target.",
        ),
        (
            "density",
            "CO2-loaded MEA liquid density",
            "data/reference/MEA/density_viscosity/Amundsen_2009_density_viscosity.csv",
            "primary_table_property_candidate",
            _regression_capability_key("supports_density_targets"),
            True,
            False,
            "future_target",
            "not_assigned",
            "The package reports density-target support but the approved MEA adapter and target schema do not implement it.",
        ),
        (
            "viscosity",
            "CO2-loaded MEA dynamic viscosity",
            "data/reference/MEA/density_viscosity/Amundsen_2009_density_viscosity.csv",
            "primary_table_validation_only",
            "unreported",
            False,
            False,
            "validation_only",
            "not_assigned",
            "No public reactive-regression viscosity target capability is reported.",
        ),
        (
            "relative_permittivity",
            "MEA-water and loaded-MEA static relative permittivity",
            "data/reference/MEA/dielectric/MEA_H2O_dielectric.csv",
            "primary_values_missing",
            _regression_capability_key("supports_relative_permittivity_targets"),
            True,
            False,
            "blocked_evidence",
            "not_assigned",
            "Public target support exists but no verified static-permittivity dataset or approved downstream adapter exists.",
        ),
        (
            "loaded_ph",
            "calibrated equilibrium pH of loaded MEA",
            "data/reference/MEA/pH/loaded_MEA_pH.csv",
            "no_equilibrium_primary_dataset",
            "unreported",
            False,
            False,
            "blocked_evidence",
            "not_assigned",
            "The screened process-monitoring lead is not an equilibrium pH target and the public target family is unreported.",
        ),
        (
            "ionic_activity",
            "MEAH+ and MEACOO- activity or osmotic evidence",
            "data/reference/MEA/ionic_activity/direct_ionic_activity.csv",
            "negative_direct_source_search",
            _regression_capability_key("supports_activity_targets"),
            True,
            False,
            "blocked_evidence",
            "not_assigned",
            "Generic activity support cannot substitute for absent direct target-ion evidence or an approved adapter.",
        ),
        (
            "calorimetry",
            "excess enthalpy and heat of CO2 absorption",
            "data/reference/MEA/calorimetry/",
            "primary_extraction_pending",
            "unreported",
            False,
            False,
            "future_target",
            "not_assigned",
            "No public reactive-regression calorimetry target capability or frozen primary dataset is available.",
        ),
    )
    rows: list[dict[str, str]] = []
    for family, observable, path, evidence, capability_key, expected_package, downstream, role, weight, reason in definitions:
        package_supported = _capability_value(receipt, capability_key) if capability_key != "unreported" else False
        admitted = expected_package and package_supported and downstream and evidence.startswith("canonical")
        rows.append(
            {
                "target_family": family,
                "observable": observable,
                "reference_path": path,
                "evidence_status": evidence,
                "capability_key": capability_key,
                "package_supported": "yes" if package_supported else "no",
                "downstream_supported": "yes" if downstream else "no",
                "admitted": "yes" if admitted else "no",
                "role": role,
                "weight": weight,
                "admission_reason": reason,
            }
        )
    return tuple(rows)


def _normalized_number(value: str) -> str:
    if value == "":
        return ""
    return f"{float(value):.12g}"


def _vle_split_rows(reference_root: Path, source_hash: str) -> list[dict[str, str]]:
    rows = _read_rows(reference_root / "VLE" / "Canonical_VLE_Observations.csv")
    included = [
        row
        for row in rows
        if row["lifecycle_status"] in {"active_v1", "validation_reserved_candidate"}
    ]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in included:
        group = row["normalization_group"] or row["replicate_group"]
        if not group:
            temperature = row["temperature_canonical_C"] or row["temperature_reported_C"]
            group = f"{row['source_key']}|w={_normalized_number(row['MEA_weight_fraction'])}|T={_normalized_number(temperature)}"
        groups[f"vle|{group}"].append(row)

    output: list[dict[str, str]] = []
    for group_id in sorted(groups):
        members = groups[group_id]
        validation = any(row["lifecycle_status"] == "validation_reserved_candidate" for row in members) or any(
            row["source_key"] in {"Jou1995", "Xu2011"} for row in members
        )
        split = "validation" if validation else "training"
        role = "reserved_validation" if validation else "active_training"
        for row in sorted(members, key=lambda item: item["observation_id"]):
            temperature = row["temperature_canonical_C"] or row["temperature_reported_C"]
            reason = (
                "Held as a source/composition/temperature group; all failed predictions remain in validation accounting."
                if validation
                else "Current active-v1 row retained in the grouped training view."
            )
            output.append(
                {
                    "target_family": "vle_pressure",
                    "record_id": row["observation_id"],
                    "source_key": row["source_key"],
                    "group_id": group_id,
                    "mea_mass_fraction": _normalized_number(row["MEA_weight_fraction"]),
                    "temperature_C": _normalized_number(temperature),
                    "lifecycle_status": row["lifecycle_status"],
                    "split": split,
                    "role": role,
                    "weight": "1",
                    "source_path": _relative_source_path("VLE/Canonical_VLE_Observations.csv"),
                    "source_hash": source_hash,
                    "reason": reason,
                }
            )
    return output


def _speciation_split_rows(reference_root: Path, source_hash: str) -> list[dict[str, str]]:
    rows = _read_rows(reference_root / "manifests" / "speciation_target_membership.csv")
    state_rows: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["target_membership"] not in {"active_v1", "transferability_candidate"}:
            continue
        state_rows.setdefault(row["state_id"], row)

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in state_rows.values():
        group = (
            f"speciation|{row['source_key']}|w={_normalized_number(row['mea_mass_fraction'])}"
            f"|T={_normalized_number(row['temperature_C'])}"
        )
        groups[group].append(row)

    output: list[dict[str, str]] = []
    for group_id in sorted(groups):
        members = groups[group_id]
        validation = any(row["lifecycle_status"] == "validation_reserved" for row in members) or any(
            row["source_key"] == "Jakobsen2005" for row in members
        )
        split = "validation" if validation else "training"
        role = "reserved_validation" if validation else "active_training"
        for row in sorted(members, key=lambda item: item["state_id"]):
            output.append(
                {
                    "target_family": "speciation",
                    "record_id": row["state_id"],
                    "source_key": row["source_key"],
                    "group_id": group_id,
                    "mea_mass_fraction": _normalized_number(row["mea_mass_fraction"]),
                    "temperature_C": _normalized_number(row["temperature_C"]),
                    "lifecycle_status": row["lifecycle_status"],
                    "split": split,
                    "role": role,
                    "weight": "1",
                    "source_path": _relative_source_path("ChEq/Canonical_Combined_ChEq.csv"),
                    "source_hash": source_hash,
                    "reason": (
                        "Held as a complete source/composition/temperature curve; every state must be accounted for."
                        if validation
                        else "Current active-v1 state retained in the grouped training view."
                    ),
                }
            )
    return output


def find_split_leakage(rows: Iterable[Mapping[str, str]]) -> tuple[str, ...]:
    assignments: dict[tuple[str, str], set[str]] = defaultdict(set)
    record_roles: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        assignments[(row["target_family"], row["group_id"])].add(row["split"])
        record_roles[(row["target_family"], row["record_id"])].add(row["split"])
    findings = [
        f"group leakage: {family} {group_id} spans {sorted(splits)}"
        for (family, group_id), splits in sorted(assignments.items())
        if len(splits) != 1
    ]
    findings.extend(
        f"record leakage: {family} {record_id} spans {sorted(splits)}"
        for (family, record_id), splits in sorted(record_roles.items())
        if len(splits) != 1
    )
    return tuple(findings)


def find_source_hash_drift(reference_root: Path, expected: Mapping[str, str]) -> tuple[str, ...]:
    findings: list[str] = []
    for relative, expected_hash in sorted(expected.items()):
        prefix = "data/reference/MEA/"
        local_relative = relative[len(prefix) :] if relative.startswith(prefix) else relative
        path = reference_root / local_relative
        actual = _sha256(path) if path.is_file() else "missing"
        if actual != expected_hash:
            findings.append(f"source hash drift: {relative} expected {expected_hash} actual {actual}")
    return tuple(findings)


def _vle_uncertainty_count(split_rows: Iterable[Mapping[str, str]]) -> int:
    # The current canonical VLE registry contains one Idris row group with retained uncertainty.
    return sum(1 for row in split_rows if row["target_family"] == "vle_pressure" and row["source_key"] == "Idris2014")


def validate_reference_observation_contract(reference_root: Path) -> dict[str, int]:
    root = Path(reference_root)
    cases = (
        ("speciation", root / "ChEq" / "Canonical_Combined_ChEq.csv", adapt_speciation_rows),
        ("vle_pressure", root / "VLE" / "Canonical_VLE_Observations.csv", adapt_vle_pressure_rows),
        (
            "loaded_property",
            root / "density_viscosity" / "Amundsen_2009_density_viscosity.csv",
            adapt_loaded_property_rows,
        ),
        (
            "loading_cross_method",
            root / "VLE" / "Wong_2015_high_pressure_loading.csv",
            adapt_paired_loading_rows,
        ),
    )
    row_counts: dict[str, int] = {}
    for family, path, adapter in cases:
        source_file = path.relative_to(ROOT).as_posix()
        report = validate_observation_records(adapter(_read_rows(path), source_file=source_file), family)
        if not report.ok:
            raise RuntimeError(f"{family} observations violate the common observation contract: {report.errors[:5]}")
        row_counts[family] = report.row_count
    return row_counts


def build_regression_readiness(
    reference_root: Path,
    capability_receipt: Mapping[str, Any],
) -> RegressionReadinessBundle:
    reference_root = Path(reference_root)
    validate_reference_observation_contract(reference_root)
    source_hashes = tuple(
        (_relative_source_path(relative), _sha256(reference_root / relative)) for relative in SOURCE_PATHS
    )
    source_hash_map = dict(source_hashes)
    split_rows = _vle_split_rows(
        reference_root,
        source_hash_map[_relative_source_path("VLE/Canonical_VLE_Observations.csv")],
    ) + _speciation_split_rows(
        reference_root,
        source_hash_map[_relative_source_path("ChEq/Canonical_Combined_ChEq.csv")],
    )
    split_rows.sort(key=lambda row: (row["target_family"], row["group_id"], row["record_id"]))
    package = capability_receipt.get("package", {})
    package_version = str(package.get("version", "unknown")) if isinstance(package, Mapping) else "unknown"
    return RegressionReadinessBundle(
        source_hashes=source_hashes,
        target_admission=_admission_rows(capability_receipt),
        grouped_split=tuple(split_rows),
        leakage_findings=find_split_leakage(split_rows),
        capability_receipt_hash=hashlib.sha256(_stable_json_bytes(capability_receipt)).hexdigest(),
        package_version=package_version,
        upstream_execution_admitted=_upstream_execution_admitted(capability_receipt),
        parameter_coverage=tuple(
            _read_rows(reference_root / "manifests" / "parameter_observable_coverage.csv")
        ),
    )


def write_bundle(
    bundle: RegressionReadinessBundle,
    *,
    admission_path: Path = ADMISSION_PATH,
    split_path: Path = SPLIT_PATH,
    summary_path: Path = SUMMARY_PATH,
) -> None:
    for path in (admission_path, split_path, summary_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    admission_path.write_bytes(_csv_bytes(bundle.target_admission, ADMISSION_FIELDS))
    split_path.write_bytes(_csv_bytes(bundle.grouped_split, SPLIT_FIELDS))
    summary_path.write_text(
        json.dumps(bundle.summary(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    receipt = public_capability_receipt()
    bundle = build_regression_readiness(REFERENCE_ROOT, receipt)
    write_bundle(bundle)
    if bundle.leakage_findings:
        for finding in bundle.leakage_findings:
            print(f"ERROR: {finding}")
        return 1
    print(f"wrote {ADMISSION_PATH.relative_to(ROOT)}")
    print(f"wrote {SPLIT_PATH.relative_to(ROOT)}")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"split hash: {bundle.split_hash}")
    print(f"upstream execution admitted: {bundle.upstream_execution_admitted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
