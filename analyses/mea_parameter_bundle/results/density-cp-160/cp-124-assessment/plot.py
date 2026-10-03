"""Render the retained #124 water property errors; no model calculation."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader((HERE/'water.csv').open()))
fig, axes = plt.subplots(1, 3, figsize=(12, 3.7), layout='constrained')
quantities = [('cp', 'Liquid Cp error (%)'),
              ('saturated_liquid_rho', 'Saturated liquid density error (%)'),
              ('psat', 'Saturation pressure error (%)')]
for ax, (quantity, ylabel) in zip(axes, quantities):
    for record, color, marker in [('original', '#0072B2', 'x'), ('adopted', '#D55E00', 'o')]:
        selected = [r for r in rows if r['record']==record and r['grid']!='atmospheric-controls']
        ax.scatter([float(r['T_K']) for r in selected],
                   [100*float(r[quantity+'_error_relative']) for r in selected],
                   color=color, marker=marker, s=20, linewidths=.8, label=record.capitalize())
    ax.axhline(0, color='#555555', linewidth=.7)
    ax.set(xlabel='Temperature (K)', ylabel=ylabel)
    ax.grid(alpha=.2)
axes[0].axhline(3, color='#555555', linestyle='--', linewidth=.8)
axes[0].axhline(-3, color='#555555', linestyle='--', linewidth=.8)
axes[0].set_title('Adopted Cp meets the 3% limit')
axes[1].set_title('Mean |density error| increases')
axes[2].set_title('Mean |pressure error| decreases')
axes[0].legend(loc='lower right', frameon=False)
fig.savefig(HERE/'water-deviations.svg', metadata={'Date': None})
fig.savefig('/tmp/cp-124-water-deviations.png', dpi=140)
