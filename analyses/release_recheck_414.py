"""Fixed-parameter replay for #414. Producer output goes to ignored run trees."""
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

from wheel_recheck_391 import compare

ROOT = Path(__file__).resolve().parents[1]
MEA = ROOT / 'analyses/mea_parameter_bundle'
COMMIT = '41dc357a656897b613597dd4c423914299f43cd2'
WHEEL = ROOT / f'build/engine-wheels/main-{COMMIT}/epcsaft-1.3.2-cp313-cp313-manylinux_2_39_x86_64.whl'
RESULTS = MEA / 'results/release-recheck-414'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def check_output(path):
    assert path.is_relative_to(ROOT / 'analyses') and '/results/runs/' in path.as_posix()
    subprocess.run(['git', 'check-ignore', '-q', str(path)], cwd=ROOT, check=True)
    assert not subprocess.check_output(['git', 'ls-files', '--', str(path)], cwd=ROOT)


def record_solve(path, sha, problem, result, row):
    import epcsaft
    evidence = dict(version=epcsaft.__version__, module=epcsaft.__file__, commit=COMMIT, sha256=sha,
                    row=row, T_K=problem.T, feed=problem.feed.values)
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


def mea(action, run):
    sys.path[:0] = [str(MEA / 'scripts'), str(ROOT / 'src')]
    import paper_evidence_341 as pe

    a, r = pe.a, pe.r
    sha = a.sha(WHEEL)
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


if __name__ == '__main__':
    command, first, second, *extra = sys.argv[1:]
    if command == 'compare':
        destination = Path(extra[0]).resolve()
        if not destination.is_relative_to(RESULTS):
            check_output(destination)
        write(destination, compare(first, second))
    else:
        assert command == 'mea'
        action, run = first, Path(second).resolve()
        assert action in ('replay', 'evidence', 'uncertainty', 'comparison', 'weights', 'shared', 'checks', 'stability')
        check_output(run)
        started = time.monotonic()
        try:
            mea(action, run)
        finally:
            write(run / f'{action}-wall.json', dict(command=sys.argv, seconds=time.monotonic() - started))
