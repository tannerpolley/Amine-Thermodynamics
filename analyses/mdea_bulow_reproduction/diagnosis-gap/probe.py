"""Issue 223: one-factor dielectric probes on previously qualified rows only."""
import concurrent.futures,copy,csv,hashlib,json,math,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import run as primary
import epcsaft

def write(name,obj):
 (HERE/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def main():
 assert epcsaft.provenance()[1]==primary.p.EXPECTED_WHEEL
 base=json.loads((HERE.parent/'run-document.json').read_text())
 old=json.loads((HERE.parent/'row-results.json').read_text()); qualified={r['source_row']:r for r in old if r['qualified']}
 rows=[r for r in csv.DictReader((primary.p.ROOT/'data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv').open()) if int(r['source_row']) in qualified]
 assert len(rows)==63 and not {11,18,50,51}&set(qualified)
 for name in ['solvent-normalized','126-temperature-laws']:
  doc=copy.deepcopy(base)
  if name=='solvent-normalized':doc['model_families'][-1]['normalization']='solvent-normalized'
  else:
   coeffs={'water':(78.41043478578715,-.36133766233691506,.00076555618295),'methyldiethanolamine':(22.358,-.10245714285714318)}
   for c in doc['correlations']:
    if c['family']=='relative_permittivity':
     cs=coeffs[c['component_id']]; c['reference_temperature']['magnitude']=298.15;c['constant']['value']['magnitude']=cs[0];c['terms']=c['terms'][:len(cs)-1]
     for t,v in zip(c['terms'],cs[1:]):t['coefficient']['value']['magnitude']=v
     c['provenance']='Issue 126 model.py PERMITTIVITY; diagnostic only'
  write(name+'-document.json',doc)
  with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:
   results=[]
   for r in pool.map(primary.solve_row,[(doc,row) for row in rows]):
    results.append(r);print(name,r['source_row'],r['qualified'],flush=True)
  write(name+'-rows.json',results)
  comparisons=[]
  for r in results:
   b=qualified[r['source_row']]
   comparisons.append(dict(source_row=r['source_row'],qualified=r['qualified'],primary_P_Pa=b['P_Pa'],probe_P_Pa=r.get('P_Pa'),relative_pressure_change=(r['P_Pa']/b['P_Pa']-1) if r['qualified'] else None,primary_signed_log_deviation=math.log(b['P_Pa']/b['observed_P_Pa']),probe_signed_log_deviation=math.log(r['P_Pa']/b['observed_P_Pa']) if r['qualified'] else None))
  write(name+'-comparison.json',comparisons)
 write('execution.json',dict(engine=primary.p.ENGINE_COMMIT,wheel_sha256=primary.p.EXPECTED_WHEEL,python=sys.executable,excluded_rows=[11,18,50,51],processes=16,threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},primary_rows_sha256=hashlib.sha256((HERE.parent/'row-results.json').read_bytes()).hexdigest()))
if __name__=='__main__':main()
