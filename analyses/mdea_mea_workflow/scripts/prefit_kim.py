"""Issue 222 item (k): Kim-only binary fit and amended-start phase gates."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import concurrent.futures
import copy
import csv
import importlib.util
import json
import math
import multiprocessing
from pathlib import Path
import types
import zipfile

AN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('diagnosis', AN/'scripts/diagnose_carson_split.py')
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
p, eq, reg = d.p, d.eq, d.p.reg
OUT = 'results/kim-prefit'
ROWS = list(csv.DictReader((p.DATA/'Kim2008_stage1.csv').open()))

def binary_model(k):
    doc = d.document('A', None); d.set_pair(doc, p.W, p.M, *k)
    params = p.epcsaft.Parameters.from_mapping(doc, components=[p.M,p.W])
    return params, p.epcsaft.Mixture(params)

def bubble(row):
    x = float(row['liquid_x_MDEA']); support = [p.W,p.M] if x else [p.W]
    feed = {p.W:1-x, **({p.M:x} if x else {})}
    return eq.Problem(T=float(row['temperature_C'])+273.15, P=eq.Free(float(row['total_pressure_kPa'])*1000),
        feed=eq.Amounts(feed), phases=[eq.Phase('L',kind='liquid',support=support,composition_guess=feed),
        eq.Phase('V',kind='vapor',support=support,amount=eq.Pinned(0.),composition_guess={p.W:1.,**({p.M:1e-5} if x else {})})],row_tolerance=1e-10)

def phase_check(job):
    k, T, x, P, label = job
    params, model = binary_model(k); ids = list(params.component_ids)
    support = [p.W,p.M] if 0<x<1 else [p.M if x else p.W]
    feed = {c:v for c,v in ((p.M,x),(p.W,1-x)) if v}
    problem = eq.Problem(T=T,P=P,feed=eq.Amounts(feed),phases=[eq.Phase('L',kind='liquid',support=support)],row_tolerance=1e-10)
    state = eq.solve_equilibrium(model,problem)
    # Search the attainable binary face, including at pure endpoints.
    options = eq.StabilityOptions(); trials = copy.copy(problem)
    trials.phases = [eq.Phase('trial-L',kind='liquid',support=support),eq.Phase('trial-V',kind='vapor',support=support)]
    options.trials = trials._native(model).phases
    report = eq.stability_test(eq.compile_problem(model,problem),state,options)
    payload = {key:p.shared._jsonable(getattr(report,key)) for key in ('completed','message','present_phases','work')}
    payload['trials'] = [dict(kind=t.phase.kind.name.lower(),evidence=t.evidence,resolved_descent=t.resolved_descent,quantities=p.shared._jsonable(t.quantities),composition=list(t.composition),
        split_checks=p.shared._jsonable(t.split_checks),split_coordinates=list(t.split_coordinates)) for t in report.trials]
    return dict(label=label,temperature_K=T,x_MDEA=x,pressure_Pa=P,success=state.success,requested_tolerance_met=state.requested_tolerance_met,
        max_residual=max(map(abs,state.residuals)),report=payload,liquid_miscible=not any(t.resolved_descent and t.phase.kind.name.lower()=='liquid' for t in report.trials),pass_search=state.requested_tolerance_met and report.completed and not any(t.resolved_descent for t in report.trials) and 'unresolved trials 0' in report.message)

def scan(job):
    k,T = job
    # Existing diagnosis grid/hull owner, with the reciprocal law evaluated at T.
    effective = k[0]+k[1]*(1/T-1/313.15)
    result = d.mixing_scan(effective,T)
    result['reciprocal_pair'] = k
    return result

def reactive(job):
    label,variant,row = job
    doc = json.loads((AN/f'inputs/amended-starts/{label}.json').read_text())
    d.PROBES = {label:(variant,lambda target: (target.clear(),target.update(doc)),None)}
    return d.reactive((label,variant,row))

def main():
    wheel = Path(json.loads((AN/'inputs/runtime.json').read_text())['wheel'])
    assert p.sha(wheel)==p.shared.ENGINE_WHEEL_SHA256
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert z.read(name)==(Path(p.epcsaft.__file__).parent.parent/name).read_bytes(),name
    available = next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    workers = min(os.cpu_count(),max(1,available//(2*268435456)))
    params,model = binary_model((-.184,0.))
    coords = [reg.coordinate(params,[(family,(p.M,p.W),1.)],origin=origin,scale=scale,bounds=bounds) for family,origin,scale,bounds in
        [('k_ij',-.184,.01,(-.5,.5)),('k_ij_reciprocal_temperature_slope',0.,10.,(-1000.,1000.))]]
    items = [reg.observation(params,'pressure',bubble(r),observed=float(r['total_pressure_kPa'])*1000,form='log_ratio') for r in ROWS]
    controls = dict(maximum_iterations=100,function_tolerance=1e-6,parameter_tolerance=1e-10,gradient_tolerance=1e-8,maximum_elapsed_time_seconds=60,workers=min(workers,len(items)))
    p.write(f'{OUT}/compute.json',dict(cpu_count=os.cpu_count(),available_memory_bytes=available,workers=workers,BLAS_threads_per_process=1,controls=controls,
        wheel_sha256=p.sha(wheel),module=p.epcsaft.__file__,installed_files_byte_identical=True,Kim_sha256=p.sha(p.DATA/'Kim2008_stage1.csv'),
        phase_search_owner_sha256=p.sha(Path(d.f.__file__)),diagnosis_owner_sha256=p.sha(AN/'scripts/diagnose_carson_split.py')))
    fit = reg.fit(params,coords,items,weights=[1.]*len(items),controls=reg.FitControls(**controls),singular_vectors=True)
    result = {key:p.shared._jsonable(getattr(fit,key)) for key in ('status','message','usable','initial_cost','final_cost','physical','optimizer','predictions','residuals','weighted_residuals','optimizer_jacobian','physical_jacobian','iterations','iteration_costs','trial_failures')}
    result['covariance'] = {key:p.shared._jsonable(getattr(fit.covariance,key)) for key in ('status','rank','singular_values','active_bounds','projected_gradient_norm','right_vectors')}
    result['coordinate_scales']=[.01,10.];result['rows']=len(items)
    p.write(f'{OUT}/fit.json',result)
    print('Fit',result['status'],result['message'],result['physical'],flush=True)
    if not fit.usable: return
    primary = fit
    secondary_coords = [reg.coordinate(params,[(family,(p.M,p.W),1.)],origin=origin,scale=scale,bounds=bounds) for family,origin,scale,bounds in
        [('k_ij',-.15,.01,(-.5,.5)),('k_ij_reciprocal_temperature_slope',0.,10.,(-1000.,1000.))]]
    secondary_params,_ = binary_model((-.15,0.))
    other = reg.fit(secondary_params,secondary_coords,items,weights=[1.]*len(items),controls=reg.FitControls(**controls),singular_vectors=True)
    second = {key:p.shared._jsonable(getattr(other,key)) for key in ('status','message','usable','initial_cost','final_cost','physical','optimizer','predictions','residuals','weighted_residuals','optimizer_jacobian','physical_jacobian','iterations','iteration_costs','trial_failures')}
    second['covariance'] = {key:p.shared._jsonable(getattr(other.covariance,key)) for key in ('status','rank','singular_values','active_bounds','projected_gradient_norm','right_vectors')}
    p.write(f'{OUT}/fit-secondary.json',second)
    print('Secondary fit',second['status'],second['message'],second['physical'],flush=True)
    agreement = other.usable and len(other.physical)==2 and abs(primary.physical[0]-other.physical[0])<=1e-4 and abs(primary.physical[1]-other.physical[1])<=1.
    p.write(f'{OUT}/initialization-agreement.json',dict(pass_agreement=agreement,primary_start=[-.184,0.],secondary_start=[-.15,0.],k_tolerance=1e-4,slope_tolerance_K=1.))
    if not agreement:return
    k = list(fit.physical)
    result['AARD_percent']=100*sum(abs(v/i.observed-1) for v,i in zip(fit.predictions,items))/len(items)
    p.write(f'{OUT}/fit.json',result)
    amended={}
    for variant,starts in [('A',(1,3,4)),('B',(1,3))]:
        for start in starts:
            doc = d.document(variant,'variant-A-start-4.json' if start==4 else None)
            if start==1:d.set_pair(doc,p.W,p.H,-.2298,0.)
            if start==3:d.start3(doc)
            d.set_pair(doc,p.W,p.M,*k)
            label=f'{variant}{start}';p.write(f'inputs/amended-starts/{label}.json',doc)
            amended[label]=dict(sha256=p.sha(AN/f'inputs/amended-starts/{label}.json'))
    for v in 'AB':amended[v+'2']=dict(duplicate_of=v+'1',sha256=amended[v+'1']['sha256'],run=False)
    p.write('inputs/amended-starts/hashes.json',amended)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        scans = list(pool.map(scan,[(k,T) for T in (293.15,313.15,353.15,393.15)]))
        p.write(f'{OUT}/mixing-scans.json',scans)
        jobs = [(k,float(r['temperature_C'])+273.15,float(r['liquid_x_MDEA']),float(r['total_pressure_kPa'])*1000,'Kim-'+r['source_row']) for r in ROWS]
        # The same diagnostic composition grid plus the pure endpoints, at 1 atm.
        grid = sorted({0.,1.}|{10**(-6+5*i/40) for i in range(41)}|{i/200 for i in range(1,200)}|{1-10**(-6+5*i/40) for i in range(41)})
        jobs += [(k,T,x,d.P,f'grid-{T}-{x}') for T in (293.15,313.15,353.15,393.15) for x in grid]
        checks=[]
        for record in pool.map(phase_check,jobs):
            checks.append(record)
            if len(checks)%100==0:print('Binary searches',len(checks),'/',len(jobs),flush=True)
        p.write(f'{OUT}/binary-phase-search.json',checks)
        records=list(pool.map(reactive,[(v+str(s),v,row) for v,starts in [('A',(1,3,4)),('B',(1,3))] for s in starts for row in ('1','10')]))
        p.write(f'{OUT}/amended-carson-search.json',records)
    print('Hull miscible:',[s['miscible'] for s in scans],flush=True)
    print('Binary pass:',sum(r['pass_search'] for r in checks),'/',len(checks),flush=True)
    for r in records:print(r['probe'],r['source_row'],r.get('message'),r.get('split'),r.get('split_delta_g_over_rt'),flush=True)

if __name__=='__main__':main()
