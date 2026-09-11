"""Evaluate fixed-bundle finite-dose absorption heat from Engine total enthalpy."""

from __future__ import annotations

import csv
import copy
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from time import perf_counter

import epcsaft
import matplotlib.pyplot as plt
import numpy as np
from epcsaft import equilibrium
from scipy.interpolate import PchipInterpolator

from shared_evaluation import (
    ENGINE_COMMIT,
    ENGINE_WHEEL_SHA256,
    PARAMETERS,
    SOURCE_CONTRACT,
    STATE_PACKET,
    EvaluationLimits,
    anchor_from,
    cached_anchors,
    corrected_request,
    evaluate_state,
    load_state_packet,
    verify_wheel,
)
from result_freshness import source_hashes, stamp_results
from refresh_results import bounded_main
from MEA.common.analysis_io import file_sha256, repo_relative_path
from MEA.common.plot_style import (
    apply_plot_theme,
    save_figure_bundle,
    write_mpl_sidecar,
)


ANALYSIS = Path(__file__).resolve().parents[1]
COMMON_SOURCE = ANALYSIS.parents[1] / "src/MEA/common"
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def residual_metrics(rows: list[dict[str, object]]) -> dict[str, float | int | None]:
    evaluated = [row for row in rows if row["status"] == "evaluated"]
    residuals = [float(row["residual_kj_per_mol_CO2"]) for row in evaluated]
    return {
        "attempted": len(rows),
        "evaluated": len(evaluated),
        "rmse_kj_per_mol_CO2": math.sqrt(
            statistics.fmean(value * value for value in residuals)
        )
        if residuals
        else None,
        "mean_bias_kj_per_mol_CO2": statistics.fmean(residuals) if residuals else None,
        "median_absolute_error_kj_per_mol_CO2": statistics.median(map(abs, residuals))
        if residuals
        else None,
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


# Neutral thermal anchors. Units: J/mol/K for cp, J/mol for enthalpy, T in K.
# CO2: ideal-gas Shomate cp (Chase 1998 via NIST WebBook, 298-1200 K) and
# CODATA gas formation enthalpy; the ideal gas has zero EOS residual.
# H2O, MEA: pure-liquid cp correlations retained by MEA-Absorption-Column
# (Hilliard 2008, kJ/kg/K in t = T - 273.15 C) minus the Engine's own pure
# liquid residual cp at 1 atm, so the model liquid cp equals the correlation
# and the residual is not counted twice. Formation enthalpies pin the liquid
# at 298.15 K, 1 atm: CODATA H2O(l) and NIST WebBook (Baroody and Carpenter
# 1972) MEA(l). Formation constants are conserved-component gauges; the
# temperature dependence is the physical content.
ANCHOR_SOURCES = {
    "carbon-dioxide": {
        "cp": "NIST WebBook Shomate, Chase 1998, gas, 298-1200 K",
        "cp_kind": "ideal_gas_shomate",
        "shomate": (24.99735, 55.18696, -33.69137, 7.948387, -0.136638),
        "formation_enthalpy_j_per_mol": -393510.0,
        "formation_source": "CODATA (Cox, Wagman et al. 1984), gas, 298.15 K",
        "basis": "ideal gas; residual enthalpy zero",
    },
    "water": {
        "cp": "Hilliard 2008 liquid cp polynomial as retained in MEA-Absorption-Column appendix_properties.tex; kJ/kg/K, t in C",
        "cp_kind": "liquid_correlation_minus_eos_residual",
        "liquid_cp_kj_kg_k": (4.2107, -1.696e-3, 2.568e-5, -1.095e-7, 3.038e-10),
        "molar_mass_kg_per_mol": 0.018015,
        "formation_enthalpy_j_per_mol": -285830.0,
        "formation_source": "CODATA H2O(l), 298.15 K, 1 atm",
        "basis": "pure liquid at 101325 Pa; correlation range per Hilliard 2008 not re-verified here",
    },
    "monoethanolamine": {
        "cp": "Hilliard 2008 liquid cp polynomial as retained in MEA-Absorption-Column appendix_properties.tex; kJ/kg/K, t in C",
        "cp_kind": "liquid_correlation_minus_eos_residual",
        "liquid_cp_kj_kg_k": (2.6161, 3.706e-3, 3.787e-6, 0.0, 0.0),
        "molar_mass_kg_per_mol": 0.061084,
        "formation_enthalpy_j_per_mol": -507500.0,
        "formation_source": "NIST WebBook, Baroody and Carpenter 1972, MEA(l), 298.15 K",
        "basis": "pure liquid at 101325 Pa; correlation range per Hilliard 2008 not re-verified here",
    },
}
ANCHOR_PRESSURE_PA = 101325.0
FORMATION_TEMPERATURE_K = 298.15
REFERENCE_DOMAIN_K = (
    293.15,
    393.15,
)  # source-reference transfer is outside the EOS domain above 393.15 K at 1 bar
REFERENCE_GRID_STEP_K = 2.5
REFERENCE_POLYNOMIAL_DEGREE = 8
CHARGE_GAUGE = "hydronium reference enthalpy equals water reference enthalpy at every temperature (zero-enthalpy proton)"
VANT_HOFF_ABS_TOLERANCE_J_PER_MOL = 1.0e-3  # half the Engine admissibility tolerance


def _shomate(temperature_k: float, coefficients: tuple[float, ...]) -> float:
    a, b, c, d, e = coefficients
    t = temperature_k / 1000.0
    return a + b * t + c * t * t + d * t**3 + e / (t * t)


def anchor_heat_capacity(
    model: epcsaft.Mixture, component_id: str, temperature_k: float
) -> float:
    """Reference cp of one neutral anchor, J/mol/K."""
    spec = ANCHOR_SOURCES[component_id]
    if spec["cp_kind"] == "ideal_gas_shomate":
        return _shomate(temperature_k, spec["shomate"])
    t = temperature_k - 273.15
    liquid = (
        1000.0
        * spec["molar_mass_kg_per_mol"]
        * math.fsum(a * t**k for k, a in enumerate(spec["liquid_cp_kj_kg_k"]))
    )
    x = [1.0 if c == component_id else 0.0 for c in model.component_ids]
    state = model.state(
        T=temperature_k * epcsaft.unit_registry.kelvin,
        P=ANCHOR_PRESSURE_PA * epcsaft.unit_registry.pascal,
        x=x,
        phase="liquid",
    )
    residual = state.cpres()
    if residual is None:
        raise ValueError(
            f"EOS residual cp unavailable for {component_id} at {temperature_k} K"
        )
    return liquid - float(residual.magnitude)


def anchor_enthalpy_at_formation(model: epcsaft.Mixture, component_id: str) -> float:
    """Reference enthalpy at 298.15 K so the anchored phase carries its formation enthalpy."""
    spec = ANCHOR_SOURCES[component_id]
    if spec["cp_kind"] == "ideal_gas_shomate":
        return float(spec["formation_enthalpy_j_per_mol"])
    x = [1.0 if c == component_id else 0.0 for c in model.component_ids]
    state = model.state(
        T=FORMATION_TEMPERATURE_K * epcsaft.unit_registry.kelvin,
        P=ANCHOR_PRESSURE_PA * epcsaft.unit_registry.pascal,
        x=x,
        phase="liquid",
    )
    return float(spec["formation_enthalpy_j_per_mol"]) - float(
        state._residual_enthalpy.magnitude
    )


def exact_reference_enthalpies(
    model: epcsaft.Mixture,
    templates: dict[int, list[tuple[float, dict[str, object]]]],
    reaction_values: dict[str, float],
    temperature_k: float,
    anchor_enthalpies: dict[str, float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve the nine references at one temperature: 5 reactions + 3 anchors + 1 gauge."""
    request = copy.deepcopy(templates[80][0][1])
    request["temperature"]["value"] = temperature_k
    problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
        corrected_request(request, reaction_values)
    )
    rows = np.asarray(problem.reaction_system.reaction_matrix, dtype=float)
    q_reaction = transformed_reaction_enthalpies(model, problem)
    ids = list(model.component_ids)
    anchors = np.eye(len(ids))[[ids.index(c) for c in ANCHOR_SOURCES]]
    gauge = np.zeros(len(ids))
    gauge[ids.index("hydronium-cation")] = 1.0
    gauge[ids.index("water")] = -1.0
    system = np.vstack([rows, anchors, gauge[None, :]])
    rhs = np.concatenate(
        [q_reaction, [anchor_enthalpies[c] for c in ANCHOR_SOURCES], [0.0]]
    )
    return np.linalg.solve(system, rhs), q_reaction, rows


def build_thermochemistry(
    model: epcsaft.Mixture,
    templates: dict[int, list[tuple[float, dict[str, object]]]],
    reaction_values: dict[str, float],
) -> tuple[epcsaft.ReferenceThermochemistry, dict[str, object]]:
    """Continuous anchored species references on the Engine's polynomial form.

    At every grid temperature the nine reference enthalpies are the unique
    solution of the five typed reaction constraints, three neutral thermal
    anchors, and one charge gauge.  Each component's h(T) is then fitted with
    one polynomial whose derivative is the declared cp polynomial, and the
    fit is verified against fresh exact reaction enthalpies between grid
    points at half the Engine's van't Hoff tolerance.
    """
    from scipy.integrate import cumulative_simpson

    grid = np.arange(
        REFERENCE_DOMAIN_K[0], REFERENCE_DOMAIN_K[1] + 1e-9, REFERENCE_GRID_STEP_K
    )
    formation = {c: anchor_enthalpy_at_formation(model, c) for c in ANCHOR_SOURCES}
    # cp on a 0.5 K grid, integrated by Simpson from the formation temperature.
    fine = np.arange(REFERENCE_DOMAIN_K[0], REFERENCE_DOMAIN_K[1] + 1e-9, 0.5)
    anchor_h: dict[str, dict[float, float]] = {}
    for c in ANCHOR_SOURCES:
        cp = np.asarray([anchor_heat_capacity(model, c, float(T)) for T in fine])
        integral = cumulative_simpson(cp, x=fine, initial=0.0)
        at_formation = float(np.interp(FORMATION_TEMPERATURE_K, fine, integral))
        h_fine = formation[c] + integral - at_formation
        anchor_h[c] = {float(T): float(np.interp(T, fine, h_fine)) for T in grid}
    exact = []
    for temperature_k in grid:
        h, _, rows = exact_reference_enthalpies(
            model,
            templates,
            reaction_values,
            float(temperature_k),
            {c: anchor_h[c][float(temperature_k)] for c in ANCHOR_SOURCES},
        )
        exact.append(h)
    exact = np.asarray(exact)
    theta = grid - REFERENCE_TEMPERATURE_K
    components = []
    component_records = []
    for index, component_id in enumerate(model.component_ids):
        coefficients = np.polynomial.polynomial.polyfit(
            theta, exact[:, index], REFERENCE_POLYNOMIAL_DEGREE
        )
        reference = float(coefficients[0])
        cp_coefficients = tuple(
            float((k + 1) * coefficients[k + 1])
            for k in range(REFERENCE_POLYNOMIAL_DEGREE)
        )
        fit_residual = float(
            np.max(
                np.abs(
                    np.polynomial.polynomial.polyval(theta, coefficients)
                    - exact[:, index]
                )
            )
        )
        component_records.append(
            {
                "component_id": component_id,
                "reference_enthalpy_j_per_mol": reference,
                "cp_coefficients_j_per_mol_k": list(cp_coefficients),
                "max_fit_residual_j_per_mol": fit_residual,
                "role": "neutral_anchor"
                if component_id in ANCHOR_SOURCES
                else "reaction_and_gauge_determined",
            }
        )
        components.append(
            epcsaft.ComponentReferenceThermochemistry(
                component_id,
                "mea-anchored-reaction-consistent-reference-v2",
                REFERENCE_TEMPERATURE_K,
                reference,
                epcsaft.IdealHeatCapacityPolynomial(
                    f"{component_id}-anchored-cp", cp_coefficients, REFERENCE_DOMAIN_K
                ),
            )
        )
    # Verify between grid points against fresh exact reaction enthalpies.
    worst = 0.0
    for temperature_k in np.arange(
        REFERENCE_DOMAIN_K[0] + 1.0, REFERENCE_DOMAIN_K[1], 4.0
    ):
        _, q_reaction, rows = exact_reference_enthalpies(
            model, templates, reaction_values, float(temperature_k), formation
        )
        h = np.asarray([c.enthalpy_j_per_mol(float(temperature_k)) for c in components])
        worst = max(worst, float(np.max(np.abs(rows @ h - q_reaction))))
    if worst > VANT_HOFF_ABS_TOLERANCE_J_PER_MOL:
        raise ValueError(
            f"anchored reference violates reaction consistency between grid points by {worst:.3e} J/mol"
        )
    payload = {
        "schema": "mea-anchored-reaction-consistent-reference-thermochemistry-v2",
        "method": "continuous solve of 5 typed reaction enthalpies (source correlation + Engine source-reference transfer) + 3 neutral thermal anchors + 1 charge gauge at every grid temperature; degree-8 polynomial per component on the Engine form",
        "engine_source_commit": ENGINE_COMMIT,
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "reference_temperature_k": REFERENCE_TEMPERATURE_K,
        "temperature_domain_k": list(REFERENCE_DOMAIN_K),
        "grid_step_k": REFERENCE_GRID_STEP_K,
        "polynomial_degree": REFERENCE_POLYNOMIAL_DEGREE,
        "anchor_pressure_pa": ANCHOR_PRESSURE_PA,
        "anchors": {
            c: {k: v for k, v in spec.items()} for c, spec in ANCHOR_SOURCES.items()
        },
        "charge_gauge": CHARGE_GAUGE,
        "component_ids": list(model.component_ids),
        "components": component_records,
        "max_vant_hoff_residual_between_grid_points_j_per_mol": worst,
        "vant_hoff_check_tolerance_j_per_mol": VANT_HOFF_ABS_TOLERANCE_J_PER_MOL,
        "gauge": "conserved-component enthalpy constants are formation-enthalpy pinned; their temperature dependence is anchored by thermal data",
    }
    fingerprint = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    payload["scientific_fingerprint"] = fingerprint
    thermochemistry = epcsaft.ReferenceThermochemistry(
        "mea-anchored-r1-r5-reaction-consistent-gauge-v2",
        fingerprint,
        tuple(model.component_ids),
        tuple(components),
    )
    return thermochemistry, payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-timeout-s", type=float, default=60.0)
    parser.add_argument("--overall-timeout-s", type=float, default=900.0)
    args = parser.parse_args()
    freshness_inputs = source_hashes(
        OBSERVATIONS,
        STATE_PACKET,
        Path(__file__),
        Path(__file__).with_name("shared_evaluation.py"),
        SOURCE_CONTRACT,
        COMMON_SOURCE / "analysis_io.py",
        COMMON_SOURCE / "plot_style.py",
    )
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
    packet = load_state_packet(STATE_PACKET)
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
    failures: dict[tuple[int, float], tuple[str, str]] = {}
    state_rows: list[dict[str, object]] = []
    attempt_rows: list[dict[str, object]] = []
    anchors = cached_anchors(set(endpoints))
    for temperature_c in sorted(endpoints):
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
            record = evaluate_state(
                model,
                request,
                reaction_values,
                f"calorimetry-{temperature_c}C-{loading:.6f}",
                anchors,
                thermochemistry,
                limits=limits,
            )
            attempt_rows.extend(
                {
                    "temperature_C": temperature_c,
                    "loading_mol_CO2_per_mol_MEA": loading,
                    "attempt": attempt_index,
                    "start_kind": attempt.get("kind", ""),
                    "anchor": attempt.get("anchor", ""),
                    "status": attempt.get("status", ""),
                    "failure_code": attempt.get("failure_code", ""),
                    "failure_diagnostic": attempt.get("failure_diagnostic", ""),
                    "wall_s": attempt.get("wall_s", 0.0),
                }
                for attempt_index, attempt in enumerate(record["attempts"], start=1)
            )
            if record["status"] != "evaluated":
                failures[(temperature_c, loading)] = (
                    str(record["failure_code"]),
                    str(record["failure_diagnostic"]),
                )
                print(f"{temperature_c:03d} C {loading:.6f}: {record['status']}")
                continue
            solved_pressure = float(record["predictions"]["system-pressure"])
            total_enthalpy_j = float(record["total_enthalpy_j"])
            states[(temperature_c, loading)] = (total_enthalpy_j, solved_pressure)
            failures.pop((temperature_c, loading), None)
            anchor = anchor_from(record)
            if anchor is not None:
                anchors.append(anchor)
            phase = next(
                phase for phase in record["phases"] if phase["role"] == "liquid"
            )
            state_rows.append(
                {
                    "temperature_C": temperature_c,
                    "loading_mol_CO2_per_mol_MEA": loading,
                    "system_pressure_pa": solved_pressure,
                    "total_liquid_enthalpy_j": total_enthalpy_j,
                    "liquid_amount_mol": record["amount_mol"],
                    "reference_molar_enthalpy_j_per_mol": phase[
                        "reference_molar_enthalpy_j_per_mol"
                    ],
                    "residual_molar_enthalpy_j_per_mol": phase[
                        "residual_molar_enthalpy_j_per_mol"
                    ],
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
    metrics = residual_metrics(comparison)
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
        "rmse_kj_per_mol_CO2": metrics["rmse_kj_per_mol_CO2"],
        "mean_bias_kj_per_mol_CO2": metrics["mean_bias_kj_per_mol_CO2"],
        "median_absolute_error_kj_per_mol_CO2": metrics[
            "median_absolute_error_kj_per_mol_CO2"
        ],
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
            linestyle="--",
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
        description="Retained calorimetry observations as points and dashed fixed-bundle total-enthalpy model curves.",
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
    stamp_results(
        RESULTS / "current-selected-direct-enthalpy-summary.json",
        [
            RESULTS / "current-selected-direct-enthalpy-states.csv",
            RESULTS / "current-selected-direct-enthalpy-attempts.csv",
            RESULTS / "current-selected-direct-enthalpy-comparison.csv",
            RESULTS / "current-selected-direct-enthalpy-curve.csv",
            RESULTS / "current-selected-reference-thermochemistry.json",
            FIGURES / "current-selected-direct-enthalpy.mpl.yaml",
            FIGURES / "current-selected-direct-enthalpy.svg",
            FIGURES / "current-selected-direct-enthalpy.png",
            FIGURES / "current-selected-direct-enthalpy.pdf",
        ],
        inputs=freshness_inputs,
    )
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    bounded_main(main)
