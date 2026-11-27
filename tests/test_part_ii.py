"""Numerical references for the transported reaction chart and property reductions."""
from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest
from MEA.solvent_specification import conditional_information

from analyses.amines.model import Route
from analyses.amines.phase import states
from analyses.amines.properties import property_rows
from analyses.amines.wheel import ROOT


def test_conditional_linear_information():
    J = np.array([[1.,0.],[0.,1.],[1.,0.],[0.,1.]])
    result = conditional_information(SimpleNamespace(physical=[0.,1.],covariance=SimpleNamespace(active_bounds=[1])),J,np.ones(4),['a','b'],[-1.,-1.],[1.,1.])
    assert result['free_coordinates']==['a']
    assert result['conditional_standard_error']['a']==pytest.approx(np.sqrt(2/3))


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


def test_missing_range_reduction(tmp_path,monkeypatch):
    route = Route.__new__(Route)
    route.config = {"reaction_ranges_K": {}}
    records = [dict(identity=str(i),problem=str(i),role='fitted') for i in range(2)]
    spec = SimpleNamespace(inputs={'observations':{'fitted':records,'comparisons':[]}},problems={str(i):SimpleNamespace(T=313.15,reactions=[SimpleNamespace(name='unknown-law')] if i==0 else []) for i in range(2)},prediction=lambda r:dict(identity=r['identity'],group='pressure',observed=0.,value=1.,status='Available',unit='Pa'))
    monkeypatch.setattr(route,'bind',lambda point:spec)
    summaries = property_rows(route, None)['deviations']
    assert {s['outside_range']:s['rows'] for s in summaries}=={False:0,True:0,'source range unknown':1,'reaction not used':1}
    assert sum(s['statistics']['relative_undefined'] for s in summaries if s['statistics'])==2


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
    route = Route.__new__(Route)
    route.config = dict(stocks=[], loadings=[])
    spec.inputs['observations']['comparisons'] = [record]
    enforced = states(route, spec)
    spec.inputs['observations']['comparisons'] = []
    assert states(route, spec) == enforced


def test_completed_reaction_chart_preserves_bounds_through_continuation(monkeypatch,tmp_path):
    """#365: fit displacement keeps bounds; law completion translates the chart."""
    route = Route.__new__(Route)
    point = {"parameters": {}}
    point['coordinates'] = [
        dict(kind='reaction_coordinate',name='R',coefficient='a',origin=5.,scale=2.,bounds=[2.,8.]),
        dict(kind='reaction_enthalpy_shift',name='R',origin=0.,scale=1000.,bounds=[-10000.,10000.])]
    point['reactions'] = dict(aqueous=[dict(name='R',correlation=dict(a=5.))])
    original = deepcopy(point)
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
