from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results" / "ion_specific_permittivity"
FIGURES = ANALYSIS / "figures"
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7")
MARKERS = ("o", "s", "^", "D")


def _read(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    states = _read("state_results.csv")
    species_rows = _read("speciation_comparison.csv")
    parameters = _read("parameter_table.csv")
    names = {row["configuration_id"]: row["configuration_name"] for row in parameters}
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.5), constrained_layout=True)
    plotted: list[dict[str, object]] = []
    for (configuration_id, name), color, marker in zip(
        names.items(), COLORS, MARKERS, strict=True
    ):
        selected = sorted(
            (
                row
                for row in states
                if row["configuration_id"] == configuration_id
            ),
            key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
        )
        loading = [float(row["loading_mol_co2_per_mol_mea"]) for row in selected]
        for axis, field, panel in (
            (axes[0, 0], "bulk_relative_permittivity", "relative_permittivity"),
            (axes[0, 1], "mass_density_kg_m3", "mass_density"),
        ):
            values = [float(row[field]) if row[field] else math.nan for row in selected]
            axis.plot(loading, values, color=color, marker=marker, label=name)
            plotted.extend(
                {
                    "panel": panel,
                    "configuration_id": configuration_id,
                    "series": name,
                    "loading": x,
                    "value": y,
                }
                for x, y in zip(loading, values, strict=True)
            )
        for axis, species in ((axes[1, 0], "MEACOO-"), (axes[1, 1], "HCO3-")):
            rows = sorted(
                (
                    row
                    for row in species_rows
                    if row["configuration_id"] == configuration_id
                    and row["species"] == species
                ),
                key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
            )
            x = [float(row["loading_mol_co2_per_mol_mea"]) for row in rows]
            y = [
                float(row["predicted_mole_fraction"])
                if row["predicted_mole_fraction"]
                else math.nan
                for row in rows
            ]
            axis.plot(x, y, color=color, marker=marker, label=name)
            plotted.extend(
                {
                    "panel": species,
                    "configuration_id": configuration_id,
                    "series": name,
                    "loading": x_value,
                    "value": y_value,
                }
                for x_value, y_value in zip(x, y, strict=True)
            )
    for axis, species in ((axes[1, 0], "MEACOO-"), (axes[1, 1], "HCO3-")):
        observed = {
            float(row["loading_mol_co2_per_mol_mea"]): float(row["observed_mole_fraction"])
            for row in species_rows
            if row["species"] == species
        }
        x = sorted(observed)
        axes_value = [observed[value] for value in x]
        axis.scatter(x, axes_value, color="black", marker="x", s=55, label="Jakobsen data")
        plotted.extend(
            {
                "panel": species,
                "configuration_id": "",
                "series": "Jakobsen data",
                "loading": x_value,
                "value": observed[x_value],
            }
            for x_value in x
        )
    axes[0, 0].set_title("Bulk relative permittivity")
    axes[0, 0].set_ylabel("Relative permittivity (-)")
    axes[0, 1].set_title("Resolved liquid density")
    axes[0, 1].set_ylabel("Mass density (kg m$^{-3}$)")
    axes[1, 0].set_title("Carbamate speciation")
    axes[1, 0].set_ylabel("MEACOO$^-$ mole fraction")
    axes[1, 1].set_title("Bicarbonate speciation")
    axes[1, 1].set_ylabel("HCO$_3^-$ mole fraction")
    for axis in axes.flat:
        axis.set_xlabel("CO$_2$ loading (mol CO$_2$ mol$^{-1}$ MEA)")
        axis.grid(alpha=0.25)
        axis.legend(frameon=False, fontsize=7)
    fig.suptitle("Ion-specific permittivity sensitivity at 313.15 K, 30 wt% MEA")
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"ion_specific_permittivity.{suffix}", dpi=220)
    plt.close(fig)
    fields = tuple(dict.fromkeys(key for row in plotted for key in row))
    with (RESULTS / "plotted_values.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(plotted)


if __name__ == "__main__":
    main()
