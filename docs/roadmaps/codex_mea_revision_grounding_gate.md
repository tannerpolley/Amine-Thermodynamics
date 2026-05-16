# Grounding and Gating Document — MEA ePC-SAFT Manuscript Revision

This document is the acceptance gate for the Codex manuscript-revision task. It converts the senior-reviewer audit into enforceable edit rules. The manuscript must be revised as a **Phase 1 + Phase 2** paper only. Phase 3 is outside the current scope.

## 1. Controlled manuscript posture

### Required posture

Use this claim as the central manuscript posture:

> This paper reports a residual-qualified, activity-based ePC-SAFT evaluation of loaded aqueous MEA using a true-species liquid basis, literature VLE records, and NMR speciation records. The paper reports an ideal Smith--Missen-style baseline and a fixed-parameter activity-coupled ePC-SAFT calculation with explicit residuals.

### Forbidden posture

Do not present the paper as any of the following:

- a finalized global parameterization;
- a finalized joint pressure/speciation regression;
- a pressure-optimized ePC-SAFT model;
- process-ready VLE prediction for absorber/stripper design;
- a complete Phase 3 result;
- a validated scale-up or kinetic model.

### Required limitation

Use this limitation language or equivalent journal-facing language:

> The present work does not report a completed coupled pressure/speciation regression. The reported parameter set is therefore evaluated as a fixed activity-based parameter set with explicit residuals.

Do not write this limitation repeatedly. Use it once in Methods/Limitations and once in the Conclusion at most.

## 2. Evidence gates

Every claim must map to at least one of these evidence classes:

| Evidence class | Allowed use |
|---|---|
| Existing LaTeX source | Current wording, equations, counts, and manuscript structure. |
| Roadmap/phase-plan files | Scope boundaries, Phase 1/2/3 claim gates, figure readiness, artifact contract. |
| Manifests | Data provenance, parameter provenance, figure status, regression status. |
| Existing CSV/data files | Numeric ranges, residual values, plotted quantities, source splits. |
| Repo-local source-paper Markdown | Literature framing and parameter/method comparison; do not paste long article text. |
| Existing figure/table artifacts | Figure inclusion only if files exist and manifest status allows their use. |

If a claim has no evidence, remove it or record it as a blocker. Do not infer missing data ranges, thresholds, parameter values, DOI status, or figure readiness.

## 3. Phase gates

| Topic | Allowed | Forbidden |
|---|---|---|
| Phase 1 | Ideal/apparent Smith--Missen-style baseline; reaction/balance convention check. | Calling Phase 1 the final true-species ePC-SAFT model. |
| Phase 2 | Activity-based true-species ePC-SAFT evaluation with explicit residuals. | Calling Phase 2 a finalized joint-regression result. |
| Phase 3 | Mention as outside scope or incomplete if repo evidence supports that. | Claiming newly regressed final pressure/speciation parameters without complete Phase 3 artifacts. |
| Figures | Use existing artifacts with honest status. | Calling diagnostic-only figures publication-ready. |
| Data/code | State verified repository/release/archive information. | Inventing DOI, release tag, repository URL, or license. |

## 4. Restricted language and required replacements

Apply this table throughout `main.tex` and all manuscript section files.

| Restricted wording or pattern | Required action |
|---|---|
| `accepted residual`, `accepted residual metrics`, `accepted pressure metric`, `accepted direct-positive`, `accepted major-species` | Use only if an explicit numerical acceptance criterion and source are written before first use. If not, replace with neutral metric language. |
| `accepted high-temperature rows` | Replace with `high-temperature rows with smaller residuals` unless an acceptance threshold is defined. |
| `solves all 161 pressure records`, `solves all 74 speciation records`, `solves all records` | Replace with `converged for all 161 pressure records`, `converged for all 74 speciation records`, or equivalent. Solver convergence is not validation. |
| `direct-positive targets`, `direct positive targets`, `direct-positive rows` | Replace with `nonzero measured targets` after defining the target class. |
| `reported-zero rows` | Replace with `measurements reported as zero and treated as upper-bound targets`. |
| `balance-inferred rows` | Define explicitly or replace with `quantities inferred from balance constraints`. |
| `solver-success rows` | Replace with `converged calculation rows`. |
| `target-role residual audit` | Replace with journal-facing residual category definitions. |
| `Born-radius mode 3` | Define from a manifest/method note or remove. Do not leave unexplained. |
| `Tier A` | Define from an evidence manifest or remove. |
| `bookkeeping variable` | Replace with `The liquid composition enters the EOS derivatives directly.` |
| `improved performance` | Replace with a specific residual change and consequence. If the improvement is small, describe it as parameter evidence, not performance improvement. |
| `This manuscript makes four specific contributions` | Replace with active voice and consequence-driven contributions. |
| `pressure-optimized global parameterization` | Forbidden as a claim. Allowed only in a limitation stating it is not reported. |
| `finalized jointly regressed parameter set` | Forbidden as a claim. Allowed only in a limitation stating it is not reported. |
| `predictive process-ready`, `validated for process design`, `scale-up validated` | Forbidden unless supported by process-scale validation data, which are not in scope. |
| `In the realm of`, `A testament to`, `significant improvement` without numbers, `state-of-the-art` without a source | Remove. |
| `worktree`, `Codex`, `agent`, `handoff`, `file:/`, `C:/Users` | Must not appear in manuscript source. |

## 5. Required abstract replacement

Replace the existing abstract with the text below, converted to the manuscript’s existing LaTeX macros only as needed. Preserve the exact numbers and limitations.

> Aqueous monoethanolamine (MEA) is a benchmark solvent for post-combustion carbon dioxide (CO2) capture, but absorber and stripper calculations require equilibrium CO2 pressure and liquid speciation rather than a pressure correlation alone. This work evaluates MEA--H2O--CO2 thermodynamics using a true-species liquid basis containing CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and OH-. Literature vapor--liquid-equilibrium records and nuclear magnetic resonance (NMR) speciation data were placed on a common CO2-loading basis and tested with two calculations. First, an ideal Smith--Missen-style five-reaction, nine-species baseline reproduced the main amine-speciation trends, with median absolute log10(model/data) residuals of 0.055 for MEA, 0.044 for MEAH+, 0.029 for MEACOO-, and 0.227 for HCO3-. Second, the same reaction network was evaluated with electrolyte perturbed-chain statistical associating fluid theory (ePC-SAFT) activities, fugacities, concentration-dependent permittivity, and solvation-shell/dielectric-saturation Born corrections. The activity-based calculation converged for all 161 pressure records and 74 speciation records, giving median absolute residuals of 0.493 for CO2 pressure, 0.074 for MEA, 0.033 for MEAH+, 0.040 for MEACOO-, and 0.461 for nonzero HCO3- targets. These results support a residual-qualified activity-based evaluation; carbonate-family species and trace water ions remain the main limitations.

## 6. Required engineering-framing insert

Add a process-facing paragraph early in the Introduction. Use this content, converted to manuscript macros and journal style:

> In absorber and stripper calculations, equilibrium CO2 partial pressure determines the gas-phase driving force used by rate-based or equilibrium-stage models. The liquid speciation determines how much amine remains chemically available, how much carbamate has formed, and whether rich/lean loading calculations remain chemically plausible. A pressure-only fit can therefore reproduce a pressure curve while hiding an implausible distribution of MEA, MEAH+, MEACOO-, bicarbonate, and carbonate species. For that reason, this work evaluates pressure and speciation together.

Do not add kinetic-rate constants, column-height claims, mass-transfer coefficients, pilot-scale validation, or scale-up claims.

## 7. Required structure

The revised manuscript must use this spine unless the existing journal class or user source files make a different layout unavoidable:

1. Introduction
2. Theory
3. Data and Methods
4. Results and Discussion
5. Conclusions
6. Data and Code Availability

The strict roadmap expects the following detailed structure:

### Introduction

1. MEA and reactive CO2 absorption
2. Thermodynamic modeling of MEA--CO2--H2O
3. SAFT and PC-SAFT models for alkanolamines
4. ePC-SAFT and advanced Born electrostatics
5. Contribution of this work

### Theory

1. PC-SAFT residual Helmholtz energy
2. Electrolyte PC-SAFT and ion activity coefficients
3. Modified Born term with solvation shell and dielectric saturation
4. MEA--CO2--H2O reaction network
5. Phase-equilibrium conditions and reference states

### Data and Methods

1. Experimental data inventory
2. Species basis and parameter hierarchy
3. Pure-component and binary parameters
4. MEAH+ and MEACOO- regression
5. Coupled pressure/speciation objective
6. Computational implementation and reproducibility

### Results and Discussion

1. Neutral baseline validation
2. Full ionic parameter set
3. MEAH+/MEACOO- regression results
4. Chemical speciation
5. CO2 partial pressure
6. Sensitivity and identifiability
7. Comparison with literature models
8. Model limitations and transferability

## 8. Paragraph-level audit actions

Use this table to drive specific paragraph edits. Scores are audit scores out of 10; lower scores need direct revision.

| ID | Location | Score | Required action |
|---:|---|---:|---|
| P01 | Abstract | 7.3 | Replace with the required abstract in this gate. |
| P02 | Introduction opening | 8.0 | Add engineering consequence sentence linking equilibrium pressure to absorber/stripper driving force. |
| P03 | Amine thermodynamics models | 7.6 | Add why parameter transferability matters for process simulation. |
| P04 | Experimental data basis | 8.4 | Add verified data ranges if available; if not available, do not invent. |
| P05 | SAFT/PC-SAFT literature | 7.8 | Shorten citation-list feel; end with a direct gap sentence. |
| P06 | SAFT gap | 8.3 | Keep, but connect activity-coupled speciation to process-relevant pressure prediction. |
| P07 | ePC-SAFT/Born literature | 7.5 | Split or synthesize by parameter strategy: inherited, independently fitted, validation. |
| P08 | Loaded MEA target | 8.2 | Add engineering output: pressure/speciation for rate-based or equilibrium process models. |
| P09 | Objective | 8.5 | Keep scope control; avoid pressure-only fit language becoming repetitive. |
| P10 | Four contributions | 8.0 | Rewrite in active voice and fewer consequence-driven claims. |
| P11 | Model target | 8.7 | Replace informal `bookkeeping` phrase with EOS-derivative language. |
| P12 | ePC-SAFT formulation | 8.1 | Add one sentence on why each term matters for MEA. |
| P13 | Residual term explanation | 7.8 | Shorten textbook-like explanation. |
| P14 | Hard-chain lead-in | 6.8 | Merge fragment with equation paragraph. |
| P15 | Segment/chain correction | 7.2 | Clarify notation after equation. |
| P16 | Excluded-volume consequence | 7.7 | Keep concise explanatory sentence. |
| P17 | Dispersion lead-in | 6.9 | Merge fragment with equation and explanation. |
| P18 | Dispersion explanation | 8.0 | Keep pressure-residual sensitivity link. |
| P19 | Association lead-in | 6.8 | Merge short paragraph. |
| P20 | Association-strength lead-in | 6.6 | Merge short paragraph. |
| P21 | Association physics | 7.7 | Qualify ions-without-sites statement if any ion cross-association is later used. |
| P22 | Debye--Huckel lead-in | 6.9 | Merge short paragraph. |
| P23 | Permittivity coupling | 8.3 | Keep; this is clear. |
| P24 | Born lead-in | 6.9 | Merge short paragraph. |
| P25 | Active Born set | 7.4 | Define SSM and DS in words before notation. |
| P26 | SSM+DS option | 7.8 | Explain ion-local dielectric medium. |
| P27 | Inverse-diameter lead-in | 6.8 | Merge short paragraph. |
| P28 | Shell-shift lead-in | 6.7 | Merge short paragraph. |
| P29 | SSM/DS physical meaning | 8.1 | Keep this style. |
| P30 | Fugacity equality | 8.2 | Specify volatile species and reference states cleanly. |
| P31 | Ionic liquid-phase constraint | 7.5 | Merge with equation explanation. |
| P32 | Residual contribution effect | 8.0 | Keep bridge to reactions. |
| P33 | Apparent feed | 7.5 | Define loading alpha in text, not only symbols. |
| P34 | CO2 addition | 7.5 | Merge with apparent-feed paragraph. |
| P35 | Species basis | 7.0 | Keep only as lead-in to vector or rewrite as prose. |
| P36 | Reaction equilibrium | 8.5 | Keep central novelty statement. |
| P37 | Activity coefficient distinction | 8.3 | Specify distinction from mole-fraction Smith--Missen baseline. |
| P38 | Balance equations lead-in | 7.0 | Add a stoichiometric-matrix or pseudo-component-balance note. |
| P39 | Advanced Born/permittivity | 8.0 | Define or remove `Born-radius mode 3`. |
| P40 | Physical dielectric explanation | 8.7 | Keep and connect to measurable pressure/speciation effect. |
| P41 | Parameter vector/residual | 7.8 | Define which parameters actually move in Phase 2. |
| P42 | Objective function | 8.2 | Keep multi-observable framing. |
| P43 | Multi-observable rationale | 9.0 | Keep; strong reviewer-facing paragraph. |
| P44 | Coupled regression status | 8.4 | State reproducibility boundary; avoid internal method-defect language. |
| P45 | Results opener | 7.7 | Replace generic opener with main result and limitation. |
| P46 | Experimental data basis | 8.7 | Add verified ranges and split status if available. |
| P47 | Ideal baseline metrics | 8.2 | Remove `accepted` unless threshold is defined. |
| P48 | Pressure baseline | 8.5 | Add practical implication of low-temperature failure. |
| P49 | Neutral parity check | 7.5 | Explain what parity protects against or merge into figure caption. |
| P50 | ePC-SAFT parameter set | 7.8 | Move detailed provenance to table; state engineering implication in prose. |
| P51 | Table note on T and sigma | 7.0 | Convert to table footnote. |
| P52 | Binary-interaction matrix | 7.6 | Use compact table/bullets; reduce dense prose. |
| P53 | Activity pressure evaluation | 7.8 | Replace undefined `accepted`; convert 0.493 log residual to factor 3.1. |
| P54 | Speciation metrics | 8.0 | Define nonzero/zero/balance-inferred categories earlier. |
| P55 | Amine-ion regression | 8.2 | Emphasize parameter evidence; do not overstate small improvement. |
| P56 | Trace-ion sensitivity | 8.5 | Keep and connect to future data needs. |
| P57 | Coupled regression status | 8.8 | Make it a scope boundary, not a deficiency. |
| P58 | Split/sensitivity analysis | 8.5 | Add supporting table/figure only if verified artifacts exist. |
| P59 | Conclusion opening | 8.3 | Make more active and engineering-facing. |
| P60 | Ideal baseline conclusion | 8.2 | Remove `accepted` unless threshold exists. |
| P61 | Activity conclusion | 8.0 | Add `not process-ready pressure prediction` boundary. |
| P62 | Final limitation/future work | 8.4 | Rephrase Phase 3 as outside present scope. |
| P63 | Data/code availability | 6.2 | Add concrete repo/release/archive facts only if verified; otherwise write blocker. |

## 9. Required next 10 steps converted to edits

| Step | Required Codex action |
|---:|---|
| 1 | Title/subtitle must frame the paper as an evaluation, not a finalized parameterization. If retitling, use language close to `Residual-Qualified Activity-Based ePC-SAFT Evaluation of Aqueous MEA--CO2--H2O`. |
| 2 | Split the manuscript into Introduction, Theory, Data and Methods, Results and Discussion, Conclusions, Data and Code Availability. |
| 3 | Add process-facing Introduction paragraph about absorber driving force, speciation, and loading consistency. |
| 4 | Define residual acceptance criteria before use, or remove `accepted` terminology. |
| 5 | Convert log pressure residual 0.493 to factor error: `10^{0.493} approx 3.1`; mark diagnostic/screening, not process design. |
| 6 | Move parameter provenance into clean tables or clear parameter hierarchy prose. Do not invent missing parameters. |
| 7 | Combine repeated speciation figures into one multi-panel figure if image files exist. |
| 8 | Audit balance equations and reference states; add a pseudo-component/stoichiometric-balance note. |
| 9 | Replace robotic/meta phrases and internal project terms using the restricted-language table. |
| 10 | Fix Data and Code Availability with verified repository/release/archive information; do not invent DOI. |

## 10. Literature-style alignment requirements

Use repo-local source-paper Markdown files only for style and technical comparison. Do not paste long article text. The revised manuscript should match these literature patterns:

- SAFT/PC-SAFT MEA papers report association schemes, binary validation, Smith--Missen chemistry, and pressure deviations.
- ePC-SAFT MDEA papers explicitly list ionic species, activity/reference-state conventions, parameter provenance, and whether ternary data were fitted or predicted.
- ePC-SAFT advanced papers clearly distinguish inherited pure parameters, independently regressed binary parameters, and final validation data.
- Process-facing ePC-SAFT papers explain how gas solubility predictions reduce experimental effort or support solvent/process screening.

Required manuscript response:

- add explicit parameter hierarchy;
- add explicit species/activity-reference-state conventions;
- compare against literature metrics only when numeric comparisons are verified from repo-local sources;
- avoid promotional language.

## 11. Data and Code Availability gate

The Data and Code Availability section must not say `cited release` unless an actual release is identified. Use verified wording only.

Allowed if no DOI exists:

> The processed validation tables, fitted parameter tables, plotting CSV files, and source identifiers used in this manuscript are maintained with the project source. No archival DOI has been minted at the time of manuscript preparation. A repository URL, release tag or commit hash, license, and archival record must be added before final submission if they are not already verified in the repository metadata.

If `git remote -v` verifies a repository URL, it may be included. If a release tag is not verified, do not include one. If an archive DOI is not verified, do not include one.

## 12. Nomenclature gate

Correct these notation problems:

- `k_{ij}` = binary dispersion interaction parameter.
- `\kappa^{A_iB_j}_{ij}` = association-volume parameter.
- `\kappa` = inverse Debye length, if used in Debye--Huckel equations.
- Do not define `\kappa_{ij}` as a binary interaction parameter.

## 13. Validation checklist

The revision is not accepted until these checks are reported:

1. `git status --short` recorded.
2. Abstract word count under 250.
3. Search completed for restricted terms.
4. Search completed for raw DOI URLs and local paths.
5. Figure artifact status checked where manifests exist.
6. Phase 3 artifact status checked where manifests exist.
7. Build attempted only through an existing repo-supported command.
8. Build warnings or skipped build reason recorded.
9. Blocker file created or updated.
10. Revision summary file created or updated.

## 14. Final acceptance state

The desired final state is **Major Revision addressed but not necessarily submission-ready if blockers remain**. Codex must not hide unresolved blockers. A correct revision can still report unresolved items such as missing archive DOI, diagnostic-only figures, or missing source-by-source residual tables.
