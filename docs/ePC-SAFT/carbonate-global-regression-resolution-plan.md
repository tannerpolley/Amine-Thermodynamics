# Carbonate Born Identifiability and Coupled Regression Resolution Plan

Date: 2026-05-11

## Purpose

This plan resolves two linked blockers in the MEA ePC-SAFT manuscript workflow:

1. The promoted carbonate Born pair remains regularized at `HCO3- d_born = 3.0` and `CO3^2- d_born = 3.0`, but an unanchored trace-only diagnostic found a lower residual near `HCO3- d_born = 6.80294` and `CO3^2- d_born = 2.99744`.
2. The full coupled all-row pressure/speciation least-squares objective remains runtime-bounded, so carbonate Born identifiability cannot yet be resolved in the same objective that supports the final pressure and speciation claims.

The target outcome is a defensible promoted parameter decision for carbonate-family Born diameters and a completed or explicitly bounded coupled pressure/speciation regression workflow that is fast enough to rerun, test, and document.

## Recommendation on ePC-SAFT Checkout Strategy

Do not clone or vendor a separate copy of `ePC-SAFT` inside `C:\Users\Tanner\Documents\git\MEA-Thermodynamics`.

Use the sibling package checkout:

```powershell
C:\Users\Tanner\Documents\git\ePC-SAFT
```

If isolation is needed, create a branch or git worktree owned by the ePC-SAFT repo, not inside MEA:

```powershell
cd C:\Users\Tanner\Documents\git\ePC-SAFT
git switch -c codex/mea-coupled-objective-runtime
```

or, if parallel agents need separate working directories:

```powershell
cd C:\Users\Tanner\Documents\git\ePC-SAFT
git worktree add .worktrees\mea-coupled-objective -b codex/mea-coupled-objective-runtime
```

Then reinstall that package into the MEA environment:

```powershell
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics
uv pip install --python .venv\Scripts\python.exe --reinstall --no-deps C:\Users\Tanner\Documents\git\ePC-SAFT
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

The current all-row coupled objective is too expensive for routine least-squares. The present global regression artifact is intentionally `bounded_incomplete`.

## Completion Criteria

The issue is solved only when all criteria below are met.

### Package Runtime Criteria

- A coupled pressure/speciation objective evaluation is fast enough to run tens to hundreds of least-squares evaluations in a normal local development session.
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
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics
.venv\Scripts\python.exe -c "import epcsaft; print(epcsaft.__version__); print(epcsaft.__file__)"
.venv\Scripts\python.exe -m unittest discover tests -v
.venv\Scripts\python.exe scripts\validate_project.py quick
```

Checks:

- Tests pass.
- Quick validation passes.
- `analyses/epcsaft_ionic_regression/results/global_regression/global_regression_summary.json` still documents `bounded_incomplete`.
- `analyses/epcsaft_ionic_regression/results/trace_carbonate_born_regression/trace_carbonate_born_fit_summary.json` still contains the `6.80294 / 2.99744` unanchored diagnostic.

Deliverable:

- A short baseline note in `docs/ePC-SAFT/full-ionic-parameter-manuscript-completion-audit.md` or a goal receipt describing the current exact package commit and metrics.

### Phase 2: Open or Link an Upstream ePC-SAFT Issue

Purpose: Track package-side work where it belongs.

Suggested issue title:

```text
Improve coupled MEA pressure/speciation objective runtime and diagnostics for carbonate Born identifiability
```

Suggested issue body:

```markdown
## Problem

The downstream MEA-Thermodynamics workflow needs a full coupled pressure/speciation least-squares fit with active carbonate Born parameters. The current objective can evaluate pressure/speciation artifacts, but all-row coupled least-squares remains too expensive for routine optimization, so the downstream manuscript must treat carbonate Born movement as an identifiability warning rather than a promoted global-fit result.

## Current downstream evidence

- Promoted regularized carbonate pair: `HCO3- d_born = 3.0`, `CO3^2- d_born = 3.0`.
- Unanchored trace-carbonate diagnostic: `HCO3- d_born ≈ 6.80294`, `CO3^2- d_born ≈ 2.99744`.
- Trace-only residual norm improves from approximately `0.702107` to `0.682871`.
- Full pressure/speciation global artifact remains `bounded_incomplete` because repeated reactive bubble-pressure and activity-speciation evaluations are too slow.

## Needed package improvements

- Structured timing diagnostics for reactive bubble pressure and activity/fugacity/speciation calls.
- Deterministic failure/penalty return path for optimizer objectives.
- Reuse/caching hooks for repeated objective evaluations at shared state points.
- Batch or vectorized evaluation helpers where practical.
- Optional warm-start/state continuation hooks for repeated parameter perturbations.
- Minimal profiling benchmark that can be run from downstream MEA to prove improvement.

## Acceptance criteria

- Downstream MEA can run a coupled objective with active `MEAH+`, `MEACOO-`, `HCO3-`, `CO3^2-`, and key `k_ij` variables for tens to hundreds of evaluations without timing out.
- Objective diagnostics report per-row success/failure and timing.
- The downstream workflow can decide whether the unanchored bicarbonate Born movement is promotable under pressure/speciation tradeoff gates.
```

### Phase 3: Add Package-Side Profiling and Diagnostics

Repository:

```powershell
C:\Users\Tanner\Documents\git\ePC-SAFT
```

Tasks:

- Add timing instrumentation around the functions used by MEA for:
  - reactive speciation solve
  - activity coefficient / fugacity calls
  - bubble-pressure solve
  - residual assembly
- Add a small benchmark entrypoint or test fixture that evaluates representative MEA rows.
- Add structured return diagnostics rather than relying on log text.
- Ensure diagnostics can be disabled during normal package use.

Acceptance checks:

```powershell
cd C:\Users\Tanner\Documents\git\ePC-SAFT
uv run python -m pytest
```

If the package does not use pytest for the relevant tests, run the established ePC-SAFT validation command instead.

### Phase 4: Optimize the Coupled Objective Evaluation

Package-side improvements to investigate:

- Cache pure-component parameters and invariant species metadata outside row loops.
- Cache composition-to-state preprocessing when only parameter perturbations change.
- Add optional warm starts for repeated bubble/speciation solves.
- Avoid recomputing activity coefficients more than necessary inside one residual evaluation.
- Add row-level timeout or iteration caps that return penalized residuals.
- Support a reduced objective mode that uses the same code path as full mode but a deterministic row subset.

MEA-side improvements to investigate:

- Split objective construction from objective evaluation.
- Persist exact row payloads used by optimization in `analyses/epcsaft_ionic_regression/data/processed/`.
- Add `--row-limit`, `--source-filter`, `--max-nfev`, `--profile`, and `--objective-variant` CLI flags.
- Save each optimization attempt under `analyses/epcsaft_ionic_regression/results/runs/`, then promote only curated summaries/figures into `results/<plot_set>/`.

Acceptance checks:

- A 5-evaluation smoke optimization completes quickly.
- A 40-evaluation bounded optimization completes without manual interruption.
- Runtime report identifies dominant cost and failure rows.

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
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics
uv pip install --python .venv\Scripts\python.exe --reinstall --no-deps C:\Users\Tanner\Documents\git\ePC-SAFT
.venv\Scripts\python.exe analyses\epcsaft_ionic_regression\scripts\fit_global_pressure_speciation.py --max-nfev 40 --promote
.venv\Scripts\python.exe analyses\epcsaft_ionic_regression\scripts\evaluate_train_validation_split.py
.venv\Scripts\python.exe analyses\epcsaft_ionic_regression\scripts\compute_parameter_sensitivity.py
.venv\Scripts\python.exe analyses\epcsaft_ionic_regression\scripts\render_figures.py
.venv\Scripts\python.exe -m unittest discover tests -v
.venv\Scripts\python.exe scripts\validate_project.py quick
```

Expected artifact updates:

- `analyses/epcsaft_ionic_regression/results/global_regression/`
- `analyses/epcsaft_ionic_regression/results/train_validation/`
- `analyses/epcsaft_ionic_regression/results/sensitivity/`
- `analyses/epcsaft_ionic_regression/results/trace_carbonate_born_regression/`
- `analyses/epcsaft_ionic_regression/results/pressure/`
- `analyses/epcsaft_ionic_regression/results/speciation/`
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
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics
.venv\Scripts\python.exe -m unittest discover tests -v
.venv\Scripts\python.exe scripts\validate_project.py quick

cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics\docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Additional checks:

- No `__pycache__` folders under `src`, `tests`, `scripts`, or `analyses`.
- No `docs/latex/main.pdf`; canonical PDF remains `docs/latex/builds/main.pdf`.
- All `\includegraphics{figures/...}` targets exist.
- Submission-safety scan has no `Codex`, `agent`, `worktree`, `handoff`, local path, or internal workflow language in rendered manuscript sources.
- Goal or handoff state documents clearly report whether the coupled objective completed or remains bounded.

## Proposed Upstream Issue

This plan supports opening an ePC-SAFT issue because the blocker is primarily package-side runtime/diagnostics, not just downstream MEA scripting.

Posted issue:

- https://github.com/tannerpolley/ePC-SAFT/issues/52

Recommended action:

```powershell
cd C:\Users\Tanner\Documents\git\ePC-SAFT
gh issue create --title "Improve coupled MEA pressure/speciation objective runtime and diagnostics for carbonate Born identifiability" --body-file <issue-body-file>
```

Post the issue before package implementation begins so the acceptance criteria are recorded at the package source of truth.

## Grill-Me Decision Tree

These are the decisions that should be resolved before implementation.

1. Should the next work happen as a package-first branch in `ePC-SAFT`, or as downstream-only MEA script optimization?
   - Recommended answer: package-first, because the current blocker is repeated thermodynamic objective runtime and diagnostics.
2. Should ePC-SAFT be cloned into MEA for local edits?
   - Recommended answer: no. Use sibling ePC-SAFT checkout or an ePC-SAFT-owned worktree.
3. Should the non-3.0 HCO3 diagnostic be promoted before full coupled regression?
   - Recommended answer: no. It is trace-only evidence.
4. Should the full all-row objective be the first optimization target?
   - Recommended answer: no. Start with a representative deterministic subset using the same code path, then scale to all rows.
5. Should pressure or speciation dominate the global objective?
   - Recommended answer: use explicit objective variants and report tradeoffs; do not hide a subjective weighting choice.
6. Should the manuscript wait for this work before submission?
   - Recommended answer: yes if the paper claims final fitted carbonate Born parameters or final global pressure-optimized parameters; no if the paper is explicitly framed as a transparent bounded validation workflow with carbonate identifiability as a limitation.
