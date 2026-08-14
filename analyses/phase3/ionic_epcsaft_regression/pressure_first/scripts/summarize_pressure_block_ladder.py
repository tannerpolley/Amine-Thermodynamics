from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
RESULTS = ANALYSIS / "results"
FIGURES = RESULTS / "figures"
ENGINE_LOCK = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"
PACKET_RECEIPT = RESULTS / "pressure_packet_receipt.json"
SCREENS = {
    "M0_direction_ladder": RESULTS / "pressure_parameter_direction_screen.json",
    "M0_MEA_water_direction": RESULTS / "m0_mea_water_direction_screen.json",
    "M1_source_fixed": RESULTS / "m1_source_fixed_direction_screen.json",
}
OUTPUT = RESULTS / "pressure_block_ladder_decision.json"
TABLE = RESULTS / "pressure_block_ladder_summary.csv"
PLOT_DATA = FIGURES / "pressure_block_ladder_plot_data.csv"
BINARY_FITS = {
    "current_2b_held": RESULTS / "cai_mea_water_binary_fit.json",
    "baygi_3b2b": RESULTS / "cai_baygi_3b2b_binary_fit.json",
    "baygi_3b4c": RESULTS / "cai_baygi_3b4c_binary_fit.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def _load_self_hashed(path: Path) -> dict[str, Any]:
    payload = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    receipt = cast(str, payload.pop("receipt_sha256"))
    if receipt != _canonical_sha256(payload):
        raise ValueError(f"receipt mismatch: {path.relative_to(ROOT)}")
    payload["receipt_sha256"] = receipt
    return payload


def _block(
    screen: dict[str, Any],
    coordinate_ids: tuple[str, ...],
) -> dict[str, Any]:
    for block in screen["block_diagnostics"]:
        if tuple(block["coordinate_identities"]) == coordinate_ids:
            return cast(dict[str, Any], block)
    raise KeyError(coordinate_ids)


def _decision_rows(screens: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    m0 = screens["M0_direction_ladder"]
    mea_water = screens["M0_MEA_water_direction"]
    m1 = screens["M1_source_fixed"]
    specifications = (
        (
            "M0-k-co2-water",
            "M0",
            m0,
            ("pair/carbon-dioxide/water/k_ij",),
            "rejected",
            "interior rank-one direction lowers the local objective but worsens the loading slope and leaves strong curvature",
        ),
        (
            "M0-plus-k-co2-mea",
            "M0",
            m0,
            (
                "pair/carbon-dioxide/water/k_ij",
                "pair/carbon-dioxide/monoethanolamine/k_ij",
            ),
            "rejected",
            "condition number exceeds 1e4 and the CO2-MEA coordinate leaves its physical bounds",
        ),
        (
            "M0-plus-meah-sigma",
            "M0",
            m0,
            (
                "pair/carbon-dioxide/water/k_ij",
                "component/protonated-monoethanolamine/segment_diameter",
            ),
            "rejected",
            "the local candidate leaves bounds and pressure alone cannot promote a single-ion coordinate",
        ),
        (
            "M0-plus-meacoo-sigma",
            "M0",
            m0,
            (
                "pair/carbon-dioxide/water/k_ij",
                "component/carbamate-anion/segment_diameter",
            ),
            "rejected",
            "the candidate is interior but materially worsens the loading trend and pressure alone cannot promote a single-ion coordinate",
        ),
        (
            "M0-plus-k-mea-water",
            "M0",
            mea_water,
            (
                "pair/carbon-dioxide/water/k_ij",
                "pair/monoethanolamine/water/k_ij",
            ),
            "rejected",
            "the identifiable interior direction worsens loading slope, residual range, and RMSE versus the simpler block; the retained -0.052 origin is formulation-mismatched",
        ),
        (
            "M1-k-co2-water",
            "M1",
            m1,
            ("pair/carbon-dioxide/water/k_ij",),
            "rejected",
            "the source-fixed quadrupolar model is worse than M0 at its exact origin and its local candidate does not outperform the simpler M0 candidate",
        ),
    )
    rows: list[dict[str, object]] = []
    for identity, model, screen, coordinates, status, reason in specifications:
        block = _block(screen, coordinates)
        rows.append(
            {
                "block_identity": identity,
                "model": model,
                "coordinate_identities": list(coordinates),
                "rank": block["rank"],
                "condition_number": block["condition_number"],
                "linearized_candidate": block["linearized_candidate"],
                "candidate_inside_bounds": block["linearized_candidate_inside_bounds"],
                "origin_log10_rmse": block["initial_log10_rmse"],
                "linearized_log10_rmse": block["linearized_log10_rmse"],
                "origin_loading_slope": block[
                    "initial_loading_slope_log10_per_loading"
                ],
                "linearized_loading_slope": block[
                    "linearized_loading_slope_log10_per_loading"
                ],
                "screen_status": status,
                "reason": reason,
                "nonlinear_fit_attempted": False,
                "scale_sensitivity_decision": (
                    "unchanged for preregistered uniform scale factors 0.5, 1, and 2"
                ),
            }
        )
    return rows


def _write_table(rows: list[dict[str, object]]) -> None:
    columns = (
        "block_identity",
        "model",
        "coordinate_identities",
        "rank",
        "condition_number",
        "linearized_candidate",
        "candidate_inside_bounds",
        "origin_log10_rmse",
        "linearized_log10_rmse",
        "origin_loading_slope",
        "linearized_loading_slope",
        "screen_status",
        "reason",
        "nonlinear_fit_attempted",
        "scale_sensitivity_decision",
    )
    with TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "coordinate_identities": ";".join(
                        cast(list[str], row["coordinate_identities"])
                    ),
                    "linearized_candidate": ";".join(
                        f"{value:.16g}"
                        for value in cast(list[float], row["linearized_candidate"])
                    ),
                }
            )


def _write_plot_data(screens: dict[str, dict[str, Any]]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for model, key, description in (
        (
            "M0",
            "M0_direction_ladder",
            "exact current nonpolar diagnostic origin; all M0 direction blocks share this state",
        ),
        (
            "M1",
            "M1_source_fixed",
            "exact source-fixed Gross 2005 CO2 quadrupolar origin",
        ),
    ):
        for result in screens[key]["results"]:
            if result["status"] != "evaluated":
                continue
            rows.append(
                {
                    "observation_id": result["observation_id"],
                    "model": model,
                    "parameter_state": description,
                    "analysis_role": "training",
                    "source_key": "Hilliard2008",
                    "temperature_k": 313.15,
                    "mea_mass_fraction": 0.17,
                    "loading_mol_co2_per_mol_mea": result[
                        "loading_mol_co2_per_mol_mea"
                    ],
                    "observed_pco2_pa": result["observed_pco2_pa"],
                    "predicted_pco2_pa": result["predicted_pco2_pa"],
                    "residual_log10": result["residual_log10"],
                    "bubble_closure_abs": result["bubble_closure_abs"],
                    "prediction_status": "exact_reactive_bubble_root",
                    "candidate_curves_plotted": False,
                    "claim_status": "diagnostic_non_promotable",
                }
            )
    columns = tuple(rows[0])
    with PLOT_DATA.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    screens = {identity: _load_self_hashed(path) for identity, path in SCREENS.items()}
    if any(screen["accounting"]["non_evaluable_rows"] for screen in screens.values()):
        raise RuntimeError("a pressure direction screen contains non-evaluable rows")
    decision_rows = _decision_rows(screens)
    _write_table(decision_rows)
    _write_plot_data(screens)
    packet = _load_self_hashed(PACKET_RECEIPT)
    binary_fits = {
        identity: _load_self_hashed(path) for identity, path in BINARY_FITS.items()
    }
    payload: dict[str, object] = {
        "schema_version": 1,
        "identity": "mea-pressure-block-ladder-decision-v1",
        "issue": "https://github.com/tannerpolley/MEA-Thermodynamics/issues/13",
        "claim_status": "completed_bounded_pressure_direction_screen_non_promotable",
        "engine": json.loads(ENGINE_LOCK.read_text(encoding="utf-8")),
        "pressure_packet": {
            "receipt_sha256": packet["receipt_sha256"],
            "input_rows": packet["packet"]["rows"],
            "training_rows": 30,
            "model_selection_rows": 6,
            "reserved_rows": 8,
        },
        "screen_receipts": {
            identity: {
                "path": str(SCREENS[identity].relative_to(ROOT)),
                "sha256": _sha256(SCREENS[identity]),
                "receipt_sha256": screen["receipt_sha256"],
                "evaluated_rows": screen["accounting"]["evaluated_rows"],
            }
            for identity, screen in screens.items()
        },
        "blocks": decision_rows,
        "model_comparison": [
            {
                "model": "M0",
                "status": "evaluated_exact_origin_rejected_for_fit",
                "exact_training_rows": 6,
                "reason": "no screened block passes the loading-trend, bounds, provenance, and identifiability gates",
            },
            {
                "model": "M1",
                "status": "evaluated_exact_source_fixed_origin_rejected",
                "exact_training_rows": 6,
                "reason": "Gross 2005 quadrupolar M1 does not improve on M0 enough to justify complexity",
            },
            *[
                {
                    "model": model,
                    "status": "not_evaluable_source_fixed_inputs_missing",
                    "exact_training_rows": 0,
                    "reason": reason,
                }
                for model, reason in (
                    ("M2", "no formulation-qualified source-fixed MEA dipole input"),
                    ("M3", "M2 input gap also blocks complete DD/QQ/DQ qualification"),
                    (
                        "M4",
                        "M3 plus source-fixed induced/cross-association topology is not qualified",
                    ),
                    (
                        "M5",
                        "M4 plus loaded-solution permittivity/Born evidence is not qualified",
                    ),
                )
            ],
        ],
        "independent_binary_audit": {
            "cai_1996_rows_extracted": 29,
            "cai_training_rows": 12,
            "cai_model_selection_rows": 13,
            "cai_source_sha256": "091edb997b7bddf3c791a0a2dff9ac03ade971a7f580f6b3ab7cbf85a305b70a",
            "fit_receipts": {
                identity: {
                    "path": str(BINARY_FITS[identity].relative_to(ROOT)),
                    "sha256": _sha256(BINARY_FITS[identity]),
                    "receipt_sha256": fit["receipt_sha256"],
                    "admitted_training_rows": fit["accounting"][
                        "admitted_training_rows"
                    ],
                    "admitted_model_selection_rows": fit["accounting"][
                        "admitted_model_selection_rows"
                    ],
                    "selected_diagnostic_k_ij": fit["selected_value"],
                    "training_normalized_rmse": fit["training_metrics"][
                        "normalized_rmse"
                    ],
                    "model_selection_normalized_rmse": fit[
                        "model_selection_metrics"
                    ].get("normalized_rmse"),
                    "rank": fit["rank"],
                    "condition_number": fit["condition_number"],
                    "all_starts_same_solution": fit["gates"][
                        "all_starts_same_solution"
                    ],
                    "all_gates_pass": fit["all_gates_pass"],
                }
                for identity, fit in binary_fits.items()
            },
            "all_gates_pass": any(
                fit["all_gates_pass"] for fit in binary_fits.values()
            ),
            "finding": (
                "all three exact fixed-state closure fits are rank-one, interior, and "
                "multistart-consistent, but none passes source-scale residual and trend "
                "gates. Baygi's reported kij values were fitted with Eq. 12 Bubble-T and "
                "Dew-T composition objectives, which the Engine does not expose as an "
                "exact-Jacobian generic observation family"
            ),
        },
        "accounting": {
            "screened_blocks": len(decision_rows),
            "passed_blocks": 0,
            "nonlinear_fits_started": 0,
            "independent_binary_diagnostic_fits_started": len(binary_fits),
            "training_pressure_roots_evaluated_per_model": 6,
            "model_selection_rows_used": 0,
            "reserved_rows_used": 0,
            "numeric_failure_penalties": 0,
        },
        "promotion_decision": "not_promoted",
        "promotion_blockers": [
            "no smallest qualified pressure-only block passes all preregistered gates",
            "the active MEA-water parameter value is not transferable across its source and runtime association/pure-component formulations",
            "principal ionic coordinates require same-state speciation or independent volumetric/activity evidence",
            "Böttinger direct speciation lacks exact per-sample pressure and includes an omitted measured byproduct; Matin species are balance-inferred without the required covariance contract",
            "M2-M5 source-fixed molecular, association, permittivity, or Born inputs remain incomplete",
            "the current, Baygi 3B/2B, and Baygi 3B/4C neutral formulations all fail the exact fixed-state Cai source-scale residual/trend gates",
            "Engine exposes exact fixed-pressure fugacity blocks but not Baygi Eq. 12 Bubble-T/Dew-T composition observations with exact total parameter Jacobians",
        ],
        "smallest_unresolved_scientific_decision": (
            "implement a generic declared-one-liquid/one-vapor Bubble-T and Dew-T "
            "observation family with exact total parameter derivatives, then reproduce "
            "Baygi Eq. 12 on the two Cai pressure levels before freezing MEA-water kij"
        ),
        "manuscript_changed": False,
        "table_sha256": _sha256(TABLE),
        "plot_data_sha256": _sha256(PLOT_DATA),
    }
    payload["receipt_sha256"] = _canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT.relative_to(ROOT))
    print(TABLE.relative_to(ROOT))
    print(PLOT_DATA.relative_to(ROOT))


if __name__ == "__main__":
    main()
