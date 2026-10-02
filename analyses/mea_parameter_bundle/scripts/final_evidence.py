"""Issue 154 fixed-record replay and scoring through the existing MEA owners."""
import copy
import csv
import json
import math
import os
from pathlib import Path
import runpy
import signal
import sys
import time
from types import SimpleNamespace
import concurrent.futures
import multiprocessing

from final_rerun import BUNDLE, OUT, module, s
sys.path.insert(0, str(BUNDLE / 'calibration-misfit'))
import probe
import compare
import numpy as np

ASSESSMENT = BUNDLE / 'results/temperature-reanchor-140/assessment.py'
CORRECTED = BUNDLE / 'results/source-corrections-152'
EVAL = OUT / 'evaluation'
assessment = module('assessment', ASSESSMENT)
low = module('low', BUNDLE / 'results/temperature-reanchor-140/low-temperature-fit.py')
NATIVE_BUILDER = s._engine_reaction_records


def table(path, rows):
    if rows:
        with path.open('w', newline='') as h:
            w = csv.DictWriter(h, list(dict.fromkeys(k for r in rows for k in r)), lineterminator='\n')
            w.writeheader()
            w.writerows(rows)


def selected():
    result = {}
    summary = json.loads((OUT / 'fit-summary.json').read_text())
    for row in summary:
        name = row['problem'] + '-' + row['lower_complete_start']
        raw = OUT / name / 'runs' / name / (name + '-fit.json')
        result[row['problem']] = dict(record=str(OUT / name / (name + '-diagnostic-parameters.json')), raw=str(raw))
    starts = [json.loads((OUT / f'F6-{letter}/slope-fixed-start-{i}-fit.json').read_text()) for letter, i in zip('AB', (1, 2))]
    if not all(x['native_complete'] for x in starts):
        raise RuntimeError('incomplete F6 fit; no evaluation or extra fit')
    best = min(range(2), key=lambda i: starts[i]['final_cost'])
    name = 'F6-' + 'AB'[best]
    result['F6'] = dict(record=str(OUT / name / f'slope-fixed-start-{best+1}-parameters.json'),
                        raw=str(OUT / name / f'runs/slope-fixed-start-{best+1}/native-fit.json'))
    return result


def binding(problem, path):
    probe.RECORD = Path(path)
    probe._BASE.clear()
    s._engine_reaction_records = NATIVE_BUILDER
    if problem == 'F6':
        native = json.loads((BUNDLE / 'results/temperature-reanchor-140/native-reaction-inputs.json').read_text())
        s._engine_reaction_records = lambda request, values: assessment.engine_records(native)


def job(problem, path, kind, observation):
    started = time.perf_counter()
    binding(problem, path)
    key = observation['identity'].replace(':', '_')
    s.RUNS = EVAL / 'cache' / problem / kind / key
    request = assessment.feed_start(observation['request'], s) if problem == 'F6' else observation['request']
    o = {**observation, 'request': request}
    record = next(probe.evaluate(states=[o]))
    check = low.check_state(record, o)
    if not check['complete'] or not all(math.isfinite(v) for v in record['predictions'].values()):
        raise RuntimeError(f'{problem} {kind} {o["identity"]}: {check}')
    record.update(problem=problem, kind=kind, numerical_checks=check)
    s.write_json(EVAL / 'states' / problem / kind / (key + '.json'), record)
    return record, time.perf_counter()-started


def density_job(problem, path, idx):
    binding(problem, path)
    name = f'{problem}-density-{idx}'
    os.environ.update(DENSITY_RECORD=path, DENSITY_SHA256=s.sha256(Path(path)),
                      DENSITY_OUTPUT=str(EVAL / (name + '.json')))
    sys.argv = ['replay.py', str(idx)]
    with (EVAL / (name + '.log')).open('w') as log:
        original = sys.stdout
        try:
            sys.stdout = log
            runpy.run_path(str(BUNDLE / 'results/density-current-record-123/replay.py'), run_name='__main__')
        finally:
            sys.stdout = original
    row = json.loads((EVAL / (name + '.json')).read_text())
    row.update(problem=problem, uncertainty_status='general source estimate only; loaded-row uncertainty scope unbound')
    return row


def observations():
    packet = s.load_state_packet(CORRECTED / 'state-packet.json.gz')['observations']
    probe.OBSERVATIONS = packet
    ids = json.loads((CORRECTED / 'accepted-wave/required-ids.json').read_text())
    groups = {'packet': [o for o in packet if o['identity'] in ids['packet']]}
    groups['canonical'] = probe.pressure_observations(lambda r: 'canonical:' + r['observation_id'] in ids['canonical'])
    transfer_ids = {i.removeprefix('transfer:') for i in ids['transfer']}
    groups['transfer'] = probe.pressure_observations(lambda r: 'canonical:' + r['observation_id'] in transfer_ids)
    for o in groups['transfer']:
        o['identity'] = 'transfer:' + o['identity']
    subsets = sorted({r['subset'] for r in csv.DictReader((ASSESSMENT.parent / 'never-accessed-vle-admission.csv').open()) if r['admitted'] == 'yes'})
    groups['wagner'] = [o for subset in subsets for o in assessment.wagner(SimpleNamespace(probe=probe, s=s), subset)]
    return packet, groups


def score_rows(problem, records):
    rows = []
    for rec in records:
        for target, (kind, identity, residual, ln) in zip(rec['targets'], compare.residuals(rec), strict=True):
            predicted = compare.predicted(rec, target)
            rows.append(dict(problem=problem, kind=rec['kind'], identity=rec['identity'], target=identity,
                source=target['source_identity'], quantity='pressure' if kind=='p' else 'species',
                species=identity.split('::')[-1] if kind=='s' else 'pCO2', temperature_K=rec['T'],
                loading=rec['feed'][0]/rec['feed'][1], observed=target['observed'], predicted=predicted,
                scaled_residual=residual, ln_pred_over_obs=ln if math.isfinite(ln) else None,
                cost=.5*residual**2, record_sha256=rec['record_sha256']))
    return rows


def summarize(records, density, choices, excluded):
    all_rows, scores, replays, carbonate = [], [], {}, []
    original = json.loads((OUT / 'fit-summary.json').read_text())
    for problem, chosen in choices.items():
        raw = json.loads(Path(chosen['raw']).read_text())
        subset = [r for r in records if r['problem']==problem]
        rows = score_rows(problem, subset)
        all_rows.extend(rows)
        mask = set(raw['targets'])
        fitted = [r for r in rows if r['kind']=='packet' and r['target'] in mask]
        cost = math.fsum(r['cost'] for r in fitted)
        check_rows = [r for r in subset if r['kind']=='packet' and any(t['identity'] in mask for t in r['targets'])]
        replay = dict(cost=cost, native_cost=raw['final_cost'], relative_error=abs(cost-raw['final_cost'])/abs(raw['final_cost']),
            states=len(check_rows), targets=len(fitted), pressure_cost=math.fsum(r['cost'] for r in fitted if r['quantity']=='pressure'),
            species_cost=math.fsum(r['cost'] for r in fitted if r['quantity']=='species'), parameter_sha256=s.sha256(Path(chosen['record'])),
            max_abs_stationarity=max(r['numerical_checks']['max_abs_stationarity'] for r in check_rows),
            max_abs_material_residual_mol=max(abs(v) for r in check_rows for v in r['numerical_checks']['material_residuals_mol']),
            max_abs_charge_residual_mol=max(abs(r['numerical_checks']['charge_residual_mol']) for r in check_rows))
        replay['passed'] = replay['relative_error'] <= 1e-8 and len(fitted)==len(raw['targets'])
        replays[problem]=replay
        s.write_json(EVAL / (problem+'-replay.json'), replay)
        with (EVAL / (problem+'-states.jsonl')).open('w') as h:
            for rec in check_rows:
                # Only the selected fit identities are transported to the decomposition mask.
                rec = {**rec, 'targets':[t for t in rec['targets'] if t['identity'] in mask]}
                h.write(json.dumps(rec)+'\n')
        if not replay['passed']:
            raise RuntimeError(f'replay mismatch: {problem}: {replay}')
        groups = {'fit pressure':[r for r in fitted if r['quantity']=='pressure'],
                  'fit species':[r for r in fitted if r['quantity']=='species']}
        if problem in ('F1','F2','F6'):
            canonical = [r for r in rows if r['kind']=='canonical']
            ids = json.loads((ASSESSMENT.parent/'assessment-row-ids.json').read_text())
            groups.update({'canonical 80C 21':[r for r in canonical if r['identity'].removeprefix('canonical:') in ids['primary_80c_pressure']],
                'Jou 80C':[r for r in rows if r['kind']=='packet' and r['quantity']=='pressure' and r['source']=='Jou1995' and round(r['temperature_K']-273.15)==80],
                '100-120C':[r for r in canonical if round(r['temperature_K']-273.15)>=100],
                'pooled 40-80C':[r for r in canonical if 40<=round(r['temperature_K']-273.15)<=80],
                'Matin pool report-only':[r for r in rows if r['kind']=='packet' and r['target'].startswith('Matin') and compare.pooled_species(r['target']) and compare.in_objective({'T':r['temperature_K'],'identity':r['identity']}, {'prediction_identity':'species'}, 80)]})
            for source in sorted({r['source'] for r in canonical}):
                groups['pooled 40-80C '+source] = [r for r in groups['pooled 40-80C'] if r['source']==source]
                groups['100-120C '+source] = [r for r in groups['100-120C'] if r['source']==source]
            for T in (353.15,392.15):
                groups[f'Wagner near {T}K']=[r for r in rows if r['kind']=='wagner' and (r['temperature_K']<355)==(T<355)]
            for w in (.15,.45):
                wanted={o['identity'] for o in probe.pressure_observations(lambda r: abs(float(r['MEA_weight_fraction'])-w)<1e-10)}
                groups[f'transfer {int(100*w)}wt%']=[r for r in rows if r['kind']=='transfer' and r['identity'].removeprefix('transfer:') in wanted]
            packet = {r['identity']:r for r in subset if r['kind']=='packet'}
            for source,T,a,observed in compare.carbonate_refs():
                predicted = compare.model_carbonate(packet,T,a)
                carbonate.append(dict(problem=problem,source=source,temperature_C=T,loading=a,observed_carbonate_share=observed,predicted_carbonate_share=predicted,ratio=predicted/observed if predicted is not None and observed>0 else None))
        for label, rr in groups.items():
            if not rr:
                continue
            positive=[r for r in rr if r['ln_pred_over_obs'] is not None]
            values=compare.stats([r['ln_pred_over_obs'] for r in positive]) if positive else {}
            if problem=='F6' and len(positive)==len(rr):
                values=assessment.metrics([{**r,'quantity':r['quantity'],'ln_pred_over_obs':r['ln_pred_over_obs'], 'relative_error':r['predicted']/r['observed']-1,'numerically_complete':True} for r in rr])
            scores.append(dict(problem=problem,group=label,rows=len(rr),positive_n=len(positive),cost=math.fsum(r['cost'] for r in rr),**values))
    table(EVAL/'targets.csv',all_rows);table(EVAL/'scores.csv',scores);table(EVAL/'density.csv',density);table(EVAL/'jakobsen-carbonate-share.csv',carbonate)
    s.write_json(EVAL/'replay-checks.json',replays);s.write_json(EVAL/'not-evaluated.json',excluded)
    return replays


def main():
    clock=time.perf_counter()
    EVAL.mkdir(parents=True,exist_ok=True)
    choices=selected(); packet, groups=observations()
    tasks=[]; excluded=[]
    for problem,chosen in choices.items():
        binding(problem,chosen['record'])
        raw=json.loads(Path(chosen['raw']).read_text());mask=set(raw['targets'])
        use=groups if problem in ('F1','F2','F6') else {'packet':[{**o,'targets':[t for t in o['targets'] if t['identity'] in mask]} for o in packet if any(t['identity'] in mask for t in o['targets'])]}
        for kind, oo in use.items():
            for o in oo:
                T=o['request']['temperature']['value']
                domain_failure = probe.reaction_domain_status(o) if problem!='F6' else None
                if domain_failure or not 293.15<=T<=393.15:
                    excluded.append(dict(problem=problem,kind=kind,identity=o['identity'],temperature_K=T,reason='not evaluated: outside declared reaction domain'))
                    continue
                tasks.append((problem,chosen['record'],kind,o))
    records=[];density=[]
    workers=len(os.sched_getaffinity(0))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        pending={pool.submit(job,*task):task[:3] for task in tasks}
        pending.update({pool.submit(density_job,problem,choices[problem]['record'],idx):('density',problem,idx) for problem in ('F1','F2','F6') for idx in range(4)})
        for future in concurrent.futures.as_completed(pending):
            key=pending[future]
            result=future.result()
            if key[0]=='density':density.append(result)
            else:records.append(result[0])
            print('complete',key,flush=True)
    records.sort(key=lambda r:(r['problem'],r['kind'],r['identity']))
    summarize(records,density,choices,excluded)
    s.write_json(EVAL/'execution.json',dict(wall_s=time.perf_counter()-clock,workers=workers,threads=1,states=len(records),density_states=len(density),choices=choices,wheel_sha256=s.ENGINE_WHEEL_SHA256))


if __name__=='__main__':
    main()
