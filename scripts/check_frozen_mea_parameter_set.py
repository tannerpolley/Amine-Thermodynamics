from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import tomllib

import epcsaft

from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, materialize_parameter_candidate


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "data/reference/MEA/parameters/best_available_mea_epcsaft/1/freeze.toml"
RESULTS = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/"
    "born_permittivity_sensitivity/results"
)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _require_value(actual: str, expected: object, identity: str) -> None:
    matches = (
        actual == expected
        if isinstance(expected, str)
        else math.isclose(float(actual), float(expected), rel_tol=1e-12, abs_tol=1e-12)
    )
    if not matches:
        raise RuntimeError(f"Frozen value drifted for {identity}: {actual} != {expected}")


def main() -> None:
    record = tomllib.loads(FREEZE.read_text(encoding="utf-8"))
    if record["status"] != "frozen-best-available-engineering-set":
        raise RuntimeError("Frozen MEA set has an unexpected status")
    for source in record["sources"]:
        path = ROOT / source["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise RuntimeError(f"Frozen source drifted: {source['path']}")

    root = FREEZE.parent
    selected_rows = _rows(root / record["selected_values"])
    selected = {row["parameter_id"]: row["value"] for row in selected_rows}
    if len(selected) != len(selected_rows):
        raise RuntimeError("Frozen parameter identities must be unique")

    settings = _load_json(RESULTS / "retained_predictive_parameter_settings.json")
    fit_path = RESULTS / "predictive_training_refinement/summary.json"
    fit = _load_json(fit_path)
    correction = _load_json(
        RESULTS / "calorimetry_consistency/reaction_temperature_candidate.json"
    )
    numerical = record["numerical_evidence"]
    if (
        record["engine"]["evaluation_wheel_sha256"] != settings["engine_wheel_sha256"]
        or fit["status"] != numerical["fit_status"]
        or fit["solver"]["controls"]["maximum_iterations"]
        != numerical["optimizer_maximum_iterations"]
        or numerical["optimizer_termination"] not in fit["termination"]
        or fit["accounting"]["accepted_starts"] != numerical["accepted_starts"]
        or fit["accounting"]["failed_starts"] != numerical["failed_starts"]
        or fit["accounting"]["dropped_rows"] != numerical["dropped_rows"]
    ):
        raise RuntimeError("Frozen numerical evidence drifted")

    structure = settings["fixed_structure"]
    association = settings["co2_water_induced_association"]
    expected = {
        "model/born": structure["born"],
        "model/relative_permittivity": structure["relative_permittivity"],
        "model/polar": str(structure["polar_term"]).lower(),
        "model/water_relative_permittivity": structure["water_relative_permittivity"],
        **fit["fitted_values"],
        **{
            f"component/{component}/ion_specific_suppression_coefficient": value
            for component, value in settings[
                "ion_specific_suppression_coefficients"
            ].items()
        },
        "association/carbon-dioxide/water/energy_over_k": association[
            "energy_over_k_kelvin"
        ],
        "association/carbon-dioxide/water/volume": association["volume"],
        "pair/carbon-dioxide/water/k_ij_slope": 3.016e-4,
        "pair/carbon-dioxide/water/k_ij_anchor_temperature": 313.15,
        "reaction/R4/delta_ln_k_at_353_15_k": correction[
            "candidate_r4_delta_ln_k_at_353_15_k"
        ],
        "reaction/R5/delta_ln_k_at_353_15_k": correction[
            "candidate_r5_delta_ln_k_at_353_15_k"
        ],
    }
    if set(selected) != set(expected):
        raise RuntimeError("Frozen parameter identity set drifted")
    for identity, value in expected.items():
        _require_value(selected[identity], value, identity)

    mapping = materialize_parameter_candidate(fit_path)
    payload = (json.dumps(mapping, indent=2, sort_keys=True) + "\n").encode()
    if f"sha256:{hashlib.sha256(payload).hexdigest()}" != record[
        "resolved_engine_mapping_sha256"
    ]:
        raise RuntimeError("Frozen resolved Engine mapping hash drifted")
    epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)

    metrics = {
        (row["quantity"], row["partition"]): row
        for row in _rows(root / record["comparison_metrics"])
    }
    balanced = _load_json(
        RESULTS / "calorimetry_balanced_reaction_validation/summary.json"
    )
    comparison = _load_json(RESULTS / "independent_evidence_comparison/summary.json")
    pressure = balanced["temperature_challenge_pressure_metrics"]
    training = balanced["training_speciation_metrics"]
    reserved = balanced["reserved_speciation_metrics"]
    heat = next(item for item in comparison["domains"] if item["domain"] == "calorimetry")
    expected_metrics = {
        ("pressure_log_rmse", "temperature_challenge"): pressure["log_rmse"],
        ("pressure_rms_factor", "temperature_challenge"): pressure["rms_factor"],
        ("speciation_log_rmse", "training"): training["log_rmse"],
        ("speciation_rms_factor", "training"): training["rms_factor"],
        ("speciation_log_rmse", "reserved"): reserved["log_rmse"],
        ("speciation_rms_factor", "reserved"): reserved["rms_factor"],
        ("heat_release_rmse", "comparison"): heat["balanced_error"],
        ("equal_domain_error_ratio_vs_retained", "comparison"): comparison[
            "equal_domain_balanced_to_retained_score"
        ],
        ("preference_fraction_over_weight_grid", "comparison"): comparison[
            "candidate_preferred_grid_fraction"
        ],
    }
    for identity, value in expected_metrics.items():
        _require_value(metrics[identity]["value"], value, "/".join(identity))
    if any(int(row["failed_or_omitted_count"]) for row in metrics.values()):
        raise RuntimeError("Frozen comparison contains failed or omitted values")

    print(
        f"Frozen MEA parameter set passed: {record['set_id']} v{record['set_version']} "
        f"({len(COMPONENT_IDS)} species, {len(selected)} selected values)"
    )


if __name__ == "__main__":
    main()
