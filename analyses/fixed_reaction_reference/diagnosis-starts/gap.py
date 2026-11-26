"""Compare each unavailable MDEA–water bubble row with the liquid Gibbs-energy hull at the same draw (issue #429).

The hull (retained #343 routine) uses liquid fugacity coefficients only, so it is independent of the bubble solve.
A feed between the hull contacts is not a stable single liquid; negative curvature there is material instability.
"""
from multiprocessing import Pool
from time import monotonic

import retained_starts as c

M, np = c.refit.MDEA, c.np
AMINE, X, P = 'methyldiethanolamine', c.refit.MDEA.FINE, 101325.
CENSUS = {q['draw']: q for q in c.r.read(c.HERE/'results/census.json.gz')['records']}
STATES = c.MANIFEST['rows']['fitted']
BINARY = [i for i, q in enumerate(c.ROWS) if q['group'] in ('Kim', 'Kuranov-binary')]


def one(draw):
    tick = monotonic()
    spec = c.at(c.ORIGIN if draw is None else c.vector(draw))
    mapping = spec.inputs['endpoint']['parameters']
    model = M.binary_model(mapping)
    y = np.array([X if cid == AMINE else 1-X for cid in model.parameters.component_ids]).T
    out, hulls = [], {}
    for i in BINARY:
        state = STATES[i]['states']['problem']
        feed, T = state['feed']['values'], state['T']
        x = feed.get(AMINE, 0.)/sum(feed.values())
        if not 0 < x < 1:
            continue  # pure-component vapor pressure: no mixing
        if T not in hulls:
            batch = model.states([T]*len(X), P=P, x=y.tolist(), phase='liquid')
            unavailable, gaps = M.binary_gaps(model, AMINE, T, P, X, batch=batch)
            assert unavailable is None, (draw, T)
            g = np.sum(y*(np.log(y)+np.array(batch.log_fugacity_coefficient)), axis=1)
            hulls[T] = gaps, g
        gaps, g = hulls[T]
        j = int(np.argmin(abs(X-x)))
        curvature = float((g[j+1]-g[j])/(X[j+1]-X[j]) - (g[j]-g[j-1])/(X[j]-X[j-1]))
        inside = any(a < x < b for a, b in (q['x_MDEA_contacts'] for q in gaps))
        row = CENSUS[draw]['rows'][i]
        out.append(dict(row=i, group=c.ROWS[i]['group'], T=T, x_MDEA=x, k=M.k_at(mapping, T),
                        gaps=[q['x_MDEA_contacts'] for q in gaps], curvature_sign=int(np.sign(curvature)),
                        hull='stable' if not inside else 'unstable' if curvature < 0 else 'metastable',
                        available=row['status'] == 'Available', message=row['message']))
    return dict(draw=draw, rows=out, seconds=monotonic()-tick)


if __name__ == '__main__':
    from collections import Counter
    tick = monotonic()
    with Pool(8) as pool:
        records = pool.map(one, [None, *(i for i in range(64) if i != 17)])
    c.refit.save(c.HERE/'results/gap.json.gz', dict(wheel=c.r.SHA, pressure_Pa=P, compositions=len(X), records=records,
                                                 wall_seconds=monotonic()-tick))
    tally = Counter((q['group'], q['hull'], 'available' if q['available'] else 'unavailable')
                    for r in records if r['draw'] is not None for q in r['rows'])
    for k, v in sorted(tally.items()):
        print(v, k)
    print('wall', monotonic()-tick, 'cpu', sum(r['seconds'] for r in records))
