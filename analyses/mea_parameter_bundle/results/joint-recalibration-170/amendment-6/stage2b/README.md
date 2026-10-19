# Amendment 6, stage 2b: MEA–water k_ij with a reciprocal-temperature slope (#170)

Run 2026-10-19 on Engine wheel `main-21e761c3` (sha256 `d2f61e3a…0357`).
- **Basis:** design §0b revision 3 (Ready at 352bda1, merged 8d9e315); declaration `stage2b-spec.json`, from `inputs/revision-3/stage2b-spec.json` on branch `build-170-amendment-6-revision-3` at 462c984, with the program priors set by the recorded operator check in `step-ledger.json`.
- **Partial-build review (2026-10-19):** stage 2b ready to run, with no stage-2 code change.

**Question.** Every density-weighted endpoint missed the CO₂-free 25 °C density gate (0.5 kg/m³). The five CO₂-free errors trended with temperature, and a constant MEA–water k_ij cannot change a trend. The owner decided to fix the miss, not disclose it (#170).

**Fit.**
- **Coordinates:** two, the MEA–water k_ij and the new slope b in k(T) = k + b(1/T − 1/313.15 K).
- **Rows:** the unchanged 50 Cai 1996 boiling-temperature and vapor-water rows (weight 1), plus the five Amundsen 2009 CO₂-free 30 wt % densities (scale 0.5 kg/m³, weight 10).
- **Starts:** stage 2's two starts, A and B, with b = 0.

## Result

**Both starts converge to the same interior point, and all five CO₂-free densities fall within the 0.5 kg/m³ gate at a 1.4 % Cai cost.**

| | Value |
|---|---|
| k_ij at 313.15 K | **−0.0898918** (B: −0.0898918) |
| Slope b | **−8.948 K** (B: −8.948) |
| Active bounds | none |
| Total cost | 103.429 (start 156.669) |
| Cai-only cost | **92.615**, against the 95.895 ceiling (+5 % over the constant-k base 91.329) |
| CO₂-free density errors, kg/m³ (25 / 40 / 50 / 70 / 80 °C) | **−0.479, −0.016, +0.023, +0.431, +0.353** |
| Linear probe prediction (`../neutral-slope-probe/`) | −0.473, −0.011, +0.028, +0.434, +0.356 |

The 25 °C row passes with only 0.021 kg/m³ to spare. The joint fits carry these five rows at weight 10, so the final candidate is checked against them again: ion parameters move them slightly through trace MEAH⁺.

**Checks.**
- **Cold replay:** relative cost difference 1.5e−14; largest weighted-row difference 1.2e−11.
- **Centered derivatives:** 220 of 220 pass per start (largest absolute error 2.1e−7).
- **Identification:** free rank 2, condition 3.64.

**Uncertainty.** k and b are fitted point estimates; the gate checks above are deterministic evaluations at them. The retained local covariance (`out/neutral-mea-water/A/identification.json`) holds only under its stated assumptions: unit-variance weighted residuals, independent errors, an interior regular linearization, and no model discrepancy. It gives conditional standard errors:

| | k_ij | b |
|---|---:|---:|
| Unit-variance | 0.00103 | 1.90 K |
| Scaled by the variance factor 3.90 | 0.00203 | 3.75 K |

The k–b correlation is 0.79. On either scaling, b is distinguishable from zero. These are not measurement-propagated uncertainties.

**Compute.** 8.24 s wall, 13.73 CPU-s (whole command), charged to the program ledger at merge.

**Next.** Substitute k and b into both joint start documents (the tie and Held forms), as §0b specifies. That is the pending step in `inputs/revision-3/*pending-stage2b.json`.
