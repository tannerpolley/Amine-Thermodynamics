"""Probe the native liquid-vapor stationarity rows with liquid carbamate fraction as continuation coordinate."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import math
import os
from pathlib import Path
import time

import numpy as np
from scipy.optimize import root

import diagnose_census_parents as diag


def follow(entry, mode):
    state = entry['state']
    mapping = diag.s.parameter_mapping(diag.ENDPOINT)
    alpha = {diag.p.coefficient_key(i): diag.s.parameter_values(mapping)[diag.p.coefficient_key(i)]
             for i in diag.p.IONS}
    request = diag.phase.e.request(mapping, 313.15, .11)
    problem = diag.f.flash_problem(request, state['loading'], state['temperature_K'], state['pressure_Pa'])
    fixed_model = diag.model(mapping)
    native = diag.eq.compile_problem(fixed_model, problem)
    labels = native.coordinate_labels()
    carb = labels.index('ln x[L,component 4]')
    liquid_x = slice(0, 9)
    if mode == 'coefficient':
        path = entry['phase_results']['LV']['continuation']
        to_dimensionless, from_dimensionless = float, float
        def for_state(lam):
            m = diag.model(diag.s.with_parameter_values(mapping, {k: lam*v for k,v in alpha.items()}))
            return m, diag.eq.compile_problem(m, problem)
    else:
        path = entry['pressure_path']
        to_dimensionless = lambda P: math.log(P/state['pressure_Pa'])
        from_dimensionless = lambda logp: state['pressure_Pa']*math.exp(logp)
        def for_state(lam):
            problem.P = from_dimensionless(lam)
            return fixed_model, diag.eq.compile_problem(fixed_model, problem)
    control = 'fraction' if mode == 'coefficient' else 'pressure'
    known = [q for q in path if q.get('requested_tolerance_met')]
    if len(known) < 2:
        return dict(mode=mode, cause='fewer than two solved starts')
    previous = np.array(known[-1]['coordinates'])
    observed = previous[carb]
    second_last = known[-2]['coordinates'][carb]
    sign = math.copysign(1., observed-second_last)
    rows = []

    # Keep the Engine's equations and Jacobian. Exchange one native coordinate
    # with the external coefficient fraction or log pressure during this probe.
    def with_control(iterate, fixed):
        point = iterate.copy()
        point[carb] = fixed
        return point

    def stationarity(iterate, fixed):
        m, c = for_state(iterate[carb])
        return np.array(c.evaluate(with_control(iterate, fixed)).values)

    def jacobian(iterate, fixed):
        point = with_control(iterate, fixed)
        dimension = len(point)
        m, c = for_state(iterate[carb])
        J = np.array(c.jacobian(point)).reshape(-1, dimension)
        delta = np.zeros(dimension)
        delta[carb] = 1e-6
        J[:,carb] = (stationarity(iterate+delta, fixed)-stationarity(iterate-delta, fixed))/(2e-6)
        return J

    current = previous.copy()
    current[carb] = to_dimensionless(known[-1][control])
    fixed, stride = observed, .005
    for attempt in range(34):
        new_carb = fixed+sign*stride
        started = time.monotonic()
        try:
            solved = root(stationarity, current, jac=jacobian, args=(new_carb,), options={'maxfev':80, 'xtol':1e-9})
            eq_residual = float(np.max(np.abs(stationarity(solved.x, new_carb))))
            point = with_control(solved.x, new_carb)
            control_value = from_dimensionless(solved.x[carb])
            coeff = control_value if mode=='coefficient' else 1.
            mole_fractions = np.exp(point[liquid_x])
            D = 1.+coeff*math.fsum(alpha[diag.p.coefficient_key(i)]*mole_fractions[diag.s.COMPONENT_IDS.index(i)]
                                   for i in diag.p.IONS)
            amounts = [float(point[labels.index(f'n[{name}] / mol')]) for name in ('L', 'V')]
            result = dict(value=control_value, D=D, residual=eq_residual, coordinates=list(point),
                          amounts=amounts, seconds=time.monotonic()-started, solver_message=solved.message)
            if eq_residual<=1e-10 and D>0. and min(amounts)>0.:
                current, fixed = solved.x, new_carb
                stride = min(.02, stride*1.5)
                result['accepted'] = True
                rows.append(result)
                continue
        except (ValueError, OverflowError, diag.f.epcsaft.EosError) as error:
            result = dict(message=str(error), seconds=time.monotonic()-started)
        rows.append(dict(result, accepted=False, log_x_carb=new_carb))
        stride *= .5
        if stride<1e-6:
            break
    print(state['index'], mode, [(r['value'],r['D']) for r in rows if r['accepted']], flush=True)
    return dict(mode=mode, origin=known[-1][control], origin_D=known[-1]['D'][0], rows=rows)


def parent(entry):
    return dict(index=entry['state']['index'], runs=[follow(entry, mode) for mode in ('coefficient', 'pressure')])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args=parser.parse_args()
    diag.r.verify()
    started=time.monotonic()
    with ProcessPoolExecutor(int(os.environ['AGENT_HEAVY_CORES'])) as pool:
        rows=list(pool.map(parent,diag.r.read(args.input)['rows']))
    diag.s.write_json(args.output,dict(engine_commit=diag.p.COMMIT, wheel_sha256=diag.p.SHA,
                                     seconds=time.monotonic()-started, rows=rows))
