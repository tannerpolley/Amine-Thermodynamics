from __future__ import annotations

import csv
import importlib.metadata
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from MEA.epcsaft_ionic.model import (
    SPECIES_INDEX,
    load_speciation_targets,
    load_vle_targets,
    reaction_definitions_from_coefficients,
    solve_activity_speciation,
    solve_reactive_bubble_targets,
)
from MEA.smith_missen.ideal_speciation import solve_ideal_speciation

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
RESULTS_DIR = ANALYSIS_DIR / "results"
REACTION_MANIFEST = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_reaction_constant_manifest.csv"
ACTIVITY_CANDIDATES = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_activity_constant_candidates.csv"
SOURCE_VERIFICATION = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_reaction_constant_source_verification.csv"
PARAMETER_DATASET = REPO_ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_phase2"
PARAMETER_MANIFEST = PARAMETER_DATASET / "phase2_parameter_artifact_manifest.csv"
MEA_REFERENCE = REPO_ROOT / "data" / "reference" / "MEA"
STALE_SCAFFOLD_PATTERNS = (
    "phase2_speciation_scaffold_curve.csv",
    "phase2_speciation_scaffold_*C.png",
    "phase2_speciation_scaffold_*C.svg",
    "phase2_speciation_scaffold_*C.mpl.yaml",
    "phase2_speciation_scaffold_*C_plot_data.csv",
)

SPECIES = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
CHARGES = {"CO2": 0, "MEA": 0, "H2O": 0, "MEAH+": 1, "MEACOO-": -1, "HCO3-": -1, "CO3^2-": -2, "H3O+": 1, "OH-": -1}
VOLATILE_SPECIES = ("CO2", "H2O", "MEA")
NONVOLATILE_SPECIES = tuple(species for species in SPECIES if species not in VOLATILE_SPECIES)
MATERIAL_BALANCES = {
    "total_amine": {"MEA": 1.0, "MEAH+": 1.0, "MEACOO-": 1.0},
    "total_carbon": {"CO2": 1.0, "MEACOO-": 1.0, "HCO3-": 1.0, "CO3^2-": 1.0},
}
CONSTRAINTS = {
    "electroneutrality": {
        "MEAH+": 1.0,
        "H3O+": 1.0,
        "MEACOO-": -1.0,
        "HCO3-": -1.0,
        "CO3^2-": -2.0,
        "OH-": -1.0,
    },
}
SPECIATION_PLOT_SPECIES = tuple(species for species in SPECIES if species != "H2O") + ("MEA + MEAH+",)
REACTION_NAME_BY_ID = {
    "R1": "R1_water_autoionization",
    "R2": "R2_CO2_to_HCO3",
    "R3": "R3_HCO3_to_CO3",
    "R4": "R4_MEACOO_hydrolysis",
    "R5": "R5_MEAH_dissociation",
}
CURVE_LOADINGS = np.linspace(0.0, 0.8, 161)
CURVE_MIN_LOADING_BY_TEMPERATURE_C = {
    20.0: 0.02,
    40.0: 0.005,
    60.0: 0.001,
    80.0: 0.001,
}
CURVE_MAX_LOADING_BY_TEMPERATURE_C = {
    20.0: 0.795,
    40.0: 0.8,
    60.0: 0.8,
    80.0: 0.8,
}
MAJOR_SPECIATION_SPECIES = ("MEA", "MEAH+", "MEACOO-", "HCO3-", "MEA + MEAH+")
PHASE2_PRESSURE_SOURCES = ("Aronu", "Hilliard", "Idris", "Jou", "Mamun", "Xu")
PHASE2_SPECIATION_SOURCES = ("Bottinger", "Jakobsen", "Matin")
SOURCE_RESIDUAL_SUMMARY_FIELDNAMES = [
    "phase",
    "model_family",
    "observable_family",
    "source",
    "species_or_property",
    "target_role",
    "state_count",
    "target_count",
    "solver_success_count",
    "median_abs_log10",
    "rmse_log10",
    "max_abs_log10",
    "max_model_mole_fraction_for_reported_zero",
    "metric",
]
PRESSURE_MEDIAN_ABS_LOG10_THRESHOLD = 0.5
SPECIATION_MEDIAN_ABS_LOG10_THRESHOLD = 0.5
SPECIATION_REPORTED_ZERO_ABS_THRESHOLD = 0.002
SOLVER_SUCCESS_FRACTION_THRESHOLD = 1.0
PHASE2_SPECIES_INITIAL_MIN = 1.0e-8
PHASE2_SOLVER_TOLERANCE = 1.0e-6
PHASE2_REACTION_TOLERANCE = 1.0e-6
LOG_RESIDUAL_TARGET_ROLES = {"direct_positive", "aggregate_direct_positive"}
ZERO_TARGET_ROLES = {"direct_zero", "aggregate_direct_zero"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise RuntimeError(f"Missing required Phase 2 input: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows available for required Phase 2 artifact: {path}")
    fieldnames = list(rows[0].keys())
    for row in rows[1:]:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    write_csv(path, rows, fieldnames)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def remove_stale_scaffold_outputs() -> None:
    for root in (PROCESSED_DIR, RESULTS_DIR):
        root.mkdir(parents=True, exist_ok=True)
        for pattern in STALE_SCAFFOLD_PATTERNS:
            for path in root.glob(pattern):
                path.unlink()


def dataset_species() -> list[str]:
    rows = read_csv(PARAMETER_DATASET / "pure" / "any_solvent.csv")
    species = [row["component"] for row in rows]
    missing = [item for item in SPECIES if item not in species]
    extra = [item for item in species if item not in SPECIES]
    if missing or extra:
        raise RuntimeError(f"Phase 2 parameter species mismatch. missing={missing}; extra={extra}")
    return species


def reaction_rows() -> list[dict[str, str]]:
    rows = read_csv(REACTION_MANIFEST)
    reaction_ids = [row["reaction_id"] for row in rows]
    if reaction_ids != ["R1", "R2", "R3", "R4", "R5"]:
        raise RuntimeError(f"Unexpected Phase 2 reaction IDs: {reaction_ids}")
    return rows


def activity_candidate_rows() -> list[dict[str, str]]:
    rows = read_csv(ACTIVITY_CANDIDATES)
    reaction_ids = [row["reaction_id"] for row in rows]
    if reaction_ids != ["R1", "R2", "R3", "R4", "R5"]:
        raise RuntimeError(f"Unexpected Phase 2 activity-candidate IDs: {reaction_ids}")
    return rows


def source_verification_rows() -> list[dict[str, str]]:
    rows = read_csv(SOURCE_VERIFICATION)
    reaction_ids = [row["reaction_id"] for row in rows]
    if reaction_ids != ["R1", "R2", "R3", "R4", "R5"]:
        raise RuntimeError(f"Unexpected Phase 2 source-verification IDs: {reaction_ids}")
    invalid = [row for row in rows if row["source_status"] != "source_verified"]
    if invalid:
        ids = [row["reaction_id"] for row in invalid]
        raise RuntimeError(f"Phase 2 source values are not verified for: {ids}")
    return rows


def epcsaft_source_detail() -> dict[str, Any]:
    try:
        dist = importlib.metadata.distribution("epcsaft")
        direct_url = dist.read_text("direct_url.json")
        payload = json.loads(direct_url) if direct_url else {}
    except Exception:
        payload = {}
    return payload


def epcsaft_commit_id() -> str:
    payload = epcsaft_source_detail()
    vcs = payload.get("vcs_info", {}) if isinstance(payload, dict) else {}
    return str(vcs.get("commit_id", "unknown"))


def phase2_reaction_coefficients(activity_candidates: list[dict[str, str]]) -> dict[str, tuple[float, float, float, float]]:
    coefficients: dict[str, tuple[float, float, float, float]] = {}
    for row in activity_candidates:
        reaction_name = REACTION_NAME_BY_ID[row["reaction_id"]]
        coefficients[reaction_name] = (
            float(row["c1"]),
            float(row["c2"]),
            float(row["c3"]),
            float(row["c4"]),
        )
    missing = [REACTION_NAME_BY_ID[item] for item in ("R1", "R2", "R3", "R4", "R5") if REACTION_NAME_BY_ID[item] not in coefficients]
    if missing:
        raise RuntimeError(f"Missing Phase 2 reaction coefficient rows: {missing}")
    return coefficients


def phase2_source_by_reaction(activity_candidates: list[dict[str, str]]) -> dict[str, str]:
    return {
        REACTION_NAME_BY_ID[row["reaction_id"]]: f"{row['candidate_source']}|{row['source_files']}"
        for row in activity_candidates
    }


def phase2_reactions(T: float, activity_candidates: list[dict[str, str]]):
    return reaction_definitions_from_coefficients(
        T,
        phase2_reaction_coefficients(activity_candidates),
        source_by_name=phase2_source_by_reaction(activity_candidates),
        standard_state="mole_fraction_activity",
    )


def phase2_speciation_kwargs() -> dict[str, float | int]:
    return {
        "max_iterations": 200,
        "tolerance": PHASE2_SOLVER_TOLERANCE,
        "reaction_tolerance": PHASE2_REACTION_TOLERANCE,
    }


def positive_initial_x(values: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(values, dtype=float), PHASE2_SPECIES_INITIAL_MIN, None)
    return x / float(np.sum(x))


def phase2_initial_x(loading: float, temperature_K: float, previous_x: np.ndarray | None = None) -> np.ndarray:
    if previous_x is not None:
        return positive_initial_x(previous_x)
    return positive_initial_x(solve_ideal_speciation(float(loading), 0.3, float(temperature_K)).mole_fractions)


def curve_loadings_for_temperature(temperature_C: float) -> np.ndarray:
    lower = CURVE_MIN_LOADING_BY_TEMPERATURE_C.get(float(temperature_C), 0.005)
    upper = CURVE_MAX_LOADING_BY_TEMPERATURE_C.get(float(temperature_C), 0.8)
    return np.linspace(lower, upper, len(CURVE_LOADINGS))


def readiness_rows(reactions: list[dict[str, str]], source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    source_verified_count = sum(1 for row in source_rows if row["source_status"] == "source_verified")
    return [
        {
            "requirement": "true_species_basis",
            "status": "basis_verified",
            "evidence": "docs/roadmaps/phase2_activity_speciation_design.md",
            "notes": "Nine liquid species and three volatile vapor species are documented.",
        },
        {
            "requirement": "one_parameter_artifact",
            "status": "data_inventory_ready",
            "evidence": "data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2",
            "notes": "The Phase 2 parameter artifact is separated from earlier ionic-fit outputs.",
        },
        {
            "requirement": "activity_reaction_constants",
            "status": "source_verified_solver_ready",
            "evidence": "data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv",
            "notes": f"{source_verified_count} of {len(reactions)} constants have repo-local source values; solver use is gated by generated residual diagnostics.",
        },
        {
            "requirement": "activity_constant_candidates",
            "status": "fixed_input_candidate_used",
            "evidence": "data/reference/MEA/manifests/phase2_activity_constant_candidates.csv",
            "notes": "R1-R5 source values are carried as fixed activity-basis candidate inputs in the Phase 2 native solver run.",
        },
        {
            "requirement": "vle_fugacity_route",
            "status": "native_epcsaft_solver_available",
            "evidence": "docs/roadmaps/epcsaft_dependency_matrix.md",
            "notes": f"Using pinned ePC-SAFT commit {epcsaft_commit_id()} with generic reactive speciation and electrolyte bubble support.",
        },
        {
            "requirement": "phase3_claim_boundary",
            "status": "phase3_out_of_scope",
            "evidence": "docs/roadmaps/phase2_activity_speciation_design.md",
            "notes": "Phase 2 is an activity-based evaluation, not a finalized joint-regression result.",
        },
    ]


def speciation_reference_points() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in load_speciation_targets(None):
        species_values = {species: float(value) for species, value in zip(SPECIES, target.x)}
        species_values["MEA + MEAH+"] = species_values["MEA"] + species_values["MEAH+"]
        for species in SPECIATION_PLOT_SPECIES:
            target_role = target.target_roles.get(species, "balance_inferred")
            if target_role not in LOG_RESIDUAL_TARGET_ROLES:
                continue
            rows.append(
                {
                    "source": target.source,
                    "temperature_C": float(target.T - 273.15),
                    "MEA_weight_fraction": 0.3,
                    "CO2_loading": float(target.loading),
                    "species": species,
                    "mole_fraction": float(max(species_values[species], 1.0e-30)),
                    "point_role": "reference_point",
                    "target_role": target_role,
                }
            )
    return rows


def speciation_target_role_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in load_speciation_targets(None):
        species_values = {species: float(value) for species, value in zip(SPECIES, target.x)}
        species_values["MEA + MEAH+"] = species_values["MEA"] + species_values["MEAH+"]
        for species in SPECIATION_PLOT_SPECIES:
            target_role = target.target_roles.get(species, "balance_inferred")
            if target_role in LOG_RESIDUAL_TARGET_ROLES:
                validation_use = "log_residual_target"
            elif target_role in ZERO_TARGET_ROLES:
                validation_use = "absolute_upper_bound"
            else:
                validation_use = "context_only"
            rows.append(
                {
                    "row_id": target.row_id,
                    "source": target.source,
                    "temperature_C": float(target.T - 273.15),
                    "MEA_weight_fraction": 0.3,
                    "CO2_loading": float(target.loading),
                    "species": species,
                    "target_role": target_role,
                    "validation_use": validation_use,
                    "reconciled_mole_fraction": float(max(species_values[species], 1.0e-30)),
                }
            )
    return rows


def _species_values(values: np.ndarray) -> dict[str, float]:
    by_species = {species: float(max(values[idx], 1.0e-30)) for species, idx in SPECIES_INDEX.items()}
    by_species["MEA + MEAH+"] = by_species["MEA"] + by_species["MEAH+"]
    return by_species


def speciation_equilibrium_rows(activity_candidates: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in load_speciation_targets(None):
        row: dict[str, object] = {
            "row_id": target.row_id,
            "source": target.source,
            "temperature_C": float(target.T - 273.15),
            "MEA_weight_fraction": 0.3,
            "CO2_loading": float(target.loading),
            "pressure_Pa": float(target.P),
            "model_family": "phase2_epcsaft_activity_speciation",
        }
        target_values = _species_values(target.x)
        for species in SPECIATION_PLOT_SPECIES:
            row[f"target_x_{species}"] = target_values[species]
            row[f"target_role_{species}"] = target.target_roles.get(species, "balance_inferred")
        try:
            result = solve_activity_speciation(
                target.loading,
                target.T,
                target.P,
                target.x,
                {},
                PARAMETER_DATASET,
                reactions=phase2_reactions(target.T, activity_candidates),
                **phase2_speciation_kwargs(),
            )
            model_values = _species_values(result.x)
            for species in SPECIATION_PLOT_SPECIES:
                row[f"model_x_{species}"] = model_values[species]
                if row[f"target_role_{species}"] in LOG_RESIDUAL_TARGET_ROLES:
                    row[f"log10_model_over_target_{species}"] = math.log10(
                        max(model_values[species], 1.0e-30) / max(target_values[species], 1.0e-30)
                    )
                else:
                    row[f"log10_model_over_target_{species}"] = ""
            for name, value in result.reaction_residuals.items():
                row[f"reaction_residual_{name}"] = float(value)
            for name, value in result.mass_balance_residuals.items():
                row[f"mass_balance_residual_{name}"] = float(value)
            row["charge_residual"] = float(result.charge_residual)
            row["max_abs_reaction_residual"] = max(abs(float(value)) for value in result.reaction_residuals.values())
            row["state_failure_count"] = int(result.state_failure_count)
            row["solver_success"] = bool(result.success)
            row["message"] = result.message
        except Exception as exc:
            for species in SPECIATION_PLOT_SPECIES:
                row[f"model_x_{species}"] = ""
                row[f"log10_model_over_target_{species}"] = ""
            row["charge_residual"] = ""
            row["max_abs_reaction_residual"] = ""
            row["state_failure_count"] = ""
            row["solver_success"] = False
            row["message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        rows.append(row)
    return rows


def speciation_activity_curve_rows(activity_candidates: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    reference_targets = load_speciation_targets(None)
    temperatures_C = sorted({round(float(target.T - 273.15), 8) for target in reference_targets})
    curve_rows: list[dict[str, object]] = []
    diagnostic_rows: list[dict[str, object]] = []
    for temperature_C in temperatures_C:
        temperature_K = float(temperature_C + 273.15)
        previous_x: np.ndarray | None = None
        for loading in curve_loadings_for_temperature(float(temperature_C)):
            effective_loading = max(float(loading), 1.0e-6)
            initial_x = phase2_initial_x(effective_loading, temperature_K, previous_x)
            diagnostic: dict[str, object] = {
                "temperature_C": float(temperature_C),
                "CO2_loading": float(loading),
                "effective_CO2_loading": float(effective_loading),
                "solver_success": False,
                "message": "",
            }
            try:
                result = solve_activity_speciation(
                    effective_loading,
                    temperature_K,
                    101325.0,
                    initial_x,
                    {},
                    PARAMETER_DATASET,
                    reactions=phase2_reactions(temperature_K, activity_candidates),
                    **phase2_speciation_kwargs(),
                )
                diagnostic["solver_success"] = bool(result.success)
                diagnostic["message"] = result.message
                diagnostic["charge_residual"] = float(result.charge_residual)
                diagnostic["max_abs_reaction_residual"] = max(abs(float(value)) for value in result.reaction_residuals.values())
                diagnostic["state_failure_count"] = int(result.state_failure_count)
                if result.success:
                    previous_x = result.x
                    values = _species_values(result.x)
                    for species in SPECIATION_PLOT_SPECIES:
                        curve_rows.append(
                            {
                                "temperature_C": float(temperature_C),
                                "CO2_loading": float(loading),
                                "effective_CO2_loading": float(effective_loading),
                                "species": species,
                                "mole_fraction": values[species],
                                "curve_role": "epcsaft_activity_equilibrium_curve",
                                "solver_success": True,
                            }
                        )
            except Exception as exc:
                previous_x = None
                diagnostic["message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
            diagnostic_rows.append(diagnostic)
    return curve_rows, diagnostic_rows


def pressure_equilibrium_rows(activity_candidates: list[dict[str, str]]) -> list[dict[str, object]]:
    targets = load_vle_targets(None)
    reactions_by_temperature = {
        float(round(target.T, 8)): phase2_reactions(target.T, activity_candidates)
        for target in targets
    }
    results = solve_reactive_bubble_targets(targets, {}, PARAMETER_DATASET, reactions_by_temperature=reactions_by_temperature)
    rows: list[dict[str, object]] = []
    for target, result in zip(targets, results):
        row: dict[str, object] = {
            "row_id": target.row_id,
            "source": target.paper,
            "temperature_C": float(target.T - 273.15),
            "MEA_weight_fraction": 0.3,
            "CO2_loading": float(target.loading),
            "observed_CO2_pressure_kPa": float(target.pressure_kPa),
        }
        try:
            if isinstance(result, Exception):
                raise result
            co2_pressure_kPa = float(result.partial_pressures.get("CO2", np.nan)) / 1000.0
            if not np.isfinite(co2_pressure_kPa) or co2_pressure_kPa <= 0.0:
                raise RuntimeError(result.message)
            row["model_CO2_pressure_kPa"] = co2_pressure_kPa
            row["model_total_pressure_kPa"] = float(result.P_total) / 1000.0
            row["log10_model_over_data"] = math.log10(co2_pressure_kPa / max(float(target.pressure_kPa), 1.0e-30))
            row["fugacity_residual_norm"] = float(result.fugacity_residual_norm)
            row["charge_residual"] = float(result.charge_residual)
            row["max_abs_reaction_residual"] = max(abs(float(value)) for value in result.named_reaction_residuals.values())
            row["state_failure_count"] = int(result.state_failure_count)
            row["solver_success"] = bool(result.success)
            row["message"] = result.message
        except Exception as exc:
            row["model_CO2_pressure_kPa"] = ""
            row["model_total_pressure_kPa"] = ""
            row["log10_model_over_data"] = ""
            row["fugacity_residual_norm"] = ""
            row["charge_residual"] = ""
            row["max_abs_reaction_residual"] = ""
            row["state_failure_count"] = ""
            row["solver_success"] = False
            row["message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        rows.append(row)
    return rows


def speciation_metrics_rows(speciation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for species in SPECIATION_PLOT_SPECIES:
        values = []
        zero_model_values = []
        success_count = 0
        for row in speciation_rows:
            target_role = str(row.get(f"target_role_{species}", "balance_inferred"))
            raw = row.get(f"log10_model_over_target_{species}", "")
            if str(row.get("solver_success", "")).lower() == "true":
                success_count += 1
                if target_role in ZERO_TARGET_ROLES:
                    try:
                        model_value = float(row.get(f"model_x_{species}", ""))
                    except (TypeError, ValueError):
                        model_value = math.nan
                    if math.isfinite(model_value):
                        zero_model_values.append(model_value)
            try:
                value = float(raw)
            except (TypeError, ValueError):
                continue
            if math.isfinite(value):
                values.append(value)
        abs_values = [abs(value) for value in values]
        rows.append(
            {
                "target_family": "speciation",
                "species_or_property": species,
                "target_role": "direct_positive",
                "metric": "median_abs_log10_error",
                "row_count": len(values),
                "solver_success_count": success_count,
                "median_abs_log10_error": float(np.median(abs_values)) if abs_values else "",
                "max_abs_log10_error": float(np.max(abs_values)) if abs_values else "",
                "rmse_log10_error": float(np.sqrt(np.mean(np.square(values)))) if values else "",
            }
        )
        if zero_model_values:
            rows.append(
                {
                    "target_family": "speciation",
                    "species_or_property": species,
                    "target_role": "direct_zero",
                    "metric": "max_model_mole_fraction_for_reported_zero",
                    "row_count": len(zero_model_values),
                    "solver_success_count": success_count,
                    "median_abs_log10_error": "",
                    "max_abs_log10_error": "",
                    "rmse_log10_error": "",
                    "max_model_mole_fraction": float(np.max(zero_model_values)),
                }
            )
    return rows


def pressure_metrics_rows(pressure_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    groups: dict[str, list[dict[str, object]]] = {"overall": pressure_rows}
    for row in pressure_rows:
        groups.setdefault(f"{float(row['temperature_C']):g} C", []).append(row)
    for label, group_rows in groups.items():
        residuals = []
        success_count = 0
        for row in group_rows:
            if str(row.get("solver_success", "")).lower() == "true":
                success_count += 1
            try:
                value = float(row.get("log10_model_over_data", ""))
            except (TypeError, ValueError):
                continue
            if math.isfinite(value):
                residuals.append(value)
        abs_values = [abs(value) for value in residuals]
        rows.append(
            {
                "target_family": "pressure",
                "temperature_C": label,
                "row_count": len(group_rows),
                "solver_success_count": success_count,
                "median_abs_log10_error": float(np.median(abs_values)) if abs_values else "",
                "max_abs_log10_error": float(np.max(abs_values)) if abs_values else "",
                "rmse_log10_error": float(np.sqrt(np.mean(np.square(residuals)))) if residuals else "",
            }
        )
    return rows


def _finite_float_values(rows: list[dict[str, object]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        try:
            value = float(row.get(key, ""))
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            values.append(value)
    return values


def _residual_summary_values(values: list[float]) -> dict[str, object]:
    abs_values = [abs(value) for value in values]
    return {
        "median_abs_log10": float(np.median(abs_values)) if abs_values else "",
        "rmse_log10": float(np.sqrt(np.mean(np.square(values)))) if values else "",
        "max_abs_log10": float(np.max(abs_values)) if abs_values else "",
    }


def source_residual_summary_rows(
    pressure_rows: list[dict[str, object]],
    speciation_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Summarize Phase 2 residuals by source without mixing observable families or target roles."""
    rows: list[dict[str, object]] = []

    pressure_by_source: dict[str, list[dict[str, object]]] = {}
    for row in pressure_rows:
        pressure_by_source.setdefault(str(row["source"]), []).append(row)
    missing_pressure = [source for source in PHASE2_PRESSURE_SOURCES if source not in pressure_by_source]
    if missing_pressure:
        raise RuntimeError(f"Missing Phase 2 pressure source rows: {missing_pressure}")

    for source in PHASE2_PRESSURE_SOURCES:
        group_rows = pressure_by_source[source]
        residuals = _finite_float_values(group_rows, "log10_model_over_data")
        rows.append(
            {
                "phase": "phase2",
                "model_family": "phase2_epcsaft_reactive_bubble",
                "observable_family": "pressure",
                "source": source,
                "species_or_property": "CO2_pressure",
                "target_role": "measured_pressure",
                "state_count": len({str(row["row_id"]) for row in group_rows}),
                "target_count": len(group_rows),
                "solver_success_count": sum(1 for row in group_rows if str(row.get("solver_success", "")).lower() == "true"),
                **_residual_summary_values(residuals),
                "max_model_mole_fraction_for_reported_zero": "",
                "metric": "log10_model_over_data",
            }
        )

    speciation_by_source: dict[str, list[dict[str, object]]] = {}
    for row in speciation_rows:
        speciation_by_source.setdefault(str(row["source"]), []).append(row)
    missing_speciation = [source for source in PHASE2_SPECIATION_SOURCES if source not in speciation_by_source]
    if missing_speciation:
        raise RuntimeError(f"Missing Phase 2 speciation source rows: {missing_speciation}")

    role_order = [
        "direct_positive",
        "aggregate_direct_positive",
        "direct_zero",
        "aggregate_direct_zero",
        "balance_inferred",
    ]
    for source in PHASE2_SPECIATION_SOURCES:
        source_rows = speciation_by_source[source]
        rows.append(
            {
                "phase": "phase2",
                "model_family": "phase2_epcsaft_activity_speciation",
                "observable_family": "speciation",
                "source": source,
                "species_or_property": "all_speciation_states",
                "target_role": "state_record",
                "state_count": len({str(row["row_id"]) for row in source_rows}),
                "target_count": len({str(row["row_id"]) for row in source_rows}),
                "solver_success_count": sum(1 for row in source_rows if str(row.get("solver_success", "")).lower() == "true"),
                "median_abs_log10": "",
                "rmse_log10": "",
                "max_abs_log10": "",
                "max_model_mole_fraction_for_reported_zero": "",
                "metric": "state_accounting",
            }
        )
        for species in SPECIATION_PLOT_SPECIES:
            species_roles = {
                str(row.get(f"target_role_{species}", "balance_inferred"))
                for row in source_rows
            }
            for target_role in role_order:
                if target_role not in species_roles:
                    continue
                group_rows = [
                    row
                    for row in source_rows
                    if str(row.get(f"target_role_{species}", "balance_inferred")) == target_role
                ]
                residuals: list[float] = []
                zero_model_values: list[float] = []
                metric = "context_count_only"
                if target_role in LOG_RESIDUAL_TARGET_ROLES:
                    residuals = _finite_float_values(group_rows, f"log10_model_over_target_{species}")
                    metric = "log10_model_over_target"
                elif target_role in ZERO_TARGET_ROLES:
                    zero_model_values = _finite_float_values(group_rows, f"model_x_{species}")
                    metric = "max_model_mole_fraction_for_reported_zero"
                residual_summary = _residual_summary_values(residuals)
                rows.append(
                    {
                        "phase": "phase2",
                        "model_family": "phase2_epcsaft_activity_speciation",
                        "observable_family": "speciation",
                        "source": source,
                        "species_or_property": species,
                        "target_role": target_role,
                        "state_count": len({str(row["row_id"]) for row in group_rows}),
                        "target_count": len(group_rows),
                        "solver_success_count": sum(
                            1 for row in group_rows if str(row.get("solver_success", "")).lower() == "true"
                        ),
                        **residual_summary,
                        "max_model_mole_fraction_for_reported_zero": (
                            float(np.max(zero_model_values)) if zero_model_values else ""
                        ),
                        "metric": metric,
                    }
                )
    return rows


def residual_acceptance_rows(
    speciation_metrics: list[dict[str, object]],
    pressure_metrics: list[dict[str, object]],
    curve_diagnostics: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    curve_success_fraction = (
        sum(1 for row in curve_diagnostics if str(row.get("solver_success", "")).lower() == "true") / max(len(curve_diagnostics), 1)
    )
    rows.append(
        {
            "target_family": "solver",
            "source_or_model": "phase2_epcsaft_activity_curve",
            "temperature_C": "all",
            "species_or_property": "curve_grid_success_fraction",
            "metric": "success_fraction",
            "threshold": SOLVER_SUCCESS_FRACTION_THRESHOLD,
            "actual_value": curve_success_fraction,
            "passes": str(curve_success_fraction >= SOLVER_SUCCESS_FRACTION_THRESHOLD).lower(),
            "claim_allowed": str(curve_success_fraction >= SOLVER_SUCCESS_FRACTION_THRESHOLD).lower(),
            "failure_reason": "" if curve_success_fraction >= SOLVER_SUCCESS_FRACTION_THRESHOLD else "not_all_curve_grid_points_converged",
            "recommended_manuscript_use": "model_evidence" if curve_success_fraction >= SOLVER_SUCCESS_FRACTION_THRESHOLD else "diagnostic_only",
        }
    )
    direct_metric_by_species = {
        str(metric["species_or_property"]): metric
        for metric in speciation_metrics
        if metric.get("metric") == "median_abs_log10_error" and metric.get("target_role") == "direct_positive"
    }
    zero_metric_by_species = {
        str(metric["species_or_property"]): metric
        for metric in speciation_metrics
        if metric.get("metric") == "max_model_mole_fraction_for_reported_zero" and metric.get("target_role") == "direct_zero"
    }
    for species in MAJOR_SPECIATION_SPECIES:
        metric = direct_metric_by_species[species]
        actual = float(metric["median_abs_log10_error"])
        passes = actual <= SPECIATION_MEDIAN_ABS_LOG10_THRESHOLD
        rows.append(
            {
                "target_family": "speciation",
                "source_or_model": "phase2_epcsaft_activity_speciation",
                "temperature_C": "overall",
                "species_or_property": species,
                "metric": "direct_positive_median_abs_log10_error",
                "threshold": SPECIATION_MEDIAN_ABS_LOG10_THRESHOLD,
                "actual_value": actual,
                "passes": str(passes).lower(),
                "claim_allowed": str(passes).lower(),
                "failure_reason": "" if passes else "major_species_residual_exceeds_phase2_threshold",
                "recommended_manuscript_use": "model_evidence" if passes else "diagnostic_only",
            }
        )
        if species in zero_metric_by_species:
            zero_metric = zero_metric_by_species[species]
            zero_actual = float(zero_metric["max_model_mole_fraction"])
            zero_passes = zero_actual <= SPECIATION_REPORTED_ZERO_ABS_THRESHOLD
            rows.append(
                {
                    "target_family": "speciation",
                    "source_or_model": "phase2_epcsaft_activity_speciation",
                    "temperature_C": "overall",
                    "species_or_property": species,
                    "metric": "reported_zero_max_model_mole_fraction",
                    "threshold": SPECIATION_REPORTED_ZERO_ABS_THRESHOLD,
                    "actual_value": zero_actual,
                    "passes": str(zero_passes).lower(),
                    "claim_allowed": str(zero_passes).lower(),
                    "failure_reason": "" if zero_passes else "reported_zero_rows_exceed_absolute_speciation_threshold",
                    "recommended_manuscript_use": "model_evidence" if zero_passes else "diagnostic_only",
                }
            )
    pressure_overall = next(row for row in pressure_metrics if row["temperature_C"] == "overall")
    actual_pressure = float(pressure_overall["median_abs_log10_error"])
    pressure_passes = actual_pressure <= PRESSURE_MEDIAN_ABS_LOG10_THRESHOLD
    rows.append(
        {
            "target_family": "pressure",
            "source_or_model": "phase2_epcsaft_reactive_bubble",
            "temperature_C": "overall",
            "species_or_property": "CO2_pressure",
            "metric": "median_abs_log10_error",
            "threshold": PRESSURE_MEDIAN_ABS_LOG10_THRESHOLD,
            "actual_value": actual_pressure,
            "passes": str(pressure_passes).lower(),
            "claim_allowed": str(pressure_passes).lower(),
            "failure_reason": "" if pressure_passes else "pressure_residual_exceeds_phase2_threshold",
            "recommended_manuscript_use": "model_evidence" if pressure_passes else "diagnostic_only",
        }
    )
    return rows


def _solver_success_rows(rows: list[dict[str, object]]) -> bool:
    return bool(rows) and all(str(row.get("solver_success", "")).lower() == "true" for row in rows)


def phase2_status_from_solver(
    speciation_equilibrium: list[dict[str, object]],
    pressure_equilibrium: list[dict[str, object]],
    speciation_curves: list[dict[str, object]],
) -> str:
    if _solver_success_rows(speciation_equilibrium) and _solver_success_rows(pressure_equilibrium) and _solver_success_rows(speciation_curves):
        return "model_ran_success"
    return "model_ran_solver_failures"


def required_output_status_rows(reactions: list[dict[str, str]], phase2_status: str) -> list[dict[str, str]]:
    pH_files = [path for path in (MEA_REFERENCE / "pH").glob("*.csv")]
    dielectric_files = [path for path in (MEA_REFERENCE / "dielectric").glob("*.csv") if not path.name.endswith("_schema.csv")]
    ionic_activity_files = [path for path in (MEA_REFERENCE / "ionic_activity").glob("*.csv")]
    density_files = [path for path in (MEA_REFERENCE / "density_viscosity").glob("*.csv") if not path.name.endswith("_schema.csv")]
    rows = [
        {
            "artifact": "phase2_activity_speciation_problem.json",
            "status": "problem_definition_generated",
            "blocking_requirement": "none",
            "next_action": "Use as the source problem definition for the next implementation slice.",
        },
        {
            "artifact": "phase2_equilibrium_results.csv",
            "status": phase2_status,
            "blocking_requirement": "residual_acceptance_audit",
            "next_action": "Treat as actual native ePC-SAFT output, but cite only gates that pass in phase2_residual_acceptance_audit.csv.",
        },
        {
            "artifact": "phase2_pressure_speciation_parity.csv",
            "status": phase2_status,
            "blocking_requirement": "residual_acceptance_audit",
            "next_action": "Use only for residual-gated comparison with Phase 1 and literature targets.",
        },
        {
            "artifact": "phase2_pressure_metrics.csv",
            "status": phase2_status,
            "blocking_requirement": "pressure residual threshold",
            "next_action": "Pressure claims remain disallowed unless the pressure audit row passes.",
        },
        {
            "artifact": "phase2_speciation_metrics.csv",
            "status": phase2_status,
            "blocking_requirement": "speciation residual thresholds",
            "next_action": "Major-species speciation claims are limited to passing audit rows.",
        },
        {
            "artifact": "phase2_source_residual_summary.csv",
            "status": phase2_status,
            "blocking_requirement": "source residual accounting",
            "next_action": "Use this table for source-resolved pressure and speciation residual accounting without mixing target roles.",
        },
        {
            "artifact": "phase2_solver_diagnostics.csv",
            "status": "generated",
            "blocking_requirement": "none",
            "next_action": "Use this file as the hard gate against best-effort or failed solver rows being presented as model evidence.",
        },
        {
            "artifact": "phase2_residual_acceptance_audit.csv",
            "status": phase2_status,
            "blocking_requirement": "none",
            "next_action": "This file controls validation and claim permission; validation outcomes do not revise model-run status.",
        },
        {
            "artifact": "phase2_speciation_activity_curves.csv",
            "status": "generated_from_native_epcsaft_activity_solver",
            "blocking_requirement": "none",
            "next_action": "Render smooth Phase 2 curves only from these solver-success rows.",
        },
        {
            "artifact": "phase2_speciation_target_roles.csv",
            "status": "generated",
            "blocking_requirement": "none",
            "next_action": "Use this file to distinguish direct positive targets, reported-zero upper bounds, and balance-inferred context rows.",
        },
        {
            "artifact": "phase2_speciation_activity_plot.png",
            "status": "render_input_ready",
            "blocking_requirement": "phase2_speciation_activity_curves.csv",
            "next_action": "Render from phase2_speciation_activity_curves.csv; do not use failed diagnostics as curve rows.",
        },
        {
            "artifact": "phase2_pH_validation.csv",
            "status": "optional_validation_inventory_ready" if pH_files else "optional_validation_source_absent",
            "blocking_requirement": "none",
            "next_action": "Do not use pH as a Phase 2 gate unless scale, method, and activity-state mapping are recorded.",
        },
        {
            "artifact": "phase2_density_viscosity_validation.csv",
            "status": "optional_validation_inventory_ready" if density_files else "optional_validation_source_absent",
            "blocking_requirement": "none",
            "next_action": "Use Amundsen density/viscosity only as optional external validation or Phase 3 regularization evidence.",
        },
        {
            "artifact": "phase2_comparison_to_phase1.md",
            "status": "problem_definition_generated",
            "blocking_requirement": "none",
            "next_action": "Update after convention-safe Phase 2 equilibrium outputs exist.",
        },
        {
            "artifact": "phase2_dielectric_policy",
            "status": "fixed_policy_no_phase2_fit" if not dielectric_files else "optional_validation_inventory_ready",
            "blocking_requirement": "none",
            "next_action": "Keep MEA f_solv fixed in Phase 2; move only in a later fit with direct MEA-H2O dielectric evidence.",
        },
        {
            "artifact": "phase2_ionic_activity_policy",
            "status": "fixed_policy_no_phase2_fit" if not ionic_activity_files else "optional_validation_inventory_ready",
            "blocking_requirement": "none",
            "next_action": "Do not treat analog electrolyte data as direct MEA ion evidence for Phase 2.",
        },
    ]
    return rows


def problem_definition(
    reactions: list[dict[str, str]], activity_candidates: list[dict[str, str]], species: list[str]
) -> dict[str, Any]:
    candidate_status_counts = {
        status: sum(1 for row in activity_candidates if row["phase2_status"] == status)
        for status in sorted({row["phase2_status"] for row in activity_candidates})
    }
    return {
        "analysis": "phase2_activity_epcsaft",
        "status": "problem_definition_generated",
        "species": species,
        "charges": CHARGES,
        "volatile_species": list(VOLATILE_SPECIES),
        "nonvolatile_species": list(NONVOLATILE_SPECIES),
        "material_balances": MATERIAL_BALANCES,
        "constraints": CONSTRAINTS,
        "activity_convention": {
            "needed_basis": "mole_fraction_activity",
            "current_manifest_conversion_status": sorted({row["conversion_status"] for row in reactions}),
            "candidate_manifest": str(ACTIVITY_CANDIDATES.relative_to(REPO_ROOT)).replace("\\", "/"),
            "candidate_status_counts": candidate_status_counts,
            "solve_policy": "run_only_with_pinned_epcsaft_native_activity_solver_and_generated_residual_gates",
            "standard_state_used": "mole_fraction_activity",
        },
        "epcsaft_dependency": {
            "commit_id": epcsaft_commit_id(),
            "direct_url": epcsaft_source_detail(),
        },
        "parameter_artifact": str(PARAMETER_DATASET.relative_to(REPO_ROOT)).replace("\\", "/"),
        "dielectric_option": "sensitivity_only_unless_direct_MEA_H2O_dielectric_evidence_supports_fit",
        "born_option": "advanced_Born_SSM_DS_with_promoted_regularized_carbonate_pair",
        "solver_route": [
            "Build true-species problem definition from this JSON and the reaction manifest.",
            "Use the pinned epcsaft native reactive speciation route for liquid activity-equilibrium rows.",
            "Use the pinned epcsaft reactive electrolyte bubble route for volatile-species pressure rows.",
            "Record solver failures and residual gates explicitly instead of treating generated rows as completion.",
        ],
        "validation_policy": {
            "direct_positive_species_metric": "median_abs_log10_error",
            "direct_positive_threshold": SPECIATION_MEDIAN_ABS_LOG10_THRESHOLD,
            "reported_zero_species_metric": "max_model_mole_fraction",
            "reported_zero_threshold": SPECIATION_REPORTED_ZERO_ABS_THRESHOLD,
            "balance_inferred_rows": "context_only_not_log_residual_targets",
        },
        "reactions": reactions,
    }


def write_comparison(path: Path, phase2_status: str, audit_rows: list[dict[str, object]]) -> None:
    failed = [row for row in audit_rows if str(row["passes"]).lower() != "true"]
    validation_status = "validated" if not failed else "residual_limited"
    failed_lines = "\n".join(
        f"- {row['target_family']}: {row['species_or_property']} {row['metric']}={row['actual_value']} threshold={row['threshold']}"
        for row in failed
    ) or "- none"
    text = f"""# Phase 2 Comparison To Phase 1

Phase 1 now solves the explicit five-reaction, nine-species ideal Smith-Missen speciation system with documented reaction constants and activities set equal to mole fractions. It remains distinct from Phase 2 because Phase 2 requires ePC-SAFT activity coefficients and package-native residual/source-validation gates.

Phase 2 now uses pinned ePC-SAFT commit `{epcsaft_commit_id()}` and the native activity-coupled reactive speciation / reactive electrolyte bubble route. The generated rows are real solver outputs, not scaffold or diagnostic curves.

phase2_status: {phase2_status}
phase2_validation_status: {validation_status}

Phase 2 activity-evaluation claims are controlled by `phase2_residual_acceptance_audit.csv`. Failed gates:

{failed_lines}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_claim_boundary_report(
    path: Path, source_rows: list[dict[str, str]], phase2_status: str, audit_rows: list[dict[str, object]]
) -> None:
    source_count = sum(1 for row in source_rows if row["source_status"] == "source_verified")
    failed = [row for row in audit_rows if str(row["passes"]).lower() != "true"]
    validation_status = "validated" if not failed else "residual_limited"
    failed_lines = "\n".join(
        f"- {row['target_family']}: {row['species_or_property']} {row['metric']}={row['actual_value']} threshold={row['threshold']}"
        for row in failed
    ) or "- none"
    text = f"""# Phase 2 Solver And Claim Boundary Report

phase2_status: {phase2_status}
phase2_validation_status: {validation_status}
source_status: source_verified
solver_status: native_epcsaft_activity_solver_ran

Phase 2 activity-evaluation claims are controlled by `phase2_residual_acceptance_audit.csv`.
This does not claim a Phase 3 package-native joint regression.

This run uses pinned ePC-SAFT commit `{epcsaft_commit_id()}` and generates actual activity-coupled equilibrium rows from the Phase 2 parameter artifact.

Evidence now present:
- {source_count} of {len(source_rows)} R1-R5 source-value rows are verified against repo-local source text in `phase2_reaction_constant_source_verification.csv`.
- The generated problem definition separates material balances from electroneutrality constraints.
- `phase2_equilibrium_results.csv`, `phase2_pressure_speciation_parity.csv`, metrics, `phase2_solver_diagnostics.csv`, and activity-curve rows are generated from the native ePC-SAFT solver.
- `phase2_source_residual_summary.csv` records source-resolved pressure and speciation residual accounting without mixing nonzero, zero-reported, and balance-inferred target roles.
- `phase2_speciation_activity_curves.csv` contains only solver-success curve rows.
- `phase2_speciation_target_roles.csv` prevents reported-zero and balance-inferred rows from being treated as direct log-residual targets.

Failed gates:
{failed_lines}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    remove_stale_scaffold_outputs()

    reactions = reaction_rows()
    activity_candidates = activity_candidate_rows()
    source_rows = source_verification_rows()
    species = dataset_species()
    artifact_manifest = read_csv(PARAMETER_MANIFEST)
    readiness = readiness_rows(reactions, source_rows)
    problem = problem_definition(reactions, activity_candidates, species)
    reference_points = speciation_reference_points()
    target_roles = speciation_target_role_rows()
    speciation_equilibrium = speciation_equilibrium_rows(activity_candidates)
    speciation_curves, solver_diagnostics = speciation_activity_curve_rows(activity_candidates)
    pressure_equilibrium = pressure_equilibrium_rows(activity_candidates)
    pressure_speciation_parity = [
        {**row, "parity_family": "speciation"} for row in speciation_equilibrium
    ] + [
        {**row, "parity_family": "pressure"} for row in pressure_equilibrium
    ]
    speciation_metrics = speciation_metrics_rows(speciation_equilibrium)
    pressure_metrics = pressure_metrics_rows(pressure_equilibrium)
    source_residual_summary = source_residual_summary_rows(pressure_equilibrium, speciation_equilibrium)
    residual_audit = residual_acceptance_rows(speciation_metrics, pressure_metrics, solver_diagnostics)
    phase2_status = phase2_status_from_solver(speciation_equilibrium, pressure_equilibrium, speciation_curves)
    output_status = required_output_status_rows(reactions, phase2_status)

    write_json(PROCESSED_DIR / "phase2_activity_speciation_problem.json", problem)
    write_json(RESULTS_DIR / "phase2_activity_speciation_problem.json", problem)
    write_csv(PROCESSED_DIR / "phase2_reaction_constant_basis.csv", reactions, list(reactions[0].keys()))
    write_csv(RESULTS_DIR / "phase2_reaction_constant_basis.csv", reactions, list(reactions[0].keys()))
    write_csv(
        PROCESSED_DIR / "phase2_reaction_constant_source_verification.csv",
        source_rows,
        list(source_rows[0].keys()),
    )
    write_csv(
        RESULTS_DIR / "phase2_reaction_constant_source_verification.csv",
        source_rows,
        list(source_rows[0].keys()),
    )
    write_csv(
        PROCESSED_DIR / "phase2_activity_constant_candidates.csv",
        activity_candidates,
        list(activity_candidates[0].keys()),
    )
    write_csv(
        RESULTS_DIR / "phase2_activity_constant_candidates.csv",
        activity_candidates,
        list(activity_candidates[0].keys()),
    )
    write_csv(PROCESSED_DIR / "phase2_parameter_artifact_manifest.csv", artifact_manifest, list(artifact_manifest[0].keys()))
    write_csv(RESULTS_DIR / "phase2_parameter_artifact_manifest.csv", artifact_manifest, list(artifact_manifest[0].keys()))
    write_csv(PROCESSED_DIR / "phase2_readiness_status.csv", readiness, list(readiness[0].keys()))
    write_csv(RESULTS_DIR / "phase2_readiness_status.csv", readiness, list(readiness[0].keys()))
    write_csv(PROCESSED_DIR / "phase2_required_output_status.csv", output_status, list(output_status[0].keys()))
    write_csv(RESULTS_DIR / "phase2_required_output_status.csv", output_status, list(output_status[0].keys()))
    write_csv(PROCESSED_DIR / "phase2_speciation_reference_points.csv", reference_points, list(reference_points[0].keys()))
    write_csv(RESULTS_DIR / "phase2_speciation_reference_points.csv", reference_points, list(reference_points[0].keys()))
    write_csv(PROCESSED_DIR / "phase2_speciation_target_roles.csv", target_roles, list(target_roles[0].keys()))
    write_csv(RESULTS_DIR / "phase2_speciation_target_roles.csv", target_roles, list(target_roles[0].keys()))
    write_rows(PROCESSED_DIR / "phase2_equilibrium_results.csv", speciation_equilibrium)
    write_rows(RESULTS_DIR / "phase2_equilibrium_results.csv", speciation_equilibrium)
    write_rows(PROCESSED_DIR / "phase2_pressure_results.csv", pressure_equilibrium)
    write_rows(RESULTS_DIR / "phase2_pressure_results.csv", pressure_equilibrium)
    write_rows(PROCESSED_DIR / "phase2_pressure_speciation_parity.csv", pressure_speciation_parity)
    write_rows(RESULTS_DIR / "phase2_pressure_speciation_parity.csv", pressure_speciation_parity)
    write_rows(PROCESSED_DIR / "phase2_pressure_metrics.csv", pressure_metrics)
    write_rows(RESULTS_DIR / "phase2_pressure_metrics.csv", pressure_metrics)
    write_rows(PROCESSED_DIR / "phase2_speciation_metrics.csv", speciation_metrics)
    write_rows(RESULTS_DIR / "phase2_speciation_metrics.csv", speciation_metrics)
    write_csv(
        PROCESSED_DIR / "phase2_source_residual_summary.csv",
        source_residual_summary,
        SOURCE_RESIDUAL_SUMMARY_FIELDNAMES,
    )
    write_csv(
        RESULTS_DIR / "phase2_source_residual_summary.csv",
        source_residual_summary,
        SOURCE_RESIDUAL_SUMMARY_FIELDNAMES,
    )
    write_rows(PROCESSED_DIR / "phase2_solver_diagnostics.csv", solver_diagnostics)
    write_rows(RESULTS_DIR / "phase2_solver_diagnostics.csv", solver_diagnostics)
    write_rows(PROCESSED_DIR / "phase2_residual_acceptance_audit.csv", residual_audit)
    write_rows(RESULTS_DIR / "phase2_residual_acceptance_audit.csv", residual_audit)
    write_rows(PROCESSED_DIR / "phase2_speciation_activity_curves.csv", speciation_curves)
    write_rows(RESULTS_DIR / "phase2_speciation_activity_curves.csv", speciation_curves)
    write_comparison(RESULTS_DIR / "phase2_comparison_to_phase1.md", phase2_status, residual_audit)
    write_claim_boundary_report(RESULTS_DIR / "phase2_solver_claim_boundary_report.md", source_rows, phase2_status, residual_audit)

    print(f"Phase 2 native ePC-SAFT status: {phase2_status}")
    print(f"Phase 2 metadata, solver, and residual artifacts: {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
