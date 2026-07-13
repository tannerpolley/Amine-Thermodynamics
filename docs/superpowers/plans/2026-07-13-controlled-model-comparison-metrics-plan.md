# Controlled Model Comparison and Metric Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a deterministic same-record Phase 1/2 comparison with source-aware uncertainty, correct target-role counts, and manuscript-ready metrics.

**Architecture:** A pure comparison module joins canonical rows by stable identity, applies existing acceptance contracts, and writes paired and full-set contextual outputs consumed by manuscript tables.

**Tech Stack:** Python 3.13, pandas, NumPy, `uv`, pytest, LaTeX, Bash.

## Global Constraints

- Primary comparisons use identical eligible rows and units.
- Preserve target roles and expose rejected/missing predictions.
- Use TDD and diagnose the 14/15 mismatch at its canonical source before editing prose.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-controlled-model-comparison-metrics-design.md`.
- Inputs: Phase 1/2 canonical results and target-role manifests.

## Outcome Proof

**Intent:** Make ideal-versus-activity claims quantitatively comparable and traceable.
**Current Behavior:** Headline medians use different pressure row sets and the manuscript reports 14 rather than 15 reported-zero targets.
**Expected Outcome:** Paired metrics use one row intersection, full-set context is separate, and every count derives from canonical roles.
**Target Output:** Comparison module, paired CSV, metrics JSON/CSV, uncertainty coverage, revised table/text, and proof tests.
**Owner:** Model-validation maintainer.
**Interface:** `build_controlled_comparison()` and `analyses/phase2/activity_epcsaft/results/controlled_comparison/`.
**Cutover:** Manuscript comparisons consume generated paired metrics rather than manually juxtaposed summaries.
**Replaced Path:** Retire the manual 31-versus-161 comparison and hard-coded reported-zero count.
**Evidence:** Failing/passing join and count tests, regenerated artifacts, and manuscript consistency checks.
**Acceptance Proof:** Saved paired rows reproduce all published metrics and canonical role aggregation yields exactly 15 reported-zero targets unless source data intentionally change.
**Stop Criteria:** Stop on duplicate keys, incompatible units/reaction bases, role ambiguity, or unexplained row loss.
**Avoid:** No fake uncertainties, silent failure exclusion, or post hoc metric selection.
**Risk:** Intersection coverage may be small; publish coverage alongside effect metrics.

## Implementation Boundaries

**Files To Create:** `src/MEA/common/model_comparison.py`, `tests/test_model_comparison.py`, and controlled-comparison result artifacts.
**Files To Modify:** Phase 2 comparison generator, `docs/latex/tables/residual_summary.tex`, results narrative, and manuscript integrity tests.
**Files To Avoid:** Phase 3 fitted-parameter artifacts and upstream ePC-SAFT.
**Source Of Truth:** Canonical row identities, solver acceptance audits, and target-role manifests.
**Read Path:** Canonical data/results to comparison module to generated metrics.
**Write Path:** Generator writes canonical comparison results; LaTeX reads generated summaries.
**Integration Points:** `scripts/validate_project.py`, manuscript build, and source-log update.
**Migration Or Cutover:** Add tests first, generate comparison artifacts, then replace manuscript values.
**Replaced Path Handling:** Delete hard-coded count/comparison logic; retain no alias metric path.
**Acceptance Proof Gate:** A second generation produces no diff and focused plus confidence validation pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Primary comparison | Approved spec | Same-record intersection. | Enables paired inference. | No | statistics maintainer |
| Zero targets | Canonical roles | Derive count; expected current value 15. | Repairs mismatch at source. | No | data maintainer |

## Test Complete and Metrics

- Join tests reject duplicate/missing identities and unit mismatches.
- Paired metrics recompute byte-for-byte from saved rows.
- Source/temperature/role counts reconcile exactly.
- Manuscript build and focused integrity tests pass.

### Task 1: Build and prove the paired comparison

**Use Cases:**
- A reviewer can reproduce acceptance evidence from paired rows and see every displaced old metric.
- Missing or rejected predictions remain visible during cutover.

**Files:**
- Create: `src/MEA/common/model_comparison.py`, `tests/test_model_comparison.py`
- Modify: `analyses/phase2/activity_epcsaft/scripts/generate_data.py`

**Interfaces:**
- Consumes: canonical row IDs and accepted Phase 1/2 results.
- Produces: `build_controlled_comparison(...) -> ComparisonBundle` with paired rows and grouped metrics.

- [ ] **Step 1: RED** — add tests for duplicate keys, identical-row joins, rejected-row visibility, and expected role count; run `uv run pytest tests/test_model_comparison.py -q`; expect failures for missing module.
- [ ] **Step 2: GREEN** — implement the minimal typed join and metric aggregation.
- [ ] **Step 3: Verify/refactor** — rerun focused tests; expect PASS, then remove duplicated aggregation logic while keeping green.
- [ ] **Step 4: Generate** — run the Phase 2 generator twice; expect identical controlled-comparison artifacts.
- [ ] **Step 5: Checkpoint commit** — commit module, tests, generator, and generated evidence as `feat: add controlled phase comparison`.

### Task 2: Cut manuscript metrics over to generated evidence

**Use Cases:**
- Published acceptance proof cites the generated comparison and the old manual 14-count path is retired.

**Files:**
- Modify: `docs/latex/tables/residual_summary.tex`, `docs/latex/sections/mea_system_modeling_results.tex`, `tests/test_manuscript_claim_integrity.py`

**Interfaces:**
- Consumes: generated metrics and role counts.
- Produces: manuscript statements traceable to saved rows.

- [ ] **Step 1: RED** — add a manuscript test requiring generated values and count 15; verify it fails on current text.
- [ ] **Step 2: GREEN** — revise table and narrative from the generated summary.
- [ ] **Step 3: Verify** — run focused tests and `bash scripts/build_manuscript.sh`; expect PASS.
- [ ] **Step 4: Inspect** — render affected pages and verify tables/claims are legible and consistent.
- [ ] **Step 5: Checkpoint commit** — commit as `docs: report controlled model comparison`.

