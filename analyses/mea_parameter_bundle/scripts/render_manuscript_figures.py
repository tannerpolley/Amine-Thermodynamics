"""Render the four manuscript figures from the retained final-rerun figure data.

Reads only `results/final-rerun/figure-data/*.csv` (hash-checked against its
`input-hashes.json`); never evaluates the equation of state. Model values are
discrete evaluations at the observed states, so they are drawn as markers.
Usage: python render_manuscript_figures.py  (writes docs/scientific/latex/figures/generated/*.pdf)
"""

import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from manuscript_style import FULL_WIDTH, apply_style

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results/final-rerun/figure-data"
OUT = ROOT.parents[1] / "docs/scientific/latex/figures/generated"
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#555555"]
SOURCES = ["Aronu2011", "Hilliard2008", "Idris2014", "Jou1995", "Mamun2005", "Xu2011", "Wagner2013"]
SOURCE_STYLE = dict(zip(SOURCES, zip(COLORS, ["s", "o", "D", "^", "v", "<", "h"]), strict=True))
LABEL = {"Aronu2011": "Aronu et al. 2011", "Hilliard2008": "Hilliard 2008", "Idris2014": "Idris et al. 2014",
         "Jou1995": "Jou et al. 1995", "Mamun2005": "Ma'mun et al. 2005", "Xu2011": "Xu and Rochelle 2011",
         "Wagner2013": "Wagner et al. 2013"}
SPECIES = {"MEA": ("#0072B2", r"MEA"), "MEAH+": ("#CC79A7", r"MEAH$^+$"),
           "MEA + MEAH+": ("#0072B2", r"MEA + MEAH$^+$"), "MEACOO-": ("#D55E00", r"MEACOO$^-$"),
           "HCO3-": ("#009E73", r"HCO$_3^-$ + CO$_3^{2-}$")}
LOADING = r"CO$_2$ loading (mol CO$_2$/mol MEA)"


def read(name):
    with (DATA / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def check_inputs():
    expected = json.loads((DATA / "input-hashes.json").read_text())
    for name, digest in expected.items():
        actual = hashlib.sha256((DATA.parent / name).read_bytes()).hexdigest()
        assert actual == digest, f"{name} differs from its retained hash"


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def celsius(row):
    return float(row["temperature_K"]) - 273.15


def pressure_figure():
    rows = [r for r in read("pressure.csv") if r["kind"] in ("canonical", "wagner")]
    panels = [40, 60, 80, 100, 120]

    def panel(r):  # nominal series; Wagner near 353 and 392 K join the 80 and 120 degC panels
        return min(panels, key=lambda t: abs(t - celsius(r)))

    fig, axes = plt.subplots(2, 3, figsize=(FULL_WIDTH, 5.0), layout="constrained")
    for ax, t in zip(axes.flat, panels):
        group = [r for r in rows if panel(r) == t]
        for source in SOURCES:
            obs = [r for r in group if r["problem"] == "F1" and r["source"] == source]
            if obs:
                color, marker = SOURCE_STYLE[source]
                ax.scatter([float(r["loading"]) for r in obs], [float(r["observed"]) / 1e3 for r in obs],
                           marker=marker, facecolors="none", edgecolors=color, s=18, linewidths=0.7)
        for problem, style in (("F1", dict(marker=".", color="black", s=14)),
                               ("F6", dict(marker="x", color="#888888", s=10, linewidths=0.6))):
            calc = [r for r in group if r["problem"] == problem]
            ax.scatter([float(r["loading"]) for r in calc], [float(r["predicted"]) / 1e3 for r in calc],
                       zorder=3, **style)
        ax.set_yscale("log")
        ax.set_title(f"({chr(97 + panels.index(t))}) {t} °C", loc="left")
        ax.set_xlabel(LOADING)
        ax.grid(alpha=0.18)
    for ax in axes[:, 0]:
        ax.set_ylabel(r"$p_{\mathrm{CO_2}}$ (kPa)")
    legend = axes.flat[-1]
    legend.set_axis_off()
    handles = [Line2D([], [], linestyle="none", marker=SOURCE_STYLE[s][1], markerfacecolor="none",
                      markeredgecolor=SOURCE_STYLE[s][0], label=LABEL[s]) for s in SOURCES]
    handles += [Line2D([], [], linestyle="none", marker=".", color="black", label="F1, SSM+DS"),
                Line2D([], [], linestyle="none", marker="x", color="#888888", label="F6, source laws")]
    legend.legend(handles=handles, frameon=False, loc="center", title="Measured (open) and calculated")
    save(fig, "pressure")


def species_panel(ax, rows, problems):
    for name, (color, _) in SPECIES.items():
        part = [r for r in rows if r["species"] == name]
        if not part:
            continue
        for r in part:
            if r["problem"] != "F1":
                continue
            fitted = r.get("fitted_target", "True") == "True"
            x, obs, calc = float(r["loading"]), float(r["observed"]), float(r["predicted"])
            ax.plot([x, x], [obs, calc], color=color, linewidth=0.5, alpha=0.6)
            ax.scatter([x], [obs], marker="o" if fitted else "s", facecolors="none", edgecolors=color,
                       s=16, linewidths=0.7)
        for problem, marker in problems:
            calc = [r for r in part if r["problem"] == problem]
            ax.scatter([float(r["loading"]) for r in calc], [float(r["predicted"]) for r in calc],
                       marker=marker, color=color, s=9, linewidths=0.6, zorder=3)
    ax.set_xlabel(LOADING)
    ax.grid(alpha=0.18)


def speciation_figure():
    rows = read("speciation.csv")
    fitted = {r["target"]: r["fitted_target"] for r in read("pool-effect.csv") if r["problem"] == "F1"}
    for r in rows:
        r["fitted_target"] = fitted[r["target"]]
    fig, axes = plt.subplots(2, 3, figsize=(FULL_WIDTH, 5.0), layout="constrained", sharey=True)
    groups = [("Matin2012", 20)] + [("Bottinger2008", t) for t in (20, 40, 60, 80)]
    for i, (ax, (source, t)) in enumerate(zip(axes.flat, groups)):
        part = [r for r in rows if r["source"] == source and round(celsius(r)) == t]
        species_panel(ax, part, [("F1", ".")])
        name = "Matin et al., titration" if source == "Matin2012" else "Böttinger et al., NMR"
        ax.set_title(f"({chr(97 + i)}) {name}, {t} °C", loc="left")
    for ax in axes[:, 0]:
        ax.set_ylabel("Liquid mole fraction")
    legend = axes.flat[-1]
    legend.set_axis_off()
    handles = [Line2D([], [], linestyle="none", marker="o", markerfacecolor="none", markeredgecolor=c, label=l)
               for k, (c, l) in SPECIES.items() if k != "MEA + MEAH+"]
    handles[0].set_label(r"MEA; MEA + MEAH$^+$ (NMR)")
    handles += [Line2D([], [], linestyle="none", marker="o", markerfacecolor="none", markeredgecolor="black",
                       label="Measured, fitted"),
                Line2D([], [], linestyle="none", marker="s", markerfacecolor="none", markeredgecolor="black",
                       label="Measured, not fitted"),
                Line2D([], [], linestyle="none", marker=".", color="black", label="Calculated, F1")]
    legend.legend(handles=handles, frameon=False, loc="center")
    save(fig, "speciation")


def born_off_figure():
    mechanism = read("born-off-mechanism.csv")
    f1 = {r["identity"]: float(r["ln_pred_over_obs"]) for r in read("pressure.csv")
          if r["problem"] == "F1" and r["kind"] == "packet"}
    fig, axes = plt.subplots(2, 2, figsize=(FULL_WIDTH, 5.2), layout="constrained", sharex=True)
    for col, t in enumerate((313.15, 333.15)):
        part = sorted((r for r in mechanism if float(r["nominal_T_K"]) == t), key=lambda r: float(r["loading"]))
        x = [float(r["loading"]) for r in part]
        top, bottom = axes[0, col], axes[1, col]
        top.axhspan(-0.3, 0.3, color="#777777", alpha=0.12, linewidth=0)
        top.axhline(0, color="#777777", linewidth=0.6)
        top.scatter(x, [f1[r["state"]] for r in part], marker="o", color="black", s=12, label="F1, Born term")
        # F3 ln ratio = F1 ln ratio + Delta ln p at the same state (identity of the retained decomposition).
        top.scatter(x, [f1[r["state"]] + float(r["dlnp"]) for r in part], marker="s", facecolors="none",
                    edgecolors="#D55E00", s=14, linewidths=0.7, label="F3, Born term removed and refitted")
        top.set_title(f"({'ab'[col]}) Fitted pressures, {t - 273.15:.0f} °C", loc="left")
        bottom.axhline(0, color="#777777", linewidth=0.6)
        for column, label, marker, color in (("dQ", r"$\Delta Q$, activity sum", "^", "#0072B2"),
                                             ("dS", r"$\Delta S$, speciation sum", "v", "#D55E00"),
                                             ("dlnp", r"$\Delta\ln p_{\mathrm{CO_2}}$", "o", "black"),
                                             ("dH", r"$\Delta H$, vapor and reference", "+", "#009E73")):
            bottom.scatter(x, [float(r[column]) for r in part], marker=marker, s=12, linewidths=0.7,
                           label=label, **({"color": color} if marker == "+" else
                                           {"facecolors": "none", "edgecolors": color}))
        bottom.set_title(f"({'cd'[col]}) F3 $-$ F1 decomposition, {t - 273.15:.0f} °C", loc="left")
        bottom.set_xlabel(LOADING)
        for ax in (top, bottom):
            ax.grid(alpha=0.18)
    axes[0, 0].set_ylabel(r"$\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})$")
    axes[1, 0].set_ylabel("Change (ln units)")
    handles = axes[0, 0].get_legend_handles_labels()[0] + axes[1, 0].get_legend_handles_labels()[0]
    fig.legend(handles=handles, loc="outside lower center", ncol=3, frameon=False)
    save(fig, "born-off-mechanism")


def pool_figure():
    rows = [r for r in read("pool-effect.csv") if r["source"] == "Matin2012" and r["species"] == "HCO3-"]
    costs = read("pool-effect-costs.csv")
    fig, (left, right) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 2.9), layout="constrained")
    obs = {r["identity"]: r for r in rows if r["problem"] == "F1"}
    left.scatter([float(r["loading"]) for r in obs.values()], [float(r["observed"]) for r in obs.values()],
                 marker="o", facecolors="none", edgecolors="black", s=18, linewidths=0.7, label="Matin et al., measured")
    styles = {"F1": ("#0072B2", "."), "F2": ("#D55E00", "."), "F4": ("#0072B2", "x"), "F5": ("#D55E00", "x")}
    names = {"F1": "F1, SSM+DS, pool not fitted", "F2": "F2, original Born, pool not fitted",
             "F4": "F4, SSM+DS, pool fitted", "F5": "F5, original Born, pool fitted"}
    for problem, (color, marker) in styles.items():
        calc = [r for r in rows if r["problem"] == problem]
        left.scatter([float(r["loading"]) for r in calc], [float(r["predicted"]) for r in calc], marker=marker,
                     color=color, s=16 if marker == "." else 12, linewidths=0.7, label=names[problem])
    left.set_xlabel(LOADING)
    left.set_ylabel(r"HCO$_3^-$ + CO$_3^{2-}$ mole fraction")
    left.set_title(r"(a) Titration bicarbonate pool, 20 °C", loc="left")
    left.legend(fontsize=7, loc="upper left", facecolor="white", edgecolor="none", framealpha=1)
    point = {r["problem"]: (float(r["base141_cost"]), float(r["pool18_cost"])) for r in costs}
    for a, b in (("F1", "F4"), ("F2", "F5")):
        right.annotate("", xy=point[b], xytext=point[a],
                       arrowprops=dict(arrowstyle="->", color=styles[a][0], linewidth=0.7))
    for problem, (x, y) in point.items():
        color, marker = styles[problem]
        right.scatter([x], [y], marker="o" if marker == "." else "x", color=color, s=20, linewidths=0.9)
        right.annotate(problem, (x, y), textcoords="offset points", xytext=(5, 3), fontsize=8)
    right.set_xlabel("Cost of the 141 base targets")
    right.set_ylabel("Cost of the 18 pool targets")
    right.set_title("(b) Base-target and pool costs", loc="left")
    right.grid(alpha=0.18)
    save(fig, "pool-effect")


if __name__ == "__main__":
    check_inputs()
    apply_style()
    pressure_figure()
    speciation_figure()
    born_off_figure()
    pool_figure()
    print(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(OUT.glob("*.pdf"))}, indent=1))
