"""Run a frozen MEA fit declaration directly through Engine (#179)."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import resource
import struct
import sys
import time
import traceback
import zipfile

COMMAND_STARTED = time.monotonic()
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def checked(path, sha):
    path = ROOT / path
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != sha:
        raise ValueError(f'input hash mismatch: {path}: {actual} != {sha}')
    return path


def verify(spec):
    files = {}
    for r in spec['inputs']:
        checked(r['path'], r['sha256'])
        files[r['path']] = r['sha256']
    wheel = checked(spec['engine']['wheel_path'], spec['engine']['wheel_sha256'])
    import epcsaft
    package = Path(epcsaft.__file__).resolve().parent
    if not package.is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError(f'Engine source checkout rejected: {package}')
    with zipfile.ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if n.startswith('epcsaft/') and not n.endswith('/')]
        for name in names:
            if (package.parent / name).read_bytes() != archive.read(name):
                raise ValueError(f'installed Engine differs from wheel: {name}')
    packages = {p: importlib.metadata.version(p) for p in ('epcsaft','numpy','scipy')}
    for p, version in spec['engine']['packages'].items():
        if packages[p] != version:
            raise ValueError(f'{p} version mismatch: {packages[p]} != {version}')
    return dict(files=files, wheel_sha256=spec['engine']['wheel_sha256'], installed_package=str(package),
        installed_files_verified=len(names), python=sys.version, packages=packages)


def workers(memory, cpu, allowance, requested=None):
    if memory < 0 or cpu < 1 or allowance <= 0:
        raise ValueError('invalid worker-sizing inputs')
    chosen = max(1, min(cpu, math.floor(memory/allowance)))
    if requested is not None and (requested > cpu or requested*allowance > memory):
        raise RuntimeError(f'deferred reproduction: {requested} workers require {requested*allowance} bytes; available {memory}')
    return requested if requested is not None else chosen


def machine(spec, requested):
    rows = {line.split(':')[0]: line.split(':')[1].strip() for line in Path('/proc/meminfo').read_text().splitlines()}
    memory = int(rows['MemAvailable'].split()[0])*1024
    cpu = os.cpu_count()
    if cpu is None:
        raise RuntimeError('CPU count unavailable')
    allowance = spec['worker_memory']['allowance_bytes']
    return dict(MemAvailable_bytes=memory, CPU_count=cpu, workers_requested=workers(memory,cpu,allowance,requested),
        worker_allowance_bytes=allowance, worker_memory_estimate=json.dumps(spec['worker_memory']),
        actual_workers=None, state_group_cap=None, actual_workers_reason='not returned by Engine')


def cpu_seconds():
    return math.fsum(r.ru_utime+r.ru_stime for r in (resource.getrusage(resource.RUSAGE_SELF),
        resource.getrusage(resource.RUSAGE_CHILDREN)))


def differences(expected, actual, path=''):
    result = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for k in expected:
            if k not in actual:
                result.append(dict(field=path+'/'+k, reason='missing'))
            else:
                result.extend(differences(expected[k], actual[k], path+'/'+k))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            result.append(dict(field=path, expected_length=len(expected), actual_length=len(actual)))
        for i,(a,b) in enumerate(zip(expected,actual)):
            result.extend(differences(a,b,f'{path}/{i}'))
    elif isinstance(expected, (int,float)) and isinstance(actual, (int,float)):
        if struct.pack('!d',expected) != struct.pack('!d',actual):
            result.append(dict(field=path,expected=expected,actual=actual,
                expected_hex=float(expected).hex(), actual_hex=float(actual).hex()))
    elif expected != actual:
        result.append(dict(field=path,expected=expected,actual=actual))
    return result



def replay_comparison(delta, policy):
    accepted = []
    for difference in delta:
        field = difference['field'].rsplit('/', 1)[-1]
        a, b = difference.get('expected'), difference.get('actual')
        eligible = (field in ('residual','weighted_residual','cost','common149_cost')
            and isinstance(a,(int,float)) and isinstance(b,(int,float)))
        if eligible and policy:
            limit = max(policy['maximum_ulps']*math.ulp(a), policy['absolute_below_one'] if abs(a)<1 else 0.)
            difference.update(absolute_difference=abs(a-b), allowed_absolute_difference=limit,
                accepted_rounding=abs(a-b)<=limit)
        else:
            difference['accepted_rounding'] = False
        if difference['accepted_rounding']:
            accepted.append(difference)
    return dict(passed=all(d['accepted_rounding'] for d in delta), bitwise_equal=not delta,
        differences=delta, accepted_rounding_fields=len(accepted), cause=policy.get('cause') if policy else None,
        maximum_abs_weighted_residual_difference=max((d['absolute_difference'] for d in accepted
            if d['field'].endswith('/weighted_residual')),default=0.),
        maximum_abs_cost_difference=max((d['absolute_difference'] for d in accepted
            if d['field'].endswith('/cost')),default=0.))


def resolve(spec, case, start):
    import fit_observations as o
    mapping = load(checked(start['parameters_path'], start['sha256']))
    variant = case['variant']
    if next(f['choice'] for f in mapping['model_families'] if f['kind']=='electrolyte') != variant['born']:
        raise ValueError('Born variant mismatch')
    if next(f for f in mapping['model_families'] if f['kind']=='permittivity') != variant['permittivity']:
        raise ValueError('permittivity variant mismatch')
    if o.s.reaction_values(mapping) != variant['chemistry']:
        raise ValueError('chemistry variant mismatch')
    params, rows = o.rows_for(spec,mapping,case['observations'])
    values = o.s.parameter_values(mapping)
    coordinates = [spec['coordinates'][i] for i in case['coordinates']]
    for c in coordinates:
        if struct.pack('!d', values[c['identity']]) != struct.pack('!d',c['origin'][start['id']]):
            raise ValueError(f"coordinate origin mismatch: {c['identity']}")
    return mapping, params, rows, coordinates



def water_study(spec, out, started):
    import fit_observations as o
    candidates = []
    def elapsed():
        return dict(cpu_s=cpu_seconds()+prior.get('cpu_s',spec['prior_cpu_charge_s']),
            wall_s=time.monotonic()-started+prior.get('wall_s',spec['prior_wall_charge_s']))
    baseline = list(csv.DictReader(checked(spec['metrics_path'],spec['metrics_sha256']).open()))
    def assess(mapping, directory):
        clock, cpu = time.monotonic(), cpu_seconds()
        result = o.water_assessment(spec,mapping)
        result.update(cpu_s=cpu_seconds()-cpu,wall_s=time.monotonic()-clock)
        write(directory/'assessment.json',result)
        return result
    def gates(result):
        rows, limits = result['rows'], spec['gates']
        verdict = dict(complete=len(rows)==42 and all(r['evaluated'] for r in rows),
            cp=all(abs(r.get('cp_error_relative',math.inf))<=limits['cp'] for r in rows),
            numerical=all(r.get('cp_verified',False) and r.get('dP_drho',0)>0 and
                (r['grid']=='atmospheric-controls' or (r.get('saturation_success',False) and
                r.get('saturation_max_abs_residual',math.inf)<=limits['raw_residual'] and r.get('saturated_dP_drho',0)>0)) for r in rows))
        for m in result['metrics']:
            if m['quantity'] not in ('saturated_liquid_rho','psat'):
                continue
            b = next(b for b in baseline if b['record']=='original' and b['grid']==m['grid'] and b['quantity']==m['quantity'])
            for stat in ('mean_absolute_relative_error','maximum_absolute_relative_error'):
                verdict[m['grid']+'/'+m['quantity']+'/'+stat] = (m['evaluated_rows']==m['requested_rows'] and m[stat] is not None and m[stat]<=float(b[stat])+limits['slack'])
        return verdict
    try:
        for record in spec['records']:
            result = assess(load(checked(record['path'],record['sha256'])),out/'replay'/record['id'])
            delta = [dict(grid=m['grid'],quantity=m['quantity'],statistic=k,difference=m[k]-float(b[k]))
                for m in result['metrics'] for b in baseline if b['record']==record['id'] and b['grid']==m['grid'] and b['quantity']==m['quantity']
                for k in ('mean_absolute_relative_error','maximum_absolute_relative_error')]
            passed = all(r['evaluated'] for r in result['rows']) and len(delta)==len([b for b in baseline if b['record']==record['id']])*2 and all(abs(d['difference'])<=spec['gates']['slack'] for d in delta)
            write(out/'replay'/record['id']/'comparison.json',dict(passed=passed,differences=delta))
            if not passed:
                raise RuntimeError('frozen water replay mismatch; fitting stopped')
        sizing = machine(spec,None)
        write(out/'machine.json',sizing)
        for case in spec['cases']:
            remaining = min(spec['budget_s']-elapsed()['wall_s'],(spec['budget_s']-elapsed()['cpu_s'])/sizing['workers_requested'])-spec['assessment_reserve_s']
            if remaining<=0:
                break
            directory = out/case['id']
            mapping = load(checked(case['parameters_path'],case['sha256']))
            mapping = o.s.with_parameter_values(mapping,case['origins'])
            params, _, thermal, declared = o.water_rows(spec,mapping)
            rows, weights = [], []
            for ref, cp, problem in declared:
                if ref['grid']=='staggered':
                    continue
                if ref['grid']=='primary':
                    for kind,q in (('phase_density','saturated_liquid_rho'),('pressure','psat')):
                        observed = float(ref['saturated_liquid_rho_kg_m3' if q=='saturated_liquid_rho' else 'psat_Pa'])
                        rows.append(o.reg.observation(params,kind,problem,observed=observed,form='difference',
                            scale=spec['relative_scales'][q]*observed,**(dict(phase='L',mass_basis=True) if kind=='phase_density' else {})))
                        weights.append(1/20)
                rows.append(cp)
                weights.append(case['lambda']/23)
            assert len(rows)==63
            coords = [o.reg.coordinate(params,[(c['family'],tuple(map(tuple,c['target'])) if isinstance(c['target'],list) else c['target'],1.)],
                origin=case['origins'][c['identity']],scale=c['scale'],bounds=tuple(c['bounds'])) for c in spec['coordinates']]
            write(directory/'targets.json',[dict(observed=r.observed,scale=r.scale,weight=w,kind=r.kind.name) for r,w in zip(rows,weights,strict=True)])
            clock, cpu = time.monotonic(), cpu_seconds()
            fitted = o.reg.fit(params,coords,rows,weights=weights,thermochemistry=thermal,
                controls=o.reg.FitControls(**dict(spec['controls'],maximum_elapsed_time_seconds=min(60.,remaining)),workers=sizing['workers_requested']))
            raw = {k:o.s._jsonable(getattr(fitted,k)) for k in ('status','message','usable','physical','initial_cost','final_cost','iterations','residual_evaluations','jacobian_evaluations','predictions','residuals','weighted_residuals','iteration_costs','iteration_seconds','trial_failures')}
            raw.update(native_wall_s=time.monotonic()-clock,cpu_s=cpu_seconds()-cpu)
            write(directory/'native-fit.json',raw)
            endpoint = o.s.with_parameter_values(mapping,dict(zip(case['origins'],raw['physical'],strict=True)))
            write(directory/'parameters.json',dict(endpoint,document_id='water-124-'+case['id'],purpose='Water-only feasibility endpoint; nothing adopted; dependent mixture coefficients and inherited coefficient provenance are historical.'))
            result = assess(endpoint,directory)
            verdict = gates(result)
            write(directory/'gates.json',verdict)
            candidates.append(dict(id=case['id'],passed=all(verdict.values()),gates=verdict,metrics=result['metrics'],physical=raw['physical']))
            print(case['id'],raw['status'],raw['physical'],verdict,elapsed(),flush=True)
            if all(verdict.values()):
                break
    finally:
        write(out/'summary.json',dict(candidates=candidates,**elapsed()))



def stage2_study(spec, out, started):
    import fit_observations as o
    import numpy as np
    assert sys.version_info[:2] == (3,13)
    prior = load(out/'summary.json') if (out/'summary.json').exists() else {}
    sizing, timing, selected = machine(spec,None), prior.get('calls',[]), []
    write(out/'machine.json',sizing)
    def elapsed():
        return dict(cpu_s=cpu_seconds()+prior.get('cpu_s',spec['prior_cpu_charge_s']),
            wall_s=time.monotonic()-started+prior.get('wall_s',spec['prior_wall_charge_s']))
    def call(mapping, case, operation, path):
        if path.exists() and not path.with_suffix('.failure.json').exists():
            return load(path)
        remaining = spec['budget_wall_s']-elapsed()['wall_s']
        if remaining<=0 or elapsed()['cpu_s']>=spec['budget_cpu_s']:
            raise RuntimeError('stage-2 allowance reached; no further call launched')
        limit = min(remaining,case['fit_wall_s'] if operation=='fit' else spec['nonfit_wall_s'])
        def child():
            try:
                write(path,o.stage2_native(spec,mapping,case,operation,sizing['workers_requested'],path))
            except Exception:
                write(path.with_suffix('.failure.json'),dict(failure=traceback.format_exc()))
        clock, cpu = time.monotonic(), cpu_seconds()
        process = multiprocessing.get_context('fork').Process(target=child)
        process.start()
        process.join(limit)
        interrupted = process.is_alive()
        if interrupted:
            process.terminate()
            process.join()
        measured = dict(path=str(path.relative_to(out)),operation=operation,cpu_s=cpu_seconds()-cpu,
            wall_s=time.monotonic()-clock,wall_limit_s=limit,interrupted=interrupted,host_load=os.getloadavg())
        timing.append(measured)
        write(out/'timing.json',dict(calls=timing,**elapsed()))
        if interrupted:
            write(path.with_suffix('.interrupted.json'),dict(unresolved='per-call wall allowance reached',**measured))
            raise RuntimeError(f'bounded call interrupted: {path}')
        if path.with_suffix('.failure.json').exists():
            raise RuntimeError(load(path.with_suffix('.failure.json'))['failure'])
        result = load(path)
        if isinstance(result,dict) and 'failure' in result:
            raise RuntimeError(result['failure'])
        return result
    def verify_rows(rows):
        for r in rows:
            e = r['equilibrium']
            if (r['status']!='Available' or not e['success'] or
                max(map(abs,e['raw_residuals']),default=0)>spec['verification']['raw_residual'] or
                any(v<=0 for v in e['dP_drho']) or e['reduced_hessian_minimum']<0):
                raise RuntimeError(f"state verification failed: {r['id']}")
    reference = load(ROOT/spec['reference_path']) if 'reference_path' in spec else o.s.stage2_reference(load(ROOT/spec['water_path']),spec)
    write(out/'reference-parameters.json',reference)
    try:
        for case in spec['cases']:
            coordinates, starts, endpoints = case.get('coordinates',[case.get('coordinate')]), [], []
            for pair in reference['pairs']:
                if [pair['component_id_a'],pair['component_id_b']]==coordinates[0]['target']:
                    pair['coefficients'].extend(case.get('additional_coefficients',[]))
            for start in case['starts']:
                values = start.get('values',[start.get('value')])
                mapping = o.s.with_parameter_values(reference,{c['identity']:v for c,v in zip(coordinates,values,strict=True) if v is not None})
                directory = out/case['id']/start['id']
                write(directory/'start-parameters.json',mapping)
                rows = call(mapping,case,'assessment',directory/'start-predictions.json')
                verify_rows(rows)
                write(directory/'start-balances.json',o.stage2_balances(spec,mapping,rows))
                starts.append((mapping,math.fsum(.5*r['weighted_residual']**2 for r in rows)))
            for start,(mapping,start_cost) in zip(case['starts'],starts,strict=True):
                directory = out/case['id']/start['id']
                raw = call(mapping,case,'fit',directory/'native-fit.json')
                complete = (raw['status']=='converged' and raw['usable'] and all(v=='Available' for v in raw['statuses'])
                    and len(raw['targets'])==case['target_count'] and len(raw['physical'])==len(coordinates)
                    and all(math.isfinite(v) for k in ('physical','predictions','weighted_residuals','optimizer_jacobian','physical_jacobian') for v in raw[k]))
                endpoint = o.s.with_parameter_values(mapping,{c['identity']:v for c,v in zip(coordinates,raw['physical'],strict=True)}) if raw['usable'] else None
                if not complete:
                    if endpoint is not None:
                        write(directory/'usable-budget-endpoint.json',endpoint)
                    write(directory/'incomplete-fit.json',dict(status=raw['status'],message=raw['message'],eligible=False))
                    raise RuntimeError(f"fit did not converge: {case['id']} {start['id']}; no further call launched")
                endpoint['purpose'] = spec['purpose']
                write(directory/'parameters.json',endpoint)
                rows = call(endpoint,case,'assessment',directory/'predictions.json')
                verify_rows(rows)
                write(directory/'balances.json',o.stage2_balances(spec,endpoint,rows))
                objective = [r for r in rows if r['weight']>0]
                cost = math.fsum(.5*r['weighted_residual']**2 for r in objective)
                delta = max(abs(r['weighted_residual']-v) for r,v in zip(objective,raw['weighted_residuals'],strict=True))
                replay = dict(cost=cost,relative_cost_difference=abs(cost-raw['final_cost'])/max(abs(cost),abs(raw['final_cost']),1e-300),
                    maximum_weighted_row_difference=delta,ids_equal=[r['id'] for r in objective]==raw['targets'],start_cost=start_cost)
                write(directory/'replay.json',replay)
                if (not replay['ids_equal'] or replay['relative_cost_difference']>spec['verification']['cost_replay_relative']
                    or delta>spec['verification']['row_replay_absolute']):
                    raise RuntimeError('candidate serialization replay failed')
                derivatives = []
                jac = np.asarray(raw['optimizer_jacobian']).reshape(-1,len(coordinates))
                for column,coordinate in enumerate(coordinates):
                    for step in spec['verification']['steps_optimizer']:
                        shifted = [call(o.s.with_parameter_values(endpoint,{coordinate['identity']:raw['physical'][column]+sign*step*coordinate['scale']}),
                            case,'residuals',directory/f'derivative-{column}-{step}-{sign}.json') for sign in (-1,1)]
                        for i,r in enumerate(objective):
                            if i and (r['quantity'],r['T_K']) in {(q['quantity'],q['T_K']) for q in objective[:i]}:
                                continue
                            fd = (shifted[1][i]['weighted_residual']-shifted[0][i]['weighted_residual'])/(2*step)
                            exact = float(jac[i,column])
                            error = abs(fd-exact)
                            derivatives.append(dict(target=r['id'],coordinate=coordinate['identity'],step_optimizer=step,centered=fd,exact=exact,
                                absolute_error=error,relative_error=error/max(abs(exact),1e-300),
                                roundoff=8*max(math.ulp(shifted[j][i]['weighted_residual']) for j in (0,1))/(2*step),
                                passed=error<=spec['verification']['derivative_absolute'] or error<=spec['verification']['derivative_relative']*abs(exact)))
                write(directory/'derivatives.json',derivatives)
                if not all(d['passed'] for d in derivatives):
                    raise RuntimeError('exact parameter derivative verification failed')
                spectrum = np.linalg.svd(jac,compute_uv=False)
                write(directory/'identification.json',dict(coordinates=coordinates,gradient=(jac.T@np.asarray(raw['weighted_residuals'])).tolist(),
                    optimizer_singular_values=spectrum.tolist(),
                    physical_singular_values=np.linalg.svd(np.asarray(raw['physical_jacobian']).reshape(jac.shape),compute_uv=False).tolist(),
                    full_condition=float(spectrum[0]/spectrum[-1]),free_condition=float(spectrum[0]/spectrum[-1]) if not raw['covariance']['active_bounds'] else None,
                    native_rank_cutoff='Engine-owned; not returned',covariance=raw['covariance']))
                write(directory/'scores.json',o.stage2_scores(rows))
                endpoints.append(dict(start=start['id'],cost=cost,k_ij=raw['physical'][0],physical=raw['physical'],path=str((directory/'parameters.json').resolve().relative_to(ROOT)),
                    sha256=hashlib.sha256((directory/'parameters.json').read_bytes()).hexdigest(),active_bounds=raw['covariance']['active_bounds']))
                print(case['id'],start['id'],endpoints[-1],elapsed(),flush=True)
            if not endpoints:
                raise RuntimeError(f"no complete converged endpoint: {case['id']}; all declared fits retained")
            chosen = min(endpoints,key=lambda e:e['cost'])
            agreement = abs(endpoints[0]['cost']-endpoints[-1]['cost'])/max(e['cost'] for e in endpoints)
            passed = chosen['cost']<=min(c for _,c in starts)
            selected.append(dict(case=case['id'],passed=passed,selected=chosen,endpoints=endpoints,
                start_relative_cost_difference=agreement,start_agreement=agreement<=spec['verification']['start_cost_relative'],
                provisional=case['id']=='co2-water',diagnostic=case.get('diagnostic',False)))
            write(out/'selection.json',selected)
            if not passed:
                raise RuntimeError('endpoint cost exceeds better same-basis start')
            reference = load(ROOT/chosen['path'])
    finally:
        write(out/'summary.json',dict(selected=selected,completed=len(selected)==len(spec['cases']),calls=timing,**elapsed()))


def run(spec_path, output_dir, *, case_ids, operation):
    started = COMMAND_STARTED if __name__ == '__main__' else time.monotonic()
    if operation not in ('fit','replay') or not case_ids:
        raise ValueError('explicit fit/replay operation and case IDs required')
    spec_path, out = Path(spec_path), Path(output_dir).resolve()
    resume_stage2 = load(spec_path).get('study')=='joint-recalibration-170' and operation=='fit' and case_ids==['stage2']
    if out.exists() and resume_stage2 and (out/'spec.json').read_bytes()!=spec_path.read_bytes():
        raise ValueError('stage-2 continuation requires the identical frozen declaration')
    out.mkdir(parents=True, exist_ok=resume_stage2)
    (out/'spec.json').write_bytes(spec_path.read_bytes())
    spec = load(spec_path)
    timing = []
    try:
        write(out/'inputs.json',verify(spec))
        import fit_observations as o
        if spec.get('study') == 'joint-recalibration-170' and operation=='fit' and case_ids==['stage2']:
            stage2_study(spec,out,started)
            return out
        if spec.get('study') == 'water-124' and operation=='fit' and case_ids==['water-124']:
            water_study(spec,out,started)
            return out
        if operation == 'replay':
            declared = o.indexed(spec['replay'],'id')
            for identity in case_ids:
                entry = declared[identity]
                directory = out/'replay'/identity
                mapping = load(checked(entry['parameters_path'],entry['sha256']))
                _, rows = o.rows_for(spec,mapping,entry['observations'])
                clock = time.monotonic()
                values = o.replay(mapping,rows)
                native_wall = time.monotonic()-clock
                write(directory/'predictions.json',values)
                summary = o.replay_summary(values,o.load(spec['heat_rows_path']))
                write(directory/'summary.json',summary)
                delta = differences(load(checked(entry['reference_path'],entry['reference_sha256'])),values)
                delta += differences(load(checked(entry['summary_path'],entry['summary_sha256'])),summary,'summary')
                comparison = replay_comparison(delta,entry.get('residual_comparison'))
                comparison.update(native_wall_s=native_wall,command_wall_s=time.monotonic()-started)
                write(directory/'comparison.json',comparison)
                if not comparison['passed']:
                    raise RuntimeError('replay mismatch; see comparison.json')
            return out
        available = {c['id'] for c in spec['cases']} | {c['id']+'-'+s['id'] for c in spec['cases'] for s in c['starts']}
        if set(case_ids)-available:
            raise ValueError(f'unknown case IDs: {set(case_ids)-available}')
        for case in spec['cases']:
            for start in case['starts']:
                name = case['id']+'-'+start['id']
                if case['id'] not in case_ids and name not in case_ids:
                    continue
                directory = out/case['id']/start['id']
                case_started = started if not timing else time.monotonic()
                row = dict(case=case['id'],start=start['id'],native_wall_s=None,cpu_s=None)
                timing.append(row)
                try:
                    mapping, params, rows, declared = resolve(spec,case,start)
                    write(directory/'start-parameters.json',mapping)
                    write(directory/'targets.json',[dict(target=i,observed=x.observed,scale=x.scale,weight=w,form=x.form.name) for i,x,w in rows])
                    row.update(machine(spec,case.get('reproduction_workers')))
                    coords = []
                    for c in declared:
                        parts = c['identity'].split('/')
                        target = parts[1] if parts[0]=='component' else tuple(parts[1:3])
                        coords.append(o.reg.coordinate(params,[(c['family'],target,1.)],origin=c['origin'][start['id']],
                            scale=c['scale'],bounds=tuple(c['bounds'])))
                    controls = o.reg.FitControls(**spec['controls'],workers=row['workers_requested'])
                    before = cpu_seconds()
                    clock = time.monotonic()
                    fitted = o.reg.fit(params,coords,[r[1] for r in rows],weights=[r[2] for r in rows],
                        controls=controls,thermochemistry=o.thermal.record())
                    row.update(native_wall_s=time.monotonic()-clock,cpu_s=cpu_seconds()-before,
                        iterations=fitted.iterations,residual_evaluations=fitted.residual_evaluations,jacobian_evaluations=fitted.jacobian_evaluations)
                    row.update(amortized_s_per_residual_evaluation_including_Jacobian_work=row['native_wall_s']/fitted.residual_evaluations if fitted.residual_evaluations else None,
                        amortized_reason='' if fitted.residual_evaluations else 'zero residual evaluations',
                        F1_native_wall_le_120_s=row['native_wall_s']<=120 if case['variant']['problem']=='F1' else None,
                        F1_excess_s=max(0.,row['native_wall_s']-120) if case['variant']['problem']=='F1' else None)
                    ids = [c['identity'] for c in declared]
                    fields = ('status','message','usable','initial_cost','final_cost','physical','predictions','residuals',
                        'weighted_residuals','optimizer_jacobian','physical_jacobian','iterations','iteration_costs','iteration_seconds',
                        'trial_failures','residual_evaluations','jacobian_evaluations')
                    raw = {k:o.s._jsonable(getattr(fitted,k)) for k in fields}
                    raw.update(coordinates=ids,scales=[c['scale'] for c in declared],start={c['identity']:c['origin'][start['id']] for c in declared},
                        targets=[r[0] for r in rows],observed=[r[1].observed for r in rows],active_bounds=list(fitted.covariance.active_bounds),
                        observation_statuses=[v.name for v in fitted.statuses],
                        covariance={k:o.s._jsonable(getattr(fitted.covariance,k)) for k in
                            ('status','assumption','rank','singular_values','physical','variance_factor','active_bounds')},
                        failures=[dict(trial=f.trial,observation=f.observation,status=f.status.name,message=f.message,jacobian=f.jacobian) for f in fitted.failures])
                    complete = (raw['status']=='converged' and raw['usable'] and len(raw['predictions'])==len(rows)
                        and len(raw['physical'])==len(declared)
                        and all(len(raw[k])==len(rows) for k in ('residuals','weighted_residuals','observation_statuses'))
                        and all(len(raw[k])==len(rows)*len(declared) for k in ('optimizer_jacobian','physical_jacobian'))
                        and all(v=='Available' for v in raw['observation_statuses'])
                        and all(math.isfinite(v) for k in ('physical','predictions','weighted_residuals','optimizer_jacobian','physical_jacobian') for v in raw[k])
                        and math.isfinite(raw['final_cost']))
                    raw['selection_eligible'] = complete
                    write(directory/'native-fit.json',raw)
                    if complete:
                        final = o.s.with_parameter_values(mapping,dict(zip(ids,raw['physical'],strict=True)))
                        final['purpose'] = 'Declared campaign endpoint; no parameter adoption or physical validation.'
                        write(directory/'parameters.json',final)
                    else:
                        if raw['usable']:
                            write(directory/'usable-budget-endpoint.json',o.s.with_parameter_values(mapping,dict(zip(ids,raw['physical'],strict=True))))
                        raise RuntimeError(f"incomplete fit: {raw['status']}: {raw['message']}")
                    (directory/'execution.log').write_text(f"{name}: {raw['status']}; cost={raw['final_cost']}; native wall={row['native_wall_s']} s\n")
                    print(name,row,flush=True)
                except Exception:
                    row['failure'] = traceback.format_exc()
                    directory.mkdir(parents=True,exist_ok=True)
                    (directory/'execution.log').write_text(row['failure'])
                    raise
                finally:
                    row['command_wall_s'] = time.monotonic()-case_started
    except Exception:
        write(out/'failure.json',dict(cause=traceback.format_exc()))
        raise
    finally:
        if timing:
            with (out/'timing.csv').open('w',newline='') as stream:
                writer = csv.DictWriter(stream,list(dict.fromkeys(k for row in timing for k in row)),lineterminator='\n')
                writer.writeheader()
                writer.writerows(timing)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('spec',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--operation',choices=('fit','replay'),required=True)
    parser.add_argument('--case',action='append',required=True)
    args = parser.parse_args()
    run(args.spec,args.output,case_ids=args.case,operation=args.operation)
