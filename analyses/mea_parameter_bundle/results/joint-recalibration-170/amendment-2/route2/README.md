# Route 2: release tests pass; the first fit reaches its wall limit

**No fitted Route 2 comparison record is available.** The smaller-d_V F1 SSM+DS mandatory block and both ion dispersions pass all four prescribed start/weight checks. The first 14-coordinate fit, lambda=0 start A, reaches its 300 s wall limit and is terminated by the captured child PID. Its measured charge is 289.631747 CPU-s / 300.112955133 wall-s, including 0.112955133 s termination overhead beyond the limit. No endpoint, iteration count or native residual/Jacobian work count is returned. Starts B and both lambda=0.1 fits remain unrun under amendment 2 section 5.

The release tests are **numerical verification** at the actual declared starts, not fitted parameter identification or physical validation. Predictions on the previously inspected measurement rows are **conditional assessments at those starting records**. The interrupted fit supplies no completed calibration and does not establish an equation-of-state limitation. No new parameter record is adopted.

## Release tests

All matrices are native residual derivatives multiplied by the declared square-root observation weights, in scaled optimizer coordinates. The cutoff is 1e-14 times the largest singular value; the declared condition limit is 10000. Source-increasing R5 a_k has the opposite sign to its native coefficient column; rank and condition are unchanged by that sign. Starting bicarbonate-water is exactly +0.5 for A/B, and B mutual interaction is exactly -1. Those columns alone are excluded from the free-matrix tests; the coordinates remain free in the fits.

| Start | Density weight | Rows | Mandatory free rank | Condition | Augmented free rank | Condition | Projected dispersion rank | Condition |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 0 | 166 | 11/11 | 4243.33872941 | 13/13 | 7804.89559687 | 2/2 | 10.10168821 |
| A | 1 | 178 | 11/11 | 3076.25475378 | 13/13 | 3491.17755113 | 2/2 | 8.07274519 |
| B | 0 | 166 | 10/10 | 2132.21089915 | 12/12 | 6468.29576964 | 2/2 | 14.66806763 |
| B | 1 | 178 | 10/10 | 1543.86275706 | 12/12 | 2296.28558963 | 2/2 | 5.65005523 |

Both dispersion origins are interior. Both dispersions are therefore released together with all 12 mandatory coordinates for the same branch/problem at every fitted density weight. Full singular spectra, weakest directions, active columns, exact unweighted columns and weighted matrices are in [release-tests.json](release-tests.json) and the `information/A` and `information/B` files. The two actual derivative evaluations each include all 178 requested rows; positive-weight subsets give 166/178 rows at lambda=0/1. Every starting row is available. The lambda=1 calculation is an information check, not a fit.

## Matched fits and primary metric

| Density weight | Start | Attempt | Complete endpoint | Common-149 cost |
|---|---|---|---|---|
| 0 | A | Interrupted at wall limit | None | Unavailable |
| 0 | B | Not launched after stop | None | Unavailable |
| 0.1 | A | Not launched after stop | None | Unavailable |
| 0.1 | B | Not launched after stop | None | Unavailable |

The primary lambda=0.1 common-149 cost and its lambda=0 fitted control cannot be reported. No lower-training-cost A/B comparison record can be selected. [endpoints.csv](endpoints.csv) retains all four dispositions. [incomplete-fit.json](lambda-0/F1/A/incomplete-fit.json) records the exact stopping point. There is no completed or usable endpoint document. The original failure traceback mistakenly says no fit was launched; `fit_calls=1`, the elapsed call and `incomplete-fit.json` establish that one fit was attempted. The executable diagnostic now correctly says no subsequent fit was launched.

## Starting values, separated from unavailable fitted results

| Start | Common-149 cost | Pressure contribution | Species contribution | Vinjarapu contribution | Pressure mean absolute relative error, % | Species mean absolute relative error, % | Vinjarapu RMSE, kJ/mol CO2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 160.863262274 | 24.051711172 | 22.248462154 | 114.563088949 | 27.662866 | 8.183326 | 18.097837 |
| B | 882.766472292 | 523.632083924 | 316.441430522 | 42.692957846 | 66.902029 | 33.444708 | 11.027447 |

These are the declared source-chemistry, seed-ion starting predictions, not fit endpoints or the primary comparison metric. The original 149 row identities and weights match exactly. [starting-targets.csv](starting-targets.csv) retains all 178 values at each start; [starting-density.csv](starting-density.csv), [starting-Cp.csv](starting-Cp.csv), and [starting-Jakobsen.csv](starting-Jakobsen.csv) retain the corresponding units, errors and bases. Density is kg/m3; native Cp is J/(mol-feed K), with the source kJ/(kg K) conversion retained separately. No endpoint density, Cp, Arcis, Kiepe or C5 assessment is inferred from these starts.

## Full comparison report availability

| Required report item | Retained evidence or unavailability |
|---|---|
| common-149 cost/contributions | No fitted records; both exact starting values retained |
| pressure/species family errors | Starting values only; no fitted records |
| Vinjarapu/Arcis heat errors | Eight starting Vinjarapu heats available per start; Arcis unrun |
| pooled Jakobsen/restored target errors | All 13 added starting rows available; no fitted records |
| all 103 densities by seven groups | 12 loaded starting densities per start available; remaining 91 and endpoint densities unrun |
| four Cp values and proxy/enthalpy checks | Four starting Cp values per start available; proxy and enthalpy verification unrun |
| direct C5 requests | Unrun; no endpoint; absorber evidence unchanged |
| Kiepe isotherm assessment | Unrun for Route 2; existing unchanged-binary qualification remains separate |
| weighted/scaled ranks and spectra | All four start/weight checks available; endpoint matrices unavailable |
| active bounds and parameter movements | Declared starting bounds retained; no endpoint or fitted movements |
| A/B cost and vector dispersion | Starting values retained; fitted 1e-6 relative-cost diagnostic unavailable |
| CPU/wall/iterations/work counts | One interrupted fit; measured CPU/wall retained; native iteration/evaluation counts not returned |
| secondary union score and six Kim heats | Unrun: union not evaluated, six intervals not qualified, s_H not frozen |
| fixed-record pressure/temperature/concentration and Wagner | Unrun; no comparison record |
| fixed-record corrected Jakobsen, 14 Arcis and 28 Hajj | Unrun; starting Jakobsen ratios are not fixed-record endpoint assessments |
| gas-root falsifier | Unrun; no physical-eligibility conclusion |
| 73-point flash family | Unrun; zero attempted points; no passed/failed/unresolved point classification |
| water and complete serialization replay | Four unchanged-record qualification checks remain passed; new endpoint replay unavailable |

The 20 loaded-density, five unloaded-density, four Cp, water, complete-replay and physical-phase eligibility requirements have not been satisfied by a new candidate. The gas-root falsifier and flash family were not attempted; no stability conclusion follows. Neither the six Kim-Svendsen interval heats nor their frozen s_H scale has been constructed or qualified, because assessment depends on a completed comparison record and further work is halted. No missing value is assigned zero score.

## Inputs, implementation and charges

Authority is [published amendment 2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6204801680), sections 4-6, with the joint design sections 6-8. The live issue and published amendment were read. Source R2/R5, zero shifts, six source/analog ion seeds, and the exact declared five-coordinate interaction vectors define both starts. CO2-water k_p=-0.046416901120577676 and b=-35.66505220645838 K, CO2 dispersion/k=169.21 K, and shared smaller d_V=0.2464540312088979 L/mol / d_T=2436.4423007273617 K remain fixed. Both corrected Jakobsen feeds are 27.14274817 wt%; the combined inorganic-carbon/amine target is unchanged. The shared zero bicarbonate-water reference is retained; +0.5 is solely the declared free interaction starting value.

Engine main commit 84ca269dfa0c7068417a1c4c326acae276d4d965, wheel SHA-256 `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`, Python 3.13.14, NumPy 2.5.4 and SciPy 1.18.1 are pinned. All 12 installed wheel files were byte-compared. The four previously qualified unchanged records are reused. Frozen declarations, source/input hashes and actual starts are retained. Runs used nice 10 and single-thread BLAS/OpenMP. The fit requested 32 native workers from 32 discovered CPUs and 20.74 GB available memory; Engine does not return its actual worker count. The low measured CPU/wall ratio does not establish the cause of the missing endpoint.

The first information attempt returned after 44.521833238 s but its report writer encountered missing direct-row residual metadata; it produced no numerical report. That attempt is retained under `information-attempt-1`, charged once, and corrected before repeating the unchanged declaration. No scientific bound, tolerance, weight, start or model was changed.

[timing-and-program-accounting.json](timing-and-program-accounting.json) owns measured, conservative and cumulative charges, including the failed output attempt and rendering. Earlier unknown overhead remains disclosed and active wall is a lower bound. Route 2 remains inside 15000 CPU-s / 2100 s wall and the shared program inside 144000 CPU-s / 21600 s; the first individual fit exhausted its own wall allowance.

Code additions are 179/200 for part 2 and 804/900 conservatively for the campaign, counting revised/replaced lines without credit. [code-accounting.json](code-accounting.json) records the base and scope. Both changes remain in the existing campaign and observation owners; no local EOS, optimizer or second fit driver was added. The exact metadata failure is checked by constructing all 178 row declarations; no persistent test was added. Parent delivered review and the decision on the stop remain pending. No new scientific call, alternate start or fit follows the stop.

## Final charges and presentation

| Charge | CPU-s | Active wall-s |
|---|---:|---:|
| Route 2 subtotal | 522.989616000 | 528.585377456 |
| Program cumulative | 2790.524753720 | at least 1231.349729583 |
| Remaining Route 2 ceiling | 14477.010384000 | at most 1571.414622544 |
| Remaining shared cap | 141209.475246280 | at most 20368.650270417 |

The subtotal includes measured process/child CPU, the original output-assembly failure, 30 CPU-s / 30 wall-s conservative preparation, and 20 CPU-s / 20 wall-s conservative reporting/checks/commits. Both presentation calls are separately measured and charged. The standard presentation refresh fails because `snakemake` is absent. Static HTML rendering of the updated notebook and home page succeeds through `analyses/render.sh` with execution disabled; no new table, figure or thermodynamic calculation is generated by that render. The Quarto preview service is unchanged. The new report and notebook have not received independent delivered review.
