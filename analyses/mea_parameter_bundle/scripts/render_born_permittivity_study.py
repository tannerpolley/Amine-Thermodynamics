"""Render retained Born/permittivity comparison outputs without rerunning the model."""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/born-permittivity-study"
OUTPUT = ANALYSIS / "figures/born_permittivity/output"
STATE_PACKET = ANALYSIS / "data/input/state-packet.json"
sys.path.insert(0, str(ROOT / "src"))

from MEA.common.analysis_io import file_sha256, repo_relative_path  # noqa: E402
from MEA.common.plot_style import (  # noqa: E402
    apply_plot_theme,
    save_figure_bundle,
    write_mpl_sidecar,
)


COLORS = {
    "A-ORG": "#006D8F",
    "D-ORG": "#B45309",
    "E-SSMDS": "#7E22CE",
    "E-SSMDS-f1.4": "#7A9E2C",
    "E-SSMDS-f1.5": "#2E8B57",
    "E-SSMDS-f1.6": "#1D6F42",
    "E-SSMDS-f1.6-noCO2": "#334155",
    "I-SSMDS": "#B42318",
}
LABELS = {
    "A-ORG": "Solvent-only mass fraction + original Born",
    "D-ORG": "Combined solvent-mass/ion-mole + original Born",
    "E-SSMDS": "Nonlinear suppression + SSM+DS, $f_{MEA}=1.0$",
    "E-SSMDS-f1.4": "Nonlinear suppression + SSM+DS, $f_{MEA}=1.4$",
    "E-SSMDS-f1.5": "Nonlinear suppression + SSM+DS, $f_{MEA}=1.5$",
    "E-SSMDS-f1.6": "Nonlinear suppression + SSM+DS, $f_{MEA}=1.6$",
    "E-SSMDS-f1.6-noCO2": "Nonlinear suppression + SSM+DS, $f_{MEA}=1.6$, CO$_2$ omitted from both pools",
    "I-SSMDS": "Ion-specific analog/fallback $\\alpha_i$ + SSM+DS",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def save(fig, stem: str, title: str, description: str, data: Path) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    png, svg, pdf = save_figure_bundle(fig, OUTPUT / stem)
    write_mpl_sidecar(
        OUTPUT / f"{stem}.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=data,
    )
    with (OUTPUT / f"{stem}.mpl.yaml").open("a", encoding="utf-8") as stream:
        stream.write(f"source_path: {repo_relative_path(data)}\n")
        stream.write(f"source_sha256: {file_sha256(data)}\n")
        stream.write("continuity: discrete Engine evaluations; no interpolation\n")
    plt.close(fig)


def grouped_statistics(targets: list[dict[str, str]]) -> Path:
    grouped: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in targets:
        if not row["log10_predicted_over_observed"]:
            continue
        error = float(row["log10_predicted_over_observed"])
        for kind, value in (
            ("overall", "all"),
            ("temperature_C", row["temperature_C"]),
            ("source", row["source"] or "not-declared"),
            ("target", row["target"]),
        ):
            grouped[(row["variant"], row["family"], kind, value)].append(error)
    output = []
    for (variant, family, kind, group), values in sorted(grouped.items()):
        output.append(
            {
                "variant": variant,
                "family": family,
                "group_type": kind,
                "group": group,
                "n": len(values),
                "log10_rmse": math.sqrt(
                    statistics.fmean(value * value for value in values)
                ),
                "median_factor": 10
                ** statistics.median(abs(value) for value in values),
                "mean_log10_bias": statistics.fmean(values),
            }
        )
    path = RESULTS / "full-grouped-residual-statistics.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=tuple(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)
    return path


def factorial_effects() -> Path:
    sparse = {row["variant"]: row for row in rows(RESULTS / "sparse-summary.csv")}
    output = []
    for rule in "ABCDE":
        original = sparse[f"{rule}-ORG"]
        corrected = sparse[f"{rule}-SSMDS"]
        output.append(
            {
                "rule": rule,
                "evaluated_state_change": int(corrected["evaluated_states"])
                - int(original["evaluated_states"]),
                "pressure_log10_rmse_change": float(corrected["pressure_log10_rmse"])
                - float(original["pressure_log10_rmse"]),
                "speciation_log10_rmse_change": float(
                    corrected["speciation_log10_rmse"]
                )
                - float(original["speciation_log10_rmse"]),
            }
        )
    path = RESULTS / "sparse-factorial-effects.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=tuple(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)
    return path


def failure_characterization(states: list[dict[str, str]]) -> Path:
    output = []
    for row in states:
        if row["status"] == "evaluated":
            continue
        diagnostic = row["failure_diagnostic"]
        if diagnostic == "bubble Newton iteration limit reached":
            stage = "bubble-pressure-iteration"
            interpretation = "pressure_coupling_robustness_failure"
        elif "certificate_failed" in diagnostic:
            stage = "candidate-certification"
            interpretation = "candidate_not_certified_no_physical_absence_inference"
        else:
            stage = "equilibrium-solve"
            interpretation = "inner_solver_execution_failure"
        output.append(
            {
                "variant": row["variant"],
                "observation_id": row["observation_id"],
                "family": row["family"],
                "temperature_C": row["temperature_C"],
                "loading": row["loading"],
                "source": row["source"] or "not-declared",
                "failure_code": row["failure_code"],
                "failure_diagnostic": diagnostic,
                "failure_stage": stage,
                "scientific_interpretation": interpretation,
                "continuation_present": row["continuation_present"],
                "liquid_start_present": row["liquid_start_present"],
                "pressure_start_count": row["pressure_start_count"],
            }
        )
    path = RESULTS / "full-failure-characterization.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=tuple(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)
    return path


def common_row_statistics(targets: list[dict[str, str]]) -> Path:
    variants = set(COLORS)
    evaluated: dict[tuple[str, str, str], dict[str, float]] = defaultdict(dict)
    for row in targets:
        if row["log10_predicted_over_observed"]:
            key = (row["family"], row["observation_id"], row["target"])
            evaluated[key][row["variant"]] = float(
                row["log10_predicted_over_observed"]
            )
    common = {key: values for key, values in evaluated.items() if set(values) == variants}
    output = []
    for family in ("pressure", "speciation"):
        for variant in COLORS:
            errors = [
                values[variant]
                for key, values in common.items()
                if key[0] == family
            ]
            output.append(
                {
                    "family": family,
                    "variant": variant,
                    "common_positive_targets": len(errors),
                    "log10_rmse": math.sqrt(
                        statistics.fmean(error * error for error in errors)
                    ),
                    "median_factor": 10
                    ** statistics.median(abs(error) for error in errors),
                    "mean_log10_bias": statistics.fmean(errors),
                }
            )
    path = RESULTS / "full-common-row-statistics.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    return path


def overview(summary: list[dict[str, str]], states: list[dict[str, str]]) -> None:
    apply_plot_theme()
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.1))
    for row in summary:
        variant = row["variant"]
        axes[0].scatter(
            float(row["pressure_log10_rmse"]),
            float(row["speciation_log10_rmse"]),
            color=COLORS[variant],
            s=60,
            label=LABELS[variant],
        )
    axes[0].set(
        xlabel="Pressure log$_{10}$ RMSE",
        ylabel="Speciation log$_{10}$ RMSE",
        title="Fit trade-off",
    )
    axes[0].grid(alpha=0.22)

    variants = [row["variant"] for row in summary]
    evaluated = [float(row["evaluated_states"]) for row in summary]
    attempted = [float(row["attempted_states"]) for row in summary]
    axes[1].barh(
        variants,
        [100 * a / b for a, b in zip(evaluated, attempted, strict=True)],
        color=[COLORS[v] for v in variants],
    )
    axes[1].set(
        xlim=(0, 102),
        xlabel="Evaluated attempts (%)",
        title="Solver outcome (descriptive)",
    )
    axes[1].grid(axis="x", alpha=0.22)

    for variant in variants:
        selected = [
            row
            for row in states
            if row["variant"] == variant and row["status"] == "evaluated"
        ]
        axes[2].scatter(
            [float(row["loading"]) for row in selected],
            [float(row["bulk_relative_permittivity"]) for row in selected],
            s=11,
            alpha=0.45,
            color=COLORS[variant],
        )
    reference = [
        row
        for row in states
        if row["variant"] == "A-ORG" and row["status"] == "evaluated"
    ]
    axes[2].scatter(
        [float(row["loading"]) for row in reference],
        [float(row["figiel_reference_permittivity"]) for row in reference],
        s=12,
        facecolors="none",
        edgecolors="#333333",
        alpha=0.55,
        label="Nonlinear suppression at solved compositions",
    )
    axes[2].set(
        xlabel="CO$_2$ loading (mol mol$^{-1}$ MEA)",
        ylabel="Bulk $\\epsilon_r$",
        title="Permittivity response",
    )
    axes[2].grid(alpha=0.22)
    axes[2].legend(fontsize=7)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=4,
        fontsize=8,
        bbox_to_anchor=(0.5, -0.08),
    )
    fig.suptitle("Fixed-parameter Born–permittivity comparison")
    fig.tight_layout()
    save(
        fig,
        "born-permittivity-overview",
        "Fixed-parameter Born–permittivity comparison",
        "Pressure/speciation error, descriptive evaluated-attempt fraction, and predicted bulk relative permittivity for every promoted configuration; the attempt fraction is not a formulation-ranking criterion.",
        RESULTS / "full-summary.csv",
    )


def residuals(targets: list[dict[str, str]]) -> None:
    apply_plot_theme()
    fig, axes = plt.subplots(2, 1, figsize=(10.2, 7.3), sharex=True)
    for axis, family in zip(axes, ("pressure", "speciation"), strict=True):
        for variant, color in COLORS.items():
            selected = [
                row
                for row in targets
                if row["variant"] == variant
                and row["family"] == family
                and row["log10_predicted_over_observed"]
            ]
            axis.scatter(
                [float(row["loading"]) for row in selected],
                [float(row["log10_predicted_over_observed"]) for row in selected],
                color=color,
                s=12,
                alpha=0.42,
                label=LABELS[variant],
            )
        axis.axhline(0, color="#333333", linewidth=1)
        axis.set_ylabel("log$_{10}$(model / data)")
        axis.set_title(f"{family.capitalize()} residuals")
        axis.grid(alpha=0.2)
    axes[-1].set_xlabel("CO$_2$ loading (mol mol$^{-1}$ MEA)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=4,
        fontsize=8,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(
        fig,
        "born-permittivity-residuals",
        "Born–permittivity residual patterns",
        "All positive retained pressure and speciation residuals by loading; temperature, source, and species summaries are retained separately in CSV.",
        RESULTS / "full-targets.csv",
    )


def grouped_residuals(grouped: list[dict[str, str]]) -> None:
    def panel(axis, family: str, group_type: str, title: str) -> None:
        selected = [
            row
            for row in grouped
            if row["family"] == family and row["group_type"] == group_type
        ]
        groups = sorted(
            {row["group"] for row in selected},
            key=lambda value: float(value) if group_type == "temperature_C" else value,
        )
        values = np.full((len(COLORS), len(groups)), np.nan)
        for row in selected:
            values[list(COLORS).index(row["variant"]), groups.index(row["group"])] = (
                float(row["log10_rmse"])
            )
        image = axis.imshow(values, aspect="auto", cmap="viridis_r", vmin=0)
        axis.set_xticks(range(len(groups)), groups, rotation=35, ha="right", fontsize=7)
        axis.set_yticks(range(len(COLORS)), list(COLORS), fontsize=7)
        axis.set_title(title)
        for y in range(values.shape[0]):
            for x in range(values.shape[1]):
                if math.isfinite(values[y, x]):
                    axis.text(
                        x,
                        y,
                        f"{values[y, x]:.2f}",
                        ha="center",
                        va="center",
                        fontsize=6,
                        color="white" if values[y, x] > 0.55 else "black",
                    )
        return image

    apply_plot_theme()
    fig, axes = plt.subplots(2, 2, figsize=(12.4, 8.0))
    images = [
        panel(axes[0, 0], "pressure", "temperature_C", "Pressure by temperature (°C)"),
        panel(axes[0, 1], "pressure", "source", "Pressure by source"),
        panel(
            axes[1, 0], "speciation", "temperature_C", "Speciation by temperature (°C)"
        ),
        panel(axes[1, 1], "speciation", "target", "Speciation by reported quantity"),
    ]
    fig.suptitle("Where each formulation agrees or disagrees with observations")
    fig.subplots_adjust(
        left=0.09, right=0.86, bottom=0.13, top=0.91, wspace=0.34, hspace=0.43
    )
    colorbar_axis = fig.add_axes((0.90, 0.20, 0.018, 0.60))
    fig.colorbar(images[0], cax=colorbar_axis, label="log$_{10}$ RMSE")
    save(
        fig,
        "born-permittivity-grouped-residuals",
        "Grouped Born–permittivity residuals",
        "Log10 RMSE by temperature and source for pressure, and by temperature and reported quantity for speciation.",
        RESULTS / "full-grouped-residual-statistics.csv",
    )


def diagnostics(summary: list[dict[str, str]], states: list[dict[str, str]]) -> None:
    apply_plot_theme()
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.2))
    variants = list(COLORS)
    evaluated = {
        variant: [
            row
            for row in states
            if row["variant"] == variant and row["status"] == "evaluated"
        ]
        for variant in variants
    }
    for variant in variants:
        axes[0].scatter(
            [float(row["loading"]) for row in evaluated[variant]],
            [float(row["liquid_density_mol_m3"]) / 1000 for row in evaluated[variant]],
            s=10,
            alpha=0.35,
            color=COLORS[variant],
        )
    axes[0].set(
        xlabel="CO$_2$ loading (mol mol$^{-1}$ MEA)",
        ylabel="Liquid density (kmol m$^{-3}$)",
        title="Accepted liquid branch",
    )
    axes[0].grid(alpha=0.2)

    classes = (
        ("numerical_convergence_failure", "numerical convergence", "#B45309"),
        ("physical_rejection", "candidate rejected", "#B42318"),
    )
    left = np.zeros(len(variants))
    summary_by_variant = {row["variant"]: row for row in summary}
    for failure_class, label, color in classes:
        values = [
            json.loads(summary_by_variant[variant]["failure_classes"]).get(
                failure_class, 0
            )
            for variant in variants
        ]
        axes[1].barh(variants, values, left=left, color=color, label=label)
        left += values
    axes[1].set(
        xlabel="Failed states",
        title="Preserved non-evaluable attempts",
    )
    axes[1].grid(axis="x", alpha=0.2)

    closure_fields = (
        "charge_closure_max",
        "material_balance_closure_max",
        "reaction_affinity_closure_max",
        "pressure_closure_max",
    )
    labels = ("charge", "material", "reaction", "pressure")
    x = np.arange(len(variants))
    width = 0.19
    for offset, field, label in zip(
        (-1.5, -0.5, 0.5, 1.5), closure_fields, labels, strict=True
    ):
        axes[2].bar(
            x + offset * width,
            [max(float(summary_by_variant[v][field]), 1e-20) for v in variants],
            width,
            label=label,
        )
    axes[2].set_yscale("log")
    axes[2].set_xticks(x, variants, rotation=30, ha="right")
    axes[2].set(ylabel="Maximum absolute closure", title="Solved-state closure")
    axes[2].legend(fontsize=7)
    axes[2].grid(axis="y", alpha=0.2)
    fig.suptitle("Physical branch and numerical diagnostics")
    fig.tight_layout()
    save(
        fig,
        "born-permittivity-diagnostics",
        "Physical branch and numerical diagnostics",
        "Accepted liquid density, preserved failure classes, and maximum charge, material, reaction-affinity, and pressure closure for every promoted configuration.",
        RESULTS / "full-states.csv",
    )


def contributions(states: list[dict[str, str]]) -> None:
    common = defaultdict(list)
    for row in states:
        if row["status"] == "evaluated":
            common[row["observation_id"]].append(row)
    complete = [values for values in common.values() if len(values) == len(COLORS)]
    representative = min(
        complete,
        key=lambda values: (
            abs(float(values[0]["temperature_C"]) - 40.0)
            + abs(float(values[0]["loading"]) - 0.4)
        ),
    )
    representative.sort(key=lambda row: list(COLORS).index(row["variant"]))
    apply_plot_theme()
    fig, axes = plt.subplots(1, 3, figsize=(11.8, 4.2))
    variants = [row["variant"] for row in representative]
    x = list(range(len(variants)))
    for ax, field, label, color in (
        (axes[0], "born_a_over_rt", "Born", "#7E22CE"),
        (axes[1], "debye_huckel_a_over_rt", "Debye–Hückel", "#006D8F"),
        (axes[2], "residual_a_over_rt", "Total residual", "#B45309"),
    ):
        ax.bar(
            x,
            [float(row[field]) for row in representative],
            color=color,
        )
        ax.set_xticks(x, variants, rotation=35, ha="right", fontsize=7)
        ax.set_title(label)
        ax.axhline(0, color="#333333", linewidth=0.8)
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("$a^{res}/(RT)$ contribution")
    fig.suptitle(
        f"Representative state: {representative[0]['temperature_C']} °C, loading {float(representative[0]['loading']):.3f}"
    )
    fig.tight_layout()
    save(
        fig,
        "born-permittivity-contributions",
        "Residual Helmholtz contribution comparison",
        "Born, Debye–Hückel, and total residual contributions at one common representative retained state.",
        RESULTS / "full-states.csv",
    )


def current_fast_comparison() -> None:
    """Render the current common-row comparison from the retained fast-wheel runs."""
    variants = {
        "A-ORG": "Solvent-only mixing, original Born",
        "A-AUTO": "Solvent-only mixing, SSM+DS",
        "A-AUTO-r5am80": "Solvent-only mixing, SSM+DS, R5 -80 K",
        "E-AUTO-r5ap80": "Nonlinear suppression, SSM+DS, R5 +80 K",
    }
    targets = rows(RESULTS / "corrected-reaction-full-targets.csv")
    targets.extend(rows(RESULTS / "figiel-r5-positive-full-targets.csv"))
    summaries = rows(RESULTS / "corrected-reaction-full-summary.csv")
    summaries.extend(rows(RESULTS / "figiel-r5-positive-full-summary.csv"))
    summary_by_variant = {row["variant"]: row for row in summaries}
    errors: dict[str, dict[str, dict[tuple[str, str], float]]] = {}
    for family in ("pressure", "speciation"):
        errors[family] = {
            variant: {
                (row["observation_id"], row["target"]): float(
                    row["log10_predicted_over_observed"]
                )
                for row in targets
                if row["variant"] == variant
                and row["family"] == family
                and row["log10_predicted_over_observed"]
            }
            for variant in variants
        }
    output = []
    for variant, label in variants.items():
        result = {
            "variant": variant,
            "label": label,
            "evaluated_states": int(summary_by_variant[variant]["evaluated_states"]),
            "attempted_states": int(summary_by_variant[variant]["attempted_states"]),
        }
        for family in ("pressure", "speciation"):
            common = set.intersection(
                *(set(values) for values in errors[family].values())
            )
            values = [errors[family][variant][key] for key in common]
            result[f"{family}_common_targets"] = len(values)
            result[f"{family}_log10_rmse"] = math.sqrt(
                statistics.fmean(value * value for value in values)
            )
            result[f"{family}_median_factor"] = 10 ** statistics.median(
                abs(value) for value in values
            )
            result[f"{family}_mean_log10_bias"] = statistics.fmean(values)
        output.append(result)

    data_path = RESULTS / "current-fast-common-comparison.csv"
    with data_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    apply_plot_theme()
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.8))
    y = np.arange(len(output))
    axes[0].scatter(
        [row["pressure_log10_rmse"] for row in output],
        y - 0.12,
        marker="o",
        s=65,
        color="#006D8F",
        label="CO$_2$ pressure (100 common targets)",
    )
    axes[0].scatter(
        [row["speciation_log10_rmse"] for row in output],
        y + 0.12,
        marker="s",
        s=58,
        color="#B45309",
        label="Speciation (123 common targets)",
    )
    axes[0].set_yticks(y, [row["label"] for row in output])
    axes[0].invert_yaxis()
    axes[0].set_xlabel("log$_{10}$ RMSE (lower is better)")
    axes[0].set_title("Agreement on identical observations")
    axes[0].grid(axis="x", alpha=0.22)
    axes[0].legend(fontsize=8)

    evaluated = [row["evaluated_states"] for row in output]
    axes[1].barh(y, evaluated, color="#2E8B57")
    axes[1].set_yticks(y, [row["variant"] for row in output])
    axes[1].invert_yaxis()
    axes[1].set_xlim(150, 205)
    axes[1].set_xlabel("Evaluated states out of 205")
    axes[1].set_title("Numerical coverage")
    axes[1].grid(axis="x", alpha=0.22)
    for index, value in enumerate(evaluated):
        axes[1].text(value + 1, index, str(value), va="center", fontsize=8)

    fig.suptitle(
        "R5 adjustment recovers extended-Born pressure while improving speciation"
    )
    fig.tight_layout()
    save(
        fig,
        "current-fast-born-reaction-comparison",
        "Current fast-wheel Born and reaction comparison",
        "Pressure and speciation log10 RMSE on targets shared by all four complete nine-species configurations, with evaluated-state counts shown separately.",
        data_path,
    )


def study_summary(summary: list[dict[str, str]], failures: list[dict[str, str]]) -> None:
    receipt = json.loads((RESULTS / "automatic-extended-full-receipt.json").read_text())
    automatic = rows(RESULTS / "automatic-extended-full-summary.csv")
    integer_fields = {
        "attempted_states",
        "compiled_states",
        "evaluated_states",
        "failed_states",
        "pressure_positive_targets",
        "speciation_positive_targets",
    }
    numeric_fields = (
        "attempted_states",
        "compiled_states",
        "evaluated_states",
        "failed_states",
        "pressure_positive_targets",
        "pressure_log10_rmse",
        "pressure_median_factor",
        "pressure_mean_log10_bias",
        "speciation_positive_targets",
        "speciation_log10_rmse",
        "speciation_median_factor",
        "speciation_mean_log10_bias",
        "bulk_relative_permittivity_min",
        "bulk_relative_permittivity_median",
        "bulk_relative_permittivity_max",
        "charge_closure_max",
        "material_balance_closure_max",
        "reaction_affinity_closure_max",
        "pressure_closure_max",
    )
    metrics = {
        row["variant"]: {
            field: int(row[field]) if field in integer_fields else float(row[field])
            for field in numeric_fields
        }
        for row in summary + automatic
    }
    failure_stages: dict[str, int] = defaultdict(int)
    for row in failures:
        failure_stages[row["failure_stage"]] += 1
    payload = {
        "scientific_question": "Which source-consistent Born formulation and composition-dependent relative-permittivity rule gives the best fixed-parameter reactive MEA pressure, speciation, dielectric-response, and phase-identity evidence?",
        "active_parameter_sha256": receipt["parameter_sha256"],
        "state_packet_sha256": receipt["state_packet_sha256"],
        "pressure_catalog_sha256": receipt["pressure_catalog_sha256"],
        "engine_commit": receipt["engine_commit"],
        "engine_wheel_sha256": receipt["engine_wheel_sha256"],
        "source_sha256": receipt["source_sha256"],
        "regression_performed": False,
        "full_metrics": metrics,
        "failure_stages": dict(sorted(failure_stages.items())),
        "component_permittivity_derivative_check": json.loads(
            (RESULTS / "component-permittivity-derivative-check.json").read_text()
        ),
        "engine_parity": json.loads((RESULTS / "engine-speed-parity.json").read_text()),
        "density_anchor": json.loads((RESULTS / "density-anchor-check.json").read_text()),
        "co2_pool_exclusion_preliminary": json.loads(
            (RESULTS / "co2-pool-exclusion-check.json").read_text()
        ),
        "decision": {
            "active_bundle_changed": True,
            "retained_formulation": "A-AUTO: solvent-only mass-fraction mixing with automatically activated corrected SSM+DS",
            "reason": "The populated unique Born diameters and non-unit water solvation factor are active model parameters, so redundant switches were removed. Original Born is recovered by zero Born diameters inheriting the Debye-Huckel diameters.",
            "best_speciation_error_alternative": "E-SSMDS with f_solv,MEA=1.0",
            "best_universal_figiel_pressure_alternative": "E-SSMDS with f_solv,MEA=1.6 and molecular CO2 excluded from both neutral pools",
            "coupled_co2_exclusion_effect": "Removing molecular CO2 from both f_mix and the salt-free neutral-permittivity pool changes pressure log10 RMSE from 0.389898 to 0.387514 and speciation log10 RMSE by less than 2e-7 on evaluated rows.",
            "next_experiment": "Profile the MEA solvation factor jointly with the MEAH+ and bicarbonate Born diameters, then repeat the complete comparison after the branch-aware pressure solve is available.",
        },
        "limitations": [
            "No admitted independent static-permittivity observations exist for loaded aqueous MEA in the retained data.",
            "Failed formulation-state attempts are preserved as bubble-pressure iteration, candidate-certificate, or inner-solver failures; they are not formulation evidence.",
            "The active automatic-SSM+DS replay preserves 43 failures, including 31 empty-native-policy wrapper exceptions concentrated at 120 C.",
            "The immutable fast study wheel remains installed and retained by commit and SHA-256; no slower-wheel restoration was performed.",
        ],
    }
    (RESULTS / "study-summary.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    summary = rows(RESULTS / "full-summary.csv")
    states = rows(RESULTS / "full-states.csv")
    targets = rows(RESULTS / "full-targets.csv")
    grouped_path = grouped_statistics(targets)
    grouped = rows(grouped_path)
    common_row_statistics(targets)
    factorial_effects()
    failure_path = failure_characterization(states)
    failures = rows(failure_path)
    overview(summary, states)
    residuals(targets)
    grouped_residuals(grouped)
    diagnostics(summary, states)
    contributions(states)
    current_fast_comparison()
    study_summary(summary, failures)


if __name__ == "__main__":
    main()
