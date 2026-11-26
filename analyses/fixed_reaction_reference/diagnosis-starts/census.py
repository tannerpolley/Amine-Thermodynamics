"""Record availability for every observation at every declared MDEA draw."""
from multiprocessing import get_context
from time import monotonic

from starts import refit


def initialize(starts):
    global design
    design = starts


def one(draw):
    # Verify inside the task so a refusal reaches the parent instead of restarting the worker.
    design.run.verify()
    tick = monotonic()
    values = design.vector(draw)
    rows = design.census(values)
    for row in rows:
        row.pop('value')
        tolerance_met = row.pop('requested_tolerance_met')
        if row['status'] == 'Available' and tolerance_met:
            row.pop('message')
        elif row['status'] == 'Available':
            row['status'] = 'ToleranceNotMet'
    return dict(draw=draw, vector=values.tolist(), rows=rows, seconds=monotonic()-tick)


def record(starts, path):
    tick = monotonic()
    workers = min(8, len(refit.os.sched_getaffinity(0)))
    records = []
    # Fork keeps the bound native specification in each worker.
    try:
        with get_context('fork').Pool(workers, initializer=initialize, initargs=(starts,)) as pool:
            for result in pool.imap_unordered(one, range(64)):
                records.append(result)
                print(result['draw'], round(result['seconds'], 1),
                      sum(q['status'] != 'Available' for q in result['rows']), flush=True)
    finally:
        refit.save(path, dict(wheel=starts.run.wheel_sha256, records=sorted(records, key=lambda q: q['draw']),
                             workers=workers, wall_seconds=monotonic()-tick))
