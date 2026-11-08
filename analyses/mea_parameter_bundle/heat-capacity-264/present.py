"""Presentation only: retained observations, predictions, contribution and cost comparisons."""
import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent
SHA='83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
def load(name):
    d=json.loads((P/name).read_text())
    assert d['wheel_sha256']==SHA
    return d['result']

def main():
    snapshots={'baseline':load('baseline.json')['predictions']}
    for name in ('A','B'):
        snapshots[name]=load(f'probe-{name}-replay.json')['broad']
    rows=[]
    for name,predictions in snapshots.items():
        for p in predictions:
            assert p['status']=='Available' and p['requested_tolerance_met'],p
            source=p['row']
            observed=float(source['cp_kJ_kg_K'])
            rows.append(dict(model=name,identity=p['identity'],source=source['source'],T_K=float(source['T_K']),loading=float(source['loading']),observed_kJ_kg_K=observed,predicted_kJ_kg_K=p['value']/p['observed']*observed,signed_error_percent=100*(p['value']/p['observed']-1),relative_scale=float(source['relative_scale']),wheel_sha256=SHA))
    def csvwrite(name,values):
        with (P/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
    csvwrite('plotted-values.csv',rows)
    bins=[]
    for name in snapshots:
        for subset in ('all sources','Hilliard fitted'):
            data=[r for r in rows if r['model']==name and (subset=='all sources' or r['source']=='Hilliard2008')]
            for field in ('T_K','loading','source'):
                for val in sorted({r[field] for r in data}):
                    selected=[r for r in data if r[field]==val]
                    bins.append(dict(model=name,subset=subset,grouping=field,value=val,count=len(selected),AARD_percent=np.mean([abs(r['signed_error_percent']) for r in selected]),RMSE_kJ_kg_K=np.sqrt(np.mean([(r['predicted_kJ_kg_K']-r['observed_kJ_kg_K'])**2 for r in selected]))))
    csvwrite('cp-by-temperature-loading-source.csv',bins)
    costs=[]
    for name in ('A','B'):
        r=load(f'probe-{name}-replay.json')
        for basis,key in [('fit objective','fit_metrics'),('original 307 plus 22 heat controls','original_metrics')]:
            for group,v in r[key]['groups'].items():
                costs.append(dict(probe=name,basis=basis,group=group,rows=v['rows'],available=v['available'],cost=v['cost'],cost_share=v['cost_share'],AARD_percent=v['AARD_percent'],RMSE_native=v['RMSE_native']))
    csvwrite('group-costs.csv',costs)
    fig,axes=plt.subplots(1,3,figsize=(11,3.6),sharey=True,layout='constrained')
    styles={'baseline':('s','#0072B2'),'A':('^','#D55E00'),'B':('v','#009E73')}
    for ax,a in zip(axes,[0.,.139,.358]):
        data=[r for r in rows if r['model']=='baseline' and r['source']=='Hilliard2008' and r['loading']==a]
        ax.errorbar([r['T_K'] for r in data],[r['observed_kJ_kg_K'] for r in data],yerr=[.02*r['observed_kJ_kg_K'] for r in data],fmt='o',ms=3,color='black',elinewidth=.5,label='Hilliard ±2% accuracy')
        for name,(marker,color) in styles.items():
            data=[r for r in rows if r['model']==name and r['source']=='Hilliard2008' and r['loading']==a]
            ax.scatter([r['T_K'] for r in data],[r['predicted_kJ_kg_K'] for r in data],marker=marker,s=14,color=color,label=name)
        ax.set(xlabel='Temperature / K',title=f'Loading = {a:g} mol CO₂/mol MEA')
    axes[0].set_ylabel('Heat capacity / kJ kg⁻¹ K⁻¹')
    axes[0].legend(fontsize=7)
    fig.savefig(P/'heat-capacity.png',dpi=180)
    print('retained values, bins, costs and figure prepared')

if __name__=='__main__':main()
