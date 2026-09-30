"""Render identified retained regression rows; never import or execute the EOS."""

import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from result_freshness import FIGURE_DATA, require_results
from shared_evaluation import ENGINE_COMMIT, ENGINE_WHEEL_SHA256

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "calibration-misfit"))
from compare import HCO3_POOL_LABEL  # noqa: E402

OUT = ROOT / "figures/regression_overview/output"
FIT = ROOT / "results/current-best-fit-residuals.csv"
SUPERSEDED = ROOT / "results/reaction-temperature-fit/full-validation-targets.csv"
GRID = ROOT / "figures/speciation/output/speciation-model-grid.csv"
DISPLAY = ROOT / "figures/speciation/output/speciation-display-observations.csv"
HEAT = ROOT / "results/calorimetry/current-selected-direct-enthalpy-comparison.csv"
HEAT_SUMMARY = (
    ROOT / "results/calorimetry/current-selected-direct-enthalpy-summary.json"
)
PARAM = ROOT / "results/selected-current-best-parameters.json"
LN_STATISTICS = ROOT / "results/current-best-fit-ln-statistics.csv"
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
SOURCES = ["Aronu2011", "Hilliard2008", "Idris2014", "Jou1995", "Mamun2005", "Xu2011"]
MARKERS = dict(zip(SOURCES, ["*", "o", "D", "x", "h", "^"], strict=True))
SPECIES = ["MEA", "MEAH+", "MEA + MEAH+", "MEACOO-", HCO3_POOL_LABEL]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def ln_ratio(row):
    return math.log(float(row["predicted"]) / float(row["observed"]))


def positive(rows):
    return [
        r
        for r in rows
        if r["predicted"] and float(r["observed"]) > 0.0 and float(r["predicted"]) > 0.0
    ]


def ln_statistics(
    family, group_type, group, rows, engine=f"greenfield {ENGINE_COMMIT[:8]}"
):
    valid = positive(rows)
    errors = [ln_ratio(r) for r in valid]
    rms_ln = math.sqrt(statistics.fmean(e * e for e in errors))
    return {
        "engine": engine,
        "family": family,
        "group_type": group_type,
        "group": group,
        "attempted": len(rows),
        "evaluated_positive": len(valid),
        "mean_ln_pred_over_obs": statistics.fmean(errors),
        "rms_ln_pred_over_obs": rms_ln,
        "rmse_log10": rms_ln / math.log(10.0),
        "rms_factor": math.exp(rms_ln),
        "aard_percent": 100.0
        * statistics.fmean(abs(math.exp(e) - 1.0) for e in errors),
        "mean_difference_native_unit": statistics.fmean(
            float(r["predicted"]) - float(r["observed"]) for r in valid
        ),
    }


def ln_label(rows):
    """n, AARD, bias and RMS ln of retained residual rows, for figure text."""
    stat = ln_statistics("", "", "", rows)
    return (
        f"n = {stat['evaluated_positive']} · AARD {stat['aard_percent']:.1f} % · "
        f"bias (mean ln) {stat['mean_ln_pred_over_obs']:+.2f} · RMS ln {stat['rms_ln_pred_over_obs']:.2f}"
    )


def species_label(rows):
    stat = ln_statistics("", "", "", rows)
    return (
        f"n = {stat['evaluated_positive']}, AARD {stat['aard_percent']:.0f} %, "
        f"RMS ln {stat['rms_ln_pred_over_obs']:.2f}"
    )


def heat_label(rows):
    stat = ln_statistics(
        "",
        "",
        "",
        [
            {
                "observed": r["observed_heat_release_kj_per_mol_CO2"],
                "predicted": r["predicted_heat_release_kj_per_mol_CO2"],
            }
            for r in rows
        ],
    )
    return (
        f"n = {stat['evaluated_positive']}, AARD {stat['aard_percent']:.1f} %, "
        f"mean dev {stat['mean_difference_native_unit']:+.1f}"
    )


def short_label(rows):
    stat = ln_statistics("", "", "", rows)
    return f"n = {stat['evaluated_positive']}, AARD {stat['aard_percent']:.0f} %"


def save(fig, name):
    for ext in ("svg", "png", "pdf"):
        fig.savefig(
            OUT / f"{name}.{ext}",
            dpi=160,
            metadata={"Date": None}
            if ext == "svg"
            else {"CreationDate": None}
            if ext == "pdf"
            else {},
        )
    plt.close(fig)


def source_colors(pressure):
    present = [s for s in SOURCES if any(r["source"] == s for r in pressure)]
    return {s: COLORS[i] for i, s in enumerate(present)}


def render_isotherms(pressure, colors, title):
    temperatures = sorted({round(float(r["temperature_C"])) for r in pressure})
    fig, axes = plt.subplots(2, 3, figsize=(13, 8.6), squeeze=False)
    for ax in axes.flat[len(temperatures) :]:
        ax.set_visible(False)
    for ax, temperature in zip(axes.flat, temperatures):
        group = [r for r in pressure if round(float(r["temperature_C"])) == temperature]
        for source, color in colors.items():
            sub = [r for r in group if r["source"] == source]
            if sub:
                ax.scatter(
                    [float(r["loading_mol_CO2_per_mol_MEA"]) for r in sub],
                    [float(r["observed"]) for r in sub],
                    marker=MARKERS[source],
                    color=color,
                    s=26,
                    label=f"{source} ({short_label(sub)})",
                    facecolors="none" if MARKERS[source] in "oDh^" else color,
                )
        model = sorted(
            positive(group), key=lambda r: float(r["loading_mol_CO2_per_mol_MEA"])
        )
        ax.plot(
            [float(r["loading_mol_CO2_per_mol_MEA"]) for r in model],
            [float(r["predicted"]) for r in model],
            color="black",
            linewidth=1.1,
            linestyle="--",
            label=f"calculated ({len(model)}/{len(group)} states)",
        )
        ax.set_yscale("log")
        n_label, rest = ln_label(group).split(" · ", 1)
        ax.set_title(f"T = {temperature} °C · {n_label}\n{rest}", fontsize=9)
        ax.set_xlabel("CO₂ loading (mol/mol MEA)")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=7, frameon=False)
    axes[0, 0].set_ylabel("CO₂ partial pressure (kPa)")
    axes[1, 0].set_ylabel("CO₂ partial pressure (kPa)")
    fig.suptitle(title, fontsize=13)
    fig.text(
        0.5,
        0.012,
        "30 mass% MEA, active-v1 observations. Markers are observations; the dashed line connects "
        "adopted-record Engine states at the observed loadings (no interpolation).",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.95))
    save(fig, "pressure")


def render_parity(pressure, colors, title):
    valid = positive(pressure)
    values = [float(r[k]) for r in valid for k in ("observed", "predicted")]
    low, high = min(values) / 1.6, max(values) * 1.6
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    ax.plot([low, high], [low, high], color="black", linewidth=1.0, label="1:1")
    for factor in (2.0, 0.5):
        ax.plot(
            [low, high],
            [low * factor, high * factor],
            color="grey",
            linewidth=0.9,
            linestyle=":",
            label="factor 2" if factor == 2.0 else None,
        )
    for source, color in colors.items():
        sub = [r for r in valid if r["source"] == source]
        ax.scatter(
            [float(r["observed"]) for r in sub],
            [float(r["predicted"]) for r in sub],
            marker=MARKERS[source],
            color=color,
            s=24,
            label=f"{source} ({short_label(sub)})",
            facecolors="none" if MARKERS[source] in "oDh^" else color,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Observed CO₂ partial pressure (kPa)")
    ax.set_ylabel("Calculated CO₂ partial pressure (kPa)")
    ax.set_title(title, fontsize=11)
    stat = ln_statistics("", "", "", pressure)
    ax.text(
        0.97,
        0.03,
        f"n = {stat['evaluated_positive']}\nAARD {stat['aard_percent']:.1f} %\n"
        f"bias (mean ln) {stat['mean_ln_pred_over_obs']:+.3f}\n"
        f"RMS ln {stat['rms_ln_pred_over_obs']:.3f}\nlog₁₀ RMSE {stat['rmse_log10']:.4f}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        bbox={"facecolor": "white", "edgecolor": "0.6", "boxstyle": "round"},
    )
    ax.grid(alpha=0.18)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout()
    save(fig, "pressure-parity")


def render_residuals(pressure, colors, title):
    valid = positive(pressure)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, field, label in (
        (axes[0], "loading_mol_CO2_per_mol_MEA", "CO₂ loading (mol/mol MEA)"),
        (axes[1], "temperature_C", "Temperature (°C)"),
    ):
        for source, color in colors.items():
            sub = [r for r in valid if r["source"] == source]
            ax.scatter(
                [float(r[field]) for r in sub],
                [ln_ratio(r) for r in sub],
                marker=MARKERS[source],
                color=color,
                s=24,
                label=source,
                facecolors="none" if MARKERS[source] in "oDh^" else color,
            )
        ax.axhline(0.0, color="black", linewidth=1.0)
        for bound in (math.log(2.0), -math.log(2.0)):
            ax.axhline(bound, color="grey", linewidth=0.9, linestyle=":")
        stat = ln_statistics("", "", "", valid)
        ax.text(
            0.02,
            0.03,
            f"all rows: n = {stat['evaluated_positive']} · bias (mean ln) "
            f"{stat['mean_ln_pred_over_obs']:+.2f} · RMS ln {stat['rms_ln_pred_over_obs']:.2f}",
            transform=ax.transAxes,
            fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "0.6", "boxstyle": "round"},
        )
        ax.set_xlabel(label)
        ax.grid(alpha=0.18)
    axes[0].set_ylabel("ln(calculated / observed pCO₂)")
    axes[1].legend(fontsize=7, frameon=False)
    fig.suptitle(title, fontsize=12)
    fig.text(
        0.5,
        0.012,
        "Dotted lines mark a factor of 2. Xu 2011 was outside the reaction-temperature objective; all other rows are calibration residuals.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    save(fig, "pressure-residuals")


def model_parts(species):
    return ("MEA", "MEAH+") if species == "MEA + MEAH+" else ("HCO3-", "CO3^2-") if species == HCO3_POOL_LABEL else (species,)


def render_speciation(speciation, grid, display, title):
    temperatures = (20, 40, 60, 80)
    fig, axes = plt.subplots(2, 3, figsize=(13, 8.6), squeeze=False)
    axes.flat[-1].set_visible(False)
    by_grid = {}
    for row in grid:
        by_grid.setdefault(row["grid_id"], {})[row["species"]] = row
    for ax, species in zip(axes.flat, SPECIES):
        for color, temperature, marker in zip(COLORS, temperatures, ("o", "^", "D", "v")):
            points = [
                r
                for r in display
                if round(float(r["temperature_C"])) == temperature
                and r["species"] == species
                and float(r["observed_mole_fraction"]) > 0.0
            ]
            ax.scatter(
                [float(r["loading_mol_CO2_per_mol_MEA"]) for r in points],
                [float(r["observed_mole_fraction"]) for r in points],
                facecolors=[color if r["source"] == "Jakobsen2005" else "none" for r in points],
                edgecolors=color,
                marker=marker,
                s=26,
            )
            line = []
            for values in by_grid.values():
                parts = model_parts(species)
                if round(float(values[parts[0]]["temperature_C"])) == temperature:
                    line.append(
                        (
                            float(values[parts[0]]["loading_mol_CO2_per_mol_MEA"]),
                            sum(float(values[p]["model_mole_fraction"]) for p in parts),
                        )
                    )
            if species == HCO3_POOL_LABEL:
                physical = sorted((float(v["HCO3-"]["loading_mol_CO2_per_mol_MEA"]), float(v["HCO3-"]["model_mole_fraction"])) for v in by_grid.values() if round(float(v["HCO3-"]["temperature_C"])) == temperature)
                ax.plot([x for x, _ in physical], [y for _, y in physical], color=color, linewidth=0.8, linestyle=":", marker=marker, markevery=6, markersize=3.2, markerfacecolor="none", label=f"{temperature} °C HCO₃⁻ alone")
                separate = [r for r in display if r["species"] == "HCO3-" and round(float(r["temperature_C"])) == temperature and float(r["observed_mole_fraction"]) > 0]
                ax.scatter([float(r["loading_mol_CO2_per_mol_MEA"]) for r in separate], [float(r["observed_mole_fraction"]) for r in separate], edgecolors=color, facecolors=[color if r["source"] == "Jakobsen2005" else "none" for r in separate], marker=marker, s=20)
            line.sort()
            scored = [
                r
                for r in speciation
                if r["target"] == species
                and round(float(r["temperature_C"])) == temperature
            ]
            ax.plot(
                [x for x, _ in line],
                [y for _, y in line],
                color=color,
                linewidth=1.1,
                linestyle="--",
                marker=marker,
                markevery=6,
                markersize=3.2,
                markerfacecolor="none",
                label=f"{temperature} °C: "
                + (species_label(scored) if scored else "not scored"),
            )
        stat = ln_statistics(
            "speciation",
            "target",
            species,
            [r for r in speciation if r["target"] == species],
        )
        ax.set_title(
            f"{species} · scored n = {stat['evaluated_positive']} · "
            f"AARD {stat['aard_percent']:.1f} % · RMS ln {stat['rms_ln_pred_over_obs']:.2f}",
            fontsize=8.5,
        )
        ax.set_yscale("log")
        ax.set_xlabel("CO₂ loading (mol/mol MEA)")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=6.5, frameon=False, loc="best")
    axes[0, 0].set_ylabel("Species / aggregate mole fraction")
    axes[1, 0].set_ylabel("Species / aggregate mole fraction")
    fig.suptitle(title, fontsize=13)
    fig.text(
        0.5,
        0.012,
        "30 wt% MEA; 46 direct states per temperature. Dashed: HCO₃⁻ + CO₃²⁻ pool; dotted: HCO₃⁻ alone.\n"
        "Shapes: ○ 20, △ 40, ◇ 60, ▽ 80 °C. Open: Matin/Böttinger; filled: Jakobsen. Statistics include report-only Matin pools.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.95))
    save(fig, "speciation")


def render_heat(heat, title):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.6), squeeze=False)
    for ax, temperature in zip(axes.flat, ("40", "80", "120")):
        group = sorted(
            [r for r in heat if r["temperature_C"] == temperature],
            key=lambda r: float(r["loading_mol_CO2_per_mol_MEA"]),
        )
        for color, source in zip(COLORS, sorted({r["source"] for r in group})):
            sub = [r for r in group if r["source"] == source]
            ax.scatter(
                [float(r["loading_mol_CO2_per_mol_MEA"]) for r in sub],
                [float(r["observed_heat_release_kj_per_mol_CO2"]) for r in sub],
                facecolors="none",
                edgecolors=color,
                s=26,
            )
            calculated = [r for r in sub if r["status"] == "evaluated"]
            ax.plot(
                [float(r["loading_mol_CO2_per_mol_MEA"]) for r in calculated],
                [float(r["predicted_heat_release_kj_per_mol_CO2"]) for r in calculated],
                color=color,
                linewidth=1.1,
                linestyle="--",
                label=f"{source} calculated ({heat_label(sub)})",
            )
        ax.set_title(f"T = {temperature} °C · {heat_label(group)}", fontsize=9)
        ax.set_xlabel("CO₂ loading (mol/mol MEA)")
        ax.grid(alpha=0.18)
        ax.legend(
            fontsize=7,
            frameon=False,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.2),
        )
    axes[0, 0].set_ylabel("Heat released (kJ/mol CO₂)")
    fig.suptitle(title, fontsize=12)
    fig.text(
        0.5,
        0.012,
        "Finite-dose total-enthalpy differences on the pinned Engine's record-anchored calorics; intervals whose "
        "endpoint failed are observed only. Circles are observed intervals and dashed lines connect calculated\n"
        "intervals, one color per source. Statistics compare them: mean dev = mean(calculated − observed) in kJ/mol CO₂.",
        ha="center",
        fontsize=8,
    )
    fig.subplots_adjust(left=0.06, right=0.98, top=0.86, bottom=0.34, wspace=0.25)
    save(fig, "heat")


def main():
    require_results(FIGURE_DATA)
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {"font.family": "DejaVu Sans", "svg.hashsalt": "mea-regression-overview"}
    )
    fit = read(FIT)
    pressure = [r for r in fit if r["family"] == "pressure"]
    speciation = [r for r in fit if r["family"] == "speciation"]
    colors = source_colors(pressure)

    table = [ln_statistics("pressure", "overall", "all", pressure)]
    table += [
        ln_statistics(
            "pressure", "source", s, [r for r in pressure if r["source"] == s]
        )
        for s in colors
    ]
    table += [
        ln_statistics(
            "pressure",
            "temperature_C",
            t,
            [r for r in pressure if round(float(r["temperature_C"])) == t],
        )
        for t in sorted({round(float(r["temperature_C"])) for r in pressure})
    ]
    table += [ln_statistics("speciation", "overall", "all", speciation)]
    table += [
        ln_statistics(
            "speciation", "target", s, [r for r in speciation if r["target"] == s]
        )
        for s in SPECIES
    ]
    # Same statistics for the superseded all-five-shift adoption replay (Engine 8438ce5f).
    superseded = [
        dict(
            r,
            loading_mol_CO2_per_mol_MEA=r["loading"],
            predicted=r["predicted"]
            if r["status"] in ("evaluated", "pivot_reuse")
            else "",
        )
        for r in read(SUPERSEDED)
        if r["family"] == "pressure"
    ]
    old = "superseded 8438ce5f candidate replay"
    table += [ln_statistics("pressure", "overall", "all", superseded, old)]
    table += [
        ln_statistics(
            "pressure", "source", s, [r for r in superseded if r["source"] == s], old
        )
        for s in colors
    ]
    with LN_STATISTICS.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)
    overall = table[0]

    render_isotherms(
        pressure,
        colors,
        f"Working-record pressure comparison "
        f"(RMS ln {overall['rms_ln_pred_over_obs']:.2f}, {overall['evaluated_positive']}/{overall['attempted']} states)",
    )
    render_parity(
        pressure,
        colors,
        f"{overall['evaluated_positive']}-state parity: RMS ln {overall['rms_ln_pred_over_obs']:.2f} "
        f"(log₁₀ {overall['rmse_log10']:.3f}, factor {overall['rms_factor']:.2f}), AARD {overall['aard_percent']:.0f}%",
    )
    render_residuals(
        pressure,
        colors,
        "Working-record pressure residuals by source and loading",
    )
    species_rms = {
        r["group"]: r["rms_ln_pred_over_obs"]
        for r in table
        if r["family"] == "speciation"
    }
    render_speciation(
        speciation,
        read(GRID),
        read(DISPLAY),
        f"Working-record species and observation-pool comparison; pool RMS ln {species_rms[HCO3_POOL_LABEL]:.2f}",
    )

    summary = json.loads(HEAT_SUMMARY.read_text())
    assert summary["engine_wheel_sha256"] == ENGINE_WHEEL_SHA256, "heat is from another Engine; regenerate it"
    heat = read(HEAT)
    assert len(heat) == 113
    render_heat(heat, "Absorption heat: 120 °C holdout remains under-predicted")

    inputs = [
        FIT,
        SUPERSEDED,
        GRID,
        DISPLAY,
        FIGURE_DATA,
        HEAT,
        HEAT_SUMMARY,
        PARAM,
        Path(__file__),
    ]
    (OUT / "provenance.json").write_text(
        json.dumps(
            {
                "inputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
                "pressure_speciation_identity": "adopted parameter record on the pinned Engine; figure-calculation record",
                "heat_identity": "adopted parameter record on the pinned Engine; current-selected-direct-enthalpy-summary.json",
                "model_executed": False,
                "series": "Speciation: temperature shapes o/^/D/v for 20/40/60/80 °C on observations and selected retained curve points; open Matin/Böttinger, filled Jakobsen; dashed modeled HCO3- + CO3^2- pool, dotted HCO3- alone. Other figures: open observation markers; dashed segments connect discrete calculations; no interpolation.",
                "outputs": {
                    p.name: digest(p)
                    for p in sorted(OUT.iterdir())
                    if p.suffix in (".csv", ".svg", ".png", ".pdf")
                },
            },
            indent=2,
        )
        + "\n"
    )
    for row in table:
        print(
            f"{row['engine'][:10]:10s} {row['family']:10s} {row['group_type']:13s} {str(row['group']):13s} "
            f"n={row['evaluated_positive']:3d}/{row['attempted']:3d} mean ln {row['mean_ln_pred_over_obs']:+.3f} "
            f"RMS ln {row['rms_ln_pred_over_obs']:.3f} log10 {row['rmse_log10']:.4f} AARD {row['aard_percent']:.1f}%"
        )


if __name__ == "__main__":
    main()
