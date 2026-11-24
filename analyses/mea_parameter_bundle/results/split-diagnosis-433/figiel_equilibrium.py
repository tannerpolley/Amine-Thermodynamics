"""Independent local coexistence check for the ions-and-solvents Born average."""
import math
from functools import lru_cache
from part_ii import epcsaft, stable
from verify import amp_inputs, dump, np, R
from decompose import parent, contribution
from scipy.optimize import root

a, route, point, _ = amp_inputs()
T,P,feed=(a[k] for k in ('T_K','P_Pa','feed_mol'))
point0=route.bind(point)
mapping=point['parameters']
key='component/carbon-dioxide/solvation_factor'
S0=np.array(a['standard_over_rt'])
indices=[0,1,2]
form=[point0.spec['element_formulas'][i] for i in point0.model.component_ids]
z=np.array([f['charge'] for f in form])
M = np.array([[f.get(e,0) for f in form] for e in 'CNO'])
M4 = np.array([[f.get(e,0) for f in form] for e in 'CHNO'])
target=M@feed
nu=np.array([r['stoichiometry'] for r in a['declaration']['reactions']])
factors=np.array([next(q['value']['magnitude'] for q in c['coefficients'] if q['family']=='solvation_factor') for c in mapping['components']])
assert (factors[z!=0]==1).all()
assert np.linalg.matrix_rank(np.vstack([M,z]))==4 and np.all(M@nu.T==0) and np.all(z@nu.T==0)
assert np.linalg.matrix_rank(nu[:,[3,4,5,6,7,8]])==5

# At the pure-water reference the subset average tends to the water factor.
# The composition-dependent part of the Born derivative is multiplied by ion amount
# and vanishes there. Test the completion's numerical invariance to CO2's factor.
constant=dict(point,parameters=stable.s.with_parameter_values(mapping,{key:1.5}))
_,_,std_control=parent(route.bind(constant),T,P,feed,a['phases'][0])
S=np.array(std_control.standard_over_rt)

@lru_cache(maxsize=16)
def model(f):
    pars=epcsaft.Parameters.from_mapping(stable.s.with_parameter_values(mapping,{key:f}))
    return epcsaft.Mixture(pars,thermochemistry=point0.thermal)
def state(x, step):
    f=float(x[1:]@factors[1:]/x[1:].sum())
    st=model(f).state(T,P=P,x=x,phase='liquid')
    assert st.returned_density_branch.name=='Liquid'
    # Only Born consumes this coefficient. Use the same T,V,n in the stencil.
    slope=0.
    for j,c in zip((-2,-1,1,2),(1,-8,8,-1),strict=True):
        slope+=c*model(f+j*step).state(T,rho=st.molar_density,x=x).born
    slope/=12*step
    df=np.r_[0.,(factors[1:]-f)/x[1:].sum()]
    mu=np.log(x*st.molar_density)+st.residual_chemical_potential_over_rt+S+slope*df
    return st,mu

keep=[0,1,4,5,6,7,8]
basis=np.delete(np.eye(len(z))-z[:,None]*np.eye(len(z))[3],3,axis=0)
def enc(p):
    x=np.array(p['x'])
    return np.r_[np.log(x[keep]/x[2]),np.log(p['amount_mol'])]
def dec(q):
    x=np.ones(len(z))
    x[keep]=np.exp(q[:-1])
    x[3]=-z[keep]@x[keep]
    if x[3]<=0:
        raise ValueError('Nonpositive protonated AMP in neutral composition chart')
    return x/x.sum(), np.exp(q[-1])
def solve(phases, fstep):
    def parse(q):
        return [dec(v) for v in q.reshape(-1,8)]
    def residual(q):
        pairs=parse(q)
        mu=[state(x,fstep)[1] for x,n in pairs]
        atoms=(M@sum(x*n for x,n in pairs)-target)/target
        rx=[nu@u for u in mu]
        return np.concatenate([atoms,*rx,*([ (mu[0]-mu[1])[indices] ] if len(pairs)==2 else [])])
    sol=root(residual,np.concatenate([enc(p) for p in phases]),options=dict(xtol=3e-10, eps=3e-9,maxfev=300))
    pairs=parse(sol.x)
    detail=[]; potentials=[]
    for x,n in pairs:
        st,mu=state(x,fstep)
        potentials.append(mu)
        detail.append(dict(x=x, amount_mol=n, rho=st.molar_density, P_error_Pa=st.pressure-P,
                           charge=x@z, reaction=nu@mu, g=math.fsum(contribution(st,T,P,x,S))))
    return dict(termination=sol.message,max_eq_residual=np.max(abs(residual(sol.x))),phase=detail,
                element_error=M4@(sum(x*n for x,n in pairs)-feed),
                equilibrium_check=(basis@(potentials[0]-potentials[1]) if len(pairs)==2 else None),
                bulk_g=math.fsum(p['amount_mol']*p['g'] for p in detail))

out=[]
for h in (3e-3,1e-3):
    par=solve(a['phases'][:1],h)
    split=solve(a['phases'][1:],h)
    out.append(dict(h=h,parent=par,split=split,delta_g=split['bulk_g']-par['bulk_g']))
dump('figiel-equilibrium.json',dict(standard_control_difference=S-S0,runs=out))
