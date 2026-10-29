"""Issue 222 stage 2: frozen endpoints, native checks, and outside-fit assessment."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import concurrent.futures as futures
import copy, importlib.util, json, math, multiprocessing, sys, types, zipfile
from pathlib import Path
import numpy as np
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('joint',AN/'scripts/fit_mdea.py')
j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
p,d,reg,eq=j.p,j.d,j.reg,j.eq
OUT='results/stage2'

def load(path): return json.loads((AN/path).read_text())
def write(path,obj):
    if OUT=='results/stage2-diagnostic':
        if isinstance(obj,dict):obj=dict(obj,**({'purpose':DIAGNOSTIC} if 'model_families' in obj else {'label':DIAGNOSTIC}))
        elif isinstance(obj,list):obj=[dict(r,label=DIAGNOSTIC) if isinstance(r,dict) else r for r in obj]
    p.write(f'{OUT}/{path}',obj)
def poolmap(fn,jobs):
    available=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    workers=min(16,os.cpu_count(),max(1,available//268435456),len(jobs))
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
    return apply_values(doc,decl['coordinates'],fit['physical']),fit

def setup(doc):
    global params,thermal,model,precomputed_scans
    precomputed_scans={}
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

def phase_report(prob,state,supports):
    trials=copy.copy(prob)
    trials.phases=[eq.Phase(f'trial-{i}',kind=kind,support=support) for i,(kind,support) in enumerate(supports)]
    options=eq.StabilityOptions();options.trials=trials._native(model).phases
    native=eq.stability_test(eq.compile_problem(model,prob),state,options)
    report={k:p.shared._jsonable(getattr(native,k)) for k in ('completed','message','present_phases','work')}
    report['declared_supports']=supports
    report['trials']=[dict(seed=t.seed,evidence=t.evidence,message=t.message,resolved_descent=t.resolved_descent,
        quantities=p.shared._jsonable(t.quantities),split_coordinates=list(t.split_coordinates),
        phase=dict(kind=t.phase.kind.name.lower(),support=list(t.phase.support))) for t in native.trials]
    return report


def classify_trials(report):
    policy=load('results/stage2-density/phase-density-threshold.json')
    dense,gas,ambiguous,rounding,other=[],[],[],[],[]
    for t in report['trials']:
        if t['resolved_descent']:
            # The final split coordinate is ln(packing fraction) of the trial phase,
            # irrespective of present-phase supports (Engine split_coordinates).
            eta=math.exp(t['split_coordinates'][-1])
            row=dict(seed=t['seed'],kind=t['phase']['kind'],packing_fraction=eta,
                delta_g_over_rt=t['quantities']['split_delta_g_over_rt'])
            (dense if eta>=policy['packing_fraction_threshold'] else gas).append(row)
            if policy['ambiguity_interval'][0]<eta<policy['ambiguity_interval'][1]:ambiguous.append(row)
        if t['evidence'] in ('unresolved','indeterminate','negative_plane_without_positive_donor'):
            target=rounding if t['evidence']=='unresolved' and t['message'].endswith('reconstruction destroys support') else other
            target.append(dict(seed=t['seed'],message=t['message'],evidence=t['evidence']))
    native_unresolved=int(report['message'].split('unresolved trials ')[1].split(';')[0])
    if native_unresolved!=len(rounding)+len(other):
        other.append(dict(message='Native unresolved count differs from classified trials',native_count=native_unresolved))
    if not report['completed']:other.append(dict(message='Native search did not complete'))
    return dict(dense_splits=dense,gas_evolution=gas,ambiguous=ambiguous,rounding_trials=rounding,other_unresolved=other)


def phase(job):
    i,prob=phase_jobs[job]
    try:
        state=eq.solve_equilibrium(model,prob)
        support=list(prob.phases[0].support)
        carbon_free=prob.feed.values.get(j.C,0.)==0.
        if carbon_free:support=[c for c in support if c not in (j.C,'bicarbonate-anion','carbonate-anion')]
        neutral=[c for c in p.published.NEUTRAL if c in support]
        report=phase_report(prob,state,[('liquid',support),('vapor',neutral)])
        gate=classify_trials(report)
        ion_free=None
        if gate['rounding_trials']:
            # #904 is ignored only after checking this same state on the ion-free face.
            ion_free=phase_report(prob,state,[('liquid',neutral),('vapor',neutral)])
            check=classify_trials(ion_free)
            for key in ('dense_splits','gas_evolution','ambiguous','other_unresolved'):gate[key]+=check[key]
            if check['rounding_trials']:gate['other_unresolved']+=check['rounding_trials']
        if not state.requested_tolerance_met:gate['other_unresolved'].append(dict(message=state.message))
        gate['passed']=not any(gate[k] for k in ('dense_splits','ambiguous','other_unresolved'))
        return dict(index=i,T_K=prob.T,success=state.success,requested_tolerance_met=state.requested_tolerance_met,
            max_residual=max(map(abs,state.residuals)),residuals=list(state.residuals),amounts=list(state.amounts),
            mole_fractions=list(state.mole_fractions),component_ids=list(params.component_ids),
            carbon_free_trial_supports=carbon_free,stability=report,ion_free_check=ion_free,density_gate=gate,
            split=bool(gate['dense_splits']))
    except Exception as e:return dict(index=i,error=f'{type(e).__name__}: {e}')

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
    if not phase_summary(results)['passed']:
        write(f'{label}/stop.json',dict(reason='Endpoint phase gate failed or unresolved; return to Design',outside_fit_evaluated=False))
        return False
    phase_jobs=jobs
    results=poolmap(phase,list(range(len(phase_jobs))))
    write(f'{label}/fitted-phase.json',results)
    failed=[r for r in results if not r.get('density_gate',{}).get('passed',False)]
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


DIAGNOSTIC='diagnostic: phase assumption violated at fitted Merkley saturation states'

def apply_values(doc,decl,values):
    values=iter(values)
    for q in decl:
        for family,target,factor in q['targets']:
            value=next(values)
            if family=='temperature_law_coefficient':
                next(t['coefficient'] for pair in doc['pairs'] for c in pair['coefficients'] for t in c.get('temperature_law',{}).get('terms',[]) if t['coefficient']['identity']==target)['value']['magnitude']=value
            else:
                block=next(c for c in doc['components'] if c['component_id']==target) if isinstance(target,str) else next(pair for pair in doc['pairs'] if {pair['component_id_a'],pair['component_id_b']}==set(target))
                next(c for c in block['coefficients'] if c['family']==family)['value']['magnitude']=value
    assert next(values,None) is None
    return doc

def fit_document(doc,variant,bounds,folder,removed=(),*,maximum_iterations=40):
    setup(doc)
    _,decl=j.coordinates(params,doc,variant)
    for q,b in zip(decl,bounds): q['bounds']=b
    coords=[reg.coordinate(params,q['targets'],origin=q['origin'],scale=q['scale'],bounds=q['bounds']) for q in decl]
    metadata,observations,weights=j.objective(params)
    keep=[i for i in range(len(metadata)) if i not in removed]
    metadata=[metadata[i] for i in keep];observations=[observations[i] for i in keep];weights=[weights[i] for i in keep]
    write(f'{folder}/declaration.json',dict(coordinates=decl,observations=metadata,removed_indices=list(removed)))
    available=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    controls=dict(maximum_iterations=maximum_iterations,function_tolerance=1e-10,parameter_tolerance=1e-10,gradient_tolerance=1e-8,maximum_elapsed_time_seconds=2100.,workers=min(16,os.cpu_count(),max(1,available//268435456),len(keep)))
    write(f'{folder}/compute.json',dict(controls=controls,available_memory_bytes=available,BLAS_threads_per_process=1))
    result=reg.fit(params,coords,observations,weights=weights,thermochemistry=thermal,controls=reg.FitControls(**controls),singular_vectors=True)
    record={k:p.shared._jsonable(getattr(result,k)) for k in ('status','message','usable','final_cost','physical','optimizer','predictions','weighted_residuals','iterations','iteration_costs','trial_failures','optimizer_jacobian','physical_jacobian','residuals')}
    record['failures']=[dict(trial=f.trial,observation=f.observation,status=f.status.name,message=f.message,jacobian=f.jacobian,optimizer=list(f.optimizer)) for f in result.failures]
    record['covariance']={k:p.shared._jsonable(getattr(result.covariance,k)) for k in ('rank','singular_values','active_bounds','right_vectors')}
    record['group_costs']={g:sum(.5*r*r for m,r in zip(metadata,result.weighted_residuals) if m['group']==g) for g in dict.fromkeys(m['group'] for m in metadata)}
    write(f'{folder}/fit.json',record)
    candidate=apply_values(copy.deepcopy(doc),decl,result.physical)
    write(f'{folder}/endpoint.json',candidate)
    print(folder,record['status'],record['final_cost'],flush=True)
    return candidate,record

def comparison_items(*, capped_merkley=False):
    # Declarations only: this function never calculates a prediction or statistic.
    global comparison_problems
    metadata,observations,comparison_problems=[],[],[]
    def add(group,row,prob,kind='pressure',observed=1.,extra=None):
        metadata.append(dict(group=group,row=row,observed=observed))
        observations.append(reg.observation(params,kind,prob,observed=observed,form='difference',scale=1.,**(extra or {})))
        comparison_problems.append([prob])
    def heat(group,r,T,P,w,alpha,obs):
        initial,final=j.problem(T,P,j.water(w),0.),j.problem(T,P,j.water(w),alpha)
        metadata.append(dict(group=group,row=r,observed=obs))
        if capped_merkley and group=='Merkley-outside' and 293.15<=T<=395:
            observations.append(reg.saturation_capped_addition_enthalpy(params,initial,j.problem(T,P,j.water(w),.5,True),{j.C:1.},basis_amount=1.,loading_cap=alpha,loading_bounds=(.05,1.5),loading_grid=[.05*i for i in range(1,31)],T=T,P=P,phase='vapor',observed=obs,form='difference',scale=1.))
        else:
            observations.append(reg.addition_enthalpy(params,initial,final,{j.C:1.},alpha,T,P,phase='vapor',observed=obs,form='difference',scale=1.))
        comparison_problems.append([initial,final])
    for r in j.rows('Ermatchkov_2006_CO2_MDEA_partial_pressure.csv'):
        m=float(r['m_MDEA_mol_per_kg_H2O']);alpha=float(r['m_CO2_mol_per_kg_H2O'])/m
        w=m*.1191622/(1+m*.1191622)
        add('Ermatchkov',dict(r,mass_fraction=w),j.problem(float(r['temperature_K']),max(1e5,float(r['p_CO2_kPa'])*1000),1/.01801528/m,alpha,True),observed=float(r['p_CO2_kPa'])*1000)
    for r in j.rows('Ermatchkov2006_stage1.csv'):
        m=float(r['m_MDEA_mol_kg_water']);add('corrected-Kamps',r,j.problem(float(r['temperature_K']),float(r['total_pressure_MPa'])*1e6,1/.01801528/m,float(r['m_CO2_mol_kg_water'])/m,True),observed=float(r['total_pressure_MPa'])*1e6)
    for r in j.rows('BottingerMDEA2008_stage1.csv'):
        amine=float(r['x_MDEA_H'])
        r=dict(r,DMDEA_over_reported_amine_sum=float(r['x_DMDEA'])/amine,byproduct_over_reported_amine_sum=float(r['x_byproduct'])/amine,exceeds_3_percent=(float(r['x_DMDEA'])+float(r['x_byproduct']))/amine>.03)
        for pressure in (500000.,2500000.):
            prob=j.problem(float(r['temperature_K']),pressure,j.water(float(r['initial_MDEA_mass_fraction'])),float(r['loading']))
            for name,species,observed in [('amine-sum',[j.M,j.H],float(r['x_MDEA_H'])),('bicarbonate',['bicarbonate-anion','carbonate-anion'],float(r['x_HCO3_reported']))]:
                add('Bottinger-'+name+f'-{pressure/1e5:g}bar',dict(r,pressure_Pa=pressure),prob,'mole_fraction',observed,dict(phase='L',species=species))
                metadata[-1]['species']=species
    loading={(r['temperature_K'],r['MDEA_mass_percent']):float(r['alpha_LP_mol_CO2_per_mol_MDEA']) for r in j.rows('Merkley1987_loading_points.csv')}
    for r in j.rows('Merkley1987_stage1.csv'):
        T=float(r['temperature_K']);w=float(r['MDEA_mass_percent'])/100;alpha=loading[(r['temperature_K'],r['MDEA_mass_percent'])]
        heat('Merkley-half-loading',r,T,float(r['proposed_pressure_kPa'])*1000,w,alpha/2,float(r['heat_kJ_mol_CO2'])*1000)
        if w>.4 or T not in (333.15,388.71):heat('Merkley-outside',r,T,float(r['proposed_pressure_kPa'])*1000,w,alpha,float(r['heat_kJ_mol_CO2'])*1000)
    for r in j.rows('Weiland1997_stage1.csv'):
        if float(r['MDEA_mass_fraction'])<=.5:continue
        nw=j.water(.6);alpha=float(r['loading']);mass=.1191622+nw*.01801528+alpha*.0440095
        add('Cp-60wt',r,j.problem(298.15,101325.,nw,alpha),'equilibrium_isobaric_heat_capacity',float(r['Cp_J_g_K'])*1000*mass/(1+nw+alpha))
    for r in j.rows('Weiland1998_stage1.csv'):
        if float(r['MDEA_mass_percent'])<=50:continue
        add('density-60wt',r,j.problem(298.15,101325.,j.water(.6),float(r['loading'])),'phase_density',float(r['density_g_mL'])*1000,dict(phase='L',mass_basis=True))
    for r in j.rows('Kuranov_1996_CO2_MDEA_total_pressure.csv'):
        if float(r['temperature_K'])<=395:continue
        m=float(r['m_MDEA_mol_per_kg_H2O']);P=float(r['ten_times_total_pressure_MPa'])*1e5
        add('Kuranov-413K',r,j.problem(float(r['temperature_K']),P,1/.01801528/m,float(r['m_CO2_mol_per_kg_H2O'])/m,True),observed=P)
    for r in j.rows('Zheng2020_stage1.csv'):
        heat('Zheng',r,float(r['temperature_K']),float(r['pressure_MPa'])*1e6,float(r['unloaded_MDEA_mass_fraction']),float(r['alpha_sat_mol_CO2_per_mol_MDEA']),-float(r['minus_integral_heat_kJ_per_mol_CO2'])*1000)
    for r in j.rows('Sedighi2024_stage1.csv'):
        if float(r['MDEA_wt_percent'])>50:continue
        P=float(r['pressure_kPa'])*1000
        add('Sedighi',r,j.problem(float(r['temperature_K']),P,j.water(float(r['unloaded_MDEA_mass_fraction'])),float(r['alpha_mol_CO2_per_mol_MDEA']),True),observed=P)
    return metadata,observations

def comparison_prediction(i):
    record=dict(cmeta[i],label=assessment_label)
    try:
        prob=comparison_problems[i][-1]
        if prob.T>395 or prob.T<293.15:
            return dict(record,status='unevaluated: frozen reaction domain 293.15–395 K')
        pred=reg.predict(model,citems[i])
        record.update(status=pred.status.name,message=pred.message)
        if pred.status.name=='Available':
            value=pred.value
            if record['group']=='Ermatchkov':
                result=eq.solve_equilibrium(model,prob)
                y=result.phase_mole_fractions(1)
                value=result.pressure*y[list(params.component_ids).index(j.C)]
                record['total_pressure_Pa']=result.pressure
            record.update(predicted=value,relative_error=value/record['observed']-1 if record['observed'] else None)
    except Exception as e:record.update(status='error',message=f'{type(e).__name__}: {e}')
    return record

def assess(doc,folder,label):
    global cmeta,citems,assessment_label
    setup(doc);assessment_label=label
    cmeta,citems=comparison_items()
    records=poolmap(comparison_prediction,list(range(len(citems))))
    write(f'{folder}/comparisons.json',records)
    def statistic(selected):
        ok=[r for r in selected if r.get('relative_error') is not None]
        return dict(rows=len(selected),available=len(ok),AARD_percent=100*float(np.mean([abs(r['relative_error']) for r in ok])) if len(ok)==len(selected) and ok else None,label=label)
    er=[r for r in records if r['group']=='Ermatchkov']
    primary=[r for r in er if r['row']['mass_fraction']<=.49]
    assert len(primary)==88 and len(er)==101
    summary={g:statistic([r for r in records if r['group']==g]) for g in dict.fromkeys(r['group'] for r in records)}
    summary.update(Ermatchkov88=statistic(primary),Ermatchkov_above49=statistic([r for r in er if r['row']['mass_fraction']>.49]),Ermatchkov_below7=statistic([r for r in er if float(r['row']['p_CO2_kPa'])<7]),Ermatchkov88_below7=statistic([r for r in primary if float(r['row']['p_CO2_kPa'])<7]),references_126_percent=[42.72,60.97],unscored=['Derks: unresolved basis/temperature','Xiao and Zhang: first-page-only attachments'])
    # Wangler sensitivity: same endpoints, no refit, all heat/Cp observations.
    spec=importlib.util.spec_from_file_location('cp_sensitivity',AN/'scripts/diagnose_unloaded_cp.py');cp=importlib.util.module_from_spec(spec);spec.loader.exec_module(cp)
    meta,items,weights=j.objective(params)
    original_meta,original_items,original_problems=cmeta,citems,comparison_problems
    neumann=records
    global thermal,model
    thermal=cp.caloric(params);model=p.epcsaft.Mixture(params,thermochemistry=thermal)
    selected=[i for i,m in enumerate(meta) if m['group'] in ('Carson','Merkley','Cp')]
    cmeta=[meta[i] for i in selected];citems=[items[i] for i in selected]
    # predictions below do not inspect the comparison problem except for domain gating
    globals()['comparison_problems']=[[j.problem(298.15,101325.,j.water(.3),.1)] for _ in selected]
    wangler=poolmap(comparison_prediction,list(range(len(citems))))
    write(f'{folder}/wangler-fitted-heat-cp.json',wangler)
    cmeta,citems=original_meta,original_items;globals()['comparison_problems']=original_problems
    write(f'{folder}/wangler-comparisons.json',poolmap(comparison_prediction,[i for i,m in enumerate(cmeta) if m['group'] in ('Zheng','Merkley-outside','Merkley-half-loading','Cp-60wt')]))
    supplemental(doc,folder,label)
    write(f'{folder}/summary.json',summary)
    print(folder,'Ermatchkov88',summary['Ermatchkov88'],flush=True)
    return summary

def phase_summary(records):
    groups={name:[r['index'] for r in records if r.get('density_gate',{}).get(key)]
        for name,key in [('liquid_witnesses','dense_splits'),('vapor_witnesses','gas_evolution'),
                         ('rounding_states','rounding_trials'),('ambiguous','ambiguous')]}
    unresolved=[r['index'] for r in records if 'density_gate' not in r or r['density_gate']['other_unresolved']]
    return dict(states=len(records),**groups,unresolved=unresolved,
        rounding_trials=sum(len(r.get('density_gate',{}).get('rounding_trials',[])) for r in records),
        passed=bool(records) and not groups['liquid_witnesses'] and not groups['ambiguous'] and not unresolved)

def search_document(doc,folder,witness_only=False):
    global phase_jobs
    setup(doc);metadata,_,_=fitted_items()
    jobs=[(f'fit:{i}:{k}',prob) for i,ps in enumerate(problems) for k,prob in enumerate(ps)]
    assert len(jobs)==len(load('results/stage2/A1/fitted-phase.json')), 'Original fitted-state phase grid changed'
    if witness_only:
        jobs=[job for job in jobs if int(job[0].split(':')[1]) in (83,126,127,128)]
    else:
        comparison_items()
        jobs += [(f'comparison:{i}:{k}',prob) for i,ps in enumerate(comparison_problems) for k,prob in enumerate(ps) if 293.15<=prob.T<=395]
    write(f'{folder}/phase-states.json',[dict(index=index,T_K=prob.T) for index,prob in jobs])
    if not witness_only:precompute_saturations(saturation_jobs())
    saturation_rows=poolmap(phase_saturation,saturation_jobs()) if not witness_only else []
    write(f'{folder}/saturation-phase-inputs.json',saturation_rows)
    for row in saturation_rows:
        if row.get('status')=='Available':jobs.append((row['index'],j.problem(row['T_K'],row['P_Pa'],j.water(row['mass_fraction']),row['alpha_phase'])))
    phase_jobs=jobs
    records=poolmap(phase,list(range(len(jobs))))
    records += [dict(index=r['index'],requested_tolerance_met=False,error=r['status']) for r in saturation_rows if r.get('status')!='Available']
    write(f'{folder}/phase.json',records);summary=phase_summary(records)
    write(f'{folder}/phase-summary.json',summary)
    print(folder,'phase',len(summary['liquid_witnesses']),'liquid witnesses;',len(summary['unresolved']),'unresolved',flush=True)
    return summary

def diagnostic():
    global OUT
    OUT='results/stage2-diagnostic'
    write('authority.json',dict(label=DIAGNOSTIC,base_commit='ed5816657738acee4afa8237fc0d6b9c7d38f194',runtime=load('inputs/runtime.json')))
    import csv
    witness=list(csv.DictReader((AN/'results/stage2/liquid-witnesses.csv').open()))
    for label in ('A1','B1'):
        doc,_=endpoint(label);assess(doc,label,DIAGNOSTIC)
        removed=sorted({int(r['index'].split(':')[0]) for r in witness if r['start']==label and r['group']=='Merkley'})
        setup(doc);_,decl=j.coordinates(params,doc,label[0])
        refit,result=fit_document(doc,label[0],[q['bounds'] for q in decl],f'{label}-removed-Merkley',removed)
        search_document(refit,f'{label}-removed-Merkley')
        assess(refit,f'{label}-removed-Merkley',DIAGNOSTIC)



def phase_score(records):
    values=[t['quantities'].get('split_delta_g_over_rt',0.) for r in records for t in r.get('stability',{}).get('trials',[]) if t['phase']['kind']=='liquid' and t['resolved_descent']]
    return min(values,default=0.)

def narrow():
    global OUT
    OUT='results/stage2-narrowed'
    write('authority.json',dict(base_commit='ed58166',decision='Phase evidence only; no outside-fit statistic before bound freeze',maximum_steps_per_variant=6,probe_rule='One coordinate inward by 10 percent of its original interval; rank by least-negative resolved liquid split, then unresolved count. Refit from variant best declared start each step.'))
    for label in ('A1','B1'):
        doc,_=endpoint(label);setup(doc);_,original=j.coordinates(params,doc,label[0])
        bounds=[list(q['bounds']) for q in original];history=[]
        if (AN/f'{OUT}/{label}/path.json').exists():
            history=load(f'{OUT}/{label}/path.json');bounds=history[-1]['bounds']
            doc=load(f'{OUT}/{label}/step-{history[-1]["step"]}/endpoint.json')
        for step in range(len(history)+1,7):
            folder=f'{label}/step-{step}'
            setup(doc);_,decl=j.coordinates(params,doc,label[0])
            probes=[]
            for i,q in enumerate(decl):
                if i<2:continue
                lo,hi=bounds[i];v=q['origin'];tol=1e-6*max(1.,hi-lo)
                side=0 if abs(v-lo)<tol else 1 if abs(v-hi)<tol else None
                if side is None:continue
                delta=.1*(original[i]['bounds'][1]-original[i]['bounds'][0])
                inward=v+delta if side==0 else v-delta
                if not lo<inward<hi:continue
                changed=copy.deepcopy(doc)
                # Multi-target diameter values retain their specified factors.
                apply_values(changed,[q],[inward*factor for _,_,factor in q['targets']])
                summary=search_document(changed,f'{folder}/probe-{i}',witness_only=True)
                records=load(f'{OUT}/{folder}/probe-{i}/phase.json')
                probes.append(dict(coordinate=i,side=side,inward=inward,minimum_liquid_delta_G_over_RT=phase_score(records),phase=summary))
            write(f'{folder}/probes.json',probes)
            if not probes:
                history.append(dict(step=step,stop='No active ion bound admits an inward probe; decision required'))
                break
            chosen=max(probes,key=lambda r:(r['minimum_liquid_delta_G_over_RT'],-len(r['phase']['unresolved'])))
            bounds[chosen['coordinate']][chosen['side']]=chosen['inward']
            write(f'{folder}/bounds.json',dict(bounds=bounds,chosen=chosen,outside_fit_statistics_computed=False))
            # Best declared start, projected only if a newly narrowed interval excludes it.
            initial=load(f'results/item-l/amended-starts/{label}.json')
            pair=next(q for q in initial['pairs'] if {q['component_id_a'],q['component_id_b']}=={j.W,j.H})
            if len(pair['coefficients'])==1:d.set_pair(initial,j.W,j.H,pair['coefficients'][0]['value']['magnitude'],0.)
            setup(initial);_,initial_decl=j.coordinates(params,initial,label[0])
            for q,b in zip(initial_decl,bounds):
                v=min(b[1],max(b[0],q['origin']))
                apply_values(initial,[q],[v*factor for _,_,factor in q['targets']])
            doc,result=fit_document(initial,label[0],bounds,folder)
            phase_result=search_document(doc,folder)
            history.append(dict(step=step,bounds=copy.deepcopy(bounds),objective=result['final_cost'],group_costs=result['group_costs'],phase=phase_result,chosen=chosen))
            write(f'{label}/path.json',history)
            if phase_result['passed']:
                write(f'{label}/frozen-bounds.json',dict(bounds=bounds,endpoint=doc,phase=phase_result,reason='No resolved liquid witness and no unresolved trial at all in-domain fitted/comparison states'))
                assess(doc,f'{label}/assessment','bound-active narrowed endpoint')
                break
        write(f'{label}/disposition.json',dict(history=history,stable=bool(history and history[-1].get('phase',{}).get('passed')),verdict='Full assessment requires stable endpoint; no MDEA outcome falsifies the MEA bicarbonate value.'))



def pressure_difference(r,alpha):
    T=float(r['temperature_K']);P=float(r.get('pressure_MPa',.156))*1e6
    w=float(r.get('unloaded_MDEA_mass_fraction',float(r.get('MDEA_mass_percent',30))/100))
    state=eq.solve_equilibrium(model,j.problem(T,P,j.water(w),alpha,True))
    if not state.requested_tolerance_met:raise ValueError(state.message)
    return state.pressure-P

def saturation_point(job):
    r,alpha=job
    try:return dict(alpha=float(alpha),delta_pressure_Pa=pressure_difference(r,float(alpha)),admitted=True)
    except Exception as e:return dict(alpha=float(alpha),admitted=False,message=f'{type(e).__name__}: {e}')

def precompute_saturations(jobs):
    global precomputed_scans
    rows=[r for _,r in jobs if 293.15<=float(r['temperature_K'])<=395]
    results=poolmap(saturation_point,[(r,float(a)) for r in rows for a in np.arange(1,31)*.05])
    precomputed_scans={json.dumps(r,sort_keys=True):results[30*i:30*(i+1)] for i,r in enumerate(rows)}

def saturation(r):
    from scipy.optimize import brentq
    difference=lambda alpha:pressure_difference(r,alpha)
    key=json.dumps(r,sort_keys=True)
    scan=precomputed_scans[key] if key in precomputed_scans else [saturation_point((r,float(a))) for a in np.arange(1,31)*.05]
    brackets=[(a['alpha'],b['alpha']) for a,b in zip(scan,scan[1:]) if a['admitted'] and b['admitted'] and a['delta_pressure_Pa']*b['delta_pressure_Pa']<=0]
    record=dict(scan=scan,brackets=brackets,sign_changes=len(brackets),nonunique=len(brackets)>1,xtol=1e-12)
    if not brackets:return dict(record,status='unresolved: no adjacent admitted pressure-sign bracket')
    try:
        alpha=brentq(difference,*brackets[0],xtol=1e-12)
        return dict(record,status='Available',alpha_sat=alpha,pressure_residual_Pa=difference(alpha))
    except Exception as e:return dict(record,status=f'unresolved inversion: {type(e).__name__}: {e}')

def saturation_jobs():
    return [('Zheng-saturation',r) for r in j.rows('Zheng2020_stage1.csv')]+[('Merkley-156kPa',r) for r in j.rows('Merkley1987_stage1.csv') if r['temperature_K']=='333.15']

def phase_saturation(job):
    group,r=job
    result=saturation(r)
    if result['status']=='Available':
        lp=next((float(s['alpha_LP_mol_CO2_per_mol_MDEA']) for s in j.rows('Merkley1987_loading_points.csv') if s['temperature_K']==r['temperature_K'] and s['MDEA_mass_percent']==r.get('MDEA_mass_percent')),float('inf')) if group=='Merkley-156kPa' else float('inf')
        result['alpha_phase']=min(lp,result['alpha_sat'])
    return dict(result,index=f"saturation:{group}:{r.get('source_row',r.get('MDEA_mass_percent'))}",T_K=float(r['temperature_K']),P_Pa=float(r.get('pressure_MPa',.156))*1e6,mass_fraction=float(r.get('unloaded_MDEA_mass_fraction',float(r.get('MDEA_mass_percent',30))/100)))

def saturation_comparison(job):
    group,r=job
    record=dict(group=group,row=r,label=assessment_label)
    try:
        if not 293.15<=float(r['temperature_K'])<=395:return dict(record,status='unevaluated: frozen reaction domain')
        sat=saturation(r);record.update(sat)
        if sat['status']!='Available':return record
        if group=='Merkley-156kPa':
            points=j.rows('Merkley1987_loading_points.csv')
            lp=next(float(s['alpha_LP_mol_CO2_per_mol_MDEA']) for s in points if s['temperature_K']==r['temperature_K'] and s['MDEA_mass_percent']==r['MDEA_mass_percent'])
            alpha=min(lp,sat['alpha_sat']);w=float(r['MDEA_mass_percent'])/100;T=float(r['temperature_K']);P=156000.
            item=reg.addition_enthalpy(params,j.problem(T,P,j.water(w),0.),j.problem(T,P,j.water(w),alpha),{j.C:1.},alpha,T,P,phase='vapor',observed=float(r['heat_kJ_mol_CO2'])*1000,form='difference',scale=1.)
            pred=reg.predict(model,item);record.update(alpha_endpoint=alpha,prediction_status=pred.status.name,predicted_J_mol=pred.value if pred.status.name=='Available' else None)
    except Exception as e:record.update(status='error',message=f'{type(e).__name__}: {e}')
    return record

def supplemental(doc,folder,label):
    global assessment_label
    setup(doc);assessment_label=label
    jobs=[('Zheng-saturation',r) for r in j.rows('Zheng2020_stage1.csv')]+[('Merkley-156kPa',r) for r in j.rows('Merkley1987_stage1.csv') if float(r['temperature_K']) in (288.71,333.15)]
    precompute_saturations(jobs)
    write(f'{folder}/saturation-and-alternative-pressure.json',poolmap(saturation_comparison,jobs))


def present():
    import csv,matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=AN/'results/stage2-diagnostic';rows=[]
    for name in ('A1','A1-removed-Merkley','B1','B1-removed-Merkley'):
        stat=load(f'results/stage2-diagnostic/{name}/summary.json')['Ermatchkov88']
        rows.append(dict(candidate=name,AARD_percent=stat['AARD_percent'],rows=stat['rows'],label=DIAGNOSTIC))
    with (root/'ermatchkov-aard.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    fig,ax=plt.subplots(figsize=(8,3.8),layout='constrained')
    for i,row in enumerate(rows):
        ax.scatter(row['AARD_percent'],i,marker='o' if i%2==0 else 'x',color='#0072B2' if i<2 else '#D55E00',s=65)
        ax.annotate(f"{row['AARD_percent']:.3f}%",(row['AARD_percent'],i),xytext=(6,7),textcoords='offset points',fontsize=10)
    ax.axvline(24.2,color='#777777',ls='--',label='Qualified pass bar (not applied here)')
    ax.set(yticks=range(4),yticklabels=['A1','A1: unstable Merkley removed','B1','B1: unstable Merkley removed'],xlabel='Ermatchkov 88-row CO₂ partial-pressure AARD (%)',xlim=(15,31),ylim=(3.6,-.6),title='Diagnostic only: fitted-state phase assumption violated')
    ax.legend(loc='lower right',fontsize=8);ax.grid(axis='x',alpha=.2)
    fig.savefig(root/'ermatchkov-aard.png',dpi=180)

if __name__=='__main__':
    OUT='results/stage2-diagnostic' if sys.argv[1] in ('diagnostic','supplement','bottinger','saturation-probe','diagnostic-phase','present') else 'results/stage2-narrowed' if sys.argv[1] in ('narrow','rephase') else OUT
    runtime=load('inputs/runtime.json');wheel=Path(runtime['wheel'])
    assert p.sha(wheel)==runtime['wheel_sha256']==p.shared.ENGINE_WHEEL_SHA256
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'): assert z.read(name)==(Path(p.epcsaft.__file__).parent.parent/name).read_bytes(),name
    write('runtime.json',dict(runtime,base_commit='ed58166' if OUT!='results/stage2' else '799f9f3',installed_files_byte_identical=True,worktree=str(p.ROOT)))
    if sys.argv[1]=='present':present()
    elif sys.argv[1]=='diagnostic': diagnostic()
    elif sys.argv[1]=='narrow': narrow()
    elif sys.argv[1]=='rephase':
        OUT='results/stage2-narrowed'
        for label in ('A1','B1'):
            if not (AN/f'{OUT}/{label}/path.json').exists():continue
            history=load(f'{OUT}/{label}/path.json')
            for row in history:
                folder=f"{label}/step-{row['step']}"
                row['phase']=search_document(load(f'{OUT}/{folder}/endpoint.json'),folder)
            write(f'{label}/path.json',history)
            if (AN/f'{OUT}/{label}/disposition.json').exists():
                disposition=load(f'{OUT}/{label}/disposition.json');disposition['history']=history;disposition['stable']=history[-1]['phase']['passed'];write(f'{label}/disposition.json',disposition)
    elif sys.argv[1]=='diagnostic-phase':
        OUT='results/stage2-diagnostic'
        for label in ('A1-removed-Merkley','B1-removed-Merkley'):search_document(load(f'{OUT}/{label}/endpoint.json'),label)
    elif sys.argv[1]=='saturation-probe':
        OUT='results/stage2-diagnostic';setup(endpoint('A1')[0]);records=[]
        for group,r in [('Zheng',j.rows('Zheng2020_stage1.csv')[0]),('Merkley',next(r for r in j.rows('Merkley1987_stage1.csv') if r['temperature_K']=='333.15' and r['MDEA_mass_percent']=='40'))]:
            T=float(r['temperature_K']);P=float(r.get('pressure_MPa',.156))*1e6;w=float(r.get('unloaded_MDEA_mass_fraction',.4))
            for alpha in (.0001,.1,.5,1.,1.5,2.):
                state=eq.solve_equilibrium(model,j.problem(T,P,j.water(w),alpha,True))
                records.append(dict(group=group,T_K=T,P_target_Pa=P,alpha=alpha,success=state.requested_tolerance_met,pressure_Pa=state.pressure,message=state.message))
        write('saturation-bracket-probe.json',records)
    elif sys.argv[1]=='bottinger':
        OUT='results/stage2-diagnostic'
        for label in ('A1','B1','A1-removed-Merkley','B1-removed-Merkley'):
            setup(endpoint(label)[0] if '-removed-' not in label else load(f'{OUT}/{label}/endpoint.json'))
            cmeta,citems=comparison_items();assessment_label=DIAGNOSTIC
            rows=poolmap(comparison_prediction,[i for i,m in enumerate(cmeta) if m['group'].startswith('Bottinger')])
            previous=load(f'{OUT}/{label}/comparisons.json');first=next(i for i,r in enumerate(previous) if r['group'].startswith('Bottinger'))
            write(f'{label}/comparisons.json',previous[:first]+rows+[r for r in previous[first:] if not r['group'].startswith('Bottinger')])
            if '-removed-' in label:search_document(load(f'{OUT}/{label}/endpoint.json'),label)
    elif sys.argv[1]=='supplement':
        OUT='results/stage2-diagnostic'
        for label in ('A1','B1'):
            supplemental(endpoint(label)[0],label,DIAGNOSTIC)
            supplemental(load(f'{OUT}/{label}-removed-Merkley/endpoint.json'),f'{label}-removed-Merkley',DIAGNOSTIC)
    elif sys.argv[1]=='check':
        for label in sys.argv[2:]:
            if not checks(label): print(label,'STOP: endpoint phase gate',flush=True)

    elif sys.argv[1]=='diagnose':
        for label in sys.argv[2:]: diagnose(label)
    elif sys.argv[1]=='sensitivity':
        for label in sys.argv[2:]: sensitivity(label)

    elif sys.argv[1]=='numerical':
        for label in sys.argv[2:]: numerical(label)
