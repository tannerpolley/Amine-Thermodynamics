# Publication Figures, Tables, Layout, and Editorial Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver publication-legible figures/tables, genuine sensitivity visuals, balanced pages, and a tighter scientific narrative using final approved outputs.

**Architecture:** Figure-owned render scripts consume immutable final data; LaTeX integrates validated bundles, then an all-page visual/editorial gate closes the work.

**Tech Stack:** Matplotlib, pandas, MPLGallery sidecars, LaTeX/latexmk, PDF rendering, pytest, Bash.

## Global Constraints

- Final scientific hashes precede visual cutover.
- Every figure has plotted data plus PNG/SVG/PDF/sidecar companions.
- Visual redesign cannot hide failures or alter values.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-publication-figures-editorial-design.md`.
- Visual audit: 18-page current PDF with legibility and pagination findings.

## Outcome Proof

**Intent:** Make the final scientific evidence readable and editorially coherent at publication scale.
**Current Behavior:** Crowded plots/tables, incomplete sensitivity comparison, excess whitespace, and repetitive/tangential text remain.
**Expected Outcome:** Final figures/tables are legible, claims match visuals, pages compose well, and narrative is concise.
**Target Output:** Revised renderers/bundles, tables, captions/sections, fresh PDF, and visual-review receipt.
**Owner:** Figure and manuscript maintainers.
**Interface:** Figure render scripts, `.mpl.yaml` bundles, LaTeX sections, final PDF.
**Cutover:** Manuscript references only final approved figure/table bundles.
**Replaced Path:** Retire crowded single-panel/one-alternative figures and fragile layout workarounds.
**Evidence:** Plot-data hash checks, focused tests, PDF build logs, and page-by-page inspection.
**Acceptance Proof:** No claimed alternative is absent; normal-scale text is legible; no clipping/undefined references/overfull boxes; all pages reviewed.
**Stop Criteria:** Stop on stale scientific input, missing companion, unreadable output, or unresolved claim/visual mismatch.
**Avoid:** No decorative plot, hidden trace data, or result-changing smoothing.
**Risk:** Journal template changes may require a final dimensions-only pass.

## Implementation Boundaries

**Files To Create:** Revised final figure artifacts and visual-review receipt.
**Files To Modify:** Phase 2/3 renderers, figure sidecars, LaTeX tables/captions/sections and layout.
**Files To Avoid:** Canonical scientific result values.
**Source Of Truth:** Approved Phase 2 comparison and Phase 3 result tables.
**Read Path:** Final result tables to renderers to plotted snapshots.
**Write Path:** Figure bundles to `docs/latex/figures` and LaTeX/PDF.
**Integration Points:** MPLGallery checks, manuscript build/freshness, PDF renderer.
**Migration Or Cutover:** Add visual/contract tests, regenerate bundles, then update manuscript references.
**Replaced Path Handling:** Remove superseded active bundles and references; do not keep duplicate aliases.
**Acceptance Proof Gate:** Deterministic bundles, clean build, and all-page visual review pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Plot strategy | Approved spec | Major/trace separation and true alternative comparison. | Improves legibility and honesty. | No | figure maintainer |

## Test Complete and Metrics

- Every active figure has same-stem data/PDF/PNG/SVG/sidecar proof.
- Captions and visuals agree on series/alternatives.
- Fresh PDF has no clipping, undefined references, or overfull boxes and all pages are reviewed.

### Task 1: Redesign and verify scientific visuals

**Use Cases:**
- Target-perspective visual evidence is readable and the displaced crowded/one-alternative path is retired.

**Files:**
- Modify: affected Phase 2/3 render scripts and figure bundles.
- Test: figure bundle and manuscript-reference tests.

**Interfaces:**
- Consumes: immutable final result tables.
- Produces: deterministic publication bundles.

- [ ] **Step 1: RED** — add tests for required alternative series, companions, source hashes, and minimum style sizes; expect current sensitivity failure.
- [ ] **Step 2: GREEN** — redesign major/trace panels and retained-versus-alternative sensitivity output.
- [ ] **Step 3: Verify/refactor** — render twice, run bundle tests, and require no diff.
- [ ] **Step 4: Checkpoint commit** — commit as `fig: redesign publication evidence`.

### Task 2: Reflow and edit the manuscript

**Use Cases:**
- Editorial acceptance proof shows migration from sparse pages and repetitive/tangential prose.

**Files:**
- Modify: affected LaTeX tables, captions, results, introduction, conclusion, references/nomenclature layout.

**Interfaces:**
- Consumes: final figure bundles and approved metrics.
- Produces: visually reviewed PDF.

- [ ] **Step 1: RED** — lock mandatory captions/references and submission-language searches.
- [ ] **Step 2: GREEN** — simplify tables, tighten prose, and repair float/end-matter composition.
- [ ] **Step 3: Verify** — build, render all pages, inspect normal-scale legibility and composition.
- [ ] **Step 4: Checkpoint commit** — commit as `docs: polish manuscript presentation`.

