"""Tabulate the census: failed rows per draw by family, beside the recorded campaign refusal."""
from collections import Counter
import json

import starts as c

census = c.r.read(c.HERE/'results/census.json.gz')
recorded = {v['start']['draw']: v.get('reason', 'eligible') for v in c.r.read(c.OUT/'MDEA/replacement-starts.json.gz')['draws'].values()}
for label in 'BC':
    recorded[c.MANIFEST['starts'][label]['draw']] = c.r.read(c.OUT/f'MDEA/{label}.json.gz')['report']['message']


def kind(reason):
    for key in ('eligible', 'LOCAL_INFEASIBILITY', 'MAXITER_EXCEEDED', 'ill_conditioned', 'saturation:loading', 'no_resolved_root', 'unresolved_slope_reversal'):
        if key in reason:
            return key
    return reason


T_COLD, T_HOT, T_REF = 288.71, 422.04, 423.
table = []
for q in sorted(census['records'], key=lambda q: -1 if q['draw'] is None else q['draw']):
    bad = [(i, x) for i, x in enumerate(q['rows']) if x['status'] != 'Available' or not x['requested_tolerance_met']]
    a0, a1 = q['vector'][:2]
    table.append(dict(draw=q['draw'], recorded=kind(recorded.get(q['draw'], 'start A')), failed=len(bad),
                      families=dict(Counter(x['group'] for _, x in bad)), first=bad[0][0] if bad else None,
                      first_matches=bool(bad) and (bad[0][1]['message'] or '').strip() == recorded.get(q['draw'], '').strip(),
                      k_cold=a0+a1*(T_COLD-T_REF), k_hot=a0+a1*(T_HOT-T_REF), vector=q['vector'], seconds=q['seconds']))
c.refit.save(c.HERE/'results/census-summary.json', dict(rows=table, wall_seconds=census['wall_seconds'],
             cpu_seconds=sum(q['seconds'] for q in census['records'])))
for t in table:
    print(f"{str(t['draw']):>4} {t['recorded'][:26]:26} failed {t['failed']:3d} first {str(t['first']):>4} match {t['first_matches']!s:5} "
          f"k(288.71)={t['k_cold']:+.3f} k(422.04)={t['k_hot']:+.3f} {json.dumps(t['families'])}")
only_merkley = [t for t in table if t['failed'] and set(t['families']) == {'Merkley'}]
print('draws', len(table)-1, 'only Merkley rows fail', len(only_merkley), Counter(t['recorded'] for t in only_merkley))
print('other', Counter(t['recorded'] for t in table if t['failed'] and set(t['families']) != {'Merkley'}))
print('wall', census['wall_seconds'], 'cpu', sum(q['seconds'] for q in census['records']))
