# AMP source preparation, issue #229

This directory retains public source transcriptions and bounded source
assessments. It contains no Engine results, parameter adoption or private
CESAR-1 observations. Existing public #227 scoping records supplied citation
leads. The private repository was used only to list filenames; none of its
rows, code or parameters was copied or executed.

- [Hamborg](hamborg-table-16.md): 24 source runs, units, basis, uncertainty,
  correlation reconstruction and per-run residuals.
- [Pure AMP](pure-amp-pcsaft.md): two agreeing published PC-SAFT parameter
  tables; remaining convention check and unexecuted reproduction definition.
- [Carbamate](carbamate-law.md): supported species, unresolved thermodynamic
  law/representation, unavailable Ciftja 2014 full text.
- [Pressure campaigns](partial-pressure-campaigns.md): candidates and whole-
  campaign Kundu recommendation, 51 public transcribed observations.
- `pdf-identities.json`: current Zotero PDF keys and SHA-256 hashes. Full papers
  stay in Zotero; no literature shelf or bibliography export was written.

The research and Zotero skills were applied. Mathpix was not used: the PDFs
needed for exact tables have usable text, and the unavailable Ciftja PDF cannot
be converted. The worktree has no local literature shelf; the main-checkout
shelf index was read-only, followed by the current Zotero source files.
Companion doctor found the live Zotero service readable, but reported unrelated
missing retained evidence records, so its generated summaries were not used
as support for these tables.

Reproduce the algebraic Hamborg check without resolving the Engine wheel:

```bash
uv run --no-project --with numpy python analyses/amp_pz_scoping/sources/check-hamborg.py
```

The project-local `uv run` could not resolve its absent pinned wheel in this
worktree. This isolated source-table calculation imports no Engine and changes
no repository dependency declaration. It does not authorize numerical fitting.
Numerical Build remains blocked for the reasons in the updated design draft.
