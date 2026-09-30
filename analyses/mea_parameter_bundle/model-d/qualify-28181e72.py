import hashlib
import json
import math
import runpy
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
hashes = json.loads((HERE / 'recovery-28181e72-input-hashes.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
sys.argv = ['probe.py', 'fit', str(HERE / 'qualification-28181e72.json')]
probe = runpy.run_path(str(HERE.parent / 'results/runs/performance-audit-2026-09-29/probe.py'))
result, record = probe['result'], probe['out']
record.update({name: list(getattr(result, name)) for name in
               ('predictions', 'residuals', 'weighted_residuals', 'physical_jacobian', 'optimizer_jacobian', 'physical')})
record['target_identities'] = [name for name, _, _ in probe['rows']]
record['statuses'] = [str(status) for status in result.statuses]
family = next(f for f in probe['design'].probe.shared.parameter_mapping(probe['design'].probe.RECORD)['model_families'] if f['kind'] == 'electrolyte')
record['born'] = {key: family[key] for key in ('c_shell', 'c_dielectric')}
reference = json.loads((HERE.parent / 'results/runs/performance-audit-2026-09-29/initial-evaluation.json').read_text())
record['objective_difference'] = result.final_cost - reference['final_cost']
record['preserved_input_sha256'] = hashes
Path(sys.argv[2]).write_text(json.dumps(record, indent=2) + '\n')
assert (record['states'], record['targets']) == (84, 160)
for name, size in [('predictions', 160), ('residuals', 160), ('weighted_residuals', 160), ('physical_jacobian', 800), ('optimizer_jacobian', 800)]:
    assert len(record[name]) == size and all(math.isfinite(value) for value in record[name]), name
assert result.trial_failures == 0 and record['physical'] == probe['point']
assert record['born'] == {'c_shell': 0.0, 'c_dielectric': 0.0}
assert math.isclose(result.final_cost, reference['final_cost'], rel_tol=1e-8, abs_tol=0.0)
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
print('Qualified frozen point:', record['final_cost'], 'difference', record['objective_difference'], flush=True)
