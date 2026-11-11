"""Issue 298 owner-amended 278-row replays and declared bounded fits."""
import os
os.environ['MDEA_ENGINE_WHEEL_SHA256']='0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'
import copy
import json
import time
from pathlib import Path
import refit_298 as r
import refit_capped as owner
s=owner.s
r.s=s
s.poolmap=owner.n.pool=r.pool
s.write=lambda name,value:r.write(name,s.p.shared._jsonable(value))
s.load=lambda name:r.read(r.AN/name)
owner.n.write=s.write
owner.n.load=s.load
s.OUT='results/refit-298'
owner.OUT=s.OUT
owner.n.OUT=s.OUT
original_objective=s.j.objective
def objective(params):
    metadata,items,weights=original_objective(params)
    keep=[i for i,m in enumerate(metadata) if not(m['group']=='Kuranov' and m['row']['source_row'] in ('28','72'))]
    assert len(keep)==278
    return tuple([[values[i] for i in keep] for values in (metadata,items,weights)])
s.j.objective=objective

def replay(doc,name):
    s.setup(doc)
    r.META,r.ITEMS,weights=s.j.objective(s.params)
    rows=r.pool(r.predict,list(range(len(r.ITEMS))))
    r.write(name+'/fitted-replay.json',rows)
    available=all(x['status']=='Available' and x['requested_tolerance_met'] for x in rows)
    independent=[( __import__('math').log(x['value']/x['meta']['observed']) if x['meta']['group'] in ('Kim','Kuranov') else (x['value']-x['meta']['observed'])/x['meta']['scale']) if x['value'] is not None else None for x in rows]
    error=max(abs(a-x['residual']) for a,x in zip(independent,rows) if a is not None)
    cost=sum(.5*w*x['residual']**2 for w,x in zip(weights,rows,strict=True)) if available else None
    groups={g:dict(rows=len(q:=[x for x in rows if x['meta']['group']==g]),scaled_RMS=(sum(x['residual']**2 for x in q)/len(q))**.5) for g in dict.fromkeys(x['meta']['group'] for x in rows)} if available else None
    summary=dict(rows=len(rows),available=available,cost=cost,groups=groups,max_independent_residual_error=error,passed=available and error<=1e-8)
    r.write(name+'/replay-summary.json',summary)
    print(name,summary,flush=True)
    return summary

if __name__=='__main__':
    r.identities()
    confirmation=r.read(r.OUT/'water-coefficient-confirmation.json')
    assert len(confirmation)==2 and all(x['passed'] for x in confirmation)
    original=next(x for x in s.j.d.REACTIONS if x.name=='R2').correlation
    reaction=next(x for x in s.j.d.REACTIONS if x.name=='R2')
    law=r.read(r.ADOPTION/'shared-R2.json')
    shared=r.read(r.ADOPTION/'shared-bicarbonate-water.json')
    summaries={}
    for label in ('A3','B1'):
        for adopted in (False,True):
            name=label+('-substitution-278' if adopted else '-baseline-278')
            doc=r.read(r.AN/f'results/stage2-capped/{label}/endpoint.json')
            reaction.correlation=s.eq.ReactionLogPolynomial(**law) if adopted else original
            if adopted:
                index=next(i for i,p in enumerate(doc['pairs']) if {p['component_id_a'],p['component_id_b']}=={'water','bicarbonate-anion'})
                doc['pairs'][index]=copy.deepcopy(shared)
            r.write(name+'/parameters.json',doc)
            summaries[name]=replay(doc,name)
    f1=r.read(r.OUT/'F1.json')
    f1.update(passed=all(x['passed'] for x in summaries.values()),explained_historical_difference=dict(cause='0e216fe replaced water ideal-gas calorics after the historical fits',confirmation=confirmation,coefficient_source='0e216fe^',scratch_only=True),rebased_278=summaries,execution_stopped_before_fitting=False,remaining_checks=['endpoint balances and derivatives','pressure replay'])
    r.write('F1.json',f1)
    assert f1['passed']
    reaction.correlation=s.eq.ReactionLogPolynomial(**law)
    attempts=[]
    for label,alternative in (('A3','A3'),('B1','B3')):
        for start in ('endpoint','alternative'):
            name=label+'-'+start
            doc=r.read(r.OUT/(label+'-substitution-278/parameters.json')) if start=='endpoint' else owner.start(alternative)
            index=next(i for i,p in enumerate(doc['pairs']) if {p['component_id_a'],p['component_id_b']}=={'water','bicarbonate-anion'})
            doc['pairs'][index]=copy.deepcopy(shared)
            r.write(name+'/start.json',doc)
            r.write(name+'/R2.json',law)
            s.setup(doc)
            coords,decl=s.j.coordinates(s.params,doc,label[0])
            meta,items,weights=s.j.objective(s.params)
            initial=s.reg.differentiate(s.params,coords,items,optimizer=[0.]*9,thermochemistry=s.thermal)
            jac=s.np.array(initial.residual_optimizer_gradient).reshape(-1,9)*s.np.sqrt(weights)[:,None]
            _,sv,right=s.np.linalg.svd(jac,full_matrices=False)
            r.write(name+'/initial-identifiability.json',dict(singular_values=sv.tolist(),right_vectors=right.tolist(),rank=int(s.np.linalg.matrix_rank(jac))))
            clock=time.monotonic()
            candidate,result=s.fit_document(doc,label[0],[q['bounds'] for q in decl],name)
            elapsed=time.monotonic()-clock
            attempt=dict(name=name,representation=label,start=start,wall_time_seconds=elapsed,status=result['status'],usable=result['usable'],cost=result['final_cost'],iterations=result['iterations'],active_bounds=result['covariance']['active_bounds'],rank=result['covariance']['rank'])
            attempts.append(attempt)
            r.write('attempts.json',attempts)
            print(attempt,flush=True)
