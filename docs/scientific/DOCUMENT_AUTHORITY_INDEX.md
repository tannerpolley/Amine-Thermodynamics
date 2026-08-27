# GREPE and MEA document authority index

General Reactive Equilibrium and Phase Equilibrium (GREPE) is the Engine
calculation used by this aqueous monoethanolamine (MEA) study.

- Audited: 2026-08-25
- Scope: Engine GREPE, predictive MEA, absorber-column integration, and the
  parallel lithium configured-LLE application
- Purpose: classify existing planning and evidence documents without creating
  a second work queue

## Authority rule

Native GitHub issues are the live queue. An authoritative scientific definition
or plan states durable decisions and names why it has authority. A literature
review supplies source synthesis. An analysis README or report states what was
actually run. Historical plans and transfer records remain readable provenance
but cannot silently reactivate or supersede current decisions.

## ePC-SAFT Engine

| Path | Classification | Use |
|---|---|---|
| `governance/GOVERNANCE.md` | Authoritative doctrine | Ownership, equilibrium/regression calculation admission, numerical evidence, and repository boundaries |
| `governance/CONTEXT.md` | Authoritative project definition | Current four-repository ownership, regression formulations, and bibliography authority |
| `engine/docs/equilibrium/plans/2026-08-14-general-reactive-equilibrium-phase-equilibrium.md` | Authoritative application-independent design | GREPE request/compiler/result definitions, current reduced-space formulation, and planned full-space formulation |
| `engine/docs/equilibrium/reactive-bubble-observations.md` | Current admitted-calculation note | Fixed-topology reactive bubble/VLE observations and local-branch semantics |
| `engine/docs/regression/science/literature-reproduction-contract.md` | Retained application-independent evidence guidance | Source reproduction classes, exact rows, and replay requirements |
| `engine/docs/regression/general-regression-quickstart.md` | Analyst-facing runtime guidance | Current Regression callables; not scientific model selection |
| `engine/docs/regression/science/pure-saturation-regression.md` | Current bounded method note | Pure-property regression behavior only |
| `engine/docs/regression/research/association-regression-source-locator.md` | Source locator | Association-regression evidence, not program authority |
| `engine/docs/regression/science/general-parameter-regression.md` | Historical/superseded design | Pre-cutover general Regression design retained for provenance |
| `engine/docs/regression/science/mea-coupled-regression-master-plan.md` | Historical readiness/source record | Pre-GREPE MEA regression inventory; not the current numerical formulation |
| `engine/docs/regression/plans/2026-08-07-owner-driven-parameter-fit.md` | Completed historical plan | Earlier owner-driven fit requirements; no live queue |

Live issues: #44 application-independent GREPE, #47 lithium configured reactive LLE, #48
MEA-intensive boundary, #50 typed null-residual failure, and #51 optional
simultaneous sparse multi-experiment backend. Closed issues #30 and #31 are
accepted homogeneous-reactive and reactive-bubble calculation history.

## MEA-Thermodynamics

| Path | Classification | Use |
|---|---|---|
| `docs/scientific/CONTEXT.md` | Authoritative scientific definition | Question, ownership, vocabulary, authority, and claim boundary; authority comes from repository guidance and issue #70 |
| `docs/scientific/PREDICTIVE_MEA_PROGRAM.md` | Authoritative scientific plan | Neutral qualification, electrostatic selection, regression, validation, and manuscript sequence; GitHub issues own execution |
| This index | Authoritative navigation | Document classification only; it owns no scientific decision or work queue |
| Engine Issue #80 and its future reviewed packet | Upstream method and current parameter-campaign authority | Builds and debugs the generic method; MEA reproduction is allowed after an immutable packet is accepted |
| `analyses/phase3/ionic_epcsaft_regression/results/issue_70/predictive_mea_parameter_decision.json` | Historical Issue 70 gate decision | Conservative supported-negative predictive decision, exact input hashes, generated tables, and downstream refusal |
| `docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md` | Current source synthesis | Literature basis for the retained induced-association and Born formulations; not adoption or queue authority |
| `docs/ePC-SAFT/full-component-parameter-source-audit.md` | Current source audit | Component-level parameter provenance |
| `docs/ePC-SAFT/mea-reaction-and-sentinel-primary-source-audit.md` | Current source audit | Reaction and sentinel evidence |
| `docs/ePC-SAFT/meah-meacoo-volumetric-evidence.md` | Current evidence synthesis | Volumetric information for MEAH+/MEACOO- |
| `docs/ePC-SAFT/meah-meacoo-direct-density-request.md` | Evidence acquisition note | Missing direct-density need, not a live plan |
| `docs/ePC-SAFT/gross_sadowski_2001_appendix_equations.md` | Equation/source companion | Exact literature equation support |
| `analyses/phase3/ionic_epcsaft_regression/pressure_first/README.md` and `analysis.yaml` | Historical analysis record | Retained neutral-family qualification evidence; no active candidate |
| `analyses/phase3/ionic_epcsaft_regression/README.md` | Analysis-area navigation | Phase-3 analysis structure, not program authority |
| `docs/revision_notes/manuscript_submission_review.md` | Manuscript review evidence | Earlier submission review findings |

Closed issues #62--#65 and #67 retain observation, neutral, electrostatic,
induced-association, and configuration evidence. Closed issues #13, #14, and
#70 retain the regression, validation, and conservative predictive-gate
decisions. Issue #68 owns manuscript evolution, and #10 is the final manuscript
gate. Issues #61 and #66 are closed historical records.

## MEA-Absorption-Column

| Path | Classification | Use |
|---|---|---|
| `analyses/nccc_validation/results/final/reports/reactive_epcsaft_claim_boundary.md` | Retained analysis result | Fixed-chemistry and feasibility claim boundary |
| `docs/coordination/august_27_predictive_reactive_epcsaft_revision_plan.md` | Historical plan | Its #30/#31 dependency state is stale |
| `docs/coordination/epcsaft_reactive_vle_upstream_handoff.md` | Historical transfer record | Earlier upstream request; not current Engine callable status |
| `docs/reviewer_quick_revision_report.md` | Current branch review record | Reviewer-driven manuscript changes, independent of predictive-thermo adoption |
| `docs/revision_report.md` | Revision evidence | Existing manuscript revision record |
| `docs/latex/**` | Current manuscript source | Fixed-chemistry/ePC-SAFT fugacity comparison until a parameter set meets independent column-comparison criteria |

Issue #3 owns the current electrolyte-path validation. Issue #12 owns creation
of an authoritative scientific definition and current predictive
mapping/manuscript-revision plan in a task attached to the Column repository.
The baseline manuscript
must remain valid if that predictive lane produces a supported negative result.

## Lithium_Extraction

| Path | Classification | Use |
|---|---|---|
| `docs/scientific/CONTEXT.md` | Authoritative application definition | Configured HBTA/TOPO reactive-LLE question, ownership, evidence, and claims |
| `docs/scientific/formulation.tex` | Authoritative formulation | Phase-specific reactive-LLE equations and conventions |
| `docs/scientific/methods.tex` | Authoritative methods | Parameter fitting, starts, numerical acceptance, surrogate generation, and domain |
| `docs/scientific/evidence.tex` | Authoritative evidence plan/record | Verification, validation, and uncertainty |
| No active research notebook | Retired | A future reviewed immutable packet may be summarized under its owning analysis; notebooks are not calculation authority |
| `docs/scientific/reports/published_epcsaft_engine_benchmark.tex` | Source/Engine benchmark report | Engine-calculation-gated literature comparison, including supported refusals |
| `analyses/hbta_topo_configured_reactive_lle/README.md` | Analysis record | Application-independent configured-LLE comparison and its limits |
| `analyses/hbta_topo_calibrated_surrogate/README.md` | Analysis record | Calibrated thermodynamic response and surrogate evidence |
| `analyses/hbta_topo_epcsaft_figure_pack/README.md` | Figure evidence record | Exact model-vs-data and flowsheet figure inputs |
| `docs/case_study/hbta_topo_evidence_acquisition_protocol.md` | Source acquisition protocol | Missing-data and source-evidence routing |
| Other `analyses/*epcsaft*` and source-case READMEs | Literature/application evidence | Independent benchmark or source-specific analyses, not application-independent Engine authority |

Live issues: #58 reactive ePC-SAFT LLE replacement, #73 source-traceable
parameter fitting, #76 Engine literature benchmark, #78 effective-species
Hubach fit, and #51 manuscript delivery. This study is parallel to MEA; it
tests the same application-independent Engine without sharing application
chemistry or fitted parameters.

## External numerical comparison

The sibling Institute for Design of Advanced Energy Systems (IDAES)
electrolyte nonrandom two-liquid (eNRTL) fitting routine is an inspected
comparison implementation. It shows a sparse shared-parameter/full-state
nonlinear program (NLP), but its active pressure residual is not a full solved
reactive bubble problem.
It is numerical-formulation evidence only and owns no GREPE equation, parameter,
dataset, decision, or manuscript claim.

## Bibliography authority

The configured project export is the single Better BibTeX authority.
Repository `references.bib` files are one-way projections and may
be curated for the manuscript, but citation-key or metadata corrections return
to Zotero and are re-exported rather than edited into multiple independent
authorities.
