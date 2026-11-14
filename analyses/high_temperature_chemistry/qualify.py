"""Qualify the owner-authorized Engine wheel against the unchanged 307 MEA rows."""
import hashlib
import json
import math
import os
from pathlib import Path
import time
import zipfile

import epcsaft
from epcsaft import regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable

AN = Path(__file__).resolve().parent
ROOT = AN.parents[1]
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')
SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'


def main():
    started = time.perf_counter()
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
    with zipfile.ZipFile(WHEEL) as archive:
        for name in archive.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert archive.read(name) == (Path(epcsaft.__file__).parent.parent / name).read_bytes(), name
    source = ROOT / 'analyses/mea_parameter_bundle/results/adoption-340/historical-spec'
    spec = SolventSpecification(source / 'MEA.toml')
    rows = spec.inputs['observations']['fitted']
    reference = json.loads((source / 'inputs/reference.json').read_text())
    predictions, differences = [], []
    for row, ref in zip(rows, reference, strict=True):
        assert row['identity'] == ref['target']
        prediction = spec.prediction(row)
        if prediction['status'] == 'Available' and prediction['requested_tolerance_met']:
            weighted = math.sqrt(row['weight']) * prediction['residual']
            fields = dict(predicted=prediction['value'], residual=prediction['residual'],
                          weighted_residual=weighted, cost=.5 * weighted**2)
            errors = {k: abs(v - ref[k]) / max(abs(ref[k]), 1.) for k, v in fields.items()}
        else:
            errors = None
        predictions.append(prediction)
        differences.append(dict(target=row['identity'], errors=errors))
        print(row['identity'], prediction['status'], flush=True)
    pair_checks = []
    for identity in {r['state_identity'] for r in rows if r['group'] == 'Cai'}:
        pair = [(r, p) for r, p in zip(rows, predictions, strict=True) if r['state_identity'] == identity]
        temperature = next(p for r, p in pair if r['kind'] == 'temperature')
        pair_checks.append(dict(identity=identity, passed=len(pair) == 2 and all(
            p['status'] == 'Available' and p['requested_tolerance_met'] for r, p in pair)
            and pair[0][0]['temperature_domain'][0] <= temperature.get('value', math.nan) <= pair[0][0]['temperature_domain'][1]))
    coordinates = [reg.reaction_enthalpy_shift(name, pivot_temperature=313.15, origin=0.,
                   scale=2500., bounds=(-10000., 10000.)) for name in ('R4', 'R5')]
    chart = reg.CoordinateSet()
    chart.coordinates = coordinates
    admission = {}
    try:
        start = list(chart.start(spec.parameters._native, [spec.observation(r) for r in rows], spec.thermal))
        admission = dict(start=start, passed=len(start) == 2 and max(map(abs, start)) <= 1e-12)
    except Exception as error:
        admission = dict(passed=False, exception=type(error).__name__, message=str(error))
    report = dict(wheel_sha256=SHA, wheel=str(WHEEL), installed_files_byte_identical=True,
                  baseline_rows=len(rows), predictions=predictions, differences=differences,
                  metric='abs(actual-reference)/max(abs(reference),1)', limit=1e-10,
                  near_zero_absolute_tolerance=1e-10, paired_checks=pair_checks, coordinate_admission=admission,
                  input_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [source / 'MEA.toml', source / 'declarations.toml', *sorted((source / 'inputs').iterdir())]},
                  law_domains={k: {r['name']: [r['correlation']['temperature_min'], r['correlation']['temperature_max']]
                                  for r in group} for k, group in spec.spec['chemistry']['reactions'].items()},
                  wall_seconds=time.perf_counter() - started, cpu_count=os.cpu_count())
    report['maximum_error'] = max((max(d['errors'].values()) for d in differences if d['errors']), default=None)
    report['passed'] = (len(rows) == 307 and all(d['errors'] and max(d['errors'].values()) <= 1e-10 for d in differences)
                        and all(p['passed'] for p in pair_checks) and admission['passed'])
    (AN / 'results').mkdir(exist_ok=True)
    (AN / 'results/qualification.json').write_text(json.dumps(jsonable(report), indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: report[k] for k in ('passed', 'maximum_error', 'coordinate_admission', 'wall_seconds')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
