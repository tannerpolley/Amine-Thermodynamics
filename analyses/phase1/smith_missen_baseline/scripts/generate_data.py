from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.data_access import load_speciation_data
from MEA.common.analysis_io import read_required_csv
from MEA.smith_missen.ideal_speciation import SPECIES_9, solve_ideal_speciation_grid

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
LEGACY_PROCESSED_DIR = REPO_ROOT / "analyses" / "phase1" / "six_species_baseline" / "data" / "processed"
NEUTRAL_PROCESSED_DIR = REPO_ROOT / "analyses" / "phase1" / "neutral_epcsaft_parity" / "data" / "processed"
MEA_WEIGHT_FRACTION = 0.3
SPECIATION_TEMPERATURES_C = (20.0, 40.0)
SPECIATION_CURVE_LOADINGS = tuple(float(value) for value in np.linspace(0.0, 0.8, 161))
SPECIATION_SPECIES = (
    ("CO2", "CO2"),
    ("MEA", "MEA"),
    ("MEAH+", "MEAH^+"),
    ("MEA + MEAH+", "MEA + MEAH^+"),
    ("MEACOO-", "MEACOO^-"),
    ("HCO3-", "HCO3^-"),
    ("CO3^2-", "CO3^2-"),
)
SPECIATION_CURVE_SPECIES = (
    "CO2",
    "MEA",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
    "MEA + MEAH+",
)

PURE_PARAMETER_ROWS = [
    {
        "item_id": "MEA_2B",
        "category": "pure_parameter_option",
        "component_or_pair": "MEA",
        "association_scheme": "2B",
        "m": 3.0353,
        "sigma_A": 3.0435,
        "epsilon_K": 277.174,
        "kappa_AB": 0.037470,
        "epsilon_AB_K": 2586.3,
        "k_ij": np.nan,
        "source_key": "Baygi2015",
        "status": "documented_not_selected",
        "phase1_role": "historical association-screening option",
        "notes": "Retained repo neutral parity still uses the inherited 2B molecular row for continuity checks.",
    },
    {
        "item_id": "MEA_3B",
        "category": "pure_parameter_option",
        "component_or_pair": "MEA",
        "association_scheme": "3B",
        "m": 4.5354,
        "sigma_A": 2.6019,
        "epsilon_K": 204.0438,
        "kappa_AB": 0.118488,
        "epsilon_AB_K": 2383.4744,
        "k_ij": np.nan,
        "source_key": "Baygi2015",
        "status": "selected_phase1_literature_choice",
        "phase1_role": "historical Smith-Missen baseline association scheme",
        "notes": "Baygi 2015 selected 3B MEA together with 4C water for the neutral PC-SAFT baseline.",
    },
    {
        "item_id": "MEA_4C",
        "category": "pure_parameter_option",
        "component_or_pair": "MEA",
        "association_scheme": "4C",
        "m": 4.5208,
        "sigma_A": 2.6574,
        "epsilon_K": 237.6864,
        "kappa_AB": 0.187533,
        "epsilon_AB_K": 989.8984,
        "k_ij": np.nan,
        "source_key": "Baygi2015",
        "status": "documented_not_selected",
        "phase1_role": "historical association-screening option",
        "notes": "Documented as a Baygi 2015 screening option but not the selected MEA scheme.",
    },
    {
        "item_id": "H2O_2B",
        "category": "pure_parameter_option",
        "component_or_pair": "H2O",
        "association_scheme": "2B",
        "m": 1.9599,
        "sigma_A": 2.3620,
        "epsilon_K": 279.42,
        "kappa_AB": 0.1750,
        "epsilon_AB_K": 2059.28,
        "k_ij": np.nan,
        "source_key": "Diamantonis2011_via_Baygi2015",
        "status": "documented_not_selected",
        "phase1_role": "historical association-screening option",
        "notes": "Included because Baygi 2015 screened both 2B and 4C water options against MEA-H2O VLE.",
    },
    {
        "item_id": "H2O_4C",
        "category": "pure_parameter_option",
        "component_or_pair": "H2O",
        "association_scheme": "4C",
        "m": 2.1945,
        "sigma_A": 2.2290,
        "epsilon_K": 141.66,
        "kappa_AB": 0.2039,
        "epsilon_AB_K": 1804.17,
        "k_ij": np.nan,
        "source_key": "Diamantonis2011_via_Baygi2015",
        "status": "selected_phase1_literature_choice",
        "phase1_role": "historical Smith-Missen baseline association scheme",
        "notes": "Baygi 2015 selected 4C water together with 3B MEA for the neutral baseline.",
    },
    {
        "item_id": "CO2_nonassociating",
        "category": "pure_parameter_option",
        "component_or_pair": "CO2",
        "association_scheme": "nonassociating",
        "m": 2.0729,
        "sigma_A": 2.7852,
        "epsilon_K": 169.21,
        "kappa_AB": np.nan,
        "epsilon_AB_K": np.nan,
        "k_ij": np.nan,
        "source_key": "Gross2001_via_Baygi2015",
        "status": "selected_phase1_literature_choice",
        "phase1_role": "neutral EOS component",
        "notes": "The Phase 1 baseline inherits the nonassociating CO2 row used in Baygi 2015 and the retained repo baseline.",
    },
    {
        "item_id": "MEA_H2O_binary_selected",
        "category": "binary_interaction_choice",
        "component_or_pair": "MEA-H2O",
        "association_scheme": "MEA 3B / H2O 4C",
        "m": np.nan,
        "sigma_A": np.nan,
        "epsilon_K": np.nan,
        "kappa_AB": np.nan,
        "epsilon_AB_K": np.nan,
        "k_ij": -0.0520,
        "source_key": "Baygi2015",
        "status": "selected_phase1_literature_choice",
        "phase1_role": "binary neutral validation basis",
        "notes": "Baygi 2015 Table 3 identified k_ij=-0.0520 as the best MEA-H2O binary choice for the selected 3B/4C association scheme pair.",
    },
    {
        "item_id": "MEA_H2O_binary_repo_retained",
        "category": "binary_interaction_choice",
        "component_or_pair": "MEA-H2O",
        "association_scheme": "retained repo neutral parity",
        "m": np.nan,
        "sigma_A": np.nan,
        "epsilon_K": np.nan,
        "kappa_AB": np.nan,
        "epsilon_AB_K": np.nan,
        "k_ij": -0.1800,
        "source_key": "src/MEA/epcsaft_neutral/parameters.py",
        "status": "retained_repo_baseline",
        "phase1_role": "neutral parity continuity check",
        "notes": "The retained repo neutral parity workflow keeps the inherited MEA-H2O k_ij row so the translation check remains comparable to the historical local baseline.",
    },
]

REACTION_CONSTANT_ROWS = [
    {
        "reaction_id": "R1",
        "reaction": "2 H2O <-> H3O+ + OH-",
        "constant_basis": "mole_fraction_based",
        "correlation_form": "ln K = A + B/T + C ln(T) + D T",
        "A": 132.899,
        "B": -13445.9,
        "C": -22.4773,
        "D": 0.0,
        "temperature_range_K": "273.15-498.15",
        "source_key": "Edwards1978_via_Baygi2015",
        "conversion_required": "no",
        "implemented_in_phase1_solver": "explicit_ideal_nine_species_solver",
        "notes": "Full five-reaction Phase 1 literature basis. The Phase 1 Smith-Missen workflow solves this explicit ideal nine-species system with activities equal to mole fractions.",
    },
    {
        "reaction_id": "R2",
        "reaction": "CO2 + 2 H2O <-> H3O+ + HCO3-",
        "constant_basis": "mole_fraction_based",
        "correlation_form": "ln K = A + B/T + C ln(T) + D T",
        "A": 231.465,
        "B": -12092.10,
        "C": -36.7816,
        "D": 0.0,
        "temperature_range_K": "273.15-498.15",
        "source_key": "Edwards1978_via_Baygi2015",
        "conversion_required": "no",
        "implemented_in_phase1_solver": "explicit_ideal_nine_species_solver",
        "notes": "CO2 hydration to bicarbonate in the Baygi 2015 Smith-Missen literature basis.",
    },
    {
        "reaction_id": "R3",
        "reaction": "HCO3- + H2O <-> H3O+ + CO3^2-",
        "constant_basis": "mole_fraction_based",
        "correlation_form": "ln K = A + B/T + C ln(T) + D T",
        "A": 216.049,
        "B": -12431.70,
        "C": -35.4819,
        "D": 0.0,
        "temperature_range_K": "273.15-498.15",
        "source_key": "Edwards1978_via_Baygi2015",
        "conversion_required": "no",
        "implemented_in_phase1_solver": "explicit_ideal_nine_species_solver",
        "notes": "Bicarbonate dissociation to carbonate in the Baygi 2015 Smith-Missen literature basis.",
    },
    {
        "reaction_id": "R4",
        "reaction": "MEACOO- + H2O <-> HCO3- + MEA",
        "constant_basis": "mole_fraction_based",
        "correlation_form": "ln K = A + B/T + C ln(T) + D T",
        "A": -1.8652,
        "B": -1545.3,
        "C": 0.0,
        "D": 0.0,
        "temperature_range_K": "293.15-323.15",
        "source_key": "Tong2012_via_Baygi2015",
        "conversion_required": "reported_molality_based_then_converted",
        "implemented_in_phase1_solver": "explicit_ideal_nine_species_solver",
        "notes": "Baygi 2015 states that the original literature form was converted from molality to mole-fraction basis for the ideal-speciation workflow.",
    },
    {
        "reaction_id": "R5",
        "reaction": "MEAH+ + H2O <-> H3O+ + MEA",
        "constant_basis": "mole_fraction_based",
        "correlation_form": "ln K = A + B/T + C ln(T) + D T",
        "A": 2.1211,
        "B": -8189.38,
        "C": 0.0,
        "D": -0.007484,
        "temperature_range_K": "273.15-323.15",
        "source_key": "Bates1951_via_Baygi2015",
        "conversion_required": "no",
        "implemented_in_phase1_solver": "explicit_ideal_nine_species_solver",
        "notes": "Protonated-amine dissociation in the Baygi 2015 Smith-Missen literature basis.",
    },
]


def _require_csv(path: Path) -> pd.DataFrame:
    return read_required_csv(path, hint="Run the upstream prerequisite analysis first")


def _summarize_pressure(
    frame: pd.DataFrame, *, observed_col: str, predicted_col: str
) -> pd.DataFrame:
    grouped = []
    for (model_family, temperature_C), subset in frame.groupby(["model_family", "temperature_C"], sort=True):
        residual = subset["log10_pred_over_obs"].to_numpy(dtype=float)
        diff = subset[predicted_col].to_numpy(dtype=float) - subset[observed_col].to_numpy(dtype=float)
        grouped.append(
            {
                "model_family": model_family,
                "temperature_C": temperature_C,
                "record_count": int(len(subset)),
                "median_abs_log10_error": float(np.nanmedian(np.abs(residual))),
                "median_log10_pred_over_obs": float(np.nanmedian(residual)),
                "mae_kPa": float(np.nanmean(np.abs(diff))),
                "rmse_kPa": float(np.sqrt(np.nanmean(diff * diff))),
            }
        )
    metrics = pd.DataFrame(grouped).sort_values(["model_family", "temperature_C"]).reset_index(drop=True)
    overall_rows = []
    for model_family, subset in frame.groupby("model_family", sort=True):
        residual = subset["log10_pred_over_obs"].to_numpy(dtype=float)
        diff = subset[predicted_col].to_numpy(dtype=float) - subset[observed_col].to_numpy(dtype=float)
        overall_rows.append(
            {
                "model_family": model_family,
                "temperature_C": "overall",
                "record_count": int(len(subset)),
                "median_abs_log10_error": float(np.nanmedian(np.abs(residual))),
                "median_log10_pred_over_obs": float(np.nanmedian(residual)),
                "mae_kPa": float(np.nanmean(np.abs(diff))),
                "rmse_kPa": float(np.sqrt(np.nanmean(diff * diff))),
            }
        )
    return pd.concat([metrics, pd.DataFrame(overall_rows)], ignore_index=True)


def _phase1_pressure_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    legacy_metrics = _require_csv(LEGACY_PROCESSED_DIR / "legacy_pcsaft_jou_fit_metrics.csv")
    neutral_metrics = _require_csv(NEUTRAL_PROCESSED_DIR / "epcsaft_neutral_jou_parity_metrics.csv")

    legacy = legacy_metrics.rename(
        columns={
            "observed_CO2_pressure_kPa": "observed_CO2_pressure_kPa",
            "pred_CO2_pressure_kPa": "predicted_CO2_pressure_kPa",
            "log10_pred_over_obs": "log10_pred_over_obs",
        }
    ).copy()
    legacy["model_family"] = "legacy_pcsaft_smith_missen"

    neutral = neutral_metrics.rename(
        columns={
            "observed_CO2_pressure_kPa": "observed_CO2_pressure_kPa",
            "epcsaft_CO2_pressure_kPa": "predicted_CO2_pressure_kPa",
            "epcsaft_log10_pred_over_obs": "log10_pred_over_obs",
        }
    )[
        [
            "temperature_C",
            "MEA_weight_fraction",
            "CO2_loading",
            "observed_CO2_pressure_kPa",
            "predicted_CO2_pressure_kPa",
            "log10_pred_over_obs",
        ]
    ].copy()
    neutral["model_family"] = "neutral_epcsaft_parity"

    pressure_results = pd.concat([legacy, neutral], ignore_index=True)
    pressure_results = pressure_results[
        [
            "model_family",
            "temperature_C",
            "MEA_weight_fraction",
            "CO2_loading",
            "observed_CO2_pressure_kPa",
            "predicted_CO2_pressure_kPa",
            "log10_pred_over_obs",
        ]
    ].sort_values(["model_family", "temperature_C", "CO2_loading"]).reset_index(drop=True)

    pressure_metrics = _summarize_pressure(
        pressure_results,
        observed_col="observed_CO2_pressure_kPa",
        predicted_col="predicted_CO2_pressure_kPa",
    )
    return pressure_results, pressure_metrics


def _phase1_speciation_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    for temperature_C in SPECIATION_TEMPERATURES_C:
        measured = load_speciation_data(
            temperature_C=temperature_C,
            mea_weight_fraction=MEA_WEIGHT_FRACTION,
        ).sort_values("CO2_loading")
        solutions = solve_ideal_speciation_grid(
            measured["CO2_loading"].astype(float).to_numpy(),
            MEA_WEIGHT_FRACTION,
            float(temperature_C) + 273.15,
        )
        for record, solution in zip(measured.to_dict("records"), solutions):
            model = solution.species_map()
            source = record.get("source", "Jakobsen")
            for species, column in SPECIATION_SPECIES:
                observed = record.get(column)
                if observed is None or pd.isna(observed):
                    continue
                observed_value = float(observed)
                if observed_value <= 0.0:
                    continue
                model_value = float(model[species])
                rows.append(
                    {
                        "source": source,
                        "temperature_C": float(temperature_C),
                        "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
                        "CO2_loading": float(record["CO2_loading"]),
                        "species": species,
                        "observed_mole_fraction": observed_value,
                        "model_mole_fraction": model_value,
                        "log10_model_over_data": float(
                            np.log10(max(model_value, 1.0e-30) / max(observed_value, 1.0e-30))
                        ),
                        "solver_success": str(solution.success).lower(),
                        "solver_max_abs_residual": solution.max_abs_residual,
                    }
                )

    results = pd.DataFrame(rows).sort_values(["temperature_C", "species", "CO2_loading"]).reset_index(drop=True)
    metric_rows = []
    for (temperature_C, species), subset in results.groupby(["temperature_C", "species"], sort=True):
        residual = subset["log10_model_over_data"].to_numpy(dtype=float)
        metric_rows.append(
            {
                "temperature_C": temperature_C,
                "species": species,
                "record_count": int(len(subset)),
                "median_abs_log10_error": float(np.nanmedian(np.abs(residual))),
                "median_log10_model_over_data": float(np.nanmedian(residual)),
                "mae_log10": float(np.nanmean(np.abs(residual))),
                "rmse_log10": float(np.sqrt(np.nanmean(residual * residual))),
            }
        )
    metrics = pd.DataFrame(metric_rows).sort_values(["temperature_C", "species"]).reset_index(drop=True)
    return results, metrics


def _phase1_speciation_curve_table() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for temperature_C in SPECIATION_TEMPERATURES_C:
        solutions = solve_ideal_speciation_grid(
            SPECIATION_CURVE_LOADINGS,
            MEA_WEIGHT_FRACTION,
            float(temperature_C) + 273.15,
        )
        for loading, solution in zip(SPECIATION_CURVE_LOADINGS, solutions):
            model = solution.species_map()
            for species in SPECIATION_CURVE_SPECIES:
                rows.append(
                    {
                        "temperature_C": float(temperature_C),
                        "MEA_weight_fraction": MEA_WEIGHT_FRACTION,
                        "CO2_loading": float(loading),
                        "species": species,
                        "mole_fraction": float(max(model.get(species, 0.0), 1.0e-30)),
                        "curve_role": "explicit_ideal_equilibrium_curve",
                        "solver_success": str(solution.success).lower(),
                        "solver_max_abs_residual": solution.max_abs_residual,
                    }
                )
    return pd.DataFrame(rows)


def _phase1_speciation_reference_points(speciation_results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in speciation_results.to_dict("records"):
        rows.append(
            {
                "source": row["source"],
                "temperature_C": row["temperature_C"],
                "MEA_weight_fraction": row["MEA_weight_fraction"],
                "CO2_loading": row["CO2_loading"],
                "species": row["species"],
                "mole_fraction": row["observed_mole_fraction"],
                "point_role": "reference_point",
            }
        )
    return pd.DataFrame(rows)


def _pressure_acceptance_rows(pressure_results: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    groups: list[tuple[str, object, pd.DataFrame]] = []
    for (model_family, temperature_C), subset in pressure_results.groupby(["model_family", "temperature_C"], sort=True):
        groups.append((str(model_family), temperature_C, subset))
    for model_family, subset in pressure_results.groupby("model_family", sort=True):
        groups.append((str(model_family), "overall", subset))

    for model_family, temperature_C, subset in groups:
        residual = subset["log10_pred_over_obs"].to_numpy(dtype=float)
        observed = subset["observed_CO2_pressure_kPa"].to_numpy(dtype=float)
        predicted = subset["predicted_CO2_pressure_kPa"].to_numpy(dtype=float)
        aad_percent = float(np.nanmean(np.abs(predicted - observed) / observed) * 100.0)
        median_abs = float(np.nanmedian(np.abs(residual)))
        rmse_log10 = float(np.sqrt(np.nanmean(residual * residual)))
        max_abs = float(np.nanmax(np.abs(residual)))
        pressure_pass = aad_percent <= 50.0 or median_abs <= 0.25
        for metric, actual, threshold in (
            ("AAD_percent", aad_percent, "pass if AAD_percent <= 50 OR median_abs_log10_error <= 0.25"),
            ("median_abs_log10_error", median_abs, "pass if AAD_percent <= 50 OR median_abs_log10_error <= 0.25"),
            ("RMSE_log10", rmse_log10, "reported; no independent pass threshold"),
            ("max_abs_log10_error", max_abs, "reported; no independent pass threshold"),
        ):
            rows.append(
                {
                    "target_family": "pressure",
                    "source_or_model": model_family,
                    "temperature_C": temperature_C,
                    "species_or_property": "CO2_pressure",
                    "metric": metric,
                    "threshold": threshold,
                    "actual_value": actual,
                    "passes": str(pressure_pass).lower(),
                    "claim_allowed": str(pressure_pass).lower(),
                    "failure_reason": "" if pressure_pass else "pressure residual gate failed",
                    "recommended_manuscript_use": (
                        "retained baseline pressure comparison"
                        if pressure_pass
                        else "diagnostic only; do not cite as validated pressure reproduction"
                    ),
                }
            )
    return rows


def _speciation_acceptance_rows(speciation_results: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    trace_or_unobserved_species = {"CO2", "CO3^2-", "H3O+", "OH-"}

    groups: list[tuple[object, str, pd.DataFrame]] = []
    for (temperature_C, species), subset in speciation_results.groupby(["temperature_C", "species"], sort=True):
        groups.append((temperature_C, str(species), subset))
    for species, subset in speciation_results.groupby("species", sort=True):
        groups.append(("overall", str(species), subset))

    for temperature_C, species, subset in groups:
        residual = subset["log10_model_over_data"].to_numpy(dtype=float)
        median_abs = float(np.nanmedian(np.abs(residual)))
        mae = float(np.nanmean(np.abs(residual)))
        rmse = float(np.sqrt(np.nanmean(residual * residual)))
        residual_pass = median_abs <= 0.50 and mae <= 0.75
        trace_limited = species in trace_or_unobserved_species
        claim_allowed = residual_pass and not trace_limited
        failure_reason = ""
        if trace_limited:
            failure_reason = (
                "trace species is solved and plotted but is not used as major-species validation evidence"
                if residual_pass
                else "trace species residual gate failed"
            )
        elif not residual_pass:
            failure_reason = "speciation residual gate failed"
        for metric, actual, threshold in (
            ("median_abs_log10_error", median_abs, "median_abs_log10_error <= 0.50 AND mae_log10 <= 0.75"),
            ("mae_log10", mae, "median_abs_log10_error <= 0.50 AND mae_log10 <= 0.75"),
            ("RMSE_log10", rmse, "reported; no independent pass threshold"),
        ):
            rows.append(
                {
                    "target_family": "speciation",
                    "source_or_model": "explicit_ideal_nine_species_smith_missen_solver",
                    "temperature_C": temperature_C,
                    "species_or_property": species,
                    "target_role": "trace_species" if trace_limited else "major_fit_or_validation_species",
                    "metric": metric,
                    "threshold": threshold,
                    "actual_value": actual,
                    "passes": str(residual_pass).lower(),
                    "claim_allowed": str(claim_allowed).lower(),
                    "failure_reason": failure_reason,
                    "recommended_manuscript_use": (
                        "major-species retained baseline comparison"
                        if claim_allowed
                        else "do not cite as major validated species evidence"
                    ),
                }
            )

    for species in ("H3O+", "OH-"):
        rows.append(
            {
                "target_family": "speciation",
                "source_or_model": "explicit_ideal_nine_species_smith_missen_solver",
                "temperature_C": "overall",
                "species_or_property": species,
                "target_role": "explicitly_solved_unobserved_species",
                "metric": "not_evaluated",
                "threshold": "no direct observed Phase 1 reference data in current target table",
                "actual_value": np.nan,
                "passes": "false",
                "claim_allowed": "false",
                "failure_reason": "explicitly solved and plotted but not directly observed in Phase 1 reference rows",
                "recommended_manuscript_use": "plot as equilibrium trace curve only; do not cite as observed validation evidence",
            }
        )
    return rows


def _phase1_residual_acceptance_audit(
    pressure_results: pd.DataFrame,
    speciation_results: pd.DataFrame,
) -> pd.DataFrame:
    rows = _pressure_acceptance_rows(pressure_results)
    rows.extend(_speciation_acceptance_rows(speciation_results))
    return pd.DataFrame(rows)


def main() -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    pressure_results, pressure_metrics = _phase1_pressure_tables()
    speciation_results, speciation_metrics = _phase1_speciation_tables()
    speciation_curve = _phase1_speciation_curve_table()
    speciation_reference_points = _phase1_speciation_reference_points(speciation_results)
    parameter_table = pd.DataFrame(PURE_PARAMETER_ROWS)
    reaction_table = pd.DataFrame(REACTION_CONSTANT_ROWS)
    residual_acceptance_audit = _phase1_residual_acceptance_audit(pressure_results, speciation_results)

    outputs = {
        "phase1_pressure_results.csv": pressure_results,
        "phase1_pressure_metrics.csv": pressure_metrics,
        "phase1_speciation_results.csv": speciation_results,
        "phase1_speciation_metrics.csv": speciation_metrics,
        "phase1_speciation_curve.csv": speciation_curve,
        "phase1_speciation_reference_points.csv": speciation_reference_points,
        "phase1_parameter_table.csv": parameter_table,
        "phase1_reaction_constant_table.csv": reaction_table,
        "phase1_residual_acceptance_audit.csv": residual_acceptance_audit,
    }
    for name, frame in outputs.items():
        frame.to_csv(PROCESSED_DIR / name, index=False)

    print(f"Phase 1 processed tables: {PROCESSED_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
