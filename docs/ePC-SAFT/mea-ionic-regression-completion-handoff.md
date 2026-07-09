# MEA Ionic ePC-SAFT Regression Completion Handoff

> **For agentic workers:** REQUIRED SUB-SKILL: Use `chemical-engineer` for thermodynamic/regression judgment. Use `coordination` when handing findings to the upstream ePC-SAFT package agent. Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` if implementing the MEA-side tasks from this document.

**Goal:** Finish the full ionic MEA-CO2-H2O ePC-SAFT regression workflow so the manuscript can honestly claim a package-backed reactive electrolyte VLE/speciation calculation with fitted MEA-system parameters.
uv run python - <<'PY'
**Architecture:** MEA-Thermodynamics is the downstream consumer and evidence repo. `<upstream-ePC-SAFT>` is the upstream package repo that owns reusable solver, regression, and diagnostics capabilities. The MEA repo should keep domain data, target construction, artifacts, manuscript text, and acceptance checks; the ePC-SAFT package should own generic reactive-electrolyte equilibrium, sweeps, regression terms, and fast/robust solver internals.
uv run python - <<'PY'
**Tech Stack:** Bash, `uv`, Python 3.13, local `epcsaft` package, SciPy least squares, Matplotlib artifacts, LaTeX manuscript mirror.
uv run python - <<'PY'
---
uv run python - <<'PY'
## Repos And Roles
uv run python - <<'PY'
Run downstream commands from:
uv run python - <<'PY'
```bash
cd <repo-root>
```
uv run python - <<'PY'
Use this upstream package path for package fixes:
uv run python - <<'PY'
```bash
cd <upstream-ePC-SAFT>
```
uv run python - <<'PY'
Current downstream workflow:

```text
source/reference data
  -> true-species target construction
  -> ePC-SAFT reactive speciation
  -> ePC-SAFT electrolyte bubble pressure
  -> CO2 partial pressure residuals
  -> speciation/activity residuals
  -> fitted dataset and curated plot artifacts
  -> manuscript figures and claims
```

True-species vector:

```text
CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, OH-
```

Advanced Born/electrostatic options currently used by the MEA workflow:

```python
{
    "elec_model": {
        "rel_perm": {"rule": "empirical", "differential_mode": "numerical"},
        "born_model": {
            "d_Born_mode": 3,
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "mu_born_model": {
                "differential_mode": "numerical",
                "comp_dep_delta_d": True,
            },
        },
    },
}
```

## Current Snapshot

The package API surface is now present in the downstream environment:

```text
epcsaft version: 1.5.0
epcsaft package path: <repo-root>/.venv/Lib/site-packages/epcsaft/__init__.py
ReactiveSpeciationOptions: present
ReactiveElectrolyteBubbleOptions: present
solve_reactive_speciation: present
solve_reactive_electrolyte_bubble: present
solve_reactive_electrolyte_bubble_sweep: present
epcsaft.regression.fit_mea_co2_h2o_electrolyte: present
```

Important caveat: the public `fit_mea_co2_h2o_electrolyte(...)` docstring still describes a pure-parameter benchmark helper. The MEA paper goal needs a coupled target against the final reactive-electrolyte vapor partial-pressure path, not only isolated pure-component benchmark terms.

Current saved parameter regression summary:

```text
file: analyses/phase3/ionic_epcsaft_regression/results/parameter_regression/ionic_parameter_regression_summary.json
target_counts: vle=3, speciation=3
optimizer.success: false
optimizer.message: The maximum number of function evaluations is exceeded.
optimizer.nfev: 1
initial_residual_norm: 1.1240674719241737
final_residual_norm: 1.1240674719241737
final_metrics.vle_median_abs_log10_error: 0.3797569935680999
final_metrics.failure_count: 0
```

This is a smoke/seed artifact, not a completed regression.

Current saved full-grid evaluation summary built from the current parameter CSV:

```text
file: analyses/phase3/ionic_epcsaft_regression/results/summary/ionic_evaluation_summary.json
pressure_success_count: 161
pressure_count: 161
raw_pressure_median_abs_log10_error: 0.36235971627584945
raw_pressure_max_abs_log10_error: 0.9726416719891973
speciation_success_count: 74
speciation_count: 74
reaction median abs ln residuals: about 1e-8 to 1e-7
large speciation median abs log10 errors remain for CO2, H3O+, and OH-
```

Interpretation:

```text
The current package-backed pressure/speciation solve is runnable across the current grid.
The pressure result is close to the proposed approval gate but misses the median threshold.
The parameter regression itself is not complete because the saved optimizer result is a tiny failed smoke run.
The final paper claim still requires a real optimization, acceptance check, and updated manuscript language.
```

Prior long-run warning from this project session:

```text
uv run python -m MEA.epcsaft_ionic.regress_parameters --max-vle-records 6 --max-speciation-records 6 --max-nfev 12 --verbose
```

This was interrupted after roughly 904 seconds in a previous run. Re-check current package performance before assuming that timeout still holds, but treat regression runtime as the main operational risk.

## Files That Matter

Downstream MEA files:

```text
src/MEA/epcsaft_ionic/model.py
src/MEA/epcsaft_ionic/regress_parameters.py
src/MEA/epcsaft_ionic/plot_results.py
tests/test_epcsaft_ionic.py
analyses/phase3/ionic_epcsaft_regression/scripts/generate_data.py
analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py
analyses/phase3/ionic_epcsaft_regression/epcsaft_ionic_package_feedback.md
analyses/phase3/ionic_epcsaft_regression/epcsaft_reactive_electrolyte_issue_body.md
scripts/validate_project.py
docs/latex/main.tex
docs/latex/references.bib
```

Downstream outputs to inspect:

```text
data/reference/MEA/ion_parameter_regression_sources.csv
data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/pure/any_solvent.csv
data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/mixed/binary_interaction/k_ij.csv
analyses/phase3/ionic_epcsaft_regression/results/parameter_regression/ionic_parameter_regression_summary.json
analyses/phase3/ionic_epcsaft_regression/results/parameter_regression/ionic_parameter_regression_values.csv
analyses/phase3/ionic_epcsaft_regression/results/pressure/ionic_pressure_comparison.csv
analyses/phase3/ionic_epcsaft_regression/results/pressure/ionic_epcsaft_co2_pressure.png
analyses/phase3/ionic_epcsaft_regression/results/pressure/ionic_epcsaft_co2_pressure.svg
analyses/phase3/ionic_epcsaft_regression/results/speciation/ionic_speciation_activity_residuals.csv
analyses/phase3/ionic_epcsaft_regression/results/speciation/ionic_speciation_plot_data.csv
analyses/phase3/ionic_epcsaft_regression/results/speciation/ionic_epcsaft_speciation_activity.png
analyses/phase3/ionic_epcsaft_regression/results/speciation/ionic_epcsaft_speciation_activity.svg
analyses/phase3/ionic_epcsaft_regression/results/summary/ionic_evaluation_summary.json
```

Upstream package files to inspect first:

```text
<upstream-ePC-SAFT>/src/epcsaft/equilibrium.py
<upstream-ePC-SAFT>/src/epcsaft/regression.py
<upstream-ePC-SAFT>/src/epcsaft/bindings.cpp
<upstream-ePC-SAFT>/src/epcsaft/native/epcsaft_chemical_equilibrium.cpp
<upstream-ePC-SAFT>/src/epcsaft/native/epcsaft_equilibrium.cpp
<upstream-ePC-SAFT>/tests/api/test_reactive_speciation.py
<upstream-ePC-SAFT>/docs/pages/electrolyte_vle_reactive_workflow.rst
```

## Exact Commands To Run
uv run python - <<'PY'
### 1. Capture Downstream State
uv run python - <<'PY'
```bash
cd <repo-root>
git status --short
git rev-parse --show-toplevel HEAD --abbrev-ref HEAD
uv --version
uv run python --version
```

Check for:

```text
The branch and commit are recorded in the final report.
Uncommitted user work is not reverted.
No destructive Git commands are used.
```
uv run python - <<'PY'
### 2. Probe The Installed ePC-SAFT API
uv run python - <<'PY'
```bash
uv run python -c "import epcsaft, epcsaft.regression as r; print(epcsaft.__version__); print(epcsaft.__file__); print(hasattr(epcsaft, 'solve_reactive_electrolyte_bubble_sweep')); print(hasattr(r, 'fit_mea_co2_h2o_electrolyte'))"
```
uv run python - <<'PY'
Check for:

```text
The import succeeds.
The package path is the expected installed package in the MEA virtual environment or an intentional editable install.
The reactive electrolyte sweep API exists.
The regression helper exists, but do not assume it solves the coupled MEA target until inspected.
```
uv run python - <<'PY'
### 3. Run Cheap Structural Validation
uv run python - <<'PY'
```bash
uv run python scripts/doctor.py
uv run python -m unittest tests.test_epcsaft_ionic -v
uv run python scripts/validate_project.py quick
```

Check for:

```text
Doctor passes.
Ionic target vectors are length 9.
The ionic pressure smoke is finite and positive.
Quick validation exits 0.
```
uv run python - <<'PY'
### 4. Read Current Metrics Before Changing Anything
uv run python - <<'PY'
```bash
@'
import json
from pathlib import Path

paths = [
    Path("analyses/phase3/ionic_epcsaft_regression/results/parameter_regression/ionic_parameter_regression_summary.json"),
    Path("analyses/phase3/ionic_epcsaft_regression/results/summary/ionic_evaluation_summary.json"),
]
for path in paths:
    print(f"/n--- {path}")
    data = json.loads(path.read_text())
    if "optimizer" in data:
        print("target_counts:", data["target_counts"])
        print("optimizer:", data["optimizer"])
        print("final_metrics.vle_median_abs_log10_error:", data["final_metrics"].get("vle_median_abs_log10_error"))
        print("final_metrics.failure_count:", data["final_metrics"].get("failure_count"))
    else:
        for key in [
            "pressure_success_count",
            "pressure_count",
            "raw_pressure_median_abs_log10_error",
            "raw_pressure_max_abs_log10_error",
            "speciation_success_count",
            "speciation_count",
            "reaction_median_abs_ln_residuals",
            "speciation_median_abs_log10_model_over_target",
        ]:
            print(f"{key}:", data.get(key))
'@ | uv run python -
```

Check for:

```text
The current saved regression is not mistaken for final if optimizer.success is false.
The full-grid pressure/speciation evaluation is recorded before overwriting artifacts.
```

### 5. Run A Regression Smoke Only When You Are Ready To Overwrite Parameter Artifacts
uv run python - <<'PY'
Current script writes directly to curated parameter-regression outputs. Do not run this casually if you need to preserve the current CSV.
uv run python - <<'PY'
```bash
uv run python -m MEA.epcsaft_ionic.regress_parameters --max-vle-records 3 --max-speciation-records 3 --max-nfev 1 --verbose
```
uv run python - <<'PY'
Check for:

```text
The command exits 0 or gives a clear package-side failure.
The residual vector length stays fixed.
No point failure changes the number of residuals returned to SciPy.
The summary JSON records target counts, nfev, success, initial metrics, final metrics, and failures.
```

### 6. Run A Candidate Regression
uv run python - <<'PY'
Start smaller than full-grid but larger than smoke:
uv run python - <<'PY'
```bash
uv run python -m MEA.epcsaft_ionic.regress_parameters --max-vle-records 18 --max-speciation-records 18 --max-nfev 24 --verbose
```
uv run python - <<'PY'
If that is still slow, run this diagnostic size and report timing:
uv run python - <<'PY'
```bash
uv run python -m MEA.epcsaft_ionic.regress_parameters --max-vle-records 6 --max-speciation-records 6 --max-nfev 6 --verbose
```
uv run python - <<'PY'
Check for:

```text
Wall time per objective evaluation.
optimizer.success or clear termination reason.
final_residual_norm lower than initial_residual_norm.
vle_median_abs_log10_error lower than initial value.
failure_count remains 0 or every failure has a compact diagnostic and fixed residual penalty.
No fitted parameter silently hits a bound without being called out.
```
uv run python - <<'PY'
### 7. Regenerate Ionic Figures And Full-Grid Evaluation
uv run python - <<'PY'
```bash
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py
```
uv run python - <<'PY'
Equivalent module call:
uv run python - <<'PY'
```bash
uv run python -m MEA.epcsaft_ionic.plot_results
```
uv run python - <<'PY'
Check for:

```text
analyses/phase3/ionic_epcsaft_regression/results/pressure/ionic_pressure_comparison.csv exists.
analyses/phase3/ionic_epcsaft_regression/results/speciation/ionic_speciation_activity_residuals.csv exists.
analyses/phase3/ionic_epcsaft_regression/results/summary/ionic_evaluation_summary.json exists.
PNG, SVG, and PDF figures are regenerated.
pressure_success_count equals pressure_count.
speciation_success_count equals speciation_count.
```
uv run python - <<'PY'
### 8. Run Full Project Confidence Check
uv run python - <<'PY'
```bash
uv run python scripts/validate_project.py confidence
```
uv run python - <<'PY'
Check for:

```text
Quick validation passes.
All curated plot-set contracts pass.
The ionic pressure and speciation folders contain CSV snapshot, .mpl.yaml, PNG, SVG, and PDF.
No new canonical artifacts appear under top-level out/.
```
uv run python - <<'PY'
### 9. Build Manuscript After Final Metrics Are Ready
uv run python - <<'PY'
```bash
cd <repo-root>/docs/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Check for:

```text
The build uses references.bib, not library.bib.
No undefined citations or references.
The text does not claim a final converged regression until the acceptance gates below pass.
```
uv run python - <<'PY'
Sync to the Overleaf-connected mirror only after the source build is good:
uv run python - <<'PY'
```bash
cd <repo-root>
bash docs/latex/scripts/sync_to_overleaf_mirror.sh
```
uv run python - <<'PY'
## Acceptance Gates

Do not mark the overall scientific goal complete unless all required gates pass.

Minimum MEA-side regression gate:

```text
ionic_parameter_regression_summary.json exists.
target_counts.vle >= 18.
target_counts.speciation >= 18.
optimizer.success is true, or optimizer.message documents a scientifically acceptable convergence/termination reason.
final_residual_norm < initial_residual_norm.
final_metrics.failure_count == 0.
final_metrics.vle_median_abs_log10_error improves over initial.
```

Approval-grade full-grid evaluation gate:

```text
pressure_success_count == pressure_count == 161.
speciation_success_count == speciation_count == 74.
raw_pressure_median_abs_log10_error <= 0.30.
raw_pressure_max_abs_log10_error <= 1.0.
median absolute reaction ln residual <= 2.0 for each modeled reaction.
No calibrated pressure correction is required.
```

Parameter plausibility gate:

```text
MEA fitted m, s, e remain physically plausible and documented.
MEAH+ and MEACOO- fitted s, e, d_born remain physically plausible and documented.
HCO3- changes are justified if still fitted.
Selected k_ij values are listed and no value hits +/-2.0 without an explanation.
The fitted dataset files match the values in ionic_parameter_regression_values.csv.
```

Artifact gate:

```text
Each curated plot set contains the exact plotted CSV snapshot, .mpl.yaml sidecar, PNG, SVG, and PDF.
The pressure plot compares against Jou data with consistent temperature colors.
The speciation plot shows all modeled species that are scientifically relevant and does not hide failed species.
The manuscript figure copies are updated only from accepted plot artifacts.
```

Manuscript gate:

```text
docs/latex/main.tex builds successfully.
docs/latex/references.bib contains all cited keys.
Sections 3 and 4 describe final parameter regression, VLE/speciation coupling, and limitations without local-process language.
Claims distinguish seed/smoke artifacts from final optimized parameters.
```

## Required Fixes In The ePC-SAFT Package

### Package Fix 1: Coupled Reactive Electrolyte Regression Term

Current public helper:

```python
epcsaft.regression.fit_mea_co2_h2o_electrolyte(...)
```

Problem:

```text
The helper appears to expose the pure-parameter benchmark path, not the final MEA target path:
record -> apparent totals -> reactive speciation -> electrolyte bubble pressure -> CO2 vapor partial pressure residual.
```

Required package behavior:

```text
Allow fitting selected m, s, e, d_born, and k_ij values.
Support pressure targets for vapor partial pressure of CO2.
Support optional species-composition targets from the reactive speciation result.
Support optional reaction residual terms.
Honor user_options for Born SSM+DS and concentration-dependent dielectric behavior.
Return fixed-length residual vectors even when some records fail.
Return per-record diagnostics and timing.
```
uv run python - <<'PY'
Downstream proof command after the package fix:
uv run python - <<'PY'
```bash
cd <repo-root>
uv run python -m MEA.epcsaft_ionic.regress_parameters --max-vle-records 18 --max-speciation-records 18 --max-nfev 24 --verbose
```

### Package Fix 2: Fast Batch/Sweep Objective Evaluation

Problem:

```text
SciPy finite-difference least squares around Python-level reactive speciation and bubble-pressure calls is too slow for practical fitting.
```

Required package behavior:

```text
Batch evaluate ordered MEA records by temperature/loading.
Reuse previous x_liq, activity coefficients, pressure, and vapor composition as warm starts.
Support continuation retries from both loading directions.
Expose concise progress diagnostics for long regression runs.
Avoid expensive exception paths inside normal residual evaluation.
```

Downstream proof:

```text
The 6 VLE / 6 speciation / 6 nfev diagnostic run should finish quickly enough to be used interactively.
The 18 VLE / 18 speciation / 24 nfev candidate run should finish without manual interruption.
```

### Package Fix 3: Structured Failure Results

Problem:

```text
Regression needs fixed-shape residuals and compact best-effort diagnostics. Exceptions alone are too brittle for outer optimization loops.
```

Required package behavior:

```text
When error_mode="result", return success=False result objects instead of throwing for recoverable finite failures.
Include best_x_liq, best_P, best_y_vap, best_partial_pressures, best_objective, best_fugacity_residual_norm, reaction residuals, mass residuals, charge residual, and penalty residuals when available.
Expose diagnostics in stable names that downstream code can write directly to CSV/JSON.
```

Downstream proof:

```text
Bad or difficult points produce fixed penalty residuals and diagnostic rows in ionic_pressure_comparison.csv or the regression summary.
The residual vector length does not depend on which rows fail.
```

### Package Fix 4: Linux uv Build Reliability

Problem:

```text
The MEA repo uses Python 3.13 through uv. Package-side C++/pybind changes must be installable and importable on this machine.
```
uv run python - <<'PY'
Required package commands:
uv run python - <<'PY'
```bash
cd <upstream-ePC-SAFT>
uv sync
uv run python scripts/build_epcsaft.py
uv run python -c "import epcsaft; import epcsaft.regression; print(epcsaft.__version__)"
```

If a full rebuild is memory-heavy, the upstream agent must report the exact lower-memory build command that works on this machine.

### Package Fix 5: Upstream Tests And Benchmark

Add or update package-side tests for:

```text
Reactive speciation success on representative MEA records.
Reactive electrolyte bubble-pressure success on representative low, medium, and high CO2-pressure MEA records.
Sweep continuation preserving result order and fixed shape.
Regression helper returning finite residuals for a tiny MEA dataset.
Regression helper honoring fitted masks for pure parameters, d_born, and selected k_ij.
```

## Required Fixes In The MEA Repo

### MEA Fix 1: Add An Approval Check Module

Create:

```text
src/MEA/epcsaft_ionic/approval_check.py
```

Behavior:

```text
Read ionic_parameter_regression_summary.json.
Read ionic_evaluation_summary.json.
Fail with exit code 1 when acceptance gates are not met.
Print exact failing metric names, observed values, thresholds, and artifact paths.
Exit 0 only when regression, full-grid evaluation, and artifact gates pass.
```
uv run python - <<'PY'
Expected command:
uv run python - <<'PY'
```bash
uv run python -m MEA.epcsaft_ionic.approval_check
```
uv run python - <<'PY'
Add it to `scripts/validate_project.py confidence` only after the threshold logic is stable.

### MEA Fix 2: Separate Smoke Runs From Curated Final Parameter Artifacts

Problem:

```text
The current regression script writes directly to analyses/phase3/ionic_epcsaft_regression/results/parameter_regression even for tiny smoke runs.
```

Required behavior:

```text
Smoke runs write under analyses/phase3/ionic_epcsaft_regression/results/runs/<timestamp-or-label>/.
Curated final regression artifacts are written to results/parameter_regression only when the run is intentionally promoted.
The command has an explicit --promote or --output-label option.
The final report states which run was promoted and why.
```

### MEA Fix 3: Add Progress, Timing, And Resume Support

Required behavior:

```text
Each objective evaluation reports elapsed time, target counts, pressure solve success count, speciation solve success count, residual norm, and current best metric.
Long runs write a progress JSONL file under results/runs/.
Interrupted runs preserve enough data to diagnose the slow records.
```

### MEA Fix 4: Use Package Coupled Regression When Available

Required behavior:

```text
Replace or bypass the slow MEA-side SciPy wrapper when the package exposes a coupled reactive electrolyte regression problem.
Keep MEA target construction and artifact writing in MEA.
Keep package-specific implementation details in ePC-SAFT.
```

Files to modify:

```text
src/MEA/epcsaft_ionic/regress_parameters.py
src/MEA/epcsaft_ionic/model.py
tests/test_epcsaft_ionic.py
```

### MEA Fix 5: Update Stale Feedback Documents

Problem:

```text
analyses/phase3/ionic_epcsaft_regression/epcsaft_ionic_package_feedback.md contains older statements from before the package exposed the reactive-electrolyte APIs. Later sections are newer, so the file is internally inconsistent.
```

Required behavior:

```text
Keep the historical context if useful.
Move stale "missing API" language into a dated archive section.
Make the active blocker clear: coupled regression robustness, speed, diagnostics, and final acceptance.
Point future agents to this completion handoff as the current source of truth.
```

### MEA Fix 6: Add Tests That Protect The Final Workflow

Add tests for:

```text
Approval check fails on the current smoke-only regression summary.
Approval check passes on a tiny synthetic/fixture summary that satisfies thresholds.
Regression residual vector length is stable when a pressure or speciation record returns a package failure result.
Generated ionic plot artifacts contain CSV, .mpl.yaml, PNG, SVG, and PDF.
The fitted dataset CSV values match ionic_parameter_regression_values.csv.
```

## What To Report To The Upstream ePC-SAFT Agent

Use this contract in a GitHub issue, GitHub discussion, handoff comment, or direct Codex handoff:

```text
Coordination contract:
- Upstream package: ePC-SAFT (<upstream-ePC-SAFT>)
- Upstream fixer thread: unknown unless user provides one
- Downstream consumer: MEA-Thermodynamics (<repo-root>)
- Downstream tester thread: current MEA regression completion thread
- Shared discussion: <issue/discussion URL or local handoff path>
- Baseline: <timestamp and latest downstream command output processed>
- Current owner: upstream
- Next actor: upstream
- Completion condition: downstream MEA approval_check passes after package-backed coupled regression and full-grid render
```

Report these exact facts:

```text
The MEA workflow uses 9 true species and Born SSM+DS/concentration-dependent dielectric options.
The current full-grid package-backed evaluation runs but is not final regression.
Current full-grid metrics: pressure 161/161, speciation 74/74, median pressure abs log10 error 0.36236, max 0.97264.
Current parameter summary is only a failed 3/3 target, 1 nfev smoke artifact.
The needed package capability is generic coupled reactive-electrolyte regression for vapor partial pressure and speciation targets, not an MEA-only hard-coded solver.
The package must provide fast batch/sweep evaluation, warm starts, fixed-shape failure results, and fitted masks for m/s/e/d_born/k_ij.
```

Attach or link these downstream files:

```text
analyses/phase3/ionic_epcsaft_regression/results/parameter_regression/ionic_parameter_regression_summary.json
analyses/phase3/ionic_epcsaft_regression/results/parameter_regression/ionic_parameter_regression_values.csv
analyses/phase3/ionic_epcsaft_regression/results/summary/ionic_evaluation_summary.json
analyses/phase3/ionic_epcsaft_regression/results/pressure/ionic_pressure_comparison.csv
analyses/phase3/ionic_epcsaft_regression/results/speciation/ionic_speciation_activity_residuals.csv
docs/ePC-SAFT/mea-ionic-regression-completion-handoff.md
docs/ePC-SAFT/meah-meacoo-real-data-regression-plan.md
```

## What The Downstream Agent Must Report Back

Use this response format after every serious run:

```text
MEA ionic regression report
Timestamp:
MEA repo commit/branch:
ePC-SAFT package commit/branch:
Installed epcsaft path/version:

Commands run:
- <command>

Runtime:
- <wall time per command>
- <objective evaluations>
- <average time per objective evaluation>

Regression summary:
- target_counts:
- optimizer.success:
- optimizer.message:
- nfev:
- initial_residual_norm:
- final_residual_norm:
- final_metrics.vle_median_abs_log10_error:
- final_metrics.failure_count:
- parameters at bounds:

Full-grid evaluation:
- pressure_success_count / pressure_count:
- raw_pressure_median_abs_log10_error:
- raw_pressure_max_abs_log10_error:
- speciation_success_count / speciation_count:
- largest speciation errors:
- reaction residual medians:

Artifacts regenerated:
- <paths>

Acceptance result:
- PASS or FAIL
- exact failed gates:

Next actor:
- upstream, downstream, or none
```

## Stop Conditions

Stop and hand off upstream when:

```text
The package regression helper cannot express the coupled MEA target.
A representative regression run is dominated by package solve runtime.
A package result throws instead of returning fixed-shape diagnostics in normal recoverable failures.
The downstream residual vector length depends on which records fail.
The package must rebuild and import under Linux uv/Python 3.13.
```

Stop and hand off downstream when:

```text
The upstream package exposes the coupled regression API and passes its own tests.
The MEA repo needs target wiring, artifact promotion, approval checks, or manuscript updates.
```

Stop and ask the user when:

```text
Final metrics pass numerically but fitted parameters hit bounds or look physically implausible.
Pressure and speciation targets trade off in a way that changes the scientific claim.
The final acceptance threshold needs to be relaxed for a defensible manuscript limitation statement.
```
