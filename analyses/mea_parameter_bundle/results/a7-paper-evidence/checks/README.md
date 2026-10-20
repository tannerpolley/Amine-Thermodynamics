# Adoption checks and execution decisions

The default-path replay returns 153 finite available predictions within
8.392969848994369e-16 relative difference. Its inputs, comparisons, diagnostics,
output and whole-command timing are in `../default-replay/`.

The final reduction returns 307 objective rows at cost 148.90525398237165,
462 state-target rows and rank 10 for the ten free scientific coordinates.
The retained covariance owner gives variance factor 1.0027289830464732 and
finite standard errors/correlations. The first reduction's timing and output
are retained as `reduction-r1-*`; the final reduction uses the campaign cutoff
on the unnormalized scientific-coordinate free Jacobian. Both calls are charged.

`tests-output.txt`: 76 tests and 17 subtests pass. The A7 interpreter lacks
pytest; `uv-sync-output.txt` records the authorized worktree environment setup.
`compile-output.txt` records a successful `python -m py_compile` of every
changed Python file. `final-file-checks.json` verifies source/output hashes,
byte-identical copies, campaign preservation and no tracked manuscript change.

`notebook-validate-output.txt` reports `valid`. `notebook-render-output.txt`
retains the full-site presentation failure: the historical
`reactive_epcsaft_parameter_evidence/results/readiness/regression_readiness_summary.json`
checksum differs from its retained list. The orchestrator identified that
mismatch as pre-existing on main since aa20f49 (2026-10-18), current 118a22a2…
versus expected 802dae17…, and authorized the direct MEA notebook render through
the native question tool. That historical analysis remains unchanged.

`notebook-direct-render-output.txt` records the successful authorized fallback.
A second successful render with `--embed-resources` produces a standalone HTML
for inspection through T3's local-file preview; its output is retained in
`notebook-standalone-render-output.txt`. The final HTML contains 16 coordinate
rows and eight loaded figures, with no page overflow at 1280 × 800. Parameter,
pressure and heat displays were visually inspected. The preview service was
not started, stopped or restarted, and no project server was launched.

One final figure-provenance edit initially had an extra closing parenthesis;
Python stopped with SyntaxError before any execution. The orchestrator clarified
that a self-introduced syntax typo is not a scientific renderer failure and
authorized its correction, compile check and rerun. Both renderers and the
direct render pass afterward. No Engine calculation resulted from that typo.

The only navigation metadata changes rename the two current-result headings
in `analyses/_cse-manuscript.json`, keeping its sidebar links consistent with
the required A7 notebook presentation and validation. Unrelated untracked
LaTeX PDFs are outside this change and must not be staged.

The final executable count against 5d5735c is 363 gross-added nonblank,
non-comment Python lines: replay 67, reduction 193, parameter renderer 61,
figure renderer 42. Tests add one line, counted separately. No executable
`.py.txt` changed. Deletions do not offset additions. The separate CSE
change-accounting report includes blank/comment additions and generated files;
the owner's 500-line ceiling uses the nonblank, non-comment count above.

This task charges 40 rounded-up compute wall-s and 38.74 CPU-s, including both
reductions and the complete repository test command. The program ledger now
charges 18,333 wall-s / 131,659.96 CPU-s, leaving 3,267 wall-s / 68,340.04 CPU-s.
No missing-quantity allowance was used. No fit, source-checkout import, campaign
change, historical-output relabeling, strict certification, absorber package,
manuscript change or remote write was performed. Independent delivered review
and integration remain with the orchestrator.

Git whitespace reporting recognizes the copied CSV CRLF endings as trailing
whitespace. Those source bytes are preserved intentionally. Raw Quarto output
also retains its original whitespace. Source and authored prose diffs are clean.
The CSE accounting report includes nine unrelated untracked LaTeX PDFs in its
other/binary category; they are excluded from the commit. Retained numerical
JSON/CSV and plots are also in that report’s other category, with no runtime
code hidden there. Its executable additions including blanks/comments are 390.
