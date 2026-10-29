"""One-convention isothermal pressure probes, issue 223 round 2."""
import concurrent.futures,copy,csv,hashlib,json,math,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import run as primary
import epcsaft
BASE=json.loads((HERE.parent/'run-document.json').read_text())
SKIP={11,18,50,51}
PROBES=['1-packing','2b-all-dispersion','3-electrostatic-diameters','4-association-d-cubed','5-cross-association','6-reference-1bar','7-hydronium']
def write(name,obj): (HERE/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def document(name,T):
 d=copy.deepcopy(BASE)
 sig={};diam={}
 for c in d['components']:
  vals={v['family']:v['value']['magnitude'] for v in c['coefficients']};i=c['component_id']
  s=vals.get('segment_diameter',2.7927+10.11*math.exp(-.01775*T)-1.417*math.exp(-.01146*T));sig[i]=s
  diam[i]=s*(1-.12*math.exp(-3*vals['dispersion_energy_over_k']/T))
  if name in ['1-packing','3-electrostatic-diameters'] and c['fixed']['charge_number']['value']['magnitude']:
   for v in c['coefficients']:
    if v['family'] in (['packing_diameter'] if name=='1-packing' else ['born_diameter','debye_huckel_diameter']):v['value']['magnitude']=diam[i]
 if name=='2b-all-dispersion':
  d['model_families'][2]['ionic_dispersion']='all-ion-pairs'
  present={frozenset((p['component_id_a'],p['component_id_b'])) for p in d['pairs']}
  for j,a in enumerate(d['components']):
   for b in d['components'][j+1:]:
    ai=a['component_id'];bi=b['component_id']
    if frozenset((ai,bi)) not in present:
     d['pairs'].append({'component_id_a':ai,'component_id_b':bi,'provenance':'Issue 223 other unlike pairs zero; now consumed by all-ion dispersion','coefficients':[{'family':'k_ij','identity':f'pair/{ai}/{bi}/k_ij','value':{'magnitude':0.,'unit':'dimensionless'}}]})
 if name=='5-cross-association':
  top=d['topology'];top['no_cross_association']=[]
  for a,b in [('methyldiethanolamine','carbon-dioxide'),('carbon-dioxide','methyldiethanolamine')]:
   e=copy.deepcopy(top['edges'][3]);e['endpoint_a']['component_id']=a;e['endpoint_b']['component_id']=b
   e['source']['inputs']={k:['association/methyldiethanolamine/'+v,'association/carbon-dioxide/'+v] for k,v in [('energy_over_k','energy'),('volume','volume')]};top['edges'].append(e)
 if name=='4-association-d-cubed':
  edges=d['topology']['edges'];own={e['endpoint_a']['component_id']:e for e in edges if e['source']['kind']=='explicit'}
  for j,e in enumerate(edges):
   a=e['endpoint_a']['component_id'];b=e['endpoint_b']['component_id'];sa=(sig[a]+sig[b])/2;da=(diam[a]+diam[b])/2
   if e['source']['kind']=='combining-rule':
    energy=sum(own[i]['energy_over_k']['value']['magnitude'] for i in [a,b])/2
    volume=math.sqrt(math.prod(own[i]['volume']['value']['magnitude'] for i in [a,b]))*(math.sqrt(sig[a]*sig[b])/sa)**3
    e['energy_over_k']={'identity':f'round2/{j}/energy','value':{'magnitude':energy,'unit':'kelvin'}}
    e['volume']={'identity':f'round2/{j}/volume','value':{'magnitude':volume,'unit':'dimensionless'}}
   # resolve all original combining rules before changing any self volumes
  for e in edges:
   a=e['endpoint_a']['component_id'];b=e['endpoint_b']['component_id'];e['volume']['value']['magnitude']*=((diam[a]+diam[b])/(sig[a]+sig[b]))**3
   e['source']={'kind':'explicit','provenance':'Diagnostic d_ij cubed in association strength; original Wolbach-Sandler volume retained before strength conversion'}
 if name=='7-hydronium':
  d['components'][6]['fixed']['molar_mass']['value']['magnitude']=.01902322
 return d
ORIGINAL_PROBLEM=primary.problem
ORIGINAL_REACTIONS=copy.deepcopy(primary.p.REACTIONS)
ORIGINAL_ELEMENTS=copy.deepcopy(primary.ELEMENTS)
def solve(task):
 name,row=task
 if int(row['source_row']) in SKIP:return dict(source_row=int(row['source_row']),qualified=False,not_retried=True,reason='Primary unresolved row; owner prohibits retry')
 primary.p.REACTIONS=copy.deepcopy(ORIGINAL_REACTIONS);primary.ELEMENTS=copy.deepcopy(ORIGINAL_ELEMENTS)
 if name=='7-hydronium':
  for r in primary.p.REACTIONS:r['stoichiometry'][primary.p.W]=r['stoichiometry'].get(primary.p.W,0)-r['stoichiometry'].get(primary.p.H,0)
  primary.ELEMENTS[6]=(0,3,0,1)
 def problem(row):
  p=ORIGINAL_PROBLEM(row)
  if name=='6-reference-1bar':
   for r in p.reactions:r.reference=primary.eq.ReactionReference(primary.eq.ReferenceSourceBasis.RawMoleFractionInfiniteDilution,100000.)
  return p
 primary.problem=problem
 try:return primary.solve_row((document(name,float(row['temperature_K'])),row))
 finally:primary.problem=ORIGINAL_PROBLEM

def main():
 assert epcsaft.provenance()[1]==primary.p.EXPECTED_WHEEL
 inv=json.loads((HERE.parent/'inventory.json').read_text());ids={n for g in inv['isotherms'] for n in g['source_rows']}
 rows=[r for r in csv.DictReader((primary.p.ROOT/inv['table_path']).open()) if int(r['source_row']) in ids];assert len(rows)==67
 write('execution.json',dict(engine=primary.p.ENGINE_COMMIT,wheel_sha256=primary.p.EXPECTED_WHEEL,python=sys.executable,primary_rows_sha256=hashlib.sha256((HERE.parent/'row-results.json').read_bytes()).hexdigest(),processes=16,threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},not_retried=sorted(SKIP),skipped_probes={'2a':'Pinned wheel admits only all-ion-pairs and exclude-same-sign-ion-pairs; no self-only exclusion and no self-pair k_ii declaration','8':'Eq.26 explicitly theta=T-298.15 K; Table 3 coefficients match; no ambiguity found'}))
 for name in PROBES:
  if (HERE/(name+'-rows.json')).exists():continue
  write(name+'-example-document.json',document(name,373.15))
  with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:
   results=[]
   for r in pool.map(solve,[(name,row) for row in rows]):results.append(r);print(name,r['source_row'],r['qualified'],flush=True)
  write(name+'-rows.json',results)
if __name__=='__main__':main()
