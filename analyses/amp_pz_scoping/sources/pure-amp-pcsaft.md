# Published neutral AMP PC-SAFT set

Verified on 2026-10-29 for #229. An applicable **neutral** PC-SAFT set exists;
its use in the reactive electrolyte model is not yet qualified.

Ayad et al. (2023), DOI [10.1021/acs.jced.2c00767](https://doi.org/10.1021/acs.jced.2c00767),
Table 5, p.2797 (PDF page 9), agrees digit-for-digit with Pakravesh & Zarei
(2025), [Supporting Information](https://acs.figshare.com/articles/journal_contribution/27930361),
DOI 10.1021/acs.jced.4c00390.s001, Table S1, p.2. SI ref.4, p.75,
identifies Ayad. Both tables were checked visually against the PDFs.

| Quantity | Value | Units |
|---|---:|---|
| m | 3.1552 | dimensionless |
| σ | 3.4676 | Å |
| ε/kB | 237.94 | K |
| εAB/kB | 3526.15 | K |
| κAB | 0.0058 | dimensionless |

Ayad §3.1, p.2794, explicitly uses 2B: one oxygen site and one hydrogen site.
This is an effective two-site association model; it is not a count of all
chemical donor/acceptor atoms. The parameters were fitted to the paper's
liquid densities and literature vapor pressures (Ayad §4.5, p.2800, ref.66).
Measured AMP densities cover 303.15, 313.15, 323.15 K at 0.1 MPa (Table 2,
p.2790). Table 6 p.2797 reports fitted density AAD=0.0210%; that is calibration,
not independent validation. Pakravesh SI Table S3 p.4 gives broader comparison
domains; these must not be relabeled as Ayad's fitting domain.

## Association-volume convention and remaining limit

Ayad §3.1 delegates detailed equations to refs.58,59,63 rather than printing
the association-strength expression. Ref.59 is Gross & Sadowski (2002),
DOI 10.1021/ie010954d, §2, pp.5511–5512; its Eq.3 uses σ in the unlike-volume
combining rule. Its five parameters and effective volume terminology agree
with Ayad, but it too refers the association expression to earlier SAFT work.
The inspected passages do **not explicitly settle** whether the implemented
pure association prefactor is κσ³ or κd(T)³. The usual σ-based interpretation
is a candidate, not a verified author-implementation fact here. No constant
volume conversion is adopted. Settle this from the defining expression or
a successful source-model reproduction before numerical Build.

## Reproduction-check definition (not executed)

1. Bind the five printed values and the two unlike sites. Declare the exact
   association-strength expression and temperature-dependent segment diameter.
   Record any conversion to Engine quantities explicitly; do not refit AMP.
2. First compare the original source convention against Pakravesh SI Table S8
   p.19: pure AMP saturation pressures in Pa. Selected transcription:
   347.5 K → 1872.47; 354.3 → 2934.43; 392.3 → 19992.69;
   423.0 → 65312.60; 452.0 → 162508.39. These are **calculated PC-SAFT
   values**, not measurements or PρT-SAFT-HR results. No aqueous or ion model
   belongs in this check. Source agreement would verify numerical convention,
   not physically validate the reactive model.
3. Check pure liquid density at 0.1 MPa against Ayad Table 2: 303.15 K →
   927.0 kg/m³; 313.15 → 918.6; 323.15 → 910.1. Expanded measurement
   uncertainty is 0.0005 g/cm³=0.5 kg/m³ at 95% confidence (Table 2 footnote,
   p.2792). Report per-point residuals and compare the reported 0.0210% AAD;
   these are calibration rows. Source table rounding and parameter rounding
   preclude treating its AAD digits as exact implementation tolerance.
4. For saturated-liquid density, retain a source-convention calculation on
   the same saturation grid as the independent numerical comparator before
   comparing Engine output. Table S8 does **not** tabulate AMP saturated-liquid
   density; its density columns belong to MEA. No AMP density oracle is
   invented. An approved reference implementation or original author values
   are still required for this part.

Owner must approve numerical reproduction tolerances after reference precision
and conventions are resolved. No Engine calculation, neutral fit, caloric
qualification or parameter promotion was performed in #229.

Zotero: Ayad parent `PX8NU8BD`, PDF `SSBW7YJ5` (18 pages); Pakravesh existing
parent `ABY3LIRG`, main PDF `TTAMHITN`, newly attached SI `467677SZ` (76 pages).
Gross 2002 existing parent `2AJYEZS6`, PDF `UGT3UV2L` was read; no new item.
