# Exact Agent Prompt: Repair PR #7 Phase 1/Phase 2 Scaffold and Add Hard Completion Gates

You are working in `tannerpolley/MEA-Thermodynamics`.

You must repair the existing draft PR:

```text
PR #7: [codex] Implement phase 2 activity scaffold
Branch: manuscript-project-phase-implementation
```

Do **not** create a new broad roadmap PR unless PR #7 cannot be edited. Continue from PR #7.

## Critical instruction

PR #7 must remain **draft** unless every validation gate in this prompt passes.

Do not claim Phase 1 complete.
Do not claim Phase 2 complete.
Do not mark the PR ready for review.
Do not close issues #4 or #5.

The correct goal for this run is:

```text
Repair PR #7 so that it honestly reports Phase 1 and Phase 2 as scaffold/bounded-incomplete where appropriate, adds hard residual/source-validation gates, removes non-portable paths, and prevents future agents from mistaking generated files for scientific completion.
```

## Non-negotiable completion contract

A file, manifest, README, status table, scaffold, or placeholder artifact is not evidence of scientific completion.

Only validated numerical outputs can close a scientific phase.

Use these status values exactly:

```text
scaffold_ready
data_inventory_ready
model_ran
model_ran_but_failed_validation
validated
publication_ready
bounded_incomplete
source_pending
source_verified
```

Only `validated` or `publication_ready` may be used for a completed scientific phase.

If a package/solver blocker prevents required outputs, the status is:

```text
bounded_incomplete
```

or:

```text
scaffold_ready_blocked_by_epcsaft_issue_115
```

If numerical residuals fail thresholds, the status is:

```text
model_ran_but_failed_validation
```

If source values come from a path outside this repo, the status is:

```text
source_pending
```

not:

```text
source_verified
```

Do not self-certify readiness by writing a CSV that says `ready`. Readiness requires source verification, residual audits, and tests.

## The failure to repair

The previous agent allowed this incorrect logic:

```text
files exist -> status CSV says ready -> phase goal accomplished
```

Replace that with:

```text
source values verified -> model outputs generated -> residuals checked against thresholds -> pass/fail assigned -> claims restricted -> phase status decided
```

## Required patch tasks

### Task 1 — Remove all local absolute paths from tracked files

Search the repo for:

```powershell
rg -n "C:/Users|C:\\Users|/Users/|Documents/git" .
```

Fix every tracked occurrence in:

```text
docs/
data/reference/MEA/manifests/
analyses/*/results/
analyses/*/data/processed/
pyproject.toml
src/MEA/
```

For `data/reference/MEA/manifests/phase2_activity_constant_candidates.csv`, replace local paths such as:

```text
C:/Users/Tanner/Documents/git/Lithium_Extraction/data/Austgen...
```

with repo-local paths if the source exists under:

```text
docs/papers/md/
```

If the source file is not in this repo, set:

```text
source_files = source_pending
phase2_status = source_pending
validation_role = not_used_until_repo_local_source_verified
```

Do not keep any absolute local path.

### Task 2 — Add a no-local-path validation test

Add either:

```text
scripts/check_no_local_paths.py
```

or integrate the check into:

```text
scripts/validate_project.py quick
```

The check must fail on:

```text
C:/Users
C:\Users
/Users/
Documents/git
```

Run it over at least:

```text
docs/
data/reference/MEA/manifests/
analyses/phase1_smith_missen_baseline/
analyses/phase2_activity_epcsaft/
pyproject.toml
src/MEA/
```

Allow only explicitly ignored binary/image files if needed.

### Task 3 — Fix Phase 1 R1 reaction constant coefficient sign

In:

```text
analyses/phase1_smith_missen_baseline/scripts/generate_data.py
```

fix R1 water autoprotolysis:

```text
A = 132.899
B = -13445.9
C = -22.4773
D = 0
```

The current `C = +22.4773` is wrong for the Baygi/Nasrifar mole-fraction table.

Regenerate:

```text
analyses/phase1_smith_missen_baseline/data/processed/phase1_reaction_constant_table.csv
analyses/phase1_smith_missen_baseline/results/phase1_reaction_constant_table.csv
```

### Task 4 — Add reaction constant source-value tests

Add tests that read the generated CSV, not only source code:

```text
analyses/phase1_smith_missen_baseline/results/phase1_reaction_constant_table.csv
```

The test must verify R1-R5 values against the source table.

At minimum:

```python
R1: A=132.899, B=-13445.9, C=-22.4773, D=0
R2: A=231.465 or source-confirmed Baygi/Nasrifar value, B=-12092.1, C=-36.7816, D=0
R3: A=216.049, B=-12431.7, C=-35.4819, D=0
R4/R5: verify against the exact cited source used in the manifest
```

If Baygi and Austgen/Tong conventions differ, document the difference. Do not silently mix them.

### Task 5 — Add Phase 1 model-lineage artifact

Create:

```text
analyses/phase1_smith_missen_baseline/results/phase1_model_lineage.md
```

It must state one of:

```text
independent_reproduction
retained_baseline_audit
translation/parity_check
scaffold_only
```

Rules:

- If the workflow reuses `six_species_legacy` or `epcsaft_neutral_parity` processed outputs, it **cannot** be `independent_reproduction`.
- If the selected 3B MEA / 4C water model is not directly run, it **cannot** be `independent_reproduction`.
- If explicit Smith-Missen equations are not solved in the Phase 1 script, it **cannot** be `independent_reproduction`.

For the current PR #7 state, this should probably be:

```text
retained_baseline_audit
```

or:

```text
translation/parity_check
```

unless you implement a real independent reproduction.

### Task 6 — Add Phase 1 residual acceptance audit

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

#### Pressure gate

Compute:

```text
AAD_percent
median_abs_log10_error
RMSE_log10
max_abs_log10_error
```

Pressure passes Phase 1 only if either:

```text
AAD_percent <= 50
```

or:

```text
median_abs_log10_error <= 0.25
```

If not, set:

```text
model_ran_but_failed_pressure_validation
```

#### Speciation gate

Classify each species as one of:

```text
major_fit_or_validation_species
trace_diagnostic_species
unsupported_by_reduced_solver
not_evaluated
```

For any species used as a successful Phase 1 claim:

```text
median_abs_log10_error <= 0.50
mae_log10 <= 0.75
```

If a species fails:

- mark `passes = false`;
- mark `claim_allowed = false`;
- include `failure_reason`;
- do not show it as a successful main-text figure result.

For CO2 molecular liquid, CO3^2-, H3O+, and OH-:

- treat as trace/diagnostic unless directly supported and residuals pass.

### Task 7 — Add Phase 1 claim boundary

Create:

```text
analyses/phase1_smith_missen_baseline/results/phase1_claim_boundary.md
```

It must explicitly state:

- what Phase 1 can claim;
- what Phase 1 cannot claim;
- which species/properties failed residual gates;
- whether Phase 1 status is:
  - `validated`,
  - `model_ran_but_failed_validation`,
  - `retained_baseline_audit`,
  - `scaffold_ready`, or
  - `bounded_incomplete`.

If residuals fail, use:

```text
model_ran_but_failed_validation
```

or:

```text
retained_baseline_audit
```

Do not use:

```text
validated
```

### Task 8 — Relabel failed Phase 1 figures

If the current speciation figure includes failed species, rename it to:

```text
phase1_speciation_vs_loading_diagnostic.png
phase1_speciation_vs_loading_diagnostic.svg
phase1_speciation_vs_loading_diagnostic.mpl.yaml
```

or remove failed species from the main figure and keep them in a diagnostic supplement.

A figure containing failed species must not be named as if it supports successful Phase 1 speciation.

### Task 9 — Add Phase 2 bounded-incomplete report

Create:

```text
analyses/phase2_activity_epcsaft/results/phase2_bounded_incomplete_report.md
```

It must say:

```text
Phase 2 is not complete.
Phase 2 is scaffold/problem-definition ready only.
Activity-coupled equilibrium rows, pressure/speciation parity, and metrics are blocked by upstream ePC-SAFT issue #115.
No Phase 2 activity-based VLE/speciation claim is allowed yet.
```

It must list missing required outputs:

```text
phase2_equilibrium_results.csv
phase2_pressure_speciation_parity.csv
phase2_pressure_metrics.csv
phase2_speciation_metrics.csv
phase2_solver_diagnostics.csv
phase2_residual_acceptance_audit.csv
```

### Task 10 — Add Phase 2 reaction-constant source verification

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
verified_against_source
conversion_performed
conversion_notes
used_in_phase2
status
notes
```

Rules:

- If `source_file_repo_relative` is missing, status must be `source_pending`.
- If the source path is outside this repo, status must be `source_pending`.
- Do not use `promoted_reference_state_verified` unless the source table is repo-local and tests verify the values.
- If upstream solver support is missing, `used_in_phase2` must be `not_yet_solver_blocked`, not `fixed_input_complete`.

### Task 11 — Clean up Phase 2 readiness language

In all Phase 2 docs/manifests/results:

Replace ambiguous:

```text
ready
promoted_reference_state_verified
generated
```

with more precise status where needed:

```text
source_verified_but_solver_blocked
problem_definition_generated
scaffold_ready_blocked_by_epcsaft_issue_115
source_pending
```

Use `ready` only if the actual numerical output exists and passed validation.

### Task 12 — Split charge from material balances in Phase 2 problem JSON

In:

```text
phase2_activity_speciation_problem.json
```

do not put charge/electroneutrality under `balances` with carbon and amine material balances.

Use a structure like:

```json
"material_balances": {
  "total_amine": {...},
  "total_carbon": {...}
},
"constraints": {
  "electroneutrality": {...}
}
```

Regenerate processed and results JSON.

### Task 13 — Add Phase 2 completion guards

Add tests that verify:

- `phase2_equilibrium_results.csv` does not exist while issue #115 is blocking;
- if it does exist, `phase2_solver_diagnostics.csv` must exist;
- solver diagnostics must pass:
  - `reaction_residual_norm <= 1e-7`
  - `charge_residual_norm <= 1e-9`
  - `material_residual_norm <= 1e-9`
  - `fugacity_residual_norm <= 1e-7`
  - `converged == true`
- Phase 2 docs do not claim completion unless those files exist and pass.

### Task 14 — Add forbidden claim checks

Add tests that scan Phase 1/2 docs/manuscript sections for forbidden wording before Phase 3:

```text
final globally optimized
final coupled regression
predictive final parameter set
newly regressed final parameter set
Phase 2 complete
Phase 1 complete
```

Allowed only if the relevant `phase*_claim_boundary.md` says `validated`.

### Task 15 — Add issue #4/#5 acceptance status file

Create:

```text
docs/roadmaps/issues_4_5_acceptance_status.md
```

It must contain a table:

```text
issue
criterion
status
evidence_file
blocker
next_action
```

Use these statuses:

```text
pass
fail
blocked
not_started
not_applicable
```

Do not use vague statuses like `ready`.

### Task 16 — Update PR #7 body

Update the PR body to say:

```text
Status: draft / bounded-incomplete scaffold repair
```

It must explicitly list:

- Phase 1 status;
- Phase 2 status;
- failed residual gates;
- blocked Phase 2 outputs;
- upstream issue #115;
- local-path cleanup status;
- tests run.

Do not use “complete” unless all hard gates pass.

## Required validation commands

Run:

```powershell
uv run python analyses\phase1_smith_missen_baseline\scripts\generate_data.py
uv run python analyses\phase1_smith_missen_baseline\scripts\render_figures.py
uv run python analyses\phase2_activity_epcsaft\scripts\generate_data.py
uv run python -m unittest tests.test_phase2_activity_scaffold tests.test_analysis_workflow_architecture -v
uv run python scripts\validate_project.py quick
```

Also run the new no-local-path test.

If any command fails, keep PR draft and report the failure.

## Required final response from the agent

At the end, report:

```text
1. Files changed.
2. Whether PR #7 remains draft.
3. Phase 1 status.
4. Phase 2 status.
5. Residual gates passed/failed.
6. Local-path scan result.
7. Reaction-constant verification result.
8. Source verification status.
9. Tests run and results.
10. Blockers that remain.
```

## Success definition for this repair PR

This repair PR is successful if it prevents false completion.

It does not need to make Phase 1 or Phase 2 validated.

It does need to make it impossible for a future agent or manuscript writer to confuse:

```text
scaffold generated
```

with:

```text
scientific phase complete
```
