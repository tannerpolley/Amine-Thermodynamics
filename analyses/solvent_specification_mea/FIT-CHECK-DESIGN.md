# Test the solvent-specification fitting path on reactive MEA rows

## Status and requested outcome

Proposed replacement body for [#235](https://github.com/tannerpolley/Amine-Thermodynamics/issues/235), prepared 2026-11-02. **Design only; not authorized for Build.** Independent readiness review must return **Ready**, and the owner must accept the executable-line and time ceilings below before execution. This document is the requested committed publication draft; the accountable owner publishes the accepted body and reads it back. No issue mutation, fit, Engine edit or implementation is part of this delivery.

Inspected and proposed accounting base: `ec5e48a7a861d335540cd674da6ea514d29be0f7`. Refresh this explicit base only if intervening integration changes the implementation surface, with owner agreement before Build.

Question: can `SolventSpecification.fit()` exercise carbamate-bearing MEA chemistry from one explicitly perturbed chart origin and reach a usable converged solution of the **same 213-row objective** with cost no greater than the accepted endpoint, while remaining in the declared local parameter neighborhood?

Choose **equal-or-lower cost**, not recovery of the accepted vector. The accepted vector minimized a 307-row objective, including 94 omitted neutral rows; it is not an established stationary point of the reduced objective. Requiring its coordinates to return within MDEA R2's `1e-5` would test a different optimization problem. This check establishes numerical operation of the declaration-to-fitting path for these rows, bounds and chemistry. It does not identify a new adopted parameter set, establish unique parameters, validate the physical model, or qualify AMP or absorber use.

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

The perturbation is one tenth of each declared scale: interaction changes of 0.001, diameter changes of 0.01 Å, slopes/dispersion changes of 1 K, a native R5 coefficient change of about 18.42 K, and enthalpy changes of 250 J/mol. Active-bound entries move inward. Other signs follow the retained subset gradient, creating a repeatable small displacement rather than a new multistart search. These are proposed numerical exercise sizes, not measurement uncertainties or literature-derived physical acceptance ranges.

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

1. **Baseline first.** Reproduce #233's 213 endpoint rows, including every prediction, residual, weighted residual, row and group cost within its existing **1e-10 relative** tolerance. Reject missing rows, nonfinite values or unmet requested equilibrium tolerances. Stable summation must give the declared subset cost. Do not proceed to fitting after a baseline failure.
2. **Declare and check the perturbation.** Bind the fit's `start` to the accepted parameter document and encode the perturbed origins in its coordinate declarations. The native chart evaluated at optimizer zero must produce the table's perturbation, ties, reaction laws and bounds. Use `reg.evaluate_coordinates` with no holds and the fixed thermochemistry. Transport native parameter/law results to fresh observation evaluation; no generic parameter-document writer is needed. The declared origin is the fitting start; verify the actual native `initial_cost` against this independently evaluated start within **1e-8 relative**. If Engine initializes differently, stop and return the discrepancy to Design, rather than adding a second start mechanism or fitting from an unverified start.
3. Require all 213 start predictions finite and available and their weighted-residual vector to differ from the baseline by Euclidean norm **at least 1e-4**. Retain actual coordinate displacements and start cost. This exposes an ignored perturbation; it is not a physical threshold. No adaptive sign, size or start retries.
4. Fit once with `maximum_iterations=60`, `function_tolerance=1e-8`, `parameter_tolerance=1e-10`, `gradient_tolerance=1e-8`, and `maximum_elapsed_time_seconds=1200`. Function tolerance is tighter than the accepted continuation's 1e-6, to leave margin for the cost comparison; it does not claim statistical accuracy. Use the full available CPU count for Engine workers and one thread per numerical-library operation. Record requested workers and actual workers if exposed; do not invent actual counts.
5. Require native **usable converged** termination, at least one accepted nonzero optimizer movement (maximum scaled displacement from the perturbed start > **1e-5**), all original physical bounds and ties satisfied, and all 213 final predictions available, finite and meeting their unchanged requested tolerances. A time/iteration limit or native refusal is not a pass.
6. Freshly replay the fitted native parameters **and fitted reaction laws**, with the same thermal record and original problem declarations. Require native fit/replay cost agreement within **1e-8 relative** and each weighted residual within **1e-8 absolute**, following the retained MEA replay tolerances in `C/spec.json:verification`. Preserve both arrays and every difference. Replaying EOS parameters with unfitted input reactions is invalid.
7. Require $C_f\le45.37796168239049(1+10^{-6})$, an allowance of about **4.54e-5** dimensionless cost, and $C_{start}-C_f\ge10^{-6}$. The former borrows #228 R2's optimizer reproduction allowance; it does not require equality or each group to improve. Report every group's change and final values. The latter ensures actual fitting progress; a returned start alone cannot qualify the path.
8. **Local basin criterion:** relative to the accepted endpoint chart, require $\max_i|(q_{i,f}-q_i^*)/s_i|\le1$ for the 14 independent coordinates. Recover $q_{i,f}$ from the native chart and compare in the table's units, including incremental enthalpies and the R5 coefficient coordinate before enthalpy composition. With shifted origins this is $\max_i|v_{i,f}+d_i|\le1$. This defines the local neighborhood for this check; it does not assert a mathematically unique attraction basin. Original physical bounds also apply. A lower-cost result outside it is retained as a classified **outside-neighborhood** result, not silently promoted or used to relax the criterion.

The chosen criterion can fail even when Engine fits correctly: for example, the reduced objective may favor a distant optimum. Preserve that distinction. One bounded unsuccessful attempt answers this numerical check only; it does not establish a defect or that MEA is unfit for physical use.

## Wheel and ownership

Use merged Engine **3e83e19ccc771b51d8ebc038931ab25192f4c5b5**, wheel `build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`, SHA-256 **0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804**. Verify installed bytes and record Python, NumPy and SciPy versions as #233 does. Use an isolated environment without changing project pins.

Reason: this wheel produced the accepted MEA fit and its derivative evidence, and #233 already qualifies the 213-row mapping on it. Its public fitting, reaction-coordinate, enthalpy-shift, native-chart and fitted-parameter operations cover this check. A serialized fitted parameter export is not required. Do not upgrade just to obtain `document_mapping`; export qualification is separate work. If an essential fitting or reaction-result field is absent, stop with the exact missing operation. A newer wheel requires owner approval and renewed numerical comparison, not automatic substitution.

**Owner/callers/retirement/evidence:** `src/MEA/solvent_specification.py` continues to own declaration mapping and report transport. The MEA fit runner is its caller. Engine alone owns coordinate transformations, fitting, derivatives, equilibrium, reaction laws and fitted native parameters. Existing MEA and MDEA endpoint checks remain passing references. No old implementation is displaced: the new capability is one declared MEA fit exercise. Do not introduce wrappers, local least-squares logic, source-law copies, parameter JSON updaters or a generic fitted-document export lifecycle.

## Runtime, hard limits and stop rule

Retained evidence separates the last continuation from cumulative work:

- `C/run/fit/timing.json`: **40.5175 s wall**, **448.4418 s CPU** for the final invocation; **16718.5175 s wall (4.64 h)** and **128524.9118 s CPU** cumulative, including earlier charged work.
- `C/run/fit/native.json`: that invocation used **8 iterations**, **9 residual evaluations**, **6 Jacobian evaluations**, no trial failures, starting cost **149.21952645122371**, ending at **148.87893934555717** on all 307 rows.
- `C/command-timing.json`: the separate information call took **216.65 s wall**; the combined final information/fit commands took **257.17 s wall**. Do not charge the 4.64 h as one 40 s fresh fit.
- The #233 materialized 213-row fixed replay took **7.28045 s wall**, with one worker and one numerical thread (`results/runtime.json`). It is not a fitting benchmark.

Estimate **5–20 minutes active wall** for preparation checks, one nearby 14-coordinate/213-row fit and fresh final replay on a comparable machine. The final continuation's roughly five wall seconds per iteration would suggest minutes for 60 iterations; permit substantially more for the new perturbation, rejected steps, derivative work and shared-machine load. This is an engineering planning estimate, not a new timing measurement or assurance of convergence. The cumulative 4.64 h warns against an unrestricted refit campaign.

Propose a **hard 1800 s (30 min) active-wall ceiling** for the complete numerical attempt, with **1200 s (20 min) maximum inside native fitting**, and at most **60 iterations**. Allow at most 300 s preflight and 300 s final replay/reporting, within the same total. Run the long command itself as a background shell through `agent-heavy`; start the active timer after memory admission. Record queue wait separately. The outer timer must terminate only its captured child process/process group if native fitting or an evaluation overruns. Preserve the log and completed diagnostics on timeout; use atomic writes for completed result records. No timeout or iteration exhaustion qualifies as convergence.

At any hard limit, stop without automatic continuation, extra starts, larger boxes, relaxed tolerances or increased time. If no complete final replay fits inside the remaining time, retain the partial evidence and classify the outcome as budget-limited. Do not report a partial sum as a final objective. The owner must authorize any subsequent numerical attempt.

## Proposed implementation surface and code ceiling

These estimates concern future Build; this Design changes only this document.

| File/responsibility | Gross added executable lines | Removed lines |
|---|---:|---:|
| Existing `analyses/solvent_specification_mea/prepare.py`: translate the 14 named coordinates, bind perturbed origins, hashes and separate fit TOML | 35–50 | 0 |
| One MEA analysis fit runner: chart/start checks, existing driver call, fresh native endpoint replay with fitted laws, comparison and timing | 75–105 | 0 |
| `src/MEA/solvent_specification.py`: only missing native report fields needed for final replay/diagnostics, if inspection confirms a gap | 0–15 | 0–5 |
| **Total** | **110–170** | **0–5** |

Request a ceiling of **170 gross added executable lines**, counted from the explicit base above, including preparation, runner, comments, blanks and any notebook code cells. Deletions buy no additions. Prepared TOML/JSON, retained numerical outputs and notebook prose are reported separately. Add **zero persistent test lines**: the retained numerical analysis itself exercises the falsifier, and no new numerical method is introduced. If Build finds a distinct shared-mapping defect requiring a persistent numerical case, return with that exact case and a separate proposed test allowance.

Reuse the current packet and comparison reductions; no re-materialization of 213 observations, dependency change, solver code or general-purpose export command is earned. If shared driver fitting behavior changes, run the existing MDEA R2 on its declared wheel and preserve its exact 280-row/nine-coordinate tolerances, within an owner-approved amendment for any extra runtime. Do not silently include that fit in this MEA-only attempt. Endpoint R1/R3/R5 are sufficient when changes only transport reporting fields; unchanged fitting code does not require a fresh MDEA fit.

Build runs `scripts/workflow/change_accounting.py` once on its final tree against the fixed base, reviews classification and stops before an expected ceiling overrun. The estimate is not permission to spend all 170 lines or to omit required numerical evidence.

## Retained delivery and failure meaning

After approval, keep separate fit inputs, full native fit report, start and final row predictions/residuals, per-row replay differences, group/subset cost comparisons, named coordinate bounds/displacements/ties, completed reaction laws, rank/singular values, active bounds, projected-gradient norm, trial failures with row IDs and causes, runtime/software/input hashes and budget disposition under this analysis directory. Link all of them from the existing `notebook.qmd`; read retained values rather than rerunning fitting when rendering. Do not overwrite #233 evidence or the accepted parameter bundle. No fitted document export or downstream handoff is promised here.

Report one of: qualified within the stated neighborhood; baseline/input mismatch; unsupported required native capability; invalid coordinate/law declaration; unavailable/nonfinite start or endpoint observation; unusable/nonconverged fitting; cost/progress failure; replay mismatch; outside-neighborhood result; or budget exhaustion. Include actual values, limits and causes rather than a success flag alone. Rejected intermediate trial solves may occur: retain them and their causes; they do not by themselves invalidate a complete usable converged endpoint.

Stop before execution for changed hashes, unreadable required evidence, changed row definitions or chemistry, or missing authority. Stop and return to Design if the coordinates, bases, ownership, wheel, objective, neighborhood, budget or code surface must change. Never remove troublesome rows, alter calorics or neutral parameters, or repair reference outputs to obtain agreement.

Independent delivered `cse:review` must inspect final code and retained numerical evidence after the single approved attempt. A numerical failure can be a complete bounded study result, but cannot qualify the fitting path. No manuscript use, parameter adoption or new physical-validation claim follows from this check.

## Owner decisions and review gates

The proposed choices are concrete; none is approved merely by this draft:

1. Accept the **equal-or-lower reduced-objective cost** falsifier, the 14 reactive coordinates, the deterministic 0.1-scale perturbation and the one-scale local-neighborhood criterion. Recovery of the original full-objective parameter vector is explicitly excluded.
2. Approve **170 gross added executable lines, zero new persistent test lines**, against the fixed base, or set a different ceiling before Build.
3. Approve the **30 min total / 20 min native fit / 60 iteration** hard limits for one numerical attempt. A further attempt needs new authority.
4. Obtain independent design-readiness **Ready**, incorporate required findings, then publish and read back the accepted issue body. This worker is prohibited from spawning a reviewer or publishing the draft; these gates remain with the accountable owner.

No owner decision on reaction source, new data, model form or parameter adoption is requested. New data, neutral-group qualification, AMP, Engine edits, physical assessment campaigns, manuscript changes and fitted-document export remain out of scope.

## Design inspection and evidence limits

Read the live #235 body, the full #233 body and its closing comment, #228 R2 and its retained result, the merged MEA packet and endpoint runner, the complete driver including `fit`, the accepted fit declarations/native diagnostics/timings/chemistry coordinates, and the scientific README/CONTEXT owners. The #228 R2 evidence is a separate MDEA reference: 23 iterations, cost **374.45201342397434**, zero optimizer difference, cost tolerance **1e-6 relative** and coordinate tolerance **1e-5**. Its coordinate-recovery requirement is not transferred to this changed MEA objective.

The only numerical Design probe reduced the retained Jacobian/residual arrays under `agent-heavy` and calculated their singular values and gradient; it ran no Engine objective evaluation or fit. The first probe could not import NumPy in system Python; it was rerun successfully with an existing interpreter through `uv run --no-project`, without modifying any environment or main-checkout file. Sources and reductions are identified above so the numerical inspection is reproducible.

The ignored literature shelf is absent in this worktree. Its README was read from the main checkout without writing there. No paper was newly read or verified against Zotero in this Design, and no new literature-based estimation standard, source equation or physical claim is asserted. Adopted chemistry/source decisions remain those explicitly qualified in #233. The coordinate and time allowances here are numerical-check proposals from retained local evidence, not literature or measurement tolerances. This document is not an independent readiness review.
