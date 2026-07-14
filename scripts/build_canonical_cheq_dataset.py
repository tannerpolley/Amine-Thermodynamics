from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
CHEQ_DIR = REPO_ROOT / "data" / "reference" / "MEA" / "ChEq"
OUTPUT_PATH = CHEQ_DIR / "Canonical_Combined_ChEq.csv"
SCHEMA_PATH = CHEQ_DIR / "Canonical_Combined_ChEq_schema.csv"
ACTIVE_VIEW_PATH = CHEQ_DIR / "Combined_ChEq.csv"
MEMBERSHIP_PATH = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "speciation_target_membership.csv"

MW_MEA_G_PER_MOL = 61.084
MW_CO2_G_PER_MOL = 44.01
LEGACY_SPECIES_COLUMNS = {
    "CO2": "CO2",
    "MEA": "MEA",
    "MEAH+": "MEAH^+",
    "MEA + MEAH+": "MEA + MEAH^+",
    "MEACOO-": "MEACOO^-",
    "HCO3-": "HCO3^-",
    "CO3^2-": "CO3^2-",
}

CANONICAL_COLUMNS = [
    "record_id",
    "source_key",
    "source",
    "source_file",
    "source_row_index",
    "row_status",
    "temperature_C",
    "temperature_K",
    "pressure_bar",
    "mea_mass_fraction",
    "co2_loading_mol_per_mol_mea",
    "species",
    "source_species",
    "measurement_role",
    "conversion_eligible",
    "lifecycle_status",
    "target_membership",
    "reported_value",
    "reported_basis",
    "reported_unit",
    "value_mole_fraction",
    "value_mol_per_kg_source_basis",
    "value_mol_per_kg_unloaded_solution",
    "value_mol_per_kg_initial_water",
    "value_mol_per_kg_loaded_solution",
    "feed_mea_mol_per_kg_unloaded_solution",
    "feed_co2_mol_per_kg_unloaded_solution",
    "loaded_solution_mass_kg_per_kg_unloaded_solution",
    "conversion_total_moles_per_kg_unloaded_solution",
    "conversion_basis",
    "source_table_or_figure",
    "source_line_start",
    "source_line_end",
    "notes",
]


@dataclass(frozen=True)
class LegacySource:
    source_key: str
    source: str
    filename: str


LEGACY_SOURCES = (
    LegacySource("Bottinger2008", "Böttinger 2008", "Bottinger_2007_ChEq.csv"),
    LegacySource("Jakobsen2005", "Jakobsen 2005", "Jakobsen_2005_ChEq.csv"),
    LegacySource("Matin2012", "Matin 2012", "Matin_2012_ChEq.csv"),
)


SCHEMA_ROWS = [
    ("record_id", "yes", "stable string", "Canonical row identifier assigned by this generator."),
    ("source_key", "yes", "source id", "Stable literature source key."),
    ("source", "yes", "text", "Human-readable source label."),
    ("source_file", "yes", "relative path", "Machine-readable source file used to build this row."),
    ("source_row_index", "yes", "1-based integer", "Row number within the source CSV, excluding the header."),
    ("row_status", "yes", "reported|extracted|ambiguous|excluded", "Source row status or extraction quality flag."),
    ("temperature_C", "yes", "degC", "Reported liquid temperature."),
    ("temperature_K", "yes", "K", "Reported liquid temperature converted from degC."),
    ("pressure_bar", "no", "bar", "Reported pressure when available."),
    ("mea_mass_fraction", "yes", "mass fraction", "MEA mass fraction for the aqueous MEA feed or solution."),
    ("co2_loading_mol_per_mol_mea", "yes", "mol/mol", "CO2 loading as mol CO2 per mol MEA."),
    ("species", "yes", "species label", "Canonical species label."),
    ("source_species", "yes", "text", "Species label or source column before canonical normalization."),
    ("measurement_role", "yes", "direct_positive|direct_zero|aggregate_direct_positive|aggregate_direct_zero|ambiguous", "How the value should be treated as measured or unresolved evidence."),
    ("conversion_eligible", "yes", "true|false", "Whether the reported basis has enough verified denominator information for normalized conversion."),
    ("lifecycle_status", "yes", "canonical_eligible|validation_reserved|diagnostic_only|qa_pending", "Row-level evidence lifecycle state."),
    ("target_membership", "yes", "active_v1|transferability_candidate|diagnostic_only_basis_unverified", "Current target or holdout membership without implying upstream admission."),
    ("reported_value", "yes", "source basis", "Numeric value exactly on the source-file basis."),
    ("reported_basis", "yes", "mole_fraction|mol_per_kg_source_basis", "Basis of reported_value."),
    ("reported_unit", "yes", "unit text", "Reported unit label."),
    ("value_mole_fraction", "no", "mole fraction", "Reported or directly standardized true-species mole fraction."),
    ("value_mol_per_kg_source_basis", "no", "mol/kg", "Reported mol/kg value when the source reports mol/kg."),
    ("value_mol_per_kg_unloaded_solution", "no", "mol/kg", "Computed mol per kg unloaded MEA-water feed."),
    ("value_mol_per_kg_initial_water", "no", "mol/kg", "Computed mol per kg initial water in the unloaded MEA-water feed."),
    ("value_mol_per_kg_loaded_solution", "no", "mol/kg", "Computed mol per kg loaded liquid, using absorbed CO2 mass from the reported loading."),
    ("feed_mea_mol_per_kg_unloaded_solution", "yes", "mol/kg", "MEA feed moles per kg unloaded MEA-water solution."),
    ("feed_co2_mol_per_kg_unloaded_solution", "yes", "mol/kg", "Absorbed CO2 moles per kg unloaded MEA-water solution from loading."),
    ("loaded_solution_mass_kg_per_kg_unloaded_solution", "yes", "kg/kg", "Loaded liquid mass per kg unloaded MEA-water solution."),
    ("conversion_total_moles_per_kg_unloaded_solution", "no", "mol/kg", "Total true-species moles used to convert reported mole fractions."),
    ("conversion_basis", "yes", "text", "Rule used for unit conversion."),
    ("source_table_or_figure", "no", "text", "Traceability pointer to the source table or figure."),
    ("source_line_start", "no", "line number", "First local Markdown line used for traceability when available."),
    ("source_line_end", "no", "line number", "Last local Markdown line used for traceability when available."),
    ("notes", "no", "text", "Short provenance and conversion notes."),
]


def _blank() -> float:
    return float("nan")


def _finite_or_blank(value: object) -> float:
    if value is None:
        return _blank()
    if isinstance(value, str) and value.strip() == "":
        return _blank()
    result = float(value)
    return result if np.isfinite(result) else _blank()


def _measurement_role(species: str, value: float, row_status: str) -> str:
    if row_status == "ambiguous":
        return "ambiguous"
    prefix = "aggregate_direct" if species == "MEA + MEAH+" else "direct"
    suffix = "positive" if value > 0.0 else "zero"
    return f"{prefix}_{suffix}"


def _feed_context(mea_mass_fraction: float, loading: float) -> dict[str, float]:
    if not 0.0 < mea_mass_fraction < 1.0:
        raise ValueError(f"MEA mass fraction must be between zero and one: {mea_mass_fraction}")
    if loading < 0.0:
        raise ValueError(f"CO2 loading must be nonnegative: {loading}")
    feed_mea = mea_mass_fraction * 1000.0 / MW_MEA_G_PER_MOL
    feed_co2 = loading * feed_mea
    loaded_mass = 1.0 + feed_co2 * MW_CO2_G_PER_MOL / 1000.0
    return {
        "feed_mea_mol_per_kg_unloaded_solution": feed_mea,
        "feed_co2_mol_per_kg_unloaded_solution": feed_co2,
        "loaded_solution_mass_kg_per_kg_unloaded_solution": loaded_mass,
    }


def _legacy_total_moles_per_kg(row: pd.Series) -> float:
    mea_mass_fraction = _finite_or_blank(row["MEA_weight_fraction"])
    feed_mea = _feed_context(mea_mass_fraction, _finite_or_blank(row["CO2_loading"]))[
        "feed_mea_mol_per_kg_unloaded_solution"
    ]
    aggregate = _finite_or_blank(row.get("MEA + MEAH^+", ""))
    meacoo = _finite_or_blank(row.get("MEACOO^-", ""))
    if np.isfinite(aggregate) and np.isfinite(meacoo):
        mea_moiety_fraction = aggregate + meacoo
    else:
        mea_moiety_fraction = sum(
            value
            for value in (
                _finite_or_blank(row.get("MEA", "")),
                _finite_or_blank(row.get("MEAH^+", "")),
                meacoo,
            )
            if np.isfinite(value)
        )
    if not np.isfinite(mea_moiety_fraction) or mea_moiety_fraction <= 0.0:
        raise ValueError(f"Cannot determine MEA-moiety mole-fraction scale for source row {dict(row)}")
    return feed_mea / mea_moiety_fraction


def _legacy_rows(source: LegacySource) -> list[dict[str, object]]:
    source_path = CHEQ_DIR / source.filename
    df = pd.read_csv(source_path)
    rows: list[dict[str, object]] = []
    for row_number, row in enumerate(df.to_dict("records"), start=1):
        series = pd.Series(row)
        mea_mass_fraction = _finite_or_blank(row["MEA_weight_fraction"])
        loading = _finite_or_blank(row["CO2_loading"])
        temperature_C = _finite_or_blank(row["temperature"])
        context = _feed_context(mea_mass_fraction, loading)
        total_moles = _legacy_total_moles_per_kg(series)
        for species, column in LEGACY_SPECIES_COLUMNS.items():
            if column not in row:
                continue
            value = _finite_or_blank(row[column])
            if not np.isfinite(value):
                continue
            amount_per_kg_unloaded = value * total_moles
            rows.append(
                {
                    "record_id": "",
                    "source_key": source.source_key,
                    "source": source.source,
                    "source_file": f"data/reference/MEA/ChEq/{source.filename}",
                    "source_row_index": row_number,
                    "row_status": "reported",
                    "temperature_C": temperature_C,
                    "temperature_K": temperature_C + 273.15,
                    "pressure_bar": _blank(),
                    "mea_mass_fraction": mea_mass_fraction,
                    "co2_loading_mol_per_mol_mea": loading,
                    "species": species,
                    "source_species": column,
                    "measurement_role": _measurement_role(species, value, "reported"),
                    "conversion_eligible": "true",
                    "lifecycle_status": (
                        "canonical_eligible"
                        if abs(mea_mass_fraction - 0.3) < 1.0e-12
                        else "validation_reserved"
                    ),
                    "target_membership": (
                        "active_v1"
                        if abs(mea_mass_fraction - 0.3) < 1.0e-12
                        else "transferability_candidate"
                    ),
                    "reported_value": value,
                    "reported_basis": "mole_fraction",
                    "reported_unit": "mole_fraction",
                    "value_mole_fraction": value,
                    "value_mol_per_kg_source_basis": _blank(),
                    "value_mol_per_kg_unloaded_solution": amount_per_kg_unloaded,
                    "value_mol_per_kg_initial_water": amount_per_kg_unloaded / (1.0 - mea_mass_fraction),
                    "value_mol_per_kg_loaded_solution": amount_per_kg_unloaded
                    / context["loaded_solution_mass_kg_per_kg_unloaded_solution"],
                    **context,
                    "conversion_total_moles_per_kg_unloaded_solution": total_moles,
                    "conversion_basis": "reported_mole_fraction_scaled_by_MEA_moiety_balance_per_kg_unloaded_solution",
                    "source_table_or_figure": "",
                    "source_line_start": "",
                    "source_line_end": "",
                    "notes": "Legacy ChEq value treated as true-species liquid mole fraction; mol/kg columns use a 1 kg unloaded MEA-water feed basis.",
                }
            )
    return rows


def _wong_rows() -> list[dict[str, object]]:
    source_path = CHEQ_DIR / "Wong_2015_Raman_speciation.csv"
    df = pd.read_csv(source_path)
    rows: list[dict[str, object]] = []
    for row_number, row in enumerate(df.to_dict("records"), start=1):
        mea_mass_fraction = _finite_or_blank(row["mea_mass_fraction"])
        loading = _finite_or_blank(row["co2_loading_mol_per_mol_mea"])
        temperature_C = _finite_or_blank(row["temperature_C"])
        value = _finite_or_blank(row["value"])
        context = _feed_context(mea_mass_fraction, loading)
        source_species = str(row["species"])
        species = "CO2" if source_species == "CO2(aq)" else source_species
        row_status = str(row["row_status"])
        notes = str(row.get("notes", "")).strip()
        if notes:
            notes += " "
        notes += "Source mol/kg denominator is not verified; no mole-fraction or alternate mol/kg conversion is eligible. Feed and loading context are retained as diagnostic metadata only."
        rows.append(
            {
                "record_id": "",
                "source_key": "Wong2015",
                "source": "Wong 2015",
                "source_file": "data/reference/MEA/ChEq/Wong_2015_Raman_speciation.csv",
                "source_row_index": row_number,
                "row_status": row_status,
                "temperature_C": temperature_C,
                "temperature_K": temperature_C + 273.15,
                "pressure_bar": _finite_or_blank(row.get("pressure_bar", "")),
                "mea_mass_fraction": mea_mass_fraction,
                "co2_loading_mol_per_mol_mea": loading,
                "species": species,
                "source_species": source_species,
                "measurement_role": _measurement_role(species, value, row_status),
                "conversion_eligible": "false",
                "lifecycle_status": "qa_pending" if row_status == "ambiguous" else "diagnostic_only",
                "target_membership": "diagnostic_only_basis_unverified",
                "reported_value": value,
                "reported_basis": "mol_per_kg_source_basis",
                "reported_unit": "mol/kg",
                "value_mole_fraction": _blank(),
                "value_mol_per_kg_source_basis": value,
                "value_mol_per_kg_unloaded_solution": _blank(),
                "value_mol_per_kg_initial_water": _blank(),
                "value_mol_per_kg_loaded_solution": _blank(),
                **context,
                "conversion_total_moles_per_kg_unloaded_solution": _blank(),
                "conversion_basis": "not_converted_unverified_source_kg_denominator",
                "source_table_or_figure": row.get("source_table_or_figure", ""),
                "source_line_start": row.get("source_line_start", ""),
                "source_line_end": row.get("source_line_end", ""),
                "notes": notes,
            }
        )
    return rows


def build_dataset() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source in LEGACY_SOURCES:
        rows.extend(_legacy_rows(source))
    rows.extend(_wong_rows())
    for index, row in enumerate(rows):
        row["record_id"] = f"cheq_canon_{index:05d}"
    return pd.DataFrame(rows, columns=CANONICAL_COLUMNS)


def build_schema() -> pd.DataFrame:
    return pd.DataFrame(SCHEMA_ROWS, columns=["column", "required", "unit_or_domain", "description"])


TARGET_ROLE_SPECIES = (
    "CO2",
    "MEA",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
    "MEA + MEAH+",
)
ACTIVE_SOURCE_KEYS = {
    "Bottinger": "Bottinger2008",
    "Jakobsen": "Jakobsen2005",
    "Matin": "Matin2012",
}


def _normalized_role(role: str) -> str:
    return {
        "aggregate_positive": "aggregate_direct_positive",
        "aggregate_zero": "aggregate_direct_zero",
        "ambiguous_positive": "ambiguous",
        "ambiguous_zero": "ambiguous",
    }.get(role, role)


def _roles_from_long_group(group: pd.DataFrame) -> dict[str, str]:
    roles = {species: "balance_inferred" for species in TARGET_ROLE_SPECIES}
    for row in group.to_dict("records"):
        roles[str(row["species"])] = _normalized_role(str(row["measurement_role"]))
    return roles


def _roles_from_active_row(row: dict[str, object]) -> dict[str, str]:
    columns = {
        "CO2": "CO2",
        "MEA": "MEA",
        "MEAH+": "MEAH^+",
        "MEACOO-": "MEACOO^-",
        "HCO3-": "HCO3^-",
        "CO3^2-": "CO3^2-",
        "MEA + MEAH+": "MEA + MEAH^+",
    }
    roles = {species: "balance_inferred" for species in TARGET_ROLE_SPECIES}
    for species, column in columns.items():
        value = _finite_or_blank(row.get(column, ""))
        if np.isfinite(value):
            roles[species] = _measurement_role(species, value, "reported")
    return roles


def _active_roles(dataset: pd.DataFrame) -> dict[tuple[str, int], dict[str, str]]:
    active = pd.read_csv(ACTIVE_VIEW_PATH)
    roles: dict[tuple[str, int], dict[str, str]] = {}
    legacy = dataset[dataset["source_key"] != "Wong2015"]
    for row in active.to_dict("records"):
        source_key = ACTIVE_SOURCE_KEYS[str(row["source"])]
        candidates = legacy[
            (legacy["source_key"] == source_key)
            & np.isclose(legacy["mea_mass_fraction"].astype(float), float(row["MEA_weight_fraction"]))
            & np.isclose(legacy["temperature_C"].astype(float), float(row["temperature"]))
            & np.isclose(
                legacy["co2_loading_mol_per_mol_mea"].astype(float),
                float(row["CO2_loading"]),
            )
        ]
        source_rows = candidates["source_row_index"].unique()
        if len(source_rows) != 1:
            raise ValueError(f"Active speciation state does not map uniquely to its source row: {row}")
        roles[(source_key, int(source_rows[0]))] = _roles_from_active_row(row)
    if len(roles) != 74:
        raise ValueError(f"Active-v1 speciation membership must contain 74 states; found {len(roles)}")
    return roles


def build_membership(dataset: pd.DataFrame) -> pd.DataFrame:
    active_roles = _active_roles(dataset)
    rows: list[dict[str, object]] = []
    legacy = dataset[dataset["source_key"] != "Wong2015"]
    for (source_key, source_row), group in legacy.groupby(
        ["source_key", "source_row_index"], sort=False
    ):
        state_key = (str(source_key), int(source_row))
        is_active = state_key in active_roles
        roles = active_roles[state_key] if is_active else _roles_from_long_group(group)
        first = group.iloc[0]
        state_id = f"{source_key}_state_{int(source_row):03d}"
        for species in TARGET_ROLE_SPECIES:
            role = roles[species]
            rows.append(
                {
                    "membership_id": f"{state_id}|{species}",
                    "state_id": state_id,
                    "source_key": source_key,
                    "source_file": first["source_file"],
                    "source_row_index": int(source_row),
                    "row_status": "reported",
                    "temperature_C": first["temperature_C"],
                    "mea_mass_fraction": first["mea_mass_fraction"],
                    "co2_loading_mol_per_mol_mea": first["co2_loading_mol_per_mol_mea"],
                    "species": species,
                    "measurement_role": role,
                    "reported_basis": "mole_fraction" if role != "balance_inferred" else "",
                    "conversion_eligible": "true",
                    "lifecycle_status": "canonical_eligible" if is_active else "validation_reserved",
                    "target_membership": "active_v1" if is_active else "transferability_candidate",
                    "target_eligible": (
                        "yes"
                        if is_active
                        and role
                        in {
                            "direct_positive",
                            "direct_zero",
                            "aggregate_direct_positive",
                            "aggregate_direct_zero",
                        }
                        else "no"
                    ),
                    "eligibility_reason": (
                        "Direct active-v1 source observation."
                        if is_active and role != "balance_inferred"
                        else "Balance-inferred context is not an independent measurement."
                        if role == "balance_inferred"
                        else "Non-30-wt% state is reserved for composition-transfer review."
                    ),
                }
            )

    wong = dataset[dataset["source_key"] == "Wong2015"]
    for row in wong.to_dict("records"):
        state_id = f"Wong2015_point_{int(row['source_row_index']):03d}"
        rows.append(
            {
                "membership_id": f"{state_id}|{row['species']}",
                "state_id": state_id,
                "source_key": "Wong2015",
                "source_file": row["source_file"],
                "source_row_index": int(row["source_row_index"]),
                "row_status": row["row_status"],
                "temperature_C": row["temperature_C"],
                "mea_mass_fraction": row["mea_mass_fraction"],
                "co2_loading_mol_per_mol_mea": row["co2_loading_mol_per_mol_mea"],
                "species": row["species"],
                "measurement_role": row["measurement_role"],
                "reported_basis": row["reported_basis"],
                "conversion_eligible": "false",
                "lifecycle_status": row["lifecycle_status"],
                "target_membership": "diagnostic_only_basis_unverified",
                "target_eligible": "no",
                "eligibility_reason": "Source kg denominator is not verified; normalized target conversion fails closed.",
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    dataset = build_dataset()
    schema = build_schema()
    membership = build_membership(dataset)
    dataset.to_csv(OUTPUT_PATH, index=False, float_format="%.12g")
    schema.to_csv(SCHEMA_PATH, index=False)
    membership.to_csv(MEMBERSHIP_PATH, index=False, float_format="%.12g")
    print(f"Wrote {OUTPUT_PATH} ({len(dataset)} rows)")
    print(f"Wrote {SCHEMA_PATH} ({len(schema)} rows)")
    print(f"Wrote {MEMBERSHIP_PATH} ({len(membership)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
