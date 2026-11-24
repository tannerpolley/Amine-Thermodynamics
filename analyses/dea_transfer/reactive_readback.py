"""Reduce #425 and #413 on paired DEA measurements."""
from collections import Counter, defaultdict
import math
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np

from binary_refit import HEAT, REFERENCE, VLE, SCALE, T_REF, evaluate, residuals, with_binary
from reactive_refit import BINARY, ROOT, ROUTE, read, sha
from f2_carbamate import dump
from MEA.solvent_specification import conditional_information, deviation_statistics
from stripper_temperature_409 import band

CONTROL = BINARY.parents[1]/'controls'


def statistics(rows):
    pairs = [(r['observed'], r['value']) for r in rows if r['status'] == 'Available']
    return dict(observed=len(rows), available=len(pairs),
                rmse=math.sqrt(math.fsum((p-o)**2 for o, p in pairs)/len(pairs)) if pairs else None,
                **(deviation_statistics(pairs, rows[0]['unit']) if pairs else {}))


def extent(values):
    values = list(values)
    return [min(values), max(values)] if values else None


def dataset_summary(rows):
    source = [r['row'] for r in rows]
    temperatures = extent(r['T_K'] for r in rows)
    composition = next((key for key in ('x_water', 'DEA_mass_percent', 'DEA_mass_fraction', 'DEA_kmol_per_m3')
                        if key in source[0]), None)
    amounts = extent(float(r[composition]) for r in source) if composition else None
    alpha = []
    for r in source:
        value = r.get('alpha_mol_CO2_per_mol_DEA', r.get('alpha_mol_CO2_per_mol_amine'))
        if value is not None:
            alpha.append(float(value))
        elif 'x_CO2' in r and 'DEA_mass_fraction' in r:
            w, x = float(r['DEA_mass_fraction']), float(r['x_CO2'])
            alpha.append(x/(1-x)*(1+(1-w)/0.01801528/(w/0.105137)))
    return dict(temperature_K=temperatures, unloaded_composition_basis=composition, unloaded_composition=amounts,
                loading_mol_CO2_per_mol_DEA=extent(alpha),
                R4=dict(Counter(str(r['outside_ranges']['carbamate-hydrolysis']) for r in rows)),
                R5=dict(Counter(str(r['outside_ranges']['DEA-dissociation']) for r in rows)))


def paired(old, new):
    aligned = {r['identity']: r for r in old}
    pair = [(aligned[r['identity']], r) for r in new]
    assert all((a['observed'], a['unit'], a['row']) == (b['observed'], b['unit'], b['row']) for a,b in pair)
    common = [(a,b) for a,b in pair if a['status'] == b['status'] == 'Available']
    return dict(reference=statistics([a for a,_ in pair]), candidate=statistics(new),
                paired_reference=statistics([a for a,_ in common]), paired_candidate=statistics([b for _,b in common]))


def objective(rows, weights):
    out = defaultdict(list)
    for r, w in zip(rows, weights, strict=True):
        assert (r['identity'], r['unit'], r['row']) == (w['identity'], w['unit'], w['source'])
        p, o = r['value'], r['observed']
        residual = math.log(p/o) if w['form'] == 'log_ratio' else (p-o)/w['scale']
        assert w['form'] in ('log_ratio', 'difference')
        out[r['group']].append(0.5*w['weight']*residual**2)
    return {k: math.fsum(v) for k,v in out.items()}


def binary_rows(source):
    return [dict(group=r['group'], role='fitted' if r['fitted'] else 'pure-component comparison', T_K=r['T'],
                 identity=f"{r['group']}:{r['source_row']}", observed=r['observed'], value=r.get('predicted'),
                 unit='J/mol mixture' if r['group'] == HEAT else 'kPa', row={k:r[k] for k in ('x_water','source_key','source_row')},
                 outside_ranges=dict.fromkeys(('carbamate-hydrolysis', 'DEA-dissociation'), 'reaction not used'),
                 status='Available' if r.get('predicted') is not None else 'Unavailable') for r in source]


def binary_uncertainty(binary, doc):
    inputs = [r for r in binary['rows'] if r['fitted']]
    point = np.array([binary['a'], binary['b']])
    def evaluate_at(coords):
        return residuals(evaluate(with_binary(doc, *coords), inputs))
    r = evaluate_at(point)
    assert math.isclose(.5*float(r@r), binary['replay_cost'], rel_tol=1e-8)
    estimates = {}
    for h in (1e-4, 5e-5):  # #425 binary readback steps, scaled chart
        differences = [(evaluate_at(point+d)-evaluate_at(point-d))/(2*h) for d in np.diag(SCALE*h)]
        jacobian = np.column_stack(differences)/SCALE
        estimates[str(h)] = conditional_information(SimpleNamespace(physical=point, covariance=SimpleNamespace(active_bounds=[])),
                                                    jacobian, r, ['a', 'b_K'], [-np.inf]*2, [np.inf]*2)
    return estimates


def covariance(information):
    errors = [information['conditional_standard_error'][key] for key in information['free_coordinates']]
    return (np.array(information['conditional_correlation'])*np.outer(errors, errors)).tolist()


def report(run, out):
    old = read(CONTROL/'reactive-data-rows.json')
    new = read(run/'data-rows.json')
    selection = read(run/'selection.json')
    chosen = selection['chosen']
    reference = read(REFERENCE/'selection.json')['chosen']
    weights = read(CONTROL/'reactive-objective.json')['weights']
    by_identity = {r['identity']: r for r in new}
    costs = {name: objective(rows, weights) for name, rows in
             [('reference', read(CONTROL/'reactive-fitted-rows.json')), ('candidate', [by_identity[w['identity']] for w in weights])]}
    for name, endpoint in [('reference', reference), ('candidate', chosen)]:
        assert math.isclose(math.fsum(costs[name].values()), endpoint['cost'], rel_tol=1e-8)
    binary = read(BINARY)
    old_bin = binary_rows(read(BINARY.parents[1]/'413-comparison.json'))
    new_bin = binary_rows(binary['rows'])
    groups = []
    for stage, a, b in [('reactive', old, new), ('binary', old_bin, new_bin)]:
        if stage == 'reactive':
            a, b = ([r for r in rows if r['group'] not in ('Horstmann', 'Cai')] for rows in (a,b))
        for group, role in sorted({(r['group'], r['role']) for r in b}):
            block = [r for r in b if (r['group'], r['role']) == (group, role)]
            groups.append(dict(group=group, stage=stage, role=role,
                               **dataset_summary(block), **paired(a, block)))
    pressures = [r for r in new if r['unit'] == 'Pa' and r['group'] != 'Cai']
    bands = [dict(band=label, role=role, **paired(old, block))
             for label in ('absorber', 'intermediate', 'stripper') for role in ('all','fitted','not fitted','comparison only')
             if (block := [r for r in pressures if band(r['T_K']) == label and role in ('all', r['role'])])]
    loaded = [r for r in pressures if r['role'] == 'fitted']
    solution = [r for r in new_bin if r['role'] == 'fitted' and r['unit'] == 'kPa']
    process = [dict(x_water=label, **paired(old_bin, [r for r in solution if r['group'] == VLE and lo <= float(r['row']['x_water']) < hi]))
               for label,lo,hi in [('0.85–<0.95', .85, .95), ('≥0.95 (mixtures)', .95, 1)]]
    def pascal(rows):
        return [dict(r, unit='Pa', observed=1000*r['observed'], value=None if r['value'] is None else 1000*r['value'])
                for r in rows if r['unit'] == 'kPa']
    assert (len(loaded), len(solution)) == (30, 49)
    table7 = dict(loaded_calibration=paired(old, loaded), binary_calibration_pressure=paired(old_bin, solution),
                  loaded_outside_reactive_fit=paired(old, [r for r in pressures if r['role'] == 'not fitted']),
                  concentrated_Lawson=paired(old, [r for r in pressures if r['role'] == 'comparison only']),
                  pooled_calibration_pressures=paired(old+pascal(old_bin), loaded+pascal(solution)))
    information = read(run/'conditional-uncertainty.json')
    dump(out/'comparisons.json', dict(table7=table7, tableS10=groups, pressure_bands=bands, process_range=process, objective=costs,
                                     reactive_conditional_covariance=dict(coordinates=information['free_coordinates'], entries=covariance(information))))
    binary_se = binary_uncertainty(binary, chosen['parameters']['parameters'])
    for estimate in binary_se.values():
        estimate['conditional_covariance'] = covariance(estimate)
    dump(out/'binary-uncertainty.json', binary_se)
    dump(out/'inputs.json', dict(issue=425, amended_disposition='reactive comparison for owner decision',
                                replacement_adopted=False, engine=read(BINARY.parents[1]/'downstream.json')['wheel'],
                                input_sha256={str(p.relative_to(ROOT)): sha(p) for p in
                                              (ROUTE, BINARY, CONTROL/'reactive-objective.json', REFERENCE/'selection.json', REFERENCE/'paper-data.csv')},
                                binary=dict(a=binary['a'], b_K=binary['b'], reference_K=T_REF,
                                            temperature_endpoints_K=[293.15, 458.64], k_endpoints=binary['k_endpoints']),
                                selected_start=chosen['name'], reactive_fit='run/selection.json',
                                starts=[f'run/binary-frozen-start-{i}.json' for i in range(2)],
                                stability='run/stability-readback.json', data_roles_and_comparisons='comparisons.json'))


if __name__ == '__main__':
    report(*map(Path, sys.argv[1:3]))
