"""Model bubble pressure behind the unavailable grid searches at the selected MDEA endpoint (issue #429).

Each grid search first needs the bubble pressure of its stock at T and loading (its pressure reference). March the
loading with warm starts for every stock and temperature, then compare the reached pressure with the search status.
"""
import ast
from collections import Counter, defaultdict
from copy import copy
from multiprocessing import Pool
from time import monotonic

import starts as c

eq = c.refit.eq
SCREEN = c.r.read(c.OUT/'MDEA/screen/selected/declared/summary.json.gz')
GRID = defaultdict(dict)
for q in SCREEN['rows']:
    if q['key'].startswith('grid:'):
        stock, rest = q['key'][5:].rsplit('}', 1)
        _, T, loading, factor = rest.split(':')
        state = GRID[stock+'}', float(T)].setdefault(float(loading), dict(messages=[], available=True))
        state['available'] &= q['status'] == 'Available'
        state['messages'].append(q['message'])
SPEC = None


def one(key):
    global SPEC
    if SPEC is None:
        SPEC = c.RUN.bind(c.r.read(c.OUT/'MDEA/A.json.gz')['endpoint'])
    tick = monotonic()
    stock, T = key
    template = SPEC.problems[next(q for q in c.ROWS if q['group'] == 'Merkley')['bubble']]

    def at(loading):
        p = copy(template)
        p.T = T
        p.feed = copy(template.feed)
        p.feed.values = ast.literal_eval(stock) | {'carbon-dioxide': loading}
        return p

    out, solution = [], None
    for target in sorted(x for x in GRID[key] if x >= .05):
        last, loading, step = (out[-1]['loading'] if out and out[-1]['reached'] else None), target, None
        stalled = bool(out) and not out[-1]['reached']
        message = out[-1]['stall'] if stalled else None
        step = target-(last or 0.)
        while not stalled:
            s = eq.solve_equilibrium(SPEC.model, at(loading), solution)
            if s.success and s.requested_tolerance_met:
                solution, last = s, loading
                if loading >= target:
                    break
                loading = min(target, loading+step)
            else:
                step /= 2
                if step < 1e-3 or last is None:
                    stalled, message = True, s.message
                    break
                loading = min(target, last+step)
        out.append(dict(loading=target, search_available=GRID[key][target]['available'], reached=not stalled,
                        pressure_Pa=solution.pressure if solution is not None and not stalled else None,
                        last_pressure_Pa=None if solution is None else solution.pressure,
                        vapor_density=None if solution is None else list(solution.molar_densities)[-1], stall=message))
    return dict(stock=stock, T=T, states=out, seconds=monotonic()-tick)


if __name__ == '__main__':
    tick = monotonic()
    keys = [k for k, v in GRID.items() if any(not s['available'] for s in v.values())]
    with Pool(8) as pool:
        records = pool.map(one, keys, chunksize=4)
    c.refit.save(c.HERE/'results/searches.json.gz', dict(wheel=c.r.SHA, stock_temperatures=len(keys), records=records,
                                                      wall_seconds=monotonic()-tick))
    tally = Counter()
    for r in records:
        for s in r['states']:
            p = s['pressure_Pa']
            band = 'stalled' if not s['reached'] else '<7.4 MPa' if p < 7.4e6 else '7.4-30 MPa' if p < 3e7 else '>=30 MPa'
            tally['search available' if s['search_available'] else 'search unavailable', band] += 1
    for k, v in sorted(tally.items()):
        print(v, k)
    print(Counter((s['stall'] or '')[:60] for r in records for s in r['states'] if not s['reached']).most_common(5))
    print('wall', monotonic()-tick, 'cpu', sum(r['seconds'] for r in records))
