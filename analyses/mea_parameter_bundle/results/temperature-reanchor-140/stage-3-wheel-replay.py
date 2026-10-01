"""Two authorized <=60 C reference replays; no fitting or high-T evaluation.

Run one record at a time using the isolated immutable-wheel environment,
OMP/OPENBLAS/MKL_NUM_THREADS=1 and timeout 1800: adopted | stage-2.
"""
import csv
import importlib.util
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[1]
sys.path[:0] = [str(BUNDLE / 'scripts'), str(BUNDLE.parents[1] / 'src')]
import shared_evaluation as s

s.ENGINE_WHEEL_SHA256 = '9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pa = load('phase_a', 'phase-a.py')
probe, compare = pa.probe, pa.compare
RAW = pa.RAW / 'stage-3-wheel-replay'
OUT = HERE / 'stage-3'


def replay(record):
    assert record in ('adopted', 'stage-2')
    OUT.mkdir(exist_ok=True)
    environment = pa.verify(RAW / '.venv')
    reference = HERE / 'replay-targets.csv'
    if record == 'stage-2':
        fit = load('low_temperature_fit', 'low-temperature-fit.py')
        fit.HERE = HERE / 'stage-2'
        fit.SOURCE = fit.HERE / 'restored-source-parameters.json'
        fit.source_context()
        probe.RECORD = fit.HERE / 'primary-parameters.json'
        reference = fit.HERE / 'slope-fixed-start-1-rescore-targets.csv'
    probe._BASE.clear()
    s.RUNS = RAW / record / 'cache'
    expected = {(r['identity'], r['target']): r for r in csv.DictReader(reference.open())}
    rows, checks = [], []
    clock = time.perf_counter()
    for result in probe.evaluate(states=pa.training()):
        check = result['check']
        assert result['T'] <= 333.15 and result['status'] == 'evaluated', result
        assert check['tolerance_met'] and not check['balance_errors'], check
        assert check['max_abs_stationarity'] <= 1e-10, check
        checks.append(check)
        for target, residual in zip(result['targets'], compare.residuals(result), strict=True):
            old = expected[(result['identity'], target['identity'])]
            prediction = compare.predicted(result, target)
            floor = 1e-12 if old['quantity'] == 'species' else 0.0
            allowed = 1e-8 * abs(float(old['predicted'])) + floor
            rows.append({'record': record, 'identity': result['identity'], 'target': target['identity'],
                'temperature_k': result['T'], 'quantity': old['quantity'], 'predicted': prediction,
                'reference_predicted': float(old['predicted']), 'difference': prediction - float(old['predicted']),
                'allowed_difference': allowed, 'cost': .5 * residual[2] ** 2,
                'reference_cost': float(old['cost'])})
        print(record, result['identity'], result['status'], round(result['wall_s'], 2), flush=True)
    assert len(checks) == 84 and len(rows) == len(expected) == 142
    costs = {q: math.fsum(r['cost'] for r in rows if q == 'total' or r['quantity'] == q)
             for q in ('pressure', 'species', 'total')}
    differences = {q: costs[q] - math.fsum(r['reference_cost'] for r in rows
                  if q == 'total' or r['quantity'] == q) for q in costs}
    passed = all(abs(d) <= 1e-8 for d in differences.values()) and all(
        abs(r['difference']) <= r['allowed_difference'] for r in rows)
    summary = {'record': record, 'environment': environment, 'states': len(checks), 'targets': len(rows),
        'costs': costs, 'cost_differences': differences, 'passed': passed,
        'maximum_prediction_tolerance_fraction': max(abs(r['difference']) / r['allowed_difference'] for r in rows),
        'maximum_stationarity': max(c['max_abs_stationarity'] for c in checks),
        'balance_errors': 0, 'requested_tolerance_met': True, 'wall_seconds': time.perf_counter() - clock,
        'parameter_sha256': s.sha256(probe.RECORD), 'reference_rows_sha256': s.sha256(reference),
        'state_packet_sha256': s.sha256(s.STATE_PACKET), 'script_sha256': s.sha256(Path(__file__))}
    pa.table(OUT / f'{record}-wheel-replay.csv', rows)
    pa.save(OUT / f'{record}-wheel-replay.json', summary)
    print(summary, flush=True)
    assert passed, 'wheel replay tolerance failed; return to diagnosis'


if __name__ == '__main__':
    replay(sys.argv[1])
