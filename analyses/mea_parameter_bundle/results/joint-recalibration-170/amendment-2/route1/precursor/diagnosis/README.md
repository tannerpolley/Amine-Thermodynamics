# Precursor A: bounded two-point diagnosis

Precursor A remains unconverged at 40 iterations, with both segment diameters at 5.8 Å, both Born diameters at 1 Å and R5 a_k at 2400 K, all bounds. The parent authorized this diagnosis at most 60 CPU-s / 60 s, with no fit, B start, 3b calculation or bound change. This is **conditional assessment of an incomplete calibration and numerical verification of local sensitivities**. It is not a selected precursor, parameter adoption or physical validation.

**Shared step 2 (stage 5, smaller d_V) completed.** Its full record is [parameters.json](../../../stage5-smaller-dV/parameters.json), with [both roots and checks](../../../stage5-smaller-dV/README.md). Smaller d_V = 0.2464540312088979 L/mol and d_T = 2436.4423007273617 K; the larger root is retained separately. The precursor stop does not undo this completed reduction.

The same merged-main Engine 84ca269d wheel, SHA-256 `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`, is used at nice 10 with single-thread BLAS/OpenMP. Inputs and hashes are in [inputs.json](inputs.json). The start uses the frozen A record and the same Kiepe continuation construction; iteration 40 uses the already retained weighted native Jacobian and predictions, without another endpoint evaluation. A new exact start evaluation makes all 203 rows available, reproduces every saved prediction exactly, and differs in weighted residual by at most 1.53e-16. No endpoint closure, centered derivative or serialized endpoint replay qualification is added by this diagnosis.

## Family costs and largest contributors

Cost is one half the squared weighted residual norm. Twenty-five reacting pressures, 39 Kiepe pressures and 131 original species observations form 195 memberships. Sixteen species targets are also in the 24-target stage-4 family; amendment 2 assigns them to standardized differences once. Thus the additive objective has 25 + 115 + 39 + 24 = 203 rows. The 131-species diagnostic below restores the original log-ratio score for those 16 targets, using weight 1/(131 ln(10)^2); it is not an extra objective term. The 24 quantities include Böttinger and Matin mole fractions and Jakobsen ratios; the five inorganic pools are identified below.

| Family | A start cost | A iteration-40 cost |
|---|---|---|
| Reacting pressures (25) | 0.103307369557 | 0.0644782745271 |
| Unshared log species (115) | 0.0296078660032 | 0.0348614530959 |
| Kiepe pressures (39) | 0.000679019498732 | 0.00122766160347 |
| Stage-4 differences (24) | 62.8112022683 | 0.486535524796 |
| All original log species (131), diagnostic only | 0.0303472434636 | 0.031883839676 |
| Additive total | 62.9447965234 | 0.587102914023 |

At the start, Jakobsen 011 inorganic pool alone contributes 49.79490669, about 79.11% of total cost. At iteration 40, the largest target is Jakobsen 011 MEAH⁺/amine, 0.2372895523, about 40.42% of total. The pool correction does not eliminate the remaining protonated-MEA and Matin pool trade-offs. The following costs belong to the actual 203-row objective; complete row/state values are in [target-costs-gradients.csv](target-costs-gradients.csv) and [state-costs.csv](state-costs.csv). `HCO3-` in a Matin target ID denotes its declared bicarbonate-plus-carbonate pool.

### A-start: ten largest targets

| Rank | Target | Cost |
|---|---|---|
| 1 | Jakobsen 011::inorganic pool | 49.7949066856 |
| 2 | Jakobsen 022::inorganic pool | 3.5811913742 |
| 3 | Matin 019::inorganic pool | 2.74707889517 |
| 4 | Matin 016::inorganic pool | 1.98795653248 |
| 5 | Jakobsen 011::MEAH+ | 0.964179989688 |
| 6 | Matin 009::inorganic pool | 0.835164142125 |
| 7 | Matin 019::MEAH+ | 0.452914279373 |
| 8 | Matin 016::MEAH+ | 0.391482728816 |
| 9 | Jakobsen 022::MEACOO- | 0.364857804993 |
| 10 | Matin 019::MEACOO- | 0.359804240926 |

### A-start: ten largest states

| Rank | State | Cost |
|---|---|---|
| 1 | Jakobsen 011 | 50.9227662215 |
| 2 | Jakobsen 022 | 4.08540646803 |
| 3 | Matin 019 | 3.56009931807 |
| 4 | Matin 016 | 2.61626033879 |
| 5 | Matin 009 | 1.10803201637 |
| 6 | Böttinger 051 | 0.325536195081 |
| 7 | Böttinger 046 | 0.144217676274 |
| 8 | Böttinger 030 | 0.024910973328 |
| 9 | Böttinger 042 | 0.0242768909729 |
| 10 | vle_obs_0193 | 0.0221109393353 |

### A-iteration-40: ten largest targets

| Rank | Target | Cost |
|---|---|---|
| 1 | Jakobsen 011::MEAH+ | 0.237289552326 |
| 2 | Matin 016::inorganic pool | 0.0597910227957 |
| 3 | Matin 009::inorganic pool | 0.0546193859801 |
| 4 | Matin 019::MEAH+ | 0.0312874479371 |
| 5 | Matin 016::MEA | 0.0237379318786 |
| 6 | Jakobsen 011::inorganic pool | 0.0201578166699 |
| 7 | Matin 016::MEAH+ | 0.0192890961252 |
| 8 | Böttinger 046::MEACOO- | 0.00894028802736 |
| 9 | vle_obs_0127-pco2 | 0.00821810517382 |
| 10 | Matin 001::inorganic pool | 0.00804355579663 |

### A-iteration-40: ten largest states

| Rank | State | Cost |
|---|---|---|
| 1 | Jakobsen 011 | 0.257516285253 |
| 2 | Matin 016 | 0.108375116322 |
| 3 | Matin 009 | 0.0616748593615 |
| 4 | Matin 019 | 0.0322211423117 |
| 5 | Jakobsen 022 | 0.0133213231341 |
| 6 | Böttinger 046 | 0.00894153927934 |
| 7 | vle_obs_0127 | 0.00821810517382 |
| 8 | Matin 001 | 0.00807678926993 |
| 9 | vle_obs_0146 | 0.00732648689216 |
| 10 | vle_obs_0233 | 0.00676296605949 |

## Bound-coordinate gradients and competing targets

All gradients here point toward **increasing source coordinates**, with coordinate scales 0.1 Å for both segment/Born diameters and 80 K for R5 a_k. Segment changes include their 0.88 packing/Debye–Hückel ties. Native R5 optimizer orientation is reversed because b_native = −ln(10) a_k; this sign is corrected here. Positive dC/dq favors decreasing the source coordinate; negative favors increasing it. Divide size gradients by 0.1 Å or R5 by 80 K to obtain gradients per physical unit. [coordinate-gradients.csv](coordinate-gradients.csv) contains both orientations, physical-unit gradients, and positive/negative row sums.

“For outward” means first-order cost reduction by increasing either segment diameter past its final upper bound, or decreasing either Born diameter/R5 past its final lower bound. This same reference direction is used at the start, when all coordinates are interior. Each signed target term is r_i J_ij; terms sum to the coordinate gradient. The two largest terms on each side are shown; [summary.json](summary.json) retains five on each side and the target CSV retains all terms.

### A-start

| Coordinate | dC/dq | Largest for outward | Largest against outward |
|---|---|---|---|
| MEAH+ segment | -1.78495571249 | Jakobsen 011::inorganic pool (-1.38956577898)<br>Matin 016::inorganic pool (-0.0996296841533) | Böttinger 030::MEACOO- (0.000784966833757)<br>vle_obs_0193-pco2 (0.000639868170975) |
| carbamate segment | 7.02833248436 | Matin 016::MEA (-0.00197332309996)<br>vle_obs_0252-pco2 (-0.000449432048693) | Jakobsen 011::inorganic pool (5.67288466431)<br>Jakobsen 022::inorganic pool (0.308766046909) |
| MEAH+ Born | -1.22094600806 | vle_obs_0132-pco2 (7.06795552806e-05)<br>vle_obs_0127-pco2 (5.78613428953e-05) | Jakobsen 011::inorganic pool (-0.949358330428)<br>Matin 019::inorganic pool (-0.0641367115387) |
| carbamate Born | 0.737795157721 | Jakobsen 011::inorganic pool (0.564403981479)<br>Matin 019::inorganic pool (0.0417197991099) | Matin 016::MEA (-0.000246858072804)<br>vle_obs_0266-pco2 (-6.26782864549e-05) |
| R5 a_k | 52.05090409 | Jakobsen 011::inorganic pool (44.372270112)<br>Matin 016::inorganic pool (1.51567297234) | vle_obs_0127-pco2 (-0.00250847093205)<br>vle_obs_0132-pco2 (-0.00201643462125) |

### A-iteration-40

| Coordinate | dC/dq | Largest for outward | Largest against outward |
|---|---|---|---|
| MEAH+ segment | 0.000693615723077 | Jakobsen 022::inorganic pool (-0.00611166208708)<br>Jakobsen 011::inorganic pool (-0.0051646032036) | Matin 016::inorganic pool (0.0046635120942)<br>Matin 016::MEA (0.00135653567779) |
| carbamate segment | -0.000950492488286 | Matin 016::inorganic pool (-0.00720274732903)<br>Matin 016::MEA (-0.00285723665858) | Jakobsen 011::inorganic pool (0.00525872857533)<br>Jakobsen 022::inorganic pool (0.00252906503684) |
| MEAH+ Born | -6.67660663724e-07 | Matin 016::inorganic pool (0.00285831302114)<br>vle_obs_0132-pco2 (0.00220452606884) | Jakobsen 022::inorganic pool (-0.00568626491526)<br>Jakobsen 011::inorganic pool (-0.00423550166217) |
| carbamate Born | 0.000247098194432 | Jakobsen 011::inorganic pool (0.0164859048612)<br>Jakobsen 022::inorganic pool (0.00356476598238) | Matin 016::inorganic pool (-0.0143996548628)<br>Matin 016::MEA (-0.00598670956885) |
| R5 a_k | 0.0021825472786 | Jakobsen 022::inorganic pool (0.0132701369412)<br>Jakobsen 011::inorganic pool (0.00777596654561) | vle_obs_0127-pco2 (-0.00654334985246)<br>vle_obs_0146-pco2 (-0.0056936731152) |

At iteration 40, carbamate segment, carbamate Born and R5 favor outward movement locally. MEAH⁺ segment and MEAH⁺ Born favor movement into the allowed interval. The MEAH⁺ Born total is small because sizeable opposing target terms cancel. In particular, the largest projected-gradient component is the MEAH⁺ segment direction toward smaller diameter, which is feasible. The active bounds alone therefore do not establish that all five directions require wider intervals. Initial and final carbamate-segment signs differ; two local derivatives cannot reconstruct the nonlinear path or assign one physical mechanism. No bound revision is proposed here.

## Weighted spectra and O1 R5 projection

Matrices include declared observation weights and coordinate scales: sizes/Born diameters 0.1 Å, dispersions 10 K, ion interaction and CO₂–water k_p 0.01, binary reciprocal-temperature slope 10 K, R5 a_k 80 K. The matrices are dimensionless weighted residual derivatives per scaled coordinate, with rank cutoff 1e-14 times the largest singular value. At the start all ten columns are free; at iteration 40, free columns are the two dispersions, mutual ion interaction, CO₂–water k_p and slope. “Final-free subset at start” is a five-column comparison, not the start's active set.

| Point | Columns | Rank | Condition |
|---|---|---|---|
| A-start | full | 10/10 | 12290.8523983 |
| A-start | free | 10/10 | 12290.8523983 |
| A-iteration-40 | full | 10/10 | 1078.53531598 |
| A-iteration-40 | free | 5/5 | 42.5286949269 |
| A-start | final-free subset | 5/5 | 49.1566097452 |

A-start full spectrum: 4.79783901579, 0.344496996991, 0.134339804995, 0.0735433731925, 0.0715535663453, 0.0258415351526, 0.00750798601527, 0.00421184798065, 0.00114743840638, 0.000390358525211.

A-start free spectrum: 4.79783901579, 0.344496996991, 0.134339804995, 0.0735433731925, 0.0715535663453, 0.0258415351526, 0.00750798601527, 0.00421184798065, 0.00114743840638, 0.000390358525211.

A-iteration-40 full spectrum: 0.350365868375, 0.273603746965, 0.212614516437, 0.0579937818832, 0.050229809913, 0.0252918386311, 0.0193935718866, 0.00544778549263, 0.00220266628087, 0.000324853403671.

A-iteration-40 free spectrum: 0.256266111901, 0.25344334162, 0.0999738086556, 0.0571622520874, 0.0060257224526.

Final-free subset at start: 0.521559475241, 0.344339429812, 0.0717307185807, 0.0308949801067, 0.0106101596091.

| Point | Ion span | Rank | R5 cosine | Angle, degrees | Outside-span norm fraction |
|---|---|---|---|---|---|
| A-start | all_7_ions | 7 | 0.999846707826 | 1.00323614198 | 0.0175088791396 |
| A-start | final_free_ions | 3 | 0.999559210846 | 1.7012535089 | 0.0296881123062 |
| A-start | final_active_ions | 4 | 0.997549905715 | 4.01160108953 | 0.0699584562976 |
| A-iteration-40 | all_7_ions | 7 | 0.999685961294 | 1.43595419167 | 0.0250595050048 |
| A-iteration-40 | final_free_ions | 3 | 0.956420037776 | 16.9773937553 | 0.291994368681 |
| A-iteration-40 | final_active_ions | 4 | 0.938136530116 | 20.2590705377 | 0.346265578511 |

R5 has only 1.75% / 2.51% of its column norm outside the full seven-ion span at the start/end. This supports strong local overlap of the R5 reference-level and ion activity sensitivities under these weights. The projections allow either sign of ion motion; they do not enforce the bounds and do not prove a feasible compensating direction or unique cause of the stopped fit. Both full matrices retain rank ten. The exact weighted matrices, including scales and source orientation, are retained in [A-start-weighted-matrix.json](A-start-weighted-matrix.json) and [A-iteration-40-weighted-matrix.json](A-iteration-40-weighted-matrix.json). No covariance is inferred for the unconverged vector.

## Inorganic pools compared with the stopped ions-first record

The pool is HCO₃⁻ + CO₃²⁻. Jakobsen quantities are pool/total analytical amine; Matin quantities are liquid mole fractions. Their values are not compared across these different bases. Standardized residual z = (prediction − observation)/(0.1 observation + 0.001); current weighted residual is z/√24. The historical Jakobsen pool is reconstructed by adding its separately reported bicarbonate and carbonate predictions; it was not the historical fitted target. Historical values below are re-expressed at the current scale/weight only for comparison, without a new calculation or use as a start. State 022 in the historical ions-first record had the wrong 11.58372141 wt% MEA feed; the new calculation uses corrected 27.14274817 wt%. The historical fit had 26 targets and fixed R5, whereas this joint objective has 203 rows and free R5/binary coefficients. Differences cannot be attributed to pooling alone.

| State | Current start z | Current iteration-40 z | Historical start z | Historical iteration-40 z |
|---|---|---|---|---|
| Jakobsen 011 | 48.8892168163 | 0.98365400429 | 48.8892168163 | 0.372086091534 |
| Jakobsen 022 | 13.1109567142 | 0.396270769652 | 9.63708507773 | 4.9554239994 |
| Matin 009 | 6.33149893959 | -1.61917587897 | 6.33149893959 | -1.738969467 |
| Matin 019 | 11.4830216828 | -0.190706177165 | 11.4830216828 | -1.13211092704 |
| Matin 016 | 9.76841407593 | -1.69409831303 | 9.76841407593 | -3.35882983866 |

| State | Observed | Current start prediction | Current iteration-40 prediction | Historical start prediction | Historical iteration-40 prediction |
|---|---|---|---|---|---|
| Jakobsen 011 | 0.00727934485896 | 0.0917567085843 | 0.00897903453517 | 0.0917567085843 | 0.00792228524825 |
| Jakobsen 022 | 0.141342756184 | 0.339767588717 | 0.147340027231 | 0.287193057908 | 0.216339508797 |
| Matin 009 | 0.003 | 0.0112309486215 | 0.000895071357336 | 0.0112309486215 | 0.000739339692898 |
| Matin 019 | 0.0114 | 0.0359736664012 | 0.0109918887809 | 0.0359736664012 | 0.00897728261613 |
| Matin 016 | 0.008 | 0.0255831453367 | 0.00495062303655 | 0.0255831453367 | 0.00195410629042 |

The current 022 pool standardized residual is +0.3963, compared with +4.9554 for the historical stopped vector on its wrong feed. Matin 009/019/016 current residuals are −1.6192/−0.1907/−1.6941, compared with −1.7390/−1.1321/−3.3588 historically. Jakobsen 011 current pool residual is +0.9837 versus +0.3721 historically. These comparisons describe calibration discrepancies at different parameter vectors and, for 022, different feeds. Full differences, scales and re-expressed weighted residuals are in [pooled-residual-comparison.csv](pooled-residual-comparison.csv).

## Iteration-40 convergence status

Native termination is `limit_reached`, “iteration limit reached”, at 40 iterations. The projected-gradient infinity norm is **0.000693615723077**, compared with **1e-8**; native and reconstructed values agree within 8.4e-16. The gradient norm on just the five non-active columns is 0.000231379242971. Bound-active MEAH⁺ segment also contributes an inward feasible direction, so the projected norm is larger than the five-column norm.

The last cost changes from **0.587105866588336** to **0.587102914022701**, a decrease of **2.95256563465e-06** (relative 5.02901742714e-06). **Cost was still falling.** The last five entries fall, while the complete history contains increases. Intermediate active sets are not retained, so no increase is assigned to an active-set event. The complete history and projected gradient vector are in summary.json. Non-convergence and five active bounds remain the binding stops; no rank, row-availability or replay discrepancy appeared in this diagnosis.

## Charges, code and handback

The first exact evaluation returned, but output capture referenced absent `ObservationEvaluation.targets` and ended before writing timing. It is charged its full enforced 35 CPU-s / 35 s cap. The replacement uses only available result fields and is capped at 15/15; it measures 7.716344000 CPU-s / 7.717599043 s, including module imports and continuation. Algebra measures 0.069284000 CPU-s / 0.074746507 s. An additional conservative 5 CPU-s / 5 s covers short inspections, reports, verification and the local commit. This capture error is not a failed scientific serialization-replay check; no fitted record was rewritten or promoted.

Total diagnosis charge is **47.785628000 CPU-s / 47.792345550 active wall-s**, within 60/60, leaving **12.214372000 CPU-s / 12.207654450 s** of the bounded diagnosis allowance. Cumulative program charges are **2204.045075720 CPU-s / at least 639.282933387 active wall-s**, leaving at most **141795.954924280 CPU-s / 20960.717066613 s**, less unknown earlier overhead. The precursor block has **6995.969486000 CPU-s / 429.241706345 s** remaining, without authorization to continue it. See [timing-and-program-accounting.json](timing-and-program-accounting.json).

This diagnosis adds **zero executable lines**. Part 1 remains at 80/180 gross added executable lines; the conservative campaign count remains 625/900. Numerical and prose consistency checks cover the added notebook text; no new HTML render is charged or claimed within this bounded diagnosis. The earlier rendered HTML predates this addition. No fit, B start, 3b, bound change, Engine edit, push, merge or GitHub write occurred. The parent retains Route 1 stopped and decides the next step with the owner; no new selected precursor or 3b record exists. Independent delivered review remains with the parent.
