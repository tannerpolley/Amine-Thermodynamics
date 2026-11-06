import csv,gzip,json,math,hashlib
from pathlib import Path
P=Path('analyses/mea_parameter_bundle/results/phase-diagnosis-255')
rows=[json.loads(q.read_text()) for q in sorted(P.glob('*/summary.json'))]
assert all(x['rows']==307 and x['available'] and x['loaded_rows']==47 for x in rows)
checks=[]
for x in rows:
    d=P/x['name']
    values=json.loads((d/'replay.json').read_text())
    assert abs(math.fsum(v['cost'] for v in values)-x['cost'])<1e-8
    with gzip.open(d/'phase-results.json.gz','rt') as f: raw=json.load(f)
    assert len(raw)==x['states']
    bad=[]
    for r in raw:
        v=r.get('final',{})
        if not (v.get('success') and v.get('requested_tolerance_met') and max(map(abs,v.get('raw_residuals',[math.inf])))<=1e-10 and v['reduced_hessian_minimum']>=0 and all(z>0 for z in v['pressure_density_derivatives'])):bad.append(r['index'])
    reduction=json.loads((d/'reduction.json').read_text())
    assert sum(not r['complete'] for r in reduction)==x['incomplete_states']
    assert [r['index'] for r in reduction if not r['parent_admitted']]==bad
    checks.append(dict(name=x['name'],parent_not_admitted=bad))
control={x['name']:x for x in rows}
assert abs(control['wide']['cost']-148.21150759040813)<1e-8
assert abs(control['final']['cost']-148.87893934555717)<1e-8
assert control['wide']['descent_states']==32 and control['final']['descent_states']==0
assert control['wide']['loaded_within_2s']==47 and control['final']['loaded_within_2s']==44
for name,indices in {'wide-pair--0.5':[155], 'final-water--0.1':[92,98], 'final-water-0.0':[55,56,74,92,95]}.items():
    reduced=json.loads((P/name/'reduction.json').read_text())
    assert sorted(r['index'] for r in reduced if not r['complete'])==indices
r=list(csv.DictReader((P/'contributions.csv').open()))
assert len(r)==51
keys=['hard_chain','dispersion','association','debye_huckel','born','cation_mixing','dipolar','pv','ideal_and_standard']
error=max(abs(sum(float(x[k]) for k in keys)-float(x['delta_g_over_rt'])) for x in r)
assert error<1e-10
energy=min(r,key=lambda x:float(x['delta_g_over_rt']))
assert (int(energy['index']),int(energy['trial']))==(133,3)
assert abs(float(energy['delta_g_over_rt'])*8.31446261815324*float(energy['temperature_K'])+7560.7640)<5e-5
out=dict(probes=len(rows),parents=checks,contribution_sum_max_error_over_rt=error,control_cost_tolerance=1e-8,controls_reproduced=True,current_producer_sha256=hashlib.sha256(Path('analyses/mea_parameter_bundle/scripts/phase_diagnosis_255.py').read_bytes()).hexdigest())
(P/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
