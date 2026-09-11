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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/regression_overview/output"
FIT = ROOT / "results/reaction-temperature-fit/full-validation-targets.csv"
HEAT = ROOT / "results/calorimetry/current-selected-direct-enthalpy-comparison.csv"
PARAM = ROOT / "results/selected-current-best-parameters.json"
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def fit_statistic(valid, log):
    if log:
        errors = [
            math.log10(float(row["predicted"]) / float(row["observed"]))
            for row in valid
        ]
        return f"log₁₀ RMSE {math.sqrt(statistics.fmean(error * error for error in errors)):.3f}"
    errors = [float(row["predicted"]) - float(row["observed"]) for row in valid]
    return f"RMSE {math.sqrt(statistics.fmean(error * error for error in errors)):.2f} kJ/mol CO₂"


def render(name, rows, panels, ylabel, title, note, log=False):
    columns = min(3, len(panels))
    rows_count = (len(panels) + columns - 1) // columns
    fig, axes = plt.subplots(
        rows_count, columns, figsize=(12, 3.8 * rows_count), squeeze=False
    )
    for ax in axes.flat[len(panels) :]:
        ax.set_visible(False)
    for ax, (field, value) in zip(axes.flat, panels):
        group = [r for r in rows if r[field] == value]
        assert group, f"Empty {name} panel: {field}={value}"
        for i, temp in enumerate(
            sorted({r["temperature_C"] for r in group}, key=float)
        ):
            sub = [r for r in group if r["temperature_C"] == temp]
            color = COLORS[i % len(COLORS)]
            ax.scatter(
                [float(r["loading"]) for r in sub],
                [float(r["observed"]) for r in sub],
                facecolors="none",
                edgecolors=color,
                s=28,
                label=f"{temp} °C observed",
            )
            valid = sorted(
                [
                    r
                    for r in sub
                    if r["predicted"]
                    and r["status"] in ("evaluated", "pivot_reuse")
                    and float(r["observed"]) > 0.0
                    and float(r["predicted"]) > 0.0
                ],
                key=lambda r: float(r["loading"]),
            )
            ax.plot(
                [float(r["loading"]) for r in valid],
                [float(r["predicted"]) for r in valid],
                color=color,
                linewidth=1.2,
                linestyle="--",
                label=f"{temp} °C calculated ({fit_statistic(valid, log)})",
            )
        if log:
            ax.set_yscale("log")
        ax.set_title(f"{value} °C" if field == "temperature_C" else value)
        ax.set_xlabel("CO₂ loading (mol/mol MEA)")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=7, frameon=False)
    axes[0, 0].set_ylabel(ylabel)
    fig.suptitle(title, fontsize=13)
    fig.text(0.5, 0.015, note, ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.055, 1, 0.94))
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
    with (OUT / f"{name}.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {"font.family": "DejaVu Sans", "svg.hashsalt": "mea-regression-overview"}
    )
    fit = read(FIT)
    pressure = [r for r in fit if r["family"] == "pressure"]
    speciation = [r for r in fit if r["family"] == "speciation"]
    assert len(pressure) == 161 and len(speciation) == 131
    assert sum(r["status"] in ("evaluated", "pivot_reuse") for r in speciation) == 129
    summary = json.loads(
        (
            ROOT / "results/calorimetry/current-selected-direct-enthalpy-summary.json"
        ).read_text()
    )
    assert summary["parameter_document_sha256"] == digest(PARAM), (
        "Heat does not match selected parameters"
    )
    heat_record = (
        ROOT / "figures/calorimetry/output/current-selected-direct-enthalpy.mpl.yaml"
    )
    expected_heat_hash = next(
        line.split(":", 1)[1].strip()
        for line in heat_record.read_text().splitlines()
        if line.startswith("comparison_sha256:")
    )
    assert digest(HEAT) == expected_heat_hash, (
        "Heat comparison differs from retained figure source"
    )
    heat = [
        dict(
            r,
            loading=r["loading_mol_CO2_per_mol_MEA"],
            observed=r["observed_heat_release_kj_per_mol_CO2"],
            predicted=r["predicted_heat_release_kj_per_mol_CO2"],
        )
        for r in read(HEAT)
    ]
    assert len(heat) == 113 and all(r["status"] == "evaluated" for r in heat)
    render(
        "pressure",
        pressure,
        [("temperature_C", t) for t in ["40", "60", "80", "100", "120"]],
        "CO₂ partial pressure (kPa)",
        "Regression candidate: pressure across temperature",
        "All 161 targets shown. Dashed lines connect calculated states; no interpolation. Candidate includes R1–R5 shifts; saved selection includes R2/R4/R5 only.",
        True,
    )
    render(
        "speciation",
        speciation,
        [("target", t) for t in ["MEA", "MEAH+", "MEA + MEAH+", "MEACOO-", "HCO3-"]],
        "Reported species / aggregate mole fraction",
        "Regression candidate: species partition remains uneven",
        "131 observations; 129 calculated targets. Dashed lines connect calculated states; no interpolation. Two failed targets remain in the CSV. Candidate differs from saved selection.",
        True,
    )
    render(
        "heat",
        heat,
        [("temperature_C", t) for t in ["40", "80", "120"]],
        "Heat released (kJ/mol CO₂)",
        "Saved parameter set: absorption heat remains biased at 120 °C",
        "113 finite-loading intervals. Dashed lines connect calculated intervals; no interpolation. Zero vapor inventory and anchored species enthalpy references; no uncertainty bands established.",
    )
    inputs = [
        FIT,
        HEAT,
        PARAM,
        ROOT / "results/reaction-temperature-fit/full-validation-receipt.json",
        ROOT / "results/calorimetry/current-selected-direct-enthalpy-summary.json",
        heat_record,
        Path(__file__),
    ]
    (OUT / "provenance.json").write_text(
        json.dumps(
            {
                "inputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
                "pressure_speciation_identity": "full-validation receipt baseline plus its five candidate_shifts_kj_mol; not saved selection",
                "heat_identity": "selected parameter SHA matches heat summary; comparison CSV hash matches retained calorimetry figure record",
                "model_executed": False,
                "series": "open circles observations; dashed segments are discrete calculations; no interpolation",
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
    print(
        "Rendered pressure 161/161, speciation 129/131, selected-parameter heat 113/113; model not run."
    )


if __name__ == "__main__":
    main()
