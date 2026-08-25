from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import colormaps, colors
from matplotlib.lines import Line2D
import pandas as pd

from MEA.common.plot_style import finish_axes, save_figure_bundle


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/candidate_speciation_comparison"
FIGURES = ANALYSIS / "figures"
TARGETS = ("CO2", "MEA", "MEAH+", "MEA + MEAH+", "MEACOO-", "HCO3-", "CO3^2-")
CANDIDATE_LABELS = {
    "retained": "Retained source reaction correlations",
    "full_r4_r5": "Full R4/R5 temperature candidate",
    "calorimetry_balanced": "Calorimetry-balanced R4/R5 candidate",
}
PARTITIONS = {"training": ("o", "-"), "reserved": ("s", "--")}


def main() -> None:
    frame = pd.read_csv(RESULTS / "predictions.csv")
    metrics = pd.read_csv(RESULTS / "metrics.csv")
    FIGURES.mkdir(parents=True, exist_ok=True)
    temperatures_c = frame["temperature_k"] - 273.15
    norm = colors.Normalize(float(temperatures_c.min()), float(temperatures_c.max()))
    cmap = colormaps["viridis"]
    plotted = []
    for candidate, label in CANDIDATE_LABELS.items():
        selected_candidate = frame.loc[frame["candidate"] == candidate]
        figure, axes = plt.subplots(2, 4, figsize=(15.5, 8.3), constrained_layout=True)
        for axis, target in zip(axes.flat[:7], TARGETS, strict=True):
            panel = selected_candidate.loc[selected_candidate["target"] == target]
            for (partition, temperature_k, source), group in panel.groupby(
                ["partition", "temperature_k", "source"], sort=True
            ):
                group = group.sort_values("loading_mol_co2_per_mol_mea")
                marker, linestyle = PARTITIONS[partition]
                color = cmap(norm(float(temperature_k) - 273.15))
                axis.scatter(
                    group["loading_mol_co2_per_mol_mea"],
                    group["observed"],
                    marker=marker,
                    facecolors="none",
                    edgecolors=color,
                    s=35,
                    linewidths=1.0,
                    zorder=3,
                )
                if len(group) > 1:
                    axis.plot(
                        group["loading_mol_co2_per_mol_mea"],
                        group["predicted"],
                        color=color,
                        linestyle=linestyle,
                        linewidth=1.35,
                    )
                else:
                    axis.scatter(
                        group["loading_mol_co2_per_mol_mea"],
                        group["predicted"],
                        color=color,
                        marker="x",
                        s=32,
                    )
                for row in group.to_dict("records"):
                    plotted.append({**row, "figure": f"speciation_fit_{candidate}"})
            axis.set_yscale("log")
            axis.set_xlabel(r"CO$_2$ loading (mol mol$^{-1}$ MEA)")
            axis.set_ylabel("Liquid mole fraction")
            finish_axes(axis, title=target)

        legend_axis = axes.flat[7]
        legend_axis.axis("off")
        candidate_metrics = metrics.loc[
            (metrics["candidate"] == candidate) & (metrics["target"] == "all")
        ].set_index("partition")
        r4 = float(selected_candidate["candidate_r4_delta_ln_k_at_353_15_k"].iloc[0])
        r5 = float(selected_candidate["candidate_r5_delta_ln_k_at_353_15_k"].iloc[0])
        legend_axis.text(
            0.02,
            0.95,
            f"{label}\n\n"
            f"Δln K$_{{R4}}$(353.15 K) = {r4:.5f}\n"
            f"Δln K$_{{R5}}$(353.15 K) = {r5:.5f}\n\n"
            f"Training RMS factor = {candidate_metrics.loc['training', 'rms_factor']:.3f}\n"
            f"Reserved RMS factor = {candidate_metrics.loc['reserved', 'rms_factor']:.3f}",
            va="top",
            fontsize=10,
        )
        legend_axis.legend(
            handles=[
                Line2D(
                    [],
                    [],
                    color="black",
                    marker=marker,
                    markerfacecolor="none",
                    linestyle=linestyle,
                    label=partition,
                )
                for partition, (marker, linestyle) in PARTITIONS.items()
            ],
            loc="lower left",
            frameon=False,
            title="Observation points / model lines",
        )
        figure.colorbar(
            plt.cm.ScalarMappable(norm=norm, cmap=cmap),
            ax=axes,
            label="Temperature (°C)",
            shrink=0.75,
            pad=0.015,
        )
        figure.suptitle(f"30 wt% MEA speciation: {label}", fontsize=14)
        save_figure_bundle(figure, FIGURES / f"speciation_fit_{candidate}", dpi=220)
        plt.close(figure)

    with (FIGURES / "candidate_speciation_comparison_plot_data.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)


if __name__ == "__main__":
    main()
