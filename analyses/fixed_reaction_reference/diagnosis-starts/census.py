"""Status of every fitted MDEA row, evaluated alone, at start A and at each drawn start (issue #429).

Tests whether one unavailable row refuses a draw (many rows evaluate) or the draw itself is unevaluable.
"""
from multiprocessing import Pool
from time import monotonic

import starts as c


def one(draw):
    tick = monotonic()
    values = c.ORIGIN if draw is None else c.vector(draw)
    return dict(draw=draw, vector=values.tolist(), rows=c.census(values), seconds=monotonic()-tick)


if __name__ == '__main__':
    tick = monotonic()
    draws = [None, *(i for i in range(64) if i != 17)]  # draw 17 was never evaluated by the campaign
    with Pool(8) as pool:
        records = []
        for q in pool.imap_unordered(one, draws):
            records.append(q)
            print(q['draw'], round(q['seconds'], 1), sum(x['status'] != 'Available' for x in q['rows']), flush=True)
    c.refit.save(c.HERE/'results/census.json.gz', dict(wheel=c.r.SHA, records=records, wall_seconds=monotonic()-tick))
