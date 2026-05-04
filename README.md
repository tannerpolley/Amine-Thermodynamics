# MEA Thermodynamics

Legacy and diagnostic workflows for the `CO2-MEA-H2O` thermodynamic system.

The active project is organized around one canonical legacy workflow:

- six-species MEA speciation
- legacy PC-SAFT Jou CO2 vapor-pressure baseline
- all-species chemistry and pressure diagnostics

Older scripts and data copies live under `archive/` for reference only.

## Setup

This repository is uv-based and targets Python 3.13.

Required sibling repositories:

- `C:\Users\Tanner\Documents\git\PC-SAFT`
- `C:\Users\Tanner\Documents\git\ePC-SAFT` for optional ePC-SAFT diagnostics

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
uv run python MEA\legacy_all_species_sweep_check.py
```

## Active Outputs

Canonical plot artifacts are committed only for the active workflow:

- `out/plots/MEA/plot_legacy_speciation/plot_legacy_speciation.png`
- `out/plots/MEA/plot_legacy_pressure/legacy_pcsaft_jou_recomputed_fit.png`
- `out/plots/MEA/plot_all_species_diagnostic/plot_all_species_diagnostic.png`
- `out/plots/MEA/plot_all_species_pressure_diagnostic/co2_partial_pressure.png`

Canonical evidence files live under:

- `out/legacy_baseline/`
- `out/plots/MEA/plot_all_species_diagnostic/`
- `out/plots/MEA/plot_all_species_pressure_diagnostic/`

## Model Roles

`MEA/plot_legacy_speciation.py` is the canonical legacy speciation plot. It uses the shared six-species solver in `MEA/legacy_chemical_equilibrium.py` and overlays the available 40 C, 30 wt% MEA speciation data.

`MEA/plot_legacy_pressure.py` is the canonical Jou vapor-pressure gate. It uses six-species legacy chemistry collapsed to apparent `CO2/MEA/H2O` and verifies the expected median absolute `log10(model/data)` pressure errors.

`MEA/plot_all_species_diagnostic.py` and `MEA/plot_all_species_pressure_diagnostic.py` are diagnostic only. They keep the nine-species chemistry path visible, record failed loadings explicitly, and should not be treated as the canonical pressure fit.

`MEA/epcsaft_diagnostics.py` and `MEA/epcsaft_present_plots.py` are optional. The default runner skips them when the sibling ePC-SAFT runtime is unavailable.

## Archive Policy

`archive/` contains historical scripts, old root-level experiments, old duplicate data copies, old fit artifacts, and previous in-repo PC-SAFT fallback code. These files are preserved for reference but are not maintained workflow entrypoints.
