# Round-6 referee comments: response

Manuscript: “Thermodynamics of CO₂-loaded aqueous amines with ePC-SAFT: monoethanolamine calibration, transfer to DEA, MDEA and AMP, and phase stability”, branch `issue-429-story-pass`, issue #429.

Locators refer to the PDFs built in this revision: main text (28 pages) and supplement (49 pages). “S” numbers are supplement sections and tables. Status words follow `round4-response.md`: **Addressed**, **Partly**, **Open**, **Not adopted**.

## What changed in this revision

1. **Round-7 calculations (#436) answer most of the round-6 requests.** The owner adopted three receiver changes on 2026-11-25. **DEA** is now fitted to 90 CO₂ partial pressures from three sources, not one, plus 50 heats. **MDEA** is refitted with pressure weights. **AMP** is refitted with the carbamate inputs of the MEA model. The MEA model stays the #435 fit. A full-weight fit to the 112 hot pressures is reported only as a sensitivity (Section 4.1.5; Tables S9, S10).
2. **The DEA model now fails a phase test.** At four states where Weiland et al. measured the density of a single liquid, it predicts two liquids. Sections 4.3 and 5.4, the abstract, highlight 4 and the conclusions report this as a model failure.
3. **The reference-pressure check for the 121.3 MPa split is done.** With the reaction reference states following the system pressure, the split is confirmed. With the reference fixed at 100 kPa, the case is unresolved (Section 4.3; S3).
4. **Still open by owner decision:** #424 (shared parameters released), #427 (multistart) and the deposit DOI.

## Astra (3/5, major)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | Pressure consistency of Eq. 8/11; test the reported 121.3 MPa split with R1–R3 at 0.1 MPa | Partly | The test is done. With tracking references the split is confirmed (ΔG/RT 4.233×10⁻⁵ mol). At 100 kPa the candidate lowers G/RT by 0.0475 mol, but its liquid roots are unresolved. The pressure-tracking correction is −15.7 % of the EOS volume (Section 4.3; S3). The 121.3 MPa split belongs to the first MDEA fit. The adopted MDEA model's split is at 204.054 MPa, and the reference convention was not tested there. No derivation of (∂G/∂P) = V was added. |
| M2 | AMP cause: narrow the slope claim | Addressed | Section 4.3 now says the added pressures do not isolate the slope as the cause, and that stability and accuracy are separate tests. |
| M3 | MDEA property comparisons at unstable or unfinished measured states | Partly | S7.1 lists the 25 measured states with descents by property (4 Sobrino densities, 13 Böttinger species states, 5 Zheng heats, 3 Merkley heats) and the 224 unfinished measured-state searches. A table of deviations by source, restricted to resolved states, was not made. |
| minor | Name the pressure observable | Addressed | Abstract; Table 8 footnote a; Section 4.2.4. |
| minor | 38.4 % against 37.71 % | Addressed | Now 25.09 % on 101 Ermatchkov pressures and 23.79 % on all 121 (Section 4.2.2; Table 8). |
| minor | Salt data are model-derived; mixed-salt 2.56 %; Kuranov “probable match”; carbonate example | Open | No change in this pass. |
| minor | DOI; which values 1.3.2 reproduces | Open | The DOI is a placeholder. The 1.3.2 cell readbacks (round 7, H) are not stated in the text. |

## Sol (3/5, major)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | Reference-pressure convention; extend to 121.3 MPa | Partly | As Astra M1. |
| M2 | Drivers of the MDEA tradeoff under one pressure weighting | Addressed | With pressure weights, both shared sets were refitted. The salt-fitted set does better on fitted totals (4.15 against 4.46 %) and on Ermatchkov pressures (25.09 against 31.11 %). The tradeoff therefore belongs to the first weighting (Section 4.2.4; S4.1). |
| M3 | Independent starts; matched fit with original R4 | Open | Multistart is #427. The DEA R4 change at 313.15 K is now +0.137 ± 0.389, within its standard error (Section 4.2.1). |
| M4 | AMP attribution wording | Addressed | “In the fits tested, adding those measured pressures removed the detected splits” (Section 4.3). |
| M5 | Auditable coverage; 121.3 MPa detail | Partly | Table 8 now counts the 204.054 MPa split. S7.1 gives its state, ΔG/RT and error, and the 262.862 MPa targeted result. A tabulation by source and role was not made. |
| M6 | Kuranov 82 vs 81; Hong labels | Partly | Row 72 is now named and its calculated value given (S8). Hong labels are unchanged. |
| minor | Development-data inventory, versions, deposit | Partly | Versions are in Data availability. The deposit sentence is marked PENDING because the stager predates the adopted fits. |

## Opus (3/5, major)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | State plainly what MEA determines; AMP inputs from the superseded fit | Addressed | AMP now uses the MEA-model inputs (204.0748 K, −0.165523, lower bound 5.201154 Å; Section 4.2.3; S1). The abstract and introduction now say that the MEA model is the benchmark and the source of the fixed carbamate energy of DEA and AMP, and that no amine data determine the shared water–anion set. |
| M2 | MDEA pressure-weighted refit under both shared sets | Addressed | As Sol M2. Loaded totals now carry 32.9 % of the MDEA objective (Section 3.3; S2). |
| M3 | Narrow generalizations | Addressed | “No shared set is better” was removed. The phase-search lesson now names its two cases (Section 4.3), and the AMP split statement is narrowed. |
| M4 | Measured MDEA states below the bubble pressure, incl. Sobrino at 393.15 K, 0.1 MPa | Open | The counts are reported (S7.1). The Sobrino pressures were not rechecked, and no sensitivity to excluding these states was run. |
| M5 | Test the 121.3 MPa split at 0.1 MPa | Partly | As Astra M1. |
| M6 | DEA weak: add Seo–Hong and Lal; quantify methane | Addressed | The broadened fit includes both sources. Seo–Hong is 66.20 %, and the Hᴱ sign is still wrong at all 14 points. With the methane-free liquid composition held fixed, the methane shift is at most 0.318 MPa (Sections 4.2.1, 4.3, 5.4). |
| M7 | Electrostatics choices | Open | Unchanged (Section 5.3). |
| M8 | Comparative claims limited to the optima found | Partly | Section 5.4 keeps “local solution”; #427 is open. |
| minor | Repeat the pH comparison with the adopted model | Addressed | Model minus electrode is −0.150 to +0.138 pH, mean +0.004, on 197 points (S1). |
| minor | Others (Fig. 5/6 form, Table S16 title, SAFT-γ Mie comparison, notation) | Open | Not changed in this pass. |

## Fable (3/5, major)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | Release water–anion interactions; joint fit | Open | #424. |
| M2 | MDEA weighting | Addressed | Pressure-weighted MDEA model (Section 4.2.2). Its variance factor is 0.128 on 271 degrees of freedom (S4). |
| M3 | Fit MEA pressures to 393 K | Addressed (sensitivity) | The full-weight expanded fit is reported. Hot pressures improve (Wagner 28.07 → 10.40 %), but the 47 legacy pressures worsen (11.35 → 22.78 %, bias +20.27 %). The sources conflict at 393 K: Jou 46.8 kPa against Ma'mun 83.6 kPa at α ≈ 0.35. The #435 MEA model is kept (Section 4.1.5; Table S9). |
| M4 | Salt-set bounds and extrapolation | Open | Section 5.4 states the limit. |
| M5 | Sensitivities not repeated for the reported models | Partly | Redone: pH (S1), the AMP inputs, the 121.3 MPa reference, the unbounded MDEA search (S7.2) and the AMP slope profile for the original salt fit (S7.3). The DEA binary, the Hessian of the AMP model and the bound refits were not redone. |
| M6 | Multistart | Open | #427. |
| M7 | DEA not credible | Addressed | DEA is broadened and its four measured-state splits are reported as failures. The water–DEA binary stays a negative result. |
| M8 | Stability coverage | Partly | Counts are updated (Section 4.3; S7.1). The MEA grid was not extended. |
| M9 | Accuracy behind the literature | Partly | Ma'mun pressures are stated as underpredicted at every point. MDEA now beats the fitted published models on Kuranov 82 (4.16 %) but not on Ermatchkov or Kamps (Section 5.2). No eNRTL or e-UNIQUAC MEA comparison was added. |
| minor | The hot-heat limit on duty | Addressed | Section 5.4 says the MEA model does not support regeneration-duty estimates. Section 4.1.5 gives the Kim et al. 393 K comparison (Table S10). |
