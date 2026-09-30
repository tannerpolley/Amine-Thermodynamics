"""MEA #121 v2--v2.2: bounded Born-form diagnosis, pinned installed Engine only."""
import time
STARTED = time.perf_counter()
import copy
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import lsq_linear

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
BUNDLE = MODEL.parent
ROOT = BUNDLE.parents[1]
sys.path.insert(0, str(MODEL))
import fit as design
from epcsaft import equilibrium, regression
import compare

s = design.probe.shared
epcsaft = design.probe.epcsaft
s.RUNS = HERE / 'cache'
IDS = list(design.S1)
LOWER, UPPER = (np.array(x) for x in zip(*design.S1.values()))
SCALES = np.array([10.0 if i.endswith(design.probe.SLOPE) else 0.01 for i in IDS])
FILES = {
    '11': MODEL / '1-1-S1-40-80C-fit-f66d972c-parameters.json',
    '00': MODEL / '0-0-S1-40-80C-fit-28181e72-parameters.json',
}
PACKETS = {
    '11': MODEL / '1-1-S1-40-80C-fit-f66d972c-eval-28181e72-packet.jsonl',
    '00': MODEL / '0-0-S1-40-80C-fit-28181e72-eval-28181e72-packet.jsonl',
}
MAPPINGS = {form: s.parameter_mapping(path) for form, path in FILES.items()}
RETAINED = {form: {r['identity']: r for r in map(json.loads, path.open())} for form, path in PACKETS.items()}
OBS = [o for o in design.probe.OBSERVATIONS if any(compare.in_objective(
    {'T': o['request']['temperature']['value'], 'identity': o['identity']}, t, 80) for t in o['targets'])]
assert len(OBS) == 84
ION_IDS = ('protonated-monoethanolamine', 'carbamate-anion', 'bicarbonate-anion',
           'carbonate-anion', 'hydroxide-anion', 'hydronium-cation')
QIDS = [f'component/{i}/born_diameter' for i in ION_IDS] + [
    'model/electrolyte/c_shell', 'component/monoethanolamine/solvation_factor',
    'model/electrolyte/c_dielectric']
QBOUNDS = [(2., 5.)] * 5 + [(1., 2.), (0., 1.), (1., 2.), (0., 1.)]
GROUPS = {'main-diameters': [0, 1, 2], 'secondary-diameters': [3, 4, 5],
          'shell-and-MEA': [6, 7], 'saturation': [8], 'joint': [0, 1, 2, 6, 7]}
LEDGER = HERE / 'job-times.json'
OLD_JOBS = json.loads(LEDGER.read_text()) if LEDGER.exists() else []
DEADLINE = STARTED + 2700.0 - sum(j.get('charged_s', j['wall_s']) for j in OLD_JOBS)
ANCHORS = {}


def save(name, value):
    (HERE / name).write_text(json.dumps(s._jsonable(value), indent=2, allow_nan=False) + '\n')


def table(name, rows):
    if rows:
        with (HERE / name).open('w', newline='') as h:
            w = csv.DictWriter(h, list(rows[0])); w.writeheader(); w.writerows(rows)


def enough(seconds=0.):
    if time.perf_counter() + seconds >= DEADLINE:
        raise TimeoutError('2700 s total execution budget exhausted')


def values(mapping):
    return {**s.parameter_values(mapping), **{
        f'model/electrolyte/{k}': f[k] for f in mapping['model_families']
        if f['kind'] == 'electrolyte' for k in ('c_shell', 'c_dielectric')}}


def changed(mapping, changes):
    out = s.with_parameter_values(mapping, {k: v for k, v in changes.items() if k not in QIDS[6::2]})
    family = next(f for f in out['model_families'] if f['kind'] == 'electrolyte')
    for name in ('c_shell', 'c_dielectric'):
        if f'model/electrolyte/{name}' in changes:
            family[name] = float(changes[f'model/electrolyte/{name}'])
    return out


def anchor(rec):
    p = rec['liquid']
    return s.Anchor(round(rec['T'] - 273.15), float(rec['feed'][0]), float(p['pressure_pa']),
                    tuple(p['mole_fractions']), float(p['molar_volume_m3_per_mol']))


def declared(mapping, form):
    reactions = s.reaction_values(mapping)
    assert {k: v for k, v in reactions.items() if k.startswith('reaction:R4:')} == design.probe.SOURCE_R4
    if form not in ANCHORS:
        prefit = design.RECORDS['1-1' if form == '11' else '0-0']
        fp = s.parameter_fingerprint(s.parameter_mapping(prefit))
        rh = s._reaction_identity(s.reaction_values(s.parameter_mapping(prefit)))
        candidates = {}
        hashes = {}
        for path in (BUNDLE / 'results/runs/calibration-misfit/cache/states').glob('*.json'):
            rec = json.loads(path.read_text())
            if (rec.get('model_parameters_fingerprint') != fp or rec.get('status') != 'evaluated'
                    or rec.get('effective_reaction_values_sha256') != rh): continue
            identity = rec['identity']
            if identity in candidates and candidates[identity].get('engine_wheel_sha256') == s.ENGINE_WHEEL_SHA256: continue
            candidates[identity] = rec; hashes[identity] = (str(path), s.sha256(path))
        assert all(o['identity'] in candidates for o in OBS), 'accepted fit anchor missing'
        ANCHORS[form] = candidates
        save('accepted-fit-anchor-hashes-' + form + '.json', dict(hashes[o['identity']] for o in OBS))
    return [(o, s._problem_from_request(s.corrected_request(o['request'], reactions),
                                      s.anchor_from(ANCHORS[form][o['identity']]))) for o in OBS]


def rows_for(mapping, form):
    params = epcsaft.Parameters.from_mapping(mapping)
    groups = declared(mapping, form)
    rows = [row for o, problem in groups for row in design.refit.observations(params, o, problem, 80)]
    assert len(rows) == 160
    return params, groups, rows


def split_cost(targets, residuals):
    out = {k: 0.0 for k in ('pressure_cost', 'bottinger_cost', 'matin_cost')}
    counts = dict.fromkeys(out, 0)
    for name, r in zip(targets, residuals, strict=True):
        key = 'pressure_cost' if name.endswith('-pco2') else 'bottinger_cost' if name.startswith('Bottinger') else 'matin_cost'
        out[key] += .5 * float(r) ** 2; counts[key] += 1
    assert list(counts.values()) == [48, 40, 72], counts
    return {**out, 'cost': sum(out.values())}


def publish_evaluation(name, mapping, form, targets, residuals, duration, diagnostics):
    result = {'name': name, 'form': form, 'complete': True, 'targets': targets,
              'weighted_residuals': list(map(float, residuals)), 'inputs': values(mapping),
              'wall_s': duration, **split_cost(targets, residuals), **diagnostics}
    save(name + '.json', result)
    path = HERE / 'objective-evaluations.csv'
    compact = {k: result[k] for k in ('name', 'form', 'complete', 'cost', 'pressure_cost', 'bottinger_cost', 'matin_cost', 'wall_s')}
    compact.update({k: result['inputs'][k] for k in QIDS})
    with path.open('a', newline='') as h:
        w = csv.DictWriter(h, list(compact))
        if path.stat().st_size == 0: w.writeheader()
        w.writerow(compact)
    print(json.dumps(compact), flush=True)
    return result


def state_evaluate(name, mapping, form='11'):
    enough(2.)
    start = time.perf_counter()
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    groups = declared(mapping, form)
    residuals, targets, branches, records = [], [], {}, []
    with (HERE / (name + '-states.jsonl')).open('w') as h:
        for o, problem in groups:
            enough(1.)
            request = s.corrected_request(o['request'], s.reaction_values(mapping))
            solved = equilibrium.solve_equilibrium(model, problem)
            snapshot = s._snapshot_from_payload(s._snapshot_from_result(model, problem, request, solved))
            payload = s._jsonable(snapshot.__dict__)
            liq = next((p for p in snapshot.phases if p['role'] == 'liquid'), None)
            rec = {'identity': o['identity'], 'T': request['temperature']['value'],
                   'feed': request['reaction_system']['feed_amounts_mol'], 'targets': o['targets'],
                   'status': snapshot.status, 'liquid': liq, 'predictions': snapshot.predictions,
                   'check': design.probe.check(payload)}
            h.write(json.dumps(rec) + '\n'); h.flush(); records.append(rec)
            evidence = dict(snapshot.evidence)
            branches[o['identity']] = {'phases': [[p['identity'], p['role'], p['support']] for p in snapshot.phases],
                                      'topology_event': evidence.get('topology_event'),
                                      'rho': [p['molar_density_mol_m3'] for p in snapshot.phases]}
            if snapshot.status != 'evaluated' or not evidence.get('requested_tolerance_met'):
                save(name + '-failure.json', {'name': name, 'complete': False, 'state': o['identity'], 'snapshot': payload})
                raise RuntimeError(f'{name}: unavailable state {o["identity"]}: {snapshot.failure_code}')
            if rec['check']['max_abs_stationarity'] is None or rec['check']['max_abs_stationarity'] > 1e-10:
                raise RuntimeError(f'{name}: stationarity unavailable/outside accepted tolerance')
            for t, (_, identity, rr, _) in zip(o['targets'], compare.residuals(rec), strict=True):
                if compare.in_objective(rec, t, 80): targets.append(identity); residuals.append(rr)
    assert len(residuals) == 160 and np.isfinite(residuals).all()
    baseline_path = HERE / f'branch-baseline-{form}.json'
    if baseline_path.exists() and not name.startswith('branch-baseline'):
        expected = json.loads(baseline_path.read_text())['branches']
        for identity, actual in branches.items():
            assert actual['phases'] == expected[identity]['phases'], 'declared solution branch changed'
            assert actual['topology_event'] == expected[identity]['topology_event'], 'solution topology event changed'
    return publish_evaluation(name, mapping, form, targets, residuals, time.perf_counter()-start,
                              {'states': 84, 'branches': branches,
                               'max_abs_stationarity': max(r['check']['max_abs_stationarity'] for r in records)})


def evaluate(name, mapping, form='11'):
    # Native solves share one immutable model; retain the existing evaluator's
    # balance, stationarity, phase and reference diagnostics for every state.
    return state_evaluate(name, mapping, form)


def fitted(name, mapping, form, iterations=1, elapsed=1e-6):
    enough(3.)
    start = time.perf_counter()
    params, groups, rows = rows_for(mapping, form)
    v = values(mapping)
    coordinates = [regression.coordinate(params,
        'k_ij_reciprocal_temperature_slope' if identity.endswith(design.probe.SLOPE) else 'k_ij',
        tuple(identity.split('/')[1:3]), origin=v[identity], scale=scale, bounds=(lo, hi))
        for identity, scale, lo, hi in zip(IDS, SCALES, LOWER, UPPER)]
    controls = regression.FitControls(); controls.maximum_iterations = iterations
    controls.maximum_elapsed_time_seconds = min(elapsed, max(.001, DEADLINE-time.perf_counter()-5.))
    result = regression.fit(params, coordinates, [item for _, item, _ in rows], weights=[w for _, _, w in rows], controls=controls)
    targets = [name for name, _, _ in rows]
    raw = {k: s._jsonable(getattr(result, k)) for k in ('status', 'message', 'physical', 'predictions',
        'residuals', 'weighted_residuals', 'physical_jacobian', 'optimizer_jacobian', 'iterations',
        'residual_evaluations', 'jacobian_evaluations', 'trial_failures', 'iteration_costs', 'iteration_seconds', 'initial_cost', 'final_cost')}
    raw['failures'] = [{'trial': f.trial, 'observation': targets[f.observation], 'status': f.status.name,
                       'message': f.message, 'jacobian': f.jacobian} for f in result.failures]
    raw['active_bounds'] = [IDS[i] for i in result.covariance.active_bounds]
    raw['observation_statuses'] = [item.name for item in result.statuses]
    save(name + '-fit.json', raw)
    if len(result.weighted_residuals) != 160 or not np.isfinite(result.weighted_residuals).all():
        raise RuntimeError(f'{name}: no complete final objective')
    if any(item != regression.ObservationStatus.Available for item in result.statuses):
        raise RuntimeError(f'{name}: unavailable observation')
    if elapsed == 1e-6:
        assert np.array_equal(result.physical, [v[i] for i in IDS]), 'evaluation changed k coordinates'
    final_mapping = changed(mapping, dict(zip(IDS, result.physical)))
    out = publish_evaluation(name, final_mapping, form, targets, result.weighted_residuals,
        time.perf_counter()-start, {'status': result.status, 'iterations': result.iterations,
        'message': result.message, 'trial_failures': result.trial_failures, 'states': 84,
        'branch_check': 'all native observation statuses Available; final compositions not returned by fit for an explicit branch comparison'})
    if len(result.optimizer_jacobian) == 800:
        J = np.asarray(result.optimizer_jacobian).reshape(160, 5) / SCALES
        save(name + '-jacobian.json', {'targets': targets, 'coordinates': IDS, 'weighted_physical_jacobian': J.tolist()})
    return out, final_mapping


def input_hashes():
    paths = [*FILES.values(), *PACKETS.values(), s.STATE_PACKET, s.CANONICAL_VLE,
             BUNDLE / 'composition-transfer/aronu-2011-untouched-vle-rows.txt',
             Path(s.__file__), Path(design.__file__), Path(design.refit.__file__), Path(design.probe.__file__),
             Path(compare.__file__), s.installed_wheel(),
             ROOT / 'data/reference/MEA/manifests/chemical_reaction_source_contract.json']
    save('input-hashes.json', {str(p): s.sha256(p) for p in paths})
    save('accepted-inputs.json', {'design_comments': [5902438283, 5902470668, 5902535041, 5902558744],
         'candidate_ids': QIDS, 'candidate_bounds': QBOUNDS, 'step_limits': [(b-a)/2 for a,b in QBOUNDS],
         'bounds_source': 'Figiel 2025 Model Parameters, Tables 2-3, p. 9411; engineering analog envelopes accepted in v2.2',
         'f_water': 1.5, 'epsilon_ion': 8., 'k_ids': IDS, 'k_bounds': [LOWER.tolist(), UPPER.tolist()],
         'finite_difference_relative_steps': [1e-4, 1e-5], 'retry_relative_steps': [1e-3, 1e-4],
         'agreement_relative': 1e-3, 'agreement_absolute': 1e-8, 'half_gap': 3.71, 'quarter_gap': 1.86})


def baselines():
    input_hashes()
    first = [fitted('baseline-00', MAPPINGS['00'], '00')[0], fitted('baseline-11', MAPPINGS['11'], '11')[0]]
    for form in ('00', '11'):
        out, _ = fitted('baseline-' + form + '-exact-k', MAPPINGS[form], form)
        reference = first[0 if form == '00' else 1]
        assert out['targets'] == reference['targets']
        assert np.max(np.abs(np.asarray(out['weighted_residuals']) - reference['weighted_residuals'])) < 1e-8
        first.append(out)
    save('first-four-timing.json', {'evaluations': [{k: r[k] for k in ('name', 'wall_s', 'cost')} for r in first],
         'mean_evaluation_s': np.mean([r['wall_s'] for r in first]), 'remaining_execution_s': DEADLINE-time.perf_counter()})
    print('FIRST FOUR TIMING', [(r['name'], r['wall_s']) for r in first], flush=True)


def equality_and_path():
    eq = evaluate('equality-01-at-00', changed(MAPPINGS['00'], {'model/electrolyte/c_dielectric': 1.}), '00')
    base = json.loads((HERE / 'baseline-00.json').read_text())
    delta = np.asarray(eq['weighted_residuals']) - base['weighted_residuals']
    save('equality-01-vs-00.json', {'max_abs_weighted_residual_difference': np.max(np.abs(delta)),
         'cost_difference': eq['cost']-base['cost'], 'tolerance': 1e-10, 'equal': bool(np.max(np.abs(delta)) < 1e-10)})
    assert np.max(np.abs(delta)) < 1e-10, 'suspected Engine defect: (0,1) != (0,0)'
    for c in (0., .25, .5, .75):
        evaluate(f'p1b-{c:g}', changed(MAPPINGS['11'], {QIDS[6]: c, QIDS[8]: c}))


if __name__ == '__main__':
    mode = sys.argv[1]
    status = 'complete'
    try:
        if mode == 'baselines': baselines()
        elif mode == 'branch-check':
            for form in ('11','00'):
                actual = state_evaluate('branch-baseline-'+form,MAPPINGS[form],form)
                base = json.loads((HERE/f'baseline-{form}.json').read_text())
                assert actual['targets']==base['targets']
                assert np.max(np.abs(np.asarray(actual['weighted_residuals'])-base['weighted_residuals'])) < 1e-8
        elif mode == 'p1b': equality_and_path()
        else: raise ValueError('mode not implemented: ' + mode)
    except BaseException as error:
        status = 'failed'
        save(mode + '-job-failure.json', {'exception': type(error).__name__, 'message': str(error)})
        raise
    finally:
        save('job-times.json', OLD_JOBS + [{'job': mode, 'wall_s': time.perf_counter()-STARTED,
             'status': status, 'script_sha256': s.sha256(Path(__file__)), 'argv': sys.argv}])
