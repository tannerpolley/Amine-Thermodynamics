# Part I visual pass: fix round 1

The three independent reports on `421c7e9` were read in full. This revision
applies the owner's required corrections, with science taking precedence.
It changes presentation and explanation of retained results only. No fit or
thermodynamic calculation ran. The three independent rechecks remain open.

## Required corrections

| Report item | Disposition | Result and reason |
| --- | --- | --- |
| Science 1 | Applied | Exact seven-name mapping owns the generated tables; first prose definitions state the restrictions and identify the present model as adopted throughout. |
| Science 2 | Applied | Uses the exact sodium-salt sentence, with italic name markup: Peiper and Pitzer (1982, Table 6), model-derived osmotic coefficients. |
| Science 3 | Modified | S6 uses story's reader-facing phase-search description and science's exact compiled-library sentence, as directed. |
| Science 4 | Overridden | Owner retains the existing nine-significant-figure rule. Caption states at most nine significant figures; no full-precision digits substituted. |
| Visual 1 | Applied | 393.15 K contrast against white is 4.67:1. Present-model bars have 5.22:1 fill contrast, dark outlines, and matching legend hatching. |
| Visual 2 | Applied | Figures 3 and 4 use temperature-sized circles with representative legend circles; dotted species branches have direct temperature labels. |
| Visual 3 | Applied | Figure 5 keys all three retained temperature/pressure conditions, using temperature color/size and open versus filled circles. |
| Story 1 | Modified | Defines earlier shared set by this study's 16-parameter stability-penalized calibration, shifted R2/R5 laws and separate amine-ion Born diameters. Omits the disallowed project-history clause. |
| Story 2 | Modified | Uses italic first definitions and explicit adoption, with science names and salt provenance. |
| Story 3 | Modified | Table 7 names the alternative branch using science names: zero protonated-MEA--carbamate modifies sodium-salt water--anion laws. |
| Story 4 | Applied | Table 2 points to the joint fit in Section 3.3; Table S5 says parameters of the present model. |
| Story 5 | Modified | Table 6 caption corrected. Fitted pressures are Hilliard and Jou; only the not-fitted subset spans all six sources. |
| Story 6 | Overridden | Retains the required abstract 53 + 1 basis with reader-facing language; applies the Section 4.2 replacement. |
| Story 7 | Modified | Uses story's S6 trial-phase account and science's compiled-library wording with unchanged SHA-256 prefixes. |
| Story 8 | Applied | S6 states that these phases are not relaxed to equilibrium under the present model. |
| Story 9 | Applied | Replaces penalty stage with stability penalty. |
| Story 10 | Modified | Four Böttinger and three Matin quantities: the display names both sources. Retained rule strings incorrectly call all seven Böttinger and remain untouched. |

The exact mapping, retained-record locators and confirmations are recorded in
`../source_log.md`, under Issue 347 visual fix round 1. Optional suggestions and
judgment calls were not added to scope.

## Confirmations and numerical preservation

Restriction producer `reduced_refit_338.py`, steps 4 and 5, and the retained
parameter records confirm the alternative branch. The protonated-MEA--bicarbonate
and protonated-MEA--carbamate interactions are respectively (1, -1) in F4,
(0, -1) in F4-0, and (1, 0) in F5.

Of 159 pressure observations, 47 fitted rows are Hilliard 30 and Jou 17.
The 112 not-fitted rows comprise Aronu 36, Hilliard 1, Idris 10, Jou 31,
Ma'mun 19 and Xu--Rochelle 15. The seven further-species quantities join to four
Böttinger and three Matin identifiers in the retained fitted rows; the counts
and scales agree with `objective-groups.csv`, whose source wording is inaccurate.

The heat figure has 8 observations at 313.15 K and 1.734 MPa, 8 at 322.5 K
and 0.51 MPa, and 6 at 322.5 K and 1.03 MPa. Section S6 identifies the
additional instability case by 333.15 K and loading 0.1 mol/mol. Its vapor-trial
descent ends in two liquids on re-evaluation. This is numerical evidence from a
finite phase search, not a measured second liquid or independent validation.

All 20 Table 1 coefficient displays are Decimal-equal to `421c7e9`; removing
alignment zeros introduces no value change. The nine-significant-figure
source-to-display rule is unchanged. All other numeric cells in revised tables
are unchanged. All eight figures' numerical plotting coordinates, bar values
and uncertainty intervals compare exactly before and after this round.
All 54 retained-input hashes from the preceding check remain unchanged.
See `347-visual-r1-checks.json` and the earlier `347-visual-values.json` for
machine-readable evidence and the Table 4 three-significant-figure reductions.

## Pages relative to 7f6e29e

The final PDFs remain 24 and 9 pages. At 100 dpi, main pages 1 and 6--19
and supplement pages 4, 5, 7 and 8 differ from the base PDFs. Other pages are
pixel-identical. Every changed page was inspected at full-page print scale in
color and grayscale.

| New main page | Changed content, including the preceding visual pass |
| --- | --- |
| 1 | Abstract: reader-facing 53 + 1 phase-search basis. |
| 6 | Table 1: spaced equilibrium arrows, two panels, aligned coefficients and explicit display precision. |
| 7 | Table 2: joint-fit caption and Böttinger/Matin source label. |
| 8 | Section 3.3: calibrated-set definitions and sodium-salt provenance. |
| 9 | Phase-method language; Table 3 unchanged, nearby text reflows. |
| 10 | Figure 1 serif labels from the preceding pass; Section 4.2 trial-phase explanation. |
| 11 | Figure 2: descriptive legend, serif labels, darker outlined and hatched bars. |
| 12 | Figure 3: temperature-sized circles and legend; Table 4 observation header and three-significant-figure AARD. |
| 13 | Figure 4: temperature circles/legend and directly labeled dotted branches; Table 5 Böttinger/Matin label. |
| 14 | Table 6: data-role caption and accurate pressure-source rows. |
| 15 | Figure 5: three temperature/pressure conditions and explicit circle keys. |
| 16 | Figure 6: darker 393.15 K curve; serif labels and dashes from the preceding pass. |
| 17 | Figure 7: serif labels and temperature size/color from the preceding pass; Table 7 exact names and branch caption. |
| 18 | Tables 8 and 9 unchanged; surrounding renamed comparison prose and reflow. |
| 19 | Table 10 reader-facing model names; surrounding comparison/limitations prose. |

| New supplement page | Changed content |
| --- | --- |
| 4 | Table S3: Böttinger/Matin source label. |
| 5 | Table S5: present-model caption; Table S4 unchanged. |
| 7 | Figure S1: serif labels from the preceding pass; Table S8 unchanged. |
| 8 | Section S6: trial phases, compiled-library provenance and fixed-phase clarification; shared-input wording from preceding pass. |

## Build and checks

The existing latexmk/pdfLaTeX route ran through `agent-heavy` in background
shells. Before (`421c7e9`): 24 + 9 pages and no material log/font warnings.
After: 24 + 9 pages, no overfull boxes, undefined references/citations,
missing glyphs or font warnings. All fonts are embedded Type 1 or TrueType
vector fonts; no Type 3. The main and supplement freshness validations pass.

The existing displayed-number check passes: 19 tables and 20 promoted input
identities. The deterministic CSE prose check passes. Build/check logs and both
raw layout reports accompany this handoff.

Raw layout status remains fail for main (160 findings) and review for supplement
(34 findings). Main has the existing Equation 27 calc/obs superscript
bounding-box error, conservative equation/vector warnings, and text-clearance
warnings. Eight additional warnings on page 11 arise from the hatch paths and
their bounding boxes. Color and grayscale inspection shows no clipping,
colliding text or spill outside the bars; disposition is exact/keep.
Supplement findings are text-clearance warnings. This manual disposition
does not convert the raw automated statuses to a pass.

Part II directories, entrypoints, PDFs, shared chemistry macros and all
bibliographies have an empty diff from `7f6e29e`. Part II was not rebuilt.
Read-only matches remain A3 in `tables/part2/fit-starts.tex` and
`shared-sensitivity.tex`; mhchem arrows in `sections/part2/model.tex` and
`pz-reaction-directions.tex`. The story report also notes the Part I section
locator and reaction-correlation wording in `sections/part2/model.tex:16--17`.
No Part II correction was made.
