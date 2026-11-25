"""Recompute keyed property, Kuranov and curve comparisons at retained endpoints."""
from concurrent.futures import ProcessPoolExecutor
import csv
from hashlib import sha256
import json
import multiprocessing
from time import monotonic
from types import SimpleNamespace
from unittest.mock import patch

from refit import MEA, OUT, WORK, P_REF, a, eq, fingerprint, put, r, save
from phase_replays import baseline_screen, controls, point_for, release_routes
from round_8.records import Sources, blob

MDEA_CURVES = 'analyses/mdea_mea_workflow/results/salt-anchored-435/curve-data.json'


def mdea_curve_declarations(run, point):
    declaration = run.config['curve_rows']
    source = str((run.path.parent/declaration['path']).relative_to(r.ROOT))
    data = blob(source,'4c923137a')
    assert sha256(data).hexdigest()==declaration['sha256']
    old = r.read(r.ROOT/MDEA_CURVES)['rows']
    templates = {q['observation']['group']:q for q in json.loads(data)}
    spec = run.bind(point)
    observations = {(q['group'],fingerprint(q['row'])):q for role in ('fitted','comparisons')
                    for q in spec.inputs['observations'][role]}
    result = []
    for row in old:
        group = row['group']
        _,T,water = row['curve'].split(':')
        source = observations[group,fingerprint(row['row'])]
        base = spec.problems[source['problem']]
        declared, = templates[group]['problems'].values()
        assert row['basis']==source['basis'] and declared['template']=='loaded-bubble'
        key = row['identity']+':problem'
        bindings = dict(declared['bindings'],T=float(T),P=base.P.guess,water=float(water),alpha=row['loading'])
        observation = dict(source,identity=row['identity'],problem=key,observed=row['observed'])
        result.append(dict(curve=row['curve'],loading=row['loading'],observation=observation,
                           problems={key:dict(template=declared['template'],bindings=bindings)}))
    assert len(result)==483
    return result


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
            curves = run.curves(point,declarations=mdea_curve_declarations(run,point))
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


def mdea_curves(pilot, label='selected'):
    route,point = point_for('MDEA',label if label!='archive' else 'tracking','retained-curve-comparison-'+label)
    if label=='archive':
        from calculations import mdea_incumbent
        point,_ = mdea_incumbent('salt')
        assert r.s.parameter_fingerprint(point['parameters'])==r.read(r.ROOT/MDEA_CURVES)['point_fingerprint']
    declarations = mdea_curve_declarations(route,point)
    batch = 24
    for offset in range(0,batch if pilot else len(declarations),batch):
        root = 'MDEA/curves' if label=='selected' else f'MDEA/curves/{label}'
        path = f'{root}/batch-{offset:03}.json.gz'
        if (OUT/path).exists():
            assert r.read(OUT/path)['endpoint_fingerprint']==fingerprint(point)
            continue
        start = monotonic()
        rows = route.curves(point,declarations=declarations[offset:offset+batch])
        put(path,dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows=rows,seconds=monotonic()-start))
        print(label,offset,len(rows),monotonic()-start,flush=True)


def search_inventory(design):
    _,point = point_for(design,'selected','search-inventory')
    for protocol,run,bank in release_routes(design,'search-inventory'):
        path = OUT / design / f'screen/selected/{protocol}/summary.json.gz'
        if not path.exists():
            continue
        retained = r.read(path)
        spec = run.bind(point)
        old_run,old_point = point_for(design,'tracking','search-inventory')
        old_spec = old_run.bind(old_point)
        states = {q['key']:q for q in run.states(spec)}
        calculated = []
        absolute_bubbles = {}
        baseline = baseline_screen(design,protocol)
        for row in retained['rows']:
            state = states[row['key']]
            archived = baseline[row['key']]
            record = dict(key=row['key'],state=state)
            try:
                item = run.stability_row(spec,state,1.)
                assert all(rx.reference.reference_pressure_pa==P_REF for rx in item.problem.reactions)
                record.update(T_K=run.temperature(spec,state),feed_mol=list(item.problem.feed.values),
                              initialization=[dict(kind=p.kind.name, composition=p.composition_guess,
                                                   packing=p.packing_guess) for p in item.problem.phases])
                if item.pressure_reference is not None:
                    assert all(rx.reference.reference_pressure_pa==P_REF for rx in item.pressure_reference.reactions)
                    ratio = item.pressure_ratio
                    old_P = archived.get('pressure_Pa')
                    new_P = row.get('pressure_Pa')
                    record.update(pressure_basis='bubble scaled',pressure_ratio=ratio,
                                  old_bubble_Pa=old_P,bubble_Pa=new_P,
                                  old_search_Pa=old_P*ratio if old_P else None,
                                  search_Pa=new_P*ratio if new_P else None)
                else:
                    canonical = row.get('same_calculation_as',row['key'])
                    if canonical not in absolute_bubbles:
                        prior_item = old_run.stability_row(old_spec,state,1.)
                        assert prior_item.problem.pressure.value==item.problem.pressure.value
                        no_reference = SimpleNamespace(pressure_reference=None)
                        before = archived.get('pressure_basis') or old_run.pressure_basis(old_spec,state,prior_item,no_reference)
                        after = row.get('pressure_basis') or run.pressure_basis(spec,state,item,no_reference)
                        absolute_bubbles[canonical] = before,after
                    before,after = absolute_bubbles[canonical]
                    record.update(pressure_basis='declared absolute',declared_pressure_Pa=item.problem.pressure.value,
                                  old_bubble_Pa=before.get('model_bubble_pressure_Pa'),
                                  bubble_Pa=after.get('model_bubble_pressure_Pa'),
                                  old_bubble_status=before.get('message'),bubble_status=after.get('message'))
            except (AttributeError, RuntimeError,ValueError) as error:
                record['refusal'] = f'{type(error).__name__}: {error}'
            calculated.append(record)
        put(f'{design}/screen/selected/{protocol}/state-inventory.json.gz',
            dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,rows=calculated,bank_fingerprint=fingerprint(bank)))


def mdea_witnesses():
    from round_8.replay import mdea_witnesses as readback

    started = monotonic()
    root = 'MDEA/screen/selected/declared'
    run,point = point_for('MDEA','selected','measured-witnesses')
    summary = r.read(OUT/root/'summary.json.gz')
    states = r.read(OUT/root/'state-inventory.json.gz')
    assert (summary['endpoint_fingerprint']==states['endpoint_fingerprint']==fingerprint(point))
    state_by_id = {q['key']:q for q in states['rows']}
    rows = [dict(q,pressure_basis=dict(model_bubble_pressure_Pa=state_by_id[q['key']].get('bubble_Pa'),
                      search_pressure_Pa=state_by_id[q['key']].get('search_Pa') or state_by_id[q['key']].get('declared_pressure_Pa')))
            for q in summary['rows']]
    output = {}

    def work(key,kind,fn,_remaining):
        t = monotonic()
        record = dict(kind=kind)
        try:
            record['value'] = fn()
        except (RuntimeError,ValueError,AttributeError,IndexError,AssertionError) as exc:
            record['refusal'] = f'{type(exc).__name__}: {exc}'
        output[key] = dict(record,seconds=monotonic()-t)
        put(f'{root}/witness-readbacks.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
            rows=output,seconds=monotonic()-started))

    readback(Sources(),work,released=(run,point,rows,summary['classifications']))


def fixed_native_reference():
    original = r.s._reaction_reference

    def pinned(declaration, name):
        reference = original(declaration,name)
        return eq.ReactionReference(reference.source_basis,reference_pressure_pa=P_REF)

    return patch.object(r.s,'_reaction_reference',pinned)


def mea_heat():
    from stripper_temperature_409 import replay

    _,point = point_for('MEA','selected','heat-comparison')
    start = monotonic()
    work = WORK/'MEA/heat'
    mapping = work/'endpoint.json'
    save(mapping,point['parameters'])
    producer = r.B/'scripts/kim2007_heat_pathways.py'
    with fixed_native_reference():
        replay(r.ROOT,mapping,r.s.sha256(mapping),MEA.parent/'evidence/F4',work,
               control=False,producer_sha=r.s.sha256(producer))
    result = r.read(work/'heat-replay.json')
    assert result['engine_wheel_sha256']==r.SHA
    put('MEA/heat-comparison.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
        reaction_reference_pressure_Pa=P_REF,rows=result,seconds=monotonic()-start))


def mea_curves():
    from stripper_temperature_409 import load

    _,point = point_for('MEA','selected','curve-comparisons')
    work = WORK/'MEA/curves'
    mapping = work/'endpoint.json'
    old = MEA.parent/'evidence/F4'
    save(mapping,point['parameters'])
    with fixed_native_reference():
        producer = load('model_curves',r.B/'scripts/model_curves.py',[
            ("BUNDLE / 'results/engine-3e83e19c-paper-evidence'",f'Path({str(old)!r})'),
            ("BUNDLE / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'",
             f'Path({str(mapping)!r})')])
        producer.RUNS = work/'runtime'
        fields = dict(T='temperature_K',P='pressure_Pa',a='analytical_loading',
                      w='mea_mass_fraction',x='liquid_mea_mole_fraction')
        with ProcessPoolExecutor(r.CORES,mp_context=multiprocessing.get_context('fork')) as pool:
            for family in producer.GRIDS:
                start = monotonic()
                path = old/'model-curves'/f'{family}.csv'
                prior = list(csv.DictReader(path.read_text().splitlines()))
                states = {}
                for row in prior:
                    state = {key:float(row[col]) for key,col in fields.items() if row.get(col)}
                    if family=='mea-water':
                        state.pop('T',None)
                    if family=='pressure':
                        state.pop('P',None)
                    state['sampling'] = row['sampling']
                    states[tuple(state.items())] = state
                predictions = [q for values in pool.map(producer.run,[family]*len(states),states.values()) for q in values]
                assert len(predictions)==len(prior)
                put(f'MEA/curves/{family}.json.gz',dict(endpoint_fingerprint=fingerprint(point),wheel=r.SHA,
                    pressure_reference_Pa=P_REF,rows=predictions,source_sha256=r.s.sha256(path),
                    source=str(path.relative_to(r.ROOT)),seconds=monotonic()-start))


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
        elif design=='MEA-curves':
            mea_curves()
        elif design=='MEA-Hong':
            mea_hong_population()
        elif design in ('MDEA-curves-pilot','MDEA-curves'):
            mdea_curves(design.endswith('pilot'))
        elif design=='MDEA-curve-controls':
            mdea_curves(True,'archive')
            for label in ('tracking','fixed-at-old'):
                mdea_curves(False,label)
        elif design.endswith('-inventory'):
            search_inventory(design.removesuffix('-inventory'))
        elif design=='MDEA-witnesses':
            mdea_witnesses()
        elif design.endswith('-tracking'):
            controls(design.removesuffix('-tracking'),'tracking')
        else:
            run(design)
            if r.read(OUT/f'{design}/selection.json')['selected'] is not None:
                search_inventory(design)
