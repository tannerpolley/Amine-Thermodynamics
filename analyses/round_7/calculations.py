"""Round 7 calculations on the immutable study wheel."""
# ruff: noqa: E402
from collections import Counter
import gzip
import json
from pathlib import Path
import sys
from time import monotonic

HERE = Path(__file__).resolve().parent
ANALYSES = HERE.parent
sys.path[:0] = [str(ANALYSES / 'mea_parameter_bundle/scripts')]

import salt_transfers_435 as transfer
from part_ii import Route, jsonable

a, r = sys.modules['salt_anchored_435'], transfer.r
ROOT = r.ROOT
OUT = HERE / 'results'
WORK = ROOT / 'build/round-7'
MDEA = transfer.mdea
SALT = MDEA.RESULTS.parent / 'salt-anchored-435/campaign'
FAMILIES = dict(Kuranov=66, **{'Kuranov-binary': 4}, Jakobsen=16, Carson=40, Merkley=4,
                Cp=33, **{'loaded-density': 33, 'unloaded-density': 24}, Kim=61)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(jsonable(value), allow_nan=False, indent=2) + '\n').encode()
    tmp = path.with_suffix('.tmp')
    tmp.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)
    tmp.replace(path)


class MDEAWeights(Route):
    def bind(self, point):
        spec = super().bind(point)
        rows = spec.inputs['observations']['fitted']
        assert Counter(row['group'] for row in rows) == FAMILIES
        assert 'measurement_covariance' not in spec.spec
        for row in rows:
            group = row['group']
            row['weight'] = 1 / FAMILIES[group]
            if group == 'Kuranov':
                assert row['arguments']['form'] == 'log_ratio'
                row['weight'] /= .015**2
        return spec


def mdea_incumbent(case):
    path = SALT / 'selection.json.gz' if case == 'salt' else MDEA.RESULTS / 'endpoint.json'
    point = r.read(path)
    return (point['point'] if case == 'salt' else point), path


def mdea_identity():
    started = monotonic()
    identity = {}
    for case in ('salt','historical'):
        point,source = mdea_incumbent(case)
        shared = (transfer.SHARED, r.s.sha256(transfer.SHARED)) if case=='salt' else None
        run = Route(MDEA.DECLARATION,WORK/f'mdea-identity/{case}',shared_values=shared)
        spec = run.bind(point)
        species = list(spec.parameters.component_ids)
        names = [q['name'] for q in point['reactions']['aqueous']]
        assert 'carbamate-anion' not in species and names==['R1','R2','R3','MDEA-dissociation']
        if case=='salt':
            ref = SALT/'identity.json.gz'
            assert run.result('identity.json')==r.read(ref)
        ref = SALT/'data-rows.json.gz' if case=='salt' else MDEA.RESULTS/'data-rows.json'
        expected = [x for x in r.read(ref) if x['role']=='fitted']
        rows,ok,cost = run.replay(point)
        a.study.reuse.compare_rows(rows,expected,('identity','status','group','observed'),1e-10)
        assert ok
        signature = run.result('identity.json')
        identity[case] = dict(species=species,reactions=point['reactions'],parameters=r.s.parameter_fingerprint(point['parameters']),
                 point_sha256=r.s.sha256(source),fitted_data_sha256=r.s.sha256(ref),identity=signature,
                 fitted=len(rows),cost=cost)
    save(OUT/'mdea-identity.json',dict(models=identity,seconds=monotonic()-started))


def mdea_phase(case, route, point):
    started = monotonic()
    states = route.states(route.bind(point))
    assert len(states)==11824
    aliases = route.same_calculations(point,states)
    unique = [s for s in states if s['key'] not in aliases]
    bank = r.read(MDEA.OLD/'split-record.json')
    trials = bank['trials']+bank.get('supplied_trials',[])
    root = OUT/f'C/{case}'
    if not (root/'pilot.json.gz').is_file():
        tick = monotonic()
        pilot = route.grid(point,states[::47],trial_set=trials)
        seconds = monotonic()-tick
        save(root/'pilot.json.gz',dict(rows=pilot,seconds=seconds,projected_seconds=seconds*len(states)/len(pilot)))
    fingerprint = r.s.parameter_fingerprint(point['parameters'])
    measured = {}
    for i in range(12):
        batch = unique[i::12]
        path = root/f'phase-batches/{i}.json.gz'
        if path.is_file():
            block = r.read(path)
            assert block['parameter_fingerprint']==fingerprint
        else:
            tick = monotonic()
            values = route.grid(point,batch,trial_set=trials)
            block = dict(rows=values,seconds=monotonic()-tick,parameter_fingerprint=fingerprint)
            save(path,block)
        assert [q['key'] for q in block['rows']]==[q['key'] for q in batch]
        measured.update((q['key'],q) for q in block['rows'])
    measured.update((dest,dict(measured[src],key=dest,seconds=0.,same_calculation_as=src))
                    for dest,src in aliases.items())
    rows = [measured[s['key']] for s in states]
    detail = transfer.classify(route,point,[x for x in rows if x['key'] not in aliases],states)
    confirmed = [x['key'] for x in detail if any(y['confirmed'] for y in x['attempts'])]
    save(root/'search-0.json.gz',rows)
    save(root/'search-outcome.json.gz',dict(seconds=monotonic()-started,tally=r.tally(rows),aliases=aliases,
        confirmed=confirmed,classifications=detail,parameter_fingerprint=fingerprint,
        bubble_refusals=[x['key'] for x in rows if (x.get('message') or '').startswith('pressure reference')]))


def mdea_weights(case):
    started = monotonic()
    incumbent, source = mdea_incumbent(case)
    shared = (transfer.SHARED, r.s.sha256(transfer.SHARED)) if case == 'salt' else None
    work = WORK / 'C' / case / 'weighted-log'
    default = Route(MDEA.DECLARATION, work / 'original', shared_values=shared)
    weighted = MDEAWeights(MDEA.DECLARATION, work / 'rms', shared_values=shared)
    reference = SALT / 'data-rows.json.gz' if case == 'salt' else MDEA.RESULTS / 'data-rows.json'
    expected = [x for x in r.read(reference) if x['role'] == 'fitted']
    actual, ok, cost = default.replay(incumbent)
    a.study.reuse.compare_rows(actual, expected, ('identity', 'group', 'status', 'observed'), 1e-10)
    assert ok
    bounds = weighted.config['k_bound']
    T = bounds['temperature_K']
    upper = next(row['k_no_gap'] for row in weighted.load(bounds['critical'])['rows'] if row['T_K'] == T) - bounds['margin']
    assert upper == -0.06711345443725586
    options = []
    for i, ref in enumerate(weighted.config['starts']):
        point = weighted.load(ref)
        if shared:
            point = transfer.substitute(point)
        value = min(MDEA.k_at(point['parameters'], T), upper)
        point['parameters'] = MDEA.rereference(point['parameters'], T, value)
        q = next(q for q in point['coordinates'] if q['identity'].startswith(MDEA.PAIR + '/a0'))
        q.update(origin=value, bounds=[q['bounds'][0], upper])
        weighted.write(f'fit-{i}/start.json', point)
        result = transfer.data_fit(weighted, f'fit-{i}', point)
        if result:
            options.append(result)
    best = min(options, default=None)
    selected = next((x for x in options if a.f.costs_tied(x[0], best[0], weighted.controls['function_tolerance'])), None)
    payload = dict(incumbent_sha256=r.s.sha256(source), original_cost=cost, selected=selected,
                   converged_starts=[(x[0], x[1]) for x in options], seconds=monotonic()-started)
    save(OUT / f'C/{case}/selection.json.gz', payload)
    for label, point in [('incumbent', incumbent)] + ([('refit', selected[2])] if selected else []):
        spec, replay, derivative = default.differentiate_endpoint(point)
        records = {label: transfer.objective.reduce_information(bound, replay, derivative, point)
                   for label, bound in (('original', spec), ('rms', weighted.bind(point)))}
        default.reduce(point)
        save(OUT / f'C/{case}/{label}.json.gz', dict(rows=default.result('data-rows.json'), objective=records,
             targeted=transfer.objective.q3_checks(default, point)))
    if selected:
        mdea_phase(case,default,selected[2])
    save(OUT / f'C/{case}/timing.json', dict(seconds=monotonic()-started, projection_s=3*573+1464))



def retain_mdea_fit_states():
    for case in ('historical','salt'):
        work = WORK/'C'/case/'weighted-log'/'rms'
        for folder in sorted(work.glob('fit-*')):
            names = ('start.json','start-replay.json','outcome.json')
            paths = [folder/name for name in names if (folder/name).is_file()]
            paths += sorted(folder.glob('stage-*/fit.json'))
            paths += sorted(folder.glob('stage-*/parameters.json'))
            paths += sorted(folder.glob('stage-*/replay.json'))
            payload = {path.relative_to(folder).as_posix():r.read(path) for path in paths}
            save(OUT/f'C/{case}/attempts/{folder.name}.json.gz',payload)


def mdea_pressures(cases):
    from mdea_reference import predicates, route, seed_state
    from phases import fixed

    started = monotonic()
    archive = r.read(SALT/'search-outcome.json.gz')
    key, = archive['confirmed']
    source = next(x for x in archive['classifications'] if x['key']==key)
    for case in cases:
        selected = r.read(OUT/f'C/{case}/selection.json.gz')['selected']
        endpoint, _ = mdea_incumbent(case)
        for label,point in [('original',endpoint)] + ([('rms',selected[2])] if selected else []):
            run = route(case,f'C/absolute-pressures/{label}')
            spec = run.bind(point)
            high = fixed(run,spec,seed_state(spec,source),source['pressure_Pa'],dict(pair=source['attempts'][0]),mdea=True)
            transfer.coexistence_421.fixed(run,spec)
            save(OUT/f'C/{case}/{label}-fixed-pressures.json.gz',dict(
                pressure_121_MPa=predicates(high,tolerance=1e-10),
                pressure_262_MPa=run.result('fixed-pressure.json'),
                fingerprint=r.s.parameter_fingerprint(point['parameters'])))
    save(OUT/'C'/f'absolute-pressures-{"-".join(cases)}-timing.json',dict(seconds=monotonic()-started))


if __name__ == '__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    if sys.argv[1]=='retain':
        retain_mdea_fit_states()
    elif sys.argv[1]=='identity':
        mdea_identity()
    elif sys.argv[1]=='absolute-pressures':
        mdea_pressures(sys.argv[2:] or ('salt','historical'))
    elif sys.argv[1]=='salt-search':
        point = r.read(OUT/'C/salt/selection.json.gz')['selected'][2]
        shared = (transfer.SHARED,r.s.sha256(transfer.SHARED))
        run = Route(MDEA.DECLARATION,WORK/'C/salt/phase',shared_values=shared)
        mdea_phase('salt',run,point)
        if 'historical' in sys.argv[2:]:
            mdea_weights('historical')
    else:
        for case in sys.argv[1:]:
            mdea_weights(case)
