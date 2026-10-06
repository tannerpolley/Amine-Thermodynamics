**Design verdict: Revise the supplied draft. The reduced proposal adds 520 gross executable-file lines, for a cumulative ceiling of 1,086 = 566 + 520.** This saves 34 lines against the proposed 1,120: 50 lines removed through reuse, with 16 added back for correctness and retained timing/failure evidence. No §7 menu choice, §9.3 limit, identification requirement, freeze, or recovery comparison has been removed. This is a measured proposal, not proof of a global minimum or an executed fit implementation.

The code ceiling is still the owner-approved **691**. This review does not raise it. The proposed 1,086 would require **395 additional lines of authority**. Deleting the live 80-line timing driver does not refund historical additions.

The review used `cse:review` and Ponytail's reuse rules. The repository and GitHub were read-only. All deliverables are under `/tmp/147-owner-route-design/shrink/`. No fit or equilibrium solve ran. Small checks ran through `agent-heavy --max 2G --timeout 10m`, with OpenMP, OpenBLAS and MKL threads set to one and bytecode writes disabled. The only initial dirty entry was the untracked zero-carbon diagnosis directory; it was left alone.

**Basis and limits.** I read the full issue body and all comments, including the 2026-10-06 [Supported qualification](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6025992100), [corrected-input amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6026191670), [Ready verdict](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6026371945), and [Recovery decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6026786257). Those comments supersede stale qualification/budget statements in the body. The reviewed worktree is `b10339d8ec0335831f335aebd93d130fa81c510f`; historical counting base remains `76ea465fe1ede72257a809d04fc986489c5267f3`.

This preserves the conditional 30 wt% MEA temperature experiment: 141 corrected pressure/species targets at or below 333.15 K, eight Vinjarapu heat rows, fixed independent chemistry, four intercepts with or without the existing slope, two starts each, and independent assessment after the selected-record freeze. It makes no new judgment about physical-model adequacy. The worktree lacks a literature shelf; the attached checkout's `literature/README.md` was available and read. No new paper-based claim or change to the approved sources, uncertainty meanings or engineering thresholds is made here.

**Concrete reduced diff and accounting.** `reduced-owner-reuse.diff` is relative to the stated worktree HEAD. It includes the two modified owners and deletion of live `temperature-heat-147/fit/timing.py`. Historical timing results and the archived previous driver stay. The two complete proposed owner files are beside the diff. The diff has been syntax-checked and independently counted with `git diff --no-index --numstat`; it also passes `git apply --check` against the unchanged worktree. It has not been imported or run as an application.

| Owner / responsibility | Gross additions |
|---|---:|
| Fit: imports, bindings, dispatch and spacing | 52 |
| Fit: immutable corrected inputs | 13 |
| Fit: absolute material-error bound | 1 |
| Fit: eight heat-row selection | 5 |
| Fit: fixed-pressure endpoint declarations | 10 |
| Fit: native finite-addition observations | 9 |
| Fit: endpoint/bubble/feed evaluation and retained evidence | 54 |
| Fit: one bounded observation subprocess | 21 |
| Fit: native fit, export and Jacobian reporting changes | 28 |
| Fit: heat rescoring and family outputs | 21 |
| Fit: exact recovery comparison and all-149 timing | 58 |
| **Fit subtotal** | **272** |
| Assessment: bindings, dispatch and spacing | 23 |
| Assessment: source-file bindings | 5 |
| Assessment: selection and freeze | 23 |
| Assessment: corrected packet construction | 6 |
| Assessment: Wagner source binding | 1 |
| Assessment: identification decisions and slope projection | 27 |
| Assessment: required independent heat | 74 |
| Assessment: source-scale statistics | 7 |
| Assessment: §9.3 decisions and primary/control differences | 59 |
| Assessment: historical heat source binding | 1 |
| Assessment: ordered stages and frozen-file checks | 22 |
| **Assessment subtotal** | **248** |
| Shared evaluation | 0 |
| Timing-driver retirement | 0 additions, 80 removals |
| **Remaining additions / cumulative proposed ceiling** | **520 / 1,086** |

The owner modifications also remove/replace 26 existing lines. They buy no addition credit. The counted diff includes comments and blanks. No new helper module, generic fitting layer, runtime dependency, packed statements, stripped comments, or test exemption is used. The recovery check's 58 lines are charged in full. `line-counts.json` records each transformation; `checks.json` gives independent Git counts, per-function counts and draft hashes. Review-only generation/check scripts are not proposed repository code.

**Cuts, with exact savings from the supplied draft.**

| Cut | Lines saved | Why correctness remains |
|---|---:|---|
| Replace repeated corrected-target admission with exact frozen hashes | 8 | Pins both strict141 CSV and the exact final-rerun JSON. Native fit still checks 83 states and 141/149 rows; recovery compares the ordered 141 IDs and all retained values. The existing low-T problem owner still enforces the execution bound. |
| Reuse existing parameter fingerprints in fresh, disjoint caches | 8 | Both fit and rescore reject an existing cache. The immutable chemistry/calorics are checked, the reaction hash is already in fit provenance, and the calorics hash is added there. Neither cache is shared across campaign inputs. |
| Write coordinate provenance once in the existing export loop | 2 | Removes the second pass over the same fitted nodes; keeps the source label, row count, record purpose, companion reaction hash and export/reload checks. |
| Remove duplicate heat output/check and repeated exact-zero support assertion | 8 | Three lines repeated completeness after it was already set; one line wrote a second identical heat JSON; four repeated §8 support verification. Full heat rows remain in the fit summary. The initial feed is still literal zero, the unchanged pinned Engine enforces its qualified support, and endpoint states remain retained. No positive-epsilon replacement is introduced. |
| One input-hash table and verification loop for freeze | 7 | Both calorimetry sources join the same frozen-input table; no input hash is omitted. |
| Remove unreachable Xu filtering and historical-heat guard | 3 | The explicit #147 refusal of stages above 4 remains. Stages 1–3 cannot contain Xu 0286–0288, and historical stage 6 cannot be reached. The freeze still names their unevaluated disposition. |
| Reuse frozen Arcis saturation-separation evidence | 5 | Phase A already records all 14 source separations in `heat-source-admission.json`, and the full CSV retains the underlying values. The reduced fit explicitly pins the accepted Arcis CSV hash. Parameter-dependent bubble comparisons still execute. One added hash line is charged among corrections below. |
| Consume fit-owner identification diagnostics instead of recomputing them in assessment | 9 | The fit owner already records column norms and normalized singular values. Its correlation calculation is changed to the required uncentered product for #147. Assessment consumes those values, retains every fitted column and bound, and still computes the slope projection from the complete native optimizer Jacobian. This saves 12 assessment lines while adding 3 fit-owner lines. |
| **Gross cuts** | **50** | |

For the last cut, the existing fit owner forms the weighted physical-coordinate matrix by dividing the native optimizer columns by their positive declared scales. Unit-column normalization therefore gives the same matrix as normalization of the optimizer columns. This is the equivalent weighted physical-coordinate calculation expressly permitted by §7; it does not use raw unweighted `physical_jacobian`. Column order and positive 0.01 / 10 K scales remain those of the existing owner. Raw native Jacobians are retained and now hash-bound through each fit summary.

**Corrections are not savings.** These require 16 net additional lines over the reduced draft, including replacements of existing lines:

- **Branch selection:** `endswith("-heat")` also matches `constant-no-heat` and `slope-no-heat`. The draft can therefore choose a control as its supposed heat finalist. Match the entire suffix after the first hyphen. The read-only check demonstrates four old matches versus the required two.
- **Endpoint call shape:** `check_state()` expects `observation["request"]["reaction_system"]`; the draft passed only `{"reaction_system": ...}`. It raises `KeyError("request")`. Wrap the request correctly. The snapshot itself is an appropriate record for this checker; the missing observation wrapper is the defect.
- **Observation timeout:** the draft launched a subprocess which itself forked a solver child. Killing the outer process on its 175 s deadline could leave that inner child running. Within the already bounded observation subprocess, call the native solver directly and pass its result to the existing shared snapshot owner. There is one process to kill and no new solver or interruption layer. Retain a worker log for exceptions before a result exists, together with completed endpoint checks.
- **Failure reporting:** native whole-trial failures can use `observation == row_count`; the existing result mapping indexed past the end. Preserve the whole-trial cause. An unavailable native heat prediction must retain its message rather than becoming only a failed assertion.
- **Frozen evidence:** check the selected parameter-file hash on the independent-heat path, which returns before the usual assessment loop. Pin the accepted Arcis bytes before reusing source-admission evidence. Hash-bind the native Jacobian file through the fit summary. Preserve zero-column failure handling when consuming identification fields.
- **Complete timing:** the recovery check now retains prediction and differentiation seconds and native messages for every one of the 149 rows, using one loop. The first 141 still require exact floating-point equality to all 141 residuals and 705 stored gradient entries. No tolerance substitutes for equality. The stored gradients are raw prediction derivatives from `differentiate`, not weighted optimizer Jacobian entries. The eight heat values/gradients must be available and finite.
- **Absolute balance limit:** the inherited checker allowed `1e-7 * max(1, |conserved total|)`. For #147, §8 requires absolute material/charge errors no larger than `1e-7 mol`. Apply the absolute material bound for #147 and make assessment consume the complete checker result. This restores the approved limit; it is not a new threshold.

The first correction group costs 4 lines, retained all-row timing costs 5, accepted-source/Jacobian/failure bindings cost 5, and the absolute-balance correction costs 2. Thus **554 − 50 + 16 = 520**.

**Why the apparent larger cuts are not safe.**

1. **The qualified drivers cannot simply be imported.** `temperature-heat-147/qualify.py` has top-level old-wheel discovery and verification, and `heat_case(alpha)` hard-codes the restored-source mapping, 313.15 K, 1.734 MPa and one observed value/scale, then predicts and writes a file. `qualification-9c31cb9a/qualify.py` rewrites and executes that source, verifies/writes installed records on import, reads `sys.argv`, and runs its dispatcher outside a main guard. Its `native()` likewise calls the fixed `heat_case()`; it cannot evaluate fitted vectors or Mathonat/Arcis states. An importable, general factory does not currently exist. Extracting and parameterizing it would add a third changed runtime owner and all moved lines count gross. This review claims **zero saving from a fictitious import**. Preserve the historical qualified producers and use the small row-declaration functions in the designated fit owner. A future extraction must be measured in full, including import safety and both changed callers; it is not a free cut.
2. **Native declaration checks stay native.** In the pinned build's `engine/native/regression/observations.cpp:202`, native admission already checks positive dose, equal endpoint reaction/reference declarations and componentwise feed balance. Do not copy the qualification wrapper's manual versions into the fit. The reduced proposal does not do so. Those old verification lines are already charged historical code and deleting them would not reduce 566.
3. **Native availability is not all of §9.3.** The Python `Prediction` binding exposes value/status/message/convergence fields but not the C++ `solved`, `final_solved`, `compiled` or `final_compiled` records (`engine/native/bindings/regression_bindings.cpp:123` and `engine/native/regression/observations.hpp:85`). Moreover `addition_enthalpy` returns the initial prediction augmented with the final result internally, not the independent pure-feed root diagnostics. It does not perform the separately declared bubble admission. Keep the fixed-P endpoint, raw-row, material/charge, pure-feed and bubble checks on fitted records. §8's original parameter values cannot establish their result at a new vector.
4. **Native covariance cannot replace identification.** `FitCovariance` is conditioned on convergence, interiority and rank; its singular values are not the required unit-column SVD over all four/five columns including active bounds. Its generic checks also do not supply this issue's source-group RMS, loading means, 21-row AARD, or projected slope fraction. Keep the small issue-specific algebra; consume native fitted arrays and diagnostics rather than inventing new fit bookkeeping.
5. **Do not remove other live owner behavior to buy a lower count.** `final_rerun.py`, `final_evidence.py`, `density_cp_160.py`, `d1_density_cp_160.py`, `reaction-constants.py` and `stage-3-wheel-replay.py` reference these owners. Removing their non-#147 declarations is a separate change, not authorized pruning. The active #147 timing wrapper is the specifically superseded path.

The pinned Engine source inspected for these statements was the local build checkout `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-build-c1067020`, read-only. It was not imported or used to build a wheel. No Engine change is proposed.

**Preserved requirements and handoff details.** The reduced diff retains all eight prescribed fits; both starts and their agreement tolerances; independent 1% simplicity selection by heat/control branch; heat as primary; all 141/149 observations; native half-squared weighted objectives without family renormalization; eight export/reload/rescores; and the exact recovery falsifier. The numerical and engineering decisions remain separate-family limits **9.077053756257484 / 27.33328854377677**, Vinjarapu global RMS and four loading means, **14 Arcis + 2 Mathonat** comparisons, primary independent-heat RMS no worse than control, complete **21-row AARD ≤20.270257%**, full-column rank/correlation limits, and selected-slope interiority / full intercept rank / **η > 0.3122499**. All effective interaction endpoint checks remain.

The selection freeze keeps source IDs/hashes and exclusions through the frozen source/input files, all eight fit-summary hashes, selected parameter hashes, code and wheel identity, and identification evidence. The owner must commit the execution inputs, selected records and full retained evidence before any new loaded solve above 333.15 K, as §9.1 already requires. The code's ordered stage check does not substitute for that commit. Bind the current Wagner source file and corrected packet provenance in the execution freeze as already allowed by the Ready comment. Report within-form heat/no-heat training and rescored-heat differences from the eight existing fit summaries in the notebook; do not add another prediction pass or choose a finalist from that report.

The measured scope is the authorized eight-fit and **in-domain** assessment identified by the latest Ready comment, matching the supplied drafts. It does not claim to implement a new outside-domain heat study, A5/A6 diagnostics, loading sensitivities, adoption, or the post-adoption full evidence suite. Those are not silently deleted from the issue; their domain/authorization and unmeasured implementation remain explicit. In particular no Xu ≥395 K extension follows from this diff. A budget for complete issue closeout cannot present 1,086 as covering those unimplemented parts.

**Owner decisions, separate from correctness cuts.**

- Approve or reject the measured **1,086** code ceiling. The current 691 does not cover it. This review is advice, not budget approval.
- I find no evidence-based reason to relax a §9.3 threshold. Keep all of them.
- If the owner wants a smaller Mathonat assessment, §9.2's first epsilon (`1e-3`) is not used in the stated last-two-value ≤100 J/mol decision; it supplies additional finite-endpoint evidence. Removing it would save **12 of the 64** required independent caloric evaluations across primary/control (2 temperatures × 3 pressures × 2 records), or 96 s at the unverified 8 s/case planning allowance. This changes the explicitly prescribed refinement grid and its completeness evidence, so **it is not cut here**, has no claimed line saving, and requires a pre-assessment owner decision. It is not a remedy for a failing refinement result.
- The ≥395 K Xu domain decision remains outside this pre-fit review, as the Ready comment states. The three rows remain explicitly unevaluated until that source-backed decision exists.

**Compute feasibility: conditional, not yet demonstrated.** The supplied retained timing arithmetic checks out. With no new numerical solve, I independently re-summed the 83 retained presolve times, 141 prediction times and 141 gradient times and checked the historical fit evaluation counts. `compute-review.json` retains the calculation.

For the existing conservative row-by-row approximation:

    t_residual,149 = 46.712028837 + 8 × 0.709674072 = 52.389421413 s
    t_Jacobian,149 = 61.243467182 + 8 × 1.473825611 = 73.034072070 s
    t_total = 40.452183260 + 50 + Nr × t_residual,149 + Nj × t_Jacobian,149

The 50 s phase/feed/export allowance is assumed, not measured. Heat proxies cover only the qualified alpha 0.11/0.45 source-start observations, not all loadings or fitted vectors. The historical `constant-free` run is a broader free-dispersion comparison, not a member of the new fixed-dispersion menu. Its 24 residual / 13 Jacobian counts are nevertheless the slowest retained count scenario; they are not a proven upper bound for a heat fit.

| Scenario | Projection (s) | Consequence |
|---|---:|---|
| Heat fits using matching fixed-dispersion historical counts | 1,041.45–1,417.72 total | Plausible headroom if counts and timings transfer |
| Slowest retained count scenario (24 residual / 13 Jacobian) | **2,297.24 total** | **102.76 s** below external 2,400 s cap |
| Native portion of that scenario | **2,206.79** | Only **43.21 s** below native 2,250 s limit |
| Add one residual evaluation | **2,259.18 native** | Exceeds native cap |
| Add one Jacobian evaluation | **2,279.82 native** | Exceeds native cap |
| 40 residual / 41 Jacobian evaluations | **5,180.43 total** | Cannot fit either cap |

A roughly **15% increase in the estimated heat contribution alone** consumes the slow scenario's remaining native margin, even with the same evaluation counts. Historical 190–480 s batch fit times do not establish current 149-row native costs, and no cache/batching/pool speedup is assumed. Conversely, this conservative row-by-row projection does not prove the native batched fit will be that slow.

The supplied campaign scenarios (about **13,022 s**, or **30,693 s** with its broader assessment allowance) fit the reported ~49,570 s remaining. That is planning arithmetic, not an audited new authorization or an execution-time guarantee. Per-job feasibility is the immediate unresolved issue; a cap-limited fit cannot be made complete by citing unused cumulative budget. The 64 independent caloric cases and eight-rescore costs also use unverified per-case allowances.

Before fitting, the owner must verify:

1. On wheel `e8ad39e0c5d7da471a6d3ace6ff62d60518c57bc1c96fe5198d8bf18747ba8b5`, run the reduced owner's recovery check: exact 141 residuals / 705 raw derivatives at the retained start and anchors, exact eight heat IDs, 149 rows, all heat values and five-column actions finite/available. This review did not run it.
2. Retain the complete 149-row residual/Jacobian timing, including alpha 0.22 and 0.33, and the actual pre-fit phase/feed costs at the prescribed starts. The integrated check supplies the full row timings without another driver. Charge new work against the remaining R2/cumulative allowance; do not treat the recovery run as an unbudgeted additional numerical job or rerun the historical wheel qualification.
3. Recalculate both native and external projections with measured setup, checks, output and kill allowance. Stop for the prespecified measured amendment if the job is projected to overrun. No ninth fit, extra starts, retries, changed stopping tolerances or 40-iteration guarantee is inferred.
4. Keep the 40-iteration / 2,250 s native controls and external **2,400 s including kill grace**, 1,650 s rescore caps, assessment caps, and single-thread worker settings. A native evaluation may overshoot a soft time check; the external termination remains required. Concurrent fitting can shorten wall time but cannot reduce charged single-core job time.
5. Preserve the selected-record commit before high-temperature loaded assessment and retain incomplete denominators and causes on any timeout or unavailable calculation.

**Delivered files.**

- `review.md`: this review and the owner decisions.
- `reduced-owner-reuse.diff`: complete proposed owner diff plus timing-driver retirement.
- `low-temperature-fit.py`, `assessment.py`: complete reduced owner drafts for inspection only.
- `low-temperature-fit.py.diff`, `assessment.py.diff`, `retire-timing.py.diff`: component diffs.
- `line-counts.json`: exact gross accounting and per-cut changes.
- `checks.json`: syntax, independent Git count, branch-membership counterexample, endpoint-call-shape check, input hashes and retained-timing arithmetic.
- `compute-review.json`: cap calculations and scenarios.
- `issue-147.json`, `issue-147-body.md`, `issue-147-full.txt`: full read-back evidence; the CLI's `--comments` text contains comments, so the body was also captured explicitly as JSON/Markdown.
- `reduce.py`, `check_review.py`: review-only reproduction of the proposed diff and small read-only checks.

The remaining checks are execution gates for the implementation owner. This review supplies no new physical prediction, validation, fitted parameter set, or adoption decision.
