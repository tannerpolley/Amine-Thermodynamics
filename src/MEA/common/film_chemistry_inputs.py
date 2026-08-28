from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from MEA.common.config import DATA_ROOT, REPO_ROOT


BUNDLE_ROOT = DATA_ROOT / "film_chemistry_inputs" / "1"
INPUT_PATH = BUNDLE_ROOT / "input.json"
SCHEMA_PATH = BUNDLE_ROOT / "schema.json"
RECEIPT_PATH = DATA_ROOT / "film_chemistry_inputs" / "1.receipt.json"
REACTION_CONTRACT_PATH = (
    DATA_ROOT / "manifests" / "chemical_reaction_source_contract.json"
)
BASE_COMMIT = "9f7c83d80900a10fbff7007c2137d126e92d9b3d"
SPECIES_ORDER = tuple("CO2 MEA H2O MEAH+ MEACOO- HCO3- CO3-- H3O+ OH-".split())
REACTION_ORDER = tuple("R1 R2 R3 R4 R5".split())
CLASSIFICATION = {
    "R1": ("fast_equilibrium_candidate", "rejected"),
    "R2": ("finite_projection_source", "admitted"),
    "R3": ("fast_equilibrium_candidate", "rejected"),
    "R4": ("fast_equilibrium_candidate", "rejected"),
    "R5": ("fast_equilibrium_candidate", "rejected"),
}
COMMON_DOMAIN = {
    "temperature_k": {
        "minimum_inclusive": 293.15,
        "maximum_inclusive": 323.15,
        "basis": "retained R4/R5 source-domain intersection",
    },
    "mea_molarity_mol_l": {
        "supported_discrete": [1.0, 5.0],
        "admission_rule": "exact_discrete_cases_only",
        "basis": "source-complete Putta2016 fit-corpus endpoints",
    },
    "loading_mol_co2_per_mol_mea": {
        "minimum_inclusive": 0.0,
        "maximum_exclusive": 0.5,
        "guard": "reject_loading_greater_than_or_equal_to_0.5",
        "reason": "Oxazolidone treatment is not included.",
    },
    "downstream_admission_rule": "A state must satisfy all three limits; broader local source domains remain provenance only.",
}
SOURCE_DOIS = {
    "Putta2016": "10.1016/j.ijggc.2016.08.009",
    "Putta2017": "10.1016/j.cej.2017.06.134",
    "Gaspar2015": "10.1016/j.ces.2015.08.023",
    "Amundsen2009": "10.1021/je900188m",
    "Luo2015": "10.1016/j.ces.2014.10.013",
    "PachecoRochelle1998": "10.1021/ie980123g",
}
EXCLUSIONS = set(
    "active_or_default_MEA_parameter_set historical_parameter_restore Provider_activity_correction "
    "bulk_ePC_SAFT_equilibrium numerical_activity_closure packet_bound_activity_concentration_comparison "
    "film_flux_prediction chemistry_specific_film_solver Maxwell_Stefan_matrix downstream_adoption_packet "
    "Issue_72_closure".split()
)


def _fields(names: str) -> set[str]:
    return set(names.split())


CLASSIFICATION_FIELDS = _fields("reaction_id film_role admission_status reason")
FINITE_FIELDS = _fields(
    "reaction_id equation stoichiometry source_basis_projection forward_direction reverse_direction classification_status rate_equation concentration_basis rate_unit standard_concentration coefficient_status uncertainty_status source_record_id source_locator"
)
CORRELATION_FIELDS = _fields(
    "correlation_id reaction_id basis equation A B_k source_reported_unit dimensionally_required_unit admission_status reason temperature_domain_k uncertainty_status evaluation_anchors"
)
TRANSPORT_FIELDS = _fields(
    "input_id species unit source_record_id source_locator uncertainty_status admission_status reason"
)
PROPERTY_FIELDS = _fields(
    "input_id source_record_id data_path data_sha256 source_locator domain instrument_uncertainty uncertainty_status admission_status reason"
)
OBSERVATION_FIELDS = _fields(
    "observation_id kind unit uncertainty_status domain admission_status reason"
)
ROW_FIELDS = {
    "D_CO2_effective_fick": TRANSPORT_FIELDS | {"candidate_identities", "domains"},
    "D_MEA_free_effective_fick": TRANSPORT_FIELDS | {"candidate_identity", "domain"},
    "D_ions_smallest_documented_approximation": TRANSPORT_FIELDS
    | {"candidate_identity", "domain"},
    "liquid_density_unloaded": PROPERTY_FIELDS
    | {"loading_state", "applicable_uncertainty"},
    "liquid_density_loaded": PROPERTY_FIELDS
    | {"loading_state", "applicable_uncertainty"},
    "liquid_dynamic_viscosity": PROPERTY_FIELDS
    | {"applicable_uncertainty_by_loading_state"},
    "Putta2016_fit_corpus_summary": OBSERVATION_FIELDS
    | {"value", "source_record_id", "source_locator"},
    "Putta2016_external_AARD_table": OBSERVATION_FIELDS
    | {"metric", "rows", "column_order", "source_record_id", "source_locator"},
    "transport_numeric_candidates": OBSERVATION_FIELDS
    | {"admitted", "rejected", "source_record_ids"},
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label} keys are malformed")
    return value


def _rows(
    value: Any,
    identities: list[str],
    id_field: str,
    fields: set[str] | dict[str, set[str]],
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != len(identities):
        raise ValueError(f"{id_field} cardinality drifted")
    if [row.get(id_field) for row in value if isinstance(row, dict)] != identities:
        raise ValueError(f"{id_field} identity or order drifted")
    for row, identity in zip(value, identities, strict=True):
        _keys(row, fields[identity] if isinstance(fields, dict) else fields, identity)
    return value


def _interval(value: Any, label: str) -> tuple[float, float]:
    numeric = (
        isinstance(value, list)
        and len(value) == 2
        and all(type(item) in (int, float) and math.isfinite(item) for item in value)
    )
    if not numeric or value[0] > value[1]:
        raise ValueError(f"{label} is malformed")
    return float(value[0]), float(value[1])


def validate_application_state(
    temperature_k: float,
    mea_molarity_mol_l: float,
    loading_mol_co2_per_mol_mea: float,
    *,
    payload: dict[str, Any] | None = None,
) -> None:
    if (payload or _load(INPUT_PATH)).get("common_application_domain") != COMMON_DOMAIN:
        raise ValueError("Common application domain drifted")
    if not 293.15 <= temperature_k <= 323.15:
        raise ValueError("temperature lies outside the common application domain")
    if mea_molarity_mol_l not in (1.0, 5.0):
        raise ValueError("MEA molarity is not a source-complete discrete case")
    if not 0.0 <= loading_mol_co2_per_mol_mea < 0.5:
        raise ValueError("loading lies outside the oxazolidone-guarded domain")


def _balance(stoichiometry: list[int], species: list[dict[str, Any]]) -> dict[str, int]:
    balance = {
        element: sum(
            coefficient * row["formula"][element]
            for coefficient, row in zip(stoichiometry, species, strict=True)
        )
        for element in "CHNO"
    }
    balance["charge"] = sum(
        coefficient * row["charge"]
        for coefficient, row in zip(stoichiometry, species, strict=True)
    )
    return balance


def _validate_schema_receipt(
    payload: dict[str, Any], schema: dict[str, Any], receipt: dict[str, Any]
) -> dict[str, str]:
    _keys(
        schema,
        _fields(
            "$schema $id title type required properties additionalProperties $defs"
        ),
        "schema",
    )
    if (
        schema["$id"] != "mea-film-chemistry-work-package-a-v1"
        or schema["type"] != "object"
        or schema["additionalProperties"] is not False
        or set(schema["required"]) != set(schema["properties"])
    ):
        raise ValueError("Schema declaration drifted")
    _keys(payload, set(schema["required"]), "input")
    identity = (
        1,
        "mea-film-chemistry-work-package-a-input-v1",
        "source_validated_deferred_inputs",
        BASE_COMMIT,
    )
    if (
        payload["schema_version"],
        payload["identity"],
        payload["status"],
        payload["base_commit"],
    ) != identity:
        raise ValueError("Input identity drifted")
    hashes = {
        "1/input.json": _sha256(INPUT_PATH),
        "1/schema.json": _sha256(SCHEMA_PATH),
    }
    expected = {
        "schema_version": 1,
        "identity": "mea-film-chemistry-work-package-a-receipt-v1",
        "bundle_identity": payload["identity"],
        "base_commit": BASE_COMMIT,
        "files": hashes,
        "scope": "Issue #72 Work Package A only; Work Package B remains blocked by ePC-SAFT Issue #80.",
    }
    if receipt != expected:
        raise ValueError("Receipt identity, scope, or hashes drifted")
    return hashes


def _validate_reactions(
    payload: dict[str, Any], source_contract: dict[str, Any]
) -> dict[str, dict[str, int]]:
    if (
        tuple(payload["species_order"]) != SPECIES_ORDER
        or tuple(payload["source_reaction_order"]) != REACTION_ORDER
        or payload["species_order"] != source_contract["species_order"]
    ):
        raise ValueError("Species or reaction order drifted")
    species = _rows(
        payload["species"], list(SPECIES_ORDER), "id", {"id", "formula", "charge"}
    )
    if any(
        row["formula"] != source["formula"] or row["charge"] != source["charge"]
        for row, source in zip(species, source_contract["species"], strict=True)
    ):
        raise ValueError("Species formula or charge drifted")
    classifications = _rows(
        payload["film_classification"],
        list(REACTION_ORDER),
        "reaction_id",
        CLASSIFICATION_FIELDS,
    )
    if any(
        CLASSIFICATION[row["reaction_id"]]
        != (row["film_role"], row["admission_status"])
        or not row["reason"]
        for row in classifications
    ):
        raise ValueError("Reaction classification or admission drifted")

    reactions = _rows(
        payload["finite_reactions"], ["F1", "F2", "F3"], "reaction_id", FINITE_FIELDS
    )
    source_rows = {
        row["reaction_id"]: row["stoichiometry"] for row in source_contract["reactions"]
    }
    balances: dict[str, dict[str, int]] = {}
    for reaction in reactions:
        projection = _keys(
            reaction["source_basis_projection"], set(REACTION_ORDER), "projection"
        )
        stoichiometry = reaction["stoichiometry"]
        values = (
            [*stoichiometry, *projection.values()]
            if isinstance(stoichiometry, list)
            else []
        )
        if len(stoichiometry) != 9 or any(type(value) is not int for value in values):
            raise ValueError("Finite-reaction stoichiometry is malformed")
        reconstructed = [
            sum(
                projection[row_id] * source_rows[row_id][column]
                for row_id in projection
            )
            for column in range(9)
        ]
        balances[reaction["reaction_id"]] = _balance(stoichiometry, species)
        if reconstructed != stoichiometry or any(
            balances[reaction["reaction_id"]].values()
        ):
            raise ValueError("Finite-reaction projection or balance drifted")
        valid = (
            stoichiometry[0] < 0
            and "CO2 consumption" in reaction["forward_direction"]
            and "CO2 release" in reaction["reverse_direction"]
            and reaction["classification_status"] == "admitted_finite_reaction"
            and reaction["rate_unit"] == "kmol m^-3 s^-1"
            and reaction["uncertainty_status"] == "not_reported"
        )
        if not valid:
            raise ValueError("Finite-reaction direction, unit, or status drifted")
    if reactions[0]["stoichiometry"] != [-1, -2, 0, 1, 1, 0, 0, 0, 0]:
        raise ValueError("Net carbamate projection drifted")
    return balances


def _validate_correlations(payload: dict[str, Any]) -> int:
    ids = "Putta2016_k_MEA_c Putta2016_k_H2O_c Putta2016_k_MEA_a Putta2016_k_H2O_a".split()
    rows = _rows(
        payload["kinetic_correlations"], ids, "correlation_id", CORRELATION_FIELDS
    )
    policy = _keys(
        payload["validation_policy"],
        _fields(
            "correlation_evaluation_relative_tolerance correlation_evaluation_absolute_tolerance correlation_evaluation_rationale stoichiometry_balance_hash_and_order_tolerance aard_metric_policy"
        ),
        "validation policy",
    )
    if (
        policy["correlation_evaluation_relative_tolerance"] != 1e-12
        or policy["correlation_evaluation_absolute_tolerance"] != 0.0
        or "same printed A/B coefficients"
        not in policy["correlation_evaluation_rationale"]
    ):
        raise ValueError("Correlation evaluation policy drifted")
    count = 0
    for row in rows:
        lower, upper = _interval(row["temperature_domain_k"], "correlation domain")
        anchors = row["evaluation_anchors"]
        valid = (
            row["equation"] == "k = A exp(-B/T)"
            and row["source_reported_unit"] == "m^6 kmol^-2 s^-2"
            and row["uncertainty_status"] == "not_reported"
            and row["admission_status"].startswith("rejected")
            and isinstance(anchors, list)
            and len(anchors) == 2
        )
        if not valid:
            raise ValueError("Correlation unit, status, or anchors drifted")
        for anchor in anchors:
            _keys(anchor, {"temperature_k", "expected"}, "evaluation anchor")
            temperature = anchor["temperature_k"]
            if not lower <= temperature <= upper or not math.isclose(
                row["A"] * math.exp(-row["B_k"] / temperature),
                anchor["expected"],
                rel_tol=1e-12,
                abs_tol=0.0,
            ):
                raise ValueError("Correlation evaluation/transcription drifted")
            count += 1
    return count


def _validate_evidence(payload: dict[str, Any]) -> None:
    transport_ids = "D_CO2_effective_fick D_MEA_free_effective_fick D_ions_smallest_documented_approximation".split()
    transport = _rows(
        payload["transport_inputs"], transport_ids, "input_id", ROW_FIELDS
    )
    if any(
        row["unit"] != "m^2 s^-1"
        or row["uncertainty_status"] != "not_reported"
        or not row["admission_status"].startswith("rejected")
        for row in transport
    ):
        raise ValueError("Transport unit, uncertainty, or admission drifted")
    for domain in transport[0]["domains"]:
        fields = (
            _fields("id temperature_k mea_molarity_mol_l loading")
            if domain.get("id") == "DC1_Ko_N2O"
            else _fields("id temperature_k mea_scope loading")
        )
        _keys(domain, fields, "CO2 transport domain")
        _interval(domain["temperature_k"], "transport temperature")
        _interval(domain["loading"], "transport loading")

    property_ids = (
        "liquid_density_unloaded liquid_density_loaded liquid_dynamic_viscosity".split()
    )
    properties = _rows(payload["property_inputs"], property_ids, "input_id", ROW_FIELDS)
    instrument = {
        "value": 0.00005,
        "unit": "g cm^-3",
        "type": "estimated_measurement_absolute",
    }
    for row, state, value in zip(
        properties[:2], ("unloaded", "loaded"), (0.0005, 0.002), strict=True
    ):
        applicable = {"value": value, "unit": "g cm^-3", "type": "combined_absolute"}
        if (
            row["loading_state"] != state
            or row["instrument_uncertainty"] != instrument
            or row["applicable_uncertainty"] != applicable
        ):
            raise ValueError("Density uncertainty meaning drifted")
    domain_fields = {
        "liquid_density_unloaded": _fields(
            "temperature_k mea_mass_fraction_supported loading_mol_co2_per_mol_mea"
        ),
        "liquid_density_loaded": _fields(
            "temperature_k mea_mass_fraction_supported loading_mol_co2_per_mol_mea_supported"
        ),
        "liquid_dynamic_viscosity": _fields(
            "temperature_k unloaded_mea_mass_fraction_supported loaded_mea_mass_fraction_supported loading_mol_co2_per_mol_mea_supported"
        ),
    }
    for row in properties:
        valid = (
            _sha256(REPO_ROOT / row["data_path"]) == row["data_sha256"]
            and row["uncertainty_status"] == "reported_combined"
            and row["admission_status"]
            == "admitted_observation_source_not_interpolator"
        )
        if not valid:
            raise ValueError("Property provenance or admission drifted")
        _interval(
            _keys(row["domain"], domain_fields[row["input_id"]], "property domain")[
                "temperature_k"
            ],
            "property temperature",
        )
    with (REPO_ROOT / properties[0]["data_path"]).open(
        newline="", encoding="utf-8"
    ) as handle:
        inventory = Counter(
            (
                row["property"],
                "loaded" if row["co2_loading_mol_per_mol_mea"] else "unloaded",
                row["uncertainty_value"],
                row["uncertainty_unit"],
                row["uncertainty_type"],
            )
            for row in csv.DictReader(handle)
        )
    expected = Counter(
        {
            ("density", "unloaded", "0.0005", "g/cm^3", "combined_absolute"): 35,
            ("density", "loaded", "0.002", "g/cm^3", "combined_absolute"): 68,
            ("dynamic_viscosity", "unloaded", "1", "percent", "combined_relative"): 35,
            ("dynamic_viscosity", "loaded", "3", "percent", "combined_relative"): 75,
        }
    )
    if inventory != expected:
        raise ValueError("Retained property uncertainty inventory drifted")

    observation_ids = "Putta2016_fit_corpus_summary Putta2016_external_AARD_table transport_numeric_candidates".split()
    observations = _rows(
        payload["observations"], observation_ids, "observation_id", ROW_FIELDS
    )
    for row, unit in zip(
        observations,
        ("wetted-wall-column rate points", "percent", "m^2 s^-1"),
        strict=True,
    ):
        if (
            row["unit"] != unit
            or row["uncertainty_status"] != "not_reported"
            or not isinstance(row["domain"], dict)
            or not row["domain"]
            or not row["reason"]
        ):
            raise ValueError("Observation metadata drifted")
    fit = _keys(
        observations[0]["domain"],
        _fields(
            "temperature_k mea_molarity_mol_l loading log_mean_pressure_difference_kpa"
        ),
        "fit-corpus domain",
    )
    for interval in fit.values():
        _interval(interval, "fit-corpus domain")
    aard = observations[1]
    rows_valid = (
        isinstance(aard["rows"], list)
        and len(aard["rows"]) == 5
        and all(
            set(row) == {"model", "aard_percent"}
            and row["model"]
            and isinstance(row["aard_percent"], list)
            and len(row["aard_percent"]) == 4
            for row in aard["rows"]
        )
    )
    domain = {
        "comparison_data_sets": aard["column_order"],
        "raw_state_rows": "unavailable_not_reconstructed",
    }
    if (
        aard["metric"] != "AARD percent as defined by the source"
        or aard["domain"] != domain
        or not rows_valid
    ):
        raise ValueError("AARD metadata drifted")
    if (
        observations[2]["admitted"] != []
        or observations[2]["rejected"] != transport_ids
    ):
        raise ValueError("Transport observation disposition drifted")


def _validate_sources(payload: dict[str, Any]) -> None:
    pdf = _fields(
        "source_id doi availability_status zotero_parent_key zotero_attachment_key local_pdf_sha256 locators"
    )
    shapes = {source_id: pdf for source_id in ("Putta2016", "Putta2017", "Gaspar2015")}
    shapes["Amundsen2009"] = _fields(
        "source_id doi availability_status zotero_parent_key zotero_attachment_key repo_markdown_path repo_markdown_sha256 locators"
    )
    gap = _fields("source_id doi availability_status locators coefficients reason")
    shapes.update({"Luo2015": gap, "PachecoRochelle1998": gap})
    sources = _rows(payload["source_records"], list(SOURCE_DOIS), "source_id", shapes)
    for row in sources:
        source_id = row["source_id"]
        if row["doi"] != SOURCE_DOIS[source_id]:
            raise ValueError("Source DOI drifted")
        if source_id in {"Luo2015", "PachecoRochelle1998"}:
            valid = (
                row["availability_status"] == "unavailable_not_adjudicated"
                and row["locators"] is None
                and row["coefficients"] is None
                and bool(row["reason"])
            )
        else:
            valid = row["availability_status"] == "available_adjudicated" and bool(
                row["locators"]
            )
        if not valid:
            raise ValueError("Source availability or gap disposition drifted")
    referenced = {
        row["source_record_id"]
        for key in ("finite_reactions", "transport_inputs", "property_inputs")
        for row in payload[key]
    }
    referenced.update(
        row["source_record_id"]
        for row in payload["observations"]
        if "source_record_id" in row
    )
    referenced.update(payload["observations"][2]["source_record_ids"])
    if referenced - set(SOURCE_DOIS):
        raise ValueError("A referenced source record is missing")


def validate_film_chemistry_inputs() -> dict[str, Any]:
    payload, schema, receipt = (
        _load(INPUT_PATH),
        _load(SCHEMA_PATH),
        _load(RECEIPT_PATH),
    )
    source_contract = _load(REACTION_CONTRACT_PATH)
    hashes = _validate_schema_receipt(payload, schema, receipt)
    if payload["common_application_domain"] != COMMON_DOMAIN:
        raise ValueError("Common application domain drifted")
    balances = _validate_reactions(payload, source_contract)
    evaluation_count = _validate_correlations(payload)
    _validate_evidence(payload)
    _validate_sources(payload)
    conversion = _keys(
        payload["source_standard_conversion"],
        _fields(
            "identity source_contract source_contract_sha256 common_source_identity source_relation algebraic_identity provider_activity_correction_ran status blocker"
        ),
        "source-standard conversion",
    )
    provider = source_contract["provider_transform"]
    if (
        conversion["source_contract_sha256"] != _sha256(REACTION_CONTRACT_PATH)
        or conversion["provider_activity_correction_ran"] is not False
        or conversion["status"] != "algebraic_identity_only"
        or conversion["identity"] != provider["identity"]
        or conversion["algebraic_identity"]
        != provider["deterministic_payload"]["transformed_vector_definition"]
    ):
        raise ValueError("Source-standard conversion drifted")
    exclusions = _keys(
        payload["exclusions"],
        {"column_fitted_quantities", "explicit", "scope_boundary"},
        "exclusions",
    )
    if (
        exclusions["column_fitted_quantities"] != []
        or set(exclusions["explicit"]) != EXCLUSIONS
    ):
        raise ValueError("Explicit exclusions drifted")
    return {
        "status": "pass",
        "input_identity": payload["identity"],
        "input_sha256": hashes["1/input.json"],
        "schema_sha256": hashes["1/schema.json"],
        "checks": [
            "schema_structure_and_receipt_hashes",
            "common_application_domain_and_guards",
            "species_reaction_order_classification_and_source_hash",
            "source_basis_projection_element_charge_direction_and_uncertainty",
            "correlation_evaluation_transcription_and_dimensional_rejection",
            "transport_fail_closed",
            "property_provenance_domain_and_uncertainty",
            "observation_metadata",
            "source_gap_disposition_and_reference_coverage",
            "algebraic_conversion_without_provider_evaluation",
            "explicit_exclusions_and_no_column_fit",
        ],
        "finite_reaction_count": 3,
        "correlation_evaluation_anchor_count": evaluation_count,
        "common_application_domain": payload["common_application_domain"],
        "net_carbamate_balance": balances["F1"],
        "admitted_fast_equilibrium_reactions": [],
        "admitted_numeric_transport_inputs": [],
        "admitted_property_inputs": [
            row["input_id"] for row in payload["property_inputs"]
        ],
        "provider_activity_correction_ran": False,
        "limitations": [
            "Published kinetic coefficient units are dimensionally inconsistent with the published rate unit.",
            "Source-complete CO2, free-MEA, and ionic diffusivity coefficients are unavailable.",
            "Luo2015 and PachecoRochelle1998 remain unavailable and not adjudicated at locator level.",
            "No active MEA parameter packet exists; Work Package B remains blocked by ePC-SAFT Issue #80.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    rendered = (
        json.dumps(validate_film_chemistry_inputs(), indent=2, sort_keys=True) + "\n"
    )
    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
