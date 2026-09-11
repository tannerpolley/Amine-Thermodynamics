# Matched six- and nine-species comparison

**Reproduction limit (8 September 2026 audit):** the retained all-parameter
screening used a historical packet and a temporary local SciPy/Newton
equilibrium layer. That non-portable generator is retired. Future regeneration
needs explicit immutable packet inputs and an Engine-owned equilibrium method.
Its retained sensitivity results are not posterior uncertainty for the current
exploratory incumbent.

This analysis holds the feed, reaction source, temperature/loading coordinate,
and reporting basis fixed while comparing nine explicit species with a six-
species reduction.

## Experiment contract

The ideal lane reads the source-controlled nine-species reaction manifest and
derives the six-species reactions by the exact projection

```text
R6-carbamate   = R2 - R4 - R5
R6-bicarbonate = R2 - R5
```

It solves all unique VLE and ChEq coordinates for 30 wt% MEA in water using
dimensionless ideal true-species activities. The result basis is amount per mol
initial MEA. It does not use the earlier sibling fitting-routine coefficient
file.

The separate ePC-SAFT lane uses the Engine candidate packet for both species
sets and the Engine-side reaction source contract. A disposable SciPy bridge
solves the reaction, balance, and charge equations while the installed Engine
wheel supplies EOS fugacity coefficients, density, source-reference transfer,
and pressure evaluation. This bypasses the Engine reactive declaration gate
only for the temporary equilibrium layer; it does not claim a production API
path.

The ePC-SAFT lane is fixed at 100 kPa and 293.15, 313.15, and 323.15 K. It is
a liquid-composition diagnostic only: no VLE pressure, global-equilibrium,
phase-stability, or parameter-adoption claim is made.

## Retained results

- `results/reaction_coefficients.csv`: ideal nine-species source rows and exact
  derived six-species rows.
- `results/common_species_comparison.csv`: ideal common-species amounts and
  nine-minus-six deltas at every canonical coordinate.
- `results/omitted_species_inventory.csv`: ideal carbonate, hydronium, and
  hydroxide inventory excluded by the six-species set.
- `results/solve_diagnostics.csv`: ideal residual and balance diagnostics.
- `results/epcsaft_scipy_*.csv`: retained temporary Engine/SciPy lane,
  including species values, reaction values, diagnostics, omitted inventory,
  packet identity, and claim boundary.
- `results/corrected_apparent_pressure_*.csv`: full CO2-pressure diagnostic
  using the conserved-total apparent projection.
- `results/corrected_apparent_parameter_sensitivity_screen.csv`: structural
  pressure-only sensitivity screen for provisional reactive/ionic parameters.
- `results/uq_parameter_inventory.csv`: all 143 packet identities, including
  fixed, derived, structurally excluded, and continuous screening records.
- `results/uq_lhc_samples.csv`, `results/uq_global_sensitivity.csv`, and
  `results/uq_uncertainty_summary.csv`: 128-point smart-LHC Engine survey,
  rank-based sensitivity results, and screening-prior propagated intervals.
- `figures/output/`: claim-led common-species and omitted-inventory figure
  bundles with plot-data CSVs and Matplotlib sidecars, including the UQ
  importance, binary-interaction, and output-interval figures.

The working notebook is [`notebook.qmd`](notebook.qmd). It reads retained
results and does not rerun either calculation.

## Commands

```bash
uv run python analyses/enrtl_six_species_ideal_comparison/scripts/generate_data.py
uv run python analyses/enrtl_six_species_ideal_comparison/scripts/generate_corrected_apparent_pressure.py
uv run python analyses/enrtl_six_species_ideal_comparison/scripts/generate_corrected_apparent_sensitivity.py
uv run python analyses/enrtl_six_species_ideal_comparison/scripts/render_figures.py
uv run python analyses/enrtl_six_species_ideal_comparison/scripts/render_uq_figures.py
quarto render analyses/enrtl_six_species_ideal_comparison/notebook.qmd --to html
quarto render analyses/enrtl_six_species_ideal_comparison/notebook.qmd --to pdf
```

The retained UQ run used the candidate-3 packet, seed `20260901`, 113
continuous parameter groups, and the temporary SciPy/Newton reaction-extents
bridge with Engine EOS evaluations. It is historical screening evidence, not a
measurement-backed posterior UQ or a supported regeneration route.

## Corrected pressure result

The corrected projection agrees between six and nine species to
`1.321165e-14`, so the neutral apparent-EOS pressure prediction is identical
for both labels. Across all 161 canonical VLE observations, the retained
neutral `flashTQ` calculation converged only one row; the converged prediction
was 2038.38 kPa for a 0.00202 kPa observation. The remaining rows failed the
neutral flash. This is not an accepted pressure fit: total absorbed carbon
cannot be treated as free molecular CO2 without a reactive bubble model.

Consequently, reaction and internal ionic parameters have structural zero
sensitivity to this corrected pressure observable. They should be excluded
from a pressure-only active fit, while the nine-species model remains the
reference for explicit reactive ePC-SAFT speciation. The existing explicit-ion
sensitivity artifacts are diagnostic scenario studies on older Engine wheels,
not current-packet probabilistic UQ.
