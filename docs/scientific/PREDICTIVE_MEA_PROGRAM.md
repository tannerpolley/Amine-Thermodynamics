# Predictive MEA ePC-SAFT scientific plan

- Status: authoritative scientific plan; native GitHub issues own execution
- Scope: model selection, regression, validation, and two manuscript boundaries
- Live work queue: native GitHub issues only
- Evidence/issue-state reconciliation: 2026-09-08; see the
  [repository audit](REPOSITORY_AUDIT_2026-09-08.md)

The complete audited document map is
[`DOCUMENT_AUTHORITY_INDEX.md`](DOCUMENT_AUTHORITY_INDEX.md).

## 1. Scientific endpoint

Select and parameterize one nine-species, five-reaction aqueous
monoethanolamine (MEA)--water (H2O)--carbon dioxide (CO2) electrolyte
Perturbed-Chain Statistical Associating Fluid Theory (ePC-SAFT) model that
predicts source-backed CO2 pressure and speciation observations and,
when supported, caloric observations. The primary
application use case is 30 mass % MEA from 315 to 360 K. Engine Issue #80
requests qualification across 293.15–393.15 K; this is a campaign target,
not an already validated domain. The pressure and
CO2-loading intervals are the intersection of the source, equation,
fitted-parameter, experimental-comparison, and downstream-property domains.
Compare the frozen candidate with observations not used for estimation or
model selection and replay it through one immutable installed Engine wheel.
Only a candidate that meets preregistered numerical and independent-comparison
criteria may support predictive manuscript claims or column-side transfer.

Direct analysis and validation whose calculation is performed by ePC-SAFT is
first built and debugged in `ePC-SAFT-project/analysis/` or `validation/`.
MEA-Thermodynamics may then reproduce the pinned method directly with an
accepted immutable packet and MEA-owned inputs. Engine Issue #80 owns the
current upstream bundle campaign; MEA Issues #83–#86 describe separate local
diagnostic work. Neither campaign has established an active MEA parameter set.

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
   permittivity as a historical diagnostic formulation; the retired
   fixed-parameter sensitivity rejected solvent-only and original-Born controls
   for that exact historical set.
5. Constrain the retained electrostatic parameters with direct evidence before
   the final reactive regression.

These qualification steps are scientific requirements, not a declaration that
the historical configuration is the current selected vector. The exploratory
incumbent in `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`
uses extended Born and solvent-only mass-fraction dielectric mixing, with
reaction-temperature and CO2 dispersion selections. Engine Issue #80 describes
a distinct source-tier campaign baseline. Preserve both identities; compare
them only through a declared same-row calculation. A favorable historical
ablation does not settle model choice for a changed parameter vector.

A paper reproduction is evidence for equations, parameter transfer, numerical
convergence or failure, or a limited comparison. It is not automatic adoption.
Methyldiethanolamine (MDEA) papers inform equation selection and failure
diagnosis but do not supply MEA reaction or species parameters without an
explicit, valid transformation.

## 4. Data authority and partitions

Closed Issue #62 retains reconciliation of the fixed-evaluation manuscript
inventory and the predictive inventory. Row counts from different analyses
still require exact input-table identity and hash; closure does not permit
blending different inventories into one claimed dataset.

Each observation records source and row identity, reported quantity, unit,
basis, temperature, apparent composition/loading, uncertainty or a justified
preregistered scale, transformation, covariance group when applicable, domain
status, and partition. Structural zeros, measured zeros, aggregate
observations, inferred context, and censoring remain distinct.

Every row already opened during a candidate comparison is model-selection
evidence, including rows previously labeled reserved. Closed Issue #14 retains
the earlier independent-comparison decision; a future campaign must freeze a
genuinely untouched replacement partition before access. If none exists,
independent validation remains blocked. The local `holdout-evaluations.csv`
already records access to Xu pressure and Kim–Svendsen 120 °C heat during
reaction selection. These are available diagnostic comparisons, not untouched
validation for that selection. Reconcile exact row access with the Engine
campaign before accepting its separately declared holdouts. Domain-challenge rows
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

The current manuscript supports fixed-parameter comparisons and the negative
predictive decision. Issue #68's later scope comment narrows its earlier
predictive body to that supported-negative account. Closed #13/#14/#70 are
historical outcomes, not evidence of a predictive fit. A future predictive
revision requires a newly reviewed candidate, replacement independent
validation, identifiability and uncertainty evidence. Issue #10 remains the
final submission gate. No exploratory notebook result is promoted to the
manuscript by this roadmap update.

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

## 9. Issue ownership as checked on 8 September 2026

- Closed #62–#65/#67: observation, neutral, electrostatic, induced-association
  and configuration evidence for the historical campaign.
- Closed #13/#14/#70: regression, independent-comparison and supported-negative
  parameter decision. Closed #61/#66 retain superseded hierarchy decisions.
- Open #83/#84: F/S and ionic screens; later reports retain diagnostic results.
- Open #85: reviewed shared start-volume correction reported complete in
  `codex/reaction-partition-fs-study`, not integrated into this checkout.
- Open #86: corrected v4 ionic comparison reported complete with no
  non-degrading direction and ten certificate failures. Underlying work is
  uncommitted in its owning checkout. Open state does not mean it needs rerunning.
- Open #68/#10: supported-negative manuscript evolution and submission gate.

[Engine #80](https://github.com/tannerpolley/ePC-SAFT/issues/80) owns the final
full-range bundle; [#119](https://github.com/tannerpolley/ePC-SAFT/issues/119)
owns minimal CO2–MEA calibration using native Ceres, with its own prerequisites
and immutable wheel. This plan does not replace that issue's parameter block,
scales, folds or derivative gates with local exploratory choices. Cross-repo
historical issues in the authority index are navigation, not current task
state; reread their owners before executing work. No GitHub issue was changed
by this audit.

## 10. Document disposition

| Document | Durable role | Authority now |
|---|---|---|
| `docs/scientific/docs/scientific/CONTEXT.md` | MEA question, vocabulary, authority, claims | Authoritative scientific definition named by repository guidance and issue #70 |
| This plan | Model selection, fitting, validation, and manuscript sequence | Authoritative planning record; native GitHub issues own execution |
| `docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md` | Primary/secondary source synthesis and retained-model scientific basis | Current evidence authority |
| `analyses/reactive_epcsaft_parameter_evidence/pressure_first/README.md` | Executed neutral qualification and current practical sequence | Analysis record only |
| Engine GREPE plan | Public equilibrium and regression callable design | Authoritative in the Engine repository |
| Engine coupled-regression master plan | Pre-GREPE readiness and source inventory | Historical source/provenance record |
| Column August 27 plan and upstream handoff | Earlier integration sequence | Historical; Engine #30/#31 are closed |
| Column reactive claim-boundary report | Fixed-chemistry and feasibility evidence | Retained analysis result |
| Lithium `docs/scientific/**` | Parallel configured reactive-LLE study | Authority is defined in the Lithium repository |

No document in this table is a second issue tracker. When a decision changes,
the successor names the superseded document and the GitHub issue records the
work.

## 11. Prioritized evidence sequence

This is a scientific dependency order, not authorization to run new campaigns.

| Priority | Question and smallest useful work | Evidence required to advance |
|---|---|---|
| 1 — numerical identity | Reconcile the reviewed #85 v4 shared correction and #86 result tables with their owner before changing this checkout. Read retained results before rerunning anything. | Exact source/input/wheel hashes, preserved v3 history, rejected snapshots, and confirmation of which code is present. Current v3 publication cannot be relabeled corrected. |
| 2 — numerical coverage | Resolve the remaining start-sensitive certificate failures under a declared same-model start/branch policy. | Same-row incumbent/candidate predictions, all failed targets and denominators, conservation/reaction/EOS certificates, starts, density and branch diagnostics; no arbitrary density cutoff or claim of global stability. |
| 3 — source qualification | Reconcile neutral, reaction, ionic, dielectric and caloric evidence and their temperature/concentration domains. | Exact locators and transforms; classify direct observations, inferred context, censored zeros, source uncertainty and extrapolation. MEA–water's fitted high-temperature domain and R4/R5's limited source domain stay explicit. Seek direct ionic/volumetric or dielectric information only where it discriminates the proposed coordinate. |
| 4 — identifiable estimation | Follow the upstream minimal CO2–MEA fit separately from the local fixed-EOS chemistry studies. For local refinement, select only coordinates distinguished by direct speciation and admitted heat as well as pressure. | Exact derivative checks, scaled weighted Jacobian rank and correlated directions, active bounds, deterministic starts and bounded parameter profiles. Do not fit all tabulated values or trade off groups silently. Failed directions from #86 are not estimates of uncertainty. |
| 5 — model selection | Compare eligible structures on frozen source/campaign blocks with declared residual scales. | Complete evaluated-row tables, paired masks and failure accounting; pressure, each speciation group and heat reported separately. Calorimetry needs exact paired endpoints, reference/gauge identity and thermodynamic K(T)/enthalpy consistency. |
| 6 — independent validation | Freeze a candidate and genuinely unused data before evaluating it. | Row-access audit, untouched source/campaign blocks in the intended domain, preregistered error limits and uncertainty; if none are available, retain a calibrated diagnostic claim. Previously opened Xu/120 °C rows cannot supply this gate. |
| 7 — adoption and delivery | Repair/review the writer before any future adoption, then serialize and replay exactly the scored vector. | R1–R5, EOS, sources, wheel, data and output hashes agree; all selected-vector coverage and scientific gates pass. The old candidate replay changed R1/R3 that the saved vector omitted. Preserve older versions and reasons, then render/package only current verified results. |
| 8 — intended use | Revise the thermodynamics manuscript from accepted evidence, then allow separately reviewed column integration. | Author-approved manuscript claims and exact figures; column composition/activity/enthalpy mappings, transport/kinetic admission, numerical convergence and independent NCCC comparisons. A ZIP or film-input check alone is not predictive authorization. |

The smallest next scientific action is to inspect the retained #85/#86 corrected
failure evidence and agree on the treatment of remaining start-sensitive states
before any joint comparison. Do not repeat the old six-direction screen or
launch a broad publication refresh from this v3 checkout. Source acquisition,
fitting, adoption and cross-checkout integration require their own scoped work.

The optional simultaneous full-space formulation can proceed as a separate
Engine algorithm study with stated problem size, hardware, runtime, memory,
and convergence metrics. It does not reorder or bypass these scientific
decisions.
