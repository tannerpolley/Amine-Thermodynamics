from __future__ import annotations

import csv
import argparse
import json
import sys
from pathlib import Path

from result_freshness import (
    FIGURE_DATA,
    FIGURES,
    require_results,
    source_hashes,
    stamp_results,
)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator
from scipy.interpolate import PchipInterpolator


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from MEA.common.plot_style import (  # noqa: E402
    JOU_TEMPERATURE_COLORS,
    TRUE_SPECIES_COLORS,
    TRUE_SPECIES_LABELS,
    apply_plot_theme,
    save_figure_bundle,
    write_mpl_sidecar,
)
from MEA.common.analysis_io import file_sha256, repo_relative_path  # noqa: E402

DISPLAY_SPECIES = ("CO2", "MEA", "MEAH+", "MEACOO-", "HCO3-")
MARKERS = {
    "Bottinger2008": "o",
    "Jakobsen2005": "s",
    "Matin2012": "^",
    "Hilliard2008": "o",
    "Jou1995": "x",
    "Aronu2011": "*",
    "Idris2014": "D",
    "Mamun2005": "h",
    "Xu2011": "^",
}
SOURCE_LABELS = {
    "Bottinger2008": "Böttinger et al. (2008)",
    "Jakobsen2005": "Jakobsen et al. (2005)",
    "Matin2012": "Matin et al. (2012)",
    "Aronu2011": "Aronu et al. (2011)",
    "Hilliard2008": "Hilliard (2008)",
    "Idris2014": "Idris et al. (2014)",
    "Jou1995": "Jou et al. (1995)",
    "Mamun2005": "Mamun et al. (2005)",
    "Xu2011": "Xu et al. (2011)",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_rows(
    path: Path, fieldnames: tuple[str, ...], values: list[dict[str, object]]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(values)


def smooth_line(
    selected: list[dict[str, str]], x_field: str, y_field: str
) -> tuple[np.ndarray, np.ndarray]:
    by_x: dict[float, float] = {}
    for row in selected:
        x_value = float(row[x_field])
        y_value = float(row[y_field])
        if x_value in by_x and not np.isclose(
            by_x[x_value], y_value, rtol=1.0e-8, atol=1.0e-14
        ):
            raise ValueError("duplicate model loading has inconsistent responses")
        by_x[x_value] = y_value
    points = sorted(by_x.items())
    if len(points) < 2 or any(y <= 0.0 for _, y in points):
        return np.array([]), np.array([])
    x = np.array([point[0] for point in points])
    y = np.array([point[1] for point in points])
    line_x = np.unique(
        np.concatenate((np.linspace(x[0], x[-1], max(240, 24 * len(x))), x))
    )
    line_y = 10.0 ** PchipInterpolator(x, np.log10(y))(line_x)
    return line_x, line_y


def save(
    fig,
    output: Path,
    stem: str,
    title: str,
    description: str,
    data: Path,
    observations: Path,
    engine_states: Path,
    line_method: str = "PCHIP interpolation of log10(model response)",
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    png, svg, pdf = save_figure_bundle(fig, output / stem)
    write_mpl_sidecar(
        output / f"{stem}.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=data,
    )
    sidecar = output / f"{stem}.mpl.yaml"
    with sidecar.open("a", encoding="utf-8") as stream:
        stream.write(f"observations_path: {repo_relative_path(observations)}\n")
        stream.write(f"observations_sha256: {file_sha256(observations)}\n")
        stream.write(f"engine_states_path: {repo_relative_path(engine_states)}\n")
        stream.write(f"engine_states_sha256: {file_sha256(engine_states)}\n")
        stream.write(f"line_method: {line_method}\n")
    plt.close(fig)


def render_speciation(temperature_c: int) -> None:
    output = ANALYSIS / "figures/speciation/output"
    model = [
        row
        for row in rows(output / "speciation-model-grid.csv")
        if round(float(row["temperature_C"])) == temperature_c
    ]
    observed = [
        row
        for row in rows(output / "speciation-display-observations.csv")
        if round(float(row["temperature_C"])) == temperature_c
    ]
    line_rows: list[dict[str, object]] = []
    apply_plot_theme()
    fig, (ax, trace_ax) = plt.subplots(
        2,
        1,
        figsize=(9.2, 7.0),
        sharex=True,
        gridspec_kw={"height_ratios": (4.2, 1.15), "hspace": 0.05},
    )
    axes = (ax, trace_ax)
    model_by_grid: dict[str, dict[str, str]] = {}
    for row in model:
        model_by_grid.setdefault(row["grid_id"], {})[row["species"]] = row
    for species in (*DISPLAY_SPECIES, "MEA + MEAH+"):
        selected: list[tuple[float, float]] = []
        for values in model_by_grid.values():
            if species == "MEA + MEAH+":
                if "MEA" not in values or "MEAH+" not in values:
                    continue
                x = float(values["MEA"]["loading_mol_CO2_per_mol_MEA"])
                y = float(values["MEA"]["model_mole_fraction"]) + float(
                    values["MEAH+"]["model_mole_fraction"]
                )
            elif species in values:
                x = float(values[species]["loading_mol_CO2_per_mol_MEA"])
                y = float(values[species]["model_mole_fraction"])
            else:
                continue
            selected.append((x, y))
        selected.sort()
        if selected:
            for current_ax in axes:
                current_ax.plot(
                    [point[0] for point in selected],
                    [point[1] for point in selected],
                    color=TRUE_SPECIES_COLORS[species],
                    linewidth=1.6,
                    linestyle="--",
                    zorder=2,
                )
            line_rows.extend(
                {
                    "temperature_C": temperature_c,
                    "species": species,
                    "loading_mol_CO2_per_mol_MEA": x,
                    "model_mole_fraction": y,
                }
                for x, y in selected
            )
    sources = tuple(
        source
        for source in ("Bottinger2008", "Jakobsen2005", "Matin2012")
        if any(row["source"] == source for row in observed)
    )
    for source in sources:
        for species in (*DISPLAY_SPECIES, "MEA + MEAH+"):
            selected = [
                row
                for row in observed
                if row["source"] == source and row["species"] == species
            ]
            positive = [
                row for row in selected if float(row["observed_mole_fraction"]) > 0
            ]
            if positive:
                for current_ax in axes:
                    current_ax.scatter(
                        [float(row["loading_mol_CO2_per_mol_MEA"]) for row in positive],
                        [float(row["observed_mole_fraction"]) for row in positive],
                        color=TRUE_SPECIES_COLORS[species],
                        edgecolors="black",
                        marker=MARKERS[source],
                        s=34,
                        linewidths=0.55,
                        alpha=0.88,
                        zorder=3,
                    )
    hco3_minimum = min(
        [
            float(row["model_mole_fraction"])
            for row in model
            if row["species"] == "HCO3-"
        ]
        + [
            float(row["observed_mole_fraction"])
            for row in observed
            if row["species"] == "HCO3-" and float(row["observed_mole_fraction"]) > 0.0
        ]
    )
    hco3_cutoff = 0.7 * hco3_minimum
    displayed_maximum = max(
        max(float(row["model_mole_fraction"]) for row in line_rows),
        max(
            float(row["observed_mole_fraction"])
            for row in observed
            if row["species"] in (*DISPLAY_SPECIES, "MEA + MEAH+")
        ),
    )
    upper_limit = 1.03 * displayed_maximum
    trace_ax.set_xlabel(r"$CO_2$ loading, mol $CO_2$/mol MEA")
    fig.supylabel("True-species mole fraction", x=0.015)
    ax.set_title(f"Speciation at {temperature_c} °C and 30 wt% MEA")
    for current_ax in axes:
        current_ax.set_yscale("log")
        current_ax.set_xlim(0.05, 1.02)
        current_ax.grid(True, which="major", alpha=0.2)
        current_ax.yaxis.set_minor_locator(NullLocator())
    ax.set_ylim(hco3_cutoff, upper_limit)
    ax.set_yticks(
        tuple(
            tick
            for tick in (1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1)
            if hco3_cutoff <= tick <= upper_limit
        )
    )
    trace_ax.set_ylim(1.0e-10, hco3_cutoff)
    trace_ax.set_yticks(
        tuple(tick for tick in (1.0e-10, 1.0e-8, 1.0e-6, 1.0e-4) if tick <= hco3_cutoff)
    )
    ax.spines.bottom.set_visible(False)
    trace_ax.spines.top.set_visible(False)
    ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    trace_ax.tick_params(axis="x", which="both", top=False)
    break_size = 0.008
    break_style = dict(color="black", clip_on=False, linewidth=0.8)
    ax.plot(
        (-break_size, break_size),
        (-break_size, break_size),
        transform=ax.transAxes,
        **break_style,
    )
    ax.plot(
        (1 - break_size, 1 + break_size),
        (-break_size, break_size),
        transform=ax.transAxes,
        **break_style,
    )
    trace_ax.plot(
        (-break_size, break_size),
        (1 - break_size, 1 + break_size),
        transform=trace_ax.transAxes,
        **break_style,
    )
    trace_ax.plot(
        (1 - break_size, 1 + break_size),
        (1 - break_size, 1 + break_size),
        transform=trace_ax.transAxes,
        **break_style,
    )
    species_handles = [
        Line2D(
            [0],
            [0],
            color=TRUE_SPECIES_COLORS[s],
            linewidth=1.6,
            linestyle="--",
            label=TRUE_SPECIES_LABELS[s],
        )
        for s in DISPLAY_SPECIES
    ]
    species_handles.append(
        Line2D(
            [0],
            [0],
            color=TRUE_SPECIES_COLORS["MEA + MEAH+"],
            linewidth=1.6,
            linestyle="--",
            label=r"$MEA + MEAH^+$ aggregate",
        )
    )
    source_handles = [
        Line2D(
            [0],
            [0],
            color="black",
            marker=MARKERS[s],
            linestyle="none",
            markerfacecolor="none",
            label=SOURCE_LABELS[s],
        )
        for s in sources
    ]
    fig.legend(
        handles=species_handles + source_handles,
        loc="lower center",
        ncol=5,
        bbox_to_anchor=(0.5, 0.0),
    )
    fig.subplots_adjust(left=0.12, right=0.98, top=0.93, bottom=0.19)
    suffix = "" if temperature_c == 20 else f"-{temperature_c}C"
    line_data = output / f"speciation-model-lines{suffix}.csv"
    write_rows(
        line_data,
        (
            "temperature_C",
            "species",
            "loading_mol_CO2_per_mol_MEA",
            "model_mole_fraction",
        ),
        line_rows,
    )
    save(
        fig,
        output,
        f"speciation-diagnostic-replay{suffix}",
        f"{temperature_c} C MEA liquid-equilibrium replay with full retained observations",
        f"Broken log scale starts 30% below the lowest positive HCO3- model or observation value ({hco3_minimum:.6g}) and ends 3% above the displayed maximum ({upper_limit:.6g}). Dashed lines connect {len(model_by_grid)} direct pinned-Engine evaluations of the five principal species plus the MEA plus MEAH+ observation operator through loading 1.0. Markers show every positive retained {temperature_c} C, 30 wt% value for those series; exact reported zeros remain in the source snapshot but are omitted from the visual. Trace ions remain in the calculation and source snapshot but are omitted from the visual.",
        line_data,
        output / "speciation-display-observations.csv",
        output / "speciation-model-grid.csv",
        f"piecewise connection of {len(model_by_grid)} direct pinned-Engine evaluations; no interpolation",
    )


def render_pressure() -> None:
    output = ANALYSIS / "figures/pressure/output"
    model = rows(output / "pressure-model.csv")
    observed = rows(output / "pressure-observations.csv")
    line_rows: list[dict[str, object]] = []
    apply_plot_theme()
    fig, ax = plt.subplots(figsize=(9.4, 6.3))
    for temperature in (40, 60, 80, 100, 120):
        color = JOU_TEMPERATURE_COLORS[temperature]
        selected = sorted(
            (row for row in model if round(float(row["temperature_C"])) == temperature),
            key=lambda row: float(row["loading_mol_CO2_per_mol_MEA"]),
        )
        if selected:
            line_x, line_y = smooth_line(
                selected,
                "loading_mol_CO2_per_mol_MEA",
                "predicted_pCO2_kPa",
            )
            ax.plot(
                line_x,
                line_y,
                color=color,
                linewidth=1.8,
                label=f"{temperature} °C model",
            )
            line_rows.extend(
                {
                    "temperature_C": temperature,
                    "loading_mol_CO2_per_mol_MEA": x,
                    "predicted_pCO2_kPa": y,
                }
                for x, y in zip(line_x, line_y, strict=True)
            )
        for source in (
            "Aronu2011",
            "Hilliard2008",
            "Idris2014",
            "Jou1995",
            "Mamun2005",
            "Xu2011",
        ):
            points = [
                row
                for row in observed
                if round(float(row["temperature_C"])) == temperature
                and row["source"] == source
            ]
            if points:
                ax.scatter(
                    [float(row["loading_mol_CO2_per_mol_MEA"]) for row in points],
                    [float(row["observed_pCO2_kPa"]) for row in points],
                    color=color,
                    marker=MARKERS[source],
                    s=34,
                    linewidths=0.7,
                    edgecolors=None if source == "Jou1995" else "black",
                    alpha=0.88,
                    zorder=3,
                )
    ax.set_xlabel(r"$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel(r"$CO_2$ partial pressure, kPa")
    ax.set_xlim(0.0, 0.72)
    ax.set_yscale("log")
    ax.set_ylim(1.0e-4, 2.0e4)
    ax.grid(True, which="major", alpha=0.2)
    displayed_sources = tuple(
        source
        for source in (
            "Aronu2011",
            "Hilliard2008",
            "Idris2014",
            "Jou1995",
            "Mamun2005",
            "Xu2011",
        )
        if any(row["source"] == source for row in observed)
    )
    source_handles = [
        Line2D(
            [0],
            [0],
            color="black",
            marker=MARKERS[source],
            linestyle="none",
            label=SOURCE_LABELS[source],
        )
        for source in displayed_sources
    ]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles + source_handles,
        labels + [h.get_label() for h in source_handles],
        ncol=3,
    )
    ax.set_title("30 wt% MEA $CO_2$ pressure: reactive ePC-SAFT parameter set")
    fig.tight_layout()
    line_data = output / "pressure-model-lines.csv"
    write_rows(
        line_data,
        (
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "predicted_pCO2_kPa",
        ),
        line_rows,
    )
    save(
        fig,
        output,
        "pressure-diagnostic-replay",
        "30 wt% MEA carbon-dioxide pressure replay",
        "Smooth lines through successfully evaluated reactive ionic Engine states and all 161 active-v1 observations from Aronu, Hilliard, Idris, Jou, Mamun, and Xu at 40--120 degrees Celsius.",
        line_data,
        output / "pressure-observations.csv",
        output / "pressure-model.csv",
    )


def render_permittivity_comparison(results: Path) -> None:
    source = results / "permittivity-formulation-targets.csv"
    comparison = json.loads(
        (results / "permittivity-formulation-comparison.json").read_text(
            encoding="utf-8"
        )
    )
    target_rows = rows(source)
    output = ANALYSIS / "figures/permittivity_comparison/output"
    output.mkdir(parents=True, exist_ok=True)
    plot_data = output / "permittivity-formulation-parity.csv"
    plotted: list[dict[str, object]] = []
    for row in target_rows:
        scale = 1.0e-3 if row["family"] == "pressure" else 1.0
        plotted.append(
            {
                "family": row["family"],
                "variant_id": row["variant_id"],
                "observation_id": row["observation_id"],
                "target_id": row["target_id"],
                "temperature_k": row["temperature_k"],
                "loading_mol_co2_per_mol_mea": row["loading_mol_co2_per_mol_mea"],
                "observed": float(row["observed"]) * scale,
                "predicted": float(row["predicted"]) * scale,
                "unit": "kPa" if row["family"] == "pressure" else "mole fraction",
                "log10_predicted_over_observed": row["log10_predicted_over_observed"],
            }
        )
    write_rows(
        plot_data,
        (
            "family",
            "variant_id",
            "observation_id",
            "target_id",
            "temperature_k",
            "loading_mol_co2_per_mol_mea",
            "observed",
            "predicted",
            "unit",
            "log10_predicted_over_observed",
        ),
        plotted,
    )

    styles = {
        "current_ion_specific": ("Ion-specific baseline", "#666666", "^"),
        "schick_temperature_mixing": ("Schick mixing", "#0072B2", "o"),
        "uyan_co2_excluding": ("Solvent-only mass fraction", "#D55E00", "s"),
    }
    metrics = comparison["variants"]
    apply_plot_theme()
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.7))
    for ax, family, title, axis_label in zip(
        axes,
        ("pressure", "speciation"),
        (r"$CO_2$ partial pressure", "Liquid speciation"),
        (r"Observed $p_{CO_2}$, kPa", "Observed mole fraction"),
        strict=True,
    ):
        selected = [row for row in plotted if row["family"] == family]
        limits = (
            min(
                min(float(row["observed"]), float(row["predicted"])) for row in selected
            ),
            max(
                max(float(row["observed"]), float(row["predicted"])) for row in selected
            ),
        )
        padding = 10.0**0.15
        low, high = limits[0] / padding, limits[1] * padding
        ax.plot(
            [low, high], [low, high], color="#333333", linewidth=1.1, linestyle="--"
        )
        for variant, (label, color, marker) in styles.items():
            points = [row for row in selected if row["variant_id"] == variant]
            variant_metrics = metrics[variant]
            rmse = variant_metrics[f"{family}_temperature_balanced_log10_rmse"]
            evaluated = variant_metrics[f"{family}_evaluated_states"]
            requested = variant_metrics[f"{family}_attempted_states"]
            ax.scatter(
                [float(row["observed"]) for row in points],
                [float(row["predicted"]) for row in points],
                label=f"{label}  (RMSE {rmse:.3f}; {evaluated}/{requested})",
                color=color,
                marker=marker,
                s=38,
                linewidths=0.9,
                facecolors="none" if marker in {"o", "^"} else color,
                alpha=0.55 if variant == "current_ion_specific" else 0.82,
                zorder=4 if variant == "uyan_co2_excluding" else 3,
            )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(low, high)
        ax.set_ylim(low, high)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title)
        ax.set_xlabel(axis_label)
        ax.set_ylabel(axis_label.replace("Observed", "Predicted"))
        ax.grid(True, which="major", alpha=0.2)
        ax.legend(loc="upper left")
    fig.suptitle("Full-domain permittivity comparison: predicted versus observed")
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(fig, output / "permittivity-formulation-parity")
    write_mpl_sidecar(
        output / "permittivity-formulation-parity.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="Three-way permittivity formulation parity",
        description="All successfully evaluated pressure and speciation targets for the ion-specific baseline, Schick component mixing, and Uyan solvent-only formulations; the dashed diagonal denotes exact agreement and legend values are temperature-balanced log10 RMSE with evaluated-state coverage.",
        data_path=plot_data,
    )
    with (output / "permittivity-formulation-parity.mpl.yaml").open(
        "a", encoding="utf-8"
    ) as stream:
        stream.write(f"source_path: {repo_relative_path(source)}\n")
        stream.write(f"source_sha256: {file_sha256(source)}\n")
        stream.write(
            "continuity: discrete evaluated endpoints; no model interpolation\n"
        )
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Render verified retained tables; never run the Engine"
    )
    parser.add_argument(
        "--permittivity-comparison",
        type=Path,
        help="Explicit directory of retained comparison results",
    )
    args = parser.parse_args()
    if args.permittivity_comparison:
        render_permittivity_comparison(args.permittivity_comparison)
        raise SystemExit(0)
    require_results(FIGURE_DATA)
    inputs = source_hashes(
        Path(__file__),
        FIGURE_DATA,
        ROOT / "src/MEA/common/plot_style.py",
        ROOT / "src/MEA/common/analysis_io.py",
    )
    for temperature in (20, 40, 60, 80):
        render_speciation(temperature)
    render_pressure()
    require_results(FIGURE_DATA)
    outputs = []
    for family, stems in (
        ("pressure", ["pressure-diagnostic-replay"]),
        (
            "speciation",
            [
                "speciation-diagnostic-replay" + suffix
                for suffix in ("", "-40C", "-60C", "-80C")
            ],
        ),
    ):
        output = ANALYSIS / "figures" / family / "output"
        outputs.extend(
            output / (stem + extension)
            for stem in stems
            for extension in (".svg", ".png", ".pdf", ".mpl.yaml")
        )
        outputs.extend(sorted(output.glob(f"{family}-model-lines*.csv")))
    stamp_results(FIGURES, outputs, inputs=inputs)
