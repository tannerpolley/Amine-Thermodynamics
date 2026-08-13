from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

from MEA.common.plot_style import finish_axes, save_figure_bundle, write_mpl_sidecar


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
RESULTS = ANALYSIS / "results"
PACKET = RESULTS / "pressure_candidate_packet.csv"
SCREEN = RESULTS / "fixed_pressure_fugacity_screen_predictions.csv"
FIGURES = RESULTS / "figures"
PLOT_DATA = FIGURES / "pco2_closure_diagnostic_plot_data.csv"
FIGURE_STEM = FIGURES / "pco2_closure_diagnostic"
BUBBLE_TABLE = FIGURES / "reactive_bubble_pressure_plot_data.csv"
BUBBLE_FIGURE_STEM = FIGURES / "reactive_bubble_pressure_diagnostic"

SOURCE_ORDER = ("Hilliard2008", "Jou1995", "Xu2011")
SOURCE_LABELS = {
    "Hilliard2008": "Hilliard (2008)",
    "Jou1995": "Jou et al. (1995)",
    "Xu2011": "Xu et al. (2011)",
}
MARKERS = ("o", "s", "^", "D", "P", "v")


def _build_plot_data() -> pd.DataFrame:
    packet = pd.read_csv(PACKET)
    packet = packet.loc[packet["analysis_role"] != "reserved"].copy()
    screen = pd.read_csv(SCREEN)
    modeled = screen[
        [
            "observation_id",
            "modeled_quantity",
            "modeled_quantity_unit",
            "modeled_liquid_co2_fugacity_pa",
            "closure_residual_log10_fugacity_over_observed_pco2",
            "pressure_prediction_status",
            "claim_status",
        ]
    ]
    frame = packet.merge(
        modeled, on="observation_id", how="left", validate="one_to_one"
    )
    frame["observed_pco2_kpa"] = frame["observed_pco2_pa"] / 1000.0
    frame["temperature_C"] = frame["temperature_K"] - 273.15
    frame["observed_pressure_plot_role"] = (
        "experimental_inventory_observed_pco2_not_model_prediction"
    )
    frame["model_curve_status"] = "not_available_coupled_pressure_closure_timed_out"
    frame["reserved_policy"] = "eight reserved rows withheld from plot"
    frame.to_csv(PLOT_DATA, index=False, lineterminator="\n")
    return frame


def _group_label(group: pd.DataFrame) -> str:
    return (
        f"{float(group['temperature_C'].iloc[0]):g} °C, "
        f"{100.0 * float(group['mea_mass_fraction'].iloc[0]):g} wt% MEA"
    )


def _plot_source(ax: object, frame: pd.DataFrame, source: str) -> None:
    subset = frame.loc[frame["source_key"] == source]
    groups = list(subset.groupby(["temperature_C", "mea_mass_fraction"], sort=True))
    colors = plt.get_cmap("viridis")
    for index, (_, group) in enumerate(groups):
        color = colors(index / max(1, len(groups) - 1))
        ax.scatter(
            group["co2_loading_mol_per_mol_mea"],
            group["observed_pco2_kpa"],
            color=color,
            edgecolor="black",
            linewidth=0.35,
            marker=MARKERS[index % len(MARKERS)],
            s=28,
            label=_group_label(group),
        )
    ax.set_yscale("log")
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("Observed $P_{CO_2}$, kPa")
    finish_axes(ax, title=SOURCE_LABELS[source])
    ax.legend(fontsize=6.2, ncol=2 if len(groups) > 6 else 1)


def _plot_closure(ax: object, frame: pd.DataFrame) -> None:
    closure = frame.loc[frame["modeled_liquid_co2_fugacity_pa"].notna()].copy()
    ax.scatter(
        closure["observed_pco2_kpa"],
        closure["closure_residual_log10_fugacity_over_observed_pco2"],
        color="#b6312c",
        edgecolor="black",
        linewidth=0.45,
        s=42,
    )
    ax.axhline(0.0, color="black", linestyle=":", linewidth=1.0)
    ax.set_xscale("log")
    ax.set_xlabel("Observed $P_{CO_2}$ supplied to closure screen, kPa")
    ax.set_ylabel("$\\log_{10}(f_{CO_2}^{liq}/P_{CO_2}^{obs})$")
    finish_axes(ax, title="Fixed-pressure ideal-vapor closure screen")
    note = Line2D(
        [],
        [],
        linestyle="none",
        marker="o",
        color="#b6312c",
        label=(
            "Unfitted M0 origin; $P^{obs}$ is a model input; "
            "no predicted-pressure curve"
        ),
    )
    ax.legend(handles=[note], fontsize=7.2)


def _render_reactive_bubble_diagnostic() -> tuple[Path, Path, Path]:
    frame = pd.read_csv(BUBBLE_TABLE)
    evaluated = frame.loc[frame["status"] == "evaluated_diagnostic"].copy()
    if evaluated.empty:
        raise RuntimeError("reactive bubble diagnostic contains no evaluated rows")
    evaluated = evaluated.sort_values("loading_mol_co2_per_mol_mea")
    evaluated["observed_pco2_kpa"] = evaluated["observed_pco2_pa"] / 1000.0
    evaluated["predicted_pco2_kpa"] = evaluated["predicted_pco2_pa"] / 1000.0

    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    ax.scatter(
        evaluated["loading_mol_co2_per_mol_mea"],
        evaluated["observed_pco2_kpa"],
        color="#28659c",
        edgecolor="black",
        linewidth=0.45,
        s=48,
        label="Hilliard (2008) experiment",
        zorder=3,
    )
    ax.plot(
        evaluated["loading_mol_co2_per_mol_mea"],
        evaluated["predicted_pco2_kpa"],
        color="#b6312c",
        marker="s",
        markersize=4.5,
        linewidth=1.6,
        label="Exact reactive-bubble diagnostic",
    )
    ax.set_yscale("log")
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("$P_{CO_2}$, kPa")
    finish_axes(
        ax,
        title="17 wt% MEA, 40 °C — diagnostic / non-promotable",
    )
    ax.legend(fontsize=8.0)
    fig.suptitle(
        "Declared one-liquid/one-vapor reactive ePC-SAFT pressure closure\n"
        "Liquid branch is certified once; the bubble owner solves only vapor and pressure",
        fontsize=11.5,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.91))
    png, svg, pdf = save_figure_bundle(fig, BUBBLE_FIGURE_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        BUBBLE_FIGURE_STEM.with_suffix(".mpl.yaml"),
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="Diagnostic exact reactive-bubble PCO2 comparison",
        description=(
            "Measured and exact reactive-bubble predicted CO2 partial pressure for the "
            "Hilliard 17 wt% MEA, 40 C subset. The parameter came from the fixed-pressure "
            "screening lane, so the curve is diagnostic and non-promotable. Phase count "
            "and roles are declared; no liquid phase is rediscovered."
        ),
        data_path=BUBBLE_TABLE,
        style_source=str(Path(__file__).relative_to(ROOT)),
    )
    return png, svg, pdf


def main() -> None:
    missing = [path for path in (PACKET, SCREEN) if not path.exists()]
    if missing:
        joined = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise FileNotFoundError(f"generate diagnostic data before rendering: {joined}")
    FIGURES.mkdir(parents=True, exist_ok=True)
    frame = _build_plot_data()
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 9.5))
    for ax, source in zip(axes.flat[:3], SOURCE_ORDER, strict=True):
        _plot_source(ax, frame, source)
    _plot_closure(axes.flat[3], frame)
    fig.suptitle(
        "MEA–$CO_2$ non-reserved pressure inventory and closure diagnostic\n"
        "Observed pressure is input to the model; coupled predictive pressure did not complete",
        fontsize=14,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
    png, svg, pdf = save_figure_bundle(fig, FIGURE_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        FIGURE_STEM.with_suffix(".mpl.yaml"),
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="MEA-CO2 observed-pressure inventory and fixed-pressure closure diagnostic",
        description=(
            "The 113 non-reserved source-resolved observed CO2-pressure rows are shown "
            "by source, temperature, and MEA concentration; eight reserved rows remain "
            "withheld. The fourth panel contains only one exact "
            "fixed-pressure ideal-vapor liquid-fugacity closure residuals. Observed total pressure "
            "is an input and no predicted-pressure curve is claimed."
        ),
        data_path=PLOT_DATA,
        style_source=str(Path(__file__).relative_to(ROOT)),
    )
    print(png.relative_to(ROOT))
    print(svg.relative_to(ROOT))
    print(pdf.relative_to(ROOT))
    print(PLOT_DATA.relative_to(ROOT))
    if BUBBLE_TABLE.exists():
        for path in _render_reactive_bubble_diagnostic():
            print(path.relative_to(ROOT))
        print(BUBBLE_TABLE.relative_to(ROOT))


if __name__ == "__main__":
    main()
