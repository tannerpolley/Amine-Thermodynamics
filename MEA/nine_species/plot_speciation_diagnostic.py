from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MEA.common.config import (
    CANONICAL_MEA_WEIGHT_FRACTION,
    CANONICAL_TEMPERATURE_C,
    CANONICAL_TEMPERATURE_K,
    NINE_SPECIES_ALPHA_GRID,
)
from MEA.common.data_access import load_speciation_data
from MEA.common.plot_export import default_output_dir, save_plot
from MEA.common.reporting import write_csv_report, write_json_report
from MEA.nine_species.chemistry import (
    AllSpeciesChemistryResult,
    PLOT_LABELS,
    PLOT_SPECIES,
    SPECIES,
    result_rows,
    solve_all_species_series,
)


def write_diagnostics(results: list[AllSpeciesChemistryResult], output_dir: Path) -> tuple[Path, Path]:
    rows = result_rows(results)
    csv_path = write_csv_report(output_dir / "all_species_solver_diagnostics.csv", rows)
    failures = [row for row in rows if not bool(row["success"])]
    payload = {
        "n_points": len(rows),
        "n_success": len(rows) - len(failures),
        "n_failed": len(failures),
        "failed_loadings": [row["CO2_loading"] for row in failures],
        "failures": failures,
    }
    json_path = write_json_report(output_dir / "all_species_solver_summary.json", payload)
    return csv_path, json_path


def _plot_failed_loadings(ax, results: list[AllSpeciesChemistryResult], y_value: float) -> None:
    failed_loadings = [result.loading for result in results if not result.success]
    if failed_loadings:
        ax.scatter(
            failed_loadings,
            np.full(len(failed_loadings), y_value),
            marker="x",
            color="black",
            label="solver failed",
            zorder=5,
        )


def plot_speciation_diagnostic(results: list[AllSpeciesChemistryResult]) -> Path:
    colors = [
        "tab:green",
        "tab:blue",
        "tab:orange",
        "tab:olive",
        "tab:red",
        "tab:cyan",
        "tab:purple",
        "tab:brown",
        "tab:gray",
        "tab:pink",
    ]
    alpha = np.asarray([result.loading for result in results], dtype=float)
    x_rows = [result.x if result.success else np.full(len(SPECIES), np.nan, dtype=float) for result in results]
    x_true_arr = np.asarray(x_rows, dtype=float).T
    x_true_arr = np.vstack([x_true_arr, x_true_arr[1] + x_true_arr[3]])

    fig, ax = plt.subplots(figsize=(10, 10))
    for species, x_true, color in zip(PLOT_SPECIES, x_true_arr, colors):
        if species == "H2O":
            continue
        ax.semilogy(alpha, x_true, "--", color=color, label=PLOT_LABELS[species])

    data = load_speciation_data(
        temperature_C=CANONICAL_TEMPERATURE_C,
        mea_weight_fraction=CANONICAL_MEA_WEIGHT_FRACTION,
    )
    data_species = list(data.columns[3:-1])
    for species, color in zip(PLOT_SPECIES, colors):
        if species in data_species:
            ax.semilogy(data["CO2_loading"].to_numpy(), data[species].to_numpy(), "o", color=color)

    finite_positive = x_true_arr[np.isfinite(x_true_arr) & (x_true_arr > 0.0)]
    y_floor = 1e-12 if finite_positive.size == 0 else 10.0 ** np.floor(np.log10(float(np.min(finite_positive))))
    _plot_failed_loadings(ax, results, y_floor)

    ax.legend(loc="lower center")
    x_range = np.linspace(0.0, float(np.max(alpha)), 11)
    y_range = np.logspace(np.log10(y_floor), 0, int(abs(np.log10(y_floor))) + 1)
    ax.set_xlim(x_range[0], x_range[-1])
    ax.set_ylim(y_range[0], y_range[-1])
    ax.set_xticks(x_range)
    ax.set_yticks(y_range)
    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    plt.tick_params(labelsize=12)
    return save_plot(fig, __file__, "speciation_diagnostic")


def main() -> int:
    results = solve_all_species_series(
        NINE_SPECIES_ALPHA_GRID,
        CANONICAL_MEA_WEIGHT_FRACTION,
        CANONICAL_TEMPERATURE_K,
    )
    output_dir = default_output_dir(__file__)
    csv_path, json_path = write_diagnostics(results, output_dir)
    plot_path = plot_speciation_diagnostic(results)

    n_failed = sum(not result.success for result in results)
    print(f"All-species diagnostics: {csv_path}")
    print(f"All-species summary: {json_path}")
    print(f"All-species plot: {plot_path}")
    print(f"All-species solver points: {len(results) - n_failed}/{len(results)} successful, {n_failed} failed")
    return 0 if any(result.success for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
