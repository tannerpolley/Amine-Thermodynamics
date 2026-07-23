# Canonical Speciation Sources

This analysis renders data-only speciation plots from the canonical combined MEA
chemical-equilibrium dataset:

`data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv`

The plots intentionally separate basis families:

- Böttinger, Jakobsen, and Matin rows reported as liquid mole fractions.
- The same mole-fraction rows converted to mol/kg loaded solution by the
  canonical dataset generator.
- Wong Raman rows reported as source-basis mol/kg.

Run:

```bash
uv run python analyses/phase2/canonical_speciation_sources/scripts/generate_data.py
uv run python analyses/phase2/canonical_speciation_sources/scripts/render_figures.py
```
