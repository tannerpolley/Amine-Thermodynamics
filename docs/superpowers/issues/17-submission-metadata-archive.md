# Complete submission metadata, licensing, and archival records

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/17
**GitHub Milestone:** Manuscript Submission
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/15
**Source Spec:** docs/superpowers/specs/2026-07-13-submission-metadata-archive-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-submission-metadata-archive-plan.md
**Submission Sprint:** docs/superpowers/plans/2026-07-17-fluid-phase-equilibria-submission-sprint-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:release, status:done, type:manuscript
Sub-Issue Role: leaf
Executable: true
**Goal Command:** Publish GitHub release `v1.0.0` from the verified merged commit and confirm that its URL resolves.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-submission-metadata-archive-plan.md#outcome-proof
**Intent:** Replace placeholders and ambiguous legal/release state with authoritative, mutually consistent records.
**Target Output:** Metadata ledger, front matter, declarations, MIT license, citation file, GitHub release/tag, availability text, and PDF metadata receipt.
**Owner:** Corresponding author and repository owner.
**Interface:** `docs/latex/submission_metadata.yml`, repository metadata files, and release/archive URLs.
**Cutover:** Replace instructional/placeholding language with final approved values.
**Replaced Path:** Retire “add before submission” text and generic/anomalous PDF fields.
**Acceptance Proof:** Every required field is authoritative; release/archive content matches final commit; manuscript and repository metadata agree.
**Stop Criteria:** Stop on mutable scientific state, a failed proof oracle, or inconsistent release metadata.
**Avoid:** No Zenodo deposit, DOI claim, inferred metadata, or release from an unmerged commit.

## Acceptance Criteria

- [x] Collect author-approved affiliation, corresponding-author, ORCID, funding, venue, and license values.
- [x] Validate manuscript, citation, repository, and PDF metadata for exact agreement.
- [x] Require final scientific proof and explicit approval before tag/release publication.
- [x] Publish GitHub release `v1.0.0` from the verified merged commit.
- [x] Confirm the release URL resolves and record it in the availability text.

## Authority and route

On 2026-07-27, the corresponding author approved the committed identity and
declaration values, *Fluid Phase Equilibria*, the MIT repository license, and a
GitHub-only release route. No Zenodo record or DOI will be created.

## Submission Sprint Role

The metadata decisions and final scientific proof are complete. GitHub release
`v1.0.0` was published from verified merge commit
`92a032a7de3233575233a75fb86bba0cf98b43c7` on 2026-07-27. Its manuscript PDF
asset has SHA-256
`462485922a40b9cb8988561f6f30756c49b8306c567dda39e77e9dcf54694db7`.

## Non-goals

- Infer author-owned or legal values.
- Publish from an unmerged or unverified commit.
- Create a Zenodo record or mint a DOI.

## Proof Oracle

- Metadata schema and placeholder tests.
- Built-PDF metadata inspection.
- Resolvable GitHub release URL after approved publication.
