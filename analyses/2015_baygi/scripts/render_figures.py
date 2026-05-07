from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from MEA.common.config import JOU_TEMPERATURES_C
from MEA.common.plot_style import (
    EPCSAFT_NEUTRAL_LINESTYLE,
    LEGACY_PCSAFT_LINESTYLE,
    PRESSURE_FIGSIZE,
    apply_pressure_axes,
    temperature_color,
)


ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
OUT_DIR = ANALYSIS_DIR / "results" / "neutral_parity"


def main() -> int:
    raw_path = PROCESSED_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity_raw.csv"
    if not raw_path.exists():
        raise RuntimeError(
            f"Missing {raw_path}. Run `uv run python analyses\\2015_baygi\\scripts\\generate_data.py` first."
        )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(raw_path)
    derived_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity_plot_data.csv"
    data.to_csv(derived_path, index=False)

    fig, ax = plt.subplots(figsize=PRESSURE_FIGSIZE)
    for temperature_C in JOU_TEMPERATURES_C:
        subset = data[data["temperature_C"] == temperature_C]
        if subset.empty:
            continue
        subset = subset.sort_values("CO2_loading")
        color = temperature_color(temperature_C)
        ax.semilogy(
            subset["CO2_loading"],
            subset["legacy_pcsaft_CO2_pressure_kPa"],
            LEGACY_PCSAFT_LINESTYLE,
            color=color,
            alpha=0.65,
            label=f"{temperature_C:g} C legacy PC-SAFT",
        )
        ax.semilogy(
            subset["CO2_loading"],
            subset["epcsaft_CO2_pressure_kPa"],
            EPCSAFT_NEUTRAL_LINESTYLE,
            color=color,
            label=f"{temperature_C:g} C neutral ePC-SAFT",
        )
    apply_pressure_axes(ax)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()

    svg_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity.svg"
    png_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity.png"
    sidecar_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity.mpl.yaml"
    if not sidecar_path.exists():
        sidecar_path.write_text(
            "figure:\n"
            "  png: baygi_neutral_epcsaft_pcsaft_pressure_parity.png\n"
            "  svg: baygi_neutral_epcsaft_pcsaft_pressure_parity.svg\n"
            "style:\n"
            "  source: analyses/2015_baygi/scripts/render_figures.py\n",
            encoding="utf-8",
        )
    fig.savefig(svg_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Baygi pressure plot data: {derived_path}")
    print(f"Baygi style sidecar: {sidecar_path}")
    print(f"Baygi pressure SVG: {svg_path}")
    print(f"Baygi pressure PNG: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
