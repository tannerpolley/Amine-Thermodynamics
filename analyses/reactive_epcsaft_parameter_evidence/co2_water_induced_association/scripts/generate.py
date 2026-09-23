from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

import epcsaft
from epcsaft import equilibrium


ANALYSIS = Path(__file__).resolve().parents[1]
SOURCE = ANALYSIS / "source/kiepe_2002_table_1.csv"
RESULTS = ANALYSIS / "results"
COMPONENTS = ("carbon-dioxide", "water")
T_REFERENCE_K = 298.15
# Each isotherm's warm-start chain begins from the most concentrated dilute
# bubble point that converges cold; a 1e-6 seed alone does not carry the
# 313.2 K chain to the first source row.
SEED_CO2_MOLE_FRACTIONS = (1.0e-4, 3.0e-5, 1.0e-5, 1.0e-6)


def value(magnitude: float, unit: str) -> dict[str, object]:
    return {"magnitude": magnitude, "unit": unit}


def provenance(source_id: str, locator: str) -> dict[str, str]:
    return {
        "source_id": source_id,
        "locator": locator,
        "domain_id": "aqueous-co2-313-394-k",
    }


def coefficient(component: str, family: str, magnitude: float, unit: str) -> dict[str, object]:
    return {
        "identity": f"component/{component}/{family}",
        "family": family,
        "value": value(magnitude, unit),
        "provenance": provenance("pabsch-2020", "Table 2"),
    }


def component(
    identity: str,
    molar_mass: float,
    segment_count: float,
    diameter: float | None,
    dispersion_energy: float,
) -> dict[str, object]:
    coefficients = [
        coefficient(identity, "segment_count", segment_count, "dimensionless"),
        coefficient(identity, "dispersion_energy_over_k", dispersion_energy, "kelvin"),
    ]
    if diameter is not None:
        coefficients.append(coefficient(identity, "segment_diameter", diameter, "angstrom"))
    return {
        "component_id": identity,
        "fixed": {
            "molar_mass": {
                "value": value(molar_mass, "kilogram / mole"),
                "provenance": provenance("pabsch-2020", "Table 2"),
            },
            "charge_number": {
                "value": value(0, "elementary-charge"),
                "provenance": provenance("pabsch-2020", "Table 2"),
            },
        },
        "coefficients": coefficients,
    }


def edge(component_a: str, site_a: str, component_b: str, site_b: str) -> dict[str, object]:
    endpoints = sorted(((component_a, site_a), (component_b, site_b)))
    left, right = endpoints
    prefix = f"association/{left[0]}/{left[1]}/{right[0]}/{right[1]}"
    return {
        "endpoint_a": {"component_id": left[0], "site_id": left[1]},
        "endpoint_b": {"component_id": right[0], "site_id": right[1]},
        "energy_over_k": {
            "identity": f"{prefix}/energy_over_k",
            "value": value(2425.6 if component_a == component_b else 1212.8, "kelvin"),
        },
        "volume": {
            "identity": f"{prefix}/volume",
            "value": value(0.0450, "dimensionless"),
        },
        "source": {
            "kind": "explicit",
            "provenance": [provenance("pabsch-2020", "Table 2 and Eqs. 15-18")],
        },
    }


def parameters(k_ij: float) -> epcsaft.Parameters:
    family_provenance = provenance("pabsch-2020", "Tables 2 and 6")
    mapping = {
        "schema": "epcsaft.parameters",
        "schema_version": 1,
        "document_id": "co2-water-pabsch-induced-reference",
        "document_version": 1,
        "purpose": "external-document",
        "sources": [
            {
                "source_id": "pabsch-2020",
                "citation": "Pabsch, Held, and Sadowski, JCED 2020, 65, 5768-5777",
                "doi": "10.1021/acs.jced.0c00704",
                "use_basis": "Tables 2 and 6; Eqs. 15-18",
            }
        ],
        "domains": [
            {
                "domain_id": "aqueous-co2-313-394-k",
                "kind": "reported-conditions",
                "temperature_min": value(313.0, "kelvin"),
                "temperature_max": value(394.0, "kelvin"),
                "pressure_min": value(1.0e3, "pascal"),
                "pressure_max": value(1.0e7, "pascal"),
            }
        ],
        "components": [
            component("carbon-dioxide", 0.0440095, 2.0729, 2.7852, 169.21),
            component("water", 0.01801528, 1.2046, None, 353.94),
        ],
        "pairs": [
            {
                "component_id_a": "carbon-dioxide",
                "component_id_b": "water",
                "coefficients": [
                    {
                        "identity": "pair/carbon-dioxide/water/k_ij",
                        "family": "k_ij",
                        "value": value(k_ij, "dimensionless"),
                        "provenance": provenance("pabsch-2020", "Table 6"),
                    }
                ],
            }
        ],
        "model_families": [
            {
                "family_id": family_id,
                "kind": kind,
                "choice": choice,
                "provenance": family_provenance,
            }
            for family_id, kind, choice in (
                ("model/base", "base", "pc-saft"),
                ("model/association", "association", "general-site"),
                ("model/electrolyte", "electrolyte", "none"),
                ("model/relative_permittivity", "permittivity", "none"),
            )
        ],
        "model_coefficients": [],
        "correlations": [
            {
                "correlation_id": "component/water/segment_diameter/constant-plus-sum-of-exponentials",
                "component_id": "water",
                "family": "segment_diameter",
                "form": "constant-plus-sum-of-exponentials",
                "independent_variables": ["temperature"],
                "constant": {
                    "identity": "component/water/segment_diameter/constant-plus-sum-of-exponentials/constant",
                    "value": value(2.7927, "angstrom"),
                },
                "terms": [
                    {
                        "amplitude": {
                            "identity": "component/water/segment_diameter/constant-plus-sum-of-exponentials/term-0/amplitude",
                            "value": value(10.11, "angstrom"),
                        },
                        "exponent_coefficient": {
                            "identity": "component/water/segment_diameter/constant-plus-sum-of-exponentials/term-0/exponent_coefficient",
                            "value": value(-0.01775, "1 / kelvin"),
                        },
                    },
                    {
                        "amplitude": {
                            "identity": "component/water/segment_diameter/constant-plus-sum-of-exponentials/term-1/amplitude",
                            "value": value(-1.417, "angstrom"),
                        },
                        "exponent_coefficient": {
                            "identity": "component/water/segment_diameter/constant-plus-sum-of-exponentials/term-1/exponent_coefficient",
                            "value": value(-0.01146, "1 / kelvin"),
                        },
                    },
                ],
                "provenance": provenance("pabsch-2020", "Table 2 footnote b"),
            }
        ],
        "topology": {
            "presets": [],
            "sites": [
                {
                    "component_id": component_id,
                    "site_id": site_id,
                    "site_role": "donor" if site_id == "a" else "acceptor",
                    "multiplicity": 1,
                    "provenance": provenance("pabsch-2020", "Table 2"),
                }
                for component_id in COMPONENTS
                for site_id in ("a", "b")
            ],
            "edges": [
                edge("water", "a", "water", "b"),
                edge("carbon-dioxide", "a", "water", "b"),
                edge("carbon-dioxide", "b", "water", "a"),
            ],
        },
    }
    return epcsaft.Parameters.from_mapping(mapping, components=COMPONENTS)


def source_rows() -> list[dict[str, str]]:
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        return [row for row in csv.DictReader(stream) if row["included"] == "true"]


def problem(temperature: float, x_co2: float) -> equilibrium.Problem:
    return equilibrium.bubble_point(
        liquid=equilibrium.Phase("liquid", kind="liquid"),
        T=temperature,
        feed=equilibrium.MoleFractions({"carbon-dioxide": x_co2, "water": 1.0 - x_co2}),
    )


def residual_inf(result: equilibrium.EquilibriumResult, kind: str) -> float:
    return max(
        abs(value)
        for row, value in zip(result.rows, result.residuals, strict=True)
        if row.kind.name == kind
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kij-offset", type=float, default=0.0)
    parser.add_argument("--results-directory", type=Path, default=RESULTS)
    args = parser.parse_args()
    results = args.results_directory
    started = time.perf_counter()
    predictions: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    previous_temperature = None
    for row in source_rows():
        temperature = float(row["temperature_k"])
        kij = 0.0122 + args.kij_offset + 3.016e-4 * (temperature - T_REFERENCE_K)
        mixture = epcsaft.Mixture(parameters(kij))
        if temperature != previous_temperature:
            previous_temperature = temperature
            start = None
            for seed in SEED_CO2_MOLE_FRACTIONS:
                trial = equilibrium.solve_equilibrium(mixture, problem(temperature, seed))
                if trial.success:
                    start = trial
                    break
        result = equilibrium.solve_equilibrium(
            mixture,
            problem(temperature, float(row["liquid_co2_mole_fraction"])),
            start,
        )
        if not result.success:
            failures.append({"row_id": row["row_id"], "reason": result.message})
            continue
        start = result
        observed_kpa = float(row["observed_pressure_kpa"])
        model_kpa = result.pressure[0] / 1000.0
        residual = math.log(model_kpa / observed_kpa)
        predictions.append(
            {
                "row_id": row["row_id"],
                "temperature_k": temperature,
                "liquid_co2_mole_fraction": float(row["liquid_co2_mole_fraction"]),
                "observed_pressure_kpa": observed_kpa,
                "model_pressure_kpa": model_kpa,
                "log_pressure_residual": residual,
                "multiplicative_error": math.exp(abs(residual)),
                "k_ij": kij,
                "liquid_density_mol_m3": result.molar_densities[0],
                "vapor_density_mol_m3": result.molar_densities[1],
                "vapor_co2_mole_fraction": result.mole_fractions[len(COMPONENTS)],
                "pressure_residual_inf": residual_inf(result, "Pressure"),
                "chemical_potential_residual_inf": residual_inf(result, "Chemical"),
            }
        )

    residuals = [float(row["log_pressure_residual"]) for row in predictions]
    module_path = Path(epcsaft.__file__).resolve()
    summary = {
        "schema": "mea.co2-water-induced-association.v1",
        "source": "Kiepe et al. (2002), Table 1, DOI 10.1021/ie020154i",
        "parameter_source": "Pabsch et al. (2020), Tables 2 and 6, DOI 10.1021/acs.jced.0c00704",
        "k_ij_offset": args.kij_offset,
        "row_count": len(source_rows()),
        "evaluated_row_count": len(predictions),
        "failed_row_count": len(failures),
        "log_pressure_rmse": (
            math.sqrt(sum(value_ * value_ for value_ in residuals) / len(residuals))
            if residuals
            else None
        ),
        "median_multiplicative_error": (
            statistics.median(
                float(row["multiplicative_error"]) for row in predictions
            )
            if predictions
            else None
        ),
        "maximum_pressure_residual_inf": (
            max(float(row["pressure_residual_inf"]) for row in predictions)
            if predictions
            else None
        ),
        "maximum_chemical_potential_residual_inf": (
            max(
                float(row["chemical_potential_residual_inf"]) for row in predictions
            )
            if predictions
            else None
        ),
        "runtime_seconds": time.perf_counter() - started,
        "engine_module": str(module_path),
        "engine_module_sha256": hashlib.sha256(module_path.read_bytes()).hexdigest(),
    }
    results.mkdir(parents=True, exist_ok=True)
    if predictions:
        write_csv(results / "predictions.csv", predictions)
    if failures:
        write_csv(results / "failures.csv", failures)
    write_csv(
        results / "parameter_table.csv",
        [
            {"parameter": "water_m", "value": 1.2046, "unit": "dimensionless"},
            {"parameter": "water_epsilon_over_k", "value": 353.94, "unit": "K"},
            {"parameter": "water_assoc_energy_over_k", "value": 2425.6, "unit": "K"},
            {"parameter": "water_assoc_volume", "value": 0.0450, "unit": "dimensionless"},
            {"parameter": "co2_m", "value": 2.0729, "unit": "dimensionless"},
            {"parameter": "co2_sigma", "value": 2.7852, "unit": "angstrom"},
            {"parameter": "co2_epsilon_over_k", "value": 169.21, "unit": "K"},
            {"parameter": "cross_assoc_energy_over_k", "value": 1212.8, "unit": "K"},
            {"parameter": "cross_assoc_volume", "value": 0.0450, "unit": "dimensionless"},
            {"parameter": "k_ij_intercept_at_298_15_K", "value": 0.0122 + args.kij_offset, "unit": "dimensionless"},
            {"parameter": "k_ij_temperature_slope", "value": 3.016e-4, "unit": "1/K"},
        ],
    )
    (results / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
