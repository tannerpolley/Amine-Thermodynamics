# Historical MEA neutral qualification

This analysis preserves the source-backed Cai (1996) MEA--water comparison for
the Held-water 2B, 3B, and 4C MEA association families. The exact comparison
table and plotted rows remain under `results/figures/`.

The earlier calculation favored 3B for pressure-level transfer, but that
result is historical diagnostic evidence, not an active neutral parameter
candidate. Superseded Cai/Baygi fits and the obsolete GREPE Gate 0 result were
removed.

The retained renderer reads existing tables and does not run thermodynamics:

```bash
uv run python analyses/reactive_epcsaft_parameter_evidence/pressure_first/scripts/render_figures.py
```

A future calculation must use a generic method built and debugged upstream,
the pinned installed Engine wheel, and an accepted immutable parameter packet;
it may be reproduced directly in this repository against MEA-owned evidence.
