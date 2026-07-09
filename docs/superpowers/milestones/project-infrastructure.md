# Project Infrastructure

## Purpose

Keep MEA-Thermodynamics clean enough that analysis, plotting, validation, and manuscript work can be repeated without rediscovering repo structure or workflow rules.

## GitHub Milestone

`Project Infrastructure`

## Related Specs

Future specs live in `docs/superpowers/specs` and should link back to this page when they change repo-wide workflow, cleanup, validation, or cross-repo integration.

## Related Plans

Future plans live in `docs/superpowers/plans` and should link back to this page when they touch validation orchestration, archive handling, MPLGallery registration, GitHub tracking, or ePC-SAFT integration policy.

## Related Issues

- [#8 Modernize the containerized dev workflow for MEA thermodynamics validation](https://github.com/tannerpolley/MEA-Thermodynamics/issues/8)

## Success Criteria

- `docs/superpowers/PROJECT_CONTEXT.md` stays current with the artifact model and tracker rules.
- Repo validation commands remain documented and runnable from the repository root.
- Cleanup removes dead files without reintroducing backup folders or legacy redirect layers.
- MPLGallery-discoverable Matplotlib plot bundles keep SVG, PDF, PNG, data snapshot, and sidecar metadata together.
- Cross-repo ePC-SAFT feedback is recorded locally and upstream when package friction affects this repo.
