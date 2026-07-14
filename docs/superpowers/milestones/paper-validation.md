# Paper Validation

## Purpose

Recreate cited literature figures and tables closely enough that manuscript comparisons are transparent, source-linked, and visually faithful to the referenced paper evidence.

## GitHub Milestone

`Paper Validation`

## Related Specs

Future specs live in `docs/superpowers/specs` and should link back to this page when they define a paper recreation target, digitization rule, or acceptance tolerance.

## Related Plans

- `docs/superpowers/plans/2026-07-14-data-acquisition-regression-readiness-plan.md`

## Related Issues

- [#9 Paper Validation: lock Baygi 2015 recreation acceptance gate](https://github.com/tannerpolley/MEA-Thermodynamics/issues/9) — completed 2026-07-13; retained in GitHub history.
- Data acquisition and source verification feed Phase 3 through `data/reference/MEA/manifests/source_search_log.csv` and `parameter_observable_coverage.csv`; metadata-only leads remain non-numeric.

## Success Criteria

- `analyses/paper_validation/2015_baygi` remains the canonical Baygi 2015 validation root.
- Recreated figures include plotted-data snapshots and vector/PDF companions when generated with Matplotlib.
- Validation artifacts state what is reproduced exactly, what is inferred, and what remains outside the paper evidence.
- Manuscript citations and figure references point to the validated artifact set rather than ad hoc screenshots.
- Every candidate regression source has an access/extraction decision, and unverified bases or primary-source gaps fail closed before target admission.
