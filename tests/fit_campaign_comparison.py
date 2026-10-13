"""Explicit same-wheel binary64 comparison of the #179 retained fit references."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'analyses/mea_parameter_bundle/scripts'), str(ROOT/'src')]
import fit_campaign as f
import fit_observations as o
for a,b in ((None,1.),('unavailable',1.),(1.,None),(1.,'unavailable')):
 mismatch=f.differences({'prediction':a},{'prediction':b})
 assert len(mismatch)==1 and mismatch[0]['field']=='/prediction'
policy=f.load(ROOT/'analyses/mea_parameter_bundle/data/input/fit-campaigns/permittivity-172.json')['replay'][0]['residual_comparison']
assert not f.replay_comparison(f.differences({'predicted':1.},{'predicted':1.+2**-52}),policy)['passed']
assert not f.replay_comparison(f.differences({'cost':1.},{'cost':1.+5*2**-52}),policy)['passed']
new,old=map(Path,sys.argv[1:3])
a=f.load(old/'native-fit.json');b=f.load(new/'native-fit.json')
fields=['physical','predictions','weighted_residuals','optimizer_jacobian','physical_jacobian','initial_cost','final_cost','iteration_costs',
'iterations','residual_evaluations','jacobian_evaluations','status','message','trial_failures','targets','start','coordinates','observation_statuses']
if 'observed' in a:fields.append('observed')
if 'usable' in a:fields.append('usable')
if 'covariance' in a:fields.append('covariance')
delta=f.differences({k:a[k] for k in fields},{k:b[k] for k in fields})
residuals=a.get('residuals',f.load(old/'fit-execution.json')['residuals'] if (old/'fit-execution.json').exists() else None)
assert residuals is not None
fields.append('residuals');delta+=f.differences(residuals,b['residuals'],'residuals')
ab=[a['coordinates'][i] if isinstance(i,int) else i for i in a['active_bounds']]
bb=[b['coordinates'][i] if isinstance(i,int) else i for i in b['active_bounds']]
delta+=f.differences(ab,bb,'active_bounds')
fa=a['failures'];fb=[{**x,'observation':b['targets'][x['observation']]} for x in b['failures']]
if fa and isinstance(fa[0]['observation'],int):fb=b['failures']
delta+=f.differences(fa,fb,'failures')
oldparameters=o.s.parameter_values(f.load(old/'parameters.json')) if (old/'parameters.json').exists() else dict(zip(a['coordinates'],a['physical'],strict=True))
newparameters=o.s.parameter_values(f.load(new/'parameters.json'))
delta+=f.differences(oldparameters,{k:newparameters[k] for k in oldparameters},'physical_mapping')
f.write(new/'comparison.json',dict(bitwise_equal=not delta,fields=fields+['active_bounds','failures','physical_mapping'],differences=delta,reference_path=str(old)))
print('PASS' if not delta else 'FAIL','cost',b['final_cost'],'iterations',b['iterations'],'differences',len(delta));print(delta[:2])
if delta:sys.exit(1)
