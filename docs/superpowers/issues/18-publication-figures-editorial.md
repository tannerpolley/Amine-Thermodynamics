# Complete publication figures, tables, layout, and editorial polish

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/18
**GitHub Milestone:** Manuscript Submission
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/15
**Source Spec:** docs/superpowers/specs/2026-07-13-publication-figures-editorial-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-publication-figures-editorial-plan.md
**Submission Sprint:** docs/superpowers/plans/2026-07-17-fluid-phase-equilibria-submission-sprint-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:editorial, priority:submission-blocker, status:blocked, type:manuscript
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Complete evidence-faithful publication visuals, layout, and editorial polish.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-publication-figures-editorial-plan.md#outcome-proof
**Intent:** Make every retained visual and manuscript page legible, evidence-faithful, and publication-ready.
**Target Output:** Revised renderers/bundles, tables, captions/sections, fresh PDF, and visual-review receipt.
**Owner:** Figure and manuscript maintainers.
**Interface:** Figure render scripts, `.mpl.yaml` bundles, LaTeX sections, and final PDF.
**Cutover:** Manuscript references only final approved figure/table bundles.
**Replaced Path:** Retire crowded single-panel/one-alternative figures and fragile layout workarounds.
**Acceptance Proof:** No claimed alternative is absent; normal-scale text is legible; no clipping, undefined references, or overfull boxes; all pages reviewed.
**Stop Criteria:** Stop on stale scientific input, missing companion, unreadable output, or unresolved claim/visual mismatch.
**Avoid:** No decorative plot, hidden trace data, or result-changing smoothing.

## Acceptance Criteria

- [ ] Redesign sensitivity and comparison visuals from immutable final data with complete companion bundles.
- [ ] Make all figure/table text legible at normal manuscript scale.
- [ ] Tighten captions, narrative, float placement, and end-matter composition.
- [ ] Render and inspect every page for clipping, unresolved references, and claim/visual mismatch.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/14

## Submission Sprint Role

Final scientific visuals begin only after Tuesday's #14 receipt. Figure, table, caption, and narrative edits must consume the immutable promoted candidate and reserved-validation outputs; no provisional or zero-evaluation artifact may survive the Wednesday manuscript freeze.

## Non-goals

- Smooth or alter scientific results to improve appearance.
- Add decorative figures without a manuscript claim role.

## Proof Oracle

- Deterministic figure bundle tests and repeat rendering.
- Clean LaTeX build log.
- All-page visual-review receipt.
