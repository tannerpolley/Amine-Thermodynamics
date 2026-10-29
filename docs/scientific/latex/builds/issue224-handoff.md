# Issue 224 manuscript corrections

All seven checklist items were applied on the issue worktree. No model calculation or parameter value changed. Main PDF: 25 pages; supplement PDF: 20 pages. No site-index change is needed.

## Source checked

Polley and Hedengren, Next Chemical Engineering 3 (2026), 100132, DOI 10.1016/j.nxcen.2026.100132. Acquired through Zotero Companion into collection 8RZP275E; parent TIVK3B6M, PDF QHI67GZ8. PDF SHA-256: c3d35ca54f7f4ac54727d790f18e6c4a90e271bb3f01d5a4d146b85755489459. Read the source PDF through its text extraction, particularly Section 2.1, methods, results/discussion, limitations and Appendix B. The local literature shelf was absent in this worktree.

Section 2.1 (p. 3) and Table 7 (p. 16) define CO2, MEA, water, MEAH+, MEACOO-, bicarbonate, carbonate, hydronium and hydroxide. Appendix B (pp. 16–18, especially p. 17) distinguishes literature inputs from fitted values: six amine-ion size/dispersion/Born values and their mutual interaction fitted to ion/speciation data; MEA–water interaction refitted to 25 Cai binary VLE rows; CO2 dispersion selected jointly with R4 on a pressure/speciation grid; R2/R4/R5 enthalpy shifts fitted to pressure, speciation and 40/80 °C calorimetry. That paper does not describe a joint pressure/speciation/caloric/density fit. Its column enthalpies are empirical and separate from the EOS equilibrium calculation. The new introduction states this narrower difference without claiming that explicit-ion MEA work is absent.

Table 7 (p. 16) gives sigma(MEAH+) = 3.48508556586 Å, versus 5.35 Å here. These fitted segment diameters are parameterization-dependent, not measured physical ion sizes.

Only polleyReactiveEPCSAFTModeling2026 was copied into references.bib through scripts/cited_bibliography.py from the existing central Better BibTeX export; previous entries were unchanged and the local attachment field was removed by the copier. No full bibliography refresh.

## Weighting and notation

The retained analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/fit-summary.json supplies total cost 148.87893934557388, Cai cost 91.87458520309771 and loaded-density cost 0.5654031419421082. The corresponding shares are 61.710934808476054% and 0.3797737574081645%, printed as 61.71% and 0.3798% in Methods. The same inputs generate tables/objective_groups.tex used by S2; reported-score.json and fitted rows are reconciled by a7_presentation.checked(). These are fitted-cost shares, not physical accuracy measures or new validation results.

Methods owns the displayed cost equation; S2 retains every residual, scale, weight and full group contribution. Dispersion uses epsilon_i/k_B in parameter tables/nomenclature and epsilon_ij in the equations. Association remains epsilon^AB; dielectric quantities remain varepsilon. Uncertainty symbols u_rho and u_alpha are unchanged. All generated-table numerical values were compared with HEAD, excluding citation keys and locator formatting, and are unchanged. The source-integrity check was updated to pin the approved revised literature and symbol blocks; numerical input checks remain active.

The Lloret 4.7, Akula 4.2 and Neumann 4.2 locators use citation optional arguments in the generator and generated table. All manuscript occurrences of e-NRTL, labelled, We examine and We ask were replaced with eNRTL, labeled and impersonal wording.

## Cross-reference audit

Checked against final auxiliary labels and section content:

- Objective: main Eq. 17; tangent-plane distance: main Eq. 19 (formerly 18).
- Residual Helmholtz split: main Eq. 1, unchanged.
- Pair dispersion energy: main Eq. 3. Corrected S11's former reference to Eqs. 3 and 4 because Eq. 4 defines temperature-dependent kij.
- Main Sections 2.2 (diameters/dispersion), 2.3 (association), and 4.4.5 (density and heat capacity) still match their supplement references.
- S1 inputs, S2 objective, S3 source conventions, S4 calorics/numerical checks, S5 density/carbonate shares, S6 uncertainty, S7 source deviations, S8 phase search, S9 bound restriction, S10 limits, S11 EOS equations and S12 MDEA still match every Section S reference. Association-strength Eq. S14 is unchanged.

## Checks

Supplement built first, followed by main, with SOURCE_DATE_EPOCH=1792750003 FORCE_SOURCE_DATE=1 nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds for each document. Table generator rerun with the existing interpreter via a temporary worktree .venv symlink; the symlink was removed. No dependency file changed.

Freshness check with --write-receipt passed; prose check on every changed .tex file passed; git diff --check passed. Final main/supplement logs contain no unresolved citations/references, duplicate labels, LaTeX/package warnings or overfull boxes. Both PDFs have zero Type 3 fonts.

Automated visual checks completed for all 45 pages with no error-severity findings; conservative warnings remain (main 200, supplement 83), mainly tight line clearances and figure text/path intersections. Contact sheets were inspected for all pages; Methods p. 9, introduction p. 3 and supplement dispersion/association p. 16 were inspected individually at larger size. This is not a complete full-size manual inspection of all 45 pages. No layout changes were made in response to warnings outside the local corrections. Visual reports and build logs remain in builds/issue224-*.

No merge, push or independent final review was performed.
