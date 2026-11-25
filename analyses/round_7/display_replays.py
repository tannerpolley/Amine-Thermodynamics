"""Replay the adopted round-7 endpoints for the manuscript displays."""
# ruff: noqa: E402
import argparse
import math
from time import monotonic

from calculations import MDEA, MDEAWeights, OUT, SALT, WORK, Route, a, r, save, transfer
from receivers import AMP, DEA, verify_binding
from part_ii import SHA, eq
from phases import fixed
from amp_stability import AMP_REFERENCE
from binary_tpd_421 import PRESSURES, binary_model, bracket_onset, k_at

DEST = OUT / 'display-replays'
WORK = WORK / 'display-replays'
MDEA_POINT = OUT / 'C/salt/selection.json.gz'


def endpoint(path):
    return r.read(path)['selected'][2]


def retain(name, started, sources, **result):
    save(DEST / f'{name}.json.gz', dict(
        wheel_sha256=SHA, engine_commit=r.COMMIT, seconds=monotonic()-started,
        sources={str(path.relative_to(r.ROOT)): r.s.sha256(path) for path in sources},
        **result))


def dea_curves():
    start = monotonic()
    source = OUT / 'F/selection.json.gz'
    point = endpoint(source)
    route = Route(DEA, WORK / 'DEA')
    verify_binding(route, point, amp=False)
    reference = route.config['curve_rows']
    grid = (route.path.parent / reference['path']).resolve()
    declarations = [row for row in route.load(reference) if row['observation']['group']
                    in ('Lawson', 'Lawson-394K', 'SeoHong', 'Lal')]
    assert len(declarations) == 275
    pilot, rest = declarations[::25], [q for i, q in enumerate(declarations) if i % 25]
    tick = monotonic()
    rows = route.curves(point, pilot)
    projected = (monotonic()-tick)*len(declarations)/len(pilot)
    if projected <= 1200:
        rows.extend(route.curves(point, rest))
    rows.sort(key=lambda q: (q['curve'], q['loading']))
    retain('dea-pressure-curves', start, [source, grid, route.path], rows=rows,
           projected_seconds=projected, requested=len(declarations))


def mdea_route(cls=Route):
    return cls(MDEA.DECLARATION, WORK / cls.__name__,
               shared_values=(transfer.SHARED, r.s.sha256(transfer.SHARED)))


def mdea_errors():
    from objective_weights_420 import information_reduction
    from part_ii import np

    start = monotonic()
    point = endpoint(MDEA_POINT)
    route = mdea_route(MDEAWeights)
    sources = [MDEA_POINT, route.path, transfer.SHARED]
    try:
        spec, rows, evaluation = route.uncertainty(point)
    except (AssertionError, RuntimeError, ValueError, np.linalg.LinAlgError) as error:
        rows, available, cost = route.replay(point)
        retain('mdea-standard-errors', start, sources, refusal=f'{type(error).__name__}: {error}',
               rows=rows, replay_available=available, cost=cost, covariance_available=False)
        return

    uncertainty = route.result('conditional-uncertainty.json')
    weights = spec.inputs['observations']['fitted']
    jacobian = spec.whiten(np.array(evaluation.residual_optimizer_gradient).reshape(len(rows), -1))
    residuals = spec.whiten(np.array([q['residual'] for q in rows]))
    information, _ = information_reduction('MDEA', weights, rows, point['coordinates'],
                                           residuals, jacobian, uncertainty, r.COMMIT)
    comparison = OUT / 'C/salt/refit.json.gz'
    expected = r.read(comparison)['objective']['rms']
    assert math.isclose(information['stage_variance'], expected['stage_variance'], rel_tol=1e-10)
    assert math.isclose(information['variance'], expected['all_variance'], rel_tol=1e-10)
    assert information['p'] == expected['rank']
    errors = {k: v*information['SE_multiplier'] for k, v in uncertainty['conditional_standard_error'].items()}
    retain('mdea-standard-errors', start, [*sources, comparison], uncertainty=uncertainty,
           information=information, responsive_standard_error=errors, covariance_available=True,
           convention='Analytical residual Jacobian, weighted once, in physical coordinates. '
                      'Hold active bounds fixed. Scale (J^T J)^-1 by responsive-row RSS / (n - rank). '
                      'Omit pure-water Kim rows from the variance estimate.')


def mdea_onset():
    start = monotonic()
    mapping = endpoint(MDEA_POINT)['parameters']
    prior = SALT / 'binary-onset.json'
    model = binary_model(mapping)
    old = r.read(SALT / 'selection.json.gz')['point']['parameters']
    assert all(next(q for q in mapping['components'] if q['component_id']==cid) ==
               next(q for q in old['components'] if q['component_id']==cid)
               for cid in ('water', 'methyldiethanolamine'))
    pressures = {}
    for P in PRESSURES:
        rows, brackets = bracket_onset(model, P)
        pressures[str(int(P))] = dict(rows=list(rows.values()), brackets=brackets)
        retain('mdea-binary-onset', start, [MDEA_POINT, prior], pressures=pressures,
               k_at_423_K=k_at(mapping, 423.), temperature_scope_K=[422.04, 430.])


def kuranov_72():
    start = monotonic()
    source = OUT / 'H/kuranov-82nd.json'
    row = r.read(source)['row']
    assert row['source_row'] == 72
    route = mdea_route()
    spec = route.bind(endpoint(MDEA_POINT))
    comparison = next(q for q in spec.inputs['observations']['comparisons'] if q['group']=='Kuranov-413K')
    dataset = next(d for d in spec.spec['datasets'] if d['name']=='outside-fit-Kuranov-413K')
    key = 'kuranov:72'
    state = dict(T=row['T'], P=row['p_exp'], water=1/.01801528/row['m_mdea'],
                 alpha=row['alpha'], observed=row['p_exp'], scale=1.)
    spec.problems[key] = spec.problem(dataset['template'], state)
    args = spec.bind(dataset['arguments'], state)
    assert args == row['salt_anchored']['basis']['arguments']
    prediction = spec.prediction(dict(comparison, identity=key, problem=key, row={'source_row': '72'},
                                      arguments=args, group='Kuranov-393K', role='not fitted',
                                      basis=dict(comparison['basis'], arguments=args, template=dataset['template'])))
    retain('kuranov-row-72', start, [source, MDEA_POINT, route.path, transfer.SHARED],
           prediction=prediction, state=state)


def amp_common_pressure():
    start = monotonic()
    historical = OUT.parents[1] / 'amp_transfer/results/salt-anchored-435/common-pressure.json'
    prior = r.read(historical)
    reference = r.read(AMP_REFERENCE)
    pressure = prior['common_Pa']
    stock = {c: n for c, n in zip(reference['species'], reference['feed_mol'], strict=True)
             if n and c != 'carbon-dioxide'}
    state = dict(T=reference['T_K'], stock=stock, a=reference['loading'])
    paths = [OUT / f'AMP/{family}/selection.json.gz' for family in ('free', 'fixed')]
    results = {}
    for family, path in zip(('free', 'fixed'), paths, strict=True):
        point = endpoint(path)
        route = Route(AMP.DECLARATION, WORK / 'AMP' / family)
        verify_binding(route, point, amp=True)
        spec = route.bind(point)
        item = route.stability_row(spec, state, 1.)
        bubble = eq.solve_equilibrium(spec.model, item.pressure_reference)
        outcome = dict(bubble_Pa=bubble.pressure if bubble.requested_tolerance_met else None,
                       bubble_tolerance_met=bubble.requested_tolerance_met, bubble_status=bubble.message)
        try:
            outcome['fixed'] = fixed(route, spec, state, pressure, dict(pair=reference['split']))
        except (ValueError, RuntimeError, AssertionError) as error:
            outcome['refusal'] = f'{type(error).__name__}: {error}'
        results[family] = outcome
        retain('amp-common-pressure', start, [historical, AMP_REFERENCE, AMP.DECLARATION, *paths],
               state=state, common_Pa=pressure, outcomes=results)


def mea_heat():
    from stripper_temperature_409 import KIM2014, VINJARAPU2024, replay

    start = monotonic()
    source = OUT / 'E/F4/parameters.json'
    evidence = a.OUT / 'MEA/evidence/F4'
    directory = WORK / 'MEA-heat'
    producer = r.B / 'scripts/kim2007_heat_pathways.py'
    replay(r.ROOT, source, r.s.sha256(source), evidence, directory, control=False,
           producer_sha=r.s.sha256(producer))
    raw = r.read(directory / 'heat-replay.json')
    assert raw['engine_wheel_sha256']==SHA
    retain('mea-heat-sensitivity', start, [source, r.ROOT/KIM2014, r.ROOT/VINJARAPU2024, producer],
           replay=raw)


if __name__ == '__main__':
    commands = {fn.__name__: fn for fn in (dea_curves, mdea_errors, mdea_onset, kuranov_72, amp_common_pressure, mea_heat)}
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('replay', choices=commands)
    args = cli.parse_args()
    a.study.reuse.bind_wheel()
    r.verify()
    commands[args.replay]()
