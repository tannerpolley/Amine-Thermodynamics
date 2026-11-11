import csv,hashlib,json,math,py_compile
from pathlib import Path
out=Path('analyses/mdea_mea_workflow/results/refit-298')
def read(path):return json.loads(path.read_text())
g=read(out/'gates.json');sel=read(out/'selection.json');f1=read(out/'F1.json')
assert f1['passed'] and all(x['passed'] for x in f1['explained_historical_difference']['confirmation'])
assert g['F4']['passed']
assert not g['F2']['A3']['passed'] and g['F2']['B1']['passed']
assert not g['F3']['A3']['passed'] and not g['F3']['B1']['passed']
for a in read(out/'attempts.json'):
 name=a['name'];fit=read(out/name/'fit.json');meta=read(out/name/'declaration.json')['observations']
 assert len(meta)==len(fit['predictions'])==278
 assert not any(x['group']=='Kuranov' and x['row']['source_row'] in ('28','72') for x in meta)
 assert abs(sum(.5*x*x for x in fit['weighted_residuals'])/fit['final_cost']-1)<1e-8
 e=read(out/name/'eligibility.json')
 assert e['passed'] and e['fit_replay']['passed']
 assert e['phase']['states']==775 and e['phase']['excluded_out_of_domain_states']==7
 assert e['phase']['unresolved']==e['phase']['ambiguous']==e['phase']['liquid_witnesses']==[]
 assert len(read(out/name/'phase-domain-exclusions.json'))==7
for label,x in sel.items():
 assert hashlib.sha256((out/x['name']/'endpoint.json').read_bytes()).hexdigest()==x['endpoint_sha256']
 assert x['cost']==min(a['cost'] for a in read(out/'attempts.json') if a['representation']==label and g['F4']['eligibility'][a['name']]['passed'])
for name,groups in read(out/'pressure-scores.json').items():
 rows=read(out/name/'pressure.json')
 for group,v in groups.items():
  q=[x['relative_error'] for x in rows if x['group']==group]
  assert len(q)==v['rows']==v['available']
  assert abs(100*sum(map(abs,q))/len(q)-v['AARD_percent'])<1e-10
assert hashlib.sha256((out/'selection.json').read_bytes()).hexdigest()==read(out/'selection-identity.json')['sha256']
for p in Path('analyses/mdea_mea_workflow/scripts').glob('*298.py'):py_compile.compile(str(p),doraise=True)
py_compile.compile('analyses/mdea_mea_workflow/scripts/stage2.py',doraise=True)
print('PASS: 278-row identity, independently reconstructed costs and pressure AARDs, endpoint replay and eligibility, domain exclusions, frozen selection, and syntax.')

for label in ('A3','B1'):
 names=[label+'-baseline-278',label+'-substitution-278',sel[label]['name']]
 cases=[read(out/name/'comparisons.json') for name in names]
 assert all([(x['group'],x['row'],x['observed']) for x in case]==[(x['group'],x['row'],x['observed']) for x in cases[0]] for case in cases)
 for name,case in zip(names,cases):
  kamps=[x for x in case if x['group']=='corrected-Kamps']
  assert len(kamps)==28
  admitted=[x for x in kamps if 'predicted' in x]
  if name.endswith('-baseline-278'):
   assert len(admitted)==28
  else:
   assert len(admitted)==21
   assert all(394.94<=float(x['row']['temperature_K'])<=395 and 'reaction R2 temperature outside reaction correlation' in x['message'] for x in kamps if 'predicted' not in x)
  heats=[x for x in case if x['group'] in ('Zheng','Merkley-outside','Merkley-half-loading')]
  assert len(heats)==26
  assert len(read(out/name/'fitted-replay.json'))==278
 before=read(out/names[0]/'parameters.json');after=read(out/names[1]/'parameters.json')
 shared=read(Path('analyses/mea_parameter_bundle/results/adoption-297/shared-bicarbonate-water.json'))
 i=next(i for i,p in enumerate(before['pairs']) if {p['component_id_a'],p['component_id_b']}=={'water','bicarbonate-anion'})
 before['pairs'][i]=shared
 assert before==after
print('PASS: three-case source/row/observable identity, 26 heat rows per case, historical 28/28 versus adopted 21/28 corrected-Kamps coverage, and fixed substitution only.')
