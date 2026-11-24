"""#411: MDEA fit with the CO2-free gap excluded by a bound on k(MDEA-water) at the hottest tested temperature.

Only k(MDEA-water) = a0 + a1 (T - T_ref) acts on the CO2-free binary. Re-referencing its linear law at the
hottest penalty temperature makes a0 the value there, so the gap-onset limit becomes an upper bound on a0.
"""
import copy
import json
import math
from pathlib import Path
import sys
import time

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from part_ii import Route, epcsaft, np, reg, stable
import reduced_refit_338 as refit
from retransfer_343 import binary_gaps, binary_scan

PAIR = 'pair/mdea-water/k_ij'
OLD = ANALYSIS/'results/retransfer-343/binary-penalty'
RESULTS = ANALYSIS/'results/bounded-binary-411'
DECLARATION = ANALYSIS/'inputs/bounded-binary-411.json'
# Gap onset is resolved on this composition grid; the hull grid's 0.001 spacing is too coarse near a critical point.
FINE = np.unique(np.concatenate([np.linspace(.001, .5, 4991), np.linspace(.5, .999, 500)]))


def law(mapping):
    pair = next(p for p in mapping['pairs'] if {p['component_id_a'], p['component_id_b']} == {'water', 'methyldiethanolamine'})
    return pair['coefficients'][0]['temperature_law']


def k_at(mapping, T):
    rule = law(mapping)
    terms = {t['power']: t['coefficient']['value']['magnitude'] for t in rule['terms']}
    return terms[0] + terms[1]*(T - rule['reference_temperature']['magnitude'])


def rereference(mapping, T_ref, a0=None):
    """Same linear k(T), written about T_ref (optionally with a0 replaced)."""
    out = copy.deepcopy(mapping)
    rule = law(out)
    value = k_at(mapping, T_ref)
    rule['reference_temperature']['magnitude'] = T_ref
    next(t for t in rule['terms'] if t['power'] == 0)['coefficient']['value']['magnitude'] = value if a0 is None else a0
    return out


def binary_model(mapping):
    return epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping, components=['methyldiethanolamine', 'water']))


def critical(mapping, temperatures, pressure):
    """Largest k(MDEA-water) at each T without a fine-grid hull gap, bisected to 1e-6 with every other value fixed."""
    rows = []
    for T in temperatures:
        def gap(k):
            unavailable, gaps = binary_gaps(binary_model(rereference(mapping, T, k)), 'methyldiethanolamine', T, pressure, FINE)
            assert not unavailable, (T, k, unavailable[:3])
            return gaps
        lo, hi = -0.5, 0.2
        assert not gap(lo) and gap(hi), T
        while hi-lo > 1e-6:
            mid = (lo+hi)/2
            lo, hi = (lo, mid) if gap(mid) else (mid, hi)
        first = gap(hi)[0]
        rows.append(dict(T_K=T, k_no_gap=lo, k_gap=hi, first_gap=first))
        print('critical', T, lo, first['x_MDEA_contacts'], flush=True)
    return rows


def binary_check(route, point):
    """The 78 #343 native binary searches and the 1,041-point hull scan at one point."""
    spec = route.bind(point)
    states = route.penalty_states([], spec)
    out = []
    for state in states:
        p = reg.predict(spec.model, route.stability_row(spec, state, 1.))
        out.append(dict(key=state['key'], status=p.status.name, value=p.value if p.status.name == 'Available' else None, message=p.message))
    scan = binary_scan(route, point)
    return dict(native=dict(states=len(out), available=sum(r['status'] == 'Available' for r in out),
                            descent=sum((r['value'] or 0.) < 0 for r in out), minimum=min((r['value'] for r in out if r['value'] is not None), default=None), rows=out),
                hull=dict(onset_bracket_K=scan['sampled_onset_bracket_K'], gaps=sum(bool(r.get('gaps')) for r in scan['rows']),
                          unavailable=sum('unavailable' in r for r in scan['rows']), temperatures=len(scan['rows'])))


if __name__ == '__main__':
    step = sys.argv[1]
    if step == 'critical':
        point = stable.read(OLD/'start-0/endpoint.json')
        binary = json.loads((ANALYSIS/'inputs/retransfer-343-binary-penalty.json').read_text())['binary_penalty']
        temperatures = sorted({*binary['temperatures_K'], *range(290, 425, 5)})
        started = time.monotonic()
        rows = critical(point['parameters'], temperatures, binary['pressure_Pa'])
        RESULTS.mkdir(parents=True, exist_ok=True)
        (RESULTS/'critical-k.json').write_text(json.dumps(dict(
            pressure_Pa=binary['pressure_Pa'], compositions=len(FINE), seconds=time.monotonic()-started,
            basis='MDEA pure and water values of the interpolated #343 point; k(MDEA-water) constant at each T', rows=rows), indent=1)+'\n')
    elif step in ('fit', 'unbounded'):
        route = Route(DECLARATION)
        route.check_run_output()
        bound = route.config['k_bound']
        T_ref = bound['temperature_K']
        rows = route.load(bound['critical'])['rows']
        upper = next(r['k_no_gap'] for r in rows if r['T_K'] == T_ref) - bound['margin']
        starts = [route.load(s) for s in route.config['starts']]
        same = rereference(starts[0]['parameters'], T_ref)
        replayed = route.replay(dict(starts[0], parameters=same))[2]
        # Invariant: re-referencing the linear law leaves every prediction unchanged.
        assert abs(replayed/route.replay(starts[0])[2]-1) <= 1e-12, replayed
        indices = range(len(starts)) if step == 'fit' else [2]
        for index in indices:
            point = copy.deepcopy(starts[index])
            a0 = min(k_at(point['parameters'], T_ref), upper) if step == 'fit' else k_at(point['parameters'], T_ref)
            point['parameters'] = rereference(point['parameters'], T_ref, a0)
            coordinate = next(q for q in point['coordinates'] if q['identity'].startswith(PAIR+'/a0'))
            coordinate['origin'] = a0
            if step == 'fit':
                coordinate['bounds'] = [coordinate['bounds'][0], upper]
            name = f'{step}-{index}'
            route.write(f'{name}/start.json', point)
            started = time.monotonic()
            endpoint, report = refit.fit(name, point, {}, [], scale=None, route=route, penalty_rows=[])
            summary = dict(start=route.config['starts'][index], start_k_423=k_at(starts[index]['parameters'], T_ref), bound=upper if step == 'fit' else None,
                           wall_s=time.monotonic()-started, status=report and report['status'], data_cost=report and report['data_cost'],
                           active_bounds=report and report['covariance']['active_bounds'], iterations=report and report['iterations'])
            if endpoint is not None:
                route.write(f'{name}/endpoint.json', endpoint)
                summary.update(k_423=k_at(endpoint['parameters'], T_ref), checks=binary_check(route, endpoint))
                summary['checks']['native'].pop('rows')
            route.write(f'{name}/summary.json', summary)
            print(json.dumps(summary, default=str), flush=True)
    elif step == 'report':
        route = Route(DECLARATION)
        runs = {p.parent.name: stable.read(p) for p in sorted(route.out.glob('*/summary.json'))}
        bounded = {k: v for k, v in runs.items() if k.startswith('fit-') and v['status'] == 'converged'}
        chosen = min(bounded, key=lambda k: bounded[k]['data_cost'])
        point = route.result(f'{chosen}/endpoint.json')
        started = time.monotonic()
        route.reduce(point)
        reduce_s = time.monotonic()-started
        new = route.result('data-rows.json')
        old = stable.read(OLD/'post-binary/data-rows.json')

        def aard(rows, keep):
            p = [abs(r['value']/r['observed']-1) for r in rows if keep(r) and r.get('status') == 'Available' and r['observed']]
            return dict(rows=sum(map(keep, rows)), available=len(p), AARD_percent=100*math.fsum(p)/len(p) if p else None)
        groups = sorted({(r['group'], r['role'], r['unit']) for r in old})
        table = [dict(group=g, role=role, unit=unit, interpolated=aard(old, lambda r: (r['group'], r['role']) == (g, role)),
                      bounded=aard(new, lambda r: (r['group'], r['role']) == (g, role))) for g, role, unit in groups]
        pressure = {role: dict(interpolated=aard(old, lambda r: r['role'] == role and r['unit'] == 'Pa'),
                               bounded=aard(new, lambda r: r['role'] == role and r['unit'] == 'Pa')) for role in ('fitted', 'not fitted')}
        RESULTS.mkdir(parents=True, exist_ok=True)
        (RESULTS/'endpoint.json').write_text(json.dumps(point, indent=1)+'\n')
        (RESULTS/'comparison.json').write_text(json.dumps(dict(
            chosen=chosen, basis='Lowest fitted-data cost among converged bounded fits', runs=runs,
            interpolated=dict(data_cost=stable.read(OLD/'summary-row.json')['selected_retreated_fitted_data_cost'], k_423=k_at(stable.read(OLD/'start-0/endpoint.json')['parameters'], 423.)),
            k_versus_critical=[dict(T_K=r['T_K'], k=k_at(point['parameters'], r['T_K']), k_no_gap=r['k_no_gap'], below=k_at(point['parameters'], r['T_K']) < r['k_no_gap'])
                               for r in route.load(route.config['k_bound']['critical'])['rows']],
            pressure=pressure, groups=table, reduce_s=reduce_s), indent=1, default=str)+'\n')
        print(json.dumps(pressure), flush=True)
    elif step == 'search':
        route = Route(DECLARATION)
        point = stable.read(RESULTS/'endpoint.json')
        if not (route.out/'split-record.json').exists():  # same trial bank as the #343 search at the interpolated point
            route.write('split-record.json', stable.read(OLD/'split-record.json'))
        started = time.monotonic()
        result = route.search(point)
        result['seconds'], result['workers'] = time.monotonic()-started, route.workers
        (RESULTS/'stability.json').write_text(json.dumps(result, indent=1, default=str)+'\n')
        print(json.dumps({k: result['grid'][k] for k in ('states', 'available', 'descent')}), result['seconds'], flush=True)
