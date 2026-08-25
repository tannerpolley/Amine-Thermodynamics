from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[5]
OUTPUT = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/pressure_first/results/grepe_gate0"
)
SOURCE = OUTPUT / "grepe_hilliard_curve.csv"
PLOTTED = OUTPUT / "grepe_hilliard_curve_plotted.csv"
FIGURE = OUTPUT / "grepe_hilliard_curve"


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "observation_id": row["observation_id"],
            "loading_mol_co2_per_mol_mea": float(row["loading_mol_co2_per_mol_mea"]),
            "observed_pco2_pa": float(row["observed_pco2_pa"]),
            "baseline_pco2_pa": (
                "" if not row["baseline_pco2_pa"] else float(row["baseline_pco2_pa"])
            ),
            "candidate_pco2_pa": (
                "" if not row["candidate_pco2_pa"] else float(row["candidate_pco2_pa"])
            ),
            "candidate_status": row["status"],
        }
        for row in rows
    ]
    with PLOTTED.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 10.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    figure, axis = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    loading = [float(row["loading_mol_co2_per_mol_mea"]) for row in plotted]
    observed = [float(row["observed_pco2_pa"]) / 1000.0 for row in plotted]
    axis.scatter(
        loading,
        observed,
        marker="o",
        facecolors="white",
        edgecolors="black",
        linewidths=1.0,
        s=36,
        label="Hilliard (2008) data",
        zorder=3,
    )
    baseline_rows = [row for row in plotted if row["baseline_pco2_pa"] != ""]
    axis.plot(
        [float(row["loading_mol_co2_per_mol_mea"]) for row in baseline_rows],
        [float(row["baseline_pco2_pa"]) / 1000.0 for row in baseline_rows],
        color="#7A7A7A",
        linestyle="--",
        linewidth=1.7,
        label="Initial two-ion diameters",
    )
    candidate_rows = [row for row in plotted if row["candidate_pco2_pa"] != ""]
    axis.plot(
        [float(row["loading_mol_co2_per_mol_mea"]) for row in candidate_rows],
        [float(row["candidate_pco2_pa"]) / 1000.0 for row in candidate_rows],
        color="#0072B2",
        linewidth=2.1,
        marker="s",
        markersize=3.5,
        label="One-iteration GREPE diagnostic fit",
    )
    axis.set_yscale("log")
    axis.set_xlabel(r"CO$_2$ loading, $\alpha$ (mol CO$_2$ mol$^{-1}$ MEA)")
    axis.set_ylabel(r"CO$_2$ partial pressure, $P_{\mathrm{CO_2}}$ (kPa)")
    axis.set_title(r"Reactive MEA equilibrium at 313.15 K and 30 wt% MEA")
    axis.grid(axis="y", which="major", color="#D4D4D4", linewidth=0.7)
    axis.legend(frameon=False, loc="upper left")
    failed = len(plotted) - len(candidate_rows)
    if failed:
        axis.text(
            0.99,
            0.03,
            f"{failed} candidate row(s) non-evaluable",
            transform=axis.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
        )
    for suffix in ("svg", "png", "pdf"):
        figure.savefig(FIGURE.with_suffix(f".{suffix}"), dpi=220)
    plt.close(figure)


if __name__ == "__main__":
    main()
