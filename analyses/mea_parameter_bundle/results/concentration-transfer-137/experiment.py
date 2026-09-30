"""#137 common concentration calibration; Engine owns all solves and fitting.

Run serially with one thread: prepare | assess LABEL RECORD | fit EXP START.
"""
import base64
import copy
import csv
import hashlib
import importlib.metadata
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[1]
sys.path[:0] = [str(BUNDLE / 'model-d'), str(BUNDLE / 'calibration-misfit')]
import fit as design
import compare
import probe
import refit
sys.path.insert(0, str(BUNDLE / 'model-d/born-form-diagnosis'))
import born_form_diagnosis as d
s, regression = probe.shared, refit.regression
ADOPTED = BUNDLE / 'results/selected-current-best-parameters.json'
SECOND = BUNDLE / 'model-d/1-1-S1-40-80C-fit-f66d972c-parameters.json'
RAW = BUNDLE / 'results/runs/137-transfer'
s.RUNS = RAW / 'cache'
probe.RECORD = ADOPTED
refit.REACTIONS = probe.reactions()
CAL_IDS = [f'vle_obs_{i:04}' for i in [*range(1, 28), *range(70, 96)]]
OUT_IDS = [f'vle_obs_{i:04}' for i in [*range(28, 34), *range(96, 107)]]
TRANSFER = probe.pressure_observations(lambda r: r['observation_id'] in CAL_IDS + OUT_IDS)
CANONICAL = {r['observation_id']: r for r in csv.DictReader(s.CANONICAL_VLE.open())}
NEUTRAL = 'pair/monoethanolamine/water/k_ij'


def save(path, value):
    path.write_text(json.dumps(s._jsonable(value), indent=2, allow_nan=False) + '\n')


write_rows = d.table


def verify():
    s.verify_wheel()
    distribution = importlib.metadata.distribution('epcsaft')
    count = 0
    for name, digest, size in csv.reader(distribution.read_text('RECORD').splitlines()):
        if digest:
            algorithm, expected = digest.split('=', 1)
            data = Path(distribution.locate_file(name)).read_bytes()
            assert base64.urlsafe_b64encode(hashlib.new(algorithm, data).digest()).decode().rstrip('=') == expected, name
            assert len(data) == int(size), name
            count += 1
    origin = Path(probe.epcsaft.__file__).resolve()
    assert origin.is_relative_to((probe.W / '.venv').resolve()), origin
    assert s.sha256(ADOPTED) == '9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241'
    return {'wheel_sha256': s.ENGINE_WHEEL_SHA256, 'installed_record_hashes': count, 'module_origin': str(origin)}


def prepare():
    environment = verify()
    assert len(TRANSFER) == 70 and len(probe.CANONICAL) == 161 and len(probe.OBSERVATIONS) == 123
    for ids, expected in [(CAL_IDS, 'fae4b717463a29abcd6f1025c58531d3aaa5a31f3bb1cadcb65cc1bb9c8aa76e'),
                          (OUT_IDS, 'bc1d9c897627994d965e3ace5954fe81d46e902e0696451e8844567ddb652b5a')]:
        assert hashlib.sha256(('\n'.join(sorted(ids)) + '\n').encode()).hexdigest() == expected
    rows = []
    metrology_path = probe.W / 'data/reference/MEA/manifests/pco2_metrology_manifest.csv'
    metrology = {r['observation_id']: r for r in csv.DictReader(metrology_path.open())}
    for observation in TRANSFER:
        identity = observation['identity'].removeprefix('canonical:')
        row = CANONICAL[identity]
        system = observation['request']['reaction_system']
        carbon, mea = system['conserved_totals']
        assert abs((carbon - 2 * mea) / mea - float(row['CO2_loading'])) < 1e-12
        assert observation['request']['pressure']['role'] == 'solved'
        assert row['source_key'] == 'Aronu2011' and float(row['MEA_weight_fraction']) in (0.15, 0.45)
        source_path = s.CANONICAL_VLE.parent / row['source_file']
        source = list(csv.DictReader(source_path.open()))[int(row['source_row']) - 1]
        assert float(source['CO2_pressure']) == float(row['CO2_pressure'])
        assert float(source['CO2_loading']) == float(row['CO2_loading'])
        rows.append({**row, 'issue_137_role': 'multi-concentration calibration' if identity in CAL_IDS else 'out-of-fit assessment',
                     'source_sha256': s.sha256(source_path), 'source_locator': metrology[identity]['source_locator'],
                     'measured_quantity': metrology[identity]['measured_primitive'], 'observed_pa': float(row['CO2_pressure']) * 1000,
                     'sigma_ln_pressure': compare.SIGMA_LN_P, 'uncertainty': metrology[identity]['uncertainty_status'],
                     'covariance': metrology[identity]['covariance_status'], 'conserved_loading': (carbon - 2 * mea) / mea})
    write_rows(HERE / 'admitted-observations.csv', rows)
    save(HERE / 'materialized-inputs.json', {'calibration_ids': CAL_IDS, 'assessment_ids': OUT_IDS,
         'transfer_observations': TRANSFER, 'packet_observations': probe.OBSERVATIONS, 'canonical_observations': probe.CANONICAL})
    inputs = [ADOPTED, SECOND, s.STATE_PACKET, s.CANONICAL_VLE, metrology_path, Path(probe.__file__),
              Path(refit.__file__), Path(compare.__file__), Path(s.__file__), Path(__file__), HERE / 'materialized-inputs.json',
              HERE / 'admitted-observations.csv']
    save(HERE / 'input-hashes.json', {'environment': environment, 'base_commit': 'd8c4cd1531b150fda915abc258a872a98272aad2',
         'owner_decision': 'https://github.com/tannerpolley/Amine-Thermodynamics/issues/137#issuecomment-5918434068',
         'hashes': {str(p.relative_to(probe.W)): s.sha256(p) for p in inputs},
         'reaction_values': refit.REACTIONS, 'process_timeout_s': 1800, 'maximum_iterations': 40,
         'fitter_maximum_elapsed_time_s': 2250, 'threads': 1})


def assess(label, record):
    verify()
    probe.RECORD = record
    assert s.reaction_values(s.parameter_mapping(record)) == refit.REACTIONS
    detailed, groups, residuals, failed, checks = [], {}, [], [], []
    d.HERE, d.DEADLINE = RAW, time.perf_counter() + 1790
    baseline = [json.loads(line) for line in (RAW / 'baseline-packet.jsonl').read_text().splitlines()]
    d.ANCHORS['11'] = {r['identity']: r for r in baseline}
    rescore = d.evaluate(label + '-160-target-rescore', s.parameter_mapping(record))
    existing = {r['identity']: r for r in map(json.loads, (RAW / f'{label}-160-target-rescore-states.jsonl').read_text().splitlines())}
    existing.update({r['identity']: r for r in baseline if r['identity'] not in existing} if label == 'baseline' else {})
    clock = time.perf_counter()
    for family, observations in [('packet', probe.OBSERVATIONS), ('canonical', probe.CANONICAL), ('aronu', TRANSFER)]:
        with (RAW / f'{label}-{family}.jsonl').open('a') as handle:
            for observation in observations:
                if family == 'packet' and observation['identity'] in existing:
                    result = existing[observation['identity']]
                else:
                    result = next(probe.evaluate(states=[observation]))
                    handle.write(json.dumps(result) + '\n'); handle.flush()
                checks.append({'family': family, 'identity': result['identity'], **result['check']})
                tc = round(result['T'] - 273.15)
                if result['status'] != 'evaluated':
                    failed.append({'family': family, 'identity': result['identity'], 'temperature_c': tc, 'check': result['check']})
                system = observation['request']['reaction_system']
                carbon, mea = system['conserved_totals']
                loading = (carbon - 2 * mea) / mea
                identity = result['identity'].removeprefix('canonical:')
                fraction = float(CANONICAL[identity]['MEA_weight_fraction']) if family != 'packet' else 0.3
                for target, residual in zip(result['targets'], compare.residuals(result) or [None] * len(result['targets']), strict=True):
                    pressure = target['prediction_identity'] == 'co2-partial-pressure'
                    predicted = compare.predicted(result, target) if result['status'] == 'evaluated' else None
                    ln = math.log(predicted / target['observed']) if predicted and target['observed'] > 0 else None
                    weighted = residual[2] if residual else None
                    fitted = (family == 'packet' and compare.in_working_objective(result, target)) or (family == 'aronu' and identity in CAL_IDS)
                    cost_group = ('packet_pressure' if pressure else 'packet_species') if family == 'packet' else 'aronu_pressure'
                    if fitted:
                        residuals.append({'target': target['identity'], 'group': cost_group, 'weighted_residual': weighted})
                    detailed.append({'family': family, 'identity': result['identity'], 'target': target['identity'],
                        'source': target['source_identity'], 'temperature_c': tc, 'mea_mass_fraction': fraction, 'loading_mol_per_mol': loading,
                        'observed': target['observed'], 'predicted': predicted, 'unit': 'Pa' if pressure else 'mol/mol true species',
                        'ln_pred_over_obs': ln, 'weighted_residual': weighted, 'calibration_member': fitted, 'status': result['status'],
                        **result['check'], 'parameter_sha256': s.sha256(record)})
                    keys = []
                    if family == 'aronu':
                        role = 'calibration' if identity in CAL_IDS else 'out-of-fit'
                        keys = [f'aronu_w={fraction}_all', f'aronu_w={fraction}_{role}', f'aronu_w={fraction}_T={tc}C',
                                f'aronu_w={fraction}_loading=' + ('<0.3' if loading < 0.3 else '0.3-0.5' if loading < 0.5 else '>=0.5')]
                    if family == 'canonical' and 40 <= tc <= 80:
                        keys = ['30wt_pressure_gate_104']
                        if tc == 80:
                            keys += ['30wt_80C_pressure', f"source={target['source_identity']}_80C_pressure"]
                    if family == 'packet':
                        if fitted:
                            keys = [f'packet_fitted_{"pressure" if pressure else "species"}']
                        if tc == 80:
                            keys += [f'packet_80C_{"pressure" if pressure else "species"}']
                    for key in keys:
                        groups.setdefault(key, []).append(ln)
                print(label, family, result['identity'], result['status'], flush=True)
    metrics = {key: {'n_rows': len(values), 'n_available': sum(x is not None for x in values),
                **(compare.stats(values) if all(x is not None for x in values) else {})} for key, values in groups.items()}
    costs = {key: sum(0.5 * r['weighted_residual']**2 for r in residuals if r['group'] == key)
             if all(r['weighted_residual'] is not None for r in residuals if r['group'] == key) else None
             for key in ('packet_pressure', 'packet_species', 'aronu_pressure')}
    write_rows(HERE / f'{label}-evaluated-rows.csv', detailed)
    save(HERE / f'{label}-assessment.json', {'metrics': metrics, 'costs': costs, 'original_160_split': {k: rescore[k] for k in ('pressure_cost', 'bottinger_cost', 'matin_cost')}, 'fitted_targets': len(residuals),
         'failures': failed, 'checks': checks, 'wall_s': time.perf_counter() - clock, 'parameter_sha256': s.sha256(record)})


def fit(experiment, start_name):
    verify()
    baseline = json.loads((HERE / 'baseline-assessment.json').read_text())
    assert abs(sum(baseline['costs'][k] for k in ('packet_pressure', 'packet_species')) - 32.9918972612169) < 1e-8
    assert not [f for f in baseline['failures'] if f['temperature_c'] <= 80]
    ids = list(design.S1)
    lower, upper = (list(x) for x in zip(*design.S1.values()))
    if experiment == '1':
        start = s.parameter_values(s.parameter_mapping(ADOPTED if start_name == 'adopted' else SECOND))
    else:
        fits = [json.loads(p.read_text()) for p in HERE.glob('experiment-1-*-fit.json')]
        assert len(fits) == 2 and all(f['status'] == 'converged' for f in fits)
        fits.sort(key=lambda f: f['final_cost'])
        start = dict(zip(ids, fits[int(start_name)]['physical']))
        neutral_base = s.parameter_values(s.parameter_mapping(ADOPTED))[NEUTRAL]
        ids.append(NEUTRAL); lower.append(neutral_base - 0.1); upper.append(neutral_base + 0.1)
        start[NEUTRAL] = neutral_base + (0.02 if start_name == '1' else 0)
    values = [start[i] for i in ids]
    assert design.admissible(ids, values, '40-80')
    params = refit.parameters(values, ids)
    calibration = []
    for observation in probe.OBSERVATIONS + TRANSFER:
        o = copy.deepcopy(observation)
        o['targets'] = [t for t in o['targets'] if (o['identity'].removeprefix('canonical:') in CAL_IDS
                        or compare.in_working_objective(refit._rec(o), t))]
        if not o['targets']:
            continue
        base = probe.base_record(o)
        assert base['status'] == 'evaluated', (o['identity'], base.get('failure_code'))
        calibration.append((o, s._problem_from_request(s.corrected_request(o['request'], refit.REACTIONS), s.anchor_from(base))))
        print('prepared', o['identity'], flush=True)
    rows = [r for o, problem in calibration for r in refit.observations(params, o, problem, 80)]
    assert len(rows) == 195 and len(calibration) == 137
    scales = [10 if i.endswith(probe.SLOPE) else 0.01 for i in ids]
    coordinates = [regression.coordinate(params, 'k_ij_reciprocal_temperature_slope' if i.endswith(probe.SLOPE) else 'k_ij',
                    tuple(i.split('/')[1:3]), origin=value, scale=scale, bounds=(lo, hi))
                   for i, value, scale, lo, hi in zip(ids, values, scales, lower, upper)]
    controls = regression.FitControls(); controls.maximum_iterations = 40; controls.maximum_elapsed_time_seconds = 2250
    clock = time.perf_counter()
    result = regression.fit(params, coordinates, [r[1] for r in rows], weights=[r[2] for r in rows], controls=controls)
    name = f'experiment-{experiment}-{start_name}'
    output = {key: s._jsonable(getattr(result, key)) for key in ('status', 'message', 'usable', 'physical', 'weighted_residuals',
        'optimizer_jacobian', 'physical_jacobian', 'iterations', 'residual_evaluations', 'jacobian_evaluations', 'trial_failures',
        'iteration_costs', 'iteration_seconds', 'initial_cost', 'final_cost')}
    output.update(coordinates=ids, start=values, scales=scales, targets=[r[0] for r in rows], fit_s=time.perf_counter() - clock,
        observation_statuses=[x.name for x in result.statuses], failures=[{'trial': f.trial, 'observation': rows[f.observation][0],
        'status': f.status.name, 'message': f.message, 'jacobian': f.jacobian} for f in result.failures],
        active_bounds=[ids[k] for k in result.covariance.active_bounds], engine_covariance={k: getattr(result.covariance, k) for k in ('status', 'assumption', 'rank', 'singular_values', 'variance_factor')},
        optimizer_updates=max(0, result.iterations - 1), native_history_rows=result.iterations,
        k_at_domain_ends=design.domain_ends(ids, result.physical, (293.15, 353.15)), admissible=design.admissible(ids, result.physical, '40-80'))
    save(RAW / f'{name}-native-fit.json', output)
    if len(result.optimizer_jacobian):
        jacobian = np.array(result.optimizer_jacobian).reshape(195, len(ids)) / scales
        output['weighted_physical_jacobian_singular_values'] = np.linalg.svd(jacobian, compute_uv=False).tolist()
        output['column_normalized_singular_values'] = np.linalg.svd(jacobian / np.linalg.norm(jacobian, axis=0), compute_uv=False).tolist()
        output['jacobian_column_correlations'] = np.corrcoef(jacobian, rowvar=False).tolist()
    for key in ('optimizer_jacobian', 'physical_jacobian'):
        output.pop(key)
    save(HERE / f'{name}-fit.json', output)
    final = probe.with_values(s.parameter_mapping(ADOPTED), dict(zip(ids, result.physical)))
    assert s.reaction_values(final) == refit.REACTIONS
    final['purpose'] = 'Issue 137 multi-concentration calibration comparison; not adopted or physically validated.'
    save(HERE / f'{name}-parameters.json', final)
    print(json.dumps({'name': name, 'status': result.status, 'cost': result.final_cost, 'fit_s': output['fit_s']}), flush=True)


if __name__ == '__main__':
    RAW.mkdir(parents=True, exist_ok=True)
    command, *arguments = sys.argv[1:]
    if command == 'prepare':
        prepare()
    elif command == 'assess':
        assess(arguments[0], Path(arguments[1]))
    elif command == 'fit':
        fit(*arguments)
    else:
        raise SystemExit('prepare | assess LABEL RECORD | fit EXP START')
