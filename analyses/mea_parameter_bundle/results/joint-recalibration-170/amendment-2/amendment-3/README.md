# Amendment 3: stopped at the larger-branch information release

**Larger dielectric branch: inconclusive. Smaller dielectric branch: inconclusive.** The 10% non-Kiepe improvement / at-most-1% common-149 increase rule cannot be evaluated on either branch. The larger-dV source/seed A information calculation completed, but the full/free 16-coordinate condition number is **562848.8359854996**, above the inherited **10000** release maximum. This is the required stop before another start or fit, not rejection of the CO₂–MEA physical hypothesis. **All four fits remain unrun.**

## Numerical information and the release stop

The [retained information result](information-results.json), [exact native values](larger-dV-information/information/larger-dV-A/native.json), and [weighted Jacobian](larger-dV-information/information/larger-dV-A/lambda-0.json) contain 217 Available observations: 205 positive-weight residuals and 12 zero-weight loaded-density requests. All 16 declared coordinates are interior at the larger source/seed A start. The singular cutoff is 10⁻¹⁴ relative; optimizer scales, source chemistry, coordinates and observations are unchanged.

| Weighted, scaled Jacobian block | Columns | Rank | Condition | Required release condition |
|---|---:|---:|---:|---|
| Existing nuisance directions, full/free at this interior start | 14 | 14 | 6390.086918958839 | Pass: ≤10000 |
| CO₂–MEA pair projected against all 14 nuisance directions | 2 | 2 | 6.298512700977455 | Pass: rank 2 and ≤10000 |
| Complete free set, nuisance plus CO₂–MEA | 16 | 16 | 562848.8359854996 | **Fail: >10000** |

The complete singular values run from 13.841073118416977 to 2.4591101968226437×10⁻⁵; the two projected values are 1.5489555196120908×10⁻⁴ and 2.4592401304068356×10⁻⁵. Rank two and a moderate projected condition do not satisfy the separate complete-system information requirement. The weakest complete direction has CO₂–MEA pivot/slope coefficients −0.4046199604131155 and −0.9144271489865977 in the declared optimizer coordinates; all nuisance components and spectra are retained. This identifies a local information limit at these scales, not a unique physical explanation or parameter uncertainty. No rescaling, fixed nuisance direction, dropped slope or threshold change was made.

The two-dimensional new-column span has principal cosines (0.4411341667, 0.0682526890) against the three chemistry directions, (0.9528637175, 0.7825191872) against the eleven ion/Born directions, and (0.9699076015, 0.9128263693) against all fourteen nuisance directions. These are local geometric diagnostics, not causal attribution. The launcher's generic exception says the mandatory chemistry/ion block fails conditioning, but its own retained report has `mandatory_passed=true`: the actual failed predicate is the complete 16-column condition, giving `dispersion_release_passed=false`.

## Kiepe invariance and source/seed quantities

At the evaluated larger start, all 39 Kiepe total-pressure rows pass the numerical invariant against the [same-wheel qualified fixed-binary reference](../qualification-84ca269d/co2-water-predictions.json). With $r_K=\ln(P_{calc}/P_{obs})/\sqrt{39}$, the maximum absolute weighted-row difference is **1.3785847463587686×10⁻¹⁴**, below 10⁻⁸; the maximum relative pressure difference is **8.609459133048355×10⁻¹⁴**. Both new weighted optimizer derivatives are **exactly zero** on all 39 rows, below 10⁻⁸ per optimizer unit. [Every pressure, difference and derivative](larger-dV-start-Kiepe.csv) is retained. The tolerance is in weighted-residual units, not Pa. Endpoint invariance and replay are unrun.

The following are **larger source/seed A evaluations**, with CO₂–MEA $(k_p,b)=(0,0\ \mathrm K)$, not fit endpoints. Cost means one half the sum of squared weighted residuals.

| Cost family | Rows | Source/seed A cost |
|---|---:|---:|
| Common pressure | 47 | 24.088735519336648 |
| Common species | 94 | 22.212567386276092 |
| Vinjarapu heat | 8 | 113.34506846611345 |
| Restored species | 7 | 2.9068785827200916 |
| Pooled Jakobsen ratios | 6 | 29.656131864212707 |
| Kiepe total pressure | 39 | 0.0006790194987315811 |
| Equilibrium heat capacity | 4 | 3.4942267920710037 |
| Full objective | 205 | 195.70428763022872 |
| Non-Kiepe objective | 166 | 195.70360861073 |
| Common objective | 149 | 159.6463713717262 |

The [family costs](larger-dV-start-family-costs.csv) and [four seed Cp predictions](larger-dV-start-Cp.csv) retain exact values. Cp uses 7 mol MEA/kg water, 101325 Pa and the declared complete-feed mass conversion. At (318.15 K, nominal loading 0), (318.15 K, 0.358), (353.15 K, nominal 0), (353.15 K, 0.358), predictions are **3.8429337814983437, 3.4007092926258196, 3.8315431506913087, 3.3338543689118705 kJ kg⁻¹ K⁻¹**. Signed errors are **+3.3185584486716824%, +0.9861705308335411%, −0.6497134602678645%, −3.942882735129205%**. Nominal zero carbon uses the declared 10⁻⁶ proxy; no new 10⁻⁷ comparison was launched after the information stop. These seed quantities cannot decide the matched-fit rule.

## All four fits

| Fit order | Branch | Arm | Convergence / iterations | C₁₆₆ / C₁₄₉ | Endpoint Kiepe check | Active bounds | CO₂–MEA endpoint | Fitted Cp errors |
|---:|---|---|---|---|---|---|---|---|
| 1 | Larger dV | Treatment, 16 coordinates | Unrun / none | Unavailable / unavailable | Unrun | Uncomputed | Unavailable; start (0, 0 K) | Unavailable |
| 2 | Larger dV | Control, 14 coordinates | Unrun / none | Unavailable / unavailable | Unrun | Uncomputed | No endpoint; pair declared fixed (0, 0 K) | Unavailable |
| 3 | Smaller dV | Treatment, 16 coordinates | Unrun / none | Unavailable / unavailable | Unrun | Uncomputed | Unavailable; start (0, 0 K) | Unavailable |
| 4 | Smaller dV | Control, 14 coordinates | Unrun / none | Unavailable / unavailable | Unrun | Uncomputed | No endpoint; pair declared fixed (0, 0 K) | Unavailable |

The [comparison declaration](comparison-declaration.json) retains the unchanged four-call order and 10%/1% rule, decided separately for each branch. A numerically complete bound-active control would complete its comparison and remain unadopted; none was launched. The smaller information start also remains unrun because the larger information release triggered the hard stop, not because the ledger was exhausted.

Centered re-solves at optimizer steps 0.01/0.005, independent serialized start/endpoint cold replay, raw closure, pressure-density/phase checks, fitted projected gradients, loaded-density/conditional assessments and endpoint uncertainty remain unrun. No warm-only success substitutes for cold replay. The fit entry point was never reached; its inherited assertion requiring four release records was not exercised by this one-start, λ=0 information declaration. No continuation through that entry point is claimed.

## Orchestrator decisions, 16 October 2026

All three decisions below were supplied by the accountable orchestrator while the owner was away. They supersede the earlier admission stop, retained in Git at `4c9b5f5`. They do not relax the numerical release stop found here.

1. **Bounded teardown.** After the native limit or crash backstop, wait at most 60 s for the fit process to exit after termination. If it remains alive, send SIGKILL only to its own started PID, then reap it. The conservative complete-call fit bound is **1200 + 120 + 60 = 1380 s**. Measure aggregate process-plus-worker CPU after reaping; use no live monitor.
2. **Ledger admission.** The recorded program ledger is the admission basis. Earlier overhead predating that ledger is unknowable, disclosed here, and does not block a launch. No measurement of zero earlier overhead is claimed.
3. **Idle is not active wall.** Disclose the retained **5215.0172 s** with no calculation process separately and exclude it from the **21600 s** active-wall cap. Recompute admission from active charge, retaining every other recorded charge and mandatory-check reserve.

Before each fit, admission requires charged active wall + **1380 s** + remaining mandatory-check wall reserve ≤21600 s, and charged CPU + **44160 CPU-s** + remaining mandatory-check CPU reserve ≤144000 s. The CPU reservation is 32×1380; it is an admission capacity bound, not a measured fit charge or the unchanged 12000 CPU-s post-call stop. The information call used a conservative **240 s / 7680 CPU-s** complete-call bound. The [admission calculation](admission.json) was 51378.048914 + 7680 + 18000 = **77058.048914 CPU-s**, and 11156.613257944995 + 240 + 2000 = **13396.613257944995 active wall-s**: both pass. No fit was subsequently admitted after information release failed.

## Ledger arithmetic and charges

The [earlier continuation ledger](../route2b/completion-accounting.json) gives active wall **4594.298996 + 3792.04 = 8386.338996 s**. The [declaration-step ledger](accounting.json) then adds **1523.379207 s**, giving **9909.718203 s** on resumed entry. Equivalently **15124.735403 − 5215.0172 = 9909.718203 s**. No inter-task idle gap is added. Earlier unknown overhead remains disclosed under the orchestrator's ledger-admission decision.

CPU at entry is **36657.498914 + 14520.55 + 100 = 51278.048914 CPU-s**. The new information child used **49.310241 CPU-s / 49.31769729300868 wall-s**, reaped normally; no live CPU measurement or teardown kill occurred during the numerical call. Whole-command CPU is max(49.513093 internal, 49.54 external) + 0.02 rounding allowance = **49.56 CPU-s**. Whole-command wall is **49.60 s**, conservatively recorded as 49.62 s. Two import-only attempts before the numerical launch failed because the `src` import path was missing; their 0.19 + 0.18 CPU-s are included in the static/reporting reservation. The successful command explicitly uses the local `src` path.

The [resumed ledger](resume-accounting.json) charges **100 CPU-s** for static preparation, lifecycle checks, local reductions, reporting, presentation and commits. Thus program CPU is **51278.048914 + 100 + 49.56 = 51427.608914 / 144000 CPU-s**, leaving **92572.391086 CPU-s**. The unused mandatory-check reserve is **17950.44 CPU-s / 1950.38 wall-s** and is not charged as executed work. Fit CPU/wall and fit count are zero.

Active wall is **9909.718203 + 1200 + 515.792373 + 180 = 11805.510576 / 21600 s**, leaving **9794.489424 s**. The 1200 s is a conservative initial-preparation reservation; 515.792373 s is the measured monotonic interval, including the numerical command; 180 s is reserved for the remaining render/check/commit. The command wall is not added again. These are charged amounts including reservations, not a claim that every reserved second was consumed.

## Implementation, identity and limits

Build replaces the unbounded post-SIGTERM join in `fit_campaign.py::stage6_study` with the accepted 60 s grace period, own-PID kill and reap. Its callers and numerical ownership remain unchanged. The [disposable lifecycle checks](launcher-check.json) execute the changed block on a cooperative child and a real SIGTERM-resistant child, assert the requested 60 s grace, and confirm reaping at exit codes −15 and −9 respectively; the check proxy accelerates the wait to 0.1 s. Syntax compilation passes. No persistent test or dependency is added.

Executable change from task entry `4c9b5f5`: **4 added / 1 removed**, net +3. Gross campaign charge is **857 + 4 = 861 / 900**, within the launcher maximum of five added lines and the task maximum of 25. The final [change accounting](resume-change-accounting.json) separates executable code from retained numerical data and notebook prose. No scientific equation, solver tolerance, observation, parameter box or fit limit changes.

The [rechecked inputs and installed files](resume-inputs-check.json) match Engine `84ca269dfa0c7068417a1c4c326acae276d4d965`, wheel SHA-256 `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`, Python 3.13.14, NumPy 2.5.4 and SciPy 1.18.1. Available memory was 24719065088 bytes, above 32×268435456 = 8589934592 bytes. The numerical command starts with `nice -n 10`; BLAS/OpenMP are single-threaded, 32 native workers are requested, and no source checkout is imported. Information differentiation does not return an actual-worker count; no 32-worker execution claim is inferred for it.

This is a local information diagnostic and binary numerical verification conditional on the source/seed start, fixed model and declared scales. It is not a fitted model-form comparison, independent prediction, physical validation, parameter adoption or manuscript promotion. No local literature shelf is present; the accepted corrected design and source-read/readiness evidence are reused, without a new literature-backed judgment or claim to have reread the papers.

The [existing notebook](../../../../joint-recalibration-history/index.qmd#amendment-3-information-release-stops-both-comparisons) records these retained numerical quantities. A compact table is sufficient for the scalar release checks; a fitted comparison figure would have no endpoints. The managed refresh cannot run because `snakemake` is absent from this worktree environment. The guarded `analyses/render.sh` static HTML path renders the notebook and index with document execution disabled; it does not run a model or alter the preview service. The prose check finds no warning in the new section or this report; three warnings remain in unchanged older notebook passages. Delivered independent review remains with the parent. All work stays in the specified worktree and branch, with local commits after completed steps. No push, merge, GitHub write, subagent, idle answer wait or Quarto preview-service action occurs.
