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
PRESSURE_FIRST = (
    ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first/results"
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def test_pressure_first_diagnostic_keeps_observed_pressure_as_input() -> None:
    packet_receipt = _assert_self_hash(PRESSURE_FIRST / "pressure_packet_receipt.json")
    packet_path = PRESSURE_FIRST / "pressure_candidate_packet.csv"
    with packet_path.open(newline="") as handle:
        packet = list(csv.DictReader(handle))
    assert len(packet) == 121
    assert len({row["canonical_row_identity"] for row in packet}) == 121
    assert packet_receipt["packet"]["sha256"] == _sha256(packet_path)
    assert Counter(row["analysis_role"] for row in packet) == {
        "training": 30,
        "model_selection": 6,
        "reserved": 8,
        "non_scoring_domain_challenge": 77,
    }
    assert all(row["promotion_eligibility"] == "no" for row in packet)

    fit_timeout = _assert_self_hash(
        PRESSURE_FIRST / "fixed_pressure_fugacity_screen_timeout.json"
    )
    assert fit_timeout["result_status"] == (
        "no_FitResult_no_accepted_start_no_fitted_parameter"
    )
    assert fit_timeout["declared_starts"] == [
        "kij-zero",
        "kij-negative",
        "kij-positive",
    ]

    with (PRESSURE_FIRST / "fixed_pressure_fugacity_screen_predictions.csv").open(
        newline=""
    ) as handle:
        predictions = list(csv.DictReader(handle))
    evaluation = _assert_self_hash(
        PRESSURE_FIRST / "fixed_pressure_fugacity_screen_evaluation_receipt.json"
    )
    assert len(predictions) == 1
    assert evaluation["prediction_table_sha256"] == _sha256(
        PRESSURE_FIRST / "fixed_pressure_fugacity_screen_predictions.csv"
    )
    assert {row["modeled_quantity"] for row in predictions} == {
        "liquid_CO2_fugacity_at_observed_T_and_total_P"
    }
    assert {row["pressure_prediction_status"] for row in predictions} == {
        "not_computed_observed_pressure_is_input"
    }
    assert {row["claim_status"] for row in predictions} == {
        "diagnostic_non_promotable"
    }

    timeout = _assert_self_hash(PRESSURE_FIRST / "coupled_timeout_evidence.json")
    assert timeout["termination"] == "owner_bounded_interrupt_no_result"
    assert timeout["elapsed_seconds"] == 1022.08
    decision = _assert_self_hash(
        PRESSURE_FIRST / "pressure_first_scientific_decision.json"
    )
    assert decision["promotion_decision"] == "not_promoted"
    assert decision["diagnostic_evaluation"]["predicted_pco2_available"] is False
    assert decision["nonlinear_diagnostic_fit"]["status"] == "timed_out_no_FitResult"
    assert decision["manuscript_changed"] is False

    with (
        PRESSURE_FIRST / "figures/pco2_closure_diagnostic_plot_data.csv"
    ).open(newline="") as handle:
        plotted = list(csv.DictReader(handle))
    assert len(plotted) == 113
    assert "reserved" not in {row["analysis_role"] for row in plotted}
    assert {row["model_curve_status"] for row in plotted} == {
        "not_available_coupled_pressure_closure_timed_out"
    }
    assert sum(bool(row["modeled_liquid_co2_fugacity_pa"]) for row in plotted) == 1
