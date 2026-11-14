"""Declaration transport and conditional linear-information reference for #343."""
import importlib.util
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
    assert len(point['coordinates'])==8
    assert route.marks(413.15)=={'R1':False,'R2':False,'R3':False,'MDEA-dissociation':True}
    assert len(spec.inputs['observations']['fitted'])==278
    state = p.stable.states([{'water':10.,route.config['amine']:1.}],[1e-5,1.3])
    assert len(state)==36 and {r['c'] for r in state}=={1.05,3.}
    for row in (dict(key='data',problem=spec.inputs['observations']['fitted'][0]['problem']),state[0]):
        assert route.stability_row(spec,row,1e-2) is not None


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
