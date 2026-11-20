"""Declaration transport and conditional linear-information reference for #343."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from MEA.solvent_specification import conditional_information

ROOT = Path(__file__).resolve().parents[1]
module = importlib.util.spec_from_file_location('part_ii',ROOT/'analyses/part_ii.py')
p = importlib.util.module_from_spec(module)
module.loader.exec_module(p)


def test_conditional_linear_information():
    J = np.array([[1.,0.],[0.,1.],[1.,0.],[0.,1.]])
    result = conditional_information(SimpleNamespace(physical=[0.,1.],covariance=SimpleNamespace(active_bounds=[1])),J,np.ones(4),['a','b'],[-1.,-1.],[1.,1.])
    assert result['free_coordinates']==['a']
    assert result['conditional_standard_error']['a']==pytest.approx(np.sqrt(2/3))


def test_shared_values_tie_and_range_marks(monkeypatch,tmp_path):
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json',tmp_path)
    point = route.start(route.config['reference'])
    spec = route.bind(point)
    ion = next(c for c in point['parameters']['components'] if c['component_id']==route.config['born_ties'][0])
    sizes = {c['family']:c['value']['magnitude'] for c in ion['coefficients']}
    assert sizes['born_diameter']==sizes['segment_diameter']
    shared = json.loads(p.SHARED.read_text())
    fixed = json.loads((ROOT/'analyses/solvent_specification_mea/inputs/endpoint.json').read_text())
    for component in point['parameters']['components'][:6]:
        assert component==next(c for c in fixed['components'] if c['component_id']==component['component_id'])
    for name in ('bicarbonate-anion','carbonate-anion'):
        pair = lambda mapping: next(row for row in mapping['pairs'] if {row['component_id_a'],row['component_id_b']}=={'water',name})
        assert pair(point['parameters'])==pair(fixed)
    for source in shared['reactions']:
        actual = next(row for group in point['reactions'].values() for row in group if row['name']==source['name'])
        assert actual['correlation']==source['correlation']
        bound = next(rx for problem in spec.problems.values() for rx in problem.reactions if rx.name==source['name'])
        assert all(getattr(bound.correlation,key)==value for key,value in source['correlation'].items() if key not in ('temperature_min','temperature_max'))
    assert len(point['coordinates'])==8
    assert route.marks(413.15)=={'R1':False,'R2':False,'R3':False,'MDEA-dissociation':True}
    assert len(spec.inputs['observations']['fitted'])==278
    assert all(row['unit'] and row['basis'] for role in ('fitted','comparisons') for row in spec.inputs['observations'][role])
    state = p.stable.states([{'water':10.,route.config['amine']:1.}],[1e-5,1.3])
    assert len(state)==36 and {r['c'] for r in state}=={1.05,3.}
    prediction = p.reg.predict(spec.model,route.stability_row(spec,dict(key='reference',stock={'water':10.,route.config['amine']:1.},T=313.15,a=.3,c=1.05),1e-2))
    assert prediction.status.name=='Available'
    assert prediction.value==0. and prediction.residual==0.
    native_stability = p.reg.stability
    original = []
    def stability(*args, **kwargs):
        item = native_stability(*args, **kwargs)
        original.append(p.calculation_declaration(item))
        return item
    monkeypatch.setattr(p.reg, 'stability', stability)
    loaded = dict(key='loaded',stock={'water':10.,route.config['amine']:1.},T=313.15,a=.3,c=1.05)
    item = route.stability_row(spec,loaded,1e-2)
    assert p.calculation_declaration(item)==original[-1]
    zero = route.stability_row(spec,dict(loaded,key='zero',a=0.),1e-2)
    removed = set(p.eq.compile_problem(spec.model,zero.problem).removed_species)
    assert removed
    assert [t.kind.name for t in zero.stability_options.trials]==['Liquid','Liquid','Vapor']
    assert [list(t.support) for t in zero.stability_options.trials]==[[1,4,5,6,7],[1,6],[1,6]]
    assert all(not removed.intersection(t.support) for t in zero.stability_options.trials)
    assert route.stability_metadata(spec,item)=={}
    assert route.stability_metadata(spec,zero)==dict(restricted_trial_families=True,removed_species=sorted(removed))
    route.config['reaction_ranges_K']['MDEA-dissociation'] = None
    assert route.marks(313.15)['MDEA-dissociation']=='source range unknown'
    assert set(route.marks(313.15,SimpleNamespace(reactions=[])).values())=={'reaction not used'}


def test_zero_observation_and_correlated_information():
    from MEA.solvent_specification import SolventSpecification, deviation_statistics, output_uncertainty
    result = deviation_statistics([(0.,2.),(4.,5.)],'Pa')
    assert result['relative_undefined']==1 and result['AARD_percent']==25.
    assert result['mean_abs_error']==1.5
    C = np.array([[4.,1.],[1.,9.]])
    residual = np.array([2.,3.])
    spec = SolventSpecification.__new__(SolventSpecification)
    spec.spec = {'measurement_covariance':C.tolist()}
    whitened = spec.whiten(residual)
    assert whitened@whitened==pytest.approx(residual@np.linalg.solve(C,residual))
    assert output_uncertainty(C).covariance==C.ravel().tolist()
    assert output_uncertainty(C,1).output_sigma==[2.,3.,1.]
    assert output_uncertainty(C,1).covariance==C.ravel().tolist()
    assert output_uncertainty(None) is None


@pytest.mark.parametrize('source_index',[0,1])
def test_pz_evaluated_negative_trial(source_index,monkeypatch,tmp_path):
    """#308 Hilliard 55/56 direct-distance references, checked within native numerical error."""
    import copy
    import csv
    import hashlib
    monkeypatch.syspath_prepend(str(ROOT/'analyses/pz_transfer'))
    import reactive as pz
    pz.verify_wheel()
    path = ROOT/'analyses/pz_transfer/diagnosis-308/refit-checks.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()=='d9c7054033bb58771491900f6689ce70a345ce8f4d4d03e59722f0f821481099'
    source = json.loads(path.read_text())['missed_dense_splits']
    record = source['rows'][source_index]
    row = next(r for r in csv.DictReader((pz.AN/'inputs/hilliard-d5.csv').open()) if r['row']==record['row'])
    start = p.epcsaft.Parameters.from_mapping(pz.document())
    chart,_ = pz.chart(start,[])
    native = p.reg.evaluate_coordinates(start,chart,source['endpoint_optimizer'][:9],[])
    parameters = p.epcsaft.Parameters(native.parameters,start.component_ids,start.site_ids)
    problem = pz.pressure_problem(parameters,row,source['endpoint_optimizer'][9:])
    model = p.epcsaft.Mixture(parameters)
    bubble = p.eq.solve_equilibrium(model,problem)
    assert bubble.requested_tolerance_met
    parent = copy.copy(problem)
    parent.P,parent.phases = bubble.pressure,[copy.copy(problem.phases[0])]
    parent.phases[0].amount = p.eq.Free()
    route = p.Route.__new__(p.Route)
    registry = json.loads((ROOT/'tests/fixtures/pz-supplied-trials.json').read_text())
    route.out, route.config, route.workers = tmp_path, dict(amine=registry['amine'],species=registry['species'],split_record=None), 1
    route.load = lambda reference: copy.deepcopy(registry)
    route.verify, route.bind = lambda: None, lambda point: SimpleNamespace(model=model)
    route.stability_row = lambda spec,state,scale:p.reg.stability(parameters,parent,scale=scale)
    route.temperature = lambda spec,state:problem.T
    states = [dict(key='pz')]
    measured, = p.stable.grid(None, states, registry['trials'], route=route)
    assert len(measured['supplied_trials'])==102
    short, = route.grid(None, states)
    retained = route.result('split-record.json')
    assert len(retained['trials'])==100 and all(w['resolved_descent'] for w in retained['trials'])
    assert retained['supplied_trials']==[dict(w, density_side=None, branch='unresolved') for w in registry['trials'][-2:]]
    trial = measured['supplied_trials'][100+source_index]
    assert measured['supplied_available'] and trial['evidence']=='evaluated'
    assert trial['quantities']['tpd_over_rt']==pytest.approx(record['endpoint_direct_tpd'],rel=0.,abs=trial['quantities']['descent_error_estimate_over_rt'])
    assert not trial['resolved_descent'] and measured['witnesses']==[]
    assert p.stable.descent(measured)
    assert p.stable.tally([measured])['descent']==1
    assert not measured['optimized_available'] and not measured['available']
    assert short['supplied_trial_counts']==measured['supplied_trial_counts']
    assert short['descent']==p.stable.descent(measured)
    assert 'supplied_trials' not in short
    index, lowest = min(enumerate(measured['supplied_trials']), key=lambda pair: pair[1]['quantities']['tpd_over_rt'])
    phase = (retained['trials']+retained['supplied_trials'])[index]
    assert dict(lowest, phase=phase) in short['supplied_trial_evidence']


def test_run_storage_limit_preserves_replaced_file(tmp_path):
    route = p.Route.__new__(p.Route)
    route.out = tmp_path
    route.write('search-0.json', [])
    search = tmp_path/'search-0.json'
    before = search.read_bytes()
    with (tmp_path/'prior-run.json').open('wb') as prior:
        prior.truncate(99_338_608-len(before))
    with pytest.raises(RuntimeError, match=r'search-0\.json:.*99338608'):
        route.write('search-0.json', [1])
    assert search.read_bytes()==before


def test_search_refuses_tracked_results_folder():
    route = p.Route.__new__(p.Route)
    route.out = ROOT/'analyses/pz_transfer/results/retransfer-345'
    with pytest.raises(RuntimeError, match='ignored by Git'):
        route.grid(None, [])


def test_timing_comparison_accepts_reused_calculations(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'analyses/stability_search'))
    from search_profile import compare

    base, changed = tmp_path/'base', tmp_path/'changed'
    row = dict(key='hartono-2013-y:0:problem', seconds=1., value=0.)
    copied = dict(row, same_calculation_as='hartono-2013-y:1:problem')
    for folder, measured in ((base, row), (changed, copied)):
        folder.mkdir()
        (folder/'search-0.json').write_text(json.dumps([measured]))
        (folder/'split-record.json').write_text('{"trials": []}')
    matching = compare(base, changed)
    assert matching['identical'] and matching['copies']==1
    (changed/'search-0.json').write_text(json.dumps([dict(copied, value=-.01)]))
    assert compare(base, changed)['row_mismatch']==[row['key']]


def test_interpolated_retreat_keeps_optimizer_evidence_separate(tmp_path):
    """#385: evaluate a new trial locally before accepting a midpoint."""
    route = p.Route.__new__(p.Route)
    route.out = tmp_path
    route.segment = lambda anchor, endpoint, t: t
    registry, calls = [], []
    route.result = lambda name: dict(trials=registry)
    route.replay = lambda point, rows: ([], True, 10.+point)
    def grid(point, states, *, trial_set=None):
        native_descent = point > .875
        witness = dict(kind='Liquid', support=[0], composition=[point], packing=.4,
                       resolved_descent=native_descent)
        if trial_set is None:
            if native_descent:
                registry.append(witness)
        else:
            assert all(w in registry or w['composition']==[point] for w in trial_set)
            calls.append((point, len(trial_set)))
        row = dict(key='reference', available=True, value=-1. if native_descent else 0.,
                   witnesses=[witness] if native_descent else [])
        if point == .875:
            # Discovery alone leaves the first sweep admissible.
            if witness in trial_set:
                row['supplied_trials'] = [dict(evidence='evaluated', quantities=dict(tpd_over_rt=-1.))]
            else:
                row['witnesses'] = [witness]
        return [row]
    route.grid = grid
    p.stable.retreat('reference', 0., 1., [dict(key='reference')], shifts=({}, {}), route=route,
                     optimizer_report=dict(status='converged', data_cost=11., final_cost=11.))
    report = json.loads((tmp_path/'reference/retreat.json').read_text())
    resolution = .01/2**10  # #385 retains the old .01 interval / ten refinements.
    assert report['t'] < report['upper_t'] == .875
    assert report['upper_t']-report['t'] <= resolution
    assert not report['non_monotone'] and report['base_trials']==1
    assert json.loads((tmp_path/'reference/candidate.json').read_text())==report['t']
    assert len(registry)==1 and registry[0]['composition']==[1.]
    assert [n for point, n in calls if point == .875] == [1, 2]
    assert report['optimizer_converged'] and not report['point_terminated_on_optimizer_tolerance']
    assert report['optimizer_cost']==11. and report['retreat_cost']==10.+report['t']
    assert report['method']=='bisection'
    route.result = lambda name: dict(t=.875)  # A retained old-walk result has no method.
    with pytest.raises(AssertionError,match='new output directory'):
        p.stable.retreat('reference',0.,1.,[],shifts=({},{}),route=route)


def test_missing_range_reduction(tmp_path,monkeypatch):
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json',tmp_path)
    route.out,route.config['reaction_ranges_K'] = tmp_path,{}
    records = [dict(identity=str(i),problem=str(i),role='fitted') for i in range(2)]
    spec = SimpleNamespace(inputs={'observations':{'fitted':records,'comparisons':[]}},problems={str(i):SimpleNamespace(T=313.15,reactions=[SimpleNamespace(name='unknown-law')] if i==0 else []) for i in range(2)},prediction=lambda r:dict(identity=r['identity'],group='pressure',observed=0.,value=1.,status='Available',unit='Pa'))
    monkeypatch.setattr(route,'bind',lambda point:spec)
    route.reduce(None)
    summaries = route.result('deviations.json')
    assert {s['outside_range']:s['rows'] for s in summaries}=={False:0,True:0,'source range unknown':1,'reaction not used':1}
    assert sum(s['statistics']['relative_undefined'] for s in summaries if s['statistics'])==2


def test_retained_fit_endpoint_transport(monkeypatch,tmp_path):
    import hashlib
    import json
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json',tmp_path)
    path = ROOT/'analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/start.json'
    point = route.start(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()),adopt=False)
    report = json.loads(path.with_name('fit.json').read_text())
    report['reactions'] = point['reactions']
    actual = route.endpoint_mapping(point,report,point['coordinates'])
    expected = route.load(route.config['reference'])
    assert p.stable.s.parameter_values(actual['parameters'])==p.stable.s.parameter_values(expected)


@pytest.mark.parametrize('status,unavailable',[('converged',False),('limit_reached',False),('converged','only'),('converged','split')])
def test_reportable_splitting_endpoint(status,unavailable,tmp_path,monkeypatch):
    import reduced_refit_338 as reduced
    route = p.Route.__new__(p.Route)
    route.out,route.config,route.controls = tmp_path,dict(starts=[1.,2.],loadings=[1e-5]),dict(function_tolerance=1e-8)
    route.start,route.replay = lambda ref:ref,lambda point: ([],True,point)
    route.search = lambda point: dict(stable=point>10.,grid=dict(descent=int(point<=10.)),offset=dict(descent=0),census=dict(descent=0))
    if unavailable:
        native = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json',tmp_path)
        p.stable._init(native.start(native.config['reference']),route=native)
        row = p.stable._measure(dict(key='comparison:362:cap',cap_record='comparison:362'))
        monkeypatch.setattr(route,'grid',lambda *args:[row]+([dict(key='split',available=True,value=-1.,native_liquid_descent=True)] if unavailable=='split' else [])); route.bind,route.states = lambda point:None,lambda spec:[]
        route.search = lambda point:p.Route.search(route,point)
        assert 'thermochemistry_unavailable: outside_interval: record excludes temperature' in route.search(None)['grid']['unavailable_searches'][0]['message']
    def fitted(name,start,*args,**kwargs):
        if unavailable and '/penalized-' in name: raise ValueError(row['message'])
        return (endpoint := start+(10. if '/penalized-' in name else 0.)),dict(status=status,final_cost=endpoint,endpoint_replay_cost=endpoint,stability_cost=1.,declared=[],cost_history=[3.,endpoint])
    monkeypatch.setattr(reduced,'fit',fitted)
    retreat = dict(disposition='no candidate',t=0.,upper_t=1.,non_monotone=True,
                   trace=[dict(t=0.,admissible=False),dict(t=1.,admissible=True)])
    route.write('start-0/retreat.json',retreat)
    chosen = route.campaign()
    if unavailable=='split': assert route.result('start-0/penalized-0/unavailable.json')['cause']==row['message']
    assert (chosen['cost']==1. and not chosen['stable']) if status=='converged' else chosen is None
    if chosen: assert chosen['retreat']==route.result('selection.json')['chosen']['retreat']==route.result('start-0/finding.json')['retreat']==retreat
    endpoints = route.result('start-0/endpoints.json')
    assert len(endpoints)==(3 if status=='converged' and not unavailable else 1)
    assert endpoints[0]['optimizer_report']['cost_history']==[3.,1.] and all(e['split_counts']=='lower bounds' for e in endpoints)
    assert endpoints[0]['disposition']==('no split found in the available searches; 1 searches unavailable' if unavailable=='only' else 'converged but still splitting' if status=='converged' else 'not converged')


# #359 continuation failure: exercise fit() rather than replacing its loop.
def test_failed_continuation_retains_nonconverged_endpoint(tmp_path,monkeypatch):
    import reduced_refit_338 as reduced
    route = p.Route.__new__(p.Route)
    route.out,route.config,route.controls = tmp_path,dict(starts=[1.,2.],loadings=[1e-5]),dict(function_tolerance=1e-8)
    route.start,route.bind,route.states = lambda ref:ref,lambda point:None,lambda spec:[]
    route.replay,route.grid = lambda point:([],True,point),lambda *args:[]
    attempts = []
    def stage(name,attempt,scale,mapping,*args,**kwargs):
        attempts.append((name,attempt,mapping))
        if attempt==1:
            return dict(status='failed',endpoint_replay_available=False,message='continuation thermochemistry unavailable')
        route.write(f'{name}/stage-{attempt}/parameters.json',mapping)
        return dict(status='limit_reached',endpoint_replay_available=True,endpoint_replay_cost=mapping,data_cost=mapping,final_cost=mapping,declared=[],cost_history=[3.,mapping])
    monkeypatch.setattr(reduced.r,'stage_fit',stage)
    assert route.campaign() is None
    selection = route.result('selection.json')
    assert len(selection['candidates'])==2 and selection['chosen'] is None
    assert [attempt for name,attempt,mapping in attempts]==[0,1,0,1]
    for i,cost in enumerate((1.,2.)):
        endpoint = route.result(f'start-{i}/endpoints.json')[0]
        assert endpoint['parameters']==cost and endpoint['cost']==cost
        assert endpoint['disposition']=='not converged' and not endpoint['optimizer_converged']
        assert endpoint['optimizer_report']['cost_history']==[3.,cost]
        failure = route.result(f'start-{i}/unpenalized/stage-1/unavailable.json')
        assert failure['message']=='continuation thermochemistry unavailable' and not failure['endpoint_replay_available']


def test_interrupted_mdea_continuation_is_counted(monkeypatch):
    from unittest.mock import Mock
    import reduced_refit_338 as reduced
    root = ROOT/'analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty'
    name = 'start-1/binary-1'
    read = lambda path: json.loads((root/path).read_text())
    route = SimpleNamespace(out=root, bind=lambda point: None, states=lambda spec: [], replay=lambda point: ([],True,0.),
                            write=lambda *args: None, result=read)
    stage = Mock(side_effect=[read(f'{name}/stage-{i}/fit.json') for i in (0,2)])
    monkeypatch.setattr(reduced.r,'stage_fit',stage)
    point, report = reduced.fit(name,None,{},None,scale=.003,route=route,penalty_rows=[])
    assert [call.args[1] for call in stage.call_args_list]==[0,2]
    assert report['status']=='converged' and point==read(f'{name}/stage-2/parameters.json')


def test_horstmann_residual_excess_enthalpy():
    """#360 same-wheel F0 reference; owner-set relative tolerance 1e-8."""
    from MEA.solvent_specification import SolventSpecification
    spec = SolventSpecification(ROOT/'analyses/dea_transfer/runs/B-2-endpoint.toml')
    spec.problems['binary'] = SimpleNamespace(T=363.15, P=1.75e6, reactions=[])
    record = dict(identity='Horstmann:1', group='Horstmann', row={'source_row': '1'},
                  observation_parameters=spec.parameter_sha256, constructor='residual_excess_enthalpy',
                  problem='binary', temperature_domain=[363.15,363.15], unit='J/mol mixture',
                  arguments=dict(observed=-232., x={'water':.0636, 'diethanolamine':.9364}))
    result = spec.prediction(record)
    assert result['value'] == pytest.approx(88.58956892024435, rel=1e-8)
    assert result['role'] == 'comparison only'
    with pytest.raises(ValueError, match='Unsupported observation constructor'):
        spec.observation(record)
    route = p.Route.__new__(p.Route)
    route.config = dict(stocks=[], loadings=[])
    spec.inputs['observations']['comparisons'] = [record]
    enforced = route.states(spec)
    spec.inputs['observations']['comparisons'] = []
    assert route.states(spec) == enforced


def test_amp_supplied_trial_component_support(monkeypatch, tmp_path):
    """#363: the reactive split from #344 e627a6f cannot enter binary Hartono."""
    spec = p.SolventSpecification(ROOT/'analyses/amp_transfer/refit-306-1.toml')
    trial = dict(kind='Liquid', support=list(range(9)), packing=.42127619395874333,
                 composition=[.0006382983819095918,.0775682901129986,.7438684616339758,
                              .0889625710887081,.0009575541611874242,.0880046145898001,
                              1.9816127717360009e-7,2.9274884923942357e-9,8.94265471074361e-9])
    route = p.Route.__new__(p.Route)
    route.out, route.config = tmp_path, {}
    route.verify, route.bind = lambda: None, lambda point: spec
    keys = ['hartono-2013-P:0:problem','hartono-2021:0:problem']
    monkeypatch.setattr(p.stable, '_SPEC', None)
    monkeypatch.setattr(p.stable, '_TRIALS', {}, raising=False)
    monkeypatch.setattr(p.stable, '_ROUTE', None, raising=False)
    p.stable._init(None, {key:[trial] for key in keys}, route)
    binary, loaded = [p.stable._measure(dict(key=key,problem=key)) for key in keys]
    assert binary['available'] and binary['optimized_available']
    assert binary['not_applicable_supplied_trials']==[dict(trial,evidence='not applicable',support_difference=[0,3,4,5,6,7,8])]
    assert not binary.get('supplied_trials') and not p.stable.descent(binary)
    assert binary['supplied_trial_counts']==dict(available=0,unavailable=0,not_applicable=1)
    assert loaded['supplied_available'] and loaded['supplied_trials'][0]['evidence']=='evaluated'
    assert loaded['not_applicable_supplied_trials']==[]
    assert loaded['supplied_trial_counts']==dict(available=1,unavailable=0,not_applicable=0)
    assert p.stable.tally([binary,loaded])['supplied_trial_counts']==dict(available=1,unavailable=0,not_applicable=1)
    def failed_search(*args):
        raise ValueError('optimized search failed')
    monkeypatch.setattr(p.reg, 'predict', failed_search)
    failed = p.stable._measure(dict(key=keys[0],problem=keys[0]))
    assert not failed['available'] and failed['message']=='ValueError: optimized search failed'
    assert failed['not_applicable_supplied_trials']==binary['not_applicable_supplied_trials']
    assert p.stable.tally([failed])['supplied_trial_counts']==binary['supplied_trial_counts']


def test_completed_reaction_chart_preserves_bounds_through_continuation(monkeypatch,tmp_path):
    """#365: fit displacement keeps bounds; law completion translates the chart."""
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json',tmp_path)
    point = route.start(route.config['reference'],adopt=False)
    point['coordinates'] = [
        dict(kind='reaction_coordinate',name='R',coefficient='a',origin=5.,scale=2.,bounds=[2.,8.]),
        dict(kind='reaction_enthalpy_shift',name='R',origin=0.,scale=1000.,bounds=[-10000.,10000.])]
    point['reactions'] = dict(aqueous=[dict(name='R',correlation=dict(a=5.))])
    original = p.copy.deepcopy(point)
    # A fitted a displacement of +1 and an independent completion offset of +.25.
    report = dict(optimizer=[.5,.25],physical=[],reactions=dict(aqueous=[dict(name='R',correlation=dict(a=6.25))]))
    endpoint = route.endpoint_mapping(point,report,point['coordinates'])
    assert point==original
    assert endpoint['coordinates'][0]['origin']==6.25
    assert endpoint['coordinates'][0]['bounds']==[2.25,8.25]
    assert endpoint['coordinates'][1]['bounds']==[-10250.,9750.]
    # Reusing an already completed law adds no further translation.
    zero = dict(optimizer=[0.,0.],physical=[],reactions=endpoint['reactions'])
    assert route.endpoint_mapping(endpoint,zero,endpoint['coordinates'])==endpoint
    # A continuation moves a by -.5 and completes with a further -.125 offset.
    report.update(optimizer=[-.25,-.125],reactions=dict(aqueous=[dict(name='R',correlation=dict(a=5.625))]))
    continued = route.endpoint_mapping(endpoint,report,endpoint['coordinates'])
    assert continued['coordinates'][0]['origin']==5.625
    assert continued['coordinates'][0]['bounds']==[2.125,8.125]
    assert continued['coordinates'][1]['bounds']==[-10125.,9875.]
    assert continued['coordinates'][1]['origin']==0.


def test_uncertainty_identity_failure_writes_no_standard_error(monkeypatch,tmp_path):
    """A failed rerun must invalidate uncertainty from a transported endpoint."""
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json',tmp_path)
    route.out = tmp_path
    point = route.start(route.config['reference'],adopt=False)
    reactions = p.copy.deepcopy(point['reactions'])
    law = next(r['correlation'] for group in reactions.values() for r in group if r['name']=='MDEA-dissociation')
    point['coordinates'] = [dict(kind='reaction_coordinate',name='MDEA-dissociation',
        coefficient='a',identity='dissociation-a',origin=law['a'],scale=1.,bounds=[law['a']-3.,law['a']+3.])]
    law['a'] += .5
    report = dict(optimizer=[.5],physical=[],reactions=reactions)
    endpoint = route.endpoint_mapping(point,report,point['coordinates'])
    route.uncertainty(endpoint)
    result = route.result('conditional-uncertainty.json')
    assert np.isfinite(result['conditional_standard_error']['dissociation-a'])
    inconsistent = p.copy.deepcopy(endpoint)
    inconsistent['coordinates'][0]['origin'] += .1
    with pytest.raises(AssertionError,match='Differentiation/replay row mismatch'):
        route.uncertainty(inconsistent)
    assert not (tmp_path/'conditional-uncertainty.json').exists()


def test_grid_builds_supplied_trials_only_in_state_worker(monkeypatch, tmp_path):
    """#368/#391: retain one inventory; each worker task holds one temperature's states, returned in input order."""
    import concurrent.futures
    class Trial(dict):
        def __deepcopy__(self, memo):
            pytest.fail('grid copied a supplied trial before state evaluation')
    trial = Trial(kind='Liquid', support=[0], composition=[1.], packing=.4)
    route = p.Route.__new__(p.Route)
    route.out, route.config, route.workers = tmp_path, dict(amine='test', species=['test'], split_record=None), 3
    route.load = lambda reference:dict(amine='test', species=['test'], trials=[trial])
    route.bind = lambda point: None
    class Pool:
        def __init__(self, workers, *, initializer, initargs):
            assert workers==3 and initargs[1]==[trial]
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def map(self, function, groups):
            assert len(groups)==9 and all(len({state['T'] for state in group})==1 for group in groups)
            return map(function, groups)
    monkeypatch.setattr(concurrent.futures, 'ProcessPoolExecutor', Pool)
    monkeypatch.setattr(p.stable, '_measure', lambda state:dict(key=state['key']))
    measured = route.grid(None, [dict(key=str(i), T=300.+i%9) for i in range(67536)])
    assert [row['key'] for row in measured]==[str(i) for i in range(67536)]


def test_density_branch_overrides_seed_label():
    """#373: a liquid seed may converge to vapor; only native liquid triggers."""
    vapor = dict(kind='Liquid', density_side=1., resolved_descent=True)
    liquid = dict(kind='Vapor', density_side=2., resolved_descent=True)
    row = dict(parent_kind='Liquid', witnesses=[vapor], supplied_trials=[
        dict(evidence='evaluated', quantities=dict(density_side=2., tpd_over_rt=-.03))])
    assert p.branch_counts(row)==dict(native_branch='vapor', supplied_branch='liquid', native_liquid_descent=False, liquid_liquid_split=False)
    row['witnesses'] = [liquid]
    assert p.branch_counts(row)['native_liquid_descent'] and p.branch_counts(row)['liquid_liquid_split']
    assert p.density_branch([vapor, liquid])=='mixed'
    assert p.density_branch([dict(kind='Liquid')])=='unresolved'
    route = p.Route.__new__(p.Route)
    route.config = {}
    spec = SimpleNamespace(problems={'NMR':dict(T=333.15,feed=[1.,2.],reactions=['R1']),
                                    'sibling':dict(T=333.15,feed=[1.,2.],reactions=['R1']),
                                    'different':dict(T=333.15,feed=[1.,2.],reactions=['R2'])})
    def stability_row(spec, state, scale):
        if state['key'].startswith('compressed:comparison:362:cap:'):
            raise ValueError('ThermochemistryUnavailable, initial:thermochemistry_unavailable: outside_interval: record excludes temperature')
        return SimpleNamespace(problem=spec.problems[state['problem']],pressure_reference=None)
    route.stability_row = stability_row
    states = [dict(key=name,problem=name) for name in spec.problems]
    states.append(dict(key='comparison:362:cap',cap_record='comparison:362'))
    copies = route.penalty_states(states,spec)
    assert route.penalty_unavailable==[dict(source='comparison:362:cap',pressure_ratio=ratio,message='ThermochemistryUnavailable, initial:thermochemistry_unavailable: outside_interval: record excludes temperature') for ratio in (1.05,3.)]
    assert len(copies)==4 and all(s['compressed'] for s in copies)
    assert {s['c'] for s in copies}=={1.05,3.}
    assert [s['sources'] for s in copies]==[['NMR','sibling'],['NMR','sibling'],['different'],['different']]
    route.config['binary_penalty'] = dict(pressure_Pa=1466000., temperatures_K=[413.15], x_MDEA=[.07])
    assert route.penalty_states(states,spec) == copies + [
        dict(key='binary:413.15:0.07', T=413.15, P=1466000., binary_x=.07)
    ]
    item = SimpleNamespace(problem=SimpleNamespace(pressure=SimpleNamespace(value=1e5)),pressure_reference=object(),pressure_ratio=3.)
    prediction = SimpleNamespace(pressure_reference=SimpleNamespace(value=2101051.3059414467))
    basis = route.pressure_basis(spec,{},item,prediction)
    assert basis['search_pressure_Pa']==6303153.91782434 and basis['pressure_ratio']==3.
    assert basis['declared_pressure_Pa'] is None
    item.pressure_reference = prediction.pressure_reference = None
    basis = route.pressure_basis(spec,{},item,prediction)
    assert basis['declared_pressure_Pa']==basis['search_pressure_Pa']==1e5
    assert basis['pressure_ratio'] is None
