"""Figures for the Baygi 2015 against ours (refit C_src) pCO2 comparison.

  pco2_comparison/baygi_ours_30wt_pco2        (a) 30 wt %, 313 and 393 K (our 40 and 120 degC rows)
  pco2_comparison/baygi_nasrifar_15wt_pco2    (b) 15.3 wt %, published Baygi and Nasrifar curves, our 15 wt % Aronu states
  pco2_comparison/baygi_fig11_check           recomputed Baygi curve on the digitized Baygi Fig. 11 curve (+ overlay on the paper figure)

    uv run python analyses/paper_validation/2015_baygi/scripts/render_pco2_comparison.py
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from baygi_model import ANALYSIS_DIR, REPO_ROOT
from MEA.common.plot_style import (
    MODEL_LINEWIDTH,
    REFERENCE_LINEWIDTH,
    apply_pressure_axes,
    save_figure_bundle,
    temperature_color,
    write_mpl_sidecar,
)

PROCESSED = ANALYSIS_DIR / "data" / "processed"
DIGITIZED = ANALYSIS_DIR / "data" / "digitized"
OUT = ANALYSIS_DIR / "results" / "pco2_comparison"
TRANSFER = REPO_ROOT / "analyses" / "mea_parameter_bundle" / "composition-transfer" / "second-look-source-R4-states.csv"
STYLE_SOURCE = "analyses/paper_validation/2015_baygi/scripts/render_pco2_comparison.py"
SOURCE_MARKERS = {"Aronu2011": "o", "Hilliard2008": "s", "Idris2014": "^", "Jou1995": "D", "Mamun2005": "v", "Xu2011": "P"}
BAYGI_COLOR = "#222222"


def bundle(fig, stem: str, title: str, description: str, data: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data_path = OUT / f"{stem}_plot_data.csv"
    data.to_csv(data_path, index=False, float_format="%.6g")
    save_figure_bundle(fig, OUT / stem)
    write_mpl_sidecar(OUT / f"{stem}.mpl.yaml", png_name=f"{stem}.png", svg_name=f"{stem}.svg", pdf_name=f"{stem}.pdf",
                      title=title, description=description, data_path=data_path, style_source=STYLE_SOURCE)
    plt.close(fig)
    print(OUT / f"{stem}.png")


def plot_30wt() -> None:
    rows = pd.read_csv(PROCESSED / "baygi_pco2_row_comparison.csv")
    grid = pd.read_csv(PROCESSED / "ours_c_src_loading_grid.csv")
    recomputed = pd.read_csv(PROCESSED / "baygi_fig11_recomputed_curves.csv")
    digitized = pd.read_csv(DIGITIZED / "baygi2015_fig11_model_curves.csv")
    fig, ax = plt.subplots(figsize=(10, 7))
    data = []
    for t_C, t_K, label in ((40, 313.15, "313 K"), (120, 393.15, "393 K")):
        color = temperature_color(t_C)
        d = digitized[digitized.series == label]
        ax.plot(d.CO2_loading, d.pCO2_kPa, color=BAYGI_COLOR, alpha=0.55, lw=3.2, solid_capstyle="round", zorder=2)
        data += [{"panel": "30 wt %", "series": f"Baygi Fig. 11 digitized, {label}", "kind": "curve", "x": x, "y": y}
                 for x, y in zip(d.CO2_loading, d.pCO2_kPa)]
        r = recomputed[(recomputed.temperature_K == t_K) & recomputed.baygi_pCO2_kPa.notna()]
        ax.plot(r.CO2_loading, r.baygi_pCO2_kPa, color=color, ls="--", lw=REFERENCE_LINEWIDTH, zorder=3)
        data += [{"panel": "30 wt %", "series": f"Baygi recomputed, {label}", "kind": "curve", "x": x, "y": y}
                 for x, y in zip(r.CO2_loading, r.baygi_pCO2_kPa)]
        g = grid[grid.temperature_C == t_C]
        ax.plot(g.CO2_loading, g.pCO2_kPa, color=color, ls="-", lw=MODEL_LINEWIDTH, zorder=4)
        data += [{"panel": "30 wt %", "series": f"ours C_src, {t_C} degC", "kind": "curve", "x": x, "y": y}
                 for x, y in zip(g.CO2_loading, g.pCO2_kPa)]
        for source, m in SOURCE_MARKERS.items():
            p = rows[(rows.temperature_C == t_C) & (rows.source == source)]
            if p.empty:
                continue
            ax.plot(p.CO2_loading, p.observed_pCO2_kPa, ls="", marker=m, ms=6.5, mfc=color, mec="white", mew=0.6, alpha=0.9, zorder=5)
            data += [{"panel": "30 wt %", "series": f"measured {source}, {t_C} degC", "kind": "points", "x": x, "y": y}
                     for x, y in zip(p.CO2_loading, p.observed_pCO2_kPa)]
    apply_pressure_axes(ax, title="30 wt % MEA: Baygi 2015 and our refit C_src, 40 degC (313 K) and 120 degC (393 K)")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(1e-4, 1e5)
    model_handles = [
        plt.Line2D([], [], color=BAYGI_COLOR, alpha=0.55, lw=3.2, label="Baygi 2015, digitized Fig. 11 line"),
        plt.Line2D([], [], color="0.3", ls="--", lw=REFERENCE_LINEWIDTH, label="Baygi 2015, recomputed here"),
        plt.Line2D([], [], color="0.3", ls="-", lw=MODEL_LINEWIDTH, label="ours, refit C_src (not adopted)"),
        plt.Line2D([], [], color=temperature_color(40), lw=4, label="40 degC (313 K)"),
        plt.Line2D([], [], color=temperature_color(120), lw=4, label="120 degC (393 K)"),
    ]
    source_handles = [plt.Line2D([], [], ls="", marker=m, color="0.4", ms=6.5, label=s) for s, m in SOURCE_MARKERS.items()]
    first = ax.legend(handles=model_handles, loc="upper left", title="Curves", fontsize=8.5)
    ax.add_artist(first)
    ax.legend(handles=source_handles, loc="lower right", title="Measured rows", ncol=2, fontsize=8.5)
    fig.tight_layout()
    bundle(fig, "baygi_ours_30wt_pco2", "30 wt % MEA pCO2: Baygi 2015 and ours",
           "pCO2 against loading at 313 K and 393 K (our 40 and 120 degC rows): measured points by source, the digitized "
           "Baygi 2015 Fig. 11 line, the Baygi model recomputed here, and our refit C_src on a loading grid.", pd.DataFrame(data))


def plot_15wt() -> None:
    fig9 = pd.read_csv(DIGITIZED / "baygi2015_fig09_model_curves.csv")
    nasrifar = pd.read_csv(DIGITIZED / "nasrifar2010_fig12a_model_curves.csv")
    states = pd.read_csv(TRANSFER)
    states = states[(states.mea_mass_fraction == 0.15) & (states.status == "evaluated")]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6), sharey=True)
    data = []
    for ax, (t_C, t_K) in zip(axes, ((40, 313.15), (60, 333.15), (80, 353.15))):
        color = temperature_color(t_C)
        b = fig9[fig9.temperature_K == t_K]
        ax.plot(b.CO2_loading, b.pCO2_kPa, color=BAYGI_COLOR, lw=REFERENCE_LINEWIDTH + 0.4, label="Baygi 2015 Fig. 9 (15.3 wt %)")
        data += [{"panel": f"{t_C} degC", "series": "Baygi Fig. 9 digitized", "kind": "curve", "x": x, "y": y}
                 for x, y in zip(b.CO2_loading, b.pCO2_kPa)]
        n = nasrifar[nasrifar.temperature_K == t_K]
        if len(n):
            ax.plot(n.CO2_loading, n.pCO2_kPa, color="#b6312c", ls="--", lw=REFERENCE_LINEWIDTH + 0.4, label="Nasrifar 2010 Fig. 12a (15.3 wt %)")
            data += [{"panel": f"{t_C} degC", "series": "Nasrifar Fig. 12a digitized", "kind": "curve", "x": x, "y": y}
                     for x, y in zip(n.CO2_loading, n.pCO2_kPa)]
        s = states[states.temperature_c == t_C].sort_values("loading")
        ax.plot(s.loading, s.observed_pa / 1000.0, ls="", marker="x", ms=7, color="0.25", label="measured, Aronu 2011 (15 wt %)")
        ax.plot(s.loading, s.predicted_pa / 1000.0, ls="", marker="o", ms=6, mfc=color, mec="white", label="ours, refit C_src, at those states")
        data += [{"panel": f"{t_C} degC", "series": "measured Aronu 2011 15 wt %", "kind": "points", "x": x, "y": y / 1000.0}
                 for x, y in zip(s.loading, s.observed_pa)]
        data += [{"panel": f"{t_C} degC", "series": "ours C_src 15 wt %", "kind": "points", "x": x, "y": y / 1000.0}
                 for x, y in zip(s.loading, s.predicted_pa)]
        apply_pressure_axes(ax, title=f"{t_C} degC ({t_K} K)")
        ax.set_xlim(0.0, 0.8)
        ax.set_ylim(1e-4, 1e4)
        ax.legend(loc="lower right", fontsize=7.8)
    for ax in axes[1:]:
        ax.set_ylabel("")
    fig.suptitle("15 wt % MEA: published Baygi and Nasrifar model lines, and our refit C_src on the Aronu 2011 states", y=1.0)
    fig.tight_layout()
    bundle(fig, "baygi_nasrifar_15wt_pco2", "15 wt % MEA pCO2: Baygi, Nasrifar and ours",
           "Digitized Baygi 2015 Fig. 9 lines (15.3 wt %) and Nasrifar and Tafazzol 2010 Fig. 12a lines (15.3 wt %, 313.15 K only "
           "at these temperatures), with the Aronu 2011 15 wt % rows and our refit C_src at those states. Jones 1959 data are not in "
           "this repository. Our model is drawn as points at the measured states, not as a curve.", pd.DataFrame(data))


def plot_fig11_check() -> None:
    c = pd.read_csv(PROCESSED / "baygi_fig11_recomputed_curves.csv")
    digitized = pd.read_csv(DIGITIZED / "baygi2015_fig11_model_curves.csv")
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.6))
    data = []
    for series, color in (("313 K", temperature_color(40)), ("393 K", temperature_color(120))):
        d = digitized[digitized.series == series]
        ax.plot(d.CO2_loading, d.pCO2_kPa, color=BAYGI_COLOR, alpha=0.55, lw=3.2)
        r = c[(c.series == series) & c.baygi_pCO2_kPa.notna()]
        ax.plot(r.CO2_loading, r.baygi_pCO2_kPa, color=color, ls="--", lw=REFERENCE_LINEWIDTH, label=f"recomputed, {series}")
        bx.plot(r.CO2_loading, r.ln_recomputed_over_digitized, color=color, lw=REFERENCE_LINEWIDTH, label=f"{series}, ions lumped with water")
        bx.plot(r.CO2_loading, r.ln_ions_dropped_over_digitized, color=color, ls=":", lw=REFERENCE_LINEWIDTH, label=f"{series}, ions dropped")
        data += [{"panel": "curves", "series": f"digitized {series}", "x": x, "y": y} for x, y in zip(d.CO2_loading, d.pCO2_kPa)]
        data += [{"panel": "curves", "series": f"recomputed {series}", "x": x, "y": y} for x, y in zip(r.CO2_loading, r.baygi_pCO2_kPa)]
        data += [{"panel": "ln ratio", "series": f"recomputed/digitized {series}", "x": x, "y": y}
                 for x, y in zip(r.CO2_loading, r.ln_recomputed_over_digitized)]
    ax.plot([], [], color=BAYGI_COLOR, alpha=0.55, lw=3.2, label="Baygi Fig. 11, digitized")
    apply_pressure_axes(ax, title="Baygi 2015 Fig. 11: paper line and recomputed model")
    ax.set_xlim(0.0, 1.2)
    ax.set_ylim(1e-6, 1e6)
    ax.legend(loc="lower right")
    bx.axhline(0.0, color="0.5", lw=0.8)
    bx.axhspan(-0.1, 0.1, color="0.9", zorder=0)
    bx.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    bx.set_ylabel("ln(recomputed / digitized pCO2)")
    bx.set_xlim(0.0, 1.0)
    bx.set_title("Recomputed over paper line (grey band: digitizing error, about 0.07)")
    bx.legend(fontsize=8)
    fig.tight_layout()
    bundle(fig, "baygi_fig11_check", "Baygi 2015 Fig. 11: recomputed against digitized",
           "Second check of the reproduction: the Baygi model recomputed here on the digitized Fig. 11 lines, and the "
           "log ratio between them.", pd.DataFrame(data))

    # overlay of the recomputed curves on the paper figure itself
    meta = json.loads((DIGITIZED / "baygi2015_fig11_model_curves.json").read_text())
    cal = meta["axis_calibration"]
    im = Image.open(meta["source_image"]).convert("RGB")
    draw = ImageDraw.Draw(im)
    for series, colour in (("313 K", (0, 90, 220)), ("393 K", (200, 0, 0))):
        r = c[(c.series == series) & c.baygi_pCO2_kPa.notna()]
        px = cal["x"]["left_frame_px"] + r.CO2_loading / (cal["x"]["values"][1] - cal["x"]["values"][0]) * (cal["x"]["right_frame_px"] - cal["x"]["left_frame_px"])
        lo, hi = np.log10(cal["y"]["values"])
        py = cal["y"]["bottom_frame_px"] + (np.log10(r.baygi_pCO2_kPa) - lo) / (hi - lo) * (cal["y"]["top_frame_px"] - cal["y"]["bottom_frame_px"])
        for x, y in zip(px, py):
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), outline=colour, width=2)
    im.save(OUT / "baygi_fig11_recomputed_on_paper_figure.png")
    print(OUT / "baygi_fig11_recomputed_on_paper_figure.png")


def main() -> int:
    plot_30wt()
    plot_15wt()
    plot_fig11_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
