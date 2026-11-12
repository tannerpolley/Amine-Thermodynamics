"""Bounded checks of the 12-coordinate refits (#308 review, 12 November 2026); no fitting.

1. Start-1 availability: Hilliard bubble solves at the design starts with three- and four-species vapour.
2. Missed dense splits: at the penalty-fit endpoint, the Full search finds no split at Hilliard rows 55/56,
   but a split exists 0.01-0.05 of a small optimizer step away. The tangent-plane distance
   tpd(w) = sum_i w_i [ln w_i + ln phi_i(w) - ln z_i - ln phi_i(z)] at that neighbour's split composition w is
   evaluated directly at both points (same T, P and parent z).
Run from analyses/pz_transfer: OMP_NUM_THREADS=1 agent-heavy uv run python diagnosis-308/refit_checks.py
"""
# ruff: noqa: E402
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
import reactive as R
from run import SHA, verify_wheel
from speciation import W, PZ, HPC, document

verify_wheel()
CO2 = R.CO2
rows = {r["row"]: r for r in csv.DictReader((R.AN / "inputs/hilliard-d5.csv").open())}
par0 = epcsaft.Parameters.from_mapping(document())
coords0, _ = R.chart(par0, R.calibration(par0, R.NMR_OFFSETS)[0])
out = dict(wheel_sha256=SHA)

# 1. Start-1 availability (design starts are the document values with stage-3 offsets).
model = epcsaft.Mixture(par0)
availability = {}
for label, support in (("three-species", [W, CO2, PZ]), ("four-species", [W, CO2, PZ, HPC])):
    R.VAPOR = support
    failed = []
    for rowid, row in rows.items():
        y = reg.predict(model, R.pressure_observation(par0, R.pressure_problem(par0, row, R.NMR_OFFSETS), row))
        if not (y.status.name == "Available" and y.requested_tolerance_met):
            failed.append(dict(row=rowid, status=y.status.name, message=y.message[:200]))
    availability[label] = dict(failed=len(failed), of=len(rows), rows=failed)
    print(label, len(failed), "failed", flush=True)
R.VAPOR = [W, CO2, PZ, HPC]
out["start1_availability"] = availability

# 2. Missed dense splits at the penalty-fit endpoint.
xs = np.array(R.read("reactive-A12s-fit.json")["optimizer"])
step = np.array([0.00066, 0.01349, 0.0, 0.00018, 0.00038, -8e-05, -7e-05, 0.00055, -0.00039, 0.00099, 0.0072, -0.00697])


def at(x):
    par = epcsaft.Parameters(reg.evaluate_coordinates(par0, coords0[:9], list(x[:9]), []).parameters, par0.component_ids, par0.site_ids)
    m = epcsaft.Mixture(par)
    prob = lambda rowid: R.pressure_problem(par, rows[rowid], list(x[9:]))  # noqa: E731
    return par, m, prob


def tpd(x, rowid, w):
    par, m, prob = at(x)
    sol = eq.solve_equilibrium(m, prob(rowid))
    n = len(par.component_ids)
    z, w = np.array(sol.mole_fractions[:n]), np.array(w[:n])
    T = float(rows[rowid]["T_K"])
    lz = np.array(m.state(T, P=sol.pressure, phase="liquid", x=list(z), derived_properties=True).log_fugacity_coefficient)
    lw = np.array(m.state(T, P=sol.pressure, phase="liquid", x=list(w), derived_properties=True).log_fugacity_coefficient)
    k = w > 0
    return float(np.sum(w[k] * (np.log(w[k]) + lw[k] - np.log(z[k]) - lz[k])))


missed = []
for rowid, t in (("55", 0.05), ("56", 0.01)):
    par, m, prob = at(xs + t * step)
    neighbour = R.phases(par, prob(rowid))
    split = next(q for q in neighbour["trials"] if q["resolved_descent"])
    par_e, m_e, prob_e = at(xs)
    endpoint = R.phases(par_e, prob_e(rowid))
    missed.append(dict(
        row=rowid, step_fraction=t, neighbour_engine_tpd=split["quantities"]["tpd_over_rt"],
        neighbour_direct_tpd=tpd(xs + t * step, rowid, split["composition"]),
        endpoint_direct_tpd=tpd(xs, rowid, split["composition"]),
        endpoint_engine_passed=endpoint["passed"], endpoint_engine_dense=endpoint["dense"],
        component_order=list(par.component_ids), split_composition=split["composition"],
    ))
    print(json.dumps({k: v for k, v in missed[-1].items() if k not in ("component_order", "split_composition")}), flush=True)
out["missed_dense_splits"] = dict(step_optimizer_units=step.tolist(), endpoint_optimizer=xs.tolist(), rows=missed)
(Path(__file__).parent / "refit-checks.json").write_text(json.dumps(out, indent=2) + "\n")
