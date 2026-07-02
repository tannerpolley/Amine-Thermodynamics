from __future__ import annotations

from pathlib import Path

import pandas as pd


ANALYSIS_DIR = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_DIR.parents[2]
OUTPUT_DIR = ANALYSIS_DIR / "figures" / "speciation" / "output"
CANONICAL_DATA = REPO_ROOT / "data" / "reference" / "MEA" / "ChEq" / "Canonical_Combined_ChEq.csv"

MOLE_FRACTION_PLOT_DATA = OUTPUT_DIR / "canonical_speciation_mole_fraction_grid_plot_data.csv"
LOADED_MOLKG_PLOT_DATA = OUTPUT_DIR / "canonical_speciation_loaded_molkg_grid_plot_data.csv"
WONG_MOLKG_PLOT_DATA = OUTPUT_DIR / "canonical_speciation_wong_source_molkg_plot_data.csv"
SOURCE_SUMMARY = OUTPUT_DIR / "canonical_speciation_source_summary.csv"

SOURCE_ORDER = ["Bottinger2008", "Jakobsen2005", "Matin2012", "Wong2015"]
SPECIES_ORDER = ["CO2", "MEA", "MEAH+", "MEA + MEAH+", "MEACOO-", "HCO3-", "CO3^2-"]


def _ordered_category(series: pd.Series, order: list[str]) -> pd.Categorical:
    return pd.Categorical(series.astype(str), categories=order, ordered=True)


def _canonical_frame() -> pd.DataFrame:
    if not CANONICAL_DATA.exists():
        raise FileNotFoundError(f"Missing canonical speciation dataset: {CANONICAL_DATA}")
    frame = pd.read_csv(CANONICAL_DATA)
    required = {
        "source_key",
        "source",
        "row_status",
        "temperature_C",
        "mea_mass_fraction",
        "co2_loading_mol_per_mol_mea",
        "species",
        "measurement_role",
        "value_mole_fraction",
        "value_mol_per_kg_loaded_solution",
        "value_mol_per_kg_source_basis",
        "reported_basis",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise RuntimeError(f"Canonical speciation dataset is missing required columns: {missing}")
    return frame


def _positive_rows(frame: pd.DataFrame, value_column: str) -> pd.DataFrame:
    rows = frame.copy()
    rows[value_column] = pd.to_numeric(rows[value_column], errors="coerce")
    rows = rows[rows[value_column].notna() & (rows[value_column] > 0.0)].copy()
    rows = rows[rows["measurement_role"].isin({"direct_positive", "aggregate_direct_positive", "ambiguous_positive"})]
    rows["plot_value"] = rows[value_column].astype(float)
    rows["mea_mass_percent"] = (rows["mea_mass_fraction"].astype(float) * 100.0).round(6)
    rows["source_key"] = _ordered_category(rows["source_key"], SOURCE_ORDER)
    rows["species"] = _ordered_category(rows["species"], SPECIES_ORDER)
    return rows.sort_values(
        ["mea_mass_percent", "temperature_C", "source_key", "species", "co2_loading_mol_per_mol_mea"],
        kind="stable",
    )


def write_plot_data() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    canonical = _canonical_frame()

    mole_fraction = _positive_rows(
        canonical[canonical["reported_basis"] == "mole_fraction"],
        "value_mole_fraction",
    )
    mole_fraction["plot_basis"] = "liquid_mole_fraction"
    mole_fraction.to_csv(MOLE_FRACTION_PLOT_DATA, index=False)

    loaded_molkg = _positive_rows(
        canonical[canonical["reported_basis"] == "mole_fraction"],
        "value_mol_per_kg_loaded_solution",
    )
    loaded_molkg["plot_basis"] = "mol_per_kg_loaded_solution_from_mole_fraction"
    loaded_molkg.to_csv(LOADED_MOLKG_PLOT_DATA, index=False)

    wong = _positive_rows(
        canonical[canonical["source_key"] == "Wong2015"],
        "value_mol_per_kg_source_basis",
    )
    wong["plot_basis"] = "source_reported_mol_per_kg"
    wong.to_csv(WONG_MOLKG_PLOT_DATA, index=False)

    summary = (
        canonical.groupby(["source_key", "reported_basis", "mea_mass_fraction", "temperature_C"], dropna=False)
        .agg(
            row_count=("record_id", "count"),
            positive_plot_rows=("reported_value", lambda values: int((pd.to_numeric(values, errors="coerce") > 0.0).sum())),
            species_count=("species", "nunique"),
        )
        .reset_index()
        .sort_values(["source_key", "mea_mass_fraction", "temperature_C"], kind="stable")
    )
    summary.to_csv(SOURCE_SUMMARY, index=False)


def main() -> int:
    write_plot_data()
    print(f"Wrote {MOLE_FRACTION_PLOT_DATA}")
    print(f"Wrote {LOADED_MOLKG_PLOT_DATA}")
    print(f"Wrote {WONG_MOLKG_PLOT_DATA}")
    print(f"Wrote {SOURCE_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
