"""#410 probe: why the water-DEA excess enthalpy has the wrong sign.

Selected #398 endpoint on the pinned 05e94210 wheel. Probes are disposable
parameter edits; no retained parameter or result changes.
Run: AGENT_HEAVY_CORES=1 .venv/bin/python analyses/dea_transfer/diagnosis-410/excess_enthalpy.py <scratch-run-dir>
"""
import copy, csv, json, math, sys
from pathlib import Path
import numpy as np
from common import AN, REF, endpoint, mixture, save
from epcsaft import equilibrium as eq

R = 8.314462618
T, P = 363.15, 1.75e6  # Horstmann 2002 Table 6
W, D = 'water', 'diethanolamine'
TERMS = ('hard_chain', 'dispersion', 'association')
HE_ROWS = [(float(r['water']), float(r['observed'])) for r in csv.DictReader(open(AN/'inputs/part-ii-346/horstmann-current.csv'))]
VLE_ROWS = [(365.15, float(r['x_water']), float(r['P_kPa'])) for r in csv.DictReader(open(REF/'Horstmann2002_Table4_water_DEA_365K.csv'))]
CAI_ROWS = [(float(r['T']), float(r['water']), float(r['P'])/1e3) for r in csv.DictReader(open(AN/'inputs/part-ii-346/cai.csv'))]


def terms(m, x):
    """Residual enthalpy split: U_k = -RT^2 (da_k/dT) at fixed density and composition, plus RT(Z-1)."""
    s = m.state(T, P=P, x=x, phase='liquid')
    up, dn = (m.state(T+h, rho=s.molar_density, x=x) for h in (0.01, -0.01))
    out = {t: -R*T*T*(getattr(up, t)-getattr(dn, t))/0.02 for t in TERMS}
    out.update(pv=R*T*(s.compressibility_factor-1), total=s.residual_enthalpy)
    other = s.residual_helmholtz - sum(getattr(s, t) for t in TERMS)
    assert abs(other) < 1e-12, other  # no ions: only these three terms exist
    return out, s


def excess(m):
    ids = list(m.component_ids)
    pure = {c: terms(m, {c: 1.0}) for c in (W, D)}
    rows = []
    for xw, observed in HE_ROWS:
        x = {W: xw, D: 1-xw}
        mix, s = terms(m, x)
        ex = {k: mix[k]-xw*pure[W][0][k]-(1-xw)*pure[D][0][k] for k in mix}
        assert abs(sum(ex[k] for k in (*TERMS, 'pv'))-ex['total']) < 1e-3*max(1, abs(ex['total']))
        lnphi = s.log_fugacity_coefficient
        ge = R*T*sum(xc*(lnphi[ids.index(c)]-pure[c][1].log_fugacity_coefficient[ids.index(c)]) for c, xc in x.items())
        rows.append(dict(x_water=xw, observed_HE=observed, HE=ex['total'], split={k: ex[k] for k in (*TERMS, 'pv')}, GE=ge))
    return rows


def bubble(m, rows=VLE_ROWS):
    out = []
    for TT, xw, p in rows:
        if not 0 < xw < 1:
            continue
        support = [W, D]
        problem = eq.problem_from_mapping(dict(T=TT, P=dict(free=True, guess=1e3*p), feed=dict(basis='amounts', values={W: xw, D: 1-xw}),
            phases=[dict(name='L', kind='liquid', support=support), dict(name='V', kind='vapor', support=support, amount=dict(status='pinned', value=0.0))], row_tolerance=1e-10))
        r = eq.solve_equilibrium(m, problem)
        out.append(r.pressure/1e3/p-1 if r.requested_tolerance_met else math.nan)
    return dict(rows=len(out), MARE_percent=100*float(np.nanmean(np.abs(out))), bias_percent=100*float(np.nanmean(out)), unavailable=int(np.isnan(out).sum()))


def summary(name, doc, note):
    m = mixture(doc)
    rows = excess(m)
    i = min(range(len(rows)), key=lambda k: rows[k]['observed_HE'])
    return dict(case=name, note=note, rows=rows, at_measured_minimum=rows[i],
                mean_signed_error_HE=float(np.mean([r['HE']-r['observed_HE'] for r in rows])), horstmann_365K_bubble=bubble(m),
                cai_6_66kPa_bubble=bubble(m, CAI_ROWS))


def pair(doc, a, b):
    return next(p for p in doc['pairs'] if {p['component_id_a'], p['component_id_b']} == {a, b})


def with_slope(doc, slope):
    """k_ij(T) = k + b(1/T - 1/313.15 K); k shifted so k_ij(365.15 K), where it was fitted, is unchanged."""
    d = copy.deepcopy(doc)
    c = {i['family']: i for i in pair(d, D, W)['coefficients']}
    c['k_ij']['value']['magnitude'] -= slope*(1/365.15-1/313.15)
    c['k_ij_reciprocal_temperature_slope']['value']['magnitude'] = slope
    return d


def sigma_water(T):
    return 2.780432614942962+10.11*math.exp(-0.01775*T)-1.417*math.exp(-0.01146*T)


def frozen_water_sigma(doc):
    d = copy.deepcopy(doc)
    c = next(c for c in d['correlations'] if c['component_id'] == W and c['family'] == 'segment_diameter')
    c['constant']['value']['magnitude'] = sigma_water(T)
    for term in c['terms']:
        term['amplitude']['value']['magnitude'] = 0.0
    return d


def explicit_cross(doc, factor):
    """Replace the DEA-water Wolbach-Sandler edges by explicit values at 363.15 K, energy scaled by `factor`."""
    d = copy.deepcopy(doc)
    edges = d['topology']['edges']
    own = {e['endpoint_a']['component_id']: e for e in edges if e['endpoint_a']['component_id'] == e['endpoint_b']['component_id'] and e['endpoint_a']['component_id'] in (W, D)}
    sig = dict(water=sigma_water(T), diethanolamine=2.9477)
    eps = (own[W]['energy_over_k']['value']['magnitude']+own[D]['energy_over_k']['value']['magnitude'])/2
    kap = math.sqrt(own[W]['volume']['value']['magnitude']*own[D]['volume']['value']['magnitude'])*(math.sqrt(sig[W]*sig[D])/((sig[W]+sig[D])/2))**3
    for e in edges:
        if {e['endpoint_a']['component_id'], e['endpoint_b']['component_id']} == {W, D}:
            e['source'] = dict(kind='explicit', provenance=[dict(source_id='issue-410', locator=f'disposable probe: Wolbach-Sandler values at {T} K, energy x {factor}')])
            e['energy_over_k'] = dict(identity=f"probe/{e['endpoint_a']['site_id']}/{e['endpoint_b']['site_id']}/energy", value=dict(magnitude=eps*factor, unit='kelvin'))
            e['volume'] = dict(identity=f"probe/{e['endpoint_a']['site_id']}/{e['endpoint_b']['site_id']}/volume", value=dict(magnitude=kap, unit='dimensionless'))
    return d, eps, kap


def main(out):
    doc = endpoint(out)['parameters']
    cases = [summary('selected #398 endpoint', doc, 'reproduces the retained Horstmann predictions')]
    cases.append(summary('water sigma frozen at 363.15 K', frozen_water_sigma(doc), 'removes d(sigma_water)/dT; pure water enthalpy changes too'))
    for slope in (-200.0, -400.0):
        cases.append(summary(f'k_ij slope {slope} K', with_slope(doc, slope), 'k_ij(365.15 K) held at the fitted -0.06363'))
    # Linear estimate of the slope that zeroes the mean signed HE error (HE is nearly linear in the slope); one probe point, not a fit.
    estimate = -200.0*cases[0]['mean_signed_error_HE']/(cases[0]['mean_signed_error_HE']-cases[2]['mean_signed_error_HE'])
    cases.insert(2, summary(f'k_ij slope {estimate:.1f} K (linear estimate)', with_slope(doc, estimate), 'k_ij(365.15 K) held at the fitted -0.06363'))
    explicit, eps, kap = explicit_cross(doc, 1.0)
    cases.append(summary('explicit cross association, factor 1', explicit, f'check: must reproduce baseline (eps {eps:.2f} K, kappa {kap:.6g})'))
    for factor in (1.05, 1.10, 1.15):
        cases.append(summary(f'cross association energy x {factor}', explicit_cross(doc, factor)[0], 'k_ij unchanged'))
    for shift in (0.02, 0.04):  # sensitivity points: can k_ij restore the 365 K isotherm while the stronger cross bond keeps HE negative?
        d = explicit_cross(doc, 1.15)[0]
        pair(d, D, W)['coefficients'][0]['value']['magnitude'] += shift
        assert pair(d, D, W)['coefficients'][0]['family'] == 'k_ij'
        cases.append(summary(f'cross association x 1.15, k_ij {shift:+.2f}', d, 'two-coordinate sensitivity point'))
    a, b = (m.state(T, rho=30000.0, x={W: 0.6, D: 0.4}).association for m in (mixture(doc), mixture(explicit)))
    assert abs(a-b) < 1e-12, 'explicit edges must reproduce the combining-rule values at 363.15 K'
    # Explicit volume is constant in T; the combining rule follows sigma_water(T). The HE gap at factor 1 is that d(kappa)/dT term.
    cases[5]['kappa_temperature_term_HE'] = [r1['HE']-r0['HE'] for r0, r1 in zip(cases[0]['rows'], cases[5]['rows'])]
    save('diagnosis-410/excess-enthalpy.json', dict(T_K=T, P_Pa=P, cases=cases))
    for c in cases:
        r = c['at_measured_minimum']
        print(f"{c['case']:42s} HE(x={r['x_water']})={r['HE']:8.1f} GE={r['GE']:7.1f} split={ {k: round(v) for k, v in r['split'].items()} } "
              f"MSE={c['mean_signed_error_HE']:7.1f} VLE365 MARE={c['horstmann_365K_bubble']['MARE_percent']:.2f}% bias={c['horstmann_365K_bubble']['bias_percent']:+.2f}% "
              f"Cai MARE={c['cai_6_66kPa_bubble']['MARE_percent']:.1f}% bias={c['cai_6_66kPa_bubble']['bias_percent']:+.1f}%", flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
