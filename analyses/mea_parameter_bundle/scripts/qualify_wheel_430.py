"""Replay the #435 declarations and #434 normalized MDEA refit on a candidate wheel."""
# ruff: noqa: E402
import argparse
from functools import wraps
import hashlib
from pathlib import Path
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[3]


def timed(name, call):
    @wraps(call)
    def measure(*args, **kwargs):
        start = monotonic()
        print('begin', name, *[arg for arg in args[:1] if isinstance(arg, str)], flush=True)
        try:
            return call(*args, **kwargs)
        finally:
            print('elapsed', name, monotonic() - start, flush=True)

    return measure


def fixed_states(out):
    import common
    import part_ii
    import salt_transfers_435 as transfer
    from salt_anchored_435 import r

    common.RESULTS = out / 'amp_transfer'
    amp = part_ii.Route(transfer.amp.DECLARATION, out / 'amp_transfer/common-pressure')
    points = {family: r.read(out / 'amp_transfer' / family / 'selection.json')['point']
              for family in ('free', 'fixed')}
    points.update({f'prior-{family}': r.read(transfer.ANALYSES /
                   f'round_5/results/A/expanded-{family}.json.gz')['point'] for family in ('free', 'fixed')})
    transfer.amp_stability.common_pressure(amp, points)

    dea = transfer.route('dea_transfer', transfer.dea.OLD / 'f2-carbamate-413-route.json',
                         'campaign')
    selected = dea.result('selection.json')['chosen']['parameters']
    prior = r.read(transfer.DEABASE / 'selection.json')['chosen']['parameters']
    path = transfer.ANALYSES / 'dea_transfer/results/salt-anchored-435/campaign/refusal-replay.json'
    states = {x['key']: x for x in dea.states(dea.bind(selected))}
    cases = [states[x['key']] for x in r.read(path)['salt']]
    baseline = part_ii.Route(dea.path, out / 'dea_transfer/prior')
    dea.write('refusal-replay.json', dict(
        prior=r.grid(prior, cases, [], route=baseline, capture=True),
        salt=r.grid(selected, cases, [], route=dea, capture=True)))


def test(args, out):
    from importlib import import_module

    import pytest

    class CandidateWheel:
        def pytest_collection_modifyitems(self, items):
            module, = {item.module for item in items}
            # The tests load their own Part II module from file. Check its
            # candidate archive and installed bytes with the original guard.
            module.p.WHEEL = args.wheel.resolve()
            module.p.SHA = args.sha256
            declaration = ROOT / 'analyses/mdea_mea_workflow/inputs/part-ii-replay.json'
            module.p.Route(declaration, out / 'test-installed-bytes')
            pz_path = str(ROOT / 'analyses/pz_transfer')
            sys.path.insert(0, pz_path)
            try:
                pz = import_module('run')
            finally:
                sys.path.remove(pz_path)
            assert Path(pz.__file__).parent == Path(pz_path)
            pz.WHEEL, pz.SHA = args.wheel.resolve(), args.sha256

    raise SystemExit(pytest.main(['-q', 'tests/test_part_ii.py'], plugins=[CandidateWheel()]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=('salt', 'mea-control', 'mea-fit', 'mea-search',
                                        'mea-select', 'DEA', 'MDEA', 'AMP', 'normalized', 'fixed-states', 'test'))
    parser.add_argument('wheel', type=Path)
    parser.add_argument('sha256')
    parser.add_argument('output', type=Path)
    parser.add_argument('start', nargs='?')
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ROOT / 'build')
    out.mkdir(parents=True, exist_ok=True)
    if args.step == 'test':
        test(args, out)

    import salt_anchored_435 as mea
    import salt_transfers_435 as transfer
    import part_ii
    import common
    import run as round_3
    from salt_anchored_435 import f, r

    reference = mea.OUT
    study_sha = part_ii.SHA
    part_ii.WHEEL = mea.study.reuse.WHEEL = args.wheel.resolve()
    part_ii.SHA = transfer.SHA = mea.study.reuse.SHA = args.sha256
    mea.OUT = out / 'mea_parameter_bundle'
    mea.setup()
    transfer.WORK = out
    # All receiver results are already persisted at WORK. The #435 publisher
    # targets the original results directories and is specific to that study.
    transfer.retain = lambda owner, name, route: None
    f.fit = timed('fit with replays', f.fit)
    r.grid = timed('stability grid', r.grid)
    r.census = timed('stability census', r.census)
    transfer.score = timed('comparison rows and derivatives', transfer.score)
    part_ii.Route.grid = timed('route grid', part_ii.Route.grid)
    part_ii.Route.same_calculations = timed('stability data-state aliases', part_ii.Route.same_calculations)

    step = args.step
    if step == 'salt':
        mea.calibrate()
    elif step == 'mea-control':
        rows, ok, cost = r.replay(r.s.parameter_mapping(mea.study.RECORD))
        f.write('MEA/F2-control/replay.json', dict(rows=rows, available=ok, cost=cost))
    elif step == 'mea-fit':
        # The qualification changes one input, the wheel. The fresh salt
        # cascade is compared separately from the archived salt-fed MEA start.
        original_start = mea.mea_start

        def retained_start(label):
            r.OUT = reference
            r.SHA = study_sha
            try:
                mapping, fitted, ties = original_start(label)
            finally:
                r.OUT = mea.OUT
                r.SHA = args.sha256
            assert mapping == r.read(reference / 'MEA' / label / 'start.json')
            return mapping, fitted, ties

        mea.mea_start = retained_start
        mea.mea_fit(args.start)
    elif step == 'mea-search':
        mea.mea_search(args.start)
    elif step == 'mea-select':
        options = []
        for label in ('F2', 'F4'):
            directory = mea.OUT / 'MEA' / label
            fit = r.read(directory / 'fit-summary.json')
            search = r.read(directory / 'search-summary.json')
            if fit['status'] == 'converged' and search['stable'] and all(
                    row['passed'] for row in fit['acceptance'].values()):
                options.append(dict(fit, label=label))
        chosen = f.lowest_cost(options)
        if chosen:
            tolerance = r.read(r.A6)['controls']['function_tolerance']
            chosen['tied_starts'] = [x['label'] for x in options
                                     if f.costs_tied(x['cost'], chosen['cost'], tolerance)]
        f.write('MEA/selection.json', dict(chosen=chosen))
    elif step == 'normalized':
        common.RESULTS = out / 'normalized'
        transfer.objective.fit = timed('normalized fit with replays', transfer.objective.fit)
        transfer.objective.normalized_assessment = timed('normalized endpoint assessment', transfer.objective.normalized_assessment)
        transfer.objective.alternative(out / 'normalized-work', 'MDEA-1')
    else:
        source = reference / 'shared-parameters.json'
        shared = r.read(source)
        assert shared['wheel_sha256'] == study_sha
        assert r.s.sha256(r.ROOT / shared['source']) == shared['parameter_sha256']
        transfer.SHARED = out / 'shared-parameters.json'
        r.s.write_json(transfer.SHARED, dict(shared, wheel_sha256=args.sha256,
                                             study_shared_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
        if step == 'fixed-states':
            fixed_states(out)
        else:
            getattr(transfer, f'{step.lower()}_fit')()
    f.OUT = r.OUT = mea.OUT
    f.write(f'receipts/{step}-{args.start or "all"}.json', round_3.receipt())


if __name__ == '__main__':
    main()
