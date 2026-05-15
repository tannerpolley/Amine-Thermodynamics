from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
RESULTS_DIR = ANALYSIS_DIR / "results"
REACTION_MANIFEST = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_reaction_constant_manifest.csv"
ACTIVITY_CANDIDATES = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_activity_constant_candidates.csv"
PARAMETER_DATASET = REPO_ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_phase2"
PARAMETER_MANIFEST = PARAMETER_DATASET / "phase2_parameter_artifact_manifest.csv"
MEA_REFERENCE = REPO_ROOT / "data" / "reference" / "MEA"

SPECIES = ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
CHARGES = {"CO2": 0, "MEA": 0, "H2O": 0, "MEAH+": 1, "MEACOO-": -1, "HCO3-": -1, "CO3^2-": -2, "H3O+": 1, "OH-": -1}
VOLATILE_SPECIES = ("CO2", "H2O", "MEA")
NONVOLATILE_SPECIES = tuple(species for species in SPECIES if species not in VOLATILE_SPECIES)
BALANCES = {
    "total_amine": {"MEA": 1.0, "MEAH+": 1.0, "MEACOO-": 1.0},
    "total_carbon": {"CO2": 1.0, "MEACOO-": 1.0, "HCO3-": 1.0, "CO3^2-": 1.0},
    "charge": {"MEAH+": 1.0, "H3O+": 1.0, "MEACOO-": -1.0, "HCO3-": -1.0, "CO3^2-": -2.0, "OH-": -1.0},
}


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


def readiness_rows(reactions: list[dict[str, str]]) -> list[dict[str, str]]:
    converted = [row for row in reactions if row["conversion_status"] in {"converted", "thermodynamic_activity"}]
    activity_ready = len(converted) == len(reactions)
    return [
        {
            "requirement": "true_species_basis",
            "status": "ready",
            "evidence": "docs/roadmaps/phase2_activity_speciation_design.md",
            "notes": "Nine liquid species and three volatile vapor species are documented.",
        },
        {
            "requirement": "one_parameter_artifact",
            "status": "ready",
            "evidence": "data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2",
            "notes": "The Phase 2 parameter artifact is separated from earlier ionic-fit outputs.",
        },
        {
            "requirement": "activity_reaction_constants",
            "status": "ready_reference_state_verified" if activity_ready else "blocked_pending_conversion",
            "evidence": "data/reference/MEA/manifests/phase2_reaction_constant_manifest.csv",
            "notes": f"{len(converted)} of {len(reactions)} constants are source-verified for thermodynamic-activity use.",
        },
        {
            "requirement": "activity_constant_candidates",
            "status": "promoted_austgen_reference_state_verified" if activity_ready else "local_r1_r5_candidates_reference_state_pending",
            "evidence": "data/reference/MEA/manifests/phase2_activity_constant_candidates.csv",
            "notes": "R1-R5 have Austgen Table V constants on the unsymmetric mole-fraction activity H3O+ basis; equilibrium rows remain blocked by upstream solver support.",
        },
        {
            "requirement": "vle_fugacity_route",
            "status": "package_route_documented",
            "evidence": "docs/roadmaps/epcsaft_dependency_matrix.md",
            "notes": "Use generic reactive speciation and electrolyte bubble/fugacity support; do not add MEA-specific package APIs.",
        },
        {
            "requirement": "phase3_claim_boundary",
            "status": "ready",
            "evidence": "docs/roadmaps/phase2_activity_speciation_design.md",
            "notes": "Phase 2 is an activity-based evaluation, not a final coupled regression.",
        },
    ]


def required_output_status_rows(reactions: list[dict[str, str]]) -> list[dict[str, str]]:
    converted = [row for row in reactions if row["conversion_status"] in {"converted", "thermodynamic_activity"}]
    activity_ready = len(converted) == len(reactions)
    activity_status = "blocked_upstream_solver_backend_unavailable" if activity_ready else "blocked_pending_reference_state_promotion"
    pH_files = [path for path in (MEA_REFERENCE / "pH").glob("*.csv")]
    dielectric_files = [path for path in (MEA_REFERENCE / "dielectric").glob("*.csv") if not path.name.endswith("_schema.csv")]
    ionic_activity_files = [path for path in (MEA_REFERENCE / "ionic_activity").glob("*.csv")]
    density_files = [path for path in (MEA_REFERENCE / "density_viscosity").glob("*.csv") if not path.name.endswith("_schema.csv")]
    rows = [
        {
            "artifact": "phase2_activity_speciation_problem.json",
            "status": "generated",
            "blocking_requirement": "none",
            "next_action": "Use as the source problem definition for the next implementation slice.",
        },
        {
            "artifact": "phase2_equilibrium_results.csv",
            "status": activity_status,
            "blocking_requirement": "upstream ePC-SAFT issue #115 native activity-coupled speciation support" if activity_ready else "all R1-R5 constants must be promoted from local candidates to thermodynamic-activity or converted constants",
            "next_action": "Rerun after upstream issue #115 exposes the required activity-coupled solver path." if activity_ready else "Verify the original Austgen/reference-state convention before solving activity-based speciation.",
        },
        {
            "artifact": "phase2_pressure_speciation_parity.csv",
            "status": "blocked_pending_phase2_equilibrium_results",
            "blocking_requirement": "phase2_equilibrium_results.csv",
            "next_action": "Generate only from convention-safe Phase 2 equilibrium rows.",
        },
        {
            "artifact": "phase2_pressure_metrics.csv",
            "status": "blocked_pending_phase2_equilibrium_results",
            "blocking_requirement": "phase2_equilibrium_results.csv",
            "next_action": "Compute only after pressure predictions exist.",
        },
        {
            "artifact": "phase2_speciation_metrics.csv",
            "status": "blocked_pending_phase2_equilibrium_results",
            "blocking_requirement": "phase2_equilibrium_results.csv",
            "next_action": "Compute only after speciation predictions exist.",
        },
        {
            "artifact": "phase2_pH_validation.csv",
            "status": "blocked_source_data_missing" if not pH_files else "blocked_pending_convention_check",
            "blocking_requirement": "convention-compatible pH data and activity-state mapping",
            "next_action": "Use pH only as validation/anchor data after scale and method are recorded.",
        },
        {
            "artifact": "phase2_density_viscosity_validation.csv",
            "status": "data_available_model_not_evaluated" if density_files else "blocked_source_data_missing",
            "blocking_requirement": "Phase 2 liquid states and validation formulas",
            "next_action": "Use Amundsen density/viscosity only as an external validation or regularization candidate.",
        },
        {
            "artifact": "phase2_comparison_to_phase1.md",
            "status": "generated",
            "blocking_requirement": "none",
            "next_action": "Update after convention-safe Phase 2 equilibrium outputs exist.",
        },
        {
            "artifact": "phase2_dielectric_policy",
            "status": "schema_only_no_observations" if not dielectric_files else "data_available_requires_policy_decision",
            "blocking_requirement": "direct MEA-H2O dielectric/permittivity observations",
            "next_action": "Keep MEA f_solv fixed or sensitivity-only until direct evidence exists.",
        },
        {
            "artifact": "phase2_ionic_activity_policy",
            "status": "blocked_source_data_missing" if not ionic_activity_files else "data_available_requires_salt_classification",
            "blocking_requirement": "direct MEAH+ or MEACOO- salt osmotic/activity data",
            "next_action": "Do not treat analog electrolyte data as direct MEA ion evidence.",
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
        "status": "problem_definition_ready_upstream_solver_backend_blocks_activity_solve",
        "species": species,
        "charges": CHARGES,
        "volatile_species": list(VOLATILE_SPECIES),
        "nonvolatile_species": list(NONVOLATILE_SPECIES),
        "balances": BALANCES,
        "activity_convention": {
            "needed_basis": "thermodynamic_activity",
            "current_manifest_conversion_status": sorted({row["conversion_status"] for row in reactions}),
            "candidate_manifest": str(ACTIVITY_CANDIDATES.relative_to(REPO_ROOT)).replace("\\", "/"),
            "candidate_status_counts": candidate_status_counts,
            "solve_policy": "do_not_run_activity_solve_until_upstream_issue_115_activity_backend_is_available",
        },
        "parameter_artifact": str(PARAMETER_DATASET.relative_to(REPO_ROOT)).replace("\\", "/"),
        "dielectric_option": "sensitivity_only_unless_direct_MEA_H2O_dielectric_evidence_supports_fit",
        "born_option": "advanced_Born_SSM_DS_with_promoted_regularized_carbonate_pair",
        "solver_route": [
            "Build true-species problem definition from this JSON and the reaction manifest.",
            "Use epcsaft.solve_reactive_speciation only after upstream activity-coupled solver support is available.",
            "Use package electrolyte bubble/fugacity support for volatile species after a liquid state is convention-safe.",
            "Record package/data blockers explicitly instead of adding downstream workarounds.",
        ],
        "reactions": reactions,
    }


def write_comparison(path: Path) -> None:
    text = """# Phase 2 Comparison To Phase 1

Phase 1 is an ideal/apparent Smith-Missen reproduction baseline. It uses the documented Phase 1 reaction constants without ePC-SAFT activity coefficients.

Phase 2 uses the nine-species liquid basis and one ePC-SAFT parameter artifact. Austgen Table V verifies R1-R5 on the unsymmetric mole-fraction activity H3O+ basis, so the reaction constants are source-ready fixed inputs. The current Phase 2 output is still a convention-safe problem definition and readiness audit, not a claimed activity-based equilibrium result, because the pinned upstream ePC-SAFT package lacks the required native activity-coupled speciation backend tracked in upstream issue #115.

Next required implementation: generate pressure/speciation tables only after upstream issue #115 lands in a pinned ePC-SAFT dependency, or keep the package blocker explicit.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    reactions = reaction_rows()
    activity_candidates = activity_candidate_rows()
    species = dataset_species()
    artifact_manifest = read_csv(PARAMETER_MANIFEST)
    readiness = readiness_rows(reactions)
    output_status = required_output_status_rows(reactions)
    problem = problem_definition(reactions, activity_candidates, species)

    write_json(PROCESSED_DIR / "phase2_activity_speciation_problem.json", problem)
    write_json(RESULTS_DIR / "phase2_activity_speciation_problem.json", problem)
    write_csv(PROCESSED_DIR / "phase2_reaction_constant_basis.csv", reactions, list(reactions[0].keys()))
    write_csv(RESULTS_DIR / "phase2_reaction_constant_basis.csv", reactions, list(reactions[0].keys()))
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
    write_comparison(RESULTS_DIR / "phase2_comparison_to_phase1.md")

    print(f"Phase 2 scaffold artifacts: {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
