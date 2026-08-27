from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data/reference/MEA/manifests"
TRACERS = (
    ROOT
    / "analyses/reactive_epcsaft_parameter_evidence/results/reactive_vle_vertical_slice"
)
PRESSURE = ROOT / "analyses/reactive_epcsaft_parameter_evidence/pressure_first/results"
CO2_WATER = (
    ROOT
    / "analyses/reactive_epcsaft_parameter_evidence/co2_water_induced_association/results"
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


def _self_hashed(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text())
    claimed = payload.pop("receipt_sha256")
    assert claimed == _canonical_sha256(payload)
    payload["receipt_sha256"] = claimed
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_candidate_inventory_and_retained_model_family_fail_closed() -> None:
    with (MANIFESTS / "reactive_vle_cross_validation.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert Counter(row["observable_family"] for row in rows) == {
        "pco2": 121,
        "speciation": 198,
    }
    assert {row["admission_status"] for row in rows} == {"candidate_not_executable"}
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
        "SHELL_BORN_SOLVENT_ONLY_INDUCED",
        "SHELL_BORN_ION_SUPPRESSED_INDUCED",
    ]
    assert {model["association"] for model in models} == {
        "Schick-Pabsch reciprocal CO2-water 2B topology"
    }
    assert all(model["promotion_eligible"] is False for model in models)


def test_installed_engine_tracers_bind_the_campaign() -> None:
    homogeneous = _self_hashed(TRACERS / "installed_homogeneous_tracer_receipt.json")
    bubble = _self_hashed(TRACERS / "installed_reactive_bubble_tracer_receipt.json")
    campaign = _self_hashed(TRACERS / "campaign_admission_receipt.json")
    execution = campaign["installed_execution_evidence"]
    assert homogeneous["status"] == "evaluated"
    assert (
        execution["homogeneous_reactive_observation"]["receipt_sha256"]
        == (homogeneous["receipt_sha256"])
    )
    assert (
        execution["reactive_bubble_vle"]["receipt_sha256"] == bubble["receipt_sha256"]
    )
    assert campaign["promotion_decision"]["status"] == "not_promoted"
    assert campaign["promotion_decision"]["fitted_parameters"] == []
    assert campaign["promotion_decision"]["manuscript_changed"] is False


def test_pressure_packet_is_immutable_and_leakage_grouped() -> None:
    packet_path = PRESSURE / "pressure_candidate_packet.csv"
    receipt = _self_hashed(PRESSURE / "pressure_packet_receipt.json")
    with packet_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len({row["canonical_row_identity"] for row in rows}) == 121
    assert receipt["packet"]["sha256"] == _sha256(packet_path)
    assert Counter(row["analysis_role"] for row in rows) == {
        "training": 30,
        "model_selection": 6,
        "reserved": 8,
        "non_scoring_domain_challenge": 77,
    }
    roles_by_group: dict[str, set[str]] = {}
    for row in rows:
        roles_by_group.setdefault(row["covariance_or_leakage_group"], set()).add(
            row["analysis_role"]
        )
    assert all(len(roles) == 1 for roles in roles_by_group.values())
    assert all(row["promotion_eligibility"] == "no" for row in rows)


def test_retained_neutral_binary_evidence_is_complete() -> None:
    for model in ("2b", "3b", "4c"):
        fit_path = PRESSURE / f"cai_held_water_mea_{model}_fit.json"
        fit = _self_hashed(fit_path)
        assert fit["accounting"]["admitted_training_rows"] == 12
        assert fit["accounting"]["admitted_model_selection_rows"] == 13
        assert fit["accounting"]["numeric_failure_penalties"] == 0
        assert fit["rank"] == 1
        assert fit["condition_number"] == 1.0
        assert fit["active_bounds"] == []
        assert fit["gates"]["all_starts_same_solution"] is True
        assert fit["gates"]["exact_jacobian_check"] is True
        assert fit["all_gates_pass"] is False
        assert fit["promotion_decision"] == "not_promoted"

    with (PRESSURE / "figures/cai_held_water_mea_family_plot_data.csv").open(
        newline=""
    ) as handle:
        binary_rows = list(csv.DictReader(handle))
    assert len(binary_rows) == 150
    assert {row["model"] for row in binary_rows} == {
        "Held water + 2B MEA",
        "Held water + 3B MEA",
        "Held water + 4C MEA",
    }
    assert {row["parameter_state"] for row in binary_rows} == {"fitted_diagnostic"}

    co2_summary = json.loads((CO2_WATER / "summary.json").read_text())
    assert co2_summary["row_count"] == 39
    assert co2_summary["log_pressure_rmse"] < 0.22
    assert co2_summary["median_multiplicative_error"] < 1.18
    assert co2_summary["maximum_pressure_residual_inf"] < 1.0e-8
    assert co2_summary["maximum_chemical_potential_residual_inf"] < 2.0e-8
