# MDEA–H₂O–CO₂ source tables

Published CO₂ solubility tables for aqueous N-methyldiethanolamine (MDEA), transcribed for
issue #126 (MDEA–CO₂–H₂O ePC-SAFT). Values are kept verbatim as strings in the source units;
nothing is converted, rounded or derived. `sources.json` owns citations, Zotero keys, PDF and
CSV SHA-256 hashes, verbatim captions, stated uncertainties with page locators, and the
transcription check.

| File | Source | Rows | Issue #126 role |
|---|---|---|---|
| `Kuranov_1996_CO2_MDEA_total_pressure.csv` | Kuranov et al. 1996, Table 2 (PDF p.2, printed p.1960) | 82 | Fit set |
| `Ermatchkov_2006_CO2_MDEA_partial_pressure.csv` | Ermatchkov et al. 2006, Tables 1–3 (PDF pp.2–3, printed pp.6082–6083) | 101 (39 + 30 + 32) | Held out: reported, not gated |
| `Hsieh_2007_MDEA_relative_permittivity.csv` | Hsieh, Chen & Li 2007, pure MDEA, via the NIST ThermoML record (paper not in Zotero) | 6 | Model input: MDEA permittivity line in Uyan Eq. 5 |

## Bases and units

- Molality: stoichiometric (overall) molality m̄, mol per kg of **water**, in both papers.
- Temperature: K as printed. Neither paper names a temperature scale. Kuranov prints a
  temperature for each row; Ermatchkov gives one per table, taken from the caption
  (313.15, 353.15, 393.15 K, ±0.1 K).
- Kuranov pressure: **total pressure** at the bubble point (synthetic method). The printed column
  `10(p) (MPa)` is 10 × p/MPa, so p/MPa = value/10 (the value equals p in bar). Stored as
  `ten_times_total_pressure_MPa`.
- Ermatchkov pressure: **CO₂ partial pressure** in kPa from headspace gas chromatography, not
  total pressure. The printed `±` uncertainties of m̄CO₂ and pCO₂ and the reproducibility
  ΔpCO₂,repr (standard deviation over 3–8 repeats) have their own columns.

## Coverage

- Kuranov: m̄MDEA 1.9938 (313 K) or 1.9493 (333–413 K) and 3.9707 (all temperatures), about
  19 and 32 mass % (computed here, not printed); isotherms near 313, 333, 373, 393 and 413 K;
  m̄CO₂/m̄MDEA up to 1.316. Four rows have m̄CO₂ = 0 (CO₂-free solvent pressure at 393 and
  413 K); they are included in the 82.
- Ermatchkov: m̄MDEA about 2, 4 and 8 mol/kg (1.905–8.441) at 313, 353 and 393 K;
  m̄CO₂/m̄MDEA 0.0028–0.784; pCO₂ 0.12–69.3 kPa.

## Locator columns

`source_table`, `source_pdf_page`, `source_printed_page` and `source_row` (1-based within the
table). Kuranov's table has two side-by-side column blocks: `source_row` 1–41 is the left block
and 42–82 the right block (`source_table_half`, `source_half_row`). `source_series` labels the
MDEA molality and isotherm; Ermatchkov prints no block headings, so its about-2/4/8 block label
is inferred from the printed m̄MDEA.

## Caveats

- Rows that fail a consistency check are flagged in `consistency_flag` and kept as printed:
  four non-monotone Kuranov pressures (source_row 5, 9, 48, 58; row 58 is 9.4 % below its
  lower-loading neighbour); one Ermatchkov loading inversion between different MDEA molalities;
  18 Ermatchkov rows whose reproducibility exceeds the stated pCO₂ uncertainty.
- 33 Ermatchkov rows lie below 7 kPa, the lower end of the stated 7–70 kPa calibration.
- Ermatchkov 2006 (p.6085) corrects the temperatures of Pérez-Salado Kamps et al. 2001 by
  +0.6/+1.2/+1.8 K at 313/353/393 K. It states no correction for Kuranov 1996 or for its own
  Tables 1–3. The corrected Kamps 2001 data (Ermatchkov Table 6) are not transcribed here.
- Both authors' MDEA purity is below 99 % (Kuranov ≥ 98 mass %, Ermatchkov ≥ 0.985 mass fraction).
