# Carbamate-hydrolysis shift handoff for #429

Use the #413 DEA endpoint and the #412 slope-150 AMP endpoint. The
coefficients describe hydrolysis of carbamate with explicit water on
the infinite-dilution common-molality basis. The variant calculations
hold every other parameter fixed. The conditional errors exclude
uncertainty in the fixed parameters, active bounds, and model form.

| Manuscript location | Existing entry | Replacement or addition | Retained source |
|---|---|---|---|
| `tables/transfer-fitted.tex`, Table 6 | DEA δh = 0 J/mol, SE 1,344 J/mol | DEA δh = −11,968 J/mol relative to Aroua Eq. 14, SE 1,344 J/mol | [DEA Table 6 values](table6.json) |
| `tables/transfer-fitted.tex`, Table 6 | No pivot-level shift row | DEA Δln K₄(313.15 K) = −1.309 (SE 0.618, bounds −3 to +3). AMP Δln K₄(313.15 K) = +1.233 (SE 0.265, bounds −3 to +2). AMP δh remains −5,000 J/mol, at the −5,000 to +5,000 bounds, with conditional SE unavailable | [DEA Table 6 values](table6.json), [AMP Table 6 values](../../../amp_transfer/results/r4-shift-426/table6.json) |
| `scripts/dea_displays.py:438`, Table 6 footnote | DEA zero relative to the final R4 law and AMP δh relative to the initial R4 law | State that DEA and AMP increments use their starting R4 correlations as zero and that the final coefficients include the fitted increments. Define Δln K₄ as the fitted minus starting log hydrolysis constant at 313.15 K. Retain the AMP fixed-slope and active-bound qualifications | [DEA chart](controls.json), [AMP chart](../../../amp_transfer/results/r4-shift-426/controls.json) |
| `tables/supplement-transfer-bounds.tex` and `scripts/dea_displays.py:440` | DEA δh bounds −18,032 to +21,968 J/mol about the final law | −30,000 to +10,000 J/mol about Aroua Eq. 14. Define the bounds on the starting-law basis in the footnote. Include the pivot-level bounds on the same basis | [DEA chart](controls.json) |
| `supplement.tex:203` | DEA increment relative to the final correlation | Define it relative to Aroua Eq. 14 and state that the final coefficients already include the increment | [DEA Table 6 values](table6.json) |
| Supplement, new Δln K₄ table | No comparison table | Give source and fitted ln K₄, their difference and ratio, conditional SE, and source-range marks at each retained temperature | [DEA shifts](shift.csv), [AMP shifts](../../../amp_transfer/results/r4-shift-426/shift.csv) |
| `sections/transfer_results.tex:27` | Qualitative statement that the laws are effective and conditional | At 298.15, 313.15 and 393.15 K the DEA shifts are −1.078, −1.309 and −2.244, with conditional SEs 0.640, 0.618 and 0.532. The AMP shifts are +1.330, +1.233 and +0.843, with conditional SE 0.265 at the enthalpy bound. At 313.15 K the ratios of fitted to source K₄ are 0.270 and 3.433. Keep the conditional interpretation and cite the supplementary table | [DEA shifts](shift.csv), [AMP shifts](../../../amp_transfer/results/r4-shift-426/shift.csv) |
| `tables/reaction_equilibrium_constants.tex`, generated at `scripts/final_rerun_tables.py:437` | AMP R4 cites Xu alone | Cite `silkenbaumerSolubilityCarbonDioxide1998`, Table 5, reaction IV, p. 3138, for the inverted coefficients and Xu Table 2, p. 11, for the three model estimates used by Silkenbäumer et al. | [AMP source identity](../../../amp_transfer/results/r4-shift-426/identity.json), [Silkenbäumer Table 5](https://doi.org/10.1021/ie970925w), [Xu Table 2](https://doi.org/10.1016/0255-2701(92)80002-K) |

Aroua's measured range is 303–331 K. Their approximately 14% uncertainties
apply to the three Table 4 estimates at 291, 298 and 313 K, with no given
uncertainty above 331 K. Silkenbäumer's 313.15–373.15 K law represents
model-derived values without a stated uncertainty. Above the NMR
temperature ranges (333.15 K for DEA and 318.15 K for AMP), speciation
results are calculations. Keep AMP total-pressure comparisons and grid
CO₂ partial pressures distinct.
