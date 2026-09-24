# Aqueous amine ePC-SAFT literature and model lineage

This document preserves the literature rationale and historical model choices.
The [scientific plan](../scientific/PREDICTIVE_MEA_PROGRAM.md) owns the current
estimation strategy; the [context map](../scientific/CONTEXT.md) connects it to
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
[CONTEXT.md](../scientific/CONTEXT.md). Consult those records before proposing
another strategy review or treating an old implementation limit as current.

## 9. Published-work gaps and what the retained evidence adds (23 September 2026)

Question: where does published MEA–CO2–H2O and reactive-amine modeling stop,
and which retained results in this repository extend it? This section judges
novelty only. It does not promote a parameter set, and it does not change the
claim limits in the [working notebook](../../analyses/mea_parameter_bundle/notebook.qmd).
Evidence strength uses three labels: **numerical verification** (the
calculation represents its equations), **prediction** (model output compared
with observations that did not set the compared quantity), and **calibration
residual** (comparison with rows used to fit or select the record). No
retained result below is **physical validation**: every compared row was used
in fitting or selection, including Xu 2011 and the Kim–Svendsen 120 °C heat
([holdout ledger](../../analyses/mea_parameter_bundle/results/holdout-evaluations.csv)).

Search scope: the local reading shelf and live Zotero library (queries on
ePC-SAFT/SAFT/CPA with MEA, alkanolamine, carbamate, heat of absorption,
2022–2026), plus a bounded web search on 23 September 2026. It is not a
Scopus or Web of Science search. "Not found" below means not found in that scope.

### 9.1 Gap map

| Topic | What published work does (locator) | What is missing | Retained evidence here (path) | Strength |
|---|---|---|---|---|
| Explicit-ion reactive ePC-SAFT for MEA | Explicit-ion ePC-SAFT exists for MDEA only: Uyan 2015 (species §2, Eqs. 12–15), Wangler 2018, Cleeton 2020, Bülow 2021a (Eqs. 1–5); the only amine ion is MDEAH+. MEA SAFT models use ideal chemistry plus a neutral EOS (Baygi 2015 §3.3; Najafloo 2018 §3.3; Nasrifar 2010 §6 lumps ions into "effective water") or association sites instead of ions (Mac Dowell 2010 §II.B; Rodriguez 2012; Perdomo 2023 Eqs. 4–14; Wang 2018 PR-CPA Fig. 2). | No explicit-ion EOS treatment of the carbamate-forming MEAH+/MEACOO- pair in the searched scope. | Nine-species, five-reaction record `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`; 161 pressure rows and 131 speciation targets, all evaluated (notebook §Pressure, §Speciation) | Calibration residual |
| Pressure, speciation and heat from one EOS | One activity-coefficient model fitted jointly to pCO2, NMR, heat of absorption and heat capacity: Hilliard 2008 (Table 13.4-2, p. 440; 35 parameters); Zhang 2011 (Table 9); Akula 2023a (Eq. 34, Table 3). EOS papers compute at most two of the three: Wang 2018 (pressure, speciation Fig. 16, heat Figs. 18–19); Wangler 2018 (pressure, heat Eqs. 22–31, MDEA). | No SAFT-family MEA work computes pressure, measured-species speciation including carbonate and differential heat from one Helmholtz energy. | Pressure and speciation tables in the notebook; single-state heat `analyses/mea_parameter_bundle/results/reference-calorics/heat.csv` | Calibration residual (pressure, speciation); prediction (heat, 2 states) |
| Exact derivatives and sensitivities | Finite differences: Hilliard 2008 heat between T and T+1 K (Eq. 13-36, p. 429); Uyan 2015 solver iterates activities without derivatives (§3). Automatic differentiation of fugacities in reactive non-electrolyte PC-SAFT: Ascani 2023 (Eqs. 16–17). No amine paper reports solved-state sensitivities. | Solved-state derivatives of a reactive electrolyte EOS equilibrium, checked against finite differences. | Temperature and pressure solved-state derivatives, relative error ≤ 1.21×10⁻⁷; kij refused and reaction-coefficient derivatives unavailable on the pinned wheel (`results/runs/engine-comparison/README.md`, Derivatives); 46/46 reference-temperature actions within 10⁻⁵ of finite differences (`results/reference-temperature/summary.json`) | Numerical verification |
| Modified Born (solvation shell + dielectric saturation) for amine ions | Figiel 2025 (Eqs. 5–11, Table 3): inorganic ions in water, methanol and ethanol, 298.15 K only; the authors state the diameter was not tested at other temperatures. Bülow 2021a uses the original Born term with MDEAH+ (Eq. 20) and proposes an ion-dependent Born/permittivity extension for high loading (Conclusions). Rueben 2024: permittivity for inorganic ions only. | No application to amine or carbamate ions or to a reactive CO2–amine system in the searched scope. Temperature transfer of the solvation-shell parameters is untested anywhere. | Record uses SSM+DS with MEAH+/MEACOO- Born diameters from a historical speciation fit (notebook species table); historical Born/permittivity comparison `results/born-permittivity-study/` | Calibration residual; no independent electrostatic evidence |
| Reference-state and K(T) conventions | Conventions conflict: Austgen 1991 mole-fraction, unsymmetric (pp. 545–546, Table V); Cleeton 2020 symmetric for water and MDEA (Eq. 8); Bülow 2021a infinite dilution in water for MDEA and says this is "often misused" (Eqs. 12–13); Böttinger 2008 molality (§4). Cleeton applies an MDEAH+ constant valid at 298–333 K up to 413 K (Table 1). | An explicit conversion of mixed-source constants to one basis with a verified temperature derivative. | Common aqueous-molality conversion (`docs/ePC-SAFT/mea-reaction-and-sentinel-primary-source-audit.md`); reaction-by-reaction slope attribution `results/reference-temperature/attribution.csv`, `slopes.csv` | Numerical verification |
| Speciation validation including carbonate | No source tabulates reliable directly measured MEA carbonate above loading 0.5: Böttinger 2008 "practically not present"; Jakobsen 2005 infers it from a shared peak and calls it unreliable above 0.6; Matin 2012 sets it to zero (Eqs. 18–19b); Wong 2015/2016 resolve it by Raman in figures only. MEA SAFT speciation comparisons are figures without metrics (Nasrifar Fig. 11; Baygi Fig. 8; Rodriguez Fig. 9b; Perdomo Fig. 14). Uyan 2015 compares carbonate for MDEA (Figs. 3–4). | A quantitative SAFT-family comparison with measured MEA species, and any measured carbonate target. | 131 targets with metrics by species (notebook §Speciation: MEA RMS ln 0.131, MEAH+ 0.262, MEACOO- 0.207, HCO3- 1.185). Carbonate is calculated but not scored. | Calibration residual |
| Heat of absorption from the EOS (Gibbs–Helmholtz) | Wangler 2018: van 't Hoff reaction terms plus a Henry's-constant correlation for physical dissolution, not the EOS (Eqs. 22–31), MDEA, graphical. Cleeton 2020 (Eq. 15): 19.7 % against Arcis/Mathonat (MDEA). Wang 2018 PR-CPA for MEA: underpredicts by 49 % once carbamate forms (Figs. 18–19). Hilliard 2008 12.9 %, Zhang 2011 10.9 %, Akula 2023a 5.9 % against Kim–Svendsen, all fitted to those data. | An MEA heat from an explicit-ion EOS whose Gibbs–Helmholtz identity is checked, compared with calorimetry not used for that state. | 82.06 kJ mol⁻¹ at 313.15 K, loading 0.35; 79.70 at 315 K, 0.415. Gibbs–Helmholtz identity to 2.5×10⁻¹³ and RT²·d ln pCO2/dT closure to 2.5×10⁻¹³ (`results/reference-calorics/heat.csv`, `closure.csv`). Against Kim–Svendsen 2007 at 40 °C: 1.7 and 4.0 kJ mol⁻¹ low (`calorimetry.csv`). | Numerical verification (identity); prediction on calibration-labelled calorimetry (2 states) |
| Identifiability and uncertainty reporting | Activity-coefficient papers report standard errors and show non-identified parameters: Austgen 1991 correlated τ pairs (p. 549); Hilliard 2008, 18 of 35 estimates smaller than their standard errors (p. 441); Zhang 2011 ΔfH standard deviations about 10² times the values (Table 10); Akula 2023a correlations to 0.97 (Table 7). No SAFT MEA paper reports parameter uncertainty; Mac Dowell 2010 describes near-optimal valleys qualitatively (Fig. 2). Smith, Rutherford and Leal 2026 argue that fitting equilibrium constants and activity parameters to the same solubility data is ill-posed (abstract only read). | A quantitative test, for an MEA EOS, of which pressure residual shapes reaction constants can and cannot absorb. | Loading-bin means remove 79 % of the residual sum of squares; ±0.3 ln K on R2/R4/R5 removes about 11 %; singular values 12.6, 4.5, 0.36; R2–R5 sensitivity correlation −0.91 (`results/runs/pco2-calibration-misfit/README.md`). Screening-prior global sensitivity over 113 parameter groups (`analyses/enrtl_six_species_ideal_comparison/notebook.qmd`, §All-parameter sensitivity) | Prediction on calibration rows (diagnosis); no confidence intervals |
| Reproducibility | No paper read releases code; several use gPROMS or Aspen. | Re-executable calculations with fixed inputs. | Engine wheel, parameter record and state packet identified by SHA-256; two Engines agree to median \|Δ ln pCO2\| 0.0011 (`results/runs/engine-comparison/README.md`) | Numerical verification |

### 9.2 Ranked publishable contribution claims

Each claim is bounded by the calibration status above. Claims 1 and 2 form
one paper; claims 3–5 support it or stand as short communications.

1. **The first explicit-ion reactive ePC-SAFT test for a carbamate-forming
   amine in the searched scope is a negative result for pressure.**
   The nine-species record reproduces MEA and carbamate speciation to RMS ln
   0.13–0.21 but pCO2 only to AARD 52.5 % (log₁₀ RMSE 0.2318, 161 rows). The
   ideal-activity chemistry of Baygi 2015 reaches 36.4 % over 691 rows
   without fitting to ternary data (Table 5). The manuscript's controlled
   comparison of the retired set also found the activity model worse than an
   ideal-activity baseline on 31 Jou 1995 rows (median |log₁₀| 0.495 against
   0.160; `docs/latex/main.tex` abstract). Evidence: notebook §Pressure and
   §Speciation; `results/current-best-fit-ln-statistics.csv`. Stronger with:
   the same ideal-activity baseline replayed on the current record and all
   161 rows, and one untouched pressure block.
2. **The pressure misfit has a loading shape that reaction constants cannot
   supply, placing it in the ionic non-ideality.** Under-prediction below
   loading 0.2, about 2× over-prediction at 0.3–0.5, under-prediction above
   0.55, at every temperature with coverage. Evidence and limits:
   `results/runs/pco2-calibration-misfit/README.md`. Published context:
   Bülow 2021a attributes the MDEA high-loading error to overpredicted
   ion–solvent interactions; Smith et al. 2026 argue the ill-posedness in
   general. This result adds a quantitative MEA instance. Stronger with: the
   README's next step (the same falsifier over CO2–water kij, MEAH+/MEACOO-
   size and dispersion, and the ion-pair kij) and a computed
   activity-coefficient decomposition, which does not exist yet.
3. **Heat of absorption from the same explicit-ion EOS with exact temperature
   derivatives.** The Gibbs–Helmholtz identity and the RT²·d ln pCO2/dT
   closure hold to 2.5×10⁻¹³. The value lies 1.7 kJ mol⁻¹ (0.9 measurement
   standard uncertainties) below Kim–Svendsen at loading 0.35 and 4.0 kJ mol⁻¹
   below at 0.415, with no heat observation in that calculation. Published
   EOS heats either take the physical term from a correlation (Wangler 2018)
   or fail once carbamate forms (Wang 2018). Stronger with: the full
   heat-versus-loading curve rebuilt on the pinned Engine (MEA #96), Kim 2014
   as a comparison, and the finite-increment versus derivative difference
   quantified. The superseded 120 °C heat bias (−18.8 kJ mol⁻¹) must be
   reported with it.
4. **The bicarbonate misfit is partly a target-definition and source-conflict
   result.** Matin 2012 and Jakobsen 2005 differ by 10–20× in bicarbonate
   below loading 0.3 at 20 °C (notebook §Speciation), and carbamate differs by
   up to 2.3× between Böttinger 2008 and Jakobsen 2005 above loading 0.5
   (Böttinger Table 3, Jakobsen Table A2). See the target-definition defect
   in §9.5. Stronger with: Matin targets rescored against HCO3- + CO3²-, and
   digitized Wong 2016 Raman carbonate (Figs. 5–6) as the one direct carbonate
   measurement.
5. **A verified reference-temperature chain for mixed-basis reaction
   constants.** 46/46 actions pass, with reaction-by-reaction attribution of
   d ln pCO2/dT. This is methods material supporting claim 3. It is not a
   standalone scientific claim.

### 9.3 pCO2 AARD at the measured loading, by dataset

All values are mean |p_model/p_obs − 1| in % on CO2 partial pressure at the
measured temperature and loading, 30 mass % MEA unless noted. "Pred." means
no ternary data were fitted; "cal." means the dataset was fitted.

| Dataset | This record (n) | Baygi 2015 PC-SAFT, pred. | Najafloo 2018 SAFT-HR | Zhang 2011 eNRTL, cal. | Hilliard 2008 eNRTL, cal.* | Aronu 2011 e-UNIQUAC, cal. | Akula 2023a eNRTL, cal. |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jou 1995 | 56.9 (48) | 43.2 | 49.5 | 33.5 (124) | 13.6 (70) | — | 40.5 over all 30 mass % data |
| Hilliard 2008 | 69.0 (30) | 35.0 | 42.6 | 35.5 (55) | 30.0 (55) | — | (same) |
| Mamun 2005 | 20.6 (19) | 21.0 | 40.0† | 13.5 (19) | 27.1 (19) | — | — |
| Xu 2011 | 48.7 (18) | 46.9 | 15.4 | 28.0 (63) | — | — | (same) |
| Aronu 2011 | 41.4 (36) | — | — | — | — | 24.3, own data, 15–60 mass % | (same) |
| Idris 2014 | 89.1 (10) | — | — | — | — | — | — |

Sources: this record from `analyses/mea_parameter_bundle/results/current-best-fit-ln-statistics.csv`;
Baygi Table 5; Najafloo Table 5; Zhang Table 9; Hilliard Table 13.4-6
(p. 447); Aronu abstract and Eq. 21; Akula 2023a Fig. 4. Published row counts
and domains differ from these rows.

\* Hilliard's regression reconciles pCO2 and loading together (maximum
likelihood with errors in all variables, p. 440), so its pCO2 AARD is not
strictly the same residual direction. Zhang 2011 uses the Aspen regression
tool without stating its error model.
† Not re-verified in this reading.

Excluded because the residual direction differs: Mac Dowell 2010 (absolute
deviation in x_CO2 at measured T and P, AAD 0.010), Schick 2023 and Pabsch 2020
(x_CO2 at given pressure), and Wang 2018 (total pressure, 12 %, Table 4).

MDEA context only: Uyan 2015 34.4 % (corrected by Wangler 2018 Table 11,
footnote b, from the published 22.9 %), Wangler 2018 19.7 %, Cleeton 2020
20–70 % by dataset, Bülow 2021a 32.7 % at 30 mass %.

### 9.4 Threats to novelty

- **Coupled pressure, speciation and heat is not new** in activity-coefficient
  models: Hilliard 2008 (Table 13.4-2), Zhang 2011 and Akula 2023a fit all
  three. The novelty is doing it with one explicit-ion EOS, not the coupling.
- **SAFT-family MEA speciation already exists** without ions: Rodriguez 2012
  (Fig. 9b) and Perdomo 2023 (Fig. 14) derive carbamate and bicarbonate from
  association and compare them with NMR. Claims must say *explicit-ion* and
  *with metrics*.
- **EOS heat of absorption for MEA exists**: Wang 2018 PR-CPA (Eq. 11,
  Figs. 18–19). Lloret and Vega (soft-SAFT, Faraday Discuss., about 2017) and
  Pereira et al. 2018 (SAFT-γ Mie, Applied Energy) report MEA heats of
  absorption but were not read.
- **Identifiability of K versus activity** is argued generally by Smith,
  Rutherford and Leal 2026 (abstract only). Activity-coefficient papers
  already report non-identified parameters (Austgen, Hilliard, Zhang, Akula).
  Claim 2 is new only as a quantitative MEA EOS instance.
- **The ion-dependent Born direction** was proposed by Bülow 2021a for MDEA.
- **Unread explicit-ion amine EOS work:** Raeispour Shirazi and Lotfollahi
  2019/2020, "ePC_SAFT-MB" (MSA + Born), MDEA (paywalled). If an MEA
  extension exists outside the searched scope, claim 1 fails. A Scopus search
  on "electrolyte" + "SAFT" + "monoethanolamine" is the check before
  submission.

### 9.5 Defects found in repository records

These are recorded here, not fixed, because the notebook and data belong to
their own owners.

- **Matin 2012 bicarbonate targets.** The 19 Matin HCO3- targets (loading
  0.106–0.531) are scored against model HCO3- alone
  (`data/reference/MEA/manifests/speciation_target_membership.csv`, empty
  `linear_coefficients`). Matin assumes carbonate is zero and folds it into
  bicarbonate above loading 0.3 (Eqs. 18–19b). The equivalent model quantity
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

### 9.6 What was read and what was not

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
Kim and Svendsen 2007, Kim et al. 2014.

Not read or read only in part:

- **Not in Zotero:** Austgen 1989, which holds the MEA-specific parameters.
- **Supplements not available locally:** Matin 2012 (Tables S1–S2), Bülow 2021a
  (Tables S1, S3), Pakravesh 2025a, and the Silva 2024 ion list.
- **Abstract only:** Smith, Rutherford and Leal 2026; Silva 2024; Novak 2023.
- **Not in Zotero, not read:** Lloret and Vega (soft-SAFT); Pereira et al. 2018
  (SAFT-γ Mie).
- **Paywalled:** Raeispour Shirazi and Lotfollahi 2019/2020.
- **Only in figures, not digitized:** Wong 2015 Fig. 8, Wong 2016 Figs. 5–6,
  du Preez Fig. 5, Baygi Fig. 8.
- **Unclear from text extraction:** which Aronu 2011 parameters were refitted
  (Tables 7–9).
- **Not checked:** local copies were not hash-checked against `literature/index.csv`.
