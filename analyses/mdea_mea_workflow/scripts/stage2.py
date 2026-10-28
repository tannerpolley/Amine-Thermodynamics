"""Issue 222 stage 2: frozen endpoints, native checks, and outside-fit assessment."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import concurrent.futures as futures
import copy, importlib.util, json, multiprocessing, sys, types, zipfile
from pathlib import Path
import numpy as np
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('joint',AN/'scripts/fit_mdea.py')
j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
p,d,reg,eq=j.p,j.d,j.reg,j.eq
OUT='results/stage2'

def load(path): return json.loads((AN/path).read_text())
def write(path,obj): p.write(f'{OUT}/{path}',obj)
def poolmap(fn,jobs):
    available=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    workers=min(os.cpu_count(),max(1,available//268435456),len(jobs))
    write(f'compute-{fn.__name__}.json',dict(cpu_count=os.cpu_count(),workers=workers,available_memory_bytes=available,BLAS_threads_per_process=1,jobs=len(jobs)))
    with futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        return list(pool.map(fn,jobs))

def endpoint(label):
    fit=load(f'results/joint-fit-linear/{label}/fit.json')
    decl=load(f'results/joint-fit-linear/{label}/declaration.json')
    doc=load(f'results/item-l/amended-starts/{label}.json')
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={j.W,j.H})
    if not any(c['family']=='k_ij_reciprocal_temperature_slope' for c in pair['coefficients']):
        d.set_pair(doc,j.W,j.H,pair['coefficients'][0]['value']['magnitude'],0.)
    values=iter(fit['physical'])
    for coord in decl['coordinates']:
        for family,target,factor in coord['targets']:
            value=next(values)
            if family=='temperature_law_coefficient':
                next(t['coefficient'] for q in doc['pairs'] for c in q['coefficients'] for t in c.get('temperature_law',{}).get('terms',[]) if t['coefficient']['identity']==target)['value']['magnitude']=value
            else:
                block=next(c for c in doc['components'] if c['component_id']==target) if isinstance(target,str) else next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}==set(target))
                next(c for c in block['coefficients'] if c['family']==family)['value']['magnitude']=value
    assert next(values,None) is None
    return doc,fit

def setup(doc):
    global params,thermal,model
    params=p.epcsaft.Parameters.from_mapping(doc)
    s=importlib.util.spec_from_file_location('cp',AN/'scripts/diagnose_unloaded_cp.py')
    cp=importlib.util.module_from_spec(s);s.loader.exec_module(cp)
    thermal=cp.caloric(params,load('results/diagnosis-unloaded-cp/summary.json')['neumann_cubic'])
    model=p.epcsaft.Mixture(params,thermochemistry=thermal)

def fitted_items():
    # Preserve the high-level problem declarations for phase and balance checks.
    global problems
    problems=[]
    observation,addition=reg.observation,reg.addition_enthalpy
    def obs(params,kind,prob,**kw):
        problems.append([prob]);return observation(params,kind,prob,**kw)
    def heat(params,initial,final,*args,**kw):
        problems.append([initial,final]);return addition(params,initial,final,*args,**kw)
    reg.observation,reg.addition_enthalpy=obs,heat
    try: return j.objective(params)
    finally: reg.observation,reg.addition_enthalpy=observation,addition

def replay(i):
    pred=reg.predict(model,items[i])
    record=dict(meta[i],prediction={k:p.shared._jsonable(getattr(pred,k)) for k in ('value','unit','status','message','residual','requested_tolerance_met')})
    if pred.status.name=='Available': record['relative_error']=abs(pred.value-fit['predictions'][i])/max(1.,abs(fit['predictions'][i]))
    return record

def phase(job):
    i,prob=phase_jobs[job]
    try:
        state=eq.solve_equilibrium(model,prob)
        support=prob.phases[0].support
        neutral=[c for c in p.published.NEUTRAL if c in support]
        d.f.s=types.SimpleNamespace(COMPONENT_IDS=tuple(neutral)+tuple(c for c in support if c not in neutral),_jsonable=p.shared._jsonable)
        # The MEA search declares its vapor support as the first three species;
        # restrict the ion-free face's trial phases explicitly when needed.
        if len(neutral)==3: report=d.f.stability(model,prob,state)
        else:
            options=eq.StabilityOptions();trials=copy.copy(prob)
            trials.phases=[eq.Phase('trial-L',kind='liquid',support=support),eq.Phase('trial-V',kind='vapor',support=neutral)]
            options.trials=trials._native(model).phases
            native=eq.stability_test(eq.compile_problem(model,prob),state,options)
            report={k:p.shared._jsonable(getattr(native,k)) for k in ('completed','message','present_phases','work')}
            report['trials']=[dict(resolved_descent=t.resolved_descent,quantities=p.shared._jsonable(t.quantities),evidence=t.evidence,message=t.message,phase=dict(kind=t.phase.kind.name.lower())) for t in native.trials]
        return dict(index=i,T_K=prob.T,success=state.success,requested_tolerance_met=state.requested_tolerance_met,max_residual=max(map(abs,state.residuals)),residuals=list(state.residuals),amounts=list(state.amounts),mole_fractions=list(state.mole_fractions),component_ids=list(params.component_ids),stability=report,split=any(t['resolved_descent'] for t in report['trials']))
    except Exception as e: return dict(index=i,error=f'{type(e).__name__}: {e}')

def checks(label):
    global fit,items,meta,phase_jobs
    doc,fit=endpoint(label);setup(doc)
    write(f'{label}/endpoint.json',doc)
    meta,items,weights=fitted_items()
    records=poolmap(replay,list(range(len(items))))
    write(f'{label}/replay.json',records)
    print(label,'replay',max(r.get('relative_error',float('inf')) for r in records),flush=True)
    jobs=[(f'{i}:{k}',prob) for i,ps in enumerate(problems) for k,prob in enumerate(ps)]
    # Carson first: a demonstrated phase failure is a stop, independent of bounds.
    carson=[job for job in jobs if meta[int(job[0].split(':')[0])]['group']=='Carson' and meta[int(job[0].split(':')[0])]['row']['source_row'] in ('1','10') and job[0].endswith(':1')]
    phase_jobs=carson
    results=poolmap(phase,list(range(len(phase_jobs))))
    write(f'{label}/carson-phase.json',results)
    print(label,'Carson',[(r['index'],r.get('split'),r.get('error'),r.get('stability',{}).get('message')) for r in results],flush=True)
    if any(r.get('split') or not r.get('requested_tolerance_met',False) or 'unresolved trials 0' not in r.get('stability',{}).get('message','') for r in results):
        write(f'{label}/stop.json',dict(reason='Endpoint phase gate failed or unresolved; return to Design',outside_fit_evaluated=False))
        return False
    phase_jobs=jobs
    results=poolmap(phase,list(range(len(phase_jobs))))
    write(f'{label}/fitted-phase.json',results)
    failed=[r for r in results if r.get('split') or not r.get('requested_tolerance_met',False) or 'unresolved trials 0' not in r.get('stability',{}).get('message','')]
    write(f'{label}/checks.json',dict(rows=len(records),max_replay_error=max(r.get('relative_error',float('inf')) for r in records),phase_states=len(results),phase_gate_failures=len(failed),failed_indices=[r['index'] for r in failed]))
    return not failed

def diagnose(label):
    doc,fit=endpoint(label);setup(doc)
    meta,items,weights=fitted_items()
    retained=load(f'{OUT}/{label}/fitted-phase.json')
    evidence=[]
    for index in ('83:0','126:1','127:1','128:1'):
        record=next(r for r in retained if r['index']==index)
        if not record.get('split'): continue
        i,k=map(int,index.split(':'));prob=problems[i][k]
        d.f.s=types.SimpleNamespace(COMPONENT_IDS=d.SPECIES,_jsonable=p.shared._jsonable)
        state=eq.solve_equilibrium(model,prob)
        report=d.f.stability(model,prob,state)
        liquid=[t for t in report['trials'] if t['resolved_descent'] and t['phase']['kind']=='liquid']
        if not liquid: continue
        trial=min(liquid,key=lambda t:t['quantities']['split_delta_g_over_rt'])
        split=d.phases(trial,list(params.component_ids))
        single=sum(n*q['g_over_rt'] for n,q in zip(state.amounts,report['present_phases']))
        two=copy.copy(prob)
        two.phases=[eq.Phase(f'L{k+1}',kind='liquid',support=p.published.SPECIES,composition_guess=q['x'],packing_guess=q['packing_fraction']) for k,q in enumerate(split)]
        result=eq.solve_equilibrium(model,two)
        evidence.append(dict(index=index,observation=meta[i],repeat=report,admitted_split=split,
            two_liquid={key:p.shared._jsonable(getattr(result,key)) for key in ('success','message','requested_tolerance_met','amounts','mole_fractions','residuals')}))
        write(f'{label}/phase-diagnosis.json',evidence)
        print(label,index,'two liquid',evidence[-1]['two_liquid']['message'],flush=True)

def sensitivity(label):
    doc,fit=endpoint(label);setup(doc)
    meta,items,weights=fitted_items()
    coords,decl=j.coordinates(params,doc,label[0])
    native=reg.differentiate(params,coords,items,optimizer=[0.]*9,thermochemistry=thermal)
    jac=np.array(native.residual_optimizer_gradient).reshape(-1,9)*np.sqrt(weights)[:,None]
    _,sv,right=np.linalg.svd(jac,full_matrices=False)
    rows=[]
    for direction in (-1,-2):
        vector=right[direction]
        for step in (-1.,-.5,-.25,.25,.5,1.):
            feasible=1.
            for q,v in zip(decl,step*vector):
                if v: feasible=min(feasible,max(0.,((q['bounds'][1] if v>0 else q['bounds'][0])-q['origin'])/(q['scale']*v)))
            displacement=step*feasible
            record=dict(direction=direction,requested_step=step,feasible_step=displacement,vector=vector.tolist())
            if abs(displacement)<1e-12:
                record.update(status='blocked by active bounds; no nonzero displacement along this direction',objective_change=None,group_prediction_changes={})
            else:
                result=reg.differentiate(params,coords,items,optimizer=(displacement*vector).tolist(),thermochemistry=thermal)
                values=list(result.predictions)
                residual=np.array([np.log(v/m['observed']) if m['group'] in ('Kuranov','Kim') else (v-m['observed'])/m['scale'] for v,m in zip(values,meta)]);cost=float(.5*np.dot(residual*np.sqrt(weights),residual*np.sqrt(weights)))
                record.update(status='evaluated',objective=cost,objective_change=cost-fit['final_cost'],group_prediction_changes={g:max(abs(values[i]-fit['predictions'][i])/max(1.,abs(fit['predictions'][i])) for i,m in enumerate(meta) if m['group']==g) for g in dict.fromkeys(m['group'] for m in meta)})
            rows.append(record)
    write(f'{label}/local-sensitivity.json',dict(definition='Two weakest scaled-Jacobian directions; bounded objective scans without refitting; not likelihood profiles',singular_values=sv.tolist(),rank=int(np.linalg.matrix_rank(jac)),right_vectors=right.tolist(),scans=rows))

def numerical(label):
    doc,fit=endpoint(label);setup(doc)
    meta,items,weights=fitted_items()
    phase_rows=load(f'{OUT}/{label}/fitted-phase.json')
    # C,H,N,O and charge for the declared eight-species chemistry.
    atoms={j.W:[0,2,0,1,0],j.C:[1,0,0,2,0],j.M:[5,13,1,2,0],j.H:[5,14,1,2,1],
        'hydronium-cation':[0,3,0,1,1],'hydroxide-anion':[0,1,0,1,-1],
        'bicarbonate-anion':[1,1,0,3,-1],'carbonate-anion':[1,0,0,3,-2]}
    matrix=np.array([atoms[c] for c in params.component_ids])
    balances=[]
    for row in phase_rows:
        if not row.get('requested_tolerance_met'): continue
        i,k=map(int,row['index'].split(':'));prob=problems[i][k]
        amounts=np.array(row['amounts']);x=np.array(row['mole_fractions']).reshape(len(amounts),-1)
        total=(amounts[:,None]*x).sum(axis=0)@matrix
        feed=sum((v*np.array(atoms[c]) for c,v in prob.feed.values.items()),np.zeros(5))
        balances.append(dict(index=row['index'],difference_mol=(total-feed).tolist(),maximum_relative_element_error=float(max(abs(total[:4]-feed[:4])/np.maximum(1.,abs(feed[:4])))),absolute_charge_error_mol=float(abs(total[4]))))
    write(f'{label}/balances.json',dict(basis='C,H,N,O element mol; charge mol elementary charges; from native phase amounts and compositions',rows=balances,max_relative_element_error=max(r['maximum_relative_element_error'] for r in balances),max_absolute_charge_error_mol=max(r['absolute_charge_error_mol'] for r in balances)))
    selected=[items[0],items[next(i for i,m in enumerate(meta) if m['group']=='Cp')]]
    coords,decl=j.coordinates(params,doc,label[0])
    baseline=reg.differentiate(params,coords,selected,optimizer=[0.]*9,thermochemistry=thermal)
    gradient=np.array(baseline.optimizer_gradient).reshape(2,9)
    checked=[]
    for n,q in enumerate(decl):
        step=1e-3
        center=q['origin']-q['scale']*step>=q['bounds'][0] and q['origin']+q['scale']*step<=q['bounds'][1]
        sign=1. if q['origin']+q['scale']*2*step<=q['bounds'][1] else -1.
        positions=(-step,step) if center else (sign*step,sign*2*step)
        values=[]
        for v in positions:
            point=np.zeros(9);point[n]=v
            values.append(np.array(reg.differentiate(params,coords,selected,optimizer=point.tolist(),thermochemistry=thermal).predictions))
        fd=(values[1]-values[0])/(2*step) if center else (-3*np.array(baseline.predictions)+4*values[0]-values[1])/(2*sign*step)
        error=float(np.linalg.norm(fd-gradient[:,n])/np.linalg.norm(gradient[:,n]))
        checked.append(dict(coordinate=n,method='centered' if center else 'inward second order',optimizer_step=step,exact=gradient[:,n].tolist(),finite_difference=fd.tolist(),relative_error=error,passed=error<=1e-5))
    write(f'{label}/derivatives.json',dict(tolerance=1e-5,observations=[meta[0],next(m for m in meta if m['group']=='Cp')],checks=checked,passed=all(r['passed'] for r in checked)))

if __name__=='__main__':
    runtime=load('inputs/runtime.json');wheel=Path(runtime['wheel'])
    assert p.sha(wheel)==runtime['wheel_sha256']==p.shared.ENGINE_WHEEL_SHA256
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'): assert z.read(name)==(Path(p.epcsaft.__file__).parent.parent/name).read_bytes(),name
    write('runtime.json',dict(runtime,base_commit='799f9f3',installed_files_byte_identical=True,worktree=str(p.ROOT)))
    if sys.argv[1]=='check':
        for label in sys.argv[2:]:
            if not checks(label): print(label,'STOP: endpoint phase gate',flush=True)

    elif sys.argv[1]=='diagnose':
        for label in sys.argv[2:]: diagnose(label)
    elif sys.argv[1]=='sensitivity':
        for label in sys.argv[2:]: sensitivity(label)

    elif sys.argv[1]=='numerical':
        for label in sys.argv[2:]: numerical(label)
