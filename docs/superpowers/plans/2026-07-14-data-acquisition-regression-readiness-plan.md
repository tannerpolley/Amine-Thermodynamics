# MEA Data Acquisition and Regression Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a provenance-complete MEA evidence system that recovers local observations, directs external acquisition by parameter identifiability, freezes leak-free target roles, and supplies regression-ready inputs without overstating current ePC-SAFT capability.

**Architecture:** Preserve reported source values in family-owned canonical observation registries, derive active regression views only through explicit row-disposition and target-admission manifests, and freeze grouped train/validation assignments before production fitting. Local recovery is completed before external acquisition; unsupported ePC-SAFT target families remain validation-ready rather than invoking private APIs or downstream optimizers.

**Tech Stack:** Python 3.13, pandas/NumPy, CSV/JSON, `uv`, `unittest`/pytest-compatible tests, repository validation scripts, public pinned ePC-SAFT integration contracts.

## Global Constraints

- Keep reported values, normalized values, uncertainty, basis, source locators, lifecycle status, and measurement role independently traceable.
- Treat missing, reported zero, below-detection, aggregate, inferred, model-derived, analog, and ambiguous values as distinct states.
- Account for every raw row with an explicit canonical, reserved, diagnostic-only, QA-pending, or excluded disposition.
- Preserve the current 161-row pressure and 74-state speciation target views until the new target-admission and split manifests pass their cutover gate.
- Do not convert Wong mol/kg values to regression-eligible mole fractions until the source denominator is verified.
- Keep viscosity validation-only unless a separately approved transport model defines its residual contract.
- Use stable ePC-SAFT mode by default; use one explicit dev worktree only for intentional upstream contract work; require final mode for manuscript-result consumption.
- No private upstream API, downstream substitute optimizer, silent fallback, fabricated uncertainty, or unsupported scientific claim.
- Use test-first changes for Python behavior; use deterministic row-count, source-locator, and source-table comparison proof for data-only extraction.
- Run the repository cleanup audit after every task that writes files or launches a process.

## Source Evidence

- Approved design: `docs/superpowers/specs/2026-07-14-data-acquisition-regression-readiness-design.md`.
- Source lifecycle: `data/reference/MEA/manifests/source_status_manifest.csv`.
- Extraction targets: `data/reference/MEA/manifests/extraction_target_manifest.csv`.
- Existing VLE sources: `data/reference/MEA/observations/vapor_liquid_equilibrium/`.
- Existing speciation sources: `data/reference/MEA/observations/liquid_speciation/`.
- Loaded-property source: `docs/papers/md/Amundsen et al. - 2009 - Density and viscosity of monoethanolamine + water + carbon dioxide from (25 to 80) °C.md`.
- Wong source: `docs/papers/md/Wong et al. - 2015 - Chemical speciation of CO2 absorption in aqueous monoethanolamine investigated by in situ Raman spec.md`.
- Sensitivity evidence: `analyses/phase3/ionic_epcsaft_regression/results/sensitivity/parameter_identifiability.csv`.
- Current zero-evaluation state: `analyses/phase3/ionic_epcsaft_regression/results/global_regression/global_regression_summary.json`.
- Upstream boundary: `docs/coordination/epcsaft_feedback_reactive_regression_admission.md` and Issue 12.

## Outcome Proof

**Intent:** Make future MEA parameter regression depend on orthogonal, source-traceable evidence rather than additional 30 wt% pressure rows or balance-inferred species alone.
**Current Behavior:** Raw observations, active target views, long canonical tables, analysis metadata, and runtime loaders have different scopes; 166 local VLE rows, 37 non-30-wt% NMR states, 143 loaded property values, and Wong Table 5 are not in active regression-facing data, while dielectric, pH, and direct ionic-activity families are absent.
**Expected Outcome:** Every local row has a verified disposition; all normalized values retain source values and uncertainty; high-value local tables are extracted; external searches are reproducible; target roles and grouped splits are frozen; unsupported target families fail closed.
**Target Output:** Observation contract, full VLE/speciation/physical-property registries, row-disposition manifests, search log, parameter-observable coverage matrix, target-admission registry, grouped split manifest, readiness summary, and integration receipts.
**Owner:** Data-provenance maintainer, with family review by physical-properties, spectroscopy, regression, validation, and cross-repo integration maintainers.
**Interface:** `build_regression_readiness(reference_root, capability_receipt) -> RegressionReadinessBundle` plus deterministic canonical builders and CSV manifests.
**Cutover:** Issue 13 consumes only rows marked target-eligible by the frozen admission/split manifests; Issue 14 consumes only the frozen reserved groups and complete failure policy.
**Replaced Path:** Replace implicit omission, hard-coded 30 wt% selection, metadata/runtime path drift, and source-less weighting with explicit observation, disposition, admission, and split contracts.
**Evidence:** Row-count reconciliation, byte-deterministic rebuilds, source-table comparisons, uncertainty-preservation tests, leakage tests, capability receipts, and cleanup receipts.
**Acceptance Proof:** All local sources reconcile; known uncertainty survives; Wong ineligible conversions fail; grouped split is frozen before fit; every admitted family has public capability proof; quick validation passes; final consumers pass immutable ePC-SAFT integration checks.
**Stop Criteria:** Stop on unresolved units/basis/phase, unaccounted rows, discarded uncertainty, source-access ambiguity, split leakage, unsupported target admission, mutable final dependency, or scientific acceptance failure.
**Avoid:** No all-at-once fit, no row-count-driven search campaign, no analog-as-direct promotion, no post-fit holdout selection, and no manuscript status upgrade from data curation alone.
**Risk:** The recovered evidence may prove that the planned parameter window is not identifiable; the correct output is then a smaller fit window or a bounded scientific rejection, not forced parameter movement.

## Implementation Boundaries

**Files To Create:** Observation-contract manifest; VLE/speciation disposition manifests; full VLE observation registry; source-search log; parameter-observable coverage manifest; target-admission manifest; grouped split manifest; readiness builder, tests, and summary receipt.
**Files To Modify:** Canonical VLE/speciation builders and tests; Amundsen property table and tests; source/extraction manifests; analysis YAML paths; Phase 3 readiness and milestone documentation.
**Files To Avoid:** Curated parameter tables, reaction constants, manuscript claims, rendered figures, upstream ePC-SAFT kernels, and GitHub state until separately routed.
**Source Of Truth:** Primary source values plus repository-owned canonical builders, row-disposition manifests, and immutable target/split receipts.
**Read Path:** Raw/reference source -> reported observation -> normalized observation -> lifecycle disposition -> target admission -> grouped split -> downstream fit/validation.
**Write Path:** Family data under `data/reference/MEA/`; readiness artifacts under `analyses/phase3/ionic_epcsaft_regression/results/readiness/`; workflow documentation under `docs/superpowers/`.
**Integration Points:** `src/MEA/common/data_access.py`, `src/MEA/epcsaft_ionic/model.py`, analysis YAML files, Issues 12--14, and `scripts/check_epcsaft_integration.py`.
**Migration Or Cutover:** Build full registries alongside the current active views, prove deterministic eligibility and grouped splits, then change consumers in one explicit cutover task.
**Replaced Path Handling:** After cutover, remove obsolete hard-coded selectors and nonexistent analysis-manifest paths; retain old result bundles only when labeled historical/diagnostic.
**Acceptance Proof Gate:** All three plan validators, focused family tests, `uv run python scripts/validate_project.py quick`, cleanup audit, and immutable integration proof for final-result consumers.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Plan shape | Approved design and shared schema dependencies | Use one staged plan with independently reviewable vertical tasks. | Keeps contract, local recovery, acquisition, and admission ordered without one monolithic implementation change. | No | project workflow maintainer |
| Active-view stability | Current manuscript and regression artifacts | Keep existing 161/74 active views until explicit cutover proof. | Prevents data discovery from silently changing scientific outputs. | No | regression maintainer |
| VLE registry | Raw-source inventory | Register all 327 source rows and preserve auxiliary vapor observables. | Enables composition transfer and row accounting without automatic training admission. | No | VLE data maintainer |
| Speciation eligibility | Direct/inferred-role audit | Reserve non-30-wt% states and exclude unverified Wong conversions. | Creates transferability evidence and avoids basis contamination. | No | spectroscopy-data maintainer |
| Property role | ePC-SAFT model boundary | Use loaded density as candidate property/regularization evidence and viscosity as validation-only. | Separates equilibrium and transport evidence. | No | physical-properties maintainer |
| Search order | Sensitivity and missing-family audit | Search neutral mixing/physical solubility, dielectric, acid-base/ionic, then independent speciation/energetics. | Targets confounded parameters before adding more pressure-only rows. | No | data-curation maintainer |
| Holdout groups | Approved design | Freeze exact source/concentration groups after recovery and before Issue 13. | Uses recovered coverage without post-fit selection. | Yes | model-validation maintainer |
| Upstream admission | Issue 12 and upstream issue 468 | Admit only public capability-reported target kinds. | Keeps downstream data readiness useful without inventing package behavior. | No | cross-repo integration maintainer |
| Issue slicing | User technical-category preference | Route implementation as multiple milestone-native issues after plan approval. | Makes data, spectroscopy, property, acquisition, and regression ownership visible. | Yes | project workflow maintainer |

## Test Complete and Metrics

- Exactly 327 raw VLE rows receive dispositions; the 161-row active view remains byte-stable until cutover.
- The 111 tabular speciation states and 71 Wong long-form points have source/basis eligibility records; 37 non-30-wt% states are identifiable as transferability candidates.
- The Amundsen machine-readable table contains 213 observations: 70 unloaded plus 68 loaded-density and 75 loaded-viscosity values.
- Known Idris and Amundsen uncertainty is present in canonical outputs and covered by tests.
- Every raw-to-canonical omission has a reason; every replicate/normalization family has a stable group identifier.
- Search-log entries exist for each approved P1/P2 source lead, with access and extraction decisions.
- Every movable parameter family has at least one coverage row naming direct evidence, indirect evidence, current hole, and promotion restriction.
- Grouped split tests report zero source-curve, replicate-group, and normalized-condition leakage.
- Unsupported target families produce a failed admission receipt rather than a fallback objective.
- Repeated canonical/readiness generation is byte-deterministic.

### Task 1: Establish the observation contract and repair live-path lineage

**Use Cases:**

- A data curator can distinguish reported, normalized, inferred, aggregate, zero, analog, and ambiguous evidence without reading builder internals.
- Analysis metadata and runtime loaders resolve the same live canonical artifacts.
- A reviewer can see acceptance evidence for every raw row and known uncertainty before target selection.

**Files:**

- Create: `data/reference/MEA/manifests/observation_contract.csv`
- Create: `src/MEA/common/reference_observations.py`
- Create: `tests/test_reference_observation_contract.py`
- Modify: `analyses/phase1/six_species_baseline/analysis.yaml`
- Modify: `analyses/phase2/activity_epcsaft/analysis.yaml`
- Modify: `analyses/phase3/ionic_epcsaft_regression/analysis.yaml`

**Interfaces:**

- Consumes: dictionaries loaded from family CSV tables.
- Produces: `validate_observation_records(rows, family) -> ObservationValidationReport` with `ok`, `row_count`, `errors`, and `warnings`.
- Defines: `MEASUREMENT_ROLES`, `LIFECYCLE_STATUSES`, and required provenance/uncertainty fields.

**Verification Method:** Test-first schema behavior followed by live-path resolution and full quick validation.

**Acceptance Evidence:** Tests reject missing source identity, invalid roles, uncertainty without type, and normalized values without retained reported values; all analysis YAML paths exist.

- [ ] **Step 1: RED — write observation-contract tests.** Add tests equivalent to:

  ```python
  def test_normalized_value_requires_reported_value_and_basis():
      row = valid_row(value_normalized=0.1, value_reported="", reported_basis="")
      report = validate_observation_records([row], "speciation")
      assert not report.ok
      assert "normalized value requires reported value and basis" in report.errors

  def test_reported_zero_is_not_missing():
      row = valid_row(value_reported=0.0, measurement_role="direct_zero")
      assert validate_observation_records([row], "speciation").ok
  ```

- [ ] **Step 2: Verify RED.** Run `uv run python -m unittest tests.test_reference_observation_contract -v`; expect failures because the module and contract do not exist.
- [ ] **Step 3: GREEN — implement the narrow validator and contract table.** Define only the fields and enum values required by the approved spec; return all row-indexed validation errors without mutating input records.
- [ ] **Step 4: Repair analysis paths.** Replace nonexistent `Canonical_Combined_VLE.csv` and `reaction_equilibrium_catalog.csv` declarations with the live source-of-truth paths selected by the contract; make declared canonical speciation scope match the runtime consumer or explicitly declare both registry and active view.
- [ ] **Step 5: Verify GREEN.** Run the focused test, `uv run python scripts/validate_project.py quick`, and `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .`; expect all tests and path checks to pass with no task-owned cleanup candidates.
- [ ] **Step 6: Checkpoint commit.** Commit as `feat: define MEA observation contract`.

### Task 2: Build the complete VLE observation and disposition registries

**Use Cases:**

- All 327 raw VLE rows are visible even when they are not active regression targets.
- Non-30-wt% rows can be reserved for transferability without changing the current manuscript result set.
- Component and total vapor pressures survive canonicalization for later neutral-interaction targets.

**Files:**

- Create: `data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv`
- Create: `data/reference/MEA/manifests/vle_row_disposition.csv`
- Modify: `scripts/build_canonical_vle_dataset.py`
- Modify: `tests/test_canonical_vle_dataset.py`
- Modify: `data/reference/MEA/manifests/source_status_manifest.csv`

**Interfaces:**

- Consumes: the six raw source CSVs plus `Combined_VLE_inclusion.csv`.
- Produces: one 327-row observation registry and one 327-row disposition manifest keyed by `source_key`, `source_file`, and `source_row`.
- Preserves: CO2 partial pressure, total pressure, H2O partial pressure, MEA partial/Raoult pressure, uncertainty, replicate group, nominal-temperature group, and active-view membership.

**Verification Method:** Test-first row accounting, byte-deterministic generation, and source-table spot checks.

**Acceptance Evidence:** Registry and disposition keys are unique and complete; active `Combined_VLE.csv` remains 161 rows and byte-identical before cutover; all 166 currently unselected rows have reasons/status.

- [ ] **Step 1: RED — add full-registry tests.** Assert 327 unique source-row keys, 161 current-active rows, 166 non-active dispositions, 70 Aronu non-active rows, 25 Hilliard non-active rows, 26 Jou non-active rows, and 45 Xu non-active rows.
- [ ] **Step 2: RED — add auxiliary-observable tests.** Assert Hilliard registry rows retain MEA/H2O/total pressure, Jou retains total and MEA Raoult pressure, Xu retains total pressure, and the one Idris uncertainty-bearing row remains populated.
- [ ] **Step 3: Verify RED.** Run `uv run python -m unittest tests.test_canonical_vle_dataset -v`; expect missing-registry/disposition failures.
- [ ] **Step 4: GREEN — extend the builder.** Generate the full registry and disposition manifest without changing the active view. Assign Aronu 15/45 wt% and Hilliard 17/40 wt% rows `validation_reserved_candidate`; assign excluded temperature regimes `qa_pending_domain_review`; preserve existing active rows as `active_v1`.
- [ ] **Step 5: Verify source fidelity.** Compare deterministic samples from each concentration/temperature block to the raw CSVs and confirm repeated generation has no diff.
- [ ] **Step 6: Run focused and quick validation plus cleanup.** Expect PASS, 327/327 disposition accounting, and no task-owned artifacts.
- [ ] **Step 7: Checkpoint commit.** Commit as `feat: register complete MEA VLE evidence`.

### Task 3: Reconcile speciation eligibility and resolve the Wong basis boundary

**Use Cases:**

- Direct species observations are never replaced by balance-inferred values in the target registry.
- The 15/20 wt% NMR states are available as grouped transferability evidence.
- Wong source-basis concentrations remain usable for review without an unverified mole-fraction conversion.

**Files:**

- Create: `data/reference/MEA/manifests/speciation_target_membership.csv`
- Modify: `scripts/build_canonical_cheq_dataset.py`
- Modify: `data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv`
- Modify: `data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq_schema.csv`
- Modify: `tests/test_canonical_cheq_dataset.py`
- Modify: `data/reference/MEA/manifests/source_status_manifest.csv`

**Interfaces:**

- Consumes: Böttinger, Jakobsen, Matin, and Wong source records.
- Produces: long-form records with reported basis, conversion eligibility, measurement role, lifecycle status, and target/holdout membership.
- Enforces: `conversion_eligible=false` and blank `value_mole_fraction` for Wong until an explicit verified denominator record exists.

**Verification Method:** Test-first source-basis and target-role behavior, source-coordinate reconciliation, and deterministic rebuild.

**Acceptance Evidence:** All 571 current long-form records remain source-traceable; 29 Böttinger 20 wt% and eight Jakobsen 15 wt% states are reserved candidates; Wong has 66 extracted and five ambiguous rows with ineligible converted mole fractions until verified.

- [ ] **Step 1: RED — add Wong fail-closed tests.** Assert that an unverified denominator yields retained `value_mol_per_kg_source_basis`, blank `value_mole_fraction`, and `conversion_eligible=false`.
- [ ] **Step 2: RED — add membership tests.** Assert the 37 non-30-wt% NMR states are grouped as transferability candidates and active-v1 membership still contains 74 30 wt% states.
- [ ] **Step 3: Verify RED.** Run `uv run python -m unittest tests.test_canonical_cheq_dataset -v`; expect failures against the current unconditional Wong conversion.
- [ ] **Step 4: GREEN — make conversion conditional.** Remove the assumption that all Wong values are mol/kg loaded liquid; preserve feed/conversion context only as diagnostic metadata until the denominator record is verified.
- [ ] **Step 5: Generate membership from direct roles.** Keep direct-positive, direct-zero, aggregate-direct, balance-inferred, and ambiguous roles distinct; do not promote the 358 balance-inferred species-state values as independent measurements.
- [ ] **Step 6: Verify deterministic generation, focused tests, quick validation, and cleanup.** Expect PASS and no change to active-v1 target counts.
- [ ] **Step 7: Checkpoint commit.** Commit as `fix: gate MEA speciation evidence by basis`.

### Task 4: Extract loaded physical-property and Wong high-pressure tables

**Use Cases:**

- Loaded density can regularize or validate liquid-state behavior across MEA concentration, loading, and temperature.
- Viscosity remains available for transport validation without being mislabeled as equilibrium evidence.
- Wong high-pressure loading data are available with method/equilibrium caveats.

**Files:**

- Modify: `data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv`
- Create: `data/reference/MEA/observations/vapor_liquid_equilibrium/Wong_2015_high_pressure_loading.csv`
- Create: `tests/test_loaded_property_extractions.py`
- Modify: `data/reference/MEA/manifests/extraction_target_manifest.csv`
- Modify: `data/reference/MEA/manifests/source_status_manifest.csv`

**Interfaces:**

- Consumes: Amundsen Tables 2--4 and 6--8; Wong Table 5.
- Produces: 213 Amundsen property rows and 41 Wong loading rows with table locators, units, uncertainty/caveat fields, and lifecycle status.
- Classifies: density `property_target_candidate`; viscosity `validation_only`; Wong repeated 1-bar batch rows `non_capacity_batch_observation`.

**Verification Method:** Independent table transcription checks, exact cell-count tests, boundary-value spot checks, and source-locator review.

**Acceptance Evidence:** Counts are 68 loaded density, 75 loaded viscosity, 70 unloaded existing, and 41 Wong loading rows; blank source cells remain blank; uncertainty is retained.

- [ ] **Step 1: Add failing count and boundary tests.** Assert the expected family counts and representative first/last cells from each source table; expect failures because loaded rows/files are absent.
- [ ] **Step 2: Extract Amundsen tables.** Transcribe measured values only, including temperature, unloaded-basis MEA mass fraction, loading, property, unit, source table, and stated uncertainty fields.
- [ ] **Step 3: Extract Wong Table 5.** Preserve pressure-drop-calculated and Raman-speciation-predicted loading as distinct observed quantities, MSE, method, temperature, pressure, and the 1-bar non-capacity caveat.
- [ ] **Step 4: Verify against source tables.** A reviewer checks every table cell or a deterministic independent parser comparison; discrepancies block promotion.
- [ ] **Step 5: Run `uv run python -m unittest tests.test_loaded_property_extractions -v`, quick validation, and cleanup.** Expect PASS and exact counts.
- [ ] **Step 6: Checkpoint commit.** Commit as `data: extract loaded MEA property evidence`.

### Task 5: Create the reproducible external acquisition register

**Use Cases:**

- A future searcher knows exactly which source, observable, metadata, and parameter gap a search is intended to resolve.
- Abstracts, snippets, inaccessible PDFs, and analog evidence cannot silently become numeric rows.
- Failed access attempts and negative searches remain useful and do not repeat indefinitely.

**Files:**

- Create: `data/reference/MEA/manifests/source_search_log.csv`
- Create: `data/reference/MEA/manifests/parameter_observable_coverage.csv`
- Modify: `data/reference/MEA/manifests/extraction_target_manifest.csv`
- Modify: `data/reference/MEA/manifests/source_status_manifest.csv`
- Test: `tests/test_reference_source_manifests.py`

**Interfaces:**

- Search-log fields: `search_id`, `parameter_family`, `observable`, `query_or_source`, `database_or_repository`, `searched_at`, `access_status`, `primary_source_status`, `si_status`, `extraction_decision`, `target_path`, `notes`.
- Coverage fields: `parameter_family`, `direct_evidence`, `indirect_evidence`, `current_hole`, `priority`, `promotion_restriction`, `owner`.
- Produces source-ready targets for Cai/Park/Kim VLE, Posey/Touhara enthalpy, Jiru/Hartono physical solubility, Hajj/dielectric leads, loaded-MEA pH, ionic activity, Fan/Du Preez speciation, Kim calorimetry, and Idris concentration completion.

**Verification Method:** Manifest schema tests, unique source/target keys, primary-source locator checks, and evidence-label review.

**Acceptance Evidence:** Every approved source lead has a search record and decision; every movable parameter family has direct/indirect/hole coverage; no numeric extraction is admitted from an abstract or snippet.

- [ ] **Step 1: RED — add manifest contract tests.** Require every `source_pending`/`external_source_pending` row to have a search-log entry, target path, parameter family, and explicit access/extraction status.
- [ ] **Step 2: Verify RED.** Run the focused test; expect missing-log and missing-coverage failures.
- [ ] **Step 3: GREEN — populate prioritized search packages.** Record the locally identified sources and exact metadata requirements before browsing or requesting full text.
- [ ] **Step 4: Execute authorized searches source by source.** Prefer primary papers/SI and lawful local/Zotero access; record inaccessible and negative outcomes without creating fabricated rows.
- [ ] **Step 5: Verify manifests and extracted-source gates.** Run focused tests, confirm target files exist only when primary evidence supports them, then run cleanup.
- [ ] **Step 6: Checkpoint commit.** Commit as `docs: register MEA regression evidence searches`.

### Task 6: Freeze target admission, parameter coverage, and grouped validation splits

**Use Cases:**

- Issue 13 receives only public-capability-supported target families with frozen roles and weights.
- Issue 14 receives leak-free reserved groups and a complete failed-row policy.
- Unsupported density, dielectric, pH, ionic-activity, or calorimetric targets remain useful without triggering a private fallback.

**Files:**

- Create: `data/reference/MEA/manifests/target_admission_manifest.csv`
- Create: `data/reference/MEA/manifests/grouped_split_manifest.csv`
- Create: `scripts/build_regression_readiness.py`
- Create: `tests/test_regression_readiness.py`
- Create: `analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json`

**Interfaces:**

- Implements: `build_regression_readiness(reference_root, capability_receipt) -> RegressionReadinessBundle`.
- Bundle fields: source hashes, row counts, role counts, uncertainty coverage, parameter coverage, target admission, split hash, leakage findings, unsupported families, and readiness decision.
- Consumes public capability-report evidence only; unsupported kinds receive `admitted=false` plus reason.

**Verification Method:** Test-first admission failures, deterministic split fixtures, hash-drift checks, and no-private-import checks.

**Acceptance Evidence:** Split has zero leakage; every target family has admission evidence; unsupported families fail closed; repeated output is byte-identical.

- [ ] **Step 1: RED — add unsupported-family and leakage tests.** Include fixtures where density lacks package admission, adjacent source-curve rows cross the split, replicate groups split, and source hashes drift; expect explicit failures.
- [ ] **Step 2: Verify RED.** Run `uv run python -m unittest tests.test_regression_readiness -v`; expect failures because the readiness builder does not exist.
- [ ] **Step 3: GREEN — implement manifest-driven readiness.** Load only canonical registries/manifests, never analysis plot snapshots; validate roles and source hashes before computing readiness.
- [ ] **Step 4: Freeze grouped assignments.** Initially reserve the 15/20 wt% NMR groups and at least one non-30-wt% VLE source/concentration group; keep replicate and normalized-temperature groups indivisible.
- [ ] **Step 5: Verify capability boundaries.** Run the public integration check appropriate to stable/dev context and confirm no private `epcsaft._*` import or downstream optimizer appears.
- [ ] **Step 6: Run focused tests twice, compare output hashes, run quick validation, and cleanup.** Expect PASS and identical summaries.
- [ ] **Step 7: Checkpoint commit.** Commit as `feat: freeze MEA regression readiness`.

### Task 7: Cut over approved consumers and publish the readiness receipt

**Use Cases:**

- Existing Phase 3 work can consume the new readiness contract without changing parameter or manuscript status.
- Project milestones show data curation under Paper Validation and fit/validation consumption under Phase 3.
- Reviewers can see which evidence is ready, reserved, unsupported, or blocked.
- The consumer cutover retires undocumented hard-coded selectors after manifest-derived views prove identity equivalence.

**Files:**

- Modify: `src/MEA/common/data_access.py`
- Modify: `src/MEA/epcsaft_ionic/model.py`
- Modify: `analyses/phase2/activity_epcsaft/analysis.yaml`
- Modify: `analyses/phase3/ionic_epcsaft_regression/analysis.yaml`
- Modify: `docs/superpowers/milestones/paper-validation.md`
- Modify: `docs/superpowers/milestones/phase-3-ionic-regression.md`
- Modify: `docs/superpowers/issues/13-coupled-regression-parameter-promotion.md`
- Modify: `docs/superpowers/issues/14-independent-validation-identifiability.md`
- Test: `tests/test_analysis_workflow_architecture.py`
- Test: `tests/test_epcsaft_ionic_native_regression.py`

**Interfaces:**

- Consumers load explicit active-training and reserved-validation views derived from the frozen manifests.
- Issue 13 receives target/split hashes but does not execute until Issue 12 admission passes.
- Issue 14 receives the same split hash and complete failure policy.

**Verification Method:** Consumer contract tests, target-count/identity reconciliation, manuscript-claim guards, quick validation, cleanup, and final integration proof when results become manuscript-facing.

**Acceptance Evidence:** No hard-coded 30 wt% selector remains as an undocumented policy; active and reserved views match manifests; current provisional parameter/result language remains unchanged; existing issues name the new readiness prerequisites.

- [ ] **Step 1: RED — add consumer contract tests.** Require runtime target identities to match the admitted active view, reserved identities to match the split manifest, and source hashes to match the readiness receipt.
- [ ] **Step 2: Verify RED.** Run the focused architecture/native-regression tests; expect failures against hard-coded selection and current metadata paths.
- [ ] **Step 3: GREEN — cut over consumers.** Replace hard-coded row selection with manifest-driven views while retaining current active-v1 membership until a separately approved Issue 13 preregistration changes it.
- [ ] **Step 4: Align milestone and issue mirrors.** Link Paper Validation to acquisition artifacts and Phase 3 Issues 13/14 to readiness/split receipts; do not create or mutate GitHub issues in this task unless separately authorized through `create-issues`.
- [ ] **Step 5: Verify scientific status.** Run manuscript-claim integrity tests and confirm the global summary still reports zero-evaluation provisional status until an admitted fit exists.
- [ ] **Step 6: Run `uv run python scripts/validate_project.py quick` and cleanup.** For manuscript-result cutover, also run `uv run python scripts/check_epcsaft_integration.py --mode final`; expect PASS from immutable package inputs.
- [ ] **Step 7: Checkpoint commit.** Commit as `docs: publish MEA regression readiness receipt`.
