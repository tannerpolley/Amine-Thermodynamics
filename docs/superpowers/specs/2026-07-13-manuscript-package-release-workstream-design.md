# Manuscript Package and Release Workstream Design

## Context

The remaining manuscript-facing work mixes numerical-method reporting, author/repository metadata, archival release, figure legibility, layout, and editorial revision. These are real deliverables but do not belong under Phase 2 or Phase 3 and should not all be children of final gate #10.

## Goals

- Create a dedicated Manuscript Submission workstream parent with three children: methods/reproducibility, metadata/archive, and figures/editorial.
- Keep #10 independent as the cross-workstream final proof gate.
- Make every child verifiable and assign human-only decisions explicitly.

## Non-goals

- Do not own Phase 2 comparison or Phase 3 fitting.
- Do not select a journal, license, ORCID, funding statement, or archive record without author input.
- Do not submit the manuscript.

## Alternatives

- Put all children under #10: rejected by the approved distributed design.
- Use three unrelated flat issues: loses package-level sequencing and closeout.
- Selected: one manuscript-package parent with three cohesive children.

## Selected design

The parent owns the finished manuscript/release package and is blocked by its three children. Cross-workstream dependencies use `blocked-by` links rather than parentage: methods depend on the executed model, and final figures depend on approved comparison/regression outputs.

## Interfaces

- Inputs: approved Phase 2/3 evidence, LaTeX sources, figures/tables, repository metadata, release policy.
- Outputs: publication-ready PDF/source package, release/archive evidence, child receipts, parent closeout.
- Consumer: final readiness gate #10.

## Data flow

Complete child work in parallel where safe → integrate final scientific outputs → build deterministic PDF → assemble release evidence → close parent → unblock #10.

## Error handling

Stop if scientific artifacts are not final, author-owned metadata is missing, figures are stale, the PDF is not reproducible, or the archive/release references do not resolve.

## Testing and proof

- Child validators and manuscript-focused tests pass.
- Fresh deterministic PDF is visually inspected.
- Release/license/archive evidence resolves from the manuscript and repository.
- GitHub verifies the parent and three child relationships.

## Risks

Venue-specific requirements remain unknown; implement venue-neutral completeness and record selected-venue deltas separately.

## Unresolved decisions

Target journal requirements remain author-owned and are handled by the metadata child without widening scientific scope.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Workstream ownership | User-approved distributed hierarchy | Create a separate manuscript-package parent. | Prevents #10 from becoming a mega-parent. | No | manuscript maintainer |
| Child boundaries | Manuscript audit | Separate methods, metadata/archive, and figures/editorial. | Gives each deliverable one proof oracle. | No | manuscript maintainer |
| Venue policy | Missing target-journal decision | Apply venue-neutral requirements and record venue deltas later. | Avoids guessing declarations or assets. | Yes | corresponding author |

