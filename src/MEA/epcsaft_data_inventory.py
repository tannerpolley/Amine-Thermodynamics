from __future__ import annotations

import csv
from pathlib import Path

from MEA.epcsaft_runtime import REPO_ROOT, output_dir


DATA_ROOT = REPO_ROOT / "data" / "reference" / "MEA"


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_inventory() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    families = {
        "VLE": {
            "units": "temperature=degC; CO2_loading=mol_CO2/mol_MEA; CO2_pressure=kPa",
            "observable_family": "co2_partial_pressure",
        },
        "ChEq": {
            "units": "temperature=degC; CO2_loading=mol_CO2/mol_MEA; species columns=mole fraction",
            "observable_family": "nmr_speciation",
        },
    }

    for family, meta in families.items():
        folder = DATA_ROOT / family
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.csv")):
            if path.name.endswith(".csv~"):
                continue
            for row in _read_rows(path):
                record = {
                    "source_file": str(path.relative_to(REPO_ROOT)),
                    "fit_role": "candidate",
                    **meta,
                    **{key: value for key, value in row.items() if key is not None},
                }
                records.append(record)
    return records


def write_inventory(records: list[dict[str, str]] | None = None) -> Path:
    records = records if records is not None else load_inventory()
    out_path = output_dir("diagnostics") / "data_inventory.csv"
    keys: list[str] = []
    seen: set[str] = set()
    for row in records:
        for key in row:
            if key not in seen:
                keys.append(key)
                seen.add(key)

    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    return out_path


def main() -> int:
    records = load_inventory()
    out_path = write_inventory(records)
    print(f"Inventory records: {len(records)}")
    print(f"Wrote inventory: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
