"""Retain column-normalized sensitivities and numerical derivative checks."""
import importlib.util
import json
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('probe',Path(__file__).with_name('admission_probe.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
p=a.p
summary={}
for v in 'AB':
 d=json.loads((p.OUT/f'results/probe-{v}.json').read_text())
 assert d['statuses']==['Available']*20
 J=np.array(d['residual_optimizer_gradient']).reshape(20,2)
 norms=np.linalg.norm(J,axis=0)
 normalized=J/norms
 summary[v]=dict(raw_column_norms=norms.tolist(),raw_larger_column=['MDEA-CO2','MDEAH+-CO2'][int(np.argmax(norms))],normalized_column_norms=np.linalg.norm(normalized,axis=0).tolist(),normalized_singular_values=np.linalg.svd(normalized,compute_uv=False).tolist(),rows=20,status='complete',meaning='The pre-normalization norms rank sensitivity. Each individually column-normalized norm is one, so those norms alone cannot rank columns.')
 np.savetxt(p.OUT/f'results/probe-{v}-columns.csv',np.column_stack((J,normalized)),delimiter=',',header='dlogP_dk_MDEA_CO2,dlogP_dk_MDEAH_CO2,normalized_MDEA_CO2,normalized_MDEAH_CO2',comments='')
summary['same_ranking']=summary['A']['raw_larger_column']==summary['B']['raw_larger_column']
summary['selected_for_stage2']=summary['A']['raw_larger_column'] if summary['same_ranking'] else None
summary['interpretation_limit']='Issue wording does not define a ranking functional after unit-column normalization. Raw norms and unit columns are both retained; no fitted-coordinate declaration has been changed.'
p.write('results/probe-summary.json',summary)
print(json.dumps(summary,indent=2))
