"""Record the retained numerical diagnosis; never run the Engine."""
import time
STARTED=time.perf_counter()
import csv
import hashlib
import json
import zipfile
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
def read(name): return json.loads((HERE/name).read_text())
def rows(name): return list(csv.DictReader((HERE/name).open()))
def save(name,value): (HERE/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def table(items,keys=None):
    if not items:return 'No completed values.\n'
    keys=keys or list(items[0])
    def fmt(v):
        if isinstance(v,float):return f'{v:.8g}'
        return str(v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(keys)+' |\n| '+' | '.join(['---']*len(keys))+' |\n'+''.join('| '+' | '.join(fmt(r.get(k,'')) for k in keys)+' |\n' for r in items)

screen=read('p2-screening.json')
raw_svd={}
for form,n in [('11',9),('00',3)]:
    jk=np.asarray(read(f'baseline-{form}-jacobian.json')['weighted_physical_jacobian'])
    cols=[read(f'column-{form}-q{j}.json') for j in range(n)]
    estimates=[]
    for k in ('jacobian_first','jacobian_second'):
        if any(not c.get('attempts') for c in cols):break
        J=np.column_stack([jk,*[c['attempts'][-1][k] for c in cols]])
        norms=np.linalg.norm(J,axis=0)
        assert np.all(norms>0)
        estimates.append({'jacobian':k,'physical_singular_values':np.linalg.svd(J,compute_uv=False).tolist(),
            'column_normalized_singular_values':np.linalg.svd(J/norms,compute_uv=False).tolist(),
            'physical_rank':int(np.linalg.matrix_rank(J)), 'normalized_rank':int(np.linalg.matrix_rank(J/norms))})
    raw_svd[form]={'accepted_for_attribution':all(c['available'] for c in cols),
        'unavailable_columns':[c['coordinate'] for c in cols if not c['available']],
        'estimates':estimates,'meaning':'Full matrix of retained estimates, including any disagreeing column. No entry dropped or zeroed. Unaccepted matrix cannot support attribution.'}
save('p2-whole-jacobian-singular-values.json',raw_svd)
fd=[]
for form,n in [('11',9),('00',3)]:
    for j in range(n):
        c=read(f'column-{form}-q{j}.json');a=c.get('attempts',[])
        fd.append({'form':form,'coordinate':c['coordinate'],'available':c['available'],
            'attempts':len(a),'agreeing_entries':a[-1]['agreeing_entries'] if a else None,
            'total_entries':160,'max_difference_over_tolerance':a[-1]['max_difference_over_tolerance'] if a else None})
with (HERE/'p2-step-agreement.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(fd[0]));w.writeheader();w.writerows(fd)
confirm=[read(p.name) for p in sorted(HERE.glob('p3-*-confirmation.json'))]
for c in confirm:
    c['native_history_entries_including_initial']=c['iterations'];c['optimizer_updates']=max(0,c['iterations']-1)
unavailable=[{'case':p.name,**read(p.name)} for p in sorted(HERE.glob('p3-*-unavailable.json'))]
unavailable+=[{'case':p.name,**read(p.name)} for p in sorted(HERE.glob('p3-*-job-failure.json'))]
costs=[r for r in rows('objective-evaluations.csv') if not r['name'].startswith('scan-')]
with (HERE/'p0-p5-complete-objective-evaluations.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(costs[0]));w.writeheader();w.writerows(costs)
key_costs=[r for r in costs if not r['name'].startswith(('fd-','p4-fd-','branch-baseline-')) and not r['name'].endswith('-exact-k')]
with (HERE/'key-objective-evaluations.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(key_costs[0]));w.writeheader();w.writerows(key_costs)
species_costs=[]
for r in costs:
    assert r['complete']=='True'
    assert abs(float(r['cost'])-sum(float(r[k]) for k in ('pressure_cost','bottinger_cost','matin_cost')))<1e-8
    full=read(r['name']+'.json')
    for source in ('Matin','Bottinger'):
        for species in ('HCO3-','MEA','MEAH+','MEACOO-','MEA + MEAH+'):
            residuals=[float(value) for target,value in zip(full['targets'],full['weighted_residuals'],strict=True)
                if target.startswith(source) and target.split('::')[-1]==species]
            species_costs.append({'evaluation':r['name'],'source':source,'species':species,'n':len(residuals),
                'cost':sum(.5*x*x for x in residuals) if residuals else None,
                'mean_signed_weighted_residual':sum(residuals)/len(residuals) if residuals else None,
                'basis':'fitted targets; positive means model above; HCO3 includes carbonate pool' if residuals else 'no fitted target for this source/species'})
with (HERE/'objective-species-costs-and-signed-residuals.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(species_costs[0]));w.writeheader();w.writerows(species_costs)
verified={}
for name in ('input-hashes.json','accepted-fit-anchor-hashes-00.json','accepted-fit-anchor-hashes-11.json','p1-transfer-input-hashes.json'):
    obj=read(name)
    # All four files map original absolute paths to SHA-256 values.
    for path,sha in obj.items():
        assert digest(Path(path))==sha, f'changed protected input: {path}'
        verified[path]=sha
save('input-preservation-check.json',{'verified_files':len(verified),'sha256_by_path':verified})
wheel=next(Path(p) for p in read('input-hashes.json') if p.endswith('.whl'))
sites=list((HERE.parents[3]/'.venv/lib').glob('python*/site-packages'))
assert len(sites)==1
installed={}
with zipfile.ZipFile(wheel) as archive:
    for name in archive.namelist():
        if name.startswith('epcsaft/') and not name.endswith('/'):
            expected=hashlib.sha256(archive.read(name)).hexdigest()
            assert digest(sites[0]/name)==expected, f'installed file differs from pinned wheel: {name}'
            installed[name]=expected
save('installed-wheel-content-check.json',{'wheel_sha256':digest(wheel),'matching_installed_files':installed})
for path,sha in read('supplementary-input-hashes.json')['sha256_by_path'].items():
    assert digest(Path(path))==sha, f'changed supplementary input: {path}'
jobs=read('job-times.json');jobs.append({'job':'summarize-results','wall_s':time.perf_counter()-STARTED,'status':'complete'})
save('job-times.json',jobs)
commands=[]
for job in jobs:
    name=job['job'];base='analyses/mea_parameter_bundle/model-d/born-form-diagnosis/'
    if name in ('baselines','p1b','branch-check'):args=base+'born_form_diagnosis.py '+name;cap={'baselines':220,'p1b':200,'branch-check':180}[name]
    elif name=='p1':args=base+'p1.py';cap=120
    elif name=='p2':args=base+'p2.py';cap=1450
    elif name.startswith('p3-'):args=base+'p3.py '+name[3:];cap=300
    elif name=='p4':args=base+'p4.py';cap=900
    elif name.startswith('p5'):args=base+'p5.py '+name[2]+' '+name[-2:];cap=300
    elif name=='render-association':args=base+'render_association.py';cap=30
    else:args=base+'summarize_results.py';cap=30
    commands.append({'job':name,'command':f'flock /tmp/t3-heavy-check.lock timeout {cap} nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python -B '+args,'script_sha256':job.get('script_sha256'),'wall_s':job['wall_s'],'completion':job['status']})
save('execution-commands.json',commands)
elapsed=sum(j.get('charged_s',j['wall_s']) for j in jobs if not j['job'].startswith(('p4','p5')))
p4_elapsed=sum(j.get('charged_s',j['wall_s']) for j in jobs if j['job'].startswith('p4'))
p5_elapsed=sum(j.get('charged_s',j['wall_s']) for j in jobs if j['job'].startswith('p5'))
assert elapsed<=2700 and p4_elapsed<=900 and p5_elapsed<=1200
summary={'cost_convention':'C = 0.5 sum weighted residual squared; dimensionless cost units',
    'states_per_complete_objective':84,'targets':160,'charged_execution_s':elapsed,'p4_execution_s':p4_elapsed,'p5_execution_s':p5_elapsed,
    'hypotheses':{
        'a':'Inconclusive: main-ion diameter confirmation converged in six iterations, recovering 3.6748899829 cost units, below 3.71. Secondary group unavailable because H3O column disagrees after retry.',
        'b':'Inconclusive: shell/MEA group predicts 3.0728051566 cost units; no confirming refit under the accepted best-group selection.',
        'c':'Unavailable for the finite configuration comparison: (1,0) initial solve failed without a complete objective. Local saturation-strength reduction is zero; (0,1) = (0,0) equality is verified.',
        'd':'Inconclusive: P1 shows no uniform attenuation, and unavailable/unconfirmed groups preclude the proposed elimination argument.'},
    'confirmations':confirm,'unavailable_p3_cases':unavailable,'screening':screen['screens'],
    'unanswered':['No joint attribution when an included whole column is unavailable.','No physical validation or intrinsic-form ranking.','No parameter adoption; delivered independent review belongs to parent thread.'],
    'evidence':'local numerical verification and descriptive model decomposition; no physical validation'}
save('diagnosis-summary.json',summary)
text='''---
title: "MEA model D: Born-form diagnosis"
format: html
execute:
  enabled: false
---

This notebook records the accepted #121 v2–v2.2 probes on installed wheel 28181e72. It is retained numerical evidence awaiting the parent's delivered review, with no parameter adoption. Cost means C = ½‖r_w‖²: 160 weighted targets at 84 states, with reaction constants fixed. Pressure uses ln(predicted/observed)/0.3; speciation uses (predicted−observed)/(0.1 observed+0.001). The reported bicarbonate target pools bicarbonate and carbonate.

The original 7.42423 cost penalty is concentrated in Matin 20 °C speciation (+11.34102); pressure (−1.77716) and Böttinger (−2.13963) favor (1,1). The re-evaluated baselines reproduce the retained values on the pinned wheel. Model D uses solvent-only permittivity. P1 decomposition and rank correlations are descriptive associations, not causal attribution.

The screening bounds are engineering analog envelopes: Figiel 2025, Model Parameters, Tables 2–3, p. 9411, reports non-proton Born diameters 2.784–4.985 Å, H⁺ 1.218 Å, and solvent factors water 1.5, methanol 1.4, ethanol 1.6 (Eqs. 8–10). It contains no MEA ions or MEA solvent factor. Each MEAH⁺, MEACOO⁻, HCO₃⁻, CO₃²⁻ and OH⁻ diameter uses 2–5 Å; H₃O⁺ uses 1–2 Å by H⁺ analogy; f_MEA uses 1–2 by solvent analogy. Held 2014 §2.3/Table 2 gives segment diameters, a different quantity. Local displacements are at most half each interval width. Water factor remains 1.5, epsilon_ion remains 8, and c_shell/c_dielectric stay in [0,1].

Finite differences use the declared scaled steps and entrywise tolerance, including one retry. No entry is dropped or zeroed. Five-coordinate bounded local least squares respect the (0,0) active bounds. A predicted reduction is a local screen; a capped refit establishes only its achieved reduction unless convergence is demonstrated. Thresholds 3.71 and 1.86 are declared screening thresholds, not statistical significance limits.

## Complete objective evaluations

Every complete evaluation has the three-group split below. P1 is a decomposition at retained states and has no new complete-objective cost.

'''
text+=table(costs,['name','cost','pressure_cost','bottinger_cost','matin_cost','wall_s'])
text+='\n## Costs and signed residuals by source and species\n\nMatin measured ambient-temperature acid/base titration and total inorganic carbon; this packet represents it at 20 °C. Its paper reports higher bicarbonate than Jakobsen NMR (Matin 2012, Experimental Section; Results and Discussion, Method Description and Speciation Comparisons, Table S1/Fig. 2). Böttinger 2008 uses online NMR (Experimental Section, NMR spectroscopy), with free and protonated MEA measured as their sum. Different source conditions and target definitions prevent treating opposite residual signs alone as experimental inconsistency. The inherited reaction-temperature screen held pivot ln K fixed; P4 adds offset directions and does not demonstrate that inherited enthalpies caused the Born-form gap.\n\n'+table(species_costs)
text+='\n## Finite-difference agreement\n\n'+table(fd)
text+='\n## Bounded local screens\n\n'+table(rows('p2-screening.csv'))
text+='\n## Confirming refits\n\nThe native iteration history includes the initial point at entry 0; optimizer updates are history length minus one (pinned Engine fit.hpp, iteration_costs comment; fit.cpp, remaining-budget subtraction and result.iterations assignment).\n\n'+table(confirm,['group','achieved_cost','achieved_reduction','classification','converged','optimizer_updates','native_history_entries_including_initial','status'])
text+='\nIncomplete or skipped cases supply no physical evidence:\n\n```json\n'+json.dumps(unavailable,indent=2)+'\n```\n'
text+='\n## Whole augmented Jacobians\n\n'
for form,obj in raw_svd.items():
    text+=f"Form {form}: accepted for attribution = {obj['accepted_for_attribution']}; unavailable columns = {obj['unavailable_columns']}. Full unaccepted estimates are shown without deleting columns. Physical singular values mix Å and dimensionless coordinate units; normalized values remove column scales.\n\n"
    for e in obj['estimates']:
        text+=f"{e['jacobian']}: normalized singular values {e['column_normalized_singular_values']}; physical singular values {e['physical_singular_values']}; ranks {e['physical_rank']}/{e['normalized_rank']}.\n\n"
text+='## P1: loading-range reaction changes\n\nAll values are dimensionless changes in the Born part of ln Πγ^ν, referenced to infinite dilution. The loading basis is retained-feed mol CO₂/mol MEA. R1 is water dissociation, R2 bicarbonate formation, R3 carbonate formation, R4 carbamate hydrolysis, R5 MEAH⁺ dissociation. Own paths use each optimum; common-11-on-00 uses the (0,0) compositions.\n\n'+table(rows('p1-loading-range-changes.csv'))
text+='\n## P1: each Matin and Böttinger state\n\nBorn water ln activity and ionic ln gamma are dimensionless native chemical-potential differences. The native on/off decomposition uses identical T, density and composition; reference is pure water at infinite dilution and 101325 Pa. These single-ion model contributions are not measured single-ion activities.\n\n'
activity=[r for r in rows('p1-water-and-ion-activities.csv') if r['identity'].startswith(('Matin','Bottinger'))]
with (HERE/'p1-matin-bottinger-born-activities.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(activity[0]));w.writeheader();w.writerows(activity)
text+=table(activity)
text+='\n## Matin residual associations\n\nEvery retained Matin state and target is shown. The excluded state is descriptive only. Both axes change with loading, so correlation does not establish cause.\n\n'+table(rows('p1-matin-associations.csv'))
text+='\n'+table(rows('p1-rank-correlations.csv'))+'\n![Matin water-activity associations](matin-water-activity-association.png)\n'
text+='\n## Meaning and limits\n\nP1 does not show uniform reduced composition sensitivity: on the common 30 wt% path the magnitudes of R1–R3 and R5 changes increase in (1,1), while R4 decreases and changes sign. The per-ion kernel estimate d/D is not the full reaction activity sensitivity. Unavailable columns cannot reject physics. The numerical groups can be collinear and the largest permitted displacement can exceed the useful range of a local linear approximation. Unconfirmed groups remain unresolved. Ten-iteration values are achieved reductions, not assumed optima. This study does not establish an intrinsic failure of SSM+DS, physical validation, concentration transfer, or adoption. The parent thread must obtain its independent delivered review.\n'
if (HERE/'p4-results.json').exists():
    p4=read('p4-results.json');summary['p4']=p4;save('diagnosis-summary.json',summary)
    p4_agreement=[]
    for path in sorted(HERE.glob('p4-column-??-q?.json')):
        col=read(path.name);a=col['attempts'][-1]
        p4_agreement.append({'form':col['form'],'coordinate':col['coordinate'],'gradient_quality':col['gradient_quality'],
            'available':col['available'],'attempts':len(col['attempts']),'agreeing_entries':a['agreeing_entries'],
            'total_entries':a['total_entries'],'max_difference_over_tolerance':a['max_difference_over_tolerance']})
    with (HERE/'p4-step-agreement.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(p4_agreement[0]));w.writeheader();w.writerows(p4_agreement)
    text+='\n## P4 reaction finite-difference agreement\n\n'+table(p4_agreement)
    text+='\n## P4 exploratory reaction directions\n\nThe owner added 900 s for P4. Reaction directions use finite-difference gradients; the five EOS interaction directions use exact Engine gradients. No covariance is estimated. The mapping changes R2 by the bicarbonate direction and R4 by bicarbonate minus carbamate; R1, R3 and R5 and all nine species remain unchanged. Direction shifts obey delta ln K(T) = delta − delta H/R (1/T−1/313.15), with delta in [−1,1] and delta H in [−10,10] kJ/mol. Source-correlation combinations before EOS conversion have mixed recorded source conventions; their numerical values are not an adopted reduced-set thermodynamic constant.\n\n```json\n'+json.dumps(p4,indent=2)+'\n```\n'
p5=[read(p.name) for p in sorted(HERE.glob('p5?-??-results.json'))]
if p5:
    for c in p5:
        c['native_history_entries_including_initial']=c['iterations'];c['optimizer_updates']=max(0,c['iterations']-1)
    rankings=[]
    for case in ('a','b'):
        pair=[p for p in p5 if p['case']==case]
        rankings.append({'case':case,'ranking_available':len(pair)==2,
            'lower_achieved_fitted_cost_form':min(pair,key=lambda p:p['achieved_fitted_cost'])['form'] if len(pair)==2 else None,
            'difference_11_minus_00':next(p['achieved_fitted_cost'] for p in pair if p['form']=='11')-next(p['achieved_fitted_cost'] for p in pair if p['form']=='00') if len(pair)==2 else None})
    save('p5-summary.json',{'fits':p5,'rankings':rankings,'meaning':'achieved capped sensitivity fits, not adopted fit definitions'})
    summary['p5']={'fits':p5,'rankings':rankings};save('diagnosis-summary.json',summary)
    text+='\n## P5 Matin-role sensitivity\n\nP5a omits 18 Matin bicarbonate targets (142 targets); P5b omits all 72 Matin targets (88 targets). Both retain all original weights and bounds. Each form starts at its own retained optimum and varies the same five interaction coordinates for at most ten iterations. Full re-scores use all 160 targets; omitted targets remain omitted only during the sensitivity fit. The original fit definition and adoption stay unchanged.\n\n```json\n'+json.dumps({'fits':p5,'rankings':rankings},indent=2)+'\n```\n'
text+='\n## Execution and provenance\n\nShared-lock waiting is excluded; the first timed-out attempt is conservatively charged its full 220 s cap. Failed attempts are retained and supply no physical evidence. Every numerical job uses the shared lock, timeout, nice priority and one-thread numerical-library settings. The initial forked evaluator timed out; the qualified native batch evaluator and subsequent one-process state evaluator reproduced the baselines.\n\n'+table(jobs,['job','wall_s','charged_s','status'])
text+=f'\nCharged P0–P3 execution and reporting: {elapsed:.6f} s out of 2700 s; P4: {p4_elapsed:.6f} s out of its additional 900 s; P5: {p5_elapsed:.6f} s out of its additional 1200 s. Input preservation verified for {len(verified)} files. Input and output SHA-256 records accompany this notebook. Scripts and failed partial files remain in this directory; no commit or Engine change was made.\n'
(HERE/'diagnosis.qmd').write_text(text)
jobs[-1]['wall_s']=time.perf_counter()-STARTED
save('job-times.json',jobs)
elapsed=sum(j.get('charged_s',j['wall_s']) for j in jobs if not j['job'].startswith(('p4','p5')))
assert elapsed<=2700
summary['charged_execution_s']=elapsed
save('diagnosis-summary.json',summary)
save('hash-catalog-scope.json',{'included':'P0–P5 scripts and retained result, table, figure, notebook and provenance files under this directory',
    'excluded':['output-hashes.json itself','shared objective-evaluations.csv, which also contains separately owned scan calls','scan-* files and scans/ directory','matplotlib-cache/'],
    'complete_objectives_in_this_report':len(costs),'immutable_cost_table':'p0-p5-complete-objective-evaluations.csv'})
hashes={str(p.relative_to(HERE)):digest(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name not in ('output-hashes.json','objective-evaluations.csv') and not p.name.startswith('scan-') and 'matplotlib-cache' not in p.parts and 'scans' not in p.parts}
save('output-hashes.json',hashes)
print(json.dumps({'charged_execution_s':elapsed,'retained_files':len(hashes),'output_hash_catalog_sha256':digest(HERE/'output-hashes.json')}),flush=True)
