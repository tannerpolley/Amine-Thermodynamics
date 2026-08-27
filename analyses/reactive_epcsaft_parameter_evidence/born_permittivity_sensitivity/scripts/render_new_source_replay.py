from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/new_source_replay"
FIGURES = ANALYSIS / "figures"


def main() -> None:
    with (RESULTS / "predictions.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    temperatures = sorted({float(row["temperature_k"]) for row in rows})
    fig, axes = plt.subplots(1, len(temperatures), figsize=(12.2, 4.2), sharey=True)
    styles = {
        "pressure_drop": ("o", "#0072B2", "Pressure-drop loading"),
        "raman": ("s", "#D55E00", "Raman loading"),
    }
    for axis, temperature_k in zip(axes, temperatures, strict=True):
        for basis, (marker, color, label) in styles.items():
            selected = sorted(
                (
                    row
                    for row in rows
                    if row["loading_basis"] == basis
                    and float(row["temperature_k"]) == temperature_k
                ),
                key=lambda row: float(row["loading"]),
            )
            loading = [float(row["loading"]) for row in selected]
            axis.scatter(
                loading,
                [float(row["observed_pressure_pa"]) / 100_000.0 for row in selected],
                marker=marker,
                facecolor="white",
                edgecolor=color,
                label=label if temperature_k == temperatures[0] else None,
                zorder=3,
            )
            axis.plot(
                [float(row["loading"]) for row in selected if row["status"] == "evaluated"],
                [
                    float(row["predicted_pressure_pa"]) / 100_000.0
                    for row in selected
                    if row["status"] == "evaluated"
                ],
                color=color,
                marker=marker,
                markersize=3.5,
                label=(f"Model at {label.lower()}" if temperature_k == temperatures[0] else None),
            )
        axis.set_yscale("log")
        axis.set_title(f"{temperature_k - 273.15:.0f} °C")
        axis.set_xlabel("CO$_2$ loading (mol mol$^{-1}$ MEA)")
        axis.grid(alpha=0.22)
    axes[0].set_ylabel("Total pressure (bar)")
    fig.suptitle(
        "Frozen MEA candidate against Wong et al. (2016) 10 wt% challenge",
        y=0.99,
    )
    fig.legend(loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.79))
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"new_source_wong2016_replay.{suffix}", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()
