from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, PARAMETER_ROOT, parameter_mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression"
BORN = ANALYSIS / "born_permittivity_sensitivity"
OUTPUT = ANALYSIS / "results/issue_70"
MANIFESTS = ROOT / "data/reference/MEA/manifests"

SETTINGS = BORN / "results/retained_predictive_parameter_settings.json"
FIT_SUMMARY = BORN / "results/predictive_training_refinement/summary.json"
CANDIDATE_SUMMARY = BORN / "results/retained_predictive_candidate_summary.json"
INDEPENDENT_SUMMARY = BORN / "results/independent_evidence_comparison/summary.json"
BORN_SUMMARY = BORN / "results/summary.json"
INDUCED_SUMMARY = ANALYSIS / "co2_water_induced_association/results/summary.json"
REACTIONS = MANIFESTS / "chemical_reaction_source_contract.json"
ENGINE_LOCK = MANIFESTS / "engine_artifact_lock.json"
MODEL_CONFIGURATIONS = MANIFESTS / "reactive_vle_model_configurations.json"

DECISION = OUTPUT / "predictive_mea_parameter_decision.json"
REFUSAL = OUTPUT / "downstream_transfer_refusal.json"
SPECIES_TABLE = OUTPUT / "species_parameter_table.csv"
BINARY_TABLE = OUTPUT / "binary_association_table.csv"
REACTION_TABLE = OUTPUT / "reaction_correlation_table.csv"
COMPARISON_TABLE = OUTPUT / "comparison_evidence_table.csv"
PROPERTY_TABLE = OUTPUT / "downstream_property_coverage.csv"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _csv_bytes(fieldnames: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _value_status(provenance: dict[str, Any]) -> str:
    locator = str(provenance.get("locator", ""))
    if "derived-" in locator:
        return "derived"
    if "analysis-declared" in locator:
        return "transferred_with_stated_transformation"
    return "fixed_to_source_value"


def _species_table(parameters: dict[str, Any], fitted: dict[str, float]) -> bytes:
    rows: list[dict[str, Any]] = []
    vapor = {"carbon-dioxide", "monoethanolamine", "water"}
    for component in parameters["components"]:
        component_id = component["component_id"]
        values = [
            {
                "identity": f"component/{component_id}/{family}",
                "family": family,
                **entry,
            }
            for family, entry in component["fixed"].items()
        ] + component["coefficients"]
        for item in values:
            provenance = item["provenance"]
            rows.append(
                {
                    "component_id": component_id,
                    "phase_support": "liquid|vapor" if component_id in vapor else "liquid",
                    "parameter_identity": item["identity"],
                    "family": item["family"],
                    "fixed_value": item["value"]["magnitude"],
                    "candidate_fitted_value": fitted.get(item["identity"], ""),
                    "unit": item["value"]["unit"],
                    "fixed_value_status": _value_status(provenance),
                    "candidate_value_status": (
                        "estimated_in_this_work_diagnostic_not_adopted"
                        if item["identity"] in fitted
                        else ""
                    ),
                    "source_id": provenance["source_id"],
                    "source_locator": provenance["locator"],
                    "domain_id": provenance["domain_id"],
                }
            )
    return _csv_bytes(
        (
            "component_id",
            "phase_support",
            "parameter_identity",
            "family",
            "fixed_value",
            "candidate_fitted_value",
            "unit",
            "fixed_value_status",
            "candidate_value_status",
            "source_id",
            "source_locator",
            "domain_id",
        ),
        rows,
    )


def _binary_table(parameters: dict[str, Any]) -> bytes:
    rows: list[dict[str, Any]] = []
    for pair in parameters["pairs"]:
        for item in pair["coefficients"]:
            provenance = item["provenance"]
            rows.append(
                {
                    "interaction_kind": "binary_coefficient",
                    "endpoint_a": pair["component_id_a"],
                    "endpoint_b": pair["component_id_b"],
                    "parameter_identity": item["identity"],
                    "value": item["value"]["magnitude"],
                    "unit": item["value"]["unit"],
                    "value_status": _value_status(provenance),
                    "source_id": provenance["source_id"],
                    "source_locator": provenance["locator"],
                    "domain_id": provenance["domain_id"],
                }
            )
    for edge in parameters["topology"]["edges"]:
        provenance = edge["source"]["provenance"][0]
        endpoint_a = f"{edge['endpoint_a']['component_id']}/{edge['endpoint_a']['site_id']}"
        endpoint_b = f"{edge['endpoint_b']['component_id']}/{edge['endpoint_b']['site_id']}"
        for family in ("energy_over_k", "volume"):
            item = edge[family]
            rows.append(
                {
                    "interaction_kind": "association_edge",
                    "endpoint_a": endpoint_a,
                    "endpoint_b": endpoint_b,
                    "parameter_identity": item["identity"],
                    "value": item["value"]["magnitude"],
                    "unit": item["value"]["unit"],
                    "value_status": "fixed_to_source_value",
                    "source_id": provenance["source_id"],
                    "source_locator": provenance["locator"],
                    "domain_id": provenance["domain_id"],
                }
            )
    return _csv_bytes(
        (
            "interaction_kind",
            "endpoint_a",
            "endpoint_b",
            "parameter_identity",
            "value",
            "unit",
            "value_status",
            "source_id",
            "source_locator",
            "domain_id",
        ),
        rows,
    )


def _reaction_table(contract: dict[str, Any]) -> bytes:
    standard = contract["common_source_standard_state"]
    rows = []
    for reaction in contract["reactions"]:
        rows.append(
            {
                "reaction_id": reaction["reaction_id"],
                "stoichiometry": json.dumps(reaction["stoichiometry"], separators=(",", ":")),
                "correlation": json.dumps(reaction["correlation"], sort_keys=True, separators=(",", ":")),
                "temperature_min_k": reaction["temperature_range_k"][0],
                "temperature_max_k": reaction["temperature_range_k"][1],
                "standard_state": standard["identity"],
                "source_record_ids": ";".join(reaction["source_record_ids"]),
                "value_status": "reported_by_source_fixed_not_fitted",
            }
        )
    return _csv_bytes(
        (
            "reaction_id",
            "stoichiometry",
            "correlation",
            "temperature_min_k",
            "temperature_max_k",
            "standard_state",
            "source_record_ids",
            "value_status",
        ),
        rows,
    )


def _comparison_table() -> bytes:
    rows: list[dict[str, Any]] = []
    for family in ("2b", "3b", "4c"):
        path = ANALYSIS / f"pressure_first/results/cai_held_water_mea_{family}_fit.json"
        result = _load(path)
        for partition, key in (("training", "training_metrics"), ("model_selection", "model_selection_metrics")):
            rows.append(
                {
                    "analysis": "neutral_binary_qualification",
                    "configuration": f"held-water/{family}-MEA",
                    "partition": partition,
                    "quantity": "normalized_rmse",
                    "value": result[key]["normalized_rmse"],
                    "unit": "dimensionless",
                    "row_count": result[key]["residual_count"],
                    "failed_count": 0,
                    "decision_status": result["promotion_decision"],
                    "source_artifact": _relative(path),
                }
            )
    induced = _load(INDUCED_SUMMARY)
    rows.append(
        {
            "analysis": "co2_water_induced_association",
            "configuration": "reciprocal-Schick-Pabsch-2B",
            "partition": "source_reproduction",
            "quantity": "log_pressure_rmse",
            "value": induced["log_pressure_rmse"],
            "unit": "dimensionless",
            "row_count": induced["row_count"],
            "failed_count": 0,
            "decision_status": "retained_fixed_physical_interaction",
            "source_artifact": _relative(INDUCED_SUMMARY),
        }
    )
    candidate = _load(CANDIDATE_SUMMARY)
    for metric in candidate["metrics"]:
        rows.append(
            {
                "analysis": "reactive_parameter_estimation",
                "configuration": "retained-diagnostic-candidate",
                "partition": metric["partition"],
                "quantity": f"{metric['block']}_log_rmse",
                "value": metric["log_rmse"],
                "unit": "dimensionless",
                "row_count": metric["row_count"],
                "failed_count": candidate["failed_or_omitted_rows"],
                "decision_status": "not_promoted",
                "source_artifact": _relative(CANDIDATE_SUMMARY),
            }
        )
    independent = _load(INDEPENDENT_SUMMARY)
    for metric in independent["domains"]:
        rows.append(
            {
                "analysis": "multiple_property_comparison",
                "configuration": "calorimetry-balanced/retained-ratio",
                "partition": metric["domain"],
                "quantity": metric["quantity"],
                "value": metric["balanced_to_retained_error_ratio"],
                "unit": "ratio",
                "row_count": metric["target_count"],
                "failed_count": 0,
                "decision_status": "diagnostic_not_independent_validation",
                "source_artifact": _relative(INDEPENDENT_SUMMARY),
            }
        )
    return _csv_bytes(
        (
            "analysis",
            "configuration",
            "partition",
            "quantity",
            "value",
            "unit",
            "row_count",
            "failed_count",
            "decision_status",
            "source_artifact",
        ),
        rows,
    )


def _property_table() -> bytes:
    rows = [
        ("mass density", "ePC-SAFT mixture state", "calculated_but_not_downstream_accepted", "data/reference/MEA/observations/density_viscosity/", "reported for admitted source rows; model uncertainty unavailable", "yes"),
        ("fugacity", "ePC-SAFT phase state", "calculated_but_not_downstream_accepted", "installed Engine equilibrium outputs", "numerical certification only; physical uncertainty unavailable", "yes"),
        ("CO2 partial pressure", "reactive bubble output", "diagnostic_candidate_only", _relative(CANDIDATE_SUMMARY), "no independent untouched validation partition", "yes"),
        ("liquid speciation", "homogeneous reactive output", "diagnostic_candidate_only", _relative(CANDIDATE_SUMMARY), "no independent untouched validation partition", "yes"),
        ("enthalpy / heat of absorption", "column energy balance", "not_accepted", "data/reference/MEA/observations/calorimetry/", "reference-state derivative and covariance incomplete", "no"),
        ("heat capacity", "column energy balance", "separate_downstream_correlation_required", "not qualified by Issue 70", "not assessed", "no"),
        ("viscosity", "transport", "separate_downstream_correlation_required", "data/reference/MEA/observations/density_viscosity/", "reported source uncertainty; no adopted correlation here", "no"),
        ("diffusivity", "mass transfer", "separate_downstream_correlation_required", "not qualified by Issue 70", "not assessed", "no"),
        ("surface tension", "mass transfer", "separate_downstream_correlation_required", "not qualified by Issue 70", "not assessed", "no"),
        ("thermal conductivity", "column energy transfer", "separate_downstream_correlation_required", "not qualified by Issue 70", "not assessed", "no"),
        ("enhancement factor", "rate model", "separate_downstream_model_required", "MEA-Absorption-Column ownership", "not assessed", "no"),
    ]
    return _csv_bytes(
        ("quantity", "consumer_scope", "status", "source_or_owner", "uncertainty_status", "calculated_by_thermodynamic_parameter_set"),
        [dict(zip(("quantity", "consumer_scope", "status", "source_or_owner", "uncertainty_status", "calculated_by_thermodynamic_parameter_set"), row, strict=True)) for row in rows],
    )


def build_outputs() -> dict[Path, bytes]:
    settings = _load(SETTINGS)
    fit_summary = _load(FIT_SUMMARY)
    engine_lock = _load(ENGINE_LOCK)
    reaction_contract = _load(REACTIONS)
    parameters = parameter_mapping(
        permittivity="ion-specific-suppression",
        ion_specific_suppression=settings["ion_specific_suppression_coefficients"],
    )
    inputs = [
        SETTINGS,
        FIT_SUMMARY,
        CANDIDATE_SUMMARY,
        INDEPENDENT_SUMMARY,
        BORN_SUMMARY,
        INDUCED_SUMMARY,
        REACTIONS,
        ENGINE_LOCK,
        MODEL_CONFIGURATIONS,
        *sorted(PARAMETER_ROOT.iterdir()),
    ]
    input_hashes = {_relative(path): _sha256(path) for path in inputs}
    fit_wheel = settings["engine_wheel_sha256"]
    locked_wheel = engine_lock["wheel_sha256"]
    record = {
        "schema": "mea.predictive-parameter-decision",
        "schema_version": 1,
        "identity": "mea-issue-70-supported-negative-v1",
        "decision": {
            "status": "supported_negative",
            "parameter_set_adopted": False,
            "predictive_export": "prohibited",
            "independent_validation": "blocked_no_untouched_replacement_partition",
            "reasons": [
                "the predictive-training optimizer terminated NO_CONVERGENCE",
                "the active scaled Jacobian is weakly identified",
                "rows formerly marked reserved were opened during model selection",
                "the fitted-candidate wheel hash does not match the frozen Engine lock",
                "the direct Wong challenge contains NaClO4 outside the nine-species chemistry",
                "calorimetry lacks an accepted reference-state derivative and covariance model",
            ],
        },
        "ordered_species": list(COMPONENT_IDS),
        "fixed_configuration": {
            "retained_settings": _relative(SETTINGS),
            "parameter_sources": [
                _relative(path) for path in sorted(PARAMETER_ROOT.iterdir())
            ],
            "materialized_views": [
                _relative(SPECIES_TABLE),
                _relative(BINARY_TABLE),
            ],
        },
        "reaction_contract": {
            "path": _relative(REACTIONS),
            "sha256": _sha256(REACTIONS),
            "materialized_view": _relative(REACTION_TABLE),
        },
        "diagnostic_candidate": {
            "settings": settings,
            "active_coordinates": fit_summary["active"],
            "solver": fit_summary["solver"],
            "fit_result_identity": fit_summary["fit_result_identity"],
            "summary": fit_summary,
            "value_status": "estimated_in_this_work_diagnostic_not_adopted",
        },
        "identity_checks": {
            "fitted_candidate_wheel_sha256": fit_wheel,
            "frozen_engine_lock_wheel_sha256": locked_wheel,
            "wheel_identity_matches": fit_wheel == locked_wheel,
            "input_file_sha256": input_hashes,
        },
        "generated_views": [
            _relative(path)
            for path in (SPECIES_TABLE, BINARY_TABLE, REACTION_TABLE, COMPARISON_TABLE, PROPERTY_TABLE)
        ],
        "downstream_transfer": {
            "status": "refused",
            "record": _relative(REFUSAL),
            "property_coverage": _relative(PROPERTY_TABLE),
        },
        "claim_boundary": "Diagnostic fixed-configuration and candidate evidence only; no predictive MEA parameter set or column transfer is authorized.",
    }
    decision_bytes = _json_bytes(record)
    refusal = {
        "schema": "mea.downstream-transfer-refusal",
        "schema_version": 1,
        "status": "refused",
        "reason": "Issue 70 reached a supported negative decision; the candidate failed numerical, identifiability, immutable-wheel, and independent-validation gates.",
        "parameter_decision_record": _relative(DECISION),
        "parameter_decision_record_sha256": _sha256_bytes(decision_bytes),
        "ordered_species": list(COMPONENT_IDS),
        "destination": "MEA-Absorption-Column issues #12 and #3",
        "prohibited_actions": ["predictive parameter export", "column parameter mapping", "predictive manuscript claim"],
    }
    return {
        DECISION: decision_bytes,
        REFUSAL: _json_bytes(refusal),
        SPECIES_TABLE: _species_table(parameters, settings["shared_parameters"]),
        BINARY_TABLE: _binary_table(parameters),
        REACTION_TABLE: _reaction_table(reaction_contract),
        COMPARISON_TABLE: _comparison_table(),
        PROPERTY_TABLE: _property_table(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.check:
        stale = [_relative(path) for path, payload in outputs.items() if not path.exists() or path.read_bytes() != payload]
        if stale:
            raise SystemExit("stale Issue 70 outputs: " + ", ".join(stale))
        print("Issue 70 decision outputs are current")
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path, payload in outputs.items():
        path.write_bytes(payload)
        print(_relative(path))


if __name__ == "__main__":
    main()
