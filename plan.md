# MEA ePC-SAFT Submission-Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current full-ionic MEA ePC-SAFT workflow and first-draft manuscript into a submission-ready thermodynamic-modeling paper comparable in scope and defensibility to the referenced ePC-SAFT and amine thermodynamics papers.

**Architecture:** Keep this repository as the downstream MEA validation, regression, and manuscript workflow. Use `src/MEA` for reusable MEA-side orchestration, `analyses/epcsaft_ionic_regression` for regression and figure artifacts, `data/reference` for source data and parameter tables, and `docs/latex` for the manuscript. Package-side improvements belong in `C:\Users\Tanner\Documents\git\ePC-SAFT` and are tracked by https://github.com/tannerpolley/ePC-SAFT/issues/44.

**Tech Stack:** Python in `.venv`, pandas, numpy, scipy, matplotlib, local `epcsaft` runtime, unittest, MiKTeX/latexmk, Zotero-managed `docs/latex/references.bib`.

---

## Current Baseline To Preserve

- Repo root: `C:\Users\Tanner\Documents\git\MEA-Thermodynamics`
- Python: `C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe`
- LaTeX source: `docs/latex/main.tex`
- Canonical PDF: `docs/latex/builds/main.pdf`
- Main ionic dataset: `data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit`
- Current pressure records: 161/161 solved
- Current speciation records: 74/74 solved
- Current pressure median absolute log10 error: `0.3317113205027986`
- Current pressure max absolute log10 error: `0.9774957143734262`
- Current MEAH+/MEACOO- fit residual norm: `0.271444549584188 -> 0.26765769640830644`
- Current carbonate Born scan: `3.0/3.0 = 0.702107882`, `4.5/4.5 = 0.837568995`, `6.5/7.5 = 1.061379851`, `1.05/1.05 = 1.913497055`
- Current OH- Born derivation: `d_born = 3.0810768940040356`

Do not edit `docs/latex/references.bib` manually. It is Zotero-owned.

Do not use `uv run` unless explicitly requested. Use the repo `.venv` Python directly.

Do not create scratch/temp folders in the repo. Use analysis-local `results/runs/` only for ignored exploratory outputs.

---

## File Map

- Modify `src/MEA/epcsaft_ionic/model.py` for runtime parameters, species maps, and reusable model helpers.
- Modify `src/MEA/epcsaft_ionic/ion_parameter_regression.py` for regression metrics shared across scripts.
- Modify `src/MEA/epcsaft_ionic/plot_results.py` for pressure/speciation plotting helpers.
- Modify `analyses/epcsaft_ionic_regression/scripts/fit_ion_parameters.py` for promoted MEAH+/MEACOO- fitting.
- Modify `analyses/epcsaft_ionic_regression/scripts/fit_trace_carbonate_born.py` only if carbonate Born identifiability evidence changes.
- Modify `analyses/epcsaft_ionic_regression/scripts/generate_data.py` and `render_figures.py` for refreshed data/figures.
- Create `analyses/epcsaft_ionic_regression/scripts/fit_global_pressure_speciation.py`.
- Create `analyses/epcsaft_ionic_regression/scripts/evaluate_train_validation_split.py`.
- Create `analyses/epcsaft_ionic_regression/scripts/compute_parameter_sensitivity.py`.
- Create `analyses/epcsaft_ionic_regression/results/global_regression/`.
- Create `analyses/epcsaft_ionic_regression/results/train_validation/`.
- Create `analyses/epcsaft_ionic_regression/results/sensitivity/`.
- Modify `data/reference/MEA/epcsaft_species_parameter_evidence.csv` only when parameter evidence status changes.
- Modify `data/reference/MEA/full_component_parameter_source_audit.csv` after source audit changes.
- Modify `docs/ePC-SAFT/full-component-parameter-source-audit.md`.
- Modify `docs/ePC-SAFT/full-ionic-parameter-manuscript-completion-audit.md`.
- Modify `docs/latex/main.tex`, `docs/latex/sections/*.tex`, `docs/latex/tables/*.tex`, and selected `docs/latex/figures/*`.
- Modify `tests/test_ion_parameter_regression_artifacts.py`.
- Create `tests/test_global_regression_artifacts.py`.

---

## Phase 0: Safety And Baseline Verification

### Task 0.1: Confirm working tree and known baseline

**Files:** none.

- [ ] **Step 1: Inspect concise git state.**

Run:

```powershell
git status --short --branch
```

Expected: dirty worktree is allowed. Do not revert unrelated changes.

- [ ] **Step 2: Run baseline tests.**

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest discover tests -v
& $py scripts\validate_project.py quick
```

Expected: all current tests pass and quick validation passes. If this fails before new edits, stop and document the failure in `docs/ePC-SAFT/full-ionic-parameter-manuscript-completion-audit.md`.

- [ ] **Step 3: Build manuscript.**

Run:

```powershell
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics\docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Expected: `docs/latex/builds/main.pdf` is produced.

---

## Phase 1: Final Pressure + Speciation Global Regression

Purpose: remove the largest scientific weakness. The current ionic set is validated, but not pressure-optimized. A submission-grade parameter paper needs either a final joint regression or a carefully bounded workflow/validation claim. Prefer the joint regression if runtime allows.

### Task 1.1: Add global-regression artifact tests

**Files:**
- Create: `tests/test_global_regression_artifacts.py`
- Create: `analyses/epcsaft_ionic_regression/scripts/fit_global_pressure_speciation.py`
- Output: `analyses/epcsaft_ionic_regression/results/global_regression/*`

- [ ] **Step 1: Create the failing test.**

Create `tests/test_global_regression_artifacts.py`:

```python
from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = ROOT / "analyses" / "epcsaft_ionic_regression" / "results" / "global_regression"


class GlobalRegressionArtifactTests(unittest.TestCase):
    def test_global_regression_artifacts_exist(self) -> None:
        required = [
            "global_regression_summary.json",
            "global_regression_values.csv",
            "global_regression_pressure_fit_data.csv",
            "global_regression_speciation_fit_data.csv",
            "global_regression_pressure_residuals.csv",
            "global_regression_speciation_residuals.csv",
            "global_regression_pressure_parity.mpl.yaml",
            "global_regression_pressure_parity.png",
            "global_regression_pressure_parity.svg",
            "global_regression_speciation_parity.mpl.yaml",
            "global_regression_speciation_parity.png",
            "global_regression_speciation_parity.svg",
        ]
        missing = [name for name in required if not (GLOBAL / name).exists()]
        self.assertEqual(missing, [])

    def test_global_regression_summary_has_submission_metrics(self) -> None:
        summary = json.loads((GLOBAL / "global_regression_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["fit_tier"], "pressure_speciation_global")
        self.assertIn("fit_parameters", summary)
        self.assertIn("objective_weights", summary)
        self.assertIn("pressure_metrics", summary)
        self.assertIn("speciation_metrics", summary)
        self.assertIn("parameters_at_bounds", summary)
        self.assertGreaterEqual(summary["pressure_metrics"]["row_count"], 100)
        self.assertGreaterEqual(summary["speciation_metrics"]["row_count"], 50)
        self.assertLessEqual(
            summary["pressure_metrics"]["median_abs_log10"],
            summary["baseline_pressure_metrics"]["median_abs_log10"],
        )
        self.assertLessEqual(summary["speciation_metrics"]["MEAH+"]["median_abs_log10"], 0.15)
        self.assertLessEqual(summary["speciation_metrics"]["MEACOO-"]["median_abs_log10"], 0.10)

    def test_global_regression_values_are_not_seed_only(self) -> None:
        with (GLOBAL / "global_regression_values.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        moved = [row for row in rows if abs(float(row["fitted"]) - float(row["initial"])) > 1.0e-6]
        self.assertGreaterEqual(len(moved), 3)
```

- [ ] **Step 2: Run the test and verify expected failure.**

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest tests.test_global_regression_artifacts -v
```

Expected: FAIL because global regression files do not exist.

### Task 1.2: Implement the global fit entrypoint

**Files:**
- Create: `analyses/epcsaft_ionic_regression/scripts/fit_global_pressure_speciation.py`
- Modify only if needed: `src/MEA/epcsaft_ionic/model.py`

- [ ] **Step 1: Use this initial fit parameter list.**

```python
FIT_NAMES = (
    "MEAH+__s",
    "MEAH+__e",
    "MEAH+__d_born",
    "MEACOO-__s",
    "MEACOO-__e",
    "MEACOO-__d_born",
    "k_ij__CO2__MEA",
    "k_ij__MEA__H2O",
    "k_ij__MEAH+__MEACOO-",
    "k_ij__MEAH+__HCO3-",
)
```

Do not fit `H3O+` or `OH-` directly without new direct data. Keep `HCO3-__d_born` and `CO3^2-__d_born` fixed at 3.0 unless a joint regression improves both pressure and carbonate speciation on validation data.

- [ ] **Step 2: Use explicit residual definitions.**

```text
pressure residual: log10(P_model / P_data)
speciation residual: log10(max(x_model, 1e-30) / max(x_target, 1e-30))
regularization residual: scale * (value - seed) / max(abs(seed), 1)
```

Start weights:

```python
PRESSURE_WEIGHT = 1.0
SPECIATION_WEIGHT = 1.0
REGULARIZATION_SCALE = 0.003
```

If pressure dominates and degrades `MEAH+` or `MEACOO-`, reduce pressure weight to `0.5`. If pressure does not improve, increase pressure weight to `2.0`. Record the final weights in the summary JSON.

- [ ] **Step 3: Write required summary fields.**

`global_regression_summary.json` must include:

```json
{
  "fit_tier": "pressure_speciation_global",
  "fit_parameters": [],
  "objective_weights": {},
  "target_counts": {},
  "optimizer": {},
  "initial_values": {},
  "fitted_values": {},
  "parameters_at_bounds": {},
  "baseline_pressure_metrics": {},
  "pressure_metrics": {},
  "baseline_speciation_metrics": {},
  "speciation_metrics": {},
  "claim_boundary": ""
}
```

- [ ] **Step 4: Write required CSV schemas.**

`global_regression_values.csv`:

```text
parameter,initial,fitted,delta,lower_bound,upper_bound,at_bound,source_status
```

`global_regression_pressure_residuals.csv`:

```text
fit_stage,row_id,source,temperature_C,MEA_weight_fraction,CO2_loading,observed_pressure_Pa,model_pressure_Pa,log10_model_over_data,success,message
```

`global_regression_speciation_residuals.csv`:

```text
fit_stage,row_id,source,temperature_C,CO2_loading,species,observed_mole_fraction,model_mole_fraction,log10_model_over_data,success,message
```

- [ ] **Step 5: Run a smoke fit first.**

Add CLI flags:

```text
--max-pressure-records
--max-speciation-records
--max-nfev
--output-label
--promote
```

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py analyses\epcsaft_ionic_regression\scripts\fit_global_pressure_speciation.py --max-pressure-records 20 --max-speciation-records 20 --max-nfev 10 --output-label smoke
```

Expected: finite residuals and non-promoted outputs under `results/runs/`.

- [ ] **Step 6: Run the promoted attempt.**

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py analyses\epcsaft_ionic_regression\scripts\fit_global_pressure_speciation.py --max-nfev 40 --promote
& $py -m unittest tests.test_global_regression_artifacts -v
```

Expected: pressure median absolute log10 residual improves relative to baseline while `MEAH+` and `MEACOO-` gates pass.

- [ ] **Step 7: If runtime blocks the full fit, document the blocker.**

If a full objective evaluation remains too slow, do not fake completion. Update `docs/ePC-SAFT/full-ionic-parameter-manuscript-completion-audit.md` and reference package issue #44. Keep the manuscript claim bounded as a workflow/validation study until package-side batching exists.

---

## Phase 2: Train/Validation Split

Purpose: prove the model is not only reproducing rows used for fitting.

### Task 2.1: Add deterministic split evaluation

**Files:**
- Create: `analyses/epcsaft_ionic_regression/scripts/evaluate_train_validation_split.py`
- Modify: `tests/test_global_regression_artifacts.py`
- Output: `analyses/epcsaft_ionic_regression/results/train_validation/*`

- [ ] **Step 1: Add split artifact tests.**

Append to `tests/test_global_regression_artifacts.py`:

```python
TRAIN_VALIDATION = ROOT / "analyses" / "epcsaft_ionic_regression" / "results" / "train_validation"


class TrainValidationArtifactTests(unittest.TestCase):
    def test_train_validation_artifacts_exist(self) -> None:
        required = [
            "train_validation_summary.json",
            "train_validation_pressure_residuals.csv",
            "train_validation_speciation_residuals.csv",
            "train_validation_pressure_by_source.csv",
            "train_validation_speciation_by_species.csv",
            "train_validation_pressure_residuals.mpl.yaml",
            "train_validation_pressure_residuals.png",
            "train_validation_pressure_residuals.svg",
        ]
        missing = [name for name in required if not (TRAIN_VALIDATION / name).exists()]
        self.assertEqual(missing, [])

    def test_train_validation_has_both_splits(self) -> None:
        summary = json.loads((TRAIN_VALIDATION / "train_validation_summary.json").read_text(encoding="utf-8"))
        self.assertIn("train", summary["pressure"])
        self.assertIn("validation", summary["pressure"])
        self.assertIn("train", summary["speciation"])
        self.assertIn("validation", summary["speciation"])
```

- [ ] **Step 2: Use deterministic split rules.**

Use these rules unless the loaded source names differ:

```text
Pressure validation sources: Jou, Xu
Pressure training sources: Aronu, Hilliard, Mamun
Speciation validation source: Jakobsen
Speciation training sources: Matin, Bottinger
```

If source names differ, print actual names and update the rule explicitly. Do not silently random-split.

- [ ] **Step 3: Evaluate both train and validation.**

Summary JSON must include:

```json
{
  "split_rule": {},
  "parameter_set": "global_regression if available, otherwise promoted_ionic_fit",
  "pressure": {
    "train": {},
    "validation": {}
  },
  "speciation": {
    "train": {},
    "validation": {}
  }
}
```

- [ ] **Step 4: Run script and tests.**

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py analyses\epcsaft_ionic_regression\scripts\evaluate_train_validation_split.py
& $py -m unittest tests.test_global_regression_artifacts -v
```

Expected: PASS and summary has both train and validation metrics.

---

## Phase 3: Sensitivity, Identifiability, And Uncertainty

Purpose: make fitted and fixed parameters scientifically defensible.

### Task 3.1: Add finite-difference sensitivity analysis

**Files:**
- Create: `analyses/epcsaft_ionic_regression/scripts/compute_parameter_sensitivity.py`
- Modify: `tests/test_global_regression_artifacts.py`
- Output: `analyses/epcsaft_ionic_regression/results/sensitivity/*`

- [ ] **Step 1: Add sensitivity artifact tests.**

Append:

```python
SENSITIVITY = ROOT / "analyses" / "epcsaft_ionic_regression" / "results" / "sensitivity"


class SensitivityArtifactTests(unittest.TestCase):
    def test_sensitivity_artifacts_exist(self) -> None:
        required = [
            "parameter_sensitivity_summary.json",
            "parameter_sensitivity_matrix.csv",
            "parameter_identifiability.csv",
            "parameter_sensitivity_heatmap.mpl.yaml",
            "parameter_sensitivity_heatmap.png",
            "parameter_sensitivity_heatmap.svg",
        ]
        missing = [name for name in required if not (SENSITIVITY / name).exists()]
        self.assertEqual(missing, [])
```

- [ ] **Step 2: Use relative perturbations.**

Use:

```text
positive-valued parameter relative step: 1e-3
k_ij absolute step: 1e-3
```

Report sensitivity of:

```text
pressure_median_abs_log10
MEAH+_median_abs_log10
MEACOO-_median_abs_log10
HCO3-_median_abs_log10
CO3^2-_median_abs_log10
```

- [ ] **Step 3: Include fixed trace ions.**

Include `HCO3-__d_born`, `CO3^2-__d_born`, `H3O+__d_born`, and `OH-__d_born` even if fixed. Mark them as `fixed_diagnostic`.

- [ ] **Step 4: Write identifiability CSV.**

Columns:

```text
parameter,norm_sensitivity,relative_rank,near_zero_sensitivity,high_correlation_risk,interpretation
```

Rules:

```text
near_zero_sensitivity = norm_sensitivity < 1e-4
high_correlation_risk = absolute pairwise sensitivity correlation > 0.98
```

- [ ] **Step 5: Run script and tests.**

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py analyses\epcsaft_ionic_regression\scripts\compute_parameter_sensitivity.py
& $py -m unittest tests.test_global_regression_artifacts -v
```

Expected: PASS and heatmap artifacts exist.

---

## Phase 4: Literature Comparison Table

Purpose: make novelty and scope obvious against similar papers.

### Task 4.1: Add manuscript-ready comparison table

**Files:**
- Create: `docs/latex/tables/literature_model_comparison.tex`
- Modify: `docs/latex/sections/introduction.tex`
- Modify: `tests/test_ion_parameter_regression_artifacts.py`

- [ ] **Step 1: Create `docs/latex/tables/literature_model_comparison.tex`.**

Use columns:

```text
Study, System, Model, Species basis, Electrolyte/Born treatment, Data used, Fitted quantities, Validation reported
```

Rows:

```text
Nasrifar and Tafazzol 2010
Baygi and Pahlavanzadeh 2015
Uyan et al. 2015
Wangler et al. 2018
Buelow et al. 2020/2021
Figiel et al. 2025
This work
```

- [ ] **Step 2: Insert the table in `docs/latex/sections/introduction.tex`.**

Add after the ePC-SAFT literature review:

```latex
\input{tables/literature_model_comparison}
```

- [ ] **Step 3: Use Zotero for missing citation keys.**

If any citation key is absent from `docs/latex/references.bib`, use Zotero export/regeneration. Do not hand-edit `references.bib`.

- [ ] **Step 4: Extend LaTeX convention test.**

Add assertions that the table exists and is input by the manuscript.

- [ ] **Step 5: Build PDF.**

Run:

```powershell
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics\docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Expected: no undefined citations from the comparison table.

---

## Phase 5: Regression Methods And Objective Equations

Purpose: reviewers need exact objective functions, residual definitions, weights, bounds, and solver settings.

### Task 5.1: Add manuscript objective equations and bounds table

**Files:**
- Modify: `docs/latex/sections/mea_system_modeling_results.tex`
- Modify: `docs/latex/sections/epc_saft_equation_of_state.tex`
- Create: `docs/latex/tables/regression_bounds.tex`

- [ ] **Step 1: Add residual equations.**

Use:

```latex
r_i^{P} = \log_{10}\left(P_i^{\mathrm{calc}}/P_i^{\mathrm{exp}}\right)
```

```latex
r_{i,j}^{x} = \log_{10}\left(\max(x_{i,j}^{\mathrm{calc}},10^{-30})/\max(x_{i,j}^{\mathrm{exp}},10^{-30})\right)
```

```latex
\Phi(\theta) = w_P \sum_i (r_i^P)^2 + w_x \sum_{i,j} (r_{i,j}^{x})^2 + w_R \sum_k \left(\frac{\theta_k - \theta_{k,0}}{\max(|\theta_{k,0}|,1)}\right)^2
```

- [ ] **Step 2: Add `docs/latex/tables/regression_bounds.tex`.**

Columns:

```text
Parameter, Initial value, Lower bound, Upper bound, Fitted value, Status
```

- [ ] **Step 3: Keep manuscript wording submission-safe.**

Do not mention local file paths in manuscript text. Use wording like:

```text
The residual tables and fitted parameter values are distributed with the reproducibility package.
```

---

## Phase 6: Residual Diagnostics Figures

Purpose: parity plots are not enough for a rigorous parameter paper.

### Task 6.1: Add pressure and speciation residual plots

**Files:**
- Modify: `analyses/epcsaft_ionic_regression/scripts/render_figures.py`
- Output: `analyses/epcsaft_ionic_regression/results/pressure/*`
- Output: `analyses/epcsaft_ionic_regression/results/speciation/*`
- Copy selected figures to: `docs/latex/figures/*`

- [ ] **Step 1: Add pressure residual plot.**

Create:

```text
analyses/epcsaft_ionic_regression/results/pressure/ionic_pressure_residuals_by_loading.csv
analyses/epcsaft_ionic_regression/results/pressure/ionic_pressure_residuals_by_loading.png
analyses/epcsaft_ionic_regression/results/pressure/ionic_pressure_residuals_by_loading.svg
analyses/epcsaft_ionic_regression/results/pressure/ionic_pressure_residuals_by_loading.mpl.yaml
```

Plot `CO2_loading` vs. `log10_model_over_data`, colored by source and marked by temperature bin.

- [ ] **Step 2: Add speciation residual plot.**

Create:

```text
analyses/epcsaft_ionic_regression/results/speciation/ionic_speciation_residuals_by_species.csv
analyses/epcsaft_ionic_regression/results/speciation/ionic_speciation_residuals_by_species.png
analyses/epcsaft_ionic_regression/results/speciation/ionic_speciation_residuals_by_species.svg
analyses/epcsaft_ionic_regression/results/speciation/ionic_speciation_residuals_by_species.mpl.yaml
```

Plot species vs. absolute log10 residual, colored by source, with median bars.

- [ ] **Step 3: Copy manuscript figures.**

Copy PNG/SVG to `docs/latex/figures` with names:

```text
mea_ionic_pressure_residuals_by_loading.png
mea_ionic_pressure_residuals_by_loading.svg
mea_ionic_speciation_residuals_by_species.png
mea_ionic_speciation_residuals_by_species.svg
```

- [ ] **Step 4: Reference figures in manuscript.**

Add one paragraph after the pressure/speciation parity figures. State which sources or species dominate residuals.

---

## Phase 7: Data And Code Availability Section

Purpose: add submission-safe reproducibility language without Codex/local-path wording.

### Task 7.1: Add availability text

**Files:**
- Create: `docs/latex/sections/data_code_availability.tex`
- Modify: `docs/latex/main.tex`

- [ ] **Step 1: Create the section.**

Use:

```latex
\section*{Data and Code Availability}
The processed validation tables, fitted parameter tables, plotting snapshots, and scripts required to reproduce the reported figures are distributed with the project repository. Literature data sources are cited in the manuscript, and derived tables preserve source identifiers, temperature, loading, and observable definitions used for regression and validation. The bibliography is managed through the cited reference database.
```

- [ ] **Step 2: Include it before bibliography.**

In `docs/latex/main.tex`, add:

```latex
\input{sections/data_code_availability}
```

immediately before `\clearpage` and the bibliography.

- [ ] **Step 3: Run submission-safety scan.**

Run:

```powershell
Select-String -Path 'docs\latex\main.tex','docs\latex\sections\*.tex','docs\latex\tables\*.tex' -Pattern 'Codex|agent|worktree|repo|repository-facing|local path|C:\\Users|artifact|handoff' -CaseSensitive:$false
```

Expected: no submission-facing process leakage.

---

## Phase 8: Figure And Table Polish

Purpose: make figures and tables publication-grade, not just present.

### Task 8.1: Enforce consistent plot styling

**Files:**
- Modify: `src/MEA/common/plot_style.py`
- Modify: render scripts under `analyses/*/scripts/`
- Output: regenerated plot sets

- [ ] **Step 1: Define final style constants.**

Use one shared map for species colors, marker shapes, and line styles for:

```text
CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, OH-
```

- [ ] **Step 2: Regenerate curated figures.**

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py analyses\six_species_legacy\scripts\render_figures.py
& $py analyses\epcsaft_neutral_parity\scripts\render_figures.py
& $py analyses\epcsaft_ionic_regression\scripts\render_figures.py
& $py analyses\2015_baygi\scripts\render_figures.py
```

Expected: all curated plot sets still contain CSV/PNG/SVG/YAML.

### Task 8.2: Clean visible LaTeX warnings

**Files:**
- Modify: `docs/latex/main.tex`
- Modify: `docs/latex/tables/*.tex`

- [ ] **Step 1: Inspect warnings.**

Run:

```powershell
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics\docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
Select-String -Path 'builds\main.log' -Pattern 'Overfull|Undefined|Citation|Reference|Warning|Infinite glue' -Context 0,1
```

- [ ] **Step 2: Fix hard blockers first.**

Expected before submission: zero undefined references and zero undefined citations.

- [ ] **Step 3: Reduce overfull and table warnings.**

For long tables, prefer `tabularx`, `adjustbox`, shorter captions, and `\makecell{}` line breaks. Do not delete scientific content to hide warnings.

---

## Phase 9: Overleaf Mirror Projection

Purpose: sync only after the source manuscript is ready.

### Task 9.1: Sync mirror safely

**Files:**
- Source: `docs/latex/*`
- Mirror: `C:\Users\Tanner\Documents\git\LaTeX-Projects\MEA-Thermodynamics-LaTeX`

- [ ] **Step 1: Check source and mirror git state.**

Run:

```powershell
git status --short --branch
git -C C:\Users\Tanner\Documents\git\LaTeX-Projects\MEA-Thermodynamics-LaTeX status --short --branch
```

- [ ] **Step 2: Validate sync script syntax.**

Run:

```powershell
[System.Management.Automation.Language.Parser]::ParseFile(
  'docs\latex\scripts\sync_to_overleaf_mirror.ps1',
  [ref]$null,
  [ref]$null
) | Out-Null
```

- [ ] **Step 3: Dry-run sync.**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File docs\latex\scripts\sync_to_overleaf_mirror.ps1 -WhatIf -CleanBuildFiles
```

- [ ] **Step 4: Run sync only when dry run is correct.**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File docs\latex\scripts\sync_to_overleaf_mirror.ps1 -CleanBuildFiles
```

Expected mirror root entries:

```text
.git
main.tex
references.bib
software_references.bib
figures
tables
sections
appendices
thumbnails
styles
```

If `styles` is not part of the current sync policy but is required by `main.tex`, update the sync policy deliberately instead of copying files by hand.

---

## Phase 10: Final Submission-Readiness Audit

Purpose: do not call the paper submission-ready based only on effort or green tests.

### Task 10.1: Run the final prompt-to-artifact audit

**Files:**
- Modify: `docs/ePC-SAFT/full-ionic-parameter-manuscript-completion-audit.md`

- [ ] **Step 1: Run Python validation.**

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest discover tests -v
& $py scripts\validate_project.py quick
```

- [ ] **Step 2: Build PDF.**

```powershell
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics\docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

- [ ] **Step 3: Update audit table.**

Add rows mapping:

```text
Requirement
Concrete artifact
Command used
Observed result
Pass/fail
Residual risk
```

Required requirements:

```text
full nine-species basis
literature/fitted parameter provenance
SSM+DS Born and dielectric handling
MEAH+/MEACOO- real-data regression
HCO3-/CO3^2- Born identifiability
H3O+/OH- literature or derivation support
pressure + speciation global regression
train/validation split
sensitivity/uncertainty
literature model comparison
pressure/speciation/residual figures
submission-safe manuscript prose
PDF build
Overleaf mirror sync, if requested
```

- [ ] **Step 4: State final claim boundary.**

If global pressure/speciation regression is complete and improves pressure without degrading speciation, the manuscript may claim a final fitted full-ionic MEA ePC-SAFT parameter set.

If global regression is not complete, the manuscript must claim a full-ionic workflow and validation/evidence set, not a final pressure-optimized parameter set.

---

## Package-Side Improvement Note

GitHub issue posted directly to the ePC-SAFT package repo:

- https://github.com/tannerpolley/ePC-SAFT/issues/44

Requested package improvements:

- Batched reactive speciation and bubble-pressure evaluation.
- Structured per-row success/failure diagnostics.
- Reusable objective helpers for pressure/speciation regressions.
- Finite-difference or native sensitivity/Jacobian utilities.
- Result schemas that downstream manuscripts can serialize without bespoke glue.
- Caching/reuse of invariant setup across multistart attempts.

Do not block MEA manuscript work on this issue. Implement downstream wrappers first, then replace them with package-native APIs later if available.

---

## Final Acceptance Criteria

The paper is submission-ready only when all of the following are true:

- Full ionic species basis is present and tested.
- Every component has parameter provenance: literature, fit, transfer, derivation, or diagnostic fixed.
- MEAH+ and MEACOO- are fitted to real data with residual statistics and plots.
- HCO3- and CO3^2- Born values are defended by the full-data seed scan or a better global regression.
- H3O+ and OH- are defended by literature/derivation and are not falsely claimed as independently fitted.
- A pressure + speciation global regression has been attempted and either completed or explicitly bounded in the manuscript claim.
- Train/validation split metrics are reported.
- Sensitivity/identifiability diagnostics are reported for fitted and fixed key parameters.
- Literature comparison table is included.
- Pressure, speciation, regression, residual, and parameter-evidence figures/tables exist in manuscript-ready form.
- `docs/latex/builds/main.pdf` builds without undefined citations or references.
- Submission-facing text contains no Codex, agent, local-path, worktree, handoff, or repository-process language.
- The final manuscript claim matches the actual validation evidence.
