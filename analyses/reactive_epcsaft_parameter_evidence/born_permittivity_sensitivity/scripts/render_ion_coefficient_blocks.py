from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results" / "ion_coefficient_blocks"
FIGURES = ANALYSIS / "figures"
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7")
MARKERS = ("o", "s", "^", "D")


def _read(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _plot_block(
    axis: object,
    species: str,
    configuration_ids: list[str],
    names: dict[str, str],
    rows: list[dict[str, str]],
    plotted: list[dict[str, object]],
) -> None:
    for configuration_id, color, marker in zip(
        configuration_ids, COLORS, MARKERS, strict=True
    ):
        selected = sorted(
            (
                row
                for row in rows
                if row["configuration_id"] == configuration_id
                and row["species"] == species
            ),
            key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
        )
        x = [float(row["loading_mol_co2_per_mol_mea"]) for row in selected]
        y = [
            float(row["predicted_mole_fraction"])
            if row["predicted_mole_fraction"]
            else math.nan
            for row in selected
        ]
        axis.plot(x, y, color=color, marker=marker, label=names[configuration_id])
        plotted.extend(
            {
                "panel": species,
                "configuration_id": configuration_id,
                "series": names[configuration_id],
                "loading": x_value,
                "value": y_value,
            }
            for x_value, y_value in zip(x, y, strict=True)
        )
    observed = {
        float(row["loading_mol_co2_per_mol_mea"]): float(row["observed_mole_fraction"])
        for row in rows
        if row["species"] == species
    }
    x = sorted(observed)
    axis.scatter(
        x,
        [observed[value] for value in x],
        color="black",
        marker="x",
        s=55,
        label="Jakobsen data",
        zorder=5,
    )
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


def main() -> None:
    parameters = _read("parameter_table.csv")
    rows = _read("speciation_comparison.csv")
    names = {row["configuration_id"]: row["configuration_name"] for row in parameters}
    amine_ids = [
        row["configuration_id"]
        for row in parameters
        if "amine" in row["analysis_block"]
    ]
    carbonate_ids = [
        row["configuration_id"]
        for row in parameters
        if "carbonate" in row["analysis_block"]
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.5), constrained_layout=True)
    plotted: list[dict[str, object]] = []
    for axis, species, configuration_ids, title, ylabel in (
        (axes[0, 0], "MEAH+", amine_ids, "MEAH+ coefficient block", "MEAH$^+$ mole fraction"),
        (axes[0, 1], "MEACOO-", amine_ids, "MEACOO- coefficient block", "MEACOO$^-$ mole fraction"),
        (axes[1, 0], "HCO3-", carbonate_ids, "Bicarbonate coefficient block", "HCO$_3^-$ mole fraction"),
        (axes[1, 1], "CO3^2-", carbonate_ids, "Carbonate coefficient block", "CO$_3^{2-}$ mole fraction"),
    ):
        _plot_block(axis, species, configuration_ids, names, rows, plotted)
        axis.set_title(title)
        axis.set_ylabel(ylabel)
        axis.set_xlabel("CO$_2$ loading (mol CO$_2$ mol$^{-1}$ MEA)")
        axis.grid(alpha=0.25)
        axis.legend(frameon=False, fontsize=7)
    fig.suptitle("Independent MEA-ion and carbonate-ion permittivity coefficients")
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"ion_coefficient_blocks.{suffix}", dpi=220)
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
