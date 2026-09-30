"""Render retained Matin associations without evaluating an Engine model."""
import time
STARTED=time.perf_counter()
import csv
import json
from pathlib import Path
import os
os.environ['MPLCONFIGDIR']=str(Path(__file__).resolve().parent/'matplotlib-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader((HERE/'p1-matin-associations.csv').open()))
stats=list(csv.DictReader((HERE/'p1-rank-correlations.csv').open()))
species=('HCO3-','MEA','MEACOO-','MEAH+')
labels={'HCO3-':'HCO₃⁻ + CO₃²⁻ pool','MEA':'Free MEA','MEACOO-':'MEACOO⁻','MEAH+':'MEAH⁺'}
fig,axes=plt.subplots(4,2,figsize=(11,13))
for i,name in enumerate(species):
    sub=[r for r in rows if r['species']==name]
    for j,path in enumerate(('difference','common_difference')):
        ax=axes[i,j]
        for fit,marker in [('True','o'),('False','s')]:
            selected=[r for r in sub if r['in_fitted_objective']==fit]
            ax.scatter([float(r[f'water_born_ln_activity_{path}']) for r in selected],
                       [float(r['weighted_residual_difference']) for r in selected],
                       marker=marker,s=35,facecolors='#0072B2' if fit=='True' else 'none',edgecolors='#0072B2')
        statistic=next(r for r in stats if r['species']==name and r['path']==path and r['population']=='fitted-only')
        prefix=('Own solved compositions\n' if j==0 else 'Common (0,0) compositions\n') if i==0 else ''
        ax.set_title(prefix+labels[name]+f"\nfitted n={statistic['n']}; Spearman ρ={float(statistic['spearman_rho']):+.3f}",fontsize=10)
        ax.axhline(0,color='#777777',linewidth=.7)
        ax.set_xlabel('Born ln a_water, (1,1) − (0,0)\n[dimensionless]')
        ax.set_ylabel('Δ weighted residual\n[dimensionless]')
        ax.grid(alpha=.2)
fig.suptitle('Matin 20 °C: descriptive association, not causal attribution\nFilled circles: fitted states; open square: excluded state',fontsize=13)
fig.tight_layout(rect=(0,0,1,.94),h_pad=2.,w_pad=2.)
for extension in ('png','svg'):
    fig.savefig(HERE/f'matin-water-activity-association.{extension}',dpi=160)
plt.close(fig)
ledger=HERE/'job-times.json';jobs=json.loads(ledger.read_text())
jobs.append({'job':'render-association','wall_s':time.perf_counter()-STARTED,'status':'complete'})
ledger.write_text(json.dumps(jobs,indent=2)+'\n')
