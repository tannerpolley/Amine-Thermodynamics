"""Issue 154 fixed-record replay and scoring through the existing MEA owners."""
import copy
import csv
import json
import math
import importlib.util
import os
from pathlib import Path
import runpy
import signal
import sys
import time
from types import SimpleNamespace
import concurrent.futures
import multiprocessing

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import shared_evaluation as s
BUNDLE = Path(__file__).resolve().parents[1]
OUT = BUNDLE / 'results/final-rerun'

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
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


def selected(output_dir=OUT, heat_rows=None, documents=None):
    if documents is not None:
        return documents
    OUT = Path(output_dir)
    result = {}
    summary = json.loads((OUT / 'fit-summary.json').read_text())
    if heat_rows is not None:
        choices = {r['problem']: dict(record=r['parameters'], raw=r['fit']) for r in summary}
        control = BUNDLE / 'results/density-cp-160/D1-evidence'
        choices['F1-no-heat'] = dict(record=str(control/'F1-double-prime-candidate-parameters.json'), raw=str(control/'F1-A/native-fit.json'))
        return choices
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


def job(problem, path, kind, observation, *, output_dir=OUT):
    EVAL = Path(output_dir) / 'evaluation'
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


def summarize(records, density, choices, excluded, *, output_dir=OUT, heat_rows=None):
    OUT = Path(output_dir)
    EVAL = OUT / 'evaluation'
    all_rows, scores, replays, carbonate = [], [], {}, []
    original = json.loads((OUT / 'fit-summary.json').read_text())
    for problem, chosen in choices.items():
        binding(problem, chosen['record'])
        raw = json.loads(Path(chosen['raw']).read_text())
        subset = [r for r in records if r['problem']==problem]
        rows = score_rows(problem, subset)
        all_rows.extend(rows)
        mask = set(raw['targets'])
        fitted = [r for r in rows if r['kind']=='packet' and r['target'] in mask]
        cost = math.fsum(r['cost'] for r in fitted)
        if heat_rows is not None and problem != 'F1-no-heat':
            from fit_observations import heat_items, predict
            mapping = s.parameter_mapping(Path(chosen['record']))
            from heat_evidence_170 import request
            values = predict(mapping, heat_items(mapping, probe.epcsaft.Parameters.from_mapping(mapping), heat_rows, request(mapping, 313.15, .11)))
            heats = [dict(problem=problem, kind='heat', identity=r['record_id'], target=r['record_id'],
                source='Vinjarapu2024', quantity='heat', basis='J/mol CO2', species='',
                temperature_K=r['temperature_K'], loading=r['alpha_final'], observed=r['observed_addition_enthalpy_J_per_mol_CO2'],
                predicted=y.value, scaled_residual=y.residual,
                ln_pred_over_obs=None, cost=.5*y.residual**2,
                record_sha256=s.sha256(Path(chosen['record']))) for r,y in zip(heat_rows,values,strict=True)]
            all_rows.extend(heats)
            fitted += heats
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
        if heat_rows is not None and problem != 'F1-no-heat':
            groups['fit heat'] = heats
        if problem in ('F1','F2','F6','F1-no-heat'):
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


def present(*, output_dir=OUT, choices=None, heat_rows=None, campaign_dir=None):
    """Tables and four figure data sets from retained results only; no state solves."""
    OUT = Path(output_dir)
    EVAL = OUT / 'evaluation'
    import refit
    choices = selected(OUT, heat_rows) if choices is None else choices
    replay=json.loads((EVAL/'replay-checks.json').read_text())
    summary=json.loads((OUT/'fit-summary.json').read_text())
    f6_choice = next(r for r in summary if r['problem']=='F6')
    summary=[r for r in summary if r['problem']!='F6']
    for row in summary:
        row['replay']=replay[row['problem']]
        row['per_state_checks']='stationarity, element and charge balance passed; declared domain checked before evaluation'
    targets={t['identity']:t for o in s.load_state_packet(CORRECTED/'state-packet.json.gz')['observations'] for t in o['targets']}
    packet_target_ids = set(targets)
    if heat_rows is not None:
        targets.update({r['record_id']: dict(source_identity='Vinjarapu2024', observed=r['observed_addition_enthalpy_J_per_mol_CO2']) for r in heat_rows})
    f6_starts=[]
    native_rows=[]
    for letter,i in zip('AB',(1,2)):
        raw=json.loads((Path(campaign_dir)/'F6'/letter/'native-fit.json' if heat_rows is not None else OUT/f'F6-{letter}/runs'/f'slope-fixed-start-{i}/native-fit.json').read_text())
        data=[dict(problem='F6',start=letter,target=identity,source=targets[identity]['source_identity'],
              observed=targets[identity]['observed'],predicted=pred,quantity='heat' if identity not in packet_target_ids else 'pressure' if identity.endswith('-pco2') else 'species',
              species='' if identity not in packet_target_ids else identity.split('::')[-1] if '::' in identity else 'pCO2',scaled_residual=res,cost=.5*res**2)
              for identity,pred,res in zip(raw['targets'],raw['predictions'],raw['weighted_residuals'],strict=True)]
        native_rows.extend(data)
        aard={kind:compare.stats([math.log(r['predicted']/r['observed']) for r in data if r['quantity']==kind and r['observed']>0 and r['predicted']>0])['aard_percent'] for kind in ('pressure','species')}
        f6_starts.append(dict(start=letter,status=raw['status'],cost=raw['final_cost'],pressure_cost=math.fsum(r['cost'] for r in data if r['quantity']=='pressure'),
            species_cost=math.fsum(r['cost'] for r in data if r['quantity']=='species'),aard_percent=aard,
            coordinates=dict(zip(raw['coordinates'],raw['physical'],strict=True)),active_bounds=raw['active_bounds'],targets=len(data),
            observation_statuses_available=all(v=='Available' for v in raw['observation_statuses'])))
    gap=abs(f6_starts[0]['cost']-f6_starts[1]['cost'])/max(r['cost'] for r in f6_starts)
    summary.append(dict(f6_choice,starts=f6_starts,lower_complete_start=min(f6_starts,key=lambda r:r['cost'])['start'],
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
                cost=math.fsum(r['cost'] for r in part),**(compare.stats([math.log(r['predicted']/r['observed']) for r in positive]) if positive else {})))
    table(OUT/'f6-aard-by-source-species.csv',source_stats)
    evaluated=list(csv.DictReader((EVAL/'targets.csv').open()))
    errors=json.loads((OUT/'conditional-uncertainty.json').read_text())
    uncertainty_checks={}
    for problem in ('F1','F2'):
        raw=json.loads(Path(choices[problem]['raw']).read_text());ids=raw['coordinates']
        rr={r['target']:float(r['scaled_residual']) for r in evaluated if r['problem']==problem and r['kind'] in ('packet','heat')}
        residual=np.array([rr[t] for t in raw['targets']]);scales=np.array([10. if i.endswith(refit.probe.SLOPE) else .01 for i in ids])
        J=np.array(raw['optimizer_jacobian']).reshape(len(raw['targets']),5)/scales
        active=[ids.index(i) if isinstance(i,str) else i for i in raw['active_bounds']]
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
        row['unit']='Pa' if row['quantity']=='pressure' else 'J/mol CO2' if row['quantity']=='heat' else 'mol/mol true liquid species'
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
        if heat_rows is not None:
            heat_cost = math.fsum(float(r['cost']) for r in evaluated if r['problem']==problem and r['quantity']=='heat')
            pool_summary[-1].update(heat8_cost=heat_cost, base149_cost=pool_summary[-1]['base141_cost']+heat_cost)
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


from epcsaft import equilibrium as eq
import epcsaft
import fit_campaign as campaign
import verify_reference_calorics as thermal


def flash_problem(request, loading, T, P, phases=None):
    return eq.Problem(T=T, P=P, feed=eq.Amounts({'monoethanolamine':9.7292821,
        'water':76.9751925, 'carbon-dioxide':loading*9.7292821}),
        phases=phases or [eq.Phase('L',kind='liquid',support=s.COMPONENT_IDS),
            eq.Phase('V',kind='vapor',support=s.COMPONENT_IDS[:3])],
        reactions=s._problem_from_request(request).reactions, neutral_reference=s._neutral_reference(request),row_tolerance=1e-10)


def phase_payload(model, problem, result):
    fields = ('success message solver_status requested_tolerance_met temperature pressure amounts mole_fractions '
        'molar_densities packing_fractions coordinates residuals classified_residuals multipliers constraint_multipliers '
        'iterations evaluations hessian_calls objective reduced_hessian_minimum jacobian_rank generic_nullity').split()
    row = {k:s._jsonable(getattr(result,k)) for k in fields}
    row['convergence'] = {k:s._jsonable(getattr(result.convergence,k)) for k in
        ('residual floor amplification contraction iterations evaluations stop').split()}
    row['closure_criterion'] = result.convergence.criterion.value if result.convergence.criterion else None
    if model is not None and result.success:
        point = eq.compile_problem(model,problem).evaluate(result.coordinates)
        row.update(raw_residuals=list(point.values),raw_objective=point.objective,roundoff_floor=point.floor,
            phases=[s._phase_payload(problem,result,i,len(model.component_ids)) for i in range(result.phase_count)],
            row_kinds=[r.kind.name for r in result.rows])
        row['pressure_density_derivatives'] = [model.state(result.temperature[0],rho=result.molar_densities[i],
            x=dict(zip(model.component_ids,result.phase_mole_fractions(i),strict=True))).pressure_density_derivative for i in range(result.phase_count)]
    return row


def stability(model, problem, result):
    options = eq.StabilityOptions()
    trials = copy.copy(problem)
    trials.phases = [eq.Phase('trial-L',kind='liquid',support=s.COMPONENT_IDS),eq.Phase('trial-V',kind='vapor',support=s.COMPONENT_IDS[:3])]
    options.trials = trials._native(model).phases
    report = eq.stability_test(eq.compile_problem(model,problem),result,options)
    payload = {k:s._jsonable(getattr(report,k)) for k in
        ('completed message candidate_coordinates standard_over_rt plane_over_rt present_phases work').split()}
    payload['trials'] = []
    for trial in report.trials:
        record = {k:s._jsonable(getattr(trial,k)) for k in ('seed evidence message raw_coordinates raw_residuals '
            'composition split_coordinates basis row_transformation quantities split_checks donor resolved_descent').split()}
        record.update(phase=dict(name=trial.phase.name,kind=trial.phase.kind.name.lower(),support=list(trial.phase.support)),
            optimizer=phase_payload(None,None,trial.optimizer))
        payload['trials'].append(record)
    return payload


def phase_classification(row):
    state, reports = row.get('final'), row.get('stability',[])
    if any(t['resolved_descent'] for r in reports for t in r['trials']):
        return 'failed'
    if state is None or not state['success'] or not state['requested_tolerance_met']:
        return 'failed'
    if 'raw_residuals' in state and (max(map(abs,state['raw_residuals']),default=0.)>1e-10
        or state['reduced_hessian_minimum']<0 or any(v<=0 for v in state['pressure_density_derivatives'])
        or any(v<0 for v in state['amounts'])):
        return 'failed'
    if (len(reports)!=1 or not reports[0]['completed'] or not reports[0]['trials']
        or {t['phase']['kind'] for t in reports[0]['trials']}!={'liquid','vapor'}
        or any(not t['optimizer']['success'] or t['evidence'] in ('unresolved','indeterminate','negative_plane_without_positive_donor') for t in reports[0]['trials'])
        or 'raw_residuals' not in state or row.get('bubble_pressure_Pa') is None or row.get('pressure_uncertainty_Pa') is None):
        return 'unresolved'
    if abs(row['pressure_Pa']-row['bubble_pressure_Pa'])<=row['pressure_uncertainty_Pa']:
        return 'unresolved'
    expected = 2 if row['pressure_Pa']<row['bubble_pressure_Pa'] else 1
    if len(state['amounts'])!=expected:
        return 'unresolved'
    return 'passed-two-phase' if expected==2 else 'passed-single-liquid'


def recover(model, problem, row, retained, out):
    nearest = sorted((r for r in retained if r['temperature_K']==row['temperature_K'] and r.get('final',{}).get('success') and len(r['final']['amounts'])==2),
        key=lambda r:abs(r['loading']-row['loading'])+abs(math.log(r['pressure_Pa']/row['pressure_Pa'])))[:2]
    if not nearest:
        return None
    starts = [eq.EquilibriumStart(coordinates=r['final']['coordinates']) for r in nearest]
    batch = eq.solve_equilibrium_starts(model,problem,starts,eq.EquilibriumWorkLimits(attempts=2,attempt_iterations=400,iterations=800))
    row['nearest_indices'] = [r['index'] for r in nearest]
    row['nearest_causes'] = list(batch.causes)
    row['nearest_selected'] = batch.selected
    row['attempts'].extend(None if r is None else phase_payload(model,problem,r) for r in batch.results)
    s.write_json(out,row)
    return batch.results[batch.selected] if batch.selected is not None else None


def diagnose(model, request, row, out):
    problem = flash_problem(request,row['loading'],row['temperature_K'],row['pressure_Pa'],[eq.Phase('L',kind='liquid',support=s.COMPONENT_IDS)])
    liquid = eq.solve_equilibrium(model,problem)
    row['liquid'] = phase_payload(model,problem,liquid)
    s.write_json(out,row)
    if not liquid.success:
        return problem,liquid,None
    problem.phases = [eq.Phase('L',kind='liquid',support=s.COMPONENT_IDS,composition_guess=liquid.phase_mole_fractions(0),packing_guess=liquid.packing_fractions[0]),
        eq.Phase('V',kind='vapor',support=s.COMPONENT_IDS[:3],amount=eq.Pinned(0.))]
    problem.P = eq.Free(row['pressure_Pa'])
    bubble = eq.solve_equilibrium(model,problem)
    row['bubble'] = phase_payload(model,problem,bubble)
    if bubble.success:
        row['bubble_pressure_Pa'] = bubble.pressure[0]
        row['pressure_uncertainty_Pa'] = bubble.pressure[0]*max(bubble.convergence.residual,bubble.convergence.floor or 0.,bubble.convergence.criterion.value if bubble.convergence.criterion else 0.)
    s.write_json(out,row)
    return problem,liquid,bubble


def bubble_recover(model, problem, bubble, row, out):
    starts = [eq.EquilibriumStart(amounts=[bubble.amounts[0]*f,bubble.amounts[0]*(1-f)],
        compositions=[bubble.phase_mole_fractions(0),bubble.phase_mole_fractions(1)],packing_fractions=bubble.packing_fractions) for f in (.5,.9)]
    batch = eq.solve_equilibrium_starts(model,problem,starts,eq.EquilibriumWorkLimits(attempts=2,attempt_iterations=400,iterations=800))
    row['bubble_causes'] = list(batch.causes)
    row['bubble_selected'] = batch.selected
    row['attempts'].extend(None if r is None else phase_payload(model,problem,r) for r in batch.results)
    s.write_json(out,row)
    return batch.results[batch.selected] if batch.selected is not None else None


def family_job(mapping, request, row, retained, out):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping),thermochemistry=thermal.record())
    problem = flash_problem(request,row['loading'],row['temperature_K'],row['pressure_Pa'])
    result = eq.solve_equilibrium(model,problem)
    row['attempts'] = [phase_payload(model,problem,result)]
    s.write_json(out,row)
    if not result.success:
        result = recover(model,problem,row,retained,out)
    bubble_problem,liquid,bubble = diagnose(model,request,row,out)
    if bubble is not None and bubble.success:
        if row['pressure_Pa']>bubble.pressure[0] and liquid.success:
            problem = flash_problem(request,row['loading'],row['temperature_K'],row['pressure_Pa'],[eq.Phase('L',kind='liquid',support=s.COMPONENT_IDS)])
            result = liquid
        elif result is None or not result.success:
            result = bubble_recover(model,problem,bubble,row,out)
    if result is not None:
        row['final'] = phase_payload(model,problem,result)
        if result.success:
            row['stability'] = [stability(model,problem,result)]
    row['classification'] = phase_classification(row)
    s.write_json(out,row)



def phase_family(mapping, request, points_path, points_sha256, output_dir):
    points = campaign.checked(points_path,points_sha256)
    inputs = [list(map(float,line.split())) for line in points.read_text().splitlines()]
    assert len(inputs)==73
    old = campaign.load(points.with_name('old-index-63.json'))['diagnosis']
    assert phase_classification(dict(old,final=dict(success=old['liquid_accepted'],requested_tolerance_met=old['liquid_residual']<=1e-10)))=='unresolved'
    retained, output = [], Path(output_dir)
    for index,(loading,T,P) in enumerate(inputs):
        path = output/f'point-{index}.json'
        row = dict(index=index,loading=loading,temperature_K=T,pressure_Pa=P,attempts=[])
        s.write_json(path,row)
        def child():
            try:
                family_job(mapping,request,row,retained,path)
            except Exception as error:
                saved = campaign.load(path)
                s.write_json(path,dict(saved,failure=f'{type(error).__name__}: {error}'))
        timing = campaign.bounded_call(child,300.)
        row = dict(campaign.load(path),timing=timing)
        row['classification'] = phase_classification(row)
        s.write_json(path,row)
        retained.append(row)
    counts = {label:sum(r['classification']==label for r in retained) for label in
        ('failed','unresolved','passed-two-phase','passed-single-liquid')}
    assert sum(counts.values())==73
    s.write_json(output/'summary.json',dict(counts=counts,eligible=counts['failed']==counts['unresolved']==0,
        points_sha256=points_sha256,parameter_sha256=__import__('hashlib').sha256(json.dumps(mapping,sort_keys=True).encode()).hexdigest()))
    return retained


def main(output_dir=OUT, documents=None, declaration=None, phase_points=None):
    if documents is not None:
        import fit_observations as o
        for problem,chosen in selected(output_dir,documents=documents).items():
            mapping = s.parameter_mapping(Path(chosen['record']))
            if phase_points is not None:
                return phase_family(mapping,__import__('heat_evidence_170').request(mapping,313.15,.11),*phase_points,output_dir)
            _,rows = o.stage6_rows(declaration,mapping)
            weights = campaign.stage6_weights(declaration,[r for r,_ in rows],chosen['density_weight'])
            values = o.replay(mapping,[(r['id'],item,w) for (r,item),w in zip(rows,weights,strict=True)])
            s.write_json(Path(output_dir)/(problem+'-full-replay.json'),values)
            raw = campaign.load(chosen['raw'])
            fitted = [r for r in values if r['weight']>0]
            assert [r['target'] for r in fitted]==[r['id'] for r in raw['rows']]
            assert all(r['status']=='Available' for r in values) and campaign.stage6_ties(declaration,mapping)
            assert max(abs(r['weighted_residual']-v) for r,v in zip(fitted,raw['weighted_residuals'],strict=True))<=1e-8
            assert abs(math.fsum(r['cost'] for r in fitted)-raw['final_cost'])<=1e-8*max(abs(raw['final_cost']),1e-300)
            reference = {r['id']:v for r,v in zip(campaign.load(chosen['kiepe_reference'])['rows'],campaign.load(chosen['kiepe_reference'])['weighted_residuals'],strict=True)}
            assert sum(r['target'].startswith('kiepe-') for r in fitted)==39
            assert all(abs(r['weighted_residual']-reference[r['target']])<=1e-8 for r in fitted if r['target'].startswith('kiepe-'))
        return

    clock=time.perf_counter()
    EVAL.mkdir(parents=True,exist_ok=True)
    choices=selected(); packet, groups=observations()
    tasks=[]; excluded=[]
    for problem,chosen in choices.items():
        binding(problem,chosen['record'])
        raw=json.loads(Path(chosen['raw']).read_text());mask=set(raw['targets'])
        use=groups if problem in ('F1','F2','F6','F1-no-heat') else {'packet':[{**o,'targets':[t for t in o['targets'] if t['identity'] in mask]} for o in packet if any(t['identity'] in mask for t in o['targets'])]}
        for kind, oo in use.items():
            for o in oo:
                T=o['request']['temperature']['value']
                domain_failure = probe.reaction_domain_status(o) if problem!='F6' else None
                if domain_failure or not 293.15<=T<=393.15:
                    excluded.append(dict(problem=problem,kind=kind,identity=o['identity'],temperature_K=T,reason='not evaluated: outside declared reaction domain'))
                    continue
                tasks.append((problem,chosen['record'],kind,o))
    records=[];density=[]
    workers=min(2,len(os.sched_getaffinity(0)))
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
