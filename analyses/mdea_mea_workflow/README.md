# MDEA–CO₂–H₂O preparation for issue 222

Stage 1 is retained below. The owner authorized stage 2 on 2026-10-28.
Stage-2 inspection found an undefined heat observable before any joint fit.
The earlier preparation descriptions below retain their stage-1 meaning.
The useful results are the pure-MDEA association-volume conversion, the
30-point dielectric fit, eight-species admission for both ion conventions,
and the two-column pressure sensitivity probe. These are numerical preparation
and calibration evidence, not a physical validation or a transfer verdict.

The [notebook](notebook.qmd) records quantities, interpretation and limits.

## Stage-2 heat definition awaiting Design

The [retained issue and owner freeze](inputs/stage2-issue-222.json) authorize
the seven starts on main `4835dfd`. The
[heat-definition evidence](results/stage2-heat-definition.json) records the
remaining question: which model loading or loading interval represents
Merkley's below-saturation slope?

Merkley 1987, Results, printed pp.439–441, obtains the Figure 3 heat from a
through-origin slope of heat per mole MDEA against loading below saturation.
The retained twelve markers specify no loading or loading interval: eight
enter the frozen fit, four are outside-fit comparisons, and six have the
declared alternative pressure. The paper's experimental loading independence
does not specify a loading-independent model observable. The reused MEA
`fit_observations.py::heat_items` calls `reg.addition_enthalpy`, which requires
two equilibrium endpoints and a positive added amount. Neither a finite
loading nor a zero-loading limit has been substituted.

The live Merkley PDF and retained table hashes match stage 1. All twelve
installed Engine wheel files match the pinned wheel, SHA-256
`0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`.
No joint optimizer, representative-endpoint selection, outside-fit assessment
or follow-up has run. A1–A4 and B1–B3 remain unevaluated; neither variant has a
pass or fail verdict. This is an input-definition finding, not a physical or
numerical result. The notebook has no new stage-2 results to summarize.

The owner or Design must define the Merkley model observable while preserving
the frozen roles, pressures, scales, weights and coordinates. No MDEA outcome
falsifies the MEA bicarbonate value; corrected Kamps remains outside the
follow-up criterion. The MEA parameter record and manuscript are unchanged.
[Input hashes](inputs/hashes.json) identify calculation inputs, source tables,
and the reused MEA methods. [Runtime identity](inputs/runtime.json) verifies
installed package files against the immutable wheel. [Source provenance](../../data/reference/MDEA/stage1-sources.json)
owns source keys, PDF keys/hashes, locators, units, bases, uncertainties,
transcription hashes and remaining source gaps. No source observations change role.

| Item | Disposition | Retained evidence and remaining criterion |
|---|---|---|
| (a) Ten transcriptions | Retained; owner freeze pending | 338 observations; both density and Merkley retained. Explicit scale and pressure proposals below. Carson corrected to cumulative integral heat; printed numbers preserved. |
| (b) Association volume | Complete, owner accepted | κ = 0.11800686; pressure AARD 1.34914%, density AARD 0.00525150%. Unconverted κ = 0.123858 gives 8.38332% and 0.0339482%, respectively. |
| (c) Ideal gas | Complete | Cubic maximum deviation 0.022213% over 293–423 K; h = s = 0 at 313.15 K. Independent EOS comparison at 298.15 K differs by −14.79%; uncertainty unquantified. |
| (d) Dielectric coefficients | Complete | 0.8630669729 L/mol, 1121.773473 K; AARD 3.86106%, cost 318.265. Alternative 0.28087913 L/mol, 2793.648 K; AARD 3.91286%, cost 328.265. MEA larger-volume convention selects the former, also lower cost. Start-1 densities, MDEA–water k = 0; mean deviations −8.1% at x=0.2, +4.7% at x=0.6, −3.4% pure. Absorber x≈0.04–0.13 lies below measured x≥0.2; at 393 K the minima differ by 1.87% at x=0.2 and 6.69% pure. |
| (e) Admission | Complete for stage 1 | Both full parameter mappings and MDEA ideal-gas record admitted; unloaded and charged liquid terms retained; native neutral selection verifies caloric anchors. Ionic reference completion remains conditional on (g). |
| (f) CO₂ coordinate | Complete, owner selected | k(MDEAH⁺–CO₂) selected, k(MDEA–CO₂)=0. Raw norms A 4.99072 vs 0.744984, B 9.42712 vs 0.0107344; both dimensionless k. |
| (g) Original reaction basis | Complete | Kamps–Maurer 1996 Eq. 12 (Zotero THBMMB2G) is the molality-scale law for MDEAH+ ⇌ MDEA + H+; Uyan's mole-fraction law equals it shifted by −4.0165 to within 0.0019 in ln K over 278–368 K, and pK_m = 8.551 at 298.15 K. Use above 368 K is extrapolation. [Check](results/reaction-basis-kamps-maurer.json) |


The ten transcriptions contain 338 observations (including twelve figure points),
not 338 admissible fitting targets. Figure-point uncertainty and source
uncertainty remain distinct. Repeated source rows and suspect values remain.
Derks Table 1 reports “room temperature,” without a numerical temperature;
it remains unscored. Its concentration basis is kmol/m³ in an initially
2 kmol/m³ MDEA solution (PDF 5467GXJK, p.5, printed p.603).

## Reproduction

Use `/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I`
with the worktree script path. Run numerical scripts with `nice -n 10`.
There is no worktree environment and no source-checkout runtime import.

Run, in order:

1. `scripts/transcribe.py`, then `scripts/digitize_merkley.py` for the ten source tables.
2. `scripts/prepare.py` for the association conversion and installed-wheel identity check.
3. `scripts/dielectric.py` to fit the two dielectric coefficients and finalize both start-1 documents.
4. `scripts/source_checks.py` for the ideal-gas cubic and interim reaction-basis checks; `scripts/source_arithmetic.py` for unconverted κ, Carson arithmetic and source-table hash updates.
5. `scripts/admission_probe.py`, then `scripts/probe_summary.py`.
6. `scripts/numerical_checks.py 0.001` for the centered derivative check, then `scripts/shared_reference_checks.py`.
7. `scripts/retain_inputs.py` to verify identities and retain source identities and input hashes without duplicate tables.

The digitizer uses the installed CSE XY helper, unchanged; its hash is in
`inputs/merkley-calibration.json`. OpenCV 5.0.0.93 was installed only under
`/tmp/mdea222-deps`, outside either environment; reproduce that disposable
helper dependency with `uv pip install --target /tmp/mdea222-deps --no-deps opencv-python-headless==5.0.0.93`.
The source page images were rendered by `pdftoppm` at the commands recorded
in the calibration and units records; they are retained, not regenerated by fitting.
`numerical-checks-1e-4.json` preserves the initial small-step derivative
check. At that step the small B neutral derivative had relative error
1.2774 × 10⁻⁵. At 10⁻³ it is 1.1071 × 10⁻⁶; the other three derivatives
also meet 10⁻⁵. This is consistent with cancellation in the smaller difference;
it does not establish a defect in the exact native derivative.

The saturation functions and native observation/coordinate declarations reuse
`mea_association_volume.py`. Pressure observations and exact coordinate
differentiation use the declarations in `fit_observations.py`; no optimizer
is invoked by the probe. The dielectric reduction follows
`fit_campaign.py::stage5_study`, extended from its single-temperature linear
reduction to least squares for two coefficients across the six Hsieh temperatures.
The density and permittivity equations are replayed by the installed library.

Before stage 2: (g) is resolved (2026-10-28); freeze the proposals for (a), obtain delivered evidence
review, then obtain the owner's issue comment freezing roles, scales, weights,
bounds and starts. The nine-coordinate fits, three starts per variant,
outside-fit assessments, phase searches, identifiability profiles and
sensitivity/control refits are all stage-2 work. Neither the MEA record nor
the manuscript has been changed. No Zotero writes, push, or merge occurred.

## Owner-freeze proposals

These are proposed residual scales and state assignments, not source-reported
standard uncertainties, and do not authorize stage 2.

- **Loaded density:** propose uρ,j = **0.001 ρobs,j** (kg/m³), and uα,j =
  **0.01 mol CO₂/mol MDEA**. Use sρ,j = √[uρ,j² + (gⱼ uα,j)²], with the
  source-neighbor secant gⱼ, one-sided at endpoints, exactly as
  `data_methods.tex`, Eq. density-scale. Weiland 1998 printed p.378 describes
  hydrometer measurements and unloaded agreement within 0.1% of literature;
  it gives neither loaded-density nor loading uncertainty. The 0.1% is a
  proposed density scale borrowed from that comparison, not a measured loaded
  uncertainty. The absolute loading scale 0.01 is an engineering allowance
  for stock mixing and titration with no quantified source uncertainty.
  Both values require owner freeze; retain all 44 rows and the declared
  30–50 wt% fit / 60 wt% comparison roles.
- **Merkley:** keep all 12 digitized markers and the owner's **5% scale**
  (heat residual still uses the issue's larger-of-3-kJ/mol-and-5% rule).
  Propose **1121 kPa at 288.71, 333.15 and 388.71 K**, **1466 kPa at
  422.04 K**, choosing the common measured pressure for the first three
  temperatures. At the first two temperatures retain **156 and 1121 kPa**
  as candidates for every marker; Figure 3 gives no assignment, and repeat
  runs differ up to 9%. The higher temperatures each have only one Table 1
  pressure. The proposal is a calculation-state convention, not recovered
  source identity; report a 156-kPa alternative calculation for the six
  ambiguous markers in stage 2. Use the source's below-saturation plateau
  heat; do not invent a finite loading. At 40 wt%, 422.04 K retain text
  **−66 kJ/mol** beside digitized **−65.3 kJ/mol**, difference 0.7 kJ/mol.
- **CO₂ bound:** recommend k(MDEAH⁺–CO₂) in **[−0.5, 0.5]**, matching the
  declared ion–water bounds. This is a finite search bound, not a physical
  confidence interval; the start-1 sensitivities provide no narrower bound.
  A fitted endpoint at an arbitrary bound returns to Design under #222.

The notebook is registered in the analysis site. The presentation refresh was
attempted but stopped because `snakemake` is absent from this environment;
the HTML has not been regenerated. Numerical checks and the requested prose
checker pass. Independent delivered review remains an owner gate.

Relative to 25d0d45, executable scripts add 105 lines and remove 19,
including comments and blanks. The additions implement the accepted cubic,
native caloric admission, alternative dielectric solution, pressure provenance
and source arithmetic; the source-table copy loop is removed. Generated
values, source tables and notebook changes are separate from that count.

## Stage-1 addendum: starts and newer comparisons

Items (h) and the authorized Zheng/Sedighi portion of (i) are complete.
[Start 4](inputs/variant-A-start-4.json) is derived from `inputs/variant-A.json`.
[Declaration checks](results/start-4-declaration.json) retain the full recursive
diff, nine strict bound checks, shared component/pair byte comparisons,
installed-wheel identity, admission message and liquid-state terms.
The shared owner remains SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`.

Bülow 2021, Eq. 26 (p.6330) and Table 3 (p.6331), gives the cubic about
298.15 K. Its coefficients re-centered at 313.15 K are
`[-0.131933125, -0.001070625, -7.575e-6, 1.25e-7]`, in increasing powers
of temperature displacement. Matching the value and first derivative gives
`b = 104.9886164016 K`; the document uses `104.9886164 K` and explicitly
sets `reference_temperature = 313.15 K`. Projection minus cubic is
**+0.0105989562** at 373.15 K. Native evaluations with the slope and with
an equivalent constant k agree exactly in pressure, dispersion and residual
Helmholtz energy at 298.15, 313.15 and 373.15 K (tolerance 1e-8).
The only changes from start 1 are the four ion diameters and the MDEA–water
pair; the start-1 identifiers and metadata are retained to keep the diff
within the issue's allowed entries. This is an initial guess, not a
reproduction of Bülow's model. [Source identity](inputs/start-4-source.json)
records the live Zotero PDF and verified reading copy.

At 313.15 K and 100 kPa, the unloaded composition (0.95 water, 0.05 MDEA)
gives **43792.4928 mol/m³**; the prescribed loaded composition (0.94 water,
0.04 MDEA, 0.01 MDEAH+, 0.01 bicarbonate) gives **45580.2694 mol/m³**.
Their dimensionless residual Helmholtz energies are **−8.93473850** and
**−11.79080043**, respectively; all separate terms are retained. The largest
pressure residual is **4.30e-6 Pa**. These are numerical admission checks
at prescribed compositions, not reactive equilibrium or physical validation.

[Addendum source provenance](../../data/reference/MDEA/addendum-sources.json)
owns attachment hashes, locators, units, bases and uncertainties. The tables
remain solely under `data/reference/MDEA/`:

- [Zheng 2020](../../data/reference/MDEA/Zheng2020_stage1.csv): six pure-MDEA
  Table 4 rows (PDF p.5, printed p.3788), two at 30 wt% and four at 50 wt%,
  all at 323.15 K. Total pressure spans 0.53–4.19 MPa. Retain loading and
  positive absorption-heat magnitude per mole CO₂, with relative expanded
  uncertainty 0.05 on both; u(T)=0.01 K and u(P)=0.002 MPa. The comparison
  is the integral heat from zero loading to reported saturation loading at
  source T/P, with the model saturation loading beside it. Exclude the
  piperazine blend and all 353.15 K rows. SI Tables S1–S2 are unavailable.
- [Sedighi 2024](../../data/reference/MDEA/Sedighi2024_stage1.csv): 24 Table 3
  rows (PDF p.8, printed p.21), of which 15 at 10–50 wt% are designated for
  later outside-fit scoring. The nine rows at 60, 80 and 98 wt% remain
  unscored. Mass fraction is printed wt% divided by 100; no molarity
  conversion is needed. The pressure per row is **total 101.325 kPa**.
  Section 2 supplies 99.995% CO₂, with no inert carrier, and an atmospheric
  manometer; gas above the solution includes solvent vapor. Section 3.2
  models vapor as CO₂ + water. Compare total model bubble pressure at the
  printed loading and temperature, including solvent vapor; do not identify
  atmospheric total pressure as CO₂ partial pressure.
- Sedighi §2.2 and §4.1 (pp.16,20) describe contact to saturation, preliminary
  checks at 2.511 mL/hr, closing the CO₂ inlet when the first liquid droplet
  reaches the manometer, and maintaining pressure by mercury adjustment.
  Table 3 uses a 20-minute measurement and averages three runs. No numerical
  equilibration tolerance is given. **The source reports no uncertainty**;
  its balance accuracy and repeated measurements do not establish one.
  Printed mole columns and loading are retained separately:
  [arithmetic check](results/sedighi-loading-arithmetic.json) finds the largest
  discrepancy in row 18 (323.15 K, 20 wt%): printed loading 0.739 versus
  0.72922636 from the mole columns. No value is repaired or excluded.
- Xiao 2018 (`F3EC6J42`) and Zhang 2023 (`PU7B5G27`) each have one PDF page.
  Their attachment hashes are recorded as declared but unscored; no abstract
  transcription or digitization was performed. Full-text acquisition remains
  outside this addendum. Zhang remains designated as extrapolation by #222.

These observations retain their outside-fit roles; no predictions have been
scored. Their later statistics are supporting comparisons and do not change
the 24.2% pressure criterion. Item (i) as a four-source task remains incomplete
until the two full texts are acquired and transcribed. Stage 2 still requires
the owner's freeze and independent delivered review.

The addendum reuses `prepare.py` for document records and wheel identity and
`admission_probe.py::caloric_record` for native thermochemistry, using the
main interpreter with `-I` and `nice -n 10`. No persistent executable code is
added. The numerical record includes the original and translated polynomial
coefficients, complete input documents, state conditions and per-term outputs;
`results/numerical-checks.json` links these checks. Table transcriptions were
checked against rendered PDFs; no plotted-only observations were needed.
