# Route 1 joint precursor: required stop at A iteration 40

No complete precursor is selected. Start A reaches its 40-iteration limit without convergence and with five coordinates on bounds. Cost decreases from 62.94479652338308 to 0.5871029140227012, below both starts, but this finite vector is ineligible for the next stage. Start B cost is 18.3038169348457. Its fit and every 3b calculation remain unrun. No bound, iteration limit or numerical tolerance was changed.

Both starts return all 203 targets and pass the retained initial equilibrium and analytical-feed checks. The matrix contains the fixed 25 reacting pressures, 115 unshared species values, 39 Kiepe pressures and 24 standardized differences. Sixteen overlaps have one difference-residual owner. Both records have CO₂ dispersion 169.21 K, the corrected 022 feed, zero bicarbonate–water interaction and source-zero enthalpy shifts. The native fit returns 203 available predictions and zero failed trials, using 41 residual and 28 Jacobian evaluations. These are an incomplete calibration attempt; they are not a qualified parameter determination.

| Family (targets) | A start mean absolute relative error, % | B start, % | A iteration 40, % |
|---|---:|---:|---:|
| reacting pressures (25) | 51.276371 | 54.796634 | 89.546995 |
| unshared species (115) | 58.074576 | 30.024264 | 15.926736 |
| Kiepe pressures (39) | 2.666524 | 2.666524 | 3.841493 |
| ion difference quantities (24) | 108.516535 | 58.847926 | 11.222979 |

`family-errors.csv` retains each family contribution and RMSE; pressure RMSE has units Pa and species/amount-ratio RMSE has its stated dimensionless basis. The final family costs are reacting pressure 0.0644782745271, unshared species 0.0348614530959, Kiepe 0.00122766160347 and standardized differences 0.486535524796. Reduced total weighted cost does not imply improvement in mean absolute relative pressure error; the two statistics weight errors differently. `kiepe-isotherm-errors.csv` retains all four isotherms at A/B starts and the native A vector.

| Declared coordinate | Native returned vector in source units | Bound |
|---|---:|---|
| `component/protonated-monoethanolamine/segment_diameter` | 5.8 | Active |
| `component/carbamate-anion/segment_diameter` | 5.8 | Active |
| `component/protonated-monoethanolamine/dispersion_energy_over_k` | 422.785693387488 | Interior |
| `component/carbamate-anion/dispersion_energy_over_k` | 359.531697736544 | Interior |
| `component/protonated-monoethanolamine/born_diameter` | 1 | Active |
| `component/carbamate-anion/born_diameter` | 1 | Active |
| `pair/carbamate-anion/protonated-monoethanolamine/k_ij` | -0.802917025987871 | Interior |
| `pair/carbon-dioxide/water/k_ij` | -0.0481735994649263 | Interior |
| `pair/carbon-dioxide/water/k_ij/reciprocal_temperature_slope` | -40.4043211793824 | Interior |
| `reaction:R5:correlation:a_k` | 2400 | Active |

Segment and Born diameters are Å, dispersion and reciprocal-temperature slope are K, and interactions are dimensionless. Packing and Debye–Hückel diameters are tied at 0.88 times each segment diameter: 5.104 Å at this vector. Both segment diameters are at their 5.8 Å upper bounds; both Born diameters are at their 1 Å lower bounds; unshifted R5 a_k is at its 2400 K lower bound. R5 changes by −277.91 K from source, exceeding the declared 80 K reporting magnitude. Its stored b=0.3869 and c=0.0004277 K⁻¹ remain source-fixed; no 3b shift has been fitted. Mutual interaction changes by −0.802917, beyond the 0.03 reporting scale. CO₂–water changes are Δk_p=-0.00175669834435 and Δb=-4.73926897292 K; maximum |Δk(T)| over the declared target temperatures is 0.00278921968943, below 0.03.

The weighted, coordinate-scaled Jacobian has full rank 10/10 and free rank 5/5 at cutoff 1e-14 times its largest singular value. Conditions are 1078.53531598 full and 42.5286949269 after removing active-bound columns. Full spectrum: [0.3503658683750459, 0.27360374696464884, 0.21261451643671872, 0.05799378188316941, 0.05022980991297917, 0.02529183863111937, 0.019393571886633085, 0.005447785492634634, 0.002202666280870749, 0.00032485340367119435]. Free spectrum: [0.2562661119012235, 0.2534433416195349, 0.09997380865557864, 0.05716225208738542, 0.006025722452604434]. The native projected gradient norm is 0.000693615723076, above the declared 1e-8 convergence tolerance. The complete optimizer and physical Jacobians, gradients and native singular vectors are retained. Native covariance is unavailable for the unconverged, bound-active vector; no covariance is inverted or interpreted as uncertainty.

O1 uses this same retained Jacobian without another fit. R5's projection cosine onto all seven ion columns is 0.9996859612943051 (1.435954 degrees); onto the three free ion columns it is 0.9564200377755065; onto the four active ion columns it is 0.9381365301161991. `R5-projection.json` binds the columns, spectra, ranks and orthogonal norms. These are local sensitivities for this exact corrected 203-target objective. They do not transfer the old wrong-feed matrix's interpretation, prove unique ion quantities, or justify widening a bound.

The preserved `A/usable-budget-endpoint.json` is the explicitly incomplete vector, not a complete `parameters.json`. Its 14 named source-coordinate/tied-target values match the corrected existing reader's native output mapping. That mapping check is numerical bookkeeping only. Endpoint serialization replay, endpoint closure, centered derivatives and subsequent chemistry-pivot/heat checks were not launched after the mandatory stop. The initial 203-row balances for both starts are retained. No new row was omitted, and no endpoint was selected automatically.

The native fit itself charges 663.565095 CPU-s / 35.254392171 wall-s. The entire precursor run, including imports, both starts and child work, charges 680.719557000 CPU-s / 52.401259255 wall-s. Including requalification and shared preparation once, this block charges 695.799685000 CPU-s / 67.607706820 wall-s at the numerical stop, leaving 7104.200315000 CPU-s / 532.392293180 wall-s before report charges. Program charge then is 2095.814246720 CPU-s / at least 536.132346552 wall-s; remaining shared allowance is at most 141904.185753280 CPU-s / 21063.867653448 wall-s. Final report/render charges are recorded separately in `timing-and-program-accounting.json`. Prior unmetered overhead remains unknown. Budgets were not exhausted.

Heavy work used `nice -n 10`, single-thread BLAS/OpenMP and one native pool requested at 32 workers, supported by 22.56 GB available memory and the declared 256 MiB per-worker estimate. Engine does not return the actual worker count. Starts/calls were sequential, bounded by 60 s per non-fit call and 300 s for the fit. No service, extra worktree, subagent, Engine change or GitHub write was used.

Bound and convergence stops require an owner decision under amendment 2 §5 and joint design §8 before another fit/start/stage. The input corrections and shared dielectric reduction remain retained independent evidence. No EOS impossibility, unique single-ion property, complete physical validation or absorber/stripper-use conclusion follows. Independent delivered review belongs to the parent; manuscript use is not authorized.

Final reporting boundary: **2156.259447720 cumulative CPU-s / at least 591.490587837 active wall-s**. The remaining program allowance is at most **141843.740552280 CPU-s / 21008.509412163 wall-s**, less unknown earlier overhead. The charged precursor block is 756.244886000 CPU-s / 122.965948105 wall-s; its remainder is 7043.755114000 CPU-s / 477.034051895 wall-s. Measured report processing and both render attempts are retained separately; 32 CPU-s / 30 wall-s conservatively charges the remaining short unmetered commands, without duplicating already measured or conservatively charged work.

The notebook source and static HTML were updated. The managed presentation refresh fails because `snakemake` is unavailable in this environment; the project's guarded static HTML render passes with execution disabled, and the five checked new numerical values match the source. No preview service was changed. Independent delivered review remains pending.

Part 1 adds **80 gross executable-file lines** and removes one, within its 180-line ceiling. The binding conservative campaign charge is **625/900** (prior 545 plus 80); the final-tree classifier reports 449 additions/4 removals from the design base, consistent with its exclusion of previously removed revisions. The historical conservative charge is preserved. `../../code-accounting.json` owns the distinction; `../../change-accounting.json` contains the required final source accounting. No test source was added; the pinned native/algebra comparison is the numerical check.
