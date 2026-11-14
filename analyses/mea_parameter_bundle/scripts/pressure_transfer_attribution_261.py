"""Fixed-volume finite-difference attribution of neutral fugacities (#261)."""
import copy,math,os
from concurrent.futures import ProcessPoolExecutor
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import numpy as np
from MEA.solvent_specification import SolventSpecification
from pressure_transfer_261 import OUT,verify,write,WHEEL_SHA
from epcsaft import equilibrium as eq
verify()
S=SolventSpecification('analyses/mea_parameter_bundle/results/adoption-340/historical-spec/MEA.toml')
R=next(r for r in S.inputs['observations']['fitted'] if r['kind']=='partial_pressure')
TERMS=['hard_chain','dispersion','association','debye_huckel','born']
def job(args):
 T,a,w=args;p=copy.copy(S.problems[R['problem']]);p.T=T
 feed=dict(p.feed.values);feed['carbon-dioxide']=a-0.0001;feed['water']=(1-w)/w*61.084/18.01528-0.00021
 p.feed=eq.Amounts(feed)
 state=eq.solve_equilibrium(S.model,p)
 assert state.success and state.requested_tolerance_met, state.message
 n=len(S.model.component_ids);x=np.array(state.mole_fractions[:n])
 # Evaluate Engine at the retained equilibrium density.
 liquid=S.model.state(T,rho=state.molar_densities[0],x=x)
 base=np.array([getattr(liquid,t) for t in TERMS]);rho=liquid.molar_density
 assert abs(base.sum()-liquid.residual_helmholtz)<1e-10
 rows=[]
 for i in range(3):
  for h in (1e-4,5e-5,2.5e-5):
   values=[]
   for d in (h,2*h):
    ns=x.copy();ns[i]+=d
    z=S.model.state(T,rho=rho*(1+d),x=ns/(1+d))
    values.append((1+d)*np.array([getattr(z,t) for t in TERMS]))
   mu=(-3*base+4*values[0]-values[1])/(2*h)
   phi=liquid.log_fugacity_coefficient[i];closure=sum(mu)-math.log(liquid.compressibility_factor)-phi
   rows.append(dict(species=S.model.component_ids[i],step=h,contributions=dict(zip(TERMS,mu.tolist())),log_phi=phi,closure=closure))
 return dict(engine_wheel_sha256=WHEEL_SHA,T=T,loading=a,wt_percent=w*100,pressure=state.pressure,residuals=list(state.residuals),x=x.tolist(),density=rho,terms=rows)
if __name__=='__main__':
 with ProcessPoolExecutor(os.cpu_count()) as pool:
  rows=list(pool.map(job,[(T,a,w) for T in (313.15,333.15,353.15) for a in (.1,.3,.5) for w in (.15,.30,.45)]))
 write(OUT/'matched-attribution.json',rows)
 checks=dict(finest_closure=max(abs(q['closure']) for r in rows for q in r['terms'] if q['step']==2.5e-5),finest_term_change=max(abs(a['contributions'][t]-b['contributions'][t]) for r in rows for a,b in zip(r['terms'][1::3],r['terms'][2::3],strict=True) for t in TERMS),tolerance=1e-5)
 write(OUT/'attribution-checks.json',checks)
 assert checks['finest_closure']<1e-5 and checks['finest_term_change']<1e-5,checks
 print('states',len(rows),'maximum closure',max(abs(q['closure']) for r in rows for q in r['terms']))
