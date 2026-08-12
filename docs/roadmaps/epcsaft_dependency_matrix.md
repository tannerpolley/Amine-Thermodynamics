# Unified ePC-SAFT dependency matrix

Status: planning contract. No Engine wheel or Data packet is bound by this document.

MEA-Thermodynamics will consume one immutable installed `epcsaft` Engine wheel exposing `epcsaft`, `epcsaft.equilibrium`, and `epcsaft.regression`. It must not import a sibling source checkout or use split-package compatibility interfaces.

## Current boundary

| Capability | Owner | Current status | MEA use |
|---|---|---|---|
| PC-SAFT, association, DD/QQ/DQ polar terms, Debye–Hückel, corrected SSM+DS Born, and relative-permittivity formulations | Engine EOS | Implemented for value and supported derivative evaluation | Evaluate explicit model configurations from immutable parameter records |
| Pure-saturation and fixed-state-pressure observations | Engine EOS and Regression | Publicly admitted | Neutral pure-component and qualified fixed-state preparation |
| Fixed-T,P homogeneous chemical equilibrium and sensitivities | Engine Equilibrium | Public solve exists; Regression observation family is absent | Direct evaluation only; regression blocked by [Engine #30](https://github.com/tannerpolley/ePC-SAFT/issues/30) |
| Nonreactive phase equilibrium | Engine Equilibrium | Public solve exists; Regression observation families were deferred | Evaluation only; no neutral VLE fit through current Regression |
| Coupled reactive bubble/VLE | Engine Equilibrium | Missing | Predictive reactive VLE blocked by [Engine #31](https://github.com/tannerpolley/ePC-SAFT/issues/31) |
| Generic optimizer, residual mapping, weights, bounds, and diagnostics | Engine Regression | Implemented for admitted owner observations | Consume only owner-advertised observation families |
| MEA source rows, reactions, campaign blocks, fit stages, residual policy, model selection, and promotion | MEA-Thermodynamics | Application-owned | Materialize an immutable Data packet; never move these policies into Engine |

The old 1.5.2 pinned evaluation lane and split-repository plans are historical evidence. They do not define current capability and must not be used to justify a new fit.

## Required upstream sequence

1. Finish the current Engine hard cutover and produce one immutable wheel.
2. Admit the source-neutral fixed-T,P homogeneous reactive Observation Family in Engine #30.
3. Admit the fixed-topology reactive bubble/VLE Observation Family in Engine #31.
4. Consume those families from MEA with exact Data-packet, wheel, parameter, topology, reference, and domain fingerprints.

Issue #30 must expose certified local reacting-state values and exact total selected-parameter Jacobians with typed non-evaluable trials. Issue #31 must couple reaction equilibrium and phase equilibrium, use EOS fugacities for caller-declared neutral vapor species, preserve phase and branch identity, and state its local/global certificate scope.

## MEA responsibilities

- curate the nine species, five reactions, source standard states, and reaction-correlation sources;
- preserve direct, aggregate, calibration-derived, model-derived, and censored observation roles;
- freeze campaign-blocked cross-validation and the later all-admissible-data refit;
- provide source-valued molecular moments and induced-association topology records;
- decide the discrete relative-permittivity and Born formulation;
- choose staged active parameter blocks, scales, bounds, priors, and scientific promotion gates;
- generate figures, uncertainty evidence, and manuscript claims only from accepted results.

## Do not implement downstream

- residual Helmholtz equations or polar, association, dielectric, Debye–Hückel, or Born kernels;
- generic chemical- or phase-equilibrium algorithms;
- implicit solved-state derivative plumbing;
- a second application-owned optimizer;
- compatibility imports, sibling-source discovery, numeric failure penalties presented as observations, or MEA-specific Engine branches.

The current executable regression boundary is intentionally narrower than the planned model. See `predictive_reactive_vle_regression.md` and the machine-readable contracts under `data/reference/MEA/manifests/`.
