"""Issue 235: one bounded fit of the 213 reactive MEA rows from the declared perturbed start."""
import gzip, hashlib, importlib.metadata, json, math, os, sys, time, zipfile
from pathlib import Path
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable

started, epoch = time.perf_counter(), time.time()
AN = Path(__file__).resolve().parent
OUT = AN / 'results/fit-e6dae5c7'
OUT.mkdir(exist_ok=True)
ACCEPTED = 45.37796168239049
def write(name, value):  # atomic; gzip above 5 MB
    data = (json.dumps(jsonable(value), indent=2, allow_nan=False) + '\n').encode()
    path = OUT / (name + '.gz' if len(data) > 5_000_000 else name)
    path.with_suffix('.tmp').write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)
    os.replace(path.with_suffix('.tmp'), path)
checks = {}
summary = dict(disposition=None, start_epoch=epoch, checks=checks)
def stop(disposition, **evidence):
    summary.update(disposition=disposition, wall_seconds=time.perf_counter() - started, **evidence)
    write('summary.json', summary)
    sys.exit(f'{disposition}: {checks}' if disposition != 'qualified within the stated neighborhood' else 0)

wheel = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')
assert hashlib.sha256(wheel.read_bytes()).hexdigest() == '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
with zipfile.ZipFile(wheel) as archive:
    assert all(archive.read(n) == (Path(epcsaft.__file__).parent.parent / n).read_bytes() for n in archive.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
summary['software'] = dict(wheel=str(wheel), wheel_sha256='83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6', installed_files_byte_identical=True, python=sys.version,
    packages={k: importlib.metadata.version(k) for k in ('epcsaft', 'numpy', 'scipy')}, cpu_count=os.cpu_count(), threads={k: os.environ.get(k, 'unset') for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')},
    input_hashes={str(p.relative_to(AN)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [AN / 'MEA-fit.toml', AN / 'declarations.toml', *sorted((AN / 'inputs').iterdir())]})

spec = SolventSpecification(AN / 'MEA-fit.toml')
rows = spec.inputs['observations']['fitted'] = [r for r in spec.inputs['observations']['fitted'] if r['group'] not in ('Kiepe', 'Cai', 'CO2-free density')]
declared, reference = spec.inputs['coordinates'], {r['target']: r for r in json.loads((AN / 'inputs/reference.json').read_text())}
assert len(rows) == 213 and len(declared) == 14
expected, where = [], {}  # Engine physical order: EOS targets with ties, then reaction rows
for q in [q for q in declared if 'targets' in q] + [q for q in declared if 'targets' not in q]:
    where[q['identity']] = len(expected)
    expected += [q['origin'] * t[2] for t in q['targets']] if 'targets' in q else [q['origin']]
def evaluate(records):  # owned native predictions; weighted residuals and group costs only
    bad = [p['identity'] for p in records if not (p['status'] == 'Available' and p['requested_tolerance_met'] and all(math.isfinite(p.get(k) or math.nan) for k in ('value', 'residual')))]
    w = [math.sqrt(r['weight']) * p['residual'] if not bad else None for r, p in zip(rows, records, strict=True)]
    return dict(unavailable=bad, rows=records, weighted_residuals=w, cost=None if bad else math.fsum(.5 * x * x for x in w),
                groups=None if bad else {g: math.fsum(.5 * x * x for x, r in zip(w, rows) if r['group'] == g) for g in dict.fromkeys(r['group'] for r in rows)})
def replay(parameters, chart):  # fresh observations with completed native laws; destination bounds kept
    laws = {(r['name'], r['correlation']['temperature_max']): r['correlation'] for g in spec.fitted_reactions(chart).values() for r in g}
    declared_laws = [(reaction, reaction.correlation) for problem in spec.problems.values() for reaction in problem.reactions]
    for reaction, law in declared_laws:
        reaction.correlation = eq.ReactionLogPolynomial(**laws[reaction.name, law.temperature_max])
    spec.model = epcsaft.Mixture(parameters, thermochemistry=spec.thermal)
    try:
        return evaluate([spec.prediction(r) for r in rows])
    finally:  # the fit must start from the declared laws, not a replayed chart
        for reaction, law in declared_laws:
            reaction.correlation = law

baseline = evaluate([spec.prediction(r) for r in rows])
baseline['differences'] = [] if baseline['unavailable'] else [dict(target=r['identity'], predicted=abs(p['value'] / q['predicted'] - 1),
    **{k: abs(v - q[k]) / max(abs(q[k]), 1) for k, v in (('residual', p['residual']), ('weighted_residual', w), ('cost', .5 * w * w))})
    for r, p, w in zip(rows, baseline['rows'], baseline['weighted_residuals']) for q in [reference[r['identity']]]]
checks['baseline'] = dict(unavailable=baseline['unavailable'], cost=baseline['cost'], reference=ACCEPTED, groups=baseline['groups'], limit=1e-10,
    cost_relative=None if baseline['unavailable'] else abs(baseline['cost'] / ACCEPTED - 1), maximum={k: max((x[k] for x in baseline['differences']), default=None) for k in ('predicted', 'residual', 'weighted_residual', 'cost')})
write('baseline.json', baseline)
if baseline['unavailable'] or max([checks['baseline']['cost_relative'], *checks['baseline']['maximum'].values()]) > 1e-10:
    stop('baseline/input mismatch')

try:
    evaluation = reg.differentiate(spec.parameters, spec.coordinates(), [spec.observation(r) for r in rows], optimizer=[0.] * 14, holds=[], thermochemistry=spec.thermal)
except Exception as error:
    stop('unavailable/nonfinite start or endpoint observation', cause=f'{type(error).__name__}: {error}')
chart = evaluation.chart
start = replay(epcsaft.Parameters(chart.parameters, spec.parameters.component_ids, spec.parameters.site_ids), chart)
probe = json.loads((AN / 'results/design-replay-e6dae5c7/coordinate-start.json').read_text())['reaction_laws']
start.update(physical=list(chart.physical), reaction_laws={n: {k: getattr(l, k) for k in probe[n]} for n, l in chart.reaction_laws.items()}, statuses=[s.name for s in evaluation.statuses],
             residual_optimizer_gradient=list(evaluation.residual_optimizer_gradient))
check = checks['start'] = dict(unavailable=start['unavailable'], cost=start['cost'], groups=start['groups'], statuses_available=start['statuses'].count('Available'),
    derivatives_finite=bool(np.isfinite(start['residual_optimizer_gradient']).all()) and len(start['residual_optimizer_gradient']) == 213 * 14,
    maximum_physical_error=max(abs(a - b) for a, b in zip(expected, chart.physical, strict=True)), laws_equal_design_probe=start['reaction_laws'] == probe,
    weighted_residual_difference_norm=None if start['unavailable'] else float(np.linalg.norm(np.subtract(start['weighted_residuals'], baseline['weighted_residuals']))), limit=1e-4)
write('start.json', start)
if check['maximum_physical_error'] > 1e-12 or not check['laws_equal_design_probe']:
    stop('invalid coordinate/law declaration')
if start['unavailable'] or check['statuses_available'] != 213 or not check['derivatives_finite'] or check['weighted_residual_difference_norm'] < 1e-4:
    stop('unavailable/nonfinite start or endpoint observation')
summary['preflight_seconds'] = time.perf_counter() - started
if summary['preflight_seconds'] > 300:
    stop('budget exhaustion', cause='preflight exceeded 300 s')

fit_started = time.perf_counter()
result, report, fitted = spec.fit()
summary['fit_seconds'] = time.perf_counter() - fit_started
report.update(solver_options=jsonable(result.solver_options), optimizer_jacobian=list(result.optimizer_jacobian), chart_physical=list(result.chart.physical), statuses=[s.name for s in result.statuses],
              reaction_laws={n: {k: getattr(l, k) for k in probe[n]} for n, l in result.chart.reaction_laws.items()}, requested_workers=os.cpu_count(),
              failures=[dict(f, target=rows[f['observation']]['identity'] if f['observation'] < 213 else 'request or model exception') for f in report['failures']])
write('native-fit.json', report)
physical, v = np.array(result.chart.physical), np.array(result.optimizer)
neighborhood = [(physical[where[q['identity']]] - q['base']) / q['scale'] for q in declared]
summary['coordinates'] = [dict(identity=q['identity'], original_index=q['original_index'], bounds=q['bounds'], start=q['origin'], fitted=physical[i], optimizer=v[j], scaled_from_accepted=neighborhood[j],
    active_bound=j in result.covariance.active_bounds, ties=[physical[i + k] / physical[i] for k in range(1, len(q.get('targets', [0])))]) for j, q in enumerate(declared) for i in [where[q['identity']]]]
singular = result.covariance.singular_values
checks['fit'] = dict(status=result.status, usable=result.usable, message=result.message, iterations=result.iterations, limit_iterations=60, trial_failures=result.trial_failures, statuses_available=report['statuses'].count('Available'),
    maximum_scaled_movement=float(np.abs(v).max()), limit_movement=1e-5, rank=result.covariance.rank, singular_values=singular, condition_number=max(singular) / min(singular) if singular and min(singular) > 0 else None,
    covariance_status=result.covariance.status, active_bounds=[declared[i]['identity'] for i in result.covariance.active_bounds], projected_gradient_norm=result.covariance.projected_gradient_norm)
if not result.usable or result.status == 'failed':  # no candidate to replay
    stop('unusable/nonconverged fitting')
final = replay(fitted, result.chart)
final['differences'] = None if final['unavailable'] else [abs(a - b) for a, b in zip(final['weighted_residuals'], result.weighted_residuals, strict=True)]
write('replay.json', final)
checks.update(
    initial_cost=dict(native=result.initial_cost, independent=start['cost'], relative=abs(result.initial_cost / start['cost'] - 1), limit=1e-8),
    bounds_and_ties=dict(within=all(q['bounds'][0] <= c['fitted'] <= q['bounds'][1] for q, c in zip(declared, summary['coordinates'])),
                         ties_error=max((abs(r - t[2]) for q, c in zip(declared, summary['coordinates']) for r, t in zip(c['ties'], q.get('targets', [])[1:])), default=0.0)),
    replay=dict(unavailable=final['unavailable'], cost=final['cost'], native=result.final_cost, groups=final['groups'], cost_relative=None if final['unavailable'] else abs(final['cost'] / result.final_cost - 1),
                maximum_weighted_residual_difference=None if final['unavailable'] else max(final['differences']), limits=[1e-8, 1e-8]),
    cost=dict(final=result.final_cost, start=start['cost'], ceiling=ACCEPTED * (1 + 1e-6), progress=start['cost'] - result.final_cost, limit_progress=1e-6,
              group_change={g: final['groups'][g] - baseline['groups'][g] for g in baseline['groups']} if final['groups'] else None),
    neighborhood=dict(maximum=float(np.abs(neighborhood).max()), optimizer_form=float(np.abs(v + [q['d'] for q in declared]).max()), limit=1.0))
summary['replay_seconds'] = time.perf_counter() - fit_started - summary['fit_seconds']
if result.status == 'limit_reached' or summary['replay_seconds'] > 300:
    stop('budget exhaustion')
if result.status != 'converged' or not result.usable or checks['fit']['maximum_scaled_movement'] <= 1e-5:
    stop('unusable/nonconverged fitting')
if checks['initial_cost']['relative'] > 1e-8 or not checks['bounds_and_ties']['within'] or checks['bounds_and_ties']['ties_error'] > 1e-12:
    stop('invalid coordinate/law declaration')
if final['unavailable'] or checks['fit']['statuses_available'] != 213:
    stop('unavailable/nonfinite start or endpoint observation')
if checks['replay']['cost_relative'] > 1e-8 or checks['replay']['maximum_weighted_residual_difference'] > 1e-8:
    stop('replay mismatch')
if result.final_cost > checks['cost']['ceiling'] or checks['cost']['progress'] < 1e-6:
    stop('cost/progress failure')
stop('outside-neighborhood result' if checks['neighborhood']['maximum'] > 1 else 'qualified within the stated neighborhood')
