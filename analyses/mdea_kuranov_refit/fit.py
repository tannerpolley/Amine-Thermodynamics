"""Issue #126: constant ion-water k_ij fit, held-out pressures and endpoint permittivity sensitivity.

Run score.py first. Native Engine observations own log-pressure residuals and exact derivatives.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

import epcsaft
import numpy as np
from epcsaft import regression as reg

import diagnose
import model
import score

ERMATCHKOV = score.KURANOV.with_name('Ermatchkov_2006_CO2_MDEA_partial_pressure.csv')
PAIRS = ((model.W, model.MDEAH), (model.W, model.HCO3))
START = (-0.184, -0.0765)
BOUNDS = (-0.3, 0.3)


def constant_document(values):
    doc = model.charged_molecule_ions(model.document(), model.MDEAH)
    for pair, value in zip(PAIRS, values):
        diagnose.set_kij(doc, *pair, value)
    return doc


def write_json(name, value):
    (score.RESULTS / name).write_text(json.dumps(value, indent=1, allow_nan=False) + '\n')


def write_rows(name, rows, solved):
    table = []
    for row in rows:
        result = solved[row['row']]
        table.append(dict(row, **result, ln_ratio=math.log(result['p_calc'] / row['p_exp']) if result['success'] else None))
    with (score.RESULTS / name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, list(table[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(table)


def ermatchkov_rows():
    with ERMATCHKOV.open() as handle:
        return [dict(row=k, source_row=int(r['source_row']), source_table=r['source_table'],
                     series=r['temperature_K'] + ' K; ' + r['source_series'], T=float(r['temperature_K']),
                     m_mdea=float(r['m_MDEA_mol_per_kg_H2O']), m_co2=float(r['m_CO2_mol_per_kg_H2O']),
                     p_exp=1000 * float(r['p_CO2_kPa'])) for k, r in enumerate(csv.DictReader(handle), 1)]


def partial_pressures(doc, rows):
    # The bubble point solves total pressure; Ermatchkov measured y_CO2 * P, in Pa.
    solved = score.solve_rows(doc, rows)
    for result in solved.values():
        result['p_total_Pa'] = result['p_calc']
        result['p_calc'] *= result['y_vapor'][2] if result['success'] else 1
    return solved


def main():
    assert epcsaft.provenance()[1] == score.WHEEL_SHA256, 'wrong Engine wheel'
    gate = json.loads((score.RESULTS / 'reading-a-reproduction-summary.json').read_text())
    assert gate['gate_pass'] and gate['provenance']['engine_wheel_sha256'] == score.WHEEL_SHA256
    rows = score.kuranov_rows()
    doc = constant_document(START)
    params = epcsaft.Parameters.from_mapping(doc)
    solved = score.solve_rows(doc, rows)
    write_rows('constant-start-kuranov.csv', rows, solved)
    assert all(s['success'] for s in solved.values()), 'constant start has unsolved rows; retained in CSV'
    items = [reg.observation(params, 'pressure', model.bubble_problem(
        r['T'], r['m_mdea'], r['m_co2'], solved[r['row']]['p_calc'],
        dict(zip(model.SPECIES, solved[r['row']]['x_liquid'])),
        dict(zip(model.NEUTRAL, solved[r['row']]['y_vapor']))), observed=r['p_exp'], form='log_ratio') for r in rows]
    coords = [reg.coordinate(params, [('k_ij', pair, 1.0)], origin=start, scale=1.0, bounds=BOUNDS)
              for pair, start in zip(PAIRS, START)]
    chart = reg.CoordinateSet()
    chart.coordinates = coords
    evaluation = reg.differentiate(params, coords, items, optimizer=chart.start(params._native, items))
    jac = np.array(evaluation.residual_optimizer_gradient).reshape(len(rows), 2)
    assert all(str(s).endswith('Available') for s in evaluation.statuses), [str(s) for s in evaluation.statuses]
    norms = np.linalg.norm(jac, axis=0)
    assert np.all(norms > 0) and np.all(np.isfinite(jac)), 'undefined column normalization'
    singular = np.linalg.svd(jac / norms, compute_uv=False)
    active_count = 1 if singular[-1] < 0.1 else 2
    report = dict(start_values=START, bounds=BOUNDS, parameter_pairs=PAIRS,
                  start_column_norms=norms.tolist(), start_column_normalized_singular_values=singular.tolist(),
                  active_parameters=active_count, constant_start=score.summary(rows, solved))
    report['provenance'] = dict(engine_wheel_sha256=score.WHEEL_SHA256,
        engine_commit='8298c6029ebb8b467929badc4a223c580ec591ab', linear_solver=gate['provenance']['linear_solver'],
        input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (score.KURANOV, ERMATCHKOV)},
        scripts_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       (Path(__file__), model.HERE / 'model.py', model.HERE / 'score.py', model.HERE / 'diagnose.py')})
    write_json('refit-summary.json', report)
    np.savetxt(score.RESULTS / 'constant-start-jacobian.csv',
               np.column_stack(([r['row'] for r in rows], jac)), delimiter=',',
               header='kuranov_row,d_ln_pressure_d_k_water_MDEAH,d_ln_pressure_d_k_water_HCO3', comments='')
    print('Start information:', json.dumps(report), flush=True)
    controls = dict(maximum_iterations=100, maximum_elapsed_time_seconds=1800,
                    function_tolerance=1e-8, parameter_tolerance=1e-10, gradient_tolerance=1e-8, workers=8)
    result = reg.fit(params, coords[:active_count], items, controls=reg.FitControls(**controls), singular_vectors=True)
    report['fit'] = dict(status=result.status, message=result.message, usable=result.usable,
        acceptance=result.acceptance, controls=controls, physical=result.physical, optimizer=result.optimizer,
        initial_cost=result.initial_cost, final_cost=result.final_cost, iterations=result.iterations,
        residual_evaluations=result.residual_evaluations, jacobian_evaluations=result.jacobian_evaluations,
        trial_failures=result.trial_failures, iteration_seconds=result.iteration_seconds,
        iteration_costs=result.iteration_costs, statuses=[str(s) for s in result.statuses],
        predictions_Pa=result.predictions, residuals=result.residuals,
        failures=[dict(trial=f.trial, observation=f.observation, optimizer=f.optimizer,
                       status=str(f.status), message=f.message, jacobian=f.jacobian) for f in result.failures])
    write_json('refit-summary.json', report)
    print('Fit:', json.dumps(report['fit']), flush=True)
    if not result.usable:
        raise RuntimeError('Engine returned no usable fitted endpoint; see refit-summary.json')
    values = list(result.physical) + list(START[active_count:])
    endpoint = constant_document(values)
    write_json('fitted-parameters.json', endpoint)
    solved = score.solve_rows(endpoint, rows)
    write_rows('fitted-kuranov.csv', rows, solved)
    fit = report['fit']
    fit.update(values=values, bounds_status=['lower' if v == BOUNDS[0] else 'upper' if v == BOUNDS[1] else 'interior' for v in values],
               kuranov=score.summary(rows, solved))
    fit['pass_10_9_percent'] = fit['kuranov']['solved'] == 82 and fit['kuranov']['ARD_percent_solved_rows'] < 10.9
    write_json('refit-summary.json', report)
    print('Endpoint:', json.dumps(fit['kuranov']), flush=True)
    held = ermatchkov_rows()
    assert len(held) == 101
    report['ermatchkov'] = {}
    for name, d in (('start', doc), ('fitted', endpoint)):
        partial = partial_pressures(d, held)
        write_rows('ermatchkov-' + name + '.csv', held, partial)
        # The held-out set includes 8 mol/kg: its own isotherm/series groups avoid the Kuranov half labels.
        report['ermatchkov'][name] = score.summary(held, partial)
        del report['ermatchkov'][name]['ARD_percent_by_MDEA_molality']
        write_json('refit-summary.json', report)
        print('Ermatchkov ' + name + ':', json.dumps(report['ermatchkov'][name]), flush=True)
    # Hsieh 2007 Table 3, epsilon = a + b*T + c*T^2, rewritten exactly about T_REF.
    a, b, c = 44.1399, -0.046824, -8.82158e-5
    law = next(v for v in endpoint['correlations'] if v['component_id'] == model.MDEA)
    law['constant']['value']['magnitude'] = a + b * model.T_REF + c * model.T_REF**2
    law['terms'] = [dict(power=p, coefficient=dict(identity=f"{law['correlation_id']}/a{p}",
        value=model._value(v, unit))) for p, v, unit in ((1, b + 2*c*model.T_REF, '1 / kelvin'), (2, c, '1 / kelvin ** 2'))]
    law['provenance'] = 'Hsieh2007 Table 3, pure MDEA, 303.15-328.15 K; extrapolated above'
    sensitivity = score.solve_rows(endpoint, rows)
    write_rows('fitted-hsieh-quadratic-kuranov.csv', rows, sensitivity)
    report['permittivity_sensitivity'] = score.summary(rows, sensitivity)
    report['permittivity_sensitivity']['ARD_change_points'] = report['permittivity_sensitivity']['ARD_percent_solved_rows'] - fit['kuranov']['ARD_percent_solved_rows']
    write_json('refit-summary.json', report)
    print('Permittivity sensitivity:', json.dumps(report['permittivity_sensitivity']), flush=True)


if __name__ == '__main__':
    main()
