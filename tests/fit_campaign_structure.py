"""Explicit #179 declaration, input-hash and memory-sizing checks; no fitting."""
import copy,json,sys,tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'analyses/mea_parameter_bundle/scripts'), str(ROOT/'src')]
import fit_campaign as f
import fit_observations as o
base=ROOT/'analyses/mea_parameter_bundle/data/input/fit-campaigns'
checks=[]
for path in sorted(base.glob('*-*.json')):
 s=f.load(path)
 if 'campaign_id' not in s:continue
 for case in s['cases']:
  for start in case['starts']:
   mapping,params,rows,coords=f.resolve(s,case,start)
   assert len(rows)==(167 if case['variant']['pool'] else 149)
   if case['variant']['problem']=='F3':
    assert len(coords)==5
    fam=next(x for x in mapping['model_families'] if x['kind']=='electrolyte')
    assert fam['choice']=='fully-dissociated-debye-huckel' and not set(fam)&{'c_shell','c_dielectric'}
    assert not any(c['family'] in ('born_diameter','solvation_factor') for comp in mapping['components'] for c in comp['coefficients'])
    assert not any(c['family']=='ionic_region_relative_permittivity' for c in mapping['model_coefficients'])
   checks.append(dict(spec=path.name,case=case['id'],start=start['id'],rows=len(rows),coordinates=len(coords)))
s=f.load(base/'permittivity-172.json');bad=copy.deepcopy(s);bad['inputs'][0]['sha256']='0'*64
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'bad.json';p.write_text(json.dumps(bad))
 try:f.run(p,Path(tmp)/'run',case_ids=['baseline'],operation='replay')
 except ValueError as e:assert 'input hash mismatch' in str(e)
 else:raise AssertionError('bad hash accepted')
assert f.workers(160_000_000,32,81_250_000)==1
try:f.workers(160_000_000,32,81_250_000,32)
except RuntimeError as e:assert 'deferred reproduction' in str(e)
else:raise AssertionError('memory constraint ignored')
if len(sys.argv)>1:
 f.write(Path(sys.argv[1]),dict(cases=checks,hash_mismatch_rejected=True,constrained_memory_passed=True))
print('structure PASS',len(checks),'declared starts')
