# Complete MEA solvent-specification reproduction: the 94 deferred rows

## Status, question and scope

Proposed complete issue body for [#236](https://github.com/tannerpolley/Amine-Thermodynamics/issues/236), prepared 2026-11-02 against `ec5e48a7a861d335540cd674da6ea514d29be0f7`. Design only. This document is the requested committed handoff to the accountable owner; it has not been published as the issue body or independently reviewed. Build requires independent `cse:review` **Ready**, owner approval of the code ceiling, and owner publication/read-back of the accepted body. No Build is authorized by this draft.

Can the generic solvent-specification driver reproduce the accepted endpoint's remaining 94 objective rows and retain agreement across all 307, using the same declarations, construction domains, native continuation and evaluation parameters as the existing numerical owner?

The result sought is fixed-endpoint numerical verification of declaration mapping. Add the 39 Kiepe CO₂–water bubble pressures, 25 Cai water–MEA bubble temperatures, 25 Cai vapor water fractions, and five CO₂-free mass densities. Preserve the merged #233 packet's 213 reactive rows. These are previously fitted observations; agreement establishes neither independent physical validation nor absorber qualification. Parameter estimation, parameter adoption, new source choices, uncertainty estimation, AMP, manuscript changes, generic phase-search qualification, and Engine edits are outside this issue.

The [#233 closing comment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/233#issuecomment-6531490102) records merged commit `78b2ad8`, exact reproduction of 213 rows, and independent execution tracing. Its cost is 45.37796168239049. Preserve that result while removing only the documented neutral-group limitations.

## Reference, inputs and falsifier

Let `E` mean `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/` and `S` mean `analyses/mea_parameter_bundle/results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/spec.json`.

| Owner | SHA-256 |
|---|---|
| `E/reported-parameters.json`, accepted unamended evaluation endpoint | `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91` |
| `E/full-replay.json`, numerical reference | `aeb3331cf95cb174faa9cfa5891e887dbae0829448b5c67a2da17727ed386560` |
| `E/fitted-rows.csv`, target identities, groups and source declarations | `e18efef61548d20e40578a2223cb203dd903ed288c02b94ab24009d6b861fb44` |
| `E/fit-summary.json`, retained group reductions | `7968c9ce1ca9947d70795787afedccf4f90786a77196e890412a13871f37d0fb` |
| `E/replay-identity.json`, prior endpoint comparison | `96069e3402f3d3d6a26f12f155d9bde730ff838c43f706a85fd0412166fa3f27` |

Use merged Engine `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, wheel `build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`, SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`. Verify installed package bytes against the wheel. Do not change repository dependency pins, import an Engine source checkout, or substitute MDEA's d5138209 wheel.

Hash `S`, every consumed source table/request/packet, the construction parameter copy and its source, calorics, and prepared declarations. Preserve existing endpoint-copy equality checks and #233's caloric/chemistry declarations, including the explicit anchors and amended reaction bounds already materialized for request-backed rows. The current packet owns species ordering, element formulas, analytical incidence and neutral references. No new reaction law, standard-state conversion, caloric polynomial or equation of state is introduced.

The complete falsifier is:

1. Exactly the same 307 unique target IDs in reference order, including exactly the 94 added IDs selected by the three group labels below. Retain observed values, units, residual forms, scales, weights, original source identities and source locators without repartitioning or reweighting.
2. Compare complete native problem/observation declarations against `fit_observations.stage2_rows` and `stage6_rows`, including fixed/free variables, feeds, phase names/supports/amount constraints, guesses, reactions/references, tolerances, constructor arguments and the construction parameter identity. For continuation compare the starting declarations and the runtime transferred guesses separately.
3. All predictions must be `Available`, finite, and meet the native requested numerical tolerance. A failed or dependent unavailable row makes the objective unavailable; never report a partial sum as the objective.
4. For each prediction, residual, weighted residual and row cost, every group cost, the 94-row subtotal, the preserved 213-row subtotal, and the complete objective, require

   $$\frac{|a-b|}{\max(|a|,|b|)}\leq10^{-10}.$$

   This is the accepted serialized-replay numerical comparison, not an experimental uncertainty. All compared reference row fields are nonzero; minimum absolute weighted residual across the 307 is approximately $8.78\times10^{-5}$. No extra absolute tolerance is needed. Retain every difference and the first differing target.
5. Use the existing objective definition $C=\tfrac12\sum_j w_jr_j^2$, weighted residual $\sqrt{w_j}r_j$, and stable summation. Engine owns residual formation, including native log-ratio pressure residuals and scaled difference residuals. The runner only weights and reduces returned residuals.

| Exact group label | Rows | Reference dimensionless cost |
|---|---:|---:|
| `common149` | 149 | 23.860996312136727 |
| `restored species` | 7 | 2.4486746519412517 |
| `Jakobsen` | 6 | 13.122182452954206 |
| `Kiepe` | 39 | 0.0006790194987316589 |
| `CO2-free density` | 5 | 11.625713440586951 |
| `Cai` | 50 | 91.87458520309771 |
| `loaded density` | 47 | 0.5654031419421082 |
| `Cp` | 4 | 5.380705123416196 |
| Preserved reactive subtotal | 213 | 45.37796168239049 |
| Added subtotal | 94 | 103.50097766318339 |
| Complete objective | 307 | **148.87893934557388** |

The complete objective is the serialized endpoint replay, not the slightly different native-fit final cost 148.87893934555717. Common-149 is included once. The six broader assessment modes and overlapping physical comparisons remain outside this calculation.

## Declarations and numerical method

### Construction and evaluation parameters

`fit_observations.stage2_rows` copies the endpoint mapping, applies `S.cases[0].neutral_domain` only to the two declared `neutral_domain_ids`, and builds `Parameters` from that amended mapping. It uses those same amended parameters for observation construction **and Kiepe continuation solves**. `fit_observations.replay` creates its evaluation mixture from the unamended endpoint. Preserve all three uses explicitly.

Materialize one shared construction document from that exact transformation: domain IDs `mea-candidate-293-15-to-393-15-k` and `cai-1996-neutral-refit`, temperature bounds 293.15–436.85 K, pressure bounds 1–100000000 Pa and `kind = fit-range`. Check by structural comparison that no other document field changes. Hash both documents and retain the field differences and source case. This is copied construction metadata, not a new fitted parameter set or a claim of reactive validity through 436.85 K.

Add an optional hash-bound `observation_parameters` reference per dataset, defaulting to the selected endpoint parameters when absent. The driver loads each distinct document once and retains its identity on the observation record. Assign the amended document to newly admitted stage-2 datasets; retain the existing 213-row construction behavior unless exact declaration comparison requires its equivalent amended document. Do not globally amend `self.parameters`, `self.model`, the endpoint JSON, or fitting coordinates. Construction and continuation mixtures use the declared construction parameters with the existing thermochemistry; objective prediction always uses `self.model` from the unamended endpoint. The shared declaration, rather than a dataset name, selects the document.

### Kiepe: independent isotherms with sequential guesses

The source declaration has 39 pressure observations at 313.20–393.17 K, with source pressure values/initial guesses spanning 95090–9257600 Pa. Preserve the actual source order within each temperature, not an invented sorting by pressure or composition. Each problem has fixed temperature, free pressure, liquid amount free, vapor amount pinned to zero, and the row's neutral support/feed/vapor guess. Pressure observations use native `log_ratio` with weight 1/39.

Preparation declares continuation group and numeric order explicitly on each participating row. A group denotes one isotherm at this construction document. The generic driver contains no `kiepe-` prefix check, temperature-specific policy or species-name branch. Empty continuation declarations retain existing behavior. Reject duplicate group/order or a group with conflicting parameter identities, fixed temperatures or phase/support declarations rather than guessing an order.

After loading problems and thermochemistry, execute each declared group once in its declared order:

- Start each isotherm from its own original source guesses. Carry no state from another isotherm or prior run.
- Before each later solve, set only free-pressure guess to the predecessor's native pressure, each phase's composition guess to the predecessor's native mole fractions mapped by model component order and declared support, and packing guess to its native packing fraction. Phase identity/order must agree. Do not transfer temperature, feed, phase amounts, chemical potentials or density as an additional guess.
- Solve **every** Kiepe problem, including the first and last, with `eq.solve_equilibrium` on the amended construction mixture. Retain native success, message, residuals and the transferred quantities with predecessor identity and document hash. The problem retains the incoming guesses for observation construction; do not replace them with its own solved result.
- Construct pressure observations from those problems using the amended construction parameters. Predict them against the unamended endpoint, exactly as replay does. A continuation solve is not the objective pressure prediction.

Do not freeze solved continuation guesses into runtime source inputs. Preparation may run the old constructor as a diagnostic reference; specification execution must recompute its declared continuation through the generic driver. No continuation caching between executions or qualification of changing-parameter fitting is included.

### Cai: free-temperature bubble states and assessment domain

The 50 rows represent 25 distinct states, each paired temperature and vapor-water-fraction observations. Preserve shared state identity, fixed pressure, free-temperature guess, feed, phase declarations and guesses. Source temperature guesses are 362.81–431.85 K at 66660 or 101330 Pa. These guesses are not solved-domain bounds. Temperature difference scale is 1 K; water-fraction difference scale is 0.01; retained weights are 1. Use existing recursive binding and `eq.problem_from_mapping` with `T = {free = true, guess = ...}`. Extend preparation's fixed-only `p.temperature.value` serialization to preserve the native free/fixed designation; pressure mapping already demonstrates the required form.

Replace the driver's unconditional `domain[0] <= problem.T <= domain[1]` with a fixed-temperature-only check. A free-variable guess is not the physical solved temperature. Preserve fixed-temperature refusal outside its declared domain, including its cause; a refusal must remain reportable without the runner assuming numerical fields exist.

Use 293.15–436.85 K as the declared Cai assessment interval from the existing case amendment. Do not derive it from the minimum/maximum observed temperatures, and do not widen any reactive assessment interval. In the MEA runner, perform one native equilibrium solve per unique Cai state on the **unamended evaluation mixture**, from the same problem used for prediction. Retain `state.temperature`, success, message and residuals; require finite solved temperature in the declared interval and the problem's native residual tolerance before accepting either member of that pair. Check the temperature observation's returned value against that native solved temperature at the same relative comparison tolerance. A vapor fraction cannot substitute for solved temperature. Predictions still come from `reg.predict`; do not recalculate mole fractions or residuals in the runner.

The paper-wheel prediction object has no solved-state/temperature field. This explicit native solve in the runner is therefore required for the domain check, including the fraction member. It adds no local equilibrium algorithm. Grouping the paired state in preparation avoids 50 duplicate domain solves. Do not use the amended construction mixture for this evaluation-domain check.

### Five CO₂-free densities

No new density mechanism is earned. `shared_evaluation.unloaded_density_problem` constructs a reactive single liquid with one mol analytical MEA, water determined from the existing mass basis at 30 wt% MEA, and exactly zero analytical carbon. Preserve its complete nine-species phase support, reactions, neutral reference, 1e-10 row tolerance and the existing amended reaction bounds. This differs from the separate loaded-density nominal-zero rows with a small nonzero CO₂ seed; never substitute those feeds.

The five states are 298.15–353.15 K, with the retained pressure assumption 100000 Pa, density scale 0.5 kg/m³ and weight 10. Observation construction uses the amended stage-2 parameters, evaluation the original endpoint. Existing templates, feed binding, reaction mapping and `phase_density` with `mass_basis = true` suffice. Preserve the source locator's unreported experimental pressure; this issue does not resolve that physical limitation.

## Generic changes, owners and removal

| Change | Owner and callers | Justification and removed limitation |
|---|---|---|
| Optional per-dataset construction parameter document, with common hash checking and reuse | `src/MEA/solvent_specification.py`; MEA preparation declares it, MEA/MDEA callers retain the default | Replaces the assumption that every constructor and continuation solve must use evaluation parameters; preserves old callers without a solvent branch. |
| Declared continuation group/order and native guess transport | Generic driver after thermochemistry initialization; MEA preparation supplies initial declarations and group/order | Replaces the historical runtime dependency for the admitted continuation. Engine owns all equilibrium solves. No copy of `_phase_payload` with its MEA component constant: map native arrays using this model's IDs and this problem's supports. |
| Fixed-only temperature precheck | Generic `prediction`; MEA runner checks native solved free temperature | Removes the `eq.Free` TypeError while keeping assessment-domain refusals. The runner owns acceptance of Cai's solved domain; the driver does not infer temperature from observation kind. |
| Materialize the 94 declarations, preserve free variables and state pairing | Existing `analyses/solvent_specification_mea/prepare.py` and TOML/CSV/JSON inputs | Reuse existing transforms, chemistry, recursive equality, source ordering and input hashing. No composition-expression language or new density constructor. |
| Complete reductions, solved-domain evidence and dependent-failure reporting | Existing `analyses/solvent_specification_mea/run.py` and notebook | Replace fixed 213 counts/group lists with the complete declared comparison; keep 213 and 94 subtotals visible. No second residual calculator. |

Historical fitting scripts remain read-only source evidence and preparation owners; they are not runtime dependencies. Runtime may load only the materialized packet, generic driver and installed Engine/numerical dependencies. No `fit_observations`, `fit_campaign`, `shared_evaluation` import or historical `.py.txt` execution is permitted during reproduction. Preparation can use those owners, including a no-continuation case copy to obtain Kiepe's original problem declarations, then the unchanged case for comparison of runtime continuation. This separates original inputs from computed guesses without modifying the historical owner.

Retain endpoint-only empty coordinates/phase-state lists and `start = endpoint`; never call `fit()`. Existing MDEA fitting/phase owners are unchanged. Recheck its established R1/R3/R5 endpoint falsifiers on d5138209 with the accepted tolerances. Preserve capped-observation result transport and #233's optional saturation-field unavailability handling. Do not add fitting or phase reruns unless a shared owner actually changes; such a change returns to Design.

## Failures, evidence and implementation sequence

A continuation failure includes a refused/failed native solve, missing required pressure/composition/packing data, nonfinite returned quantities or a native residual outside the declared row tolerance. Record the failing target, predecessor, construction document identity, native message and available diagnostics. Stop that isotherm immediately; retain all later members as dependent unavailable with the failing predecessor/cause. Never reuse the last successful state across the failure, retry with another start, drop a member, or seed the next isotherm from this one. Independent isotherms and unrelated rows may finish to collect diagnostics. No partial objective passes.

Treat a prediction refusal, exception, missing field, nonfinite value, unmet numerical tolerance or outside-domain solved temperature as an explicit failure. Retain it without synthesizing zeros or indexing absent residual fields. A native exception must retain its type/message. An optional saturation field absent on an ordinary observation remains explicitly unavailable and does not itself fail the observation; admitted pressure, temperature, fraction and density calculations and their required diagnostics must exist.

After Ready, code-limit approval and publication/read-back:

1. Freeze Build's actual base and inventory the packet/endpoint/reference/wheel hashes before changes. Verify exact group membership and the 307 unique IDs. Preserve accepted bundle evidence unchanged.
2. Extend the existing preparation and generic driver within the approved ceiling. Check that the construction document changes only declared domain fields. Compare every materialized declaration and the runtime continuation guesses against native owner construction, including independent isotherm starts and Cai pairing.
3. Execute fresh 94-row and complete 307-row comparisons through the materialized specification under `agent-heavy` as a background shell. A complete pass can produce both subtotals; a separate duplicate full pass is unnecessary. Record actual compute wall time separately from admission/environment setup time. Retain predictions, native continuation results, solved-temperature checks, every row difference, group/subtotal/total reductions and the first failing target.
4. Run the existing MDEA R1/R3/R5 checks in their separate pinned environment. Use the full Cai rows to exercise free-temperature success and the density rows for exact-carbon-free mapping. Add only focused failure checks: fixed and solved temperature outside the declared interval; and a native refused continuation whose later members remain unavailable while another group starts independently. Do not add parser/helper coverage. Reuse a real native failure case or the exact exposed failure if one occurs; do not turn the production path into an injectable solver framework.
5. Extend `notebook.qmd` from retained results with counts, cost, maximum field differences, domains, failure evidence, timing and claim limits. Use `cse:summarize` for that stage. Independent delivered `cse:review` and investigator acceptance remain required after implementation. A successful command is not the result.

Keep results in the existing analysis's `results/` directory and update its preparation provenance and runtime inventory. Preserve complete per-row identities and diagnostics; add no parallel plan store. Build runs `scripts/workflow/change_accounting.py` against its frozen base and reports the final commit and counted surface.

## Runtime and incremental code estimate

The retained `E/execution.json` reports 9.133172251997166 s wall for the original 307-row replay-identity invocation. #233's final 213-row specification pass took 7.2805 s and MDEA R1/R3/R5 took 12.93 s. These are reference timings, not a new performance requirement. Design's read-only paper-wheel probe constructed the 107 stage-2 observations (including native Kiepe continuation), evaluated five mapped densities, and solved/evaluated the 25 Cai temperature states in approximately 0.56 s inside the Python process on this machine; it was not a complete specification run.

Plan **10–30 s for a fresh complete MEA pass**, and **under two minutes for preparation, full replay and report checks**, excluding environment provisioning and `agent-heavy` admission. Allow several minutes for combined MEA/MDEA and focused failure checks. Sequential continuation is required within an isotherm; no parallel campaign is necessary. Record actual worker and numerical-thread settings rather than carrying forward the historical scripts' thread settings as a new policy. No fit or hours-scale campaign is included.

Incremental gross executable additions relative to the frozen Build base, beyond merged #233:

| Existing file/responsibility | Added lines | Removed lines |
|---|---:|---:|
| Generic driver: document selection, continuation/typed failures, fixed-only domain check | 85–115 | 5–12 |
| MEA preparation: 94 declarations, free variables, original guesses, amended document and equality evidence | 45–65 | 10–20 |
| MEA runner: solved Cai domain checks, full reductions and failure evidence | 25–40 | 5–10 |
| **Executable total** | **155–220** | **20–42** |

Allow **25–40 additional test lines** for numerical domain/failure invariants. Existing MDEA checks and the anchor check are reused. Comments, blanks, preparation/comparison scripts and any notebook code cells count in executable additions; no notebook code is currently proposed. TOML, generated inputs/results and notebook prose are reported separately. Deletions buy no allowance. No new dependency is proposed.

Recommend an owner-set ceiling of **220 gross added executable lines plus 40 test lines** for this incremental task. This is an estimate and recommendation, not approval and not a reuse of #233's exhausted 230 + 30 allowance. Stop before adding code beyond the approved limit; propose the smallest revised estimate with reasons if needed, without compression or removed safeguards to conceal an overrun.

## Stop conditions and open owner decisions

- No Build before independent readiness **Ready**, owner approval of the incremental code ceiling, and publication/read-back by the accountable owner. This design task ends with the requested local commit; it does not publish, push or delegate review.
- Stop on any required input/endpoint/wheel hash mismatch, unknown row identity or unreadable scientific owner. Do not edit accepted reference results to obtain agreement.
- Stop dependent continuation at the first failure as specified above. Retain mismatches and independent diagnostic results, but never accept partial costs or weakened tolerances.
- Return to Design for any needed parameter-value change, domain change beyond the exact retained construction amendment, additional transferred state variable, new continuation algorithm, unsupported required native quantity, or change of Engine wheel. Do not implement an Engine fix or a local thermodynamic substitute.
- Return to Design if fixed-endpoint continuation is being extended to fitting, if new phase/fit behavior must change, or runtime needs historical producers or a second chemistry owner. No hidden retries, new starts, reweighting or new physical acceptance thresholds.
- Stop before a code-limit overrun or scope expansion. Report first differing target and all available comparisons for an unexplained numerical mismatch; correct only demonstrated declaration/transport defects within the accepted design.

The scope and numerical falsifier are supplied by #236. The remaining **owner decision is the incremental executable/test ceiling** (recommendation 220 + 40). Independent readiness and owner publication/read-back are open gates. No reaction-source selection, new fitting strategy or model-adoption decision is left to Build.

## Design evidence and reading limits

Read live #236 and #233 bodies/comments, including #233's closing comment; the merged packet, driver, `stage2_rows`, `replay`, `stage6_rows`, `unloaded_density_problem` and `_phase_payload`; and the archived design. The archive tag points to the reduced 213-row revision, so the original continuation/document/Cai proposals were also recovered from first-design commit `9c0ed61`. The supplied readiness findings 2 and 3 are resolved explicitly above: fixed-only precheck plus native solved-temperature assessment, and amended construction/continuation versus unamended replay.

Read-only reductions rechecked hashes, all group counts/costs and nonzero reference fields. A paper-wheel probe verified installed bytes, reproduced all five mapped density predictions exactly (1010.0425155475415, 1003.3192439783633, 998.0678517477409, 986.1949402864064 and 979.7270533325251 kg/m³), and inspected native prediction fields. The first Cai state gave native solved temperature and temperature prediction both 433.6729375243276 K, illustrating why an observed-temperature range cannot be used as its assessment interval. These are mapping/solver diagnostics, not new physical results or completed driver qualification. Temporary probe mapping attempts first exposed the distinction between Python `Problem` fields and native observation fields and the need for declaration mappings rather than raw native reaction objects; only the corrected existing-driver materialization produced the five density comparisons.

The ignored literature shelf is absent in this worktree. Its README was read at the main checkout without writing there. No paper-derived equation, parameter, source conversion or physical-validity judgment was changed; source quantities and domains above describe the accepted retained declarations. This Design did not independently reread or authenticate the underlying Cai/Kiepe/density papers and does not make a new literature-backed assessment of them. Source uncertainty, extrapolation and experimental-pressure limitations remain as recorded by their existing owners. No Build, fit, Engine edit, main-checkout write, push, subagent or independent readiness review occurred.
