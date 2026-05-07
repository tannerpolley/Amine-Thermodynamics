# MEA Thermodynamics

Legacy and diagnostic workflows for the `CO2-MEA-H2O` thermodynamic system.

The active project is organized around two separate legacy ecosystems plus a
neutral ePC-SAFT parity layer:

- `MEA.six_species`: canonical six-species MEA speciation and Jou CO2 vapor-pressure baseline
- `MEA.nine_species`: diagnostic nine-species chemistry and pressure workflow
- `MEA.epcsaft_neutral`: first-pass ePC-SAFT replacement for the neutral apparent `CO2/MEA/H2O` pressure backend
- `MEA.epcsaft_ionic`: full true-species ionic ePC-SAFT diagnostics and bounded parameter regression with Born SSM+DS

Older scripts and data copies live under `archive/` for reference only.

## Setup

This repository is uv-based and targets Python 3.13.

Required sibling repositories:

- `C:\Users\Tanner\Documents\git\PC-SAFT`
- `C:\Users\Tanner\Documents\git\ePC-SAFT`

From this repo:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
uv sync
```

The old `pcsaft` package is retained as a reference backend for parity checks.
The active ePC-SAFT dependency is resolved from the absolute local path above so
this repository still works when checked out under `.codex\worktrees`.

## Canonical Commands

Compile active scripts:

```powershell
uv run python -m compileall MEA
```

Regenerate canonical plots and diagnostic artifacts:

```powershell
uv run python MEA\run_plot_exports.py
```

Run the focused all-species sweep check:

```powershell
uv run python -m MEA.nine_species.sweep_check
```

Run individual package entrypoints:

```powershell
uv run python -m MEA.six_species.plot_speciation
uv run python -m MEA.six_species.plot_pressure
uv run python -m MEA.epcsaft_neutral.plot_pressure
uv run python -m MEA.epcsaft_ionic.regress_parameters
uv run python -m MEA.epcsaft_ionic.plot_results
uv run python -m MEA.nine_species.plot_speciation_diagnostic
uv run python -m MEA.nine_species.plot_pressure_diagnostic
```

## Active Outputs

Canonical plot artifacts are committed only for the active workflow:

- `out/plots/MEA/six_species/speciation/speciation.png`
- `out/plots/MEA/six_species/pressure/legacy_pcsaft_jou_recomputed_fit.png`
- `out/plots/MEA/epcsaft_neutral/pressure/epcsaft_neutral_pcsaft_parity.png`
- `out/plots/MEA/epcsaft_ionic/pressure/ionic_epcsaft_co2_pressure.png`
- `out/plots/MEA/epcsaft_ionic/speciation/ionic_epcsaft_speciation_activity.png`
- `out/plots/MEA/nine_species/speciation_diagnostic/speciation_diagnostic.png`
- `out/plots/MEA/nine_species/pressure_diagnostic/co2_partial_pressure.png`

Canonical evidence files live under:

- `out/legacy_baseline/`
- `out/epcsaft/neutral_parity/`
- `out/epcsaft/ionic_regression/`
- `out/plots/MEA/nine_species/speciation_diagnostic/`
- `out/plots/MEA/nine_species/pressure_diagnostic/`

## Model Roles

`MEA.six_species.plot_speciation` is the canonical legacy speciation plot. It uses the six-species solver in `MEA.six_species.chemistry` and overlays the available 40 C, 30 wt% MEA speciation data.

`MEA.six_species.plot_pressure` is the canonical Jou vapor-pressure gate. It uses six-species legacy chemistry collapsed to apparent `CO2/MEA/H2O` and verifies the expected median absolute `log10(model/data)` pressure errors.

`MEA.epcsaft_neutral.plot_pressure` is the first ePC-SAFT migration gate. It
uses the same six-species chemistry and apparent liquid composition, then solves
the neutral apparent `CO2/MEA/H2O` pressure with the sibling `epcsaft` package.
It writes old-PC-SAFT vs neutral-ePC-SAFT parity CSV/JSON evidence and must match
the legacy Jou pressure metrics within the same tolerance before any ionic
ePC-SAFT workflow becomes canonical.

`MEA.epcsaft_ionic.regress_parameters` fits the full ionic true-species
parameter set against local VLE/speciation targets using the public sibling
`epcsaft` state/activity/fugacity APIs, Born SSM+DS user options, fitted `d_born`
variables for ions, and regularization to literature/legacy seeds.
`MEA.epcsaft_ionic.plot_results` evaluates the fitted ionic dataset, writes raw
and calibrated CO2 pressure diagnostics, and regenerates ionic pressure and
speciation plots. The calibrated pressure curve is explicit and reproducible; the
raw fugacity residuals remain in the CSV/JSON reports.

`MEA.nine_species.plot_speciation_diagnostic` and `MEA.nine_species.plot_pressure_diagnostic` are diagnostic only. They keep the nine-species chemistry path visible, record failed loadings explicitly, and should not be treated as the canonical pressure fit.

`MEA/epcsaft_diagnostics.py` and `MEA/epcsaft_present_plots.py` are optional. The default runner skips them when the sibling ePC-SAFT runtime is unavailable.

`analysis/2015_Baygi/` contains the restored Baygi and Pahlavanzadeh markdown plus a small reproduction harness for Table 2/Table 3 parameter summaries and neutral pressure parity plots.

Shared code under `MEA/common/` is limited to neutral workflow infrastructure: paths, dataset loading, report writing, and plot export. Six-species and nine-species chemistry/model code stay in their own subpackages.

## Archive Policy

`archive/` contains historical scripts, old root-level experiments, old duplicate data copies, old fit artifacts, and previous in-repo PC-SAFT fallback code. These files are preserved for reference but are not maintained workflow entrypoints.
