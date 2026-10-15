# Carbonate diagnosis for the initial ions-first stage 4

**Classification: a confirmed 022 source-feed inconsistency, a source-reliability limitation for the separate 022 carbonate target, and a real mismatch between the 011 observations and the declared source-chemistry/seed-ion calculation. No single trace-interaction defect is established.** The 011 carbonate share of its common NMR peak is 75%, so the source's 10% warning does not reject that carbonate measurement. Replacing both species by their pool does not remove the 011 discrepancy. The earlier adopted model can approach both carbonate ratios with different ion/interactions/chemistry; the evidence does not establish an unavoidable model-form conflict or unique ion properties.

This is `cse:diagnose` Explore work for #170. The endpoint is an evidence-backed causal distinction for the parent. No fit, production-code edit, design/target change, parameter selection, notebook promotion, push, merge, GitHub write, subagent or preview-service action occurred. Inert `.py.txt` scripts reproduce the probes explicitly; they are not imported by production. Independent review and any design amendment remain with the parent.

## 1. States, observations and model values

All evaluations use a homogeneous reacting liquid at 101325 Pa and the pinned cf26a17b wheel. The nine declared states and 26 targets use difference scales `0.1*y_obs + 0.001`, weight 1/26 and cost `0.5*sum(weight*residual**2)`. The recorded iteration-40 vector is a nonconverged, bound-active vector, used here only for diagnosis.

Table A2, printed p.9902/PDF p.9, gives 011 at 293.15 K, `maxload=loadNMR=0.29`, and 022 at 313.15 K, `maxload=0.60`, `loadNMR=0.59`. Both are from the nominal 30 wt% batch. In #184's `proposed-states.csv`, data rows 11 and 22 both have model CO2-free MEA mass fraction **0.2714274817259226**: 256.34 g MEA, 598.22 g H2O and approximately 99.891111 g D2O, with D2O replaced mole-for-mole by H2O and dioxane omitted; the model water equivalent is 688.074318 g. The approximate 10% dilution, ignored isotope/dioxane effects and inferred `loadNMR` interpretation remain engineering assumptions (Table 2 and preparation, pp.9896-9897).

The *executed declaration* instead uses **0.11583721405835971** for 022. Its neutral feed is `(CO2,MEA,H2O)=(0.59,1,25.878992563232906)` mol; 011 uses `(0.29,1,9.100855238251219)` mol. Applying the accepted mass-fraction transformation with Engine species molar masses gives the corrected 022 water amount 9.100855238251219 mol per mol MEA, matching declared 011. The original #184 source-batch moles use their stated source molar masses; this evaluation preserves the existing Engine feed conversion. The 11.5837 wt% number belongs to the source's *15 wt% batch* and conflicts with Table A2 and #184. This error is already present in design line 162 and is faithfully propagated to stage-4 rows/requests; it is not an Engine equation failure. Correcting it needs parent resolution of that source/design inconsistency.

Ratios below use total amine `MEA + MEAH+ + carbamate`; printed amine sums are 0.1099 at 011 and 0.1132 at 022. Free MEA is shown for completeness, not added to the objective. CO2 is blank in both source rows and supplies no observed ratio. The derived `MEA+MEAH+` ratio is 0.7206551410 / 0.5636042403, respectively, and supplies no additional observation.

| State | Species | Printed fraction | Observed ratio | A start | A iteration 40 |
| --- | --- | --- | --- | --- | --- |
| 011 | MEA | 0.0556 | 0.5059144677 | 0.4341260468 | 0.4225512799 |
| 011 | MEAH^+ | 0.0236 | 0.2147406733 | 0.3676314734 | 0.2953712996 |
| 011 | MEACOO^- | 0.0307 | 0.279344859 | 0.1982424797 | 0.2820774205 |
| 011 | HCO3^- | 0.0002 | 0.001819836215 | 0.01414710537 | 0.002573894371 |
| 011 | CO3^2- | 0.0006 | 0.005459508644 | 0.07760960322 | 0.005348390877 |
| 022 | MEA | 0.0028 | 0.02473498233 | 0.070773203 | 0.0331156536 |
| 022 | MEAH^+ | 0.061 | 0.538869258 | 0.6273408054 | 0.5958648469 |
| 022 | MEACOO^- | 0.0494 | 0.4363957597 | 0.3018859916 | 0.3710194995 |
| 022 | HCO3^- | 0.0151 | 0.1333922261 | 0.2489380165 | 0.2078367298 |
| 022 | CO3^2- | 0.0009 | 0.007950530035 | 0.03825504139 | 0.008502779015 |

The observed carbonate shares of `HCO3- + CO3^2-` are **75% at 011** and **5.625% at 022**. Only 022 is below 10%. Starting modeled shares are 84.58194% / 13.32032%; iteration-40 shares are 67.51071% / 3.930294%. The source warning concerns the fraction within a proton-exchanging pair, not an absolute mole fraction or carbonate divided by total dissolved carbon. At 011 even bicarbonate is 25% of that pool. At 022 the carbonate warning applies by its measured 5.625% share even though `loadNMR=0.59` is just below the separate “>0.6” loading warning.

The source ratios imply charge differences `(MEAH-carbamate-HCO3-2*CO3)/total_amine` of **-0.07734303913** / **-0.04681978799** before unreported H3O+/OH-. They are not silently repaired. These printed-row balance discrepancies further limit simultaneous exact reproduction; they are not new measured trace-ion concentrations.

PDF verification: live Zotero parent `VDRXENRB`, PDF `XVFDEJM2`, Markdown `SIZRW28I`; hashes and inspected passages are in `source-provenance.json`. The PDF confirms the fast-exchange common peak and chemical-shift calibration (p.9895, Calibration Experiments; p.9896, Figure 2 discussion). Printed p.9900 says “Fractions <10% cannot be evaluated with reasonable accuracy.” It also says “the concentration of carbonate is most likely overpredicted.” That latter sentence refers to the experimentally inferred carbonate split, not this Engine prediction; reducing the observed carbonate would increase the present model/observation ratio. The loading >0.6 warning is on p.9901. The relevant preparation, uncertainty, balance and model-comparison passages and Table A2 were read. This diagnosis makes no new literature-based claim about R4/R5 validity or general fitting practice.

## 2. Governing reaction, reference basis and one-input evaluations

The declaration's R3 is `HCO3- + H2O = CO3^2- + H3O+` and R5 is `MEAH+ + H2O = MEA + H3O+` (Jakobsen's displayed reactions (4) and (5), p.9895, identify the chemical reactions; the numerical correlations here are the accepted MEA input records). Subtracting R5 eliminates water and hydronium:

$$
\ln\frac{x_{CO_3}}{x_{HCO_3}}=(\ln K_3^{EOS}-\ln K_5^{EOS})+\ln\frac{x_{MEA}}{x_{MEAH}}+\ln\phi_{MEA}+\ln\phi_{HCO_3}-\ln\phi_{MEAH}-\ln\phi_{CO_3}.
$$

Here the Engine basis is `a_i=x_i*phi_i`; all log fugacity coefficients are retained directly from the installed Engine state. Both reactions have zero total stoichiometric mole change, so a common pressure factor cancels. At 011 the source R3 log constant is **-27.9197766601** on raw mole-fraction infinite-dilution basis; R5 is **-22.2135639200** on common aqueous-molality basis, or **-26.2300989123** after the declared -4.0165349923 source-scale conversion. Native neutral-reference contractions then give **ln K3(EOS)=-1029.5626724127**, **ln K5(EOS)=-325.9104025521**. These large EOS numbers include Born/reference contributions and must not be compared with source log constants without conversion.

| 011 term | Value |
| --- | --- |
| ln K3(EOS) - ln K5(EOS) | -703.6522699 |
| Activity-coefficient combination | 705.1881971 |
| ln(x_MEA/x_MEAH) | 0.1662539169 |
| Sum = ln(x_CO3/x_HCO3) | 1.702181137 |
| x_CO3/x_HCO3 | 5.48589985 |
| Observed CO3/HCO3 | 3 |

Direct R3 decomposition is `-1029.562672413 + 1006.047510079 + 25.217343471 = 1.702181137`, where the last term is `ln(x_H2O/x_H3O)`. The native equation residuals and the combined identity are checked to 2e-9 or better. R2 conversion is outside this carbonate decomposition and is deliberately unreported in `native_lnK`; an initial check showed that the abbreviated conversion does not close for R2, which is not used in this carbonate identity. The final checks cover R1/R3/R4/R5 only.

| Species | ln phi at 011 (native EOS) | ln gamma_x at 011 | ln gamma_x at declared 022 |
| --- | --- | --- | --- |
| carbonate-anion | -736.8290525 | -3.81335 | -3.35880 |
| bicarbonate-anion | -171.6590716 | -1.71988 | -1.07631 |
| protonated-monoethanolamine | -148.5088241 | -1.03256 | -0.74469 |
| monoethanolamine | -8.490607825 | 0.09958 | -0.07145 |
| hydronium-cation | -444.6296262 | -2.29310 | -1.18430 |
| hydroxide-anion | -181.8734502 | -0.21572 | -0.64843 |
| water | -3.752096936 | 0.01804 | 0.00976 |

`gamma_x` uses the unsymmetric infinite-dilution-in-water mole-fraction scale at 100000 Pa: `ln gamma_x = ln phi(state) - ln phi(infinite dilution) + ln(P/100000)`. The Engine neutral-salt references stop at molality 1e-12, with reported terminal errors up to 7.53e-5; these single-ion values are therefore printed to five decimals as diagnostic values, not independently measurable single-ion properties. The exact reaction combination above uses native contractions rather than these approximate individual limiting coefficients. MEA/water use a neutral MEA insertion of mole fraction 1e-12. Conversion to molality-scale solute gamma adds `ln(x_water)`; it cancels in R3-minus-R5.

At 011 the pool/amine excess factor is **12.605077842** and the carbonate share factor is **1.127759186**. Their product is **14.215492323**. Thus the 14-fold carbonate excess mainly arises from too much inorganic-carbon pool, rather than a 14-fold error in splitting a correctly predicted pool. R4 hydrolysis and R5 protonation/activity compensation are plausible causes of pool movement; the specified changes below quantify this conditional sensitivity without identifying one physical cause.

| Evaluation | 011 carbonate/amine | 022 carbonate/amine | 011 carbonate cost | 022 carbonate cost | 26-target total cost |
| --- | --- | --- | --- | --- | --- |
| A-start | 0.07760960322 | 0.03825504139 | 41.88698419 | 5.480960524 | 59.17684172 |
| carbonate-water-kij-zero | 0.1207801374 | 0.04438814649 | 107.0087489 | 7.923955413 | 132.9675599 |
| hydronium-hydroxide-water-kij-zero | 0.07761224659 | 0.03825490641 | 41.89005349 | 5.480911699 | 59.1809112 |
| R4-a-minus-0.2 | 0.0661785878 | 0.03258336353 | 29.66577077 | 3.62135287 | 42.44130487 |
| R4-a-plus-0.2 | 0.09007266462 | 0.04465127395 | 57.60777101 | 8.038811362 | 80.56998364 |
| R5-ak-minus-80K | 0.04432860344 | 0.02176886061 | 12.15665626 | 1.139602147 | 21.81609857 |
| carbonate-born-1.05A | 0.2461100304 | 0.1130278199 | 465.9924696 | 65.89611773 | 579.054864 |
| carbonate-born-4.5A | 0.06070628228 | 0.03178636186 | 24.55947761 | 3.390804321 | 36.62685418 |
| carbonate-born-7.5A | 0.05011545899 | 0.02743708547 | 16.04589537 | 2.266273172 | 25.79597441 |
| A-iteration-40 | 0.005348390877 | 0.008502779015 | 9.935101137e-05 | 0.001820169976 | 1.360975044 |
| 022-feed-27.1427wtpct-evaluation | 0.07760960322 | 0.09147011177 | 41.88698419 | 41.63118034 | 95.55411174 |
| historical-adopted-parameters-current-declared-feeds | 0.005026550523 | 0.0101739833 | 0.001508332412 | 0.02950516949 | 1.605894116 |

All perturbations change one declared input group at a time from A; the final two historical/adopted rows explicitly change complete records or one feed and are comparisons. `sensitivity-summary.csv` also supplies both complete state costs. All 26 prediction statuses are Available, all requested native tolerances pass, and all 9 states in each of 12 variants have retained native residual/closure evidence in `states.json`; there were zero unavailable target evaluations.

For these specified perturbation sizes, carbonate-water interaction strongly affects the result, but changing -0.25 to zero **worsens** 011 and the total cost. It is not identified as a mistaken input. The hydronium/hydroxide water interactions are negligible here (total change +0.00406948). R4 a ±0.2 changes the total by -16.7355/+21.3931, and R5 a_k -80 K changes it by -37.3607. Carbonate Born assumptions can also cause large movement. These finite changes use different units and magnitudes; they are not an invariant parameter-importance ranking or uncertainty analysis. R5/ion compensation remains consistent with the prior exact sensitivity cosine 0.98924.

No distinct complete carbonate size/Born parameter record was found among retained bundle `*parameters.json` files: the record remains m=1, sigma=2.4422 A, packing/Debye-Huckel diameter=2.149136 A, epsilon/k=249.26 K, Born=3 A. Records without Born represent a changed physical formulation and are not an alternative Born diameter. The older trace-ion scan does retain carbonate Born seeds **1.05, 4.5 and 7.5 A** in `trace_carbonate_born_multistart_attempts.csv` (paired there with HCO3 Born seeds 1.05, 4.5 and 6.5 A). All three carbonate-only substitutions were evaluated above, leaving bicarbonate unchanged as requested. These are historical seed alternatives, not adopted or independently fitted carbonate records. Its actual current summary gives selected values 3/3 A and says the optimizer loop was skipped; the parameter evidence CSV’s older 2.9998 A “fit” wording is not supported by that retained summary.

The separate source-consistent 022 feed probe raises its carbonate/amine from 0.03825504 to 0.09147011, carbonate cost from 5.48096 to 41.63118, and the total from 59.17684 to 95.55411. Correcting this input does not remove 011’s mismatch and makes the source-chemistry comparison worse at 022. It remains required source reconciliation, not a remedy selected to lower cost.

## 3. Retained history and the adopted record

`heat-final-170/evaluation/jakobsen-carbonate-share.csv` uses carbonate / **total dissolved carbon** (CO2 + carbamate + bicarbonate + carbonate), as implemented in `calibration-misfit/compare.py:92-110`. It does not contain the HCO3/CO3 peak-pool share. At 20 C, loading 0.29, observed total-carbon share is 0.01904761905. Retained values are:

| Heat-final comparison | Predicted total-carbon share | Predicted/observed |
| --- | --- | --- |
| F1 | 0.014983944256390247 | 0.786657073460488 |
| F2 | 0.029176663256373907 | 1.5317748209596302 |
| F6 | 0.02194236600157749 | 1.1519742150828183 |
| F1-no-heat | 0.013217787471066597 | 0.6939338422309964 |

These are nominal-30 wt% interpolated model comparisons, with maxload and the original unresolved feed assumptions explicitly disclosed in their CSV. The comparison selects loading <=0.5 and has **no 022/0.60 entry**. Earlier final-rerun and density-cp-160 comparisons are retained in `historical-share-comparisons.json`; they share the same total-carbon definition and cannot establish the corrected state agreement.

The historical ion fit at `897bb6e` did not reproduce 011 carbonate: its final mole fraction was **0.003496298909** against **0.000594982353** on its old transformed basis (5.876-fold). At the 022-like 40 C/0.60 case it gave **0.000576584044** against **0.000897761299** (0.642-fold). A final state failed for a different Böttinger state, so the historical fit was not a complete passing calibration. The seven fitted ion/mutual values are the design B starts at lines 179-185; the corresponding historical rows and exact commit/path are retained here. The later trace-ion scan also gives 011 carbonate **0.005548329547 / 0.000594982353** and 022-like carbonate **0.001118664907 / 0.000897761299**; those rows are converged but retain earlier nominal feeds and are not new validation.

The previously adopted heat-fitted F1 record uses MEAH `(sigma,epsilon/k,Born)=(3.48508556586 A,232.687201645 K,3.53322927146 A)` and carbamate `(3.53543525721 A,453.265244384 K,3.54107030822 A)`. Packing and Debye-Huckel diameters equal 0.88*sigma. Its carbonate/trace records match the present precursor: carbonate `(sigma,epsilon/k,Born)=(2.4422 A,249.26 K,3 A)`, bicarbonate `(2.9296 A,70 K,3 A)`, hydronium `(3.4654 A,500 K,1.218 A)` and hydroxide `(2.0177 A,650 K,3.08107689400404 A)`; carbonate-water=-0.25, hydronium-water=+0.25 and hydroxide-water=-0.25.

It also has fitted carbamate-water **+0.22395029736**, MEAH-water **-0.31245311346**, MEAH-water reciprocal-temperature slope **+107.963956737 K**, bicarbonate-water **+0.5**, mutual **-0.968286748826**, R5 `(a_k,b,c)=(3037.63995347 K,-1.01731508373,0.0004277/K)` and shifted R2 `(a,b_k)=(232.331415339,-11105.6400305 K)`; R4 remains `(2.151,-1545.3 K)`. Full precision for both F1 and the byte-pinned adopted document is in `historical-and-current-parameter-values.json`. These differences prevent crediting the carbonate agreement to a different trace-ion record.

Evaluating that adopted parameter document on this pinned wheel gives carbonate/amine **0.005026550523 at 011** and **0.010173983300 at declared 11.5837 wt% 022**. On the source-consistent **27.1427 wt% 022** feed the latter becomes **0.008242378194**, versus **0.007950530035** observed (about +3.67%); 011 is about -7.93%. These are new conditional evaluations of a reused fitted model, not retained historical exact-state calculations or independent physical validation. Other targets remain discrepant: at corrected 022 its bicarbonate ratio is 0.19579964 versus 0.13339223.

## 4. Target definition and pool evaluation only

Design section 4 line 155 explicitly says **“MEAH⁺, carbamate, bicarbonate and carbonate, four per state, expressed as species/total-amine ratios”**. Line 156 separately prescribes the Matin “bicarbonate/carbonate pool,” while line 173 fixes 26 targets and weight 1/26. Thus no Jakobsen pool substitution is currently authorized. The ions-first amendment's section 1 explicitly keeps all of section 4.

Evaluation only: replace each Jakobsen HCO3/CO3 pair by its sum, preserve the amine denominator, and set its difference scale to `0.1*(observed HCO3+CO3 ratio)+0.001`. This leaves 24 scalar targets. Keep 1/26 first for a paired cost comparison, and report 1/24 separately to show the effect of normalization:

| State | Observed pool/amine | Predicted pool/amine | Pool cost, weight 1/26 | Whole state cost, weight 1/26 |
| --- | --- | --- | --- | --- |
| 011 | 0.007279344859 | 0.09175670858 | 45.96452925 | 47.00563036 |
| 022 | 0.1413427562 | 0.2871930579 | 1.786027092 | 2.010600133 |

Starting total: **56.21902702576** at preserved 1/26, versus **59.17684171981** originally. Normalizing all 24 weights to 1/24 gives **60.90394594457**; the two pool contributions become 49.794906686 / 1.934862683, and whole-state contributions 50.922766221 / 2.178150144. The 011 pool discrepancy survives and its pooled contribution exceeds its original carbonate-only contribution. No production declaration was changed.

## 5. Options for the parent, without selecting one

- Reconcile the 022 feed with Table A2/#184 and design line 162 before another fit. This changes one state input, preserves 9 states/26 targets if targets stay separate, and requires corrected starting evaluations and consistent later stage-3/comparison feeds. The evaluated source correction increases the mismatch; it cannot be represented as a cost-improving correction.
- Keep separate Jakobsen targets after that reconciliation. The declared stage 4 still needs an eligible converged interior/replay-qualified result; the iteration-40 vector remains stopped. The parent would need to resolve the 011 pool/model-input conflict and 022 carbonate reliability treatment before claiming ion identification. Extra iterations or wider bounds alone are not justified by this diagnosis.
- Amend Jakobsen to pool targets. This follows what the shared peak directly measures and avoids its split uncertainty, but changes stage 4 to 24 targets and requires an explicit weight/scale amendment. It does not cure 011's large pool error. Any corresponding later stage-3/joint-fit observation change must be separately declared; do not silently propagate a new target meaning.
- Amend only the unreliable 022 carbonate admission/scale while retaining 011 carbonate. Removing that one target gives 25 targets; retaining it with a different scale requires a declared uncertainty/engineering scale. Neither action removes 011's dominant pool mismatch. Later stages must keep source reliability and repeated-use labels consistent. This diagnosis supplies no replacement numerical uncertainty.
- Reconsider which fixed chemistry/ion/interactions are estimated first, or authorize a bounded comparison of accepted alternatives before another ion fit. R4/R5 and carbonate Born sensitivity, the prior R5/ion overlap, and the adopted-model evaluation make compensation plausible. This changes the accepted sequencing or fixed-input assumptions and therefore needs a design amendment; it also changes the precursor used by later stages. No single alternative, parameter shift or trace interaction is selected here.

The scientific finding is conditional model/data disagreement for these exact inputs and approximate feeds, plus a source-basis input defect at 022. It is not physical validation, a confidence interval, proof of a structurally incapable model, or permission to promote the bound-active endpoint. Source calibration correlations and isotope/dioxane effects remain unquantified.

## Evidence, numerical checks and accounting

`target-evaluations.csv` gives every target for every variant; `sensitivity-summary.csv` adds total/state/carbonate contributions; `states.json` gives all solved states, species ratios, densities, residuals and native reference contractions; `decomposition.json` gives exact log constants and activities. `observed-and-modeled-ratios.csv`, `pool-evaluation.json`, the historical tables, `source-provenance.json`, `inputs.json` and `timing-and-program-accounting.json` identify the remaining evidence. The source-corrected 022 request is an evaluation input stored only in this directory.

The fresh A-start and iteration-40 predictions agree with the retained chemistry diagnosis to absolute 1e-10; the native equilibrium residuals for all 108 evaluated state records are below 1e-10. The Engine wheel hash is `32ce708a671c24dbb0112f53bc4a18021eaa1bd10a1f04e96b9ce8d3145da52f`; every installed `epcsaft/` wheel member was checked byte-for-byte. No Engine source checkout is imported.

Measured successful inspection/evaluation/history/report processes used **13.622686000 CPU-s / 13.707330031 wall-s**. A conservative additional charge of **96 CPU-s / 12 wall-s** covers short unmetered commands, source checks and the two disposable equation-check attempts; it is a charge, not measured utilization. Charged diagnosis total is **109.622686000 CPU-s / 25.707330031 active wall-s**, within 300/300. Native numerical scripts ran at `nice -n 10`; the longest complete evaluation was below 10 s. One final evaluation repeat retained all state closure diagnostics and native requested-tolerance flags; both runs are charged. No fit was run.

Entry cumulative charge was **1289.168844720 CPU-s / at least 441.633359797 active wall-s**. Exit cumulative is **1398.791530720 CPU-s / at least 467.340689828 active wall-s**; remaining is at most **142601.208469280 CPU-s / 21132.659310172 active wall-s**. The prior charge is included once; earlier unmetered startup/verification overhead remains unknown. Prose and Git closeout do not run the model. Parent review remains open.
