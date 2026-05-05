from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ANALYSIS_DIR = Path(__file__).resolve().parent
OUT_DIR = ANALYSIS_DIR / "out"


def main() -> int:
    raw_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity_raw.csv"
    if not raw_path.exists():
        raise RuntimeError(
            f"Missing {raw_path}. Run `uv run python analysis\\2015_Baygi\\generate_baygi_tables.py` first."
        )
    data = pd.read_csv(raw_path)
    derived_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity_plot_data.csv"
    data.to_csv(derived_path, index=False)

    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    for temperature_C, subset in data.groupby("temperature_C"):
        subset = subset.sort_values("CO2_loading")
        ax.semilogy(
            subset["CO2_loading"],
            subset["legacy_pcsaft_CO2_pressure_kPa"],
            ":",
            label=f"{temperature_C:g} C legacy PC-SAFT",
        )
        ax.semilogy(
            subset["CO2_loading"],
            subset["epcsaft_CO2_pressure_kPa"],
            "-",
            label=f"{temperature_C:g} C neutral ePC-SAFT",
        )
    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("CO2 partial pressure, kPa")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()

    svg_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity.svg"
    png_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity.png"
    fig.savefig(svg_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Baygi pressure plot data: {derived_path}")
    print(f"Baygi pressure SVG: {svg_path}")
    print(f"Baygi pressure PNG: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
