"""#410 figure from retained probe values only (no Engine call)."""
import csv, json, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
AN = HERE.parent
plt.rcParams['svg.hashsalt'] = 'dea410'
he = json.loads((HERE/'excess-enthalpy.json').read_text())['cases']
ps = json.loads((HERE/'pressure-shape.json').read_text())
alpha = {r['identity']: float(r['alpha']) for name in ('lal-1985', 'lawson-1976', 'seo-hong-1996')
         for r in csv.DictReader((AN/f'inputs/{name}.csv').open())}
blue, orange, green, purple = '#0072B2', '#D55E00', '#009E73', '#CC79A7'
values = []
fig, ax = plt.subplots(2, 2, figsize=(6.8, 5.6), constrained_layout=True)

a = ax[0, 0]
base, slope = he[0], next(c for c in he if 'linear estimate' in c['case'])
x = [r['x_water'] for r in base['rows']]
a.plot(x, [r['observed_HE'] for r in base['rows']], 'o', mfc='none', color='k', label='Horstmann 2002, 363.15 K')
a.plot(x, [r['HE'] for r in base['rows']], 'x', color=blue, label='Selected model')
a.plot(x, [r['HE'] for r in slope['rows']], '+', color=orange, label=f"Probe: {slope['case'].split(' (')[0]}")
a.axhline(0, color='0.6', lw=0.6)
a.set(xlabel='Water mole fraction', ylabel='Excess enthalpy (J/mol)', title='(a) Water–DEA excess enthalpy')
a.legend(fontsize=6.5)
for c, rows in (('selected', base['rows']), ('slope probe', slope['rows'])):
    values += [dict(panel='a', series=c, x=r['x_water'], y=r['HE'], observed=r['observed_HE'], unit='J/mol mixture') for r in rows]

a = ax[0, 1]
for term, color, marker in (('hard_chain', green, 's'), ('dispersion', purple, '^'), ('association', blue, 'o')):
    y = [r['split'][term] for r in base['rows']]
    a.plot(x, y, marker, color=color, ms=4, label=term.replace('_', ' '))
    values += [dict(panel='b', series=term, x=xi, y=yi, observed='', unit='J/mol mixture') for xi, yi in zip(x, y)]
a.axhline(0, color='0.6', lw=0.6)
a.set(xlabel='Water mole fraction', ylabel='Term contribution (J/mol)', title='(b) Model, by Helmholtz term')
a.legend(fontsize=6.5)

a = ax[1, 0]
S = ps['ln_p_sensitivity']['ln K carbamate hydrolysis (a)']
for group, color, marker in (('Lal', blue, 'o'), ('Lawson', orange, 's'), ('SeoHong', green, '^')):
    pts = [(alpha[b['identity']], math.log(b['observed']/b['value']), S[i]) for i, b in enumerate(ps['rows'])
           if b['group'] == group and b['T_K'] < 315]
    a.plot([p[0] for p in pts], [p[1] for p in pts], marker, color=color, ms=4, label=f'{group}')
    a.plot([p[0] for p in pts], [p[1]-0.9*p[2] for p in pts], marker, mfc='none', color=color, ms=4, label=f'{group}, ln K$_{{hyd}}$+0.9')
    values += [dict(panel='c', series=f'{group} {s}', x=p[0], y=y, observed='', unit='ln(observed/model)')
               for p in pts for s, y in (('selected', p[1]), ('lnK+0.9 linear', p[1]-0.9*p[2]))]
a.axhline(0, color='0.6', lw=0.6)
a.set(xlabel='Loading (mol CO₂/mol DEA)', ylabel='ln(measured / model) CO₂ pressure', title='(c) CO₂ pressure, 310.9–313.15 K', ylim=(-0.9, 2.0))
a.legend(fontsize=5, ncol=3, loc='upper center', handletextpad=0.2, columnspacing=0.6)

a = ax[1, 1]
prof = [s for s in ps['speciation_313K'] if s['stock'].startswith('20')]
meas = [r for r in csv.DictReader(open(AN.parents[1]/'data/reference/DEA/Bottinger2008_Table4_DEA_NMR.csv')) if r['T_K'] == '313.15']
for sp, col, color in (('carbamate-anion', 'x_DEACOO', blue), ('bicarbonate-anion', 'x_HCO3', orange)):
    a.plot([s['alpha'] for s in prof], [s['x'][sp] for s in prof], '-', color=color, label=f"{sp.split('-')[0]}, model")
    a.plot([float(r['alpha_mol_CO2_per_mol_DEA']) for r in meas], [float(r[col]) for r in meas], 'o', mfc='none', color=color, label=f"{sp.split('-')[0]}, Böttinger 2008")
    values += [dict(panel='d', series=f'{sp} model', x=s['alpha'], y=s['x'][sp], observed='', unit='mole fraction') for s in prof]
a.set(xlabel='Loading (mol CO₂/mol DEA)', ylabel='True mole fraction', title='(d) 20 wt% DEA, 313.15 K')
a.legend(fontsize=6)

fig.savefig(HERE/'diagnosis-410.png', dpi=200)
with (HERE/'figure-values.csv').open('w') as f:
    w = csv.DictWriter(f, list(values[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(values)
