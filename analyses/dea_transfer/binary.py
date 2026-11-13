"""#317 design steps 2-3 and D3: pure-DEA check, DEA-water k_ij, DEA dielectric coefficients, DEA ideal-gas Cp.

Run: agent-heavy env OMP_NUM_THREADS=1 uv run --no-sync python analyses/dea_transfer/binary.py
"""
import copy, csv, json, math, os, sys
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from pinned import AN, REF, MEA, DEA, H, C, W, M_DEA, M_W, verify_wheel, save

verify_wheel()
rows = lambda name: list(csv.DictReader((REF / name).open()))
log = dict(wheel='391dfe5d', mea_record=str(MEA.relative_to(AN.parents[1])))
def stop(disposition):
    log['disposition'] = disposition
    save('results/binary.json', log)
    sys.exit(0 if disposition == 'accepted' else disposition)
def controls(seconds):
    return reg.FitControls(maximum_iterations=60, function_tolerance=1e-10, parameter_tolerance=1e-10, gradient_tolerance=1e-8,
                           maximum_elapsed_time_seconds=seconds, workers=int(os.environ.get('AGENT_HEAVY_CORES', 1)))
def coefficient(component, family, value, locator):
    for item in component['coefficients']:
        if item['family'] == family:
            item['value']['magnitude'] = value
            item['provenance'] = dict(source_id='issue-317', locator=locator)

# Design step 2: Nasrifar & Tafazzol 2010 Table 2, 4C (two donor, two acceptor sites), sigma_ij^3 kappa as Eq. 34 and the Engine.
NASRIFAR = 'Nasrifar & Tafazzol 2010 Table 2 (Zotero CBRPAXQG), DEA 4C'
doc = json.loads(MEA.read_text().replace('monoethanolamine', DEA))
doc.update(document_id='dea-transfer-317', purpose='#317 DEA working fit: adopted MEA shared record frozen; DEA species per design comment 6836480110')
dea = next(c for c in doc['components'] if c['component_id'] == DEA)
dea['aliases'] = ['DEA']
for family, value in dict(segment_count=5.2048, segment_diameter=2.9477, dispersion_energy_over_k=269.00).items():
    coefficient(dea, family, value, NASRIFAR)
dea['fixed']['molar_mass']['value']['magnitude'] = M_DEA
for site in doc['topology']['sites']:
    if site['component_id'] == DEA:
        site['multiplicity'] = 2
own = next(e for e in doc['topology']['edges'] if e['endpoint_a']['component_id'] == e['endpoint_b']['component_id'] == DEA)
own['energy_over_k']['value']['magnitude'], own['volume']['value']['magnitude'] = 1517.6, 0.1014
own['source'] = dict(kind='explicit', provenance=[dict(source_id='issue-317', locator=NASRIFAR)])
pure = copy.deepcopy(doc)
pure.update(components=[dea], pairs=[], correlations=[], reaction_correlations=[],
            topology=dict(doc['topology'], edges=[own], no_cross_association=[], sites=[s for s in doc['topology']['sites'] if s['component_id'] == DEA]))
model = epcsaft.Pure(epcsaft.Parameters.from_mapping(pure))
def saturation(T):
    r = eq.solve_equilibrium(model, model.saturation(T))
    return r.pressure / 1e3 if r.requested_tolerance_met and r.pressure else math.nan
measured = [dict(source=s, T_K=float(r['T_K']), P_kPa=float(r['P_kPa'])) for s in ('Horstmann2002_Table1_pure_DEA.csv', 'Klepacova2011_Table4_pure_DEA.csv') for r in rows(s)]
for r in measured:
    r['model_kPa'] = saturation(r['T_K'])
    r['relative_percent'] = 100 * (r['model_kPa'] / r['P_kPa'] - 1)
antoine = lambda T: 10 ** (7.26044 - 2326.23 / (T - 98.907))  # Horstmann 2002 Table 2
between = [abs(r['P_kPa'] / antoine(r['T_K']) - 1) * 100 for r in measured if r['source'].startswith('Klep')]
log['pure'] = dict(rows=measured, model_MARE_percent=float(np.mean([abs(r['relative_percent']) for r in measured])),
                   between_laboratory_MARE_percent=float(np.mean(between)), sites='4C: site a donor x2, site b acceptor x2', accepted_by_engine=True)
log['pure']['rule_met'] = log['pure']['model_MARE_percent'] <= log['pure']['between_laboratory_MARE_percent']
save('results/binary.json', log)
if not log['pure']['rule_met']:
    stop('pure-DEA rule not met: stop and ask (design step 2)')

# Form-A reactive document (D2): single spheres sized by the DEA/MEA neutral segment-volume cube root; MEA ion energies and Born diameters.
mea = {c['component_id']: c for c in json.loads(MEA.read_text())['components']}
ratio = (5.2048 * 2.9477 ** 3 / (3.0353 * 3.0435 ** 3)) ** (1 / 3)
log['size_ratio'] = ratio
for c in doc['components']:
    if c['component_id'] in (H, C):
        s = ratio * next(i['value']['magnitude'] for i in mea[{H: 'protonated-monoethanolamine', C: C}[c['component_id']]]['coefficients'] if i['family'] == 'segment_diameter')
        for family, value in dict(segment_diameter=s, debye_huckel_diameter=s, packing_diameter=0.88 * s).items():
            coefficient(c, family, value, 'design D2: MEA ion diameter x (m sigma^3 DEA / MEA)^(1/3)')
        c['fixed']['molar_mass']['value']['magnitude'] = {H: 0.106145, C: 0.148139}[c['component_id']]
        c['aliases'] = [{H: 'DEAH+', C: 'DEACOO-'}[c['component_id']]]
for p in doc['pairs']:  # D2: new pairs zero except DEACOO--water (MEA value); DEA-water from the binary fit
    if {p['component_id_a'], p['component_id_b']} & {DEA, H, C} and {p['component_id_a'], p['component_id_b']} != {C, W}:
        for item in p['coefficients']:
            item['value']['magnitude'] = 0.0
epcsaft.Parameters.from_mapping(doc)

# Design step 3a: one temperature-independent DEA-water k_ij on Horstmann 2002 Table 4 (44 rows, 365.15 K, log-ratio pressure).
horstmann = rows('Horstmann2002_Table4_water_DEA_365K.csv')
def bubble(par, r):
    x = float(r['x_water'])
    support = [c for c, n in ((DEA, 1 - x), (W, x)) if n > 0]
    problem = eq.problem_from_mapping(dict(T=float(r['T_K']), P=dict(free=True, guess=1e3 * float(r['P_kPa'])), feed=dict(basis='amounts', values={c: n for c, n in ((DEA, 1 - x), (W, x)) if n > 0}),
        phases=[dict(name='L', kind='liquid', support=support), dict(name='V', kind='vapor', support=support, amount=dict(status='pinned', value=0.0))], row_tolerance=1e-10))
    return reg.observation(par, 'pressure', problem, observed=1e3 * float(r['P_kPa']), form='log_ratio')
# Start at Nasrifar Table 3 (-0.04, same Horstmann data): k_ij = 0 is locally unstable (L-L split) at Table 4 row 22, as for AMP.
for p in doc['pairs']:
    if {p['component_id_a'], p['component_id_b']} == {DEA, W}:
        next(i for i in p['coefficients'] if i['family'] == 'k_ij')['value']['magnitude'] = -0.04
par = epcsaft.Parameters.from_mapping(doc)
obs = [bubble(par, r) for r in horstmann]
coords = [reg.coordinate(par, [('k_ij', (DEA, W), 1.0)], origin=-0.04, scale=0.05, bounds=(-1.0, 1.0))]
result = reg.fit(par, coords, obs, weights=[1 / len(obs)] * len(obs), controls=controls(1200), singular_vectors=True)
k = -0.04 + 0.05 * result.optimizer[0] if result.optimizer else math.nan
fitted = epcsaft.Mixture(reg.fitted_parameters(par, result))
end = [reg.predict(fitted, o) for o in obs]
log['binary'] = dict(status=result.status, usable=result.usable, message=result.message, cost=result.final_cost, k_ij=k, nasrifar_k_ij=-0.04,
                     active_bounds=list(result.covariance.active_bounds), singular_values=list(result.covariance.singular_values),
                     rows=[dict(r, predicted_kPa=p.value / 1e3 if p.status.name == 'Available' else None, status=p.status.name) for r, p in zip(horstmann, end)])
ok = [r for r in log['binary']['rows'] if r['status'] == 'Available']
log['binary']['MARE_percent'] = float(np.mean([abs(r['predicted_kPa'] / float(r['P_kPa']) - 1) * 100 for r in ok]))
if result.status != 'converged' or not result.usable or result.covariance.active_bounds or len(ok) != len(obs):
    stop('binary fit not admissible: stop and ask')
for p in doc['pairs']:
    if {p['component_id_a'], p['component_id_b']} == {DEA, W}:
        for item in p['coefficients']:
            item['value']['magnitude'] = k if item['family'] == 'k_ij' else 0.0

# Design step 3b: two DEA dielectric coefficients on Hsieh 2007 at fixed EOS densities, method of analyses/amp_transfer/binary.py.
par = epcsaft.Parameters.from_mapping(doc)
model, hsieh = epcsaft.Mixture(par), rows('Hsieh2007_DEA_permittivity.csv')
for r in hsieh:
    x, T = float(r['x_DEA']), float(r['T_K'])
    state = model.state(T, P=101325.0, x={DEA: x, W: 1 - x}, phase='liquid')
    r.update(rho_mol_L=state.molar_density / 1e3, dP_drho=state.pressure_density_derivative)
    if not state.pressure_density_derivative > 0:
        stop('ambiguous or unstable Hsieh liquid density')
A, Cw, T = 0.3777, 1403.0, 313.15  # adopted water dielectric coefficients; quadratic reduction on the 313.15 K isotherm gives two starts
iso = [r for r in hsieh if float(r['T_K']) == T]
x, rho, e = (np.array([float(r[k]) for r in iso]) for k in ('x_DEA', 'rho_mol_L', 'epsilon'))
K = Cw / T - 1
q = np.linalg.lstsq(np.column_stack((rho * x, rho * x * x)) / (0.01 * e)[:, None], (e - 1 - rho * A * K) / (0.01 * e), rcond=None)[0]
disc = q[0] ** 2 - 4 * K * A * q[1]
if disc <= 0:
    stop('no distinct real dielectric roots at 313.15 K')
starts = [(A + u, Cw + T * (q[0] - K * u) / A) for u in (q[0] + np.array([-1, 1]) * math.sqrt(disc)) / (2 * K)]
def with_dielectric(volume, temperature):
    d = copy.deepcopy(doc)
    c = next(c for c in d['components'] if c['component_id'] == DEA)
    coefficient(c, 'dielectric_volume', volume, 'issue 317 Hsieh 2007 dielectric fit')
    coefficient(c, 'dielectric_temperature', temperature, 'issue 317 Hsieh 2007 dielectric fit')
    return d
branches = []
for volume, temperature in starts:
    par = epcsaft.Parameters.from_mapping(with_dielectric(volume, temperature))
    obs = [reg.electrolyte(par, 'bulk_relative_permittivity', float(r['T_K']), 101325.0, {DEA: float(r['x_DEA']), W: 1 - float(r['x_DEA'])}, ions=('hydronium-cation', 'hydroxide-anion'),
                           stoichiometry=(1, 1), molality=0.0, observed=float(r['epsilon']), form='difference', scale=0.01 * float(r['epsilon'])) for r in hsieh]
    coords = [reg.coordinate(par, [('dielectric_volume', DEA, 1e-3)], origin=volume, scale=0.1), reg.coordinate(par, [('dielectric_temperature', DEA, 1.0)], origin=temperature, scale=100.0)]
    result = reg.fit(par, coords, obs, controls=controls(600), singular_vectors=True)
    V, Td = volume + 0.1 * result.optimizer[0], temperature + 100 * result.optimizer[1]
    branches.append(dict(start=[volume, temperature], dielectric_volume_L_mol=V, dielectric_temperature_K=Td, status=result.status, usable=result.usable, cost=result.final_cost,
                         predictions=list(result.predictions), admissible=result.status == 'converged' and result.usable and V > 0 and Td > 393.15))
log.update(hsieh_rows=hsieh, dielectric_branches=branches)
ok = [b for b in branches if b['admissible']]
if not ok:
    stop('no admissible dielectric branch: stop and ask')
best = min(ok, key=lambda b: b['cost'])
log['dielectric'] = dict(best, MARE_percent=float(np.mean([abs(p / float(r['epsilon']) - 1) * 100 for p, r in zip(best['predictions'], hsieh)])))
doc = with_dielectric(best['dielectric_volume_L_mol'], best['dielectric_temperature_K'])
log['document_sha256'] = save('inputs/dea-A.json', doc)

# D3: DEA ideal-gas Cp = Maham 1997 liquid Cp - pinned-Engine residual Cp of the pure-DEA record at 1 bar; line in (T - 313.15 K).
maham = rows('Maham1997_Table1_DEA_cp.csv')
Tm = np.array([float(r['T_K']) for r in maham])
residual = np.array([model.state(T, P=1e5, x={DEA: 1.0}, phase='liquid').residual_isobaric_heat_capacity for T in Tm])
ideal = np.array([float(r['cp_J_per_mol_K']) for r in maham]) - residual
slope, intercept = np.polyfit(Tm - 313.15, ideal, 1)
caloric = json.loads((AN.parent / 'solvent_specification_mea/inputs/caloric.json').read_text())
caloric['components'] = {k: caloric['components'][k] for k in ('carbon-dioxide', W)}
caloric['components'][DEA] = dict(representation='cp_polynomial', coefficients=[float(intercept), float(slope)], range_k=[293.0, 423.0],
    basis='ideal gas; Cp = sum(a_k*(T - T_ref)^k), T_ref = 313.15 K; Cp in J/(mol K); coefficients in ascending k',
    source='Maham et al. 1997 Table 1 liquid Cp minus pinned-Engine (391dfe5d) residual Cp of the Nasrifar 2010 pure-DEA record at 1 bar; straight line (#317 D3)',
    enthalpy_entropy_anchor_k=313.15, anchor_basis='h=s=0 at 313.15 K, MEA amine convention', enthalpy_anchor_j_per_mol=0.0, entropy_anchor_j_per_mol_k=0.0)
log['caloric'] = dict(T_K=Tm.tolist(), residual_cp=residual.tolist(), ideal_cp=ideal.tolist(), line=[float(intercept), float(slope)],
                      line_residuals=(ideal - (intercept + slope * (Tm - 313.15))).tolist(), sha256=save('inputs/caloric.json', caloric))
stop('accepted')
