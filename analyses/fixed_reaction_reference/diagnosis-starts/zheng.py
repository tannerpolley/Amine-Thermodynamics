"""Bubble pressure along CO2 loading for Zheng row 6 at the selected MDEA endpoint (issue #429).

Source state: 50 wt % MDEA, 323.15 K, loading 1.177 mol/mol, total pressure 4.19 MPa (Zheng 2020, Table 4, row 6).
"""
from copy import copy
from time import monotonic

import retained_starts as c

eq = c.refit.eq
endpoint = c.r.read(c.OUT/'MDEA/A.json.gz')['endpoint']
assert c.refit.fingerprint(endpoint) == c.r.read(c.OUT/'MDEA/selection.json')['endpoint_fingerprint']
spec = c.RUN.bind(endpoint)
row = next(q for q in spec.inputs['observations']['comparisons'] if q['group'] == 'Zheng' and q['row']['source_row'] == '6')
merkley = next(q for q in c.ROWS if q['group'] == 'Merkley')
template = spec.problems[merkley['bubble']]
final = spec.problems[row['final']]
target = dict(final.feed.values)['carbon-dioxide']


def at(loading):
    p = copy(template)
    p.T = final.T
    p.feed = copy(final.feed)
    p.feed.values = dict(final.feed.values) | {'carbon-dioxide': loading}
    return p


tick = monotonic()
cold = eq.solve_equilibrium(spec.model, at(target))
solution, last, loading, step, trace = None, None, .05, .05, []
while True:
    s = eq.solve_equilibrium(spec.model, at(loading), solution)
    if s.success and s.requested_tolerance_met:
        solution, last = s, loading
        trace.append((loading, s.pressure, list(s.molar_densities)))
        if loading >= target:
            break
        loading = min(target, loading+step)
    else:
        step /= 2
        if step < 1e-3:
            break
        loading = min(target, last+step)
record = dict(wheel=c.r.SHA, endpoint_fingerprint=c.refit.fingerprint(endpoint), T=final.T, feed=dict(final.feed.values),
              source_pressure_Pa=float(row['row']['pressure_MPa'])*1e6, target_loading=target,
              cold=dict(success=bool(cold.success), message=cold.message, pressure=cold.pressure if cold.success else None),
              reached_loading=last, stall_message=None if last >= target else s.message, trace=trace, seconds=monotonic()-tick)
c.refit.save(c.HERE/'results/zheng-row-6.json', record)
print('feed', record['feed'], 'T', final.T)
print('cold', record['cold'])
for a, p, rho in trace[-12:]:
    print(f'{a:.4f} {p/1e6:.3f} MPa densities {[round(x) for x in rho]}')
print('reached', last, 'of', target, record['stall_message'], round(record['seconds'], 1), 's')
