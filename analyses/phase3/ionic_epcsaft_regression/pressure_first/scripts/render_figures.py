from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from MEA.common.plot_style import finish_axes, save_figure_bundle, write_mpl_sidecar


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
RESULTS = ANALYSIS / "results"
FIGURES = RESULTS / "figures"
LADDER_TABLE = FIGURES / "pressure_block_ladder_plot_data.csv"
LADDER_STEM = FIGURES / "pressure_block_ladder_diagnostic"
BINARY_INPUTS = {
    "Baygi 3B/2B": RESULTS / "cai_baygi_3b2b_binary_predictions.csv",
    "Baygi 3B/4C": RESULTS / "cai_baygi_3b4c_binary_predictions.csv",
}
BINARY_TABLE = FIGURES / "cai_baygi_binary_model_comparison_plot_data.csv"
BINARY_STEM = FIGURES / "cai_baygi_binary_model_comparison_diagnostic"


def _render_pressure_models() -> tuple[Path, Path, Path]:
    frame = pd.read_csv(LADDER_TABLE)
    if set(frame["analysis_role"]) != {"training"}:
        raise RuntimeError("pressure plot may contain training rows only")
    styles = {
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
    for model, (color, marker, label) in styles.items():
        subset = frame.loc[frame["model"] == model].sort_values(
            "loading_mol_co2_per_mol_mea"
        )
        x = subset["loading_mol_co2_per_mol_mea"]
        pressure_ax.plot(
            x,
            subset["predicted_pco2_pa"] / 1000.0,
            color=color,
            marker=marker,
            linewidth=1.5,
            markersize=4.5,
            label=label,
        )
        residual_ax.plot(
            x,
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
        "17 wt% MEA, 40 °C — diagnostic M0/M1 screen\n"
        "Exact origins only; no fitted pressure curve is promoted",
        fontsize=11.5,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.90))
    paths = save_figure_bundle(fig, LADDER_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        LADDER_STEM.with_suffix(".mpl.yaml"),
        png_name=paths[0].name,
        svg_name=paths[1].name,
        pdf_name=paths[2].name,
        title="Diagnostic exact reactive-bubble M0/M1 pressure screen",
        description=(
            "Experimental and exact independently rooted reactive-bubble CO2 partial "
            "pressures for the Hilliard 17 wt% MEA, 40 C training subset. Both "
            "models are diagnostic and non-promotable; reserved data remain unused."
        ),
        data_path=LADDER_TABLE,
        style_source=str(Path(__file__).relative_to(ROOT)),
    )
    return paths


def _render_binary_models() -> tuple[Path, Path, Path]:
    frames: list[pd.DataFrame] = []
    for model, path in BINARY_INPUTS.items():
        frame = pd.read_csv(path)
        frame = frame.loc[frame["parameter_state"] == "fitted_diagnostic"].copy()
        frame["model"] = model
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(BINARY_TABLE, index=False, lineterminator="\n")
    components = ("monoethanolamine", "water")
    titles = {"monoethanolamine": "MEA closure", "water": "Water closure"}
    roles = {
        "binary_training": ("#28659c", "o", "101.33 kPa training"),
        "binary_model_selection": ("#b6312c", "^", "66.66 kPa held-out"),
    }
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 8.1), sharex=True)
    for row_index, model in enumerate(BINARY_INPUTS):
        for column_index, component in enumerate(components):
            ax = axes[row_index, column_index]
            subset = combined.loc[
                (combined["model"] == model) & (combined["component_id"] == component)
            ]
            for role, (color, marker, label) in roles.items():
                rows = subset.loc[subset["fit_role"] == role].sort_values(
                    "water_liquid_mole_fraction"
                )
                ax.plot(
                    rows["water_liquid_mole_fraction"],
                    rows["normalized_residual"],
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
        "Cai (1996) source-consistent Baygi diagnostics — non-promotable\n"
        "Measured $T$, $P$, $x$, and $y$ are inputs; Bubble-T/Dew-T is not claimed",
        fontsize=11.5,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.92))
    paths = save_figure_bundle(fig, BINARY_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        BINARY_STEM.with_suffix(".mpl.yaml"),
        png_name=paths[0].name,
        svg_name=paths[1].name,
        pdf_name=paths[2].name,
        title="Diagnostic Cai Baygi binary-model fugacity closure comparison",
        description=(
            "Exact fixed-state closure residuals for source-consistent Baygi 3B/2B "
            "and 3B/4C models. Both fits fail source-scale residual and trend gates."
        ),
        data_path=BINARY_TABLE,
        style_source=str(Path(__file__).relative_to(ROOT)),
    )
    return paths


def main() -> None:
    required = (LADDER_TABLE, *BINARY_INPUTS.values())
    missing = [path for path in required if not path.exists()]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise FileNotFoundError(f"generate retained analysis tables first: {names}")
    FIGURES.mkdir(parents=True, exist_ok=True)
    for path in (*_render_pressure_models(), *_render_binary_models()):
        print(path.relative_to(ROOT))
    print(LADDER_TABLE.relative_to(ROOT))
    print(BINARY_TABLE.relative_to(ROOT))


if __name__ == "__main__":
    main()
