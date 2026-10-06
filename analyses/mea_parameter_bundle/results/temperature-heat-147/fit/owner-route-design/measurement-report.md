# Measurement of the #147 owner-reuse design

The existing owners can express the corrected eight-fit experiment. The concrete
diff drafts require **554 gross added executable-file lines**, giving a proposed
cumulative ceiling of **1,120 = 566 + 554**. This draft is larger than the retired
398-line remaining-work projection by **156 lines**. It is a measured candidate,
not a proof that 554 is the smallest possible implementation.

The numerical work is feasible within the remaining cumulative allowance on the
retained timing evidence, subject to the new complete timing check. The matching
fixed-dispersion history gives about **13,022 s** including fits, rescores,
assessment and the recovery check. A conservative envelope gives **30,693 s**.
The largest historical-count per-fit projection is **2,297 s**, leaving only
**103 s** below the 2,400 s external cap. No fit result, physical validation or
adoption follows from these estimates.

## Authority and measurement boundary

The governing instruction is the [2026-10-06 recovery decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6026786257).
The [corrected-input amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6026191670)
and [Ready review](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6026371945)
keep chemistry, source inputs, starts, weights, eight fits, limits and the
50,400 s cumulative ceiling fixed. The full issue body and 23 comments were
read. Their captured JSON is `issue-147.json` beside this report.

The measured checkout is branch `work/147-heat-temperature`, HEAD
`b10339d8ec0335831f335aebd93d130fa81c510f`. The historical accounting base remains
`76ea465fe1ede72257a809d04fc986489c5267f3`. The current 566 gross additions include
retired code and its repair; deleting it does not refund those additions.

Only `/tmp/147-owner-route-design/` was written. The generated drafts were
parsed as Python, but neither imported nor executed. The installed-wheel
inspection read callable signatures only. Retained-value checks verified four
input hashes, the exact CSV/JSON target membership and the eight admitted heat
rows. All checks used `agent-heavy --max 2G --timeout 10m`, with OpenMP,
OpenBLAS and MKL threads set to one. No fit, new equilibrium calculation,
commit, GitHub write, notebook change or parameter adoption was performed.

The worktree does not contain `literature/README.md`. This report inherits the
reviewed source choices and engineering limits from #147; it makes no new
literature-backed judgment about the laws, uncertainties or model adequacy.

## Files and parameterization

1. `temperature-reanchor-140/low-temperature-fit.py` remains the native fit,
   export and rescore owner. An explicit `--issue147` binding selects #147's
   immutable wheel, corrected inputs, physical calorics, frozen reaction file,
   permitted forms and output paths. Default #140 input paths, menu, calls and
   historical method remain available. `shared_evaluation.py` needs **zero**
   added lines and continues to own normalization, construction of the
   pressure/species problems, snapshots and bounded endpoint solving.
2. `temperature-reanchor-140/assessment.py` remains the selection and assessment
   owner. Its #147 binding chooses independently within the no-heat and heat
   branches, assigns heat to primary and no-heat to control, consumes corrected
   packet observations, and retains the existing canonical/Wagner scoring.
   Native fixed-pressure heat is a #147 branch in this owner; the historical
   #140 bubble-endpoint/ideal-feed calculation remains historical.
3. Delete the live `temperature-heat-147/fit/timing.py` execution path: **80
   removed lines, no addition credit**. Retain its measured JSON and exact
   producer through Git history or an explicitly historical archive. Treat
   `remaining-code-measurement.md` and its 398-line projection as superseded
   measurement evidence, not an execution plan.

The fit binding uses:

- `final-rerun/training-inputs.json`, SHA-256 `a063148a…`: 83 states and 141
  targets, with exact membership checked against `strict141-targets.csv`,
  SHA-256 `b2c63743…`. The retained fit input JSON already contains the source
  corrected feeds and starts; no second CSV-to-problem converter is needed.
- Frozen restored-source physical record `7e9e3f02…` and campaign reactions
  `c1cb5c74…`; no #140 finalist or #160 record initializes the fit. The physical
  export binds the campaign reaction companion by hash, and subsequent owner
  evaluation consumes that companion. Its inherited reaction fields must not
  be presented as a standalone #147 chemistry declaration.
- Physical calorics `c94d504e…`, using existing `thermal.record()`, supplied to
  both `Mixture` and native `regression.fit(..., thermochemistry=...)`. Supplying
  calorics to the presolve model alone would leave the heat objective without
  its fixed physical record.
- The installed affine coordinate declaration
  `coordinate(params, [(family, pair, 1.0)], origin=..., scale=..., bounds=...)`.
  Coefficient 1 preserves the previously qualified map. The default #140 call
  remains in its existing branch.
- Exactly eight Vinjarapu rows selected by `role_147 == 'heat_calibration'`.
  Each uses native signed `addition_enthalpy`, difference residual and its
  printed `uH_J_per_mol_CO2`; initial loading is exactly zero. Replicates and
  their individual scales remain separate observations.
- Four structures: constant/no-heat, slope/no-heat, constant/heat and slope/heat,
  each with starts 1 and 2. Every fitted coordinate retains the §7 bounds and
  scales. Neither source reaction nor CO2 dispersion becomes a free coordinate.

All summaries, exported parameter files, heat rescoring, selected files,
freeze and assessments are directed under `results/temperature-heat-147/fit/`.
Ignored caches use `results/runs/temperature-heat-147/fit/`. The thermal and
reaction bindings are included in execution identities; the old generic
parameter fingerprint alone does not describe the new heat comparison.

## Gaps in the owners

The existing fit loop has the correct four intercepts, optional existing slope,
two starts, bounds, native optimizer, iteration limits, export, parameter reload,
pressure/species rescore, active-bound reporting and full Jacobian retention.
It does not need another optimizer or duplicated pressure/species mapping.

Its remaining #147 work is the explicit input/output binding; updated affine
coordinate call; native heat declarations and thermochemistry; variable 141/149
row counts; heat family cost and row outputs; and heat rescoring for all eight
fits, including the no-heat controls. The latter is a comparison after fitting,
not an added control objective. Separate per-family costs remain sums of
half-squared native weighted residuals, with no family-count normalization.

The assessment owner's existing selection must stop when **any** prespecified
form is incomplete or its starts disagree. Its historical behavior permits
selection from the remaining eligible form, which #147 forbids. Selection
must use the 1% constant-form rule independently for each branch and retain
the heat branch as primary even when its selected form differs from the control.

The existing identification report uses `np.corrcoef`, a centered correlation.
#147 requires uncentered normalized column products. The added check therefore
uses the native `optimizer_jacobian` directly, includes active-bound directions,
checks zero/nonfinite columns, normalized singular ratio and all pairwise
uncentered correlations, and projects the slope against all four intercepts.
It retains norms, singular values, correlations, active bounds, slope interior
and projected fraction. Start agreement remains owned by selection.

## Coverage of §9.3

| Requirement | Draft owner operation and fixed denominator |
|---|---|
| Numerical completeness | Existing state tolerance, raw stationarity and material/charge checks; all 83 base states and all required caloric endpoints; failures retain their cause and remain in the denominator |
| Pressure preservation | Selected heat primary cost ≤ **9.077053756257484** on 47 corrected targets; control reported separately |
| Species preservation | Selected heat primary cost ≤ **27.33328854377677** on 94 targets; no combined-family passing limit |
| Vinjarapu | All 8 source-scaled residuals, RMS ≤2 and absolute mean ≤2 at each of four loading levels; raw kJ/mol RMSE, bias and individual predictions retained |
| Arcis | Exactly 14 frozen rows; 8 at 0.51 MPa and 6 at 1.03 MPa, 322.5 K; each group's RMS and absolute mean ≤2; source saturation margins and fixed-P/bubble checks retained |
| Mathonat | Exactly 2 source-average observations at 313.15/353.15 K; native 0→ε at ε=0.001, 0.0005, 0.00025 for each of 2/5/10 MPa; last two values differ by ≤100 J/mol; compare the three-pressure average once with the pooled source scale, retaining pressure spread |
| Independent heat versus control | Aggregate RMS over 14 Arcis + 2 Mathonat residuals; primary ≤ matched control; incomplete cases cannot pass |
| 80 °C pressure | Existing canonical **21-row** AARD ≤ **20.270257%**; retain 19-row diagnostic separately and primary-minus-control AARD, RMS log ratio and signed bias |
| Identification | Both-start agreement; all 4 or 5 columns; normalized singular ratio ≥1e−8; absolute uncentered correlations <0.95; selected slope also has interior b, full intercept/five-column rank and η>0.3122499 |
| Effective interactions | Existing endpoint checks retained, including selected primary at required assessment temperatures |

The fixed-P heat calculation reuses the Engine's total enthalpy and derivatives.
Application code declares endpoint feeds, references, phases and source scales;
it does not reconstruct absorption enthalpy. Endpoint and phase-boundary checks
call the shared bounded solver and check owner. The supported pure-CO2 state
query retains feed density, pressure-density derivative, root count and total
enthalpy; no `FeedEnthalpy` enum call is introduced. Each complete observation
has one ≤175 s subprocess timeout inside its parent deadline. Failures keep
the endpoint checks and diagnostics already obtained.

Stages 1–3 retain canonical pressure, existing 80 °C species and Wagner near
353 K. Stage 4 is the required independent heat comparison and final limits.
The draft explicitly refuses #147 stages above 4: the historical #140 stage 5
would otherwise launch a new 15/45 wt% transfer study. Xu `0286`–`0288` remain
unevaluated. Outside-domain execution, diagnostic loading sensitivities and
the eventual full post-adoption suite are not measured implementations here;
they are not needed to evaluate the requested §9.3 limits and are not silently
claimed complete. The compute envelope below reserves their assessment caps
without authorizing or implementing them.

## Line count

Actual unified diffs were written from the exact worktree owners to the `/tmp`
drafts. Counts include replacements, comments and blank lines. No formatter,
semicolon packing, helper/test exemption or deletion credit was used.

| Part | Gross added lines | Existing lines replaced/removed |
|---|---:|---:|
| Fit owner bindings and input checks | 73 | Included in fit total |
| Native heat row selection/problem/observation | 24 | 0 |
| Fixed-P endpoint/feed/boundary checks and bounded heat calls | 75 | 0 |
| Native fit/coordinate/export changes | 28 | Included in fit total |
| Heat rescoring and family output | 30 | Included in fit total |
| Exact recovery check in the fit owner | 53 | 0 |
| **Fit owner subtotal** | **283** | **7** |
| Assessment bindings, corrected observations and stage dispatch | 63 | Included in assessment total |
| Branch selection and freeze | 26 | Included in assessment total |
| Identification, including selected slope | 38 | 0 |
| Independent heat and source-scale metrics | 85 | 0 |
| §9.3 limits and primary/control comparison | 59 | 0 |
| **Assessment owner subtotal** | **271** | **14** |
| Shared evaluation | **0** | **0** |
| Retired live timing driver | **0** | **80** |
| **Total remaining gross additions** | **554** | **101** |

The two owner diffs have 575 changed lines if additions and replaced/removed
lines are counted together. Including timing retirement gives 655 changed
lines. These are different measures from the **554 additions** charged to the
ceiling. Retired measurement prose is documentation, accounted separately.

The proposed minimum ceiling for this concrete draft is **1,120**. This is
**156** above the retired route's cumulative projection of 964. A rounded
buffer is not added. The 53-line numerical recovery check and the 75-line
endpoint/feed/timeout responsibility are explicit rather than hidden in a
temporary script or claimed to cost zero. The smaller retired fragments were
not integrated code and their count did not establish complete execution.
This draft also remains unqualified until Build and independent Review; its
count is not a mathematical lower bound.

## Compute measurement

The retained no-heat branch of `fit/timing.json` has 141 rows:

- presolve state time: **40.452 s**;
- complete row-by-row residual prediction time: **46.712 s**;
- complete five-direction differentiation time: **61.243 s**.

The branch named heat has only 141 rows and supplies no heat timing. It is not
used as a complete heat objective. The retained §8 files instead give native
heat prediction times **0.335–0.376 s** at α=0.11 and 0.45. Their independent
prediction subprocesses took **0.644–0.710 s**; exact five-direction gradient
subprocesses took **1.281–1.474 s**. The latter include interpreter/setup time
and are a conservative proxy for native per-row differentiation. There is no
measured α=0.22/0.33 or fitted-parameter heat timing yet.

#140's eight retained fits have 7–24 iterations, 7–24 residual evaluations,
8–14 Jacobian evaluations and wall times **192.557–481.618 s**. The four
fixed-dispersion fits, closest to #147's coordinates, have 7–10 iterations
and wall times **192.557–247.976 s**. The longest #140 cases include free CO2
dispersion, which is excluded from #147; they bound a broader historical
comparison and do not prove future heat-fit convergence.

For conservative current-wheel timing, use the actual residual and Jacobian
evaluation counts separately:

    t_fit = 40.452 + 50 + N_residual*46.712 + N_Jacobian*61.243
            + heat_branch*8*(N_residual*0.710 + N_Jacobian*1.474).

The added 50 s allows calibration phase/feed checks and execution overhead.
No shared-endpoint caching, native row batching speedup or process-pool speedup
is assumed. Native #140 batch times divided by evaluation counts are only
about 9.79–12.35 s; those historical batch times must not be confused with the
107.956 s current row-by-row pair of passes. The conservative calculation
uses the measured current costs, rather than claiming the historical speedup
will recur on the new wheel.

| Work | Estimated single-thread elapsed/job seconds |
|---|---:|
| 8 fits, matching fixed-dispersion evaluation counts | 9,195.6 |
| 8 export/reload/rescores, with 8 heat rows scored for every fit | 1,369.3 |
| In-domain assessment, including 64 required independent caloric calls | 2,312.0 |
| Exact recovery/149-row check | 145.4 |
| **Total** | **13,022.4** |

The 64 caloric calls are `(14 + 2*3*3)*2` across primary and control.
The 512 s estimate allows 8 s per bounded case including endpoint/bubble/feed
checks; source conditions and fitted parameters may make them slower. The
remaining 1,800 s assessment allowance covers pressure, species, Wagner,
grouped statistics and execution overhead. These are planning allowances,
not newly measured costs at the selected parameters.

The matching projections per fit are no-heat **907–1,231 s** and heat
**1,041–1,418 s**. Applying the largest historical counts gives **2,297 s**
for one heat fit, about **103 s** below the external 2,400 s cap. Its native
estimate after setup/overhead is about **2,207 s**, only about **43 s** below
the native 2,250 s stop. Neither margin justifies a cap increase without
measurement. Forty residual and 41 Jacobian evaluations would project about
**5,180 s** for a heat fit and cannot fit the current cap.

An envelope of eight copies of the slowest projected fit, eight rescores, all
six 1,800 s assessment caps and the recovery check is **30,692.7 s**. Against
the approximately **49,570 s** remaining, this leaves **18,877.3 s**. The
cumulative allowance is therefore not the immediate constraint; individual
fit convergence and the native/external per-fit caps remain decisive. A
complete 149-row timing measurement must update the estimate before fitting.
No extra iteration allowance, retry, ninth fit or domain extension is proposed.

## Falsifying check and execution handoff

After approval and implementation, run the owner check on the pinned wheel:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 \
agent-heavy --max 2G --timeout 10m \
uv run --no-project \
  --python analyses/mea_parameter_bundle/results/runs/temperature-heat-147/.venv-c1067020/bin/python \
  python analyses/mea_parameter_bundle/results/temperature-reanchor-140/low-temperature-fit.py \
  --issue147 check147
```

This is a future command against the implemented owner, not a command that
exists in tracked code today. Its draft body is 53 counted lines.

1. Verify corrected input IDs/hashes, wheel and frozen source bindings. Use
   the prescribed all-zero intercept/slope start, four 0.01 scales and 10 K
   slope scale. Construct the exact five-coordinate affine chart.
2. Reuse the retained 83 presolve states solely as numerical anchors, after
   checking their completeness. Construct each corrected problem through
   the existing shared owner and every pressure/species row through existing
   `refit.observations`. Assert identical ordering of all 141 target IDs.
3. Require exact floating-point equality, with **no tolerance substitution**,
   for all 141 weighted residuals and all **705** retained gradient entries.
   Record mismatches by target; any mismatch rejects the proposed bindings
   before fitting. Do not rerun all 83 presolves merely to generate a different
   starting anchor for this equivalence check.
4. Assert the exact eight `heat_calibration` IDs, append them after the 141 base
   rows, and assert **149 observations**. Evaluate all eight native predictions
   and five-direction gradients; require finite, available results. The
   branch's first 141 declarations must be the same base rows, not a new mask.

Important field meaning: `timing.json` stores `regression.differentiate`'s
raw prediction gradients, not the optimizer Jacobian returned by a native fit.
The check compares what was actually retained, exactly. Native fitting applies
the residual transformation, declared weight and coordinate scale; §7
identification consumes its `optimizer_jacobian` without a second weighting.
Calling the raw stored gradients an already weighted optimizer matrix would
be an incorrect comparison.

The check should take roughly 145 s and fits the allowed 10-minute small-check
ceiling. A later complete presolve/timing job still respects the 1,800 s R2 cap;
its full heat-row costs, rather than the history-only estimate, decide whether
the eight fits may proceed. Run each owner fit under the 2,400 s external cap
and native 40-iteration/2,250 s controls; each rescore under 1,650 s. Commit the
required input/selection freeze before any new loaded solve above 333.15 K.
Then assess once in order. Adoption remains a separate owner decision.

## Obstacles and limits

No missing Engine capability was found: the installed wheel exposes affine
coordinates, `addition_enthalpy`, exact differentiation and the thermochemistry
argument to native fitting. The prior Ready/Supported evidence covers the
declared wheel and exact-zero endpoint. No solver or fit was run here, so this
report does not claim that the exact recovery check has passed.

The current approved ceiling of 691 does not cover this measured draft.
Owner approval of a revised ceiling, or a separately measured smaller draft,
is required before implementation. The exact recovery check and full heat
timing are unresolved execution gates. The narrow per-fit timing margin is
an uncertainty, not evidence that the method is impossible.

The drafts are measurement evidence and have syntax checks only. Full
integration, retained failure-field checks and
independent readiness/delivered reviews remain with the accountable worker
and parent. This report does not add an outside-domain study, loading-sensitivity
implementation, notebook authoring or manuscript requirements to the requested
measurement scope.

Files beside this report: `owner-reuse.diff`, `low-temperature-fit.py.diff`,
`assessment.py.diff`, the two complete owner drafts, `line-counts.json`,
`compute-measurement.json`, and three draft-generation scripts. The JSON
records bind the exact draft hashes and the retained timing arithmetic.
