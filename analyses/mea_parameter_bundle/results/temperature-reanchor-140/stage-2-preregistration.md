# Independent R4/R5 temperature estimation, issue 140, Stage 2

## Question, authority and stopping point

Can independent dilute-solution chemical temperature information replace the
source R4/R5 laws while preserving the ≤60 °C loaded-solution fit and reducing
the frozen 80 °C pressure error? The owner decision dated 2026-10-01 in
[issue 140](https://github.com/tannerpolley/Amine-Thermodynamics/issues/140)
authorizes Stage 2, the subsequent low-temperature fits, and scoring, and skips
the deferred folds. This document is the immutable local preregistration
snapshot. Base: `cc508d1`, branch `work/140-temperature-reanchor`.

**No source or loaded-solution fit has run for Stage 2.** An independent
readiness review precedes both kinds of fit. The source evidence leaves the
admission decisions below unresolved; the proposed diagnostic estimation does
not override the issue's instruction to stop on unresolved activity convention
or source uncertainty. A Ready review and resolution of required admission
decisions precede execution. A complete numerical miss remains evidence; an
unavailable quantity or unfinished solve does not establish model failure.

Done means source coefficients, covariance with its statistical assumptions,
row residuals and enthalpy comparisons; at most eight low-temperature fits;
selection and a local committed freeze before any new ≥80 °C evaluation;
unchanged assessment metrics compared with adopted and Phase B records; the
existing notebook updated from retained values; independent delivered review;
local commits only. No parameter promotion or manuscript change is authorized.

## Source identities and rows

Extraction commit: `1e92af1` in the main checkout. Read by `git show`, never
by a changing working copy. `stage-2-inputs.json` records complete-file hashes,
selected source rows, source conventions, and live PDF hashes. Original source
CSV files remain under their existing Data owner. Extraction review establishes
transcription, not model-basis admission.

| Quantity | Selected rows | Excluded from estimation and selection |
|---|---|---|
| Kim 2011 Table 7, This work Exp, MEA ln Ka | 298.15, 313.15, 323.15, 333.15 K, four rows | Literature/Corr columns and all rows >333.15 K |
| Kim 2011 Table 12, This work Exp, MEA protonation heat magnitude | 298.15, 313.15, 333.15 K, three rows, comparison only | All rows >333.15 K; heat not fitted |
| Aroua 1999 Table 3, MEA zero-I K1 | 298, 308, 318, 328 K, four rows | Table 2 finite-I Kc, species calculations, DEA column, Table 4 literature/VLE comparisons |

Finite-I and extrapolated zero-I constants are from the same Aroua campaign,
and cannot be counted as 52 independent chemical observations. Added NaClO4
concentration is not total ionic strength. No finite-I extrapolation is repeated:
the zero-I Table 3 values own that source transformation. The inconsistent
Results prose temperatures do not replace the verified Table 3 temperatures.

Sources actually read: Aroua PDF `L8GDWZEW/93Y7NVMH`, pp. 887–891,
especially reaction (i), Eqs. 1–5/12–14, Tables 1–3, Results and Conclusion;
Kim PDF `89KKLDUF/7R3LYF7R`, §§2.2/3.1/3.3, Eqs. 4–6, Tables 7/12 and
Conclusion. Both live PDF hashes match the extraction inventory. Neither has
a Markdown companion in the live Companion source view; no conversion or
library write was made. Böttinger 2008 §§4–6 and Table 5 establish the existing
molality/solvent conventions and selective chemical estimation precedent.

## Conversion equations and limits

**S2-E1 — activity bases.** Let m°=1 mol/kg H2O, c°=1 mol/L, and
q(T,p°)=rho_water(T,p°) m°/c°, where rho_water is in kg/L. At infinite
dilution c_i/c°=q m_i/m°. Solute activity coefficients tend to one on their
respective aqueous infinite-dilution scales. For a reaction with net solute
stoichiometry Δν_s, K_c=q^(Δν_s) K_m. Solvent activity is Raoult-normalized
and tends to one. Converting a finite-I apparent quotient by this relation
alone is invalid: its activity coefficients and water activity remain needed.

**S2-E2 — R4.** Aroua reaction (i) is
MEA + HCO3− ⇌ MEACOO− + H2O. Its Eq. 1 is
Kc_dim=[MEACOO−]/([HCO3−][MEA]) in L/mol; Eq. 2 applies solute activity
coefficients; the water factor is omitted. Table 3 is the I→0 extrapolation,
where water activity tends to one. Thus its dimensionless concentration
formation constant is Kf_c=c° K1_dim. Δν_s=−1 and

    Kf_m = q Kf_c
    K4_m = 1/Kf_m = 1/(rho_water m° K1_dim)
    ln K4_m = −ln(K1_dim c°) − ln q.

R4 is exactly the reverse reaction, so no R2/R3/R5 combination is required.
The finite-solution model quotient remains
a_MEA^m a_HCO3^m/(a_MEACOO^m a_water); water activity is not deleted from
the model. If instead a CO2 + 2MEA ⇌ MEACOO− + MEAH+ constant had been
reported on the same basis, the algebra would be
ln K4=ln K2−ln K5−ln Knet. That is not Aroua's reported reaction.

For an exact T-dependent source conversion,
ΔH4_m=−ΔHf_c−R T² ∂T ln q. Reversing the reaction reverses the chemical
enthalpy sign; conversion contributes the density derivative as well.
Published Eq. 14, −0.934+671/T in log10 formation units, is not copied as a
new fit. The old Tong-derived 2.151−1545.3/T is a historical comparator.

Proposed density convention: reuse `water_reference` in
`scripts/verify_temperature_reference.py` (Wagner–Pruss 2002, Eqs. 2.5–2.6)
to calculate saturated-liquid pure-water density at the four source
temperatures. Multiply its mol/m³ result by 0.01801528 kg/mol /1000 L/m³.
This is an explicitly disclosed approximation to ambient-reference density;
the Aroua experimental reference pressure is not quantified. Do not silently
call the saturated-density conversion an exact ambient-pressure conversion.
Admission must settle whether this approximation is acceptable here.

**S2-E3 — R5.** The model direction is
MEAH+ + H2O ⇌ MEA + H3O+. With the accepted hydrated-proton reference,
the proton represents H3O+−H2O and
K5_m=a_MEA^m a_H3O^m/(a_MEAH^m a_water). In the aqueous infinite-dilution
limit, this maps to the proton-dissociation Ka on the molal proton scale.
If Kim's operational pH is on that conventional scale,

    ln K5_m = ln Ka_Kim = −ln(10) pKa_Kim.

No 55.51 factor or water-molality factor applies under that interpretation.
If a literal infinite-dilution mole-fraction constant were supplied instead,
Δν_s=+1 gives K5_m=K5_x/(M_water m°), adding 4.016534992299479 to ln K.
Those are different source interpretations, not interchangeable fits.

Kim §2.2 defines pKa as measured pH at half equivalence using calibrated
buffers; §3.1 assumes the 0.01 mol/kg constants equal infinite dilution from
an MDEA comparison, without a MEA-specific extrapolation. Its general Eq. 4
and notation define gamma_i x_i with x_i a mole fraction, but do not supply
the numerical pH-to-reference transformation for Table 7. Table 7 comparison
with Bates and Böttinger's explicitly molal Table 5 supports the operational
molal interpretation; that is an inference, not an explicit Kim declaration.
Readiness must establish that inference or return the admission choice to the
owner. No fitted pressure may be used to choose the interpretation.

## Source-only coefficient estimation and uncertainty

**S2-E4 — fitted form.** For each reaction use unweighted linear least
squares on the converted four ln K values, centered at T0=313.15 K:

    ln K(T) = L0 + B (1/T−1/T0) = A+B/T, A=L0−B/T0.
    ΔHr° = −R B; ΔHp°(MEA+H+→MEAH+) = +R B5.

No fitted C ln T or D T is admitted. Four temperatures spanning 30–35 K and
three nearly constant low-T heat magnitudes do not separately establish
curvature. Kim's full-temperature fitted Table 5 coefficients, which use
high-T chemical/heat data, cannot enter this exclusion experiment. R4's
conversion includes density at each input T before the two-coefficient fit;
the fitted enthalpy is the derivative of that fitted molal law, not the raw
inverse Aroua law with its density correction omitted.

No loaded-solution datum, historical fitted interaction, high-T chemical
coefficient, absorption heat, or high-T score enters either chemical fit.
Report (L0,B), (A,B), covariance in both parameterizations, coefficient
correlation, residuals, degrees of freedom, singular values and source domains.
OLS covariance is s²(XᵀX)⁻¹, with s²=sum(residual²)/(4−2), transformed
linearly to (A,B). It is conditional on independent, equal-variance residuals.
It does not recover unreported source systematic uncertainty or campaign
correlation. Propagated fitted enthalpy variance is R² Var(B).

**Admission limit:** Aroua Table 3 has no point uncertainties/covariance.
Eq. 14 gives coefficient standard errors 0.272 and 85 K, without their
covariance. Table 2's maximum-deviation concentration uncertainties and summed
relative Kc errors cannot be reassigned to Table 3 as independent standard
deviations. The proposed residual-only covariance is a diagnostic statistical
estimate, not measured uncertainty. The issue explicitly stops on a source
uncertainty gap: owner acceptance of this bounded diagnostic use is required
if that gap remains after review.

Kim reports ±0.02 pH, ±0.1 K and ±2.5% heat uncertainty, without a coverage
factor or covariance. Keep 0.02 ln(10) as a stated ln K uncertainty scale,
not a known one-standard-deviation error. Keep printed 0.01 ln K rounding
separately (half-step 0.005). Report temperature sensitivity after the fit;
do not fit a new errors-in-variables model. Aroua temperature control is ±0.5 K.
Comparisons use only the three selected low-T Kim heat rows: positive reported
magnitudes 49.0, 49.1, 48.9 kJ/mol correspond to negative protonation enthalpy
and positive dissociation enthalpy. These are 0.1 mol/kg measurements assumed
infinite dilution by Kim §3.1, not independent ideal-state proof. R4 is not
compared as if Kim measured carbamate hydrolysis heat. No ≥80 °C chemical or
heat row is scored until the loaded-solution record freeze.

## Conditional low-temperature refits, freeze and assessment

After Ready and source admission, retain R2 at its verified source molal
A=235.4815349922995, B=−12092.1 K, C=−36.7816, D=0; R1/R3 unchanged.
Set R4/R5 to their independent estimates as fixed inputs. Keep Engine wheel
`28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`.
Do not adopt the delivered heat wheel or add heat to the objective here.

Reuse Phase B `low-temperature-fit.py` and `assessment.py` with separate
Stage 2 output/cache paths. Do not duplicate an optimizer or generic Engine
equation. R5 A+B/T maps into the existing pKa polynomial as
b_pKa=−A5/ln(10), a_pKa=−B5/ln(10), c_pKa=0; R4 maps directly. Native
C ln(T/Tref) changes A to A+C ln Tref; source-basis declarations remain
common molality for R2/R4/R5. Verify converted ln K at source temperatures
through native coefficients within the existing 5e−13 algebra tolerance.
Declare candidate interval [293.15,353.15] K; label chemical extrapolation
outside R4 [298,328] K and R5 [298.15,333.15] K. Separate ≥100 °C scores
remain extrapolations outside that candidate interval.

The immutable Phase B preregistration owns the unchanged 84-state/142-target
selection, objective, bounds, scales, four structures and two default starts,
eight-fit cap, numerical completeness checks, 1% within-energy-branch rule,
two-start agreement, failure meaning and assessment identities. Starts:
intercepts zero or (+0.05,−0.05,+0.05,−0.05), slope zero, optional energy
169.21 or 172.5942 K. No fitted record is an optimizer start.

Preserve the fallback: constant k if within 1% of that energy branch's best
complete fit, otherwise slope k; an incomplete branch has no finalist. The
primary is the eligible finalist with fewest fitted coordinates, tied in
favor of fixed source energy. At most one secondary from the other branch.
Both starts must converge and agree under the existing tolerances. If no
structure qualifies, report incompleteness and stop: no ninth fit or retuning.
Folds are skipped by owner decision; simplicity selects the comparison record
and does not establish optimal model selection. Export, reload, low-T rescore,
hash and **locally commit** the freeze before any ≥80 °C calculation.

Run the same six ordered assessment groups once for frozen records: canonical
80 °C pressure (21 primary /19 diagnostic rows), all admitted 80 °C species,
finite-dose heat outside the objective, canonical 100–120 °C pressure (57),
15/45 wt% transfer, and never-accessed Wagner near-353 K (11) /near-392 K (12).
Reuse already retained adopted-record comparisons, not new adopted solves.
Retain AARD, RMS ln and mean ln, source/temperature groups, numerical residuals,
balance evidence, row predictions and failures; no available-row-only metric
when required rows fail. Heat retains per-isotherm RMSE and bias, run/source
groups, and the already declared dose/first-dose approximations. Preserve
the Phase B primary/secondary and adopted comparison identities exactly.

**Resources:** at most two host-wide single-thread jobs including other
worktrees; inspect running fits and wait on identified PIDs if slots are full.
OMP/OPENBLAS/MKL=1; nproc is 2. Native maximum_iterations=40, native fitter
2250 s, external timeout 2400 s. Each rescore/assessment timeout 1800 s,
each state 180 s. No hidden retries, extra starts or bounds changes. Source
OLS calculation timeout 60 s, one thread. Gross executable addition ceiling
300 lines relative to cc508d1, for source conversions/OLS outputs and minimal
changes to reuse the existing fit/assessment owners; outputs are separate.
This ceiling requires readiness acceptance before Build and cannot be raised
silently. No generic method, additional dependency or test suite is proposed.

## Falsifiers and claim boundaries

1. Unresolved source-basis mapping, unavailable uncertainty required for the
   chosen claim, or rank-deficient source estimation blocks admission.
2. Source fit disagreement with selected Kim ln K beyond its declared pH
   scale plus rounding, or implied R5 dissociation heat inconsistent with
   selected positive Kim magnitudes ±2.5%, falsifies chemical consistency
   at that stated scale. Unknown correlation/coverage prevents a probabilistic
   validation claim. Aroua residuals/covariance are reported; no invented
   measurement-normalized pass is supplied for Table 3.
3. If fixed independent chemistry cannot preserve the loaded-solution family
   costs within the existing 10% diagnostic allowance, report the conflict
   rather than changing K to match loaded-solution observations.
4. Frozen canonical 80 °C AARD >20.270257% fails the adopted no-loss condition.
   Also compare with Phase B primary 29.333590%, its secondary, and the
   matched Wagner/adopted records. Better pressure scores cannot repair a
   wrong chemical conversion or unresolved source uncertainty claim.
5. Any high-T observation/score influencing coefficients, weights, starts,
   bounds, selection or roles invalidates the temperature exclusion claim.
6. Preserve balance ≤1e−7, stationarity ≤1e−10, requested Engine tolerance,
   effective k(T)<1 checks and incomplete-state causes from Phase B.

Source estimation is a conditional correlation of dilute measurements;
coefficient algebra is numerical verification; the frozen loaded-solution
comparison is prediction conditional on historically selected SSM+DS physics
and the retained high-T binary-subsystem fits. It is not untouched physical
validation. Saturated-density approximation, Kim's infinite-dilution/proton
interpretation, Aroua's inferred activity model, missing source covariance,
active loaded-fit bounds and two-start local estimation limit the claims.
No individual loaded-solution reaction-enthalpy identification, calorimetric
constraint, concentration/stripper qualification or parameter adoption follows.
