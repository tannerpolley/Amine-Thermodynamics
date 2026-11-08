"""Render retained issue 266 comparisons; never import or run the model."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AN = Path(__file__).resolve().parents[1]
OUT = AN / 'results/bicarbonate-carbonate-266'
def read(name):
    path = OUT / (name+'.json')
    return json.loads(path.read_text() if path.exists() else gzip.decompress(path.with_suffix('.json.gz').read_bytes()))
inputs = read('inputs')
endpoints = {name:read(name) for name in ('baseline','fit1-executed','fit2')}
scales = {r['identity']:r for r in inputs['reconciliation']}
rows, inside = [], {}
for name, endpoint in endpoints.items():
    inside[name] = {}
    for r,p in zip(inputs['records'],endpoint['comparisons'],strict=True):
        row = dict(endpoint=name,identity=r['identity'],quantity=r['group'],loading=r['row']['model_loading'],
            wheel_sha256=endpoint['wheel_sha256'],
            pressure_Pa=inputs['problems'][r['problem']]['P'],temperature_K=inputs['problems'][r['problem']]['T'],
            observed=r['arguments']['observed'],predicted=p.get('value'),status=p['status'],tolerance_met=p.get('requested_tolerance_met'))
        if r['state_identity'] in scales:
            s = scales[r['state_identity']]
            row.update(lower=s['lower'],upper=s['upper'],empirical_scale=s['scale'],
                inside=p['status']=='Available' and p.get('requested_tolerance_met') and s['lower']<=p['value']<=s['upper'])
            key = str(row['pressure_Pa'])
            inside[name].setdefault(key,dict(inside=0,total=0))
            inside[name][key]['total'] += 1
            inside[name][key]['inside'] += int(row['inside'])
        rows.append(row)
with (OUT/'comparison-values.csv').open('w') as stream:
    writer = csv.DictWriter(stream,fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
    writer.writeheader()
    writer.writerows(rows)
sensitivities = read('sensitivity')
derivatives = []
for q in inputs['coordinates']:
    minus, plus = [s for s in sensitivities if s['coordinate']==q['identity']]
    for r,m,p in zip(inputs['records'],minus['comparisons'],plus['comparisons'],strict=True):
        available = all(v['status']=='Available' and v.get('requested_tolerance_met') for v in (m,p))
        derivatives.append(dict(coordinate=q['identity'],identity=r['identity'],quantity=r['group'],wheel_sha256=minus['wheel_sha256'],
            minus=m.get('value'),plus=p.get('value'),physical_step=q['scale'],
            central_derivative=(p['value']-m['value'])/(2*q['scale']) if available else None,available=available))
with (OUT/'sensitivity-values.csv').open('w') as stream:
    writer = csv.DictWriter(stream,fieldnames=list(derivatives[0]))
    writer.writeheader()
    writer.writerows(derivatives)
phase = {}
for name in endpoints:
    path = OUT / ('phase-'+name+'-runtime.json')
    if not path.exists():
        phase[name] = dict(coverage='incomplete or not assessed')
        continue
    evidence = read('phase-'+name)
    phase[name] = dict(requested=len(evidence),completed=sum(r.get('stability',{}).get('completed',False) for r in evidence),
        resolved=sum(not r['unresolved'] for r in evidence),unresolved=sum(bool(r['unresolved']) for r in evidence),
        states_with_liquid_witness=sum(bool(r.get('dense')) for r in evidence),states_with_vapor_witness=sum(bool(r.get('gas')) for r in evidence),
        liquid_witness_trials=sum(len(r.get('dense',[])) for r in evidence),vapor_witness_trials=sum(len(r.get('gas',[])) for r in evidence))
summary = dict(wheel_sha256=endpoints['baseline']['wheel_sha256'],inside=inside,phase=phase,probes={n:dict(assessable=e['assessable'],preservation_passed=all(g['passed'] for g in e['preservation'].values()),
    trial_failures=e['trial_failures']) for n,e in endpoints.items() if n!='baseline'})
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
group_rows = [dict(endpoint=n,group=g,**v,wheel_sha256=e['wheel_sha256'],preservation_passed=None if n=='baseline' else e['preservation'][g]['passed'])
              for n,e in endpoints.items() for g,v in e['groups'].items()]
with (OUT/'group-metrics.csv').open('w') as stream:
    writer = csv.DictWriter(stream,fieldnames=list(group_rows[0]))
    writer.writeheader()
    writer.writerows(group_rows)
fig, axes = plt.subplots(1,3,figsize=(13,4),sharey=True,layout='constrained')
for ax,pressure in zip(axes,(101325.,500000.,2500000.)):
    source = inputs['reconciliation']
    x = [r['loading'] for r in source]
    ax.vlines(x,[r['lower'] for r in source],[r['upper'] for r in source],color='.7',lw=4,label='Two-source envelope')
    ax.scatter(x,[r['matin'] for r in source],marker='o',s=22,facecolor='none',edgecolor='black',label='Matin')
    ax.scatter(x,[r['bottinger'] for r in source],marker='x',s=22,color='black',label='Böttinger interpolated')
    for name,marker,color in [('baseline','s','#0072B2'),('fit1-executed','+','#D55E00'),('fit2','^','#009E73')]:
        values = [r for r in rows if r['endpoint']==name and r['quantity']=='Matin2012 pool' and r['pressure_Pa']==pressure and r['status']=='Available']
        ax.scatter([r['loading'] for r in values],[r['predicted'] for r in values],marker=marker,s=22,color=color,label={'baseline':'Baseline','fit1-executed':'Probe 1','fit2':'Probe 2'}[name])
    ax.set(title=f'{pressure/1e5:g} bar; 293.15 K',xlabel='Loading (mol CO₂/mol MEA)')
    ax.grid(alpha=.2)
axes[0].set_ylabel('HCO₃⁻ + CO₃²⁻ (mol/mol true liquid)')
axes[-1].legend(fontsize=7)
fig.savefig(OUT/'source-envelope.png',dpi=180,metadata={'Description':'Engine wheel SHA-256 '+summary['wheel_sha256']})
plt.close(fig)
files = [p for p in OUT.iterdir() if p.suffix in ('.json','.gz','.csv','.png') and p.name not in ('presentation-hashes.json','change-accounting.json')]
(OUT/'presentation-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
print(json.dumps(summary,indent=2))
