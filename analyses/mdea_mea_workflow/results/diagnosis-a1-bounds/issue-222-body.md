## Experiment: do the MEA shared-species parameters transfer to MDEA–CO2–H2O?

Parent: #220. This is the published design. It incorporates the GPT-6 Astra draft, two Claude Fable 5.1 readiness reviews and the owner's decisions of 2026-10-28. The first review (Revise) had ten required findings; the re-check of this issue (Revise) had eight, R1–R8. All are applied below, the re-check's in its own replacement text.

### Question and intended use
Can the MEA paper's ePC-SAFT formulation describe MDEA pressure, speciation, absorption heat, density, heat capacity and binary VLE when every shared-species parameter stays fixed and only MDEA-specific quantities are fitted? The result is an assessment of parameter transfer between two solvents, within the measured MDEA domain, together with a retained MDEA parameter record. It does not qualify absorber use and does not establish universal ion parameters. #126 did not answer this question: it had no Born term and used only Wangler's convention.

### Model and frozen inputs
- **Model:** as in `docs/scientific/latex/sections/epc_saft_equation_of_state.tex`: hard chain, dispersion, association, Debye–Hückel, and the SSM+DS Born term with its corrected Eq. 7. It keeps the density-, temperature- and composition-dependent permittivity and its derivatives, ε_ion = 8 and c_shell = c_dielectric = 1. It runs on Engine `3e83e19c`, wheel `0d08dff9…6804`. Generic equations, solving and differentiation stay in the Engine.
- **Frozen (shared species):** the full declarations of H2O, CO2, H3O+, OH-, HCO3- and CO3^2-, and every shared–shared interaction. The owner of these values is `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`, SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`. A pair involving MDEA or MDEAH+ is MDEA-specific.
- **Two frozen shared values are MEA calibration quantities, not source values:**
  - k(HCO3-–water) = 0.72705585, with conditional SE 1.265 on [−0.5, 1];
  - the R2 enthalpy shift, −1.364 kJ/mol with SE 5.292.

  The manuscript tables own their fitted status. The JSON provenance for the bicarbonate–water pair cites a diagnostic start file, which is a locator defect. Transfer conclusions about these two values are bounded by their MEA uncertainty.

### Chemistry
- **Species:** eight in the liquid: H2O, CO2, MDEA, MDEAH+, HCO3-, CO3^2-, H3O+ and OH-. The vapor holds only H2O, CO2 and MDEA. There is no carbamate.
- **Reactions:** R1–R3 are the frozen MEA laws, including the R2 shift. The fourth reaction is MDEAH+ + H2O ⇌ MDEA + H3O+.
- **MDEA dissociation law:** ln K_x = −83.491 − 819.7/T + 10.976 ln T, from Uyan 2015 Table 1, on the mole-fraction basis and in the dissociation direction.
  - Use ln K_m = ln K_x + 4.0165 (the solute stoichiometric sum excluding water is +1). This gives pK_m 8.55 at 298.15 K (pK_x 10.29).
  - Use the MEA R5 convention for the hydronium form, the water activity and the 100 kPa source standard pressure.
  - Before Build, acquire Kamps and Maurer 1996 (not in Zotero; owner approval needed through cse:zotero) and confirm the coefficients and basis. The 278–368 K range comes from that paper's title. Kamps–Maurer basis: resolved when the acquired paper's coefficients and basis reproduce ln K_x of Uyan Table 1 and of Jakobsen 2005's reaction-constant table at their printed precision, and give pK_m = 8.55 at 298.15 K on the molality basis. The automatic Zotero add of DOI 10.1021/je960141+ failed at its metadata step on 2026-10-28; the owner adds it by hand.
- **Feed:** one mole of analytical MDEA plus the source water; loading α = n(CO2 added)/n(MDEA total). Complete-feed mass is used for the density and heat-capacity conversions.

### Two MDEAH+ conventions, both fitted (owner decision: "try both")
| | Variant A, MEA convention (single sphere) | Variant B, reading A (charged molecule, as in #126) |
|---|---|---|
| Segments | m = 1 | m = 3.675 |
| Packing diameter | 0.88σ, temperature-independent | neutral-style, temperature-dependent |
| Like-ion dispersion | excluded | kept (self-dispersion) |
| Association | none | four sites, two donor and two acceptor, self-energy 0 K, volume equal to MDEA's converted κ; Wolbach–Sandler cross-association with water and with MDEA, no correction; none with CO2 (Uyan 2015 §4.1, Table 4 footnote a, §4.3.2) |
| Debye–Hückel diameter | σ | σ(MDEAH+), the fitted value, as in Variant A and in #126 (Held 2008, a_j = σ_j) |

Variant B's parameter document declares MDEAH+ with the Engine's charged_molecule_ion flag and no packing diameter, declares the MDEAH+–CO2 pair as no_cross_association, and gives MDEAH+ the same fitted Born diameter and unit solvation factor as Variant A.

Both variants use the same data, weights, fitted coordinates, bounds and falsifier, and both are reported side by side. Neither is chosen after the fact by its pressure score. Each gets its own pass or fail verdict.

### Pure MDEA and permittivity
- **Pure MDEA:** the 4C set, two donor and two acceptor sites: m = 3.675, σ = 3.563 Å, u/k = 228.711 K, ε^AB/k = 2046.624 K and κ^AB = 0.123858 (Pahlavanzadeh 2013 Table 2; Uyan 2015 Table 3).
  - Pahlavanzadeh Eq. 4 uses d_ij³. **Convert κ^AB to the σ_ij³ convention** by the MEA method of Section S1, with the bundle's association-volume script. Retain the converted value and its pure-MDEA saturation AARD; this is the pure-MDEA reference check. Converted κ: the constant that least-squares fits Pahlavanzadeh's own 4C model saturation pressure and saturated-liquid density at 21 temperatures from 293.15 to 393.15 K, the Section S1 method; retain the AARDs against that model. Resolved when the Engine replay of the source model agrees within the S1 tolerances and the value is fixed to eight significant figures.
  - MDEA–water cross-association uses Wolbach–Sandler with no correction. MDEA and CO2 do not associate.
- **Permittivity:** fit two MDEA dielectric coefficients of the MEA law to Hsieh 2007 Table 2 (pure MDEA) and Table 5 (x = 0.2–0.8, 303–328 K; needs transcription), using model densities. Then freeze them.
- **Ideal-gas Cp:** represent MDEA as a polynomial in the form of `physical-ideal-gas-calorics.json` (MEA uses a cubic, with H and S anchored at 313.15 K). Fit it to Wangler Table 3 (the Aly–Lee form, Eq. 26) or take a cited polynomial, and record its deviation over 293–423 K. Ideal-gas record: resolved when it reproduces the heat capacity implied by Wangler Eq. 26 within 0.5 % over 293–423 K and anchors h = s = 0 at 313.15 K, the MEA amine convention. Check the units of Eq. 26 against the PDF first: the reading copy may have dropped a factor of T.

### Fitted coordinates (9 per variant, plus 2 dielectric coefficients fitted beforehand)
| Coordinate | Count |
|---|---:|
| MDEA–water k(T_ref) and its slope | 2 |
| One CO2 interaction coordinate, chosen by the probe below | 1 |
| MDEAH+–water k(T_ref) and its slope | 2 |
| MDEAH+–HCO3- constant k | 1 |
| MDEAH+ σ, u/k and Born diameter | 3 |

- **CO2 coordinate probe** (no optimizer): at each variant's start 1, compute the column-normalized Jacobian of the 20 Kuranov log pressures above α = 1.0, all at or below 393 K, with respect to k(MDEA–CO2) and k(MDEAH+–CO2). If both variants rank the same column larger, keep it for both and fix the other at zero. If they disagree, stop and return the choice to the owner before stage 2. Retain both columns for both variants.
- **Declared starts**, three per variant, plus a fourth for Variant A (amendment 2026-10-28), fixed before stage 2: (1) σ(MDEAH+) at the variant's convention value, 5.50 Å for A and 3.563 Å for B, u/k = 228.71 K, Born diameter 5 Å, every MDEA-specific k and slope zero; (2) start 1 with k(MDEAH+–water) = −0.2298 from #126 and the MEA MEA–water values k = −0.0899, slope −8.06 K; (3) start 1 with the MEA MEAH+ values u/k = 177.9 K, k(MDEAH+–water) = −0.5, slope −41.6 K. Every endpoint is reported.
- **Start amendment (owner decision 2026-10-28, after the start-1 phase diagnosis in `analyses/mdea_mea_workflow/results/diagnosis-carson-split/`):** every declared start sat in an unphysical two-liquid region. With k(MDEA–water) = 0 the MDEA–water binary itself is immiscible (gap x(MDEA) ≈ 1e-5 to 0.8 at 298.15 K); it becomes miscible only at k ≤ −0.13, and k(MDEAH+–water) = 0 leaves an ion-pair-rich liquid. Therefore: (1) the MDEA–water k(313.15 K) and slope in **all** starts are replaced by the stage-1 item (k) pre-fit to Kim 2008 alone; (2) start 1's k(MDEAH+–water) is −0.2298 (slope 0); (3) start 2 then coincides with start 1 for both variants and is recorded as a duplicate, not run separately; (4) start 4 keeps Bülow's MDEAH+ σ, u/k and Born diameter but takes the pre-fit MDEA–water pair instead of the projection of Bülow's cubic, which lies above the −0.13 miscibility threshold at 298.15 K (−0.115 there, −0.132 at 313.15 K; the projected law becomes more negative with temperature). Both MDEA–water coordinates remain free in the joint fit, and the phase gate applies at every endpoint as before.
- **Start 4, Variant A only (Bülow-derived, projected to this model):** σ(MDEAH+) = 3.5630 Å, u/k = 228.71 K, Born diameter 3.5630 Å (Bülow, Gerek Ince, Hirohama, Sadowski and Held 2021, Ind. Eng. Chem. Res. 60, 6327, Table 2; Born diameter = σ by its Eq. 20 convention); k(MDEA–water)(313.15 K) = −0.131933125 and slope +104.9886164 K, the value-and-first-derivative projection at 313.15 K of Bülow's Table 3 cubic, which is re-centered exactly as −0.131933125 − 0.001070625 θ − 7.575e-6 θ² + 1.25e-7 θ³ with θ = T − 313.15 K (the projection differs from the cubic by 0.0106 in k at 373.15 K); k(MDEAH+–CO2), k(MDEAH+–water) and its slope, and k(MDEAH+–HCO3-) all 0 (Bülow Table 3 lists no MDEAH+ pair; its ion–water values are shared-species entries, frozen here). m = 1, packing diameter 0.88σ = 3.13544 Å, Debye–Hückel diameter σ, no association, same-sign dispersion excluded, unit solvation factor. This reuses Bülow's values as an initial guess; it is not a reproduction of Bülow's model, whose Born term, permittivity, water and bicarbonate–water values differ. All seven endpoints (four A, three B) are reported, and any representative endpoint is chosen by the fitted objective and the identifiability requirements before outside-fit data are evaluated.
- **Bounds:** σ(MDEAH+) in [3, 7] Å for Variant A (widened from [4, 7] Å on 2026-10-28 so that Bülow's 3.563 Å single sphere is admissible; the 4C-MDEA equal-volume sphere is 5.50 Å); σ(MDEAH+) in [3.0, 4.5] Å for Variant B, the segment diameter of a 3.675-segment chain whose neutral value is 3.563 Å. Born diameter in [2, 7] Å and u/k in [50, 950] K for both. Neutral–water and ion–water k in [−0.5, 0.5], unlike-ion k in [−1, 1], slopes ±1000 K, T_ref = 313.15 K. (The 4C MDEA equal-volume sphere is 5.50 Å, so the MEA cap of 5.8 Å would be too tight.)
- **Identifiability:** at the start and endpoint, record the scaled-Jacobian singular values, the weak combinations and the active bounds. Use several declared starts and profile the weak directions. If distinct vectors fit equally well but predict differently, return to Design.

### Data roles (frozen before the first optimizer run)
| Source | Role |
|---|---|
| Kuranov 1996, 82 total pressures, about 19 and 32 wt% | Fit the 313–393 K rows; the 13 rows at 413 K are reported as extrapolation |
| Ermatchkov 2006 Tables 1–3, 101 partial pressures | **Primary outside-fit set:** the 88 rows at ≤ 49 wt%. Report separately the 13 rows above 49 wt% and the 33 rows below 7 kPa. The nitrogen headspace is not modeled |
| Corrected Kamps data, Ermatchkov Table 6: 28 rows at two molalities (about 32 and 48.8 wt%) | Outside-fit high-loading comparison; never an acceptance criterion. Transcribe from PDF UD6X5RGU. Kamps 2000 = Zotero 5R8DLM23, DOI 10.1021/ie000441r |
| Jakobsen 2005 Table A5, 23 wt%, 293 and 313 K, 8 states | Fitted speciation. The column labeled xAmCOO- is MDEAH+; check the charge balance on every row and use loadNMR |
| Böttinger MDEA 2008 (DOI 10.1021/ie800914m) Table 2, 52 or more rows | Outside-fit speciation. **Keep all rows** (default; the owner may change it): compare the amine sum and HCO3- as reported, tabulate the DMDEA+ and byproduct fractions, and flag rows where those exceed the paper's 3 % amine-balance accuracy. Recount the rows from the PDF |
| Derks 2011, 4 states at 2 kmol/m³ and room temperature | Supplemental; resolve its temperature and basis before scoring |
| Carson 2000 Table 3, 298 K, 10–30 wt%, α ≤ 0.2 | Fitted heat (it fixes the low-loading value only; partial-molar definition) |
| Merkley 1987, 20/40 wt%, 289–422 K, ±5 % | **Fitted** heat (owner decision). The 60 wt% rows are an outside-fit extrapolation |
| Weiland 1997 Table 1, Cp at 298 K | Fit 30–50 wt%; report 60 wt% separately |
| Weiland 1998 Table 1, loaded density at 298 K | Fit 30–50 wt%; report 60 wt% separately |
| Sobrino 2016, unloaded density | Fit the 0.1 MPa rows, 293–393 K |
| Kim 2008 Table 8, isothermal P–x–y at 40, 60, 80 and 100 °C | Fit as a bubble-pressure log ratio; no vapor-fraction residual (y(MDEA) is 1e-5 to 7e-4) |

**Newer outside-fit comparisons (owner, 2026-10-28; none enters the fit):**
| Source (Zotero) | Role |
|---|---|
| Xiao et al. 2018, J. Chem. Thermodyn. 122, 170 (WE7ZG7KW) | Loading at 23.5 wt%, 298–313 K, 8–61 kPa CO2 partial pressure; transcribe from its table |
| Zheng et al. 2020, J. Chem. Eng. Data 65, 3784 (YKU6CMAM) | Calorimetric heat of absorption, Table 4: aqueous MDEA 30 wt% (two states) and 50 wt% (four states), all at 323.15 K and 0.53–4.19 MPa total pressure, giving α_sat and −ΔH_sat per mole CO2 with relative expanded uncertainty 0.05 on both; the loading-resolved curves are in SI Tables S1–S2, which are not in Zotero. The 40 + 10 wt% MDEA–piperazine block, which holds every 353.15 K row, is excluded. Observable: the MEA integral heat per mole of added CO2 from zero loading to the reported α_sat at the source temperature and total pressure; the model's own α_sat at that total pressure is reported beside it as context. |
| Zhang et al. 2023, Chem. Eng. J. 466, 143279 (TMHPSMM9) | Pure MDEA at 5 mol/L, about 57 wt% (119.16 g/mol; the density for the conversion is fixed from the paper), so outside the claim domain: every Zhang comparison is reported as extrapolation, like the 60 wt% rows, never as a transfer result. Loading at 298–323 K and 5–60 kPa (Figs. 5–9) and 13C NMR speciation (Fig. 4), locators to be confirmed under R1; plotted only, so digitized with a QA overlay and a stated digitization uncertainty. |
| Sedighi et al. 2024, Iranian J. Chem. Eng. 21(3), 14 (E7IXZ766) | Loading at atmospheric pressure, Table 3; only the 10–50 wt% rows are scored; no uncertainty is reported |

The Zotero attachments for Xiao 2018 (F3EC6J42) and Zhang 2023 (PU7B5G27) hold only the first page of each paper. Before item (i) runs on these two sources, acquire the full text through cse:zotero (owner approval) and record the new attachment key and hash; their table and figure locators above come from the owner's reading and are confirmed against the full text in (i). Until then both rows are declared but unscored.

Scoring: each newer loading source is scored by the existing pressure observable, the model pressure at the reported loading and temperature as a log ratio, reported as an AARD beside the Ermatchkov statistic: CO2 partial pressure for Xiao and Zhang; for Sedighi the total pressure 101.325 kPa (Table 3 footnote), with the gas-phase basis resolved from the paper's §2 in (i). Zheng uses the heat definition in its row. These four statistics are context, never pass bars, and none changes the 24.2 % criterion or the freeze.

Untouched MDEA pressure sets in the library are optional extra hold-outs: Jou, Mather and Otto, and Dicko 2010 at 50 wt%.

### Objective and checks
The objective is the MEA bounded least squares C = ½ Σ w r² (supplement §S2):

| Residual | Scale | Weight |
|---|---|---|
| Pressure, log ratio | — | 100/9 |
| Species | source-specific | 1 |
| Heat | per row, the larger of 3 kJ/mol and 5 % of the observed value | 1 |
| Heat capacity | 2 % | 1 |
| Binary bubble pressure, log ratio (Kim) | — | 1 |
| Unloaded density | 0.5 kg/m³ | 10 |
| Loaded density | s_ρ from the MDEA sources' own uncertainties | 1/N |

Jakobsen A5 is scored as the MEA Jakobsen group: MDEAH+ and HCO3- + CO3^2- each divided by total amine, difference residuals, scale the source's 5–10 % estimate of each ratio; the column printed as xAmCOO- is MDEAH+. The charge imbalance of every row is reported and excludes nothing. Heat observables: Carson rows (corrected 2026-10-28: the printed "partial molar" column is the cumulative ΔH/n(CO2) from zero loading, Carson p. 1289, as the stage-1 delivered review established) use the MEA integral heat per mole of added CO2 from α = 0 to the row's cumulative loading, at the source temperature and pressure; Merkley rows (owner decision 2026-10-28, after the stage-2 pause): Merkley's value is the slope through zero of cumulative heat (kJ/mol MDEA) against loading below the calorimetric saturation 'loading point' (Merkley 1987 pp. 439–441, Figs. 1–2), so the model observable is the MEA integral heat per mole of added CO2 from α = 0 to that run's loading point α_LP, read from Merkley Fig. 4 (loading point against temperature for 20, 40 and 60 wt% at 1121 kPa, 1466 kPa at 422.04 K), at the run's temperature and pressure. The model's integral heat from 0 to α_LP/2 is reported beside it as a check of the flatness Merkley reports. For the 156 kPa alternative-pressure calculations the endpoint is the smaller of α_LP and the model's own saturation loading at 156 kPa. Stage 1 records the definition per row; no scale or weight changes after the first optimizer run.

Reference checks:
- shared-only water and CO2 cases unchanged;
- pure-MDEA saturation after the κ conversion;
- unloaded MDEA–water VLE, permittivity and density;
- one finite-loading state;
- independent replay of every fitted prediction.

Tolerances: equilibrium residual 1e-10, replay 1e-8, derivatives 1e-5 relative. Verify charge and element balances, the pressure definition and the reference conversion separately. Run the MEA tangent-plane phase search at the fitted and comparison states for both variants.

### Pre-registered transfer test
1. Freeze each variant's fit before evaluating any outside-fit data.
2. **Primary statistic:** the CO2 partial-pressure AARD on the 88 Ermatchkov rows at ≤ 49 wt%.
   - **Pass if ≤ 24.2 %**, the MEA model's own outside-fit pressure deviation (112 non-fitted rows; owner decision).
   - References for context: 42.72 % (#126 reading-A gate) and 60.97 % (#126 fitted endpoint) on the same 88 rows. 11.86 % is the MEA fitted-data value and is not used as a pass bar.
3. **Sensitivity follow-up, not attribution, run for each variant:**
   - refit the 9 coordinates plus k(HCO3-–water) within [−0.5, 1];
   - as a control, refit the 9 coordinates plus the CO2 coordinate the probe fixed at zero;
   - record the scaled-Jacobian correlation between k(HCO3-–water) and k(MDEAH+–water) at each endpoint. A magnitude above 0.95 means the pair is reported as non-separable.
4. **When the follow-up counts:** it shows that the frozen bicarbonate value matters only if it beats the control on the 88-row statistic by at least 2 percentage points of AARD, the MEA acceptance-limit allowance, while keeping the other property results. The 88 rows include the 29 rows below 7 kPa at ≤ 49 wt%; none is removed.
   - Because the MEA conditional SE already spans [−0.5, 1], no MDEA outcome falsifies the MEA bicarbonate value, and the result must say so.
   - The corrected-Kamps set is excluded from this criterion.
5. **Other properties:** compare against the MEA fitted levels as context, not as pass bars: loaded density 0.177 %, Cp 2.845 %, binary bubble pressure on its own log-ratio statistic.

### Build stages
**Stage 1, preparation, no optimizer.** (a) Transcriptions of Hsieh Table 5, Ermatchkov Table 6, Jakobsen A5, Böttinger Table 2, Merkley, Carson Table 3, Weiland 1997 Table 1, Weiland 1998 Table 1, Sobrino and Kim Table 8, each with locator, units, basis, uncertainty and file hash. (b) The κ conversion. (c) The MDEA ideal-gas record. (d) The two dielectric coefficients. (e) The Engine capability check. (f) The CO2-coordinate probe. (g) The Kamps–Maurer basis check. **Stage-1 addendum (2026-10-28):** (h) the start-4 declaration check: resolved when (1) Bülow Table 3 (water–MDEA, T_ref = 298.15 K by Eq. 26) re-centered at 313.15 K reproduces the printed coefficients, and the value-and-derivative projection onto the reciprocal law k(T) = k(313.15 K) + b(1/T − 1/313.15 K) gives k = −0.131933125 and b = +104.9886164 K, with projection minus cubic +0.0106 at 373.15 K; (2) every start-4 value lies strictly inside its Variant A bound: σ in [3, 7] Å, Born diameter in [2, 7] Å, u/k in [50, 950] K, each k in its declared interval, the slope within ±1000 K; and (3) the retained start-4 Variant A document differs from the retained start-1 document only in the MDEAH+ segment, packing, Debye–Hückel and Born diameters and in the MDEA–water pair, which carries T_ref = 313.15 K so the Engine applies the reciprocal law, while the shared record SHA-256 00e77608… and every shared pair are byte-identical; (k) pre-fit of k(MDEA–water)(313.15 K) and its reciprocal-temperature slope to Kim 2008 Table 8 alone (ion-free MDEA–water, bubble-pressure log-ratio residual, weight 1, MEA bounds), resolved when (1) it converges with its scaled-Jacobian singular values recorded, (2) the binary is miscible at every Kim state and over x(MDEA) 0–1 at 293.15, 313.15, 353.15 and 393.15 K (tangent-plane search and a Gibbs-mixing convex-hull scan), and (3) every amended start passes the tangent-plane search at Carson rows 1 and 10. If (2) or (3) fails, stage 2 returns to Design. (j) digitization of Merkley Fig. 4 loading points (calibrated axes, QA overlay, stated digitization uncertainty, checked against the printed 0.35 mol CO2/mol MDEA for 40 wt% at 388.71 K, Fig. 2 text); stage 2 runs its fits only after (j) passes. (i) transcription or digitization of the four newer outside-fit sources: resolved when each retained file carries the attachment key and hash, the locator, units, the wt% or molarity basis with its conversion, the pressure basis (partial or total) per row, the source uncertainty or the statement that the source reports none (Sedighi), the row count (Zheng: 6 pure-MDEA rows; Sedighi: 24 rows, 15 scored at 10–50 wt%, the 60, 80 and 98 wt% rows reported unscored; Xiao and Zhang after R1), and, for digitized values, the QA overlay and a stated digitization uncertainty. Each item carries the completion criterion given with it and is retained in the MDEA analysis directory. Derks is scored in stage 2 only if (a) resolves its temperature and basis; otherwise it is reported unscored.

**Stage 2, fitting.** Starts only when every stage-1 item is retained with its criterion met and the owner has confirmed in one comment on this issue that the data roles, scales, weights, bounds and declared starts are frozen. Nothing in stage 1 changes a role, scale, weight or bound.

### Stop conditions
**In stage 1:** admit each variant's full eight-species parameter document on the pinned Engine and evaluate one unloaded and one loaded liquid state: four MDEA sites with two-site water under Wolbach–Sandler, the MDEA ideal-gas record, and for Variant B the charged_molecule_ion flag with its four sites, Born diameter and solvation factor under the MEA density-dependent permittivity. Retain the admission messages and the per-term residual Helmholtz contributions. A refusal stops stage 2 for that variant.

**During the work:**
- No data set changes role after the first optimizer run.
- The 13 Kuranov rows at 413 K are reported as extrapolation, never as pass or fail. Above Hsieh's 328.15 K the MDEA dielectric coefficients are a model assumption, as the MEA paper treats its own law; those states stay in the primary statistic and in every property comparison, and the result states this limitation.

**Return to Design if:**
- the parameters are non-identifiable;
- an endpoint sits on an arbitrary bound;
- a phase assumption fails.

Never release a shared parameter or drop a property group silently, and never overwrite the MEA record.

### Outputs and claim limits
- **Deliverable:** one MDEA analysis notebook with both variants: inputs and hashes, parameter records, row-level predictions, failures, residual summaries, identifiability and phase-search results. Independent review follows on delivery.
- **Claim limits:** the strongest claim is conditional transfer of the frozen MEA record, under the stated model, data and domain (293–393 K; ≤ 49 wt% for the pressure test, ≤ 50 wt% for the other properties). Fitted residuals are calibration evidence; outside-fit comparisons are physical assessments within the domain. There is no manuscript promotion and no process-use claim.

### Published benchmark
Bülow 2021 SI Table S3 reports Kuranov pressure ARDs of 10.54–42.21 % (19 wt%) and 14.78–63.06 % (32.3 wt%) by isotherm. They are not directly comparable here: Bülow labels the points CO2 partial pressure, these Kuranov rows are total pressures, and Table S3 gives no row counts. The owner chose to reproduce Bülow's model in #223, so a like-for-like comparison comes from that study; no #222 parameter or pass bar depends on it. This issue's pass bar (24.2 % on the 88 Ermatchkov rows) is unchanged.

### Remaining owner decisions (defaults apply unless changed)
- The Böttinger row rule: default is to keep all rows and flag them.
- The MDEAH+ bounds above.
- Acquisition of Kamps and Maurer 1996 through Zotero: **needs approval.**

🤖 Generated with [Claude Code](https://claude.com/claude-code)







