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
