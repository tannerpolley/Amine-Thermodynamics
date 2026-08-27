from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from MEA.common.analysis_io import read_csv_rows as _read


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/independent_evidence_comparison"
FIGURES = ANALYSIS / "figures"


def main() -> None:
    metrics = _read(RESULTS / "domain_metrics.csv")
    threshold = _read(RESULTS / "preference_threshold.csv")
    profiles = _read(RESULTS / "priority_profiles.csv")
    labels = {
        "pressure_challenge": "Pressure\nchallenge",
        "reserved_speciation": "Reserved\nspeciation",
        "calorimetry": "Calorimetry",
    }

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.5))
    x = list(range(len(metrics)))
    ratios = [float(row["balanced_to_retained_error_ratio"]) for row in metrics]
    axes[0].axhline(1.0, color="black", linewidth=1.5, label="Retained reference")
    axes[0].scatter(x, ratios, color="#0072B2", marker="o", s=65, label="Calorimetry-balanced")
    for coordinate, ratio in zip(x, ratios, strict=True):
        axes[0].annotate(f"{ratio:.3f}", (coordinate, ratio), xytext=(0, 8), textcoords="offset points", ha="center")
    axes[0].set_xticks(x, [labels[row["domain"]] for row in metrics])
    axes[0].set_ylabel("Error relative to retained set")
    axes[0].set_ylim(0.58, 1.10)
    axes[0].set_title("Independent-domain error ratios")
    axes[0].grid(axis="y", alpha=0.22)
    axes[0].legend(frameon=False, fontsize=8)

    pressure_share = [float(row["pressure_share_of_non_speciation_weight"]) for row in threshold]
    speciation_limit = [float(row["maximum_speciation_weight_preferring_balanced"]) for row in threshold]
    axes[1].fill_between(pressure_share, 0, speciation_limit, color="#56B4E9", alpha=0.35)
    axes[1].fill_between(pressure_share, speciation_limit, 1, color="0.85", alpha=0.55)
    axes[1].plot(pressure_share, speciation_limit, color="#0072B2", linewidth=2, label="Equal-score boundary")
    for row in profiles:
        non_speciation_weight = 1 - float(row["reserved_speciation_weight"])
        x_value = float(row["pressure_weight"]) / non_speciation_weight
        y_value = float(row["reserved_speciation_weight"])
        axes[1].scatter(x_value, y_value, marker="x", color="black", s=48)
    equal = profiles[0]
    axes[1].annotate(
        "equal domains",
        (float(equal["pressure_weight"]) / (1 - float(equal["reserved_speciation_weight"])), float(equal["reserved_speciation_weight"])),
        xytext=(8, -16),
        textcoords="offset points",
        fontsize=8,
    )
    axes[1].text(0.03, 0.08, "balanced preferred", color="#0072B2", transform=axes[1].transAxes)
    axes[1].text(0.03, 0.94, "retained preferred", color="0.25", transform=axes[1].transAxes)
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("Pressure share of non-speciation weight")
    axes[1].set_ylabel("Reserved-speciation weight")
    axes[1].set_title("Sensitivity to engineering priorities")
    axes[1].grid(alpha=0.18)

    fig.suptitle("Retained versus calorimetry-balanced MEA parameter set")
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    plotted = [
        {
            "series": "domain_error_ratio",
            "x": row["domain"],
            "y": row["balanced_to_retained_error_ratio"],
        }
        for row in metrics
    ] + [
        {
            "series": "equal_score_boundary",
            "x": row["pressure_share_of_non_speciation_weight"],
            "y": row["maximum_speciation_weight_preferring_balanced"],
        }
        for row in threshold
    ]
    with (FIGURES / "independent_evidence_comparison_plot_data.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=("series", "x", "y"))
        writer.writeheader()
        writer.writerows(plotted)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"independent_evidence_comparison.{suffix}", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()
