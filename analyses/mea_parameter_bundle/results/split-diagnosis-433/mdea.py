from part_ii import ROOT, Route, stable
from verify import verify, dump, RUN, thermo, np
from decompose import parent, describe, phase_terms, split_records, profile, tpd, TERMS
import math

work = ROOT/'analyses/mdea_mea_workflow'
lowdir, = (work/'results/shared-bicarbonate-417/mdea').glob('mdea-low-*')
low = stable.read(lowdir/'endpoint.json.gz')
bounded = stable.read(work/'results/bounded-binary-411/endpoint.json')
route = Route(work/'inputs/bounded-binary-411.json',RUN/'mdea')
a = stable.read(work/'results/phase-search-421/fixed-pressure.json')
states = [(s['key'],low,s['temperature_K'],s['pressure_Pa'],s['feed_mol'],next(a for a in s['attempts'] if a['confirmed']))
          for s in stable.read(lowdir/'stability.json.gz')['pressure_roots'] if s['phase_identity']=='two liquids']
states += [('reported-262MPa',bounded,a['T_K'],a['P_Pa'],a['feed'],next(q for q in a['attempts'] if q['confirmed']))]
out = []
for key,point,T,P,feed,ret in states:
    r=dict(key=key, T=T,P=P,retained=ret)
    out.append(r)
    try:
        spec = route.bind(point)
        problem,pr,report = parent(spec,T,P,feed)
        pp=describe(pr)
        r['parent'] = pp
        pair=sorted(split_records(ret),key=lambda p:p['x'][1],reverse=True)
        m=spec.model
        standard=np.asarray(report.standard_over_rt)
        fs = [spec.spec['element_formulas'][c] for c in m.component_ids]
        r['verification'] = verify(m,T,P,[pp,*pair],standard,fs,[q.stoichiometry for q in problem.reactions],problem.feed.values)
        r['bulk'] = dict(zip(TERMS,sum(phase_terms(m,T,P,p,standard) for p in pair)-phase_terms(m,T,P,pp,standard)))
        r['tie'] = profile(m,T,P,[p['x'] for p in pair],standard)
        r['contacts'] = [{**p,'permittivity':m.state(T,rho=p['density_mol_m3'],x=p['x']).bulk_relative_permittivity,
                          'returned':m.state(T,P=P,x=p['x'],phase='liquid').returned_density_branch.name} for p in [pp,*pair]]
        r['trial_distances'] = [tpd(m,T,P,np.asarray(pp['x']),p['x'],standard) for p in pair]
    except (RuntimeError,ValueError,TypeError,AssertionError) as error:
        print(key,type(error).__name__,str(error),flush=True)
        r['refusal']=str(error)
dump('mdea.json',out)
