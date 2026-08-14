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
LADDER_TABLE = FIGURES / "pressure_block_ladder_plot_data.csv"
LADDER_FIGURE_STEM = FIGURES / "pressure_block_ladder_diagnostic"
BINARY_INPUT = RESULTS / "cai_mea_water_binary_predictions.csv"
BINARY_TABLE = FIGURES / "cai_mea_water_binary_plot_data.csv"
BINARY_FIGURE_STEM = FIGURES / "cai_mea_water_binary_diagnostic"
BAYGI_BINARY_INPUTS = {
    "Baygi 3B/2B": RESULTS / "cai_baygi_3b2b_binary_predictions.csv",
    "Baygi 3B/4C": RESULTS / "cai_baygi_3b4c_binary_predictions.csv",
}
BAYGI_BINARY_TABLE = FIGURES / "cai_baygi_binary_model_comparison_plot_data.csv"
BAYGI_BINARY_FIGURE_STEM = FIGURES / "cai_baygi_binary_model_comparison_diagnostic"

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


def _render_pressure_block_ladder() -> tuple[Path, Path, Path]:
    frame = pd.read_csv(LADDER_TABLE)
    if set(frame["analysis_role"]) != {"training"}:
        raise RuntimeError("pressure block ladder plot may contain training rows only")
    models = {
        "M0": ("#28659c", "s", "M0 exact origin"),
        "M1": ("#b6312c", "^", "M1 exact source-fixed origin"),
    }
    fig, (pressure_ax, residual_ax) = plt.subplots(1, 2, figsize=(11.2, 4.8))
    observations = frame.loc[frame["model"] == "M0"].sort_values(
        "loading_mol_co2_per_mol_mea"
    )
    pressure_ax.scatter(
        observations["loading_mol_co2_per_mol_mea"],
        observations["observed_pco2_pa"] / 1000.0,
        color="white",
        edgecolor="black",
        linewidth=0.8,
        s=48,
        label="Hilliard (2008) experiment",
        zorder=4,
    )
    for model, (color, marker, label) in models.items():
        subset = frame.loc[frame["model"] == model].sort_values(
            "loading_mol_co2_per_mol_mea"
        )
        pressure_ax.plot(
            subset["loading_mol_co2_per_mol_mea"],
            subset["predicted_pco2_pa"] / 1000.0,
            color=color,
            marker=marker,
            linewidth=1.5,
            markersize=4.5,
            label=label,
        )
        residual_ax.plot(
            subset["loading_mol_co2_per_mol_mea"],
            subset["residual_log10"],
            color=color,
            marker=marker,
            linewidth=1.5,
            markersize=4.5,
            label=label,
        )
    pressure_ax.set_yscale("log")
    pressure_ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    pressure_ax.set_ylabel("$P_{CO_2}$, kPa")
    finish_axes(pressure_ax, title="Exact reactive-bubble pressure roots")
    pressure_ax.legend(fontsize=7.5)
    residual_ax.axhline(0.0, color="black", linestyle=":", linewidth=1.0)
    residual_ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    residual_ax.set_ylabel("$\\log_{10}(P_{CO_2}^{model}/P_{CO_2}^{obs})$")
    finish_axes(residual_ax, title="Loading-dependent pressure residual")
    residual_ax.legend(fontsize=7.5)
    fig.suptitle(
        "17 wt% MEA, 40 °C — bounded M0/M1 direction screen\n"
        "Exact origins only; linearized candidates are not plotted as predictions",
        fontsize=11.5,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.90))
    png, svg, pdf = save_figure_bundle(fig, LADDER_FIGURE_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        LADDER_FIGURE_STEM.with_suffix(".mpl.yaml"),
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="Diagnostic exact reactive-bubble M0/M1 pressure screen",
        description=(
            "Experimental and exact independently rooted reactive-bubble CO2 partial "
            "pressures for the Hilliard 17 wt% MEA, 40 C training subset. M0 uses the "
            "current nonpolar diagnostic origin; M1 uses the source-fixed Gross 2005 "
            "CO2 quadrupolar origin. No linearized parameter candidate is presented as "
            "an exact pressure prediction. Both models are diagnostic and non-promotable; "
            "model-selection and reserved campaigns remain unevaluated."
        ),
        data_path=LADDER_TABLE,
        style_source=str(Path(__file__).relative_to(ROOT)),
    )
    return png, svg, pdf


def _render_cai_binary_diagnostic() -> tuple[Path, Path, Path]:
    frame = pd.read_csv(BINARY_INPUT)
    if set(frame["fit_role"]) != {"binary_training"}:
        raise RuntimeError(
            "Cai diagnostic plot may contain admitted training rows only"
        )
    frame.to_csv(BINARY_TABLE, index=False, lineterminator="\n")
    component_titles = {
        "monoethanolamine": "MEA fugacity closure",
        "water": "Water fugacity closure",
    }
    state_styles = {
        "retained_origin": ("#666666", "--", "o", "retained origin"),
        "fitted_diagnostic": ("#28659c", "-", "s", "fitted diagnostic"),
    }
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6), sharex=True)
    for ax, component in zip(axes, component_titles, strict=True):
        component_frame = frame.loc[frame["component_id"] == component]
        for state, (color, line_style, marker, label) in state_styles.items():
            subset = component_frame.loc[
                component_frame["parameter_state"] == state
            ].sort_values("water_liquid_mole_fraction")
            parameter = float(subset["k_ij_mea_water"].iloc[0])
            ax.plot(
                subset["water_liquid_mole_fraction"],
                subset["normalized_residual"],
                color=color,
                linestyle=line_style,
                marker=marker,
                linewidth=1.5,
                markersize=5,
                label=f"{label}, $k_{{ij}}={parameter:.5f}$",
            )
        ax.axhline(0.0, color="black", linestyle=":", linewidth=1.0)
        ax.set_xlabel("Liquid water mole fraction")
        ax.set_ylabel("Normalized log-fugacity closure residual")
        finish_axes(ax, title=component_titles[component])
        ax.legend(fontsize=7.3)
    fig.suptitle(
        "Cai (1996) MEA–water binary qualification diagnostic\n"
        "66.66 kPa admitted subset; measured $T$, $P$, $x$, and $y$ are inputs",
        fontsize=11.5,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.90))
    png, svg, pdf = save_figure_bundle(fig, BINARY_FIGURE_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        BINARY_FIGURE_STEM.with_suffix(".mpl.yaml"),
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="Diagnostic Cai MEA-water binary fugacity closure",
        description=(
            "Exact liquid/vapor fixed-pressure component fugacity-closure residuals "
            "for the three Cai 1996 internal rows inside the current Held-water "
            "source domain. The fitted neutral interaction is identifiable and "
            "multistart-consistent but fails residual-trend and held-out-pressure-level "
            "qualification gates. It is diagnostic and non-promotable."
        ),
        data_path=BINARY_TABLE,
        style_source=str(Path(__file__).relative_to(ROOT)),
    )
    return png, svg, pdf


def _render_baygi_binary_comparison() -> tuple[Path, Path, Path]:
    frames: list[pd.DataFrame] = []
    for model, path in BAYGI_BINARY_INPUTS.items():
        frame = pd.read_csv(path)
        frame = frame.loc[frame["parameter_state"] == "fitted_diagnostic"].copy()
        frame["model"] = model
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(BAYGI_BINARY_TABLE, index=False, lineterminator="\n")
    components = ("monoethanolamine", "water")
    titles = {"monoethanolamine": "MEA closure", "water": "Water closure"}
    role_styles = {
        "binary_training": ("#28659c", "o", "101.33 kPa training"),
        "binary_model_selection": ("#b6312c", "^", "66.66 kPa held-out"),
    }
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 8.1), sharex=True)
    for row_index, model in enumerate(BAYGI_BINARY_INPUTS):
        for column_index, component in enumerate(components):
            ax = axes[row_index, column_index]
            subset = combined.loc[
                (combined["model"] == model) & (combined["component_id"] == component)
            ]
            for role, (color, marker, label) in role_styles.items():
                role_rows = subset.loc[subset["fit_role"] == role].sort_values(
                    "water_liquid_mole_fraction"
                )
                ax.plot(
                    role_rows["water_liquid_mole_fraction"],
                    role_rows["normalized_residual"],
                    color=color,
                    marker=marker,
                    linewidth=1.2,
                    markersize=4.5,
                    label=label,
                )
            parameter = float(subset["k_ij_mea_water"].iloc[0])
            ax.axhline(0.0, color="black", linestyle=":", linewidth=1.0)
            ax.set_xlabel("Liquid water mole fraction")
            ax.set_ylabel("Normalized log-fugacity closure")
            finish_axes(
                ax, title=f"{model}: {titles[component]}, $k_{{ij}}={parameter:.5f}$"
            )
            ax.legend(fontsize=6.8)
    fig.suptitle(
        "Cai (1996) source-consistent Baygi binary diagnostics — non-promotable\n"
        "Measured $T$, $P$, $x$, and $y$ are inputs; no Bubble-T/Dew-T prediction is claimed",
        fontsize=11.5,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.92))
    png, svg, pdf = save_figure_bundle(fig, BAYGI_BINARY_FIGURE_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        BAYGI_BINARY_FIGURE_STEM.with_suffix(".mpl.yaml"),
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="Diagnostic Cai Baygi binary-model fugacity closure comparison",
        description=(
            "Exact declared-liquid/declared-vapor fixed-state closure residuals for "
            "Baygi's 3B-MEA/2B-water and 3B-MEA/4C-water parameterizations. Both "
            "complete Cai pressure levels are shown. The fits are identifiable and "
            "multistart-consistent but fail source-scale residual and trend gates; "
            "Baygi's Bubble-T/Dew-T Eq. 12 objective is not claimed."
        ),
        data_path=BAYGI_BINARY_TABLE,
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
    if LADDER_TABLE.exists():
        for path in _render_pressure_block_ladder():
            print(path.relative_to(ROOT))
        print(LADDER_TABLE.relative_to(ROOT))
    if BINARY_INPUT.exists():
        for path in _render_cai_binary_diagnostic():
            print(path.relative_to(ROOT))
        print(BINARY_TABLE.relative_to(ROOT))
    if all(path.exists() for path in BAYGI_BINARY_INPUTS.values()):
        for path in _render_baygi_binary_comparison():
            print(path.relative_to(ROOT))
        print(BAYGI_BINARY_TABLE.relative_to(ROOT))


if __name__ == "__main__":
    main()
