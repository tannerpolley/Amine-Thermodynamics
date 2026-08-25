from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import statistics
import time

import epcsaft
from epcsaft import equilibrium

from generate import CHARGES, _canonical_sha256, _configuration, _write_csv
from MEA.common.analysis_io import read_csv_rows as _read
from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


ANALYSIS = Path(__file__).resolve().parents[1]
REPO = ANALYSIS.parents[3]
PRESSURE_PACKET = (
    REPO
    / "analyses/phase3/ionic_epcsaft_regression/pressure_first/results/pressure_candidate_packet.csv"
)
HAJJ_TABLE = ANALYSIS / "inputs/hajj_2024_table1.csv"
PRIOR_SUMMARY = ANALYSIS / "results/ion_coefficient_blocks/summary.json"
RESULTS = ANALYSIS / "results/broader_candidate"
BASE_COEFFICIENTS = {
    "protonated-monoethanolamine": 7.01,
    "carbamate-anion": 7.01,
    "bicarbonate-anion": 7.01,
    "carbonate-anion": 7.01,
    "hydronium-cation": 9.55,
    "hydroxide-anion": 13.96,
}
SELECTED_COEFFICIENTS = {
    **BASE_COEFFICIENTS,
    "protonated-monoethanolamine": 2.60,
    "bicarbonate-anion": 7.89,
    "carbonate-anion": 7.89,
}
CASES = (
    ("baseline_7_01", "H+/OH- source values; remaining ions 7.01", BASE_COEFFICIENTS, False),
    (
        "selected_ion_specific",
        "MEAH+ 2.60; HCO3-/CO3^2- 7.89; MEACOO- 7.01",
        SELECTED_COEFFICIENTS,
        False,
    ),
    (
        "selected_water_temperature",
        "Selected ion-specific set; Archer-Wang water permittivity",
        SELECTED_COEFFICIENTS,
        True,
    ),
)
OLD_DOMAIN = "mea-tracer-313-15-k-fit-range"
BROADER_DOMAIN = "mea-diagnostic-293-15-to-393-15-k"


def _broader_parameters(
    coefficients: dict[str, float],
    water_temperature_correlation: bool,
) -> tuple[epcsaft.Parameters, dict[str, object]]:
    _, mapping = _configuration(
        "ion-specific-suppression", 1.0, 1.0, True, coefficients
    )

    def replace_domain(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "domain_id" and item == OLD_DOMAIN:
                    value[key] = BROADER_DOMAIN
                else:
                    replace_domain(item)
        elif isinstance(value, list):
            for item in value:
                replace_domain(item)

    replace_domain(mapping)
    mapping["domains"] = [
        {
            "domain_id": BROADER_DOMAIN,
            "kind": "fit-range",
            "temperature_min": {"magnitude": 293.15, "unit": "kelvin"},
            "temperature_max": {"magnitude": 393.15, "unit": "kelvin"},
            "pressure_min": {"magnitude": 10.0, "unit": "pascal"},
            "pressure_max": {"magnitude": 300_000.0, "unit": "pascal"},
        }
    ]
    if water_temperature_correlation:
        mapping["sources"].append(
            {
                "source_id": "uyan-2015-permittivity-transfer",
                "citation": "Uyan Eq. 5; Wangler campaign Archer-Wang approximation.",
                "use_basis": "Explicit transfer approximation, not an exact Floriano-Nascimento replay.",
            }
        )
        water = next(
            item for item in mapping["components"] if item["component_id"] == "water"
        )
        water["coefficients"] = [
            item
            for item in water["coefficients"]
            if item["family"] != "relative_permittivity"
        ]
        reference_temperature = 298.15
        quadratic = 7.6555618295e-4
        linear = -8.1783881423e-1
        constant = (
            quadratic * reference_temperature**2
            + linear * reference_temperature
            + 254.19616803
        )
        mapping["correlations"].append(
            {
                "correlation_id": "component/water/relative_permittivity/constant-plus-polynomial-in-temperature",
                "component_id": "water",
                "family": "relative_permittivity",
                "form": "constant-plus-polynomial-in-temperature",
                "independent_variables": ["temperature"],
                "constant": {
                    "identity": "component/water/relative_permittivity/constant-plus-polynomial-in-temperature/constant",
                    "value": {"magnitude": constant, "unit": "dimensionless"},
                },
                "reference_temperature": {
                    "magnitude": reference_temperature,
                    "unit": "kelvin",
                },
                "terms": [
                    {
                        "power": 1,
                        "coefficient": {
                            "identity": "component/water/relative_permittivity/constant-plus-polynomial-in-temperature/term-0/coefficient",
                            "value": {
                                "magnitude": 2.0 * quadratic * reference_temperature + linear,
                                "unit": "1 / kelvin",
                            },
                        },
                    },
                    {
                        "power": 2,
                        "coefficient": {
                            "identity": "component/water/relative_permittivity/constant-plus-polynomial-in-temperature/term-1/coefficient",
                            "value": {
                                "magnitude": quadratic,
                                "unit": "1 / kelvin ** 2",
                            },
                        },
                    },
                ],
                "provenance": {
                    "source_id": "uyan-2015-permittivity-transfer",
                    "locator": "Engine Validation Archer-Wang water approximation at Tref=298.15 K",
                    "domain_id": BROADER_DOMAIN,
                },
            }
        )
    return epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS), mapping


def _pressure_rows() -> list[dict[str, str]]:
    rows = _read(PRESSURE_PACKET)
    result: list[dict[str, str]] = []
    for temperature_c, source in (
        (40.0, "Hilliard2008"),
        (60.0, "Hilliard2008"),
        (80.0, "Jou1995"),
        (100.0, "Jou1995"),
        (120.0, "Jou1995"),
    ):
        group = sorted(
            (
                row
                for row in rows
                if math.isclose(float(row["mea_mass_fraction"]), 0.30)
                and math.isclose(float(row["temperature_reported_C"]), temperature_c)
                and row["source_key"] == source
            ),
            key=lambda row: float(row["co2_loading_mol_per_mol_mea"]),
        )
        if len(group) < 3:
            raise RuntimeError(f"pressure group missing: {temperature_c:g} C, {source}")
        result.extend(group[index] for index in (0, len(group) // 2, len(group) - 1))
    return result


def _evaluate_state(
    parameters: epcsaft.Parameters,
    configuration_id: str,
    family: str,
    row_id: str,
    temperature_k: float,
    pressure_pa: float,
    loading: float,
    initial_reference: object | None,
) -> tuple[dict[str, object], object | None]:
    started = time.monotonic()
    error: Exception | None = None
    for budget, reference in ((2, initial_reference), (5, None)):
        try:
            problem = build_homogeneous_reactive_problem(
                parameters,
                identity=f"broader-{configuration_id}-{family}-{row_id}",
                phase_identity="mea-nine-species-liquid",
                continuation_identity=f"broader-{configuration_id}-{family}",
                temperature_k=temperature_k,
                pressure_pa=pressure_pa,
                mea_mass_fraction_unloaded=0.30,
                loading_mol_co2_per_mol_mea=loading,
                maximum_log_composition_distance=2.0,
                maximum_log_volume_distance=2.0,
                solver_options={
                    "maximum_iterations": 50,
                    "convergence_tolerance": 1.0e-6,
                    "primary_start_budget": budget,
                },
                allow_reaction_extrapolation=True,
                initial_reference=reference,
            )
            descriptor = equilibrium.homogeneous_reactive_observation_descriptor(
                problem,
                (
                    equilibrium.HomogeneousReactiveObservationRow(
                        "co2-liquid-fugacity",
                        "fugacity_pa",
                        (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                        support="positive",
                    ),
                ),
            )
            evaluated = equilibrium.evaluate_homogeneous_reactive_observations(
                problem,
                temperature_k * epcsaft.unit_registry.kelvin,
                pressure_pa * epcsaft.unit_registry.pascal,
                descriptor,
            )
            if evaluated.status != "evaluated" or evaluated.state is None:
                raise RuntimeError(str(evaluated.failure or "state evaluation failed"))
            model_state = epcsaft.Mixture(parameters).state(
                T=temperature_k * epcsaft.unit_registry.kelvin,
                rho=evaluated.state.molar_density_mol_per_m3
                * epcsaft.unit_registry.mole
                / epcsaft.unit_registry.meter**3,
                x=evaluated.state.mole_fractions,
            )
            diagnostics = evaluated.diagnostics
            assert diagnostics is not None
            return (
                {
                    "configuration_id": configuration_id,
                    "family": family,
                    "row_id": row_id,
                    "temperature_k": temperature_k,
                    "pressure_pa": pressure_pa,
                    "co2_loading_mol_per_mol_mea": loading,
                    "status": "evaluated",
                    "runtime_seconds": time.monotonic() - started,
                    "co2_liquid_fugacity_pa": evaluated.rows[0].value,
                    "bulk_relative_permittivity": model_state.bulk_relative_permittivity,
                    "molar_density_mol_m3": evaluated.state.molar_density_mol_per_m3,
                    "ion_mole_fraction": math.fsum(
                        x
                        for x, charge in zip(
                            evaluated.state.mole_fractions, CHARGES, strict=True
                        )
                        if charge
                    ),
                    "balance_inf_norm": diagnostics.balance_inf_norm,
                    "charge_inf_norm": diagnostics.charge_inf_norm,
                    "reaction_affinity_inf_norm": diagnostics.reaction_affinity_inf_norm,
                    "pressure_relative_residual": diagnostics.pressure_relative_residual,
                    "failure": "",
                },
                problem.continuation_reference,
            )
        except (RuntimeError, ValueError, equilibrium.ChemicalEquilibriumError) as caught:
            error = caught
    assert error is not None
    return (
        {
            "configuration_id": configuration_id,
            "family": family,
            "row_id": row_id,
            "temperature_k": temperature_k,
            "pressure_pa": pressure_pa,
            "co2_loading_mol_per_mol_mea": loading,
            "status": "non_evaluable",
            "runtime_seconds": time.monotonic() - started,
            "co2_liquid_fugacity_pa": "",
            "bulk_relative_permittivity": "",
            "molar_density_mol_m3": "",
            "ion_mole_fraction": "",
            "balance_inf_norm": "",
            "charge_inf_norm": "",
            "reaction_affinity_inf_norm": "",
            "pressure_relative_residual": "",
            "failure": str(error),
        },
        None,
    )


def _run_case(
    case: tuple[str, str, dict[str, float], bool],
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    configuration_id, name, coefficients, water_temperature_correlation = case
    parameters, mapping = _broader_parameters(
        coefficients, water_temperature_correlation
    )
    pressure_results: list[dict[str, object]] = []
    previous = None
    previous_temperature = None
    for row in _pressure_rows():
        temperature_k = float(row["temperature_K"])
        if temperature_k != previous_temperature:
            previous = None
            previous_temperature = temperature_k
        result, previous = _evaluate_state(
            parameters,
            configuration_id,
            "pressure",
            row["observation_id"],
            temperature_k,
            float(row["state_pressure_pa"]),
            float(row["co2_loading_mol_per_mol_mea"]),
            previous,
        )
        result.update(
            {
                "configuration_name": name,
                "source_key": row["source_key"],
                "temperature_c": float(row["temperature_reported_C"]),
                "observed_pco2_pa": float(row["observed_pco2_pa"]),
                "source_row_identity": row["source_row_identity"],
            }
        )
        if result["status"] == "evaluated":
            result["ln_model_over_observed"] = math.log(
                float(result["co2_liquid_fugacity_pa"])
                / float(result["observed_pco2_pa"])
            )
        else:
            result["ln_model_over_observed"] = ""
        pressure_results.append(result)
        print(json.dumps({"configuration": configuration_id, "family": "pressure", "row": result["row_id"], "status": result["status"]}), flush=True)

    dielectric_results: list[dict[str, object]] = []
    previous_loading = None
    previous = None
    for index, row in enumerate(
        sorted(
            _read(HAJJ_TABLE),
            key=lambda item: (
                float(item["co2_loading_mol_per_mol_mea"]),
                float(item["temperature_k"]),
            ),
        )
    ):
        loading = float(row["co2_loading_mol_per_mol_mea"])
        if loading != previous_loading:
            previous = None
            previous_loading = loading
        result, previous = _evaluate_state(
            parameters,
            configuration_id,
            "dielectric",
            f"hajj-{index + 1:02d}",
            float(row["temperature_k"]),
            101_325.0,
            loading,
            previous,
        )
        result.update(
            {
                "configuration_name": name,
                "source_id": row["source_id"],
                "doi": row["doi"],
                "source_locator": row["source_locator"],
                "temperature_c": float(row["temperature_c"]),
                "fitted_static_relative_permittivity": float(
                    row["fitted_static_relative_permittivity"]
                ),
                "measurement_classification": row["measurement_classification"],
            }
        )
        if result["status"] == "evaluated":
            result["model_minus_fitted_static_permittivity"] = float(
                result["bulk_relative_permittivity"]
            ) - float(result["fitted_static_relative_permittivity"])
        else:
            result["model_minus_fitted_static_permittivity"] = ""
        dielectric_results.append(result)
        print(json.dumps({"configuration": configuration_id, "family": "dielectric", "row": result["row_id"], "status": result["status"]}), flush=True)
    return (
        {
            "configuration_id": configuration_id,
            "configuration_name": name,
            "parameter_mapping_sha256": _canonical_sha256(mapping),
            "coefficients": coefficients,
            "water_permittivity": (
                "Archer-Wang temperature correlation"
                if water_temperature_correlation
                else "constant 78.09"
            ),
        },
        pressure_results,
        dielectric_results,
    )


def _metrics(rows: list[dict[str, object]], residual: str) -> dict[str, object]:
    evaluated = [row for row in rows if row["status"] == "evaluated"]
    values = [float(row[residual]) for row in evaluated]
    return {
        "evaluated_count": len(evaluated),
        "failed_count": len(rows) - len(evaluated),
        "rmse": math.sqrt(math.fsum(value * value for value in values) / len(values)) if values else None,
        "median_absolute": statistics.median(abs(value) for value in values) if values else None,
        "maximum_balance_inf_norm": max((float(row["balance_inf_norm"]) for row in evaluated), default=None),
        "maximum_reaction_affinity_inf_norm": max((float(row["reaction_affinity_inf_norm"]) for row in evaluated), default=None),
    }


def _write_best_candidate(summary: dict[str, object]) -> None:
    _, mapping = _broader_parameters(SELECTED_COEFFICIENTS, True)
    path = RESULTS / "best_fixed_candidate_parameters.json"
    path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["best_fixed_candidate"] = {
        "configuration_id": "selected_water_temperature",
        "parameter_mapping": str(path.relative_to(REPO)),
        "parameter_mapping_sha256": _canonical_sha256(mapping),
        "classification": "best fixed structure in this sensitivity screen; not a completed global fit",
    }


def main() -> None:
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=2) as executor:
        completed = list(executor.map(_run_case, CASES))
    parameters = [item[0] for item in completed]
    pressure_rows = [row for item in completed for row in item[1]]
    dielectric_rows = [row for item in completed for row in item[2]]
    parameter_rows = [
        {
            "configuration_id": item["configuration_id"],
            "configuration_name": item["configuration_name"],
            "parameter_mapping_sha256": item["parameter_mapping_sha256"],
            "water_permittivity": item["water_permittivity"],
            "component_id": component,
            "ion_specific_suppression_coefficient": value,
        }
        for item in parameters
        for component, value in item["coefficients"].items()
    ]
    RESULTS.mkdir(parents=True, exist_ok=True)
    _write_csv(RESULTS / "pressure_comparison.csv", pressure_rows)
    _write_csv(RESULTS / "dielectric_comparison.csv", dielectric_rows)
    _write_csv(RESULTS / "configuration_parameters.csv", parameter_rows)
    prior = json.loads(PRIOR_SUMMARY.read_text(encoding="utf-8"))
    summary = {
        "schema": "mea.broader-ion-specific-candidate.v1",
        "status": "completed",
        "engine_wheel_path": prior["engine_wheel_path"],
        "engine_wheel_sha256": prior["engine_wheel_sha256"],
        "worker_count": 2,
        "solver_maximum_iterations": 50,
        "solver_convergence_tolerance": 1.0e-6,
        "reaction_extrapolation_above_323_15_k": True,
        "parameter_domain_extension": {
            "status": "analysis_only_not_source_qualification",
            "domain_id": BROADER_DOMAIN,
            "temperature_range_k": [293.15, 393.15],
            "pressure_range_pa": [10.0, 300000.0],
        },
        "pressure_comparison": "diagnostic fixed-pressure neutral-CO2 liquid fugacity",
        "dielectric_comparison": "Hajj 2024 Table 1 Cole-Cole fitted static limit; not direct DC permittivity",
        "runtime_seconds": time.monotonic() - started,
        "configurations": [
            {
                **item,
                "pressure_metrics": {
                    **_metrics(
                        [row for row in pressure_rows if row["configuration_id"] == item["configuration_id"]],
                        "ln_model_over_observed",
                    ),
                    "typical_factor": (
                        None
                        if _metrics(
                            [row for row in pressure_rows if row["configuration_id"] == item["configuration_id"]],
                            "ln_model_over_observed",
                        )["median_absolute"]
                        is None
                        else math.exp(
                            _metrics(
                                [row for row in pressure_rows if row["configuration_id"] == item["configuration_id"]],
                                "ln_model_over_observed",
                            )["median_absolute"]
                        )
                    ),
                },
                "dielectric_metrics": _metrics(
                    [row for row in dielectric_rows if row["configuration_id"] == item["configuration_id"]],
                    "model_minus_fitted_static_permittivity",
                ),
            }
            for item in parameters
        ],
    }
    _write_best_candidate(summary)
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
