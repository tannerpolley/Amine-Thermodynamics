# Baygi 2015 Neutral Parity

Reproduction workflow for the Baygi and Pahlavanzadeh parameter tables and neutral ePC-SAFT parity.

```bash
uv run python analyses/paper_validation/2015_baygi/scripts/render_figures.py
```

Stable inputs are in `data/input_baygi_2015.md`, reproduced tables are in
`data/processed/`, and the exact plotted-data and rendered validation bundle is in
`results/neutral_parity/`.

The historical numerical generator was retired. These commands render retained
tables only; they do not regenerate or adopt an ePC-SAFT parameter set. If a
required table is missing, recover its exact retained version rather than
following a renderer hint to the deleted generator.
