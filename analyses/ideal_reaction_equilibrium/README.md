# Ideal Reaction-Equilibrium Reference

This analysis curates ideal reaction-equilibrium manuscript evidence. It consumes
the six-species and neutral-pressure reference results, adds source-aligned speciation comparisons,
and produces the pressure and ideal-activity speciation figures used by the paper.

```bash
uv run python analyses/ideal_reaction_equilibrium/scripts/generate_data.py
uv run python analyses/ideal_reaction_equilibrium/scripts/render_figures.py
```

Canonical calculation tables live in `results/`. Each directory under `figures/`
owns its source manifest, exact plotted-data subset, rendered PNG/SVG/PDF bundle,
and `.mpl.yaml` lineage sidecar. Figure directories do not mirror whole calculation
tables.
