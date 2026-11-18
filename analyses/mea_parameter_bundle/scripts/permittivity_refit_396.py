"""Part I loaded-MEA permittivity refit (#396)."""
from collections import Counter
import sys
import tarfile
import tempfile
import time
import tomllib

import shared_evaluation as s

COMMIT, SHA = s.ENGINE_COMMIT, s.ENGINE_WHEEL_SHA256
import reduced_refit_338 as refit  # noqa: E402 -- historical module changes the pin on import

r = refit.r
OUT = r.B / 'results/permittivity-refit'
ADOPTED = r.ROOT / 'analyses/solvent_specification_mea/inputs/endpoint.json'
BASELINE = OUT.parent / 'wheel-recheck-05e94210/stability-adopted-law'
FAMILY = 'ion_specific_suppression_coefficient'
LAW = 'solvent-density-temperature-ion-specific-susceptibility-suppression'
IONS = ('carbamate-anion', 'bicarbonate-anion', 'carbonate-anion')
HAJJ = r.ROOT/'analyses/permittivity_temperature_loading/inputs/source-values.csv'
refit.OUT = OUT
r.COMMIT, r.SHA = COMMIT, SHA
s.ENGINE_COMMIT, s.ENGINE_WHEEL_SHA256 = COMMIT, SHA
r.WHEEL = s.installed_wheel()
refit.a.SHA, refit.a.COMMIT, refit.a.WHEEL = SHA, COMMIT, r.WHEEL
from final_evidence import flash_problem, table  # noqa: E402 -- imports verify the restored pin


def coefficient_key(ion):
    return f'component/{ion}/{FAMILY}'


def coefficients(mapping, pairs=(0., 0.), shift=0., *, cation=0., anion=0.):
    result = r.copy.deepcopy(mapping)
    law = next(x for x in result['model_families'] if x['kind'] == 'permittivity')
    law['choice'] = LAW
    values = dict(zip(IONS, (pairs[0], pairs[1], pairs[1]), strict=True)) if pairs is not None else {}
    for component in result['components']:
        cid = component['component_id']
        charge = component['fixed']['charge_number']['value']['magnitude']
        if charge:
            component['coefficients'].append(dict(
                family=FAMILY, identity=coefficient_key(cid),
                value=dict(magnitude=values.get(cid, cation if charge > 0 else anion) + shift * charge, unit='dimensionless'),
                candidate_domain_id=law['candidate_domain_id'], qualification=law['qualification'],
                provenance=law['provenance'], source_sha256=law['source_sha256']))
    return result


def bind(mapping, lower=0., weight=1.):
    dataset, = tomllib.loads((OUT/'declarations.toml').read_text())['datasets']
    dataset.update(weight=dataset['weight']*weight)
    spec = r.d.bind(mapping, 'MEA.toml', additional_datasets=[dataset])
    declared = r.read(OUT.parent/'reduced-refit/F2/previous/unpenalized/declaration.json')['declared']
    values = s.parameter_values(mapping)
    for ions in (IONS[:1], IONS[1:]):
        key = coefficient_key(ions[0])
        if key in values:
            declared.append(dict(identity=key, scale=1., bounds=[lower, 15.],
                                 targets=[('ion_suppression_coefficient', ion, 1.) for ion in ions]))
    spec.inputs['coordinates'] = [dict(q, origin=values[q['identity']]) for q in declared]
    return spec


def observation_identity(adopted, zero):
    import uncertainty_307 as u
    spec = bind(zero)
    records = spec.inputs['observations']['fitted']
    started = time.monotonic()
    derivative = u.derivative(spec, records)
    seconds = time.monotonic()-started
    new = r.d.evaluate(spec, records)
    old_spec = bind(adopted)
    old = r.d.evaluate(old_spec, old_spec.inputs['observations']['fitted'])
    r.d.check(old)
    r.d.check(new)
    assert len(old) == len(new) == len(derivative.predictions) == 335
    differences = [refit.a.relative(x['value'], y['value']) for x,y in zip(new,old,strict=True)]
    costs = [r.math.fsum(x['cost'] for x in rows[:307]) for rows in (new,old)]
    rows = [dict(current=x, adopted=y, derivative_prediction=p, relative_difference=d)
            for x,y,p,d in zip(new, old, derivative.predictions, differences, strict=True)]
    scatter = [float(x['row']['epsilon']) - (.418*t-.0155*t*t+319) *
               (-3.47*a**3+3.12*a*a-.643*a+.258)
               for x in old[307:] for t,a in [(float(x['row']['T_K'])-273.15,float(x['row']['loading']))]]
    report = dict(rows=rows, derivative_seconds=seconds, part_i_costs=costs,
                  part_i_max_relative=max(differences[:307]), hajj_max_relative=max(differences[307:]),
                  cost_relative=refit.a.relative(*costs), hajj_scale_rms=r.math.sqrt(r.math.fsum(d*d for d in scatter)/28),
                  hajj_scale_maximum=max(map(abs,scatter)), limit=1e-10)
    report['passed'] = max(report[k] for k in ('part_i_max_relative', 'hajj_max_relative', 'cost_relative')) <= report['limit']
    s.write_json(OUT/'C1.json', report)
    print({k:v for k,v in report.items() if k!='rows'}, flush=True)
    assert report['passed'], 'C1 observation identity failed'


def stability_identity(mapping):
    start = time.monotonic()
    r.OUT = OUT
    rows = r.grid(mapping, sum(r.states(), []), {})
    r.write('C2/grid.json.gz', rows)
    census = r.census(mapping, 'C2')
    old = r.read(BASELINE / 'grid.json')
    fields = ('key', 'available', 'optimized_available', 'completed', 'no_descent_in_trial_set')
    differences = [new['key'] for new, old in zip(rows, old, strict=True)
                   if any(new.get(k) != old.get(k) for k in fields) or r.descent(new) != r.descent(old)]
    compared = r.result('C2/census.json')['rows']
    previous = r.read(BASELINE / 'census.json')['result']['rows']
    census_differences = [new['index'] for new, old in zip(compared, previous, strict=True)
                          if any(new[k] != old[k] for k in ('index', 'classification', 'complete', 'resolved'))]
    report = dict(grid=r.tally(rows[:1908]), offset=r.tally(rows[1908:]), census=census,
                  grid_differences=differences, census_differences=census_differences,
                  passed=not (differences or census_differences), seconds=time.monotonic()-start)
    r.write('C2/identity.json', report)
    print(report, flush=True)
    assert report['passed'], 'C2 stability identity failed'


def phase_rows(spec, problems, mapping):
    indices = [spec.model.component_ids.index(i) for i in IONS]
    D = denominator(mapping)
    rows = []
    for name, problem in problems:
        solved = r.eq.solve_equilibrium(spec.model, problem)
        assert solved.success and solved.requested_tolerance_met, (name, solved.message)
        for phase, rho in enumerate(solved.molar_densities):
            x = solved.phase_mole_fractions(phase)
            eps = spec.model.state(solved.temperature, rho=rho, x=x).bulk_relative_permittivity
            rows.append(dict(name=name, T_K=solved.temperature, P_Pa=solved.pressure, phase=phase,
                             rho=rho, x=list(x), anion=sum(x[i] for i in indices), D=D(x), epsilon=eps))
    return rows


def fitted_problems(spec):
    keys = dict.fromkeys(row[k] for row in spec.inputs['observations']['fitted']
                        for k in ('problem', 'initial', 'final') if k in row)
    return [(k, spec.problems[k]) for k in keys]


def domain(adopted):
    spec = bind(adopted)
    r.OUT = OUT
    census = r.result('C2/census-raw.json.gz')
    grid = r.result('C2/grid.json.gz')
    problems = []
    for state, row in zip(sum(r.states(), []), grid, strict=True):
        item = r.stability_row(spec, state, 1.)
        item.problem.pressure = type(item.problem.pressure).fixed(row['pressure_Pa']*state['c'])
        problems.append((state['key'], item.problem))
    rows = phase_rows(spec, fitted_problems(spec) + problems, adopted)
    ids = spec.model.component_ids
    maximum = max(rows, key=lambda x: x['anion'])
    for row in census:
        for phase in row['final']['phases']:
            x = dict(zip(phase['support'], phase['mole_fractions'], strict=True))
            anion = sum(x.get(i, 0.) for i in IONS)
            if anion > maximum['anion']:
                maximum = dict(name=f"census:{row['index']}", x=[x.get(i, 0.) for i in ids], anion=anion)
    xmax = maximum['anion']
    lower, negative = r.math.trunc(-100./xmax)/100., max(-6.75, -.5/xmax)
    s.write_json(OUT/'domain.json', dict(maximum=maximum, lower=lower, negative_start=negative, rows=rows))
    print('parent domain', maximum, lower, negative, flush=True)
    return lower, negative


def fit(name, adopted, pairs, lower, weight=1.):
    r.bind = lambda mapping: bind(mapping, lower, weight)
    start = coefficients(adopted, pairs) if pairs is not None else adopted
    declared = r.bind(start).inputs['coordinates']
    fitted = [dict(q, targets=[dict(family=f, target=i, factor=v) for f,i,v in q['targets']])
              if FAMILY in q['identity'] else q['identity'] for q in declared]
    ties = {q['identity']: [t for t in q['targets'] if t[0]=='born_diameter']
            for q in declared if any(t[0]=='born_diameter' for t in q['targets'])}
    mapping, report = refit.fit(name, start, {}, fitted, ties)
    s.write_json(OUT/name/'endpoint.json', dict(available=mapping is not None, report=report))
    if mapping is not None:
        s.write_json(OUT/name/'parameters.json', mapping)
        refit.information(name, mapping, report['declared'])
        spec = r.bind(mapping)
        rows = phase_rows(spec, fitted_problems(spec), mapping)
        s.write_json(OUT/name/'C5.json', dict(rows=rows, minimum_D=min(x['D'] for x in rows),
                     passed=all(x['D'] > 0 for x in rows)))
    return mapping, report


def endpoint_checks(name):
    root = OUT/name
    mapping = r.read(sorted(root.glob('parameters-*.json'))[-1])
    replay = r.read(root/'replay.json')['rows']
    phase = next(x for x in r.read(root/'C5.json')['rows'] if x['name']=='Hajj2024-table-1-28:problem')
    values = s.parameter_values(mapping)
    prefix = [f'component/{i}/' for i in s.COMPONENT_IDS[:3]]
    x = phase['x'][:3]
    A, B = [sum(xi*values[p+f] for xi,p in zip(x,prefix,strict=True)) for f in ('dielectric_volume','dielectric_temperature')]
    hand = 1. + phase['rho']/1000*A*(B/(sum(x)*phase['T_K'])-1.)/phase['D']
    error = refit.a.relative(hand, replay[-1]['value'])
    s.write_json(root/'C3.json', dict(state=phase, hand=hand, prediction=replay[-1]['value'], relative=error, limit=1e-10))
    assert error <= 1e-10, 'C3 failed'
    pairs = tuple(values[coefficient_key(i)] for i in IONS[:2])
    bare = r.copy.deepcopy(mapping)
    for component in bare['components']:
        component['coefficients'] = [c for c in component['coefficients'] if c['family']!=FAMILY]
    passed = True
    for label, shift in (('unit', 1.), ('bicarbonate', pairs[1])):
        spec = bind(coefficients(bare, pairs, shift))
        rows = r.d.evaluate(spec, spec.inputs['observations']['fitted'])
        unavailable = [v for v in rows if v['status']!='Available' or not v.get('requested_tolerance_met')]
        errors = {v['identity']: refit.a.relative(v['value'], old['value'])
                  for v,old in zip(rows,replay,strict=True) if v not in unavailable}
        s.write_json(root/f'C4-{label}.json', dict(shift=shift, unavailable=unavailable, relative_errors=errors, limit=1e-10))
        passed &= not unavailable and max(errors.values()) <= 1e-10
    assert passed, 'C4 failed'


def comparisons(adopted, endpoint):
    from MEA.solvent_specification import deviation_statistics
    from dielectric_volume import composition
    started = time.monotonic()
    results = {}
    for label, cation, anion in (('Zuber', 2.60, 7.89), ('Figiel', 7.01, 7.01)):
        spec = bind(coefficients(adopted, None, cation=cation, anion=anion))
        rows = r.d.evaluate(spec, spec.inputs['observations']['fitted'])
        results[label] = dict(rows=rows, part_i_cost=sum(x['cost'] for x in rows[:307])
                              if all('cost' in x for x in rows[:307]) else None)
    unloaded = [row for row in refit.e.rows(HAJJ) if float(row['loading']) == 0.]
    for label, mapping in (('adopted', adopted), ('S1', endpoint)):
        model = bind(mapping).model
        rows = [dict(row, calculated=model.state(float(row['T_K']), P=101325., phase='liquid',
                     x=composition(mapping, float(row['MEA_mass_fraction']))).bulk_relative_permittivity) for row in unloaded]
        results[label] = dict(rows=rows, deviations=deviation_statistics([(float(x['epsilon']), x['calculated']) for x in rows]))
    s.write_json(OUT/'S1/permittivity-comparisons.json', dict(results=results, seconds=time.monotonic()-started))
    r.bind = bind
    refit.information('adopted', adopted, bind(adopted).inputs['coordinates'])


def hajj_inputs():
    source = [row for row in refit.e.rows(HAJJ) if row['source']=='HajjLoaded2024']
    # Hajj, Pré and Curet (2024), Table 1 (p. 9), in source-values.csv row order.
    frequencies = [5.97, 7.27, 8.99, 10.36, 12.14, 14.10, 14.29, 4.97, 5.78, 6.92, 8.19, 9.70, 11.10, 12.24,
                   4.11, 4.49, 5.50, 6.78, 8.31, 9.83, 10.43, 3.61, 4.13, 4.99, 5.98, 6.35, 9.29, 9.91]
    amine, water = .30/.06108, .70/.01801528  # 1 kg of CO₂-free 30 wt% stock.
    table(OUT/'hajj-table-1.csv', [dict(identity=f'Hajj2024-table-1-{i:02}', observation_order=306+i,
        T_K=x['T_K'], epsilon=x['epsilon'], carbon=float(x['loading'])*amine,
        source=s.json.dumps(dict(x, relaxation_frequency_GHz=f)), P=101325, amine=amine, water=water, zero=0, tolerance=1e-10)
        for i,(x,f) in enumerate(zip(source, frequencies, strict=True), 1)])


def hajj_comparison():
    import matplotlib.pyplot as plt
    candidate = r.read(OUT/'S1/replay.json')['rows'][307:]
    baseline = [x['adopted'] for x in r.read(OUT/'C1.json')['rows'][307:]]
    rows = [dict(T_K=x['T_K'], loading=x['loading'], relaxation_frequency_GHz=x['relaxation_frequency_GHz'],
                 hajj=float(x['epsilon']), adopted=a['value'], candidate=b['value'])
            for x,a,b in zip((s.json.loads(row['source']) for row in refit.e.rows(OUT/'hajj-table-1.csv')), baseline, candidate, strict=True)]
    table(OUT/'hajj-comparison.csv', rows)
    fig, axes = plt.subplots(2, 4, figsize=(12, 6), sharey=True, layout='constrained')
    for T, ax in zip(sorted({row['T_K'] for row in rows}), axes.flat):
        series = [row for row in rows if row['T_K']==T]
        for column, label, marker in [('hajj','Hajj extrapolation','o'), ('adopted','Adopted law','x'), ('candidate','S1','s')]:
            ax.scatter([float(row['loading']) for row in series], [row[column] for row in series], label=label, marker=marker)
        ax.set(title=f'{T} K', xticks=[.22, .33, .44, .55])
    axes.flat[-1].axis('off')
    axes.flat[-1].legend(*axes.flat[0].get_legend_handles_labels(), loc='center')
    fig.supxlabel('CO₂ loading (mol CO₂ per mol MEA)')
    fig.supylabel('Relative permittivity')
    fig.savefig(OUT/'hajj-comparison.png', dpi=160)


def denominator(mapping):
    values = s.parameter_values(mapping)
    terms = [(s.COMPONENT_IDS.index(i), values.get(coefficient_key(i), 0.)) for i in IONS]
    return lambda x: 1. + sum(b*x[i] for i,b in terms) if len(x) == len(s.COMPONENT_IDS) else None


def stability(endpoint, sample=False):
    r.OUT = OUT
    D = denominator(endpoint)
    original = r.read(OUT.parent/'reduced-refit/split-trials.json')
    name = 'S1/stability-probe' if sample else 'S1/stability'
    grid = sum(r.states(), [])[::137 if sample else 1]
    memory = {x['key']: [t for t in original.get(x['key'], []) if D(t['composition']) > 0.] for x in grid}
    started = time.monotonic()
    measured = r.grid(endpoint, grid, memory, capture=True)
    result = dict(grid_seconds=time.monotonic()-started, grid_states=len(grid))
    r.write(f'{name}/grid.json.gz', measured)
    s.write_json(OUT/name/'timing.json', result)
    print(result, flush=True)


def candidate_census(endpoint, probe=False):
    r.OUT = OUT
    name = 'S1/census-probe' if probe else 'S1/stability'
    D = denominator(endpoint)
    record = r.read(OUT/'S1/stability/split-registry.json')
    registry = record['trials'][:len(record['trials'])-len(record.get('census_witnesses', []))]
    admitted = [t for t in registry if D(t['composition']) > 0.]
    started = time.monotonic()
    r.census(endpoint, name, dict.fromkeys(map(str, range(162)), admitted),
             indices=(0, 54, 81, 108, 135, 161) if probe else None, keep_refusals=True)
    reduced = r.result(f'{name}/census.json')['rows']
    rows = []
    parents = []
    for raw, row in zip(r.result(f'{name}/census-raw.json.gz'), reduced, strict=True):
        reports = raw.get('stability', [])
        supplied = [t for report in reports for t in report.get('supplied_trials', [])]
        trials = [dict(t, D=D(t['composition'])) for report in reports for t in report['trials']]
        outside = [t for t in trials if t['D'] is not None and t['D'] <= 0.]
        splits = [t for t in trials if t['D'] is not None and t['D'] > 0. and t['resolved_descent']]
        cause = raw.get('failure') or (raw['attempts'][-1]['message'] if not raw.get('final') else None)
        evaluated = sum(t['evidence']=='evaluated' for t in supplied)
        rows.append(dict(row, classification=row['classification'] if row['parent_admitted'] else 'unavailable', cause=cause,
                         supplied_outside=len(registry)-len(admitted), supplied_evaluated=evaluated, supplied_unavailable=len(admitted)-evaluated,
                         optimized_outside=outside, split_trials=splits, phases=len(raw.get('final', {}).get('amounts', [])),
                         complete=row['complete'] and not outside and len(admitted)==len(registry)))
        if raw['index'] in (0, 27, 54, 81, 108, 135):
            first = next(iter(raw.get('attempts', [])), {})
            parents.append(dict(index=raw['index'], success=first.get('success', False), message=first.get('message', cause)))
    result = dict(rows=rows, seconds=time.monotonic()-started, registry_size=len(registry))
    s.write_json(OUT/name/'census-domains.json', result)
    s.write_json(OUT/('S1/census-probe' if probe else 'S1/stability-probe')/'census-parents.json', parents)
    print({k:v for k,v in result.items() if k!='rows'}, flush=True)


def penalty_profile(endpoint, grids_only=False):
    from heat_evidence_170 import request
    spec = bind(endpoint, r.read(OUT/'domain.json')['lower'])
    spec.spec['optimizer'] = dict(r.read(r.A6)['controls'], maximum_iterations=1, maximum_elapsed_time_seconds=1500.)
    scale = r.STAGES[0]
    census = [] if grids_only else r.read(OUT/'S1/stability/census-raw.json.gz')['result']
    req = request(endpoint, 313.15, .11)
    items = [r.stability_row(spec, state, scale) for state in sum(r.states(), [])]
    for state in census:
        phases = [r.eq.Phase('L', kind='liquid', support=s.COMPONENT_IDS)] if len(state.get('final', {}).get('amounts', [])) == 1 else None
        problem = flash_problem(req, state['loading'], state['temperature_K'], state['pressure_Pa'], phases)
        items.append(r.reg.stability(spec.parameters, problem, scale=scale))
    del census
    measured = r.read(OUT/'S1/stability/grid.json.gz')['result']
    report = dict(scale=scale, stability_rows=len(items), grid_unavailable=Counter(x['status'] for x in measured if not x['available']))
    started = time.monotonic()
    try:
        _, fit, _ = spec.fit([(item, 1.) for item in items])
        report.update({k: fit[k] for k in ('status', 'message', 'initial_cost', 'failures',
                       'iterations', 'residual_evaluations', 'jacobian_evaluations')})
    except r.epcsaft.ParameterError as error:
        report['cause'] = str(error)
    report['seconds'] = time.monotonic()-started
    report['seconds_at_21_iterations'] = 21*report['seconds'] if report.get('iterations') else None
    s.write_json(OUT/'S1'/('penalty-grid-profile.json' if grids_only else 'penalty-profile.json'), r.jsonable(report))
    print({k:v for k,v in report.items() if k not in ('grid_unavailable', 'failures')}, flush=True)


def not_fitted(endpoint_path):
    started = time.monotonic()
    refit.a.OUT = OUT.parent/'paper-evidence-341'
    refit.evidence('S1', endpoint_path)
    refit.scores('S1', r.read(endpoint_path))
    with tarfile.open(OUT/'S1/not-fitted-evidence.tar.gz', 'w:gz') as archive:
        for folder in ('evidence', 'point-data'):
            archive.add(OUT/folder, arcname=folder)
    s.write_json(OUT/'S1/not-fitted-timing.json', dict(seconds=time.monotonic()-started))


def stability_domains(endpoint):
    D, model = denominator(endpoint), bind(endpoint).model
    name = 'S1/stability'
    rows = r.read(OUT/name/'grid.json.gz')['result']
    reduced = []
    for row in rows:
        trials = row.get('optimized_trials', [])
        for trial in trials:
            trial['D'] = D(trial['composition'])
        outside = [t for t in trials if t['D'] is not None and t['D'] <= 0.]
        inside = [t for t in trials if t['D'] is not None and t['D'] > 0.]
        resolved = [t for t in inside if t['resolved_descent']]
        determinate = [t for t in inside if t['resolved_descent'] or
                       (t['evidence']=='no_resolved_descent' and t['optimizer_success'])]
        missing = len(trials)-len(outside)-len(determinate)
        parent = row.get('parent', {})
        if parent.get('success'):
            parent['D'] = D(parent['x'])
            parent['epsilon'] = model.state(parent['temperature'], rho=parent['rho'], x=parent['x']).bulk_relative_permittivity
        complete = bool(determinate) and not (missing or outside) and row.get('available') and row.get('completed') and parent.get('success')
        reduced.append(dict(key=row['key'], classification='resolved_descent' if resolved else
                            'no_descent_in_domain' if complete else 'incomplete', parent=parent,
                            optimized_trials=len(trials), outside_domain=len(outside), outside_trials=outside,
                            unresolved=missing, incomplete=not complete, split_trials=resolved,
                            minimum_tpd=min((t['quantities']['tpd_over_rt'] for t in determinate
                                             if t['quantities'].get('tpd_over_rt') is not None), default=None)))
    s.write_json(OUT/name/'domains.json', reduced)
    registry = r.read(OUT.parent/'reduced-refit/split-registry.json')
    witnesses = [dict(w, kind=w['kind'].lower(), parent=row['key'], D=D(w['composition'])) for row in rows
                 for w in row['witnesses'] if D(w['composition']) > 0.]
    census_path = OUT/name/'census-domains.json'
    census_witnesses = [dict(parent=row['index'], D=t['D'], kind=t['phase']['kind'], support=t['phase']['support'],
                         composition=t['composition'], packing=r.math.exp(t['split_coordinates'][-1]))
                        for row in r.read(census_path)['rows'] for t in row['split_trials']] if census_path.exists() else []
    trials = registry['trials'] + [{k:w[k] for k in ('composition', 'kind', 'packing', 'support')} for w in witnesses+census_witnesses]
    digest = r.hashlib.sha256(s.json.dumps(trials, sort_keys=True).encode()).hexdigest()
    s.write_json(OUT/name/'split-registry.json', dict(trials=trials, new_s1_witnesses=witnesses,
                 census_witnesses=census_witnesses, previous_sha256=registry['sha256'], sha256=digest))
    summary = dict(registry=dict(previous=len(registry['trials']), new_grid=len(witnesses), new_census=len(census_witnesses), total=len(trials)))
    for label, selected in [('enforced', reduced[:1908]), ('offset', reduced[1908:])]:
        summary[label] = dict(states=len(selected), classifications=Counter(x['classification'] for x in selected),
            **{k:sum(x[k] for x in selected) for k in ('optimized_trials', 'outside_domain', 'unresolved', 'incomplete')})
    for label, converged in [('converged', True), ('unconverged', False)]:
        split = [(row['key'], t) for row in reduced for t in row['split_trials'] if t['optimizer_success']==converged]
        ds, tpds = [t['D'] for _,t in split], [t['quantities']['tpd_over_rt'] for _,t in split]
        summary[label] = dict(trials=len(split), state_keys=sorted({key for key,_ in split}),
                              D_range=[min(ds), max(ds)], tpd_over_rt_range=[min(tpds), max(tpds)])
    s.write_json(OUT/name/'summary.json', summary)
    costs = {n:r.read(OUT/n/'replay.json')['cost'] for n in ('S1', 'S2', 'S3')}
    tolerance = min(costs.values())*r.read(r.A6)['controls']['function_tolerance']
    s.write_json(OUT/'summary.json', dict(selected=min(costs,key=costs.get), costs=costs, optimizer_cost_tie=tolerance,
                 ties=[n for n,cost in costs.items() if cost-min(costs.values())<=tolerance],
                 domain='domain.json', stability='S1/stability/summary.json', penalty='S1/penalty-profile.json'))


def retained_comparisons(endpoint):
    reference = OUT.parent/'paper-evidence-341/paper-evidence'
    refit.a.OUT = reference.parent
    summary = []
    with tempfile.TemporaryDirectory() as directory, tarfile.open(OUT/'S1/not-fitted-evidence.tar.gz') as archive:
        archive.extractall(directory, filter='data')
        candidate = r.Path(directory)/'evidence/S1'
        comparison_domains(endpoint, candidate)
        for label, root in [('adopted-341', reference), ('S1', candidate)]:
            groups = refit.scores('S1', endpoint, root=root, groups_only=True)
            mamun = [row for row in groups['six-source pressures'] if row['source']=='Mamun2005']
            assert [row['identity'] for row in mamun]==[f'canonical:vle_obs_{i:04d}' for i in range(246, 265)]
            groups['Ma’mun pressures'] = mamun
            for cohort, rows in groups.items():
                pairs = [(float(row['observed']), float(row['predicted'])) for row in rows if row['predicted'] not in (None, '', 'None')]
                errors = [p-o for o,p in pairs]
                metrics = dict(rows=len(pairs), aard_percent=100*r.math.fsum(abs(p/o-1) for o,p in pairs)/len(pairs),
                               rmse=r.math.sqrt(r.math.fsum(e*e for e in errors)/len(pairs)), bias=r.math.fsum(errors)/len(pairs)) if pairs else None
                summary.append(dict(label=label, cohort=cohort, expected=len(rows), metrics=metrics,
                                    unavailable=[row for row in rows if row['predicted'] in (None, '', 'None')]))
        table(OUT/'S1/mamun-pressure-rows.csv', mamun)
    s.write_json(OUT/'S1/not-fitted-comparisons.json', summary)


def comparison_domains(endpoint, root):
    import fit_observations as fo
    import heat_evidence_170 as he
    spec, D = bind(endpoint), denominator(endpoint)
    fitted = {x['identity'] for x in r.read(OUT/'S1/replay.json')['rows']}
    rows = []
    for path in (root/'selected-assessment/evaluation/states/Held').glob('*/*.json'):
        state = r.read(path)
        if not any(t['identity'] not in fitted for t in state['targets']):
            continue
        for phase in state['phases']:
            x = dict(zip(phase['support'], phase['mole_fractions'], strict=True))
            full = [x.get(i, 0.) for i in s.COMPONENT_IDS]
            dielectric = spec.model.state(state['T'], rho=phase['molar_density_mol_m3'], x=full)
            rows.append(dict(name=state['identity'], T_K=state['T'], P_Pa=phase['pressure_pa'],
                             x=full, D=D(full), epsilon=dielectric.bulk_relative_permittivity))
    han = [x for x in r.d.density_rows() if x['source']=='Han2012']
    records = r.d.density_records(spec, han)
    arcis = [r.read(p)['result']['source_row'] for p in (root/'selected-assessment/calorics-rows').glob('*.json')
             if r.read(p)['result']['source']=='Arcis2011']
    heat = fo.heat_items(endpoint, spec.parameters, arcis, he.request(endpoint, 313.15, .11))
    problems = [(x['identity'], spec.problems[x['problem']]) for x in records]
    problems += [(f"{x['record_id']}:{label}", problem) for x, item in zip(arcis, heat, strict=True)
                 for label, problem in [('initial',item.problem), ('final',item.final_problem)]]
    rows.extend(phase_rows(spec, problems, endpoint))
    s.write_json(OUT/'S1/comparison-domains.json', rows)
    started = time.monotonic()
    kim = []
    endpoints = {(float(row['T_K']), float(row[key])) for row in refit.e.rows(root/'kim2007-heat-pathways/kim-heat.csv')
                 if float(row['T_K']) in (313.15, 353.15) and row['interval_status']=='available'
                 for key in ('loading', 'previous_loading')}
    for row in refit.e.rows(root/'kim2007-heat-pathways/states.csv'):
        T, P, loading = float(row['T_K']), float(row['P_Pa']), round(float(row['loading']), 15)
        if row['status']=='available' and (T, loading) in endpoints:
            x = s.json.loads(row['mole_fractions'])
            state = spec.model.state(T, P=P, x=x, phase='liquid')
            kim.append(dict(T_K=T, P_Pa=P, loading=loading, x=x, D=D(x),
                            rho=state.molar_density, epsilon=state.bulk_relative_permittivity))
    s.write_json(OUT/'S1/kim-domains.json', dict(rows=sorted(kim, key=lambda row: (row['T_K'], row['loading'])), seconds=time.monotonic()-started))


if __name__ == '__main__':
    r.verify()
    assert s.sha256(ADOPTED) == 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
    adopted = s.parameter_mapping(ADOPTED)
    zero = coefficients(adopted)
    s.write_json(OUT/'zero-coefficients.json', zero)
    action, *args = sys.argv[1:]
    early = dict(C1=lambda: observation_identity(adopted, zero), C2=lambda: stability_identity(zero),
                 domain=lambda: domain(adopted), checks=lambda: endpoint_checks(*args),
                 **{'hajj-inputs': hajj_inputs, 'hajj-comparison': hajj_comparison})
    if action in early:
        early[action]()
    elif action in ('S1', 'S2', 'S3'):
        limits = r.read(OUT/'domain.json')
        value = {'S1': 0., 'S2': limits['negative_start'], 'S3': 10.42}[action]
        fit(action, adopted, (value, value), limits['lower'])
    else:
        sys.path.insert(0, str(r.ROOT/'analyses/permittivity_temperature_loading'))
        path = OUT/'S1/parameters-0.json'
        endpoint = r.read(path)
        actions = {'comparisons': lambda: comparisons(adopted, endpoint),
                   'stability': lambda: stability(endpoint), 'stability-probe': lambda: stability(endpoint, sample=True),
                   'census': lambda: candidate_census(endpoint), 'census-probe': lambda: candidate_census(endpoint, probe=True),
                   'penalty-profile': lambda: penalty_profile(endpoint, 'grids-only' in args), 'not-fitted': lambda: not_fitted(path),
                   'stability-domains': lambda: stability_domains(endpoint), 'comparison-domains': lambda: retained_comparisons(endpoint),
                   'weight': lambda: fit(f'weight-{args[0]}', endpoint, None, r.read(OUT/'domain.json')['lower'], float(args[0]))}
        actions[action]()
