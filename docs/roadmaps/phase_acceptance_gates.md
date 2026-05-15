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

> retained ideal/apparent-speciation baseline audit.

Forbidden claim:

> final true-species ePC-SAFT activity-based MEA model.

Current status:

- Generated for a retained-baseline audit; not validated as an independent Phase 1 reproduction.
- The consolidated Phase 1 workflow now lives under `analyses/phase1_smith_missen_baseline/`.
- Provenance and convention audits are captured in `data/reference/MEA/manifests/phase1_data_inventory.csv`, `data/reference/MEA/manifests/phase1_parameter_provenance.csv`, and `data/reference/MEA/manifests/reaction_constant_manifest.csv`.
- This PR must not close the Phase 1 validation gate until residual and source gates allow it.

## Phase 2 — Activity-based ePC-SAFT speciation and VLE

Required:

- reaction constant conventions explicit,
- activity-based speciation enabled where constants support it,
- VLE/fugacity-equilibrium route documented,
- pressure/speciation outputs generated from one parameter artifact,
- unsupported ePC-SAFT package paths listed as package dependencies.

Allowed current claim:

> true-species ePC-SAFT problem-definition scaffold.

Forbidden claim:

> finalized joint-regression result.

Current status:

- Diagnostic artifacts exist for full-ionic pressure and speciation using `promoted_ionic_fit`.
- Wong 2015 high-pressure Raman data are present as Markdown and must be extracted before being used as validation.
- Phase 2 equilibrium and residual artifacts remain blocked until upstream issue #115 and the residual gates pass.

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
