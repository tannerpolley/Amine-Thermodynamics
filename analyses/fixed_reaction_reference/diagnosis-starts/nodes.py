"""Cold public solve of each saturation-search node that failed inside the search (issue #429).

The search warm-starts a node from its neighbour. A cold `solve_equilibrium` of the same declared node that converges
shows the node has a solution and the refusal came from the search's start.
"""
from collections import Counter
from copy import copy
from multiprocessing import Pool
from time import monotonic

import retained_starts as c

eq = c.refit.eq
SAT = [q for q in c.r.read(c.HERE/'results/saturation.json.gz')['records'] if q['draw'] is not None]
OUTLOOK = {q['draw']: q['cause'] for q in c.r.read(c.HERE/'results/outlook.json')['draws']}


def one(record):
    tick = monotonic()
    spec = c.at(c.vector(record['draw']))
    out = []
    for q in record['rows']:
        if q['first_failed_loading'] is None:
            continue
        problem = spec.problems[c.ROWS[q['row']]['bubble']]
        p = copy(problem)
        p.feed = copy(problem.feed)
        p.feed.values = dict(problem.feed.values) | {'carbon-dioxide': q['first_failed_loading']}
        s = eq.solve_equilibrium(spec.model, p)
        ok = bool(s.success and s.requested_tolerance_met)
        out.append(dict(row=q['row'], loading=q['first_failed_loading'], cap=q['cap'], target_Pa=q['P'], search_message=q['failed_message'],
                        cold_success=ok, cold_pressure_Pa=s.pressure if ok else None, cold_message=s.message))
    return dict(draw=record['draw'], cause=OUTLOOK[record['draw']], rows=out, seconds=monotonic()-tick)


if __name__ == '__main__':
    tick = monotonic()
    with Pool(8) as pool:
        records = pool.map(one, SAT, chunksize=1)
    c.refit.save(c.HERE/'results/nodes.json.gz', dict(wheel=c.r.SHA, records=records, wall_seconds=monotonic()-tick))
    tally = Counter((r['cause'], 'cold solve converges' if q['cold_success'] else 'cold solve fails') for r in records for q in r['rows'])
    for k, v in sorted(tally.items()):
        print(v, k)
    ok = [q for r in records if r['cause'] == 'Merkley saturation search only' for q in r['rows'] if q['cold_success']]
    print('below target among converged Merkley-only nodes:', sum(q['cold_pressure_Pa'] < q['target_Pa'] for q in ok), 'of', len(ok))
    print('wall', monotonic()-tick, 'cpu', sum(r['seconds'] for r in records))
