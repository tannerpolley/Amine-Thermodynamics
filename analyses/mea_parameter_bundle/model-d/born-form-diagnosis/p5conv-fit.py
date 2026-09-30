"""Owner-authorized convergence continuation; pinned Engine and retained inputs."""
import time
STARTED = time.perf_counter()
import json
import sys
from pathlib import Path
import numpy as np
import born_form_diagnosis as d

ROOT = Path(__file__).resolve().parent

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
    name=f'p5conv-{case}-{form}'
    setup(name)
    startpath=ROOT/f'p5{case}-{form}-diagnostic-parameters.json'
    mapping=d.s.parameter_mapping(startpath)
    d.save(name+'-start-hash.json',{'path':str(startpath),'sha256':d.s.sha256(startpath),'script_sha256':d.s.sha256(Path(__file__))})
    params,groups,all_rows=d.rows_for(mapping,form)
    keep=lambda t: not(t.startswith('Matin') and (case=='b' or t.endswith('::HCO3-')))
    rows=[r for r in all_rows if keep(r[0])]
    assert len(rows)==(142 if case=='a' else 88)
    v=d.values(mapping)
    coords=[d.regression.coordinate(params,'k_ij_reciprocal_temperature_slope' if identity.endswith(d.design.probe.SLOPE) else 'k_ij',
        tuple(identity.split('/')[1:3]),origin=v[identity],scale=scale,bounds=(lo,hi))
        for identity,scale,lo,hi in zip(d.IDS,d.SCALES,d.LOWER,d.UPPER)]
    controls=d.regression.FitControls();controls.maximum_iterations=40
    controls.maximum_elapsed_time_seconds=2250.
    fit=d.regression.fit(params,coords,[r[1] for r in rows],weights=[r[2] for r in rows],controls=controls)
    raw={key:d.s._jsonable(getattr(fit,key)) for key in ('status','message','physical','weighted_residuals','optimizer_jacobian',
        'physical_jacobian','iterations','residual_evaluations','jacobian_evaluations','trial_failures','iteration_costs','iteration_seconds','initial_cost','final_cost')}
    raw['targets']=[r[0] for r in rows]
    raw['observation_statuses']=[x.name for x in fit.statuses]
    raw['failures']=[dict(trial=f.trial,observation=raw['targets'][f.observation],status=f.status.name,message=f.message,jacobian=f.jacobian) for f in fit.failures]
    d.save(name+'-fit.json',raw)
    assert len(fit.weighted_residuals)==len(rows) and np.isfinite(fit.weighted_residuals).all()
    assert all(x==d.regression.ObservationStatus.Available for x in fit.statuses)
    final=d.changed(mapping,dict(zip(d.IDS,fit.physical)))
    assert d.s.reaction_values(final)==d.s.reaction_values(mapping)
    assert all(d.values(final)[i]==v[i] for i in d.QIDS)
    final['purpose']='MEA #121 converged Matin-role sensitivity; diagnosis only, not adopted.'
    (ROOT/(name+'-diagnostic-parameters.json')).write_text(json.dumps(final,indent=2)+'\n')
    result=dict(name=name,form=form,case=case,fitted_targets=len(rows),fitted_cost=float(.5*np.dot(fit.weighted_residuals,fit.weighted_residuals)),
        fitted_species_costs_and_signed_residuals=species(raw['targets'],fit.weighted_residuals),k_coordinates=dict(zip(d.IDS,map(float,fit.physical))),
        active_bounds=active(fit.physical),optimizer_updates=max(0,fit.iterations-1),native_history_rows=fit.iterations,
        stopping_reason=fit.status,message=fit.message,converged=fit.status=='converged',trial_failures=fit.trial_failures,full_rescore_available=False,
        gradient_quality='exact Engine EOS-parameter derivatives',evidence='local bounded numerical sensitivity fit; not physical validation')
    save_summary(name,result)
    d.enough(55.)
    full=d.evaluate(name+'-full-rescore',final,form);check_branches(full,form)
    subset=sum(.5*r*r for t,r in zip(full['targets'],full['weighted_residuals']) if keep(t))
    assert abs(subset-result['fitted_cost'])<1e-8
    result.update(full_rescore_available=True,full_cost=full['cost'],full_three_group_cost={k:full[k] for k in ('pressure_cost','bottinger_cost','matin_cost')},
        full_species_costs_and_signed_residuals=species(full['targets'],full['weighted_residuals']),subset_rescore_difference=subset-result['fitted_cost'],wall_s=time.perf_counter()-STARTED)
    save_summary(name,result)
    print('RESULT',json.dumps(result),flush=True)

if __name__=='__main__':
    case,form=sys.argv[1:];name=f'p5conv-{case}-{form}';status='complete'
    try:main(case,form)
    except BaseException as error:
        status='failed';d.save(name+'-failure.json',dict(exception=type(error).__name__,message=str(error)));raise
    finally:
        (ROOT/(name+'-time.json')).write_text(json.dumps(dict(name=name,status=status,wall_s=time.perf_counter()-STARTED,timeout_s=2400,threads=1,lock=False,script_sha256=d.s.sha256(Path(__file__))),indent=2)+'\n')
