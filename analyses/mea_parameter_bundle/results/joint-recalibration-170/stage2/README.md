# Stage 2 joint recalibration, 13 October 2026

Stage-2 implementation and numerical evidence are complete. Both MEA–water fits and both owner-approved CO₂–water reciprocal-temperature fits converge and pass their replay, derivative and equilibrium checks. All 39 Kiepe rows remain included. The binary records are frozen inputs for stage 3; the CO₂–water endpoint is explicitly provisional. Nothing is adopted. Independent delivered review remains with the parent task.

The accepted basis is [#170 §2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000594), [§8 controls](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000919), the [subset-start amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158350746), and the superseding [owner slope decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158787639). No new physics, rows, tolerances, bounds or budget extensions were selected by this implementation.

**MEA–water.** The unchanged comparison endpoint is A: constant $k_{ij}=-0.0843938800264992$. B gives −0.08439384952694257. Costs fall from 102.57716039244268 and 788.2827447533418 to 91.84540850646788 and 91.84540850692042; relative endpoint-cost difference is 4.92724×10⁻¹². Both lie inside −0.5…0.5, with no active bound. The previous #160 value is −0.08031722618968729; the earlier all-Cai value is −0.07352749874985018.

The objective contains both targets at all 25 internal Cai rows (12 at 101330 Pa and 13 at 66660 Pa), plus three unloaded Amundsen density targets. Boiling-temperature and vapor-water fraction difference scales are 1 K and 0.01, each weight 1. Density scale is 0.5 kg/m³ with weight 1/3 at each fitted row. The Cai interval is 362.81–431.85 K. Pure endpoints are excluded as declared; these are temperature/composition errors at fixed measured pressure.

| Pressure, Pa | Rows | Temperature MAE / maximum / RMSE, K | Vapor-water fraction MAE / maximum / RMSE | Pressure-level cost |
|---:|---:|---:|---:|---:|
| 101330 | 12 | 1.514611 / 3.234746 / 1.721445 | 0.01407445 / 0.02820476 / 0.01728448 | 35.70545157 |
| 66660 | 13 | 1.432137 / 3.726595 / 1.820914 | 0.01514660 / 0.06352112 / 0.02289486 | 55.62357017 |

**All five unloaded density rows.** Exact zero carbon, 30 wt% MEA on a CO₂-free basis, assumed 100000 Pa, retained water/amine protonation. These unchanged values belong to the MEA–water endpoint; the carbon-free face does not use the CO₂–water interaction.

| Row | Temperature, K | Observed, kg/m³ | Predicted, kg/m³ | Signed error, kg/m³ | Role | Within 0.5 kg/m³ |
|---|---:|---:|---:|---:|---|---|
| AMU-DENS-002 | 298.15 | 1010.6 | 1009.907212 | -0.692788 | Fit | No |
| AMU-DENS-009 | 313.15 | 1003.4 | 1003.287419 | -0.112581 | Assessment | Yes |
| AMU-DENS-016 | 323.15 | 998.1 | 998.099992 | -0.000008 | Fit | Yes |
| AMU-DENS-023 | 343.15 | 985.8 | 986.342794 | +0.542794 | Fit | No |
| AMU-DENS-030 | 353.15 | 979.4 | 979.927109 | +0.527109 | Assessment | No |

The three finite misses remain reported. The all-five hard density pass belongs to the completed stage-6/7 candidate, after the provisional ions are refreshed; it is not a stage-2 stopping condition. Both withheld temperatures are same-source assessment, not independent validation.

**CO₂–water progression.** Original A = −0.02424240226792941 stopped at `kiepe-313.20-10`; the declared vapor branch was unavailable. Original B = 0.013262879176919628 failed earlier at row 09 in the retained diagnosis. Original qualification, including unattempted rows, remains under `co2-water/original-starts/` and `co2-water/A/`; the original stage-level `failure.json`, `spec.json`, `summary.json` and `timing.json` are historical records.

The eight-row 313.20 K subset fit (rows 02–09) generated A = −0.046912921483332176; B was A −0.002. Both qualified cold on all 39 rows. This subset generated starts only. `co2-water/start-generation/` retains its native fit, source identity and timing.

The two full constant-interaction fits then stopped at 40 iterations: A $k_{ij}=-0.04559724536444507$, cost 1.2558811832335612, 26 failed trials; B −0.045597450607821735, cost 1.2559043043780767, 27 failed trials. Their returned endpoints contain all 39 rows, but neither converged. Trial failures involve 313.20 K rows 12/13. No constant endpoint was frozen; no diagnostic slope fit ran from those unfinished records. `co2-water/amendment/` preserves round 2, including its original interpretation.

The owner then authorized two coordinates with

$$k_{ij}(T)=k_{ij}(313.15)+b\left(1/T-1/313.15\right),$$

with $T$ in K and $b$ in K. The constant coordinate has bounds −0.5…0.5 and scale 0.01; the slope family `k_ij_reciprocal_temperature_slope` has bounds −1000…1000 K and scale 10 K. Formal starts are A = (−0.04560, 0) and B = (−0.04690, 0). The updated amendment declaration has one CO₂–water case; its earlier version remains frozen in the round-2 result directory.

| Formal start | Initial cost | Replayed endpoint cost | $k_{ij}(313.15)$ | $b$, K | Iterations | Failed trials |
|---|---:|---:|---:|---:|---:|---:|
| A | 1.25619165897 | 0.0264817604505262 | -0.04641690132412801 | -35.66505265248939 | 4 | 0 |
| B | 1.43852289509 | 0.0264817604505243 | -0.04641690112057768 | -35.66505220645838 | 4 | 0 |

Both starts and both endpoints have all 39 observations available, five residual evaluations and six Jacobian evaluations per fit, and no active bounds. B is selected by the lower **cold-replayed** objective. Native A is cheaper than native B by 2.18×10⁻¹⁵; cold replay reverses that ordering at rounding precision. The retained relative replayed-cost difference is 7.33671e-14, well below 10⁻⁶. The vector differences are also retained; selection does not establish parameter uniqueness.

**Pressure errors by isotherm.** Mean / maximum absolute relative error, percent, against every declared Kiepe Table 1 nonzero-CO₂ row. Pressure units are Pa, with natural-log ratio residual and weight 1. Previous #160 values are historical retained predictions with old water and association, not a current-wheel replay. The constant column is the lower-cost unfinished constant A; both constant starts and both slope starts are preserved in `co2-water/isotherm-comparison.json` and `co2-water/all-row-results.csv`.

| Temperature, K | Rows | Previous #160, % | Constant A at limit, % | Provisional slope B, % | Effective slope $k_{ij}(T)$ |
|---:|---:|---:|---:|---:|---:|
| 313.20 | 12 | 59.3384 / 346.5507 | 3.1909 / 11.3068 | 1.5012 / 2.6591 | -0.04639872 |
| 353.11 | 9 | 10.0934 / 12.7218 | 19.2082 / 24.9227 | 3.8261 / 5.5775 | -0.03352830 |
| 373.26 | 12 | 19.7573 / 24.2869 | 26.3691 / 32.8308 | 0.9726 / 2.7998 | -0.02807579 |
| 393.17 | 6 | 24.0965 / 36.1706 | 27.7912 / 41.4272 | 6.6456 / 11.3361 | -0.02323716 |

The slope separates the cold-isotherm interaction from the hotter-isotherm correction. This is calibrated agreement at 313.20–393.17 K, not evidence of transfer to unmeasured compositions, an absorber or a stripper. The largest slope error is still 11.3361% at 393.17 K. No additional accuracy cutoff was imposed.

**Numerical verification.** MEA–water replay relative cost difference is ≤1.13×10⁻¹³ and weighted-row difference ≤2.76×10⁻¹¹. Its centered checks at optimizer steps 0.01/0.005 pass for boiling temperature, vapor fraction and reacting density. Material/charge errors are ≤1.15×10⁻¹⁵ / 1.08×10⁻¹⁵ mol; source-mass closure is ≤7.80×10⁻¹⁷ kg. Unloaded carbon is exactly zero. Rounded EOS masses give a separately retained ≤8.50×10⁻⁹ kg difference.

For both CO₂–water endpoints, serialization replay preserves observation IDs and the frozen definitions. The largest relative cost difference is 6.79×10⁻¹³ and largest weighted-row difference 1.18×10⁻¹³, against 10⁻⁸ limits. Both coordinates pass centered re-solves at optimizer steps 0.01 and 0.005: physical steps 0.0001/0.00005 for $k_{ij}$ and 0.1/0.05 K for $b$. Sixteen representative comparisons per endpoint cover both coordinates, both steps and the first pressure observation at each isotherm. Maximum relative derivative error is 3.84×10⁻⁷, below 10⁻⁵; the 10⁻⁸ absolute near-zero rule and roundoff evidence are retained. All 39 shifted residual rows are retained at each step.

All 39 endpoint states retain raw equilibrium residuals, material/charge/source-mass balances, phase amounts/compositions/densities, nonnegative returned reduced Hessian minima, and positive phase pressure-density derivatives. Maximum raw equilibrium residual across A/B is 1.07470×10⁻¹³, below the native 10⁻¹⁰ row tolerance; minimum pressure-density derivative is 563.84 Pa/(mol/m³). Independent direct EOS evaluation at those returned states gives maximum absolute pressure closure 1.07834×10⁻⁵ Pa. `phase-root-evidence.json` retains both phases at every row. The declared vapor is dense at 313.20 K row 13; density alone is not treated as branch failure.

These are checks of the returned declared roots and local equilibrium, not a global phase-stability search or mixture critical-locus determination. Stable-root counts and mechanical-class labels are unavailable for these observations; positive EOS derivatives are evaluated explicitly. Both weighted optimizer and native physical Jacobians, singular spectra, gradients, rank-two covariance, bounds, and weakest directions remain retained. The selected optimizer condition number is about 4.94. Native rank cutoff and actual worker count are not returned. Covariance holds branch, inputs, weights and source assumptions fixed and assumes independent errors with a regular local linearization; it does not include full water, chemistry, composition, dielectric or model-form uncertainty.

**Budgets and execution.** Round 1 charged 157.473325 CPU-s / 137.025568 active wall-s, including the prior declaration check; round 2’s summary is cumulative at 406.135343 CPU-s / 159.585256 wall-s, hence its increment is 248.662018 CPU-s / 22.559688 wall-s. These records are preserved. The separate start-generation fit records 1.434069 CPU-s / 1.439403 wall-s; bounded diagnosis and scratch slope fits remain distinct from formal calibration.

This additional formal round used **76.925783 CPU-s / 37.936401 wall-s**, including direct pressure closure, within the authorized **600 CPU-s / 300 s wall**. Lightweight table/hash reporting adds 0.006902 CPU-s / 0.006905 wall-s. The formal-round cumulative total is 483.061126 CPU-s / 197.521657 wall-s, before that separately stated reporting and start-generation work. All calls were sequential, at `nice -n 10`, with single-threaded libraries. One native row pool requested 32 workers from 32 CPUs and 23.03 GB available memory; actual count is not returned. Each fit had at most 40 iterations / 90 s wall, every non-fit call at most 60 s. No call was interrupted. Per-call CPU, wall, host load, iteration and evaluation counts are retained.

**Frozen stage-3 inputs.** `frozen-inputs.json` contains the paths, exact edges, hashes, source/input references and intended stage-3 scope. It points to existing endpoint files; no duplicated selected parameter document is created.

- MEA–water A, $k_{ij}=-0.0843938800264992$: `neutral-mea-water/A/parameters.json`, SHA-256 `36c827bdb5e8b27997f3bc82439ef22d70f7fe8648526e0aa2ac1b6079e6d237`.
- Provisional CO₂–water B, $k_{ij}(313.15)=-0.046416901120577676$, $b=-35.665052206458377$ K: `co2-water/slope/co2-water/B/parameters.json`, SHA-256 `b1ec1ddc22abe5ced8d08116fc91a7b3da1361864db1b34c33dda121b642a5e2`.
- Six association edges, SHA-256 `2fd9b2839ac8ba2a142eeefcc3525135c9c17c724b9ce24d02c0dad381791b62` over the canonical JSON encoding declared in `frozen-inputs.json`. They are byte-equivalent as data in the selected MEA–water and CO₂–water records: MEA self 2586.3 K / 0.036287; water self 1756.6497964508999 K / 0.0376197279502706; both CO₂–water reciprocal edges 878.3248982254499 K / 0.0376197279502706; both MEA–water reciprocal edges use the retained Engine-owned Wolbach–Sandler combining declaration. No association coordinate was fitted.
- Adopted water input SHA-256 `59acacc310a6dbea73b33599e9fdca3a474e4eccf12ccd139c27816cbef75a7f`; fixed pure-MEA/topology and source chemistry stay in the record lineage. Stage 3a will re-estimate both provisional CO₂–water coordinates with CO₂ dispersion and the R5 reference coefficient, retaining every Kiepe row.
- Engine main `36485a88`, wheel SHA-256 `da5a2b65668ab5647e51b917a659614bdcb4afbe7e5c3149aee2294b86a4c1bd`; installed package bytes were verified against that immutable wheel. Python 3.13.14, NumPy 2.5.4, SciPy 1.18.1, `tmp/stage2/venv`; no Engine source imports.
- Formal declaration SHA-256 `6d3bac18fefbc725d4aaeac36fbb80ee99a52decab7d4407b5c9c779cd741408`; full source-row, state-packet, chemistry and caloric hashes are in `co2-water/slope/inputs.json` and `frozen-inputs.json`.

**Evidence and limits.** The binary errors are conditional calibration; the two withheld unloaded temperatures are conditional same-source assessment; replay, centered derivatives, closure and root checks are numerical verification. No independent physical validation, unique ion identification, parameter adoption or absorber/stripper qualification is established. Ion seeds, trace-ion assumptions, source chemistry and fixed water remain the declared conditions. This implementation used the accepted design and retained diagnosis; no new literature judgment was made. The worktree has no `literature/` shelf or journal preference files. The original paper reads and locators are recorded in the accepted design and diagnosis, rather than claimed as new reads here.

Only the incomplete-fit stop in `fit_campaign.py` changed executable code in this round: one replacement line, with no new executable lines in observations, EOS or fitting algorithms. Repository accounting against `6c8d20073fd0e5fda8dd323a51f55551d12b7486` reports 294 gross added executable lines and 3 removed. The task supplied 326 pre-round lines; conservatively charging this replacement as one more gives **327 of 350**. The difference between the supplied baseline and the accounting classifier is stated rather than used to claim extra capacity. Input/result JSON/CSV and the inert historical diagnostic text are separate retained evidence. No new tests were added; the required numerical comparisons catch the declared scientific errors.

Notebook, manuscript and selected-current record were not edited. No push, GitHub write, subagent or worktree was created. Independent delivered review and later notebook integration remain with the parent task.
