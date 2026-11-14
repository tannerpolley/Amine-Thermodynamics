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


def test_shared_values_tie_and_range_marks(monkeypatch):
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json')
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
    measured = route.result(route.grid(None,[dict(key='pz')])[0]['details'])
    assert len(measured['supplied_trials'])==102
    measured = route.result(route.grid(None,[dict(key='pz')])[0]['details'])
    retained = route.result('split-record.json')
    assert len(retained['trials'])==100 and all(w['resolved_descent'] for w in retained['trials'])
    assert retained['supplied_trials']==registry['trials'][-2:]
    trial = measured['supplied_trials'][100+source_index]
    assert measured['supplied_available'] and trial['evidence']=='evaluated'
    assert trial['quantities']['tpd_over_rt']==pytest.approx(record['endpoint_direct_tpd'],rel=0.,abs=trial['quantities']['descent_error_estimate_over_rt'])
    assert not trial['resolved_descent'] and measured['witnesses']==[]
    assert p.stable.descent(measured)
    assert p.stable.tally([measured])['descent']==1
    assert not measured['optimized_available'] and not measured['available']


def test_interpolated_retreat_keeps_optimizer_evidence_separate(tmp_path,monkeypatch):
    """A prescribed admissible interval checks retreat decisions, not phase stability."""
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json')
    route.out = tmp_path
    monkeypatch.setattr(route,'segment',lambda anchor,endpoint,t:t)
    def prescribed(t,*args,**kwargs):
        return t<=.875,dict(suspects=[],descent=int(t>.875),available=1,minimum_tau=None,unavailable=[]),10.+t
    monkeypatch.setattr(p.stable,'admissible',prescribed)
    p.stable.retreat('decision',None,1.,[],shifts=({},{}),route=route,optimizer_report=dict(status='converged',data_cost=11.,final_cost=11.))
    result = route.result('decision/retreat.json')
    assert result['t']==.875 and result['disposition']=='interpolated'
    assert result['optimizer_converged'] and not result['point_terminated_on_optimizer_tolerance']
    assert result['optimizer_cost']==11. and result['retreat_cost']==10.875


def test_missing_range_reduction(tmp_path,monkeypatch):
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json')
    route.out,route.config['reaction_ranges_K'] = tmp_path,{}
    records = [dict(identity=str(i),problem=str(i),role='fitted') for i in range(2)]
    spec = SimpleNamespace(inputs={'observations':{'fitted':records,'comparisons':[]}},problems={str(i):SimpleNamespace(T=313.15,reactions=[SimpleNamespace(name='unknown-law')] if i==0 else []) for i in range(2)},prediction=lambda r:dict(identity=r['identity'],group='pressure',observed=0.,value=1.,status='Available',unit='Pa'))
    monkeypatch.setattr(route,'bind',lambda point:spec)
    route.reduce(None)
    summaries = route.result('deviations.json')
    assert {s['outside_range']:s['rows'] for s in summaries}=={False:0,True:0,'source range unknown':1,'reaction not used':1}
    assert sum(s['statistics']['relative_undefined'] for s in summaries if s['statistics'])==2


def test_retained_fit_endpoint_transport(monkeypatch):
    import hashlib
    import json
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json')
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
        native = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json')
        p.stable._init(native.start(native.config['reference']),route=native)
        row = p.stable._measure(dict(key='comparison:362:cap',cap_record='comparison:362'))
        monkeypatch.setattr(route,'grid',lambda *args:[row]+([dict(key='split',available=True,value=-1.)] if unavailable=='split' else [])); route.bind,route.states = lambda point:None,lambda spec:[]
        route.search = lambda point:p.Route.search(route,point)
        assert 'thermochemistry_unavailable: outside_interval: record excludes temperature' in route.search(None)['grid']['unavailable_searches'][0]['message']
    def fitted(name,start,*args,**kwargs):
        if unavailable and '/penalized-' in name: raise ValueError(row['message'])
        return (endpoint := start+(10. if '/penalized-' in name else 0.)),dict(status=status,final_cost=endpoint,endpoint_replay_cost=endpoint,stability_cost=1.,declared=[],cost_history=[3.,endpoint])
    monkeypatch.setattr(reduced,'fit',fitted)
    chosen = route.campaign()
    if unavailable=='split': assert route.result('start-0/penalized-0/unavailable.json')['cause']==row['message']
    assert (chosen['cost']==1. and not chosen['stable']) if status=='converged' else chosen is None
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


def test_completed_reaction_chart_preserves_bounds_through_continuation(monkeypatch):
    """#365: fit displacement keeps bounds; law completion translates the chart."""
    monkeypatch.setenv('AGENT_HEAVY_CORES','3')
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json')
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
    route = p.Route(ROOT/'analyses/mdea_mea_workflow/inputs/part-ii-replay.json')
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
    """#368: retain one inventory and submit at most four states per worker."""
    import concurrent.futures
    class Trial(dict):
        def __deepcopy__(self, memo):
            pytest.fail('grid copied a supplied trial before state evaluation')
    trial = Trial(kind='Liquid', support=[0], composition=[1.], packing=.4)
    route = p.Route.__new__(p.Route)
    route.out, route.config, route.workers = tmp_path, dict(amine='test', species=['test'], split_record=None), 3
    route.load = lambda reference:dict(amine='test', species=['test'], trials=[trial])
    class Pool:
        def __init__(self, workers, *, initializer, initargs):
            assert workers==3 and initargs[1]==[trial]
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def map(self, function, states, chunksize):
            assert len(states)<=12
            return map(function, states)
    monkeypatch.setattr(concurrent.futures, 'ProcessPoolExecutor', Pool)
    monkeypatch.setattr(p.stable, '_measure', lambda state:dict(key=state['key']))
    measured = route.grid(None, [dict(key=str(i)) for i in range(67536)])
    assert [row['key'] for row in measured]==[str(i) for i in range(67536)]
