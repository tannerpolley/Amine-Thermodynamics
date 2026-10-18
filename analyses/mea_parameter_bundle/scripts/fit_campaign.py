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
        return dict(cpu_s=cpu_seconds()+spec['prior_cpu_charge_s'],wall_s=time.monotonic()-started+spec['prior_wall_charge_s'])
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



def fitted_parameter_values(coordinates, physical):
    coordinates = sorted(coordinates, key=lambda c: 'reaction' in c)
    targets = [(c['identity'],c.get('source_to_native_factor',1.))
        for c in coordinates]
    targets = [target for c,primary in zip(coordinates,targets,strict=True)
        for target in [primary,*[(tie['identity'],1.) for tie in c.get('ties',[])]]]
    return {identity:value/factor for (identity,factor),value in zip(targets,physical,strict=True)}


def stage5_study(spec, out, started):
    """Yang Eqs. 1a/2a/2b reduction on Agieienko ESI Tables S1/S2."""
    import fit_observations as o
    import numpy as np
    reference = load(ROOT/spec['reference_path'])
    template = load(ROOT/spec['dielectric_template_path'])
    rows = list(csv.DictReader((ROOT/spec['dielectric_rows_path']).open()))
    assert len(rows) == 14
    model = o.epcsaft.Mixture(o.epcsaft.Parameters.from_mapping(reference))
    masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in reference['components']}
    compositions, density, fractions = [], [], []
    for row in rows:
        w = float(row['MEA_wt_percent'])/100
        amounts = {'monoethanolamine':w/masses['monoethanolamine'], 'water':(1-w)/masses['water']}
        x = {k:v/sum(amounts.values()) for k,v in amounts.items()}
        state = model.state(298.15,P=101325.,x=x,phase='liquid')
        assert state.pressure_density_derivative > 0
        compositions.append(x)
        density.append(state.molar_density/1000)
        fractions.append(x['monoethanolamine'])
        row.update(native_density_mol_L=density[-1],native_density_kg_m3=state.molar_density*sum(x[k]*masses[k] for k in x),
            native_pressure_Pa=state.pressure,dP_drho=state.pressure_density_derivative,
            measured_density_kg_m3=1000*float(row['density_g_cm3']))
    A, C, T = .3777, 1403., 298.15
    K, x, rho = C/T-1, np.array(fractions), np.array(density)
    observed = np.array([float(r['epsilon_s']) for r in rows])
    scale = .01*observed
    H = np.column_stack((rho*x,rho*x*x))/scale[:,None]
    q, _, rank, singular = np.linalg.lstsq(H,(observed-1-rho*A*K)/scale,rcond=None)
    def roots(coefficients):
        discriminant = coefficients[0]**2-4*K*A*coefficients[1]
        assert discriminant > 0, 'distinct real dielectric roots required'
        u = (coefficients[0]+np.array([-1,1])*np.sqrt(discriminant))/(2*K)
        pairs = [(float(A+b),float(C+T*(coefficients[0]-K*b)/A)) for b in u]
        assert all(v>0 and t>393.15 for v,t in pairs), 'inadmissible dielectric root'
        return float(discriminant), pairs
    delta, pairs = roots(q)
    assert rank == 2
    covariance = np.linalg.inv(H.T@H)
    predicted = 1+rho*(A*K+q[0]*x+q[1]*x*x)
    result = dict(q=q.tolist(),rank=int(rank),singular_values=singular.tolist(),condition=float(singular[0]/singular[-1]),
        discriminant=delta,scale_covariance=covariance.tolist(),cost=float(.5*np.sum(((predicted-observed)/scale)**2)),branches=[],sensitivity=[])
    for factor in (.99,1.01):
        shifted = np.linalg.lstsq(H,(factor*observed-1-rho*A*K)/scale,rcond=None)[0]
        disc, values = roots(shifted)
        result['sensitivity'].append(dict(coherent_permittivity_factor=factor,q=shifted.tolist(),discriminant=disc,pairs=values))
    for label,(volume,temperature) in zip(('smaller-dV','larger-dV'),pairs,strict=True):
        mapping = json.loads(json.dumps(reference))
        next(f for f in mapping['model_families'] if f['kind']=='permittivity')['choice'] = 'solvent-density-temperature'
        mapping['correlations'] = [r for r in mapping['correlations'] if r['family']!='relative_permittivity']
        for component,source in zip(mapping['components'],template['components'],strict=True):
            assert component['component_id'] == source['component_id']
            component['coefficients'] = [r for r in component['coefficients'] if r['family']!='relative_permittivity']
            component['coefficients'].extend(json.loads(json.dumps(r)) for r in source['coefficients'] if r['family'] in ('dielectric_volume','dielectric_temperature'))
        mapping = o.s.with_parameter_values(mapping,{'component/monoethanolamine/dielectric_volume':volume,'component/monoethanolamine/dielectric_temperature':temperature})
        mapping['sources'].append(dict(source_id='joint-recalibration-170-stage5',citation='Yang2024 Eqs.1a/2a/2b Table6; AgieienkoBuchner2024 ESI S1/S2',use_basis=spec['purpose']))
        for node in o.s._identified(mapping):
            if node.get('family') in ('dielectric_volume','dielectric_temperature'):
                node['provenance'].update(source_id='joint-recalibration-170-stage5',locator=spec['dielectric_rows_path']+'; fixed Yang water and assumed CO2 pair; MEA pair from reduction.json')
        mapping.update(document_id='joint-recalibration-170-stage5-'+label,purpose=spec['purpose'])
        native = o.epcsaft.Mixture(o.epcsaft.Parameters.from_mapping(mapping))
        replay = np.array([native.state(T,rho=density[i]*1000,x=composition).bulk_relative_permittivity for i,composition in enumerate(compositions)])
        error = float(np.max(np.abs(replay-predicted)))
        u, v = volume-A, temperature-C
        transform = np.linalg.inv(np.array([[K,A/T],[v/T,u/T]]))
        path = out/('parameters.json' if label=='smaller-dV' else 'larger-dV-parameters.json')
        write(path,mapping)
        result['branches'].append(dict(branch=label,dielectric_volume_L_mol=volume,dielectric_temperature_K=temperature,
            max_abs_native_replay_epsilon=error,scale_covariance_dV_dT=(transform@covariance@transform.T).tolist(),path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        for i,row in enumerate(rows):
            row.update(derived_MEA_mole_fraction=float(x[i]),reduced_epsilon=float(predicted[i]),residual_epsilon=float(predicted[i]-observed[i]),weighted_residual=float((predicted[i]-observed[i])/scale[i]))
            row[label+'_epsilon'] = float(replay[i])
        assert error <= 1e-10, 'native dielectric replay failed'
    write(out/'rows.json',rows)
    write(out/'reduction.json',result)
    write(out/'timing.json',dict(cpu_s=cpu_seconds(),wall_s=time.monotonic()-started))
    print(result,flush=True)


def stage2_study(spec, out, started):
    import fit_observations as o
    import numpy as np
    assert sys.version_info[:2] == (3,13)
    prior = load(out/'summary.json') if (out/'summary.json').exists() else {}
    sizing, timing, selected = machine(spec,None), prior.get('calls',[]), []
    write(out/'machine.json',sizing)
    def elapsed():
        cpu = cpu_seconds()+prior.get('cpu_s',spec['prior_cpu_charge_s'])
        wall = time.monotonic()-started+prior.get('wall_s',spec['prior_wall_charge_s'])
        return dict(cpu_s=cpu,wall_s=wall,
            cumulative_cpu_s=spec.get('program_prior_cpu_s',0.)+cpu,
            cumulative_wall_s=spec.get('program_prior_wall_s',0.)+wall,
            remaining_cpu_s=spec.get('program_cpu_limit_s',144000.)-spec.get('program_prior_cpu_s',0.)-cpu,
            remaining_wall_s=spec.get('program_wall_limit_s',21600.)-spec.get('program_prior_wall_s',0.)-wall)
    def call(mapping, case, operation, path):
        if path.exists() and not path.with_suffix('.failure.json').exists():
            return load(path)
        remaining = spec['budget_wall_s']-elapsed()['wall_s']
        remaining = min(remaining,elapsed()['remaining_wall_s'])
        if remaining<=0 or elapsed()['cpu_s']>=spec['budget_cpu_s'] or elapsed()['remaining_cpu_s']<=0:
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
    if spec['stage']==2:
        write(out/'reference-parameters.json',reference)
    def parameter_record(mapping, coordinates, values):
        updates = {}
        for coordinate,value in zip(coordinates,values,strict=True):
            updates[coordinate['identity']] = value
            updates.update({tie['identity']:tie['factor']*value for tie in coordinate.get('ties',[])})
        return o.s.with_parameter_values(mapping,updates)
    write(out/'entry-accounting.json',elapsed())
    try:
        for case in spec['cases']:
            coordinates, starts, endpoints = case.get('coordinates',[case.get('coordinate')]), [], []
            for pair in reference['pairs']:
                if [pair['component_id_a'],pair['component_id_b']]==coordinates[0].get('target'):
                    pair['coefficients'].extend(case.get('additional_coefficients',[]))
            for start in case['starts']:
                values = start.get('values',[start.get('value')])
                mapping = parameter_record(reference,coordinates,values)
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
                    and len(raw['targets'])==case['target_count'] and len(raw['physical'])==sum(1+len(c.get('ties',[])) for c in coordinates)
                    and all(math.isfinite(v) for k in ('physical','predictions','weighted_residuals','optimizer_jacobian','physical_jacobian') for v in raw[k]))
                endpoint = o.s.with_parameter_values(mapping,fitted_parameter_values(coordinates,raw['physical'])) if raw['usable'] else None
                if raw['usable']:
                    jac = np.asarray(raw['optimizer_jacobian']).reshape(-1,len(coordinates))
                    active = raw['covariance']['active_bounds']
                    free = [j for j in range(len(coordinates)) if j not in active]
                    spectra = [np.linalg.svd(matrix,compute_uv=False) for matrix in (jac,jac[:,free])]
                    write(directory/'identification.json',dict(coordinates=coordinates,
                        gradient=(jac.T@np.asarray(raw['weighted_residuals'])).tolist(),
                        optimizer_singular_values=spectra[0].tolist(),free_optimizer_singular_values=spectra[1].tolist(),
                        physical_singular_values=np.linalg.svd(np.asarray(raw['physical_jacobian']).reshape(len(raw['targets']),len(raw['physical'])),compute_uv=False).tolist(),
                        full_rank=int(np.count_nonzero(spectra[0]>1e-14*spectra[0][0])),
                        free_rank=int(np.count_nonzero(spectra[1]>1e-14*spectra[1][0])) if free else 0,
                        full_condition=float(spectra[0][0]/spectra[0][-1]) if spectra[0][-1]>0 else None,
                        free_condition=float(spectra[1][0]/spectra[1][-1]) if free and spectra[1][-1]>0 else None,
                        rank_relative_cutoff=1e-14,covariance=raw['covariance']))
                if not complete:
                    if endpoint is not None:
                        write(directory/'usable-budget-endpoint.json',endpoint)
                    write(directory/'incomplete-fit.json',dict(status=raw['status'],message=raw['message'],eligible=False))
                    raise RuntimeError(f"fit did not converge: {case['id']} {start['id']}; no further call launched")
                endpoint['purpose'] = spec['purpose']
                write(directory/'parameters.json',endpoint)
                if raw['covariance']['rank']<len(coordinates) or raw['covariance']['active_bounds']:
                    raise RuntimeError('rank-deficient or bound-limited endpoint; no further call launched')
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
                        factor = coordinate.get('source_to_native_factor',1.)
                        shifted = [call(parameter_record(endpoint,[coordinate],[o.s.parameter_values(endpoint)[coordinate['identity']]+sign*step*coordinate['scale']*math.copysign(1.,factor)]),
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


def stage6_study(spec, out, started):
    """Amendment 2 information checks or one explicitly declared joint fit."""
    import fit_observations as o
    import numpy as np
    sizing = machine(spec, spec.get('workers'))
    write(out/'machine.json', sizing)
    reports, calls = [], []
    fit_case = spec.get('fit_case')
    if fit_case:
        release = load(checked(spec['release_tests_path'], spec['release_tests_sha256']))
        assert any(r['start']==fit_case['start'] for r in release) and all(r['mandatory_passed'] and r['dispersion_release_passed'] for r in release)
    def elapsed():
        cpu = cpu_seconds()+spec['prior_cpu_charge_s']
        wall = time.monotonic()-started+spec['prior_wall_charge_s']
        return dict(cpu_s=cpu, wall_s=wall, cumulative_cpu_s=spec['program_prior_cpu_s']+cpu,
            cumulative_wall_s=spec['program_prior_wall_s']+wall)
    def spectrum(matrix):
        _, sv, vh = np.linalg.svd(matrix, full_matrices=False)
        return dict(columns=matrix.shape[1], rank=int(sum(sv>sv[0]*1e-14)),
            condition=float(sv[0]/sv[-1]) if sv[-1]>0 else None,
            singular_values=sv.tolist(), weakest_direction=vh[-1].tolist())
    try:
        for start in spec['information_starts']:
            if fit_case and start['id']!=fit_case['start']:
                continue
            mapping = load(checked(start['parameters_path'], start['sha256']))
            directory = out if fit_case else out/'information'/start['id']
            path = directory/'native.json'
            cpu_limit = spec['fit_cpu_s'] if fit_case else spec['nonfit_cpu_s']
            wall_limit = spec['fit_wall_s'] if fit_case else spec['nonfit_wall_s']
            guard_wall_limit = wall_limit + (120 if fit_case else 0)
            remaining_cpu = min(spec['budget_cpu_s']-elapsed()['cpu_s'],
                spec['program_cpu_limit_s']-elapsed()['cumulative_cpu_s'])
            remaining_wall = min(spec['budget_wall_s']-elapsed()['wall_s'],
                spec['program_wall_limit_s']-elapsed()['cumulative_wall_s'])
            if remaining_cpu<cpu_limit or remaining_wall<guard_wall_limit:
                raise RuntimeError('allowance insufficient for the next bounded information call')
            def child():
                try:
                    params, rows = o.stage6_rows(spec, mapping)
                    coordinates, values = [], o.s.parameter_values(mapping)
                    for c in spec['information_coordinates']:
                        factor = c.get('source_to_native_factor', 1.)
                        origin = 0. if c.get('enthalpy_shift') else factor*values[c['identity']]
                        kw = dict(origin=origin, scale=abs(factor)*c['scale'],
                            bounds=tuple(sorted(factor*b for b in c['bounds'])))
                        coordinates.append(o.reg.reaction_enthalpy_shift(c['reaction'], pivot_temperature=313.15, **kw)
                            if c.get('enthalpy_shift') else o.reg.reaction_coordinate(c['reaction'], c['coefficient'], **kw)
                            if 'reaction' in c else o.reg.coordinate(params, [(t['family'],
                                tuple(t['target']) if isinstance(t['target'], list) else t['target'], t.get('factor', 1.))
                                for t in c.get('targets', [dict(family=c.get('family'), target=c.get('target'))])], **kw))
                    if fit_case:
                        rows = [(dict(r, weight=fit_case['density_weight']/12) if r['quantity']=='phase_density' else r, item) for r,item in rows]
                        rows = [(r,item) for r,item in rows if r['weight']>0]
                        v = o.reg.fit(params, coordinates, [item for _,item in rows], weights=[r['weight'] for r,_ in rows],
                            thermochemistry=o.thermal.record(), controls=o.reg.FitControls(**spec['controls'],
                                workers=sizing['workers_requested'], maximum_elapsed_time_seconds=wall_limit), singular_vectors=True)
                        raw = {k:o.s._jsonable(getattr(v,k)) for k in ('status','message','usable','initial_cost','final_cost','physical',
                            'optimizer','predictions','residuals','weighted_residuals','optimizer_jacobian','physical_jacobian','iterations',
                            'iteration_costs','iteration_seconds','trial_failures','residual_evaluations','jacobian_evaluations')}
                        raw.update(rows=[r for r,_ in rows], statuses=[s.name for s in v.statuses],
                            covariance={k:o.s._jsonable(getattr(v.covariance,k)) for k in ('status','assumption','rank','singular_values',
                                'physical','optimizer','variance_factor','active_bounds','projected_gradient_norm','left_vectors','right_vectors')},
                            failures=[dict(trial=f.trial,observation=f.observation,status=f.status.name,message=f.message,jacobian=f.jacobian) for f in v.failures])
                        write(path, raw)
                        if v.usable:
                            ordinary = [c for c in spec['information_coordinates'] if 'reaction' not in c]
                            updates = fitted_parameter_values(ordinary, v.physical[:len(v.chart.active)])
                            for name,law in v.chart.reaction_laws.items():
                                fields = dict(zip(('a_k','b','c_per_k'), o.reg.reaction_log10_reciprocal(law), strict=True)) if name=='R5' else dict(a=law.a,b_k=law.b,c=law.c,d_per_k=law.d)
                                updates.update({f'reaction:{name}:correlation:{k}':val for k,val in fields.items()})
                            write(directory/'usable-budget-endpoint.json', o.s.with_parameter_values(mapping, updates))
                            write(directory/'chemistry-coordinates.json', dict(R5_unshifted_a_k=values['reaction:R5:correlation:a_k']-80*v.optimizer[9],
                                enthalpy_shifts_J_mol={c['reaction']:c['scale']*v.optimizer[i] for i,c in enumerate(spec['information_coordinates']) if c.get('enthalpy_shift')}))
                        return
                    v = o.reg.differentiate(params, coordinates, [item for _, item in rows],
                        optimizer=[0.]*len(coordinates), thermochemistry=o.thermal.record())
                    write(path, dict(rows=[r for r, _ in rows], predictions=list(v.predictions),
                        statuses=[s.name for s in v.statuses], residuals=[math.log(p/r['observed'])
                            if r['form'] in ('LogRatio','log_ratio') else (p-r['observed'])/r['scale']
                            for p,(r,_) in zip(v.predictions,rows,strict=True)],
                        residual_optimizer_gradient=list(v.residual_optimizer_gradient)))
                except Exception:
                    write(directory/'failure.json', dict(cause=traceback.format_exc()))
            clock, cpu = time.monotonic(), cpu_seconds()
            process = multiprocessing.get_context('fork').Process(target=child)
            process.start()
            process.join(guard_wall_limit)
            interrupted = process.is_alive()
            if interrupted:
                process.terminate()
                process.join(60)
                if process.is_alive():
                    process.kill()
                    process.join()
            calls.append(dict(start=start['id'], cpu_s=cpu_seconds()-cpu,
                wall_s=time.monotonic()-clock, exitcode=process.exitcode, interrupted=interrupted, host_load=os.getloadavg()))
            write(out/'timing.json', dict(calls=calls, **elapsed()))
            if interrupted or process.exitcode or (directory/'failure.json').exists():
                if fit_case:
                    write(directory/'incomplete-fit.json', dict(case=fit_case, endpoint_available=False,
                        reason='bounded call interrupted' if interrupted else 'child call failed', call=calls[-1]))
                raise RuntimeError(f'bounded call failed: {directory}; no subsequent fit launched')
            raw = load(path)
            if fit_case:
                if calls[-1]['cpu_s']>cpu_limit:
                    raise RuntimeError('aggregate fit CPU ceiling exceeded; return to owner before another fit')
                if raw['status']!='converged' or raw['covariance']['rank']<len(spec['information_coordinates']):
                    raise RuntimeError('nonconverged or rank-deficient joint fit; return to owner before another fit')
                return
            if raw['statuses']!=['Available']*len(raw['rows']) or not all(math.isfinite(x) for key in
                ('predictions','residuals','residual_optimizer_gradient') for x in raw[key]):
                raise RuntimeError(f'unavailable or nonfinite information row: {directory}; no fit launched')
            coordinates = spec['information_coordinates']
            values = o.s.parameter_values(mapping)
            mandatory_count = len(coordinates)-2
            active = [i for i,c in enumerate(coordinates) if values.get(c['identity'],0.) in c['bounds']]
            for density_weight in spec['information_density_weights']:
                weights = np.array([density_weight/12 if r['quantity']=='phase_density' else r['weight'] for r in raw['rows']])
                keep = weights>0
                J = np.array(raw['residual_optimizer_gradient']).reshape(len(raw['rows']),len(coordinates))[keep]*np.sqrt(weights[keep,None])
                free = [j for j in range(mandatory_count) if j not in active]
                mandatory = spectrum(J[:,free])
                u, sv, _ = np.linalg.svd(J[:,free], full_matrices=False)
                u = u[:,sv>sv[0]*1e-14]
                projected = spectrum(J[:,mandatory_count:] - u@(u.T@J[:,mandatory_count:]))
                augmented = spectrum(J[:,free+list(range(mandatory_count,len(coordinates)))])
                passed = mandatory['rank']==len(free) and mandatory['condition'] is not None and mandatory['condition']<=1e4
                release = (passed and not any(j in active for j in range(mandatory_count,len(coordinates))) and augmented['rank']==len(free)+2
                    and augmented['condition'] is not None and augmented['condition']<=1e4
                    and projected['rank']==2 and projected['condition'] is not None and projected['condition']<=1e4)
                record = dict(start=start['id'], density_weight=density_weight, row_count=int(sum(keep)),
                    full=spectrum(J[:,:mandatory_count]), mandatory_free=mandatory, augmented_free=augmented,
                    projected_dispersions=projected, active_columns=active, free_columns=free,
                    mandatory_passed=passed, dispersion_release_passed=release)
                reports.append(record)
                write(directory/f'lambda-{density_weight}.json', dict(record, row_ids=[r['id'] for r,k in zip(raw['rows'],keep) if k],
                    weighted_optimizer_jacobian=J.tolist(), weighted_residuals=(np.array(raw['residuals'])[keep]*np.sqrt(weights[keep])).tolist()))
                write(out/'release-tests.json', reports)
                print(record, flush=True)
            if not all(r['mandatory_passed'] and r['dispersion_release_passed'] for r in reports):
                raise RuntimeError('mandatory chemistry/ion block fails conditioning; return to owner before another start or fit')
    finally:
        write(out/'summary.json', dict(release_tests=reports, calls=calls, fit_calls=int(bool(fit_case)), **elapsed()))


def run(spec_path, output_dir, *, case_ids, operation):
    started = COMMAND_STARTED if __name__ == '__main__' else time.monotonic()
    if operation not in ('fit','replay','information') or not case_ids:
        raise ValueError('explicit fit/replay operation and case IDs required')
    spec_path, out = Path(spec_path), Path(output_dir).resolve()
    declaration = load(spec_path)
    resume_stage2 = declaration.get('study')=='joint-recalibration-170' and operation in ('fit','information') and case_ids==[f"stage{declaration['stage']}"]
    frozen_spec = out/('stage'+str(declaration['stage'])+'-spec.json' if resume_stage2 and declaration['stage']!=2 else 'spec.json')
    if frozen_spec.exists() and resume_stage2 and frozen_spec.read_bytes()!=spec_path.read_bytes():
        raise ValueError('stage-2 continuation requires the identical frozen declaration')
    out.mkdir(parents=True, exist_ok=resume_stage2)
    frozen_spec.write_bytes(spec_path.read_bytes())
    spec = load(spec_path)
    timing = []
    try:
        write(out/'inputs.json',verify(spec))
        import fit_observations as o
        if operation in ('information','fit') and spec.get('stage')==6 and case_ids==['stage6']:
            stage6_study(spec,out,started)
            return out
        if spec.get('study') == 'joint-recalibration-170' and operation=='fit' and case_ids==[f"stage{spec['stage']}"]:
            (stage5_study if spec['stage']==5 else stage2_study)(spec,out,started)
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
                clock, before = time.monotonic(), cpu_seconds()
                values = o.replay(mapping,rows)
                native_wall = time.monotonic()-clock
                write(directory/'predictions.json',values)
                summary = o.replay_summary(values,o.load(spec['heat_rows_path']))
                write(directory/'summary.json',summary)
                delta = differences(load(checked(entry['reference_path'],entry['reference_sha256'])),values)
                delta += differences(load(checked(entry['summary_path'],entry['summary_sha256'])),summary,'summary')
                comparison = replay_comparison(delta,entry.get('residual_comparison'))
                if 'verification' in entry:
                    expected = load(ROOT/entry['reference_path'])
                    prior_summary = load(ROOT/entry['summary_path'])
                    same_rows = len(values)==len(expected) and all(
                        all(a[k]==b[k] for k in ('target','observed','scale','weight','form','status'))
                        for a,b in zip(expected,values))
                    row_differences = [dict(target=a['target'],expected=a['weighted_residual'],actual=b['weighted_residual'],
                        difference=b['weighted_residual']-a['weighted_residual']) for a,b in zip(expected,values)]
                    relative = abs(summary['cost']-prior_summary['cost'])/abs(prior_summary['cost'])
                    maximum = max(abs(r['difference']) for r in row_differences)
                    policy = entry['verification']
                    comparison = dict(passed=same_rows and relative<=policy['cost_replay_relative'] and
                        maximum<=policy['row_replay_absolute'],identical_definitions=same_rows,
                        relative_cost_difference=relative,maximum_weighted_row_difference=maximum,
                        expected_summary=prior_summary,actual_summary=summary,rows=row_differences,limits=policy)
                comparison.update(native_wall_s=native_wall,command_wall_s=time.monotonic()-started)
                comparison.update(cpu_s=cpu_seconds()-before,host_load=os.getloadavg())
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
    parser.add_argument('--operation',choices=('fit','replay','information'),required=True)
    parser.add_argument('--case',action='append',required=True)
    args = parser.parse_args()
    run(args.spec,args.output,case_ids=args.case,operation=args.operation)
