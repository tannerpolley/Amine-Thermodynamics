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
SOURCE_VERIFICATION = REPO_ROOT / "data" / "reference" / "MEA" / "manifests" / "phase2_reaction_constant_source_verification.csv"
PARAMETER_DATASET = REPO_ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_phase2"
PARAMETER_MANIFEST = PARAMETER_DATASET / "phase2_parameter_artifact_manifest.csv"
MEA_REFERENCE = REPO_ROOT / "data" / "reference" / "MEA"

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


def readiness_rows(reactions: list[dict[str, str]], source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    source_verified_count = sum(1 for row in source_rows if row["source_status"] == "source_verified")
    return [
        {
            "requirement": "true_species_basis",
            "status": "scaffold_ready",
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
            "status": "source_verified_but_solver_blocked",
            "evidence": "data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv",
            "notes": f"{source_verified_count} of {len(reactions)} constants have repo-local source values; no equilibrium solve is claimed.",
        },
        {
            "requirement": "activity_constant_candidates",
            "status": "source_verified_but_solver_blocked",
            "evidence": "data/reference/MEA/manifests/phase2_activity_constant_candidates.csv",
            "notes": "R1-R5 source values are carried as fixed candidate inputs; equilibrium rows remain blocked by upstream solver support and residual gates.",
        },
        {
            "requirement": "vle_fugacity_route",
            "status": "scaffold_ready_blocked_by_epcsaft_issue_115",
            "evidence": "docs/roadmaps/epcsaft_dependency_matrix.md",
            "notes": "Use generic reactive speciation and electrolyte bubble/fugacity support; do not add MEA-specific package APIs.",
        },
        {
            "requirement": "phase3_claim_boundary",
            "status": "bounded_incomplete",
            "evidence": "docs/roadmaps/phase2_activity_speciation_design.md",
            "notes": "Phase 2 is an activity-based evaluation, not a finalized joint-regression result.",
        },
    ]


def required_output_status_rows(reactions: list[dict[str, str]]) -> list[dict[str, str]]:
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
            "status": "scaffold_ready_blocked_by_epcsaft_issue_115",
            "blocking_requirement": "upstream ePC-SAFT issue #115 native activity-coupled speciation support",
            "next_action": "Rerun only after upstream issue #115 exposes the required activity-coupled solver path and the pinned dependency is updated.",
        },
        {
            "artifact": "phase2_pressure_speciation_parity.csv",
            "status": "bounded_incomplete",
            "blocking_requirement": "phase2_equilibrium_results.csv",
            "next_action": "Generate only from convention-safe Phase 2 equilibrium rows.",
        },
        {
            "artifact": "phase2_pressure_metrics.csv",
            "status": "bounded_incomplete",
            "blocking_requirement": "phase2_equilibrium_results.csv",
            "next_action": "Compute only after pressure predictions exist.",
        },
        {
            "artifact": "phase2_speciation_metrics.csv",
            "status": "bounded_incomplete",
            "blocking_requirement": "phase2_equilibrium_results.csv",
            "next_action": "Compute only after speciation predictions exist.",
        },
        {
            "artifact": "phase2_pH_validation.csv",
            "status": "source_pending" if not pH_files else "data_inventory_ready",
            "blocking_requirement": "convention-compatible pH data and activity-state mapping",
            "next_action": "Use pH only as validation/anchor data after scale and method are recorded.",
        },
        {
            "artifact": "phase2_density_viscosity_validation.csv",
            "status": "data_inventory_ready" if density_files else "source_pending",
            "blocking_requirement": "Phase 2 liquid states and validation formulas",
            "next_action": "Use Amundsen density/viscosity only as an external validation or regularization candidate.",
        },
        {
            "artifact": "phase2_comparison_to_phase1.md",
            "status": "problem_definition_generated",
            "blocking_requirement": "none",
            "next_action": "Update after convention-safe Phase 2 equilibrium outputs exist.",
        },
        {
            "artifact": "phase2_dielectric_policy",
            "status": "source_pending" if not dielectric_files else "data_inventory_ready",
            "blocking_requirement": "direct MEA-H2O dielectric/permittivity observations",
            "next_action": "Keep MEA f_solv fixed or sensitivity-only until direct evidence exists.",
        },
        {
            "artifact": "phase2_ionic_activity_policy",
            "status": "source_pending" if not ionic_activity_files else "data_inventory_ready",
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
        "status": "problem_definition_generated",
        "species": species,
        "charges": CHARGES,
        "volatile_species": list(VOLATILE_SPECIES),
        "nonvolatile_species": list(NONVOLATILE_SPECIES),
        "material_balances": MATERIAL_BALANCES,
        "constraints": CONSTRAINTS,
        "activity_convention": {
            "needed_basis": "thermodynamic_activity",
            "current_manifest_conversion_status": sorted({row["conversion_status"] for row in reactions}),
            "candidate_manifest": str(ACTIVITY_CANDIDATES.relative_to(REPO_ROOT)).replace("\\", "/"),
            "candidate_status_counts": candidate_status_counts,
            "solve_policy": "do_not_run_activity_solve_until_upstream_issue_115_activity_backend_is_available_and_residual_gates_are_defined",
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

Phase 1 is a retained ideal/apparent Smith-Missen baseline audit. It uses documented reaction constants without ePC-SAFT activity coefficients, but it is not an independent completed reproduction.

Phase 2 uses the nine-species liquid basis and one ePC-SAFT parameter artifact. The current Phase 2 output is a source-verified problem definition and bounded-incomplete scaffold, not a claimed activity-based equilibrium result, because the pinned upstream ePC-SAFT package lacks the required native activity-coupled speciation backend tracked in upstream issue #115.

Next required implementation: generate pressure/speciation tables only after upstream issue #115 lands in a pinned ePC-SAFT dependency, or keep the package blocker explicit.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bounded_report(path: Path, source_rows: list[dict[str, str]]) -> None:
    source_count = sum(1 for row in source_rows if row["source_status"] == "source_verified")
    text = f"""# Phase 2 Bounded Incomplete Report

phase2_status: bounded_incomplete
source_status: source_verified
solver_status: scaffold_ready_blocked_by_epcsaft_issue_115

This PR repairs the Phase 2 scaffold so it records verified source values and a true-species problem definition without claiming an activity-coupled equilibrium solve.

Evidence now present:
- {source_count} of {len(source_rows)} R1-R5 source-value rows are verified against repo-local source text in `phase2_reaction_constant_source_verification.csv`.
- The generated problem definition separates material balances from electroneutrality constraints.
- Required solver/residual artifacts are listed in `phase2_required_output_status.csv` as blocked or bounded incomplete until actual equilibrium rows and residual metrics exist.

Blocked work:
- `phase2_equilibrium_results.csv` must not be generated or claimed until upstream ePC-SAFT issue #115 is available in the pinned dependency.
- Pressure/speciation residual metrics must not be cited until generated from actual Phase 2 equilibrium rows.
- Phase 2 must remain a scaffold/problem-definition slice until the residual gates pass.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    reactions = reaction_rows()
    activity_candidates = activity_candidate_rows()
    source_rows = source_verification_rows()
    species = dataset_species()
    artifact_manifest = read_csv(PARAMETER_MANIFEST)
    readiness = readiness_rows(reactions, source_rows)
    output_status = required_output_status_rows(reactions)
    problem = problem_definition(reactions, activity_candidates, species)

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
    write_comparison(RESULTS_DIR / "phase2_comparison_to_phase1.md")
    write_bounded_report(RESULTS_DIR / "phase2_bounded_incomplete_report.md", source_rows)

    print(f"Phase 2 scaffold artifacts: {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
