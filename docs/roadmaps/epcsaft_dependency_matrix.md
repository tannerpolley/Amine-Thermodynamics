# ePC-SAFT Package Dependency Matrix for MEA-Thermodynamics

## Policy

MEA-Thermodynamics must use generic ePC-SAFT APIs. It must not request application-specific public APIs.

## Dependency table

| Package capability | ePC-SAFT owner | MEA phase affected | Required for | Current action |
|---|---|---:|---|---|
| Derivative coverage gates | ePC-SAFT | 0-3 | honest capability reporting | verify with `scripts/check_epcsaft_integration.py` and package `capabilities()` |
| Reaction/equilibrium-constant convention layer | ePC-SAFT | 1-3 | basis-safe reaction constants | use generic `ReactionSet`/convention support if available; keep MEA mapping local |
| Generic TargetRow / TargetDataset schema | ePC-SAFT | 3 | generic regression data input | local code currently maps MEA rows through `src/MEA/epcsaft_ionic/native_regression.py` |
| Explicit CppAD parameter derivatives | ePC-SAFT | 3 | native regression derivatives | required before routine coupled pressure/speciation fitting is credible |
| Generic implicit solved-state sensitivities | ePC-SAFT | 2-3 | speciation/VLE/regression derivatives | expected Task C / #86 dependency; do not reimplement in MEA |
| Generic activity-based speciation solver | ePC-SAFT | 2-3 | Phase 2 speciation | current MEA workflow calls generic package speciation symbols through `src/MEA/epcsaft_runtime.py` |
| Generic VLE/fugacity equilibrium solver | ePC-SAFT | 2-3 | pressure calculations | current MEA workflow calls generic reactive electrolyte bubble support |
| Generic regression backend | ePC-SAFT | 3 | coupled regression | current `global_regression_summary.json` says package native fit did not complete; Phase 3 blocked |
| Literature benchmark suite | ePC-SAFT | 2-3 | package confidence | expected Task L / #95 dependency; MEA owns only MEA-specific validation |

## Do not implement in MEA-Thermodynamics

- residual Helmholtz equation internals,
- CppAD derivative plumbing,
- generic equilibrium solver internals,
- generic regression optimizer internals,
- generic TargetRow schema implementation,
- generic Ceres backend implementation.

## Do implement in MEA-Thermodynamics

- MEA data curation,
- MEA reaction network selection,
- MEA source manifests,
- MEA figure generation,
- MEA manuscript text,
- MEA phase-specific workflow scripts,
- MEA-specific wrappers around generic APIs if useful.

## Current dependency status

The repo has an explicit integration contract at `integration/epcsaft_contract.json` and a checker at `scripts/check_epcsaft_integration.py`.

Current local development still uses a machine-local ePC-SAFT worktree path in `pyproject.toml`/`uv.lock`. That is acceptable for `dev` mode but not for final manuscript or archive results. See `docs/roadmaps/reproducibility_dependency_note.md`.

Current 2026-05-13 blocker: the configured dev path `C:\Users\Tanner\.codex\worktrees\epcsaft-dev\ePC-SAFT` is missing. Package-dependent Phase 2/3 work must stay blocked until that path is restored or `epcsaft` is repinned and the integration checker passes.

Phase status:

- Phase 1: can proceed with repo-owned data and existing baseline scripts; it must not depend on unavailable package features.
- Phase 2: depends on generic activity-based speciation and reactive VLE/fugacity support from `epcsaft`.
- Phase 3: depends on generic native regression backend support that can complete the coupled pressure/speciation fit at routine cost.

Do not request MEA-specific public APIs from `epcsaft`; convert recurring needs into generic reaction, equilibrium, target-dataset, or regression capabilities.
