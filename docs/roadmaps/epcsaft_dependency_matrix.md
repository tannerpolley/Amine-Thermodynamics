# ePC-SAFT Package Dependency Matrix for MEA-Thermodynamics

## Policy

MEA-Thermodynamics must use generic ePC-SAFT APIs. It must not request application-specific public APIs.

The preserved `tannerpolley/ePC-SAFT-lab` is historical/transitional evidence, not a production or tracker owner. Clean `ePC-SAFT/ePC-SAFT` owns future provider capabilities, clean `ePC-SAFT/ePC-SAFT-regression` owns future Ceres regression, and the migration control plane owns stage sequencing until accepted promotion receipts transfer runtime authority.

## Dependency table

| Package capability | Production owner | MEA phase affected | Required for | Current action |
|---|---|---:|---|---|
| Provider derivative coverage gates | Clean `ePC-SAFT/ePC-SAFT` after promotion | 0-3 | honest capability reporting | preserve the pinned historical lane; require a clean capability receipt before cutover |
| Reaction/equilibrium-constant convention layer | Clean provider/equilibrium owners after promotion | 1-3 | basis-safe reaction constants | keep MEA mapping local until a generic admitted contract exists |
| Generic target dataset schema | Clean `ePC-SAFT/ePC-SAFT-regression` after promotion | 3 | generic regression data input | MEA maps frozen rows locally; no clean production schema is admitted yet |
| Exact CppAD residual Jacobians | Clean provider plus regression owners after promotion | 3 | native regression derivatives | required before coupled pressure/speciation execution is admitted |
| Generic implicit solved-state sensitivities | Clean provider owner after promotion | 2-3 | speciation/VLE/regression derivatives | do not reimplement in MEA or infer from historical lab scope |
| Generic activity-based speciation solver | Current immutable 1.5.2 evidence; future clean owners | 2-3 | Phase 2 speciation | current MEA workflow consumes the pinned public symbols through `src/MEA/epcsaft_runtime.py` |
| Generic VLE/fugacity equilibrium solver | Current immutable 1.5.2 evidence; future clean owners | 2-3 | pressure calculations | current fixed-evaluation workflow consumes the pinned reactive electrolyte bubble support |
| Generic regression backend | Clean `ePC-SAFT/ePC-SAFT-regression` after promotion | 3 | coupled regression | migration stage approval and immutable clean capability evidence are absent; Phase 3 execution stays blocked |
| Literature and installed-artifact acceptance | Clean `ePC-SAFT/ePC-SAFT-validation` after promotion | 2-3 | package confidence | MEA owns only MEA-specific validation and final pinned-source checks |

## Immutable Phase 2 evaluation inspection on 2026-05-15

The current MEA environment imports `epcsaft` version `1.5.2` from a stable pinned Git dependency. This is immutable historical evaluation evidence, not proof that the lab owns future clean production:

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

Current local validation uses the stable-mode pinned Git dependency in `pyproject.toml` and `uv.lock`; routine downstream validation must not resolve through a mutable sibling checkout. See `docs/roadmaps/reproducibility_dependency_note.md`.

New clean-package co-development requires a stage-approved migration transfer plan and an explicit worktree outside this repository. The clean regression repository is currently a governance-only skeleton, so no development checkout or clean capability can yet satisfy Issue #12.

Current 2026-05-15 status: stable integration validation passes against the pinned Git dependency. Final manuscript or archive results still require final-mode validation, but they no longer depend on a mutable local package path.

Phase status:

- Phase 1: can proceed with repo-owned data and existing baseline scripts; it must not depend on unavailable package features.
- Phase 2: depends on generic activity-based speciation and reactive VLE/fugacity support from `epcsaft`.
- Phase 3: depends on a stage-approved clean regression slice, exact residual Jacobians, a production native Ceres loop, structured diagnostics, and an immutable installed-artifact receipt. Until then, `upstream_execution_admitted` remains false.

Do not request MEA-specific public APIs from `epcsaft`; convert recurring needs into generic reaction, equilibrium, target-dataset, or regression capabilities.
