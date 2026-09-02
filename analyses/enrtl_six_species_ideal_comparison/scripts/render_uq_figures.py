"""Render claim-led figures from the retained all-parameter UQ tables."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.analysis_io import file_sha256, normalize_svg, repo_relative_path  # noqa: E402
from MEA.common.plot_style import (  # noqa: E402
    apply_plot_theme,
    finish_axes,
    save_figure_bundle,
    write_mpl_sidecar,
)

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ANALYSIS_DIR / "results"
OUTPUT_DIR = ANALYSIS_DIR / "figures" / "output"


def read(name: str) -> pd.DataFrame:
    path = RESULTS_DIR / name
    if not path.is_file():
        raise RuntimeError(f"Missing retained UQ table: {path}")
    return pd.read_csv(path)


def label(identity: str) -> str:
    parts = identity.split("/")
    if parts[0] == "component" and len(parts) >= 3:
        return f"{parts[1]}: {parts[-1]}"
    if parts[0] == "pair" and len(parts) >= 4:
        return f"{parts[1]}–{parts[2]} k$_{{ij}}$"
    if parts[0] == "reaction:" and len(parts) >= 3:
        return identity
    if identity.startswith("reaction:"):
        return identity.removeprefix("reaction:").replace(":correlation:", " ")
    if parts[0] == "association" and len(parts) >= 6:
        return f"{parts[1]}/{parts[3]} {parts[-1]}"
    return identity


def save(fig: plt.Figure, stem: str, title: str, description: str, data: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data_path = OUTPUT_DIR / f"{stem}_plot_data.csv"
    data.to_csv(data_path, index=False, lineterminator="\n")
    png, svg, pdf = save_figure_bundle(fig, OUTPUT_DIR / stem)
    normalize_svg(svg)
    write_mpl_sidecar(
        OUTPUT_DIR / f"{stem}.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=data_path,
        style_source="analyses/enrtl_six_species_ideal_comparison/scripts/render_uq_figures.py",
    )
    plt.close(fig)


def global_importance() -> None:
    source = read("uq_global_sensitivity.csv")
    outputs = [
        ("log10_fugacity_co2_kpa", "$\\log_{10} f_{CO_2}$ (kPa)"),
        ("density_mol_m3", "liquid density (mol m$^{-3}$)"),
        ("log10_amount_meah", "$\\log_{10} n_{MEAH^+}$"),
        ("log10_amount_meacoo", "$\\log_{10} n_{MEACOO^-}$"),
    ]
    apply_plot_theme()
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 10.0))
    plotted = []
    for ax, (output, title) in zip(axes.flat, outputs, strict=True):
        subset = source[source["output"] == output].copy()
        subset = subset.sort_values("absolute_importance", ascending=False).head(10).sort_values("prcc_ridge")
        subset["label"] = subset["parameter_identities"].map(label)
        colors = plt.get_cmap("tab20")(np.linspace(0.02, 0.92, len(subset)))
        ax.barh(subset["label"], subset["prcc_ridge"], color=colors, alpha=0.85)
        ax.axvline(0.0, color="0.2", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel("ridge-PRCC; sign gives response direction")
        ax.tick_params(axis="y", labelsize=8)
        finish_axes(ax)
        plotted.append(subset.assign(plot_output=output))
    fig.suptitle("Top all-parameter global sensitivity drivers", y=1.01)
    fig.tight_layout()
    save(
        fig,
        "uq_global_importance",
        "Top all-parameter global sensitivity drivers",
        "Top ten parameter groups by absolute ridge-PRCC for four central-state Engine outputs. The 128-point scrambled Latin-hypercube input ranges are screening priors, not a measurement-backed posterior.",
        pd.concat(plotted, ignore_index=True),
    )


def binary_interactions() -> None:
    source = read("uq_global_sensitivity.csv")
    source = source[source["family"].isin(["k_ij", "k_ij_reciprocal_temperature_slope"])].copy()
    source["label"] = source["parameter_identities"].map(label)
    source["plot_output"] = source["output"]
    top = source.assign(abs_rank=source["absolute_importance"]).sort_values("abs_rank", ascending=False).head(8)
    palette = {
        "log10_fugacity_co2_kpa": "#0072B2",
        "density_mol_m3": "#D55E00",
        "log10_amount_meah": "#009E73",
        "log10_amount_meacoo": "#CC79A7",
        "log10_amount_co3": "#E69F00",
    }
    apply_plot_theme()
    fig, ax = plt.subplots(figsize=(12.5, 6.8))
    for output, group in source.groupby("output"):
        ax.scatter(group["spearman_rho"], group["absolute_importance"], s=34, alpha=0.7, color=palette.get(output, "#444444"), label=output)
    for _, row in top.iterrows():
        ax.annotate(row["label"], (row["spearman_rho"], row["absolute_importance"]), xytext=(4, 4), textcoords="offset points", fontsize=7)
    ax.set_xlabel("Spearman rank correlation")
    ax.set_ylabel("absolute ridge-PRCC")
    ax.set_title("Binary-interaction parameter sensitivity")
    ax.legend(title="Output", fontsize=8)
    finish_axes(ax)
    fig.tight_layout()
    save(
        fig,
        "uq_binary_interaction_sensitivity",
        "Binary-interaction parameter sensitivity",
        "All included binary k_ij groups in the global screening survey. Several binary interactions enter the highest-importance set for speciation or density; same-sign ion pairs excluded by the installed ionic topology are not sampled.",
        source,
    )


def uncertainty_intervals() -> None:
    source = read("uq_uncertainty_summary.csv").copy()
    labels = {
        "log10_fugacity_co2_kpa": "$\\log_{10} f_{CO_2}$",
        "density_mol_m3": "density",
        "log10_amount_meah": "$\\log_{10} n_{MEAH^+}$",
        "log10_amount_meacoo": "$\\log_{10} n_{MEACOO^-}$",
        "log10_amount_co3": "$\\log_{10} n_{CO_3^{2-}}$",
    }
    apply_plot_theme()
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.8))
    for ax, subset in zip(axes, [source[source["output"].str.startswith("log10_")], source[source["output"] == "density_mol_m3"]], strict=True):
        subset = subset.copy()
        subset["label"] = subset["output"].map(labels)
        if len(subset) == 1:
            y = np.array([0.0])
        else:
            y = np.arange(len(subset))
        for yi, (_, row) in zip(y, subset.iterrows(), strict=True):
            ax.plot([row["q_0_025"], row["q_0_975"]], [yi, yi], color="#0072B2", linewidth=3.0)
            ax.plot(row["q_0_500"], yi, "o", color="#D55E00", markersize=6)
            ax.plot(row["baseline"], yi, "x", color="0.15", markersize=7, mew=1.6)
        ax.set_yticks(y, subset["label"])
        ax.set_xlabel("screening-prior output value")
        ax.set_title("log outputs" if len(subset) > 1 else "density (mol m$^{-3}$)")
        ax.legend([Line2D([], [], color="#0072B2", linewidth=3), Line2D([], [], marker="o", color="#D55E00", linestyle="None"), Line2D([], [], marker="x", color="0.15", linestyle="None")], ["2.5–97.5%", "median", "baseline"], fontsize=8)
        finish_axes(ax)
    fig.suptitle("Screening-prior propagated output uncertainty", y=1.01)
    fig.tight_layout()
    save(
        fig,
        "uq_output_uncertainty",
        "Screening-prior propagated output uncertainty",
        "Median and 2.5–97.5 percentile ranges from valid central-state LHC samples. Intervals quantify the declared screening prior only; they are not experimental confidence or posterior credible intervals.",
        source,
    )


def main() -> int:
    global_importance()
    binary_interactions()
    uncertainty_intervals()
    inputs = ["uq_parameter_inventory.csv", "uq_lhc_samples.csv", "uq_global_sensitivity.csv", "uq_uncertainty_summary.csv"]
    pd.DataFrame({"artifact": [repo_relative_path(RESULTS_DIR / name) for name in inputs], "sha256": [file_sha256(RESULTS_DIR / name) for name in inputs]}).to_csv(OUTPUT_DIR / "uq_source_manifest.csv", index=False, lineterminator="\n")
    print(f"Rendered UQ figures under {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
