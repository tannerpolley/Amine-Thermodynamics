"""Trace each unavailable Merkley saturation search in the census (issue #429).

Keeps every node's loading, pressure mismatch, slope and message; `outlook.py` owns the reading of the traces.
"""
from multiprocessing import Pool
from time import monotonic

import starts as c

MERKLEY = [i for i, q in enumerate(c.ROWS) if q['group'] == 'Merkley']


def one(draw):
    tick = monotonic()
    spec = c.at(c.ORIGIN if draw is None else c.vector(draw))
    out = []
    for i in MERKLEY:
        record = spec.inputs['observations']['fitted'][i]
        args = record['arguments']
        p = c.reg.predict(spec.model, spec.observation(record))
        nodes = [dict(loading=n.loading, mismatch=n.mismatch, slope=n.slope, solved=bool(n.state.success),
                      message=None if n.state.success else n.state.message) for n in p.saturation.nodes]
        solved = [n for n in nodes if n['solved'] and n['mismatch'] == n['mismatch']]
        bracket = next((b['loading'] for a, b in zip(solved, solved[1:]) if a['mismatch'] < 0 <= b['mismatch']), None)
        reversal = next((n['loading'] for n in solved if not n['slope'] > 0), None)
        failed = next((n['loading'] for n in nodes if not n['solved']), None)
        cap = args['loading_cap']
        out.append(dict(row=i, T=args['T'], P=args['P'], cap=cap, status=p.status.name, message=p.message,
                        causes=list(p.saturation.causes), nodes_solved=len(solved), first_failed_loading=failed,
                        failed_message=next((n['message'] for n in nodes if not n['solved']), None),
                        first_bracket_upper=bracket, first_nonpositive_slope=reversal,
                        pressure_at_last_solved=solved[-1]['mismatch']+args['P'] if solved else None,
                        last_solved_loading=solved[-1]['loading'] if solved else None, nodes=nodes))
    return dict(draw=draw, rows=out, seconds=monotonic()-tick)


if __name__ == '__main__':
    tick = monotonic()
    with Pool(8) as pool:
        records = pool.map(one, [None, *(i for i in range(64) if i != 17)])
    c.refit.save(c.HERE/'results/saturation.json.gz', dict(wheel=c.r.SHA, records=records, wall_seconds=monotonic()-tick))
    from collections import Counter
    print(Counter(q['status'] for r in records for q in r['rows']))
    print('wall', monotonic()-tick, 'cpu', sum(r['seconds'] for r in records))
