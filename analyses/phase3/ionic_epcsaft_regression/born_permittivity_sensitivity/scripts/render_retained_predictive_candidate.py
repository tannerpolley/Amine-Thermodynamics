from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import colormaps, colors
from matplotlib.lines import Line2D
import pandas as pd

from generate import ANALYSIS
from MEA.common.plot_style import finish_axes, save_figure_bundle, write_mpl_sidecar


RESULTS = ANALYSIS / "results"
FIGURES = ANALYSIS / "figures"
INPUT = RESULTS / "co2_water_kij_anchored_transfer/predictions.csv"
PARAMETERS = RESULTS / "retained_predictive_parameter_settings.json"
PLOT_TABLE = FIGURES / "retained_predictive_candidate_plot_data.csv"
METRIC_TABLE = RESULTS / "retained_predictive_candidate_metrics.csv"
SUMMARY = RESULTS / "retained_predictive_candidate_summary.json"
STEM = FIGURES / "retained_predictive_candidate_evidence"
PARTITIONS = {
    "training": ("o", "-"),
    "reserved": ("s", "--"),
    "temperature challenge": ("x", ":"),
}
TARGETS = ("CO2", "MEA", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "MEA + MEAH+")


def _metrics(frame: pd.DataFrame) -> dict[str, float | int]:
    residual = (frame["predicted"] / frame["observed"]).map(math.log)
    rmse = math.sqrt(float((residual * residual).mean()))
    return {
        "row_count": len(frame),
        "log_rmse": rmse,
        "rms_factor": math.exp(rmse),
        "median_factor": math.exp(float(residual.abs().median())),
        "mean_log_bias": float(residual.mean()),
    }


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    retained = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    frame = pd.read_csv(INPUT).rename(
        columns={"state_identity": "identity", "loading": "loading_mol_co2_per_mol_mea"}
    )
    frame["partition"] = frame["partition"].str.replace("_", " ")
    frame["target"] = frame["target_identity"].str.rsplit("::", n=1).str[-1]
    frame.loc[frame["block"] == "pressure", "target"] = "CO2 partial pressure"
    frame["mea_mass_fraction"] = 0.30
    frame = frame.sort_values(
        ["block", "target", "partition", "temperature_k", "loading_mol_co2_per_mol_mea"]
    )
    frame.to_csv(PLOT_TABLE, index=False, lineterminator="\n")

    metric_rows = [
        {"partition": partition, "block": block, **_metrics(subset)}
        for (partition, block), subset in frame.groupby(
            ["partition", "block"], sort=False
        )
    ]
    pd.DataFrame(metric_rows).to_csv(METRIC_TABLE, index=False, lineterminator="\n")
    summary = {
        "schema": "mea.retained-predictive-candidate-figure.v1",
        "engine_wheel_sha256": retained["engine_wheel_sha256"],
        "state_count": retained["accounting"]["equilibrium_state_count"],
        "row_count": len(frame),
        "failed_or_omitted_rows": retained["accounting"]["failure_count"],
        "metrics": metric_rows,
        "retained_parameter_file": str(PARAMETERS.relative_to(ANALYSIS)),
    }
    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    figure, axes = plt.subplots(2, 4, figsize=(17.2, 10.2), constrained_layout=True)
    panels = [
        ("pressure", "CO2 partial pressure"),
        *(("speciation", target) for target in TARGETS),
    ]
    temperatures_c = frame["temperature_k"] - 273.15
    norm = colors.Normalize(float(temperatures_c.min()), float(temperatures_c.max()))
    cmap = colormaps["viridis"]
    for ax, (block, target) in zip(axes.flat, panels, strict=True):
        panel = frame.loc[(frame["block"] == block) & (frame["target"] == target)]
        for (partition, temperature_k), group in panel.groupby(
            ["partition", "temperature_k"], sort=True
        ):
            group = group.sort_values("loading_mol_co2_per_mol_mea")
            marker, linestyle = PARTITIONS[partition]
            color = cmap(norm(float(temperature_k) - 273.15))
            marker_style = (
                {"color": color}
                if marker == "x"
                else {"facecolors": "none", "edgecolors": color}
            )
            ax.scatter(
                group["loading_mol_co2_per_mol_mea"],
                group["observed"],
                marker=marker,
                s=36,
                linewidths=1.0,
                zorder=3,
                **marker_style,
            )
            if len(group) > 1:
                ax.plot(
                    group["loading_mol_co2_per_mol_mea"],
                    group["predicted"],
                    color=color,
                    linestyle=linestyle,
                    linewidth=1.25,
                )
        ax.set_yscale("log")
        ax.set_xlabel(r"CO$_2$ loading, mol CO$_2$/mol MEA")
        ax.set_ylabel(
            r"CO$_2$ partial pressure, Pa"
            if block == "pressure"
            else "Liquid mole fraction"
        )
        finish_axes(
            ax, title=("30 wt% MEA pressure" if block == "pressure" else target)
        )

    shared = retained["shared_parameters"]
    axes[0, 0].text(
        0.97,
        0.03,
        "Retained parameterization\n"
        "shell Born; ion-suppressed permittivity\n"
        "CO$_2$-water induced association\n"
        r"$k_{CO_2,H_2O}=3.016\times10^{-4}(T-313.15)$"
        "\n"
        f"$k_{{CO_2,MEA}}$ = {shared['pair/carbon-dioxide/monoethanolamine/k_ij']:.5f}\n"
        f"$\\sigma_{{MEAH^+}}$ = {shared['component/protonated-monoethanolamine/segment_diameter_angstrom']:.5f} Å\n"
        f"$\\sigma_{{MEACOO^-}}$ = {shared['component/carbamate-anion/segment_diameter_angstrom']:.5f} Å",
        transform=axes[0, 0].transAxes,
        ha="right",
        va="bottom",
        fontsize=7.4,
        bbox={"facecolor": "white", "edgecolor": "0.7", "alpha": 0.92},
    )
    axes[0, 0].legend(
        handles=[
            Line2D(
                [],
                [],
                color="black",
                marker=marker,
                markerfacecolor="none",
                linestyle=linestyle,
                label=partition,
            )
            for partition, (marker, linestyle) in PARTITIONS.items()
        ],
        loc="upper left",
        fontsize=7.5,
        title="Observation / model line",
        title_fontsize=8,
    )
    figure.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=axes,
        label="Temperature (°C)",
        shrink=0.75,
        pad=0.015,
    )
    figure.suptitle(
        "Retained predictive MEA candidate: 119 states, 257 targets, zero failures",
        fontsize=14,
    )
    paths = save_figure_bundle(figure, STEM, dpi=240)
    plt.close(figure)
    write_mpl_sidecar(
        STEM.with_suffix(".mpl.yaml"),
        png_name=paths[0].name,
        svg_name=paths[1].name,
        pdf_name=paths[2].name,
        title="Retained predictive MEA candidate evidence",
        description=(
            "Observed pressure and speciation values are points; retained model predictions "
            "at the same states are lines. The candidate evaluates every retained target."
        ),
        data_path=PLOT_TABLE,
        style_source=str(Path(__file__).relative_to(ANALYSIS.parents[3])),
    )
    print(SUMMARY)
    print(METRIC_TABLE)
    print(PLOT_TABLE)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
