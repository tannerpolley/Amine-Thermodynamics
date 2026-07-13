# Computational Methods and Reproducibility Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and publish a testable inventory of every executed numerical method and reproducibility setting required by the manuscript.

**Architecture:** A canonical JSON method inventory reads declared runtime/config sources; manuscript text and consistency tests consume its stable fields.

**Tech Stack:** Python 3.13, JSON, pytest, `uv`, LaTeX, Bash.

## Global Constraints

- Describe executed algorithms only.
- Trace every critical value to code/config or a generated receipt.
- Preserve package commit/version and final integration proof.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-computational-methods-reproducibility-design.md`.

## Outcome Proof

**Intent:** Make the computational thermodynamics method reproducible from the paper and repository.
**Current Behavior:** The methods subsection omits solver, continuation, tolerance, failure, permittivity, runtime, and package details.
**Expected Outcome:** One generated inventory and revised text fully describe the executed method.
**Target Output:** Method inventory, generator/test, revised sections/table, commands, and fresh PDF.
**Owner:** Reproducibility maintainer.
**Interface:** `build_method_inventory() -> dict` and `docs/latex/generated/method_inventory.json`.
**Cutover:** Manuscript values derive from the inventory instead of manual prose constants.
**Replaced Path:** Retire undocumented defaults and untested duplicated settings.
**Evidence:** RED/GREEN consistency tests, inventory diff, final integration receipt, and PDF build.
**Acceptance Proof:** Inventory covers every required field and manuscript/runtime values match exactly.
**Stop Criteria:** Stop on conflicting sources, hidden defaults, unpinned package state, or missing final Phase 3 algorithm.
**Avoid:** No prospective method presented as executed or exhaustive settings dumped without explanation.
**Risk:** Final Phase 3 changes can stale the inventory; bind it to hashes.

## Implementation Boundaries

**Files To Create:** `src/MEA/common/method_inventory.py`, `scripts/build_method_inventory.py`, `tests/test_method_inventory.py`, generated inventory.
**Files To Modify:** methods/theory sections, source log, tooling tests, manuscript build.
**Files To Avoid:** Solver algorithms and upstream package code.
**Source Of Truth:** Runtime/config declarations and final integration receipt.
**Read Path:** Code/config/receipts to method inventory.
**Write Path:** Generator to JSON/table to LaTeX/PDF.
**Integration Points:** manuscript build/freshness and final integration checker.
**Migration Or Cutover:** Add failing coverage tests, generate inventory, then revise prose.
**Replaced Path Handling:** Remove duplicated hard-coded method values from manuscript sources.
**Acceptance Proof Gate:** Focused tests, final integration, and fresh PDF pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Inventory owner | Approved spec | Generate from executable declarations. | Prevents drift. | No | reproducibility maintainer |

## Test Complete and Metrics

- Required method fields have source paths and values.
- Manuscript consistency tests pass.
- Clean build records pinned ePC-SAFT and runtime commands.

### Task 1: Build the method inventory TDD-first

**Use Cases:**
- Acceptance evidence exposes every setting and the undocumented old path is retired during cutover.

**Files:**
- Create: method inventory module/script/test and generated JSON.
- Modify: build/freshness integration.

**Interfaces:**
- Consumes: runtime/config values.
- Produces: stable inventory schema.

- [ ] **Step 1: RED** — add tests requiring algorithms, initialization, continuation, limits, damping, tolerances, failures, bubble-pressure, permittivity, version, and runtime; expect failures.
- [ ] **Step 2: GREEN** — implement minimal inventory collection with source locators and hashes.
- [ ] **Step 3: Verify/refactor** — run focused tests twice and ensure deterministic JSON.
- [ ] **Step 4: Checkpoint commit** — commit as `feat: generate computational method inventory`.

### Task 2: Revise and verify manuscript methods

**Use Cases:**
- Published proof consumes the inventory and displaced manual values cannot drift.

**Files:**
- Modify: `docs/latex/sections/data_methods.tex`, EOS/method sections, source log, manuscript tests.

**Interfaces:**
- Consumes: method inventory.
- Produces: complete methods narrative and table.

- [ ] **Step 1: RED** — add manuscript tests for inventory-backed values; verify current prose fails coverage.
- [ ] **Step 2: GREEN** — revise sections and generated table.
- [ ] **Step 3: Verify** — run focused tests, final integration, and manuscript build; expect PASS.
- [ ] **Step 4: Checkpoint commit** — commit as `docs: document computational method`.

