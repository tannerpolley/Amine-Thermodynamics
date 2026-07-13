# Submission Metadata, Licensing, and Archive Design

## Context

The current manuscript lacks complete affiliation/corresponding-author metadata, ORCID/funding decisions, a final license, release/tag, archival DOI, citation metadata, and final data/code availability language. The PDF metadata also needs correction.

## Goals

- Collect and validate all author-owned front-matter and declaration fields.
- Establish repository license, versioned release, archive record/DOI, citation metadata, and final availability links.
- Produce clean PDF title/author/subject/keywords metadata and remove internal pre-submission instructions.

## Non-goals

- Do not invent personal, funding, legal, or journal information.
- Do not mint a release or DOI before scientific artifacts are final.
- Do not choose a license without repository-owner approval.

## Alternatives

- Leave placeholders until upload: unacceptable and easy to miss.
- Infer common defaults: unsafe for legal and author metadata.
- Selected: explicit HITL metadata ledger plus machine-checkable release/archive evidence.

## Selected design

Maintain a submission-metadata ledger distinguishing required values, author decisions, and machine-derived release fields. Once author inputs and final artifacts exist, create the approved license/release/archive/citation files and update manuscript metadata atomically.

## Interfaces

- Inputs: author-provided identity/declarations, selected venue, final commit/tag, repository release, archive provider.
- Outputs: completed front matter, license, citation metadata, release URL/tag, DOI/archive record, availability statement, PDF metadata receipt.
- Parent: Manuscript Package and Release; status is HITL until author fields are supplied.

## Data flow

Collect author decisions → validate completeness → freeze final commit → publish approved release/archive → update manuscript and citation metadata → verify resolved links and PDF fields.

## Error handling

Block on missing author/legal decisions, unpublished or mutable release references, unresolved DOI, license mismatch, malformed ORCID, or placeholder/instructional wording.

## Testing and proof

- Metadata schema validation and placeholder scan.
- Resolve repository release and archive links.
- Inspect PDF author/subject/keywords fields.
- Verify license and citation files match manuscript availability language.

## Risks

External archive publication is irreversible and must remain a separate approved mutation after scientific closeout.

## Unresolved decisions

Affiliation, corresponding-author format, ORCID, funding statement, target venue, license, and archive provider remain explicit corresponding-author/repository-owner decisions.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Metadata ownership | Submission audit | Require explicit author input; infer nothing personal or legal. | Prevents fabricated declarations. | No | corresponding author |
| Release timing | Reproducibility policy | Publish release/archive only after scientific artifacts are final. | Keeps DOI content immutable and correct. | No | repository owner |
| Author and legal values | Missing external decisions | Collect affiliation, ORCID, funding, venue, license, and archive provider at execution. | Blocks final closeout until supplied. | Yes | repository owner |

