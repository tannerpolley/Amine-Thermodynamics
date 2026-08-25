from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/broader_candidate"
FIGURES = ANALYSIS / "figures"
COLORS = {
    "baseline_7_01": "#0072B2",
    "selected_ion_specific": "#D55E00",
    "selected_water_temperature": "#009E73",
}
LABELS = {
    "baseline_7_01": "Remaining ions 7.01",
    "selected_ion_specific": "Selected ion-specific set",
    "selected_water_temperature": "Selected + water ε(T)",
}


def _read(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(FIGURES / f"{stem}.{suffix}", dpi=220)


def _pressure() -> None:
    rows = _read("pressure_comparison.csv")
    temperatures = (40.0, 60.0, 80.0, 100.0, 120.0)
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.4), sharex=True, sharey=True)
    for axis, temperature in zip(axes.flat, temperatures, strict=False):
        observed = sorted(
            (row for row in rows if float(row["temperature_c"]) == temperature and row["configuration_id"] == "baseline_7_01"),
            key=lambda row: float(row["co2_loading_mol_per_mol_mea"]),
        )
        axis.scatter(
            [float(row["co2_loading_mol_per_mol_mea"]) for row in observed],
            [float(row["observed_pco2_pa"]) / 1000.0 for row in observed],
            color="black",
            facecolor="white",
            marker="o",
            s=42,
            label="Observed" if temperature == temperatures[0] else None,
            zorder=3,
        )
        for configuration_id, color in COLORS.items():
            selected = sorted(
                (row for row in rows if float(row["temperature_c"]) == temperature and row["configuration_id"] == configuration_id and row["status"] == "evaluated"),
                key=lambda row: float(row["co2_loading_mol_per_mol_mea"]),
            )
            axis.plot(
                [float(row["co2_loading_mol_per_mol_mea"]) for row in selected],
                [float(row["co2_liquid_fugacity_pa"]) / 1000.0 for row in selected],
                color=color,
                marker=".",
                label=LABELS[configuration_id] if temperature == temperatures[0] else None,
            )
        axis.set_yscale("log")
        axis.set_title(f"{temperature:g} °C")
        axis.grid(alpha=0.22)
    axes.flat[-1].axis("off")
    for axis in axes[-1, :2]:
        axis.set_xlabel("CO$_2$ loading (mol CO$_2$ mol$^{-1}$ MEA)")
    for axis in axes[:, 0]:
        axis.set_ylabel("CO$_2$ partial pressure equivalent (kPa)")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.96, 0.10), frameon=False)
    fig.suptitle("Fixed-pressure liquid-fugacity screen across 30 wt% MEA observations")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _save(fig, "broader_candidate_pressure")
    plt.close(fig)


def _dielectric() -> None:
    rows = _read("dielectric_comparison.csv")
    loadings = (0.22, 0.33, 0.44, 0.55)
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.5), sharex=True, sharey=True)
    for axis, loading in zip(axes.flat, loadings, strict=True):
        observed = sorted(
            (row for row in rows if float(row["co2_loading_mol_per_mol_mea"]) == loading and row["configuration_id"] == "baseline_7_01"),
            key=lambda row: float(row["temperature_c"]),
        )
        axis.scatter(
            [float(row["temperature_c"]) for row in observed],
            [float(row["fitted_static_relative_permittivity"]) for row in observed],
            color="black",
            facecolor="white",
            s=42,
            label="Hajj fitted static limit" if loading == loadings[0] else None,
            zorder=3,
        )
        for configuration_id, color in COLORS.items():
            selected = sorted(
                (row for row in rows if float(row["co2_loading_mol_per_mol_mea"]) == loading and row["configuration_id"] == configuration_id and row["status"] == "evaluated"),
                key=lambda row: float(row["temperature_c"]),
            )
            axis.plot(
                [float(row["temperature_c"]) for row in selected],
                [float(row["bulk_relative_permittivity"]) for row in selected],
                color=color,
                marker=".",
                label=LABELS[configuration_id] if loading == loadings[0] else None,
            )
        axis.set_title(f"Loading = {loading:.2f}")
        axis.grid(alpha=0.22)
    for axis in axes[-1, :]:
        axis.set_xlabel("Temperature (°C)")
    for axis in axes[:, 0]:
        axis.set_ylabel("Relative permittivity (-)")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.94), ncol=4, frameon=False)
    fig.suptitle("30 wt% loaded-MEA permittivity: EOS versus Hajj Cole–Cole fit", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    _save(fig, "broader_candidate_dielectric")
    plt.close(fig)


def main() -> None:
    _pressure()
    _dielectric()


if __name__ == "__main__":
    main()
