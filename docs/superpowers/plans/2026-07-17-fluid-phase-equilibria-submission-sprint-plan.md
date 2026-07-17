# Fluid Phase Equilibria Submission Sprint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and submit a scientifically complete coupled-regression MEA thermodynamics manuscript to *Fluid Phase Equilibria* on Friday, July 24, 2026.

**Architecture:** Seven fail-closed gates move one immutable evidence chain from preregistration through upstream admission, training, held-out validation, manuscript generation, publication packaging, and portal submission. Submission-facing LaTeX consumes only accepted generated evidence; project state and gate records remain outside the compiled manuscript.

**Tech Stack:** Python 3.13, `uv`, NumPy/pandas, Matplotlib, pytest/unittest, LaTeX/latexmk, ePC-SAFT public packages, native Ceres/CppAD capability metadata, JSON/YAML/CSV, Git/GitHub, Zenodo-compatible archive deposit, Elsevier Editorial Manager.

## Global Constraints

- Target submission date: Friday, July 24, 2026, in the morning (America/Denver).
- Target venue: *Fluid Phase Equilibria*, original research article, current Elsevier CAS LaTeX route.
- Submit only the full coupled pressure/speciation regression paper; there is no fixed-parameter fallback.
- Missing any scientific gate produces a submission hold.
- Preserve the frozen 147-training/220-validation observation split, source identities, readiness hashes, target roles, zero bounds, and aggregate targets.
- Keep `upstream_execution_admitted=false` until an immutable clean-package capability receipt proves the admitted native path.
- Do not fit against validation observations, omit failed predictions, relax gates after seeing results, or manually edit generated values.
- Treat solver convergence, numerical convergence, and physical acceptance as separate claims.
- The compiled manuscript contains no project-management, tracker, migration, backup, worktree, or implementation-status language.
- Do not create or use a repository-local `.worktrees` directory.
- External GitHub writes, releases, archive publication, and journal submission require explicit user approval at their gates.
- Build and submit from `docs/latex`; the dirty Overleaf mirror is outside the critical path.

---

## Calendar and hard gates

| Date | Required outcome | Hard stop |
| --- | --- | --- |
| Fri Jul 17 | Scope, author metadata requests, tracker/milestone execution contract | Missing author/venue ownership record |
| Sat Jul 18 | Hash-bound preregistration and leak-proof validation design | Mutable objective, split, bounds, or acceptance criteria |
| Sun Jul 19 noon | Immutable upstream execution admission | Capability absent, incomplete, mutable, or private |
| Mon Jul 20 | Completed native joint fit and conditional parameter promotion | Nonconvergence, incomplete rows/diagnostics, active-bound rejection, or failed physical gate |
| Tue Jul 21 noon | Held-out validation and identifiability receipts | Leakage, omitted failures, candidate drift, or unsupported identification claim |
| Wed Jul 22 | Scientific manuscript freeze and complete scientific proof | Any untraceable value, equation, citation, visual, or result claim |
| Thu Jul 23 | Publication freeze, release/archive, author approval | Missing metadata, license, DOI/data statement, package proof, or author approval |
| Fri Jul 24 morning | Portal proof accepted and submission confirmed | Portal-generated proof differs from frozen package |

## File responsibility map

### New internal control and evidence files

- `analyses/phase3/ionic_epcsaft_regression/config/final_fit_preregistration.json` — immutable fit objective, command, hashes, gates, and promotion policy.
- `analyses/phase3/ionic_epcsaft_regression/results/validation/validation_summary.json` — held-out aggregate and failure accounting bound to the promoted candidate.
- `analyses/phase3/ionic_epcsaft_regression/results/validation/validation_predictions.csv` — one record for every reserved observation, including failures.
- `analyses/phase3/ionic_epcsaft_regression/results/validation/validation_metrics_by_source.csv` — source/family held-out metrics.
- `analyses/phase3/ionic_epcsaft_regression/results/validation/identifiability_summary.json` — sensitivity, correlations, active bounds, robustness, and claim decision.
- `analyses/phase3/ionic_epcsaft_regression/scripts/evaluate_reserved_validation.py` — validation-only runner that cannot fit parameters.
- `src/MEA/common/method_inventory.py` — deterministic inventory of executed algorithms, configuration, package identities, and evidence hashes.
- `scripts/build_method_inventory.py` — writes the final method inventory and manuscript table inputs.
- `docs/latex/generated/method_inventory.json` — generated manuscript methods source.
- `docs/latex/tables/computational_method_inventory.tex` — concise executed-method table.
- `docs/latex/tables/regression_validation_summary.tex` — training/validation and failure-accounting table.
- `docs/latex/tables/fitted_parameter_changes.tex` — initial/fitted/bounds/active-bound parameter table.
- `docs/submission/fluid_phase_equilibria/submission_metadata.yml` — author-approved submission ledger outside the compiled tree.
- `docs/submission/fluid_phase_equilibria/highlights.txt` — required 3–5 journal highlights.
- `docs/submission/fluid_phase_equilibria/competing_interest.docx` — required separate declaration document.
- `docs/submission/fluid_phase_equilibria/cover_letter.md` — concise editor-facing cover letter.
- `docs/submission/fluid_phase_equilibria/submission_checklist.md` — venue and author sign-off record.
- `docs/submission/fluid_phase_equilibria/package_manifest.json` — file hashes and frozen commit/tag/DOI identities.
- `docs/submission/fluid_phase_equilibria/all_page_visual_review.md` — page-by-page inspection receipt.
- `docs/submission/fluid_phase_equilibria/release_archive_receipt.json` — tag, release, archive, DOI, license, and link verification.
- `docs/submission/fluid_phase_equilibria/submission_confirmation.json` — final journal manuscript identifier and confirmation metadata.
- `CITATION.cff`, `LICENSE`, and `LICENSE-DATA` — public citation and author-approved software/documentation and original-data reuse terms; third-party source tables remain excluded from relicensing.

### Existing implementation and manuscript owners

- `src/MEA/epcsaft_ionic/native_regression.py` — frozen target construction and role-aware training/validation problems.
- `src/MEA/epcsaft_ionic/global_regression.py` — package-native coupled fit orchestration and generated result bundles.
- `src/MEA/epcsaft_ionic/approval_check.py` — sole parameter-promotion decision owner.
- `analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py` — final fit entry point.
- `analyses/phase3/ionic_epcsaft_regression/scripts/compute_parameter_sensitivity.py` — candidate-bound sensitivity generation.
- `analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py` — Phase 3 final figure generation.
- `docs/latex/main.tex` — title, abstract, author metadata, keywords, and manuscript assembly.
- `docs/latex/sections/{epc_saft_equation_of_state,data_methods,mea_system_modeling_results,conclusion,data_code_availability}.tex` — final scientific narrative and declarations.
- `docs/latex/tables/*.tex` and `docs/latex/figures/*` — final generated/curated submission assets.
- `scripts/validate_project.py`, `scripts/check_epcsaft_integration.py`, `scripts/build_manuscript.sh`, and `scripts/check_manuscript_freshness.py` — final repository/manuscript proof.

---

### Task 1: Establish the sprint control surface and collect author decisions

**Deadline:** Friday, July 17

**Files:**
- Create: `docs/submission/fluid_phase_equilibria/submission_metadata.yml`
- Modify: `docs/superpowers/issues/{10,12,13,14,15,16,17,18}-*.md`
- Modify: `docs/superpowers/milestones/manuscript-submission.md`
- Test: `tests/test_submission_package.py`

**Interfaces:**
- Consumes: the approved sprint design and explicit author responses.
- Produces: a complete local metadata ledger plus an exact tracker/milestone mutation proposal.

- [ ] **Step 1: Add a failing metadata/package contract test**

  Require the ledger to contain `venue`, `article_type`, `submission_date`, `authors`, `corresponding_author`, `affiliations`, `orcid_policy`, `funding`, `acknowledgments`, `competing_interest`, `credit`, `ai_disclosure`, `license`, `archive`, and `reviewer_preferences`. Require the target date to equal `2026-07-24` and the venue to equal `Fluid Phase Equilibria`.

  Run:

  ```bash
  uv run pytest tests/test_submission_package.py -q
  ```

  Expected: FAIL because the ledger and package files do not exist.

- [ ] **Step 2: Collect author-controlled values with native structured prompts**

  Ask one bounded question at a time for authorship, full affiliation/address, corresponding email/contact, ORCID policy, funding, acknowledgments, competing interests, CRediT, AI disclosure, repository/data/documentation licenses, archive provider, release naming, and reviewer preferences. Do not infer answers from Git history or email domains.

- [ ] **Step 3: Populate the ledger without placeholder values**

  Store only the approved values. The file must not contain draft markers, example identities, unresolved values, or inferred legal terms.

- [ ] **Step 4: Reconcile local tracker mirrors to the full-paper critical path**

  Keep #12 → #13 → #14 as the scientific chain; make #16 consume the executed #13/#14 receipts; make #18 start only after the Tuesday scientific outputs; keep #17 in parallel; make #15 aggregate #16–18; make #10 the final submit-or-hold gate. Set the local manuscript milestone deadline to July 24.

- [ ] **Step 5: Prepare but do not perform live GitHub mutations**

  Generate a structured read-back checklist for issue bodies, relationships, labels, assignees, milestone due date, and acceptance checkboxes. Request explicit approval before `gh issue edit`, milestone mutation, assignment, or comments.

- [ ] **Step 6: Verify and commit**

  Run:

  ```bash
  uv run pytest tests/test_submission_package.py -q
  git diff --check
  ```

  Expected: metadata schema tests PASS; local issue/milestone mirrors describe one unambiguous critical path.

  Commit: `docs: establish FPE submission sprint controls`

---

### Task 2: Freeze the preregistered coupled-regression contract

**Deadline:** Saturday, July 18

**Files:**
- Create: `analyses/phase3/ionic_epcsaft_regression/config/final_fit_preregistration.json`
- Modify: `analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py`
- Modify: `src/MEA/epcsaft_ionic/approval_check.py`
- Modify: `tests/test_epcsaft_ionic_{native_regression,approval_check,artifact_promotion}.py`
- Modify: `tests/test_regression_readiness.py`

**Interfaces:**
- Consumes: readiness summary, split manifest, target construction, parameter specs, and upstream capability requirements.
- Produces: one hash-bound preregistration consumed by the fit and approval checker.

- [ ] **Step 1: Write failing preregistration tests**

  Require exact keys for schema version, created date, readiness hash, split hash, source hashes, 147/220 role counts, parameter names/order, initial values, lower/upper bounds, scales, regularization, target weights, zero-bound policy, aggregate-target policy, objective definition, solver/evaluation budget, accepted upstream capability hash, row-failure policy, metric gates, active-bound policy, plausibility gates, promotion policy, and exact command arguments.

  Add adversarial cases for split drift, changed source hash, reordered parameters, validation rows in the training problem, absent zero-bound policy, missing diagnostics, and post-result threshold changes.

- [ ] **Step 2: Run the focused tests and confirm the red state**

  ```bash
  uv run pytest tests/test_epcsaft_ionic_native_regression.py tests/test_epcsaft_ionic_approval_check.py tests/test_epcsaft_ionic_artifact_promotion.py tests/test_regression_readiness.py -q
  ```

  Expected: new preregistration tests FAIL; existing readiness and training-only behavior remains green.

- [ ] **Step 3: Add a preregistration-driven CLI**

  Add `--preregistration <path>` to `fit_global_pressure_speciation.py`. The entry point must load and validate the frozen file, derive the native problem only from `target_role="active_training"`, and reject any CLI override that changes objective, bounds, weights, regularization, evaluation budget, hashes, or gates.

- [ ] **Step 4: Freeze the measured execution budget before the full fit**

  Use only the admitted reduced public fixture to measure per-evaluation throughput. Record the resulting fixed `max_nfev` and wall-time ceiling in the preregistration before seeing full-fit results. Do not change either value after the fit begins.

- [ ] **Step 5: Bind promotion to the preregistration hash**

  Extend the global summary and approval result with the preregistration SHA-256. Reject promotion when the recorded hash, split hash, source hashes, parameter order, row counts, diagnostics, or gates differ.

- [ ] **Step 6: Verify deterministic preregistration and commit**

  ```bash
  uv run python scripts/build_regression_readiness.py
  uv run pytest tests/test_epcsaft_ionic_native_regression.py tests/test_epcsaft_ionic_approval_check.py tests/test_epcsaft_ionic_artifact_promotion.py tests/test_regression_readiness.py -q
  git diff --exit-code -- data/reference/MEA/manifests/grouped_split_manifest.csv analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json
  ```

  Expected: tests PASS; regenerated readiness bytes and 147/220 counts are unchanged; preregistration is stable across two reads.

  Commit: `test: preregister final coupled regression`

---

### Task 3: Admit and pin the upstream regression capability

**Deadline:** Sunday, July 19 at noon MDT

**Files:**
- Modify: `integration/epcsaft_contract.json`
- Modify: `src/MEA/epcsaft_ionic/native_regression.py`
- Modify: `scripts/check_epcsaft_integration.py`
- Modify: `analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json`
- Modify: `tests/test_epcsaft_contract.py`
- Modify: `tests/test_epcsaft_ionic_native_regression.py`
- Modify: `tests/test_phase3_authority_rebaseline.py`

**Interfaces:**
- Consumes: immutable clean provider/regression package refs and their accepted capability receipt.
- Produces: an admitted MEA adapter contract and immutable final integration identity.

- [ ] **Step 1: Verify the capability receipt before editing MEA**

  Require native Ceres ownership, exact residual Jacobians for admitted pressure/speciation targets, reduced public fixture success, public typed request/result/status APIs, complete evaluation/row/source/parameter diagnostics, installed-artifact isolation, and immutable package commits. Stop if any field is absent or inferred.

- [ ] **Step 2: Write failing adapter and final-mode tests**

  Add admitted, nonadmitted, malformed, private-import, mutable-source, missing-diagnostic, unsupported-target, and failed-fixture cases. Require exact public symbols from the accepted receipt rather than guessed names.

- [ ] **Step 3: Implement the smallest admitted adapter**

  Update the integration contract and `native_regression.py` to map MEA's frozen targets into the admitted public schema. Remove displaced root-package assumptions in the same checkpoint; do not retain a dual compatibility path.

- [ ] **Step 4: Rebuild readiness from immutable upstream evidence**

  Set `upstream_execution_admitted=true` only when the receipt hash and immutable package identities validate. Preserve every source hash and the 147/220 split.

- [ ] **Step 5: Run reduced smoke and final integration**

  ```bash
  uv run pytest tests/test_epcsaft_contract.py tests/test_epcsaft_ionic_native_regression.py tests/test_phase3_authority_rebaseline.py -q
  uv run python scripts/check_epcsaft_integration.py --mode final
  ```

  Expected: public reduced fixture PASS; final mode reports immutable clean package refs; no curated Phase 3 result changes occur.

- [ ] **Step 6: Stop or commit**

  If admission fails by noon, record a submission hold outside the manuscript and stop Tasks 4–9. If it passes, commit as `feat: admit clean reactive regression contract`.

---

### Task 4: Execute the full training fit and conditionally promote parameters

**Deadline:** Monday, July 20

**Files:**
- Modify: `analyses/phase3/ionic_epcsaft_regression/results/global_regression/*`
- Modify on approval only: `data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/**`
- Create: `analyses/phase3/ionic_epcsaft_regression/results/global_regression/global_regression_approval.json`
- Test: `tests/test_global_regression_artifacts.py`
- Test: `tests/test_epcsaft_ionic_artifact_promotion.py`

**Interfaces:**
- Consumes: the admitted upstream contract and frozen preregistration.
- Produces: immutable training result, approval decision, and an atomically promoted parameter set only on pass.

- [ ] **Step 1: Record protected hashes before execution**

  Hash the curated parameter dataset, readiness summary, grouped split, manuscript inputs, and current Phase 3 curated results. Store the comparison in the run-local result receipt.

- [ ] **Step 2: Run the exact preregistered fit**

  ```bash
  uv run python analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py \
    --preregistration analyses/phase3/ionic_epcsaft_regression/config/final_fit_preregistration.json \
    --output-label final_candidate \
    --promote \
    --verbose
  ```

  Expected: the entry point refuses execution unless Gate 2 is admitted; the native result reports positive evaluations, accepted termination, complete rows and diagnostics, and the preregistration hash.

- [ ] **Step 3: Run the sole promotion checker**

  ```bash
  uv run python -m MEA.epcsaft_ionic.approval_check analyses/phase3/ionic_epcsaft_regression/results/global_regression/global_regression_summary.json
  ```

  Expected: exit 0 and `approve_global_regression_promotion`. Any nonzero exit preserves the previous curated parameters and triggers submission hold.

- [ ] **Step 4: Verify atomic promotion and deterministic regeneration**

  ```bash
  uv run pytest tests/test_epcsaft_ionic_artifact_promotion.py tests/test_global_regression_artifacts.py -q
  uv run python analyses/phase3/ionic_epcsaft_regression/scripts/generate_data.py
  ```

  Run generation twice. Expected: second run produces no diff; protected readiness/split/source hashes are unchanged; only approval-authorized parameter/result paths change.

- [ ] **Step 5: Review scientific diagnostics**

  Confirm objective change, row coverage, termination, evaluations, parameter deltas, active bounds, residual structure, reaction/charge/balance gates, domain failures, and plausibility. Do not promote from objective improvement alone.

- [ ] **Step 6: Commit accepted evidence**

  Commit only a passing promoted candidate and its receipts as `feat: promote coupled MEA regression`. A failed run is retained only in the run-local diagnostic lane and causes submission hold.

---

### Task 5: Evaluate held-out evidence and decide identifiability

**Deadline:** Tuesday, July 21 at noon MDT

**Files:**
- Create: `analyses/phase3/ionic_epcsaft_regression/scripts/evaluate_reserved_validation.py`
- Create: `analyses/phase3/ionic_epcsaft_regression/results/validation/{validation_summary.json,validation_predictions.csv,validation_metrics_by_source.csv,identifiability_summary.json}`
- Modify: `analyses/phase3/ionic_epcsaft_regression/scripts/compute_parameter_sensitivity.py`
- Create: `tests/test_epcsaft_ionic_validation.py`
- Modify: `tests/test_manuscript_claim_integrity.py`

**Interfaces:**
- Consumes: immutable promoted candidate hash and `target_role="reserved_validation"` problem.
- Produces: complete held-out predictions, failure accounting, metrics, sensitivity/correlation results, and bounded claim decision.

- [ ] **Step 1: Write leakage and failure-accounting tests**

  Require candidate immutability, validation-only rows, group disjointness, one output per reserved observation, explicit failed-prediction status, metrics that cannot silently drop failures, and candidate/split/source hash agreement.

- [ ] **Step 2: Implement a validation-only runner**

  The script may load the promoted parameter map and evaluate the reserved problem. It must not call a fit function, mutate parameters, change bounds, rebuild the split, or write training outputs.

- [ ] **Step 3: Execute held-out validation**

  ```bash
  uv run python analyses/phase3/ionic_epcsaft_regression/scripts/evaluate_reserved_validation.py \
    --candidate analyses/phase3/ionic_epcsaft_regression/results/global_regression/global_regression_summary.json \
    --preregistration analyses/phase3/ionic_epcsaft_regression/config/final_fit_preregistration.json
  ```

  Expected: every reserved observation appears exactly once with prediction or explicit failure; no parameter mutation occurs.

- [ ] **Step 4: Run candidate-bound sensitivity and identifiability**

  ```bash
  uv run python analyses/phase3/ionic_epcsaft_regression/scripts/compute_parameter_sensitivity.py
  ```

  Bind all outputs to the promoted candidate hash. Report sensitivity ranks, near-zero directions, parameter-vector correlations, active bounds, perturbation stability, source/family dependence, and the exact supported claim boundary. Do not fabricate confidence intervals when covariance is unsupported.

- [ ] **Step 5: Verify and commit**

  ```bash
  uv run pytest tests/test_epcsaft_ionic_validation.py tests/test_regression_readiness.py tests/test_manuscript_claim_integrity.py -q
  ```

  Expected: leakage/failure/candidate-hash tests PASS; validation and sensitivity reruns are deterministic.

  Commit: `feat: validate promoted MEA parameter set`

---

### Task 6: Generate the executed method inventory and manuscript tables

**Deadline:** Tuesday, July 21 evening

**Files:**
- Create: `src/MEA/common/method_inventory.py`
- Create: `scripts/build_method_inventory.py`
- Create: `tests/test_method_inventory.py`
- Create: `docs/latex/generated/method_inventory.json`
- Create: `docs/latex/tables/{computational_method_inventory,regression_validation_summary,fitted_parameter_changes}.tex`
- Modify: `scripts/build_manuscript.sh`

**Interfaces:**
- Consumes: preregistration, upstream receipt, training/approval receipt, validation receipt, integration contract, and runtime declarations.
- Produces: deterministic JSON and LaTeX tables containing only executed settings and accepted evidence.

- [ ] **Step 1: Write failing inventory coverage tests**

  Require algorithm/owner, initialization, continuation, scaling, damping, tolerances, stopping/failure criteria, evaluation budget, objective weights, regularization, parameter bounds, active bounds, bubble-pressure route, permittivity/Born configuration, balance/reaction gates, package versions/commits, machine/runtime protocol, split/source hashes, candidate hash, and receipt hashes.

- [ ] **Step 2: Implement deterministic inventory assembly**

  Read values from executable declarations and immutable receipts. Reject missing fields and conflicting values. Do not insert unexecuted-state sentinels, examples, inferred defaults, or duplicated handwritten numerical constants.

- [ ] **Step 3: Generate concise LaTeX tables**

  Produce the method, training/validation, and parameter-change tables from the inventory/result files. Separate state count from target-observation count and include failed-row accounting.

- [ ] **Step 4: Add generation to the manuscript build preflight**

  Run the inventory/table generator before LaTeX compilation and fail if generated files differ from immutable receipts or source inputs.

- [ ] **Step 5: Verify and commit**

  ```bash
  uv run python scripts/build_method_inventory.py
  uv run pytest tests/test_method_inventory.py tests/test_manuscript_claim_integrity.py -q
  git diff --check
  ```

  Expected: two generator runs are byte-identical; no unresolved execution state exists.

  Commit: `feat: generate final computational evidence`

---

### Task 7: Rewrite the full-paper manuscript from accepted evidence

**Deadline:** Wednesday, July 22 morning

**Files:**
- Modify: `docs/latex/main.tex`
- Modify: `docs/latex/sections/epc_saft_equation_of_state.tex`
- Modify: `docs/latex/sections/data_methods.tex`
- Modify: `docs/latex/sections/mea_system_modeling_results.tex`
- Modify: `docs/latex/sections/conclusion.tex`
- Modify: `docs/latex/sections/data_code_availability.tex`
- Modify: `docs/latex/sections/nomenclature.tex`
- Modify: `docs/latex/source_log.md`
- Modify: `tests/test_manuscript_claim_integrity.py`

**Interfaces:**
- Consumes: accepted generated method, fit, validation, sensitivity, and identifiability evidence.
- Produces: final professional manuscript narrative with no unexecuted or project-state language.

- [ ] **Step 1: Strengthen submission-language and claim tests**

  Reject project-management terms, prospective regression descriptions, fixed/provisional parameter claims displaced by promotion, untraceable numeric literals, missing validation/failure accounting, and unsupported performance/uncertainty/identifiability claims.

- [ ] **Step 2: Reconcile theory and material balances**

  Derive the displayed carbon, amine, water, and charge conventions from the implemented balance matrix and cite the governing source or equation owner. Verify units, species order, reaction stoichiometry, and normalization.

- [ ] **Step 3: Rewrite methods in executed form**

  Replace the prospective objective and high-level implementation paragraph with the exact executed objective, native solver route, derivatives, initialization, scaling, tolerances, failure policy, preregistration, training/validation split, and parameter-promotion rules.

- [ ] **Step 4: Rewrite results and conclusions from generated evidence**

  Report training and held-out metrics separately; account for every failed prediction; report parameter movement/bounds and identifiability limitations; compare the fitted activity model with the ideal baseline on controlled evidence. The abstract and conclusion must agree with the final tables.

- [ ] **Step 5: Complete front matter and declarations**

  Populate author, affiliation, corresponding-author, ORCID policy, funding, acknowledgments, competing interests, CRediT, and exact AI disclosure from the approved ledger. Set explicit PDF title, author, subject, and keywords; remove the anomalous author glyph.

- [ ] **Step 6: Verify manuscript claims and build**

  ```bash
  uv run pytest tests/test_manuscript_claim_integrity.py tests/test_method_inventory.py -q
  bash scripts/build_manuscript.sh
  uv run python scripts/check_manuscript_freshness.py
  ```

  Expected: manuscript tests PASS; abstract is at most 250 words; no undefined citations/references; every reported number maps to generated evidence.

  Commit: `docs: integrate final regression manuscript`

---

### Task 8: Regenerate figures, tables, and publication layout

**Deadline:** Wednesday, July 22 afternoon

**Files:**
- Modify: `analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py`
- Modify: `analyses/phase3/ionic_epcsaft_regression/results/{global_regression,validation,sensitivity}/**`
- Modify: `docs/latex/figures/*`
- Modify: `docs/latex/tables/*.tex`
- Modify: `docs/latex/sections/{mea_system_modeling_results,nomenclature}.tex`
- Create: `docs/submission/fluid_phase_equilibria/all_page_visual_review.md`
- Modify: `tests/test_project_structure.py`
- Modify: `tests/test_manuscript_claim_integrity.py`

**Interfaces:**
- Consumes: frozen scientific CSV/JSON evidence.
- Produces: deterministic publisher-safe figure bundles, legible tables, balanced pages, and a visual-review receipt.

- [ ] **Step 1: Add figure bundle and font tests**

  Require same-stem PDF/PNG/SVG/plot-data/sidecar companions, source hashes, minimum label sizes, no Type 3 PDF fonts, and exact manuscript figure references. Require claimed validation/sensitivity series to be present.

- [ ] **Step 2: Render final scientific visuals**

  Separate major/trace species where necessary; include training versus held-out evidence, parameter changes, sensitivity/correlation or identifiability result, and complete failure accounting. Do not smooth, omit, or visually suppress rejected rows.

- [ ] **Step 3: Repair tables and page composition**

  Make the residual/validation and parameter tables readable at normal manuscript scale. Remove forced end-matter spacing, complete nomenclature, fix underfull/overfull layout causes, and balance references/nomenclature pages without altering scientific content.

- [ ] **Step 4: Verify deterministic rendering**

  ```bash
  uv run python scripts/render_all_plots.py
  uv run python scripts/render_all_plots.py
  uv run pytest tests/test_project_structure.py tests/test_manuscript_claim_integrity.py -q
  bash scripts/build_manuscript.sh
  ```

  Expected: second render and second build produce no unexplained diff; no missing companions, Type 3 fonts, clipping, undefined references, or overfull boxes.

- [ ] **Step 5: Inspect every PDF page**

  Record page number, figures/tables, legibility, clipping, whitespace, headers/footers, equations, citations, and disposition in `all_page_visual_review.md`. View at normal manuscript scale, not only enlarged zoom.

- [ ] **Step 6: Commit the scientific freeze**

  Commit: `fig: freeze FPE manuscript evidence`

  After this commit, change scientific results only to correct a proven blocker and rerun Tasks 5–8.

---

### Task 9: Build the Fluid Phase Equilibria submission package

**Deadline:** Thursday, July 23 morning

**Files:**
- Create: `docs/submission/fluid_phase_equilibria/{highlights.txt,competing_interest.docx,cover_letter.md,submission_checklist.md,package_manifest.json}`
- Create: `CITATION.cff`
- Create: `LICENSE`
- Create: `LICENSE-DATA`
- Modify: `README.md`
- Modify: `docs/latex/sections/data_code_availability.tex`
- Modify: `tests/test_submission_package.py`

**Interfaces:**
- Consumes: frozen scientific commit and approved metadata ledger.
- Produces: complete editable journal package and locally validated publication metadata.

- [ ] **Step 1: Write final package tests**

  Require 3–5 highlights with each line at most 85 characters; abstract at most 250 words; 1–7 keywords; complete title-page/contact/funding/declaration fields; valid `CITATION.cff`; approved license files; editable tables/equations; separate figure files; consistent citations; and no internal instruction or placeholder language.

- [ ] **Step 2: Write final highlights and cover letter**

  State only results proven by the frozen tables. The cover letter must identify the thermodynamic contribution, the joint pressure/speciation evidence, the held-out validation, the fit of the paper to the journal's equilibrium/thermophysical scope, sole/coauthorship, originality, and competing-interest status.

- [ ] **Step 3: Create the separate competing-interest document**

  Generate the journal-required `.docx` from the author-approved declaration. Verify it opens and matches the manuscript/portal declaration exactly.

- [ ] **Step 4: Assemble and hash the editable source package**

  Include `main.tex`, included sections, bibliography files, class/style files, editable tables, and separate final figures. Exclude `builds`, scripts not needed for compilation, internal plans, issue mirrors, caches, and the dirty Overleaf mirror.

- [ ] **Step 5: Run package and clean-checkout builds**

  ```bash
  uv run pytest tests/test_submission_package.py -q
  bash scripts/build_manuscript.sh
  uv run python scripts/check_manuscript_freshness.py
  ```

  Then compile the assembled source package from a clean temporary checkout. Expected: identical scientific content, resolved references, complete figures, correct metadata, and no local absolute path.

- [ ] **Step 6: Commit the local publication package**

  Commit: `docs: prepare Fluid Phase Equilibria submission package`

---

### Task 10: Publish immutable release/archive identifiers

**Deadline:** Thursday, July 23 afternoon

**Files:**
- Create: `docs/submission/fluid_phase_equilibria/release_archive_receipt.json`
- Modify: `docs/latex/sections/data_code_availability.tex`
- Modify: `CITATION.cff`
- Modify: `docs/submission/fluid_phase_equilibria/package_manifest.json`

**Interfaces:**
- Consumes: final clean scientific/package commit and explicit external-publication approval.
- Produces: immutable tag, GitHub release, archive deposit/DOI, and final resolvable availability statement.

- [ ] **Step 1: Run the pre-publication proof and request approval**

  Require clean Git state, passing Task 11 proof lanes, final author metadata, approved licenses, and exact tag/release/archive payloads. Show all irreversible or externally visible actions before execution.

- [ ] **Step 2: Create and publish the approved tag and GitHub release**

  Bind the release to the final commit and attach the verified manuscript/source/data package. Do not publish from a mutable or unverified commit.

- [ ] **Step 3: Publish the approved archive deposit**

  Deposit the final data/code release with author, title, description, license, version, related identifiers, and exact file hashes. Record the DOI and immutable archive URL.

- [ ] **Step 4: Cut final identifiers into the manuscript and citation metadata**

  Replace the current availability instruction with the final repository release, archive DOI, version, license scope, and reproducibility location. Rebuild and verify link resolution.

- [ ] **Step 5: Commit and verify publication metadata**

  Commit: `docs: publish manuscript archive metadata`

  Expected: `CITATION.cff`, manuscript, release, archive record, package manifest, and PDF metadata agree exactly.

---

### Task 11: Execute the complete submission-readiness proof

**Deadline:** Thursday, July 23 before author review

**Files:**
- Modify: `docs/submission/fluid_phase_equilibria/submission_checklist.md`
- Modify: `docs/superpowers/issues/10-final-submission-readiness-gate.md`
- Modify: `docs/superpowers/milestones/manuscript-submission.md`

**Interfaces:**
- Consumes: accepted #12–18 evidence, final package, release/archive receipt, and clean repository state.
- Produces: a complete readiness matrix and explicit author submit-or-hold prompt.

- [ ] **Step 1: Run locked environment and full repository proof**

  ```bash
  uv sync --locked --group test
  uv run ruff check src scripts analyses tests
  uv run pytest -q
  uv run python scripts/validate_project.py confidence
  uv run python scripts/check_epcsaft_integration.py --mode final
  ```

  Expected: all commands PASS against immutable admitted package identities.

- [ ] **Step 2: Run deterministic manuscript proof twice**

  ```bash
  bash scripts/build_manuscript.sh
  uv run python scripts/check_manuscript_freshness.py
  bash scripts/build_manuscript.sh
  uv run python scripts/check_manuscript_freshness.py
  ```

  Expected: stable input and PDF hashes; no undefined citations/references, overfull boxes, missing assets, Type 3 fonts, or anomalous PDF metadata.

- [ ] **Step 3: Run semantic publication checks**

  Verify every numerical claim against generated tables; every citation key against tracked bibliographies; every figure/table reference and caption; abstract/highlight limits; title/author/affiliation/funding/declaration consistency; archive links; license scope; complete source package; and all-page visual receipt.

- [ ] **Step 4: Run cleanup and source-state audit**

  ```bash
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  git status --short --branch
  ```

  Remove only task-owned ignored candidates through the cleanup hook's explicit removal mode. Expected: clean branch, no task-owned process, no repository-local `.worktrees`, and no untracked package debris.

- [ ] **Step 5: Reconcile live GitHub state with approval**

  After explicit approval, update/read back acceptance and closeout evidence for #12, #13, #14, #16, #17, #18, #15, and finally #10. Set the Manuscript Submission milestone due date to July 24. Do not close an issue whose proof lane failed.

- [ ] **Step 6: Present the author gate**

  Show the frozen PDF, title/abstract, central metrics, parameter/identifiability decision, all known limitations, package manifest, DOI/release, venue checklist, and proof results. Request one explicit `submit` or `hold` decision.

---

### Task 12: Submit and verify the journal record

**Deadline:** Friday, July 24 in the morning

**Files:**
- Create after submission: `docs/submission/fluid_phase_equilibria/submission_confirmation.json`
- Modify after submission: `docs/submission/fluid_phase_equilibria/submission_checklist.md`

**Interfaces:**
- Consumes: explicit submit approval and the frozen package manifest.
- Produces: verified Editorial Manager submission and retained confirmation metadata.

- [ ] **Step 1: Run the short smoke gate**

  ```bash
  git status --short --branch
  uv run python scripts/check_epcsaft_integration.py --mode final
  uv run python scripts/check_manuscript_freshness.py
  uv run pytest tests/test_submission_package.py tests/test_manuscript_claim_integrity.py -q
  ```

  Expected: clean source state and all checks PASS without regeneration or scientific changes.

- [ ] **Step 2: Upload exactly the frozen package**

  Enter manuscript type, title, abstract, keywords, authors, affiliations, funding, declarations, data statement/DOI, suggested/opposed reviewers, and highlights from the approved ledger/package. Upload editable LaTeX sources, separate figures, competing-interest document, and any portal-required supporting files.

- [ ] **Step 3: Inspect the portal-generated proof**

  Compare title, author/affiliation, abstract, equations, tables, figures, captions, references, special characters, declarations, and page completeness with the frozen PDF. Stop before final submission on any mismatch.

- [ ] **Step 4: Submit and retain confirmation**

  After proof acceptance, complete the submission. Record journal, manuscript identifier, submission timestamp/timezone, corresponding author, frozen commit/tag, PDF SHA-256, archive DOI, release URL, and confirmation reference in `submission_confirmation.json`.

- [ ] **Step 5: Commit the confirmation record**

  Commit: `docs: record Fluid Phase Equilibria submission`

  Run the cleanup audit and verify a clean repository.

---

## Final stop conditions

The July 24 submission is held if any of the following remains true:

- upstream execution is not immutably admitted by Sunday noon;
- the joint fit is nonconverged, incomplete, physically rejected, or not promotable;
- held-out evaluation leaks training information, omits failures, or cannot support the stated validation/identifiability claim;
- manuscript numbers, equations, tables, figures, or conclusions lack immutable evidence;
- author/legal metadata, license, archive, DOI, or declarations are incomplete;
- final integration, tests, confidence validation, deterministic build, visual review, or source-package reproduction fails; or
- the author does not explicitly approve submission.

No stop condition may be bypassed by editorial wording, a manual parameter edit, a looser threshold, or submission urgency.
