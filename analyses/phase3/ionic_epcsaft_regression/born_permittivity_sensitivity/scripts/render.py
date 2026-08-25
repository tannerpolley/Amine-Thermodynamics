from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results"
FIGURES = ANALYSIS / "figures"
COLORS = {
    "original_born_no_induced": "#CC79A7",
    "original_born_solvent_only": "#E69F00",
    "shell_born_ion_suppressed_no_induced": "#009E73",
    "shell_born_ion_suppressed": "#0072B2",
}
MARKERS = {
    "original_born_no_induced": "D",
    "original_born_solvent_only": "^",
    "shell_born_ion_suppressed_no_induced": "v",
    "shell_born_ion_suppressed": "o",
}
LINESTYLES = {
    "original_born_no_induced": "--",
    "original_born_solvent_only": ":",
    "shell_born_ion_suppressed_no_induced": "--",
    "shell_born_ion_suppressed": "-",
}


def _read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _float(value: str) -> float | None:
    return None if value == "" else float(value)


def main() -> None:
    states = _read_csv("state_results.csv")
    parameters = _read_csv("parameter_table.csv")
    speciation = _read_csv("speciation_comparison.csv")
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    names = {row["configuration_id"]: row["configuration_name"] for row in parameters}
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.5), constrained_layout=True)
    plotted: list[dict[str, object]] = []

    for configuration_id, name in names.items():
        selected = sorted(
            (
                row
                for row in states
                if row["configuration_id"] == configuration_id
                and row["status"] == "evaluated"
            ),
            key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
        )
        if selected:
            x = [float(row["loading_mol_co2_per_mol_mea"]) for row in selected]
            density = [float(row["mass_density_kg_m3"]) for row in selected]
            permittivity = [
                float(row["bulk_relative_permittivity"]) for row in selected
            ]
            axes[0, 0].plot(
                x,
                density,
                color=COLORS[configuration_id],
                marker=MARKERS[configuration_id],
                linestyle=LINESTYLES[configuration_id],
                label=name,
            )
            axes[0, 1].plot(
                x,
                permittivity,
                color=COLORS[configuration_id],
                marker=MARKERS[configuration_id],
                linestyle=LINESTYLES[configuration_id],
                label=name,
            )
            for row, y_density, y_permittivity in zip(
                selected, density, permittivity, strict=True
            ):
                plotted.extend(
                    (
                        {
                            "panel": "mass_density",
                            "series": name,
                            "role": "model",
                            "configuration_id": configuration_id,
                            "loading": row["loading_mol_co2_per_mol_mea"],
                            "x": row["loading_mol_co2_per_mol_mea"],
                            "y": y_density,
                            "unit": "kg/m3",
                        },
                        {
                            "panel": "bulk_relative_permittivity",
                            "series": name,
                            "role": "model",
                            "configuration_id": configuration_id,
                            "loading": row["loading_mol_co2_per_mol_mea"],
                            "x": row["loading_mol_co2_per_mol_mea"],
                            "y": y_permittivity,
                            "unit": "dimensionless",
                        },
                    )
                )

        for axis, species in ((axes[1, 0], "MEACOO-"), (axes[1, 1], "HCO3-")):
            rows = sorted(
                (
                    row
                    for row in speciation
                    if row["configuration_id"] == configuration_id
                    and row["species"] == species
                    and row["predicted_mole_fraction"] != ""
                ),
                key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
            )
            if rows:
                x = [float(row["loading_mol_co2_per_mol_mea"]) for row in rows]
                y = [float(row["predicted_mole_fraction"]) for row in rows]
                axis.plot(
                    x,
                    y,
                    color=COLORS[configuration_id],
                    marker=MARKERS[configuration_id],
                    linestyle=LINESTYLES[configuration_id],
                    label=name,
                )
                plotted.extend(
                    {
                        "panel": species,
                        "series": name,
                        "role": "model",
                        "configuration_id": configuration_id,
                        "loading": row["loading_mol_co2_per_mol_mea"],
                        "x": row["loading_mol_co2_per_mol_mea"],
                        "y": row["predicted_mole_fraction"],
                        "unit": "mole fraction",
                    }
                    for row in rows
                )

    density = float(summary["unloaded_density_reference_kg_m3"])
    density_uncertainty = float(summary["unloaded_density_uncertainty_kg_m3"])
    axes[0, 0].errorbar(
        [0.0],
        [density],
        yerr=[density_uncertainty],
        color="#222222",
        marker="x",
        linestyle="none",
        capsize=3,
        label="Amundsen unloaded reference",
    )
    plotted.append(
        {
            "panel": "mass_density",
            "series": "Amundsen unloaded reference",
            "role": "observation",
            "configuration_id": "",
            "loading": 0.0,
            "x": 0.0,
            "y": density,
            "y_uncertainty": density_uncertainty,
            "unit": "kg/m3",
        }
    )

    for axis, species in ((axes[1, 0], "MEACOO-"), (axes[1, 1], "HCO3-")):
        observed_by_loading: dict[float, float] = {}
        for row in speciation:
            if row["species"] == species:
                observed_by_loading[float(row["loading_mol_co2_per_mol_mea"])] = float(
                    row["observed_mole_fraction"]
                )
        x = sorted(observed_by_loading)
        y = [observed_by_loading[value] for value in x]
        axis.scatter(
            x,
            y,
            color="#222222",
            marker="x",
            s=55,
            linewidths=1.6,
            label="Jakobsen data",
            zorder=5,
        )
        plotted.extend(
            {
                "panel": species,
                "series": "Jakobsen data",
                "role": "observation",
                "configuration_id": "",
                "loading": loading,
                "x": loading,
                "y": observed_by_loading[loading],
                "unit": "mole fraction",
            }
            for loading in x
        )

    axes[0, 0].set_title("Resolved mass density")
    axes[0, 0].set_ylabel("Mass density (kg m$^{-3}$)")
    axes[0, 1].set_title("Bulk relative permittivity")
    axes[0, 1].set_ylabel("Relative permittivity (-)")
    axes[1, 0].set_title("Carbamate speciation")
    axes[1, 0].set_ylabel("MEACOO$^-$ mole fraction")
    axes[1, 1].set_title("Bicarbonate speciation")
    axes[1, 1].set_ylabel("HCO$_3^-$ mole fraction")
    for axis in axes.flat:
        axis.set_xlabel("CO$_2$ loading (mol CO$_2$ mol$^{-1}$ MEA)")
        axis.grid(alpha=0.25)
        axis.legend(frameon=False, fontsize=8)
    fig.suptitle(
        "MEA Born-formulation and induced-association sensitivity at 313.15 K and 30 wt% MEA",
        fontsize=15,
    )
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"born_permittivity_sensitivity.{suffix}", dpi=220)
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
