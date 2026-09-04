# Invalid exploratory run — do not use for model selection

2026-09-03: The driver incorrectly used state-packet R4/R5 correlation origins
instead of the selected parameter bundle. R4 `(a, b_k)` was `(2.151, -1545.3)`
instead of `(3.3515778177997895, -1895.3)`; R5 `a_k` was `2677.91` instead of
`2597.91`. The EOS wheel and non-reaction parameters were correctly pinned,
but that does not make this a selected-bundle replay.

All screen, SVD, candidate, and partial-validation numbers in this directory
are invalid for the requested study. They are retained only as failure evidence.
No parameters were promoted. The selected bundle and notebook were not changed.
The corrected driver binds reaction origins to the selected bundle and includes
them in its cache validation and runnable self-check.
