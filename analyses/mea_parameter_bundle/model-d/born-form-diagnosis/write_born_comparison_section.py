"""Write one notebook section from retained tables; no model evaluation."""
import csv
from assessment_section import assessment
from pathlib import Path

HERE=Path(__file__).resolve().parent
NOTEBOOK=HERE.parents[1]/'notebook.qmd'
START='# Born-form comparison: SSM+DS vs Original Born {#born-form-comparison}'
def rows(path):return list(csv.DictReader((HERE/path).open()))
def table(headers,values):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in values)+'\n'

def main():
    base={r['name'][-2:]:r for r in rows('key-objective-evaluations.csv') if r['name'] in ('baseline-11','baseline-00')}
    group=table(['Target group','Targets','SSM+DS cost','Original Born cost','SSM+DS − Original'],
        [[label,n,f'{float(base["11"][key]):.6f}',f'{float(base["00"][key]):.6f}',f'{float(base["11"][key])-float(base["00"][key]):+.6f}']
         for key,label,n in [('pressure_cost','Pressure',48),('bottinger_cost','Böttinger species',40),('matin_cost','Matin species',72),('cost','Full historical objective',160)]])
    sp=rows('runs/tables/objective-species-costs-and-signed-residuals.csv')
    species=[]
    names={'HCO3-':'HCO₃⁻ + CO₃²⁻ pool','MEA':'MEA','MEAH+':'MEAH⁺','MEACOO-':'MEACOO⁻','MEA + MEAH+':'MEA + MEAH⁺'}
    for source in ('Matin','Bottinger'):
        for name in names:
            pair=[next(r for r in sp if r['evaluation']=='baseline-'+f and r['source']==source and r['species']==name) for f in ('11','00')]
            if not int(pair[0]['n']):continue
            species.append(['Böttinger' if source=='Bottinger' else source,names[name],pair[0]['n'],
                *[f'{float(r[key]):.6f}' for r in pair for key in ('cost','mean_signed_weighted_residual')]])
    species_table=table(['Source','Target','n','SSM+DS cost','SSM+DS signed mean','Original cost','Original signed mean'],species)
    p5=rows('p5conv-costs.csv')
    p5_table=table(['Fitted set','Form','Fitted-set cost','Full 160 re-score','Pressure','Böttinger','Matin'],
        [[('P5a: no Matin HCO₃⁻ pool (142)' if '-a-' in r['run'] else 'P5b: no Matin (88)'),('SSM+DS' if r['run'].endswith('11') else 'Original Born'),
          *[f'{float(r[key]):.6f}' for key in ('fitted_cost','full_cost','pressure_cost','bottinger_cost','matin_cost')]] for r in p5])
    p4=rows('p4refit-costs-and-reaction-coordinates.csv')
    p4_table=table(['Form','Full 160 cost','Pressure','Böttinger','Matin'],
        [[('SSM+DS' if r['run'].endswith('11') else 'Original Born'),*[f'{float(r[key]):.6f}' for key in
           ('cost','pressure_cost','bottinger_cost','matin_cost')]] for r in p4])
    p4_table+='\n'+table(['Form','Carbamate δ','Carbamate ΔH, kJ/mol','Bicarbonate δ','Bicarbonate ΔH, kJ/mol'],
        [[('SSM+DS' if r['run'].endswith('11') else 'Original Born'),*[f'{float(r[key]):.6f}' for key in
           ('carbamate_delta_lnK','carbamate_delta_H_kJ_mol','bicarbonate_delta_lnK','bicarbonate_delta_H_kJ_mol')]] for r in p4])
    p1=rows('p1-loading-range-changes.csv')
    reaction_table=table(['Reaction','Original Born on its path','SSM+DS on that same path'],
        [[reaction,*[f'{float(next(r for r in p1 if r["path"]==path and r["mass_fraction"]=="0.3" and r["T_K"]=="313.15" and r["reaction"]==reaction)["change_over_retained_loading_range"]):+.6f}'
                     for path in ('own-00','common-11-on-00')]] for reaction in ('R1','R2','R3','R4','R5')])
    text=r'''# Born-form comparison: SSM+DS vs Original Born {#born-form-comparison}

**The Born-form ranking depends on which species observations enter the fit.** Original Born has the lower cost on the historical 160-target objective, 40.201537 against 47.625767 for SSM+DS. After removing Matin's 18 bicarbonate-pool targets, the converged 142-target fits favor SSM+DS, 32.991897 against 34.584032. Both forms are reported here. This is an application of the modified Born term to reactive MEA–CO₂–H₂O extending [Figiel et al. (2025)](#ref-10), whose parameter estimation and results concern ion solvation, salt activities and aqueous/organic solvent mixtures (Model Parameters, Tables 2–5; Results, Figs. 4–9). It does not establish an intrinsic ranking of the two Born forms.

The historical 160-target calculations, the 142-target sensitivity fits and the exploratory reaction fits have different data or adjustable coordinates. They are distinguished throughout. The preceding decision-23 assessment concerns the older 160-target records; the assessment of the 142-target records is pending below. The <a href="model-d/born-form-diagnosis/diagnosis.qmd" download="diagnosis.qmd">detailed diagnosis.qmd record</a> retains the original probes; [the convergence record](model-d/born-form-diagnosis/p5conv-results.qmd) retains the later P4/P5 fits. Both use numerical evidence from installed wheel `28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`.

## Formulation and question

The question is whether the SSM+DS cost penalty in this MEA application follows from the inherited Born diameters, solvent factors, dielectric-saturation correction, or reduced composition sensitivity after the five interaction coordinates are fitted. SSM means the solvation-shell modification; DS means dielectric saturation. The implemented relations are the Engine equations `born_outer_shell_diameter`, `born_radial_charging_work` and `born_residual_helmholtz`:

$$
f_{\mathrm{mix}}=\frac{\sum_k x_k f_k}{\sum_k x_k},\qquad
D_i=d_i^{\mathrm{Born}}\left[1+c_{\mathrm{shell}}\frac{f_{\mathrm{mix}}-1}{|z_i|}\right],
$$

$$
W_{\mathrm{Born}}=\sum_{i\in\mathcal I}x_i z_i^2
\left[\frac{1-\varepsilon_{\mathrm{bulk}}^{-1}}{D_i}
+c_{\mathrm{dielectric}}(1-\varepsilon_{\mathrm{ion}}^{-1})
\left(\frac1{d_i^{\mathrm{Born}}}-\frac1{D_i}\right)\right],
\qquad
a^{\mathrm{Born}}=-\frac{e^2}{4\pi\varepsilon_0 k_B T}W_{\mathrm{Born}}.
$$

Here $a^{\mathrm{Born}}$ is the dimensionless residual Helmholtz contribution, $z_i$ is ionic charge number and $\mathcal I$ is the set of ions. Distances are expressed in consistent units, with metres in the SI prefactor; the retained diameter parameters are in Å. SSM+DS is $(c_{\mathrm{shell}},c_{\mathrm{dielectric}})=(1,1)$ and Original Born is $(0,0)$. At $c_{\mathrm{shell}}=0$, $D_i=d_i^{\mathrm{Born}}$, so the saturation correction vanishes; the retained equality evaluation verifies that $(0,1)$ equals $(0,0)$.

Figiel's Born Term, Eqs. (5)–(10), pp. 9407–9409, provides the shell and solvation-factor construction; Table 1, p. 9409, gives $\varepsilon_{\mathrm{ion}}=8$, and Model Parameters, Table 2, p. 9411, gives $f_{\mathrm{water}}=1.5$. The Engine equation record attributes its canonical charging form to corrected Eq. (7); the correction text was not separately verified in this source reading. The installed Engine averages $f_k$ over all nine components, including ions. With the baseline $f_{\mathrm{MEA}}=1$ and unit factors for CO₂ and the ions, $f_{\mathrm{mix}}=1+0.5x_{\mathrm{water}}$. Consequently, the shell diameter depends on ionic content and the Born contribution can enter water activity. Model D retains solvent-only bulk permittivity; it does not add explicit ion suppression to that mixing rule.

## Fit basis and source methods

The historical fit uses **160 targets at 84 declared states**, with a CO₂-free feed basis of **30 wt% MEA in water**: 48 pressure targets at 40/60 °C, 40 Böttinger species targets and 72 Matin species targets. The same five interaction coordinates and bounds are used for the two forms. The weights define dimensionless residuals and cost:

$$
r_p=\frac{\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})}{0.3},\qquad
r_x=\frac{x_{\mathrm{calc}}-x_{\mathrm{obs}}}{0.1x_{\mathrm{obs}}+0.001},\qquad
C=\frac12\sum_j r_j^2.
$$

The species targets are liquid mole fractions; a positive signed residual means the model lies above the observation. The bicarbonate target uses the retained HCO₃⁻ + CO₃²⁻ pool. These weights are the declared fitting scales, not independently measured experimental standard deviations. The 80 °C isotherm is outside this fit. P1 additionally describes the 15 and 45 wt% states on common composition paths; those descriptive probes do not enlarge the fitted domain.

[Matin et al. (2012)](#ref-6) use acid/base titration, total alkalinity and CO₂ loading at ambient pressure and temperature (Experimental Section, pp. 6614–6615; supplementary Table S1). Their figures label the measurements **21 °C**; the retained packet uses **20 °C**. Their Speciation Comparisons discussion reports bicarbonate above Jakobsen's NMR values, especially at loading 0.3–0.45 (Fig. 2, p. 6616), and compares their 21 °C results with Böttinger's 20 °C results (Fig. 3, p. 6617). Their MEA, MEAH⁺ and carbamate comparisons are closer to NMR. This source-method distinction is retained rather than correcting the data by the fitted residual.

[Böttinger et al. (2008)](#ref-8) use online quantitative ¹H/¹³C NMR (§3, pp. 132–134; MEA results in §7, Figs. 6–7). Fast proton exchange permits measurement of **MEA + MEAH⁺ as a sum**, rather than separate free and protonated MEA observations. Bicarbonate is quantified by ¹³C NMR, and the authors describe carbonate as practically absent under their conditions. Different measurement methods, temperatures, loading coverage and reported species prevent treating the residual signs alone as proof of experimental inconsistency.

## Historical full-objective costs and signed residuals

The two retained optima were re-evaluated on the same pinned wheel. The 7.424230 cost gap is concentrated in Matin: its cost is 11.341018 higher for SSM+DS, while pressure and Böttinger favor SSM+DS by 1.777157 and 2.139631. Matin's bicarbonate pool contributes 6.023860 of the net gap.

'''+group+'\n'+species_table+r'''
Signed means in the table use the same weighted residuals as the cost. There are no separate fitted Böttinger MEA or MEAH⁺ targets and no fitted Matin MEA + MEAH⁺ sum; absent target groups are not zeros.

![The historical 160-target cost favors Original Born because Matin species outweigh the pressure and Böttinger advantages of SSM+DS. The right panel separates the species costs; Matin's bicarbonate pool contributes 6.02 of the 7.42 net cost gap. Bars represent categorical target groups at each form's own retained optimum, with dimensionless weighted least-squares costs.](model-d/born-form-diagnosis/figures/born-cost-by-group-and-species.svg){#fig-born-cost-groups fig-alt="Two panels of categorical costs for SSM plus dielectric saturation and Original Born: full objective and source groups on the left, species groups on the right."}

## Fixed-interaction scans A–D

These are exploratory one-dimensional scans with the five $k_{ij}$ coordinates fixed at each form's retained optimum. They are complete historical **160-target** evaluations where available, not new parameter fits or an assessment of the 142-target objective. A varies water and MEA solvation factors in SSM+DS; B varies ion-region relative permittivity in SSM+DS; C multiplies all ion Born diameters in both forms; D varies the MEA relative-permittivity input in both forms.

Within A's sampled values, $f_{\mathrm{water}}=1.5$ and $f_{\mathrm{MEA}}=1$ give the lowest costs, 47.625767. In B, $\varepsilon_{\mathrm{ion}}=8$ gives the lowest available sampled cost; the value 2 is unavailable. C gives costs 39.114436 and 39.142415 for Original Born at diameter multipliers 0.8 and 0.9, compared with 40.201537 at 1.0; SSM+DS gives its lowest sampled cost at 1.0. D gives SSM+DS costs 48.802928, 47.625767 and 47.025516 at MEA permittivities 24, 32 and 40, while Original Born gives 39.081604, 40.201537 and 43.422158. These sampled responses cannot establish optimal parameter values after refitting the interactions.

![The fixed-interaction response depends on both the varied input and the Born form. A and B show SSM+DS only; C and D show both forms at their own retained interaction coordinates. Lines connect the retained samples of continuous input scans; they add no evaluated points. A and B use logarithmic cost axes. The εion = 2 solve is unavailable and has no plotted cost.](model-d/born-form-diagnosis/figures/born-fixed-k-scans.svg){#fig-born-fixed-scans fig-alt="Four panels showing retained cost against solvent factor, ion-region permittivity, Born-diameter multiplier and MEA permittivity, with the unavailable ion-permittivity case marked without a cost."}

## Born activity contributions and local hypotheses

P1 evaluates Born chemical-potential differences at identical temperature, density and composition and subtracts the infinite-dilution pure-water reference at 101325 Pa. Its reaction quantity is the dimensionless Born part of $\sum_i\nu_i\ln\gamma_i$. On the common 30 wt% composition path at 313.15 K, the changes over the retained loading range are:

'''+reaction_table+r'''
The magnitudes increase for R1–R3 and R5 in SSM+DS, while R4 decreases and changes sign. **P1 therefore shows no uniform attenuation of reaction activity sensitivity.** The 15 and 45 wt% common-path tables retain the additional concentration dependence. The simple per-ion charging-kernel ratio $d_i/D_i$ is not the full reaction sensitivity.

The Born part of $\ln a_{\mathrm{water}}$ and its SSM+DS − Original difference were evaluated at each Matin and Böttinger state, both at their own compositions and on the common composition path. For the 18 fitted Matin bicarbonate targets, its rank correlation with the weighted residual difference is **0.733746**; the common-path calculation gives the same rank correlation. Including the report-only retained Matin state gives **0.773684, n = 19**. The common path separates the composition-coupling association from a speciation shift, but **this remains descriptive association, not causal attribution**. [Per-state activities](model-d/born-form-diagnosis/p1-matin-bottinger-born-activities.csv), [correlations](model-d/born-form-diagnosis/p1-rank-correlations.csv) and [the association plot](model-d/born-form-diagnosis/matin-water-activity-association.svg) retain the decomposition.

P2 uses exact Engine interaction columns and two-step finite-difference Born-input columns, with relative steps $10^{-4}$ and $10^{-5}$, pointwise agreement tolerance $10^{-3}\max(|J_1|,|J_2|)+10^{-8}$ and one larger-step retry. No entry is dropped or zeroed; a column that still disagrees is unavailable. Bounds are engineering analog envelopes from Figiel's Model Parameters, Tables 2–3, p. 9411: 2–5 Å for the non-proton ions, 1–2 Å for H₃O⁺ and 1–2 for $f_{\mathrm{MEA}}$, with local displacements at most half the interval width. These are not measured MEA-ion bounds. The declared reduction screens are 3.71 cost units for at least half of the original gap, below 1.86 for not supported locally, and an inconclusive band between them.

| Hypothesis | Retained P2/P3 finding | Classification against the declared falsifier |
|:--|:--|:--|
| (a) Inherited Born diameters account for the gap | Main-ion local prediction: 4.072221 reduction; confirming five-interaction refit converged at 43.950877, a 3.674890 reduction, below 3.71. The secondary-ion group includes an unavailable H₃O⁺ derivative. | **Inconclusive**; at least half accounted for was not confirmed. |
| (b) Shell/MEA solvation-factor directions account for the gap | Bounded local predicted reduction 3.072805; no confirming refit under the accepted best-group selection. | **Inconclusive**. |
| (c) The dielectric-saturation correction accounts for the gap | Local saturation-direction reduction is zero (**not supported locally**); (0,1) = (0,0) is verified, but the (1,0) comparison has no complete objective. | **Unavailable** for the finite-form comparison. |
| (d) Reduced composition sensitivity explains the remaining gap | P1 shows no uniform attenuation; unavailable and unconfirmed parameter groups prevent the proposed elimination argument. | **Inconclusive**. |

The H₃O⁺ column has only 157 of 160 entries agreeing after its retry, so the joint P2/P3 group is unavailable. This derivative-quality result is distinct from a failed equilibrium solve and supplies no physical falsification. [Screening table](model-d/born-form-diagnosis/p2-screening.csv), [step agreement](model-d/born-form-diagnosis/p2-step-agreement.csv) and [confirming refit](model-d/born-form-diagnosis/p3-best-group-confirmation.json) retain the numerical basis.

## Reaction directions and converged Matin-role fits

P4 adds carbamate and bicarbonate offset and enthalpy directions, with $\delta$ a natural-log equilibrium-constant shift at 313.15 K and $\Delta H$ in kJ/mol:

$$
\Delta\ln K(T)=\delta-\frac{1000\Delta H}{R}(1/T-1/313.15),
\qquad |\delta|\leq1,\quad |\Delta H|\leq10\;\mathrm{kJ\,mol^{-1}}.
$$

The reduced directions are carbamate R2 − R4 − R5 and bicarbonate R2 − R5. They map to recorded reaction changes $\Delta R2=\mathrm{bicarbonate}$ and $\Delta R4=\mathrm{bicarbonate}-\mathrm{carbamate}$, for both offsets and enthalpies. R1, R3 and R5 remain fixed and all nine species remain in the equilibrium calculation. Reaction gradients have **finite-difference quality**, alongside exact Engine interaction gradients; no covariance is estimated.

The later P4 warm refits freed the five interaction coordinates and all four reaction coordinates. Their returned full-objective costs are **43.67 for SSM+DS and 32.29 for Original Born**:

'''+p4_table+r'''
Both stopped at the remaining-time guard after four accepted steps and four complete Jacobians, **without convergence**. The carbamate $\Delta H$ reaches its **+10 kJ/mol bound in both**. The last accepted point has a complete objective but no new Jacobian. All 32 completed reaction columns pass the agreement rule; one SSM+DS bicarbonate enthalpy column required the permitted retry. The source-correlation combinations before EOS conversion are not measured reduced-reaction constants or absorption heats. These unfinished local fits leave Original Born lower on the full data, but do not establish a converged reaction-adjusted ranking.

P5 changes the fitted target set while keeping the five interaction bounds and weights, source reactions and Born inputs fixed. All four warm fits converged on the native relative function tolerance $10^{-12}$, with zero or one further accepted update from the capped records. **HCO₃⁻–water is at its +0.5 bound in every P5 fit**; Original Born also reaches the cation–anion −1 bound.

'''+p5_table+r'''
SSM+DS is lower on the fitted 142- and 88-target sets, while every full 160-target re-score favors Original Born. Its reduced-set advantages are 1.592135 and 6.378265 cost units. The latter is sensitivity to removing all Matin targets, not the new official fit definition. [Converged costs](model-d/born-form-diagnosis/p5conv-costs.csv), [interaction coefficients and bounds](model-d/born-form-diagnosis/p5conv-k-coordinates.csv) and [species costs with signed means](model-d/born-form-diagnosis/p5conv-species-costs-and-signed-means.csv) retain the exact values.

![The form ranking reverses on the reduced fitted sets and reverses again when those points are scored on all 160 targets. Compare forms within each target set; the absolute cost magnitudes across 160, 142 and 88 targets use different numbers of observations. P5a and P5b are converged local fits of the five interaction coordinates.](model-d/born-form-diagnosis/figures/born-p5-ranking-reversal.svg){#fig-born-p5-ranking fig-alt="Two panels: fitted costs for the historical full, no-Matin-bicarbonate and no-Matin objectives, followed by full 160-target re-scores of the two reduced-set fits."}

## Unavailable solves and limits

The two unavailable cases reproduce exactly on the pinned wheel at 313.15 K: the (1,0) shell-only target at `vle_obs_0119`, and scan B at $\varepsilon_{\mathrm{ion}}=2$ at `vle_obs_0193`. [tannerpolley/ePC-SAFT#201](https://github.com/tannerpolley/ePC-SAFT/pull/201) diagnoses the conserved-carbon balance (row 16) in both; case 1 also fails the total-MEA balance. Continuation reaches a fold, or turning point, before each target: near $c_{\mathrm{dielectric}}=0.33$ for case 1 and $\varepsilon_{\mathrm{ion}}=2.018$–2.031 for case 2, with a returning segment above 2.

Along those branches the dimensionless Born contribution becomes more negative, from about −5 to −17 in case 1 and −22 to −52 in case 2; OH⁻ in case 1 or H₃O⁺ in case 2 reaches about 0.8–1 mol%. Bounded Newton probes and alternate starts found no target root. **No solver defect is demonstrated and no Engine runtime repair was made.** Disconnected solutions are not excluded, so global nonexistence remains undetermined. At the specified loading and retained SSM+DS interaction coordinates, these Born settings take the model outside the usable region of the connected bubble-state branch. Both cases remain **unavailable for attribution, now with a diagnosed cause**; they do not rank the fitted forms. The frozen requests and parameters remain in [engine-handoff/](model-d/born-form-diagnosis/engine-handoff/).

The completed values are **numerical verification and local fitting evidence, not physical validation**. They do not establish an intrinsic ranking, concentration transfer, a global optimum, caloric performance or adoption of either parameter record. Active bounds, engineering probe intervals, finite-difference quality, the Matin 21 °C versus packet 20 °C convention, source-method differences and the unconverged P4 refits limit interpretation. The original P2/P3 falsifiers concern the historical 160-target gap; they are not redefined after the objective change. The physical use remains limited by the pending 142-target assessment and delivered review. This new section has not been independently reviewed or promoted for manuscript use.

## Assessment of the 142-target records

Pending: the separate assessment worker owns the decision-23 assessment of `p5conv-a-11` and `p5conv-a-00`. Its `assessment-p5a-*` results will be inserted here after completion and review. No assessment result is assumed in this subsection.

## Decisions

The owner made [decisions 24 and 21 on 30 September 2026](https://github.com/tannerpolley/MEA-Thermodynamics/issues/121#issuecomment-5906843564). **Decision 24 makes Matin's 18 HCO₃⁻ + CO₃²⁻ pool targets report-only**, based on the authors' high-bicarbonate titration/NMR comparison; Matin's MEA, MEAH⁺ and MEACOO⁻ targets remain fitted. The official objective is now **142 targets**. **Decision 21 chooses SSM+DS**, based on its converged decision-24 cost of 32.991897 against 34.584032 for Original Born, a 4.6% advantage relative to Original Born. The choice is gated on the decision-23 assessment of both 142-target records—104-row 40–80 °C pressure AARD against the 35% limit, packet and canonical completeness, 15/45 wt% transfer, the 80 °C comparison, carbonate against Jakobsen and the indicative NaHCO₃ check—and a **Supported delivered review of that assessment and this comparison section**. The earlier intended adoption scope remains 30 wt% MEA at 40–80 °C; the gates are pending and no record is adopted here.

'''

    begin=text.index('Pending: the separate assessment worker')
    end=text.index('## Decisions',begin)
    text=text[:begin]+assessment()+text[end:]
    text=text.replace('the assessment of the 142-target records is pending below','the completed numerical assessment of the 142-target records is reported below')
    text=text.replace('[the convergence record](model-d/born-form-diagnosis/p5conv-results.qmd)', '<a href="model-d/born-form-diagnosis/p5conv-results.qmd" download="p5conv-results.qmd">the convergence record</a>')
    text=text.replace('The physical use remains limited by the pending 142-target assessment and delivered review.','The physical use remains limited by the 142-target assessment results and pending delivered review.')
    text=text.replace('the gates are pending and no record is adopted here.','the numerical assessment is complete, the Supported delivered-review gate is pending and no record is adopted here.')
    # Raw prose keeps single LaTeX escapes; only the literal doubled escapes above are normalized.
    text=text.replace('\\\\','\\')
    original=NOTEBOOK.read_text()
    if START in original:
        begin=original.index(START);end=original.index('# Selected parameters',begin)
        updated=original[:begin]+text+original[end:]
    else:
        assert original.count('# Selected parameters')==1
        updated=original.replace('# Selected parameters',text+'# Selected parameters',1)
    assert updated.count(START)==1
    NOTEBOOK.write_text(updated)
    print('Updated one Born-form comparison section from retained tables.')

if __name__=='__main__':main()
