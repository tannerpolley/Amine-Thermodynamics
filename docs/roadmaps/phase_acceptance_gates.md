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

Allowed claim:

> ideal/apparent-speciation reproduction baseline.

Forbidden claim:

> final true-species ePC-SAFT activity-based MEA model.

Current status:

- Partially available through the retained six-species and neutral-parity workflows.
- Not yet publication-final until source/parameter provenance, reaction-constant conventions, and figure artifact mapping are audited against the 15-figure plan.

## Phase 2 — Activity-based ePC-SAFT speciation and VLE

Required:

- reaction constant conventions explicit,
- activity-based speciation enabled where constants support it,
- VLE/fugacity-equilibrium route documented,
- pressure/speciation outputs generated from one parameter artifact,
- unsupported ePC-SAFT package paths listed as package dependencies.

Allowed claim:

> activity-based true-species ePC-SAFT evaluation.

Forbidden claim:

> final coupled regression.

Current status:

- Diagnostic artifacts exist for full-ionic pressure and speciation using `promoted_ionic_fit`.
- Wong 2015 high-pressure Raman data are present as Markdown and must be extracted before being used as validation.
- Final Phase 2 figures must all name the same parameter artifact and include CSV/PNG/SVG/sidecar outputs.

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

If global fit was skipped, bounded incomplete, or used inconsistent pressure/speciation artifacts.

Current status:

- Not accepted.
- `analyses/epcsaft_ionic_regression/results/global_regression/global_regression_summary.json` reports `package_fit_not_completed`, `attempted_optimization=false`, and `selected_parameter_set=promoted_ionic_fit`.
- Phase 3 remains blocked until generic ePC-SAFT regression support can complete the coupled objective and emit the required artifacts.
