from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import statistics
from pathlib import Path

import epcsaft
from shared_evaluation import (
    ENGINE_WHEEL,
    ENGINE_WHEEL_SHA256,
    installed_wheel,
    sha256,
    evaluate_state,
    anchor_from,
)


ANALYSIS = Path(__file__).resolve().parents[1]
STATE_PACKET = ANALYSIS / "data/input/state-packet.json"
RESULTS = ANALYSIS / "results/permittivity-comparison"
VARIANTS = {
    "current_ion_specific": "ion-specific-suppression",
    "schick_temperature_mixing": "component-permittivity-mixing",
    "uyan_co2_excluding": "solvent-only",
}
SCHICK_SOURCE_ID = "schick-et-al-2023"
SCHICK_SOURCE_DOI = "10.1016/j.fluid.2022.113714"
SCHICK_SOURCE_SHA256 = (
    "sha256:958d21b21def89c9d704a0844a01c506809f3a86b5405bda4e07b05d7a3939d3"
)
UYAN_SOURCE_ID = "uyan-2015-permittivity-transfer"
UYAN_SOURCE_DOI = "10.1016/j.fluid.2015.02.026"
UYAN_SOURCE_SHA256 = (
    "sha256:1ae7cabd2a7b84f7c543999106be3fa4387e566739cb8defb5e567405b20d9d6"
)


def ion_permittivity_record(component_id: str) -> dict[str, object]:
    return {
        "candidate_domain_id": "mea-candidate-293-15-to-393-15-k",
        "family": "relative_permittivity",
        "identity": f"component/{component_id}/relative_permittivity",
        "provenance": {
            "domain_id": "mea-diagnostic-293-15-to-393-15-k",
            "locator": "Schick et al. 2023 Table 2, PDF page 4: ion epsilon_r=8",
            "source_id": SCHICK_SOURCE_ID,
        },
        "qualification": "candidate_extrapolation",
        "source_sha256": SCHICK_SOURCE_SHA256,
        "value": {"magnitude": 8.0, "unit": "dimensionless"},
    }


def variant_parameters(
    source: dict[str, object], variant_id: str
) -> epcsaft.Parameters:
    mapping = copy.deepcopy(source)
    choice = VARIANTS[variant_id]
    if variant_id == "current_ion_specific":
        return epcsaft.Parameters.from_mapping(mapping)
    next(
        family
        for family in mapping["model_families"]
        if family["kind"] == "permittivity"
    )["choice"] = choice

    if choice == "component-permittivity-mixing":
        mapping["sources"].append(
            {
                "citation": (
                    "Schick et al. (2023), Fluid Phase Equilibria 567, 113714, "
                    "doi:10.1016/j.fluid.2022.113714"
                ),
                "source_id": SCHICK_SOURCE_ID,
                "use_basis": (
                    "Controlled transfer of Table 2 CO2 permittivity and ion "
                    "epsilon_r=8 into the current MEA parameter foundation."
                ),
            }
        )

    for component in mapping["components"]:
        component["coefficients"] = [
            coefficient
            for coefficient in component["coefficients"]
            if coefficient["family"] != "ion_specific_suppression_coefficient"
            and not (
                component["component_id"] == "carbon-dioxide"
                and coefficient["family"] == "relative_permittivity"
            )
        ]
        charge = component["fixed"]["charge_number"]["value"]["magnitude"]
        if choice == "component-permittivity-mixing" and charge != 0:
            component["coefficients"].append(
                ion_permittivity_record(component["component_id"])
            )

    if choice == "component-permittivity-mixing":
        mapping["correlations"].append(
            {
                "candidate_domain_id": "mea-candidate-293-15-to-393-15-k",
                "component_id": "carbon-dioxide",
                "constant": {
                    "identity": (
                        "component/carbon-dioxide/relative_permittivity/"
                        "constant-plus-polynomial-in-temperature/constant"
                    ),
                    "value": {"magnitude": 1.4122, "unit": "dimensionless"},
                },
                "correlation_id": (
                    "component/carbon-dioxide/relative_permittivity/"
                    "constant-plus-polynomial-in-temperature"
                ),
                "family": "relative_permittivity",
                "form": "constant-plus-polynomial-in-temperature",
                "independent_variables": ["temperature"],
                "provenance": {
                    "domain_id": "mea-diagnostic-293-15-to-393-15-k",
                    "locator": "Schick et al. 2023 Table 2, PDF page 4",
                    "source_id": SCHICK_SOURCE_ID,
                },
                "qualification": "candidate_extrapolation",
                "reference_temperature": {"magnitude": 293.0, "unit": "kelvin"},
                "source_sha256": SCHICK_SOURCE_SHA256,
                "terms": [
                    {
                        "coefficient": {
                            "identity": (
                                "component/carbon-dioxide/relative_permittivity/"
                                "constant-plus-polynomial-in-temperature/"
                                "term-0/coefficient"
                            ),
                            "value": {
                                "magnitude": -0.0036,
                                "unit": "1 / kelvin",
                            },
                        },
                        "power": 1,
                    }
                ],
            }
        )
    return epcsaft.Parameters.from_mapping(mapping)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(parameter_path: Path) -> None:
    assert sha256(ENGINE_WHEEL) == ENGINE_WHEEL_SHA256
    assert sha256(installed_wheel()) == ENGINE_WHEEL_SHA256
    source_parameters = json.loads(parameter_path.read_text(encoding="utf-8"))
    packet = json.loads(STATE_PACKET.read_text(encoding="utf-8"))
    RESULTS.mkdir(parents=True, exist_ok=True)
    target_path = RESULTS / "permittivity-formulation-targets.csv"
    state_path = RESULTS / "permittivity-formulation-states.csv"
    target_rows = []
    state_rows = []

    def checkpoint() -> None:
        write_csv(target_path, target_rows)
        write_csv(state_path, state_rows)

    summary: dict[str, object] = {
        "question": (
            "Select the live permittivity treatment by comparing the current "
            "ion-specific formulation, all-component mixing, and solvent-only "
            "mass-fraction mixing over every retained pressure and speciation state."
        ),
        "parameter_input": str(parameter_path.resolve()),
        "parameter_sha256": sha256(parameter_path),
        "immutable_state_input": str(STATE_PACKET.relative_to(ANALYSIS)),
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "state_selection": (
            "all 79 pressure states across 313.15-393.15 K and all 44 "
            "speciation states across 293.15-353.15 K"
        ),
        "variant_provenance": {
            "current_ion_specific": {
                "classification": "retained baseline",
                "scope": (
                    "Unmodified frozen-foundation parameter document using its "
                    "ion-specific-suppression permittivity choice."
                ),
            },
            "schick_temperature_mixing": {
                "classification": "derived transfer",
                "source_doi": SCHICK_SOURCE_DOI,
                "source_id": SCHICK_SOURCE_ID,
                "source_sha256": SCHICK_SOURCE_SHA256,
                "scope": (
                    "Schick CO2 temperature correlation and component mixing "
                    "with ion epsilon_r=8, retaining the current bundle's water input"
                ),
            },
            "uyan_co2_excluding": {
                "classification": "derived transfer",
                "source_doi": UYAN_SOURCE_DOI,
                "source_id": UYAN_SOURCE_ID,
                "source_sha256": UYAN_SOURCE_SHA256,
                "scope": (
                    "Solvent-only mass-fraction rule using the current bundle's "
                    "constant MEA epsilon_r=32 and water input"
                ),
            },
        },
        "variants": {},
    }

    observations = packet["observations"]
    variant_mappings: dict[str, dict[str, object]] = {}
    for variant_id in VARIANTS:
        parameters = variant_parameters(source_parameters, variant_id)
        variant_mappings[variant_id] = parameters.to_mapping()
        model = epcsaft.Mixture(parameters)
        failures = 0
        evaluated = 0
        anchors = []
        reactions = {
            spec.identity: float(spec.value.magnitude)
            for spec in parameters.parameter_specs
            if spec.identity.startswith("reaction:")
        }
        for index, observation in enumerate(observations, start=1):
            family = "pressure" if len(observation["targets"]) == 1 else "speciation"
            temperature_k = float(observation["request"]["temperature"]["value"])
            loading = float(
                observation["request"]["reaction_system"]["feed_amounts_mol"][0]
            )
            record = evaluate_state(
                model,
                observation["request"],
                reactions,
                f"{observation['identity']}-{variant_id}",
                anchors,
                budget_s=45,
            )
            status = record["status"]
            if status != "evaluated":
                failures += 1
                state_rows.append(
                    {
                        "variant_id": variant_id,
                        "observation_id": observation["identity"],
                        "family": family,
                        "temperature_k": temperature_k,
                        "loading_mol_co2_per_mol_mea": loading,
                        "status": status,
                        "failure_code": record["failure_code"],
                        "failure_diagnostic": record["failure_diagnostic"],
                        "parameter_fingerprint": parameters.fingerprint,
                        "bulk_relative_permittivity": "",
                        "born_a_over_rt": "",
                    }
                )
                checkpoint()
                continue

            evaluated += 1
            liquid = anchor_from(record)
            if family == "pressure":
                anchors.append(liquid)
            state = model.state(
                T=temperature_k * epcsaft.unit_registry.kelvin,
                rho=(1.0 / liquid.molar_volume_m3_per_mol)
                * epcsaft.unit_registry.mole
                / epcsaft.unit_registry.meter**3,
                x=liquid.mole_fractions,
            )
            state_rows.append(
                {
                    "variant_id": variant_id,
                    "observation_id": observation["identity"],
                    "family": family,
                    "temperature_k": temperature_k,
                    "loading_mol_co2_per_mol_mea": loading,
                    "status": status,
                    "failure_code": "",
                    "failure_diagnostic": "",
                    "parameter_fingerprint": parameters.fingerprint,
                    "bulk_relative_permittivity": state.bulk_relative_permittivity,
                    "born_a_over_rt": state.born,
                }
            )
            predictions = record["predictions"]
            for target in observation["targets"]:
                predicted = predictions[target["prediction_identity"]]
                observed = float(target["observed"])
                target_rows.append(
                    {
                        "variant_id": variant_id,
                        "observation_id": observation["identity"],
                        "family": family,
                        "temperature_k": temperature_k,
                        "loading_mol_co2_per_mol_mea": loading,
                        "target_id": target["identity"],
                        "observed": observed,
                        "predicted": predicted,
                        "log10_predicted_over_observed": (
                            math.log10(predicted / observed)
                            if predicted > 0.0 and observed > 0.0
                            else ""
                        ),
                    }
                )
            print(
                f"{variant_id}: {index:02d}/{len(observations)} {status}",
                flush=True,
            )
            checkpoint()

        metrics: dict[str, object] = {
            "attempted_states": len(observations),
            "evaluated_states": evaluated,
            "failed_states": failures,
            "parameter_fingerprint": parameters.fingerprint,
        }
        for family in ("pressure", "speciation"):
            family_rows = [
                row
                for row in target_rows
                if row["variant_id"] == variant_id
                and row["family"] == family
                and row["log10_predicted_over_observed"] != ""
            ]
            errors = [
                float(row["log10_predicted_over_observed"]) for row in family_rows
            ]
            metrics[f"{family}_positive_targets"] = len(errors)
            metrics[f"{family}_log10_rmse"] = (
                math.sqrt(math.fsum(error * error for error in errors) / len(errors))
                if errors
                else None
            )
            metrics[f"{family}_median_log10_bias"] = (
                statistics.median(errors) if errors else None
            )
            by_temperature: dict[float, list[float]] = {}
            for row in family_rows:
                by_temperature.setdefault(float(row["temperature_k"]), []).append(
                    float(row["log10_predicted_over_observed"])
                )
            temperature_mse = {
                str(temperature): math.fsum(error * error for error in values)
                / len(values)
                for temperature, values in sorted(by_temperature.items())
            }
            metrics[f"{family}_per_temperature_log10_rmse"] = {
                temperature: math.sqrt(value)
                for temperature, value in temperature_mse.items()
            }
            metrics[f"{family}_temperature_balanced_log10_rmse"] = (
                math.sqrt(math.fsum(temperature_mse.values()) / len(temperature_mse))
                if temperature_mse
                else None
            )
            family_states = [
                row
                for row in state_rows
                if row["variant_id"] == variant_id and row["family"] == family
            ]
            metrics[f"{family}_attempted_states"] = len(family_states)
            metrics[f"{family}_evaluated_states"] = sum(
                row["status"] == "evaluated" for row in family_states
            )
        epsilon = [
            float(row["bulk_relative_permittivity"])
            for row in state_rows
            if row["variant_id"] == variant_id
            and row["bulk_relative_permittivity"] != ""
        ]
        metrics["bulk_relative_permittivity_min"] = min(epsilon, default=None)
        metrics["bulk_relative_permittivity_median"] = (
            statistics.median(epsilon) if epsilon else None
        )
        metrics["bulk_relative_permittivity_max"] = max(epsilon, default=None)
        summary["variants"][variant_id] = metrics
        checkpoint()

    paired: dict[str, object] = {}
    for family in ("pressure", "speciation"):
        target_pairs: dict[tuple[str, str], dict[str, dict[str, object]]] = {}
        for row in target_rows:
            if row["family"] != family:
                continue
            key = (str(row["observation_id"]), str(row["target_id"]))
            target_pairs.setdefault(key, {})[str(row["variant_id"])] = row
        wins = {"schick_temperature_mixing": 0, "uyan_co2_excluding": 0}
        log_ratios: list[float] = []
        for pair in target_pairs.values():
            if not {
                "schick_temperature_mixing",
                "uyan_co2_excluding",
            }.issubset(pair):
                continue
            schick = pair["schick_temperature_mixing"]
            uyan = pair["uyan_co2_excluding"]
            schick_error = abs(float(schick["log10_predicted_over_observed"]))
            uyan_error = abs(float(uyan["log10_predicted_over_observed"]))
            winner = (
                "schick_temperature_mixing"
                if schick_error < uyan_error
                else "uyan_co2_excluding"
            )
            wins[winner] += 1
            log_ratios.append(
                math.log10(float(schick["predicted"]) / float(uyan["predicted"]))
            )
        paired[family] = {
            "paired_targets": len(log_ratios),
            "closer_target_counts": wins,
            "median_log10_schick_over_uyan": statistics.median(log_ratios)
            if log_ratios
            else None,
            "minimum_log10_schick_over_uyan": min(log_ratios, default=None),
            "maximum_log10_schick_over_uyan": max(log_ratios, default=None),
        }
    summary["paired_comparison"] = paired

    if any(metrics["failed_states"] for metrics in summary["variants"].values()):
        summary["candidate_selection"] = {
            "status": "incomplete",
            "reason": "Failed states prevent candidate selection; any prior candidate is historical.",
        }
        checkpoint()
        (RESULTS / "permittivity-formulation-comparison.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return

    baseline = summary["variants"]["current_ion_specific"]
    best_speciation = min(
        variant["speciation_temperature_balanced_log10_rmse"]
        for variant in summary["variants"].values()
        if variant["speciation_evaluated_states"] == 44
    )
    eligible: list[str] = []
    for variant_id, metrics in summary["variants"].items():
        pressure_guardrail = all(
            metrics["pressure_per_temperature_log10_rmse"][temperature]
            <= 1.10 * baseline["pressure_per_temperature_log10_rmse"][temperature]
            for temperature in baseline["pressure_per_temperature_log10_rmse"]
        )
        speciation_guardrail = (
            metrics["speciation_evaluated_states"] == 44
            and metrics["speciation_temperature_balanced_log10_rmse"]
            <= 1.10 * best_speciation
        )
        if pressure_guardrail and speciation_guardrail:
            eligible.append(variant_id)
    selected_variant = min(
        eligible,
        key=lambda variant_id: summary["variants"][variant_id][
            "pressure_temperature_balanced_log10_rmse"
        ],
        default="current_ion_specific",
    )
    selected_parameters = RESULTS / "selected-candidate-parameters.json"
    selected_parameters.write_text(
        json.dumps(variant_mappings[selected_variant], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary["candidate_selection"] = {
        "selected_variant": selected_variant,
        "eligible_variants": eligible,
        "pressure_metric": "equal-temperature-weighted positive-target log10 RMSE",
        "pressure_guardrail": (
            "each temperature no more than 10 percent worse than the current baseline"
        ),
        "speciation_guardrail": (
            "all 44 states evaluated and temperature-balanced log10 RMSE no more "
            "than 10 percent above the best candidate"
        ),
        "selected_parameter_path": str(selected_parameters.relative_to(ANALYSIS)),
        "selected_parameter_sha256": sha256(selected_parameters),
    }
    checkpoint()
    (RESULTS / "permittivity-formulation-comparison.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parameters",
        type=Path,
        required=True,
        help="Explicit source vector for this model comparison; never adopts a candidate",
    )
    main(parser.parse_args().parameters.resolve())


if __name__ == "__main__":
    from refresh_results import bounded_main

    bounded_main(cli)
