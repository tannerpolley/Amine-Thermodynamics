# Analysis Workflows

This directory contains source-controlled scientific analysis, validation, and figure workflows. Runtime package code belongs under `src/MEA`; reusable literature and parameter inputs belong under `data/reference`; analysis-specific generated snapshots stay with the analysis that owns them.

```text
analyses/
  paper_validation/
    2015_baygi/
  phase1/
    six_species_baseline/
    neutral_epcsaft_parity/
    smith_missen_baseline/
  phase2/
    activity_epcsaft/
    canonical_speciation_sources/
  phase3/
    ionic_epcsaft_regression/
```

`paper_validation/` is reserved for paper-matching reproduction work: figures, tables, and parameters should be recreated to match the cited paper artifact as directly as possible. The phase folders are project-stage analyses: Phase 1 keeps retained neutral and Smith-Missen baselines, Phase 2 keeps activity-based true-species ePC-SAFT evaluation, and Phase 3 keeps full ionic ePC-SAFT regression and diagnostics.

Each analysis should remain self-contained:

```text
analyses/<category>/<analysis_id>/
  README.md
  analysis.yaml
  data/
    processed/
  figures/
    <figure_id>/
      input/
      output/
      scripts/
  results/
  scripts/
```

Only create optional folders when the analysis needs them. Curated Matplotlib plot bundles keep the plotted CSV snapshot, `.mpl.yaml` sidecar, PNG preview, SVG figure, and PDF artifact together in the owning figure or result folder. Disposable run output belongs under ignored `results/runs/`.
