from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
RESULTS = ANALYSIS / "results"
PACKET = RESULTS / "pressure_candidate_packet.csv"
PREDICTIONS = RESULTS / "fixed_pressure_fugacity_screen_predictions.csv"
COUPLED_TIMEOUT = RESULTS / "coupled_timeout_evidence.json"
FIT_TIMEOUT = RESULTS / "fixed_pressure_fugacity_screen_timeout.json"
ENGINE_RECEIPT = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/results/reactive_vle_vertical_slice"
    / "installed_homogeneous_tracer_receipt.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def _write_parameter_table(prediction: pd.Series) -> None:
    value = float(prediction["evaluated_kij_co2_water"])
    fugacity = float(prediction["modeled_liquid_co2_fugacity_pa"])
    derivative = float(prediction["exact_d_fugacity_d_kij_pa"])
    observed = float(prediction["observed_pco2_pa"])
    local_correction = -math.log(fugacity / observed) / (derivative / fugacity)
    pd.DataFrame(
        [
            {
                "parameter_identity": "pair/carbon-dioxide/water/k_ij",
                "unit": "dimensionless",
                "coordinate_transform": "physical = origin + scale * affine",
                "origin": 0.0,
                "scale": 0.05,
                "lower_bound": -0.2,
                "upper_bound": 0.2,
                "evaluated_value": value,
                "local_linear_zero_residual_correction": local_correction,
                "local_linear_candidate": value + local_correction,
                "candidate_status": "unvalidated_single_row_local_sensitivity_not_fit",
                "fitted_value": None,
                "promotion_status": "not_promotable",
            }
        ]
    ).to_csv(RESULTS / "diagnostic_parameter_table.csv", index=False, lineterminator="\n")


def _write_model_comparison() -> None:
    rows = [
        {
            "model": "M0",
            "physical_configuration": "baseline nonpolar retained parameter document",
            "evaluation": "one fixed-pressure ideal-vapor closure value/Jacobian",
            "evaluated_rows": 1,
            "fitted_parameter_available": False,
            "predicted_pco2_available": False,
            "status": "diagnostic_non_promotable",
            "reason": "coupled pressure closure and nonlinear screen timed out",
        }
    ]
    for model, configuration in (
        ("M1", "CO2 quadrupole"),
        ("M2", "neutral dipoles plus CO2 quadrupole"),
        ("M3", "full neutral DD/QQ/DQ"),
        ("M4", "M3 plus induced/cross association"),
        ("M5", "M4 plus SSM+DS Born and qualified permittivity"),
    ):
        rows.append(
            {
                "model": model,
                "physical_configuration": configuration,
                "evaluation": "not_evaluated",
                "evaluated_rows": 0,
                "fitted_parameter_available": False,
                "predicted_pco2_available": False,
                "status": "source_inputs_not_qualified",
                "reason": "required source-fixed physical inputs are not qualified",
            }
        )
    pd.DataFrame(rows).to_csv(
        RESULTS / "diagnostic_model_comparison.csv", index=False, lineterminator="\n"
    )


def _write_support_screen(engine: dict[str, object]) -> None:
    evidence = {
        "schema_version": 1,
        "identity": "mea-pressure-base-support-screen-v1",
        "scope": "44 rows in current R4/R5 source domain",
        "parameter_state": "retained M0 diagnostic parameter document",
        "accounting": {"input": 44, "certified": 38, "rejected": 6, "failed": 0},
        "rejected_rows": [
            "vle_obs_0107",
            "vle_obs_0126",
            "vle_obs_0128",
            "vle_obs_0141",
            "vle_obs_0151",
            "vle_obs_0154",
        ],
        "typed_rejection": {
            "exception": "ChemicalEquilibriumError",
            "failure_kind": "physical_domain_failure",
            "first_failed_physical_criterion": "trace_status",
            "search_status": "domain_rejected",
        },
        "reserved_use": (
            "support certification only; no observed residual, metric, or selection "
            "decision was evaluated"
        ),
        "engine": engine,
    }
    evidence["receipt_sha256"] = _canonical_sha256(evidence)
    (RESULTS / "base_support_screen_evidence.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    )


def main() -> None:
    packet = pd.read_csv(PACKET)
    predictions = pd.read_csv(PREDICTIONS)
    if len(predictions) != 1:
        raise ValueError("bounded diagnostic must retain exactly one evaluated point")
    coupled_timeout = json.loads(COUPLED_TIMEOUT.read_text())
    fit_timeout = json.loads(FIT_TIMEOUT.read_text())
    engine_receipt = json.loads(ENGINE_RECEIPT.read_text())
    _write_parameter_table(predictions.iloc[0])
    _write_model_comparison()
    _write_support_screen(engine_receipt["engine"])
    predictions[
        [
            "observation_id",
            "source_key",
            "temperature_K",
            "mea_mass_fraction",
            "co2_loading_mol_per_mol_mea",
            "closure_residual_log10_fugacity_over_observed_pco2",
            "claim_status",
        ]
    ].to_csv(RESULTS / "diagnostic_residual_summary.csv", index=False, lineterminator="\n")
    decision = {
        "schema_version": 1,
        "identity": "mea-pressure-first-scientific-decision-v1",
        "packet": {
            "rows": len(packet),
            "sha256": _sha256(PACKET),
            "training": int((packet["analysis_role"] == "training").sum()),
            "model_selection": int((packet["analysis_role"] == "model_selection").sum()),
            "reserved": int((packet["analysis_role"] == "reserved").sum()),
            "domain_challenge": int(
                (packet["analysis_role"] == "non_scoring_domain_challenge").sum()
            ),
        },
        "engine": {
            **engine_receipt["engine"],
            "installed_tracer_receipt_sha256": engine_receipt["receipt_sha256"],
        },
        "support_preflight": {
            "input_rows": 44,
            "certified_rows": 38,
            "typed_rejections": 6,
        },
        "diagnostic_evaluation": {
            "status": "one_unfitted_origin_value_and_exact_jacobian",
            "evaluated_rows": 1,
            "available_scoring_rows": 36,
            "observed_pressure_is_model_input": True,
            "modeled_quantity": "liquid_CO2_fugacity_at_observed_T_and_total_P",
            "closure_comparison": "ideal-vapor fugacity assumed equal to observed PCO2",
            "predicted_pco2_available": False,
            "prediction_table_sha256": _sha256(PREDICTIONS),
        },
        "nonlinear_diagnostic_fit": {
            "status": "timed_out_no_FitResult",
            "elapsed_seconds": fit_timeout["elapsed_seconds"],
            "fitted_parameter_available": False,
            "receipt_sha256": fit_timeout["receipt_sha256"],
        },
        "coupled_promotion_lane": {
            "status": "timed_out_no_pressure_root_result",
            "elapsed_seconds": coupled_timeout["elapsed_seconds"],
            "receipt_sha256": coupled_timeout["receipt_sha256"],
        },
        "promotion_decision": "not_promoted",
        "promotion_blockers": [
            "coupled reactive-bubble pressure closure returned no result",
            "fixed-pressure nonlinear regression returned no FitResult",
            "only 1 of 36 training/model-selection rows has a retained exact closure point",
            "residual scales are provisional diagnostic weights, not source uncertainties",
            "M1-M5 source-fixed inputs are not qualified",
            "held-out campaign selection and reserved validation were not scored",
        ],
        "next_method_decision": (
            "profile and reduce the certified chemical-equilibrium owner cost before "
            "any further optimizer execution"
        ),
        "manuscript_changed": False,
        "residual_trend_claim": "unavailable_one_point_is_insufficient",
    }
    decision["receipt_sha256"] = _canonical_sha256(decision)
    (RESULTS / "pressure_first_scientific_decision.json").write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n"
    )
    print(RESULTS / "pressure_first_scientific_decision.json")


if __name__ == "__main__":
    main()
