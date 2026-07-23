from __future__ import annotations

import csv
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from MEA.common.config import DATA_ROOT, REPO_ROOT


REACTION_CONTRACT_PATH = DATA_ROOT / "manifests" / "chemical_reaction_source_contract.json"
SENTINEL_CONTRACT_PATH = (
    DATA_ROOT / "manifests" / "homogeneous_speciation_sentinel_contract.json"
)
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
PRIMARY_ANCHORS_298_15_K = {
    "R1": -40.26536023393261,
    "R2": -18.658825483177367,
    "R3": -27.80868301316974,
    "R4": -3.031961596511823,
    "R5": -21.86574617291778,
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Contract must be a JSON object: {path}")
    return value


def load_reaction_contract(
    path: Path = REACTION_CONTRACT_PATH,
) -> dict[str, Any]:
    return _load_json(path)


def load_sentinel_contract(
    path: Path = SENTINEL_CONTRACT_PATH,
) -> dict[str, Any]:
    return _load_json(path)


def _exact_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, row_count) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            multiple = work[row][column]
            if multiple:
                work[row] = [
                    value - multiple * pivot_value
                    for value, pivot_value in zip(work[row], work[rank], strict=True)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def _evaluate_ln_k(reaction: dict[str, Any], temperature_k: float) -> float:
    correlation = reaction["correlation"]
    kind = correlation["kind"]
    if kind == "ln_a_plus_b_over_t_plus_c_ln_t_plus_d_t":
        return (
            correlation["a"]
            + correlation["b_k"] / temperature_k
            + correlation["c"] * math.log(temperature_k)
            + correlation["d_per_k"] * temperature_k
        )
    if kind == "ln_a_plus_b_over_t":
        return correlation["a"] + correlation["b_k"] / temperature_k
    if kind == "ln_from_negative_log10_a_over_t_plus_b_plus_c_t":
        return -math.log(10.0) * (
            correlation["a_k"] / temperature_k
            + correlation["b"]
            + correlation["c_per_k"] * temperature_k
        )
    raise ValueError(f"Unsupported reaction correlation kind: {kind}")


def validate_reaction_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if contract.get("identity") != "mea-nine-species-reaction-source-contract-v1":
        raise ValueError("Unexpected MEA reaction contract identity")
    species_order = tuple(contract.get("species_order", ()))
    if species_order != EXPECTED_SPECIES_ORDER:
        raise ValueError("MEA reaction species order does not match the nine-species contract")

    species = contract.get("species", [])
    if [row.get("name") for row in species] != list(EXPECTED_SPECIES_ORDER):
        raise ValueError("MEA species records do not match the declared order")
    balance_rows = [
        [int(row["formula"][element]) for row in species]
        for element in contract["balance_row_order"]
    ]
    balance_rank = _exact_rank(balance_rows)
    if balance_rank != contract.get("declared_balance_rank"):
        raise ValueError("MEA balance matrix rank does not match its declaration")

    reactions = contract.get("reactions", [])
    if [row.get("reaction_id") for row in reactions] != list(PRIMARY_ANCHORS_298_15_K):
        raise ValueError("MEA reaction records must contain ordered unique R1-R5 rows")
    source_records = contract.get("source_records", [])
    source_ids = {row.get("source_id") for row in source_records}
    if None in source_ids or len(source_ids) != len(source_records):
        raise ValueError("MEA reaction source records must have unique source identities")
    reaction_matrix = [list(map(int, row["stoichiometry"])) for row in reactions]
    if any(len(row) != len(species) for row in reaction_matrix):
        raise ValueError("MEA reaction stoichiometry dimensions do not match species order")
    reaction_rank = _exact_rank(reaction_matrix)
    if reaction_rank != contract.get("declared_reaction_rank"):
        raise ValueError("MEA reaction matrix rank does not match its declaration")

    for reaction, expected in zip(
        reactions, PRIMARY_ANCHORS_298_15_K.values(), strict=True
    ):
        reaction_id = reaction["reaction_id"]
        required_metadata = (
            "equation",
            "selected_source",
            "source_role",
            "activity_convention",
            "source_standard_state",
            "pressure_binding",
        )
        if (
            any(not reaction.get(field) for field in required_metadata)
            or reaction.get("dimensionless") is not True
            or reaction.get("contract_logarithm") != "natural"
            or not reaction.get("source_record_ids")
            or not set(reaction["source_record_ids"]) <= source_ids
        ):
            raise ValueError(f"{reaction_id} source metadata is incomplete")
        temperature_k = float(reaction["anchor_temperature_k"])
        actual = _evaluate_ln_k(reaction, temperature_k)
        tolerance = float(reaction["anchor_abs_tolerance"])
        if abs(actual - expected) > tolerance:
            raise ValueError(f"{reaction_id} primary-source anchor is inconsistent")
        if abs(float(reaction["anchor_ln_k"]) - expected) > tolerance:
            raise ValueError(f"{reaction_id} retained anchor is inconsistent")
        lower, upper = map(float, reaction["temperature_range_k"])
        if not lower <= temperature_k <= upper:
            raise ValueError(f"{reaction_id} anchor lies outside its source range")
        for balance in balance_rows:
            if sum(
                coefficient * amount
                for coefficient, amount in zip(balance, reaction["stoichiometry"], strict=True)
            ):
                raise ValueError(f"{reaction_id} does not conserve the declared elements")
        if sum(
            int(row["charge"]) * amount
            for row, amount in zip(species, reaction["stoichiometry"], strict=True)
        ):
            raise ValueError(f"{reaction_id} does not conserve charge")

    if _exact_rank([*balance_rows, *reaction_matrix]) != len(species):
        raise ValueError("MEA balances and reactions do not span the species space")
    temperature_intersection = [
        max(float(row["temperature_range_k"][0]) for row in reactions),
        min(float(row["temperature_range_k"][1]) for row in reactions),
    ]
    if temperature_intersection[0] > temperature_intersection[1]:
        raise ValueError("MEA reaction source temperature domains do not intersect")

    common = contract.get("common_source_standard_state", {})
    if (
        common.get("identity") != "aqueous-molality-infinite-dilution-water-v1"
        or common.get("ready") is not True
        or common.get("solvent") != "H2O"
        or float(common.get("solute_standard_molality_mol_per_kg", 0.0)) != 1.0
    ):
        raise ValueError("MEA common source standard state is incomplete")
    water_molar_mass = float(common["water_molar_mass_kg_per_mol"])
    log_scale = math.log(
        water_molar_mass * float(common["solute_standard_molality_mol_per_kg"])
    )
    expected_scales = [
        0.0 if species_id == "H2O" else log_scale
        for species_id in EXPECTED_SPECIES_ORDER
    ]
    if any(
        abs(actual - expected) > 5.0e-15
        for actual, expected in zip(
            common["log_activity_scale_factors_by_species"],
            expected_scales,
            strict=True,
        )
    ):
        raise ValueError("MEA common source activity-scale vector is inconsistent")
    molar_mass_path = REPO_ROOT / common["water_molar_mass_source"]
    if _sha256(molar_mass_path) != common["water_molar_mass_source_sha256"]:
        raise ValueError("MEA common source water-molar-mass fingerprint does not match")
    exponents = list(map(int, common["source_to_common_solute_stoichiometric_exponents"]))
    if exponents != [2, 1, 1, 0, 0]:
        raise ValueError("MEA source-to-common reaction exponents are inconsistent")
    offsets = [-exponent * log_scale for exponent in exponents]
    if any(
        abs(actual - expected) > 5.0e-15
        for actual, expected in zip(
            common["source_to_common_ln_k_offsets"], offsets, strict=True
        )
    ):
        raise ValueError("MEA source-to-common lnK offsets are inconsistent")
    common_ln_k = [
        anchor + offset
        for anchor, offset in zip(
            PRIMARY_ANCHORS_298_15_K.values(), offsets, strict=True
        )
    ]
    if any(
        abs(actual - expected) > 5.0e-15
        for actual, expected in zip(
            common["common_ln_k_298_15_k"], common_ln_k, strict=True
        )
    ):
        raise ValueError("MEA common-source lnK anchors are inconsistent")

    provider_transform = contract.get("provider_transform", {})
    blockers = provider_transform.get("blockers")
    if (
        provider_transform.get("ready") is not False
        or provider_transform.get("required_common_source_convention")
        != common["identity"]
        or blockers
        != ["provider-neutral-reference-unavailable-until-qualified-bundle-domain"]
    ):
        raise ValueError("MEA Provider transformation must retain its exact unresolved blockers")
    return {
        "reaction_count": len(reactions),
        "reaction_rank": reaction_rank,
        "balance_rank": balance_rank,
        "temperature_intersection_k": temperature_intersection,
        "common_source_standard_state": common["identity"],
        "common_ln_k_298_15_k": common_ln_k,
        "source_conversion_ready": True,
        "provider_transform_ready": False,
        "blockers": blockers,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_row(path: Path, record_id: str) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        matches = [row for row in csv.DictReader(handle) if row["record_id"] == record_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one source row {record_id} in {path}")
    return matches[0]


def validate_sentinel_contract(
    contract: dict[str, Any], reaction_contract: dict[str, Any]
) -> dict[str, Any]:
    reaction_summary = validate_reaction_contract(reaction_contract)
    if contract.get("identity") != "mea-homogeneous-fixed-tp-sentinel-contract-v1":
        raise ValueError("Unexpected MEA sentinel contract identity")
    if tuple(contract.get("species_order", ())) != EXPECTED_SPECIES_ORDER:
        raise ValueError("MEA sentinel species order does not match the reaction contract")
    states = contract.get("states", [])
    if len(states) != 1:
        raise ValueError("MEA sentinel contract must contain exactly one source-bound state")
    state = states[0]

    source_path = REPO_ROOT / state["source_file"]
    source = _source_row(source_path, state["source_record_id"])
    temperature_k = float(source["temperature_K"])
    pressure_pa = float(source["pressure_bar"]) * 100_000.0
    loading = float(source["calculated_loading"])
    mass_fraction = float(source["mea_mass_fraction"])
    reported = state.get("reported_observations", {})
    if (
        temperature_k != float(state["temperature_k"])
        or pressure_pa != float(state["pressure_pa"])
        or loading != float(state["loading_mol_co2_per_mol_mea"])
        or mass_fraction != float(state["mea_mass_fraction_unloaded"])
        or float(source["calculated_loading"]) != float(reported.get("calculated_loading"))
        or float(source["predicted_loading"]) != float(reported.get("raman_loading"))
        or float(source["mse"]) != float(reported.get("mse"))
    ):
        raise ValueError("MEA sentinel state does not reproduce its Wong source row")
    if (
        state.get("pressure_convention")
        != "published nominal total pressure for the closed-feed batch row"
        or state.get("uncertainty_status")
        != "no row-specific standard uncertainty reported"
        or reported.get("mse_role")
        != "reported squared agreement metric, not a measurement uncertainty"
    ):
        raise ValueError("MEA sentinel pressure or uncertainty convention is incomplete")

    molar_mass = contract["molar_mass_basis"]
    molar_mass_path = REPO_ROOT / molar_mass["source_file"]
    if _sha256(molar_mass_path) != molar_mass["source_file_sha256"]:
        raise ValueError("MEA sentinel molar-mass artifact fingerprint does not match")
    values = molar_mass["values"]
    water_amount = (
        (1.0 - mass_fraction)
        / mass_fraction
        * float(values["MEA"])
        / float(values["H2O"])
    )
    expected_feed = [loading, 1.0, water_amount, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    actual_feed = list(map(float, state["feed_amounts_mol"]))
    if len(actual_feed) != len(expected_feed) or any(
        abs(actual - expected) > 2.0e-15
        for actual, expected in zip(actual_feed, expected_feed, strict=True)
    ):
        raise ValueError("MEA sentinel feed amounts do not match the source-bound mass basis")

    charges = [int(row["charge"]) for row in reaction_contract["species"]]
    charge = sum(
        amount * charge_number
        for amount, charge_number in zip(actual_feed, charges, strict=True)
    )
    if charge != float(state["initial_charge_equivalents_mol"]):
        raise ValueError("MEA sentinel feed is not exactly electroneutral")
    lower, upper = reaction_summary["temperature_intersection_k"]
    reaction_domain_passed = lower <= temperature_k <= upper
    if reaction_domain_passed is not state.get("reaction_domain_passed"):
        raise ValueError("MEA sentinel reaction-domain status is inconsistent")

    oxazolidone = state["oxazolidone_rule"]
    exclusion_passed = loading < float(oxazolidone["excluded_when_loading_below"])
    if exclusion_passed is not oxazolidone.get("passed"):
        raise ValueError("MEA sentinel oxazolidone exclusion status is inconsistent")
    if state.get("observation_roles") != {
        "calculated_loading_0.150": "direct_closed_feed_input_from_gas_pressure_drop",
        "raman_loading_0.144": "calibration_derived_context_only",
        "species_concentrations": "not_available_for_this_row_and_not_predictive_acceptance",
        "equilibrium_capacity": "not_claimed",
    }:
        raise ValueError("MEA sentinel observation roles are incomplete")
    blockers = state.get("blockers")
    expected_blockers = [
        "provider-parameter-bundle-provisional",
        "provider-applicability-domain-unknown",
    ]
    if state.get("equilibrium_ready") is not False or blockers != expected_blockers:
        raise ValueError("MEA sentinel must fail closed on its unresolved scientific blockers")

    return {
        "state_count": 1,
        "temperature_k": temperature_k,
        "pressure_pa": pressure_pa,
        "feed_amounts_mol": actual_feed,
        "initial_charge_equivalents_mol": charge,
        "reaction_domain_passed": reaction_domain_passed,
        "oxazolidone_exclusion_passed": exclusion_passed,
        "equilibrium_ready": False,
        "blockers": blockers,
    }
