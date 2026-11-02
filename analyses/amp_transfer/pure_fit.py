"""#242 stage 2: pure-AMP pre-fit, m profile and gates (design §3), all fitting in the pinned Engine."""
import copy, csv, hashlib, json, math, os, sys, time, zipfile
from collections import Counter
from pathlib import Path
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg

AN, t0 = Path(__file__).resolve().parent, time.perf_counter()
OUT = AN / 'results/pure'
OUT.mkdir(parents=True, exist_ok=True)
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')
assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
with zipfile.ZipFile(WHEEL) as z:
    assert all(z.read(n) == (Path(epcsaft.__file__).parents[1] / n).read_bytes() for n in z.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
AMP, SITES = 'aminomethylpropanol', (('aminomethylpropanol', 'a'), ('aminomethylpropanol', 'b'))
DECL = dict(m=('segment_count', AMP, 3.1552, 0.5, (1.5, 5.0)), sigma=('segment_diameter', AMP, 3.4676, 0.25, (2.8, 4.2)),
            epsilon=('dispersion_energy_over_k', AMP, 237.94, 50.0, (150.0, 400.0)),
            eps_ab=('association_energy_over_k', SITES, 3526.15, 500.0, (1500.0, 5500.0)), kappa=('association_volume', SITES, 0.0058, 0.005, (0.0005, 0.05)))
AYAD = {k: v[2] for k, v in DECL.items()}
TEMPLATE = json.loads((AN / 'inputs/amp-pure-ayad.json').read_text())
rows = list(csv.DictReader((AN / 'inputs/pure-amp.csv').open()))
cal = [r for r in rows if r['role'] == 'calibration']
N = Counter(r['campaign'] for r in cal)
# Native cost 1/2 sum w r^2 equals the design objective, the sum over campaigns of mean squared scaled residuals.
weights = [2 / N[r['campaign']] / (float(r['scale']) ** 2 if r['kind'] == 'pressure' else 1) for r in cal]
log = dict(software=dict(wheel_sha256='83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6', python=sys.version, cpu_count=os.cpu_count(),
           input_sha256={p: hashlib.sha256((AN / p).read_bytes()).hexdigest() for p in ('inputs/pure-amp.csv', 'inputs/amp-pure-ayad.json')}), fits={})

def document(values):
    doc = copy.deepcopy(TEMPLATE)
    for item in doc['components'][0]['coefficients']:
        for name in ('m', 'sigma', 'epsilon'):
            if item['family'] == DECL[name][0]:
                item['value']['magnitude'] = values[name]
    edge = doc['topology']['edges'][0]
    edge['energy_over_k']['value']['magnitude'], edge['volume']['value']['magnitude'] = values['eps_ab'], values['kappa']
    return doc

def observation(par, r):
    T, value = float(r['T_K']), float(r['value'])
    if r['kind'] == 'density':
        return reg.density(par, T, 1e5, {AMP: 1.0}, phase='liquid', observed=value, form='difference', mass_basis=True, scale=float(r['scale']))
    return reg.observation(par, 'pressure', epcsaft.Pure(par).saturation(T), observed=value, form='log_ratio')

def jacobian(par, coords, v):  # weighted, coordinate-scaled residual Jacobian and its singular structure
    e = reg.differentiate(par, coords, [observation(par, r) for r in cal], optimizer=v)
    J = np.sqrt(weights)[:, None] * np.reshape(e.residual_optimizer_gradient, (len(cal), len(coords)))
    _, s, vt = np.linalg.svd(J)
    return dict(singular_values=s.tolist(), right_vectors=vt.tolist(), ratio=float(s[-1] / s[0]) if s[0] > 0 else 0.0)

def assess(doc):  # predictions, errors and phase admissibility of one parameter document
    par = epcsaft.Parameters.from_mapping(doc)
    model, out, bad = epcsaft.Pure(par), [], []
    for r in rows:
        p = reg.predict(model, observation(par, r))
        ok = (p.status.name == 'Available' and p.requested_tolerance_met is not False and math.isfinite(p.value) and p.value > 0
              and (r['kind'] == 'pressure' or p.branch.name == 'Liquid'))  # a pressure-closed density has no solve tolerance
        row = dict(campaign=r['campaign'], role=r['role'], kind=r['kind'], T_K=float(r['T_K']), observed=float(r['value']), predicted=p.value if ok else None, status=p.status.name)
        if ok and r['kind'] == 'pressure':  # distinct, mechanically stable liquid and vapor roots at the solved pressure
            roots = [model.state(row['T_K'], P=p.value, phase=ph) for ph in ('liquid', 'vapor')]
            row.update(relative_error_percent=100 * (p.value / row['observed'] - 1), liquid_vapor_density_mol_m3=[s.molar_density for s in roots],
                       dP_drho=[s.pressure_density_derivative for s in roots])
            ok = all(d > 0 for d in row['dP_drho']) and roots[0].molar_density > 10 * roots[1].molar_density
        elif ok:
            row['error_kg_m3'] = p.value - row['observed']
        out.append(row)
        if not ok:
            bad.append(row)
    stats = {c: dict(n=len(e), mean_abs_percent=float(np.mean(np.abs(e))), max_abs_percent=float(np.max(np.abs(e))))
             for c in dict.fromkeys(r['campaign'] for r in out if r['kind'] == 'pressure')
             for e in [[r['relative_error_percent'] for r in out if r['campaign'] == c and 'relative_error_percent' in r]] if e}
    density = [r['error_kg_m3'] for r in out if 'error_kg_m3' in r]
    accepted = not bad and len(stats) == 3 and all(s['mean_abs_percent'] <= 5 and s['max_abs_percent'] <= 10 for c, s in stats.items() if c != 'Pappa2006') \
        and len(density) == 3 and max(map(abs, density)) <= 1
    return dict(rows=out, unavailable=bad, campaigns=stats, density_errors=density, calibration_accepted=accepted)

def fit(label, values, names, seconds):
    par = epcsaft.Parameters.from_mapping(document(values))
    coords = [reg.coordinate(par, [(f, t, 1.0)], origin=o, scale=s, bounds=b) for n in names for f, t, o, s, b in [DECL[n]]]
    chart = reg.CoordinateSet()
    chart.coordinates = coords
    started = time.perf_counter()
    v0 = list(chart.start(par._native, [observation(par, r) for r in cal], None))  # start from the physical document
    record = dict(label=label, fitted=names, start=values, inferred_optimizer=v0, start_jacobian=jacobian(par, coords, v0), first_jacobian_seconds=time.perf_counter() - started)
    controls = reg.FitControls(maximum_iterations=60, function_tolerance=1e-10, parameter_tolerance=1e-10, gradient_tolerance=1e-8,
                               maximum_elapsed_time_seconds=seconds, workers=os.cpu_count())
    result = reg.fit(par, coords, [observation(par, r) for r in cal], weights=weights, controls=controls, singular_vectors=True)
    end = dict(values, **{n: DECL[n][2] + DECL[n][3] * x for n, x in zip(names, result.optimizer)})
    record.update(status=result.status, usable=result.usable, message=result.message, iterations=result.iterations, initial_cost=result.initial_cost,
                  cost=result.final_cost, endpoint=end, active_bounds=[names[i] for i in result.covariance.active_bounds], seconds=time.perf_counter() - started,
                  endpoint_jacobian=jacobian(par, coords, list(result.optimizer)), assessment=assess(document(end)))
    record['admissible'] = (result.status == 'converged' and result.usable and not record['active_bounds'] and not record['assessment']['unavailable']
                            and all(b[0] <= end[n] <= b[1] for n in names for b in [DECL[n][4]]))
    log['fits'][label] = record
    (OUT / 'summary.json').write_text(json.dumps(log, indent=1, default=float) + '\n')
    return record

def stop(disposition):
    log.update(disposition=disposition, wall_seconds=time.perf_counter() - t0)
    (OUT / 'summary.json').write_text(json.dumps(log, indent=1, default=float) + '\n')
    sys.exit(disposition)

FIVE = list(DECL)
starts = [fit('five-ayad', AYAD, FIVE, 2700), fit('five-second', dict(m=3.0, sigma=3.55, epsilon=250.0, eps_ab=3200.0, kappa=0.008), FIVE, 2700)]
admissible = [f for f in starts if f['admissible']]
if not admissible:
    stop('no admissible five-parameter endpoint')
anchor = min(admissible, key=lambda f: f['cost'])
log['anchor'] = anchor['label']
GRID = (1.5, 2.3276, 3.1552, 4.0776, 5.0)
profile = [fit(f'profile-m-{m}', dict(anchor['endpoint'], m=m), FIVE[1:], 1200) for m in GRID]
ref = {(r['kind'], r['T_K']): r['predicted'] for r in anchor['assessment']['rows'] if r['role'] == 'calibration'}
for p in profile:
    calib = [r for r in p['assessment']['rows'] if r['role'] == 'calibration' and r['predicted'] is not None]  # unavailable rows make the point inadmissible
    p['delta_cost'] = p['cost'] - anchor['cost']
    p['max_pressure_change_percent'] = max((100 * abs(r['predicted'] / ref[r['kind'], r['T_K']] - 1) for r in calib if r['kind'] == 'pressure'), default=math.inf)
    p['max_density_change_kg_m3'] = max((abs(r['predicted'] - ref[r['kind'], r['T_K']]) for r in calib if r['kind'] == 'density'), default=math.inf)
log['profile'] = [dict(m=m, **{k: p[k] for k in ('admissible', 'cost', 'delta_cost', 'max_pressure_change_percent', 'max_density_change_kg_m3', 'active_bounds')}) for m, p in zip(GRID, profile)]
if any(p['delta_cost'] < -1e-9 * anchor['cost'] for p in profile):
    stop('profile cost below the anchor: anchor not settled; return to Design')
flat = all(p['admissible'] and 0 <= p['delta_cost'] + 1e-9 * anchor['cost'] and p['delta_cost'] < 1 and p['max_pressure_change_percent'] <= 5
           and p['max_density_change_kg_m3'] <= 1 for p in profile)
log['profile_flat'] = flat
if flat:
    final = fit('fixed-m-3.1552', profile[2]['endpoint'], FIVE[1:], 1200)
    gate = final['endpoint_jacobian']['ratio']
else:
    costs = [p['cost'] for p in profile]
    j = int(np.argmin(costs))
    if not (all(p['admissible'] for p in profile) and 0 < j < 4 and costs[0] - costs[j] >= 1 and costs[4] - costs[j] >= 1):
        stop('profile not flat and m not identified (one-sided, incomplete or equivalent-cost endpoints); return to owner')
    final, gate = anchor, anchor['endpoint_jacobian']['ratio']
log['information_gate'] = dict(endpoint=final['label'], s_min_over_s_max=gate, limit=1e-4, passed=gate >= 1e-4)
if not final['admissible']:
    stop('selected endpoint not admissible')
if gate < 1e-4:
    stop('information gate failed: second unresolved direction; return to owner')
if not final['assessment']['calibration_accepted']:
    stop('calibration acceptance failed')
frozen = json.dumps(document(final['endpoint']), indent=1) + '\n'  # freeze, then cold replay from the written record
(AN / 'inputs/amp-pure-endpoint.json').write_text(frozen)
replay = assess(json.loads((AN / 'inputs/amp-pure-endpoint.json').read_text()))
worst = max(abs(a['predicted'] / b['predicted'] - 1) for a, b in zip(replay['rows'], final['assessment']['rows'], strict=True))
log.update(frozen_endpoint=dict(path='inputs/amp-pure-endpoint.json', sha256=hashlib.sha256(frozen.encode()).hexdigest(), values=final['endpoint']),
           replay_max_relative=worst, pappa=final['assessment']['campaigns'].get('Pappa2006'))
stop('accepted' if worst <= 1e-8 else 'replay mismatch')
