"""Evaluate fixed-bundle finite-dose absorption heat from Engine total enthalpy."""

from __future__ import annotations

import csv
import copy
import hashlib
import json
import math
import statistics
from dataclasses import replace
from pathlib import Path

import epcsaft
import matplotlib.pyplot as plt
import numpy as np
from epcsaft import equilibrium
from scipy.interpolate import PchipInterpolator

from generate_figure_data import (
    ENGINE_COMMIT,
    ENGINE_WHEEL,
    ENGINE_WHEEL_SHA256,
    PARAMETERS,
    STATE_PACKET,
    corrected_request,
    installed_wheel,
    prepared_problem,
    sha256,
)
from MEA.common.analysis_io import file_sha256, repo_relative_path
from MEA.common.plot_style import (
    apply_plot_theme,
    save_figure_bundle,
    write_mpl_sidecar,
)


ANALYSIS = Path(__file__).resolve().parents[1]
OBSERVATIONS = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
RESULTS = ANALYSIS / "results/calorimetry"
FIGURES = ANALYSIS / "figures/calorimetry/output"
TEMPERATURES_K = (313.15, 353.15, 393.15)
REFERENCE_TEMPERATURE_K = 353.15
R_J_MOL_K = 8.31446261815324


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows produced for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def residual_metrics(rows: list[dict[str, object]]) -> dict[str, float | int]:
    evaluated = [row for row in rows if row["status"] == "evaluated"]
    residuals = [float(row["residual_kj_per_mol_CO2"]) for row in evaluated]
    return {
        "attempted": len(rows),
        "evaluated": len(evaluated),
        "rmse_kj_per_mol_CO2": math.sqrt(
            statistics.fmean(value * value for value in residuals)
        ),
        "mean_bias_kj_per_mol_CO2": statistics.fmean(residuals),
        "median_absolute_error_kj_per_mol_CO2": statistics.median(map(abs, residuals)),
    }


def reaction_derivative(
    record: equilibrium.ChemicalEquilibriumConstant, temperature_k: float
) -> float:
    values = record.coefficient_values
    if record.correlation_kind == "ln-k-a-plus-b-over-t":
        return -values[1] / temperature_k**2
    if record.correlation_kind == "ln-k-a-plus-b-over-t-plus-c-ln-t-plus-d-t":
        return -values[1] / temperature_k**2 + values[2] / temperature_k + values[3]
    if record.correlation_kind == "negative-log10-temperature-polynomial":
        return math.log(10.0) * (values[0] / temperature_k**2 - values[2])
    raise ValueError(f"untyped reaction correlation: {record.reaction_id}")


def transformed_reaction_enthalpies(
    model: epcsaft.Mixture,
    problem: equilibrium.GeneralReactiveEquilibriumProblem,
) -> np.ndarray:
    reaction = problem.reaction_system
    standard = reaction.source_standard_state
    if standard is None:
        raise ValueError("MEA reaction system lacks its source standard state")
    transfer = epcsaft.source_reference_transfer(
        model,
        epcsaft.SourceReferenceDeclaration(
            reference_state_id=standard.id,
            component_ids=standard.source_reference_component_ids,
            solvent_mole_fractions=standard.source_reference_solvent_composition,
            ion_pairs=standard.source_reference_ion_pairs,
            phase=standard.source_reference_phase,
            reference_convention=standard.source_reference_convention,
            activity_convention_id=standard.source_reference_activity_convention_id,
            standard_molality_mol_per_kg=standard.source_reference_standard_molality_mol_per_kg,
            reference_pressure_pa=standard.reference_pressure_pa,
            required_derivatives=("temperature",),
            pure_components=standard.source_reference_pure_components,
        ),
        T=problem.temperature.value,
        P=standard.reference_pressure_pa * epcsaft.unit_registry.pascal,
    )
    basis = np.asarray(transfer.neutral_basis, dtype=float)
    source_derivatives = np.asarray(transfer.temperature_derivatives_per_k, dtype=float)
    rows = np.asarray(reaction.reaction_matrix, dtype=float)
    derivatives = []
    for row, record in zip(rows, reaction.equilibrium_constants, strict=True):
        coordinates, *_ = np.linalg.lstsq(basis.T, row, rcond=None)
        mismatch = np.max(np.abs(coordinates @ basis - row))
        if mismatch > 1.0e-10:
            raise ValueError(
                f"reaction {record.reaction_id} is outside the neutral basis"
            )
        derivative = (
            reaction_derivative(
                record, float(problem.temperature.value.to("kelvin").magnitude)
            )
            + float(coordinates @ source_derivatives)
            - float(np.sum(row))
            / float(problem.temperature.value.to("kelvin").magnitude)
        )
        derivatives.append(derivative)
    temperature_k = float(problem.temperature.value.to("kelvin").magnitude)
    return R_J_MOL_K * temperature_k**2 * np.asarray(derivatives)


def build_thermochemistry(
    model: epcsaft.Mixture,
    templates: dict[int, list[tuple[float, dict[str, object]]]],
    reaction_values: dict[str, float],
) -> tuple[epcsaft.ReferenceThermochemistry, dict[str, object]]:
    reaction_rows: np.ndarray | None = None
    component_enthalpies = []
    reaction_enthalpies = []
    for temperature_k in TEMPERATURES_K:
        temperature_c = round(temperature_k - 273.15)
        request = copy.deepcopy(templates[temperature_c][0][1])
        request["temperature"]["value"] = temperature_k
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            corrected_request(request, reaction_values)
        )
        rows = np.asarray(problem.reaction_system.reaction_matrix, dtype=float)
        reaction_rows = rows if reaction_rows is None else reaction_rows
        q_reaction = transformed_reaction_enthalpies(model, problem)
        h_components = rows.T @ np.linalg.solve(rows @ rows.T, q_reaction)
        if not np.allclose(rows @ h_components, q_reaction, rtol=2.0e-12, atol=2.0e-6):
            raise ValueError(
                "component thermochemistry does not span reaction enthalpies"
            )
        reaction_enthalpies.append(q_reaction)
        component_enthalpies.append(h_components)

    theta = np.asarray(TEMPERATURES_K) - REFERENCE_TEMPERATURE_K
    values = np.asarray(component_enthalpies)
    components = []
    component_records = []
    for index, component_id in enumerate(model.component_ids):
        quadratic, linear, reference = np.polyfit(theta, values[:, index], 2)
        cp_coefficients = (float(linear), float(2.0 * quadratic))
        component_records.append(
            {
                "component_id": component_id,
                "reference_enthalpy_j_per_mol": float(reference),
                "cp_coefficients_j_per_mol_k": list(cp_coefficients),
            }
        )
        components.append(
            epcsaft.ComponentReferenceThermochemistry(
                component_id,
                "mea-reaction-consistent-conserved-gauge",
                REFERENCE_TEMPERATURE_K,
                float(reference),
                epcsaft.IdealHeatCapacityPolynomial(
                    f"{component_id}-reaction-consistent-cp",
                    cp_coefficients,
                    (293.15, 413.15),
                ),
            )
        )
    payload = {
        "schema": "mea-reaction-consistent-reference-thermochemistry-v1",
        "method": "minimum-norm conserved gauge from Engine source-reference transfer and typed R1-R5 temperature derivatives",
        "engine_source_commit": ENGINE_COMMIT,
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "reference_temperature_k": REFERENCE_TEMPERATURE_K,
        "temperature_knots_k": list(TEMPERATURES_K),
        "component_ids": list(model.component_ids),
        "components": component_records,
        "reaction_enthalpies_j_per_mol": [row.tolist() for row in reaction_enthalpies],
        "gauge": "minimum Euclidean norm; no calorimetry fit",
    }
    fingerprint = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    payload["scientific_fingerprint"] = fingerprint
    thermochemistry = epcsaft.ReferenceThermochemistry(
        "mea-r1-r5-reaction-consistent-gauge-v1",
        fingerprint,
        tuple(model.component_ids),
        tuple(components),
    )
    assert reaction_rows is not None
    for temperature_k, q_reaction in zip(
        TEMPERATURES_K, reaction_enthalpies, strict=True
    ):
        h = np.asarray(
            thermochemistry.enthalpies_j_per_mol(temperature_k, model.component_ids)
        )
        if not np.allclose(reaction_rows @ h, q_reaction, rtol=2.0e-8, atol=2.0e-3):
            raise ValueError(
                "fitted reference thermochemistry violates reaction consistency"
            )
    return thermochemistry, payload


def main() -> None:
    if (
        sha256(ENGINE_WHEEL) != ENGINE_WHEEL_SHA256
        or sha256(installed_wheel()) != ENGINE_WHEEL_SHA256
    ):
        raise RuntimeError("installed and retained Engine wheels must match")
    parameters = epcsaft.Parameters.from_json(PARAMETERS)
    model = epcsaft.Mixture(parameters)
    reaction_values = {
        spec.identity: float(spec.value.magnitude)
        for spec in parameters.parameter_specs
        if spec.identity.startswith("reaction:")
    }
    packet = json.loads(STATE_PACKET.read_text(encoding="utf-8"))
    templates: dict[int, list[tuple[float, dict[str, object]]]] = {}
    for observation in packet["observations"]:
        if len(observation["targets"]) != 1:
            continue
        request = observation["request"]
        temperature_c = round(float(request["temperature"]["value"]) - 273.15)
        loading = float(request["reaction_system"]["feed_amounts_mol"][0])
        templates.setdefault(temperature_c, []).append((loading, request))
    missing = {round(value - 273.15) for value in TEMPERATURES_K} - set(templates)
    if missing:
        raise ValueError(f"missing pressure templates at {sorted(missing)} C")

    thermochemistry, thermochemistry_payload = build_thermochemistry(
        model, templates, reaction_values
    )
    observations = [
        row for row in read_rows(OBSERVATIONS) if row["regression_eligible"] == "true"
    ]
    endpoints: dict[int, set[float]] = {}
    for row in observations:
        temperature_c = round(float(row["temperature_C"]))
        endpoints.setdefault(temperature_c, set()).update(
            (
                float(row["previous_loading_mol_per_mol_mea"]),
                float(row["co2_loading_mol_per_mol_mea"]),
            )
        )

    states: dict[tuple[int, float], tuple[float, float]] = {}
    continuations: dict[tuple[int, float], object] = {}
    failures: dict[tuple[int, float], tuple[str, str]] = {}
    state_rows: list[dict[str, object]] = []
    attempt_rows: list[dict[str, object]] = []
    for temperature_c in sorted(endpoints):
        anchor_state = None
        anchor_pressure = None
        for loading in sorted(endpoints[temperature_c]):
            _, template = min(
                templates[temperature_c], key=lambda item: abs(item[0] - loading)
            )
            request = copy.deepcopy(template)
            request["reaction_system"]["feed_amounts_mol"][0] = loading
            request["reaction_system"]["conserved_totals"] = [
                math.fsum(
                    coefficient * amount
                    for coefficient, amount in zip(
                        balance,
                        request["reaction_system"]["feed_amounts_mol"],
                        strict=True,
                    )
                )
                for balance in request["reaction_system"]["balance_matrix"]
            ]
            source_pressure = float(request["pressure"]["initial"])
            attempts = [
                ("same-temperature-continuation", anchor_state, source_pressure),
                ("source-continuation", None, source_pressure),
            ]
            if anchor_state is not None and anchor_pressure is not None:
                attempts.append(
                    (
                        "same-temperature-continuation-previous-pressure",
                        anchor_state,
                        anchor_pressure,
                    )
                )
            for key in sorted(
                (
                    candidate
                    for candidate in continuations
                    if candidate[0] != temperature_c
                ),
                key=lambda item: (
                    abs(item[0] - temperature_c),
                    abs(item[1] - loading),
                ),
            )[:8]:
                attempts.extend(
                    (
                        (
                            f"cross-temperature-{key[0]}C-source-pressure",
                            continuations[key],
                            source_pressure,
                        ),
                        (
                            f"cross-temperature-{key[0]}C-anchor-pressure",
                            continuations[key],
                            states[key][1],
                        ),
                    )
                )
            result = None
            for attempt_index, (start_kind, attempt_state, pressure_start) in enumerate(
                attempts, start=1
            ):
                candidate = copy.deepcopy(request)
                candidate["pressure"]["initial"] = pressure_start
                candidate["pressure"]["starts"] = [pressure_start]
                problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
                    corrected_request(candidate, reaction_values)
                )
                if attempt_state is not None:
                    problem = replace(problem, continuation_state=attempt_state)
                problem = replace(
                    prepared_problem(
                        problem, f"calorimetry-{temperature_c}C-{loading:.6f}"
                    ),
                    thermochemistry=thermochemistry,
                )
                try:
                    result = equilibrium.solve(model, problem)
                except Exception as exc:
                    failures[(temperature_c, loading)] = (
                        "engine_exception",
                        f"{type(exc).__name__}: {exc}",
                    )
                    attempt_rows.append(
                        {
                            "temperature_C": temperature_c,
                            "loading_mol_CO2_per_mol_MEA": loading,
                            "attempt": attempt_index,
                            "start_kind": start_kind,
                            "pressure_start_pa": pressure_start,
                            "status": "exception",
                            "failure_code": "engine_exception",
                            "failure_diagnostic": f"{type(exc).__name__}: {exc}",
                        }
                    )
                    continue
                failure = result.failure
                if result.status == "evaluated" and isinstance(
                    result.total_enthalpy, epcsaft.NonEvaluableTrial
                ):
                    failure = result.total_enthalpy
                attempt_rows.append(
                    {
                        "temperature_C": temperature_c,
                        "loading_mol_CO2_per_mol_MEA": loading,
                        "attempt": attempt_index,
                        "start_kind": start_kind,
                        "pressure_start_pa": pressure_start,
                        "status": (
                            "evaluated"
                            if result.status == "evaluated"
                            and isinstance(
                                result.total_enthalpy, epcsaft.EquilibriumEnthalpy
                            )
                            else "failed"
                        ),
                        "failure_code": str(getattr(failure, "code", "")),
                        "failure_diagnostic": str(getattr(failure, "diagnostic", "")),
                    }
                )
                if result.status == "evaluated" and isinstance(
                    result.total_enthalpy, epcsaft.EquilibriumEnthalpy
                ):
                    break
            if result is None:
                print(f"{temperature_c:03d} C {loading:.6f}: exception")
                continue
            if result.status != "evaluated" or not isinstance(
                result.total_enthalpy, epcsaft.EquilibriumEnthalpy
            ):
                failure = (
                    result.total_enthalpy
                    if isinstance(result.total_enthalpy, epcsaft.NonEvaluableTrial)
                    else result.failure
                )
                failures[(temperature_c, loading)] = (
                    str(getattr(failure, "code", "non_evaluable")),
                    str(getattr(failure, "diagnostic", failure)),
                )
                print(
                    f"{temperature_c:03d} C {loading:.6f}: non_evaluable "
                    f"{failures[(temperature_c, loading)]}"
                )
                continue
            anchor_state = result.continuation_state
            solved_pressure = next(
                float(row.value)
                for row in result.rows
                if row.identity == "system-pressure"
            )
            anchor_pressure = solved_pressure
            total_enthalpy_j = float(result.total_enthalpy.value.to("joule").magnitude)
            states[(temperature_c, loading)] = (total_enthalpy_j, solved_pressure)
            continuations[(temperature_c, loading)] = result.continuation_state
            failures.pop((temperature_c, loading), None)
            phase = result.total_enthalpy.phases[0]
            state_rows.append(
                {
                    "temperature_C": temperature_c,
                    "loading_mol_CO2_per_mol_MEA": loading,
                    "system_pressure_pa": solved_pressure,
                    "total_liquid_enthalpy_j": total_enthalpy_j,
                    "liquid_amount_mol": phase.amount_mol,
                    "reference_molar_enthalpy_j_per_mol": phase.reference_molar_enthalpy_j_per_mol,
                    "residual_molar_enthalpy_j_per_mol": phase.residual_molar_enthalpy_j_per_mol,
                    "status": "evaluated",
                    "failure_code": "",
                    "failure_diagnostic": "",
                }
            )
            print(f"{temperature_c:03d} C {loading:.6f}: evaluated")

    for (temperature_c, loading), (code, diagnostic) in sorted(failures.items()):
        state_rows.append(
            {
                "temperature_C": temperature_c,
                "loading_mol_CO2_per_mol_MEA": loading,
                "system_pressure_pa": "",
                "total_liquid_enthalpy_j": "",
                "liquid_amount_mol": "",
                "reference_molar_enthalpy_j_per_mol": "",
                "residual_molar_enthalpy_j_per_mol": "",
                "status": "failed",
                "failure_code": code,
                "failure_diagnostic": diagnostic,
            }
        )

    comparison: list[dict[str, object]] = []
    for row in observations:
        temperature_c = round(float(row["temperature_C"]))
        current = float(row["co2_loading_mol_per_mol_mea"])
        prior = float(row["previous_loading_mol_per_mol_mea"])
        current_state = states.get((temperature_c, current))
        prior_state = states.get((temperature_c, prior))
        predicted = None
        status = "evaluated"
        failure_code = ""
        if current_state is None or prior_state is None:
            status = "endpoint_failed"
            missing_loading = current if current_state is None else prior
            failure_code = failures.get(
                (temperature_c, missing_loading), ("missing_endpoint", "")
            )[0]
        else:
            temperature_k = temperature_c + 273.15
            h_co2_feed = thermochemistry.enthalpies_j_per_mol(
                temperature_k, model.component_ids
            )[0]
            predicted = (
                -((current_state[0] - prior_state[0]) - (current - prior) * h_co2_feed)
                / (current - prior)
                / 1000.0
            )
        observed = float(row["dh_kj_per_mol_co2"])
        comparison.append(
            {
                "record_id": row["record_id"],
                "source": row["source"],
                "temperature_C": temperature_c,
                "campaign_partition": row["campaign_partition"],
                "prior_loading_mol_CO2_per_mol_MEA": prior,
                "loading_mol_CO2_per_mol_MEA": current,
                "observed_heat_release_kj_per_mol_CO2": observed,
                "predicted_heat_release_kj_per_mol_CO2": ""
                if predicted is None
                else predicted,
                "residual_kj_per_mol_CO2": ""
                if predicted is None
                else predicted - observed,
                "status": status,
                "failure_code": failure_code,
            }
        )

    curve: list[dict[str, object]] = []
    for temperature_c in sorted(endpoints):
        by_loading: dict[float, list[float]] = {}
        for row in comparison:
            if row["temperature_C"] != temperature_c or row["status"] != "evaluated":
                continue
            loading = float(row["loading_mol_CO2_per_mol_MEA"])
            by_loading.setdefault(loading, []).append(
                float(row["predicted_heat_release_kj_per_mol_CO2"])
            )
        paired = sorted(
            (loading, statistics.fmean(values))
            for loading, values in by_loading.items()
        )
        if len(paired) < 3:
            continue
        loading = np.asarray([item[0] for item in paired])
        heat = np.asarray([item[1] for item in paired])
        interpolator = PchipInterpolator(loading, heat)
        grid = np.linspace(loading[0], loading[-1], 180)
        curve.extend(
            {
                "temperature_C": temperature_c,
                "loading_mol_CO2_per_mol_MEA": float(x),
                "heat_release_kj_per_mol_CO2": float(y),
                "construction": "PCHIP interpolation of scored finite-interval predictions",
            }
            for x, y in zip(grid, interpolator(grid), strict=True)
        )

    evaluated = [row for row in comparison if row["status"] == "evaluated"]
    residuals = [float(row["residual_kj_per_mol_CO2"]) for row in evaluated]
    summary = {
        "schema": "mea.selected-bundle-direct-total-enthalpy-calorimetry.v1",
        "status": "fixed_bundle_zero_vapor_ideal_co2_feed_reconstruction",
        "engine_source_commit": ENGINE_COMMIT,
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "parameter_document_sha256": file_sha256(PARAMETERS),
        "thermochemistry_fingerprint": thermochemistry.scientific_fingerprint,
        "assumptions": [
            "calorimeter finite vapor inventory is zero",
            "incoming CO2 has the same ideal/reference enthalpy gauge and zero residual enthalpy",
            "reported heat is compared to the finite loading interval declared by each retained observation",
        ],
        "attempted_endpoint_states": sum(len(value) for value in endpoints.values()),
        "evaluated_endpoint_states": len(states),
        "failed_endpoint_states": len(failures),
        "total_solver_attempts": len(attempt_rows),
        "failed_solver_attempts_before_recovery": sum(
            row["status"] != "evaluated" for row in attempt_rows
        ),
        "attempted_observations": len(comparison),
        "evaluated_observations": len(evaluated),
        "rmse_kj_per_mol_CO2": math.sqrt(
            statistics.fmean(value * value for value in residuals)
        ),
        "mean_bias_kj_per_mol_CO2": statistics.fmean(residuals),
        "median_absolute_error_kj_per_mol_CO2": statistics.median(map(abs, residuals)),
        "by_temperature_C": {
            str(temperature): residual_metrics(
                [row for row in comparison if row["temperature_C"] == temperature]
            )
            for temperature in sorted(endpoints)
        },
        "by_campaign_partition": {
            partition: residual_metrics(
                [row for row in comparison if row["campaign_partition"] == partition]
            )
            for partition in sorted(
                {str(row["campaign_partition"]) for row in comparison}
            )
        },
        "by_source": {
            source: residual_metrics(
                [row for row in comparison if row["source"] == source]
            )
            for source in sorted({str(row["source"]) for row in comparison})
        },
        "observations_sha256": file_sha256(OBSERVATIONS),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    write_rows(
        RESULTS / "current-selected-direct-enthalpy-states.csv",
        sorted(
            state_rows,
            key=lambda row: (
                float(row["temperature_C"]),
                float(row["loading_mol_CO2_per_mol_MEA"]),
            ),
        ),
    )
    write_rows(RESULTS / "current-selected-direct-enthalpy-attempts.csv", attempt_rows)
    write_rows(RESULTS / "current-selected-direct-enthalpy-comparison.csv", comparison)
    write_rows(RESULTS / "current-selected-direct-enthalpy-curve.csv", curve)
    (RESULTS / "current-selected-reference-thermochemistry.json").write_text(
        json.dumps(thermochemistry_payload, indent=2) + "\n", encoding="utf-8"
    )
    (RESULTS / "current-selected-direct-enthalpy-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    apply_plot_theme()
    fig, ax = plt.subplots(figsize=(9.0, 5.7))
    colors = {40: "#0072B2", 80: "#009E73", 120: "#D55E00"}
    markers = {40: "o", 80: "s", 120: "^"}
    for temperature_c in sorted(endpoints):
        values = [row for row in curve if row["temperature_C"] == temperature_c]
        ax.plot(
            [row["loading_mol_CO2_per_mol_MEA"] for row in values],
            [row["heat_release_kj_per_mol_CO2"] for row in values],
            color=colors[temperature_c],
            linewidth=2.0,
            label=f"Model, {temperature_c} °C",
        )
        data = [row for row in comparison if row["temperature_C"] == temperature_c]
        ax.scatter(
            [row["loading_mol_CO2_per_mol_MEA"] for row in data],
            [row["observed_heat_release_kj_per_mol_CO2"] for row in data],
            marker=markers[temperature_c],
            color=colors[temperature_c],
            edgecolor="black",
            linewidth=0.4,
            s=36,
            alpha=0.72,
            label=f"Data, {temperature_c} °C",
        )
    ax.set(
        xlabel="CO$_2$ loading (mol mol$^{-1}$ MEA)",
        ylabel="Heat release magnitude (kJ mol$^{-1}$ CO$_2$)",
        title="Current fixed-bundle absorption heat",
    )
    ax.grid(alpha=0.2)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    png, svg, pdf = save_figure_bundle(
        fig, FIGURES / "current-selected-direct-enthalpy"
    )
    write_mpl_sidecar(
        FIGURES / "current-selected-direct-enthalpy.mpl.yaml",
        png_name=png.name,
        svg_name=svg.name,
        pdf_name=pdf.name,
        title="Current fixed-bundle absorption heat",
        description="Retained calorimetry observations as points and fixed-bundle total-enthalpy model curves.",
        data_path=RESULTS / "current-selected-direct-enthalpy-curve.csv",
    )
    with (FIGURES / "current-selected-direct-enthalpy.mpl.yaml").open(
        "a", encoding="utf-8"
    ) as stream:
        stream.write(
            f"comparison_path: {repo_relative_path(RESULTS / 'current-selected-direct-enthalpy-comparison.csv')}\n"
        )
        stream.write(
            f"comparison_sha256: {file_sha256(RESULTS / 'current-selected-direct-enthalpy-comparison.csv')}\n"
        )
        stream.write(
            "continuity: model line is a PCHIP interpolation of the scored finite-interval predictions\n"
        )
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
