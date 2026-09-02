from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.smith_missen.ideal_speciation import (  # noqa: E402
    REACTION_CONSTANTS,
    REACTION_MATRIX,
    REDUCED_REACTION_MATRIX,
    SPECIES_6,
    SPECIES_9,
    solve_ideal_speciation,
    solve_reduced_ideal_speciation,
)

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ANALYSIS_DIR / "results"
REACTION_MANIFEST = REPO_ROOT / "data/reference/MEA/manifests/reaction_constant_manifest.csv"
VLE_PATH = REPO_ROOT / "data/reference/MEA/observations/vapor_liquid_equilibrium/Combined_VLE.csv"
SPECIATION_PATH = REPO_ROOT / "data/reference/MEA/observations/liquid_speciation/Combined_ChEq.csv"

MEA_WEIGHT_FRACTION = 0.30
SOLVER_TOLERANCE = 1.0e-8
COMMON_SPECIES = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-")
OMITTED_SPECIES = ("CO3^2-", "H3O+", "OH-")
OBSERVED_COLUMNS = {
    "CO2": "CO2",
    "MEA": "MEA",
    "MEAH+": "MEAH^+",
    "MEACOO-": "MEACOO^-",
    "HCO3-": "HCO3^-",
    "CO3^2-": "CO3^2-",
}
MODEL_NAMES = ("ideal_9_species", "ideal_6_species")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reaction_data() -> tuple[pd.DataFrame, np.ndarray]:
    manifest = pd.read_csv(REACTION_MANIFEST)
    if tuple(manifest["reaction_id"]) != ("R1", "R2", "R3", "R4", "R5"):
        raise RuntimeError("reaction manifest order changed")
    columns = ["A", "B", "C", "D"]
    coefficients = manifest[columns].to_numpy(dtype=float)
    np.testing.assert_allclose(coefficients, REACTION_CONSTANTS, rtol=0.0, atol=1.0e-12)
    reduction = np.array(
        [
            [0.0, 1.0, 0.0, -1.0, -1.0],
            [0.0, 1.0, 0.0, 0.0, -1.0],
        ]
    )
    reduced = reduction @ coefficients
    common_indices = [SPECIES_9.index(species) for species in SPECIES_6]
    np.testing.assert_allclose(
        reduction @ REACTION_MATRIX,
        np.vstack((
            np.array([-1, -2, 0, 1, 1, 0, 0, 0, 0]),
            np.array([-1, -1, -1, 1, 0, 1, 0, 0, 0]),
        )),
        rtol=0.0,
        atol=1.0e-12,
    )
    np.testing.assert_allclose(reduction @ REACTION_MATRIX[:, common_indices], REDUCED_REACTION_MATRIX)
    rows = manifest.assign(
        species_count=9,
        coefficient_set="ideal_9_source_manifest",
        source_reaction_ids=manifest["reaction_id"],
        source_status="reference-backed",
    )[["reaction_id", "species_count", "coefficient_set", "source_reaction_ids", "source_key", "source_status", *columns]]
    reduced_rows = pd.DataFrame(
        [
            {
                "reaction_id": reaction_id,
                "species_count": 6,
                "coefficient_set": "ideal_6_derived_from_9",
                "source_reaction_ids": source_reaction_ids,
                "source_key": "derived_from_reaction_constant_manifest",
                "source_status": "inference",
                **dict(zip(columns, values, strict=True)),
            }
            for reaction_id, source_reaction_ids, values in (
                ("R6-carbamate-formation", "R2-R4-R5", reduced[0]),
                ("R6-bicarbonate-formation", "R2-R5", reduced[1]),
            )
        ]
    )
    return pd.concat((rows, reduced_rows), ignore_index=True), reduced


def _state_table() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for family, path in (("vle", VLE_PATH), ("speciation", SPECIATION_PATH)):
        frame = pd.read_csv(path)
        source_column = "source" if "source" in frame else "source_key"
        required = {source_column, "temperature", "CO2_loading"}
        if not required.issubset(frame.columns):
            raise RuntimeError(f"{path} is missing {sorted(required - set(frame.columns))}")
        for index, record in frame.iterrows():
            rows.append(
                {
                    "state_id": f"{family}:{index}:{record[source_column]}:{float(record['temperature']):g}:{float(record['CO2_loading']):.8g}",
                    "state_family": family,
                    "source": str(record[source_column]),
                    "temperature_C": float(record["temperature"]),
                    "CO2_loading": float(record["CO2_loading"]),
                }
            )
    return (
        pd.DataFrame(rows)
        .drop_duplicates(["state_family", "source", "temperature_C", "CO2_loading"])
        .sort_values(["state_family", "temperature_C", "CO2_loading", "source"])
        .reset_index(drop=True)
    )


def _totals(species: tuple[str, ...], x: np.ndarray) -> dict[str, float]:
    values = dict(zip(species, x, strict=True))
    return {
        "carbon_total": sum(values.get(name, 0.0) for name in ("CO2", "MEACOO-", "HCO3-", "CO3^2-")),
        "amine_total": sum(values.get(name, 0.0) for name in ("MEA", "MEAH+", "MEACOO-")),
        "water_total": sum(values.get(name, 0.0) for name in ("H2O", "HCO3-", "CO3^2-", "H3O+", "OH-")),
        "charge_total": values.get("MEAH+", 0.0) + values.get("H3O+", 0.0) - values.get("MEACOO-", 0.0) - values.get("HCO3-", 0.0) - 2.0 * values.get("CO3^2-", 0.0) - values.get("OH-", 0.0),
    }


def _solve(model: str, state: dict[str, object], reduced: np.ndarray):
    temperature_K = float(state["temperature_C"]) + 273.15
    if model == "ideal_9_species":
        return solve_ideal_speciation(float(state["CO2_loading"]), MEA_WEIGHT_FRACTION, temperature_K)
    return solve_reduced_ideal_speciation(float(state["CO2_loading"]), MEA_WEIGHT_FRACTION, temperature_K, reduced)


def _ideal_results(states: pd.DataFrame, reduced: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    value_rows: list[dict[str, object]] = []
    diagnostic_rows: list[dict[str, object]] = []
    for state in states.to_dict("records"):
        for model in MODEL_NAMES:
            result = _solve(model, state, reduced)
            species = SPECIES_9 if model == "ideal_9_species" else SPECIES_6
            x = np.asarray(result.mole_fractions, dtype=float)
            totals = _totals(species, x)
            residuals = result.residuals
            reaction = [abs(value) for key, value in residuals.items() if key.endswith("_ln_residual")]
            balance = [abs(value) for key, value in residuals.items() if key.endswith("_residual") and not key.endswith("_ln_residual")]
            diagnostic_rows.append(
                {
                    **state,
                    "model": model,
                    "solver_success": bool(result.success),
                    "max_abs_residual": float(result.max_abs_residual),
                    "max_abs_reaction_residual": max(reaction),
                    "max_abs_balance_residual": max(balance),
                    "normalization_residual": float(np.sum(x) - 1.0),
                    **totals,
                }
            )
            values = dict(zip(species, x, strict=True))
            for name in (*COMMON_SPECIES, *OMITTED_SPECIES):
                value_rows.append(
                    {
                        **state,
                        "model": model,
                        "species": name,
                        "species_present": name in values,
                        "mole_fraction": values.get(name, 0.0),
                        "amount_per_mol_initial_MEA": values.get(name, 0.0) / totals["amine_total"],
                        "solver_success": bool(result.success),
                        "max_abs_residual": float(result.max_abs_residual),
                    }
                )
    return pd.DataFrame(value_rows), pd.DataFrame(diagnostic_rows)


def _comparison(values: pd.DataFrame) -> pd.DataFrame:
    index = ["state_id", "state_family", "source", "temperature_C", "CO2_loading"]
    wide = values.pivot(index=index + ["species"], columns="model", values="amount_per_mol_initial_MEA").reset_index()
    wide = wide.rename(columns={"ideal_9_species": "nine_amount_per_mol_initial_MEA", "ideal_6_species": "six_amount_per_mol_initial_MEA"})
    for column in ("nine_amount_per_mol_initial_MEA", "six_amount_per_mol_initial_MEA"):
        if column not in wide:
            wide[column] = 0.0
        wide[column] = wide[column].fillna(0.0)
    wide["nine_minus_six_amount_per_mol_initial_MEA"] = wide["nine_amount_per_mol_initial_MEA"] - wide["six_amount_per_mol_initial_MEA"]
    return wide.sort_values(index + ["species"]).reset_index(drop=True)


def _inventory(comparison: pd.DataFrame) -> pd.DataFrame:
    index = ["state_id", "state_family", "source", "temperature_C", "CO2_loading"]
    return comparison[comparison["species"].isin(OMITTED_SPECIES)].pivot(index=index, columns="species", values="nine_amount_per_mol_initial_MEA").reset_index().rename_axis(None, axis=1).assign(omitted_total_amount_per_mol_initial_MEA=lambda frame: frame[list(OMITTED_SPECIES)].sum(axis=1)).sort_values(["state_family", "temperature_C", "CO2_loading", "source"])


def _observed(comparison: pd.DataFrame) -> pd.DataFrame:
    observations = pd.read_csv(SPECIATION_PATH)
    rows: list[dict[str, object]] = []
    for row in comparison[comparison["state_family"] == "speciation"].to_dict("records"):
        match = observations[(observations["source"].astype(str) == row["source"]) & (observations["temperature"] == row["temperature_C"]) & (observations["CO2_loading"] == row["CO2_loading"])]
        column = OBSERVED_COLUMNS.get(row["species"])
        observed = float(match.iloc[0][column]) if column and not match.empty and pd.notna(match.iloc[0][column]) else np.nan
        for model, prediction in (("ideal_9_species", row["nine_amount_per_mol_initial_MEA"]), ("ideal_6_species", row["six_amount_per_mol_initial_MEA"])):
            rows.append({**{key: row[key] for key in ("state_id", "source", "temperature_C", "CO2_loading", "species")}, "model": model, "observed_mole_fraction": observed, "predicted_amount_per_mol_initial_MEA": prediction, "observation_role": "direct_zero" if pd.notna(observed) and observed == 0.0 else "direct_positive" if pd.notna(observed) and observed > 0.0 else "not_observed", "log10_predicted_over_observed": np.log10(prediction / observed) if pd.notna(observed) and observed > 0.0 and prediction > 0.0 else np.nan})
    return pd.DataFrame(rows)


def _reports(diagnostics: pd.DataFrame, comparison: pd.DataFrame, inventory: pd.DataFrame, observed: pd.DataFrame) -> None:
    direct = observed[observed["observation_role"] == "direct_positive"]
    metrics = []
    for (model, species), subset in direct.groupby(["model", "species"], sort=True):
        residual = subset["log10_predicted_over_observed"].dropna().to_numpy()
        metrics.append({"model": model, "species": species, "row_count": len(residual), "median_abs_log10_error": np.median(np.abs(residual)) if len(residual) else np.nan, "rmse_log10_error": np.sqrt(np.mean(residual**2)) if len(residual) else np.nan})
    pd.DataFrame(metrics).to_csv(RESULTS_DIR / "observed_speciation_metrics.csv", index=False, lineterminator="\n")
    maximum_delta = float(comparison[comparison["species"].isin(COMMON_SPECIES)]["nine_minus_six_amount_per_mol_initial_MEA"].abs().max())
    summary = f"""# Matched six- and nine-species experiment

status: verified_ideal_lane; ePCSAFT_lane_is_retained_separately
question: quantify the species-set effect while holding source chemistry and feed fixed
states: {len(diagnostics) // 2} unique canonical VLE/ChEq coordinate rows
models: ideal_9_species and ideal_6_species
basis: true-species mole fractions and amount per mol initial MEA
feed: 30 wt% MEA in water; loading is mol CO2/mol initial MEA
solver_tolerance: {SOLVER_TOLERANCE:.1e}
maximum_ideal_solver_residual: {float(diagnostics['max_abs_residual'].max()):.6e}
maximum_common_species_absolute_delta: {maximum_delta:.6e}
maximum_omitted_nine_species_inventory: {float(inventory['omitted_total_amount_per_mol_initial_MEA'].max()):.6e}

The ideal nine-species coefficients are read from the source-controlled reaction manifest. The ideal six-species coefficients are the exact R2-R4-R5 and R2-R5 projections; no sibling fit is substituted. The ePCSAFT liquid lane is generated by the separate disposable SciPy bridge and retained in `epcsaft_scipy_*.csv`.
"""
    (RESULTS_DIR / "comparison_summary.md").write_text(summary, encoding="utf-8")
    (RESULTS_DIR / "model_lineage.md").write_text(
        f"""# Model lineage

ideal_9_species: reference-backed `reaction_constant_manifest.csv` plus Smith-Missen ideal solver
ideal_6_species: exact projection of the same nine-species reactions; derived rows are inference
liquid_activity: ideal, a_i = x_i
comparison_basis: amount per mol initial MEA
maximum_solver_residual: {float(diagnostics['max_abs_residual'].max()):.6e}
reaction_manifest_sha256: {_sha256(REACTION_MANIFEST)}
""",
        encoding="utf-8",
    )
    (RESULTS_DIR / "experiment_contract.md").write_text(
        """# Experiment contract

Primary experiment: compare nine and six species at identical temperature, loading, feed, reaction source, and reporting basis. The ideal lane uses the source manifest and exact six-species reaction projection. The activity-aware lane uses the Engine candidate EOS for both species sets, the same source-standard-state transfer, and a temporary SciPy equilibrium solve enforcing material-balance ratios, charge balance, and reaction affinities.

The comparison is diagnostic. The Engine packet remains a provisional candidate, and the temporary SciPy bridge is not production chemistry or a parameter-adoption path. VLE pressure claims require a separate matched bubble calculation and are not inferred from this fixed-T,P lane.
""",
        encoding="utf-8",
    )


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    coefficients, reduced = _reaction_data()
    states = _state_table()
    values, diagnostics = _ideal_results(states, reduced)
    comparison = _comparison(values)
    inventory = _inventory(comparison)
    observed = _observed(comparison)
    coefficients.to_csv(RESULTS_DIR / "reaction_coefficients.csv", index=False, lineterminator="\n")
    states.to_csv(RESULTS_DIR / "comparison_states.csv", index=False, lineterminator="\n")
    values.to_csv(RESULTS_DIR / "state_species_results.csv", index=False, lineterminator="\n")
    diagnostics.to_csv(RESULTS_DIR / "solve_diagnostics.csv", index=False, lineterminator="\n")
    comparison.to_csv(RESULTS_DIR / "common_species_comparison.csv", index=False, lineterminator="\n")
    inventory.to_csv(RESULTS_DIR / "omitted_species_inventory.csv", index=False, lineterminator="\n")
    observed.to_csv(RESULTS_DIR / "observed_speciation_results.csv", index=False, lineterminator="\n")
    _reports(diagnostics, comparison, inventory, observed)
    pd.DataFrame([{"artifact": path, "role": role, "sha256": _sha256(REPO_ROOT / path)} for path, role in (("data/reference/MEA/manifests/reaction_constant_manifest.csv", "nine-species reaction source"), ("data/reference/MEA/observations/vapor_liquid_equilibrium/Combined_VLE.csv", "VLE state coordinates"), ("data/reference/MEA/observations/liquid_speciation/Combined_ChEq.csv", "ChEq state coordinates and observations"))]).to_csv(RESULTS_DIR / "source_manifest.csv", index=False, lineterminator="\n")
    print(f"Generated ideal matched six- and nine-species results under {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
