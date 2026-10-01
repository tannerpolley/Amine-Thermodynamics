"""Issue 147 ordered wheel qualification; no fits or corrected targets.

Use the isolated results/runs/temperature-heat-147/.venv via uv --no-project.
R1 external cap 1800 s; single-threaded workers, full CPU affinity pool.
"""
import csv
import importlib.metadata as metadata
import importlib.util
import json
import math
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[1]
ROOT = BUNDLE.parents[1]
RAW = BUNDLE / 'results/runs/temperature-heat-147'
OLD = HERE.with_name('temperature-reanchor-140')
CLONE = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-build-717a2990')
WHEEL = next((CLONE / 'build/environment-wheel').glob('epcsaft-*.whl'))
sys.path[:0] = [str(BUNDLE / 'scripts'), str(ROOT / 'src')]
import shared_evaluation as s

s.ENGINE_WHEEL_SHA256 = '9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4'
s.ENGINE_COMMIT = '717a2990e443423e051fc0569f25209d04007543'
s.verify_wheel()
for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    assert os.environ[variable] == '1'
spec = importlib.util.spec_from_file_location('phase_a_140', OLD / 'phase-a.py')
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)
probe, compare = pa.probe, pa.compare


def freeze():
    distribution = metadata.distribution('epcsaft')
    files = {str(p): s.sha256(Path(distribution.locate_file(p)))
             for p in distribution.files if Path(distribution.locate_file(p)).is_file()
             and '__pycache__' not in str(p)}
    pa.save(HERE / 'wheel-identity.json', {
        'source_commit': s.ENGINE_COMMIT, 'clone': str(CLONE),
        'wheel': str(WHEEL), 'wheel_sha256': s.sha256(WHEEL),
        'wheel_fingerprint': (CLONE / 'build/environment-wheel/build.sha256').read_text().strip(),
        'preparation': json.loads((CLONE / 'build/environment-wheel/preparation.json').read_text()),
        'build_origin': 'Engine own setup/build script restored fingerprint-matched shared cache',
        'build_jobs': len(os.sched_getaffinity(0)), 'CPU_affinity': sorted(os.sched_getaffinity(0)),
        'toolchain_fingerprint': (CLONE / 'build/environment-wheel/meson-build-dir').read_text().strip().rsplit('-', 1)[1],
        'module_origin': probe.epcsaft.__file__, 'python': sys.version,
        'installed_file_sha256': files,
        'direct_url': json.loads(distribution.read_text('direct_url.json')),
        'input_hashes': {str(p.relative_to(ROOT)): s.sha256(p) for p in
            [probe.RECORD, s.STATE_PACKET, OLD / 'training-targets.csv', OLD / 'replay-targets.csv',
             HERE / 'inputs.json', HERE / 'source-laws.json', HERE / 'source-law-admission.json']},
        'identity_check': 'Engine verify-installed-wheel.py: all 14 wheel RECORD hashes match; metadata unmodified',
    })


def replay_one(observation):
    s.RUNS = RAW / 'R1' / observation['identity']
    assert not s.RUNS.exists(), 'separate empty replay cache required'
    mapping = s.parameter_mapping(probe.RECORD)
    model = probe.epcsaft.Mixture(probe.epcsaft.Parameters.from_mapping(mapping))
    clock = time.perf_counter()
    rec = s.evaluate_state(model, observation['request'], probe.reactions(), observation['identity'], [],
                           budget_s=180, limits=s.EvaluationLimits(180, 180),
                           model_fingerprint=s.parameter_fingerprint(mapping))
    liquid = next((p for p in rec.get('phases', []) if p['role'] == 'liquid'), None)
    return {**rec, 'T': observation['request']['temperature']['value'], 'targets': observation['targets'],
            'liquid': liquid, 'check': probe.check(rec), 'elapsed_s': time.perf_counter() - clock,
            'module_origin': probe.epcsaft.__file__, 'worker_pid': os.getpid()}


def replay():
    freeze()
    assert s.sha256(OLD / 'training-targets.csv') == '8a9426d253b23a5dce5db9e5fa71493136a843f40d919f694021815d5b8ea36b'
    expected = {(r['identity'], r['target']): r for r in csv.DictReader((OLD / 'replay-targets.csv').open())}
    clock = time.perf_counter()
    records, rows = [], []
    with mp.get_context('fork').Pool(len(os.sched_getaffinity(0))) as pool:
        for rec in pool.imap(replay_one, pa.training()):
            records.append(rec)
            pa.save(HERE / 'old-replay-states.json', records)
            check = rec['check']
            assert rec['status'] == 'evaluated' and check['tolerance_met'] and not check['balance_errors'], rec
            assert check['max_abs_stationarity'] <= 1e-10, check
            for target, residual in zip(rec['targets'], compare.residuals(rec), strict=True):
                old = expected[(rec['identity'], target['identity'])]
                value = compare.predicted(rec, target)
                allowance = 1e-8 * abs(float(old['predicted'])) + (1e-12 if old['quantity'] == 'species' else 0)
                rows.append({'identity': rec['identity'], 'target': target['identity'], 'quantity': old['quantity'],
                             'predicted': value, 'reference': float(old['predicted']),
                             'difference': value - float(old['predicted']), 'allowance': allowance,
                             'cost': .5 * residual[2] ** 2, 'reference_cost': float(old['cost'])})
            pa.table(HERE / 'old-replay-targets.csv', rows)
    costs = {q: math.fsum(r['cost'] for r in rows if q == 'total' or r['quantity'] == q)
             for q in ('pressure', 'species', 'total')}
    reference = dict(zip(costs, (8.14345313051485, 24.848444130706277, 32.991897261221126)))
    passed = len(records) == 84 and len(rows) == 142 and all(abs(costs[q] - reference[q]) <= 1e-8 for q in costs)
    passed = passed and all(abs(r['difference']) <= r['allowance'] for r in rows)
    pa.save(HERE / 'old-replay.json', {'passed': passed, 'costs': costs, 'reference_costs': reference,
        'cost_differences': {q: costs[q] - reference[q] for q in costs}, 'states': len(records), 'targets': len(rows),
        'maximum_prediction_tolerance_fraction': max(abs(r['difference']) / r['allowance'] for r in rows),
        'maximum_stationarity': max(r['check']['max_abs_stationarity'] for r in records),
        'wall_s': time.perf_counter() - clock, 'summed_worker_s': sum(r['elapsed_s'] for r in records),
        'pool_size': len(os.sched_getaffinity(0)), 'module_origin': probe.epcsaft.__file__,
        'producer_sha256': s.sha256(Path(__file__))})
    assert passed, 'OLD replay failed; stop without resetting the benchmark'


def campaign():
    from epcsaft import equilibrium as eq
    import verify_reference_calorics as thermal
    mapping = s.parameter_mapping(OLD / 'restored-source-parameters.json')
    params = probe.epcsaft.Parameters.from_mapping(mapping)
    records = json.loads((OLD / 'stage-3/native-reaction-inputs.json').read_text())
    laws = json.loads((HERE / 'source-laws.json').read_text())
    for index, key in ((1, 'R2_reused'), (3, 'R4'), (4, 'R5')):
        law, correlation = laws[key], records[index]['engine_correlation']
        correlation.update(a=law['a_native'], b=law['B_K'], c=law['C'], d=law['D_per_K'])
    request = pa.training()[0]['request']
    request['reaction_system']['engine_reactions'] = records
    reactions = [eq.Reaction(dict(zip(s.COMPONENT_IDS, r['stoichiometry'], strict=True)), name=r['reaction_id'],
                 correlation=s._reaction_correlation(r, r['reaction_id']),
                 reference=s._reaction_reference(r, r['reaction_id'])) for r in records]
    return mapping, params, records, request, reactions, thermal


def mapping_check():
    from epcsaft import equilibrium as eq, regression as reg
    mapping, params, records, request, reactions, thermal = campaign()
    laws = json.loads((HERE / 'source-laws.json').read_text())
    assert all(laws[k]['passed'] for k in ('R2_reused', 'R4', 'R5'))
    pa.save(HERE / 'campaign-reactions.json', records)
    rows = []
    model = probe.epcsaft.Mixture(params)
    for index, key in ((1, 'R2_reused'), (3, 'R4'), (4, 'R5')):
        law, native = laws[key], records[index]['engine_correlation']
        A = law['A_stored'] if index == 1 else law['A']
        assert abs(native['a'] - (A + law['C'] * math.log(313.15))) < 5e-13
        for T in (293.15, 313.15, 333.15, 353.15):
            request['temperature']['value'] = T
            problem = s._problem_from_request(request)
            item = reg.Observation()
            item.kind, item.reaction = reg.ObservationKind.LogEquilibriumConstant, records[index]['reaction_id']
            item.problem, item.form, item.scale = problem._native(params), reg.ResidualForm.Difference, 1.0
            prediction = reg.predict(model, item)
            document = A + law['B_K'] / T + law['C'] * math.log(T) + law['D_per_K'] * T
            derivative = s.epcsaft.GAS_CONSTANT_J_PER_MOL_K * (-law['B_K'] + law['C'] * T + law['D_per_K'] * T*T)
            native_derivative = s.epcsaft.GAS_CONSTANT_J_PER_MOL_K * (-native['b'] + native['c'] * T + native['d'] * T*T)
            rows.append({'reaction': item.reaction, 'T_K': T, 'status': prediction.status.name,
                         'document_lnK': document, 'native_lnK': prediction.value,
                         'delta_lnK': prediction.value - document, 'document_RT2_derivative_J_mol': derivative,
                         'native_polynomial_RT2_derivative_J_mol': native_derivative,
                         'reference_pressure_pa': problem.reactions[index].reference.reference_pressure_pa,
                         'module_origin': probe.epcsaft.__file__})
            pa.table(HERE / 'native-law-mapping.csv', rows)
            assert prediction.status.name == 'Available' and abs(prediction.value - document) < 5e-13
            assert derivative == native_derivative
    pa.save(HERE / 'native-law-mapping.json', {'passed': True, 'rows': len(rows),
        'max_abs_delta_lnK': max(abs(r['delta_lnK']) for r in rows),
        'RT2_derivative_check': 'stored versus native polynomial coefficients; Engine thermochemistry.cpp:221-229 inspected',
        'source_representation_checks': 'phase-A frozen admission grid and continuation errors retained unchanged',
        'producer_sha256': s.sha256(Path(__file__)), 'module_origin': probe.epcsaft.__file__})


if __name__ == '__main__':
    try:
        {'freeze': freeze, 'R1': replay, 'Q1-mapping': mapping_check}[sys.argv[1]]()
    except Exception as exc:
        pa.save(HERE / 'qualification-failure.json', {'job': sys.argv[1], 'exception': type(exc).__name__,
            'message': str(exc), 'module_origin': probe.epcsaft.__file__, 'producer_sha256': s.sha256(Path(__file__))})
        raise
