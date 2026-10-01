"""Render the frozen 80 °C comparisons from retained rows; never solve a model."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
rows = [
    r
    for stage in (1, 3, 6)
    for r in csv.DictReader((HERE / f"assessment-stage-{stage}-rows.csv").open())
]
fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
styles = {
    "primary": ("#0072B2", "x"),
    "secondary": ("#D55E00", "+"),
    "adopted": ("#009E73", "s"),
}
for ax, group, title in zip(
    axes,
    ("canonical-80C-21", "never-accessed-80C"),
    ("Canonical 21 rows, 353.15 K", "Wagner 11 rows, 352.81–352.86 K"),
    strict=True,
):
    selected = [r for r in rows if r["group"] == group]
    observed = {r["target"]: r for r in selected}
    xs = [float(r["loading_mol_CO2_per_mol_MEA"]) for r in observed.values()]
    ys = [float(r["observed"]) / 1000 for r in observed.values()]
    if group == "never-accessed-80C":
        ax.errorbar(
            xs,
            ys,
            yerr=[max(0.02 * y, 0.4) for y in ys],
            fmt="o",
            color="black",
            markerfacecolor="none",
            capsize=2,
            markersize=4,
            label="Measured ± source estimate",
        )
    else:
        ax.scatter(
            xs, ys, facecolors="none", edgecolors="black", s=25, label="Measured"
        )
    for role, (color, marker) in styles.items():
        predicted = [r for r in selected if r["record_role"] == role and r["predicted"]]
        if predicted:
            ax.scatter(
                [float(r["loading_mol_CO2_per_mol_MEA"]) for r in predicted],
                [float(r["predicted"]) / 1000 for r in predicted],
                color=color,
                marker=marker,
                s=28,
                label=role.capitalize(),
            )
    ax.set(
        xlabel="CO₂ loading / (mol CO₂ per mol MEA)",
        ylabel="CO₂ partial pressure / kPa",
        yscale="log",
        title=title,
    )
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
fig.savefig(HERE / "pressure-80C.svg", metadata={"Date": None})
plt.close(fig)
