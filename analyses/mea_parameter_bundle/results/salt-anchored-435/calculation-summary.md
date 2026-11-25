
| Quantity | Value | Source |
| --- | --- | --- |
| NaCl osmotic coefficient AARD | 1.5142673% on 10 available rows | [summary.json](results/salt-anchored-435/salt/summary.json) `result.scores.NaCl` |
| NaHCO3 osmotic coefficient AARD | 0.16297888% on 45 available rows | [summary.json](results/salt-anchored-435/salt/summary.json) `result.scores.NaHCO3` |
| Na2CO3 osmotic coefficient AARD | 5.1113299% on 45 available rows | [summary.json](results/salt-anchored-435/salt/summary.json) `result.scores.Na2CO3` |
| mixed osmotic coefficient AARD | 2.5614335% on 39 available rows | [summary.json](results/salt-anchored-435/salt/summary.json) `result.scores.mixed` |
| Water–sodium-cation $k(T)$ | $a_0=-1$ at 298.15 K, $a_1=-0.007981$ K⁻¹ | [summary.json](results/salt-anchored-435/salt/summary.json) `result.laws.sodium-cation` |
| Water–bicarbonate-anion $k(T)$ | $a_0=0.1117253829105505$ at 298.15 K, $a_1=0.003931187632871687$ K⁻¹ | [summary.json](results/salt-anchored-435/salt/summary.json) `result.laws.bicarbonate-anion` |
| Water–carbonate-anion $k(T)$ | $a_0=-1$ at 298.15 K, $a_1=0.001963126045030628$ K⁻¹ | [summary.json](results/salt-anchored-435/salt/summary.json) `result.laws.carbonate-anion` |
| MEA F2-control cost | 150.76290287955263 | [replay.json](results/salt-anchored-435/MEA/F2-control/replay.json) `cost` |
| MEA F2 cost | 152.95825584472823 | [fit-summary.json](results/salt-anchored-435/MEA/F2/fit-summary.json) `cost` |
| MEA F2 grid | 1908/1908 available, 0 descents | [search-summary.json](results/salt-anchored-435/MEA/F2/search-summary.json) `grid` |
| MEA F2 offset | 576/576 available, 0 descents | [search-summary.json](results/salt-anchored-435/MEA/F2/search-summary.json) `offset` |
| MEA F2 census | 162/162 available, 0 descents | [search-summary.json](results/salt-anchored-435/MEA/F2/search-summary.json) `census` |
| MEA F4 cost | 152.9581738516127 | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `cost` |
| MEA F4 grid | 1908/1908 available, 0 descents | [search-summary.json](results/salt-anchored-435/MEA/F4/search-summary.json) `grid` |
| MEA F4 offset | 576/576 available, 0 descents | [search-summary.json](results/salt-anchored-435/MEA/F4/search-summary.json) `offset` |
| MEA F4 census | 162/162 available, 0 descents | [search-summary.json](results/salt-anchored-435/MEA/F4/search-summary.json) `census` |
| MEA selected objective | 152.9581738516127 | [selection.json](results/salt-anchored-435/MEA/selection.json) |
| DEA selected objective | 10.932834014387195 | [selection.json.gz](../dea_transfer/results/salt-anchored-435/campaign/selection.json.gz) |
| MDEA selected objective | 537.6587969229375 | [selection.json.gz](../mdea_mea_workflow/results/salt-anchored-435/campaign/selection.json.gz) |
| AMP free selected objective | 76.31190308633893 | [selection.json.gz](../amp_transfer/results/salt-anchored-435/free/selection.json.gz) |
| AMP fixed selected objective | 77.64284261021933 | [selection.json.gz](../amp_transfer/results/salt-anchored-435/fixed/selection.json.gz) |
| MEA CO2-free density | 0.031172% AARD on 5 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.CO2-free density` |
| MEA Cai MEA-water VLE | 1.48811% AARD on 50 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.Cai MEA-water VLE` |
| MEA Jakobsen ratio | 16.168% AARD on 6 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.Jakobsen ratio` |
| MEA Kiepe pressure | 2.66652% AARD on 39 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.Kiepe pressure` |
| MEA fitted CO2 partial pressure | 11.3465% AARD on 47 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.fitted CO2 partial pressure` |
| MEA fitted heat of absorption | 2.03184% AARD on 8 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.fitted heat of absorption` |
| MEA fitted phase mole fraction | 7.43695% AARD on 94 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.fitted phase mole fraction` |
| MEA heat capacity | 3.02969% AARD on 4 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.heat capacity` |
| MEA loaded density | 0.154022% AARD on 47 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.loaded density` |
| MEA restored species | 9.33355% AARD on 7 fitted rows | [fit-summary.json](results/salt-anchored-435/MEA/F4/fit-summary.json) `metrics.restored species` |
| MEA reference addition heat | -81.795187 kJ/mol CO₂ at 313.15 K and 1.734 MPa | [reference-state.json](results/salt-anchored-435/MEA/F4/reference-state.json) `heat_kJ_mol` |

### Computation time

| Step | Projection (s) | Elapsed (s) | Source |
| --- | --- | --- | --- |
| F2 fit | 67 | 72.18123960800585 | [fit-timing.json](results/salt-anchored-435/MEA/F2/fit-timing.json) |
| F2 search | 629.3120108719438 | 523.5123613220057 | [search-timing.json](results/salt-anchored-435/MEA/F2/search-timing.json) |
| F4 assessment | — | 14.350985616008984 | [assessment-timing.json](results/salt-anchored-435/MEA/F4/assessment-timing.json) |
| F4 curve | 300 | 80.56975176099513 | [curve-timing.json](results/salt-anchored-435/MEA/F4/curve-timing.json) |
| F4 fit | 67 | 49.493589065008564 | [fit-timing.json](results/salt-anchored-435/MEA/F4/fit-timing.json) |
| F4 property-evidence | — | 255.6770728200063 | [property-evidence-timing.json](results/salt-anchored-435/MEA/F4/property-evidence-timing.json) |
| F4 search | 629.3120108719438 | 481.1337389279943 | [search-timing.json](results/salt-anchored-435/MEA/F4/search-timing.json) |
| AMP-resume | 960 | 460.329 (exit 0) | [AMP-resume-runtime.json](results/salt-anchored-435/AMP-resume-runtime.json) |
| AMP | 960 | 252.149 (exit 1) | [AMP-runtime.json](results/salt-anchored-435/AMP-runtime.json) |
| DEA-report | 660 | 49.532 (exit 0) | [DEA-report-runtime.json](results/salt-anchored-435/DEA-report-runtime.json) |
| DEA | 660 | 229.716 (exit 1) | [DEA-runtime.json](results/salt-anchored-435/DEA-runtime.json) |
| MDEA | 2405 | 2175.290 (exit 0) | [MDEA-runtime.json](results/salt-anchored-435/MDEA-runtime.json) |

DEA [deviations.json.gz](../dea_transfer/results/salt-anchored-435/campaign/deviations.json.gz)

DEA [information.json.gz](../dea_transfer/results/salt-anchored-435/campaign/DEA/information.json.gz)

DEA [contributions.csv.gz](../dea_transfer/results/salt-anchored-435/campaign/DEA/contributions.csv.gz)

MDEA [deviations.json.gz](../mdea_mea_workflow/results/salt-anchored-435/campaign/deviations.json.gz)

MDEA [information.json.gz](../mdea_mea_workflow/results/salt-anchored-435/campaign/MDEA/information.json.gz)

MDEA [contributions.csv.gz](../mdea_mea_workflow/results/salt-anchored-435/campaign/MDEA/contributions.csv.gz)

MDEA [search-outcome.json.gz](../mdea_mea_workflow/results/salt-anchored-435/campaign/search-outcome.json.gz)

AMP free [deviations.json.gz](../amp_transfer/results/salt-anchored-435/free/deviations.json.gz)

AMP free [information.json.gz](../amp_transfer/results/salt-anchored-435/free/AMP/information.json.gz)

AMP free [contributions.csv.gz](../amp_transfer/results/salt-anchored-435/free/AMP/contributions.csv.gz)

AMP free [search-outcome.json.gz](../amp_transfer/results/salt-anchored-435/free/native/search-outcome.json.gz)

AMP free [search-outcome.json.gz](../amp_transfer/results/salt-anchored-435/free/supplied/search-outcome.json.gz)

AMP fixed [deviations.json.gz](../amp_transfer/results/salt-anchored-435/fixed/deviations.json.gz)

AMP fixed [information.json.gz](../amp_transfer/results/salt-anchored-435/fixed/AMP/information.json.gz)

AMP fixed [contributions.csv.gz](../amp_transfer/results/salt-anchored-435/fixed/AMP/contributions.csv.gz)

AMP fixed [search-outcome.json.gz](../amp_transfer/results/salt-anchored-435/fixed/native/search-outcome.json.gz)

AMP fixed [search-outcome.json.gz](../amp_transfer/results/salt-anchored-435/fixed/supplied/search-outcome.json.gz)

### Matched observations and worked states

- [receiver-law-verification.json](results/salt-anchored-435/receiver-law-verification.json)
- [hong-matched-pressure.json](results/salt-anchored-435/MEA/hong-matched-pressure.json)
- [baygi-matched-pressure.json](results/salt-anchored-435/MEA/baygi-matched-pressure.json)
- [reference-state.json](results/salt-anchored-435/MEA/F4/reference-state.json)
- [retained-raw-files.json](results/salt-anchored-435/MEA/evidence/F4/retained-raw-files.json)
- [readback.json](results/salt-anchored-435/MEA/controls/readback.json)
- [matched-deviations-campaign.json](../dea_transfer/results/salt-anchored-435/matched-deviations-campaign.json)
- [shift.json](../dea_transfer/results/salt-anchored-435/hydrolysis/shift.json)
- [matched-deviations-campaign.json](../mdea_mea_workflow/results/salt-anchored-435/matched-deviations-campaign.json)
- [kuranov-matched-pressure.json.gz](../mdea_mea_workflow/results/salt-anchored-435/kuranov-matched-pressure.json.gz)
- [fixed-pressure.json.gz](../mdea_mea_workflow/results/salt-anchored-435/campaign/fixed-pressure.json.gz)
- [matched-deviations-fixed.json](../amp_transfer/results/salt-anchored-435/matched-deviations-fixed.json)
- [matched-deviations-free.json](../amp_transfer/results/salt-anchored-435/matched-deviations-free.json)
- [common-pressure.json](../amp_transfer/results/salt-anchored-435/common-pressure.json)
- [shift.json](../amp_transfer/results/salt-anchored-435/hydrolysis/shift.json)
