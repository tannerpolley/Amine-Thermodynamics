"""Per-draw cause and what each proposed correction would leave refused (issue #429). Reads the retained probes only."""
from collections import Counter
import json

import retained_starts as c

np = c.np
read = lambda name: c.r.read(c.HERE/'results'/name)  # noqa: E731
census = {q['draw']: q for q in read('census.json.gz')['records'] if q['draw'] is not None}
gap = {q['draw']: q for q in read('gap.json.gz')['records'] if q['draw'] is not None}
sat = {q['draw']: q for q in read('saturation.json.gz')['records'] if q['draw'] is not None}
cont = {q['draw']: q for q in read('continuation.json.gz')['records']}
critical = json.loads((c.refit.MDEA.RESULTS/'critical-k.json').read_text())['rows']
Tc, kc = np.array([q['T_K'] for q in critical]), np.array([q['k_no_gap'] for q in critical])

# Retained #411 gap-onset k(T) against this model's hull at every drawn k(T).
agree = Counter()
for q in gap.values():
    for T, k, has in {(x['T'], x['k'], bool(x['gaps'])) for x in q['rows']}:
        agree[k > np.interp(T, Tc, kc), has] += 1
print('k above retained gap onset, hull gap found:', dict(agree))


def decided(q):
    """Capped endpoint fixed by solved nodes alone: a crossing at or below the cap, or every node up to the cap below target."""
    nodes = [n for n in q['nodes'] if n['solved']]
    for i, n in enumerate(q['nodes']):
        if not n['solved']:
            return False
        if n['mismatch'] >= 0:
            return i > 0
        if n['loading'] >= q['cap']:
            return True
    return bool(nodes) and nodes[-1]['loading'] >= q['cap']


rows = []
for d in sorted(census):
    bad = [x for x in census[d]['rows'] if x['status'] != 'Available']
    families = Counter(x['group'] for x in bad)
    unstable = sum(x['hull'] != 'stable' for x in gap[d]['rows'])
    merkley = [q for q in sat[d]['rows'] if q['status'] != 'Available']
    cause = ('none' if not bad else 'MDEA-water liquid split' if unstable else
             'Merkley saturation search only' if set(families) == {'Merkley'} else 'bubble pressure beyond vapor-like CO2')
    rows.append(dict(draw=d, cause=cause, failed=len(bad), families=dict(families), hull_unstable_binary_rows=unstable,
                     merkley_unavailable=len(merkley), merkley_decided_by_solved_nodes=sum(map(decided, merkley)),
                     continuation=dict(Counter('reached' if x['reached_target'] else 'stalled' for x in cont[d]['rows'])) if d in cont else None))
print(Counter(q['cause'] for q in rows))
only = [q for q in rows if q['cause'] == 'Merkley saturation search only']
print('Merkley-only draws:', len(only), 'all unavailable searches decided by solved nodes:',
      sum(q['merkley_unavailable'] == q['merkley_decided_by_solved_nodes'] for q in only))
print('searches in those draws: unavailable', sum(q['merkley_unavailable'] for q in only), 'decided', sum(q['merkley_decided_by_solved_nodes'] for q in only))
c.refit.save(c.HERE/'results/outlook.json', dict(critical_k_agreement={f'{a}/{b}': v for (a, b), v in agree.items()}, draws=rows))
for label in ('A', 'LHS-53'):
    report = c.r.read(c.OUT/f'MDEA/{label}.json.gz')['report']
    print(label, 'trial failures', report['trial_failures'], Counter((f['observation'], f['message'].split(':')[1][:14]) for f in report['failures']))
