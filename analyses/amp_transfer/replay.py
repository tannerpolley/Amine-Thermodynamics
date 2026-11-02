"""#242: replay the retained A-1 and A-2 endpoints and completed laws over all calibration rows after the binary domain correction (owner 2026-11-02; no refit)."""
import json, math
from pathlib import Path
import epcsaft
from epcsaft import equilibrium as eq
from pinned_engine import SHA256
from MEA.solvent_specification import SolventSpecification, jsonable
AN, out = Path(__file__).resolve().parent, dict(wheel_sha256=SHA256)
native = json.loads((AN / 'results/reactive/summary.json').read_text())['runs']
for run in ('A-1', 'A-2'):  # observations built from the start document, predicted with the endpoint model and fitted laws, as in reactive.py
    spec, report = SolventSpecification(AN / f'{run}.toml', parameter='start'), json.loads((AN / f'results/reactive/{run}-fit.json').read_text())['report']
    laws = {r['name']: r['correlation'] for g in report['reactions'].values() for r in g}
    for reaction in [r for p in spec.problems.values() for r in p.reactions or []]:
        reaction.correlation = eq.ReactionLogPolynomial(**laws[reaction.name])
    spec.model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(json.loads((AN / f'inputs/{run}-endpoint.json').read_text())), thermochemistry=spec.thermal)
    replay = list(map(spec.prediction, rows := spec.inputs['observations']['fitted']))
    w = [math.sqrt(r['weight']) * p['residual'] if p.get('status') == 'Available' else math.nan for r, p in zip(rows, replay)]
    cost = math.fsum(0.5 * x * x for x in w)
    out[run] = dict(rows=len(rows), available=sum(p['status'] == 'Available' for p in replay), cost=cost, native_cost=native[run]['cost'], replay_cost_relative=abs(cost / native[run]['cost'] - 1),
                    max_weighted_residual_difference=max(abs(x - y) for x, y in zip(w, report['weighted_residuals'])),
                    groups={g: math.fsum(0.5 * x * x for x, r in zip(w, rows) if r['group'] == g) for g in dict.fromkeys(r['group'] for r in rows)}, replay=replay)
(AN / 'results/reactive/replay-binary-domain.json').write_text(json.dumps(jsonable(out), indent=1, default=float) + '\n')
