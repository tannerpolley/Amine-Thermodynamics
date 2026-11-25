"""Expand the AMP pressure calibration and refit the #412 F2 slope families."""
from collections import Counter, defaultdict
import argparse
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from common import ROOT, fingerprints, save
from part_ii import Route, deviation_statistics, stable
from recall import DECLARATION, ENDPOINTS
from fit_412 import SLOPE, fixed_slope, reduced

ADDED = {'tong', 'hartono-2021-supplemental'}
LOADED = 'loaded-pressure'
ORIGINAL = ('main', 'slope-150')
Q2 = ROOT / 'analyses/round_3/results/q2.json'
Q7 = ROOT / 'analyses/round_3/results/q7-recall.json.gz'


class ExpandedPressure(Route):
    def bind(self, point):
        spec = super().bind(point)
        observations = spec.inputs['observations']
        fitted, outside = (observations[role] for role in ('fitted', 'comparisons'))
        added = [r for r in outside if r['group'] in ADDED]
        original = [r for r in fitted if r['group'] == LOADED]
        assert len(fitted) == 156 and len(original) == 47
        assert Counter(r['group'] for r in added) == {'tong': 40, 'hartono-2021-supplemental': 18}
        assert all(r['arguments']['form'] == 'log_ratio' and r['unit'] == 'Pa' for r in original + added)
        coefficient, = {r['weight'] for r in original}
        assert math.isclose(coefficient, 1 / (47 * .015**2), rel_tol=1e-13)
        for r in original + added:
            r.update(weight=coefficient * 47 / 105, role='fitted')
        fitted.extend(added)
        observations['comparisons'] = [r for r in outside if r['group'] not in ADDED]
        return spec


def scores(route, point, rows_archive):
    spec = route.bind(point)
    predictions = []
    groups = defaultdict(list)
    for role, rows in spec.inputs['observations'].items():
        if role not in ('fitted', 'comparisons'):
            continue
        for r in rows:
            p = spec.prediction(r)
            ref = rows_archive[r['identity']]
            key = (r['role'], r['group'], r['kind'], r['unit'])
            keys = [key, (*key, ref['T_K'])] if 'T_K' in ref else [key]
            for group in keys:
                groups[group].append((r, p))
            predictions.append(dict(identity=r['identity'], role=r['role'], group=r['group'], kind=r['kind'],
                                    unit=r['unit'], observed=r['arguments']['observed'], arguments=r['arguments'],
                                    weight=r['weight'], prediction=p))
    summaries = []
    for (role, group, kind, unit, *temperature), rows in groups.items():
        pairs = [(r['arguments']['observed'], p['value']) for r, p in rows if p['status'] == 'Available']
        summaries.append(dict(role=role, group=group, kind=kind, T_K=temperature[0] if temperature else None,
                              total=len(rows), unavailable=[r['identity'] for r, p in rows if p['status'] != 'Available'],
                              **(deviation_statistics(pairs, unit) if pairs else {'unit': unit})))
    return dict(rows=predictions, scores=summaries)


def fit(route, name, start_point):
    started = monotonic()
    point, report = reduced.fit(name, start_point, {}, [], route=route, penalty_rows=[])
    stages = [stable.read(p) for p in sorted((route.out / name).glob('stage-*/fit.json'))]
    replay_path = route.out / name / 'start-replay.json'
    save(f'A/{name}.json.gz', dict(point=point, starting_point=start_point, report=report, stages=stages,
         start_replay=stable.read(replay_path) if replay_path.is_file() else None,
         reason='Initial fitted replay unavailable' if report is None else None), start=started)
    return point, report


def calibrate(work):
    started = monotonic()
    endpoints = [ENDPOINTS / label / 'parameters.json' for label in ORIGINAL]
    free, fixed = map(stable.read, endpoints)
    archive = ENDPOINTS / 'main/data-rows.json'
    rows = {r['identity']: r for r in stable.read(archive)}
    assert len(rows) == 270
    before = Route(DECLARATION, work / 'original')
    after = ExpandedPressure(DECLARATION, work / 'expanded')
    bound = before.bind(free)
    expanded = after.bind(free)
    original_ids = {r['identity']: r for r in bound.inputs['observations']['fitted'] + bound.inputs['observations']['comparisons']}
    new_ids = {r['identity']: r for r in expanded.inputs['observations']['fitted'] + expanded.inputs['observations']['comparisons']}
    assert original_ids.keys() == new_ids.keys() == rows.keys()
    hot = {r['identity'] for r in stable.read(Q2)['rows']}
    crosswalk = [dict(r, old_role=original_ids[k]['role'], new_role=new_ids[k]['role'],
                     old_weight=original_ids[k]['weight'], new_weight=new_ids[k]['weight'], in_Q2=k in hot)
                 for k, r in rows.items()]
    assert Counter((r['group'], r['in_Q2']) for r in crosswalk if r['group'] == 'tong') == {('tong', True): 23, ('tong', False): 17}
    assert Counter(r['group'] for r in crosswalk if r['in_Q2']) == {'tong': 23, 'tong-baseline': 2, 'hartono-2021-supplemental': 18}
    save('A/crosswalk.json.gz', dict(rows=crosswalk, inputs=fingerprints(DECLARATION, bound.path, archive, Q2, Q7, *endpoints)), start=started)

    for label, point in zip(ORIGINAL, (free, fixed), strict=True):
        replay, ok, cost = before.replay(point)
        ref = {r['identity']: r for r in stable.read(ENDPOINTS / label / 'data-rows.json') if r['role'] == 'fitted'}
        difference = max(abs(r['residual'] - ref[r['identity']]['residual']) for r in replay)
        save(f'A/original-{label}.json.gz', dict(replay=replay, available=ok, cost=cost,
             maximum_retained_residual_difference=difference, reproduced=ok and len(replay) == 156 and difference <= 1e-10,
             original=scores(before, point, rows), expanded=scores(after, point, rows)))

    # The opposite family maps through the same bounded physical slope coordinate.
    slope = next(q for q in free['coordinates'] if q['identity'] == 'AMPH-water-slope')
    promoted = dict(fixed, coordinates=[*fixed['coordinates'], dict(slope, origin=-150.)])
    for label, starts in (('free', (free, promoted)), ('fixed', (fixed, fixed_slope(free, -150)))):
        candidates = []
        for name, start in zip(('incumbent', 'opposite'), starts, strict=True):
            point, report = fit(after, f'expanded-{label}-{name}', start)
            if point is not None and report and report.get('endpoint_replay_available'):
                candidates.append((report['endpoint_replay_cost'], name, point, report['status']))
        if candidates:
            cost, name, point, status = min(candidates, key=lambda c: c[0])
            save(f'A/expanded-{label}.json.gz', dict(cost=cost, start=name, status=status, point=point,
                 slope_K=stable.s.parameter_values(point['parameters'])[SLOPE],
                 original=scores(before, point, rows), expanded=scores(after, point, rows)))
    save('A/calibration.json', dict(projection_minutes=[5, 8]), start=started)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if args.work:
        calibrate(args.work)
    else:
        with TemporaryDirectory() as directory:
            calibrate(Path(directory))
