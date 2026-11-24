import copy
import math
import sys
from verify import RUN, amp_inputs, dump, thermo, np, eq, R
from part_ii import jsonable, calculation_declaration, epcsaft, reg
# The #255 module imports a historical wheel gate. Read its literal term list.
import ast
from part_ii import ROOT
legacy = ast.parse((ROOT/'analyses/mea_parameter_bundle/scripts/phase_diagnosis_255.py').read_text())
RESIDUAL_TERMS = next(ast.literal_eval(n.value) for n in legacy.body
                      if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'TERMS')
from amp_transfer.classify_descents import coexistence, pressure_roots
from scipy.optimize import brentq

TERMS = ['ideal/reaction', *RESIDUAL_TERMS, 'PV']

def contribution(st,T,P,x,standard):
    xs = np.asarray(x)
    ok = xs>0
    ideal = xs[ok] @ (np.log(xs[ok]*st.molar_density)-1+np.asarray(standard)[ok])
    residual = [getattr(st,t) for t in RESIDUAL_TERMS]
    assert abs(math.fsum(residual)-st.residual_helmholtz)<1e-10
    return np.array([ideal, *residual, P/(st.molar_density*R*T)])

def evaluate(model,T,P,x,standard):
    st = model.state(T,P=P,x=x,phase='liquid')
    if abs(st.pressure/P-1)>1e-10 or st.pressure_density_derivative <= 0:
        raise ValueError(f'Liquid pressure closure: {st.pressure/P-1}, {st.pressure_density_derivative}')
    return contribution(st,T,P,x,standard)

def tpd(model,T,P,z,y,standard):
    direction = np.asarray(y)-z
    def f(t):
        return evaluate(model,T,P,z+t*direction,standard)
    gz, gy = f(0.), f(1.)
    base = model.state(T,P=P,x=z,phase='liquid')
    mu = np.log(z*base.molar_density)+base.residual_chemical_potential_over_rt+standard
    exact = float(math.fsum(gy)-math.fsum(gz)-direction@mu)
    rows = []
    for h in (1e-3,3e-4,1e-4):
        if np.any(z-2*h*direction<=0):
            tangent = sum(c*f(j*h) for j,c in enumerate((-25,48,-36,16,-3)))/(12*h)
        else:
            tangent = (f(-2*h)-8*f(-h)+8*f(h)-f(2*h))/(12*h)
        rows.append(dict(h=h,terms=dict(zip(TERMS,gy-gz-tangent)),error=math.fsum(gy-gz-tangent)-exact))
    return dict(total=exact, detail=rows)

def profile(model,T,P,pair,standard):
    a,b = map(np.asarray,pair)
    direction = b-a
    def eval_at(t):
        x = a+t*direction
        st = model.state(T,P=P,x=x,phase='liquid')
        assert abs(st.pressure/P-1)<1e-10 and st.pressure_density_derivative>0
        mu = np.log(x*st.molar_density)+st.residual_chemical_potential_over_rt+standard
        return contribution(st,T,P,x,standard), direction@mu
    g0,s0 = eval_at(0)
    def slope(t):
        return eval_at(t)[1]-s0
    def dist(t):
        g, s = eval_at(t)
        return math.fsum(g-g0)-t*s0
    ts = np.linspace(0,1,51)
    ss = [slope(t) for t in ts]
    roots = [brentq(slope,u,v,xtol=1e-11) for u,v,f,g in zip(ts[:-1],ts[1:],ss[:-1],ss[1:]) if f*g<0]
    def row(t):
        h = .001
        if t<=h or t>=1-h:
            sign=1 if t<=h else -1
            c = [eval_at(t+j*h*sign)[0] for j in range(4)]
            curv = (2*c[0]-5*c[1]+4*c[2]-c[3])/h**2
            total=(slope(t+sign*h)-slope(t))/(sign*h)
        else:
            a,_ = eval_at(t-h)
            b,_ = eval_at(t+h)
            c,_ = eval_at(t)
            curv = (a+b-2*c)/h**2
            total=(slope(t+h)-slope(t-h))/(2*h)
        return dict(t=t,tpd=dist(t),slope=slope(t),curv=dict(zip(TERMS,curv)),total_curv=total)
    return dict(roots=roots,points=[row(t) for t in sorted(set([0., .25, .5, .75, 1., *roots]))],
                path=[dict(t=t,tpd=dist(t),slope=q) for t,q in zip(ts,ss)])

def describe(result):
    return dict(x=list(result.phase_mole_fractions(0)),density_mol_m3=result.molar_densities[0],amount_mol=result.amounts[0])

def parent(spec,T,P,feed,seed=None):
    template = next(p for p in spec.problems.values() if p.reactions)
    kwargs = {}
    if seed:
        kwargs = dict(composition_guess=seed['x'],packing_guess=seed['density_mol_m3']*
                 spec.model._model.packing_fraction_coefficient(T,seed['x']))
    problem = eq.Problem(T=T,P=P,feed=eq.Amounts(dict(zip(spec.parameters.component_ids,feed,strict=True)) if not isinstance(feed,dict) else feed),phases=[eq.Phase('L',kind='liquid',support=list(spec.parameters.component_ids),**kwargs)],
                         reactions=template.reactions,neutral_reference=template.neutral_reference,row_tolerance=template.row_tolerance)
    problem = reg.stability(spec.parameters,problem,scale=1.).problem
    result = eq.solve_equilibrium(spec.model,problem)
    if not result.requested_tolerance_met:
        raise ValueError(result.message)
    compiled = eq.compile_problem(spec.model,problem)
    report = eq.stability_test(compiled,result)
    return problem, result, report

def split_records(result):
    return [dict(x=x, density_mol_m3=rho, amount_mol=n) for x,rho,n in
            zip(result['phases'],result['densities_mol_m3'],result['amounts_mol'],strict=True)]

def phase_terms(model,T,P,phase,standard):
    return evaluate(model,T,P,phase['x'],standard)*phase['amount_mol']

def summary(spec,T,P,pp,phases,trial,standard,re_eq,report):
    model = spec.model
    gsplit = sum(phase_terms(model,T,P,p,standard) for p in phases[1:])
    free_parent = phase_terms(model,T,P,phases[0],standard)
    this_parent = phase_terms(model,T,P,pp,standard)
    pairs = [phases[2]['x'],phases[1]['x']]
    return dict(no_search_parent=pp,standard=standard,
        phase_states=[dict(permittivity=(st:=model.state(T,P=P,x=p['x'],phase='liquid')).bulk_relative_permittivity,rho=st.molar_density,
                           f_mix=p['x']@np.array([next((q['value']['magnitude'] for q in c['coefficients'] if q['family']=='solvation_factor'),1) for c in spec.inputs['endpoint']['parameters']['components']]))
                      for p in [pp,*phases,trial]],
        old_split_vs_old_parent=dict(zip(TERMS,gsplit-free_parent)),old_split_vs_own_parent=dict(zip(TERMS,gsplit-this_parent)),
        trial_vs_frozen_parent=tpd(model,T,P,np.array(phases[0]['x']),trial['x'],standard),
        trial_vs_own_parent=tpd(model,T,P,np.array(pp['x']),trial['x'],standard),
        tie_line=profile(model,T,P,pairs,standard),
        parent_to_trial=profile(model,T,P,[pp['x'],trial['x']],standard),
        re_equilibration=re_eq)

def try_attempts(spec,problem,pr,report,phases,trial):
    model=spec.model
    T,P=pr.temperature,pr.pressure
    def seed(ph):
        x=ph['x']
        st=model.state(T,P=P,x=x,phase='liquid')
        return x, st.molar_density * model._model.packing_fraction_coefficient(T,x)
    pp=describe(pr)
    gp=thermo(model,T,P,pp,np.array(report.standard_over_rt))[1]*pp['amount_mol']
    q=report.present_phases[0]
    err=pp['amount_mol']*sum(q[k] for k in ('association_energy_estimate_over_rt','feasibility_estimate_over_rt','summation_estimate_over_rt'))
    attempts = []
    for a,b in ((phases[1],phases[2]),(pp,trial),(pp,phases[1])):
        try:
            attempts.append(coexistence(spec,problem,(gp,err),[seed(a),seed(b)]))
        except (RuntimeError,ValueError) as exc:
            attempts.append(dict(error=str(exc)))
    return attempts

def off(point):
    point=copy.deepcopy(point)
    mapping=point['parameters']
    form=next(f for f in mapping['model_families'] if f['kind']=='electrolyte')
    form.update(choice='fully-dissociated-debye-huckel')
    next(f for f in mapping['model_families'] if f['kind']=='permittivity').pop('ionic_region_relative_permittivity',None)
    for k in ('c_shell','c_dielectric','ionic_region_relative_permittivity'):
        form.pop(k,None)
    mapping['model_coefficients']=[q for q in mapping['model_coefficients'] if q['family']!='ionic_region_relative_permittivity']
    for c in mapping['components']:
        c['coefficients']=[q for q in c['coefficients'] if q['family'] not in ('born_diameter','solvation_factor')]
    return point

def slope_move(point, slope, anchor=None):
    point=copy.deepcopy(point)
    mapping = point['parameters']
    pair = next(p for p in mapping['pairs'] if {p['component_id_a'],p['component_id_b']}=={'water','protonated-aminomethylpropanol'})
    cs = {q['family']:q['value'] for q in pair['coefficients']}
    tref=next(q['reference_temperature']['magnitude'] for q in pair['coefficients'] if q['family']=='k_ij_reciprocal_temperature_slope')
    if anchor is not None:
        cs['k_ij']['magnitude']+=(cs['k_ij_reciprocal_temperature_slope']['magnitude']-slope)*(1/anchor-1/tref)
    cs['k_ij_reciprocal_temperature_slope']['magnitude']=slope
    return point

if __name__=='__main__':
    a, route, free, fixed = amp_inputs()
    T,P,feed=(a[k] for k in ('T_K','P_Pa','feed_mol'))
    cases = {'free': free, 'fixed': fixed, 'born-off': off(free),
             'slope-anchored': lambda:slope_move(free,-150.,353.22), 'k-at-353':lambda:slope_move(free,0.,353.22)}
    for name in sys.argv[1:] or list(cases):
        try:
            q = cases[name]
            spec = route.bind(q() if callable(q) else q)
            problem,res,report=parent(spec,T,P,feed,a['phases'][0])
            attempts=try_attempts(spec,problem,res,report,a['phases'],a['trial'])
            dump(name+'-attempts.json',attempts)
            out=summary(spec,T,P,describe(res),a['phases'],a['trial'],np.array(report.standard_over_rt),attempts,report)
            out['parent_notes']=res.message
            out['standard_diff_from_428']=list(np.asarray(report.standard_over_rt)-a['standard_over_rt'])
            dump(name+'.json',out)
        except (ValueError,RuntimeError,KeyError) as exc:
            print(name,type(exc).__name__,str(exc),flush=True)
