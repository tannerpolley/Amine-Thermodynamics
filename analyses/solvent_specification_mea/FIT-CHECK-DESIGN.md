# Test the solvent-specification fitting path on reactive MEA rows

## Status and requested outcome

Design amendment for [#235](https://github.com/tannerpolley/Amine-Thermodynamics/issues/235), 2026-11-02, following Build attempt 1 at `4e7243a` and the owner's decision to allow one rerun from a true perturbed start. This amendment is pending independent readiness review, issue-body publication by the accountable owner, and approval of the extra line allowance below. The earlier readiness decision does not cover the corrected starting declaration and recovery falsifier.

Accounting base remains `35703c29300eddcc2d2988eb84e68c066d24cf16`. Attempt 1 spent the approved **170 executable + 20 test lines** from that base. Request **45 additional executable + 0 additional test lines**, for ceilings of **215 + 20**; approval is open. Time remains **30 min total / 20 min fit / 60 iterations** for one further attempt.

Question: can `SolventSpecification.fit()` recover attempt 1's endpoint of the same 213-row objective from the authoritative perturbation, when both physical parameters and starting reaction laws actually carry that perturbation?

The recovery reference is attempt 1 at cost **45.360525618233154**, not the 307-row accepted vector. Require cost agreement within **1e-6 relative**, all 14 coordinates within **1e-5 scaled units**, and the same active bounds and sides. These are numerical reproduction tolerances, not physical uncertainties. The old one-scale neighborhood and equal-or-lower-only test are superseded. The accepted 307-row endpoint remains the baseline and the perturbation basis. Recovery does not establish unique parameters, physical validation, parameter adoption, or AMP/absorber suitability.

## Reference, equations and fixed inputs

Reuse the merged [#233](https://github.com/tannerpolley/Amine-Thermodynamics/issues/233) packet `analyses/solvent_specification_mea/`, including its declarations, endpoint, calorics, all 213 row identities and order, seeded feeds, phase supports, initial guesses, reaction references, residual definitions, scales, weights and requested equilibrium tolerances. Preserve the 13 request-backed construction declarations and their existing temperature bounds. Do not regenerate observations from nominal concentration/loading. Do not fit the 39 Kiepe, 50 Cai or five CO2-free-density rows.

Let `C` denote `analyses/mea_parameter_bundle/results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/`, and `E` denote `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/`.

| Reference | SHA-256 |
|---|---|
| `inputs/endpoint.json` in the MEA solvent packet, identical to `E/reported-parameters.json` | `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91` |
| `C/spec.json` | `41d7036739727ba93a1bcbf08e42d85e96033de3143ddc9c66b6938239385869` |
| `C/run/fit/native.json` | `eaf0acffda6068af4832b35ba2469e387409e1716c1037742eaad8dca3d0ca4d` |
| `C/run/fit/timing.json` | `f432092b7ca112d71c0a786f9f6a21f715ffeaac7bd148c45e21ecbcf767b93b` |
| `C/run/fit/chemistry-coordinates.json` | `ed15a32884d7b64ae92733bd324e2296957ccec3f327e34fa41c2b8f03a033fb` |

Hash every consumed packet file at execution. Preserve the existing endpoint-only `MEA.toml` and its results; add a separate fit declaration and results within this same analysis directory.

The unchanged dimensionless weighted least-squares objective is

$$C_{213}=\tfrac12\sum_{j=1}^{213}w_jr_j^2.$$

The accepted reference cost is **45.37796168239049**. Its group costs are common149 **23.860996312136727** (149 rows), restored species **2.4486746519412517** (7), Jakobsen **13.122182452954206** (6), loaded density **0.5654031419421082** (47), and Cp **5.380705123416196** (4). Weights and residual scales come from the packet, not uniform group normalization. Pressure is Pa; heat is signed J/mol added CO2; density is kg/m³; equilibrium heat capacity is J/(mol analytical feed K). Species mole fractions and amount ratios keep their original denominators. This equation and the values are owned by #233 and its notebook, not a new model declaration here.

## Coordinates and local information

Use the 14 reactive entries of `C/spec.json:information_coordinates`, in their original relative order: original zero-based indices **0–11, 14, 15**. Freeze indices 12 and 13 (neutral MEA–water interaction and reciprocal-temperature slope) and every other undeclared parameter at the accepted endpoint. Reactive rows may respond to neutral parameters; freezing them is the owner's scope restriction, not a claim of zero sensitivity.

The chart relation is the Engine's affine declaration $q_i=o_i+s_i v_i$. For the table below, define $q_i^*$ as the accepted endpoint value, $s_i$ as the positive scale, and $o_i=q_i^*+s_i d_i$ as the original perturbed origin. Enthalpy-shift coordinates instead use the accepted laws as their base, $q_i^*=0$, and represent **incremental** shifts. The table uses the original accepted-law basis. Preapplying the starting laws requires the equivalent translations below; it must preserve these physical bounds.

| Original index | Physical coordinate | Scale | Physical bounds | Perturbation $d_i$ |
|---:|---|---:|---|---:|
| 0 | carbamate–water `k_ij` | 0.01 | [-0.5, 0.5] | -0.1 |
| 1 | MEAH+–water `k_ij` | 0.01 | [-0.5, -0.161] | +0.1 |
| 2 | bicarbonate–water `k_ij` | 0.01 | [-0.5, 1] | +0.1 |
| 3 | carbamate–MEAH+ `k_ij` | 0.01 | [-1, 1] | +0.1 |
| 4 | MEAH+–water reciprocal-temperature slope | 10 K | [-1000, 1000] K | +0.1 |
| 5 | MEAH+ segment diameter, tied targets below | 0.1 Å | [5.35, 5.8] Å | +0.1 |
| 6 | carbamate segment diameter, tied targets below | 0.1 Å | [2, 5.8] Å | -0.1 |
| 7 | MEAH+ Born diameter | 0.1 Å | [2, 5] Å | -0.1 |
| 8 | carbamate Born diameter | 0.1 Å | [2, 5] Å | -0.1 |
| 9 | R5 native natural-log coefficient `b` | $80\ln(10)$ K | sorted $-\ln(10)[2922.336201205647,3522.336201205647]$ K | +0.1 |
| 10 | R2 incremental reaction-enthalpy shift | 2500 J/mol reaction | [-8636.068425883279, 11363.931574116721] J/mol | -0.1 |
| 11 | R5 incremental reaction-enthalpy shift | 2500 J/mol reaction | [-20000, 0] J/mol | -0.1 |
| 14 | MEAH+ dispersion energy divided by Boltzmann constant | 10 K | [50, 950] K | -0.1 |
| 15 | carbamate dispersion energy divided by Boltzmann constant | 10 K | [50, 1000] K | +0.1 |

Both segment coordinates retain the declared target multipliers **segment 1, packing 0.88, Debye–Hückel 1**. Born diameters are separate coordinates. No hydration hold or extra coordinate is added. Do not infer target identities from positions in the native physical vector; retain names, units and ties in the fit input.

The perturbation is one tenth of each declared scale: interaction changes of 0.001, diameter changes of 0.01 Å, slopes/dispersion changes of 1 K, a native R5 coefficient change of about 18.42 K, and enthalpy changes of 250 J/mol. Active-bound entries move inward. The table is the authoritative record of starts: $d_i=0.1\,\mathrm{sign}(g_i)$ with $g=J^T r_w$ over the 213 retained rows, except that active-bound entries move inward. Here $J$ is the weighted-residual Jacobian and $r_w$ the weighted-residual vector. Build copies the table; it must not recompute signs from a new gradient. This is one repeatable displacement; no multistart search is authorized. These are proposed numerical exercise sizes, not measurement uncertainties or literature-derived physical acceptance ranges.

### Reaction basis and inherited shifts

Use `reg.reaction_coordinate('R5', 'b', ...)` and `reg.reaction_enthalpy_shift(..., pivot_temperature=313.15, ...)`. `C/spec.json` supplies the R5 source-to-native factor **−ln(10)** and scale 80 K. Apply that factor once and sort the converted bounds. Its accepted effective source coefficient is **3354.099229276806 K**; `chemistry-coordinates.json` separately records unshifted R5 **2831.763028071159 K** and total inherited shifts R2 **−1363.931574116721 J/mol**, R5 **10000 J/mol**.

The prepared chemistry already includes those inherited shifts. Do not apply them again. R2's old incremental bounds [-8188.069891814774, 11811.930108185226] were relative to the earlier −1811.930108185226 J/mol shift. They represent total [-10000, 10000] J/mol, hence the translated bounds in the table at the accepted endpoint. R5 is already at total +10000 J/mol, so its incremental bounds remain [-20000, 0]. Retain the original R5 coefficient bounds; the inherited R5 shift has not changed between that declaration and this endpoint.

The Engine owns law evaluation, coefficient conversion and enthalpy-shift composition. Reuse the packet's adopted chemistry and native chart evaluation; no local thermodynamic equation or reaction-completion implementation is introduced. No new reaction-source judgment is made.

### Evidence for this restriction and its limits

A read-only reduction during Design reshaped `C/run/fit/native.json:optimizer_jacobian` to 307 × 16, joined native `rows[].id` to `E/fitted-rows.csv:target`, selected exactly the five admitted groups, and retained columns 0–11,14,15. Its 213 × 14 singular values are:

`16.6566570866, 3.62657685479, 3.17187298495, 2.79721378570, 0.863184151186, 0.197225767749, 0.163645037341, 0.104609358931, 0.0200861195323, 0.0107870984931, 0.00889695676612, 0.00468814748724, 0.00435427836766, 0.000832358568811`.

Numerical rank is 14; condition number is **20011.3962**. This is local numerical sensitivity in the retained chart, not practical parameter identifiability or a global basin proof. Bounds remain active and covariance remains conditional. The retained subset gradient is nonzero, including original columns 0 **−0.0066521**, 3 **0.0624510**, 5 **0.218148** and 9 **0.0188745**. This supports using attempt 1's reduced-objective endpoint for recovery rather than the full-objective vector. Refresh native rank/conditioning at the actual fit endpoint; do not impose equality with these singular values on a shifted chart.

## Execution and numerical falsifier

Use one call through the existing `SolventSpecification.fit()` and native `reg.fit`. No historical producer may be imported during runtime. Preparation may inspect existing owners to translate coordinate declarations; it may not create a second fitting implementation.

1. **Baseline first.** Reproduce #233's 213 endpoint rows, using the owner-approved 2026-11-02 replay rule: **1e-10 relative** on predicted values and total cost; residuals, weighted residuals and row costs satisfy $|\Delta|\le10^{-10}\max(|\mathrm{reference}|,1)$. Report group costs as well. Near-zero residuals amplify relative changes because a log-ratio residual divides the relative prediction change by $|r|$; the cause of the approximately 1e-13 prediction change was not diagnosed. The e6dae5c7 baseline is accepted; retain its comparison beside the notebook evidence. Reject missing rows, nonfinite values or unmet requested equilibrium tolerances. Stable summation must give the declared subset cost. Do not proceed to fitting after a baseline failure.
2. **Declare and check the true perturbation.** Keep the endpoint-only baseline unchanged. Prepare a separate `inputs/fit-start.json` containing physical values $q_i^*+s_i d_i$ for every named EOS target, including all tied diameter targets with multipliers 1, 0.88 and 1. Preserve all other values, domains and metadata. Bind `MEA-fit.toml:start` to that document with its hash; the fit instance must explicitly load `SolventSpecification(..., parameter="start")`, since the default selects `endpoint`. Bind a separate fit declaration to R2/R5 starting laws completed by observation-aware native differentiation of the original table at zero. Those laws include **−250 J/mol incremental shifts for both R2 and R5**, plus the R5 pre-composition coefficient **−7704.67820501164 K**. Do not apply those shifts twice or change the original observation construction parameters, row definitions or thermal record. The existing `fitted_reactions` transport supplies coefficients/reference temperature while retaining each destination's domain and standard-state identity.

   The chart origin alone does not select the start. The wheel's `reg.fit` docstring identifies the parameter document as the physical start and refuses explicit `starts` with enthalpy-shift coordinates. Use the rebased chart described below, whose native inferred start is zero. Verify every native starting value, tie, law and physical bound; require finite/available predictions and exact derivatives. The actual fit report's `initial_cost` must agree with the independently evaluated document/law start **45.897410107590936** within **1e-8 relative**. A discrepancy stops the attempt as invalid coordinate/law declaration, with no retry.

3. Require all 213 start predictions finite and available and their weighted-residual vector to differ from the baseline by Euclidean norm **at least 1e-4**. Retain actual coordinate displacements and start cost. This exposes an ignored perturbation; it is not a physical threshold. No adaptive sign, size or start retries.
4. Fit once with `maximum_iterations=60`, `function_tolerance=1e-8`, `parameter_tolerance=1e-10`, `gradient_tolerance=1e-8`, and `maximum_elapsed_time_seconds=1200`. Function tolerance is tighter than the accepted continuation's 1e-6, to leave margin for the cost comparison; it does not claim statistical accuracy. Use the full available CPU count for Engine workers and one thread per numerical-library operation. Record requested workers and actual workers if exposed; do not invent actual counts.
5. Require native **usable converged** termination, at least one accepted nonzero optimizer movement (maximum scaled displacement from the perturbed start > **1e-5**), all original physical bounds and ties satisfied, and all 213 final predictions available, finite and meeting their unchanged requested tolerances. A time/iteration limit or native refusal is not a pass.
6. Freshly replay the fitted native parameters **and fitted reaction laws**, with the same thermal record and original problem declarations. Require native fit/replay cost agreement within **1e-8 relative** and each weighted residual within **1e-8 absolute**, following the retained MEA replay tolerances in `C/spec.json:verification`. Preserve both arrays and every difference. Replaying EOS parameters with unfitted input reactions is invalid.
7. Require $|C_f/C_1-1|\le10^{-6}$, where $C_1=45.360525618233154$, an absolute allowance of **0.00004536052561823315**, and $C_{start}-C_f\ge10^{-6}$. Report every group's change; individual groups need not improve. The cost tolerance follows [#228 R2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/228), a numerical reproduction standard rather than measurement accuracy.
8. **Endpoint recovery:** join the 14 coordinates by identity to `results/fit-e6dae5c7/summary.json:coordinates[].fitted`. In the original table's units/basis require $\max_i|(q_{i,f}-q_{i,1})/s_i|\le10^{-5}$. Translate the rebased reaction coordinates back before comparison as described below; raw optimizer vectors from different charts are not comparable. Require exactly the same native active-bound identity set and bound sides: original indices **1, 3, 5, 10 lower**, **7, 8 upper**. Record native covariance active bounds and each bound distance. Use the native active-bound decision, not a new application threshold.

The **1e-5 scaled-coordinate** tolerance also follows #228 R2. Six active bounds do not justify discarding their recovery or widening this allowance: compare all 14 coordinates and require the same active set. This is a deliberately falsifiable reproduction requirement. Attempt 1 had condition number **18552.2036** and projected-gradient norm **0.000139829183**; its stopping point is not a proven exact minimizer or a unique basin. Function-tolerance termination can therefore miss coordinate recovery even with close costs. Retain that finding rather than relaxing tolerances after seeing the rerun.

All convergence, availability, bounds/ties, initial-cost, replay and progress checks must pass along with recovery. A coordinate or active-set mismatch is **different endpoint**, even if the cost falls within its tolerance. Cost below $C_1(1-10^{-6})$ is **lower-cost different endpoint**: evidence of a better accessible point under the same objective, but failure to recover the specified endpoint; it is not an Engine defect or an adopted parameter set. Cost above $C_1(1+10^{-6})$ is **higher-cost recovery failure**: the required recovery was not demonstrated, without proving no better point exists. A cost within tolerance with matching coordinates and active set qualifies the recovery only after every other check passes. No additional attempt follows automatically.

### Equivalent chart after preapplying the starting laws

Let $h_0=-250$ J/mol be each preapplied incremental shift, and let $h'$ denote subsequent shifts relative to the new starting laws. The original-law coordinate is $h=h_0+h'$. Set new enthalpy origins to **0**, keep scale **2500 J/mol**, and subtract $h_0$ from the old bounds: R2 **[−8386.068425883279, 11613.931574116721] J/mol**, R5 **[−19750, 250] J/mol**. This preserves original total enthalpy ranges; an unchanged old box would move the physical limits.

Native law completion changes R5 `b` by **+30.06808876068135 K** when preapplying its −250 J/mol shift. Thus use the completed starting `b` **−7674.610116250958 K**, its origin equal to that value, scale **184.2068074395237 K**, and translate both original `b` bounds by **+30.06808876068135 K**, giving **[−8080.410740648717, −6698.85968485229] K**. At any fitted point recover the old pre-composition coefficient by subtracting this constant; recover both old incremental enthalpies by adding **−250 J/mol** to the new shifts. These translations preserve the original admissible laws, including the independent R5 coefficient/enthalpy combination. EOS origins, scales and physical bounds remain those in the table. Engine continues to own law composition: consume its completed laws, do not reproduce the enthalpy-to-coefficient equation locally.

A read-only wheel probe is retained in `results/design-true-start-e6dae5c7/probe.json`. It round-tripped the perturbed physical document, applied completed starting laws with destination domains preserved, and called the wheel's native `CoordinateSet.start(parameters._native, observations, thermochemistry)`. All **14 inferred optimizer entries were 0**. Native observation-aware differentiation at that inferred point gave cost **45.897410107588506**; fresh predictions from the physical document and starting laws gave **45.897410107590936**, identical to attempt 1's independently evaluated perturbation. Relative difference was **5.295763827461997e-14**, below **1e-8**, with **213 available rows**. Installed Engine bytes matched the specified wheel and SHA-256. Runtime was **20.4205 s active wall**, via `agent-heavy`, Python `-I`, with one numerical-library thread. This checks the native start-selection and evaluation operations without calling `reg.fit` or taking optimizer iterations. It does not claim a new `FitResult.initial_cost`; that exact returned field is a mandatory Build check. No fitting ran in this amendment.

## Wheel and ownership

Use Engine **1.2.0** from merged commit **e6dae5c7353ae10e0aa2d8e46055847b9d64bbe4**, wheel `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl`, SHA-256 **83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6**. Verify installed bytes and record Python, NumPy and SciPy versions. Use the isolated environment without changing project pins.

This merged wheel supplies #962's support for tied reaction coordinates with per-problem temperature bounds. The owner accepted its fixed 213-row baseline replay at cost **45.37796168239802**, against **45.37796168239049** (1.659e-13 relative). Preserve R2/R5 declarations: **13 rows at temperature_max 436.85 K and 200 at 393.15 K**, all at temperature_min 293.15 K. Do not narrow domains, drop rows or infer physical validity above 393.15 K. Fitted-parameter export qualification remains separate work. Stop on an absent required native result; do not substitute another wheel automatically.

### Preserve each destination reaction domain

Before attempt 1, `SolventSpecification.fitted_reactions` replaced the entire destination correlation from `chart.reaction_laws`, including `temperature_min` and `temperature_max`. That copies one observation's domain into every reaction set. Attempt 1 corrected that overwrite within the existing method; retain the correction: require equal `standard_state_id` between completed law and destination, then copy only `a,b,c,d,e,f,reference_temperature`. Keep each destination's temperature bounds, standard-state identity, stoichiometry and reference unchanged. Fail explicitly on a standard-state mismatch; no conversion or fallback is authorized. The current R2 and R5 declarations share `aqueous-molality-infinite-dilution-water-v1` across both domains.

One persistent two-domain check is earned within the **20 test-line** allowance: transport completed R2/R5 laws with nonzero incremental shifts to the original two reaction sets, assert identical fitted coefficients/reference-temperature representation in both, and assert their original 293.15–393.15 and 293.15–436.85 K bounds survive. Include explicit refusal for a mismatched standard-state identity in this same case. This check fails with the former overwrite and is already implemented in attempt 1. It tests mapping; native Engine retains ownership of law composition. No Build code or test is added by this design revision.

**Owner/callers/retirement/evidence:** `src/MEA/solvent_specification.py` continues to own declaration mapping and report transport. The MEA fit runner is its caller. Engine alone owns coordinate transformations, fitting, derivatives, equilibrium, reaction laws and fitted native parameters. Existing MEA and MDEA endpoint checks remain passing references. Keep the whole-correlation replacement retired in `fitted_reactions`; the existing method remains the sole owner of reaction-result transport. The new exercise consumes that corrected mapping. Do not introduce wrappers, local least-squares logic, source-law copies or a generic fitted-document export lifecycle. The analysis preparation edits only named starting EOS values in a copied document; it is not a generic fitted-document exporter.

## Runtime, hard limits and stop rule

Retained evidence separates the last continuation from cumulative work:

- `C/run/fit/timing.json`: **40.5175 s wall**, **448.4418 s CPU** for the final invocation; **16718.5175 s wall (4.64 h)** and **128524.9118 s CPU** cumulative, including earlier charged work.
- `C/run/fit/native.json`: that invocation used **8 iterations**, **9 residual evaluations**, **6 Jacobian evaluations**, no trial failures, starting cost **149.21952645122371**, ending at **148.87893934555717** on all 307 rows.
- `C/command-timing.json`: the separate information call took **216.65 s wall**; the combined final information/fit commands took **257.17 s wall**. Do not charge the 4.64 h as one 40 s fresh fit.
- The #233 materialized 213-row fixed replay took **7.28045 s wall**, with one worker and one numerical thread (`results/runtime.json`). It is not a fitting benchmark.

Estimate **5–20 minutes active wall** for preparation checks, one nearby 14-coordinate/213-row fit and fresh final replay on a comparable machine. The final continuation's roughly five wall seconds per iteration would suggest minutes for 60 iterations; permit substantially more for the new perturbation, rejected steps, derivative work and shared-machine load. This is an engineering planning estimate, not a new timing measurement or assurance of convergence. The cumulative 4.64 h warns against an unrestricted refit campaign.

The owner approved a **hard 1800 s (30 min) active-wall ceiling** for the complete numerical attempt, with **1200 s (20 min) maximum inside native fitting**, and at most **60 iterations**. Allow at most 300 s preflight and 300 s final replay/reporting, within the same total. Run the long command itself as a background shell through `agent-heavy`; start the active timer after memory admission. Record queue wait separately. The outer timer must terminate only its captured child process/process group if native fitting or an evaluation overruns. Preserve the log and completed diagnostics on timeout; use atomic writes for completed result records. No timeout or iteration exhaustion qualifies as convergence.

At any hard limit, stop without automatic continuation, extra starts, larger boxes, relaxed tolerances or increased time. If no complete final replay fits inside the remaining time, retain the partial evidence and classify the outcome as budget-limited. Do not report a partial sum as a final objective. The owner must authorize any subsequent numerical attempt.

## Proposed implementation surface and code ceiling

Attempt 1 at `4e7243a` already spent **170 gross added executable lines and 20 test lines**, counted from `35703c2`, including preparation, fitting runner, destination-law transport fix and its two-domain check. Preserve that evidence and reuse those owners. This Design adds no Build code.

**Owner decision requested before Build: +45 executable lines and +0 test lines**, raising the ceilings to **215 executable + 20 test lines** against the same base. This is a bounded estimate, not approval or a requirement to spend the allowance:

| Existing owner to change | Additional executable allowance | Basis |
|---|---:|---|
| Analysis `prepare.py` | 30 | Copy the physical start with named ties, obtain native completed starting laws, translate the three reaction-coordinate declarations, and hash/write separate fit inputs without altering endpoint inputs |
| Analysis `fit.py` | 15 | Select the physical start and starting laws after the baseline, compare endpoint coordinates in their original basis and the native active set, and retain rerun results separately |
| Existing driver and test | 0 | `parameter="start"` and corrected law transport already exist; the numerical probe checks start selection and the retained rerun checks recovery, so no new persistent test is earned |
| **Requested addition** | **45** | **Total proposed ceilings 215 + 20** |

Count final gross additions against the base, including replacement preparation/runner lines, comments, blanks and notebook code cells; deletions buy no additions. Prepared TOML/JSON, retained outputs and prose are reported separately. Replace the erroneous chart-origin start assumption and neighborhood check in the existing runner, rather than layering a second fit path over them. If 215 executable or 20 test lines prove insufficient, stop before the overrun for a new owner decision. No line allowance is granted by this document.

Reuse the current packet and comparison reductions; no re-materialization of 213 observations, dependency change, solver code or general-purpose export command is earned. If shared driver fitting behavior changes, run the existing MDEA R2 on its declared wheel and preserve its exact 280-row/nine-coordinate tolerances, within an owner-approved amendment for any extra runtime. Do not silently include that fit in this MEA-only attempt. Endpoint R1/R3/R5 are sufficient when changes only transport reporting fields; unchanged fitting code does not require a fresh MDEA fit.

Build runs the installed CSE helper `/home/tnnrpolley21/Workspaces/Agentic-Coding/plugins/cse/cse-plugin/plugin/scripts/workflow/change_accounting.py` (not copied into this repository) once on its final tree against the fixed base, reviews classification and stops before an expected ceiling overrun. The estimate is not permission to spend all 215 proposed lines or to omit required numerical evidence. The helper run for this amendment confirmed that the executable/test additions remain **170/20** from `35703c2`; the inherited #241 design prose is outside this task and was not edited.

## Retained delivery and failure meaning

After approval, write the rerun under `results/fit-true-start-e6dae5c7/`, preserving `results/fit-e6dae5c7/` byte-for-byte as attempt 1 evidence. Keep separate fit inputs, full native fit report, start and final row predictions/residuals, per-row replay differences, group/subset cost comparisons, named coordinate bounds/displacements/ties, completed reaction laws, rank/singular values, active bounds, projected-gradient norm, trial failures with row IDs and causes, runtime/software/input hashes and budget disposition under this analysis directory. Link all of them from the existing `notebook.qmd`; read retained values rather than rerunning fitting when rendering. Do not overwrite #233 evidence or the accepted parameter bundle. No fitted document export or downstream handoff is promised here.

Report one of: qualified endpoint recovery; baseline/input mismatch; unsupported required native capability; invalid coordinate/law declaration; unavailable/nonfinite start or endpoint observation; unusable/nonconverged fitting; cost/progress failure; replay mismatch; different endpoint; lower-cost different endpoint; higher-cost recovery failure; or budget exhaustion. Include actual values, limits and causes for each reported outcome. Rejected intermediate trial solves may occur: retain them and their causes; they do not by themselves invalidate a complete usable converged endpoint.

Stop before execution for changed hashes, unreadable required evidence, changed row definitions or chemistry, or missing authority. Stop and return to Design if the coordinates, bases, ownership, wheel, objective, recovery tolerance, budget or code surface must change. Never remove troublesome rows, alter calorics or neutral parameters, or repair reference outputs to obtain agreement.

Independent delivered `cse:review` must inspect final code and retained numerical evidence after the single approved attempt. A numerical failure can be a complete bounded study result, but cannot qualify the fitting path. No manuscript use, parameter adoption or new physical-validation claim follows from this check.

## Owner decisions and review gates

The owner accepted the e6dae5c7 baseline replay and authorized one rerun from the true perturbed start, replacing the one-scale neighborhood with recovery of attempt 1. Preserve **30 min total / 20 min native fit / 60 iterations**, with 300 s preflight and 300 s replay/reporting inside the total. The old **170 + 20** line ceilings remain authoritative until the owner accepts **+45 executable / +0 test**.

1. Independent readiness review of this amendment remains open. No subagent or independent review ran in this design-only task; do not infer Ready from the numerical probe.
2. The accountable issue owner must publish this amendment into the live #235 body and read it back before Build. The live body read at task entry still described the superseded neighborhood and chart-origin start.
3. Obtain the owner's line decision before Build. This worker requests it through the handoff; it does not approve it or run Build.
4. Existing MDEA R2 extra fitting runtime remains a separate owner amendment if shared fitting mechanics change. This design uses existing driver start selection and native mechanisms; no such driver change is planned.

No reaction-source, data, model-form or parameter-adoption decision is reopened. New data, neutral-group qualification, AMP, Engine edits, physical assessment campaigns, manuscript changes and fitted-document export remain out of scope. Retain attempt 1's invalid-start disposition and its converged endpoint as reproduction evidence, without relabeling it as a qualified fitting-path result.

## Design inspection and evidence limits

Read the live #235 body, the full #233 body and its closing comment, #228 R2 and its retained result, the merged MEA packet and endpoint runner, the complete driver including `fit`, the accepted fit declarations/native diagnostics/timings/chemistry coordinates, and `docs/scientific/README.md` and `docs/scientific/CONTEXT.md`. The #228 R2 evidence is a separate MDEA reference: 23 iterations, cost **374.45201342397434**, zero optimizer difference, cost tolerance **1e-6 relative** and coordinate tolerance **1e-5**. This amendment uses those proposed reproduction tolerances against attempt 1 on the same MEA objective; it does not compare MEA coordinates to MDEA or the 307-row endpoint.

The original numerical Design probe reduced the retained Jacobian/residual arrays under `agent-heavy` and calculated their singular values and gradient; it ran no Engine objective evaluation or fit. The first probe could not import NumPy in system Python; it was rerun successfully with an existing interpreter through `uv run --no-project`, without modifying any environment or main-checkout file. Sources and reductions are identified above so the numerical inspection is reproducible.

The ignored literature shelf is absent in this worktree. Its README was read from the main checkout without writing there. No paper was newly read or verified against Zotero in this Design, and no new literature-based estimation standard, source equation or physical claim is asserted. Adopted chemistry/source decisions remain those explicitly qualified in #233. The coordinate and time allowances here are numerical-check proposals from retained local evidence, not literature or measurement tolerances. This document is not an independent readiness review.

The continuation probes on e6dae5c7 are retained beside the accepted baseline in `results/design-replay-e6dae5c7/` and interpreted in the notebook. They evaluate the accepted endpoint and the prescribed perturbed start through native differentiation; they perform no optimization and do not qualify the fitting path. No independent review is claimed.

The true-start amendment read the live #235 body and comments, attempt 1's full runner/preparation and result diagnostics, the wheel fitting and differentiation docstrings and native start binding, and the #228 R2 tolerance declaration. Its probe uses the installed pinned wheel only; scratch Python and parameter document remained outside the repository. The retained probe contains completed starting laws, rebased coordinate declarations, changed physical values and predictions. No new literature claim, fit, Build code or manuscript-index edit was made. Independent readiness and the owner line decision remain open.
