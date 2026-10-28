"""Replay the bound-stopped A1 endpoint and its Carson single-liquid states."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import concurrent.futures,importlib.util,json,multiprocessing,types
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('joint',AN/'scripts/fit_mdea.py');j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
p,d=j.p,j.d
OUT='results/joint-fit/A1'
fit=json.loads((AN/OUT/'fit.json').read_text());decl=json.loads((AN/OUT/'declaration.json').read_text())
doc=json.loads((AN/'inputs/amended-starts/A1.json').read_text())
values=iter(fit['physical'])
for coord in decl['coordinates']:
    for family,target,factor in coord['targets']:
        value=next(values)
        block=next(c for c in doc['components'] if c['component_id']==target) if isinstance(target,str) else next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}==set(target))
        next(c for c in block['coefficients'] if c['family']==family)['value']['magnitude']=value
assert next(values,None) is None
params=p.epcsaft.Parameters.from_mapping(doc);thermal=d.a.caloric_record(params);model=p.epcsaft.Mixture(params,thermochemistry=thermal)
meta,items,weights=j.objective(params)

def replay(i):
    prediction=j.reg.predict(model,items[i])
    retained=dict(meta[i],prediction=p.shared._jsonable(prediction))
    if prediction.status.name=='Available':retained['relative_replay_error']=abs(prediction.value-fit['predictions'][i])/max(abs(fit['predictions'][i]),1.)
    return retained

def carson(row_id):
    row=d.ROWS[row_id];problem=j.problem(298.15,101325.,row['water'],row['alpha'])
    state=j.eq.solve_equilibrium(model,problem)
    d.f.s=types.SimpleNamespace(COMPONENT_IDS=d.SPECIES,_jsonable=p.shared._jsonable)
    report=d.f.stability(model,problem,state)
    return dict(source_row=row_id,alpha=row['alpha'],success=state.success,requested_tolerance_met=state.requested_tolerance_met,max_residual=max(map(abs,state.residuals)),stability=report,**d.summary(report,list(params.component_ids)))

if __name__=='__main__':
    p.write(f'{OUT}/endpoint.json',doc)
    available=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    workers=min(os.cpu_count(),max(1,available//268435456),len(items))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        replayed=list(pool.map(replay,range(len(items))))
        checks=list(pool.map(carson,('1','10')))
    p.write(f'{OUT}/replay.json',replayed);p.write(f'{OUT}/carson-phase.json',checks)
    maximum=max(r.get('relative_replay_error',float('inf')) for r in replayed)
    assert maximum<=1e-8
    p.write(f'{OUT}/verification.json',dict(rows=len(replayed),maximum_relative_replay_error=maximum,tolerance=1e-8,workers=workers,available_memory_bytes=available,BLAS_threads_per_process=1,endpoint_sha256=p.sha(AN/OUT/'endpoint.json')))
    print('Replay maximum error',maximum,flush=True)
    for r in checks:print('Carson',r['source_row'],r['message'],r['split_delta_g_over_rt'],flush=True)
