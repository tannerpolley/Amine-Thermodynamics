from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results"
FIGURES = ANALYSIS / "figures"
# Same reproducible-output settings as MEA.common.plot_style.save_figure_bundle.
plt.rcParams["svg.hashsalt"] = "MEA-Thermodynamics"
REPRODUCIBLE = {"svg": {"Date": None}, "pdf": {"CreationDate": None, "ModDate": None}}


def rows() -> list[dict[str, str]]:
    with (RESULTS / "predictions.csv").open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    values = rows()
    temperatures = sorted({float(row["temperature_k"]) for row in values})
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.0), constrained_layout=True)
    for axis, temperature in zip(axes.flat, temperatures, strict=True):
        selected = [row for row in values if float(row["temperature_k"]) == temperature]
        x = [float(row["liquid_co2_mole_fraction"]) for row in selected]
        observed = [float(row["observed_pressure_kpa"]) for row in selected]
        model = [float(row["model_pressure_kpa"]) for row in selected]
        axis.scatter(x, observed, color="#222222", marker="o", label="Kiepe data", zorder=3)
        axis.plot(x, model, color="#0072B2", marker="s", label="Pabsch model")
        axis.set_yscale("log")
        axis.set_title(f"T = {temperature:.2f} K")
        axis.set_xlabel("Liquid CO$_2$ mole fraction")
        axis.set_ylabel("Total pressure (kPa)")
        axis.grid(alpha=0.25)
        axis.legend(frameon=False)
    fig.suptitle("CO$_2$–water coexistence with fixed induced association", fontsize=16)
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"co2_water_induced_association.{suffix}", dpi=220, metadata=REPRODUCIBLE.get(suffix))
    plt.close(fig)


if __name__ == "__main__":
    main()
