"""Loading continuation for reactive rows that are unavailable from the generic start (issue #429).

For each unavailable CO2-loaded row in a draw whose MDEA–water liquid is hull-stable, march the CO2 loading upward
from 0.05 with warm starts. Reaching the row's own loading shows a solution exists (initialization); a stall bounds it.
"""
from copy import copy
from multiprocessing import Pool
import sys
from time import monotonic

import starts as c

eq = c.refit.eq
CENSUS = {q['draw']: q for q in c.r.read(c.HERE/'results/census.json.gz')['records']}
GAP = {q['draw']: any(x['hull'] != 'stable' for x in q['rows']) for q in c.r.read(c.HERE/'results/gap.json.gz')['records']}
STATES = c.MANIFEST['rows']['fitted']
CO2 = 'carbon-dioxide'


def one(draw):
    tick = monotonic()
    spec = c.at(c.vector(draw))
    out = []
    for i, row in enumerate(CENSUS[draw]['rows']):
        record = STATES[i]
        if row['status'] == 'Available' or record['constructor'] != 'observation' or 'problem' not in record:
            continue
        problem = spec.problems[record['problem']]
        target = dict(problem.feed.values).get(CO2, 0.)
        if not target:
            continue

        def at(loading):
            p = copy(problem)
            p.feed = copy(problem.feed)
            p.feed.values = dict(problem.feed.values) | {CO2: loading}
            return p

        cold = eq.solve_equilibrium(spec.model, at(target))
        solution, last, loading, step, trace, solves = None, None, min(.05, target), .05, [], 0
        while True:
            s = eq.solve_equilibrium(spec.model, at(loading), solution)
            solves += 1
            if s.success and s.requested_tolerance_met:
                solution, last = s, loading
                trace.append((loading, s.pressure))
                if loading >= target:
                    break
                loading = min(target, loading+step)
            else:
                step /= 2
                if step < 1e-3 or last is None:
                    break
                loading = min(target, last+step)
        out.append(dict(row=i, group=record['group'], T=problem.T, loading=target, observed_Pa=record['arguments'].get('observed'),
                        cold_success=bool(cold.success and cold.requested_tolerance_met), cold_message=cold.message,
                        reached=last, reached_target=last is not None and last >= target, solves=solves,
                        pressure_Pa=None if solution is None else solution.pressure, stall_message=None if last is not None and last >= target else s.message,
                        trace=trace))
    return dict(draw=draw, hull_gap=GAP[draw], rows=out, seconds=monotonic()-tick)


if __name__ == '__main__':
    from collections import Counter
    tick = monotonic()
    draws = [d for d in CENSUS if d is not None and not GAP[d]] if len(sys.argv) == 1 else list(map(int, sys.argv[1:]))
    with Pool(8) as pool:
        records = pool.map(one, draws, chunksize=1)
    c.refit.save(c.HERE/'results/continuation.json.gz', dict(wheel=c.r.SHA, records=records, wall_seconds=monotonic()-tick))
    for r in sorted(records, key=lambda r: r['draw']):
        if r['rows']:
            print(r['draw'], Counter((q['group'], 'cold ok' if q['cold_success'] else 'cold fails', 'reached' if q['reached_target'] else 'stalled') for q in r['rows']), round(r['seconds'], 1))
    print('wall', monotonic()-tick, 'cpu', sum(r['seconds'] for r in records))
