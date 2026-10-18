"""Presentation only: relative CO2 Henry-constant error at the released neutral pair, from retained evaluation.json."""
import csv, json, sys
from pathlib import Path
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]/'scripts')); from manuscript_style import apply_style; apply_style()
rows = list(csv.DictReader(open(HERE.parents[5]/'data/reference/MEA/physical_solubility/CO2_physical_from_N2O.csv')))
error = json.load(open(HERE/'A/evaluation.json'))['endpoint']['larger-dV']['relative_H_error']
fig, ax = plt.subplots(figsize=(5.2, 3.4))
ax.axhspan(-10, 10, color='0.92', zorder=0); ax.axhline(0, color='0.4', lw=0.8)
ax.plot([float(r['temperature_K']) for r in rows[:7]], [100*e for e in error[:7]], 'o', mfc='none', mec='k', ms=6, label='Hartono 2014, 30 wt % (fitted)')
for w, m in zip(sorted({r['mea_mass_fraction'] for r in rows[7:]}), ('s', '^', 'D', 'v')):
    sel = [(float(r['temperature_K']), 100*e) for r, e in zip(rows[7:], error[7:]) if r['mea_mass_fraction'] == w]
    ax.plot(*zip(*sel), m, ms=5, label=f'Xu & Wang 2018, {100*float(w):.0f} wt % (comparison)')
ax.set_xlabel('Temperature / K'); ax.set_ylabel('Model / target − 1 for $H_{CO_2}$ / %')
ax.legend(fontsize=7, frameon=False, loc='lower right'); fig.tight_layout()
fig.savefig(HERE/'neutral-henry-errors.svg'); print('written')
