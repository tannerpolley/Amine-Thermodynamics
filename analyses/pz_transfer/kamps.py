"""Issue 327: Kamps 2003 total-pressure comparison and the design check states, on the frozen A12 refit.

Comparison only: nothing here fits, selects or adopts. Run with agent-heavy:
  kamps.py kamps     95 Kamps Table 3 rows (precipitation row excluded), bubble pressure and phase census
  kamps.py checks    design check states: Hilliard feeds at 1.5 x bubble pressure; NMR liquids at T + 0.5 K
"""

import csv
import json
import os
import sys
from multiprocessing import Pool

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq
from binary_evidence import jsonable
from fit_speciation import declarations
from speciation import DC, HC, HPC, PC, PH, PH2
from reactive import AN, CO2, PZ, W, endpoint, laws_at, nmr_phases, phases, pressure_problem, problem, summarize_census
from run import verify_wheel, write_csv
from speciation import save

CARBAMATE_LAW_K = (283.15, 333.15)  # Ermatchkov 2003 NMR tabulated temperatures
PROTONATION_LAW_K = (293.14, 353.42)  # Hamborg 2009 Table 16 run temperatures
R2_LAW_K = (293.15, 393.15)  # shared CO2 first-dissociation law interval (results/speciation-reactions.json)
SOLVENT_MASS = 0.007  # Kamps p.2664: solvent mass at most +-0.7 % relative


def law_label(T, span):
    lo, hi = span
    return "inside" if lo <= T <= hi else f"outside ({T - hi:+.2f} K)" if T > hi else f"outside ({T - lo:+.2f} K)"


def group(r):
    if float(r["mCO2"]) == 0:
        return "unloaded"
    if float(r["p_MPa"]) < 0.2:
        return "below 0.2 MPa"
    return "374-395 K" if float(r["T_K"]) > 370 else "313-354 K, 0.2 MPa and above"


def init():
    global PAR, OFFSETS, MODEL
    PAR, OFFSETS, _ = endpoint("A12")
    MODEL = epcsaft.Mixture(PAR)


def kamps_row(r):
    row = dict(T_K=r["T_K"], mPZ=float(r["mPZ"]), alpha_per_PZ=float(r["alpha_per_PZ"]), pCO2_kPa=float(r["p_MPa"]) * 1000)
    prob = pressure_problem(PAR, row, OFFSETS)
    try:
        state = phases(PAR, prob)
    except Exception as error:
        state = dict(passed=False, exception=type(error).__name__, message=str(error), pressure_Pa=float("nan"), requested_tolerance_met=False)
    # The source solvent is the prepared PZ solution (mPZ known to 0.1 %), so a solvent-mass error d at fixed charged CO2
    # changes the CO2 molality and the loading by 1/(1+d), not the water alone.
    shifted = {}
    for d in (SOLVENT_MASS, -SOLVENT_MASS):
        s = eq.solve_equilibrium(MODEL, pressure_problem(PAR, dict(row, alpha_per_PZ=row["alpha_per_PZ"] / (1 + d)), OFFSETS))
        shifted[d] = s.pressure if s.requested_tolerance_met else float("nan")
    liquid = eq.solve_equilibrium(MODEL, prob)
    x = dict(zip(PAR.component_ids, liquid.mole_fractions[: len(PAR.component_ids)]))
    pz_total = sum(x[i] for i in (PZ, PH, PH2, PC, HPC, DC))
    co2_total = x[CO2] + x[HC] + x["carbonate-anion"] + x[PC] + x[HPC] + 2 * x[DC]
    p, obs = state["pressure_Pa"] / 1e6, float(r["p_MPa"])
    u_high = 0.010
    u_low = 0.004 if obs <= 4 else 0.010
    return dict(
        row=int(r["row"]), block=int(r["block"]), T_printed_K=float(r["T_printed_K"]), T_K=float(r["T_K"]), mPZ=float(r["mPZ"]),
        mCO2=float(r["mCO2"]), alpha_per_PZ=float(r["alpha_per_PZ"]), group=group(r), observed_MPa=obs, calculated_MPa=p,
        available=bool(state.get("requested_tolerance_met")), relative_error=p / obs - 1, difference_kPa=1000 * (p - obs),
        within_4kPa_bound=abs(p - obs) <= u_low, within_10kPa_bound=abs(p - obs) <= u_high,
        solvent_mass_plus_0p7pct_relative_change=shifted[SOLVENT_MASS] / state["pressure_Pa"] - 1,
        solvent_mass_minus_0p7pct_relative_change=shifted[-SOLVENT_MASS] / state["pressure_Pa"] - 1,
        PZH2_share_of_PZ=x[PH2] / pz_total, PZH_share_of_PZ=x[PH] / pz_total, bicarbonate_share_of_CO2=x[HC] / co2_total if co2_total else float("nan"),
        molecular_CO2_share_of_CO2=x[CO2] / co2_total if co2_total else float("nan"),
        carbamate_law=law_label(float(r["T_K"]), CARBAMATE_LAW_K), protonation_law=law_label(float(r["T_K"]), PROTONATION_LAW_K), shared_R2_law=law_label(float(r["T_K"]), R2_LAW_K),
        phase_passed=bool(state["passed"]), undecided=bool(state.get("unresolved")), dense=bool(state.get("dense")), gas=bool(state.get("gas")),
        phase_message=state.get("message", ""),
    ), state


def stats(rows):
    e = np.array([r["relative_error"] for r in rows])
    return dict(n=len(rows), AARD_percent=100 * float(np.mean(abs(e))), bias_percent=100 * float(np.mean(e)),
                within_4kPa=sum(r["within_4kPa_bound"] for r in rows), within_10kPa=sum(r["within_10kPa_bound"] for r in rows),
                phase_passed=sum(r["phase_passed"] for r in rows))


def by(rows, key):
    return {str(k): stats([r for r in rows if key(r) == k]) for k in dict.fromkeys(key(r) for r in rows)}


def kamps():
    source = [r for r in csv.DictReader((AN / "inputs/kamps2003-table3.csv").open()) if r["decision"].startswith("score")]
    with Pool(int(os.environ["AGENT_HEAVY_CORES"]), initializer=init) as pool:
        out = pool.map(kamps_row, source)
    rows = [r for r, _ in out]
    write_csv("kamps2003-A12.csv", rows)
    census = [dict(s, row=r["row"], T_K=r["T_K"]) for r, s in out]
    summary = dict(
        endpoint="A12 (frozen 12-coordinate refit)", rows=len(rows), all_available=all(r["available"] for r in rows),
        overall=stats(rows), by_group=by(rows, lambda r: r["group"]), by_temperature=by(rows, lambda r: r["T_K"]),
        by_block=by(rows, lambda r: f"{r['T_K']} K, {r['mPZ']} mol/kg"),
        loaded_by_group_excluding_unloaded=stats([r for r in rows if r["group"] != "unloaded"]),
        census=summarize_census(census),
    )
    save("kamps2003-A12.json", jsonable(dict(summary=summary, states=census)))
    print(json.dumps(jsonable(summary), indent=1), flush=True)


def hilliard_check(h):
    sol = eq.solve_equilibrium(MODEL, pressure_problem(PAR, h, OFFSETS))
    assert sol.requested_tolerance_met, h["row"]
    prob = problem(laws_at(OFFSETS), float(h["T_K"]))
    prob.feed.values = {PZ: 1.0, W: 1 / (0.0180153 * float(h["mPZ"])), CO2: float(h["alpha_per_PZ"])}
    prob.P = 1.5 * sol.pressure
    try:
        out = phases(PAR, prob)
    except Exception as error:
        out = dict(passed=False, exception=type(error).__name__, message=str(error))
    return dict(out, row=f"Hilliard-{h['row']}", T_K=float(h["T_K"]), bubble_Pa=sol.pressure)


def nmr_check(r):
    r = dict(r, T_K=float(r["T_K"]) + 0.5)
    try:
        out = nmr_phases(PAR, r, OFFSETS)
    except Exception as error:
        out = dict(passed=False, exception=type(error).__name__, message=str(error))
    return dict(out, row=r["identity"], T_K=r["T_K"])


def checks():
    init()
    nmr = [r for r in declarations(par=PAR, offsets=OFFSETS)[5] if r["group"] == 1]
    hilliard = list(csv.DictReader((AN / "inputs/hilliard-d5.csv").open()))
    with Pool(int(os.environ["AGENT_HEAVY_CORES"]), initializer=init) as pool:
        h = pool.map(hilliard_check, hilliard)
        n = pool.map(nmr_check, nmr)
    summary = {"Hilliard feeds, liquid at 1.5 x model bubble pressure": summarize_census(h),
               "NMR liquids at T + 0.5 K, 0.1 MPa (1.05 x bubble where that exceeds 0.1 MPa)": summarize_census(n)}
    save("check-states-A12.json", jsonable(dict(summary=summary, hilliard=h, nmr=n)))
    print(json.dumps(jsonable(summary), indent=1), flush=True)


def direct():
    """Record-census split rows that the 1.5 x bubble search reports clean: tpd(w) = sum w_i [ln w_i + ln phi_i(w) - ln z_i - ln phi_i(z)]
    evaluated directly at the record split composition w, liquid parent z, at 1.5 x bubble pressure (diagnosis-308/refit_checks.py form)."""
    init()
    record = {s["row"]: s for s in json.loads((AN / "results/reactive-A12-census.json").read_text())["states"]}
    check = json.loads((AN / "results/check-states-A12.json").read_text())["hilliard"]
    hilliard = {h["row"]: h for h in csv.DictReader((AN / "inputs/hilliard-d5.csv").open())}
    ids, out = list(PAR.component_ids), []
    for c in check:
        rowid = c["row"].removeprefix("Hilliard-")
        if not record[rowid].get("dense"):
            continue
        h = hilliard[rowid]
        z = np.array([{PZ: 1.0, W: 1 / (0.0180153 * float(h["mPZ"])), CO2: float(h["alpha_per_PZ"])}.get(i, 0.0) for i in ids])
        prob = problem(laws_at(OFFSETS), float(h["T_K"]))
        prob.feed.values = dict(zip(ids, z))
        prob.P = 1.5 * c["bubble_Pa"]
        z = np.array(eq.solve_equilibrium(MODEL, prob).mole_fractions[: len(ids)])
        split = next(t for t in record[rowid]["trials"] if t["resolved_descent"])
        w = np.array(split["composition"][: len(ids)])
        T, P = float(h["T_K"]), prob.P
        lz = np.array(MODEL.state(T, P=P, phase="liquid", x=list(z), derived_properties=True).log_fugacity_coefficient)
        lw = np.array(MODEL.state(T, P=P, phase="liquid", x=list(w), derived_properties=True).log_fugacity_coefficient)
        k = w > 0
        out.append(dict(row=c["row"], check_search_passed=c["passed"], record_engine_tpd=split["quantities"]["tpd_over_rt"],
                        direct_tpd_at_1p5_bubble=float(np.sum(w[k] * (np.log(w[k]) + lw[k] - np.log(z[k]) - lz[k]))), pressure_Pa=P))
        print(json.dumps(out[-1]), flush=True)
    save("check-states-A12-direct.json", out)


if __name__ == "__main__":
    verify_wheel()
    {"kamps": kamps, "checks": checks, "direct": direct}[sys.argv[1]]()
