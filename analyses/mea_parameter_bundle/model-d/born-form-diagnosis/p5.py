"""Matin-role sensitivity: five-coordinate fits, followed by full re-scores."""
import time
STARTED=time.perf_counter()
import json
import sys
from pathlib import Path
import numpy as np
import born_form_diagnosis as d

d.DEADLINE=STARTED+1200.-sum(j.get('charged_s',j['wall_s']) for j in d.OLD_JOBS if j['job'].startswith('p5'))

def main(case,form):
    assert case in ('a','b') and form in ('11','00')
    name=f'p5{case}-{form}'
    mapping=d.MAPPINGS[form]
    params,groups,all_rows=d.rows_for(mapping,form)
    keep=lambda target: not (target.startswith('Matin') and (case=='b' or target.endswith('::HCO3-')))
    rows=[r for r in all_rows if keep(r[0])]
    assert len(rows)==(142 if case=='a' else 88)
    v=d.values(mapping)
    coordinates=[d.regression.coordinate(params,
        'k_ij_reciprocal_temperature_slope' if identity.endswith(d.design.probe.SLOPE) else 'k_ij',
        tuple(identity.split('/')[1:3]),origin=v[identity],scale=scale,bounds=(lo,hi))
        for identity,scale,lo,hi in zip(d.IDS,d.SCALES,d.LOWER,d.UPPER)]
    d.enough(55.)
    controls=d.regression.FitControls();controls.maximum_iterations=10
    controls.maximum_elapsed_time_seconds=min(240.,max(.001,d.DEADLINE-time.perf_counter()-35.))
    fit=d.regression.fit(params,coordinates,[r[1] for r in rows],weights=[r[2] for r in rows],controls=controls)
    raw={k:d.s._jsonable(getattr(fit,k)) for k in ('status','message','physical','weighted_residuals',
        'optimizer_jacobian','iterations','residual_evaluations','jacobian_evaluations','trial_failures','iteration_costs','iteration_seconds','initial_cost','final_cost')}
    raw['observation_statuses']=[x.name for x in fit.statuses]
    raw['targets']=[r[0] for r in rows]
    raw['active_bounds']=[d.IDS[i] for i in fit.covariance.active_bounds]
    d.save(name+'-fit.json',raw)
    if len(fit.weighted_residuals)!=len(rows) or not np.isfinite(fit.weighted_residuals).all() or any(x!=d.regression.ObservationStatus.Available for x in fit.statuses):
        raise RuntimeError('no complete sensitivity-set objective')
    achieved=float(.5*np.dot(fit.weighted_residuals,fit.weighted_residuals))
    by_group={'pressure_cost':0.,'bottinger_cost':0.,'matin_cost':0.}
    by_species=[]
    for target,r in zip(raw['targets'],fit.weighted_residuals,strict=True):
        group='bottinger_cost' if target.startswith('Bottinger') else 'matin_cost' if target.startswith('Matin') else 'pressure_cost'
        by_group[group]+=.5*float(r)**2
    assert abs(sum(by_group.values())-achieved)<1e-8
    for source in ('Matin','Bottinger'):
        for species in ('HCO3-','MEA','MEAH+','MEACOO-','MEA + MEAH+'):
            rr=[float(r) for target,r in zip(raw['targets'],fit.weighted_residuals) if target.startswith(source) and target.split('::')[-1]==species]
            by_species.append({'source':source,'species':species,'n':len(rr),
                'cost':sum(.5*r*r for r in rr) if rr else None,'mean_signed_weighted_residual':sum(rr)/len(rr) if rr else None})
    final=d.changed(mapping,dict(zip(d.IDS,fit.physical)))
    assert d.s.reaction_values(final)==d.s.reaction_values(mapping)
    assert all(d.values(final)[i]==v[i] for i in d.QIDS)
    preliminary={'form':form,'case':case,'fitted_targets':len(rows),'achieved_fitted_cost':achieved,
        'fitted_three_group_cost':by_group,'fitted_species_costs_and_signed_residuals':by_species,
        'k_coordinates':dict(zip(d.IDS,map(float,fit.physical))), 'active_bounds':raw['active_bounds'],
        'iterations':fit.iterations,'converged':fit.status=='converged','stopping_condition':fit.status,
        'full_rescore_available':False,'evidence':'sensitivity of achieved fits; not a replacement fit definition or adoption'}
    d.save(name+'-results.json',preliminary)
    final['purpose']='Matin-role sensitivity diagnosis, MEA #121; not adopted.'
    d.save(name+'-diagnostic-parameters.json',final)
    d.enough(28.)
    full=d.evaluate(name+'-full-rescore',final,form)
    preliminary.update({'full_rescore_available':True,'full_cost':full['cost'],
        'full_three_group_cost':{k:full[k] for k in ('pressure_cost','bottinger_cost','matin_cost')}})
    assert abs(sum(.5*r*r for t,r in zip(full['targets'],full['weighted_residuals']) if keep(t))-achieved)<1e-8
    d.save(name+'-results.json',preliminary)
    print('P5 RESULT',json.dumps(preliminary),flush=True)

if __name__=='__main__':
    case,form=sys.argv[1:];status='complete'
    try:main(case,form)
    except BaseException as error:
        status='failed';d.save(f'p5{case}-{form}-job-failure.json',{'exception':type(error).__name__,'message':str(error)});raise
    finally:
        d.save('job-times.json',d.OLD_JOBS+[{'job':f'p5{case}-{form}','wall_s':time.perf_counter()-STARTED,
            'status':status,'budget_family_s':1200.,'script_sha256':d.s.sha256(Path(__file__))}])
