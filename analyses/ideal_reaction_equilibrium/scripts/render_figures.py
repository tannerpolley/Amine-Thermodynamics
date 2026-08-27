from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.plot_style import (
    EPCSAFT_NEUTRAL_LINESTYLE,
    JOU_DATA_MARKER,
    JOU_DATA_MARKERSIZE,
    LEGACY_PCSAFT_LINESTYLE,
    MODEL_LINEWIDTH,
    REFERENCE_LINEWIDTH,
    apply_pressure_axes,
    save_figure_bundle,
    temperature_color,
    write_mpl_sidecar,
)
from MEA.common.analysis_io import copy_file_as, normalize_svg, read_required_csv
from MEA.common.speciation_figures import write_speciation_plot

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = ANALYSIS_DIR / "results"
PRESSURE_FIGURE_OUT = ANALYSIS_DIR / "figures" / "pressure" / "output"
SPECIATION_FIGURE_OUT = ANALYSIS_DIR / "figures" / "speciation" / "output"
LATEX_FIGURES_DIR = REPO_ROOT / "docs" / "latex" / "figures"
PRESSURE_MODEL_LABELS = {
    "legacy_pcsaft_smith_missen": ("Legacy PC-SAFT Smith-Missen", LEGACY_PCSAFT_LINESTYLE, REFERENCE_LINEWIDTH),
    "neutral_pcsaft_pressure_reference": ("Neutral ePC-SAFT parity", EPCSAFT_NEUTRAL_LINESTYLE, MODEL_LINEWIDTH),
}
IDEAL_REFERENCE_PRESSURE_FIGSIZE = (9.2, 5.4)


def _data_xlim(frame: pd.DataFrame, column: str, *, pad: float = 0.035) -> tuple[float, float]:
    values = frame[column].dropna().astype(float)
    if values.empty:
        return (0.0, 0.8)
    lo = max(0.0, float(values.min()) - pad)
    hi = min(0.8, float(values.max()) + pad)
    return (lo, hi)


def require_csv(name: str) -> pd.DataFrame:
    return read_required_csv(
        OUT_DIR / name,
        hint="Run `uv run python analyses/ideal_reaction_equilibrium/scripts/generate_data.py` first",
    )


def _write_curated_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PRESSURE_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    SPECIATION_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    pressure_results = require_csv("ideal_reference_pressure_results.csv")
    speciation_results = require_csv("ideal_reference_speciation_results.csv")
    speciation_curve = require_csv("ideal_reference_speciation_curve.csv")
    speciation_reference_points = require_csv("ideal_reference_speciation_reference_points.csv")
    residual_acceptance_audit = require_csv("ideal_reference_residual_acceptance_audit.csv")
    for flag_column in ("passes", "claim_allowed"):
        residual_acceptance_audit[flag_column] = residual_acceptance_audit[flag_column].astype(str).str.lower()
    return pressure_results, speciation_results, residual_acceptance_audit, speciation_curve, speciation_reference_points


def plot_pressure(pressure_results: pd.DataFrame) -> None:
    title = "Smith-Missen baseline CO2 solubility"
    description = (
        "Observed 30 wt% MEA CO2 partial-pressure data are compared against the Smith-Missen "
        "solubility-pressure baseline and the neutral ePC-SAFT parity route."
    )
    fig, ax = plt.subplots(figsize=IDEAL_REFERENCE_PRESSURE_FIGSIZE)
    temperatures = sorted(pressure_results["temperature_C"].dropna().unique())
    for temperature_C in temperatures:
        color = temperature_color(temperature_C)
        t_df = pressure_results[pressure_results["temperature_C"] == temperature_C]
        observed = t_df[["CO2_loading", "observed_CO2_pressure_kPa"]].drop_duplicates().sort_values("CO2_loading")
        if not observed.empty:
            ax.plot(
                observed["CO2_loading"],
                observed["observed_CO2_pressure_kPa"],
                linestyle="none",
                marker=JOU_DATA_MARKER,
                markersize=JOU_DATA_MARKERSIZE,
                color=color,
                alpha=0.9,
            )
        for model_family, (label, linestyle, linewidth) in PRESSURE_MODEL_LABELS.items():
            subset = t_df[t_df["model_family"] == model_family].sort_values("CO2_loading")
            if subset.empty:
                continue
            ax.plot(
                subset["CO2_loading"],
                subset["predicted_CO2_pressure_kPa"],
                linestyle,
                color=color,
                linewidth=linewidth,
                alpha=0.9 if model_family == "neutral_pcsaft_pressure_reference" else 0.65,
            )
    apply_pressure_axes(ax, title=title)
    ax.set_xlim(*_data_xlim(pressure_results, "CO2_loading"))
    ax.set_ylim(1.0e-3, 2.0e3)
    temperature_handles = [
        Line2D([0], [0], color=temperature_color(temperature_C), linewidth=MODEL_LINEWIDTH, label=f"{temperature_C:g} C")
        for temperature_C in temperatures
    ]
    role_handles = [
        Line2D(
            [0],
            [0],
            marker=JOU_DATA_MARKER,
            linestyle="none",
            color="0.25",
            markersize=JOU_DATA_MARKERSIZE,
            label="Jou data",
        ),
        Line2D(
            [0],
            [0],
            linestyle=LEGACY_PCSAFT_LINESTYLE,
            color="0.25",
            linewidth=REFERENCE_LINEWIDTH,
            label="Legacy PC-SAFT",
        ),
        Line2D(
            [0],
            [0],
            linestyle=EPCSAFT_NEUTRAL_LINESTYLE,
            color="0.25",
            linewidth=MODEL_LINEWIDTH,
            label="Neutral ePC-SAFT parity",
        ),
    ]
    temperature_legend = ax.legend(
        handles=temperature_handles,
        title="Temperature",
        ncol=1,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
    )
    ax.add_artist(temperature_legend)
    ax.legend(handles=role_handles, title="Role", ncol=1, loc="lower left", bbox_to_anchor=(1.02, 0.0))
    fig.subplots_adjust(right=0.72)
    plot_data_path = PRESSURE_FIGURE_OUT / "ideal_reference_pressure_plot_data.csv"
    pressure_results.to_csv(plot_data_path, index=False)
    figure_stem = PRESSURE_FIGURE_OUT / "ideal_reference_pressure_vs_loading"
    png, svg, pdf = save_figure_bundle(fig, figure_stem)
    normalize_svg(svg)
    plt.close(fig)
    write_mpl_sidecar(
        PRESSURE_FIGURE_OUT / "ideal_reference_pressure_vs_loading.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title=title,
        description=description,
        data_path=plot_data_path,
        style_source="analyses/ideal_reaction_equilibrium/scripts/render_figures.py",
    )
    copy_file_as(pdf, LATEX_FIGURES_DIR / "mea_ideal_pressure_vs_loading.pdf")


def plot_speciation(speciation_curve: pd.DataFrame, speciation_reference_points: pd.DataFrame) -> None:
    for old_name in (
        "ideal_reference_speciation_vs_loading_diagnostic.png",
        "ideal_reference_speciation_vs_loading_diagnostic.svg",
        "ideal_reference_speciation_vs_loading_diagnostic.pdf",
        "ideal_reference_speciation_vs_loading_diagnostic.mpl.yaml",
        "ideal_reference_speciation_vs_loading_diagnostic_plot_data.csv",
    ):
        old_path = OUT_DIR / old_name
        if old_path.exists():
            old_path.unlink()

    for temperature_C in sorted(speciation_curve["temperature_C"].dropna().unique()):
        for suffix in (".png", ".svg", ".pdf", ".mpl.yaml", "_plot_data.csv"):
            old_path = SPECIATION_FIGURE_OUT / f"ideal_reference_speciation_{int(round(float(temperature_C)))}C_diagnostic{suffix}"
            if old_path.exists():
                old_path.unlink()
        png, svg, pdf, sidecar = write_speciation_plot(
            curve_frame=speciation_curve,
            point_frame=speciation_reference_points,
            output_dir=SPECIATION_FIGURE_OUT,
            stem=f"ideal_reference_speciation_{int(round(float(temperature_C)))}C",
            title=f"Ideal Smith-Missen speciation, {temperature_C:g} C",
            description=(
                "Continuous explicit nine-species ideal Smith-Missen equilibrium curves are shown with "
                "measured reference points. Major-species validation is controlled by the residual audit."
            ),
            style_source="analyses/ideal_reaction_equilibrium/scripts/render_figures.py",
            temperature_C=float(temperature_C),
        )
        if int(round(float(temperature_C))) in {20, 40}:
            copy_file_as(pdf, LATEX_FIGURES_DIR / f"mea_ideal_speciation_{int(round(float(temperature_C)))}C.pdf")
    write_mpl_sidecar(
        SPECIATION_FIGURE_OUT / "ideal_reference_speciation_figure_family.mpl.yaml",
        png_name="ideal_reference_speciation_40C.png",
        svg_name="ideal_reference_speciation_40C.svg",
        pdf_name="ideal_reference_speciation_40C.pdf",
        title="Smith-Missen baseline speciation figure family",
        description="Figure-owned explicit ideal-equilibrium speciation outputs; one full-coverage plot is generated per temperature.",
        data_path=SPECIATION_FIGURE_OUT / "ideal_reference_speciation_40C_plot_data.csv",
        style_source="analyses/ideal_reaction_equilibrium/scripts/render_figures.py",
    )


def write_ideal_reference_reports(residual_acceptance_audit: pd.DataFrame) -> None:
    speciation_rows = residual_acceptance_audit[residual_acceptance_audit["target_family"] == "speciation"].copy()
    if "target_role" not in speciation_rows.columns:
        speciation_rows["target_role"] = ""
    major_speciation_failures = speciation_rows[
        (speciation_rows["target_role"].astype(str) == "major_fit_or_validation_species")
        & (speciation_rows["passes"].astype(str).str.lower() != "true")
    ]
    pressure_rows = residual_acceptance_audit[residual_acceptance_audit["target_family"] == "pressure"].copy()
    pressure_failures = pressure_rows[
        (pressure_rows["temperature_C"].astype(str).str.lower() != "overall")
        & (pressure_rows["passes"].astype(str).str.lower() != "true")
    ]
    if not major_speciation_failures.empty:
        ideal_reference_status = "model_ran_but_failed_speciation_validation"
    elif not pressure_failures.empty:
        ideal_reference_status = "validated_major_species_speciation_with_pressure_limits"
    else:
        ideal_reference_status = "validated"

    failed = residual_acceptance_audit[
        (residual_acceptance_audit["passes"].astype(str).str.lower() != "true")
        | (residual_acceptance_audit["claim_allowed"].astype(str).str.lower() != "true")
    ]
    failed_targets = (
        failed[["target_family", "temperature_C", "species_or_property"]]
        .drop_duplicates()
        .sort_values(["target_family", "temperature_C", "species_or_property"])
    )
    failed_lines = [
        f"- {row.target_family}: {row.species_or_property} at {row.temperature_C}"
        for row in failed_targets.itertuples(index=False)
    ]
    if not failed_lines:
        failed_lines = ["- No residual acceptance failures were detected by this audit."]

    lineage = """# ideal reaction-equilibrium reference Model Lineage

lineage_status: explicit_ideal_smith_missen_reproduction
ideal_reference_status: {ideal_reference_status}

This artifact solves the explicit five-reaction, nine-species ideal Smith-Missen speciation problem for the ideal reaction-equilibrium reference speciation surface. Activities are set equal to mole fractions, and the solved species are CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and OH-.

The pressure comparison remains a retained legacy PC-SAFT and neutral ePC-SAFT parity surface against Jou data. Pressure claims remain limited by `ideal_reference_residual_acceptance_audit.csv`, especially the lower-temperature rows.
""".format(ideal_reference_status=ideal_reference_status)
    (OUT_DIR / "ideal_reference_model_lineage.md").write_text(lineage, encoding="utf-8")

    claim_boundary = "\n".join(
        [
            "# ideal reaction-equilibrium reference Claim Boundary",
            "",
            f"ideal_reference_status: {ideal_reference_status}",
            "lineage_status: explicit_ideal_smith_missen_reproduction",
            "",
            "Allowed claims:",
            "- The ideal reaction-equilibrium reference speciation workflow solves the explicit five-reaction, nine-species ideal Smith-Missen equilibrium system.",
            "- Major observed speciation species may be used as ideal reaction-equilibrium reference validation evidence where `ideal_reference_residual_acceptance_audit.csv` has `claim_allowed=true`.",
            "- Pressure comparisons may be discussed only where `ideal_reference_residual_acceptance_audit.csv` has `claim_allowed=true`.",
            "",
            "Forbidden claims:",
            "- Do not use trace or unobserved species as successful major-species validation evidence.",
            "- Do not present the lower-temperature pressure rows as validated where their audit rows fail.",
            "- Do not promote this ideal reaction-equilibrium reference baseline to a finalized joint-regression parameter set.",
            "",
            "Residual-gate failures, trace limits, or unobserved targets:",
            *failed_lines,
            "",
        ]
    )
    (OUT_DIR / "ideal_reference_claim_boundary.md").write_text(claim_boundary, encoding="utf-8")


def main() -> int:
    pressure_results, _, residual_acceptance_audit, speciation_curve, speciation_reference_points = _write_curated_tables()
    plot_pressure(pressure_results)
    plot_speciation(speciation_curve, speciation_reference_points)
    write_ideal_reference_reports(residual_acceptance_audit)
    print(f"ideal reaction-equilibrium reference curated artifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
