"""MDEA re-transfer #343: fixed-pressure binary penalty and miscibility check."""
import math
from pathlib import Path
import sys
import time

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS.parent))
from part_ii import Route, epcsaft, np, stable
import reduced_refit_338 as refit


COMPOSITIONS = np.array(sorted({0., 1., *np.linspace(.001, .999, 999),
                                 *np.geomspace(1e-6, .001, 21), * (1-np.geomspace(1e-6, .001, 21))}))


def binary_gaps(model, amine, T, pressure, x=COMPOSITIONS):
    """Lower-convex-envelope gaps of G/(RT) for amine-water liquid at (T, P); None when any composition is unavailable."""
    y = np.array([x if cid == amine else 1-x for cid in model.parameters.component_ids]).T
    with np.errstate(divide='ignore'):
        ideal = np.sum(y*np.log(np.where(y > 0, y, 1)), axis=1)
    batch = model.states([T]*len(x), P=pressure, x=y.tolist(), phase='liquid')
    if any(v is None for v in batch.log_fugacity_coefficient):
        return [dict(x_MDEA=float(z), cause=c) for z,v,c in zip(x,batch.log_fugacity_coefficient,batch.cause,strict=True) if v is None], None
    g = ideal + np.sum(y*np.array(batch.log_fugacity_coefficient), axis=1)
    hull, gaps = [], []
    for i in range(len(x)):
        while len(hull) >= 2:
            a, b = hull[-2:]
            if (g[b]-g[a])*(x[i]-x[b]) < (g[i]-g[b])*(x[b]-x[a]):
                break
            hull.pop()
        hull.append(i)
    for a,b in zip(hull,hull[1:]):
        if b>a+1:
            chord = np.interp(x[a:b+1],x[[a,b]],g[[a,b]])
            excess = g[a:b+1]-chord
            if max(excess)>16*np.spacing(max(1.,abs(g[a]),abs(g[b]))):
                gaps.append(dict(x_MDEA_contacts=x[[a,b]].tolist(), x_MDEA_max_excess=float(x[a+np.argmax(excess)]),
                                 max_g_excess_over_RT=float(max(excess))))
    return None, gaps


def binary_scan(route, point):
    amine, water = route.config['amine'], 'water'
    parameters = epcsaft.Parameters.from_mapping(point['parameters'], components=[amine, water])
    model = epcsaft.Mixture(parameters)
    x = COMPOSITIONS
    pressure = 1466000.
    first, last = route.config['calculation_interval_K']
    temperatures = sorted({first, last, *range(math.ceil(first/5)*5, 422, 5), 393.15, 413.15, 422.})
    records = {}

    def evaluate(T):
        record = records[T] = dict(temperature_K=T, pressure_Pa=pressure)
        unavailable, gaps = binary_gaps(model, amine, T, pressure)
        if unavailable:
            record['unavailable'] = unavailable
            return False
        record['gaps'] = gaps
        return bool(gaps)

    started = time.monotonic()
    splits = [T for T in temperatures if evaluate(T)]
    if splits and min(splits)>first:
        lo, hi = max(T for T in temperatures if T<min(splits)), min(splits)
        while hi-lo>.1:  # bracket the sampled onset to 0.1 K
            midpoint = (lo+hi)/2
            if evaluate(midpoint):
                hi = midpoint
            else:
                lo = midpoint
    else:
        lo = hi = None
    return dict(pressure_Pa=pressure, composition_points=len(x), sampled_onset_bracket_K=[lo,hi],
                rows=[records[T] for T in sorted(records)], seconds=time.monotonic()-started)

if __name__ == '__main__':
    route = Route(ANALYSIS/'inputs/retransfer-343-binary-penalty.json')
    index = int(sys.argv[1])
    reference = route.config['starts'][index]
    start = point = route.start(reference)
    profile = route.result(f'profile-start-{index}.json')
    assert profile['identity'] == route.result('identity.json')
    assert profile['complete_residual'] and profile['complete_derivatives'], reference['label']
    projection = max(profile['projections_s'].values())
    assert projection*len(stable.STAGES) <= 3600, 'Projected fit exceeds one hour'
    fixed = route.penalty_states([], route.bind(start))
    name = f'start-{index}'
    report = None
    for stage, scale in enumerate(stable.STAGES):
        mapping, report = refit.fit(f'{name}/binary-{stage}',point,{},[],scale=scale,route=route,penalty_rows=fixed)
        if mapping is None:
            break
        point = mapping
        tally = report['stability_tally']
        if not tally['descent'] or tally['unavailable'] or report['status']!='converged':
            break
    if report and point is not start:
        if report['stability_tally']['descent'] or report['stability_tally']['unavailable']:
            stable.retreat(name,start,point,fixed,shifts=({},{}),route=route,optimizer_report=report)
            if (route.out/name/'candidate.json').exists():
                point = route.result(f'{name}/candidate.json')
        scan = binary_scan(route,point)
        route.write(f'{name}/binary-mixing.json',scan)
        route.write(f'{name}/endpoint.json',point)
        print(reference['label'],report['status'],scan['sampled_onset_bracket_K'],flush=True)
