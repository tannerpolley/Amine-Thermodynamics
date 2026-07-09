# Full Project and Manuscript Audit Findings

**Date:** 2026-07-09
**Repository:** `MEA-Thermodynamics`
**Scope:** repository architecture, scientific model ownership, data provenance, generated artifacts, validation, reproducibility, plotting, and the submission manuscript
**Audit mode:** evidence-first; this document records findings and repair oracles but does not silently revise scientific outputs

## Executive assessment

The repository has a credible scientific core and a substantially developed manuscript, but it is not submission-ready. The strongest part is the Phase 2 activity-based evaluation: it uses source-verified reaction constants, the pinned upstream `epcsaft` package passes its final integration check, and all 644 retained Phase 2 speciation states report convergence. The main pressure and speciation residuals quoted in the abstract are traceable to those Phase 2 artifacts.

The blocking problem is that the repository currently tells two incompatible scientific stories. Phase 2 and the manuscript table use one source-verified reaction-constant basis, while the active Phase 3 package code uses materially different hard-coded constants. Phase 3 also promotes and plots an eight-row local SciPy fit that the current code explicitly calls a historical snapshot and refuses to rerun. Tests then certify the stale files as a “promoted” fit. Those contradictions undermine the manuscript's direct ion-parameter, sensitivity, and validation claims even though they do not invalidate the retained Phase 2 pressure result by themselves.

Recommended disposition: retain Phase 2 as the current defensible result, quarantine Phase 3 fitted/validation claims, establish one canonical reaction catalog and one artifact-ownership model, then regenerate or explicitly remove every manuscript claim that depends on historical Phase 3 outputs. Submission packaging, source provenance, and automated scientific claim gates should follow that repair.

## Evidence classification

- **Verified:** directly observed in tracked source/artifacts or reproduced with a command during this audit.
- **Inference:** consequence supported by verified evidence but requiring regeneration to quantify its numerical size.
- **Unknown:** a question that cannot be resolved from the retained repository evidence and must not be presented as fact.

## Companion skills used

- `chemical-engineer` for reaction-equilibrium, solver-contract, provenance, and claim-status discipline.
- `article-writer-latex-submission` for manuscript evidence, reproducibility, submission language, and LaTeX review.
- `improve-codebase-architecture` and `thermo-nuclear-code-quality-review` for ownership, seam, giant-module, duplication, and dead-code analysis.
- `matplotlib-plotting` and `pdf` for plot-artifact and rendered-manuscript inspection.
- `zotero` for local-library source lookup; Zotero Desktop was unavailable, so the missing Idris source was verified from the primary DOI/repository record instead.

## Healthy checks worth preserving

- **Verified:** `uv run python scripts/validate_project.py quick` passed 68 unit tests, the doctor, local-path guard, and compilation in 2.225 s.
- **Verified:** `uv run python scripts/check_epcsaft_integration.py --mode final` passed against pinned `epcsaft` commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` and version 1.5.2.
- **Verified:** the Phase 2 solver diagnostics contain 644/644 `solver_success=True`, 644/644 `message=converged`, maximum absolute charge residual $4.46\times10^{-10}$, and no state failures in the retained pressure/speciation campaign.
- **Verified:** the manuscript builds to a 19-page PDF with no undefined citations or cross-references; the build produced only two underfull-box warnings.
- **Verified:** all citation keys used by the manuscript exist, and the submission-safety text scan found no internal AI/tooling language in manuscript `.tex` files.
- **Verified:** the repository already has useful central seams for upstream integration (`epcsaft_runtime.py`, diagnostics modules), source/processed/result analysis folders, plot sidecars, and explicit claim-boundary artifacts.
- **Verified:** the manuscript's main reported Phase 2 metrics match the retained tables to the shown precision: pressure median absolute log residual 0.493; direct-positive speciation residuals 0.074 (MEA), 0.033 (MEAH+), 0.040 (MEACOO-), and 0.461 (HCO3-).

## Ranked findings

### P0 — Phase 3 solves a different reaction-constant model than Phase 2 and the manuscript

**Evidence (verified)**

- `src/MEA/epcsaft_ionic/model.py:29-35` hard-codes Phase 3 constants, including R2 (A=231.465), R3 (B=-12431.0, C=-35.4891), and R4 (A=-1.8652, B=-1543.3).
- `data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv:2-6` verifies the activity-basis constants against the retained Nasrifar/Austgen source: R2 (A=231.456), R3 (B=-12431.7, C=-35.4819), and R4 (A=2.8898, B=-3635.09).
- `docs/latex/tables/reaction_equilibrium_constants.tex:13-17` publishes the Phase 2 source-verified set.
- `src/MEA/epcsaft_ionic/model.py:417-418,438-478,540-559` routes Phase 3 speciation and reactive bubble calculations through the hard-coded set.
- `tests/test_phase2_activity_scaffold.py:36-51` validates the manifest but never asserts that the production Phase 3 reaction definitions equal it.

**Impact**

The active Phase 3 fitting, sensitivity, global-regression, and split-evaluation workflows invoke a different chemical-equilibrium basis from the one disclosed in the manuscript. The R4 difference is not a rounding error; it represents a materially different temperature correlation. Because retained Phase 3 artifacts store no reaction-catalog hash, they cannot prove otherwise and cannot be combined safely with Phase 2 residuals as one model campaign.

**Repair**

Create one typed reaction-catalog module loaded from one canonical, source-provenanced manifest. Give the ideal baseline and activity model explicit named bases where their literature conventions genuinely differ. Delete duplicated hard-coded coefficient sets. Make every analysis record the catalog ID and content hash in its summary.

**Proof oracle**

1. A test compares every runtime `ReactionDefinition` coefficient and stoichiometric row with the canonical manifest.
2. Every Phase 2/3 summary contains the same activity-catalog ID/hash where the same chemistry is claimed.
3. All affected Phase 3 data, plots, parameter tables, and manuscript statements are regenerated from the unified catalog.

**Classification:** verified mismatch; numerical effect on regenerated Phase 3 metrics is an inference until rerun.

### P0 — The manuscript presents a disabled historical eight-row fit as current “This work” evidence

**Evidence (verified)**

- `src/MEA/epcsaft_ionic/ion_parameter_regression.py:215-220` always raises and states that the local SciPy fit is disabled and that existing artifacts are historical evidence snapshots only.
- The retained summary at `analyses/phase3/ionic_epcsaft_regression/results/ion_parameter_regression/ion_parameter_fit_summary.json:2-27` reports a SciPy `xtol` fit using only 8 rows and 22 residuals.
- The improvement is small: residual norm 0.27144 to 0.26766 and median absolute log residual 0.10105 to 0.09885 (`:26-27,64-66,115-117`). The final summary also records `failure_count: 2` but an empty failures list (`:155-156`).
- `data/reference/MEA/manifests/parameter_provenance_manifest.csv:6-7` still labels the selected-row artifact as promoted while acknowledging that a full-row fit is required before a final claim.
- `docs/latex/sections/data_methods.tex:49-50`, `docs/latex/sections/mea_system_modeling_results.tex:44-56`, and `docs/latex/tables/full_ionic_ssm_ds_parameters.tex:16-17` describe the retained values as a direct regression and “This work.”
- `tests/test_ion_parameter_regression_artifacts.py:49-92` certifies the historical files as a promoted fit, while `tests/test_epcsaft_ionic_artifact_promotion.py:145-148` simultaneously asserts that the producing route is disabled.

**Impact**

The strongest parameter claim in the paper is not reproducible through the active production path and is based on a tiny mechanically subsampled fit. Readers cannot reproduce the claimed fit, and the parameter provenance contradicts the code's own declared status.

**Repair**

Choose one scientifically honest route:

1. complete the upstream-native full Tier-A fit, record selection/weighting and solver receipts, and regenerate all dependent artifacts; or
2. remove “fitted/This work” claims and the direct-fit figure, label the values historical exploratory seeds, and keep the paper as a fixed-parameter Phase 2 evaluation.

Do not retain the current mixed state.

**Proof oracle**

- A clean checkout can run the documented fit command and reproduce the parameter values within declared tolerances, or the manuscript contains no current-fit claim.
- Fit receipts include all target rows, weights, convergence status, failure rows, parameter covariance/profile information, and reaction-catalog hash.
- Tests reject historical artifacts as promotable production evidence.

### P1 — Best-effort nonconvergence is encoded as success in Phase 3 artifacts

**Evidence (verified)**

- `src/MEA/epcsaft_ionic/model.py:185-209,460-491` sets `return_best_effort=True` and copies `result.success` and `result.message` without imposing a message/residual acceptance gate.
- `analyses/phase3/ionic_epcsaft_regression/data/processed/ionic_speciation_activity_residuals.csv` has 74 rows marked `success=True`, but 10 have `message=chemical equilibrium did not converge`.
- The same contradiction propagates to 40 of 296 global-regression speciation residual rows and 40 of 296 so-called train-validation residual rows.
- The Phase 2 artifacts do not show this defect: their retained 644 states all report `message=converged`.

**Impact**

Phase 3 row counts, residual aggregates, plots, and validation summaries overstate solver coverage. A boolean success flag is being treated as scientific acceptance even when the solver message says the state did not converge.

**Repair**

Define one acceptance predicate requiring solver success, an accepted convergence status, finite outputs, and explicit mass/charge/reaction residual thresholds. Store `solver_returned`, `accepted`, and `rejection_reason` separately. Exclude rejected rows from model-performance metrics while reporting their count and conditions.

**Proof oracle**

- No row can have `accepted=True` with a nonconverged message or residual above tolerance.
- Summary counts reconcile exactly with accepted/rejected CSV rows.
- Regression objectives fail loudly or apply an explicitly documented penalty to rejected rows.

### P1 — Ten of the 161 VLE rows are omitted from the manuscript's source inventory

**Evidence (verified)**

- `data/reference/MEA/VLE/Combined_VLE.csv:43-52` contains 10 records labeled `Idris`.
- `docs/latex/sections/data_methods.tex:4,17` says the 161 records come from five sources and cites Aronu, Hilliard, Jou, Ma'mun, and Xu only.
- No Idris entry exists in `docs/latex/references.bib`, no Idris source CSV exists in `data/reference/MEA/VLE/`, and no builder/schema records how `Combined_VLE.csv` was assembled.
- Independent source verification identifies these points as Z. Idris, K. J. Jens, and D. A. Eimer, “Speciation of MEA–CO2 adducts at equilibrium using Raman spectroscopy,” *Energy Procedia* 63 (2014) 1424–1431, DOI `10.1016/j.egypro.2014.11.152`. The source reports new 30/40/50 wt% MEA VLE data at 40 °C, and its table includes the retained 0.460 loading / 0.813 kPa point.

**Impact**

The published evidence count and citation set are factually incomplete. The unreferenced rows affect the aggregate pressure metric, and their transformation/rounding cannot be audited from the repository.

**Repair**

Add the primary Idris source, source-specific CSV with uncertainty columns, bibliography entry, and row-level provenance; then generate the combined table from declared inclusion rules. Alternatively exclude the 10 rows and regenerate all metrics. Add a VLE schema with units and a uniqueness/range/source-count test.

**Proof oracle**

- Every combined row has `source_key`, source row/table locator, units, inclusion status, and transformation record.
- Combined source counts equal the manuscript inventory and bibliography.
- Rebuilding from source tables is deterministic and changes no rows unexpectedly.

### P1 — Scientific artifacts have multiple owners and already drift from one another

**Evidence (verified)**

- The audit found 31 exact-duplicate hash groups containing 64 tracked CSV/JSON/SVG files.
- Phase 2 copies full calculation outputs among `data/processed/`, `results/`, and `figures/*/output`.
- Same-named copies have diverged: `phase2_speciation_activity_curves.csv` has one hash in `data/processed/` and another shared by `results/` and the figure folder; `phase2_pressure_results.csv` and `phase2_pressure_metrics.csv` differ between the calculation result and figure output.
- Phase 1 has the same problem for `phase1_speciation_curve.csv`, `phase1_pressure_metrics.csv`, `phase1_speciation_metrics.csv`, and other tables.
- `analyses/phase1/smith_missen_baseline/analysis.yaml` explicitly calls these “compatibility CSV snapshots,” while repository policy forbids compatibility layers that preserve an old path without a current owner.

**Impact**

There is no reliable answer to “which table produced this manuscript figure?” A render-only command can preserve a stale plot snapshot while a calculation table changes elsewhere. Reviews and tests can pass against different copies of nominally the same evidence.

**Repair**

Adopt one canonical calculation-table owner per analysis. A figure bundle may retain only the exact plotted subset/snapshot with explicit upstream path and content hash; it must not mirror whole result families. Remove redundant result copies and compatibility wording. Make analysis manifests declare canonical inputs, calculation outputs, plotted snapshots, and manuscript exports separately.

**Proof oracle**

- A repository check rejects same logical artifact IDs at multiple canonical paths.
- Every plot sidecar records the SHA-256 of its plotted CSV and upstream calculation table.
- Regenerating data and then figures leaves `git diff --exit-code` clean.

### P1 — Validation proves file presence more strongly than scientific truth

**Evidence (verified)**

- `scripts/validate_project.py:11-16` quick mode runs doctor, local-path scan, compilation, and unit tests but does not lint, rebuild scientific tables, build the manuscript, or verify claim-to-artifact freshness.
- Confidence mode (`:18-20,178-210`) rerenders figures and verifies only that curated files exist. It does not regenerate expensive Phase 3 data and does not compare hashes, summary logic, or manuscript values.
- `tests/test_ion_parameter_regression_artifacts.py:49-92` promotes stale historical artifacts based on their stored content and existence.
- A fresh `ruff check src scripts analyses tests` found 51 violations, including 15 unused imports and three unresolved `Path` names in the six-species plotting modules.
- No CI workflow runs these checks in a clean environment.

**Impact**

Green validation can coexist with incompatible reaction constants, nonconverged accepted rows, stale absolute paths, and an unreproducible manuscript fit. The current suite provides structural confidence but not end-to-end scientific assurance.

**Repair**

Build tiered gates:

- quick: formatting/lint, imports, unit/contract tests, path/schema checks;
- scientific: canonical data regeneration, solver acceptance, artifact hashes, reaction-catalog equality, claim-table consistency;
- manuscript: deterministic figure export, LaTeX build to `docs/latex/builds`, citation/reference checks, PDF freshness, submission-safety scan;
- final: pinned upstream integration and clean-checkout reproducibility receipt.

**Proof oracle**

A clean CI run executes all non-expensive gates on every change; a documented final command runs the complete scientific/manuscript gate and produces a machine-readable receipt tied to the Git commit.

### P1 — “Train-validation” is a post hoc source split, not validation of a trained global model

**Evidence (verified)**

- `analyses/phase3/ionic_epcsaft_regression/results/global_regression/global_regression_summary.json:2-34` says `package_fit_not_completed`, `attempted_optimization=false`, `nfev=0`, and that the coupled fit was skipped.
- Initial and fitted values are identical (`:35-57`), and the selected set is the historical promoted ionic fit (`:88`).
- `docs/latex/sections/mea_system_modeling_results.tex:129-130` describes held-out sources as validation, and `docs/latex/tables/literature_model_comparison.tex:16` claims a train-validation split.

**Impact**

The held-out rows were not held out from a completed training procedure. Calling the result validation implies independence that the workflow did not create.

**Repair**

Rename the current artifact “source-grouped residual stratification” and present it only as a robustness diagnostic, or perform a real source-held-out fit in which validation rows cannot affect parameter selection, preprocessing decisions, or model choice.

**Proof oracle**

The training receipt lists only training source IDs; a separate evaluation command loads frozen parameters and scores untouched validation rows; the manuscript terminology matches the executed protocol.

### P1 — The local-path guard misses escaped Windows paths in tracked JSON

**Evidence (verified)**

- `scripts/check_no_local_paths.py:17-22` matches literal `C:\Users\` text but not JSON-escaped `C:\\Users\\` sequences.
- Tracked Phase 3 JSON files contain stale absolute paths, including `results/summary/ionic_evaluation_summary.json:2-6`, `results/parameter_regression/ionic_parameter_regression_summary.json:2,148-150`, and `results/ion_parameter_regression/ion_parameter_fit_summary.json:159-168`.
- Some stored paths point to obsolete pre-category analysis layouts or a disposable Codex worktree.
- The generating code serializes absolute `Path` values in `src/MEA/epcsaft_ionic/plot_results.py:296-301` and `src/MEA/epcsaft_ionic/regress_parameters.py:155-169`.

**Impact**

Artifacts are nonportable, stale paths pass the advertised guard, and summaries cannot be consumed reliably outside the machine that produced them.

**Repair**

Serialize repository-relative POSIX paths through one shared artifact-path helper. Scan parsed JSON values in addition to raw text, including escaped forms. Regenerate affected artifacts rather than manually rewriting them.

**Proof oracle**

No tracked text or parsed JSON string contains a home/worktree path; every declared artifact path resolves from the repository root in a clean checkout.

### P1 — The manuscript lacks enough computational detail and packaging for reproduction/submission

**Evidence (verified)**

- `docs/latex/sections/data_methods.tex:82-85` describes the model at a high level but omits the exact package version/commit, solver algorithm, initialization/continuation, acceptance criteria, row rejection policy, hardware/runtime, and regeneration commands.
- The coupled objective in `:54-80` is presented as a method even though `:83` states the coupled regression was not completed.
- `README.md:55-60` builds LaTeX directly in the source directory. The repository has no canonical `docs/latex/scripts/build_main.sh` or PDF freshness checker and does not enforce `docs/latex/builds/`.
- There is no `LICENSE`, `CITATION.cff`, `CONTRIBUTING.md`, release/archival DOI, or CI workflow. `docs/latex/sections/data_code_availability.tex:2` acknowledges the missing archive and license.

**Impact**

An external reviewer cannot reproduce the calculation-to-PDF chain or know which revision supports the claims. The manuscript is not ready for archival submission even if its scientific inconsistencies are repaired.

**Repair**

Add a concise computational reproducibility subsection and a single final-build script that regenerates approved data/figures, validates claim tables, builds to `docs/latex/builds`, and checks PDF freshness. Add licensing, citation metadata, contribution guidance, a tagged archive/DOI, and CI.

**Proof oracle**

A clean checkout at the cited tag can execute one documented command to produce the final PDF and a receipt containing code commit, dependency lock hash, upstream ePC-SAFT commit, reaction/parameter catalog hashes, accepted-row counts, and figure/table hashes.

### P2 — The architecture duplicates scientific policy and concentrates too much orchestration in giant modules

**Evidence (verified)**

- Reaction constants exist independently in manifests, the Phase 2 generator, the ideal model, the Phase 3 model, and the LaTeX table.
- `analyses/phase2/activity_epcsaft/scripts/generate_data.py` is 1,102 lines with 165 branch points.
- `src/MEA/epcsaft_ionic/global_regression.py` is 831 lines/102 branches, and `src/MEA/epcsaft_ionic/model.py` is 745 lines/93 branches.
- `model.py` owns parameter defaults, dataset copying, reaction policy, target construction, solver adapters, and artifact writing in one module.

**Impact**

The most important scientific policy has low locality: one change must be repeated across multiple modules and artifacts, which caused the P0 split. Large orchestration files make it difficult to test scientific seams independently.

**Repair**

Deepen a small number of meaningful modules rather than creating wrappers:

- reaction catalog and basis/provenance;
- parameter-set catalog and promotion status;
- target/dataset construction;
- solver adapter and acceptance contract;
- metrics/claim gates;
- artifact writer with relative paths/hashes.

Keep analysis scripts as thin orchestration over these modules. Split `generate_data.py` by problem construction, execution, metrics, and report generation only where each module owns a coherent invariant.

**Proof oracle**

Scientific policies have one owner, analysis scripts contain no duplicated coefficient/parameter literals, and module-level tests can exercise each seam without writing a full artifact tree.

### P2 — Analysis manifests and workspace conventions are inconsistent

**Evidence (verified)**

- Seven analysis roots use materially different `analysis.yaml` schemas. Early analyses provide only `layout/commands/results_policy`; Phase 2 adds typed inputs/outputs, runtime, tracked results, and references; Phase 3 reverts to the minimal schema.
- `analyses/phase1/smith_missen_baseline/` has no README and uses a compatibility-results policy.
- The project instructions prefer shared `.run/*.run.xml` durable commands, but none are tracked and `.gitignore` ignores `*.run.xml`.
- The README lists active and historical analysis paths but does not provide a campaign/status matrix or explain which analyses support manuscript claims.

**Impact**

Automation cannot reliably discover ownership, inputs, outputs, cost, or claim status. New contributors cannot distinguish canonical publication evidence from retained diagnostics.

**Repair**

Define and validate one analysis-manifest schema with status, scientific question, inputs, outputs, commands, runtime class, upstream catalog hashes, manuscript consumers, and artifact policy. Add a root analysis index and per-analysis README. Track only durable run configurations that add value.

**Proof oracle**

A schema validator passes every analysis; the root index identifies each analysis as canonical, supporting, diagnostic, historical, or superseded and links it to manuscript claims.

### P2 — Dependency and code-quality hygiene are not controlled

**Evidence (verified)**

- `pyproject.toml:7-18` includes `numdifftools`, `pillow`, `plotly`, `streamlit`, and `sympy`, but no imports were found in tracked production/analysis/test Python. The optional IDAES/Pyomo group is also undocumented in active workflows.
- There is no Ruff configuration, type-checking configuration, pre-commit hook, or CI lint gate.
- Fresh Ruff output reports 51 issues, including dead imports and unresolved names.

**Impact**

The environment is larger and slower than necessary, dead code accumulates, and simple defects remain invisible to the passing quick validation.

**Repair**

Prove or remove each unused dependency; move genuinely optional UI/notebook tooling to named extras. Add a minimal Ruff configuration and resolve all findings, deleting imports and disabled-code remnants rather than suppressing them broadly. Introduce type checking incrementally at public scientific interfaces.

**Proof oracle**

`uv sync --locked`, Ruff, and the selected type checker pass from a clean checkout; every direct dependency has a tracked import or documented command owner.

### P2 — Manuscript tables and narrative blur executed, proposed, and historical work

**Evidence (verified)**

- `docs/latex/sections/data_methods.tex:64-80` gives a coupled objective that was not executed.
- `docs/latex/tables/regression_bounds.tex:8-15` labels fitted retained values as “Initial value” and omits the claimed fitted MEAH+/MEACOO- binary interaction.
- `docs/latex/sections/mea_system_modeling_results.tex:113-130` combines historical Phase 3 sensitivity/split results with the Phase 2 fixed-parameter campaign without a campaign identifier.
- The data-methods statement that speciation records were “reconciled” (`:4`) does not quantify the reconciliation method, uncertainty propagation, or whether reported values were changed.

**Impact**

Readers cannot tell which operations were performed for this paper, which were proposed, and which are historical diagnostics. Parameter and validation claims appear stronger than their actual execution status.

**Repair**

Use explicit labels: executed fixed-parameter evaluation, historical exploratory fit, proposed coupled objective, and future work. Generate parameter tables directly from the approved parameter artifact and include seed/final/status/source columns. Describe reconciliation as a reproducible transformation with uncertainty and row-role rules.

**Proof oracle**

Every numerical table cell is generated from one approved artifact; every method verb corresponds to an executed receipt; proposed work appears only as proposed/future work.

### P2 — Figure legibility and manuscript page composition need a publication pass

**Evidence (verified)**

- Visual review of the 19-page PDF found very small labels/legends in the paired direct-ion regression figure and the four-panel speciation figure.
- Page 12 contains roughly half a page of avoidable whitespace around the direct-fit figure.
- The nomenclature is forced onto a mostly empty final page by `docs/latex/main.tex:101-106`.
- The title page has no affiliation/ORCID, uses `\shortauthors{Polley et al.}` for a single author (`main.tex:76-82`), and the PDF author metadata contains a stray glyph.

**Impact**

The science is harder to read at journal scale, and the front matter/layout look unfinished.

**Repair**

Regenerate figures for final column width with minimum 7–8 pt embedded text, simplify legends, and separate panels when necessary. Rebalance float placement and nomenclature. Complete affiliation, ORCID, funding/acknowledgment fields as applicable, correct the running author, and sanitize PDF metadata.

**Proof oracle**

Rendered-page review at 100% confirms legible axes/legends, no accidental half-empty pages, correct author metadata, and no clipping or unresolved layout warnings.

### P3 — Plot discovery and naming have minor gaps

**Evidence (verified)**

- `.mplgallery/manifest.yaml` has 30 valid records and no missing targets.
- `analyses/phase3/ionic_epcsaft_regression/results/ion_parameter_regression/ion_parameter_pressure_parity.svg` has a sidecar but is absent from the manifest.
- The manifest indexes duplicate result/figure copies of the same Phase 1/2 SVGs.

**Impact**

Plot discovery is incomplete and amplifies the duplicate-artifact ownership problem.

**Repair**

Regenerate the manifest after artifact consolidation and validate one record per canonical plot ID.

**Proof oracle**

Every tracked `.mpl.yaml` SVG is registered exactly once and every manifest fingerprint matches the file.

### P3 — Small terminology and repository-finish issues remain

**Evidence (verified)**

- Nomenclature defines loading as `L`, while the manuscript uses `\alpha`.
- `README.md:37` points readers to a legacy branch instead of clearly classifying the current retained baseline in the analysis index.
- The bibliography contains a large amount of imported abstract metadata unrelated to citation rendering, increasing noise and scan false positives.

**Impact**

These do not change results but reduce polish and maintenance clarity.

**Repair**

Normalize notation, move historical-route explanation to the analysis status index, and prune bibliography fields not needed for submission while preserving Zotero ownership rules.

**Proof oracle**

Notation search shows one loading symbol; repository and bibliography checks are quiet and intentional.

## Recommended repair sequence

1. **Freeze the defensible publication baseline.** Record the exact Phase 2 parameter/reaction hashes, accepted-row counts, metrics, and figures. Mark all Phase 3 fit/sensitivity/split artifacts as non-publication until regenerated.
2. **Unify scientific ownership.** Implement canonical reaction and parameter catalogs plus a strict solver-acceptance contract. Remove hard-coded duplicates.
3. **Resolve the parameter claim.** Either run the native full-row ion fit and regenerate Phase 3, or remove current-fit language and retain a fixed-parameter Phase 2 paper.
4. **Repair data provenance.** Rebuild VLE data with row-level source lineage, including Idris; standardize schemas and uncertainty fields.
5. **Consolidate artifacts.** Choose one calculation output owner and hash-linked figure snapshots. Delete redundant/stale copies and absolute paths.
6. **Build scientific gates.** Add reaction-catalog, solver-acceptance, artifact-freshness, claim-table, lint, and manuscript-build checks in CI.
7. **Revise the manuscript.** Separate executed/proposed/historical work, add computational detail, regenerate tables/figures, and complete submission front matter and archive metadata.
8. **Perform the final clean-checkout reproduction.** Regenerate data, plots, tables, and PDF from the pinned tag; archive the receipt and release.

## Open questions requiring an explicit project decision

1. Is the intended paper a defensible fixed-parameter Phase 2 evaluation, or must it make a novel direct MEAH+/MEACOO- regression claim? This choice controls whether Phase 3 regeneration is mandatory for submission.
2. Should the Idris VLE data remain in the 161-row pressure set after its uncertainty and row transformations are captured, or should all reported metrics be recomputed without it?
3. What is the selected journal/template and its required data/code archive policy? The current CAS template is usable, but affiliation, highlights/graphical abstract, declarations, and archive requirements are venue-dependent.
4. The exact pseudo-component balance convention should be documented against the pinned upstream solver API before revising the displayed balance equations. The audit found no retained package-level derivation sufficient to claim that the displayed normalized mole-fraction balances are the unique canonical formulation.

## Completion criteria for a submission-ready repository

- No P0 or P1 finding remains open.
- One reaction/parameter basis is traceable from source literature through runtime, artifacts, tables, and prose.
- All reported solver rows satisfy explicit acceptance criteria; failures are visible and excluded/penalized consistently.
- Every combined experimental row has source-level provenance, units, uncertainty/role, and deterministic generation.
- A clean checkout reproduces approved data, figures, manuscript tables, and PDF through one final command.
- The final PDF is visually reviewed, citation-complete, metadata-clean, archived at a tagged release/DOI, and linked to an explicit license.

## Audit commands and artifacts inspected

- Repository inventory via Git-tracked file counts, sizes, duplicate hashes, analysis manifests, source/module complexity, and artifact-path scans.
- `uv run python scripts/validate_project.py quick`
- `uv run python scripts/check_epcsaft_integration.py --mode final`
- `ruff check src scripts analyses tests --output-format concise`
- Phase 1/2/3 CSV/JSON summaries, solver diagnostics, manifests, tests, and plot sidecars.
- Manuscript LaTeX sources, bibliography, generated figures, a fresh `latexmk` build, and rendered review of all 19 PDF pages.
- Pinned upstream `epcsaft` equation documentation at commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` for the Born/SSM/DS formulation.
- Primary-source web verification for the missing Idris VLE citation and DOI.
