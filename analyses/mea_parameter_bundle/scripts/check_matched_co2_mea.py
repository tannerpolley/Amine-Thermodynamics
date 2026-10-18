"""Amendment 4 matched comparison (#170): A4-5 decision, Kiepe invariance, endpoint cold replay and centered derivatives."""
import math, multiprocessing, sys, time
from pathlib import Path
import numpy as np
import fit_campaign as campaign
import fit_observations as o
D, started, cpu = Path(sys.argv[1]), time.monotonic(), campaign.cpu_seconds()
COMMON, STEPS = ('PartialPressure', 'PhaseMoleFraction', 'AdditionEnthalpy'), (0.01, 0.005)
residual = lambda p, r: math.sqrt(r['weight'])*(math.log(p/r['observed']) if r['form'] in ('LogRatio', 'log_ratio') else (p-r['observed'])/r['scale'])
def costs(n):
    q, w = [x['quantity'] for x in n['rows']], n['weighted_residuals']
    part = lambda keep: math.fsum(.5*v*v for v, k in zip(w, q) if keep(k))
    return dict(C205=part(lambda k: True), C166=part(lambda k: k != 'pressure'), C149=part(lambda k: k in COMMON), **{k: part(lambda j, k=k: j == k) for k in sorted(set(q))})
def evaluate(q):
    v = o.reg.differentiate(params, coordinates, [i for _, i in rows], optimizer=q, thermochemistry=o.thermal.record())
    return [s.name for s in v.statuses], list(v.predictions), list(v.residual_optimizer_gradient)
result, natives, start = {}, {}, campaign.load(next((D/'information/information').glob('*-control'))/'native.json')
reference = {r['id']: math.sqrt(r['weight'])*x for r, x in zip(start['rows'], start['residuals'])}  # same-wheel fixed CO2-water binary
for arm in ('control', 'variant'):
    natives[arm] = native = campaign.load(D/arm/'native.json'); spec = campaign.load(D/f'{arm}-fit-spec.json')
    entry = dict(status=native['status'], message=native['message'], iterations=native['iterations'], available=native['statuses'].count('Available'), rows=len(native['rows']), rank=native['covariance']['rank'], singular_values=native['covariance']['singular_values'], active_bounds=native['covariance']['active_bounds'], projected_gradient_norm=native['covariance']['projected_gradient_norm'], costs=costs(native))
    params, rows = o.stage6_rows(spec, endpoint := campaign.load(D/arm/'usable-budget-endpoint.json'))
    rows = [(r, i) for r, i in rows if r['quantity'] != 'phase_density' and r['weight'] > 0]  # the fit's lambda-0 rows
    coordinates, n = campaign.stage6_coordinates(dict(spec, information_coordinates=[dict(c, bounds=[c['bounds'][0]-c['scale'], c['bounds'][1]+c['scale']]) for c in spec['information_coordinates']]), params, endpoint), len(spec['information_coordinates'])  # boxes widened one unit so centered steps at active bounds stay inside
    statuses, predictions, gradient = evaluate([0.]*n)
    replay = [residual(p, r) for p, (r, _) in zip(predictions, rows)] if statuses == ['Available']*len(rows) else None
    entry['cold_replay'] = dict(statuses_available=statuses.count('Available'), maximum_weighted_row_difference=max(abs(a-b) for a, b in zip(replay, native['weighted_residuals'])) if replay else None, cost_relative_difference=abs(math.fsum(.5*x*x for x in replay)/native['final_cost']-1) if replay else None)
    if replay:
        J = np.array(gradient).reshape(len(rows), n)*np.sqrt([r['weight'] for r, _ in rows])[:, None]
        with multiprocessing.get_context('fork').Pool(28) as pool:
            ends = pool.map(evaluate, [[s*h if k == j else 0. for k in range(n)] for j in range(n) for h in STEPS for s in (1, -1)])
        entry['derivatives'] = [dict(coordinate=j, step=h, all_available=all(ends[4*j+2*m+s][0] == statuses for s in (0, 1)), maximum_absolute=float(np.max(np.abs(d := np.array([(residual(a, r)-residual(b, r))/(2*h) for a, b, (r, _) in zip(ends[4*j+2*m][1], ends[4*j+2*m+1][1], rows)])-J[:, j]))), maximum_relative=float(np.max(np.abs(d)/np.maximum(np.abs(J[:, j]), 1e-300))), passed=bool(np.all((np.abs(d) <= 1e-8) | (np.abs(d) <= 1e-5*np.abs(J[:, j]))))) for j in range(n) for m, h in enumerate(STEPS)]
        free = [j for j in range(n) if j not in entry['active_bounds']]; entry['free_condition'] = float(np.linalg.cond(J[:, free]))
    entry['kiepe_vs_fixed_binary_start'] = max(abs(w-reference[r['id']]) for w, r in zip(native['weighted_residuals'], native['rows']) if r['quantity'] == 'pressure')
    entry['checks_passed'] = bool(native['status'] == 'converged' and entry['available'] == entry['rows'] == 205 and entry['rank'] == n and replay and entry.get('free_condition', math.inf) <= 1e4 and entry['cold_replay']['maximum_weighted_row_difference'] <= 1e-8 and entry['cold_replay']['cost_relative_difference'] <= 1e-8 and all(d['passed'] and d['all_available'] for d in entry['derivatives']) and entry['kiepe_vs_fixed_binary_start'] <= 1e-8)
    result[arm] = entry
c, v = result['control']['costs'], result['variant']['costs']
result['decision'] = dict(rule='C166_variant <= 0.90 C166_control and C149_variant <= 1.01 C149_control (A4-5)', C166_ratio=v['C166']/c['C166'], C149_ratio=v['C149']/c['C149'], decidable=result['control']['checks_passed'] and result['variant']['checks_passed'], variant_improves=v['C166'] <= .90*c['C166'] and v['C149'] <= 1.01*c['C149'])
campaign.write(D/'matched-checks.json', dict(result, cpu_s=campaign.cpu_seconds()-cpu, wall_s=time.monotonic()-started))
