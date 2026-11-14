"""Issue 266: pinned-wheel replay, bounded minor-species probes and phase evidence."""
import concurrent.futures
import copy
import gzip
import hashlib
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import sys
import time
import zipfile
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'analyses/mea_parameter_bundle/results/bicarbonate-carbonate-266'
PACKET = ROOT / 'analyses/solvent_specification_mea'
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')
WHEEL_SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
def read(name):
    return json.loads((OUT / name).read_text())
def write(name, value):
    value = dict(value,wheel_sha256=WHEEL_SHA) if isinstance(value,dict) else [dict(r,wheel_sha256=WHEEL_SHA) for r in value]
    path = OUT / (name+'.json')
    data = (json.dumps(jsonable(value), indent=2, allow_nan=False)+'\n').encode()
    if len(data) > 5000000:
        path, data = path.with_suffix('.json.gz'), gzip.compress(data, mtime=0)
    temporary = path.with_suffix('.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)
    alternate = path.with_suffix('') if path.suffix=='.gz' else path.with_suffix('.json.gz')
    alternate.unlink(missing_ok=True)
def valid(p):
    return p['status']=='Available' and p.get('requested_tolerance_met') and all(math.isfinite(p[k]) for k in ('value','residual'))
def predictions(rows):
    return [spec.prediction(r) for r in rows]
def quantity(r):
    return r['kind'] if r['constructor']=='observation' else r['constructor']
def metrics(rows, results):
    groups = {}
    for group, kind in dict.fromkeys((r['group'],quantity(r)) for r in rows):
        pairs = [(r,p) for r,p in zip(rows, results, strict=True) if (r['group'],quantity(r))==(group,kind)]
        good = [(r,p) for r,p in pairs if valid(p)]
        groups[group+' / '+kind] = dict(rows=len(pairs), available=len(good),
            cost=math.fsum(.5*r['weight']*p['residual']**2 for r,p in good),
            aard=100*math.fsum(abs(p['value']/r['arguments']['observed']-1) for r,p in good)/len(good) if good and all(r['arguments']['observed']!=0 for r,p in good) else None,
            rmse=math.sqrt(math.fsum((p['value']-r['arguments']['observed'])**2 for r,p in good)/len(good)) if good else None,
            within_2s=sum(abs(p['value']-r['arguments']['observed']) <= 2*r['arguments']['scale'] for r,p in good) if all('scale' in r['arguments'] for r,p in pairs) else None)
    return groups
def preservation(actual, baseline):
    result = {}
    for group, b in baseline.items():
        a = actual[group]
        kind = group.split(' / ')[1]
        pressure_species = kind in ('pressure','partial_pressure','mole_fraction','amount_ratio')
        metric = 'aard' if pressure_species or kind in ('phase_density','equilibrium_isobaric_heat_capacity') else 'rmse'
        result[group] = dict(metric=metric, before=b, after=a, passed=a['available']==b['rows'] and
            a[metric] is not None and a[metric] <= (b[metric]+2 if pressure_species else 1.25*b[metric]) and
            (pressure_species or a['within_2s']>=b['within_2s']))
    return result
def install(parameters, laws):
    spec.model = epcsaft.Mixture(parameters, thermochemistry=spec.thermal)
    for key, p in spec.problems.items():
        for reaction in p.reactions:
            original = original_laws[key, reaction.name]
            reaction.correlation = eq.ReactionLogPolynomial(**laws.get(reaction.name, original) |
                {k:original[k] for k in ('temperature_min','temperature_max','standard_state_id')})
def completed_laws(chart):
    return {r['name']:r['correlation'] for r in spec.fitted_reactions(chart)['aqueous']}
def chart_document(chart):
    document = copy.deepcopy(spec.inputs['endpoint'])
    values = {}
    index = 0
    for q in inputs['coordinates']:
        if 'targets' in q:
            for family, target, multiplier in q['targets']:
                identity = ('pair/'+'/'.join(target) if isinstance(target,list) else 'component/'+target)+'/'+family
                values[identity] = chart.physical[index]
                index += 1
    for entry in [*document['components'], *document['pairs']]:
        for coefficient in entry['coefficients']:
            if coefficient['identity'] in values:
                coefficient['value']['magnitude'] = values.pop(coefficient['identity'])
    assert not values
    return document
def phase_task(item):
    identity, key = item
    return spec.phase(dict(identity=identity, problem=key, endpoint_sha256=spec.parameter_sha256), policy)

if __name__ == '__main__':
    started = time.perf_counter()
    mode = sys.argv[1]
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest()==WHEEL_SHA
    with zipfile.ZipFile(WHEEL) as archive:
        assert all(archive.read(n)==(Path(epcsaft.__file__).parent.parent/n).read_bytes() for n in archive.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
    inputs = read('inputs.json')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in inputs['sources'].items())
    spec = SolventSpecification(PACKET / 'MEA-pre-260-340.toml')
    fitted = list(spec.inputs['observations']['fitted'])
    comparisons = inputs['records']
    spec.spec['templates'].update(inputs['problems'])
    spec.problems.update({k:spec.problem(k,{}) for k in inputs['problems']})
    spec.inputs['coordinates'] = inputs['coordinates']
    fields = ('a','b','c','d','e','f','reference_temperature','temperature_min','temperature_max','standard_state_id')
    original_laws = {(k,r.name):{f:getattr(r.correlation,f) for f in fields} for k,p in spec.problems.items() for r in p.reactions}
    baseline_metrics = read('baseline.json')['groups'] if mode!='baseline' else None
    reference_path = ROOT/'analyses/mea_parameter_bundle/results/adoption-297/historical-spec/inputs/reference.json'
    if mode=='baseline':
        results = predictions(fitted)
        reference = json.loads(reference_path.read_text())
        differences = [dict(identity=r['identity'], available=valid(p), prediction=None if not valid(p) else abs(p['value']/q['predicted']-1),
            residual=None if not valid(p) else abs(p['residual']-q['residual'])/max(abs(q['residual']),1)) for r,p,q in zip(fitted,results,reference,strict=True)]
        groups = metrics(fitted,results)
        cost = math.fsum(g['cost'] for g in groups.values())
        write('baseline',dict(rows=results,groups=groups,cost=cost,differences=differences,comparisons=predictions(comparisons)))
        assert len(results)==307 and all(d['available'] and max(d['prediction'],d['residual'])<=1e-8 for d in differences)
        assert abs(cost/148.87893934557388-1)<=1e-8
        assert groups['loaded density / phase_density']['within_2s']==44
        chart = reg.CoordinateSet()
        chart.coordinates = spec.coordinates()
        inferred = list(chart.start(spec.parameters._native,[spec.observation(r) for r in fitted+[r for r in comparisons if r['added']]],spec.thermal))
        assert max(map(abs,inferred))<=1e-12
        write('qualification-replay',dict(rows=307,cost=cost,relative_cost_error=abs(cost/148.87893934557388-1),inferred_start=inferred,
            residual_absolute_floor=1e-8,prediction_relative_tolerance=1e-8,R2_domains=sorted({v['temperature_max'] for (k,n),v in original_laws.items() if n=='R2'})))
        print('baseline verified',cost,flush=True)
    elif mode=='sensitivity':
        rows = []
        for j,q in enumerate(inputs['coordinates']):
            for sign in (-1,1):
                optimizer = [0.]*6
                optimizer[j] = sign
                native = reg.differentiate(spec.parameters,spec.coordinates(),[spec.observation(r) for r in comparisons],optimizer=optimizer,holds=[],thermochemistry=spec.thermal)
                document = chart_document(native.chart)
                laws = completed_laws(native.chart)
                install(epcsaft.Parameters.from_mapping(document),laws)
                replay = predictions(comparisons)
                assert all(valid(p) and abs(p['value']-v)<=1e-10*max(abs(v),1) for p,v in zip(replay,native.predictions,strict=True))
                rows.append(dict(coordinate=q['identity'],sign=sign,physical=list(native.chart.physical),comparisons=replay))
                install(spec.parameters,{})
                print('sensitivity',q['identity'],sign,flush=True)
        write(mode,rows)
    elif mode in ('fit1-executed','fit2'):
        added = [r for r in comparisons if r['added'] and (mode=='fit2' or r['group'].startswith('Matin'))]
        spec.inputs['observations']['fitted'] = fitted+added
        spec.spec['optimizer'] = dict(maximum_iterations=60,function_tolerance=1e-8,parameter_tolerance=1e-10,gradient_tolerance=1e-8,maximum_elapsed_time_seconds=1200.)
        result, report, parameters = spec.fit()
        write(mode+'-native',report)
        if not result.usable:
            write(mode,dict(assessable=False,status=result.status,message=result.message,usable=False,trial_failures=result.trial_failures))
            raise RuntimeError('Native probe unusable; retained diagnostics require diagnosis before any further fit')
        laws = completed_laws(result.chart)
        report.update(fitted_parameters=chart_document(result.chart),laws=laws,added=[r['identity'] for r in added],workers_requested=os.cpu_count())
        write(mode+'-native',report)
        install(parameters,laws)
        rows = spec.inputs['observations']['fitted']
        replay = predictions(rows)
        good = all(valid(p) for p in replay)
        cost = math.fsum(.5*r['weight']*p['residual']**2 for r,p in zip(rows,replay,strict=True)) if good else None
        delta = max(abs(math.sqrt(r['weight'])*p['residual']-w) for r,p,w in zip(rows,replay,result.weighted_residuals,strict=True)) if good else None
        assessable = result.usable and result.status=='converged' and good and delta<=1e-8 and abs(cost/result.final_cost-1)<=1e-8
        groups = metrics(fitted,replay[:307])
        write(mode,dict(assessable=assessable,status=result.status,message=result.message,usable=result.usable,
            cost=cost,native_cost=result.final_cost,maximum_replay_difference=delta,groups=groups,preservation=preservation(groups,baseline_metrics),
            rows=replay,comparisons=predictions(comparisons),trial_failures=result.trial_failures))
        print(mode,result.status,result.final_cost,'assessable',assessable,flush=True)
    elif mode.startswith('phase-'):
        endpoint = mode.removeprefix('phase-')
        if endpoint!='baseline':
            native = read(endpoint+'-native.json')
            if not read(endpoint+'.json')['assessable']:
                raise RuntimeError('No assessable endpoint: phase evaluation withheld')
            install(epcsaft.Parameters.from_mapping(native['fitted_parameters']),native['laws'])
        policy = dict(carbon_component='carbon-dioxide', carbon_species=['carbon-dioxide','carbamate-anion','bicarbonate-anion','carbonate-anion'],
            neutral_species=['water','monoethanolamine','carbon-dioxide'],packing_fraction_threshold=.1,ambiguity_interval=[.05,.35])
        tasks = list(dict.fromkeys((r.get('state_identity') or r['identity'],r[k]) for r in fitted+comparisons for k in ('problem','initial','final') if k in r))
        results = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count(),mp_context=multiprocessing.get_context('fork')) as pool:
            for result in pool.map(phase_task,tasks):
                results.append(result)
                write(mode,results)
                print(mode,len(results),'/',len(tasks),result['identity'],'liquid',len(result.get('dense',[])),'unresolved',len(result['unresolved']),flush=True)
    else:
        raise ValueError(mode)
    write(mode+'-runtime',dict(seconds=time.perf_counter()-started,mode=mode,python=sys.version,
        wheel_sha256=hashlib.sha256(WHEEL.read_bytes()).hexdigest(),installed_files_byte_identical=True,
        inputs_sha256=hashlib.sha256((OUT/'inputs.json').read_bytes()).hexdigest(),
        packages={k:importlib.metadata.version(k) for k in ('epcsaft','numpy','scipy','matplotlib')},
        sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('bicarbonate_carbonate_266_prepare.py'),ROOT/'src/MEA/solvent_specification.py',spec.path,
            *((spec.path.parent/spec.spec[k]['path']).resolve() for k in ('endpoint','declarations','caloric')), *([reference_path] if mode=='baseline' else []),
            *(p for p in sorted((PACKET/'inputs').iterdir()) if p.name not in ('endpoint.json','caloric.json','reference.json'))]}))
