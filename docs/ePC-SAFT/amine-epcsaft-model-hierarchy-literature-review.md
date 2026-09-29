# Aqueous amine ePC-SAFT literature and model lineage

This document preserves the literature rationale and historical model choices.
The [scientific plan](../scientific/PREDICTIVE_MEA_PROGRAM.md) owns the current
estimation strategy; the established-work map `docs/scientific/docs/scientific/CONTEXT.md` connects it to
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
[`docs/scientific/latex/manuscript_references.bib`](../scientific/latex/manuscript_references.bib);
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
`docs/scientific/docs/scientific/CONTEXT.md`. Consult those records before proposing
another strategy review or treating an old implementation limit as current.

## 9. Published-work gaps and what the retained evidence adds (23 September 2026; revised 24 September 2026, twice)

Question: where does published MEA–CO2–H2O and reactive-amine modeling stop,
and which retained results in this repository extend it? This section judges
novelty only. It does not promote a parameter set, and it does not change the
claim limits in the [working notebook](../../analyses/mea_parameter_bundle/notebook.qmd).

Manuscript direction (owner decision, 24 September 2026): a predictive paper
for Fluid Phase Equilibria built on the R4-fixed refit of candidate A
([MEA #107](https://github.com/tannerpolley/MEA-Thermodynamics/issues/107);
candidate A reaches pCO2 AARD 26.9 % on the 161 rows, draft
[PR #106](https://github.com/tannerpolley/MEA-Thermodynamics/pull/106)), with
composition-transfer validation on the 95 reserved pressure rows, 94 of them at other MEA concentrations
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
| Explicit-ion reactive ePC-SAFT for MEA | Explicit-ion ePC-SAFT exists for MDEA, a tertiary amine that forms no carbamate: Uyan 2015 (§3, Eqs. 12–15), Wangler 2018, Cleeton 2020, Bülow 2021a (Eqs. 1–5); the only amine ion is MDEAH+. MEA SAFT models use ideal chemistry plus a neutral EOS (Baygi 2015 §3.3; Najafloo 2018 §3.3; Nasrifar 2010 §6 lumps ions into "effective water") or association sites instead of ions (Mac Dowell 2010 §II.B; Rodriguez 2012; Perdomo 2023 Eqs. 4–14; Wang 2018 PR-CPA association scheme Fig. 1). Carbamate ions as EOS species with electrolyte terms exist outside SAFT-for-MEA: electrolyte SAFT-HR with MSA and Born terms for the AEEA carbamates in MDEA + AEEA (Najafloo, Zoghi & Feyzi 2015, Eqs. 19–21, A1, A21–A26, Table 8); a cubic + association EOS with a Debye–Hückel term for MEAH+, MEACOO- and HCO3- (Téllez-Arredondo & Medeiros 2013, Eqs. 10–14, Tables 5–6); a Helmholtz multiparameter EOS whose reaction part is an e-NRTL excess Gibbs energy with Pitzer–Debye–Hückel and Born terms for MEA (Neumann 2021, Eqs. 15–17, Table 3). Search record: §9.6. | No SAFT-family equation of state with MEA ions as species with electrolyte terms, in the searches of §9.6 (Scopus and Web of Science pending). | Nine-species, five-reaction pre-refit record; 161 pressure rows and 131 speciation targets, all evaluated (notebook §Pressure, §Speciation) | Calibration residual |
| Pressure, speciation and heat from one model | Activity-coefficient models fitted jointly to pCO2, NMR, heat of absorption and heat capacity: Hilliard 2008 (data inventory Table 13.4-2, p. 440; 35 parameters Table 13.4-3, p. 441), Zhang 2011 (Table 9); Akula 2023a fits pCO2 and heat of absorption only (Table 3, p. 8) and compares speciation and heat capacity (Figs. 7–8). **Cleeton 2020 already does all three with one explicit-ion ePC-SAFT, for MDEA:** pCO2 (Figs. 7–9), speciation including carbonate against Jakobsen 2005 (§3.3.2, Fig. 6), and differential heat from the EOS fugacity temperature derivative plus reaction terms (Eq. 15, Fig. 10; 19.73 % against Arcis and Mathonat). Wang 2018 does all three with pseudo-chemical PR-CPA for MEA (Fig. 16; Figs. 18–19). | The same three quantities from one explicit-ion EOS for a carbamate-forming amine. | Pressure and speciation tables in the notebook; single-state heat `analyses/mea_parameter_bundle/results/reference-calorics/heat.csv` | Calibration residual (pressure, speciation); prediction (heat, 2 states) |
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

1. **Explicit-ion reactive ePC-SAFT for MEA, validated across MEA
   concentration (contingent on #107 and #108).** Defensible wording: in the
   searches of §9.6 (Scopus and Web of Science still pending), no published
   SAFT-family equation of state places MEAH+, MEACOO-, HCO3- and CO3²- in
   the equation of state with electrolyte terms and solves the MEA reaction
   equilibria with fugacities from that equation of state. The claim needs
   all three qualifiers (SAFT-family, MEA, ions inside the equation of state
   with electrolyte terms), because each has been done without the others
   (§9.4). Nasrifar 2010, Baygi 2015 and Najafloo 2018 carry the MEA ions
   and reactions, but as ideal species outside the SAFT term. Najafloo,
   Zoghi and Feyzi 2015 put carbamate ions in a SAFT equation of state with
   MSA and Born terms, but for AEEA in MDEA + AEEA. Téllez-Arredondo and
   Medeiros 2013 put the MEA ions in a cubic + association equation of
   state with a Debye–Hückel term. Neumann 2021 puts them in a Helmholtz
   multiparameter model through an e-NRTL excess Gibbs term. Explicit-ion
   ePC-SAFT itself (Debye–Hückel, or MSA and Born) has been applied only to
   MDEA; Cleeton 2020 is the closest precedent. Evidence now: the pre-refit
   record evaluates every pressure and speciation row, and candidate A
   reaches 26.9 % on the 161 rows (PR #106). What establishes it: #107
   adoption with its promotion gates, then #108 on the 95 reserved rows, 94
   of them at other MEA concentrations. That would be the first physical
   validation here, limited to transfer across concentration. Stronger with:
   the per-source table of §9.3 recomputed on the adopted record, and the
   Rozmus 2012 thesis chapters (§9.6).
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

All values are mean |p_model/p_obs − 1| in % on CO2 partial pressure; the
pre-refit record, Baygi, Najafloo, Zhang and Akula evaluate it at the measured
temperature and loading, and Hilliard's residual definition is unresolved (*). "Pred." means no ternary data were fitted;
"cal." means the dataset was fitted. The pre-refit record column is superseded
once MEA #107 adopts a record; candidate A (26.9 % over the same 161 rows,
PR #106) has no per-source row here because its record is not adopted.

| Dataset | Pre-refit record (n) | Baygi 2015 PC-SAFT, pred.‡ | Najafloo 2018 SAFT-HR, pred.‡ | Zhang 2011 eNRTL, cal. | Hilliard 2008 eNRTL, cal.* | Aronu 2011 e-UNIQUAC, cal. | Akula 2023a eNRTL, cal. |
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
Baygi's overall 36.42 % covers 691 rows at x_MEA 0.02–0.16 and 273–443 K
(Table 5), mostly other concentrations. It is not a like-for-like comparison
with the 161-row value.

\* Hilliard's parameters are fitted by maximum likelihood with errors in all
variables (Chapter VI, Appendix L; data in Table 13.4-2). The Table 13.4-6
errors come from a separate Aspen Plus flash test of the fitted model
(§13.4.1, p. 447) whose specification is not stated. That table reports a
nonzero loading AARD for every row (Mamun 1.60 %), including the heat and
heat-capacity rows, so loading was not held at its measured value; p. 499
attributes the 12.91 % heat figure to the parameter-fitting tool adjusting the
measured variables. The text and table therefore disagree, and the residual
definition is unresolved. Zhang 2011 uses the Aspen fitting tool without
stating its error model.
‡ Baygi's "prediction" is weaker than the label suggests: it chose the Tong
2012 and Bates–Pinching constants for R4/R5 because they gave the best
ideal-chemistry agreement (text before Table 5). Najafloo 2018 reuses the
Tong 2012 constant for K3 (Table 3), so the caveat applies to it too.
§ The Baygi and Najafloo Hilliard rows span x_MEA 0.06–0.16 (3.5–11 m). The
pre-refit record uses the 7 m (30 mass %) rows only.

Excluded because the residual direction differs: Mac Dowell 2010 (absolute
deviation in x_CO2 at measured T and P, AAD 0.010), Schick 2023 and Pabsch 2020
(x_CO2 at given pressure), and Wang 2018 (total pressure, 12 %, Table 4).

MDEA values, for comparison only: Uyan 2015 34.4 % (corrected by Wangler 2018
Table 11, footnote b, from the published 22.9 %), Wangler 2018 19.7 %, Cleeton
2020 20–70 % by dataset, Bülow 2021a 32.7 % at 30 mass %.

#### Published MEA–CO2–H2O models and their 30 mass % pressure deviations

For the manuscript comparison. This repository scores pCO2 AARD at the
measured temperature and loading, per source, on Jou 1995, Hilliard 2008,
Aronu 2011, Mamun 2005, Xu 2011 and Idris 2014, 30 mass % MEA only, 40–120 °C
(table above). A published value is **like-for-like** only if it is a relative
pCO2 deviation at the measured loading, restricted to 30 mass %, on the same
source over the same temperatures. "Partly" names the difference. Values are
as printed; "not reported" means the paper gives no number for that quantity.

| Model (paper) | Datasets, points | Deviation reported | Conditions | Fitted or predicted | Value, % | Locator | Like-for-like with ours |
|---|---|---|---|---|---|---|---|
| Baygi 2015, PC-SAFT, ideal ions | Jou 1995 (100), Hilliard 2008 (42), Mamun 2005 (19), Xu 2011 (52); 14 other sources | Mean \|Δp/p\| on pCO2; speciation solved at the measured composition (§3.3) | Jou 273–423 K, loading 0.002–1.324; Hilliard x_MEA 0.06–0.16, 313–333 K; Mamun 393 K, 0.155–0.418; Xu 373–443 K, 0.303–0.52 | Predicted: no ternary data fitted, but K(R4, R5) chosen for fit (‡ above) | Jou 43.16; Hilliard 34.97; Mamun 21.03; Xu 46.88; all 691 rows 36.42 | Table 5, footnote b | Mamun: yes (same source, all at 120 °C and 30 mass %, n = 19 in both). Jou, Xu: partly (wider temperature range). Hilliard: partly (other concentrations) |
| Najafloo 2018, SAFT-HR, ideal ions | Same rows as Baygi | Mean \|Δp/p\| on pCO2 (§3.3, text before Table 5) | As Baygi (Table 4) | Predicted, with the ‡ caveat: MEA–H2O and CO2–MEA kij zero, CO2–H2O kij from Najafloo et al. 2016 (§3.2); K from literature, K3 from Tong 2012 as in Baygi (Table 3); MEA parameters from pure-component data (§3.1) | Jou 49.52; Hilliard 42.59; Mamun 39.96; Xu 15.44; all 691 rows 34.71 | Table 5 | As Baygi |
| Zhang 2011, e-NRTL | Hilliard 2008 (55), Jou 1995 (124), Mamun 2005 (19), Xu 2011 (63) | Mean \|ΔY/Y\| on CO2 partial pressure for all four sources (§3.3, p. 72) | Hilliard 313–333 K, x_MEA 0.06–0.16, 0.11–0.59; Jou 273–423 K, 0.002–1.33; Mamun 393 K, 0.16–0.42; Xu 373–443 K, 0.30–0.52 | Fitted with the Aspen fitting tool, jointly with heat, heat capacity and NMR speciation | Hilliard 35.5; Jou 33.5; Mamun 13.5; Xu 28.0 | Table 9 | Mamun: yes, as a calibration residual. Others: partly (wider ranges) |
| Hilliard 2008, e-NRTL | Jou 1995 (70), own data (55), Mamun 2005 (19), Lee 1976 (93), Lawson and Garst 1976 (16), Goldman and Leibush 1959 (38) | pCO2 AARD from an Aspen Plus flash test of the fitted model, specification not stated; loading AARD reported separately (§13.4.1) | Jou 25–120 °C; own data 40–120 °C as listed in Table 13.4-2; Mamun 120 °C | Fitted (with heat of absorption, heat capacity, NMR) | Jou 13.55; own data 30.01; Mamun 27.06; Lee 21.67; Lawson and Garst 67.99; Goldman and Leibush 13.93 | Tables 13.4-2 (p. 440), 13.4-6 (p. 447); §13.4.1 | Partly: residual definition unresolved; the nonzero loading errors show loading was not fixed at the measured value (* above) |
| Aronu 2011, extended UNIQUAC | Own data, 15, 30, 45 and 60 mass % | pCO2 AARD (Eq. 21) pooled over all concentrations; total pressure separately | pCO2 40–80 °C; total pressure 60–120 °C; loading range not extracted | Fitted to own data | pCO2 24.3; total pressure 11.7; all own data 16.2. 30 mass % alone not reported | Abstract; Eq. 21; §4.2 (p. 6400) | Partly: pooled across concentrations |
| Akula 2023a, e-NRTL | Aronu 2011 (138), Hilliard 2008 (55), Jou 1995 (38), Xu 2011 (25), Kim 2014 (7) | Mean absolute percentage error on pCO2 (Eq. 36); objective in ln pCO2 at measured T and loading (Eq. 34) | 30 mass % subset, loading 0.003–0.5, 40–120 °C | Fitted (with heat of absorption) | 40.5, pooled over the 30 mass % subset; per source not reported | Table 3; Eqs. 34, 36; Fig. 4 | Partly: same residual and concentration, pooled across sources, loading ≤ 0.5 |
| Akula 2021, rate-based process model | Thermodynamics taken from Morgan et al. (Table 1) | Not reported | — | — | Not reported | Table 1 | No |
| Téllez-Arredondo 2013, eCTS (cubic + association + Debye–Hückel, EOS ions) | Lawson and Garst 1976, Mamun 2005, Jou 1995; 107 points | %AAD in the partial pressure of the acid gas (§4.3.3, p. 54); the fitting objective also includes total pressure (Eq. 28) | 298–393 K (Table 2; §4.3.3 gives 298–366.68 K), 15.2–30 mass %; loading range not stated | Fitted (MEACOO- d1 and cross-parameters; Table 5) | 12.5, pooled | Tables 2, 8; §4.3.3 | Partly: pooled over 15.2–30 mass % and three sources |
| Wang 2018, PR-CPA, association instead of ions | Jou 1995, 30 mass % | Relative deviation of total pressure (Eq. 8) | 298–393 K; loading range not stated | Fitted (kij(T), cross-association; Table 4) | 12 | Table 4, Fig. 5 | No: total pressure |
| Neumann 2021, Helmholtz model + e-NRTL | Aronu 2011, Jou 1995, Lee 1976, Shen and Li 1992 at 30 mass % (plotted) | Not reported for pressure (density AARD only) | 30 mass % in Fig. 5 (caption); the selected datasets span 298–393 K and 15–60 mass % (§4.2) | K3–K5 fitted to VLE (§3, Table 6); e-NRTL parameters from Putta 2016 unchanged; low-loading Jou rows below the MEA vapor pressure not fitted (§4.2) | Not reported | Fig. 5 | No |
| Lloret 2017, soft-SAFT, association instead of ions | Jou 1995 at 30 mass % (Fig. 10a); Lee 1976 at 2.5 N (Fig. 11) | Not reported | 313–373 K (Fig. 10a); 298–373 K (Fig. 11) | CO2 reactive-site energy and volume fitted to the Jou data; 2.5 N predicted | Not reported | §4.7; Figs. 10a, 11 | No |

The same limitation applies to Chremos 2016 (Fig. 11) and Noroozi 2020
(Fig. 5): pressure comparisons for 30 mass % MEA in figures only, with no
numerical deviation. The like-for-like published comparisons are the three
Mamun 2005 values (Baygi 21.03, Najafloo 39.96, Zhang 13.5, n = 19).
Hilliard's Mamun 27.06 (n = 19, fitted) is not like-for-like, because its
loading was not held at the measured value (* above).
Akula 2023a is the closest pooled comparison: same residual and
concentration, fitted, and loading limited to 0.5. The pre-refit record's
Mamun value is 20.6 % (n = 19).

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
- **Non-SAFT equations of state with ions for MEA (both read in full).**
  Neumann, Poplsteinova Jakobsen, Thol and Span (Chem. Eng. Sci. 252,
  117261; online 2021) add an "effect of reaction" term to a Helmholtz
  multiparameter mixture model (Eqs. 2, 8, 15). That term is the Putta 2016
  e-NRTL excess Gibbs energy, used with unchanged parameters, including its
  Pitzer–Debye–Hückel and Born terms (Eqs. 16–17, §4.2). MEAH+, MEACOO-,
  HCO3-, CO3²-, H3O+ and OH- are species of the combined model (Table 3).
  Their pure-fluid residual Helmholtz energy is set to zero and their
  ideal-gas part comes from the Joback method (§2). K3–K5 are fitted to VLE
  data (Table 6, §3). The ternary pressure comparison is figures only
  (Fig. 5), the speciation comparison with Jakobsen 2005 is a figure
  without a metric (Fig. 7), and no heat of absorption is reported.
  Téllez-Arredondo and Medeiros 2013 (FPE 344:45) use SRK + two-state
  association + a Debye–Hückel primitive-model term (Eqs. 1, 10–14). MEAH+,
  MEACOO- and HCO3- are EOS species with fitted parameters (Tables 5–6).
  CO3²- is omitted because the second acid dissociation is neglected (§3).
  The MEA–CO2 ionic parameters are fitted to ternary VLE, with pressure
  %AAD 12.5 (§4.3.3, Table 8). Téllez reports neither speciation nor heat.
  Neumann reports MEA speciation only in a figure (Fig. 7, Jakobsen 2005,
  313.15 K, 30 mass %, no metric) and no heat.
  The claim must say "SAFT-family", not "equation of state" or
  "Helmholtz-energy model".
- **Electrolyte SAFT with carbamate ions, for AEEA (read in full).**
  Najafloo, Zoghi and Feyzi 2015 (J. Chem. Thermodyn. 82:143) use
  electrolyte SAFT-HR, SAFT-HR plus MSA and Born terms (Appendix A,
  Eqs. A1, A21–A26), for CO2 in MDEA + AEEA. Ion fugacity coefficients
  from the equation of state enter the equilibrium constants (Eqs. 19–21).
  The two AEEA carbamate ions have SAFT parameters fitted to the authors'
  own total pressures (Eq. 29, Table 8); the other ions copy the parameters
  of their parent molecules, and every kij is zero (§4.2). Total-pressure
  AAD is 7.74 % (Tables 10–13). A SAFT equation of state with carbamate
  ions and electrolyte terms therefore exists, and claim 1's heading is
  narrowed from "a carbamate-forming amine" to MEA.
- **IFP electrolyte PPC-SAFT line.** The Rozmus 2012 thesis plans GC-PPC-SAFT
  with ions and reactions for primary and secondary amines. Its abstract
  (theses.fr snapshot, Zotero 3GBTNFUA) reports strong electrolytes with MSA
  and Born terms and CO2-free amine solutions only. Rozmus et al. 2013 (IECR,
  read in full) covers alkali halides and calls amine–CO2 "the final aim".
  The thesis chapters are unread; Zotero holds the record without full text.
- **Pressure, speciation and heat from one model is not new.** It is done
  with activity-coefficient models (Hilliard 2008, Zhang 2011, Akula 2023a),
  with pseudo-chemical SAFT (Perdomo 2023, heat for MAPA, Fig. 7; Rodriguez
  2012, MEA speciation), with PR-CPA for MEA (Wang 2018), and with PR-CPA plus
  Deshmukh–Mather for MEA (Wang 2017 thesis, Figs. 5-17, 5-20, 5-21).
- **Heat and derivatives.** EOS heats of absorption for MEA exist without
  ions: Wang 2018, and Lloret 2017, whose soft-SAFT heat comes from the
  Clausius–Clapeyron slope of pCO2 (Eq. 26, Fig. 10b, against Kim 2014,
  no metric). Exact derivatives are standard in Helmholtz-energy software
  (EOS-CG-2021, Sect. 2.2). Neither is a headline claim.
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

- **Matin 2012 bicarbonate targets (data mapping set by MEA #109; the calibration packet still scores bicarbonate alone).** The 19 Matin HCO3-
  targets (loading 0.106–0.531) were scored against model HCO3- alone
  (`data/reference/MEA/manifests/speciation_target_membership.csv`, empty
  `linear_coefficients`). That file now gives HCO3- + CO3²- for every Matin
  and Böttinger 2008 HCO3- row. Matin sets carbonate to zero at every loading and
  counts it with bicarbonate (Eqs. 18–19b). Its text justifies this for most
  loadings and "particularly" above 0.25, and separately below 0.3, where both
  ions are small (Discussion). The equivalent model quantity
  is HCO3- + CO3²-.
- **Hilliard residual direction.** Notebook §Fit statistics groups Hilliard
  2008 with the papers that report pressure at the measured loading. Its
  Table 13.4-6 values come from an Aspen Plus flash test whose
  specification is not stated (§13.4.1), and its nonzero loading errors show
  loading was not held at the measured value, so that grouping is not
  supported (see §9.3).
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
| Neumann et al. 2021, Chem. Eng. Sci. 252 (doi 10.1016/j.ces.2021.117261) | Full text (Zotero PDF) | Helmholtz multiparameter model + e-NRTL reaction term (Pitzer–Debye–Hückel and Born); MEA ions are model species (Table 3, Eqs. 15–17); pressure and speciation in figures only (Figs. 5, 7); no heat. Not SAFT-family; narrows claim 1 to SAFT-family |
| Téllez-Arredondo & Medeiros 2013, FPE (doi 10.1016/j.fluid.2013.01.005) | Full text (Zotero PDF) | SRK + two-state association + Debye–Hückel; MEAH+, MEACOO-, HCO3- are EOS species, CO3²- omitted (§3, Tables 5–6); MEA–CO2 fitted, %AAD p 12.5 (Table 8). Cubic, outside SAFT wording |
| Najafloo, Zoghi & Feyzi 2015, J. Chem. Thermodyn. (doi 10.1016/j.jct.2014.11.006) | Full text (Zotero PDF) | Electrolyte SAFT-HR (MSA + Born) with AEEA carbamate ions as EOS species, MDEA + AEEA (Eqs. 19–21, Appendix A, Table 8). Narrows claim 1 from "carbamate-forming amine" to MEA |
| Rozmus 2012 thesis (2012PA066320) | Abstract only (Zotero record 3GBTNFUA, theses.fr snapshot; no full text) | GC-PPC-SAFT; MSA and Born for strong electrolytes; aqueous primary amines without CO2 in the reported work. Chapters unread |
| Rozmus et al. 2013, IECR (doi 10.1021/ie303527j) | Full text (Zotero) | Alkali halides only; no effect |
| Rozmus et al. 2011, FPE (doi 10.1016/j.fluid.2010.12.009) | Metadata only | Amine + alkane/alcohol, no CO2; no effect expected |
| Chremos et al. 2016, FPE (doi 10.1016/j.fluid.2015.07.052) | Full text (Zotero PDF, §3.6) | SAFT-γ SW group contribution; reactions by association; ions only as neutral tight ion pairs (§3.6). MEA–CO2 parameters fitted to one Jou 1995 isotherm (353 K, 30 mass %, loading ≤ 0.7); 313 and 393 K predicted (Fig. 11); carbamate and bicarbonate from bonding fractions (Fig. 12). No numerical pCO2 deviation. No effect |
| Brand et al. 2016, Faraday Discuss. (doi 10.1039/c6fd00041j) | Full text (Zotero PDF, model and results sections) | SAFT-VR SW inside a rate-based MEA absorber; reactions by physical association, products not treated explicitly (abstract, §2.1); thermodynamic parameters from Mac Dowell et al. (§2.1). No ions; no effect |
| Pereira, Llovell & Vega 2018, Appl. Energy (doi 10.1016/j.apenergy.2018.04.021) | Full text (Zotero PDF) | soft-SAFT + free-volume + density-gradient theory for aqueous MEA, DEA, MDEA, AMP and piperazine without CO2 (abstract, §3); MEA parameters from Lloret 2017. No CO2, reactions or ions; no effect |
| Pereira & Vega 2018, Appl. Energy (doi 10.1016/j.apenergy.2018.09.189) | Abstract | soft-SAFT with implicit reactions; no ions |
| Lloret, Vega & Llovell 2017, J. CO2 Util. (doi 10.1016/j.jcou.2017.08.018) | Full text (Zotero PDF) | soft-SAFT, no ions: CO2 has two reactive association sites fitted to Jou 1995 at 30 mass % (§4.7, Fig. 10a); heat from the Clausius–Clapeyron slope of pCO2 (Eq. 26, Fig. 10b); 2.5 N predicted (Fig. 11). No numerical pCO2 deviation. No effect on claim 1 |
| Raeispour Shirazi & Lotfollahi 2019 and 2020, FPE (doi 10.1016/j.fluid.2019.112289; 10.1016/j.fluid.2020.112801) | Full text (Zotero PDFs; methods and results) | ePC_SAFT-MB (PC-SAFT + MSA + Born) with MDEAH+ and HS- or HCO3- as EOS species. 2019: H2S in MDEA, total-pressure AAD 18.6 % on 277 points after fitting ion BIPs; 2020: CO2 in MDEA, 15.3 % on 162 points (abstracts). MDEA only; no effect on the MEA claim |
| Mehdizade et al. 2024, J. Mol. Liq. (doi 10.1016/j.molliq.2024.124441) | Title only | Electrolyte SRK-CPA, H2S in MDEA/MEA/DEA; no CO2 per title |
| Plakia, Pappa & Voutsas 2018, FPE (doi 10.1016/j.fluid.2018.09.013) | Abstract | UMR-PRU cubic EoS/GE with extended UNIQUAC ions, MEA + CO2; outside SAFT wording |
| Wang 2017 thesis (tel-01865166) | Full text (open) | PR-CPA + Deshmukh–Mather for MEA speciation and heat; no EOS ions |
| Noroozi & Smith 2020, IECR (doi 10.1021/acs.iecr.0c03738) | Full text (Zotero PDF) | Equilibrium constants from quantum chemistry and molecular-dynamics solvation free energies, ideal (Henry's-law) solution, no EOS (abstract, §2). MEA speciation (Fig. 3) and 30 mass % pCO2 (Fig. 5) in figures only. No effect |

Entries marked "Abstract", "Title only" or "Metadata only" were screened
without the full text. The full-text reads of 24 September 2026 used Zotero
PDFs saved by the owner (collection MEA-Absorption-Paper), read as text
extractions; none has a Markdown companion.

**Zotero.** The owner saved Neumann 2021, Najafloo 2015, Téllez-Arredondo
2013, Lloret 2017, Raeispour Shirazi 2019 and 2020, Pereira, Llovell and Vega
2018, Chremos 2016, Brand 2016 and Noroozi 2020 with PDFs, and the Rozmus
2012 thesis as a record without full text. No agent wrote to Zotero.

**Still required before submission:** the Scopus and Web of Science query
and "cited by" lists in the owner's browser session; the Rozmus 2012 thesis
chapters (Université Paris 6, 2012PA066320; library or interlibrary loan);
and Pereira & Vega 2018 (doi 10.1016/j.apenergy.2018.09.189), still at
abstract level.

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
Kim and Svendsen 2007, Kim et al. 2014; Neumann 2021, Téllez-Arredondo 2013,
Najafloo 2015 and Lloret 2017 (24 September 2026, Zotero PDFs). Methods and
results only: Raeispour Shirazi 2019 and 2020, Pereira 2018, Chremos 2016,
Brand 2016, Noroozi 2020. Papers screened during the pre-submission search
are listed with their read status in §9.6.

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
