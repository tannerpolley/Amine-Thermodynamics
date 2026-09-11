"""Compare the selected bundle's Gibbs--Helmholtz slope with retained calorimetry."""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = Path(__file__).resolve().parents[1]
PRESSURE = ANALYSIS / "figures/pressure/output/pressure-model-lines.csv"
OBSERVATIONS = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
RESULTS = ANALYSIS / "results/historical/calorimetry"
FIGURES = ANALYSIS / "figures/historical/calorimetry/output"
TEMPERATURES_C = (40.0, 60.0, 80.0)
R_J_MOL_K = 8.31446261815324

sys.path.insert(0, str(ROOT / "src"))
from MEA.common.analysis_io import file_sha256, repo_relative_path  # noqa: E402
from MEA.common.plot_style import (  # noqa: E402
    apply_plot_theme,
    save_figure_bundle,
    write_mpl_sidecar,
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    pressure = read_rows(PRESSURE)
    isotherms: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    for temperature_c in TEMPERATURES_C:
        selected = [
            row for row in pressure if float(row["temperature_C"]) == temperature_c
        ]
        isotherms[temperature_c] = (
            np.asarray(
                [float(row["loading_mol_CO2_per_mol_MEA"]) for row in selected]
            ),
            np.log(np.asarray([float(row["predicted_pCO2_kPa"]) for row in selected])),
        )
    lower = max(values[0][0] for values in isotherms.values())
    upper = min(values[0][-1] for values in isotherms.values())
    loading_grid = np.linspace(lower, upper, 160)
    inverse_temperature = 1.0 / (
        np.asarray(TEMPERATURES_C, dtype=float) + 273.15
    )
    curve = []
    for loading in loading_grid:
        log_pressure = np.asarray(
            [np.interp(loading, *isotherms[temperature]) for temperature in TEMPERATURES_C]
        )
        slope, intercept = np.polyfit(inverse_temperature, log_pressure, 1)
        fitted = slope * inverse_temperature + intercept
        curve.append(
            {
                "loading_mol_CO2_per_mol_MEA": float(loading),
                "heat_release_kj_per_mol_CO2": float(-R_J_MOL_K * slope / 1000.0),
                "ln_pressure_fit_rmse": float(np.sqrt(np.mean((fitted - log_pressure) ** 2))),
            }
        )

    observations = [
        row
        for row in read_rows(OBSERVATIONS)
        if row["regression_eligible"] == "true"
        and row["mea_mass_fraction"] == "0.30"
        and row["temperature_C"] in {"40", "80"}
        and row["source_role"] == "primary_direct_calorimetry"
    ]
    grid_x = np.asarray([row["loading_mol_CO2_per_mol_MEA"] for row in curve])
    grid_y = np.asarray([row["heat_release_kj_per_mol_CO2"] for row in curve])
    comparison = []
    for row in observations:
        loading = float(row["co2_loading_mol_per_mol_mea"])
        admitted = lower <= loading <= upper
        predicted = float(np.interp(loading, grid_x, grid_y)) if admitted else None
        observed = float(row["dh_kj_per_mol_co2"])
        comparison.append(
            {
                "record_id": row["record_id"],
                "source": row["source"],
                "temperature_C": float(row["temperature_C"]),
                "campaign_partition": row["campaign_partition"],
                "loading_mol_CO2_per_mol_MEA": loading,
                "observed_heat_release_kj_per_mol_CO2": observed,
                "predicted_heat_release_kj_per_mol_CO2": predicted,
                "residual_kj_per_mol_CO2": None if predicted is None else predicted - observed,
                "status": "evaluated" if admitted else "outside_common_loading_interval",
            }
        )
    residuals = [
        float(row["residual_kj_per_mol_CO2"])
        for row in comparison
        if row["status"] == "evaluated"
    ]
    summary = {
        "schema": "mea.selected-bundle-gibbs-helmholtz-calorimetry.v1",
        "status": "diagnostic_not_direct_total_enthalpy",
        "method": "linear fit of ln(pCO2) versus inverse temperature at fixed loading using the selected-bundle 40, 60, and 80 C curves",
        "temperature_isotherms_C": TEMPERATURES_C,
        "common_loading_interval": [float(lower), float(upper)],
        "observations": len(observations),
        "evaluated_observations": len(residuals),
        "rmse_kj_per_mol_CO2": math.sqrt(statistics.fmean(value * value for value in residuals)),
        "mean_bias_kj_per_mol_CO2": statistics.fmean(residuals),
        "median_absolute_error_kj_per_mol_CO2": statistics.median(map(abs, residuals)),
        "pressure_model_lines_sha256": file_sha256(PRESSURE),
        "calorimetry_partition_sha256": file_sha256(OBSERVATIONS),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_rows(RESULTS / "current-selected-gibbs-helmholtz-curve.csv", curve)
    write_rows(RESULTS / "current-selected-gibbs-helmholtz-comparison.csv", comparison)
    (RESULTS / "current-selected-gibbs-helmholtz-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    apply_plot_theme()
    fig, ax = plt.subplots(figsize=(9.0, 5.7))
    ax.plot(grid_x, grid_y, color="#111827", linewidth=2.1, linestyle="--", label="Selected bundle Gibbs--Helmholtz slope")
    for temperature_c, marker, color in ((40.0, "o", "#0072B2"), (80.0, "s", "#D55E00")):
        selected = [row for row in comparison if row["temperature_C"] == temperature_c]
        ax.scatter(
            [row["loading_mol_CO2_per_mol_MEA"] for row in selected],
            [row["observed_heat_release_kj_per_mol_CO2"] for row in selected],
            marker=marker,
            color=color,
            edgecolor="black",
            linewidth=0.45,
            s=42,
            alpha=0.86,
            label=f"Kim and Svendsen 2007, {temperature_c:.0f} °C",
        )
    ax.set(
        xlabel="CO$_2$ loading (mol mol$^{-1}$ MEA)",
        ylabel="Heat release magnitude (kJ mol$^{-1}$ CO$_2$)",
        title="Selected-bundle absorption-heat diagnostic",
    )
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    png, svg, pdf = save_figure_bundle(fig, FIGURES / "current-selected-calorimetry-diagnostic")
    write_mpl_sidecar(
        FIGURES / "current-selected-calorimetry-diagnostic.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="Selected-bundle absorption-heat diagnostic",
        description="Retained direct calorimetry observations and the selected bundle's dashed Gibbs--Helmholtz pressure-slope diagnostic.",
        data_path=RESULTS / "current-selected-gibbs-helmholtz-comparison.csv",
    )
    with (FIGURES / "current-selected-calorimetry-diagnostic.mpl.yaml").open(
        "a", encoding="utf-8"
    ) as stream:
        stream.write(f"pressure_lines_path: {repo_relative_path(PRESSURE)}\n")
        stream.write(f"pressure_lines_sha256: {file_sha256(PRESSURE)}\n")
        stream.write("continuity: line is a fixed-loading Gibbs--Helmholtz slope from three discrete temperature isotherms\n")
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
