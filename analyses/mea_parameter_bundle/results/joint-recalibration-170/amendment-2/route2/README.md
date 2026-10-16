# Route 2: native time limit at 81 iterations; comparison incomplete

**The primary lambda=0.1 common-149 cost and the completed lambda=0 control are unavailable.** Restarting lambda=0 A from its declared source/seed start at the new 100-iteration/1200-s limits returns an incomplete vector after **81 iterations**. Whole-training cost is **196.865136591 → 40.5902023581**; its partial common-149 subset cost is **24.2811941137**. The current adopted record's retained **32.05668491** uses a different wheel and declaration: it is a historical reference only, not a ranking. There is no complete A/B record to select at either lambda.

The native time-limit stop requires an owner decision before lambda=0 B, lambda=0.1 A/B or any replay/assessment call. All three later fits remain unrun. **Bound activity alone does not stop these four fits.** This vector is incomplete calibration evidence, not a bound-constrained optimum, physical validation or an adopted parameter set. No equation-of-state limitation follows.

## Authority, fixed declaration and normal return

The [owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6207429019) changes the four comparison fits to 100 iterations, 1200 s native wall and 12000 aggregate CPU-s each, with at most 48000 CPU-s from the selected-route reserve. The existing launcher backstop is 1320 s. The [frozen declaration](lambda-0/F1/A/converge-1/stage6-spec.json) keeps all 14 released coordinates, bounds, starts, observation IDs, weights and thermodynamic inputs unchanged. A starts from its original document, not either partial vector.

Wheel SHA-256 is `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`, merged Engine `84ca269dfa0c7068417a1c4c326acae276d4d965`; all 12 installed files match. Python 3.13.14, NumPy 2.5.4 and SciPy 1.18.1 are verified. Launch is nice 10 with single-thread BLAS/OpenMP and 32 requested native workers. Available memory is 22792073216 bytes, versus 8589934592 bytes for the declared worker estimate. Actual worker count is not returned by Engine.

The [native return](lambda-0/F1/A/converge-1/native.json) is `limit_reached`, usable, with all **166/166 predictions Available**, **82 residual / 64 Jacobian evaluations**, and zero trial failures. Message: `Maximum solver time reached. Total solver time: 4.077778e+01 >= 3.289800e+01.`. The message reports an internal native solver span, not total call wall time. The owner exits 0 and is reaped normally, interrupted=false, after **1248.10051365 wall-s / 7446.787965 CPU-s**. The whole command uses **1248.33090244 wall-s / 7447.008186 CPU-s**. The native call exceeds 1200 s by **48.100513649 s**, but the 1320-s backstop does not fire. Aggregate CPU is measured after normal reaping; its 12000-s margin is **4553.212035 CPU-s**. The driver's exit 1 records the required stop after the clean native return.

The first launch lacked `PYTHONPATH=src` and stopped at import before constructing thermodynamic rows. Its [setup failure](lambda-0/F1/A/converge-1/setup-failure.json) and [0.187377 CPU-s / 0.209009864 s timing](lambda-0/F1/A/converge-1/setup-command-timing.json) are retained and included once in preparation overhead. The successful native launch used the project path.

Fixed inputs remain CO2–water pivot interaction -0.046416901120577676, reciprocal-temperature slope -35.66505220645838 K, CO2 dispersion/k 169.21 K, and shared smaller dielectric coefficients 0.2464540312088979 L/mol and 2436.4423007273617 K. Corrected Jakobsen 011/022 both use 27.14274817 wt% and the pooled inorganic-carbon numerators. No input, bound, weight or release decision changes.

## Four fit dispositions and comparison records

| lambda | Start | Result | Partial training cost | Partial common-149 | Complete comparison cost |
|---|---|---|---|---|---|
| 0 | A | Native time limit at 81 iterations; incomplete calibration | 40.5902023581 | 24.2811941137 | Unavailable |
| 0 | B | Unrun after required non-convergence stop; awaiting owner decision | Unrun | Unrun | Unavailable |
| 0.1 | A | Unrun after required non-convergence stop; awaiting owner decision | Unrun | Unrun | Unavailable |
| 0.1 | B | Unrun after required non-convergence stop; awaiting owner decision | Unrun | Unrun | Unavailable |

The [endpoint table](endpoints.csv) distinguishes partial costs from completed comparison metrics. Lower-training-cost A/B selection and the 1e-6 relative-cost/vector-dispersion diagnostic are unavailable. The original interrupted attempt and the 29-iteration rerun remain historical records in `lambda-0/F1/A/` and `rerun-1/`; neither supplies a comparison endpoint.

## Partial calibration costs and family errors

Costs are dimensionless, one half the sum of squared declared weighted residuals. The exact unchanged 149 IDs and weights are verified against the frozen base. Reconstructing the full objective gives 40.59020235812788, versus native 40.590202358127875: one ulp, 7.105427357601002e-15. This is retained-array arithmetic, not serialization replay.

| Family | Rows | Start cost | Partial cost | Partial mean absolute relative error, % |
|---|---|---|---|---|
| Common-149 pressure | 47 | 24.0517111716 | 6.63091194532 | 12.3906185005 |
| Common-149 species | 94 | 22.2484621542 | 16.9797004741 | 7.17742618759 |
| Common-149 Vinjarapu heat | 8 | 114.563088949 | 0.670581694244 | 1.34808361727 |
| Restored species | 7 | 2.90846901287 | 2.47797629947 | 9.0995149244 |
| Pooled Jakobsen ratios | 6 | 29.6415203756 | 11.519375472 | 17.2389630897 |
| Equilibrium Cp | 4 | 3.4518849279 | 2.31165647297 | 1.92682550827 |

The eight Vinjarapu heats have partial RMSE **1.48858761067 kJ/mol CO2**. Pressure/species errors are **12.3906185005% / 7.17742618759%**. The [per-target table](lambda-0/F1/A/converge-1/target-costs.csv) retains every prediction, observed value, weight, residual, signed error and contribution; [family costs](lambda-0/F1/A/converge-1/family-costs.csv) retain the grouping. All six Jakobsen and seven restored targets are incomplete calibration, not fixed-record assessment. Arcis is unrun.

## Parameters, movements, active bounds and conditioning

Full weighted/scaled rank is **14/14**, condition **13247.5500859**. Excluding five active columns gives **9/9**, condition **831.249742487**. The native projected-gradient norm is **2.10700056805**, against 1e-8; covariance is `not_converged`. No conditional uncertainty is claimed. Full/free spectra, weakest directions, mandatory block and projected two-dispersion results are in [identification.json](lambda-0/F1/A/converge-1/identification.json). The full condition exceeds the 1e4 release threshold; the free condition is below it. The unchanged starting release decision remains passed; no endpoint rank deficiency occurs.

| Coordinate | Unit | Start | Partial | Movement | Bound |
|---|---|---|---|---|---|
| pair/carbamate-anion/water/k_ij | dimensionless | 0.134080741317 | -0.202719733667 | -0.336800474984 | Interior |
| pair/protonated-monoethanolamine/water/k_ij | dimensionless | -0.379554080066 | -0.152249129162 | 0.227304950904 | Interior |
| pair/bicarbonate-anion/water/k_ij | dimensionless | 0.5 | 0.5 | 0 | upper |
| pair/carbamate-anion/protonated-monoethanolamine/k_ij | dimensionless | -0.707285890215 | -1 | -0.292714109785 | lower |
| pair/protonated-monoethanolamine/water/k_ij/reciprocal_temperature_slope | K | -112.567750584 | 36.9034558902 | 149.471206474 | Interior |
| component/protonated-monoethanolamine/segment_diameter | angstrom | 3.563 | 5.51743301647 | 1.95443301647 | Interior |
| component/carbamate-anion/segment_diameter | angstrom | 3.5605 | 5.8 | 2.2395 | upper |
| component/protonated-monoethanolamine/born_diameter | angstrom | 3.563 | 5 | 1.437 | upper |
| component/carbamate-anion/born_diameter | angstrom | 3.5605 | 3.62897938162 | 0.0684793816162 | Interior |
| reaction:R5:correlation:a_k | K | 2677.91 | 2568.56004544 | -109.349954556 | Interior |
| reaction:R2:enthalpy_shift | J/mol | 0 | -10000 | -10000 | lower |
| reaction:R5:enthalpy_shift | J/mol | 0 | -8392.06021931 | -8392.06021931 | Interior |
| component/protonated-monoethanolamine/dispersion_energy_over_k | K | 228.71 | 251.302802793 | 22.5928027927 | Interior |
| component/carbamate-anion/dispersion_energy_over_k | K | 533.11 | 168.034884166 | -365.075115834 | Interior |

A size coordinate carries its packing and Debye–Hückel diameters at 0.88 times segment diameter. The full partial parameter record preserves these linked values. All 14 gradients, including the source R5 coordinate sign, are in [parameters-and-gradients.csv](lambda-0/F1/A/converge-1/parameters-and-gradients.csv). Below, g_q is J^T r in the scaled optimizer coordinate; g_p is its derivative per displayed physical unit. These are gradients of the retained training objective.

| Active bound | Value | Side | g_q | g_p per physical unit |
|---|---|---|---|---|
| pair/bicarbonate-anion/water/k_ij | 0.5 | upper | 0.0319591960294 | 3.19591960294 |
| pair/carbamate-anion/protonated-monoethanolamine/k_ij | -1 | lower | -0.0239158824269 | -2.39158824269 |
| component/carbamate-anion/segment_diameter | 5.8 | upper | 0.448229029215 | 4.48229029215 |
| component/protonated-monoethanolamine/born_diameter | 5 | upper | -0.0108382835599 | -0.108382835599 |
| reaction:R2:enthalpy_shift | -10000 | lower | -0.274943154841 | -0.000109977261936 |

R2/R5 linked shifts are **-10000 / -8392.06021931 J/mol**, pivot 313.15 K. Unshifted R5 a_k is **2568.56004544 K**, movement **-109.349954556 K** from source 2677.91 K. The Engine-serialized linked R5 coefficients are a_k=**2130.21235992 K**, b=**1.78670100758**. The unshifted box constrains the unshifted coefficient, not this composed sum. These are partial parameter estimates, with no identification or optimum claim.

## Cp, densities and physical eligibility

The four Hilliard values use the frozen 7 mol MEA/kg-water feeds, 101325 Pa, and the 1e-6 unloaded CO2 proxy. Equilibrium Cp is returned in J/(mol-feed K); the retained feed mass and amount convert it to the source mass basis. These native fit predictions have not passed proxy, centered-enthalpy or frozen-composition verification.

| T, K | Loading | Observed kJ/(kg K) | Partial kJ/(kg K) | Signed error, % |
|---|---|---|---|---|
| 318.15 | 0.0 | 3.7195 | 3.84277891451 | 3.31439479786 |
| 318.15 | 0.358 | 3.3675 | 3.42372348313 | 1.66959118423 |
| 353.15 | 0.0 | 3.8566 | 3.83152349216 | -0.650223197679 |
| 353.15 | 0.358 | 3.4707 | 3.39874916634 | -2.0730928533 |

Only three of four partial Cp errors lie within 3%; the unloaded 318.15 K error is +3.3143948%. This partial vector therefore misses the Cp target, independent of its uncompleted numerical/phase checks. It is not a physically eligible completed record. [Cp.csv](lambda-0/F1/A/converge-1/Cp.csv) retains both bases. No new density calculation follows the stop.

| Density group | Requested rows | Evaluated on partial | Requirement |
|---|---|---|---|
| Loaded fit: 30 wt%, 25/50/70 C | 12 | 0 | <=2 kg/m3 |
| Loaded temperature: 30 wt%, 40/80 C | 8 | 0 | <=2 kg/m3 |
| Unloaded stage-2 fit: 30 wt% | 3 | 0 | <=0.5 kg/m3 |
| Unloaded temperature: 30 wt%, 40/80 C | 2 | 0 | <=0.5 kg/m3 |
| 30 wt%, loading 0.5 | 3 | 0 | Report only |
| Loaded 20/40 wt% | 45 | 0 | Report only |
| Unloaded non-30 wt% | 30 | 0 | Report only |

All 103 endpoint density errors remain unavailable, including the 20 loaded and five unloaded pass rows. Starting density values remain separate in `starting-density.csv`; they do not fill endpoint cells.

| Requirement | Limit | Evidence | Disposition |
|---|---|---|---|
| 20 loaded densities | Every absolute error <=2 kg/m3 | 0/20 evaluated on partial; unassessed | Unassessed |
| 5 unloaded densities | Every absolute error <=0.5 kg/m3 | 0/5 evaluated on partial; unassessed | Unassessed |
| 4 Cp targets | Every absolute relative error <=3% | Partial errors +3.3143948%, +1.6695912%, -0.6502232%, -2.0730929%; 3/4 within target; numerical checks unrun | Partial vector misses one target |
| Water gates | D section 6 / adopted water limits | Prior unchanged-water qualification passed; new partial record not assessed | Unassessed on partial |
| Complete replay / derivatives / closure | D section 8 | Unrun; returned predictions and array cost are not serialization replay | Unassessed |
| No stable ionic gas root | D section 7 fixed state and witness | 0 attempted states | Unassessed |
| 73-point flash family | Zero failed and zero unresolved points | 0 attempted points per comparison; missing evidence does not count as zero failures | Unassessed |
| Complete calibration | Native termination within approved limits | limit_reached after 81 iterations | Not satisfied |

There are zero attempted gas-root states and zero attempted flash-family points per lambda comparison. Missing phase evidence never becomes zero failed points. No global stability, absorber/stripper use or physical validation claim follows.

## Full amendment-2 section-5 reporting availability

| Required item | Evidence or precise gap |
|---|---|
| common-149 cost/contributions | A partial 24.2811941137, with pressure/species/heat costs; both completed comparison records and primary metric unavailable |
| pressure/species family errors | A partial mean absolute relative errors 12.3906185% / 7.17742619%; all target values retained |
| Vinjarapu/Arcis heat errors | Eight partial Vinjarapu heats, RMSE 1.48858761 kJ/mol CO2; 14 Arcis unrun |
| pooled Jakobsen/restored target errors | All six pooled ratios and seven restored species available at partial; per-row errors retained |
| all 103 densities by seven groups | No partial endpoint density evaluations; all 103 endpoint rows unrun |
| four Cp values and proxy/enthalpy checks | Four native partial predictions retained; proxy, frozen-composition Cp and enthalpy re-solves unrun |
| direct C5 requests | Unrun; no complete record; absorber evidence not refreshed |
| Kiepe isotherm assessment | No new partial assessment; unchanged neutral-binary qualification retained separately |
| weighted/scaled ranks and spectra | Full 14/14; free 9/9; full/free spectra, mandatory block and projected dispersions retained |
| active bounds and parameter movements | All 14 values, start movements and gradients retained; five active bounds |
| A/B cost and vector dispersion | Unavailable: no complete A or B; B not launched |
| CPU/wall/iterations/work counts | 7447.008186 command CPU-s; 1248.33090244 wall-s; 81 iterations; 82 residual / 64 Jacobian evaluations; zero trial failures |
| secondary union score and six Kim heats | Unrun; union not evaluated; six intervals unqualified; s_H not frozen |
| fixed-record pressure/temperature/concentration and Wagner | Unrun; no completed comparison record |
| fixed-record corrected Jakobsen, 14 Arcis and 28 Hajj | Unrun; six training ratios are partial calibration, not fixed-record assessment |
| gas-root falsifier | Zero attempted states; stable ionic gas-root requirement unassessed |
| 73-point flash family | Zero attempted points for each lambda comparison; no pass/fail/unresolved classification |
| water and complete serialization replay | Frozen water qualification passed; no new partial-record water/replay assessment |

D section 7 fixed-record pressure/temperature/concentration groups, Wagner, corrected Jakobsen, 14 Arcis and 28 Hajj remain unrun, as do direct C5 requests. No absorber-owned evidence is refreshed. The secondary union has not been scored; its ordered union, six Kim intervals and frozen s_H remain unavailable. No missing quantity is assigned zero cost.

The prior unchanged-binary qualification is available separately in [qualification-kiepe-isotherm-errors.csv](qualification-kiepe-isotherm-errors.csv); it is not a new assessment of this incomplete reactive vector. Its qualified wheel and fixed binary match the declared neutral inputs.

| Kiepe qualification T, K | Rows | Mean absolute relative error, % |
|---|---|---|
| 313.2 | 12 | 1.50120691391 |
| 353.11 | 9 | 3.82609450155 |
| 373.26 | 12 | 0.972617820457 |
| 393.17 | 6 | 6.64561194293 |

## Release tests


All matrices are native residual derivatives multiplied by the declared square-root observation weights, in scaled optimizer coordinates. The cutoff is 1e-14 times the largest singular value; the declared condition limit is 10000. Source-increasing R5 a_k has the opposite sign to its native coefficient column; rank and condition are unchanged by that sign. Starting bicarbonate-water is exactly +0.5 for A/B, and B mutual interaction is exactly -1. Those columns alone are excluded from the free-matrix tests; the coordinates remain free in the fits.

| Start | Density weight | Rows | Mandatory free rank | Condition | Augmented free rank | Condition | Projected dispersion rank | Condition |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 0 | 166 | 11/11 | 4243.33872941 | 13/13 | 7804.89559687 | 2/2 | 10.10168821 |
| A | 1 | 178 | 11/11 | 3076.25475378 | 13/13 | 3491.17755113 | 2/2 | 8.07274519 |
| B | 0 | 166 | 10/10 | 2132.21089915 | 12/12 | 6468.29576964 | 2/2 | 14.66806763 |
| B | 1 | 178 | 10/10 | 1543.86275706 | 12/12 | 2296.28558963 | 2/2 | 5.65005523 |

Both dispersion origins are interior. Both dispersions are therefore released together with all 12 mandatory coordinates for the same branch/problem at every fitted density weight. Full singular spectra, weakest directions, active columns, exact unweighted columns and weighted matrices are in [release-tests.json](release-tests.json) and the `information/A` and `information/B` files. The two actual derivative evaluations each include all 178 requested rows; positive-weight subsets give 166/178 rows at lambda=0/1. Every starting row is available. The lambda=1 calculation is an information check, not a fit.

## Native history and reproducibility

The [81-iteration history](lambda-0/F1/A/converge-1/iteration-history.csv) includes every native entry and rejected trial. Entry zero is the declared start; native entry durations are not total call wall time. The final five costs are 96.0731671279, 91.5948919183, 43.0208788258, 40.9876576761 and 40.5902023581. No monotone trajectory or convergence is inferred from accepted decreases. Matplotlib is absent from the pinned environment. The report uses scalar/property/availability tables and retains the exact history; a convergence plot would not turn this time-limited iterate into a comparison endpoint.

## Charges, code and next owner decision

The [accounting file](timing-and-program-accounting.json) preserves the prior conservative reservation, adds the complete command once, reserves 120 CPU-s/120 active wall-s for continuation preparation/reporting/checks/commits, and reserves another 60 CPU-s/60 active wall-s for presentation, checked against measured presentation work. The initial import failure is included in that overhead, not charged again. Native CPU is a subset of command CPU. The 32-CPU upper-bound reservation for the original interrupted worker run remains; the new complete measurement does not erase it. Earlier unmetered overhead remains disclosed, and program active wall is a lower bound.

Including these conservative preparation/reporting and presentation charges, Route 2 is **19732.208820256 conservative CPU-s / 2442.685345839 wall-s**; the program is **21999.743957976 conservative CPU-s / at least 3145.449697966 wall-s**. Program remaining is **122000.256042024 CPU-s / at most 18454.550302034 wall-s**. The four-fit reserve has **40552.991814000 CPU-s** left; assessment/reporting has **2714.799365744 CPU-s** left. These remaining amounts do not override the non-convergence stop.

The owner-policy launcher change adds two executable lines and removes two. Conservative code totals are **187/200 part 2 and 812/900 campaign**. No new persistent executable, test, optimizer or EOS is added. Final change accounting is retained in `converge-change-accounting.json` against the active design base `6c8d20073fd0e5fda8dd323a51f55551d12b7486`.

The numerical run is retained in commit `dd7a1a9`. Independent delivered review and investigator promotion have not occurred. The owner must decide the non-convergence stop before any remaining fit or thermodynamic assessment. Route 1 remains stopped. No subagent, Quarto preview action, push, merge or GitHub write occurs.

The presentation-only refresh reports missing `snakemake`. Both guarded HTML renders succeed with `--no-execute`: notebook and home page. Actual presentation is **50.240062 CPU-s / 45.470171144 wall-s**, inside the charged 60/60 reservation. The [render timing](converge-presentation-timing.json) retains each command and outcome. No numerical calculation or preview-service action occurs.
