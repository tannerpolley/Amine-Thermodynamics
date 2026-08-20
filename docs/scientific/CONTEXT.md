# Scientific context

Status: official ePC-SAFT downstream application under Governance D-038.
This repository remains a separate sibling Git repository and consumes a
commit- and SHA-256-identified non-editable Engine wheel.

## Question and intended use

Determine which source-supported ePC-SAFT model form and parameter set can
predict CO2 pressure, liquid speciation, and eventually caloric behavior for
the aqueous MEA--H2O--CO2 system over a declared domain, then provide one
immutable validated candidate to the absorber-column application.

This repository owns MEA chemistry hypotheses, source translations, data
partitions, model selection, parameter estimation, validation, uncertainty,
plots, and manuscript claims. The generic installed `epcsaft` wheel owns EOS
evaluation, GREPE equilibrium, exact derivatives, and generic regression
mechanics. The column and lithium repositories are downstream applications;
they do not define MEA thermodynamic equations or parameter adoption here.

## Current scientific status

The current manuscript is a fixed-parameter transfer and model-form evaluation.
It is not yet a predictive parameterization manuscript. Existing pressure-first,
Hilliard-only, fixed-observed-pressure, and M0--M7 calculations are diagnostic
unless their own retained evidence explicitly says otherwise. A lower SSE,
optimizer termination, or visually improved curve does not promote a model or
parameter set.

The live predictive program is
[`PREDICTIVE_MEA_PROGRAM.md`](PREDICTIVE_MEA_PROGRAM.md). GitHub issues are the
only work queue. Literature reviews, roadmaps, Superpowers plans, issue mirrors,
analysis READMEs, and campaign reports provide evidence or history; they do not
silently supersede the program or tracker.

The audited classification of relevant Engine, MEA, Column, Lithium, and IDAES
documents is [`DOCUMENT_AUTHORITY_INDEX.md`](DOCUMENT_AUTHORITY_INDEX.md).

## Shared vocabulary

- **B0:** the separately reproduced neutral Baygi comparator. It is outside the
  electrolyte M0--M7 factor hierarchy.
- **M0:** the common qualified electrolyte reference with the declared direct
  Born/electrostatic basis.
- **M1:** the source-qualified SSM+DS modified-Born singleton.
- **M2:** the complete explicit polar DD+QQ+DQ singleton.
- **M3:** a source-qualified induced-association singleton that does not double
  count the retained association model.
- **M4--M7:** only combinations whose singleton prerequisites pass and whose
  exact composition is frozen before reactive regression.
- **Diagnostic fit:** a transparent optimization useful for sensitivity,
  runtime, or model-form diagnosis but not sufficient for adoption.
- **Promotable candidate:** a complete fitted parameter document that passes
  source, domain, numerical, identifiability, reserved-validation, and immutable
  installed-artifact replay requirements.
- **Reduced-space regression:** shared parameters are optimized outside one
  certified GREPE solve per unique condition.
- **Full-space regression:** local equilibrium states and global fitted
  parameters are solved in one sparse multi-experiment NLP. This is a planned
  numerical backend, not a different physical model.

## Authority map

1. Repository `AGENTS.md`, the pinned Engine identity, and current native
   GitHub issues.
2. This context and `PREDICTIVE_MEA_PROGRAM.md`.
3. The source synthesis in
   `docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md`.
4. Frozen data manifests, analysis manifests, exact result tables, and model
   ladder analysis records.
5. Historical roadmaps, Superpowers artifacts, old handoffs, and issue mirrors.

The configured Better BibTeX export
`/home/tnnrpolley21/Zotero/exports/references.bib` is the citation authority.
`docs/latex/references.bib` is a one-way manuscript projection, not an
independent bibliography.

## Claim boundaries

This program may ultimately support a predictive MEA parameterization inside a
declared temperature, composition, loading, pressure, and model-form domain,
with separate results for calibration, model selection, and reserved
validation. It may then support a separately validated predictive thermodynamic
lane in MEA-Absorption-Column.

It may not infer unique ionic, reaction, association, or electrostatic
parameters from pressure alone; treat source extrapolation as in-domain
evidence; call a local fixed-topology solve a global phase-stability proof; or
rewrite either manuscript's claims before its stated evidence gates pass.
