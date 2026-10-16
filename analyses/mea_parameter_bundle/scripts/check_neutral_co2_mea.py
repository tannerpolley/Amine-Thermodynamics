import csv, sys, time
from pathlib import Path
import fit_campaign as campaign
import fit_observations as owner
root = Path('analyses/mea_parameter_bundle/results/joint-recalibration-170')
out, started, cpu = Path(sys.argv[1]), time.monotonic(), campaign.cpu_seconds()
rows = list(csv.DictReader(open('data/reference/MEA/physical_solubility/CO2_physical_from_N2O.csv')))[:7]
inputs = [dict(id=r['record_id'], T=float(r['temperature_K']), observed=1e-5*float(r['H_CO2_primary_mole_fraction_Pa']), weight=float(r['neutral_log_ratio_weight'])) for r in rows]
campaign.write(out/'inputs.json', inputs)
def problem(T, epsilon):
    x = 0.3/0.06108/(0.3/0.06108+0.7/0.01801528)
    support = ['carbon-dioxide', 'monoethanolamine', 'water'] if epsilon else ['monoethanolamine', 'water']
    return owner.eq.Problem(T=T, P=owner.eq.Free(10000.), feed=owner.eq.Amounts({'carbon-dioxide':epsilon, 'monoethanolamine':(1-epsilon)*x, 'water':(1-epsilon)*(1-x)}), phases=[owner.eq.Phase('L',kind='liquid',support=support), owner.eq.Phase('V',kind='vapor',support=support,amount=owner.eq.Pinned(0.))], reactions=(), row_tolerance=1e-10)
base = campaign.load(root/'stage2/co2-water/slope/co2-water/B/parameters.json')
for branch in ('larger-dV','smaller-dV'):
    branch_mapping = campaign.load(root/f'amendment-2/route2b/{branch}/start-parameters.json')
    mapping = owner.s.with_parameter_values(branch_mapping,{k:v for k,v in owner.s.parameter_values(base).items() if k in owner.s.parameter_values(branch_mapping)})
    params = owner.epcsaft.Parameters.from_mapping(mapping)
    coords = [owner.reg.coordinate(params,[(family,('carbon-dioxide','monoethanolamine'),1.)],origin=0.,scale=scale,bounds=bounds) for family,scale,bounds in [('k_ij',0.01,(-0.5,0.5)),('k_ij_reciprocal_temperature_slope',10.,(-500.,500.))]]
    observations = [owner.reg.observation(params,'partial_pressure',problem(r['T'],1e-5),observed=r['observed'],form='log_ratio',phase='V',species=['carbon-dioxide']) for r in inputs]
    for label, point in [('A',[0.,0.]),('B',[10.,10.])]:
        evaluations = {name:owner.reg.differentiate(params,coords,observations,optimizer=q) for name,q in [('native',point)]+[(f'{j}/{h}/{sign}',[p+(sign*h if i==j else 0.) for i,p in enumerate(point)]) for j in range(2) for h in (0.01,0.005) for sign in (-1,1)]}
        campaign.write(out/f'{branch}-{label}-derivatives.json',{name:{k:owner.s._jsonable(getattr(v,k)) for k in ('predictions','statuses','residual_optimizer_gradient')} for name,v in evaluations.items()})
        native = owner.epcsaft.Mixture(owner.epcsaft.Parameters.from_mapping(owner.s.with_parameter_values(mapping,{'pair/carbon-dioxide/monoethanolamine/k_ij':point[0]*.01,'pair/carbon-dioxide/monoethanolamine/k_ij/reciprocal_temperature_slope':point[1]*10.})))
        for T in (298.35,360.25):
            for epsilon in (0.,1e-5,1e-6,1e-7):
                declaration = problem(T,epsilon); state = owner.eq.solve_equilibrium(native,declaration)
                mechanical = [native.state(T,rho=rho,x=list(state.mole_fractions[i*len(native.component_ids):(i+1)*len(native.component_ids)])).pressure_density_derivative for i,rho in enumerate(state.molar_densities)]
                campaign.write(out/f'{branch}-{label}-{T}-{epsilon}.json',dict(T=T,epsilon=epsilon,success=state.success,requested_tolerance_met=state.requested_tolerance_met,dP_drho_Pa_m3_mol=mechanical,message=state.message,raw_residuals=list(owner.eq.compile_problem(native,declaration).evaluate(state.coordinates).values),pressure=list(state.pressure),phases=[owner.s._phase_payload(declaration,state,i,len(native.component_ids)) for i in range(state.phase_count)]))
campaign.write(out/'timing.json',dict(cpu_s=campaign.cpu_seconds()-cpu,wall_s=time.monotonic()-started))
