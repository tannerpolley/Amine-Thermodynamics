from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from MEA.common.analysis_io import write_csv_rows


REPO_ROOT = Path(__file__).resolve().parents[1]
VLE_DIR = REPO_ROOT / "data" / "reference" / "MEA" / "observations" / "vapor_liquid_equilibrium"
INCLUSION_PATH = VLE_DIR / "Combined_VLE_inclusion.csv"
OUTPUT_PATH = VLE_DIR / "Combined_VLE.csv"
OBSERVATION_PATH = VLE_DIR / "Canonical_VLE_Observations.csv"
DISPOSITION_PATH = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "vle_row_disposition.csv"

SOURCE_FILES = {
    "Aronu2011": "Aronu_2011_VLE.csv",
    "Hilliard2008": "Hilliard_2008_VLE.csv",
    "Idris2014": "Idris_2014_VLE.csv",
    "Jou1995": "Jou_1995_VLE.csv",
    "Mamun2005": "Mamun_2005_VLE.csv",
    "Xu2011": "Xu_2011_VLE.csv",
}
SOURCE_LABELS = {
    "Aronu2011": "Aronu",
    "Hilliard2008": "Hilliard",
    "Idris2014": "Idris",
    "Jou1995": "Jou",
    "Mamun2005": "Mamun",
    "Xu2011": "Xu",
}
MEASUREMENT_FIELDS = (
    "MEA_weight_fraction",
    "temperature",
    "CO2_loading",
    "CO2_pressure",
)
OUTPUT_FIELDS = (
    "row_id",
    "source_key",
    "source_file",
    "source_row",
    "MEA_weight_fraction",
    "temperature",
    "CO2_loading",
    "CO2_pressure",
    "paper",
)
EXPECTED_ROW_COUNT = 161
EXPECTED_OBSERVATION_COUNT = 327
OBSERVATION_FIELDS = (
    "observation_id",
    "source_key",
    "source_file",
    "source_row",
    "source_table_or_figure",
    "doi",
    "MEA_weight_fraction",
    "temperature_reported_C",
    "temperature_canonical_C",
    "temperature_normalized",
    "CO2_loading",
    "CO2_pressure",
    "MEA_pressure",
    "H2O_pressure",
    "pressure_MEA_raoult",
    "total_pressure",
    "CO2_loading_uncertainty",
    "CO2_pressure_uncertainty",
    "replicate_group",
    "normalization_group",
    "active_view_member",
    "active_row_id",
    "lifecycle_status",
    "disposition_reason",
    "notes",
)
DISPOSITION_FIELDS = (
    "source_key",
    "source_file",
    "source_row",
    "active_view_member",
    "active_row_id",
    "lifecycle_status",
    "disposition_reason",
)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise RuntimeError(f"Missing required VLE provenance input: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"Required VLE provenance input has no rows: {path}")
    return rows


def _decimal(value: str, *, field: str, context: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise RuntimeError(f"Invalid {field} value {value!r} in {context}") from exc
    if not result.is_finite():
        raise RuntimeError(f"Non-finite {field} value {value!r} in {context}")
    return result


def _validate_measurement(row: dict[str, str], *, context: str) -> None:
    values = {
        field: _decimal(row.get(field, ""), field=field, context=context)
        for field in MEASUREMENT_FIELDS
    }
    if not Decimal("0") < values["MEA_weight_fraction"] < Decimal("1"):
        raise RuntimeError(f"MEA_weight_fraction must be between zero and one in {context}")
    if values["CO2_loading"] < 0:
        raise RuntimeError(f"CO2_loading must be nonnegative in {context}")
    if values["CO2_pressure"] <= 0:
        raise RuntimeError(f"CO2_pressure must be positive in {context}")


def _load_sources() -> dict[str, list[dict[str, str]]]:
    return {
        source_key: _read_rows(VLE_DIR / source_file)
        for source_key, source_file in SOURCE_FILES.items()
    }


def build_dataset(
    *,
    inclusion_path: Path = INCLUSION_PATH,
    output_path: Path = OUTPUT_PATH,
    observation_path: Path = OBSERVATION_PATH,
    disposition_path: Path = DISPOSITION_PATH,
) -> list[dict[str, str | int]]:
    inclusion_rows = _read_rows(inclusion_path)
    if len(inclusion_rows) != EXPECTED_ROW_COUNT:
        raise RuntimeError(
            f"Canonical VLE inclusion manifest must contain {EXPECTED_ROW_COUNT} rows; "
            f"found {len(inclusion_rows)}"
        )

    sources = _load_sources()
    generated: list[dict[str, str | int]] = []
    included_source_rows: set[tuple[str, int]] = set()

    for expected_sequence, inclusion in enumerate(inclusion_rows, start=1):
        context = f"inclusion row {expected_sequence}"
        try:
            sequence = int(inclusion.get("sequence", ""))
            source_row = int(inclusion.get("source_row", ""))
        except ValueError as exc:
            raise RuntimeError(f"Invalid integer identity in {context}") from exc
        if sequence != expected_sequence:
            raise RuntimeError(
                f"Non-contiguous inclusion sequence in {context}: expected "
                f"{expected_sequence}, found {sequence}"
            )

        source_key = inclusion.get("source_key", "")
        if source_key not in SOURCE_FILES:
            raise RuntimeError(f"Unknown source_key {source_key!r} in {context}")
        source_file = inclusion.get("source_file", "")
        if source_file != SOURCE_FILES[source_key]:
            raise RuntimeError(
                f"Source file mismatch for {source_key} in {context}: "
                f"expected {SOURCE_FILES[source_key]!r}, found {source_file!r}"
            )

        source_identity = (source_key, source_row)
        if source_identity in included_source_rows:
            raise RuntimeError(f"Duplicate source-row identity {source_identity!r}")
        included_source_rows.add(source_identity)

        source_rows = sources[source_key]
        if source_row < 1 or source_row > len(source_rows):
            raise RuntimeError(
                f"Unmatched source row {source_row} for {source_key}; "
                f"source contains {len(source_rows)} rows"
            )
        source = source_rows[source_row - 1]
        if "source_row" in source and int(source["source_row"]) != source_row:
            raise RuntimeError(
                f"Embedded source_row does not match physical row for {source_key} row {source_row}"
            )
        _validate_measurement(source, context=f"{source_key} source row {source_row}")

        for field in MEASUREMENT_FIELDS:
            expected_field = f"expected_{field}"
            expected_value = _decimal(
                inclusion.get(expected_field, ""),
                field=expected_field,
                context=context,
            )
            source_value = _decimal(source[field], field=field, context=context)
            if source_value != expected_value:
                raise RuntimeError(
                    f"Source drift for {source_key} row {source_row}, field {field}: "
                    f"expected {expected_value}, found {source_value}"
                )

        canonical_temperature = inclusion.get("canonical_temperature", "").strip()
        temperature = source["temperature"]
        if canonical_temperature:
            _decimal(
                canonical_temperature,
                field="canonical_temperature",
                context=context,
            )
            temperature = canonical_temperature

        generated.append(
            {
                "row_id": f"vle_{sequence:04d}",
                "source_key": source_key,
                "source_file": source_file,
                "source_row": source_row,
                "MEA_weight_fraction": source["MEA_weight_fraction"],
                "temperature": temperature,
                "CO2_loading": source["CO2_loading"],
                "CO2_pressure": source["CO2_pressure"],
                "paper": SOURCE_LABELS[source_key],
            }
        )

    if set(SOURCE_FILES) != {row["source_key"] for row in generated}:
        raise RuntimeError("Canonical VLE data set does not include every declared source")

    write_csv_rows(output_path, generated, fieldnames=OUTPUT_FIELDS)
    _write_full_registry(
        sources,
        generated,
        observation_path=observation_path,
        disposition_path=disposition_path,
    )
    return generated


def _write_full_registry(
    sources: dict[str, list[dict[str, str]]],
    active_rows: list[dict[str, str | int]],
    *,
    observation_path: Path,
    disposition_path: Path,
) -> None:
    active_lookup = {
        (str(row["source_key"]), int(row["source_row"])): row
        for row in active_rows
    }
    observations: list[dict[str, str | int]] = []
    dispositions: list[dict[str, str | int]] = []
    sequence = 0
    for source_key, source_file in SOURCE_FILES.items():
        for source_row, source in enumerate(sources[source_key], start=1):
            sequence += 1
            context = f"{source_key} source row {source_row}"
            if "source_row" in source and int(source["source_row"]) != source_row:
                raise RuntimeError(f"Embedded source_row does not match physical row for {context}")
            _validate_measurement(source, context=context)

            active = active_lookup.get((source_key, source_row))
            active_member = "yes" if active is not None else "no"
            active_row_id = str(active["row_id"]) if active is not None else ""
            canonical_temperature = str(active["temperature"]) if active is not None else ""
            temperature_normalized = (
                "yes"
                if active is not None and canonical_temperature != source["temperature"]
                else "no"
            )
            if active is not None:
                lifecycle_status = "active_v1"
                disposition_reason = "Retained in the byte-stable Combined_VLE.csv active-v1 view."
            elif source_key in {"Aronu2011", "Hilliard2008"}:
                lifecycle_status = "validation_reserved_candidate"
                disposition_reason = (
                    "Non-30-wt% composition-transfer evidence reserved for grouped validation review."
                )
            elif source_key in {"Jou1995", "Xu2011"}:
                lifecycle_status = "qa_pending_domain_review"
                disposition_reason = (
                    "Temperature, phase, apparatus, and current model-domain eligibility require review."
                )
            else:
                raise RuntimeError(f"Unaccounted non-active VLE row: {context}")

            replicate_group = (
                f"{source_key}|w={source['MEA_weight_fraction']}|T={source['temperature']}"
            )
            normalization_group = (
                f"{source_key}|nominal_T={canonical_temperature}"
                if temperature_normalized == "yes"
                else ""
            )
            observations.append(
                {
                    "observation_id": f"vle_obs_{sequence:04d}",
                    "source_key": source_key,
                    "source_file": source_file,
                    "source_row": source_row,
                    "source_table_or_figure": source.get("source_table_or_figure", ""),
                    "doi": source.get("doi", ""),
                    "MEA_weight_fraction": source["MEA_weight_fraction"],
                    "temperature_reported_C": source["temperature"],
                    "temperature_canonical_C": canonical_temperature,
                    "temperature_normalized": temperature_normalized,
                    "CO2_loading": source["CO2_loading"],
                    "CO2_pressure": source["CO2_pressure"],
                    "MEA_pressure": source.get("MEA_pressure", ""),
                    "H2O_pressure": source.get("H2O_pressure", ""),
                    "pressure_MEA_raoult": source.get("pressure_MEA_raoult", ""),
                    "total_pressure": source.get("total_pressure", ""),
                    "CO2_loading_uncertainty": source.get("CO2_loading_uncertainty", ""),
                    "CO2_pressure_uncertainty": source.get("CO2_pressure_uncertainty", ""),
                    "replicate_group": replicate_group,
                    "normalization_group": normalization_group,
                    "active_view_member": active_member,
                    "active_row_id": active_row_id,
                    "lifecycle_status": lifecycle_status,
                    "disposition_reason": disposition_reason,
                    "notes": source.get("notes", ""),
                }
            )
            dispositions.append(
                {
                    "source_key": source_key,
                    "source_file": source_file,
                    "source_row": source_row,
                    "active_view_member": active_member,
                    "active_row_id": active_row_id,
                    "lifecycle_status": lifecycle_status,
                    "disposition_reason": disposition_reason,
                }
            )

    if len(observations) != EXPECTED_OBSERVATION_COUNT:
        raise RuntimeError(
            f"Full VLE registry must contain {EXPECTED_OBSERVATION_COUNT} rows; "
            f"found {len(observations)}"
        )
    write_csv_rows(observation_path, observations, fieldnames=OBSERVATION_FIELDS)
    write_csv_rows(disposition_path, dispositions, fieldnames=DISPOSITION_FIELDS)


if __name__ == "__main__":
    rows = build_dataset()
    print(f"Wrote {len(rows)} canonical VLE rows to {OUTPUT_PATH}")
