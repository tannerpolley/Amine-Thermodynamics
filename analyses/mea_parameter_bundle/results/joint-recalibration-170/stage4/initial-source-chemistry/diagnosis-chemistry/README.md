# Initial ion diagnosis: local R5–ion confounding and an unsettled constrained fit

**Classification:** the retained result is an incomplete, bound-active ion calibration with strong local overlap between R5 reference-level and ion sensitivities. The fitted rows do not isolate ion properties from fixed chemistry. The requested R2 pivot-preserving temperature direction is weak on these 20/40 °C states. This probe does not distinguish fixed zero reactive interactions from other fixed model assumptions, and does not establish a unique cause of the four bounds.

The parent authorized at most 120 CPU-s / 120 wall-s, reader correction and exact Jacobian evaluation only. No fit, B endpoint, changed bound/start/iteration limit, parameter selection or model change was authorized or performed. The same cf26a17b wheel and immutable 26-target declaration remain in use.

## Eleven physical values and the reader correction

`fit_campaign.fitted_parameter_values` now consumes every returned physical target in native chart order, applying the existing R5 source-to-native conversion where required. The endpoint completeness count and physical-Jacobian dimensions use the target count, while the optimizer Jacobian and its coordinate derivatives keep seven columns. Centered coordinate declarations take their source value from the serialized endpoint rather than indexing a target vector as if it were a coordinate vector. No new fit was run to exercise that path.

The corrected reader was checked on the exact native charts at both requested points; all eleven source values agree with their source parameter records within $10^{-12}$ in their stored units. This checks the previous failing tied-output case. It does not replace the unrun full endpoint replay or centered derivative qualification.

| Physical target | A start | A iteration 40 |
|---|---:|---:|
| `component/protonated-monoethanolamine/segment_diameter` | 3.563 | 4.49330937370393 |
| `component/protonated-monoethanolamine/packing_diameter` | 3.13544 | 3.95411224885946 |
| `component/protonated-monoethanolamine/debye_huckel_diameter` | 3.13544 | 3.95411224885946 |
| `component/carbamate-anion/segment_diameter` | 3.5605 | 2 |
| `component/carbamate-anion/packing_diameter` | 3.13324 | 1.76 |
| `component/carbamate-anion/debye_huckel_diameter` | 3.13324 | 1.76 |
| `component/protonated-monoethanolamine/dispersion_energy_over_k` | 228.71 | 489.253732302516 |
| `component/carbamate-anion/dispersion_energy_over_k` | 533.11 | 50 |
| `component/protonated-monoethanolamine/born_diameter` | 3.563 | 1 |
| `component/carbamate-anion/born_diameter` | 3.5605 | 1 |
| `pair/carbamate-anion/protonated-monoethanolamine/k_ij` | 0 | -0.763082703628406 |

## What the objective is fitting

All 9 states and 26 targets return exact native predictions and residual derivatives at both points. The new iteration-40 first seven Jacobian columns match the retained fitted columns with maximum absolute difference 3.02813e-14; the maximum prediction difference is 3.05311e-15. No observation, denominator, source feed, scale or weight changed.

| State | A start cost | Iteration-40 cost |
|---|---:|---:|
| Bottinger2008_state_030 | 0.0229947446105 | 0.00110896232066 |
| Bottinger2008_state_042 | 0.0224094378211 | 0.00221385081316 |
| Bottinger2008_state_046 | 0.133124008868 | 0.00346554765975 |
| Matin2012_state_009 | 1.02279700515 | 0.0674349397711 |
| Matin2012_state_019 | 3.28596684504 | 0.0672235559633 |
| Matin2012_state_016 | 2.41500954349 | 0.372928712291 |
| Bottinger2008_state_051 | 0.300494949306 | 0.00882909299647 |
| Jakobsen2005_state_011 | 45.0198243132 | 0.255630801666 |
| Jakobsen2005_state_022 | 6.95422087232 | 0.582139580149 |

| Species family | A start cost | Iteration-40 cost |
|---|---:|---:|
| MEA + MEAH+ | 0.128092917933 | 0.00600989728564 |
| MEACOO- | 1.32004737324 | 0.0821254336502 |
| MEAH+ | 1.87509351735 | 0.334518846121 |
| HCO3- | 8.48214899753 | 0.82592023276 |
| MEA | 0.00351419694217 | 0.110481112826 |
| CO3^2- | 47.3679447168 | 0.00191952098742 |

At A, Jakobsen 011 carbonate alone contributes 41.88698419 of the 59.17684172 total; the two printed carbonate-ratio targets together contribute 47.36794472. The initial gradients favor decreasing carbamate size/dispersion and carbamate Born diameter, while MEAH⁺ Born diameter initially has the opposite local sign. A single starting derivative therefore cannot describe the whole nonlinear path to four bounds.

At iteration 40, the remaining cost is led by Jakobsen 022 bicarbonate (0.51833522), Jakobsen 011 protonated MEA (0.24753315), Matin 016 bicarbonate/carbonate pool (0.21695650), and Matin 016 free MEA (0.11048111). The 011/022 carbonate cost has fallen to 0.00191952. Jakobsen 011 carbonate/amine ratio changes from 0.07760960 to 0.00534839 against 0.00545951 observed. At iteration 40, Jakobsen 022 bicarbonate/amine remains high (0.20783673 against 0.13339223), while Matin 016 bicarbonate/carbonate pool is low (0.00195411 against 0.008) and free MEA is low (0.01136478 against 0.0181). These are different declared quantities and state bases; their numerical values are not compared directly across sources. The four bound-active directions all have positive cost gradients for an increase away from the lower bound; they still favor movement below the allowed bounds locally.

| Bound-active coordinate | Gradient per optimizer unit | Largest contributions favoring a lower value | Largest opposing contribution |
|---|---:|---|---|
| Carbamate segment size | +0.00143785043 | Jakobsen2005_state_022::HCO3- (+0.00156147), Matin2012_state_009::HCO3- (+0.000701888) | Jakobsen2005_state_011::MEAH+ (-0.000742621) |
| Carbamate dispersion | +0.0016550729 | Matin2012_state_016::HCO3- (+0.00394648), Matin2012_state_016::MEA (+0.00202024) | Jakobsen2005_state_022::HCO3- (-0.00634738) |
| MEAH⁺ Born diameter | +0.00343523008 | Matin2012_state_016::HCO3- (+0.0121542), Matin2012_state_009::HCO3- (+0.00423818) | Jakobsen2005_state_022::HCO3- (-0.00687473) |
| Carbamate Born diameter | +0.000618166748 | Jakobsen2005_state_022::HCO3- (+0.0207862), Jakobsen2005_state_011::HCO3- (+0.00462263) | Matin2012_state_016::HCO3- (-0.0141062) |

Positive entries mean increasing that coordinate raises cost; decreasing it lowers cost to first order. Large signed row contributions cancel, especially for the Born diameters. The competing Jakobsen bicarbonate ratio and Matin bicarbonate/carbonate-pool/free-MEA targets explain the remaining trade-off. They do not identify one physical ion mechanism.

## Exact chemistry columns and weighted conditioning

The nine-column matrices use the same difference residuals and weights as the ion fit. Scales are 0.1 Å for sizes/Born diameters, 10 K for dispersion, 0.01 for mutual interaction, 80 K for unshifted R5, and 2500 J/mol for the R2 enthalpy shift. The R5 native natural-log reciprocal coefficient is mapped by −ln(10); its reported column is oriented toward increasing source $a_k$. R2 uses Engine `reaction_enthalpy_shift` at 313.15 K. It tests temperature response while holding the 313.15 K reference level fixed; it does not test an arbitrary R2 reference-level offset. The 40 °C rows have essentially zero sensitivity to this pivot-preserving R2 direction.

| Point | Rank, cutoff $10^{-14}s_{max}$ | Condition number | R5 cost gradient per K | R2 cost gradient per J/mol |
|---|---:|---:|---:|---:|
| A-start | 9/9 | 175500.86677 | +0.7404668065 | -9.31448986393e-08 |
| A-iteration-40 | 9/9 | 131178.520439 | +0.000408081465393 | +5.07483619356e-08 |

A positive R5 gradient at both points means a small reduction of the fixed source R5 reference coefficient lowers this ion objective locally. The 80 K-scaled R5 column norms are 5.82232402 and 0.66911987, compared with 0.00007711119 and 0.00077327577 for the 2500 J/mol-scaled R2 direction. This is a statement about these rows, residual scales and local points, not a source-uncertainty estimate.

| Point / chemistry column | Cosine with four bound-active ion columns | Principal angle, degrees | Column norm outside that span, fraction |
|---|---:|---:|---:|
| A-start / R5 unshifted a_k | 0.989239780846 | 8.41275777076 | 0.146303301367 |
| A-start / R2 enthalpy shift | 0.874829015362 | 28.9752538902 | 0.484431825833 |
| A-iteration-40 / R5 unshifted a_k | 0.987652485256 | 9.0131229092 | 0.156660679071 |
| A-iteration-40 / R2 enthalpy shift | 0.603824948843 | 52.8556665883 | 0.797116949484 |

The comparison uses the four columns that are bound-active at iteration 40 at both points, even though all coordinates start interior. Their span has rank four. The angle is between each chemistry column and that whole span, computed from an orthonormal singular-vector basis. It permits both signs of ion movement and does not assert that the compensating direction is feasible at a lower bound. R5 has 98.8–98.9% projection cosine, with 14.6–15.7% of its norm outside the span; the directions overlap strongly but are not identical. This supports reaction-reference/activity-coefficient confounding as a local explanation for the compensating ion changes. It does not prove the complete fitting trajectory has one cause.

Full nine-column singular values, in the declared weighted optimizer units:

- A-start: 5.87784547769, 0.287333745593, 0.0995467942806, 0.0355497261323, 0.0151261039776, 0.00384658050598, 0.000220735491708, 9.27359183033e-05, 3.34918316123e-05.
- A-iteration-40: 0.706856653893, 0.0633513860575, 0.0300277128795, 0.0122708193686, 0.00400646626292, 0.00144454614046, 0.000567850469319, 0.000182873169078, 5.38850912121e-06.

The matrices are numerically full rank but poorly conditioned. The chemistry columns are diagnostic, not newly fitted coordinates. No covariance or standard errors are inferred. Carbamate–water, MEAH⁺–water value/slope and bicarbonate–water interactions remain fixed at zero, so these two-point derivatives cannot assign the residual mismatch to those choices or rule them out. The R2 result is limited to the chosen pivot-preserving enthalpy direction.

## Iteration-40 status and active-set history

Native projected-gradient infinity norm is 1.07738919368e-05, reproduced from the exact residual matrix as 1.07738919755e-05, against gradient tolerance $10^{-8}$. Thus the remaining three free ion directions are not converged under the declared gradient limit. The last cost step is -3.5063487247e-07 (relative -2.57634982903e-07); cost is still falling, despite smaller steps. Native termination remains `limit_reached`, not an optimum.

All seven ion coordinates start interior; four finish exactly at their lower bounds. Intermediate active-bound membership was not exposed or retained, so transition indices and any restart’s membership cannot be reconstructed without another fit, which is prohibited here. The native scalar cost history has a jump at history index 21, from 1.3971057713524728 to 1.5947854875568344. Its cause is unverified; it is not labeled an active-set event. The native final message reports 20 iterations while the aggregate counter/history has 40; both remain disclosed. `native-cost-history.csv` retains all 41 scalar entries and timings.

## Retained evidence, allowance and stop

`target-costs-gradients.csv` gives all 26 targets at both points; `state-costs-gradients.csv` gives all nine state contributions, and `coordinate-gradients.csv` gives total coordinate gradients and positive/negative row sums in source and optimizer units. `all-physical-target-values.csv` gives the eleven corrected-reader outputs. The two `*-exact.json` files retain native predictions, unit-weight exact residual Jacobians and charts; the two `*-weighted-matrix.json` files retain the final weighted nine-column matrices and source-unit conversions. `declaration.json` binds the same frozen inputs, point hashes, chemistry definitions and authority.

The two bounded exact-Jacobian calls and their process overhead used 1.050963000 measured CPU-s / 1.053779847 wall-s. Short unmetered inspection, reader-check and algebra commands receive an additional conservative 64 CPU-s / 2 wall-s charge, covering their rounded host-command durations at all 32 CPUs; this is a charge, not measured CPU. Total charged diagnosis is **65.050963000 CPU-s / 3.053779847 wall-s**, inside 120/120, leaving 54.949037000 CPU-s / 116.946220153 wall-s of this diagnosis allowance. No further numerical call is planned.

Cumulative program charges are **1289.168844720 CPU-s / at least 441.633359797 active wall-s**; remaining at most **142710.831155280 CPU-s / 21158.366640203 wall-s**. Prior charges are retained once. Earlier unmetered startup/verification overhead remains unknown, as already recorded. These probes ran at `nice -n 10`, single-thread BLAS/OpenMP, with no fit pool or subagent. Each native call had a 60 s wall cap and completed in under 0.5 s.

The result is local conditional assessment and numerical verification of the corrected output reader and exact sensitivities. The calibration remains stopped: no eligible I₀, S₁, I₁ or S₂, no movement test, no endpoint promotion and no physical validation. The parent chooses any subsequent design or diagnosis; this task selects none. Independent delivered review remains with the parent.

## All target costs

| Target | A start cost | Iteration-40 cost |
|---|---:|---:|
| Bottinger2008_state_030::MEA + MEAH+ | 9.19648133692e-06 | 0.000281104346385 |
| Bottinger2008_state_030::MEACOO- | 0.0229855481292 | 0.000827857974278 |
| Bottinger2008_state_042::MEA + MEAH+ | 3.15286198728e-05 | 0.000941207396917 |
| Bottinger2008_state_042::MEACOO- | 0.0223779092013 | 0.00127264341624 |
| Bottinger2008_state_046::MEA + MEAH+ | 0.020364312026 | 0.000370815613238 |
| Bottinger2008_state_046::MEACOO- | 0.112759696842 | 0.00309473204651 |
| Matin2012_state_009::MEAH+ | 0.155672804208 | 0.00631298245395 |
| Matin2012_state_009::MEACOO- | 0.0962034543696 | 0.00296782641018 |
| Matin2012_state_009::HCO3- | 0.770920746577 | 0.058154130907 |
| Matin2012_state_019::MEAH+ | 0.418074719421 | 0.0372500349301 |
| Matin2012_state_019::MEACOO- | 0.332126991624 | 0.00532592197305 |
| Matin2012_state_019::HCO3- | 2.535765134 | 0.0246475990602 |
| Matin2012_state_016::MEA | 0.00351419694217 | 0.110481112826 |
| Matin2012_state_016::MEAH+ | 0.361368672753 | 0.0226858989118 |
| Matin2012_state_016::MEACOO- | 0.215089874589 | 0.0228052027634 |
| Matin2012_state_016::HCO3- | 1.83503679921 | 0.21695649779 |
| Bottinger2008_state_051::MEA + MEAH+ | 0.107687880806 | 0.0044167699291 |
| Bottinger2008_state_051::MEACOO- | 0.1928070685 | 0.00441232306736 |
| Jakobsen2005_state_011::MEAH+ | 0.890012298174 | 0.247533149168 |
| Jakobsen2005_state_011::MEACOO- | 0.151088811825 | 0.000171516152069 |
| Jakobsen2005_state_011::HCO3- | 2.09173901022 | 0.00782678533407 |
| Jakobsen2005_state_011::CO3^2- | 41.886984193 | 9.93510113661e-05 |
| Jakobsen2005_state_022::MEAH+ | 0.0499650227949 | 0.020736780657 |
| Jakobsen2005_state_022::MEACOO- | 0.174608018163 | 0.041247409847 |
| Jakobsen2005_state_022::HCO3- | 1.24868730752 | 0.518335219669 |
| Jakobsen2005_state_022::CO3^2- | 5.48096052384 | 0.00182016997606 |

## Final code accounting

The complete block now adds **46/250 gross executable lines** and removes 14, against `e1ece11`. Its conservative campaign charge is **544/900**, leaving 356 campaign lines and 204 in this block. The final classifier against `6c8d20073fd0e5fda8dd323a51f55551d12b7486` reports 369 executable additions; the retained conservative prior charge is not replaced by that smaller classification. All code remains in the two existing fit owners. Generated inputs, results, notebook and prose are separate. No new executable probe file, persistent test, generic EOS/equilibrium/fit method or dependency was added. The one previous failing reader case is checked on its retained native charts at both points.
