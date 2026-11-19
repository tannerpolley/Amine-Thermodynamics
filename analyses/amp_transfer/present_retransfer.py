"""Plot the retained AMP measurements and homogeneous model curves."""
import csv
import json
from pathlib import Path
import sys

from matplotlib.figure import Figure

AN = Path(__file__).resolve().parent
OUT = AN / 'results/retransfer-344-05e94210'
title = 'AMP on the adopted shared inputs'
if sys.argv[1:]:
    assert sys.argv[1:] == ['sensitivity-3.5']
    OUT /= 'sensitivity-3.5'
    title = 'AMP with a 3.5 Å carbamate diameter floor'
with (AN / 'inputs/retransfer-344/observation-rows.csv').open() as stream:
    inputs = {row['identity']: row for row in csv.DictReader(stream)}
rows = json.loads((OUT / 'data-rows.json').read_text())
curves = json.loads((OUT / 'curve-data.json').read_text())
panels = sorted({(r['curve'].split('|')[0], float(r['curve'].split('|')[2])) for r in curves})
colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#8C510A']
shown = set()
fig = Figure(figsize=(15, 13), constrained_layout=True)
axes = fig.subplots(3, 3)
for ax, (dataset, water) in zip(axes.flat, panels):
    series = sorted({r['curve'] for r in curves if r['curve'].split('|')[0] == dataset
                     and float(r['curve'].split('|')[2]) == water})
    for color, name in zip(colors, series):
        line = sorted([r for r in curves if r['curve'] == name], key=lambda r: r['loading'])
        T, unit = line[0]['T_K'], line[0]['unit']
        outside = any(v is True for v in line[0]['outside_ranges'].values())
        factor = 1000 if unit == 'Pa' else 1
        measured = [r for r in rows if inputs[r['identity']]['dataset'] == dataset and r['T_K'] == T
                    and abs(float(inputs[r['identity']]['water'])-water) < 1e-8]
        assert measured, name
        shown.update(r['identity'] for r in measured)
        ax.plot([r['loading'] for r in line], [r['value']/factor if r['status'] == 'Available' else float('nan') for r in line],
                color=color, ls='--' if outside else '-', label=f'{T:g} K'+(' outside range' if outside else ''))
        ax.scatter([float(inputs[r['identity']]['alpha']) for r in measured],
                   [r['observed']/factor for r in measured], marker='D' if outside else 'o',
                   facecolors='none', edgecolors=color, s=23)
    ax.set(title=f"{dataset} ({measured[0]['role']})\nwater/AMP = {water:.4g} mol/mol",
           xlabel='Loading / mol CO₂ per mol AMP',
           ylabel=('CO₂ partial pressure / kPa' if dataset == 'kundu-2003' else 'Total pressure / kPa')
                  if unit == 'Pa' else 'Carbamate / analytical AMP')
    if unit == 'Pa':
        ax.set_yscale('log')
    ax.grid(alpha=.2)
    ax.legend(fontsize=7)
for ax in list(axes.flat)[len(panels):]:
    ax.set_visible(False)
assert shown == {k for k, r in inputs.items() if r['reactive'] == 'True'}
fig.suptitle(title+'\nMeasured observations and homogeneous model curves\nDashed lines / diamonds: outside an applicable source range; uncertainty bands not shown')
fig.savefig(OUT / 'measured-model.png', dpi=160)
