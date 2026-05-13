# MEA-Thermodynamics Handoff

## Current Architecture

The repo has been cut over to the cross-project architecture standard:

- Importable code lives in `src/MEA`.
- Reusable source data lives in `data/reference`.
- Durable workflows live in separate `analyses/<analysis_id>` folders.
- Curated plot artifacts live in `analyses/<analysis_id>/results/<plot_set>/`.
- Manuscript source lives in `docs/latex` as a normal writable folder, not a submodule.
- Top-level `out/` is no longer a canonical tracked output location.

## Canonical Commands

```powershell
uv sync
uv run python scripts\doctor.py
uv run python scripts\validate_project.py quick
uv run python scripts\validate_project.py confidence
uv run python scripts\render_all_plots.py
uv run python scripts\generate_all_analysis_data.py
uv run python analyses\<analysis_id>\scripts\generate_data.py
uv run python analyses\<analysis_id>\scripts\render_figures.py
```

`scripts\render_all_plots.py` is the canonical single command for regenerating all curated figures from existing processed CSVs. It must stay render-only. `scripts\generate_all_analysis_data.py` is the separate data-refresh orchestrator; its default path avoids full ionic regeneration, while `--include-ionic-full` and `--include-expensive` explicitly opt into slow recomputation.

Old path commands such as `uv run python MEA\run_plot_exports.py` were deliberately removed.

## Analysis Ownership

- `analyses/six_species_legacy`: retained six-species PC-SAFT pressure/speciation baseline for neutral parity checks.
- `analyses/epcsaft_neutral_parity`: neutral apparent-component ePC-SAFT parity.
- `analyses/epcsaft_ionic_regression`: full ionic ePC-SAFT regression, pressure, and speciation.
- `analyses/2015_baygi`: Baygi 2015 parameter and neutral parity reproduction.

The nine-species/Gekko diagnostic workflow was removed from active `main`. It remains on `legacy/main-legacy` with its code, tests, and old artifacts under `out/plots/MEA/nine_species` and `out/legacy_baseline/all_species_*`.

Each plot set should contain its plotted CSV snapshot, `.mpl.yaml`, PNG, and SVG.

## Manuscript

The active article draft is `docs/latex/main.tex`. The separate Overleaf-connected checkout is still `C:\Users\Tanner\Documents\git\LaTeX-Projects\MEA-Thermodynamics-LaTeX`; keep it as a separate Git repo and sync from `docs/latex` with `docs\latex\sync_to_overleaf_mirror.ps1`.

Build check:

```powershell
cd docs\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Current draft scope: full-ionic ePC-SAFT workflow, literature context, data basis, six-species baseline, neutral parity, ionic pressure/speciation figures, and an explicit note that the current parameter artifact is regression-ready rather than a converged final optimum.

## Plot Style

`src/MEA/common/plot_style.py` is the shared style contract for Jou temperature colors and pressure plot line styles.

## Current Scientific Boundaries

The active ePC-SAFT-centered workflow is `analyses/epcsaft_ionic_regression`, which exercises the full true-species reactive electrolyte package path. `analyses/epcsaft_neutral_parity` is apparent-component parity. The six-species workflow is retained only as the small legacy baseline needed by neutral parity/Baygi reproduction.

The current regression-completion handoff for another downstream/upstream Codex agent is `docs/ePC-SAFT/mea-ionic-regression-completion-handoff.md`.
The MEAH+/MEACOO- real-data regression data contract is `docs/ePC-SAFT/meah-meacoo-real-data-regression-plan.md`, with a machine-readable source manifest at `data/reference/MEA/ion_parameter_regression_sources.csv`.

## Validation

Use `uv run python scripts\validate_project.py quick` for compile/import/unit checks. Use `uv run python scripts\validate_project.py confidence` to also regenerate representative curated plot sets and verify the artifact contract.
