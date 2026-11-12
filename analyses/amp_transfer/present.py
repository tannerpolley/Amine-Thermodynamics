"""Plot retained AMP calibration pressures; no Engine calculation."""
import csv, gzip, json
from pathlib import Path
import matplotlib.pyplot as plt

AN = Path(__file__).resolve().parent
OUT = AN / 'results/redesign'
plt.rcParams['svg.hashsalt'] = 'amp243'
summary = json.loads((OUT / 'summary.json').read_text())
rows, selected = [], {}
for setting in (1, 2):
    candidates = {r: v for r, v in summary['runs'].items() if v.get('setting') == setting and 'cost' in v}
    if not candidates:
        continue
    run = min(candidates, key=lambda r: candidates[r]['cost'])
    selected[setting] = run
    path = AN / candidates[run].get('reused_from', f'results/redesign/{run}-fit.json')
    if not path.exists():
        path = path.with_suffix(path.suffix + '.gz')
    data = json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())
    for p in data['replay']:
        if p['group'] == 'loaded-pressure':
            source = p['row']
            rows.append(dict(run=run, setting=setting, identity=p['identity'], T_K=float(source['T_K']),
                alpha=float(source['alpha_mol_CO2_per_mol_AMP']), observed_kPa=p['observed']/1000,
                predicted_kPa=p['value']/1000, u_P_kPa=float(source['u_P_kPa']), u_alpha=float(source['u_alpha'])))
with (OUT / 'pressure-plot.csv').open('w') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); writer.writeheader(); writer.writerows(rows)
fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), constrained_layout=True)
for ax, T in zip(axes, (313, 333, 353)):
    for setting, color, marker in ((1, '#0072B2', 'x'), (2, '#D55E00', '+')):
        group = [r for r in rows if r['setting'] == setting and round(r['T_K']) == T]
        if not group:
            continue
        if setting == min(selected):
            ax.errorbar([r['alpha'] for r in group], [r['observed_kPa'] for r in group],
                xerr=[r['u_alpha'] for r in group], yerr=[r['u_P_kPa'] for r in group], fmt='o',
                mfc='none', color='black', ms=4, lw=.6, label='Hartono 2021')
        ax.scatter([r['alpha'] for r in group], [r['predicted_kPa'] for r in group], marker=marker,
            color=color, s=30, label=f'Fitted set {setting}')
    ax.set(title=f'{T} K', xlabel='Loading / mol CO₂ per mol AMP', ylabel='Total pressure / kPa', yscale='log')
    ax.grid(alpha=.2); ax.legend(fontsize=8)
fig.suptitle('Lowest calibration cost in each fitted set; adoption checks apply separately', fontsize=11)
fig.savefig(OUT / 'pressure-comparison.svg', metadata={'Date': None})
plt.close(fig)
(OUT / 'plot-provenance.json').write_text(json.dumps(dict(summary='summary.json', diagnostic_candidates=selected,
    values='pressure-plot.csv', uncertainty='Hartono Table 7 reported u(P), u(alpha); coverage interpretation in source-admission.md',
    series='observations and fitted predictions at measured states, shown as discrete points'), indent=2)+'\n')

# #304: discrete held-out predictions and loading sensitivity, from retained values only.
KUNDU = AN / 'results/kundu'
if (KUNDU / 'current-pressures.csv').exists():
    with (KUNDU / 'current-pressures.csv').open() as f:
        rows = [{k: v if k == 'identity' else float(v) for k,v in r.items()} for r in csv.DictReader(f)]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
    for ax, stock in zip(axes, (2.0, 2.8, 3.4)):
        for T, color in ((303, '#0072B2'), (313, '#D55E00'), (323, '#009E73')):
            group = [r for r in rows if r['stock_mol_L']==stock and r['T_K']==T]
            if not group:
                continue
            alpha = [r['alpha'] for r in group]
            predicted = [r['predicted_Pa']/1000 for r in group]
            ax.scatter(alpha, [r['observed_Pa']/1000 for r in group], facecolors='none', edgecolors=color, marker='o', s=30, label=f'{T} K measured')
            ax.errorbar(alpha, predicted,
                yerr=[[r['predicted_Pa']/1000-min(r['low_alpha_Pa'], r['high_alpha_Pa'])/1000 for r in group],
                      [max(r['low_alpha_Pa'], r['high_alpha_Pa'])/1000-r['predicted_Pa']/1000 for r in group]],
                fmt='x', color=color, ms=5, lw=.7, label=f'{T} K predicted, α ±2%')
        ax.set(title=f'{stock:.1f} mol/L stock', xlabel='Loading / mol CO₂ per mol AMP', ylabel='CO₂ partial pressure / kPa', yscale='log')
        ax.grid(alpha=.2); ax.legend(fontsize=7)
    fig.suptitle('Frozen AMP working fit with current shared species: held-out mean error 21.89%')
    fig.savefig(KUNDU / 'pressure-comparison.svg', metadata={'Date': None})
    plt.close(fig)
