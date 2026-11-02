# Ciftja 2014 AMP carbamate law and its conflict with Ciftja 2011

Source assessment for #238, 2026-11-02. It extends
[carbamate-law.md](carbamate-law.md) and
[carbamate-law-sources.md](carbamate-law-sources.md) (#234) and uses their
hydrolysis definition, activity identity and molality conversion unchanged.
No fitting, Engine calculation or code was run. Numbers marked *hand
arithmetic* evaluate printed equations or tables to check transcriptions; they
are not new results.

Sources read in full (methods, results, tables, figures):

- Ciftja, Hartono & Svendsen 2014, Chem. Eng. Sci. 107, 317–327, DOI
  [10.1016/j.ces.2013.12.028](https://doi.org/10.1016/j.ces.2013.12.028);
  Zotero parent `PUUFV6NX`, PDF `FBQ5R6DR` (11 pages). Equation signs were
  checked on the page images.
- Its Supporting Information `mmc1.doc` (a Word file, 3 pages: Figs. S-1, S-2,
  Tables S1–S4), from the publisher link in the Zotero snapshot `MUCDVPER`.
  It is **not attached in Zotero**: Companion has no route for attaching a
  supplementary file that is not a PDF or Markdown. Its URL and SHA-256 are in
  `pdf-identities.json`.
- Ciftja et al. 2011, `N3M32YAK`, PDF `CISK7MCE` (7 pages), re-read for the
  conflict.
- Ciftja, Hartono & Svendsen 2013, Int. J. Greenh. Gas Control 16, 224–232,
  DOI [10.1016/j.ijggc.2013.04.006](https://doi.org/10.1016/j.ijggc.2013.04.006);
  **new** Zotero parent `UA8GZ42B`, PDF `IY7MCKNF`. Ciftja 2014 cites it for
  its quantitative NMR conditions (§2.2, p.318).
- Yi et al. 2024, Sep. Purif. Technol. 350, 127924, DOI
  [10.1016/j.seppur.2024.127924](https://doi.org/10.1016/j.seppur.2024.127924);
  `SDKLQTBQ`, PDF `3YP4GUWT` (13 pages). Its supplementary information was not
  read.

## Result

1. **Ciftja 2014 gives an apparent constant with an empirical
   ionic-strength extrapolation, not a thermodynamic constant.** It is a
   mole-fraction formation ratio with no activity coefficients for AMP or
   water and no water term. Its correlation (Eq. 19) gives an apparent
   hydrolysis enthalpy of +20.8 kJ/mol at 298 K. Part of that slope comes
   from the authors' pH-based split of AMP/AMPH⁺ and HCO₃⁻/CO₃²⁻, not from the
   NMR signals alone.
2. **Tables S1–S3 hold 62 rows: 59 loaded, 3 unloaded.** These are 30 wt% AMP
   at 25, 35 and 45 °C, with measured sums x(AMP+AMPH⁺), x(AMPCOO⁻) and
   x(HCO₃⁻+CO₃²⁻), pH and NMR loading. Two 25 °C rows fail the CO₂ balance, so
   **57 rows are usable**. The split speciation and the per-row K_C values
   are not tabulated.
3. **Conflict.** Ciftja 2014 carbamate per total AMP is 4–7 times Ciftja
   2011's at matching loadings. Neither paper explains this. The 2011 data
   fail their own carbon and charge balances; the 2014 data close against
   titration. Relaxation delay does not explain the gap. A missing
   nuclear-Overhauser-effect (NOE) suppression in 2011 could explain part of
   the carbonate deficit, but not the carbamate gap; this is inference.
   **Recommendation: Ciftja 2014 Tables S1–S3 (57 rows) are the AMP carbamate
   speciation data. Exclude Ciftja 2011 from fitting and scoring.**
4. **Yi 2024 has no AMP carbamate.** AMPCOO⁻ is "neglected to simplify the
   model" (§2.1.2, p.3). It compares Ciftja 2014 HCO₃⁻/CO₃²⁻ sums only
   (Fig. 5b, p.6). Its parameter regression includes Kundu 2003 and Tong 2012 (Table 4,
   p.5).

## 1. The law

### Reaction, definition and basis

- Reaction as written (Eq. 5, p.318, headed "Carbamate hydrolysis"):
  AMP + HCO₃⁻ ⇌ AMPCO₂⁻ + H₂O. Despite the heading, it is written in the
  formation direction.
- Definition (Eq. 13, p.321): K_C = [AMPCO₂⁻]/([HCO₃⁻][AMP]). This is a
  formation ratio with **no water term**.
- Basis: mole fraction. Fig. 8's axis reads "K_C [mol fraction]" and the
  caption says "on mol fraction bases" (p.324). §3.2 reports "about 41, 34 and
  25 (mol fraction)" (p.323). Tables S1–S3 are mole fractions. For the split,
  the authors converted the data to molality, because the literature
  constants they used are molal (§2.5.2, p.320). Fig. 7 is plotted in mol/kg
  (p.324).
- Activity treatment: **apparent**. Eq. 13 uses concentrations only. Activity
  coefficients enter only the split: the AMP pKa at ionic strength I
  (Oscarson correlation, Eq. 8, p.320) and K_HCO₃⁻ at I (extended
  Debye–Hückel, Eqs. 11–12, p.321). The statement that K_C uses "activity
  coefficients estimated by thermodynamic models" (§2.5.1, p.320) is not
  reflected in Eq. 13 or Eq. 19. The conclusion calls the constants
  "estimates" (§4, p.326).

### Temperature and ionic-strength law

Eq. 19 (p.323), with signs checked on the page image:

$$\log_{10}K_C=-33.60+\frac{2493.32}{T}+10.87\log_{10}T-\frac{0.7\sqrt I}{1+\sqrt I}-16.03\,I$$

- T is in K, at 25, 35 and 45 °C only (§2.2, p.318).
- The paper says "at zero ionic strength the infinite dilution carbamate
  stability constant results" (p.323).
- The ionic-strength terms copy the form of the molal Debye–Hückel Eq. 12,
  but with fitted coefficients: 0.7 and 16.03, against 2.04 and 0.13 in
  Eq. 11.
- Fig. 8 plots I as dimensionless, over 0–0.1, with data at 0.015–0.085
  (p.324). At 30 wt% AMP and α≈0.5, molal ionic strength is several mol/kg.
  **Inference:** I in Eq. 19 is a mole-fraction ionic strength. The paper does
  not define it. With molal I, Eq. 19 would give K_C below 10⁻³⁰.
- "Zero ionic strength" means zero loading of the same 30 wt% AMP solvent. It
  does not mean AMP infinitely dilute in water. The I→0 value therefore still
  contains γ(AMP) at about x(AMP)≈0.08 and a water activity below 1.

*Hand arithmetic*, Eq. 19 at I = 0:

| T, K | log₁₀ K_C^∞ | K_C^∞ (mole fraction) | Paper, Fig. 8 / p.323 | ΔH formation, kJ/mol |
|---|---:|---:|---:|---:|
| 298.15 | 1.660 | 45.7 | ≈41 | −20.8 |
| 308.15 | 1.544 | 35.0 | ≈34 | −19.9 |
| 318.15 | 1.441 | 27.6 | ≈25 | −19.0 |

- Here ΔH = R(10.87 T − 2493.32 ln 10). The paper's "about" values are read
  off its fitted curves; they agree to within 10%.
- The ionic-strength terms do not depend on temperature, so this apparent
  enthalpy is the same at every I.
- At a typical I = 0.05, K_C(298 K) = 5.4. This is consistent with the
  log K_C = 0.56 (K_C = 3.6) that Sherman quotes (#234). Sherman's basis
  remains unverified.

### Uncertainty, as stated

The paper gives no uncertainty for any Eq. 19 coefficient. It states:

- species concentration ±0.0002 mole fraction, from the ¹³C detection limit
  and parallel samples (§2.6, p.321);
- error of order 10⁻⁴ mole fraction in the AMP/AMPH⁺ and HCO₃⁻/CO₃²⁻ split
  (p.322);
- electroneutrality error averaging about 1%, maximum 14%, at 25 and 35 °C,
  and larger at 45 °C (p.322);
- NMR versus titration loading AARD below 1.5% (Fig. 6, p.322–323);
- chemical shift ±0.2 ppm (p.319);
- carbamate uncertainty largest "at low CO2 loadings and high temperature"
  (abstract; p.323).

Fig. 8 scatter about each isotherm spans roughly a factor of two (read by eye).

### Where the temperature slope comes from

The NMR carbamate fraction barely changes with temperature. The highlights
call it "almost temperature independent" (p.317), and §3.1 reads the same
(p.322). *Hand arithmetic* on Tables S1–S3, using r_c = x(AMPCOO⁻)/[x(AMP+AMPH⁺) + x(AMPCOO⁻)]
at α = 0.45–0.55:

| T | r_c at α = 0.45–0.55 |
|---|---|
| 25 °C | 0.027–0.034 |
| 35 °C | 0.026–0.035 |
| 45 °C | 0.021–0.026 |

That is a fall of about 20% from 25 to 45 °C. K_C^∞ falls by 40% over the
same range. The rest comes from the split: free AMP and HCO₃⁻ in Eq. 13 are
computed from measured pH with the authors' pKa(T, I) and K_HCO₃⁻(T, I) laws.
Two observations follow:

- **Eq. 19's slope is model-assisted.** It carries the Oscarson/Phillips split.
  An ePC-SAFT fit to the NMR sums would instead carry its own split, from
  Hamborg AMPH⁺ and the frozen R2/R3.
- **Table 2 (p.321) does not reproduce its own split as printed.** *Hand
  arithmetic:* Eq. 9 with A = −96.482, B = 0, C = −16.5905, D = −0.0258 gives
  ln K = −198.7 at 298.15 K. Reversing the sign of C gives −9.65, close to the
  AMP pKa of about 9.7 at 25 °C; the result is then a base-10 value. The
  HCO₃⁻ column gives −10.13 at 298.15 K only if "log T" in Eq. 12 is read as
  ln T; the zero-I value in Fig. 4 is 10.33. These are printing defects in the
  coefficient table. They do not change Tables S1–S3, which report the
  directly measured sums.

### Expression in the repository hydrolysis form

Inverting Eq. 19 at I→0 gives the apparent mole-fraction hydrolysis ratio
(*hand arithmetic*, exact algebra):

$$\ln K_{h,x}^{\rm app}(T)=-\ln K_C^\infty=77.367-\frac{5741.08}{T}-10.87\ln T$$

- At 298.15 K: ln K_h,x = −3.821 (K_h,x = 0.0219).
- Apparent ΔH_h = R(5741.08 − 10.87 T) = +20.8 kJ/mol at 298 K and +19.0 kJ/mol
  at 318 K.
- This is already the `ReactionLogPolynomial` form A + B/T + C ln T.

The activity identity in `carbamate-law.md` links it to the repository
constant:

$$K_h=\frac{1}{K_C^\infty}\,
\frac{\gamma_{\rm AMP}\gamma_{\rm HCO_3^-}}{\gamma_{\rm AMPCOO^-}a_w}\Bigg|_{\text{30 wt\% AMP},\,\alpha\to0}.$$

- The γ ratio must be evaluated in the target model at the zero-loading
  30 wt% state. For ePC-SAFT that needs AMPCOO⁻ parameters, and those would
  be fitted to these same rows. **So the conversion cannot be closed without
  a circular fit.**
- On the molality scale, the apparent formation ratio at that state is
  q_m = K_C^∞ · x_w · M_w ≈ 45.7 × 0.92 × 0.018015 ≈ **0.76 kg/mol** at
  298 K. With the #234 infinite-dilution offset (+4.0165), it would be
  0.82 kg/mol.
- That is the highest value in the #234 comparison table: 2.4 times Hartono
  2020 and 15 times Xu/Silkenbäumer. Most of the excess comes from the
  steep empirical I-extrapolation. At finite I the apparent values are 1–20,
  i.e. 0.02–0.3 kg/mol.
- **The I→0 intercept is poorly determined**: it extrapolates a fitted
  −16.03·I term by about one decade.
- The temperature slope does not depend on the intercept, because the I terms
  are temperature-independent.

### Slope agreement with an independent source

| Source | Data | ΔH_h at 298 K, kJ/mol |
|---|---|---:|
| Xu 1992 / Silkenbäumer 1998 | VLE, extended Debye–Hückel; no NMR, no Kundu, no Tong (#234) | +21.2, constant |
| Ciftja 2014, Eq. 19 | NMR plus pH split; 25–45 °C | +20.8 (+19.0 at 318 K) |
| Mehdizadeh 2013 | DFT | +17.1 |
| Hartono 2020 | eNRTL fitted to VLE | +35.8 |

The first two routes are independent of each other and agree to within
0.4 kJ/mol at 298 K and 2.2 kJ/mol at 318 K. Both are apparent constants
inside their own activity treatments, so this is **corroboration, not
verification**. The temperature derivative of the ePC-SAFT γ ratio in the
identity above remains unquantified.

## 2. Speciation data

Transcription: [ciftja-2014-tables-s1-s3.csv](ciftja-2014-tables-s1-s3.csv).
It was taken from the text layer of the publisher's Word supplement, not by
OCR, and checked against rendered pages 2–3.

| Table (SI p.) | T | Rows | Loaded | Loading range (NMR) |
|---|---|---:|---:|---|
| S1 (p.2) | 25 °C | 20 | 19 | 0.08–0.72 |
| S2 (p.2) | 35 °C | 25 | 24 | 0.08–0.62 |
| S3 (p.3) | 45 °C | 17 | 16 | 0.084–0.542 |

- **Stock solution:** 30 wt% AMP from ≥97% AMP and distilled water. CO₂ was
  bubbled in; 1,4-dioxane served as reference; 5–10 mass% D₂O was added in the
  tube (§2.1, p.318).
- **Columns:** NMR loading, pH, x(AMP+AMPH⁺), x(AMPCO₂⁻), x(HCO₃⁻+CO₃²⁻).
- **Lumped species:** AMP with AMPH⁺, and HCO₃⁻ with CO₃²⁻, because of fast
  proton exchange (§2.4, p.319). CO₂(aq), OH⁻, H₃O⁺ and water are not reported.
- **pH** was measured at each temperature with a Metrohm 827 meter calibrated
  against pH 4, 9 and 12 buffers (§2.1, p.318).
- **Repeats:** the S2 note says some 35 °C samples were measured several times.
- **Table S4 (SI p.3)** gives relative integrals for all carbamate carbons at
  25 °C, with NMR and titration loadings for eight samples.
- **CO₂ balance (*hand arithmetic*).** The two S1 rows at α = 0.13 give
  (x_c + x_HCO₃)/(x_A + x_c) = 0.059 and 0.024 instead of 0.13. They look like
  exponent errors in the bicarbonate or carbamate entries, and they appear as
  the two low outliers in Yi 2024 Fig. 5b (p.6). Both are flagged
  `co2_balance_fails`. The other 57 loaded rows close to |Δα| ≤ 0.0046. That
  is an internal check only: the tabulated loading comes from the same
  integrals. The independent check is the titration agreement (Fig. 6; Table
  S4: NMR and titration within 0.02).
- **Normalization scatter (*hand arithmetic*).** x(AMP+AMPH⁺) ranges over
  0.0742–0.0922 within one isotherm, although the analytical amine is fixed.
  That is roughly ±10%, much larger than ±0.0002. The ratio r_c cancels this
  normalization.
- **Replicates (*hand arithmetic*).** Four 35 °C rows at α = 0.47 give r_c
  mean 0.0315, standard deviation 0.0028. Propagating ±0.0002 through
  r_c ≈ x_c/0.08 gives 0.0025, so the two estimates agree.
- **Count.** The data map lists a 57-row private CESAR-1 file at 298–318 K.
  The public count of usable loaded rows is also 57. Whether these are the
  same rows was not checked; nothing was read from that file.

### Usability

- **Calibration.** These are the only measured AMP carbamate speciation data
  over a temperature range.
- **Non-redundant observable.** One value per row: r_c, the carbamate per
  total AMP.
  - The AMP sum per total AMP is 1 − r_c.
  - HCO₃⁻+CO₃²⁻ per total AMP is α − r_c.
  - Neither adds independent information once α is the feed.
- **Proposed residual scale.** σ(r_c) ≈ 0.0025–0.003 absolute. It is derived
  from the stated ±0.0002 and matches the replicate scatter. Relative to r_c,
  that is about 10% at mid loading and about 30% at α ≈ 0.08.
- **Not data.** Split species (Fig. 7) and per-row K_C (Fig. 8) are
  model-assisted and only plotted. §3.2 says Eq. 19 was fitted to "the
  carbamate stability constants given in Tables S1–S3", but those tables
  contain no K_C column.
- **No independent hold-out exists for AMP carbamate speciation.**
  - Ciftja 2011 fails (§3 below).
  - Chakraborty 1986, Sartori 1983 and McCann 2011 give only upper bounds:
    about 0.1, below 0.1 and below 0.2 L/mol (Ciftja 2014 §3.3, p.323; #234).
  - Ciftja 2014's finite-I apparent values, about 0.02–0.3 kg/mol, sit near
    those bounds.
  - A temperature block, for example the 45 °C rows, could be held out to test
    a fixed slope. It comes from the same laboratory and method, so this is an
    owner decision.

## 3. The 2011/2014 conflict

*Hand arithmetic* at matching 25 °C loadings, r_c = carbamate per total AMP:

| α | Ciftja 2011, Table 2 p.618 | Ciftja 2014, Table S1 | Ratio |
|---|---:|---:|---:|
| 0.12 | 0.0020 | 0.0121 | 6.0 |
| 0.24 / 0.23 | 0.0048 | 0.0258 | 5.4 |
| 0.33 / 0.35 | 0.0044 | ≈0.032 | 7.3 |
| 0.41 / 0.42 | 0.0045 | 0.0333 | 7.4 |
| 0.51 | 0.0063 | 0.0274 | 4.4 |
| 0.62 | 0.0048 | 0.0238 | 5.0 |

### Methods compared

| Aspect | 2011 (§2, p.615; §5, pp.616–618) | 2014 (§§2.1–2.6, pp.318–322) |
|---|---|---|
| Spectrometer, probe | Bruker Avance DPX 400, 5 mm dual ¹H/¹³C | same |
| Pulse, acquisition time, delay D1, scans | 6.90 µs, 2.83 s, **150 s**, 300 (13 h) | 7 µs, 1.37 s, **40 s**, 300 (4 h) |
| NOE suppression | not stated. §1 (p.615) names inversion recovery as the anti-NOE measure; that is a T1 measurement, not decoupling | inverse gated decoupling stated (§2.2, p.318) |
| T1 check | none reported | inversion recovery; D1 > 5 × longest carbon T1 |
| Reference | 1,4-dioxane, about 5 mol% of amine | 1,4-dioxane |
| Carbamate first seen | α = 0.12 | α = 0.08 |
| Carbamate carbonyl range | 159.2–164.8 ppm, overlapping HCO₃⁻/CO₃²⁻ at 163.5–166.2 (§5.1, p.616) | 164.68–164.73 ppm; HCO₃⁻/CO₃²⁻ 162.61–166.36 (Table 1, p.320) |
| HCO₃⁻/CO₃²⁻ split | Holmes ammonia chemical-shift method | pH plus Phillips K_HCO₃⁻(T, I); 2014 says the Holmes method "was not validated for systems other than ammonia" and ignored ionic strength (§2.5.2, p.320) |
| Loading column | from weight change, compared with titration (p.615) | from NMR; titration AARD < 1.5% (Fig. 6) |

### Evidence

1. **Relaxation does not explain the gap.** Ciftja 2013 Table 1 (p.228)
   measured T1 in loaded 30 wt% AMP at α = 0.84 and 25 °C: carbamate carbonyl
   4.2 s, HCO₃⁻/CO₃²⁻ 3.5 s, quaternary C-2 2.3 s. Ciftja 2013 shows that
   D1 ≥ 4–5 T1 gives ≥98% intensity (Fig. 3, p.229). Both D1 values exceed
   21 s; 2011's is the longer one.
2. **The 2011 table fails its own balances (*hand arithmetic*).**
   - The CO₂ balance (x_c + x_HCO₃ + x_CO₃)/(total AMP) gives 0.082, 0.176,
     0.211, 0.315, 0.334 and 0.351. The stated loadings are 0.12–0.62, so NMR
     accounts for only 57–77% of the CO₂.
   - In charge balance, x(AMPH⁺) differs from x_c + x_HCO₃ + 2x_CO₃ by up
     to 29% at α = 0.62 (0.0477 against 0.0341).
   - The AMPH⁺ fraction tracks the nominal loading (0.63 at α = 0.62). The
     pH split is therefore consistent with the weighed loading, while the
     carbon integrals are low.
3. **The 2014 data close and are internally consistent.**
   - NMR and titration loadings agree (Fig. 6; Table S4).
   - In Table S4, the carbonyl carbamate carbon (4*, no attached H) and the
     CH₂ carbon (1*) differ by at most 0.03 in relative integral at every loading (ratio 0.83–1.25), with no consistent sign.
     The two-methyl peak (3*) is about twice those. This is what equal
     per-carbon response looks like.
4. **NOE (inference, not stated by the authors).** Without inverse gated
   decoupling, carbons with attached protons (AMP, dioxane, carbamate CH₂ and
   CH₃) are enhanced relative to carbons without them (HCO₃⁻/CO₃²⁻ and the
   carbamate carbonyl). That predicts the low 2011 carbonate integrals.
   It cannot produce a factor of 4–7 in carbamate: the theoretical maximum
   ¹³C{¹H} enhancement is about 3, and the carbonate deficit implies only
   1.3–1.75. The 2011 paper does not say which carbamate peak it quantified.
5. **The authors never explain the change.** Ciftja 2014 cites 2011 only for
   not considering ionic strength (§3.3, p.323). Ciftja 2013 quotes the 2011
   acquisition parameters without comment (§1, p.225).

### Recommendation

- **Use Ciftja 2014 Tables S1–S3 (57 rows) as the AMP carbamate speciation
  data.**
- **Exclude Ciftja 2011** from calibration, from scoring and as "earlier
  speciation evidence". Its own CO₂ and charge balances fail, it is a single
  temperature from the same laboratory, and 2014 re-measured that
  temperature with a documented quantitative protocol.
- Sherman's exclusion of 2011 as "inconsistent" (thesis p.86) is supported
  by those balances.
- **Consequence for Mehdizadeh 2013:** its absolute K5 was fitted partly to
  Ciftja 2011 (#234), so it is likely biased toward too little carbamate.
- The mechanism behind the 2011 carbamate deficit remains **unexplained**.

## 4. Yi 2024 cross-check

- **Model.** Aspen eNRTL (ELECNRTL for parameter regression, ENRTL-RK for the
  zwitterion); equilibrium constants come from Gibbs energies of formation
  (§§2.1.2–2.1.3, p.4).
- **Carbamate.** Reaction R10 (H₂O + CO₂ + AMP ⇌ AMPCO₂⁻ + H₃O⁺) is listed,
  but "the generation of PZH₂²⁺ and AMPCO₂⁻ ions was here neglected … AMP is a
  sterically hindered amine, therefore both will hardly be formed" (§2.1.2,
  p.3). §3.2 repeats "the absence of carbamates" for loaded AMP (p.11).
  **No AMP carbamate law.**
- **Carbamate data used.** Only Ciftja 2014, and only as validation of the
  HCO₃⁻+CO₃²⁻ sum at 25, 35 and 45 °C (Fig. 5b, p.6; text p.11). The AMPCOO⁻
  column is not compared. The model with zero carbamate matches those sums
  apart from the two flagged α = 0.13 rows. *Inference:* since carbamate
  holds at most about 5% of the absorbed CO₂, the bicarbonate sum cannot
  discriminate carbamate laws; r_c carries that information.
- **AMP regression data (Table 4, p.5).**
  - Accepted CO₂ partial-pressure campaigns: Chen 2011 (13), Hartono 2020
    (109), Li & Chang 1994 (27), Seo & Hong 1996 (17), Dash 2011 (166) and
    **Kundu 2003 (51)**.
  - Accepted total-pressure campaigns: Hartono 2020 (53) and **Tong 2012
    (45)**.
  - Rejected: Jane 1997 and Silkenbäumer 1998.
  - Yi is therefore not independent of the candidate Kundu hold-out, or of
    Tong.
- **PZ data.** Ermatchkov 2006 is used as VLE for the PZ system (Table 3,
  p.2). Li 2013 AMP/PZ NMR is used for blend validation (p.11); Yi notes its
  amine mass balance is off by more than 20 percentage points.
- **Role.** A cross-check showing that an eNRTL model fitted to VLE can omit
  AMPCOO⁻ and still match pressures and carbonate sums. It neither supports
  nor contradicts the Ciftja 2014 carbamate magnitudes.

## Effect on the AMP design

| Design blocker (`../design-draft-amp.md`) | Status after #238 |
|---|---|
| Ciftja 2014 missing; temperature dependence unknown | **Settled as a source.** Read; apparent law and data recorded above |
| Ciftja 2011 overlap with 2014 (line 84) | **Settled by evidence:** recommend excluding 2011 (owner confirms) |
| Nonredundant NMR observable | **Proposed:** one r_c per row |
| NMR residual scale | **Proposed:** σ(r_c) ≈ 0.0025–0.003 absolute, from source uncertainty and replicates (owner freezes) |
| Nonzero-carbamate detection threshold (line 91) | **Settled:** ±0.0002 mole fraction (§2.6, p.321). Carbamate quantified at x ≥ 6.5×10⁻⁴, i.e. α ≥ 0.08, in all three isotherms |
| Carbamate temperature slope "fixed to a verified source law" (line 70) | **Owner decision.** No thermodynamically verified slope exists. Two independent apparent slopes agree at about +21 kJ/mol |
| Carbamate offset bounds (line 74) | **Partly informed:** apparent formation constants at 298 K span 0.0075–0.82 kg/mol (#234 table plus this note). Bounds remain an owner decision |
| Thermodynamic K_h in ePC-SAFT | **Open:** needs AMPCOO⁻ γ in ePC-SAFT; no non-circular conversion |
| AMPCOO⁻ PC-SAFT representation (σ, u/k, sites, Born diameter) | **Open:** untouched by these sources |

## Owner decisions

1. **Carbamate slope**, recommended first:
   - **(a) Recommended:** fix ΔH_h to Xu/Silkenbäumer
     (ln K_h,m = −2546.2/T + 11.555, i.e. +21.2 kJ/mol). It is independent of
     the NMR calibration rows and of the Kundu and Tong campaigns. Report
     Ciftja 2014 Eq. 19 (+20.8 kJ/mol at 298 K) as corroboration. Fit only the
     offset to the Ciftja 2014 r_c rows.
   - (b) Fix to Ciftja 2014 Eq. 19. It is not independent of the calibration
     rows, and it imports the authors' split.
   - (c) Fit slope and offset to the NMR rows. This adds an enthalpy-like
     coordinate, which the draft excludes without heat evidence, over only
     20 K.

   Under (a), "verified source law" in line 70 becomes "apparent source
   slope, corroborated".
2. **Ciftja 2011:** confirm exclusion from fitting and scoring.
3. **Ciftja 2014 roles:** all 57 rows as calibration (recommended), or hold
   out the 45 °C block as a temperature-transfer check of the fixed slope.
4. **NMR residual:** adopt r_c with σ ≈ 0.0025–0.003 absolute, or another
   scale.
5. **Initial value:** the offset start could come from Ciftja 2014 finite-I
   apparent values or from Hartono 2020 (#234). Neither is a thermodynamic
   constant.

## Unread or limits

- Ciftja 2014 Fig. S-1 and S-2 (SI p.1) were seen only as captions.
- Oscarson 1989, Phillips 1985, Kim 2011 (split inputs) and McCann 2011 were
  not read; their content here is as quoted by Ciftja 2014.
- Yi 2024 supplementary information and its GitHub model files were not read.
- Sherman 2016 (Ind. Eng. Chem. Res.) remains unread, as in #234.
- The definition of I in Eq. 19 is inferred from Fig. 8, not stated.
- The NOE explanation for 2011 is inference; the 2011 integration choices
  are not reported.
- The private CESAR-1 repository was used only as an index; nothing from it
  is recorded here.
