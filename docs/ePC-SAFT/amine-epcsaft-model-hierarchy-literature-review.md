# Aqueous amine ePC-SAFT literature and model lineage

This document preserves the literature rationale and historical model choices.
The [scientific plan](../scientific/PREDICTIVE_MEA_PROGRAM.md) owns the current
estimation strategy; the established-work map `docs/scientific/CONTEXT.md` connects it to
completed studies and real gaps. Historical choices below are not instructions
to reset the current exploratory incumbent.

## 1. Historical model comparison

The historical comparison targeted one explicit-electrolyte, nine-species model with
CO2-water induced association fixed. Model selection compares only two Born
and relative-permittivity formulations:

| Configuration | Association | Electrostatic formulation |
|---|---|---|
| Shell Born, solvent-only | Schick-Pabsch reciprocal CO2-water 2B topology | Solvent-only relative permittivity |
| Shell Born, ion-suppressed | Same fixed topology | Ion-fraction-suppressed relative permittivity |

Neutral pure and binary parameters are qualified before reactive fitting.
Reactive pressure does not determine neutral binary interactions, Born
diameters, or relative-permittivity coefficients by itself.

## 2. Target system

The liquid species are CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+,
and OH-. The independent reaction set is:

1. water autoprotolysis;
2. MEA protonation;
3. carbamate hydrolysis;
4. CO2 hydration to bicarbonate;
5. bicarbonate dissociation to carbonate.

The incipient vapor contains the declared neutral species. Charged species are
liquid-only. The equilibrium calculation simultaneously enforces reaction
equilibria, elemental balances, electroneutrality, phase normalization,
mechanical equilibrium, and neutral-species chemical-potential equality.

The residual Helmholtz energy contains hard-chain, dispersion, general-site
association, Debye-Huckel, and Born contributions. The relative permittivity is
evaluated from the selected solvent-composition formulation. Reaction
correlations use one declared standard-state convention and remain fixed until
the physical parameter blocks are qualified.

## 3. Fixed induced-association topology

Schick et al. (2023), using the Pabsch et al. (2020) parameterization, assign
CO2 one donor and one acceptor site and retain reciprocal CO2-water cross
edges. The MEA implementation uses:

- one `a` and one `b` site on CO2;
- reciprocal CO2(a)-H2O(b) and CO2(b)-H2O(a) edges;
- cross energy `1212.85 K` from the arithmetic energy rule;
- cross volume `0.04509`;
- zero CO2 self-association.

This interaction represents the physical CO2-water precursor interaction. It
does not replace or duplicate carbamate formation in the explicit reaction
network. A separate CO2-MEA chemical-association edge is not used.

## 4. Literature evidence

| Source | System and useful evidence | Use in this project |
|---|---|---|
| Fakouri Baygi and Pahlavanzadeh (2015) | MEA-H2O-CO2 PC-SAFT, MEA association alternatives, Cai MEA-water VLE | Neutral MEA candidates and a source-faithful baseline reproduction |
| Uyan et al. (2015) | Explicit-ion aqueous MDEA ePC-SAFT with reaction activities and neutral isofugacity | Numerical and formulation comparison for explicit-electrolyte amines |
| Wangler et al. (2018) | Electrolyte amine phase-equilibrium calculations | Independent reactive-electrolyte implementation comparison |
| Cleeton et al. (2020) | Competitive MDEA-H2S-CO2 electrolyte calculations | Multi-acid-gas transfer and residual-trend evidence |
| Bülow et al. (2021) | MDEA, sulfolane, CO2, and H2S with Born solvation and solvent-composition permittivity | Binary-first parameter sequence and high-loading limitation evidence |
| Schick et al. (2023) | CO2 solubility in aqueous and organic electrolyte solutions | Fixed CO2-water induced-association topology and altered-Born comparison |
| Figiel, Yu, and Held (2025) | Solvation-shell-modified Born and nonlinear permittivity for electrolyte properties | Screened-Born equations, ion inputs, and independent evidence targets |

The MDEA sources demonstrate a workable sequence: qualify pure and binary
properties, freeze those values, then evaluate reactive mixtures. Their amine
and ion parameters are not transferred to MEA without matching species,
standard states, and parameter definitions.

### 4.1 Model lineage and evidence dependencies

This is the model-dependency chain used by the project, not a claim that every
later paper directly cites every earlier paper or that their fitted parameters
are transferable to MEA:

- Gross and Sadowski (2001, 2002) provide the PC-SAFT chain, dispersion, and
  association framework.
  - The MEA neutral-evidence branch runs from the Cai et al. (1996) MEA-water
    measurements through the source-backed MEA association alternatives
    evaluated by Fakouri Baygi and Pahlavanzadeh (2015).
  - The electrolyte branch begins with the Cameretti et al. (2005) aqueous
    ePC-SAFT extension and reaches reactive amine VLE through Uyan et al.
    (2015), followed by the independent binary-parameter and multiproperty
    tests of Wangler et al. (2018) and Cleeton et al. (2020).
- The electrostatic branch adds composition-dependent permittivity and Born
  solvation through Bülow, Ascani, and Held (2020, 2021), then combines the
  Pabsch et al. (2020) CO2-water induced-association treatment with advanced
  Born electrostatics in Schick et al. (2023).
- Rueben et al. (2024) and Figiel, Yu, and Held (2025) refine that branch with
  solvation-shell and dielectric-saturation corrections.
- The present MEA model joins the neutral-MEA and electrolyte branches: it
  retains the qualified MEA-water family, explicit carbamate chemistry,
  Schick-Pabsch CO2-water induced association, and the selected modified-Born
  formulation in one nine-species calculation.

Each arrow transfers a model choice or an evidence requirement. Numerical
parameters transfer only when their species definition, water family,
association topology, standard state, units, and fitted domain also match.
Canonical citation metadata and DOIs are in
[`docs/latex/manuscript_references.bib`](../latex/manuscript_references.bib);
the primary-paper reading copies and exact source identities are in
[`literature/index.csv`](../../literature/index.csv).

## 5. Parameter ownership

| Parameter family | Evidence used | Current treatment |
|---|---|---|
| H2O and CO2 pure parameters | Held/Schick/Pabsch source family | Fixed during MEA-water qualification |
| MEA `m`, `sigma`, `epsilon/k`, association topology | Pure MEA vapor pressure and density plus independent MEA-water evidence | Compare source-backed candidate families |
| `k_MEA,H2O` | Cai and additional MEA-water VLE, density, and caloric observations | Fit only after the pure family is fixed |
| `k_CO2,H2O(T)` | Physical CO2-water solubility | Fit with induced association fixed |
| `k_CO2,MEA` | Physical neutral evidence when available | Start at zero; do not infer from reactive pressure alone |
| Trace carbonate and water ions | Reviewed electrolyte sources with matched definitions | Fixed during principal-ion estimation |
| MEAH+ and MEACOO- size/dispersion | Direct and aggregate speciation, volumetric evidence, and source-backed priors | Estimate only identifiable directions |
| Born diameters and solvation factors | Solvation, transfer, and activity evidence | Fixed or independently constrained before reactive fitting |
| Relative-permittivity parameters | Unloaded and loaded solution measurements | Compare direct and screened formulations independently of pressure fitting |
| Reaction correlations | Source correlations with declared temperature domains | Fixed initially; reopen only after EOS qualification |

### 5.1 Parameter adoption and estimation ownership

The exploratory incumbent is
`analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`.
Read its [parameter history](../../analyses/mea_parameter_bundle/results/parameter-record-history.csv)
and [working notebook](../../analyses/mea_parameter_bundle/notebook.qmd) for the
later calculations. It is not an accepted MEA parameter set.
The scientific plan owns the parameter ladder and acceptance requirements;
the [volumetric synthesis](meah-meacoo-volumetric-evidence.md) and its linked
preregistration already define the detailed ionic estimation strategy.

## 6. Historical neutral qualification

### 6.1 Pure components

The retained water family uses the Held 2B parameters and its
temperature-dependent segment diameter. Candidate MEA families must be
evaluated with their own source association topology. A binary interaction
value fitted with another water or MEA family is only an initial value.

### 6.2 MEA-water

Cai et al. (1996) provide 29 isobaric VLE rows at 101.33 and 66.66 kPa. The
101.33 kPa series trains `k_MEA,H2O`; the 66.66 kPa series independently tests
pressure-level transfer. Each measured state contributes component
log-fugacity equalities. The exact Engine derivative with respect to the active
binary coordinate is checked against centered finite differences.

The source-faithful Baygi reproductions remain diagnostics because their
fixed-state residuals retain strong composition trends. The completed
Held-water comparison evaluated source-backed 2B, 3B, and 4C MEA association
families. The 3B family gave the best transfer to the independent 66.66 kPa
pressure level in that historical comparison. Upstream PR 132 superseded that
selection for the current foundation by selecting the MEA 2B scheme; 3B is not
the retained neutral authority.

### 6.3 CO2-water

Physical CO2-water data identify the temperature-dependent binary interaction
under the fixed induced-association topology. Fit and challenge pressure ranges
remain separate. The resulting `k_CO2,H2O(T)` is frozen before any reactive MEA
fit.

## 7. Historical electrostatic comparison

Both retained configurations use solvation-shell-modified Born. The historical
MEA candidate used the Figiel-style ion-fraction suppression law and its
source-fixed discrete choices. A fixed-parameter sensitivity at 313.15 K
rejected original-Born and shell-Born solvent-only controls because they found
vapor-scale rather than liquid-scale roots under that historical parameter set.
Direct dielectric, solvation, transfer, and activity observations are still
needed to constrain the retained electrostatic parameters independently.

Missing MEAH+ or MEACOO- solvation evidence does not create another freely
fitted pressure coordinate. It yields a source-centered prior or a retained
uncertainty interval whose effect is reported explicitly.

## 8. Existing estimation research

The estimation sequence is already developed in the
[scientific plan, §§4–7](../scientific/PREDICTIVE_MEA_PROGRAM.md), with the
[ionic identification strategy](meah-meacoo-volumetric-evidence.md) specifying
analog data, active coordinates, objectives, uncertainty and staged fitting.
Completed and blocked calculations are mapped in
`docs/scientific/CONTEXT.md`. Consult those records before proposing
another strategy review or treating an old implementation limit as current.

## 9. Published-work gaps and what the retained evidence adds (23 September 2026; revised 24 September 2026)

Question: where does published MEA–CO2–H2O and reactive-amine modeling stop,
and which retained results in this repository extend it? This section judges
novelty only. It does not promote a parameter set, and it does not change the
claim limits in the [working notebook](../../analyses/mea_parameter_bundle/notebook.qmd).

Manuscript direction (owner decision, 24 September 2026): a predictive paper
for Fluid Phase Equilibria built on the R4-fixed refit of candidate A
([MEA #107](https://github.com/tannerpolley/MEA-Thermodynamics/issues/107);
candidate A reaches pCO2 AARD 26.9 % on the 161 rows, draft
[PR #106](https://github.com/tannerpolley/MEA-Thermodynamics/pull/106)), with
composition-transfer validation on the 95 reserved non-30 mass % pressure rows
([MEA #108](https://github.com/tannerpolley/MEA-Thermodynamics/issues/108);
row-access audit running). Every "pre-refit record" number below comes from
the exploratory incumbent `selected-current-best-parameters.json`
(SHA-256 `868a5018…fcb7be`). Those numbers are superseded once #107 adopts a
record, and they must then be recomputed.

Evidence strength uses three labels: **numerical verification** (the
calculation represents its equations), **prediction** (model output compared
with observations that did not set the compared quantity), and **calibration
residual** (comparison with rows used to fit or select the record). No retained
result here is physical validation yet: every compared row was used in fitting
or selection, including Xu 2011 and the Kim–Svendsen 120 °C heat
([holdout ledger](../../analyses/mea_parameter_bundle/results/holdout-evaluations.csv)).
MEA #108 may supply the first physical validation, bounded to transfer across
MEA concentration at the tested temperatures and loadings, and only if its
access audit confirms those rows are untouched.

The search record, including the Scopus and Web of Science status, is in §9.6.

### 9.1 Gap map

Repository paths are relative to the repository root. "Pre-refit record" means
the exploratory incumbent named above.

| Topic | What published work does (locator) | What is missing | Retained evidence here (path) | Strength |
|---|---|---|---|---|
| Explicit-ion reactive ePC-SAFT for MEA | Explicit-ion ePC-SAFT exists for MDEA, a tertiary amine that forms no carbamate: Uyan 2015 (§3, Eqs. 12–15), Wangler 2018, Cleeton 2020, Bülow 2021a (Eqs. 1–5); the only amine ion is MDEAH+. MEA SAFT models use ideal chemistry plus a neutral EOS (Baygi 2015 §3.3; Najafloo 2018 §3.3; Nasrifar 2010 §6 lumps ions into "effective water") or association sites instead of ions (Mac Dowell 2010 §II.B; Rodriguez 2012; Perdomo 2023 Eqs. 4–14; Wang 2018 PR-CPA association scheme Fig. 1). Search results for other explicit-ion EOS work: §9.6. | No explicit-ion ePC-SAFT treatment of the carbamate-forming MEAH+/MEACOO- pair. | Nine-species, five-reaction pre-refit record; 161 pressure rows and 131 speciation targets, all evaluated (notebook §Pressure, §Speciation) | Calibration residual |
| Pressure, speciation and heat from one model | Activity-coefficient models fitted jointly to pCO2, NMR, heat of absorption and heat capacity: Hilliard 2008 (data inventory Table 13.4-2, p. 440; 35 parameters Table 13.4-3, p. 441), Zhang 2011 (Table 9), Akula 2023a (Eq. 34, Table 3). **Cleeton 2020 already does all three with one explicit-ion ePC-SAFT, for MDEA:** pCO2 (Figs. 7–9), speciation including carbonate against Jakobsen 2005 (§3.3.2, Fig. 6), and differential heat from the EOS fugacity temperature derivative plus reaction terms (Eq. 15, Fig. 10; 19.73 % against Arcis and Mathonat). Wang 2018 does all three with pseudo-chemical PR-CPA for MEA (Fig. 16; Figs. 18–19). | The same three quantities from one explicit-ion EOS for a carbamate-forming amine. | Pressure and speciation tables in the notebook; single-state heat `analyses/mea_parameter_bundle/results/reference-calorics/heat.csv` | Calibration residual (pressure, speciation); prediction (heat, 2 states) |
| Exact derivatives and sensitivities | Finite differences: Hilliard 2008 heat between T and T+1 K (Eq. 13-36, p. 429); Uyan 2015 iterates activities without derivatives (§3). Automatic differentiation of fugacities in reactive non-electrolyte PC-SAFT: Ascani 2023 (Eqs. 16–17). No amine paper read reports solved-state sensitivities. | Solved-state derivatives of a reactive electrolyte EOS equilibrium, checked against finite differences. | Temperature and pressure solved-state derivatives, relative error ≤ 1.21×10⁻⁷; kij refused and reaction-coefficient derivatives unavailable on the pinned wheel (`analyses/mea_parameter_bundle/results/runs/engine-comparison/README.md`, Derivatives); 46/46 reference-temperature actions within 10⁻⁵ of finite differences (`analyses/mea_parameter_bundle/results/reference-temperature/summary.json`) | Numerical verification |
| Modified Born (solvation shell + dielectric saturation) for amine ions | Figiel 2025 (Eqs. 5–11, Table 3): inorganic ions in water, methanol and ethanol, 298.15 K only; the authors state the diameter was not tested at other temperatures. Bülow 2021a uses the original Born term with MDEAH+ (Eq. 20). In its Results discussion of the sulfolane blends, Bülow 2021a says the deviation at loading near and above 1 "needs a careful investigation", "might be reasoned in the induced association of CO2", and that "an extended version of the model … that includes an altered Born contribution" including ionic species might be applied. Rueben 2024: permittivity for inorganic ions only. | No application to amine or carbamate ions, or to a reactive CO2–amine system, in the papers read. Temperature transfer of the solvation-shell parameters is untested anywhere. | The pre-refit record uses SSM+DS with MEAH+/MEACOO- Born diameters from a historical speciation fit (notebook species table); historical Born/permittivity comparison `analyses/mea_parameter_bundle/results/born-permittivity-study/` | Calibration residual; no independent electrostatic evidence |
| Reference-state and K(T) conventions | Conventions conflict: Austgen 1991 mole-fraction, unsymmetric (pp. 545–546; Table V, p. 547); Cleeton 2020 symmetric for water and MDEA (Eq. 8); Bülow 2021a infinite dilution in water for MDEA and calls the alternative "often misused" (Eqs. 12–13); Böttinger 2008 molality (§4). Cleeton applies an MDEAH+ constant valid at 298–333 K up to 413 K (Table 1). | An explicit conversion of mixed-source constants to one basis with a verified temperature derivative. | Common aqueous-molality conversion (`docs/ePC-SAFT/mea-reaction-and-sentinel-primary-source-audit.md`); reaction-by-reaction slope attribution `analyses/mea_parameter_bundle/results/reference-temperature/attribution.csv`, `slopes.csv` | Numerical verification |
| Speciation validation including carbonate | No source tabulates reliable directly measured MEA carbonate above loading 0.5: Böttinger 2008 "practically not present"; Jakobsen 2005 infers it from a shared peak and calls it unreliable above 0.6; Matin 2012 sets it to zero (Eqs. 18–19b); Wong 2015/2016 resolve it by Raman in figures only. MEA SAFT speciation comparisons are figures without metrics (Nasrifar Fig. 11; Baygi Fig. 8; Rodriguez Fig. 9b; Perdomo Fig. 14). For MDEA, Uyan 2015 (Figs. 3–4) and Cleeton 2020 (Fig. 6) compare carbonate. | A quantitative explicit-ion comparison with measured MEA species, and any measured carbonate target. | 131 targets with metrics by species for the pre-refit record (notebook §Speciation: MEA RMS ln 0.131, MEAH+ 0.262, MEACOO- 0.207, HCO3- 1.185). Carbonate is calculated but not scored. | Calibration residual |
| Heat of absorption from the EOS (Gibbs–Helmholtz) | Cleeton 2020 (Eq. 15): Δh from −RT²∂ln f/∂T of the explicit-ion EOS plus reaction van 't Hoff terms, 19.73 % against Arcis and Mathonat (MDEA). Wangler 2018: van 't Hoff reaction terms plus a Henry's-constant correlation for the physical term, not the EOS (Eqs. 22–31), MDEA, graphical. Wang 2018 PR-CPA for MEA: underpredicts by 49 % once carbamate forms (Figs. 18–19). Hilliard 2008 12.9 %, Zhang 2011 10.9 %, Akula 2023a 5.9 % (against Kim–Svendsen 2007 and Kim 2014 combined), all fitted to those data. | An MEA heat from an explicit-ion EOS whose Gibbs–Helmholtz identity is verified, compared with calorimetry not used for that state. | Pre-refit record: 82.06 kJ mol⁻¹ at 313.15 K, loading 0.35; 79.70 at 315 K, 0.415. Gibbs–Helmholtz identity to 2.5×10⁻¹³ and RT²·d ln pCO2/dT closure to 2.5×10⁻¹³ (`analyses/mea_parameter_bundle/results/reference-calorics/heat.csv`, `closure.csv`). Mean offset from the 10 Kim–Svendsen 2007 points at 40 °C: −1.668 and −4.032 kJ mol⁻¹ (`calorimetry.csv`). | Numerical verification (identity); prediction on calibration-labelled calorimetry (2 states) |
| Identifiability and uncertainty reporting | Activity-coefficient papers report standard errors and show non-identified parameters: Austgen 1991 correlated τ pairs (p. 549); Hilliard 2008, 18 of 35 estimates smaller than their standard errors (p. 441); Zhang 2011 ΔfH standard deviations about 40–80 times the values (Table 10); Akula 2023a correlations to 0.97 (Table 7). No SAFT MEA paper reports parameter uncertainty; Mac Dowell 2010 describes near-optimal valleys qualitatively (Fig. 2). Smith, Rutherford and Leal 2026 argue that fitting equilibrium constants and activity parameters to the same solubility data is ill-posed (abstract only read). | A quantitative test, for an MEA EOS, of which pressure residual shapes the reaction constants can and cannot absorb. | Loading-bin means remove 79 % of the residual sum of squares; ±0.3 ln K on R2/R4/R5 removes about 11 %; singular values 12.6, 4.5, 0.36; R2–R5 sensitivity correlation −0.91 (`analyses/mea_parameter_bundle/results/runs/pco2-calibration-misfit/README.md`). Screening-prior global sensitivity over 113 parameter groups (`analyses/enrtl_six_species_ideal_comparison/notebook.qmd`, §All-parameter sensitivity) | Prediction on calibration rows (diagnosis); no confidence intervals |
| Reproducibility | No paper read releases code; several use gPROMS or Aspen. | Re-executable calculations with fixed inputs. | Engine wheel, parameter record and state packet identified by SHA-256; on the 66 states both Engines evaluated, median \|Δ ln pCO2\| is 0.00112 (`analyses/mea_parameter_bundle/results/runs/engine-comparison/README.md`) | Numerical verification |

### 9.2 Ranked publishable contribution claims

These claims follow the predictive framing above. The earlier claim that the
explicit-ion model gives a negative result for pressure does not survive:
candidate A already reaches 26.9 %, and the pre-refit record's 52.5 % is
superseded once MEA #107 adopts a record. The novelty wording follows the
search in §9.6.

1. **Explicit-ion reactive ePC-SAFT for a carbamate-forming amine, validated
   across MEA concentration (contingent on #107 and #108).** Defensible
   wording: no published SAFT-family equation of state places MEAH+,
   MEACOO-, HCO3- and CO3²- in the equation of state with electrolyte
   (Debye–Hückel and Born) terms and solves the reaction equilibria with
   fugacities from that equation of state. Nasrifar 2010, Baygi 2015 and
   Najafloo 2018 carry the same ions and reactions, but as ideal species
   outside the SAFT term (§9.4). The only published explicit-ion ePC-SAFT
   treatments are for MDEA, which forms no carbamate; Cleeton 2020 is the
   closest precedent. Evidence now: the pre-refit record evaluates every
   pressure and speciation row, and candidate A reaches 26.9 % on the 161
   rows (PR #106). What establishes it: #107 adoption with its promotion
   gates, then #108 on the 95 reserved non-30 mass % rows. That would be the
   first physical validation here, limited to transfer across concentration.
   Stronger with: the per-source table of §9.3 recomputed on the adopted
   record, and the reads listed in §9.6 that are still missing
   (Neumann 2021 and the Rozmus thesis).
2. **Hypothesis tested by #107: the loading-shaped pCO2 misfit lies outside
   the reaction-constant span.** For the pre-refit record, loading-bin means
   remove 79 % of the residual sum of squares, and ±0.3 ln K on R2/R4/R5
   removes about 11 % (singular values 12.6, 4.5, 0.36; R2–R5 correlation
   −0.91). The diagnosis leaves open which of two causes is responsible: the
   fitted EOS/ionic parameters or the ePC-SAFT ionic formulation. Coverage
   limits the shape. The < 0.2 and 0.3–0.5 bins keep their signs at all five
   temperatures, and the 0.2–0.3 bin exists only at 40 and 60 °C. The ≥ 0.55
   bin is negative at 40, 60 and 80 °C, +0.03 at 100 °C (n = 3), and has one
   point at 120 °C
   (`analyses/mea_parameter_bundle/results/runs/pco2-calibration-misfit/README.md`).
   An R4-fixed ionic refit that removes the shape supports the
   fitted-parameter cause. One that cannot remove it points to the
   formulation. Published framing: Smith, Rutherford and Leal 2026 argue that
   fitting equilibrium constants and activity parameters to the same
   solubility data is ill-posed (abstract only read).
3. **Heat of absorption from the same explicit-ion EOS, as a verified
   method.** The Gibbs–Helmholtz identity and the RT²·d ln pCO2/dT closure
   hold to 2.5×10⁻¹³ (numerical verification). The method is not new:
   Cleeton 2020 (Eq. 15) computes Δh from the explicit-ion ePC-SAFT fugacity
   temperature derivative plus reaction terms for MDEA. What is added: the
   first such heat for MEA, with a verified identity. The pre-refit values
   (82.06 and 79.70 kJ mol⁻¹; mean offsets −1.668 and −4.032 kJ mol⁻¹ from
   10 Kim–Svendsen 2007 points at 40 °C, ±2.2 % reported without a coverage
   factor) must be recomputed on the adopted record. Also required: the full
   heat-versus-loading curve (MEA #96), Kim 2014 as a comparison, and the
   superseded 120 °C bias (−18.8 kJ mol⁻¹) reported with it.
4. **The bicarbonate misfit is partly a target-definition and source-conflict
   result.** Matin 2012 and Jakobsen 2005 differ by 10–20× in bicarbonate
   below loading 0.3 at 20 °C (notebook §Speciation). Böttinger 2008 and
   Jakobsen 2005 differ by up to 2.3× in carbamate above loading 0.5
   (Böttinger Table 3, Jakobsen Table A2). The Matin targets need rescoring
   against HCO3- + CO3²- (§9.5). Stronger with: digitized Wong 2016 Raman
   carbonate (Figs. 5–6), the one direct carbonate measurement.
5. **A verified reference-temperature chain for reaction constants taken
   from sources on different bases.** All 46 temperature actions agree with
   finite differences, with reaction-by-reaction attribution of
   d ln pCO2/dT. This is methods material supporting claim 3; exact
   derivatives are standard in Helmholtz-energy software and are not a
   standalone contribution.

### 9.3 pCO2 AARD at the measured loading, by dataset

All values are mean |p_model/p_obs − 1| in % on CO2 partial pressure at the
measured temperature and loading. "Pred." means no ternary data were fitted;
"cal." means the dataset was fitted. The pre-refit record column is superseded
once MEA #107 adopts a record; candidate A (26.9 % over the same 161 rows,
PR #106) has no per-source row here because its record is not adopted.

| Dataset | Pre-refit record (n) | Baygi 2015 PC-SAFT, pred.‡ | Najafloo 2018 SAFT-HR | Zhang 2011 eNRTL, cal. | Hilliard 2008 eNRTL, cal.* | Aronu 2011 e-UNIQUAC, cal. | Akula 2023a eNRTL, cal. |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jou 1995 | 56.9 (48) | 43.2 | 49.5 | 33.5 (124) | 13.6 (70) | — | 40.5 over all its 30 mass % data |
| Hilliard 2008 | 69.0 (30) | 35.0§ | 42.6§ | 35.5 (55) | 30.0 (55) | — | (same) |
| Mamun 2005 | 20.6 (19) | 21.0 | 39.96 | 13.5 (19) | 27.1 (19) | — | — |
| Xu 2011 | 48.7 (18) | 46.9 | 15.4 | 28.0 (63) | — | — | (same) |
| Aronu 2011 | 41.4 (36) | — | — | — | — | 24.3, own data, 15–60 mass % | (same) |
| Idris 2014 | 89.1 (10) | — | — | — | — | — | — |

Sources: pre-refit record from `analyses/mea_parameter_bundle/results/current-best-fit-ln-statistics.csv`;
Baygi Table 5; Najafloo Table 5; Zhang Table 9; Hilliard Table 13.4-6
(p. 447); Aronu abstract and Eq. 21; Akula 2023a Fig. 4 (30 mass %, loading
0.003–0.5, 40–120 °C). Published row counts and domains differ from these rows.

Scope: every pre-refit row is 30 mass % MEA (x_MEA ≈ 0.11) at 40–120 °C.
Baygi's overall 36.42 % covers 691 rows at x_MEA 0.02–0.16 and 298–443 K
(Table 5), mostly other concentrations. It is not a like-for-like comparison
with the 161-row value.

\* Hilliard's fit reconciles pCO2 and loading together (maximum likelihood
with errors in all variables; method in Chapter VI and Appendix L, data in
Table 13.4-2). Its pCO2 AARD is therefore not strictly the same residual
direction. Zhang 2011 uses the Aspen fitting tool without stating its error model.
‡ Baygi's "prediction" is weaker than the label suggests: it chose the Tong
2012 and Bates–Pinching constants for R4/R5 because they gave the best
ideal-chemistry agreement (text before Table 5).
§ The Baygi and Najafloo Hilliard rows span x_MEA 0.06–0.16 (3.5–11 m). The
pre-refit record uses the 7 m (30 mass %) rows only.

Excluded because the residual direction differs: Mac Dowell 2010 (absolute
deviation in x_CO2 at measured T and P, AAD 0.010), Schick 2023 and Pabsch 2020
(x_CO2 at given pressure), and Wang 2018 (total pressure, 12 %, Table 4).

MDEA values, for comparison only: Uyan 2015 34.4 % (corrected by Wangler 2018
Table 11, footnote b, from the published 22.9 %), Wangler 2018 19.7 %, Cleeton
2020 20–70 % by dataset, Bülow 2021a 32.7 % at 30 mass %.

### 9.4 Threats to novelty

- **Closest precedent: Cleeton 2020 (MDEA).** One explicit-ion ePC-SAFT gives
  pCO2 (Figs. 7–9), speciation including carbonate against Jakobsen 2005
  (§3.3.2, Fig. 6), and differential heat from the EOS fugacity temperature
  derivative plus reaction terms (Eq. 15, Fig. 10; 19.73 %). Claims must be
  limited to a carbamate-forming amine (MEA).
- **MEA with explicit ions and reactions alongside a SAFT EOS already exists,
  but with ideal ions.** Nasrifar 2010 (Eqs. 1–10, Table 1; ions lumped into
  "effective water", §6), Baygi 2015 (§3.3, a_i = x_i) and Najafloo 2018
  (§3.3) carry MEAH+, MEACOO-, HCO3- and CO3²- outside the SAFT term.
  "Explicit ions" alone is therefore not new; ions as EOS species with
  electrolyte terms is the defensible wording.
- **Non-SAFT equations of state with ions for MEA.** Neumann, Poplsteinova
  Jakobsen, Thol and Span 2021 (Chem. Eng. Sci., doi 10.1016/j.ces.2021.117261)
  combine a Helmholtz-energy multiparameter EOS with an excess-Gibbs-energy
  model for reactive mixtures. The EOS-CG-2021 paper (Int. J. Thermophys.
  44:178, 2023, Sect. 5) states that H2O+MEA+CO2 is validated against VLE,
  density and speciation data. Téllez-Arredondo and Medeiros 2013 (FPE
  344:45) use SRK + two-state association + Debye–Hückel for ionic species in
  aqueous MEA, DEA and MDEA. Neither paper has been read in full. The claim
  must say "SAFT-family", not "equation of state" or "Helmholtz-energy model".
- **Electrolyte SAFT for another carbamate-forming amine.** Najafloo, Zoghi
  and Feyzi 2015 (J. Chem. Thermodyn. 82:143) use an electrolyte SAFT-HR for
  CO2 in MDEA + AEEA; AEEA forms carbamate. Only the search summary was read.
  If its AEEA carbamate ion is an EOS species, the MEA claim still holds, but
  "only MDEA" must be dropped.
- **IFP electrolyte PPC-SAFT line.** The Rozmus 2012 thesis plans GC-PPC-SAFT
  with ions and reactions for primary and secondary amines. Its abstract
  reports strong electrolytes and CO2-free amine solutions only. Rozmus et al.
  2013 (IECR, read in full) covers alkali halides and calls amine–CO2 "the
  final aim". The thesis chapters are unread.
- **Pressure, speciation and heat from one model is not new.** It is done
  with activity-coefficient models (Hilliard 2008, Zhang 2011, Akula 2023a),
  with pseudo-chemical SAFT (Perdomo 2023, heat for MAPA, Fig. 7; Rodriguez
  2012, MEA speciation), with PR-CPA for MEA (Wang 2018), and with PR-CPA plus
  Deshmukh–Mather for MEA (Wang 2017 thesis, Figs. 5-17, 5-20, 5-21).
- **Heat and derivatives.** EOS heats of absorption for MEA exist without
  ions (Wang 2018; soft-SAFT and SAFT-VR SW papers screened in §9.6). Exact
  derivatives are standard in Helmholtz-energy software (EOS-CG-2021,
  Sect. 2.2). Neither is a headline claim.
- **Identifiability.** Smith, Rutherford and Leal 2026 argue the general
  point, and activity-coefficient papers already report non-identified
  parameters (Austgen, Hilliard, Zhang, Akula). Claim 2 is new only as the
  test #107 runs on an MEA EOS.
- **Born extension.** Bülow 2021a already proposes an altered Born term that
  includes ionic species for MDEA at high loading (Results, sulfolane-blend
  discussion).

### 9.5 Defects found in repository records

These are recorded here, not fixed, because the notebook and data belong to
their own owners.

- **Matin 2012 bicarbonate targets.** The 19 Matin HCO3- targets (loading
  0.106–0.531) are scored against model HCO3- alone
  (`data/reference/MEA/manifests/speciation_target_membership.csv`, empty
  `linear_coefficients`). Matin assumes carbonate is zero and folds it into
  bicarbonate above loading 0.25 (Eqs. 18–19b). The equivalent model quantity
  is HCO3- + CO3²-.
- **Hilliard residual direction.** Notebook §Fit statistics groups Hilliard
  2008 with the papers that report pressure at the measured loading. Its
  Table 13.4-6 values are reconciled maximum-likelihood residuals (see §9.3).
- **Idris 2014.** The notebook calls it "the paper that also reports the Raman
  speciation measurements." It reports Raman calibrations and spectra, and
  states that quantitative speciation is future work (p. 1430). Only its
  Table 2 solubility is data.
- **Figiel 2025 correction.** IECR 2026, 65, 7782 (doi 10.1021/acs.iecr.6c01415)
  corrects Eq. 7: a missing bracket, and ε_r,ion replaces ε_r,bulk in the
  second term. The local reading copy is uncorrected. Whether the Engine's
  SSM+DS term uses the corrected form was not checked.
- **Transcription conflicts in predecessor constants:** Baygi Table 4 R1 C
  = +22.4773 against Nasrifar Table 1 −22.4773; Najafloo Table 3 K3 A = 2.151
  against Baygi −1.8652. Check both PDFs before reusing either value.

### 9.6 Pre-submission search

Run 23–24 September 2026. The query the owner specified, for Scopus and Web
of Science, 2005–2026:

```
TITLE-ABS-KEY((SAFT OR "PC-SAFT" OR ePC-SAFT OR "SAFT-VR" OR "SAFT-gamma" OR soft-SAFT OR CPA OR "equation of state") AND (monoethanolamine OR MEA OR "2-aminoethanol" OR alkanolamine* OR amine*) AND (CO2 OR "carbon dioxide") AND (electrolyte* OR ion* OR carbamate OR speciation OR "heat of absorption" OR "enthalpy of absorption"))
```

**Scopus and Web of Science: not run.** Automated access failed on
24 September 2026 with the institutional VPN on:

| Endpoint | Result |
|---|---|
| `https://www.scopus.com/search/form.uri?display=advanced` | HTTP 403 (bot protection) |
| `https://api.elsevier.com/content/search/scopus` | HTTP 401, "Invalid API Key" |
| `https://www.webofscience.com/wos/woscc/advanced-search` | HTTP 200, a JavaScript application shell that needs an interactive browser session |
| `https://wos-api.clarivate.com/api/wos` | HTTP 401, "No API key found in request" |

No bypass was attempted. Running the query above in a browser, and the Scopus
"cited by" lists below, still requires the owner's institutional session.
The alternative is a key for the Elsevier Scopus Search service or the Clarivate Web of Science Expanded service.

**Open-index substitute (OpenAlex, run 24 September 2026).** The same boolean
query, with wildcards expanded to explicit plurals, as
`title_and_abstract.search` filtered to publication dates 2005-01-01 to
2026-12-31: **82 hits**. The same query over full text (`default.search`)
returned 3070 hits and was not screened. All 82 titles were screened; the
candidates are listed below.

**Forward citations (OpenAlex `cites:` filter, 24 September 2026):** Uyan 2015,
51 citing works; Wangler 2018, 38; Cleeton 2020, 21; Bülow 2021a, 21;
Figiel 2025, 9; **140 in total**. All titles were screened.

**Other searches:** OpenAlex keyword searches ("soft-SAFT monoethanolamine
carbon dioxide", 57 hits; "electrolyte SAFT monoethanolamine", 151;
"electrolyte equation of state monoethanolamine carbon dioxide speciation",
247; "ePC-SAFT alkanolamine carbon dioxide", 24; "electrolyte CPA
monoethanolamine carbon dioxide", 39; "SAFT carbamate monoethanolamine heat
of absorption", 72), first 20–25 titles each. Also a live Zotero search
(`zotero-companion zotero-search`: "ePC-SAFT advanced amine", "MDEA
ePC-SAFT", "monoethanolamine ePC-SAFT", "electrolyte PC-SAFT amine"; 0 hits).
Also general web search.

**Screening outcome.** Hits that could be an explicit-ion or reactive EOS
treatment of a carbamate-forming amine, or an EOS heat of absorption for MEA:

| Paper | Read | Outcome |
|---|---|---|
| Nasrifar 2010; Baygi 2015; Najafloo 2018 | Full text | Ions and reactions present, but ideal and outside the SAFT term; narrows claim 1 (§9.4) |
| Neumann et al. 2021, Chem. Eng. Sci. (doi 10.1016/j.ces.2021.117261) | Not obtained (paywalled); described through the open EOS-CG-2021 paper | Non-SAFT Helmholtz EOS + excess-Gibbs model for reactive MEA; narrows claim 1 to SAFT-family |
| Téllez-Arredondo & Medeiros 2013, FPE (doi 10.1016/j.fluid.2013.01.005) | Search summary only | Cubic + association + Debye–Hückel for MEA ions; outside SAFT wording |
| Najafloo, Zoghi & Feyzi 2015, J. Chem. Thermodyn. (doi 10.1016/j.jct.2014.11.006) | Search summary only | Electrolyte SAFT-HR, MDEA + AEEA; may affect "only MDEA" |
| Rozmus 2012 thesis (2012PA066320) | Abstract only; theses.fr lists it as not accessible | Planned ions + reactions for amines; reported work stops before CO2 |
| Rozmus et al. 2013, IECR (doi 10.1021/ie303527j) | Full text (Zotero) | Alkali halides only; no effect |
| Rozmus et al. 2011, FPE (doi 10.1016/j.fluid.2010.12.009) | Metadata only | Amine + alkane/alcohol, no CO2; no effect expected |
| Chremos et al. 2016, FPE (doi 10.1016/j.fluid.2015.07.052) | Abstract | SAFT-γ SW with physical association for reactions, no ions; no effect |
| Brand et al. 2016, Faraday Discuss. (doi 10.1039/c6fd00041j) | Abstract | SAFT-VR SW absorber model for MEA, reactions via physical association; no ions |
| Pereira, Llovell & Vega 2018 and Pereira & Vega 2018, Appl. Energy | Abstracts | soft-SAFT with implicit reactions; no ions |
| Lloret, Vega & Llovell 2017, J. CO2 Util. (doi 10.1016/j.jcou.2017.08.018) | Not obtained | soft-SAFT MEA model; heat of absorption reported per web summary; no ions expected |
| Raeispour Shirazi & Lotfollahi 2019/2020, FPE | Abstract (2020) | ePC_SAFT-MB (PC-SAFT + MSA + Born), MDEA only; no effect on MEA claim |
| Mehdizade et al. 2024, J. Mol. Liq. (doi 10.1016/j.molliq.2024.124441) | Title only | Electrolyte SRK-CPA, H2S in MDEA/MEA/DEA; no CO2 per title |
| Plakia, Pappa & Voutsas 2018, FPE (doi 10.1016/j.fluid.2018.09.013) | Abstract | UMR-PRU cubic EoS/GE with extended UNIQUAC ions, MEA + CO2; outside SAFT wording |
| Wang 2017 thesis (tel-01865166) | Full text (open) | PR-CPA + Deshmukh–Mather for MEA speciation and heat; no EOS ions |
| Noroozi & Smith 2020, IECR (doi 10.1021/acs.iecr.0c03738) | Abstract | Simulated K + ideal solution; no effect |

The second screening helper's detailed reads of the electrolyte-CPA and
pseudo-chemical SAFT papers are pending; entries marked "Abstract" or "Title
only" may be updated.

**Zotero.** No items were added. The Zotero workflow does not allow automated
publisher downloads, and adding an item requires the owner to save it through
the browser Connector. Papers to save, in priority order:

1. Neumann et al. 2021 — doi 10.1016/j.ces.2021.117261 (decides whether any
   Helmholtz model already gives MEA heat with EOS ions)
2. Najafloo, Zoghi & Feyzi 2015 — doi 10.1016/j.jct.2014.11.006
3. Téllez-Arredondo & Medeiros 2013 — doi 10.1016/j.fluid.2013.01.005
4. Lloret, Vega & Llovell 2017 — doi 10.1016/j.jcou.2017.08.018
5. Rozmus 2012 thesis, Université Paris 6, 2012PA066320 (library or
   interlibrary loan)
6. Raeispour Shirazi & Lotfollahi 2019 (doi 10.1016/j.fluid.2019.112289) and
   2020 (doi 10.1016/j.fluid.2020.112801)
7. Pereira, Llovell & Vega 2018 (doi 10.1016/j.apenergy.2018.04.021);
   Pereira & Vega 2018 (doi 10.1016/j.apenergy.2018.09.189)

**Still required before submission:** the Scopus and Web of Science query
and "cited by" lists in the owner's browser session, and full reads of
items 1–5.

### 9.7 What was read and what was not

Read in full for methods, fitting, results and limitations (local Markdown
copies or Zotero PDF text): Baygi 2015, Nasrifar 2010, Najafloo 2018,
Pakravesh 2025a, Mac Dowell 2010, Rodriguez 2012 (MEA section), Perdomo 2023,
Wang 2018; Uyan 2015, Wangler 2018, Cleeton 2020, Bülow 2021a, Schick 2023,
Pabsch 2020; Held 2008, Held 2014, Bülow 2020 and 2021 with corrigenda,
Figiel 2025 with its 2026 correction, Rueben 2024, Ascani 2021, 2022a and 2023;
Austgen 1991, Liu 1999, Gabrielsen 2005, Hilliard 2008 (Chapter 13, Appendix F,
§13.3.4), Zhang 2011, Aronu 2011 with corrigendum, Akula 2021 (main text and
supplement), Akula 2023a; Böttinger 2008 (Table 3 from the PDF, which the
Markdown copy lacks), Jakobsen 2005, Wong 2015, Wong 2016 (RSC Adv. and
J. Nat. Gas Sci. Eng.), Matin 2012, Idris 2014, du Preez 2019, Yamada 2012;
Kim and Svendsen 2007, Kim et al. 2014. Papers screened during the
pre-submission search are listed with their read status in §9.6.

Not read or read only in part:

- **Not in Zotero:** Austgen 1989, which holds the MEA-specific parameters.
- **Supplements not available locally:** Matin 2012 (Tables S1–S2), Bülow 2021a
  (Tables S1, S3), Pakravesh 2025a, and the Silva 2024 ion list.
- **Abstract only:** Smith, Rutherford and Leal 2026; Silva 2024; Novak 2023.
- **Only in figures, not digitized:** Wong 2015 Fig. 8, Wong 2016 Figs. 5–6,
  du Preez Fig. 5, Baygi Fig. 8.
- **Unclear from text extraction:** which Aronu 2011 parameters were refitted
  (Tables 7–9).
- **Not checked:** local copies were not hash-checked against `literature/index.csv`.
