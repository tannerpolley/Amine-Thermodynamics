"""Issue 175: reuse the retained heat campaign with 16 Engine workers."""
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import traceback

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
REFERENCE = OUT.parent / 'heat-final-170'
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e9b1aed5/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl')
SHA = 'e691b5a9a2fe41e9115d83c914c912a928ed671f1b82ea001c90e6edf8e3d97b'
WORKERS = 16
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def read(path):
    return json.loads(path.read_text())


def fit(problem, start):
    os.environ['FINAL_HEAT_160'] = '1'
    os.environ['FINAL_POOL'] = str(int(problem in ('F4', 'F5')))
    os.environ['SENSITIVITY_OUTPUT'] = str(OUT / f'{problem}-{start}')
    sys.path.insert(0, str(ROOT / 'analyses/mea_parameter_bundle/scripts'))
    import d1_density_cp_160 as d
    d.s.ENGINE_WHEEL_SHA256, d.s.ENGINE_COMMIT = SHA, 'e9b1aed5'
    import probe  # Verify the new pin before heat_160 loads its historical metadata.
    import heat_160
    d.OUT = OUT
    d.s.ENGINE_WHEEL_SHA256, d.s.ENGINE_COMMIT = SHA, 'e9b1aed5'
    d.s.verify_wheel()
    import epcsaft
    assert str(Path(epcsaft.__file__).resolve()).startswith(str(Path(sys.prefix).resolve()))
    controls_type, native_fit = d.regression.FitControls, d.regression.fit

    def controls(**kwargs):
        assert kwargs == dict(maximum_iterations=40, maximum_elapsed_time_seconds=2250.)
        return controls_type(**kwargs, workers=WORKERS)

    def timed_fit(*args, **kwargs):
        clock = time.monotonic()
        result = native_fit(*args, **kwargs)
        write(OUT / f'{problem}-{start}' / 'fit-execution.json', dict(
            wall_s=time.monotonic()-clock, workers=WORKERS, maximum_iterations=40,
            maximum_elapsed_time_seconds=2250., residuals=d.s._jsonable(result.residuals)))
        return result

    d.regression.FitControls = controls
    d.regression.fit = timed_fit
    d.fit_worker(problem, start)
    actual = read(OUT / f'{problem}-{start}' / 'native-fit.json')
    expected = read(REFERENCE / f'{problem}-{start}' / 'native-fit.json')
    assert actual['targets'] == expected['targets'] and actual['observed'] == expected['observed']
    assert actual['start'] == expected['start'] and actual['coordinates'] == expected['coordinates']
    assert read(OUT / f'{problem}-{start}' / 'start-parameters.json') == read(REFERENCE / f'{problem}-{start}' / 'start-parameters.json')


def compare(problem, start, wall):
    name = f'{problem}-{start}'
    old, new = (read(p / name / 'native-fit.json') for p in (REFERENCE, OUT))
    fields = ['physical', 'initial_cost', 'final_cost', 'iteration_costs', 'weighted_residuals',
              'predictions', 'optimizer_jacobian', 'physical_jacobian']
    differences = []
    for field in fields:
        a, b = old[field], new[field]
        a, b = (a, b) if isinstance(a, list) else ([a], [b])
        if len(a) != len(b):
            differences.append(dict(field=field, old_length=len(a), new_length=len(b)))
        for i, (before, after) in enumerate(zip(a, b)):
            if struct.pack('!d', before) != struct.pack('!d', after):
                differences.append(dict(field=field, index=i, old=before, new=after,
                    old_hex=float(before).hex(), new_hex=float(after).hex(), delta=after-before))
    if 'residuals' in old:
        residuals = read(OUT / name / 'fit-execution.json')['residuals']
        for i, (before, after) in enumerate(zip(old['residuals'], residuals, strict=True)):
            if struct.pack('!d', before) != struct.pack('!d', after):
                differences.append(dict(field='residuals', index=i, old=before, new=after,
                    old_hex=float(before).hex(), new_hex=float(after).hex(), delta=after-before))
    write(OUT / name / 'differences.json', differences)
    # resources.txt records elapsed time for every retained command, including first-wave fits.
    resource_text = (REFERENCE / name / 'resources.txt').read_text()
    elapsed = next(line.split(': ', 1)[1] for line in resource_text.splitlines() if 'Elapsed (wall clock)' in line)
    old_wall = 0.
    for part in elapsed.split(':'):
        old_wall = old_wall * 60 + float(part)
    return dict(fit=problem, start=start, targets=len(new['targets']), wall_s=wall,
        fit_wall_s=read(OUT / name / 'fit-execution.json')['wall_s'], old_wall_s=old_wall,
        iterations=new['iterations'], cost=new['final_cost'],
        max_abs_delta_parameter=max(abs(a-b) for a,b in zip(old['physical'],new['physical'],strict=True)),
        max_relative_delta_cost=max(abs(a-b)/abs(a) if a else abs(b) for a,b in
            zip([old['initial_cost'],old['final_cost']],
                [new['initial_cost'],new['final_cost']],strict=True)),
        max_abs_delta_weighted_residual=max(abs(a-b) for a,b in zip(old['weighted_residuals'],new['weighted_residuals'],strict=True)),
        bitwise_equal='yes' if not differences else 'no', differing_values=len(differences))


def campaign():
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
    started = time.monotonic()
    assert not (OUT / 'execution.json').exists(), 'Do not overwrite a retained campaign'
    runs, comparisons = [], []
    write(OUT / 'engine.json', dict(commit='e9b1aed5', wheel=str(WHEEL), wheel_sha256=SHA,
        workers=WORKERS, threads=1, python=sys.version,
        packages={p: importlib.metadata.version(p) for p in ('numpy','scipy','matplotlib','pandas','epcsaft')}))
    for problem in [f'F{i}' for i in range(1,7)]:
        for start in ('A','B'):
            name = f'{problem}-{start}'
            directory = OUT / name
            directory.mkdir(exist_ok=False)
            clock = time.monotonic()
            command = [sys.executable, str(Path(__file__).resolve()), 'fit', problem, start]
            print('START', name, flush=True)
            with (directory / 'execution.txt').open('w') as log:
                code = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
            wall = time.monotonic()-clock
            run = dict(name=name, command=command, returncode=code, wall_s=wall)
            runs.append(run)
            if code == 0:
                comparisons.append(compare(problem,start,wall))
                print('COMPLETE', name, comparisons[-1], flush=True)
            else:
                print('FAILED', name, (directory / 'execution.txt').read_text()[-4000:], flush=True)
            write(OUT / 'execution.json', dict(wall_s=time.monotonic()-started, runs=runs, workers=WORKERS, threads=1))
            if comparisons:
                with (OUT / 'comparison.csv').open('w',newline='') as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(comparisons[0]), lineterminator="\n")
                    writer.writeheader(); writer.writerows(comparisons)


if __name__ == '__main__':
    if sys.argv[1:2] == ['fit']:
        worker_started = time.monotonic()
        try:
            fit(*sys.argv[2:])
        except Exception:
            write(OUT / f'{sys.argv[2]}-{sys.argv[3]}' / 'exception.json', dict(traceback=traceback.format_exc()))
            raise
        finally:
            write(OUT / f'{sys.argv[2]}-{sys.argv[3]}' / 'worker-execution.json', dict(wall_s=time.monotonic()-worker_started))
    else:
        campaign()
