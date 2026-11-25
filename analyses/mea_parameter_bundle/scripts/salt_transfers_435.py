"""Refit the receiver declarations using the qualifying #435 MEA laws."""
# ruff: noqa: E402 -- use the existing transfer analysis owners.
import copy
import gzip
import sys
from time import monotonic

from salt_anchored_435 import ANALYSES, OUT, f, r, setup, salt, timed

sys.path[:0] = [str(ANALYSES / name) for name in ('dea_transfer', 'round_5', 'round_3')]
from part_ii import Route, SHA
from classify_descents import classify
import f2_carbamate as dea
import bounded_binary_411 as mdea
import coexistence_421
import amp
import amp_stability
import objective

WORK = r.ROOT / 'build/salt-anchored-435'
SHARED = OUT / 'shared-parameters.json'
DEABASE = dea.AN / 'results/refit-413'


def export():
    chosen = r.read(OUT / 'MEA/selection.json')['chosen']
    if chosen is None:
        raise ValueError('No qualifying same-declaration MEA endpoint')
    path = OUT / 'MEA' / chosen['label'] / 'parameters.json'
    endpoint = r.s.parameter_mapping(path)
    pairs = [p for p in endpoint['pairs'] if {p['component_id_a'], p['component_id_b']}
             in ({salt.W, salt.HCO3}, {salt.W, salt.CO3})]
    assert len(pairs) == 2
    values = r.s.parameter_values(endpoint)
    carbamate = dict(sigma=values['component/carbamate-anion/segment_diameter'],
                      epsilon=values['component/carbamate-anion/dispersion_energy_over_k'])
    f.write(SHARED.name, dict(wheel_sha256=SHA, parameter_sha256=r.s.sha256(path), water_ion_pairs=pairs,
                             carbamate=carbamate, source=path.relative_to(r.ROOT).as_posix()))


def route(owner, declaration, name, cls=Route):
    return cls(declaration, WORK / owner / name, shared_values=(SHARED, r.s.sha256(SHARED)))


def substitute(point, *, carbamate=False):
    mapped = copy.deepcopy(point)
    shared = r.read(SHARED)
    for pair in shared['water_ion_pairs']:
        node, = [c for c in pair['coefficients'] if c['family'] == 'k_ij']
        salt.set_pair(mapped['parameters'], pair['component_id_a'], pair['component_id_b'], node)
    if carbamate:
        dea.carbamate(mapped['parameters'], shared['carbamate'])
    return mapped


def retain(owner, name, run):
    out = ANALYSES / owner / 'results/salt-anchored-435' / name
    for path in sorted(p for p in run.out.rglob('*') if p.name.endswith(('.json', '.json.gz', '.csv'))):
        destination = out / (path.relative_to(run.out).as_posix() + ('' if path.suffix == '.gz' else '.gz'))
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        destination.write_bytes(data if path.suffix == '.gz' else gzip.compress(data, mtime=0))


def score(run, point, case):
    run.reduce(point)
    run.uncertainty(point)
    import objective_weights_420 as information
    spec, rows, ev = run.differentiate_endpoint(point)
    information.OUT = r.OUT = run.out
    information.information(case, spec, rows, point['coordinates'], ev.residual_optimizer_gradient,
                            run.result('conditional-uncertainty.json'), r.COMMIT)


def data_fit(run, label, point):
    path = f'{label}/outcome.json'
    if (run.out / path).is_file():
        previous = run.result(path)
        endpoint, report = previous['point'], previous['report']
    else:
        started = monotonic()
        endpoint, report = f.fit(label, point, {}, [], route=run, penalty_rows=[])
        run.write(path, dict(point=endpoint, report=report, seconds=monotonic()-started))
    if endpoint is not None and report['status'] == 'converged':
        return report['endpoint_replay_cost'], label, endpoint
    return None


def search(run, point, states, *, trials=None):
    rows, seconds = timed(run.grid, point, states, trial_set=trials)
    aliases = {x['key']: x['same_calculation_as'] for x in rows if 'same_calculation_as' in x}
    detail = classify(run, point, [x for x in rows if x['key'] not in aliases], states)
    confirmed = [x['key'] for x in detail if any(y['confirmed'] for y in x['attempts'])]
    run.write('search-outcome.json', dict(seconds=seconds, tally=r.tally(rows), aliases=aliases, confirmed=confirmed,
                                         classifications=detail, parameter_fingerprint=r.s.parameter_fingerprint(point['parameters']),
                                         bubble_refusals=[x['key'] for x in rows if (x.get('message') or '').startswith('pressure reference')]))
    return rows


def dea_fit():
    owner = 'dea_transfer'
    run = route(owner, dea.OLD / 'f2-carbamate-413-route.json', 'campaign')
    started = monotonic()
    old = r.read(DEABASE / 'selection.json')['chosen']
    starts = [substitute(run.start(ref), carbamate=True) for ref in run.config['starts']]
    candidates = [f.candidate(f'start-{i}', start, {}, [], {}, route=run) for i, start in enumerate(starts)]
    eligible = [c for c in candidates if c is not None and c['optimizer_converged']]
    chosen = f.lowest_cost(eligible)
    run.write('selection.json', dict(candidates=candidates, chosen=chosen, prior_cost=old['cost'],
                                     ties=[x['name'] for x in eligible if f.costs_tied(x['cost'], chosen['cost'], run.controls['function_tolerance'])],
                                     seconds=monotonic()-started, projected_minutes=[8, 11]))
    if chosen:
        score(run, chosen['parameters'], 'DEA')
        run.curves(chosen['parameters'])
    retain(owner, 'campaign', run)


def mdea_fit():
    owner = 'mdea_mea_workflow'
    run = route(owner, mdea.DECLARATION, 'campaign')
    started = monotonic()
    bound = run.config['k_bound']
    T = bound['temperature_K']
    upper = next(row['k_no_gap'] for row in run.load(bound['critical'])['rows'] if row['T_K'] == T) - bound['margin']
    assert upper == -0.06711345443725586
    options = []
    for i, ref in enumerate(run.config['starts']):
        original = run.load(ref)
        point = substitute(original)
        assert mdea.law(point['parameters']) == mdea.law(original['parameters'])
        value = min(mdea.k_at(point['parameters'], T), upper)
        point['parameters'] = mdea.rereference(point['parameters'], T, value)
        q = next(q for q in point['coordinates'] if q['identity'].startswith(mdea.PAIR + '/a0'))
        q.update(origin=value, bounds=[q['bounds'][0], upper])
        assert len(run.bind(point).inputs['observations']['fitted']) == 281
        result = data_fit(run, f'fit-{i}', point)
        if result:
            options.append(result)
        retain(owner, 'campaign', run)
    if not options:
        return
    cost, label, point = min(options)
    assert mdea.k_at(point['parameters'], T) <= upper
    binary = mdea.binary_check(run, point)
    run.write('selection.json', dict(cost=cost, start=label, point=point, binary=binary, wall_s=monotonic()-started,
                                     projected_fit_s=891.8))
    prior = r.read(mdea.RESULTS / 'endpoint.json')
    score(run, point, 'MDEA')
    control = objective.ObservableWeights(mdea.DECLARATION, WORK / owner / 'normalized', 'MDEA')
    run.write('cross-score.json', dict(prior_primary=Route(mdea.DECLARATION, WORK / owner / 'prior').replay(prior)[2], new_primary=cost,
                                      prior_equalized=control.replay(prior)[2], new_equalized=control.replay(point)[2],
                                      prior_fixed_states=objective.q3_checks(control, prior), new_fixed_states=objective.q3_checks(run, point)))
    spec = run.bind(point)
    states = run.states(spec)
    assert len(states) == 11824
    bank = r.read(mdea.OLD / 'split-record.json')
    trials = bank['trials'] + bank.get('supplied_trials', [])
    pilot = route(owner, mdea.DECLARATION, 'timing-probe')
    subset = states[::47]
    sample, seconds = timed(pilot.grid, point, subset, trial_set=trials)
    pilot.write('projection.json', dict(seconds=seconds, states=len(sample), unique=sum('same_calculation_as' not in x for x in sample),
                                       projected_seconds=seconds * len(states) / len(sample)))
    retain(owner, 'timing-probe', pilot)
    search(run, point, states, trials=trials)
    coexistence_421.fixed(run, spec)
    retain(owner, 'campaign', run)


def amp_fit():
    owner = 'amp_transfer'
    free, fixed = [r.read(amp.ENDPOINTS / label / 'parameters.json') for label in amp.ORIGINAL]
    slope = next(q for q in free['coordinates'] if q['identity'] == 'AMPH-water-slope')
    promoted = dict(fixed, coordinates=[*fixed['coordinates'], dict(slope, origin=-150.)])
    for family, starts in (('free', (free, promoted)), ('fixed', (fixed, amp.fixed_slope(free, -150.)))):
        run = route(owner, amp.DECLARATION, family, amp.ExpandedPressure)
        options = []
        for label, source in zip(('incumbent', 'opposite'), starts, strict=True):
            start = substitute(source)
            assert len(run.bind(start).inputs['observations']['fitted']) == 214
            result = data_fit(run, label, start)
            if result:
                options.append(result)
            retain(owner, family, run)
        if not options:
            continue
        cost, label, point = min(options)
        prior = r.read(ANALYSES / f'round_5/results/A/expanded-{family}.json.gz')
        run.write('selection.json', dict(cost=cost, start=label, point=point, prior_expanded_cost=prior['cost'],
                                         slope_K=r.s.parameter_values(point['parameters'])[amp.SLOPE]))
        archive = {x['identity']: x for x in r.read(amp.ENDPOINTS / 'main/data-rows.json')}
        run.write('paired-expanded-scores.json', dict(new=amp.scores(run, point, archive), prior=prior['expanded']))
        score(run, point, 'AMP')
        original = Route(amp.DECLARATION, WORK / owner / 'original')
        states = original.states(original.bind(free))
        assert len(states) == 666
        for protocol in ('native', 'supplied'):
            phase = route(owner, amp.DECLARATION, f'{family}/{protocol}')
            bank = amp_stability.trial_bank(phase) if protocol == 'supplied' else {'trials': []}
            if protocol == 'supplied':
                assert amp_stability.bank_hash(bank) == amp_stability.TRIAL_SHA
            search(phase, point, states, trials=bank['trials'] + bank.get('supplied_trials', []))
            retain(owner, f'{family}/{protocol}', phase)
        retain(owner, family, run)


if __name__ == '__main__':
    setup()
    {'export': export, 'DEA': dea_fit, 'MDEA': mdea_fit, 'AMP': amp_fit}[sys.argv[1]]()
