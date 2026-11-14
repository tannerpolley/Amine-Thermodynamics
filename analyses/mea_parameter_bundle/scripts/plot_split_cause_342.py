"""Three-panel figure from retained split evidence; never evaluates the model."""
import csv
import gzip
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":18})
B = Path('analyses/mea_parameter_bundle')
OUT = B/'results/split-cause-342'
rows = list(csv.DictReader((OUT/'contributions.csv').open()))
wide = min((x for x in rows if x['record']=='wide'),key=lambda x:float(x['delta_g_over_rt']))
pair = [x for x in rows if x['source']==wide['source'] and x['record'] in ('wide-isobaric','F2-isobaric')]
composition = [x for x in csv.DictReader((OUT/'compositions.csv').open()) if x['source']==wide['source'] and x['kind']=='liquid' and x['record']=='wide-isobaric' and x['configuration']=='split']
points = []
for row in json.loads(gzip.decompress((B/'results/stable-refit-255/qualification/wide-grid.json.gz').read_bytes()))['result']:
    block,wt,T,loading,ratio = row['key'].split('|')
    points.append(dict(block=block,wt=.3 if wt=='None' else float(wt),temperature_K=float(T),loading=float(loading),pressure_Pa=row['pressure_Pa'],available=row['available'],resolved=row['available'] and not row['no_descent_in_trial_set']))
for raw in json.loads(gzip.decompress((OUT/'wide/raw.json.gz').read_bytes())):
    points.append(dict(block='liquid-vapor',wt=.3,temperature_K=raw['temperature_K'],loading=raw['loading'],pressure_Pa=raw['pressure_Pa'],available=raw['final']['success'],resolved=any(t['resolved_descent'] for s in raw['stability'] for t in s['trials'])))
for filename,values in [('split-map.csv',points),('figure-contributions.csv',pair),('figure-compositions.csv',composition)]:
    with (OUT/filename).open('w') as handle:
        writer = csv.DictWriter(handle,fieldnames=values[0],lineterminator='\n')
        writer.writeheader()
        writer.writerows(values)
fig,axes = plt.subplots(1,3,figsize=(16,5.5),layout='constrained',gridspec_kw={'width_ratios':[1,1.2,1]})
ax = axes[0]
ax.scatter([x['loading'] for x in points],[x['temperature_K'] for x in points],c='#888888',s=9,label='Searched')
selected = [x for x in points if x['resolved']]
ax.scatter([x['loading'] for x in selected],[x['temperature_K'] for x in selected],marker='x',s=25,color='#D55E00',label='Resolved split')
ax.set(xlabel='Loading (mol CO₂/mol MEA)',ylabel='Temperature (K)',title='(a) Split locations')
ax.legend(fontsize=14,loc='upper left')
terms = ['hard_chain','dispersion','association','debye_huckel','born','pv','ideal_and_standard','delta_g_over_rt']
labels = ['Hard chain','Dispersion','Association','Debye–Hückel','Born','PV','Ideal + standard','Total']
for row,marker,color in zip(pair,('o','x'),('#D55E00','#0072B2'),strict=True):
    axes[1].scatter([float(row[t]) for t in terms],range(len(terms)),marker=marker,color=color,label=row['record'].replace('-isobaric',''))
axes[1].set(yticks=range(len(terms)),yticklabels=labels,xlabel='Split minus parent energy / RT (mol)',title='(b) Energy contributions')
axes[1].axvline(0,color='gray',lw=.5)
axes[1].legend(loc='lower right')
for ph,marker,color in zip(sorted(composition,key=lambda x:float(x['water'])),('o','x'),('#D55E00','#0072B2'),strict=True):
    species = ['water','monoethanolamine','protonated-monoethanolamine','carbamate-anion','bicarbonate-anion']
    axes[2].scatter([float(ph[s]) for s in species],range(len(species)),marker=marker,color=color,label='Water-poor' if marker=='o' else 'Water-rich')
axes[2].set(yticks=range(5),yticklabels=['H₂O','MEA','MEAH⁺','MEACOO⁻','HCO₃⁻'],xlabel='Mole fraction (mol/mol)',title='(c) Liquid compositions')
axes[2].legend()
fig.suptitle(f"Fixed-model attribution: {wide['temperature_K']} K, loading {wide['loading']}, {float(wide['pressure_Pa'])/1000:.3f} kPa")
fig.savefig(OUT/'split-cause.png',dpi=180)
