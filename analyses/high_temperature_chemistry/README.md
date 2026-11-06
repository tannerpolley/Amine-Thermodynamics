# High-temperature MEA chemistry (#263)

Read [the notebook](notebook.qmd) for the scientific result and its limits.
The Forgejo issue owns the calculation design; this folder owns source
assessment, immutable inputs, retained calculations and presentation.

The owner authorized merged Engine e6dae5c7 only for this issue, wheel SHA-256
`83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6`.
Use the issue worktree's environment; normal project `uv run` would select the
main checkout's older pin. From the repository root:

```bash
PYTHONPATH=src agent-heavy uv run --no-project --python .venv/bin/python analyses/high_temperature_chemistry/qualify.py
PYTHONPATH=src agent-heavy uv run --no-project --python .venv/bin/python analyses/high_temperature_chemistry/run.py baseline
PYTHONPATH=src agent-heavy uv run --no-project --python .venv/bin/python analyses/high_temperature_chemistry/run.py hamborg
PYTHONPATH=src agent-heavy uv run --no-project --python .venv/bin/python analyses/high_temperature_chemistry/run.py all-five
PYTHONPATH=src agent-heavy uv run --no-project --python .venv/bin/python analyses/high_temperature_chemistry/run.py holdout
PYTHONPATH=src agent-heavy uv run --no-project --python .venv/bin/python analyses/high_temperature_chemistry/check_heat_domain.py
agent-heavy uv run --no-project --python .venv/bin/python analyses/high_temperature_chemistry/present.py
```

The main EOS parameter record and all 307 original objective rows remain
unchanged. R4/R5 completed laws in the fit results are probe results, not adopted
parameters. `comparison-inputs.json` records the 159 pressure observations and
five NMR states, plus their original source hashes. `environment.json` records
the actual packages used. Every numerical result JSON records the Engine wheel
SHA. The presentation command reads retained values and calls no model.

Pressure values in `state-targets.csv` and the native observations are both Pa;
no factor of 1000 belongs in the baseline pressure reproduction check. NMR
loading coordinates are read from the retained source coordinates (0.064,
0.141, 0.245, 0.336, 0.398), rather than ratios of numerically seeded species
feeds. These statements distinguish the physical quantities from numerical
initial guesses and source display conventions.

The notebook is rendered separately to honor the prohibition on modifying
`analyses/_cse-manuscript.json`. Neither site membership, manuscript text,
parameter adoption nor a global phase-stability search is part of this change.
