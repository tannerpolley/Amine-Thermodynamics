"""Native capped-heat value and nine-coordinate derivative acceptance for #222."""
import importlib.util
import sys
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('acceptance',AN/'scripts/accept_engine_delivery.py')
a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
s=a.s

def item(row,cap):
    T=float(row['temperature_K']);P=float(row['proposed_pressure_kPa'])*1000;nw=s.j.water(float(row['MDEA_mass_percent'])/100)
    return s.reg.saturation_capped_addition_enthalpy(s.params,s.j.problem(T,P,nw,0.),s.j.problem(T,P,nw,.5,True),{s.j.C:1.},basis_amount=1.,loading_cap=cap,loading_bounds=(.05,1.5),loading_grid=[.05*i for i in range(1,31)],T=T,P=P,phase='vapor',observed=float(row['heat_kJ_mol_CO2'])*1000,form='difference',scale=3000.)

def check(job):
    label,row,cap,reference,derivatives=job
    doc=s.load(f'results/item-l/amended-starts/{label}.json')
    pair=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={s.j.W,s.j.H})
    if not any(c['family']=='k_ij_reciprocal_temperature_slope' for c in pair['coefficients']):s.d.set_pair(doc,s.j.W,s.j.H,pair['coefficients'][0]['value']['magnitude'],0.)
    s.setup(doc);obs=item(row,cap);pred=s.reg.predict(s.model,obs)
    result=dict(start=label,row=row,loading_cap=cap,reference_J_mol=reference,status=pred.status.name,message=pred.message,value=pred.value)
    result['value_relative_error']=abs(pred.value/reference-1) if pred.status.name=='Available' else None
    result['passed']=pred.status.name=='Available' and result['value_relative_error']<=1e-8
    if derivatives:
        coords,decl=s.j.coordinates(s.params,doc,label[0]);zero=[0.]*9
        exact=s.reg.differentiate(s.params,coords,[obs],optimizer=zero,thermochemistry=s.thermal)
        result['exact']=list(exact.optimizer_gradient);result['central_differences']=[]
        for step in (.003,.001):
            for i in range(9):
                values=[]
                for sign in (-1,1):
                    point=zero.copy();point[i]=sign*step
                    q=s.reg.differentiate(s.params,coords,[obs],optimizer=point,thermochemistry=s.thermal)
                    values.append(q.predictions[0])
                fd=(values[1]-values[0])/(2*step);ex=exact.optimizer_gradient[i]
                result['central_differences'].append(dict(coordinate=i,step=step,exact=ex,finite_difference=fd,relative_error=abs(fd-ex)/abs(ex)))
        result['passed'] &= all(min(r['relative_error'] for r in result['central_differences'] if r['coordinate']==i)<=1e-5 for i in range(9))
    return result

if __name__=='__main__':
    a.identity();ref=s.load('results/stage2-density/merkley-fit-capability.json');jobs=[]
    for r in ref['rows']:jobs.append((r['start'],r['row'],r['alpha_LP'],r['heat_J_mol_CO2'],False))
    for r in ref['both_branch_acceptance_reference']:jobs.append(('A1',r['row'],r['alpha_LP'],r['heat_J_mol_CO2'],True))
    records=a.n.pool(check,jobs)
    a.n.write('capped-heat-acceptance.json',dict(passed=all(r['passed'] for r in records),records=records))
    print([(r['start'],r['row']['temperature_K'],r['loading_cap'],r['passed'],r['value_relative_error']) for r in records],flush=True)
