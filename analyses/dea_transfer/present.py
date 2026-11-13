"""#317 figure from retained rows only (no Engine call): measured CO2 pressures and heats against the frozen selected predictions."""
import csv, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pinned import AN

plt.rcParams['svg.hashsalt'] = 'dea317'
read = lambda p: json.loads((AN / p).read_text())
run = read('results/selection.json')['run']
score = read('results/score.json')
fit = read(f'results/fit-runs/{run}-replay.json')
rows = []
for set_name, preds, key, alpha in (('Lawson 1976 (fitted, 25 wt%)', [p for p in fit if p['group'] == 'Lawson'], 'T_F', 'alpha_mol_CO2_per_mol_DEA'),
                                    ('Seo & Hong 1996 (held out, 30 wt%)', score['SeoHong']['table'], 'T_C', 'alpha_mol_CO2_per_mol_amine'),
                                    ('Lal 1985 (held out, 2.0 kmol/m³)', score['Lal']['table'], 'T_C', 'alpha_mol_CO2_per_mol_DEA')):
    for p in preds:
        T = float(p['row'][key])
        rows.append(dict(set=set_name, T_label=f"{p['row'][key]} °{key[-1]}", T_K=(T - 32) / 1.8 + 273.15 if key == 'T_F' else T + 273.15,
                         alpha=float(p['row'][alpha]), observed=p['observed'] / 1e3, predicted=p['value'] / 1e3, unit='kPa'))
for p in fit:
    if p['group'] == 'Carson':
        rows.append(dict(set='Carson 2000 (fitted, 298.15 K)', T_label=f"w = {p['row']['DEA_mass_fraction']}", T_K=298.15,
                         alpha=float(p['row']['x_CO2']), observed=-p['observed'] / 1e3, predicted=-p['value'] / 1e3, unit='kJ/mol'))
with (AN / 'results/figure-values.csv').open('w') as f:
    writer = csv.DictWriter(f, list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
fig, axes = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9']
for ax, name in zip(axes.flat, dict.fromkeys(r['set'] for r in rows)):
    group = [r for r in rows if r['set'] == name]
    for color, label in zip(colors, dict.fromkeys(r['T_label'] for r in group)):
        g = sorted((r for r in group if r['T_label'] == label), key=lambda r: r['alpha'])
        ax.plot([r['alpha'] for r in g], [r['observed'] for r in g], 'o', mfc='none', color=color, label=f'{label} measured')
        ax.plot([r['alpha'] for r in g], [r['predicted'] for r in g], 'x', color=color, label=f'{label} model')
    heat = group[0]['unit'] == 'kJ/mol'
    ax.set(title=name, xlabel='CO₂ mole fraction x₁' if heat else 'Loading α (mol CO₂/mol DEA)',
           ylabel='Integral heat of solution −ΔH (kJ/mol CO₂)' if heat else 'CO₂ partial pressure (kPa)', yscale='linear' if heat else 'log')
    ax.legend(fontsize=7, ncol=2)
fig.savefig(AN / 'results/measured-vs-model.png', dpi=170)
