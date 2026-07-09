from __future__ import annotations

import csv
import json
import shutil
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import pandas as pd


def read_required_csv(path: Path, *, hint: str | None = None) -> pd.DataFrame:
    if not path.exists():
        message = f"Missing required CSV input: {path}"
        if hint:
            message += f". {hint}"
        raise RuntimeError(message)
    return pd.read_csv(path)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise RuntimeError(f"Missing required CSV input: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: Sequence[str] | None = None) -> None:
    if not rows and fieldnames is None:
        raise RuntimeError(f"No rows available for required artifact: {path}")
    columns = list(fieldnames) if fieldnames is not None else list(rows[0].keys())
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_svg(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def copy_files(paths: Iterable[Path], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for path in paths:
        shutil.copy2(path, destination / path.name)


def copy_file_as(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def remove_matching_files(roots: Iterable[Path], patterns: Iterable[str]) -> None:
    for root in roots:
        root.mkdir(parents=True, exist_ok=True)
        for pattern in patterns:
            for path in root.glob(pattern):
                path.unlink()
