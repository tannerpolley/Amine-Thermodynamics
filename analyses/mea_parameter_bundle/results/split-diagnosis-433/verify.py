import math
import os
from pathlib import Path
import part_ii
from part_ii import ROOT, Route, stable, np, epcsaft, jsonable, eq
from reference_states_428 import balances

part_ii.WHEEL = Path(os.environ["EPCA_WHEEL_433"])

RUN = ROOT/'analyses/mea_parameter_bundle/results/split-diagnosis-433'
AMP = ROOT/'analyses/amp_transfer'
AMP_RECORD = ROOT/'analyses/mea_parameter_bundle/results/reference-states-428/amp.json'
R = epcsaft.GAS_CONSTANT_J_PER_MOL_K

def dump(name, data):
    (RUN/name).write_text(__import__('json').dumps(jsonable(data), indent=2, allow_nan=False)+'\n')

def amp_inputs():
    a = stable.read(AMP_RECORD)
    from reference_states_428 import identity
    assert identity(*(ROOT/p for p in a['inputs'])) == a['inputs']
    route = Route(AMP/'inputs/retransfer-344/phase-2/AMP-05e94210.json', RUN/'amp')
    params = AMP/'results/retransfer-412-f2-05e94210'
    return a, route, stable.read(params/'main/parameters.json'), stable.read(params/'slope-150/parameters.json')

def g(state, T, P, x, standard):
    x = np.asarray(x)
    ideal = np.dot(x[x>0],np.log(x[x>0]*state.molar_density)-1+np.asarray(standard)[x>0])
    return math.fsum((ideal,state.residual_helmholtz,P/(state.molar_density*R*T)))

def thermo(model,T,P,p,standard):
    x = np.asarray(p['x'])
    st = model.state(T,rho=p['density_mol_m3'],x=x)
    mu = np.log(x*st.molar_density)+st.residual_chemical_potential_over_rt+standard
    return st,g(st,T,P,x,standard),mu

def verify(model, T, P, phases, standard, formulas, reactions, feed):
    states, energies, potentials = zip(*(thermo(model,T,P,p,standard) for p in phases))
    ids = list(model.component_ids)
    z = np.array([f['charge'] for f in formulas])
    pivot = next(i for i,name in enumerate(ids) if name.startswith('protonated-'))
    directions = np.eye(len(z))-z[:,None]*np.eye(len(z))[pivot]/z[pivot]
    mask = np.arange(len(z))!=pivot
    directions = directions[mask]
    nu = np.array(reactions)
    assert np.all(directions@z==0) and np.linalg.matrix_rank(directions)==len(ids)-1
    phase_log = []
    for p,st,gi,mu in zip(phases,states,energies,potentials):
        x = np.asarray(p['x'])
        V = 1/st.molar_density
        def ar(n,v):
            nsum = n.sum()
            return nsum*model.state(T,rho=nsum/v,x=n/nsum).residual_helmholtz
        exact = directions@st.residual_chemical_potential_over_rt
        errors = {}
        for h in (1e-4,3e-5,1e-5,3e-6,1e-6):
            # Forward stencil keeps trace species positive. Ideal derivative is analytic.
            fd = np.array([sum(c*ar(x+j*h*d,V) for j,c in enumerate((-25,48,-36,16,-3)))/(12*h)
                           if np.all(x+4*h*d>0) else np.nan for d in directions])
            # The ideal contribution to -d(A/RT)/dV is 1/V on the unit-mol basis.
            pressure = R*T*(1-(ar(x,V*(1+h))-ar(x,V*(1-h)))/(2*h))/V
            errors[str(h)] = dict(direction_error=[float(v) if math.isfinite(v) else None for v in fd-exact], pressure_relative_error=(pressure-st.pressure)/P)
        phase_log.append(dict(g_over_rt=gi,euler_error=gi-x@mu, pressure_error_Pa=st.pressure-P,
                              pressure_density_derivative=st.pressure_density_derivative,
                              normalization=x.sum()-1,charge=x@z,reaction_affinities=nu@mu, finite_differences=errors))
    delta = math.fsum([s['amount_mol']*v*(1 if i else -1) for i,(s,v) in enumerate(zip(phases,energies))])
    return dict(phase_log=phase_log, delta=delta, ion_basis_pivot=ids[pivot],basis=[dict(zip(ids,row)) for row in directions],
                interphase= directions@(potentials[1]-potentials[2]),
                balance_parent=balances(np.asarray(feed),phases[:1],formulas),balance_split=balances(np.asarray(feed),phases[1:],formulas))

if __name__=='__main__':
    a, route, point, _ = amp_inputs()
    spec = route.bind(point)
    form = [spec.spec['element_formulas'][c] for c in spec.parameters.component_ids]
    out = verify(spec.model, a['T_K'], a['P_Pa'], a['phases'], np.array(a['standard_over_rt']),form,
                 [r['stoichiometry'] for r in a['declaration']['reactions']], a['feed_mol'])
    out['delta_from_retained'] = out['delta']-a['Gibbs_difference_over_RT_mol']
    dump('verification.json',out)
