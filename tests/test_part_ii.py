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
    from MEA.solvent_specification import deviation_statistics, output_uncertainty
    result = deviation_statistics([(0.,2.),(4.,5.)],'Pa')
    assert result['relative_undefined']==1 and result['AARD_percent']==25.
    assert result['mean_abs_error']==1.5
    C = np.array([[4.,1.],[1.,9.]])
    residual = np.array([2.,3.])
    whitened = np.linalg.solve(np.linalg.cholesky(C),residual)
    assert whitened@whitened==pytest.approx(residual@np.linalg.solve(C,residual))
    assert output_uncertainty(C).covariance==C.ravel().tolist()


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
