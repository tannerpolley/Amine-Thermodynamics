# Neutral ePC-SAFT Parity

Canonical commands:

`powershell
uv run python analyses\epcsaft_neutral_parity\scripts\generate_data.py
uv run python analyses\epcsaft_neutral_parity\scripts\render_figures.py
`

Curated artifacts live under esults/<plot_set>/ with plotted CSV snapshots, .mpl.yaml style sidecars, PNG previews, and SVG figures.
Disposable solver/run output belongs under ignored esults/runs/.
