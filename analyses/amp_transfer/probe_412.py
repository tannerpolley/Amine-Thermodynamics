"""#412 cause probes: change one extrapolated law of the #404 main fit and repeat the native search on its descent states."""
import copy
import gzip
import json
import math
import sys
import time

from part_ii import Route, stable
from refit_404 import DECLARATIONS, AMP

MAIN = AMP/'results/retransfer-404-05e94210/main'
EDGE = 353.22  # top of the measured AMP dissociation constants (Hamborg and Versteeg 2009, Table 16)
PAIRS = {'AMPH-water': 'pair/protonated-aminomethylpropanol/water/k_ij',
         'AMP-water': 'pair/aminomethylpropanol/water/k_ij'}
T_REF = 313.15  # reference temperature of both k_ij laws in parameters.json


def freeze_pair(point, label, T=EDGE):
    """k_ij(T) held at its value at T: same value at T, no reciprocal-temperature drift."""
    k = PAIRS[label]
    v = stable.s.parameter_values(point['parameters'])
    value = v[k]+v[k+'/reciprocal_temperature_slope']*(1/T-1/T_REF)
    return dict(point, parameters=stable.s.with_parameter_values(point['parameters'], {k: value, k+'/reciprocal_temperature_slope': 0.}))


def law(point, name):
    return next(r['correlation'] for g in point['reactions'].values() for r in g if r['name']==name)


def ln_k(c, T):
    return c['a']+c['b']/T+c.get('c', 0.)*math.log(T)


def freeze_law(point, name, T=EDGE, enthalpy=False):
    """ln K held at its value at T, or (enthalpy=True) continued with the constant enthalpy at T."""
    point = copy.deepcopy(point)
    c = law(point, name)
    value, slope = ln_k(c, T), -c['b']+c.get('c', 0.)*T  # d ln K/d(1/T) = -(Delta H)/R
    b = -slope if enthalpy else 0.
    c.update(a=value-b/T, b=b, c=0.)
    return point


def set_value(point, identities, value):
    return dict(point, parameters=stable.s.with_parameter_values(point['parameters'], {k: value for k in identities}))


DIAMETER = ['component/carbamate-anion/'+f for f in ('segment_diameter', 'debye_huckel_diameter', 'born_diameter')]
PROBES = {
    'base': lambda p: p,
    'AMPH-water-353': lambda p: freeze_pair(p, 'AMPH-water'),
    'AMP-water-353': lambda p: freeze_pair(p, 'AMP-water'),
    'both-pairs-353': lambda p: freeze_pair(freeze_pair(p, 'AMPH-water'), 'AMP-water'),
    'dissociation-353': lambda p: freeze_law(p, 'AMP-dissociation'),
    'dissociation-constant-enthalpy': lambda p: freeze_law(p, 'AMP-dissociation', enthalpy=True),
    'hydrolysis-353': lambda p: freeze_law(p, 'carbamate-hydrolysis'),
    'carbamate-diameter-floor': lambda p: dict(set_value(set_value(p, DIAMETER, 5.34799141560911),
                                                         ['component/carbamate-anion/packing_diameter'], .88*5.34799141560911)),
}


def main(case, names):
    """case f0: the retained #404 main set; case f2: the #412 F2 reference refit (fit_412.py reference)."""
    route = Route(DECLARATIONS/'AMP-05e94210.json', AMP/f'results/runs/412-{case}-probes')
    route.check_run_output()
    if case=='f0':
        base, searched = stable.read(MAIN/'parameters.json'), json.load(gzip.open(MAIN/'search-0.json.gz'))
    else:
        reference = AMP/'results/runs/404-f2-412/main'
        selected = stable.read(reference/'selection.json')['selected']
        base = next(e['endpoint'] for e in stable.read(reference/'fits.json') if e['start']==selected)
        searched = stable.read(reference/f'search-{selected}.json')
    keys = {r['key'] for r in searched if r['descent']}
    states = [s for s in route.states(route.bind(base)) if s['key'] in keys]
    assert len(states)==len(keys) and (case!='f0' or len(keys)==92)
    out = route.result('probes.json') if (route.out/'probes.json').exists() else {}
    for name in names:
        point = PROBES[name](base)
        started = time.monotonic()
        rows = route.grid(point, states, trial_set=[])
        descents = [r for r in rows if stable.descent(r)]
        spec, hit = route.bind(point), {r['key'] for r in descents}
        out[name] = dict(states=len(rows), available=sum(bool(r.get('available')) for r in rows), descent=len(descents),
                         minimum_tau=min((r['value'] for r in descents if r.get('available')), default=None),
                         descent_temperatures_K=sorted({route.temperature(spec, s) for s in states if s['key'] in hit}),
                         seconds=time.monotonic()-started, workers=route.workers)
        route.write('probes.json', out)
        print(name, out[name], flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:] or list(PROBES))
