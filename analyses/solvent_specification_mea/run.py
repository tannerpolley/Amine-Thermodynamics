"""Fresh endpoint replay from the materialized packet; no historical imports."""
import hashlib
import importlib.metadata
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import epcsaft
from MEA.solvent_specification import SolventSpecification

AN = Path(__file__).resolve().parent
started = time.perf_counter()
def write(name, value):
    (AN/'results'/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
wheel = AN.parents[1]/'build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl'
assert hashlib.sha256(wheel.read_bytes()).hexdigest() == '0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804'
with zipfile.ZipFile(wheel) as archive:
    for name in archive.namelist():
        if name.startswith('epcsaft/') and not name.endswith('/'):
            assert archive.read(name) == (Path(epcsaft.__file__).parent.parent/name).read_bytes(), name
spec = SolventSpecification(AN/'MEA.toml')
reference = json.loads((AN/'inputs/reference.json').read_text())
records, differences = [], []
fields = ('predicted','residual','weighted_residual','cost')
for row, ref in zip(spec.inputs['observations']['fitted'],reference,strict=True):
    assert row['identity'] == ref['target']
    result = spec.prediction(row)
    if result['status'] == 'Available':
        result.update(predicted=result['value'],weighted_residual=math.sqrt(row['weight'])*result['residual'])
        result['cost'] = .5*result['weighted_residual']**2
    records.append(result)
    differences.append(dict(target=row['identity'],relative={k:abs(result[k]-ref[k])/max(abs(result[k]),abs(ref[k])) if k in result and result[k] is not None else None for k in fields},available=result['status']=='Available',tolerance_met=result['requested_tolerance_met']))
write('predictions.json',records)
passed = [d for d in differences if d['available'] and d['tolerance_met'] and all(v is not None and v<=1e-10 for v in d['relative'].values())]
groups = {}
for group in ('common149','restored species','Jakobsen','loaded density','Cp'):
    actual = math.fsum(r['cost'] for r in records if r['group']==group) if len(passed)==213 else None
    expected = math.fsum(r['cost'] for r,q in zip(reference,records,strict=True) if q['group']==group)
    groups[group] = dict(actual=actual,reference=expected,relative=None if actual is None else abs(actual-expected)/max(abs(actual),abs(expected)))
cost = math.fsum(r['cost'] for r in records) if len(passed)==213 else None
report = dict(rows=len(records),rows_within_tolerance=len(passed),subset_cost=cost,subset_reference=45.37796168239049,groups=groups,differences=differences,first_differing_target=next((d['target'] for d in differences if d not in passed),None),maximum_relative_difference={k:max((d['relative'][k] for d in differences if d['relative'][k] is not None),default=None) for k in fields})
write('endpoint-checks.json',report)
write('runtime.json',dict(wheel=str(wheel),wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),installed_files_byte_identical=True,python=sys.version,packages={k:importlib.metadata.version(k) for k in ('epcsaft','numpy','scipy')},workers=1,numerical_threads=1,wall_seconds=time.perf_counter()-started,files={str(p.relative_to(AN)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [AN/'MEA.toml',AN/'declarations.toml',*sorted((AN/'inputs').iterdir())]},historical_modules_loaded=[k for k in ('fit_observations','fit_campaign','shared_evaluation') if k in sys.modules]))
assert len(passed)==213 and abs(cost/45.37796168239049-1)<=1e-10 and all(g['relative']<=1e-10 for g in groups.values()), report
print(cost,report['maximum_relative_difference'])
