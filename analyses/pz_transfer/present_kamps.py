"""Issue 327: Kamps 2003 comparison figure and tables, and check-state table, from retained values only."""

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

AN = Path(__file__).resolve().parent
R = AN / "results"
rows = list(csv.DictReader((R / "kamps2003-A12.csv").open()))
summary = json.loads((R / "kamps2003-A12.json").read_text())["summary"]
COLORS = {"313.75": "#0072B2", "334.05": "#009E73", "354.35": "#E69F00", "374.65": "#D55E00", "374.7": "#D55E00", "395.0": "#CC79A7"}
LABELS = {"374.65": "374.65 / 374.7 K", "374.7": None}

fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True, layout="constrained")
for ax, (lo, hi, title) in zip(axes, ((1.9, 2.1, "≈2 mol PZ/kg"), (3.9, 4.0, "≈4 mol PZ/kg"))):
    for T, color in COLORS.items():
        sel = [r for r in rows if r["T_K"] == T and lo <= float(r["mPZ"]) <= hi]
        if not sel:
            continue
        for split, face in ((False, color), (True, "none")):
            s = [r for r in sel if (r["dense"] == "True") == split]
            ax.scatter([float(r["alpha_per_PZ"]) for r in s], [100 * float(r["relative_error"]) for r in s], s=26,
                       edgecolors=color, facecolors=face, label=LABELS.get(T, f"{T} K") if not split else None)
    ax.axhline(0, color="0.3", lw=0.6)
    ax.axvline(1, color="0.6", lw=0.6, ls=":")
    ax.set(title=title, xlabel="Loading (mol CO$_2$ / mol PZ)")
    ax.grid(alpha=0.2)
axes[0].set_ylabel("Calculated / measured total pressure − 1 (%)")
axes[0].scatter([], [], edgecolors="0.3", facecolors="none", label="hollow: model liquid split found")
axes[0].legend(fontsize=7)
fig.suptitle("Kamps 2003 total pressure (94 rows, not fitted) on the 12-coordinate refit; corrected temperatures")
fig.savefig(AN / "figures/kamps2003.png", dpi=160)


def line(name, s):
    return (f"| {name} | {s['n']} | {s['AARD_percent']:.1f} | {s['bias_percent']:+.1f} | {s['within_4kPa']} | {s['within_10kPa']} | "
            f"{s['phase_passed']} |")


head = ["| Group | Rows | AARD (%) | Signed bias (%) | Within ±4 kPa | Within ±10 kPa | No split found |", "|---|---:|---:|---:|---:|---:|---:|"]
lines = head + [line("All scored rows", summary["overall"])]
lines += [line(g, summary["by_group"][g]) for g in ("below 0.2 MPa", "374-395 K", "313-354 K, 0.2 MPa and above", "unloaded")]
lines += ["", "| Temperature (corrected), PZ molality | Carbamate law | Protonation law | Rows | AARD (%) | Signed bias (%) | Within ±10 kPa | No split found |",
          "|---|---|---|---:|---:|---:|---:|---:|"]
for k, s in summary["by_block"].items():
    r = next(r for r in rows if f"{r['T_K']} K, {r['mPZ']} mol/kg" == k)
    lines.append(f"| {k} | {r['carbamate_law']} | {r['protonation_law']} | {s['n']} | {s['AARD_percent']:.1f} | {s['bias_percent']:+.1f} | "
                 f"{s['within_10kPa']} | {s['phase_passed']} |")
(R / "kamps2003-tables.md").write_text("\n".join(lines) + "\n")
