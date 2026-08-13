from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data/reference/MEA/manifests"
RESULTS = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/results/reactive_vle_vertical_slice"
)


def _canonical_sha256(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def _assert_self_hash(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text())
    claimed = payload.pop("receipt_sha256")
    assert claimed == _canonical_sha256(payload)
    payload["receipt_sha256"] = claimed
    return payload


def test_candidate_packet_and_nested_models_fail_closed() -> None:
    with (MANIFESTS / "reactive_vle_cross_validation.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert Counter(row["observable_family"] for row in rows) == {
        "pco2": 121,
        "speciation": 198,
    }
    assert {row["admission_status"] for row in rows} == {
        "candidate_not_executable"
    }
    assert all("residual_scale_missing" in row["admission_blockers"] for row in rows)
    assert all(
        "state_pressure_contract_missing" in row["admission_blockers"]
        for row in rows
        if row["observable_family"] == "speciation"
    )

    models = json.loads(
        (MANIFESTS / "reactive_vle_model_configurations.json").read_text()
    )["configurations"]
    assert [model["configuration_id"] for model in models] == [
        "M0",
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
    ]
    assert all(model["promotion_eligible"] is False for model in models)


def test_installed_tracers_and_campaign_receipt_are_immutable() -> None:
    homogeneous = _assert_self_hash(RESULTS / "installed_homogeneous_tracer_receipt.json")
    bubble = _assert_self_hash(RESULTS / "installed_reactive_bubble_tracer_receipt.json")
    campaign = _assert_self_hash(RESULTS / "campaign_admission_receipt.json")

    assert homogeneous["status"] == "evaluated"
    assert campaign["input_packet"]["executable_row_count"] == 0
    execution = campaign["installed_execution_evidence"]
    assert execution["homogeneous_reactive_observation"]["receipt_sha256"] == (
        homogeneous["receipt_sha256"]
    )
    assert execution["reactive_bubble_vle"]["receipt_sha256"] == bubble[
        "receipt_sha256"
    ]
    assert campaign["promotion_decision"]["status"] == "not_promoted"
    assert campaign["promotion_decision"]["manuscript_changed"] is False
