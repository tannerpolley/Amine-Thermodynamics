# Controlled Model Comparison Figure Design

## Purpose

Add a submission-facing figure that makes the controlled Phase 1/Phase 2 pressure comparison visually auditable. The figure must use the same 31 Jou1995 records as the generated comparison metrics and must not recompute either thermodynamic model.

## Selected Design

Use one two-panel diagnostic figure:

1. **Observed-versus-predicted parity.** Plot observed pressure on the horizontal axis and predicted pressure on the vertical axis, both on logarithmic scales. Show the ideal Smith--Missen predictions as open circles and the fixed activity-based ePC-SAFT predictions as filled triangles. Include a one-to-one reference line.
2. **Paired absolute-residual comparison.** Plot each record's ideal absolute \(\log_{10}(P_\mathrm{model}/P_\mathrm{data})\) residual on the horizontal axis and its activity-model absolute residual on the vertical axis. Include a one-to-one reference line. Distinguish improved and worsened records with both marker shape and color, and annotate the aggregate result of 4 improved and 27 worsened records.

The second panel places improved activity-model predictions below the one-to-one line and worsened predictions above it. This is more direct than overlaid pressure curves and less cluttered than a 31-row dumbbell chart.

## Data Flow

The renderer reads only:

`analyses/phase2/activity_epcsaft/results/controlled_comparison/paired_pressure_rows.csv`

It validates the required columns, accepted paired-row status, positive finite pressures, finite residuals, and the expected comparison labels. It then writes an exact plotted-data snapshot beside the rendered files. Model calculation remains owned by the Phase 1 and Phase 2 data generators.

## Output Contract

Create a figure-owned bundle under:

`analyses/phase2/activity_epcsaft/figures/controlled_comparison/output/`

The bundle contains:

- `controlled_pressure_comparison.png`
- `controlled_pressure_comparison.svg`
- `controlled_pressure_comparison.pdf`
- `controlled_pressure_comparison_plot_data.csv`
- `controlled_pressure_comparison.mpl.yaml`

The SVG is registered in the root `.mplgallery/manifest.yaml`. The PDF is copied to `docs/latex/figures/` for manuscript inclusion.

## Figure Semantics

- Axes state variables and pressure units explicitly.
- Pressure parity uses logarithmic axes because the measurements span orders of magnitude.
- Residual parity uses linear axes because both quantities are nonnegative log-ratio magnitudes over a compact range.
- Marker shapes as well as color communicate model and improvement status.
- The figure reports no uncertainty intervals because the canonical VLE rows contain no pressure uncertainties.
- The caption describes this as a fixed-parameter, same-record evaluation and does not generalize the result beyond the tested parameterization.

## Repository Integration

- Add a focused renderer under the controlled-comparison figure directory.
- Invoke it from the Phase 2 render entry point so `scripts/render_all_plots.py` retains complete figure ownership.
- Add the figure bundle and manifest entry to repository validation.
- Place the figure immediately after the controlled pressure-comparison discussion in the Results and Discussion section.
- Preserve the existing activity-only pressure figure because it communicates six-source coverage rather than the same-record comparison.

## Failure Behavior

Rendering fails with a clear error when required columns are missing, paired rows are rejected, pressures are nonpositive or nonfinite, residuals are nonfinite, or the improvement counts disagree with the saved comparison evidence. No rows are silently dropped.

## Test Strategy

Use test-first development:

1. Add a failing test for conversion of the paired table into validated plotted data and the expected 4/27 classification.
2. Add failing project-structure assertions for the complete figure bundle and MPLGallery registration.
3. Add a failing manuscript-integrity assertion requiring the PDF include and bounded caption.
4. Implement the minimal renderer and integration.
5. Regenerate twice and confirm deterministic output.
6. Run focused tests, the render-all-plots command, manuscript build, project validation, and visual inspection of PNG/PDF output.

## Acceptance Criteria

- The plotted-data snapshot contains exactly the 31 accepted paired Jou1995 records.
- Panel A shows both models against the same observations with a one-to-one line.
- Panel B independently reproduces 4 improved and 27 worsened activity predictions.
- PNG, SVG, PDF, plotted CSV, and sidecar are present and deterministic.
- MPLGallery and manuscript references resolve to the retained bundle.
- The manuscript builds without layout defects or claims beyond the fixed parameter set and tested records.
