# Bounded R2 temperature test, issue 140, Stage 3

## Question, recommendation and authority

Can independent aqueous CO2 first-dissociation information replace R2's temperature law so that a 30 wt% MEA model estimated on loaded-solution data at ≤60 °C meets the adopted 80 °C pressure error, without degrading either low-temperature observation family by more than 10%? Compare this with estimating R2 enthalpy from the same low-temperature loaded-solution data.

**Recommend independent R2(T) as the primary test, conditional on source admission.** Keep free R2 enthalpy as a prespecified secondary diagnostic. Independent chemistry separates the standard-state temperature law from the activity model; freeing R2 and an interaction temperature coefficient with only two pressure isotherms may exchange their effects. A pressure improvement from the latter does not identify a physical R2 enthalpy. The available coefficient comparison suggests a modest source-law correction, so success is uncertain; do not enlarge it to recover the historical fitted shift.

This is the design requested by the [owner's Stage 2 decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/140#issuecomment-5927029509). The [following owner note](https://github.com/tannerpolley/Amine-Thermodynamics/issues/140#issuecomment-5927062016) confirms Engine heat support already exists. This bounded test retains pressure/species estimation only; heat remains an assessment quantity. Adding heat to estimation, changing the Engine without qualification, adopting parameters, or writing manuscript conclusions requires another owner decision.

Base: `329ac06f702685faaaea6854403def4b308c7e18`; worktree `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/downstream/.worktrees/Amine-Thermodynamics-140-reanchor`; branch `work/140-temperature-reanchor`. Issue body read on 2026-10-01, SHA-256 `3127ba66f28579ba023362d1f4e1e16808bb0ba61733cc300b57875a923a255c`. This file owns the bounded Stage 3 proposal; the issue comment links it. It is not an execution authorization. **No fit or equilibrium solve was run in this design task. Stop after local commit and issue comment; the parent obtains independent readiness review before fits.** Source and wheel admission below are unresolved execution requirements, not findings that the chemistry fails.

## Starting evidence and scientific meaning

The retained Phase B and Stage 2 results already answer the R4/R5 question for their exact inputs. Reuse `preregistration.md`, `stage-2-preregistration.md`, `stage-2/stage-2-summary.json`, `stage-2/comparison-scores.csv` and the working notebook; do not repeat their campaigns.

| Record | Low-T cost | Canonical 80 °C AARD, 21 rows | Wagner near 353 K AARD, 11 rows |
|---|---:|---:|---:|
| Adopted, historical high-T selection ancestry | 32.991897 | 20.270257% | 24.511124% |
| Phase B source R2/R4/R5 primary | 33.012694 | 29.333590% | 52.301450% |
| Stage 2 source R2, independent dilute R4/R5 primary | 32.844138 | 28.578316% | 51.611414% |

Stage 2 primary canonical 100–120 °C AARD is 50.89%; signed mean logarithmic pressure errors at 80 °C are about −0.36 to −0.73. These are numerically complete, diagnostic conditional comparisons. They suggest missing temperature response, without assigning its cause uniquely to R2. The historical R2 shift −8.2018845 kJ/mol used loaded measurements at 80/120 °C and is comparison history only, never a start, bound estimate or prior.

Sources read for this design: [Austgen 1991](https://doi.org/10.1021/ie00051a016) PDF pp. 546–549, Eq. 7, Table V and Data Regression; [Böttinger 2008](https://doi.org/10.1016/j.fluid.2007.09.017) Markdown §§4–8, Table 5 and conclusion; [Baygi–Pahlavanzadeh 2015](https://doi.org/10.1016/j.cherd.2014.07.017) §§3.1–3.3, Eqs. 17–18, Table 5 and conclusion; [Wangler 2018](https://doi.org/10.1016/j.fluid.2017.12.033) §§4–6.1/7, Eqs. 19–23 and Tables 2/4–7. The three Markdown files match their current Zotero file hashes in the main checkout's `literature/index.csv`. Austgen PDF `NL4W5CA6/UNTA6KIT` hash is `8c0a6a57e5bf9e28b1f9da8022d54290506fe04b4286b6494ef8a44fd924f8db`; Table V was visually checked. The worktree lacks `literature/`; the main shelf and verified Zotero files supplied these readings. No library write or paper conversion occurred.

Published practices differ: Böttinger uses extended Pitzer activities, retains MEA proton dissociation and estimates carbamate formation from NMR at 293–353 K; Baygi uses ideal chemical activities with PC-SAFT physical fugacities, estimates pure/binary parameters and assesses ternary pressure without ternary fitting; Wangler's MDEA ePC-SAFT model estimates binary/ion–water parameters, extends its CO2 comparisons to MDEA mass fraction 0.6, and assesses ternary gas solubility and heat. These do not prescribe our 10%/20.27% limits. Those are owner-selected experiment limits. Austgen's eNRTL analysis documents correlated temperature coefficients and fixes unestimable terms. None establishes identifiability for the present seven-coordinate secondary fit.

## Allowed information and admitted inputs

**Allowed-information rule:** independent pure-water thermodynamic K1 data and dilute inorganic measurements used to infer zero-ionic-strength K1 may include T≥80 °C. They contain no loaded-MEA observations and constrain a separate aqueous chemical standard state. Thus this tests loaded-MEA temperature transfer using independently measured chemical temperature information; it is not extrapolation from exclusively ≤60 °C information in every subsystem. Source choice, transformations, bounds and compression must be frozen without using any loaded-MEA ≥80 °C result. Shared source data between published compilations are one campaign, not multiple independent measurements.

**Excluded throughout selection:** loaded-MEA pressure/species/heat at ≥80 °C, transfer observations, inherited selected R2 shifts, adopted interaction/dispersion starts, historical high-T caches and any new #123/#137 record. Known Phase B/Stage 2 high-T scores motivate the scientific question, but do not tune Stage 3 coefficients or choose among its fitted records. Wagner was never accessed before Phase B; it has since been assessed twice and is now a previously assessed cohort.

The exact loaded calibration remains `training-targets.csv` (SHA-256 `8a9426d253b23a5dce5db9e5fa71493136a843f40d919f694021815d5b8ea36b`): 84 states, 142 targets, 48 pressures at 313.15/333.15 K (32/16), and 94 species at packet 293.15/313.15/333.15 K (66/16/12). Preserve all measured sums, source conventions, exclusions, feeds and corrected loading. Keep Matin's measured-21 °C/packet-20 °C convention and report-only bicarbonate/carbonate targets. No new loaded row is admitted.

Retain the Stage 2 fixed dilute R4/R5 estimates, not new fits: R4 A=2.282869879, B=−1585.057202 K; R5 A=−1.443016604, B=−6080.400894 K, in ln K=A+B/T. Build takes full-precision values from `stage-2/source-fit.json`, SHA-256 `4993fca00d573b573b8d85dbebd3c46039acf4c92b9fecb307a6f0bf7276f530`. Their original selected inputs are four Kim 2011 Table 7 Exp MEA rows at 298.15–333.15 K, four Aroua 1999 Table 3 zero-I formation rows at 298–328 K, with three low-T Kim heat rows used only for comparison. Zotero PDFs are `89KKLDUF/7R3LYF7R` (DOI [10.1016/j.jct.2011.06.004](https://doi.org/10.1016/j.jct.2011.06.004)) and `L8GDWZEW/93Y7NVMH` ([10.1021/je980290n](https://doi.org/10.1021/je980290n)). Their source identities, selected rows and file hashes are retained in `stage-2-inputs.json`; do not reread high-T Kim rows to select Stage 3. Source uncertainty and chemical consistency remain UNRESOLVED under the inherited diagnostic exception.

Live `cse-zotero doctor` confirms read-only source access. Project/global Companion queries, live author/title searches and `~/Zotero/storage` filename inspection found no carbonic-acid primary papers below. `data/reference/MEA/manifests/source_status_manifest.csv` has no R2/pure-water K1 entry; its generic external-source rows are not admission of these constants. Edwards 1978 is metadata plus a publisher HTML snapshot (`Y27HTJXV/VV38QD9Q`), with no local PDF. Austgen is locally readable.

| Source and purpose | DOI / availability | Admission decision |
|---|---|---|
| Harned & Davis 1943, aqueous CO2 ionization, 0–50 °C | [10.1021/ja01250a059](https://doi.org/10.1021/ja01250a059); absent Zotero; publisher metadata read | Low-T source check only, not an 80 °C measurement; owner import needed if used |
| Edwards et al. 1978, Austgen's Table V source | [10.1002/aic.690240605](https://doi.org/10.1002/aic.690240605); metadata/HTML only | Austgen printed coefficients remain verified; acquire PDF if tracing the underlying measurement selection |
| Plummer & Busenberg 1982, independently synthesized CO2–water K1(T) | [10.1016/0016-7037(82)90056-4](https://doi.org/10.1016/0016-7037(82)90056-4); absent Zotero | Preselected primary law, conditional on full-paper import, methods/basis/uncertainty reading and PDF verification; do not fit its carbonate-solubility measurements here |
| Patterson et al. 1982, NaCl-media first ionization to 300 °C | [10.1016/0016-7037(82)90320-9](https://doi.org/10.1016/0016-7037(82)90320-9); absent Zotero; publisher abstract read | Source lineage and zero-I cross-check after import; finite-I quotients are not pure-water constants |
| Millero et al. 2007, NaCl dissociation measurements and literature synthesis | [10.1016/j.gca.2006.08.041](https://doi.org/10.1016/j.gca.2006.08.041); absent Zotero; author-institution abstract read | Check newer pure-water reference and high-T lineage after import; do not assign NaCl fit scatter as pure-water measurement uncertainty |
| Stefánsson, Bénézeth & Schott 2013, dilute hydrothermal ionization/ion pairing to 200 °C | [10.1016/j.gca.2013.04.023](https://doi.org/10.1016/j.gca.2013.04.023); absent Zotero; author-institution/publisher abstracts read | Newer independent cross-check after import; resolve simultaneous sodium-pair estimation and reference pressure before using K1 |
| Millero 1979/1995 seawater formulations | [10.1016/0016-7037(79)90184-4](https://doi.org/10.1016/0016-7037(79)90184-4), [10.1016/0016-7037(94)00354-O](https://doi.org/10.1016/0016-7037(94)00354-O); absent Zotero; publisher abstracts read | Excluded as direct R2 replacements: salinity/apparent-constant conventions require conversion; no imports required for this test |

Required owner imports for the primary-source comparison are Plummer–Busenberg 1982, Patterson 1982, Millero 2007 and Stefánsson 2013. Harned–Davis is an optional historical check; Edwards needs its PDF only if the ancestry audit requires the underlying rows. Do not mutate Zotero or acquire papers automatically. Before Ready, retain exact PDF/attachment identities, hashes, table/equation/page locators, CO2 definition, proton scale, standard pressure and uncertainty statements for the selected independent law. Publisher/author abstracts provide leads, not admitted experimental rows. No claim that Plummer–Busenberg is the current best pK1(T) is established from this incomplete full-paper comparison. If the imported newer results materially contradict the preselected law within its domain, return to Design and preregister the source change before any loaded fit; never choose the law by pressure scores.

## Reaction equations and basis

**S3-E1 — aqueous reaction quotient.** R2 is CO2(aq)+2H2O ⇌ HCO3−+H3O+. Solute activities are a_i^m=gamma_i^m m_i/m°, m°=1 mol/kg water, gamma_i^m→1 in aqueous infinite dilution; a_w is Raoult-normalized. Define the hydrated proton by mu_H+=mu_H3O+−mu_H2O and a_H+=a_H3O+/a_w. Then

    K2_m = a_HCO3^m a_H3O^m / (a_CO2^m a_w²)
         = a_HCO3^m a_H+^m / (a_CO2^m a_w).

Only in the pure-water infinite-dilution limit does a_w→1 permit direct use of K1=a_H+ a_HCO3/a_CO2. Do not delete water factors at loaded composition. This is the same hydrated-proton interpretation used in Stage 2; verify the Engine's reaction reference uses it. Literature K1 for dissolved CO2 is neither gas Henry's law nor the true H2CO3 dissociation constant near pKa≈3.6. If a source denominator is CO2*=CO2(aq)+H2CO3, K1_CO2=K1_star(1+r_h), r_h=m_H2CO3/m_CO2 at infinite dilution. Its definition and T dependence must be verified; do not silently equate species or add a hydration reaction. Missing correction or source convention blocks admission.

**S3-E2 — basis conversion.** For dimensionless solute standards, m_i/m°=x_i/(M_w m°) at infinite dilution, M_w=0.01801528 kg/mol. Net solute stoichiometry for R2 is +1, hence

    ln K2_m = ln K2_x − ln(M_w m°).
    ln K2_x = 231.465 − 12092.1/T − 36.7816 ln(T/1 K).
    ln K2_m = 235.4815349922995 − 12092.1/T − 36.7816 ln(T/1 K).

Austgen 1991 Table V reaction 4a, p. 547, explicitly names Edwards 1978 and a 0–225 °C correlation interval. This is a reported correlation interval, not verified evidence that every temperature was measured. Direct molal pK1 maps as ln K=−ln(10)pK1 with no additional 55.51 factor. For a concentration constant, q=rho_w m°/c°, c°=1 mol/L; K_c=q K_m for R2. Convert before comparing, including density derivatives in enthalpy. Seawater proton scales and finite-I apparent constants cannot enter by a molarity factor alone.

**S3-E3 — reference transfer.** With source and Engine potentials related by mu_i=mu_i,src°+RT ln a_i,src=mu_i,E°+RT ln a_i,E,

    ln K_E = ln K_src + sum_i nu_i (mu_i,src°−mu_i,E°)/(RT).

The Engine owns this conversion and its EOS derivatives; the application owns source identity and reference declaration. Reuse `shared_evaluation._engine_reaction_records`, `_reaction_reference`, `_neutral_reference` and Engine `CommonMolalityInfiniteDilution`. Set a common-molality law once; do not also apply the Austgen offset. Molecular CO2 must retain its aqueous infinite-dilution reference, never a pure-liquid or gas standard. Inorganic pure-water K1 is transferable as a standard-state input only under these matched conventions; transfer of the finite-composition activity model to concentrated MEA is the hypothesis being assessed. Charge-neutral R2 does not determine separate single-ion standard potentials.

For Plummer–Busenberg, the [USGS author record](https://pubs.usgs.gov/publication/70011789) states 1 atm below 100 °C and the water vapor-pressure curve above. Bind the fitted source representation to 101325 Pa for the ≤80 °C test, rather than the existing R2 `None` (system-pressure) setting. Verify the Engine reference-pressure conversion; do not assume pressure effects vanish. The 100–120 °C assessments use a separately disclosed mathematical continuation of the frozen 1-atm law and remain outside the candidate-use domain; they do not qualify the published pressure curve or justify new pressure-dependent chemistry.

## Source-law comparison already calculated, without fitting

**S3-E4 — independent candidate law.** The [accessible Plummer–Busenberg publisher abstract](https://www.sciencedirect.com/science/article/abs/pii/0016703782900564) gives, with T in K,

    log10 K1 = −356.3094 − 0.06091964 T + 21834.37/T
               + 126.8339 log10(T/1 K) − 1684915/T².

Only direct coefficient arithmetic was performed here. This transcription still requires the imported PDF/basis check; the following is a provisional correlation comparison, not accepted physical validation or a newly fitted result.

| T / °C | Austgen molal pK1 | Candidate pK1 | ln(K_candidate/K_Austgen) |
|---|---:|---:|---:|
| 20 | 6.389330 | 6.381871 | +0.017175 |
| 25 | 6.359066 | 6.351864 | +0.016583 |
| 40 | 6.299458 | 6.297395 | +0.004749 |
| 60 | 6.281664 | 6.290305 | −0.019895 |
| 80 | 6.320228 | 6.338232 | −0.041454 |

At 80 °C this is K_candidate/K_Austgen=0.959394. The enthalpy from ΔHr°=RT² d(ln K)/dT is −7.46075 versus −8.36814 kJ/mol at 80 °C. Those differences are small relative to the magnitude of the inherited fitted correction; they are not uncertainty-normalized differences. At fixed aqueous activities a decrease in K tends to raise the molecular CO2 required by the quotient, but coupled pressure/speciation need not change by the same percentage. A 4.1% K change alone is not evidence that a 29% pressure error will reach 20%.

Methods, exact source uncertainties, newer independent coefficients and the CO2/CO2* definition remain unread for these absent papers. Therefore the 80 °C comparison with a verified current-best chemical law is an explicit source-admission gap, not silently replaced by this provisional table.

## Seven-fit maximum and frozen estimation method

R1/R3, SSM+DS Born/dielectric/association choices, ions and binary interactions remain as disclosed in Phase B. Keep source CO2 dispersion 169.21 K fixed in both tests. Its historical 173.44025 K selection included 80 °C; the independent constant-energy-free branch is not repeated. Keep Stage 2 R4/R5 fixed, diagnostic. No density, Cp, loaded heat, fitted reaction curvature, additional interaction slope, folds, bootstrap or optimization profile enters loaded-solution estimation.

**Source representation, one fit maximum.** The installed `28181e72` wheel's `ReactionLogPolynomial` supports A+B/T+C ln(T/Tref)+DT, not E/T². Do not discard the last term or write generic Engine chemistry. After source admission, make one source-only linear least-squares representation of S3-E4 on the eleven predetermined temperatures 273.15+10j K, j=0,…,10. Fit

    L0 + B(1/T−1/T0) + C ln(T/T0) + D(T−T0), T0=313.15 K.

Use equal numerical representation weights, scaled columns and NumPy `linalg.lstsq`, reusing the Stage 2 source-estimation owner; these eleven correlation samples are not eleven new measurements. Full source coefficients determine every sample. Map native a=L0−B/T0−D T0, b=B, c=C, d=D. Check a 1 K grid over 293.15–353.15 K plus every actual assessment temperature after freezing the coefficients. Required representation error on the candidate interval: |δ ln K|≤1e−3 and |δΔHr°|≤0.10 kJ/mol. These are engineering approximation limits, not source uncertainties. Rank deficiency or exceeding either limit stops this design; no different grid, weights, fifth coefficient or new source fit is authorized. Outside-domain errors are reported, never used to reselect coefficients. The law keeps source-derived curvature; no A+B/T-only extrapolation is substituted. Representation covariance is not chemical measurement covariance.

**Secondary enthalpy model, S3-E5.** Relative to the verified source Austgen molal law,

    ln K2(T) = ln K2,Austgen(T) + δa + δb/T
             = ln K2,Austgen(T) + δL0 − δH/R (1/T−1/T0),
    δH=−R δb, δL0=δa+δb/T0; R=8.31446261815324 J/(mol K).

R2 enthalpy is free and source curvature fixed. Fit native a and b as two independent reaction coordinates; report their transformed δL0/δH covariance. The inspected newer wheel interface exposes one stored coefficient per reaction coordinate; it does not expose a centered a/b affine constraint. Consequently this design honestly includes the intercept nuisance coordinate, rather than claiming a fixed 40 °C anchor while silently moving it. Native bounds are δa∈[−8,+8], δb∈[−20000/R,+20000/R] K. The latter is δH∈[−20,+20] kJ/mol; ±8 allows the corresponding entropy/intercept compensation at 313.15 K. These are finite engineering search limits, not chemical confidence intervals. Scales: a 0.1, b 10 K. Starts: (δa,δb)=(0,0) and (2000/(R T0),−2000/R), the second having δL0=0 and δH=+2 kJ/mol. No historical fitted R2 coefficient enters.

| Estimation | Active coordinates | Starts | Fit count |
|---|---:|---|---:|
| Independent R2 four-coefficient representation | 4 source representation coefficients | Closed linear solve | 1 |
| Independent R2, constant interactions, fixed CO2 energy | 4 existing interaction intercepts | Two prescribed defaults | 2 |
| Independent R2, interaction slope, fixed CO2 energy | Existing 4 intercepts + MEAH+–water slope | Two prescribed defaults | 2 |
| Source R2 with free a/b, interaction slope, fixed CO2 energy | Existing 5 + R2 a/b | Two prescribed defaults | 2 |
| Total maximum | | | **7** |

There is no eighth exploratory fit, fallback source, extra start, unregistered continuation or bound enlargement. If sources cannot be admitted, do not silently spend the independent-route budget on the secondary route. Each route may miss; their roles do not change after assessment.

Loaded objective remains Φ=½Σp[ln(pcalc/pobs)/0.3]²+½Σx[(xcalc−xobs)/(0.1xobs+0.001)]², on exactly 142 targets. Scales are diagnostic, not measured uncertainties. Existing bounds: three ion–water intercepts ±0.5 and MEAH+–MEACOO− ±1, scale 0.01; optional MEAH+–water slope b_k∈[−1000,+1000] K, scale 10 K, k(T)=k0+b_k(1/T−1/313.15). Intercept starts are zero and (+0.05,−0.05,+0.05,−0.05); b_k=0 and energy=169.21 K at both. Regenerate training state declarations and reaction-derived thermochemistry from the candidate laws. Initialize phases from positive feed fractions and pressure from geometric bounds, retaining the accepted recovery path without historical/high-T fingerprints.

Use Engine `epcsaft.regression.fit`, native reaction-coordinate first derivatives and the existing low-temperature fit/assessment owners. No local optimizer, finite-difference reaction fitter, generic equation copy or new dependency. Proposed executable addition ceiling: 200 lines relative to `329ac06`, for source mapping and reuse of current owners; exceeding it returns to Design. No source law is fitted to loaded pressure in the primary route.

## Wheel admission and numerical completeness

The old installed wheel SHA-256 `28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2` has no native reaction fitting coordinates. Engine [#187](https://github.com/tannerpolley/ePC-SAFT/issues/187) supplies them; [#211](https://github.com/tannerpolley/ePC-SAFT/issues/211) and [#210](https://github.com/tannerpolley/ePC-SAFT/issues/210) supply direct source-ln K and finite-addition heat. This is a wheel-adoption requirement, not missing generic Engine work.

Propose the owner-reported #210 wheel SHA-256 `62c2f9078579f300c5e1dc5ae0814223b021a3b5e0a921d331cb6b63a58fbaf5` for **both** loaded routes, after parent/readiness acceptance. Its actual immutable file must be supplied and hash-verified before Build; it was not found in the inspected build-wheel locations. The current `build/environment-wheel` is `9e6a76cf…`, a different wheel; it was read only as interface evidence and is not adopted. No installation, synchronization, build or fit occurs in this design task.

Before candidate fits on the new wheel, replay the Stage 2 fixed primary and adopted low-T record on all 84 states, using separate comparison caches. Require absolute family/total cost differences ≤1e−8 against retained results, matching predictions within relative 1e−8 with absolute 1e−12 mole-fraction floor, plus existing numerical conditions. A discrepancy returns to diagnosis; never attribute a wheel change to R2. If a newer wheel is proposed, the parent pins and qualifies it before fitting; no unrecorded wheel substitution is permitted. No source checkout import.

Every loaded start must converge with all 142 finite predictions/residuals/Jacobian rows, then export/reload/rescore all training targets. Requested Engine tolerance must be met, material/charge balance errors ≤1e−7 and maximum stationarity ≤1e−10. Check k(T)<1 at fitting endpoints and after freeze at assessment endpoints. A missing solve, time limit, failed native reference conversion or nonfinite Jacobian is incompleteness, not a physical falsifier. Keep failures; no available-row-only scoring, penalties replacing rows or silent retries.

Use the Phase B two-start agreement limits: relative cost 1e−6, intercepts absolute 1e−5, interaction slope 0.1 K. For secondary R2 also require |δL0 difference|≤1e−4 and |δH difference|≤0.01 kJ/mol. Equal costs with differing parameters mean nonidentification. Both starts must satisfy agreement/completeness for an eligible finalist; an incomplete route has no finalist.

## Identifiability, selection, freeze and one assessment

Pressure has only 40/60 °C isotherms; the 20–60 °C species targets add chemical sensitivity but do not guarantee separation of R2 a/b, MEAH+–water slope and ion interactions. This is an engineering expectation, not a calculated rank result. Report weighted physically scaled and column-normalized Jacobian singular values, coefficient correlations, conditional covariance when permitted, bound activity, cost per family/source/temperature, R2 δL0/δH and propagated ln K uncertainty. |column correlation|≥0.95 or an active bound limits identification claims as in Phase B. Do not invent a confidence interval at an active bound; no bootstrap/profile campaign is authorized.

Primary selection reuses Phase B's 1% simplicity rule within the only retained, fixed-energy branch: among eligible independent-R2 constant/slope forms, select constant if its cost is ≤1.01 times the branch minimum, otherwise slope. Use the lower-cost agreeing start; cost ties within relative 1e−6 prefer start 1. The secondary is the eligible free-R2 slope form, chosen within its two starts by the same rule. It can never replace the primary because of a high-T score. Fix both roles before assessment. This smaller menu retains the freeze/single-evaluation policy; it does not repeat Phase B's free-energy alternatives.

Before any new loaded T≥80 °C solve, export/reload, low-T rescore and **locally commit** the freeze: source PDF and data hashes, source coefficients/conversion/pressure declaration, source representation errors, full input/code/wheel hashes, all start outcomes, covariance/Jacobians, selected primary/secondary identities, assessment row IDs and exclusions. Source-only pure-water high-T arithmetic is explicitly permitted before this loaded-solution freeze. An observed high-T loaded score cannot change weights, bounds, source compression, starts, candidate laws, shortlist or roles. No additional fit or post-score refit follows a miss.

After freeze, run the existing ordered assessments once for each prespecified finalist, with unchanged `assessment-row-ids.json` and `never-accessed-vle-admission.csv`:

1. Canonical 80 °C pressure: **21** primary rows; **19** excluding the two historical Jou anchors as a separately labelled diagnostic.
2. All already admitted 80 °C species; retain Matin report-only quantities separately.
3. Wagner Table 6 rows 9–19, actual 352.81–352.86 K: **11** previously assessed rows, distinct from canonical rows.
4. Canonical 100–120 °C pressure: **57** rows; Wagner Table 6 rows 20–31 near 391.94–392.03 K: **12** rows, separately labelled outside domain.
5. Existing 15/45 wt% transfer sets: **33/37** rows, with unchanged concentration/loading conventions.
6. Existing finite-dose heat assessment: **113** intervals, retaining first-dose and endpoint approximations, source/run/isotherm grouping. Heat is excluded from estimation. Reuse adopted/Phase B/Stage 2 baseline results after the required low-T wheel replay; do not perform new adopted high-T solves.

Pressure metrics remain AARD=100 mean|pcalc/pobs−1|, RMS ln=sqrt(mean ln²(pcalc/pobs)) and mean ln=mean ln(pcalc/pobs), with matched source/temperature groups and complete denominators. Retain row values, signed residuals, numerical balances/stationarity, state failure causes and frozen hashes. Heat retains per-isotherm RMSE/bias. Six assessment jobs maximum, bundling candidates as before; no repeated scoring to choose a candidate. Record results and their physical limits in `analyses/mea_parameter_bundle/notebook.qmd` during authorized execution, then obtain independent delivered review. This design task does not update the notebook with nonexistent fit results.

## Pass condition, falsifier and interpretation

**Primary pass:** a numerically complete frozen independent-R2 primary must have canonical 21-row 80 °C AARD **≤20.270257%** (the unrounded adopted 20.27% benchmark), while its low-T pressure and species costs are each ≤1.10 times the adopted replay values, 8.14345313051485 and 24.848444130706277. Thus the limits are **8.95779844356634** and **27.33328854377691**. Both families must pass separately; a total-cost reduction cannot mask a loss in one family. Report the same condition for the secondary without promoting it to primary. Comparisons with Stage 2 costs and all other cohorts remain descriptive; no additional pass requirement is invented for Wagner or transfer.

**Numerical falsifier of the bounded hypothesis:** with admitted source conventions and successful representation/reference checks, a complete primary has 80 °C AARD>20.270257%, or exceeds either low-T family limit. Then independently fixing this R2 law does not suffice in the fixed SSM+DS model and current calibration design. If both routes miss completely, the two tested R2 treatments do not recover the missing response within their bounds. This does not rule out other chemical/activity laws or an independently constrained heat fit.

**Identification falsifier:** the secondary's equal-cost starts disagree in δH/δL0, its scaled Jacobian lacks independent reaction directions, an R2 bound is active, or the R2/slope columns have |correlation|≥0.95. Then a physical R2 enthalpy is not identified by this test, even if pressure passes. Report any pressure improvement as conditional mixture calibration. An unsupported source mapping, missing primary paper, failed state, unavailable wheel or budget exhaustion leaves the physical question unresolved; it is not a negative physical result. Leakage invalidates the exclusion claim, irrespective of scores.

A pass supports loaded-MEA 80 °C prediction conditional on independently sourced high-T aqueous chemistry, historical SSM+DS/model choices and the retained high-T binary-subsystem interactions. It is not untouched model-selection validation, independent identification of individual ion properties, concentration/stripper qualification or parameter adoption. Measurement/systematic uncertainty, source overlap, source-law compression, source pressure, active parameter bounds and model-form error remain distinct. R4/R5 chemical consistency remains UNRESOLVED. Scientific promotion and manuscript use stay with the investigator.

## Resource estimate and stop

Design used only reads, hashes, PDF inspection and scalar coefficient arithmetic. **Zero fits and zero equilibrium states were evaluated. CPU remains reserved for the other job.**

For later authorized execution: nproc=2; run one single-thread job at a time, with OMP/OPENBLAS/MKL=1 and no process pool, only after the reserved job releases CPU. Inspect host jobs once; wait on identified PIDs if needed. Keep native maximum_iterations=40, maximum_elapsed_time_seconds=2250, external `timeout 2400`; each low-T rescore/replay/assessment job has `timeout 1800`, each state ≤180 s. Source-only representation and scalar checks have `timeout 60`. Preserve native stopping tolerances; no hidden retries or budget extensions.

Stage 2 retained start times span 192.6–481.6 s; eight fits sum to 2590.2 s (43.2 one-core minutes including setup). Six new loaded fits are estimated at **30–60 one-core minutes**, with higher uncertainty for the seven-coordinate secondary. Representation is negligible (<1 minute). Replays, rescoring and up to two-finalist pressure/species/heat assessment are estimated at another **30–90 one-core minutes**; this is a planning estimate, not a measured speed claim. Total expected compute is roughly **1–2.5 one-core hours**. Hard external limits: six fits 4 h, two replay plus six rescore jobs 4 h, six assessment jobs 3 h, and one source job 1 min, at most **11 h 1 min** of capped single-core job time. Stop each job at its limit; an incomplete stage returns to the parent without using the unspent fit count for repairs.

Parent handoff: source import/admission and wheel qualification are open; independent readiness review has not occurred. No execution follows from this design comment. Stop after local commit and publication, leaving the clean feature worktree and all prior evidence intact.
