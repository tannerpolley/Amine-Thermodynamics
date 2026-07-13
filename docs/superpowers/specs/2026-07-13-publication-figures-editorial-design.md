# Publication Figures, Tables, Layout, and Editorial Design

## Context

The manuscript PDF is technically clean but several multi-species figures and tables are too small at normal page size, the Born sensitivity discussion lacks a genuine retained-versus-alternative visual comparison, and pages 10, 13, 17, and 18 have poor composition. The narrative also needs tighter focus.

## Goals

- Make all figures/tables legible at publication size and scientifically faithful to final approved results.
- Show retained and alternative Born behavior explicitly when sensitivity is discussed.
- Repair floats, whitespace, reference/nomenclature placement, and end-matter pagination.
- Remove tangential or repetitive prose and synthesize the conclusion.

## Non-goals

- Do not change scientific results for visual convenience.
- Do not generate decorative figures without a manuscript claim.
- Do not tune layout before final comparison/regression outputs are frozen.

## Alternatives

- Scale existing graphics larger: insufficient for crowded legends and extreme dynamic ranges.
- Move everything to supplement: hides central evidence.
- Selected: redesign main-evidence figures, split trace-species context where needed, and use supplement only for secondary detail.

## Selected design

Define publication-size legibility checks, redesign crowded species plots with major/trace separation or panels, generate an actual two-alternative Born sensitivity comparison, simplify tables, and apply a final page-by-page editorial/layout pass to the fresh PDF.

## Interfaces

- Inputs: approved Phase 2 comparison and Phase 3 outputs, Matplotlib bundles, LaTeX tables/sections, journal-neutral page constraints.
- Outputs: revised figure bundles and sidecars, simplified tables, edited sections, fresh visually approved PDF.
- Parent: Manuscript Package and Release; blocked by final scientific outputs for closeout.

## Data flow

Freeze scientific inputs → redesign figures/tables → update LaTeX references/captions → edit narrative → rebuild → render all pages → inspect and iterate.

## Error handling

Fail on stale input hashes, clipped labels, unreadable print-size text, figures that do not display claimed alternatives, missing companion artifacts, or broken citations/references.

## Testing and proof

- Figure bundle and plotted-data hash checks.
- PDF build with no undefined references or overfull boxes.
- All-page visual inspection at normal reading scale.
- Editorial search for legacy/internal terminology and repeated conclusions.

## Risks

Layout is template-sensitive; preserve source clarity and record venue-specific deltas rather than hard-coding fragile fixes.

## Unresolved decisions

Journal-specific dimensions remain deferred; the design targets conservative single-column and full-width legibility.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Figure strategy | Visual manuscript audit | Redesign crowded main figures and separate trace detail when necessary. | Improves readability without hiding evidence. | No | figure maintainer |
| Sensitivity evidence | Scientific review | Plot retained and alternative Born cases explicitly. | Aligns visual evidence with narrative claims. | No | thermodynamic-model maintainer |
| Venue dimensions | Missing target journal | Use conservative journal-neutral sizing, then apply venue deltas. | Avoids premature template coupling. | Yes | manuscript maintainer |

