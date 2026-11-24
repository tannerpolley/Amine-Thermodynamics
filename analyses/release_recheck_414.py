"""Fixed-parameter replay for #414. Producer output goes to ignored run trees."""
from itertools import count
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

from wheel_recheck_391 import compare, load

ROOT = Path(__file__).resolve().parents[1]
MEA = ROOT / 'analyses/mea_parameter_bundle'
COMMIT = '41dc357a656897b613597dd4c423914299f43cd2'
WHEEL = ROOT / f'build/engine-wheels/main-{COMMIT}/epcsaft-1.3.2-cp313-cp313-manylinux_2_39_x86_64.whl'
RESULTS = MEA / 'results/release-recheck-414'
WHEEL_SHA = 'ad8f2338f2983ec509cabba1280007005081ef3460838b584bd4b32b334dd2b5'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def check_output(path):
    assert path.is_relative_to(ROOT / 'analyses') and '/results/runs/' in path.as_posix()
    subprocess.run(['git', 'check-ignore', '-q', str(path)], cwd=ROOT, check=True)
    assert not subprocess.check_output(['git', 'ls-files', '--', str(path)], cwd=ROOT)


def record_solve(path, sha, problem, result, row):
    import epcsaft
    temperature = problem.T if hasattr(problem, 'T') else problem.temperature.value
    evidence = dict(version=epcsaft.__version__, module=epcsaft.__file__, commit=COMMIT, sha256=sha,
                    row=row, T_K=temperature, feed=problem.feed.values)
    evidence.update({k: getattr(result, k) for k in ('linear_solver', 'solver_status', 'success',
                                                    'requested_tolerance_met', 'message', 'pressure')})
    write(path, evidence)
    assert epcsaft.__version__ == '1.3.2' and result.linear_solver == 'ma57', evidence


def record_identity(spec, path, sha):
    from epcsaft import equilibrium as eq
    record = spec.inputs['observations']['fitted'][0]
    problem = spec.problems[record.get('problem', record.get('initial'))]
    record_solve(path, sha, problem, eq.solve_equilibrium(spec.model, problem), record['identity'])


def uncertainty(pe, sha):
    import uncertainty_307 as u

    class ConditionalFit(Exception):
        pass

    def skip_fit(*args, **kwargs):
        raise ConditionalFit

    u.WHEEL, u.SHA, u.fit = WHEEL, sha, skip_fit
    try:
        pe.uncertainty()
    except ConditionalFit:
        pass
    spec, _, out = u.setup('MEA')
    records = u.prediction_records(spec, 'MEA')
    ev = u.derivative(spec, records)
    u.write(out / 'predictions.json', dict(records=[{k: r.get(k) for k in ('identity', 'group', 'kind', 'row', 'arguments')}
                                                   for r in records], values=ev.predictions, gradient=ev.optimizer_gradient))


def census(run, reduce_state):
    saved = RESULTS.parent / 'runs/release-recheck-414/stability/candidate'
    retained = RESULTS.parent / 'paper-evidence-341/stability/candidate/census-raw.json.gz'
    reference, replay = (load(path)['result'] for path in (retained, saved / retained.name))
    pairs, complete = [], []
    for old, new in zip(reference, replay, strict=True):
        before, after = (row['stability'][0]['trials'] for row in (old, new))
        assert old['index'] == new['index'] and len(before) == 9 and len(after) == 10
        assert after[9]['seed'] == 'dominant-charge-pair-midpoint', new['index']
        state = reduce_state(new)
        complete.append(state['parent_admitted'] and state['reports_completed'] and state['trials'] == 10
                        and state['failed_optimizers'] == state['unresolved_trials'] == 0)
        assert new['classification'] == old['classification'] and state['resolved'] == 0, state
        for i, (a, b) in enumerate(zip(before, after[:9], strict=True)):
            x, y = (t['quantities'] for t in (a, b))
            limit = x['summation_estimate_over_rt'] + y['summation_estimate_over_rt']
            matched = all(a[k] == b[k] for k in ('seed', 'phase', 'resolved_descent'))
            matched &= a['optimizer']['success'] == b['optimizer']['success']
            pairs.append(dict(index=new['index'], trial=i, retained=x['tpd_over_rt'], release=y['tpd_over_rt'],
                              limit=limit, matched=matched, release_status=b['optimizer']['solver_status']))
    worst = max(pairs, key=lambda p: abs(p['release'] - p['retained']))
    failures = [p for p in pairs if not p['matched'] or abs(p['release'] - p['retained']) > p['limit']]
    write(run / 'census-amendment-1.json', dict(reference=str(retained.relative_to(ROOT)), pairs=len(pairs),
          complete=sum(complete), worst=worst, failures=failures,
          max_fraction_of_limit=max(abs(p['release'] - p['retained']) / p['limit'] for p in pairs)))
    assert len(pairs) == 1458 and sum(complete) == 162 and not failures, failures[:3]
    destination = run / 'stability/candidate'
    destination.mkdir(parents=True, exist_ok=True)
    for name in ('census-raw.json.gz', 'grid.json'):
        shutil.copyfile(saved / name, destination / name)
    search = load(saved / 'search.json')
    search['census'].update(incomplete=0, incomplete_indices=[])
    write(destination / 'search.json', search)
    reduced = load(saved / 'census.json')
    reduced['result']['summary'] = search['census']
    for row, admitted in zip(reduced['result']['rows'], complete, strict=True):
        row['complete'] = admitted
    write(destination / 'census.json', reduced)
    (ROOT / '.venv').mkdir(exist_ok=True)


def mea(action, run):
    sys.path[:0] = [str(MEA / 'scripts'), str(ROOT / 'src')]
    import paper_evidence_341 as pe

    a, r = pe.a, pe.r
    sha = a.sha(WHEEL)
    assert sha == WHEEL_SHA
    for owner in (a, r):
        owner.COMMIT, owner.SHA, owner.WHEEL = COMMIT, sha, WHEEL
    r.s.ENGINE_COMMIT, r.s.ENGINE_WHEEL_SHA256 = COMMIT, sha
    r.s.RUNS = pe.OUT = run
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                          cwd=ROOT, text=True).strip()).parent
    a.subprocess = SimpleNamespace(check_output=lambda command: subprocess.check_output(
        [*command[:2], str(common / 'upstream/epcsaft'), *command[3:]]))
    pe.setup()
    spec = r.bind(r.s.parameter_mapping(pe.RECORD))
    record_identity(spec, run / f'{action}-identity.json', sha)
    try:
        if action == 'uncertainty':
            uncertainty(pe, sha)
        elif action == 'stability':
            from phase_diagnosis_255 import reduce_state
            census(run, reduce_state)
            pe.stability()
            retained = RESULTS.parent / 'wheel-recheck-05e94210/stability-adopted-law/search.json'
            checks = ('grid', 'offset', 'census', 'supplied', 'stable')
            expected, actual = (load(p) for p in (retained, run / 'stability/candidate/search.json'))
            for name in ('minimum_tpd', 'minimum_liquid_tpd'):
                del expected['supplied'][name], actual['supplied'][name]
            assert {k: actual[k] for k in checks} == {k: expected[k] for k in checks}, actual
        else:
            getattr(pe, action)()
    except (AssertionError, TypeError) as error:
        frame = error.__traceback__
        while frame is not None:
            local = frame.tb_frame.f_locals
            if frame.tb_frame.f_code is pe.replay.__code__ and 'reference' in local:
                write(run / 'failed-replay.json', {k: local[k] for k in ('values', 'reference', 'cost', 'ok', 'delta') if k in local})
            frame = frame.tb_next
        raise


def stripper(run, export):
    sys.path[:0] = [str(export / 'analyses/mea_parameter_bundle/scripts'), str(export / 'src'), str(MEA / 'scripts')]
    import shared_evaluation as shared
    import stripper_temperature_409 as producer
    from epcsaft import equilibrium as eq

    assert producer.sha(WHEEL) == WHEEL_SHA
    shared.ENGINE_COMMIT, shared.ENGINE_WHEEL_SHA256, producer.OUT = COMMIT, WHEEL_SHA, run
    solve = eq.solve_equilibrium
    ordinal = count()

    def observed_solve(model, problem, **kwargs):
        result = solve(model, problem, **kwargs)
        record_solve(run / f'solves/{os.getpid()}-{next(ordinal)}.json', WHEEL_SHA, problem, result, None)
        return result

    eq.solve_equilibrium = observed_solve
    try:
        producer.replay(export)
    except (AssertionError, TypeError) as error:
        local = error.__traceback__.tb_next.tb_frame.f_locals
        if 'check' in local:
            write(run / 'failed-heat-replay.json', local['check'])
        raise
    producer.table()


def dea(run):
    base = ROOT / 'analyses/dea_transfer'
    sys.path.insert(0, str(base))
    import part_ii
    import pinned
    import rerun

    part_ii.WHEEL, part_ii.SHA = pinned.WHEEL, pinned.SHA = WHEEL, WHEEL_SHA
    chosen = load(base / 'results/refit-413/selection.json')['chosen']
    point, native = chosen['parameters'], chosen['optimizer_report']
    route = part_ii.Route(base / 'inputs/part-ii-346/f2-carbamate-413-route.json', run)
    record_identity(route.bind(point), run / 'solve.json', WHEEL_SHA)
    rows, available, cost = route.replay(point)
    ref = [dict(r, value=v) for r, v in zip(rows, native['predictions'][:len(rows)], strict=True)]
    route.write('replay.json', dict(rows=rows, reference=ref, available=available, cost=cost, reference_cost=native['data_cost']))
    errors = rerun.error(rows, ref, cost, native['data_cost'])
    route.write('replay-errors.json', errors)
    assert available and max(errors['max_relative_prediction_error'], errors['relative_cost_error']) <= rerun.LIMIT, errors
    route.reduce(point)
    route.uncertainty(point)
    route.curves(point)
    search = route.search(point)
    route.write('search-summary.json', search)
    for key in ('states', 'available', 'descent'):
        assert search['grid'][key] == chosen['search']['grid'][key], (key, search['grid'], chosen['search']['grid'])


if __name__ == '__main__':
    command, first, second, *extra = sys.argv[1:]
    if command == 'compare':
        destination = Path(extra[0]).resolve()
        if not destination.is_relative_to(RESULTS):
            check_output(destination)
        write(destination, compare(first, second))
    else:
        action, run = first, Path(second).resolve()
        check_output(run)
        started = time.monotonic()
        try:
            if command == 'stripper':
                stripper(run, Path(extra[0]).resolve())
            elif command == 'dea':
                dea(run)
            else:
                assert command == 'mea'
                assert action in ('replay', 'evidence', 'uncertainty', 'comparison', 'weights', 'shared', 'checks', 'stability')
                mea(action, run)
        finally:
            write(run / f'{action}-wall.json', dict(command=sys.argv, seconds=time.monotonic() - started))
