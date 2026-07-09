# MEA Thermodynamics

MEA-CO2-H2O thermodynamics workflows organized around importable package code in `src/MEA`, reusable reference data in `data/reference`, and durable analysis workspaces in `analyses/<category>/<analysis_id>`.

## Canonical Commands

```bash
uv sync
uv run python scripts/doctor.py
uv run python scripts/validate_project.py quick
uv run python scripts/validate_project.py confidence
uv run python scripts/render_all_plots.py
uv run python scripts/generate_all_analysis_data.py
uv run python analyses/<category>/<analysis_id>/scripts/generate_data.py
uv run python analyses/<category>/<analysis_id>/scripts/render_figures.py
```

`scripts/render_all_plots.py` is the single figure-regeneration command. It only calls analysis-local `render_figures.py` scripts, which read already generated CSV inputs and write curated plot snapshots plus PNG/SVG outputs. `scripts/generate_all_analysis_data.py` refreshes processed CSV/JSON data tables without rendering figures; expensive ionic regeneration is opt-in with `--include-ionic-full` and `--include-expensive`.

Package imports remain `import MEA...`; source lives under `src/MEA`.
Old file-path commands such as `uv run python MEA/run_plot_exports.py` are intentionally not preserved.

## Layout

- `src/MEA/`: importable model, data-loading, ePC-SAFT, and plotting support code.
- `data/reference/MEA/`: reusable MEA VLE and chemical-equilibrium reference tables.
- `data/reference/epcsaft_datasets/`: reusable ePC-SAFT parameter datasets.
- `analyses/paper_validation/2015_baygi/`: Baygi 2015 figure, parameter-table, and neutral parity reproduction.
- `analyses/phase1/six_species_baseline/`: retained six-species PC-SAFT pressure/speciation baseline needed for neutral parity checks.
- `analyses/phase1/neutral_epcsaft_parity/`: neutral apparent-component ePC-SAFT parity artifacts.
- `analyses/phase1/smith_missen_baseline/`: Phase 1 Smith-Missen pressure/speciation baseline.
- `analyses/phase2/activity_epcsaft/`: Phase 2 true-species activity-based ePC-SAFT evaluation.
- `analyses/phase3/ionic_epcsaft_regression/`: full ionic ePC-SAFT regression, pressure, and speciation artifacts.
- `docs/latex/`: writable manuscript source mirrored from the separate Overleaf Git checkout.
- `scripts/`: root doctor, validation, and plot orchestration entrypoints.

The removed nine-species/Gekko diagnostic workflow remains available on `legacy/main-legacy`; it is not part of active `main` validation.

Each analysis owns local `data/raw/`, `data/processed/`, and `results/<plot_set>/` folders. Curated plot sets keep the exact plotted CSV snapshot, `.mpl.yaml` style sidecar, PNG preview, and SVG figure together. Disposable run output belongs under ignored `analyses/**/results/runs/`.

## Key Artifact Paths

- `analyses/phase1/six_species_baseline/results/pressure/legacy_pcsaft_jou_recomputed_fit.png`
- `analyses/phase1/six_species_baseline/results/pressure/legacy_pcsaft_jou_recomputed_fit.svg`
- `analyses/phase1/six_species_baseline/results/speciation/speciation.png`
- `analyses/phase1/neutral_epcsaft_parity/results/pressure/epcsaft_neutral_pcsaft_parity.png`
- `analyses/phase3/ionic_epcsaft_regression/results/pressure/ionic_epcsaft_co2_pressure.png`
- `analyses/phase3/ionic_epcsaft_regression/results/speciation/ionic_epcsaft_speciation_activity.png`
- `analyses/paper_validation/2015_baygi/results/neutral_parity/baygi_neutral_epcsaft_pcsaft_pressure_parity.png`

## Manuscript

The article draft source lives under `docs/latex/`. It is a normal folder in this repo, not a submodule. Set `MEA_OVERLEAF_MIRROR` to the absolute path of the independent Overleaf-connected mirror checkout.

Build the local manuscript with:

```bash
cd docs/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Sync the local manuscript source back to the Overleaf mirror with:

```bash
bash docs/latex/scripts/sync_to_overleaf_mirror.sh
```

## Model Boundaries

The active package-centered path is the full ionic ePC-SAFT workflow. The neutral ePC-SAFT workflow checks apparent `CO2/MEA/H2O` parity against the retained six-species baseline. The removed nine-species/Gekko workflow was diagnostic-only legacy material and is preserved on `legacy/main-legacy`.
