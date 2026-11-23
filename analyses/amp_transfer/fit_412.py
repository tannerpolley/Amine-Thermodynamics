"""#412 AMP fits on the F2 carbamate inputs (owner decision 2026-11-23): the F2 reference refit of #404's main fit,
the AMPH+-water slope profile and the penalty on descending states, each searched for liquid splits."""
import os
import sys
import time

os.environ['AMP_CARBAMATE_FIT'], os.environ['AMP_404_RUN'] = 'F2', '404-f2-412'
from part_ii import Route, deviation_statistics, stable
from refit_404 import (AMP, DECLARATIONS, PUBLISHED, RUN as REFERENCE, check_fixed, record_f0_source, replace_fixed,
                       run_fits, source_values, trial_bank)
import classify_descents
import reduced_refit_338 as reduced

RUN = AMP/'results/runs'
SLOPE = 'pair/protonated-aminomethylpropanol/water/k_ij/reciprocal_temperature_slope'


def reference():
    """#404's main fit with only the two carbamate inputs moved to F2: same declaration, data, starts, trial bank and search."""
    published = stable.read(PUBLISHED/'data-rows.json')
    source = source_values()
    started = time.monotonic()
    checks = run_fits('main', 'AMP-05e94210.json', float(source[2]['value']), source, {r['identity']: r for r in published})
    route = Route(DECLARATIONS/'AMP-05e94210.json', REFERENCE/'main')
    fitted_s = time.monotonic()-started
    for entry in route.result('fits.json'):
        classify_descents.write_classification(route, entry['endpoint'], f'search-{entry["start"]}.json', f'phase-classification-{entry["start"]}.json')
    route.write('timing.json', dict(fits_and_searches_s=fitted_s, total_s=time.monotonic()-started, workers=route.workers, endpoint_replays=checks))


def reference_point():
    route = Route(DECLARATIONS/'AMP-05e94210.json', REFERENCE/'main')
    selected = route.result('selection.json')['selected']
    return next(e['endpoint'] for e in route.result('fits.json') if e['start']==selected)


def fixed_slope(point, value):
    """Drop the slope coordinate and set its value; the other eight coordinates stay free."""
    coordinates = [q for q in point['coordinates'] if q.get('identity')!='AMPH-water-slope']
    assert len(coordinates)==len(point['coordinates'])-1==8
    return dict(point, coordinates=coordinates,
                parameters=stable.s.with_parameter_values(point['parameters'], {SLOPE: float(value)}))


def score(route, point):
    spec = route.bind(point)
    rows = [(role, record, spec.prediction(record)) for role in ('fitted','comparisons') for record in spec.inputs['observations'][role]]
    assert all(p['status']=='Available' for _, r, p in rows if r['unit']=='Pa'), 'unavailable pressure row'
    def aard(keep):
        pairs = [(r['arguments']['observed'], p['value']) for role, r, p in rows if r['unit']=='Pa' and keep(role, r)]
        return dict(rows=len(pairs), AARD_percent=deviation_statistics(pairs,'Pa')['AARD_percent'])
    out = dict(loaded_fitted=aard(lambda role, r: role=='fitted' and r['group']=='loaded-pressure'),
               all_fitted=aard(lambda role, r: role=='fitted'),
               not_fitted=aard(lambda role, r: role!='fitted'))
    assert (out['loaded_fitted']['rows'], out['all_fitted']['rows'], out['not_fitted']['rows'])==(47, 73, 114)
    return out


def native(route, point):
    """Native search on all 666 states (no supplied trials): the screen the probes showed reproduces #404's 92 descents."""
    started = time.monotonic()
    rows = route.grid(point, route.states(route.bind(point)), trial_set=[])
    tally = stable.tally(rows)
    spec = route.bind(point)
    by_key = {s['key']: s for s in route.states(spec)}
    temps = sorted({route.temperature(spec, by_key[r['key']]) for r in rows if stable.descent(r)})
    keys = sorted(r['key'] for r in rows if stable.descent(r))
    return dict(states=tally['states'], available=tally['available'], descent=tally['descent'], descent_keys=keys,
                measured_descent=[k for k in keys if not k.startswith('grid:')],
                minimum_tau=tally['minimum_tau'], descent_temperatures_K=temps, seconds=time.monotonic()-started)


def refit(route, name, start, fixed, scale=None, rows=()):
    started = time.monotonic()
    endpoint, report = reduced.fit(name, start, {}, [], scale=scale, route=route, penalty_rows=list(rows))
    assert endpoint is not None and report['status']=='converged', (name, report and report['status'])
    check_fixed(endpoint, fixed)
    return endpoint, dict(cost=report['endpoint_replay_cost'], iterations=report['iterations'], scale=scale, penalty_rows=len(rows),
                          residual_evaluations=report['residual_evaluations'], seconds=time.monotonic()-started,
                          workers=route.workers)


def scan(slopes):
    source = source_values()
    fixed = {r['identity']: float(r['value']) for r in source[:2]}
    base = reference_point()
    summary = Route(DECLARATIONS/'AMP-05e94210.json', RUN/'412-f2-scan')
    found = summary.result('scan.json') if (summary.out/'scan.json').exists() else {}
    for value in slopes:
        route = Route(DECLARATIONS/'AMP-05e94210.json', RUN/f'412-f2-slope{value}')
        route.check_run_output()
        endpoint, fit = refit(route, 'warm', fixed_slope(base, value), fixed)
        found[str(value)] = dict(slope_K=value, fit=fit, native=native(route, endpoint), score=score(route, endpoint))
        summary.write('scan.json', found)
        print(value, found[str(value)], flush=True)


def confirm(value):
    """Second declared start, full #404 search with the 7301-trial bank, uncertainty and scores for one slope."""
    source = source_values()
    fixed = {r['identity']: float(r['value']) for r in source[:2]}
    route = Route(DECLARATIONS/'AMP-05e94210.json', RUN/f'412-f2-slope{value}')
    warm = route.result('warm/stage-0/parameters.json')
    start = record_f0_source(replace_fixed(route.start(route.config['starts'][1]), fixed), source)
    cold, fit = refit(route, 'start-1', fixed_slope(start, value), fixed)
    chosen = min((warm, route.replay(warm)[2]), (cold, fit['cost']), key=lambda pair: pair[1])[0]
    if not (route.out/'split-record.json').exists():
        route.write('split-record.json', trial_bank(route))
    started = time.monotonic()
    searched = route.search(chosen)
    record = max(route.out.glob('search-*.json'), key=lambda p: int(p.stem.split('-')[-1])).name
    if searched['grid']['descent']:
        classify_descents.write_classification(route, chosen, record, 'phase-classification.json')
    route.uncertainty(chosen)
    route.reduce(chosen)
    route.curves(chosen)
    route.write('parameters.json', chosen)
    result = dict(slope_K=value, start_1=fit, warm_cost=route.replay(warm)[2], selected_cost=route.replay(chosen)[2],
                  full_search={k: searched['grid'][k] for k in ('states','available','descent','minimum_tau','supplied_minimum_tpd','liquid_liquid_splits')},
                  stable=searched['stable'], search_record=record, search_seconds=time.monotonic()-started, score=score(route, chosen))
    route.write('confirmation.json', result)
    print('confirm', result, flush=True)


def penalize(scales):
    """Penalty on the compressed copies of the states that descend, all 9 coordinates free, warm-started from #404.

    Each stage adds the states the full native screen still finds; the screen of all 666 states, not the
    penalty rows, decides acceptance. No retreat: the stage endpoint itself is the candidate."""
    source = source_values()
    fixed = {r['identity']: float(r['value']) for r in source[:2]}
    route = Route(DECLARATIONS/'AMP-05e94210.json', RUN/'412-f2-penalty')
    route.check_run_output()
    point = reference_point()
    screen = native(route, point)
    active, stages = set(screen['descent_keys']), []
    for i, scale in enumerate(scales):
        spec = route.bind(point)
        rows = route.penalty_states([s for s in route.states(spec) if s['key'] in active], spec)
        assert not route.penalty_unavailable
        point, fit = refit(route, f'penalized-{i}', point, fixed, scale, rows)
        screen = native(route, point)
        stages.append(dict(fit=fit, penalized_states=sorted(active), native=screen, score=score(route, point)))
        route.write('stages.json', stages)
        print('stage', i, scale, fit['cost'], screen['descent'], screen['measured_descent'], round(fit['seconds']), flush=True)
        if not screen['descent']:
            route.write('parameters.json', point)
            break
        active |= set(screen['descent_keys'])


def retain(value):
    """Write the F2 reference (against #404) and the fixed-slope set (against the F2 reference) to the candidate folder."""
    import csv
    import retain_404
    out = AMP/'results/retransfer-412-f2-05e94210'
    retain_404.OUT = out
    source = source_values()
    statistics = retain_404.retain_case('main', 'main', AMP/'results/retransfer-404-05e94210/main/data-rows.json', source)
    for row in statistics:
        row['case'] = 'F2 main against #404 main'
    route = Route(DECLARATIONS/'AMP-05e94210.json', RUN/f'412-f2-slope{value}')
    confirmation = route.result('confirmation.json')
    label = f'slope{value:g}'
    retain_404.write(out/label/'parameters.json', record_f0_source(route.result('parameters.json'), source))
    for name in ('confirmation.json', 'conditional-uncertainty.json'):
        retain_404.write(out/label/name, route.result(name))
    retain_404.write(out/label/f"{confirmation['search_record']}.gz", route.result(confirmation['search_record']))
    if (route.out/'phase-classification.json').exists():
        retain_404.write(out/label/'phase-classification.json.gz', route.result('phase-classification.json'))
    retain_404.retain_curves(label, route.out/'curve-data.json')
    rows = retain_404.compare(label, route.out/'data-rows.json', out/'main/data-rows.json')
    for row in rows:
        row['case'] = f'Slope {value:g} K against F2 main'
    statistics += rows
    for case in ('f0', 'f2'):
        retain_404.write(out/f'diagnosis/{case}-probes.json', stable.read(RUN/f'412-{case}-probes/probes.json'))
        scan = stable.read(RUN/f'412-{case}-scan/scan.json')
        for entry in scan.values():
            entry['native'].pop('descent_keys', None)
        retain_404.write(out/f'diagnosis/{case}-scan.json', scan)
    retain_404.write(out/'reference-timing.json', stable.read(REFERENCE/'main/timing.json'))
    retain_404.write(out/'source.json', dict(coefficients=source, path=retain_404.FITS.relative_to(retain_404.ROOT).as_posix(),
                                              source_sha256=retain_404.FITS_SHA, input_checks=stable.read(REFERENCE/'main/input-checks.json')))
    with (out/'same-row-deviations.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(statistics[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(statistics)


if __name__ == '__main__':
    if sys.argv[1]=='retain':
        retain(float(sys.argv[2]))
    elif sys.argv[1]=='reference':
        reference()
    elif sys.argv[1]=='penalize':
        penalize([float(v) for v in sys.argv[2:]])
    elif sys.argv[1]=='confirm':
        confirm(float(sys.argv[2]))
    else:
        scan([float(v) for v in sys.argv[1:]])
