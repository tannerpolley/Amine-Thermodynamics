"""Read back DEA reactive stability witnesses with the #343 two-liquid solve."""
from pathlib import Path
import sys

import numpy as np

from binary_refit import REFERENCE
from reactive_refit import AN, FrozenBinaryRoute, read
from part_ii import stable

sys.path.insert(0, str(AN.parent/'amp_transfer'))
from classify_descents import COINCIDENCE, classify


def targeted(route, point, states, primary, registry):
    by_key = {s['key']: s for s in states}
    affected = [by_key[r['key']] for r in primary if stable.descent(r) or not r['available']]
    if not affected:
        return [], []
    route.short_rows = False
    rows = stable.grid(point, affected, registry, route=route, capture=True)
    spec = route.bind(point)
    for row in rows:
        if not row.get('supplied_trials'):
            continue
        item = route.stability_row(spec, by_key[row['key']], 1.)
        support = {i for i, amount in enumerate(item.problem.feed.values) if amount > 0}
        support.update(i for rx in item.problem.reactions for i, v in enumerate(rx.stoichiometry) if v != 0)
        _, _, repeated, _ = stable._applicable(item, registry, support)
        row['supplied_trial_evidence'] = [
            dict(trial, phase=witness) for trial, (_, witness) in zip(row['supplied_trials'], repeated, strict=True)]
    entries = classify(route, point, rows, states)
    for entry in entries:
        if entry['attempts']:
            parent = route.stability_row(spec, by_key[entry['key']], 1.).problem
            stoichiometry = np.array([rx.stoichiometry for rx in parent.reactions]).reshape(-1, len(parent.feed.values))
            for attempt in entry['attempts']:
                if 'phases' not in attempt:
                    continue
                amounts, phases = np.array(attempt['amounts_mol']), np.array(attempt['phases'])
                difference = amounts @ phases - entry['feed_mol']
                extents = np.linalg.lstsq(stoichiometry.T, difference, rcond=None)[0]
                balance = np.max(abs(difference - stoichiometry.T @ extents))
                distance = np.max(abs(phases[0] - phases[1]))
                attempt.update(max_composition_difference=distance, max_conserved_balance_residual_mol=balance,
                               confirmed=attempt['confirmed'] and distance > COINCIDENCE and balance <= parent.row_tolerance)
        entry['confirmed'] = any(a['confirmed'] for a in entry['attempts'])
    return rows, entries


def report(route):
    chosen = route.result('selection.json')['chosen']
    point, search = chosen['parameters'], chosen['search']
    spec = route.bind(point)
    states, primary = route.states(spec), route.result(search['search_file'])
    assert [s['key'] for s in states] == [r['key'] for r in primary]
    registry = route.result('split-record.json')
    rows, entries = targeted(route, point, states, primary, registry['trials'] + registry.get('supplied_trials', []))
    confirmed = {e['key'] for e in entries if e['confirmed']}
    reference = read(REFERENCE/'selection.json')['chosen']['search']['grid']
    old_unavailable = set(reference['unavailable'])
    data = {}
    for group in ('data', 'grid'):
        subset = [r for r in primary if r['key'].startswith('grid:') == (group == 'grid')]
        tally = stable.tally(subset)
        liquid = {r['key'] for r in subset if any(r[f'{method}_branch'] in ('liquid', 'mixed') for method in ('native', 'supplied'))}
        vapor = {r['key'] for r in subset if any(r[f'{method}_branch'] in ('vapor', 'mixed') for method in ('native', 'supplied'))}
        keys = {r['key'] for r in subset}
        unresolved = set(tally['unavailable']) | (liquid - confirmed)
        unresolved |= {e['key'] for e in entries if e['key'] in keys and
                       ('classification_error' in e or 'unresolved' in (e['native_branch'], e['supplied_branch']))}
        data[group] = dict(tally, vapor_descents=sorted(vapor), liquid_descents=sorted(liquid),
                           confirmed=sorted(confirmed & keys), unconfirmed_liquid=sorted(liquid - confirmed),
                           unresolved=sorted(unresolved), newly_unavailable=sorted(set(tally['unavailable']) - old_unavailable),
                           previously_unavailable_now_available=sorted((old_unavailable & keys) - set(tally['unavailable'])))
    route.write('stability-readback.json', dict(reference=reference, sections=data, selected_search=search['search_file'],
                                               states=states, targeted=rows, classification=entries))
    print({k: {f: len(v[f]) for f in ('unavailable', 'vapor_descents', 'liquid_descents', 'confirmed')}
           for k, v in data.items()}, flush=True)


if __name__ == '__main__':
    report(FrozenBinaryRoute(Path(sys.argv[1])))
