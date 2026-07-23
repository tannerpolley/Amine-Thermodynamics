# Engineering Methods

Use Matt engineering methods for the technical work they actually cover and
Project Truss only for GitHub-native coordination.

## Required shaping method

New governed outcomes and material rescopes require `grilling` before
publication. Add `domain-modeling` only when terminology, invariants,
ownership, or state transitions are unresolved. Existing decisions and
evidence should be read before asking the user for facts that the repository
can answer.

## Implementation routing

- Use `research` for niche scientific claims that require primary-source
  evidence.
- Use `tdd` for stable discrete behavior at an approved seam.
- Use `diagnosing-bugs` only after reproducing an unexplained defect.
- Use `prototype` for a design question that requires executable evidence.
- Use `code-review` for a stable shared diff.
- Use `resolving-merge-conflicts` only for an active merge or rebase conflict.

Availability is checked against the active Codex skill inventory for every
Project Truss start. A missing required method blocks governed work rather
than being silently replaced.

## Scientific boundary

The repository profile is `scientific-computing`. Numerical and
thermodynamic claims require provenance, units and basis, conservation and
domain checks, numerical convergence where applicable, and an independent or
experimental reference oracle. A solver success flag or fitted residual alone
is not scientific acceptance.
