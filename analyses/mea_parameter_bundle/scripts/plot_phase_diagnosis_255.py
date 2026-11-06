"""Read retained fixed probes; show calibration cost versus water interaction."""
import csv
import re
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path('analyses/mea_parameter_bundle/results/phase-diagnosis-255')
rows=list(csv.DictReader((OUT/'probes.csv').open()))
fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
for ax,base,title in zip(axes,('wide','final'),('Wider-bound parameters','Final parameters'),strict=True):
    points=[r for r in rows if re.fullmatch(base+r'-water--?[0-9.]+',r['name'])]
    for r in points:
        k=float(r['name'].split('water-')[1])
        if int(r['descent_states']): marker,color,label='x','#D55E00','Resolved descent'
        elif int(r['incomplete_states']): marker,color,label='^','#777777','No descent; incomplete search'
        else: marker,color,label='o','#0072B2','No resolved descent, 162 states'
        ax.scatter(k,float(r['cost']),marker=marker,color=color,label=label)
    ax.set(xlabel='MEAH⁺–water interaction constant kᵢⱼ (dimensionless)',ylabel='307-row cost (dimensionless)',title=title,yscale='log')
    handles,labels=ax.get_legend_handles_labels()
    unique=dict(zip(labels,handles))
    ax.legend(unique.values(),unique.keys(),fontsize=7)
fig.suptitle('Removing detected liquid splitting can be expensive without refitting',fontsize=12)
fig.savefig(OUT/'water-interaction-cost.png',dpi=170)
