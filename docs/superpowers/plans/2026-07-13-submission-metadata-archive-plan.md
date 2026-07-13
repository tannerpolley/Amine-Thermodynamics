# Submission Metadata, Licensing, and Archive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete author metadata, legal/release records, archival references, citation metadata, availability language, and PDF metadata without inventing author-owned values.

**Architecture:** A validated metadata ledger separates human inputs from machine-derived release/archive fields and gates irreversible publication until scientific closeout.

**Tech Stack:** YAML/JSON, LaTeX, Git, GitHub Releases, archive provider, PDF metadata tools, pytest/Bash.

## Global Constraints

- Human/legal values require explicit owner input.
- Release/archive publication occurs only from final scientific commit.
- All links and identifiers must resolve before closeout.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-submission-metadata-archive-design.md`.

## Outcome Proof

**Intent:** Remove front-matter and archival blockers with traceable authority.
**Current Behavior:** Affiliation/funding/ORCID/license/release/DOI are incomplete and availability text contains an internal instruction.
**Expected Outcome:** Final manuscript/repository metadata are complete, consistent, resolvable, and author-approved.
**Target Output:** Metadata ledger, front matter, declarations, license, citation file, release/tag, archive DOI, availability text, PDF metadata receipt.
**Owner:** Corresponding author and repository owner.
**Interface:** `docs/latex/submission_metadata.yml`, repository metadata files, and release/archive URLs.
**Cutover:** Replace instructional/placeholding language with final approved values.
**Replaced Path:** Retire “add before submission” text and generic/anomalous PDF fields.
**Evidence:** Ledger validation, link checks, release/archive receipts, PDF metadata inspection.
**Acceptance Proof:** Every required field is authoritative; release/archive content matches final commit; manuscript and repository metadata agree.
**Stop Criteria:** Stop on missing author/legal decision, mutable scientific state, unresolved DOI, or inconsistent license.
**Avoid:** No inferred ORCID/funding/license or premature irreversible publication.
**Risk:** Archive publication is external and difficult to reverse.

## Implementation Boundaries

**Files To Create:** submission metadata ledger, `LICENSE`, `CITATION.cff`, release/archive receipt.
**Files To Modify:** LaTeX front matter, declarations, availability section, README, build metadata.
**Files To Avoid:** Scientific results and external records before approval.
**Source Of Truth:** Author-approved ledger and final commit/tag.
**Read Path:** Human inputs and final Git state to metadata/release package.
**Write Path:** Ledger to repository/manuscript, then approved release/archive APIs.
**Integration Points:** manuscript build, GitHub release, archive provider, PDF inspection.
**Migration Or Cutover:** Validate inputs locally, freeze scientific commit, publish approved records, then update links atomically.
**Replaced Path Handling:** Remove all placeholders/instructions; retain no fake defaults.
**Acceptance Proof Gate:** Human approvals and machine link/PDF checks both pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Personal/legal data | Approved spec | Require explicit owner values. | Prevents fabrication. | No | corresponding author |
| Exact values | Pending owner input | Collect at execution gate. | Keeps issue HITL. | Yes | repository owner |

## Test Complete and Metrics

- No placeholder/instruction strings remain.
- PDF metadata contains approved author, subject, and keywords.
- License, citation, release, and archive identifiers resolve and agree.

### Task 1: Collect and validate metadata locally

**Use Cases:**
- Acceptance proof identifies missing authority and the placeholder old path is displaced only after cutover.

**Files:**
- Create: `docs/latex/submission_metadata.yml`, metadata tests.
- Modify: front matter and declarations after approval.

**Interfaces:**
- Consumes: author-approved values.
- Produces: complete validated ledger.

- [ ] **Step 1: RED** — add schema/placeholder tests and run them against current state; expect failures naming missing fields.
- [ ] **Step 2: HITL** — collect affiliation, corresponding-author format, ORCID, funding, venue, license, and archive provider.
- [ ] **Step 3: GREEN** — populate ledger and revise local metadata/declarations.
- [ ] **Step 4: Verify** — run tests and inspect built PDF metadata; expect PASS.
- [ ] **Step 5: Checkpoint commit** — commit as `docs: complete submission metadata`.

### Task 2: Publish final release and archive

**Use Cases:**
- External acceptance evidence resolves to the final commit and the mutable pre-release path is retired.

**Files:**
- Create/modify: `LICENSE`, `CITATION.cff`, release/archive receipt, availability section.

**Interfaces:**
- Consumes: approved final commit and metadata ledger.
- Produces: tag, release URL, DOI/archive record, final availability statement.

- [ ] **Step 1: Verify preconditions** — require clean final scientific proof and owner approval.
- [ ] **Step 2: Publish** — create approved tag/release and archive record; record immutable identifiers.
- [ ] **Step 3: GREEN** — replace availability instructions with final links/license.
- [ ] **Step 4: Verify** — resolve links, rebuild PDF, and compare metadata.
- [ ] **Step 5: Checkpoint commit** — commit receipts and final wording as `docs: publish archival metadata`.

