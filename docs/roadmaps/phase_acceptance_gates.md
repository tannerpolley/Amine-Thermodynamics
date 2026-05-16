# Phase Acceptance Gates

## Phase 1 — Smith–Missen-style reproduction baseline

Required:

- pure CO2/MEA/H2O parameter provenance,
- MEA association scheme documented,
- MEA–H2O binary parameter documented,
- reaction constants listed with convention,
- ideal/apparent speciation runs reproducibly,
- CO2 pressure/speciation plots generated,
- limitations explicit.

Allowed current claim:

> explicit ideal Smith-Missen major-species speciation baseline, with pressure and trace-species limits.

Forbidden claim:

> final true-species ePC-SAFT activity-based MEA model.

Current status:

- The speciation workflow solves the explicit five-reaction, nine-species ideal Smith-Missen system and passes major observed species gates.
- Pressure rows and trace/unobserved species remain limited by the residual audit.
- The consolidated Phase 1 workflow now lives under `analyses/phase1_smith_missen_baseline/`.
- Provenance and convention audits are captured in `data/reference/MEA/manifests/phase1_data_inventory.csv`, `data/reference/MEA/manifests/phase1_parameter_provenance.csv`, and `data/reference/MEA/manifests/reaction_constant_manifest.csv`.
- Phase 1 claims must stay aligned with `analyses/phase1_smith_missen_baseline/results/phase1_residual_acceptance_audit.csv`.

## Phase 2 — Activity-based ePC-SAFT speciation and VLE

Required:

- reaction constant conventions explicit,
- activity-based speciation enabled where constants support it,
- VLE/fugacity-equilibrium route documented,
- pressure/speciation outputs generated from one parameter artifact,
- unsupported ePC-SAFT package paths listed as package dependencies.

Allowed current claim:

> true-species ePC-SAFT activity-equilibrium model run with residual-gated pressure/speciation claims.

Forbidden claim:

> finalized joint-regression result.

Current status:

- Native Phase 2 equilibrium, pressure, solver-diagnostic, residual-audit, and activity-curve artifacts exist under `analyses/phase2_activity_epcsaft/results/`.
- Wong 2015 high-pressure Raman data are present as Markdown and must be extracted before being used as validation.
- Phase 2 solver run status is `model_ran_success`; target-role residual audit rows control validation/manuscript claims but do not revise model-run status.

## Phase 3 — Coupled regression mode

Required:

- regression problem JSON,
- fit result JSON,
- parameter movement table,
- active-bound table,
- source-stratified residuals,
- target-family residuals,
- pressure and speciation generated from same final parameter artifact,
- identifiability notes.

Allowed claim:

> coupled pressure/speciation regression with newly regressed parameters.

Only if all Phase 3 artifacts exist.

Forbidden claim:

> final globally regressed parameter set.

If global fitting was skipped, returned a specific nonconverged package status, or used inconsistent pressure/speciation artifacts.

Current status:

- Not accepted.
- `analyses/epcsaft_ionic_regression/results/global_regression/global_regression_summary.json` reports a nonpromoted package-native candidate with `attempted_optimization=false` and `selected_parameter_set=promoted_ionic_fit`.
- Phase 3 remains blocked until generic ePC-SAFT regression support can complete the coupled objective and emit the required artifacts.
- The configured local dev dependency path is currently missing; before reattempting Phase 3, restore or repin `epcsaft`, then run `uv sync`, `uv run python scripts/check_epcsaft_integration.py --mode dev`, and `uv run python scripts/check_epcsaft_integration.py --mode final`.
