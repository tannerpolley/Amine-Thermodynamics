"""Issue 262: finite MEA coordinate profiles and source/series bootstrap."""
import copy
import gzip
import hashlib
import importlib.metadata
import json
import math
import os
import traceback
from pathlib import Path
import resource
import sys
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
AN = Path(__file__).resolve().parent
B = AN.parent
sys.path[:0] = [str(ROOT/'src'), str(B/'scripts'), str(B/'calibration-misfit')]
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from epcsaft.parameters import document_mapping
from MEA.solvent_specification import SolventSpecification, jsonable
import fit_campaign as campaign
import shared_evaluation as owner

WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')
SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
owner.ENGINE_WHEEL_SHA256 = SHA
owner.ENGINE_COMMIT = 'e6dae5c7353ae10e0aa2d8e46055847b9d64bbe4'
import phase_diagnosis_255 as phase  # Existing import-time guard checks the task-approved wheel.
COST = 148.87893934557388
LAW = ('a', 'b', 'c', 'd', 'e', 'f', 'reference_temperature')
COORDS = json.loads((AN/'inputs/coordinates.json').read_text())
BLOCKS = json.loads((AN/'inputs/blocks.json').read_text())


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(jsonable(value), allow_nan=False) + '\n').encode()
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)
    tmp.replace(path)


def verify():
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
    with zipfile.ZipFile(WHEEL) as archive:
        assert all(archive.read(n) == (Path(epcsaft.__file__).parent.parent/n).read_bytes()
                   for n in archive.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
    for path, digest in read(AN/'inputs/input-hashes.json').items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    assert read(AN/'inputs/environment.json') == {k: importlib.metadata.version(k) for k in read(AN/'inputs/environment.json')}
    assert read(AN/'results/qualification-replay.json')['summary']['passed']
    assert read(AN/'results/qualification-interactions.json')['summary']['passed']


def fresh():
    s = SolventSpecification(ROOT/'analyses/solvent_specification_mea/MEA.toml')
    s.inputs['coordinates'] = copy.deepcopy(COORDS)
    return s


def set_laws(s, laws):
    for group in s.spec['chemistry']['reactions'].values():
        for reaction in group:
            reaction['correlation'].update(laws.get(reaction['name'], {}))
    for problem in s.problems.values():
        for reaction in problem.reactions:
            law = reaction.correlation
            if reaction.name not in laws:
                continue
            original = (law.temperature_min, law.temperature_max, law.standard_state_id)
            fields = {k: getattr(law, k) for k in (*LAW, 'temperature_min', 'temperature_max', 'standard_state_id')}
            fields.update(laws[reaction.name])
            reaction.correlation = eq.ReactionLogPolynomial(**fields)
            assert original == tuple(getattr(reaction.correlation, k) for k in ('temperature_min', 'temperature_max', 'standard_state_id'))


def replay(s, path):
    rows = [s.prediction(r) for r in s.inputs['observations']['fitted']]
    dump(path, dict(wheel_sha256=SHA, rows=rows))
    bad = [r for r in rows if not (r['status'] == 'Available' and r.get('requested_tolerance_met')
           and math.isfinite(r['value']) and math.isfinite(r['residual']))]
    if len(rows) != 307 or bad:
        raise ValueError('Unavailable 307-row replay: '+str([(r['identity'], r['status'], r.get('message')) for r in bad]))
    return rows


def weighted(rows, s, multiplicities):
    return [math.sqrt(r['weight']*m)*v['residual'] for r, v, m in
            zip(s.inputs['observations']['fitted'], rows, multiplicities, strict=True)]


def starting(task):
    s, offset = fresh(), 0.
    if task['kind'] == 'profile':
        index, node = task['coordinate'], task['node']
        q = s.inputs['coordinates'][index]
        if 'targets' in q:
            updates = {('component/'+target if isinstance(target, str) else 'pair/'+'/'.join(target))
                       +'/'+family.replace('_reciprocal', '/reciprocal'): node*factor
                       for family, target, factor in q['targets']}
            s.parameters = epcsaft.Parameters.from_mapping(owner.with_parameter_values(s.inputs['endpoint'], updates))
        else:
            q['bounds'] = [min(q['bounds'][0], node), max(q['bounds'][1], node)]  # Only the held node crosses its frozen historical bound.
            u = [0.]*16
            u[index] = (node-q['origin'])/q['scale']
            v = reg.differentiate(s.parameters, s.coordinates(), [s.observation(r) for r in s.inputs['observations']['fitted']],
                                  optimizer=u, holds=[], thermochemistry=s.thermal)
            set_laws(s, {name: {k: getattr(law, k) for k in LAW} for name, law in v.chart.reaction_laws.items()})
            if index == 11:
                offset = v.chart.reaction_laws['R5'].b-COORDS[9]['origin']
                s.inputs['coordinates'][9]['origin'] += offset
                s.inputs['coordinates'][9]['bounds'] = [b+offset for b in COORDS[9]['bounds']]
        s.inputs['coordinates'] = [q for q in s.inputs['coordinates'] if q['original_index'] != index]
    s.model = epcsaft.Mixture(s.parameters, thermochemistry=s.thermal)
    return s, offset


def original_values(s, result, task, offset):
    values, cursor = {}, 0
    declared = s.inputs['coordinates']
    for q in [q for q in declared if 'targets' in q]+[q for q in declared if 'targets' not in q]:
        x = result.chart.physical[cursor]
        values[q['original_index']] = x-(offset if q['original_index'] == 9 else 0.)
        if 'targets' in q:
            for j, (_, _, factor) in enumerate(q['targets']):
                assert abs(result.chart.physical[cursor+j]-x*factor) <= 1e-10
        assert q['bounds'][0]-1e-10 <= x <= q['bounds'][1]+1e-10
        cursor += len(q.get('targets', [None]))
    if task['kind'] == 'profile':
        values[task['coordinate']] = task['node']
    assert len(values) == 16
    return [values[i] for i in range(16)]


def reload_candidate(s, mapping):
    s.parameters = epcsaft.Parameters.from_mapping(mapping)
    s.model = epcsaft.Mixture(s.parameters, thermochemistry=s.thermal)
    request = {'reaction_system': {'reaction_matrix': [[r.stoichiometry.get(cid, 0.) for cid in s.model.component_ids]
                for r in next(p for p in s.problems.values() if p.reactions).reactions]}}
    normalized = owner._engine_reaction_records(request, owner.reaction_values(mapping), mapping=mapping)
    set_laws(s, {r['reaction_id']: {k: r['engine_correlation'][k] for k in ('a', 'b', 'c', 'd', 'reference_temperature')} for r in normalized})


def interactions(mapping, path):
    rows = []
    x = dict(water=.70, monoethanolamine=.15, **{'carbon-dioxide': .05, 'protonated-monoethanolamine': .05,
                                             'carbamate-anion': .04, 'bicarbonate-anion': .01})
    for i, pair in enumerate(mapping['pairs']):
        c = {r['family']: r for r in pair['coefficients']}
        if 'k_ij_reciprocal_temperature_slope' not in c:
            continue
        A = c['k_ij']['value']['magnitude']
        slope = c['k_ij_reciprocal_temperature_slope']
        B, Tr = slope['value']['magnitude'], slope['reference_temperature']['magnitude']
        for T in (293.15, 436.85):
            k = A+B*(1/T-1/Tr)  # Owner-authorized reading of the MEA input declaration; issue 262 revision 4.
            constant = copy.deepcopy(mapping)
            p = constant['pairs'][i]
            p['coefficients'] = [r for r in p['coefficients'] if r['family'] != 'k_ij_reciprocal_temperature_slope']
            next(r for r in p['coefficients'] if r['family'] == 'k_ij')['value']['magnitude'] = k
            perturbed = copy.deepcopy(constant)
            next(r for r in perturbed['pairs'][i]['coefficients'] if r['family'] == 'k_ij')['value']['magnitude'] = k+1e-3
            models = [epcsaft.Mixture(epcsaft.Parameters.from_mapping(m)) for m in (mapping, constant, perturbed)]
            component = pair['component_id_b']
            ci = models[0].component_ids.index(component)
            for P in (1e5, 5e5, 1e6):
                try:
                    states = [m.state(T, P=P, x=x, phase='liquid') for m in models]
                except Exception as error:
                    rows.append(dict(pair=[pair['component_id_a'], component], T_K=T, P_Pa=P, composition=x,
                                     kij=k, cause=f'{type(error).__name__}: {error}'))
                    dump(path, dict(wheel_sha256=SHA, rows=rows))
                    raise
                v = [r.residual_chemical_potential_over_rt[ci] for r in states]
                assert all(isinstance(z, (int, float)) and math.isfinite(z) for z in v)
                difference, sensitivity = abs(v[0]-v[1])/max(abs(v[0]), 1e-300), abs(v[2]-v[1])/max(abs(v[1]), 1e-300)
                rows.append(dict(pair=[pair['component_id_a'], component], T_K=T, P_Pa=P, composition=x, kij=k,
                                 quantity='neutral residual chemical potential / RT', unit='dimensionless', values=v,
                                 relative_difference=difference, relative_sensitivity=sensitivity,
                                 density_mol_m3=[r.molar_density for r in states], admissible=k <= 1))
                dump(path, dict(wheel_sha256=SHA, rows=rows))
                assert difference <= 1e-10 and sensitivity >= 1e-7, rows[-1]
    return rows


def phase_state(mapping, index, directory):
    old = phase.e.load(phase.OLD/'comparison'/f'point-{index}.json')
    row = {k: old[k] for k in ('index', 'temperature_K', 'loading', 'pressure_Pa')}
    path = directory/f'phase-point-{index}.json'
    try:
        phase.f.family_job(mapping, phase.e.request(mapping, 313.15, .11), row, [], path)
    except Exception as error:
        row.update(classification='unavailable', failure=f'{type(error).__name__}: {error}')
    row['wheel_sha256'] = SHA
    reduced = phase.reduce_state(row)
    reduced['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    dump(path.with_suffix('.json.gz'), row)
    path.unlink(missing_ok=True)
    if index % 40 == 0:
        print('phase', directory.name, 'completed state', index, flush=True)
    return reduced


def phases(mapping, directory):
    reduced = [phase_state(mapping, i, directory) for i in range(162)]
    summary = dict(wheel_sha256=SHA, states=len(reduced), descent_states=sum(r['resolved'] > 0 for r in reduced),
                   incomplete_states=sum(not r['complete'] for r in reduced), reductions=reduced)
    dump(directory/'phase-summary.json', summary)
    return {k: summary[k] for k in ('states', 'descent_states', 'incomplete_states')}


def curve_predictions(mapping, path):
    import model_curves as curves
    curves.MAPPING, curves.RECORD = mapping, path
    curves.PARAMS = epcsaft.Parameters.from_mapping(mapping)
    curves.MODEL = epcsaft.Mixture(curves.PARAMS, thermochemistry=curves.he.vrc.record())
    curves.HEAT_REQUEST = curves.he.request(mapping, 313.15, .11)
    curves.RUNS = path.parent/'curve-runs'
    curves.IDENTITY = dict(parameter_sha256=owner.sha256(path), engine_wheel_sha256=SHA)
    curves.fe.binding('Held', str(path))
    rows = []
    for i, q in enumerate(read(AN/'inputs/curve-states.json')):
        rows.extend(dict(r, state_index=i) for r in curves.run(q['family'], q['state']))
        if i % 100 == 0:
            print('curve', path.parent.name, 'completed state', i, flush=True)
    return rows


def fit(task):
    directory = AN/'results'/task['identity']
    if (directory/'summary.json').exists():
        return read(directory/'summary.json')
    started = time.monotonic()
    summary = dict(wheel_sha256=SHA, task=task, usable=False, inference_available=False)
    try:
        s, offset = starting(task)
        records = s.inputs['observations']['fitted']
        multiplicities = task.get('multiplicities', [1]*307)
        start = replay(s, directory/'start.json.gz')
        w0 = weighted(start, s, multiplicities)
        initial_cost = math.fsum(.5*x*x for x in w0)
        included = [i for i, m in enumerate(multiplicities) if m]
        controls = reg.FitControls(maximum_iterations=180, function_tolerance=1e-6, parameter_tolerance=1e-10,
                                   gradient_tolerance=1e-8, maximum_elapsed_time_seconds=600., workers=1)
        result = reg.fit(s.parameters, s.coordinates(), [s.observation(records[i]) for i in included],
                         weights=[records[i]['weight']*multiplicities[i] for i in included],
                         thermochemistry=s.thermal, controls=controls, singular_vectors=True)
        report = {k: jsonable(getattr(result, k)) for k in ('status', 'message', 'usable', 'initial_cost', 'final_cost',
                  'optimizer', 'physical', 'weighted_residuals', 'predictions', 'iterations', 'iteration_costs',
                  'trial_failures', 'residual_evaluations', 'jacobian_evaluations')}
        report.update(wheel_sha256=SHA, included_rows=included, multiplicities=multiplicities,
                      statuses=[v.name for v in result.statuses], solver_options=jsonable(result.solver_options),
                      independent_initial_cost=initial_cost, covariance={k: jsonable(getattr(result.covariance, k))
                      for k in ('rank', 'singular_values', 'active_bounds', 'projected_gradient_norm', 'right_vectors')},
                      failures=[dict(observation=f.observation, status=f.status.name, message=f.message) for f in result.failures])
        dump(directory/'native-fit.json.gz', report)
        print('fit', task['identity'], result.status, 'cost', result.final_cost, flush=True)
        assert abs(result.initial_cost-initial_cost) <= 1e-8*max(abs(initial_cost), 1e-300)
        summary.update(status=result.status, usable=result.usable, initial_cost=initial_cost, cost=result.final_cost)
        if result.usable:
            values = original_values(s, result, task, offset)
            fitted = reg.fitted_parameters(s.parameters, result)
            laws = {r['name']: eq.ReactionLogPolynomial(**r['correlation']) for group in s.fitted_reactions(result.chart).values()
                    for r in group if r['name'] in ('R2', 'R5')}
            mapping = owner.with_parameter_values(dict(document_mapping(fitted)), campaign.completed_reaction_values(laws))
            dump(directory/'parameters.json', mapping)
            reload_candidate(s, read(directory/'parameters.json'))
            final = replay(s, directory/'replay.json.gz')
            wf = weighted(final, s, multiplicities)
            cost = math.fsum(.5*x*x for x in wf)
            difference = max(abs(wf[i]-r) for i, r in zip(included, result.weighted_residuals, strict=True))
            dump(directory/'replay.json.gz', dict(wheel_sha256=SHA, rows=final, cost=cost, maximum_weighted_residual_difference=difference))
            assert abs(cost-result.final_cost) <= 1e-8*max(abs(cost), 1e-300) and difference <= 1e-8
            assert cost-initial_cost <= 1e-8*max(abs(initial_cost), 1e-300)
            summary.update(coordinates=values, calibration_cost=math.fsum(.5*r['weight']*v['residual']**2 for r, v in zip(records, final)))
            if task['kind'] == 'profile':
                summary.update(delta_cost=cost-COST, twice_delta_cost=2*(cost-COST), lower_reference=cost < COST*(1-1e-8))
            summary['oracle_failure'] = True
            checked = interactions(mapping, directory/'interactions.json')
            summary['oracle_failure'] = False
            summary['interaction_admissible'] = all(r['admissible'] for r in checked)
            summary['inference_available'] = result.status == 'converged' and summary['interaction_admissible']
            if task['kind'] == 'profile':
                summary['phase'] = phases(mapping, directory)
            elif result.status == 'converged':
                dump(directory/'curves.json.gz', dict(wheel_sha256=SHA, rows=curve_predictions(mapping, directory/'parameters.json')))
    except Exception as error:
        summary.update(cause=f'{type(error).__name__}: {error}', inference_available=False, traceback=traceback.format_exc())
    summary.update(wall_seconds=time.monotonic()-started, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    dump(directory/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'task'}), flush=True)
    return summary


def complete(task):
    """Finish a converged draw whose replay stopped only on zero-multiplicity rows (owner decision, 2026-11-08).

    Reuses the retained fit and candidate; no refit. Eligibility itself is checked from retained data in aggregate.py.
    """
    directory = AN/'results'/task['identity']
    native = read_gz(directory/'native-fit.json.gz')
    rows = read_gz(directory/'replay.json.gz')['rows']
    bad = [m for r, m in zip(rows, task['multiplicities'], strict=True) if r['status'] != 'Available']
    if native['status'] != 'converged' or not bad or any(bad) or (directory/'completion.json').exists():
        return None
    s, offset = starting(task)
    values = original_values(s, SimpleNamespace(chart=SimpleNamespace(physical=native['physical'])), task, offset)
    mapping = read(directory/'parameters.json')
    checked = interactions(mapping, directory/'interactions.json')
    dump(directory/'curves.json.gz', dict(wheel_sha256=SHA, rows=curve_predictions(mapping, directory/'parameters.json')))
    record = dict(wheel_sha256=SHA, coordinates=values, interaction_admissible=all(r['admissible'] for r in checked))
    dump(directory/'completion.json', record)
    return record


def read_gz(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def tasks():
    result = [dict(identity=f'profile-{q["original_index"]:02d}-{j:02d}', kind='profile', coordinate=q['original_index'], node=node)
              for q in COORDS for j, node in enumerate(q['nodes'])]
    rng = np.random.default_rng(262)
    sources = sorted({r['source'] for r in BLOCKS})
    for draw in range(200):
        counts = dict.fromkeys({r['series'] for r in BLOCKS}, 0)
        for source in rng.choice(sources, len(sources), replace=True):
            series = sorted({r['series'] for r in BLOCKS if r['source'] == source})
            for selected in rng.choice(series, len(series), replace=True):
                counts[selected] += 1
        m = [counts[r['series']] for r in BLOCKS]
        assert all(len({m[i] for i, r in enumerate(BLOCKS) if r['state'] == state}) == 1 for state in {r['state'] for r in BLOCKS})
        result.append(dict(identity=f'bootstrap-{draw:03d}', kind='bootstrap', multiplicities=m))
    dump(AN/'inputs/tasks.json', dict(wheel_sha256=SHA, seed=262, tasks=result))
    return result


if __name__ == '__main__':
    verify()
    memory = int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1])*1024
    allowance = 512*1024**2
    reference = AN/'results/phase-reference/summary.json'
    if reference.exists():
        allowance = max(allowance, max(r['peak_rss_kib'] for r in read(reference)['reductions'])*1024)
    workers = max(1, min(os.cpu_count(), (memory-8*1024**3)//allowance))
    command = sys.argv[1]
    if command == 'complete':
        draws = [t for t in tasks() if t['kind'] == 'bootstrap']
        for t in draws:  # The coordinate recovery must reproduce every retained converged summary.
            s = read(AN/'results'/t['identity']/'summary.json')
            if s.get('coordinates'):
                native = read_gz(AN/'results'/t['identity']/'native-fit.json.gz')
                assert original_values(fresh(), SimpleNamespace(chart=SimpleNamespace(physical=native['physical'])), t, 0.) == s['coordinates']
        with ProcessPoolExecutor(min(workers, len(draws))) as pool:
            print(sum(r is not None for r in pool.map(complete, draws)), 'draws completed', flush=True)
    elif command == 'phase-reference':
        directory = AN/'results/phase-reference'
        with ProcessPoolExecutor(workers) as pool:
            rows = list(pool.map(phase_state, [fresh().inputs['endpoint']]*162, range(162), [directory]*162))
        summary = dict(wheel_sha256=SHA, states=len(rows), descent_states=sum(r['resolved'] > 0 for r in rows), incomplete_states=sum(not r['complete'] for r in rows))
        dump(directory/'summary.json', dict(summary, reductions=rows))
        print(summary, flush=True)
        assert summary['states'] == 162 and summary['descent_states'] == summary['incomplete_states'] == 0
    else:
        ref = read(AN/'results/phase-reference/summary.json')
        assert ref['states'] == 162 and ref['descent_states'] == ref['incomplete_states'] == 0
        declared = tasks()
        selected = declared if command == 'calculate' else [q for q in declared if q['identity'] == command or
                    (command == 'held-reactions' and q.get('coordinate') in (10, 11) and q['node'] != 0)]
        assert selected
        workers = min(workers, len(selected))
        dump(AN/f'results/runtime-{command}.json', dict(wheel_sha256=SHA, workers=workers, cpu_count=os.cpu_count(), available_memory_bytes=memory,
                                           fit_workers=1, reserve_bytes=8*1024**3, process_allowance_bytes=allowance, process_pid=os.getpid(),
                                           producer_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                           for p in (Path(__file__), B/'scripts/fit_campaign.py', B/'scripts/model_curves.py')}))
        with ProcessPoolExecutor(workers) as pool:
            for summary in pool.map(fit, selected):
                if summary.get('oracle_failure'):
                    pool.shutdown(wait=True, cancel_futures=True)
                    raise RuntimeError('Interaction equivalence unavailable; stop and report '+str(summary))
