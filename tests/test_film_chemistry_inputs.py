from __future__ import annotations

import hashlib
import json
import math
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import MEA.common.film_chemistry_inputs as contract


def _sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    input_path = tmp_path / "input.json"
    schema_path = tmp_path / "schema.json"
    receipt_path = tmp_path / "receipt.json"
    source_contract_path = tmp_path / "source_contract.json"
    for source, target in (
        (contract.INPUT_PATH, input_path),
        (contract.SCHEMA_PATH, schema_path),
        (contract.RECEIPT_PATH, receipt_path),
        (contract.REACTION_CONTRACT_PATH, source_contract_path),
    ):
        shutil.copyfile(source, target)
    monkeypatch.setattr(contract, "INPUT_PATH", input_path)
    monkeypatch.setattr(contract, "SCHEMA_PATH", schema_path)
    monkeypatch.setattr(contract, "RECEIPT_PATH", receipt_path)
    monkeypatch.setattr(contract, "REACTION_CONTRACT_PATH", source_contract_path)
    return input_path, receipt_path


def _mutate(
    input_path: Path,
    receipt_path: Path,
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    mutation(payload)
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["files"]["1/input.json"] = hashlib.sha256(
        input_path.read_bytes()
    ).hexdigest()
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")


def test_work_package_a_inputs_fail_closed_and_conserve_balances() -> None:
    report = contract.validate_film_chemistry_inputs()
    assert report["status"] == "pass"
    assert report["net_carbamate_balance"] == {
        "C": 0,
        "H": 0,
        "N": 0,
        "O": 0,
        "charge": 0,
    }
    assert report["admitted_fast_equilibrium_reactions"] == []
    assert report["admitted_numeric_transport_inputs"] == []
    assert report["provider_activity_correction_ran"] is False
    contract.validate_application_state(293.15, 1.0, 0.0)
    contract.validate_application_state(323.15, 5.0, 0.499)


@pytest.mark.parametrize(
    ("temperature_k", "mea_molarity", "loading"),
    [(293.14, 1.0, 0.0), (323.16, 5.0, 0.0), (313.15, 3.0, 0.0), (313.15, 1.0, 0.5)],
)
def test_common_application_domain_rejects_unsupported_states(
    temperature_k: float, mea_molarity: float, loading: float
) -> None:
    with pytest.raises(ValueError):
        contract.validate_application_state(temperature_k, mea_molarity, loading)


def test_empty_required_collection_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path, receipt_path, lambda payload: payload["finite_reactions"].clear()
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize("case", ["unit", "domain", "order"])
def test_malformed_unit_domain_or_order_is_rejected(
    case: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)

    def mutate(payload: dict[str, Any]) -> None:
        if case == "unit":
            payload["finite_reactions"][0]["rate_unit"] = ""
        elif case == "domain":
            payload["property_inputs"][0]["domain"]["temperature_k"] = [353.15, 298.15]
        else:
            payload["species_order"].reverse()

    _mutate(input_path, receipt_path, mutate)
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize("case", ["identity", "hash"])
def test_receipt_tampering_or_hash_drift_is_rejected(
    case: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if case == "identity":
        receipt["identity"] = "tampered"
    else:
        receipt["files"]["1/input.json"] = "0" * 64
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


def test_admission_classification_drift_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["film_classification"][1].update(
            admission_status="rejected"
        ),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


def test_finite_reaction_domain_drift_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["finite_reactions"][0]["domain"].pop("temperature_k"),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


def test_source_contract_path_drift_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["source_standard_conversion"].update(
            source_contract="wrong/path.json"
        ),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("equation", "wrong"),
        ("rate_equation", "wrong"),
        ("forward_direction", "CO2 consumption"),
        ("reverse_direction", "CO2 release"),
    ],
)
def test_finite_reaction_semantic_text_drift_is_rejected(
    field: str, value: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["finite_reactions"][0].update({field: value}),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


def test_correlation_reaction_mapping_drift_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["kinetic_correlations"][0].update(reaction_id="F2"),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize(
    "field",
    [
        "provider_transform_identity",
        "common_source_identity",
        "source_relation",
        "source_contract_identity",
    ],
)
def test_conversion_identity_drift_is_rejected(
    field: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["source_standard_conversion"].update({field: "wrong"}),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


def test_loaded_source_contract_identity_drift_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sandbox(tmp_path, monkeypatch)
    payload = json.loads(contract.REACTION_CONTRACT_PATH.read_text(encoding="utf-8"))
    payload["identity"] = "wrong"
    contract.REACTION_CONTRACT_PATH.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="source contract identity"):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_record_id", "Putta2017"),
        ("source_locator", ""),
        ("source_locator", "wrong"),
    ],
)
def test_finite_reaction_provenance_drift_is_rejected(
    field: str, value: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["finite_reactions"][0].update({field: value}),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize("field", ["A", "B_k"])
def test_correlation_coefficients_cannot_drift_with_refreshed_anchors(
    field: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)

    def mutate(payload: dict[str, Any]) -> None:
        row = payload["kinetic_correlations"][0]
        row[field] += 1.0
        for anchor in row["evaluation_anchors"]:
            anchor["expected"] = row["A"] * math.exp(
                -row["B_k"] / anchor["temperature_k"]
            )

    _mutate(input_path, receipt_path, mutate)
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize(
    "field",
    ["source_reported_unit", "dimensionally_required_unit", "temperature_domain_k"],
)
def test_correlation_unit_or_domain_drift_is_rejected(
    field: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["kinetic_correlations"][0].update(
            {field: [293.15, 323.15] if field == "temperature_domain_k" else "wrong"}
        ),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize("field", ["source_record_id", "source_locator"])
def test_correlation_source_linkage_drift_is_rejected(
    field: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)
    _mutate(
        input_path,
        receipt_path,
        lambda payload: payload["kinetic_correlations"][0].update({field: "wrong"}),
    )
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize(
    "case", ["domain", "species", "candidate_identity", "source_id", "source_locator"]
)
def test_coordinated_transport_provenance_drift_is_rejected(
    case: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)

    def mutate(payload: dict[str, Any]) -> None:
        row = payload["transport_inputs"][0]
        if case == "domain":
            row["domains"][0]["temperature_k"] = [303.15, 323.15]
        elif case == "species":
            row["species"] = ["MEA"]
        elif case == "candidate_identity":
            row["candidate_identities"][0] = "wrong"
        elif case == "source_id":
            row["source_record_id"] = "Putta2016"
        else:
            row["source_locator"] = "wrong"

    _mutate(input_path, receipt_path, mutate)
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


@pytest.mark.parametrize(
    "case",
    [
        "source_pdf_hash",
        "source_zotero_key",
        "source_markdown_hash",
        "observation_kind",
        "observation_source_locator",
    ],
)
def test_coordinated_source_or_observation_drift_is_rejected(
    case: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path, receipt_path = _sandbox(tmp_path, monkeypatch)

    def mutate(payload: dict[str, Any]) -> None:
        if case == "source_pdf_hash":
            payload["source_records"][0]["local_pdf_sha256"] = "0" * 64
        elif case == "source_zotero_key":
            payload["source_records"][0]["zotero_parent_key"] = "WRONG"
        elif case == "source_markdown_hash":
            payload["source_records"][3]["repo_markdown_sha256"] = "0" * 64
        elif case == "observation_kind":
            payload["observations"][0]["kind"] = "wrong"
        else:
            payload["observations"][0]["source_locator"] = "wrong"

    _mutate(input_path, receipt_path, mutate)
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()


def test_coordinated_nested_schema_drift_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, receipt_path = _sandbox(tmp_path, monkeypatch)
    schema = json.loads(contract.SCHEMA_PATH.read_text(encoding="utf-8"))
    schema["$defs"]["kinetic_correlation"]["required"].remove("source_locator")
    contract.SCHEMA_PATH.write_text(json.dumps(schema), encoding="utf-8")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["files"]["1/schema.json"] = hashlib.sha256(
        contract.SCHEMA_PATH.read_bytes()
    ).hexdigest()
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError):
        contract.validate_film_chemistry_inputs()
