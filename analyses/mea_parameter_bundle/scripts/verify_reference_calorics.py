"""Differential heat of CO2 absorption from the Engine's reference calorics (Engine #138).

On the adopted model with neutral ideal-gas records (CO2 and water NIST Shomate, MEA
Zhang-Que-Chen 2011 Table 3) and reaction-completed ions:
- heat: dH_abs = h_CO2^ig - d(nH)/dn_CO2 on the liquid-only TP state (feed A1 of extensive H),
  against RT^2 d ln f_CO2/dT at fixed P and feed (Gibbs-Helmholtz, the T-A1 of ln a) and a
  centered feed re-solve;
- closure: at vle_obs_0130 the bubble-path RT^2 d ln(y P)/dT decomposed exactly as
  dH_abs + T vbar dP/dT + RT^2 d ln phi/dT (all from Engine first actions);
- calorimetry: dH_abs against Kim & Svendsen 2007 / Kim et al. 2014 at 313.15 K, 30 wt%.

dH_abs is independent of the neutral cp and anchor constants (they shift conserved moieties
only); cp itself is refused on this electrolyte (order-2 reference slope criterion).
Run with an explicitly supplied candidate wheel installed; its SHA-256 is recorded.
"""
from __future__ import annotations

import csv
import json
from math import comb
from pathlib import Path

import shared_evaluation as shared
import verify_temperature_reference as vt
from epcsaft import GAS_CONSTANT_J_PER_MOL_K as R
from epcsaft import (
    IdealCorrelation,
    IdealInterval,
    IdealPolynomial,
    IdealShomate,
    Mixture,
    PropertyObservable,
    ThermochemistryRecord,
    equilibrium,
)

OUTPUT = Path(__file__).resolve().parents[1] / "results" / "reference-calorics"
CALORIMETRY = Path(__file__).resolve().parents[3] / "data/reference/MEA/observations/calorimetry/MEA_heat_of_absorption_observations.csv"
PHYSICAL_CALORICS = Path(__file__).resolve().parents[3] / "data/reference/MEA/thermal/physical-ideal-gas-calorics.json"
CALORICS = json.loads(PHYSICAL_CALORICS.read_text())
CO2, WATER = vt.CO2, vt.WATER
IDENTITY_RTOL, RESOLVE_RTOL, CLOSURE_RTOL = 1e-6, 1e-6, 1e-5
FEED_STEP = 1e-4  # mol CO2, relative to ~1 mol MEA


def shomate_enthalpy(temperature: float, c: tuple[float, ...], formation: float) -> float:
    t = temperature / 1000.0
    return formation + 1000.0 * (c[0] * t + c[1] * t**2 / 2 + c[2] * t**3 / 3 + c[3] * t**4 / 4 - c[4] / t + c[5] - c[7])


def co2_gas_enthalpy(temperature: float) -> float:
    co2 = CALORICS["components"]["carbon-dioxide"]
    return shomate_enthalpy(temperature, co2["coefficients"], co2["formation_enthalpy_j_per_mol"])


def record() -> ThermochemistryRecord:
    references, p0 = CALORICS["components"], CALORICS["reference_pressure_pa"]
    centre = references["monoethanolamine"]["enthalpy_entropy_anchor_k"]
    cp = references["monoethanolamine"]["coefficients"]
    mea = [sum(a * comb(j, k) * centre ** (j - k) for j, a in enumerate(cp) if j >= k) for k in range(4)]
    intervals: list[list[IdealInterval]] = [[] for _ in shared.COMPONENT_IDS]
    for component, index in (("carbon-dioxide", CO2), ("water", WATER)):
        source = references[component]
        intervals[index] = [IdealInterval(*source["range_k"], True, True, IdealCorrelation(
            IdealShomate(tuple(source["coefficients"]), source["formation_enthalpy_j_per_mol"]),
            p0))]
    source = references["monoethanolamine"]
    intervals[shared.COMPONENT_IDS.index("monoethanolamine")] = [IdealInterval(
        *source["range_k"], True, True, IdealCorrelation(
            IdealPolynomial(mea, centre, 0.0, 0.0), p0))]
    return ThermochemistryRecord(p0, intervals)


def observable(kind: str, phase: int, component: int = 0, prop: object | None = None) -> object:
    kind_value = getattr(equilibrium.SolvedStateObservableKind, kind)
    if prop is None:
        return equilibrium.SolvedStateObservable(kind_value, phase, component)
    return equilibrium.SolvedStateObservable(kind_value, phase, component, prop)


def first_actions(model: object, problem: object, result: object, observables: list, directions: list) -> list:
    width = len(shared.COMPONENT_IDS)
    batches = equilibrium.solved_state_first_actions(equilibrium.compile_problem(model, problem), result, observables, [
        equilibrium.SolvedStateActionDirection(d_t, d_p, feed or [0.0] * width, []) for d_t, d_p, feed in directions])
    for batch in batches:
        for item in batch.results:
            if item.status.name != "Available":
                raise RuntimeError(f"{item.observable}: {item.status.name} {item.diagnostic_message}")
    return [[(item.value, item.action) for item in batch.results] for batch in batches]


def extensive_enthalpy(model: object, problem: object, extra: float, warm: object) -> float:
    shifted = dict(problem.feed.values)
    shifted[shared.COMPONENT_IDS[CO2]] += extra
    changed = equilibrium.Problem(T=problem.T, P=problem.P, feed=equilibrium.Amounts(shifted), phases=problem.phases,
                                  neutral_reference=problem.neutral_reference, reactions=problem.reactions)
    result = equilibrium.solve_equilibrium(model, changed)
    assert result.success, result.message
    (h, _), (n, _) = first_actions(model, changed, result, [
        observable("PhaseProperty", 0, prop=PropertyObservable.TotalEnthalpy), observable("PhaseAmount", 0)],
        [(0.0, 0.0, None)])[0]
    return h * n


def liquid_heat(model: object, base: dict, temperature: float, pressure: float, warm: object) -> dict:
    problem, result = vt.solve(model, vt.request_at(base, temperature, pressure, liquid_only=True), warm)
    width = len(shared.COMPONENT_IDS)
    feed = [0.0] * width
    feed[CO2] = 1.0
    (h, dh), (n, dn), (_, dv), (_, _) = first_actions(model, problem, result, [
        observable("PhaseProperty", 0, prop=PropertyObservable.TotalEnthalpy), observable("PhaseAmount", 0),
        observable("PhaseVolume", 0), observable("PhaseLogActivity", 0, CO2)], [(0.0, 0.0, feed)])[0]
    # The enthalpy T action needs cp, refused on this electrolyte; ln a carries the T side.
    (((_, t_ln_a),), ((_, p_ln_a),)) = first_actions(model, problem, result, [observable("PhaseLogActivity", 0, CO2)],
                                                     [(1.0, 0.0, None), (0.0, 1.0, None)])
    partial = n * dh + h * dn
    resolve = (extensive_enthalpy(model, problem, FEED_STEP, warm)
               - extensive_enthalpy(model, problem, -FEED_STEP, warm)) / (2 * FEED_STEP)
    heat = co2_gas_enthalpy(temperature) - partial
    gibbs_helmholtz = R * temperature**2 * t_ln_a + R * temperature
    apparent = sum(result.mole_fractions[shared.COMPONENT_IDS.index(c)] for c in (
        "carbon-dioxide", "carbamate-anion", "bicarbonate-anion", "carbonate-anion"))
    mea_total = sum(result.mole_fractions[shared.COMPONENT_IDS.index(c)] for c in (
        "monoethanolamine", "protonated-monoethanolamine", "carbamate-anion"))
    return {"T_K": temperature, "P_Pa": pressure, "apparent_loading": apparent / mea_total,
            "heat_kJ_per_mol": heat / 1e3, "gibbs_helmholtz_kJ_per_mol": gibbs_helmholtz / 1e3,
            "identity_rel": abs(heat - gibbs_helmholtz) / abs(gibbs_helmholtz),
            "partial_enthalpy_kJ_per_mol": partial / 1e3, "resolve_partial_kJ_per_mol": resolve / 1e3,
            "resolve_rel": abs(partial - resolve) / abs(resolve), "vbar_co2_m3_per_mol": dv, "dlna_dP_per_Pa": p_ln_a, "molar_h_J_per_mol": h}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    vt.OUTPUT = OUTPUT  # reuse the CSV writer for this result set
    model = Mixture(shared.load_parameters(), thermochemistry=record())
    reactions = shared._selected_reactions()
    packet = {o["identity"]: o["request"] for o in shared.load_state_packet()["observations"]}
    vle = shared.corrected_request(packet["vle_obs_0130"], reactions)
    speciation = shared.corrected_request(packet["Bottinger2008_state_058"], reactions)
    rows, closure = [], []
    # Bubble state: heat on the liquid-only TP state at the solved bubble pressure.
    problem, central = vt.solve(model, vt.request_at(vle, 313.15))
    warm = vt.anchor(problem, central)
    vapor = vt.phase_index(problem, "vapor")
    (p, dp), (y, dy), (_, d_ln_a_v) = first_actions(model, problem, central, [
        observable("Pressure", 0), observable("PhaseMoleFraction", vapor, CO2),
        observable("PhaseLogActivity", vapor, CO2)], [(1.0, 0.0, None)])[0]
    heat = liquid_heat(model, vle, 313.15, p, warm)
    rows.append({"state": "vle_obs_0130", **heat})
    t = 313.15
    rt2 = R * t * t
    ln_pco2 = rt2 * (dp / p + dy / y) / 1e3
    ln_f = (rt2 * d_ln_a_v + R * t) / 1e3
    # Exact model path: RT^2 dln f/dT|_bubble = dH_abs + RT^2 (dln a/dP)|_T,feed dP/dT; with system-pressure
    # reference rows dln a/dP differs from vbar_EOS/(RT) by the reference pressure dependence.
    predicted = heat["heat_kJ_per_mol"] + rt2 * heat["dlna_dP_per_Pa"] * dp / 1e3
    closure.append({"state": "vle_obs_0130", "T_K": t, "P_bubble_Pa": p, "pCO2_Pa": p * y,
                    "RT2_dlnpCO2_dT_kJ": ln_pco2, "RT2_dlnf_dT_kJ": ln_f,
                    "phi_term_kJ": ln_f - ln_pco2, "T_vbar_dPdT_kJ": t * heat["vbar_co2_m3_per_mol"] * dp / 1e3,
                    "RT2_dlna_dP_dPdT_kJ": rt2 * heat["dlna_dP_per_Pa"] * dp / 1e3, "dPb_dT_Pa_per_K": dp,
                    "heat_plus_pressure_kJ": predicted, "closure_rel": abs(predicted - ln_f) / abs(ln_f)})
    for temperature in vt.TEMPERATURES_K:
        problem, central = vt.solve(model, vt.request_at(speciation, temperature), warm)
        rows.append({"state": f"058@{temperature:g}K", **liquid_heat(model, speciation, temperature,
                                                                     central.pressure[0], vt.anchor(problem, central))})
    measured = [r for r in csv.DictReader(CALORIMETRY.open())
                if float(r["temperature_K"]) == 313.15 and r["mea_mass_fraction"] in ("0.30", "0.3")
                and 0.25 <= float(r["co2_loading_mol_per_mol_mea"]) <= 0.46 and r["source"].startswith("Kim")]
    # Both 30 wt% model states near 313 K: vle_obs_0130 (313.15 K) and 058 at 315 K.
    near = {r["state"]: r for r in rows if r["state"] in ("vle_obs_0130", "058@315K")}
    comparison = [{"source": r["source"], "table": r["source_table"], "loading": float(r["co2_loading_mol_per_mol_mea"]),
                   "measured_kJ_per_mol": float(r["dh_kj_per_mol_co2"]),
                   "uncertainty_kJ_per_mol": float(r["dh_kj_per_mol_co2"]) * float(r["measurement_uncertainty_relative_percent"] or "nan") / 100,
                   **{f"model_{state}_minus_measured_kJ": m["heat_kJ_per_mol"] - float(r["dh_kj_per_mol_co2"])
                      for state, m in near.items()}} for r in measured]
    hashes = {name: vt.write(name, data) for name, data in (("heat", rows), ("closure", closure), ("calorimetry", comparison))}
    passed = sum(r["identity_rel"] <= IDENTITY_RTOL and r["resolve_rel"] <= RESOLVE_RTOL for r in rows)
    summary = {
        "engine_wheel_sha256": vt.wheel_sha256(), "csv_sha256": hashes,
        "producer_sha256": shared.sha256(Path(__file__)), "parameter_sha256": shared.sha256(shared.PARAMETERS),
        "calorimetry_input_sha256": shared.sha256(CALORIMETRY),
        "physical_calorics_sha256": shared.sha256(PHYSICAL_CALORICS),
        "criteria": {"gibbs_helmholtz_rel": IDENTITY_RTOL, "feed_resolve_rel": RESOLVE_RTOL, "bubble_closure_rel": CLOSURE_RTOL},
        "heat_rows_passed": passed, "heat_rows_total": len(rows),
        "closure_passed": all(c["closure_rel"] <= CLOSURE_RTOL for c in closure),
        "claim_limit": "Numerical qualification of Engine calorics on one adopted model; the calorimetry "
                       "comparison is empirical and semi-differential in loading (finite increments). Neutral "
                       "records: CO2 NIST Shomate; water NIST Shomate extrapolated below 500 K; MEA Zhang-Que-Chen "
                       "2011 Table 3 (Aspen, uncertainty unreported), none of which affect dH_abs. Solution cp is "
                       "refused (ionic order-2 reference slope). Ideal-gas CO2 reference (<0.1 kJ/mol at these pressures).",
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    for r in rows:
        print(r["state"], round(r["apparent_loading"], 3), round(r["heat_kJ_per_mol"], 3), f"{r['identity_rel']:.1e}", f"{r['resolve_rel']:.1e}")
    print(closure)
    print(comparison)


if __name__ == "__main__":
    main()
