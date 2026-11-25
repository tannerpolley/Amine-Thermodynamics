# Round 5 manuscript handoff

These calculations compare declared EOS fits, pressure and composition paths, and observation groups. Numerical agreement and phase searches apply to the checks and supports recorded for each case. Results are for investigator review.

## A. AMP pressure calibration and phase behavior

| Data design | Slope family | Slope (K) | Objective | Phase search | Completed / attempted | Descents | Confirmed LL | Retained records |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original | free | -219.25135 | 61.28527532 | retained original | 666 / 666 | 93 | 73 | [original-main.json.gz](results/A/original-main.json.gz) · [phase-controls.json.gz](results/A/phase-controls.json.gz) · [original slope](../amp_transfer/results/retransfer-412-f2-05e94210/main/parameters.json) |
| original | fixed | −150 | 62.06511058 | retained original | 666 / 666 | 0 | 0 | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · [phase-controls.json.gz](results/A/phase-controls.json.gz) |
| expanded | free | -181.09022 | 72.73322264 | native | 666 / 666 | 0 | 0 | [expanded-free.json.gz](results/A/expanded-free.json.gz) · [search-free-native-full.json.gz](results/A/search-free-native-full.json.gz) |
| expanded | free | -181.09022 | 72.73322264 | supplied | 666 / 666 | 0 | 0 | [expanded-free.json.gz](results/A/expanded-free.json.gz) · [search-free-supplied-full.json.gz](results/A/search-free-supplied-full.json.gz) |
| expanded | fixed | -150 | 72.85609695 | native | 666 / 666 | 0 | 0 | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · [search-fixed-native-full.json.gz](results/A/search-fixed-native-full.json.gz) |
| expanded | fixed | -150 | 72.85609695 | supplied | 666 / 666 | 0 | 0 | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · [search-fixed-supplied-full.json.gz](results/A/search-fixed-supplied-full.json.gz) |

The added pressure rows enter the fit. The five zero-loading Tong rows and the Kundu partial pressures remain comparisons. The original fitted-residual replay and the row-level changes are retained in [crosswalk.json.gz](results/A/crosswalk.json.gz) · `rows`.

The loaded-pressure block grows from 47 to 105 observations. The coefficient multiplying each squared log-pressure residual in twice the objective changes from 94.5626 to 42.328. [crosswalk.json.gz](results/A/crosswalk.json.gz) · `rows`

| Endpoint | Source block | Observable | Role | Rows | AARD (%) | Signed bias (%) | Mean absolute error | Unit | Retained record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original-main | loaded-pressure | pressure | fitted | 47 | 10.3389 | -1.2057 | 21261.7 | Pa | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-main | binary | pressure | fitted | 26 | 1.14462 | 1.10133 | 770.752 | Pa | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-main | binary | mole_fraction | fitted | 26 | 3.68556 | 2.03189 | 0.000409223 | dimensionless | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-main | nmr | amount_ratio | fitted | 57 | 25.5484 | 3.70203 | 0.00528168 | dimensionless | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-main | hartono-2021-supplemental | pressure | not fitted | 18 | 28.0992 | -28.0992 | 104769 | Pa | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-main | kundu | partial_pressure | not fitted | 51 | 43.9125 | 38.0136 | 15412.2 | Pa | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-main | tong-baseline | pressure | not fitted | 5 | 3.64533 | 2.47387 | 1021.27 | Pa | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-main | tong | pressure | not fitted | 40 | 28.1625 | -12.1612 | 76912.1 | Pa | [original-main.json.gz](results/A/original-main.json.gz) · `original.scores` |
| original-slope-150 | loaded-pressure | pressure | fitted | 47 | 10.4864 | -1.5608 | 21454.5 | Pa | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| original-slope-150 | binary | pressure | fitted | 26 | 1.03141 | 1.03141 | 622.77 | Pa | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| original-slope-150 | binary | mole_fraction | fitted | 26 | 5.89876 | 1.46154 | 0.000564972 | dimensionless | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| original-slope-150 | nmr | amount_ratio | fitted | 57 | 23.8154 | 2.45198 | 0.0050639 | dimensionless | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| original-slope-150 | hartono-2021-supplemental | pressure | not fitted | 18 | 28.3485 | -28.3485 | 104807 | Pa | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| original-slope-150 | kundu | partial_pressure | not fitted | 51 | 47.0155 | 39.5391 | 16639.9 | Pa | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| original-slope-150 | tong-baseline | pressure | not fitted | 5 | 3.98213 | 2.4838 | 1286.01 | Pa | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| original-slope-150 | tong | pressure | not fitted | 40 | 27.9779 | -12.5399 | 75555.4 | Pa | [original-slope-150.json.gz](results/A/original-slope-150.json.gz) · `original.scores` |
| expanded-free | loaded-pressure | pressure | fitted | 47 | 11.7889 | 3.86308 | 28024.2 | Pa | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-free | binary | pressure | fitted | 26 | 1.11441 | 1.09213 | 736.898 | Pa | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-free | binary | mole_fraction | fitted | 26 | 3.88895 | 1.97625 | 0.000428225 | dimensionless | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-free | nmr | amount_ratio | fitted | 57 | 21.256 | 4.95488 | 0.00438427 | dimensionless | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-free | hartono-2021-supplemental | pressure | fitted | 18 | 6.74328 | -5.10146 | 24175.6 | Pa | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-free | tong | pressure | fitted | 40 | 11.0935 | -2.73569 | 32363.4 | Pa | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-free | kundu | partial_pressure | not fitted | 51 | 15.6668 | 2.69652 | 5913.03 | Pa | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-free | tong-baseline | pressure | not fitted | 5 | 3.72746 | 2.48156 | 1083.53 | Pa | [expanded-free.json.gz](results/A/expanded-free.json.gz) · `expanded.scores` |
| expanded-fixed | loaded-pressure | pressure | fitted | 47 | 11.7645 | 3.78657 | 28205.6 | Pa | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |
| expanded-fixed | binary | pressure | fitted | 26 | 1.06202 | 1.06202 | 654.554 | Pa | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |
| expanded-fixed | binary | mole_fraction | fitted | 26 | 5.37596 | 1.79188 | 0.000524753 | dimensionless | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |
| expanded-fixed | nmr | amount_ratio | fitted | 57 | 21.2873 | 5.20484 | 0.00437964 | dimensionless | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |
| expanded-fixed | hartono-2021-supplemental | pressure | fitted | 18 | 6.70838 | -4.83451 | 24090.3 | Pa | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |
| expanded-fixed | tong | pressure | fitted | 40 | 11.0294 | -2.71933 | 32321.9 | Pa | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |
| expanded-fixed | kundu | partial_pressure | not fitted | 51 | 15.2869 | 1.89763 | 5916.97 | Pa | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |
| expanded-fixed | tong-baseline | pressure | not fitted | 5 | 3.92916 | 2.49595 | 1238.06 | Pa | [expanded-fixed.json.gz](results/A/expanded-fixed.json.gz) · `expanded.scores` |

At S14 the four bubble references set a common pressure of 2037241.251 Pa. [common-pressure.json.gz](results/A/common-pressure.json.gz) · `common_Pa`

| Endpoint | Bubble pressure (Pa) | Margin (Pa) | Vapor TPD/RT | Liquid TPD/RT | Gibbs decrease / RT (mol) | Paired error (mol) | Retained record |
| --- | --- | --- | --- | --- | --- | --- | --- |
| expanded-fixed | 1940229.76 | 97011.4881 | 0.0461454 | 5.68434e-14 | — | — | [common-pressure.json.gz](results/A/common-pressure.json.gz) · `outcomes.expanded-fixed` |
| expanded-free | 1907238.1 | 130003.153 | 0.0623843 | -2.84217e-14 | — | — | [common-pressure.json.gz](results/A/common-pressure.json.gz) · `outcomes.expanded-free` |
| original-main | 1154753.29 | 882487.963 | 0.534919 | -0.00364094 | 0.0184966 | 2.81141e-09 | [common-pressure.json.gz](results/A/common-pressure.json.gz) · `outcomes.original-main` |
| original-slope-150 | 1238249.64 | 798991.613 | 0.462645 | 2.84217e-14 | — | — | [common-pressure.json.gz](results/A/common-pressure.json.gz) · `outcomes.original-slope-150` |

| Data design | Stage variance | Nominal ΔC cutoff | Slope brackets (K) | Retained record |
| --- | --- | --- | --- | --- |
| original | 0.822621 | 1.58003 | -1: -365.345 to -365.736, 1: -134.375 to -133.984 | [profile-original.json](results/A/profile-original.json) |
| expanded | 0.706148 | 1.35632 | -1: -283.043 to -283.434, 1: -77.6739 to -77.2357 | [profile-expanded.json](results/A/profile-expanded.json) |

The thresholds describe the declared weighted objectives. Correlated observations and heuristic weights limit statistical interpretation.

## B. Aqueous reference convention

| Feed | Reference | System P (Pa) | Gibbs decrease / RT (mol) | Paired error (mol) | Largest neutral transfer / RT | Pair disposition | Retained record |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S14 | 100-kPa | 1212490.953 | 0.0188247 | 2.81199e-09 | 1.7053e-13 | persists | [reactions.json.gz](results/B/reactions.json.gz) · `S14.100-kPa` |
| S14 | baseline | 1212490.953 | 0.0188141 | 2.82172e-09 | 1.49214e-13 | persists | [reactions.json.gz](results/B/reactions.json.gz) · `S14.baseline` |
| comparison:363:final | 100-kPa | 1121000 | 0.00188972 | 1.06158e-07 | 2.10321e-12 | persists | [reactions.json.gz](results/B/reactions.json.gz) · `comparison:363:final.100-kPa` |
| comparison:363:final | baseline | 1121000 | 0.00193713 | 1.23695e-07 | 1.36424e-12 | persists | [reactions.json.gz](results/B/reactions.json.gz) · `comparison:363:final.baseline` |
| grid:{'water': 1.7987685418415897, 'methyldiethanolamine': 1.0}:373.15:1.3:1.05 | 100-kPa | 203126858.9 | — | — | — | undecided | [reactions.json.gz](results/B/reactions.json.gz) · `grid:{'water': 1.7987685418415897, 'methyldiethanolamine': 1.0}:373.15:1.3:1.05.100-kPa` |
| grid:{'water': 1.7987685418415897, 'methyldiethanolamine': 1.0}:373.15:1.3:1.05 | baseline | 203126858.9 | 0.000249499 | 7.65654e-10 | 1.34037e-10 | undecided | [reactions.json.gz](results/B/reactions.json.gz) · `grid:{'water': 1.7987685418415897, 'methyldiethanolamine': 1.0}:373.15:1.3:1.05.baseline` |

Each convention uses one composition-independent species-standard vector at fixed temperature and system pressure. The empirical reaction law supplies its temperature dependence. Any dependence of the completed vector on pressure comes through the fugacity reference conversion. The retained volume and enthalpy derivatives apply to the added standard vector. The reported EOS volume and calorics exclude that additional term. The highest-pressure state is extreme extrapolation. [reactions.json.gz](results/B/reactions.json.gz) · `rows`

| MDEA T (K) | System P (Pa) | Reference | Support | Candidate P (Pa) | Qualified in search | Gibbs / RT (mol) | Check missed or solver message | Retained record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 288.71 | 1121000 | baseline | L | — | yes | -2730.682667 | — | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[0]` |
| 288.71 | 1121000 | baseline | L1+L2 | 1121000 | yes | -2730.684605 | — | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[0]` |
| 288.71 | 1121000 | baseline | L+V | — | no | — | phase V vanished: its amount reached at most PHASE_DISAPPEARANCE_AMOUNT of the feed | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[0]` |
| 288.71 | 1121000 | baseline | L1+L2+incipient V | 3735.156313 | no | — | physical closure, pressure-root readback | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[0]` |
| 288.71 | 1121000 | 100-kPa | L | — | yes | -2730.651643 | — | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[1]` |
| 288.71 | 1121000 | 100-kPa | L1+L2 | 1121000 | yes | -2730.653533 | — | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[1]` |
| 288.71 | 1121000 | 100-kPa | L+V | — | no | — | phase V vanished: its amount reached at most PHASE_DISAPPEARANCE_AMOUNT of the feed | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[1]` |
| 288.71 | 1121000 | 100-kPa | L1+L2+incipient V | 3739.890067 | no | — | physical closure, pressure-root readback | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[1]` |
| 373.15 | 203126858.9 | baseline | L | — | yes | -525.9223677 | — | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[2]` |
| 373.15 | 203126858.9 | baseline | L1+L2 | 203126858.9 | yes | -525.9226172 | — | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[2]` |
| 373.15 | 203126858.9 | baseline | L+V | — | no | — | phase V vanished: its amount reached at most PHASE_DISAPPEARANCE_AMOUNT of the feed | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[2]` |
| 373.15 | 203126858.9 | baseline | L1+L2+incipient V | — | no | — | phase L1 vanished: its amount reached at most PHASE_DISAPPEARANCE_AMOUNT of the feed | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[2]` |
| 373.15 | 203126858.9 | 100-kPa | L | — | yes | -524.3707447 | — | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[3]` |
| 373.15 | 203126858.9 | 100-kPa | L1+L2 | — | no | — | Seeded attempts did not confirm distinct liquid roots below parent Gibbs beyond paired error. | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[3]` |
| 373.15 | 203126858.9 | 100-kPa | L+V | 203126858.9 | no | -524.4614143 | pressure-root readback | [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) · `rows[3]` |

The L+V searches use the reevaluated liquid parent and the default vapor initialization. The two-liquid candidates use the archived pair seeds. The incipient vapor calculation solves for pressure separately and is excluded from the fixed-pressure Gibbs comparison.

| Feed in order above | Reference | Parent standard V (m³) | Parent standard H (J) | Retained record |
| --- | --- | --- | --- | --- |
| 1 | 100-kPa | 0 | -7.11044e+06 | [reactions.json.gz](results/B/reactions.json.gz) · `rows[0].conventions.100-kPa.derivative_estimates` |
| 1 | baseline | -9.51429e-05 | -7.11065e+06 | [reactions.json.gz](results/B/reactions.json.gz) · `rows[0].conventions.baseline.derivative_estimates` |
| 2 | 100-kPa | 0 | -5.49577e+06 | [reactions.json.gz](results/B/reactions.json.gz) · `rows[1].conventions.100-kPa.derivative_estimates` |
| 2 | baseline | -7.29641e-05 | -5.50835e+06 | [reactions.json.gz](results/B/reactions.json.gz) · `rows[1].conventions.baseline.derivative_estimates` |
| 3 | 100-kPa | 0 | -1.30942e+06 | [reactions.json.gz](results/B/reactions.json.gz) · `rows[2].conventions.100-kPa.derivative_estimates` |
| 3 | baseline | -2.56738e-05 | -1.42736e+06 | [reactions.json.gz](results/B/reactions.json.gz) · `rows[2].conventions.baseline.derivative_estimates` |

## C. Objective contributions and weights

| Reported model | C | Interior rank | All-row variance | Stage variance | Retained record |
| --- | --- | --- | --- | --- | --- |
| AMP | 62.06511058 | 6 | 0.827534808 | 0.827534808 | [reported-objectives.json](results/C/reported-objectives.json) · `models.AMP` |
| DEA | 8.082968228 | 4 | 0.21270969 | 0.21270969 | [reported-objectives.json](results/C/reported-objectives.json) · `models.DEA` |
| MDEA | 564.4836961 | 6 | 4.10533597 | 4.15061398 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA` |
| MEA | 150.7629029 | 10 | 1.0152384 | 1.16869941 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA` |

| Reported model | Observable | Rows | Objective contribution | Weight sum | Retained record |
| --- | --- | --- | --- | --- | --- |
| AMP | amount_ratio | 57 | 1.9250544 | 1 | [reported-objectives.json](results/C/reported-objectives.json) · `models.AMP.groups.amount_ratio` |
| AMP | mole_fraction | 26 | 0.42576573 | 0.5 | [reported-objectives.json](results/C/reported-objectives.json) · `models.AMP.groups.mole_fraction` |
| AMP | total pressure | 73 | 59.71429 | 4644.4444 | [reported-objectives.json](results/C/reported-objectives.json) · `models.AMP.groups.total pressure` |
| DEA | Carson addition enthalpy | 50 | 0.1790765 | 1 | [reported-objectives.json](results/C/reported-objectives.json) · `models.DEA.groups.Carson addition enthalpy` |
| DEA | partial_pressure | 30 | 7.9038917 | 123.45679 | [reported-objectives.json](results/C/reported-objectives.json) · `models.DEA.groups.partial_pressure` |
| MDEA | Carson addition enthalpy | 40 | 25.868202 | 40 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA.groups.Carson addition enthalpy` |
| MDEA | Merkley addition enthalpy | 4 | 8.4512282 | 4 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA.groups.Merkley addition enthalpy` |
| MDEA | carbonate | 8 | 4.0219721 | 8 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA.groups.carbonate` |
| MDEA | cation | 8 | 17.917979 | 8 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA.groups.cation` |
| MDEA | equilibrium_isobaric_heat_capacity | 33 | 36.890182 | 33 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA.groups.equilibrium_isobaric_heat_capacity` |
| MDEA | mass density | 57 | 453.60885 | 241 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA.groups.mass density` |
| MDEA | total pressure | 131 | 17.725287 | 739.33333 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MDEA.groups.total pressure` |
| MEA | addition_enthalpy | 8 | 1.38648 | 8 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.addition_enthalpy` |
| MEA | amount_ratio | 6 | 12.74575 | 6 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.amount_ratio` |
| MEA | equilibrium_isobaric_heat_capacity | 4 | 6.6483493 | 4 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.equilibrium_isobaric_heat_capacity` |
| MEA | mole_fraction | 126 | 70.699674 | 126 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.mole_fraction` |
| MEA | partial_pressure | 47 | 5.9625534 | 522.22222 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.partial_pressure` |
| MEA | phase_density | 52 | 13.495509 | 51 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.phase_density` |
| MEA | temperature | 25 | 39.823909 | 25 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.temperature` |
| MEA | total pressure | 39 | 0.0006790195 | 1 | [reported-objectives.json](results/C/reported-objectives.json) · `models.MEA.groups.total pressure` |

| Conditional MEA k | Objective | Increase | Nominal cutoff | Retained record |
| --- | --- | --- | --- | --- |
| 0.765000023 | 150.7628847 | 0 | 2.2447557 | [reported-objectives.json](results/C/reported-objectives.json) · `MEA_profile[0]` · [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `delta_cutoff` |
| -0.5 | 166.651406 | 15.888521 | 2.2447557 | [reported-objectives.json](results/C/reported-objectives.json) · `MEA_profile[1]` · [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `delta_cutoff` |
| 0.132500012 | 151.7858891 | 1.0230044 | 2.2447557 | [reported-objectives.json](results/C/reported-objectives.json) · `MEA_profile[2]` · [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `delta_cutoff` |
| 1 | 150.7865582 | 0.02367353 | 2.2447557 | [reported-objectives.json](results/C/reported-objectives.json) · `MEA_profile[3]` · [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `delta_cutoff` |

| MEA fixed k | Replayed objective | Retained objective | Increase | Retained record |
| --- | --- | --- | --- | --- |
| 0.765000023 | 150.7628847 | 150.7628847 | 0 | [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `rows[0]` |
| -0.5 | 166.651406 | 166.651406 | 15.888521 | [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `rows[1]` |
| 0.132500012 | 151.7858891 | 151.7858891 | 1.0230044 | [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `rows[2]` |
| 1 | 150.7865582 | 150.7865582 | 0.02367353 | [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `rows[3]` |

The retained lower MEA crossing lies between -0.5 and 0.1325. The scan approaches the upper bound with no crossing. [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) · `rows`

| Fixed MDEA k | Objective | Retained record |
| --- | --- | --- |
| 0.132500012 | 541.0792552 | [MDEA-k-low.json.gz](results/C/MDEA-k-low.json.gz) · `information` |
| 0.765000023 | 564.4836961 | [MDEA-k-reported.json.gz](results/C/MDEA-k-reported.json.gz) · `information` |
| 1 | 565.9424986 | [MDEA-k-high.json.gz](results/C/MDEA-k-high.json.gz) · `information` |

The profile thresholds are nominal objective-scale sensitivities for the declared weights. The MDEA fixed-k contrasts have no unrestricted MDEA minimum in this comparison.

| Candidate | Default metric | Normalized metric | Interior rank | Active bounds | Feeds with confirmed LL | Retained record |
| --- | --- | --- | --- | --- | --- | --- |
| cross-start-low-cross_start | 541.0792552 | — | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 2 / 2 | [cross-start-low-cross_start-assessment.json.gz](results/C/cross-start-low-cross_start-assessment.json.gz) |
| cross-start-low-incumbent | 541.0792552 | — | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 2 / 2 | [cross-start-low-incumbent-assessment.json.gz](results/C/cross-start-low-incumbent-assessment.json.gz) |
| cross-start-reported-cross_start | 564.4836961 | — | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 / 2 | [cross-start-reported-cross_start-assessment.json.gz](results/C/cross-start-reported-cross_start-assessment.json.gz) |
| cross-start-reported-incumbent | 564.4836961 | — | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 / 2 | [cross-start-reported-incumbent-assessment.json.gz](results/C/cross-start-reported-incumbent-assessment.json.gz) |
| normalized-AMP-0-original | 61.28527532 | 41.88374 | 7 | AMPCOO-segment-diameter, AMP-hydrolysis-enthalpy-increment | 1 / 1 | [normalized-AMP-0-original-assessment.json.gz](results/C/normalized-AMP-0-original-assessment.json.gz) |
| normalized-AMP-0-refit | 61.30184269 | 41.85257562 | 7 | AMPCOO-segment-diameter, AMP-hydrolysis-enthalpy-increment | 1 / 1 | [normalized-AMP-0-refit-assessment.json.gz](results/C/normalized-AMP-0-refit-assessment.json.gz) |
| normalized-AMP-1-original | 62.06511058 | 42.58611284 | 6 | AMPCOO-segment-diameter, AMP-hydrolysis-enthalpy-increment | 0 / 1 | [normalized-AMP-1-original-assessment.json.gz](results/C/normalized-AMP-1-original-assessment.json.gz) |
| normalized-AMP-1-refit | 62.12530075 | 42.49171717 | 5 | AMPH-segment-diameter, AMPCOO-segment-diameter, AMP-hydrolysis-enthalpy-increment | 0 / 1 | [normalized-AMP-1-refit-assessment.json.gz](results/C/normalized-AMP-1-refit-assessment.json.gz) |
| normalized-MDEA-0-limited | 626.6988309 | 6.511952531 | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 / 2 | [normalized-MDEA-0-limited-assessment.json.gz](results/C/normalized-MDEA-0-limited-assessment.json.gz) |
| normalized-MDEA-0-original | 541.0792552 | 9.143252041 | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 2 / 2 | [normalized-MDEA-0-original-assessment.json.gz](results/C/normalized-MDEA-0-original-assessment.json.gz) |
| normalized-MDEA-0-refit | 626.6988265 | 6.511952514 | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 / 2 | [normalized-MDEA-0-refit-assessment.json.gz](results/C/normalized-MDEA-0-refit-assessment.json.gz) |
| normalized-MDEA-1-original | 564.4836961 | 8.526059356 | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 / 2 | [normalized-MDEA-1-original-assessment.json.gz](results/C/normalized-MDEA-1-original-assessment.json.gz) |
| normalized-MDEA-1-refit | 635.8584669 | 6.161340877 | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 / 2 | [normalized-MDEA-1-refit-assessment.json.gz](results/C/normalized-MDEA-1-refit-assessment.json.gz) |

The fixed k=0.765 MDEA fit reduced the normalized objective from 8.52605935588 to 6.16134087651. [normalized-MDEA-1.json.gz](results/C/normalized-MDEA-1.json.gz) · `report`

| MDEA T (K) | System P (Pa) | Q3 search | Confirmed LL | Retained record |
| --- | --- | --- | --- | --- |
| 288.71 | 1121000 | finite search, no resolved descent | no | [normalized-MDEA-1-refit-assessment.json.gz](results/C/normalized-MDEA-1-refit-assessment.json.gz) · `Q3[0]` |
| 373.15 | 203126858.9 | finite search, no resolved descent | no | [normalized-MDEA-1-refit-assessment.json.gz](results/C/normalized-MDEA-1-refit-assessment.json.gz) · `Q3[1]` |

| Stopped run | Starting normalized objective | Last native objective | Last replayed normalized objective | Last optimizer status | Fit-process minutes at stop | Retained record |
| --- | --- | --- | --- | --- | --- | --- |
| MDEA-1 | 8.526059356 | — | — | No endpoint returned | 6.01996 | [normalized-MDEA-1-time-stop.json.gz](results/C/normalized-MDEA-1-time-stop.json.gz) |

| MDEA endpoint | Available rows | Combined AARD (%) | Combined signed bias (%) | Retained record |
| --- | --- | --- | --- | --- |
| high | 121 | 20.0502 | -10.4406 | [partial-pressures.json.gz](results/C/partial-pressures.json.gz) · `endpoints.high` |
| low | 121 | 33.6243 | -33.4175 | [partial-pressures.json.gz](results/C/partial-pressures.json.gz) · `endpoints.low` |
| reported | 121 | 20.0679 | -10.3874 | [partial-pressures.json.gz](results/C/partial-pressures.json.gz) · `endpoints.reported` |

## D. Composition curvature and hot extension

| S14 liquid phase | Minimum generalized eigenvalue | Difference from #433 | Retained record |
| --- | --- | --- | --- |
| parent | -0.0833753045 | 0 | [S14-hessian.json](results/D/S14-hessian.json) · `phases[0]` |
| daughter 1 | 0.215816591 | 0 | [S14-hessian.json](results/D/S14-hessian.json) · `phases[1]` |
| daughter 2 | 0.16136078 | 0 | [S14-hessian.json](results/D/S14-hessian.json) · `phases[2]` |

| Fit | State type | States | Analytic positive | Analytic negative | Analytic undecided | Unavailable | Analytic minimum | Retained record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AMP-expanded-fixed | loaded reactive | 152 | 152 | 0 | 0 | 0 | 0.439247 | [AMP-expanded-fixed.json.gz](results/D/AMP-expanded-fixed.json.gz) · `summary` |
| AMP-expanded-fixed | unloaded or binary | 26 | 26 | 0 | 0 | 0 | 0.659586 | [AMP-expanded-fixed.json.gz](results/D/AMP-expanded-fixed.json.gz) · `summary` |
| AMP-expanded-free | loaded reactive | 152 | 152 | 0 | 0 | 0 | 0.407937 | [AMP-expanded-free.json.gz](results/D/AMP-expanded-free.json.gz) · `summary` |
| AMP-expanded-free | unloaded or binary | 26 | 26 | 0 | 0 | 0 | 0.636736 | [AMP-expanded-free.json.gz](results/D/AMP-expanded-free.json.gz) · `summary` |
| AMP-original-main | loaded reactive | 94 | 94 | 0 | 0 | 0 | 0.121908 | [AMP-original-main.json.gz](results/D/AMP-original-main.json.gz) · `summary` |
| AMP-original-main | unloaded or binary | 26 | 26 | 0 | 0 | 0 | 0.627725 | [AMP-original-main.json.gz](results/D/AMP-original-main.json.gz) · `summary` |
| AMP-original-slope-150 | loaded reactive | 94 | 94 | 0 | 0 | 0 | 0.136713 | [AMP-original-slope-150.json.gz](results/D/AMP-original-slope-150.json.gz) · `summary` |
| AMP-original-slope-150 | unloaded or binary | 26 | 26 | 0 | 0 | 0 | 0.667513 | [AMP-original-slope-150.json.gz](results/D/AMP-original-slope-150.json.gz) · `summary` |
| MDEA-high | loaded reactive | 152 | 152 | 0 | 0 | 0 | 0.384761 | [MDEA-high.json.gz](results/D/MDEA-high.json.gz) · `summary` |
| MDEA-high | unloaded or binary | 98 | 95 | 0 | 0 | 3 | 0.105333 | [MDEA-high.json.gz](results/D/MDEA-high.json.gz) · `summary` |
| MDEA-low | loaded reactive | 152 | 152 | 0 | 0 | 0 | 0.39518 | [MDEA-low.json.gz](results/D/MDEA-low.json.gz) · `summary` |
| MDEA-low | unloaded or binary | 98 | 95 | 0 | 0 | 3 | 0.105593 | [MDEA-low.json.gz](results/D/MDEA-low.json.gz) · `summary` |
| MDEA-reported | loaded reactive | 152 | 152 | 0 | 0 | 0 | 0.384232 | [MDEA-reported.json.gz](results/D/MDEA-reported.json.gz) · `summary` |
| MDEA-reported | unloaded or binary | 98 | 95 | 0 | 0 | 3 | 0.105335 | [MDEA-reported.json.gz](results/D/MDEA-reported.json.gz) · `summary` |
| MDEA-unbounded | loaded reactive | 152 | 152 | 0 | 0 | 0 | 0.309436 | [MDEA-unbounded.json.gz](results/D/MDEA-unbounded.json.gz) · `summary` |
| MDEA-unbounded | unloaded or binary | 98 | 95 | 0 | 0 | 3 | 8.20953e-12 | [MDEA-unbounded.json.gz](results/D/MDEA-unbounded.json.gz) · `summary` |

The independent directional readback for fit:502 at 413.15 K changes sign at the finest steps. With that state undecided, the 98 unbounded MDEA binary states include 94 positive, 1 undecided and 3 unavailable. The analytic minimum remains 8.21e-12. [MDEA-unbounded-near-zero.json](results/D/MDEA-unbounded-near-zero.json) · `extrapolated_projected_mu_curvature`

| Paths retained | States sampled | Liquid descents | Vapor descents | Negative eigenvalues | Lowest eigenvalue | Refusals | Retained record |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 44 / 44 | 616 | 0 | 0 | 0 | 0.0603372 | 0 | [hot-paths.json.gz](results/D/hot-paths.json.gz) · `paths` |

The finite grid supplies a sampled bound through 458 K. [hot-paths.json.gz](results/D/hot-paths.json.gz) · `temperature_grid_K`

The extended declaration replayed 396 original grid paths and temperatures. Pressure and stability differences are retained per state. [overlap.json.gz](results/D/overlap.json.gz) · `rows`

Negative curvature is evidence of local instability of the model liquid. Positive curvature can coexist with a lower tangent at a distant composition. The calculations test properties of the model and supply no observation of physical demixing.

## E. Molecular geometry, pure properties and association

| Source | Predicted / measured | Mean abs. relative error (%) | Signed bias (%) | Retained record |
| --- | --- | --- | --- | --- |
| Alvarez2010 | 7 / 7 | 5.66108 | 5.66108 | [pure-properties.json](results/E/pure-properties.json) · `summary.Alvarez2010` |
| Horstmann2002 | 6 / 6 | 4.85812 | -4.85812 | [pure-properties.json](results/E/pure-properties.json) · `summary.Horstmann2002` |
| Kim2008 | 7 / 7 | 11.289 | -11.289 | [pure-properties.json](results/E/pure-properties.json) · `summary.Kim2008` |
| Klepacova2011 | 5 / 5 | 2.52605 | 0.153052 | [pure-properties.json](results/E/pure-properties.json) · `summary.Klepacova2011` |
| Neumann2022 | 35 / 35 | 1.02271 | 0.893655 | [pure-properties.json](results/E/pure-properties.json) · `summary.Neumann2022` |

The chain has 3.675 segments and a 3.65527 Å segment diameter. The spherical segment diameter is 5.64078 Å at the same $m\sigma^3$. [cation-geometry.json](results/E/cation-geometry.json)

| MDEAH⁺ geometry | Refit | Objective | Interior rank | Active bounds | Q3 confirmed LL | Retained record |
| --- | --- | --- | --- | --- | --- | --- |
| chain | before | 564.4836961 | 5 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 | [cation-chain-before.json.gz](results/E/cation-chain-before.json.gz) |
| chain | after | 564.4836961 | 5 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 0 | [cation-chain-after.json.gz](results/E/cation-chain-after.json.gz) |
| sphere | before | 1472.238929 | 5 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient, ['protonated-methyldiethanolamine', 'bicarbonate-anion'] / k_ij | 1 | [cation-sphere-before.json.gz](results/E/cation-sphere-before.json.gz) |
| sphere | after | 593.482774 | 6 | pair/mdea-water/k_ij/a0 / temperature_law_coefficient | 0 | [cation-sphere-after.json.gz](results/E/cation-sphere-after.json.gz) |

The geometry contrast holds the electrostatic diameters and association topology fixed. The remaining fits compare EOS parameterizations for the declared measurements.

A bounded CPU sample of the spherical fit identifies the native derivative sweeps. [cation-optimizer-sample.json](results/E/cation-optimizer-sample.json)

| Unlike energy multiplier | k at 365.15 K | Slope (K) | Binary objective | Hᴱ at xw=0.6414 (J/mol) | Horstmann pressure AARD (%) | Cai pressure AARD (%) | Reactive objective | Retained records |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| combining rule | -0.0870306 | -32.2542 | 0.12407 | -1475.56 | 9.50484 | 48.5528 | 6.74755 | [DEA-combining-rule.json.gz](results/E/DEA-combining-rule.json.gz) · [DEA-explicit-1-control.json](results/E/DEA-explicit-1-control.json) |
| 1 | -0.0870324 | -32.2583 | 0.124079 | -1475.53 | 9.50553 | 48.5537 | 6.74647 | [DEA-association-1-binary.json.gz](results/E/DEA-association-1-binary.json.gz) · [DEA-association-1-reactive.json.gz](results/E/DEA-association-1-reactive.json.gz) |
| 1.05 | -0.0650956 | -30.1526 | 0.123398 | -1501.39 | 8.3159 | 48.6801 | 7.42467 | [DEA-association-1.05-binary.json.gz](results/E/DEA-association-1.05-binary.json.gz) · [DEA-association-1.05-reactive.json.gz](results/E/DEA-association-1.05-reactive.json.gz) |
| 1.1 | -0.0410041 | -27.4853 | 0.126279 | -1555.53 | 7.94469 | 48.9325 | 8.13217 | [DEA-association-1.1-binary.json.gz](results/E/DEA-association-1.1-binary.json.gz) · [DEA-association-1.1-reactive.json.gz](results/E/DEA-association-1.1-reactive.json.gz) |
| 1.15 | -0.014875 | -24.412 | 0.133897 | -1644.11 | 9.28463 | 49.3872 | 8.99393 | [DEA-association-1.15-binary.json.gz](results/E/DEA-association-1.15-binary.json.gz) · [DEA-association-1.15-reactive.json.gz](results/E/DEA-association-1.15-reactive.json.gz) |

The combining-rule and explicit-edge control have the same association term at the frozen-volume state. The temperature dependence of the combining-rule volume still changes predicted enthalpy. [DEA-explicit-1-control.json](results/E/DEA-explicit-1-control.json)

## Wall time

Measured wall times sum the listed operations, with the continuous timed interval used for Group C. Several operations ran concurrently.

| Group | Projected minutes | Recorded minutes | Operation records |
| --- | --- | --- | --- |
| A | 18–35 | 35.2932 | [calibration.json](results/A/calibration.json) 10.36 min · [phase-timing.json](results/A/phase-timing.json) 5.91 min · [profile-original.json](results/A/profile-original.json) 7.19 min · [profile-expanded.json](results/A/profile-expanded.json) 11.84 min |
| B | 1–4 | 0.553143 | [reactions.json.gz](results/B/reactions.json.gz) 0.30 min · [MDEA-supports.json.gz](results/B/MDEA-supports.json.gz) 0.25 min |
| C | 8–14 | 28 | [reported-objectives.json](results/C/reported-objectives.json) 0.00 min · [partial-pressures.json.gz](results/C/partial-pressures.json.gz) 0.00 min · [cross-start-timing.json](results/C/cross-start-timing.json) 10.75 min · [MEA-k-profile.json.gz](results/C/MEA-k-profile.json.gz) 3.06 min · [group-runtime.json](results/C/group-runtime.json) |
| D | 6–18 | 9.70453 | [fitted-timing.json](results/D/fitted-timing.json) 5.81 min · [hot-paths.json.gz](results/D/hot-paths.json.gz) 2.32 min · [overlap.json.gz](results/D/overlap.json.gz) 1.58 min |
| E | 6–17 | 26.091 | [cation-timing.json](results/E/cation-timing.json) 18.95 min · [pure-properties.json](results/E/pure-properties.json) 0.00 min · [DEA-association-timing.json](results/E/DEA-association-timing.json) 7.14 min |

The isolated four-worker MDEA k=0.765 rerun took 522.6 s including both metric replays and the Q3 checks. The separate diagnostic profile attributed 84% of sampled CPU stacks to automatic differentiation and 33% to saturation-loading searches. The profiled fit took about ten times the wall time of the ordinary MDEA fit. Engine #214 tracks reuse in the saturation-loading search. [normalized-MDEA-1-timing.json](results/C/normalized-MDEA-1-timing.json) · [Engine #214](https://github.com/tannerpolley/epcsaft/issues/214)

## Reconciled records and open items

The Hilliard heat-capacity comparison contains 4 fitted and 47 outside-fit observations. [Hilliard-Cp.json](results/records/Hilliard-Cp.json) · `current_broad_roles`

| Outside-fit band | Rows | AARD (%) | Signed bias (%) | Printed AARD (%) | Retained record |
| --- | --- | --- | --- | --- | --- |
| absorber | 69 | 24.91061381426 | -20.55285172 | 24.91 | [S8-pressure-bands.json](results/records/S8-pressure-bands.json) · `bands.absorber` |
| stripper | 66 | 24.91338368654 | -14.78422263 | 24.91 | [S8-pressure-bands.json](results/records/S8-pressure-bands.json) · `bands.stripper` |

| MDEA state record tier | Stage | Incomplete records | Retained record |
| --- | --- | --- | --- |
| data | supplied incomplete | 146 | [MDEA-coverage.json.gz](results/records/MDEA-coverage.json.gz) · `groups[0]` |
| data | optimized unavailable | 72 | [MDEA-coverage.json.gz](results/records/MDEA-coverage.json.gz) · `groups[1]` |
| data | preparation failed | 7 | [MDEA-coverage.json.gz](results/records/MDEA-coverage.json.gz) · `groups[2]` |
| grid | optimized unavailable | 4 | [MDEA-coverage.json.gz](results/records/MDEA-coverage.json.gz) · `groups[3]` |
| grid | bubble reference | 870 | [MDEA-coverage.json.gz](results/records/MDEA-coverage.json.gz) · `groups[4]` |

Q8 reached distinct phases at 16 of 18 attempted feeds. The confirmed two-liquid count is 0. [MDEA-coverage.json.gz](results/records/MDEA-coverage.json.gz) · `Q8`

| Jakobsen observation | Measured fraction | Calculated fraction | Required pH shift | Electrode pH shift | pH-adjusted fraction | Retained record |
| --- | --- | --- | --- | --- | --- | --- |
| Jakobsen2005_state_017:101325:carbonate-pool-split | 0.5 | 0.0390141 | 1.3915 | 0.785697 | 0.198626 | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[0]` |
| Jakobsen2005_state_018:101325:carbonate-pool-split | 0.574468 | 0.017073 | 1.89055 | 0.748434 | 0.0886925 | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[1]` |
| Jakobsen2005_state_019:101325:carbonate-pool-split | 0.571429 | 0.0114788 | 2.06003 | 0.704451 | 0.0555328 | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[2]` |
| Jakobsen2005_state_020:101325:carbonate-pool-split | 0.5 | 0.0122864 | 1.90521 | 0.738139 | 0.0637288 | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[3]` |
| Jakobsen2005_state_021:101325:carbonate-pool-split | 0.454545 | 0.00438532 | 2.27691 | 0.693627 | 0.0212907 | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[4]` |
| Jakobsen2005_state_022:101325:carbonate-pool-split | 0.05625 | 0.000184519 | 2.50914 | — | — | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[5]` |
| Jakobsen2005_state_023:101325:carbonate-pool-split | 0.0196937 | 1.7466e-05 | 3.06076 | — | — | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[6]` |
| Jakobsen2005_state_024:101325:carbonate-pool-split | 0.0155587 | 5.88605e-06 | 3.42896 | — | — | [pH-carbonate.json](results/records/pH-carbonate.json) · `rows[7]` |

| Original AMP search outcome | States | Retained record |
| --- | --- | --- |
| both | 92 | [AMP-public-trials.json.gz](results/records/AMP-public-trials.json.gz) · `native_supplied_overlap` |
| native_only | 1 | [AMP-public-trials.json.gz](results/records/AMP-public-trials.json.gz) · `native_supplied_overlap` |
| neither | 573 | [AMP-public-trials.json.gz](results/records/AMP-public-trials.json.gz) · `native_supplied_overlap` |
| supplied_only | 0 | [AMP-public-trials.json.gz](results/records/AMP-public-trials.json.gz) · `native_supplied_overlap` |

- Temperature and observation identities for Kuranov rows 72 and 28. [Kuranov-R2.json](results/records/Kuranov-R2.json)

- Hilliard broad and fitted heat capacity identities and their intersection. [Hilliard-Cp.json](results/records/Hilliard-Cp.json)

- Outside-fit absorber and stripper partial-pressure bands. [S8-pressure-bands.json](results/records/S8-pressure-bands.json)

- Stage-keyed MDEA coverage, property pressure deficits and Q8 root classifications. [MDEA-coverage.json.gz](results/records/MDEA-coverage.json.gz)

- Original AMP classification and unavailable pressures. [AMP-native-starts.json.gz](results/records/AMP-native-starts.json.gz)

- AMP replay by publicly returned trial identity. [AMP-public-trials.json.gz](results/records/AMP-public-trials.json.gz)

- Carbonate odds and matched electrode offsets. [pH-carbonate.json](results/records/pH-carbonate.json)

- Reference-state numerical and rounding checks on the isolated public distribution. [public-1.3.2.json](results/records/public-1.3.2.json)

- Corresponding checks on the pinned study wheel. [study-wheel-S13-controls.json](results/records/study-wheel-S13-controls.json)

- Numerical misses, unavailable evidence and remaining checks. [open-items.json](results/records/open-items.json)
