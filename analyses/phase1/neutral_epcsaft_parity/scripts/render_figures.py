from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.config import JOU_TEMPERATURES_C
from MEA.common.plot_style import (
    EPCSAFT_NEUTRAL_LINESTYLE,
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    LEGACY_PCSAFT_LINESTYLE,
    MODEL_LINEWIDTH,
    PRESSURE_FIGSIZE,
    REFERENCE_LINEWIDTH,
    apply_pressure_axes,
    save_figure_bundle,
    temperature_color,
    write_mpl_sidecar,
)
from MEA.epcsaft_neutral.parameters import DATASET_DIR

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
OUT_DIR = ANALYSIS_DIR / "results" / "pressure"


def require(path: Path) -> Path:
    if not path.exists():
        raise RuntimeError(f"Missing {path}. Run analyses\\neutral_epcsaft_parity\\scripts\\generate_data.py first.")
    return path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = pd.read_csv(require(PROCESSED_DIR / "epcsaft_neutral_jou_parity_metrics.csv"))
    summary = pd.read_csv(require(PROCESSED_DIR / "epcsaft_neutral_jou_parity_summary.csv"))
    curves = pd.read_csv(require(PROCESSED_DIR / "epcsaft_neutral_jou_parity_curves.csv"))
    metrics.to_csv(OUT_DIR / "epcsaft_neutral_jou_parity_metrics.csv", index=False)
    summary.to_csv(OUT_DIR / "epcsaft_neutral_jou_parity_summary.csv", index=False)
    curves.to_csv(OUT_DIR / "epcsaft_neutral_jou_parity_curves.csv", index=False)

    title = "Neutral ePC-SAFT parity against legacy PC-SAFT pressure curves"
    description = "Neutral ePC-SAFT and legacy PC-SAFT pressure curves are compared against Jou et al. 30 wt% MEA carbon-dioxide partial-pressure data using a shared temperature palette."
    fig, ax = plt.subplots(figsize=PRESSURE_FIGSIZE)
    for temperature_C in JOU_TEMPERATURES_C:
        color = temperature_color(temperature_C)
        t_data = metrics[metrics["temperature_C"] == temperature_C].sort_values("CO2_loading")
        t_curve = curves[curves["temperature_C"] == temperature_C].sort_values("CO2_loading")
        if t_data.empty or t_curve.empty:
            continue
        ax.plot(t_data["CO2_loading"], t_data["observed_CO2_pressure_kPa"], linestyle="none", marker=JOU_DATA_MARKER, markersize=JOU_DATA_MARKERSIZE, color=color, alpha=0.9, label=f"{temperature_C} C Jou data")
        ax.plot(t_curve["CO2_loading"], t_curve["legacy_pcsaft_CO2_pressure_kPa"], LEGACY_PCSAFT_LINESTYLE, color=color, alpha=0.65, linewidth=REFERENCE_LINEWIDTH, label=f"{temperature_C} C legacy PC-SAFT")
        ax.plot(t_curve["CO2_loading"], t_curve["epcsaft_CO2_pressure_kPa"], EPCSAFT_NEUTRAL_LINESTYLE, color=color, linewidth=MODEL_LINEWIDTH, label=f"{temperature_C} C ePC-SAFT neutral")
    apply_pressure_axes(ax, title=title)
    ax.legend(ncol=2, title="Temperature and role")
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(fig, OUT_DIR / "epcsaft_neutral_pcsaft_parity")
    plt.close(fig)
    write_mpl_sidecar(
        OUT_DIR / "epcsaft_neutral_pcsaft_parity.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
    )
    summary_json = {
        "dataset_dir": str(DATASET_DIR),
        "metrics": str(OUT_DIR / "epcsaft_neutral_jou_parity_metrics.csv"),
        "summary": str(OUT_DIR / "epcsaft_neutral_jou_parity_summary.csv"),
        "curves": str(OUT_DIR / "epcsaft_neutral_jou_parity_curves.csv"),
        "plot": str(png),
    }
    (OUT_DIR / "epcsaft_neutral_jou_parity_summary.json").write_text(json.dumps(summary_json, indent=2) + "\n", encoding="utf-8")
    print(f"Neutral ePC-SAFT pressure plot: {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
