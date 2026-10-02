"""Issue 154: input binding and full-CPU dispatch to the named fit owners."""
import concurrent.futures
import csv
import importlib.util
import json
import multiprocessing
import os
from pathlib import Path
import signal
import sys
import time

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
os.environ['FINAL_RERUN'] = '1'
BUNDLE = Path(__file__).resolve().parents[1]
OUT = BUNDLE / 'results/final-rerun'
OWNER = BUNDLE / 'model-d/born-form-diagnosis'
sys.path[:0] = [str(OWNER), str(BUNDLE / 'scripts'), str(BUNDLE.parents[1] / 'src')]
import shared_evaluation as s


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def timeout(signum, frame):
    raise TimeoutError('existing per-fit 2400 s timeout')


def worker(problem, start):
    clock = time.perf_counter()
    name = f'{problem}-{start}'
    directory = OUT / name
    directory.mkdir(exist_ok=problem == 'F6')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(2400)
    os.environ['SENSITIVITY_OUTPUT'] = str(directory)
    os.environ['FINAL_NAME'] = name
    os.environ['FINAL_POOL'] = '1' if problem in ('F4', 'F5') else '0'
    original_stdout, original_stderr = sys.stdout, sys.stderr
    with (directory / 'execution.log').open('w') as log:
        sys.stdout = sys.stderr = log
        try:
            s.verify_wheel()
            if problem == 'F6':
                low = module('low', BUNDLE / 'results/temperature-reanchor-140/low-temperature-fit.py')
                low.NATIVE_INPUTS = low.HERE / 'native-reaction-inputs.json'
                low.HERE = directory
                low.RAW = directory / 'runs'
                low.TRAINING = OUT / 'f6-input/training-inputs.json'
                low.fit('slope-fixed', '1' if start == 'A' else '2')
                fit = json.loads(next(directory.glob('*-fit.json')).read_text())
                complete = fit['native_complete']
            else:
                p5 = module('p5', OWNER / 'p5conv-fit.py')
                d = p5.d
                primary = BUNDLE / 'results/selected-current-best-parameters.json'
                original = OWNER / 'p5conv-a-00-diagnostic-parameters.json'
                off = BUNDLE / 'model-d/sensitivity-current/ablation-off-11-diagnostic-parameters.json'
                paths = {'F1': (primary, original), 'F2': (original, primary),
                         'F3': (off, primary), 'F4': (primary, original), 'F5': (original, primary)}
                form = '00' if problem in ('F2', 'F5') else '11'
                os.environ['SENSITIVITY_MAPPING'] = str(original if form == '00' else primary)
                d.FILES[form] = paths[problem][start == 'B']
                p5.main('off' if problem == 'F3' else 'refit', form)
                fit = json.loads((directory / f'{name}-results.json').read_text())
                complete = fit['converged']
            result = dict(name=name, complete=complete, wall_s=time.perf_counter()-clock,
                          diagnostic=None, timeout_s=2400)
        except Exception as exc:
            result = dict(name=name, complete=False, wall_s=time.perf_counter()-clock,
                          diagnostic=f'{type(exc).__name__}: {exc}', timeout_s=2400)
        finally:
            signal.alarm(0)
            sys.stdout, sys.stderr = original_stdout, original_stderr
    s.write_json(directory / 'execution.json', result)
    return result


def main():
    s.verify_wheel()
    f6_only = sys.argv[1:] == ['f6']
    OUT.mkdir(parents=True, exist_ok=True)
    corrected = BUNDLE / 'results/source-corrections-152'
    selected = {(r['identity'], r['target']) for r in csv.DictReader(
        (corrected / 'accepted-wave/strict141-targets.csv').open())}
    observations = s.load_state_packet(corrected / 'state-packet.json.gz')['observations']
    training = [{**o, 'targets': [t for t in o['targets'] if (o['identity'], t['identity']) in selected]}
                for o in observations if any((o['identity'], t['identity']) in selected for t in o['targets'])]
    if f6_only:
        assessment = module('assessment', BUNDLE / 'results/temperature-reanchor-140/assessment.py')
        training = [{**o, 'request': assessment.feed_start(o['request'], s)} for o in training]
    input_root = OUT / 'f6-input' if f6_only else OUT
    s.write_json(input_root / 'training-inputs.json', training)
    paths = [input_root / 'training-inputs.json', BUNDLE / 'results/temperature-reanchor-140/restored-source-parameters.json',
             *[BUNDLE / 'calibration-misfit' / f'{name}.py' for name in ('refit', 'probe', 'compare')],
             Path(s.__file__)]
    s.write_json(input_root / 'input-hashes.json', {'hashes': {str(p.relative_to(BUNDLE.parents[1])): s.sha256(p) for p in paths}})
    clock = time.perf_counter()
    workers = len(os.sched_getaffinity(0))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,
            mp_context=multiprocessing.get_context('spawn')) as pool:
        futures = [pool.submit(worker, f'F{i}', start) for i in ([6] if f6_only else range(1, 7)) for start in ('A', 'B')]
        runs = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            runs.append(result)
            print(json.dumps(result), flush=True)
    s.write_json(OUT / ('f6-execution.json' if f6_only else 'execution.json'), dict(runs=runs, workers=workers,
        threads=1, wall_s=time.perf_counter()-clock, wheel_sha256=s.ENGINE_WHEEL_SHA256,
        installed_module=s.epcsaft.__file__, training_sha256=s.sha256(input_root / 'training-inputs.json')))


if __name__ == '__main__':
    main()
