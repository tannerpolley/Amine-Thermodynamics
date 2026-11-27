"""Issue 236 domain and failed-predecessor numerical invariants."""
from pathlib import Path
from MEA.solvent_specification import SolventSpecification

AN = Path(__file__).resolve().parents[1] / 'analyses/solvent_specification_mea'

def test_domain_and_continuation():
    spec = SolventSpecification(AN / 'MEA.toml')
    rows = spec.inputs['observations']['fitted']
    fixed = next(r for r in rows if r['group']=='CO2-free density')
    fixed = dict(fixed, temperature_domain=[300., 310.])
    refused = spec.prediction(fixed)
    assert refused['status']=='OutsideDeclaredDomain' and 'outside' in refused['message']
    first = next(r for r in rows if r['continuation'])
    group = first['continuation']['group']
    members = [r for r in rows if r['continuation'] and r['continuation']['group']==group]
    for row in members:
        spec.problems[row['problem']].T = 1000.
    spec.continue_groups()
    evidence = spec.continuation
    assert evidence[first['identity']]['status']=='ContinuationUnavailable'
    assert all(evidence[r['identity']]['status']=='DependentUnavailable' for r in members[1:])
    assert all(evidence[r['identity']]['cause']['target']==first['identity'] for r in members[1:])
    independent = [r for r in rows if r['continuation'] and r['continuation']['group']!=group]
    assert all(evidence[r['identity']]['status']=='Available' for r in independent)
    starts = [evidence[r['identity']] for r in independent if r['continuation']['order']==min(q['continuation']['order'] for q in independent if q['continuation']['group']==r['continuation']['group'])]
    assert all(r['predecessor'] is None for r in starts)
