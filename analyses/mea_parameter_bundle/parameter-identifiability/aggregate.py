"""Reduce the retained issue-262 fits; no model evaluations."""
import csv
import gzip
import hashlib
import json
import math
import re
from pathlib import Path
import numpy as np

AN = Path(__file__).resolve().parent
EVIDENCE = AN.parent/'results/engine-3e83e19c-paper-evidence'
SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
read = lambda p: json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
tasks = read(AN/'inputs/tasks.json')['tasks']
summaries = [read(AN/'results'/t['identity']/'summary.json') for t in tasks]
assert len(summaries) == 356 and all(s['wheel_sha256'] == SHA for s in summaries)
coords = read(AN/'inputs/coordinates.json')
blocks = read(AN/'inputs/blocks.json')
profiles = [s for s in summaries if s['task']['kind'] == 'profile']
bootstrap = [s for s in summaries if s['task']['kind'] == 'bootstrap']
lower = [s['task']['identity'] for s in profiles if s.get('lower_reference')]
first100 = lambda identity: int(identity[-3:]) < 100


def spread(values):
    a = np.asarray(values, dtype=float)
    return dict(count=len(a), percentiles=None if not len(a) else np.percentile(a, [2.5, 50, 97.5], axis=0).tolist())


def eligibility(s):
    """Owner decision 2026-11-08: a converged draw is eligible when its sampled objective replays.

    Rows with zero multiplicity are outside that draw's objective; their availability does not enter eligibility.
    """
    directory = AN/'results'/s['task']['identity']
    m = s['task']['multiplicities']
    native = read(directory/'native-fit.json.gz')
    rows = read(directory/'replay.json.gz')['rows']
    included = [i for i, k in enumerate(m) if k]
    ok = lambda r: r['status'] == 'Available' and r.get('requested_tolerance_met') and math.isfinite(r['value']) and math.isfinite(r['residual'])
    weights = [r['row']['weight'] for r in rows]
    record = dict(identity=s['task']['identity'], status=native['status'], rows_available=sum(map(ok, rows)),
                  positive_multiplicity_unavailable=sum(not ok(rows[i]) for i in included),
                  zero_multiplicity_unavailable=sum(not ok(r) for r, k in zip(rows, m) if not k))
    if native['status'] != 'converged' or record['positive_multiplicity_unavailable']:
        return dict(record, eligible=False)
    w = [math.sqrt(weights[i]*m[i])*rows[i]['residual'] for i in included]
    cost = math.fsum(.5*x*x for x in w)
    completion = directory/'completion.json'
    extra = read(completion) if completion.exists() else s
    record.update(native_cost=native['final_cost'], replayed_sampled_cost=cost,
                  maximum_weighted_residual_difference=max(abs(a-b) for a, b in zip(w, native['weighted_residuals'], strict=True)),
                  interaction_admissible=extra.get('interaction_admissible'), coordinates=extra.get('coordinates'))
    record['eligible'] = bool(abs(cost-native['final_cost']) <= 1e-8*abs(cost) and record['maximum_weighted_residual_difference'] <= 1e-8
                              and record['interaction_admissible'] and record['coordinates'])
    return record


draws = [eligibility(s) for s in bootstrap]
primary = [d for d in draws if d['eligible']]
complete_case = [d for d in primary if d['rows_available'] == 307]


def parameter_summary(selected):
    result = spread([d['coordinates'] for d in selected])
    result['first100'] = spread([d['coordinates'] for d in selected if first100(d['identity'])])
    return result


parameters = dict(primary=parameter_summary(primary), complete_case=parameter_summary(complete_case))
p, c = (np.array(parameters[k]['percentiles']) for k in ('primary', 'complete_case'))
parameters['complete_case_change'] = dict(median=(c[1]-p[1]).tolist(), central95_width=((c[2]-c[0])-(p[2]-p[0])).tolist())

# Conditional linearized errors of the 10 free coordinates (10 free, 6 bounds active); R5 maps to native b by -ln(10).
uncertainty = read(EVIDENCE/'conditional-uncertainty.json')
errors = {r['identity']: r for r in csv.DictReader((EVIDENCE/'conditional-standard-errors.csv').open())}
comparison = []
for i, q in enumerate(coords):
    se = errors[q['identity']]['conditional_standard_error']
    se = float(se)*(math.log(10) if q['identity'] == 'reaction:R5:correlation:a_k' else 1.) if se else None
    width = p[2][i]-p[0][i]
    x = np.array([d['coordinates'][i] for d in primary])
    tolerance = 1e-6*q['scale']
    comparison.append(dict(identity=q['identity'], unit=q['units'], conditional_standard_error=se,
                           draws_at_lower_bound=int(np.sum(x <= q['bounds'][0]+tolerance)), draws_at_upper_bound=int(np.sum(x >= q['bounds'][1]-tolerance)),
                           linearized_central95_width=None if se is None else 2*1.959963984540054*se,
                           bootstrap_central95_width=width, bootstrap_to_linearized_width=None if se is None else width/(2*1.959963984540054*se)))

# First-order cost change from the retained reference gradient at each lower-cost excursion.
excursions = []
for identity in lower:
    s = next(x for x in profiles if x['task']['identity'] == identity)
    q = next(x for x in coords if x['original_index'] == s['task']['coordinate'])
    step = s['task']['node']-q['origin']
    gradient = uncertainty['cost_gradient'][q['identity']]
    excursions.append(dict(identity=identity, coordinate=q['identity'], unit=q['units'], node=s['task']['node'], step=step,
                           reference_gradient=gradient, first_order_delta_cost=gradient*step, attained_delta_cost=s['delta_cost'],
                           outward_descent=uncertainty['active_bound_outward_descent'][q['identity']],
                           phase=s.get('phase'), inference_available=s['inference_available']))

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

# Calibration-row predictions, AARD and curves use, for each quantity, the primary draws where it is available.
available = lambda r: r['status'] == 'Available' and r['value'] is not None and math.isfinite(r['value'])
row_values = [[] for _ in blocks]
metrics, curves, curve_failures = {}, {}, {}
curves = {(i, q, u): [] for i, s in enumerate(read(AN/'inputs/curve-states.json')) for q, u in s['quantities']}
for d in primary:
    directory = AN/'results'/d['identity']
    rows = read(directory/'replay.json.gz')['rows']
    for values, r in zip(row_values, rows, strict=True):
        if available(r):
            values.append((d['identity'], r['value']))
    groups = {'reported pressure': [r for r in rows if r['row'].get('quantity') == 'PartialPressure'],
              'reported species': [r for r in rows if r['row'].get('quantity') == 'PhaseMoleFraction']}
    for r, b in zip(rows, blocks, strict=True):
        groups.setdefault(b['source']+' / '+r['row'].get('quantity', 'unknown'), []).append(r)
    for key, part in groups.items():
        if all(r['observed'] != 0 for r in part):
            metrics.setdefault(key, dict(observations=len(part), draws=[]))
            if all(map(available, part)):
                metrics[key]['draws'].append((d['identity'], 100*np.mean([abs(r['value']/r['observed']-1) for r in part])))
    for r in read(directory/'curves.json.gz')['rows']:
        if r['status'] == 'available' and isinstance(r['value'], (int, float)) and np.isfinite(r['value']):
            curves.setdefault((r['state_index'], r['quantity'], r['unit']), []).append((d['identity'], r['value']))
        else:
            cause = re.sub(r'-?\d[\d.]*(e[+-]?\d+)?', '#', r.get('cause') or 'nonfinite prediction')
            curve_failures[cause] = curve_failures.get(cause, 0)+1
complete_ids = {d['identity'] for d in complete_case}


def subsets(values):
    return dict(spread([v for _, v in values]), first100=spread([v for i, v in values if first100(i)]),
                complete_case=spread([v for i, v in values if i in complete_ids]))


metric_summary = {k: dict(subsets(m['draws']), observations=m['observations'], unit='percent',
                          draws=[dict(identity=i, AARD_percent=v) for i, v in m['draws']]) for k, m in metrics.items()}
row_summary = [dict(identity=b['identity'], source=b['source'], observed=r['observed'], quantity=r['row'].get('quantity'), **spread([v for _, v in values]))
               for b, r, values in zip(blocks, read(AN/'results'/primary[0]['identity']/'replay.json.gz')['rows'], row_values, strict=True)]
curve_summary = [dict(state_index=i, quantity=q, unit=u, **subsets(values)) for (i, q, u), values in sorted(curves.items())]
result = dict(wheel_sha256=SHA, attempted_profiles=len(profiles), attempted_bootstrap=len(bootstrap),
              bootstrap_eligibility=('Owner decision 2026-11-08 (orchestrator, recommended option): primary set is every converged draw whose '
                                     'positive-multiplicity rows are available and reproduce the native sampled cost (1e-8 relative) and weighted '
                                     'residuals (1e-8 absolute), with interaction admissibility; zero-multiplicity rows are outside the draw objective. '
                                     'Complete-case sensitivity additionally requires all 307 replay predictions.'),
              primary_bootstrap=len(primary), complete_case_bootstrap=len(complete_case),
              draw_eligibility=[{k: v for k, v in d.items() if k != 'coordinates'} for d in draws],
              lower_reference_profiles=lower, lower_reference_first_order=excursions, classifications=classification,
              parameters=parameters, conditional_error_comparison=comparison, calibration_rows=row_summary,
              AARD=metric_summary, curves=curve_summary, unavailable_curve_quantities_by_cause=curve_failures,
              failures=[dict(identity=s['task']['identity'], status=s.get('status'), cause=s.get('cause'))
                        for s in profiles if not s['inference_available']]
                       +[dict(identity=d['identity'], status=d['status'], cause=next(s.get('cause') for s in bootstrap if s['task']['identity'] == d['identity']))
                         for d in draws if not d['eligible']])
(AN/'results/study.json.tmp').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
(AN/'results/study.json.tmp').replace(AN/'results/study.json')
paths = [p for directory in ('inputs', 'results') for p in (AN/directory).rglob('*')
         if p.is_file() and p.name != 'result-hashes.json' and 'curve-runs' not in p.parts]
(AN/'results/result-hashes.json').write_text(json.dumps({str(p.relative_to(AN)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}, indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('attempted_profiles', 'attempted_bootstrap', 'primary_bootstrap', 'complete_case_bootstrap', 'lower_reference_profiles')}))
