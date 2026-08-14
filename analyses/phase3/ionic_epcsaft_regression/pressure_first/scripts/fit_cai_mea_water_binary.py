from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import epcsaft
import numpy as np
from scipy.optimize import least_squares

from MEA.epcsaft_ionic.parameter_document import parameter_mapping


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
ENGINE_LOCK = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def _extend_domain(value: object, domain_id: str) -> None:
    if isinstance(value, dict):
        if "domain_id" in value:
            value["domain_id"] = domain_id
        for child in value.values():
            _extend_domain(child, domain_id)
    elif isinstance(value, list):
        for child in value:
            _extend_domain(child, domain_id)


def _set_coefficient(
    mapping: dict[str, Any],
    component_id: str,
    family: str,
    magnitude: float,
    unit: str,
    provenance: dict[str, str],
) -> None:
    component = next(
        item for item in mapping["components"] if item["component_id"] == component_id
    )
    coefficients = [
        item for item in component["coefficients"] if item["family"] != family
    ]
    coefficients.append(
        {
            "identity": f"component/{component_id}/{family}",
            "family": family,
            "value": {"magnitude": magnitude, "unit": unit},
            "provenance": provenance,
        }
    )
    component["coefficients"] = sorted(
        coefficients, key=lambda item: str(item["identity"])
    )


def _apply_baygi(mapping: dict[str, Any], domain_id: str, *, water_scheme: str) -> None:
    source_id = "baygi-pahlavanzadeh-2015-pcsaft"
    mapping["sources"].append(
        {
            "source_id": source_id,
            "citation": (
                "Fakouri Baygi and Pahlavanzadeh (2015), Chemical Engineering "
                "Research and Design 93, 789-799"
            ),
            "use_basis": (
                f"Table 2 3B-MEA/{water_scheme.upper()}-water pure parameters, "
                "Eqs. 6-7 association "
                "combining rules, and Table 3 MEA-water binary interaction"
            ),
        }
    )
    if water_scheme not in {"2b", "4c"}:
        raise ValueError(f"unsupported Baygi water association scheme: {water_scheme}")
    water_values = (
        {
            "segment_count": (1.9599, "dimensionless"),
            "segment_diameter": (2.362, "angstrom"),
            "dispersion_energy_over_k": (279.42, "kelvin"),
        }
        if water_scheme == "2b"
        else {
            "segment_count": (2.1945, "dimensionless"),
            "segment_diameter": (2.229, "angstrom"),
            "dispersion_energy_over_k": (141.66, "kelvin"),
        }
    )
    component_values = {
        "monoethanolamine": {
            "segment_count": (4.5354, "dimensionless"),
            "segment_diameter": (2.6019, "angstrom"),
            "dispersion_energy_over_k": (204.0438, "kelvin"),
        },
        "water": water_values,
    }
    for component_id, values in component_values.items():
        for family, (magnitude, unit) in values.items():
            _set_coefficient(
                mapping,
                component_id,
                family,
                magnitude,
                unit,
                {
                    "source_id": source_id,
                    "locator": (
                        "Table 2: 3B MEA row"
                        if component_id == "monoethanolamine"
                        else f"Table 2: {water_scheme.upper()} H2O row"
                    ),
                    "domain_id": domain_id,
                },
            )
    mapping["correlations"] = [
        item
        for item in mapping["correlations"]
        if not (
            item["component_id"] == "water" and item["family"] == "segment_diameter"
        )
    ]
    mea_sigma = 2.6019
    water_sigma = 2.362 if water_scheme == "2b" else 2.229
    mea_volume = 0.118488
    water_volume = 0.1750 if water_scheme == "2b" else 0.2039
    cross_volume = (
        math.sqrt(mea_volume * water_volume)
        * (math.sqrt(mea_sigma * water_sigma) / (0.5 * (mea_sigma + water_sigma))) ** 3
    )
    water_energy = 2059.28 if water_scheme == "2b" else 1804.17
    cross_energy = 0.5 * (2383.4744 + water_energy)
    provenance = {
        "source_id": source_id,
        "locator": "Table 2 and association combining rules Eqs. 6-7",
        "domain_id": domain_id,
    }

    def edge(
        component_a: str,
        site_a: str,
        component_b: str,
        site_b: str,
        energy: float,
        volume: float,
    ) -> dict[str, object]:
        prefix = f"association/{component_a}/{site_a}/{component_b}/{site_b}"
        return {
            "endpoint_a": {"component_id": component_a, "site_id": site_a},
            "endpoint_b": {"component_id": component_b, "site_id": site_b},
            "energy_over_k": {
                "identity": f"{prefix}/energy_over_k",
                "value": {"magnitude": energy, "unit": "kelvin"},
            },
            "volume": {
                "identity": f"{prefix}/volume",
                "value": {"magnitude": volume, "unit": "dimensionless"},
            },
            "source": {"kind": "explicit", "provenance": [provenance]},
        }

    mapping["topology"] = {
        "presets": [],
        "sites": [
            {
                "component_id": "monoethanolamine",
                "site_id": "a",
                "site_role": "donor",
                "multiplicity": 2,
                "provenance": provenance,
            },
            {
                "component_id": "monoethanolamine",
                "site_id": "b",
                "site_role": "acceptor",
                "multiplicity": 1,
                "provenance": provenance,
            },
            {
                "component_id": "water",
                "site_id": "a",
                "site_role": "donor",
                "multiplicity": 1 if water_scheme == "2b" else 2,
                "provenance": provenance,
            },
            {
                "component_id": "water",
                "site_id": "b",
                "site_role": "acceptor",
                "multiplicity": 1 if water_scheme == "2b" else 2,
                "provenance": provenance,
            },
        ],
        "edges": [
            edge(
                "monoethanolamine",
                "a",
                "monoethanolamine",
                "b",
                2383.4744,
                mea_volume,
            ),
            edge(
                "monoethanolamine",
                "a",
                "water",
                "b",
                cross_energy,
                cross_volume,
            ),
            edge(
                "monoethanolamine",
                "b",
                "water",
                "a",
                cross_energy,
                cross_volume,
            ),
            edge("water", "a", "water", "b", water_energy, water_volume),
        ],
    }
    pair = next(
        item
        for item in mapping["pairs"]
        if {item["component_id_a"], item["component_id_b"]}
        == {"monoethanolamine", "water"}
    )
    coefficient = pair["coefficients"][0]
    source_kij = -0.0146 if water_scheme == "2b" else -0.052
    coefficient["value"] = {"magnitude": source_kij, "unit": "dimensionless"}
    coefficient["provenance"] = {
        "source_id": source_id,
        "locator": f"Table 3: 3B MEA / {water_scheme.upper()} H2O",
        "domain_id": domain_id,
    }


def _parameters(config: dict[str, Any]) -> epcsaft.Parameters:
    mapping = cast(dict[str, Any], deepcopy(parameter_mapping(polar="none")))
    domain_id = "cai-1996-admitted-neutral-binary-domain"
    maximum = float(config["data"]["admitted_temperature_max_k"])
    mapping["domains"] = [
        {
            "domain_id": domain_id,
            "kind": "fit-range",
            "temperature_min": {"magnitude": 303.15, "unit": "kelvin"},
            "temperature_max": {"magnitude": maximum, "unit": "kelvin"},
            "pressure_min": {"magnitude": 66_000.0, "unit": "pascal"},
            "pressure_max": {"magnitude": 102_000.0, "unit": "pascal"},
        }
    ]
    _extend_domain(mapping, domain_id)
    parameterization = config["model"].get("parameterization")
    if parameterization in {"baygi_3b_mea_2b_water", "baygi_3b_mea_4c_water"}:
        _apply_baygi(
            mapping,
            domain_id,
            water_scheme="2b" if parameterization == "baygi_3b_mea_2b_water" else "4c",
        )
    return epcsaft.Parameters.from_mapping(
        mapping, components=("monoethanolamine", "water")
    )


class Evaluator:
    def __init__(
        self,
        parameters: epcsaft.Parameters,
        coordinate_identity: str,
        rows: list[dict[str, str]],
    ) -> None:
        self._parameters = parameters
        self._model = epcsaft.Mixture(parameters)
        self._identity = coordinate_identity
        self._rows = rows
        self._cache: dict[
            float, tuple[np.ndarray, np.ndarray, list[dict[str, object]]]
        ] = {}
        self.phase_evaluations = 0

    def evaluate(
        self, value: float
    ) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
        key = float(value)
        if key in self._cache:
            return self._cache[key]
        active = epcsaft.ActiveParameterSet(
            self._parameters, (self._identity,), values=(key,)
        )
        residuals: list[float] = []
        jacobian: list[float] = []
        records: list[dict[str, object]] = []
        for row in self._rows:
            temperature = float(row["temperature_k"])
            pressure = float(row["pressure_pa"])
            water_x = float(row["water_liquid_mole_fraction"])
            water_y = float(row["water_vapor_mole_fraction"])
            liquid_x = (1.0 - water_x, water_x)
            vapor_y = (1.0 - water_y, water_y)
            liquid = self._model.observable_block(
                active,
                identity="eos.fixed-pressure-fugacity",
                T=temperature * epcsaft.unit_registry.kelvin,
                P=pressure * epcsaft.unit_registry.pascal,
                x=liquid_x,
                phase="liquid",
            )
            vapor = self._model.observable_block(
                active,
                identity="eos.fixed-pressure-fugacity",
                T=temperature * epcsaft.unit_registry.kelvin,
                P=pressure * epcsaft.unit_registry.pascal,
                x=vapor_y,
                phase="vapor",
            )
            self.phase_evaluations += 2
            for index, component_id in enumerate(("monoethanolamine", "water")):
                raw = (
                    math.log(liquid_x[index])
                    + liquid.values[index]
                    - math.log(vapor_y[index])
                    - vapor.values[index]
                )
                scale = math.sqrt(
                    (0.001 / liquid_x[index]) ** 2
                    + (0.001 / vapor_y[index]) ** 2
                    + (133.0 / pressure) ** 2
                    + (0.1 / temperature) ** 2
                )
                derivative = liquid.jacobian[index][0] - vapor.jacobian[index][0]
                residuals.append(raw / scale)
                jacobian.append(derivative / scale)
                records.append(
                    {
                        "row_id": row["row_id"],
                        "source_partition_role": row["role"],
                        "fit_role": row["fit_role"],
                        "component_id": component_id,
                        "temperature_k": temperature,
                        "pressure_pa": pressure,
                        "water_liquid_mole_fraction": water_x,
                        "water_vapor_mole_fraction": water_y,
                        "raw_log_fugacity_residual": raw,
                        "source_error_scale": scale,
                        "normalized_residual": raw / scale,
                        "exact_parameter_derivative": derivative,
                    }
                )
        result = (
            np.asarray(residuals),
            np.asarray(jacobian)[:, np.newaxis],
            records,
        )
        self._cache[key] = result
        return result


def _metrics(
    residuals: np.ndarray,
    records: list[dict[str, object]],
) -> dict[str, object]:
    composition = np.asarray(
        [float(record["water_liquid_mole_fraction"]) for record in records]
    )
    slope = float(np.polyfit(composition, residuals, 1)[0])
    return {
        "residual_count": len(residuals),
        "normalized_rmse": float(np.sqrt(np.mean(residuals**2))),
        "normalized_mae": float(np.mean(np.abs(residuals))),
        "normalized_max_abs": float(np.max(np.abs(residuals))),
        "composition_slope": slope,
    }


def _unavailable_metrics(reason: str) -> dict[str, object]:
    return {
        "status": "unavailable",
        "reason": reason,
        "residual_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = cast(dict[str, Any], json.loads(config_path.read_text(encoding="utf-8")))
    output_stem = cast(str, config.get("output_stem", "cai_mea_water_binary"))
    output = ANALYSIS / f"results/{output_stem}_fit.json"
    table = ANALYSIS / f"results/{output_stem}_predictions.csv"
    source_path = ROOT / config["data"]["path"]
    with source_path.open(newline="", encoding="utf-8") as handle:
        all_rows = list(csv.DictReader(handle))
    admitted_maximum = float(config["data"]["admitted_temperature_max_k"])
    rows_by_id = {row["row_id"]: row for row in all_rows}
    training_ids = cast(list[str], config["data"]["admitted_training_row_ids"])
    selection_ids = cast(list[str], config["data"]["model_selection_row_ids"])
    training = [
        {**rows_by_id[row_id], "fit_role": "binary_training"} for row_id in training_ids
    ]
    model_selection = [
        {**rows_by_id[row_id], "fit_role": "binary_model_selection"}
        for row_id in selection_ids
    ]
    if any(float(row["temperature_k"]) > admitted_maximum for row in training):
        raise ValueError("an admitted training row exceeds the source-qualified domain")
    if any(float(row["temperature_k"]) > admitted_maximum for row in model_selection):
        raise ValueError(
            "an admitted model-selection row exceeds the source-qualified domain"
        )
    if not training:
        raise ValueError("the binary qualification requires at least one admitted row")
    challenges = [
        row
        for row in all_rows
        if row["role"] not in {"pure_endpoint_context"}
        and row["row_id"] not in {*training_ids, *selection_ids}
    ]
    parameters = _parameters(config)
    coordinate = config["active_coordinate"]
    identity = cast(str, coordinate["identity"])
    evaluator = Evaluator(parameters, identity, training)
    started = time.monotonic()
    starts: list[dict[str, object]] = []
    for start in config["multistart"]["starts"]:
        cache: dict[float, tuple[np.ndarray, np.ndarray]] = {}

        def evaluated(value: float) -> tuple[np.ndarray, np.ndarray]:
            if value not in cache:
                residual, jacobian, _ = evaluator.evaluate(value)
                cache[value] = residual, jacobian
            return cache[value]

        result = least_squares(
            lambda values: evaluated(float(values[0]))[0],
            [float(start["value"])],
            jac=lambda values: evaluated(float(values[0]))[1],
            bounds=(
                [float(coordinate["bounds"][0])],
                [float(coordinate["bounds"][1])],
            ),
            x_scale=[float(coordinate["scale"])],
            max_nfev=int(config["optimizer"]["maximum_function_evaluations"]),
            ftol=float(config["optimizer"]["function_tolerance"]),
            gtol=float(config["optimizer"]["gradient_tolerance"]),
            xtol=float(config["optimizer"]["parameter_tolerance"]),
        )
        starts.append(
            {
                "identity": start["identity"],
                "initial_value": start["value"],
                "final_value": float(result.x[0]),
                "cost": float(result.cost),
                "function_evaluations": int(result.nfev),
                "jacobian_evaluations": int(result.njev or 0),
                "optimality": float(result.optimality),
                "success": bool(result.success),
                "status": int(result.status),
                "message": str(result.message),
            }
        )
        print(
            f"{start['identity']}: k_ij={result.x[0]:.12g}, "
            f"nfev={result.nfev}, success={result.success}",
            flush=True,
        )
    fitted_values = np.asarray([float(start["final_value"]) for start in starts])
    selected = float(
        fitted_values[np.argmin([float(start["cost"]) for start in starts])]
    )
    training_residual, training_jacobian, training_records = evaluator.evaluate(
        selected
    )
    selection_evaluator = Evaluator(parameters, identity, model_selection)
    selection_residual, _, selection_records = selection_evaluator.evaluate(selected)
    origin = float(coordinate["origin"])
    origin_training, _, origin_training_records = evaluator.evaluate(origin)
    origin_selection, _, origin_selection_records = selection_evaluator.evaluate(origin)
    singular_values = np.linalg.svd(
        training_jacobian * float(coordinate["scale"]), compute_uv=False
    )
    derivative_checks: list[dict[str, object]] = []
    for row in training[:2]:
        single = Evaluator(parameters, identity, [row])
        step = 1.0e-5
        low, _, _ = single.evaluate(selected - step)
        center, exact, records = single.evaluate(selected)
        high, _, _ = single.evaluate(selected + step)
        numerical = (high - low) / (2.0 * step)
        relative = np.abs(exact[:, 0] - numerical) / np.maximum(1.0, np.abs(numerical))
        derivative_checks.append(
            {
                "row_id": row["row_id"],
                "roles": [record["component_id"] for record in records],
                "exact": exact[:, 0].tolist(),
                "central_difference": numerical.tolist(),
                "maximum_scaled_relative_error": float(np.max(relative)),
                "center_values": center.tolist(),
            }
        )
    training_metrics = _metrics(training_residual, training_records)
    selection_metrics = (
        _metrics(selection_residual, selection_records)
        if model_selection
        else _unavailable_metrics(
            cast(str, config["data"]["pressure_level_validation_status"])
        )
    )
    gates = {
        "all_admitted_rows_evaluated": len(training_records) == 2 * len(training),
        "rank": int(np.linalg.matrix_rank(training_jacobian)) == 1,
        "condition_number": 1.0 <= float(config["gates"]["maximum_condition_number"]),
        "strictly_interior": float(coordinate["bounds"][0])
        < selected
        < float(coordinate["bounds"][1]),
        "all_starts_same_solution": float(np.ptp(fitted_values))
        <= float(config["multistart"]["same_solution_tolerance"]),
        "training_normalized_rmse": float(training_metrics["normalized_rmse"])
        <= float(config["gates"]["training_normalized_rmse_maximum"]),
        "independent_pressure_level_validation": bool(model_selection),
        "model_selection_normalized_rmse": bool(model_selection)
        and float(selection_metrics["normalized_rmse"])
        <= float(
            config["gates"].get("model_selection_normalized_rmse_maximum", math.inf)
        ),
        "model_selection_not_worse_than_training": bool(model_selection)
        and float(selection_metrics["normalized_rmse"])
        <= float(
            config["gates"].get(
                "model_selection_not_worse_than_training_factor", math.inf
            )
        )
        * float(training_metrics["normalized_rmse"]),
        "no_material_composition_trend": abs(
            max(
                [float(training_metrics["composition_slope"])]
                + (
                    [float(selection_metrics["composition_slope"])]
                    if model_selection
                    else []
                ),
                key=abs,
            )
        )
        <= 1.0,
        "exact_jacobian_check": max(
            float(check["maximum_scaled_relative_error"]) for check in derivative_checks
        )
        <= float(config["gates"]["exact_jacobian_check_relative_tolerance"]),
    }
    payload: dict[str, object] = {
        "schema_version": 1,
        "identity": f"{config['identity']}-result",
        "claim_status": "independent_neutral_binary_diagnostic",
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "source_csv_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "engine": json.loads(ENGINE_LOCK.read_text(encoding="utf-8")),
        "parameter_fingerprint": parameters.fingerprint,
        "parameter_mapping_sha256": _canonical_sha256(parameters.to_mapping()),
        "active_coordinate": coordinate,
        "accounting": {
            "source_rows": len(all_rows),
            "admitted_training_rows": len(training),
            "admitted_model_selection_rows": len(model_selection),
            "domain_challenge_rows": len(challenges),
            "pure_endpoint_context_rows": sum(
                row["role"] == "pure_endpoint_context" for row in all_rows
            ),
            "optimizer_phase_evaluations": evaluator.phase_evaluations,
            "selection_phase_evaluations": selection_evaluator.phase_evaluations,
            "numeric_failure_penalties": 0,
        },
        "starts": starts,
        "selected_value": selected,
        "training_metrics": training_metrics,
        "model_selection_metrics": selection_metrics,
        "origin_metrics": {
            "training_normalized_rmse": float(np.sqrt(np.mean(origin_training**2))),
            "model_selection_normalized_rmse": (
                float(np.sqrt(np.mean(origin_selection**2)))
                if model_selection
                else None
            ),
        },
        "rank": int(np.linalg.matrix_rank(training_jacobian)),
        "singular_values_affine": singular_values.tolist(),
        "condition_number": 1.0,
        "active_bounds": [],
        "covariance": {
            "status": "unavailable_missing_component_covariance_and_statistical_uncertainty_model",
            "degrees_of_freedom": None,
        },
        "derivative_checks": derivative_checks,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "promotion_decision": "not_promoted",
        "promotion_reason": (
            "all gates passed but generic Regression ownership is absent"
            if all(gates.values())
            else "one or more preregistered scientific gates failed"
        ),
        "pressure_level_validation_status": config["data"][
            "pressure_level_validation_status"
        ],
        "runtime_seconds": time.monotonic() - started,
        "domain_challenge_row_ids": [row["row_id"] for row in challenges],
    }
    payload["receipt_sha256"] = _canonical_sha256(payload)
    output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with table.open("w", newline="", encoding="utf-8") as handle:
        plotted_records = [
            {
                **record,
                "parameter_state": "retained_origin",
                "k_ij_mea_water": origin,
                "claim_status": "diagnostic_non_promotable",
            }
            for record in [*origin_training_records, *origin_selection_records]
        ] + [
            {
                **record,
                "parameter_state": "fitted_diagnostic",
                "k_ij_mea_water": selected,
                "claim_status": "diagnostic_non_promotable",
            }
            for record in [*training_records, *selection_records]
        ]
        columns = tuple(plotted_records[0])
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(plotted_records)
    print(output.relative_to(ROOT))
    print(table.relative_to(ROOT))


if __name__ == "__main__":
    main()
