# Bounded R2 temperature test, issue 140, Stage 3

## Question, recommendation and authority

Can independent aqueous CO2 first-dissociation information replace R2's temperature law so that a 30 wt% MEA model estimated on loaded-solution data at ≤60 °C meets the adopted 80 °C pressure error, without degrading either low-temperature observation family by more than 10%? Compare this with estimating R2 enthalpy from the same low-temperature loaded-solution data.

**Recommend independent R2(T) as the primary test, conditional on source admission.** Keep free R2 enthalpy as a prespecified secondary diagnostic. Independent chemistry separates the standard-state temperature law from the activity model; freeing R2 and an interaction temperature coefficient with only two pressure isotherms may exchange their effects. A pressure improvement from the latter does not identify a physical R2 enthalpy. The available coefficient comparison suggests a modest source-law correction, so success is uncertain; do not enlarge it to recover the historical fitted shift.

This is the design requested by the [owner's Stage 2 decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/140#issuecomment-5927029509). The [following owner note](https://github.com/tannerpolley/Amine-Thermodynamics/issues/140#issuecomment-5927062016) confirms Engine heat support already exists. This bounded test retains pressure/species estimation only; heat remains an assessment quantity. Adding heat to estimation, changing the Engine without qualification, adopting parameters, or writing manuscript conclusions requires another owner decision.

Base: `329ac06f702685faaaea6854403def4b308c7e18`; worktree `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/downstream/.worktrees/Amine-Thermodynamics-140-reanchor`; branch `work/140-temperature-reanchor`. Issue body read on 2026-10-01, SHA-256 `3127ba66f28579ba023362d1f4e1e16808bb0ba61733cc300b57875a923a255c`. This file owns the bounded Stage 3 proposal; the issue comment links it. It is not an execution authorization. **No fit was run. The parent subsequently authorized only adopted/Stage 2 low-temperature wheel replays to resolve the readiness review at `d74b62e`; their numerical evidence is recorded below. Stop after the amendment commit and issue comment; the parent obtains a short independent re-review before fits.** The Edwards species convention remains a disclosed approximation, not a verified source finding.

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

The four requested pK1 sources are now readable in Zotero. The table records the live parent/attachment identities and exact PDF SHA-256 hashes inspected for this amendment. The main checkout's ignored `literature/` shelf is a reading copy; these Zotero PDFs own the evidence. `data/reference/MEA/manifests/source_status_manifest.csv` still has no R2/pure-water K1 row. This source admission does not add loaded-MEA data or assign measurement weights to compiled laws.

| Source / DOI | Zotero parent / PDF; SHA-256 | Admission and exact evidence |
|---|---|---|
| Plummer–Busenberg 1982, [10.1016/0016-7037(82)90056-4](https://doi.org/10.1016/0016-7037(82)90056-4), citation key `plummerSolubilitiesCalciteAragonite1982a` | `RWKJERFY/NJSUXCZL`; `ad957d246e8daf35e9173a57c723f1e5940dde7bf700bea790df9e530c5a51d6` | Primary law admitted: p. 1012 reactions 1–3/Eq. 5 define CO2(aq) as CO2⁰+H2CO3⁰ with water activity; pp. 1014–1015 source selection/regression, Eq. 13/Table 3 give molal K1 and the full five-term law. Low-T EMF and higher-T conductivity data are synthesized with judgement-based weights. Do not fit its carbonate-solubility observations here. |
| Patterson et al. 1982, [10.1016/0016-7037(82)90320-9](https://doi.org/10.1016/0016-7037(82)90320-9) | `RQWHJBGM/IU4XDR9K`; `b7e60a1c2f9410f13af6ee5f669e5b04a58a203b04d565bdccb5283a3049cacb` | Lineage/cross-check only. Discussion p. 1657 defines total un-ionized dissolved CO2, including H2CO3; finite-NaCl quotients need zero-ionic-strength inference and cannot enter by a molarity factor alone. |
| Millero et al. 2007, [10.1016/j.gca.2006.08.041](https://doi.org/10.1016/j.gca.2006.08.041) | `PZ8JE67Q/AF3YNWGZ`; `2f4c25a744de421abe292fecbdcfdb17477764bb366efd7962cf95b8fd28440e` | Cross-check/lineage only. pp. 47–48 describe the inherited Patterson 50–250 °C information; §3.1 and §4.3 combine prior pure-water/NaCl results. It is not an independent newer high-T campaign, and its NaCl scatter is not pure-water uncertainty. |
| Stefánsson–Bénézeth–Schott 2013, [10.1016/j.gca.2013.04.023](https://doi.org/10.1016/j.gca.2013.04.023) | `V7KQI67Z/G8RW297E`; `58738426749fbb9ed9f5e38384fdcef8999cb34740980a254b3b380a4820f604` | Independent cross-check, no new fitting weight. Methods pp. 600–605 use dilute solutions and simultaneous ionization/sodium-pair estimation. Table 2 p. 606 gives log10 K1 = −6.33 ± 0.03 at 80 °C, consistent with PB −6.33823. Reported constants follow water-vapour saturation pressure; this does not verify the concentrated-MEA activity model. |
| Edwards et al. 1978, [10.1002/aic.690240605](https://doi.org/10.1002/aic.690240605), `edwardsVaporliquidEquilibriaMulticomponent1978` | `Y27HTJXV/VV38QD9Q`, HTML abstract snapshot only | Austgen Table V reaction 4a explicitly inherits Edwards 1978. No full text exists in the accessible local library, so its CO2/H2CO3 convention and underlying row overlap remain **unverified**. The parent corrected the earlier claim of a PDF; use the bounded disclosed assumption below. Owner PDF import remains needed. |

Harned–Davis 1943 ([10.1021/ja01250a059](https://doi.org/10.1021/ja01250a059)) is optional historical reading, not an additional admitted row set. PB already uses its low-T measurements with Harned–Bonner refinements. Edwards predates PB/Patterson/Millero/Stefánsson, but overlap through older experiments remains unknown; independence here means independence from loaded MEA, not independence among all water correlations. Millero seawater formulations are excluded as direct replacements. No claim that PB is uniquely the current best law is made: it is the frozen, readable molal compilation consistent with the newer independent 80 °C cross-check.

**Hydration source and decision.** [Wang et al. 2010](https://doi.org/10.1021/jp909019u), pp. 1735–1737, Tables 1–2/Eq. 5, was read as a primary full paper via its accessible PDF mirror; page 1737 was visually checked. PDF SHA-256 is `6fa113319ec16706ced3c4464007fa19e4123e8e90e0d9f72589c73ab1743094`. It is not in Zotero; DOI **10.1021/jp909019u** needs owner import. Dilute stopped-flow experiments span 6.6–42.8 °C with ionic-activity corrections. Table 1 gives pseudo-first-order hydration ratio 0.0015 ± 0.0001 at 25 °C, with water held at 55.6 M; Table 2 gives hydration enthalpy 10 ± 2 kJ/mol. For the approximation check only, use the constant-enthalpy continuation and a rectangular envelope at twice the printed errors:

    r_h(T) = r_25 exp[H_h/R (1/298.15 − 1/T)],
    r_25 ∈ [0.0013, 0.0017], H_h ∈ [6, 14] kJ/mol,
    δ ln K = ln(1+r_h),
    δH = R T² d ln(1+r_h)/dT = H_h r_h/(1+r_h).

Analytic monotonicity and the retained 1 K grid in `stage-3/hydration-bound.csv` give maxima over 293–353.15 K: **r_h≤0.0040967021**, **ln(1+r_h)≤0.0040883334**, and **δH≤0.057119826 kJ/mol** (all maxima at 353.15 K). The maximum difference in K is 0.40967021%, below the parent-selected 0.5% limit; compare that with the 4.06063% PB/Austgen source-law difference at 80 °C. This is an engineering envelope conditional on constant hydration enthalpy and the paper's constant-water approximation, **not** a confidence interval or empirical bound above 42.8 °C; unknown curvature is not covered. Soli–Byrne 2002 ([10.1016/S0304-4203(02)00010-5](https://doi.org/10.1016/S0304-4203(02)00010-5)), absent Zotero, provides a lower hydration-ratio estimate but its 15–32.5 °C, 0.65 molal NaCl domain cannot itself establish the pure-water 80 °C bound; it is not the chosen bound source.

Under the parent's explicit rule (a), **adopt the combined CO2+H2CO3 pool convention for both inherited Austgen/Edwards and PB as a disclosed approximation**. PB's pool definition is verified; Edwards' is assumed pending full text. No hydration correction is applied to either law in this bounded design. If future full text establishes different conventions, or independent hydration evidence exceeds 0.5% within the interval, stop before fits and amend: molecular-CO2 input requires `ln K1,CO2 = ln K1,* + ln(1+r_h(T))` and the corresponding δH above. The present bound limits standard-state sensitivity; it does not bound nonlinear pressure response or prove that a near-threshold pass could never change.

## Reaction equations and basis

**S3-E1 — aqueous reaction quotient.** R2 is CO2(aq)+2H2O ⇌ HCO3−+H3O+. Solute activities are a_i^m=gamma_i^m m_i/m°, m°=1 mol/kg water, gamma_i^m→1 in aqueous infinite dilution; a_w is Raoult-normalized. Define the hydrated proton by mu_H+=mu_H3O+−mu_H2O and a_H+=a_H3O+/a_w. Then

    K2_m = a_HCO3^m a_H3O^m / (a_CO2^m a_w²)
         = a_HCO3^m a_H+^m / (a_CO2^m a_w).

Only in the pure-water infinite-dilution limit does a_w→1 permit direct use of K1=a_H+ a_HCO3/a_CO2. Do not delete water factors at loaded composition. This is the same hydrated-proton interpretation used in Stage 2; verify the Engine's reaction reference uses it. Literature K1 for dissolved CO2 is neither gas Henry's law nor the true H2CO3 dissociation constant near pKa≈3.6. If a source denominator is CO2*=CO2(aq)+H2CO3, K1_CO2=K1_star(1+r_h), r_h=m_H2CO3/m_CO2 at infinite dilution. PB explicitly uses the combined pool. The parent-authorized approximation above maps that pool onto the Engine neutral CO2 component for both laws without adding a hydration reaction; its size and unresolved Edwards convention are disclosed.

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

**S3-E4 — independent candidate law.** Plummer–Busenberg Eq. 13/Table 3, p. 1015, verified against its Zotero PDF, gives, with T in K,

    log10 K1 = −356.3094 − 0.06091964 T + 21834.37/T
               + 126.8339 log10(T/1 K) − 1684915/T².

Only direct coefficient arithmetic was performed here; the following is a source-correlation comparison under the disclosed common-pool approximation, not physical validation or a newly fitted result.

| T / °C | Austgen molal pK1 | Candidate pK1 | ln(K_candidate/K_Austgen) |
|---|---:|---:|---:|
| 20 | 6.389330 | 6.381871 | +0.017175 |
| 25 | 6.359066 | 6.351864 | +0.016583 |
| 40 | 6.299458 | 6.297395 | +0.004749 |
| 60 | 6.281664 | 6.290305 | −0.019895 |
| 80 | 6.320228 | 6.338232 | −0.041454 |

At 80 °C this is K_candidate/K_Austgen=0.959394. The enthalpy from ΔHr°=RT² d(ln K)/dT is **Austgen −7.46075 kJ/mol** and **Plummer–Busenberg −8.36814 kJ/mol** at 80 °C. Those differences are small relative to the magnitude of the inherited fitted correction; they are not uncertainty-normalized differences. At fixed aqueous activities a decrease in K tends to raise the molecular CO2 required by the quotient, but coupled pressure/speciation need not change by the same percentage. A 4.1% K change alone is not evidence that a 29% pressure error will reach 20%.

For scale, the historical −8.2018845 kJ/mol correction preserving the 40 °C anchor changes ln K at 80 °C by −0.356802451, a K ratio of 0.699910751 (30.0089% decrease). It remains excluded from starts and priors. PB’s compilation weights and source overlap are distinct from the newer cross-check uncertainty; none provides a measurement covariance for this representation fit. Edwards’ unverified pool convention remains the explicit source limitation.

## Seven-fit maximum and frozen estimation method

R1/R3, SSM+DS Born/dielectric/association choices, ions and binary interactions remain as disclosed in Phase B. Keep source CO2 dispersion 169.21 K fixed in both tests. Its historical 173.44025 K selection included 80 °C; the independent constant-energy-free branch is not repeated. Keep Stage 2 R4/R5 fixed, diagnostic. No density, Cp, loaded heat, fitted reaction curvature, additional interaction slope, folds, bootstrap or optimization profile enters loaded-solution estimation.

**Source representation, one fit maximum.** Both inspected `28181e72` and `9e6a76cf` wheels support `ReactionLogPolynomial` with A+B/T+C ln(T/Tref)+DT, not E/T². Do not discard the last term or write generic Engine chemistry. After source admission, make one source-only linear least-squares representation of S3-E4 on the eleven predetermined temperatures 273.15+10j K, j=0,…,10. Fit

    L0 + B(1/T−1/T0) + C ln(T/T0) + D(T−T0), T0=313.15 K.

Use equal numerical representation weights, scaled columns and NumPy `linalg.lstsq`, reusing the Stage 2 source-estimation owner; these eleven correlation samples are not eleven new measurements. Full source coefficients determine every sample. Pin **reference_temperature=T0=313.15 K**. There are two distinct serialization mappings:

    Direct native input: a_native=L0−B/T0−D T0; b=B, c=C, d=D.
    Stored document through shared_evaluation.py:380:
        A=L0−B/T0−D T0−C ln(T0/1 K); B=B, C=C, D=D.

The adapter adds C ln(T0/1 K) to stored A before creating native a. On export, use **A=a_native−C ln(T0/1 K)** and **L0=a_native+B/T0+D T0**; never write a_native into stored A. Reuse the existing source/native algebra checks at absolute |δ ln K|<5e−13 at 293.15/313.15/333.15/353.15 K, and the existing full-precision parameter export/reload/rescore checks. Compare direct native and adapter-created laws and RT² derivatives before fitting; a serialization mismatch stops admission. Check a 1 K grid over 293.15–353.15 K plus every actual assessment temperature after freezing the coefficients. Required representation error on the candidate interval: |δ ln K|≤1e−3 and |δΔHr°|≤0.10 kJ/mol. These are engineering approximation limits, not source uncertainties. Rank deficiency or exceeding either limit stops this design; no different grid, weights, fifth coefficient or new source fit is authorized. Outside-domain errors are reported, never used to reselect coefficients. The law keeps source-derived curvature; no A+B/T-only extrapolation is substituted. Representation covariance is not chemical measurement covariance.

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

Use Engine `epcsaft.regression.fit`, native reaction-coordinate first derivatives and the existing low-temperature fit/assessment owners. No local optimizer, finite-difference reaction fitter, generic equation copy or new dependency. Approved executable addition ceiling: 350 lines relative to `329ac06`, for source mapping and reuse of current owners; exceeding it returns to Design. No source law is fitted to loaded pressure in the primary route.

## Wheel admission and numerical completeness

The Phase B/Stage 2 immutable wheel is `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/fit-audit-20260929/candidate-28181e72/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl`, SHA-256 `28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`. Archive inspection confirms the four-term reaction law but **no native `reaction_coordinate` or `addition_enthalpy` regression interface**. Stage 3’s free R2 a/b route requires native reaction coordinates; the old wheel therefore cannot serve the whole registered test. The existing separate heat endpoint assessment does not itself require heat regression. Engine [#187](https://github.com/tannerpolley/ePC-SAFT/issues/187), [#211](https://github.com/tannerpolley/ePC-SAFT/issues/211) and [#210](https://github.com/tannerpolley/ePC-SAFT/issues/210) provide the already implemented capabilities; no new generic Engine work is proposed.

**Bind both loaded routes to this actual immutable wheel:**

    /home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/fit-audit-20261001/candidate-9e6a76cf/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl
    SHA-256: 9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4

The first design named `62c2f9078579f300c5e1dc5ae0814223b021a3b5e0a921d331cb6b63a58fbaf5` from the owner-reported #210 verification. That is the older wheel recorded in Engine `analyses/2026-addition-enthalpy-fitting/results/summary.json`, base `3f5ee19f`; it was never installed for Stage 3. The current environment-wheel preparation records **9e6a76cf**, build fingerprint `18483e74957c5a9e6bb6e1b64f610e0c9da32fb8bd18b51357206e5d29786a6d`. Engine’s subsequent trace-solvent-activity verification also records 9e6a76cf, source base `502e8099051c00bf169198c970f3525bbcfac7fd`. Thus the discrepancy was a proposal based on an older verification wheel versus the actual later environment wheel, not a hash alias. The wheel hash is authoritative; do not infer a precise source commit from the current checkout or reuse the old downstream `ENGINE_COMMIT` value as its build identity.

The existing `build/environment-wheel` was copied byte-for-byte to the immutable path above, hash-checked, and installed normally with `uv pip install` into a separate environment at `results/runs/temperature-reanchor-140/stage-3-wheel-replay/.venv`. **No `direct_url.json` or `RECORD` was edited**, and the old worktree environment was left intact. The installed module originates inside this isolated environment; all 18 hashed installed RECORD entries matched their actual bytes and declared sizes. No Engine source checkout is imported. For subsequent Stage 3 execution, explicitly use this environment and set the scoped wheel pin before importing the existing `probe`/fit owners, as the replay driver does; the global shared-evaluation default still belongs to the historical wheel.

**Parent-authorized wheel qualification, no fits.** Reused `phase-a.training`, the shared evaluator, existing residual owner and Stage 2 fixed-source context; used separate empty record caches. `stage-3-wheel-replay.py` rejects T>333.15 K and fitting is never called. Each record replayed all 84 states / 142 targets (48 pressure, 94 species), with single-thread caps and external `timeout 1800`.

| Replay on 9e6a76cf | Pressure cost | Species cost | Total cost | Largest absolute family/total cost difference from retained row sums |
|---|---:|---:|---:|---:|
| Adopted | 8.143453130514850 | 24.848444130706277 | 32.991897261221126 | 0 |
| Stage 2 primary | 8.218958638682464 | 24.625178978786007 | 32.844137617468470 | 1.31×10⁻¹² |

All cost differences pass **≤1e−8**. The Stage 2 total differs from its retained native-fit summary 32.84413761745968 by 8.79×10⁻¹², also passing; the small row-sum/native-summary distinction is not a chemistry change. Every prediction passes relative **1e−8**, with species absolute floor **1e−12**; maximum used fraction of that allowed prediction difference is 0 for adopted and 9.5572×10⁻⁵ for Stage 2. All states met the requested Engine tolerance, no material/charge balance violation above the existing 1e−7 limits was reported, and maximum stationarity was **3.9791×10⁻¹³ / 1.2222×10⁻¹²**, both ≤1e−10. Measured wall times were 22.916 / 21.990 s. Exact record/packet/script/reference hashes, row predictions and costs are retained in `stage-3/{adopted,stage-2}-wheel-replay.{csv,json}` and summarized in the research notebook. These are numerical replay checks, not physical validation or Stage 3 prediction results. The wheel replay gate is satisfied; source/serialization disclosure and the amended design still go to the parent's independent re-review before fitting. A future wheel change requires repeating this qualification before any fit.

Every loaded start must converge with all 142 finite predictions/residuals/Jacobian rows, then export/reload/rescore all training targets. Requested Engine tolerance must be met, material/charge balance errors ≤1e−7 and maximum stationarity ≤1e−10. Check k(T)<1 at fitting endpoints and after freeze at assessment endpoints. A missing solve, time limit, failed native reference conversion or nonfinite Jacobian is incompleteness, not a physical falsifier. Keep failures; no available-row-only scoring, penalties replacing rows or silent retries.

Use the Phase B two-start agreement limits: relative cost 1e−6, intercepts absolute 1e−5, interaction slope 0.1 K. For secondary R2 also require |δL0 difference|≤1e−4 and |δH difference|≤0.01 kJ/mol. Equal costs with differing parameters mean nonidentification. Both starts must satisfy agreement/completeness for an eligible finalist; an incomplete route has no finalist.

## Identifiability, selection, freeze and one assessment

Two pressure isotherms can constrain a slope when other effects are fixed; identifiability is not mathematically impossible solely because there are two. Pressure here has only 40/60 °C isotherms with seven competing coordinates in the secondary; the 20–60 °C species targets add chemical sensitivity but do not guarantee separation of R2 a/b, MEAH+–water slope and ion interactions. This is an engineering expectation, not a calculated rank result. Report weighted physically scaled and column-normalized Jacobian singular values, coefficient correlations, conditional covariance when permitted, bound activity, cost per family/source/temperature, R2 δL0/δH and propagated ln K uncertainty. |column correlation|≥0.95 or an active bound limits identification claims as in Phase B. Do not invent a confidence interval at an active bound; no bootstrap/profile campaign is authorized.

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

The amendment used source reads, hashes, scalar hydration arithmetic and the two explicitly authorized low-T wheel replays: **zero fits, 168 equilibrium states, 284 target comparisons, and zero loaded ≥80 °C evaluations**. The two reserved fitting PIDs had exited before either single-thread replay began. No Stage 3 source representation or loaded fit has been run.

For later authorized execution: nproc=2; run one single-thread job at a time, with OMP/OPENBLAS/MKL=1 and no process pool, only after the reserved job releases CPU. Inspect host jobs once; wait on identified PIDs if needed. Keep native maximum_iterations=40, maximum_elapsed_time_seconds=2250, external `timeout 2400`; each low-T rescore/replay/assessment job has `timeout 1800`, each state ≤180 s. Source-only representation and scalar checks have `timeout 60`. Preserve native stopping tolerances; no hidden retries or budget extensions.

Stage 2 retained start times span 192.6–481.6 s; eight fits sum to 2590.2 s (43.2 one-core minutes including setup). Six new loaded fits are estimated at **30–60 one-core minutes**, with higher uncertainty for the seven-coordinate secondary. Representation is negligible (<1 minute). Replays, rescoring and up to two-finalist pressure/species/heat assessment are estimated at another **30–90 one-core minutes**; this is a planning estimate, not a measured speed claim. Total expected compute is roughly **1–2.5 one-core hours**. Hard external limits: six fits 4 h, two replay plus six rescore jobs 4 h, six assessment jobs 3 h, and one source job 1 min, at most **11 h 1 min** of capped single-core job time. Stop each job at its limit; an incomplete stage returns to the parent without using the unspent fit count for repairs.

Parent handoff: the full readiness review at `d74b62e` returned **Block for fits**. This amendment resolves the serialization and actual-wheel/replay findings, updates source availability/ancestry, and applies the parent-selected small-hydration approximation with Edwards explicitly unverified. Edwards PDF and Wang hydration-paper Zotero import remain source-access limitations, not concealed evidence. The parent obtains a short re-review of this amendment; **no fits follow from this comment**. Stop after local commit/publication, leaving the feature worktree clean and prior evidence intact.

## Execution amendment log, 2026-10-01

The scoped independent re-review returned **READY at `129f19e`** (thread `mea140-stage3-rereview-1`); the parent then explicitly authorized Stage 3 execution. The parent's subsequent approval increases only the executable addition ceiling from 200 to **350 lines**, retaining all seven-fit, input, numerical-tolerance, freeze and assessment limits. Measured before any source or loaded fit: `git diff --numstat 329ac06 -- '*.py'` gives **342 added lines, 10 removed, net 332**: assessment 9/1, loaded-fit owner 27/7, phase-a verification 2/2, R2 driver 179/0, CPU-gated campaign command 36/0 and retained replay driver 89/0. This conservative count includes comments and blank lines. No optimizer, generic equation implementation or dependency was added. The existing fit owner now creates Engine reaction coordinates, converts native a back to stored A on export, and rescoring uses the final chemistry. The source driver uses the existing linear least-squares method; the assessment owner retains 1% selection with fixed primary/secondary roles and transformed R2 two-start limits. Source-law representation runs first, then the four primary starts, then the two secondary starts; every complete native fit receives one export/reload rescore.

The host-wide limit is two concurrent single-thread jobs. Before each calculation launch inspect `ps -eo pid,args` for numerical workers, excluding their parent/shell commands; if both slots are occupied, wait on one identified worker PID with `while kill -0 <pid>; do sleep 60; done`, then inspect before launching. No process-name polling, job overlap within Stage 3, unregistered retry or budget extension is allowed. The original resource timeouts and OMP/OPENBLAS/MKL=1 remain. A committed freeze is checked from Git before any loaded ≥80 °C scoring. Numerical incompleteness remains excluded from ranking. The earlier design-stop paragraphs record the chronology; this explicit owner-authorized execution amendment supersedes that stop for this campaign only.
