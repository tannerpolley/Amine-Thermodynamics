import os,sys,json,subprocess
from pathlib import Path
root=Path.cwd()
sys.path.insert(0,str(root/'analyses/mdea_mea_workflow/scripts'))
old={}
for name in ('analyses/mdea_mea_workflow/inputs/physical-ideal-gas-calorics.json','analyses/solvent_specification_mdea/inputs/caloric.json'):
    content=subprocess.check_output(['git','show','0e216fe^:'+name],text=True)
    old[root/name]=content
    (Path('/tmp/mdea-298-water')/Path(name).name).write_text(content)
original=Path.read_text
Path.read_text=lambda self,*a,**kw:old[self] if self in old else original(self,*a,**kw)
os.environ['MDEA_ENGINE_WHEEL_SHA256']='0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'
import refit_298 as r
import refit_capped as owner
r.s=owner.s
results=[]
for label in ('A3','B1'):
    r.s.setup(r.read(r.AN/f'results/stage2-capped/{label}/endpoint.json'))
    r.META,r.ITEMS,weights=r.s.j.objective(r.s.params)
    rows=r.pool(r.predict,list(range(len(r.ITEMS))))
    retained=r.read(r.AN/f'results/stage2-capped/{label}/fit.json')
    available=all(x['status']=='Available' and x['requested_tolerance_met'] for x in rows)
    cost=sum(.5*w*x['residual']**2 for w,x in zip(weights,rows,strict=True)) if available else None
    error=abs(cost/retained['final_cost']-1) if available else None
    result=dict(record=label,rows=len(rows),available=available,cost=cost,historical_cost=retained['final_cost'],relative_cost_difference=error,passed=available and error<=1e-8)
    results.append(result)
    Path(f'/tmp/mdea-298-water/{label}-rows.json').write_text(json.dumps(rows,indent=2)+'\n')
    Path('/tmp/mdea-298-water/results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(result,flush=True)
