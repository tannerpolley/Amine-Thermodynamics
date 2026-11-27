# Writer handoff: S1 structural cut (#430)

**Issue and decisions.** Stage S1 of the [#430 plan amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/430#issuecomment-7206880920), applying the [owner's scope decisions](https://github.com/tannerpolley/Amine-Thermodynamics/issues/429#issuecomment-7206880701) and the part-2 and part-3 actions of the [scope assessment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/429#issuecomment-7206791380). Branch `issue-430-rebuild`, base `181e42f62`. Text only; no code, record or generator was changed.

**What changed.**
- Main text: one parameter set per amine. The comparison-fit column and rows, the section on shared interactions and calibration choices, the MEA restrictions section, the stability-penalty equation, the starts paragraph, the Hong sentences and four of the five limitation paragraphs are gone. Phase stability is three paragraphs. The abstract and conclusions state the result and carry no numerical method.
- Supplement: the Hong section, start tables, MDEA outcome table, split certificate, derivative checks, system-pressure and weighting comparisons, restrictions, Kim alternatives and expanded-MEA-fit tables are out. One ablation table and one paragraph with a figure on the first AMP fit remain.
- `STYLE.md`: a pointer row for the scope decision and the provenance clause on the numerical-detail row.

**Evidence and verification.** Both PDFs build (main 26 pages, was 32; supplement 32, was 64). The only LaTeX errors are six new `\res` names. The corrected claims (DEA splits at six states; MEA none at 321 of 321) rest on the phase diagnosis of commit `046e7462f`, which I read but did not rerun. Its records were retired from the tree at `75fd0501a`.

**What S2 must do.**
1. Bind the six new names: `dea-split-states-abstract`, `-results`, `-conclusion`, `-supplement` (six; `analyses/fixed_reaction_reference/diagnosis-phase/assemblages.json.gz` at `046e7462f`), `mdea-zheng-row-6-bubble-pressure` (38.1 MPa; `diagnosis-starts/zheng-row-6.json` at the same commit), `mdea-restricted-grid-states` (no S record; produced with the restricted grid).
2. Remove the 851 bindings and 175 number-collision entries that the cut text no longer uses, and add collision entries for 27 typed conditions. `uv run --locked python -m analyses.amines.displays --check` lists all of them.
3. Make nine generators match their hand-edited tables: `amine-summary`, `published-models`, `mea_data`, `supplement_mea_comparison`, `supplement-temperature-bands`, `supplement-amp-ranges`, `supplement-transfer-bounds`, `supplement-liquid-splits`, `supplement-shared-interaction-sensitivity`.
4. Build four new displays, named in comments beside their placeholders in `sections/transfer_results.tex`: `tables/transfer-deviations.tex`, `mdea-isotherms.pdf`, `amp-isotherms.pdf`, `mdea-speciation.pdf`.
5. Redraw three figures: `mdea-gap-onset.pdf` (one line, the MDEA model), `amp-splits.pdf` (one marker class), `salt-osmotic-residuals.pdf` (no panel of excluded rows).

**Open questions.**
- The supplement is 32 pages, not about 25. The rest is equations, parameters, reference values and figures that standing decisions place there.
- The MDEA rows of the ablation table come from a fit that stopped at its iteration limit (assessment row 5, undecided). It must be continued in M5 before those numbers are final.
- The main text says the restricted MDEA grid has no detected instability. No S record shows this yet; M4 produces it.
- The methods name no optimizer algorithm, because no retained record or earlier text names one.
- Two reused bindings still have "unresolved" in their names (`dea-unresolved-weiland-loading-results`, `dea-unresolved-lawson-pressure-results`); S2 should rename them.

**Next stage's first action.** Run the displays check, then prune `displays.py` to the names the sources still use.
