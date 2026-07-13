# Complete submission metadata, licensing, and archival records

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/17
**GitHub Milestone:** Manuscript Submission
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/15
**Source Spec:** docs/superpowers/specs/2026-07-13-submission-metadata-archive-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-submission-metadata-archive-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:release, priority:submission-blocker, status:hitl, type:manuscript
Sub-Issue Role: leaf
Executable: true
**Goal Command:** HITL: collect authoritative metadata, then publish only with explicit owner approval.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-submission-metadata-archive-plan.md#outcome-proof
**Intent:** Replace placeholders and ambiguous legal/release state with authoritative, mutually consistent records.
**Target Output:** Metadata ledger, front matter, declarations, license, citation file, release/tag, archive DOI, availability text, and PDF metadata receipt.
**Owner:** Corresponding author and repository owner.
**Interface:** `docs/latex/submission_metadata.yml`, repository metadata files, and release/archive URLs.
**Cutover:** Replace instructional/placeholding language with final approved values.
**Replaced Path:** Retire “add before submission” text and generic/anomalous PDF fields.
**Acceptance Proof:** Every required field is authoritative; release/archive content matches final commit; manuscript and repository metadata agree.
**Stop Criteria:** Stop on missing author/legal decision, mutable scientific state, unresolved DOI, or inconsistent license.
**Avoid:** No inferred ORCID, funding, license, or premature irreversible publication.

## Acceptance Criteria

- [ ] Collect author-approved affiliation, corresponding-author, ORCID, funding, venue, and license values.
- [ ] Validate manuscript, citation, repository, and PDF metadata for exact agreement.
- [ ] Require final scientific proof and explicit approval before tag/release/archive publication.
- [ ] Record immutable release and archive identifiers in availability text.

## Blocked by

- Human metadata and legal decisions.
- Final scientific closeout before irreversible release/archive publication.

## Non-goals

- Infer author-owned or legal values.
- Publish a release, tag, or archive record without explicit approval.

## Proof Oracle

- Metadata schema and placeholder tests.
- Built-PDF metadata inspection.
- Resolvable final release/archive identifiers after approved publication.
