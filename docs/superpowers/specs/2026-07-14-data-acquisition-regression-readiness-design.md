# MEA Data Acquisition and Regression Readiness Design

## Context

The project has enough experimental evidence to support model diagnostics, but not yet a regression-ready evidence system that can distinguish neutral-solvent, reactive-equilibrium, and electrolyte parameter effects. The active Phase 3 summary currently names 161 pressure targets and 74 speciation states, but it records `attempted_optimization=false` and `nfev=0`. Its parameter values are therefore provisional inputs evaluated by diagnostics, not the result of a completed coupled regression.

The repository audit found that the immediate bottleneck is not simply a lack of literature. A substantial reserve of already-local evidence is excluded from active targets or remains embedded in source transcriptions:

- `verified`: Six raw VLE tables contain 327 observations, while `data/reference/MEA/observations/vapor_liquid_equilibrium/Combined_VLE.csv` selects 161 observations, all at 30 wt% MEA. The 166 unselected rows include concentration and temperature regimes that are directly relevant to transferability.
- `verified`: The source speciation tables contain 111 state rows and the Wong Raman extraction contains 71 species points. Active regression-facing code uses only 74 states at 30 wt% MEA, leaving 37 tabulated 15/20 wt% states unused and all Wong rows outside the active target path.
- `verified`: The local Amundsen transcription contains 68 loaded-density and 75 loaded-viscosity measurements in addition to the 70 unloaded measurements already machine-readable.
- `verified`: The local Wong transcription contains 41 high-pressure loading observations at 303.15--323.15 K and pressures up to about 60 bar, but no Wong VLE CSV exists.
- `verified`: Machine-readable MEA--water dielectric, loaded-MEA pH, and direct MEAH+/carbamate ionic-activity datasets do not exist in the repository.
- `verified`: Current sensitivity diagnostics rank `k_ij__MEA__H2O`, `k_ij__CO2__MEA`, `CO3^2-__d_born`, and `MEACOO-__s` as the four strongest tracked directions. `H3O+__d_born` is near-zero on the current metrics, while several ion-size/Born/interaction directions are highly correlated.

The program defined here converts that audit into a reproducible evidence-acquisition lifecycle. It complements the existing Phase 3 issues rather than replacing them:

- Issue 12 owns admission of the public split-package reactive-regression contract.
- Issue 13 owns preregistration, execution, and guarded promotion of the coupled fit.
- Issue 14 owns candidate-bound independent validation and identifiability.
- This design owns the data inventory, acquisition priorities, canonical observation contracts, eligibility decisions, and pre-fit evidence readiness that those issues consume.

## Governing scientific question

Which additional observations most cheaply reduce decision-relevant uncertainty in the MEA--H2O--CO2 parameter set without allowing reactive CO2 pressure, inferred species balances, or historical parameter assumptions to compensate for missing neutral-solvent, dielectric, acid-base, or ionic evidence?

The governing regression principle is weighted residual minimization with explicit measurement roles and uncertainty:

\[
\min_{\theta}\;\sum_f\sum_{i\in f} w_{i,f}\,r_{i,f}(\theta)^2 + R(\theta),
\]

where each target family `f`, residual definition, weight, uncertainty basis, eligibility state, regularization term, and validation assignment is frozen before a production fit. A lower aggregate objective does not establish identifiability, physical validity, or predictive transferability.

## Goals

- Recover and QA all high-value observations already available locally before initiating broad external searches.
- Define one canonical observation contract that preserves source identity, locator, units, thermodynamic basis, uncertainty, phase, replicate relationships, and measurement role.
- Separate direct observations, reported zeros, aggregate observations, balance-inferred values, analog evidence, and model-derived values so they cannot be silently given equivalent regression status.
- Build a parameter-to-observable coverage matrix that drives literature acquisition by identifiability value rather than publication count.
- Establish a ranked external acquisition backlog with source leads, required metadata, admission criteria, and expected parameter value.
- Freeze grouped training, validation, and transferability reservations before the first production coupled fit.
- Keep downstream curation productive while the upstream ePC-SAFT reactive-regression target family remains unadmitted.
- Make every future manuscript claim traceable to a canonical observation, an immutable model result, and an explicit acceptance decision.

## Non-goals

- Do not execute or claim completion of the coupled parameter regression in this program-design route.
- Do not alter curated parameter values, reaction constants, figures, or manuscript claims merely because new rows are discovered.
- Do not treat viscosity or surface tension as direct equilibrium ePC-SAFT targets unless a separately approved transport or interfacial model defines that contract.
- Do not treat ethanolammonium salts with unrelated counterions as direct MEACOO- evidence.
- Do not convert Wong mol/kg values to mole fraction for regression until the source denominator and total-mole construction are verified.
- Do not infer missing uncertainty as zero, reported zero concentration as missing, or solver-filled species as independent measurements.
- Do not depend on private upstream APIs, a mutable shared ePC-SAFT checkout, or an unsupported target family.
- Do not place every resulting task under a generic submission-readiness wrapper. Work must be assigned to the milestone and technical area that owns its outcome.

## Alternatives considered

### Alternative A: Search-first literature campaign

Begin broad database and web searches immediately, then ingest useful-looking papers as they are found.

Advantages: quickly expands the bibliography and may discover recent measurements. Disadvantages: duplicates evidence already present locally, creates heterogeneous schemas, and encourages source-count growth without regard to parameter identifiability. This approach is rejected as the primary workflow.

### Alternative B: One monolithic coupled-regression dataset

Normalize every observation into one table and fit every movable parameter simultaneously.

Advantages: simple top-level objective and one apparent result. Disadvantages: obscures direct versus inferred evidence, allows high-count families to dominate, increases parameter confounding, and cannot represent upstream target-family admission accurately. This approach is rejected.

### Alternative C: Local-first, parameter-driven evidence ladder

First repair the observation contract and recover local evidence. Then acquire external data in the order implied by sensitivity and missing orthogonal observables. Admit each family independently for training, reserved validation, regularization, or diagnostic-only use.

Advantages: maximizes value from existing sources, preserves provenance, creates meaningful holdouts, and remains useful while upstream regression support is blocked. Disadvantages: requires more explicit lifecycle metadata and staged review. This is the selected design.

## Selected design

The program is one evidence system with five independently plan-able workstreams. They share schemas and manifests but have separate scientific owners and acceptance proof.

### Workstream 1: Observation contract and lineage repair

Create a common observation envelope for all experimental families. Family-specific values remain in typed columns or family tables; they are not forced into ambiguous generic numbers.

Required common fields:

- `record_id`, `source_key`, `source_file`, and primary-source locator.
- `data_family`, `observed_quantity`, `species` when applicable, and phase.
- Temperature, pressure, unloaded-solution MEA mass fraction, CO2 loading, and their explicit units/bases.
- Reported value, reported unit, reported basis, and any normalized value with a named conversion.
- Uncertainty value, uncertainty type, coverage status, and source locator.
- `measurement_role`: direct positive, direct zero, aggregate direct, balance inferred, model derived, analog, or ambiguous.
- `lifecycle_status`: raw, QA pending, canonical eligible, validation reserved, diagnostic only, or excluded.
- Replicate group, normalization group, exclusion reason, and reviewer decision.

Contract rules:

1. Missing, zero, below-detection, and not-reported states are distinct.
2. A normalized value never replaces the reported value or its basis.
3. Every row in a raw source must receive one lifecycle disposition; silent omission is invalid.
4. Canonical builders must preserve known uncertainty and auxiliary observables even when a current model cannot consume them.
5. Analysis YAML declarations, runtime loaders, and canonical artifact names must resolve to the same live files.
6. Derived analysis tables and plot snapshots cannot be registered as independent experimental evidence.

### Workstream 2: Local evidence recovery

Local recovery precedes external acquisition because it is cheaper, reproducible, and already source-controlled.

#### VLE recovery

- Review all 166 raw rows outside `Combined_VLE.csv`.
- Prioritize Aronu 15/45 wt% and Hilliard 17/40 wt% rows as composition-transfer evidence.
- Review Jou 0/25/150 °C and Xu 109--170 °C rows against source validity, phase, and current model domain before admission.
- Preserve Hilliard MEA, H2O, and total pressures; Jou total pressure and MEA Raoult-pressure field; and Xu total pressure.
- Treat normalized Xu temperatures and overlapping/replicate conditions as explicit groups rather than independent unlabeled points.

#### Speciation recovery

- Preserve the 29 Böttinger 20 wt% and eight Jakobsen 15 wt% states as initial transferability holdout candidates.
- Keep direct species, aggregate MEA+MEAH+, reported zeros, and reconciled balances in separate roles.
- Do not count the expanded 666 species-state reconciliation table as 666 independent measurements.
- Prefer direct CO2(aq), CO3^2-, individual MEA, and individual MEAH+ observations because the active 74-state table contains only six direct CO2 observations, 16 direct carbonate observations, and 35 individual MEA/MEAH+ observations each.

#### Loaded physical-property recovery

- Extract the 68 loaded-density observations from Amundsen Tables 2--4 with stated density, temperature, composition, and loading uncertainties.
- Extract the 75 loaded-viscosity observations from Tables 6--8 for transport validation and state-property context.
- Classify density as a potential equilibrium/property target or regularizer subject to upstream admission; classify viscosity as validation-only unless a transport model is separately specified.

#### Wong recovery

- Verify the Raman concentration denominator, pressure correspondence, calibration basis, and five ambiguous overlap-sensitive points.
- Until verified, retain reported mol/kg observations as source-basis values and exclude derived mole fractions from regression eligibility.
- Extract Wong Table 5 as a separate high-pressure loading dataset with method and equilibrium-status fields.
- Label repeated 1-bar low-loading batches as non-capacity transient/batch observations according to the paper caveat rather than ordinary equilibrium replicates.

### Workstream 3: Parameter-driven external acquisition

External searching begins only after the schema can retain the evidence found. Search packages must record query, database/source, date, inclusion criteria, access outcome, full-text/SI status, and extraction decision.

#### Priority 1: Neutral-solvent and physical-solubility separation

Targets:

- MEA--H2O binary VLE from Cai et al. 1996, Park and Lee 1997, and Kim et al. 2008.
- MEA--H2O excess enthalpy from Posey 1996 and Touhara et al. 1982.
- Physical CO2 solubility or N2O-analogy evidence from Jiru 2012 and Hartono 2014.
- Pure-MEA saturation pressure and liquid-density evidence used to establish the selected pure parameters and association scheme.

Expected value: constrain `k_ij__MEA__H2O`, `k_ij__CO2__MEA`, and neutral pure/association parameters before reactive pressure can move them.

#### Priority 2: Dielectric and Born separation

Targets:

- MEA--H2O relative static permittivity versus temperature and composition.
- Loaded-MEA permittivity versus temperature and carbonation ratio, beginning with Hajj 2024 and the Hsieh/Floriano/Nascimento leads already named locally.

Expected value: determine whether MEA `f_solv`, dielectric mixing, or ion Born parameters can be promoted. Pressure alone is not admissible evidence for MEA `f_solv`.

#### Priority 3: Acid-base and ionic evidence

Targets:

- Loaded-MEA pH or potentiometric data with explicit pH scale, calibration, temperature, pressure, composition, and loading.
- Direct MEAH+/carbamate osmotic coefficients, activities, or defensible salt-solution measurements.
- Analog ethanolammonium or ammonium-carbamate measurements only as separately labeled plausibility evidence.

Expected value: constrain H3O+/OH- behavior, ion size/dispersion/Born directions, and ion--ion interactions that are weak or correlated under current pressure/speciation metrics.

#### Priority 4: Independent speciation and energetics

Targets:

- Fan 2009 NMR full text/SI and Du Preez 2019 FTIR full text/SI.
- Additional individual MEA/MEAH+, molecular CO2, bicarbonate, and carbonate measurements across concentration and temperature.
- Differential heat-of-absorption data from Kim and Svendsen 2007 and Kim et al. 2014.
- Idris 40/50 wt% VLE rows and complete uncertainty metadata if the primary source confirms their availability.

Expected value: create source-independent validation groups and distinguish reaction energetics from parameter sets that fit equilibrium pressure similarly.

### Workstream 4: Regression target and split registry

Each observation family receives a target-admission record containing:

- owning residual definition and parameter families it can inform;
- direct, aggregate, zero-bound, inferred, regularization, or validation-only status;
- uncertainty-derived or policy-derived weight and the reason;
- supported upstream target kind and capability-report evidence;
- training group, validation group, transferability group, or diagnostic-only assignment;
- failure-accounting policy and physical acceptance checks.

The initial split policy is grouped rather than random:

- Keep at least one complete source/concentration family out of training where coverage permits.
- Reserve the 15/20 wt% NMR states initially for composition transferability unless a later coverage analysis proves a more informative leak-free grouping.
- Prevent adjacent rows from the same source curve or normalized temperature group from crossing training and validation.
- Freeze the split manifest and its hash before the production fit in Issue 13.
- Account for every reserved row, including model-domain and solver failures, in Issue 14.

### Workstream 5: ePC-SAFT integration boundary

Downstream data work must continue without pretending the upstream package already supports every desired target.

- Stable mode remains the default for normal curation and diagnostics.
- Dev mode may use one explicit ePC-SAFT worktree only for intentional contract co-development.
- Final manuscript results require released, tagged, pinned, or repo-owned immutable inputs and must pass `uv run python scripts/check_epcsaft_integration.py --mode final`.
- Reusable provider, equilibrium, and regression calls remain behind approved MEA runtime/adapter modules.
- Unsupported density, dielectric, calorimetric, pH, ionic-activity, or coupled reactive targets remain validation-ready data or explicit upstream requests; they must not fall back to private APIs or a downstream optimizer.
- The public coupled pressure/speciation target and structured result contract remains owned by upstream issue 468 and downstream Issue 12.

## Parameter-to-observable coverage map

| Parameter family | Primary evidence | Secondary evidence | Current hole |
| --- | --- | --- | --- |
| MEA `m`, `sigma`, `epsilon`, association | Pure saturation pressure, saturated liquid density, caloric data | Binary VLE and excess enthalpy | Raw pointwise pure-property basis is not curated |
| `k_ij(MEA,H2O)` | Binary MEA--H2O VLE and excess enthalpy | Unloaded/loaded density | Current value is inherited; underlying raw binary data are absent |
| `k_ij(CO2,MEA)` | Physical CO2 solubility/molecular CO2 plus concentration-resolved VLE | Total and component vapor pressures | Reactive 30 wt% pressure dominates current evidence |
| MEAH+/MEACOO- `sigma`, `epsilon` | Direct ionic activity/osmotic/density evidence | Individual speciation across concentration | No direct ionic-activity family; dispersion directions are weak |
| Ion `d_born`, MEA `f_solv`, dielectric parameters | Relative permittivity and transfer/activity evidence | pH and carbonate-sensitive speciation | No machine-readable dielectric table; several directions are correlated |
| Ion--ion and ion--neutral `k_ij` | Direct activity plus orthogonal speciation | VLE only after neutral terms are anchored | Pressure/speciation alone cannot isolate all pairs |
| Reaction constants | Temperature-resolved speciation, pH, calorimetry | VLE consistency | No pH family and little uncertainty on constant correlations |

## Interfaces and canonical artifacts

The implementation plan should preserve the existing flat Superpowers artifact model and place scientific data in current project-owned roots. Expected durable interfaces are:

- `data/reference/MEA/manifests/source_status_manifest.csv`: source acquisition and review state.
- `data/reference/MEA/manifests/extraction_target_manifest.csv`: concrete source-to-target extraction work.
- A versioned observation-schema document or table covering the common envelope and family extensions.
- Canonical family tables under `data/reference/MEA/` with deterministic builders.
- A row-disposition manifest accounting for every raw observation.
- A target-admission manifest mapping observations to residual roles and upstream capabilities.
- A frozen grouped-split manifest consumed by Issues 13 and 14.
- Source-search logs that contain queries and access decisions but no copyrighted full-text redistribution.

Milestone ownership should be outcome-based:

- Paper Validation: source acquisition, extraction, units/basis verification, uncertainty, and canonical datasets.
- Phase 3 Ionic Regression: target admission, parameter coverage, split freeze, package integration, and fit consumption.
- Manuscript Submission: claim updates only after immutable regression and validation proof exists.

Planning may create a coordinated issue set, but should avoid a single generic parent that obscures these technical owners.

## Data flow

Inventory source lead -> acquire or locate primary evidence -> quarantine raw extraction -> record source locator and basis -> normalize without overwriting reported values -> run row-level QA -> assign lifecycle status -> build canonical family table -> update parameter-coverage matrix -> assign training/validation/diagnostic role -> verify upstream target admission -> freeze hashes and split -> execute Issue 13 fit -> evaluate Issue 14 validation -> update manuscript claims.

No later stage may silently repair an earlier-stage omission. If basis, uncertainty, phase, source identity, or target support is missing, the observation remains QA pending or diagnostic-only.

## Error handling and stop conditions

Stop admission or fail validation on:

- unverified units, composition basis, species identity, phase, or source locator;
- a missing value interpreted as zero or an inferred value interpreted as direct;
- row loss between raw and canonical data without a disposition record;
- uncertainty discarded during canonicalization;
- duplicate source observations treated as independent without a replicate/normalization group;
- Wong mole-fraction conversion before denominator verification;
- analog salts promoted as direct carbamate evidence;
- training/validation leakage across source curves, replicate groups, or normalized conditions;
- runtime loading a different artifact than analysis metadata declares;
- unsupported upstream target kinds, private API use, or mutable package state in final results;
- a numerically converged fit that fails conservation, bounds, residual, plausibility, or validation gates.

## Testing and proof

The implementation plan must include proportionate deterministic checks:

- Row-accounting tests prove every raw observation is canonical, reserved, diagnostic-only, or excluded with a reason.
- Schema tests distinguish missing, zero, below-detection, aggregate, inferred, analog, and ambiguous roles.
- Unit/basis conversion tests use independently calculated fixtures and retain the reported source value.
- Uncertainty tests prove known Idris and Amundsen uncertainty survives canonicalization.
- Duplicate and replicate tests preserve grouping and prevent leakage.
- Wong tests fail conversion when the denominator contract is unresolved.
- Runtime/metadata tests ensure analysis YAML and loaders name live canonical artifacts.
- Split tests prove deterministic grouped assignment and no source-family leakage.
- Target-admission tests fail closed when the upstream capability report does not admit a requested family.
- Regression receipts distinguish solver termination, numerical acceptance, physical acceptance, and scientific promotion.
- Routine work passes `uv run python scripts/validate_project.py quick`; release/manuscript gates use the repository confidence validation and final ePC-SAFT integration check.

## Acceptance criteria

The data-acquisition and regression-readiness program is ready for Issue 13 consumption when:

1. Every local raw VLE and speciation row has a lifecycle disposition and stable provenance.
2. The local Amundsen loaded tables and Wong Table 5 are extracted or explicitly rejected with evidence.
3. Known uncertainty and auxiliary observables survive canonicalization.
4. The Wong basis conflict is resolved or all converted Wong targets remain ineligible.
5. The parameter-to-observable matrix names direct evidence, weak directions, and unsupported claims for every movable parameter.
6. External acquisitions have reproducible search/access logs and primary-source locators.
7. Training, reserved validation, transferability, and diagnostic-only groups are frozen and hashed before production fitting.
8. The target-admission registry matches current public ePC-SAFT capabilities and fails closed for unsupported families.
9. No derived plot/result table is counted as independent experimental evidence.
10. The manuscript continues to describe the current parameter set and zero-evaluation summary as provisional until Issues 12--14 provide immutable proof.

## Risks

- Additional observations may reveal model-form inadequacy rather than make all parameters identifiable. That result should narrow the fit window or manuscript claim instead of encouraging unconstrained parameter movement.
- Direct carbamate ionic-activity data may not exist. Analog evidence can support plausibility bounds but cannot prove MEACOO- parameters.
- Dielectric measurements may report frequency-dependent quantities that do not map directly to the static relative permittivity required by the model. Extraction must preserve measurement frequency and fitted static-limit methodology.
- Expanded high-temperature VLE may cross model, phase, apparatus, or degradation regimes. Local availability does not imply training eligibility.
- A high-count family can dominate the objective even with good provenance. Family balancing must be preregistered and reported separately from measurement-uncertainty weighting.
- Upstream target admission may lag data readiness. Curated observations remain useful as validation assets and upstream contract fixtures without being forced into unsupported regression paths.

## Unresolved decisions

- Exact grouped holdout membership will be selected after local row recovery and coverage analysis, then frozen before Issue 13 execution. The model-validation maintainer owns this decision.
- Exact external full-text acquisition routes depend on institutional/user access and will be resolved source by source without bypassing access controls. The data-curation maintainer owns this decision.
- Whether loaded density, dielectric, pH, ionic activity, and calorimetry become fitted target families or validation-only families depends on public upstream capability admission and identifiability evidence. The cross-repo integration maintainer owns this decision.
- The implementation plan will determine whether work is represented by a coordinated issue set or separate milestone-native issues; technical ownership must remain visible either way. The project workflow maintainer owns this decision.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Workflow mode | Native `project_workflow_mode` gate | Use bounded Auto Mode for one data-readiness outcome. | Allows routine safe routing while failing closed on scope or proof gaps. | No | project workflow maintainer |
| Program strategy | Repository data audit | Use a local-first, parameter-driven evidence ladder. | Recovers high-value existing evidence before external searching. | No | data-curation maintainer |
| Observation contract | Provenance and uncertainty audit | Preserve reported values, normalized values, roles, uncertainty, locators, and lifecycle status separately. | Prevents silent basis conversion, row loss, and false measurement equivalence. | No | data-provenance maintainer |
| Regression evidence | Sensitivity and target-role artifacts | Prioritize orthogonal neutral, dielectric, acid-base, and ionic observations over more 30 wt% pressure alone. | Directs acquisition toward identifiability rather than row count. | No | regression maintainer |
| Validation split | Existing Issue 14 design plus coverage audit | Use preregistered grouped source/concentration holdouts with leakage guards. | Preserves predictive and transferability meaning. | No | model-validation maintainer |
| Wong eligibility | Source manifest and canonical-builder conflict | Exclude converted Wong mole fractions until the mol/kg denominator is verified. | Prevents a source-basis assumption from contaminating fitted parameters. | No | spectroscopy-data maintainer |
| Viscosity role | ePC-SAFT equilibrium model boundary | Keep viscosity validation-only unless a separate transport model is approved. | Avoids treating transport behavior as a direct equilibrium target. | No | physical-properties maintainer |
| Upstream boundary | ePC-SAFT integration contract and Issue 12 | Curate data now, but fit only target families admitted by public immutable package contracts. | Keeps downstream progress independent without inventing package capability. | No | cross-repo integration maintainer |
| Holdout membership | Post-recovery coverage analysis | Freeze exact groups after local recovery and before production fitting. | Uses the recovered coverage without post-fit split selection. | Yes | model-validation maintainer |
| External source access | Primary-source acquisition policy | Resolve access per source and retain only lawful source locators and extracted facts. | Prevents inaccessible snippets or abstracts from becoming numeric evidence. | Yes | data-curation maintainer |
| Issue structure | User preference for technical categorization | Preserve milestone-native technical ownership instead of one generic readiness wrapper. | Keeps data, regression, validation, and manuscript work independently legible. | Yes | project workflow maintainer |
