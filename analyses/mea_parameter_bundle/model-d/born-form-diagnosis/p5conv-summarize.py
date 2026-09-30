"""Presentation only: continuation tables, notebook and provenance from retained outputs."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def save(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def table(name,rows):
    with (HERE/name).open('w',newline='') as h:
        w=csv.DictWriter(h,list(rows[0]));w.writeheader();w.writerows(rows)
def md(rows):
    keys=list(rows[0]);fmt=lambda x: f'{x:.8g}' if isinstance(x,float) else str(x)
    return '| '+' | '.join(keys)+' |\n| '+' | '.join(['---']*len(keys))+' |\n'+'\n'.join('| '+' | '.join(fmt(row[k]) for k in keys)+' |' for row in rows)
def species_comparison(results,key):
    rows=[]
    for source in ('Matin','Bottinger'):
        for sp in ('HCO3-','MEA','MEAH+','MEACOO-','MEA + MEAH+'):
            row=dict(source=source,species=sp)
            for r in results:
                item=next(x for x in r[key] if x['source']==source and x['species']==sp)
                if item['n']:row[r['name']]=f'{item["cost"]:.6f} ({item["mean_signed_weighted_residual"]:+.6f})'
            if len(row)>2:rows.append(row)
    return rows
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p5=[json.loads((HERE/f'p5conv-{case}-{form}-results.json').read_text()) for case in ('a','b') for form in ('11','00')]
    p4=[json.loads((HERE/f'p4refit-{form}-results.json').read_text()) for form in ('11','00')]
    costrows=[];krows=[];species=[];times=[]
    for r in p5:
        costrows.append(dict(run=r['name'],n=r['fitted_targets'],fitted_cost=r['fitted_cost'],full_cost=r['full_cost'],
            **r['full_three_group_cost'],updates=r['optimizer_updates'],stop=r['stopping_reason'],wall_s=json.loads((HERE/(r['name']+'-time.json')).read_text())['wall_s']))
        ids=list(r['k_coordinates']);vals=list(r['k_coordinates'].values())
        krows.append(dict(run=r['name'],carbamate_water=vals[0],MEAH_water=vals[1],bicarbonate_water=vals[2],carbamate_MEAH=vals[3],MEAH_water_slope_K=vals[4],active_bounds='; '.join(r['active_bounds'])))
        for label,key in [('fitted','fitted_species_costs_and_signed_residuals'),('full','full_species_costs_and_signed_residuals')]:
            species.extend(dict(run=r['name'],set=label,**row) for row in r[key])
    table('p5conv-costs.csv',costrows);table('p5conv-k-coordinates.csv',krows);table('p5conv-species-costs-and-signed-means.csv',species)
    p4rows=[];p4k=[];p4species=[];svd=[]
    for r in p4:
        p4rows.append(dict(run=r['name'],cost=r['cost'],**r['three_group_cost'],**r['directions'],
            complete_J=r['counts']['complete_jacobians'],callback_updates=r['counts']['accepted_updates'],stop=r['stopping_reason'],wall_s=json.loads((HERE/(r['name']+'-time.json')).read_text())['wall_s']))
        vals=list(r['k_coordinates'].values())
        p4k.append(dict(run=r['name'],carbamate_water=vals[0],MEAH_water=vals[1],bicarbonate_water=vals[2],carbamate_MEAH=vals[3],MEAH_water_slope_K=vals[4],active_k_bounds='; '.join(r['active_k_bounds']),active_reaction_bounds='; '.join(r['active_reaction_bounds'])))
        p4species.extend(dict(run=r['name'],**row) for row in r['species_costs_and_signed_residuals'])
        for path in sorted((HERE/'runs'/r['name']).glob(r['name']+'-jacobian-*.json')):
            rec=json.loads(path.read_text())
            svd.extend(dict(run=r['name'],jacobian=path.stem,ordinal=i+1,singular_value_scaled=x) for i,x in enumerate(rec['singular_values_scaled']))
    table('p4refit-costs-and-reaction-coordinates.csv',p4rows)
    table('p4refit-k-coordinates-and-active-bounds.csv',p4k)
    table('p4refit-final-species-costs-and-signed-means.csv',p4species)
    if svd:table('p4refit-augmented-jacobian-singular-values.csv',svd)
    evaluationrows=[];allspecies=[];fd=[];max_cost_difference=0.;max_stationarity=0.;state_records=0
    for folder in sorted((HERE/'runs').glob('*')):
        if not folder.is_dir() or not folder.name.startswith(('p5conv-','p4refit-')):continue
        for path in sorted(folder.glob('*.json')):
            r=json.loads(path.read_text())
            if isinstance(r,dict) and r.get('complete') and len(r.get('weighted_residuals',[]))==160:
                rr=r['weighted_residuals'];difference=abs(sum(.5*x*x for x in rr)-r['cost']);assert difference<1e-8
                max_cost_difference=max(max_cost_difference,difference)
                evaluationrows.append({k:r[k] for k in ('name','form','cost','pressure_cost','bottinger_cost','matin_cost','wall_s')})
                for source in ('Matin','Bottinger'):
                    for sp in ('HCO3-','MEA','MEAH+','MEACOO-','MEA + MEAH+'):
                        vals=[x for t,x in zip(r['targets'],rr,strict=True) if t.startswith(source) and t.split('::')[-1]==sp]
                        allspecies.append(dict(evaluation=r['name'],source=source,species=sp,n=len(vals),cost=sum(.5*x*x for x in vals) if vals else None,mean_signed_weighted_residual=sum(vals)/len(vals) if vals else None))
            if path.name.endswith('finite-difference-quality.json'):
                fd.extend(dict(run=folder.name,jacobian=x['jacobian'],coordinate=x['coordinate'],available=x['available'],
                    attempts=len(x['attempts']),agreeing_entries=x['attempts'][-1]['agreeing_entries'],maximum_difference_over_tolerance=x['attempts'][-1]['maximum_difference_over_tolerance']) for x in r)
        for path in list(folder.glob('objective-evaluations.csv')):
            path.rename(folder/(folder.name+'-objective-evaluations.csv'))
        for path in folder.glob('*-states.jsonl'):
            records=[json.loads(line) for line in path.read_text().splitlines()]
            assert len(records)==84
            for rec in records:
                assert rec['status']=='evaluated' and rec['check']['tolerance_met']
                assert not rec['check']['balance_errors']
                assert rec['check']['max_abs_stationarity']<=1e-10
                max_stationarity=max(max_stationarity,rec['check']['max_abs_stationarity']);state_records+=1
    table('p4refit-all-complete-evaluation-costs.csv',evaluationrows)
    table('p4refit-all-complete-evaluation-species.csv',allspecies)
    if fd:table('p4refit-finite-difference-agreement.csv',fd)
    for r in p5+p4:times.append(json.loads((HERE/(r['name']+'-time.json')).read_text()))
    save('p5conv-job-times.json',times)
    ranking=[dict(case=case,SSM_DS_cost=next(r['fitted_cost'] for r in p5 if r['case']==case and r['form']=='11'),
        Original_cost=next(r['fitted_cost'] for r in p5 if r['case']==case and r['form']=='00')) for case in ('a','b')]
    save('p5conv-summary.json',dict(P5=p5,P4=p4,ranking=ranking,job_times=times,complete_evaluations=len(evaluationrows)))
    iterations=[]
    for r in p4:
        history=json.loads((HERE/'runs'/r['name']/(r['name']+'-history.json')).read_text())
        assert len(history)==5 and all(history[i]['cost']<history[i-1]['cost'] for i in range(1,5))
        assert r['counts']['complete_jacobians']==4 and r['counts']['accepted_updates']==3
        iterations.append(dict(run=r['name'],accepted_steps=4,callback_updates_with_completed_jacobian=3,
            last_accepted_point_jacobian_available=False,basis='SciPy bounded TRF assigns a cost-reducing x_new before calling jac(x); the fifth jac call stopped at its initial time guard.'))
    scipy_source=HERE.parents[3]/'.venv/lib/python3.13/site-packages/scipy/optimize/_lsq/trf.py'
    save('p4refit-iteration-interpretation.json',dict(runs=iterations,source=str(scipy_source),source_sha256=sha(scipy_source)))
    max_subset_difference=0.;max_warm_difference=0.;max_exact_residual_difference=0.
    for r in p5:
        raw=json.loads((HERE/'runs'/r['name']/(r['name']+'-fit.json')).read_text())
        old=json.loads((HERE/f'p5{r["case"]}-{r["form"]}-results.json').read_text())
        assert raw['status']=='converged' and all(s=='Available' for s in raw['observation_statuses'])
        assert raw['trial_failures']==0
        assert abs(raw['initial_cost']-old['achieved_fitted_cost'])<1e-8
        max_subset_difference=max(max_subset_difference,abs(r['subset_rescore_difference']))
    for r in p4:
        initial=json.loads((HERE/'runs'/r['name']/(r['name']+'-objective-001.json')).read_text())
        max_warm_difference=max(max_warm_difference,abs(initial['cost']-r['initial_cost']))
        assert abs(initial['cost']-r['initial_cost'])<1e-8
        for j in range(1,5):
            native=json.loads((HERE/'runs'/r['name']/(r['name']+f'-jac{j:02d}-exact-k.json')).read_text())
            direct=json.loads((HERE/'runs'/r['name']/(r['name']+f'-objective-{j:03d}.json')).read_text())
            error=max(abs(a-b) for a,b in zip(native['weighted_residuals'],direct['weighted_residuals'],strict=True))
            assert error<1e-8;max_exact_residual_difference=max(max_exact_residual_difference,error)
    old=json.loads((HERE/'input-preservation-check.json').read_text())['source_sha256_by_path']
    for filename,expected in old.items():
        path=Path(filename);content=gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()
        assert hashlib.sha256(content).hexdigest()==expected,filename
    for filename,expected in json.loads((HERE/'output-hashes.json').read_text()).items():assert sha(HERE/filename)==expected,filename
    save('p5conv-numerical-verification.json',dict(complete_160_target_evaluations=len(evaluationrows),explicit_state_records=state_records,
        maximum_cost_reconstruction_difference=max_cost_difference,maximum_absolute_raw_stationarity=max_stationarity,
        maximum_P5_subset_rescore_difference=max_subset_difference,maximum_P4_warm_start_cost_difference=max_warm_difference,
        maximum_exact_k_native_vs_direct_residual_difference=max_exact_residual_difference,
        previous_inputs_verified=len(old),previous_outputs_verified=312,all_reaction_columns_available=all(row['available'] for row in fd),
        completed_reaction_columns=len(fd),columns_with_retry=sum(row['attempts']>1 for row in fd),active_k_reporting_tolerance=1e-8,
        covariance='not estimated',evidence='numerical verification; no physical validation'))
    prose='''---
title: "Converged Matin-role sensitivity and reaction warm refits"
format: html
execute:
  enabled: false
---

The owner-authorized continuation uses the immutable Engine wheel `28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`. Form 11 is SSM+DS; form 00 is Original Born. All costs are dimensionless, with convention C = ½ sum of squared weighted residuals. This is evidence from local numerical fitting and numerical verification, with no physical validation or parameter adoption.

P5a removes the 18 Matin bicarbonate-pool targets (142 retained); P5b removes all 72 Matin targets (88 retained). Fits warm-start from their corresponding capped results, retaining the five interaction-coordinate bounds, weights, source reactions, Born inputs and accepted initial guesses. Native gradients are exact for these interaction coordinates. The slope coordinate has units K; four reference interaction coordinates are dimensionless. Each job has a 2400 s timeout and one numerical-library thread; at most two run concurrently, with no shared lock.

## P5 convergence and full-set re-scores

'''+md(costrows)+'\n\n'+md(krows)+'\n\nEach entry below is dimensionless species cost (mean signed weighted residual), on the full 160-target re-score.\n\n'+md(species_comparison(p5,'full_species_costs_and_signed_residuals'))+'''

The SSM+DS reduced-set ranking remains lower for both objectives after the native convergence criterion is met. Full re-scores still rank Original Born lower. Removing Matin changes the objective; it does not validate either form or resolve the official role of Matin. The full-set source/species costs and signed means are retained in [p5conv-species-costs-and-signed-means.csv](p5conv-species-costs-and-signed-means.csv). Signed residuals follow model minus observation, divided by the retained target scale. Böttinger directly measures the MEA + MEAH+ sum; it has no separate MEA or MEAH+ targets in this fit. Empty groups have null means and costs, rather than zero observations.

## P4 exploratory reaction warm refits

The four added coordinates are δ_carbamate, ΔH_carbamate, δ_bicarbonate, and ΔH_bicarbonate. δ is a dimensionless natural-log equilibrium-constant shift at 313.15 K; ΔH is in kJ/mol. ΔlnK(T) = δ − (1000 ΔH/R)(1/T − 1/313.15). Changes are mapped to recorded R2 = bicarbonate and R4 = bicarbonate − carbamate; R1, R3 and R5 remain fixed, and all nine species remain present. δ is bounded to ±1 and ΔH to ±10 kJ/mol.

The MEA-side bounded trust-region least-squares calculation uses exact Engine interaction columns and two-step finite-difference reaction columns. Relative steps are 1e-4 and 1e-5, with h = ρ max(|coordinate|, 1 unit). Near a bound it uses a feasible second-order one-sided difference. Every entry must agree within 1e-3 max(|J_coarse|, |J_fine|) + 1e-8; one retry uses 1e-3 and 1e-4. No entry is removed or zeroed. No covariance is estimated. Each refit is capped at 20 accepted updates and 2400 s; unfinished gradients or stopped fits establish no physical significance.

'''+md(p4rows)+'\n\n'+md(p4k)+'\n\nEach entry below is dimensionless species cost (mean signed weighted residual), on the full 160-target returned point.\n\n'+md(species_comparison(p4,'species_costs_and_signed_residuals'))+'''

Costs at returned points are complete 160-target numerical evaluations; finite-difference perturbations are also retained with their complete source/species splits. Source-correlation shifts and local enthalpy combinations are before EOS standard-state conversion, not measured equilibrium constants or absorption heats. See [p4refit-all-complete-evaluation-costs.csv](p4refit-all-complete-evaluation-costs.csv), [p4refit-all-complete-evaluation-species.csv](p4refit-all-complete-evaluation-species.csv), and [p4refit-finite-difference-agreement.csv](p4refit-finite-difference-agreement.csv).

The final P4 species costs and signed means are retained separately in [p4refit-final-species-costs-and-signed-means.csv](p4refit-final-species-costs-and-signed-means.csv). The nine singular values of every completed scaled augmented Jacobian are in [p4refit-augmented-jacobian-singular-values.csv](p4refit-augmented-jacobian-singular-values.csv); interaction scales are 0.01 for reference coefficients and 10 K for the reciprocal-temperature slope, with reaction scales 1 natural-log unit and 1 kJ/mol. These singular values describe the local numerical sensitivity, not a covariance or physical identifiability result.

P4 uses function, step and gradient tolerances of 1e-8. Its internal deadline is 2380 s from process start, inside the external 2400 s timeout. Before another Jacobian, it reserves its previous measured Jacobian duration plus 70 s. Both runs stopped at this guard. Each accepted four cost-reducing steps, of which three reached the callback after the new Jacobian completed; four complete Jacobians include the starting-point Jacobian. The last accepted point has a complete objective but no new Jacobian and is not declared converged. This count is traced in [p4refit-iteration-interpretation.json](p4refit-iteration-interpretation.json). The inherited helper's exception text names the earlier 2700 s stage budget, but that earlier deadline is overridden for these jobs.

Both returned points place the carbamate enthalpy shift at +10 kJ/mol. SSM+DS also places bicarbonate–water k at +0.5. Original Born's bicarbonate–water k is 1.083e-7 below +0.5, close to the bound but outside the 1e-8 active-bound reporting tolerance. All 32 completed reaction columns passed with all 160 entries; one bicarbonate enthalpy column for SSM+DS required the permitted retry. P4 improves the evaluated warm-start cost by 0.040162871 for SSM+DS and 0.261465597 for Original Born. The unfinished fits do not establish a converged reaction-adjusted ranking.

## Numerical checks and limits

Full-score reduced-set costs must reproduce the native fitted-set costs within 1e-8. Every explicit state evaluation checks requested solve tolerance, raw stationarity ≤1e-10, finite residuals, phase support and topology against the retained baseline. The two previously failed solves are unchanged and remain with the Engine lead. Native stopping criteria establish numerical termination of a local bounded fit; they do not establish a unique global optimum or physical validation. Reaction-gradient quality is finite difference next to exact EOS directions. Active bounds and finite CPU limits constrain interpretation. No adopted fit definition or retained source parameter record is changed.

## Provenance

Owner direction: [MEA #121 continuation](https://github.com/tannerpolley/MEA-Thermodynamics/issues/121#issuecomment-5905866107). Per-job input hashes, native histories, state records, finite-difference columns and exact Jacobians are under `runs/`. Compact JSON/CSV and diagnostic parameter records are beside this notebook. [p5conv-job-times.json](p5conv-job-times.json) records elapsed seconds and execution rules. The existing diagnosis notebook remains unchanged; this separate notebook has not received an independent delivered-result review or promotion. The output manifest records raw-byte SHA-256 hashes. Input lineage uses the retained helper convention, which hashes decompressed content for gzip packets.
'''
    (HERE/'p5conv-results.qmd').write_text(prose)
    hashes={str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and (p.name.startswith(('p5conv-','p4refit-')) or ('runs' in p.relative_to(HERE).parts and p.parent.name.startswith(('p5conv-','p4refit-')))) and p.name!='p5conv-output-hashes.json'}
    save('p5conv-output-hashes.json',hashes)
    print(json.dumps(dict(P5=costrows,P4=p4rows,times=times,output_files=len(hashes)),indent=2))

if __name__=='__main__':main()
