from __future__ import annotations

import csv
import copy
import hashlib
import importlib.metadata
import json
import math
import statistics
from dataclasses import replace
from pathlib import Path
from urllib.parse import unquote, urlparse

import epcsaft
from epcsaft import equilibrium


ANALYSIS = Path(__file__).resolve().parents[1]
INPUT = ANALYSIS / "data/input"
SPECIATION_OUTPUT = ANALYSIS / "figures/speciation/output"
PRESSURE_OUTPUT = ANALYSIS / "figures/pressure/output"
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
COMPARISON = ANALYSIS / "results/permittivity-formulation-comparison.json"
STATE_PACKET = INPUT / "state-packet.json"
ENGINE_WHEEL = INPUT / "engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
CANONICAL_SPECIATION = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
)
CANONICAL_VLE = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv"
)
STATE_PACKET_SHA256 = "41017bcf727a486a8f3feb280e19c111a15c5dda5a3cca4e8c7dc5b051168fef"
ENGINE_COMMIT = "38e91823b6d4f26c1d549f07aaef24a089d8e16d"
ENGINE_WHEEL_SHA256 = "d7b4fc5ba5cbf0e979b65af83442d565496d11b771bb559233ad9dc3a4f8414a"
CANONICAL_SPECIATION_SHA256 = (
    "8c07df9efd1c1ecbd775ccdd42791e0cef1880b3837e5749a60d2142aa85809e"
)
CANONICAL_VLE_SHA256 = (
    "9e7d9ba5fead8bfa83a311dad341e3e2e8df1806d5249642a23562e99a72cb73"
)
SPECIATION_GRID_TEMPERATURES_C = (20, 40, 60, 80)
SPECIATION_GRID_POINTS = 46
R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS = (
    8.0330699846,
    4.0165349923,
    4.0165349923,
)

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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(
    path: Path, rows: list[dict[str, object]], fields: tuple[str, ...]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def failure_fields(failure: object | None) -> tuple[str, str]:
    if failure is None:
        return "", ""
    return str(getattr(failure, "code", "unknown")), str(
        getattr(failure, "diagnostic", failure)
    )


def installed_wheel() -> Path:
    direct_url = json.loads(
        importlib.metadata.distribution("epcsaft").read_text("direct_url.json") or "{}"
    ).get("url", "")
    path = Path(unquote(urlparse(direct_url).path))
    if (
        not direct_url.startswith("file://")
        or path.suffix != ".whl"
        or not path.is_file()
    ):
        raise RuntimeError("replay requires epcsaft installed from the retained wheel")
    return path


def prepared_problem(problem: object, identity: str) -> object:
    continuation = problem.continuation_state
    if continuation is None:
        raise ValueError("state packet request lacks a continuation warm start")
    phase = continuation.phases[0]
    balance = problem.reaction_system.balance_matrix
    targets = problem.reaction_system.conserved_totals
    projected = tuple(
        math.fsum(
            coefficient * value
            for coefficient, value in zip(row, phase.mole_fractions, strict=True)
        )
        for row in balance
    )
    total = targets[1] / projected[1]
    amounts = [total * value for value in phase.mole_fractions]
    amounts[0] += targets[0] - math.fsum(
        coefficient * amount
        for coefficient, amount in zip(balance[0], amounts, strict=True)
    )
    if amounts[0] <= problem.reaction_system.strict_interior_amount_floor_mol:
        amounts = list(problem.reaction_system.feed_amounts_mol)
    if amounts[0] <= problem.reaction_system.strict_interior_amount_floor_mol:
        raise ValueError("continuation warm start cannot satisfy the current feed")
    start = equilibrium.FinitePhaseStart(
        tuple(amounts), math.fsum(amounts) * phase.molar_volume_m3_per_mol
    )
    phases = tuple(
        replace(candidate, start=start if candidate.amount_role == "finite" else None)
        for candidate in problem.phases
    )
    return replace(
        problem,
        phases=phases,
        continuation_identity=(
            identity
            if any(candidate.amount_role == "incipient" for candidate in phases)
            else None
        ),
        continuation_state=None,
    )


def corrected_request(request: dict[str, object]) -> dict[str, object]:
    """Apply the audited Austgen source-to-common-molality shifts to R1--R3."""

    corrected = copy.deepcopy(request)
    records = corrected["reaction_system"]["equilibrium_constants"]
    for index, offset in enumerate(R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS):
        records[index][0] = float(records[index][0]) + offset
        records[index][1] = "Austgen1991_converted_to_common_molality"
    return corrected


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
        errors = [
            float(row["predicted"]) - float(row["observed"]) for row in evaluated
        ]
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
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))
    parameter_sha256 = sha256(PARAMETERS)
    assert parameter_sha256 == comparison["promotion"]["selected_parameter_sha256"]
    assert sha256(STATE_PACKET) == STATE_PACKET_SHA256
    assert sha256(ENGINE_WHEEL) == ENGINE_WHEEL_SHA256
    assert sha256(CANONICAL_SPECIATION) == CANONICAL_SPECIATION_SHA256
    assert sha256(CANONICAL_VLE) == CANONICAL_VLE_SHA256
    if sha256(installed_wheel()) != ENGINE_WHEEL_SHA256:
        raise RuntimeError(
            "installed epcsaft wheel does not match the retained replay wheel"
        )
    parameters = epcsaft.Parameters.from_json(PARAMETERS)
    model = epcsaft.Mixture(parameters)
    fit = json.loads(STATE_PACKET.read_text(encoding="utf-8"))

    speciation_model: list[dict[str, object]] = []
    speciation_observed: list[dict[str, object]] = []
    pressure_model: list[dict[str, object]] = []
    pressure_observed: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    source_continuation_fingerprints: set[str] = set()
    speciation_templates: dict[int, list[tuple[float, dict[str, object]]]] = {}
    pressure_templates: dict[int, list[tuple[float, dict[str, object]]]] = {}

    for index, observation in enumerate(fit["observations"], start=1):
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            corrected_request(observation["request"])
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
        problem = prepared_problem(problem, f"{problem.identity}-notebook-bundle")
        try:
            result = equilibrium.solve(model, problem)
            status = result.status
            code, diagnostic = failure_fields(result.failure)
        except Exception as exc:
            result = None
            status = "exception"
            code = "engine_exception"
            diagnostic = f"{type(exc).__name__}: {exc}"

        if status == "evaluated":
            if result is None or result.continuation_state is None:
                raise RuntimeError("evaluated result lacks a continuation state")
            if (
                result.continuation_state.parameter_fingerprint
                != parameters.fingerprint
            ):
                raise RuntimeError(
                    "evaluated result does not match the notebook parameter bundle"
                )

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
            if (
                status == "evaluated"
                and result is not None
                and result.continuation_state is not None
            ):
                liquid = next(
                    phase
                    for phase in result.continuation_state.phases
                    if phase.role == "liquid"
                )
                for species, value in zip(
                    liquid.supported_component_ids, liquid.mole_fractions, strict=True
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
            row
            for row in csv.DictReader(stream)
            if row["active_view_member"] == "yes"
        ]
    for pressure_index, row in enumerate(canonical_vle_rows, start=1):
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
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            corrected_request(request)
        )
        problem = prepared_problem(problem, f"{identity}-notebook-bundle")
        try:
            result = equilibrium.solve(model, problem)
            status = result.status
            code, diagnostic = failure_fields(result.failure)
        except Exception as exc:
            result = None
            status = "exception"
            code = "engine_exception"
            diagnostic = f"{type(exc).__name__}: {exc}"
        pressure_observed.append(
            {
                "observation_id": identity,
                "source": row["source_key"],
                "temperature_C": float(temperature_c),
                "loading_mol_CO2_per_mol_MEA": loading,
                "observed_pCO2_kPa": float(row["CO2_pressure"]),
            }
        )
        if status == "evaluated" and result is not None:
            if (
                result.continuation_state is None
                or result.continuation_state.parameter_fingerprint
                != parameters.fingerprint
            ):
                raise RuntimeError("pressure result does not match the notebook bundle")
            predicted = next(
                result_row.value
                for result_row in result.rows
                if result_row.identity == "co2-partial-pressure"
            )
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
        print(
            f"pressure {pressure_index:03d}/{len(canonical_vle_rows)}: "
            f"{identity} {status}"
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
            problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
                corrected_request(request)
            )
            problem = prepared_problem(problem, grid_id)
            try:
                result = equilibrium.solve(model, problem)
                status = result.status
                code, diagnostic = failure_fields(result.failure)
            except Exception as exc:
                result = None
                status = "exception"
                code = "engine_exception"
                diagnostic = f"{type(exc).__name__}: {exc}"
            if (
                status == "evaluated"
                and result is not None
                and result.continuation_state is not None
            ):
                liquid = next(
                    phase
                    for phase in result.continuation_state.phases
                    if phase.role == "liquid"
                )
                for species, value in zip(
                    liquid.supported_component_ids, liquid.mole_fractions, strict=True
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
                "loading_mol_CO2_per_mol_MEA": row[
                    "loading_mol_CO2_per_mol_MEA"
                ],
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
    temperature_balanced_log10_rmse = {
        family: math.sqrt(
            statistics.fmean(
                float(row["rmse_log10_error"]) ** 2
                for row in statistics_rows
                if row["family"] == family and row["group_type"] == "temperature_C"
            )
        )
        for family in ("pressure", "speciation")
    }
    receipt = {
        "schema_version": 1,
        "status": "active_current_best_bundle",
        "engine_source_commit": ENGINE_COMMIT,
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "engine_distribution_version": importlib.metadata.version("epcsaft"),
        "parameter_document_sha256": parameter_sha256,
        "selected_permittivity_variant": comparison["promotion"]["selected_variant"],
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
        "successful_fingerprints_match_bundle": True,
        "warm_start_policy": (
            "source continuation values projected to mass-balanced finite starts, "
            "with the strictly positive feed used when projection crosses the "
            "interior boundary; continuation identity and state cleared before "
            "every solve"
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


if __name__ == "__main__":
    main()
