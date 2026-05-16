# Codex Agent Prompt — MEA ePC-SAFT Manuscript Revision for *Next Chemical Engineering*

## How to use this prompt

Attach the companion grounding file `codex_mea_revision_grounding_gate.md` to the Codex task. Start Codex from the root of the `MEA-Thermodynamics` repository. The agent must edit the LaTeX manuscript in-place and must treat the companion grounding file as the acceptance gate.

---

## Prompt to give Codex

You are a manuscript-revision agent operating on the `MEA-Thermodynamics` repository. Apply a **Major Revision** to the LaTeX manuscript for *Next Chemical Engineering* using the attached file `codex_mea_revision_grounding_gate.md` as the controlling gate.

### Non-negotiable rule: no assumptions

Every manuscript claim must be supported by one of the following repo-local sources:

1. the current LaTeX manuscript source;
2. repo-local roadmaps and phase plans;
3. repo-local manifests;
4. repo-local processed CSV/data files;
5. repo-local source-paper Markdown files; or
6. existing figure/table artifacts.

If a fact, threshold, figure status, data range, parameter value, repository URL, release tag, archive DOI, validation result, or source split cannot be verified from repo-local evidence, **do not invent it**. Either remove the claim, write it as an explicit limitation, or record it in `docs/roadmaps/manuscript_revision_blockers.md` as blocked evidence. Do not use web search. Do not paste long source-paper text into the manuscript.

### Required scope

Revise the manuscript as a **Phase 1 + Phase 2 paper only**:

- Phase 1 = ideal/apparent Smith--Missen-style reproduction baseline.
- Phase 2 = activity-based true-species ePC-SAFT evaluation.
- Phase 3 coupled pressure/speciation regression is **not in scope**.

The final manuscript must present the work as a **residual-qualified, activity-based ePC-SAFT evaluation**, not as a finalized global regression, not as a pressure-optimized parameterization, and not as process-ready pressure prediction.

### Files to verify before editing

From the repository root, verify the existence and current contents of these files or their repo-equivalent paths:

- `docs/latex/main.tex`
- `docs/latex/sections/introduction.tex`
- `docs/latex/sections/epc_saft_equation_of_state.tex`
- `docs/latex/sections/mea_system_modeling_results.tex`
- `docs/latex/sections/conclusion.tex`
- `docs/latex/sections/data_code_availability.tex`
- `docs/latex/sections/nomenclature.tex`
- `docs/roadmaps/manuscript_artifact_plan.md`
- `docs/roadmaps/manuscript_structure_and_figures.md`
- `docs/roadmaps/mea_manuscript_phase_plan.md`
- `docs/roadmaps/submission_readiness_pr_summary.md`

If the paths differ, locate the same files by filename. If a required manuscript source file cannot be found, stop editing and write a blocker report. Do not create duplicate manuscript trees.

### First commands

1. Run `git status --short` and record the result in the final summary. Do not revert user changes.
2. Locate the roadmaps, manifests, and LaTeX source files listed above.
3. Confirm whether figure artifacts are marked `publication_ready` or `diagnostic_only` in `data/reference/MEA/manifests/figure_artifact_manifest.csv` and `data/reference/MEA/manifests/figure_artifact_file_manifest.csv`, if those files exist.
4. Confirm whether any Phase 3/global-regression artifact is explicitly marked complete. If no complete Phase 3 artifact exists, do not write any final-regression claim.

### Edits to apply

#### 1. Replace the abstract with this exact content, converted only as needed to match existing LaTeX macros

Use the existing macros such as `\MEA`, `\COtwo`, `\HtwoO`, `\MEAH`, `\MEACOO`, `\HCOthree`, `\COthree`, `\HthreeO`, and `\Hydroxide` where the manuscript already uses them. Preserve the meaning and all numbers. Keep the abstract under 250 words.

> Aqueous monoethanolamine (MEA) is a benchmark solvent for post-combustion carbon dioxide (CO2) capture, but absorber and stripper calculations require equilibrium CO2 pressure and liquid speciation rather than a pressure correlation alone. This work evaluates MEA--H2O--CO2 thermodynamics using a true-species liquid basis containing CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and OH-. Literature vapor--liquid-equilibrium records and nuclear magnetic resonance (NMR) speciation data were placed on a common CO2-loading basis and tested with two calculations. First, an ideal Smith--Missen-style five-reaction, nine-species baseline reproduced the main amine-speciation trends, with median absolute log10(model/data) residuals of 0.055 for MEA, 0.044 for MEAH+, 0.029 for MEACOO-, and 0.227 for HCO3-. Second, the same reaction network was evaluated with electrolyte perturbed-chain statistical associating fluid theory (ePC-SAFT) activities, fugacities, concentration-dependent permittivity, and solvation-shell/dielectric-saturation Born corrections. The activity-based calculation converged for all 161 pressure records and 74 speciation records, giving median absolute residuals of 0.493 for CO2 pressure, 0.074 for MEA, 0.033 for MEAH+, 0.040 for MEACOO-, and 0.461 for nonzero HCO3- targets. These results support a residual-qualified activity-based evaluation; carbonate-family species and trace water ions remain the main limitations.

Do not include references or DOI links in the abstract.

#### 2. Revise the Introduction for engineering consequence

Add one process-facing paragraph early in the Introduction after the first paragraph. It must say, in journal language, that:

- equilibrium CO2 partial pressure controls gas-phase driving force in absorber calculations;
- liquid speciation constrains chemically available amine, carbamate formation, and rich/lean loading consistency;
- pressure-only fitting can hide chemically implausible liquid states;
- the manuscript therefore evaluates pressure and speciation together.

Do not add kinetic claims unless the manuscript already provides kinetic data. Do not claim scale-up validation.

Rename and align Introduction subsections to the strict roadmap where possible:

1. `MEA and reactive CO2 absorption`
2. `Thermodynamic modeling of MEA--CO2--H2O`
3. `SAFT and PC-SAFT models for alkanolamines`
4. `ePC-SAFT and advanced Born electrostatics`
5. `Contribution of this work`

Replace template wording such as “This manuscript makes four specific contributions” with active voice. Use language like “We assemble...”, “We define...”, “We evaluate...”, and “We delimit...” only where those actions are supported by existing content.

#### 3. Split the current model section into Theory and Data and Methods

The current section titled `Thermodynamic Model and Residual Evaluation` combines theory, methods, residual definitions, and parameter status. Revise it to match this manuscript spine:

1. Introduction
2. Theory
3. Data and Methods
4. Results and Discussion
5. Conclusions
6. Data and Code Availability

Use the existing file structure unless adding a new `sections/data_methods.tex` is simpler and cleaner. If you add a new section file, update `main.tex` exactly once and do not create unused files.

The **Theory** section must contain:

- PC-SAFT/ePC-SAFT residual Helmholtz-energy terms;
- electrolyte activity-coefficient and fugacity definitions;
- modified Born SSM+DS and concentration-dependent permittivity explanation;
- MEA--CO2--H2O reaction network;
- phase-equilibrium conditions and reference-state conventions.

The **Data and Methods** section must contain:

- experimental data inventory;
- species basis and parameter hierarchy;
- pure-component and binary-parameter provenance;
- direct MEAH+/MEACOO- regression evidence;
- residual definitions and objective function;
- computational implementation and reproducibility boundaries.

If exact source ranges, solver tolerances, weights, or thresholds are not present in repo-local evidence, do not invent them. State only what is verified and record missing items in the blocker report.

#### 4. Define or remove “accepted” terminology

Before any use of “accepted,” the manuscript must state the exact numerical acceptance threshold and its evidence source. If no threshold is verified from repo-local evidence, remove the word “accepted” from the manuscript body and replace it with neutral reporting language.

Required replacements unless a verified threshold exists:

- “accepted major-species residuals” -> “major-species median absolute residuals”
- “accepted pressure metric” -> “reported pressure metric” or “pressure residual”
- “accepted direct-positive speciation metrics” -> “nonzero measured-target speciation metrics”
- “accepted high-temperature rows” -> “high-temperature rows with smaller residuals”

#### 5. Replace internal/project jargon with journal-facing language

Apply the restricted-language table in `codex_mea_revision_grounding_gate.md`. Mandatory examples:

- “solves all 161 pressure records” -> “converged for all 161 pressure records”
- “direct-positive targets” -> “nonzero measured targets”
- “reported-zero rows” -> “measurements reported as zero and treated as upper-bound targets”
- “solver-success rows” -> “converged calculation rows”
- “Born-radius mode 3” -> define in text or move to a table note; do not leave it unexplained
- “Tier A” -> define from the evidence manifest or remove
- “bookkeeping variable” -> replace with “The liquid composition enters the EOS derivatives directly.”

#### 6. Add engineering interpretation of residuals

Where the manuscript reports the pressure residual of 0.493 on a log10 scale, add this interpretation:

- `10^{0.493} \approx 3.1`, so the median pressure error corresponds to about a factor of 3.1.
- This supports a diagnostic/activity-based evaluation, not a standalone process-design pressure correlation.

Use cautious language. Do not claim process readiness.

#### 7. Consolidate repetitive figures if the same diagnostic panels are repeated

If the manuscript contains separate temperature-specific speciation figures with nearly identical captions, consolidate them into a single multi-panel figure using the existing image files. Do not regenerate data or invent new plots. Use the existing `subcaption` package if it is already loaded. The combined caption must state:

- the curves are from converged activity-coupled ePC-SAFT states;
- markers are nonzero measured speciation targets;
- zero-reported and balance-inferred quantities are evaluated separately;
- the figure is a residual comparison, not proof of a finalized global regression.

If the artifact manifest marks the figure inputs as `diagnostic_only`, do not call the figures publication-ready. Record the figure readiness blocker.

#### 8. Improve Results and Discussion framing

Revise the Results opener so it states the main result and limitation, not just a list of subsections. The revised section must make these points without overclaiming:

- the ideal baseline verifies reaction/balance conventions;
- the activity-coupled ePC-SAFT calculation converged on the assembled pressure/speciation records;
- MEA, MEAH+, and MEACOO- speciation are the strongest supported observables;
- bicarbonate, carbonate, and trace water ions remain limiting observables;
- pressure residuals are quantified but not promoted to a pressure-optimized model.

#### 9. Tighten Phase 3 limitation language

The manuscript may mention the missing coupled regression once in the Methods/Limitations area and once in the Conclusion. It must not repeatedly foreground failure. Use this posture:

> The present work does not report a completed coupled pressure/speciation regression. The reported parameter set is therefore evaluated as a fixed activity-based parameter set with explicit residuals.

Do not write “future work is required before this paper matters.” Do not write any final parameterization claim.

#### 10. Correct Data and Code Availability

Revise the Data and Code Availability section so it does not imply an archive DOI exists unless one is verified. Required content:

- processed validation tables;
- fitted parameter tables;
- plotting CSV files;
- source identifiers;
- repository URL only if confirmed from `git remote -v` or existing source files;
- release tag and commit hash only if an actual release exists or the manuscript is explicitly using the current commit;
- explicit statement that no archival DOI has been minted if that remains true.

Do not invent a DOI, release tag, Zenodo archive, license, or permanent URL.

#### 11. Fix nomenclature consistency

In `nomenclature.tex`, replace any entry that defines `\kappa_{ij}` as a binary interaction parameter. Use `k_{ij}` for binary dispersion interaction parameters. Keep `\kappa` for inverse Debye length and `\kappa^{A_iB_j}_{ij}` for association volume if both appear in the manuscript.

#### 12. Add a blocker/summary file

Create or update `docs/roadmaps/manuscript_revision_blockers.md` with unresolved evidence gates. At minimum, include blockers for:

- missing acceptance thresholds, if not found;
- missing publication-ready figure artifacts, if manifests mark figures diagnostic-only;
- missing archive DOI, if not present;
- missing condition ranges or source-by-source residual tables, if not found;
- missing Phase 3 artifacts, if no complete coupled-regression artifact exists.

Create or update `docs/roadmaps/manuscript_revision_summary.md` with:

- files edited;
- claims removed or softened;
- terms replaced;
- validation commands run;
- validation commands skipped and why.

### Validation gates before final response

Run these checks from the repository root. Adapt path prefixes only if the repo uses a different manuscript directory.

1. Search for banned or restricted terms in manuscript source:
   - `accepted residual`
   - `accepted pressure`
   - `accepted direct-positive`
   - `direct-positive`
   - `reported-zero`
   - `solver-success`
   - `solves all`
   - `pressure-optimized global parameterization`
   - `finalized jointly regressed parameter set`
   - `worktree`
   - `Codex`
   - `C:/`
   - `file:/`
2. Confirm the abstract is under 250 words.
3. Confirm no raw DOI URLs or local Windows paths appear in manuscript text.
4. Build the manuscript only using an existing repo-supported build command. Do not invent a build system. If no build command is found, record that in the summary.
5. If the build runs, inspect the log for undefined references, missing figures, missing citations, and font/encoding warnings. Record unresolved issues.

### Final response from Codex

Return a concise revision report with:

- the files changed;
- the exact manuscript posture after revision;
- which gates passed;
- which gates remain blocked;
- any validation/build output summary;
- no unsupported claims.
