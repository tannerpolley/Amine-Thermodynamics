# Computational Methods and Reproducibility Reporting Design

## Context

The manuscript's computational implementation subsection omits solver mechanics already present in the repository: initialization, continuation, damping, iteration limits, acceptance tolerances, failure policy, bubble-pressure solving, permittivity rules, package revision, and runtime protocol.

## Goals

- Document the exact executed Phase 1/2/3 algorithms and their numerical acceptance criteria.
- Trace every reported setting to code/config or a generated method receipt.
- Include package version/commit, environment, hardware-relevant runtime context, and reproducible commands.

## Non-goals

- Do not describe unexecuted prospective algorithms as current methods.
- Do not duplicate equations already defined clearly elsewhere.
- Do not hard-code values in prose that cannot be tested against runtime sources.

## Alternatives

- Expand prose manually: prone to drift.
- Publish only repository links: insufficient for a journal article.
- Selected: concise manuscript methods backed by a generated, testable method inventory.

## Selected design

Create a canonical method-inventory artifact populated from declared runtime/config sources. Manuscript text and tables cite or reproduce its stable fields. Tests compare critical prose/table values against the inventory and reject stale package revisions or tolerances.

## Interfaces

- Inputs: solver acceptance contract, reaction catalog, analysis configs, package integration receipt, executed Phase 3 method.
- Outputs: method inventory, revised methods/theory sections, reproducibility command block, consistency tests.
- Parent: Manuscript Package and Release; blocked by final Phase 3 method details for closeout.

## Data flow

Collect declared settings → validate against executable sources → generate inventory → revise manuscript → build PDF → run consistency tests.

## Error handling

Fail on undocumented defaults, conflicting values, unpinned package state, missing failure policy, prospective/current method conflation, or manuscript values without a source.

## Testing and proof

- Inventory schema and completeness tests.
- Manuscript-to-runtime consistency tests for tolerances, versions, counts, and algorithms.
- Clean-checkout method inventory and PDF rebuild.

## Risks

Excess detail can overwhelm the paper; keep the main text sufficient and place exhaustive settings in a reproducibility table or supplement.

## Unresolved decisions

Final placement between main text and supplement depends on the selected journal, but all required content must exist before closeout.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Method source | Repository audit | Generate one canonical method inventory from executable declarations. | Prevents prose/config drift. | No | reproducibility maintainer |
| Reporting depth | Submission review | Main text is sufficient; exhaustive settings may move to supplement. | Balances rigor and readability. | Yes | corresponding author |

