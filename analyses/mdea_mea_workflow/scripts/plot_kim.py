"""Render the retained Kim calibration comparison; no thermodynamic evaluation."""
import csv,os
os.environ['MPLBACKEND']='Agg'
from pathlib import Path
import matplotlib.pyplot as plt
AN=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((AN/'results/kim-prefit/bubble-pressure-residuals.csv').open()))
fig,axes=plt.subplots(2,2,figsize=(9,6),layout='constrained')
for ax,temp in zip(axes.flat,(313,333,353,373)):
    rr=[r for r in rows if round(float(r['temperature_K']))==temp]
    x=[float(r['x_MDEA']) for r in rr]
    ax.errorbar(x,[float(r['observed_pressure_Pa'])/1000 for r in rr],yerr=.3,fmt='o',ms=4,color='#0072B2',label='Kim Table 8; u(P) = 0.3 kPa')
    ax.plot(x,[float(r['predicted_pressure_Pa'])/1000 for r in rr],'x',color='#D55E00',label='Kim-only fit at reported T')
    ax.set(title=f'Nominal {temp} K',xlabel='Liquid MDEA mole fraction',ylabel='Bubble pressure (kPa)')
axes[0,0].legend(fontsize=7)
fig.savefig(AN/'results/kim-prefit/bubble-pressure.png',dpi=180)
