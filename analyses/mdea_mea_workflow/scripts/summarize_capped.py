"""Render retained capped-fit results; no Engine imports or calculations."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
AN=Path(__file__).resolve().parents[1]
OUT=AN/'results/stage2-capped'
def load(path):return json.loads((OUT/path).read_text())
def number(value):return 'Unavailable' if value is None else f'{value:.4g}'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(str(v) for v in row)+' |' for row in rows])
def aggregate(rows):
    good=[r for r in rows if r.get('relative_error') is not None]
    return 100*sum(abs(r['relative_error']) for r in good)/len(rows) if rows and len(good)==len(rows) else None

selection=load('selection.json');labels=[selection[v]['label'] for v in 'AB']
assessment=[load(f'{q}/assessment.json') for q in labels]
fits=[load(f'{q}/fit.json') for q in labels]
phases=[load(f'{q}/phase-summary.json') for q in labels]
plotted=[dict(variant=v,endpoint=q,AARD_percent=a['Ermatchkov88']['AARD_percent'],criterion_percent=24.2) for v,q,a in zip('AB',labels,assessment)]
with (OUT/'transfer-test.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(plotted[0]));writer.writeheader();writer.writerows(plotted)
fig,ax=plt.subplots(figsize=(7,3.5),layout='constrained')
for i,row in enumerate(plotted):
    ax.scatter(i,row['AARD_percent'],color=('#0072B2','#D55E00')[i],marker=('o','x')[i],s=85)
    ax.annotate(f"{row['AARD_percent']:.3f}%",(i,row['AARD_percent']),xytext=(10,4),textcoords='offset points')
ax.axhline(24.2,color='#555555',ls='--',label='Declared limit: 24.2%')
ax.set(xticks=[0,1],xticklabels=['Variant A: A3','Variant B: B1'],ylabel='CO₂ partial-pressure AARD (%)',ylim=(0,32),xlim=(-.5,1.5),title='Frozen MEA record: 88-row MDEA pressure-transfer test')
ax.grid(axis='y',alpha=.2);ax.legend(loc='lower left');fig.savefig(OUT/'transfer-test.png',dpi=180);plt.close(fig)

rows=[]
for label,fit,phase,a in zip(labels,fits,phases,assessment):
    rows.append([label,number(fit['final_cost']),number(a['Ermatchkov88']['AARD_percent']),'Pass' if a['Ermatchkov_pass'] else 'Fail',len(phase['liquid_witnesses']),len(phase['vapor_witnesses']),phase['rounding_trials'],len(phase['unresolved'])])
primary=table(['Endpoint','Cost','Ermatchkov AARD (%)','24.2% test','Dense splits','Gas states','Reconstruction trials','Other unresolved'],rows)
metrics=[]
for group,title in [('Kuranov','Kuranov total pressure, fitted (69)'),('Jakobsen','Jakobsen two speciation ratios, fitted (16)'),('Carson','Carson integral heat, fitted (40)'),('Merkley','Merkley capped heat, fitted (4)'),('Cp','Weiland Cp, fitted (33)'),('loaded-density','Weiland loaded density, fitted (33)'),('unloaded-density','Sobrino density, fitted (24)'),('Kim','Kim bubble pressure, fitted (61)')]:
    metrics.append([title,*[number(a['fitted'][group]['AARD_percent']) for a in assessment]])
metrics.append(['Hsieh permittivity, frozen coefficients',*[number(a['Hsieh']['AARD_percent']) for a in assessment]])
for group,title in [('Ermatchkov_above49','Ermatchkov above 49 wt%, extrapolation (13)'),('Ermatchkov_below7','Ermatchkov below 7 kPa (33)'),('Ermatchkov88_below7','Primary-set rows below 7 kPa (29)'),('corrected-Kamps','Corrected Kamps pressure, context (28)'),('Bottinger-amine-sum-5bar','Böttinger amine sum, 5 bar (58)'),('Bottinger-amine-sum-25bar','Böttinger amine sum, 25 bar (58)'),('Cp-60wt','Weiland Cp at 60 wt%, extrapolation (6)'),('density-60wt','Weiland density at 60 wt%, extrapolation (11)'),('Zheng','Zheng integral heat, context (6)'),('Sedighi','Sedighi total pressure, context (15)')]:
    metrics.append([title,*[number(a[group]['AARD_percent']) for a in assessment]])
merkley=[]
for label in labels:
    comp=load(f'{label}/comparisons.json')
    selected=[r for r in comp if r['group']=='Merkley-outside' and float(r['row']['MDEA_mass_percent'])==60 and r.get('relative_error') is not None]
    merkley.append(aggregate(selected))
metrics.append(['Merkley 60 wt%, 333.15/388.71 K (2)',*[number(q) for q in merkley]])
metric_table=table(['Source and role','Variant A AARD (%)','Variant B AARD (%)'],metrics)
bounds=[]
for label,fit in zip(labels,fits):
    decl=load(f'{label}/declaration.json')['coordinates']
    for i in fit['covariance']['active_bounds']:
        q=decl[i];bounds.append([label,i,str(q['targets'][0][1]),q['targets'][0][0],number(q['origin']+q['scale']*fit['optimizer'][i]),str(q['bounds'])])
caprows=[]
for label in labels:
    for row in load(f'{label}/Merkley-caps.json'):
        caprows.append([label,row['temperature_K'],row['MDEA_mass_percent'],number(row['source_loading']),number(row['saturation_loading']),number(row['selected_loading']),number(row['truncation'])])
follow=[]
for label in labels:
    b=load(f'{label}/followup-bicarbonate/assessment.json');f=load(f'{label}/followup-comparison.json')
    corr=load(f'{label}/followup-bicarbonate/correlation.json')['correlation']
    follow.append([label,number(b['Ermatchkov88']['AARD_percent']),number(corr),f.get('status','Available'),f.get('improvement_points','Unavailable')])
sv=table(['Singular-value index','A3','B1'],[[i+1,*[number(f['covariance']['singular_values'][i]) for f in fits]] for i in range(9)])
wangler=table(['Endpoint','Neumann Cp AARD (%)','Wangler Cp AARD (%)','Change (percentage points)','Kim RMS log ratio'],[[q,number(a['fitted']['Cp']['AARD_percent']),number(a['Wangler_fitted']['Cp']['AARD_percent']),number(a['Wangler_Cp_delta_points']),number(a['fitted']['Kim']['root_mean_square_log_ratio'])] for q,a in zip(labels,assessment)])
text='''---
title: "MDEA transfer with saturation-capped absorption heat"
format: html
---

## Outcome and intended use

Variant A fails the declared 24.2% pressure-transfer test; Variant B passes. AARD is average absolute relative deviation. The endpoints were selected by the lowest fitted cost among candidates passing the density-classified phase gate. Selection was committed in `005f79e` before any outside-fit statistic was computed.

'''+primary+'''

![Variant A exceeds the declared pressure limit; Variant B is below it. Points are aggregate statistics over 88 retained source rows, not an uncertainty estimate.](results/stage2-capped/transfer-test.png)

The pressure test uses all 88 Ermatchkov rows at ≤49 wt% MDEA, including the 29 rows below 7 kPa. The 13 higher-concentration rows and the complete 33-row low-pressure subset are separate comparisons. Nitrogen headspace is not modeled. These are conditional physical assessments of the declared model against outside-fit data. Fitted errors are calibration evidence; phase searches, derivative comparisons and balances are numerical verification. There is no absorber-use qualification or universal-ion-parameter claim.

## Model, inputs and selection

The liquid contains water, CO₂, MDEA, MDEAH⁺, bicarbonate, carbonate, hydronium and hydroxide; only neutral species enter the vapor. Variant A uses the MEA single-sphere cation convention; Variant B uses the charged-molecule convention. The shared MEA components, interactions and reaction laws remain frozen in the main fits. The MDEA–water interaction is linear in temperature, initialized from the Kim pre-fit. Neumann ideal-gas Cp is primary, with Wangler evaluated at the same endpoints as a sensitivity. Carson is integral heat from zero loading at 101325 Pa; Jakobsen scales are 10% of each observed ratio; Böttinger is evaluated at 5 and 25 bar.

Merkley uses the native Engine observable with final loading equal to the smaller of the digitized loading point and model saturation loading at 1121 kPa (1466 kPa for the 422.04 K source rows). Only the 20/40 wt% rows at 333.15 and 388.71 K enter the objective. The reaction domain remains 293.15–395 K; the 288.71/422.04 K Merkley and 413 K Kuranov comparisons are retained as unevaluated domain refusals. The source-loading digitization uncertainty is ±0.02 mol CO₂/mol MDEA. Above Hsieh's 328.15 K, the dielectric temperature dependence is a model assumption. The intended comparison domain is ≤49 wt% for the pressure test and ≤50 wt% for other properties; 60 wt% is extrapolation.

A1, A3, B1 and B3 all converged. A2/B2 are duplicates, and A4 remains excluded. B3 has one unresolved phase record (`comparison:113:0`) and is inadmissible for selection. A1 and A3 have costs differing by less than 1e-8; the declared exact lowest-cost rule selects A3. Active bounds are accepted under the owner's MEA precedent and do not establish that these quantities are experimentally identified.

'''+table(['Endpoint','Coordinate','Target','Quantity','Value','Bounds'],bounds)+'''

## Property comparisons

Only the 88-row pressure statistic has a pass bar. Every other value below is context under the frozen data roles and residual definitions.

'''+metric_table+'''

Böttinger retains all 58 rows, their DMDEA/byproduct fractions and the flags above the source's 3% amine-balance accuracy. A complete relative bicarbonate AARD is undefined because one observed value is zero; all row-level absolute predictions remain retained. No zero row is silently removed. Xiao and Zhang remain unscored because the retained attachments contain only the first page; Derks remains unscored because temperature/basis is unresolved. Zheng uses the source loading for integral heat, with model saturation loading reported separately. Corrected Kamps never enters the follow-up criterion.

'''+wangler+'''

The complete Wangler heat/Cp and outside-fit predictions are retained in each endpoint's `wangler-*.json`. Merkley half-loading predictions and the 156 kPa alternatives are retained separately; unavailable out-of-domain rows are not averaged into an apparently complete statistic.

## Saturation truncation and phase search

The phase classifier was declared before refitting: packing fraction above 0.10 is dense; ambiguity near the threshold and other unresolved trials block a clean gate. Gas evolution is reported separately. Zero-loading searches use carbon-free trial supports. Each selected endpoint has 760 state records, including repeated physical states for distinct observables and six actual capped saturation endpoints. There are zero reconstruction trials, so no residual #904 ion-free recovery is needed. Full state/trial records and hashes are retained, rather than interpreting gas-like liquid seeds as liquid–liquid splitting.

The following loadings are mol CO₂/mol analytical MDEA. A positive truncation means the native heat endpoint is below the source loading point; the 60 wt% entries are extrapolation.

'''+table(['Endpoint','T (K)','MDEA wt%','Source loading','Model saturation','Heat endpoint','Truncation'],caprows)+'''

The saturation root is unique only within the declared 30-point search over 0.05–1.50 mol/mol; unsampled paired roots or tangencies can escape it. The gradient is unavailable exactly at the cap switch. Native refused optimizer trials remain in `fit.json`; the selected main fits converged despite their retained refusals. No fallback equation, downstream optimizer, or parameter-independent cap was substituted.

## Local identification and numerical checks

Both selected nine-coordinate Jacobians have rank 9. Their singular values use the declared coordinate scales and weighted residuals:

'''+sv+'''

The two weakest-direction bounded objective scans are retained in `local-sensitivity.json`. They are not likelihood profiles; active bounds can block their displacements. Full rank is conditional local information and does not establish universal parameter uniqueness. Each endpoint retains independent fitted-prediction replays, finite-difference comparisons, element/charge balances, solver residuals and full phase evidence. Numerical success is not physical validation.

## Bicarbonate follow-up

'''+table(['Selected start','Bicarbonate-release pressure AARD (%)','Jacobian correlation with cation–water','Control comparison','Control minus bicarbonate (points)'],follow)+'''

The owner's 2026-10-29 decision makes a phase-failed CO₂-control comparison unavailable: retain its endpoint, cost and gate states; do not compute its outside-fit AARD and make no bicarbonate claim for that variant. A bicarbonate-release AARD alone is context, not a verdict. A magnitude above 0.95 in the declared column correlation means the pair is non-separable. When a control passes, the declared margin is two AARD percentage points, with the other property results retained; corrected Kamps is excluded. No MDEA outcome falsifies the MEA bicarbonate value, whose MEA conditional uncertainty already spans the declared range.

## Engine acceptance and provenance

All new calculations use the isolated worktree MDEA environment with Engine `d513820994a78bfe628d42fffd55b2eeab6f89bd`, immutable wheel SHA-256 `ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5`. The main MEA dependency pins remain on 3e83e19c. Exact wheel path, installed-byte verification and runtime identity are in [runtime.json](results/stage2-capped/runtime.json).

Acceptance (a) passes: the historical A1/B1 754-state searches have zero reconstruction trials; every other classification is unchanged; maximum absolute change in ΔG/RT is 1.82e-12, within the owner's clarified 1e-10 absolute criterion near zero. Acceptance (b) passes: eight start values and four branch checks agree with direct saturation-plus-heat within 4.79e-13 relative, and all nine derivatives pass 1e-5 on both branches (worst more-accurate-step error 2.41e-7). Acceptance (c) passes: both 61-row Kim laws replay within 9.33e-15 relative, all 2354 binary phase searches and all mixing scans pass, and item-(l) Cp and the eight retained Carson checks pass. See the [acceptance guide](results/stage2-density/engine-d5138209/README.md).

The [selection](results/stage2-capped/selection.json), endpoint documents, row-level predictions, native failures and phase summaries own the numerical evidence. Newly retained files above 5 MB are gzipped with raw/compressed SHA-256 hashes in [the evidence registry](results/compressed-evidence.json). The manuscript and Engine source are unchanged. Historical pre-cap results remain in their existing result directories and Git history; they are not the selected endpoints shown here.

This notebook has not been independently reviewed or promoted for manuscript use.
'''
(AN/'notebook.qmd').write_text(text)
(OUT/'reported-statistics.json').write_text(json.dumps(dict(primary=plotted,metrics=metrics,Wangler_delta_points=[a['Wangler_Cp_delta_points'] for a in assessment],Merkley60_in_domain_AARD_percent=merkley),indent=2)+'\n')
print('Notebook and figure prepared from retained results')
