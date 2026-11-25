"""Recompute keyed property, Kuranov and curve comparisons at retained endpoints."""
from hashlib import sha256
import json
from time import monotonic
from unittest.mock import patch

from refit import MEA, OUT, WORK, P_REF, a, eq, fingerprint, put, r, save
from phase_replays import controls, point_for, release_routes
from round_8.records import Sources, blob


def mdea_82nd(run, spec):
    # Reuse the S31 row-72 construction with the fixed-reference template.
    retained = Sources().core('H/kuranov-82nd.json')['row']
    assert retained['source_row']==72
    comparison = next(q for q in spec.inputs['observations']['comparisons'] if q['group']=='Kuranov-413K')
    dataset = next(d for d in spec.spec['datasets'] if d['name']=='outside-fit-Kuranov-413K')
    key = 'kuranov:72'
    state = dict(T=retained['T'],P=retained['p_exp'],water=1/.01801528/retained['m_mdea'],
                 alpha=retained['alpha'],observed=retained['p_exp'],scale=1.)
    problem = spec.problem(dataset['template'],state)
    assert all(rx.reference.reference_pressure_pa==100000. for rx in problem.reactions)
    spec.problems[key] = problem
    args = spec.bind(dataset['arguments'],state)
    assert args==retained['salt_anchored']['basis']['arguments']
    row = dict(comparison,identity=key,problem=key,row={'source_row':'72'},arguments=args,group='Kuranov-393K',
               role='not fitted',basis=dict(comparison['basis'],arguments=args,template=dataset['template']))
    return dict(spec.prediction(row),declaration=run.stability_metadata(spec,run.stability_row(spec,dict(problem=key),1.)))


def compare_rows(run, point, label):
    started = monotonic()
    rows = run.reduce(point)
    spec = run.bind(point)
    extra = mdea_82nd(run,spec) if run.config['amine']=='methyldiethanolamine' else None
    curves = []
    if label=='selected' and 'curve_rows' in run.config:
        if run.config['amine']=='diethanolamine':
            declarations = [q for q in run.load(run.config['curve_rows'])
                            if q['observation']['group'] in ('Lawson','Lawson-394K','SeoHong','Lal')]
            assert len(declarations)==275
            curves = run.curves(point,declarations=declarations)
        elif run.config['amine']=='methyldiethanolamine':
            declaration = run.config['curve_rows']
            source = run.path.parent/declaration['path']
            archive = '4c923137a'
            data = blob(str(source.relative_to(r.ROOT)),archive)
            assert sha256(data).hexdigest()==declaration['sha256']
            curves = run.curves(point,declarations=json.loads(data))
        else:
            curves = run.curves(point)
    return dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows=rows,curves=curves,
                additional_Kuranov_72=extra,seconds=monotonic()-started)


def run(design):
    selection = r.read(OUT/f'{design}/selection.json')
    for label in ('fixed-at-old','A','B','C','selected'):
        if label=='selected' and selection['selected'] is None:
            continue
        if label in 'ABC' and not selection['attempts'][label]['endpoint']:
            continue
        path = f'{design}/property-comparisons/{label}.json.gz'
        route,point = point_for(design,label,'common-row-comparison')
        put(path,compare_rows(route,point,label))
        print(design,label,'observation and curve comparisons',flush=True)


def search_inventory(design):
    _,point = point_for(design,'selected','search-inventory')
    for protocol,run,bank in release_routes(design,'search-inventory'):
        path = OUT / design / f'screen/selected/{protocol}/summary.json.gz'
        if not path.exists():
            continue
        retained = r.read(path)
        spec = run.bind(point)
        states = {q['key']:q for q in run.states(spec)}
        calculated = []
        basis = retained['original_pressure_basis']
        for row in retained['rows']:
            state = states[row['key']]
            record = dict(key=row['key'],pressure_Pa=row.get('pressure_Pa'),
                          original=basis[row['key']], state=state)
            try:
                item = run.stability_row(spec,state,1.)
                assert all(rx.reference.reference_pressure_pa==P_REF for rx in item.problem.reactions)
                record.update(T_K=run.temperature(spec,state),feed_mol=list(item.problem.feed.values),
                              initialization=[dict(kind=p.kind.name, composition=p.composition_guess,
                                                   packing=p.packing_guess) for p in item.problem.phases])
                if item.pressure_reference is not None:
                    assert all(rx.reference.reference_pressure_pa==P_REF for rx in item.pressure_reference.reactions)
                    ratio = item.pressure_ratio
                    old_P = record['original'].get('search_pressure_Pa')
                    new_P = row.get('pressure_Pa')
                    record.update(pressure_basis='bubble scaled',pressure_ratio=ratio,
                                  old_bubble_Pa=old_P/ratio if old_P else None,
                                  bubble_Pa=new_P/ratio if new_P else None)
                else:
                    record.update(pressure_basis='declared absolute',declared_pressure_Pa=item.problem.pressure.value,
                                  bubble_Pa=row.get('pressure_basis',{}).get('model_bubble_pressure_Pa'))
            except (AttributeError, RuntimeError,ValueError) as error:
                record['refusal'] = f'{type(error).__name__}: {error}'
            calculated.append(record)
        put(f'{design}/screen/selected/{protocol}/state-inventory.json.gz',
            dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows=calculated,bank_fingerprint=fingerprint(bank)))


def mea_heat():
    from stripper_temperature_409 import replay

    _,point = point_for('MEA','selected','heat-comparison')
    start = monotonic()
    work = WORK/'MEA/heat'
    mapping = work/'endpoint.json'
    save(mapping,point['parameters'])
    producer = r.B/'scripts/kim2007_heat_pathways.py'
    original = r.s._reaction_reference

    def pinned(declaration, name):
        reference = original(declaration,name)
        return eq.ReactionReference(reference.source_basis,reference_pressure_pa=P_REF)

    with patch.object(r.s,'_reaction_reference',pinned):
        replay(r.ROOT,mapping,r.s.sha256(mapping),MEA.parent/'evidence/F4',work,
               control=False,producer_sha=r.s.sha256(producer))
    result = r.read(work/'heat-replay.json')
    assert result['engine_wheel_sha256']==r.SHA
    put('MEA/heat-comparison.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
        reaction_reference_pressure_Pa=P_REF,rows=result,seconds=monotonic()-start))


def mea_hong_population():
    import mea_pressure as pressure

    start = monotonic()
    run,point = point_for('MEA','selected','hong-comparison')
    spec = run.bind(point)
    retained = r.read(r.ROOT/'analyses/round_8/results/literature-populations.json.gz')['quantities']['hong']['rows']
    queries, _ = pressure.requests()
    template = pressure.pressure_template(spec)[0]
    population = [q for q in retained.values() if q['block']=='canonical' and q['inside_hong_grid']=='True']
    assert len(population)==132
    rows = []
    for q in population:
        key = q['record_id']
        row = pressure.pressure_record(spec,template,key,queries[key],group='Hong matched canonical')
        result = spec.prediction(row)
        assert abs(result['observed']/float(q['observed'])-1)<=1e-12
        rows.append(dict(result,role=q['adopted_role'],retained_adopted_Pa=float(q['adopted']),
                         hong_Pa=float(q['predicted']),polley_hedengren_Pa=float(q['polley_hedengren_2026'])))
    put('MEA/hong-matched.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
        rows=rows,seconds=monotonic()-start))


if __name__=='__main__':
    import sys
    a.study.reuse.bind_wheel()
    r.verify()
    for design in sys.argv[1:]:
        if design=='MEA':
            for label in ('A','B','C','fixed-at-old'):
                controls('MEA',label)
        elif design=='MEA-heat':
            mea_heat()
        elif design=='MEA-Hong':
            mea_hong_population()
        else:
            run(design)
            if r.read(OUT/f'{design}/selection.json')['selected'] is not None:
                search_inventory(design)
