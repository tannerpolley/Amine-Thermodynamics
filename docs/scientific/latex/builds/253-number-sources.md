# Issue 253 displayed-number sources

All values below are unchanged retained results. A3 is single-sphere; B1 is charged-molecule.

| Displayed value | Retained file and field or reduction |
| --- | --- |
| Ermatchkov 26.21%, 19.15% (checks 26.208406175677485%, 19.1460124028601%) | `analyses/mdea_mea_workflow/results/stage2-capped/{A3,B1}/comparisons.json`: `observed`, `predicted` (Pa), selecting `group == "Ermatchkov"` and `row.mass_fraction <= 0.49`; 100 mean(abs(predicted/observed - 1)). Also `{A3,B1}/assessment.json`, `Ermatchkov88.AARD_percent`. |
| 88 observations, no more than 49 wt% | Same selection: 88 rows per representation; `row.mass_fraction <= 0.49`. This is the selected domain, not a claim that any observation is exactly 49 wt%. |
| Xiao 20.40%, 28.28% (checks 20.397550919041485%, 28.276415410147838%) | `analyses/mdea_mea_workflow/results/context-sources/{A3,B1}-Xiao.json`: all rows, `observed_p_CO2_Pa`, `predicted_p_CO2_Pa`; same AARD formula. Also `context-sources/summary.json`, `{A3,B1}.AARD_percent`. |
| Xiao 20 observations | Length of each retained Xiao row list, also `context-sources/summary.json`, `{A3,B1}.rows`. |
| Nine fitted MDEA parameters | `analyses/mdea_mea_workflow/results/stage2-capped/{A3,B1}/declaration.json`, length of `coordinates` = 9. |
| Four and two active bounds | `analyses/mdea_mea_workflow/results/stage2-capped/selection.json`, length of `A.active_bounds` = 4 and `B.active_bounds` = 2. |
| MEA comparison limit 24.2%, 112 non-fitted pressures | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/canonical-pressure.csv`, rows whose `target` is absent from `fitted-rows.csv` field `id`: n = 112, 100 mean(abs(predicted/observed - 1)) = 24.198632701313954%. MDEA adopted limit also in `analyses/mdea_mea_workflow/results/stage2-capped/reported-statistics.json`, `primary[].criterion_percent`. |
| 293.15–395 K, 50 wt% for other properties | Existing comparison-domain statement retained from supplement S12 and `analyses/mdea_mea_workflow/scripts/summarize_capped.py`, paragraph beginning “Merkley uses”; frozen scope in `inputs/stage2-issue-222.json`, `body` and `comments`. These are intended comparison limits, not new model evaluations. |
| Dielectric assumption above 328.15 K | Same retained domain statement; `data/reference/MDEA/Hsieh2007_stage1.csv`, `temperature_K` maximum = 328.15 K. Supplement S12 gives the same limit. |
| Figure axes and coordinates | Each plotted measured/calculated pair is from the fields above, divided by 1000 from Pa to kPa; equality is a mathematical reference, not a new prediction. Logarithmic tick labels are axis scale values. |

Source citation locators in the new section are unchanged: Vaidya 2007 for carbamate chemistry; Ermatchkov 2006 for pressure observations; Xiao 2018 Table 4 for pressure observations. The Uyan Table 4 citation remains in the introduction. No bibliography refresh or new source adoption occurred.

The figure generator verifies all four AARDs before rendering. Its input hashes and exact reproduced statistics are in `docs/scientific/latex/figures/generated/provenance.json`, `outputs.mdea-pressure`. Original per-row files remain the plotted-value authority.
