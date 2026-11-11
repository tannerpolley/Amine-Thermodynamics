"""#242 stage 3: AMP document, Hartono 2013 binary pre-fit, fixed-density record and Hsieh dielectric fit (design §§2, 4)."""
import copy, csv, hashlib, json, math, os, sys, time
from pathlib import Path
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from pinned_engine import SHA256

AN, t0 = Path(__file__).resolve().parent, time.perf_counter()
AMP, H, C, W = 'aminomethylpropanol', 'protonated-aminomethylpropanol', 'carbamate-anion', 'water'
MEA = AN.parent / 'mea_parameter_bundle/results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'
assert hashlib.sha256(MEA.read_bytes()).hexdigest() == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
log = dict(wheel_sha256=SHA256, python=sys.version)
def save(name, doc):
    text = json.dumps(doc, indent=1, default=float) + '\n'
    (AN / name).write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()
def stop(disposition):
    log.update(disposition=disposition, wall_seconds=time.perf_counter() - t0)
    save('results/binary-dielectric.json', log)
    sys.exit(0 if disposition == 'accepted' else disposition)
def controls(seconds):
    return reg.FitControls(maximum_iterations=60, function_tolerance=1e-10, parameter_tolerance=1e-10, gradient_tolerance=1e-8,
                           maximum_elapsed_time_seconds=seconds, workers=os.cpu_count())

# AMP document: adopted MEA record with the MEA species renamed; frozen neutral AMP; cation A sphere; AMP pairs zero
# except the analog carbamate-water value (design §§2, 6).
doc = json.loads(MEA.read_text().replace('monoethanolamine', 'aminomethylpropanol'))
doc.update(document_id='amp-transfer-242', purpose='#242 AMP transfer assessment: MEA shared species fixed; AMP species per design 842bc73 §§2-4')
pure = json.loads((AN / 'inputs/amp-pure-endpoint.json').read_text())
doc['components'] = [pure['components'][0] if c['component_id'] == AMP else c for c in doc['components']]
doc['topology']['edges'] = [pure['topology']['edges'][0] if {e['endpoint_a']['component_id'], e['endpoint_b']['component_id']} == {AMP} else e
                            for e in doc['topology']['edges']]
amp_eps = next(i['value']['magnitude'] for i in pure['components'][0]['coefficients'] if i['family'] == 'dispersion_energy_over_k')
ions = {H: dict(segment_diameter=5.3, packing_diameter=0.88 * 5.3, debye_huckel_diameter=5.3, dispersion_energy_over_k=amp_eps),
        C: dict(segment_diameter=5.3, packing_diameter=0.88 * 5.3, debye_huckel_diameter=5.3)}
for c in doc['components']:
    for item in c['coefficients']:
        item['value']['magnitude'] = ions.get(c['component_id'], {}).get(item['family'], item['value']['magnitude'])
    c['fixed']['molar_mass']['value']['magnitude'] = {H: 0.09015, C: 0.13214}.get(c['component_id'], c['fixed']['molar_mass']['value']['magnitude'])
for p in doc['pairs']:
    # AMP-water keeps the MEA-water analog only as the binary start: zero k is locally unstable (L-L split) at all 26 rows.
    if {p['component_id_a'], p['component_id_b']} & {AMP, H, C} and {p['component_id_a'], p['component_id_b']} not in ({C, W}, {AMP, W}):
        for item in p['coefficients']:
            item['value']['magnitude'] = 0.0
par = epcsaft.Parameters.from_mapping(doc)

# Binary pre-fit: Hartono 2013 Table 3, 26 P (log, scale 0.05) + 26 y_AMP (scale max(1e-4, 0.05 y)), group mean.
binary = list(csv.DictReader((AN / 'inputs/hartono-2013-table-3.csv').open()))
def bubble(par, r, kind):
    x, y, T = float(r['x_AMP']), float(r['y_AMP']), float(r['t_C']) + 273.15
    problem = eq.problem_from_mapping(dict(T=T, P=dict(free=True, guess=1e3 * float(r['P_kPa'])), feed=dict(basis='amounts', values={AMP: x, W: 1 - x}),
        phases=[dict(name='L', kind='liquid', support=[AMP, W], composition_guess={AMP: x, W: 1 - x}),
                dict(name='V', kind='vapor', support=[AMP, W], amount=dict(status='pinned', value=0.0), composition_guess={AMP: y, W: 1 - y})], row_tolerance=1e-10))
    if kind == 'P':
        return reg.observation(par, 'pressure', problem, observed=1e3 * float(r['P_kPa']), form='log_ratio')
    return reg.observation(par, 'mole_fraction', problem, phase='V', species=[AMP], observed=y, form='difference', scale=max(1e-4, 0.05 * y))
obs = [bubble(par, r, k) for k in 'Py' for r in binary]
weights = [2 / 52 / 0.05 ** 2] * 26 + [2 / 52] * 26
coords = [reg.coordinate(par, [(f, (AMP, W), 1.0)], origin=0.0, scale=s, bounds=b) for f, s, b in
          (('k_ij', 0.05, (-0.5, 0.5)), ('k_ij_reciprocal_temperature_slope', 100.0, (-1000.0, 1000.0)))]
def predictions(par, items):
    model = epcsaft.Mixture(par)
    return [dict(status=p.status.name, value=p.value, residual=p.residual, tolerance=p.requested_tolerance_met) for p in (reg.predict(model, o) for o in items)]
start = predictions(par, obs)
log['binary_start_unavailable'] = [i for i, p in enumerate(start) if p['status'] != 'Available' or p['tolerance'] is False]
if log['binary_start_unavailable']:
    stop('binary start not phase-admissible')
result = reg.fit(par, coords, obs, weights=weights, controls=controls(1200), singular_vectors=True)
fitted = reg.fitted_parameters(par, result)
end = predictions(fitted, obs)
k, s = (0.05 * result.optimizer[0], 100 * result.optimizer[1])
log['binary'] = dict(status=result.status, usable=result.usable, message=result.message, iterations=result.iterations, initial_cost=result.initial_cost,
                     cost=result.final_cost, k_ref=k, slope_K=s, active_bounds=list(result.covariance.active_bounds), singular_values=list(result.covariance.singular_values),
                     rows=[dict(r, kind=kind, predicted=p['value'], status=p['status']) for kind, rs in (('P', binary), ('y', binary)) for r in rs for p in [end.pop(0)]])
if result.status != 'converged' or not result.usable or result.covariance.active_bounds or any(r['status'] != 'Available' for r in log['binary']['rows']):
    stop('binary pre-fit not admissible')
for p in doc['pairs']:
    if {p['component_id_a'], p['component_id_b']} == {AMP, W}:
        for item in p['coefficients']:
            item['value']['magnitude'] = k if item['family'] == 'k_ij' else s
log['density_record'] = dict(path='inputs/amp-density-record.json', sha256=save('inputs/amp-density-record.json', doc))

# Fixed EOS densities at the 30 Hsieh states (101325 Pa, stable liquid), then the Engine fit of AMP's two dielectric coefficients.
par = epcsaft.Parameters.from_mapping(json.loads((AN / 'inputs/amp-density-record.json').read_text()))
model, hsieh = epcsaft.Mixture(par), list(csv.DictReader((AN / 'inputs/hsieh-2007.csv').open()))
for r in hsieh:
    x, T = float(r['x_AMP']), float(r['T_K'])
    state = model.state(T, P=101325.0, x={AMP: x, W: 1 - x}, phase='liquid')
    r.update(rho_mol_L=state.molar_density / 1e3, rho_kg_m3=state.molar_density * (x * 0.08914 + (1 - x) * 0.01801528), P_Pa=state.pressure, dP_drho=state.pressure_density_derivative)
    if not state.pressure_density_derivative > 0:
        stop('ambiguous or unstable Hsieh liquid density')
A, Cw, T = 0.3777, 1403.0, 313.15  # adopted water coefficients (L/mol, K); MEA quadratic reduction on the 313.15 K isotherm
iso = [r for r in hsieh if float(r['T_K']) == T]
x, rho, e = (np.array([float(r[k]) for r in iso]) for k in ('x_AMP', 'rho_mol_L', 'epsilon'))
K = Cw / T - 1
q = np.linalg.lstsq(np.column_stack((rho * x, rho * x * x)) / (0.01 * e)[:, None], (e - 1 - rho * A * K) / (0.01 * e), rcond=None)[0]
disc = q[0] ** 2 - 4 * K * A * q[1]
log['reduction_313K'] = dict(q=q.tolist(), discriminant=disc)
if disc <= 0:
    stop('no distinct real dielectric roots at 313.15 K')
starts = [(A + u, Cw + T * (q[0] - K * u) / A) for u in (q[0] + np.array([-1, 1]) * math.sqrt(disc)) / (2 * K)]
def permittivity(par, r):
    x = float(r['x_AMP'])
    return reg.electrolyte(par, 'bulk_relative_permittivity', float(r['T_K']), 101325.0, {AMP: x, W: 1 - x}, ions=('hydronium-cation', 'hydroxide-anion'),
                           stoichiometry=(1, 1), molality=0.0, observed=float(r['epsilon']), form='difference', scale=0.01 * float(r['epsilon']))
def with_dielectric(volume, temperature):
    d = json.loads((AN / 'inputs/amp-density-record.json').read_text())
    for item in next(c for c in d['components'] if c['component_id'] == AMP)['coefficients']:
        item['value']['magnitude'] = dict(dielectric_volume=volume, dielectric_temperature=temperature).get(item['family'], item['value']['magnitude'])
    return d
branches = []
for label, (volume, temperature) in zip(('smaller-dV', 'larger-dV'), starts):
    par = epcsaft.Parameters.from_mapping(with_dielectric(volume, temperature))
    coords = [reg.coordinate(par, [('dielectric_volume', AMP, 1e-3)], origin=volume, scale=0.1), reg.coordinate(par, [('dielectric_temperature', AMP, 1.0)], origin=temperature, scale=100.0)]
    result = reg.fit(par, coords, [permittivity(par, r) for r in hsieh], controls=controls(600), singular_vectors=True)
    V, Td = volume + 0.1 * result.optimizer[0], temperature + 100 * result.optimizer[1]
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(with_dielectric(V, Td)))
    replay = [model.state(float(r['T_K']), rho=1e3 * r['rho_mol_L'], x={AMP: float(r['x_AMP']), W: 1 - float(r['x_AMP'])}).bulk_relative_permittivity for r in hsieh]
    branches.append(dict(label=label, start=[volume, temperature], dielectric_volume_L_mol=V, dielectric_temperature_K=Td, status=result.status, usable=result.usable,
                         message=result.message, cost=result.final_cost, singular_values=list(result.covariance.singular_values), predictions=list(result.predictions),
                         fixed_density_replay_max=max(abs(a - b) for a, b in zip(replay, result.predictions)),
                         admissible=result.status == 'converged' and result.usable and V > 0 and Td > 393.15 and all(math.isfinite(v) and v > 1 for v in replay)))
log.update(hsieh_rows=hsieh, dielectric_branches=branches)
ok = [b for b in branches if b['admissible'] and b['fixed_density_replay_max'] <= 1e-8]
distinct = len(ok) == 2 and abs(ok[0]['dielectric_volume_L_mol'] - ok[1]['dielectric_volume_L_mol']) > 1e-6 * abs(ok[0]['dielectric_volume_L_mol'])
if not ok or (distinct and abs(ok[0]['cost'] - ok[1]['cost']) <= 1e-10 * max(b['cost'] for b in ok)):
    stop('no admissible dielectric branch' if not ok else 'two admissible branches with indistinguishable cost: owner choice')
best = min(ok, key=lambda b: b['cost'])
log['amp_document'] = dict(path='inputs/amp-document.json', branch=best['label'],
                           sha256=save('inputs/amp-document.json', with_dielectric(best['dielectric_volume_L_mol'], best['dielectric_temperature_K'])))
stop('accepted')
