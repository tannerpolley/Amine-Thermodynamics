# Full-Ionic ePC-SAFT MEA Parameter and Manuscript Completion Audit

Date: 2026-05-10

## Goal Restatement

The project is complete when all deliverables in the active ionic workflow are
verified against explicit evidence and reproducible checks:

- full nine-species ionic basis (CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, OH-),
- component-by-component parameter source audit across all matching literature and local tables,
- MEAH+ and MEACOO- promoted fit demonstrates true optimization (not seed-only),
- ionic/speciation and pressure outputs have required CSV/PNG/SVG/YAML artifacts,
- LaTeX source and build outputs follow repository conventions.

## Completion Audit Matrix

| Deliverable | Gate Check | Evidence | Status |
| --- | --- | --- | --- |
| All runtime species present | `src/MEA/epcsaft_runtime.py` `SPECIES` includes the nine-species full basis | `src/MEA/epcsaft_runtime.py` | Required |
| All active-species parameter scope documented | `data/reference/MEA/epcsaft_species_parameter_evidence.csv` includes every species and required `s/e/d_born/dielc/f_solv/z/MW` fields where applicable | `data/reference/MEA/epcsaft_species_parameter_evidence.csv` | Required |
| Best available parameter source selected | Each component is audited against matching local paper digests/tables; placeholder trace-ion sigma/energy rows are replaced by Held/Uyan values where available | `docs/ePC-SAFT/full-component-parameter-source-audit.md`, `data/reference/MEA/full_component_parameter_source_audit.csv` | Required |
| Trace-ion promoted values locked | HCO3-, CO3^2-, H3O+, and OH- promoted rows match Held/Uyan sigma/energy values and promoted water-ion interactions; H3O+ uses Figiel SSM+DS `d_born=1.218`; OH- uses hydration-derived `d_born=3.081076894` | `data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/{pure/any_solvent.csv,mixed/binary_interaction/k_ij.csv}` | Required |
| Trace-carbonate Born fit checked | HCO3- and CO3^2- `d_born` are checked against Tier A rows that directly report those species; artifacts include full-data seed attempts, CSV, statistics summary, PNG, SVG, and style sidecar | `analyses/epcsaft_ionic_regression/results/trace_carbonate_born_regression/` | Required |
| OH- Born derivation documented | OH- `d_born` is derived from a hydroxide hydration free energy by Born-equation inversion and written as CSV/JSON/YAML evidence | `analyses/epcsaft_ionic_regression/results/oh_born_derivation/` | Required |
| MEAH+ and MEACOO- are not seed-only | Optimizer summary shows residual reduction and parameter movement for both promoted ions | `analyses/epcsaft_ionic_regression/results/ion_parameter_regression/ion_parameter_fit_summary.json` | Required |
| Regression artifact contract | Values/statistics/fit data + plot family CSV/PNG/SVG/YAML exist | `analyses/epcsaft_ionic_regression/results/ion_parameter_regression/*` | Required |
| Full ionic speciation/pressure outputs | CSV + plot package for ionic pressure/speciation deliverables exists | `analyses/epcsaft_ionic_regression/results/{pressure,speciation}` | Required |
| LaTeX source/build convention | `docs/latex/main.tex` is source; PDF is under `docs/latex/builds/main.pdf`; build dir is configured by `.latexmkrc` | `docs/latex/main.tex`, `docs/latex/.latexmkrc`, `docs/latex/builds/main.pdf` | Required |
| Validation hygiene | Validation executed via repository `.venv` Python, not `uv run` cache mode | `.venv\\Scripts\\python.exe` | Required |

## Explicit Deliverable Checks

### 1) Species and parameter-scope coverage

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest tests.test_ion_parameter_regression_artifacts.IonParameterRegressionArtifactTests.test_full_species_and_parameter_scope_is_complete -v
```

Expected behavior:

- `set(species)` from `epcsaft_species_parameter_evidence.csv` equals
  `CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, OH-`.
- For each species, required fields are present (including `d_born`, `dielc`, `f_solv`, `z`, `MW` where applicable).

### 2) MEAH+/MEACOO- not seed-only

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest tests.test_ion_parameter_regression_artifacts.IonParameterRegressionArtifactTests.test_promoted_ion_fit_is_not_seed_only -v
```

Expected behavior:

- `final_residual_norm < initial_residual_norm`,
- at least `MEAH+__s`, `MEACOO-__s`, `MEAH+__d_born`, and `MEACOO-__e` change from initial values,
- no promoted parameter at bound.

### 2b) Full parameter-audit promotion gate

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest tests.test_ion_parameter_regression_artifacts.IonParameterRegressionArtifactTests.test_trace_ion_literature_values_are_promoted -v
```

Expected behavior:

- `HCO3-` uses `sigma=2.9296`, `epsilon/k=70.0`, `d_born=3.0`, and `water-HCO3- k_ij=0.0`.
- `CO3^2-` uses `sigma=2.4422`, `epsilon/k=249.26`, `d_born=3.0`, and `water-CO3^2- k_ij=-0.25`.
- `H3O+` uses `sigma=3.4654`, `epsilon/k=500.0`, `d_born=1.218`, and `water-H3O+ k_ij=0.25`.
- `OH-` uses `sigma=2.0177`, `epsilon/k=650.0`, `d_born=3.081076894`, and `water-OH- k_ij=-0.25`.

### 3) Artifact completeness (CSV + PNG + SVG + YAML)

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest tests.test_ion_parameter_regression_artifacts.IonParameterRegressionArtifactTests.test_full_ionic_plot_artifacts_include_expected_formats -v
```

Expected behavior:

- `meah_meacoo_speciation_parity.{png,svg,mpl.yaml}` and `ion_parameter_speciation_fit_data.csv`
- `meah_meacoo_loading_curves.{png,svg,mpl.yaml}` and `ion_parameter_speciation_fit_data.csv`
- `ion_parameter_pressure_parity.{png,svg,mpl.yaml}` and `ion_parameter_pressure_fit_data.csv`
- `ionic_epcsaft_co2_pressure.{png,svg,mpl.yaml}` and `ionic_pressure_comparison.csv`
- `ionic_epcsaft_speciation_activity.{png,svg,mpl.yaml}` and `ionic_speciation_plot_data.csv`
- `trace_carbonate_born_parity.{png,svg,mpl.yaml}` plus `trace_carbonate_born_fit_data.csv`, `trace_carbonate_born_fit_values.csv`, and `trace_carbonate_born_fit_summary.json`

### 4) LaTeX convention gate

Run:

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest tests.test_ion_parameter_regression_artifacts.IonParameterRegressionArtifactTests.test_latex_source_and_output_conventions -v
& $py -m unittest tests.test_ion_parameter_regression_artifacts.IonParameterRegressionArtifactTests.test_active_runtime_species_are_complete -v
```

Expected behavior:

- `docs/latex/main.tex` contains `\documentclass`, `\begin{document}`, `\end{document}` and sections inputs,
- `.latexmkrc` sets both `out_dir` and `aux_dir` to `builds`,
- `docs/latex/main.pdf` does not exist at repo root level,
- `docs/latex/builds/main.pdf` exists.

### 5) Full suite acceptance for this audit

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py -m unittest tests.test_ion_parameter_regression_artifacts -v
```

### 6) Human-readable build and quant evidence (informational)

```powershell
$py = 'C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe'
& $py scripts\doctor.py
cd C:\Users\Tanner\Documents\git\MEA-Thermodynamics\docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Current Quantitative Evidence

- Promotion tier: `tier_a_local_speciation`
- Fitted parameters: 8 rows (`MEAH+__s`, `MEAH+__e`, `MEAH+__d_born`,
  `MEACOO-__s`, `MEACOO-__e`, `MEACOO-__d_born`, `k_ij__MEAH+__MEACOO-`)
- Trace-carbonate Born scan: `HCO3-__d_born = 3.0`,
  `CO3^2-__d_born = 3.0`, retained as promoted values because the available
  Tier A rows reject substantial alternatives. Full-data residual norms:
  `3.0/3.0 = 0.702107882`, `4.5/4.5 = 0.837568995`,
  `6.5/7.5 = 1.061379851`, and `1.05/1.05 = 1.913497055`.
- OH- Born derivation: `d_born = 3.0810768940040356` from Born hydration-energy
  inversion using an absolute hydroxide hydration free energy of `106.4 kcal/mol`.
- Optimizer: success, `final_residual_norm 0.2677 < initial_residual_norm 0.2714`
- Full ionic runtime checks after the full parameter-audit promotion: 161 pressure rows and 74 speciation rows solved
- Raw pressure median absolute log10 error after trace-ion promotion: `0.3317113205027986`
- Active speciation residual medians (log10 model/target):
  CO2 `3.9763`, MEA `0.1708`, H2O `0.0088`, MEAH+ `0.0947`,
  MEACOO- `0.0594`, HCO3- `0.4795`, CO3^2- `0.8602`,
  H3O+ `9.4067`, OH- `6.3244`.
- Remaining caveat unchanged: MEACOO-/MEAH+ parameters are promoted against
  local speciation data only; full pressure-weighted global re-optimization remains
  the next optimization step.

## 2026-05-10 Validation Snapshot

| Requirement | Concrete artifact | Command used | Observed result | Pass/fail | Residual risk |
| --- | --- | --- | --- | --- | --- |
| Full nine-species basis | `src/MEA/epcsaft_runtime.py`, `data/reference/MEA/epcsaft_species_parameter_evidence.csv` | `python -m unittest tests.test_ion_parameter_regression_artifacts -v` | Species basis and parameter-scope tests passed | Pass | None beyond normal maintenance |
| Literature/fitted parameter provenance | `docs/ePC-SAFT/full-component-parameter-source-audit.md`, promoted dataset CSVs | `python -m unittest tests.test_ion_parameter_regression_artifacts -v` | Trace-ion promotion and audit tests passed | Pass | Source audit remains narrative-heavy rather than database-backed |
| SSM+DS Born and dielectric handling | `docs/latex/sections/epc_saft_equation_of_state.tex`, promoted dataset, OH and carbonate Born artifacts | `python -m unittest tests.test_ion_parameter_regression_artifacts -v` | Born-radius audit tests passed; manuscript section updated | Pass | Carbonate and hydroxide support remain bounded by available data |
| MEAH+/MEACOO- real-data regression | `analyses/epcsaft_ionic_regression/results/ion_parameter_regression/*` | `python -m unittest tests.test_ion_parameter_regression_artifacts -v` | Promoted fit reduced residual norm and moved fitted ion parameters off seeds | Pass | Fit is still local-speciation-led rather than pressure-coupled |
| HCO3-/CO3^2- Born identifiability | `analyses/epcsaft_ionic_regression/results/trace_carbonate_born_regression/*` | `python analyses/epcsaft_ionic_regression/scripts/fit_trace_carbonate_born.py` | Deterministic full-data seed scan retained `3.0/3.0` as the promoted pair | Pass | Not a full multivariate global identifiability proof |
| H3O+/OH- literature or derivation support | `analyses/epcsaft_ionic_regression/results/oh_born_derivation/*` | `python -m unittest tests.test_ion_parameter_regression_artifacts -v` | H3O+ and OH- support artifacts passed | Pass | No direct MEA-system hydronium/hydroxide fit data |
| Pressure + speciation global regression | `analyses/epcsaft_ionic_regression/results/global_regression/*` | `python analyses/epcsaft_ionic_regression/scripts/fit_global_pressure_speciation.py --promote` | Coupled objective and parity artifacts were written; summary status is `bounded_incomplete` and selected parameter set remains `promoted_ionic_fit` | Pass with boundary | Final all-row least-squares remains runtime-bounded |
| Train/validation split | `analyses/epcsaft_ionic_regression/results/train_validation/*` | `python analyses/epcsaft_ionic_regression/scripts/evaluate_train_validation_split.py` | Deterministic source-held-out split summary written for pressure and speciation | Pass | Validation is source-held-out, not random or temperature-fold cross-validation |
| Sensitivity/uncertainty | `analyses/epcsaft_ionic_regression/results/sensitivity/*` | `python analyses/epcsaft_ionic_regression/scripts/compute_parameter_sensitivity.py` | Finite-difference sensitivity and identifiability tables written | Pass | Sensitivity uses a reduced live subset because full-data finite differences remain costly |
| Literature model comparison | `docs/latex/tables/literature_model_comparison.tex` | `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` | Table included and citations resolved | Pass | Table still produces layout warnings that could be polished further |
| Pressure/speciation/residual figures | `analyses/epcsaft_ionic_regression/results/{pressure,speciation}`, `docs/latex/figures/mea_ionic_*residuals*` | `python analyses/epcsaft_ionic_regression/scripts/render_figures.py` | Residual plots added and copied into manuscript figure set | Pass | Figure styling is consistent but not yet warning-free in all table/figure placements |
| Submission-safe manuscript prose | `docs/latex/main.tex`, `docs/latex/sections/*.tex`, `docs/latex/tables/*.tex` | `Select-String ... -Pattern 'Codex|agent|worktree|repo|repository-facing|local path|C:\\Users|artifact|handoff'` | No direct Codex, agent, worktree, handoff, or local-path leakage; `repo` produced false-positive substring matches such as `reported` and `reproduce` | Pass with note | Grep pattern is over-broad for `repo` substring matches |
| PDF build | `docs/latex/builds/main.pdf` | `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` | PDF built successfully with no undefined citations or references | Pass | Overfull/underfull layout warnings remain in the log |

## Result Log

- 2026-05-10: Audit file strengthened with explicit checks for species coverage,
  per-species parameter completeness, non-seed fit movement, artifact format
  completeness, and LaTeX build conventions.
- 2026-05-10: Added bounded global-regression, train/validation, and sensitivity
  artifact families plus manuscript coverage for the comparison table, regression
  bounds table, residual diagnostics, and data/code availability section.
- 2026-05-10: Full component parameter audit added to the gate. HCO3-, CO3^2-,
  H3O+, and OH- sigma/dispersion values and water-ion interactions were promoted
  from Held/Uyan tables; H3O+ uses Figiel2025 `d_born=1.218`. Ionic pressure
  and speciation artifacts were regenerated against the updated dataset.
- 2026-05-10: Added trace-carbonate Born regression artifacts. HCO3- and
  CO3^2- Born radii converge back to the promoted 3.0 values against Tier A
  rows that report those species. OH- remains literature/convention-only because
  the local target set does not directly report hydroxide.
- 2026-05-10: Added OH- Born derivation artifact and promoted `d_born=3.081076894`.
  This satisfies the parameter-evidence requirement as a literature-backed Born
  estimate, not as an MEA-system regression.
