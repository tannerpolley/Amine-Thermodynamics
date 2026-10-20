"""Render the accepted A7 endpoint's retained fitted loaded-density errors against A6's; no model calls.

Run from any directory with a Python environment containing matplotlib:
    python loaded-density-errors.py
Inputs are the A7 and A6 selected-assessment density CSVs and summaries, bound by SHA-256 below.
"""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
A7 = HERE.parent/"selected-assessment"
A6 = HERE.parents[1]/"amendment-6/selected-assessment"
INPUTS = {A7/"density.csv": "1983f82ba4b030623d909b364ecceb7dc60466b5ea4f327222fa199827dd2fdd", A7/"summary.json": "4d02aef2fa28534994d65e5364c0146e6d86e9d4f45aa656376a9333cd74c095",
          A6/"density.csv": "2918d2dec72687161fa01161012ad46d70e76349d8cfbd8652d568e9207144a4",
          A6/"summary.json": "af775385eadbb7396eacb69cbd9abd1defbec46eed35b3bfa300fec619edbd3d"}
for path, expected in INPUTS.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path


def ratios(base, cohort):
    summary = json.loads((base/"summary.json").read_text())
    with (base/"density.csv").open() as stream:
        rows = {row["id"]: row for row in csv.DictReader(stream)}
    selected = [rows[i] for i in summary["density"][cohort]["row_ids"]]
    assert all(row["parameter_sha256"] == summary["parameter_sha256"] for row in selected)
    return [(float(r["T_K"]) - 273.15, float(r["loading"]), float(r["error_kg_m3"])/float(r["s_kg_m3"]), r["id"]) for r in selected]


loadings = [0.1, 0.2, 0.3, 0.4]
colors = {0.1: "#0072B2", 0.2: "#009E73", 0.3: "#D55E00", 0.4: "#CC79A7"}
nearest = lambda a: min(loadings, key=lambda x: abs(x - a))
fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.0), sharey=True)
for axis, (cohort, title, marker) in zip(axes, [("Amundsen fitted 15", "Amundsen 2009", "o"), ("Hartono fitted 32", "Hartono 2014", "s")]):
    new, old = ratios(A7, cohort), ratios(A6, cohort)
    assert [r[3] for r in new] == [r[3] for r in old]
    axis.axhspan(-2, 2, color="#E7EDF2", zorder=0)
    axis.axhline(0, color="#666666", linewidth=0.7)
    for bound in (-2, 2):
        axis.axhline(bound, color="#444444", linestyle="--", linewidth=0.8)
    axis.scatter([r[0] for r in old], [r[2] for r in old], s=34, marker=marker, facecolors="none", edgecolors="#9A9A9A",
                 linewidths=1.0, zorder=2, label="A6 selected (splits at 12 family points)")
    for a in loadings:
        group = [r for r in new if nearest(r[1]) == a]
        axis.scatter([r[0] for r in group], [r[2] for r in group], s=34, marker=marker, color=colors[a], zorder=3,
                     label=f"A7 accepted, α ≈ {a:g}")
    within = sum(abs(r[2]) <= 2 for r in new)
    axis.set(title=f"{title}: A7 {within}/{len(new)} within 2s", xlabel="Temperature (°C)", ylim=(-3.1, 2.6))
    axis.spines[["top", "right"]].set_visible(False)
    for t, a, e, i in new:
        if abs(e) > 2:
            axis.annotate(f"{e:.2f}s", xy=(t, e), xytext=(t - 22, e - 0.25), fontsize=8,
                          arrowprops={"arrowstyle": "-", "color": "#444444", "linewidth": 0.6})
axes[0].set_ylabel(r"Signed density error / adopted $s$ (dimensionless)")
handles, labels = axes[1].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8)
fig.suptitle("Fitted loaded densities: split-free A7 endpoint against A6", fontsize=12)
fig.tight_layout(rect=(0, 0.13, 1, 0.95))
fig.savefig(HERE/"loaded-density-errors.png", dpi=180)
plt.close(fig)
print("Rendered 47 retained fitted rows for each endpoint; input SHA-256 checks passed.")
