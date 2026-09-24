"""Loaded-solution heat capacity from the Engine's reference calorics (Engine #140).

The Hilliard/Weiland composition (30 wt% MEA, loading 0.35: the vle_obs_0130 liquid feed) on
liquid-only TP states at 101325 Pa, with the neutral records of verify_reference_calorics:
- equilibrium cp = d(nH)/dT|_P,feed per kg solution (reactions shift with T, as in a calorimeter),
  against centered re-solves of nH and against Hilliard 2008 App. G.2 / Weiland 1997 Table 3;
- frozen-composition TotalIsobaricHeatCapacity on the same basis, reported beside it.
Run with an explicitly supplied candidate wheel installed; its SHA-256 is recorded.
"""
from __future__ import annotations

import json
from pathlib import Path

import shared_evaluation as shared
import verify_reference_calorics as vrc
import verify_temperature_reference as vt
from epcsaft import Mixture, PropertyObservable

OUTPUT = Path(__file__).resolve().parents[1] / "results" / "solution-heat-capacity"
PRESSURE_PA = 101325.0
STEP_K = (0.1, 0.05)
RESOLVE_RTOL = 1e-6
# g/mol in shared.COMPONENT_IDS order; reactions conserve mass, so feed mass is the solution mass.
MOLAR_MASS = (44.0095, 61.0831, 18.01528, 62.0910, 104.0852, 61.0168, 60.0089, 19.0232, 17.0073)
# Observed loaded-solution cp, kJ/(kg K): Hilliard 2008 App. G.2 p. 937 (7 mol MEA/kg water, loading
# 0.358; uncertainty not transcribed) and Weiland 1997 Table 3 p. 1004 (30 wt%, loadings 0.3/0.4
# averaged to 0.35; +/-1 % repeatability).
MEASURED = ((298.15, "Weiland 1997 Table 3 (0.3/0.4 mean)", (3.457 + 3.418) / 2, 0.01),
            (318.15, "Hilliard 2008 App. G.2 (loading 0.358)", 3.3675, None),
            (353.15, "Hilliard 2008 App. G.2 (loading 0.358)", 3.4707, None))
# Liquid water cp at 0.101325 MPa, kJ/(kg K), IAPWS-95 (Wagner and Pruss 2002) via the NIST WebBook:
# attributes the solution-cp gap to the residual EOS of water.
WATER_CP = {298.15: 4.1813, 318.15: 4.1804, 353.15: 4.1965}


def water_ideal_cp(temperature: float) -> float:
    a, b, c, d, e = vrc.WATER_SHOMATE[:5]
    t = temperature / 1000.0
    return a + b * t + c * t * t + d * t**3 + e / (t * t)


def extensive_enthalpy(model: object, base: dict, temperature: float, warm: object) -> float:
    problem, result = vt.solve(model, vt.request_at(base, temperature, PRESSURE_PA, liquid_only=True), warm)
    (h, _), (n, _) = vrc.first_actions(model, problem, result, [
        vrc.observable("PhaseProperty", 0, prop=PropertyObservable.TotalEnthalpy),
        vrc.observable("PhaseAmount", 0)], [(0.0, 0.0, None)])[0]
    return h * n


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    vt.OUTPUT = OUTPUT
    model = Mixture(shared.load_parameters(), thermochemistry=vrc.record())
    packet = {o["identity"]: o["request"] for o in shared.load_state_packet()["observations"]}
    base = shared.corrected_request(packet["vle_obs_0130"], shared._selected_reactions())
    rows, warm = [], None
    for temperature, source, measured, relative in MEASURED:
        problem, result = vt.solve(model, vt.request_at(base, temperature, PRESSURE_PA, liquid_only=True), warm)
        warm = vt.anchor(problem, result)
        mass = sum(problem.feed.values[c] * m for c, m in zip(shared.COMPONENT_IDS, MOLAR_MASS)) / 1e3
        (h, dh), (n, dn) = vrc.first_actions(model, problem, result, [
            vrc.observable("PhaseProperty", 0, prop=PropertyObservable.TotalEnthalpy),
            vrc.observable("PhaseAmount", 0)], [(1.0, 0.0, None)])[0]
        ((cp, _),) = vrc.first_actions(model, problem, result, [  # cp's own T action is order 3, refused
            vrc.observable("PhaseProperty", 0, prop=PropertyObservable.TotalIsobaricHeatCapacity)],
            [(0.0, 0.0, None)])[0]
        equilibrium_cp = (n * dh + h * dn) / mass / 1e3
        water = [0.0] * len(shared.COMPONENT_IDS)
        water[vrc.WATER] = 1.0
        residual = model.state(temperature, P=PRESSURE_PA, x=water, phase="liquid").residual_isobaric_heat_capacity
        pure_water = (residual + water_ideal_cp(temperature)) / MOLAR_MASS[vrc.WATER]
        coarse, fine = ((extensive_enthalpy(model, base, temperature + s, warm)
                         - extensive_enthalpy(model, base, temperature - s, warm)) / (2 * s) / mass / 1e3
                        for s in STEP_K)
        rows.append({"T_K": temperature, "loading": problem.feed.values["carbon-dioxide"]
                     / problem.feed.values["monoethanolamine"], "mea_mass_fraction":
                     problem.feed.values["monoethanolamine"] * MOLAR_MASS[1] / 1e3 / mass,
                     "equilibrium_cp_kJ_per_kg_K": equilibrium_cp, "resolve_fine_kJ_per_kg_K": fine,
                     "resolve_coarse_kJ_per_kg_K": coarse, "resolve_rel": abs(equilibrium_cp - fine) / abs(fine),
                     "frozen_cp_kJ_per_kg_K": cp * n / mass / 1e3, "measured_kJ_per_kg_K": measured,
                     "measured_source": source,
                     "measured_uncertainty_kJ_per_kg_K": measured * relative if relative else None,
                     "model_minus_measured_rel": equilibrium_cp / measured - 1.0,
                     "pure_water_cp_model_kJ_per_kg_K": pure_water, "pure_water_cp_iapws_kJ_per_kg_K": WATER_CP[temperature],
                     "pure_water_model_minus_iapws_rel": pure_water / WATER_CP[temperature] - 1.0})
    hashes = {"heat_capacity": vt.write("heat_capacity", rows)}
    summary = {
        "engine_wheel_sha256": vt.wheel_sha256(), "csv_sha256": hashes,
        "criterion": f"|cp_action - FD| <= {RESOLVE_RTOL:g}|FD|, FD centered at {STEP_K[1]} K",
        "resolve_passed": sum(r["resolve_rel"] <= RESOLVE_RTOL
                              and abs(r["resolve_fine_kJ_per_kg_K"] - r["equilibrium_cp_kJ_per_kg_K"])
                              <= abs(r["resolve_coarse_kJ_per_kg_K"] - r["equilibrium_cp_kJ_per_kg_K"]) / 2
                              for r in rows),
        "resolve_total": len(rows),
        "claim_limit": "Equilibrium cp is numerically qualified against re-solves; the measured comparison is "
                       "empirical on one adopted model. Neutral ideal-gas cp inputs (water NIST Shomate "
                       "extrapolated below 500 K; MEA Zhang-Que-Chen 2011 Table 3, Aspen, uncertainty "
                       "unreported) enter cp directly. Hilliard loading 0.358 vs model 0.35.",
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    for r in rows:
        print({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
