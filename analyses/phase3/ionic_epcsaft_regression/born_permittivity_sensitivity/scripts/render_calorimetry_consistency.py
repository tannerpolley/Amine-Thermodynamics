from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/calorimetry_consistency"
FIGURES = ANALYSIS / "figures"


def _read(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    curve = _read("model_heat_curve.csv")
    observations = [
        row
        for row in _read("calorimetry_comparison.csv")
        if row["status"] == "evaluated" and row["configuration"] == "retained"
    ]
    fig, axis = plt.subplots(figsize=(8.4, 5.2))
    for configuration, color, label in (
        ("retained", "black", "Retained ePC-SAFT"),
        ("joint_r4_r5_temperature_candidate", "#E69F00", "R4/R5 temperature candidate"),
        ("calorimetry_balanced_exact", "#56B4E9", "Calorimetry-balanced candidate"),
    ):
        selected = [row for row in curve if row["configuration"] == configuration]
        axis.plot(
            [float(row["loading"]) for row in selected],
            [float(row["model_heat_release_kj_per_mol_co2"]) for row in selected],
            color=color,
            linewidth=2.0,
            label=f"{label} Gibbs–Helmholtz curve",
        )
    styles = {
        ("Kim and Svendsen 2007", 313.15): ("o", "#0072B2"),
        ("Kim and Svendsen 2007", 353.15): ("s", "#D55E00"),
        ("Kim et al. 2014", 313.15): ("^", "#009E73"),
        ("Kim et al. 2014", 353.15): ("D", "#CC79A7"),
    }
    for (source, temperature_k), (marker, color) in styles.items():
        selected = [
            row
            for row in observations
            if row["source"] == source
            and float(row["temperature_k"]) == temperature_k
        ]
        axis.scatter(
            [float(row["loading"]) for row in selected],
            [float(row["observed_heat_release_kj_per_mol_co2"]) for row in selected],
            marker=marker,
            color=color,
            label=f"{source}, {temperature_k - 273.15:.0f} °C",
            alpha=0.82,
        )
    axis.set_xlabel("CO$_2$ loading (mol mol$^{-1}$ MEA)")
    axis.set_ylabel("Heat release magnitude (kJ mol$^{-1}$ CO$_2$)")
    axis.set_title("30 wt% MEA calorimetry consistency")
    axis.grid(alpha=0.22)
    axis.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"calorimetry_consistency.{suffix}", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()
