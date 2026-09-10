# Neutral PC-SAFT Pressure Reference

Render retained results:

```bash
uv run python analyses/neutral_pcsaft_pressure_reference/scripts/render_figures.py
```

Curated artifacts live under `results/<plot_set>/` with plotted CSV snapshots, `.mpl.yaml` style sidecars, PNG previews, SVG figures, and PDF LaTeX artifacts.
Disposable solver/run output belongs under ignored `results/runs/`.

The historical numerical generator was retired. These commands render retained
tables only; they do not regenerate or adopt an ePC-SAFT parameter set. If a
required table is missing, recover its exact retained version rather than
following a renderer hint to the deleted generator.
