"""Materialize the retained calorimetry rows and paired-state assignments."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1]
REPO = ANALYSIS.parents[1]
SOURCE = (
    REPO
    / "data/reference/MEA/observations/calorimetry/MEA_heat_of_absorption_observations.csv"
)
OUTPUT = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
RECEIPT = (
    ANALYSIS
    / "results/calorimetry/calorimetry-observation-partition-receipt.json"
)
ASSUMED_START_LOADING = 0.003


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def partition(row: dict[str, str]) -> str | None:
    if row["source"] == "Kim and Svendsen 2007":
        return "temperature_holdout" if row["temperature_K"] == "393.15" else "calibration"
    if row["source"] == "Kim et al. 2014" and row["source_table"] == "Table A1-1":
        return "model_selection_comparison"
    return None


def group_key(row: dict[str, str]) -> tuple[str, ...]:
    return (
        row["source"],
        row["source_table"],
        row["temperature_K"],
        row["mea_mass_fraction"],
        row["run"] or "reported_series",
    )


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        source_fields = tuple(reader.fieldnames or ())
        rows = [row for row in reader if partition(row) is not None]

    record_ids = [row["record_id"] for row in rows]
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("selected calorimetry record_id values are not unique")

    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[group_key(row)].append(row)

    enriched: list[dict[str, str]] = []
    for key in sorted(groups):
        ordered = sorted(groups[key], key=lambda row: float(row["co2_loading_mol_per_mol_mea"]))
        previous_loading = ASSUMED_START_LOADING
        previous_id = "assumed_start_loading_0.003"
        for index, row in enumerate(ordered):
            loading = float(row["co2_loading_mol_per_mol_mea"])
            if loading <= previous_loading:
                raise ValueError(f"non-positive loading increment in {key}: {previous_loading} -> {loading}")
            enriched.append(
                {
                    **row,
                    "campaign_partition": partition(row) or "",
                    "pair_group": " | ".join(key),
                    "previous_record_id": previous_id,
                    "previous_loading_mol_per_mol_mea": f"{previous_loading:.6g}",
                    "previous_endpoint_basis": (
                        "assumed_start_loading" if index == 0 else "preceding_observation_endpoint"
                    ),
                    "first_row_source_typo_sensitivity": (
                        "exclude_and_replay" if row["record_id"] == "kim2007_t40_r1_0.041" else ""
                    ),
                }
            )
            previous_loading = loading
            previous_id = row["record_id"]

    expected = Counter(
        calibration=66,
        temperature_holdout=20,
        model_selection_comparison=27,
    )
    counts = Counter(row["campaign_partition"] for row in enriched)
    if counts != expected:
        raise ValueError(f"unexpected partition counts: {dict(counts)}")

    output_fields = source_fields + (
        "campaign_partition",
        "pair_group",
        "previous_record_id",
        "previous_loading_mol_per_mol_mea",
        "first_row_source_typo_sensitivity",
        "previous_endpoint_basis",
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(enriched)

    receipt = {
        "schema_version": 1,
        "canonical_source": str(SOURCE.relative_to(REPO)),
        "canonical_source_sha256": sha256(SOURCE),
        "materialized_view": str(OUTPUT.relative_to(REPO)),
        "materialized_view_sha256": sha256(OUTPUT),
        "row_count": len(enriched),
        "partition_counts": dict(sorted(counts.items())),
        "pair_group_count": len(groups),
        "pairing_rule": "adjacent loading endpoints within source, table, temperature, MEA mass fraction, and run",
        "first_endpoint_assumption": {
            "co2_loading_mol_per_mol_mea": ASSUMED_START_LOADING,
            "required_sensitivity": "perturb before parameter adoption",
        },
        "source_typo_sensitivity_record_id": "kim2007_t40_r1_0.041",
        "heat_sign": "reported positive heat-release magnitude",
        "heat_unit": "kJ/mol CO2",
        "engine_requirement": "paired-state total reactive-liquid enthalpy owner with compatible incoming ideal-gas CO2 enthalpy and typed endpoint failures",
        "engine_requirement_state": "not present at inspected ePC-SAFT-project commit 9eccbfd9d4c3cd308a37906a0342908e4efed87e",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
