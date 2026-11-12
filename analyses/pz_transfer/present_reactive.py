"""Frozen A versus A12 refit: hold-out and calibration figures and tables from retained values only."""

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

AN = Path(__file__).resolve().parent
R = AN / "results"
TAGS = {
    "A": ("Frozen stage-4 A (17 coordinates)", "#0072B2", "o"),
    "A12": ("12-coordinate refit, unconstrained", "#999999", "^"),
    "A12s": ("12-coordinate refit, stability-enforced (record)", "#D55E00", "s"),
}
record = {t: json.loads((R / f"reactive-{t}-record.json").read_text()) for t in TAGS}
hold = {t: list(csv.DictReader((R / f"holdout-{t}.csv").open())) for t in TAGS}

fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True, layout="constrained")
for ax, T in zip(axes, ("313.1", "353.15", "393.15")):
    rows = [r for r in hold["A"] if r["T_K"] == T]
    a = np.array([float(r["alpha_per_PZ"]) for r in rows])
    u = np.array([100 * float(r["total_uncertainty_kPa"]) / float(r["observed_kPa"]) for r in rows])
    ax.errorbar(a, 0 * a, yerr=u, fmt="none", ecolor="0.6", capsize=2, label="Source total uncertainty")
    for t, (label, color, marker) in TAGS.items():
        rows = [r for r in hold[t] if r["T_K"] == T]
        ax.scatter([float(r["alpha_per_PZ"]) for r in rows], [100 * float(r["relative_error"]) for r in rows],
                   edgecolors=color, marker=marker, s=22, label=label, facecolors="none" if t != "A12s" else color)
    ax.axhline(0, color="0.3", lw=0.6)
    ax.set(title=f"{T} K", xlabel="Loading (mol CO$_2$ / mol PZ)")
    ax.grid(alpha=0.2)
axes[0].set_ylabel("Calculated / measured pCO$_2$ − 1 (%)")
axes[0].legend(fontsize=7)
fig.suptitle("Ermatchkov 2006 hold-out (52 rows, not fitted); 393 K is outside the 283–333 K carbamate-law range")
fig.savefig(AN / "figures/holdout-ermatchkov2006.png", dpi=160)

fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
for t, (label, color, marker) in TAGS.items():
    rows = [r for r in csv.DictReader((R / f"reactive-{t}-residuals.csv").open()) if r["group"] == "pressure"]
    ax.scatter([float(r["mPZ"]) for r in rows], [100 * (float(r["calculated"]) / float(r["observed_fraction"]) - 1) for r in rows],
               edgecolors=color, marker=marker, s=18, label=label, facecolors="none" if t != "A12s" else color)
ax.axhline(0, color="0.3", lw=0.6)
ax.set(xlabel="PZ molality (mol/kg water)", ylabel="Calculated / measured pCO$_2$ − 1 (%)", title="Hilliard D.5 calibration pressures (fitted)")
ax.grid(alpha=0.2)
ax.legend(fontsize=7)
fig.savefig(AN / "figures/calibration-hilliard.png", dpi=160)


def pct(x):
    return f"{x:.1f}"


lines = ["| Quantity | Frozen A | Unconstrained refit | Stability-enforced refit (record) |", "|---|---:|---:|---:|"]
for name, get in [
    ("Calibration cost (294 observations)", lambda r: f"{r['cost']:.1f}"),
    ("NMR whitened RMS, q=0.02", lambda r: f"{r['NMR_RMS']:.2f}"),
    ("Hilliard pressure RMS / 2 % scale", lambda r: f"{r['pressure_RMS']:.2f}"),
    ("Hilliard mean absolute relative error (%)", lambda r: pct(r["hilliard"]["MARE_percent"])),
    ("Hilliard signed bias (%)", lambda r: pct(r["hilliard"]["bias_percent"])),
    *[(f"Hilliard bias at ~{c} mol/kg (%)", lambda r, c=c: pct(r["hilliard"]["by_concentration"][c]["bias_percent"])) for c in ("0.9", "2.0", "2.5", "3.6", "5.0")],
    ("NMR PZCOO⁻+HPZCOO mean absolute error (fraction of PZ)", lambda r: f"{r['carbamate_MAE']['1']:.4f}"),
    ("NMR PZ(COO)₂²⁻ mean absolute error (fraction of PZ)", lambda r: f"{r['carbamate_MAE']['2']:.4f}"),
    ("Census: states with no extra phase / 183", lambda r: str(r["census"]["no_extra_phase"])),
    ("Census: undecided states", lambda r: str(r["census"]["undecided"])),
    ("Census: liquid splits", lambda r: ", ".join(r["census"]["dense_split"]) or "none"),
    ("Hold-out mean absolute relative error, 52 rows (%)", lambda r: pct(r["holdout"]["MARE_percent"])),
    ("Hold-out signed bias (%)", lambda r: pct(r["holdout"]["bias_percent"])),
    ("Hold-out RMS of (calc − meas)/source uncertainty", lambda r: f"{r['holdout']['RMS_scaled_residual']:.2f}"),
    ("Hold-out rows within source uncertainty / 52", lambda r: str(r["holdout"]["within_source_uncertainty"])),
    ("Hold-out bubble states with no extra phase / 52", lambda r: str(r["holdout"]["phase_passed"])),
    ("Hold-out, 313–353 K only (37 rows) (%)", lambda r: pct(r["holdout"]["excluding_393K"]["313-353 K"]["MARE_percent"])),
]:
    lines.append("| " + " | ".join([name] + [get(record[t]) for t in TAGS]) + " |")
lines += ["", "| Hold-out block | Rows | Frozen A error / bias (%) | Unconstrained refit | Stability-enforced refit (record) |", "|---|---:|---:|---:|---:|"]
for k, v in record["A"]["holdout"]["by_temperature_and_concentration"].items():
    w = [record[t]["holdout"]["by_temperature_and_concentration"][k] for t in TAGS]
    lines.append(f"| {k} | {v['n']} | " + " | ".join(f"{pct(q['MARE_percent'])} / {pct(q['bias_percent'])}" for q in w) + " |")
(R / "reactive-tables.md").write_text("\n".join(lines) + "\n")
