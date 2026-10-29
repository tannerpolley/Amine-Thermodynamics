"""Frozen #222 endpoint predictions for the #225 context sources; no fitting."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import concurrent.futures as futures
import csv,hashlib,importlib.util,json,math,multiprocessing,sys,zipfile
from pathlib import Path
AN=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(AN.parents[1]/'src'),str(AN.parents[1]/'analyses/mea_parameter_bundle/scripts')]
import shared_evaluation
SHA='ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'
shared_evaluation.ENGINE_WHEEL_SHA256=SHA
spec=importlib.util.spec_from_file_location('context_stage2',AN/'scripts/stage2.py')
s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
OUT=AN/'results/context-sources'

def write(name,obj):
 OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def predict(row):
 rec=dict(row=row,status='unavailable')
 try:
  prob=s.j.problem(float(row['temperature_K']),101000.,s.j.water(float(row['unloaded_MDEA_mass_fraction'])),float(row['alpha_exp']),True)
  result=s.eq.solve_equilibrium(s.model,prob)
  rec.update(success=result.success,requested_tolerance_met=result.requested_tolerance_met,message=result.message,residuals=list(result.residuals))
  if result.success and result.requested_tolerance_met:
   value=result.pressure*result.phase_mole_fractions(1)[list(s.params.component_ids).index(s.j.C)]
   observed=float(row['p_CO2_kPa'])*1000
   rec.update(status='available',predicted_p_CO2_Pa=value,observed_p_CO2_Pa=observed,total_pressure_Pa=result.pressure,log_ratio=math.log(value/observed),relative_error=value/observed-1)
 except Exception as e:rec['message']=f'{type(e).__name__}: {e}'
 return rec

def pool(fn,jobs):
 with futures.ProcessPoolExecutor(max_workers=min(os.cpu_count(),len(jobs)),mp_context=multiprocessing.get_context('fork')) as ex:return list(ex.map(fn,jobs))

if __name__=='__main__':
 wheel=Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-d5138209/epcsaft-1.0.0-cp313-cp313-manylinux_2_39_x86_64.whl')
 assert sha(wheel)==SHA
 with zipfile.ZipFile(wheel) as z:
  for name in z.namelist():
   if name.startswith(('epcsaft/','epcsaft.libs/')) and not name.endswith('/'):assert z.read(name)==(Path(s.p.epcsaft.__file__).parent.parent/name).read_bytes(),name
 write('runtime.json',dict(wheel=str(wheel),wheel_sha256=SHA,installed_files_byte_identical=True,module=s.p.epcsaft.__file__,python=sys.version,cpu_count=os.cpu_count(),pool_size=os.cpu_count(),BLAS_threads=1))
 rows=list(csv.DictReader((s.p.DATA/'Xiao2018_context.csv').open()));assert len(rows)==20
 summary={};checks={}
 for label in ('A3','B1'):
  endpoint=AN/f'results/stage2-capped/{label}/endpoint.json';s.setup(json.loads(endpoint.read_text()))
  results=pool(predict,rows);write(f'{label}-Xiao.json',results)
  # Same bubble-state trial supports and density gate as #222; nitrogen is omitted.
  s.phase_jobs=[(r['source_row'],s.j.problem(float(r['temperature_K']),101000.,s.j.water(.235),float(r['alpha_exp']),True)) for r in rows]
  phase=pool(s.phase,list(range(len(rows))));write(f'{label}-phase.json',phase)
  ok=[r for r in results if r['status']=='available']
  assert len(results)==len(phase)==20
  if len(ok)==20:
   residual=max(abs(x) for r in results for x in r['residuals']);assert residual<=1e-10
   checks[label]=dict(rows=20,max_equilibrium_residual=residual,max_phase_residual=max(r['max_residual'] for r in phase),all_requested_tolerances_met=True)
  else:checks[label]=dict(rows=20,available=len(ok),all_requested_tolerances_met=False)
  write('numerical-checks.json',checks)
  summary[label]=dict(endpoint_sha256=sha(endpoint),rows=len(rows),available=len(ok),AARD_percent=100*sum(abs(r['relative_error']) for r in ok)/len(rows) if len(ok)==len(rows) else None,mean_absolute_log_ratio=sum(abs(r['log_ratio']) for r in ok)/len(rows) if len(ok)==len(rows) else None,phase=s.phase_summary(phase),Ermatchkov88=json.loads((AN/f'results/stage2-capped/{label}/assessment.json').read_text())['Ermatchkov88'])
  write('summary.json',summary);print(label,summary[label],flush=True)
