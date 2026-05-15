from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.data_access import load_speciation_data
from MEA.six_species.chemistry import legacy_true_mole_fractions

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
LEGACY_PROCESSED_DIR = REPO_ROOT / "analyses" / "six_species_legacy" / "data" / "processed"
NEUTRAL_PROCESSED_DIR = REPO_ROOT / "analyses" / "epcsaft_neutral_parity" / "data" / "processed"
MEA_WEIGHT_FRACTION = 0.3
SPECIATION_TEMPERATURES_C = (20.0, 40.0)
SPECIATION_SPECIES = (
    ("CO2", "CO2"),
    ("MEA", "MEA"),
    ("MEAH+", "MEAH^+"),
    ("MEA + MEAH+", "MEA + MEAH^+"),
    ("MEACOO-", "MEACOO^-"),
    ("HCO3-", "HCO3^-"),
    ("CO3^2-", "CO3^2-"),
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
        "C": 22.4773,
        "D": 0.0,
        "temperature_range_K": "273.15-498.15",
        "source_key": "Edwards1978_via_Baygi2015",
        "conversion_required": "no",
        "implemented_in_retained_phase1_solver": "reduced_apparent_solver",
        "notes": "Full five-reaction Phase 1 literature basis. The retained six-species solver exposes a reduced apparent-equilibrium representation rather than five explicit equations.",
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
        "implemented_in_retained_phase1_solver": "reduced_apparent_solver",
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
        "implemented_in_retained_phase1_solver": "reduced_apparent_solver",
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
        "implemented_in_retained_phase1_solver": "reduced_apparent_solver",
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
        "implemented_in_retained_phase1_solver": "reduced_apparent_solver",
        "notes": "Protonated-amine dissociation in the Baygi 2015 Smith-Missen literature basis.",
    },
]


def _require_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite artifact {path}")
    return pd.read_csv(path)


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


def _model_species_map(loading: float, temperature_C: float) -> dict[str, float]:
    x = legacy_true_mole_fractions(float(loading), MEA_WEIGHT_FRACTION, float(temperature_C) + 273.15)
    model = {
        "CO2": float(x[0]),
        "MEA": float(x[1]),
        "H2O": float(x[2]),
        "MEAH+": float(x[3]),
        "MEACOO-": float(x[4]),
        "HCO3-": float(x[5]),
    }
    model["CO3^2-"] = 0.0
    model["MEA + MEAH+"] = model["MEA"] + model["MEAH+"]
    return model


def _phase1_speciation_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    for temperature_C in SPECIATION_TEMPERATURES_C:
        measured = load_speciation_data(
            temperature_C=temperature_C,
            mea_weight_fraction=MEA_WEIGHT_FRACTION,
        )
        for record in measured.to_dict("records"):
            model = _model_species_map(float(record["CO2_loading"]), float(temperature_C))
            source = record.get("source", "Jakobsen")
            for species, column in SPECIATION_SPECIES:
                observed = record.get(column)
                if observed is None or pd.isna(observed):
                    continue
                observed_value = float(observed)
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


def main() -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    pressure_results, pressure_metrics = _phase1_pressure_tables()
    speciation_results, speciation_metrics = _phase1_speciation_tables()
    parameter_table = pd.DataFrame(PURE_PARAMETER_ROWS)
    reaction_table = pd.DataFrame(REACTION_CONSTANT_ROWS)

    outputs = {
        "phase1_pressure_results.csv": pressure_results,
        "phase1_pressure_metrics.csv": pressure_metrics,
        "phase1_speciation_results.csv": speciation_results,
        "phase1_speciation_metrics.csv": speciation_metrics,
        "phase1_parameter_table.csv": parameter_table,
        "phase1_reaction_constant_table.csv": reaction_table,
    }
    for name, frame in outputs.items():
        frame.to_csv(PROCESSED_DIR / name, index=False)

    print(f"Phase 1 processed tables: {PROCESSED_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
