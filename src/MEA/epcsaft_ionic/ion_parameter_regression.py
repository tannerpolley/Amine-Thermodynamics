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
from scipy.optimize import least_squares

from MEA.common.plot_style import species_color, species_label
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
            success = "did not converge" not in prediction.message.lower()
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
    output_dir = _run_dir(args.output_label, args.promote)
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = load_tier_a_targets(args.max_records)
    if not targets:
        raise RuntimeError("No Tier A MEAH+/MEACOO- ion-regression targets were found.")

    x0 = initial_fit_vector()
    lower, upper = fit_bounds()
    x0 = np.clip(x0, lower, upper)
    initial_values = fit_vector_to_values(x0)
    initial_residuals, initial_frame, initial_metrics = evaluate_fit_values(initial_values, targets)

    result = least_squares(
        lambda vector: evaluate_fit_values(fit_vector_to_values(np.asarray(vector, dtype=float)), targets)[0],
        x0,
        bounds=(lower, upper),
        loss="soft_l1",
        f_scale=1.0,
        x_scale=np.maximum(np.abs(x0), 1.0),
        max_nfev=int(args.max_nfev),
        verbose=2 if args.verbose else 0,
    )

    fitted_values = fit_vector_to_values(result.x)
    final_residuals, final_frame, final_metrics = evaluate_fit_values(fitted_values, targets)
    initial_frame.insert(0, "fit_stage", "initial")
    final_frame.insert(0, "fit_stage", "final")
    plotted = pd.concat([initial_frame, final_frame], ignore_index=True)

    values_rows = []
    at_bounds = {}
    for name, initial, fitted, lo, hi in zip(FIT_NAMES, x0, result.x, lower, upper):
        near_bound = bool(np.isclose(fitted, lo, rtol=0.0, atol=1.0e-7) or np.isclose(fitted, hi, rtol=0.0, atol=1.0e-7))
        at_bounds[name] = near_bound
        values_rows.append(
            {
                "parameter": name,
                "initial": float(initial),
                "fitted": float(fitted),
                "delta": float(fitted - initial),
                "lower_bound": float(lo),
                "upper_bound": float(hi),
                "at_bound": near_bound,
            }
        )

    stats_rows = _statistics_rows(initial_metrics, final_metrics)
    write_csv(output_dir / "ion_parameter_fit_values.csv", values_rows)
    write_csv(output_dir / "ion_parameter_fit_statistics.csv", stats_rows)
    write_csv(output_dir / "ion_parameter_speciation_fit_data.csv", plotted)
    pressure_stub = pd.DataFrame(
        [
            {
                "note": "Pressure parity is intentionally not regenerated by the speciation-only ion-parameter fit. "
                "Run the full ionic pressure renderer after promoting a final ion fit.",
            }
        ]
    )
    write_csv(output_dir / "ion_parameter_pressure_fit_data.csv", pressure_stub)
    _write_sidecar(output_dir / "meah_meacoo_speciation_parity.mpl.yaml", "meah_meacoo_speciation_parity")
    _write_sidecar(output_dir / "meah_meacoo_loading_curves.mpl.yaml", "meah_meacoo_loading_curves")
    _write_sidecar(output_dir / "ion_parameter_pressure_parity.mpl.yaml", "ion_parameter_pressure_parity")
    speciation_plot = plot_speciation_parity(plotted, output_dir)
    loading_plot = plot_loading_curves(plotted, output_dir)
    pressure_plot = plot_pressure_placeholder(output_dir)

    summary = {
        "fit_tier": "tier_a_local_speciation",
        "source_manifest": "data/reference/MEA/ion_parameter_regression_sources.csv",
        "target_sources": sorted({target.source for target in targets}),
        "target_row_count": len(targets),
        "target_residual_count": int(len(final_frame)),
        "fit_parameters": list(FIT_NAMES),
        "optimizer": {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "nfev": int(result.nfev),
            "cost": float(result.cost),
            "initial_residual_norm": float(np.linalg.norm(initial_residuals)),
            "final_residual_norm": float(np.linalg.norm(final_residuals)),
        },
        "initial_values": {name: float(value) for name, value in zip(FIT_NAMES, x0)},
        "fitted_values": {name: float(fitted_values[name]) for name in FIT_NAMES},
        "parameters_at_bounds": at_bounds,
        "initial_metrics": initial_metrics,
        "final_metrics": final_metrics,
        "artifacts": {
            "values_csv": str(output_dir / "ion_parameter_fit_values.csv"),
            "statistics_csv": str(output_dir / "ion_parameter_fit_statistics.csv"),
            "speciation_fit_data_csv": str(output_dir / "ion_parameter_speciation_fit_data.csv"),
            "pressure_fit_data_csv": str(output_dir / "ion_parameter_pressure_fit_data.csv"),
            "speciation_plot_png": str(speciation_plot),
            "speciation_plot_svg": str(speciation_plot.with_suffix(".svg")),
            "loading_curves_png": str(loading_plot),
            "loading_curves_svg": str(loading_plot.with_suffix(".svg")),
            "pressure_plot_png": str(pressure_plot),
            "pressure_plot_svg": str(pressure_plot.with_suffix(".svg")),
        },
        "claim_boundary": (
            "This fit proves the MEAH+/MEACOO- parameters are optimized against real Tier A liquid-speciation data. "
            "It is not by itself the final full VLE pressure regression; pressure parity must be regenerated with the promoted parameter set."
        ),
    }
    write_json(output_dir / "ion_parameter_fit_summary.json", summary)
    return summary


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


def _write_sidecar(path: Path, stem: str) -> None:
    path.write_text(
        "\n".join(
            [
                "figure:",
                f"  png: {stem}.png",
                f"  svg: {stem}.svg",
                "  dpi: 300",
                "style:",
                "  source: src/MEA/common/plot_style.py",
                "",
            ]
        ),
        encoding="utf-8",
    )


def plot_speciation_parity(frame: pd.DataFrame, output_dir: Path) -> Path:
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
    ax.set_xlabel("Observed mole fraction")
    ax.set_ylabel("Model mole fraction")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    path = output_dir / "meah_meacoo_speciation_parity.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    return path


def plot_loading_curves(frame: pd.DataFrame, output_dir: Path) -> Path:
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
    ax.set_xlabel("CO2 loading, mol CO2/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_ylim(1.0e-5, 0.3)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    path = output_dir / "meah_meacoo_loading_curves.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    return path


def plot_pressure_placeholder(output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        "Pressure parity must be regenerated\nwith the promoted full ionic VLE workflow.",
        ha="center",
        va="center",
    )
    path = output_dir / "ion_parameter_pressure_parity.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
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
