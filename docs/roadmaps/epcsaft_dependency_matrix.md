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

## Phase 2 package inspection on 2026-05-15

The current MEA environment imports `epcsaft` version `1.5.2` from a stable pinned Git dependency:

`epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785`

`uv run python scripts/check_epcsaft_integration.py --mode stable` and `--mode final` report `source kind: pinned_git` at commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785`.

| Issue #5 capability | Current package status | Phase 2 action |
|---|---|---|
| Generic activity-based speciation | Present and used by Phase 2 through the native reactive electrolyte solver path. Current MEA Phase 2 artifacts record `model_ran_success`. | Keep residual validation in MEA-owned `phase2_residual_acceptance_audit.csv`; do not collapse validation outcomes into solver-run status. |
| Generic VLE/fugacity equilibrium | Present: `electrolyte_bubble` and `ElectrolyteBubbleResult` are importable; package capabilities list reactive electrolyte bubble pressure for fixed liquid composition with neutral vapor species. | Use for volatile `CO2`, `H2O`, and `MEA`; ions remain liquid-only. |
| Reaction constant convention layer | Partial: `ReactionDefinition` accepts `standard_state` and convention metadata; no `ReactionSet` symbol is exposed. | Keep MEA reaction-source mapping local and block unsupported apparent-to-activity conversion. |
| Implicit solved-state sensitivities | Partial: package capabilities report production speciation implicit sensitivities, but bubble-pressure implicit sensitivities are still unavailable. | Do not claim Phase 3-quality coupled derivative coverage from Phase 2. |
| Generic TargetDataset schema | Present: `TargetDataset`, `ReactiveElectrolyteBatch`, `ReactiveElectrolyteRow`, and `ReactiveRegressionObjective` are importable. | Use for future target-row construction; keep MEA data ownership downstream. |
| Generic regression backend | Present but not a Phase 2 claim: reactive electrolyte batch regression status fields are exposed, while current MEA global artifacts still show package fit not completed. | Keep Phase 3 regression blocked until a coupled package fit passes approval gates. |

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

Current local development uses the stable-mode pinned Git dependency in `pyproject.toml` and `uv.lock`. Use the local `epcsaft-dev` worktree only for intentional upstream/downstream co-development, not routine downstream validation. See `docs/roadmaps/reproducibility_dependency_note.md`.

Current 2026-05-15 status: stable integration validation passes against the pinned Git dependency. Final manuscript or archive results still require final-mode validation, but they no longer depend on a mutable local package path.

Phase status:

- Phase 1: can proceed with repo-owned data and existing baseline scripts; it must not depend on unavailable package features.
- Phase 2: depends on generic activity-based speciation and reactive VLE/fugacity support from `epcsaft`.
- Phase 3: depends on generic native regression backend support that can complete the coupled pressure/speciation fit at routine cost.

Do not request MEA-specific public APIs from `epcsaft`; convert recurring needs into generic reaction, equilibrium, target-dataset, or regression capabilities.
