"""Scheduled phase evidence keeps missing work and descents in its denominators."""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'analyses/mea_parameter_bundle/scripts'))
import phase_extension_201 as study


def test_missing_phase_evidence_and_failed_confirmation_preserve_descent(tmp_path, monkeypatch):
    monkeypatch.setattr(study, 'OUT', tmp_path)
    monkeypatch.setattr(study, 'R', tmp_path.parent)
    for name in ('A6', 'A7', 'inputs'):
        (tmp_path/name).mkdir()
    (tmp_path/'inputs/family-points.txt').write_text('declared states')
    states = [dict(index=i, temperature_K=353.15, loading=.5, pressure_Pa=1e5,
                   admitted=True, cause='') for i in range(81)]
    source = study.J/'amendment-7/fixed-study/wheel-8298c602/after-adoption/a6-selected/point-70.json'
    point = copy.deepcopy(json.loads(source.read_text()))
    point['index'] = 0
    original = point['stability'][0]['trials']
    assert len(original)==9 and any(t['resolved_descent'] for t in original)
    missing = next(i for i,t in enumerate(original) if not t['resolved_descent'])
    point['stability'][0]['trials'].pop(missing)
    study.write(tmp_path/'A6/point-0.json',point)
    # An unsuccessful confirmation cannot overwrite the screening evidence.
    study.write(tmp_path/'A6/split-seeded-0-trial-0.json',dict(confirmed=False))
    rows, slots, confirmations = study.reduce(states,None)
    assert len(rows)==162 and len(slots)==1458
    a6 = [r for r in rows if r['record']=='A6']
    assert a6[0]['classification']=='failed' and a6[0]['resolved_trials']>0
    assert a6[0]['missing_trials']==1 and a6[1]['missing_trials']==9
    assert all(t['resolved_descent'] is None for t in slots if t['index']==1)
    assert len({(t['record'],t['index'],t['phase_kind'],t['seed']) for t in slots})==1458
    assert confirmations and all(c['path'].endswith(f"trial-{c['representative']}.json") for c in confirmations)


def test_continued_reference_and_parent_recover_diagnosed_cases():
    run = study.R/'phase-extension-201/run-2'
    reference = json.loads((run/'reference-pressure/reference-393.15-0.json').read_text())
    assert reference['admitted'] and reference['start'].endswith('reference-353.15-0.json')
    assert abs(reference['result']['pressure']-173333.00198051374)<1e-5
    assert max(map(abs, reference['result']['raw_residuals']))<1e-10
    excluded = json.loads((run/'reference-pressure/reference-393.15-6.json').read_text())
    assert excluded['result']['success'] and excluded['result']['pressure']>1e7
    assert not excluded['admitted']
    parent = json.loads((run/'A7/point-28.json').read_text())
    assert parent['bubble_start']['index']==27
    assert abs(parent['bubble_pressure_Pa']-41767.47872334231)<1e-5
    assert parent['classification']=='passed-single-liquid'
    trials = parent['stability'][0]['trials']
    assert len(trials)==9 and all(t['optimizer']['success'] for t in trials)
    assert not any(t['resolved_descent'] for t in trials)


def test_bubble_recovery_projects_model_order_onto_declared_support(tmp_path, monkeypatch):
    from types import SimpleNamespace
    f = study.f
    model = SimpleNamespace(component_ids=list(f.s.COMPONENT_IDS))
    liquid, vapor = [.2,.3,.5]+[0.]*6, [.1,.2,.7]+[0.]*6
    bubble = SimpleNamespace(amounts=[10.,0.],packing_fractions=[.4,.001],
                             phase_mole_fractions=lambda i: [liquid,vapor][i])
    problem = SimpleNamespace(phases=[f.eq.Phase('L',support=model.component_ids),
        f.eq.Phase('V',support=model.component_ids[:3][::-1])])
    def solve(model, problem, starts, limits):
        assert [s.compositions for s in starts] == [[liquid,[.7,.2,.1]]]*2
        assert [s.amounts for s in starts] == [[5.,5.],[9.,10.*(1.-.9)]]
        assert all(s.packing_fractions==bubble.packing_fractions for s in starts)
        assert (limits.attempts,limits.attempt_iterations,limits.iterations)==(2,400,800)
        return SimpleNamespace(causes=['unattempted']*2,selected=None,results=[None,None])
    monkeypatch.setattr(f.eq,'solve_equilibrium_starts',solve)
    assert f.bubble_recover(model,problem,bubble,dict(attempts=[]),tmp_path/'point.json') is None
