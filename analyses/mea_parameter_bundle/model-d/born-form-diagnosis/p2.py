"""Bounded local weighted least squares using complete two-step Born-input columns."""
import time
STARTED = time.perf_counter()
import json
from pathlib import Path
import numpy as np
from scipy.optimize import lsq_linear
import born_form_diagnosis as d

GROUPS = {**d.GROUPS, 'joint': list(range(8))}


def baseline(form):
    rec=json.loads((d.HERE/f'baseline-{form}.json').read_text())
    jac=json.loads((d.HERE/f'baseline-{form}-jacobian.json').read_text())
    assert rec['targets']==jac['targets']
    return rec,np.asarray(rec['weighted_residuals']),np.asarray(jac['weighted_physical_jacobian'])


def sample(form,j,rho,offset):
    base=d.values(d.MAPPINGS[form])[d.QIDS[j]]
    h=rho*max(abs(base),1.)
    name=f'fd-{form}-q{j}-rho{rho:g}-offset{offset:g}'
    path=d.HERE/(name+'.json')
    target=base+offset*h
    lo,hi=d.QBOUNDS[j]
    assert lo <= target <= hi
    if path.exists():
        out=json.loads(path.read_text());assert out['inputs'][d.QIDS[j]]==target
        return np.asarray(out['weighted_residuals'])
    out=d.evaluate(name,d.changed(d.MAPPINGS[form],{d.QIDS[j]:target}),form)
    assert out['targets']==baseline(form)[0]['targets']
    return np.asarray(out['weighted_residuals'])


def column(form,j,rho,r0):
    base=d.values(d.MAPPINGS[form])[d.QIDS[j]]
    lo,hi=d.QBOUNDS[j];h=rho*max(abs(base),1.)
    if base-h<lo or base+h>hi:
        sign=1 if base-h<lo else -1
        a=sample(form,j,rho,sign);b=sample(form,j,rho,2*sign)
        return sign*(-3*r0+4*a-b)/(2*h),'second-order-one-sided'
    return (sample(form,j,rho,1)-sample(form,j,rho,-1))/(2*h),'central'


def finite_difference(form,j):
    rec,r0,_=baseline(form)
    attempts=[]
    for rhos in ((1e-4,1e-5),(1e-3,1e-4)):
        try:
            a,formula=column(form,j,rhos[0],r0);b,_=column(form,j,rhos[1],r0)
        except (RuntimeError,TimeoutError) as error:
            result={'form':form,'coordinate':d.QIDS[j],'available':False,'attempts':attempts,
                    'reason':str(error),'interpretation':'unavailable for attribution; no physical disposition'}
            d.save(f'column-{form}-q{j}.json',result);return result
        tolerance=1e-3*np.maximum(np.abs(a),np.abs(b))+1e-8
        delta=np.abs(a-b);ratio=delta/tolerance
        attempts.append({'relative_steps':list(rhos),'formula':formula,
            'jacobian_first':a.tolist(),'jacobian_second':b.tolist(),
            'max_absolute_step_difference':float(delta.max()),
            'max_difference_over_tolerance':float(ratio.max()),
            'median_difference_over_tolerance':float(np.median(ratio)),
            'p95_difference_over_tolerance':float(np.quantile(ratio,.95)),
            'agreeing_entries':int(np.count_nonzero(ratio<=1.)),'total_entries':160})
        if np.all(ratio<=1.):
            result={'form':form,'coordinate':d.QIDS[j],'available':True,'attempts':attempts,
                    'jacobian_first':a.tolist(),'jacobian_second':b.tolist()}
            d.save(f'column-{form}-q{j}.json',result)
            print('COLUMN',form,j,'available',attempts[-1]['max_difference_over_tolerance'],flush=True)
            return result
    result={'form':form,'coordinate':d.QIDS[j],'available':False,'attempts':attempts,
            'reason':'step disagreement after one retry; no entries dropped or zeroed'}
    d.save(f'column-{form}-q{j}.json',result)
    print('COLUMN',form,j,'unavailable',attempts[-1]['max_difference_over_tolerance'],flush=True)
    return result


def category(reduction):
    return 'not supported locally' if reduction<1.86 else 'inconclusive' if reduction<3.71 else 'confirmation required'


def bounded(form,Jq,qindices):
    rec,r,Jk=baseline(form)
    v=d.values(d.MAPPINGS[form]);k0=np.array([v[i] for i in d.IDS])
    lo=list(d.LOWER-k0);hi=list(d.UPPER-k0)
    for j in qindices:
        a,b=d.QBOUNDS[j];limit=(b-a)/2.;q0=v[d.QIDS[j]]
        lo.append(max(a-q0,-limit));hi.append(min(b-q0,limit))
    lo=np.asarray(lo);hi=np.asarray(hi)
    scales=np.r_[(d.UPPER-d.LOWER)/2.,[(d.QBOUNDS[j][1]-d.QBOUNDS[j][0])/2. for j in qindices]]
    A=np.column_stack([Jk,Jq]) if len(qindices) else Jk
    solved=lsq_linear(A*scales,-r,bounds=(lo/scales,hi/scales),method='trf',lsq_solver='exact',tol=1e-12,max_iter=1000)
    delta=solved.x*scales
    assert solved.success and np.all(delta>=lo-1e-10) and np.all(delta<=hi+1e-10)
    finalk=k0+delta[:5]
    assert d.design.admissible(d.IDS,finalk,'40-80')
    return {'local_cost':float(.5*np.dot(r+A@delta,r+A@delta)),
        'delta_k':delta[:5].tolist(),'delta_q':delta[5:].tolist(),
        'k_at_predicted_step':finalk.tolist(),
        'q_at_predicted_step':{d.QIDS[j]:float(v[d.QIDS[j]]+dq) for j,dq in zip(qindices,delta[5:])},
        'lsq_optimality':float(solved.optimality),'lsq_message':solved.message}


def screening(form,columns,groups):
    rec,r,Jk=baseline(form)
    base=bounded(form,np.empty((160,0)),[])
    results=[]
    for name,idx in groups.items():
        if any(not columns[j]['available'] for j in idx):
            results.append({'group':name,'form':form,'available':False,'classification':'unavailable',
                            'reason':'one or more complete columns unavailable'});continue
        predictions=[]
        for key in ('jacobian_first','jacobian_second'):
            Jq=np.column_stack([columns[j][key] for j in idx])
            point=bounded(form,Jq,idx)
            point['predicted_reduction_vs_five_k_only']=base['local_cost']-point['local_cost']
            point['classification']=category(point['predicted_reduction_vs_five_k_only'])
            predictions.append(point)
        agree=predictions[0]['classification']==predictions[1]['classification']
        results.append({'group':name,'form':form,'available':agree,'classification':predictions[1]['classification'] if agree else 'unavailable',
                        'classification_agreement':agree,'five_k_only_cost':base['local_cost'],
                        'candidate_indices':idx,'predictions':predictions})
    return results


def main():
    columns={};symmetry={}
    for j in range(9): columns[j]=finite_difference('11',j)
    for j in range(3): symmetry[j]=finite_difference('00',j)
    results=screening('11',columns,{**{f'single-q{j}':[j] for j in range(9)},**GROUPS})
    results+=screening('00',symmetry,{**{f'single-q{j}':[j] for j in range(3)},'main-diameters':[0,1,2]})
    sv={};collinearity=[]
    for form,cols in [('11',columns),('00',symmetry)]:
        _,_,Jk=baseline(form)
        if not all(v['available'] for v in cols.values()):
            sv[form]={'available':False,'reason':'whole augmented Jacobian includes an unavailable column'}
        else:
            matrices=[]
            for key in ('jacobian_first','jacobian_second'):
                J=np.column_stack([Jk,*[cols[j][key] for j in cols]])
                norm=np.linalg.norm(J,axis=0)
                assert np.all(norm>0), 'zero complete column requires attribution unavailable'
                matrices.append({'step':key,'physical_singular_values':np.linalg.svd(J,compute_uv=False).tolist(),
                    'column_normalized_singular_values':np.linalg.svd(J/norm,compute_uv=False).tolist(),
                    'physical_rank':int(np.linalg.matrix_rank(J)),
                    'column_normalized_rank':int(np.linalg.matrix_rank(J/norm))})
            sv[form]={'available':True,'matrices':matrices}
        for j,c in cols.items():
            if not c['available']: continue
            q=np.asarray(c['jacobian_second']);projection=Jk@np.linalg.lstsq(Jk,q,rcond=None)[0]
            collinearity.append({'form':form,'coordinate':d.QIDS[j],
                'fraction_norm_in_k_span':float(np.linalg.norm(projection)/np.linalg.norm(q)),
                'fraction_norm_orthogonal_to_k_span':float(np.linalg.norm(q-projection)/np.linalg.norm(q)),
                'maximum_absolute_cosine_with_one_k_column':float(max(abs(np.dot(q,Jk[:,i]))/(np.linalg.norm(q)*np.linalg.norm(Jk[:,i])) for i in range(5)))})
    d.table('p2-collinearity.csv',collinearity)
    d.save('p2-screening.json',{'groups':GROUPS,'screens':results,'singular_values':sv,
        'interpretation':'local numerical screen, not significance or broad rejection; all bounds and active k bounds respected'})
    summary=[]
    for result in results:
        summary.append({'form':result['form'],'group':result['group'],'available':result['available'],
            'classification':result['classification'],
            'predicted_reduction_first':result.get('predictions',[{},{}])[0].get('predicted_reduction_vs_five_k_only'),
            'predicted_reduction_second':result.get('predictions',[{},{}])[1].get('predicted_reduction_vs_five_k_only')})
    d.table('p2-screening.csv',summary)
    usable=[r for r in results if r['form']=='11' and r['group'] in GROUPS and r['group']!='joint' and r['available']]
    best=max(usable,key=lambda r:r['predictions'][1]['predicted_reduction_vs_five_k_only']) if usable else None
    joint=next(r for r in results if r['form']=='11' and r['group']=='joint')
    selected=[]
    for label,result in [('best-group',best),('joint-group',joint)]:
        if result is None or not result['available']: continue
        point=result['predictions'][1]
        changes={**dict(zip(d.IDS,point['k_at_predicted_step'])),**point['q_at_predicted_step']}
        mapping=d.changed(d.MAPPINGS['11'],changes)
        try:
            actual=d.evaluate('p2-predicted-'+label,mapping)
        except (RuntimeError,TimeoutError) as error:
            selected.append({'label':label,'group':result['group'],'available':False,'reason':str(error)});continue
        selected.append({'label':label,'group':result['group'],'available':True,'changes':changes,
                         'actual_cost':actual['cost'],'actual_reduction':baseline('11')[0]['cost']-actual['cost']})
    d.save('p2-selected-steps.json',selected)
    print('P2 SCREENS',json.dumps(summary),flush=True)


if __name__=='__main__':
    status='complete'
    try:main()
    except BaseException as error:
        status='failed';d.save('p2-job-failure.json',{'exception':type(error).__name__,'message':str(error)});raise
    finally:
        d.save('job-times.json',d.OLD_JOBS+[{'job':'p2','wall_s':time.perf_counter()-STARTED,'status':status,
                    'script_sha256':d.s.sha256(Path(__file__))}])
