"""MEA objective weighting and information audit (#420)."""
# ruff: noqa: E402
import hashlib
import json
import math
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'mdea_mea_workflow/scripts'))
from shared_bicarbonate_417 import BASE, ROOT, bind_wheel, compare_rows, f, mea_search, paper, r, s
from classify_descents import classify, coexistence, gibbs, pressure_roots
from part_ii import Route, active_bound_indices, branch_counts, deviation_statistics, np, reg

OUT = BASE.parent/'objective-weights-420'
EVIDENCE = paper.OUT/'paper-evidence'
STATE = 'dense|0.15|313.15|0.125|1.05'
UNITS = {'partial_pressure':'Pa','pressure':'Pa','temperature':'K','phase_density':'kg/m³',
         'addition_enthalpy':'J/mol CO₂','equilibrium_isobaric_heat_capacity':'J/(mol feed K)'}


def setup():
    bind_wheel()
    r.verify()
    wheel = r.read(ROOT/'analyses/mdea_mea_workflow/results/shared-bicarbonate-417/wheel-modules.json')
    installed = Path(r.epcsaft.__file__).parent.parent
    assert all(f.a.sha(installed/name) == sha for name, sha in wheel['installed_module_sha256'].items())
    assert f.a.sha(paper.RECORD) == 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
    r.OUT = f.OUT = OUT
    return s.parameter_mapping(paper.RECORD)


def control(mea):
    rows, ok, cost = r.replay(mea)
    r.write('reported-mea.json.gz', dict(rows=rows, available=ok, cost=cost))
    assert ok and len({v['identity'] for v in rows}) == len(rows) == 307
    assert f.a.relative(cost, 150.76290287953717) <= 1e-10
    compare_rows(rows, r.read(paper.OUT/'candidate/replay.json')['rows'],
                 ('identity', 'group', 'status', 'observed', 'row'), 1e-10)
    return rows


def grid_classify(mapping, rows, states):
    assert not any('supplied_trials' in row for row in rows), 'MEA grid carries supplied trials'
    ranges = {v['reaction']: (float(v['minimum_K']), float(v['maximum_K']))
              for v in f.e.rows(paper.OUT/'reaction-source-ranges.csv')}
    route = SimpleNamespace(bind=r.bind, stability_row=r.stability_row, config=dict(reaction_ranges_K=ranges))
    route.marks = Route.marks.__get__(route)
    return classify(route, mapping, [row | branch_counts(row) for row in rows], states)


def attempt_outcome(attempt):
    if not attempt['requested_tolerance_met']:
        return 'failed_solve'
    return 'confirmed' if attempt['confirmed'] else 'unconfirmed'


def census_classify(model, parent, result, report, registry):
    spec = SimpleNamespace(model=model, parameters=model.parameters)
    parent = parent._native(model)
    supplied = [(dict(bank_index=t['bank_index']), registry[t['bank_index']])
                for t in report['supplied_trials'] if r.supplied_negative(t)]
    native = [(dict(native_index=i), dict(t['phase'], composition=t['composition'], packing=math.exp(t['split_coordinates'][-1])))
              for i, t in enumerate(report['trials']) if t['resolved_descent']]
    outcomes = []
    donor = next(i for i, phase in enumerate(parent.phases) if phase.kind.name.lower() == 'liquid')
    primary = list(result.phase_mole_fractions(donor)), result.packing_fractions[donor]
    roots = pressure_roots(model, result.temperature, result.pressure, primary[0], result.molar_densities[donor])
    parent_g = gibbs(r.eq.compile_problem(model, parent), result) if result.requested_tolerance_met else None
    for identity, seed in native + supplied:
        entry = dict(identity, seed=seed, parent_roots=roots)
        outcomes.append(entry)
        try:
            assert result.requested_tolerance_met, result.message
            assert parent.pressure.value == result.pressure
            attempt = coexistence(spec, parent, parent_g,[primary, (seed['composition'], seed['packing'])])
            entry.update(attempt=attempt, outcome=attempt_outcome(attempt))
        except (AssertionError, ValueError, RuntimeError) as error:
            entry.update(outcome='unavailable', message=str(error))
    return outcomes


def handoff():
    main, offset = r.states()
    states = [v for v in main if v['key'] == STATE]
    bank = r.read(BASE/'split-trials.json')
    assert all(bank[v['key']] == [] for v in main+offset)
    registry = r.read(BASE/'split-registry.json')['trials']
    assert len(registry) == 6121 and hashlib.sha256(json.dumps(registry, sort_keys=True).encode()).hexdigest() == 'f7f02b1ef565690efb466dd6d3d73bc9c74c708116725b2b0d931486cdc1b666'
    wide = s.parameter_mapping(r.STARTS['wide'])
    row, = r.grid(wide, states, bank, capture=True)
    r.write('handoff/grid.json', row)
    assert r.descent(row), 'check (a): no native descent on the study wheel'
    entry, = grid_classify(wide, [row], states)
    r.write('handoff/classification.json', entry)
    assert 'classification_error' not in entry and (entry['native_branch'] != 'liquid' or entry['attempts']), entry
    assert all(entry['outside_ranges'][name] is False for name in ('R1', 'R2', 'R3'))
    try:
        grid_classify(wide, [dict(row, supplied_trials=[registry[0]])], states)
    except AssertionError as error:
        assert str(error) == 'MEA grid carries supplied trials'
        r.write('handoff/supplied-grid-guard.json', str(error))
    else:
        raise AssertionError('check (c): unexpected supplied grid trial accepted')
    mapping = s.parameter_mapping(BASE.parent/'split-cause-342/move-1-00/parameters.json')
    r.census(mapping, 'handoff', {'40': registry}, indices=[40], keep_refusals=True,
             compact_supplied=True, confirm=census_classify)
    reduced, = r.result('handoff/census.json')['rows']
    raw, = r.result('handoff/census-raw.json.gz')
    assert not reduced['resolved'] and reduced['supplied_negative'], 'check (b): expected supplied-only descent on study wheel'
    assert len({entry['bank_index'] for entry in raw['coexistence']}) == len(raw['coexistence']) == reduced['supplied_negative']
    assert all(entry.get('attempt') or entry.get('message') for entry in raw['coexistence'])


def transfer(case, declaration, endpoint, rows_file):
    route = Route(ROOT/'analyses'/declaration, OUT/case)
    path = ROOT/'analyses'/rows_file
    saved = r.read(path) if path.suffix == '.json' else f.e.rows(path)
    rows = [dict(v, value=float(v['predicted'])) if 'predicted' in v else v for v in saved if v['role'] == 'fitted']
    point = r.read(ROOT/'analyses'/endpoint)
    if case == 'DEA':
        assert point['chosen']['name'] == 'start-0'
        point = point['chosen']['parameters']
    spec, replay, ev = route.differentiate_endpoint(point)
    declared, records = point['coordinates'], spec.inputs['observations']['fitted']
    for saved, value, record in zip(rows, replay, records, strict=True):
        assert saved['identity'] == value['identity'] == record['identity']
        assert float(saved['observed']) == value['observed'] and saved['unit'] == value['unit']
        assert f.a.relative(saved['value'], value['value']) <= 1e-8
        assert 'residual' not in saved or f.a.relative(saved['residual'], value['residual']) <= 1e-8
    residuals = [math.log(v/o['arguments']['observed']) if o['arguments']['form']=='log_ratio'
                 else (v-o['arguments']['observed'])/o['arguments']['scale']
                 for v,o in zip(ev.predictions,records,strict=True)]
    assert np.allclose(residuals, [v['residual'] for v in replay], rtol=1e-8, atol=1e-13)
    expected_cost = {'DEA': 8.08296823, 'MDEA': 564.48369613, 'AMP': 62.06511058}[case]
    assert abs(math.fsum(v['cost'] for v in replay) - expected_cost) < 1e-8
    if case == 'AMP':
        for group in r.read(path.parent/'group-costs.json'):
            selected = [v for v in replay if (v['group'], v['unit']) == (group['group'], group['unit'])]
            assert len(selected) == group['rows'] and abs(math.fsum(v['cost'] for v in selected) - group['cost']) < 1e-8
        active = {q['identity']: 'lower' if q['origin'] == q['bounds'][0] else 'upper'
                  for q in declared if q['origin'] in q['bounds']}
        assert active == {'AMPCOO-segment-diameter': 'upper',
                          'AMP-hydrolysis-enthalpy-increment': 'lower'}, active
    return spec, replay, declared, ev.residual_optimizer_gradient


def pure_water_control(spec, rows, coords, jacobian):
    J = np.array(jacobian).reshape(len(rows), len(coords))
    records = spec.inputs['observations']['fitted']
    matches = []
    indices = []
    for i, (row, record, gradient) in enumerate(zip(rows, records, J, strict=True)):
        if record['row'].get('liquid_x_MDEA') != '0':
            continue
        problem = spec.problems[record['problem']]
        indices.append(i)
        matches.append(dict(identity=row['identity'], source_row=record['row'], feed=problem.feed.values,
                            phases=[dict(name=v.name, support=v.support) for v in problem.phases],
                            weight=record['weight'], predicted=row['value'], observed=row['observed'], cost=row['cost'],
                            optimizer_residual_derivatives=dict(zip([c['identity'] for c in coords], gradient, strict=True))))
    cost = math.fsum(x['cost'] for x in rows)
    zero_rows = [v['identity'] for v,g in zip(rows,J,strict=True) if not np.any(g)]
    point = r.read(ROOT/'analyses/mdea_mea_workflow/results/bounded-binary-411/endpoint.json')
    topology = point['parameters']['topology']
    edges = topology['edges']
    topology['edges'] = [q for q in edges if {q['endpoint_a']['component_id'], q['endpoint_b']['component_id']}
                         != {'water', 'protonated-methyldiethanolamine'}]
    assert len(edges) - len(topology['edges']) == 2
    topology['no_cross_association'].append(dict(component_id_a='water', component_id_b='protonated-methyldiethanolamine',
                                                  provenance='#420 pure-water diagnostic'))
    diagnostic = Route(ROOT/'analyses/mdea_mea_workflow/inputs/bounded-binary-411.json', OUT/'MDEA').bind(point)
    ev = reg.differentiate(diagnostic.parameters, diagnostic.coordinates(),
                           [diagnostic.observation(records[i]) for i in indices],
                           optimizer=[0.]*len(coords), thermochemistry=diagnostic.thermal)
    G = np.asarray(ev.residual_optimizer_gradient).reshape(len(indices), len(coords))
    for row, prediction, gradient in zip(matches, ev.predictions, G, strict=True):
        row.update(diagnostic_pressure_Pa=prediction, pressure_change_Pa=prediction-row['predicted'],
                   diagnostic_derivatives=dict(zip([c['identity'] for c in coords], gradient, strict=True)))
    r.write('MDEA/pure-water-derivative-control.json', dict(rows=matches,declared=len(rows),objective=cost,
            pure_water_cost=math.fsum(x['cost'] for x in matches),all_row_scale=2*cost/(len(rows)-6),raw_exact_zero_rows=zero_rows))
    assert [v['identity'] for v in matches] == ['fit:227', 'fit:229', 'fit:249']
    assert all(t.name == 'Available' for t in ev.statuses) and not np.any(G)
    assert max(abs(v['pressure_change_Pa']) for v in matches) <= 1.5e-11
    assert abs(math.fsum(v['cost'] for v in matches)-0.00019501364415) < 1e-13


def information(case, spec, rows, coords, jacobian, covariance, wheel):
    records = spec.inputs['observations']['fitted']
    e = spec.whiten(np.array([v['residual'] for v in rows]))
    J = spec.whiten(np.asarray(jacobian, dtype=np.float64).reshape(len(rows), len(coords)))
    report, contributions = information_reduction(case, records, rows, coords, e, J, covariance, wheel)
    f.e.table(OUT/case/'contributions.csv', contributions)
    r.write(f'{case}/information.json.gz', report)
    return report['blocks'], report['variance'], report['stage_variance']


def information_reduction(case, records, rows, coords, e, J, covariance, wheel):
    assert len({v['identity'] for v in rows}) == len(rows)
    scales = np.array([q['scale'] for q in coords])
    active = active_bound_indices(coords)
    interior = [i for i in range(len(coords)) if i not in active]
    groups, detail, excluded = defaultdict(list), [], []
    targets = {v['target']: v for v in f.e.rows(EVIDENCE/'state-targets.csv')}
    # The MEA objective origins assign Kiepe Table 1 and Amundsen Table 1 to these blocks.
    mea_sources = {'Cai': 'Cai1996', 'Kiepe': 'Kiepe', 'CO2-free density': 'Amundsen2009'}
    for i, (v, rec) in enumerate(zip(rows, records, strict=True)):
        assert v['identity'] == rec['identity'] and v['group'] == rec['group']
        target = targets.get(v['identity'], {})
        source = ((mea_sources.get(v['group']) if case == 'MEA' else None) or target.get('source')
                  or rec['row'].get('source_key') or rec['row'].get('source')
                  or v['identity'].split(':')[0].split('_')[0].rsplit('-',1)[0])
        source = {'AMU': 'Amundsen2009', 'hartono-2013': 'Hartono2013', 'hartono':'Hartono2021',
                  'ciftja':'Ciftja2014'}.get(source, source)
        quantity = rec['kind'] if rec['constructor']=='observation' else rec['constructor']
        observable = rec['row'].get('ratio') or rec['arguments'].get('species') or quantity
        if case == 'MDEA' and v['group'] == 'Kim':
            observable = 'pure water' if rec['row']['liquid_x_MDEA']=='0' else 'mixture'
        groups[(v['group'], source, str(observable))].append(i)
        unit = v.get('unit') or UNITS.get(quantity,'dimensionless')
        detail.append(dict(v, source=source, observable=quantity, unit=unit,
                           weight=rec['weight'], scale=rec['arguments'].get('scale',rec['row'].get('scale',1.)),
                           form=rec['arguments'].get('form',rec['row'].get('form')), cost=.5*e[i]**2, role='fitted'))
        if (case == 'MEA' and v['group'] == 'Kiepe') or (case == 'MDEA' and rec['row'].get('liquid_x_MDEA') == '0'):
            excluded.append(i)
    exact_zeros = set(np.flatnonzero(~np.any(J, axis=1)))
    assert exact_zeros <= set(excluded) and (case == 'MDEA' or exact_zeros == set(excluded))
    blocks = {str(key): ids for key, ids in groups.items()}
    for block in dict.fromkeys(v['group'] for v in rows):
        blocks.update({block: [i for i,v in enumerate(rows) if v['group'] == block]})
    if case == 'MEA':
        blocks.update({label: [i for i,v in enumerate(rows) if v['group']==group and (quantity is None or quantity in v['row'].values())]
                       for label,group,quantity,_ in r.GROUPS})
        blocks.update({k: [i for i,d in enumerate(detail) if d['group']=='Cai' and d['observable']==k] for k in ('temperature','mole_fraction')})
        blocks['species mole fractions'] = blocks['fitted phase mole fraction'] + blocks['restored species']
    blocks['whole fit'] = list(range(len(rows)))
    ranks = {}
    for label, ids in blocks.items():
        ranks[label] = dict(n=len(ids), zero_rows=int(sum(~np.any(J[ids],axis=1))), cost=math.fsum(detail[i]['cost'] for i in ids),
                            nonzero_columns=[coords[i]['identity'] for i in np.flatnonzero(np.any(J[ids],axis=0))])
        for basis, idx in [('adjustable', list(range(len(coords)))), ('interior', interior)]:
            block = J[np.ix_(ids,idx)]
            _, singular, vectors = np.linalg.svd(block, full_matrices=len(ids)<len(idx))
            cutoff = np.finfo(np.float64).eps*max(block.shape)*singular[0]
            ranks[label][basis] = dict(rank=int(sum(singular > cutoff)), cutoff=cutoff, singular_values=singular.tolist(),
                                       right_vectors=[dict(zip([coords[i]['identity'] for i in idx], v, strict=True)) for v in vectors])
    p = ranks['whole fit']['interior']['rank']
    affected = np.ones(len(rows),dtype=bool)
    affected[excluded] = False
    rss, rss_stage = math.fsum(e**2), math.fsum(e[affected]**2)
    n, na = len(rows), int(sum(affected))
    old, stage = rss/(n-p), rss_stage/(na-p)
    physical = J[:,interior]/scales[interior]
    assert np.array_equal(physical.T@physical, physical[affected].T@physical[affected]) or np.allclose(physical.T@physical, physical[affected].T@physical[affected],rtol=1e-12)
    assert p == len(interior) and na > p
    contributions = [
        dict(group=group,source=source,observable=observable,role='fitted',n=len(ids),
             unit=str(sorted({str(detail[i].get('unit')) for i in ids})),
             form=str(sorted({str(detail[i]['form']) for i in ids})),
             scale_min=min(float(detail[i]['scale']) for i in ids),scale_max=max(float(detail[i]['scale']) for i in ids),
             weight_min=min(detail[i]['weight'] for i in ids),weight_max=max(detail[i]['weight'] for i in ids),
             coefficient_min=min(detail[i]['weight']/float(detail[i]['scale'])**2 for i in ids),
             coefficient_max=max(detail[i]['weight']/float(detail[i]['scale'])**2 for i in ids),
             cost=ranks[str((group,source,observable))]['cost'],percent=200*ranks[str((group,source,observable))]['cost']/rss)
        for (group,source,observable),ids in groups.items()]
    return dict(wheel=wheel,basis='optimizer coordinates, scaled residual weighted once',
            coordinates=coords,active_bounds=active,blocks=ranks, rows=detail,
            n=n,na=na,p=p,denominator=n-p,stage_denominator=na-p,rss=rss,stage_rss=rss_stage,variance=old,
            stage_variance=stage,excluded=[detail[i] for i in excluded],SE_multiplier=math.sqrt(stage/old),
            conditional_correlation=covariance['conditional_correlation'],unscaled_information=(physical.T@physical).tolist()), contributions


def audit(mea):
    control(mea)
    history = paper.OUT/'uncertainty'
    spec = r.bind(mea)
    rows = r.read(paper.OUT/'candidate/replay.json')['rows']
    adopted = r.read(history/'adopted.json')
    assert adopted['predictions'] == [v['value'] for v in rows] and adopted['residuals'] == [v['residual'] for v in rows]
    coords = r.read(history/'inputs.json')['coordinates']
    ranks, old, stage = information('MEA', spec, rows, coords, adopted['jacobian'],
                                    r.read(history/'covariance.json')['adopted_point'], '391dfe5d')
    cases = {'fitted CO2 partial pressure':(47,11,10,5.9625533550202565), 'temperature':(25,2,2,39.82390854417673),
             'mole_fraction':(25,2,2,51.80738006), 'Kiepe':(39,0,0,.00067901949873167), 'Cai':(50,2,2,91.63128860)}
    for group, (n, full, interior, cost) in cases.items():
        b = ranks[group]
        assert (b['n'],b['adjustable']['rank'],b['interior']['rank']) == (n,full,interior) and abs(b['cost']-cost)<1e-8
    assert ranks['Cai']['nonzero_columns'] == ['pair/monoethanolamine/water/k_ij',
                                              'pair/monoethanolamine/water/k_ij/reciprocal_temperature_slope']
    assert abs(old-1.0152384) < 1e-8 and abs(stage-1.1686994098) < 1e-10
    revised_uncertainty('MEA', history/'covariance.json')
    for case, dec, res, point, rows_file, expected in (
        ('DEA','dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json','dea_transfer/results/refit-413','selection.json','paper-data.csv',(.21270969,.21270969)),
        ('MDEA','mdea_mea_workflow/inputs/bounded-binary-411.json','mdea_mea_workflow/results/bounded-binary-411','endpoint.json','data-rows.json',(4.10533597,4.15061398)),
        ('AMP','amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json','amp_transfer/results/retransfer-412-f2-05e94210/slope-150','parameters.json','data-rows.json',(.82753481,.82753481)),
    ):
        args = transfer(case,dec,f'{res}/{point}',f'{res}/{rows_file}')
        if case == 'MDEA':
            pure_water_control(*args)
        covariance = ROOT/'analyses'/res/'conditional-uncertainty.json'
        _, old, stage = information(case, *args, r.read(covariance), r.COMMIT)
        assert np.allclose([old,stage],expected,rtol=0.,atol=1e-8), (case,old,stage)
        revised_uncertainty(case, covariance)


def revised_uncertainty(case, path):
    info = r.result(f'{case}/information.json.gz')
    covariance = r.read(path)
    multiplier = info['SE_multiplier']
    adopted = covariance['adopted_point'] if case=='MEA' else covariance
    se = adopted['conditional_standard_error']
    coordinates = list(adopted['free_coordinates'])
    errors = np.array([se[q] for q in coordinates])
    physical = np.asarray(adopted['conditional_correlation'])*np.outer(errors,errors)
    revised = dict(coordinates=coordinates, adopted_point=dict(
        original=physical, stage=physical*multiplier**2, correlation=adopted['conditional_correlation']))
    table = [dict(parameter=q, original_SE=v, stage_SE=v*multiplier) for q,v in se.items()]
    if case == 'MEA':
        native = covariance['native']
        variance = native['variance_factor']
        stage = (variance*info['denominator'] - (info['rss']-info['stage_rss']))/info['stage_denominator']
        native_factor = math.sqrt(stage/variance)
        # The native physical array also includes tied and reaction targets.
        # Use the ten independent optimizer coordinates as in uncertainty_307.
        scales = {q['identity']:q['scale'] for q in info['coordinates']}
        native_physical = np.asarray(native['optimizer']).reshape(physical.shape)*np.outer(
            [scales[q] for q in coordinates],[scales[q] for q in coordinates])
        assert np.allclose(np.sqrt(np.diag(native_physical)*variance),covariance['native_standard_errors'],rtol=1e-12)
        revised['native'] = dict(original_variance=variance,stage_variance=stage,
                                 original=native_physical*variance, stage=native_physical*stage,
                                 correlation=covariance['native_correlation'])
        table = [dict(v, native_stage_SE=float(v['native_SE_bound_fixed'])*native_factor,
                      adopted_point_stage_SE=float(v['adopted_point_SE_bound_fixed'])*multiplier)
                 for v in f.e.rows(path.parent/'standard-errors.csv')]
        bands = f.e.rows(path.parent/'prediction-bands.csv')
        factor = native_factor if covariance['ranking_covariance'].startswith('native') else multiplier
        for v in bands:
            spread = float(v['SE_bound_fixed'])*factor
            v.update(stage_SE=spread,stage_lower_95=float(v['value'])-1.96*spread,stage_upper_95=float(v['value'])+1.96*spread)
        f.e.table(OUT/case/'prediction-bands.csv',bands)
        ranking = r.read(path.parent/'ranking.json')
        for v in ranking:
            v['stage_max_fractional_change'] = v['max_fractional_change']*(multiplier if v['SE_bound_fixed'] is not None else 1)
        f.e.table(OUT/case/'ranking.csv',sorted(ranking,key=lambda v:v['stage_max_fractional_change'],reverse=True))
    r.write(f'{case}/covariance.json',revised)
    f.e.table(OUT/case/'standard-errors.csv',table)


def alternative_rows(spec):
    rows = spec.inputs['observations']['fitted']
    assert Counter(v['kind'] for v in rows if v['group'] == 'Cai') == {'temperature': 25, 'mole_fraction': 25}
    assert all(v['weight'] == 1 for v in rows if v['group'] == 'Cai')
    return [dict(v, weight=1/25) if v['group'] == 'Cai' else v for v in rows]


def alternative(mea):
    old = r.result('reported-mea.json.gz')['rows']
    rows, ok, cost = r.replay(mea, alternative_rows)
    r.write('alternative/f2-replay.json.gz', dict(rows=rows, available=ok, cost=cost))
    assert ok and abs(cost - 62.79686582) < 1e-8
    for a,b in zip(old,rows,strict=True):
        assert all(a[k] == b[k] for k in ('identity','value','residual'))
        assert math.isclose(a['weighted_residual']/(5 if a['group']=='Cai' else 1), b['weighted_residual'], rel_tol=1e-14)
    declared = r.read(BASE/'F2/current/unpenalized/declaration.json')['declared']
    coordinates = [q['identity'] for q in declared]
    ties = {q['identity']: [t for t in q['targets'] if t[0]=='born_diameter']
            for q in declared if any(t[0]=='born_diameter' for t in q['targets'])}
    assert len(coordinates)==11 and len(ties)==2
    starts = {'previous': s.parameter_mapping(BASE/'F1/parameters.json'),
              'current': s.parameter_mapping(f.a.RECORDS['candidate'])}
    endpoints = []
    for label in ('previous','current','reported-restart'):
        if label == 'reported-restart' and any(p['eligible'] and p['cost'] <= cost*(1+1e-6) for p in endpoints):
            break
        start = starts.get(label,mea)
        values = s.parameter_values(start)
        if label in starts:
            assert all(values[q['identity']]==q['origin'] for q in r.read(BASE/f'F2/{label}/unpenalized/declaration.json')['declared'])
        start = s.with_parameter_values(start,{q.replace('segment_diameter','born_diameter'): values[q] for q in ties})
        signature = dict(wheel=r.SHA, start=s.parameter_fingerprint(start), fixed=f.LITERATURE,
                         rows=alternative_rows(r.bind(start)), controls=r.read(r.A6)['controls'], coordinates=declared)
        digest = hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()
        name = f'alternative/{label}-{digest}'
        r.write(f'{name}/inputs.json.gz', signature)
        mapping, report = f.fit(name,start,f.LITERATURE,coordinates,ties,rows=alternative_rows)
        replay = r.read(OUT/name/'replay.json') if (OUT/name/'replay.json').exists() else {}
        eligible = bool(mapping and report['status']=='converged' and replay['available'] and len(replay['rows'])==307)
        endpoints.append(dict(start=label, run=name, mapping=mapping, eligible=eligible, cost=replay.get('cost'),
                              status=report['status'] if report else None, message=report['message'] if report else None))
    ranked = sorted((p for p in endpoints if p['eligible']), key=lambda p:p['cost'])
    best = ranked[0] if ranked else None
    r.write('alternative/selection.json',dict(starts=endpoints, selected=best,
            tie=len(ranked)>1 and ranked[1]['cost']-best['cost']<=1e-6*best['cost']))
    assert best and best['cost'] <= cost*(1+1e-6), endpoints
    mapping = best['mapping']
    other, ok, original = r.replay(mapping)
    assert ok
    effective = r.read(OUT/best['run']/'replay.json')['rows']
    values, initial = s.parameter_values(mapping), s.parameter_values(mea)
    units = {q['identity']:q['value']['unit'] for item in mapping['components']+mapping['pairs'] for q in item['coefficients']}
    parameters = []
    for q in declared:
        k = q['identity']
        bound = lambda value: next((side for side,b in zip(('lower','upper'),q['bounds']) if abs(value-b)<=1e-6*q['scale']), None)
        parameters.append(dict(identity=k,unit=units[k],reported=initial[k],alternative=values[k],change=values[k]-initial[k],
                               reported_bound=bound(initial[k]),alternative_bound=bound(values[k])))
    diameters = {q.replace('segment_diameter','born_diameter'): [initial[q],values[q]] for q in ties}
    assert all(values[k]==v[1] for k,v in diameters.items())
    def costs(values):
        return {label:math.fsum(v['cost'] for v in values if v['group']==group and (quantity is None or quantity in v['row'].values()))
                for label,group,quantity,_ in r.GROUPS}
    r.write('alternative/cross-score.json.gz',dict(parameters=parameters,born_diameters_angstrom=diameters,rows=other,
            objectives=[[math.fsum(v['cost'] for v in old),cost],[original,best['cost']]],
            groups=[[costs(old),costs(rows)],[costs(other),costs(effective)]]))


def selected():
    return r.result('alternative/selection.json')['selected']['mapping']


def assessment(record, task):
    import final_evidence as evidence

    kind, observation = task
    try:
        row, _ = evidence.job('Held', str(record), kind, observation, output_dir=ROOT/'tmp/objective-weights-420'/record.stem)
        return dict(identity=observation['identity'], targets=evidence.score_rows('Held',[row]))
    except (AssertionError, ValueError, RuntimeError, r.epcsaft.EosError) as error:
        return dict(identity=observation['identity'], targets=[], message=f'{type(error).__name__}: {error}')


def deviations(rows, key):
    pairs = [(v['observed'], v[key]) for v in rows if v[key] is not None]
    stats = deviation_statistics(pairs) if pairs else {}
    return dict(declared=len(rows), available=len(pairs), relative_eligible=stats.get('relative_rows', 0),
                aard=stats.get('AARD_percent'), relative_bias=stats.get('bias_percent'),
                rmse=math.sqrt(math.fsum((p-o)**2 for o,p in pairs)/len(pairs)) if pairs else None)


def carbonate_measurement(declaration, target):
    species = {'bicarbonate-anion': 'HCO₃⁻', 'carbonate-anion': 'CO₃²⁻'}
    components = declaration['arguments'].get('species', [])
    if declaration['kind'] == 'mole_fraction' and set(components) == species.keys():
        assert target['basis'] == 'true-species-liquid-mole-fraction-linear-aggregate', target
        return dict(basis=target['basis'], measured=' + '.join(species.values()))
    return {}


def fitted_species_label(row):
    return f"fitted {row['source']} {row.get('measured', row['species'])} {row['basis']}"


def comparison_groups(data):
    grouped = defaultdict(list)
    for row in data:
        a, b = row['reported'], row['alternative']
        row['change'] = b-a if a is not None and b is not None else None
        for label in row['groups']:
            grouped[label].append(row)
    summary = {}
    for label, rows in grouped.items():
        paired = [v for v in rows if v['reported'] is not None and v['alternative'] is not None]
        old, new = (deviations(paired,k) for k in ('reported','alternative'))
        summary[label] = dict(reported=deviations(rows,'reported'),alternative=deviations(rows,'alternative'),
                              paired_reported=old,paired_alternative=new,
                              aard_change_pp=new['aard']-old['aard'] if old['aard'] is not None else None,
                              availability_changes=[v['identity'] for v in rows if (v['reported'] is None)!=(v['alternative'] is None)],
                              largest_change=max(paired,key=lambda v:abs(v['change']),default=None))
    return summary


def observable_errors(summary):
    return [
        dict(group=label,unit=group['largest_change']['unit'] if group['largest_change'] else None,
             aard_change_pp=group['aard_change_pp'],
             **{f'{basis}_{metric}':value for basis in ('reported','alternative','paired_reported','paired_alternative')
                for metric,value in group[basis].items()})
        for label,group in summary.items()]


def compare():
    import final_evidence as evidence

    historical = EVIDENCE
    targets = f.e.rows(historical/'state-targets.csv')
    _, groups = evidence.observations()
    spec = r.read(f.e.SPEC)
    requests = r.read(ROOT/spec['state_requests_path'])
    fitted = {v['identity'] for v in r.result('reported-mea.json.gz')['rows']}
    wanted = {(v['kind'],v['identity']) for v in targets if v['target'] not in fitted
              and (v['kind']!='packet' or v['quantity']!='pressure')}
    tasks = [(kind,dict(o,request=requests.get(o['identity'],o['request'])))
             for kind,observations in groups.items() for o in observations if (kind,o['identity']) in wanted]
    assert {(k,o['identity']) for k,o in tasks} == wanted
    alternative_record = OUT/'alternative/parameters.json'
    s.write_json(alternative_record,selected())
    replay = [r.result('reported-mea.json.gz')['rows'], r.result('alternative/cross-score.json.gz')['rows']]
    predictions, failures = [], []
    for record in (paper.RECORD,alternative_record):
        with ProcessPoolExecutor(r.CORES) as pool:
            results = list(pool.map(partial(assessment,record),tasks))
        predictions.append({(v['kind'],v['identity'],v['target']):v for x in results for v in x['targets']})
        failures.append({v['identity']:v['message'] for v in results if 'message' in v})
    data = []
    canonical = {v['observation_id']:v for v in f.e.rows(ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
    roles = r.read(historical/'state-summary.json')['scores']
    def add(v, labels):
        v['groups'] = labels
        data.append(v)
    for row in targets:
        key = row['kind'],row['identity'],row['target']
        kind, _, target = key
        if target in fitted or (kind=='packet' and row['quantity']=='pressure'):
            continue
        new = [v.get(key) for v in predictions]
        for v in filter(None,new):
            assert all(v[k]==row[k] for k in ('basis','source','species'))
            assert float(row['observed'])==v['observed'] and float(row['temperature_K'])==v['temperature_K']
        measured = ('HCO₃⁻ + CO₃²⁻' if row['species']=='HCO3-' and row['basis'].endswith('linear-aggregate')
                    else row['species'])
        labels = [f"unfitted {row['source']} {measured} {row['basis']}"] if kind!='transfer' else []
        if kind in ('canonical','wagner'):
            labels += ['unfitted six-source pressures' if kind=='canonical' else 'Wagner pressures']
        labels += [label for label in ('transfer 15 wt%','transfer 45 wt%','Matin 19 pools')
                   if target in roles[label]['row_ids'] and kind==('transfer' if label.startswith('transfer') else 'packet')]
        source = canonical.get(target.removesuffix('-pco2'),{})
        add(dict(row, observed=float(row['observed']),historical=float(row['predicted']),role='unfitted',measured=measured,
                 unit='Pa' if row['quantity']=='pressure' else 'dimensionless',
                 mea_mass_fraction=source.get('MEA_weight_fraction'),
                 reported=new[0]['predicted'] if new[0] else None,alternative=new[1]['predicted'] if new[1] else None),labels)
    metadata = {v['target']:v for v in sorted(targets,key=lambda v: v['kind']=='canonical')}
    declarations = r.read(paper.OUT/'objective-declarations.json')
    published = r.read(paper.OUT/'candidate/replay.json')['rows']
    for a,b,decl,ref in zip(*replay,declarations,published,strict=True):
        identity = a['identity']
        assert identity==decl['identity']==ref['identity']
        assert all(a.get(k)==b.get(k) for k in ('identity','unit','observed','row','basis'))
        row = a['row']
        label, = [label for label,group,quantity,_ in r.GROUPS if a['group']==group and (quantity is None or quantity in row.values())]
        source = metadata.get(identity,{})
        labels = ['fitted '+(f"Cai {row['quantity']}" if a['group']=='Cai' else label)]
        if label=='fitted CO2 partial pressure':
            labels.append(f"fitted {source['source']} pCO2")
        if 'mole fraction' in label or label in ('restored species','Jakobsen ratio'):
            basis = 'moles per mole total amine' if label=='Jakobsen ratio' else 'true liquid mole fraction'
            measurement = carbonate_measurement(decl, source)
            source = dict(source,basis=basis,source=identity.split('_')[0],species=identity.split('::')[-1])
            source.update(measurement)
            labels.append(fitted_species_label(source))
        add(dict(source,identity=identity,kind='fitted',role='fitted',target=identity,observed=a['observed'],
                 unit=UNITS.get(decl['constructor'],UNITS.get(decl['kind'],'dimensionless')),historical=ref['value'],
                 row=row,mea_mass_fraction=canonical.get(identity.removesuffix('-pco2'),{}).get('MEA_weight_fraction'),
                 reported=a['value'],alternative=b['value']),labels)
    # The ten #338 353 K checks use the separately retained phase-amount declaration.
    bottinger = []
    for mapping in (s.parameter_mapping(paper.RECORD),selected()):
        spec = r.bind(mapping)
        bottinger.append([(v,reg.predict(spec.model,v['item'])) for v in r.bottinger_targets(spec,mapping)])
    for (a,p),(b,q) in zip(*bottinger,strict=True):
        assert a['identity']==b['identity'] and a['observed']==b['observed']
        add(dict(identity=a['identity'],kind='development check',role='unfitted',observed=a['observed'],species=a['species'],
                 unit='dimensionless',basis='true liquid mole fraction',
                 temperature_K=353.15,reported=p.value if p.requested_tolerance_met else None,
                 alternative=q.value if q.requested_tolerance_met else None,messages=[p.message,q.message]),
            ['Böttinger 353 K checks',f"Böttinger 353 K {a['species']} mole fraction"])
    summary = comparison_groups(data)
    r.write('alternative/paired-comparisons.json.gz',dict(rows=data,groups=summary,refusals=failures))
    f.e.table(OUT/'alternative/observable-errors.csv', observable_errors(summary))
    old = r.read(BASE/'F2/agreement.json')
    references = {v['dataset']:v for v in old}
    labels = ('fitted: fitted CO2 partial pressure','not fitted: six-source pressures','fitted: Cai temperature','fitted: Cai mole_fraction')
    readback = []
    for label,field,expected,n in zip(labels,('aard_percent','aard_percent','rmse','rmse'),
                                     (11.6416,24.8871,1.78491,.0203583),(47,112,25,25),strict=True):
        ref = references[label]
        new = summary[label.replace('not fitted: ','unfitted ').replace('fitted: ','fitted ')]['reported']
        actual = new['aard' if field=='aard_percent' else field]
        assert ref['n']==new['declared']==n and math.isclose(ref[field],expected,rel_tol=5e-6)
        readback.append(dict(group=label,n=n,metric=field,historical=ref[field],study_wheel=actual,change=actual-ref[field]))
    r.write('alternative/published-readback.json',readback)


def search():
    mapping = selected()
    main, offset = r.states()
    if sys.argv[1] == 'time-search':
        registry = r.read(BASE/'split-registry.json')['trials']
        r.census(mapping,'timing',{'40':registry},indices=[40],keep_refusals=True,compact_supplied=True,confirm=census_classify)
        return
    mea_search('alternative',mapping,None,output=OUT/'alternative',confirm=census_classify)
    rows = r.result('search/grid.json.gz')
    phases = grid_classify(mapping, rows, main+offset)
    r.write('search/grid-classification.json.gz', phases)
    search_counts()


def search_counts():
    r.OUT = OUT/'alternative'
    r.write('search/outcomes.json', search_accounting(r.result, r.result('search/census-raw.json.gz')))


def search_accounting(result, census_raw):
    rows = result('search/grid.json.gz')
    phases = {v['key']:v for v in result('search/grid-classification.json.gz')}
    raw = {v['index']:v for v in census_raw}
    census = result('search/census.json')['rows']
    search_summary = result('search/summary.json')
    baseline = r.read(BASE.parent/'wheel-recheck-05e94210/stability-adopted-law/search.json')
    summary, changed = {}, []
    main_count = search_summary['grid']['states']
    for label, bank in (('grid',rows[:main_count]),('offset',rows[main_count:]),('census',census)):
        counts = Counter(states=len(bank),parents_available=0,descents=0,confirmed=0,
                         unconfirmed=0,failed_solves=0,unresolved=0,unavailable=0,clear=0)
        for row in bank:
            is_census = label=='census'
            key = row['index'] if is_census else row['key']
            available = row['parent_admitted'] if is_census else row.get('parent',{}).get('success',False)
            complete = row['complete'] if is_census else available and row['available']
            descent = bool(row['resolved'] or row['supplied_negative']) if is_census else r.descent(row)
            classified = raw[key].get('coexistence',[]) if is_census else phases.get(key,{})
            if is_census:
                assert len(classified)==row['resolved']+row['supplied_negative'], key
                outcomes = Counter(attempt_outcome(q['attempt']) if 'attempt' in q else q['outcome'] for q in classified)
            else:
                assert bool(classified)==descent, key
                outcomes = Counter(map(attempt_outcome, classified.get('attempts', [])))
                outcomes['unavailable'] = int('classification_error' in classified)
            state = ('confirmed' if outcomes['confirmed'] else 'unavailable' if not complete or outcomes['unavailable']
                     else 'unresolved' if descent else 'clear')
            counts.update({state:1})
            counts['parents_available'] += available
            counts['descents'] += descent
            counts['unconfirmed'] += outcomes['unconfirmed']
            counts['failed_solves'] += outcomes['failed_solve']
            if state!='clear':
                changed.append(dict(group=label,key=key,outcome=state,available=available,complete=complete,
                                    descent=descent,attempts=dict(outcomes)))
        assert counts['states']==sum(counts[k] for k in ('confirmed','unavailable','unresolved','clear'))
        assert counts['states']==baseline[label]['states']
        summary[label] = dict(counts)
    supplied = dict(search_summary['supplied'], missing=search_summary['missing_supplied'],
                    negative=sum(v['supplied_negative'] for v in census))
    return dict(baseline=baseline,alternative=summary,supplied=supplied,changed=changed)


if __name__ == '__main__':
    mea = setup()
    if sys.argv[1] == 'control':
        control(mea)
    elif sys.argv[1] == 'audit':
        audit(mea)
    elif sys.argv[1] == 'handoff':
        handoff()
    elif sys.argv[1] == 'fit':
        alternative(mea)
    elif sys.argv[1] in ('search','time-search'):
        search()
    elif sys.argv[1] == 'compare':
        compare()
    elif sys.argv[1] == 'search-counts':
        search_counts()
