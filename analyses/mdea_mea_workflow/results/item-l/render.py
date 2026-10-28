"""Render retained item-(l) Cp comparisons; no model calculations."""
import csv,json,hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
rows=list(csv.DictReader((OUT/'cp-comparison.csv').open()))
fig,ax=plt.subplots(figsize=(7.4,4.3),layout='constrained')
for label,marker in [('item-k reciprocal + Wangler','s'),('linear + Neumann','o'),('slope-0 + Neumann (item-k k0)','^')]:
    group=[r for r in rows if r['case']==label and r['source'].startswith('Weiland')]
    ax.scatter([100*float(r['w_MDEA']) for r in group],[float(r['error_percent']) for r in group],label=label,marker=marker,s=55)
ax.fill_between([28,50],-5,5,color='gray',alpha=.12,label='±5% gate within ≤50 wt%')
ax.plot([28,50],[5,5],color='gray',ls='--',lw=1);ax.axhline(0,color='gray',lw=.5)
ax.axvspan(50,62,color='orange',alpha=.07,label='>50 wt% extrapolation')
ax.set(xlabel='MDEA mass fraction (%)',ylabel='Cp error relative to Weiland 1997 (%)',title='Linear law passes the ≤50 wt% Cp gate, 298.15 K',xticks=[30,40,50,60])
ax.legend(fontsize=8);fig.savefig(OUT/'cp-comparison.png',dpi=180)
html='<!doctype html><html><body><img style="width:100%;height:auto" alt="Cp errors compared with the requested five percent limit" src="'+str(OUT/'cp-comparison.png')+'"></body></html>'
(OUT/'comparison.html').write_text(html)
