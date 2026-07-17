# Manuscript Submission

## Purpose

Keep the LaTeX manuscript, figure set, source log, and final validation gates aligned so the paper can be submitted with traceable analysis evidence.

## GitHub Milestone

`Manuscript Submission`

**Local target date:** 2026-07-24

The local execution contract targets a Friday-morning submission to *Fluid Phase Equilibria*. The date is not a scientific waiver: any missing coupled-regression, held-out-validation, manuscript, metadata, or package receipt produces a submission hold.

## Related Specs

- `docs/superpowers/specs/2026-07-17-fluid-phase-equilibria-submission-sprint-design.md`
- `docs/superpowers/specs/2026-07-13-manuscript-package-release-workstream-design.md`
- `docs/superpowers/specs/2026-07-13-computational-methods-reproducibility-design.md`
- `docs/superpowers/specs/2026-07-13-submission-metadata-archive-design.md`
- `docs/superpowers/specs/2026-07-13-publication-figures-editorial-design.md`
- `docs/superpowers/specs/2026-07-13-final-submission-readiness-gate-design.md`

## Related Plans

- `docs/superpowers/plans/2026-07-17-fluid-phase-equilibria-submission-sprint-plan.md`
- `docs/superpowers/plans/2026-07-13-manuscript-package-release-workstream-plan.md`
- `docs/superpowers/plans/2026-07-13-computational-methods-reproducibility-plan.md`
- `docs/superpowers/plans/2026-07-13-submission-metadata-archive-plan.md`
- `docs/superpowers/plans/2026-07-13-publication-figures-editorial-plan.md`
- `docs/superpowers/plans/2026-07-13-final-submission-readiness-gate-plan.md`

## Related Issues

- [#15 Manuscript package and release workstream](https://github.com/tannerpolley/MEA-Thermodynamics/issues/15)
- [#16 Document computational methods and reproducibility](https://github.com/tannerpolley/MEA-Thermodynamics/issues/16)
- [#17 Complete submission metadata, licensing, and archival records](https://github.com/tannerpolley/MEA-Thermodynamics/issues/17)
- [#18 Complete publication figures, tables, layout, and editorial polish](https://github.com/tannerpolley/MEA-Thermodynamics/issues/18)
- [#10 Final cross-workstream submission readiness gate](https://github.com/tannerpolley/MEA-Thermodynamics/issues/10)

#10 is an independent blocked-by gate. It does not parent scientific or manuscript-package implementation issues.

## Critical Path

1. #12 admits the immutable upstream execution contract.
2. #13 executes the preregistered training-only coupled fit and conditionally promotes one candidate.
3. #14 evaluates every reserved row and issues the validation/identifiability decision.
4. #16 and #18 consume the executed scientific receipts; #17 proceeds in parallel under author control.
5. #15 aggregates #16–18, and #10 records the final submit-or-hold decision.

Live GitHub milestone or issue mutations are not implied by this local mirror and require an explicit execution approval.

## Success Criteria

- `docs/latex` uses the curated PDF figure artifacts where the manuscript expects publication-ready figures.
- Manuscript language reflects the actual validated artifact status and package-reported fit status.
- `docs/latex/source_log.md` records source, figure, and parameter-evidence changes that support manuscript claims.
- Final work passes `uv run python scripts/validate_project.py confidence` and the required ePC-SAFT final integration check before submission.
- Author-controlled metadata, licensing, release, and archival actions remain HITL until explicitly approved.
