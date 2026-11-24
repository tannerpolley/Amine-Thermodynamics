from pathlib import Path
from part_ii import ROOT, Route, stable
from verify import dump,RUN,np
from decompose import off, parent, describe, split_records,phase_terms,TERMS, tpd, try_attempts

work=ROOT/'analyses/mdea_mea_workflow'
route=Route(work/'inputs/bounded-binary-411.json',RUN/'mdea')
lowdir,=(work/'results/shared-bicarbonate-417/mdea').glob('mdea-low-*')
low=stable.read(lowdir/'endpoint.json.gz')
reported=stable.read(work/'results/bounded-binary-411/endpoint.json')
ab=stable.read(work/'results/phase-search-421/fixed-pressure.json')
src=[(s['key'], low,s['temperature_K'],s['pressure_Pa'],s['feed_mol'],next(a for a in s['attempts'] if a['confirmed']))
     for s in stable.read(lowdir/'stability.json.gz')['pressure_roots'] if s['phase_identity']=='two liquids']
src+=[('reported-262MPa',reported,ab['T_K'],ab['P_Pa'],ab['feed'],next(a for a in ab['attempts'] if a['confirmed']))]
original=stable.read(RUN/'mdea.json')
key='pair/bicarbonate-anion/water/k_ij'
k=stable.s.parameter_values(reported['parameters'])[key]
out=[]
for i,(name,point,T,P,feed,ret) in enumerate(src):
    pair=split_records(ret)
    old=original[i]['parent']
    settings={'Born off':off(point)}
    if i<2:
        settings['reported water-bicarbonate only']=dict(point,parameters=stable.s.with_parameter_values(point['parameters'],{key:k}))
    for label,c in settings.items():
        r=dict(key=name,label=label,k=k if label.startswith('reported') else None)
        out.append(r)
        try:
            spec=route.bind(c)
            pr,res,report=parent(spec,T,P,feed,old)
            pp=describe(res)
            S=np.array(report.standard_over_rt)
            r['old_pair_minus_new_parent']=dict(zip(TERMS,sum(phase_terms(spec.model,T,P,p,S) for p in pair)-phase_terms(spec.model,T,P,pp,S)))
            r['distances']=[tpd(spec.model,T,P,np.array(pp['x']),p['x'],S)['total'] for p in pair]
            r['attempts']=try_attempts(spec,pr,res,report,[pp,*pair],pair[0])
        except (RuntimeError,ValueError,AssertionError) as error:
            r['refusal']=str(error)
            print(name,label,str(error),flush=True)
dump('mdea-controls.json',out)
