"""Fixed-parameter Born/permittivity structure comparison for reactive MEA."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import epcsaft
from epcsaft import equilibrium

from generate_figure_data import corrected_request, failure_fields, prepared_problem
from run_direct_parameter_campaign import (
    CANONICAL_VLE,
    pressure_catalog as complete_pressure_catalog,
)


ANALYSIS = Path(__file__).resolve().parents[1]
BASELINE = ANALYSIS / "results/selected-current-best-parameters.json"
STATE_PACKET = ANALYSIS / "data/input/state-packet.json"
FOUNDATION = ANALYSIS / "data/input/parameters.json"
RESULTS = ANALYSIS / "results/born-permittivity-study"
ENGINE_COMMIT = "d782cc9de6d7dc3011de27362eb79feb4668c68e"
ENGINE_WHEEL_SHA256 = "11634405821c028a1f85033e495563ae6dc15fc8c19829f73c18ef39d5340989"
ION_IDS = {
    "protonated-monoethanolamine",
    "carbamate-anion",
    "bicarbonate-anion",
    "carbonate-anion",
    "hydronium-cation",
    "hydroxide-anion",
}
NEUTRAL_IDS = {"water", "monoethanolamine", "carbon-dioxide"}
BORN_MODIFIERS = {
    "dMEAHm10": ("protonated-monoethanolamine", 0.9),
    "dMEAHp10": ("protonated-monoethanolamine", 1.1),
    "dMEACOOm10": ("carbamate-anion", 0.9),
    "dMEACOOp10": ("carbamate-anion", 1.1),
    "dHCO3m10": ("bicarbonate-anion", 0.9),
    "dHCO3p10": ("bicarbonate-anion", 1.1),
    "dCO3m10": ("carbonate-anion", 0.9),
    "dCO3p10": ("carbonate-anion", 1.1),
    "dH3Om10": ("hydronium-cation", 0.9),
    "dH3Op10": ("hydronium-cation", 1.1),
    "dOHm10": ("hydroxide-anion", 0.9),
    "dOHp10": ("hydroxide-anion", 1.1),
}
FORMULATIONS = {
    "A": "solvent-only",
    "B": "mole-fraction-component-mixing",
    "C": "mass-fraction-component-mixing",
    "D": "component-permittivity-mixing",
    "E": "ion-fraction-suppression",
    "I": "ion-specific-suppression",
}
SOURCE_SHA256 = {
    "uyan-2015-permittivity-transfer": "1ae7cabd2a7b84f7c543999106be3fa4387e566739cb8defb5e567405b20d9d6",
    "schick-et-al-2023": "958d21b21def89c9d704a0844a01c506809f3a86b5405bda4e07b05d7a3939d3",
    "bulow-2020": "a675d71d754e1dd2de012abab45cb8349b92548e1c2174b68fb783461feca009",
    "bulow-2021-corrigendum": "2f5ef7eb2d2db73337f5670ddc39921c1e9aca73850aed06b00b7e6d4e090b3c",
    "ascani-2021": "9ab259a8dfb27a052fcf49782e6ab75132140d94c5f8f695215a2703f1d010ab",
    "figiel-2025": "a3c940895c530f72f47f22f8c0f4796b5ad37918a4edd274f85497c6dd81ad1f",
    "figiel-2025-supporting-information": "005b38ed566ec3c09b87e1ca3a9dd6eeafc9ba75e1a30b9322291d770bb93895",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _provenance(source_id: str, locator: str) -> dict[str, str]:
    return {
        "domain_id": "mea-diagnostic-293-15-to-393-15-k",
        "locator": locator,
        "source_id": source_id,
    }


def _coefficient(
    component_id: str, family: str, value: float, source_id: str, locator: str
) -> dict[str, object]:
    return {
        "candidate_domain_id": "mea-candidate-293-15-to-393-15-k",
        "family": family,
        "identity": f"component/{component_id}/{family}",
        "provenance": _provenance(source_id, locator),
        "qualification": "candidate_extrapolation",
        "source_sha256": f"sha256:{SOURCE_SHA256[source_id]}",
        "value": {"magnitude": value, "unit": "dimensionless"},
    }


def _co2_permittivity_correlation() -> dict[str, object]:
    source_sha = (
        "sha256:958d21b21def89c9d704a0844a01c506809f3a86b5405bda4e07b05d7a3939d3"
    )
    prefix = "component/carbon-dioxide/relative_permittivity/constant-plus-polynomial-in-temperature"
    return {
        "candidate_domain_id": "mea-candidate-293-15-to-393-15-k",
        "component_id": "carbon-dioxide",
        "constant": {
            "identity": f"{prefix}/constant",
            "value": {"magnitude": 1.4122, "unit": "dimensionless"},
        },
        "correlation_id": prefix,
        "family": "relative_permittivity",
        "form": "constant-plus-polynomial-in-temperature",
        "independent_variables": ["temperature"],
        "provenance": _provenance("schick-et-al-2023", "Schick et al. 2023, Table 2"),
        "qualification": "candidate_extrapolation",
        "reference_temperature": {"magnitude": 293.0, "unit": "kelvin"},
        "source_sha256": source_sha,
        "terms": [
            {
                "coefficient": {
                    "identity": f"{prefix}/term-0/coefficient",
                    "value": {"magnitude": -0.0036, "unit": "1 / kelvin"},
                },
                "power": 1,
            }
        ],
    }


def variant_mapping(variant: str) -> dict[str, object]:
    rule, born, *modifiers = variant.split("-")
    mapping = json.loads(BASELINE.read_text(encoding="utf-8"))
    known_sources = {row["source_id"] for row in mapping["sources"]}
    for source_id, citation in (
        (
            "schick-et-al-2023",
            "Schick et al. (2023), Fluid Phase Equilibria 567, 113714",
        ),
        ("bulow-2020", "Bülow et al. (2020), Fluid Phase Equilibria 535, 112967"),
        (
            "bulow-2021-corrigendum",
            "Bülow et al. (2021), corrigendum to Fluid Phase Equilibria 535, 112967",
        ),
        ("ascani-2021", "Ascani & Held (2021), Z. Anorg. Allg. Chem. 647, 1305"),
        (
            "figiel-2025",
            "Figiel et al. (2025), Industrial & Engineering Chemistry Research 64, 9406",
        ),
    ):
        if source_id not in known_sources:
            mapping["sources"].append(
                {
                    "citation": citation,
                    "source_id": source_id,
                    "use_basis": "Born/permittivity fixed-parameter structure comparison",
                }
            )
    permittivity = next(
        f for f in mapping["model_families"] if f["kind"] == "permittivity"
    )
    electrolyte = next(
        f for f in mapping["model_families"] if f["kind"] == "electrolyte"
    )
    permittivity["choice"] = FORMULATIONS[rule]
    if born == "AUTO":
        electrolyte.pop("c_shell", None)
        electrolyte.pop("c_dielectric", None)
    else:
        electrolyte["c_shell"] = 0.0 if born == "ORG" else 1.0
        electrolyte["c_dielectric"] = 0.0 if born == "ORG" else 1.0

    mapping["model_coefficients"] = [
        row
        for row in mapping["model_coefficients"]
        if row["family"] != "ion_fraction_suppression_coefficient"
    ]
    if rule == "E":
        mapping["model_coefficients"].append(
            {
                "candidate_domain_id": "mea-candidate-293-15-to-393-15-k",
                "family": "ion_fraction_suppression_coefficient",
                "identity": "model/relative_permittivity/ion_fraction_suppression_coefficient",
                "provenance": _provenance("figiel-2025", "Figiel et al. 2025, Eq. 11"),
                "qualification": "candidate_extrapolation",
                "source_sha256": f"sha256:{SOURCE_SHA256['figiel-2025']}",
                "value": {"magnitude": 7.01, "unit": "dimensionless"},
            }
        )

    for component in mapping["components"]:
        component["coefficients"] = [
            row
            for row in component["coefficients"]
            if row["family"]
            not in {"relative_permittivity", "ion_specific_suppression_coefficient"}
        ]
        component_id = component["component_id"]
        if component_id == "monoethanolamine":
            component["coefficients"].append(
                _coefficient(
                    component_id,
                    "relative_permittivity",
                    32.0,
                    "uyan-2015-permittivity-transfer",
                    "Uyan et al. 2015, Eq. 5 mixing form transferred from MDEA to MEA; retained MEA scalar",
                )
            )
        elif component_id in ION_IDS and rule in {"B", "C", "D"}:
            component["coefficients"].append(
                _coefficient(
                    component_id,
                    "relative_permittivity",
                    8.0,
                    "bulow-2020" if rule == "B" else "ascani-2021",
                    (
                        "Bülow et al. 2020 ion convention"
                        if rule == "B"
                        else "Ascani & Held 2021 ion convention"
                    ),
                )
            )

    mapping["correlations"] = [
        row
        for row in mapping["correlations"]
        if not (
            row["family"] == "relative_permittivity"
            and row["component_id"] == "carbon-dioxide"
        )
    ]
    if rule in {"B", "C", "D", "E", "I"}:
        mapping["correlations"].append(_co2_permittivity_correlation())
    if rule == "I":
        foundation = json.loads(FOUNDATION.read_text(encoding="utf-8"))
        source_components = {
            row["component_id"]: row for row in foundation["components"]
        }
        for component in mapping["components"]:
            component["coefficients"].extend(
                copy_row
                for copy_row in source_components[component["component_id"]][
                    "coefficients"
                ]
                if copy_row["family"] == "ion_specific_suppression_coefficient"
            )
    for modifier in modifiers:
        if modifier.startswith("f"):
            value = float(modifier[1:])
            mea = next(
                row
                for row in mapping["components"]
                if row["component_id"] == "monoethanolamine"
            )
            record = next(
                row
                for row in mea["coefficients"]
                if row["family"] == "solvation_factor"
            )
            record["value"]["magnitude"] = value
            record["provenance"] = _provenance(
                "figiel-2025", f"Figiel SSM+DS MEA transfer sensitivity f_solv={value}"
            )
            record["source_sha256"] = f"sha256:{SOURCE_SHA256['figiel-2025']}"
        elif modifier in BORN_MODIFIERS:
            component_id, factor = BORN_MODIFIERS[modifier]
            component = next(
                row for row in mapping["components"] if row["component_id"] == component_id
            )
            record = next(
                row
                for row in component["coefficients"]
                if row["family"] == "born_diameter"
            )
            record["value"]["magnitude"] = float(record["value"]["magnitude"]) * factor
            record["provenance"] = _provenance(
                "figiel-2025",
                f"local ±10% sensitivity about the retained ion-specific d_Born; factor={factor}",
            )
            record["source_sha256"] = f"sha256:{SOURCE_SHA256['figiel-2025']}"
        elif modifier == "dDH":
            for component in mapping["components"]:
                for record in component["coefficients"]:
                    if record["family"] == "born_diameter":
                        record["value"]["magnitude"] = 0.0
        elif modifier == "noCO2":
            mapping["correlations"] = [
                row
                for row in mapping["correlations"]
                if not (
                    row["family"] == "relative_permittivity"
                    and row["component_id"] == "carbon-dioxide"
                )
            ]
            carbon_dioxide = next(
                row
                for row in mapping["components"]
                if row["component_id"] == "carbon-dioxide"
            )
            carbon_dioxide["coefficients"] = [
                row
                for row in carbon_dioxide["coefficients"]
                if row["family"] != "solvation_factor"
            ]
    mapping["document_id"] = (
        f"mea-born-permittivity-{variant.lower().replace('.', 'p')}"
    )
    return epcsaft.Parameters.from_mapping(mapping).to_mapping()


def _request(raw: dict[str, object]) -> dict[str, object]:
    request = corrected_request(raw)
    for phase in request["phases"]:
        phase["model"]["kind"] = "eos"
        phase["model"]["reference_id"] = "installed-eos"
    for record in request["reaction_system"]["equilibrium_constants"]:
        record[4] = "source-standard-state-to-eos-neutral-reference"
    return request


def packet_catalog() -> list[dict[str, object]]:
    packet = json.loads(STATE_PACKET.read_text(encoding="utf-8"))
    output = []
    for observation in packet["observations"]:
        request = observation["request"]
        family = "pressure" if len(observation["targets"]) == 1 else "speciation"
        output.append(
            {
                "family": family,
                "observation_id": observation["identity"],
                "temperature_C": float(request["temperature"]["value"]) - 273.15,
                "loading": float(request["reaction_system"]["feed_amounts_mol"][0]),
                "source": str(observation["targets"][0].get("source_identity", "")),
                "request": request,
                "targets": [
                    target | {"unit_scale": 1.0} for target in observation["targets"]
                ],
            }
        )
    return output


def catalog() -> list[dict[str, object]]:
    pressure = []
    for row in complete_pressure_catalog(full=True):
        pressure.append(
            {
                "family": "pressure",
                "observation_id": row["observation_id"],
                "temperature_C": row["temperature_c"],
                "loading": row["loading"],
                "source": row["source"],
                "request": row["request"],
                "targets": [
                    target | {"source_identity": row["source"]}
                    for target in row["targets"]
                ],
            }
        )
    speciation = [row for row in packet_catalog() if row["family"] == "speciation"]
    return [*pressure, *speciation]


def sparse_catalog() -> list[dict[str, object]]:
    selected = []
    by_family_temperature: dict[tuple[str, float], list[dict[str, object]]] = (
        defaultdict(list)
    )
    for row in packet_catalog():
        by_family_temperature[(str(row["family"]), float(row["temperature_C"]))].append(
            row
        )
    for family in ("pressure", "speciation"):
        ranked = sorted(
            (
                (key, rows)
                for key, rows in by_family_temperature.items()
                if key[0] == family
            ),
            key=lambda item: (-len(item[1]), item[0][1]),
        )[:2]
        for _, rows in ranked:
            ordered = sorted(rows, key=lambda row: float(row["loading"]))
            for index in {0, len(ordered) // 2, len(ordered) - 1}:
                selected.append(ordered[index])
    return list({str(row["observation_id"]): row for row in selected}.values())


def _evidence(result: object) -> dict[str, object]:
    return {str(key): value for key, value in result.evidence}


def retain_component_permittivity_derivative_check() -> None:
    temperature_k = 313.15
    density_mol_m3 = 1_000.0
    step = 1.0e-6
    fractions = [0.70, 0.25, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    output = []
    for variant, basis in (("B-ORG", "mole"), ("C-ORG", "mass")):
        mapping = variant_mapping(variant)
        model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))

        def epsilon(values: list[float]) -> float:
            return float(
                model.state(
                    T=temperature_k * epcsaft.unit_registry.kelvin,
                    rho=density_mol_m3
                    * epcsaft.unit_registry.mole
                    / epcsaft.unit_registry.meter**3,
                    x=values,
                ).bulk_relative_permittivity
            )

        plus = fractions.copy()
        minus = fractions.copy()
        plus[0] += step
        plus[1] -= step
        minus[0] -= step
        minus[1] += step
        numerical = (epsilon(plus) - epsilon(minus)) / (2.0 * step)

        pure_values = []
        for index in (0, 1):
            pure = [0.0] * len(fractions)
            pure[index] = 1.0
            pure_values.append(epsilon(pure))
        if basis == "mole":
            expected = pure_values[0] - pure_values[1]
        else:
            masses = [
                float(component["fixed"]["molar_mass"]["value"]["magnitude"])
                for component in mapping["components"]
            ]
            total_mass = math.fsum(
                x * mass for x, mass in zip(fractions, masses, strict=True)
            )
            co2 = [0.0] * len(fractions)
            co2[2] = 1.0
            neutral_permittivities = [*pure_values, epsilon(co2)]
            numerator = math.fsum(
                x * mass * pure
                for x, mass, pure in zip(
                    fractions[:3], masses[:3], neutral_permittivities, strict=True
                )
            )
            delta_mass = masses[0] - masses[1]
            delta_numerator = masses[0] * pure_values[0] - masses[1] * pure_values[1]
            expected = (
                delta_numerator * total_mass - numerator * delta_mass
            ) / total_mass**2
        relative_error = abs(numerical - expected) / max(abs(expected), 1.0)
        output.append(
            {
                "variant": variant,
                "basis": basis,
                "direction": "x_water += h; x_MEA -= h",
                "step": step,
                "numerical_directional_derivative": numerical,
                "analytic_directional_derivative": expected,
                "relative_error": relative_error,
                "accepted": relative_error < 2.0e-8,
            }
        )
    assert all(row["accepted"] for row in output)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "component-permittivity-derivative-check.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )


def evaluate_variant(
    task: tuple[str, str, int, int],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    variant, phase, shard, shard_count = task
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(variant_mapping(variant)))
    reference = epcsaft.Mixture(
        epcsaft.Parameters.from_mapping(variant_mapping("E-ORG"))
    )
    source = sparse_catalog() if phase == "sparse" else catalog()
    observations = [
        row for index, row in enumerate(source) if index % shard_count == shard
    ]
    states: list[dict[str, object]] = []
    targets: list[dict[str, object]] = []
    for observation in observations:
        started = time.perf_counter()
        compiled = False
        raw_request = observation["request"]
        liquid_request = next(
            phase for phase in raw_request["phases"] if phase["fluid_role"] == "liquid"
        )
        try:
            problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
                _request(observation["request"])
            )
            problem = prepared_problem(
                problem, f"{observation['observation_id']}-{variant}"
            )
            compiled = True
            result = equilibrium.solve(model, problem)
            status = result.status
            code, diagnostic = failure_fields(result.failure)
        except Exception as exc:
            result = None
            status = "exception"
            code = type(exc).__name__
            diagnostic = str(exc)
        state_row: dict[str, object] = {
            "phase": phase,
            "variant": variant,
            "rule": variant.split("-")[0],
            "born_formulation": variant.split("-")[1],
            "observation_id": observation["observation_id"],
            "family": observation["family"],
            "temperature_C": observation["temperature_C"],
            "loading": observation["loading"],
            "source": observation["source"],
            "continuation_present": raw_request.get("continuation") is not None,
            "liquid_start_present": liquid_request.get("start") is not None,
            "pressure_start_count": len(
                raw_request.get("pressure", {}).get("starts", [])
            ),
            "compiled": compiled,
            "status": status,
            "failure_code": code,
            "failure_diagnostic": diagnostic,
            "elapsed_s": time.perf_counter() - started,
        }
        if result is not None:
            state_row.update(
                solver_status=result.solver_status,
                physical_status=result.physical_status,
                eos_domain_status=result.eos_domain_status,
            )
        if status == "evaluated" and result is not None:
            liquid = next(
                candidate for candidate in result.phases if candidate.role == "liquid"
            )
            state = model.state(
                T=(float(observation["temperature_C"]) + 273.15)
                * epcsaft.unit_registry.kelvin,
                rho=liquid.molar_density_mol_m3
                * epcsaft.unit_registry.mole
                / epcsaft.unit_registry.meter**3,
                x=liquid.mole_fractions,
            )
            reference_state = reference.state(
                T=(float(observation["temperature_C"]) + 273.15)
                * epcsaft.unit_registry.kelvin,
                rho=liquid.molar_density_mol_m3
                * epcsaft.unit_registry.mole
                / epcsaft.unit_registry.meter**3,
                x=liquid.mole_fractions,
            )
            evidence = _evidence(result)
            charges = (0, 0, 0, 1, -1, -1, -2, 1, -1)
            vapor = next(
                (candidate for candidate in result.phases if candidate.role == "vapor"),
                None,
            )
            state_row.update(
                liquid_density_mol_m3=liquid.molar_density_mol_m3,
                liquid_packing_fraction=liquid.packing_fraction,
                liquid_mole_fractions=json.dumps(liquid.mole_fractions),
                liquid_mechanical_class=liquid.mechanical_class,
                vapor_mechanical_class="" if vapor is None else vapor.mechanical_class,
                charge_closure=math.fsum(
                    x * z for x, z in zip(liquid.mole_fractions, charges, strict=True)
                ),
                material_balance_closure=evidence.get("balance_inf_norm", ""),
                reaction_affinity_closure=evidence.get(
                    "reaction_affinity_inf_norm", ""
                ),
                pressure_closure=evidence.get("pressure_relative_inf_norm", ""),
                bulk_relative_permittivity=state.bulk_relative_permittivity,
                figiel_reference_permittivity=reference_state.bulk_relative_permittivity,
                born_a_over_rt=state.born,
                debye_huckel_a_over_rt=state.debye_huckel,
                residual_a_over_rt=float(state.ares().to("joule / mole").magnitude)
                / (8.31446261815324 * (float(observation["temperature_C"]) + 273.15)),
                eos_evaluation_count=evidence.get("eos_evaluation_count", ""),
            )
            predictions = {row.identity: row.value for row in result.rows}
            for target in observation["targets"]:
                predicted = predictions.get(target["prediction_identity"])
                predicted = (
                    None
                    if predicted is None
                    else float(predicted) * float(target.get("unit_scale", 1.0))
                )
                observed = float(target["observed"])
                targets.append(
                    {
                        "phase": phase,
                        "variant": variant,
                        "rule": variant.split("-")[0],
                        "born_formulation": variant.split("-")[1],
                        "family": observation["family"],
                        "observation_id": observation["observation_id"],
                        "source": target.get("source_identity", ""),
                        "temperature_C": observation["temperature_C"],
                        "loading": observation["loading"],
                        "target": target["identity"].split("::")[-1],
                        "observed": observed,
                        "predicted": "" if predicted is None else float(predicted),
                        "log10_predicted_over_observed": (
                            ""
                            if predicted is None
                            or float(predicted) <= 0
                            or observed <= 0
                            else math.log10(predicted / observed)
                        ),
                    }
                )
        states.append(state_row)
    return states, targets


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = tuple(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(
    phase: str, states: list[dict[str, object]], targets: list[dict[str, object]]
) -> list[dict[str, object]]:
    output = []
    for variant in sorted({str(row["variant"]) for row in states}):
        members = [row for row in states if row["variant"] == variant]
        summary: dict[str, object] = {
            "phase": phase,
            "variant": variant,
            "rule": variant.split("-")[0],
            "born_formulation": variant.split("-")[1],
            "attempted_states": len(members),
            "compiled_states": sum(bool(row["compiled"]) for row in members),
            "evaluated_states": sum(row["status"] == "evaluated" for row in members),
            "failed_states": sum(row["status"] != "evaluated" for row in members),
            "failure_classes": json.dumps(
                Counter(
                    str(row["failure_code"])
                    for row in members
                    if row["status"] != "evaluated"
                ),
                sort_keys=True,
            ),
            "elapsed_s": math.fsum(float(row["elapsed_s"]) for row in members),
        }
        evaluated_states = [row for row in members if row["status"] == "evaluated"]
        for field in (
            "bulk_relative_permittivity",
            "liquid_density_mol_m3",
            "charge_closure",
            "material_balance_closure",
            "reaction_affinity_closure",
            "pressure_closure",
        ):
            values = [
                abs(float(row[field]))
                for row in evaluated_states
                if row.get(field) != ""
            ]
            summary[f"{field}_min"] = min(values) if values else ""
            summary[f"{field}_median"] = statistics.median(values) if values else ""
            summary[f"{field}_max"] = max(values) if values else ""
        for family in ("pressure", "speciation"):
            rows = [
                row
                for row in targets
                if row["variant"] == variant
                and row["family"] == family
                and row["log10_predicted_over_observed"] != ""
            ]
            errors = [float(row["log10_predicted_over_observed"]) for row in rows]
            summary[f"{family}_positive_targets"] = len(errors)
            summary[f"{family}_log10_rmse"] = (
                math.sqrt(statistics.fmean(error * error for error in errors))
                if errors
                else ""
            )
            summary[f"{family}_median_factor"] = (
                10 ** statistics.median(abs(error) for error in errors)
                if errors
                else ""
            )
            summary[f"{family}_mean_log10_bias"] = (
                statistics.fmean(errors) if errors else ""
            )
        output.append(summary)
    return output


def run(
    phase: str, variants: list[str], workers: int, output_prefix: str | None = None
) -> None:
    if any(variant.startswith(("B-", "C-")) for variant in variants):
        retain_component_permittivity_derivative_check()
    shard_count = min(workers, 8)
    tasks = [
        (variant, phase, shard, shard_count)
        for variant in variants
        for shard in range(shard_count)
    ]
    all_states: list[dict[str, object]] = []
    all_targets: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=min(workers, len(tasks))) as pool:
        futures = {
            pool.submit(evaluate_variant, task): f"{task[0]} [{task[2] + 1}/{task[3]}]"
            for task in tasks
        }
        for future in as_completed(futures):
            states, targets = future.result()
            all_states.extend(states)
            all_targets.extend(targets)
            print(f"{phase}: {futures[future]} complete", flush=True)
    all_states.sort(key=lambda row: (str(row["variant"]), str(row["observation_id"])))
    all_targets.sort(
        key=lambda row: (
            str(row["variant"]),
            str(row["observation_id"]),
            str(row["target"]),
        )
    )
    summaries = summarize(phase, all_states, all_targets)
    prefix = output_prefix or phase
    _write_csv(RESULTS / f"{prefix}-states.csv", all_states)
    _write_csv(RESULTS / f"{prefix}-targets.csv", all_targets)
    _write_csv(RESULTS / f"{prefix}-summary.csv", summaries)
    receipt = {
        "phase": phase,
        "variants": variants,
        "workers": min(workers, len(tasks)),
        "parameter_sha256": sha256(BASELINE),
        "state_packet_sha256": sha256(STATE_PACKET),
        "pressure_catalog_sha256": sha256(CANONICAL_VLE),
        "engine_commit": ENGINE_COMMIT,
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "source_sha256": SOURCE_SHA256,
        "neutral_pool": sorted(NEUTRAL_IDS),
        "ion_relative_permittivity": 8.0,
        "regression": False,
        "states_per_variant": len(sparse_catalog() if phase == "sparse" else catalog()),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{prefix}-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("sparse", "full"), required=True)
    parser.add_argument("--variants", nargs="+", default=[])
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output-prefix")
    args = parser.parse_args()
    variants = args.variants or [
        f"{rule}-{born}" for rule in "ABCDE" for born in ("ORG", "SSMDS")
    ]
    run(args.phase, variants, args.workers, args.output_prefix)


if __name__ == "__main__":
    main()
