# Adopted MEA record at absorber and stripper temperatures, issue #409

This study compares the adopted F2 record (parameter SHA-256 `ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed`, Engine `391dfe5d`, wheel SHA-256 `0962e21d…ab66b`) with data already in the repository, separately for absorber and stripper temperatures. No parameter is fitted. The owner reduced the scope on 2026-11-23: only data already in the repository are used.

**Bands.** Absorber: T ≤ 353.2 K. Stripper: T ≥ 370 K. Rows between 353.2 and 370 K are reported as intermediate in [band-table.csv](band-table.csv). Only heat capacity and density have such rows.

**Roles.** "Fitted" rows are in F2's 307-row objective. "Not fitted" rows are outside that objective. All of them were seen during model development, so they test fixed-parameter prediction, but they do not give independent validation.

## Result

Mean signed relative deviation (MSRD) is 100·mean((calc − obs)/obs). Its sign is the bias sign. AARD is the average absolute relative deviation. Heats are positive heat-release magnitudes, in kJ/mol CO₂. Pressure rows are 30 mass% MEA unless stated.

| Property | Band | Role | n | AARD (%) | RMSE | MSRD (%) | Sources |
|---|---|---|---:|---:|---:|---:|---|
| CO₂ partial pressure | absorber, 313–333 K | fitted | 47 | 11.64 | 7.49 kPa | +1.1 | Hilliard 2008, Jou 1995 |
| CO₂ partial pressure | absorber, 313–353 K | not fitted | 69 | 24.91 | 10.8 kPa | −20.6 | Aronu 2011, Hilliard 2008, Idris 2014, Jou 1995, Wagner 2013 |
| CO₂ partial pressure | absorber, 313–353 K | not fitted, 15/45 mass% | 70 | 45.49 | 1.60 kPa | +9.0 | Aronu 2011 |
| CO₂ partial pressure | stripper | fitted | 0 | – | – | – | none |
| CO₂ partial pressure | stripper, 373–393 K | not fitted | 66 | 24.91 | 109 kPa | −14.8 | Jou 1995, Ma'mun 2005, Wagner 2013, Xu 2011 |
| Heat of absorption | absorber, 313 K | fitted | 8 | 1.97 | 1.98 | −1.0 | Vinjarapu 2024 Table 4 |
| Heat of absorption | absorber, 313–353 K | not fitted | 84 | 7.19 | 7.51 | −4.3 | Arcis 2011 (322.5 K), Kim 2007, Kim 2014 |
| Heat of absorption | stripper | fitted | 0 | – | – | – | none |
| Heat of absorption | stripper, 393 K | not fitted | 28 | 14.07 | 15.35 | −10.0 | Kim 2007 (16), Kim 2014 (7), Vinjarapu 2024 Table 5 (5) |
| Heat of absorption | stripper, 393 K | not fitted, source-flagged | 4 | 210.6 | 59.5 | +159 | Kim 2007 (#245 flags) |
| Heat capacity | absorber, 318–353 K | fitted | 4 | 2.83 | 0.129 kJ/(kg K) | +2.8 | Hilliard 2008 |
| Heat capacity | absorber, 298–353 K | not fitted | 31 | 3.86 | 0.151 kJ/(kg K) | +3.7 | Hilliard 2008, Weiland 1997, Concepción 2023 |
| Heat capacity | stripper | fitted | 0 | – | – | – | none |
| Heat capacity | stripper, 373–393 K | not fitted | 15 | 1.35 | 0.054 kJ/(kg K) | −0.8 | Hilliard 2008 (10 loaded, 5 CO₂-free) |
| Density | absorber, 293–353 K | fitted | 52 | 0.14 | 1.75 kg/m³ | +0.02 | Amundsen 2009, Hartono 2014 |
| Density | absorber, 293–353 K | not fitted | 149 | 0.32 | 5.26 kg/m³ | −0.19 | Amundsen 2009, Han 2012, Hartono 2014, Sobrino 2016 |
| Density | stripper | fitted | 0 | – | – | – | none |
| Density | stripper, 373–393 K | not fitted | 26 | 0.41 | 5.09 kg/m³ | −0.24 | Han 2012 (15 loaded, 3 CO₂-free), Sobrino 2016 (8 CO₂-free) |

The same rows broken down by source and by loaded or CO₂-free state are in [band-table.csv](band-table.csv). Every comparison is in [points.csv](points.csv).

### Stripper results by source

- **Pressure at 373–393 K.** The source sign is not uniform. Jou 1995 is 17.2% AARD at 373 K (MSRD +10.9%) and 16.6% at 393 K (+3.7%). Ma'mun 2005 is 33.5% at 393 K (−33.5%). Wagner 2013 is 28.1% and 19.2% at about 392 K (both negative). Xu 2011 is 30.9% at 373 K (−30.9%) and 21.6% at 393 K (+1.6%). At 393 K the model lies between Jou and Ma'mun, which disagree with each other. The absorber AARD of the not-fitted 30 mass% rows (24.9%) equals the stripper AARD (24.9%), and the absorber bias is more negative.
- **Heat at 393.15 K.** F2 predicts 91.0–91.5 kJ/mol CO₂ for low-loading intervals. The measurements are 99–101 (Kim 2014), 94–98 (Vinjarapu Table 5, u = 3–4 kJ/mol) and 97–119 at loadings up to 0.44 (Kim 2007, unflagged). From 313 to 393 K, the model's low-loading heat rises by about 10.5 kJ/mol (80.8 to 91.3). Over the same range, Kim 2014 rises by 15 kJ/mol (84.0 to 99.1) and Vinjarapu by 16 kJ/mol (fitted 80 to about 96). The in-repository Mathonat 1998 low-loading plateau rises by 21 kJ/mol (81, 90, 102 at 313, 353, 393 K). F2 therefore under-predicts how much the heat of absorption increases with temperature. All five Vinjarapu Table 5 rows fall within twice their stated uncertainty; Vinjarapu Table 5 uses the same pressure, method and declaration as the fitted 313 K rows. Most unflagged Kim 2007 low-loading rows at 393 K lie 5–20 kJ/mol above the other two 393 K sources.
- **Heat capacity.** The stripper rows come only from Hilliard 2008, the same campaign as the four fitted states. The stripper error (1.35%) is smaller than the absorber error (3.86%). The bias changes from positive to slightly negative above about 365 K.
- **Density.** The negative bias for loaded rows grows with temperature: Han 2012 loaded MSRD is −0.02% in the absorber band and −0.55% at 373–393 K (about −5.6 kg/m³). Han 2012 is the only loaded stripper source.

## Checks

- **Regrouping identity.** The table builder regroups the retained F2 rows and reproduces #338's [agreement.csv](../reduced-refit/agreement.csv) AARD for seven whole cohorts to 10⁻⁹ relative ([agreement-check.json](agreement-check.json)): six-source, Wagner, Arcis, Kim 2007, Han, fitted pressure and fitted heat.
- **Replay identity.** Only the Kim 2014 (27 rows) and Vinjarapu 2024 Table 5 (5 rows) heats had no F2 prediction. They were replayed with #338's own Kim finite-addition call (`kim2007_heat_pathways.py`, SHA-256 `557c94…`) from a `git archive` of `f7e09b9ec`, the commit that produced the F2 evidence, on the pinned wheel. Before the new rows are accepted, the replay recomputes the 20 retained F2 Kim 2007 393.15 K intervals and the 8 fitted Vinjarapu 313.15 K heats. The maximum relative difference is **1.66×10⁻¹³**, within #340's 10⁻¹⁰ same-wheel limit ([heat-replay.json](heat-replay.json)).
- **Availability.** 29 of the 32 replayed rows are available. Three Kim 2014 rows at 313 K, with loadings 0.61–0.69, exceed the producer's 0.6 loading ceiling. Every stripper-band row is available.

## Basis and limits

- The Kim and Vinjarapu heats use the F2 Kim producer's 1.734 MPa system pressure. This pressure is Vinjarapu's reported value. Kim 2014 reports no pressure. For each run, the first Kim 2014 interval starts at zero loading, as in the retained Kim 2007 F2 call. The partition file instead assumes 0.003.
- The four source-flagged Kim 2007 rows are the 393.15 K run-2 rows at loadings 0.078 and 0.445, which are inconsistent with their integrals, and the two first 120 °C additions from zero loading. They are reported separately and not pooled.
- Fitted high-temperature data exist only for binary subsystems: Kiepe CO₂–water pressures (18 rows at 373 and 393 K) and Cai MEA–water bubble temperatures and vapor compositions (22 states at 374–432 K). No loaded-MEA row at 370 K or above is in F2's objective.
- Each pressure RMSE in pascals is dominated by its highest-pressure rows. Use AARD and MSRD to compare bands.
- None of these comparisons is independent physical validation. The study does not qualify the model for any absorber or stripper process use.

## Stripper-range gaps in the repository

| Property | What the repository lacks | Sources that could fill it (not acquired) |
|---|---|---|
| CO₂ partial pressure | Fitted stripper rows. Accepted rows above 393 K. | Xu and Rochelle 2011 rows at 383–443 K are already in `Canonical_VLE_Observations.csv` with status `qa_pending_domain_review`. Aronu et al. 2011 (Chem. Eng. Sci., 15/30/45/60 mass%, 40–120 °C): the repository keeps only its rows at 353 K or below. |
| Heat of absorption | Data at about 373 K. Any source above 393 K. | Arcis et al. 2011, J. Chem. Eng. Data, doi 10.1021/je2002946: 372.9 K table, listed in `source_status_manifest.csv` as `inventory_only_no_extraction`. Mathonat et al. 1998, 393 K: in the repository, but its pooled 2–10 MPa low-loading plateau is not the interval-heat declaration used here. |
| Loaded heat capacity | A second source at 353 K or above. | No second source found. A short search found only Weiland/Dingman 1997, whose temperature range is unconfirmed (the repository holds its 298 K rows), and reviews limiting MEA heat-capacity data to 353 K or below. |
| Loaded density | A second loaded source at 353 K or above, and data above 393 K. | None identified in the local shelf or the short search. |

`literature/README.md` lists no stripper-specific study. The sources above come from the repository's source manifest and a short web search. Their tables were not read for this study.

## Reproduction

From a `git archive f7e09b9ec` export, with a Python 3.13 environment holding the pinned wheel, run:

`AGENT_HEAVY_CORES=4 agent-heavy python analyses/mea_parameter_bundle/scripts/stripper_temperature_409.py replay <export>`

This writes `heat-replay.json` and takes about one minute on 4 cores. The `table` mode uses retained files only. The export needs these paths from `f7e09b9ec`: `analyses/mea_parameter_bundle/{scripts,calibration-misfit,data}`, `src`, `data`, and these results folders: `temperature-reanchor-140`, `final-rerun`, `density-cp-160`, `source-corrections-152`, `density-current-record-123`, `selected-current-best-parameters.json`, `joint-recalibration-170/amendment-{6,7}`, `engine-3e83e19c-refit-chain/restricted-2/attempt-3/spec.json`, `reduced-refit/F2/parameters.json`, `reduced-refit/evidence/F2`.
