# Manuscript version 1: submission readiness

Scientific scope (owner decisions, #68, 2026-10-01 and 2026-10-02): one snapshot of the
corrected141 final rerun (#154, promoted at `79256a0`), with the SSM+DS parameter set F1
`ae92bac5…f1aa` for 30 wt% MEA. The July 2026 authorization for release
`v1.0.0` and its empty human-gate list belong to the retired fixed-parameter manuscript and do not
certify this version.

## Checks at the final build

- [x] Writer A's methods, equation-of-state, nomenclature and parameter tables are integrated
      (build of 2026-09-30, PDF SHA-256 `8664a9bd…ecd5a193e`). Since the 2026-10-01 restructure,
      the methods state once that each calculated feed carries the measured loading; the captions carry no loading note.
- [x] `references.bib` (31 entries) is regenerated with `python scripts/cited_bibliography.py > references.bib`
      and the command exits with no missing key.
- [x] `latexmk` build into `builds/` completes with no undefined citation or reference, no
      duplicate label, no overfull box and no missing figure; rerun at the tagged commit.
- [ ] Every number in the abstract, Results, conclusion, highlights and cover letter matches the
      correctly rounded retained value named in `source_log.md`, with its group and count.
- [x] The four figure files match the SHA-256 values in `source_log.md` (rendered by
      `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py`).
- [x] Every page has been inspected at intended size, in color and in grayscale; the PDF metadata
      shows the title, author, subject and keywords. Repeat after the review corrections.
- [ ] Independent evidence review (cse:review), final prose inspection (cse:prose) and PDF check
      (cse:latex) are complete, and the required corrections are made.
- [ ] Source commit, `manuscript-v1.pdf` SHA-256 and `manuscript-v1-source.zip` SHA-256 are
      recorded in `submission_metadata.yml`; the source ZIP builds in an isolated directory.
- [ ] The annotated `manuscript-v1` tag is created at the reviewed commit, after the loading-fix
      merge.

## Resolved evidence links

- Historical heat-capacity rows are public at an immutable link: https://github.com/tannerpolley/MEA-Absorption-Column/blob/ccedbd2cecf82c843908a406387c180cd31e7f93/analyses/physical_acceptance_149/results/physical-checks.csv (rows 6–8; repository public, commit on main).

## Owner-only steps

- Generative-AI declaration confirmed by the author on 2026-10-01 (names OpenAI Codex and Claude).
- Make `tannerpolley/Amine-Thermodynamics` public when the preprint is posted.
  The data-availability statement promises the materials at `manuscript-v1` at posting.
- Publish the draft GitHub release for `manuscript-v1`, including the manuscript, supplement,
  and the `epcsaft` wheels `28181e72…` and `9e6a76cf…`, when the repository is public and
  the preprint is posted.
- Post to ChemRxiv and complete its attestations.
- For Fluid Phase Equilibria, report any AI contribution to research methods or figure
  generation in Methods with tool and version details, as Elsevier requests; state only actual
  use.
- Check the current Fluid Phase Equilibria Guide for Authors for required fields (graphical
  abstract, suggested reviewers, file types). The design inspection received HTTP 403, so these
  requirements were not verified.
- Upload the PDF, the source ZIP, `submission/highlights.txt` and the edited
  `submission/cover_letter.md` in Editorial Manager. Do not upload
  `docs/submission/fluid_phase_equilibria/submission_metadata.yml`, which is the legacy record.
