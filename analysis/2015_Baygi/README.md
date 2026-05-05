# 2015 Baygi Reproduction Workspace

This folder contains the restored Baygi and Pahlavanzadeh paper markdown and a
small reproduction harness for the first neutral ePC-SAFT migration pass.

The active reproduction target is intentionally limited: preserve the current
six-species MEA chemistry/speciation workflow, collapse to apparent
`CO2/MEA/H2O`, and compare the new neutral ePC-SAFT pressure backend against the
legacy PC-SAFT pressure baseline. Full electrolyte ePC-SAFT regression is out of
scope for this first parity pass.

Run from the repository root:

```powershell
uv run python analysis\2015_Baygi\generate_baygi_tables.py
uv run python analysis\2015_Baygi\plot_baygi_neutral_parity.py
```

Outputs are written to `analysis/2015_Baygi/out/`.

