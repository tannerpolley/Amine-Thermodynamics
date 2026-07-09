# Neutral ePC-SAFT Parity

Canonical commands:

```bash
uv run python analyses/phase1/neutral_epcsaft_parity/scripts/generate_data.py
uv run python analyses/phase1/neutral_epcsaft_parity/scripts/render_figures.py
```

Curated artifacts live under `results/<plot_set>/` with plotted CSV snapshots, `.mpl.yaml` style sidecars, PNG previews, SVG figures, and PDF LaTeX artifacts.
Disposable solver/run output belongs under ignored `results/runs/`.
