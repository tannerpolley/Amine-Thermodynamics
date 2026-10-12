"""Compare all retained numerical outputs, including post-fit gate failures."""
import csv
import hashlib
from pathlib import Path
import run

rows = []
executions = {r['name']: r for r in run.read(run.OUT / 'execution.json')['runs']}
for problem in [f'F{i}' for i in range(1, 7)]:
    for start in ('A', 'B'):
        name = f'{problem}-{start}'
        directory = run.OUT / name
        path = directory / 'native-fit.json'
        if not path.exists():
            raw = run.read(directory / 'runs' / name / f'{name}-fit.json')
            assert raw['status'] == 'converged'
            run.write(path, raw)
            run.write(directory / 'parameters.json', run.read(directory / f'{name}-diagnostic-parameters.json'))
        new, old = run.read(path), run.read(run.REFERENCE / name / 'native-fit.json')
        assert new['targets'] == old['targets'] and new['start'] == old['start']
        assert new['coordinates'] == old['coordinates']
        assert run.read(directory / 'start-parameters.json') == run.read(run.REFERENCE / name / 'start-parameters.json')
        assert len(new['targets']) == (167 if problem in ('F4', 'F5') else 149)
        assert all(x == 'Available' for x in new['observation_statuses'])
        wall = executions[name]['wall_s'] if name in executions else run.read(directory / 'worker-execution.json')['wall_s']
        row = run.compare(problem, start, wall)
        row.update(status=new['status'], returncode=executions[name]['returncode'] if name in executions else 0,
            final_cost_delta=new['final_cost']-old['final_cost'],
            final_cost_relative_delta=abs(new['final_cost']/old['final_cost']-1),
            old_iterations=old['iterations'], post_fit_gate_failed=(directory / 'exception.json').exists())
        rows.append(row)
with (run.OUT / 'comparison.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
run.write(run.OUT / 'summary.json', dict(fits=len(rows), converged=sum(r['status']=='converged' for r in rows),
    bitwise_equal=sum(r['bitwise_equal']=='yes' for r in rows),
    sum_fit_command_wall_s=sum(r['wall_s'] for r in rows), sum_native_fit_wall_s=sum(r['fit_wall_s'] for r in rows),
    max_abs_delta_parameter=max(r['max_abs_delta_parameter'] for r in rows),
    max_final_cost_relative_delta=max(r['final_cost_relative_delta'] for r in rows),
    max_abs_delta_weighted_residual=max(r['max_abs_delta_weighted_residual'] for r in rows),
    post_fit_gate_failures=[r['fit']+'-'+r['start'] for r in rows if r['post_fit_gate_failed']],
    peak_memory_measured=False))
run.write(run.OUT / 'file-hashes.json', {str(p.relative_to(run.OUT)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(run.OUT.rglob('*')) if p.is_file() and p.name != 'file-hashes.json' and '__pycache__' not in p.parts})
print(rows)
