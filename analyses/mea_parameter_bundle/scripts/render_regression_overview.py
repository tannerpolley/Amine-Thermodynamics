"""Render identified retained regression rows; never import or execute the EOS."""

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from result_freshness import FIGURE_DATA, require_results

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/regression_overview/output"
FIT = ROOT / "results/current-best-fit-residuals.csv"
SUPERSEDED = ROOT / "results/reaction-temperature-fit/full-validation-targets.csv"
GRID = ROOT / "figures/speciation/output/speciation-model-grid.csv"
DISPLAY = ROOT / "figures/speciation/output/speciation-display-observations.csv"
HEAT = ROOT / "results/calorimetry/current-selected-direct-enthalpy-comparison.csv"
HEAT_SUMMARY = ROOT / "results/calorimetry/current-selected-direct-enthalpy-summary.json"
PARAM = ROOT / "results/selected-current-best-parameters.json"
LN_STATISTICS = ROOT / "results/current-best-fit-ln-statistics.csv"
SUPERSEDED_HEAT_WHEEL = "40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805"
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
SOURCES = ["Aronu2011", "Hilliard2008", "Idris2014", "Jou1995", "Mamun2005", "Xu2011"]
MARKERS = dict(zip(SOURCES, ["*", "o", "D", "x", "h", "^"], strict=True))
SPECIES = ["MEA", "MEAH+", "MEA + MEAH+", "MEACOO-", "HCO3-"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def ln_ratio(row):
    return math.log(float(row["predicted"]) / float(row["observed"]))


def positive(rows):
    return [r for r in rows if r["predicted"] and float(r["observed"]) > 0.0 and float(r["predicted"]) > 0.0]


def ln_statistics(family, group_type, group, rows, engine="greenfield 83ac1126"):
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
        "aard_percent": 100.0 * statistics.fmean(abs(math.exp(e) - 1.0) for e in errors),
    }


def save(fig, name):
    for ext in ("svg", "png", "pdf"):
        fig.savefig(
            OUT / f"{name}.{ext}",
            dpi=160,
            metadata={"Date": None} if ext == "svg" else {"CreationDate": None} if ext == "pdf" else {},
        )
    plt.close(fig)


def source_colors(pressure):
    present = [s for s in SOURCES if any(r["source"] == s for r in pressure)]
    return {s: COLORS[i] for i, s in enumerate(present)}


def render_isotherms(pressure, colors, title):
    temperatures = sorted({round(float(r["temperature_C"])) for r in pressure})
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.6), squeeze=False)
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
                    marker=MARKERS[source], color=color, s=26, label=source,
                    facecolors="none" if MARKERS[source] in "oDh^" else color,
                )
        model = sorted(positive(group), key=lambda r: float(r["loading_mol_CO2_per_mol_MEA"]))
        ax.plot(
            [float(r["loading_mol_CO2_per_mol_MEA"]) for r in model],
            [float(r["predicted"]) for r in model],
            color="black", linewidth=1.1, linestyle="--",
            label=f"calculated ({len(model)}/{len(group)} states)",
        )
        ax.set_yscale("log")
        ax.set_title(f"{temperature} °C")
        ax.set_xlabel("CO₂ loading (mol/mol MEA)")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=7, frameon=False)
    axes[0, 0].set_ylabel("CO₂ partial pressure (kPa)")
    axes[1, 0].set_ylabel("CO₂ partial pressure (kPa)")
    fig.suptitle(title, fontsize=13)
    fig.text(
        0.5, 0.012,
        "30 mass% MEA, active-v1 observations. Markers are observations; the dashed line connects "
        "adopted-record Engine states at the observed loadings (no interpolation).",
        ha="center", fontsize=8,
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
        ax.plot([low, high], [low * factor, high * factor], color="grey", linewidth=0.9,
                linestyle=":", label="factor 2" if factor == 2.0 else None)
    for source, color in colors.items():
        sub = [r for r in valid if r["source"] == source]
        ax.scatter([float(r["observed"]) for r in sub], [float(r["predicted"]) for r in sub],
                   marker=MARKERS[source], color=color, s=24, label=f"{source} ({len(sub)})",
                   facecolors="none" if MARKERS[source] in "oDh^" else color)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Observed CO₂ partial pressure (kPa)")
    ax.set_ylabel("Calculated CO₂ partial pressure (kPa)")
    ax.set_title(title, fontsize=11)
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
            ax.scatter([float(r[field]) for r in sub], [ln_ratio(r) for r in sub],
                       marker=MARKERS[source], color=color, s=24, label=source,
                       facecolors="none" if MARKERS[source] in "oDh^" else color)
        ax.axhline(0.0, color="black", linewidth=1.0)
        for bound in (math.log(2.0), -math.log(2.0)):
            ax.axhline(bound, color="grey", linewidth=0.9, linestyle=":")
        ax.set_xlabel(label)
        ax.grid(alpha=0.18)
    axes[0].set_ylabel("ln(calculated / observed pCO₂)")
    axes[1].legend(fontsize=7, frameon=False)
    fig.suptitle(title, fontsize=12)
    fig.text(0.5, 0.012, "Dotted lines mark a factor of 2. Xu 2011 was outside the reaction-temperature objective; all other rows are calibration residuals.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    save(fig, "pressure-residuals")


def render_speciation(speciation, grid, display, title):
    temperatures = (20, 40, 60, 80)
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.6), squeeze=False)
    axes.flat[-1].set_visible(False)
    by_grid = {}
    for row in grid:
        by_grid.setdefault(row["grid_id"], {})[row["species"]] = row
    for ax, species in zip(axes.flat, SPECIES):
        for color, temperature in zip(COLORS, temperatures):
            points = [
                r for r in display
                if round(float(r["temperature_C"])) == temperature and r["species"] == species
                and float(r["observed_mole_fraction"]) > 0.0
            ]
            ax.scatter([float(r["loading_mol_CO2_per_mol_MEA"]) for r in points],
                       [float(r["observed_mole_fraction"]) for r in points],
                       facecolors="none", edgecolors=color, s=26, label=f"{temperature} °C observed")
            line = []
            for values in by_grid.values():
                parts = ("MEA", "MEAH+") if species == "MEA + MEAH+" else (species,)
                if round(float(values[parts[0]]["temperature_C"])) == temperature:
                    line.append((float(values[parts[0]]["loading_mol_CO2_per_mol_MEA"]),
                                 sum(float(values[p]["model_mole_fraction"]) for p in parts)))
            line.sort()
            ax.plot([x for x, _ in line], [y for _, y in line], color=color, linewidth=1.1,
                    linestyle="--", label=f"{temperature} °C calculated")
        stat = ln_statistics("speciation", "target", species,
                             [r for r in speciation if r["target"] == species])
        ax.set_title(f"{species}  (scored n={stat['evaluated_positive']}, "
                     f"RMS ln {stat['rms_ln_pred_over_obs']:.2f})", fontsize=10)
        ax.set_yscale("log")
        ax.set_xlabel("CO₂ loading (mol/mol MEA)")
        ax.grid(alpha=0.18)
    axes[0, 0].set_ylabel("Species / aggregate mole fraction")
    axes[1, 0].set_ylabel("Species / aggregate mole fraction")
    axes[0, 0].legend(fontsize=7, frameon=False, ncol=2)
    fig.suptitle(title, fontsize=13)
    fig.text(
        0.5, 0.012,
        "30 mass% MEA. Circles are all positive retained observations; dashed lines connect 46 adopted-record "
        "Engine states per temperature. Panel statistics use the scored packet targets.",
        ha="center", fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.95))
    save(fig, "speciation")


def render_heat(heat, title):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), squeeze=False)
    for ax, temperature in zip(axes.flat, ("40", "80", "120")):
        group = sorted([r for r in heat if r["temperature_C"] == temperature],
                       key=lambda r: float(r["loading_mol_CO2_per_mol_MEA"]))
        for color, source in zip(COLORS, sorted({r["source"] for r in group})):
            sub = [r for r in group if r["source"] == source]
            errors = [float(r["predicted_heat_release_kj_per_mol_CO2"])
                      - float(r["observed_heat_release_kj_per_mol_CO2"]) for r in sub]
            rmse = math.sqrt(statistics.fmean(e * e for e in errors))
            ax.scatter([float(r["loading_mol_CO2_per_mol_MEA"]) for r in sub],
                       [float(r["observed_heat_release_kj_per_mol_CO2"]) for r in sub],
                       facecolors="none", edgecolors=color, s=26, label=f"{source} observed")
            ax.plot([float(r["loading_mol_CO2_per_mol_MEA"]) for r in sub],
                    [float(r["predicted_heat_release_kj_per_mol_CO2"]) for r in sub],
                    color=color, linewidth=1.1, linestyle="--",
                    label=f"{source} calculated (RMSE {rmse:.1f})")
        ax.set_title(f"{temperature} °C")
        ax.set_xlabel("CO₂ loading (mol/mol MEA)")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=7, frameon=False)
    axes[0, 0].set_ylabel("Heat released (kJ/mol CO₂)")
    fig.suptitle(title, fontsize=12)
    fig.text(
        0.5, 0.012,
        "Calculated on the superseded Engine 8438ce5f (wheel 40fba7cf); the greenfield Engine cannot yet "
        "reproduce it (ePC-SAFT #84). Dashed lines connect calculated intervals; RMSE in kJ/mol CO₂.",
        ha="center", fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    save(fig, "heat")


def main():
    require_results(FIGURE_DATA)
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.hashsalt": "mea-regression-overview"})
    fit = read(FIT)
    pressure = [r for r in fit if r["family"] == "pressure"]
    speciation = [r for r in fit if r["family"] == "speciation"]
    colors = source_colors(pressure)

    table = [ln_statistics("pressure", "overall", "all", pressure)]
    table += [ln_statistics("pressure", "source", s, [r for r in pressure if r["source"] == s]) for s in colors]
    table += [ln_statistics("pressure", "temperature_C", t, [r for r in pressure if round(float(r["temperature_C"])) == t])
              for t in sorted({round(float(r["temperature_C"])) for r in pressure})]
    table += [ln_statistics("speciation", "overall", "all", speciation)]
    table += [ln_statistics("speciation", "target", s, [r for r in speciation if r["target"] == s]) for s in SPECIES]
    # Same statistics for the superseded all-five-shift adoption replay (Engine 8438ce5f).
    superseded = [
        dict(r, loading_mol_CO2_per_mol_MEA=r["loading"],
             predicted=r["predicted"] if r["status"] in ("evaluated", "pivot_reuse") else "")
        for r in read(SUPERSEDED) if r["family"] == "pressure"
    ]
    old = "superseded 8438ce5f candidate replay"
    table += [ln_statistics("pressure", "overall", "all", superseded, old)]
    table += [ln_statistics("pressure", "source", s, [r for r in superseded if r["source"] == s], old) for s in colors]
    with LN_STATISTICS.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)
    overall = table[0]

    render_isotherms(
        pressure, colors,
        f"Adopted record spans five decades of pCO₂ but overshoots near loading 0.3–0.5 "
        f"(RMS ln {overall['rms_ln_pred_over_obs']:.2f}, {overall['evaluated_positive']}/{overall['attempted']} states)",
    )
    render_parity(
        pressure, colors,
        f"{overall['evaluated_positive']}-state parity: RMS ln {overall['rms_ln_pred_over_obs']:.2f} "
        f"(log₁₀ {overall['rmse_log10']:.3f}, factor {overall['rms_factor']:.2f}), AARD {overall['aard_percent']:.0f}%",
    )
    render_residuals(
        pressure, colors,
        "Residuals follow loading across sources: low below 0.2 and above 0.55, high near 0.3–0.5",
    )
    species_rms = {r["group"]: r["rms_ln_pred_over_obs"] for r in table if r["family"] == "speciation"}
    render_speciation(
        speciation, read(GRID), read(DISPLAY),
        f"Adopted record: amine and carbamate within RMS ln {max(species_rms[s] for s in SPECIES[:4]):.2f}; "
        f"bicarbonate misses low-loading data (RMS ln {species_rms['HCO3-']:.2f})",
    )

    summary = json.loads(HEAT_SUMMARY.read_text())
    assert summary["engine_wheel_sha256"] == SUPERSEDED_HEAT_WHEEL, "heat identity changed; relabel figure"
    heat = read(HEAT)
    assert len(heat) == 113 and all(r["status"] == "evaluated" for r in heat)
    render_heat(heat, "Superseded-Engine heat: 120 °C absorption heat remains under-predicted")

    inputs = [FIT, SUPERSEDED, GRID, DISPLAY, FIGURE_DATA, HEAT, HEAT_SUMMARY, PARAM, Path(__file__)]
    (OUT / "provenance.json").write_text(
        json.dumps(
            {
                "inputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
                "pressure_speciation_identity": "adopted parameter record on the pinned Engine; figure-calculation receipt",
                "heat_identity": "parameter record 568f7a5f (same coefficients) on superseded Engine 8438ce5f, wheel 40fba7cf",
                "model_executed": False,
                "series": "open markers observations; dashed segments connect discrete calculations; no interpolation",
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
        print(f"{row['engine'][:10]:10s} {row['family']:10s} {row['group_type']:13s} {str(row['group']):13s} "
              f"n={row['evaluated_positive']:3d}/{row['attempted']:3d} mean ln {row['mean_ln_pred_over_obs']:+.3f} "
              f"RMS ln {row['rms_ln_pred_over_obs']:.3f} log10 {row['rmse_log10']:.4f} AARD {row['aard_percent']:.1f}%")


if __name__ == "__main__":
    main()
