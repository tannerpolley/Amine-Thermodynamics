# Superpowers Issue Mirrors

Issue mirrors in this directory capture GitHub issue context that needs to be durable in the repo. Keep one mirror per issue when local planning or execution needs a repo-tracked copy.

Use this root for canonical issue mirror files; milestone pages should link here rather than nesting issue mirrors under milestone directories.

Milestones own lifecycle phase. Labels add orthogonal project meaning:

- `kind:workstream` identifies non-executable rollups; `kind:deliverable` identifies executable vertical slices.
- `area:*` labels route model comparison, regression, validation, reproducibility, release, and editorial ownership.
- `priority:submission-blocker` identifies work required for the full-model manuscript submission without making it a child of the final readiness gate.
- `status:*` records whether a slice is ready, blocked, or requires human input.
