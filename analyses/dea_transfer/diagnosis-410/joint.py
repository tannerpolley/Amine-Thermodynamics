"""#410: linearized joint analysis from retained pressure-shape.json (no Engine call).

Identifiability of the seven DEA-specific coordinates on the 29 rows at 310.9-313.15 K, joint
linearized residual reduction, and the fitted Lawson cost by isotherm when ln K_hydrolysis is raised.
"""
import json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
d = json.loads((HERE/'pressure-shape.json').read_text())
names = list(d['ln_p_sensitivity'])
idx = [i for i, b in enumerate(d['rows']) if b['group'] in ('Lawson', 'SeoHong', 'Lal') and b['T_K'] < 315]
r = np.array([math.log(d['rows'][i]['observed']/d['rows'][i]['value']) for i in idx])
S = np.array([[d['ln_p_sensitivity'][n][i] for n in names] for i in idx])
rms = lambda v: float(np.sqrt(np.mean(v**2)))
high = [k for k, i in enumerate(idx) if d['rows'][i]['group'] == 'Lawson' and d['rows'][i]['alpha'] >= 1.0]
out = dict(rows=len(idx), names=names[:7],
           unit_column_singular_values=np.linalg.svd(S[:, :7]/np.linalg.norm(S[:, :7], axis=0), compute_uv=False).tolist(), joint={})
for label, cols in (('carbamate hydrolysis + carbamate-water k_ij', [0, 3]), ('seven DEA-specific', list(range(7))),
                    ('seven DEA-specific + offset', list(range(7))+['offset'])):
    M = np.column_stack([np.ones(len(idx)) if c == 'offset' else S[:, c] for c in cols])
    c = np.linalg.lstsq(M, r, rcond=None)[0]
    res = r-M@c
    out['joint'][label] = dict(steps=dict(zip([names[k] if k != 'offset' else k for k in cols], c.tolist())), rms=rms(res),
                               residual_lawson_alpha_ge_1=res[high].tolist())
# Fitted Lawson cost (retained objective: 0.5 * weight * r^2, weight 4.1152 per row) by isotherm, linearized in ln K_hydrolysis.
s = d['ln_p_sensitivity']['ln K carbamate hydrolysis (a)']
weight = 4.11522633744856
cost = {}
for i, b in enumerate(d['rows']):
    if b['group'] == 'Lawson':
        r0 = math.log(b['observed']/b['value'])
        t = cost.setdefault(f"{b['T_K']:.2f}", dict(rows=0, cost={'0.0': 0.0, '0.5': 0.0, '0.9': 0.0}))
        t['rows'] += 1
        for shift in t['cost']:
            t['cost'][shift] += 0.5*weight*(r0-float(shift)*s[i])**2
out['lawson_cost_by_isotherm_linearized'] = cost
(HERE/'joint-reduction.json').write_text(json.dumps(out, indent=1)+'\n')
print(json.dumps(out, indent=1))
