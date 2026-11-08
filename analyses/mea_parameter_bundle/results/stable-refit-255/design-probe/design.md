## Stage 2 design: stability-constrained refit (for readiness review)

**Question.** The final set (`00e77608…`, cost 148.87893934557388) is already stable on every grid below, so stable vectors exist by construction. The questions are:

1. When stability is enforced over a dense grid inside the original wide bounds, instead of through the narrowed #170/#212 bounds, does a fitted vector exist that is stable, keeps the calibrated properties within the shared acceptance rules, and has a **lower 307-row cost** than the final set?
2. If not, does the constrained fit return to, or near, the final set? That would show the final set's stability is held by the enforced constraint rather than by the narrowed bounds.
3. How do the #262, #263 and #261 restrictions change the result?

Evidence class: calibration and numerical verification. No physical-validation, global-stability or adoption claim.

### Engine and wheel qualification

- Engine #1059 merged as Engine `main` **`bc7794731e94be961d16028d3f4880c6718a93ad`** (PR #1074). Wheel built from the ignored clone detached at that commit, no source edits: `build/engine-wheels/main-bc7794731e94be961d16028d3f4880c6718a93ad/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl`, SHA-256 **`8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069`**. Installed only in this worktree's environment (`--no-sync`); the repository pin stays on `0d08dff9…`.
- Interface used: `epcsaft.regression.stability(parameters, problem, scale=s, pressure_reference=bubble_problem, pressure_ratio=c)`, inside the existing `reg.fit` driver (`SolventSpecification.fit`). It requires an **all-liquid parent at fixed pressure**, Full optimized trials, zero target in Difference form; the residual is $r=\sqrt{w}\,m/s$, where $m$ is the raw minimum reduced tangent-plane distance $\tau$ on a resolved descending branch and 0 when the completed search has no witness. An unavailable search is a failed evaluation, never zero. Stability cost is reported separately from data cost (`FitResult.data_cost`, `stability_cost`).
- **Qualification (gate before any fit).** Replay the 307 rows for the final set and the wide-bound set (`efb2a9ab…`, 148.211508) on the new wheel against the retained `phase-diagnosis-255/{final,wide}/replay.json`: per-row prediction difference $|y_\text{new}-y_\text{old}|/\max(1,|y_\text{old}|)\le10^{-8}$, same for scaled and weighted residuals (absolute floor 1 for near-zero values), relative cost difference $\le10^{-8}$. Also rerun the stage-1 162-state census (existing `family_job`, liquid+vapor parents at 0.50/0.80/0.95 of bubble pressure) on both sets. The final set must keep 0 descent states, because it is the retreat anchor; if it does not, the work stops and is reported. Differences for the wide set from 54/162, and the incomplete counts, are reported and diagnosed but do not stop the work. A replay failure stops the work and is reported as an Engine regression.

### Design probe already run (scratch, will be retained by the build)

On the proposed fit grid below, the new wheel gives:

| Set | States | Available | Resolved descent | Most negative τ | Unavailable states |
|---|---:|---:|---:|---:|---|
| final `00e77608…` | 1800 | 1796 | **0** | — | 313.15 and 323.15 K, CO₂-free, 25 wt%, both pressure ratios (parent plane uncertainty unavailable; bubble reference iteration limit) |
| wide `efb2a9ab…` | 1800 | 1797 | **1137** | −0.3883 | 313.15 K CO₂-free 25 wt% (both ratios); 383.15 K, α = 0.3, 45 wt%, c = 1.05 (3 failed trial optimizers) |

About 0.2 s per state. The probe takes descent to mean "available with value < 0". The build's grid evaluations also retain `uncertainty`, `cause`, `event` and `report.no_descent_in_trial_set` for each state. The final set is therefore a feasible start inside the wide bounds; the wide set violates the requirement throughout the grid at both pressure ratios and all four strengths.

### Primary fit

- **Data.** The same 307 rows, roles, weights, residual forms and scales as `results/engine-3e83e19c-refit-chain/a6/spec.json` (existing `bind`/`coordinates` path from `density_268.py`, without the 25 #268 Han rows).
- **Coordinates and bounds.** The same 16 coordinates, ties (packing = 0.88 × segment diameter, Debye–Hückel = segment diameter) and scales, with the **original wide bounds from `a6/spec.json` for both starts**: MEAH⁺ segment diameter [2, 5.8] Å, MEAH⁺–water k [−0.5, 0.5], carbamate–MEAH⁺ k [−1, 1], Born diameters [2, 5] Å, R5 aₖ [2922.34, 3522.34], ion dispersion energies [50, 950] and [50, 1000] K, and the remaining a6 bounds. Enthalpy-shift coordinates keep total-shift bounds [−10 000, +10 000] J/mol about 313.15 K, expressed as increments from each start's inherited totals (final: R2 −1363.931574, R5 +10 000; wide: R2 +3442.783281, R5 +10 000).
- **Starts.** (1) the final set; (2) the wider-bound fit `efb2a9ab…`.
- **Stability fit grid (1908 declared states, enforced).** Liquid parents only (the Engine interface takes nothing else), at $P=c\,P^*_\text{bubble}(u)$ with c = 1.05 and 3.0. $P^*$ is the candidate's own reactive bubble pressure: liquid plus pinned-zero vapor, with the same reactions, neutral reference and row tolerance 10⁻¹⁰ as the census.
  - *Dense block, 1800 states:* 15, 25, 35 and 45 wt% MEA on a CO₂-free basis; T = 313.15–393.15 K in 10 K steps (9); analytical loading 10⁻⁵ and 0.025–0.600 in 0.025 steps (25).
  - *Census nodes, 108 states:* the census strength (9.7292821 mol MEA, 76.9751925 mol water, about 30 wt%), at the census temperatures (313.15, 318.15, 333.15, 353.15, 373.15, 393.15 K) and loadings (10⁻⁵, 0.05, 0.1, 0.2, 0.256, 0.3, 0.4, 0.5, 0.6), with liquid parents at both ratios.
  - *Coverage:* the census's own below-bubble liquid + vapor parents cannot be enforced through this interface. Liquid compositions depleted of water and CO₂ are covered by the lower loadings and the 35/45 wt% strengths. The census itself is a held-out check.
  - *Exclusions:* states unavailable at either start cannot be evaluated by the fitter. They are removed from the enforced set before fitting, listed, and re-evaluated at every endpoint. The design probe found 5 such states in the dense block; the census nodes are screened the same way.
- **Penalty stages.** Each start is its own `reg.fit` call; `starts=` refuses enthalpy-shift coordinates. Each stability row has weight 1 and scale $s$, with two stages: $s=10^{-2}$, then $s=3\times10^{-3}$ warm-started from the first. Controls per stage: the a6 controls (180 iterations, function tolerance 10⁻⁶, gradient 10⁻⁸, parameter 10⁻¹⁰), elapsed limit 7200 s, all cores. Each stage writes its full fit report and endpoint before the next starts, and a restart resumes from the last completed stage.
  - *Why two stages, and why a retreat.* The exterior penalty settles near $\tau^*\approx-s^2\,\partial C_\text{data}/\partial\tau\approx-1.7\,s^2$. That estimate takes ΔC ≈ 0.667 between the wide and final sets over the deepest Δτ ≈ 0.39. It gives τ\* ≈ −1.7×10⁻⁴ and −1.5×10⁻⁵, both inside the band the Engine resolves. Smaller $s$ would put τ\* in the Engine's unavailable band. The readiness probe (`review-band-probe.py.txt`) found:
    - −2.2×10⁻⁶ and below: resolved descent;
    - about −1.3×10⁻⁷: *indeterminate*;
    - within about ±2×10⁻⁹: *overlapping-minima tie*;
    - both of the last two are **unavailable**, and the outcome is not monotone along a path.

    An active state therefore always ends slightly unstable, and every run ends with the retreat below. When many enforced states are active, they share the push toward descent, so each may settle shallower than the single-state estimate, possibly in the unavailable band. The stop rule and the retreat cover that case.
  - *Driver outputs (a required change).* Today `SolventSpecification.fit` sets the reactions and fitted parameters to `None` when `usable` is false (`src/MEA/solvent_specification.py:374, 390`). The build changes it so that it retains `result.optimizer` and the physical parameters even when `usable` is false. Its report adds `data_cost`, `stability_cost`, `acceptance`, `stability_predictions` and `stability_transitions`.
  - *Stage endpoint $u_E$.* The last returned optimizer vector, from any stage including an interrupted (`failed`) one, whose fresh 307-row replay has every row available within tolerance. The stability availability of $u_E$ does not matter; the retreat decides. If no stage returns such a vector, the run yields only its anchor (t = 0).
  - *Stop rule.* Go to the next stage only when the stage ends with status converged or limit reached **and** every enforced state is available at its endpoint, per the Engine's own final searches. Otherwise stop. Also stop when those searches show zero descent with every enforced state available; that endpoint is then the retreat's t = 1 point and passes immediately. No other restarts.
- **Retreat (required last step).** In the run's own optimizer chart, take the segment $u(t)=u_A+t\,(u_E-u_A)$. Here $u_E$ is the stage endpoint defined above and $u_A$ is the run's stable anchor: the final set for both primary starts, expressed in that start's affine chart, and each variant's own start when it passes the stability test.
  - A point is *admissible* when all enforced states are available, none has a resolved descent, and all 307 rows are available.
  - Scan t = 1, 0.99, 0.98, … down to the first admissible t. Then refine by 10 halvings between that t and t + 0.01, keeping the last admissible point.
  - The result is *an* admissible point near the endpoint, not the farthest one, because the outcome is not monotone.
  - **That retreat point is the run's candidate.** It is then assessed once against criteria 1–3 below, including the check grids. A candidate that fails is reported as such; the scan does not continue to lower t.
  - It is reported with its t, data cost and the vector. t = 0 returns the anchor itself.
- **Selection.** Among the two starts' candidates that pass criteria 1–3 with t > 0, the primary candidate is the one with the lower 307-row data cost.

### Held-out check grid (never enters the fit)

1. 576 liquid-parent states with offset nodes: 20, 30, 40 wt%; T = 318.15–388.15 K in 10 K steps (8); loading 0.0125–0.5875 in 0.025 steps (24); c = 1.5.
2. The stage-1 162-state census with liquid + vapor parents at 0.50/0.80/0.95 of the final set's bubble pressures (existing `family_job` and `reduce_state`). This keeps the stage-1 definition directly comparable (wide 54/162, final 0/162 on the old wheel). It is the only check of the below-bubble topology.

Reference counts on the new wheel, from the readiness probe (`offset-final.json`, `offset-wide.json`): on the offset grid the final set has 576/576 available and 0 descent, and the wide set 385/576 descent. The census counts on the new wheel come from the qualification step.

### Bounded variants (each compared with the primary)

Each variant uses the same enforced grid, penalty stages, stop rule and retreat. It is assessed under the same acceptance rules, and its cost and metric changes are reported relative to the primary candidate.

- **Start rule.** A variant whose start passes the stability test (all enforced states available, no descent) skips $s=10^{-2}$ and runs only the $s=3\times10^{-3}$ stage, with that start as its retreat anchor. A start with any resolved descent runs from $s=10^{-2}$, with the final set as anchor.
- **(a) R2 held (#262).** Start from the final set, where the R2 increment is exactly zero as in #262's `profile-10-03`. Remove the R2 enthalpy-shift coordinate and fix the R2 total shift at −1363.931574 J/mol; 15 coordinates. Its result is compared with the primary.
- **(b) Joint chemistry + EOS (#263).** Start from the primary candidate, or from the final set under outcome B. Add an R4 incremental enthalpy-shift coordinate (pivot 313.15 K, scale 2500 J/mol, total bounds ±10 000 J/mol) and the ten Böttinger 2008 353 K NMR targets from #263's all-five case: MEA + MEAH⁺ and carbamate mole fractions at its five states, residual $(x_\text{calc}-x_\text{obs})/(0.1x_\text{obs}+0.001)$, weight 1; 317 rows. R5 keeps the original total-shift bounds [−10 000, +10 000] J/mol (owner, 2026-11-08). The final set sits at the +10 000 upper bound, so (b) cannot follow #263's small upward R5 move (+156 J/mol); this is stated with the result. Report the 307-row cost separately and the 353 K carbamate excess (#263 baseline about 26 %). This variant does **not** fit the Hamborg dilute R5 values that #263 recommends as reaction evidence (owner, 2026-11-08). The wheel could declare them as `LogEquilibriumConstant` rows, but #263 never fitted them, so their weighting is untested, and #263's Hamborg law replacement raised Kim heat errors by 211 % at 353 K. Instead, the candidate's completed R5 law is compared after the fit with #263's retained `hamborg-law.json` at Hamborg's temperatures, and reported only.
- **(c) #261 data roles (sensitivity only).** Start from the primary candidate, or from the final set under outcome B. Replace the 47 fitted pressure rows with the 57 Jou/Hilliard/Idris rows at ≤ 333.15 K in `results/pressure-transfer-261/recommendation-data-roles.json`, with #261's declarations, scales and weights; all 106 Aronu rows and the 89 other rows above 333.15 K stay outside the fit and are scored. Criterion 2 is scored on the 57 fitted pressure rows, which replace the 47. The original 47 are also reported. Never eligible as primary.

### Falsifier, acceptance and outcome classes

Each candidate (a retreat point) is compared with the final set, replayed on the new wheel.

1. **Stability.** Fresh Full searches at the candidate, on every enforced state and every check state.
   - Every enforced state must be available and none may have a resolved descent.
   - Among check states (576 offset plus 162 census), none may have a resolved descent.
   - Unavailable or incomplete check states are counted and listed next to the final set's count on the same states. They are never counted as stable.
   - Any resolved descent anywhere fails the candidate.
2. **Pressure and species.** AARD may rise by at most 2 percentage points, separately for: the 47 fitted CO₂ partial pressures, the 39 Kiepe pressures, the 94 fitted phase mole fractions, the 7 restored species and the 6 Jakobsen ratios.
3. **Density, heat, heat capacity.** The count within 2 s must not drop, and AARD and RMSE may each rise by at most 25 % relative. This applies separately to:
   - 47 loaded densities (final: 44/47);
   - 5 CO₂-free densities (5/5);
   - 8 fitted heats of absorption;
   - 4 heat capacities (3/4).

   The 50 Cai MEA–water binary rows (25 bubble temperatures, 25 vapor water fractions; final 36/50 within 2 s) are **reported only**: within-2 s count, AARD and RMSE against the final set, with no pass/fail role (owner, 2026-11-08).
4. **Cost (outcome criterion, separate from acceptance).** The 307-row data cost and the separate stability cost are reported and compared with 148.87893934557388. Criteria 1–3 decide whether a candidate is acceptable. Cost decides the outcome class below (owner, 2026-11-08).
5. **Bounds.** Every coordinate on a bound at the candidate is listed, together with which restricted (#170/#212) bounds it leaves.

**Outcome classes**, decided from the primary runs before any variant result is interpreted:

- **A. Stable improvement.** A candidate with t > 0 passes criteria 1–3 and has 307-row data cost below 148.87893934557388 × (1 − 10⁻⁶), the smallest change resolvable beyond replay tolerance with margin.
  - It goes to the downstream rerun.
  - Report its cost difference, its retreat t, and its distance from the final set coordinate by coordinate.
- **B. No stable improvement.** No start yields such a candidate. This includes a candidate that is stable and acceptable but not cheaper, and runs that yield only their anchor (t = 0).
  - Say so plainly.
  - If the constrained wide-bound fit returns to, or near, the final set, report that as a result in its own right. The final set's stability is then held by the constraint enforced over the 1908-state grid, not by the narrowed #170/#212 bounds, which answers the owner's original objection. "Near" means every coordinate within one coordinate scale of the final set; the per-coordinate distances are reported either way.
  - No downstream rerun.
  - Open one model-form design issue, scoped to the gaps the refit leaves open:
    - the 15/45 wt% pressure-transfer bias (#261);
    - the 353 K carbamate excess (#263);
    - the density conflict above 353 K (#268);
    - the 318 K heat-capacity offset (#264).

    That line of work stops there; no model-form build this sprint.
  - The variants still run and are reported, because they test other restrictions.

### Stage 3 downstream rerun (outcome A only; candidate evidence, not adoption)

Rerun on the branch against the candidate, with the new wheel, into `analyses/mea_parameter_bundle/results/stable-refit-255/`: paper tables and figure data (the existing paper-evidence producers), heat of absorption (8 fitted + 14 Arcis), density (`density_268.py compare` path, including the 25 Han rows above 353 K from #268), heat capacity (#264 producer, including the 318 K offset), the Kim 2007 comparison (#245/#263 producer at 1.734 MPa), and the MDEA transfer (#267 producer). MDEA heat rows that fail on Engine #1073 (`saturation_capped_addition_enthalpy` vapor-branch admission, B1, 333.15 K, 60 wt%, 1.121 MPa) are reported as unavailable, with no workaround. Before regenerating figure data, `generate_figure_data.py` gets the current canonical-VLE hash `d5cd6ea0…` (per #248), after checking which rows changed between the two CSV versions.

**No adoption.** `selected-current-best-parameters.json`, the repository Engine pin and the manuscript stay unchanged. The candidate's README states exactly what adoption would replace: the selected parameter file and hash, the Engine pin (`0d08dff9…` → `8b9609d4…`), and the parameter tables, figures and numbers in the paper evidence.

### Limits

- The requirement is a finite Full search at declared states; zero descent is bounded numerical evidence, not a global certificate.
- Liquid-parent states above the bubble pressure test liquid–liquid stability. The below-bubble liquid + vapor topology is checked only by the census.
- Penalty endpoints are local optima from two starts, and each retreat point is one passing point on one segment. Neither is a global constrained optimum.
- Acceptance rules come from the limitation studies, not from published practice.

### Readiness review disposition

- **Round 1, Revise, 5 findings.** The retreat became the required last step. Rules were added for unavailability and stopped stages. The outcome branch was made reachable. The census nodes were added to the fit grid. Unstable variant starts were addressed.
- **Round 2, Revise, 7 findings.** The candidate is defined as the retreat point, assessed once. The stop rule and stage endpoint now cover the Engine's failure outcomes, and variant starts under outcome B are defined. The owner decided four questions on 2026-11-08: outcome A requires a lower cost; the Cai rows are reported only; variant (b) keeps the original R5 bounds; Hamborg is compared, not fitted.
- **Fix verification.** All twelve earlier findings resolved. Two leftover inconsistencies, the variant stage scale and the definition of $u_E$, were corrected with the reviewer's exact one-line fixes. Ready for Build.
