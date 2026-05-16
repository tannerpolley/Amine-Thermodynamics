# Manuscript Revision Summary

Date: 2026-05-15 local

## Files Edited

- `docs/latex/main.tex`
- `docs/latex/sections/introduction.tex`
- `docs/latex/sections/epc_saft_equation_of_state.tex`
- `docs/latex/sections/data_methods.tex`
- `docs/latex/sections/mea_system_modeling_results.tex`
- `docs/latex/sections/conclusion.tex`
- `docs/latex/sections/data_code_availability.tex`
- `docs/latex/sections/nomenclature.tex`
- `docs/latex/tables/regression_bounds.tex`
- `docs/roadmaps/manuscript_revision_blockers.md`
- `docs/roadmaps/manuscript_revision_summary.md`

## Follow-Up Self-Review Fixes

- Corrected the Theory, Data and Methods, and Results subsection names/order to match the grounding-gate roadmap more closely.
- Reduced repeated pressure-optimization limitation wording while preserving the required fixed-activity-set and process-design boundaries.
- Converted the Phase 2 pressure and trace-carbonate sensitivity graphics from forced inline caption blocks to regular figures after the self-review build exposed an overfull page.
- Removed an extra blank line at end of file in the Theory source caught by `git diff --check`.

## Claims Removed or Softened

- Reframed the manuscript title, abstract, results opener, and conclusions as a residual-qualified activity-based ePC-SAFT evaluation.
- Removed final-regression, pressure-optimized, and process-design pressure-correlation posture from the manuscript body.
- Limited Phase 3 language to one Methods boundary statement and one Conclusion boundary statement.
- Removed unsupported archive/release wording from Data and Code Availability.
- Avoided adding unverified condition ranges or source-by-source residual claims.

## Terms Replaced

- `solves all ... records` -> `converged for all ... records`
- `accepted major-species residuals` -> `major-species median absolute residuals`
- `accepted pressure metric` -> `pressure residual`
- `accepted direct-positive speciation metrics` -> `nonzero measured-target speciation metrics`
- `accepted high-temperature rows` -> `high-temperature rows with smaller residuals`
- `direct-positive targets` -> `nonzero measured targets`
- `reported-zero rows` -> `measurements reported as zero and treated as upper-bound targets`
- `solver-success rows` -> `converged calculation rows`
- `Born-radius mode 3` -> `selected modified-Born convention`
- `Tier A` -> `NMR/speciation source subset`
- `\kappa_{ij}` as binary interaction parameter -> `k_{ij}`

## Validation Commands Run

- `git status --short` before editing: no output; working tree was clean.
- Required file existence check for the listed manuscript files and roadmap files.
- Self-review `git status --short`: the follow-up pass touched `introduction.tex`, `epc_saft_equation_of_state.tex`, `data_methods.tex`, `mea_system_modeling_results.tex`, and `data_code_availability.tex`.
- `Import-Csv data/reference/MEA/manifests/figure_artifact_manifest.csv | Group-Object publication_status`
- `Import-Csv data/reference/MEA/manifests/figure_artifact_file_manifest.csv | Group-Object publication_status`
- `Import-Csv data/reference/MEA/manifests/regression_artifact_manifest.csv`
- `git remote -v`
- `git tag --list`
- `Test-Path docs/latex/scripts/build_main.ps1` and build-command search; no build wrapper was found, while `.latexmkrc` and repo-local planning files support the `latexmk` command below.
- `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` from `docs/latex`
- `git diff --check`
- Restricted-term search over `docs/latex/main.tex`, `docs/latex/sections`, and `docs/latex/tables`
- Abstract word-count check: 172 words by local macro-stripped count.
- Raw DOI URL and local-path search over manuscript source.
- Manuscript figure target existence check.
- Build-log scan for undefined references, missing figures, missing citations, font/encoding warnings, overfull boxes, and underfull boxes.
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Validation Results

- Restricted-term search passed with no matches for the requested banned/restricted terms.
- Raw DOI URL and local Windows path search passed with no matches in manuscript source.
- All referenced manuscript figures exist under `docs/latex/figures`.
- Build succeeded and wrote `docs/latex/builds/main.pdf`.
- Build-log scan found one remaining underfull hbox in the abstract. No undefined references, missing citations, missing figures, font/encoding warnings, or overfull boxes were found in the final log scan.
- `git diff --check` passed after the follow-up whitespace fix.
- Cleanup hook passed: no matching leftover Codex processes under the repository root.

## Validation Skipped

- No new data generation or figure regeneration was run. The revision was constrained to existing repo-local evidence and existing figure/table artifacts.
- No web search was performed.
