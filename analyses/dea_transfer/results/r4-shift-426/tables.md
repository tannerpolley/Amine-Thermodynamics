| T (K) | Source ln K₄ | Fitted ln K₄ | Δln K₄ | Fitted/source K₄ | Conditional SE of ln K₄ | Source range |
| --- | --- | --- | --- | --- | --- | --- |
| 293.15 | -2.200 | -3.195 | -0.995 | 0.370 | 0.648 | extrapolated |
| 298.15 | -1.965 | -3.043 | -1.078 | 0.340 | 0.640 | extrapolated |
| 303.00 | -1.745 | -2.900 | -1.155 | 0.315 | 0.632 | inside |
| 313.15 | -1.306 | -2.615 | -1.309 | 0.270 | 0.618 | inside |
| 331.00 | -0.600 | -2.157 | -1.557 | 0.211 | 0.594 | inside |
| 380.37 | 1.008 | -1.113 | -2.121 | 0.120 | 0.543 | extrapolated |
| 393.15 | 1.358 | -0.886 | -2.244 | 0.106 | 0.532 | extrapolated |
| 394.26 | 1.388 | -0.867 | -2.255 | 0.105 | 0.531 | extrapolated |

| Table 6 quantity | Value | Conditional SE | Lower bound | Upper bound |
| --- | --- | --- | --- | --- |
| Δln K₄ at 313.15 K | -1.309 | 0.618 | -3 | +3 |
| Enthalpy increment (J/mol) | -11,968 | 1,344 | -30,000 | 10,000 |

The source and fitted hydrolysis enthalpies are 34.10 and 22.13 kJ/mol.

### Numerical controls

| Control | Outcome | Result |
| --- | --- | --- |
| C1 | passed | coefficients = [11.789235676129515, -4100.9040506223955], reference = [11.789235676129515, -4100.9040506223955], relative error = 0.0, limit = 1e-12 |
| C2 | passed | T K = [291, 298, 313], reference = [0.1, 0.14, 0.268], values = [0.099936718722653, 0.1391521538463255, 0.2690940861042928], relative errors = [-0.0006328127734700484, -0.006056043954817847, 0.004082410836913297], limits = [0.020667473180975726, 0.01912191555718845, 0.017201378596307437] |
| C4 | passed | mapped bounds = {'level': [-2.999999999999999, 3.0000000000000018], 'enthalpy': [-30000.0, 9999.999999999998]}, declared = {'level': [-3, 3], 'enthalpy': [-30000, 10000]}, stored bounds = {'level': [4.192498214341383, 10.192498214341384], 'enthalpy': [-18031.59432899114, 21968.40567100886]}, increment J mol = -11968.40567100886, relative error = 6.661338147750939e-16, limit = 1e-09 |
| C5 | passed | matched = True, rows = 299, scored = 299, cost = 8.082968228315169, reference cost = 8.082968228315169, relative cost error = 0.0, max relative prediction error = 0.0, limit = 1e-08 |
| C6 | passed | wheel sha256 = c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb |

### Fitted-row costs and replay time

| R4 law | Replayed rows | Replay (s) | Grid (s) | NMR curves (s) | Fitted cost | Carson | Lawson |
| --- | --- | --- | --- | --- | --- | --- | --- |
| reported | 299 | 8.56 | 1.92 | 3.42 | 8.082968 | 0.179077 | 7.903892 |
| source | 299 | 9.48 | 1.93 | 3.48 | 44.652034 | 25.402668 | 19.249366 |

### Deviations from observations

Absorber is T ≤ 353.2 K, stripper is T ≥ 370 K, and intermediate is between. AARD and signed bias use available rows with nonzero observations.
Reaction-specific breakdowns and the observation bases are in the linked deviation CSVs.

| R4 law | Group | Role | Band | Unit | Available / rows | AARD (%) | Bias (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| reported | Lawson | fitted | all | Pa | 30 / 30 | 28.51 | -0.65 |
| reported | Lawson | fitted | absorber | Pa | 19 / 19 | 34.49 | +8.39 |
| reported | Lawson | fitted | intermediate | Pa | 8 / 8 | 17.99 | -15.36 |
| reported | Lawson | fitted | stripper | Pa | 3 / 3 | 18.70 | -18.70 |
| reported | Carson | fitted | all | J/mol CO2 | 50 / 50 | 0.94 | -0.12 |
| reported | Carson | fitted | absorber | J/mol CO2 | 50 / 50 | 0.94 | -0.12 |
| reported | Lawson-394K | not fitted | all | Pa | 7 / 7 | 22.95 | -22.95 |
| reported | Lawson-394K | not fitted | stripper | Pa | 7 / 7 | 22.95 | -22.95 |
| reported | SeoHong | not fitted | all | Pa | 16 / 16 | 85.36 | +83.59 |
| reported | SeoHong | not fitted | absorber | Pa | 16 / 16 | 85.36 | +83.59 |
| reported | Lal | not fitted | all | Pa | 44 / 44 | 47.41 | -30.30 |
| reported | Lal | not fitted | absorber | Pa | 17 / 17 | 55.79 | -52.94 |
| reported | Lal | not fitted | stripper | Pa | 27 / 27 | 42.13 | -16.04 |
| reported | Weiland | comparison only | all | kg/m3 | 44 / 44 | 0.70 | -0.47 |
| reported | Weiland | comparison only | absorber | kg/m3 | 44 / 44 | 0.70 | -0.47 |
| reported | Lawson-VIII | comparison only | all | Pa | 10 / 10 | 38.73 | -20.03 |
| reported | Lawson-VIII | comparison only | absorber | Pa | 6 / 6 | 32.83 | -1.66 |
| reported | Lawson-VIII | comparison only | intermediate | Pa | 4 / 4 | 47.57 | -47.57 |
| reported | Bottinger-DEA_plus_DEAH | comparison only | all | mol/mol | 25 / 25 | 7.48 | -7.33 |
| reported | Bottinger-DEA_plus_DEAH | comparison only | absorber | mol/mol | 25 / 25 | 7.48 | -7.33 |
| reported | Bottinger-DEACOO | comparison only | all | mol/mol | 25 / 25 | 59.20 | +58.34 |
| reported | Bottinger-DEACOO | comparison only | absorber | mol/mol | 25 / 25 | 59.20 | +58.34 |
| reported | Bottinger-HCO3 | comparison only | all | mol/mol | 25 / 25 | 33.21 | -33.21 |
| reported | Bottinger-HCO3 | comparison only | absorber | mol/mol | 25 / 25 | 33.21 | -33.21 |
| reported | Cai | comparison only | all | Pa | 9 / 9 | 40.82 | +33.59 |
| reported | Cai | comparison only | stripper | Pa | 6 / 6 | 56.86 | +54.65 |
| reported | Horstmann | comparison only | all | J/mol mixture | 14 / 14 | 152.45 | -152.45 |
| reported | Horstmann | comparison only | intermediate | J/mol mixture | 14 / 14 | 152.45 | -152.45 |
| reported | Cai | comparison only | intermediate | Pa | 1 / 1 | 23.64 | -23.64 |
| reported | Cai | comparison only | absorber | Pa | 2 / 2 | 1.29 | -0.99 |
| source | Lawson | fitted | all | Pa | 30 / 30 | 39.51 | -12.88 |
| source | Lawson | fitted | absorber | Pa | 19 / 19 | 44.76 | -12.92 |
| source | Lawson | fitted | intermediate | Pa | 8 / 8 | 31.83 | -14.30 |
| source | Lawson | fitted | stripper | Pa | 3 / 3 | 26.71 | -8.87 |
| source | Carson | fitted | all | J/mol CO2 | 50 / 50 | 14.09 | +14.09 |
| source | Carson | fitted | absorber | J/mol CO2 | 50 / 50 | 14.09 | +14.09 |
| source | Lawson-394K | not fitted | all | Pa | 7 / 7 | 24.02 | -0.99 |
| source | Lawson-394K | not fitted | stripper | Pa | 7 / 7 | 24.02 | -0.99 |
| source | SeoHong | not fitted | all | Pa | 16 / 16 | 113.40 | +87.53 |
| source | SeoHong | not fitted | absorber | Pa | 16 / 16 | 113.40 | +87.53 |
| source | Lal | not fitted | all | Pa | 44 / 44 | 169.05 | +168.58 |
| source | Lal | not fitted | absorber | Pa | 17 / 17 | 34.65 | +33.44 |
| source | Lal | not fitted | stripper | Pa | 27 / 27 | 253.67 | +253.67 |
| source | Weiland | comparison only | all | kg/m3 | 44 / 44 | 0.61 | -0.37 |
| source | Weiland | comparison only | absorber | kg/m3 | 44 / 44 | 0.61 | -0.37 |
| source | Lawson-VIII | comparison only | all | Pa | 10 / 10 | 27.47 | +0.78 |
| source | Lawson-VIII | comparison only | absorber | Pa | 6 / 6 | 24.33 | -20.14 |
| source | Lawson-VIII | comparison only | intermediate | Pa | 4 / 4 | 32.18 | +32.18 |
| source | Bottinger-DEA_plus_DEAH | comparison only | all | mol/mol | 25 / 25 | 4.19 | -0.06 |
| source | Bottinger-DEA_plus_DEAH | comparison only | absorber | mol/mol | 25 / 25 | 4.19 | -0.06 |
| source | Bottinger-DEACOO | comparison only | all | mol/mol | 25 / 25 | 22.45 | +18.72 |
| source | Bottinger-DEACOO | comparison only | absorber | mol/mol | 25 / 25 | 22.45 | +18.72 |
| source | Bottinger-HCO3 | comparison only | all | mol/mol | 25 / 25 | 13.25 | -5.65 |
| source | Bottinger-HCO3 | comparison only | absorber | mol/mol | 25 / 25 | 13.25 | -5.65 |
| source | Cai | comparison only | all | Pa | 9 / 9 | 40.82 | +33.59 |
| source | Cai | comparison only | stripper | Pa | 6 / 6 | 56.86 | +54.65 |
| source | Horstmann | comparison only | all | J/mol mixture | 14 / 14 | 152.45 | -152.45 |
| source | Horstmann | comparison only | intermediate | J/mol mixture | 14 / 14 | 152.45 | -152.45 |
| source | Cai | comparison only | intermediate | Pa | 1 / 1 | 23.64 | -23.64 |
| source | Cai | comparison only | absorber | Pa | 2 / 2 | 1.29 | -0.99 |

### Grid changes relative to the reported law

| R4 law | T (K) | Quantity | Unit | Available pairs | Minimum change | Maximum change |
| --- | --- | --- | --- | --- | --- | --- |
| source | 313.15 | CO2 partial pressure | kPa | 7 / 7 | -79.722 | +1.86 |
| source | 313.15 | bicarbonate+carbonate | mol/mol | 7 / 7 | +0.0078102 | +0.084623 |
| source | 313.15 | carbamate | mol/mol | 7 / 7 | -0.084402 | -0.0078165 |
| source | 393.15 | CO2 partial pressure | kPa | 7 / 7 | -185.81 | +147.12 |
| source | 393.15 | bicarbonate+carbonate | mol/mol | 7 / 7 | +0.045112 | +0.19867 |
| source | 393.15 | carbamate | mol/mol | 7 / 7 | -0.17422 | -0.04659 |
