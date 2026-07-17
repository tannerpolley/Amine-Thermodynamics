# Model–Data Summary Figures Design

## Purpose

Create two publication-quality, scientifically distinct figure bundles:

1. a compact Phase 2 summary of fixed activity-based ePC-SAFT predictions against experimental pressure and speciation observations; and
2. a PR #27 diagnostic comparing the clean-provider reactive solver with the pinned ePC-SAFT 1.5.2 model lane and reporting its evaluation cost.

The first figure is a candidate manuscript summary. The second remains analysis-only unless the manuscript later needs an implementation-parity discussion. No manuscript source changes are in scope until the rendered figures are reviewed.

## Scientific Claim Boundaries

- Label literature measurements as experimental data.
- Label the PR #27 pinned lane as a model reference, never as data or experiment.
- Preserve the Phase 2 fixed-parameter evaluation boundary; the figure must not imply a completed coupled pressure/speciation regression.
- Preserve the PR #27 diagnostic boundary: it does not admit regression execution or parameter promotion.
- Plot only solver-accepted model states and eligible measured targets. Do not silently promote upper bounds or balance-inferred context rows to measured residual evidence.

## Figure 1: Fixed Activity Model Versus Experiment

Create `model_experiment_parity` under:

`analyses/phase2/activity_epcsaft/figures/model_data_summary/`

Use a two-panel log–log parity layout:

- **Panel (a), pressure:** observed versus predicted CO2 partial pressure for accepted rows from `phase2_pressure_results.csv`. Color points by temperature and retain literature source in the plotted-data snapshot.
- **Panel (b), speciation:** observed versus predicted true-species mole fraction for accepted `direct_positive` and `aggregate_direct_positive` targets from `phase2_equilibrium_results.csv`. Color and marker-code points by species.

Both panels include a one-to-one line and subtle factor-of-ten guides. The guides describe model/data ratios, not uncertainty. Axes must state units or dimensionless basis explicitly.

## Figure 2: Clean-Provider Reactive Diagnostic

Create `reactive_speciation_provider_parity` under:

`analyses/phase3/reactive_speciation_feasibility/figures/provider_parity/`

Use three panels sourced only from the tracked PR #27 receipt and its pinned reference:

- **Panel (a), composition parity:** clean-provider nominal mole fractions versus pinned-model mole fractions at loadings 0.2, 0.4, and 0.6, on log–log axes with species-coded markers and a one-to-one line.
- **Panel (b), signed composition difference:** a species-by-loading heatmap of `x_clean - x_pinned` with a symmetric-log color normalization and zero-centered palette.
- **Panel (c), evaluation cost:** public EOS evaluations versus loading, with nominal elapsed time annotated at each point.

The title and sidecar description must say “model-reference diagnostic.” The pinned lane must not be presented as experimental truth.

## Data And Rendering Flow

Each figure owns two small scripts:

1. `scripts/generate_data.py` reads existing tracked result tables or receipts, validates eligibility and finiteness, and writes the exact long-form plotted-data CSV under `output/`.
2. `scripts/render_figure.py` reads only that plotted snapshot and writes same-stem PNG, SVG, PDF, and `.mpl.yaml` artifacts under `output/`.

Use existing `MEA.common.plot_style` helpers and species styling. Add both renderers to the repository render-only orchestration, add the cheap snapshot generators to data orchestration, register the SVGs in `.mplgallery/manifest.yaml`, and list the new outputs in the owning analysis metadata. Do not rerun the PR #27 EOS experiment during rendering.

## Failure Handling

Fail closed when required columns, receipt sections, accepted states, or eligible targets are missing; when parity values are nonfinite or nonpositive; or when a plotted snapshot is empty. Include row identifiers, source, temperature, loading, species, target role, and comparison role in snapshots so every point remains traceable.

## Verification

- Run both snapshot generators and renderers.
- Inspect the PNG and SVG outputs for labels, scales, legends, overlap, and claim-boundary wording.
- Run targeted Ruff checks and the project confidence validation.
- Rerun rendering and confirm byte-deterministic outputs.
- Add no persistent pytest tests unless implementation reveals a distinct numerical claim not already protected by the project validation commands.

## Review Decision After Rendering

Show both PNG previews in chat. Recommend manuscript inclusion only for the experimental parity summary if it adds interpretive value beyond the existing loading-resolved figures. Keep the PR #27 diagnostic in the analysis archive unless the paper explicitly discusses provider migration, parity, or computational feasibility.
