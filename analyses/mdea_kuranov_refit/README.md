# MDEA–CO₂–H₂O: Wangler 2018 reproduction gate and Kuranov refit (issue #126)

## Result: the reproduction gate fails; the refit was not run

Wangler et al. 2018 (Zotero `ZILDPWWE`) predicts the 82 Kuranov 1996 Table 2 total pressures with
19.7 % ARD (Table 11). The issue's working gate is 16.7–22.7 %. Declared as printed and
evaluated on the pinned Engine wheel (`21e761c3`, SHA-256 `d2f61e3a…0357`), the model solves all
82 rows but gives **ARD = 1036 %**. Its pressures are too high by a geometric-mean factor of 6.2;
at 313 K and 32 mass % MDEA the factor reaches about 60. The interpretations behind "as printed"
are listed under *Interpretations*. Step 3 (the two-parameter k_ij refit) was not run, as the
issue requires. The held-out Ermatchkov 2006 rows were not scored.

**Update, 2026-10-18 (convention diagnosis, next section):** the gap shared with Uyan 2015 is the
MDEAH⁺ dispersion convention, not the CO₂ reference state. The printed reading gives MDEAH⁺ the
inorganic-ion rule (no MDEAH⁺–MDEAH⁺ dispersion, diameter 0.88σ). Treating MDEAH⁺ as MDEA with a
charge brings the printed Wangler model to 17.6 % and reproduces Uyan's own speciation. Uyan's own
pressures and Wangler's osmotic coefficients remain unreproduced, so the convention is the leading
candidate, not a confirmed reproduction.

| Reading of the published model | Rows solved | ARD | 19 mass % (41 rows) | 32 mass % (41 rows) |
|---|---|---|---|---|
| **As printed** (the gate) | 82/82 | **1036 %** | 434 % | 1638 % |
| As printed, permittivity of the initial CO₂-free solvent | 82/82 | 953 % | 408 % | 1499 % |
| Spherical MDEAH⁺ (segment number 1) | 82/82 | 31.8 % | 20.6 % | 43.0 % |
| Spherical MDEAH⁺, initial-solvent permittivity | 82/82 | 19.8 % | 13.1 % | 26.4 % |
| Wangler 2018 (published) | 82 | 19.7 % | not given | 19.44 % (Fig. 11) |

Evidence: `results/reproduction-summary.json` and `results/reproduction-rows.csv` (every row, every
reading), `results/diagnosis.json`. ARD = (100/82) Σ|1 − p_calc/p_exp|.

Wangler's exact row set is ambiguous. The Table 11 caption limits loading to 1.2 mol CO₂/mol MDEA,
yet the table counts 82 points, and five Kuranov rows exceed 1.2 (rows 8–11 and 18, up to 1.316).
All 82 rows are scored here.

The last reading matches Wangler's overall ARD, but it does not reproduce his implementation. Its
32 mass % ARD is 26.4 %, against his 19.44 % (Fig. 11). It misses his reported speciation (below)
and his own MDEA·HCl osmotic coefficients. Both changes are departures from the printed text.

## Convention diagnosis (2026-10-18): MDEAH⁺ dispersion, not the CO₂ reference state

**Result.** The printed reading gives MDEAH⁺ the inorganic-ion rule: no MDEAH⁺–MDEAH⁺
dispersion and a diameter of 0.88σ (Uyan Eq. 10, Wangler Eq. 7). The authors' text describes
MDEAH⁺ as MDEA with a charge.
- Uyan §4.1 (p. 95): MDEAH⁺ parameters "were inherited from the parameters of MDEA except
  self-association and with the difference that the positive charge of MDEAH⁺ was additionally
  accounted for".
- Wangler §3 (p. 17) forbids equal-sign ions only "cross dispersion".
- Uyan gives the 0.88σ rule as a consequence of zero self-dispersion (p. 94). An ion that keeps
  its self-dispersion therefore keeps Eq. 11.

**(A) MDEAH⁺ as charged MDEA** keeps MDEA's self-dispersion (u/k = 228.71 K) and its
temperature-dependent diameter (Uyan Eq. 11, Wangler Eq. 6).
- It is the only tested convention that reproduces Uyan's own speciation: Fig. 4, x_CO₂ within
  0.85–1.28×.
- With no other change, the printed Wangler model goes from 1036 % to **17.6 %**. That is inside
  the gate of 16.7–22.7 %; the 32 mass % ARD is 20.7 % against 19.44 %.
- It does not reproduce Uyan's pressures: 0.41× his Fig. 5 lines, 58 % ARD.
- It does not reproduce Wangler's osmotic coefficients (28 % against 5.05 %) or his §6.2 x(H⁺).

**The readings closest to Uyan's pressure lines** fail his speciation and Wangler's ARD.
- Self-dispersion with 0.88σ, reading (B): Uyan 38.8 % against the re-determined 34.4 %; within
  22 % of his Fig. 5 lines.
- The Eq. 11 diameter alone: also within 22 % of the Fig. 5 lines.
- Both miss his speciation by 3–23×, and Wangler by 6× or more.

**γ⁰ for CO₂ (Uyan Eq. 18 as printed) is ruled out.**
- It puts x_CO₂ at 0.001–0.05× of Uyan's own Fig. 4 line, and pressures at 0.31× of his Fig. 5
  lines.
- Wangler Eq. 15 and Bülow 2021a Eq. 13 print γ*. Eq. 18's γ⁰ is therefore a typesetting slip.

**Uyan's targets.** All are for the same 82 Kuranov rows, ARD = (100/NP) Σ|1 − p_mod/p_exp|
(Uyan Eq. 25).
- Uyan Table 6 (p. 98) gives 22.9 % over "313 < T < 413 K, w_MDEA = {0.19 and 0.32},
  α < 1.316". By composition: 19.82 % at 0.19 (abstract), or 19.22 % over 0.01 < α < 1.32
  (§4.3.2); 25.91 % at 0.32.
- Wangler Table 11 note b (p. 23) states that Uyan's published ARD "was incorrect" and gives
  34.4 % as the re-determined value.
- Uyan's own model curves are a further target: x_CO₂ in Fig. 4 (313 K, w_MDEA = 0.23) and total
  pressure in Fig. 5 (w_MDEA = 0.19).
  - Both were read from the 600 dpi page, with the axis ticks as calibration.
  - Reading error is ±5 % for Fig. 4 and ±0.3 bar for Fig. 5.

**Checks that hold** (`results/conventions.json`, `kvalue_checks`):
- **Equilibrium constants, basis and loading.** Uyan's K-value method without activity
  coefficients (§3, step 1, a local recomputation) reproduces his Fig. 4 dashed line within 1 % at
  α = 0.2, 0.4, 0.6 and 0.75. This excludes a molality/mole-fraction or loading misreading.
- **The Engine solves Uyan Eqs. 17–23.** The K-value method iterated with the Engine's γ*
  reproduces the Engine's own bubble-point x_CO₂ to all printed digits (2.681e-4 at α = 0.2,
  printed Uyan model). The Engine's convention is the one Uyan used: water as pure liquid,
  MDEA, CO₂ and ions at infinite dilution in pure water.

**Every tested convention, Uyan 2015** (one declared change from the printed model unless the name
lists two). Columns:
- *ARD*: % on the 82 rows, then the 19 and 32 mass % halves (41 rows each), then the 77 rows with
  α ≤ 1.2.
- *ln p/p_exp*: mean ln(p_calc/p_exp).
- *Fig. 4*: x_CO₂ divided by Uyan's line at α = 0.2–0.75.
- *Fig. 5*: mean ln(p_calc/p_line) over 11 points of Uyan's lines.
- *Osmotic*: ARD on Wangler's MDEAH⁺Cl⁻ osmotic coefficients (Tables 8–9).

| Variant | Source | ARD | 19 % | 32 % | α ≤ 1.2 | ln p/p_exp | Fig. 4 | Fig. 5 | Osmotic |
|---|---|---|---|---|---|---|---|---|---|
| Published (Table 6 / Wangler re-determination) | | 22.9 / 34.4 | 19.82 | 25.91 | | | 1 | 0 | |
| As printed | Tables 1, 3–5; Eqs. 26–27; k_hb 0.015 | 234.0 | 190.4 | 277.7 | 248.1 | +0.85 | 28–72 | +0.53 | 92.4 |
| k(water–MDEAH⁺) = 0 | §4.2.1 vs Table 5 | 236.8 | 194.2 | 279.4 | 251.3 | +0.91 | 27–65 | +0.58 | 89.9 |
| γ⁰ CO₂ | Eq. 18 as printed | 72.6 | 57.2 | 88.0 | 74.5 | −0.69 | 0.001–0.05 | −1.18 | 92.4 |
| γ⁰ MDEA | misuse named by Bülow 2021a, p. 6329 | 74.9 | 48.6 | 101.1 | 76.9 | −0.38 | 0.26–4.1 | −0.94 | 92.4 |
| Table 1 as molality-based K | Table 1 caption | 234.0 | 190.4 | 277.7 | 248.1 | +0.85 | 28–72 | +0.53 | 92.4 |
| Solutes referenced to the water/MDEA solvent † | Eq. 23 | 251.2 | 208.2 | 294.2 | 266.4 | +0.95 | 28–71 | +0.62 | 92.4 |
| Initial-solvent permittivity † | Eq. 5 | 222.8 | 179.5 | 266.1 | 236.3 | +0.82 | 27–66 | +0.50 | 92.4 |
| MDEAH⁺ non-associating | Bülow 2021a, p. 6329 | 205.0 | 167.3 | 242.8 | 217.6 | +0.77 | 27–63 | +0.45 | 87.8 |
| Spherical MDEAH⁺ | Bülow 2021a Table 2 | 107.4 | 63.9 | 150.9 | 113.6 | +0.59 | 4.6–14 | +0.25 | 14.5 |
| MDEAH⁺ Eq. 11 diameter only | Eq. 11 | 87.7 | 75.5 | 99.9 | 91.1 | +0.24 | 5.8–23 | −0.03 | 55.0 |
| **(B)** MDEAH⁺ self-dispersion | §4.1; Wangler §3 | **38.8** | 27.2 | 50.3 | 38.8 | +0.10 | 3.4–9.9 | −0.16 | 12.2 |
| (B), every ion's self-dispersion | side-effect bound | 36.4 | 26.0 | 46.9 | 36.3 | +0.08 | 3.2–9.8 | −0.17 | 10.2 |
| (B), initial-solvent permittivity † | §4.1; Eq. 5 | 26.3 | 22.0 | 30.6 | 25.4 | −0.08 | 2.3–9.1 | −0.26 | 12.2 |
| **(A)** MDEAH⁺ as charged MDEA | §4.1; Eqs. 10–11 | **58.2** | 49.7 | 66.7 | 57.7 | −0.93 | **0.85–1.28** | −0.90 | 20.6 |
| (A), k(water–MDEAH⁺) = 0 | §4.2.1 | 53.4 | 44.6 | 62.3 | 52.5 | −0.83 | 0.70–1.03 | −0.78 | 24.0 |
| (A), k_hb(water–MDEAH⁺) = 0.015 | Table 5 note a, inherited | 58.2 | 49.8 | 66.7 | 57.7 | −0.93 | 0.85–1.27 | −0.90 | 20.6 |
| (A), initial-solvent permittivity † | Eq. 5 | 64.4 | 55.1 | 73.6 | 64.2 | −1.13 | 0.58–1.14 | −1.01 | 20.6 |
| (A), pure-water permittivity | Uyan §2 (ion-parameter source) | 59.7 | 50.9 | 68.5 | 59.2 | −0.98 | 0.76–1.51 | −0.92 | 20.6 |
| Every ion as a charged molecule | no ion rule | 62.8 | 54.2 | 71.4 | 62.5 | −1.07 | 0.63–1.02 | −0.99 | 22.5 |

† Local diagnostic recomputation (a ln K shift per reaction, or Uyan Eq. 5 recomputed per state).
It must not feed adopted results.

**The same conventions applied to Wangler 2018.**
- The speciation column is x(H⁺) and x(MDEAH⁺) divided by Wangler's §6.2 values, at α = 0.02 and
  α = 1.4 (313 K, w_MDEA = 0.23).
- Wangler's osmotic fit reached 5.05 % (Fig. 10).

| Variant | ARD | 19 % | 32 % | α ≤ 1.2 | ln p/p_exp | H⁺ (0.02 / 1.4) | MDEAH⁺ (0.02 / 1.4) | Osmotic |
|---|---|---|---|---|---|---|---|---|
| Published (Table 11, Fig. 11) | 19.7 | | 19.44 | | | 1 | 1 | 5.05 |
| As printed | 1036.3 | 434.2 | 1638.4 | 1092.2 | +1.83 | 0.64 / 5.03 | 0.94 / 0.66 | 129.3 |
| γ⁰ CO₂ | 188.7 | 49.9 | 327.5 | 199.9 | −0.07 | 0.64 / 56.2 | 0.94 / 1.02 | 129.3 |
| MDEAH⁺ Eq. 6 diameter only | 289.6 | 203.1 | 376.1 | 306.7 | +1.02 | 0.16 / 2.40 | 1.09 / 0.82 | 104.1 |
| (B) MDEAH⁺ self-dispersion | 121.8 | 64.0 | 179.5 | 128.4 | +0.69 | 0.55 / 0.37 | 0.95 / 1.22 | 48.7 |
| **(A) MDEAH⁺ as charged MDEA** | **17.6** | 14.6 | 20.7 | 16.3 | −0.16 | 0.14 / 0.35 | 1.12 / 1.24 | 28.1 |
| (A), initial-solvent permittivity † | 30.2 | 20.4 | 40.0 | 29.6 | −0.38 | 0.14 / 0.47 | 1.12 / 1.25 | 28.1 |
| (A), pure-water permittivity | 17.1 | 13.7 | 20.4 | 15.6 | −0.19 | 0.13 / 0.35 | 1.08 / 1.25 | 28.1 |
| Every ion as a charged molecule | 24.0 | 17.4 | 30.5 | 22.8 | −0.29 | 0.22 / 0.97 | 1.13 / 1.25 | 26.1 |

**What the evidence supports, ranked.**
1. **Identified cause of the gross overprediction:** the printed MDEAH⁺ treatment.
   - Every reading that keeps the inorganic-ion rule misses Uyan's speciation by at least 4.6×,
     or with the wrong trend (γ⁰ MDEA).
   - Switching MDEAH⁺ to charged MDEA (A) is the only change that reproduces it. The same change,
     and nothing else, puts Wangler inside the gate.
2. **Unresolved for Uyan: his pressures.** Uyan's Fig. 4 and Fig. 5 are not reproduced together
   by any reading.
   - At matched speciation (A), the CO₂ liquid fugacity is about e^0.9 below Uyan's lines.
   - The readings that match his lines miss his speciation by 3–23×.
   - The mechanism is not identified.
   - Wangler reports that Uyan's published ARD was incorrect (Table 11 note b), so Uyan's pressure
     results may carry an error the paper does not describe. This is inference.
3. **Unresolved for Wangler under (A):**
   - his MDEAH⁺Cl⁻ osmotic coefficients: 28 % against 5.05 %;
   - his §6.2 x(H⁺): 0.14–0.35×.
   - The duplicated water–MDEAH⁺ k_ij row in Table 6 matches Uyan's inheritance of the water–MDEA
     k_ij (Uyan Table 5). A copy error is therefore less likely than the D1 discussion below
     suggested.
4. **Excluded**, each by Uyan's own Fig. 4 or by the CO₂-free rows:
   - γ⁰ CO₂, γ⁰ MDEA, and molality-based K;
   - a mixed-solvent reference for solutes;
   - the permittivity basis (at most 12 ARD points, under every MDEAH⁺ reading);
   - MDEAH⁺ association;
   - a spherical MDEAH⁺ (fails Uyan's speciation, 4.6–14×);
   - total-pressure bookkeeping (CO₂-free rows within 6–15 % for Uyan, 0–3 % for Wangler).
5. **Not testable here:** Eq. 23 read literally, with x_i → 0 in the current mixture. For an ion
   this needs a non-electroneutral state, which the Engine refuses.

**Engine capability.** Neither MDEAH⁺ convention can be declared directly in one parameter
document.
- **Self-dispersion of one ion.** `ionic_dispersion` offers only `exclude-same-sign-ion-pairs`
  (which removes the self pair) or `all-ion-pairs` (which restores every inorganic ion's self pair).
  The exact declaration used here is a workaround:
  - `all-ion-pairs` with k_ij = 1 on every unlike same-sign pair;
  - every inorganic ion's u/k scaled by 1e-8, with each of its k_ij rescaled so u_ij is unchanged
    (`check_self_dispersion` asserts the identity to 1e-6 in ln φ).
  - It changes the declared u/k of the inorganic ions, so it is unsuitable for adoption.
- **A temperature-dependent diameter for an ion** (needed by A). The Engine refuses an ion without
  `packing_diameter` ("missing component/…/packing_diameter"). The Eq. 11 diameter therefore needs
  one document per temperature, which a single `epcsaft.regression.fit` cannot use (as with gap c).
- **Requests for the orchestrator.** These would go to the Engine owner as a comment on an Engine
  issue:
  - a per-component declaration that a charged component keeps its own self-dispersion;
  - optionally, that it uses the neutral temperature-dependent segment diameter instead of
    `packing_diameter`.

**Decisions made here (reversible).**
- Uyan Eqs. 26–27 use T⁺ = 298 K. They were re-expanded exactly about 298.15 K for the Engine's
  law grammar.
- Water–HCO₃⁻ is zero ('–' in Table 5).
- Water–MDEAH⁺ follows Table 5 and §4.3.2 (Eq. 27); §4.2.1 (zero) is a variant.
- No k_hb on the water–MDEAH⁺ edge; the inherited 0.015 is a variant.
- Every other Uyan input is shared with `model.py`.
- The figure readings are retained in `conventions.py` with their calibration.

## What the diagnosis established

1. **The reaction and reference-state conversion is internally consistent.** At Kuranov row 42
   (313.15 K, 3.9707 mol/kg MDEA, α = 0.673), the solution returned by the Engine satisfies
   Uyan Eqs. 17–23 as coded here.
   - The check uses independently computed rational activity coefficients: water relative to pure
     liquid, every other species relative to infinite dilution in water.
   - Residuals in ln K are ≤ 6e-5 for R1–R3 and 3e-10 for R4.
   - Uyan's text, Wangler Eq. 15 and Bülow 2021a (Eq. 13 and the text before Eq. 12) support this
     convention, MDEA included. Uyan Eq. 18 as printed uses γ⁰ for CO₂ instead (see
     *Interpretations*).
2. **Gaps (a) and (b) are closed by Engine #567** (merged `fd14723c`, an ancestor of `21e761c3`).
   - The cubic water–MDEA and water–MDEAH⁺ k_ij(T), the quadratic water–CO₂ and water–HCO₃⁻
     k_ij(T), and both l^hb(T) corrections are declared under the power reading of Wangler
     Eqs. 34–35 (*Interpretations*).
   - `score.check_temperature_laws` asserts that the declared laws equal hand-evaluated constants
     at 373.15 K (|Δ ln φ| < 1e-10).
   - The four CO₂-free Kuranov rows reproduce the water–MDEA solvent pressure within 3.4 %
     (1.912 vs 1.909, 3.573 vs 3.464, 1.804 vs 1.862, 3.500 vs 3.386 bar).
3. **Gap (c) is real.** The Engine's `solvent-only` permittivity is Uyan Eq. 5 mass-weighted over
   the *speciated* free water and free MDEA, with CO₂ and ions excluded. Uyan's "ion-free and
   CO₂-free MDEA/water solution" also reads as the *initial* solvent.
   - On the spherical reading the two interpretations differ by 12 ARD points (31.8 vs 19.8 %).
   - The initial-solvent reading can only be expressed as one document per (T, m_MDEA). A single
     `epcsaft.regression.fit` therefore cannot use it.
   - `model.initial_solvent_permittivity` is a local diagnostic recomputation of Uyan Eq. 5; it
     must not feed adopted results.
4. **Candidate explanation (d): the printed MDEAH⁺ declaration.**
   - The printed declaration is MDEA's segment number 3.675, packing 0.88σ, and a water–MDEAH⁺
     k_ij(T) row identical to water–MDEA in Table 6.
   - With these values, ln γ*(MDEAH⁺) = 7.5 at row 42. The overall
     MDEA + CO₂ + H₂O → MDEAH⁺ + HCO₃⁻ activity term is +5.0, which suppresses the reaction about
     150-fold.
   - Single changes at fixed composition move ln γ*(MDEAH⁺) to 0.65 (segment number 1), 2.8
     (k = 0) or 4.2 (packing = σ).
   - Wangler fitted water–MDEAH⁺ to MDEA·HCl osmotic coefficients (Tables 8–9, ARD 5.05 %).
     The printed declaration gives φ = 1.47–2.37 against measured 0.835–0.874 (ARD 129 %). With
     segment number 1 it gives 0.95–1.06 (ARD 17.9 %).
   - The same routine reproduces NaCl at 298 K with Held 2014 parameters (φ 0.914/0.940/1.007/
     1.136 vs 0.921/0.936/0.983/1.116 at 0.5–4 mol/kg). That check covers only spherical,
     non-associating ions; it does not clear the Engine's handling of a chain-like, associating
     cation such as MDEAH⁺.
5. **Reviewer probes weaken (d) as the sole cause.** They used the same wheel and code path; the
   Uyan part is now retained in `results/conventions.json`.
   - *Uyan 2015's own model fails the same way.* Declared from Uyan's equations (Eqs. 26–27,
     association correction 0.015, MDEAH⁺ segment number 3.675), it scores 234 % on the 82 rows,
     and 223 % with initial-solvent permittivity. Uyan published 22.9 %; Wangler re-determined it as
     34.4 %. With a spherical MDEAH⁺ it scores 107 %. Pressures are too high in every case, as with
     Wangler.
     - The shared gap is the MDEAH⁺ dispersion convention (see *Convention diagnosis*), not only
       Wangler's printed MDEAH⁺ values.
   - *The osmotic data do not single out a spherical MDEAH⁺.* They constrain segment number and
     k together.
     - With the printed segment number 3.675 and a constant water–MDEAH⁺ k ≈ +0.35, Wangler's
       MDEA·HCl data (Tables 8–9) are reproduced at 3.4 % ARD, better than spherical (17.9 %) and
       his 5.05 %.
     - That reading scores 56 % on Kuranov, with pressures ×0.40.
   - *Water–CO₂ is not the problem.* The Engine's CO₂-in-water Henry constant is 9–23 % above
     Carroll 1991.
6. **Wangler's reported speciation is not matched by either reading** (313 K, 23 mass % MDEA,
   §6.2):

   | Quantity | Wangler | As printed | Candidate |
   |---|---|---|---|
   | x(MDEAH⁺), α = 0.02 | 9.80e-4 | 9.21e-4 | 1.31e-3 |
   | x(H⁺), α = 0.02 | 3.80e-11 | 2.41e-11 | 2.32e-12 |
   | x(MDEAH⁺), α = 1.4 | 3.37e-2 | 2.21e-2 | 4.20e-2 |
   | x(H⁺), α = 1.4 | 3.32e-9 | 1.67e-8 | 9.35e-9 |

   - At α = 0.02 the printed reading is closer: x(MDEAH⁺) within 6 %, but x(H⁺) 37 % low.
   - At α = 1.4 his values fall between the two readings.
   - Wangler's implementation is therefore not identified from the paper.
7. **Box corners of the planned refit.** These are fixed evaluations at k(water–MDEAH⁺),
   k(water–HCO₃⁻) ∈ {−0.3, +0.3}, not a fit.
   - Printed base: 50–2918 % ARD; one corner leaves a row unsolved.
   - Candidate base: 22–45 % ARD.
   - Four corners do not bound the interior of the box, so they do not show whether a fit could
     reach 10.9 %. They show only that no corner comes close.

## Interpretations in "as printed"

- **Wangler Eqs. 34–35.** As printed (PDF p. 19) they have no exponents on (T − T⁺). Reading the
  terms as powers 1–3 is justified by the Table 6 headers (k_ij,T, k_ij,T², k_ij,T³), by the
  water–CO₂ row matching Uyan's quadratic Eq. 26, and by Bülow 2021a Eq. 26. It remains an
  interpretation.
  - Under it, water–HCO₃⁻ k_ij reaches −0.47 at 373 K and −0.975 at 413 K, although it was fitted
    on 278–318 K.
- **CO₂ activity coefficient.** The code uses the infinite-dilution γ* for CO₂, following Uyan's
  text, Wangler Eq. 15 and Bülow Eq. 13. Uyan Eq. 18 as printed (p. 94) uses γ⁰.
  - Tested on 2026-10-18 and ruled out (*Convention diagnosis*). With γ⁰, x_CO₂ falls to
    0.001–0.05× of Uyan's own Fig. 4 line.

## Decisions made here (2026-10-17/18, without owner input; each reversible)

- **Source values.**
  - Uyan Table 1 constants are used: Wangler Table 2 prints them rounded to four digits, which
    shifts ln K by up to ~0.05.
  - Uyan Table 3 full-precision water/MDEA association values are used (Wangler Table 4 rounds
    them).
  - Wangler Table 6 water–CO₂ (−0.0215, T⁺ = 298.15 K) is used, not Uyan Eq. 26 (−0.022, 298 K),
    because the issue names Wangler Tables 4–7.
- **Ions.** Held's convention applies: packing diameter 0.88σ (Uyan Eq. 10; Held 2014 Eq. 21),
  Debye–Hückel diameter σ (Held 2008 Eq. 3). This was already the repository reading in
  `analyses/mea_parameter_bundle/model-d/README.md`.
  - H⁺ carries the H₃O⁺ parameters (Uyan §3) with the H⁺ molar mass, so every reaction conserves
    mass.
  - Pairs Wangler and Uyan leave unparameterized are declared zero.
  - Same-sign ion pairs are excluded (`exclude-same-sign-ion-pairs`).
- **Association.**
  - MDEA is 4C, declared as two donor plus two acceptor sites.
  - MDEAH⁺ carries MDEA's sites with zero self energy and κ = 0.123858 (Uyan Table 4,
    footnote a).
  - Wolbach–Sandler cross edges are declared for water–MDEA and water–MDEAH⁺ (with Wangler
    Table 7 l^hb(T)) and for MDEA–MDEAH⁺ (no correction). This satisfies Engine #569: every
    site-bearing pair has edges.
- **Permittivity.** Uyan's own temperature functions are not published, so both are
  approximations within the stated limits.
  - Water reuses the repository's quadratic law. It agrees with Floriano & Nascimento's
    0.1 MPa values (`NBK9T7B7`, Table I with Eq. 3) within 0.16 % at 273–348 K.
  - MDEA is a least-squares line through Hsieh 2007 pure-MDEA values
    (`data/reference/MDEA/Hsieh_2007_MDEA_relative_permittivity.csv`, max residual 0.011),
    extrapolated beyond 328 K.
- **Bubble point.** Stoichiometric molality feed; the liquid holds all eight species and the vapor
  water, MDEA and CO₂. Each solve starts from the previous row of its isotherm, with Kuranov's
  pressure as the initial guess only.
- **Stop at the gate.** The two readings that bring the ARD near 19.7 % are diagnoses, not the
  published model. Adopting either is a scientific decision for the owner, and the fit could not
  use one of them anyway (point 3).

## Open decisions and limits

- **D1 (owner): which base model should the #126 refit use?** The printed one misses by a factor
  of about 6, and so does Uyan's own model (reviewer probes). The evidence on MDEAH⁺:
  - Wangler writes that "eight binary parameters were fit to new osmotic-coefficient data in the
    subsystems water–MDEAH⁺ and water–HCO₃⁻" (§6.2.1). His duplicated water–MDEAH⁺ row in
    Table 6 may therefore be a copy error.
  - Uyan §4.3.2 inherited the MDEAH⁺/water k_ij from MDEA/water, a precedent for such a copy.
  - Bülow 2021a Table 2 (p. 6331, from the same group) gives MDEAH⁺ segment number 1 with the
    same σ (3.5630 Å) and u/k (228.71 K) as Uyan and Wangler. It treats charged species as
    non-associating (text after Eq. 18) and writes Wangler's k_ij(T) with explicit powers
    (Eq. 26).
  - The options:
    - (i) A spherical MDEAH⁺, as in Bülow 2021a.
    - (ii) Reconstruct Wangler's water–MDEAH⁺ parameters from his Tables 8–9 osmotic data.
      This is a scope change.
    - (iii) Base the refit on Bülow 2021a. It adds a Born term, which conflicts with the issue's
      "no Born" rule, so this is a scope change.
    - (iv) Fit the MDEAH⁺ size together with the k_ij. Also a scope change.
  - The shared Uyan/Wangler gap is now located in the MDEAH⁺ dispersion convention (*Convention
    diagnosis*). Reading (A), MDEAH⁺ as charged MDEA, is a fifth option and the one closest to
    both texts. It reproduces Uyan's speciation and puts the printed Wangler model at 17.6 %.
    - It cannot be declared in one Engine document (see *Engine capability*).
    - It leaves Uyan's pressures and Wangler's osmotic data unexplained.
    - Under it, the Table 6 row is Uyan's inheritance rather than a copy error.
- **D2 (Engine).** Declaring Uyan Eq. 5 on the initial CO₂-free solvent needs a generic
  permittivity rule whose solvent mass weighting counts reacted species with their parent solvent,
  or another fixed-solvent basis. Without it, the refit must use the Engine's speciated basis.
- **Sources.**
  - The Hsieh 2007 paper (doi 10.1021/je600515j) is not in Zotero; its values come from the NIST
    ThermoML record.
  - The originals for Uyan Table 1 remain unverified (issue list).
- **Data caveats.**
  - Kuranov row 58 is 9.4 % below its lower-loading neighbour (flagged in the CSV and kept).
  - The four CO₂-free rows are counted in the 82.
  - Wangler's exact 82-row set is ambiguous (see *Result*).

## Files and commands

- `model.py`: the published declarations with locators, the bubble-point problem, and the two
  diagnostic readings. `python model.py` rewrites `wangler-2018-parameters.json` (SHA-256
  `75a15629…cc28`), which `score.py` checks against the declarations and hashes into its record.
- `score.py`: scores the four readings on all 82 rows and checks the temperature-law declarations.
- `diagnose.py`: mass action, activity decomposition, osmotic checks, §6.2 speciation, box corners.
- `conventions.py`: the convention diagnosis.
  - It declares Uyan 2015 and every variant, and scores them on Kuranov.
  - It checks speciation against Uyan Fig. 4 and Wangler §6.2, pressures against Uyan's Fig. 5
    lines, and osmotic coefficients against Wangler Tables 8–9.
  - It runs the K-value checks and writes `results/conventions.json`.
  - Run it with `OMP_NUM_THREADS=1 uv run python conventions.py`: about 4 minutes, one process per
    variant, at most 16.

Run from this directory: `uv run python score.py && uv run python diagnose.py` (about 5 minutes,
single thread). Sources: `data/reference/MDEA/README.md`.
