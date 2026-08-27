# Full Ionic ePC-SAFT Regression

Historical results are retained for provenance. New direct ePC-SAFT analysis
and validation is owned by Engine Issue #80. After an immutable packet is
accepted upstream, this directory may replay it and render parameter-agnostic
figures from its retained tables.

Render-only command:

```bash
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py
```

Curated artifacts live under `results/<plot_set>/` with plotted CSV snapshots, `.mpl.yaml` style sidecars, PNG previews, SVG figures, and PDF LaTeX artifacts.
Disposable solver/run output belongs under ignored `results/runs/`.
