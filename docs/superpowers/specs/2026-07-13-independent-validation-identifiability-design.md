# Independent Validation and Identifiability Design

## Context

Optimizer convergence alone does not establish predictive value or parameter identifiability. The validation split, leakage checks, and failure-accounting policy must be frozen before fitting; candidate-dependent conclusions wait for the immutable #13 result.

## Goals

- Define reserved validation data before fitting and preserve source/temperature/species coverage.
- Quantify predictive pressure/speciation performance, uncertainty coverage, parameter sensitivity, correlation, and practical identifiability.
- Stress-test the promoted candidate across seeds, perturbations, and admissible alternative parameterizations.

## Non-goals

- Do not call a post hoc source split held-out validation.
- Do not use training residuals as validation proof.
- Do not interpret local sensitivity as a full confidence interval without supporting assumptions.

## Alternatives

- Validate only on training rows: rejected.
- Random row split: risks leakage across source/temperature families.
- Selected: preregistered grouped holdout plus clearly labeled robustness and identifiability analyses.

## Selected design

Stage A reserves grouped evidence by source/condition, freezes failure accounting, and proves leakage guards before fit execution. Stage B binds the immutable candidate hash, reports validation metrics separately from training, and combines local sensitivity, multistart/perturbation evidence, active-bound analysis, and parameter plausibility into an approval decision with explicit limitations. Stage A alone cannot close the issue.

## Interfaces

- Inputs: immutable promoted candidate, preregistered split, canonical targets, uncertainty metadata.
- Outputs: validation predictions, grouped metrics, identifiability matrix, robustness report, approval receipt.
- Parent: Phase 3 workstream; blocked by the coupled-fit candidate.

## Data flow

Freeze split/policy/tests before fit → wait for immutable candidate → verify candidate hash → load untouched validation groups → predict → apply acceptance gates → compute metrics → run sensitivity/robustness → approve, reject, or require refit.

## Error handling

Fail on split leakage, candidate hash drift, missing groups, post hoc relabeling, unreported prediction failures, singular analyses presented as identified, or unsupported uncertainty claims.

## Testing and proof

- Split leakage and determinism tests.
- Receipt proving the split and failure policy predate the full-fit result.
- Validation metrics recompute from saved predictions.
- Adversarial fixtures for active bounds, failed rows, and nonidentifiable directions.
- Manuscript tests distinguish training, validation, and sensitivity language.

## Risks

Available data may not support strong independent claims; the outcome must narrow claims or block submission rather than fabricate certainty. Infrastructure can be prepared while upstream work proceeds, but it is not candidate validation.

## Unresolved decisions

The exact grouped holdout composition is finalized in the plan from source coverage before the fit is executed and then frozen.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Validation design | Manuscript audit | Use preregistered grouped holdout evidence. | Prevents leakage and post hoc validation claims. | No | model-validation maintainer |
| Identifiability claim | Scientific standards | Require sensitivity, robustness, bounds, and plausibility evidence. | Separates optimizer convergence from parameter trust. | No | statistics maintainer |
| Holdout membership | Canonical source coverage | Freeze exact groups before full fit execution. | Preserves independence. | Yes | model-validation maintainer |
