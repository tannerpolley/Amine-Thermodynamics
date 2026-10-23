"""Issue 201 revision 2: paired finite phase searches; no fitting or solver changes."""
import ctypes
import importlib.metadata
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

START = time.monotonic()
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import final_evidence as f
from heat_evidence_170 import request

R = f.BUNDLE/'results'
OUT = R/'phase-extension-201'
J = R/'joint-recalibration-170'
FITS = {'A6': J/'amendment-6/joint-mea-water/held/fit/usable-budget-endpoint.json', 'A7': f.s.PARAMETERS}
TEMPERATURES = (353.15, 373.15, 393.15)
LOADINGS = (1e-5, .05, .1, .2, .25557798094241313, .3, .4, .5, .6)
FRACTIONS = (.5, .8, .95)
ANCHORS = ((313.15, 1e-5, 4825.512054880343), (318.15, .25557798094241313, 7398.160760169702), (333.15, .5, 76573.56849304347))
SCHEDULE = [(kind, seed) for kind in ('liquid', 'vapor') for seed in ('positive-neutral-base', 'near-pure-0', 'near-pure-1', 'near-pure-2', 'ideal-gas') if kind=='vapor' or seed!='ideal-gas']
load, write = f.campaign.load, f.s.write_json


def descendants(pid):
    found = []
    for child in Path(f'/proc/{pid}/task/{pid}/children').read_text().split():
        try:
            found.extend(descendants(int(child)))
        except FileNotFoundError:
            pass
    return [pid] + found


def cpu_used():
    ticks = os.sysconf('SC_CLK_TCK')
    total = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = total.ru_utime + total.ru_stime + time.process_time()
    for pid in descendants(os.getpid())[1:]:
        try:
            stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
            cpu += sum(int(stat[i]) for i in (11, 12, 13, 14))/ticks
        except FileNotFoundError:
            pass
    return cpu


def supervise(commands, stage, started, cpu_start):
    jobs, stopped = [], None
    for number, command in enumerate(commands):
        if time.monotonic()-started >= 600 or cpu_used()-cpu_start >= 1800:
            stopped = 'stage budget exhausted before dispatch'
            break
        prefix = OUT/f'command-{stage}-{number}-{time.monotonic_ns()}'
        argv = ['/usr/bin/time', '-f', '{"user_s":%U,"system_s":%S,"wall_s":%e,"max_rss_kib":%M}', '-o', str(prefix)+'.time.json', sys.executable, __file__, *command, str(started+600)]
        log = open(str(prefix)+'.log', 'w')
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT)
        jobs.append((process, log, dict(argv=argv, pid=process.pid, log=log.name)))
    while not stopped and any(p.poll() is None for p, _, _ in jobs):
        elapsed, cpu = time.monotonic()-started, cpu_used()-cpu_start
        if elapsed >= 600 or cpu >= 1800:
            stopped = 'stage wall ceiling' if elapsed >= 600 else 'stage CPU ceiling'
            break
        time.sleep(.02)
    stopping = time.monotonic()
    if stopped:
        roots = [p.pid for p, _, _ in jobs if p.poll() is None]
        for root in roots:
            for pid in descendants(root):
                try:
                    os.kill(pid, signal.SIGSTOP)
                except ProcessLookupError:
                    pass
        owned = list(dict.fromkeys(pid for root in roots for pid in descendants(root)))
        for pid in reversed(owned):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    for p, log, row in jobs:
        row['exitcode'] = p.wait()
        log.close()
        row['timing'] = load(Path(row['log'].replace('.log', '.time.json'))) if Path(row['log'].replace('.log', '.time.json')).stat().st_size else None
    if stopped:
        while True:
            try:
                os.waitpid(-1, 0)
            except ChildProcessError:
                break
    record = dict(stage=stage, stop=stopped, wall_s=time.monotonic()-started, cpu_s=cpu_used()-cpu_start, cleanup_s=time.monotonic()-stopping, terminated_pids=owned if stopped else [], host_load=os.getloadavg(), calls=[r for _, _, r in jobs])
    prior = load(OUT/'calls.json') if (OUT/'calls.json').exists() else []
    write(OUT/'calls.json', prior+[record])
    print(record, flush=True)
    return stopped


def bounded(action, path, deadline):
    write(path, dict(cause='not completed'))
    def child():
        try:
            action()
        except Exception as error:
            write(path, dict(load(path), cause=f'{type(error).__name__}: {error}'))
    timing = f.campaign.bounded_call(child, min(300., max(0., deadline-time.monotonic())))
    write(path, dict(load(path), timing=timing))


def reference(T, loading, path):
    mapping, data = load(OUT/'inputs/reference-runtime.json'), load(OUT/'inputs/engine-case7-reactions.json')
    model = f.epcsaft.Mixture(f.epcsaft.Parameters.from_mapping(mapping, components=f.s.COMPONENT_IDS))
    reactions = [f.eq.Reaction(nu, correlation=f.eq.ReactionLogPolynomial(a, 0., 0., 0., data['T_ref'], data['T_min'], data['T_max'], f.eq.EOS_STANDARD_STATE_ID)) for nu, a in zip(data['stoichiometry'], data['ln_k'], strict=True)]
    problem = f.eq.Problem(T=T, P=f.eq.Free(7398.16), feed=f.eq.Amounts({'carbon-dioxide':loading*9.7292821, 'monoethanolamine':9.7292821, 'water':76.9751925}), reactions=reactions, row_tolerance=1e-10,
        phases=[f.eq.Phase('L', kind='liquid'), f.eq.Phase('V', kind='vapor', support=f.s.COMPONENT_IDS[:3], amount=f.eq.Pinned(0.))])
    result = f.eq.solve_equilibrium(model, problem)
    payload = f.phase_payload(model, problem, result)
    admitted = result.success and result.requested_tolerance_met and math.isfinite(result.pressure) and 1 <= result.pressure <= 1e7 and result.amounts[0]>0 and result.amounts[1]==0 and max(map(abs, payload['raw_residuals']))<=1e-10 and result.reduced_hessian_minimum>=0 and all(v>0 for v in payload['pressure_density_derivatives'])
    write(path, dict(temperature_K=T, loading=loading, result=payload, admitted=admitted, cause='' if admitted else 'reference admission failed'))


def split(mapping, old, index, trial, path):
    model = f.epcsaft.Mixture(f.epcsaft.Parameters.from_mapping(mapping), thermochemistry=f.thermal.record())
    phases = [f.eq.Phase(p['identity'], kind=p['role'], support=p['support']) for p in old['final']['phases']]
    support = [f.s.COMPONENT_IDS[i] for i in trial['phase']['support']]
    phases.append(f.eq.Phase('additional', kind=trial['phase']['kind'], support=support))
    problem = f.flash_problem(request(mapping,313.15,.11), old['loading'], old['temperature_K'], old['pressure_Pa'], phases)
    cursor, amounts, compositions, packings = 0, [], [], []
    for phase in phases:
        count = len(phase.support)
        compositions.append([math.exp(v) for v in trial['split_coordinates'][cursor:cursor+count]])
        amounts.append(trial['split_coordinates'][cursor+count])
        packings.append(math.exp(trial['split_coordinates'][cursor+count+1]))
        cursor += count+2
    assert cursor==len(trial['split_coordinates'])
    begin = f.eq.EquilibriumStart(compositions=compositions, amounts=amounts, packing_fractions=packings)
    batch = f.eq.solve_equilibrium_starts(model,problem,[begin],f.eq.EquilibriumWorkLimits(attempts=1,attempt_iterations=400,iterations=400))
    result = batch.results[0]
    row = dict(index=old['index'], native_trial_index=index, phase=trial['phase'], seed=trial['seed'], selected=batch.selected, causes=list(batch.causes), original_G_over_RT=old['final']['objective'], finite_split=trial['quantities'], confirmed=False)
    if result is not None:
        payload = f.phase_payload(model,problem,result)
        delta = result.objective-old['final']['objective']
        row.update(result=payload, delta_G_over_RT=delta, delta_G_J=delta*8.31446261815324*old['temperature_K'])
        row['confirmed'] = result.success and result.requested_tolerance_met and delta<0 and max(map(abs,payload.get('raw_residuals',[math.inf])))<=1e-10 and result.reduced_hessian_minimum>0 and all(a>0 for a in result.amounts) and all(v>0 for v in payload.get('pressure_density_derivatives',[]))
        write(path,row)
        if result.success:
            row['stability'] = f.stability(model,problem,result)
    write(path,row)


def chain(mode, label, deadline):
    if mode in ('anchors', 'reference'):
        cases = ANCHORS if mode=='anchors' else [(float(label), a, None) for a in LOADINGS]
        for i, (T, a, expected) in enumerate(cases):
            path = OUT/'reference-pressure'/f'{mode}-{label}-{i}.json'
            bounded(lambda: reference(T,a,path),path,deadline)
            row = load(path)
            if expected is not None and (not row.get('admitted') or abs(row['result']['pressure']/expected-1)>1e-8):
                raise RuntimeError(f'anchor reproduction failed: {path}')
    else:
        fit, T = label.split(':')
        mapping = f.s.parameter_mapping(FITS[fit])
        if mode=='screen':
            indices = [r['index'] for r in load(OUT/'inputs/states.json') if r['temperature_K']==float(T) and r['admitted']]
            if indices:
                f.phase_family(mapping,request(mapping,313.15,.11),OUT/'inputs/family-points.txt',f.s.sha256(OUT/'inputs/family-points.txt'),OUT/fit,indices,deadline)
        else:
            for item in load(OUT/fit/'split-summary.json'):
                if item['temperature_K']==float(T) and item['representative']==item['native_trial_index']:
                    old = load(OUT/fit/f"point-{item['index']}.json")
                    trial = old['stability'][0]['trials'][item['native_trial_index']]
                    bounded(lambda: split(mapping,old,item['native_trial_index'],trial,OUT/item['path']),OUT/item['path'],deadline)


def reduce(states, stop):
    rows, trials, confirmations = [], [], []
    for fit in FITS:
        for state in states:
            path = OUT/fit/f"point-{state['index']}.json"
            row = load(path) if path.exists() else dict(state, cause=stop or state['cause'] or 'chain did not return state')
            if not path.exists():
                write(path,row)
            returned = [t for report in row.get('stability',[]) for t in report['trials']]
            descending = [(i,t) for i,t in enumerate(returned) if t['resolved_descent']]
            cause = row.get('failure') or row.get('cause') or ('state deadline' if row.get('timing',{}).get('interrupted') else '')
            classification = f.phase_classification(row)
            if classification.startswith('passed') and len(returned)!=9:
                classification = 'unresolved'
            if not cause and classification in ('failed','unresolved'):
                cause = 'resolved descent' if descending else 'parent numerical checks' if classification=='failed' else 'incomplete or unresolved trial/bubble evidence'
            summary = dict(state, record=fit, classification=classification, cause=cause, final_success=row.get('final',{}).get('success',False), resolved_trials=len(descending), failed_trial_optimizers=sum(not t['optimizer']['success'] for t in returned), missing_trials=9-len(returned), source_path=str(path.relative_to(R)), temperature_extrapolation=True,executed='timing' in row,parent_numerical_failure=state['admitted'] and not row.get('final',{}).get('success',False),trial_unresolved=sum(t['evidence'] in ('unresolved','indeterminate','negative_plane_without_positive_donor') for t in returned))
            rows.append(summary)
            for kind, seed in SCHEDULE:
                matching = [(i,t) for i,t in enumerate(returned) if t['phase']['kind']==kind and t['seed']==seed]
                assert len(matching)<=1
                i, trial = matching[0] if matching else (None,{})
                trials.append(dict(record=fit,index=state['index'],temperature_K=state['temperature_K'],phase_kind=kind,seed=seed,native_trial_index=i,status='returned' if trial else 'unavailable' if not state['admitted'] else 'not_run',support=trial.get('phase',{}).get('support'),cause=(trial['optimizer']['message'] if not trial['optimizer']['success'] else trial['evidence']) if trial else cause or 'native duplicate-root suppression',resolved_descent=trial.get('resolved_descent'),optimizer_success=trial.get('optimizer',{}).get('success'),evidence=trial.get('evidence'),**trial.get('quantities',{})))
            kept = []
            for i, trial in sorted(descending,key=lambda it:it[1]['quantities']['split_delta_g_over_rt']):
                same = next((j for j,k in kept if trial['phase']['kind']==k['phase']['kind'] and trial['phase']['support']==k['phase']['support'] and max(abs(a-b) for a,b in zip(trial['composition'],k['composition'],strict=True))<=1e-6),None)
                representative = i if same is None else same
                if same is None:
                    kept.append((i,trial))
                confirmations.append(dict(record=fit,index=state['index'],temperature_K=state['temperature_K'],native_trial_index=i,phase_kind=trial['phase']['kind'],support=trial['phase']['support'],seed=trial['seed'],representative=representative,path=f'{fit}/split-seeded-{state["index"]}-trial-{representative}.json'))
        subset = [r for r in rows if r['record']==fit]
        write(OUT/fit/'reduction.json',subset)
        write(OUT/fit/'summary.json',dict(states=81,scheduled_trials=729,counts={k:sum(r['classification']==k for r in subset) for k in ('failed','unresolved','passed-two-phase','passed-single-liquid')},points_sha256=f.s.sha256(OUT/'inputs/family-points.txt')))
        write(OUT/fit/'split-summary.json',[r for r in confirmations if r['record']==fit])
    assert len(rows)==162 and len(trials)==1458
    f.table(OUT/'phase-family.csv',rows)
    f.table(OUT/'trials.csv',trials)
    return rows, trials, confirmations


def main():
    OUT.mkdir(exist_ok=False)
    for directory in ('inputs','reference-pressure','A6','A7'):
        (OUT/directory).mkdir()
    expected = dict(zip([*FITS.values(),R/'a7-paper-evidence/phase-family.csv',J/'amendment-6/inputs/revision-3/phase/family-points.txt'],['ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7','e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e','fd16142967e4fef1408b907a40839780923bef381da6a685eac8d9ae4b8db6a7','6e1231d9506fd6dd9e965a64120ff952cebf1c4778da5d66cfb0f888e8b7f44b']))
    assert all(f.s.sha256(p)==h for p,h in expected.items())
    f.s.verify_wheel()
    for name, checksum in [('parameters','2ea3b41485a98d2cf49add620b87bb05fc5a275cdd132c1cdbb0cfc5f07f2ca4'),('reactions','2058458ca473bbc7b3deef77c67a9bb5124011c0bd5d28ba3a24da5d9c0e22a4')]:
        path = OUT/'inputs'/f'engine-case7-{name}.json'
        path.write_bytes(subprocess.check_output(['git','show',f'5ebcb37:analyses/mea_parameter_bundle/results/permittivity-screen-172/inputs/{path.name}']))
        assert f.s.sha256(path)==checksum
    mapping = load(OUT/'inputs/engine-case7-parameters.json')
    mapping['topology']['no_cross_association'] = [dict(component_id_a='carbon-dioxide',component_id_b='monoethanolamine',provenance=dict(source_id=mapping['document_id'],locator='packet 3: no CO2/MEA edge'))]
    write(OUT/'inputs/reference-runtime.json',mapping)
    write(OUT/'inputs/study.json',dict(issue=201,design_sha256='fb771344530184e34fe80c884cbd552780472db9d8abab8c217adc9945992b49',readiness='GPT-6 Astra xhigh round 2 Ready; parent instruction',temperatures_K=TEMPERATURES,loadings=LOADINGS,fractions=FRACTIONS,feed_mol=dict(MEA=9.7292821,water=76.9751925),row_tolerance=1e-10,state_wall_s=300,stage_wall_s=600,stage_cpu_s=1800,workers=6,reference_workers=3,pressure_fit_temperature_K=[313.,333.15],temperature_extrapolation=True,topology_change='explicit absent CO2-MEA cross edge only; baseline.py:139-144 at Engine 8298c602'))
    provenance = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),python=sys.version,libraries={k:importlib.metadata.version(k) for k in ('epcsaft','numpy','scipy')},wheel_path=str(f.s.installed_wheel()),wheel_sha256=f.s.ENGINE_WHEEL_SHA256,engine_commit=f.s.ENGINE_COMMIT,producers={str(p):f.s.sha256(p) for p in (Path(__file__),Path(f.__file__))},inputs={str(p):h for p,h in expected.items()})
    write(OUT/'provenance.json',provenance)
    cpu_start = 0.
    assert ctypes.CDLL(None).prctl(36,1,0,0,0)==0  # Reap only this supervisor's orphaned solve children.
    stop = supervise([['anchors','all']],'reference-and-screen',START,cpu_start)
    anchors = [load(p) if p.exists() else {} for i in range(3) for p in [OUT/'reference-pressure'/f'anchors-all-{i}.json']]
    if stop or any(not r.get('admitted') or abs(r['result']['pressure']/a[2]-1)>1e-8 for r,a in zip(anchors,ANCHORS)):
        raise RuntimeError('anchor qualification stopped dependent work; diagnose retained reference solves')
    stop = supervise([['reference',str(T)] for T in TEMPERATURES],'reference-and-screen',START,cpu_start)
    states, references = [], []
    for j, a in enumerate(LOADINGS):
        for T in TEMPERATURES:
            path = OUT/'reference-pressure'/f'reference-{T}-{j}.json'
            ref = load(path) if path.exists() else dict(cause=stop or 'reference chain stopped')
            P = ref.get('result',{}).get('pressure')
            for fraction in (1., *FRACTIONS):
                pressure = P*fraction if P is not None else None
                domain = dict(diagnostic_interval=pressure is not None and 10<=pressure<=300000,candidate_interval=pressure is not None and 1<=pressure<=1e7,observed_total_interval=pressure is not None and {353.15:1e5,373.15:1.1e5,393.15:2.5e5}[T]<=pressure<={353.15:1e6,373.15:1e6,393.15:3e6}[T])
                references.append(dict(temperature_K=T,loading=a,fraction=fraction,pressure_Pa=pressure,reference_path=str(path.relative_to(OUT)),admitted=ref.get('admitted',False) and domain['candidate_interval'],cause=ref.get('cause','') or ('' if domain['candidate_interval'] else 'pressure outside candidate interval or unavailable'),**domain))
                if fraction!=1.:
                    states.append(dict(references[-1],index=len(states),temperature_extrapolation=True))
    f.table(OUT/'reference-pressure/reference-pressures.csv',references)
    write(OUT/'inputs/states.json',states)
    f.table(OUT/'inputs/states.csv',states)
    (OUT/'inputs/family-points.txt').write_text(''.join(f'{s["loading"]!r} {s["temperature_K"]!r} {s["pressure_Pa"] if s["pressure_Pa"] is not None else "nan"}\n' for s in states))
    for fit,path in FITS.items():
        write(OUT/fit/'provenance.json',dict(parameter_path=str(path),parameter_bytes_sha256=f.s.sha256(path),mapping_sha256=__import__('hashlib').sha256(json.dumps(f.s.parameter_mapping(path),sort_keys=True).encode()).hexdigest(),states_sha256=f.s.sha256(OUT/'inputs/states.csv'),**provenance))
    commands = [[mode,f'{fit}:{T}'] for fit in FITS for T in TEMPERATURES for mode in ['screen']]
    stop = stop or supervise(commands,'reference-and-screen',START,cpu_start)
    rows,trials,confirmations = reduce(states,stop)
    confirm_start, confirm_cpu = time.monotonic(),cpu_used()
    confirm_stop = supervise([['confirm',f'{fit}:{T}'] for fit in FITS for T in TEMPERATURES if any(c['record']==fit and c['temperature_K']==T for c in confirmations)],'confirmation',confirm_start,confirm_cpu)
    for row in confirmations:
        path = OUT/row['path']
        result = load(path) if path.exists() else dict(confirmed=False,cause=confirm_stop or 'confirmation not returned')
        row.update(confirmed=result.get('confirmed',False),cause=result.get('cause') or '; '.join(result.get('causes',[])),delta_G_over_RT=result.get('delta_G_over_RT'),delta_G_J=result.get('delta_G_J'))
    for fit in FITS:
        write(OUT/fit/'split-summary.json',[r for r in confirmations if r['record']==fit])
    f.table(OUT/'split-confirmations.csv',confirmations or [dict(cause='no resolved descents',confirmed=False)])
    counts = [dict(record=fit,temperature_K=T,states=27,scheduled_trials=243,descent_states=sum(r['resolved_trials']>0 for r in rows if r['record']==fit and r['temperature_K']==T),**{k:sum(r['classification']==k for r in rows if r['record']==fit and r['temperature_K']==T) for k in ('failed','unresolved','passed-two-phase','passed-single-liquid')},unavailable_states=sum(not r['admitted'] for r in rows if r['record']==fit and r['temperature_K']==T),executed_states=sum(r['executed'] for r in rows if r['record']==fit and r['temperature_K']==T),parent_numerical_failures=sum(r['parent_numerical_failure'] for r in rows if r['record']==fit and r['temperature_K']==T),failed_trial_optimizers=sum(r['failed_trial_optimizers'] for r in rows if r['record']==fit and r['temperature_K']==T),trial_unresolved=sum(r['trial_unresolved'] for r in rows if r['record']==fit and r['temperature_K']==T),returned_trials=sum(t['status']=='returned' for t in trials if t['record']==fit and t['temperature_K']==T),resolved_trials=sum(t['resolved_descent'] is True for t in trials if t['record']==fit and t['temperature_K']==T)) for fit in FITS for T in TEMPERATURES]
    f.table(OUT/'counts-by-temperature.csv',counts)
    old = list(f.csv.DictReader((R/'a7-paper-evidence/phase-family.csv').open()))
    f.table(OUT/'phase-family-combined.csv',[dict(r,family='original-73',combined_index=int(r['index']),source_path='a7-paper-evidence/phase-family.csv') for r in old]+[dict(r,family='extension-81',combined_index=73+r['index']) for r in rows])
    assert all(f.s.sha256(p)==h for p,h in expected.items())
    write(OUT/'input-hashes.json',{str(p.relative_to(OUT)):f.s.sha256(p) for p in (OUT/'inputs').iterdir()})
    print(counts,flush=True)


if __name__=='__main__':
    chain(sys.argv[1],sys.argv[2],float(sys.argv[3])) if len(sys.argv)>1 else main()
