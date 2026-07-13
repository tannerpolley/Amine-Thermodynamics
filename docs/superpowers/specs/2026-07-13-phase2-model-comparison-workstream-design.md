# Phase 2 Model Comparison Workstream Design

## Context

GitHub issue #5 delivered the fixed-parameter activity workflow, including 161/161 pressure solves and 74/74 speciation solves, but its original checklist no longer describes the remaining work. The remaining Phase 2 concern is whether the ideal and activity calculations are compared on a common evidence basis with honest claim boundaries.

## Goals

- Convert #5 into a Phase 2 workstream parent instead of an obsolete implementation checklist.
- Own one child deliverable for controlled comparison, uncertainty, metric integrity, and residual-qualified claim boundaries.
- Make Phase 2 completion depend on the child proof rather than unchecked historical tasks.

## Non-goals

- Do not fit Phase 3 ion parameters.
- Do not treat all converged rows as scientifically accepted without residual gates.
- Do not move manuscript-package or release work into Phase 2.

## Alternatives

- Close #5 and create an unrelated comparison issue: loses useful phase history.
- Keep the original body unchanged: preserves stale scope and misleading checkboxes.
- Selected: retain #5 as the parent and replace its body with current evidence and one bounded child.

## Selected design

#5 becomes a `kind:workstream` issue in the Phase 2 milestone. It summarizes completed model infrastructure, links the fixed-parameter evidence receipt, and is blocked only by the controlled-comparison child. The child owns all remaining statistics and manuscript-facing Phase 2 claim gates.

## Interfaces

- Inputs: Phase 1 and Phase 2 canonical results, source manifests, target-role tables, and final-verification receipt.
- Outputs: updated #5 mirror/body, one child relationship, and a Phase 2 completion receipt.
- Dependencies: none outside the child deliverable; Phase 3 consumes but does not own this workstream.

## Data flow

1. Load current Phase 1/2 evidence and counts.
2. Publish the comparison child from its validated mirror.
3. Link the child under #5 and mark #5 blocked by it.
4. Close #5 only after the child proof is verified.

## Error handling

Stop if current evidence contradicts the 161/74 solve counts, if the child cannot be linked, or if #5 would still contain unchecked superseded acceptance criteria after the rewrite.

## Testing and proof

- Local mirror validation passes.
- GitHub verification shows #5 in Phase 2 with the intended labels and child.
- The completed-infrastructure statement matches the July 9 verification receipt.

## Risks

- Parent status can be mistaken for implementation status; mitigate with explicit completed and remaining sections.
- Cross-phase comparison may drift into Phase 3; keep the child scoped to fixed-parameter evidence.

## Unresolved decisions

No scope decision remains. The user approved the distributed hierarchy and full-model endpoint.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Phase 2 hierarchy | User-approved distributed design | Retain #5 as the parent with one comparison child. | Preserves phase ownership while removing stale checklist semantics. | No | Phase 2 maintainer |
| Completion boundary | July 9 verification receipt | Infrastructure is complete; controlled comparison remains. | Prevents reopening solved implementation work. | No | validation maintainer |

