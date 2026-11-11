"""Fixed B1 adoption replay against #298; no parameter fitting (#302)."""
import hashlib
import json
import math
from pathlib import Path
import sys

AN = Path(__file__).resolve().parent
ROOT = AN.parents[1]
sys.path.insert(0, str(ROOT / 'analyses/mdea_mea_workflow/scripts'))
sys.path.insert(0, str(ROOT / 'analyses/permittivity_temperature_loading'))
import assess_298 as a
from dielectric_volume import verify_wheel
from MEA.solvent_specification import SolventSpecification
r, c = a.r, a.c
EVIDENCE = r.OUT
r.OUT = AN / 'results/adoption-302'
SPEC = None


def predict(row):
    return SPEC.prediction(row)


def main():
    global SPEC
    verify_wheel(r.WHEEL, r.SHA)
    SPEC = SolventSpecification(AN / 'B1.toml')
    doc = SPEC.inputs['endpoint']
    assert hashlib.sha256((ROOT / 'analyses/mea_parameter_bundle/results/adoption-297/shared-R2.json').read_bytes()).hexdigest() == '1b2b51e77924e7d01f43eebe80e02c7094644ef7a5a5e6ac211ac60dc5673471'
    law = next(x for x in SPEC.spec['chemistry']['reactions']['aqueous'] if x['name'] == 'R2')['correlation']
    assert law == r.read(EVIDENCE / 'B1-endpoint/R2.json')
    reaction = next(x for x in a.s.j.d.REACTIONS if x.name == 'R2')
    reaction.correlation = a.s.eq.ReactionLogPolynomial(**law)
    rows = r.pool(predict, SPEC.inputs['observations']['fitted'])
    ref = r.read(EVIDENCE / 'B1-endpoint/fitted-replay.json')
    assert len(rows) == len(ref) == 278
    assert all(x['status'] == 'Available' and x['requested_tolerance_met'] for x in rows)
    differences = [abs(x['value'] - y['value']) / max(abs(y['value']), 1e-300) for x,y in zip(rows,ref,strict=True)]
    cost = math.fsum(.5*q['weight']*x['residual']**2 for q,x in zip(SPEC.inputs['observations']['fitted'],rows,strict=True))
    expected = r.read(EVIDENCE / 'selection.json')['B1']['cost']
    result = dict(rows=len(rows), cost=cost, reference_cost=expected, relative_cost_difference=abs(cost/expected-1), max_relative_prediction_difference=max(differences), parameter_sha256=SPEC.parameter_sha256, wheel_sha256=r.SHA)
    r.write('replay.json', rows)
    r.write('verification.json', result)
    assert max(differences) <= 1e-8 and abs(cost/expected-1) <= 1e-8, result
    scores = a.pressure_scores(doc, 'B1')
    for source, expected in [('Xiao',28.191041), ('Ermatchkov',18.270562)]:
        assert abs(scores[source]['AARD_percent']-expected) <= 1e-6
    comparisons = r.pool(predict, SPEC.inputs['observations']['comparisons'])
    r.write('comparisons.json', comparisons)
    print(json.dumps(dict(**result, pressures=scores)), flush=True)


if __name__ == '__main__':
    main()
