import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path(__file__).resolve().parents[1]/'results/refit-298'
scores=json.loads((out/'pressure-scores.json').read_text())
selection=json.loads((out/'selection.json').read_text())
rows=[]
for label in ('A3','B1'):
 for group in ('Xiao','Ermatchkov'):
  rows.append(dict(record=label,source=group,rebased_baseline_AARD_percent=scores[label+'-baseline-278'][group]['AARD_percent'],fixed_substitution_AARD_percent=scores[label+'-substitution-278'][group]['AARD_percent'],refit_AARD_percent=scores[selection[label]['name']][group]['AARD_percent']))
with (out/'pressure-comparison.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
fig,ax=plt.subplots(figsize=(8,3.6),layout='constrained')
for y,row in enumerate(rows):
 ax.plot(row['rebased_baseline_AARD_percent'],y+.18,'o',color='#0072B2',label='Historical shared values' if y==0 else None)
 ax.plot(row['fixed_substitution_AARD_percent'],y,'s',color='#009E73',label='Fixed substitution' if y==0 else None)
 ax.plot(row['refit_AARD_percent'],y-.18,'x',color='#D55E00',markersize=8,label='Selected refit' if y==0 else None)
ax.set(yticks=range(4),yticklabels=[r['record']+' · '+r['source'] for r in rows],xlabel='CO₂ partial-pressure AARD (%)',xlim=(0,65),title='B1 recovers both pressure baselines; A3 does not')
ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.legend(loc='lower right',frameon=False)
fig.savefig(out/'pressure-comparison.png',dpi=170)
