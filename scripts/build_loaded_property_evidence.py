from __future__ import annotations

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


def _amundsen_rows() -> list[dict[str, str | int]]:
    lines = _source_lines(AMUNDSEN_SOURCE)
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
                        "uncertainty_value": uncertainty_value,
                        "uncertainty_unit": uncertainty_unit,
                        "uncertainty_type": "combined_relative" if uncertainty_unit == "percent" else "combined_absolute",
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
                            else "Unloaded binary MEA-water measurement."
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
    amundsen = _amundsen_rows()
    wong = _wong_rows()
    write_csv_rows(AMUNDSEN_OUTPUT, amundsen, fieldnames=AMUNDSEN_FIELDS)
    write_csv_rows(WONG_OUTPUT, wong, fieldnames=WONG_FIELDS)
    print(f"Wrote {len(amundsen)} Amundsen observations to {AMUNDSEN_OUTPUT}")
    print(f"Wrote {len(wong)} Wong loading rows to {WONG_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
