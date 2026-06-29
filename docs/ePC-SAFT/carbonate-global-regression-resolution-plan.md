# Carbonate Born Identifiability and Coupled Regression Resolution Plan

Date: 2026-05-11

## Purpose

This plan resolves two linked blockers in the MEA ePC-SAFT manuscript workflow:

1. The promoted carbonate Born pair remains regularized at `HCO3- d_born = 3.0` and `CO3^2- d_born = 3.0`, but an unanchored trace-only diagnostic found a lower residual near `HCO3- d_born = 6.80294` and `CO3^2- d_born = 2.99744`.
2. The full coupled all-row pressure/speciation package-native candidate has not passed the promotion gate, so carbonate Born identifiability cannot yet be resolved in the same approved objective that supports the final pressure and speciation claims.

The target outcome is a defensible promoted parameter decision for carbonate-family Born diameters and a completed or explicitly bounded coupled pressure/speciation regression workflow that is fast enough to rerun, test, and document.

## Recommendation on ePC-SAFT Checkout Strategy

Do not clone or vendor a separate copy of `ePC-SAFT` inside `<repo-root>`.

Use the sibling package checkout:

```powershell
<upstream-ePC-SAFT>
```

If isolation is needed, create a branch or git worktree owned by the ePC-SAFT repo, not inside MEA:

```powershell
cd <upstream-ePC-SAFT>
git switch -c codex/mea-coupled-objective-runtime
```

or, if parallel agents need separate working directories:

```powershell
cd <upstream-ePC-SAFT>
git worktree add .worktrees\mea-coupled-objective -b codex/mea-coupled-objective-runtime
```

Then reinstall that package into the MEA environment:

```powershell
cd <repo-root>
uv pip install --python .venv\Scripts\python.exe --reinstall --no-deps <upstream-ePC-SAFT>
```

Rationale:

- MEA is the downstream scientific workflow and manuscript repo; ePC-SAFT is the upstream thermodynamics package.
- Vendoring a local copy of ePC-SAFT inside MEA would create duplicate source-of-truth problems, stale package edits, and harder Git history.
- A sibling checkout keeps package improvements publishable as ePC-SAFT issues/PRs and keeps MEA artifacts tied to a package commit.
- If rapid package editing is needed, use an ePC-SAFT branch/worktree plus explicit reinstall or editable install. Do not create a hidden in-project package fork.

## Current Evidence State

### Promoted Values

Current promoted carbonate-family values in the MEA ionic dataset:

- `HCO3-__d_born = 3.0`
- `CO3^2-__d_born = 3.0`

These remain the manuscript-promoted values because the promoted fit is regularized and the full pressure/speciation global objective has not completed.

### Diagnostic Warning

The trace-carbonate artifact reports:

- regularized fit: approximately `3.0 / 3.0`
- regularized trace residual norm: approximately `0.702107`
- best unanchored multistart diagnostic: approximately `6.80294 / 2.99744`
- unanchored trace residual norm: approximately `0.682871`

Interpretation:

- The data contain real sensitivity to bicarbonate `d_born`.
- The unanchored value is not yet promotable because it was selected only on trace carbonate residuals.
- The final decision must be made in a coupled objective that includes pressure, major amine-family speciation, carbonate speciation, and regularization/identifiability diagnostics.

### Runtime Blocker

The current all-row coupled package-native objective has not produced an approved full-fit result. The present global regression artifact is intentionally `package_fit_not_completed`, which means promotion is blocked by package-fit status rather than accepted as a scientific optimum.

## Completion Criteria

The issue is solved only when all criteria below are met.

### Package Runtime Criteria

- A coupled pressure/speciation package-native candidate is fast enough to run normal local development smoke and candidate fits.
- Objective evaluation produces structured timing diagnostics by pressure rows, speciation rows, bubble-pressure calls, activity/fugacity calls, and failures.
- Repeated evaluations avoid redundant work where state, composition, temperature, pressure, and parameter set are unchanged or differ only in finite-difference perturbations.
- Failure handling is deterministic and returns penalized residuals with diagnostics rather than hanging or silently dropping rows.

### Regression Criteria

- A full coupled fit can be attempted with active variables that include at minimum:
  - `MEAH+__s`
  - `MEAH+__e`
  - `MEAH+__d_born`
  - `MEACOO-__s`
  - `MEACOO-__e`
  - `MEACOO-__d_born`
  - `HCO3-__d_born`
  - `CO3^2-__d_born`
  - `k_ij__CO2__MEA`
  - `k_ij__MEA__H2O`
  - `k_ij__MEAH+__MEACOO-`
  - `k_ij__MEAH+__HCO3-`
- At least three objective variants are run:
  - regularized global objective with carbonate Born values initialized at `3.0 / 3.0`
  - regularized global objective initialized at `6.80294 / 2.99744`
  - unregularized or weakly regularized sensitivity objective to test whether carbonate movement is data-driven or penalty-driven
- Each run records:
  - optimizer success/status/message
  - initial and final cost
  - initial and final pressure metrics
  - initial and final species metrics
  - parameter values and active bounds
  - wall-time and evaluation counts
  - train/validation metrics
  - carbonate-specific residual improvement
  - pressure/speciation tradeoff plots

### Carbonate Promotion Criteria

Promote a non-3.0 bicarbonate or carbonate Born value only if all are true:

- The coupled objective improves meaningfully, not only the trace-carbonate residual.
- Pressure metrics do not degrade beyond a predeclared tolerance.
- `MEAH+` and `MEACOO-` speciation metrics do not degrade beyond a predeclared tolerance.
- The selected carbonate values are not bound artifacts.
- The selected carbonate values are stable across at least two initializations or regularization settings.
- Train/validation behavior supports the movement rather than showing overfit to one source.

If these gates fail, keep `3.0 / 3.0` promoted and report the unanchored result as an identifiability warning.

### Manuscript Criteria

- The manuscript states the final carbonate decision without overclaiming.
- The manuscript includes a table or appendix row with:
  - promoted carbonate values
  - unanchored diagnostic values
  - global objective decision
  - reason for promoting or rejecting the alternative
- Figures include:
  - full pressure parity
  - full speciation parity
  - pressure residuals by source/loading
  - speciation residuals by species
  - carbonate Born diagnostic plot
  - train/validation residual plot
  - sensitivity or identifiability plot
- `docs/latex/builds/main.pdf` builds with no missing figures or citation errors.

## Work Breakdown

### Phase 1: Freeze Current Downstream Baseline

Purpose: Make the current state reproducible before package changes.

Commands:

```powershell
cd <repo-root>
.venv\Scripts\python.exe -c "import epcsaft; print(epcsaft.__version__); print(epcsaft.__file__)"
.venv\Scripts\python.exe -m unittest discover tests -v
.venv\Scripts\python.exe scripts\validate_project.py quick
```

Checks:

- Tests pass.
- Quick validation passes.
- `analyses/phase3/ionic_epcsaft_regression/results/global_regression/global_regression_summary.json` documents `package_fit_not_completed`.
- `analyses/phase3/ionic_epcsaft_regression/results/trace_carbonate_born_regression/trace_carbonate_born_fit_summary.json` still contains the `6.80294 / 2.99744` unanchored diagnostic.

Deliverable:

- A short baseline note in `docs/ePC-SAFT/full-ionic-parameter-manuscript-completion-audit.md` or a goal receipt describing the current exact package commit and metrics.

### Phase 2: Link MEA-Thermodynamics Issue #3

Purpose: Track this work in the MEA-Thermodynamics project, where the implementation scope belongs.

Correct GitHub issue:

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/3

The mistakenly opened upstream issue was closed:

- https://github.com/tannerpolley/ePC-SAFT/issues/52

Issue #3 requires MEA-Thermodynamics to become the data, target-construction, artifact, validation, and manuscript evidence repo. MEA should not own production optimization loops with SciPy. MEA should build native regression problems, call the ePC-SAFT native regression API, consume structured package fit results, and run approval/promotion checks.

### Phase 3: Remove MEA Production Optimizer Ownership

Purpose: eliminate local SciPy optimizer ownership from MEA production fitting.

Tasks:

- Refactor `src/MEA/epcsaft_ionic/regress_parameters.py` so production regression no longer imports or calls:
  - `scipy.optimize.least_squares`
  - `scipy.optimize.minimize`
  - `scipy.optimize.differential_evolution`
- Keep MEA-owned responsibilities:
  - load and reconcile VLE/speciation data
  - build target rows
  - define parameter specs, bounds, scales, and provenance
  - define train/validation splits
  - call the ePC-SAFT native regression API
  - write downstream artifacts and manuscript tables
- Move legacy SciPy diagnostic code, if still useful, behind an explicitly non-production diagnostic path or remove it.

Acceptance checks:

```powershell
cd <repo-root>
.venv\Scripts\python.exe -m unittest tests.test_epcsaft_ionic_native_regression -v
```

### Phase 4: Build Native Regression Problem in MEA

Purpose: translate MEA data and scientific fit windows into a structured native regression problem owned by the downstream project.

Required MEA functions:

```python
build_pressure_target_rows(...)
build_speciation_target_rows(...)
build_parameter_specs(...)
build_regularization_terms(...)
build_native_regression_problem(...)
```

Each target row must preserve:

- `row_id`
- `T`
- `P` or `P_seed`
- `loading`
- `initial_x`
- apparent totals
- reaction definitions
- volatile and nonvolatile species mapping
- target values
- source
- train/validation split
- metadata needed for audit and manuscript tables

The native regression problem must preserve advanced SSM+DS/Born options rather than silently falling back to a numerical derivative fitting path.

Acceptance checks:

- MEA can build and serialize `native_regression_problem.json` without running an optimizer.
- Source labels and split assignments are preserved.
- Target names are stable and traceable to original data.
- The species basis remains `CO2`, `MEA`, `H2O`, `MEAH+`, `MEACOO-`, `HCO3-`, `CO3^2-`, `H3O+`, and `OH-`.

### Phase 4B: Consume Native Package Fit Results

Purpose: make package results the source of truth for convergence, residuals, bounds, and promotion eligibility.

MEA should consume package result fields such as:

- `fit.status`
- `fit.success`
- `fit.message`
- `fit.objective_initial`
- `fit.objective_final`
- `fit.residuals`
- `fit.residual_names`
- `fit.row_results`
- `fit.metrics`
- `fit.active_bounds`
- `fit.parameter_map`
- `fit.timing`

Acceptance checks:

- MEA no longer computes residual vectors for optimizer use.
- MEA can still compute independent reporting metrics after a package fit.
- Nonconverged package statuses are written as specific statuses, not vague `package_fit_not_completed` language.
- Curated artifacts update only with explicit `--promote` and a passing approval check.

Current MEA implementation checkpoint on 2026-05-11:

- `src/MEA/epcsaft_ionic/regress_parameters.py` delegates production fitting to `epcsaft.fit_reactive_electrolyte_parameters`.
- `src/MEA/epcsaft_ionic/global_regression.py` no longer owns a SciPy optimizer loop for the pressure/speciation production path.
- `src/MEA/epcsaft_ionic/approval_check.py` blocks curated promotion unless the package-native fit is completed, selected as the global parameter set, reports zero row failures, avoids active bounds, and has coupled pressure/speciation evidence for any non-3.0 carbonate Born movement.
- A promoted run of `analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py --max-nfev 40 --promote` was rejected by the approval gate and written only as a run candidate under `analyses/phase3/ionic_epcsaft_regression/results/runs/global_regression/smoke/`. The rejection reasons were `completion_status_not_completed`, `selected_parameter_set_not_global_regression`, `native_fit_success_not_true`, and `native_row_failure_count_missing`.
- Because the approval gate failed, curated global artifacts and manuscript claims should remain at the regularized `3.0 / 3.0` carbonate Born pair with the `6.80294 / 2.99744` trace-only result treated as an identifiability warning.

### Phase 5: Run Designed Carbonate Identifiability Experiments

Run a controlled experiment matrix:

| Run | Initial carbonate values | Regularization | Purpose |
| --- | --- | --- | --- |
| A | `3.0 / 3.0` | current | baseline promoted path |
| B | `6.80294 / 2.99744` | current | test if diagnostic survives global objective |
| C | `3.0 / 3.0` | weak | test penalty sensitivity |
| D | `6.80294 / 2.99744` | weak | test alternative stability |
| E | multiple seeds | weak/none | identify local minima and bound artifacts |

Minimum reported metrics:

- pressure median absolute log10 residual
- pressure RMSE log10 residual
- pressure max absolute log10 residual
- `MEAH+` median/RMSE log10 residual
- `MEACOO-` median/RMSE log10 residual
- `HCO3-` median/RMSE log10 residual
- `CO3^2-` median/RMSE log10 residual
- train/validation pressure metrics
- train/validation speciation metrics
- final parameter table
- active-bound flags
- wall-time/evaluation count

### Phase 6: Decide Carbonate Promotion

Decision rule:

- Promote the non-3.0 HCO3 value only if it improves the coupled objective without materially degrading pressure or amine-family speciation.
- Keep `3.0 / 3.0` if the alternative only improves carbonate trace residuals, destabilizes pressure, worsens `MEAH+`/`MEACOO-`, depends strongly on initialization, or lands near a bound.

Required output:

```text
decision: promote_alternative | keep_regularized_3_0_pair
reason:
pressure_delta:
amine_speciation_delta:
carbonate_speciation_delta:
train_validation_delta:
bound_status:
runtime_status:
```

### Phase 7: Refresh MEA Artifacts

Commands:

```powershell
cd <repo-root>
uv pip install --python .venv\Scripts\python.exe --reinstall --no-deps <upstream-ePC-SAFT>
.venv\Scripts\python.exe analyses\phase3\ionic_epcsaft_regression\scripts\fit_global_pressure_speciation.py --max-nfev 40 --promote
.venv\Scripts\python.exe analyses\phase3\ionic_epcsaft_regression\scripts\evaluate_train_validation_split.py
.venv\Scripts\python.exe analyses\phase3\ionic_epcsaft_regression\scripts\compute_parameter_sensitivity.py
.venv\Scripts\python.exe analyses\phase3\ionic_epcsaft_regression\scripts\render_figures.py
.venv\Scripts\python.exe -m unittest discover tests -v
.venv\Scripts\python.exe scripts\validate_project.py quick
```

Expected artifact updates:

- `analyses/phase3/ionic_epcsaft_regression/results/global_regression/`
- `analyses/phase3/ionic_epcsaft_regression/results/train_validation/`
- `analyses/phase3/ionic_epcsaft_regression/results/sensitivity/`
- `analyses/phase3/ionic_epcsaft_regression/results/trace_carbonate_born_regression/`
- `analyses/phase3/ionic_epcsaft_regression/results/pressure/`
- `analyses/phase3/ionic_epcsaft_regression/results/speciation/`
- `docs/latex/figures/`

### Phase 8: Update Manuscript and Audit Documents

If non-3.0 HCO3 is promoted:

- Update parameter tables with the new promoted value.
- Explain why the coupled objective supports promotion.
- Add pressure/speciation tradeoff evidence to avoid trace-only overclaiming.

If `3.0 / 3.0` remains promoted:

- Keep current promoted table values.
- State that coupled evidence does not justify promotion of the unanchored diagnostic.
- Keep the diagnostic as an identifiability limitation and future-work boundary.

Files to update:

- `docs/latex/sections/mea_system_modeling_results.tex`
- `docs/latex/sections/conclusion.tex`
- `docs/latex/tables/full_ionic_ssm_ds_parameters.tex`
- `docs/latex/tables/parameter_evidence_matrix.tex`
- `docs/latex/source_log.md`
- `docs/ePC-SAFT/full-component-parameter-source-audit.md`
- `docs/ePC-SAFT/full-ionic-parameter-manuscript-completion-audit.md`
- `docs/.codex-journal/project_memory.md`

Do not manually edit:

- `docs/latex/references.bib`

### Phase 9: Final Validation

Commands:

```powershell
cd <repo-root>
.venv\Scripts\python.exe -m unittest discover tests -v
.venv\Scripts\python.exe scripts\validate_project.py quick

cd <repo-root>\docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Additional checks:

- No `__pycache__` folders under `src`, `tests`, `scripts`, or `analyses`.
- No `docs/latex/main.pdf`; canonical PDF remains `docs/latex/builds/main.pdf`.
- All `\includegraphics{figures/...}` targets exist.
- Submission-safety scan has no `Codex`, `agent`, `worktree`, `handoff`, local path, or internal workflow language in rendered manuscript sources.
- Goal or handoff state documents clearly report whether the coupled objective completed or remains bounded.

## GitHub Issue

This plan is tracked in the MEA-Thermodynamics project because the implementation scope is downstream MEA target construction, native regression delegation, package-result consumption, artifact promotion, and manuscript validation.

Correct issue:

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/3

Misplaced issue closed:

- https://github.com/tannerpolley/ePC-SAFT/issues/52

Do not reopen the ePC-SAFT issue unless Scout/Judge evidence during implementation proves the package API itself is missing required native regression capability.

Recommended action for this repo:

```powershell
cd <repo-root>
/goal Follow docs/goals/issue-3-native-regression-carbonate/goal.md.
```

## Grill-Me Decision Tree

These are the decisions that should be resolved before implementation.

1. Should the next work happen in `MEA-Thermodynamics`, or as package-first work in `ePC-SAFT`?
   - Recommended answer: MEA-Thermodynamics first, because issue #3 is about MEA target construction, native regression delegation, artifact promotion, and manuscript evidence. Escalate to ePC-SAFT only if the required native API is absent or broken.
2. Should ePC-SAFT be cloned into MEA for local edits?
   - Recommended answer: no. Use the sibling ePC-SAFT checkout as the package dependency; do not vendor a hidden package fork inside MEA.
3. Should the non-3.0 HCO3 diagnostic be promoted before full coupled regression?
   - Recommended answer: no. It is trace-only evidence.
4. Should the full all-row objective be the first optimization target?
   - Recommended answer: no. Start with a representative deterministic subset using the same code path, then scale to all rows.
5. Should pressure or speciation dominate the global objective?
   - Recommended answer: use explicit objective variants and report tradeoffs; do not hide a subjective weighting choice.
6. Should the manuscript wait for this work before submission?
   - Recommended answer: yes if the paper claims final fitted carbonate Born parameters or final global pressure-optimized parameters; no if the paper is explicitly framed as a transparent bounded validation workflow with carbonate identifiability as a limitation.




