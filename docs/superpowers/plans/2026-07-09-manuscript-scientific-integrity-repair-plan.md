# Manuscript Scientific Integrity Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the fixed-parameter Phase 2 manuscript scientifically reproducible by unifying reaction ownership, rejecting nonconverged states, removing unsupported Phase 3 fit claims, repairing VLE provenance, and enforcing calculation-to-PDF proof gates.

**Architecture:** A pure-data reaction catalog becomes the single chemistry source for activity-based workflows, while a separate acceptance module owns solver-result admissibility. Canonical result tables live under each analysis `results/` root; figure folders retain only plotted snapshots and render artifacts with upstream hashes. The manuscript is cut over to the verified Phase 2 fixed-parameter campaign and generated/validated from pinned code and data.

**Tech Stack:** Python 3.13, `uv`, `unittest`, NumPy, pandas, pinned `epcsaft` 1.5.2, Matplotlib, Ruff, Bash, LaTeX/`latexmk`, GitHub Actions.

## Global Constraints

- Preserve the verified Phase 2 activity campaign: 161 converged pressure records, 74 converged speciation records, strict acceptance for all auxiliary curve states, and source-verified Nasrifar/Austgen activity constants.
- Treat the disabled eight-row SciPy fit and every dependent fit/sensitivity/validation claim as non-publication evidence; do not invent a replacement fit.
- Use repository-relative POSIX artifact paths and fail loudly on nonconvergence, missing provenance, stale artifacts, or unsupported promotion.
- Keep ideal-baseline and activity-model reaction bases explicitly named; do not force genuinely different literature conventions into one unlabeled coefficient set.
- Use TDD for code and validation changes; use systematic diagnosis for any failed scientific regeneration; verify before each completion or merge claim.
- Implement on `codex/manuscript-scientific-integrity-repair`; do not push, publish, or merge until the bounded Auto Mode clean-premerge proof passes.
- License selection, journal-specific front matter, archival DOI minting, and a new native full-row ion regression are outside this plan because they require authority or evidence not present in the source audit.

---

## Intake and linkage

- **Source findings:** `docs/superpowers/specs/2026-07-09-full-project-and-manuscript-audit-findings.md`
- **Auto Mode authorization:** `.superpowers/runs/2026-07-09-mea-project-audit/auto-mode-authorization.json`
- **Milestones:** Phase 2 Activity ePC-SAFT, Phase 3 Ionic Regression, Manuscript Submission
- **Execution route:** direct plan implementation, inline in the current thread, no GitHub issue mirror
- **Companion methods:** `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`

## Outcome Proof

**Intent:** Restore one internally consistent and reproducible scientific story without overstating the incomplete Phase 3 regression program.

**Current Behavior:** Phase 2/manuscript and Phase 3 use different reaction constants; historical local-fit artifacts are presented as current fit evidence; best-effort nonconvergence can be marked successful; 10 Idris VLE rows lack manuscript provenance; generated summaries store absolute paths; validation proves artifact presence more strongly than scientific freshness.

**Expected Outcome:** The active manuscript reports only the verified fixed-parameter Phase 2 campaign, all activity workflows consume one source-verified reaction catalog, rejected solver states cannot enter accepted metrics, every VLE source is cited and testable, and one final command proves source-to-PDF consistency.

**Target Output:** A clean development branch containing the canonical chemistry/acceptance seams, repaired data provenance and artifacts, revised manuscript/PDF, tiered validation, and machine-readable final verification receipt.

**Owner:** `MEA-Thermodynamics` owns reaction/data selection, downstream solver acceptance, analysis artifacts, and manuscript claims; pinned `epcsaft` owns thermodynamic kernels and native solver/regression implementations.

**Interface:** Python modules under `src/MEA/common`, analysis `generate_data.py`/`render_figures.py` entrypoints, `scripts/validate_project.py`, `scripts/build_manuscript.sh`, and `docs/latex/main.tex`.

**Cutover:** The fixed-parameter Phase 2 campaign becomes the only publication campaign. Active code and tests stop treating the disabled local ion fit, unexecuted coupled regression, and post hoc split as publication evidence.

**Replaced Path:** Replace hard-coded Phase 3 `REACTION_CONSTANTS`, permissive `success` propagation, absolute-path serialization, duplicated result ownership, and manuscript fit/validation language. Remove obsolete historical-fit publication artifacts instead of retaining redirects or compatibility copies.

**Evidence:** Focused red/green tests; canonical catalog/hash receipts; regenerated accepted-row summaries; deterministic VLE build; clean Ruff; quick/final validation; fresh LaTeX build; rendered PDF review; clean Git diff after a second regeneration.

**Acceptance Proof:** All commands in `## Test Complete and Metrics` pass, the final receipt records exact counts/hashes, the fresh PDF contains no current direct-fit or train-validation claim, and `git diff --exit-code` is clean after deterministic regeneration.

**Stop Criteria:** Stop before scientific mutation if the source constants cannot reproduce Phase 2; if a required change would alter the verified Phase 2 residuals without an explained data/model change; if the pinned package cannot provide required solver evidence; if a license/journal/new-fit decision is required; or if any final validation fails.

**Avoid:** No fallback constants, no best-effort state promoted as converged, no manual editing of generated numerical results, no fake default fit, no compatibility artifact mirrors, no local absolute paths, no unsupported “This work” parameter claim, and no direct implementation on `main`.

**Risk:** Regenerating Phase 3 with corrected chemistry may materially change diagnostic values. This plan avoids using those values in the paper and records any retained Phase 3 output as diagnostic until a separate native-regression plan is approved.

## Implementation Boundaries

**Files To Create:** `src/MEA/common/reaction_catalog.py`, `src/MEA/common/solver_acceptance.py`, `scripts/build_canonical_vle_dataset.py`, `scripts/build_manuscript.sh`, `scripts/check_manuscript_freshness.py`, `tests/test_reaction_catalog.py`, `tests/test_solver_acceptance.py`, `tests/test_canonical_vle_dataset.py`, `tests/test_manuscript_claim_integrity.py`, `.github/workflows/validate.yml`, `data/reference/MEA/VLE/Idris_2014_VLE.csv`, `data/reference/MEA/VLE/Combined_VLE_inclusion.csv`, and `docs/latex/builds/verification-receipt.json` (generated/ignored as appropriate).

**Files To Modify:** `src/MEA/epcsaft_ionic/model.py`, Phase 2/3 generators and renderers, artifact/path helpers, validation scripts, analysis manifests, parameter provenance tables, manuscript sections/tables, bibliography, README, `pyproject.toml`, `uv.lock`, `.gitignore`, and affected tests.

**Files To Avoid:** Upstream `ePC-SAFT`, plugin cache files, source-literature markdown/PDF exports, Zotero-owned bibliography fields unrelated to the new Idris entry, and unrelated user changes.

**Source Of Truth:** Activity reaction coefficients come from `data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv`; VLE rows come from source-specific CSVs plus `Combined_VLE_inclusion.csv`; publication metrics come from Phase 2 canonical `results/`; manuscript tables/figures consume those canonical artifacts.

**Read Path:** Source manifests/data → pure catalog/loaders → solver adapters → accepted canonical results → plotted snapshots/tables → LaTeX → PDF.

**Write Path:** Generators write canonical calculation outputs once under `results/`; renderers write plotted subsets plus `.mpl.yaml`/PNG/SVG/PDF to figure output and copy only approved PDF figures to `docs/latex/figures`.

**Integration Points:** `load_epcsaft()`, `ReactionDefinition.from_literature_constant`, Phase 2 `generate_data.py`, Phase 3 model/evaluation, common reporting/path helpers, `validate_project.py`, and `latexmk`.

**Migration Or Cutover:** Regenerate current artifacts from new owners, delete redundant/stale mirrors and historical publication plots, update manifests/tests atomically, then revise manuscript claims and rebuild the PDF.

**Replaced Path Handling:** Delete old hard-coded constants and historical-fit publication files. Do not preserve alias constants, deprecated loaders, legacy folders, compatibility snapshots, or redirects.

**Acceptance Proof Gate:** A task cannot close unless its focused tests pass and its replaced path is absent. The plan cannot close unless all final metrics, freshness, cleanup, and clean-premerge checks pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Publication campaign | Audit recommended disposition + Auto Mode recorded default | Preserve the verified fixed-parameter Phase 2 campaign and remove unsupported Phase 3 fit claims. | Avoids inventing a native fit and gives the paper one reproducible basis. | No | manuscript maintainer |
| Reaction source of truth | Audit P0 evidence | Use the Phase 2 source-verification manifest for activity workflows; keep ideal literature basis separately named. | Removes the chemistry split without conflating ideal and activity conventions. | No | thermodynamic-model maintainer |
| Solver acceptance | Audit P1 evidence | Accepted means solver success, converged status, finite state, and all declared residual thresholds pass. | Nonconverged best-effort states cannot enter metrics. | No | solver-adapter maintainer |
| Historical fit handling | Audit P0 evidence + repository no-legacy policy | Remove publication claims and obsolete fit figures/artifacts; keep no compatibility path. | Parameter values remain explicitly provisional fixed inputs, not a current regression result. | No | parameter-provenance maintainer |
| VLE Idris rows | Audit primary-source verification | Retain the 10 rows, add source CSV/citation/row lineage, and rebuild the 161-row table deterministically. | Preserves current Phase 2 counts while correcting provenance. | No | data-provenance maintainer |
| Artifact owner | Audit duplicate/hash evidence | Canonical numerical outputs live once under analysis `results/`; figure folders own only plotted snapshots and render bundles. | Eliminates drift and clarifies calculation-to-figure lineage. | No | analysis-artifact maintainer |
| Test-complete threshold | Source artifacts + Auto Mode recorded default | Require 161 converged pressure rows, 74 converged speciation rows, 642 accepted plus 2 explicitly rejected auxiliary curve states, accepted charge residual ≤1e-6, accepted reaction residual ≤1e-7, no nonconverged accepted rows, and deterministic rebuild. | Converts manuscript claims into executable gates without hiding strict-gate failures. | No | validation maintainer |
| TDD policy | Required planning method | Use red/green focused tests before every code-path repair; diagnostic regeneration follows systematic debugging on failure. | Prevents artifact-led changes from masking broken contracts. | No | implementation maintainer |
| Branch/topology | Auto Mode authorization + multi-agent restriction | Use `codex/manuscript-scientific-integrity-repair`, inline execution, no subagents. | Keeps changes isolated while respecting current collaboration policy. | No | implementation maintainer |
| Publish/merge behavior | Auto Mode authorization | No push; local merge is preauthorized only after clean premerge proof and verification. | Prevents unverified external mutation. | No | merge maintainer |
| License and DOI | Audit open question | Do not choose a license or mint/archive a DOI in this plan. Record the remaining submission blocker. | Scientific integrity can close without inventing legal/venue authority. | Yes | repository owner |
| Journal-specific front matter | Audit open question | Apply venue-neutral corrections only (single-author running head, metadata, reproducibility); defer journal-specific declarations/assets. | Avoids guessing the target venue. | Yes | corresponding author |
| Native full-row regression | Audit open question | Exclude from this plan; require a separate upstream-backed plan if the author wants a novel fit claim. | Keeps this repair reproducible with currently available evidence. | Yes | regression owner |

## Test Complete and Metrics

Test complete means all of the following are true:

1. `uv run python -m unittest discover tests -v` passes.
2. `ruff check src scripts analyses tests` reports zero violations.
3. `uv run python scripts/validate_project.py quick` passes.
4. `uv run python scripts/check_epcsaft_integration.py --mode final` passes at the pinned commit.
5. Phase 2 regenerated summaries contain exactly 161 converged pressure rows, 74 converged speciation targets, 642 accepted and 2 explicitly rejected auxiliary curve diagnostics; accepted maximum absolute charge residual is at most `1e-6`, accepted maximum absolute reaction residual is at most `1e-7`, and accepted nonconverged rows equal zero.
6. The canonical VLE builder produces 161 unique rows from six cited sources with exactly 10 Idris rows; a second build produces no diff.
7. No tracked parsed JSON value contains a local home/worktree path.
8. No current manuscript source contains “direct amine-ion regression,” “train-validation split,” or a “This work” label for MEAH+/MEACOO- fitted values.
9. `bash scripts/build_manuscript.sh` succeeds, `uv run python scripts/check_manuscript_freshness.py` passes, citations/references are defined, and rendered visual review finds no clipping or unreadable manuscript figures.
10. `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .` reports `cleanup_state: complete`, and the branch is clean after intended files are committed.

## Non-goals

- Completing or claiming a new native coupled pressure/speciation regression.
- Choosing the repository license, minting a DOI, selecting the journal, or modifying the external Overleaf mirror.
- Changing upstream ePC-SAFT thermodynamic kernels or API contracts.
- Improving Phase 2 residual values by fitting new parameters.
- Retaining historical artifacts through renamed legacy/backup folders.

### Task 1: Canonical activity reaction catalog

**Use Cases:**
- Phase 2 and Phase 3 request activity reaction coefficients and receive byte-equivalent values from one source manifest.
- A missing, duplicate, unverified, nonfinite, or malformed reaction row fails before a solver call.
- The ideal baseline can retain a separately named literature basis without being mislabeled as the activity catalog.
- A manuscript/runtime consistency test catches coefficient or stoichiometry drift.

**Files:**
- Create: `src/MEA/common/reaction_catalog.py`
- Create: `tests/test_reaction_catalog.py`
- Modify: `src/MEA/epcsaft_ionic/model.py:29-42,397-418`
- Modify: `analyses/phase2/activity_epcsaft/scripts/generate_data.py`
- Modify: `tests/test_phase2_activity_scaffold.py`

**Interfaces:**
- Consumes: `phase2_reaction_constant_source_verification.csv` with `reaction_id`, `source_value_A..D`, `source_verified`, and provenance fields.
- Produces: `ReactionCoefficient`, `load_activity_reaction_catalog() -> tuple[ReactionCoefficient, ...]`, `activity_coefficient_map() -> dict[str, tuple[float,float,float,float]]`, and `reaction_catalog_sha256() -> str`.

- [ ] **Step 1: Write failing catalog contract tests**

```python
def test_runtime_activity_coefficients_equal_verified_manifest():
    rows = load_activity_reaction_catalog()
    assert [row.reaction_id for row in rows] == ["R1", "R2", "R3", "R4", "R5"]
    assert activity_coefficient_map()["R4_MEACOO_hydrolysis"] == (2.8898, -3635.09, 0.0, 0.0)
    assert model.activity_coefficient_map() == activity_coefficient_map()

def test_unverified_or_duplicate_catalog_fails_loudly(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("reaction_id,source_verified\nR1,no\nR1,no\n", encoding="utf-8")
    with pytest.raises(ValueError, match="verified unique R1-R5"):
        load_activity_reaction_catalog(bad)
```

- [ ] **Step 2: Run the focused tests and confirm coefficient ownership fails**

Run: `uv run python -m unittest tests.test_reaction_catalog -v`
Expected: failure because the catalog module and runtime seam do not exist.

- [ ] **Step 3: Implement the pure-data catalog and replace hard-coded Phase 3 constants**

```python
@dataclass(frozen=True)
class ReactionCoefficient:
    reaction_id: str
    name: str
    a: float
    b: float
    c: float
    d: float
    source_key: str

    def coefficients(self) -> tuple[float, float, float, float]:
        return (self.a, self.b, self.c, self.d)
```

Load and validate the five rows, map `R1..R5` to the existing reaction names, compute the catalog hash from normalized JSON, import the catalog in `model.py`, and remove `REACTION_CONSTANTS`. Refactor the Phase 2 generator to consume the same map rather than parse coefficients independently.

- [ ] **Step 4: Run focused and Phase 2 scaffold tests**

Run: `uv run python -m unittest tests.test_reaction_catalog tests.test_phase2_activity_scaffold -v`
Expected: pass with R4 `(2.8898, -3635.09, 0.0, 0.0)` and all five runtime rows equal to the manifest.

- [ ] **Step 5: Commit the catalog cutover**

```bash
git add src/MEA/common/reaction_catalog.py src/MEA/epcsaft_ionic/model.py analyses/phase2/activity_epcsaft/scripts/generate_data.py tests/test_reaction_catalog.py tests/test_phase2_activity_scaffold.py
git commit -m "fix: unify activity reaction constants"
```

### Task 2: Strict solver acceptance contract

**Use Cases:**
- A best-effort result with `success=True` and `message="chemical equilibrium did not converge"` is rejected.
- A converged state with residuals within thresholds is accepted.
- Nonfinite mole fractions, excessive mass/charge/reaction residuals, or state failures have explicit rejection reasons.
- Metrics and plots include only accepted rows while preserving rejected-row diagnostics.

**Files:**
- Create: `src/MEA/common/solver_acceptance.py`
- Create: `tests/test_solver_acceptance.py`
- Modify: `src/MEA/epcsaft_ionic/model.py:160-209,438-492`
- Modify: `src/MEA/epcsaft_ionic/plot_results.py`
- Modify: `src/MEA/epcsaft_ionic/global_regression.py`
- Modify: Phase 3 analysis scripts that aggregate `success`

**Interfaces:**
- Consumes: solver boolean/message, state vector, mass residuals, charge residual, reaction residuals, state-failure count, and configured tolerances.
- Produces: `AcceptanceDecision(accepted: bool, rejection_reasons: tuple[str, ...])` and explicit `solver_returned`, `accepted`, `rejection_reason` artifact columns.

- [ ] **Step 1: Write failing acceptance tests**

```python
def test_nonconverged_best_effort_is_rejected():
    decision = assess_speciation_result(
        solver_success=True,
        message="chemical equilibrium did not converge",
        x=np.full(9, 1 / 9),
        mass_residuals={"carbon_total": 0.0},
        charge_residual=0.0,
        reaction_residuals={"R1": 0.0},
        state_failure_count=0,
    )
    assert not decision.accepted
    assert "nonconverged_status" in decision.rejection_reasons
```

- [ ] **Step 2: Run focused tests and confirm permissive behavior fails**

Run: `uv run python -m unittest tests.test_solver_acceptance -v`
Expected: failure because no acceptance module exists.

- [ ] **Step 3: Implement thresholds and cut aggregators over to `accepted`**

Use `mass_tolerance=1e-7`, `charge_tolerance=1e-6`, and `reaction_tolerance=1e-7`; require normalized finite positive composition and `state_failure_count == 0`. Preserve raw solver return fields separately and delete equality-to-`True` pandas checks.

- [ ] **Step 4: Run focused tests plus affected ionic tests**

Run: `uv run python -m unittest tests.test_solver_acceptance tests.test_epcsaft_ionic_approval_check tests.test_global_regression_artifacts -v`
Expected: all acceptance cases pass; no accepted nonconverged fixture remains.

- [ ] **Step 5: Commit strict acceptance semantics**

```bash
git add src/MEA/common/solver_acceptance.py src/MEA/epcsaft_ionic tests/test_solver_acceptance.py tests/test_epcsaft_ionic_approval_check.py tests/test_global_regression_artifacts.py analyses/phase3/ionic_epcsaft_regression/scripts
git commit -m "fix: reject nonconverged ionic states"
```

### Task 3: Cut the manuscript over to fixed-parameter Phase 2 evidence

**Use Cases:**
- A reader can distinguish the executed Phase 2 evaluation from unexecuted regression work.
- MEAH+/MEACOO- values are reported as provisional fixed inputs, not a reproducible current fit.
- Historical direct-fit figures and train-validation language cannot re-enter the PDF unnoticed.
- Parameter tables expose source/status without calling retained values initial or “This work.”

**Files:**
- Modify: `docs/latex/sections/data_methods.tex`
- Modify: `docs/latex/sections/mea_system_modeling_results.tex`
- Modify: `docs/latex/sections/conclusion.tex`
- Modify: `docs/latex/tables/full_ionic_ssm_ds_parameters.tex`
- Modify: `docs/latex/tables/regression_bounds.tex` or delete if no longer referenced
- Modify: `docs/latex/tables/literature_model_comparison.tex`
- Modify: `data/reference/MEA/manifests/parameter_provenance_manifest.csv`
- Create: `tests/test_manuscript_claim_integrity.py`
- Delete: obsolete manuscript direct-fit PDF copies and active artifact-promotion expectations

**Interfaces:**
- Consumes: Phase 2 residual tables and current parameter dataset.
- Produces: manuscript prose/tables containing only executed claims and a static claim-integrity guard.

- [ ] **Step 1: Write failing forbidden-claim tests**

```python
def test_manuscript_does_not_promote_historical_fit():
    manuscript = "\n".join(path.read_text() for path in LATEX_ROOT.rglob("*.tex"))
    for phrase in ("direct amine-ion regression", "train-validation split", "retained fit decreases"):
        assert phrase not in manuscript
    assert "fixed provisional input" in manuscript
```

- [ ] **Step 2: Run the test and verify current prose fails**

Run: `uv run python -m unittest tests.test_manuscript_claim_integrity -v`
Expected: failure on current direct-fit and train-validation language.

- [ ] **Step 3: Remove historical promotion and rewrite the parameter-evidence boundary**

Delete the direct-fit results subsection/figure and post hoc validation claim. Replace the regression-method section with an explicit statement that a coupled/native regression was not completed and the retained MEAH+/MEACOO- values are provisional fixed inputs inherited from an exploratory historical calculation. Remove “This work” and rename table columns to `Retained value`, `Source/status`, and bounds only where bounds remain scientifically relevant.

- [ ] **Step 4: Remove obsolete artifact contracts and files**

Delete historical publication plot copies from `docs/latex/figures`, remove them from `scripts/validate_project.py`, replace `test_promoted_ion_fit_*` with nonpromotion guards, and remove dead local-fit code/imports that have no active diagnostic owner.

- [ ] **Step 5: Run manuscript claim and affected artifact tests**

Run: `uv run python -m unittest tests.test_manuscript_claim_integrity tests.test_ion_parameter_regression_artifacts tests.test_epcsaft_ionic_artifact_promotion -v`
Expected: manuscript claim guard passes and no test calls the historical artifact promoted.

- [ ] **Step 6: Commit the publication-scope cutover**

```bash
git add docs/latex data/reference/MEA/manifests scripts/validate_project.py tests src/MEA/epcsaft_ionic
git commit -m "fix: scope manuscript to verified phase2 evidence"
```

### Task 4: Deterministic six-source VLE provenance

**Use Cases:**
- The 10 Idris rows are traceable to DOI `10.1016/j.egypro.2014.11.152` and included intentionally.
- Every combined row resolves to one source-specific row and has stable units/identity.
- Duplicate/unmatched/ambiguous inclusion rows fail the builder.
- Manuscript source counts and citations equal dataset source counts.

**Files:**
- Create: `data/reference/MEA/VLE/Idris_2014_VLE.csv`
- Create: `data/reference/MEA/VLE/Combined_VLE_inclusion.csv`
- Create: `scripts/build_canonical_vle_dataset.py`
- Create: `tests/test_canonical_vle_dataset.py`
- Modify: `data/reference/MEA/VLE/Combined_VLE.csv`
- Modify: `data/reference/MEA/manifests/source_status_manifest.csv`
- Modify: `docs/latex/references.bib`
- Modify: `docs/latex/sections/data_methods.tex`

**Interfaces:**
- Consumes: six source-specific VLE CSVs and an inclusion manifest keyed by source plus source-row identity.
- Produces: deterministic `Combined_VLE.csv` with existing model columns plus `row_id`, `source_key`, `source_file`, and `source_row` provenance.

- [ ] **Step 1: Write failing source-count and lineage tests**

```python
def test_combined_vle_has_complete_source_lineage():
    frame = pd.read_csv(COMBINED)
    assert len(frame) == 161
    assert frame["source_key"].value_counts().to_dict()["Idris2014"] == 10
    assert set(frame["source_key"]) == {"Aronu2011", "Hilliard2008", "Idris2014", "Jou1995", "Mamun2005", "Xu2011"}
    assert not frame[["row_id", "source_file", "source_row"]].isna().any().any()
```

- [ ] **Step 2: Run the tests and confirm the missing Idris/source columns fail**

Run: `uv run python -m unittest tests.test_canonical_vle_dataset -v`
Expected: failure because only five source CSVs exist and the combined table lacks lineage.

- [ ] **Step 3: Add the Idris source and inclusion manifest**

Enter the 10 retained 30 wt%/40 °C rows exactly as published/retained, with loading, pressure, uncertainty where available, table locator, DOI, and source row. Build the inclusion manifest for all 161 currently approved rows by exact numeric/source matching.

- [ ] **Step 4: Implement the deterministic builder**

The builder must normalize headers/units, require one exact source match per inclusion row, preserve the approved ordering, generate stable `vle_0001..vle_0161` IDs, and write through the repository CSV helper. It must never use the existing combined output as an input.

- [ ] **Step 5: Update data consumers and manuscript citations**

Keep the existing `MEA_weight_fraction`, `temperature`, `CO2_loading`, `CO2_pressure`, and `paper` compatibility-free public columns as actual canonical fields, while teaching loaders to use `source_key`. Change “five” to “six” and cite `Idris2014` in text/table.

- [ ] **Step 6: Prove deterministic regeneration**

Run: `uv run python scripts/build_canonical_vle_dataset.py && uv run python -m unittest tests.test_canonical_vle_dataset -v && git diff --exit-code data/reference/MEA/VLE/Combined_VLE.csv`
Expected: 161 rows, six sources, 10 Idris rows, tests pass, no second-build diff.

- [ ] **Step 7: Commit VLE provenance**

```bash
git add data/reference/MEA/VLE data/reference/MEA/manifests/source_status_manifest.csv scripts/build_canonical_vle_dataset.py tests/test_canonical_vle_dataset.py docs/latex/references.bib docs/latex/sections/data_methods.tex src/MEA/common/data_access.py
git commit -m "fix: make vle provenance reproducible"
```

### Task 5: Portable artifact paths and single artifact ownership

**Use Cases:**
- Generated JSON resolves artifact paths from any clone root.
- JSON-escaped Windows paths and POSIX home/worktree paths fail validation.
- Phase 1/2 calculations have one canonical result-table owner.
- Figure snapshots record upstream paths/hashes and cannot drift silently.

**Files:**
- Modify: `src/MEA/common/analysis_io.py`
- Modify: `scripts/check_no_local_paths.py`
- Modify: `src/MEA/epcsaft_ionic/plot_results.py`
- Modify: `src/MEA/epcsaft_ionic/regress_parameters.py`
- Modify: Phase 1/2 generators/renderers and `analysis.yaml` files
- Modify: `scripts/validate_project.py`
- Create or modify: path/artifact lineage tests under `tests/`
- Delete: redundant `data/processed`/`results`/figure-output mirrors identified in the audit

**Interfaces:**
- Consumes: absolute or repository-relative `Path` objects and canonical result IDs.
- Produces: `repo_relative_path(path: Path) -> str`, parsed-JSON path validation, and sidecars with `data_path` plus `data_sha256`.

- [ ] **Step 1: Write failing path and duplicate-owner tests**

```python
def test_json_escaped_windows_path_is_rejected(tmp_path):
    path = tmp_path / "summary.json"
    path.write_text('{"artifact":"C:\\\\Users\\\\Tanner\\\\result.csv"}')
    assert scan_file(path)

def test_repo_relative_path_rejects_external_path():
    with pytest.raises(ValueError, match="outside repository"):
        repo_relative_path(Path("/tmp/result.csv"))
```

- [ ] **Step 2: Run focused tests and verify current guard misses escaped JSON**

Run: `uv run python -m unittest tests.test_project_structure -v` (or the exact new test module)
Expected: failure on escaped-path and duplicate-owner fixtures.

- [ ] **Step 3: Implement relative-path serialization and parsed JSON scanning**

Use `Path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()` with a loud `ValueError` outside the repository. Recursively inspect parsed JSON strings and raw text. Replace all `str(path)` artifact writes.

- [ ] **Step 4: Cut result ownership over and delete mirrors**

Keep canonical calculation outputs under `results/`; retain only plotted subsets and render bundles in figure output. Add upstream relative path/hash to `.mpl.yaml`. Remove mirrored whole-table writes and update manifests/validation requirements atomically.

- [ ] **Step 5: Regenerate affected lightweight artifacts and test lineage**

Run the Phase 1/2 generation and render commands, then assert no duplicate logical artifact IDs, no local paths, and matching sidecar hashes.

- [ ] **Step 6: Commit artifact ownership repair**

```bash
git add src scripts analyses tests
git commit -m "refactor: enforce portable artifact ownership"
```

### Task 6: Lint, dependency, CI, and manuscript build gates

**Use Cases:**
- A clean clone gets the same locked environment and quick validation.
- Ruff catches dead imports/unresolved names before scientific validation.
- The manuscript builds only into `docs/latex/builds` and freshness is machine-checked.
- CI runs safe non-expensive checks without pretending to run the expensive native regression.

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: Python files reported by Ruff
- Create: `scripts/build_manuscript.sh`
- Create: `scripts/check_manuscript_freshness.py`
- Create: `.github/workflows/validate.yml`
- Modify: `README.md`
- Modify: `.gitignore`
- Modify: `scripts/validate_project.py`

**Interfaces:**
- Consumes: locked dependencies, validated canonical artifacts, LaTeX source/figures.
- Produces: zero-warning Ruff gate, `docs/latex/builds/main.pdf`, freshness result, and CI receipts.

- [ ] **Step 1: Add Ruff configuration and run the expected red check**

Configure target version `py313`, source roots, and narrow intentional E402 per-file ignores only for scripts that must bootstrap `src`. Run `ruff check src scripts analyses tests`; expected initial result is the audited 51 violations.

- [ ] **Step 2: Remove dead imports and fix unresolved names without broad suppressions**

Delete unused imports/code and add required `Path` imports only where the path-returning functions remain active. Re-run Ruff until zero violations.

- [ ] **Step 3: Prove or remove unused dependencies**

Remove `numdifftools`, `pillow`, `plotly`, `streamlit`, and `sympy` from runtime dependencies unless a tracked command/import proves ownership; retain IDAES/Pyomo only as the documented optional `idaes` group. Run `uv lock` and `uv sync --locked`.

- [ ] **Step 4: Implement canonical manuscript build/freshness scripts**

`build_manuscript.sh` must run `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=builds main.tex` from `docs/latex`. The freshness checker must compare `main.pdf` mtime/hash against tracked `.tex`, `.bib`, table, and figure inputs and fail on undefined citations/references or a stale PDF.

- [ ] **Step 5: Add CI and tiered validation**

CI runs `uv sync --locked --group test`, Ruff, quick validation, final pinned integration smoke, and manuscript build/freshness where TeX is available. Label expensive Phase 3 regeneration explicitly as a manual final-release gate.

- [ ] **Step 6: Run all new gates**

Run: `ruff check src scripts analyses tests && uv run python scripts/validate_project.py quick && bash scripts/build_manuscript.sh && uv run python scripts/check_manuscript_freshness.py`
Expected: all pass; output PDF is `docs/latex/builds/main.pdf`.

- [ ] **Step 7: Commit validation infrastructure**

```bash
git add pyproject.toml uv.lock src scripts analyses tests .github README.md .gitignore docs/latex
git commit -m "build: add scientific manuscript validation gates"
```

### Task 7: Regenerate and reconcile current scientific/manuscript artifacts

**Use Cases:**
- Phase 2 regenerates with unchanged approved metrics and the canonical reaction hash.
- Phase 3 diagnostics use corrected chemistry and strict acceptance but remain outside manuscript claims.
- A failed or changed scientific metric stops the workflow with a diagnostic diff.
- Analysis manifests and plot discovery describe only current owners.

**Files:**
- Modify/generated: Phase 1/2/3 canonical result artifacts
- Modify: all seven `analysis.yaml` files and missing analysis README
- Modify: `.mplgallery/manifest.yaml`
- Modify/generated: `docs/latex/figures/*.pdf`, generated manuscript tables, `docs/latex/builds/main.pdf`
- Create: final verification receipt under `.superpowers/runs/2026-07-09-mea-project-audit/`

**Interfaces:**
- Consumes: Tasks 1–6 canonical code/data/contracts.
- Produces: current deterministic artifacts with catalog/data hashes and one final publication receipt.

- [x] **Step 1: Run Phase 1/2 data generation under systematic-debugging discipline**

Run: `uv run python scripts/generate_all_analysis_data.py`
Expected: Phase 1/2 complete; Phase 2 remains 161 converged pressure rows and 74 converged speciation rows, with 642 accepted plus 2 explicitly rejected auxiliary curve states at the canonical reaction gate. Any metric change stops execution for root-cause analysis.

- [x] **Step 2: Regenerate Phase 3 diagnostic evaluation with corrected chemistry**

Run only the active non-fit diagnostic generator. Do not call the disabled local fit or claim promotion. Verify rejected/nonconverged counts are explicit and excluded from accepted metrics.

- [x] **Step 3: Render all plots and update manuscript figure copies**

Run: `uv run python scripts/render_all_plots.py`
Expected: plot sidecar hashes match plotted data; no historical direct-fit figure is copied to the manuscript.

- [x] **Step 4: Normalize analysis manifests and plot registry**

Give every manifest `id`, `title`, `status`, `summary`, `owner`, typed `inputs`, typed `outputs`, `commands`, runtime class, manuscript consumers, and results policy. Add the missing Smith-Missen README and regenerate MPLGallery after duplicate removal.

- [x] **Step 5: Rebuild and visually inspect the PDF**

Run the canonical build, render all pages, and inspect title metadata, figure text, floats, and nomenclature. Correct the single-author running head and loading notation; do not add venue-specific author fields.

- [x] **Step 6: Prove deterministic second regeneration**

Repeat VLE build, analysis generation, render, and manuscript build; run `git diff --exit-code` against the first regenerated state. Any diff blocks completion.

- [x] **Step 7: Commit regenerated evidence**

```bash
git add analyses data docs .mplgallery README.md tests scripts
git commit -m "docs: regenerate verified manuscript evidence"
```

### Task 8: Final verification and clean-premerge proof

**Use Cases:**
- The branch cannot be called complete if any focused/full gate fails.
- The cleanup hook leaves no task-owned processes or temp artifacts.
- The merge handoff records exact scientific counts, hashes, commits, and deferred owner decisions.
- No issue/PR closure is claimed because this is a direct plan route.

**Files:**
- Modify: plan checkboxes as tasks complete
- Create/generated: `.superpowers/runs/2026-07-09-mea-project-audit/final-verification.json`
- Modify: `docs/.codex-journal/project_memory.md` with durable final workflow facts only

**Interfaces:**
- Consumes: completed branch and all prior proof artifacts.
- Produces: clean-premerge proof suitable for bounded Auto Mode local merge.

- [x] **Step 1: Run the complete proof oracle**

```bash
ruff check src scripts analyses tests
uv run python -m unittest discover tests -v
uv run python scripts/validate_project.py quick
uv run python scripts/check_epcsaft_integration.py --mode final
uv run python scripts/build_canonical_vle_dataset.py
bash scripts/build_manuscript.sh
uv run python scripts/check_manuscript_freshness.py
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
git diff --check
```

Expected: all exit zero; exact counts/tolerances match `## Test Complete and Metrics`.

- [x] **Step 2: Record structured readiness evidence**

Write `final-verification.json` with branch/commit list, catalog/data/parameter hashes, row/acceptance counts, residual maxima, test totals, PDF hash/page count, cleanup state, `plan_alignment`, `correctness`, `maintainability`, and `reality_evidence` all true.

- [x] **Step 3: Verify branch state and deferred blockers**

Confirm no unrelated changes, no untracked temp files, no local paths, and only the license/DOI/journal/new-fit decisions remain deferred to named owners.

- [x] **Step 4: Commit plan/verification bookkeeping**

```bash
git add docs/superpowers docs/.codex-journal/project_memory.md
git commit -m "chore: record scientific integrity verification"
```

- [x] **Step 5: Enter the bounded Auto Mode clean-premerge route**

Use `superpowers:verification-before-completion`, validate the Auto Mode ledger again, produce the merge-ready handoff, and merge locally only if the branch and target are clean. Do not push, open a PR, or claim GitHub issue closure.

## Plan self-review

- **Spec coverage:** All P0 findings and the scientific/reproducibility P1 findings map to Tasks 1–7. P2/P3 items needed to enforce the cutover (architecture seam, lint, manifests, plots, manuscript legibility/notation) are included. License/DOI, venue-specific front matter, and a new regression are explicitly deferred because the audit identifies them as authority/evidence decisions.
- **Placeholder scan:** Tasks name exact files, interfaces, commands, expected failures/passes, cutovers, and deletions. No implementation step relies on a compatibility path or unspecified error handling.
- **Type consistency:** The catalog, acceptance, path, builder, and validation interfaces are defined before consumers use them.
- **Test completeness:** Numerical thresholds, row counts, deterministic rebuild, source counts, claim strings, lint, package integration, PDF freshness, cleanup, and clean-premerge proof are explicit.
