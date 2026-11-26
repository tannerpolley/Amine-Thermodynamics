"""One-coordinate scans from start A across each declared bound interval (issue #429).

Every other coordinate stays at A, so an unavailable row is attributable to the scanned coordinate alone.
"""
from collections import Counter
from multiprocessing import Pool
from time import monotonic

import retained_starts as c

FRACTIONS = [0., .125, .25, .375, .5, .625, .75, .875, 1.]


def one(task):
    j, fraction = task
    tick = monotonic()
    values = c.ORIGIN.copy()
    values[j] = c.LOWER[j] + fraction*(c.UPPER[j]-c.LOWER[j])
    rows = c.census(values)
    bad = [(i, q) for i, q in enumerate(rows) if q['status'] != 'Available' or not q['requested_tolerance_met']]
    return dict(coordinate=j, identity=c.POINT['coordinates'][j]['identity'], fraction=fraction, value=float(values[j]),
                failed=len(bad), families=dict(Counter(q['group'] for _, q in bad)),
                failures=[dict(row=i, group=q['group'], message=q['message']) for i, q in bad], seconds=monotonic()-tick)


if __name__ == '__main__':
    tick = monotonic()
    with Pool(8) as pool:
        records = pool.map(one, [(j, f) for j in range(len(c.NATIVE)) for f in FRACTIONS], chunksize=1)
    c.refit.save(c.HERE/'results/scan.json.gz', dict(wheel=c.r.SHA, origin=c.ORIGIN.tolist(), lower=c.LOWER.tolist(),
                                                  upper=c.UPPER.tolist(), records=records, wall_seconds=monotonic()-tick))
    for q in records:
        print(q['coordinate'], f"{q['value']:+.5g}", q['failed'], q['families'], round(q['seconds'], 1))
    print('wall', monotonic()-tick, 'cpu', sum(q['seconds'] for q in records))
