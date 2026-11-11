"""Render only retained pressure values; never invoke the thermodynamic model."""
import csv
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
