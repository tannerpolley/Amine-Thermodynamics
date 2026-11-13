# Part II Kamps comparison: delivery evidence

## Outputs

- `docs/scientific/latex/builds/part2.pdf`: 17 pages; SHA-256 `bed84e720052a6d76f2afe59a99e812b545bcb2daf2fc8ed789dd22ce711b1e0`.
- `docs/scientific/latex/builds/part2_supplement.pdf`: 19 pages; SHA-256 `2d9e0f509cf57d35b49e7b131c0906919db8417a8cc0172b124a221223e739ae`.

## Changed or added manuscript sentences (old → new)

Each source line contains one manuscript sentence. `Absent` denotes an added sentence.

### `docs/scientific/latex/part2.tex`

**Old:** At least four false liquid splits remain for PZ; a separate fit with Part I's stability penalty still has at least three, two of which the routine phase search missed.

**New:** At least forty false liquid splits are detected for PZ across calibration and comparison states; a separate fit with Part I's stability penalty still has at least three, two of which the routine phase search missed.

### `docs/scientific/latex/sections/part2/conclusions.tex`

**Old:** Absent.

**New:** The comparison-only Kamps PZ total pressures give 42.5\,\% AARD and $-40.3$\,\% bias, including substantial underprediction inside both PZ law ranges.

**Old:** At least four false liquid splits remain for the reported PZ fit; a separate penalty fit and direct split evaluations demonstrate that the finite phase search can miss instability.

**New:** At least forty false liquid splits are detected for the reported PZ fit, including thirty-six high-loading Kamps states; compression to 1.5 times bubble pressure preserves all four Hilliard splits, and direct evaluations demonstrate that the routine search misses two of them.

### `docs/scientific/latex/sections/part2/discussion.tex`

**Old:** Absent.

**New:** The Kamps comparison extends the detected PZ false splits to at least forty states and shows underprediction inside both PZ law ranges.

At the thirty-six Kamps split states, doubly protonated PZ accounts for 2--29\,\% of total PZ in the calculated parent liquid, whereas the source's model describes it as present ``only in very small amounts'' at 353 K and about 4 mol/kg \cite[p.~2666]{kampsSolubilityCO2H2O+piperazine2003a}.

This is a model-speciation observation, not a measured fraction.

Candidate causes, without ranking, are physical \COtwo solubility at MPa pressure, PZH$^+$--bicarbonate and zwitterion interactions, second protonation through its law and tied PZH$_2^{2+}$ parameters, and the shared MEA \COtwo--water description.

This comparison cannot separate them.

**Old:** Tests near the PZ false splits (about 5 mol/kg, loading 0.77--0.83), for the water--DEA mixing enthalpy and above reaction-law measurement ranges reveal the limitations reported here; conditions beyond the measured and searched states were not tested.

**New:** Tests at the PZ false splits (Hilliard loading 0.77--0.83 and Kamps loading 0.96--1.64), for the water--DEA mixing enthalpy and above reaction-law measurement ranges reveal the limitations reported here; conditions beyond the measured and searched states were not tested.

### `docs/scientific/latex/sections/part2/results.tex`

**Old:** Absent.

**New:** The comparison-only total pressures of P\'erez-Salado Kamps et al. \cite[Table~3, p.~2666]{kampsSolubilityCO2H2O+piperazine2003a} were scored once on the frozen twelve-coordinate PZ fit and never fitted or used to select it.

The ninety-four rows give 42.5\,\% AARD and $-40.3$\,\% bias.

Loaded rows below 0.2 MPa give 20.4\,\% AARD and $-6.0$\,\% bias; the loaded 374--395 K rows at or above 0.2 MPa give 37.1\,\% and $-35.2$\,\%, and the remaining loaded 313--354 K rows give 53.0\,\% and $-53.0$\,\%.

The 313.75 K block, inside both the 283.15--333.15 K carbamate and 293.14--353.42 K protonation measurements, still has $-32.1$\,\% bias, so leaving those ranges is not the only cause.

Only that block lies inside both PZ laws; the 395.0 K rows also exceed the shared R2 interval (Supplementary Table~\ref{supp-tab:p2-kamps-blocks}).

The source gives pressure bounds of $\pm4$ or $\pm10$ kPa, without assigning the transducer to each row, and uncertainty up to 10\,\% below 0.1 MPa \cite[pp.~2664, 2667]{kampsSolubilityCO2H2O+piperazine2003a}.

All eighty-two loaded rows at or above 0.2 MPa lie outside both pressure bounds.

The $\pm0.7$\,\% solvent-mass bound moves calculated pressure by up to $-10.8$\,\% / $+11.7$\,\%; the median ratio of sensitivity to misfit is 0.07 and the maximum is 0.88.

Near 1 mol/mol at low pressure this sensitivity can be comparable to the misfit, but for thirty rows above 1.2 mol/mol and at or above 0.2 MPa it is at most 3.2\,\% against misfits of at least 34.9\,\%.

These are input sensitivities, not propagated total uncertainties; the individual charged \COtwo masses needed to propagate their uncertainty were not reported.

**Old:** Small property residuals do not exclude false liquid phases: the reported PZ fit has at least four, and a separate fit with the Part I stability penalty still has at least three, two of which the routine search missed.

**New:** Small property residuals do not exclude false liquid phases: the reported PZ fit has at least forty across calibration and comparison states, and a separate fit with the Part I stability penalty still has at least three, two of which the routine search missed.

**Old:** At least four false liquid splits remain for the reported PZ fit at Hilliard rows 55, 56, 61 and 62, near 4.96--5.02 mol PZ/kg water, loading 0.77--0.83 and 313 or 333 K.

**New:** Four false liquid splits are detected for the reported PZ fit at Hilliard rows 55, 56, 61 and 62, near 4.96--5.02 mol PZ/kg water, loading 0.77--0.83 and 313 or 333 K.

**Old:** Absent.

**New:** Thirty-six additional false liquid splits occur at Kamps states, at 313--354 K and loading 0.96--1.64 mol \COtwo/mol PZ, with tangent-plane distances from $-0.026$ to $-0.554\,RT$.

The second liquids are rich in bicarbonate and doubly protonated PZ.

Pressures at these states belong to a single liquid that is not the stable state of this model; the split count is a lower bound.

At 1.5 times bubble pressure all four Hilliard splits persist, although the routine search misses two; all 121 NMR states pass the finite search at $T+0.5$ K, with rich states moved above bubble pressure as specified in the supplement.

### `docs/scientific/latex/sections/part2/supplement.tex`

**Old:** Absent.

**New:** Kamps total pressures are comparison-only, scored once after the twelve-coordinate fit was frozen.

The temperatures use the correction in Ermatchkov et al., Table~6, p.~1794 \cite{ermatchkovSolubilityCarbonDioxide2006a}; the precipitation row at 313.75 K, 1.995 mol PZ/kg water, loading 1.69 and 4.446 MPa is excluded.

The block comparison labels both PZ measurement intervals and the shared R2 computational interval; all 395.0 K rows exceed the latter.

The two unloaded rows are included in the block and overall scores but separated from the loaded pressure groups.

**Old:** Absent.

**New:** At Kamps bubble states the search detects thirty-six dense-liquid splits, finds no additional phase at fifty-six states, and leaves two unloaded states undecided; no gas or ambiguous split is found.

The no-split count is an upper bound and the detected-split count a lower bound.

At 1.5 times bubble pressure the routine search finds splits at Hilliard rows 55 and 62 but misses rows 56 and 61.

Direct tangent-plane distances at the known split compositions are $-0.0957$, $-0.1107$, $-0.0024$ and $-0.0306\,RT$ at rows 55, 56, 61 and 62, respectively.

All 121 NMR states pass at $T+0.5$ K and 0.1 MPa, except that three rich states are evaluated at 1.05 times bubble pressure where it exceeds 0.1 MPa.

These checks do not establish a continuous stable region.

## Every changed or added table number

Table entries below are generated from retained values. The prose numbers and conditions, including sensitivity and phase depths, are mapped in `tables/part2/number-sources.md`, section “Kamps comparison and design checks”.

| Display | Source file | Field | Retained value |
|---|---|---|---|
| `94` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "overall", "n"]` | `94` |
| `42.5` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "overall", "AARD_percent"]` | `42.519153259282284` |
| `-40.3` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "overall", "bias_percent"]` | `-40.25953615127497` |
| `10` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "below 0.2 MPa", "n"]` | `10` |
| `20.4` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "below 0.2 MPa", "AARD_percent"]` | `20.377095127625704` |
| `-6.0` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "below 0.2 MPa", "bias_percent"]` | `-5.953970402573185` |
| `35` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "374-395 K", "n"]` | `35` |
| `37.1` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "374-395 K", "AARD_percent"]` | `37.088270880706546` |
| `-35.2` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "374-395 K", "bias_percent"]` | `-35.20366359315821` |
| `47` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "313-354 K, 0.2 MPa and above", "n"]` | `47` |
| `53.0` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "313-354 K, 0.2 MPa and above", "AARD_percent"]` | `53.04075518860933` |
| `-53.0` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "313-354 K, 0.2 MPa and above", "bias_percent"]` | `-53.04075518860933` |
| `2` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "unloaded", "n"]` | `2` |
| `1.0` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "unloaded", "AARD_percent"]` | `1.012240203454945` |
| `0.1` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_group", "unloaded", "bias_percent"]` | `0.09351271553001417` |
| `313.75` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 1, T_K` | `313.75` |
| `1.995` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 1, mPZ` | `1.995` |
| `7` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "313.75 K, 1.995 mol/kg", "n"]` | `7` |
| `32.1` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "313.75 K, 1.995 mol/kg", "AARD_percent"]` | `32.13158379174722` |
| `-32.1` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "313.75 K, 1.995 mol/kg", "bias_percent"]` | `-32.13158379174722` |
| `334.05` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 9, T_K` | `334.05` |
| `1.995` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 9, mPZ` | `1.995` |
| `8` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 1.995 mol/kg", "n"]` | `8` |
| `35.6` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 1.995 mol/kg", "AARD_percent"]` | `35.62376564801891` |
| `-35.6` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 1.995 mol/kg", "bias_percent"]` | `-35.62376564801891` |
| `334.05` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 17, T_K` | `334.05` |
| `2.035` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 17, mPZ` | `2.035` |
| `6` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 2.035 mol/kg", "n"]` | `6` |
| `48.2` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 2.035 mol/kg", "AARD_percent"]` | `48.18074532748328` |
| `-48.2` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 2.035 mol/kg", "bias_percent"]` | `-48.18074532748328` |
| `354.35` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 23, T_K` | `354.35` |
| `1.995` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 23, mPZ` | `1.995` |
| `13` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "354.35 K, 1.995 mol/kg", "n"]` | `13` |
| `33.4` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "354.35 K, 1.995 mol/kg", "AARD_percent"]` | `33.40054125976586` |
| `-33.4` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "354.35 K, 1.995 mol/kg", "bias_percent"]` | `-33.40054125976586` |
| `374.65` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 36, T_K` | `374.65` |
| `2.035` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 36, mPZ` | `2.035` |
| `10` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "374.65 K, 2.035 mol/kg", "n"]` | `10` |
| `29.4` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "374.65 K, 2.035 mol/kg", "AARD_percent"]` | `29.375169693122142` |
| `-29.4` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "374.65 K, 2.035 mol/kg", "bias_percent"]` | `-29.375169693122142` |
| `395.0` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 46, T_K` | `395.0` |
| `2.035` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 46, mPZ` | `2.035` |
| `10` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "395.0 K, 2.035 mol/kg", "n"]` | `10` |
| `23.7` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "395.0 K, 2.035 mol/kg", "AARD_percent"]` | `23.6626589841045` |
| `-22.8` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "395.0 K, 2.035 mol/kg", "bias_percent"]` | `-22.814510130248884` |
| `334.05` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 56, T_K` | `334.05` |
| `3.964` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 56, mPZ` | `3.964` |
| `13` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 3.964 mol/kg", "n"]` | `13` |
| `76.3` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 3.964 mol/kg", "AARD_percent"]` | `76.29203317740902` |
| `-67.6` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "334.05 K, 3.964 mol/kg", "bias_percent"]` | `-67.59097705164862` |
| `354.35` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 69, T_K` | `354.35` |
| `3.964` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 69, mPZ` | `3.964` |
| `8` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "354.35 K, 3.964 mol/kg", "n"]` | `8` |
| `56.5` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "354.35 K, 3.964 mol/kg", "AARD_percent"]` | `56.544544407168075` |
| `-56.5` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "354.35 K, 3.964 mol/kg", "bias_percent"]` | `-56.544544407168075` |
| `374.7` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 77, T_K` | `374.7` |
| `3.95` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 77, mPZ` | `3.95` |
| `10` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "374.7 K, 3.95 mol/kg", "n"]` | `10` |
| `49.8` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "374.7 K, 3.95 mol/kg", "AARD_percent"]` | `49.76519629271111` |
| `-46.7` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "374.7 K, 3.95 mol/kg", "bias_percent"]` | `-46.653444531147116` |
| `395.0` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 87, T_K` | `395.0` |
| `3.95` | `analyses/pz_transfer/results/kamps2003-A12.csv` | `row 87, mPZ` | `3.95` |
| `9` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "395.0 K, 3.95 mol/kg", "n"]` | `9` |
| `32.4` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "395.0 K, 3.95 mol/kg", "AARD_percent"]` | `32.37940556013977` |
| `-25.7` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "by_block", "395.0 K, 3.95 mol/kg", "bias_percent"]` | `-25.74704196418357` |
| `56` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "census", "no_extra_phase"]` | `56` |
| `2` | `analyses/pz_transfer/results/kamps2003-A12.json` | `["summary", "census", "undecided"]` | `2` |
| `36` | `analyses/pz_transfer/results/kamps2003-A12.json` | `len(summary.census.dense_split)` | `36` |
| `0` | `analyses/pz_transfer/results/kamps2003-A12.json` | `len(summary.census.gas_split)` | `0` |
| `0` | `analyses/pz_transfer/results/kamps2003-A12.json` | `len(summary.census.ambiguous)` | `0` |

## Every added prose number and source


All following paths are under `analyses/pz_transfer/`. New table cells are individually indexed in `displayed-values.csv`.

| Value or claim | Source file and field |
|---|---|
| 94; 42.5%; −40.3% | `results/kamps2003-A12.json :: summary.overall.{n,AARD_percent,bias_percent}` |
| 10 / 20.4 / −6.0; 35 / 37.1 / −35.2; 47 / 53.0 / −53.0; 2 / 1.0 / +0.1 | `results/kamps2003-A12.json :: summary.by_group.*.{n,AARD_percent,bias_percent}` |
| Every block temperature, molality, row count, AARD and bias | `results/kamps2003-A12.json :: summary.by_block; results/kamps2003-A12.csv :: T_K,mPZ,carbamate_law,protonation_law,shared_R2_law` |
| 283.15–333.15 K; 293.14–353.42 K; 293.15–393.15 K; 395.0 K | `notebook.qmd :: Kamps 2003 / Law ranges; CSV law labels` |
| 313.75 K; −32.1% | `results/kamps2003-A12.json :: summary.by_temperature.313.75.bias_percent` |
| ±4, ±10 kPa; 10% below 0.1 MPa; ±0.7% | `notebook.qmd :: Kamps 2003 / Uncertainty (pp.2664,2667); results/kamps2003-A12.csv :: within_4kPa_bound,within_10kPa_bound,solvent_mass_*` |
| 82 outside both bounds; 30 above 1.2 mol/mol and ≥0.2 MPa | `results/kamps2003-A12.csv :: observed_MPa,alpha_per_PZ,within_4kPa_bound,within_10kPa_bound; notebook.qmd :: What the errors show` |
| −10.8/+11.7%; median 0.07; maximum 0.88; ≤3.2% versus ≥34.9% | `notebook.qmd :: Input sensitivity; results/kamps2003-A12.csv :: solvent_mass_plus_0p7pct_relative_change,solvent_mass_minus_0p7pct_relative_change,relative_error` |
| 36; 56; 2; 0 gas; 0 ambiguous | `results/kamps2003-A12.json :: summary.census.{dense_split,no_extra_phase,undecided,gas_split,ambiguous} (list lengths for splits)` |
| At least 40 = 4 Hilliard + 36 Kamps (distinct states) | `results/reactive-A12-record.json :: census; results/kamps2003-A12.json :: summary.census.dense_split` |
| 313–354 K; 0.96–1.64 mol/mol; −0.026 to −0.554 RT; bicarbonate-rich split liquid | `notebook.qmd :: Phase census at the scored states; results/kamps2003-A12.csv :: T_K,alpha_per_PZ,dense; results/kamps2003-A12.json :: states[].trials[].quantities.tpd_over_rt and composition` |
| 2–29% parent-liquid doubly protonated fraction; 353 K / about 4 mol/kg source comparison | `results/kamps2003-A12.csv :: PZH2_share_of_PZ where dense=True (2.1–28.8%); notebook.qmd :: What the errors show; Kamps p.2666` |
| 1.5 times bubble; 4 persistent splits; rows 55,56,61,62; 2 missed; −0.0957,−0.1107,−0.0024,−0.0306 RT | `results/check-states-A12-direct.json :: [].{row,check_search_passed,direct_tpd_at_1p5_bubble}` |
| 121 NMR; T+0.5 K; 0.1 MPa; 3 moved; 1.05 times bubble | `results/check-states-A12.json :: summary.NMR liquids at T + 0.5 K, 0.1 MPa (1.05 x bubble where that exceeds 0.1 MPa); notebook.qmd :: Design check states` |
| Excluded 313.75 K / 1.995 mol/kg / 1.69 mol/mol / 4.446 MPa | `notebook.qmd :: Excluded row; inputs/kamps2003-table3.csv :: precipitation row` |
| Table 3 p.2666; correction Table 6 p.1794 | `notebook.qmd :: Source; inputs/kamps2003-provenance.json` |

| Added paragraph | Digits and conditions | Source |
|---|---|---|
| `p2-discussion-kamps` | 2, -29, 353, 4, 2, 2 | Kamps and check-state fields above |
| `p2-results-kamps-01` | 42.5, -40.3, 0.2, 20.4, -6.0, 374, -395, 0.2, 37.1, -35.2, 313, -354, 53.0, -53.0, 313.75, 283.15, -333.15, 293.14, -353.42, -32.1, 395.0, 2 | Kamps and check-state fields above |
| `p2-results-kamps-02` | 4, 10, 10, 0.1, 0.2, 0.7, -10.8, +11.7, 0.07, 0.88, 1, 1.2, 0.2, 3.2, 34.9 | Kamps and check-state fields above |
| `p2-results-phase-kamps` | 313, -354, 0.96, -1.64, -0.026, -0.554, 1.5, 121, +0.5 | Kamps and check-state fields above |
| `p2-s-kamps` | 6, 1794, 313.75, 1.995, 1.69, 4.446, 2, 395.0, 2, 2 | Kamps and check-state fields above |
| `p2-s-phases-kamps` | 1.5, 55, 62, 56, 61, -0.0957, -0.1107, -0.0024, -0.0306, 55, 56, 61, 62, 121, +0.5, 0.1, 1.05, 0.1, 2 | Kamps and check-state fields above |

## Limits

No new model calculations, parameter selection or science review. Split counts are lower bounds. Kamps split-state pressures are for a non-stable single liquid. Candidate causes remain unranked. No figure panel was needed.

## Changed or added table captions

### `kamps-blocks.tex`

**Old:** Absent.

**New:** Kamps total-pressure blocks at corrected temperatures. Law labels: carbamate measurements 283.15--333.15 K; protonation measurements 293.14--353.42 K; shared R2 interval 293.15--393.15 K. Unloaded rows are included. Labels describe temperature ranges, not phase stability.

### `kamps-census.tex`

**Old:** Absent.

**New:** Kamps phase census at 94 scored bubble states. Split counts are lower bounds; states without a detected split do not prove stability.

### `kamps-groups.tex`

**Old:** Absent.

**New:** Kamps total-pressure groups. Loaded high-temperature groups exclude unloaded rows and pressures below 0.2 MPa. Overall: 94 rows, 42.5\,\% AARD, $-40.3$\,\% bias.

### `unfitted.tex`

**Old:** Unfitted pressure errors by source and temperature. MDEA sets were previously accessed; AMP Kundu and PZ Ermatchkov were scored before final parameter selection, and DEA was first scored on a numerically tied fit. All are partial pressures except AMP Tong.

**New:** Unfitted pressure errors by source and temperature. MDEA sets were previously accessed; AMP Kundu and PZ Ermatchkov were scored before final parameter selection, and DEA was first scored on a numerically tied fit. Kamps was scored once after the PZ fit was frozen. All are partial pressures except AMP Tong and PZ Kamps.
