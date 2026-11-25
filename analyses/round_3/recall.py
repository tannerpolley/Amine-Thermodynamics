"""Issue #432 Q7. Empty-bank AMP replays in bounded, independently retained batches."""
import gzip
import json
import math
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from part_ii import ROOT, Route, stable

AMP = ROOT / 'analyses/amp_transfer'
DECLARATION = AMP / 'inputs/retransfer-344/phase-2/AMP-05e94210.json'
ENDPOINTS = AMP / 'results/retransfer-412-f2-05e94210'
OUT = Path(__file__).resolve().parent / 'results'


def recall(work):
    from part_ii import SHARED
    from reference_states_428 import identity
    from run import receipt

    start = monotonic()
    route = Route(DECLARATION, work)
    point = stable.read(ENDPOINTS / 'main/parameters.json')
    archive = ENDPOINTS / 'main/search-1.json.gz'
    old = {r['key']: r for r in stable.read(archive)}
    inputs = identity(archive, ENDPOINTS/'main/parameters.json', DECLARATION, SHARED, DECLARATION.with_name('specification.toml'))
    states = route.states(route.bind(point))
    aliases = route.same_calculations(point, states)
    assert old.keys() == {s['key'] for s in states} and len(old) == 666
    assert aliases == {k: r['same_calculation_as'] for k, r in old.items() if 'same_calculation_as' in r}
    assert sum(stable.descent(r) and bool(r['witnesses']) for r in old.values()) == 93
    positives = {aliases.get(k, k) for k, r in old.items() if stable.descent(r)}
    canonical = [s for s in states if s['key'] not in aliases]
    groups = [[s for s in canonical if (s['key'] in positives)==positive] for positive in (True,False)]
    spec = route.bind(point)
    done, batches = {}, []
    for batch in (g[i:i+18] for g in groups for i in range(0,len(g),18)):
        batch_start = monotonic()
        for state, row in zip(batch, route.grid(point, batch, trial_set=[]), strict=True):
            key = row['key']
            item = route.stability_row(spec, state, 1.)
            bubble = row.get('pressure_Pa')
            pressure = item.problem.pressure.value if item.pressure_reference is None else None if bubble is None else bubble*item.pressure_ratio
            for k in [key, *(a for a, source in aliases.items() if source == key)]:
                prior = old[k]
                archived = prior.get('supplied_parent_pressure_Pa')
                matched = None if archived is None or pressure is None else math.isclose(archived, pressure, abs_tol=.01, rel_tol=0.)
                found = bool(stable.descent(row) and row.get('witnesses') and row['raw_minimum'] < -row['uncertainty'])
                outcome = ('unavailable' if matched is False or not row['available'] or pressure is None
                           else 'resolved descent' if found else 'no resolved descent')
                done[k] = dict(row, key=k, same_calculation_as=aliases.get(k), archived_descent=stable.descent(prior),
                               archived_search_Pa=archived, replay_search_Pa=pressure, pressure_matched=matched, outcome=outcome)
        batches.append(dict(rows=len(batch), seconds=monotonic()-batch_start))
        replay_path = OUT / 'q7-recall.json.gz'
        staged = replay_path.with_suffix('.tmp')
        with gzip.GzipFile(staged, 'wb', mtime=0) as file:
            file.write(json.dumps(list(done.values()), allow_nan=False).encode())
        staged.replace(replay_path)
        elapsed = monotonic()-start
        processed = sum(b['rows'] for b in batches)
        projected = elapsed + sum(b['seconds'] for b in batches)/processed*(len(canonical)-processed)
        print('Q7', len(done), round(elapsed, 1), round(projected, 1), flush=True)
        summary = dict(inputs=inputs, **receipt(), seconds=elapsed, batches=batches, projected_seconds=projected, total=len(old),
                       searched=len(done), matched_pressure=sum(r['pressure_matched'] is True for r in done.values()),
                       missing_archived_pressure=sum(r['archived_search_Pa'] is None for r in done.values()),
                       archived_positive=93,
                       recovered=sum(r['archived_descent'] and r['outcome']=='resolved descent' for r in done.values()),
                       missed=sum(r['archived_descent'] and r['outcome']=='no resolved descent' for r in done.values()),
                       new_detections=sum(not r['archived_descent'] and r['outcome']=='resolved descent' for r in done.values()),
                       searched_negatives=sum(not r['archived_descent'] for r in done.values()),
                       unavailable_searches=sum(r['outcome']=='unavailable' for r in done.values()))
        summary['positive_unavailable'] = 93-summary['recovered']-summary['missed']
        (OUT / 'q7-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
        if elapsed + max(b['seconds'] for b in batches) >= 600 or (processed >= len(positives) and projected >= 600):
            break


if __name__ == '__main__':
    with TemporaryDirectory() as directory:
        recall(Path(directory))
