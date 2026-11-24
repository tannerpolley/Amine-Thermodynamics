"""#411: MDEA fit with the CO2-free gap excluded by a bound on k(MDEA-water) at the hottest tested temperature.

Only k(MDEA-water) = a0 + a1 (T - T_ref) acts on the CO2-free binary. Re-referencing its linear law at the
hottest penalty temperature makes a0 the value there, so the gap-onset limit becomes an upper bound on a0.
"""
import copy
from collections import Counter
import json
import math
from pathlib import Path
import sys
import time
import types

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
    elif step == 'retain':
        # The files the paper displays read, in the #343 layouts, for the adopted bounded fit.
        route = Route(DECLARATION)
        point = stable.read(RESULTS/'endpoint.json')
        started = time.monotonic()
        route.uncertainty(point)
        # The pressure figure's 23 curves (483 rows), as retained for the #343 figure.
        route.config['curve_rows'] = dict(path='../results/retransfer-343/binary-penalty/curves/curve-rows.json',
                                          sha256='c566979aaf300ea3501ce3b2d4a665dedc4bab71ed15679aede78dbbd628cc01')
        route.curves(point)
        seconds = time.monotonic()-started
        unc, declared = route.result('conditional-uncertainty.json'), point['coordinates']
        assert all(not unc['active_bound_outward_descent'] or v for v in unc['active_bound_outward_descent'].values()), 'an active bound must hold the cost down'
        active = {declared[k]['identity'] for k in unc['active_bounds']}
        T_ref = route.config['k_bound']['temperature_K']
        UNITS = ['1', '1/K', '1', '1', 'K', '1', 'angstrom', 'K']
        table = [dict(name=q['identity'], unit=u, role='fitted', source='Bounded fit, k(MDEA-water) at 423 K at most the CO2-free gap onset',
                      value=q['origin'], bounds=q['bounds'], conditional_standard_error=unc['conditional_standard_error'].get(q['identity']),
                      on_bound=q['identity'] in active) for q, u in zip(declared, UNITS, strict=True)]
        old = stable.read(OLD/'parameter-table.json')
        sigma = next(r for r in table if r['name'].endswith('segment_diameter'))
        table += [dict(old[8], source='Tie to the fitted MDEAH+ segment diameter', value=sigma['value'], conditional_standard_error=sigma['conditional_standard_error']), *old[9:]]
        assert all(old[i]['name'].startswith(('pair/mdea-water/k_ij/a0', 'pair/mdea-water/k_ij/a1')) or old[i]['name'] == table[i]['name'] for i in range(8))
        rows = route.result('data-rows.json')
        by_id = {r['identity']: r for r in rows}
        pub = stable.read(OLD/'published-pressure-comparisons.json')
        for c in pub['comparisons']:
            c['selected_point_mean_absolute_relative_deviation_percent'] = 100*math.fsum(abs(by_id[i]['value']/by_id[i]['observed']-1) for i in c['row_ids'])/len(c['row_ids'])
        search = route.result('search-0.json')
        assert len(search) == 11824
        stability = stable.read(RESULTS/'stability.json')
        unavailable = [r for r in search if not r.get('available')]
        causes = Counter(('grid' if r['key'].startswith('grid:') else 'data', 'pressure reference' if (r.get('message') or '').startswith('pressure reference') else 'other') for r in unavailable)
        stability['unavailable_by_cause'] = [dict(tier=t, cause=c, count=n) for (t, c), n in sorted(causes.items())]
        stability['distinct_calculations'] = sum('same_calculation_as' not in r for r in search)
        descents = [r for r in search if r.get('descent')]
        gap = lambda w, v: max(max(abs(a-b) for a, b in zip(w['composition'], v['composition'])), abs(w['packing']-v['packing']))
        # #343 test: a liquid-labelled witness that coincides with a vapor-labelled one is the same vapor-connected root.
        stability['descent_witnesses'] = dict(records=len(descents), distinct_calculations=len({r.get('same_calculation_as', r['key']) for r in descents}),
            records_with_liquid_label=sum(any(w.get('density_side') == 2 for w in r.get('witnesses', [])) for r in descents),
            largest_liquid_to_vapor_witness_distance=max(min(gap(w, v) for v in r['witnesses'] if v.get('density_side') == 1)
                                                         for r in descents for w in r.get('witnesses', []) if w.get('density_side') == 2))
        witness = stability['descent_witnesses']
        assert witness['largest_liquid_to_vapor_witness_distance'] < 1e-6 and stability['grid']['branches']['grid']['native']['liquid'] == 0  # Engine PHASE_COINCIDENCE_DISTANCE
        if 'liquid_liquid_splits' in stability['grid']:  # seed labels, as #343 renamed them; the interpreted count follows
            stability['grid']['preliminary_seed_based_liquid_liquid_labels'] = stability['grid'].pop('liquid_liquid_splits')
        stability['liquid_liquid_splits_among_completed_searches'] = dict(
            distinct=0, basis='No grid record has a liquid-labelled descent; every liquid-labelled witness of the 48 measured records coincides with a vapor-labelled witness')
        spec, by_key = route.bind(point), {}
        for state in route.states(spec):
            by_key.setdefault(state['key'], state)
        ratios = []
        for key in sorted(witness_keys := {r.get('same_calculation_as', r['key']) for r in descents}):
            state = by_key[key]
            item = route.stability_row(spec, state, 1.)
            assert item.pressure_reference is None, key  # every descent is at an assigned pressure
            basis = route.pressure_basis(spec, state, item, types.SimpleNamespace(pressure_reference=None))
            ratios.append(dict(key=key, **basis, ratio=basis['declared_pressure_Pa']/basis['model_bubble_pressure_Pa']))
        stability['descent_witnesses'].update(bubble_pressure_ratio_range=[min(r['ratio'] for r in ratios), max(r['ratio'] for r in ratios)], calculations=ratios)
        split = "grid:{'water': 1.7987685418415897, 'methyldiethanolamine': 1.0}:363.15:1.368:1.05"
        stability['interpolated_set_split_state'] = {k: next(r for r in search if r['key'] == split).get(k) for k in ('key', 'available', 'message')}
        pressures = {role: dict(rows=len(p), relative_rows=len(p), AARD_percent=100*math.fsum(p)/len(p)) for role in ('fitted', 'not fitted')
                     for p in [[abs(r['value']/r['observed']-1) for r in rows if r['role'] == role and r['unit'] == 'Pa' and r['status'] == 'Available']]}
        summary = dict(amine='MDEA', point='bounded fit', free_fitted_parameters=len(declared), on_bounds=len(active), fitted_pressure=dict(statistics=pressures['fitted']),
                       not_fitted_pressure=dict(statistics=pressures['not fitted']), unavailable_searches=len(unavailable),
                       liquid_liquid_splits_found=stability['liquid_liquid_splits_among_completed_searches']['distinct'], data_cost=stable.read(RESULTS/'comparison.json')['runs']['fit-0']['data_cost'])
        for name, value in [('parameter-table.json', table), ('conditional-uncertainty.json', unc), ('published-pressure-comparisons.json', pub),
                            ('summary-row.json', summary), ('stability.json', stability), ('data-rows.json', rows), ('deviations.json', route.result('deviations.json')),
                            ('curves/curve-data.json', route.result('curve-data.json'))]:
            (RESULTS/name).parent.mkdir(parents=True, exist_ok=True)
            (RESULTS/name).write_text(json.dumps(value, indent=1, default=str)+'\n')
        print(json.dumps(dict(seconds=seconds, table=[(r['name'], r['value'], r['conditional_standard_error'], r['on_bound']) for r in table[:8]],
                              published=[(c['group'], c['selected_point_mean_absolute_relative_deviation_percent']) for c in pub['comparisons']],
                              causes=stability['unavailable_by_cause'], distinct=stability['distinct_calculations'], split=stability['interpolated_set_split_state']), default=str), flush=True)
