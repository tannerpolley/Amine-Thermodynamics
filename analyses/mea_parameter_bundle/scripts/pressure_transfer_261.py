"""Pressure-source and concentration-transfer probes using the generic solvent driver (#261)."""
import ast
import copy
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tomllib
import zipfile

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'analyses/mea_parameter_bundle'
OUT = B / 'results/pressure-transfer-261'
AN = ROOT / 'analyses/solvent_specification_mea'
REF = B / 'results/engine-3e83e19c-paper-evidence/selected-assessment'
WHEEL_SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
CHAIN = B / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/spec.json'


def read(path):
    path=Path(path)
    compressed=path.with_suffix(path.suffix+'.gz')
    if not path.exists() and compressed.exists():
        with gzip.open(compressed,'rt') as stream:
            return json.load(stream)
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name not in ('coordinates.json','pressure-identity.json','parameters.json'):
        value = dict(value,engine_wheel_sha256=WHEEL_SHA) if isinstance(value,dict) else [dict(v,engine_wheel_sha256=WHEEL_SHA) if isinstance(v,dict) else v for v in value]
    data = (json.dumps(jsonable(value), indent=2, allow_nan=False) + '\n').encode()
    if len(data) > 5000000:
        path = path.with_suffix(path.suffix + '.gz')
        data = gzip.compress(data, mtime=0)
    path.write_bytes(data)
    if path.name=='parameters.json':
        write(path.with_name('parameters-provenance.json'),dict(parameter_sha256=hashlib.sha256(data).hexdigest()))


def verify():
    wheel = ROOT / 'build/engine-wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl'
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == WHEEL_SHA
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert archive.read(name) == (Path(epcsaft.__file__).parent.parent / name).read_bytes(), name
    assert hashlib.sha256((AN / 'inputs/endpoint.json').read_bytes()).hexdigest() == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'


def prepare():
    # Reuse the existing declaration serializer without executing its campaign preparation.
    import shared_evaluation as historical
    source = AN / 'prepare.py'
    nodes = [n for n in ast.parse(source.read_text()).body if isinstance(n, ast.FunctionDef) and n.name in ('toml', 'fields', 'equal', 'problem')]
    ns = dict(json=json, jsonable=jsonable)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), ns)
    base = SolventSpecification(AN / 'MEA.toml')
    ns['ids'] = base.parameters.component_ids
    declaration = copy.deepcopy(base.spec)
    declaration.pop('declarations')
    for dataset in declaration['datasets']:
        dataset['path'] = os.path.relpath(AN / dataset['path'], OUT)
        if 'observation_parameters' in dataset:
            dataset['observation_parameters']['path'] = os.path.relpath(AN / dataset['observation_parameters']['path'], OUT)
    config = {k: copy.deepcopy(base.spec[k]) for k in ('schema', 'start', 'endpoint', 'coordinates', 'phase_states', 'caloric')}
    for key in ('start', 'endpoint', 'phase_states', 'caloric'):
        config[key]['path'] = os.path.relpath(AN / config[key]['path'], OUT)
    def binding(name, value):
        write(OUT / name, value)
        return dict(path=name, sha256=hashlib.sha256((OUT / name).read_bytes()).hexdigest())
    coords = read(AN / 'inputs/fit-coordinates.json')
    coords = [dict(q, origin=q['base']) for q in coords]
    original = read(CHAIN)['information_coordinates']
    values = historical.parameter_values(base.inputs['endpoint'])
    for i in (12, 13):
        q = original[i]
        coords.append(dict(identity=q['identity'], original_index=i, origin=values[q['identity']], scale=q['scale'], bounds=q['bounds'], targets=[[q['family'], q['target'], 1.0]]))
    coords.sort(key=lambda q: q['original_index'])
    config['coordinates'] = binding('coordinates.json', coords)
    config['optimizer'] = dict(maximum_iterations=60, maximum_elapsed_time_seconds=1200., function_tolerance=1e-8, gradient_tolerance=1e-8, parameter_tolerance=1e-10)
    metadata, exclusions, native_checks = {}, [], []
    overlap = {r['identity']: r for r in base.inputs['observations']['fitted'] if r['kind'] == 'partial_pressure'}
    assert len(overlap) == 47
    for group, observations in read(REF / 'observation-groups.json').items():
        if group == 'packet':
            continue
        for observation in observations:
            target, = observation['targets']
            request = historical.corrected_request(observation['request'], historical.reaction_values(base.inputs['endpoint']), mapping=base.inputs['endpoint'])
            T = request['temperature']['value']
            if T > 393.15:
                exclusions.append(dict(identity=target['identity'], T_K=T, reason='outside declared reaction domain 293.15–393.15 K'))
                continue
            identity = target['identity']
            feed = request['reaction_system']['feed_amounts_mol']
            meta = dict(source=target['source_identity'], T_K=T, loading=feed[0]/feed[1], wt_percent=round(100*feed[1]*61.084/(feed[1]*61.084+feed[2]*18.01528)), original=identity in overlap)
            assert identity not in metadata
            metadata[identity] = meta
            if identity in overlap:
                continue
            p = historical._problem_from_request(request)
            native = p._native(base.model)
            chemistry = {}
            template = ns['problem'](native, chemistry)
            normalized = tomllib.loads('x = '+ns['toml'](chemistry))['x']
            assert all(declaration['chemistry']['reactions'][k] == v for k,v in normalized.items())
            key = 'pressure-' + identity
            declaration['templates'][key] = template
            path = OUT / 'inputs' / (identity + '.csv')
            path.parent.mkdir(exist_ok=True)
            with path.open('w') as stream:
                writer = csv.DictWriter(stream, fieldnames=['identity', 'source', 'observation_order'])
                writer.writeheader(); writer.writerow(dict(identity=identity, source=json.dumps(meta), observation_order=1000+len(metadata)))
            declaration['datasets'].append(dict(name=identity, group='reactive pressure', role='comparison', constructor='observation', kind='partial_pressure', template=key, arguments=dict(observed=target['observed'], form='log_ratio', phase=p.phases[1].name, species=['carbon-dioxide'], mass_basis=False), weight=11.11111111111111, filter={}, temperature_domain=[293.15,393.15], path=str(path.relative_to(OUT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), columns=dict(observation_order='observation_order')))
            native_checks.append((key, native))
    assert len(metadata) == 252 and len(exclusions) == 3
    write(OUT / 'pressure-identity.json', metadata); write(OUT / 'excluded.json', exclusions)
    declaration = {k:v for k,v in declaration.items() if k not in config}
    text = '\n'.join(k+' = '+ns['toml'](v) for k,v in declaration.items())+'\n'
    (OUT / 'declarations.toml').write_text(text)
    config['declarations'] = dict(path='declarations.toml', sha256=hashlib.sha256(text.encode()).hexdigest())
    (OUT / 'study.toml').write_text('\n'.join(k+' = '+ns['toml'](v) for k,v in config.items())+'\n')
    loaded = SolventSpecification(OUT / 'study.toml')
    for key, native in native_checks:
        ns['equal'](native, loaded.problem(key, {})._native(loaded.model))
    write(OUT / 'preparation.json', dict(native_problems_compared=len(native_checks), unique_pressure_rows=len(metadata), original_overlap=len(overlap), exclusions=len(exclusions), inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, AN/'MEA.toml', AN/'declarations.toml', AN/'inputs/fit-coordinates.json', CHAIN, REF/'observation-groups.json', Path(__file__)]}))
    print('Prepared', len(metadata), 'pressure rows and', len(native_checks), 'native problem comparisons', flush=True)


def predictions(s, rows):
    values = [s.prediction(r) for r in rows]
    source = AN/'run.py'
    functions = [n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='accept_pairs']
    namespace = dict(math=math)
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),namespace)
    namespace['accept_pairs'](rows,values)
    bad = [p for p in values if p['status'] != 'Available' or not p.get('requested_tolerance_met')]
    if bad:
        write(OUT/'unavailable-predictions.json',bad)
    assert not bad, bad[:1]
    return values


def baseline():
    s = SolventSpecification(OUT / 'study.toml')
    fitted = s.inputs['observations']['fitted']
    values = predictions(s, fitted)
    ref = read(AN / 'inputs/reference.json')
    differences = []
    for r,p,q in zip(fitted, values, ref, strict=True):
        assert r['identity'] == q['target']
        differences.append(dict(identity=r['identity'], prediction=abs(p['value']-q['predicted'])/max(abs(q['predicted']),1e-300), residual=abs(p['residual']-q['residual'])/max(abs(q['residual']),1.)))
    assert max(max(d['prediction'],d['residual']) for d in differences) <= 1e-8
    write(OUT / 'baseline.json', dict(rows=values, differences=differences, cost=sum(.5*r['weight']*p['residual']**2 for r,p in zip(fitted,values,strict=True))))
    assert abs(sum(.5*r['weight']*p['residual']**2 for r,p in zip(fitted,values,strict=True))-148.87893934557388)<=1e-8*148.87893934557388
    coords = s.coordinates()
    gradient = reg.differentiate(s.parameters, coords, [s.observation(r) for r in fitted], optimizer=[0.]*16, thermochemistry=s.thermal)
    assert max(abs(p['value']-v)/max(abs(p['value']),1.) for p,v in zip(values,gradient.predictions,strict=True)) <= 1e-10
    write(OUT / 'zero-chart.json', dict(predictions=list(gradient.predictions), physical=list(gradient.chart.physical)))
    comparisons = predictions(s, s.inputs['observations']['comparisons'])
    write(OUT / 'baseline-comparisons.json', comparisons)
    print('Baseline',len(values), 'cost',sum(.5*r['weight']*p['residual']**2 for r,p in zip(fitted,values,strict=True)),flush=True)


def apply(s, parameters, chart, mapping):
    laws = s.fitted_reactions(chart)
    for problem in s.problems.values():
        for reaction in problem.reactions:
            options = [r['correlation'] for group in laws.values() for r in group if r['name'] == reaction.name and r['correlation']['temperature_max'] == reaction.correlation.temperature_max]
            assert options
            reaction.correlation = eq.ReactionLogPolynomial(**options[0])
    s.model = epcsaft.Mixture(parameters, thermochemistry=s.thermal)
    # Continuation uses construction_parameters: replace each with the fitted EOS, retaining only construction domain extensions.
    import shared_evaluation as h
    for key in list(s.construction_parameters):
        if key == s.parameter_sha256:
            s.construction_parameters[key] = parameters
        else:
            document = next(d['observation_parameters'] for d in s.spec['datasets'] if d.get('observation_parameters',{}).get('sha256') == key)
            amended = h.with_parameter_values(s.load_record(document),h.parameter_values(mapping))
            s.construction_parameters[key] = epcsaft.Parameters.from_mapping(amended)
    s.continue_groups()


def sensitivity():
    s = SolventSpecification(OUT / 'study.toml')
    meta = read(OUT / 'pressure-identity.json')
    rows = [r for group in ('fitted','comparisons') for r in s.inputs['observations'][group] if meta.get(r['identity'],{}).get('wt_percent') in (15,45)]
    assert len(rows) == 70
    native = reg.differentiate(s.parameters, s.coordinates(), [s.observation(r) for r in rows], optimizer=[0.]*16, thermochemistry=s.thermal)
    J = np.array(native.residual_optimizer_gradient).reshape(70,16)
    write(OUT / 'sensitivities.json', dict(identities=[r['identity'] for r in rows], coordinates=s.inputs['coordinates'], log_pressure_optimizer_derivatives=J.tolist(), predictions=list(native.predictions), by_strength={str(w):J[[meta[r['identity']]['wt_percent']==w for r in rows]].mean(axis=0).tolist() for w in (15,45)}))
    checks=[]
    for col in (0,12):
        for step in (.01,.005):
            samples=[]
            for sign in (-1,1):
                point=[0.]*16;point[col]=step*sign
                v=reg.differentiate(s.parameters,s.coordinates(),[s.observation(r) for r in rows[:1]],optimizer=point,thermochemistry=s.thermal)
                samples.append(math.log(v.predictions[0]))
            fd=(samples[1]-samples[0])/(2*step)
            checks.append(dict(column=col,step=step,exact=J[0,col],finite_difference=fd,error=abs(fd-J[0,col])))
    write(OUT / 'sensitivity-checks.json',checks)
    assert all(q['error']<=1e-8+1e-5*abs(q['exact']) for q in checks)
    print('Sensitivities',J.shape,flush=True)


def statistics(s, rows, values):
    grouped={}
    for r,p in zip(rows,values,strict=True):
        if r['kind']=='partial_pressure':
            continue
        key=r['group']+' / '+('addition_enthalpy' if r['constructor']!='observation' else r['kind'])
        grouped.setdefault(key,[]).append((r,p))
    result={}
    for key, pairs in grouped.items():
        kind=pairs[0][0]['kind']
        dimensional=kind=='temperature' or pairs[0][0]['constructor']!='observation'
        count=sum(abs(p['residual'])<=2 for r,p in pairs)
        metric=math.sqrt(sum((p['value']-p['observed'])**2 for r,p in pairs)/len(pairs)) if dimensional else 100*sum(abs(p['value']/p['observed']-1) for r,p in pairs if p['observed']!=0)/sum(p['observed']!=0 for r,p in pairs)
        result[key]=dict(n=len(pairs),within_2s=count,metric=metric,metric_kind='RMSE' if dimensional else 'AARD_percent',cost=sum(.5*r['weight']*p['residual']**2 for r,p in pairs),zero_observations=sum(p['observed']==0 for r,p in pairs))
    return result


def fit_fold(name, normalized=False):
    s=SolventSpecification(OUT / 'study.toml')
    fitted=s.inputs['observations']['fitted']; allrows=fitted+s.inputs['observations']['comparisons']
    meta=read(OUT / 'pressure-identity.json')
    pressure=[r for r in allrows if r['identity'] in meta]
    if name.startswith('fit-'):
        strength=int(name.split('-')[1])
        train=[r for r in fitted if r['kind']!='partial_pressure']+[r for r in pressure if meta[r['identity']]['original'] or meta[r['identity']]['wt_percent']==strength]
    else:
        source=name.removeprefix('without-')
        train=[r for r in fitted if r['kind']!='partial_pressure']+[r for r in pressure if meta[r['identity']]['source']!=source]
    assert len({r['identity'] for r in train})==len(train)
    npressure=sum(r['identity'] in meta for r in train)
    if normalized:
        train=[dict(r,weight=r['weight']*47/npressure) if r['identity'] in meta else r for r in train]
    directory=OUT / (name+('-normalized' if normalized else ''))
    assert not (directory/'fit.json').exists(), 'No automatic repeat of a completed fit'
    directory.mkdir(exist_ok=True)
    write(directory/'membership.json',dict(fitted=[r['identity'] for r in train],held_out=[r['identity'] for r in pressure if r['identity'] not in {q['identity'] for q in train}],n_reactive_pressure=npressure,normalized=normalized))
    start=predictions(s,train)
    expected=sum(.5*r['weight']*p['residual']**2 for r,p in zip(train,start,strict=True))
    s.inputs['observations']['fitted']=train
    print(name,'fit starting',len(train),'rows',npressure,'reactive pressures',flush=True)
    native,report,parameters=s.fit()
    report['expected_initial_cost']=expected
    write(directory/'fit.json',report)
    assert abs(native.initial_cost-expected)<=1e-8*max(abs(expected),1)
    if not native.usable:
        print(name,'incomplete',report['message'],flush=True)
        return
    # Retain the complete fitted source document with existing physical-value mapping and native reaction conversion.
    import shared_evaluation as h
    from fit_campaign import fitted_parameter_values
    original=read(CHAIN)['information_coordinates']
    updates=fitted_parameter_values([q for q in original if 'reaction' not in q],native.physical[:len(native.chart.active)])
    for reaction,law in native.chart.reaction_laws.items():
        fields=dict(zip(('a_k','b','c_per_k'),reg.reaction_log10_reciprocal(law),strict=True)) if reaction=='R5' else dict(a=law.a-law.c*math.log(law.reference_temperature),b_k=law.b,c=law.c,d_per_k=law.d)
        updates.update({f'reaction:{reaction}:correlation:{k}':v for k,v in fields.items()})
    mapping=h.with_parameter_values(s.inputs['endpoint'],updates)
    write(directory/'parameters.json',mapping)
    apply(s,parameters,native.chart,mapping)
    replay=predictions(s,train)
    weighted=[math.sqrt(r['weight'])*p['residual'] for r,p in zip(train,replay,strict=True)]
    cost=sum(.5*v*v for v in weighted)
    assert abs(cost-native.final_cost)<=1e-8*max(abs(cost),1)
    assert max(abs(a-b) for a,b in zip(weighted,native.weighted_residuals,strict=True))<=1e-8
    allvalues=predictions(s,allrows)
    write(directory/'replay.json',dict(rows=allvalues,training_cost=cost,training_weighted_residuals=weighted,reactions=s.fitted_reactions(native.chart)))
    basevalues=read(OUT/'baseline.json')['rows']
    originalvalues=allvalues[:len(fitted)]
    before=statistics(s,fitted,basevalues);after=statistics(s,fitted,originalvalues)
    preservation={k:dict(before=before[k],after=after[k],passed=after[k]['within_2s']>=before[k]['within_2s'] and after[k]['metric']<=1.25*before[k]['metric']) for k in before}
    shares={label:{g:sum(.5*r['weight']*p['residual']**2 for r,p in zip(train,vals,strict=True) if r['group']==g)/total for g in {r['group'] for r in train}} for label,vals,total in [('start',start,expected),('fitted',replay,cost)]}
    write(directory/'assessment.json',dict(converged=report['status']=='converged',termination=report['status'],preservation=preservation,cost_shares=shares,baseline_cost_shares={g:sum(.5*r['weight']*p['residual']**2 for r,p in zip(fitted,basevalues,strict=True) if r['group']==g)/read(OUT/'baseline.json')['cost'] for g in {r['group'] for r in fitted}},replay_cost=cost,n_reactive_pressure=npressure))
    print(name,'converged',cost,'preservation',all(q['passed'] for q in preservation.values()),flush=True)


def binary():
    s=SolventSpecification(OUT/'study.toml');rows=[]
    for T in (313.15,333.15,353.15):
        for w in (.15,.30,.45):
            feed={'monoethanolamine':1.,'water':(1-w)/w*61.084/18.01528}
            x={k:v/sum(feed.values()) for k,v in feed.items()}
            problem=eq.bubble_point(T=T,feed=eq.Amounts(feed),liquid=eq.Phase('L',kind='liquid',support=list(feed)),vapor_support=list(feed))
            state=eq.solve_equilibrium(s.model,problem)
            assert state.success and state.requested_tolerance_met,state.message
            for P in (66660.,100000.,101330.):
                mixture=s.model.state(T,P=P,x=x,phase='liquid')
                for cid in feed:
                    index=s.model.component_ids.index(cid)
                    reference=s.model.state(T,P=P,x={cid:1.},phase='liquid')
                    rows.append(dict(T_K=T,wt_percent=100*w,P_Pa=P,bubble_P_Pa=state.pressure,metastable_liquid=P<state.pressure,species=cid,log_phi=mixture.log_fugacity_coefficient[index],log_gamma_pure_liquid=mixture.log_fugacity_coefficient[index]-reference.log_fugacity_coefficient[index],log_fugacity_activity=math.log(x[cid])+mixture.log_fugacity_coefficient[index]+math.log(P/100000.)))
    write(OUT/'unloaded-activities.json',rows)


def phase_job(task):
    name,index=task
    import shared_evaluation as h
    h.ENGINE_WHEEL_SHA256=WHEEL_SHA
    h.ENGINE_COMMIT='e6dae5c7353ae10e0aa2d8e46055847b9d64bbe4'
    h.verify_wheel()
    import phase_diagnosis_255 as d
    mapping=read(OUT/name/'parameters.json')
    old=read(d.OLD/'reported'/f'point-{index}.json')
    row={k:old[k] for k in ('index','temperature_K','loading','pressure_Pa')}
    directory=OUT/name/'phase';directory.mkdir(exist_ok=True)
    path=directory/f'point-{index}.json'
    d.f.family_job(mapping,d.e.request(mapping,313.15,.11),row,[],path)
    return d.reduce_state(read(path))


def phase(name):
    from concurrent.futures import ProcessPoolExecutor
    memory_kb=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))
    with ProcessPoolExecutor(min(os.cpu_count(),max(1,memory_kb//750000))) as pool:
        rows=list(pool.map(phase_job,[(name,i) for i in range(162)]))
    for path in (OUT/name/'phase').glob('*.json'):
        data=path.read_bytes();compressed=path.with_suffix('.json.gz')
        compressed.write_bytes(gzip.compress(data,mtime=0))
        assert gzip.decompress(compressed.read_bytes())==data
        path.unlink()
    print(name,'phase states',len(rows),'descent',sum(r['resolved']>0 for r in rows),'incomplete',sum(not r['complete'] for r in rows),flush=True)
    write(OUT/name/'phase-summary.json',dict(wt_percent=30,requested=162,completed=sum(r['complete'] for r in rows),detected_descent=sum(r['resolved']>0 for r in rows),incomplete=sum(not r['complete'] for r in rows),rows=rows))


def reduce():
    allrows=read(OUT/'baseline.json')['rows']+read(OUT/'baseline-comparisons.json');meta=read(OUT/'pressure-identity.json');reports=[]
    for directory in sorted(OUT.glob('*/assessment.json')):
        path=directory.parent;values=read(path/'replay.json')['rows'];assert all(r['identity']==v['identity'] for r,v in zip(allrows,values,strict=True));membership=read(path/'membership.json');held=set(membership['held_out']);scores={}
        for key,select in [('held-out',lambda m:True),('held-lowT',lambda m:m['T_K']<=333.15),('held-highT',lambda m:m['T_K']>333.15),('held-15wt',lambda m:m['wt_percent']==15),('held-45wt',lambda m:m['wt_percent']==45),('original47',lambda m:m['original'])]:
            pairs=[(r,p) for r,p in zip(allrows,values,strict=True) if r['identity'] in meta and (key=='original47' or r['identity'] in held) and select(meta[r['identity']])]
            scores[key]=dict(n=len(pairs),AARD_percent=100*sum(abs(p['value']/p['observed']-1) for r,p in pairs)/len(pairs),mean_log_error=sum(math.log(p['value']/p['observed']) for r,p in pairs)/len(pairs)) if pairs else dict(n=0)
        report=dict(name=path.name,scores=scores,**read(directory))
        report['preservation']={k.replace('common149 / pressure','common149 / addition_enthalpy'):v for k,v in report['preservation'].items()}
        totals=dict(baseline=read(OUT/'baseline.json')['cost'],start=read(path/'fit.json')['expected_initial_cost'],fitted=report['replay_cost'])
        report['objective_shares_by_observable']={}
        for label,total in totals.items():
            groups={k:p['after' if label=='fitted' else 'before']['cost']/total for k,p in report['preservation'].items()}
            groups['reactive CO2 pressure']=1-sum(groups.values())
            report['objective_shares_by_observable'][label]=groups
        reports.append(report)
    baseline_groups={}
    for p in allrows:
        m=meta.get(p['identity'])
        if m and m['wt_percent'] in (15,45):
            band='below 0.2' if m['loading']<.2 else '0.2 to below 0.4' if m['loading']<.4 else '0.4 and above'
            key=f"{m['wt_percent']} wt% / {m['T_K']} K / {band}"
            baseline_groups.setdefault(key,[]).append(p)
    write(OUT/'baseline-by-temperature-loading.json',{k:dict(n=len(v),AARD_percent=100*sum(abs(p['value']/p['observed']-1) for p in v)/len(v),mean_log_error=sum(math.log(p['value']/p['observed']) for p in v)/len(v)) for k,v in baseline_groups.items()})
    differences=[]
    matched=read(OUT/'matched-attribution.json')
    for row in matched:
        reference=next(r for r in matched if r['T']==row['T'] and r['loading']==row['loading'] and r['wt_percent']==30)
        a=next(q for q in row['terms'] if q['species']=='carbon-dioxide' and q['step']==2.5e-5)
        b=next(q for q in reference['terms'] if q['species']=='carbon-dioxide' and q['step']==2.5e-5)
        terms={t:a['contributions'][t]-b['contributions'][t] for t in a['contributions']}
        terms['minus_ln_Z']=a['log_phi']-b['log_phi']-sum(terms.values())+a['closure']-b['closure']
        dx=math.log(row['x'][0]/reference['x'][0]);dp=math.log(row['pressure']/reference['pressure'])
        differences.append(dict(T_K=row['T'],loading=row['loading'],wt_percent=row['wt_percent'],reference_wt_percent=30,chemical_potential_terms=terms,delta_log_phi=a['log_phi']-b['log_phi'],delta_log_x=dx,delta_log_pressure=dp,delta_log_fugacity_activity=dx+dp+a['log_phi']-b['log_phi']))
    write(OUT/'matched-attribution-differences.json',differences)
    write(OUT/'probe-summary.json',reports)
    candidates=[q for q in reports if q['converged'] and not q['name'].endswith('-normalized') and any(not p['passed'] for p in q['preservation'].values())]
    if candidates:
        rank=lambda q:(-sum(max(0,p['before']['within_2s']-p['after']['within_2s']) for p in q['preservation'].values()),-max(p['after']['metric']/p['before']['metric'] for p in q['preservation'].values()),q['name'])
        write(OUT/'normalization-selection.json',dict(fold=min(candidates,key=rank)['name'],reason='Largest count loss, then largest relative deterioration, then name; tests objective balance, not presumed causality'))
    print([(q['name'],q['scores']['held-out']) for q in reports],flush=True)


if __name__ == '__main__':
    verify()
    if sys.argv[1]=='fit':
        fit_fold(sys.argv[2],len(sys.argv)>3)
    elif sys.argv[1]=='phase':
        phase(sys.argv[2])
    else:
        {'prepare':prepare,'baseline':baseline,'sensitivity':sensitivity,'binary':binary,'reduce':reduce}[sys.argv[1]]()
