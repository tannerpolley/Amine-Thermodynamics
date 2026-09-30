"""MEA-side bounded least squares: exact interaction and checked FD reaction columns."""
import time
STARTED=time.perf_counter()
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
import p4 as chemistry
import born_form_diagnosis as d

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('continuation',ROOT/'p5conv-fit.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def main(form):
    name=f'p4refit-{form}'
    c.setup(name);d.DEADLINE=STARTED+2380.
    source=ROOT/'p4-results.json'
    prior=next(r for r in json.loads(source.read_text()) if r['form']==form)
    point=prior['predictions']['joint-five-k']['estimates'][1]
    x0=np.r_[point['k'],point['q']]
    lower=np.r_[d.LOWER,-chemistry.LIMIT];upper=np.r_[d.UPPER,chemistry.LIMIT]
    scales=np.r_[d.SCALES,[1.,1.,1.,1.]]
    d.save(name+'-start-hash.json',dict(path=str(source),sha256=d.s.sha256(source),point=x0.tolist(),script_sha256=d.s.sha256(Path(__file__))))
    cache={};history=[];columns=[];counts=dict(function_calls=0,complete_jacobians=0,accepted_updates=0)
    best=None;last_jacobian_s=0.

    def objective(x,label,fit_point=False):
        nonlocal best
        key=tuple(map(float,x))
        if key not in cache:
            d.enough(55.)
            rec=d.evaluate(name+'-'+label,chemistry.mapping(form,x[5:],x[:5]),form)
            c.check_branches(rec,form);cache[key]=rec
        rec=cache[key]
        if fit_point:
            history.append(dict(evaluation=label,cost=rec['cost'],x=list(key),elapsed_s=time.perf_counter()-STARTED))
            d.save(name+'-history.json',history)
            if best is None or rec['cost']<best[1]['cost']:best=(np.array(x),rec)
            summary(x,rec,'running')
        return np.asarray(rec['weighted_residuals'])

    def summary(x,rec,reason,optimizer=None):
        result=dict(name=name,form=form,cost=rec['cost'],three_group_cost={k:rec[k] for k in ('pressure_cost','bottinger_cost','matin_cost')},
            species_costs_and_signed_residuals=c.species(rec['targets'],rec['weighted_residuals']),k_coordinates=dict(zip(d.IDS,map(float,x[:5]))),
            directions=dict(zip(chemistry.LABELS,map(float,x[5:]))),recorded_comparison=chemistry.recorded(form,x[5:]),
            active_k_bounds=c.active(x[:5]),active_reaction_bounds=[label for label,q,limit in zip(chemistry.LABELS,x[5:],chemistry.LIMIT) if abs(abs(q)-limit)<1e-7],
            stopping_reason=reason,counts=counts.copy(),wall_s=time.perf_counter()-STARTED,
            reaction_gradient_quality='two-step finite differences, pointwise agreement checked; no exact reaction derivatives',
            interaction_gradient_quality='exact Engine derivatives',covariance='not estimated',
            evidence='local bounded numerical fit; no physical validation or adoption',initial_cost=prior['actual_cost'])
        if optimizer is not None:result['optimizer']=optimizer
        c.save_summary(name,result)
        return result

    def fun(z):
        counts['function_calls']+=1
        return objective(z*scales,f'objective-{counts["function_calls"]:03d}',True)

    def jac(z):
        nonlocal last_jacobian_s
        d.enough(max(60.,last_jacobian_s+70.))
        begun=time.perf_counter();x=z*scales;index=counts['complete_jacobians']+1
        r0=objective(x,f'jac{index:02d}-origin')
        native,_=d.fitted(name+f'-jac{index:02d}-exact-k',chemistry.mapping(form,x[5:],x[:5]),form)
        assert np.max(abs(np.asarray(native['weighted_residuals'])-r0))<1e-8
        jfile=d.HERE/(name+f'-jac{index:02d}-exact-k-jacobian.json')
        Jk=np.asarray(json.loads(jfile.read_text())['weighted_physical_jacobian'])
        Jq=[];coarse=[]
        for j in range(4):
            attempts=[]
            for attempt,rhos in enumerate(((1e-4,1e-5),(1e-3,1e-4))):
                pair=[]
                for rho in rhos:
                    at=5+j;h=rho*max(abs(x[at]),1.)
                    left=x[at]-lower[at];right=upper[at]-x[at]
                    if min(left,right)>=h:
                        xp=x.copy();xm=x.copy();xp[at]+=h;xm[at]-=h
                        rp=objective(xp,f'jac{index:02d}-q{j}-a{attempt}-r{rho:g}-plus')
                        rm=objective(xm,f'jac{index:02d}-q{j}-a{attempt}-r{rho:g}-minus')
                        derivative=(rp-rm)/(2*h);method='central'
                    else:
                        sign=1 if right>=left else -1
                        h=min(h,max(left,right)/2)
                        assert h>0
                        x1=x.copy();x2=x.copy();x1[at]+=sign*h;x2[at]+=sign*2*h
                        r1=objective(x1,f'jac{index:02d}-q{j}-a{attempt}-r{rho:g}-one')
                        r2=objective(x2,f'jac{index:02d}-q{j}-a{attempt}-r{rho:g}-two')
                        derivative=sign*(-3*r0+4*r1-r2)/(2*h);method='second-order one-sided'
                    pair.append(derivative)
                ratio=abs(pair[0]-pair[1])/(1e-3*np.maximum(abs(pair[0]),abs(pair[1]))+1e-8)
                attempts.append(dict(relative_steps=list(rhos),method=method,agreeing_entries=int(sum(ratio<=1)),total_entries=160,
                    maximum_difference_over_tolerance=float(max(ratio)),coarse_column=pair[0].tolist(),fine_column=pair[1].tolist()))
                if np.all(ratio<=1):break
            rec=dict(jacobian=index,coordinate=chemistry.LABELS[j],available=bool(np.all(ratio<=1)),attempts=attempts,entries_dropped_or_zeroed=0)
            columns.append(rec);d.save(name+'-finite-difference-quality.json',columns)
            print('REACTION COLUMN',form,index,j,rec['available'],float(max(ratio)),flush=True)
            if not rec['available']:raise ValueError('reaction column unavailable after two-step retry; no entries discarded')
            coarse.append(pair[0]);Jq.append(pair[1])
        J=np.column_stack([Jk,np.column_stack(Jq)])
        Jcoarse=np.column_stack([Jk,np.column_stack(coarse)])
        d.save(name+f'-jacobian-{index:02d}.json',dict(x=x.tolist(),coordinates=d.IDS+chemistry.LABELS,
            weighted_physical_jacobian=J.tolist(),coarse_weighted_physical_jacobian=Jcoarse.tolist(),
            singular_values_scaled=np.linalg.svd(J*scales,compute_uv=False).tolist(),reaction_gradient_quality='finite differences',k_gradient_quality='exact'))
        counts['complete_jacobians']+=1;last_jacobian_s=time.perf_counter()-begun
        return J*scales

    def callback(intermediate_result):
        counts['accepted_updates']+=1
        print('ACCEPTED UPDATE',form,counts['accepted_updates'],float(intermediate_result.cost),flush=True)
        if counts['accepted_updates']>=20:raise StopIteration

    reason='unavailable';optimizer=None
    try:
        opt=least_squares(fun,x0/scales,jac=jac,bounds=(lower/scales,upper/scales),method='trf',
            ftol=1e-8,xtol=1e-8,gtol=1e-8,max_nfev=100,callback=callback)
        optimizer=dict(status=int(opt.status),message=str(opt.message),success=bool(opt.success),nfev=int(opt.nfev),njev=int(opt.njev),optimality=float(opt.optimality))
        reason='converged' if opt.success else '20 accepted-update cap' if opt.status==-2 else str(opt.message)
    except TimeoutError as error:reason='time limit before completing the next Jacobian';optimizer=dict(message=str(error))
    except ValueError as error:
        if 'reaction column unavailable' not in str(error):raise
        reason=str(error)
    if best is None:raise RuntimeError('no complete evaluated fit point')
    x,rec=best
    final=chemistry.mapping(form,x[5:],x[:5]);final['purpose']='MEA #121 exploratory reaction warm refit; diagnosis only, not adopted.'
    (ROOT/(name+'-diagnostic-parameters.json')).write_text(json.dumps(final,indent=2)+'\n')
    result=summary(x,rec,reason,optimizer)
    print('RESULT',json.dumps(result),flush=True)

if __name__=='__main__':
    form=sys.argv[1];name=f'p4refit-{form}';status='complete'
    try:main(form)
    except BaseException as error:
        status='failed';d.save(name+'-failure.json',dict(exception=type(error).__name__,message=str(error)));raise
    finally:
        (ROOT/(name+'-time.json')).write_text(json.dumps(dict(name=name,status=status,wall_s=time.perf_counter()-STARTED,timeout_s=2400,threads=1,lock=False,script_sha256=d.s.sha256(Path(__file__))),indent=2)+'\n')
