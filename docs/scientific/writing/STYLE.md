# Scientific writing decisions

## Part I aqueous MEA thermodynamics
Sources: `docs/scientific/latex/main.tex`; `docs/scientific/latex/supplement.tex`; `docs/scientific/latex/figures/generated/`.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Table 1 coefficients | Preserve the existing nine-significant-figure display; state that rule in the caption. Do not print full-precision digits. | Owner's issue 347 visual fix-round-1 instructions, 2026-11-16, A4: “keep the existing nine-significant-figure display” |
| Parameter-set names | Use descriptive physical restrictions in reader-facing text, tables and figures; no internal F-codes. | Owner's 2026-11-16 visual-pass addendum: “Take internal parameter-set names out of Part I.” Exact names for this revision are recorded in `../latex/source_log.md`. |
| Part II and shared inputs | Do not edit Part II, `chemistry_macros.tex` or `.bib` files during this pass. | Owner's 2026-11-16 visual fix-round-1 instructions, D |

No other project-wide standing editorial directions have been recorded here.
