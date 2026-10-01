"""Render retained Born-input sensitivity values without model calculations."""
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
GENERATED = ROOT / "docs/scientific/latex/figures/generated"
FIGURE_INPUTS = HERE / "figure-inputs.json"
VALUES = HERE / "born-input-sensitivity-values.csv"
os.environ.setdefault("MPLCONFIGDIR", str(HERE / "runs/matplotlib-cache"))
sys.path.insert(0, str(ROOT / "analyses/mea_parameter_bundle/scripts"))
from manuscript_style import FULL_WIDTH, apply_style

import matplotlib

matplotlib.use("Agg")
apply_style()
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

COLORS = {"11": "#0072B2", "00": "#D55E00"}
LABELS = {"11": "SSM+DS", "00": "Original Born"}
FIGURE = "born-input-sensitivity"
PDF = GENERATED / f"{FIGURE}.pdf"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with VALUES.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    complete = [row for row in rows if row["complete"].lower() == "true"]
    unavailable = [row for row in rows if row["complete"].lower() != "true"]
    if any(not row["delta_cost"] for row in complete):
        raise ValueError("complete sensitivity row is missing its retained cost change")
    if any(not row["reason"] for row in unavailable):
        raise ValueError("unavailable sensitivity row is missing its retained reason")

    fig, axes = plt.subplots(2, 2, figsize=(FULL_WIDTH, 5.35))
    axes = axes.ravel()
    panels = {
        "A": (axes[0], "water", "monoethanolamine"),
        "B": (axes[1], "eps_ion"),
        "C": (axes[2], "diameter_scale"),
        "D": (axes[3], "eps_MEA"),
    }
    plotted = []
    for letter, (ax, *series) in panels.items():
        ax.axhline(0, color="black", linewidth=0.6, linestyle=":", zorder=0)
        ax.grid(True, which="major", alpha=0.2)
        ax.set_axisbelow(True)
        if letter in {"A", "B"}:
            ax.set_yscale("symlog", linthresh=1)
        ax.text(0, 1.04, f"({letter.lower()})", transform=ax.transAxes,
                ha="left", va="bottom", fontweight="bold")

        if letter == "A":
            handles = []
            markers = {"water": "o", "monoethanolamine": "^"}
            series_labels = {"water": "water", "monoethanolamine": "MEA"}
            for form in ("11", "00"):
                for axis in series:
                    selected = [row for row in complete if row["panel"] == letter and
                                row["form"] == form and row["axis"] == axis]
                    selected.sort(key=lambda row: float(row["value"]))
                    marker = markers[axis]
                    face = COLORS[form] if form == "11" else "none"
                    if selected:
                        ax.scatter([float(row["value"]) for row in selected],
                                   [float(row["delta_cost"]) for row in selected],
                                   marker=marker, s=16, facecolors=face, edgecolors="black",
                                   linewidths=0.7, zorder=3)
                        plotted.extend(selected)
                    handles.append(Line2D([0], [0], marker=marker, linestyle="none",
                        markerfacecolor=face, markeredgecolor="black", markersize=4,
                        label=f"{LABELS[form]} {series_labels[axis]}"))
            ax.legend(handles=handles, loc="upper right", ncol=2, fontsize=8,
                      frameon=False, handletextpad=0.3, columnspacing=0.6)
            ax.set_xlabel("Solvent solvation factor (dimensionless)")
            ax.set_xlim(0.95, 2.05)
        else:
            axis = series[0]
            for form, marker in (("11", "o"), ("00", "x")):
                selected = [row for row in complete if row["panel"] == letter and
                            row["form"] == form and row["axis"] == axis]
                selected.sort(key=lambda row: float(row["value"]))
                if selected:
                    ax.scatter([float(row["value"]) for row in selected],
                               [float(row["delta_cost"]) for row in selected],
                               marker=marker, s=16, color=COLORS[form], linewidths=0.7, zorder=3)
                    plotted.extend(selected)
            handles = [
                Line2D([0], [0], marker="o", linestyle="none", color=COLORS["11"],
                       markersize=4, label=LABELS["11"] +
                       (r" ($\epsilon_{\mathrm{ion}}=2$ unavailable)" if letter == "B" else "")),
                Line2D([0], [0], marker="x", linestyle="none", color=COLORS["00"],
                       markersize=4, label=LABELS["00"]),
            ]
            ax.legend(handles=handles, loc="best", fontsize=8, frameon=False,
                      handletextpad=0.35, labelspacing=0.3)
            if letter == "B":
                ax.set_xscale("log", base=2)
                ax.set_xticks([2, 4, 8, 16, 32], ["2", "4", "8", "16", "32"])
                ax.set_xlabel(r"Ion-region relative permittivity" + "\n" +
                              r"$\epsilon_{\mathrm{ion}}$ (dimensionless)")
            elif letter == "C":
                ax.set_xlim(0.78, 1.22)
                ax.set_xlabel(r"Born-diameter multiplier for" + "\n" +
                              r"$\mathrm{MEAH^+}$, $\mathrm{MEACOO^-}$, and $\mathrm{HCO_3^-}$")
            else:
                ax.set_xlim(22, 42)
                ax.set_xlabel(r"MEA relative permittivity, $\epsilon_{\mathrm{MEA}}$ (dimensionless)")

    if len(plotted) != len(complete):
        raise ValueError(f"plotted {len(plotted)} of {len(complete)} complete retained rows")
    fig.supylabel(r"$\Delta C$ from matched form baseline" + "\n" +
                  r"(a,b symlog; linear within $|\Delta C|\leq 1$)", x=0.015)
    fig.subplots_adjust(left=0.17, right=0.99, bottom=0.12, top=0.94,
                        wspace=0.22, hspace=0.36)
    GENERATED.mkdir(parents=True, exist_ok=True)
    fig.savefig(HERE / f"{FIGURE}.svg")
    fig.savefig(HERE / f"{FIGURE}.png", dpi=160)
    fig.savefig(PDF)
    plt.close(fig)

    style = ROOT / "analyses/mea_parameter_bundle/scripts/manuscript_style.py"
    renderer = Path(__file__).resolve()
    source_hash = sha256(VALUES)
    details = json.loads(FIGURE_INPUTS.read_text())
    details.update({
        "renderer_file": str(renderer.relative_to(ROOT)),
        "renderer_sha256": sha256(renderer),
        "style_file": str(style.relative_to(ROOT)),
        "style_sha256": sha256(style),
        "manuscript_pdf": str(PDF.relative_to(ROOT)),
        "manuscript_pdf_sha256": sha256(PDF),
        "display": "No connecting lines or interpolation; panels A/B use symlog threshold 1, panels C/D use linear axes.",
        "values_sha256_after_render": source_hash,
        "rendered_complete_rows": len(plotted),
        "unavailable_rows_excluded": len(unavailable),
        "panel_labels": ["(a)", "(b)", "(c)", "(d)"],
        "encoding": "form colors plus filled/open or distinct marker shapes for grayscale",
        "figure_width_mm": 164.6,
    })
    FIGURE_INPUTS.write_text(json.dumps(details, indent=2) + "\n")

    manifest_path = HERE / "output-hashes.json"
    manifest = json.loads(manifest_path.read_text())
    outputs = [renderer, style, VALUES, FIGURE_INPUTS, manifest_path,
               HERE / f"{FIGURE}.png", HERE / f"{FIGURE}.svg", PDF]
    for path in outputs:
        manifest[str(path.relative_to(ROOT))] = sha256(path)
    manifest.pop(str(manifest_path.relative_to(ROOT)), None)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Rendered {len(plotted)} retained points from {len(rows)} rows; values SHA-256 {source_hash}.")


if __name__ == "__main__":
    main()
