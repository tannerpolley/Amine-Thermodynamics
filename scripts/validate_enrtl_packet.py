from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "data/reference/MEA/enrtl_packet"
RECEIPT = ROOT / "data/reference/MEA/enrtl_packet_adoption_receipt.json"

EXPECTED_MODEL_IDENTITY = "mea-enrtl-six-parameter-corrected-dh-v1"
EXPECTED_SPECIES_ORDER = ["H2O", "MEA", "CO2", "MEAH^+", "MEACOO^-", "HCO3^-"]
EXPECTED_REACTION_ORDER = [
    "MEA_carbamate_formation_combo",
    "MEA_bicarbonate_formation_combo",
]
EXPECTED_PARAMETER_ORDER = [
    "params.reaction_MEA_bicarbonate_formation_combo.log_k_ref",
    "params.reaction_MEA_bicarbonate_formation_combo.dh_rxn_ref",
    "params.reaction_MEA_bicarbonate_formation_combo.dcp_rxn",
    "params.reaction_MEA_carbamate_formation_combo.log_k_ref",
    "params.reaction_MEA_carbamate_formation_combo.dh_rxn_ref",
    "params.reaction_MEA_carbamate_formation_combo.dcp_rxn",
]
EXPECTED_BASES = {
    "enthalpy_phase_basis": "apparent",
    "property_basis": "true",
    "reaction_activities": "true-species activity",
    "state_components": "apparent",
}
EXPECTED_REFERENCE_STATE = {
    "phase": "Liq",
    "reference_component": "H2O",
    "type": "InfiniteDilutionSingleSolvent",
}
EXPECTED_REFERENCE_TEMPERATURE = {"unit": "K", "value": 353.15}
EXPECTED_INTERACTION_DEFAULTS = {
    "alpha": {
        "all_other": {"unit": "dimensionless", "value": 0.2},
        "molecule_molecule": {"unit": "dimensionless", "value": 0.3},
        "symmetry": "symmetric",
    },
    "tau_A": {"unit": "dimensionless", "value": 0},
    "tau_B": {"unit": "K", "value": 0},
}
EXPECTED_SOLVER = {
    "execution_route": "IDAES",
    "executable_sha256": "8f8711b709b5f265ff7cb8b352c037bb999d88628384be8390f26530f08de94e",
    "name": "IPOPT",
    "version": "3.13.2",
}
EXPECTED_DOMAINS = {
    "Kim_2014_comparison": {"role": "selection-exposed comparison", "temperature_C": [40.0, 120.0]},
    "calibration_VLE": {
        "amine_weight_fraction": "source rows; no extrapolation claim",
        "loading": "0.1 < CO2_loading < 0.6",
        "temperature_C": [0.0, 120.0],
    },
    "calibration_calorimetry": {
        "loading": "source rows",
        "role": "fit",
        "source": "Kim and Svendsen 2007",
        "temperature_C": [40.0, 80.0],
    },
    "calibration_speciation": {
        "amine_weight_fraction": "source rows",
        "species_basis": "true-species mole fraction",
        "temperature_C": [20.0, 20.0],
    },
    "temperature_holdout_calorimetry": {
        "role": "temperature holdout; not fitted",
        "source": "Kim and Svendsen 2007",
        "temperature_C": [120.0, 120.0],
    },
}
EXPECTED_RESULT_IDENTITIES = {
    "baseline": "baseline-six-parameter-physical-reaction-coordinates",
    "candidate_selection": "none",
    "comparison": "historical-coordinate-sensitivity",
}
EXPECTED_UNAVAILABLE = [
    ("total_reacting_solution_heat_capacity", "unavailable"),
    ("transport_properties", "unavailable"),
    ("process_model_execution", "unavailable"),
]
EXPECTED_OBSERVATION_COUNTS = {"vle": 240, "speciation": 172, "calorimetry_fit": 66}


def _json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid packet JSON: {path}") from error


def _finite(value, location="value"):
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)) and not math.isfinite(value):
        raise ValueError(f"non-finite packet value at {location}")
    if isinstance(value, dict):
        for key, item in value.items():
            _finite(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _finite(item, f"{location}[{index}]")


def _require_equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label} mismatch")


def _validate_contract(receipt_data, manifest, payload):
    _require_equal(receipt_data.get("schema_version"), 1, "receipt schema")
    _require_equal(receipt_data.get("identity"), "mea-enrtl-packet-adoption-receipt-v1", "receipt identity")
    if not isinstance(receipt_data.get("source_commit"), str) or not receipt_data["source_commit"]:
        raise ValueError("receipt source commit is missing")
    _require_equal(
        receipt_data.get("adoption_role"),
        "comparison/adoption record only; no production eNRTL runtime",
        "adoption role",
    )
    model = manifest.get("model")
    if not isinstance(model, dict):
        raise ValueError("model contract is missing")
    _require_equal(manifest.get("identity"), "mea-enrtl-corrected-fit-manifest-v1", "manifest identity")
    _require_equal(manifest.get("schema_version"), 1, "manifest schema")
    _require_equal(payload.get("schema_version"), 1, "payload schema")
    _require_equal(payload.get("identity"), manifest.get("payload_identity"), "payload identity")
    _require_equal(model.get("identity"), EXPECTED_MODEL_IDENTITY, "model identity")
    _require_equal(model.get("species_order"), EXPECTED_SPECIES_ORDER, "species order")
    _require_equal(model.get("reaction_order"), EXPECTED_REACTION_ORDER, "reaction order")
    _require_equal(model.get("parameter_order"), EXPECTED_PARAMETER_ORDER, "parameter order")
    _require_equal(model.get("bases"), EXPECTED_BASES, "bases")
    _require_equal(model.get("reference_state"), EXPECTED_REFERENCE_STATE, "reference state")
    _require_equal(model.get("reference_temperature"), EXPECTED_REFERENCE_TEMPERATURE, "reference temperature")
    _require_equal(model.get("interaction_defaults"), EXPECTED_INTERACTION_DEFAULTS, "interaction defaults")
    _require_equal(manifest.get("dependencies", {}).get("solver"), EXPECTED_SOLVER, "solver identity")
    _require_equal(manifest.get("property_domains"), EXPECTED_DOMAINS, "property domains")
    _require_equal(manifest.get("result_identities"), EXPECTED_RESULT_IDENTITIES, "result identities")
    unavailable = [
        (item.get("property"), item.get("status"))
        for item in manifest.get("unavailable_properties", [])
        if isinstance(item, dict)
    ]
    _require_equal(unavailable, EXPECTED_UNAVAILABLE, "unavailable properties")
    _require_equal(payload.get("model_identity"), EXPECTED_MODEL_IDENTITY, "payload model identity")
    _require_equal(payload.get("baseline_identity"), EXPECTED_RESULT_IDENTITIES["baseline"], "payload baseline identity")
    _require_equal(payload.get("fit", {}).get("observation_counts"), EXPECTED_OBSERVATION_COUNTS, "observation counts")
    _require_equal(
        [item.get("id") for item in payload.get("parameters", [])],
        EXPECTED_PARAMETER_ORDER,
        "payload parameter identities",
    )
    required_numbers = [("payload.fit.objective", payload.get("fit", {}).get("objective"))]
    required_numbers.extend(
        (f"payload.parameters[{index}].value", item.get("value"))
        for index, item in enumerate(payload.get("parameters", []))
    )
    for location, value in required_numbers:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"required finite number missing at {location}")


def validate_packet(packet_dir: Path = PACKET_DIR, receipt: Path = RECEIPT):
    packet_dir = Path(packet_dir)
    receipt_data = _json(Path(receipt))
    manifest_path = packet_dir / "manifest.json"
    payload_path = packet_dir / "payload.json"
    manifest = _json(manifest_path)
    payload = _json(payload_path)
    expected = receipt_data["files"]
    for name, path in (("manifest.json", manifest_path), ("payload.json", payload_path)):
        item = expected[name]
        if not path.is_file() or path.stat().st_size != item["bytes"]:
            raise ValueError(f"adopted packet file size mismatch: {name}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            raise ValueError(f"adopted packet file hash mismatch: {name}")
    if receipt_data["manifest_sha256_external"] != expected["manifest.json"]["sha256"]:
        raise ValueError("external manifest digest mismatch")
    _validate_contract(receipt_data, manifest, payload)
    listed_payload = next(
        (item for item in manifest.get("files", []) if item.get("path") == "payload.json"),
        None,
    )
    if listed_payload is None or listed_payload["sha256"] != expected["payload.json"]["sha256"]:
        raise ValueError("manifest payload inventory mismatch")
    _finite(receipt_data, "receipt")
    _finite(manifest, "manifest")
    _finite(payload, "payload")
    return manifest, payload


def load_packet(
    *,
    packet_dir: Path = PACKET_DIR,
    receipt: Path = RECEIPT,
    expected_model: str | None = None,
    expected_species_order: list[str] | None = None,
    expected_reaction_order: list[str] | None = None,
    expected_property_basis: str | None = None,
    expected_domain: str | None = None,
    result_identity: str | None = None,
    requested_property: str | None = None,
):
    manifest, payload = validate_packet(packet_dir, receipt)
    model = manifest["model"]
    if expected_model is not None and expected_model != model["identity"]:
        raise ValueError("unsupported requested model")
    if expected_species_order is not None and expected_species_order != model["species_order"]:
        raise ValueError("species order mismatch")
    if expected_reaction_order is not None and expected_reaction_order != model["reaction_order"]:
        raise ValueError("reaction order mismatch")
    if expected_property_basis is not None and expected_property_basis != model["bases"]["property_basis"]:
        raise ValueError("basis mismatch")
    if expected_domain is not None and expected_domain not in manifest["property_domains"]:
        raise ValueError("unsupported property domain")
    if result_identity is not None and result_identity not in manifest["result_identities"].values():
        raise ValueError("baseline/comparison identity mismatch")
    if requested_property is not None:
        unavailable = {item["property"] for item in manifest["unavailable_properties"]}
        if requested_property in unavailable:
            raise ValueError(f"unavailable property: {requested_property}")
    return payload


if __name__ == "__main__":
    validate_packet()
    print("MEA eNRTL packet validation passed")
