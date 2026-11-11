"""Render only retained pressure values; never invoke the thermodynamic model."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AN = Path(__file__).resolve().parent


def read(name):
    with (AN / 'results' / name).open() as stream:
        return [{k: float(v) if k not in ('solver_status', 'classification') else v for k, v in r.items()}
                for r in csv.DictReader(stream)]


rows, curve, extra = (read(p) for p in ('pressure-residuals.csv', 'liquid-curve.csv', 'extrapolation.csv'))
fig, axes = plt.subplots(2, 1, figsize=(7, 6.5), sharex=True, layout='constrained')
a, b = axes
for key, label, color, style in [('model_kPa', 'Frozen Razavi PC-SAFT', '#0072B2', '-'),
                                  ('hartono_kPa', 'Hartono supporting correlation', '#D55E00', '--')]:
    a.plot([r['T_K'] for r in curve], [r[key] for r in curve], style, color=color, label=label)
a.errorbar([r['T_K'] for r in rows], [r['observed_kPa'] for r in rows],
           yerr=[r['sigma_kPa'] for r in rows], fmt='o', color='black', capsize=3,
           label='Steele liquid measurements ± propagated error')
a.set(ylabel='Saturation pressure (kPa)', title='Frozen pure-PZ pressure exceeds Steele measurements')
a.legend(fontsize=8)
b.plot([r['T_K'] for r in rows], [r['residual_sigma'] for r in rows], 'o', color='#0072B2')
b.axhline(0, color='black', linewidth=.7)
b.set(xlabel='Temperature (K)', ylabel='(Model − measured) / source error', title='Every discrepancy greatly exceeds the printed source error')
fig.savefig(AN / 'figures/liquid-pressure.png', dpi=180)
plt.close(fig)
fig, a = plt.subplots(figsize=(7, 3.5), layout='constrained')
for subcooled, style, label in [(True, '--', 'Subcooled-liquid extrapolation'), (False, '-', 'Liquid extrapolation below measured span')]:
    selected = [r for r in extra if (r['T_K'] <= 384.6 if subcooled else r['T_K'] >= 384.6)]
    a.semilogy([r['T_K'] for r in selected], [r['model_kPa'] for r in selected], style, color='#0072B2', label=label)
a.axvline(384.6, color='black', linewidth=.7)
a.set(xlabel='Temperature (K)', ylabel='Pure-liquid pressure (kPa)', title='Extrapolated branch: no pure-liquid physical validation below 418 K')
a.legend(fontsize=8)
fig.savefig(AN / 'figures/extrapolation.png', dpi=180)
plt.close(fig)
lines = ['| T (K) | Steele (kPa) | Error scale (kPa) | Frozen model (kPa) | Difference (kPa) | Relative error (%) | Difference / error scale |',
         '|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
    lines.append('| ' + ' | '.join(f'{r[k]:.6g}' for k in ('T_K', 'observed_kPa', 'sigma_kPa', 'model_kPa', 'difference_kPa', 'relative_percent', 'residual_sigma')) + ' |')
lines += ['', 'Supporting correlation, evaluated only over the measured liquid span:', '',
          '| T (K) | Hartono (kPa) | Hartono − Steele (kPa) | Relative difference (%) |', '|---:|---:|---:|---:|']
for r in rows:
    d = r['hartono_kPa'] - r['observed_kPa']
    lines.append(f"| {r['T_K']:.3f} | {r['hartono_kPa']:.6g} | {d:.6g} | {100*d/r['observed_kPa']:.6g} |")
(AN / 'results/tables.md').write_text('\n'.join(lines)+'\n')

# Current owner-authorized energy-only refit; the frozen comparison remains retained above.
fit = json.loads((AN / 'results/refit-fits.json').read_text())
rr, rc, re = (read(p) for p in ('refit-residuals.csv', 'refit-liquid-curve.csv', 'refit-extrapolation.csv'))
fig, axes = plt.subplots(2, 2, figsize=(10, 7), layout='constrained')
a, b, c, d = axes.flat
for key, label, color, style in [('razavi_kPa', 'Razavi', '#0072B2', '--'), ('p_kPa', 'Energy refit', '#009E73', '-')]:
    a.plot([r['T_K'] for r in rc], [r[key] for r in rc], style, color=color, label=label)
    c.semilogy([r['T_K'] for r in re], [r[key] for r in re], style, color=color, label=label)
a.plot([r['T_K'] for r in curve], [r['hartono_kPa'] for r in curve], ':', color='#D55E00', label='Hartono (supporting)')
a.errorbar([r['T_K'] for r in rr], [r['observed_kPa'] for r in rr], yerr=[r['sigma_kPa'] for r in rr], fmt='o', color='black', label='Steele ± propagated error')
a.set(xlabel='Temperature (K)', ylabel='Saturation pressure (kPa)', title='Energy refit removes the pressure bias')
a.legend(fontsize=8)
b.axhspan(-1, 1, color='gray', alpha=.15, label='± source error')
b.plot([r['T_K'] for r in rr], [r['residual_sigma'] for r in rr], 'o', color='#009E73')
b.axhline(0, color='black', linewidth=.7)
b.set(xlabel='Temperature (K)', ylabel='(Refit − Steele) / source error', title='Three points outside the printed scale')
b.legend(fontsize=8)
c.axvline(384.6, color='black', linewidth=.7)
c.set(xlabel='Temperature (K)', ylabel='Pure-liquid pressure (kPa)', title='Below 384.6 K: subcooled extrapolation')
c.legend(fontsize=8)
d.plot([r['T_K'] for r in re], [r['density_shift_percent'] for r in re], color='#009E73')
d.plot([r['T_K'] for r in rc], [r['density_shift_percent'] for r in rc], color='#009E73')
d.set(xlabel='Temperature (K)', ylabel='Liquid density change from Razavi (%)', title='Density shifts; no pure-liquid validation')
fig.savefig(AN / 'figures/energy-refit.png', dpi=180)
plt.close(fig)
lines = ['| T (K) | Refit (kPa) | Difference (kPa) | Relative error (%) | Residual / source error | Beyond ± source error (kPa) |', '|---:|---:|---:|---:|---:|---:|']
for r in rr:
    lines.append('| '+' | '.join(f'{r[k]:.7g}' for k in ('T_K','p_kPa','difference_kPa','relative_percent','residual_sigma','outside_source_scale_kPa'))+' |')
lines += ['', 'Subset comparison (all start from Razavi; the three-parameter continuation is also retained):', '', '| Fitted coordinates | Sum of squared source-scale residuals | Status |', '|---|---:|---|']
for f in [*fit['fits'], fit['selected']]:
    lines.append(f"| {', '.join(f['names'])} | {f['sum_squared_source_residuals']:.7g} | {f['status']} |")
(AN / 'results/refit-tables.md').write_text('\n'.join(lines)+'\n')
