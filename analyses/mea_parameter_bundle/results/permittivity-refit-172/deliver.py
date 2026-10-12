"""Collect completed numerical evidence without another Engine calculation."""
import json
from pathlib import Path
import run as c
rows = json.loads((c.OUT/'comparison.json').read_text())
paths = [(r['branch']+'/'+r['problem'],Path(r['parameters']).parent) for r in rows]
paths += [('current',c.OUT/'baseline')]+[(b+'/unrefitted',c.OUT/b/'unrefitted') for b in ('smaller-dV','larger-dV')]
counts, trials, gates = [],[],[]
ceilings = dict(cost=35.26,pressure=15.81,species=9.89,Vinjarapu=3.13,Arcis=9.36)
baseline = json.loads((c.OUT/'baseline/summary.json').read_text())
for name,path in paths:
    points = json.loads((path/'family.json').read_text()); count = json.loads((path/'family-counts.json').read_text())
    assert [p['index'] for p in points]==list(range(73)) and sum(count.values())==73
    counts.append(dict(variant=name,**count))
    for p in points:
        for t in p.get('stability',{}).get('trials',[]): trials.append(dict(variant=name,index=p['index'],classification=p['classification'],**{k:t[k] for k in ('seed','support','evidence','resolved_descent','optimizer_success','optimizer_message','quantities','split_checks')}))
for r in rows:
    r['family'] = json.loads((Path(r['parameters']).parent/'family-counts.json').read_text())
    if r['problem']!='F1': continue
    r['gates']['family'] = r['family']['unresolved']==r['family']['failed']==0
    values = dict(cost=r['common149_cost'],pressure=r['scores']['pressure']['AARD_percent'],species=r['scores']['species']['AARD_percent'],Vinjarapu=r['Vinjarapu_RMSE_kJ_mol'],Arcis=r['Arcis_RMSE_kJ_mol'])
    control = dict(cost=baseline['cost'],pressure=baseline['scores']['pressure']['AARD_percent'],species=baseline['scores']['species']['AARD_percent'],Vinjarapu=baseline['Vinjarapu_RMSE_kJ_mol'],Arcis=baseline['Arcis_RMSE_kJ_mol'])
    for k,v in values.items(): gates.append(dict(branch=r['branch'],quantity=k,value=v,ceiling=ceilings[k],delta_from_same_wheel_current=v-control[k],passed=v<=ceilings[k]))
    gates += [dict(branch=r['branch'],quantity=k,passed=r['gates'][k]) for k in ('gas_root','family')]
c.write(c.OUT/'comparison.json',rows)
c.table(c.OUT/'family-counts.csv',counts); c.table(c.OUT/'trial-evidence.csv',trials); c.table(c.OUT/'owner-gates.csv',gates)
print('DELIVERED',[(r['branch'],r['gates']) for r in rows if r['problem']=='F1'],flush=True)
