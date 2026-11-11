"""Steele Table 7 energy-only calibration, with native Engine fitting/derivatives."""
import copy
import csv
import itertools
import json
import os

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from run import AN, SHA, verify_wheel, write_csv

TEMPLATE = json.loads((AN / 'inputs/razavi.json').read_text())
SITES = (('piperazine', 'a'), ('piperazine', 'b'))
DECL = dict(u=('dispersion_energy_over_k', 'piperazine', 274.1),
            eps_ab=('association_energy_over_k', SITES, 1923.25),
            kappa=('association_volume', SITES, .07275))
DATA = list(csv.DictReader((AN / 'inputs/steele-table7.csv').open()))


def document(values):
    doc = copy.deepcopy(TEMPLATE)
    doc['components'][0]['coefficients'][2]['value']['magnitude'] = values['u']
    edge = doc['topology']['edges'][0]
    edge['energy_over_k']['value']['magnitude'] = values['eps_ab']
    edge['volume']['value']['magnitude'] = values['kappa']
    return doc


def observations(par):
    return [reg.observation(par, 'pressure', epcsaft.Pure(par).saturation(float(r['T_K'])),
                            observed=1000*float(r['p_kPa']), form='difference', scale=1000*float(r['sigma_kPa'])) for r in DATA]


def information(par, coords, optimizer):
    e = reg.differentiate(par, coords, observations(par), optimizer=optimizer)
    J = np.array(e.residual_optimizer_gradient).reshape(8, len(coords))
    _, s, vt = np.linalg.svd(J, full_matrices=False)
    # SVD avoids squaring the condition number. Source-error covariance has no fitted variance factor.
    cov = (vt.T / s**2) @ vt
    sd = np.sqrt(np.diag(cov))
    return dict(singular_values=s.tolist(), right_vectors=vt.tolist(),
                numerical_rank=int(np.linalg.matrix_rank(J)), covariance_scaled=cov.tolist(),
                correlation=(cov / np.outer(sd, sd)).tolist(), se_fraction_of_Razavi=sd.tolist())


def fit(names, start=None):
    par = epcsaft.Parameters.from_mapping(document(start) if start else TEMPLATE)
    coords = [reg.coordinate(par, [(DECL[n][0], DECL[n][1], 1.)], origin=DECL[n][2], scale=DECL[n][2]) for n in names]
    controls = reg.FitControls(maximum_iterations=100, maximum_elapsed_time_seconds=600, function_tolerance=1e-10, parameter_tolerance=1e-10,
                               gradient_tolerance=1e-8, workers=int(os.environ['AGENT_HEAVY_CORES']))
    result = reg.fit(par, coords, observations(par), controls=controls, singular_vectors=True)
    values = {n: d[2] for n, d in DECL.items()}
    values.update({n: DECL[n][2]*(1+x) for n, x in zip(names, result.optimizer, strict=True)})
    info = information(par, coords, list(result.optimizer))
    scales = np.array([DECL[n][2] for n in names])
    cov = np.array(info['covariance_scaled']) * np.outer(scales, scales)
    record = dict(start=start, iteration_costs=list(result.iteration_costs), names=list(names), status=result.status, usable=result.usable, message=result.message,
                  iterations=result.iterations, values=values, sum_squared_source_residuals=2*result.final_cost,
                  start_information=information(par, coords, [(start[n]/DECL[n][2]-1) if start else 0. for n in names]), information=info,
                  covariance_physical=cov.tolist(), se_physical=np.sqrt(np.diag(cov)).tolist(),
                  residual_scaled_se=(np.sqrt(np.diag(cov))*np.sqrt(2*result.final_cost/(8-len(names)))).tolist())
    print(json.dumps(record), flush=True)
    return record


def solve(values, T, tolerance=None):
    model = epcsaft.Pure(epcsaft.Parameters.from_mapping(document(values)))
    problem = model.saturation(T)
    if tolerance is not None:
        problem.row_tolerance = tolerance
    result = eq.solve_equilibrium(model, problem)
    assert result.requested_tolerance_met and result.pressure is not None
    assert result.molar_densities[0] > result.molar_densities[1] > 0
    roots = [model.state(T, rho=rho) for rho in result.molar_densities]
    assert all(s.pressure_density_derivative > 0 for s in roots)
    return dict(T_K=T, p_kPa=result.pressure/1000, rho_kg_m3=result.molar_densities[0]*.08613,
                max_equilibrium_residual=max(map(abs, result.residuals)))


def calculate():
    verify_wheel()
    fits = [fit(names) for count in (1, 2, 3) for names in itertools.combinations(DECL, count)]
    # Diagnosed valley traversal: retain the 100-iteration stop, then the unchanged-tolerance continuation.
    final = fit(tuple(DECL), fits[-1]['values'])
    assert final['status'] == 'converged' and final['usable']
    assert all(v > 0 for v in final['values'].values())
    assert final['information']['numerical_rank'] == 3
    log = dict(wheel_sha256=SHA, fits=fits, selected=final)
    selected, baseline = final['values'], {n: d[2] for n, d in DECL.items()}
    rows = []
    for source in DATA:
        T, observed, sigma = (float(source[k]) for k in ('T_K', 'p_kPa', 'sigma_kPa'))
        r, old = solve(selected, T), solve(baseline, T)
        r.update(refinement_source_units=abs(solve(selected, T, 1e-12)['p_kPa']-r['p_kPa'])/sigma,
                 observed_kPa=observed, sigma_kPa=sigma, razavi_kPa=old['p_kPa'],
                 difference_kPa=r['p_kPa']-observed, relative_percent=100*(r['p_kPa']/observed-1),
                 residual_sigma=(r['p_kPa']-observed)/sigma,
                 outside_source_scale_kPa=abs(r['p_kPa']-observed)-sigma,
                 density_shift_percent=100*(r['rho_kg_m3']/old['rho_kg_m3']-1),
                 hartono_kPa=10**(5.9832-1215.77/(T-113.56)))
        rows.append(r)
    write_csv('refit-residuals.csv', rows)
    for filename, temperatures in [('refit-liquid-curve.csv', np.linspace(417.997,460.477,61)),
                                    ('refit-extrapolation.csv', sorted({283.,393.,384.6,*np.linspace(283.,393.,56)}))]:
        curve = []
        for T in temperatures:
            r, old = solve(selected, float(T)), solve(baseline, float(T))
            r.update(razavi_kPa=old['p_kPa'], razavi_rho_kg_m3=old['rho_kg_m3'],
                     pressure_shift_percent=100*(r['p_kPa']/old['p_kPa']-1),
                     density_shift_kg_m3=r['rho_kg_m3']-old['rho_kg_m3'],
                     density_shift_percent=100*(r['rho_kg_m3']/old['rho_kg_m3']-1))
            curve.append(r)
        write_csv(filename, curve)
    T = np.array([r['T_K'] for r in rows])
    old_errors = [100*(r['razavi_kPa']/r['observed_kPa']-1) for r in rows]
    log['summary'] = dict(AARD_percent=float(np.mean([abs(r['relative_percent']) for r in rows])),
                          residual_sigma=[r['residual_sigma'] for r in rows],
                          razavi_error_slope_percent_per_K=float(np.polyfit(T,old_errors,1)[0]),
                          refit_error_slope_percent_per_K=float(np.polyfit(T,[r['relative_percent'] for r in rows],1)[0]),
                          max_equilibrium_residual=max(r['max_equilibrium_residual'] for r in rows),
                          max_refinement_source_units=max(r['refinement_source_units'] for r in rows))
    (AN / 'results/refit-fits.json').write_text(json.dumps(log, indent=2)+'\n')
    # This is a calibration candidate, not an adopted parameter record.
    doc = document(selected)
    for cell in [doc['components'][0]['coefficients'][2], doc['topology']['edges'][0]['energy_over_k'], doc['topology']['edges'][0]['volume']]:
        cell['provenance'] = dict(source_id='steele-1997-energy-refit', locator='Table 7; results/refit-fits.json')
    (AN / 'results/refit-parameters.json').write_text(json.dumps(doc, indent=2)+'\n')


if __name__ == '__main__':
    calculate()
