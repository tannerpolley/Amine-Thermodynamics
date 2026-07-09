from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MEA.common.plot_style import finish_axes, save_figure_bundle, species_color, species_label, write_mpl_sidecar
from MEA.epcsaft_ionic.model import (
    BOUNDS,
    DEFAULT_INITIAL_GUESS,
    EPCSAFT_IONIC_ANALYSIS,
    SPECIES,
    SPECIES_INDEX,
    load_speciation_targets,
    solve_activity_speciation,
    theta_to_map,
    write_csv,
    write_json,
)

OUT_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "ion_parameter_regression"
RUNS_DIR = EPCSAFT_IONIC_ANALYSIS / "results" / "runs" / "ion_parameter_regression"

FIT_NAMES = (
    "MEAH+__s",
    "MEAH+__e",
    "MEAH+__d_born",
    "MEACOO-__s",
    "MEACOO-__e",
    "MEACOO-__d_born",
    "k_ij__MEAH+__MEACOO-",
)

TIER_A_SOURCE_RULES = {
    "Matin": ("MEAH+", "MEACOO-", "HCO3-"),
    "Jakobsen": ("MEAH+", "MEACOO-", "HCO3-", "CO3^2-"),
    "Bottinger": ("MEACOO-", "MEA + MEAH+"),
}


@dataclass(frozen=True)
class IonRegressionTarget:
    row_id: str
    source: str
    T: float
    P: float
    loading: float
    x: np.ndarray
    species_targets: tuple[str, ...]


def _run_dir(label: str | None, promote: bool) -> Path:
    if promote:
        return OUT_DIR
    stamp = label or time.strftime("%Y%m%d-%H%M%S")
    return RUNS_DIR / stamp


def _select_evenly(items: list[IonRegressionTarget], limit: int | None) -> list[IonRegressionTarget]:
    if limit is None or limit <= 0 or len(items) <= limit:
        return items
    positions = np.linspace(0, len(items) - 1, limit)
    return [items[int(round(position))] for position in positions]


def load_tier_a_targets(max_records: int | None = None) -> list[IonRegressionTarget]:
    targets: list[IonRegressionTarget] = []
    for target in load_speciation_targets(None):
        species_targets = TIER_A_SOURCE_RULES.get(target.source)
        if not species_targets:
            continue
        targets.append(
            IonRegressionTarget(
                row_id=target.row_id,
                source=target.source,
                T=target.T,
                P=target.P,
                loading=target.loading,
                x=target.x,
                species_targets=species_targets,
            )
        )
    return _select_evenly(sorted(targets, key=lambda row: (row.source, row.T, row.loading)), max_records)


def initial_fit_vector() -> np.ndarray:
    return np.asarray([DEFAULT_INITIAL_GUESS[name] for name in FIT_NAMES], dtype=float)


def fit_bounds() -> tuple[np.ndarray, np.ndarray]:
    lower = np.asarray([BOUNDS[name][0] for name in FIT_NAMES], dtype=float)
    upper = np.asarray([BOUNDS[name][1] for name in FIT_NAMES], dtype=float)
    return lower, upper


def fit_vector_to_values(vector: Iterable[float]) -> dict[str, float]:
    values = dict(DEFAULT_INITIAL_GUESS)
    values.update({name: float(value) for name, value in zip(FIT_NAMES, vector)})
    return values


def _target_value(target: IonRegressionTarget, species: str) -> float:
    if species == "MEA + MEAH+":
        return float(target.x[SPECIES_INDEX["MEA"]] + target.x[SPECIES_INDEX["MEAH+"]])
    return float(target.x[SPECIES_INDEX[species]])


def _prediction_value(prediction_x: np.ndarray, species: str) -> float:
    if species == "MEA + MEAH+":
        return float(prediction_x[SPECIES_INDEX["MEA"]] + prediction_x[SPECIES_INDEX["MEAH+"]])
    return float(prediction_x[SPECIES_INDEX[species]])


def evaluate_fit_values(values: dict[str, float], targets: list[IonRegressionTarget]) -> tuple[np.ndarray, pd.DataFrame, dict[str, Any]]:
    residuals: list[float] = []
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    scale = math.sqrt(1.0 / max(sum(len(target.species_targets) for target in targets), 1))

    for target in targets:
        try:
            prediction = solve_activity_speciation(target.loading, target.T, target.P, target.x, values)
            prediction_x = prediction.x
            success = prediction.success
            message = prediction.message
        except Exception as exc:
            prediction_x = np.full(len(SPECIES), np.nan, dtype=float)
            success = False
            message = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
            failures.append(f"{target.row_id}: {message}")

        for species in target.species_targets:
            observed = _target_value(target, species)
            predicted = _prediction_value(prediction_x, species)
            raw = math.log10(max(predicted, 1.0e-30) / max(observed, 1.0e-30)) if np.isfinite(predicted) else 8.0
            residuals.append(scale * raw)
            rows.append(
                {
                    "row_id": target.row_id,
                    "source": target.source,
                    "temperature_C": target.T - 273.15,
                    "CO2_loading": target.loading,
                    "species": species,
                    "observed_mole_fraction": observed,
                    "model_mole_fraction": predicted,
                    "log10_model_over_data": raw,
                    "success": bool(success),
                    "message": message,
                }
            )

    # Keep the fit weakly anchored, but not frozen, so a no-change result is visible.
    for name in FIT_NAMES:
        seed = DEFAULT_INITIAL_GUESS[name]
        value = values[name]
        residuals.append(0.003 * (value - seed) / max(abs(seed), 1.0))

    frame = pd.DataFrame(rows)
    metrics = metrics_from_frame(frame)
    metrics["failure_count"] = int((frame["success"] == False).sum()) if not frame.empty else 0
    metrics["failures"] = failures[:20]
    return np.asarray(residuals, dtype=float), frame, metrics


def metrics_from_frame(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {}
    ok = frame[np.isfinite(frame["log10_model_over_data"].astype(float))]
    by_species = {}
    for species, subset in ok.groupby("species"):
        residual = subset["log10_model_over_data"].astype(float).to_numpy()
        observed = subset["observed_mole_fraction"].astype(float).to_numpy()
        predicted = subset["model_mole_fraction"].astype(float).to_numpy()
        by_species[str(species)] = {
            "count": int(len(subset)),
            "rmse_log10": float(np.sqrt(np.mean(residual * residual))),
            "mae_log10": float(np.mean(np.abs(residual))),
            "median_abs_log10": float(np.median(np.abs(residual))),
            "r2_log10": _r2(np.log10(np.clip(observed, 1.0e-30, None)), np.log10(np.clip(predicted, 1.0e-30, None))),
        }
    by_source = {
        str(source): int(len(subset))
        for source, subset in frame.groupby("source")
    }
    residual = ok["log10_model_over_data"].astype(float).to_numpy()
    return {
        "row_count": int(frame["row_id"].nunique()),
        "residual_count": int(len(frame)),
        "source_counts": by_source,
        "overall_rmse_log10": float(np.sqrt(np.mean(residual * residual))) if residual.size else None,
        "overall_mae_log10": float(np.mean(np.abs(residual))) if residual.size else None,
        "overall_median_abs_log10": float(np.median(np.abs(residual))) if residual.size else None,
        "by_species": by_species,
    }


def _r2(observed: np.ndarray, predicted: np.ndarray) -> float | None:
    if observed.size < 2 or predicted.size != observed.size or not np.all(np.isfinite(predicted)):
        return None
    ss_res = float(np.sum((observed - predicted) ** 2))
    ss_tot = float(np.sum((observed - float(np.mean(observed))) ** 2))
    if ss_tot <= 0.0:
        return None
    return float(1.0 - ss_res / ss_tot)


def run_fit(args: argparse.Namespace) -> dict[str, Any]:
    raise RuntimeError(
        "Local SciPy-based Tier-A ion parameter fitting is disabled by MEA-Thermodynamics issue #3. "
        "Use `python -m MEA.epcsaft_ionic.regress_parameters` to build MEA target rows and delegate "
        "parameter fitting to the ePC-SAFT native regression API. Existing ion-parameter artifacts are "
        "historical evidence snapshots only until regenerated from package-native results."
    )


def _statistics_rows(initial_metrics: dict[str, Any], final_metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metric in ("overall_rmse_log10", "overall_mae_log10", "overall_median_abs_log10"):
        rows.append({"family": "overall", "metric": metric, "initial": initial_metrics.get(metric), "final": final_metrics.get(metric)})
    species = sorted(set(initial_metrics.get("by_species", {})) | set(final_metrics.get("by_species", {})))
    for name in species:
        for metric in ("rmse_log10", "mae_log10", "median_abs_log10", "r2_log10"):
            rows.append(
                {
                    "family": str(name),
                    "metric": metric,
                    "initial": initial_metrics.get("by_species", {}).get(name, {}).get(metric),
                    "final": final_metrics.get("by_species", {}).get(name, {}).get(metric),
                }
            )
    return rows


def _write_sidecar(path: Path, stem: str, *, title: str, description: str) -> None:
    write_mpl_sidecar(
        path,
        png_name=f"{stem}.png",
        svg_name=f"{stem}.svg",
        pdf_name=f"{stem}.pdf",
        title=title,
        description=description,
    )


def plot_speciation_parity(frame: pd.DataFrame, output_dir: Path) -> Path:
    title = "MEAH+/MEACOO- ion-parameter speciation parity"
    description = (
        "Tier-A ion-parameter evidence compares measured and model amine-family true-species mole fractions."
    )
    final = frame[(frame["fit_stage"] == "final") & frame["species"].isin(["MEAH+", "MEACOO-", "MEA + MEAH+"])]
    fig, ax = plt.subplots(figsize=(7, 7))
    for species, subset in final.groupby("species"):
        color = species_color(species)
        for source, source_subset in subset.groupby("source"):
            ax.scatter(
                source_subset["observed_mole_fraction"],
                source_subset["model_mole_fraction"],
                label=f"{species_label(species)} {source}",
                color=color,
                alpha=0.75,
                edgecolor="black",
                linewidth=0.3,
            )
    finite = final[["observed_mole_fraction", "model_mole_fraction"]].replace([np.inf, -np.inf], np.nan).dropna()
    if not finite.empty:
        lo = max(1.0e-5, float(finite.min().min()) * 0.7)
        hi = min(1.0, float(finite.max().max()) * 1.3)
    else:
        lo, hi = 1.0e-5, 1.0
    ax.plot([lo, hi], [lo, hi], color="black", linestyle=":", label="1:1")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Observed true-species mole fraction")
    ax.set_ylabel("Model true-species mole fraction")
    finish_axes(ax, title=title)
    ax.legend(fontsize=8, title="Species and source")
    fig.tight_layout()
    path = output_dir / "meah_meacoo_speciation_parity.png"
    save_figure_bundle(fig, path.with_suffix(""))
    plt.close(fig)
    _write_sidecar(path.with_suffix(".mpl.yaml"), path.stem, title=title, description=description)
    return path


def plot_loading_curves(frame: pd.DataFrame, output_dir: Path) -> Path:
    title = "MEAH+/MEACOO- loading curves from Tier-A speciation evidence"
    description = (
        "Observed and model amine-family true-species mole fractions are plotted against carbon-dioxide loading."
    )
    subset = frame[frame["species"].isin(["MEAH+", "MEACOO-", "MEA + MEAH+"])]
    fig, ax = plt.subplots(figsize=(9, 6))
    for species, species_frame in subset.groupby("species"):
        color = species_color(species)
        final = species_frame[species_frame["fit_stage"] == "final"].sort_values("CO2_loading")
        observed = final.drop_duplicates(["row_id", "source", "species"]).sort_values("CO2_loading")
        if not observed.empty:
            ax.semilogy(
                observed["CO2_loading"],
                observed["observed_mole_fraction"],
                "o",
                color=color,
                alpha=0.6,
                label=f"{species_label(species)} data",
            )
        if not final.empty:
            ax.semilogy(
                final["CO2_loading"],
                final["model_mole_fraction"],
                "-",
                color=color,
                label=f"{species_label(species)} fitted",
            )
    ax.set_xlabel("$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_ylim(1.0e-5, 0.3)
    finish_axes(ax, title=title)
    ax.legend(fontsize=8, title="Species and role")
    fig.tight_layout()
    path = output_dir / "meah_meacoo_loading_curves.png"
    save_figure_bundle(fig, path.with_suffix(""))
    plt.close(fig)
    _write_sidecar(path.with_suffix(".mpl.yaml"), path.stem, title=title, description=description)
    return path


def plot_pressure_placeholder(output_dir: Path) -> Path:
    title = "Ion-parameter pressure parity placeholder"
    description = (
        "Placeholder panel indicating that pressure parity belongs to the full ionic pressure workflow, "
        "not the ion-only speciation evidence artifact."
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.axis("off")
    ax.set_title(title)
    ax.text(
        0.5,
        0.5,
        "Pressure parity must be regenerated\nwith the promoted full ionic VLE workflow.",
        ha="center",
        va="center",
    )
    path = output_dir / "ion_parameter_pressure_parity.png"
    save_figure_bundle(fig, path.with_suffix(""))
    plt.close(fig)
    _write_sidecar(path.with_suffix(".mpl.yaml"), path.stem, title=title, description=description)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit MEAH+/MEACOO- ePC-SAFT parameters against real Tier A speciation data.")
    parser.add_argument("--max-records", type=int, default=8)
    parser.add_argument("--max-nfev", type=int, default=8)
    parser.add_argument("--output-label", default=None)
    parser.add_argument("--promote", action="store_true", help="Write curated artifacts under results/ion_parameter_regression.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    summary = run_fit(args)
    print(f"Ion parameter target rows: {summary['target_row_count']}")
    print(f"Optimizer success: {summary['optimizer']['success']} ({summary['optimizer']['message']})")
    print(
        "Residual norm: "
        f"{summary['optimizer']['initial_residual_norm']:.6g} -> {summary['optimizer']['final_residual_norm']:.6g}"
    )
    print(f"Overall median |log10(model/data)|: {summary['initial_metrics'].get('overall_median_abs_log10')} -> {summary['final_metrics'].get('overall_median_abs_log10')}")
    print("Fitted ion parameters:")
    for name, value in summary["fitted_values"].items():
        print(f"  {name} = {value:.12g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

