# Predictive MEA ePC-SAFT program

- Status: canonical program definition
- Scope: model selection, regression, validation, and two manuscript boundaries
- Live work queue: native GitHub issues only

The complete audited document map is
[`DOCUMENT_AUTHORITY_INDEX.md`](DOCUMENT_AUTHORITY_INDEX.md).

## 1. Scientific endpoint

Select and parameterize one nine-species, five-reaction aqueous
MEA--H2O--CO2 ePC-SAFT model that predicts source-backed CO2 pressure and
speciation observations and, when supported, caloric observations. Validate
the frozen candidate on untouched campaign blocks and replay it through one
immutable installed Engine wheel. Only then revise the MEA thermodynamics
manuscript toward predictive claims and expose the candidate to the absorber
column as a new, separately validated lane.

The endpoint is not the lowest available SSE. It is a reproducible model-form
decision and parameter document with an explicit domain, source basis,
identifiability evidence, failure accounting, exact plotted row tables, and
bounded claims.

## 2. System and equations

The liquid phase contains CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3--, H3O+,
and OH-. The independent reaction basis, standard states, units, temperature
correlations, and validity domains are owned by the current chemistry catalog
and must remain declared rather than inferred from reaction names. The vapor
support contains only source- and model-supported neutral volatile species.
Declared phases and species support define each GREPE problem; no application,
paper, or component name selects a solver route.

Every equilibrium result must separately establish material and charge
balance, reaction/electrochemical equilibrium, phase support, pressure or
fugacity closure, local branch identity, numerical convergence, and derivative
availability. Local fixed-topology equilibrium does not establish global phase
stability.

## 3. Model hierarchy and decisions

The literature synthesis
[`amine-epcsaft-model-hierarchy-literature-review.md`](../ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md)
is the source authority for the exact equations, sources, parameter families,
and model-form hypotheses. Its hierarchy is applied as follows:

1. Reproduce B0 as a neutral literature comparator; do not silently import its
   parameters into the electrolyte hierarchy.
2. Qualify the common M0 neutral and electrolyte reference inputs.
3. Compare M0 and M1 to isolate the Born/permittivity formulation.
4. Evaluate M2 and M3 as complete singleton changes.
5. Construct M4--M7 only from singleton factors that survive their own source,
   binary, numerical, and identifiability evidence.
6. Freeze one selected model form before the final reactive regression.

A paper reproduction is evidence for equations, parameter transfer, numerical
behavior, or a limited benchmark. It is not automatic adoption. MDEA papers
inform architecture and failure diagnosis but do not supply MEA reaction or
species parameters without an explicit, valid transformation.

## 4. Data authority and partitions

Issue #62 owns reconciliation of the fixed-evaluation manuscript inventory and
the predictive inventory. Until it closes, row counts from different analyses
must retain their exact manifest identity and may not be blended into one
claimed dataset.

Each observation records source and row identity, reported quantity, unit,
basis, temperature, apparent composition/loading, uncertainty or a justified
preregistered scale, transformation, covariance group when applicable, domain
status, and partition. Structural zeros, measured zeros, aggregate
observations, inferred context, and censoring remain distinct.

Campaign-blocked training, model-selection, and untouched reserved partitions
are frozen before model comparison. Domain-challenge rows remain visible but
do not become scoring rows merely because a solver returns a value. Plotting
uses the immutable evaluated-row table stored by `FitResult`; it never reruns
thermodynamics.

The single citation authority is
`/home/tnnrpolley21/Zotero/exports/references.bib`. Source-driving equations,
parameters, data, and tolerances require exact locators in the primary paper,
supplement, or verified companion.

## 5. Parameter ladder

The scientific order controls what may be learned; it is independent of the
numerical backend.

1. **Source and identity freeze.** Freeze species, reaction basis, standard
   states, data rows, partitions, source validity domains, Engine wheel, and
   parameter-document identities.
2. **Pure neutral qualification.** Refit or requalify pure MEA, water, and CO2
   parameters separately for every model form that changes the neutral EOS.
3. **Neutral binary qualification.** Fit source-supported binary interaction
   terms against independent binary data. Test induced association only with a
   complete source topology and independent evidence.
4. **Electrolyte/solvation qualification.** Constrain ionic size, dispersion,
   Born, and relative-permittivity families with direct or transferable
   electrolyte evidence before using reactive pressure to refine them.
5. **Reaction/speciation qualification.** Hold source reaction correlations
   fixed initially. Use direct same-state speciation and, when available,
   caloric evidence to test a small correction block on one declared independent
   reaction basis. Keep K(T) and reaction enthalpy thermodynamically linked.
6. **Reactive pressure fit.** Fit true configured reactive VLE/bubble
   observations with complete equilibrium and failure accounting. Pressure
   cannot independently identify every preceding family.
7. **Joint refinement.** Refit only the retained, identifiable coordinates
   against pressure, speciation, volumetric/dielectric, and caloric families,
   with each family's diagnostics reported separately.
8. **Model selection and uncertainty.** Select on campaign-blocked evidence,
   inspect active bounds and scaled Jacobian rank/conditioning, then perform
   justified profiles or bootstrap analyses.
9. **Freeze and replay.** Refit the selected structure on the allowed
   calibration data, export a new immutable candidate, replay with the pinned
   installed wheel, and evaluate the untouched reserved blocks once.

Fitting every available table entry simultaneously is not the default. It is
allowed only after the ladder establishes which coordinates are defensible and
identifiable.

## 6. Numerical architecture

The implemented near-term path is reduced space:

\[
\boldsymbol\theta \rightarrow
\{\text{certified GREPE solve for condition }j\}_{j=1}^{N}
\rightarrow \mathbf r(\boldsymbol\theta),\;\mathbf J(\boldsymbol\theta).
\]

Regression/Ceres owns parameter coordinates, bounds, residual transforms,
covariance whitening, multistart, and diagnostics. GREPE/Ipopt owns each local
equilibrium state and exact total output derivatives. Unique conditions should
be cached, batched, and evaluated independently where safe.

The planned mature path is a generic sparse full-space NLP. Each experiment has
local pressure, compositions, densities, reaction coordinates, and equilibrium
constraints; the selected parameters are global variables; one objective sums
the declared residual rows. The backend must preserve the public GREPE request
and observation schema, exact sparse derivatives, per-state certification,
failure semantics, and the same `FitResult` table. It may not add MEA-, CO2-,
bubble-, or paper-specific branches.

IDAES demonstrates that a block-arrow simultaneous formulation can be
efficient. Its current eNRTL example is not a full reactive bubble solve and is
therefore architecture evidence only, not a parity target or model authority.

## 7. Verification, validation, and uncertainty

Keep the following distinct:

- **Code verification:** analytic/manufactured identities, conservation,
  limiting behavior, and exact derivative comparisons establish that the
  implementation represents the declared equations.
- **Solution verification:** residual certificates, scaling, start dispersion,
  branch identity, solver convergence, and reduced/full-space agreement on
  fixed local branches establish numerical adequacy.
- **Model validation:** source observations not used for a fit establish
  physical predictive performance inside the intended domain.
- **Uncertainty:** measurement, input, parameter, numerical, and model-form
  uncertainty are reported separately and propagated only when supported.

Tolerances retain their physical role. Solver and conservation tolerances are
not weakened to improve fit coverage. Diagnostic residual scales may be used
only when transparent, preregistered, and sensitivity-tested; they are not
promotion evidence.

## 8. Manuscript gates

### MEA-Thermodynamics

The current fixed-parameter manuscript remains intact until issues #61--#67
freeze a selected model and issues #13 and #14 complete predictive regression,
reserved validation, identifiability, and uncertainty. Issue #68 then owns the
claim-by-claim manuscript evolution. Issue #10 is the final submission gate.

The revised paper must distinguish literature reproduction, calibration,
model selection, reserved validation, and domain challenges. Every model-vs-
data figure includes the exact plotted rows and fitted parameter table or an
unambiguous linked table.

### MEA-Absorption-Column

The existing fixed-chemistry/fugacity benchmark remains a separate baseline.
The column manuscript gains a predictive third lane only after MEA-
Thermodynamics exports one immutable validated candidate and the column repo
passes its own integration, convergence, and NCCC comparison work. Column
agreement does not retroactively validate the thermodynamic fit, and the
thermodynamics paper does not claim absorber performance.

## 9. Live issue graph

- #61: model-hierarchy parent
- #62: observation-inventory reconciliation
- #63: B0 and common M0 qualification
- #64: M0/M1 Born attribution
- #65: M3 induced-association adjudication
- #66: M2 polar singleton
- #67: conditional M4--M7 combinations and selected-model freeze
- #13: predictive regression through the generic equilibrium interface
- #14: reserved validation and identifiability
- #68: predictive manuscript evolution
- #10: final predictive-manuscript readiness

Engine issues #44 and #48 own the generic and MEA-intensive GREPE capability;
#50 owns the current typed-failure defect and #51 owns the optional generic
simultaneous regression backend. Column issue #3 owns its current
electrolyte-path validation and Column issue #12 owns its context and
predictive-manuscript integration program. Lithium issues #58, #73, #76, and
#78 are a parallel downstream GREPE program and do not gate MEA parameter
adoption.

## 10. Document disposition

| Document | Durable role | Authority now |
|---|---|---|
| `docs/scientific/CONTEXT.md` | MEA question, vocabulary, authority, claims | Canonical |
| This program | End-to-end model-selection, fitting, validation, manuscript sequence | Canonical |
| `docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md` | Primary/secondary source synthesis and M0--M7 scientific basis | Current evidence authority |
| `analyses/phase3/ionic_epcsaft_regression/model_ladder/README.md` | Exact executed model-ladder analysis and current results | Analysis record only |
| `docs/roadmaps/predictive_reactive_vle_regression.md` | Earlier preregistration snapshot | Historical; superseded here |
| `docs/superpowers/PROJECT_CONTEXT.md` and `docs/superpowers/**` | Previous planning/milestone system and issue mirrors | Historical organization evidence |
| Engine GREPE plan | Generic public equilibrium and regression architecture | Upstream canonical design |
| Engine coupled-regression master plan | Pre-GREPE readiness and source inventory | Historical source/provenance record |
| Column August 27 plan and upstream handoff | Earlier integration sequence | Historical; Engine #30/#31 are closed |
| Column reactive claim-boundary report | Fixed-chemistry and feasibility evidence | Retained analysis result |
| Lithium `docs/scientific/**` | Parallel configured reactive-LLE program | Canonical in Lithium repository |

No document in this table is a second issue tracker. When a decision changes,
the successor names the superseded document and the GitHub issue records the
work.

## 11. Immediate sequence

1. Finish and inspect the current fixed-K global multi-temperature fit as a
   diagnostic; do not reinterpret it as selected-model promotion.
2. Close the inventory and model-hierarchy prerequisites in #62--#67.
3. Use #13 to execute the selected model through the generic interface with
   complete row/failure and derivative evidence.
4. Use #14 for untouched validation and practical identifiability.
5. Freeze one candidate, revise the thermodynamics manuscript through #68,
   then begin the column's predictive third lane.

The optional simultaneous full-space backend can proceed as an Engine
performance capability in parallel, but it does not reorder or bypass these
scientific gates.
