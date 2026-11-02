# Test the solvent-specification fitting path on reactive MEA rows

## Status and requested outcome

Accepted design for [#235](https://github.com/tannerpolley/Amine-Thermodynamics/issues/235), 2026-11-02. Readiness: Block on `f1b9b9c` (Engine #962), resolved by merged Engine `e6dae5c7`; re-review of `4a2e83e` returned Revise on one defect, the accounting base, corrected in `c499336` with owner agreement and checked by the orchestrator (no Python changes from the new base). Build is authorized within the limits below. The owner approved the executable-line, test-line and time ceilings on 2026-11-02; this design does not raise them.

Accounting base: `35703c29300eddcc2d2988eb84e68c066d24cf16` (main after #240; owner agreement 2026-11-02). The earlier base `ec5e48a` also counted the merged #233 307-row work (196 executable and 36 test lines). Refresh this explicit base only if intervening integration changes the implementation surface, with owner agreement before Build.

Question: can `SolventSpecification.fit()` exercise carbamate-bearing MEA chemistry from one explicitly perturbed chart origin and reach a usable converged solution of the **same 213-row objective** with cost no greater than the accepted endpoint, while remaining in the declared local parameter neighborhood?

Use **equal-or-lower cost** as the falsifier. The accepted vector minimized a 307-row objective, including 94 omitted neutral rows; it is not an established stationary point of the reduced objective. Requiring its coordinates to return within MDEA R2's `1e-5` would test a different optimization problem. This check establishes numerical operation of the declaration-to-fitting path for these rows, bounds and chemistry. It does not identify a new adopted parameter set, establish unique parameters, validate the physical model, or qualify AMP or absorber use.

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

The chart relation is the Engine's affine declaration $q_i=o_i+s_i v_i$. For the table below, define $q_i^*$ as the accepted endpoint value, $s_i$ as the positive scale, and $o_i=q_i^*+s_i d_i$ as the proposed perturbed origin. Enthalpy-shift coordinates instead use the accepted laws as their base, $q_i^*=0$, and represent **incremental** shifts. Keep all original bounds, expressed relative to that base as detailed below.

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

Numerical rank is 14; condition number is **20011.3962**. This is local numerical sensitivity in the retained chart, not practical parameter identifiability or a global basin proof. Bounds remain active and covariance remains conditional. The retained subset gradient is nonzero, including original columns 0 **−0.0066521**, 3 **0.0624510**, 5 **0.218148** and 9 **0.0188745**. This is additional evidence against requiring return to the full-objective vector. Refresh native rank/conditioning at the actual fit endpoint; do not impose equality with these singular values on a shifted chart.

## Execution and numerical falsifier

Use one call through the existing `SolventSpecification.fit()` and native `reg.fit`. No historical producer may be imported during runtime. Preparation may inspect existing owners to translate coordinate declarations; it may not create a second fitting implementation.

1. **Baseline first.** Reproduce #233's 213 endpoint rows, using the owner-approved 2026-11-02 replay rule: **1e-10 relative** on predicted values and total cost; residuals, weighted residuals and row costs satisfy $|\Delta|\le10^{-10}\max(|\mathrm{reference}|,1)$. Report group costs as well. Near-zero residuals amplify relative changes because a log-ratio residual divides the relative prediction change by $|r|$; the cause of the approximately 1e-13 prediction change was not diagnosed. The e6dae5c7 baseline is accepted; retain its comparison beside the notebook evidence. Reject missing rows, nonfinite values or unmet requested equilibrium tolerances. Stable summation must give the declared subset cost. Do not proceed to fitting after a baseline failure.
2. **Declare and check the perturbation.** Bind the fit's `start` to the accepted parameter document and encode the perturbed origins in its coordinate declarations. The native chart evaluated at optimizer zero must produce the table's perturbation, ties, reaction laws and bounds. Use observation-aware `reg.differentiate(parameters, coordinates, observations, optimizer=[0]*14, holds=[], thermochemistry=thermal)` with all 213 unchanged observations. Its completed chart contains the R2/R5 laws including incremental enthalpy shifts; `reg.evaluate_coordinates` alone has empty `reaction_laws` and cannot verify that start. Check every returned row and exact derivative for availability and finiteness. Transport native parameter/law results to fresh observation evaluation; no generic parameter-document writer is needed. The declared origin is the fitting start; verify the actual native `initial_cost` against this independently evaluated start within **1e-8 relative**. If Engine initializes differently, stop and return the discrepancy to Design, rather than adding a second start mechanism or fitting from an unverified start.
3. Require all 213 start predictions finite and available and their weighted-residual vector to differ from the baseline by Euclidean norm **at least 1e-4**. Retain actual coordinate displacements and start cost. This exposes an ignored perturbation; it is not a physical threshold. No adaptive sign, size or start retries.
4. Fit once with `maximum_iterations=60`, `function_tolerance=1e-8`, `parameter_tolerance=1e-10`, `gradient_tolerance=1e-8`, and `maximum_elapsed_time_seconds=1200`. Function tolerance is tighter than the accepted continuation's 1e-6, to leave margin for the cost comparison; it does not claim statistical accuracy. Use the full available CPU count for Engine workers and one thread per numerical-library operation. Record requested workers and actual workers if exposed; do not invent actual counts.
5. Require native **usable converged** termination, at least one accepted nonzero optimizer movement (maximum scaled displacement from the perturbed start > **1e-5**), all original physical bounds and ties satisfied, and all 213 final predictions available, finite and meeting their unchanged requested tolerances. A time/iteration limit or native refusal is not a pass.
6. Freshly replay the fitted native parameters **and fitted reaction laws**, with the same thermal record and original problem declarations. Require native fit/replay cost agreement within **1e-8 relative** and each weighted residual within **1e-8 absolute**, following the retained MEA replay tolerances in `C/spec.json:verification`. Preserve both arrays and every difference. Replaying EOS parameters with unfitted input reactions is invalid.
7. Require $C_f\le45.37796168239049(1+10^{-6})$, an allowance of about **4.54e-5** dimensionless cost, and $C_{start}-C_f\ge10^{-6}$. The former borrows #228 R2's optimizer reproduction allowance; it does not require equality or each group to improve. Report every group's change and final values. The latter ensures actual fitting progress; a returned start alone cannot qualify the path.
8. **Local basin criterion:** relative to the accepted endpoint chart, require $\max_i|(q_{i,f}-q_i^*)/s_i|\le1$ for the 14 independent coordinates. Recover $q_{i,f}$ from the native chart and compare in the table's units, including incremental enthalpies and the R5 coefficient coordinate before enthalpy composition. With shifted origins this is $\max_i|v_{i,f}+d_i|\le1$. This defines the local neighborhood for this check; it does not assert a mathematically unique attraction basin. Original physical bounds also apply. A lower-cost result outside it is retained as a classified **outside-neighborhood** result, not silently promoted or used to relax the criterion.

The chosen criterion can fail even when Engine fits correctly: for example, the reduced objective may favor a distant optimum. Preserve that distinction. One bounded unsuccessful attempt answers this numerical check only; it does not establish a defect or that MEA is unfit for physical use.

## Wheel and ownership

Use Engine **1.2.0** from merged commit **e6dae5c7353ae10e0aa2d8e46055847b9d64bbe4**, wheel `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl`, SHA-256 **83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6**. Verify installed bytes and record Python, NumPy and SciPy versions. Use the isolated environment without changing project pins.

This merged wheel supplies #962's support for tied reaction coordinates with per-problem temperature bounds. The owner accepted its fixed 213-row baseline replay at cost **45.37796168239802**, against **45.37796168239049** (1.659e-13 relative). Preserve R2/R5 declarations: **13 rows at temperature_max 436.85 K and 200 at 393.15 K**, all at temperature_min 293.15 K. Do not narrow domains, drop rows or infer physical validity above 393.15 K. Fitted-parameter export qualification remains separate work. Stop on an absent required native result; do not substitute another wheel automatically.

### Preserve each destination reaction domain

`SolventSpecification.fitted_reactions` currently replaces the entire destination correlation from `chart.reaction_laws`, including `temperature_min` and `temperature_max`. That copies one observation's domain into every reaction set. Replace that overwrite within the existing method: require equal `standard_state_id` between completed law and destination, then copy only `a,b,c,d,e,f,reference_temperature`. Keep each destination's temperature bounds, standard-state identity, stoichiometry and reference unchanged. Fail explicitly on a standard-state mismatch; no conversion or fallback is authorized. The current R2 and R5 declarations share `aqueous-molality-infinite-dilution-water-v1` across both domains.

One persistent two-domain check is earned within the **20 test-line** allowance: transport completed R2/R5 laws with nonzero incremental shifts to the original two reaction sets, assert identical fitted coefficients/reference-temperature representation in both, and assert their original 293.15–393.15 and 293.15–436.85 K bounds survive. Include explicit refusal for a mismatched standard-state identity in this same case. This check must fail with the existing overwrite. It tests mapping; native Engine retains ownership of law composition. No Build code or test is added by this design revision.

**Owner/callers/retirement/evidence:** `src/MEA/solvent_specification.py` continues to own declaration mapping and report transport. The MEA fit runner is its caller. Engine alone owns coordinate transformations, fitting, derivatives, equilibrium, reaction laws and fitted native parameters. Existing MEA and MDEA endpoint checks remain passing references. Retire the whole-correlation replacement in `fitted_reactions`; the existing method remains the sole owner of reaction-result transport. The new exercise consumes that corrected mapping. Do not introduce wrappers, local least-squares logic, source-law copies, parameter JSON updaters or a generic fitted-document export lifecycle.

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

These estimates concern future Build; this Design changes prose and retains numerical probe outputs only.

| File/responsibility | Gross added executable lines | Removed lines |
|---|---:|---:|
| Existing `analyses/solvent_specification_mea/prepare.py`: translate the 14 named coordinates, bind perturbed origins, hashes and separate fit TOML | 35–50 | 0 |
| One MEA analysis fit runner: chart/start checks, existing driver call, fresh native endpoint replay with fitted laws, comparison and timing | 75–100 | 0 |
| `src/MEA/solvent_specification.py`: preserve destination reaction bounds, reject mismatched standard states and transport native results | 5–20 | 1–5 |
| **Total** | **115–170** | **1–5** |

The owner-approved ceiling is **170 gross added executable lines plus 20 test lines**, counted from the explicit base above, including preparation, runner, comments, blanks and any notebook code cells. Deletions buy no additions. Prepared TOML/JSON, retained numerical outputs and notebook prose are reported separately. The two-domain reaction-transport check must fit within 20 test lines without compressing safeguards or weakening the check. If implementation needs more than either ceiling, stop and list the smallest required increase as an owner decision; this revision grants no increase.

Reuse the current packet and comparison reductions; no re-materialization of 213 observations, dependency change, solver code or general-purpose export command is earned. If shared driver fitting behavior changes, run the existing MDEA R2 on its declared wheel and preserve its exact 280-row/nine-coordinate tolerances, within an owner-approved amendment for any extra runtime. Do not silently include that fit in this MEA-only attempt. Endpoint R1/R3/R5 are sufficient when changes only transport reporting fields; unchanged fitting code does not require a fresh MDEA fit.

Build runs the installed CSE helper `/home/tnnrpolley21/Workspaces/Agentic-Coding/plugins/cse/cse-plugin/plugin/scripts/workflow/change_accounting.py` (not copied into this repository) once on its final tree against the fixed base, reviews classification and stops before an expected ceiling overrun. The estimate is not permission to spend all 170 lines or to omit required numerical evidence.

## Retained delivery and failure meaning

After approval, keep separate fit inputs, full native fit report, start and final row predictions/residuals, per-row replay differences, group/subset cost comparisons, named coordinate bounds/displacements/ties, completed reaction laws, rank/singular values, active bounds, projected-gradient norm, trial failures with row IDs and causes, runtime/software/input hashes and budget disposition under this analysis directory. Link all of them from the existing `notebook.qmd`; read retained values rather than rerunning fitting when rendering. Do not overwrite #233 evidence or the accepted parameter bundle. No fitted document export or downstream handoff is promised here.

Report one of: qualified within the stated neighborhood; baseline/input mismatch; unsupported required native capability; invalid coordinate/law declaration; unavailable/nonfinite start or endpoint observation; unusable/nonconverged fitting; cost/progress failure; replay mismatch; outside-neighborhood result; or budget exhaustion. Include actual values, limits and causes for each reported outcome. Rejected intermediate trial solves may occur: retain them and their causes; they do not by themselves invalidate a complete usable converged endpoint.

Stop before execution for changed hashes, unreadable required evidence, changed row definitions or chemistry, or missing authority. Stop and return to Design if the coordinates, bases, ownership, wheel, objective, neighborhood, budget or code surface must change. Never remove troublesome rows, alter calorics or neutral parameters, or repair reference outputs to obtain agreement.

Independent delivered `cse:review` must inspect final code and retained numerical evidence after the single approved attempt. A numerical failure can be a complete bounded study result, but cannot qualify the fitting path. No manuscript use, parameter adoption or new physical-validation claim follows from this check.

## Owner decisions and review gates

The 2026-11-02 owner decisions accept the e6dae5c7 replay under the revised tolerance rule and fix the limits at **170 executable + 20 test lines; 30 min total / 20 min native fit / 60 iterations**. No ceiling increase is requested by this revision.

1. Design readiness: Block on `f1b9b9c` pending #962; re-review of `4a2e83e` (GPT-6 Astra) returned Revise on the accounting base only, corrected in `c499336` with owner agreement. That re-review recomputed the retained numerical evidence, confirmed the reaction-law overwrite with an in-memory probe, and found the perturbation table and stop rules sufficient for Build.
2. This body is the published accepted plan. Build reads it back before starting.
3. The equal-or-lower reduced-cost falsifier, 14 coordinates, authoritative perturbation table and one-scale neighborhood remain the proposed scientific check. No recovery requirement is added.
4. Any extra runtime for the existing MDEA R2 fitting reference, if required by a change to fitting mechanics, needs a separate owner amendment; do not spend beyond this attempt's approved limits. A destination-law transport change is checked by the two-domain case and existing endpoint references.

No owner decision on reaction source, new data, model form or parameter adoption is requested. New data, neutral-group qualification, AMP, Engine edits, physical assessment campaigns, manuscript changes and fitted-document export remain out of scope.

## Design inspection and evidence limits

Read the live #235 body, the full #233 body and its closing comment, #228 R2 and its retained result, the merged MEA packet and endpoint runner, the complete driver including `fit`, the accepted fit declarations/native diagnostics/timings/chemistry coordinates, and `docs/scientific/README.md` and `docs/scientific/CONTEXT.md`. The #228 R2 evidence is a separate MDEA reference: 23 iterations, cost **374.45201342397434**, zero optimizer difference, cost tolerance **1e-6 relative** and coordinate tolerance **1e-5**. Its coordinate-recovery requirement is not transferred to this changed MEA objective.

The original numerical Design probe reduced the retained Jacobian/residual arrays under `agent-heavy` and calculated their singular values and gradient; it ran no Engine objective evaluation or fit. The first probe could not import NumPy in system Python; it was rerun successfully with an existing interpreter through `uv run --no-project`, without modifying any environment or main-checkout file. Sources and reductions are identified above so the numerical inspection is reproducible.

The ignored literature shelf is absent in this worktree. Its README was read from the main checkout without writing there. No paper was newly read or verified against Zotero in this Design, and no new literature-based estimation standard, source equation or physical claim is asserted. Adopted chemistry/source decisions remain those explicitly qualified in #233. The coordinate and time allowances here are numerical-check proposals from retained local evidence, not literature or measurement tolerances. This document is not an independent readiness review.

The continuation probes on e6dae5c7 are retained beside the accepted baseline in `results/design-replay-e6dae5c7/` and interpreted in the notebook. They evaluate the accepted endpoint and the prescribed perturbed start through native differentiation; they perform no optimization and do not qualify the fitting path. No independent review is claimed.
