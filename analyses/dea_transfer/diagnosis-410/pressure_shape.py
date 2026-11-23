"""#410 probe: cause of the shape error in CO2 partial pressure against loading.

1. Speciation and molality-basis activity coefficients along loading at 313.15 K.
2. Boettinger 2008 apparent carbamate-hydrolysis quotient against the model's.
3. Sensitivity of ln p(CO2) and Boettinger speciation to each DEA-specific parameter and
   reaction constant (plus two shared ones as contrast), with linearized residual reduction.
Selected #398 endpoint, pinned 05e94210 wheel; perturbations are disposable.
Run: AGENT_HEAVY_CORES=1 .venv/bin/python analyses/dea_transfer/diagnosis-410/pressure_shape.py <scratch-run-dir>
"""
import copy, csv, json, math, sys
from pathlib import Path
import numpy as np
from common import AN, endpoint, route, save
from epcsaft import equilibrium as eq

M_W = 0.01801528
SPECIES = ['carbon-dioxide', 'diethanolamine', 'water', 'protonated-diethanolamine', 'carbamate-anion',
           'bicarbonate-anion', 'carbonate-anion', 'hydronium-cation', 'hydroxide-anion']
PRESSURE = ('Lawson', 'Lawson-394K', 'SeoHong', 'Lal')
SPECIATION = ('Bottinger-DEACOO', 'Bottinger-HCO3', 'Bottinger-DEA_plus_DEAH')
LOADINGS = [0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
STOCKS = {'25 wt% (Lawson)': 17.50797101127487, '20 wt% (Boettinger 313.15 K)': 20.691238467870306}


def law(point, name):
    return next(r['correlation'] for g in point['reactions'].values() for r in g if r['name'] == name)


def k_ij(point, a, b):
    p = next(p for p in point['parameters']['pairs'] if {p['component_id_a'], p['component_id_b']} == {a, b})
    return next(c['value'] for c in p['coefficients'] if c['family'] == 'k_ij')


def scale_carbamate(point, factor):
    c = next(c for c in point['parameters']['components'] if c['component_id'] == 'carbamate-anion')
    for item in c['coefficients']:
        if item['family'] in ('segment_diameter', 'born_diameter', 'debye_huckel_diameter', 'packing_diameter'):
            item['value']['magnitude'] *= factor


# name, step, edit; DEA-specific first, then shared contrasts.
PERTURBATIONS = [
    ('ln K carbamate hydrolysis (a)', 0.1, lambda p: law(p, 'carbamate-hydrolysis').__setitem__('a', law(p, 'carbamate-hydrolysis')['a']+0.1)),
    ('ln K DEA dissociation (a)', 0.1, lambda p: law(p, 'DEA-dissociation').__setitem__('a', law(p, 'DEA-dissociation')['a']+0.1)),
    ('k_ij protonated DEA-water', 0.01, lambda p: k_ij(p, 'protonated-diethanolamine', 'water').__setitem__('magnitude', k_ij(p, 'protonated-diethanolamine', 'water')['magnitude']+0.01)),
    ('k_ij carbamate-water', 0.01, lambda p: k_ij(p, 'carbamate-anion', 'water').__setitem__('magnitude', k_ij(p, 'carbamate-anion', 'water')['magnitude']+0.01)),
    ('k_ij DEA-water', 0.01, lambda p: k_ij(p, 'diethanolamine', 'water').__setitem__('magnitude', k_ij(p, 'diethanolamine', 'water')['magnitude']+0.01)),
    ('k_ij DEA-CO2 (fixed at 0)', 0.01, lambda p: k_ij(p, 'diethanolamine', 'carbon-dioxide').__setitem__('magnitude', k_ij(p, 'diethanolamine', 'carbon-dioxide')['magnitude']+0.01)),
    ('carbamate diameters x1.01', 0.01, lambda p: scale_carbamate(p, 1.01)),
    ('shared k_ij bicarbonate-water', 0.01, lambda p: k_ij(p, 'bicarbonate-anion', 'water').__setitem__('magnitude', k_ij(p, 'bicarbonate-anion', 'water')['magnitude']+0.01)),
    ('shared k_ij CO2-water', 0.01, lambda p: k_ij(p, 'carbon-dioxide', 'water').__setitem__('magnitude', k_ij(p, 'carbon-dioxide', 'water')['magnitude']+0.01)),
]


def speciation(r, point):
    spec = r.bind(point)
    out = []
    for stock, water in STOCKS.items():
        for alpha in LOADINGS:
            res = eq.solve_equilibrium(spec.model, spec.problem('loaded-bubble', dict(T=313.15, P=1e4, water=water, alpha=alpha)))
            assert res.requested_tolerance_met, (stock, alpha, res.message)
            x = dict(zip(SPECIES, res.mole_fractions[:9]))
            acts = eq.reaction_activities(spec.model, res)
            liquid = next(a for a in acts if a.phase_index == 0 and a.basis.startswith('common-molality'))
            a = dict(zip(SPECIES, liquid.species.activities))
            m = {s: x[s]/(x['water']*M_W) for s in SPECIES if s != 'water'}
            gamma = {s: a[s]/m[s] for s in m}
            hyd, dis = law(point, 'carbamate-hydrolysis'), law(point, 'DEA-dissociation')
            lnK = lambda c: c['a']+c['b']/313.15+c['d']*313.15
            q_ideal = math.log(m['diethanolamine']*m['bicarbonate-anion']/m['carbamate-anion'])
            out.append(dict(stock=stock, alpha=alpha, p_CO2_Pa=res.pressure*res.mole_fractions[9], x=x, gamma=gamma, a_water=a['water'],
                            hydrolysis=dict(lnK=lnK(hyd), ln_Q_ideal_molality=q_ideal, ln_activity_term=lnK(hyd)-q_ideal),
                            dissociation_ln_activity_term=lnK(dis)-math.log(m['diethanolamine']*m['hydronium-cation']/m['protonated-diethanolamine']),
                            carbon_split={s: x[s]/sum(x[c] for c in ('carbon-dioxide', 'carbamate-anion', 'bicarbonate-anion', 'carbonate-anion'))
                                          for s in ('carbon-dioxide', 'carbamate-anion', 'bicarbonate-anion', 'carbonate-anion')}))
    return out


def bottinger_quotient():
    """Apparent mole-fraction hydrolysis quotient x_DEA x_HCO3 / x_DEACOO from Boettinger Table 4,
    free DEA by charge balance (DEAH+ = HCO3- + DEACOO-; CO3^2- and OH- neglected)."""
    rows = list(csv.DictReader(open(AN.parents[1]/'data/reference/DEA/Bottinger2008_Table4_DEA_NMR.csv')))
    out = []
    for r in rows:
        total, c, b = (float(r[k]) for k in ('x_DEA_plus_DEAH', 'x_DEACOO', 'x_HCO3'))
        free = total-c-b
        out.append(dict(T_K=float(r['T_K']), alpha=float(r['alpha_mol_CO2_per_mol_DEA']), x_free_DEA_charge_balance=free,
                        ln_Q_x=math.log(free*b/c) if free > 0 and b > 0 and c > 0 else None))
    return out


def predictions(r, point):
    spec = r.bind(point)
    rows = [rec for role in ('fitted', 'comparisons') for rec in spec.inputs['observations'][role] if rec['group'] in PRESSURE+SPECIATION]
    out = []
    for rec in rows:
        p = spec.prediction(rec)
        assert p['status'] == 'Available', (rec['identity'], p.get('message'))
        out.append(dict(identity=rec['identity'], group=rec['group'], role=rec['role'], T_K=spec.problems[rec['problem']].T,
                        alpha=float(rec['row'].get('alpha_mol_CO2_per_mol_DEA', 'nan')), observed=p['observed'], value=p['value']))
    return out


def reduce(base, sens, select, transform):
    """RMS of residual r, after the best offset, after the best single parameter, and after offset plus parameter (linearized)."""
    idx = [i for i, b in enumerate(base) if select(b)]
    r = np.array([transform(base[i]['observed'])-transform(base[i]['value']) for i in idx])
    rms = lambda v: float(np.sqrt(np.mean(v**2)))
    out = dict(rows=len(idx), rms=rms(r), rms_after_offset=rms(r-r.mean()), parameters={})
    for name, s in sens.items():
        s = np.array([s[i] for i in idx])
        if not np.any(s):
            continue
        d1 = float(s@r/(s@s))
        A = np.column_stack([np.ones_like(s), s])
        c = np.linalg.lstsq(A, r, rcond=None)[0]
        out['parameters'][name] = dict(step_alone=d1, rms_alone=rms(r-d1*s), step_with_offset=float(c[1]), rms_with_offset=rms(r-A@c))
    return out


def main(out):
    r = route(out)
    point = endpoint(out)
    base = predictions(r, point)
    retained = {row['identity']: float(row['predicted']) for row in csv.DictReader(open(AN/'results/retransfer-398/paper-data.csv')) if row['model'] == '05e94210'}
    replay = max(abs(b['value']/retained[b['identity']]-1) for b in base if retained[b['identity']] != 0)
    assert replay < 1e-8, replay  # #346/#255 replay limit
    sens, ln_sens = {}, {}
    for name, step, edit in PERTURBATIONS:
        p = copy.deepcopy(point)
        edit(p)
        moved = predictions(r, p)
        ln_sens[name] = [(math.log(m['value'])-math.log(b['value']))/step if b['group'] in PRESSURE else 0.0 for b, m in zip(base, moved, strict=True)]
        sens[name] = [(m['value']-b['value'])/step if b['group'] in SPECIATION else 0.0 for b, m in zip(base, moved, strict=True)]
        print(name, 'done', flush=True)
    log, x = (lambda v: math.log(v)), (lambda v: v)
    analysis = {
        'ln p, 310.9-313.15 K (Lawson, Seo-Hong, Lal)': reduce(base, ln_sens, lambda b: b['group'] in PRESSURE and b['T_K'] < 315, log),
        'ln p, all 97 pressure rows': reduce(base, ln_sens, lambda b: b['group'] in PRESSURE, log),
        'ln p, Lal 313.15 K': reduce(base, ln_sens, lambda b: b['group'] == 'Lal' and b['T_K'] < 315, log),
        'carbamate mole fraction, Boettinger 313.15 K': reduce(base, sens, lambda b: b['group'] == 'Bottinger-DEACOO' and abs(b['T_K']-313.15) < 0.1, x),
        'bicarbonate mole fraction, Boettinger 313.15 K': reduce(base, sens, lambda b: b['group'] == 'Bottinger-HCO3' and abs(b['T_K']-313.15) < 0.1, x),
    }
    profile = speciation(r, point)
    save('diagnosis-410/pressure-shape.json', dict(replay_max_relative_difference=replay, perturbations=[(n, s) for n, s, _ in PERTURBATIONS],
                                                   residual_reduction=analysis, speciation_313K=profile, bottinger_quotient=bottinger_quotient(),
                                                   rows=base, ln_p_sensitivity=ln_sens, speciation_sensitivity=sens))
    for k, v in analysis.items():
        print(f"\n{k}: rows {v['rows']} rms {v['rms']:.4f} after offset {v['rms_after_offset']:.4f}")
        for n, s in v['parameters'].items():
            print(f"  {n:34s} alone {s['step_alone']:+9.3f} -> {s['rms_alone']:.4f}   with offset {s['step_with_offset']:+9.3f} -> {s['rms_with_offset']:.4f}")


if __name__ == '__main__':
    main(Path(sys.argv[1]))
