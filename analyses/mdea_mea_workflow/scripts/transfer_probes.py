"""Issue 267: bounded MDEA pressure, heat and shared-interaction diagnostics."""
import os
for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
import concurrent.futures as futures
import copy, csv, gzip, hashlib, json, math, multiprocessing, sys, zipfile
from pathlib import Path
AN = Path(__file__).resolve().parents[1]
ROOT = AN.parents[1]
OUT = AN / 'results/transfer-267'
MODE = sys.argv[1]
sys.path[:0] = [str(ROOT/'src'), str(AN/'scripts')]
import epcsaft
from epcsaft import regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable


def write(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(jsonable(value), indent=2, allow_nan=False)+'\n').encode()
    if len(data) > 5_000_000:
        path = path.with_suffix(path.suffix+'.gz'); data = gzip.compress(data, mtime=0)
    path.write_bytes(data)


def read(path):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else json.loads(gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes()))


def pool(fn, jobs):
    if not jobs: return []
    available = next(int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    with futures.ProcessPoolExecutor(max_workers=min(os.cpu_count(), len(jobs), max(1, available//268435456)), mp_context=multiprocessing.get_context('fork')) as executor:
        return list(executor.map(fn, jobs))


def pair(document):
    return next(c for p in document['pairs'] if {p['component_id_a'], p['component_id_b']} == {'water','bicarbonate-anion'} for c in p['coefficients'] if c['family']=='k_ij')


def metric(records):
    valid = [r for r in records if r.get('relative_error') is not None]
    complete = len(valid)==len(records) and bool(records)
    return dict(rows=len(records), available=len(valid), AARD_percent=100*sum(abs(r['relative_error']) for r in valid)/len(valid) if complete else None,
                bias_percent=100*sum(r['relative_error'] for r in valid)/len(valid) if complete else None,
                mean_log_ratio=sum(math.log1p(r['relative_error']) for r in valid)/len(valid) if complete else None,
                underpredictions=sum(r['relative_error']<0 for r in valid))


def pressure(index):
    group, row, prob, observed = PRESSURE_JOBS[index]
    result = dict(group=group, row=row, observed_Pa=observed)
    try:
        state = s.eq.solve_equilibrium(s.model, prob)
        result.update({k: jsonable(getattr(state,k)) for k in ('success','requested_tolerance_met','message','pressure','residuals','mole_fractions','amounts')})
        if state.success and state.requested_tolerance_met:
            value = state.pressure*state.phase_mole_fractions(1)[list(s.params.component_ids).index(s.j.C)]
            result.update(predicted_Pa=value, relative_error=value/observed-1)
    except Exception as error: result['message']=f'{type(error).__name__}: {error}'
    return result


def pressure_jobs():
    jobs=[]
    for row in s.j.rows('Xiao2018_context.csv'):
        jobs.append(('Xiao',row,s.j.problem(float(row['temperature_K']),101000.,s.j.water(float(row['unloaded_MDEA_mass_fraction'])),float(row['alpha_exp']),True),float(row['p_CO2_kPa'])*1000))
    for row in s.j.rows('Ermatchkov_2006_CO2_MDEA_partial_pressure.csv'):
        m=float(row['m_MDEA_mol_per_kg_H2O'])
        if m*.1191622/(1+m*.1191622)>.49: continue
        jobs.append(('Ermatchkov',row,s.j.problem(float(row['temperature_K']),max(1e5,float(row['p_CO2_kPa'])*1000),1/.01801528/m,float(row['m_CO2_mol_per_kg_H2O'])/m,True),float(row['p_CO2_kPa'])*1000))
    assert len(jobs)==108
    return jobs


def assess(document, name, baseline=False):
    shared={'water','carbon-dioxide','hydronium-cation','hydroxide-anion','bicarbonate-anion','carbonate-anion'}
    base=read(AN/'results/stage2-capped/A3/endpoint.json')
    assert [c for c in document['components'] if c['component_id'] in shared]==[c for c in base['components'] if c['component_id'] in shared]
    frozen=copy.deepcopy(document); pair(frozen)['value']['magnitude']=pair(base)['value']['magnitude']
    assert [p for p in frozen['pairs'] if {p['component_id_a'],p['component_id_b']}<=shared]==[p for p in base['pairs'] if {p['component_id_a'],p['component_id_b']}<=shared]
    s.setup(document)
    global PRESSURE_JOBS
    jobs=PRESSURE_JOBS=pressure_jobs(); records=pool(pressure,list(range(len(jobs))))
    write(f'{name}/pressure.json',records)
    if baseline:
        old=read(AN/f'results/context-sources/{name}-Xiao.json')
        previous=[r['predicted_p_CO2_Pa'] for r in old]
        previous += [r['predicted'] for r in read(AN/f'results/stage2-capped/{name}/comparisons.json') if r['group']=='Ermatchkov' and r['row']['mass_fraction']<=.49]
        assert all(abs(r['predicted_Pa']-v)<=1e-8*max(1,abs(v)) for r,v in zip(records,previous,strict=True))
    s.phase_jobs=[(f'{group}:{i}',prob) for i,(group,row,prob,observed) in enumerate(jobs)]
    phases=pool(s.phase,list(range(len(jobs))))
    write(f'{name}/pressure-phase.json',phases)
    summary=dict(shared_k=pair(document)['value']['magnitude'], pressure={g:metric([r for r in records if r['group']==g]) for g in ('Xiao','Ermatchkov')},phase=s.phase_summary(phases))
    write(f'{name}/summary.json',summary); print(name,summary,flush=True)


def prediction(record): return SPEC.prediction(record)


if MODE=='present':
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=[]
    for path in sorted(OUT.glob('*/summary.json')):
        result=read(path)
        if 'pressure' not in result: continue
        for source,values in result['pressure'].items():
            rows.append(dict(probe=path.parent.name,source=source,k=result['shared_k'],**values))
    with (OUT/'pressure-summary.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True)
    names=list(dict.fromkeys(r['probe'] for r in rows))
    for i,source in enumerate(('Xiao','Ermatchkov')):
        for j,key in enumerate(('AARD_percent','bias_percent')):
            ax=axes[i,j]
            for n,name in enumerate(names):
                r=next(r for r in rows if r['probe']==name and r['source']==source)
                ax.plot(n,r[key],marker='o' if name.startswith('A') else 's',color='#0072B2' if name.startswith('A') else '#D55E00')
            ax.axhline(0,color='0.5',linewidth=.7); ax.set_ylabel(source+' '+('AARD (%)' if j==0 else 'signed mean error (%)'))
            if source=='Ermatchkov' and j==0: ax.axhline(24.2,color='0.3',linestyle=':',label='24.2% repository criterion'); ax.legend(fontsize=8)
            ax.set_xticks(range(len(names)),names,rotation=60,ha='right'); ax.grid(axis='y',alpha=.2)
    fig.suptitle('Lower bicarbonate–water k improves Xiao but has different Ermatchkov consequences')
    fig.tight_layout(); fig.savefig(OUT/'pressure-comparison.png',dpi=180); plt.close(fig)
    raise SystemExit(0)


if MODE=='latest-heat':
    wheel=Path(sys.argv[2]); digest=hashlib.sha256(wheel.read_bytes()).hexdigest()
elif MODE=='mea':
    wheel=Path('/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl')
    digest='0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804'
else:
    wheel=Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-d5138209/epcsaft-1.0.0-cp313-cp313-manylinux_2_39_x86_64.whl')
    digest='ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'
assert hashlib.sha256(wheel.read_bytes()).hexdigest()==digest
with zipfile.ZipFile(wheel) as archive:
    for name in archive.namelist():
        if name.startswith(('epcsaft/','epcsaft.libs/')) and not name.endswith('/'):
            assert archive.read(name)==(Path(epcsaft.__file__).parent.parent/name).read_bytes(),name
write(f'runtime-{MODE}.json',dict(wheel=str(wheel),sha256=digest,installed_files_byte_identical=True,python=sys.version))
if MODE=='latest-heat':
    results=[]
    for case in read(OUT/'heat-reproducer.json')['cases']:
        SPEC=SolventSpecification(AN.parent/'solvent_specification_mdea'/f"{case['label']}.toml")
        record=copy.deepcopy(next(r for r in SPEC.inputs['observations']['comparisons'] if r['group']=='Merkley-outside' and float(r['row']['temperature_K'])==case['T_K'] and r['row']['MDEA_mass_percent']=='60'))
        record['arguments']['loading_grid']=case['grid']
        pred=reg.predict(SPEC.model,SPEC.observation(record))
        results.append(dict(label=case['label'],T_K=case['T_K'],grid=case['grid'],**{k:jsonable(getattr(pred,k,None)) for k in ('status','message','value','requested_tolerance_met','saturation_loading','endpoint_loading')}))
        write('heat-latest.json',dict(commit=sys.argv[3],wheel_sha256=digest,cases=results))
        print(case['label'],case['T_K'],len(case['grid']),pred.status.name,pred.value,pred.message,flush=True)
elif MODE!='mea':
    import refit_capped as owner
    s=owner.s
    s.write=lambda name,value:write(name,value)
    s.poolmap=pool
    original=read(AN/'results/stage2-capped/A3/endpoint.json')
    base_k=pair(original)['value']['magnitude']
    if MODE=='heat':
        results=[]
        for label,T in [('B1',333.15),('A3',333.15),('B1',388.71)]:
            s.setup(read(AN/f'results/stage2-capped/{label}/endpoint.json'))
            row=next(r for r in s.j.rows('Merkley1987_loading_points.csv') if float(r['temperature_K'])==T and r['MDEA_mass_percent']=='60')
            for count in (30,60,120):
                grid=[.05+i*1.45/(count-1) for i in range(count)]
                if count==30: grid=[.05*i for i in range(1,31)]
                initial=s.j.problem(T,1121000.,s.j.water(.6),0.)
                item=reg.saturation_capped_addition_enthalpy(s.params,initial,s.j.problem(T,1121000.,s.j.water(.6),.5,True),{s.j.C:1.},basis_amount=1.,loading_cap=float(row['alpha_LP_mol_CO2_per_mol_MDEA']),loading_bounds=(.05,1.5),loading_grid=grid,T=T,P=1121000.,phase='vapor',observed=0.,form='difference',scale=1.)
                pred=reg.predict(s.model,item)
                results.append(dict(label=label,T_K=T,wt_percent=60,P_Pa=1121000,grid=grid,**{k:jsonable(getattr(pred,k,None)) for k in ('status','message','value','requested_tolerance_met','saturation_loading','endpoint_loading')}))
                write('heat.json',results); print(label,T,count,results[-1]['status'],results[-1]['value'],results[-1]['message'],flush=True)
    elif MODE=='pressure':
        for label in ('A3','B1'):
            document=read(AN/f'results/stage2-capped/{label}/endpoint.json')
            for suffix,k in [('',base_k),('-kminus',base_k-.1),('-kplus',base_k+.1)]:
                candidate=copy.deepcopy(document); pair(candidate)['value']['magnitude']=k
                assess(candidate,label+suffix,baseline=not suffix)
            assess(read(AN/f'results/stage2-capped/{label}/followup-bicarbonate/endpoint.json'),label+'-released')
    elif MODE=='fit':
        for label in ('A3','B1'):
            document=read(AN/f'results/stage2-capped/{label}/endpoint.json'); s.setup(document)
            _,decl=s.j.coordinates(s.params,document,label[0]); bounds=[q['bounds'] for q in decl]
            bounds[2]=bounds[3]=[-.6,.6]; bounds[5]=[-1.2,1.]; bounds[8]=[1.5,8.]
            candidate,result=s.fit_document(document,label[0],bounds,label+'-bounds')
            if result['usable'] and result['status']=='converged':
                interaction=next(p for p in candidate['pairs'] if {p['component_id_a'],p['component_id_b']}=={s.j.H,s.j.W})
                coefficients={c['family']:c['value']['magnitude'] for c in interaction['coefficients']}
                extrema=[coefficients['k_ij']+coefficients['k_ij_reciprocal_temperature_slope']*(1/T-1/313.15) for T in (293.15,395.)]
                write(label+'-bounds/attraction.json',dict(temperature_endpoints_K=[293.15,395.],k_values=extrema,admitted=max(extrema)<=1.))
                if max(extrema)>1.: continue
                assess(candidate,label+'-bounds')
                s.setup(candidate); meta,items,weights=s.j.objective(s.params)
                values=[reg.predict(s.model,item) for item in items]
                residuals=[math.sqrt(w)*p.residual for w,p in zip(weights,values,strict=True)]
                assert max(abs(a-b) for a,b in zip(residuals,result['weighted_residuals'],strict=True))<=1e-8
                assert abs(sum(.5*v*v for v in residuals)/result['final_cost']-1)<=1e-8
                write(label+'-bounds/replay.json',[dict(meta=m,value=p.value,residual=p.residual,status=p.status.name) for m,p in zip(meta,values,strict=True)])
                s.search_document(candidate,label+'-bounds')
    else: raise ValueError(MODE)
else:
    mea=ROOT/'analyses/solvent_specification_mea'
    values={pair(read(AN/'results/stage2-capped/A3/endpoint.json'))['value']['magnitude']}
    base=next(iter(values)); values.update((base-.1,base+.1))
    values.update(pair(read(AN/f'results/stage2-capped/{label}/followup-bicarbonate/endpoint.json'))['value']['magnitude'] for label in ('A3','B1'))
    for k in [base,*sorted(values-{base})]:
        SPEC=SolventSpecification(mea/'MEA.toml')
        document=copy.deepcopy(SPEC.inputs['endpoint']); pair(document)['value']['magnitude']=k
        SPEC.parameters=epcsaft.Parameters.from_mapping(document)
        SPEC.model=epcsaft.Mixture(SPEC.parameters,thermochemistry=SPEC.thermal)
        rows=SPEC.inputs['observations']['fitted']; assert len(rows)==307
        records=pool(prediction,rows)
        if k==base:
            reference=read(mea/'inputs/reference.json')
            assert all(p['status']=='Available' and p['requested_tolerance_met'] and abs(p['value']-r['predicted'])<=1e-10*max(1,abs(r['predicted'])) for p,r in zip(records,reference,strict=True))
            assert abs(sum(.5*r['weight']*p['residual']**2 for r,p in zip(rows,records,strict=True))/148.87893934557388-1)<=1e-10
        write(f'mea/{k:.17g}.json',records)
        summary={}
        for group in dict.fromkeys(r['group'] for r in rows):
            selected=[(r,p) for r,p in zip(rows,records,strict=True) if r['group']==group]
            ok=[(r,p) for r,p in selected if p.get('status')=='Available']
            summary[group]=dict(rows=len(selected),available=len(ok),cost=sum(.5*r['weight']*p['residual']**2 for r,p in ok) if len(ok)==len(selected) else None)
        write(f'mea/{k:.17g}-summary.json',dict(k=k,groups=summary)); print('MEA',k,summary,flush=True)
