"""Render the selected Held fit's retained density errors; no model calls.

Run from any directory with a Python environment containing matplotlib:
    python loaded-density-errors.py
Inputs are the adjacent selected-assessment CSV and summary, bound below.
"""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
INPUTS = {
    "density.csv": "2918d2dec72687161fa01161012ad46d70e76349d8cfbd8652d568e9207144a4",
    "summary.json": "af775385eadbb7396eacb69cbd9abd1defbec46eed35b3bfa300fec619edbd3d",
}
for name, expected in INPUTS.items():
    assert hashlib.sha256((BASE / "selected-assessment" / name).read_bytes()).hexdigest() == expected, name
summary = json.loads((BASE / "selected-assessment/summary.json").read_text())
with (BASE / "selected-assessment/density.csv").open() as stream:
    rows = {row["id"]: row for row in csv.DictReader(stream)}
cohorts = [("Amundsen fitted 15", "Amundsen 2009", "o"),
           ("Hartono fitted 32", "Hartono 2014", "x")]
colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#A66A00", "#000000", "#526D82", "#767600"]
temperatures = sorted({float(rows[identity]["T_K"]) for cohort, _, _ in cohorts
                       for identity in summary["density"][cohort]["row_ids"]})
assert len(temperatures) <= len(colors)
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.8), sharey=True)
for axis, (cohort, title, marker) in zip(axes, cohorts):
    selected = [rows[identity] for identity in summary["density"][cohort]["row_ids"]]
    assert all(row["parameter_sha256"] == summary["parameter_sha256"] for row in selected)
    ratios = [float(row["error_kg_m3"]) / float(row["s_kg_m3"]) for row in selected]
    assert all(abs(value) <= 2 for value in ratios)
    axis.axhspan(-2, 2, color="#E7EDF2", zorder=0)
    axis.axhline(0, color="#666666", linewidth=0.7)
    for bound in (-2, 2):
        axis.axhline(bound, color="#444444", linestyle="--", linewidth=0.8)
    for temperature, color in zip(temperatures, colors):
        group = [row for row in selected if float(row["T_K"]) == temperature]
        axis.scatter([float(row["loading"]) for row in group],
                     [float(row["error_kg_m3"]) / float(row["s_kg_m3"]) for row in group],
                     s=36, marker=marker, color=color, linewidths=1.3,
                     label=f"{temperature - 273.15:g} °C", zorder=3)
    axis.set(title=f"{title}: {len(selected)}/{len(selected)} within 2s",
             xlabel=r"Loading $\alpha$ (mol CO$_2$/mol MEA)", ylim=(-2.3, 2.3),
             xlim=(0.075, 0.415), xticks=[0.1, 0.2, 0.3, 0.4])
    axis.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel(r"Signed density error / adopted $s$ (dimensionless)")
axes[0].annotate("80 °C: −1.976s", xy=(0.3, -1.9764146338225996),
                 xytext=(0.16, -1.5), fontsize=9,
                 arrowprops={"arrowstyle": "-", "color": "#444444"})
handles, labels = axes[1].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=8, frameon=False, fontsize=8)
fig.suptitle("Selected Held larger-A: fitted loaded densities", fontsize=12)
fig.tight_layout(rect=(0, 0.08, 1, 0.95))
fig.savefig(HERE / "loaded-density-errors.png", dpi=180)
plt.close(fig)
print("Rendered 47 retained fitted rows; input SHA-256 checks passed.")
