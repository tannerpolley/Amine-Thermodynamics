"""MEA objective weighting and information audit (#420)."""
# ruff: noqa: E402
import hashlib
import json
import math
from collections import defaultdict
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'mdea_mea_workflow/scripts'))
from shared_bicarbonate_417 import BASE, ROOT, bind_wheel, compare_rows, f, paper, r, s
from classify_descents import classify, coexistence, gibbs, pressure_roots
from part_ii import Route, branch_counts, np, reg

OUT = BASE.parent/'objective-weights-420'
STATE = 'dense|0.15|313.15|0.125|1.05'


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


def census_classify(model, parent, result, report, registry):
    spec = SimpleNamespace(model=model, parameters=model.parameters)
    parent = parent._native(model)
    supplied = [(dict(bank_index=t['bank_index']), registry[t['bank_index']])
                for t in report['supplied_trials'] if r.supplied_negative(t)]
    native = [(dict(native_index=i), dict(t['phase'], composition=t['composition'], packing=math.exp(t['split_coordinates'][-1])))
              for i, t in enumerate(report['trials']) if t['resolved_descent']]
    outcomes = []
    for identity, seed in native + supplied:
        entry = dict(identity, seed=seed)
        outcomes.append(entry)
        try:
            assert result.requested_tolerance_met, result.message
            assert parent.pressure.value == result.pressure
            donor = next(i for i, phase in enumerate(parent.phases) if phase.kind.name.lower() == 'liquid')
            primary = list(result.phase_mole_fractions(donor)), result.packing_fractions[donor]
            entry['parent_roots'] = pressure_roots(model, result.temperature, result.pressure, primary[0], result.molar_densities[donor])
            attempt = coexistence(spec, parent, gibbs(r.eq.compile_problem(model, parent), result),
                                  [primary, (seed['composition'], seed['packing'])])
            entry.update(attempt=attempt, outcome='confirmed' if attempt['confirmed'] else 'unconfirmed')
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
    spec = route.bind(point)
    declared, records = point['coordinates'], spec.inputs['observations']['fitted']
    ev = reg.differentiate(spec.parameters, spec.coordinates(), [spec.observation(v) for v in records],
                           optimizer=[0.]*len(declared), thermochemistry=spec.thermal)
    replay, ok, _ = route.replay(point)
    assert ok and all(status.name == 'Available' for status in ev.statuses)
    for saved, value, record in zip(rows, replay, records, strict=True):
        assert saved['identity'] == value['identity'] == record['identity']
        assert float(saved['observed']) == value['observed'] and saved['unit'] == value['unit']
        assert f.a.relative(saved['value'], value['value']) <= 1e-8
        assert 'residual' not in saved or f.a.relative(saved['residual'], value['residual']) <= 1e-8
    assert np.allclose(ev.predictions, [v['value'] for v in replay], rtol=1e-8, atol=0.)
    return spec, replay, declared, ev.residual_optimizer_gradient


def pure_water_control(spec, rows, coords, jacobian):
    J = np.array(jacobian).reshape(len(rows), len(coords))
    records = spec.inputs['observations']['fitted']
    matches = []
    for row, record, gradient in zip(rows, records, J, strict=True):
        if record['row'].get('liquid_x_MDEA') != '0':
            continue
        problem = spec.problems[record['problem']]
        matches.append(dict(identity=row['identity'], source_row=record['row'], feed=problem.feed.values,
                            phases=[dict(name=v.name, support=v.support) for v in problem.phases],
                            weight=record['weight'], predicted=row['value'], observed=row['observed'], cost=row['cost'],
                            optimizer_residual_derivatives=dict(zip([c['identity'] for c in coords], gradient, strict=True))))
    cost = math.fsum(x['cost'] for x in rows)
    zero_rows = [v['identity'] for v,g in zip(rows,J,strict=True) if not np.any(g)]
    r.write('MDEA/pure-water-derivative-control.json', dict(rows=matches,declared=len(rows),objective=cost,
            pure_water_cost=math.fsum(x['cost'] for x in matches),all_row_scale=2*cost/(len(rows)-6),exact_zero_rows=zero_rows))
    assert [v['identity'] for v in matches] == zero_rows == ['fit:227', 'fit:229', 'fit:249'], '#420 MDEA pure-water derivative control'


def information(case, spec, rows, coords, jacobian, covariance, wheel):
    records = spec.inputs['observations']['fitted']
    assert len({v['identity'] for v in rows}) == len(rows)
    e = spec.whiten(np.array([v['residual'] for v in rows]))
    J = spec.whiten(np.asarray(jacobian, dtype=np.float64).reshape(len(rows), len(coords)))
    scales = np.array([q['scale'] for q in coords])
    interior = [i for i,q in enumerate(coords) if min(q['origin']-q['bounds'][0], q['bounds'][1]-q['origin']) > 1e-6*q['scale']]
    groups, detail, excluded = defaultdict(list), [], []
    targets = {v['target']: v['source'] for v in f.e.rows(paper.OUT/'paper-evidence/state-targets.csv')}
    for i, (v, rec) in enumerate(zip(rows, records, strict=True)):
        assert v['identity'] == rec['identity'] and v['group'] == rec['group']
        source = targets.get(v['identity'], rec['row'].get('source_key') or rec['row'].get('source') or v['identity'].split(':')[0].split('_')[0].rsplit('-',1)[0])
        quantity = rec['kind']
        groups[(v['group'], source, quantity)].append(i)
        detail.append(dict(v, source=source, observable=quantity, weight=rec['weight'], scale=rec['arguments'].get('scale',rec['row'].get('scale',1.)),
                           form=rec['arguments'].get('form',rec['row'].get('form')), cost=.5*e[i]**2, role='fitted'))
        if (case == 'MEA' and v['group'] == 'Kiepe') or (case == 'MDEA' and rec['row'].get('liquid_x_MDEA') == '0'):
            assert not np.any(J[i])
            excluded.append(i)
    assert np.flatnonzero(~np.any(J, axis=1)).tolist() == excluded
    blocks = {str(key): ids for key, ids in groups.items()}
    for block in {v['group'] for v in rows}:
        blocks.update({block: [i for i,v in enumerate(rows) if v['group'] == block]})
    if case == 'MEA':
        blocks.update({label: [i for i,v in enumerate(rows) if v['group']==group and (quantity is None or quantity in v['row'].values())]
                       for label,group,quantity,_ in r.GROUPS})
        blocks.update({k: [i for i,d in enumerate(detail) if d['group']=='Cai' and d['observable']==k] for k in ('temperature','mole_fraction')})
        blocks['species mole fractions'] = blocks['fitted phase mole fraction'] + blocks['restored species']
    blocks['whole fit'] = list(range(len(rows)))
    ranks = {}
    for label, ids in blocks.items():
        ranks[label] = dict(n=len(ids), zero_rows=int(sum(~np.any(J[ids],axis=1))), cost=math.fsum(detail[i]['cost'] for i in ids))
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
    r.write(f'{case}/information.json.gz', dict(wheel=wheel,basis='optimizer coordinates, scaled residual weighted once',
            coordinates=coords,active_bounds=sorted(set(range(len(coords)))-set(interior)),blocks=ranks, rows=detail,
            n=n,na=na,p=p,denominator=n-p,stage_denominator=na-p,rss=rss,stage_rss=rss_stage,variance=old,
            stage_variance=stage,excluded=[detail[i] for i in excluded],SE_multiplier=math.sqrt(stage/old),
            conditional_correlation=covariance['conditional_correlation'],unscaled_information=(physical.T@physical).tolist()))
    return ranks, old, stage


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
    assert abs(old-1.0152384) < 1e-8 and abs(stage-1.1686994098) < 1e-10
    for case, dec, res, point, rows_file, expected in (
        ('DEA','dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json','dea_transfer/results/refit-413','selection.json','paper-data.csv',(.21270969,.21270969)),
        ('MDEA','mdea_mea_workflow/inputs/bounded-binary-411.json','mdea_mea_workflow/results/bounded-binary-411','endpoint.json','data-rows.json',(4.10533597,4.15061398)),
        ('AMP','amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json','amp_transfer/results/retransfer-412-f2-05e94210/slope-150','parameters.json','data-rows.json',(.82753481,.82753481)),
    ):
        args = transfer(case,dec,f'{res}/{point}',f'{res}/{rows_file}')
        if case == 'MDEA':
            pure_water_control(*args)
        _, old, stage = information(case, *args, r.read(ROOT/'analyses'/res/'conditional-uncertainty.json'), r.COMMIT)
        assert np.allclose([old,stage],expected,rtol=0.,atol=1e-8), (case,old,stage)


if __name__ == '__main__':
    mea = setup()
    if sys.argv[1] == 'control':
        control(mea)
    elif sys.argv[1] == 'audit':
        audit(mea)
    elif sys.argv[1] == 'handoff':
        handoff()
