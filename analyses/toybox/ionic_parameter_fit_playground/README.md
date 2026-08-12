# Ionic Parameter-Fit Playground

## Status

**Exploratory only. Not a manuscript input. Not a promoted parameter source.**

This folder preserves two experiments from the legacy playground branch
`codex/manuscript-parameter-fit-provenance`. They were useful while the unified
ePC-SAFT regression path was unavailable, but they do not satisfy the current
Engine-owned regression, immutable-data, uncertainty, or promotion contracts.

The source snapshots came from:

- `58660ed9a051d701fb9295f97cd71d86adcb984a`: historical seven-parameter fit;
- `aaa638427f50fbd63acb90de54c9ee94186d8b02`: pressure-qualified shared-ion-size experiment.

The manuscript edits from that branch are intentionally excluded.

## Experiments

### Historical seven-parameter snapshot

`results/historical_seven_parameter_fit/` records a legacy ePC-SAFT 1.5.2
SciPy fit of seven MEAH+/MEACOO- coordinates to eight NMR states and 22
composition residuals. The residual norm changed from 0.27144 to 0.26766.
The producing implementation and a complete immutable run receipt are not
present, so these files are historical sensitivity evidence only.

### Shared-ion-size SciPy experiment

`scripts/run_shared_ion_size_scipy_experiment.py` fits one shared effective
segment diameter for MEAH+ and MEACOO-. The fitted coordinate is in angstrom;
density targets are evaluated in kg/m3, speciation targets on mole-fraction
bases, and pressure qualification in kPa.

The retained run found a shared diameter of 5.334530692 angstrom. Density
relative RMSE improved from 13.75% to 2.49% in training and from 12.79% to
2.40% in reserved validation. The pressure qualification failed: median
absolute log10 pressure error increased from 0.432 to 0.869 for active rows
and from 0.542 to 0.730 for reserved rows, with one rejected state in each
role. The experiment therefore demonstrated that a density/speciation-only
ion-size fit can degrade reactive pressure predictions.

The preserved pressure CSV is the exact historical output. Its legacy bubble
path used the default 30 wt% apparent totals for its 15, 17, 40, and 45 wt%
rows, so the cross-concentration reserved-pressure metric is not a quantitative
validation result. The active 30 wt% pressure degradation remains a useful
warning, and current reruns propagate each row's MEA mass fraction correctly.

The script uses finite differences and assigns failed trial states a heuristic
optimizer score of 8. That score is not a thermodynamic residual. Final failed
states reject a toy candidate, but the method is not admissible for production
regression.

## Running the toy experiment

The script depends on legacy downstream MEA model interfaces and may fail as
the unified Engine integration evolves. Run it only to explore or reproduce
the historical design question:

```bash
.venv/bin/python analyses/toybox/ionic_parameter_fit_playground/scripts/run_shared_ion_size_scipy_experiment.py \
  --confirm-toybox --max-nfev 12
```

Use `--skip-pressure` only for iteration; a run without pressure qualification
cannot establish even the toy experiment's rejection or acceptance result.
New runs write to the ignored `results/runs/shared_ion_size_scipy/` directory;
they do not overwrite the retained branch snapshots.

## Promotion boundary

Values and outputs in this directory must not be copied into `docs/latex`,
canonical parameter bundles, readiness receipts, or production result tables.
The current governed path remains the staged reactive-VLE plan under
`docs/roadmaps/predictive_reactive_vle_regression.md`.
