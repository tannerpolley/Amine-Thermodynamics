from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path
import re

from MEA.common.analysis_io import write_csv_rows


REPO_ROOT = Path(__file__).resolve().parents[1]
AMUNDSEN_SOURCE = (
    REPO_ROOT
    / "docs"
    / "papers"
    / "md"
    / "Amundsen et al. - 2009 - Density and viscosity of monoethanolamine + water + carbon dioxide from (25 to 80) °C.md"
)
WONG_SOURCE = (
    REPO_ROOT
    / "docs"
    / "papers"
    / "md"
    / "Wong et al. - 2015 - Chemical speciation of CO2 absorption in aqueous monoethanolamine investigated by in situ Raman spec.md"
)
AMUNDSEN_OUTPUT = (
    REPO_ROOT
    / "data"
    / "reference"
    / "MEA"
    / "observations"
    / "density_viscosity"
    / "Amundsen_2009_density_viscosity.csv"
)
WONG_OUTPUT = (
    REPO_ROOT / "data" / "reference" / "MEA" / "VLE" / "Wong_2015_high_pressure_loading.csv"
)

AMUNDSEN_FIELDS = (
    "source_key",
    "row_status",
    "property",
    "temperature_C",
    "mea_mass_fraction",
    "co2_loading_mol_per_mol_mea",
    "pressure_kPa",
    "value",
    "value_unit",
    "uncertainty_value",
    "uncertainty_unit",
    "uncertainty_type",
    "temperature_uncertainty_K",
    "mea_mass_fraction_relative_uncertainty_percent",
    "co2_loading_relative_uncertainty_percent",
    "measurement_role",
    "lifecycle_status",
    "source_table_or_figure",
    "source_line_start",
    "source_line_end",
    "notes",
)
AMUNDSEN_FIELDS += (
    "system", "uncertainty_status", "uncertainty_scope",
    "source_general_uncertainty_value", "source_general_uncertainty_unit", "source_locator",
)
WONG_FIELDS = (
    "record_id",
    "source_key",
    "row_status",
    "temperature_K",
    "pressure_bar",
    "mea_mass_fraction",
    "calculated_loading",
    "predicted_loading",
    "loading_unit",
    "mse_x_1e3",
    "mse",
    "calculated_method",
    "predicted_method",
    "measurement_role",
    "lifecycle_status",
    "source_table_or_figure",
    "source_line_start",
    "source_line_end",
    "caveat",
    "notes",
)


def _source_lines(path: Path) -> list[str]:
    if not path.is_file():
        raise RuntimeError(f"Missing repository source transcription: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def _latex_values(line: str) -> list[str]:
    body = line.replace("\\hline", "", 1).split("\\\\", 1)[0]
    return [value.strip() for value in body.split("&")]


def _amundsen_rows(source_file: Path) -> list[dict[str, str | int]]:
    lines = _source_lines(source_file)
    tables = (
        ("Table 1", "density", None, (0.20, 0.30, 0.40, 0.50, 0.70, 0.90, 1.00), (), 43, 47, 38, 49),
        ("Table 2", "density", 0.20, (), (0.1, 0.2, 0.3, 0.4, 0.5), 59, 63, 54, 65),
        ("Table 3", "density", 0.30, (), (0.1, 0.2, 0.3, 0.4, 0.5), 75, 79, 70, 81),
        ("Table 4", "density", 0.40, (), (0.1, 0.2, 0.3, 0.4, 0.5), 106, 110, 101, 112),
        ("Table 5", "dynamic_viscosity", None, (0.20, 0.30, 0.40, 0.50, 0.70, 0.90, 1.00), (), 122, 126, 117, 128),
        ("Table 6", "dynamic_viscosity", 0.20, (), (0.1, 0.2, 0.3, 0.4, 0.5), 138, 142, 133, 144),
        ("Table 7", "dynamic_viscosity", 0.30, (), (0.1, 0.2, 0.3, 0.4, 0.5), 154, 158, 149, 160),
        ("Table 8", "dynamic_viscosity", 0.40, (), (0.1, 0.2, 0.3, 0.4, 0.5), 170, 174, 165, 176),
    )
    rows: list[dict[str, str | int]] = []
    for (
        table,
        property_name,
        loaded_mea_fraction,
        unloaded_fractions,
        loadings,
        first_line,
        last_line,
        locator_start,
        locator_end,
    ) in tables:
        for line_number in range(first_line, last_line + 1):
            values = _latex_values(lines[line_number - 1])
            temperature = values[0]
            observations = values[1:]
            axes = unloaded_fractions if loaded_mea_fraction is None else loadings
            if len(observations) != len(axes):
                raise RuntimeError(f"Unexpected {table} shape at source line {line_number}")
            for axis, value in zip(axes, observations, strict=True):
                if not value:
                    continue
                loaded = loaded_mea_fraction is not None
                mea_fraction = loaded_mea_fraction if loaded else axis
                loading = axis if loaded else ""
                density = property_name == "density"
                if density:
                    uncertainty_value = "0.002" if loaded else "0.0005"
                    uncertainty_unit = "g/cm^3"
                    value_unit = "g/cm^3"
                else:
                    uncertainty_value = "3" if loaded else "1"
                    uncertainty_unit = "percent"
                    value_unit = "mPa*s"
                rows.append(
                    {
                        "source_key": "Amundsen2009",
                        "row_status": "extracted",
                        "property": property_name,
                        "temperature_C": temperature,
                        "mea_mass_fraction": format(float(mea_fraction), ".2f"),
                        "co2_loading_mol_per_mol_mea": format(float(loading), ".1f") if loaded else "",
                        "pressure_kPa": "",
                        "value": value,
                        "value_unit": value_unit,
                        "uncertainty_value": "" if loaded else uncertainty_value,
                        "uncertainty_unit": uncertainty_unit,
                        "uncertainty_type": "unbound_source_scope" if loaded else "combined_relative" if uncertainty_unit == "percent" else "combined_absolute",
                        "system": "pure_mea" if not loaded and float(mea_fraction) == 1 else "ternary" if loaded else "binary",
                        "uncertainty_status": "loaded_scope_unbound" if loaded else "unloaded_source_estimate",
                        "uncertainty_scope": "Loaded general estimates exclude highest T/loadings; exact per-row boundary unresolved (pp.3099-3100)." if loaded else "Unloaded source estimate; not a loaded-row weight.",
                        "source_general_uncertainty_value": uncertainty_value,
                        "source_general_uncertainty_unit": uncertainty_unit,
                        "source_locator": f"3QJR6RHH/NGQVTDX7 {table}; pressure unreported; uncertainty pp.3099-3100",
                        "temperature_uncertainty_K": "0.03",
                        "mea_mass_fraction_relative_uncertainty_percent": "0.5",
                        "co2_loading_relative_uncertainty_percent": "2" if loaded else "",
                        "measurement_role": "direct_positive",
                        "lifecycle_status": "property_target_candidate" if density else "validation_only",
                        "source_table_or_figure": table,
                        "source_line_start": locator_start,
                        "source_line_end": locator_end,
                        "notes": (
                            "CO2-loaded ternary measurement; MEA mass fraction is on the unloaded-solution basis."
                            if loaded
                            else "Pure MEA endpoint; pressure unreported." if float(mea_fraction) == 1 else "Unloaded binary MEA-water; pressure unreported."
                        ),
                    }
                )
    if len(rows) != 213:
        raise RuntimeError(f"Amundsen extraction must contain 213 observations; found {len(rows)}")
    return rows


def _wong_rows() -> list[dict[str, str | int]]:
    lines = _source_lines(WONG_SOURCE)
    rows: list[dict[str, str | int]] = []
    temperature = ""
    for line_number in range(375, 416):
        values = _latex_values(lines[line_number - 1])
        match = re.search(r"(303\.15|313\.15|323\.15)", values[0])
        if match:
            temperature = match.group(1)
        if not temperature or len(values) != 5:
            raise RuntimeError(f"Unexpected Wong Table 5 shape at source line {line_number}")
        pressure, calculated, predicted, mse_scaled = values[1:]
        one_bar_batch = Decimal(pressure) == Decimal("1.0")
        caveat = (
            "Repeated 1 bar batch reading had not reached equilibrium maximum and is not maximum absorption capacity."
            if one_bar_batch
            else "Paired pressure-drop and Raman loading observation for validation review."
        )
        rows.append(
            {
                "record_id": f"wong_table5_{len(rows) + 1:03d}",
                "source_key": "Wong2015",
                "row_status": "extracted",
                "temperature_K": temperature,
                "pressure_bar": pressure,
                "mea_mass_fraction": "0.30",
                "calculated_loading": calculated,
                "predicted_loading": predicted,
                "loading_unit": "mol_CO2_per_mol_MEA",
                "mse_x_1e3": mse_scaled,
                "mse": format(Decimal(mse_scaled) * Decimal("0.001"), "f"),
                "calculated_method": "gas_phase_pressure_drop",
                "predicted_method": "raman_carbon_species_sum",
                "measurement_role": "paired_direct_positive",
                "lifecycle_status": (
                    "non_capacity_batch_observation" if one_bar_batch else "validation_candidate"
                ),
                "source_table_or_figure": "Table 5",
                "source_line_start": 370,
                "source_line_end": 420,
                "caveat": caveat,
                "notes": "Calculated and predicted loadings are retained as distinct reported methods; MSE is reported per row.",
            }
        )
    if len(rows) != 41:
        raise RuntimeError(f"Wong Table 5 extraction must contain 41 rows; found {len(rows)}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--amundsen-only", action="store_true", required=True)
    parser.add_argument("--source-file", type=Path, required=True)
    args = parser.parse_args()
    amundsen = _amundsen_rows(args.source_file)
    write_csv_rows(AMUNDSEN_OUTPUT, amundsen, fieldnames=AMUNDSEN_FIELDS)
    schema_path = AMUNDSEN_OUTPUT.with_name("Amundsen_2009_density_viscosity_schema.csv")
    with schema_path.open(newline="", encoding="utf-8") as stream:
        schema = list(csv.DictReader(stream))
    original = [row for row in schema if row["column"] not in AMUNDSEN_FIELDS[21:]]
    for row in original:
        if row["column"] == "uncertainty_value":
            row.update(required="no", description="Row estimate unavailable where loaded scope is unbound; general estimate retained separately.")
        if row["column"] == "uncertainty_type":
            row["unit_or_domain"] = "combined_absolute|combined_relative|unbound_source_scope"
    for field in AMUNDSEN_FIELDS[21:]:
        original.append({
            "column": field, "required": "yes", "unit_or_domain": "property-dependent source unit" if field.endswith("unit") else "text",
            "description": "Source-qualified metadata; loaded row weights unbound; pressure unreported.",
        })
    write_csv_rows(schema_path, original, fieldnames=list(schema[0]))
    print(f"Wrote {len(amundsen)} Amundsen observations to {AMUNDSEN_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
