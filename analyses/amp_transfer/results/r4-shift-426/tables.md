The reported AMP endpoint is the #412 slope-150 fit. R4 is carbamate +
water ⇌ AMP + bicarbonate on the infinite-dilution common-molality basis,
with $m^\circ=1$ mol/kg and water explicit. The fitted law increases the
hydrolysis constant and favors the products. The referee's +1.7 estimate at
313.15 K used symmetric level bounds. The declared bounds span −3 to +2
about the source value and give the pivot shift shown below, about 4.6
conditional standard errors. The fit standard error holds the enthalpy
increment at its lower bound and the shared inputs and model form fixed.

The starting hydrolysis law inverts Silkenbäumer et al. (1998, Table 5,
reaction IV, p. 3138), which represents Xu et al.'s (1992, Table 2, p. 11)
three extended Debye–Hückel solubility-model estimates of the formation
constant. Xu gives 0.034, 0.024 and 0.0089 kg/mol at 40, 50 and 100 °C
with no stated uncertainty. The maximum log deviation of the starting
law from those estimates is given in C3. Xu's Table 3 gives apparent
carbon-13 NMR upper bounds of 0.1 L/mol at 40 °C (Sartori and Savage)
and 42 °C (Chakraborty et al.). Bosch et al. obtained 0.048 L/mol at
25 °C from absorption kinetics, with 20% stated inaccuracy (Bosch
Table 4, p. 1169). Those molarity values give order-of-magnitude
comparisons with the fitted infinite-dilution formation constants of
0.0130 and 0.0095 kg/mol at 298.15 and 313.15 K.
[Silkenbäumer Table 5](https://doi.org/10.1021/ie970925w) ·
[Xu Tables 2–3](https://doi.org/10.1016/0255-2701(92)80002-K)

At about 298 K, the retained source comparison spans 0.0075 kg/mol
(Ciftja 2011, apparent ratio converted at finite composition) to about
0.76 kg/mol (Ciftja 2014 Eq. 19, expressed at finite composition).
Ciftja 2014 gives 0.82 kg/mol at infinite dilution. Published hydrolysis
enthalpies near 298 K are 17.1 (Mehdizadeh 2013), 20.8 (Ciftja 2014),
21.2 (Xu and Silkenbäumer) and 35.8 kJ/mol (Hartono 2020).
[AMP law sources](../amp_pz_scoping/sources/carbamate-law-sources.md) ·
[Ciftja basis and residual scale](../amp_pz_scoping/sources/ciftja-2014.md)

The source-enthalpy and released variants hold the fitted $\ln K_4$
at 313.15 K and set the source-relative enthalpy increment to zero and
−10 kJ/mol, respectively. The source variant restores both source
coefficients. The fitted cost gradient of +$7.567\times10^{-5}$
per J/mol projected a 0.38 cost reduction on release. The evaluated
reduction is about 0.24 and comes from the carbamate fractions, while
the loaded-pressure cost rises. At fixed parameters, the release raises
grid carbamate above the calibration range. The calibration residual changes
sign across that range, with the endpoint mean errors exceeding
the 0.0025–0.003 absolute residual scale cited in the source assessment.
The temperature groups cover different loadings.

The grid uses 30 mass % AMP, species amounts per total amine, and vapor
CO₂ partial pressure. Tong and the supplemental Hartono 2021 rows use
total equilibrium pressure. The deviations preserve the declared
observable of every other row, including Hartono 2013 vapor AMP mole
fractions and Kundu CO₂ partial pressures. Speciation above the Ciftja
measurement range comes from the model.
The law variants quantify fixed-parameter sensitivity. The unbounded
optimum would require a refit.

[Input hashes](results/r4-shift-426/identity.json) ·
[Reported deviations](results/r4-shift-426/reported-deviations.csv) ·
[Source-enthalpy deviations](results/r4-shift-426/source-enthalpy-deviations.csv) ·
[Released deviations](results/r4-shift-426/released-deviations.csv) ·
[Source deviations](results/r4-shift-426/source-deviations.csv) ·
[Reported grid](results/r4-shift-426/reported-grid.csv) ·
[Source-enthalpy grid](results/r4-shift-426/source-enthalpy-grid.csv) ·
[Released grid](results/r4-shift-426/released-grid.csv) ·
[Source grid](results/r4-shift-426/source-grid.csv)

| T (K) | Source ln K₄ | Fitted ln K₄ | Δln K₄ | Fitted/source K₄ | Conditional SE of ln K₄ | Source range |
| --- | --- | --- | --- | --- | --- | --- |
| 298.15 | 3.015 | 4.345 | +1.330 | 3.781 | 0.265 | extrapolated |
| 313.15 | 3.424 | 4.657 | +1.233 | 3.433 | 0.265 | inside |
| 318.15 | 3.552 | 4.755 | +1.203 | 3.330 | 0.265 | inside |
| 353.00 | 4.342 | 5.358 | +1.017 | 2.764 | 0.265 | inside |
| 373.15 | 4.731 | 5.656 | +0.925 | 2.521 | 0.265 | inside |
| 393.15 | 5.079 | 5.921 | +0.843 | 2.322 | 0.265 | extrapolated |

| Table 6 quantity | Value | Conditional SE | Lower bound | Upper bound |
| --- | --- | --- | --- | --- |
| Δln K₄ at 313.15 K | +1.233 | 0.265 | -3 | +2 |
| Enthalpy increment (J/mol) | -5,000 | — | -5,000 | 5,000 |

The source and fitted hydrolysis enthalpies are 21.17 and 16.17 kJ/mol.

### Numerical controls

| Control | Outcome | Result |
| --- | --- | --- |
| C3 | comparison | T K = [313.15, 323.15, 373.15], reference = [0.034, 0.024, 0.0089], values = [0.032579490004937595, 0.025331996779310823, 0.008813500474774196], relative errors = [-0.041779705737129635, 0.05549986580461752, -0.009719047778180223], max abs log error = 0.054014461167071016 |
| C4 | passed | mapped bounds = {'level': [-3.000000000000001, 1.9999999999999991], 'enthalpy': [-4999.999999999999, 5000.000000000001]}, declared = {'level': [-3, 2], 'enthalpy': [-5000, 5000]}, stored bounds = {'level': [6.634636675032315, 11.634636675032315], 'enthalpy': [0.0, 10000.0]}, increment J mol = -4999.999999999999, relative error = 4.440892098500626e-16, limit = 1e-09 |
| C5 | passed | matched = True, rows = 270, scored = 270, cost = 62.0651105779247, reference cost = 62.0651105779247, relative cost error = 0.0, max relative prediction error = 0.0, limit = 1e-08 |
| C6 | passed | wheel sha256 = c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb |

### Fitted-row costs and replay time

| R4 law | Replayed rows | Replay (s) | Grid (s) | NMR curves (s) | Fitted cost | binary | loaded-pressure | nmr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| released | 270 | 7.63 | 5.47 | — | 61.821560 | 0.439061 | 59.876098 | 1.506400 |
| reported | 270 | 8.41 | 6.13 | — | 62.065111 | 0.439061 | 59.700995 | 1.925054 |
| source-enthalpy | 270 | 7.93 | 5.45 | — | 62.591727 | 0.439061 | 59.542183 | 2.610482 |
| source | 270 | 8.29 | 5.96 | — | 153.952496 | 0.439061 | 59.720189 | 93.793246 |

### Deviations from observations

Absorber is T ≤ 353.2 K, stripper is T ≥ 370 K, and intermediate is between. AARD and signed bias use available rows with nonzero observations.
Reaction-specific breakdowns and the observation bases are in the linked deviation CSVs.

| R4 law | Group | Role | Band | Unit | Available / rows | AARD (%) | Bias (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| released | loaded-pressure | fitted | all | Pa | 47 / 47 | 10.52 | -1.49 |
| released | loaded-pressure | fitted | absorber | Pa | 47 / 47 | 10.52 | -1.49 |
| released | binary | fitted | all | Pa | 26 / 26 | 1.03 | +1.03 |
| released | binary | fitted | absorber | Pa | 15 / 15 | 0.90 | +0.90 |
| released | binary | fitted | stripper | Pa | 11 / 11 | 1.22 | +1.22 |
| released | binary | fitted | all | dimensionless | 26 / 26 | 5.90 | +1.46 |
| released | binary | fitted | absorber | dimensionless | 15 / 15 | 6.54 | +5.72 |
| released | binary | fitted | stripper | dimensionless | 11 / 11 | 5.03 | -4.35 |
| released | nmr | fitted | all | dimensionless | 57 / 57 | 20.69 | -1.10 |
| released | nmr | fitted | absorber | dimensionless | 57 / 57 | 20.69 | -1.10 |
| released | hartono-2021-supplemental | not fitted | all | Pa | 18 / 18 | 28.33 | -28.33 |
| released | hartono-2021-supplemental | not fitted | stripper | Pa | 18 / 18 | 28.33 | -28.33 |
| released | kundu | not fitted | all | Pa | 51 / 51 | 46.79 | +39.33 |
| released | kundu | not fitted | absorber | Pa | 51 / 51 | 46.79 | +39.33 |
| released | tong-baseline | not fitted | all | Pa | 5 / 5 | 3.98 | +2.48 |
| released | tong-baseline | not fitted | absorber | Pa | 3 / 3 | 5.63 | +5.15 |
| released | tong | not fitted | all | Pa | 40 / 40 | 27.98 | -12.47 |
| released | tong | not fitted | absorber | Pa | 17 / 17 | 28.57 | +7.90 |
| released | tong-baseline | not fitted | stripper | Pa | 2 / 2 | 1.51 | -1.51 |
| released | tong | not fitted | stripper | Pa | 23 / 23 | 27.53 | -27.53 |
| reported | loaded-pressure | fitted | all | Pa | 47 / 47 | 10.49 | -1.56 |
| reported | loaded-pressure | fitted | absorber | Pa | 47 / 47 | 10.49 | -1.56 |
| reported | binary | fitted | all | Pa | 26 / 26 | 1.03 | +1.03 |
| reported | binary | fitted | absorber | Pa | 15 / 15 | 0.90 | +0.90 |
| reported | binary | fitted | stripper | Pa | 11 / 11 | 1.22 | +1.22 |
| reported | binary | fitted | all | dimensionless | 26 / 26 | 5.90 | +1.46 |
| reported | binary | fitted | absorber | dimensionless | 15 / 15 | 6.54 | +5.72 |
| reported | binary | fitted | stripper | dimensionless | 11 / 11 | 5.03 | -4.35 |
| reported | nmr | fitted | all | dimensionless | 57 / 57 | 23.82 | +2.45 |
| reported | nmr | fitted | absorber | dimensionless | 57 / 57 | 23.82 | +2.45 |
| reported | hartono-2021-supplemental | not fitted | all | Pa | 18 / 18 | 28.35 | -28.35 |
| reported | hartono-2021-supplemental | not fitted | stripper | Pa | 18 / 18 | 28.35 | -28.35 |
| reported | kundu | not fitted | all | Pa | 51 / 51 | 47.02 | +39.54 |
| reported | kundu | not fitted | absorber | Pa | 51 / 51 | 47.02 | +39.54 |
| reported | tong-baseline | not fitted | all | Pa | 5 / 5 | 3.98 | +2.48 |
| reported | tong-baseline | not fitted | absorber | Pa | 3 / 3 | 5.63 | +5.15 |
| reported | tong | not fitted | all | Pa | 40 / 40 | 27.98 | -12.54 |
| reported | tong | not fitted | absorber | Pa | 17 / 17 | 28.56 | +7.77 |
| reported | tong-baseline | not fitted | stripper | Pa | 2 / 2 | 1.51 | -1.51 |
| reported | tong | not fitted | stripper | Pa | 23 / 23 | 27.55 | -27.55 |
| source-enthalpy | loaded-pressure | fitted | all | Pa | 47 / 47 | 10.46 | -1.62 |
| source-enthalpy | loaded-pressure | fitted | absorber | Pa | 47 / 47 | 10.46 | -1.62 |
| source-enthalpy | binary | fitted | all | Pa | 26 / 26 | 1.03 | +1.03 |
| source-enthalpy | binary | fitted | absorber | Pa | 15 / 15 | 0.90 | +0.90 |
| source-enthalpy | binary | fitted | stripper | Pa | 11 / 11 | 1.22 | +1.22 |
| source-enthalpy | binary | fitted | all | dimensionless | 26 / 26 | 5.90 | +1.46 |
| source-enthalpy | binary | fitted | absorber | dimensionless | 15 / 15 | 6.54 | +5.72 |
| source-enthalpy | binary | fitted | stripper | dimensionless | 11 / 11 | 5.03 | -4.35 |
| source-enthalpy | nmr | fitted | all | dimensionless | 57 / 57 | 27.50 | +6.23 |
| source-enthalpy | nmr | fitted | absorber | dimensionless | 57 / 57 | 27.50 | +6.23 |
| source-enthalpy | hartono-2021-supplemental | not fitted | all | Pa | 18 / 18 | 28.36 | -28.36 |
| source-enthalpy | hartono-2021-supplemental | not fitted | stripper | Pa | 18 / 18 | 28.36 | -28.36 |
| source-enthalpy | kundu | not fitted | all | Pa | 51 / 51 | 47.26 | +39.76 |
| source-enthalpy | kundu | not fitted | absorber | Pa | 51 / 51 | 47.26 | +39.76 |
| source-enthalpy | tong-baseline | not fitted | all | Pa | 5 / 5 | 3.98 | +2.48 |
| source-enthalpy | tong-baseline | not fitted | absorber | Pa | 3 / 3 | 5.63 | +5.15 |
| source-enthalpy | tong | not fitted | all | Pa | 40 / 40 | 27.98 | -12.60 |
| source-enthalpy | tong | not fitted | absorber | Pa | 17 / 17 | 28.54 | +7.65 |
| source-enthalpy | tong-baseline | not fitted | stripper | Pa | 2 / 2 | 1.51 | -1.51 |
| source-enthalpy | tong | not fitted | stripper | Pa | 23 / 23 | 27.56 | -27.56 |
| source | loaded-pressure | fitted | all | Pa | 47 / 47 | 11.45 | +0.34 |
| source | loaded-pressure | fitted | absorber | Pa | 47 / 47 | 11.45 | +0.34 |
| source | binary | fitted | all | Pa | 26 / 26 | 1.03 | +1.03 |
| source | binary | fitted | absorber | Pa | 15 / 15 | 0.90 | +0.90 |
| source | binary | fitted | stripper | Pa | 11 / 11 | 1.22 | +1.22 |
| source | binary | fitted | all | dimensionless | 26 / 26 | 5.90 | +1.46 |
| source | binary | fitted | absorber | dimensionless | 15 / 15 | 6.54 | +5.72 |
| source | binary | fitted | stripper | dimensionless | 11 / 11 | 5.03 | -4.35 |
| source | nmr | fitted | all | dimensionless | 57 / 57 | 169.58 | +169.58 |
| source | nmr | fitted | absorber | dimensionless | 57 / 57 | 169.58 | +169.58 |
| source | hartono-2021-supplemental | not fitted | all | Pa | 18 / 18 | 28.28 | -28.28 |
| source | hartono-2021-supplemental | not fitted | stripper | Pa | 18 / 18 | 28.28 | -28.28 |
| source | kundu | not fitted | all | Pa | 51 / 51 | 59.50 | +52.78 |
| source | kundu | not fitted | absorber | Pa | 51 / 51 | 59.50 | +52.78 |
| source | tong-baseline | not fitted | all | Pa | 5 / 5 | 3.98 | +2.48 |
| source | tong-baseline | not fitted | absorber | Pa | 3 / 3 | 5.63 | +5.15 |
| source | tong | not fitted | all | Pa | 40 / 40 | 30.15 | -9.90 |
| source | tong | not fitted | absorber | Pa | 17 / 17 | 33.74 | +13.89 |
| source | tong-baseline | not fitted | stripper | Pa | 2 / 2 | 1.51 | -1.51 |
| source | tong | not fitted | stripper | Pa | 23 / 23 | 27.49 | -27.49 |

### Grid changes relative to the reported law

| R4 law | T (K) | Quantity | Unit | Available pairs | Minimum change | Maximum change |
| --- | --- | --- | --- | --- | --- | --- |
| released | 298.15 | CO2 partial pressure | kPa | 8 / 8 | -0.21786 | +0.00068061 |
| released | 298.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | +0.001355 | +0.0027899 |
| released | 298.15 | carbamate | mol/mol | 8 / 8 | -0.0027897 | -0.001355 |
| released | 313.15 | CO2 partial pressure | kPa | 8 / 8 | +0 | +0 |
| released | 313.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | +0 | +0 |
| released | 313.15 | carbamate | mol/mol | 8 / 8 | +0 | +0 |
| released | 333.15 | CO2 partial pressure | kPa | 8 / 8 | -0.0015357 | +0.38374 |
| released | 333.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.0013144 | -0.00070981 |
| released | 333.15 | carbamate | mol/mol | 8 / 8 | +0.00070552 | +0.0013141 |
| released | 353.15 | CO2 partial pressure | kPa | 8 / 8 | -0.0049019 | +0.99837 |
| released | 353.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.0015233 | -0.00085162 |
| released | 353.15 | carbamate | mol/mol | 8 / 8 | +0.00080647 | +0.0015223 |
| released | 373.15 | CO2 partial pressure | kPa | 8 / 8 | -0.01361 | +1.8406 |
| released | 373.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.0014003 | -0.00079973 |
| released | 373.15 | carbamate | mol/mol | 8 / 8 | +0.0007752 | +0.0013979 |
| released | 393.15 | CO2 partial pressure | kPa | 8 / 8 | -0.038248 | +2.5277 |
| released | 393.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.0012114 | -0.00069796 |
| released | 393.15 | carbamate | mol/mol | 8 / 8 | +0.00069883 | +0.0012058 |
| source-enthalpy | 298.15 | CO2 partial pressure | kPa | 8 / 8 | -0.00074146 | +0.23795 |
| source-enthalpy | 298.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.0029737 | -0.001433 |
| source-enthalpy | 298.15 | carbamate | mol/mol | 8 / 8 | +0.0014331 | +0.0029735 |
| source-enthalpy | 313.15 | CO2 partial pressure | kPa | 8 / 8 | +0 | +0 |
| source-enthalpy | 313.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | +0 | +0 |
| source-enthalpy | 313.15 | carbamate | mol/mol | 8 / 8 | +0 | +0 |
| source-enthalpy | 333.15 | CO2 partial pressure | kPa | 8 / 8 | -0.34327 | +0.001369 |
| source-enthalpy | 333.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | +0.00064407 | +0.0011881 |
| source-enthalpy | 333.15 | carbamate | mol/mol | 8 / 8 | -0.0011878 | -0.00063477 |
| source-enthalpy | 353.15 | CO2 partial pressure | kPa | 8 / 8 | -0.80696 | +0.0039347 |
| source-enthalpy | 353.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | +0.00069702 | +0.001245 |
| source-enthalpy | 353.15 | carbamate | mol/mol | 8 / 8 | -0.0012442 | -0.00065529 |
| source-enthalpy | 373.15 | CO2 partial pressure | kPa | 8 / 8 | -1.3583 | +0.01007 |
| source-enthalpy | 373.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | +0.00059807 | +0.0010426 |
| source-enthalpy | 373.15 | carbamate | mol/mol | 8 / 8 | -0.0010407 | -0.00057404 |
| source-enthalpy | 393.15 | CO2 partial pressure | kPa | 8 / 8 | -1.7191 | +0.026031 |
| source-enthalpy | 393.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | +0.00047943 | +0.00082893 |
| source-enthalpy | 393.15 | carbamate | mol/mol | 8 / 8 | -0.00082506 | -0.00048003 |
| source | 298.15 | CO2 partial pressure | kPa | 8 / 8 | -0.017748 | +5.986 |
| source | 298.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.05899 | -0.025819 |
| source | 298.15 | carbamate | mol/mol | 8 / 8 | +0.025819 | +0.058976 |
| source | 313.15 | CO2 partial pressure | kPa | 8 / 8 | -0.020368 | +5.8319 |
| source | 313.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.037659 | -0.01827 |
| source | 313.15 | carbamate | mol/mol | 8 / 8 | +0.018271 | +0.037656 |
| source | 333.15 | CO2 partial pressure | kPa | 8 / 8 | -0.025668 | +6.276 |
| source | 333.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.019881 | -0.010431 |
| source | 333.15 | carbamate | mol/mol | 8 / 8 | +0.010432 | +0.019877 |
| source | 353.15 | CO2 partial pressure | kPa | 8 / 8 | -0.035731 | +7.1262 |
| source | 353.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.01049 | -0.0057761 |
| source | 353.15 | carbamate | mol/mol | 8 / 8 | +0.0056556 | +0.010483 |
| source | 373.15 | CO2 partial pressure | kPa | 8 / 8 | -0.056437 | +7.6681 |
| source | 373.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.0057432 | -0.0032542 |
| source | 373.15 | carbamate | mol/mol | 8 / 8 | +0.0032095 | +0.0057332 |
| source | 393.15 | CO2 partial pressure | kPa | 8 / 8 | -0.10512 | +6.9525 |
| source | 393.15 | bicarbonate+carbonate | mol/mol | 8 / 8 | -0.0033111 | -0.0019002 |
| source | 393.15 | carbamate | mol/mol | 8 / 8 | +0.0019026 | +0.0032958 |

### AMP total-pressure sensitivity at not-fitted observations

| R4 law | Campaign | Band | Available pairs | Reported-law AARD (%) | Min ΔP (kPa) | Max ΔP (kPa) |
| --- | --- | --- | --- | --- | --- | --- |
| released | tong-2012 | absorber | 20 / 20 | 25.12 | +0 | +1.417 |
| released | tong-2012 | stripper | 25 / 25 | 25.47 | -0.02359 | +1.647 |
| released | hartono-2021-supplemental | stripper | 18 / 18 | 28.35 | -0.03226 | +0.6456 |
| reported | tong-2012 | absorber | 20 / 20 | 25.12 | +0 | +0 |
| reported | tong-2012 | stripper | 25 / 25 | 25.47 | +0 | +0 |
| reported | hartono-2021-supplemental | stripper | 18 / 18 | 28.35 | +0 | +0 |
| source-enthalpy | tong-2012 | absorber | 20 / 20 | 25.12 | -1.266 | +0 |
| source-enthalpy | tong-2012 | stripper | 25 / 25 | 25.47 | -1.215 | +0.01579 |
| source-enthalpy | hartono-2021-supplemental | stripper | 18 / 18 | 28.35 | -0.477 | +0.02183 |
| source | tong-2012 | absorber | 20 / 20 | 25.12 | +0 | +46.3 |
| source | tong-2012 | stripper | 25 / 25 | 25.47 | -0.06586 | +6.85 |
| source | hartono-2021-supplemental | stripper | 18 / 18 | 28.35 | -0.08949 | +2.697 |

### Reported residuals at the calibration temperatures

| T (K) | Rows | Mean observed carbamate (mol/mol) | Mean predicted minus observed (mol/mol) |
| --- | --- | --- | --- |
| 298.15 | 17 | 0.02500 | +0.00656 |
| 308.15 | 24 | 0.02413 | -0.00166 |
| 318.15 | 16 | 0.02131 | -0.00576 |
