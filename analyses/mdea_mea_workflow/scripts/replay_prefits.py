"""Qualify retained Kim/item-(l) numerical evidence on the isolated MDEA wheel."""
import importlib.util
import sys
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('acceptance',AN/'scripts/accept_engine_delivery.py')
a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
s=a.s;n=a.n
spec=importlib.util.spec_from_file_location('linear',AN/'results/item-l/run.py')
l=importlib.util.module_from_spec(spec);sys.modules[spec.name]=l;spec.loader.exec_module(l)
k=s.j.k

def phase(job):
    kind,args=job
    return l.phase_check(args) if kind=='linear' else k.phase_check(args)

def scan(job):
    kind,args=job
    return l.scan(args) if kind=='linear' else k.scan(args)

def carson(job):
    label,row=job
    doc=s.load(f'results/item-l/amended-starts/{label}.json');s.setup(doc)
    r=next(r for r in s.j.rows('Carson2000_stage1.csv') if r['source_row']==row)
    w=float(r['MDEA_mass_fraction']);x=float(r['x_CO2']);alpha=x/(1-x)*(1+s.j.water(w))
    s.phase_jobs=[(label+':'+row,s.j.problem(298.15,101325.,s.j.water(w),alpha))]
    return s.phase(0)

if __name__=='__main__':
    a.identity();summaries={}
    grid=sorted({0.,1.}|{10**(-6+5*i/40) for i in range(41)}|{i/200 for i in range(1,200)}|{1-10**(-6+5*i/40) for i in range(41)})
    for kind,folder in [('linear','item-l'),('reciprocal','kim-prefit')]:
        ref=s.load(f'results/{folder}/fit-primary.json' if kind=='linear' else f'results/{folder}/fit.json');values=ref['physical']
        params,model=l.binary(values) if kind=='linear' else k.binary_model(values)
        items=[s.reg.observation(params,'pressure',k.bubble(r),observed=float(r['total_pressure_kPa'])*1000,form='log_ratio') for r in k.ROWS]
        predictions=[s.reg.predict(model,item) for item in items]
        errors=[abs(r.value/v-1) if r.status.name=='Available' else float('inf') for r,v in zip(predictions,ref['predictions'],strict=True)]
        n.write(f'prefit-{kind}-predictions.json',[dict(row=row,value=p.value,status=p.status.name,message=p.message,relative_error=e) for row,p,e in zip(k.ROWS,predictions,errors)])
        jobs=[(values,float(r['temperature_C'])+273.15,float(r['liquid_x_MDEA']),float(r['total_pressure_kPa'])*1000,'Kim-'+r['source_row']) for r in k.ROWS]
        jobs += [(values,T,x,s.d.P,f'grid-{T}-{x}') for T in (293.15,313.15,353.15,393.15) for x in grid]
        records=n.pool(phase,[(kind,j) for j in jobs]);n.write(f'prefit-{kind}-phase.json',records)
        scans=n.pool(scan,[(kind,(values,T)) for T in (293.15,313.15,353.15,393.15)])
        n.write(f'prefit-{kind}-mixing.json',scans)
        summary=dict(rows=len(items),max_relative_replay_error=max(errors),phase_states=len(records),dense_splits=sum(not r['liquid_miscible'] for r in records),unresolved=sum('unresolved trials 0' not in r['report']['message'] for r in records),hull_miscible=all(r['miscible'] for r in scans))
        summary['passed']=max(errors)<=1e-8 and not summary['dense_splits'] and not summary['unresolved'] and summary['hull_miscible']
        summaries[kind]=summary;print(kind,summary,flush=True)
    # Retain the identical property computation on the new wheel in the acceptance directory.
    l.OUT=AN/a.OUT
    l.write=lambda name,obj:n.write('item-l-'+name,obj)
    property_pass=l.properties(s.load('results/item-l/fit-primary.json')['physical'])
    records=n.pool(carson,[(label,row) for label in ('A1','A3','B1','B3') for row in ('1','10')]);n.write('prefit-carson.json',records)
    summaries.update(Cp_pass=property_pass,Carson_pass=all(r['density_gate']['passed'] for r in records))
    summaries['passed']=summaries['linear']['passed'] and summaries['reciprocal']['passed'] and property_pass and summaries['Carson_pass']
    n.write('prefit-acceptance.json',summaries);print(summaries,flush=True)
