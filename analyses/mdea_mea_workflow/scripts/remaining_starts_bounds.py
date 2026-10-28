"""Owner-authorized #222 remaining starts and one-change A1 diagnostics."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import concurrent.futures, importlib.util, json, multiprocessing, types, zipfile
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('joint',AN/'scripts/fit_mdea.py');j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
p,d=j.p,j.d
base_objective=j.objective
base_coordinates=j.coordinates
base_write=p.write

def endpoint_doc(label,fit,decl):
    doc=json.loads((AN/f'inputs/amended-starts/{label}.json').read_text())
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={j.W,j.H})
    if not any(c['family']=='k_ij_reciprocal_temperature_slope' for c in pair['coefficients']): d.set_pair(doc,j.W,j.H,pair['coefficients'][0]['value']['magnitude'],0.)
    values=iter(fit['physical'])
    for coord in decl['coordinates']:
        for family,target,factor in coord['targets']:
            value=next(values)
            block=next(c for c in doc['components'] if c['component_id']==target) if isinstance(target,str) else next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}==set(target))
            next(c for c in block['coefficients'] if c['family']==family)['value']['magnitude']=value
    assert next(values,None) is None
    return doc

def replay(i):
    prediction=j.reg.predict(model,items[i])
    assert prediction.status.name=='Available',str(prediction)
    value=float(prediction.value)
    return dict(meta[i],predicted=value,residual=(value-meta[i]['observed'])/meta[i]['scale'] if meta[i]['group'] in ('Cp','unloaded-density') else None,relative_replay_error=abs(value-reference[i])/max(abs(reference[i]),1.))

def carson(row_id):
    row=d.ROWS[row_id];prob=j.problem(298.15,101325.,row['water'],row['alpha'])
    state=j.eq.solve_equilibrium(model,prob)
    d.f.s=types.SimpleNamespace(COMPONENT_IDS=d.SPECIES,_jsonable=p.shared._jsonable)
    report=d.f.stability(model,prob,state)
    return dict(source_row=row_id,alpha=row['alpha'],success=state.success,requested_tolerance_met=state.requested_tolerance_met,max_residual=max(map(abs,state.residuals)),stability=report,**d.summary(report,list(model.component_ids)))

def verify(out,label,fit):
    global model,meta,items,reference
    decl=json.loads((AN/out/'declaration.json').read_text())
    doc=endpoint_doc(label,fit,decl);base_write(f'{out}/endpoint.json',doc)
    params=p.epcsaft.Parameters.from_mapping(doc);model=p.epcsaft.Mixture(params,thermochemistry=d.a.caloric_record(params))
    meta,items,weights=base_objective(params);reference=fit['predictions']
    # Refits omit only the declared observations. Report omitted groups too.
    keep=[i for i,m in enumerate(meta) if m['group'] not in removed]
    meta=[meta[i] for i in keep];items=[items[i] for i in keep]
    available=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    workers=min(os.cpu_count(),max(1,available//268435456),len(items))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        records=list(pool.map(replay,range(len(items))))
        checks=list(pool.map(carson,('1','10')))
    maximum=max(r['relative_replay_error'] for r in records);assert maximum<=1e-8,maximum
    base_write(f'{out}/replay.json',records);base_write(f'{out}/carson-phase.json',checks)
    base_write(f'{out}/verification.json',dict(maximum_relative_replay_error=maximum,tolerance=1e-8,rows=len(records),workers=workers))
    omitted=[]
    for m,item in zip(*base_objective(params)[:2]):
        if m['group'] in removed:
            pred=j.reg.predict(model,item);assert pred.status.name=='Available'
            omitted.append(dict(m,predicted=pred.value,residual=(pred.value-m['observed'])/m['scale']))
    base_write(f'{out}/omitted-group-residuals.json',omitted)
    print(out,'Carson',[(r['source_row'],r['completed'],r['split_delta_g_over_rt']) for r in checks],flush=True)

if __name__=='__main__':
    runtime=json.loads((AN/'inputs/runtime.json').read_text());wheel=Path(runtime['wheel'])
    assert p.sha(wheel)==p.shared.ENGINE_WHEEL_SHA256==runtime['wheel_sha256']
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'): assert z.read(name)==(Path(p.epcsaft.__file__).parent.parent/name).read_bytes(),name
    base_write('results/diagnosis-a1-bounds/runtime.json',dict(runtime,module=p.epcsaft.__file__,base_commit='2623829',installed_files_byte_identical=True))
    for case,label,removed,widen in [('A3','A3',[],False),('A4','A4',[],False),('B1','B1',[],False),('B3','B3',[],False),('without-unloaded-density','A1',['unloaded-density'],False),('without-Cp','A1',['Cp'],False),('without-both','A1',['unloaded-density','Cp'],False),('widened-bounds','A1',[],True)]:
        out=f'results/joint-fit/{case}' if case in ('A3','A4','B1','B3') else f'results/diagnosis-a1-bounds/{case}'
        def write(path,obj):base_write(path.replace(f'results/joint-fit/{label}',out),obj)
        p.write=write
        def objective(params):
            m,i,w=base_objective(params);keep=[n for n,r in enumerate(m) if r['group'] not in removed]
            return [m[n] for n in keep],[i[n] for n in keep],[w[n] for n in keep]
        j.objective=objective
        def coordinates(params,doc,variant):
            coords,decl=base_coordinates(params,doc,variant)
            if widen:
                for n,bounds in [(2,(-1.,1.)),(5,(-1.,2.)),(8,(1.,7.))]:decl[n]['bounds']=bounds
                coords=[j.reg.coordinate(params,q['targets'],origin=q['origin'],scale=q['scale'],bounds=q['bounds']) for q in decl]
            return coords,decl
        j.coordinates=coordinates
        try:
            if (AN/out/'fit.json').exists():fit=json.loads((AN/out/'fit.json').read_text())
            else:fit=j.run(label)
            verify(out,label,fit)
        except Exception as e:
            base_write(f'{out}/failure.json',dict(error=f'{type(e).__name__}: {e}'));print(case,'ERROR',repr(e),flush=True)
