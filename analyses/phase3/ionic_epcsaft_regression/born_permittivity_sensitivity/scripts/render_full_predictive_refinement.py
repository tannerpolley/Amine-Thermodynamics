from __future__ import annotations

import csv
import json

import matplotlib.pyplot as plt
from matplotlib import colormaps, colors
from matplotlib.lines import Line2D

from generate import ANALYSIS, SOURCE
from run_full_predictive_refinement import _pressure_rows
from MEA.common.analysis_io import read_csv_rows as _read
from MEA.common.plot_style import save_figure_bundle


RESULTS = ANALYSIS / "results/full_predictive_refinement"
FIGURES = ANALYSIS / "figures"
STEM = FIGURES / "full_predictive_pressure_speciation_refinement"
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9")
MARKERS = ("o", "s", "^", "D", "P", "X")


def main() -> None:
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    fit_rows = _read(RESULTS / "fit_rows.csv")
    pressure_source = {row["observation_id"]: row for row in _pressure_rows()}
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        speciation_source = {row["record_id"]: row for row in csv.DictReader(stream)}

    plotted = []
    for row in fit_rows:
        if row["unit"] == "pascal":
            source = pressure_source[row["identity"]]
            plotted.append(
                {
                    "block": "pressure",
                    "identity": row["identity"],
                    "temperature_k": source["temperature_K"],
                    "mea_mass_fraction": source["mea_mass_fraction"],
                    "source_key": source["source_key"],
                    "loading_mol_co2_per_mol_mea": source[
                        "co2_loading_mol_per_mol_mea"
                    ],
                    "species": "CO2",
                    "observed": row["observed"],
                    "model": row["predicted"],
                    "model_role": summary["pressure_formulation"],
                }
            )
        else:
            source = speciation_source[row["identity"]]
            plotted.append(
                {
                    "block": "speciation",
                    "identity": row["identity"],
                    "temperature_k": source["temperature_K"],
                    "mea_mass_fraction": "0.30",
                    "source_key": "Jakobsen2005",
                    "loading_mol_co2_per_mol_mea": source[
                        "co2_loading_mol_per_mol_mea"
                    ],
                    "species": source["species"],
                    "observed": row["observed"],
                    "model": row["predicted"],
                    "model_role": "shared-parameter fit",
                }
            )
    with (RESULTS / "plotted_values.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream, fieldnames=tuple(plotted[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(plotted)

    parameters = _read(RESULTS / "parameter_table.csv")
    figure = plt.figure(figsize=(15.0, 9.0), constrained_layout=True)
    grid = figure.add_gridspec(2, 2, height_ratios=(4.0, 1.15))
    pressure_ax = figure.add_subplot(grid[0, 0])
    speciation_ax = figure.add_subplot(grid[0, 1])
    table_ax = figure.add_subplot(grid[1, :])

    pressure = [row for row in plotted if row["block"] == "pressure"]
    temperatures = [float(row["temperature_k"]) for row in pressure]
    normalization = colors.Normalize(
        min(temperatures) - 273.15, max(temperatures) - 273.15
    )
    color_map = colormaps["viridis"]
    source_markers = {"Hilliard2008": "^", "Jou1995": "D"}
    for row in pressure:
        temperature_c = float(row["temperature_k"]) - 273.15
        pressure_ax.scatter(
            float(row["loading_mol_co2_per_mol_mea"]),
            float(row["observed"]),
            color=color_map(normalization(temperature_c)),
            marker=source_markers[row["source_key"]],
            s=42,
        )
    groups = sorted(
        {(float(row["temperature_k"]), row["source_key"]) for row in pressure}
    )
    for temperature_k, source_key in groups:
        rows = sorted(
            (
                row
                for row in pressure
                if float(row["temperature_k"]) == temperature_k
                and row["source_key"] == source_key
            ),
            key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
        )
        pressure_ax.plot(
            [float(row["loading_mol_co2_per_mol_mea"]) for row in rows],
            [float(row["model"]) for row in rows],
            color=color_map(normalization(temperature_k - 273.15)),
            linestyle="--",
            linewidth=1.4,
        )
    pressure_ax.set_yscale("log")
    pressure_ax.set_xlabel(r"CO$_2$ loading, mol CO$_2$/mol MEA")
    pressure_ax.set_ylabel(r"CO$_2$ partial pressure, Pa")
    pressure_ax.set_title("30 wt% MEA pressure block")
    pressure_ax.grid(True, which="both", alpha=0.22)
    source_legend = pressure_ax.legend(
        handles=[
            Line2D([], [], color="black", marker=marker, linestyle="None", label=source)
            for source, marker in source_markers.items()
        ],
        title="Observation source",
        fontsize=7.5,
        loc="upper left",
    )
    pressure_ax.add_artist(source_legend)
    pressure_ax.legend(
        handles=[Line2D([], [], color="black", linestyle="--", label="30% MEA model")],
        fontsize=7.5,
        loc="lower right",
    )
    figure.colorbar(
        plt.cm.ScalarMappable(norm=normalization, cmap=color_map),
        ax=pressure_ax,
        label="Temperature (°C)",
        pad=0.02,
    )

    speciation = [row for row in plotted if row["block"] == "speciation"]
    for index, name in enumerate(sorted({row["species"] for row in speciation})):
        rows = sorted(
            (row for row in speciation if row["species"] == name),
            key=lambda row: float(row["loading_mol_co2_per_mol_mea"]),
        )
        loading = [float(row["loading_mol_co2_per_mol_mea"]) for row in rows]
        speciation_ax.scatter(
            loading,
            [float(row["observed"]) for row in rows],
            color=COLORS[index],
            marker=MARKERS[index],
            s=52,
            label=f"{name} data",
        )
        speciation_ax.plot(
            loading,
            [float(row["model"]) for row in rows],
            color=COLORS[index],
            linewidth=1.8,
            label=f"{name} model",
        )
    speciation_ax.set_yscale("log")
    speciation_ax.set_xlabel(r"CO$_2$ loading, mol CO$_2$/mol MEA")
    speciation_ax.set_ylabel("Liquid mole fraction")
    speciation_ax.set_title("Direct Jakobsen speciation block, 40 °C")
    speciation_ax.grid(True, which="both", alpha=0.22)
    speciation_ax.legend(fontsize=7.5, ncol=2)

    labels = {
        "pair/carbon-dioxide/monoethanolamine/k_ij": r"$k_{\mathrm{CO_2,MEA}}$",
        "component/protonated-monoethanolamine/segment_diameter": r"$\sigma_{\mathrm{MEAH^+}}$ (Å)",
        "component/carbamate-anion/segment_diameter": r"$\sigma_{\mathrm{MEACOO^-}}$ (Å)",
    }
    table_ax.axis("off")
    table = table_ax.table(
        cellText=[
            [
                labels[row["identity"]],
                f"{float(row['start']):.6g}",
                f"{float(row['fitted']):.8g}",
                f"[{float(row['lower']):g}, {float(row['upper']):g}]",
            ]
            for row in parameters
        ],
        colLabels=("Shared parameter", "Start", "Fitted", "Bounds"),
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.35)
    figure.suptitle(
        f"30 wt% full reactive pressure–speciation refinement | {len(plotted)} targets | "
        f"cost = {float(summary['final_cost']):.4f} | "
        f"Jacobian cond. = {float(summary['jacobian_condition_number']):.1f}",
        fontsize=15,
    )
    FIGURES.mkdir(parents=True, exist_ok=True)
    save_figure_bundle(figure, STEM, dpi=220)
    plt.close(figure)
    print(STEM)


if __name__ == "__main__":
    main()
