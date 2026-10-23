# Issue 197 manuscript reframe

The rewrite produces a 17-page main manuscript and a 21-page supplement. The accepted question is whether one explicit-ion ePC-SAFT formulation with carbamate chemistry represents the selected equilibrium, caloric and density observations for nominal 30 wt% MEA. The text supports that bounded use, reports the property discrepancies beside their comparisons, and does not establish suitability across an absorber's operating range. This is a rewrite of retained calculations and literature comparisons, not a new fit or physical validation.

- Main: `docs/scientific/latex/builds/main.pdf`, SHA-256 `45c77179e1b93b985935b0df0bb9e425cd42897798b37efefbe7f5f6238a1416`.
- Supplement: `docs/scientific/latex/builds/supplement.pdf`, SHA-256 `2e7cc54d113be2f1ad940c945b9107d3858bb71aa9dfb0f105ae9d048e4c4c7a`.
- Worktree: `/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.worktrees/issue-197-stage-3-rewrite-the-mea-manuscript-2`.
- Branch: `issue-197-stage-3-rewrite-the-mea-manuscript-2`; base `d57855530e80118b990e0a7cfc4ae012625faf79`, including the model-curve figures from #202.
- Authority: the latest owner-approved [Reframe plan](https://github.com/tannerpolley/Amine-Thermodynamics/issues/197#issuecomment-6359283213) and the full writer brief. This file records implementation and evidence; the issue comment remains the plan.

## Main-text outline

1. Introduction, pp. 1–2: motivation, question in the first paragraph, grouped literature and carbamate distinction.
2. Thermodynamic model, pp. 2–4: Helmholtz energy, Born contribution, permittivity, reactions and equilibrium.
3. Data and parameter estimation, pp. 4–6: one data inventory, property definitions, caloric/density basis, one objective paragraph, one solver sentence, final parameters.
4. Results and discussion, pp. 7–14: MEA–water VLE; CO2 solubility; liquid speciation; heat of absorption; density and heat capacity; short scope paragraph; phase stability; comparison with published models.
5. Conclusions, p. 14: intended use, limits, phase-stability lesson and remaining tests.

Declarations and references follow; nomenclature is on p. 17. The main has six figures. The density-error figure is Figure S1 on supplement p. 6.

## Approved plan implemented

Locations below are relative to `docs/scientific/latex/`. Paragraph comments remain in the source for review, without appearing in the PDFs.

| Plan item | Implementation and location |
|---|---|
| Exact title, without a prediction claim | `main.tex:77`, title page; matching supplement title, PDF metadata, local submission aids and `submission_metadata.yml`. |
| Motivation and question early | `sections/introduction.tex:2`, `introduction-01`, p. 1. The explicit-ion application distinction is in `introduction-03`; earlier MEA carbamate models are acknowledged. |
| Exact three-sentence supported answer | `sections/mea_system_modeling_results.tex:165`, `results-literature-02`, p. 14. The abstract and conclusion preserve the same claim limits. |
| Five properties from one thermodynamic formulation; density without volume translation | Required two sentences in `results-scope-01`, `sections/mea_system_modeling_results.tex:113`, p. 11; density AARD and its 47 fitted observations are in `results-density-01`, p. 10. |
| Accuracy within the published range, with both pressure populations | Abstract, Section 4.2 and Section 4.7, pp. 1, 7 and 13. Section 4.7 gives Zhang 13.5–35.5%, Najafloo 34.71% and Baygi 36.42%, with the 691-comparison populations and different-data/role/domain qualifications; Table 4 retains its source locators. Zhang's differential heat is distinguished from integral heat. |
| Use guidance beside each property | Sections 4.2–4.5, pp. 7–11. Concentration and high-temperature pressure errors stay with pressure; carbonate share and titration bicarbonate stay with species; Arcis stays with heat; three density misses, Han discrepancies and four heat-capacity errors stay with density and heat capacity. The short scope paragraph follows Figure 5. |
| Correct pressure versus species state convention | `sections/epc_saft_equation_of_state.tex:2`, p. 2: reactive bubble calculations for pressure, imposed single-liquid calculations at 101325 Pa for species. Figure 3 caption repeats the species convention. |
| Compact model, objective and solver treatment | Sections 2–3. Model equations and standard states remain. `sections/data_methods.tex:69` contains one objective sentence, the supplement reference and one solver sentence. Complete process definitions move to S4–S6/S10. |
| Keep final model, reaction laws, 16 parameters and six active bounds | Main Tables 1 and 3; `methods-04`/`methods-05`, p. 6. R5's 0.49 pK departure is beside the parameters, with the 50.5/63.4 kJ/mol comparison and compensation warning. Full fixed inputs remain in S9. |
| Preserve pressure/composition/species and caloric definitions | Section 3, pp. 4–5; heat, total enthalpy, equilibrium heat capacity and complete-feed mass basis remain explicit. Böttinger and Matin aggregate meanings, carrier-gas approximation, source compositions and heterogeneous density scales remain. |
| Preserve data roles | `methods-03`, p. 5; Table 2 and S2/S10. Arcis is a selection comparison; Wagner and 15/45 wt% observations were previously examined. No blind-validation claim is made. |
| Model-curve figures in the main, with new captions | Figures 1–5, pp. 7–11, all in `sections/mea_system_modeling_results.tex`. Captions give conditions, nominal composition, source/fit markers and state conventions. See the caption clarification below. |
| Exactly one main phase section and one figure | Section 4.6, pp. 11–12, Figure 6. Required two-sentence comparison-fit wording is in `results-phase-01`; 4.16/5.35 Å, +0.027/−0.5, 47/47 versus 44/47 and 0.45% are retained. |
| Finite phase domain in every condensed claim | Abstract, Section 4.6, Figure 6 and conclusion state 313.15–333.15 K and loading 1e-5–0.5. The 73-state comparison resolves descent at 12 versus zero states. #201's warmer extension is unused. |
| Exact literature phase wording, with Schick distinction | `results-phase-03`, `sections/mea_system_modeling_results.tex:150`, p. 12, cites Uyan Section 4, Wangler Section 6, Bülow Results and Discussion, Böttinger Sections 4–7, Nasrifar Sections 4–6, Baygi/Najafloo Section 3, Cleeton/Schick Sections 2–4. Schick Section 3.2 is experimental absence of observed demixing. No priority claim is made. |
| Move process detail and density-error figure | S1 reference fit/acceptance margins; S3 density errors and Figure S1; S4 pressure levels, repeated state, trial counts and solver details; S5 bound history, two single starts and fitting tolerances; S6 per-parameter conditional errors and correlations; S10 weights, cost shares and full data inventory. |
| Conclusions guide use and identify remaining tests | `sections/conclusion.tex`, p. 14: nominal 30 wt% measured-domain representation, poorer concentration transfer, bounded phase finding, independent phase and wider caloric comparisons still needed before process use. |
| Abstract at most 250 words | `main.tex:94`, 194 rendered words; local ChemRxiv version 189 words. Both retain 11.86%/47 and 20.55%/159 together. |
| Remove development labels; preserve sources and prior corrections | Neither PDF contains A6, A7, F1, endpoint, packet, canonical, gate, amendment or file hashes. The main also removes original-bound/restricted-bound names; those necessary process descriptions remain in the supplement. No filesystem paths appear in PDF prose. The bibliography is unchanged. |

## What moved to the supplement

- S1, pp. 1–2: reference fit and matched comparison, study-specific acceptance margins and their derivation.
- S3, pp. 4–6: density scales/source differences, carbonate-share table, three fitted density misses and the density-error figure.
- S4, pp. 7–9: full phase-search definition, 0.50/0.80/0.95 pressure levels, reference pressures, repeated 318.15 K evaluation, nine trials per state, numerical-error formulas and separately seeded split details.
- S5, p. 10: original/restricted bounds, 5.49 Å then 5.35 Å history, sequential single-start fits, fitting tolerances and linear algebra, diameter probes and loading sensitivity.
- S6, pp. 10–12: coefficient-by-coefficient conditional standard errors, covariance formula and correlation matrix. The main retains final parameters, bounds and the physical interpretation limits.
- S9, pp. 14–17: fixed species/interaction inputs, association-volume conversion and earlier input estimates.
- S10, pp. 17–19: objective formula, scales, weights, cost shares and complete source-by-source data inventory. The main has one compact data inventory.

S2 retains source-specific deviations; S7 retains source conventions/reaction shifts; S8 retains ideal-gas caloric inputs and numerical solution checks.

## Figure captions and retained prior corrections

The #202 curves are used as generated. Filled/open markers identify fitted/not-fitted observations. Liquid-property captions explain dashed segments as imposed single-liquid states below their bubble pressure; the species panel at 353.15 K uses 31 wt% MEA. The binary figure varies solvent composition and uses dashed lines for its vapor branch; the pressure figure uses bubble curves, and the heat curves contain no below-bubble segments. These exceptions are stated explicitly to avoid assigning the liquid-property dash meaning to a different calculation.

Prior science corrections remain: no claim of physical validation from calibration or numerical convergence; matched reference-fit density pressures differ and lack a retained correction; heterogeneous density scales are not uniformly standard uncertainties; two-phase classification alone does not identify two liquids; independently seeded splits have a separate software identity; parameter compensation and standard-state shifts remain disclosed. No missing source was encountered.

## Numerical evidence and changes

`197-reframe-number-sources.md` lists the displayed values and populations. `197-reframe-numeric-check.json` retains 41 numerical/population checks, the 73 identified paragraphs, every generated table's numerical rows and input hashes, all prose-number additions/cuts, and line-ending/bibliography checks. The earlier revision and correction audits remain applicable to unchanged coefficients and process details.

Notable clarified populations and newly explicit curve observations are: pressure at loading 0.69, 159 kPa at 313.15 K versus 2.848 MPa at 393.15 K; source pressure deviations 9.42/19.37/29.76%; Aronu cold high-loading errors 46–70% low; MEA + MEAH+ AARD 2.32% over 25 compared observations, 20 fitted; carbonate curve maximum at or below 1.8e-5; Matin's 19 bicarbonate totals at 67.48%; Arcis signed errors +10.21/+3.14 kJ/mol with about 0.19 kJ/mol calculated pressure effect; Han's five loaded 30 wt% values per temperature at −0.43/−0.72/−1.20% mean signed error and worst error −20.02 kg/m3. The four heat-capacity errors are +5.53/+2.57/+1.15/−2.13%. The fitted species and loaded-density ranges in the compact table are derived from the retained rows: 293.15–333.15 K and 293.15–353.15 K. No model-result file changed.

Figures and tables changed only through their two generators. A read-only rerun reproduced all 38 generated files byte for byte: 23 table files, 14 PDF/PNG figures and figure provenance. Table-data comparisons show 17 existing files unchanged and both moved full tables preserving their earlier data cells. The table generator also narrows the eight-plus-column layout slightly to remove an overfull box; the phase-figure generator replaces process labels and separates panel titles from axis labels.

## Builds and visual inspection

The retained PDFs use SOURCE_DATE_EPOCH `1792744075`, the base commit timestamp. The normal main build used `scripts/build_manuscript.sh`; supplement compilation used `latexmk`. Exact commands, source hashes, generated-file hashes, PDF hashes and checks are in `197-reframe-build-checks.json`; build output is in `197-reframe-main-build.log` and `197-reframe-supplement-build.log`. To reproduce these exact PDF bytes after committing, run latexmk with the recorded epoch rather than the build wrapper's newer HEAD timestamp.

Both builds finish without overfull boxes, undefined references/citations, missing characters or font substitutions. One underfull bibliography paragraph remains in the supplement (Uyan reference, p. 21); inspection confirms it is legible. Automated visual QA returns `review` for both PDFs: main has 40 tight-clearance and 16 text/graphic warnings; supplement has 74 tight-clearance and 11 landscape-edge warnings, with no errors. Every page was inspected in color and grayscale at full size. The warnings concern intentional mathematical geometry, class caption/title spacing and the landscape correlation table; no unintended clipping or overlap remains. The automated result is preserved as `review`.

The main freshness check, CSE prose check and `git diff --check` are recorded with the final evidence. Existing files retain their line endings. The bibliography is byte-identical to the starting commit and all cited keys exist.

## Open items and delivery limits

The parent's independent number/claim review and reader-story review remain, followed by owner review. The 353–393 K phase extension remains outside the promoted manuscript evidence. The retained comparisons do not physically validate phase behavior or absorber/stripper performance. There are no missing sources or unresolved build defects for this implementation.

No subagent, agent memory, Zotero edit, bibliography refresh, Overleaf sync, deposit/DOI change, journal action, push, merge or issue closure was performed. The Quarto preview service was untouched. The issue-branch commit is the implementation handoff; its SHA is reported in the final response.
