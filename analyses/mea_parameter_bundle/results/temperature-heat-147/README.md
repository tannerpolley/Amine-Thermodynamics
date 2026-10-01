# Issue 147 — source admission and freeze (phase A)

This record fixes source rows, signs, uncertainty meanings, reaction laws and
continuations before any MEA calculation. It does not qualify an Engine wheel,
solve equilibrium, fit mixture parameters, or change the adopted parameter set.
The owner-approved issue sections 3/3.1/4.2/5.2/5.3/6 govern these choices.
Independent delivered source review remains required before qualification.

## Calorimetry

Arcis 2011, DOI `10.1021/je2002946`, Zotero `LJKBNXS9/UAIPQMND`:
Table 5 is on printed p.3356 (PDF p.6); Table 7 is on p.3358 (PDF p.8).
All 178 rows are retained in
`data/reference/MEA/observations/calorimetry/Arcis_2011_calorimetry_30wt.csv`.
Stable IDs contain DOI/table/temperature/printed pressure/block row ordinal;
repeated loadings remain separate rows. Both printed heat columns are
**−ΔsolH**, verified visually. Negative exothermic per-CO2 targets are
−1000 times those printed magnitudes. Per-MEA/per-CO2 values use the same
calorimetric signal (Eq.2, p.3353), not independent observations.

| T/K | p/MPa | All rows | α≤0.45 | Required | Report-only |
|---|---:|---:|---:|---:|---:|
|322.5|0.51|18|8|8|10|
|322.5|1.03|21|6|6|15|
|322.5|5.16|38|7|0|38|
|372.9|0.54|36|13|0|36|
|372.9|1.03|21|5|0|21|
|372.9|3.07|14|4|0|14|
|372.9|5.13|30|9|0|30|

The 14 required rows span α=0.087–0.448 and 0.183–0.405. Every required
row satisfies the source-derived Table 10 separation α+uα<s−us; this is
not independent solubility evidence. Required endpoints declare one reacting
liquid, but Engine bubble-separation and feed-root checks are still pending.

All 82 rows in >2 MPa blocks are quarantined/report-only. Section 3.1,
p.3356 names 5.13 MPa mixing difficulties; Conclusion p.3361 warns about
underestimation above 2 MPa at low loading. The 5.16/3.07 MPa disposition
is conservative; no source restoration cutoff exists. All 372.9 K rows
remain outside the R2/R4 representation admission interval, even if clean.
Arcis and Mathonat remain one conservatively linked reserved apparatus block.

QA: `pdftotext -layout` extraction was compared with a separate manual
transcription from `pdftoppm` page images: **178/178 rows, 1068/1068 numeric
cells, seven pressure/temperature blocks, zero mismatches**. See
`arcis-image-recheck.csv` and `arcis-extraction-check.json`. This is a second
transcription by the implementation agent, not an independent delivered review.
Printed dependent-column rounding/inconsistencies were retained, not repaired.

Vinjarapu 2024, `MSICA5ZB/CE8AP5BM`, Table 4 PDF p.7 rows 1–8:
**eight calibration observations, four loading-level groups**, integral 0→α,
313.15 K and 1.734 MPa. Targets in J/mol CO2 are
−80000, −79000, −85000, −81000, −84000, −82000, −84000, −83000;
printed uH values are 3000, 3000, 4000, 4000, 3000, 6000, 3000, 3000.
Loading uncertainties remain separate. These are declared scales, not known
one-standard-deviation errors. The existing 21-row source CSV is unchanged;
`heat-source-admission.json` assigns eight calibration and 13 report-only roles,
retains duplicate links, and records all conditions. The eight rows and their
six numeric columns were checked against the image (48 cells; zero mismatches).
No combined-ledger or per-MEA duplicate enters the calibration denominator.

## Source laws

`source-laws.json` owns numerical coefficients; `source-law-admission.json`
owns directions, references, domains, methods and limits. `r5-residuals.csv`
retains all 13 raw and scaled residuals; `representation-errors.csv` retains
R4/R2 source and represented values/enthalpies on the admission grid and exact
diagnostic temperatures. Source approximation errors are not measurement errors.

R5 option (a): one joint scaled linear least-squares solve, B=0, centered at
313.15 K, seven Kim Table 7 Exp ln Ka and six Table 12 MEA Exp heat rows.
Scales are ln(10)·0.02 and 0.025·Exp heat in J/mol, row weights one, no family
normalization. Dissociation heat is positive, reverse to exothermic protonation.

- L0 = −20.83336019500154; C = 33.42398310259077;
  D = −0.045427685333101375 K⁻¹.
- A = −198.68469292395895; Engine-native a = −6.607680532940861.
- ln Ka scaled RMS 1.032711426, maximum |r| 1.792571832.
- Heat scaled RMS 0.773907290, maximum |r| 1.441254878.
- Both families and every row pass the factor-two admission allowance.
  Largest coefficient difference from rounded readiness check values is
  4.11×10⁻¹¹ (A). This is a new source-data representation, not the printed
  Kim Table 5 vector or a verified published correction.

R5 measured constants: 298.15–363.15 K; measured heats: 298.15–393.15 K.
The unchanged lower/upper constant continuations are explicitly admitted to
293.15/393.15 K. Missing covariance and dilute-state assumptions remain.

R4: one equal-weight four-term representation of the converted Aroua Eq.14
law at exactly 298+5j K (j=0…6), centered at 313.15 K. The existing
`verify_temperature_reference.py:water_reference` density function was reused
without importing its Engine callers; its temperature derivative was retained.
On 293.15–353.15 K, maximum errors are **0.000138469338 ln K** and
**0.014196250 kJ/mol**, passing 0.002/0.15. Measurements remain limited to
298–328 K; agreement of a numerical representation does not extend that domain.

R2: the #140 four-term representation is reused unchanged, including original
`source-fit.json` SHA-256
`6fd269cd48ab3027b59af2d4b3f4b5048dadc80662a30777661f61c6bdb0dadd`
and the amended `source-admission.json`. Maximum errors over 293.15–353.15 K
are **0.001344023018 ln K** and **0.107140696 kJ/mol**, passing 0.002/0.15.
The combined CO2+H2CO3 pool and inherited mapping assumptions are unchanged.

|Law|T/K|Represented−source ln K|Represented−source ΔH/(kJ/mol)|
|---|---:|---:|---:|
|R4|372.9|−0.000636563434|−0.045267819|
|R4|393.15|−0.001823632530|−0.103834171|
|R2|372.9|+0.001235686151|+0.416516658|
|R2|393.15|+0.015913506574|+1.483732053|

All continuations above 353.15 K for R2/R4 are report-only. In-domain
representation limits are not claimed there. R1/R3 and their inherited
mole-fraction-to-molality conversions are unchanged; Edwards lineage remains
incomplete. Engine owns source-reference conversion and caloric completion;
there is no second 55.51 factor or local ionic caloric equation.

## Reproduction and freeze identity

The **450 gross added executable-line ceiling** is counted from implementation
base `76ea465fe1ede72257a809d04fc986489c5267f3`, amended **2026-10-01** in
issue #147 §10 from design base `b58e4d7ff4dc4aff0ef072df85b1c2c8019f9d90`.
Phase A's own additions are **120 lines**, including comments/blanks, all in
`source-laws.py`; **330 lines remain** for subsequent #147 phases. The following
**262 inherited unrelated additions are excluded** from the #147 ceiling:

- `analyses/mea_parameter_bundle/results/concentration-transfer-137/experiment.py`: 250.
- `.codex/environments/setup.sh`: 5.
- `analyses/mea_parameter_bundle/scripts/compare_engines.py`: 6.
- `analyses/mea_parameter_bundle/scripts/render_regression_overview.py`: 1.

The 120 own lines meet the phase-A source/unit allocation. The script reuses
NumPy, not a new optimizer or runtime dependency. No executable tests/fixtures
were added. The source-only S1 job
ran once under a 60 s external cap with single-threaded BLAS; numerical work
elapsed 0.01449 s. No second source-law solve was run. After execution,
extraneous temperatures above 393.15 K from a broad Wagner temperature
inventory were removed by data-only curation; coefficients/weights/grid were
unchanged. Timing/environment metadata moved to the admission record.
`source-law-admission.json` identifies the executed producer hash;
`inputs.json` identifies the final reproduction script hash.

`inputs.json` freezes input/PDF/output hashes and row-scoped identities for
shared inventories. Whole shared-file hashes are captured provenance, not a
requirement that unrelated #152 rows remain unchanged after integration.
`SHA256SUMS` includes the written files, including `inputs.json`.

Primary material read here: Arcis methods/results/quality limitations and
Tables 5/7/10; Vinjarapu methods/integral definition/results and Table 4;
Kim methods/estimation/results and Tables 5/7/12; Aroua methods/results,
Eqs.1–2/14 and Table 3; PB p.1015 Eq.13/Table 3 and nearby source assessment.
Their numerical tables/equations were checked against rendered primary pages.
The worktree has no literature shelf; relevant sources were read as existing
Zotero PDFs. No conversion, source acquisition, library write or Mathpix use.

Remaining work belongs to the parent: independent delivered source review,
#152 corrected-input integration, immutable-wheel preparation and qualification.
No training-target, pressure/species, qualification or adopted-record file was
modified by this phase.
