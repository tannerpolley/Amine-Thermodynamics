"""Presentation only: source comparisons from retained stage-2 values."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

AN = Path(__file__).resolve().parent


def rows(name):
    return list(csv.DictReader((AN / "results" / name).open()))


def calculate():
    cal = rows("binary-calibration-residuals.csv")
    hill = rows("binary-hilliard.csv")
    den = rows("binary-density.csv")
    used = [r for r in cal if r["role"] == "calibration"]
    summary = {}
    for key in ["P_source_units", "y_source_units"]:
        a = np.array([float(r[key]) for r in used])
        summary[key] = dict(
            mean=float(a.mean()),
            rms=float(np.sqrt(np.mean(a * a))),
            minimum=float(a.min()),
            maximum=float(a.max()),
            within_one=int(sum(abs(a) <= 1)),
        )
    summary["Hilliard"] = {}
    for label, group in [
        ("all", hill),
        ("below_2Pa", [r for r in hill if r["below_2Pa"] == "True"]),
        ("at_least_2Pa", [r for r in hill if r["below_2Pa"] == "False"]),
        ("below_313K", [r for r in hill if r["below_313K"] == "True"]),
    ]:
        summary["Hilliard"][label] = dict(
            count=len(group),
            bias_Pa=float(np.mean([float(r["difference_Pa"]) for r in group])),
            AARD_percent=float(
                np.mean([abs(float(r["relative_percent"])) for r in group])
            ),
        )
    summary["density"] = {}
    for label, group in [
        (s, [r for r in den if r["source"] == s])
        for s in ["Concepcion2020", "Friis2025"]
    ]:
        summary["density"][label] = dict(
            count=len(group),
            bias_kg_m3=float(np.mean([float(r["difference_kg_m3"]) for r in group])),
            difference_range_kg_m3=[
                min(float(r["difference_kg_m3"]) for r in group),
                max(float(r["difference_kg_m3"]) for r in group),
            ],
            source_unit_range=[
                min(float(r["source_units"]) for r in group),
                max(float(r["source_units"]) for r in group),
            ],
        )
    (AN / "results/binary-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    table = [
        "| Hartono row | T (K) | x(PZ) | P residual / 0.3 kPa | y residual / conditional scale | Role |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    table += [
        f"| {r['row']} | {float(r['T_K']):.2f} | {float(r['x']):.4f} | {float(r['P_source_units']):+.4f} | {float(r['y_source_units']):+.4f} | {r['role']} |"
        for r in cal
    ]
    table += [
        "",
        "| Concepción T (K) | Measured density (kg/m³) | Model density (kg/m³) | Difference (kg/m³) | Difference / 0.7 kg/m³ | Fluid phase |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    table += [
        f"| {float(r['T_K']):.2f} | {float(r['rho_kg_m3']):.1f} | {float(r['predicted_kg_m3']):.4f} | {float(r['difference_kg_m3']):+.4f} | {float(r['source_units']):+.3f} | {'passed trials' if r['fluid_phase_passed'] == 'True' else 'metastable liquid'} |"
        for r in den
        if r["source"] == "Concepcion2020"
    ]
    (AN / "results/binary-tables.md").write_text("\n".join(table) + "\n")
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), layout="constrained")
    colors = ["#0072B2", "#D55E00", "#009E73"]
    for T, color in zip([333.15, 353.15, 373.15], colors):
        group = [r for r in used if abs(float(r["T_K"]) - T) < 1]
        x = [float(r["x"]) for r in group]
        for ax, obs, pred, err in [
            (axes[0, 0], "P_kPa", "predicted_P_kPa", 0.3),
            (axes[0, 1], "y", "predicted_y", None),
        ]:
            errors = (
                err
                if err
                else [
                    np.hypot(0.01 * float(r["y"]), 0.00005 / np.sqrt(3)) for r in group
                ]
            )
            ax.errorbar(
                x,
                [float(r[obs]) for r in group],
                yerr=errors,
                fmt="o",
                color=color,
                label=f"{T:.0f} K measured",
                ms=4,
                capsize=2,
            )
            ax.scatter(
                x,
                [float(r[pred]) for r in group],
                marker="x",
                color=color,
                label=f"{T:.0f} K model",
                s=26,
            )
    axes[0, 0].set(
        xlabel="Liquid PZ mole fraction",
        ylabel="Total pressure (kPa)",
        title="Hartono calibration: pressure systematically low",
    )
    axes[0, 1].set(
        xlabel="Liquid PZ mole fraction",
        ylabel="Vapor PZ mole fraction",
        title="Hartono calibration: composition pattern not fitted",
    )
    for ax in axes[0, :2]:
        ax.legend(fontsize=7, ncol=2)
    ax = axes[0, 2]
    for key, marker, color, label in [
        ("pPZ_Pa", "o", "#0072B2", "Hilliard D.2"),
        ("predicted_pPZ_Pa", "x", "#D55E00", "Frozen model"),
    ]:
        ax.scatter(
            [float(r["T_K"]) for r in hill],
            [float(r[key]) for r in hill],
            marker=marker,
            color=color,
            s=22,
            label=label,
        )
    ax.set(
        xlabel="Temperature (K)",
        ylabel="PZ partial pressure (Pa)",
        title="Independent volatility comparison",
    )
    ax.legend(fontsize=8)
    ax = axes[1, 0]
    group = [r for r in den if r["source"] == "Concepcion2020"]
    ax.axhspan(-0.7, 0.7, color="0.9", label="Expanded uncertainty bound")
    for r in group:
        ax.scatter(
            float(r["T_K"]),
            float(r["difference_kg_m3"]),
            marker="o" if r["fluid_phase_passed"] == "True" else "x",
            color="#0072B2",
        )
    ax.set(
        xlabel="Temperature (K)",
        ylabel="Model − measured density (kg/m³)",
        title="Concepción, w(PZ)=0.1001, 0.1 MPa",
    )
    ax.legend(fontsize=8)
    ax = axes[1, 1]
    group = [r for r in den if r["source"] == "Friis2025"]
    for T in sorted({float(r["T_K"]) for r in group}):
        g = [r for r in group if float(r["T_K"]) == T]
        ax.scatter(
            [100 * float(r["w_PZ"]) for r in g],
            [float(r["difference_kg_m3"]) for r in g],
            label=f"{T:.0f} K",
            s=20,
        )
    ax.set(
        xlabel="PZ mass fraction (%)",
        ylabel="Model − measured density (kg/m³)",
        title="Friis: density underprediction grows with concentration",
    )
    ax.legend(fontsize=7, ncol=2)
    ax = axes[1, 2]
    r = json.loads((AN / "results/binary-calibration.json").read_text())["starts"][0]
    text = f"k₀ = {r['values'][0]:.7f} ± {r['information']['se'][0]:.7f}\nk₁ = {r['values'][1]:.7f} ± {r['information']['se'][1]:.7f} K⁻¹\n\nConditional local SE only.\n23/23 calibration phase trials pass.\n393.15 K Concepción state: vapor instability.\nHilliard source scales unavailable.\nFriis ± meaning unresolved.\nNo endpoint adoption or solid qualification."
    ax.text(0.02, 0.95, text, va="top", fontsize=10, transform=ax.transAxes)
    ax.axis("off")
    fig.suptitle(
        "PZ–water: numerical calibration converges; source agreement remains poor",
        fontsize=15,
    )
    fig.savefig(AN / "figures/binary-comparisons.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    calculate()
