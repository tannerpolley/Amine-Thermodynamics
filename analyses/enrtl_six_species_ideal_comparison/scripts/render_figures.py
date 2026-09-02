from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.analysis_io import file_sha256, normalize_svg, repo_relative_path  # noqa: E402
from MEA.common.plot_style import (  # noqa: E402
    MODEL_LINEWIDTH,
    apply_plot_theme,
    finish_axes,
    save_figure_bundle,
    species_color,
    species_label,
    write_mpl_sidecar,
)

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ANALYSIS_DIR / "results"
OUTPUT_DIR = ANALYSIS_DIR / "figures" / "output"
COMMON_SPECIES = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-")
OMITTED_SPECIES = ("CO3^2-", "H3O+", "OH-")


def _read(name: str) -> pd.DataFrame:
    path = RESULTS_DIR / name
    if not path.is_file():
        raise RuntimeError(f"Missing retained input {path}; run generate_data.py first")
    return pd.read_csv(path)


def _save(fig: plt.Figure, stem: str, *, title: str, description: str, data: pd.DataFrame) -> None:
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
        style_source="analyses/enrtl_six_species_ideal_comparison/scripts/render_figures.py",
    )
    plt.close(fig)


def _common_delta_figure() -> None:
    ideal = _read("common_species_comparison.csv")
    ideal = ideal[ideal["species"].isin(COMMON_SPECIES)].copy()
    ideal["lane"] = "ideal canonical states"
    ideal["x"] = ideal["CO2_loading"]
    ideal["delta"] = ideal["nine_minus_six_amount_per_mol_initial_MEA"]
    ideal["temperature"] = ideal["temperature_C"]

    epcsaft = _read("epcsaft_scipy_comparison.csv")
    epcsaft = epcsaft[epcsaft["species"].isin(COMMON_SPECIES)].copy()
    epcsaft["lane"] = "ePC-SAFT fixed-T,P states"
    epcsaft["x"] = epcsaft["temperature_K"] - 273.15
    epcsaft["delta"] = epcsaft["nine_minus_six_amount_per_mol_initial_MEA"]
    epcsaft["temperature"] = epcsaft["temperature_K"] - 273.15
    plot_data = pd.concat(
        [
            ideal[["lane", "state_family", "source", "temperature", "x", "species", "delta"]],
            epcsaft.assign(state_family="fixed_TP", source="installed Engine wheel")[["lane", "state_family", "source", "temperature", "x", "species", "delta"]],
        ],
        ignore_index=True,
    )

    apply_plot_theme()
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.4), sharey=True)
    for species in COMMON_SPECIES:
        color = species_color(species)
        subset = ideal[ideal["species"] == species]
        axes[0].scatter(subset["x"], subset["delta"], s=12, alpha=0.28, color=color)
        subset = epcsaft[epcsaft["species"] == species].sort_values("x")
        axes[1].plot(subset["x"], subset["delta"], marker="o", markersize=4.5, linewidth=MODEL_LINEWIDTH, color=color)
    for ax in axes:
        ax.axhline(0.0, color="0.25", linewidth=0.9)
        ax.set_yscale("symlog", linthresh=1.0e-6)
        ax.set_ylabel("nine-species minus six-species amount\nper mol initial MEA")
        finish_axes(ax)
    axes[0].set_xlabel("$CO_2$ loading, mol $CO_2$/mol initial MEA")
    axes[0].set_title("Ideal canonical states")
    axes[1].set_xlabel("Temperature, °C; fixed at 100 kPa")
    axes[1].set_title("ePC-SAFT liquid, fixed-$T,P$")
    axes[0].set_xlim(left=0.0)
    axes[1].set_xlim(left=15.0, right=55.0)
    axes[1].legend(
        handles=[Line2D([0], [0], color=species_color(s), linewidth=MODEL_LINEWIDTH, label=species_label(s)) for s in COMMON_SPECIES],
        title="Common species",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
    )
    fig.suptitle("Matched species-set effect on common species", y=1.02)
    fig.tight_layout()
    _save(
        fig,
        "matched_common_species_delta",
        title="Matched species-set effect on common species",
        description="Nine-species minus six-species amounts for the common species. The ideal panel contains all canonical VLE and ChEq coordinates; the ePC-SAFT panel contains fixed-100-kPa states solved by the disposable SciPy bridge.",
        data=plot_data,
    )


def _omitted_inventory_figure() -> None:
    ideal = _read("omitted_species_inventory.csv").copy()
    ideal["lane"] = "ideal canonical states"
    ideal["x"] = ideal["CO2_loading"]
    ideal["total"] = ideal["omitted_total_amount_per_mol_initial_MEA"]
    epcsaft = _read("epcsaft_scipy_omitted_inventory.csv").copy()
    epcsaft["lane"] = "ePC-SAFT fixed-T,P states"
    epcsaft["x"] = epcsaft["temperature_K"] - 273.15
    epcsaft["total"] = epcsaft["omitted_total_amount_per_mol_initial_MEA"]
    plot_data = pd.concat(
        [
            ideal.assign(temperature=ideal["temperature_C"])[["lane", "state_family", "source", "temperature", "x", *OMITTED_SPECIES, "total"]],
            epcsaft.assign(state_family="fixed_TP", source="installed Engine wheel", temperature=epcsaft["temperature_K"] - 273.15)[["lane", "state_family", "source", "temperature", "x", *OMITTED_SPECIES, "total"]],
        ],
        ignore_index=True,
    )

    apply_plot_theme()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2))
    temperature_norm = plt.Normalize(float(ideal["temperature_C"].min()), float(ideal["temperature_C"].max()))
    for family, marker in (("vle", "o"), ("speciation", "s")):
        subset = ideal[ideal["state_family"] == family]
        axes[0].scatter(subset["x"], subset["total"], c=subset["temperature_C"], cmap="viridis", norm=temperature_norm, marker=marker, s=20, alpha=0.65, label=family)
    axes[0].set_xlabel("$CO_2$ loading, mol $CO_2$/mol initial MEA")
    axes[0].set_ylabel("Omitted inventory per mol initial MEA")
    axes[0].set_title("Ideal canonical states")
    axes[0].legend(title="State family")
    for species in OMITTED_SPECIES:
        axes[1].plot(epcsaft["x"], epcsaft[species], marker="o", linewidth=1.7, color=species_color(species), label=species_label(species))
    axes[1].plot(epcsaft["x"], epcsaft["total"], "k--", linewidth=MODEL_LINEWIDTH, label="total")
    axes[1].set_xlabel("Temperature, °C; fixed at 100 kPa")
    axes[1].set_ylabel("Amount per mol initial MEA")
    axes[1].set_title("ePC-SAFT fixed-$T,P$ states")
    axes[1].legend()
    for ax in axes:
        ax.set_yscale("log")
        finish_axes(ax)
    fig.suptitle("Inventory excluded by the six-species set", y=1.02)
    fig.tight_layout()
    _save(
        fig,
        "matched_omitted_inventory",
        title="Inventory excluded by the six-species set",
        description="The omitted inventory is the nine-species amount of carbonate, hydronium, and hydroxide. It is an inventory diagnostic, not a causal decomposition of pressure or speciation error.",
        data=plot_data,
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _common_delta_figure()
    _omitted_inventory_figure()
    inputs = [
        "common_species_comparison.csv",
        "omitted_species_inventory.csv",
        "epcsaft_scipy_comparison.csv",
        "epcsaft_scipy_omitted_inventory.csv",
    ]
    pd.DataFrame(
        {"artifact": [repo_relative_path(RESULTS_DIR / name) for name in inputs], "sha256": [file_sha256(RESULTS_DIR / name) for name in inputs]}
    ).to_csv(OUTPUT_DIR / "source_manifest.csv", index=False, lineterminator="\n")
    print(f"Rendered matched comparison figures under {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
