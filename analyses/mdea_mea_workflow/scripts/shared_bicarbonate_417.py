"""Fixed water–bicarbonate coordinate profiles and MDEA transfer (#417)."""
# ruff: noqa: E402 -- Part II and the retained MEA producers own their imports.
from collections import Counter
import hashlib
import json
import sys
import time

from bounded_binary_411 import DECLARATION, OLD, PAIR, RESULTS, Route, binary_check, k_at, np, rereference
from part_ii import ROOT, SHA, WHEEL, deviation_statistics, stable as r
from epcsaft.parameters import document_mapping
import paper_evidence_341 as paper

sys.path.insert(0, str(ROOT/'analyses/amp_transfer'))
from classify_descents import COINCIDENCE, classify, matched

f, s = paper.f, r.s
KEY = 'pair/bicarbonate-anion/water/k_ij'
K0 = 0.7650000233694618
ALLOWANCE = 1.3986782373879123
BASE = r.B/'results/reduced-refit'
OUT = RESULTS.parent/'shared-bicarbonate-417'
RUN = RESULTS.parent/'runs/417'/WHEEL.parent.name


def run_key(label, mapping, k):
    digest = s.parameter_fingerprint(mapping).split(':')[1]
    return RUN/f'{label}-{k!r}-{digest}'


def vapor_at_parent(model, state, trial):
    roots = matched(trial['roots'], 1e-10)
    if not roots or trial.get('reclosed_evidence') != 'evaluated' or trial['reclosed_quantities']['tpd_over_rt'] >= 0:
        return False
    root = min(roots, key=lambda q: q['log_density_distance'])
    if root['returned'] != 'unspecified':
        return root['returned'] == 'vapor'
    density = root['density']*np.geomspace(1e-4, 1., 33)
    batch = model.states([state['temperature_K']]*33, rho=density, x=trial['witness']['phase']['composition'], derived_properties=True)
    trial['isotherm'] = dict(density_mol_m3=density.tolist(), pressure_Pa=batch.pressure, dP_drho=batch.pressure_density_derivative, causes=batch.cause)
    return all(v is not None and v > 0 for v in batch.pressure_density_derivative) and all(np.diff(batch.pressure) > 0)


def witnesses(route, point, rows):
    descents = [row for row in rows if r.descent(row)]
    counts = Counter(unavailable_records=sum(not row['available'] for row in rows), descent_records=len(descents))
    details, candidates = [], []
    for row in descents:
        if 'same_calculation_as' in row:
            continue
        counts['distinct_descents'] += 1
        vapor = [w for w in row.get('witnesses', []) if w['density_side'] == 1]
        distances = [min((max(abs(w['packing']-v['packing']),
                         *(abs(a-b) for a,b in zip(w['composition'], v['composition'], strict=True)))
                         for v in vapor), default=None)
                     for w in row.get('witnesses', []) if w['density_side'] == 2]
        unmatched = sum(d is None or d >= COINCIDENCE for d in distances)
        counts['vapor_coincident'] += len(distances)-unmatched
        counts['unmatched_liquid_label'] += unmatched
        counts['calculations_with_vapor_coincidence'] += len(distances) > unmatched
        counts['calculations_with_unmatched_liquid_label'] += unmatched > 0
        details.append(dict(key=row['key'], distances=distances, unmatched=unmatched))
        if unmatched or row['native_branch'] == 'unresolved' or row['supplied_branch'] in ('liquid','mixed','unresolved'):
            candidates.append(row)
    spec = route.bind(point)
    phases = classify(route, point, candidates, route.states(spec))
    unmatched = {row['key'] for row in details if row['unmatched']}
    for state in phases:
        vapor = [vapor_at_parent(spec.model, state, trial) for trial in state.get('supplied_pressure_roots', [])]
        split = any(attempt['confirmed'] for attempt in state['attempts'])
        resolved = bool(vapor) and all(vapor) and state['key'] not in unmatched and state['native_branch'] != 'unresolved'
        state['phase_identity'] = 'two liquids' if split else 'vapor' if resolved else 'unresolved'
    counts['confirmed_distinct_splits'] = sum(state['phase_identity'] == 'two liquids' for state in phases)
    counts['unresolved_phase_identity'] = sum(state['phase_identity'] == 'unresolved' for state in phases)
    return dict(counts=counts, witnesses=details, pressure_roots=phases)


def mea_search(label, mapping, k):
    started = time.monotonic()
    r.OUT = run_key(label, mapping, k)
    registry = r.read(BASE/'split-registry.json')['trials']
    control = r.read(BASE.parent/'wheel-recheck-05e94210/stability-adopted-law/search.json')
    digest = hashlib.sha256(json.dumps(registry, sort_keys=True).encode()).hexdigest()
    assert len(registry) == 6121 and digest == control['registry_sha256']
    bank = r.read(BASE/'split-trials.json')
    r.write('search/grid-trials.json', bank)
    main, offset = r.states()
    grid = r.grid(mapping, main+offset, bank, capture=True)
    r.write('search/grid.json.gz', grid)
    census = r.census(mapping, 'search', dict.fromkeys(map(str, range(162)), registry),
                      keep_refusals=True, compact_supplied=True)
    supplied = Counter()
    for raw in r.result('search/census-raw.json.gz'):
        for report in raw.get('stability', []):
            supplied.update(report['supplied_counts'])
    assert (len(main), len(offset), census['states']) == (1908, 576, 162)
    summary = dict(grid=r.tally(grid[:len(main)]), offset=r.tally(grid[len(main):]), census=census,
                   supplied=dict(supplied), missing_supplied=162*len(registry)-sum(supplied.values()),
                   registry_sha256=digest, seconds=time.monotonic()-started, run=str(r.OUT.relative_to(ROOT)))
    r.write('search/summary.json', summary)
    return summary


def compare_rows(rows, old, fields, tolerance):
    for new, ref in zip(rows, old, strict=True):
        assert all(new.get(field) == ref.get(field) for field in fields), (new, ref)
        if new['status'] == 'Available':
            assert abs(new['value']-ref['value']) <= tolerance * max(1., abs(ref['value'])), (new, ref)


def bind_wheel():
    r.COMMIT, r.SHA, r.WHEEL = WHEEL.parent.name.removeprefix('main-'), SHA, WHEEL
    f.a.COMMIT, f.a.SHA, f.a.WHEEL = r.COMMIT, SHA, WHEEL
    s.ENGINE_COMMIT, s.ENGINE_WHEEL_SHA256 = r.COMMIT, SHA


def controls(mea, mdea):
    route = Route(DECLARATION, out=run_key('mdea-control', mdea, K0))
    bind_wheel()
    f.write('controls.json', dict(wheel_sha256=SHA, engine_commit=r.COMMIT, workers=route.workers,
                                mea=r.read(r.A6)['controls'], mdea=route.controls))
    mea_rows, ok, cost = r.replay(mea)
    f.write('reported-mea/replay.json', dict(rows=mea_rows, available=ok, cost=cost))
    ref = r.read(paper.OUT/'candidate/replay.json')
    assert ok and len(mea_rows) == 307 and f.a.relative(cost, ref['cost']) <= 1e-10
    compare_rows(mea_rows, ref['rows'], ('identity','group','status','observed','row'), 1e-10)
    rows, ok, mdea_cost = route.replay(mdea)
    route.write('replay.json', dict(rows=rows, available=ok, cost=mdea_cost))
    old_cost = r.read(RESULTS/'comparison.json')['runs']['fit-0']['data_cost']
    assert ok and f.a.relative(mdea_cost, old_cost) <= 1e-8
    route.reduce(mdea)
    old = r.read(RESULTS/'data-rows.json')
    compare_rows(route.result('data-rows.json'), old, ('identity','group','role','unit','status','observed','row','outside_ranges'), 1e-8)
    bound = route.config['k_bound']
    critical = route.load(bound['critical'])['rows']
    upper = next(row['k_no_gap'] for row in critical if row['T_K'] == 423.)-bound['margin']
    assert upper == -0.06711345443725586 and k_at(mdea['parameters'],423.) <= upper
    return cost, route, critical, upper


def mea_fit(k, label, source, coordinates, ties):
    f.OUT = run = run_key(f'mea-{label}', source, k)
    fixed = dict(f.LITERATURE, **{KEY: k})
    mapping, report = f.fit('fit', source, fixed, coordinates, ties)
    start = r.read(run/'fit/declaration.json')
    assert len(start['declared']) == 10 and all(q['identity'] != KEY for q in start['declared'])
    replay = r.read(run/'fit/replay.json') if (run/'fit/replay.json').exists() else {}
    cost = replay.get('cost') if mapping is not None and report['status'] == 'converged' else None
    if mapping is not None:
        values = s.parameter_values(mapping)
        assert values[KEY] == k and all(values[q] == values[q.replace('segment_diameter','born_diameter')] for q in ties)
    result = dict(start=label, k=k, cost=cost, start_cost=start['cost'],
                  status=report['status'] if report else 'start replay unavailable',
                  message=report['message'] if report else None,
                  active_bounds=report['covariance']['active_bounds'] if report and report.get('covariance') else [],
                  run=str(run.relative_to(ROOT)))
    f.OUT = OUT
    f.write(f'mea/{k!r}/{label}.json', result)
    return dict(result, mapping=mapping)


def profile(mea, control_cost):
    assert s.parameter_values(mea)[KEY] == K0
    starts = {'previous': s.parameter_mapping(BASE/'F1/parameters.json'),
              'current': s.parameter_mapping(f.a.RECORDS['candidate'])}
    declared = r.read(BASE/'F2/current/unpenalized/declaration.json')['declared']
    coordinates = [q['identity'] for q in declared if q['identity'] != KEY]
    ties = {q['identity']: [t for t in q['targets'] if t[0] == 'born_diameter']
            for q in declared if any(t[0] == 'born_diameter' for t in q['targets'])}
    for label, mapping in starts.items():
        values = s.parameter_values(mapping)
        original = r.read(BASE/f'F2/{label}/unpenalized/declaration.json')['declared']
        assert all(values[q['identity']] == q['origin'] for q in original)
        starts[label] = s.with_parameter_values(mapping, {q.replace('segment_diameter','born_diameter'): values[q] for q in ties})
    points, searches = {}, {}
    def fit(k, label, source):
        return mea_fit(k, label, source, coordinates, ties)
    def best(points):
        return min((p for p in points if p['cost'] is not None), key=lambda p: p['cost'], default=None)
    center = best([fit(K0, label, start) for label, start in starts.items()])
    if center is None or center['cost'] - control_cost > 1e-6*control_cost:
        center = best([center, fit(K0, 'reported-restart', mea)] if center else [fit(K0, 'reported-restart', mea)])
    assert center and center['cost'] - control_cost <= 1e-6*control_cost, center
    center_cost = min(center['cost'], control_cost)
    choices = {side: [end, K0+(end-K0)/2, K0+(end-K0)/4] for side, end in [('low', -.5), ('high', 1.)]}
    mea_search('mea-center', center['mapping'] if center['cost'] <= control_cost else mea, K0)
    while True:
        previous_cost, selected = center_cost, {}
        for side, candidates in choices.items():
            for k in candidates:
                if k not in points:
                    points[k] = best([fit(k, label, start) for label, start in starts.items()])
                    point = points[k]
                    if point and center_cost-point['cost'] > 1e-6*center_cost:
                        restart = fit(K0, f'restart-from-{k!r}', point['mapping'])
                        if restart['cost'] is not None and restart['cost'] < center_cost:
                            center, center_cost = restart, restart['cost']
                            mea_search('mea-center', center['mapping'], K0)
                point = points[k]
                if not point or point['cost']-center_cost > ALLOWANCE:
                    continue
                if k not in searches:
                    searches[k] = mea_search(f'mea-{side}', point['mapping'], k)
                q = searches[k]
                if not any(q[g]['unavailable'] or q[g]['descent'] for g in ('grid','offset')) and not (q['census']['incomplete'] or q['census']['descent']):
                    selected[side] = point
                    break
        if previous_cost == center_cost:
            break
    f.write('profile.json', dict(center=center, center_cost=center_cost, points=points, searches=searches,
                                 selected={side: selected.get(side) for side in choices}))
    return selected


def mdea_fit(side, k, reference, control, critical, upper):
    starts = [control.load(ref) for ref in control.config['starts']]
    route = Route(DECLARATION, out=run_key(f'mdea-{side}', reference, k))
    target = control.config['k_bound']['temperature_K']
    def common(m):
        return {q: v for q,v in s.parameter_values(m).items() if 'methyldiethanolamine' not in q and 'mdea' not in q and q != KEY}
    def laws(p):
        return [rx for rx in route.bind(p).spec['chemistry']['reactions']['aqueous'] if rx['name'] in ('R1','R2','R3')]
    endpoints = []
    for index, point in enumerate(starts):
        name = f'fit-{index}'
        mapping = s.with_parameter_values(point['parameters'], {KEY: k})
        assert common(mapping) == common(reference['parameters']) and laws(point) == laws(reference)
        assert len(point['coordinates']) == 8 and all(q['identity'] != KEY for q in point['coordinates'])
        equivalent = dict(point, parameters=rereference(mapping, target))
        before, after = route.replay(dict(point, parameters=mapping)), route.replay(equivalent)
        route.write(f'{name}/rereference.json', dict(original=before, shifted=after))
        assert before[1] and after[1] and f.a.relative(before[2], after[2]) <= 1e-12
        a0 = min(k_at(mapping, target), upper)
        point['parameters'] = rereference(mapping, target, a0)
        coordinate = next(q for q in point['coordinates'] if q['identity'].startswith(PAIR+'/a0'))
        coordinate.update(origin=a0, bounds=[coordinate['bounds'][0], upper])
        assert s.parameter_values(document_mapping(route.bind(point).parameters))[KEY] == k
        route.write(f'{name}/start.json', point)
        endpoint, report = f.fit(name, point, {}, [], route=route, penalty_rows=[])
        if endpoint is not None and report['status'] == 'converged':
            evaluated = document_mapping(route.bind(endpoint).parameters)
            assert s.parameter_values(evaluated)[KEY] == k and common(evaluated) == common(mapping) and laws(endpoint) == laws(reference)
            assert k_at(evaluated, target) <= upper
            endpoints.append((report['endpoint_replay_cost'], name, endpoint))
    assert endpoints, (side, 'no converged eight-coordinate endpoint')
    cost, chosen, point = min(endpoints)
    route.reduce(point)
    margin = [dict(T_K=row['T_K'], distance=row['k_no_gap']-k_at(point['parameters'],row['T_K'])) for row in critical]
    for cid in ('methyldiethanolamine', 'water'):
        def pure(p):
            return next(c for c in p['parameters']['components'] if c['component_id'] == cid)
        assert pure(point) == pure(starts[0])
    route.write('binary.json', dict(binary_check(route, point), margin=margin))
    route.write('split-record.json', r.read(OLD/'split-record.json'))
    started = time.monotonic()
    search = route.search(point)
    rows = route.result('search-0.json')
    assert len(rows) == 11824
    route.write('stability.json', dict(search, **witnesses(route, point, rows), seconds=time.monotonic()-started))
    route.write('selection.json', dict(chosen=chosen, cost=cost, k=k, run=str(route.out.relative_to(ROOT))))
    return route.result('data-rows.json')


def mdea_comparison(data):
    available = [{r['identity'] for r in rows if r['status'] == 'Available'} for rows in data]
    paired = set.intersection(*available)
    groups = {}
    for index, rows in enumerate(data):
        for row in rows:
            group, role = row['group'], row['role']
            labels = [group, f"{group} {row['outside_ranges'].get('MDEA-dissociation')}"]
            labels += [f'all pressures {role}'] if row['unit'] == 'Pa' else []
            labels += [f"Jakobsen {row['row']['ratio']}"] if group == 'Jakobsen' else []
            for label in labels:
                groups.setdefault(label, [[],[],[]])[index].append(row)
    def statistics(rows, ids):
        pairs = [(r['observed'], r['value']) for r in rows if r['identity'] in ids]
        return deviation_statistics(pairs, rows[0]['unit']) if pairs else {}
    f.write('mdea-comparison.json', {name: dict(total=list(map(len, rows)), original=[statistics(rr, ids) for rr,ids in zip(rows,available,strict=True)],
                                              paired=[statistics(rr, paired) for rr in rows]) for name,rows in groups.items()})


if __name__ == '__main__':
    f.OUT = OUT
    mea, mdea = s.parameter_mapping(paper.RECORD), r.read(RESULTS/'endpoint.json')
    cost, route, critical, upper = controls(mea, mdea)
    selected = profile(mea, cost)
    if selected.keys() == {'low', 'high'}:
        mdea_comparison([route.result('data-rows.json'), *(mdea_fit(side, s.parameter_values(selected[side]['mapping'])[KEY], mdea, route, critical, upper)
                                                          for side in ('low','high'))])
