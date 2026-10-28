"""Render only retained fitted-row residuals; no model evaluation."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parents[1]/'results/diagnosis-a1-bounds'
rows=list(csv.DictReader((OUT/'a1-density-cp-residuals.csv').open()))
fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
for ax,group,xkey,xlabel,ylabel in zip(axes,('unloaded-density','Cp'),('temperature_K','loading'),('Temperature (K)','Loading (mol CO₂/mol MDEA)'),('Density difference (kg/m³)','Heat-capacity difference (J/g/K)')):
    subset=[r for r in rows if r['group']==group]
    for w,color,marker in zip(sorted(set(r['MDEA_mass_fraction'] for r in subset)),('#0072B2','#D55E00','#009E73','#CC79A7'),('o','x','s','^')):
        selected=[r for r in subset if r['MDEA_mass_fraction']==w]
        ax.scatter([float(r[xkey]) for r in selected],[float(r['difference']) for r in selected],label=f'{100*float(w):g} wt%',color=color,marker=marker,s=28)
    ax.axhline(0,color='0.3',lw=.7);ax.set(xlabel=xlabel,ylabel=ylabel,title='A1: model minus fitted observations');ax.legend(fontsize=8);ax.grid(alpha=.15)
fig.savefig(OUT/'a1-density-cp-residuals.png',dpi=170)
