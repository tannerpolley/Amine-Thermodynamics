# MEA Thermodynamics

Legacy and diagnostic workflows for the `CO2-MEA-H2O` thermodynamic system.

The active project is organized around two separate legacy ecosystems:

- `MEA.six_species`: canonical six-species MEA speciation and Jou CO2 vapor-pressure baseline
- `MEA.nine_species`: diagnostic nine-species chemistry and pressure workflow

Older scripts and data copies live under `archive/` for reference only.

## Setup

This repository is uv-based and targets Python 3.13.

Required sibling repositories:

- `C:\Users\Tanner\Documents\git\PC-SAFT`
- `C:\Users\Tanner\Documents\git\ePC-SAFT` for optional ePC-SAFT diagnostics
- `C:\Users\Tanner\Documents\git\LaTeX-Projects\MEA-Thermodynamics-LaTeX` for the external LaTeX paper checkout

From this repo:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
uv sync
```

The legacy pressure workflow requires the local `pcsaft` package from `../PC-SAFT`. If that package is missing, the pressure scripts fail with setup instructions instead of using an old in-repo fallback copy.

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
uv run python -m MEA.nine_species.plot_speciation_diagnostic
uv run python -m MEA.nine_species.plot_pressure_diagnostic
```

## Active Outputs

Canonical plot artifacts are committed only for the active workflow:

- `out/plots/MEA/six_species/speciation/speciation.png`
- `out/plots/MEA/six_species/pressure/legacy_pcsaft_jou_recomputed_fit.png`
- `out/plots/MEA/nine_species/speciation_diagnostic/speciation_diagnostic.png`
- `out/plots/MEA/nine_species/pressure_diagnostic/co2_partial_pressure.png`

Canonical evidence files live under:

- `out/legacy_baseline/`
- `out/plots/MEA/nine_species/speciation_diagnostic/`
- `out/plots/MEA/nine_species/pressure_diagnostic/`

## Model Roles

`MEA.six_species.plot_speciation` is the canonical legacy speciation plot. It uses the six-species solver in `MEA.six_species.chemistry` and overlays the available 40 C, 30 wt% MEA speciation data.

`MEA.six_species.plot_pressure` is the canonical Jou vapor-pressure gate. It uses six-species legacy chemistry collapsed to apparent `CO2/MEA/H2O` and verifies the expected median absolute `log10(model/data)` pressure errors.

`MEA.nine_species.plot_speciation_diagnostic` and `MEA.nine_species.plot_pressure_diagnostic` are diagnostic only. They keep the nine-species chemistry path visible, record failed loadings explicitly, and should not be treated as the canonical pressure fit.

`MEA/epcsaft_diagnostics.py` and `MEA/epcsaft_present_plots.py` are optional. The default runner skips them when the sibling ePC-SAFT runtime is unavailable.

Shared code under `MEA/common/` is limited to neutral workflow infrastructure: paths, dataset loading, report writing, and plot export. Six-species and nine-species chemistry/model code stay in their own subpackages.

## Archive Policy

`archive/` contains historical scripts, old root-level experiments, old duplicate data copies, old fit artifacts, and previous in-repo PC-SAFT fallback code. These files are preserved for reference but are not maintained workflow entrypoints.
