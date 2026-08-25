from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import colormaps, colors
from matplotlib.lines import Line2D
import pandas as pd

from generate import ANALYSIS
from run_full_predictive_refinement import _pressure_rows
from MEA.common.analysis_io import read_csv_rows as _csv, read_diagnostic_rows
from MEA.common.plot_style import finish_axes, save_figure_bundle, write_mpl_sidecar
from MEA.epcsaft_ionic.model import load_speciation_targets


RESULTS = ANALYSIS / "results"
FIGURES = ANALYSIS / "figures"
TRAINING = RESULTS / "predictive_training_refinement"
RESERVED = RESULTS / "predictive_reserved_validation"
CHALLENGE = RESULTS / "predictive_temperature_challenge"
PLOT_TABLE = FIGURES / "predictive_partition_plot_data.csv"
METRIC_TABLE = RESULTS / "predictive_partition_metrics.csv"
SUMMARY = RESULTS / "predictive_partition_summary.json"
STEM = FIGURES / "predictive_partition_evidence"
PARTITIONS = {
    "training": ("o", "-"),
    "reserved": ("s", "--"),
    "temperature challenge": ("x", ":"),
}
TARGETS = ("CO2", "MEA", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "MEA + MEAH+")


def _row(*, partition: str, block: str, identity: str, target: str,
         temperature_k: float, loading: float, observed: float, predicted: float,
         source: str) -> dict[str, object]:
    return {
        "partition": partition,
        "block": block,
        "identity": identity,
        "target": target,
        "temperature_k": temperature_k,
        "mea_mass_fraction": 0.30,
        "source": source,
        "loading_mol_co2_per_mol_mea": loading,
        "observed": observed,
        "predicted": predicted,
        "unit": "pascal" if block == "pressure" else "dimensionless",
    }


def _load_rows() -> list[dict[str, object]]:
    pressure = {row["observation_id"]: row for row in _pressure_rows()}
    speciation = {
        state.row_id: state
        for role in ("active_training", "reserved_validation")
        for state in load_speciation_targets(None, role=role)
    }
    rows: list[dict[str, object]] = []
    for fit in _csv(TRAINING / "fit_rows.csv"):
        if fit["unit"] == "pascal":
            source = pressure[fit["identity"]]
            rows.append(_row(
                partition="training", block="pressure", identity=fit["identity"],
                target="CO2 partial pressure", temperature_k=float(source["temperature_K"]),
                loading=float(source["co2_loading_mol_per_mol_mea"]),
                observed=float(fit["observed"]), predicted=float(fit["predicted"]),
                source=source["source_key"],
            ))
        else:
            state_id, target = fit["identity"].rsplit("::", 1)
            state = speciation[state_id]
            rows.append(_row(
                partition="training", block="speciation", identity=fit["identity"],
                target=target, temperature_k=state.T, loading=state.loading,
                observed=float(fit["observed"]), predicted=float(fit["predicted"]),
                source=state.source,
            ))
    for partition, path in (
        ("reserved", RESERVED / "compile_diagnostics.csv"),
        ("temperature challenge", CHALLENGE / "compile_diagnostics.csv"),
    ):
        for item in read_diagnostic_rows(path, nested=True):
            if item["block"] == "pressure":
                source = pressure[item["identity"]]
                rows.append(_row(
                    partition=partition, block="pressure", identity=item["identity"],
                    target="CO2 partial pressure", temperature_k=float(item["temperature_k"]),
                    loading=float(item["loading"]), observed=float(item["observed"]),
                    predicted=float(item["predicted"]), source=source["source_key"],
                ))
            else:
                state = speciation[item["identity"]]
                for target_row in item["targets"]:
                    target = str(target_row["identity"]).rsplit("::", 1)[1]
                    rows.append(_row(
                        partition=partition, block="speciation",
                        identity=str(target_row["identity"]), target=target,
                        temperature_k=state.T, loading=state.loading,
                        observed=float(target_row["observed"]),
                        predicted=float(target_row["predicted"]), source=state.source,
                    ))
    return rows


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
    frame = pd.DataFrame(_load_rows()).sort_values(
        ["block", "target", "partition", "temperature_k", "source", "loading_mol_co2_per_mol_mea"]
    )
    frame.to_csv(PLOT_TABLE, index=False, lineterminator="\n")
    metric_rows = []
    for (partition, block), subset in frame.groupby(["partition", "block"], sort=False):
        metric_rows.append({"partition": partition, "block": block, **_metrics(subset)})
    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(METRIC_TABLE, index=False, lineterminator="\n")
    summary = {
        "schema": "mea.predictive-partition-evidence.v1",
        "engine_wheel_sha256": json.loads((TRAINING / "summary.json").read_text())["engine_wheel_sha256"],
        "parameters": json.loads((TRAINING / "summary.json").read_text())["fitted_values"],
        "metrics": metric_rows,
        "row_count": len(frame),
        "failed_or_omitted_rows": 0,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    figure, axes = plt.subplots(2, 4, figsize=(17.2, 10.2), constrained_layout=True)
    panels = [("pressure", "CO2 partial pressure"), *(("speciation", target) for target in TARGETS)]
    temperatures_c = frame["temperature_k"] - 273.15
    norm = colors.Normalize(float(temperatures_c.min()), float(temperatures_c.max()))
    cmap = colormaps["viridis"]
    for ax, (block, target) in zip(axes.flat, panels, strict=True):
        panel = frame.loc[(frame["block"] == block) & (frame["target"] == target)]
        for (partition, temperature_k, source), group in panel.groupby(
            ["partition", "temperature_k", "source"], sort=True
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
                group["loading_mol_co2_per_mol_mea"], group["observed"],
                marker=marker, s=36, linewidths=1.0, zorder=3, **marker_style,
            )
            if len(group) > 1:
                ax.plot(
                    group["loading_mol_co2_per_mol_mea"], group["predicted"],
                    color=color, linestyle=linestyle, linewidth=1.25,
                )
        ax.set_yscale("log")
        ax.set_xlabel(r"CO$_2$ loading, mol CO$_2$/mol MEA")
        ax.set_ylabel(r"CO$_2$ partial pressure, Pa" if block == "pressure" else "Liquid mole fraction")
        finish_axes(ax, title=("30 wt% MEA pressure" if block == "pressure" else target))

    parameters = summary["parameters"]
    axes[0, 0].text(
        0.97, 0.03,
        "Frozen training parameters\n"
        f"$k_{{CO_2,MEA}}$ = {parameters['pair/carbon-dioxide/monoethanolamine/k_ij']:.5f}\n"
        f"$\\sigma_{{MEAH^+}}$ = {parameters['component/protonated-monoethanolamine/segment_diameter']:.5f} Å\n"
        f"$\\sigma_{{MEACOO^-}}$ = {parameters['component/carbamate-anion/segment_diameter']:.5f} Å",
        transform=axes[0, 0].transAxes, ha="right", va="bottom", fontsize=8,
        bbox={"facecolor": "white", "edgecolor": "0.7", "alpha": 0.9},
    )
    axes[0, 0].legend(
        handles=[
            Line2D([], [], color="black", marker=marker, markerfacecolor="none",
                   linestyle=linestyle, label=partition)
            for partition, (marker, linestyle) in PARTITIONS.items()
        ],
        loc="upper left", fontsize=7.5, title="Partition / model line", title_fontsize=8,
    )
    figure.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=axes,
        label="Temperature (°C)", shrink=0.75, pad=0.015,
    )
    figure.suptitle(
        "Frozen MEA parameter prediction: training, untouched reserved data, and temperature challenge",
        fontsize=14,
    )
    paths = save_figure_bundle(figure, STEM, dpi=240)
    plt.close(figure)
    write_mpl_sidecar(
        STEM.with_suffix(".mpl.yaml"), png_name=paths[0].name,
        svg_name=paths[1].name, pdf_name=paths[2].name,
        title="Frozen MEA predictive partition evidence",
        description=(
            "Observed pressure and speciation values are points; model predictions at the "
            "same states are lines. Parameters are fitted only to the training partition."
        ),
        data_path=PLOT_TABLE, style_source=str(Path(__file__).relative_to(ANALYSIS.parents[3])),
    )
    print(SUMMARY)
    print(METRIC_TABLE)
    print(PLOT_TABLE)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
