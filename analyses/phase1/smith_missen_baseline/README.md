# Phase 1 Smith-Missen Baseline

This analysis curates the Phase 1 manuscript evidence. It consumes the canonical
six-species and neutral-parity results, adds source-aligned speciation comparisons,
and produces the pressure and ideal-activity speciation figures used by the paper.

```bash
uv run python analyses/phase1/smith_missen_baseline/scripts/generate_data.py
uv run python analyses/phase1/smith_missen_baseline/scripts/render_figures.py
```

Canonical calculation tables live in `results/`. Each directory under `figures/`
owns its source manifest, exact plotted-data subset, rendered PNG/SVG/PDF bundle,
and `.mpl.yaml` lineage sidecar. Figure directories do not mirror whole calculation
tables.
