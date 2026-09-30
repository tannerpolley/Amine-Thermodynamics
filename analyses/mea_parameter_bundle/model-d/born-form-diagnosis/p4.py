"""Exploratory reduced-reaction directions; finite-difference reaction gradients."""
import time
STARTED=time.perf_counter()
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import lsq_linear
import born_form_diagnosis as d

R=8.31446261815324
TREF=313.15
LABELS=['carbamate_delta_lnK','carbamate_delta_H_kJ_mol','bicarbonate_delta_lnK','bicarbonate_delta_H_kJ_mol']
LIMIT=np.array([1.,10.,1.,10.])
P4_JOBS=[j for j in d.OLD_JOBS if j['job'].startswith('p4')]
d.DEADLINE=STARTED+900.-sum(j.get('charged_s',j['wall_s']) for j in P4_JOBS)
original_declared=d.declared

def mapping(form,q,k=None):
    dc,hc,db,hb=q
    changes={}
    for rx,delta,h in [('R2',db,hb),('R4',db-dc,hb-hc)]:
        p=f'reaction:{rx}:correlation:';v=d.values(d.MAPPINGS[form])
        changes[p+'a']=v[p+'a']+delta+1000*h/(R*TREF)
        changes[p+'b_k']=v[p+'b_k']-1000*h/R
        assert abs((changes[p+'a']-v[p+'a'])+(changes[p+'b_k']-v[p+'b_k'])/TREF-delta)<1e-12
    if k is not None:changes.update(dict(zip(d.IDS,k)))
    out=d.changed(d.MAPPINGS[form],changes)
    before=d.s.reaction_values(d.MAPPINGS[form]);after=d.s.reaction_values(out)
    assert all(after[i]==v for i,v in before.items() if not i.startswith(('reaction:R2:','reaction:R4:')))
    assert len(out['components'])==9
    return out

def declared(candidate,form):
    original_declared(d.MAPPINGS[form],form) # Preserve the accepted initial guesses.
    reactions=d.s.reaction_values(candidate)
    return [(o,d.s._problem_from_request(d.s.corrected_request(o['request'],reactions),
             d.s.anchor_from(d.ANCHORS[form][o['identity']]))) for o in d.OBS]

d.declared=declared # Only this process permits the owner-authorized R2/R4 perturbations.

def evaluate(form,q,k,name):
    path=d.HERE/(name+'.json')
    if path.exists():return json.loads(path.read_text())
    d.enough(28.)
    return d.evaluate(name,mapping(form,q,k),form)

def column(form,j,r0):
    attempts=[]
    for rhos in ((1e-4,1e-5),(1e-3,1e-4)):
        jac=[]
        for rho in rhos:
            # Direction origins are zero; scale = 1 ln K or 1 kJ/mol.
            samples=[]
            for sign in (1,-1):
                q=np.zeros(4);q[j]=sign*rho
                rec=evaluate(form,q,None,f'p4-fd-{form}-q{j}-rho{rho:g}-sign{sign}')
                samples.append(np.asarray(rec['weighted_residuals']))
            jac.append((samples[0]-samples[1])/(2*rho))
        tol=1e-3*np.maximum(abs(jac[0]),abs(jac[1]))+1e-8
        ratio=abs(jac[0]-jac[1])/tol
        attempts.append({'relative_steps':list(rhos),'jacobian_first':jac[0].tolist(),'jacobian_second':jac[1].tolist(),
            'agreeing_entries':int(sum(ratio<=1)), 'total_entries':160,'max_difference_over_tolerance':float(max(ratio))})
        if np.all(ratio<=1):break
    out={'form':form,'coordinate':LABELS[j],'gradient_quality':'finite difference; exact EOS interaction columns separate',
        'available':bool(np.all(ratio<=1)), 'attempts':attempts,'entries_dropped_or_zeroed':0}
    d.save(f'p4-column-{form}-q{j}.json',out)
    print('P4 COLUMN',form,j,out['available'],float(max(ratio)),flush=True)
    return out

def solve(form,Jq,include_k):
    base=json.loads((d.HERE/f'baseline-{form}.json').read_text());r=np.asarray(base['weighted_residuals'])
    Jk=np.asarray(json.loads((d.HERE/f'baseline-{form}-jacobian.json').read_text())['weighted_physical_jacobian'])
    k=np.asarray([d.values(d.MAPPINGS[form])[i] for i in d.IDS])
    A=np.column_stack([Jk,Jq]) if include_k else Jq
    lo=np.r_[d.LOWER-k,-LIMIT] if include_k else -LIMIT
    hi=np.r_[d.UPPER-k,LIMIT] if include_k else LIMIT
    scale=np.r_[(d.UPPER-d.LOWER)/2,LIMIT] if include_k else LIMIT
    result=lsq_linear(A*scale,-r,bounds=(lo/scale,hi/scale),tol=1e-12,max_iter=1000,lsq_solver='exact')
    assert result.success
    step=result.x*scale;k1=k+step[:5] if include_k else k
    assert d.design.admissible(d.IDS,k1,'40-80')
    q=step[-4:];cost=float(.5*np.dot(r+A@step,r+A@step))
    screens=json.loads((d.HERE/'p2-screening.json').read_text())['screens']
    k_only=next(s['five_k_only_cost'] for s in screens if s['form']==form and 'five_k_only_cost' in s)
    return {'predicted_cost':cost,'predicted_reduction':base['cost']-cost,'q':q.tolist(),'k':k1.tolist(),
        'five_k_only_local_cost':k_only,'predicted_reduction_vs_five_k_only':k_only-cost,
        'reaction_gradient_quality':'finite differences','k_gradient_quality':'exact Engine derivatives','covariance':'not estimated'}

def recorded(form,q):
    v=d.s.reaction_values(d.MAPPINGS[form]);t=TREF
    ln2=v['reaction:R2:correlation:a']+v['reaction:R2:correlation:b_k']/t+v['reaction:R2:correlation:c']*math.log(t)+v['reaction:R2:correlation:d_per_k']*t
    ln4=v['reaction:R4:correlation:a']+v['reaction:R4:correlation:b_k']/t
    ln5=-math.log(10)*(v['reaction:R5:correlation:a_k']/t+v['reaction:R5:correlation:b']+v['reaction:R5:correlation:c_per_k']*t)
    h2=-R*(v['reaction:R2:correlation:b_k']-v['reaction:R2:correlation:c']*t-v['reaction:R2:correlation:d_per_k']*t*t)/1000
    h4=-R*v['reaction:R4:correlation:b_k']/1000
    h5=R*math.log(10)*(v['reaction:R5:correlation:a_k']-v['reaction:R5:correlation:c_per_k']*t*t)/1000
    return {'basis':'recorded source-correlation combination, before EOS standard-state conversion; local enthalpy from -R d ln K/d(1/T) at 313.15 K',
        'carbamate_lnK_recorded':ln2-ln4-ln5,'bicarbonate_lnK_recorded':ln2-ln5,
        'carbamate_H_recorded_kJ_mol':h2-h4-h5,'bicarbonate_H_recorded_kJ_mol':h2-h5,
        'carbamate_lnK_result':ln2-ln4-ln5+q[0],'bicarbonate_lnK_result':ln2-ln5+q[2],
        'carbamate_H_result_kJ_mol':h2-h4-h5+q[1],'bicarbonate_H_result_kJ_mol':h2-h5+q[3]}

def main():
    results=[]
    for form in ('11','00'):
        base=json.loads((d.HERE/f'baseline-{form}.json').read_text());r=np.asarray(base['weighted_residuals'])
        cols=[]
        try:
            for j in range(4):cols.append(column(form,j,r))
            if not all(c['available'] for c in cols):
                results.append({'form':form,'available':False,'reason':'whole reaction column unavailable; no attribution'});continue
            predictions={}
            for label,use_k in [('reaction-alone',False),('joint-five-k',True)]:
                points=[solve(form,np.column_stack([c['attempts'][-1][key] for c in cols]),use_k) for key in ('jacobian_first','jacobian_second')]
                cats=[('not supported locally' if p['predicted_reduction']<1.86 else 'inconclusive' if p['predicted_reduction']<3.71 else 'confirmation required') for p in points]
                predictions[label]={'estimates':points,'classification_agreement':cats[0]==cats[1], 'thresholds':'descriptive original-gap screens only; P4 is exploratory'}
            if not all(p['classification_agreement'] for p in predictions.values()):
                results.append({'form':form,'available':False,'predictions':predictions,'reason':'classification disagrees across Jacobians'});continue
            point=predictions['joint-five-k']['estimates'][1]
            actual=evaluate(form,point['q'],point['k'],f'p4-predicted-joint-{form}')
            out={'form':form,'available':True,'predictions':predictions,'actual_cost':actual['cost'],
                'actual_reduction':base['cost']-actual['cost'],'actual_three_group_cost':{i:actual[i] for i in ('pressure_cost','bottinger_cost','matin_cost')},
                'directions':dict(zip(LABELS,point['q'])),'recorded_comparison':recorded(form,point['q']),
                'warm_refit':'not completed; budget reserved for two-step columns and actual predicted-step costs',
                'evidence':'exploratory bounded local prediction and actual numerical evaluation, no adoption'}
            results.append(out);d.save('p4-results.json',results)
        except (TimeoutError,RuntimeError) as error:
            results.append({'form':form,'available':False,'reason':str(error),'completed_columns':len(cols),'interpretation':'unavailable; not physics evidence'})
            d.save('p4-results.json',results)
            if isinstance(error,TimeoutError):break
    d.save('p4-results.json',results)

if __name__=='__main__':
    status='complete'
    try:main()
    except BaseException as error:
        status='failed';d.save('p4-job-failure.json',{'exception':type(error).__name__,'message':str(error)});raise
    finally:
        d.save('job-times.json',d.OLD_JOBS+[{'job':'p4','wall_s':time.perf_counter()-STARTED,'status':status,'budget_s':900.,'script_sha256':d.s.sha256(Path(__file__))}])
