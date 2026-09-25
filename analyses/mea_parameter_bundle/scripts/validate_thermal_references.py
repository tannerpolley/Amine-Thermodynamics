"""Validate the thermal reference behind the heat calculation for non-isothermal use.

Checks, each on the adopted model with ``verify_reference_calorics.record``:
- reference-chain consistency at the calorimetry temperatures (313.15, 353.15, 393.15 K) and
  loadings 0.1/0.3/0.5: the absorption heat h_CO2^ig - d(nH)/dn_CO2 from the Engine enthalpy
  must equal RT^2 d ln a_CO2/dT|_P + RT (Gibbs-Helmholtz), and the enthalpy feed action must
  match centered feed re-solves. This is the state-level form of the reaction-enthalpy
  constraint sum_i nu_i h_i = RT^2 d ln K/dT that the Engine imposes on the ions;
- pure liquid water cp (ideal-gas record + EOS residual) against IAPWS-95;
- water vaporization enthalpy (EOS residual only) against IAPWS-95 saturation values.
Loaded-solution cp against Hilliard 2008 and Weiland 1997 is owned by
``verify_solution_heat_capacity`` (it needs the Engine's electrolyte Cp, ePC-SAFT #140).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import verify_reference_calorics as vrc
import verify_solution_heat_capacity as vsc
import verify_temperature_reference as vt
from evaluate_direct_absorption_heat import RESULTS, heat_request, thermal_model
from refresh_results import bounded_main
from result_freshness import source_hashes, stamp_results
from run_direct_parameter_campaign import load_packet, pressure_templates
from shared_evaluation import ENGINE_WHEEL_SHA256, STATE_PACKET, corrected_request, reaction_values, parameter_mapping, verify_wheel

TEMPERATURES_C = (40, 80, 120)
LOADINGS = (0.1, 0.3, 0.5)
# IAPWS-95 saturated water (Wagner and Pruss 2002, NIST WebBook): T/C, p_sat/Pa, dh_vap/(kJ/mol).
STEAM_TABLE = ((40, 7384.0, 43.35), (80, 47390.0, 41.59), (100, 101325.0, 40.66), (120, 198500.0, 39.68))
OUTPUT = RESULTS / "thermal-reference-validation.csv"
SUMMARY = RESULTS / "thermal-reference-validation.json"


def consistency_rows(model) -> list[dict[str, object]]:
    templates, reactions = pressure_templates(load_packet()), reaction_values(parameter_mapping())
    rows = []
    for temperature_c in TEMPERATURES_C:
        warm = None
        for loading in LOADINGS:
            request = corrected_request(heat_request(templates, temperature_c, loading), reactions)
            problem, result = vt.solve(model, request, warm)
            warm = vt.anchor(problem, result)
            heat = vrc.liquid_heat(model, request, temperature_c + 273.15, result.pressure[0], warm)
            rows.append({"check": "reference_chain_consistency", "temperature_C": temperature_c, "loading": loading,
                         **{k: heat[k] for k in ("P_Pa", "heat_kJ_per_mol", "gibbs_helmholtz_kJ_per_mol",
                                                  "identity_rel", "resolve_rel")}})
    return rows


def water_rows(model) -> list[dict[str, object]]:
    water = [0.0] * len(vt.shared.COMPONENT_IDS)
    water[vrc.WATER] = 1.0
    rows = []
    for temperature, reference in vsc.WATER_CP.items():
        state = model.state(temperature, P=vsc.PRESSURE_PA, x=water, phase="liquid")
        cp = (state.residual_isobaric_heat_capacity + vsc.water_ideal_cp(temperature)) / vsc.MOLAR_MASS[vrc.WATER]
        rows.append({"check": "pure_water_cp", "temperature_C": round(temperature - 273.15, 2),
                     "model_kJ_per_kg_K": cp, "reference_kJ_per_kg_K": reference, "error_rel": cp / reference - 1.0})
    for temperature_c, pressure, reference in STEAM_TABLE:
        liquid, vapor = (model.state(temperature_c + 273.15, P=pressure, x=water, phase=p) for p in ("liquid", "vapor"))
        value = (vapor.residual_enthalpy - liquid.residual_enthalpy) / 1000.0
        rows.append({"check": "water_vaporization_enthalpy", "temperature_C": temperature_c,
                     "model_kJ_per_mol": value, "reference_kJ_per_mol": reference, "error_rel": value / reference - 1.0})
    return rows


def main() -> None:
    verify_wheel()
    inputs = source_hashes(STATE_PACKET, Path(__file__), Path(__file__).with_name("verify_reference_calorics.py"),
                           Path(__file__).with_name("evaluate_direct_absorption_heat.py"))
    model, _ = thermal_model()
    rows = consistency_rows(model) + water_rows(model)
    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    chain = [r for r in rows if r["check"] == "reference_chain_consistency"]
    summary = {
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "criteria": {"gibbs_helmholtz_rel": vrc.IDENTITY_RTOL, "feed_resolve_rel": vrc.RESOLVE_RTOL},
        "reference_chain_passed": sum(r["identity_rel"] <= vrc.IDENTITY_RTOL and r["resolve_rel"] <= vrc.RESOLVE_RTOL
                                      for r in chain),
        "reference_chain_total": len(chain),
        "max_identity_rel": max(r["identity_rel"] for r in chain),
        "max_resolve_rel": max(r["resolve_rel"] for r in chain),
        **{f"{check}_max_abs_error_rel": max(abs(r["error_rel"]) for r in rows if r["check"] == check)
           for check in ("pure_water_cp", "water_vaporization_enthalpy")},
        "claim_limit": "Numerical consistency of the Engine reference chain at the calorimetry states and two pure-water "
                       "EOS checks. The ideal-gas neutral records are unadopted; liquid water cp inherits the EOS "
                       "residual-cp deficit. Pure MEA liquid cp has no retained verified reference and is not assessed.",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    stamp_results(SUMMARY, [OUTPUT], inputs=inputs)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    bounded_main(main)
