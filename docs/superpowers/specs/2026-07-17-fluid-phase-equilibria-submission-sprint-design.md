# Fluid Phase Equilibria Submission Sprint Design

**Target:** Submit the completed MEA thermodynamics manuscript to *Fluid Phase Equilibria* on Friday, July 24, 2026.

**Decision date:** July 17, 2026

**Approved strategy:** Conditional full-paper submission with a Wednesday submit-or-hold gate.

## Outcome

Deliver a scientifically complete, internally consistent, reproducible journal article that reports the coupled pressure/speciation regression, independent validation, parameter sensitivity, and identifiability evidence promised by the full paper. The compiled manuscript must read only as the finished article. Development state, issue tracking, repository operations, migration history, and execution planning remain outside the submission-facing LaTeX tree.

The July 24 deadline is conditional. The article may be submitted only if every scientific and publication gate in this design passes. Missing evidence causes a submission hold; it does not authorize an unsupported claim, an invented result, or a weakened verification threshold.

## Governing scientific claim

The final article evaluates SSM+DS modified-Born ePC-SAFT for reactive \(\ce{CO2}\) solubility in aqueous monoethanolamine on a true-species basis and reports a completed joint pressure/speciation parameter regression. The claim requires all of the following:

- the frozen 147-training/220-validation observation split and source identities;
- a package-native joint pressure/speciation fit with accepted solver termination;
- exact admitted residual Jacobians for every fitted target family;
- complete parameter movement, active-bound, evaluation, row-status, and source/target diagnostics;
- explicit accounting for every training and validation observation, including failed predictions;
- held-out pressure and speciation results that were not used to select the fitted parameters;
- sensitivity, correlation, active-bound, robustness, and physical-plausibility evidence sufficient to state the identifiability boundary; and
- immutable source, data, parameter, environment, and result identities.

Solver convergence, numerical convergence, and physical acceptance remain separate. A lower objective or successful termination alone cannot promote parameters or support a manuscript claim.

## Manuscript boundary

Submission-facing files under `docs/latex` contain only professional journal prose and final evidence. They must not expose project-management state or describe the paper as a live development document.

- Methods may describe only the exact calculation that produced the accepted final results.
- Results may contain only values traceable to immutable generated tables.
- Figures and tables must be regenerated from accepted outputs rather than manually transcribed.
- Limitations must describe scientific scope and evidence boundaries, not software or project status.
- The conclusion must match the accepted regression and validation receipts.
- No sentence may imply that an unexecuted fit, validation campaign, uncertainty analysis, or identifiability result occurred.

Internal readiness records, tracker mirrors, specifications, plans, receipts, and validation reports remain outside the compiled source path.

## Fixed inputs and no-change boundaries

The sprint preserves the following unless a failed scientific check proves that one is invalid:

- the canonical pressure and speciation source tables;
- the frozen 147-training/220-validation split;
- target-role eligibility, including direct-positive targets, reported-zero upper bounds, and balance-inferred context rows;
- source and readiness hashes;
- zero-valued bounds and aggregate targets where already admitted;
- the current fail-closed execution gate until immutable upstream evidence explicitly admits execution; and
- the final-integration requirement for immutable ePC-SAFT sources.

The sprint does not bypass `upstream_execution_admitted=false`, fit against validation observations, suppress failed rows, relax scientific acceptance to obtain a result, or treat the preserved personal lab as a production dependency.

## Dated scientific gates

### Gate 1: Preregistration freeze — Saturday, July 18

Freeze the objective, fitted parameters, bounds, scaling, weights, regularization, target eligibility, training/validation identities, source hashes, solver acceptance, physical acceptance, failed-row accounting, parameter-promotion rules, and manuscript metrics before executing the full fit.

**Pass evidence:** a hash-bound preregistration record that reproduces the frozen readiness identities and admits no validation leakage.

### Gate 2: Upstream execution admission — Sunday, July 19 at noon MDT

Execution requires an immutable clean-package capability receipt proving:

- a native Ceres optimization loop;
- exact residual Jacobians for all admitted pressure and speciation targets;
- the reduced public fixture;
- public request, result, status, and capability-report contracts;
- termination, iteration/evaluation, cost, parameter movement, active-bound, row, and source/target diagnostics; and
- installed-artifact execution without a mutable sibling source dependency.

**Failure disposition:** hold the July 24 submission. Do not switch to an unadmitted implementation or claim that regression occurred.

### Gate 3: Coupled regression completion — Monday, July 20

Execute the preregistered training fit. Reject zero-evaluation, nonfinite, nonconverged, incomplete, physically implausible, or diagnostically incomplete candidates. Promote the fitted parameter set only if every preregistered training and physical gate passes.

**Pass evidence:** immutable fit result and promotion receipts containing the exact input, environment, package, parameter, row, source, and diagnostic identities.

### Gate 4: Independent validation and identifiability — Tuesday, July 21 at noon MDT

Evaluate all frozen validation observations without refitting. Account for rejected predictions in validation metrics and report them separately. Complete sensitivity, active-bound, correlation, robustness, and physical-plausibility analysis. State the parameter families that are identified, weakly identified, or unsupported by the available evidence.

**Pass evidence:** immutable validation and identifiability receipts plus generated manuscript tables and figure data.

### Gate 5: Scientific freeze — Wednesday, July 22

Integrate the accepted methods, results, discussion, limitations, and conclusion. Reconcile every numerical statement to a final table or figure. Verify equations, units, species bases, balances, residual definitions, citations, and source locators. Freeze scientific inputs and outputs after the complete proof suite and all-page review pass.

**Failure disposition:** correct an evidence-backed blocker and rerun the affected gate. If the scientific freeze cannot pass Wednesday, hold submission.

### Gate 6: Publication freeze — Thursday, July 23

Complete author review, venue compliance, metadata, declarations, data deposit, license, citation metadata, immutable tag/release, source package, highlights, and final availability text. Verify all identifiers and links from the frozen package.

**Pass evidence:** publication checklist, archive identifiers, package manifest, deterministic PDF identity, and explicit author approval.

### Gate 7: Submission — Friday, July 24 in the morning

Run the short final smoke gate, obtain an explicit submit decision, upload the frozen package, inspect the portal-generated proof, and retain the submission confirmation and manuscript identifier. No new scientific result or broad editorial revision begins on submission day.

## Fluid Phase Equilibria package contract

The final package follows the current official journal guide:

- editable LaTeX sources and all required figure/table assets;
- a concise abstract of no more than 250 words;
- one through seven English keywords;
- a separate editable highlights file containing three through five bullets, each no more than 85 characters including spaces;
- complete title-page author, affiliation, postal, corresponding-author, and contact information;
- funding and acknowledgment statements;
- a journal-compliant generative-AI disclosure that identifies the tool or service and its use;
- a separate competing-interest declaration document;
- a CRediT author statement;
- a research-data availability statement and linked repository deposit, or an explicit reason data cannot be shared;
- separately supplied publication-quality figure files and complete captions; and
- internally consistent references with persistent identifiers where available.

The article reports no new experimental measurements, so the journal's experimental-data validation report is not applicable. A graphical abstract is optional and is omitted from the critical path unless the scientific package freezes early. Generative AI must not be used to create or alter manuscript figures or graphical-abstract artwork.

## Author-controlled decisions

The publication freeze cannot pass until the author records and approves:

- final author name and sole- or coauthorship status;
- department, institution, city, region/postal code, and country;
- corresponding-author email, postal address, and portal contact details;
- ORCID inclusion or omission;
- funding statement and sponsor role, or the journal's no-specific-funding statement;
- acknowledgments or an explicit decision that none are required;
- competing-interest and CRediT statements;
- the exact AI disclosure;
- licenses for original software, data, and documentation, with third-party source data excluded from relicensing where necessary;
- archive provider and release/tag naming; and
- any suggested or opposed reviewers requested by the submission portal.

These values are not inferred from repository history.

## Repository and tracker disposition

The execution plan must reconcile the live tracker with this full-paper sprint:

- Issue #12 owns upstream contract adoption and cannot close before Gate 2.
- Issue #13 owns preregistration, coupled regression, and conditional parameter promotion.
- Issue #14 owns held-out validation and identifiability.
- Issue #16 owns the final executed computational-method inventory and reproducibility proof.
- Issue #17 owns author metadata, licensing, release, archive, and portal records.
- Issue #18 owns final figures, tables, layout, and editorial proof after Gate 4.
- Issue #15 aggregates #16 through #18.
- Issue #10 remains the final independent submit-or-hold gate.

Any milestone-date, issue-body, relationship, assignment, or status change is an external write and requires explicit approval at execution time.

## Submission-facing work packages

### Scientific methods and equations

- Reconcile the material-balance convention with the implemented balance matrix.
- Record the exact solver, initialization, continuation, scaling, tolerances, stopping and rejection criteria, package identities, and runtime protocol.
- Replace prospective objective language with the exact executed regression definition.
- Report quantitative charge, carbon, amine, water, reaction, and phase-equilibrium closure evidence.

### Results, figures, and tables

- Generate training and held-out metrics with complete failure accounting.
- Separate state counts from target-observation counts.
- Add source-stratified pressure/speciation evidence and the final parameter-change table.
- Add sensitivity, active-bound, correlation, and identifiability evidence.
- Regenerate readable vector figures with publisher-safe embedded fonts.
- Remove scientific exclusions phrased as project status and state stable evidence-based inclusion criteria instead.

### Narrative and front matter

- Align title, abstract, introduction, methods, results, limitations, and conclusion with the completed regression claim.
- Remove nonessential application framing that does not support the thermodynamic contribution.
- Complete affiliation, author identifiers, funding, acknowledgments, declarations, and PDF metadata.
- Keep the abstract citation-free, self-contained, and below the journal limit.

### Reproducibility and publication package

- Build from the authoritative `docs/latex` source tree.
- Reconcile bibliography ownership and source-log descriptions.
- Package all editable sources and separate figure files.
- Create license and citation metadata approved by the author.
- Deposit the frozen research data and code release, then cite its persistent identifier.
- Produce required highlights and a submission checklist/package manifest.

The existing dirty Overleaf mirror is not on the critical path. It may be reconciled only after its independent changes are reviewed and only if doing so cannot endanger the scientific or publication freeze. Submission may proceed from the verified repository source package.

## Verification contract

The complete gate includes:

```bash
uv sync --locked --group test
uv run ruff check src scripts analyses tests
uv run pytest -q
uv run python scripts/validate_project.py confidence
uv run python scripts/check_epcsaft_integration.py --mode final
bash scripts/build_manuscript.sh
uv run python scripts/check_manuscript_freshness.py
```

Additional proof must cover:

- readiness/source/split hash stability;
- accepted regression and validation receipts;
- no training/validation leakage;
- complete failed-row accounting;
- balance and residual acceptance;
- citation/reference integrity;
- venue-language, placeholder, and internal-status scans;
- deterministic figure and PDF regeneration;
- PDF metadata and embedded-font inspection;
- all-page visual review;
- clean-checkout source-package reproduction;
- archive-link and identifier resolution;
- cleanup audit and clean Git state; and
- the explicit author submit-or-hold decision.

## Success criteria

The sprint succeeds only when:

1. every scientific gate passes on immutable evidence;
2. the manuscript contains no unsupported or prospective result claim;
3. all venue and author-controlled package requirements are complete;
4. the data/code archive and manuscript cite stable identifiers;
5. the final source package and PDF reproduce from a clean checkout;
6. the portal-generated proof matches the frozen manuscript; and
7. the author explicitly approves submission.
