"""Render the retained loading comparison; never call the Engine."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AN=Path(__file__).resolve().parent
rows=json.loads((AN/'results/trend.json').read_text())
with (AN/'results/plotted-values.csv').open('w') as h:
    w=csv.DictWriter(h,fieldnames=['coefficient','loading','T_K','P_Pa','source_epsilon','epsilon'],lineterminator='\n')
    w.writeheader()
    w.writerows({k:r.get(k) for k in w.fieldnames} for r in rows)
fig,axes=plt.subplots(1,2,figsize=(10.5,5.5),sharey=True,layout='constrained')
for ax,cs in zip(axes,[[-2.,0.,7.01],['fitted',0.]]):
    sources=[r for r in rows if r['coefficient']==0.]
    ax.scatter([r['loading'] for r in sources],[r['source_epsilon'] for r in sources],marker='o',facecolors='none',edgecolors='black',label='Hajj: 915–2450 MHz-derived estimate',s=50)
    for c,color,marker in zip(cs,['#17658b','#c15525','#785899'],['s','^','v']):
        selected=[r for r in rows if r['coefficient']==c and 'epsilon' in r]
        ax.scatter([r['loading'] for r in selected],[r['epsilon'] for r in selected],color=color,marker=marker,label='Part I refit' if c=='fitted' else f'Equal ion coefficients = {c:g}')
    ax.set_xlabel('Loading / mol CO₂ per mol MEA')
    ax.legend(fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.2))
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.2)
axes[0].set_ylabel('Relative permittivity / dimensionless')
axes[0].set_title('A negative coefficient reverses the sampled trend')
axes[1].set_title('Part I fitting does not target the microwave estimates')
fig.suptitle('30 mass% MEA before loading; 353.15 K; model at 101325 Pa',fontsize=11)
fig.savefig(AN/'comparison.png',dpi=170)
plt.close(fig)
