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
def test_pz_evaluated_negative_trial(source_index,monkeypatch):
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
    witness = dict(kind='Liquid',support=list(range(12)),composition=record['split_composition'],packing=None)
    monkeypatch.setattr(p.stable,'_ROUTE',SimpleNamespace(stability_row=lambda spec,state,scale:p.reg.stability(parameters,parent,scale=scale)),raising=False)
    monkeypatch.setattr(p.stable,'_SPEC',SimpleNamespace(model=model))
    monkeypatch.setattr(p.stable,'_TRIALS',{'pz':[witness]},raising=False)
    measured = p.stable._measure(dict(key='pz'))
    trial = measured['supplied_trials'][0]
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
