"""DEA–water calibration on Horstmann Tables 4 and 6 and Cai Table 4 (#425)."""
import csv
from functools import lru_cache
import math
from pathlib import Path
import sys
from time import monotonic

import numpy as np
from scipy.optimize import LinearConstraint, minimize

from f2_carbamate import AN, OLD, P as PREFIX, dump, read
from part_ii import Route, eq, jsonable
from MEA.solvent_specification import residual_excess_enthalpy
from pinned import DEA, W, REF

sys.path.insert(0, str(AN/'diagnosis-410'))
from excess_enthalpy import mixture, pair, with_slope

REFERENCE = AN/'results/refit-413'
T_REF, T_HEAT, P_HEAT = 365.15, 363.15, 1.75e6
A_OLD, B_PROBE = -0.06363352262762448, -46.20553081855322
SCALE = np.array([.05, abs(B_PROBE)])
ENDPOINTS = np.array([293.15, 458.64])
CHART = np.column_stack((np.ones(2), 1/ENDPOINTS-1/T_REF))*SCALE
VLE, CAI, HEAT = GROUPS = ('Horstmann VLE', 'Cai VLE', 'Horstmann heat')
FILES = ('Horstmann2002_Table4_water_DEA_365K', 'Cai1996_Table4_water_DEA',
         'Horstmann2002_Table6_water_DEA_HE')
X_GRID = np.linspace(0, 1, 101)
FTOL = 1e-10  # #413 objective stopping tolerance

def rows():
    for group, file in zip(GROUPS, FILES, strict=True):
        with (REF/f'{file}.csv').open() as source:
            for row in csv.DictReader(source):
                x = float(row['x_water'])
                heat = group == HEAT
                yield dict(row, group=group, x=x, T=float(row['T_K']), fitted=0 < x < 1,
                           observed=float(row['HE_J_per_mol' if heat else 'P_kPa']),
                           measured_pressure_Pa=float(row['P_MPa' if heat else 'P_kPa'])*(1e6 if heat else 1e3))

def composition(x):
    return {c: n for c, n in ((DEA, 1-x), (W, x)) if n > 0}

def with_binary(doc, a, b):
    result = with_slope(doc, b)
    for c in pair(result, DEA, W)['coefficients']:
        if c['family']=='k_ij':
            c['value']['magnitude'] = a+b*(1/c_ref(result)-1/T_REF)
    return result

def c_ref(doc):
    return next(c['reference_temperature']['magnitude'] for c in pair(doc, DEA, W)['coefficients']
                if c['family']=='k_ij_reciprocal_temperature_slope')

def evaluate(doc, inputs, readback=False, row_tolerance=1e-10):
    model = mixture(doc)
    output = []
    for row in inputs:
        T, x, P = (row[k] for k in ('T', 'x', 'measured_pressure_Pa'))
        feed = composition(x)
        record = dict(row)
        try:
            if row['group'] == HEAT:
                value = residual_excess_enthalpy(model, T, P, feed)
            else:
                phases = [eq.Phase('L', kind='liquid', support=list(feed)),
                          eq.Phase('V', kind='vapor', support=list(feed), amount=eq.Pinned(0.))]
                problem = eq.Problem(T=T, P=eq.Free(P), feed=eq.Amounts(feed), phases=phases, row_tolerance=row_tolerance)
                result = eq.solve_equilibrium(model, problem)
                if not result.requested_tolerance_met:
                    raise ValueError(result.message)
                value = result.pressure/1000
                P = result.pressure
                if readback:
                    record.update(y_water_calculated=result.phase_mole_fractions(1)[list(model.component_ids).index(W)],
                                  bubble_liquid_density=result.molar_densities[0],
                                  equilibrium_residual=max(map(abs, result.residuals)))
            record['predicted'] = value if math.isfinite(value) else None
            if readback:
                state = model.state(T, P=P, x=feed, phase='liquid')
                record.update(dP_drho=state.pressure_density_derivative, liquid_density=state.molar_density,
                              returned_branch=state.returned_density_branch.name, density_branch_mismatch=state.density_branch_mismatch,
                              liquid_pressure_residual_Pa=state.pressure-P)
        except (ValueError, RuntimeError) as err:
            record.setdefault('predicted', None)
            record['message'] = str(err)
        output.append(record)
    return output

def reduce_rows(records):
    groups = {}
    for group in GROUPS:
        for selection in ('all', 'fitted', 'pure'):
            block = [r for r in records if r['group']==group and (selection=='all' or r['fitted']==(selection=='fitted'))]
            if not block:
                continue
            available = [r for r in block if r['predicted'] is not None]
            observed = np.array([r['observed'] for r in available])
            error = np.array([r['predicted'] for r in available])-observed
            relative = error/observed
            metrics = dict(observed=len(block), available=len(available), unit='J/mol' if group==HEAT else 'kPa')
            if available:
                metrics.update(aard=100*np.mean(abs(relative)), bias=100*np.mean(relative),
                               rmse=np.sqrt(np.mean(error**2)), signed_error=np.mean(error))
            groups[f'{group} / {selection}'] = metrics
    return groups

def heat_grid(doc):
    model = mixture(doc)
    return np.array([residual_excess_enthalpy(model, T_HEAT, P_HEAT, composition(x)) for x in X_GRID])

def residuals(records):
    if any(r['predicted'] is None for r in records):
        return None
    groups = [[r for r in records if r['group']==group] for group in GROUPS]
    return np.array([((r['predicted']-r['observed'])/1707 if group==HEAT
                      else math.log(r['predicted']/r['observed']))/math.sqrt(len(block))
                     for group, block in zip(GROUPS, groups, strict=True) for r in block])

def search(doc, inputs, start, constrained):
    rejected = []
    @lru_cache(maxsize=32)
    def evaluate_trial(q):
        if np.min(CHART @ q) < -1 or np.max(CHART @ q) >= 1:
            rejected.append(dict(q=q, k=(CHART@q).tolist()))
            return None, None
        data = evaluate(with_binary(doc, *(SCALE*q)), inputs)
        residual = residuals(data)
        if residual is None:
            rejected.append(dict(q=q, rows=data))
        return data, residual

    def cost(q):
        _, residual = evaluate_trial(tuple(q))
        return math.inf if residual is None else residual @ residual/2

    def feasibility(q):
        data, residual = evaluate_trial(tuple(q))
        if residual is None:
            return np.full(19, -math.inf)
        heats = np.array([r['predicted'] for r in data if r['group']==HEAT])
        metrics = reduce_rows(data)
        depth = min(heat_grid(with_binary(doc, *(SCALE*q))))
        return np.r_[-heats/1707, (depth+3414)/1707, (-853.5-depth)/1707,
                     (1040.933-metrics[f'{HEAT} / fitted']['rmse'])/1707,
                     (5-metrics[f'{VLE} / fitted']['aard'])/100,
                     (51.490316-metrics[f'{CAI} / fitted']['aard'])/100]

    bounds = LinearConstraint(CHART, -1., np.nextafter(1., 0.))
    extra = [{'type': 'ineq', 'fun': feasibility}] if constrained else []
    result = minimize(cost, np.array(start)/SCALE, method='SLSQP', jac='3-point',
                      constraints=[bounds, *extra], options=dict(ftol=FTOL, maxiter=60))
    return result, rejected

def main(out, mode):
    out.mkdir(parents=True, exist_ok=True)
    Route(OLD/f'{PREFIX}route.json', out)
    doc = read(REFERENCE/'selection.json')['chosen']['parameters']['parameters']
    inputs = list(rows())
    fit_rows = [r for r in inputs if r['fitted']]
    assert len(fit_rows)==63
    if mode=='time':
        started = monotonic()
        evaluated = evaluate(doc, fit_rows)
        elapsed = monotonic()-started
        dump(out/'timing.json', dict(seconds=elapsed, rows=evaluated, metrics=reduce_rows(evaluated)))
        assert residuals(evaluated) is not None
        print(f'{elapsed:.3f} s for {len(evaluated)} rows', flush=True)
        return
    assert (out/'timing.json').is_file()
    for i, start in enumerate(((A_OLD, 0.), (A_OLD, -46.2))):
        case = out/f'{mode}-{i}'
        case.mkdir(exist_ok=False)
        fit, rejected = search(doc, fit_rows, start, mode=='constrained')
        a, b = SCALE*fit.x
        endpoint = with_binary(doc, a, b)
        data = evaluate(endpoint, inputs, readback=True)
        r = residuals([row for row in data if row['fitted']])
        curve = heat_grid(endpoint)
        dump(case/'fit.json', jsonable(dict(a=a, b=b, k_endpoints=(CHART@fit.x).tolist(), start=start,
             solver={**fit, 'x':fit.x.tolist(), 'jac':fit.jac.tolist(), 'multipliers':fit.multipliers.tolist()}, rejected=rejected,
             replay_cost=None if r is None else r@r/2, metrics=reduce_rows(data), rows=data,
             heat_grid=list(zip(X_GRID.tolist(), curve.tolist(), strict=True)))))
        print(case, fit.message, a, b, fit.fun, flush=True)

if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
