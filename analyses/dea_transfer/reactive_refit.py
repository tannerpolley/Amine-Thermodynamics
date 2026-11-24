"""Run #425 §D with the temperature-dependent binary frozen in the #413 campaign."""
import math
from pathlib import Path
import sys
from time import monotonic

from binary_refit import AN, CAI, OLD, PREFIX, Route, T_REF, composition, pair, with_binary
from f2_carbamate import read, sha
from part_ii import ROOT, SHARED, epcsaft
from pinned import DEA, W
import rerun

BINARY = AN/'results/binary-refit-425/unconstrained-1/fit.json'
ROUTE = OLD/f'{PREFIX}route.json'
ADOPTED = ROOT/'analyses/solvent_specification_mea/inputs/endpoint.json'


class FrozenBinaryRoute(Route):
    def __init__(self, out):
        super().__init__(ROUTE, out)
        fit = read(BINARY)
        self.a, self.b = fit['a'], fit['b']
        self.pair = pair(with_binary(self.load(self.config['starts'][0]), self.a, self.b), DEA, W)
        self.search_files = {}

    def start(self, reference, *, adopt=True):
        point = super().start(reference, adopt=adopt)
        point['parameters'] = with_binary(point['parameters'], self.a, self.b)
        return point

    def bind(self, point):
        assert pair(point['parameters'], DEA, W) == self.pair, 'Frozen DEA–water interaction changed'
        return super().bind(point)

    def bound_readback(self, point):
        spec = self.bind(point)
        cai = [r['T'] for r in read(BINARY)['rows'] if r['group'] == CAI and r['fitted']]
        rows = []
        for T in sorted({313.15, T_REF, min(cai), max(cai), *self.config['calculation_interval_K']}):
            k = self.a + self.b*(1/T-1/T_REF)
            constant = epcsaft.Mixture(epcsaft.Parameters.from_mapping(with_binary(point['parameters'], k, 0.)))
            args = dict(T=T, rho=10000, x=composition(.5))
            error = spec.model.state(**args).dispersion - constant.state(**args).dispersion
            assert abs(error) < 1e-12, (T, error)  # #425 binary dispersion readback
            rows.append(dict(T_K=T, k=k, dispersion_difference=error))
        return rows

    def grid(self, point, states, *, trial_set=None):
        count, begin = len(list(self.out.glob('search-*.json'))), monotonic()
        rows = super().grid(point, states, trial_set=trial_set)
        if (self.out/f'search-{count}.json').exists():
            self.search_files[id(rows)] = f'search-{count}.json'
            self.write(f'endpoint-search-{count}.json', point)
            print(f'search-{count}: {monotonic()-begin:.1f} s', flush=True)
        self.last_search_file = self.search_files[id(rows)]
        return rows

    def search(self, point):
        return dict(super().search(point), search_file=self.last_search_file)


def probe(route):
    point = route.start(route.config['starts'][0])
    route.bound_readback(point)
    begin = monotonic()
    rows, available, cost = route.replay(point)
    result = dict(seconds=monotonic()-begin, rows=rows, available=available, cost=cost)
    route.write('objective-probe.json', result)
    print(f'80-row objective: {result["seconds"]:.2f} s, available={available}, cost={cost}', flush=True)
    assert len(rows) == 80 and available and math.isfinite(cost)


def campaign(route):
    adopted, shared = read(ADOPTED), read(SHARED)
    starts = [route.start(ref) for ref in route.config['starts']]
    checks = dict(binary_fit_sha256=sha(BINARY), bound_starts=[route.bound_readback(p) for p in starts])
    for point in starts:
        rerun.check_shared(point, adopted, shared)
        states = route.states(route.bind(point))
        assert len(states) == 1271 and sum(s['key'].startswith('grid:') for s in states) == 936
    registry = route.load(route.config['split_record'])
    assert not registry['trials'] and not registry.get('supplied_trials')
    for i, point in enumerate(starts):
        route.write(f'binary-frozen-start-{i}.json', point)
    route.write('checks.json', checks)
    begin = monotonic()
    chosen = route.campaign()
    route.write('timings.json', dict(campaign_s=monotonic()-begin))
    if chosen:
        checks['bound_endpoint'] = route.bound_readback(chosen['parameters'])
        route.write('checks.json', checks)
        rerun.report(route, ADOPTED, shared)


if __name__ == '__main__':
    command, output = sys.argv[1:3]
    route = FrozenBinaryRoute(Path(output))
    {'probe': probe, 'campaign': campaign}[command](route)
