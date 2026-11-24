"""Read back Part II binary stability witnesses and test two-liquid closure (#425)."""
from pathlib import Path
import sys

import numpy as np

from binary_refit import AN, HEAT, OLD, PREFIX, REFERENCE, Route, read, with_binary
from part_ii import stable

sys.path.insert(0, str(AN.parent/'amp_transfer'))
from classify_descents import COINCIDENCE, classify


def stability(out, case):
    route = Route(OLD/f'{PREFIX}route.json', out/case)
    point = read(REFERENCE/'selection.json')['chosen']['parameters']
    fit = route.result('fit.json')
    point['parameters'] = with_binary(point['parameters'], fit['a'], fit['b'])
    states = [dict(key=f"{r['group']}:{r['source_row']}", T=r['T'], binary_x=1-r['x'],
                   P=r['measured_pressure_Pa'], pressure_basis='calorimetric' if r['group']==HEAT else 'measured VLE')
              for r in fit['rows'] if r['fitted']]
    registry = route.load(route.config['split_record'])
    assert not registry['trials'] and not registry.get('supplied_trials')
    rows = stable.grid(point, states, [], route=route, capture=True)
    witnesses = [w for row in rows for w in row['witnesses'] if w['density_side']==2]
    affected = {r['key'] for r in rows if stable.descent(r) or not r['available']}
    targeted = [state for state in states if state['key'] in affected]
    readback = stable.grid(point, targeted, witnesses, route=route, capture=True) if targeted else []
    for row in readback:
        row['supplied_trial_evidence'] = [
            dict(t, phase=w) for t, w in zip(row.get('supplied_trials', []), witnesses)]
    classified = classify(route, point, readback, states)
    for entry in classified:
        for attempt in entry['attempts']:
            if attempt.get('phases'):
                amounts, phases = np.array(attempt['amounts_mol']), np.array(attempt['phases'])
                distance = np.max(abs(phases[0]-phases[1]))
                balance = np.max(abs(amounts @ phases-entry['feed_mol']))
                attempt.update(max_composition_difference=distance, max_material_balance_residual_mol=balance,
                               confirmed=attempt['confirmed'] and distance>COINCIDENCE and balance<=1e-10)
        entry['confirmed'] = any(a['confirmed'] for a in entry['attempts'])
        entry['unresolved'] = 'classification_error' in entry or (
            entry['native_branch'] in ('liquid', 'mixed', 'unresolved') or
            entry['supplied_branch'] in ('liquid', 'mixed', 'unresolved')) and not entry['confirmed']
    route.write('stability.json', dict(states=states, primary=rows, targeted=readback, classification=classified,
                tally=stable.tally(rows), targeted_tally=stable.tally(readback),
                confirmed=sum(e['confirmed'] for e in classified),
                unresolved=sorted({e['key'] for e in classified if e['unresolved']} |
                                  {r['key'] for r in [*rows, *readback] if not r['available']})))
    print(case, stable.tally(rows), flush=True)


if __name__=='__main__':
    out = Path(sys.argv[1])
    for case in sorted(out.glob('*/fit.json')):
        stability(out, case.parent.name)
