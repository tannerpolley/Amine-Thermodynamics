from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from MEA.common.config import REPO_ROOT


ACTIVITY_REACTION_MANIFEST = (
    REPO_ROOT
    / "data"
    / "reference"
    / "MEA"
    / "manifests"
    / "phase2_reaction_constant_source_verification.csv"
)
REACTION_NAMES = {
    "R1": "R1_water_autoionization",
    "R2": "R2_CO2_to_HCO3",
    "R3": "R3_HCO3_to_CO3",
    "R4": "R4_MEACOO_hydrolysis",
    "R5": "R5_MEAH_dissociation",
}
EXPECTED_REACTION_IDS = tuple(REACTION_NAMES)


@dataclass(frozen=True)
class ReactionCoefficient:
    reaction_id: str
    name: str
    a: float
    b: float
    c: float
    d: float
    source_key: str
    source_file: str
    source_locator: str

    def coefficients(self) -> tuple[float, float, float, float]:
        return (self.a, self.b, self.c, self.d)

    def source(self) -> str:
        return f"{self.source_key}|{self.source_file}|{self.source_locator}"


def load_activity_reaction_catalog(
    path: Path = ACTIVITY_REACTION_MANIFEST,
) -> tuple[ReactionCoefficient, ...]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))

    reaction_ids = [row.get("reaction_id", "") for row in raw_rows]
    verified = all(
        row.get("source_verified", "").strip().lower() == "yes"
        and row.get("source_status", "").strip() == "source_verified"
        for row in raw_rows
    )
    if tuple(reaction_ids) != EXPECTED_REACTION_IDS or len(set(reaction_ids)) != len(reaction_ids) or not verified:
        raise ValueError(f"Activity reaction catalog must contain verified unique R1-R5 rows: {path}")

    rows: list[ReactionCoefficient] = []
    for row in raw_rows:
        values = tuple(float(row[f"source_value_{key}"]) for key in ("A", "B", "C", "D"))
        if not all(math.isfinite(value) for value in values):
            raise ValueError(f"Activity reaction catalog contains nonfinite coefficients for {row['reaction_id']}: {path}")
        reaction_id = row["reaction_id"]
        rows.append(
            ReactionCoefficient(
                reaction_id=reaction_id,
                name=REACTION_NAMES[reaction_id],
                a=values[0],
                b=values[1],
                c=values[2],
                d=values[3],
                source_key=row["source_key"],
                source_file=row["source_file_repo_relative"],
                source_locator=row["source_table_or_figure"],
            )
        )
    return tuple(rows)


def activity_coefficient_map() -> dict[str, tuple[float, float, float, float]]:
    return {row.name: row.coefficients() for row in load_activity_reaction_catalog()}


def activity_source_map() -> dict[str, str]:
    return {row.name: row.source() for row in load_activity_reaction_catalog()}


def reaction_catalog_sha256() -> str:
    payload = [asdict(row) for row in load_activity_reaction_catalog()]
    normalized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
