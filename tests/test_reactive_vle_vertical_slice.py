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
        "M0",
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
    ]
    assert all(model["promotion_eligible"] is False for model in models)


def test_installed_tracers_and_campaign_receipt_are_immutable() -> None:
    homogeneous = _assert_self_hash(
        RESULTS / "installed_homogeneous_tracer_receipt.json"
    )
    bubble = _assert_self_hash(
        RESULTS / "installed_reactive_bubble_tracer_receipt.json"
    )
    campaign = _assert_self_hash(RESULTS / "campaign_admission_receipt.json")

    assert homogeneous["status"] == "evaluated"
    assert campaign["input_packet"]["executable_row_count"] == 0
    execution = campaign["installed_execution_evidence"]
    assert (
        execution["homogeneous_reactive_observation"]["receipt_sha256"]
        == (homogeneous["receipt_sha256"])
    )
    assert (
        execution["reactive_bubble_vle"]["receipt_sha256"] == bubble["receipt_sha256"]
    )
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
    assert packet_receipt["preregistration_sha256"] == _sha256(
        PRESSURE_FIRST.parent / "config/preregistration.json"
    )
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
    assert {row["claim_status"] for row in predictions} == {"diagnostic_non_promotable"}

    timeout = _assert_self_hash(PRESSURE_FIRST / "coupled_timeout_evidence.json")
    assert timeout["termination"] == "owner_bounded_interrupt_no_result"
    assert timeout["elapsed_seconds"] == 1022.08
    decision = _assert_self_hash(
        PRESSURE_FIRST / "pressure_first_scientific_decision.json"
    )
    assert decision["promotion_decision"] == "not_promoted"
    assert decision["diagnostic_evaluation"]["predicted_pco2_available"] is False
    assert decision["nonlinear_diagnostic_fit"]["status"] == (
        "completed_exact_jacobian_fixed_pressure_screen"
    )
    assert decision["nonlinear_diagnostic_fit"]["attempted_starts"] == 3
    assert decision["nonlinear_diagnostic_fit"]["accepted_starts"] == 3
    assert decision["nonlinear_diagnostic_fit"]["optimizer_basin_count"] == 1
    assert decision["coupled_promotion_lane"]["status"] == (
        "six_exact_pressure_roots_completed_diagnostic_only"
    )
    assert decision["manuscript_changed"] is False

    bubble = _assert_self_hash(
        PRESSURE_FIRST / "reactive_bubble_pressure_diagnostic.json"
    )
    assert bubble["claim_status"] == ("diagnostic_non_promotable_exact_reactive_bubble")
    assert bubble["topology"] == {
        "phase_count": 2,
        "liquid": "one_certified_reacting_nine_species_branch",
        "vapor": "one_declared_incipient_three-neutral_nonideal_branch",
        "vapor_component_ids": [
            "carbon-dioxide",
            "monoethanolamine",
            "water",
        ],
        "phase_count_search": "not_performed",
        "liquid_branch_rediscovery": "not_performed",
    }
    assert bubble["metrics"]["input_rows"] == 6
    assert bubble["metrics"]["evaluated_rows"] == 6
    assert bubble["metrics"]["failed_rows"] == 0
    assert bubble["metrics"]["log10_rmse"] > 0.3
    assert all(result["search"]["attempted"] == 1 for result in bubble["results"])
    assert all(result["search"]["accepted"] == 1 for result in bubble["results"])
    assert all(
        result["search"]["distinct_branches"] == 1 for result in bubble["results"]
    )
    assert all(result["bubble_closure_abs"] < 2.0e-10 for result in bubble["results"])

    with (PRESSURE_FIRST / "figures/pco2_closure_diagnostic_plot_data.csv").open(
        newline=""
    ) as handle:
        plotted = list(csv.DictReader(handle))
    assert len(plotted) == 113
    assert "reserved" not in {row["analysis_role"] for row in plotted}
    assert {row["model_curve_status"] for row in plotted} == {
        "not_available_coupled_pressure_closure_timed_out"
    }
    assert sum(bool(row["modeled_liquid_co2_fugacity_pa"]) for row in plotted) == 1


def test_pressure_block_ladder_and_cai_binary_audit_fail_closed() -> None:
    cai_path = (
        ROOT
        / "data/reference/MEA/observations/vapor_liquid_equilibrium"
        / "Cai_1996_MEA_H2O_VLE.csv"
    )
    with cai_path.open(newline="") as handle:
        cai_rows = list(csv.DictReader(handle))
    assert len(cai_rows) == 29
    assert Counter(row["role"] for row in cai_rows) == {
        "binary_training": 12,
        "binary_model_selection": 13,
        "pure_endpoint_context": 4,
    }
    assert {row["source_sha256"] for row in cai_rows} == {
        "091edb997b7bddf3c791a0a2dff9ac03ade971a7f580f6b3ab7cbf85a305b70a"
    }

    binary = _assert_self_hash(PRESSURE_FIRST / "cai_mea_water_binary_fit.json")
    assert binary["accounting"]["source_rows"] == 29
    assert binary["accounting"]["admitted_training_rows"] == 3
    assert binary["accounting"]["admitted_model_selection_rows"] == 0
    assert binary["accounting"]["numeric_failure_penalties"] == 0
    assert binary["rank"] == 1
    assert binary["condition_number"] == 1.0
    assert binary["active_bounds"] == []
    assert binary["gates"]["all_starts_same_solution"] is True
    assert binary["gates"]["exact_jacobian_check"] is True
    assert binary["gates"]["training_normalized_rmse"] is False
    assert binary["gates"]["independent_pressure_level_validation"] is False
    assert binary["all_gates_pass"] is False
    assert binary["promotion_decision"] == "not_promoted"

    with (PRESSURE_FIRST / "cai_mea_water_binary_predictions.csv").open(
        newline=""
    ) as handle:
        binary_predictions = list(csv.DictReader(handle))
    assert len(binary_predictions) == 12
    assert {row["fit_role"] for row in binary_predictions} == {"binary_training"}
    assert {row["source_partition_role"] for row in binary_predictions} == {
        "binary_model_selection"
    }
    assert {row["parameter_state"] for row in binary_predictions} == {
        "retained_origin",
        "fitted_diagnostic",
    }
    assert {row["claim_status"] for row in binary_predictions} == {
        "diagnostic_non_promotable"
    }

    for model in ("3b2b", "3b4c"):
        source_fit = _assert_self_hash(
            PRESSURE_FIRST / f"cai_baygi_{model}_binary_fit.json"
        )
        assert source_fit["accounting"]["admitted_training_rows"] == 12
        assert source_fit["accounting"]["admitted_model_selection_rows"] == 13
        assert source_fit["accounting"]["numeric_failure_penalties"] == 0
        assert source_fit["rank"] == 1
        assert source_fit["condition_number"] == 1.0
        assert source_fit["active_bounds"] == []
        assert source_fit["gates"]["all_starts_same_solution"] is True
        assert source_fit["gates"]["exact_jacobian_check"] is True
        assert source_fit["gates"]["training_normalized_rmse"] is False
        assert source_fit["gates"]["model_selection_normalized_rmse"] is False
        assert source_fit["all_gates_pass"] is False
        assert source_fit["promotion_decision"] == "not_promoted"
        with (PRESSURE_FIRST / f"cai_baygi_{model}_binary_predictions.csv").open(
            newline=""
        ) as handle:
            source_predictions = list(csv.DictReader(handle))
        assert len(source_predictions) == 100
        assert {row["fit_role"] for row in source_predictions} == {
            "binary_training",
            "binary_model_selection",
        }
        assert {row["claim_status"] for row in source_predictions} == {
            "diagnostic_non_promotable"
        }

    decision = _assert_self_hash(PRESSURE_FIRST / "pressure_block_ladder_decision.json")
    assert len(decision["blocks"]) == 6
    assert decision["accounting"]["passed_blocks"] == 0
    assert decision["accounting"]["model_selection_rows_used"] == 0
    assert decision["accounting"]["reserved_rows_used"] == 0
    assert decision["independent_binary_audit"]["all_gates_pass"] is False
    assert decision["promotion_decision"] == "not_promoted"
    assert decision["manuscript_changed"] is False

    with (PRESSURE_FIRST / "figures/pressure_block_ladder_plot_data.csv").open(
        newline=""
    ) as handle:
        ladder_plot = list(csv.DictReader(handle))
    assert len(ladder_plot) == 12
    assert {row["prediction_status"] for row in ladder_plot} == {
        "exact_reactive_bubble_root"
    }
    assert {row["candidate_curves_plotted"] for row in ladder_plot} == {"False"}
    assert "reserved" not in {row["analysis_role"] for row in ladder_plot}

    with (
        PRESSURE_FIRST / "figures/cai_baygi_binary_model_comparison_plot_data.csv"
    ).open(newline="") as handle:
        binary_model_plot = list(csv.DictReader(handle))
    assert len(binary_model_plot) == 100
    assert {row["model"] for row in binary_model_plot} == {
        "Baygi 3B/2B",
        "Baygi 3B/4C",
    }
    assert {row["parameter_state"] for row in binary_model_plot} == {
        "fitted_diagnostic"
    }
