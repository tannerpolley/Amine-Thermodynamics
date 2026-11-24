import copy, math
from verify import amp_inputs, dump, np, eq, thermo
from decompose import parent, describe, try_attempts, split_records, off, contribution, TERMS
from part_ii import stable, epcsaft, jsonable
from scipy.linalg import null_space

a, route, point, fixed = amp_inputs()
T,P,feed=(a[k] for k in ('T_K','P_Pa','feed_mol'))
spec=route.bind(point)
standard=np.array(a['standard_over_rt'])
z=np.array([spec.spec['element_formulas'][id]['charge'] for id in spec.parameters.component_ids])
E=null_space(np.vstack([np.ones(len(z)),z]))
hs=[]
for p in a['phases']+[a['trial']]:
    m=spec.model
    x=np.array(p['x'])
    anchor=m.state(T,P=P,x=x,phase='liquid')
    cols=[]
    for d in E.T:
        act=m.pressure_actions(T,P,x=x,phase='liquid',anchor=anchor,observables=[epcsaft.PropertyObservable.LogFugacityCoefficient],
                               directions=[epcsaft.PressureActionDirection(composition=d)])
        cols.append(E.T@(d/x+np.array([q.action for q in act.results])))
    H=np.array(cols).T
    scales=np.linalg.cholesky(E.T@(E/x[:,None]))
    scaled=np.linalg.solve(scales,np.linalg.solve(scales,H).T).T
    eig,U=np.linalg.eigh((scaled+scaled.T)/2)
    dx=E@np.linalg.solve(scales.T,U[:,0])
    maxh=min(x[dx!=0]/abs(dx[dx!=0]))
    err=[]
    for h in [maxh*q for q in (.1,.03,.01)]:
        def eval_at(sign):
            y=x+sign*h*dx
            s=m.state(T,P=P,x=y,phase='liquid')
            return np.log(y*s.molar_density)+s.residual_chemical_potential_over_rt+standard, math.fsum(contribution(s,T,P,y,standard))
        mup,gp=eval_at(1)
        mum,gm=eval_at(-1)
        val=math.fsum(contribution(anchor,T,P,x,standard))
        err.append(dict(h=h,mu_fd=dx@(mup-mum)/(2*h),g_fd=(gp+gm-2*val)/h**2))
    hs.append(dict(eig=eig,symmetry=np.max(abs(scaled-scaled.T)),branch=anchor.returned_density_branch.name,
                   min_dir=dx,finite_differences=err))
dump('amp-hessian.json',hs)

def coeff(mapping):
    return [next(q['value']['magnitude'] for q in c['coefficients'] if q['family']=='solvation_factor') for c in mapping['components']]

mapping=point['parameters']
factors=np.array(coeff(mapping))
assert (factors[z!=0]==1).all()
key='component/carbon-dioxide/solvation_factor'
assert list(spec.model.component_ids).index('carbon-dioxide')==0
def energy(x,replacement=None):
    x=np.asarray(x)
    alternate=float(x[1:]@factors[1:]/x[1:].sum())
    m=epcsaft.Mixture(epcsaft.Parameters.from_mapping(stable.s.with_parameter_values(mapping,{key:alternate})),thermochemistry=spec.thermal)
    st=m.state(T,P=P,x=x,phase='liquid')
    return contribution(st,T,P,x,standard),alternate,st.molar_density
before,*split=a['phases']
row=[energy(p['x']) for p in a['phases']+[a['trial']]]
bulk=sum(p['amount_mol']*terms for p,(terms,_,_) in zip(split,row[1:3],strict=True))-before['amount_mol']*row[0][0]
x0=np.array(before['x']); delta=np.array(a['trial']['x'])-x0
d=[]
for h in (1e-3,3e-4,1e-4):
    vals=[energy(x0+i*h*delta)[0] for i in (-2,-1,1,2)]
    tangent=(vals[0]-8*vals[1]+8*vals[2]-vals[3])/(12*h)
    d.append(dict(h=h,tpd=math.fsum(row[-1][0]-row[0][0]-tangent)))
dump('figiel-fixed-geometries.json',dict(factors=factors,values=row,split_minus_frozen_parent=dict(zip(TERMS,bulk)),tpd_against_frozen_parent=d))

b=route.bind(off(point))
pr,res,report=parent(b,T,P,feed,before)
branch=[]
for p in a['phases']+[a['trial']]:
    x=np.array(p['x'])
    rho=p['density_mol_m3']
    st=spec.model.state(T,rho=rho,x=x)
    nob=b.model.state(T,rho=rho,x=x)
    root=b.model.state(T,P=P,x=x,phase='liquid')
    branch.append(dict(rho=root.molar_density,branch=root.returned_density_branch.name,
                       preserved_terms={term:getattr(st,term)-getattr(nob,term) for term in TERMS[1:-1] if term!='born'},
                       permittivity_error=st.bulk_relative_permittivity-nob.bulk_relative_permittivity,
                       born_value=nob.born))
dump('born-off-roots.json',branch)
opt=eq.StabilityOptions()
opt.mode=type(opt.mode).Full
native=eq.stability_test(eq.compile_problem(b.model,pr),res,opt)
trials=[dict(msg=t.message,resolved=t.resolved_descent,composition=t.composition,q=t.quantities) for t in native.trials]
dump('born-off-search.json',trials)
