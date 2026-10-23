# Issue 197 manuscript rewrite: Implementor handoff (2026-10-22)

The authorized rewrite is complete locally and ready for the parent’s independent science and reader reviews. Main PDF: 22 pages; supplement: 16 pages. Retained numerical results and hashed inputs are unchanged. No Engine calculation, new fit or issue #201 result was used. The staged deposit is unpublished.

The current branch is `issue-197-stage-3-rewrite-the-mea-manuscript`; starting commit `2738fcee88f1c1cad2dec4e6f87ecd1cf0f995fc`. The source used for the final PDFs is `948e518da19aa26a33b49cb2f20c1832b8139938`; both builds use `SOURCE_DATE_EPOCH=1792728632` and `FORCE_SOURCE_DATE=1`. Later verification metadata commits do not change rendered inputs.

## Final documents and checks

| Document | Pages | SHA-256 |
|---|---:|---|
| `main.pdf` | 22 | `2efa9565fd034a750941722f412b0e7af219239a8daa835872f5d732a17425c8` |
| `supplement.pdf` | 16 | `5f67716e609c8a1e6505742314bf1f8c12175abb903e963ed7ed0fc754d82c32` |

- Main build after source commit: `UV_NO_SYNC=1 nice -n 10 bash scripts/build_manuscript.sh`, exit 0. The worktree has no pinned wheel at its relative path; this authorized presentation-only invocation uses no Engine import or evaluation.
- Supplement: `SOURCE_DATE_EPOCH=1792728632 FORCE_SOURCE_DATE=1 TEXINPUTS='./styles//:' nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex`, exit 0.
- `scripts/check_manuscript_freshness.py`: `Manuscript PDF is current`, matching the main hash above. The tracked verification receipt and submission metadata are updated.
- CSE prose checker on main, all section sources, supplement, all generated tables and submission aids: `Prose check passed for plugin-wide and scoped rules.`
- Final logs: no undefined references/citations, no overfull boxes, no BibTeX warnings. Three underfull-box notices remain in the supplement (water-fit paragraph and one reference); visual inspection found readable text with no clipping or overlap.
- Every page was rendered to PNG and inspected. After the last label/layout correction, changed pages were reinspected; 15 unchanged main content areas and three unchanged supplement pages were verified by pixel comparison with the inspected images. Five figures were also inspected in grayscale. Final images and comparison record are in `tmp/revision-197/verified-*-page-*.png` and `page-comparison.json`.
- Rendered abstract: **223 words**, joining line-end hyphenation; synchronized ChemRxiv plain text: 217 whitespace-delimited words. Both are below 250. Highlights: 82, 69, 69, 73, 79 characters.
- `git diff --check`: passes. Existing bibliography entries have zero field drift; the approved local script adds/removes only cited entries from the unchanged central export.

## Numerical audit and code size

`197-revision-numeric-check.json` records 825 distinct added numeric tokens across file contexts and 1949 removed tokens in 32 files. Unresolved source/rounding classifications: zero. It identifies deliberate history/bulk-table cuts, rounding, duplication removal and newly specified source/method numbers. The lookup is a traceability check; the parent’s independent scientific review remains required. The companion Markdown explains the physical sources and arithmetic reductions. No retained result or hashed input changed.

Gross executable additions against the starting commit: **195 table-generator lines + 41 figure-generator lines = 236**, below 400. Deletions do not offset additions; literal data rows/multiline statements are counted conservatively. No test code was added.

## Verified R5 disclosure

Bates and Pinching (1951), Zotero parent `TAE3BGEB`, PDF `A9H4U73D`, **Eq. 10 and Table 2, printed p.351**: pK = 2677.91/T + 0.3869 + 0.0004277T. Böttinger (2008), PDF `TJCRKTFQ`, **Table 5, printed p.138**, retains this law for MEA reaction IV. The selected coefficients are taken directly from the unchanged serialized parameter record; they already include the total enthalpy shift.

| T (K) | Source pK | Fitted pK | Difference | Source/fitted dissociation enthalpy (kJ/mol) |
|---:|---:|---:|---:|---:|
| 298.15 | 9.4961729056 | 10.0958410589 | +0.5996681533 | 50.54005978 / 63.48396762 |
| 313.15 | 9.0723590834 | 9.5634047933 | +0.4910457099 | 50.46497796 / 63.40888580 |

Enthalpy uses R ln(10)(A − CT²). The **+10 kJ/mol total adjustment is at its bound**; the unshifted reciprocal-temperature coefficient also changes, so that bound alone is not the full departure. The printed disclosure rounds to +0.60/+0.49 pK and 50.5→63.4 kJ/mol at 313.15 K. The old source-declaration Eq. 7 locator is preserved in hashed input and corrected only in presentation. Table 2 does not support a uniform ±0.0014 pK uncertainty.

## Staged deposit and unresolved scope

The existing main-checkout directory `tmp/joint-design/a7-data-release/` is updated, including byte-identical `data/manuscript/density-210.csv` and a full-precision 73-row column-wise paired phase CSV, current sources/displays, README, `manifest.json` and `SHA256SUMS`. Nothing was published. Final file counts/checksum verification are recorded in `tmp/revision-197/deposit-check.json` and `deposit-checksums.log`.

The exact fixed reference-pressure grid is supplied and its 0.50/0.80/0.95 ratios are verified. The historical calculation first producing those reference pressures is untraced; the manuscript correctly identifies them as design inputs rather than bubble pressures generated by either current fit. This is the material provenance limit for C2.

Separate Hilliard-model, Kent–Eisenberg and Faramarzi comparison rows remain optional omissions. Central bibliography capitalization/chemical typography and the Chase “−1” metadata field remain uncorrected; local hand-editing was not used. No R5-fixed fit, computed isotherm or Kim–Svendsen heat comparison was made, per D1. Phase evidence stays at 313–333 K; higher-temperature work belongs to #201. DOI publication and restricted wheel access are submission actions, not completed publication claims.

The parent runs GPT-6 Astra on numbers/claims and Opus on the reader’s story, then applies their accepted corrections and merges. No push, merge, PR, Overleaf synchronization, GitHub comment or submission occurred here.

## Finding-by-finding disposition

| Item | Disposition | Implementation or reason |
|---|---|---|
| C1 | Applied | Descriptive fit names; removed development labels, paths and hashes from rendered text and submission prose. |
| C2 | Applied with changed wording | Explicit tangent-plane criterion, starts, solvers, tolerances, finite transfers and numerical-error formulas; exact pressure design supplied. Historical origin of its reference pressures is untraced, so they are identified as fixed design inputs. Engine source at the retained commit and Michelsen §2. |
| C3 | Applied with changed wording | Quantitative model table with counts where established, reported errors, fitting roles and source locators. Missing aggregate statistics are stated rather than invented. Actual source tables govern the values. |
| C4 | Partly applied; remaining rows not done | Added Hessen, Aronu, Téllez-Arredondo and Neumann; corrected Böttinger, Zhang and Baygi. Separate Hilliard-model, Kent–Eisenberg and Faramarzi rows were not added because their full estimation/results evidence was not established in this revision. |
| C5 | Applied | Contribution is the explicit-ion application and paired property/phase-search comparison; multi-property fitting is acknowledged as established. |
| C6 | Applied | Abstract rewritten, with the phase range as the leading stated limitation; no “feasibility” claim. |
| C7 | Applied | Selected-fit AARDs are explicitly attributed to the selected fit. |
| C8 | Applied with changed wording | Rounded narrative and comparison statistics; exact state-design and reproduction quantities retain necessary precision. Full precision remains electronic. |
| C9 | Applied | Consolidated the general qualifications in §5.6, retaining the four scope statements specifically required by D1. |
| C10 | Applied | Author–year source names and Böttinger spelling in generated figures; source codes removed from printed tables. |
| C11 | Applied | Source/species marker shapes, fitted/open membership and ≥8 pt legends; grayscale inspection completed. |
| C12 | Applied | Charged-species typography, carbonate axis and matching marker legend fixed in the figure generator. |
| C13 | Applied with changed wording | Retained the paired six-panel comparison in a smaller layout; removed the tiny note, clarified fills/shapes, fits, composition and separately counted state. |
| C14 | Applied | Five-column parameter table, rounded values, mathematical minus signs/bounds, conditional errors and one-page placement. |
| C15 | Applied | Removed historical inventory and six-fit history; bulk CSVs staged; compact summaries and 10×10 lower-triangular correlations printed. |
| C16 | Applied with changed wording | Source/locator, fitted, assumed or derived provenance for parameters; earlier water/permittivity estimates and IAPWS documented. Unverified fixed inputs are explicitly model assumptions. |
| C17 | Applied under D4 | Future Zenodo deposit, DOI added at submission, restricted Engine wheel access for referees. Publication/access arrangements remain submission actions. |
| T1 | Applied with changed wording | R5 pK and enthalpy departures verified; Eq. 10 locator/reference added. Böttinger retention is stated; the reviewers’ unsupported “Zhang kept Bates fixed” assertion is omitted. |
| T2 | Applied under D1 | Current 313–333 K scope leads the limitations in abstract, §5.1, §5.6 and conclusion. No #201 results written. |
| T3 | Applied | Explicit 9.7292821 mol MEA / 76.9751925 mol water phase-feed basis, including extensive Gibbs differences. |
| T4 | Applied | Total enthalpy, neutral calorics, water extrapolation, reaction contributions, equilibrium heat-capacity derivative and mass conversion specified. |
| T5 | Applied; refit not done | Six active bounds, compensation and conditional interpretation explained; no new parameter fit authorized by D1. |
| T6 | Applied | Three fits and changed bounds defined in §4.1; +0.45% cost and threshold-sensitive 47/47→44/47 comparison stated. |
| T7 | Applied with changed wording | Water-rich versus amine/ion-rich split described; limited to lack of experimental confirmation in the read homogeneous-liquid sources, avoiding an unsupported universal absence claim. Neumann §4.2. |
| T8 | Applied under D1 | Pressure deviation panel from retained values; no computed isotherms. |
| T9 | Applied | Removed fixed-height figure padding and unnecessary break before references; final pages inspected. |
| T10 | Applied | Heat scales in kJ/mol, explicit molar analytical-feed objective versus source mass conversion, fractional weights. |
| T11 | Applied | Table 5 retained, tolerances justified in §4.1, first restricted-fit column removed. |
| T12 | Applied | NMR/AARD/RMSE/eNRTL and residual energy defined, reaction-coefficient units and data domains added, nomenclature expanded, comparison abbreviations spelled out. |
| T13 | Applied | Matin observation approximation and reported disagreement with NMR stated. Matin pp.6615–6617. |
| O R18 | Applied | Densities are calculated without translation; 44/47 within 2s. |
| O R19 | Applied | Loaded-density cost 0.566/148.9 = 0.38%, with weighting rationale. |
| O R20 | Applied | Cai cost share and 1.79 K error discussed; Baygi Table 3 comparison qualified by operator and association scheme. |
| O R21 | Applied | Aronu identified as the 15/45 wt% comparison source. |
| O R22 | Applied | NMR dilution basis and <10% quantitative reliability qualification explained. Jakobsen sample preparation and Matin p.6616. |
| O R35 | Applied | Removed 153-quantity replay statement from the manuscript. |
| O R44 | Applied | CO2 parameters attributed to Gross–Sadowski Table 1. |
| O R45 | Not done under D1 | No Kim–Svendsen heat comparison; untested temperature dependence stated. |
| O R42 | Applied | Section renamed “Experimental data.” |
| O R47 | Applied | Running-head CO2 subscript fixed. |
| O R48 | Not done | Local bibliography copies the approved existing central export unchanged. Central title capitalization/chemistry metadata and the Chase “−1” field remain for correction through the source workflow; no hand-edit of the generated bibliography. |
| O R49 | Applied | “License” used. |
| O R40 / N R25 | Applied | Introduction grouped by thermodynamic approach and aim stated earlier. |
| A R7 | Applied | Density-scale equation, source inputs and qualifications tabulated. |
| A R17 / S R21 | Applied | Heat sign, initial solvent, added-CO2 basis and feed enthalpy specified in text/caption. |
| S R4 | Applied | Explicit water/solute activities, fugacity coefficients and molality conversion. |
| S R5 | Applied | Ceres method, exact derivatives, scaling, tolerances and bound rationale described from retained declarations. |
| S R24 | Applied | Carrier-gas omission and partial-pressure/bubble calculation mapping explained. |
| N R19 | Applied | Nasrifar Eq. 12 described directly; no “lumped ions” assertion. |
| N R24 | Applied with changed wording | Printed Arcis series compared at nearby, unequal loadings; no pressure-only attribution. Arcis Table 5, pp.3355–3356. |
| N R26 | Applied | Highlight rewritten in plain language; all five within 85 characters. |
| N R23 | Applied | Size-probe sentence removed from main discussion; retained methods/evidence remain in the supplement for the bound rationale. |
| A R21 | Applied | Historical nine-of-ten carbonate sentence deleted; all ten retained. |
