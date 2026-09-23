"""Validate the anchored species thermal references for non-isothermal use.

Checks, in order: reaction-reference consistency across the whole domain for
the anchored construction; pure
liquid heat capacities against the anchor correlations and the ideal-gas
diagnostic; water vaporization enthalpy against steam-table values; and
fixed-composition versus equilibrium heat capacity of 30 mass % MEA solutions
at the calorimetry temperatures.  Equilibrium heat capacities need exact
Engine solves and run only with ``--equilibrium``.
"""

from __future__ import annotations

import os

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import argparse  # noqa: E402
import copy  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
from pathlib import Path  # noqa: E402

import epcsaft  # noqa: E402
import numpy as np  # noqa: E402
from epcsaft import equilibrium  # noqa: E402

from evaluate_direct_absorption_heat import (  # noqa: E402
    ANCHOR_PRESSURE_PA,
    ANCHOR_SOURCES,
    REFERENCE_DOMAIN_K,
    _shomate,
    build_thermochemistry,
    transformed_reaction_enthalpies,
)
from shared_evaluation import (  # noqa: E402
    PARAMETERS,
    SOURCE_CONTRACT,
    STATE_PACKET,
    corrected_request,
    load_parameters,
)
from run_reaction_temperature_fit import (  # noqa: E402
    Anchor,
    anchor_from,
    baseline_reactions,
    evaluate_state,
    heat_request,
    pressure_templates,
    provenance,
    write_csv,
    write_json,
)
from result_freshness import source_hashes, stamp_results  # noqa: E402
from refresh_results import bounded_main  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/calorimetry"
U = epcsaft.unit_registry
# NIST/IAPWS saturated-water values, kJ/mol, used only as an external check.
STEAM_TABLE = (
    (40, 7384.0, 43.35),
    (80, 47390.0, 41.59),
    (100, 101325.0, 40.66),
    (120, 198500.0, 39.68),
)
WATER_IDEAL_GAS_SHOMATE = (
    30.09200,
    6.832514,
    6.793435,
    -2.534480,
    0.082139,
)  # Chase 1998, 500-1700 K, extrapolated
SOLUTION_TEMPERATURES_C = (25, 40, 80, 120)
SOLUTION_LOADINGS = (0.0, 0.2, 0.4)
MEA_MASS_FRACTION = 0.30


def consistency_rows(
    model, templates, reactions, references
) -> list[dict[str, object]]:
    rows = []
    for temperature_k in np.arange(
        REFERENCE_DOMAIN_K[0], REFERENCE_DOMAIN_K[1] + 1e-9, 2.0
    ):
        request = copy.deepcopy(templates[80][0][1])
        request["temperature"]["value"] = float(temperature_k)
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            corrected_request(request, reactions)
        )
        matrix = np.asarray(problem.reaction_system.reaction_matrix, dtype=float)
        q = transformed_reaction_enthalpies(model, problem)
        for name, thermo in references.items():
            h = np.asarray(
                thermo.enthalpies_j_per_mol(float(temperature_k), model.component_ids)
            )
            rows.append(
                {
                    "check": "reaction_reference_consistency",
                    "reference": name,
                    "temperature_K": float(temperature_k),
                    "max_abs_residual_j_per_mol": float(np.max(np.abs(matrix @ h - q))),
                    "engine_tolerance_j_per_mol": 2.0e-3,
                }
            )
    return rows


def pure_liquid_rows(model, thermo) -> list[dict[str, object]]:
    rows = []
    for component_id in ("water", "monoethanolamine"):
        spec = ANCHOR_SOURCES[component_id]
        x = [1.0 if c == component_id else 0.0 for c in model.component_ids]
        for temperature_c in (25, 40, 60, 80, 100, 120):
            temperature_k = temperature_c + 273.15
            state = model.state(
                T=temperature_k * U.kelvin,
                P=ANCHOR_PRESSURE_PA * U.pascal,
                x=x,
                phase="liquid",
            )
            t = temperature_c
            correlation = (
                1000.0
                * spec["molar_mass_kg_per_mol"]
                * math.fsum(a * t**k for k, a in enumerate(spec["liquid_cp_kj_kg_k"]))
            )
            model_cp = float(state.cp(thermo).to("joule/mole/kelvin").magnitude)
            residual = float(state.cpres().magnitude)
            row = {
                "check": "pure_liquid_cp",
                "component": component_id,
                "temperature_C": temperature_c,
                "correlation_cp_j_per_mol_k": correlation,
                "model_cp_j_per_mol_k": model_cp,
                "eos_residual_cp_j_per_mol_k": residual,
                "reference_cp_j_per_mol_k": model_cp - residual,
            }
            if component_id == "water":
                ideal = _shomate(temperature_k, WATER_IDEAL_GAS_SHOMATE)
                row["nist_ideal_gas_cp_j_per_mol_k"] = ideal
                row["ideal_gas_anchored_model_cp_j_per_mol_k"] = ideal + residual
                row["ideal_gas_anchored_error_percent"] = (
                    100.0 * (ideal + residual - correlation) / correlation
                )
            rows.append(row)
    return rows


def vaporization_rows(model) -> list[dict[str, object]]:
    rows = []
    x = [1.0 if c == "water" else 0.0 for c in model.component_ids]
    for temperature_c, pressure_pa, table in STEAM_TABLE:
        temperature_k = temperature_c + 273.15
        liquid = model.state(
            T=temperature_k * U.kelvin, P=pressure_pa * U.pascal, x=x, phase="liquid"
        )
        vapor = model.state(
            T=temperature_k * U.kelvin, P=pressure_pa * U.pascal, x=x, phase="vapor"
        )
        model_hvap = (
            float(vapor._residual_enthalpy.magnitude)
            - float(liquid._residual_enthalpy.magnitude)
        ) / 1000.0
        rows.append(
            {
                "check": "water_vaporization_enthalpy",
                "temperature_C": temperature_c,
                "saturation_pressure_pa": pressure_pa,
                "model_kj_per_mol": model_hvap,
                "steam_table_kj_per_mol": table,
                "error_percent": 100.0 * (model_hvap - table) / table,
                "note": "reference cancels between phases; this tests the EOS residual only",
            }
        )
    return rows


def solution_rows(
    model, templates, reactions, references, equilibrium_solves: bool, budget_s: float
) -> list[dict[str, object]]:
    """Fixed-composition cp of equilibrium liquid states, and equilibrium cp when requested."""
    rows = []
    masses = np.asarray(
        templates[80][0][1]["reaction_system"]["molar_masses_kg_per_mol"], dtype=float
    )
    anchors: list[Anchor] = []
    for temperature_c in SOLUTION_TEMPERATURES_C:
        if temperature_c not in templates:
            continue
        for loading in SOLUTION_LOADINGS:
            request = heat_request(temperature_c, max(loading, 0.003))
            record = evaluate_state(
                model,
                request,
                reactions,
                f"thermal-{temperature_c}C-{loading:.3f}",
                anchors,
                references["anchored"],
                budget_s,
            )
            if record["status"] != "evaluated":
                rows.append(
                    {
                        "check": "solution_cp",
                        "temperature_C": temperature_c,
                        "loading": loading,
                        "status": record["status"],
                        "failure_diagnostic": record["failure_diagnostic"],
                    }
                )
                continue
            anchors.append(anchor_from(record))
            x = np.asarray(record["anchor"]["mole_fractions"])
            mass_per_mol = float(x @ masses)
            state = model.state(
                T=(temperature_c + 273.15) * U.kelvin,
                rho=record["molar_density_mol_m3"] * U.mole / U.meter**3,
                x=list(x),
            )
            row: dict[str, object] = {
                "check": "solution_cp",
                "temperature_C": temperature_c,
                "loading": loading,
                "mea_mass_fraction_nominal": MEA_MASS_FRACTION,
                "status": "evaluated",
                "mixture_molar_mass_kg_per_mol": mass_per_mol,
            }
            for name, thermo in references.items():
                cp = state.cp(thermo)
                value = (
                    None if cp is None else float(cp.to("joule/mole/kelvin").magnitude)
                )
                row[f"fixed_composition_cp_{name}_kj_per_kg_k"] = (
                    None if value is None else value / mass_per_mol / 1000.0
                )
            if equilibrium_solves:
                totals = {}
                for delta in (-1.0, 1.0):
                    shifted = copy.deepcopy(request)
                    shifted["temperature"]["value"] = temperature_c + 273.15 + delta
                    rec = evaluate_state(
                        model,
                        shifted,
                        reactions,
                        f"thermal-{temperature_c}C-{loading:.3f}-dT{delta:+.0f}",
                        anchors,
                        references["anchored"],
                        budget_s,
                    )
                    totals[delta] = (
                        None
                        if rec["status"] != "evaluated"
                        else (float(rec["total_enthalpy_j"]), float(rec["amount_mol"]))
                    )
                if all(v is not None for v in totals.values()):
                    h_plus, n_plus = totals[1.0]
                    h_minus, n_minus = totals[-1.0]
                    amount = float(record["amount_mol"])
                    row["equilibrium_cp_anchored_kj_per_kg_k"] = (
                        ((h_plus / n_plus - h_minus / n_minus) / 2.0)
                        / mass_per_mol
                        / 1000.0
                    )
                    row["equilibrium_solve_amount_mol"] = amount
                else:
                    row["equilibrium_cp_anchored_kj_per_kg_k"] = None
                    row["equilibrium_cp_note"] = (
                        "a shifted-temperature equilibrium solve failed"
                    )
            rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--equilibrium",
        action="store_true",
        help="also solve T +/- 1 K equilibrium states for equilibrium cp",
    )
    parser.add_argument("--budget-s", type=float, default=600.0)
    args = parser.parse_args()
    freshness_inputs = source_hashes(
        RESULTS / "current-selected-reference-thermochemistry.json",
        STATE_PACKET,
        Path(__file__),
        Path(__file__).with_name("shared_evaluation.py"),
        SOURCE_CONTRACT,
        Path(__file__).with_name("evaluate_direct_absorption_heat.py"),
        Path(__file__).with_name("run_reaction_temperature_fit.py"),
    )
    model = epcsaft.Mixture(load_parameters())
    templates = pressure_templates()
    reactions = baseline_reactions()
    anchored, payload = build_thermochemistry(model, templates, reactions)
    retained_reference = json.loads(
        (RESULTS / "current-selected-reference-thermochemistry.json").read_text()
    )
    if retained_reference != json.loads(json.dumps(payload)):
        raise ValueError(
            "Thermal reference differs from calorimetry; regenerate calorimetry first"
        )
    references = {"anchored": anchored}
    rows = []
    rows += consistency_rows(model, templates, reactions, references)
    rows += pure_liquid_rows(model, anchored)
    rows += vaporization_rows(model)
    rows += solution_rows(
        model, templates, reactions, references, args.equilibrium, args.budget_s
    )
    write_csv(RESULTS / "thermal-reference-validation.csv", rows)
    consistency = [r for r in rows if r["check"] == "reaction_reference_consistency"]
    summary = {
        **provenance(anchored),
        "reference_payload": payload,
        "max_consistency_residual_j_per_mol": {
            name: max(
                r["max_abs_residual_j_per_mol"]
                for r in consistency
                if r["reference"] == name
            )
            for name in references
        },
        "water_vaporization_max_error_percent": max(
            abs(r["error_percent"])
            for r in rows
            if r["check"] == "water_vaporization_enthalpy"
        ),
        "water_ideal_gas_anchored_cp_error_percent": {
            str(r["temperature_C"]): r["ideal_gas_anchored_error_percent"]
            for r in rows
            if r.get("component") == "water"
        },
        "solution_cp_rows": [r for r in rows if r["check"] == "solution_cp"],
        "missing_evidence": [
            "30 mass % MEA loaded-solution heat capacity, 25-120 C, loading 0-0.5 (Weiland et al. 1997 J. Chem. Eng. Data 42:1004; Hilliard 2008 thesis) is not retained; the solution cp rows above are model predictions without a retained comparison",
            "MEA ideal-gas heat capacity (DIPPR/TRC) is not retained; MEA reference cp is inferred from the liquid correlation net of the EOS residual",
            "Hilliard 2008 liquid cp correlation temperature ranges are taken from MEA-Absorption-Column and not re-verified against the thesis",
        ],
    }
    write_json(RESULTS / "thermal-reference-validation.json", summary)
    stamp_results(
        RESULTS / "thermal-reference-validation.json",
        [
            RESULTS / "thermal-reference-validation.csv",
        ],
        inputs=freshness_inputs,
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in summary.items()
                if k not in ("reference_payload", "solution_cp_rows")
            },
            indent=2,
        )
    )
    for r in summary["solution_cp_rows"]:
        print(r)


if __name__ == "__main__":
    bounded_main(main)
