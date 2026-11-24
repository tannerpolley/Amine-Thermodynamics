"""Run the #398 DEA campaign and check its retained evidence."""
from pathlib import Path
import sys
from time import monotonic

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from part_ii import Route, ROOT, SHARED
from MEA.common.analysis_io import file_sha256 as digest
from stable_refit_255 import read

AN = Path(__file__).resolve().parent
HISTORY = AN / 'results/retransfer-346'
INPUT = AN / 'inputs/part-ii-346'
LIMIT = 1e-8  # #346 and #255 reproducibility limit.


def replay_errors(pairs, cost, reference_cost):
    return dict(max_relative_prediction_error=max((abs(value / ref - 1) for value, ref in pairs), default=None),
                relative_cost_error=abs(cost / reference_cost - 1) if cost is not None else None,
                cost=cost, reference_cost=reference_cost)


def error(rows, reference, cost, reference_cost):
    assert len(rows) == len(reference) == 80
    assert all(a['identity'] == b['identity'] and a['status'] == 'Available'
               and a['requested_tolerance_met'] for a, b in zip(rows, reference, strict=True))
    return replay_errors(((a['value'], b['value']) for a, b in zip(rows, reference, strict=True)),
                         cost, reference_cost)


def check_shared(point, adopted, shared, interval=None):
    species = {'water', 'carbon-dioxide', 'hydronium-cation', 'hydroxide-anion',
               'bicarbonate-anion', 'carbonate-anion'}
    for section, keys in [('components', ('component_id',)), ('pairs', ('component_id_a', 'component_id_b'))]:
        select = lambda data: {tuple(row[key] for key in keys): row for row in data[section]
                               if all(row[key] in species for key in keys)}
        assert select(point['parameters']) == select(adopted)
    reactions = {law['name']: law for law in point['reactions']['aqueous']}
    for law in shared['reactions']:
        expected = law['correlation'] if interval is None else dict(law['correlation'], temperature_min=interval[0], temperature_max=interval[1])
        assert reactions[law['name']]['correlation'] == expected and reactions[law['name']]['reference'] == law['reference']


def retained_replay(route, baseline):
    previous = HISTORY / 'f2-current'
    rows, available, cost = route.replay(baseline)
    reference = read(previous / 'start-0/unpenalized/stage-0/replay.json')
    assert available, 'The retained #346 endpoint replay is unavailable'
    replay = error(rows, reference, cost, read(previous / 'selection.json')['chosen']['cost'])
    assert max(replay[k] for k in ('max_relative_prediction_error', 'relative_cost_error')) <= LIMIT
    return dict(replay, limit=LIMIT, rows=len(rows))


def main(out):
    started = monotonic()
    assert not (out/'selection.json').exists(), 'Choose a new output directory for a completed campaign'
    route = Route(INPUT / 'route-current.json', out)
    shared = read(SHARED)
    adopted = ROOT / 'analyses/solvent_specification_mea/inputs/endpoint.json'
    for ref in route.config['starts']:
        check_shared(route.start(ref), read(adopted), shared)
    baseline = read(HISTORY / 'f2-current/endpoint-completed-365.json')
    replay = retained_replay(route, baseline)
    registry = route.load(route.config['split_record'])
    assert not registry['trials'] and not registry.get('supplied_trials')
    baseline_states = route.states(route.bind(baseline))
    assert len(baseline_states) == 1271 and sum(s['key'].startswith('grid:') for s in baseline_states) == 936
    checks = dict(retained_replay=replay,
                  shared_inputs=dict(adopted_sha256=digest(adopted), shared_values_sha256=digest(SHARED), both_starts=True),
                  earlier_split_compositions=len(registry['trials']))
    route.write('checks.json', checks)

    grid, timings = route.grid, {}
    def timed_grid(point, states, **kwargs):
        count, begin = len(list(out.glob('search-*.json'))), monotonic()
        result = grid(point, states, **kwargs)
        if len(list(out.glob('search-*.json'))) > count:
            timings[f'search-{count}'] = monotonic() - begin
            print(f'search-{count}: {timings[f"search-{count}"]:.1f} s', flush=True)
        return result
    route.grid = timed_grid
    route.campaign()
    timings['preflight_and_campaign'] = monotonic() - started
    route.write('timings.json', timings)
    report(route, adopted, shared)


def report(route, adopted, shared):
    chosen = route.result('selection.json')['chosen']
    if chosen is None:
        return
    begin = monotonic()
    checks, timings = route.result('checks.json'), route.result('timings.json')
    point = chosen['parameters']
    check_shared(point, read(adopted), shared, route.config['calculation_interval_K'])
    values, available, cost = route.replay(point)
    native = chosen['optimizer_report']
    endpoint = error(values, [dict(r, value=p) for r, p in zip(values, native['predictions'][:len(values)], strict=True)],
                     cost, native['data_cost'])
    assert available and max(endpoint[k] for k in ('max_relative_prediction_error', 'relative_cost_error')) <= LIMIT
    checks['endpoint'] = dict(endpoint, limit=LIMIT, selected_shared_inputs_equal=True)
    route.reduce(point)
    route.uncertainty(point)
    route.curves(point)
    rows, curves = route.result('data-rows.json'), route.result('curve-data.json')
    assert len(rows) == 299 and len(curves) == 750
    reactive = {'R1', 'R2', 'R3', 'DEA-dissociation', 'carbamate-hydrolysis'}
    for row in rows + curves:
        used = set() if row['group'] in ('Cai', 'Horstmann') else reactive
        expected = {name: not lo <= row['T_K'] <= hi if name in used else 'reaction not used'
                    for name, (lo, hi) in route.config['reaction_ranges_K'].items()}
        assert row['outside_ranges'] == expected, row['identity']
    checks['range_marks'] = dict(observations=len(rows), curve_points=len(curves), all_matched=True)
    route.write('checks.json', checks)
    timings['endpoint_and_reporting_calculations'] = monotonic() - begin
    route.write('timings.json', timings)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
