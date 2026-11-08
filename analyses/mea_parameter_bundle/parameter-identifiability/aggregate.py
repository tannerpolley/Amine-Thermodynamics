"""Reduce the retained issue-262 fits; no model evaluations."""
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np

AN = Path(__file__).resolve().parent
SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
read = lambda p: json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
tasks = read(AN/'inputs/tasks.json')['tasks']
summaries = [read(AN/'results'/t['identity']/'summary.json') for t in tasks]
assert len(summaries) == 356 and all(s['wheel_sha256'] == SHA for s in summaries)
coords = read(AN/'inputs/coordinates.json')
profiles = [s for s in summaries if s['task']['kind'] == 'profile']
bootstrap = [s for s in summaries if s['task']['kind'] == 'bootstrap']
good = [s for s in bootstrap if s['inference_available'] and not s.get('cause')]
lower = [s['task']['identity'] for s in profiles if s.get('lower_reference')]


def spread(values):
    a = np.asarray(values, dtype=float)
    return dict(count=len(a), percentiles=None if not len(a) else np.percentile(a, [2.5, 50, 97.5], axis=0).tolist())


parameters = spread([s['coordinates'] for s in good])
parameters['first100'] = spread([s['coordinates'] for s in good if int(s['task']['identity'][-3:]) < 100])
parameters['quantile_change'] = None if not parameters['count'] or not parameters['first100']['count'] else (np.array(parameters['percentiles'])-parameters['first100']['percentiles']).tolist()
classification = []
for q in coords:
    points = sorted([s for s in profiles if s['task']['coordinate'] == q['original_index']], key=lambda s:s['task']['node'])
    origin = next(i for i, s in enumerate(points) if s['task']['node'] == q['origin'])
    sides = []
    for cutoff in (3.84, 3.929176131182156):
        brackets = []
        for sequence in (points[:origin][::-1], points[origin+1:]):
            previous, crossing, unresolved = points[origin], None, not points[origin]['inference_available']
            for s in sequence:
                if unresolved or not s['inference_available']:
                    unresolved = True
                    break
                if s['twice_delta_cost'] > cutoff:
                    crossing = sorted([previous['task']['node'], s['task']['node']])
                    break
                previous = s
            brackets.append(dict(crossing_bracket=crossing, unresolved=unresolved))
        sides.append(dict(cutoff_on_twice_delta_cost=cutoff, sides=brackets, likelihood_interpretation_available=not lower))
    brackets = sides[0]['sides']
    shape = 'two-sided cost restriction in finite scan' if all(s['crossing_bracket'] for s in brackets) else 'numerically unresolved comparison' if any(s['unresolved'] for s in brackets) else 'one-sided cost restriction in finite scan' if any(s['crossing_bracket'] for s in brackets) else 'no cutoff crossing in tested range'
    label = 'reference reconciliation required' if lower else shape
    attained = [s['twice_delta_cost'] for s in points if s['inference_available']]
    phase_reports = [read(AN/'results'/s['task']['identity']/'phase-summary.json') for s in points if s.get('phase')]
    phase_counts = dict(endpoints=len(phase_reports), states=sum(p['states'] for p in phase_reports),
                        trials=sum(r['trials'] for p in phase_reports for r in p['reductions']),
                        detected_descent_states=sum(p['descent_states'] for p in phase_reports), incomplete_states=sum(p['incomplete_states'] for p in phase_reports))
    classification.append(dict(identity=q['identity'], unit=q['units'], classification=label, conditional_scan_shape=shape, sides=sides,
                               attained_twice_delta_cost_range=[min(attained), max(attained)] if attained else None,
                               phase_counts=phase_counts,
                               converged=sum(s['inference_available'] for s in points), attempted=len(points)))

metrics, curves, curve_failures = {}, {}, {}
curves = {(i, q, u): [] for i, s in enumerate(read(AN/'inputs/curve-states.json')) for q, u in s['quantities']}
for s in good:
    directory = AN/'results'/s['task']['identity']
    rows = read(directory/'replay.json.gz')['rows']
    groups = {'reported pressure': [r for r in rows if r['row'].get('quantity') == 'PartialPressure'],
              'reported species': [r for r in rows if r['row'].get('quantity') == 'PhaseMoleFraction']}
    blocks = read(AN/'inputs/blocks.json')
    for r, b in zip(rows, blocks, strict=True):
        groups.setdefault(b['source']+' / '+r['row'].get('quantity', 'unknown'), []).append(r)
    for key, part in groups.items():
        observed = [r for r in part if r['observed'] != 0]
        if len(observed) == len(part):
            metrics.setdefault(key, []).append((s['task']['identity'], 100*np.mean([abs(r['value']/r['observed']-1) for r in part]), len(part)))
    path = directory/'curves.json.gz'
    if path.exists():
        for r in read(path)['rows']:
            if r['status'] == 'available' and isinstance(r['value'], (int, float)) and np.isfinite(r['value']):
                curves.setdefault((r['state_index'], r['quantity'], r['unit']), []).append((s['task']['identity'], r['value']))
            else:
                cause = r.get('cause') or 'nonfinite prediction'
                curve_failures[cause] = curve_failures.get(cause, 0)+1
metric_summary = {k:dict(spread([v for _, v, _ in values]), observations=values[0][2], unit='percent',
                       draws=[dict(identity=i, AARD_percent=v) for i, v, _ in values],
                       first100=spread([v for i, v, _ in values if int(i[-3:]) < 100])) for k, values in metrics.items()}
curve_summary = [dict(state_index=i, quantity=q, unit=u, **spread([v for _, v in values]),
                      first100=spread([v for d, v in values if int(d[-3:]) < 100])) for (i, q, u), values in sorted(curves.items())]
result = dict(wheel_sha256=SHA, attempted_profiles=len(profiles), attempted_bootstrap=len(bootstrap),
              bootstrap_eligibility='Provisional complete-case alternative: converged, admissible, matching replay and all 307 predictions available; owner choice pending',
              usable_bootstrap=len(good), lower_reference_profiles=lower, classifications=classification,
              parameters=parameters, AARD=metric_summary, curves=curve_summary, unavailable_curve_quantities_by_cause=curve_failures,
              failures=[dict(identity=s['task']['identity'], status=s.get('status'), cause=s.get('cause')) for s in summaries if not s['inference_available']])
(AN/'results/study.json.tmp').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
(AN/'results/study.json.tmp').replace(AN/'results/study.json')
paths = [p for directory in ('inputs', 'results') for p in (AN/directory).rglob('*') if p.is_file() and p.name != 'result-hashes.json']
(AN/'results/result-hashes.json').write_text(json.dumps({str(p.relative_to(AN)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('attempted_profiles', 'attempted_bootstrap', 'usable_bootstrap', 'lower_reference_profiles')}))
