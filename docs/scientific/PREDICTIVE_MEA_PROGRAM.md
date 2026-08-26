# Predictive MEA ePC-SAFT scientific plan

- Status: authoritative scientific plan; native GitHub issues own execution
- Scope: model selection, regression, validation, and two manuscript boundaries
- Live work queue: native GitHub issues only

The complete audited document map is
[`DOCUMENT_AUTHORITY_INDEX.md`](DOCUMENT_AUTHORITY_INDEX.md).

## 1. Scientific endpoint

Select and parameterize one nine-species, five-reaction aqueous
monoethanolamine (MEA)--water (H2O)--carbon dioxide (CO2) electrolyte
Perturbed-Chain Statistical Associating Fluid Theory (ePC-SAFT) model that
predicts source-backed CO2 pressure and speciation observations and,
when supported, caloric observations. The primary
application domain is 30 mass % MEA from 315 to 360 K; the pressure and
CO2-loading intervals are the intersection of the source, equation,
fitted-parameter, experimental-comparison, and downstream-property domains.
Compare the frozen candidate with observations not used for estimation or
model selection and replay it through one immutable installed Engine wheel.
Only a candidate that meets preregistered numerical and independent-comparison
criteria may support predictive manuscript claims or column-side transfer.

A best-available engineering set may be frozen earlier for bounded calculation
and comparison when its exact values, source identities, numerical behavior,
failed-case accounting, and limitations are immutable. This selection does not
convert a solver termination label into a scientific verdict, and it does not
inherit the predictive or transfer claims reserved for an independently
validated set.

The endpoint is not the lowest available sum of squared residuals. It is a
retained model-form decision and parameter record with an explicit domain,
source basis, code revision, installed-wheel identity, input hashes,
identifiability evidence, failed-state accounting, exact plotted row tables,
agreement criteria, uncertainty, and bounded claims.

## 2. System and equations

The liquid phase contains CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3--, H3O+,
and OH-. The independent reaction basis, standard states, units, temperature
correlations, and validity domains are owned by the current chemistry catalog
and must remain declared rather than inferred from reaction names. The vapor
support contains only source- and model-supported neutral volatile species.
Declared phases and species support define each General Reactive Equilibrium
and Phase Equilibrium (GREPE) problem; no application, paper, or chemical
species name selects a solver route.

Every equilibrium result must separately establish material and charge
balance, reaction/electrochemical equilibrium, phase support, pressure or
fugacity closure, local branch identity, numerical convergence, and derivative
availability. Local fixed-topology equilibrium does not establish global phase
stability.

## 3. Retained model family and decisions

The literature synthesis
[`amine-epcsaft-model-hierarchy-literature-review.md`](../ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md)
is the source authority for the exact equations, sources, parameter families,
and retained physical interactions. This plan applies it as follows:

1. Qualify one neutral Perturbed-Chain Statistical Associating Fluid Theory
   (PC-SAFT) reference under the Held water family.
2. Keep the Schick--Pabsch reciprocal CO2--water induced-association topology
   fixed in every subsequent MEA calculation.
3. Qualify `k_MEA,H2O`, `k_CO2,H2O(T)`, and, when supported by physical neutral
   evidence, `k_CO2,MEA` before reactive fitting.
4. Retain shell-modified Born with ion-fraction-suppressed relative
   permittivity for practical MEA calculations; the fixed-parameter sensitivity
   rejects solvent-only and original-Born controls under the current parameter
   set.
5. Constrain the retained electrostatic parameters with direct evidence before
   the final reactive regression.

A paper reproduction is evidence for equations, parameter transfer, numerical
convergence or failure, or a limited comparison. It is not automatic adoption.
Methyldiethanolamine (MDEA) papers inform equation selection and failure
diagnosis but do not supply MEA reaction or species parameters without an
explicit, valid transformation.

## 4. Data authority and partitions

Issue #62 owns reconciliation of the fixed-evaluation manuscript inventory and
the predictive inventory. Until it closes, row counts from different analyses
must retain their exact input-table identity and hash and may not be blended
into one claimed dataset.

Each observation records source and row identity, reported quantity, unit,
basis, temperature, apparent composition/loading, uncertainty or a justified
preregistered scale, transformation, covariance group when applicable, domain
status, and partition. Structural zeros, measured zeros, aggregate
observations, inferred context, and censoring remain distinct.

Every row already opened during a candidate comparison is model-selection
evidence, including rows previously labeled reserved. Issue #14 freezes a
genuinely untouched replacement partition before access; if none exists, the
plan records that independent validation is blocked. Domain-challenge rows
remain visible but do not become scoring rows merely because a solver returns
a value. Plotting uses the immutable evaluated-row table stored by `FitResult`;
it never reruns thermodynamics.

The single citation authority is the configured project Better BibTeX export.
Source-driving equations, parameters, data, and tolerances require exact
locators in the primary paper, supplement, or verified companion.

## 5. Parameter ladder

The scientific order controls what may be learned; it is independent of the
numerical backend.

1. **Source and identity freeze.** Freeze species, reaction basis, standard
   states, data rows, partitions, source validity domains, Engine wheel, and
   parameter-document identities.
2. **Pure neutral qualification.** Refit or requalify pure MEA, water, and CO2
   parameters under the retained neutral PC-SAFT equation.
3. **Neutral binary qualification.** Fit source-supported binary interaction
   terms against independent binary data while retaining the fixed reciprocal
   induced-association topology.
4. **Electrolyte/solvation qualification.** Constrain ionic size, dispersion,
   Born, and relative-permittivity families with direct or transferable
   electrolyte evidence before using reactive pressure to refine them.
5. **Reaction/speciation qualification.** Hold source reaction correlations
   fixed initially. Use direct same-state speciation to test a small correction
   block on one declared independent reaction basis. Calorimetry enters fitting
   or adoption only after its measured quantity, source basis, uncertainty, and
   application-independent Engine derivative are accepted. Keep K(T) and
   reaction enthalpy thermodynamically linked.
6. **Reactive pressure fit.** Fit true configured reactive VLE/bubble
   observations with complete equilibrium and failure accounting. Pressure
   cannot independently identify every preceding family. Every admitted row
   reports separate solver-convergence, numerical-convergence, and
   physical-validity statuses; no row is dropped, replaced by a numeric
   penalty, or hidden from the fitted objective or comparison table.
7. **Joint refinement.** Refit only the retained, identifiable coordinates
   against pressure, speciation, and admitted volumetric, dielectric, or
   caloric observations, with each measured quantity reported separately.
8. **Model selection and uncertainty.** Select on campaign-blocked evidence,
   inspect active bounds and scaled Jacobian rank/conditioning, then perform
   justified profiles or bootstrap analyses.
9. **Freeze and replay.** Refit the selected structure on the allowed
   calibration data, export a new immutable candidate, replay with the pinned
   installed wheel, and evaluate the frozen replacement independent-comparison
   partition once.

Fitting every available table entry simultaneously is not the default. It is
allowed only after the ladder establishes which coordinates are defensible and
identifiable.

## 6. Numerical formulation

The implemented near-term path is reduced space:

\[
\boldsymbol\theta \rightarrow
\{\text{GREPE solve meeting residual and conservation tolerances for }j\}_{j=1}^{N}
\rightarrow \mathbf r(\boldsymbol\theta),\;\mathbf J(\boldsymbol\theta).
\]

Regression/Ceres owns parameter coordinates, bounds, residual transforms,
covariance whitening, multistart, and diagnostics. GREPE/Ipopt owns each local
equilibrium state and exact total output derivatives. Unique conditions should
be cached, batched, and evaluated independently where safe.

The optional application-independent path is a sparse full-space nonlinear
program (NLP). Each experiment has local pressure, compositions, densities,
reaction coordinates, and equilibrium constraints; the selected parameters
are global variables; one objective sums the declared residual rows. The
backend must preserve the public GREPE request and observation schema, exact
sparse derivatives, per-state numerical acceptance, failure semantics, and the
same `FitResult` table. It may not add MEA-, CO2-, bubble-, or paper-specific
branches.

The Institute for Design of Advanced Energy Systems (IDAES) demonstrates a
block-arrow simultaneous formulation for its reported electrolyte nonrandom
two-liquid (eNRTL) example. That example is not a full reactive bubble
calculation, so it is a numerical-formulation reference rather than a runtime
parity target or thermodynamic-model authority.

## 7. Verification, validation, and uncertainty

Keep the following distinct:

- **Code verification:** analytic/manufactured identities, conservation,
  limiting behavior, and exact derivative comparisons establish that the
  implementation represents the declared equations.
- **Solution verification:** residual certificates, scaling, start dispersion,
  branch identity, solver convergence, and reduced/full-space agreement on
  fixed local branches establish numerical adequacy.
- **Model validation:** source observations not used for fitting or model
  selection quantify pressure and speciation prediction error inside the
  intended domain against preregistered metrics and uncertainty.
- **Uncertainty:** measurement, input, parameter, numerical, and model-form
  uncertainty are reported separately and propagated only when supported.

Tolerances retain their physical role. Solver and conservation tolerances are
not weakened to improve fit coverage. Diagnostic residual scales may be used
only when transparent, preregistered, and sensitivity-tested; they are not
promotion evidence.

## 8. Manuscript gates

### MEA-Thermodynamics

The current fixed-parameter manuscript remains intact until neutral and
electrostatic qualification freeze a selected model and issues #13 and #14
complete predictive regression, replacement independent validation,
identifiability, and uncertainty. Issue #68 then owns the claim-by-claim
manuscript evolution. Issue #10 is the final submission gate.

The revised paper must distinguish literature reproduction, calibration,
model selection, independent validation, and domain challenges. Every model-vs-
data figure includes the exact plotted rows and fitted parameter table or an
unambiguous linked table.

### MEA-Absorption-Column

The existing fixed-chemistry/fugacity benchmark remains a separate baseline.
The column manuscript gains a predictive third lane only after MEA-
Thermodynamics exports one immutable candidate that met preregistered pressure,
speciation, numerical, identifiability, and uncertainty criteria on independent
observations, and the column repository passes its own mapping, convergence,
and National Carbon Capture Center (NCCC) comparisons. Column agreement does
not retroactively validate the thermodynamic fit, and the
thermodynamics paper does not claim absorber CO2 capture, energy duty,
temperature profile, or hydraulic behavior.

## 9. Live issue graph

- #62: observation-inventory reconciliation
- #63: neutral pure and binary qualification
- #64: shell-Born permittivity sensitivity and independent electrostatic evidence
- #65: reciprocal CO2--water induced-association qualification
- #67: retained physical-configuration freeze
- #13: predictive regression through the typed public equilibrium and
  regression callables
- #14: independent validation and identifiability
- #70: parameter-record assembly and predictive-claim decision
- #68: predictive manuscript evolution
- #10: final predictive-manuscript readiness

Issues #61 and #66 are closed historical records for the superseded M-number
factorial plan and the supported negative polar-model decision, respectively.

Engine issues #44 and #48 own the application-independent and MEA-intensive
GREPE calculations; #50 owns the current typed-failure defect, and #51 owns the
optional simultaneous regression backend. Column issue #3 owns its current
electrolyte-path validation and Column issue #12 owns its context and
predictive-manuscript revision plan. Lithium issues #58, #73, #76, and
#78 are a parallel downstream GREPE study and do not gate MEA parameter
adoption.

## 10. Document disposition

| Document | Durable role | Authority now |
|---|---|---|
| `docs/scientific/CONTEXT.md` | MEA question, vocabulary, authority, claims | Authoritative scientific definition named by repository guidance and issue #70 |
| This plan | Model selection, fitting, validation, and manuscript sequence | Authoritative planning record; native GitHub issues own execution |
| `docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md` | Primary/secondary source synthesis and retained-model scientific basis | Current evidence authority |
| `analyses/phase3/ionic_epcsaft_regression/pressure_first/README.md` | Executed neutral qualification and current practical sequence | Analysis record only |
| Engine GREPE plan | Public equilibrium and regression callable design | Authoritative in the Engine repository |
| Engine coupled-regression master plan | Pre-GREPE readiness and source inventory | Historical source/provenance record |
| Column August 27 plan and upstream handoff | Earlier integration sequence | Historical; Engine #30/#31 are closed |
| Column reactive claim-boundary report | Fixed-chemistry and feasibility evidence | Retained analysis result |
| Lithium `docs/scientific/**` | Parallel configured reactive-LLE study | Authority is defined in the Lithium repository |

No document in this table is a second issue tracker. When a decision changes,
the successor names the superseded document and the GitHub issue records the
work.

## 11. Immediate sequence

1. Close the observation-inventory and equation/parameter prerequisites in
   #62--#67.
2. Use #13 to estimate the retained fitted coordinates through the typed public
   equilibrium and regression callables with complete row, failure, and
   derivative evidence.
3. Use #14 to audit row access, freeze replacement independent observations,
   and assess identifiability and uncertainty.
4. Use #70 to assemble one parameter record and decide whether the evidence
   supports predictive pressure and speciation claims.
5. Revise the thermodynamics manuscript through #68 only after that decision,
   then begin the column's predictive third lane.

The optional simultaneous full-space formulation can proceed as a separate
Engine algorithm study with stated problem size, hardware, runtime, memory,
and convergence metrics. It does not reorder or bypass these scientific
decisions.
