"""Issue 208: regenerate the declared finite searches; run from the checkout with python -I."""
import ast
from concurrent.futures import ProcessPoolExecutor
import hashlib
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import shutil
import sys
import time

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
ROOT = Path.cwd()
B = ROOT/'analyses/mea_parameter_bundle'
sys.path[:0] = [str(B/'scripts'), str(B/'calibration-misfit'), str(ROOT/'src')]
import final_evidence as f
import phase_extension_201 as extension
R, J, OUT = B/'results', B/'results/joint-recalibration-170', B/'results/engine-3e83e19c-phase'
FITS = {'A6': R/'engine-3e83e19c-refits/a6/run/fit/usable-budget-endpoint.json', 'A7': R/'selected-current-best-parameters.json'}
WORKERS = min(os.cpu_count(), int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1])//1_000_000)
load, write, table = f.campaign.load, f.s.write_json, f.table
REFERENCE = R/'phase-extension-201/run-2/phase_extension_201.py.txt'
STUDY = J/'amendment-7/fixed-study/study.py.txt'
PROBES = J/'amendment-6/selected-checks/phase-diagnosis/probes.py.txt'
OLD = R/'engine-3e83e19c-adoption'
EXTENSION = Path(extension.__file__)


def edited(text, changes):
    for old, new in changes:
        assert old in text, old
        text = text.replace(old, new)
    return text


def function(path, name):
    text = path.read_text()
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])+'\n'


def reference_job(job):
    T, loading, path, seed = job
    extension.bounded(lambda: reference(T, loading, path, seed), path, time.monotonic()+300)
    return load(path)


def references():
    root = OUT/'reference-pressure'
    (root/'inputs').mkdir(parents=True, exist_ok=False)
    for name in ('reference-runtime.json', 'engine-case7-parameters.json', 'engine-case7-reactions.json'):
        shutil.copyfile(R/'phase-extension-201/run-2/inputs'/name, root/'inputs'/name)
    source = edited(function(REFERENCE, 'reference'), [
        ('def reference(T, loading, path):', 'def reference(T, loading, path, seed=None):'),
        (next(line for line in REFERENCE.read_text().splitlines() if line.startswith('    seeds =')), '    seeds = [seed] if seed else []'),
        ("f.eq.Free(load(seeds[0])['result']['amounts'][0])", 'f.eq.Free()'),
        (' and 1 <= result.pressure <= 1e7', ''),
        ('admitted=admitted,', 'numerically_admitted=admitted, admitted=admitted and 1 <= result.pressure <= 1e7,'),
        ("cause='' if admitted else", "cause='' if admitted and 1 <= result.pressure <= 1e7 else")])
    namespace = dict(vars(extension), OUT=root)
    exec(compile(source, str(REFERENCE), 'exec'), namespace)
    globals()['reference'] = namespace['reference']
    declaration = load(R/'phase-extension-201/run-2/inputs/study.json')
    write(root/'declaration.json', dict(declaration, engine_source='/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/issue-350/seed_family.cpp', engine_source_sha256='f7bebb0888aff98c56db093be5058ad9db8228356f1991efacab1994fd7dd33b', effective_reference_sha256=hashlib.sha256(source.encode()).hexdigest()))
    ref_path = lambda kind,T,j: root/f'{kind}-{T}-{j}.json'
    with ProcessPoolExecutor(WORKERS, mp_context=multiprocessing.get_context('fork')) as pool:
        anchors = list(pool.map(reference_job, [(T,a,root/f'anchor-{i}.json',None) for i,(T,a,P) in enumerate(ANCHORS)]))
        assert all(r.get('numerically_admitted') and abs(r['result']['pressure']/a[2]-1)<=1e-8 for r,a in zip(anchors,ANCHORS,strict=True)), 'anchor failed: return to owner'
        cold = [(T,a,ref_path('original',T,j),None) for j,a in enumerate(LOADINGS[:8]) for T in (313.15,318.15,333.15)]
        cold += [(T,a,ref_path('cold',T,j),None) for T in (353.15,373.15) for j,a in enumerate(LOADINGS) if T==353.15 or j>0]
        values = list(pool.map(reference_job,cold))
        assert all(r.get('numerically_admitted') for r in values), 'cold reference/predecessor failed: return to owner'
        for T in (373.15,393.15):
            jobs = [(T,a,ref_path('extension',T,j),ref_path('cold',353.15 if T==373.15 or j==0 else 373.15,j)) for j,a in enumerate(LOADINGS)]
            values = list(pool.map(reference_job,jobs))
            assert all(r.get('numerically_admitted') for r in values), 'continued reference failed: return to owner'
    for j in range(9):
        shutil.copyfile(ref_path('cold',353.15,j),ref_path('extension',353.15,j))
    for family, temperatures in (('original-73',(313.15,318.15,333.15)), ('extension-81',extension.TEMPERATURES)):
        states, pressures = [], []
        for j,a in enumerate(LOADINGS[:8] if family=='original-73' else LOADINGS):
            for T in temperatures:
                path = ref_path('original' if family=='original-73' else 'extension',T,j)
                ref = load(path)
                for fraction in (1.,.5,.8,.95):
                    P = ref['result']['pressure']*fraction
                    row = dict(temperature_K=T,loading=a,fraction=fraction,pressure_Pa=P,reference_path=str(path.relative_to(OUT)),admitted=ref['admitted'] and 1<=P<=1e7,cause=ref['cause'],temperature_extrapolation=family=='extension-81')
                    pressures.append(row)
                    if fraction!=1.:
                        states.append(row)
        if family=='original-73':
            states.insert(0,dict(next(r for r in states if r['temperature_K']==318.15 and r['loading']==LOADINGS[4] and r['fraction']==.8),pressure_Pa=5918.5286,fraction='key'))
        states = [dict(row,index=i) for i,row in enumerate(states)]
        folder = OUT/family
        (folder/'inputs').mkdir(parents=True)
        (folder/'reference-pressure').mkdir()
        write(folder/'inputs/states.json',states)
        table(folder/'states.csv',states)
        table(folder/'reference-pressure/reference-pressures.csv',pressures)
        (folder/'family-points.txt').write_text(''.join(f'{s["loading"]!r} {s["temperature_K"]!r} {s["pressure_Pa"]!r}\n' for s in states))
        shutil.copyfile(folder/'family-points.txt',folder/'inputs/family-points.txt')
    print('reference pressures and both grids retained',flush=True)


def study(mode, fit):
    points = OUT/'original-73/family-points.txt'
    text = edited(STUDY.read_text(), [("output = root/'amendment-7/fixed-study'", f'output = Path({str(OUT/"original-73")!r})'),
        ("root/'amendment-6/inputs/revision-3/phase/family-points.txt'", f'Path({str(points)!r})'),
        ('6e1231d9506fd6dd9e965a64120ff952cebf1c4778da5d66cfb0f888e8b7f44b', f.s.sha256(points))])
    sys.argv = [str(STUDY),mode,fit,str(FITS[fit])]
    exec(compile(text,str(STUDY),'exec'), dict(__name__='issue208_study',__file__=str(STUDY)))


def searches(family, retained=False):
    os.environ['ISSUE208_FAMILY'] = family
    extension.OUT, extension.FITS = OUT/family, FITS
    extension.TEMPERATURES = (313.15,318.15,333.15) if family=='original-73' else (353.15,373.15,393.15)
    reduction = edited(function(EXTENSION,'reduce'), [('states=81','states=len(states)'),('scheduled_trials=729','scheduled_trials=9*len(states)'),('len(rows)==162 and len(trials)==1458','len(rows)==2*len(states) and len(trials)==18*len(states)'),('temperature_extrapolation=True',"temperature_extrapolation=state['temperature_extrapolation']")])
    exec(compile(reduction,str(EXTENSION),'exec'),vars(extension))
    tail = function(EXTENSION,'main').split('    commands = ',1)[1].split('    old = ',1)[0]
    text = 'def run_searches():\n    states = load(OUT/"inputs/states.json")\n    START, cpu_start = time.monotonic(), cpu_used()\n    commands = '+tail
    text = edited(text,[('states=27,scheduled_trials=243',"states=sum(r['temperature_K']==T for r in states),scheduled_trials=9*sum(r['temperature_K']==T for r in states)")])
    if family=='original-73':
        text = edited(text,[("[[mode,f'{fit}:{T}'] for fit in FITS for T in TEMPERATURES for mode in ['screen']]", "[['screen-original',fit] for fit in FITS]")])
        if retained:
            assert all(len(list((extension.OUT/fit).glob('point-*.json')))==73 for fit in FITS)
            text = edited(text,[("stop = supervise(commands,'screen',START,cpu_start)", 'stop = None')])
    else:
        for fit in FITS:
            (extension.OUT/fit).mkdir()
            write(extension.OUT/fit/'fixed-parameters.json',f.s.parameter_mapping(FITS[fit]))
    exec(compile(text,str(EXTENSION),'exec'),vars(extension))
    extension.run_searches()
    rows, trials = load(extension.OUT/'A6/reduction.json')+load(extension.OUT/'A7/reduction.json'), list(f.csv.DictReader((extension.OUT/'trials.csv').open()))
    outcomes = []
    for fit in FITS:
        for T in extension.TEMPERATURES:
            states = [r for r in rows if r['record']==fit and r['temperature_K']==T]
            returned = [t for t in trials if t['record']==fit and float(t['temperature_K'])==T and t['status']=='returned']
            completed = sum(r['admitted'] and r['final_success'] and r['missing_trials']==r['failed_trial_optimizers']==r['trial_unresolved']==0 for r in states)
            outcomes.append(dict(run='issue-208',record=fit,temperature_K=T,scheduled_states=len(states),scheduled_trials=9*len(states),completed=completed,unresolved=sum(r['admitted'] and r['final_success'] for r in states)-completed,unavailable_pressure=sum(not r['admitted'] for r in states),unavailable_numerical=sum(r['parent_numerical_failure'] for r in states),returned_trials=len(returned),resolved_trials=sum(t['resolved_descent']=='True' for t in returned),descent_states=sum(r['resolved_trials']>0 for r in states),passed=sum(r['classification'].startswith('passed') for r in states)))
    table(extension.OUT/'outcomes-by-temperature.csv',outcomes)


def supplement():
    folder = OUT/'A6-supplement-splits'
    folder.mkdir()
    text = PROBES.read_text()
    selection = text[text.index('        chosen = [trials[0]]'):text.index('        rows=[]')]
    text = edited(text,[("out = base/'selected-checks/phase-diagnosis'",f'out = Path({str(folder)!r})'),
        ("record = base/'joint-mea-water/held/fit/usable-budget-endpoint.json'",f'record = Path({str(FITS["A6"])!r})'),
        ("base/f'selected-checks/phase-family/point-{index}.json'",f'Path({str(OUT/"original-73/A6")!r})/f"point-{{index}}.json"'),
        (selection,"        chosen = [(i,t) for name in ('positive-neutral-base','near-pure-2') for i,t in trials if t['phase']['kind']=='liquid' and t['seed']==name]\n        f.s.write_json(out/f'seed-availability-{index}.json',dict(index=index,seeds=[t['seed'] for i,t in chosen],complete=len(chosen)==2))\n")])
    sys.argv = [str(PROBES),'split','21','63','70']
    exec(compile(text,str(PROBES),'exec'),dict(__name__='issue208_supplement',__file__=str(PROBES)))


def density_export():
    spec = load(J/'amendment-6/joint-mea-water/held/fit-spec.json')
    replay = {r['target']:r for r in load(OUT/'original-73/A6/full-replay.json')}
    metadata = {r['id']:r for r in spec['direct_rows'] if r['id'] in spec['loaded_density_ids']}
    assert len(metadata)==47 and len(replay)==307
    table(OUT/'original-73/A6/loaded-density-errors.csv',[dict(id=k,source=r['source_locator'],T_K=r['T_K'],P_Pa=r['P_Pa'],loading=r['analytical_feed']['carbon-dioxide']/r['analytical_feed']['monoethanolamine'],observed_kg_m3=replay[k]['observed'],s_kg_m3=replay[k]['scale'],predicted_kg_m3=replay[k]['predicted'],error_kg_m3=replay[k]['predicted']-replay[k]['observed'],error_over_s=replay[k]['residual']) for k,r in metadata.items()])


def comparisons():
    import fit_observations as observations
    _, targets = observations.stage6_rows(load(J/'amendment-6/joint-mea-water/held/fit-spec.json'),f.s.parameter_mapping(FITS['A6']))
    units = {r['id']:{'AdditionEnthalpy':'J/mol CO2','PartialPressure':'Pa','PhaseMoleFraction':'mol/mol','amount_ratio':'mol/mol','equilibrium_isobaric_heat_capacity':'J/(mol K)','mole_fraction':'mol/mol','phase_density':'kg/m3','pressure':'Pa','temperature':'K'}[r['quantity']] for r,_ in targets}
    exec(compile(function(OLD/'adopt.py.txt','leaves'),'adopt.py.txt','exec'),globals())
    rows = []
    phases = lambda r:{p['identity']:{'amount_mol':p['amount_mol'],'molar_density_mol_m3':p['molar_density_mol_m3'],'x':dict(zip(p['support'],p['mole_fractions'],strict=True)),'kind':p['role'],'support':p['support']} for p in r.get('phases',[])}
    admission = lambda r:r.get('success',False) and r['requested_tolerance_met'] and max(map(abs,r.get('raw_residuals',[math.inf])))<=1e-10 and r['reduced_hessian_minimum']>0 and all(v>0 for v in r['amounts']) and all(v>0 for v in r.get('pressure_density_derivatives',[]))
    def compare(group, identity, old, new, limit=0., unit='categorical', diagnostic=False):
        a,b = dict(leaves(old)),dict(leaves(new))
        for k in sorted(a.keys()|b.keys()):
            o,n = a.get(k,'absent'),b.get(k,'absent')
            numeric = type(o) in (int,float) and type(n) in (int,float)
            absolute = abs(n-o) if numeric else None
            delta = absolute/max(abs(o),abs(n),1e-300) if numeric and math.isfinite(absolute) else None
            passed = (delta is not None and (abs(n)<=1e-300 if o==0 else delta<=limit)) if numeric else o==n
            quantity_unit = 'mol' if 'amount_mol' in k else 'mol/m3' if 'molar_density_mol_m3' in k else 'mol/mol supported species' if '/x/' in k else unit
            if group=='replay score':
                quantity_unit = 'kg/m3' if 'co2_free' in k else '%' if 'AARD_pct' in k else 'kJ/mol CO2' if 'vinjarapu_rmse' in k else 'dimensionless'
            rows.append(dict(group=group,identity=identity+k,old=o,new=n,absolute_difference=absolute,unit=quantity_unit,delta=delta,limit=limit,diagnostic=diagnostic,unchanged=passed,owner_return=not passed and not diagnostic))
    def keyed(items, key):
        result = {key(r):r for r in items}
        assert len(result)==len(items), 'duplicate scientific identity'
        return result
    csv_rows = lambda p:list(f.csv.DictReader(p.open()))
    for family, oldroot in (('original-73',OLD),('extension-81',R/'phase-extension-201/run-3')):
        states = load(OUT/family/'inputs/states.json')
        oldpoints = [list(map(float,line.split())) for line in (J/'amendment-6/inputs/revision-3/phase/family-points.txt').read_text().splitlines()] if family=='original-73' else [[float(r[k]) for k in ('loading','temperature_K','pressure_Pa')] for r in load(oldroot/'inputs/states.json')]
        for state,oldpoint in zip(states,oldpoints,strict=True):
            i=state['index']; identity=f'{family}/{i}/T={state["temperature_K"]}/a={state["loading"]}/f={state["fraction"]}'
            assert [state['loading'],state['temperature_K']]==oldpoint[:2]
            compare('exclusion',identity,True if family=='original-73' else load(oldroot/'inputs/states.json')[i]['admitted'],state['admitted'])
            compare('imposed pressure',identity,oldpoint[2],state['pressure_Pa'],1e-8,'Pa')
            if state['fraction']==.5:
                compare('P*',identity,oldpoint[2]/.5,state['pressure_Pa']/.5,1e-8,'Pa')
            for fit in FITS:
                o,n = (load(p/fit/f'point-{i}.json') for p in (oldroot,OUT/family))
                status = lambda r:dict(classification=f.phase_classification(r),success=r.get('final',{}).get('success',False),requested_tolerance_met=r.get('final',{}).get('requested_tolerance_met',False),completed=[v['completed'] for v in r.get('stability',[])],failure=bool(r.get('failure')),interrupted=r.get('timing',{}).get('interrupted',False))
                compare('state outcomes',f'{fit}/{identity}',status(o),status(n))
                trials = [keyed([t for s in r.get('stability',[]) for t in s['trials']],lambda t:(t['phase']['kind'],tuple(t['phase']['support']),t['seed'])) for r in (o,n)]
                compare('trial identities',f'{fit}/{identity}',sorted(trials[0]),sorted(trials[1]))
                for key in trials[0].keys()&trials[1].keys():
                    pick = lambda t:dict(success=t['optimizer']['success'],evidence=t['evidence'],resolved_descent=t['resolved_descent'])
                    compare('trial outcomes',f'{fit}/{identity}/{key}',pick(trials[0][key]),pick(trials[1][key]))
                    compare('trial quantities',f'{fit}/{identity}/{key}',trials[0][key]['quantities'],trials[1][key]['quantities'],diagnostic=True,unit='native quantity identified by leaf')
        if family=='extension-81':
            for name,keys in (('outcomes-by-temperature.csv',('record','temperature_K')),('split-confirmations.csv',('record','index','native_trial_index','phase_kind','support','seed'))):
                sides = [keyed(csv_rows(p/name),lambda r:tuple(r[k] for k in keys)) for p in (oldroot,OUT/family)]
                compare('reduction identities',name,sorted(sides[0]),sorted(sides[1]))
                for key in sides[0].keys()&sides[1].keys():
                    if name.startswith('outcomes'):
                        compare('extension counts',str(key),{k:v for k,v in sides[0][key].items() if k!='run'},{k:v for k,v in sides[1][key].items() if k!='run'})
                    else:
                        compare('confirmation outcomes',str(key),{k:sides[0][key][k] for k in ('confirmed','representative')},{k:sides[1][key][k] for k in ('confirmed','representative')})
                        o,n=(load(p/sides[j][key]['path']) for j,p in enumerate((oldroot,OUT/family)))
                        compare('confirmation Gibbs',str(key),{k:o.get(k) for k in ('delta_G_over_RT','delta_G_J')},{k:n.get(k) for k in ('delta_G_over_RT','delta_G_J')},1e-6,'G/(RT) feed basis; J as named',not o.get('confirmed'))
                        compare('confirmation phases',str(key),phases(o.get('result',{})),phases(n.get('result',{})),1e-6,diagnostic=not o.get('confirmed'))
                        compare('confirmation diagnostics',str(key),o.get('result'),n.get('result'),diagnostic=True,unit='native quantity identified by leaf')
        table(OUT/family/'comparison-state-identities.csv',[r for r in rows if r['group']=='state outcomes' and family in r['identity']])
    for i in (21,63,70):
        sides = [keyed(load(p/'A6-supplement-splits'/f'split-seeded-{i}.json'),lambda r:r['seed']) for p in (OLD,OUT)]
        compare('supplement identities',str(i),sorted(sides[0]),sorted(sides[1]))
        for seed in sides[0].keys()&sides[1].keys():
            o,n=(s[seed] for s in sides); identity=f'{i}/{seed}'
            compare('supplement admission',identity,dict(success=o['result']['success'],tolerance=o['result']['requested_tolerance_met'],admitted=admission(o['result'])),dict(success=n['result']['success'],tolerance=n['result']['requested_tolerance_met'],admitted=admission(n['result'])))
            for field in ('delta_G_over_RT_vs_original','delta_G_over_RT_vs_single_liquid'):
                compare('supplement Gibbs',identity+'/'+field,o.get(field),n.get(field),1e-6,'G/(RT) on feed basis',not o['result']['success'])
            compare('supplement phases',identity,phases(o['result']),phases(n['result']),1e-6,'mol; mol/m3; mole fraction as named',not o['result']['success'])
            compare('supplement diagnostics',identity,o['result'],n['result'],diagnostic=True,unit='native quantity identified by leaf')
    sides = [keyed(load(p/'A6/full-replay.json'),lambda r:r['target']) for p in (OLD,OUT/'original-73')]
    assert sides[0].keys()==sides[1].keys() and len(sides[1])==307
    for key in sides[0]:
        for field in ('observed','scale','weight','form','status','requested_tolerance_met','predicted','residual','weighted_residual','cost'):
            compare('replay',key+'/'+field,sides[0][key][field],sides[1][key][field],1e-10,units[key] if field in ('predicted','observed') or field=='scale' and sides[0][key]['form']!='LogRatio' else 'dimensionless')
    for key in load(J/'amendment-6/joint-mea-water/held/fit-spec.json')['loaded_density_ids']:
        compare('loaded density errors',key,*[s[key]['predicted']-s[key]['observed'] for s in sides],limit=1e-10,unit='kg/m3')
    score = lambda r:dict({k:v for k,v in r.items() if k not in ('label','parameter_sha256')},co2_free_max_abs_error_kg_m3=max(map(abs,r['co2_free_errors'].values())))
    compare('replay score','A6',*(score(load(p/'A6/score.json')) for p in (OLD,OUT/'original-73')),limit=1e-10,unit='score field unit')
    compare('Table S23','comparison fit / Arcis RMSE',*[load(R/'engine-3e83e19c-refits/displays/summary.json')['arcis']['comparison']['RMSE_kJ_mol']]*2,limit=1e-10,unit='kJ/mol CO2')
    rows[-1].update(old_printed=f'{rows[-1]["old"]:.2f}',new_printed=f'{rows[-1]["new"]:.2f}',source='analyses/mea_parameter_bundle/results/engine-3e83e19c-refits/displays/summary.json',source_sha256=f.s.sha256(R/'engine-3e83e19c-refits/displays/summary.json'))
    table(OUT/'old-new-comparison.csv',rows)
    write(OUT/'comparison-summary.json',{group:dict(rows=len(part),owner_returns=sum(r['owner_return'] for r in part),largest=max((r for r in part if r['delta'] is not None),key=lambda r:r['delta'],default=None)) for group in sorted({r['group'] for r in rows}) for part in [[r for r in rows if r['group']==group]]})
    combined = [dict(r,family=family,combined_index=r['index']+(73 if family=='extension-81' else 0)) for family in ('original-73','extension-81') for fit in FITS for r in load(OUT/family/fit/'reduction.json')]
    assert len(combined)==308
    for row in combined:
        point = load(OUT/row['family']/row['record']/f'point-{row["index"]}.json')
        trials = [t for s in point.get('stability',[]) for t in s['trials']]
        row.update(evidence=sorted({t['evidence'] for t in trials}),minimum_resolved_tpd_over_rt=min((t['quantities']['tpd_over_rt'] for t in trials if t['resolved_descent']),default=None),minimum_split_delta_g_over_rt=min((t['quantities']['split_delta_g_over_rt'] for t in trials if t['resolved_descent']),default=None))
    table(OUT/'phase-family-combined.csv',combined)


def provenance():
    producers = [Path(__file__),EXTENSION,Path(f.__file__),REFERENCE,STUDY,PROBES,OLD/'adopt.py.txt']
    inputs = [*FITS.values(),*sorted((OUT/'reference-pressure/inputs').iterdir()),J/'amendment-6/joint-mea-water/held/fit-spec.json',R/'engine-3e83e19c-refits/displays/summary.json']
    base = dict(engine_commit=f.s.ENGINE_COMMIT,wheel_path=str(f.s.installed_wheel()),wheel_sha256=f.s.sha256(f.s.installed_wheel()),interpreter=sys.executable,environment='main checkout verified environment; no worktree environment',packages={k:importlib.metadata.version(k) for k in ('epcsaft','numpy','scipy')},linear_solver=f.epcsaft._core.linear_solver(),numerical_library_threads=1,reference_pool_sizing='min(os.cpu_count(), MemAvailable_kib//1000000)',final_tree_producers={str(p.relative_to(ROOT)):f.s.sha256(p) for p in producers},executions=load(OUT/'execution-source-recovery.json')['executions'],inputs={str(p.relative_to(ROOT)):f.s.sha256(p) for p in inputs})
    write(OUT/'provenance.json',base)
    for family in ('original-73','extension-81'):
        for fit,record in FITS.items():
            mapping = f.s.parameter_mapping(record)
            binding = dict(parameter_path=str(record.relative_to(ROOT)),parameter_document_sha256=f.s.sha256(record),runtime_mapping_sha256=hashlib.sha256(json.dumps(mapping,sort_keys=True).encode()).hexdigest(),states_sha256=f.s.sha256(OUT/family/'inputs/states.json'),points_sha256=f.s.sha256(OUT/family/'family-points.txt'))
            write(OUT/family/fit/'provenance.json',dict(base,**binding))
            for path in (OUT/family/fit).glob('point-*.json'):
                write(path,dict(load(path),parameter_binding=binding))
            for path in (OUT/family/fit).glob('split-seeded-*.json'):
                parent = OUT/family/fit/f'point-{load(path)["index"]}.json'
                write(path,dict(load(path),parameter_binding=binding,parent_path=str(parent.relative_to(OUT)),parent_sha256=f.s.sha256(parent)))
    for path in (OUT/'A6-supplement-splits').glob('split-seeded-*.json'):
        rows = load(path)
        for row in rows:
            parent = OUT/'original-73/A6'/f'point-{row["index"]}.json'
            row.update(parameter_document_sha256=f.s.sha256(FITS['A6']),runtime_mapping_sha256=load(OUT/'original-73/A6/provenance.json')['runtime_mapping_sha256'],parent_path=str(parent.relative_to(OUT)),parent_sha256=f.s.sha256(parent))
        write(path,rows)
    write(OUT/'A6-supplement-splits/provenance.json',dict(load(OUT/'original-73/A6/provenance.json'),producer_sha256=f.s.sha256(PROBES)))
    write(OUT/'original-73/A6/loaded-density-provenance.json',dict(load(OUT/'original-73/A6/provenance.json'),rows=47,error_over_s='unweighted replay residual; observations and scales from declared direct_rows'))
    score = load(OUT/'original-73/A6/score.json')
    write(OUT/'original-73/A6/score.json',dict(score,co2_free_max_abs_error_kg_m3=max(map(abs,score['co2_free_errors'].values()))))


ANCHORS = ((313.15,1e-5,4825.512054880343),(318.15,.25557798094241313,7398.160760169702),(333.15,.5,76573.56849304347))
LOADINGS = (1e-5,.05,.1,.2,.25557798094241313,.3,.4,.5,.6)
if __name__=='__main__':
    f.s.verify_wheel()
    assert [f.s.sha256(p) for p in FITS.values()]==['968ed8c035e23011687edfa502d31a935545abadfca87b6261a498e0b14569a4','e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e']
    # The existing supervisor starts this adapter's children and preserves its stage ceilings.
    extension.__file__ = str(Path(__file__).resolve())
    supervisor = edited(function(EXTENSION,'supervise'), [('sys.executable, __file__', "sys.executable, '-I', __file__")])
    exec(compile(supervisor,str(EXTENSION),'exec'),vars(extension))
    mode = sys.argv[1] if len(sys.argv)>1 else 'references'
    write(OUT/'execution-source-captures'/('-'.join(sys.argv[1:3]) or 'references'),dict(argv=sys.argv,captured_unix_s=time.time(),sources={str(p.relative_to(ROOT)):f.s.sha256(p) for p in (Path(__file__),EXTENSION,Path(f.__file__),REFERENCE,STUDY,PROBES,OLD/'adopt.py.txt')}))
    if mode=='references':
        references()
    elif mode in ('original-73','extension-81'):
        searches(mode)
    elif mode=='original-retained':
        searches('original-73',retained=True)
    elif mode=='screen-original':
        study('screen',sys.argv[2])
    elif mode=='score':
        study('score','A6')
        density_export()
    elif mode=='supplement':
        supplement()
    elif mode=='compare':
        comparisons()
    elif mode=='provenance':
        provenance()
    else:
        extension.OUT, extension.FITS = OUT/os.environ.get('ISSUE208_FAMILY','extension-81'), FITS
        extension.chain(mode,sys.argv[2],float(sys.argv[3]))
