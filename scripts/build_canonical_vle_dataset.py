from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from MEA.common.analysis_io import write_csv_rows


REPO_ROOT = Path(__file__).resolve().parents[1]
VLE_DIR = REPO_ROOT / "data" / "reference" / "MEA" / "VLE"
INCLUSION_PATH = VLE_DIR / "Combined_VLE_inclusion.csv"
OUTPUT_PATH = VLE_DIR / "Combined_VLE.csv"

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
    return generated


if __name__ == "__main__":
    rows = build_dataset()
    print(f"Wrote {len(rows)} canonical VLE rows to {OUTPUT_PATH}")
