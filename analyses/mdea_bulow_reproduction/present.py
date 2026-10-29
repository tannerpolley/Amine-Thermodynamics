"""Read retained issue-223 results; never run the thermodynamic model."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
summary=json.loads((OUT/'summary.json').read_text())
groups=summary['isotherms']
with (OUT/'comparison.csv').open('w',newline='') as f:
    writer=csv.writer(f,lineterminator="\n")
    writer.writerow(['nominal_MDEA_wt_percent','nominal_T_K','N','qualified','Bulow_SI_S3_ARD_percent','our_ARD_percent','interval_lower_percent','interval_upper_percent','reached'])
    writer.writerows([[g['nominal_wt_percent'],g['nominal_T_K'],g['N'],g['qualified_count'],g['SI_S3_percent'],g['our_ARD_percent'],*g['interval_percent'],g['reached']] for g in groups])
lines=['| MDEA / wt% | T / K | Qualified / N | Our ARD / % | SI S3 ARD / % | Interval / % | Disposition |','|---|---|---|---|---|---|---|']
fig,ax=plt.subplots(figsize=(8,5.5))
for i,g in enumerate(groups):
    ours=g['our_ARD_percent']
    ax.errorbar(g['SI_S3_percent'],i,xerr=3,fmt='o',color='#0072B2',capsize=4,label='SI Table S3 ±3 point working interval' if i==0 else None)
    if ours is not None:
        ax.plot(ours,i,'x',color='#D55E00',ms=8,label='Our complete isotherm' if i==2 else None)
    else:
        ax.text(76,i,'unresolved',va='center',fontsize=9)
    interval='–'.join(f'{v:.2f}' for v in g['interval_percent'])
    lines.append(f"| {g['nominal_wt_percent']} | {g['nominal_T_K']} | {g['qualified_count']}/{g['N']} | {ours:.4f}"+f" | {g['SI_S3_percent']:.2f} | {interval} | Outside interval |" if ours is not None else f"| {g['nominal_wt_percent']} | {g['nominal_T_K']} | {g['qualified_count']}/{g['N']} | Unavailable | {g['SI_S3_percent']:.2f} | {interval} | Inconclusive |")
ax.set(yticks=range(8),yticklabels=[f"{g['nominal_wt_percent']} wt%, {g['nominal_T_K']} K" for g in groups],xlabel='Absolute relative deviation / %',xlim=(0,102),title='Five complete isotherms miss; three remain unresolved')
ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.14),fontsize=9)
fig.tight_layout();fig.subplots_adjust(bottom=.24);fig.savefig(OUT/'comparison.png',dpi=180);plt.close(fig)
(OUT/'results/comparison.md').write_text('\n'.join(lines)+'\n')
