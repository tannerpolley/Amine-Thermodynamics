from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from MEA.common.plot_style import finish_axes, save_figure_bundle, write_mpl_sidecar


ROOT = Path(__file__).resolve().parents[4]
ANALYSIS = ROOT / "analyses/reactive_epcsaft_parameter_evidence/pressure_first"
RESULTS = ANALYSIS / "results"
FIGURES = RESULTS / "figures"
MODELS = {
    "Held water + 2B MEA": "cai_held_water_mea_2b",
    "Held water + 3B MEA": "cai_held_water_mea_3b",
    "Held water + 4C MEA": "cai_held_water_mea_4c",
}
PLOT_TABLE = FIGURES / "cai_held_water_mea_family_plot_data.csv"
SUMMARY_TABLE = FIGURES / "cai_held_water_mea_family_summary.csv"
FIGURE_STEM = FIGURES / "cai_held_water_mea_family_comparison"


def _load() -> tuple[pd.DataFrame, pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    summaries: list[dict[str, object]] = []
    for label, stem in MODELS.items():
        frame = pd.read_csv(RESULTS / f"{stem}_predictions.csv")
        frame = frame.loc[frame["parameter_state"] == "fitted_diagnostic"].copy()
        frame["model"] = label
        frames.append(frame)
        fit = json.loads((RESULTS / f"{stem}_fit.json").read_text(encoding="utf-8"))
        training = frame.loc[frame["fit_role"] == "binary_training"]
        selection = frame.loc[frame["fit_role"] == "binary_model_selection"]
        training_rmse = float(
            math.sqrt((training["raw_log_fugacity_residual"] ** 2).mean())
        )
        selection_rmse = float(
            math.sqrt((selection["raw_log_fugacity_residual"] ** 2).mean())
        )
        summaries.append(
            {
                "model": label,
                "k_mea_h2o": fit["selected_value"],
                "training_raw_log_rmse": training_rmse,
                "training_typical_factor": math.exp(training_rmse),
                "held_out_raw_log_rmse": selection_rmse,
                "held_out_typical_factor": math.exp(selection_rmse),
                "all_rows_evaluated": fit["gates"]["all_admitted_rows_evaluated"],
                "exact_jacobian_check": fit["gates"]["exact_jacobian_check"],
                "multistart_agreement": fit["gates"]["all_starts_same_solution"],
                "runtime_seconds": fit["runtime_seconds"],
            }
        )
    return pd.concat(frames, ignore_index=True), pd.DataFrame(summaries)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    combined, summary = _load()
    combined.to_csv(PLOT_TABLE, index=False, lineterminator="\n")
    summary.to_csv(SUMMARY_TABLE, index=False, lineterminator="\n")

    components = ("monoethanolamine", "water")
    titles = {"monoethanolamine": "MEA closure", "water": "Water closure"}
    roles = {
        "binary_training": ("#28659c", "o", "101.33 kPa fit"),
        "binary_model_selection": ("#b6312c", "^", "66.66 kPa held out"),
    }
    fig, axes = plt.subplots(len(MODELS), 2, figsize=(10.8, 10.8), sharex=True)
    for row_index, model in enumerate(MODELS):
        parameter = float(summary.loc[summary["model"] == model, "k_mea_h2o"].iloc[0])
        for column_index, component in enumerate(components):
            ax = axes[row_index, column_index]
            subset = combined.loc[
                (combined["model"] == model)
                & (combined["component_id"] == component)
            ]
            for role, (color, marker, label) in roles.items():
                rows = subset.loc[subset["fit_role"] == role].sort_values(
                    "water_liquid_mole_fraction"
                )
                ax.plot(
                    rows["water_liquid_mole_fraction"],
                    rows["raw_log_fugacity_residual"],
                    color=color,
                    marker=marker,
                    linewidth=1.2,
                    markersize=4.5,
                    label=label,
                )
            ax.axhline(0.0, color="black", linestyle=":", linewidth=1.0)
            ax.set_xlabel("Liquid water mole fraction")
            ax.set_ylabel("Log-fugacity closure residual")
            finish_axes(
                ax,
                title=f"{model}: {titles[component]}, $k_{{ij}}={parameter:.5f}$",
            )
            ax.legend(fontsize=7)
    fig.suptitle(
        "Cai (1996) MEA-water qualification under fixed Held 2B water",
        fontsize=12,
        fontweight="semibold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.97))
    paths = save_figure_bundle(fig, FIGURE_STEM)
    plt.close(fig)
    write_mpl_sidecar(
        FIGURE_STEM.with_suffix(".mpl.yaml"),
        png_name=paths[0].name,
        svg_name=paths[1].name,
        pdf_name=paths[2].name,
        title="Cai MEA-water association-family qualification",
        description=(
            "Measured-state component log-fugacity closure for three Baygi MEA "
            "association candidates under fixed Held water. The 101.33 kPa series "
            "fits the binary interaction; the 66.66 kPa series is held out."
        ),
        data_path=PLOT_TABLE,
        style_source=str(Path(__file__).relative_to(ROOT)),
    )
    for path in paths:
        print(path.relative_to(ROOT))
    print(PLOT_TABLE.relative_to(ROOT))
    print(SUMMARY_TABLE.relative_to(ROOT))


if __name__ == "__main__":
    main()
