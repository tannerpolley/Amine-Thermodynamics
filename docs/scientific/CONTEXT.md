# Scientific context

Status: official ePC-SAFT downstream application under Governance D-038.
This repository remains a separate sibling Git repository and consumes a
commit- and SHA-256-identified non-editable Engine wheel.

## Question and intended use

Determine which source-supported electrolyte Perturbed-Chain Statistical
Associating Fluid Theory (ePC-SAFT) model form and parameter set can predict
carbon-dioxide (CO2) pressure and liquid speciation for aqueous 30 mass %
monoethanolamine (MEA) from 315 to 360 K and, when the measured quantity and
thermodynamic derivative are
accepted, caloric quantities. Transfer a parameter set to the absorber-column
application only after it meets preregistered criteria on independent
observations within a declared pressure and CO2-loading domain.

This repository owns MEA chemistry hypotheses, source translations, data
partitions, model selection, parameter estimation, validation, uncertainty,
plots, and manuscript claims. The installed `epcsaft` wheel owns
equation-of-state evaluation, General Reactive Equilibrium and Phase
Equilibrium (GREPE), exact derivatives, and the public regression calculation.
The column and lithium repositories are downstream applications; they do not
define MEA thermodynamic equations or parameter adoption here.

## Current scientific status

The current manuscript is a fixed-parameter transfer and model-form evaluation.
It is not yet a predictive parameterization manuscript. Existing pressure-first,
Hilliard-only and fixed-observed-pressure calculations are diagnostic unless
their own retained evidence explicitly says otherwise. Optimizer termination is
reported as numerical evidence; it does not by itself accept or reject an
engineering parameter set.

Issue 70 retained a conservative supported-negative predictive decision. A
subsequent user-directed engineering selection froze the calorimetry-balanced
configuration as the best available MEA set. Its numerical authority is
`data/reference/MEA/parameters/best_available_mea_epcsaft/1/freeze.toml`.
The freeze supports bounded MEA calculations and manuscript comparison while
preserving the lack of independent validation, parameter uniqueness, and exact
evaluation-wheel replay. Absorber-column transfer remains unauthorized.

The authoritative scientific plan is
[`PREDICTIVE_MEA_PROGRAM.md`](PREDICTIVE_MEA_PROGRAM.md). GitHub issues are the
only work queue. Literature reviews, planned-analysis documents, issue mirrors,
analysis READMEs, and campaign reports provide evidence
or history; they do not silently supersede that plan or the tracker.

The audited classification of relevant Engine, MEA, Column, Lithium, and IDAES
documents is [`DOCUMENT_AUTHORITY_INDEX.md`](DOCUMENT_AUTHORITY_INDEX.md).

## Shared vocabulary

- **Neutral reference:** Held water plus one source-backed MEA association
  family and physical binary interaction parameters.
- **Induced association:** the fixed reciprocal Schick--Pabsch CO2--water 2B
  topology used throughout the MEA analyses.
- **Shell Born, solvent-only:** solvation-shell-modified Born with the
  solvent-composition relative permittivity.
- **Shell Born, ion-suppressed:** the same Born formulation with
  ion-fraction-suppressed relative permittivity.
- **Retained physical configuration:** the neutral, association,
  electrostatic, ionic, and reaction equations retained after the named
  binary, electrolyte, and model-selection comparisons.
- **Diagnostic fit:** a transparent optimization useful for sensitivity,
  runtime, or model-form diagnosis but not sufficient for adoption.
- **Best-available engineering freeze:** one immutable, hash-bound selection
  for bounded calculations when no candidate satisfies every predictive gate;
  its limitations remain part of the numerical authority.
- **Candidate eligible for adoption:** a complete fitted parameter record that
  meets its source, domain, numerical, identifiability, independent-validation,
  and immutable installed-wheel replay criteria.
- **Reduced-space regression:** shared parameters are optimized outside one
  GREPE solve per unique condition; each solve reports separate
  solver-convergence, numerical-convergence, and physical-validity statuses.
- **Full-space regression:** local equilibrium states and global fitted
  parameters are solved in one sparse multi-experiment nonlinear program
  (NLP). This is a planned numerical backend, not a different physical model.

## Authority map

1. Repository `AGENTS.md`, the pinned Engine identity, and current native
   GitHub issues.
2. The frozen best-available parameter record, this context, and
   `PREDICTIVE_MEA_PROGRAM.md`.
3. The source synthesis in
   `docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md`.
4. Frozen observation identities, dependency manifests, analysis descriptions,
   and exact calculated-value tables.
5. Historical planning documents, old transfer records, and issue mirrors.

The configured project Better BibTeX export is the citation authority.
`docs/latex/references.bib` is a one-way manuscript projection, not an
independent bibliography.

## Claim boundaries

This plan may ultimately support a predictive MEA parameterization inside a
declared temperature, composition, loading, pressure, and model-form domain,
with separate results for parameter estimation, model selection, and
independent validation. It may then supply a new thermodynamic parameter set
for separate column-side mapping and comparison in MEA-Absorption-Column.

It may not infer unique ionic, reaction, association, or electrostatic
parameters from pressure alone; treat source extrapolation as in-domain
evidence; call a local fixed-topology solve a global phase-stability proof; or
rewrite either manuscript's claims before its stated evidence gates pass.
