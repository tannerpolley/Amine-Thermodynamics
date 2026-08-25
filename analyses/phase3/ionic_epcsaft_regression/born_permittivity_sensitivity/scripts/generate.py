from __future__ import annotations

import csv
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

import epcsaft
from epcsaft import equilibrium

from MEA.common.analysis_io import write_csv_rows as _write_csv
from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, parameter_mapping
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


ANALYSIS = Path(__file__).resolve().parents[1]
REPO = ANALYSIS.parents[3]
SOURCE = (
    REPO
    / "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
)
DENSITY_SOURCE = (
    REPO
    / "data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv"
)
ENGINE_LOCK = REPO / "data/reference/MEA/manifests/engine_artifact_lock.json"
RESULTS = ANALYSIS / "results"
TEMPERATURE_K = 313.15
PRESSURE_PA = 101_325.0
MEA_MASS_FRACTION = 0.30
LOADINGS = (0.11, 0.21, 0.40, 0.60, 0.78, 0.99)
CHARGES = (0, 0, 0, 1, -1, -1, -2, 1, -1)
CONFIGURATIONS = (
    (
        "original_born_no_induced",
        "Original Born, solvent-only permittivity, no induced association",
        "solvent-only",
        0.0,
        0.0,
        False,
    ),
    (
        "original_born_solvent_only",
        "Original Born, solvent-only permittivity, induced association",
        "solvent-only",
        0.0,
        0.0,
        True,
    ),
    (
        "shell_born_ion_suppressed_no_induced",
        "Shell Born, ion-suppressed permittivity, no induced association",
        "ion-fraction-suppression",
        1.0,
        1.0,
        False,
    ),
    (
        "shell_born_ion_suppressed",
        "Shell Born, ion-suppressed permittivity, induced association",
        "ion-fraction-suppression",
        1.0,
        1.0,
        True,
    ),
)
SPECIES_COEFFICIENTS = {
    "CO2": {"carbon-dioxide": 1.0},
    "MEA": {"monoethanolamine": 1.0},
    "MEAH+": {"protonated-monoethanolamine": 1.0},
    "MEA + MEAH+": {"monoethanolamine": 1.0, "protonated-monoethanolamine": 1.0},
    "MEACOO-": {"carbamate-anion": 1.0},
    "HCO3-": {"bicarbonate-anion": 1.0},
    "CO3^2-": {"carbonate-anion": 1.0},
}


def _canonical_sha256(mapping: dict[str, object]) -> str:
    payload = json.dumps(mapping, separators=(",", ":"), sort_keys=True).encode()
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _configuration(
    permittivity: str,
    c_shell: float,
    c_dielectric: float,
    induced_association: bool,
    ion_specific_suppression: dict[str, float] | None = None,
) -> tuple[epcsaft.Parameters, dict[str, object]]:
    mapping = deepcopy(
        parameter_mapping(
            permittivity=permittivity,
            ion_specific_suppression=ion_specific_suppression,
        )
    )
    for family in mapping["model_families"]:
        if family["kind"] == "electrolyte":
            family["c_shell"] = c_shell
            family["c_dielectric"] = c_dielectric
    if not induced_association:
        mapping["topology"]["sites"] = [
            site
            for site in mapping["topology"]["sites"]
            if site["component_id"] != "carbon-dioxide"
        ]
        mapping["topology"]["edges"] = [
            edge
            for edge in mapping["topology"]["edges"]
            if all(
                edge[endpoint]["component_id"] != "carbon-dioxide"
                for endpoint in ("endpoint_a", "endpoint_b")
            )
        ]
    return (
        epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS),
        mapping,
    )


def _source_states() -> list[dict[str, object]]:
    grouped: dict[float, list[dict[str, str]]] = {loading: [] for loading in LOADINGS}
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            loading = float(row["co2_loading_mol_per_mol_mea"])
            if (
                row["source_key"] == "Jakobsen2005"
                and math.isclose(float(row["temperature_K"]), TEMPERATURE_K)
                and math.isclose(float(row["mea_mass_fraction"]), MEA_MASS_FRACTION)
                and loading in grouped
            ):
                grouped[loading].append(row)
    if any(not rows for rows in grouped.values()):
        raise RuntimeError("one or more declared Jakobsen states are missing")
    return [{"loading": loading, "rows": grouped[loading]} for loading in LOADINGS]


def _unloaded_density_kg_m3() -> tuple[float, float]:
    with DENSITY_SOURCE.open(newline="", encoding="utf-8") as stream:
        matches = [
            row
            for row in csv.DictReader(stream)
            if row["property"] == "density"
            and math.isclose(float(row["temperature_C"]), 40.0)
            and math.isclose(float(row["mea_mass_fraction"]), MEA_MASS_FRACTION)
            and not row["co2_loading_mol_per_mol_mea"]
        ]
    if len(matches) != 1:
        raise RuntimeError("expected one Amundsen unloaded density row")
    return float(matches[0]["value"]) * 1000.0, float(
        matches[0]["uncertainty_value"]
    ) * 1000.0


def _observation_rows() -> tuple[equilibrium.HomogeneousReactiveObservationRow, ...]:
    return tuple(
        equilibrium.HomogeneousReactiveObservationRow(
            f"mole-fraction-{component_id}",
            "mole_fraction",
            tuple(
                1.0 if index == selected else 0.0 for index in range(len(COMPONENT_IDS))
            ),
            support="positive",
        )
        for selected, component_id in enumerate(COMPONENT_IDS)
    )


def _failure_record(
    configuration_id: str,
    configuration_name: str,
    loading: float,
    runtime_seconds: float,
    error: Exception,
    start_budget: int,
) -> dict[str, object]:
    diagnostics = getattr(error, "diagnostics", None)
    return {
        "configuration_id": configuration_id,
        "configuration_name": configuration_name,
        "temperature_k": TEMPERATURE_K,
        "pressure_pa": PRESSURE_PA,
        "mea_mass_fraction": MEA_MASS_FRACTION,
        "loading_mol_co2_per_mol_mea": loading,
        "status": "non_evaluable",
        "start_budget": start_budget,
        "runtime_seconds": runtime_seconds,
        "failure_reason": str(error),
        "solver_status": getattr(diagnostics, "solver_status", ""),
        "search_status": getattr(getattr(diagnostics, "search", None), "status", ""),
        "first_failed_numerical_criterion": getattr(
            diagnostics, "first_failed_numerical_criterion", ""
        ),
        "first_failed_physical_criterion": getattr(
            diagnostics, "first_failed_physical_criterion", ""
        ),
    }


def _evaluate_configuration(
    configuration_id: str,
    configuration_name: str,
    parameters: epcsaft.Parameters,
    source_states: list[dict[str, object]],
) -> list[dict[str, object]]:
    result_rows: list[dict[str, object]] = []
    previous_reference = None
    observation_rows = _observation_rows()
    model = epcsaft.Mixture(parameters)
    molar_masses = {
        component["component_id"]: float(
            component["fixed"]["molar_mass"]["value"]["magnitude"]
        )
        for component in parameters.to_mapping()["components"]
    }
    for state in source_states:
        loading = float(state["loading"])
        started = time.monotonic()
        problem = None
        error: Exception | None = None
        used_budget = 2
        used_reference = False
        for budget, initial_reference in (
            (2, previous_reference),
            (5, None),
        ):
            used_budget = budget
            used_reference = initial_reference is not None
            try:
                problem = build_homogeneous_reactive_problem(
                    parameters,
                    identity=f"born-permittivity-{configuration_id}-{loading:g}",
                    phase_identity="mea-nine-species-liquid",
                    continuation_identity=f"born-permittivity-{configuration_id}-branch",
                    temperature_k=TEMPERATURE_K,
                    pressure_pa=PRESSURE_PA,
                    mea_mass_fraction_unloaded=MEA_MASS_FRACTION,
                    loading_mol_co2_per_mol_mea=loading,
                    maximum_log_composition_distance=2.0,
                    maximum_log_volume_distance=2.0,
                    solver_options={
                        "maximum_iterations": 100,
                        "convergence_tolerance": 1.0e-6,
                        "primary_start_budget": budget,
                    },
                    initial_reference=initial_reference,
                )
                break
            except (
                RuntimeError,
                ValueError,
                equilibrium.ChemicalEquilibriumError,
            ) as caught:
                error = caught
        if problem is None:
            assert error is not None
            result_rows.append(
                _failure_record(
                    configuration_id,
                    configuration_name,
                    loading,
                    time.monotonic() - started,
                    error,
                    used_budget,
                )
            )
            print(
                json.dumps(
                    {
                        "configuration": configuration_id,
                        "loading": loading,
                        "status": "non_evaluable",
                        "runtime_seconds": result_rows[-1]["runtime_seconds"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            continue
        descriptor = equilibrium.homogeneous_reactive_observation_descriptor(
            problem, observation_rows
        )
        evaluated = equilibrium.evaluate_homogeneous_reactive_observations(
            problem,
            TEMPERATURE_K * epcsaft.unit_registry.kelvin,
            PRESSURE_PA * epcsaft.unit_registry.pascal,
            descriptor,
        )
        if (
            evaluated.status != "evaluated"
            or evaluated.state is None
            or evaluated.diagnostics is None
        ):
            error = RuntimeError(
                str(evaluated.failure or "observation evaluation failed")
            )
            result_rows.append(
                _failure_record(
                    configuration_id,
                    configuration_name,
                    loading,
                    time.monotonic() - started,
                    error,
                    used_budget,
                )
            )
            continue
        state_result = evaluated.state
        eos_state = model.state(
            T=TEMPERATURE_K * epcsaft.unit_registry.kelvin,
            rho=state_result.molar_density_mol_per_m3
            * epcsaft.unit_registry.mole
            / epcsaft.unit_registry.meter**3,
            x=state_result.mole_fractions,
        )
        average_molar_mass = math.fsum(
            mole_fraction * molar_masses[component_id]
            for component_id, mole_fraction in zip(
                COMPONENT_IDS, state_result.mole_fractions, strict=True
            )
        )
        diagnostics = evaluated.diagnostics
        record: dict[str, object] = {
            "configuration_id": configuration_id,
            "configuration_name": configuration_name,
            "temperature_k": TEMPERATURE_K,
            "pressure_pa": PRESSURE_PA,
            "mea_mass_fraction": MEA_MASS_FRACTION,
            "loading_mol_co2_per_mol_mea": loading,
            "status": "evaluated",
            "start_budget": used_budget,
            "continuation_reference_used": used_reference,
            "runtime_seconds": time.monotonic() - started,
            "failure_reason": "",
            "solver_status": diagnostics.solver_status,
            "search_status": diagnostics.search.status,
            "first_failed_numerical_criterion": "",
            "first_failed_physical_criterion": "",
            "molar_density_mol_m3": state_result.molar_density_mol_per_m3,
            "mass_density_kg_m3": state_result.molar_density_mol_per_m3
            * average_molar_mass,
            "packing_fraction": diagnostics.packing_fraction,
            "ion_mole_fraction": math.fsum(
                value
                for value, charge in zip(
                    state_result.mole_fractions, CHARGES, strict=True
                )
                if charge
            ),
            "bulk_relative_permittivity": eos_state.bulk_relative_permittivity,
            "born_a_over_rt": eos_state.born,
            "debye_huckel_a_over_rt": eos_state.debye_huckel,
            "balance_inf_norm": diagnostics.balance_inf_norm,
            "charge_inf_norm": diagnostics.charge_inf_norm,
            "pressure_relative_residual": diagnostics.pressure_relative_residual,
            "reaction_affinity_inf_norm": diagnostics.reaction_affinity_inf_norm,
            "kkt_stationarity_inf_norm": diagnostics.kkt_stationarity_inf_norm,
            "condition_number_inf": diagnostics.condition_number_inf,
        }
        record.update(
            {
                f"x_{component_id}": value
                for component_id, value in zip(
                    COMPONENT_IDS, state_result.mole_fractions, strict=True
                )
            }
        )
        result_rows.append(record)
        previous_reference = problem.continuation_reference
        print(
            json.dumps(
                {
                    "configuration": configuration_id,
                    "loading": loading,
                    "status": "evaluated",
                    "density_kg_m3": record["mass_density_kg_m3"],
                    "runtime_seconds": record["runtime_seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    return result_rows


def _speciation_rows(
    state_rows: list[dict[str, object]],
    source_states: list[dict[str, object]],
    configurations: tuple[tuple[object, ...], ...] = CONFIGURATIONS,
) -> list[dict[str, object]]:
    by_key = {
        (str(row["configuration_id"]), float(row["loading_mol_co2_per_mol_mea"])): row
        for row in state_rows
    }
    output: list[dict[str, object]] = []
    for configuration_id, configuration_name, *_ in configurations:
        for state in source_states:
            loading = float(state["loading"])
            model_state = by_key[(configuration_id, loading)]
            for source in state["rows"]:
                species = source["species"]
                if (
                    source["measurement_role"]
                    not in {"direct_positive", "aggregate_direct_positive"}
                    or species not in SPECIES_COEFFICIENTS
                    or float(source["value_mole_fraction"]) <= 0.0
                ):
                    continue
                observed = float(source["value_mole_fraction"])
                predicted = None
                log10_ratio = None
                if model_state["status"] == "evaluated":
                    predicted = math.fsum(
                        coefficient * float(model_state[f"x_{component_id}"])
                        for component_id, coefficient in SPECIES_COEFFICIENTS[
                            species
                        ].items()
                    )
                    if predicted > 0.0:
                        log10_ratio = math.log10(predicted / observed)
                output.append(
                    {
                        "configuration_id": configuration_id,
                        "configuration_name": configuration_name,
                        "loading_mol_co2_per_mol_mea": loading,
                        "source_key": source["source_key"],
                        "source_record_id": source["record_id"],
                        "species": species,
                        "measurement_role": source["measurement_role"],
                        "observed_mole_fraction": observed,
                        "predicted_mole_fraction": predicted,
                        "log10_model_over_observed": log10_ratio,
                        "state_status": model_state["status"],
                    }
                )
    return output


def main() -> None:
    started = time.monotonic()
    source_states = _source_states()
    state_rows: list[dict[str, object]] = []
    parameter_rows: list[dict[str, object]] = []
    for (
        configuration_id,
        configuration_name,
        permittivity,
        c_shell,
        c_dielectric,
        induced_association,
    ) in CONFIGURATIONS:
        parameters, mapping = _configuration(
            permittivity, c_shell, c_dielectric, induced_association
        )
        parameter_rows.append(
            {
                "configuration_id": configuration_id,
                "configuration_name": configuration_name,
                "relative_permittivity_formulation": permittivity,
                "born_c_shell": c_shell,
                "born_c_dielectric": c_dielectric,
                "co2_water_induced_association": induced_association,
                "ionic_region_relative_permittivity": 8.0,
                "ion_fraction_suppression_coefficient": 7.01
                if permittivity == "ion-fraction-suppression"
                else "",
                "parameter_mapping_sha256": _canonical_sha256(mapping),
            }
        )
        state_rows.extend(
            _evaluate_configuration(
                configuration_id, configuration_name, parameters, source_states
            )
        )
    speciation_rows = _speciation_rows(state_rows, source_states)
    RESULTS.mkdir(parents=True, exist_ok=True)
    _write_csv(RESULTS / "state_results.csv", state_rows)
    _write_csv(RESULTS / "speciation_comparison.csv", speciation_rows)
    _write_csv(RESULTS / "parameter_table.csv", parameter_rows)
    unloaded_density, unloaded_density_uncertainty = _unloaded_density_kg_m3()
    summaries = []
    for configuration_id, configuration_name, *_ in CONFIGURATIONS:
        states = [
            row for row in state_rows if row["configuration_id"] == configuration_id
        ]
        evaluated = [row for row in states if row["status"] == "evaluated"]
        residuals = [
            abs(float(row["log10_model_over_observed"]))
            for row in speciation_rows
            if row["configuration_id"] == configuration_id
            and row["log10_model_over_observed"] not in (None, "")
        ]
        summaries.append(
            {
                "configuration_id": configuration_id,
                "configuration_name": configuration_name,
                "state_count": len(states),
                "evaluated_state_count": len(evaluated),
                "failed_state_count": len(states) - len(evaluated),
                "minimum_mass_density_kg_m3": min(
                    (float(row["mass_density_kg_m3"]) for row in evaluated),
                    default=None,
                ),
                "maximum_mass_density_kg_m3": max(
                    (float(row["mass_density_kg_m3"]) for row in evaluated),
                    default=None,
                ),
                "minimum_bulk_relative_permittivity": min(
                    (float(row["bulk_relative_permittivity"]) for row in evaluated),
                    default=None,
                ),
                "maximum_bulk_relative_permittivity": max(
                    (float(row["bulk_relative_permittivity"]) for row in evaluated),
                    default=None,
                ),
                "median_absolute_speciation_log10_ratio": statistics.median(residuals)
                if residuals
                else None,
                "typical_speciation_factor": 10.0 ** statistics.median(residuals)
                if residuals
                else None,
                "maximum_balance_inf_norm": max(
                    (float(row["balance_inf_norm"]) for row in evaluated), default=None
                ),
                "maximum_charge_inf_norm": max(
                    (float(row["charge_inf_norm"]) for row in evaluated), default=None
                ),
                "maximum_pressure_relative_residual": max(
                    (float(row["pressure_relative_residual"]) for row in evaluated),
                    default=None,
                ),
                "maximum_reaction_affinity_inf_norm": max(
                    (float(row["reaction_affinity_inf_norm"]) for row in evaluated),
                    default=None,
                ),
            }
        )
    lock = json.loads(ENGINE_LOCK.read_text(encoding="utf-8"))
    module_path = Path(epcsaft.__file__).resolve()
    summary = {
        "schema": "mea.born-induced-association-sensitivity.v3",
        "status": "completed",
        "temperature_k": TEMPERATURE_K,
        "pressure_pa": PRESSURE_PA,
        "mea_mass_fraction": MEA_MASS_FRACTION,
        "loadings_mol_co2_per_mol_mea": list(LOADINGS),
        "source_speciation": "Jakobsen et al. (2005), canonical MEA source rows",
        "unloaded_density_reference_kg_m3": unloaded_density,
        "unloaded_density_uncertainty_kg_m3": unloaded_density_uncertainty,
        "density_reference_scope": "unloaded 30 wt% MEA-water at 313.15 K; scale comparison only",
        "engine_wheel_sha256": lock["wheel_sha256"],
        "installed_epcsaft_module_sha256": hashlib.sha256(
            module_path.read_bytes()
        ).hexdigest(),
        "runtime_seconds": time.monotonic() - started,
        "configurations": summaries,
        "claim": "fixed-parameter Born-formulation by induced-association sensitivity; no parameter promotion",
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
