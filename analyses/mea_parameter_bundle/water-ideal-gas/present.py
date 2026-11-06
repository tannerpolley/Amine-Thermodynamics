"""Present retained water fit and fixed-parameter uncertainty comparisons."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
rows = json.loads((HERE/'comparison.json').read_text())
heat = {r['record_id']: r for r in json.loads((ROOT/'analyses/mea_parameter_bundle/data/input/fit-campaigns/heat-rows.json').read_text())}
with (ROOT/'data/reference/MEA/observations/calorimetry/Kim_2007_calorimetry_30wt.csv').open() as f:
    kim = {r['record_id']: r for r in csv.DictReader(f)}
ratios = []
for r in rows:
    if r['difference'] is None:
        continue
    if r['group'] == 'integral heat':
        source = heat[r['identity']]
        scale = source['uH_J_per_mol_CO2']
        basis = 'reported heat uncertainty' if r['identity'].startswith('10.') else 'printed Table 4 uncertainty'
    elif r['group'] == 'Kim finite addition':
        source = kim[r['identity']]
        scale = float(source['heat_uncertainty_relative_percent_reported'])/100 * abs(float(source['dHdiff_kJ_per_mol_CO2_reported']))
        basis = 'reported relative molar heat uncertainty'
    else:
        continue
    ratios.append(dict(identity=r['identity'], group=r['group'], difference=r['difference'], unit=r['unit'],
                       uncertainty=scale, uncertainty_basis=basis, ratio=abs(r['difference'])/scale))
(HERE/'uncertainty-comparison.json').write_text(json.dumps(ratios, indent=2)+'\n')
with (HERE/'verification-grid.csv').open() as f:
    grid = list(csv.DictReader(f))
T = np.array([float(r['T_K']) for r in grid])
ref = np.array([float(r['iapws_cp_J_mol_K']) for r in grid])
fitted = np.array([float(r['fit_cp_J_mol_K']) for r in grid])
a,b,c,d,e = json.loads((HERE/'old-water.json').read_text())['coefficients'][:5]
t = T/1000
old = a+b*t+c*t**2+d*t**3+e/t**2
fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.5), constrained_layout=True)
for ax, values, title, color in zip(axes, (old, fitted), ('Old extrapolated record', 'IAPWS-based fit'), ('#D55E00', '#0072B2')):
    ax.plot(T, 100*(values/ref-1), color=color, lw=1.7)
    ax.axhline(0, color='black', lw=.7)
    ax.set(title=title, xlabel='Temperature (K)', ylabel='Relative $c_p^\\circ$ error (%)')
fig.savefig(HERE/'cp-error.png', dpi=180, metadata={'Software': 'matplotlib'})
plt.close(fig)
for group in ('integral heat', 'Kim finite addition'):
    print(group, max(r['ratio'] for r in ratios if r['group']==group))
