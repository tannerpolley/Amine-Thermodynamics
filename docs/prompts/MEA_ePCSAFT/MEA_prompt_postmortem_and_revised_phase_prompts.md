# Revised Agent Prompt Standards After PR #7 Review

## Purpose

This document is a postmortem and replacement prompt language for the MEA-Thermodynamics Phase 1 and Phase 2 agents.

The failure mode in PR #7 was not that the agents were lazy. The failure mode was that the prompts allowed a roadmap/scaffold to be treated as phase completion. The prompts used words like “document,” “generate,” “status explicit,” and “PR-ready,” but did not define hard numerical acceptance thresholds, failure conditions, source-verification tests, or what to do when residuals were unacceptable.

These revisions add explicit completion gates.

---

# 1. Prompt failure postmortem

## 1.1 What went wrong

### Failure 1 — “Scaffold exists” was allowed to imply “phase complete”

The earlier prompt asked the agent to:

- update roadmaps,
- create manifests,
- create target folders,
- document data status,
- list required artifacts.

It did not say:

> Creating a manifest or status table does not count as completing the phase.

The result was predictable: the agent created useful files and statuses, then treated the scaffold as closer to completion than it actually was.

### Failure 2 — No hard residual thresholds were stated

The prompt did not define any of these:

- maximum acceptable pressure residual,
- maximum acceptable speciation residual,
- what to do with failed species,
- whether trace species can appear in success figures,
- how to classify unsupported species,
- what residuals force “bounded incomplete.”

The agent generated residuals and did not fail the phase even when major values were unacceptable.

### Failure 3 — The prompt did not require an explicit residual audit

The agent should have been required to produce a file like:

```text
phase1_residual_acceptance_audit.csv
```

with:

```text
species_or_property
metric
threshold
actual_value
passes
claim_allowed
reason
```

Because that was not required, the agent could produce metrics without interpreting them.

### Failure 4 — The prompt did not forbid self-certification

The prompt allowed status files such as:

```text
ready
generated
promoted_reference_state_verified
```

without requiring independent verification against source data, tests, and numerical criteria.

That allowed the agent to certify the output by writing a file that said the output was ready.

### Failure 5 — Source verification was too weak

The prompt said to use repo-local Markdown papers and update manifests. It did not say:

> A source is not “verified” until the exact source row/table/figure is available in this repo or in a machine-readable manifest with DOI, source location, and extracted value.

This allowed local absolute source paths and source claims to leak into tracked data.

### Failure 6 — “PR-ready” was too ambiguous

The phrase “PR-ready” let the agent optimize for a coherent commit, not a scientifically complete phase.

A PR can be useful and still incomplete. The prompt needed the status vocabulary:

```text
scaffold_ready
data_inventory_ready
model_ran
validated
publication_ready
bounded_incomplete
```

### Failure 7 — The prompts did not force draft PR behavior

The prompt should have said:

> If any required model output is missing, blocked, or fails residual thresholds, the PR must remain draft and the issue must remain open.

That was missing.

### Failure 8 — It did not distinguish “roadmap acceptance” from “scientific acceptance”

The agent satisfied several roadmap tasks but did not satisfy the scientific intent of Phase 1 or Phase 2.

The revised prompt must separate:

```text
roadmap scaffolding
data extraction
model execution
residual validation
manuscript claim authorization
```

---

# 2. Non-negotiable global completion contract

Add this to the top of every Phase 1, Phase 2, and Phase 3 prompt.

```markdown
# Non-Negotiable Completion Contract

Do not call this issue complete, do not mark the PR ready for review, and do not write language implying phase completion unless every required completion gate below passes.

A file, manifest, scaffold, README, status table, or placeholder artifact is not evidence of scientific completion.

The following statuses are allowed:

- `scaffold_ready`: roadmaps/manifests/scripts exist, but model outputs are missing or blocked.
- `data_inventory_ready`: source/data inventory is complete, but model execution is not complete.
- `model_ran`: model produced numerical outputs, but validation has not passed.
- `validated`: model outputs passed residual, provenance, and artifact gates.
- `publication_ready`: validated outputs are connected to manuscript figures/tables/claims.
- `bounded_incomplete`: work is useful but cannot satisfy phase completion because of a blocker, bad residuals, missing data, or missing package support.

Only `validated` or `publication_ready` may close a scientific phase issue.

If a solver/package blocker prevents required outputs, the correct status is `scaffold_ready` or `bounded_incomplete`, not `complete`.

If numerical residuals fail thresholds, the correct status is `model_ran_but_failed_validation`, not `complete`.

If source values are taken from local paths outside this repo, the correct status is `source_pending`, not `source_verified`.

Do not self-certify readiness by writing a CSV that says `ready`. Readiness requires tests and residual audits that compare actual values to thresholds.

The PR must remain draft if any required output is missing, blocked, or fails validation.
```

---

# 3. Revised Phase 1 prompt

## Title

Phase 1: True Smith–Missen MEA reproduction baseline, not scaffold-only audit

## Replacement prompt

```markdown
You are working in `tannerpolley/MEA-Thermodynamics`.

Your task is to complete Phase 1 only if you can produce a true, validated Smith–Missen-style MEA baseline. If you can only create a scaffold or reuse old outputs, leave the issue open and label the result `scaffold_ready` or `bounded_incomplete`.

## Scientific goal

Reproduce the historical MEA–CO2–H2O PC-SAFT / SAFT-HR style workflow:

- neutral EOS parameters for MEA, H2O, and CO2;
- MEA/H2O association scheme decision;
- MEA–H2O binary interaction basis;
- apparent or ideal Smith–Missen chemical-equilibrium speciation;
- CO2 partial pressure vs loading;
- speciation vs loading for measured major species;
- explicit comparison to the Baygi/Najafloo/Nasrifar baseline.

This phase is not an ePC-SAFT activity-based model and is not a final regression.

## Absolute failure conditions

If any of the following occur, do not mark Phase 1 complete:

1. The workflow only reuses old processed outputs without independently documenting and validating the Baygi/Najafloo-style calculation.
2. Any reaction constant coefficient disagrees with the cited source table.
3. Any tracked manifest/result/doc contains an absolute local path such as `C:/Users`, `C:\Users`, `/Users/`, or another machine-local source path.
4. Pressure or speciation metrics are generated but not compared to explicit thresholds.
5. A species with failing residuals is shown in a main success figure without a failure/diagnostic label.
6. The output says or implies `Phase 1 complete` while residual gates fail.
7. Data rows lack source, units, status, and fit/validation role.

## Required source verification

Create:

```text
data/reference/MEA/manifests/phase1_source_value_verification.csv
```

For every parameter and reaction constant, include:

```text
item_id
value_name
value
units
source_key
source_file_repo_relative
source_table_or_figure
source_row_or_line
verified_against_source: yes/no
notes
```

No source entry may use absolute paths. If the source file is not in the repo, status must be:

```text
source_pending
```

not:

```text
verified
```

## Required reaction-constant test

Add a test that checks the exact R1–R5 coefficients used in Phase 1.

For the Baygi/Nasrifar mole-fraction reaction constants, R1 must use:

```text
A = 132.899
B = -13445.9
C = -22.4773
D = 0
```

If the code or generated table has `C = +22.4773`, the test must fail.

The test must read the generated `phase1_reaction_constant_table.csv`, not only the source code.

## Required model-lineage declaration

Create:

```text
analyses/phase1_smith_missen_baseline/results/phase1_model_lineage.md
```

It must state one of these:

```text
independent_reproduction
retained_baseline_audit
translation/parity_check
scaffold_only
```

Rules:

- If the script reuses `six_species_legacy` or `epcsaft_neutral_parity` processed outputs, the status cannot be `independent_reproduction`.
- If the selected 3B MEA / 4C water model is not directly run, the status cannot be `independent_reproduction`.
- If explicit Smith–Missen equations are not solved in this phase script, the status cannot be `independent_reproduction`.

## Required residual audit

Create:

```text
analyses/phase1_smith_missen_baseline/results/phase1_residual_acceptance_audit.csv
```

Columns:

```text
target_family
source
temperature_C
species_or_property
metric
threshold
actual_value
passes
claim_allowed
failure_reason
recommended_manuscript_use
```

### Pressure acceptance gate

Compute relative pressure error and log-pressure error.

Minimum required metrics:

```text
AAD_percent
median_abs_log10_error
RMSE_log10
max_abs_log10_error
```

Phase 1 pressure can be marked `passes` only if either:

```text
AAD_percent <= 50
```

or

```text
median_abs_log10_error <= 0.25
```

and all pressure figures clearly state this is a Phase 1 apparent-speciation baseline.

If pressure exceeds these thresholds, status must be:

```text
model_ran_but_failed_pressure_validation
```

### Speciation acceptance gate

Classify species before plotting:

```text
major_fit_or_validation_species
trace_diagnostic_species
unsupported_by_reduced_solver
not_evaluated
```

For a species to appear as a successful Phase 1 model result in a main figure:

```text
median_abs_log10_error <= 0.50
```

and

```text
mae_log10 <= 0.75
```

If a species fails these thresholds:

- it may appear only in a diagnostic plot;
- it must be labeled as failed/diagnostic;
- it must not be used to support a manuscript claim of successful speciation reproduction.

If `MEACOO-`, `MEAH+`, `MEA + MEAH+`, or `HCO3-` fails at a major source/temperature combination, Phase 1 speciation is not complete.

### Special trace-species rule

For CO2 molecular liquid, CO3^2-, H3O+, and OH-:

- do not include in a success claim unless directly supported and residuals pass;
- otherwise mark as `trace_diagnostic_species` or `unsupported_by_reduced_solver`.

## Required claim-boundary artifact

Create:

```text
analyses/phase1_smith_missen_baseline/results/phase1_claim_boundary.md
```

It must explicitly say:

- what the Phase 1 model can claim;
- what it cannot claim;
- which species/properties failed thresholds;
- whether the result is `validated`, `model_ran_but_failed_validation`, or `scaffold_ready`.

## Required figures

Only generate main figures from passing outputs.

If a figure contains failed species, the filename must include:

```text
diagnostic
```

Required figures:

```text
phase1_pressure_vs_loading.png/svg/yaml
phase1_speciation_vs_loading.png/svg/yaml
```

If speciation residuals fail, rename the figure:

```text
phase1_speciation_vs_loading_diagnostic.png/svg/yaml
```

and update captions accordingly.

## Required tests

Add tests for:

1. no absolute local paths in tracked docs/manifests/results;
2. R1–R5 coefficient values and signs;
3. every generated data row has source, units, role, and status where applicable;
4. residual acceptance audit exists;
5. no main-success figure includes failed species without diagnostic labeling;
6. no Phase 1 document claims final ePC-SAFT or final coupled regression.

## Completion definition

Phase 1 is complete only if all are true:

- source verification passes;
- no local paths are present;
- reaction constants match source values;
- model-lineage status is honest;
- pressure residual gate passes;
- major speciation residual gate passes or the phase is explicitly marked incomplete;
- figures are named and captioned according to pass/fail status;
- tests pass;
- manuscript claim boundary is written.

If any gate fails, leave the issue open and produce:

```text
phase1_bounded_incomplete_report.md
```

Do not mark the PR ready for review.
```

---

# 4. Revised Phase 2 prompt

## Title

Phase 2: Activity-based true-species ePC-SAFT evaluation with hard solver/output gates

## Replacement prompt

```markdown
You are working in `tannerpolley/MEA-Thermodynamics`.

Your task is to complete Phase 2 only if the generic ePC-SAFT package can produce convention-safe activity-based speciation and VLE/pressure outputs. If the required package path is blocked, do not mark Phase 2 complete. Mark the result `scaffold_ready` or `bounded_incomplete`.

## Scientific goal

Build a true-species activity-based ePC-SAFT evaluation for MEA–CO2–H2O:

- nine-species liquid basis;
- neutral volatile vapor basis;
- explicit reaction network;
- thermodynamic-activity reaction constants or documented conversions;
- ePC-SAFT activities/fugacities inside the residual;
- pressure/speciation outputs generated from one parameter artifact;
- residual and solver diagnostics;
- honest blocker reporting.

## Absolute failure conditions

If any of the following occur, do not mark Phase 2 complete:

1. `phase2_equilibrium_results.csv` does not exist.
2. `phase2_pressure_speciation_parity.csv` does not exist.
3. `phase2_pressure_metrics.csv` or `phase2_speciation_metrics.csv` does not exist.
4. The package solver is blocked by upstream ePC-SAFT support.
5. The workflow only writes a problem JSON or readiness table.
6. Reaction constants are called `verified` while the source file/table is not repo-local or machine-readable.
7. Any manifest/result/doc contains absolute local paths.
8. The problem uses stale or external activities instead of ePC-SAFT activities inside the nonlinear residual.
9. The script uses a downstream MEA-specific nonlinear workaround instead of a generic package route, unless clearly labeled diagnostic and not complete.
10. Phase 2 documents claim activity-based prediction while actual equilibrium rows are missing.

## Required source verification for activity constants

Create:

```text
data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv
```

Required columns:

```text
reaction_id
source_key
source_file_repo_relative
source_table_or_figure
source_value_A
source_value_B
source_value_C
source_value_D
basis_in_source
standard_state
activity_convention
verified_against_source: yes/no
conversion_performed: yes/no
conversion_notes
used_in_phase2: yes/no
```

Rules:

- If `source_file_repo_relative` is missing, status is `source_pending`.
- If any value is copied from a local path outside this repo, status is `source_pending`.
- Do not use `promoted_reference_state_verified` unless the source table is repo-local and tested.
- `Austgen1991_TableV` may be used only after exact source values and standard-state convention are verified.

## Required problem schema

The Phase 2 problem JSON must include:

```text
species
charges
volatile_species
nonvolatile_species
material_balances
electroneutrality_constraint
reaction_residuals
activity_convention
reference_states
parameter_artifact
dielectric_option
born_option
solver_route
package_dependency_status
```

Do not put charge/electroneutrality in the same dictionary as material balances. Use:

```json
"material_balances": {...},
"constraints": {
  "electroneutrality": {...}
}
```

or equivalent.

## Required package-solver proof

Phase 2 can be complete only if the model is solved through a generic ePC-SAFT package route.

Required output:

```text
analyses/phase2_activity_epcsaft/results/phase2_solver_diagnostics.csv
```

Columns:

```text
row_id
temperature_K
pressure_or_loading
solver_backend
activity_backend
reaction_residual_norm
charge_residual_norm
material_residual_norm
fugacity_residual_norm
iterations
converged
failure_reason
```

Completion thresholds:

```text
reaction_residual_norm <= 1e-7
charge_residual_norm <= 1e-9
material_residual_norm <= 1e-9
fugacity_residual_norm <= 1e-7
converged == true
```

If these cannot be produced because upstream ePC-SAFT issue #115 is open or package support is unavailable, Phase 2 status is:

```text
scaffold_ready_blocked_by_epcsaft_issue_115
```

not complete.

## Required numerical outputs

Phase 2 completion requires these files:

```text
phase2_equilibrium_results.csv
phase2_pressure_speciation_parity.csv
phase2_pressure_metrics.csv
phase2_speciation_metrics.csv
phase2_solver_diagnostics.csv
phase2_residual_acceptance_audit.csv
phase2_claim_boundary.md
```

If any are missing, Phase 2 is incomplete.

## Required residual audit

Create:

```text
analyses/phase2_activity_epcsaft/results/phase2_residual_acceptance_audit.csv
```

Columns:

```text
target_family
source
temperature_C
species_or_property
metric
threshold
actual_value
passes
claim_allowed
failure_reason
recommended_manuscript_use
```

### Pressure acceptance gate

For any pressure claims:

```text
median_abs_log10_error <= 0.25
```

or a source-justified literature-comparable threshold.

If pressure residuals exceed the threshold, Phase 2 may still be a diagnostic run but not a validated activity-based VLE model.

### Speciation acceptance gate

For species used in the main Phase 2 claim:

```text
median_abs_log10_error <= 0.50
mae_log10 <= 0.75
```

If a species fails, mark it as diagnostic or failed and exclude it from success claims.

### pH validation gate

Use pH only if:

- pH scale is documented;
- electrode/method is documented;
- conversion to model activity basis is documented.

If not, status is:

```text
pH_anchor_only
```

not a fit/validation residual.

### Density/viscosity gate

Amundsen density/viscosity data can be:

```text
external_validation
regularization_candidate
not_evaluated
```

Do not claim density/viscosity validation unless a model prediction is actually generated.

## Required single-parameter-artifact rule

Every Phase 2 pressure/speciation/density/pH output must use one parameter artifact.

Create:

```text
phase2_parameter_artifact_lineage.json
```

It must record:

```text
parameter_artifact_path
git_sha
species_table_sha
kij_table_sha
user_options_sha
used_for_pressure: yes/no
used_for_speciation: yes/no
used_for_density: yes/no
used_for_pH: yes/no
```

If outputs use different parameter artifacts, Phase 2 is incomplete.

## Required no-local-path test

Add a test that scans at least:

```text
docs/
data/reference/MEA/manifests/
analyses/phase1_smith_missen_baseline/results/
analyses/phase2_activity_epcsaft/results/
pyproject.toml
src/MEA/
```

and fails on:

```text
C:/Users
C:\Users
/Users/
Documents/git
```

If a local override is needed for development, move it to an untracked file or dev-only documentation that is explicitly excluded from publication artifacts.

## Required tests

Add tests for:

1. no absolute local paths;
2. reaction constants source verification;
3. Phase 2 problem JSON schema;
4. absence of Phase 2 completion claim if equilibrium outputs are missing;
5. solver diagnostics residual thresholds if equilibrium outputs exist;
6. one-parameter-artifact lineage;
7. no MEA-specific public API request;
8. no final regression/manuscript claim before Phase 3.

## Completion definition

Phase 2 is complete only if all are true:

- activity constants are source-verified;
- no local paths exist in tracked publication-facing files;
- generic package solver produces equilibrium rows;
- solver residual norms pass;
- pressure/speciation metrics pass or are honestly marked failed;
- pressure/speciation figures use one parameter artifact;
- Phase 2 claim boundary is written;
- tests pass.

If upstream ePC-SAFT issue #115 blocks the solve, produce:

```text
phase2_bounded_incomplete_report.md
```

and keep the PR draft.
```

---

# 5. Revised Codex instruction for PR self-review

Add this to the end of every agent prompt.

```markdown
# Required self-review before PR submission

Before opening or updating the PR, write:

```text
docs/roadmaps/agent_self_review_<issue>.md
```

It must answer:

1. What did I actually complete?
2. What remains scaffold-only?
3. Which issue acceptance criteria are not satisfied?
4. Which residual thresholds passed?
5. Which residual thresholds failed?
6. Which files prove each pass/fail?
7. Are there any local paths in tracked files?
8. Are there any generated status files that self-certify without external evidence?
9. Are any figures showing failed species/properties without diagnostic labels?
10. Should this PR remain draft?

If any answer indicates missing outputs, failed residuals, local paths, or package blockers, the PR must remain draft and the issue must stay open.

Do not write “complete” in the PR title or body unless every completion gate passes.
```

---

# 6. Revised PR title/body standard

## If scaffold only

Title:

```text
[draft][scaffold] Phase 1/2 roadmap and artifact scaffold
```

Body must include:

```markdown
## Status

This PR is scaffold-ready only. It does not complete Phase 1/2.

## Blockers

- ...
```

## If model ran but residuals failed

Title:

```text
[draft][bounded-incomplete] Phase 1 model ran but failed residual gates
```

Body must include:

```markdown
## Failed residual gates

| target | threshold | actual | status |
|---|---:|---:|---|
```

## If validated

Title:

```text
[validated] Phase 1 Smith–Missen baseline reproduction
```

Allowed only after all completion gates pass.

---

# 7. Why the residuals should never have passed

The agent let the residuals pass because the prompt let it.

The prompt required generated tables and figures, but not:

- residual thresholds;
- a pass/fail residual audit;
- mandatory interpretation of every metric;
- blocking behavior when residuals were bad;
- diagnostic relabeling for failed species;
- a source-backed claim boundary.

A scientifically safe prompt must not allow this logic:

```text
metrics generated -> task complete
```

It must require:

```text
metrics generated -> compared to thresholds -> pass/fail assigned -> claims restricted -> issue status decided
```

The current Phase 1 residuals should have triggered:

```text
model_ran_but_failed_speciation_validation
```

or:

```text
retained_baseline_audit_only
```

not phase completion.

---

# 8. Minimal patch request to fix PR #7

Give this to the agent working on PR #7:

```markdown
Keep PR #7 draft. Do not mark Phase 1 or Phase 2 complete.

Patch the PR as follows:

1. Remove all local absolute paths from tracked files.
   - Replace absolute user-machine paths with repo-local paths or `source_pending`.
   - Add a no-local-path test to quick validation.

2. Fix the Phase 1 R1 reaction constant coefficient.
   - `C` must be `-22.4773`, not `+22.4773`.
   - Add tests for R1-R5 coefficient values and signs.

3. Add `phase1_model_lineage.md`.
   - If Phase 1 reuses `six_species_legacy` or `epcsaft_neutral_parity`, mark it `retained_baseline_audit`, not `independent_reproduction`.

4. Add `phase1_residual_acceptance_audit.csv`.
   - Define thresholds.
   - Mark CO2/HCO3-/CO3^2-/MEACOO-/MEAH+ failures explicitly.
   - Do not allow failed species to appear as success evidence.

5. Add `phase1_claim_boundary.md`.
   - State what Phase 1 can and cannot claim.

6. Add `phase2_bounded_incomplete_report.md`.
   - State that Phase 2 is a problem-definition scaffold until upstream ePC-SAFT issue #115 is resolved.
   - Do not call Phase 2 complete.

7. Add `phase2_reaction_constant_source_verification.csv`.
   - A source is not verified unless the source table is repo-local and values are tested.

8. Revise tests.
   - no local paths;
   - reaction coefficient values;
   - source verification;
   - blocked Phase 2 outputs remain absent;
   - no final regression claims in Phase 1/2 files.

9. Update the PR body.
   - Say this is scaffold/bounded-incomplete.
   - List failed gates and blockers.
```

---

# 9. Final corrected stance

The original prompts were too permissive. They optimized for organization, not scientific acceptance.

The corrected rule is:

> A phase is not complete because files exist. A phase is complete only when source-backed values, generated numerical outputs, residual thresholds, artifact lineage, tests, and manuscript claim boundaries all pass.

For this project, the agent must be forced to fail loudly. That is the only way to prevent a scaffold from turning into a false manuscript claim.
