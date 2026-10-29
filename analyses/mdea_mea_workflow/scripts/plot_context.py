"""Render retained Xiao observations and frozen endpoint predictions only."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parents[1]/'results/context-sources'
fig,axes=plt.subplots(2,2,figsize=(9,6.5),sharex=True,sharey=True)
data={k:json.loads((OUT/f'{k}-Xiao.json').read_text()) for k in ('A3','B1')}
for ax,T in zip(axes.flat,(298.15,303.15,308.15,313.15),strict=True):
 rows=[r for r in data['A3'] if float(r['row']['temperature_K'])==T]
 x=[float(r['row']['alpha_exp']) for r in rows];y=[r['observed_p_CO2_Pa']/1000 for r in rows]
 ax.errorbar(x,y,xerr=.004,yerr=[.015*v for v in y],fmt='o',color='black',label='Xiao observations',capsize=2)
 for key,marker,color in [('A3','x','#0072B2'),('B1','+','#D55E00')]:
  rows=[r for r in data[key] if float(r['row']['temperature_K'])==T and r['status']=='available']
  ax.scatter([float(r['row']['alpha_exp']) for r in rows],[r['predicted_p_CO2_Pa']/1000 for r in rows],marker=marker,color=color,label=key)
 ax.set_title(f'{T:.2f} K');ax.grid(alpha=.2)
fig.supxlabel('CO₂ loading (mol CO₂ / mol MDEA)');fig.supylabel('CO₂ partial pressure (kPa)')
axes[0,0].legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'Xiao-pressure.png',dpi=180)
