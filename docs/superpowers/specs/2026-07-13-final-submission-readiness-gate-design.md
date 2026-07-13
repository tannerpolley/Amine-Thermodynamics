# Final Submission Readiness Gate Design

## Context

GitHub issue #10 currently acts as an underspecified umbrella and child parent. Under the approved distributed taxonomy, it should instead be an independent final gate that aggregates proof from Phase 2, Phase 3, and the Manuscript Package and Release workstream.

## Goals

- Rewrite #10 as a cross-milestone proof gate with no unrelated children.
- Require completed workstream receipts, final integration, deterministic manuscript build, visual review, archive/metadata proof, and explicit human submission decision.
- Make blocked-by relationships and failure reasons visible.

## Non-goals

- Do not own the implementation tasks of its upstream workstreams.
- Do not claim readiness from repository tests alone.
- Do not submit, release, or archive as an implicit side effect.

## Alternatives

- Keep #10 as mega-parent: rejected by the distributed design.
- Remove #10 entirely: loses one final decision/proof surface.
- Selected: retain #10 only as an evidence aggregation and human decision gate.

## Selected design

#10 is blocked by the Phase 2 parent (#5), Phase 3 parent (#6), and the new Manuscript Package and Release parent. Its checklist contains only final cross-workstream proofs. It reaches HITL only after machine-verifiable gates pass, then records the author's submission decision.

## Interfaces

- Inputs: parent closeout receipts, final ePC-SAFT integration receipt, deterministic PDF/hash, source log, release/archive metadata, visual review.
- Outputs: readiness matrix, unresolved-risk statement, human decision record, final gate state.
- Relationships: blocked-by workstream parents; no child ownership.

## Data flow

Verify parent closures → run final clean-checkout proofs → inspect final PDF/package → assemble readiness matrix → request human decision → mark ready or reopen the owning workstream.

## Error handling

Any missing, stale, failed, or contradictory receipt keeps #10 blocked and routes the finding back to its workstream owner. Human approval cannot override failed scientific proof.

## Testing and proof

- `uv run python scripts/validate_project.py confidence`.
- `uv run python scripts/check_epcsaft_integration.py --mode final`.
- Deterministic clean manuscript build and freshness receipt.
- All-page visual review, metadata/archive link validation, clean worktree, and explicit final author decision.

## Risks

A green automation suite can be mistaken for scientific readiness; the readiness matrix must distinguish machine proof, scientific evidence, editorial review, and author decisions.

## Unresolved decisions

The final submit/hold decision remains HITL and occurs only after all upstream proof is valid.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| #10 role | User-approved distributed hierarchy | Use #10 only as the final blocked-by gate. | Keeps implementation ownership in real project workstreams. | No | project maintainer |
| Readiness semantics | Manuscript audit | Require scientific, computational, editorial, metadata, and human proof. | Prevents tests-only readiness claims. | No | corresponding author |
| Submission decision | External author authority | Request submit/hold only after all proofs pass. | Preserves human publication authority. | Yes | corresponding author |

