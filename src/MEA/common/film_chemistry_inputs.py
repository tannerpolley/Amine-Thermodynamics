from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from MEA.common.config import DATA_ROOT, REPO_ROOT


BUNDLE_ROOT = DATA_ROOT / "film_chemistry_inputs" / "1"
INPUT_PATH = BUNDLE_ROOT / "input.json"
SCHEMA_PATH = BUNDLE_ROOT / "schema.json"
RECEIPT_PATH = DATA_ROOT / "film_chemistry_inputs" / "1.receipt.json"
REACTION_CONTRACT_PATH = DATA_ROOT / "manifests" / "chemical_reaction_source_contract.json"
EXPECTED_BASE_COMMIT = "9f7c83d80900a10fbff7007c2137d126e92d9b3d"
EXPECTED_SPECIES_ORDER = (
    "CO2",
    "MEA",
    "H2O",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3--",
    "H3O+",
    "OH-",
)
EXPECTED_SOURCE_REACTION_ORDER = ("R1", "R2", "R3", "R4", "R5")
EXPECTED_EXCLUSIONS = {
    "active_or_default_MEA_parameter_set",
    "historical_parameter_restore",
    "Provider_activity_correction",
    "bulk_ePC_SAFT_equilibrium",
    "numerical_activity_closure",
    "packet_bound_activity_concentration_comparison",
    "film_flux_prediction",
    "chemistry_specific_film_solver",
    "Maxwell_Stefan_matrix",
    "downstream_adoption_packet",
    "Issue_72_closure",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _balance(
    stoichiometry: list[int], species: list[dict[str, Any]]
) -> dict[str, int]:
    return {
        key: sum(
            coefficient * int(row["formula"][key])
            for coefficient, row in zip(stoichiometry, species, strict=True)
        )
        for key in ("C", "H", "N", "O")
    } | {
        "charge": sum(
            coefficient * int(row["charge"])
            for coefficient, row in zip(stoichiometry, species, strict=True)
        )
    }


def validate_film_chemistry_inputs() -> dict[str, Any]:
    payload = _load_json(INPUT_PATH)
    schema = _load_json(SCHEMA_PATH)
    receipt = _load_json(RECEIPT_PATH)
    reaction_contract = _load_json(REACTION_CONTRACT_PATH)
    checks: list[str] = []

    if set(schema["required"]) != set(payload):
        raise ValueError("Input keys do not match the frozen schema")
    if (
        payload.get("schema_version") != 1
        or payload.get("identity")
        != "mea-film-chemistry-work-package-a-input-v1"
        or payload.get("status") != "source_complete_nonexecutable_input_contract"
        or payload.get("base_commit") != EXPECTED_BASE_COMMIT
    ):
        raise ValueError("Unexpected Work Package A input identity")
    checks.append("schema_identity_and_base_commit")

    expected_hashes = {
        "1/input.json": _sha256(INPUT_PATH),
        "1/schema.json": _sha256(SCHEMA_PATH),
    }
    if receipt.get("files") != expected_hashes:
        raise ValueError("Work Package A bundle hashes do not match the receipt")
    checks.append("bundle_file_hashes")

    if (
        tuple(payload["species_order"]) != EXPECTED_SPECIES_ORDER
        or [row["id"] for row in payload["species"]]
        != list(EXPECTED_SPECIES_ORDER)
        or tuple(payload["source_reaction_order"])
        != EXPECTED_SOURCE_REACTION_ORDER
        or payload["species_order"] != reaction_contract["species_order"]
        or payload["source_reaction_order"]
        != [row["reaction_id"] for row in reaction_contract["reactions"]]
    ):
        raise ValueError("Species or reaction ordering drifted")
    if (
        payload["source_standard_conversion"]["source_contract_sha256"]
        != _sha256(REACTION_CONTRACT_PATH)
    ):
        raise ValueError("Reaction-source contract hash drifted")
    checks.append("species_reaction_order_and_source_hash")

    source_rows = {
        row["reaction_id"]: row["stoichiometry"]
        for row in reaction_contract["reactions"]
    }
    balances: dict[str, dict[str, int]] = {}
    for reaction in payload["finite_reactions"]:
        projection = reaction["source_basis_projection"]
        reconstructed = [
            sum(projection[row_id] * source_rows[row_id][column] for row_id in projection)
            for column in range(len(EXPECTED_SPECIES_ORDER))
        ]
        if reconstructed != reaction["stoichiometry"]:
            raise ValueError(f"{reaction['reaction_id']} source-basis projection drifted")
        balances[reaction["reaction_id"]] = _balance(
            reaction["stoichiometry"], payload["species"]
        )
        if any(balances[reaction["reaction_id"]].values()):
            raise ValueError(f"{reaction['reaction_id']} violates balance invariants")
        if not (
            reaction["stoichiometry"][0] < 0
            and "CO2 consumption" in reaction["forward_direction"]
            and "CO2 release" in reaction["reverse_direction"]
        ):
            raise ValueError(f"{reaction['reaction_id']} direction signs drifted")
    expected_net_carbamate = [-1, -2, 0, 1, 1, 0, 0, 0, 0]
    if payload["finite_reactions"][0]["stoichiometry"] != expected_net_carbamate:
        raise ValueError("Net carbamate projection drifted")
    checks.extend(
        ["source_basis_projections", "element_and_charge_balances", "direction_signs"]
    )

    admitted_fast = {
        row["reaction_id"]
        for row in payload["film_classification"]
        if row["film_role"] == "fast_equilibrium_candidate"
        and row["admission_status"] == "admitted"
    }
    finite_sources = {
        row["reaction_id"]
        for row in payload["film_classification"]
        if row["film_role"] == "finite_projection_source"
        and row["admission_status"] == "admitted"
    }
    if admitted_fast & finite_sources:
        raise ValueError("A reaction is both fast-equilibrium and finite-rate")
    checks.append("fast_finite_disjointness")

    reconstructed_anchors = 0
    tolerance = payload["validation_policy"]
    if (
        tolerance["correlation_anchor_relative_tolerance"] != 1e-12
        or tolerance["correlation_anchor_absolute_tolerance"] != 0.0
        or tolerance["stoichiometry_balance_hash_and_order_tolerance"] != "exact"
        or not tolerance["correlation_tolerance_rationale"]
        or not tolerance["aard_metric_policy"]
    ):
        raise ValueError("Validation tolerance or metric rationale drifted")
    for correlation in payload["kinetic_correlations"]:
        lower, upper = correlation["temperature_domain_k"]
        if lower > upper or correlation["uncertainty_status"] != "not_reported":
            raise ValueError("Kinetic domain or uncertainty status drifted")
        for anchor in correlation["anchors"]:
            if not lower <= anchor["temperature_k"] <= upper:
                raise ValueError("Kinetic anchor lies outside its source domain")
            actual = correlation["A"] * math.exp(
                -correlation["B_k"] / anchor["temperature_k"]
            )
            if not math.isclose(
                actual,
                anchor["expected"],
                rel_tol=tolerance["correlation_anchor_relative_tolerance"],
                abs_tol=tolerance["correlation_anchor_absolute_tolerance"],
            ):
                raise ValueError("Published kinetic correlation reconstruction drifted")
            reconstructed_anchors += 1
        if correlation["admission_status"].startswith("admitted"):
            raise ValueError("Dimensionally unresolved kinetic correlation was admitted")
    checks.extend(["published_correlation_reconstruction", "dimensional_rejection"])

    for row in payload["transport_inputs"]:
        if not row["admission_status"].startswith("rejected"):
            raise ValueError("Unsupported transport coefficient was admitted")
        if not row["unit"] or not row["uncertainty_status"] or not row["reason"]:
            raise ValueError("Transport units or uncertainty status are incomplete")
    for row in payload["property_inputs"]:
        path = REPO_ROOT / row["data_path"]
        if _sha256(path) != row["data_sha256"]:
            raise ValueError(f"Property source hash drifted: {path}")
        if row["domain"]["temperature_k"][0] > row["domain"]["temperature_k"][1]:
            raise ValueError("Property domain is inverted")
    checks.extend(["transport_fail_closed", "property_provenance_domains_uncertainty"])

    conversion = payload["source_standard_conversion"]
    if (
        conversion["provider_activity_correction_ran"] is not False
        or conversion["status"] != "algebraic_identity_only"
        or conversion["identity"]
        != reaction_contract["provider_transform"]["identity"]
        or conversion["algebraic_identity"]
        != reaction_contract["provider_transform"]["deterministic_payload"][
            "transformed_vector_definition"
        ]
    ):
        raise ValueError("Provider conversion scope drifted")
    checks.append("algebraic_conversion_without_provider_evaluation")

    exclusions = payload["exclusions"]
    if (
        exclusions["column_fitted_quantities"] != []
        or set(exclusions["explicit"]) != EXPECTED_EXCLUSIONS
    ):
        raise ValueError("Explicit exclusions drifted")
    checks.append("explicit_exclusions_and_no_column_fit")

    return {
        "status": "pass",
        "input_identity": payload["identity"],
        "input_sha256": expected_hashes["1/input.json"],
        "schema_sha256": expected_hashes["1/schema.json"],
        "checks": checks,
        "finite_reaction_count": len(payload["finite_reactions"]),
        "kinetic_anchor_count": reconstructed_anchors,
        "net_carbamate_balance": balances["F1"],
        "admitted_fast_equilibrium_reactions": sorted(admitted_fast),
        "admitted_numeric_transport_inputs": [],
        "provider_activity_correction_ran": False,
        "limitations": [
            "Published kinetic coefficient units are dimensionally inconsistent with the published rate unit.",
            "Source-complete CO2, free-MEA, and ionic diffusivity coefficients are unavailable.",
            "The retained density CSV uncertainty differs by one decimal place from the primary source.",
            "No active MEA parameter packet exists; Work Package B remains blocked by ePC-SAFT Issue #80.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    report = validate_film_chemistry_inputs()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
