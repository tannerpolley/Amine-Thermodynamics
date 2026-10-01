# Manuscript version 1: submission readiness

Scientific scope (owner decisions, #68, 2026-09-30): a scoped predictive paper on the SSM+DS
record `9055458d…cb241` for 30 wt% MEA at 40–80 °C. The July 2026 authorization for release
`v1.0.0` and its empty human-gate list belong to the retired fixed-parameter manuscript and do not
certify this version.

## Checks at the final build

- [x] Writer A's methods, equation-of-state, nomenclature and parameter tables are integrated
      (build of 2026-09-30, PDF SHA-256 `8664a9bd…ecd5a193e`). The pressure caption and Table 6
      describe the canonical loading correction themselves; the methods do not mention it.
- [x] `references.bib` (31 entries) is regenerated with `python scripts/cited_bibliography.py > references.bib`
      and the command exits with no missing key.
- [x] `latexmk` build into `builds/` completes with no undefined citation or reference, no
      duplicate label, no overfull box and no missing figure; rerun at the tagged commit.
- [ ] Every number in the abstract, Results, conclusion, highlights and cover letter matches the
      correctly rounded retained value named in `source_log.md`, with its group and count.
- [ ] The four figure files match the SHA-256 values in `source_log.md`.
- [x] Every page has been inspected at intended size, in color and in grayscale; the PDF metadata
      shows the title, author, subject and keywords. Repeat after the review corrections.
- [ ] Independent evidence review (cse:review), final prose inspection (cse:prose) and PDF check
      (cse:latex) are complete, and the required corrections are made.
- [ ] Source commit, `manuscript-v1.pdf` SHA-256 and `manuscript-v1-source.zip` SHA-256 are
      recorded in `submission_metadata.yml`; the source ZIP builds in an isolated directory.
- [ ] The annotated `manuscript-v1` tag is created at the reviewed commit, after the loading-fix
      merge.

## Owner-only steps

- Generative-AI declaration confirmed by the author on 2026-10-01 (names OpenAI Codex and Claude).
- Make `tannerpolley/Amine-Thermodynamics` public before submitting. The data-availability
  statement cites it and the `manuscript-v1` tag.
- Check the current Fluid Phase Equilibria Guide for Authors for required fields (graphical
  abstract, suggested reviewers, file types). The design inspection received HTTP 403, so these
  requirements were not verified.
- Upload the PDF, the source ZIP, `submission/highlights.txt` and the edited
  `submission/cover_letter.md` in Editorial Manager. Do not upload
  `docs/submission/fluid_phase_equilibria/submission_metadata.yml`, which is the legacy record.
