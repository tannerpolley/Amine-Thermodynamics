from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from MEA.common.analysis_io import read_csv_rows as _read


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results" / "ion_diameter_fit"
FIGURES = ANALYSIS / "figures"
SOURCE = ANALYSIS.parents[3] / (
    "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
)
SPECIES = ("MEA", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-")
COLORS = {
    "shell_born_ion_suppressed_no_induced": "#009E73",
    "shell_born_ion_suppressed": "#0072B2",
}


def main() -> None:
    predictions = _read(RESULTS / "fit_predictions.csv")
    parameters = _read(RESULTS / "fitted_parameters.csv")
    source_species = {row["record_id"]: row["species"] for row in _read(SOURCE)}
    names = {row["configuration_id"]: row["configuration_name"] for row in parameters}
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.0), constrained_layout=True)
    plotted = []
    for axis, species in zip(axes.flat[:5], SPECIES, strict=True):
        observed = {}
        for row in predictions:
            if source_species[row["record_id"]] == species:
                loading = float(row["loading_mol_co2_per_mol_mea"])
                observed[loading] = float(row["observed_mole_fraction"])
        axis.scatter(
            sorted(observed),
            [observed[value] for value in sorted(observed)],
            color="#222222",
            marker="x",
            s=55,
            label="Jakobsen data",
            zorder=5,
        )
        for configuration_id, name in names.items():
            rows = sorted(
                (
                    row
                    for row in predictions
                    if row["configuration_id"] == configuration_id
                    and source_species[row["record_id"]] == species
                ),
                key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
            )
            axis.plot(
                [float(row["loading_mol_co2_per_mol_mea"]) for row in rows],
                [float(row["predicted_mole_fraction"]) for row in rows],
                color=COLORS[configuration_id],
                linestyle="-" if configuration_id.endswith("suppressed") else "--",
                marker="o" if configuration_id.endswith("suppressed") else "v",
                label=name,
            )
            plotted.extend(
                {
                    **row,
                    "species": species,
                }
                for row in rows
            )
        axis.set_title(species)
        axis.set_xlabel("CO$_2$ loading (mol CO$_2$ mol$^{-1}$ MEA)")
        axis.set_ylabel("Mole fraction")
        axis.grid(alpha=0.25)
    axes[0, 0].legend(frameon=False, fontsize=7)
    table_axis = axes.flat[5]
    table_axis.axis("off")
    table_rows = []
    for configuration_id in names:
        selected = [
            row for row in parameters if row["configuration_id"] == configuration_id
        ]
        table_rows.append(
            [
                "IA on" if configuration_id.endswith("suppressed") else "IA off",
                f"{float(selected[0]['fitted']):.5f}",
                f"{float(selected[1]['fitted']):.5f}",
            ]
        )
    table_axis.table(
        cellText=table_rows,
        colLabels=("Case", "$\\sigma_{MEAH^+}$", "$\\sigma_{MEACOO^-}$"),
        cellLoc="center",
        loc="center",
    )
    table_axis.set_title("Fitted segment diameters (Å)")
    fig.suptitle(
        "Two-ion-diameter fit under shell Born and ion-suppressed permittivity",
        fontsize=15,
    )
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"ion_diameter_fit.{suffix}", dpi=220)
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
