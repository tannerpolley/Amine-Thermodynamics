"""Issue 222(l): Kim-only linear-temperature pair fit and prescribed gates; no joint fit."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import concurrent.futures, copy, csv, importlib.util, json, math, multiprocessing, sys, zipfile
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent
AN=OUT.parents[1]
spec=importlib.util.spec_from_file_location('cp',AN/'scripts/diagnose_unloaded_cp.py')
cp=importlib.util.module_from_spec(spec);spec.loader.exec_module(cp)
j,p,d,reg=cp.j,cp.p,cp.d,cp.reg
k=j.k
M,W=p.M,p.W
IDENTITY='pair/mdea-water/k_ij'
CUBIC=json.loads((AN/'results/diagnosis-unloaded-cp/summary.json').read_text())['neumann_cubic']

def write(name,obj):p.write('results/item-l/'+name,obj)
def linear(doc,values):
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={M,W})
    pair['coefficients']=[dict(family='k_ij',identity=IDENTITY,temperature_law=dict(form='polynomial-plus-reciprocal-temperature',reference_temperature=p.value(313.15,'kelvin'),terms=[dict(power=i,coefficient=dict(identity=IDENTITY+f'/a{i}',value=p.value(v,u))) for i,(v,u) in enumerate(zip(values,('dimensionless','1 / kelvin')))]))]

def binary(values):
    doc=d.document('A',None);linear(doc,values)
    params=p.epcsaft.Parameters.from_mapping(doc,components=[M,W])
    return params,p.epcsaft.Mixture(params)

def thermal(params):return cp.caloric(params,CUBIC)
def phase_check(job):
    k.binary_model=binary
    record=k.phase_check(job)
    record['pass_search']=bool(record['success'] and record['requested_tolerance_met'] and record['report']['completed'] and record['liquid_miscible'] and 'unresolved trials 0' in record['report']['message'])
    return record

def scan(job):
    values,T=job
    return d.mixing_scan(values[0]+values[1]*(T-313.15),T)
def reactive(job):
    label,variant,row=job
    doc=json.loads((OUT/f'amended-starts/{label}.json').read_text())
    d.PROBES={label:(variant,lambda target:(target.clear(),target.update(doc)),None)}
    d.a.caloric_record=thermal
    return d.reactive(job)

def fitted_result(fit,items):
    result={key:p.shared._jsonable(getattr(fit,key)) for key in ('status','message','usable','initial_cost','final_cost','physical','optimizer','predictions','residuals','weighted_residuals','optimizer_jacobian','physical_jacobian','iterations','iteration_costs','trial_failures')}
    result['covariance']={key:p.shared._jsonable(getattr(fit.covariance,key)) for key in ('status','rank','singular_values','active_bounds','projected_gradient_norm','right_vectors')}
    result['AARD_percent']=100*sum(abs(v/o.observed-1) for v,o in zip(fit.predictions,items))/len(items)
    return result

def properties(values):
    rows=[];density=[]
    # Slope-zero control retains item-(k) k0, matching the retained diagnosis control.
    cases=[('linear + Neumann',lambda doc:linear(doc,values),CUBIC),('item-k reciprocal + Wangler',lambda doc:cp.pair_edit(doc,*cp.KIM),None),('slope-0 + Neumann (item-k k0)',lambda doc:cp.pair_edit(doc,cp.KIM[0],0.),CUBIC)]
    for label,edit,cubic in cases:
        model,_=cp.build(edit,cubic)
        for w,obs in sorted(cp.WEILAND.items()):
            pred,rho=cp.cp_mass(model,298.15,w)
            rows.append(dict(case=label,source='Weiland 1997 Table 1',T_K=298.15,w_MDEA=w,observed_J_g_K=obs,predicted_J_g_K=pred,error_percent=100*(pred/obs-1)))
        for w,series in cp.CONCEPCION.items():
            for T,obs in series.items():
                pred,rho=cp.cp_mass(model,T,w,P=1e5)
                rows.append(dict(case=label,source='Concepcion 2023 Table 6',T_K=T,w_MDEA=w,observed_J_g_K=obs,predicted_J_g_K=pred,error_percent=100*(pred/obs-1)))
        for r in csv.DictReader((p.DATA/'Sobrino2016_stage1.csv').open()):
            if float(r['pressure_MPa'])!=.1:continue
            T,w=float(r['temperature_K']),float(r['MDEA_mass_fraction'])
            _,pred=cp.cp_mass(model,T,w,P=1e5);obs=float(r['density_kg_m3'])
            density.append(dict(case=label,T_K=T,w_MDEA=w,observed_kg_m3=obs,predicted_kg_m3=pred,error_kg_m3=pred-obs,error_percent=100*(pred/obs-1)))
    cp.write_csv(OUT/'cp-comparison.csv',rows);cp.write_csv(OUT/'density-comparison.csv',density)
    summary=[]
    for label,_,_ in cases:
        record={'case':label}
        for source in ('Weiland','Concepcion'):
            errors=[r['error_percent'] for r in rows if r['case']==label and r['source'].startswith(source)]
            record[source+'_AARD_percent']=float(np.mean(np.abs(errors)));record[source+'_min_percent']=min(errors);record[source+'_max_percent']=max(errors)
        errors=[r for r in density if r['case']==label]
        record.update(Sobrino_rows=len(errors),Sobrino_AARD_percent=float(np.mean([abs(r['error_percent']) for r in errors])),Sobrino_mean_kg_m3=float(np.mean([r['error_kg_m3'] for r in errors])),Sobrino_max_abs_kg_m3=max(abs(r['error_kg_m3']) for r in errors))
        summary.append(record)
    write('property-summary.json',summary)
    return max(abs(r['error_percent']) for r in rows if r['case']==cases[0][0] and r['source'].startswith('Weiland') and r['w_MDEA']<=.5)<=5

def main():
    wheel=Path(json.loads((AN/'inputs/runtime.json').read_text())['wheel'])
    assert p.sha(wheel)==p.shared.ENGINE_WHEEL_SHA256
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):assert z.read(name)==(Path(p.epcsaft.__file__).parent.parent/name).read_bytes(),name
    workers=os.cpu_count()
    write('runtime.json',dict(engine_commit='3e83e19ccc771b51d8ebc038931ab25192f4c5b5',wheel=str(wheel),wheel_sha256=p.sha(wheel),module=p.epcsaft.__file__,installed_files_byte_identical=True,cpu_count=os.cpu_count(),workers=workers,BLAS_threads_per_process=1))
    if '--finish-gates' in sys.argv:
        fits=[json.loads((OUT/f'fit-{name}.json').read_text()) for name in ('primary','secondary')]
        assert all(r['usable'] and r['status']=='converged' for r in fits)
        a=fits[0]['physical']
        assert json.loads((OUT/'initialization-agreement.json').read_text())['passed']
        rows=list(csv.DictReader((OUT/'cp-comparison.csv').open()))
        cp_pass=max(abs(float(r['error_percent'])) for r in rows if r['case']=='linear + Neumann' and float(r['T_K'])==298.15 and float(r['w_MDEA'])<=.5)<=5
    else:
        source=copy.deepcopy(cp.CALORICS);source['components'][M].update(coefficients=CUBIC,source='Neumann et al. 2022, CA5R9QN8, Eq. 5 / Table 8; retained diagnosis cubic',enthalpy_entropy_anchor_k=313.15)
        write('physical-ideal-gas-calorics.json',source)
        write('wangler-sensitivity.json',cp.CALORICS)
        params,model=binary((-.1818,0.))
        model=p.epcsaft.Mixture(params,thermochemistry=thermal(params))
        s=model.state(313.15,rho=1e5/(cp.R*313.15),x={M:1.},derived_properties=True)
        worst=max(abs(np.polynomial.polynomial.polyval(T,CUBIC)/cp.neumann_ideal_cp(T)-1) for T in np.arange(293.,423.05,.1))
        assert worst<1.3e-4 and abs(s.ideal_enthalpy)<1e-9 and abs(s.ideal_entropy)<1e-9
        write('ideal-gas-check.json',dict(coefficients=CUBIC,max_relative_deviation=worst,temperature_range_K=[293.,423.],step_K=.1,anchor_K=313.15,ideal_enthalpy_J_mol=s.ideal_enthalpy,ideal_entropy_J_mol_K=s.ideal_entropy))
        items=[reg.observation(params,'pressure',k.bubble(r),observed=float(r['total_pressure_kPa'])*1000,form='log_ratio') for r in k.ROWS]
        controls=dict(maximum_iterations=100,function_tolerance=1e-6,parameter_tolerance=1e-10,gradient_tolerance=1e-8,maximum_elapsed_time_seconds=60,workers=min(workers,len(items)))
        declaration=dict(family='temperature_law_coefficient',identities=[IDENTITY+'/a0',IDENTITY+'/a1'],scales=[.01,.001],bounds=[[-.5,.5],[-.01,.01]],slope_bound_basis='Diagnostic computational bound; not a physical prior.',controls=controls,weight=1,rows=len(items))
        write('declaration.json',declaration)
        fits=[]
        for name,start in [('primary',-.1818),('secondary',-.15)]:
            params,_=binary((start,0.))
            coords=[reg.coordinate(params,[('temperature_law_coefficient',IDENTITY+f'/a{i}',1.)],origin=v,scale=scale,bounds=bounds) for i,(v,scale,bounds) in enumerate(zip((start,0.),declaration['scales'],declaration['bounds']))]
            initial=reg.differentiate(params,coords,items,optimizer=[0.,0.])
            jac=np.array(initial.residual_optimizer_gradient).reshape(-1,2)
            write(f'initial-{name}.json',dict(singular_values=np.linalg.svd(jac,compute_uv=False).tolist(),statuses=initial.statuses))
            fitted=reg.fit(params,coords,items,weights=[1.]*len(items),controls=reg.FitControls(**controls),singular_vectors=True)
            result=fitted_result(fitted,items);write(f'fit-{name}.json',result);fits.append(result)
            print(name,result['status'],result['physical'],result['AARD_percent'],flush=True)
        a,b=[r['physical'] for r in fits]
        agreement=all(r['usable'] for r in fits) and abs(a[0]-b[0])<=1e-4 and abs(a[1]-b[1])<=1e-6
        write('initialization-agreement.json',dict(passed=agreement,absolute_difference=[abs(x-y) for x,y in zip(a,b)],tolerances=[1e-4,1e-6]))
        if not agreement:return
        doc=d.document('A',None);linear(doc,a);write('binary-endpoint.json',doc)
        cp_pass=properties(a);print('Cp 298K gate',cp_pass,flush=True)
        if not cp_pass:
            write('gate-status.json',dict(prefit=True,Cp_298K=False,binary=None,Carson=None,stage2_ready=False,reason='Unloaded Cp error exceeds 5 percent at 298.15 K, within the <=50 wt% claim domain; return to Design.'))
            print('STOP: return to Design; no further phase checks or amended starts',flush=True)
            return
    assert cp_pass
    # Reuse item-(k)'s declared phase search unchanged with the new binary law.
    k.binary_model=binary
    grid=sorted({0.,1.}|{10**(-6+5*i/40) for i in range(41)}|{i/200 for i in range(1,200)}|{1-10**(-6+5*i/40) for i in range(41)})
    jobs=[(a,float(r['temperature_C'])+273.15,float(r['liquid_x_MDEA']),float(r['total_pressure_kPa'])*1000,'Kim-'+r['source_row']) for r in k.ROWS]
    jobs += [(a,T,x,d.P,f'grid-{T}-{x}') for T in (293.15,313.15,353.15,393.15) for x in grid]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        scans=list(pool.map(scan,[(a,T) for T in (293.15,313.15,353.15,393.15)]));write('mixing-scans.json',scans)
        checks=[]
        for record in pool.map(phase_check,jobs):
            checks.append(record)
            if len(checks)%100==0:print('binary searches',len(checks),'/',len(jobs),flush=True)
        write('binary-phase-search.json',checks)
    binary_pass=all(r['miscible'] for r in scans) and all(r['liquid_miscible'] and r['pass_search'] for r in checks)
    write('gate-status.json',dict(prefit=True,Cp_298K=cp_pass,binary=binary_pass,Carson=None,stage2_ready=False))
    if not cp_pass or not binary_pass:
        print('STOP: return to Design; no Carson search or amended starts',flush=True);return
    hashes={}
    for path in sorted((AN/'inputs/amended-starts').glob('[AB][134].json')):
        doc=json.loads(path.read_text());linear(doc,a);write('amended-starts/'+path.name,doc)
        hashes[path.stem]=dict(sha256=p.sha(OUT/'amended-starts'/path.name),calorics_sha256=p.sha(OUT/'physical-ideal-gas-calorics.json'),coordinates=[dict(family='temperature_law_coefficient',identity=IDENTITY+f'/a{i}',origin=v) for i,v in enumerate(a)])
    for v in 'AB':hashes[v+'2']=dict(duplicate_of=v+'1',run=False,**hashes[v+'1'])
    write('amended-starts/hashes.json',hashes)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        records=list(pool.map(reactive,[(label,label[0],row) for label in hashes if not label.endswith('2') for row in ('1','10')]))
    write('amended-carson-search.json',records)
    carson_pass=all(r.get('liquid',{}).get('requested_tolerance_met') and r.get('completed') and not r.get('split',True) and 'unresolved trials 0' in r.get('message','') for r in records)
    write('gate-status.json',dict(prefit=True,Cp_298K=cp_pass,binary=binary_pass,Carson=carson_pass,item_l_complete=bool(binary_pass and carson_pass and cp_pass),stage2_ready=bool(binary_pass and carson_pass and cp_pass),independent_review_pending=True,reason='Item (l) gates pass; starts ready for stage 2, which was not run.' if carson_pass else 'Carson gate fails; return to Design.'))
    for r in records:print('Carson',r['probe'],r['source_row'],r.get('message'),r.get('error'),flush=True)
if __name__=='__main__':main()
