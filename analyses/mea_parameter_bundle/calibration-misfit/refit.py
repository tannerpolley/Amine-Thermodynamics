"""Diagnostic nonlinear refit of a named parameter subset against pCO2 and liquid speciation.

Usage: refit.py [--iterations=N] NAME identity@lower@upper[@start] ...  (start defaults to the adopted value)
Stopping: below a 2 % drop in calibration pCO2 RMS per iteration, or with --iterations only the
least_squares default tolerances, capped at N iterations.
Calibration: every packet state except 80 degC. Validation: the 80 degC isotherm
(Jou 1995 pressure, reserved_validation in the grouped split manifest, plus Bottinger 2008).
Residuals: pCO2 ln(pred/obs)/0.3 (the #101 data floor); species (pred-obs)/(0.1 obs + 0.001).
The NMR "HCO3-" observation is compared with model HCO3- + CO3^2- (fast-exchange carbon pool).
Writes results/runs/calibration-misfit/refit-NAME.jsonl (every evaluation) and the result JSON beside this script.
Diagnostic only: never writes the selected parameter record.
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

import probe

SIGMA_LN_P = 0.3


def residuals(rec):
    """(kind, target identity, scaled residual, ln residual) for one evaluated state."""
    if rec['status'] != 'evaluated':
        return None
    out = []
    for t in rec['targets']:
        if t['prediction_identity'] == 'co2-partial-pressure':
            ln = math.log(rec['predictions']['co2-partial-pressure'] / t['observed'])
            out.append(('p', t['identity'], ln / SIGMA_LN_P, ln))
            continue
        x = rec['liquid']['mole_fractions']
        pred = rec['predictions'][t['prediction_identity']]
        if t['identity'].endswith('::HCO3-'):
            pred = x[5] + x[6]
        ln = math.log(pred / t['observed']) if t['observed'] > 0 and pred > 0 else float('nan')
        out.append(('s', t['identity'], (pred - t['observed']) / (0.1 * t['observed'] + 0.001), ln))
    return out


def is_validation(rec):
    return round(rec['T'] - 273.15) == 80


def main(argv):
    cap = int(argv.pop(0).split('=')[1]) if argv[0].startswith('--iterations=') else None
    name, specs = argv[0], argv[1:]
    ids, lo, hi, start = [], [], [], {}
    for s in specs:
        ident, a, b, *x = s.split('@')
        ids.append(ident)
        lo.append(float(a))
        hi.append(float(b))
        if x:
            start[ident] = float(x[0])
    base_vals = probe.shared.parameter_values(probe.with_values(probe.shared.parameter_mapping(),
                                                                {i: 0.0 for i in ids if i.endswith(probe.SLOPE)}))
    x0 = np.array([start.get(i, base_vals[i]) for i in ids])
    log = probe.SCRATCH / f'refit-{name}.jsonl'
    log.parent.mkdir(parents=True, exist_ok=True)
    base = {r['identity']: r for r in probe.evaluate()}
    keys = [(r['identity'], k) for r in base.values() if not is_validation(r) and residuals(r) for k in residuals(r)]
    order = [(i, k[1]) for i, k in keys]

    def evaluate_all(x):
        recs = {r['identity']: r for r in probe.evaluate(dict(zip(ids, map(float, x))))}
        with log.open('a') as h:
            h.write(json.dumps({'x': list(map(float, x)), 'states': list(recs.values())}) + '\n')
        return recs

    def scaled(recs):
        table = {}
        for i, r in recs.items():
            for kind, tid, sc, ln in residuals(r) or []:
                table[(i, tid)] = (kind, sc, ln)
        return table

    fallback = scaled(base)

    def fun(x):  # a state that fails at a trial point keeps its adopted-model residual (zero derivative)
        table = scaled(evaluate_all(x))
        return np.array([table.get(k, fallback[k])[1] for k in order])

    steps = np.array([10.0 if i.endswith(probe.SLOPE) else 0.01 if 'k_ij' in i
                      else 0.05 if i.startswith('reaction:') else 0.02 * abs(v)
                      for i, v in zip(ids, x0)])
    memo = {}

    def fun_memo(x):
        key = tuple(map(float, x))
        if key not in memo:
            memo[key] = fun(x)
        return memo[key]

    def jac(x):  # forward differences at the sweep steps; stepping inward at an upper bound
        f0 = fun_memo(x)
        cols = []
        for k, h in enumerate(steps):
            h = -h if x[k] + h > hi[k] else h
            xk = np.array(x, float)
            xk[k] += h
            cols.append((fun_memo(xk) - f0) / h)
        return np.array(cols).T

    pressure_rows = np.array([k[0] == 'p' for _, k in keys])
    history = []

    def pressure_rms(f):
        return float(np.sqrt(np.mean(np.square(f[pressure_rows] * SIGMA_LN_P))))

    def stop_rule(intermediate_result):  # the lane's rule: stop below a 2 % drop in calibration pCO2 RMS per iteration
        history.append(pressure_rms(intermediate_result.fun))
        print('iteration', len(history), 'x', list(intermediate_result.x), 'pCO2 RMS ln', history[-1], flush=True)
        if cap is not None:
            if len(history) >= cap:
                raise StopIteration
            return
        previous = history[-2] if len(history) > 1 else pressure_rms(fun_memo(x0))
        if previous - history[-1] < 0.02 * previous:
            raise StopIteration

    fit = least_squares(fun_memo, x0, jac=jac, bounds=(lo, hi), x_scale=steps, max_nfev=None if cap else 60, verbose=2,
                        callback=stop_rule)
    J = fit.jac
    dof = max(len(order) - len(ids), 1)
    s2 = 2 * fit.cost / dof
    cov = np.linalg.pinv(J.T @ J) * s2
    sv = np.linalg.svd(J / np.maximum(np.linalg.norm(J, axis=0), 1e-300), compute_uv=False)

    def stats(recs, validation):
        v = {'p': [], 's': []}
        for r in recs.values():
            if is_validation(r) != validation:
                continue
            for kind, tid, sc, ln in residuals(r) or []:
                if np.isfinite(ln):
                    v[kind].append(ln)
        def summary(a):
            return {'n': len(a), 'rms_ln': float(np.sqrt(np.mean(np.square(a)))) if a else None,
                    'mean_ln': float(np.mean(a)) if a else None}
        return {'pco2': summary(v['p']), 'speciation': summary(v['s'])}

    final = {r['identity']: r for r in probe.evaluate(dict(zip(ids, map(float, fit.x))))}
    result = {
        'name': name, 'parameters': ids, 'start': list(map(float, x0)), 'fitted': list(map(float, fit.x)),
        'bounds': [lo, hi], 'standard_error': list(map(float, np.sqrt(np.clip(np.diag(cov), 0, None)))),
        'correlation': (cov / np.outer(np.sqrt(np.diag(cov)), np.sqrt(np.diag(cov)))).tolist() if np.all(np.diag(cov) > 0) else None,
        'jacobian_singular_values_column_normalized': list(map(float, sv)),
        'status': int(fit.status), 'message': fit.message, 'pco2_rms_per_iteration': history,
        'nfev': int(fit.nfev), 'cost': float(fit.cost), 'n_residuals': len(order),
        'before': {'calibration': stats(base, False), 'validation': stats(base, True)},
        'after': {'calibration': stats(final, False), 'validation': stats(final, True)},
        'wheel_sha256': probe.shared.ENGINE_WHEEL_SHA256,
        'parameter_record_sha256': probe.shared.sha256(probe.shared.PARAMETERS),
        'state_packet_sha256': probe.shared.sha256(probe.shared.STATE_PACKET),
        'script_sha256': probe.shared.sha256(Path(__file__)),
    }
    Path(__file__).with_name(f'refit-{name}.json').write_text(json.dumps(result, indent=1))
    print(json.dumps({k: result[k] for k in ('fitted', 'standard_error', 'before', 'after')}, indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
