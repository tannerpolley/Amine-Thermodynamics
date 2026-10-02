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
        if row['problem']=='F6':
            continue
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
                source=target['source_identity'], quantity='pressure' if kind=='p' else 'species', basis=target['basis'],
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
                'Bottinger 80C species':[r for r in rows if r['kind']=='packet' and r['quantity']=='species' and r['source']=='Bottinger2008' and round(r['temperature_K']-273.15)==80],
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
            carbonate_roles = {(float(r['temperature_C']),float(r['maxload_mol_per_mol_mea'])):r for r in csv.DictReader((CORRECTED/'accepted-wave/jakobsen-comparisons.csv').open())}
            for source,T,a,observed in compare.carbonate_refs():
                predicted = compare.model_carbonate(packet,T,a)
                role = carbonate_roles[(T,a)]
                carbonate.append(dict(problem=problem,source=source,temperature_C=T,loading=a,observed_carbonate_share=observed,predicted_carbonate_share=predicted,ratio=predicted/observed if predicted is not None and observed>0 else None,
                    summary_included=role['summary_included'],loading_convention=role['loading_convention'],model_loading_alignment=role['model_loading_alignment']))
        for label, rr in groups.items():
            if not rr:
                continue
            positive=[r for r in rr if r['ln_pred_over_obs'] is not None]
            values=compare.stats([r['ln_pred_over_obs'] for r in positive]) if positive else {}
            if problem=='F6' and len(positive)==len(rr):
                values=assessment.metrics([{**r,'quantity':r['quantity'],'ln_pred_over_obs':r['ln_pred_over_obs'], 'relative_error':r['predicted']/r['observed']-1,'numerically_complete':True} for r in rr])
            scores.append({**dict(problem=problem,group=label,rows=len(rr),positive_n=len(positive),cost=math.fsum(r['cost'] for r in rr)), **values})
    table(EVAL/'targets.csv',all_rows);table(EVAL/'scores.csv',scores);table(EVAL/'density.csv',density);table(EVAL/'jakobsen-carbonate-share.csv',carbonate)
    s.write_json(EVAL/'replay-checks.json',replays);s.write_json(EVAL/'not-evaluated.json',excluded)
    return replays


def present():
    """Tables and four figure data sets from retained results only; no state solves."""
    import refit
    choices=selected()
    replay=json.loads((EVAL/'replay-checks.json').read_text())
    summary=json.loads((OUT/'fit-summary.json').read_text())
    summary=[r for r in summary if r['problem']!='F6']
    for row in summary:
        row['replay']=replay[row['problem']]
        row['per_state_checks']='stationarity, element and charge balance passed; declared domain checked before evaluation'
    targets={t['identity']:t for o in s.load_state_packet(CORRECTED/'state-packet.json.gz')['observations'] for t in o['targets']}
    f6_starts=[]
    native_rows=[]
    for letter,i in zip('AB',(1,2)):
        raw=json.loads((OUT/f'F6-{letter}/runs'/f'slope-fixed-start-{i}/native-fit.json').read_text())
        data=[dict(problem='F6',start=letter,target=identity,source=targets[identity]['source_identity'],
              observed=targets[identity]['observed'],predicted=pred,quantity='pressure' if identity.endswith('-pco2') else 'species',
              species=identity.split('::')[-1] if '::' in identity else 'pCO2',scaled_residual=res,cost=.5*res**2)
              for identity,pred,res in zip(raw['targets'],raw['predictions'],raw['weighted_residuals'],strict=True)]
        native_rows.extend(data)
        aard={kind:compare.stats([math.log(r['predicted']/r['observed']) for r in data if r['quantity']==kind and r['observed']>0 and r['predicted']>0])['aard_percent'] for kind in ('pressure','species')}
        f6_starts.append(dict(start=letter,status=raw['status'],cost=raw['final_cost'],pressure_cost=math.fsum(r['cost'] for r in data if r['quantity']=='pressure'),
            species_cost=math.fsum(r['cost'] for r in data if r['quantity']=='species'),aard_percent=aard,
            coordinates=dict(zip(raw['coordinates'],raw['physical'],strict=True)),active_bounds=raw['active_bounds'],targets=len(data),
            observation_statuses_available=all(v=='Available' for v in raw['observation_statuses'])))
    gap=abs(f6_starts[0]['cost']-f6_starts[1]['cost'])/max(r['cost'] for r in f6_starts)
    summary.append(dict(problem='F6',starts=f6_starts,lower_complete_start=min(f6_starts,key=lambda r:r['cost'])['start'],
        relative_cost_difference=gap,start_agreement=gap<=1e-6,replay=replay['F6'],per_state_checks=summary[0]['per_state_checks']))
    s.write_json(OUT/'fit-summary.json',summary)
    table(OUT/'f6-fit-targets.csv',native_rows)
    source_stats=[]
    for letter in 'AB':
        rr=[r for r in native_rows if r['start']==letter]
        for source,species in sorted({(r['source'],r['species']) for r in rr}):
            part=[r for r in rr if (r['source'],r['species'])==(source,species)]
            positive=[r for r in part if r['observed']>0 and r['predicted']>0]
            source_stats.append(dict(problem='F6',start=letter,source=source,species=species,rows=len(part),positive_n=len(positive),
                cost=math.fsum(r['cost'] for r in part),**compare.stats([math.log(r['predicted']/r['observed']) for r in positive])))
    table(OUT/'f6-aard-by-source-species.csv',source_stats)
    evaluated=list(csv.DictReader((EVAL/'targets.csv').open()))
    errors=json.loads((OUT/'conditional-uncertainty.json').read_text())
    uncertainty_checks={}
    for problem in ('F1','F2'):
        raw=json.loads(Path(choices[problem]['raw']).read_text());ids=raw['coordinates']
        rr={r['target']:float(r['scaled_residual']) for r in evaluated if r['problem']==problem and r['kind']=='packet'}
        residual=np.array([rr[t] for t in raw['targets']]);scales=np.array([10. if i.endswith(refit.probe.SLOPE) else .01 for i in ids])
        J=np.array(raw['optimizer_jacobian']).reshape(141,5)/scales
        active=[ids.index(i) for i in raw['active_bounds']]
        proxy=SimpleNamespace(covariance=SimpleNamespace(active_bounds=active),physical=raw['physical'])
        value=refit.identifiability(proxy,J,residual,ids,[-.5,-.5,-.5,-1.,-1000.],[.5,.5,.5,1.,1000.])
        previous=errors[problem]
        delta=max(abs(value['conditional_standard_error'][k]/v-1) for k,v in previous['conditional_standard_error'].items())
        corr=float(np.max(np.abs(np.array(value['conditional_correlation'])-previous['conditional_correlation'])))
        uncertainty_checks[problem]=dict(max_relative_standard_error_difference=delta,max_abs_correlation_difference=corr,
            replay_passed=replay[problem]['passed'],retained_standard_error_table_sha256=s.sha256(OUT/'conditional-standard-errors.csv'),
            retained_correlation_table_sha256=s.sha256(OUT/'conditional-correlations.csv'))
    s.write_json(OUT/'uncertainty-replay-checks.json',uncertainty_checks)
    figures=OUT/'figure-data';figures.mkdir(exist_ok=True)
    for row in evaluated:
        row['unit']='Pa' if row['quantity']=='pressure' else 'mol/mol true liquid species'
        row['operator_label']=compare.HCO3_POOL_LABEL if compare.pooled_species(row['target']) else row['species']
    table(figures/'pressure.csv',[r for r in evaluated if r['problem'] in ('F1','F2','F6') and r['quantity']=='pressure'])
    table(figures/'speciation.csv',[r for r in evaluated if r['problem'] in ('F1','F2') and r['quantity']=='species'])
    mechanism=list(csv.DictReader((OUT/'activity-contributions/born-off-pressure-decomposition.csv').open()))
    table(figures/'born-off-mechanism.csv',mechanism)
    activity=list(csv.DictReader((OUT/'activity-contributions/state-activity-contributions.csv').open()))
    table(figures/'born-activity-sums.csv',[r for r in activity if r['quantity']=='Q' or (r['quantity']=='reaction sum' and r['reaction']=='OV')])
    pools=[r for r in evaluated if r['problem'] in ('F1','F2','F4','F5') and r['kind']=='packet']
    masks={problem:set(json.loads(Path(chosen['raw']).read_text())['targets']) for problem,chosen in choices.items()}
    for r in pools:
        r['fitted_target']=r['target'] in masks[r['problem']]
    table(figures/'pool-effect.csv',pools)
    pool_summary=[]
    for problem in ('F1','F2','F4','F5'):
        rr=[r for r in pools if r['problem']==problem and r['target'] in masks['F4']]
        added=[r for r in rr if r['target'] not in masks['F1']]
        pool_summary.append(dict(problem=problem,base141_cost=math.fsum(float(r['cost']) for r in rr if r['target'] in masks['F1']),
            pool18_cost=math.fsum(float(r['cost']) for r in added),pool18_aard_percent=compare.stats([float(r['ln_pred_over_obs']) for r in added])['aard_percent'],
            pool_role='fitted' if problem in ('F4','F5') else 'report-only'))
    table(figures/'pool-effect-costs.csv',pool_summary)
    s.write_json(figures/'input-hashes.json',{str(p.relative_to(OUT)):s.sha256(p) for p in figures.glob('*.csv')})


def render():
    """Notebook mechanism figure from the retained 47-row decomposition."""
    import pandas as pd
    import matplotlib.pyplot as plt
    rows=pd.read_csv(OUT/'figure-data/born-off-mechanism.csv')
    figures=OUT/'figures';figures.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),sharey=True,layout='constrained')
    series=[('dlnp','Total ln pressure','o','#222222'),('dQ','Activity sum Q','x','#0072B2'),
            ('dS','Speciation S','^','#D55E00'),('dH','Vapor/reference H','+','#009E73')]
    for ax,(T,group) in zip(axes,rows.groupby('nominal_T_K'),strict=True):
        ax.axhspan(-.3,.3,color='#777777',alpha=.12)
        ax.axhline(0,color='#777777',linewidth=.6)
        for column,label,marker,color in series:
            ax.scatter(group.loading,group[column],label=label,marker=marker,color=color,s=27)
        ax.set(xlabel='Loading (mol CO₂ / mol MEA)',title=f'Nominal {T-273.15:.0f} °C series, n={len(group)}')
    axes[0].set_ylabel('F3 − F1 change (dimensionless)')
    axes[1].legend(fontsize=8,loc='best')
    fig.suptitle('Born-off refit: activity-sum shifts exceed speciation shifts',fontsize=11)
    fig.savefig(figures/'born-off-mechanism.png',dpi=200)
    plt.close(fig)
    s.write_json(figures/'render-inputs.json',dict(data_sha256=s.sha256(OUT/'figure-data/born-off-mechanism.csv'),
        image_sha256=s.sha256(figures/'born-off-mechanism.png'),points=47,
        grey_band='±0.3 natural-log units: declared pressure residual scale, not an acceptance interval',
        semantics='Discrete computed states, no interpolation or physical-necessity claim'))


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
    if sys.argv[1:] == ['summarize']:
        choices=selected()
        retained=[json.loads(p.read_text()) for p in sorted((EVAL/'states').rglob('*.json'))]
        density=[{**json.loads(p.read_text()),'problem':p.name.split('-')[0],
                  'uncertainty_status':'general source estimate only; loaded-row uncertainty scope unbound'} for p in sorted(EVAL.glob('F*-density-*.json'))]
        _,groups=observations()
        excluded=[dict(problem=problem,kind='canonical',identity=o['identity'],temperature_K=o['request']['temperature']['value'],reason='not evaluated: outside declared reaction domain')
                  for problem in ('F1','F2','F6') for o in groups['canonical'] if not 293.15<=o['request']['temperature']['value']<=393.15]
        summarize(retained,density,choices,excluded)
    elif sys.argv[1:] == ['present']:
        present()
    elif sys.argv[1:] == ['render']:
        render()
    else:
        main()
