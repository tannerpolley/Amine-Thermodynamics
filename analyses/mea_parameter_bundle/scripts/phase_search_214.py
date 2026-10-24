"""Issue 214: one finite grid on the reported record's bubble pressures."""
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT = Path.cwd()
B = ROOT/'analyses/mea_parameter_bundle'
sys.path[:0] = [str(B/'scripts'), str(B/'calibration-misfit'), str(ROOT/'src')]
import phase_extension_201 as e
f, load, write = e.f, e.load, e.write
OUT = B/'results/engine-3e83e19c-phase-search/run-2'
CHAIN = B/'results/engine-3e83e19c-refit-chain'
FITS = {'reported': CHAIN/'restricted-2/attempt-3/run/fit/usable-budget-endpoint.json', 'comparison': CHAIN/'a6/run/fit/usable-budget-endpoint.json'}
EXPECTED = ('00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91', 'efb2a9abe3787410734394f5ee32e6eade42d7cb6f5ad23445a357423690b2f3')
TEMPERATURES, LOADINGS = (313.15,318.15,333.15,353.15,373.15,393.15), (1e-5,.05,.1,.2,.256,.3,.4,.5,.6)
SOURCE = Path(e.__file__)


def adapt(name, changes, prefix='', suffix=''):
    node = next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)
    source = '\n'.join(SOURCE.read_text().splitlines()[node.lineno-1:node.end_lineno])+'\n'
    for old,new in changes:
        assert old in source, old
        source = source.replace(old,new)
    exec(compile(prefix+source+suffix,str(SOURCE),'exec'),vars(e))


def reference(T, a, path):
    mapping = f.s.parameter_mapping(FITS['reported'])
    model = f.epcsaft.Mixture(f.epcsaft.Parameters.from_mapping(mapping),thermochemistry=f.thermal.record())
    row = dict(temperature_K=T,loading=a,pressure_Pa=101325.,bubble_start=None,parameter_binding=load(OUT/'provenance.json')['parameters']['reported'])
    _,liquid,bubble = f.diagnose(model,e.request(mapping,313.15,.11),row,path)
    payload = row.get('bubble',{})
    admitted = bubble is not None and bubble.success and bubble.requested_tolerance_met and math.isfinite(bubble.pressure) and 1<=bubble.pressure<=1e7 and bubble.amounts[0]>0 and bubble.amounts[1]==0 and max(map(abs,payload['raw_residuals']))<=1e-10 and bubble.reduced_hessian_minimum>=0 and all(v>0 for v in payload['pressure_density_derivatives'])
    write(path,dict(row,result=payload,admitted=admitted,cause='' if admitted else 'reference unavailable or numerical/pressure admission failed'))


def grid(stop):
    states, references = [], []
    for j,a in enumerate(LOADINGS):
        for T in TEMPERATURES:
            path = OUT/'reference-pressure'/f'{T}-{j}.json'
            ref = load(path) if path.exists() else dict(cause=stop or 'reference not returned')
            P = ref.get('result',{}).get('pressure')
            references.append(dict(temperature_K=T,loading=a,reference_pressure_Pa=P,admitted=ref.get('admitted',False),cause=ref.get('cause'),path=str(path.relative_to(OUT)),diagnostics=ref.get('result'),timing=ref.get('timing')))
            for fraction in (.5,.8,.95):
                pressure = P*fraction if P is not None and math.isfinite(P) else None
                candidate = pressure is not None and 1<=pressure<=1e7
                observed = {353.15:(1e5,1e6),373.15:(1.1e5,1e6),393.15:(2.5e5,3e6)}.get(T)
                states.append(dict(index=len(states),temperature_K=T,loading=a,fraction=fraction,pressure_Pa=pressure,reference_pressure_Pa=P,reference_path=str(path.relative_to(OUT)),admitted=ref.get('admitted',False) and candidate,cause=ref.get('cause') or ('' if candidate else 'outside candidate pressure interval'),diagnostic_interval=pressure is not None and 10<=pressure<=300000,candidate_interval=candidate,observed_total_interval=observed[0]<=pressure<=observed[1] if observed and pressure is not None else None,temperature_extrapolation=T>333.15))
    write(OUT/'inputs/states.json',states)
    for path in (OUT/'states.csv',OUT/'inputs/states.csv'):
        f.table(path,states)
    for path in (OUT/'family-points.txt',OUT/'inputs/family-points.txt'):
        path.write_text(''.join(f'{s["loading"]!r} {s["temperature_K"]!r} {s["pressure_Pa"] if s["pressure_Pa"] is not None else "nan"}\n' for s in states))
    f.table(OUT/'reference-pressures.csv',references)
    return states


def export(states, provenance):
    rows = [row for fit in FITS for row in load(OUT/fit/'reduction.json')]
    trials = list(f.csv.DictReader((OUT/'trials.csv').open()))
    outcomes, confirmations, incomplete = [], [], []
    for fit,path in FITS.items():
        binding = dict(parameter_path=str(path.relative_to(ROOT)),parameter_bytes_sha256=f.s.sha256(path),runtime_mapping_sha256=hashlib.sha256(json.dumps(f.s.parameter_mapping(path),sort_keys=True).encode()).hexdigest(),states_sha256=f.s.sha256(OUT/'inputs/states.json'),points_sha256=f.s.sha256(OUT/'inputs/family-points.txt'))
        write(OUT/fit/'provenance.json',dict(provenance,**binding))
        for raw in (OUT/fit).glob('point-*.json'):
            payload = load(raw)
            write(raw,dict(payload,parameter_binding=binding))
            state = next(r for r in rows if r['record']==fit and r['index']==payload['index'])
            if not state['admitted'] or not state['final_success'] or state['missing_trials'] or state['failed_trial_optimizers'] or state['trial_unresolved'] or state['classification']=='unresolved' or not payload.get('final',{}).get('requested_tolerance_met') or not all(r['completed'] for r in payload.get('stability',[])):
                incomplete.append(dict(state,raw_timing=payload.get('timing'),raw_failure=payload.get('failure'),stability_completed=[r['completed'] for r in payload.get('stability',[])]))
        distinct = {r['path']:r for r in load(OUT/fit/'split-summary.json') if r['native_trial_index']==r['representative']}
        for relative,item in distinct.items():
            raw = OUT/relative
            result = load(raw) if raw.exists() else dict(confirmed=False,cause='confirmation not returned')
            parent = OUT/fit/f'point-{item["index"]}.json'
            write(raw,dict(result,parameter_binding=binding,parent_path=str(parent.relative_to(OUT)),parent_sha256=f.s.sha256(parent)))
            row = dict(item,loading=states[item['index']]['loading'],pressure_Pa=states[item['index']]['pressure_Pa'],success=result.get('result',{}).get('success',False))
            if result.get('confirmed'):
                for phase in result['result']['phases']:
                    prefix = phase['identity']+'/'
                    row.update({prefix+'role':phase['role'],prefix+'support':phase['support'],prefix+'amount_mol':phase['amount_mol'],prefix+'molar_density_mol_m3':phase['molar_density_mol_m3']})
                    row.update({prefix+'x/'+species:x for species,x in zip(phase['support'],phase['mole_fractions'],strict=True)})
            confirmations.append(row)
        for T in TEMPERATURES:
            subset = [r for r in rows if r['record']==fit and r['temperature_K']==T]
            returned = [t for t in trials if t['record']==fit and float(t['temperature_K'])==T and t['status']=='returned']
            completed = sum(r['admitted'] and r['final_success'] and r['missing_trials']==r['failed_trial_optimizers']==r['trial_unresolved']==0 for r in subset)
            outcomes.append(dict(run='issue-214',record=fit,temperature_K=T,scheduled_states=len(subset),scheduled_trials=9*len(subset),completed=completed,unresolved=sum(r['admitted'] and r['final_success'] for r in subset)-completed,unavailable_pressure=sum(not r['admitted'] for r in subset),unavailable_numerical=sum(r['parent_numerical_failure'] for r in subset),returned_trials=len(returned),resolved_trials=sum(t['resolved_descent']=='True' for t in returned),descent_states=sum(r['resolved_trials']>0 for r in subset),passed=sum(r['classification'].startswith('passed') for r in subset)))
    f.table(OUT/'outcomes-by-temperature.csv',outcomes)
    f.table(OUT/'split-confirmations.csv',confirmations or [dict(cause='no resolved descents',confirmed=False)])
    write(OUT/'summary.json',dict(outcomes=outcomes,confirmation_attempts=len(confirmations),confirmed_paths=sum(r['confirmed'] for r in confirmations),confirmed_states=len({(r['record'],r['index']) for r in confirmations if r['confirmed']}),reported_descents=[r for r in rows if r['record']=='reported' and r['resolved_trials']],incomplete_states=incomplete,calls=load(OUT/'calls.json')))


def main():
    OUT.mkdir(exist_ok=False)
    (OUT/'inputs').mkdir()
    (OUT/'reference-pressure').mkdir()
    memory = int(next(x for x in open('/proc/meminfo') if x.startswith('MemAvailable')).split()[1])
    assert min(os.cpu_count(),memory//1_000_000)>=12, 'insufficient free memory for 12 chains'
    engine = load(CHAIN/'a6/spec.json')['engine']
    provenance = dict(base_commit=e.subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),engine_commit=f.s.ENGINE_COMMIT,engine=f.campaign.verify(dict(inputs=[],engine=engine)),wheel=engine,producer_hashes={str(p.relative_to(ROOT)):f.s.sha256(p) for p in (Path(__file__),SOURCE,Path(f.__file__),Path(f.s.__file__),Path(e.request.__code__.co_filename),Path(f.thermal.__file__))},command=sys.argv,available_memory_kib=memory,chains=12,threads=1,stage_wall_s=600,stage_cpu_s=3600,item_wall_s=300)
    provenance['parameters'] = {fit:dict(parameter_path=str(path.relative_to(ROOT)),parameter_bytes_sha256=f.s.sha256(path),runtime_mapping_sha256=hashlib.sha256(json.dumps(f.s.parameter_mapping(path),sort_keys=True).encode()).hexdigest()) for fit,path in FITS.items()}
    for fit,path in FITS.items():
        write(OUT/'inputs'/f'{fit}-parameters.json',load(path))
        write(OUT/'inputs'/f'{fit}-runtime.json',f.s.parameter_mapping(path))
    write(OUT/'provenance.json',provenance)
    assert e.ctypes.CDLL(None).prctl(36,1,0,0,0)==0
    started, cpu = time.monotonic(),e.cpu_used()
    stop = e.supervise([['reference',str(T)] for T in TEMPERATURES],'reference',started,cpu)
    states = grid(stop)
    for fit,path in FITS.items():
        write(OUT/fit/'fixed-parameters.json',f.s.parameter_mapping(path))
    e.run_searches(states,started,cpu)
    export(states,provenance)
    write(OUT/'input-hashes.json',{str(p.relative_to(OUT)):f.s.sha256(p) for directory in ('inputs','reference-pressure') for p in (OUT/directory).rglob('*') if p.is_file()})
    write(OUT/'timing.json',dict(wall_s=time.monotonic()-started,cpu_s=e.cpu_used()-cpu))


e.OUT, e.FITS, e.TEMPERATURES, e.__file__ = OUT, FITS, TEMPERATURES, str(Path(__file__).resolve())
adapt('supervise',[('cpu_start >= 1800','cpu_start >= 3600'),('cpu >= 1800','cpu >= 3600'),('sys.executable, __file__',"sys.executable, '-I', __file__")])
adapt('reduce',[('states=81','states=len(states)'),('scheduled_trials=729','scheduled_trials=9*len(states)'),('len(rows)==162 and len(trials)==1458','len(rows)==2*len(states) and len(trials)==18*len(states)'),('temperature_extrapolation=True',"temperature_extrapolation=state['temperature_extrapolation']")])
source = SOURCE.read_text().split('    commands = ',1)[1].split('    old = ',1)[0]
exec(compile('def run_searches(states,START,cpu_start):\n    commands = '+source,str(SOURCE),'exec'),vars(e))
if __name__=='__main__':
    assert [f.s.sha256(p) for p in FITS.values()]==list(EXPECTED)
    f.s.verify_wheel()
    if len(sys.argv)==1:
        main()
    elif sys.argv[1]=='reference':
        T,deadline = float(sys.argv[2]),float(sys.argv[3])
        for j,a in enumerate(LOADINGS):
            if time.monotonic()>=deadline:
                break
            path = OUT/'reference-pressure'/f'{T}-{j}.json'
            e.bounded(lambda: reference(T,a,path),path,deadline)
    else:
        e.chain(sys.argv[1],sys.argv[2],float(sys.argv[3]))
