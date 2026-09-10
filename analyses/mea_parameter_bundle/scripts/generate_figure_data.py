from __future__ import annotations

import argparse
import csv
import copy
import importlib.metadata
import json
import math
import statistics
from time import perf_counter
from pathlib import Path

import epcsaft
from epcsaft import equilibrium
from shared_evaluation import (
    ENGINE_COMMIT,
    ENGINE_WHEEL,
    ENGINE_WHEEL_SHA256,
    PARAMETERS,
    R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS,
    SOURCE_CONTRACT,
    STATE_PACKET,
    STATE_PACKET_SHA256,
    EvaluationLimits,
    EVALUATOR_VERSION,
    anchor_from,
    cached_anchors,
    corrected_request,
    evaluate_state,
    load_state_packet,
    sha256,
    verify_wheel,
)
from result_freshness import source_hashes, stamp_results
from refresh_results import bounded_main


ANALYSIS = Path(__file__).resolve().parents[1]
INPUT = ANALYSIS / "data/input"
SPECIATION_OUTPUT = ANALYSIS / "figures/speciation/output"
PRESSURE_OUTPUT = ANALYSIS / "figures/pressure/output"
COMPARISON = ANALYSIS / "results/permittivity-formulation-comparison.json"
CANONICAL_SPECIATION = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
)
CANONICAL_VLE = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv"
)
CANONICAL_SPECIATION_SHA256 = (
    "8c07df9efd1c1ecbd775ccdd42791e0cef1880b3837e5749a60d2142aa85809e"
)
CANONICAL_VLE_SHA256 = (
    "9e7d9ba5fead8bfa83a311dad341e3e2e8df1806d5249642a23562e99a72cb73"
)
SPECIATION_GRID_TEMPERATURES_C = (20, 40, 60, 80)
SPECIATION_GRID_POINTS = 46

SPECIES_LABELS = {
    "carbon-dioxide": "CO2",
    "monoethanolamine": "MEA",
    "water": "H2O",
    "protonated-monoethanolamine": "MEAH+",
    "carbamate-anion": "MEACOO-",
    "bicarbonate-anion": "HCO3-",
    "carbonate-anion": "CO3^2-",
    "hydronium-cation": "H3O+",
    "hydroxide-anion": "OH-",
}


def write_csv(
    path: Path, rows: list[dict[str, object]], fields: tuple[str, ...]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fit_statistics(
    residual_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in residual_rows:
        family = str(row["family"])
        groups.setdefault((family, "overall", "all"), []).append(row)
        for group_type, field in (
            ("temperature_C", "temperature_C"),
            ("source", "source"),
            ("target", "target"),
        ):
            groups.setdefault((family, group_type, str(row[field])), []).append(row)
        groups.setdefault(
            (
                family,
                "temperature_source",
                f"{row['temperature_C']} C | {row['source']}",
            ),
            [],
        ).append(row)
    output: list[dict[str, object]] = []
    for (family, group_type, group), values in sorted(groups.items()):
        evaluated = [row for row in values if row["predicted"] != ""]
        positive = [
            row
            for row in evaluated
            if float(row["observed"]) > 0.0 and float(row["predicted"]) > 0.0
        ]
        log_errors = [
            math.log10(float(row["predicted"]) / float(row["observed"]))
            for row in positive
        ]
        errors = [float(row["predicted"]) - float(row["observed"]) for row in evaluated]
        percent_errors = [
            100.0
            * abs(float(row["predicted"]) - float(row["observed"]))
            / float(row["observed"])
            for row in positive
        ]
        output.append(
            {
                "family": family,
                "group_type": group_type,
                "group": group,
                "attempted_targets": len(values),
                "evaluated_targets": len(evaluated),
                "coverage_fraction": len(evaluated) / len(values),
                "positive_log_targets": len(positive),
                "mean_signed_log10_error": (
                    statistics.fmean(log_errors) if log_errors else ""
                ),
                "median_signed_log10_error": (
                    statistics.median(log_errors) if log_errors else ""
                ),
                "median_absolute_log10_error": (
                    statistics.median(map(abs, log_errors)) if log_errors else ""
                ),
                "rmse_log10_error": (
                    math.sqrt(statistics.fmean(error * error for error in log_errors))
                    if log_errors
                    else ""
                ),
                "rmse_factor": (
                    10.0
                    ** math.sqrt(
                        statistics.fmean(error * error for error in log_errors)
                    )
                    if log_errors
                    else ""
                ),
                "mape_percent": (
                    statistics.fmean(percent_errors) if percent_errors else ""
                ),
                "median_absolute_percent_error": (
                    statistics.median(percent_errors) if percent_errors else ""
                ),
                "mae_native_unit": (
                    statistics.fmean(map(abs, errors)) if errors else ""
                ),
                "rmse_native_unit": (
                    math.sqrt(statistics.fmean(error * error for error in errors))
                    if errors
                    else ""
                ),
            }
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-timeout-s", type=float, default=60.0)
    parser.add_argument("--overall-timeout-s", type=float, default=900.0)
    args = parser.parse_args()
    freshness_inputs = source_hashes(
        STATE_PACKET,
        CANONICAL_SPECIATION,
        CANONICAL_VLE,
        COMPARISON,
        Path(__file__),
        Path(__file__).with_name("shared_evaluation.py"),
        SOURCE_CONTRACT,
    )
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))
    parameter_sha256 = sha256(PARAMETERS)
    adoption = ANALYSIS / "results/reaction-temperature-fit/adoption-receipt.json"
    accepted = {comparison["promotion"]["selected_parameter_sha256"]}
    if adoption.exists():
        accepted.add(
            json.loads(adoption.read_text(encoding="utf-8")).get(
                "adopted_parameter_sha256"
            )
        )
    assert parameter_sha256 in accepted, (
        "parameter document is not a recorded incumbent"
    )
    assert sha256(STATE_PACKET) == STATE_PACKET_SHA256
    assert sha256(ENGINE_WHEEL) == ENGINE_WHEEL_SHA256
    assert sha256(CANONICAL_SPECIATION) == CANONICAL_SPECIATION_SHA256
    assert sha256(CANONICAL_VLE) == CANONICAL_VLE_SHA256
    verify_wheel()
    limits = EvaluationLimits(
        state_timeout_s=args.state_timeout_s,
        overall_timeout_s=args.overall_timeout_s,
        deadline_monotonic=perf_counter() + args.overall_timeout_s,
    )
    parameters = epcsaft.Parameters.from_json(PARAMETERS)
    model = epcsaft.Mixture(parameters)
    reaction_values = {
        spec.identity: float(spec.value.magnitude)
        for spec in parameters.parameter_specs
        if spec.identity.startswith("reaction:")
    }
    fit = load_state_packet(STATE_PACKET)

    speciation_model: list[dict[str, object]] = []
    speciation_observed: list[dict[str, object]] = []
    pressure_model: list[dict[str, object]] = []
    pressure_observed: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    source_continuation_fingerprints: set[str] = set()
    speciation_templates: dict[int, list[tuple[float, dict[str, object]]]] = {}
    pressure_templates: dict[int, list[tuple[float, dict[str, object]]]] = {}
    speciation_anchors: dict[int, list[object]] = {}

    for index, observation in enumerate(fit["observations"], start=1):
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            corrected_request(observation["request"], reaction_values)
        )
        temperature_c = float(problem.temperature.value.to("kelvin").magnitude) - 273.15
        loading = float(problem.reaction_system.feed_amounts_mol[0])
        family = "pressure" if len(observation["targets"]) == 1 else "speciation"
        source = str(observation["targets"][0]["source_identity"])
        if (
            family == "speciation"
            and round(temperature_c) in SPECIATION_GRID_TEMPERATURES_C
        ):
            speciation_templates.setdefault(round(temperature_c), []).append(
                (loading, observation["request"])
            )
        elif family == "pressure":
            pressure_templates.setdefault(round(temperature_c), []).append(
                (loading, observation["request"])
            )
        if problem.continuation_state is None:
            raise ValueError(
                f"{observation['identity']} lacks a continuation warm start"
            )
        source_continuation_fingerprints.add(
            problem.continuation_state.parameter_fingerprint
        )
        if family == "pressure":
            continue
        temperature_key = round(temperature_c)
        if temperature_key not in speciation_anchors:
            speciation_anchors[temperature_key] = cached_anchors({temperature_key})
        anchors = speciation_anchors[temperature_key]
        record = evaluate_state(
            model,
            observation["request"],
            reaction_values,
            f"{observation['identity']}-notebook-bundle",
            anchors,
            limits=limits,
        )
        status = record["status"]
        code = record["failure_code"]
        diagnostic = record["failure_diagnostic"]

        if family == "speciation":
            for target in observation["targets"]:
                speciation_observed.append(
                    {
                        "observation_id": observation["identity"],
                        "source": source,
                        "temperature_C": temperature_c,
                        "loading_mol_CO2_per_mol_MEA": loading,
                        "species": str(target["identity"]).split("::")[-1],
                        "observed_mole_fraction": float(target["observed"]),
                    }
                )
            if status == "evaluated" and record.get("anchor") is not None:
                liquid = next(
                    phase for phase in record["phases"] if phase["role"] == "liquid"
                )
                speciation_anchors[temperature_key].append(anchor_from(record))
                species_ids = (
                    "carbon-dioxide",
                    "monoethanolamine",
                    "water",
                    "protonated-monoethanolamine",
                    "carbamate-anion",
                    "bicarbonate-anion",
                    "carbonate-anion",
                    "hydronium-cation",
                    "hydroxide-anion",
                )
                for species, value in zip(
                    species_ids, liquid["mole_fractions"], strict=True
                ):
                    speciation_model.append(
                        {
                            "observation_id": observation["identity"],
                            "source": source,
                            "temperature_C": temperature_c,
                            "loading_mol_CO2_per_mol_MEA": loading,
                            "species": SPECIES_LABELS[species],
                            "model_mole_fraction": float(value),
                        }
                    )

        if status != "evaluated":
            failures.append(
                {
                    "index": index,
                    "family": family,
                    "observation_id": observation["identity"],
                    "source": source,
                    "temperature_C": temperature_c,
                    "loading_mol_CO2_per_mol_MEA": loading,
                    "status": status,
                    "failure_code": code,
                    "failure_diagnostic": diagnostic,
                }
            )
        print(
            f"{index:03d}/{len(fit['observations'])}: {observation['identity']} {status}"
        )

    with CANONICAL_VLE.open(newline="", encoding="utf-8") as stream:
        canonical_vle_rows = [
            row for row in csv.DictReader(stream) if row["active_view_member"] == "yes"
        ]
    pressure_anchors = cached_anchors(
        {round(float(row["temperature_canonical_C"])) for row in canonical_vle_rows}
    )
    pressure_outcomes: dict[str, tuple[dict[str, object], str, str, str]] = {}
    for pressure_index, row in enumerate(
        sorted(
            canonical_vle_rows,
            key=lambda item: (
                round(float(item["temperature_canonical_C"])),
                float(item["CO2_loading"]),
                item["observation_id"],
            ),
        ),
        start=1,
    ):
        temperature_c = round(float(row["temperature_canonical_C"]))
        loading = float(row["CO2_loading"])
        if temperature_c not in pressure_templates:
            raise ValueError(f"missing {temperature_c} C pressure template")
        _, template = min(
            pressure_templates[temperature_c],
            key=lambda candidate: abs(candidate[0] - loading),
        )
        request = copy.deepcopy(template)
        reaction_system = request["reaction_system"]
        reaction_system["feed_amounts_mol"][0] = loading
        reaction_system["conserved_totals"] = [
            math.fsum(
                coefficient * amount
                for coefficient, amount in zip(
                    balance, reaction_system["feed_amounts_mol"], strict=True
                )
            )
            for balance in reaction_system["balance_matrix"]
        ]
        identity = row["observation_id"]
        record = evaluate_state(
            model,
            request,
            reaction_values,
            identity,
            pressure_anchors,
            limits=limits,
        )
        status = str(record["status"])
        code = str(record["failure_code"])
        diagnostic = str(record["failure_diagnostic"])
        pressure_outcomes[identity] = (record, status, code, diagnostic)
        if status == "evaluated":
            anchor = anchor_from(record)
            if anchor is not None:
                pressure_anchors.append(anchor)
        print(
            f"pressure {pressure_index:03d}/{len(canonical_vle_rows)}: "
            f"{identity} {status}"
        )

    for pressure_index, row in enumerate(canonical_vle_rows, start=1):
        identity = row["observation_id"]
        temperature_c = round(float(row["temperature_canonical_C"]))
        loading = float(row["CO2_loading"])
        record, status, code, diagnostic = pressure_outcomes[identity]
        pressure_observed.append(
            {
                "observation_id": identity,
                "source": row["source_key"],
                "temperature_C": float(temperature_c),
                "loading_mol_CO2_per_mol_MEA": loading,
                "observed_pCO2_kPa": float(row["CO2_pressure"]),
            }
        )
        if status == "evaluated":
            predicted = record["predictions"]["co2-partial-pressure"]
            pressure_model.append(
                {
                    "observation_id": identity,
                    "source": row["source_key"],
                    "temperature_C": float(temperature_c),
                    "loading_mol_CO2_per_mol_MEA": loading,
                    "predicted_pCO2_kPa": float(predicted) / 1000.0,
                }
            )
        else:
            failures.append(
                {
                    "index": len(fit["observations"]) + pressure_index,
                    "family": "pressure",
                    "observation_id": identity,
                    "source": row["source_key"],
                    "temperature_C": float(temperature_c),
                    "loading_mol_CO2_per_mol_MEA": loading,
                    "status": status,
                    "failure_code": code,
                    "failure_diagnostic": diagnostic,
                }
            )

    with CANONICAL_SPECIATION.open(newline="", encoding="utf-8") as stream:
        canonical_rows = list(csv.DictReader(stream))
    grid_ranges: dict[int, tuple[float, float]] = {}
    for temperature_c in SPECIATION_GRID_TEMPERATURES_C:
        loadings = [
            float(row["co2_loading_mol_per_mol_mea"])
            for row in canonical_rows
            if row["value_mole_fraction"] != ""
            and float(row["temperature_C"]) == temperature_c
            and float(row["mea_mass_fraction"]) == 0.3
        ]
        if not loadings or temperature_c not in speciation_templates:
            raise ValueError(f"missing {temperature_c} C speciation grid authority")
        grid_ranges[temperature_c] = (min(loadings), 1.0)

    speciation_grid: list[dict[str, object]] = []
    grid_attempt = 0
    for temperature_c, (loading_min, loading_max) in grid_ranges.items():
        templates = speciation_templates[temperature_c]
        for grid_index in range(1, SPECIATION_GRID_POINTS + 1):
            grid_attempt += 1
            loading = loading_min + (grid_index - 1) * (loading_max - loading_min) / (
                SPECIATION_GRID_POINTS - 1
            )
            eligible = [candidate for candidate in templates if candidate[0] <= loading]
            _, template = (
                max(eligible, key=lambda candidate: candidate[0])
                if eligible
                else min(templates, key=lambda candidate: candidate[0])
            )
            grid_id = f"speciation-grid-{temperature_c:03d}C-{grid_index:03d}"
            request = copy.deepcopy(template)
            reaction_system = request["reaction_system"]
            reaction_system["feed_amounts_mol"][0] = loading
            reaction_system["conserved_totals"] = [
                math.fsum(
                    coefficient * amount
                    for coefficient, amount in zip(
                        balance,
                        reaction_system["feed_amounts_mol"],
                        strict=True,
                    )
                )
                for balance in reaction_system["balance_matrix"]
            ]
            if temperature_c not in speciation_anchors:
                speciation_anchors[temperature_c] = cached_anchors({temperature_c})
            grid_anchors = speciation_anchors[temperature_c]
            record = evaluate_state(
                model,
                request,
                reaction_values,
                grid_id,
                grid_anchors,
                limits=limits,
            )
            status = record["status"]
            code = record["failure_code"]
            diagnostic = record["failure_diagnostic"]
            if status == "evaluated" and record.get("anchor") is not None:
                liquid = next(
                    phase for phase in record["phases"] if phase["role"] == "liquid"
                )
                grid_anchors.append(anchor_from(record))
                species_ids = (
                    "carbon-dioxide",
                    "monoethanolamine",
                    "water",
                    "protonated-monoethanolamine",
                    "carbamate-anion",
                    "bicarbonate-anion",
                    "carbonate-anion",
                    "hydronium-cation",
                    "hydroxide-anion",
                )
                for species, value in zip(
                    species_ids, liquid["mole_fractions"], strict=True
                ):
                    speciation_grid.append(
                        {
                            "grid_id": grid_id,
                            "temperature_C": float(temperature_c),
                            "loading_mol_CO2_per_mol_MEA": loading,
                            "species": SPECIES_LABELS[species],
                            "model_mole_fraction": float(value),
                        }
                    )
            else:
                failures.append(
                    {
                        "index": (
                            len(fit["observations"])
                            + len(canonical_vle_rows)
                            + grid_attempt
                        ),
                        "family": "speciation_grid",
                        "observation_id": grid_id,
                        "source": "direct_engine_grid",
                        "temperature_C": float(temperature_c),
                        "loading_mol_CO2_per_mol_MEA": loading,
                        "status": status,
                        "failure_code": code,
                        "failure_diagnostic": diagnostic,
                    }
                )
            print(
                f"grid {temperature_c:02d} C {grid_index:02d}/{SPECIATION_GRID_POINTS}: "
                f"loading={loading:.4f} {status}"
            )

    speciation_display_observed = [
        {
            "observation_id": row["record_id"],
            "source": row["source_key"],
            "temperature_C": row["temperature_C"],
            "mea_mass_fraction": row["mea_mass_fraction"],
            "loading_mol_CO2_per_mol_MEA": row["co2_loading_mol_per_mol_mea"],
            "species": row["species"],
            "observed_mole_fraction": row["value_mole_fraction"],
            "measurement_role": row["measurement_role"],
            "lifecycle_status": row["lifecycle_status"],
            "target_membership": row["target_membership"],
        }
        for row in canonical_rows
        if float(row["temperature_C"]) in SPECIATION_GRID_TEMPERATURES_C
        and float(row["mea_mass_fraction"]) == 0.3
        and row["value_mole_fraction"] != ""
    ]

    write_csv(
        SPECIATION_OUTPUT / "speciation-model.csv",
        speciation_model,
        (
            "observation_id",
            "source",
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "species",
            "model_mole_fraction",
        ),
    )
    write_csv(
        SPECIATION_OUTPUT / "speciation-observations.csv",
        speciation_observed,
        (
            "observation_id",
            "source",
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "species",
            "observed_mole_fraction",
        ),
    )
    write_csv(
        SPECIATION_OUTPUT / "speciation-model-grid.csv",
        speciation_grid,
        (
            "grid_id",
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "species",
            "model_mole_fraction",
        ),
    )
    write_csv(
        SPECIATION_OUTPUT / "speciation-display-observations.csv",
        speciation_display_observed,
        (
            "observation_id",
            "source",
            "temperature_C",
            "mea_mass_fraction",
            "loading_mol_CO2_per_mol_MEA",
            "species",
            "observed_mole_fraction",
            "measurement_role",
            "lifecycle_status",
            "target_membership",
        ),
    )
    write_csv(
        PRESSURE_OUTPUT / "pressure-model.csv",
        pressure_model,
        (
            "observation_id",
            "source",
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "predicted_pCO2_kPa",
        ),
    )
    write_csv(
        PRESSURE_OUTPUT / "pressure-observations.csv",
        pressure_observed,
        (
            "observation_id",
            "source",
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "observed_pCO2_kPa",
        ),
    )
    write_csv(
        ANALYSIS / "results/figure-calculation-failures.csv",
        failures,
        (
            "index",
            "family",
            "observation_id",
            "source",
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "status",
            "failure_code",
            "failure_diagnostic",
        ),
    )
    pressure_predictions = {
        row["observation_id"]: row["predicted_pCO2_kPa"] for row in pressure_model
    }
    species_predictions = {
        (row["observation_id"], row["species"]): row["model_mole_fraction"]
        for row in speciation_model
    }
    residual_rows: list[dict[str, object]] = []
    residual_rows.extend(
        {
            "family": "pressure",
            "observation_id": row["observation_id"],
            "source": row["source"],
            "temperature_C": row["temperature_C"],
            "loading_mol_CO2_per_mol_MEA": row["loading_mol_CO2_per_mol_MEA"],
            "target": "pCO2",
            "unit": "kPa",
            "observed": row["observed_pCO2_kPa"],
            "predicted": pressure_predictions.get(row["observation_id"], ""),
        }
        for row in pressure_observed
    )
    for row in speciation_observed:
        key = (row["observation_id"], row["species"])
        if row["species"] == "MEA + MEAH+":
            mea = species_predictions.get((row["observation_id"], "MEA"))
            meah = species_predictions.get((row["observation_id"], "MEAH+"))
            predicted = mea + meah if mea is not None and meah is not None else ""
        else:
            predicted = species_predictions.get(key, "")
        residual_rows.append(
            {
                "family": "speciation",
                "observation_id": row["observation_id"],
                "source": row["source"],
                "temperature_C": row["temperature_C"],
                "loading_mol_CO2_per_mol_MEA": row["loading_mol_CO2_per_mol_MEA"],
                "target": row["species"],
                "unit": "mole_fraction",
                "observed": row["observed_mole_fraction"],
                "predicted": predicted,
            }
        )
    write_csv(
        ANALYSIS / "results/current-best-fit-residuals.csv",
        residual_rows,
        (
            "family",
            "observation_id",
            "source",
            "temperature_C",
            "loading_mol_CO2_per_mol_MEA",
            "target",
            "unit",
            "observed",
            "predicted",
        ),
    )
    statistics_rows = fit_statistics(residual_rows)
    write_csv(
        ANALYSIS / "results/current-best-fit-statistics.csv",
        statistics_rows,
        (
            "family",
            "group_type",
            "group",
            "attempted_targets",
            "evaluated_targets",
            "coverage_fraction",
            "positive_log_targets",
            "mean_signed_log10_error",
            "median_signed_log10_error",
            "median_absolute_log10_error",
            "rmse_log10_error",
            "rmse_factor",
            "mape_percent",
            "median_absolute_percent_error",
            "mae_native_unit",
            "rmse_native_unit",
        ),
    )
    speciation_packet_count = sum(
        len(observation["targets"]) != 1 for observation in fit["observations"]
    )
    temperature_balanced_log10_rmse = {}
    for family in ("pressure", "speciation"):
        errors = [float(row["rmse_log10_error"]) for row in statistics_rows
                  if row["family"] == family and row["group_type"] == "temperature_C" and row["rmse_log10_error"] != ""]
        temperature_balanced_log10_rmse[family] = math.sqrt(statistics.fmean(value * value for value in errors)) if errors else None
    receipt = {
        "schema_version": 1,
        "evaluator_version": EVALUATOR_VERSION,
        "status": "exploratory_incumbent",
        "engine_source_commit": ENGINE_COMMIT,
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "engine_distribution_version": importlib.metadata.version("epcsaft"),
        "parameter_document_sha256": parameter_sha256,
        "selected_permittivity_variant": "solvent_only_mass_fraction_co2_excluded",
        "state_packet_sha256": STATE_PACKET_SHA256,
        "reaction_standard_state_correction": {
            "reason": (
                "the retained state packet contains raw Austgen R1-R3 values "
                "already labeled as common molality"
            ),
            "reaction_ids": ["R1", "R2", "R3"],
            "ln_k_offsets": list(R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS),
            "resulting_standard_state": ("aqueous-molality-infinite-dilution-water-v1"),
        },
        "parameter_fingerprint": parameters.fingerprint,
        "source_continuation_parameter_fingerprints": sorted(
            source_continuation_fingerprints
        ),
        "warm_start_policy": (
            "source continuation values are projected to mass-balanced finite "
            "starts; pressure observations then reuse certified states across "
            "nearby loadings, fall back to the independent source start, and use "
            "neighboring-temperature certified states when the local branch is "
            "otherwise missed"
        ),
        "attempted_states": (
            speciation_packet_count + len(canonical_vle_rows) + grid_attempt
        ),
        "state_packet_observations": len(fit["observations"]),
        "pressure_template_states": sum(map(len, pressure_templates.values())),
        "attempted_speciation_packet_states": speciation_packet_count,
        "attempted_canonical_pressure_states": len(canonical_vle_rows),
        "attempted_speciation_grid_states": grid_attempt,
        "speciation_grid_temperatures_C": list(SPECIATION_GRID_TEMPERATURES_C),
        "speciation_grid_ranges": {
            str(temperature): list(bounds)
            for temperature, bounds in grid_ranges.items()
        },
        "evaluated_speciation_grid_states": len(speciation_grid) // len(SPECIES_LABELS),
        "display_speciation_observations": len(speciation_display_observed),
        "display_speciation_source_sha256": CANONICAL_SPECIATION_SHA256,
        "pressure_observation_source_sha256": CANONICAL_VLE_SHA256,
        "evaluated_pressure_states": len(pressure_model),
        "pressure_states": len(pressure_observed),
        "evaluated_speciation_states": len(speciation_model) // len(SPECIES_LABELS),
        "speciation_states": len(
            {row["observation_id"] for row in speciation_observed}
        ),
        "failed_states": len(failures),
        "failure_table": "results/figure-calculation-failures.csv",
        "fit_residual_table": "results/current-best-fit-residuals.csv",
        "fit_statistics_table": "results/current-best-fit-statistics.csv",
        "temperature_balanced_log10_rmse": temperature_balanced_log10_rmse,
    }
    (ANALYSIS / "results/figure-calculation-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    stamp_results(
        ANALYSIS / "results/figure-calculation-receipt.json",
        [
            SPECIATION_OUTPUT / "speciation-model.csv",
            SPECIATION_OUTPUT / "speciation-observations.csv",
            SPECIATION_OUTPUT / "speciation-model-grid.csv",
            SPECIATION_OUTPUT / "speciation-display-observations.csv",
            PRESSURE_OUTPUT / "pressure-model.csv",
            PRESSURE_OUTPUT / "pressure-observations.csv",
            ANALYSIS / "results/figure-calculation-failures.csv",
            ANALYSIS / "results/current-best-fit-residuals.csv",
            ANALYSIS / "results/current-best-fit-statistics.csv",
        ],
        inputs=freshness_inputs,
    )


if __name__ == "__main__":
    bounded_main(main)
