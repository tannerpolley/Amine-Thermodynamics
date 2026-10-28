"""A1 fitted-row residuals and ion-free density invariance, #222 diagnosis."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import concurrent.futures,csv,importlib.util,json,multiprocessing
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('joint',AN/'scripts/fit_mdea.py');j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
p,d=j.p,j.d
OUT='results/diagnosis-a1-bounds'
fit=json.loads((AN/'results/joint-fit/A1/fit.json').read_text())
doc=json.loads((AN/'results/joint-fit/A1/endpoint.json').read_text())
params=p.epcsaft.Parameters.from_mapping(doc)
meta,items,weights=j.objective(params)
neutral=p.epcsaft.Parameters.from_mapping(doc,components=[p.M,p.W])
model=p.epcsaft.Mixture(neutral,thermochemistry=d.a.caloric_record(neutral))

def density(i):
    m=meta[i];r=m['row'];nw=j.water(float(r['MDEA_mass_fraction']))
    prob=j.eq.Problem(T=float(r['temperature_K']),P=1e5,feed=j.eq.Amounts({p.W:nw,p.M:1.}),phases=[j.eq.Phase('L',kind='liquid',support=[p.W,p.M])],row_tolerance=1e-10)
    item=j.reg.observation(neutral,'phase_density',prob,phase='L',mass_basis=True,observed=m['observed'],form='difference',scale=m['scale'])
    pred=j.reg.predict(model,item);assert pred.status.name=='Available'
    return dict(source_row=r['source_row'],temperature_K=float(r['temperature_K']),MDEA_mass_fraction=float(r['MDEA_mass_fraction']),observed_kg_m3=m['observed'],full_model_kg_m3=fit['predictions'][i],ion_free_kg_m3=pred.value,difference_kg_m3=pred.value-fit['predictions'][i])

if __name__=='__main__':
    out=AN/OUT;out.mkdir(exist_ok=True)
    records=[]
    for i,m in enumerate(meta):
        if m['group'] not in ('Cp','unloaded-density'):continue
        r=m['row'];pred=fit['predictions'][i];obs=m['observed'];scale=m['scale']
        w=float(r['MDEA_mass_fraction']);alpha=float(r.get('loading',0))
        factor=(1+j.water(w)+alpha)/(.1191622+j.water(w)*.01801528+alpha*.0440095)/1000 if m['group']=='Cp' else 1.
        records.append(dict(group=m['group'],source_row=r['source_row'],temperature_K=float(r.get('temperature_K',298.15)),MDEA_mass_fraction=w,loading=alpha,observed=obs*factor,predicted=pred*factor,units='J/g/K' if m['group']=='Cp' else 'kg/m3',difference=(pred-obs)*factor,scaled_residual=(pred-obs)/scale,weighted_residual=fit['weighted_residuals'][i],cost=.5*fit['weighted_residuals'][i]**2))
    with (out/'a1-density-cp-residuals.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=records[0],lineterminator="\n");writer.writeheader();writer.writerows(records)
    indices=[i for i,m in enumerate(meta) if m['group']=='unloaded-density']
    available=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    workers=min(os.cpu_count(),len(indices),max(1,available//268435456))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:values=list(pool.map(density,indices))
    maximum=max(abs(v['difference_kg_m3']) for v in values);assert maximum<1e-8
    jac=j.np.asarray(fit['optimizer_jacobian']).reshape(len(meta),9)
    max_ion_derivative=float(abs(jac[indices,2:]).max());assert max_ion_derivative<1e-10
    p.write(f'{OUT}/ion-free-density.json',dict(rows=values,maximum_difference_kg_m3=maximum,maximum_scaled_ion_derivative=max_ion_derivative,cost=sum(r['cost'] for r in records if r['group']=='unloaded-density'),basis='A1 MDEA-water reciprocal k; fixed pure MDEA; neutral-only support and no reactions; all ion coordinates removed',workers=workers))
    print('Ion-free density difference',maximum,'ion derivative',max_ion_derivative,flush=True)

    # Only the existing reciprocal MDEA-water law is free in this neutral diagnostic.
    coords=[]
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={p.M,p.W})
    for family,scale,bounds in [('k_ij',.01,(-.5,.5)),('k_ij_reciprocal_temperature_slope',10.,(-1000.,1000.))]:
        origin=next(c['value']['magnitude'] for c in pair['coefficients'] if c['family']==family)
        coords.append(j.reg.coordinate(neutral,[(family,(p.M,p.W),1.)],origin=origin,scale=scale,bounds=bounds))
    density_items=[]
    for i in indices:
        m=meta[i];r=m['row'];nw=j.water(float(r['MDEA_mass_fraction']))
        prob=j.eq.Problem(T=float(r['temperature_K']),P=1e5,feed=j.eq.Amounts({p.W:nw,p.M:1.}),phases=[j.eq.Phase('L',kind='liquid',support=[p.W,p.M])],row_tolerance=1e-10)
        density_items.append(j.reg.observation(neutral,'phase_density',prob,phase='L',mass_basis=True,observed=m['observed'],form='difference',scale=.5))
    fitted=j.reg.fit(neutral,coords,density_items,weights=[10.]*len(indices),thermochemistry=d.a.caloric_record(neutral),controls=j.reg.FitControls(maximum_iterations=40,function_tolerance=1e-10,parameter_tolerance=1e-10,gradient_tolerance=1e-8,maximum_elapsed_time_seconds=2100.,workers=workers),singular_vectors=True)
    result={q:p.shared._jsonable(getattr(fitted,q)) for q in ('status','message','usable','initial_cost','final_cost','physical','optimizer','predictions','residuals','weighted_residuals','iterations')}
    result['active_bounds']=list(fitted.covariance.active_bounds)
    p.write(f'{OUT}/ion-free-density-only-fit.json',result)
    print('Density-only fit',result['final_cost'],result['physical'],flush=True)
