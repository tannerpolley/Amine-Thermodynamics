"""Owner-authorized convergence continuation; pinned Engine and retained inputs."""
import time
STARTED = time.perf_counter()
import json
import os
import sys
from pathlib import Path
import numpy as np
import born_form_diagnosis as d

ROOT = Path(os.environ['SENSITIVITY_OUTPUT'])

def setup(name):
    raw = ROOT / 'runs' / name
    raw.mkdir(parents=True, exist_ok=False)
    d.HERE = raw
    d.s.RUNS = raw / (name + '-cache')
    d.DEADLINE = STARTED + 2380.
    original_save = d.save
    d.save = lambda filename, value: original_save(filename if filename.startswith(name) else name+'-'+filename, value)
    d.input_hashes()
    return raw

def species(targets, residuals):
    out = []
    for source in ('Matin', 'Bottinger'):
        for sp in ('HCO3-', 'MEA', 'MEAH+', 'MEACOO-', 'MEA + MEAH+'):
            rr = [float(r) for t,r in zip(targets,residuals,strict=True) if t.startswith(source) and t.split('::')[-1] == sp]
            out.append(dict(source=source,species=sp,n=len(rr),cost=sum(.5*r*r for r in rr) if rr else None,
                            mean_signed_weighted_residual=sum(rr)/len(rr) if rr else None))
    return out

def check_branches(result, form):
    expected = json.loads((ROOT/f'branch-baseline-{form}.json').read_text())['branches']
    for identity,actual in result['branches'].items():
        assert actual['phases'] == expected[identity]['phases'], 'declared solution branch changed'
        assert actual['topology_event'] == expected[identity]['topology_event'], 'solution topology event changed'

def save_summary(name, result):
    (ROOT/(name+'-results.json')).write_text(json.dumps(d.s._jsonable(result),indent=2,allow_nan=False)+'\n')

def active(k):
    return [identity for identity,x,lo,hi in zip(d.IDS,k,d.LOWER,d.UPPER) if abs(x-lo)<1e-8 or abs(x-hi)<1e-8]

def main(case, form):
    name=os.environ.get('FINAL_NAME', f'ablation-{case}-{form}')
    setup(name)
    startpath=d.FILES[form]
    start=d.values(d.s.parameter_mapping(startpath))
    mapping=d.changed(d.s.parameter_mapping(Path(os.environ.get('SENSITIVITY_MAPPING',d.FILES['11']))), {i: start[i] for i in d.IDS})
    if case == 'off':
        family = next(f for f in mapping['model_families'] if f['kind'] == 'electrolyte')
        family['choice'] = 'fully-dissociated-debye-huckel'
        for key in ('c_shell', 'c_dielectric'):
            family.pop(key, None)
        for c in mapping['components']:
            c['coefficients'] = [x for x in c['coefficients'] if x['family'] not in ('solvation_factor', 'born_diameter')]
        mapping['model_coefficients'] = [x for x in mapping['model_coefficients'] if x['family'] != 'ionic_region_relative_permittivity']
    elif case != 'refit':
        mapping=d.changed(mapping, {d.IDS[int(case)]: 0.})
    free=[i for i in d.IDS if case in ('off','refit') or i != d.IDS[int(case)]]
    assert d.design.admissible(d.IDS, [d.values(mapping)[i] for i in d.IDS], '40-80')
    d.save(name+'-start-hash.json',{'path':str(startpath),'sha256':d.s.sha256(startpath),'script_sha256':d.s.sha256(Path(__file__))})
    params,groups,rows=d.rows_for(mapping,'11')
    assert len(rows)==(159 if os.environ.get('FINAL_POOL') == '1' else 141) if os.environ.get('FINAL_RERUN') else len(rows)==142
    v=d.values(mapping)
    coords=[d.regression.coordinate(params,'k_ij_reciprocal_temperature_slope' if identity.endswith(d.design.probe.SLOPE) else 'k_ij',
        tuple(identity.split('/')[1:3]),origin=v[identity],scale=scale,bounds=(lo,hi))
        for identity,scale,lo,hi in zip(d.IDS,d.SCALES,d.LOWER,d.UPPER) if identity in free]
    controls=d.regression.FitControls();controls.maximum_iterations=40
    controls.maximum_elapsed_time_seconds=2250.
    fit=d.regression.fit(params,coords,[r[1] for r in rows],weights=[r[2] for r in rows],controls=controls)
    raw={key:d.s._jsonable(getattr(fit,key)) for key in ('status','message','physical','predictions','weighted_residuals','optimizer_jacobian',
        'physical_jacobian','iterations','residual_evaluations','jacobian_evaluations','trial_failures','iteration_costs','iteration_seconds','initial_cost','final_cost')}
    raw.update(targets=[r[0] for r in rows], coordinates=free, start={i: v[i] for i in d.IDS},
               active_bounds=[free[i] for i in fit.covariance.active_bounds])
    raw['observation_statuses']=[x.name for x in fit.statuses]
    raw['failures']=[dict(trial=f.trial,observation=raw['targets'][f.observation],status=f.status.name,message=f.message,jacobian=f.jacobian) for f in fit.failures]
    d.save(name+'-fit.json',raw)
    assert len(fit.weighted_residuals)==len(rows) and np.isfinite(fit.weighted_residuals).all()
    assert all(x==d.regression.ObservationStatus.Available for x in fit.statuses)
    final=d.changed(mapping,dict(zip(free,fit.physical)))
    assert d.s.reaction_values(final)==d.s.reaction_values(mapping)
    assert all(d.values(final)[i]==v[i] for i in d.QIDS if i in v)
    final['purpose']='Issue 141 conditional sensitivity; not adopted or physically identified.'
    (ROOT/(name+'-diagnostic-parameters.json')).write_text(json.dumps(final,indent=2)+'\n')
    result=dict(name=name,form=form,case=case,fitted_targets=len(rows),fitted_cost=float(.5*np.dot(fit.weighted_residuals,fit.weighted_residuals)),
        fitted_species_costs_and_signed_residuals=species(raw['targets'],fit.weighted_residuals),k_coordinates={i: d.values(final)[i] for i in d.IDS},
        active_bounds=active([d.values(final)[i] for i in d.IDS]),optimizer_updates=max(0,fit.iterations-1),native_history_rows=fit.iterations,
        stopping_reason=fit.status,message=fit.message,converged=fit.status=='converged',trial_failures=fit.trial_failures,full_rescore_available=False,
        gradient_quality='exact Engine EOS-parameter derivatives',evidence='local bounded numerical sensitivity fit; not physical validation')
    save_summary(name,result)
    print('RESULT',json.dumps(result),flush=True)

if __name__=='__main__':
    case,form=sys.argv[1:];name=f'ablation-{case}-{form}';status='complete'
    try:
        main(case,form)
        status='complete' if json.loads((ROOT/(name+'-results.json')).read_text())['converged'] else 'incomplete'
    except BaseException as error:
        status='failed';d.save(name+'-failure.json',dict(exception=type(error).__name__,message=str(error)));raise
    finally:
        (ROOT/(name+'-time.json')).write_text(json.dumps(dict(name=name,status=status,wall_s=time.perf_counter()-STARTED,timeout_s=2400,threads=1,lock=False,script_sha256=d.s.sha256(Path(__file__))),indent=2)+'\n')
