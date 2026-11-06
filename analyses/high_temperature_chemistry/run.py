"""Issue 263: source-law replacement and bounded reaction-only MEA fits."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable
from qualify import AN, ROOT, SHA

BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
sys.path.insert(0, str(BUNDLE / 'scripts'))
import shared_evaluation as shared
import fit_observations as fo
import kim2007_heat_pathways as kim

EVIDENCE = BUNDLE / 'results/engine-3e83e19c-paper-evidence'
OUT = AN / 'results'
FIELDS = ('a', 'b', 'c', 'd', 'e', 'f', 'reference_temperature', 'temperature_min', 'temperature_max', 'standard_state_id')


def read(path):
    return list(csv.DictReader(Path(path).open()))


def write(name, value):
    (OUT / name).write_text(json.dumps(jsonable(dict(wheel_sha256=SHA, **value)), indent=2, allow_nan=False) + '\n')


def law_fields(law):
    return {k: getattr(law, k) for k in FIELDS}


def source_law():
    rows = read(AN / 'inputs/hamborg-table16.csv')
    t, y, u = np.array([[float(r[k]) for r in rows] for k in ('temperature_K', 'ln_K', 'printed_uncertainty')])
    x = np.column_stack((1 / t, np.ones(len(t)), np.log(t)))
    q, _, rank, singular = np.linalg.lstsq(x / u[:, None], y / u, rcond=None)
    a, b, c = q
    coefficients = dict(a=float(b + c * np.log(313.15)), b=float(a), c=float(c), d=0., e=0., f=0., reference_temperature=313.15)
    checks = []
    model = eq.IdealMoleFraction(['source', 'product'], [0, 0])
    for temperature, expected in zip(t, x @ q):
        law = eq.ReactionLogPolynomial(**coefficients, temperature_min=float(min(t)), temperature_max=float(max(t)),
                                       standard_state_id=eq.IDEAL_MOLE_FRACTION_STANDARD_STATE_ID)
        problem = eq.Problem(T=float(temperature), P=100000., feed=eq.Amounts({'source': 1., 'product': 1e-8}),
            phases=[eq.Phase('liquid', kind='liquid', support=('source', 'product'))],
            reactions=[eq.Reaction({'source': -1., 'product': 1.}, name='source-law', correlation=law)], row_tolerance=1e-12)
        result = eq.solve_equilibrium(model, problem)
        actual = math.log(result.mole_fractions[1] / result.mole_fractions[0])
        checks.append(dict(T_K=float(temperature), expected=float(expected), native=actual, error=abs(actual - expected),
                           tolerance_met=result.requested_tolerance_met))
    assert rank == 3 and max(r['error'] for r in checks) <= 1e-10 and all(r['tolerance_met'] for r in checks)
    write('hamborg-law.json', dict(coefficients=coefficients, source_form_coefficients=q.tolist(),
        residuals=(x @ q - y).tolist(), weighted_residuals=((x @ q - y) / u).tolist(),
        conditional_covariance=np.linalg.inv((x / u[:, None]).T @ (x / u[:, None])).tolist(),
        covariance_assumption='Printed uncertainty scales treated as independent standard deviations solely for conditional weighting.',
        weighted_design_condition=float(singular[0] / singular[-1]), normal_matrix_condition=float((singular[0] / singular[-1])**2), checks=checks,
        extrapolation_above_K=float(max(t)), source_sha256=hashlib.sha256((AN / 'inputs/hamborg-table16.csv').read_bytes()).hexdigest()))
    return coefficients


def inputs(spec):
    source_paths, pressure = [], []
    for path in sorted((EVIDENCE / 'selected-assessment/states-rows').glob('*.json')):
        data = json.loads(path.read_bytes())['input']
        if data['group'] == 'canonical':
            source_paths.append(path)
            pressure.append(data['observation'])
    packet_path = BUNDLE / 'results/source-corrections-152/state-packet.json.gz'
    packet = shared.load_state_packet(packet_path)['observations']
    species = [o for o in packet if o['identity'] in {f'Bottinger2008_state_{i:03d}' for i in range(63, 68)}]
    assert len(pressure) == 159 and len(species) == 5
    mapping = spec.inputs['endpoint']
    problems = {}
    for observation in pressure + species:
        request = shared.corrected_request(observation['request'], shared.reaction_values(mapping), mapping=mapping)
        problem = shared._problem_from_request(request)
        problem.row_tolerance = 1e-10
        problems[observation['identity']] = problem
    measured = {r['target']: r for r in read(EVIDENCE / 'species-figure-data.csv')}
    baseline = {r['target']: r for r in read(EVIDENCE / 'state-targets.csv') if r['kind'] == 'canonical' and r['quantity'] == 'pressure'}
    fitted = {r['identity'] for r in spec.inputs['observations']['fitted']}
    assert sum(o['targets'][0]['identity'] in fitted for o in pressure) == 47
    write('comparison-inputs.json', dict(pressure=pressure, species=species,
        input_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [*source_paths, packet_path, EVIDENCE / 'species-figure-data.csv', EVIDENCE / 'state-targets.csv', kim.SOURCE]},
        species_residual_owner='calibration-misfit/refit.py: (pred-observed)/(0.1*observed+0.001), weight 1'))
    return pressure, species, problems, measured, baseline, fitted


def assign(problems, laws):
    for problem in problems:
        reactions = problem.reactions
        for reaction in reactions:
            if reaction.name in laws:
                coefficients = {k: v for k, v in laws[reaction.name].items() if k not in ('temperature_min', 'temperature_max', 'standard_state_id')}
                reaction.correlation = eq.ReactionLogPolynomial(**dict(law_fields(reaction.correlation), **coefficients))
        problem.reactions = reactions


def prediction(model, item, **details):
    try:
        p = reg.predict(model, item)
        return dict(details, **{k: jsonable(getattr(p, k)) for k in ('value', 'residual', 'status', 'message', 'requested_tolerance_met', 'branch', 'stable_root_count')})
    except Exception as error:
        return dict(details, status='Exception', message=f'{type(error).__name__}: {error}', value=None)


def usable(row):
    return row['status'] == 'Available' and row['requested_tolerance_met'] and isinstance(row['value'], (int, float)) and math.isfinite(row['value'])


def species_items(spec, observations, problems, measured):
    result = []
    for o in observations:
        for target in o['targets']:
            if target['identity'].endswith(('::MEA + MEAH+', '::MEACOO-')):
                r = measured[target['identity']]
                species = ('monoethanolamine', 'protonated-monoethanolamine') if r['species'] == 'MEA + MEAH+' else ('carbamate-anion',)
                item = reg.observation(spec.parameters, 'mole_fraction', problems[o['identity']], phase=problems[o['identity']].phases[0].name,
                    species=species, observed=float(r['observed']), form='difference', scale=.1 * float(r['observed']) + .001)
                result.append((target['identity'], item))
    return result


def assessment(name, spec, declarations, laws):
    pressure, species, problems, measured, baseline, fitted = declarations
    assign([*spec.problems.values(), *problems.values()], laws)
    rows = []
    for o in pressure:
        t = o['targets'][0]
        assert t['observed'] == float(baseline[t['identity']]['observed'])
        item = reg.observation(spec.parameters, 'partial_pressure', problems[o['identity']], phase=problems[o['identity']].phases[1].name,
                               species=('carbon-dioxide',), observed=t['observed'], form='log_ratio')
        row = prediction(spec.model, item, family='pressure', identity=t['identity'], observed=t['observed'], fitted=t['identity'] in fitted,
                         source=t['source_identity'], T_K=float(problems[o['identity']].T), unit='Pa')
        if usable(row):
            row['relative_error_percent'] = 100 * (row['value'] / row['observed'] - 1)
            row['incumbent_prediction_relative_difference'] = abs(row['value'] / float(baseline[t['identity']]['predicted']) - 1)
        rows.append(row)
        print(name, o['identity'], row['status'], flush=True)
    if name == 'baseline':
        assert all(usable(r) and r['incumbent_prediction_relative_difference'] <= 1e-6 for r in rows)
    for o in species:
        for r in (r for r in measured.values() if r['identity'] == o['identity']):
            selector = {'MEA + MEAH+': ('monoethanolamine', 'protonated-monoethanolamine'), 'MEACOO-': ('carbamate-anion',),
                        'HCO3-': ('bicarbonate-anion', 'carbonate-anion')}[r['species']]
            item = reg.observation(spec.parameters, 'mole_fraction', problems[o['identity']], phase=problems[o['identity']].phases[0].name,
                                   species=selector, observed=float(r['observed']), form='difference', scale=.1 * float(r['observed']) + .001)
            row = prediction(spec.model, item, family='species', identity=r['target'], observed=float(r['observed']), species=r['species'],
                             loading=float(o['request']['reaction_system']['analytical_feed_contract']['source_coordinates']['CO2_loading']), T_K=353.15, P_Pa=101325., mea_mass_fraction=.31, unit='mole fraction')
            if usable(row):
                row['relative_error_percent'] = 100 * (row['value'] / row['observed'] - 1) if row['observed'] else None
            rows.append(row)
    heat_request = species[0]['request']
    heat_rows = []
    for r in kim.source_rows():
        if r['T_K'] not in (313.15, 353.15, 393.15):
            continue
        if r['loading'] > .6:
            heat_rows.append(dict(identity=r['record_id'], status='OutsideLoadingDomain', value=None, T_K=r['T_K']))
            continue
        if r['T_K'] not in (313.15, 353.15, 393.15):
            continue
        native = fo.heat_items(spec.inputs['endpoint'], spec.parameters, [dict(temperature_K=r['T_K'], system_pressure_Pa=kim.PRESSURE,
                 alpha_final=r['loading'], observed_addition_enthalpy_J_per_mol_CO2=0., uH_J_per_mol_CO2=1000.)], heat_request)[0]
        initial, final = native.problem, native.final_problem
        # The existing heat owner compiles its extensive feeds; retain those exact amounts.
        feed = initial.feed
        feed.values = [r['previous_loading'], *list(final.feed.values)[1:]]
        initial.feed = feed
        initial.row_tolerance = final.row_tolerance = 1e-10
        assign([initial, final], laws)
        item = native
        item.problem, item.final_problem = initial, final
        item.feed_amount = r['loading'] - r['previous_loading']
        item.observed = -1000 * float(r['dHdiff_kJ_per_mol_CO2_reported'])
        row = prediction(spec.model, item, identity=r['record_id'], T_K=r['T_K'], loading=r['loading'], previous_loading=r['previous_loading'],
            source_inconsistent=r['source_inconsistent'], observed=float(r['dHdiff_kJ_per_mol_CO2_reported']), unit='kJ/mol CO2, positive release', P_Pa=kim.PRESSURE)
        if usable(row):
            row['native_value_J_per_mol'] = row['value']
            row['residual_convention'] = 'Signed addition-enthalpy difference / 1000 J/mol; value and observed are separately reported as positive heat release.'
            row['value'] /= -1000.
            row['relative_error_percent'] = 100 * (row['value'] / row['observed'] - 1)
        heat_rows.append(row)
        print(name, r['record_id'], row['status'], flush=True)
    print(name, 'assessment complete', len(rows), len(heat_rows), flush=True)
    write(name + '-assessment.json', dict(laws=laws, rows=rows, heat=heat_rows,
        detected_instabilities=None, instability_unavailability='No global stability search in this probe; native prediction root diagnostics are retained separately.'))
    return rows, heat_rows


def fit_case(name, holdout):
    started = time.perf_counter()
    spec = SolventSpecification(ROOT / 'analyses/solvent_specification_mea/MEA.toml')
    declarations = inputs(spec)
    pressure, species, problems, measured, _, _ = declarations
    records = spec.inputs['observations']['fitted']
    extra = [(i, item) for i, item in species_items(spec, species, problems, measured) if not (holdout and 'state_067' in i)]
    observations = [spec.observation(r) for r in records] + [item for _, item in extra]
    weights = [r['weight'] for r in records] + [1.] * len(extra)
    coordinates = [reg.reaction_enthalpy_shift(n, pivot_temperature=313.15, origin=0., scale=2500., bounds=(-10000., 10000.)) for n in ('R4', 'R5')]
    controls = reg.FitControls(maximum_iterations=60, maximum_elapsed_time_seconds=1200., function_tolerance=1e-8,
                               parameter_tolerance=1e-10, gradient_tolerance=1e-8, workers=os.cpu_count())
    print(name, 'fit starts', len(observations), flush=True)
    result = reg.fit(spec.parameters, coordinates, observations, weights=weights, thermochemistry=spec.thermal, controls=controls, singular_vectors=True)
    laws = {n: law_fields(law) for n, law in result.chart.reaction_laws.items()}
    report = {k: jsonable(getattr(result, k)) for k in ('status', 'message', 'usable', 'initial_cost', 'final_cost', 'optimizer', 'physical',
        'weighted_residuals', 'residuals', 'predictions', 'iterations', 'trial_failures', 'iteration_costs', 'iteration_seconds')}
    report.update(laws=laws, included=[r['identity'] for r in records] + [i for i, _ in extra],
        shifts_j_per_mol=list(result.chart.physical), active_bounds=list(result.covariance.active_bounds),
        failures=[dict(trial=f.trial, observation=f.observation, status=f.status.name, message=f.message) for f in result.failures],
        wall_seconds=time.perf_counter() - started, holdout='Bottinger2008_state_067' if holdout else None)
    write(name + '-fit.json', report)
    if not result.usable:
        return
    assign([*spec.problems.values(), *problems.values()], laws)
    replay = [spec.prediction(r) for r in records] + [prediction(spec.model, item, identity=i) for i, item in species_items(spec, species, problems, measured) if not (holdout and 'state_067' in i)]
    assert all(usable(p) for p in replay)
    weighted = [p['residual'] * math.sqrt(w) for p, w in zip(replay, weights, strict=True)]
    cost = math.fsum(.5 * w*w for w in weighted)
    write(name + '-replay.json', dict(rows=replay, weighted_residuals=weighted, cost=cost, cost_relative=abs(cost/result.final_cost - 1),
                                     maximum_residual_difference=max(abs(a-b) for a,b in zip(weighted, result.weighted_residuals, strict=True))))
    assert abs(cost/result.final_cost - 1) <= 1e-8 and max(abs(a-b) for a,b in zip(weighted, result.weighted_residuals, strict=True)) <= 1e-8
    assessment(name, spec, declarations, laws)


if __name__ == '__main__':
    assert json.loads((OUT / 'qualification.json').read_bytes())['passed']
    case = sys.argv[1]
    if case in ('all-five', 'holdout'):
        fit_case(case, case == 'holdout')
    else:
        spec = SolventSpecification(ROOT / 'analyses/solvent_specification_mea/MEA.toml')
        laws = {r.name: law_fields(r.correlation) for r in next(iter(spec.problems.values())).reactions if r.name in ('R4', 'R5')}
        if case == 'hamborg':
            laws['R5'].update(source_law())
        assessment(case, spec, inputs(spec), laws)
