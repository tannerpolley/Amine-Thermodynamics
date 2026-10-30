# Qualify the solvent-specification driver on the accepted MEA endpoint

## Status and authority

Proposed complete body for [Amine-Thermodynamics #233](https://github.com/tannerpolley/Amine-Thermodynamics/issues/233), prepared 2026-10-30. Design only. The owner publishes this body after independent `cse:review` readiness review. On 2026-10-30 the owner reduced the scope to 213 reactive rows and set a ceiling of 230 gross added executable lines plus 30 test lines. This draft authorizes no Build, fit, parameter adoption, manuscript update or Engine change. Independent readiness review returned **Revise**. It passed the reference, hashes, group table, R4/R5 laws, no-reapplied-shift rule and calorics, and independently reproduced all 307 reference rows at cost 148.87893934557388 with zero differences. This revision addresses the reduced scope and reporting/failure findings; renewed readiness review remains required.

Inspected base: `e5314f96b536985e36ad6ec0a7f965869bc9e911`. This worktree contains only this design addition. The manuscript helper actually lives at `docs/scientific/latex/scripts/final_rerun_tables.py`; its `a7_presentation.checked()` call identifies the accepted endpoint and 307 rows. The October 20 endpoint is historical and is not the reference for this task.

## Question, result and claim boundary

This increment reproduces the accepted endpoint's 213 reactive objective rows from a solvent specification, with retained subset cost 45.37796168239049. It preserves the same row-level falsifier and scientific declarations. Kiepe, Cai and CO2-free-density qualification are deferred. This demonstrates specification-driven reproduction of the accepted carbamate-amine reactive observations. It does not reproduce the complete 307-row manuscript objective, establish neutral binary continuation or free-temperature support, or qualify parameter fitting.

Deliver fixed-endpoint numerical reproduction, with no fit or new model/data selection. Preserve the accepted calibration and comparison roles, extrapolation labels, active-bound limits and conditional uncertainty. This supports no independent physical-validation, phase-stability or absorber-suitability claim. The deferred groups require no follow-up issue.

## Exact reference and numerical falsifier

All paths below are relative to the repository root. Let `E` denote `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/` and `C` denote `analyses/mea_parameter_bundle/results/engine-3e83e19c-refit-chain/`.

| Input/result | Exact owner | SHA-256 |
|---|---|---|
| Accepted Engine parameter document | `E/reported-parameters.json` | `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91` |
| Row-level numerical reference | `E/full-replay.json` | `aeb3331cf95cb174faa9cfa5891e887dbae0829448b5c67a2da17727ed386560` |
| Row identities, groups and declarations | `E/fitted-rows.csv` | `e18efef61548d20e40578a2223cb203dd903ed288c02b94ab24009d6b861fb44` |
| Group costs and coordinates | `E/fit-summary.json` | `7968c9ce1ca9947d70795787afedccf4f90786a77196e890412a13871f37d0fb` |
| Prior fresh replay comparison | `E/replay-identity.json` | `96069e3402f3d3d6a26f12f155d9bde730ff838c43f706a85fd0412166fa3f27` |
| Physical neutral calorics | `data/reference/MEA/thermal/physical-ideal-gas-calorics.json` | `c94d504e68c6dc6e85d3d950cc51422499846729b1a06994b362040be991924a` |

The endpoint is byte-identical to `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json` and `C/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json`. Use the immutable `E/reported-parameters.json` as the specification input; do not follow a mutable default. The joint fit's native final cost is **148.87893934555717**; the complete accepted serialized endpoint's fixed replay cost is **148.87893934557388**, dimensionless. Common-149 cost is **23.860996312136727**. The complete reference contains exactly **307** unique objective targets, all available and finite. These full-objective facts are reference context; only the 213-row subset below is qualified here.

Use the paper's immutable merged Engine commit `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, wheel `build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`, SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`. Verify installed bytes against it and record Python/numerical-library versions. The MDEA d5138209 wheel is a separate reference environment; do not silently substitute it or change `pyproject.toml`/`uv.lock`. The observation-specific wheel stop condition is defined under prediction reporting below; optional result-field absence alone does not require a wheel change.

**Falsifier:** evaluate from the specification, without importing the legacy fitting scripts at execution time. Join by original target ID and preserve the reference order. Require:

1. Exactly the same 213 selected IDs, observation values, residual forms, scales, weights and group membership; no exclusions or duplicated targets. The complete prepared problem declarations must also match the original declarations, including phase names/supports, feeds, starts, free/fixed variables, references and tolerances.
2. All 213 predictions `Available`, finite and meeting their requested numerical tolerance. Preserve unavailable causes and diagnostics if a row fails; a partial sum is not a cost.
3. For each prediction, residual, weighted residual and row cost, and the subset and admitted-group costs, require
   $$|a-b|/\max(|a|,|b|)\leq10^{-10}.$$
   No compared reference field is zero, so no separate zero clause is needed. The smallest absolute weighted residual in the full reference is about $8.78\times10^{-5}$; in the admitted subset it is about $8.45\times10^{-4}$. This is the existing #215 replay criterion, not an experimental-error limit. Its fresh replay retained zero differences in all these fields. Reusing it avoids weakening the accepted reference for a mapping change. The native-fit/serialized-replay cost difference is about $1.1\times10^{-13}$ relative and does not consume this allowance materially.
4. Retain the first differing target and every difference, not just a pass flag or total cost. Sum row costs with stable summation. The objective is $C=\frac12\sum_j w_jr_j^2$ and weighted residual is $\sqrt{w_j}r_j$; difference residuals use the retained scale and log-ratio residuals use the native log-ratio constructor.

## Data roles and domain: reuse, do not repartition

The executable declarations are owned by `C/restricted-2/attempt-3/spec.json`, `fit_observations.rows_for`, `stage2_rows`, `stage6_rows`, and `fit_campaign.stage6_weights`. Hash the spec and every consumed file during preparation, including its packet, anchors, source requests, heat rows, the admitted stage-2 row declarations, density scales and source membership. `E/fitted-rows.csv` owns the final row membership/group labels; its source declaration is evidence, not a substitute for the actual physical problem.

| Objective group (exact retained label) | Rows | Quantity/role and qualification scope |
|---|---:|---|
| `common149` | 47 | Fitted CO₂ partial pressures |
| `common149` | 94 | Fitted species mole fractions, retaining declared species sums |
| `common149` | 8 | Fitted Vinjarapu integral addition enthalpies |
| `restored species` | 7 | Fitted additional species mole fractions |
| `Jakobsen` | 6 | Fitted amount ratios; denominator includes MEA, MEAH⁺ **and carbamate** |
| `Kiepe` | 39 | Fitted CO₂–water bubble pressures; **deferred**, out of scope |
| `CO2-free density` | 5 | Fitted unloaded mass densities; **deferred**, out of scope |
| `Cai` | 25 + 25 | Fitted bubble temperatures and vapor water mole fractions at fixed pressure; **deferred**, out of scope |
| `loaded density` | 47 | Fitted mass densities; final weight 1/47, from `stage6_weights` |
| `Cp` | 4 | Fitted equilibrium isobaric heat capacity on total analytical-feed molar basis |

The complete table sums to 307. The admitted groups sum to **213**: common-149 (149), restored species (7), Jakobsen (6), loaded density (47) and Cp (4). Kiepe (39), Cai (50) and CO₂-free density (5) are deferred with no follow-up issue. Common-149 is nested, not a second added objective. Preserve all other weights and source scales exactly; do not import MDEA's group weighting or convert every group to 1/N. Preserve the source-derived density scales rather than recomputing uncertainties. Preserve Hilliard's 7 mol MEA/kg water preparation, including the retained $10^{-6}$ mol CO₂ feed for nominal zero loading; it is not an exact-zero-carbon density problem. Source seeded ionic feeds and diluted Jakobsen preparation must remain as declared, rather than being reconstructed from nominal 30 wt% and loading.

The retained subset cost check uses stable summation of the admitted groups:

| Admitted group | Retained cost |
|---|---:|
| `common149` | 23.860996312136727 |
| `restored species` | 2.4486746519412517 |
| `Jakobsen` | 13.122182452954206 |
| `loaded density` | 0.5654031419421082 |
| `Cp` | 5.380705123416196 |
| **213-row subset** | **45.37796168239049** |

`math.fsum` of these five costs is exactly 45.37796168239049, matching stable summation of the 213 retained row costs. Select these exact groups from `E/fitted-rows.csv`, preserving their relative order in `E/full-replay.json`; hash the full files and retain the selected IDs. Compare every selected declaration, row field and group/subset cost; do not compare the reduced sum to the complete-objective cost.

### Preparation dependency on `stage2_rows`

The existing `stage6_rows` calls `stage2_rows` for all 107 added rows. Of the admitted 213, exactly **13** come through that owner, from `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-6/inputs/joint-mea-water/joint-added-rows.json`, case `F1`:

- `Bottinger2008_state_042::MEA + MEAH+`, `Bottinger2008_state_042::MEACOO-`, `Bottinger2008_state_046::MEA + MEAH+`, `Bottinger2008_state_046::MEACOO-`;
- `Matin2012_state_016::MEA`, `Matin2012_state_016::MEAH+`, `Matin2012_state_016::MEACOO-`;
- for each of `Jakobsen2005_state_011` and `Jakobsen2005_state_022`, the three suffixes `::MEAH+`, `::MEACOO-` and `::HCO3- + CO3^2-`.

All 13 use the `request_id` branch. Preparation selects only these declarations before construction, reads their matching requests from `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-2/shared/stage4-requests.json`, and reuses `shared_evaluation.corrected_request` and `_problem_from_request` with the same temporary construction mapping as the existing owner: copy the accepted endpoint in memory and apply only `cases[0].neutral_domain` to its `neutral_domain_ids`. No parameter values change and no construction parameter document is retained or consumed at runtime. Materialize the resulting fixed-temperature problems, seeded feeds, source phase names, guesses, references and reaction declarations through existing templates/columns, and copy the native observation arguments, ratio denominators, scales and weights. Do not call the unfiltered `stage6_rows`/`stage2_rows` path, construct deferred observations, or add per-dataset parameter documents. The existing construction amendment also reaches the R2/R4/R5 correlations through their shared `candidate_domain_id`: these 13 problems carry the existing 293.15–436.85 K correlation bounds. Materialize those effective bounds exactly and record their origin; do not silently replace them with 393.15 K when comparing declarations. This is preservation of existing problem metadata, not new free-temperature handling or evidence of validity above 393.15 K. Evaluate every observation against the original endpoint model, as the retained replay does. Verify the materialized declarations against the filtered `request_id` branch before evaluation. Common-149 uses `rows_for`; the 47 loaded densities and 4 Cp use the 51 `direct_rows` declarations and final `stage6_weights`.

No admitted row needs a preceding row's newly solved state. Stored request continuation states and common-row anchors supply fixed initial guesses and must be preserved as input; they create no inter-row continuation dependency. Kiepe's parameter-dependent continuation is deferred.

The manuscript's other comparisons keep their roles: 14 Arcis heats are outside the objective but were used to accept fits; the wider pressure comparison was examined during model development; 19 Matin bicarbonate-total and 10 Jakobsen carbonate-share comparisons remain outside the fit. The 210-density assessment includes the 52 fitted densities, with overlap retained. Water, separate permittivity and earlier neutral fits remain separate stages. No old “holdout” label becomes untouched prediction evidence. Do not add these overlapping comparisons to the 213-row qualification. Export their existing roles/limits by reference if needed; rerunning the six assessment modes, curves or phase search is outside this increment.

Preserve each admitted group's actual domain and basis. The endpoint R2/R4/R5 candidate-law domain remains 293.15–393.15 K, with source-range extrapolation recorded. Preserve the 13 existing construction declarations described above without claiming broader temperature support. New neutral construction-domain support and Cai fixed-pressure/free-temperature handling are deferred with the neutral groups. Pressure observations use their retained Pa declarations; source transformations and heat signs/units remain unchanged.

## Chemistry and reference-state owners

Species IDs and ordering come from `shared_evaluation.COMPONENT_IDS` and the source packet: CO₂, MEA, water, MEAH⁺, carbamate, bicarbonate, carbonate, hydronium and hydroxide. Keep neutral CO₂/water/MEA vapor supports and liquid-only ions from each existing problem; do not copy MDEA supports.

`data/reference/MEA/manifests/chemical_reaction_source_contract.json` owns the reaction directions and selected source conventions; `src/MEA/common/mea_source_contracts.py` owns their checked source values. `shared_evaluation._engine_reaction_records`, `_reaction_reference` and `_neutral_reference_data` own their Engine mapping. Prepare their effective declarations once, with provenance, into MEA TOML. Do not rederive an EOS standard-state correction or add a second reaction calculator.

- **R4, carbamate hydrolysis:** $\mathrm{MEACOO^-+H_2O\rightleftharpoons MEA+HCO_3^-}$. Retain this direction. Its accepted law is $\ln K=2.151-1545.3/T$, already on `CommonMolalityInfiniteDilution`, standard-state ID `aqueous-molality-infinite-dilution-water-v1`, reference pressure 100000 Pa. Selected source: Tong (2012), §3 Eqs. (5)–(12), Table 5 p.44, via Aroua (1999); source interval 293.15–323.15 K. The accepted record extends it to 393.15 K as candidate extrapolation. Do not replace it with Austgen's VLE-fitted mole-fraction carbamate law or invert it without transforming K.
- **R5, protonated-amine dissociation:** $\mathrm{MEAH^++H_2O\rightleftharpoons MEA+H_3O^+}$. The unmodified source law is $-\log_{10}K=2677.91/T+0.3869+0.0004277T$ (Bates–Pinching 1951, p.349). The **accepted endpoint** instead contains $(a_K,b,c_{1/K})=(3354.099229276806,-1.2811063905656925,0.00042769999999999993)$. Use that endpoint, not the source coefficients. The mapped natural-log polynomial has $(a,b,c,d)=(2.9498564774559717,-7723.098885755592,0,-0.0009848156442735533)$, pivot 313.15 K, `CommonMolalityInfiniteDilution`, the same molality standard-state ID and 100000 Pa reference pressure. Source interval 273.15–323.15 K; accepted candidate interval 293.15–393.15 K. Protonation is the reverse reaction; no independent protonation law is introduced.
- Retain R1 water autoionization, R2 CO₂ dissociation to bicarbonate and R3 bicarbonate dissociation to carbonate, with their existing hydronium/water stoichiometry. R1/R3 use `RawMoleFractionInfiniteDilution`; R2 uses the accepted common-molality law. The source-to-common conversion remains Engine-owned. Preserve the null reference pressures for R1–R3 rather than substituting R4/R5's 100000 Pa.

The mapped polynomial convention is $a+b/T+c\ln(T/T_{ref})+dT$ for these laws. Preparation follows the existing pivot recentering exactly. The accepted endpoint already incorporates the R2/R5 enthalpy shifts; `C/restricted-2/attempt-3/run/fit/chemistry-coordinates.json` records totals −1363.931574116721 and 10000 J/mol. Do **not** apply those shifts again to endpoint laws.

The aqueous neutral reference is water, standard molality 1 mol/kg water, with solute-direction ratios: CO₂ 0.125, MEA 0.125, MEAH⁺ 0.625, carbamate 0.25, bicarbonate 0.125, carbonate 0.125, hydronium 0.125, hydroxide 0.125. These are the existing charge-balanced reference direction, not an experimental composition. Default species references are water `PureLiquid`, solutes `InfiniteDilution`; preserve any per-problem declaration. Check elements and charge using the #230 generic balance check. Declare formulas/analytical incidence for carbamate once in MEA TOML; retain one analytical amine and one carbon unit for carbamate.

### Caloric declaration

`verify_reference_calorics.record()` and the hash-bound physical calorics file above own the accepted neutral calorics. CO₂/water retain NIST Shomate records and formation enthalpies; water's low-temperature extrapolation stays explicit. MEA uses Zhang–Que–Chen (2011) Table 3 Cp coefficients, recentered from powers of T to powers of $(T-313.15)$ exactly as that owner does, with **h = s = 0 at 313.15 K**. This is the retained moiety gauge, not a measured zero formation enthalpy. Engine completes ionic thermochemistry from the reaction laws/reference convention. No independent ionic Cp/heat fit or second absorption-heat formula is added.

The current driver already accepts zero anchors but hardcodes them in `IdealPolynomial`. Replace that literal policy with declared `enthalpy_anchor_j_per_mol` and `entropy_anchor_j_per_mol_k`, including explicit zero fields in both MEA and MDEA prepared caloric records. Preparation performs polynomial recentering; the driver only passes coefficients, anchors, intervals and pressure to Engine. No inference of absent anchors. A minimal direct Engine comparison at the anchor and one off-anchor temperature checks that explicitly nonzero supplied anchors survive mapping; this is a caloric mapping invariant, not new MEA calibration.

## Driver gaps and minimum changes

`SolventSpecification` remains the application mapping owner; Engine remains the owner of thermodynamics, equilibrium, coordinate transforms, predictions and fitting. No driver branch tests a MEA species name, dataset label or filename. The implementation inventory below distinguishes missing mapping from declarations already supported.

| Exposed limitation | Minimum change and owner | Why/reuse and retirement |
|---|---|---|
| MDEA-shaped row vocabulary and state preparation | MEA preparation writes arbitrary numeric columns, one per needed feed/guess value; TOML templates bind each through existing recursive `bind`. Keep original target ID and source row separately from ordinal. No formula language or runtime composition converter. | Existing dataset `columns` is already arbitrary; the five-field `T,P,water,alpha,amine` restriction exists specifically in the driver's **phase-state** loop. This increment supplies an empty phase-state record because no new phase search is authorized. Do not add or claim generic phase-row support here. The objective must never be reconstructed through those five fields. |
| Sorting assumes `fit:<integer>` identities | Replace string parsing with an explicit numeric observation-order column mapped from prepared rows; migrate MDEA preparation/declarations to emit it. Keep original target IDs as identities. Driver owns ordering; preparation owns ordinals. | MEA IDs such as `vle_obs_0119-pco2` and `Jakobsen2005_state_011::MEAH+` are scientific identities. Removing positional interpretation prevents a silent reorder and avoids replacing source IDs with driver-shaped aliases. Preserve existing MDEA order exactly. |
| Row-specific initial guesses and seeded feeds | Add MEA templates and flat column declarations, including separate initial/final heat feeds and all nine seeded feed components where present; use existing `eq.problem_from_mapping`. | Driver's recursive binder and Engine free-variable mapping already support this. No new solver or MEA template code is justified. Preserve source phase names and raw row tolerance from each owner rather than copying `L,V` or one global default. |
| Polynomial anchors hardcoded to zero | Explicit anchors in caloric input; pass them into native `IdealPolynomial`; update MDEA preparation and hashes. | Replace the two literals, retain existing NIST Shomate handling, and preserve the existing zero-gauge cases. |

The small MEA runner reduces native residuals with the declared weights into row costs and a subset/group comparison report. Reuse the existing templates, arbitrary dataset columns and recursive binder. Declared Kiepe continuation, per-dataset construction/observation parameter documents and free-temperature handling are deferred with the neutral groups.

**Prediction reporting on the pinned wheels.** Require the native prediction fields `status`, `message`, `value`, `residual` and `requested_tolerance_met`. Transport `branch`, `stable_root_count` and the named convergence fields using the existing `fit_observations.replay` mapping. Serialize the convergence object explicitly; do not pass it to the generic iterable serializer. Treat `saturation_loading` and `endpoint_loading` as optional result fields: retain their native values where exposed and otherwise record null with their unavailability explained. They are not required by any MEA observation in this qualification. Require a capped-addition-enthalpy constructor only when a specification actually declares that observation. No species-name or wheel-version branch is introduced. Stop for a missing calculation or result required by an admitted observation. Absence of an optional saturation field on an ordinary MEA observation is not a failed calculation and is not grounds for a wheel upgrade. Preserve the existing MDEA capped-observation reporting and recheck R1/R3/R5 on its pinned wheel.

The named convergence fields are `residual`, `floor`, `amplification`, `contraction`, `iterations` and `stop`. The current driver's unconditional reads of `saturation_loading` and `endpoint_loading` must be replaced by this availability policy; those fields are absent on 3e83e19c.

Endpoint-only loading needs no new mode or optimizer code: the existing required `start` can reference the same hash-bound endpoint, `coordinates` can reference an empty list, and `phase_states` an empty list. Label these explicitly as endpoint-only inputs; they are not an inferred fit start, a qualified coordinate declaration, or a completed phase search. Do not call `fit()`.

During preparation, existing owners may be imported to obtain exact declarations and source transformations, including the Engine-native problem objects used by `stage6_rows`. Materialize their fields, not their predictions. The runtime reproduction must load the TOML/CSV/JSON packet alone plus the installed Engine and generic driver; it must not import `fit_observations`, `fit_campaign`, `shared_evaluation` or execute historical `.py.txt` producers. Check the materialized declarations field by field against these owners before numerical comparison. Preparation needs no new continuation solves for the selected rows; preserve stored guesses and materialize only their declarations.

**Owner/callers/retirement/evidence:** `src/MEA/solvent_specification.py` owns common declaration mapping. Its MEA and existing MDEA runners are callers. Remove numeric-suffix identity parsing and literal caloric anchors; update MDEA inputs/hashes that depend on them. The old MEA/MDEA fitting scripts remain historical evidence, with no monkey-patching or new numerical execution dependency. Retain MEA row reproduction and MDEA R1/R3/R5 endpoint checks. R2 fitting and R4 phase reruns are not newly required by changes outside their numerical owners; if shared phase or fitting behavior must change, return to Design.

## Implementation sequence and retained evidence

Only after independent Ready, owner publication/read-back and a fixed code ceiling:

1. Freeze Build's actual base SHA and inspect concurrent #232 changes. Bind the endpoint, full replay, source spec, wheel and all consumed files by SHA-256. Verify the two endpoint copies and selected bytes agree with the reference hash.
2. Implement only earned generic mappings above; materialize `analyses/solvent_specification_mea/MEA.toml`, chemistry/problem declarations and prepared inputs with a preparation-provenance record. Check reaction element/charge balance, caloric coverage and exact source row mapping. Preserve MDEA declarations through the generic changes.
3. Reproduce the 213-row reactive subset, using the pinned paper wheel at niceness 10. Retain `results/runtime.json`, complete row predictions/residuals, hash inventory and `results/endpoint-checks.json` with every row difference and group/subset reductions. Do not write into the accepted bundle evidence. No stale prediction cache is an execution result.
4. Run the existing MDEA endpoint falsifiers R1/R3/R5 in their d5138209 wheel environment after input migration; preserve their tolerances from #228. Run one focused numerical caloric-anchor check. Do not add parser/helper tests or launch a fit.
5. Present the numerical result in `analyses/solvent_specification_mea/notebook.qmd`, including cost, counts, limits and any typed failures. This is a numerical reproduction notebook, with no manuscript edits or new physical-validation claim. Independent delivered `cse:review` checks the final implementation and retained evidence; investigator acceptance is separate from a successful command.

The hand-off follows #230's existing species, mass, reaction-direction, reference-state, caloric and property-role semantics. Hash the exact **supplied** endpoint document; this task does not produce newly fitted parameters. No new serializer, local parameter JSON updater or dependency on Engine #928 is earned for endpoint-only evaluation. #232 owns fitted MDEA serialization. A future column export must state that calibration reproduction is not absorber qualification; column transport, kinetics and solve policy remain column-owned. No column issue update or external publication is included here.

## Runtime and executable-line estimate

Retained timing owner: `E/execution.json`, entry `stage = replay identity`: **9.133172251997166 s wall**, for construction and fresh 307-row evaluation. The six separate assessment modes in `E/assessments-timing.json` each took 9.30–13.43 s and are not required here. The read-only Design construction probe on 2026-10-30 constructed all 307 observations, including Kiepe's native continuation, in 2.23 s command wall; it ran no fit and did not evaluate the full objective.

For the reduced 213-row scope, estimate **5–20 s per MEA endpoint pass**, and **under one minute** for preparation, one endpoint pass and report checks on a comparable warm environment. Allow several minutes for the combined MEA/MDEA checks, excluding environment provisioning. This is an estimate from retained execution, not a promised benchmark; record actual timing and worker/thread configuration. The 213-row timing is a planning estimate inferred from the retained 307-row timing, not a measured subset benchmark. No parallel campaign is needed.

For comparison only, the retained restricted-2 fit timing at `C/restricted-2/attempt-3/run/fit/timing.json` records 40.5175 s for that resumed invocation and **16718.5175 s cumulative wall (4.64 h)**, **128524.9118 s cumulative CPU**, including earlier charged work. Do not describe 40 s as a fresh full refit estimate. A new fit plus information diagnostics would require a separately authorized hours-scale budget; it is unnecessary for this known-endpoint falsifier.

Proposed gross executable additions against inspected base `e5314f9`, including preparation, comparison scripts, comments, blanks and notebook code cells; tests are counted separately:

| File/responsibility | Estimated additions | Estimated removals |
|---|---:|---:|
| `src/MEA/solvent_specification.py`: order, explicit anchors, native reporting and optional-field handling | 40–55 | 8–15 |
| `analyses/solvent_specification_mea/prepare.py`: existing-owner materialization, hashes and declaration equality | 75–100 | 0 |
| `analyses/solvent_specification_mea/run.py`: endpoint execution, row/group reference reduction and timing | 45–55 | 0 |
| Existing MDEA preparation/runner adjustments for order and anchor fields | 10–20 | 2–5 |
| **Executable total** | **170–230** | **10–20** |

Separately estimate 15–30 test lines for one numerical anchor invariant; TOML, prepared CSV/JSON, numerical results and notebook prose are reported separately. If code is embedded in a notebook, count it as executable. The owner-approved ceiling (2026-10-30) is **230 gross added executable lines plus 30 test lines**. All preparation/comparison scripts, comments, blanks and notebook code cells count against the 230; deletions buy nothing. TOML, prepared data, numerical results and notebook prose are separate from executable additions. The estimate reserves no notebook code beyond the runner; any such cells share the same ceiling. Build uses `scripts/workflow/change_accounting.py` against its frozen base and stops before an overrun. No new dependency, fitting mechanism, covariance calculation or local thermodynamic equation is included.

## Stop conditions and open gates

- No Build until renewed independent readiness **Ready** and owner publication/read-back. The owner has settled the reduced scope and the 230 + 30 ceiling; this draft is not a published plan.
- Stop on an endpoint/source/wheel hash mismatch, unknown source role, unreadable required owner, or changed accepted endpoint. Do not repair the reference by editing retained evidence.
- Verify hashes, row membership and materialized declarations before numerical evaluation. On a numerical mismatch, retain the first differing target and all differences available from that pass. Independent rows may finish for diagnosis. Do not accept a partial cost, launch a fit, alter controls or relax the comparison tolerance. Correct mapping defects within the approved scope and repeat the affected comparison. Return to Design for a missing native calculation, changed scientific declaration, wheel change or budget overrun.
- No reactive row has an inter-row continuation dependency, so the dependent-continuation stop clause is omitted. Stored initial guesses remain part of the declarations.
- Apply the observation-specific wheel condition under prediction reporting: require admitted calculations/results and preserve optional-field unavailability. No Engine edit, local equation substitute or silent d5138209 migration.
- Return to Design if runtime independence requires a second chemistry owner, or scope expands to neutral qualification, generic phase qualification, coordinate/fitting qualification, a campaign or a new export lifecycle.
- Preserve typed failures and every admitted row. A missing prediction, refused solve or timeout cannot be converted into successful reproduction.

The scope and code ceiling are settled owner decisions. Remaining gates are renewed independent readiness and publication/read-back by the owner. No unresolved reaction-source choice, data repartition or new physical acceptance threshold is delegated to Build. A refit or a newer wheel requires an explicit scope amendment with its own numerical comparison and budget.

## Design evidence and reading limits

This Design read #233, #228 and #230 bodies and the relevant #228 hand-off constraints; inspected the driver, MDEA B1/declarations/preparation/runner, MEA bundle overview and joint-recalibration record, manuscript generator and `a7_presentation`, source-reaction requirements, effective reaction mapping, caloric owner, row constructors and retained replay/timing files. Read-only probes counted the exact rows and loaded the retained endpoint; no fitting command ran.

The ignored reading shelf is absent in this worktree but was read at the main checkout's `literature/` path without writing there. Böttinger (2008) §§2–6 and relevant results were read, including fitted versus compared constants and molality reference conventions; its current Zotero Markdown hash matches index SHA-256 `b9643df4c5606e79136dff0ddff9db5adbcd4481a2ebb2f06dc15b19cb3f074d`. Tong (2012) printed pp.42–44 (model equations/Table 5) and Aroua (1999) pp.887–890 (methods, theory and results) were inspected from Zotero PDFs. Tong PDF hash matches the source audit, `78af3d67d58ff610dcc7c34fd55a75763470b7cd5bac0f3e39c256c7d7ffd61c`. These readings confirm the need to preserve direction and source basis; they do not change the adopted chemistry. Exact polynomial values above come from the retained endpoint and its existing mapping, not a fresh paper transcription.

Bates–Pinching was not independently reread here; its source formula and locator are inherited from the checked source-reaction requirements and `docs/ePC-SAFT/mea-reaction-and-sentinel-primary-source-audit.md`. This task reproduces that adopted choice and does not adjudicate the underlying source conversion. No new literature-based fitting recommendation or validation claim is made. The task checkout has no `BANNED.md`; the stop-hook vocabulary at `/home/tnnrpolley21/.local/share/cse/hooks/cse-BANNED.md` was subsequently read and its reported wording corrected.

Revision evidence (2026-10-30): read the live #233 body/comments and the current row constructors, prediction mapping and retained declarations. A read-only reduction of `E/full-replay.json` selected the 213 rows using `E/fitted-rows.csv` and reproduced all five group costs and their subset sum without running Engine. The 13 request-backed stage-2 declarations and 51 direct rows account for every admitted row outside common-149. The literature readings above are inherited from the original Design; this revision changes no source law or scientific declaration and makes no new literature judgment. No Build or independent renewed readiness review was performed in this revision.
