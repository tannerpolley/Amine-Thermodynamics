# MDEA–CO₂–H₂O: Wangler 2018 reproduction gate and Kuranov refit (issue #126)

## Result: the reproduction gate fails; the refit was not run

Wangler et al. 2018 (Zotero `ZILDPWWE`) predicts the 82 Kuranov 1996 Table 2 total pressures with
19.7 % ARD (Table 11). The issue's working gate is 16.7–22.7 %. Declared exactly as printed and
evaluated on the pinned Engine wheel (`21e761c3`, SHA-256 `d2f61e3a…0357`), the model solves all
82 rows but gives **ARD = 1036 %**. Its pressures are too high by a geometric-mean factor of 6.2;
at 313 K and 32 mass % MDEA the factor reaches about 60. Step 3 (the two-parameter k_ij refit) was
not run, as the issue requires. The held-out Ermatchkov 2006 rows were not scored.

| Reading of the published model | Rows solved | ARD | 19 mass % (41 rows) | 32 mass % (41 rows) |
|---|---|---|---|---|
| **As printed** (the gate) | 82/82 | **1036 %** | 434 % | 1638 % |
| As printed, permittivity of the initial CO₂-free solvent | 82/82 | 953 % | 408 % | 1499 % |
| Spherical MDEAH⁺ (segment number 1) | 82/82 | 31.8 % | 20.6 % | 43.0 % |
| Spherical MDEAH⁺, initial-solvent permittivity | 82/82 | 19.8 % | 13.1 % | 26.4 % |
| Wangler 2018 (published) | 82 | 19.7 % | not given | 19.44 % (Fig. 11) |

Evidence: `results/reproduction-summary.json` and `results/reproduction-rows.csv` (every row, every
reading), `results/diagnosis.json`. ARD = (100/82) Σ|1 − p_calc/p_exp|.

The last reading matches Wangler's overall ARD, but it does not reproduce his implementation. Its
32 mass % ARD is 26.4 %, against his 19.44 % (Fig. 11). It misses his reported speciation (below)
and his own MDEA·HCl osmotic coefficients. Both changes are departures from the printed text.

## What the diagnosis established

1. **The reaction and reference-state conversion is correct.** At Kuranov row 42 (313.15 K,
   3.9707 mol/kg MDEA, α = 0.673), the solution returned by the Engine satisfies Uyan Eqs. 17–23.
   The check uses independently computed rational activity coefficients: water relative to pure
   liquid, every other species relative to infinite dilution in water. Residuals in ln K are
   ≤ 6e-5 for R1–R3 and 3e-10 for R4. Bülow 2021a (text before Eq. 12) confirms that this is the
   intended reference convention, MDEA included.
2. **Gaps (a) and (b) are closed by Engine #567** (merged `fd14723c`, an ancestor of `21e761c3`).
   - The cubic water–MDEA and water–MDEAH⁺ k_ij(T), the quadratic water–CO₂ and water–HCO₃⁻
     k_ij(T), and both l^hb(T) corrections are declared exactly as published.
   - `score.check_temperature_laws` asserts that the declared laws equal hand-evaluated constants
     at 373.15 K (|Δ ln φ| < 1e-10).
   - The four CO₂-free Kuranov rows reproduce the water–MDEA solvent pressure within 3 %
     (1.912 vs 1.909, 3.573 vs 3.464, 1.805 vs 1.862, 3.500 vs 3.386 bar).
3. **Gap (c) is real.** The Engine's `solvent-only` permittivity is Uyan Eq. 5 mass-weighted over
   the *speciated* free water and free MDEA, with CO₂ and ions excluded. Uyan's "ion-free and
   CO₂-free MDEA/water solution" also reads as the *initial* solvent.
   - On the spherical reading the two interpretations differ by 12 ARD points (31.8 vs 19.8 %).
   - The initial-solvent reading can only be expressed as one document per (T, m_MDEA)
     (`model.initial_solvent_permittivity`). A single `epcsaft.regression.fit` therefore cannot
     use it.
4. **New gap (d): the printed MDEAH⁺ declaration does not reproduce Wangler's own MDEAH⁺ fit.**
   - The printed declaration is MDEA's segment number 3.675, packing 0.88σ, and a water–MDEAH⁺
     k_ij(T) row identical to water–MDEA in Table 6, although the text says it was fitted.
   - With these values, ln γ*(MDEAH⁺) = 7.5 at row 42. The overall
     MDEA + CO₂ + H₂O → MDEAH⁺ + HCO₃⁻ activity term is +5.0, which suppresses the reaction about
     150-fold.
   - Single changes at fixed composition move ln γ*(MDEAH⁺) to 0.65 (segment number 1), 2.8
     (k = 0) or 4.2 (packing = σ).
   - Wangler fitted water–MDEAH⁺ to MDEA·HCl osmotic coefficients (Tables 8–9, ARD 5.05 %).
     The printed declaration gives φ = 1.47–2.37 against measured 0.835–0.874 (ARD 129 %). With
     segment number 1 it gives 0.95–1.06 (ARD 17.9 %).
   - The same routine reproduces NaCl at 298 K with Held 2014 parameters (φ 0.914/0.940/1.007/
     1.136 vs 0.921/0.936/0.983/1.116 at 0.5–4 mol/kg). The Engine's ion handling is therefore not
     the cause.
5. **Wangler's reported speciation is not matched by either reading** (313 K, 23 mass % MDEA,
   §6.2):

   | Quantity | Wangler | As printed | Candidate |
   |---|---|---|---|
   | x(MDEAH⁺), α = 0.02 | 9.80e-4 | 9.21e-4 | 1.31e-3 |
   | x(H⁺), α = 0.02 | 3.80e-11 | 2.41e-11 | 2.32e-12 |
   | x(MDEAH⁺), α = 1.4 | 3.37e-2 | 2.21e-2 | 4.20e-2 |
   | x(H⁺), α = 1.4 | 3.32e-9 | 1.67e-8 | 9.35e-9 |

   The printed reading matches his low-loading numbers; at α = 1.4 his values fall between the
   two readings. Wangler's implementation is therefore not identified from the paper.
6. **The planned refit cannot rescue the printed base.** These are fixed evaluations at the box
   corners k(water–MDEAH⁺), k(water–HCO₃⁻) ∈ {−0.3, +0.3}, not a fit.
   - Printed base: 50–2918 % ARD; one corner leaves a row unsolved.
   - Candidate base: 22–45 % ARD.
   - A corner does not bound the interior optimum.

## Decisions made here (owner asleep; each reversible)

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
  published model. Adopting them is a scientific decision for the owner, and the fit could not
  use one of them anyway (point 3).

## Open decisions and limits

- **D1 (owner).** Which base model should the #126 refit use? The printed one cannot reach the
  benchmark. A spherical MDEAH⁺ is supported by Wangler's own osmotic data, but contradicts his
  text ("non-spherical") and his §6.2 speciation.
  - Alternatives: base the refit on Bülow 2021a, the later model from the same group, which
    defines the references explicitly.
  - Or treat the MDEAH⁺ size and k_ij as part of the fit with a spherical cation.
- **D2 (Engine).** Declaring Uyan Eq. 5 on the initial CO₂-free solvent needs a generic
  permittivity rule whose solvent mass weighting counts reacted species with their parent solvent,
  or another fixed-solvent basis. Without it, the refit must use the Engine's speciated basis.
- **Sources.**
  - The Hsieh 2007 paper (doi 10.1021/je600515j) is not in Zotero; its values come from the NIST
    ThermoML record.
  - The originals for Uyan Table 1 remain unverified (issue list).
- **Data caveats.** Kuranov row 58 is 9.4 % below its lower-loading neighbour (flagged in the
  CSV and kept). The four CO₂-free rows are counted in the 82; Wangler Table 11 also counts 82, so it presumably includes them.

## Files and commands

- `model.py`: the published declarations with locators, the bubble-point problem, and the two
  diagnostic readings. `python model.py` rewrites `wangler-2018-parameters.json` (SHA-256
  `75a15629…cc28`).
- `score.py`: scores the four readings on all 82 rows and checks the temperature-law declarations.
- `diagnose.py`: mass action, activity decomposition, osmotic checks, §6.2 speciation, box corners.

Run from this directory: `uv run python score.py && uv run python diagnose.py` (about 5 minutes,
single thread). Sources: `data/reference/MDEA/README.md`.
