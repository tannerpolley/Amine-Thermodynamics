"""Sampled CO2-free MDEA-water tangent-plane distances and hull gaps (#421)."""
from bounded_binary_411 import FINE, OLD, RESULTS, binary_gaps, binary_model, critical, k_at, np, stable

TEMPERATURES = (422.04, 423., 423.05, 423.10, 423.15, 423.20, 423.25, 423.50, 424., 425., 430.)
PRESSURES = (1121000., 1466000., 1811000.)
REFINED = np.sort(np.r_[FINE, (FINE[:-1]+FINE[1:])/2])


def isotherm(model, T, P, x):
    amine = 'methyldiethanolamine'
    assert len(FINE) == 5490 and np.all(np.diff(x) > 0)
    y = np.array([x if c == amine else 1-x for c in model.component_ids]).T
    batch = model.states([T]*len(x), P=P, x=y.tolist(), phase='liquid')
    unavailable, gaps = binary_gaps(model, amine, T, P, x, batch=batch)
    out = dict(T_K=T, P_Pa=P, compositions=len(x), unavailable=unavailable, gaps=gaps, classification=None)
    if unavailable:
        return out
    mu = np.log(y) + batch.log_fugacity_coefficient
    best, parent, trial = 0., 0, 0
    for start in range(0, len(x), 256):
        m = mu[start:start+256]
        tpd = y[:, 0]*(mu[:, 0]-m[:, 0, None]) + y[:, 1]*(mu[:, 1]-m[:, 1, None])
        assert np.all(tpd[np.arange(len(m)), start+np.arange(len(m))] == 0.)
        i, j = np.unravel_index(tpd.argmin(), tpd.shape)
        if tpd[i,j] < best:
            best, parent, trial = float(tpd[i,j]), start+i, j
    g = (mu*y).sum(axis=1)
    resolution = float(16*np.spacing(max(1., abs(g[parent]), abs(g[trial]))))
    classification = bool(gaps) if bool(gaps) == (best < -resolution) else None
    return dict(out, tpd_over_RT=best, x_MDEA_parent=float(x[parent]), x_MDEA_trial=float(x[trial]),
                tpd_roundoff=resolution, classification=classification)


def bracket_onset(model, P):
    rows, brackets = {}, []
    def resolved(T):
        coarse, fine = [isotherm(model, T, P, x) for x in (FINE, REFINED)]
        flag = coarse['classification'] if fine['classification'] == coarse['classification'] else None
        rows[T] = dict(coarse=coarse, refined=fine, gap=flag)
        return flag
    flags = [resolved(T) for T in TEMPERATURES]
    for lo, hi, left, right in zip(TEMPERATURES, TEMPERATURES[1:], flags, flags[1:]):
        if left is None or right is None or left == right:
            continue
        sampled = [lo, hi]
        while hi-lo > .01:
            mid = (lo+hi)/2
            flag = resolved(mid)
            if flag is None:
                break
            lo, hi = (mid, hi) if flag == left else (lo, mid)
        brackets.append(dict(adjacent_K=sampled, bracket_K=[lo, hi], resolved=hi-lo <= .01, low_side_gap=left))
    return rows, brackets


def binary(route, mapping):
    old = stable.read(OLD/'start-0/endpoint.json')['parameters']
    for cid in ('water', 'methyldiethanolamine'):
        assert next(c for c in mapping['components'] if c['component_id']==cid) == next(c for c in old['components'] if c['component_id']==cid)
    fitted = k_at(mapping, 423.)
    assert fitted == -0.06711345443725586
    onset = stable.read(RESULTS/'critical-k.json')
    middle = next(r for r in onset['rows'] if r['T_K'] == 423.)
    assert onset['pressure_Pa'] == PRESSURES[1] and middle['k_no_gap']-fitted > 0 and len(onset['rows']) == 33
    model = binary_model(mapping)
    for P in PRESSURES:
        rows, brackets = bracket_onset(model, P)
        try:
            bound = middle if P == onset['pressure_Pa'] else critical(mapping, [423.], P)[0]
            bound = dict(bound, fitted_minus_k_no_gap=fitted-bound['k_no_gap'])
        except AssertionError as error:
            bound = dict(refusal=str(error))
        route.write(f'binary-{P:.0f}.json', dict(fitted_k_at_423_K=fitted, k_bound=bound, rows=rows, brackets=brackets))
