"""Issue 222 joint objective, using native MEA regression declarations."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import csv, importlib.util, json, math, concurrent.futures, multiprocessing
from pathlib import Path
import numpy as np
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('kim',AN/'scripts/prefit_kim.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
d,p,eq,reg=k.d,k.p,k.eq,k.reg
W,M,H,C=p.W,p.M,p.H,p.C
# Owner decision 2026-10-28: application-only upper-domain amendment.
recs=json.loads((AN/'inputs/probe-reaction-reference.json').read_text())['shared']
for r in recs:r['engine_correlation']['temperature_max']=395.
d.REACTIONS=[eq.Reaction({cid:v for cid,v in zip(p.shared.COMPONENT_IDS,r['stoichiometry']) if v},name=r['reaction_id'],correlation=p.shared._reaction_correlation(r,r['reaction_id']),reference=p.shared._reaction_reference(r,r['reaction_id'])) for r in recs]
d.REACTIONS.append(eq.Reaction({H:-1,W:-1,M:1,'hydronium-cation':1},name='MDEA-dissociation',correlation=eq.ReactionLogPolynomial(-83.491+4.0165+10.976*math.log(313.15),-819.7,10.976,0.,313.15,278.,395.,p.shared.COMMON_SOURCE_STANDARD_STATE_ID),reference=eq.ReactionReference(eq.ReferenceSourceBasis.CommonMolalityInfiniteDilution,1e5)))

def rows(name):return list(csv.DictReader((p.DATA/name).open()))
def water(w):return .1191622*(1-w)/w/.01801528

def problem(T,P,nw,alpha,bubble=False):
    feed={W:nw,M:1.,C:alpha}
    phases=[eq.Phase('L',kind='liquid',support=p.published.SPECIES)]
    if bubble:phases.append(eq.Phase('V',kind='vapor',support=p.published.NEUTRAL,amount=eq.Pinned(0.),composition_guess={W:.1,M:1e-5,C:.9}))
    return eq.Problem(T=T,P=eq.Free(P) if bubble else P,feed=eq.Amounts(feed),phases=phases,reactions=d.REACTIONS,neutral_reference=p.published.NEUTRAL_REFERENCE,row_tolerance=1e-10)

def coordinates(params,doc,variant):
    def comp(f):return next(c['value']['magnitude'] for q in doc['components'] if q['component_id']==H for c in q['coefficients'] if c['family']==f)
    def pair(a,b,f):return next(c['value']['magnitude'] for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={a,b} for c in q['coefficients'] if c['family']==f)
    law=json.loads((AN/'results/item-l/declaration.json').read_text())
    terms=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={M,W})['coefficients'][0]['temperature_law']['terms']
    declarations=[dict(targets=[('temperature_law_coefficient',term['coefficient']['identity'],1.)],origin=term['coefficient']['value']['magnitude'],scale=scale,bounds=bounds)
        for term,scale,bounds in zip(terms,law['scales'],law['bounds'],strict=True)]
    for a,b,f,scale,bounds in [(H,C,'k_ij',.01,(-.5,.5)),(H,W,'k_ij',.01,(-.5,.5)),(H,W,'k_ij_reciprocal_temperature_slope',10.,(-1000.,1000.)),(H,'bicarbonate-anion','k_ij',.01,(-1.,1.))]:
        declarations.append(dict(targets=[(f,(a,b),1.)],origin=pair(a,b,f),scale=scale,bounds=bounds))
    declarations += [dict(targets=[('segment_diameter',H,1.),('debye_huckel_diameter',H,1.)]+([('packing_diameter',H,.88)] if variant=='A' else []),origin=comp('segment_diameter'),scale=.1,bounds=(3.,7.) if variant=='A' else (3.,4.5)),
        dict(targets=[('dispersion_energy_over_k',H,1.)],origin=comp('dispersion_energy_over_k'),scale=10.,bounds=(50.,950.)),
        dict(targets=[('born_diameter',H,1.)],origin=comp('born_diameter'),scale=.1,bounds=(2.,7.))]
    return [reg.coordinate(params,q['targets'],origin=q['origin'],scale=q['scale'],bounds=q['bounds']) for q in declarations],declarations

def objective(params, *, capped_merkley=False):
    metadata,items,weights=[],[],[]
    def add(group,row,item,weight=1.):metadata.append(dict(group=group,row=row,weight=weight,observed=item.observed,scale=item.scale));items.append(item);weights.append(weight)
    for r in rows('Kuranov_1996_CO2_MDEA_total_pressure.csv'):
        T=float(r['temperature_K'])
        if round(T)>393:continue
        m=float(r['m_MDEA_mol_per_kg_H2O']);alpha=float(r['m_CO2_mol_per_kg_H2O'])/m;P=float(r['ten_times_total_pressure_MPa'])*1e5
        add('Kuranov',r,reg.observation(params,'pressure',problem(T,P,1/.01801528/m,alpha,True),observed=P,form='log_ratio'),100/9)
    for r in rows('Jakobsen2005_stage1.csv'):
        T=float(r['temperature_C'])+273.15;prob=problem(T,101325.,water(.23),float(r['loadNMR']))
        denom=float(r['x_MDEA'])+float(r['x_MDEAH_printed_xAmCOO'])
        for name,species,obs in [('cation',[H],float(r['x_MDEAH_printed_xAmCOO'])/denom),('carbonate',['bicarbonate-anion','carbonate-anion'],(float(r['x_HCO3'])+float(r['x_CO3']))/denom)]:
            add('Jakobsen',dict(r,ratio=name),reg.observation(params,'amount_ratio',prob,phase='L',species=species,denominator_phase='L',denominator_species=[M,H],observed=obs,form='difference',scale=.1*obs))
    def heat(group,r,T,P,w,alpha,obs):
        add(group,r,reg.addition_enthalpy(params,problem(T,P,water(w),0.),problem(T,P,water(w),alpha),{C:1.},alpha,T,P,phase='vapor',observed=obs,form='difference',scale=max(3000.,.05*abs(obs))))
    for r in rows('Carson2000_stage1.csv'):
        w=float(r['MDEA_mass_fraction']);x=float(r['x_CO2']);heat('Carson',r,298.15,101325.,w,x/(1-x)*(1+water(w)),float(r['solution_enthalpy_kJ_mol_CO2'])*1000)
    loading={(r['temperature_K'],r['MDEA_mass_percent']):float(r['alpha_LP_mol_CO2_per_mol_MDEA']) for r in rows('Merkley1987_loading_points.csv')}
    for r in rows('Merkley1987_stage1.csv'):
        if float(r['MDEA_mass_percent'])>40 or float(r['temperature_K']) not in (333.15,388.71):continue
        T,P,w=float(r['temperature_K']),float(r['proposed_pressure_kPa'])*1000,float(r['MDEA_mass_percent'])/100
        alpha=loading[(r['temperature_K'],r['MDEA_mass_percent'])];obs=float(r['heat_kJ_mol_CO2'])*1000
        if capped_merkley:
            add('Merkley',r,reg.saturation_capped_addition_enthalpy(params,problem(T,P,water(w),0.),problem(T,P,water(w),.5,True),{C:1.},basis_amount=1.,loading_cap=alpha,loading_bounds=(.05,1.5),loading_grid=[.05*i for i in range(1,31)],T=T,P=P,phase='vapor',observed=obs,form='difference',scale=max(3000.,.05*abs(obs))))
        else:
            heat('Merkley',r,T,P,w,alpha,obs)
    for r in rows('Weiland1997_stage1.csv'):
        w=float(r['MDEA_mass_fraction']);alpha=float(r['loading'])
        if w>.5:continue
        nw=water(w);mass=.1191622+nw*.01801528+alpha*.0440095
        obs=float(r['Cp_J_g_K'])*1000*mass/(1+nw+alpha)
        add('Cp',r,reg.observation(params,'equilibrium_isobaric_heat_capacity',problem(298.15,101325.,nw,alpha),observed=obs,form='difference',scale=.02*obs))
    rho=[r for r in rows('Weiland1998_stage1.csv') if float(r['MDEA_mass_percent'])<=50]
    for r in rho:
        group=sorted([s for s in rho if s['MDEA_mass_percent']==r['MDEA_mass_percent']],key=lambda s:float(s['loading']));i=group.index(r);left,right=group[max(0,i-1)],group[min(len(group)-1,i+1)]
        g=(float(right['density_g_mL'])-float(left['density_g_mL']))*1000/(float(right['loading'])-float(left['loading']))
        obs=float(r['density_g_mL'])*1000;scale=math.hypot(.001*obs,g*.01)
        add('loaded-density',dict(r,secant_g_kg_m3=g),reg.observation(params,'phase_density',problem(298.15,101325.,water(float(r['MDEA_mass_percent'])/100),float(r['loading'])),phase='L',mass_basis=True,observed=obs,form='difference',scale=scale),1/len(rho))
    # All observations use the full model order; supports restrict these to ion-free faces.
    for r in rows('Sobrino2016_stage1.csv'):
        if float(r['pressure_MPa'])!=.1:continue
        nw=water(float(r['MDEA_mass_fraction']))
        prob=eq.Problem(T=float(r['temperature_K']),P=1e5,feed=eq.Amounts({W:nw,M:1.}),phases=[eq.Phase('L',kind='liquid',support=[W,M])],row_tolerance=1e-10)
        add('unloaded-density',r,reg.observation(params,'phase_density',prob,phase='L',mass_basis=True,observed=float(r['density_kg_m3']),form='difference',scale=.5),10.)
    for r in k.ROWS:add('Kim',r,reg.observation(params,'pressure',k.bubble(r),observed=float(r['total_pressure_kPa'])*1000,form='log_ratio'))
    return metadata,items,weights

def run(label):
    doc=json.loads((AN/f'results/item-l/amended-starts/{label}.json').read_text())
    # Declare zero slopes explicitly where the source start had only a constant.
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={W,H})
    if not any(c['family']=='k_ij_reciprocal_temperature_slope' for c in pair['coefficients']):d.set_pair(doc,W,H,pair['coefficients'][0]['value']['magnitude'],0.)
    params=p.epcsaft.Parameters.from_mapping(doc);coords,declarations=coordinates(params,doc,label[0])
    spec=importlib.util.spec_from_file_location('cp',AN/'scripts/diagnose_unloaded_cp.py')
    cp=importlib.util.module_from_spec(spec);spec.loader.exec_module(cp)
    cubic=json.loads((AN/'results/diagnosis-unloaded-cp/summary.json').read_text())['neumann_cubic']
    thermal=cp.caloric(params,cubic)
    meta,items,weights=objective(params)
    p.write(f'results/joint-fit-linear/{label}/declaration.json',dict(coordinates=declarations,observations=meta))
    initial=reg.differentiate(params,coords,items,optimizer=[0.]*9,thermochemistry=thermal)
    p.write(f'results/joint-fit-linear/{label}/initial-jacobian.json',initial)
    jac=np.array(initial.residual_optimizer_gradient).reshape(-1,9)*np.sqrt(weights)[:,None]
    _,singular,right=np.linalg.svd(jac,full_matrices=False)
    p.write(f'results/joint-fit-linear/{label}/initial-identifiability.json',dict(singular_values=singular.tolist(),right_vectors=right.tolist(),rank=int(np.linalg.matrix_rank(jac)),column_scales=[r['scale'] for r in declarations],statuses=initial.statuses))
    print(label,'initial derivative retained',flush=True)
    available=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    workers=min(os.cpu_count(),max(1,available//268435456),len(items))
    controls=dict(maximum_iterations=40,function_tolerance=1e-10,parameter_tolerance=1e-10,gradient_tolerance=1e-8,maximum_elapsed_time_seconds=2100.,workers=workers)
    p.write(f'results/joint-fit-linear/{label}/compute.json',dict(workers=workers,available_memory_bytes=available,BLAS_threads_per_process=1,controls=controls))
    fitted=reg.fit(params,coords,items,weights=weights,thermochemistry=thermal,controls=reg.FitControls(**controls),singular_vectors=True)
    result={q:p.shared._jsonable(getattr(fitted,q)) for q in ('status','message','usable','initial_cost','final_cost','physical','optimizer','predictions','residuals','weighted_residuals','optimizer_jacobian','physical_jacobian','iterations','iteration_costs','iteration_seconds','trial_failures','residual_evaluations','jacobian_evaluations')}
    result['covariance']={q:p.shared._jsonable(getattr(fitted.covariance,q)) for q in ('status','rank','singular_values','active_bounds','projected_gradient_norm','right_vectors')}
    result['failures']=[dict(trial=f.trial,observation=f.observation,status=f.status.name,message=f.message,jacobian=f.jacobian) for f in fitted.failures]
    result['group_costs']={g:sum(.5*r*r for m,r in zip(meta,fitted.weighted_residuals) if m['group']==g) for g in dict.fromkeys(m['group'] for m in meta)}
    p.write(f'results/joint-fit-linear/{label}/fit.json',result)
    print(label,result['status'],result['message'],result['final_cost'],flush=True)
    return result

if __name__=='__main__':
    # Each native observation campaign is parallelized by row in the fit, never nested pools.
    for label in ('A1','A3','B1','B3'):
        try:
            result=run(label)
            if not result['usable'] or result['covariance']['rank']<9 or result['covariance']['active_bounds']:break
        except Exception as e:
            p.write(f'results/joint-fit-linear/{label}/failure.json',dict(error=f'{type(e).__name__}: {e}'))
            print(label,type(e).__name__,str(e),flush=True)
            break
