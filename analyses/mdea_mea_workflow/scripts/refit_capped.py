"""Issue 222 native saturation-capped refits and density-gated selection."""
import copy
import importlib.util
import sys
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('acceptance',AN/'scripts/accept_engine_delivery.py')
a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
s,n=a.s,a.n
OUT='results/stage2-capped'
original_objective=s.j.objective
s.j.objective=lambda params:original_objective(params,capped_merkley=True)
s.OUT=OUT;n.OUT=OUT
s.write=n.write
s.load=n.load
original_comparison_items=s.comparison_items
s.comparison_items=lambda:original_comparison_items(capped_merkley=True)
original_fitted_items=s.fitted_items

def fitted_items():
    cap=s.reg.saturation_capped_addition_enthalpy
    captured=[]
    def capped(params,initial,bubble,feed,**kw):
        nw=initial.feed.values[s.j.W];w=.1191622/(.1191622+nw*.01801528)
        row=dict(temperature_K=str(initial.T),pressure_MPa=str(kw['P']/1e6),unloaded_MDEA_mass_fraction=str(w))
        sat=s.saturation(row)
        if sat['status']!='Available' or sat['sign_changes']!=1:raise RuntimeError('Saturation root refused during endpoint gate: '+str(sat))
        alpha=min(kw['loading_cap'],sat['alpha_sat'])
        captured.append((initial,s.j.problem(initial.T,kw['P'],nw,alpha)))
        return cap(params,initial,bubble,feed,**kw)
    s.reg.saturation_capped_addition_enthalpy=capped
    try:
        metadata,items,weights=original_fitted_items()
        indices=[i for i,m in enumerate(metadata) if m['group']=='Merkley']
        assert len(s.problems)==len(metadata) and len(captured)==len(indices)
        for index,states in zip(indices,captured,strict=True):s.problems[index]=list(states)
        return metadata,items,weights
    finally:s.reg.saturation_capped_addition_enthalpy=cap
s.fitted_items=fitted_items

def start(label):
    doc=s.load(f'results/item-l/amended-starts/{label}.json')
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={s.j.W,s.j.H})
    if not any(c['family']=='k_ij_reciprocal_temperature_slope' for c in pair['coefficients']):s.d.set_pair(doc,s.j.W,s.j.H,pair['coefficients'][0]['value']['magnitude'],0.)
    return doc

def endpoint(label):return s.load(f'{OUT}/{label}/endpoint.json'),s.load(f'{OUT}/{label}/fit.json')
s.endpoint=endpoint

def saturation_gate(label):
    doc,_=endpoint(label);s.setup(doc);jobs=[];caps=[]
    loading={(q['temperature_K'],q['MDEA_mass_percent']):float(q['alpha_LP_mol_CO2_per_mol_MDEA']) for q in s.j.rows('Merkley1987_loading_points.csv')}
    s.precompute_saturations([('Merkley',dict(row,pressure_MPa=str(float(row['proposed_pressure_kPa'])/1000))) for row in s.j.rows('Merkley1987_stage1.csv')])
    for i,row in enumerate(s.j.rows('Merkley1987_stage1.csv')):
        T=float(row['temperature_K']);P=float(row['proposed_pressure_kPa'])*1000
        if not 293.15<=T<=395:continue
        sat=s.saturation(dict(row,pressure_MPa=str(P/1e6)))
        if sat['status']!='Available' or sat['sign_changes']!=1:raise RuntimeError('Owner decision: refused saturation at '+label+' '+str(row))
        lp=loading[(row['temperature_K'],row['MDEA_mass_percent'])];alpha=min(lp,sat['alpha_sat'])
        caps.append(dict(row,source_loading=lp,saturation_loading=sat['alpha_sat'],selected_loading=alpha,truncation=lp-alpha))
        jobs.append((f'Merkley-capped:{i}',s.j.problem(T,P,s.j.water(float(row['MDEA_mass_percent'])/100),alpha)))
    s.phase_jobs=jobs;extra=n.pool(s.phase,list(range(len(jobs))))
    n.write(f'{label}/capped-phase.json',extra);n.write(f'{label}/Merkley-caps.json',caps)
    original=n.load(f'{OUT}/{label}/phase.json')
    summary=s.phase_summary(original+extra);n.write(f'{label}/phase-summary.json',summary)
    return summary

if __name__=='__main__':
    assert s.load('results/stage2-density/engine-d5138209/prefit-acceptance.json')['passed']
    a.identity();n.write('authority.json',dict(runtime=s.load('results/stage2-density/engine-d5138209/runtime.json'),starts=['A1','A3','B1','B3'],excluded=['A4'],duplicates={'A2':'A1','B2':'B1'},density_threshold=.10,selection='lowest fitted cost among density-gate-passing endpoints, before outside-fit statistics'))
    for label in ('A1','A3','B1','B3'):
        if (AN/f'{OUT}/{label}/fit.json').exists():
            candidate,result=endpoint(label)
            if not (AN/f'{OUT}/{label}/phase-summary.json').exists():s.search_document(candidate,label)
            continue
        doc=start(label);s.setup(doc)
        coords,decl=s.j.coordinates(s.params,doc,label[0]);metadata,items,weights=s.j.objective(s.params)
        initial=s.reg.differentiate(s.params,coords,items,optimizer=[0.]*9,thermochemistry=s.thermal)
        jac=s.np.array(initial.residual_optimizer_gradient).reshape(-1,9)*s.np.sqrt(weights)[:,None]
        _,sv,right=s.np.linalg.svd(jac,full_matrices=False)
        n.write(f'{label}/initial-identifiability.json',dict(singular_values=sv.tolist(),right_vectors=right.tolist(),rank=int(s.np.linalg.matrix_rank(jac))))
        candidate,result=s.fit_document(doc,label[0],[q['bounds'] for q in decl],label)
        if not result['usable'] or result['status']!='converged' or result['covariance']['rank']<9:
            n.write('stop.json',dict(label=label,reason='Unusable fit or rank-deficient endpoint',result=result));raise RuntimeError('Owner decision required: '+label+' '+result['message'])
        phase=s.search_document(candidate,label)
        if phase['rounding_trials']:print('Remaining reconstruction trials retained with ion-free checks',flush=True)
    for label in ('A1','A3','B1','B3'):
        if endpoint(label)[1]['status']!='converged':raise RuntimeError('Owner decision required: nonconverged '+label)
        saturation_gate(label)
    selection={}
    for variant in 'AB':
        passing=[label for label in (variant+'1',variant+'3') if s.load(f'{OUT}/{label}/phase-summary.json')['passed']]
        if not passing:raise RuntimeError('Owner decision required: no density-gate-passing endpoint for '+variant)
        label=min(passing,key=lambda label:endpoint(label)[1]['final_cost'])
        doc,fit=endpoint(label)
        selection[variant]=dict(label=label,cost=fit['final_cost'],active_bounds=fit['covariance']['active_bounds'],endpoint_sha256=s.p.sha(AN/f'{OUT}/{label}/endpoint.json'))
    n.write('selection.json',selection)
    print('SELECTION',selection,flush=True)
