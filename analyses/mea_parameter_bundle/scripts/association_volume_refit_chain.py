"""Issue 212: declarations and refits at the owner-fixed MEA association volume."""
import copy
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import time
import traceback

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT/'src'), str(Path(__file__).parent), str(ROOT/'analyses/mea_parameter_bundle/calibration-misfit')]
import engine_3e83e19c_refits as r
import fit_observations as o

c, OLD, J = r.c, r.OUT, r.J
OUT = r.R/'engine-3e83e19c-refit-chain'
VOLUME = 'association/monoethanolamine/a/monoethanolamine/b/volume'
KIJ = 'pair/monoethanolamine/water/k_ij'
loader = importlib.machinery.SourceFileLoader('held_followups', str(J/'amendment-6/inputs/held-followups/build.py.txt'))
h = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
loader.exec_module(h)


def save(path, value):
    c.write(path, value)
    return str(path.relative_to(ROOT))


def bind(spec, moved):
    spec = r.repoint(spec, moved)
    spec['engine'] = r.ENGINE
    for key in ('reference', 'reduction'):
        if key+'_sha256' in spec:
            spec[key+'_sha256'] = h.sha(ROOT/spec[key+'_path'])
    return spec


def run(mode):
    directory = OUT/mode
    if mode == 'stage2':
        spec = c.load(OLD/'stage2/spec.json')
        reference = o.s.with_parameter_values(c.load(OLD/'stage2/run/reference-parameters.json'), {VOLUME: .036305439})
        spec['reference_path'] = save(OUT/'reference/parameters.json', reference)
        spec['inputs'].append(dict(path=spec['reference_path'], sha256=h.sha(ROOT/spec['reference_path'])))
        spec['cases'] = [x for x in spec['cases'] if x['id']=='neutral-mea-water']
        for start in spec['cases'][0]['starts']:
            path = OLD/f"stage2/run/neutral-mea-water/{start['id']}/parameters.json"
            start['value'] = o.s.parameter_values(c.load(path))[KIJ]
            spec['inputs'].append(dict(path=str(path.relative_to(ROOT)), sha256=h.sha(path)))
    elif mode == 'stage5':
        spec = c.load(OLD/'stage5/spec.json')
        endpoint = c.load(OUT/'stage2/run/selection.json')[0]['selected']['path']
        reference = o.s.with_parameter_values(c.load(ROOT/spec['reference_path']),
            {VOLUME: .036305439, KIJ: o.s.parameter_values(c.load(ROOT/endpoint))[KIJ]})
        path = save(directory/'reference.json', reference)
        spec = bind(spec, {spec['reference_path']: path})
        spec['inputs'].append(dict(path=endpoint, sha256=h.sha(ROOT/endpoint)))
    else:
        source = OLD/mode/'spec.json' if mode!='held-x3' else J/'amendment-6/held-followups/held-x3/fit-spec.json'
        spec = c.load(source)
        endpoint = (OUT/'restricted' if mode=='restricted-2' else OLD/mode)/'run/fit/usable-budget-endpoint.json'
        if mode=='held-x3':
            endpoint = J/'amendment-6/held-followups/held-x3/fit/usable-budget-endpoint.json'
        chemistry = endpoint.with_name('chemistry-coordinates.json')
        totals = c.load(chemistry)['enthalpy_shifts_J_mol']
        original = c.load(h.BASE/'held-information.json')['information_coordinates']
        boxes = {x['identity']: x['bounds'] for x in original if 'reaction' in x}
        for coordinate in spec['information_coordinates']:
            if coordinate['identity'] in boxes:
                coordinate['bounds'] = copy.deepcopy(boxes[coordinate['identity']])
        h.rebase(spec, totals)
        branch = OUT/'stage5/run/larger-dV-parameters.json'
        dielectric = {k: v for k,v in o.s.parameter_values(c.load(branch)).items() if k.startswith('component/monoethanolamine/dielectric_')}
        mapping = o.s.with_parameter_values(c.load(endpoint), {VOLUME: .036305439, **dielectric})
        values, inward = o.s.parameter_values(mapping), {}
        for coordinate in spec['information_coordinates']:
            if coordinate.get('family')=='segment_diameter':
                lo, hi = coordinate['bounds']
                room = 2*max(spec['verification']['steps_optimizer'])*coordinate['scale']
                value = values[coordinate['identity']]
                if value < lo+room or value > hi-room:
                    inward[coordinate['identity']] = [value, min(max(value,lo+room),hi-room)]
        mapping = h.held_sizes(o.s.with_parameter_values(mapping, {k:v[1] for k,v in inward.items()}), spec)
        assert c.stage6_ties(spec, mapping)
        assert abs(values['reaction:R5:correlation:a_k']-c.load(chemistry)['R5_unshifted_a_k']-totals['R5']/(o.thermal.R*r.math.log(10)))<1e-9
        start_path = save(directory/'start.json', mapping)
        save(directory/'chemistry-start.json', c.load(chemistry))
        save(directory/'preparation.json', dict(endpoint=str(endpoint.relative_to(ROOT)), endpoint_sha256=h.sha(endpoint), chemistry_sha256=h.sha(chemistry), inward_moves=inward, inherited_totals_J_mol=totals))
        old_start = spec['information_starts'][0]
        reduction = OUT/'stage5/run/reduction.json'
        moved = {old_start['parameters_path']: start_path, spec['reference_path']: str((OUT/'stage5/run/parameters.json').relative_to(ROOT)),
                 spec['shared_stage5']['reduction_path']: str(reduction.relative_to(ROOT))}
        spec = bind(spec, moved)
        spec['shared_stage5'] = dict(reduction_path=str(reduction.relative_to(ROOT)), reduction_sha256=h.sha(reduction), branches=c.load(reduction)['branches'])
        spec['information_starts'] = [dict(old_start, parameters_path=start_path, sha256=h.sha(ROOT/start_path), reaction_enthalpy_shifts_J_mol=totals)]
        for path in (endpoint, chemistry, branch):
            spec['inputs'].append(dict(path=str(path.relative_to(ROOT)), sha256=h.sha(path)))
        groups = 1 if mode=='restricted-2' else 3
        spec['workers'] = max(1, min(os.cpu_count()//groups, c.machine(spec,None)['MemAvailable_bytes']//(groups*spec['worker_memory']['allowance_bytes'])))
        information = {k:v for k,v in spec.items() if k not in ('fit_case','release_tests_path','release_tests_sha256')}
        path = directory/'information-spec.json'
        c.write(path, information)
        c.run(path, directory/'release', case_ids=['stage6'], operation='information')
        assert not list(OUT.glob('*/stop.json')), 'another refit stopped; no further fit launched'
        release = directory/'release/release-tests.json'
        spec.update(release_tests_path=str(release.relative_to(ROOT)), release_tests_sha256=h.sha(release))
    spec['engine'] = r.ENGINE
    c.write(directory/'spec.json', spec)
    c.run(directory/'spec.json', directory/('run/fit' if mode not in ('stage2','stage5') else 'run'), case_ids=['stage'+str(spec['stage'])], operation='fit')


if __name__ == '__main__':
    mode, started, cpu = sys.argv[1], time.monotonic(), c.cpu_seconds()
    assert r.ENGINE['wheel_sha256']=='0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804'
    save(OUT/mode/'command.json', dict(argv=sys.orig_argv, engine=r.ENGINE, producer_sha256=h.sha(__file__)))
    try:
        run(mode)
    except Exception:
        save(OUT/mode/'stop.json', dict(cause=traceback.format_exc()))
        raise
    finally:
        save(OUT/mode/'command-timing.json', dict(wall_s=time.monotonic()-started, cpu_s=c.cpu_seconds()-cpu))
