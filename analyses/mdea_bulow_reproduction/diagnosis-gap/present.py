"""Draw retained signed log-pressure deviations; no model execution."""
import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
rows=list(csv.DictReader((p/'signed-pressure-deviations.csv').open()))
fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
for ax,wt in zip(axes,[19,32.3]):
 for T,color,marker in zip([313,333,373,393],['#0072B2','#E69F00','#009E73','#CC79A7'],['o','s','^','x']):
  rs=[r for r in rows if r['qualified']=='True' and abs(float(r['m_MDEA'])-(1.97 if wt==19 else 3.97))<.1 and abs(float(r['T_K'])-T)<1]
  ax.scatter([float(r['loading']) for r in rs],[float(r['signed_log_pressure_deviation']) for r in rs],c=color,marker=marker,label=f'{T} K',s=27)
 ax.axhline(0,color='black',lw=.7);ax.set(title=f'{wt} wt% nominal MDEA',xlabel='Loading / mol CO₂ per mol MDEA');ax.grid(alpha=.2)
axes[0].set_ylabel('ln(calculated total pressure / measured total pressure)')
axes[1].legend(fontsize=9);fig.suptitle('High-temperature pressures are systematically low')
fig.tight_layout();fig.savefig(p/'signed-pressure-deviations.png',dpi=170)
