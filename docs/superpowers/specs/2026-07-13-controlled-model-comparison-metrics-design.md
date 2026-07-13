# Controlled Model Comparison and Metric Integrity Design

## Context

The manuscript compares a 31-row ideal/neutral pressure baseline with a 161-row activity calculation, so the reported medians are not a controlled model comparison. It also reports 14 reported-zero targets while canonical role data contain 15.

## Goals

- Evaluate ideal and activity calculations on identical eligible records and reaction conventions.
- Report paired residuals, signed bias, median, RMSE, upper quantiles, maximum error, source/temperature strata, uncertainty availability, and failure accounting.
- Correct the 14/15 reported-zero inconsistency and resolve Wong/curve-grid claim boundaries.
- State explicitly where the activity model improves or worsens pressure and speciation.

## Non-goals

- Do not substitute this comparison for Phase 3 independent validation.
- Do not invent uncertainty where source publications do not report it.
- Do not hide rejected states or collapse reported-zero targets into direct-positive metrics.

## Alternatives

- Compare current headline medians: rejected because the row sets differ.
- Restrict all evidence to the 31 Jou rows: comparable but discards the six-source evidence base.
- Selected: construct an intersection comparison plus full-set source-stratified context.

## Selected design

Create one canonical paired-results table keyed by stable source row identity. Primary comparative metrics use rows evaluated by both models. Full Phase 2 results remain a separate coverage analysis. Target roles remain direct-positive, reported-zero upper bound, or balance-inferred context.

## Interfaces

- Inputs: canonical VLE/speciation datasets, Phase 1/2 result tables, target-role manifests, solver acceptance audits.
- Outputs: paired result table, metric summary, uncertainty-coverage table, manuscript tables/paragraphs, and acceptance receipt.
- Parent: Phase 2 workstream (#5).

## Data flow

1. Join models by canonical row identity and reject ambiguous joins.
2. Apply each model's acceptance contract without silently imputing failures.
3. Compute paired and contextual full-set metrics.
4. Reconcile the 15 reported-zero rows and update manuscript tables.
5. Record Wong and curve-grid rows as evidence, QA-only context, or excluded with reasons.

## Error handling

Fail on duplicate keys, unmatched units, mixed reaction bases presented as paired, missing role labels, or any manuscript count not derivable from the canonical tables.

## Testing and proof

- Deterministic paired-table test.
- Exact source/row and role-count tests.
- Metric recomputation tests covering rejected and censored rows.
- Manuscript integrity test locks the corrected reported-zero count and comparison wording.

## Risks

- A smaller intersection may weaken apparent coverage; report both intersection rigor and full-set context.
- Sparse uncertainty may limit weighted metrics; quantify coverage and avoid fake precision.

## Unresolved decisions

The selected design does not require a new scientific choice. Data eligibility is evidence-driven and recorded row by row.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Comparison basis | Manuscript audit + user-approved full-model endpoint | Use identical rows for primary comparison. | Makes model claims statistically interpretable. | No | model-validation maintainer |
| Reported-zero count | Canonical target-role evidence | Derive the count from canonical rows; current expected value is 15. | Removes the 14/15 inconsistency. | No | data-provenance maintainer |
| Uncertainty handling | Source evidence | Report availability and use uncertainty only where documented. | Avoids invented weights. | No | statistics maintainer |

