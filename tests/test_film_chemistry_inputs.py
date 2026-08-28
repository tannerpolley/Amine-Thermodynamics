from __future__ import annotations

import hashlib
import json
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
    for source, target in (
        (contract.INPUT_PATH, input_path),
        (contract.SCHEMA_PATH, schema_path),
        (contract.RECEIPT_PATH, receipt_path),
    ):
        shutil.copyfile(source, target)
    monkeypatch.setattr(contract, "INPUT_PATH", input_path)
    monkeypatch.setattr(contract, "SCHEMA_PATH", schema_path)
    monkeypatch.setattr(contract, "RECEIPT_PATH", receipt_path)
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
