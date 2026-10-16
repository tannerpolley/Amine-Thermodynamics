# Amendment 3: comparison stopped before numerical launch

**Larger dielectric branch: inconclusive. Smaller dielectric branch: inconclusive.** Neither branch can be decided under the 10% non-Kiepe improvement / at-most-1% common-149 increase rule. No information evaluation, derivative re-solve, fit, replay or thermodynamic assessment was launched. This is an execution-admission stop, not evidence for or against the CO₂–MEA model-form hypothesis.

The [published corrected amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6211312555), §7 and readiness correction C3, prohibits a launch without a conservative complete-call bound and accounted overhead. The [admission record](admission.json) retains the two unresolved quantities. The accountable parent must settle them before numerical work resumes; no answer, idle wait or automatic owner-away disposition is assumed here.

## What stopped the first call

The first pending operation is the larger-dV source/seed A information calculation, before expensive fitting. In `fit_campaign.py::stage6_study`, lines 573–580, `process.start()` precedes the bounded join; on timeout, `process.terminate()` is followed by `process.join()` **without a timeout**. The 1320 s fit backstop therefore bounds the first join, not complete launch, termination, reaping and result writing. The information calculation has the same unbounded reaping path after its 180 s first join. Observed previous call durations do not establish an upper bound for this path. No finite complete-call wall or CPU bound can be supplied from that launcher.

The [previous accounting](../route2b/completion-accounting.json), notes[4], also explicitly leaves earlier overhead unknown. No finite upper bound for it is supplied. The historical 5215.0172 s idle charge is preserved; the smaller idle-inclusive remainder is used rather than reclaiming that time. Subsequent preparation and reporting charges do not resolve the earlier missing quantity.

At the supplied entry charges, remaining CPU is 92821.951086 s and remaining wall is **at most** 7998.643804 s. The nominal capacity calculation 32 × 1320 = 42240 CPU-s, plus the untouched mandatory-check reserve of 18000 CPU-s, gives 60240 CPU-s; the nominal wall calculation is 1320 + 2000 = 3320 s. Those nominal sums fit the entry remainders, but omit the unbounded operations and unknown overhead. They cannot admit a call. The four-fit 7280 s planning reservation leaves only 718.643804 s before subsequent charges and unresolved overhead; it is not a measured runtime guarantee.

The launcher was left unchanged. An outer systemd containment option was considered, but no unit or containment implementation was created: it would not reconcile the historical overhead, and the task requires handing back when the admission quantities cannot be accounted for. No live CPU monitor, CPU throttle, shortened arm, altered solver tolerance, new fit or increased program cap was introduced.

## Retained declarations and checks

The [information declaration](information-spec.json) retains the actual two A starts in larger/smaller order and λ=0. Its first 14 coordinates are the common nuisance directions, including both free ion dispersion energies. Its final two are CO₂–MEA pivot interaction and reciprocal-temperature slope, initially zero, with bounds ±0.5 and ±500 K and scales 0.01 and 10 K. The [comparison declaration](comparison-declaration.json) names the four unexecuted fits and refers to that single coordinate owner; it is a schedule, not a new executable or a completed release qualification.

CO₂–water is fixed at the stage-2 law, with pivot −0.046416901120577676 and slope −35.66505220645838 K at 313.15 K. Each arm starts independently from the unchanged branch-specific source/seed document. The treatment frees all 16 coordinates; the matched control fixes CO₂–MEA at zero and frees only the first 14. The two measured dielectric branches and all fixed source chemistry, size ties and other model quantities retain their declared owners.

Static comparisons preserve the exact original observation definitions, order, feeds, weights and scales: 47 pressures, 94 common species, eight Vinjarapu heats, seven restored species, six pooled Jakobsen ratios, 39 Kiepe total pressures and four equilibrium heat capacities, totaling 205 positive-weight residuals. The 12 loaded density requests keep zero weight. No new density weight, start, gas–ion coordinate or parameter adoption is included.

[Input and installed-wheel checks](inputs-check.json) pass for all frozen inputs, both A starts and all 12 installed Engine files. Wheel SHA-256 is `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`, Engine `84ca269dfa0c7068417a1c4c326acae276d4d965`, Python 3.13.14, NumPy 2.5.4 and SciPy 1.18.1. The corrected local design exactly matches its published issue comment. At inspection, 24,696,377,344 bytes of physical memory were available, exceeding the declared 32 × 268,435,456 = 8,589,934,592 byte worker estimate. These are static identity, declaration and machine checks, not thermodynamic verification.

No local literature shelf is present in this worktree. The accepted design and its source-read/readiness evidence were read; this task makes no new literature-backed judgment and does not claim an independent reread of its primary papers.

## Four-fit reporting

| Fit order | Branch | Arm | Free coordinates | Convergence | CO₂–MEA endpoint |
|---:|---|---|---:|---|---|
| 1 | Larger dV | Treatment | 16 | Unrun | Unavailable; start is (0, 0 K) |
| 2 | Larger dV | Control | 14 | Unrun | No endpoint; pair declared fixed at (0, 0 K) |
| 3 | Smaller dV | Treatment | 16 | Unrun | Unavailable; start is (0, 0 K) |
| 4 | Smaller dV | Control | 14 | Unrun | No endpoint; pair declared fixed at (0, 0 K) |

| Training cost family or total | Rows | Larger treatment | Larger control | Smaller treatment | Smaller control |
|---|---:|---|---|---|---|
| Common pressure | 47 | Unavailable | Unavailable | Unavailable | Unavailable |
| Common species | 94 | Unavailable | Unavailable | Unavailable | Unavailable |
| Vinjarapu heat | 8 | Unavailable | Unavailable | Unavailable | Unavailable |
| Restored species | 7 | Unavailable | Unavailable | Unavailable | Unavailable |
| Pooled Jakobsen ratios | 6 | Unavailable | Unavailable | Unavailable | Unavailable |
| Kiepe total pressure | 39 | Unavailable | Unavailable | Unavailable | Unavailable |
| Equilibrium heat capacity | 4 | Unavailable | Unavailable | Unavailable | Unavailable |
| Full objective | 205 | Unavailable | Unavailable | Unavailable | Unavailable |
| Non-Kiepe objective | 166 | Unavailable | Unavailable | Unavailable | Unavailable |
| Common objective | 149 | Unavailable | Unavailable | Unavailable | Unavailable |

For **each of the four fits**, the Kiepe weighted-residual invariance check and its two new-coordinate derivatives are unrun; active bounds and signed gradients are uncomputed; all four Cp predictions and errors are unavailable. Missing values are not zero, and the source/seed values are not fitted endpoints. The retained Route 2b costs, bounds, heat capacities and failed replay belong to a different free set and do not supply these missing comparison values.

The intended Kiepe check remains absolute weighted-row change ≤10⁻⁸ relative to the qualified fixed-binary reference, with $r_K=\ln(P_{calc}/P_{obs})/\sqrt{39}$, and new-column magnitudes ≤10⁻⁸ per optimizer unit. This tolerance is not in Pa. New-column projected rank, full/free condition, representative pressure/species/heat/Cp derivatives, start/endpoint closure and cold replay remain required and unrun. A complete bound-active control would remain a permitted comparison under the accepted design; that exception does not resolve this earlier admission stop.

No parameter uncertainty, independent prediction, physical validation, model rejection, parameter adoption or manuscript promotion follows. A numerical figure would have no evaluated values to show, so no plot is made. The existing [notebook](../../../../notebook.qmd#amendment-3-comparison-stopped-before-launch) records only this campaign stopping point; no new scientific results notebook is created. Delivered independent review remains with the parent.

## Charges and code

Numerical Engine CPU and wall charges are **0 / 0**; the numerical call count is zero. A conservative **100 CPU-s** covers declaration preparation, static identity checks, reporting, presentation and commits, including the measured 0.169915 CPU-s identity/declaration command. Program CPU charge is therefore **51278.048914 / 144000 CPU-s**, leaving **92721.951086 CPU-s**. The [final accounting](accounting.json) retains measured presentation charges, the tracked wall interval, separate preparation/finish reservations, historical idle time and unresolved earlier overhead. No actual fit CPU measurement or complete-call timing is claimed.

There are **0 executable additions and 0 removals**, with the existing campaign charge **857/900**; the task-specific 25-line maximum is unused. There are no new tests or dependencies. The [change accounting](change-accounting.json) separates declarations, static-check records and notebook prose. The scientific runtime and observation modules are unchanged. Work remains in the specified worktree and feature branch. Local commits retain each completed step; no push, merge, GitHub write, subagent or Quarto preview-service action occurs.

The parent handoff is the complete-call lifecycle bound and a reconciliation or authorized bound for historical overhead. After those are supplied, admission must be recomputed with all intervening charges and the remaining mandatory-check reserve before the pending start-information call. The four-fit campaign is **not executed or complete**.
