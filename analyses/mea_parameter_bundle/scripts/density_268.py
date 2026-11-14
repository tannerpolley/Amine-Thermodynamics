"""Density comparisons and local parameter probes for issue 268; no adoption."""
# ruff: noqa: E402 -- set numerical-library threads before importing Engine.
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import zipfile

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'analyses/mea_parameter_bundle'
AN = ROOT / 'analyses/solvent_specification_mea'
OUT = B / 'results/density-268'
sys.path.insert(0, str(Path(__file__).parent))
import shared_evaluation as s

OLD_SHA = s.ENGINE_WHEEL_SHA256
NEW_SHA = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
WHEELS = {OLD_SHA: ROOT / 'build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl',
          NEW_SHA: Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')}
CHAIN = B / 'results/engine-3e83e19c-refit-chain'
STARTS = {'final': B / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json', 'wide': CHAIN / 'a6/run/fit/usable-budget-endpoint.json'}
SHA = None
def read(path):
    return json.loads(Path(path).read_text())
def write(path, value):
    path = OUT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(wheel_sha256=SHA, result=jsonable(value))
    data = (json.dumps(payload, indent=2, allow_nan=False) + '\n').encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)
def verify():
    global SHA
    for digest, path in WHEELS.items():
        if not path.exists():
            continue
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        with zipfile.ZipFile(path) as archive:
            if all(archive.read(n) == (Path(epcsaft.__file__).parent.parent / n).read_bytes()
                   for n in archive.namelist() if n.startswith('epcsaft/') and not n.endswith('/')):
                SHA = digest
                # Owner-authorized wheel for this process; repository defaults stay pinned.
                s.ENGINE_WHEEL_SHA256 = digest
                s.ENGINE_COMMIT = 'e6dae5c7' if digest == NEW_SHA else '3e83e19ccc771b51d8ebc038931ab25192f4c5b5'
                return
    raise RuntimeError('Installed Engine differs from both authorized immutable wheels')
def bind(mapping, specification='MEA-pre-260-340.toml'):
    spec = SolventSpecification(AN / specification)
    spec.parameters = epcsaft.Parameters.from_mapping(mapping)
    spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
    packet = s.load_state_packet()['observations'][0]['request']
    request = s.corrected_request(packet, s.reaction_values(mapping), mapping=mapping)
    laws = {r.name: r.correlation for r in s._problem_from_request(request).reactions}
    fields = ('a', 'b', 'c', 'd', 'e', 'f', 'reference_temperature')
    for problem in spec.problems.values():
        for reaction in problem.reactions:
            old = reaction.correlation
            reaction.correlation = eq.ReactionLogPolynomial(**{k: getattr(laws[reaction.name], k) for k in fields},
                temperature_min=old.temperature_min, temperature_max=old.temperature_max, standard_state_id=old.standard_state_id)
    for group in spec.spec['chemistry']['reactions'].values():
        for reaction in group:
            reaction['correlation'].update({k: getattr(laws[reaction['name']], k) for k in fields})
    return spec
def evaluate(spec, records):
    values = [spec.prediction(r) for r in records]
    for r, v in zip(records, values, strict=True):
        if v['status'] == 'Available' and v['requested_tolerance_met']:
            v['weighted_residual'] = math.sqrt(r['weight']) * v['residual']
            v['cost'] = .5 * v['weighted_residual'] ** 2
    return values
def check(values):
    assert all(v['status'] == 'Available' and v.get('requested_tolerance_met') and
               all(math.isfinite(v[k]) for k in ('value', 'residual')) for v in values), [v for v in values if v['status'] != 'Available']
def coordinates(spec, name):
    historical = read(CHAIN / ('restricted-2/attempt-3/spec.json' if name == 'final' else 'a6/spec.json'))
    mapping = read(STARTS[name])
    values, result = s.parameter_values(mapping), []
    shifts = read(STARTS[name].parent / 'chemistry-coordinates.json')['enthalpy_shifts_J_mol'] if name == 'wide' else {'R2': -1363.931574116721, 'R5': 10000.}
    for q in historical['information_coordinates']:
        scale, bounds = q['scale'], q['bounds']
        if 'coefficient' in q:
            scale *= abs(q['source_to_native_factor'])
            bounds = sorted(v * q['source_to_native_factor'] for v in bounds)
            origin = next(r['correlation'][q['coefficient']] for r in spec.spec['chemistry']['reactions']['aqueous'] if r['name'] == q['reaction'])
            args = dict(kind='reaction_coordinate', name=q['reaction'], coefficient=q['coefficient'])
        elif q.get('enthalpy_shift'):
            origin, bounds = 0., [-10000 - shifts[q['reaction']], 10000 - shifts[q['reaction']]]
            args = dict(kind='reaction_enthalpy_shift', name=q['reaction'], pivot_temperature=313.15)
        else:
            origin = values[q['identity']]
            args = dict(targets=[[t['family'], t['target'], t['factor']] for t in q.get('targets', [dict(q, factor=1.)])])
        result.append(dict(args, identity=q['identity'], origin=origin, scale=scale, bounds=bounds))
    spec.inputs['coordinates'] = result
    return result
def baseline(name):
    spec = bind(read(STARTS[name]))
    rows = spec.inputs['observations']['fitted']
    values = evaluate(spec, rows)
    check(values)
    reference = read(B / f'results/phase-diagnosis-255/{name}/replay.json')
    refs = {r['target']: r for r in reference}
    differences = [{k: abs(v[a] - refs[v['identity']][b]) / (abs(refs[v['identity']][b]) if k=='value' else max(1., abs(refs[v['identity']][b])))
                    for k, a, b in [('value', 'value', 'predicted'), ('residual', 'residual', 'residual'), ('weighted_residual', 'weighted_residual', 'weighted_residual')]}
                   for v in values]
    write(f'{name}/baseline.json', dict(rows=values, differences=differences, cost=math.fsum(v['cost'] for v in values)))
    assert len(values) == 307 and max(x[k] for x in differences for k in x) <= (1e-10 if SHA == OLD_SHA else 1e-8)
    assert abs(math.fsum(v['cost'] for v in values)/math.fsum(v['cost'] for v in reference)-1) <= 1e-8
    write(f'{name}/coordinates.json', coordinates(spec, name))
    try:
        derivative = reg.differentiate(spec.parameters, spec.coordinates(), [spec.observation(r) for r in rows],
            optimizer=[0.] * 16, holds=[], thermochemistry=spec.thermal)
        chart_errors = [abs(a-v['value'])/max(1.,abs(v['value'])) for a,v in zip(derivative.predictions,values,strict=True)]
        write(f'{name}/chart.json', dict(physical=derivative.chart.physical, statuses=[x.name for x in derivative.statuses], prediction_errors=chart_errors))
        assert max(chart_errors) <= 1e-8 and all(x.name == 'Available' for x in derivative.statuses)
    except epcsaft.ParameterError as exc:
        write(f'{name}/chart-refusal.json', dict(exception=type(exc).__name__, message=str(exc)))
        raise
    return spec

def density_rows():
    path = B / 'results/engine-3e83e19c-paper-evidence/density.csv'
    rows = list(csv.DictReader(path.open()))
    rows.extend(csv.DictReader((ROOT / 'data/reference/MEA/observations/density_viscosity/Sobrino_2016_density.csv').open()))
    assert len(rows) == 234 and len({r['id'] for r in rows}) == 234
    return rows
def density_records(spec, rows):
    template = spec.problems[next(r['problem'] for r in spec.inputs['observations']['fitted'] if r['group'] == 'loaded density')]
    masses = {c['component_id']: c['fixed']['molar_mass']['value']['magnitude'] for c in spec.inputs['endpoint']['components']}
    result = []
    for row in rows:
        identity, alpha, w = row['id'], float(row['loading']), float(row['mea_mass_fraction'])
        feed = {'monoethanolamine': 1., 'water': masses['monoethanolamine'] * (1-w) / (w*masses['water'])}
        support = list(feed) if w < 1 else ['monoethanolamine']
        if w == 1:
            feed.pop('water')
        if w < 1:
            if alpha:
                feed['carbon-dioxide'] = alpha
            support = list(spec.parameters.component_ids)
        spec.problems[identity] = eq.Problem(T=float(row['T_K']), P=float(row['P_Pa']), feed=eq.Amounts(feed),
            phases=[eq.Phase('L', kind='liquid', support=support)], reactions=template.reactions if w < 1 else [],
            neutral_reference=template.neutral_reference if w < 1 else None, row_tolerance=template.row_tolerance)
        result.append(dict(identity=identity, group='density comparison', row=row, observation_parameters=spec.parameter_sha256,
            constructor='observation', kind='phase_density', arguments=dict(observed=float(row['observed_kg_m3']),
            scale=float(row.get('s_kg_m3') or row.get('source_uncertainty_value') or 1.), form='difference', phase='L', mass_basis=True),
            weight=1., problem=identity, temperature_domain=[293.15, 393.15]))
    return result
def comparisons(name, mapping=None):
    spec = bind(read(STARTS[name]) if mapping is None else mapping)
    rows = density_rows()
    records = density_records(spec, rows)
    values = evaluate(spec, records)
    for row, value in zip(rows, values, strict=True):
        if value['status'] == 'Available':
            value.update(error_kg_m3=value['value'] - float(row['observed_kg_m3']),
                         error_percent=100*(value['value']/float(row['observed_kg_m3'])-1))
    write(f'{name}/density.json', values)
    return spec, records, values
def sensitivities(task):
    name, index = task
    verify()
    mapping = read(STARTS[name])
    params = s.parameter_values(mapping)
    keys = [f'component/{cid}/{q}' for cid in ('monoethanolamine', 'water')
            for q in ('segment_count', 'segment_diameter', 'dispersion_energy_over_k')]
    keys[keys.index('component/water/segment_diameter')] += '/constant-plus-sum-of-exponentials/constant'
    keys += ['pair/monoethanolamine/water/k_ij', 'pair/monoethanolamine/water/k_ij/reciprocal_temperature_slope',
             'component/protonated-monoethanolamine/dispersion_energy_over_k']
    for key in [keys[index]]:
        assert key in params, key
        step = 1. if key.endswith('slope') else .001 if '/pair/' in '/'+key else .001*params[key]
        output = []
        for factor in (1., .5):
            for sign in (-1, 1):
                changed = s.with_parameter_values(mapping, {key: params[key] + sign*step*factor})
                spec = bind(changed)
                rows = density_records(spec, density_rows())
                output.append(dict(step=sign*step*factor, values=evaluate(spec, rows)))
        write(f'{name}/sensitivities/{keys.index(key)}.json.gz', dict(coordinate=key, origin=params[key], probes=output))
        print(name, key, flush=True)

def sensitivity_run(name):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=min(9, os.cpu_count())) as pool:
        list(pool.map(sensitivities, [(name, i) for i in range(9)]))

def extend_255():
    for name in ('final-size-wide','wide-size-5.35','wide-water--0.175','wide-born-4.5','wide-pair--0.5'):
        directory = B/'results/phase-diagnosis-255'/name
        spec = bind(read(directory/'parameters.json'))
        records = density_records(spec, [r for r in density_rows() if r['source']=='Han2012' and float(r['T_K'])>353.15])
        values = evaluate(spec, records)
        check(values)
        write(f'reused-255/{name}.json',dict(source=str(directory.relative_to(ROOT)),original_wheel_sha256=OLD_SHA,
            original_summary=read(directory/'summary.json'),higher_temperature_rows=values))

def fit(name):
    assert SHA == NEW_SHA and read(OUT / 'final/baseline.json')['wheel_sha256'] == SHA
    if (OUT / name / 'fit.json').exists():
        finish_fit(name)
        return
    spec = baseline(name)
    original = spec.inputs['observations']['fitted']
    extra = [r for r in density_rows() if r['source'] == 'Han2012' and float(r['T_K']) > 353.15]
    added = density_records(spec, extra)
    assert len(added) == 25
    for r in added:
        r['weight'] = 1/20 if float(r['row']['loading']) else 1/5
        r['arguments']['scale'] = float(r['row']['source_uncertainty_value'])
    rows = original + added
    start = evaluate(spec, rows)
    check(start)
    write(f'{name}/fit-inputs.json', dict(coordinates=spec.inputs['coordinates'], rows=rows, start=start))
    spec.inputs['observations']['fitted'] = rows
    historical = read(CHAIN / ('restricted-2/attempt-3/spec.json' if name == 'final' else 'a6/spec.json'))
    spec.spec['optimizer'] = dict(historical['controls'], maximum_elapsed_time_seconds=historical['fit_wall_s'])
    result, report, _ = spec.fit()
    report['statuses'] = [x.name for x in result.statuses]
    write(f'{name}/fit.json', report)
    finish_fit(name)
def finish_fit(name):
    import fit_campaign as campaign
    report, inputs = retained(f'{name}/fit.json'), retained(f'{name}/fit-inputs.json')
    assert abs(report['initial_cost']/math.fsum(r['cost'] for r in inputs['start'])-1) <= 1e-8
    if not report['usable']:
        return
    historical = read(CHAIN / ('restricted-2/attempt-3/spec.json' if name == 'final' else 'a6/spec.json'))
    ordinary = [q for q in historical['information_coordinates'] if 'reaction' not in q]
    count = sum(1+len(q.get('ties',[])) for q in ordinary)
    updates = campaign.fitted_parameter_values(ordinary, report['physical'][:count])
    for entry in report['reactions']['aqueous']:
        reaction, law = entry['name'], eq.ReactionLogPolynomial(**entry['correlation'])
        if reaction not in ('R2','R5'):
            continue
        fields = dict(zip(('a_k','b','c_per_k'), reg.reaction_log10_reciprocal(law), strict=True)) if reaction == 'R5' else dict(a=law.a-law.c*math.log(law.reference_temperature), b_k=law.b, c=law.c, d_per_k=law.d)
        updates.update({f'reaction:{reaction}:correlation:{k}': v for k,v in fields.items()})
    mapping = s.with_parameter_values(read(STARTS[name]), updates)
    write(f'{name}/fitted-parameters.json', mapping)
    replay = bind(mapping)
    extra = [r['row'] for r in inputs['rows'][307:]]
    records = density_records(replay, extra)
    for r, original in zip(records, inputs['rows'][307:],strict=True):
        r['arguments']['scale'], r['weight'] = original['arguments']['scale'],original['weight']
    values = evaluate(replay, replay.inputs['observations']['fitted'] + records)
    check(values)
    differences = [abs(v['value']-p)/max(1.,abs(p)) for v,p in zip(values,report['predictions'],strict=True)]
    write(f'{name}/fit-replay.json', dict(rows=values, differences=differences))
    assert max(differences) <= 1e-8
    comparisons(name + '-fit', mapping)

def phase_job(task):
    name, state = task
    import phase_diagnosis_255 as d
    mapping = read(OUT / f'{name}/fitted-parameters.json')['result']
    path = OUT / f'{name}/phase/{state["index"]}.json'
    row = {k: state[k] for k in ('index','temperature_K','loading','pressure_Pa')}
    d.f.family_job(mapping, d.e.request(mapping,313.15,.11), row, [], path)
    raw = read(path)
    write(f'{name}/phase/{state["index"]}.json.gz', raw)
    path.unlink()
    print(name, state['index'], raw['classification'], flush=True)
    return d.reduce_state(raw)
def phase(name):
    from concurrent.futures import ProcessPoolExecutor
    states = read(B / 'results/engine-3e83e19c-phase-search/run-2/inputs/states.json')
    (OUT / name / 'phase').mkdir(exist_ok=True)
    memory = int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1])
    with ProcessPoolExecutor(max_workers=min(os.cpu_count(), max(1,memory//750000),len(states)), initializer=verify) as pool:
        rows = list(pool.map(phase_job, [(name,state) for state in states]))
    write(f'{name}/phase-summary.json', dict(rows=rows, descent_states=sum(r['resolved']>0 for r in rows), incomplete_states=sum(not r['complete'] for r in rows)))

def retained(path):
    path = OUT / path
    payload = json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())
    assert payload['wheel_sha256'] == SHA
    return payload['result']
def present():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    summaries, sensitivity, qualification = [], [], {}
    for name in STARTS:
        rows = retained(f'{name}/baseline.json')['rows']
        refs = {r['target']: r for r in read(B/f'results/phase-diagnosis-255/{name}/replay.json')}
        qualification[name] = dict(rows=len(rows),maximum_relative_prediction_difference=max(abs(v['value']/refs[v['identity']]['predicted']-1) for v in rows),
            maximum_scaled_residual_difference=max(abs(v['residual']-refs[v['identity']]['residual'])/max(1.,abs(refs[v['identity']]['residual'])) for v in rows),
            relative_cost_difference=abs(math.fsum(v['cost'] for v in rows)/math.fsum(v['cost'] for v in refs.values())-1))
        assert len(rows)==307 and max(v for k,v in qualification[name].items() if k!='rows')<=1e-8
    write('qualification.json', qualification)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout='constrained')
    for name, marker, color in [('final','o','#0072B2'),('wide','x','#D55E00'),('final-fit','+','#009E73'),('wide-fit','1','#CC79A7')]:
        values = retained(f'{name}/density.json')
        check(values)
        for src, axis in zip(('Amundsen2009','Hartono2014','Han2012','Sobrino2016'),axes.flat,strict=True):
            selected = [v for v in values if v['row']['source'] == src]
            axis.scatter([float(v['row']['T_K']) for v in selected], [v['error_kg_m3'] for v in selected], label=name,marker=marker,color=color,s=18,alpha=.7)
            if name=='final' and src in ('Han2012','Sobrino2016'):
                axis.errorbar([float(v['row']['T_K']) for v in selected], [v['error_kg_m3'] for v in selected],
                    yerr=[float(v['row']['source_expanded_uncertainty_value']) for v in selected], fmt='none',ecolor=color,alpha=.3,linewidth=.7)
            axis.set(title=src, xlabel='Temperature / K', ylabel='Predicted − measured density / kg m⁻³')
        for src in dict.fromkeys(v['row']['source'] for v in values):
            for loaded in (False,True):
                for hot in (False,True):
                    group = [v for v in values if v['row']['source']==src and bool(float(v['row']['loading']))==loaded and (float(v['row']['T_K'])>353.15)==hot]
                    if not group:
                        continue
                    expanded = [v for v in group if v['row'].get('source_expanded_uncertainty_value')]
                    summaries.append(dict(parameters=name,source=src,loaded=loaded,above_353_K=hot,n=len(group),mean_error_kg_m3=math.fsum(v['error_kg_m3'] for v in group)/len(group),
                        minimum_error_kg_m3=min(v['error_kg_m3'] for v in group),maximum_error_kg_m3=max(v['error_kg_m3'] for v in group),
                        AARD_percent=math.fsum(abs(v['error_percent']) for v in group)/len(group),source_expanded_available=len(expanded),
                        within_source_expanded=sum(abs(v['error_kg_m3'])<=float(v['row']['source_expanded_uncertainty_value']) for v in expanded)))
    for axis in axes.flat:
        axis.axhline(0.,color='.4',linewidth=.7)
        axis.legend(fontsize=8)
        axis.grid(alpha=.15)
    fig.savefig(OUT / 'density-errors.png',dpi=180)
    plt.close(fig)
    for name in STARTS:
        for path in sorted((OUT/name/'sensitivities').glob('*.gz')):
            data = retained(path.relative_to(OUT))
            probes = data['probes']
            for probe in probes:
                check(probe['values'])
            for loaded in (False,True):
                ids = [i for i,v in enumerate(probes[0]['values']) if v['row']['source']=='Han2012' and float(v['row']['T_K'])>353.15 and bool(float(v['row']['loading']))==loaded]
                derivatives = [[(probes[j+1]['values'][i]['value']-probes[j]['values'][i]['value'])/(probes[j+1]['step']-probes[j]['step']) for i in ids] for j in (0,2)]
                sensitivity.append(dict(parameters=name,coordinate=data['coordinate'],origin=data['origin'],loaded=loaded,n=len(ids),step=probes[1]['step'],
                    mean_derivative_kg_m3_per_coordinate=math.fsum(derivatives[1])/len(ids),
                    mean_density_change_for_positive_step_kg_m3=math.fsum(derivatives[1])/len(ids)*probes[1]['step'],
                    half_step_max_derivative_difference=max(abs(a-b) for a,b in zip(*derivatives,strict=True))))
    write('density-summary.json', summaries)
    write('sensitivity-summary.json', sensitivity)
    fits = {}
    for name in STARTS:
        report, replay = retained(f'{name}/fit.json'), retained(f'{name}/fit-replay.json')['rows']
        ids = {r['identity'] for r in retained(f'{name}/baseline.json')['rows'] if r['group']=='loaded density'}
        loaded = [v for v in replay if v['identity'] in ids]
        fits[name] = dict(status=report['status'],usable=report['usable'],iterations=report['iterations'],initial_cost=report['initial_cost'],final_cost=report['final_cost'],
            original307_cost=math.fsum(v['cost'] for v in replay[:307]),within_2s=sum(abs(v['residual'])<=2 for v in loaded),loaded_rows=len(loaded),phase=retained(f'{name}/phase-summary.json'))
        assert len(loaded) == 47
    write('summary.json', fits)
    paths = [Path(__file__), ROOT/'src/MEA/solvent_specification.py', AN/'MEA-pre-260-340.toml', AN/'declarations.toml',
             *sorted((AN/'inputs').iterdir()), *STARTS.values(), ROOT/'data/reference/MEA/observations/density_viscosity/Sobrino_2016_density.csv',
             ROOT/'data/reference/MEA/observations/density_viscosity/Han_2012_loaded_density.csv', B/'results/engine-3e83e19c-paper-evidence/density.csv']
    write('provenance.json',dict(base='30db72afad45232c36f8bfce82ea80278f3267e2',python=sys.version, CPU_count=os.cpu_count(), installed_wheel_bytes_verified=True,
        inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        reused_255={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'results/phase-diagnosis-255').rglob('*') if p.is_file()},
        source_PDF_SHA256=dict(Han2012='14d8a6b065889dddd06a21c736df2dacee86201bd624b0bb5f6282a1af5f8a92',Sobrino2016='713cf402c55d3af0224c1e3abe689050aa63b42350939618a5a0d8a04f3dea78')))

if __name__ == '__main__':
    verify()
    if sys.argv[1] == 'baseline':
        baseline(sys.argv[2])
    elif sys.argv[1] == 'compare':
        comparisons(sys.argv[2])
    elif sys.argv[1] == 'sensitivity':
        sensitivity_run(sys.argv[2])
    elif sys.argv[1] == 'fit':
        fit(sys.argv[2])
    elif sys.argv[1] == 'phase':
        phase(sys.argv[2])
    elif sys.argv[1] == 'present':
        present()
    elif sys.argv[1] == 'extend-255':
        extend_255()
