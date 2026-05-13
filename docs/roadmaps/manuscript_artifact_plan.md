# Manuscript Artifact Plan

## Main figures

1. Literature/modeling roadmap.
2. Reactive species and model architecture.
3. Modified Born SSM+DS schematic.
4. Data map over temperature, loading, pressure, and MEA weight fraction.
5. Pure MEA vapor pressure and saturated liquid density.
6. Binary neutral validation for MEA–H2O and CO2–H2O.
7. MEAH+/MEACOO- parameter regression movement.
8. MEAH+/MEACOO- speciation parity.
9. MEAH+/MEACOO- loading curves.
10. Full chemical speciation vs CO2 loading.
11. CO2 partial pressure vs loading.
12. CO2 pressure parity.
13. Residuals by loading, temperature, and source.
14. Sensitivity/identifiability.
15. Literature-model comparison.

## Required artifact contract

Each curated figure must include:

- plotted CSV snapshot,
- PNG preview,
- SVG vector file,
- `.mpl.yaml` or equivalent style sidecar,
- caption draft or caption notes,
- source split indicator if data include fit/validation rows.

## Main tables

1. Literature comparison and manuscript gap.
2. Reaction set and equilibrium constants.
3. Experimental data inventory.
4. Pure-component ePC-SAFT parameters.
5. Binary interaction parameters.
6. Regressed MEAH+/MEACOO- parameters.
7. Regression objective and weights.
8. Speciation error metrics.
9. CO2 pressure error metrics.
10. Sensitivity and identifiability status.

## Claim audit

Every manuscript claim must map to one of:

- a table,
- a figure,
- a manifest entry,
- a regression summary,
- a validation command,
- an explicit limitation.

## Current artifact boundary

Current diagnostic artifacts exist for:

- MEAH+/MEACOO- selected-row fit under `analyses/epcsaft_ionic_regression/results/ion_parameter_regression/`.
- Full-ionic pressure and speciation evaluation under `analyses/epcsaft_ionic_regression/results/pressure/` and `analyses/epcsaft_ionic_regression/results/speciation/`.
- Global-regression diagnostics under `analyses/epcsaft_ionic_regression/results/global_regression/`.
- Sensitivity diagnostics under `analyses/epcsaft_ionic_regression/results/sensitivity/`.

Publication-facing final figures must all identify one final parameter artifact. The current selected artifact is `promoted_ionic_fit`; the global pressure/speciation fit did not complete and must not be described as a final globally regressed parameter set.

No roadmap or manuscript text should paste full article text. Extract source data from `docs/papers/md/` into machine-readable files and cite only the extracted data/provenance needed for the claim.
