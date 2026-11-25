# Writer handoff for the #435 display changes

Paths and line numbers below are relative to `docs/scientific/latex/` at the pre-rewrite branch tip. Grouped rows cover repeated occurrences of the same result. Entry names refer to the [#435 manuscript handoff](../../../../analyses/mea_parameter_bundle/results/salt-anchored-435/manuscript-handoff.md). The [#429 number ledger](429-story-pass-number-sources.md) locates the previous records. For historical studies, keep the original numbers and qualify the declaration as the previous shared set.

`dea_displays.py --check` is **expected-to-fail-until-rewrite**. The byte comparisons for its generated tables, figures and source manifest pass. Its final exact-string assertion reports 56 missing strings: 23 in transfer results, 17 in the supplement, 5 in MEA results, 4 in the conclusion, 2 each in methods, theory and introduction, and 1 in the abstract. The 35 ledger rows group repeated occurrences and include unchecked numbers and historic attributions. The Introduction's “less than 3%” claim covers four caloric/density groups, including the 3.03% heat-capacity AARD in the adopted fit.

## Main text and submission

| Location | Previous wording or value | Replacement or disposition | #435 handoff entry or retained locator |
|---|---|---|---|
| `main.tex:94`, `sections/introduction.tex:41`, `sections/conclusion.tex:4`, `submission/chemrxiv.md:13`, `submission/cover_letter.md:9`, `submission/highlights.txt:1–2` | 10.3 / 10.5%, 47 pressures, 73 splits above 353 K, none for the fixed slope | Expanded free slope 10.92% on 105 loaded total pressures versus 10.66% for the previous-set expanded free fit. Both have zero descents and zero confirmed splits in 666 native and 666 supplied searches each. The salt-anchored −150 K sensitivity gives 11.10%; keep it in the supplement. The 73 splits belong to the original 47-pressure comparison. | AMP expanded free/−150 K sensitivity objectives, deviations and native/supplied coverage. Generated expanded-fit table in `tables/supplement-amp-ranges.tex`. |
| `main.tex:95`, `sections/conclusion.tex:9`, `submission/chemrxiv.md:13`, `submission/cover_letter.md:10`, `submission/highlights.txt:4` | 20.1→11.2% fitted MDEA total pressure, 20.1→33.6% outside-fit partial pressure, two splits | Previous-to-adopted fitted total pressure 20.09→10.12% (66), outside-fit total pressure 38.75→30.39% (54), outside-fit CO₂ partial pressure 20.07→37.71% (121). One adopted grid split in the finite search. The two splits are historical #417 results. | MDEA deviations by source; MDEA full search; MDEA confirmed grid split. |
| `main.tex:96`, `sections/introduction.tex:43`, `sections/conclusion.tex:13–16`, `submission/cover_letter.md:11` | MEA 11.6%; DEA 28.5%; MDEA 20.1%; fitted heats, heat capacities and densities all below 3%; no detected instability stated without search coverage | MEA 11.35% (47 partial), DEA 36.63% (30 partial), MDEA 10.12% (66 total). MEA heat 2.03%, Cp 3.03%, loaded density 0.15%, CO₂-free density 0.03%. MEA completed 2,646; DEA completed 1,269/1,271; zero descents in completed searches. MDEA has one grid split. | MEA fitted deviations, DEA Lawson, MDEA Kuranov and all three phase-search coverage entries. |
| `sections/epc_saft_equation_of_state.tex:35–41`, `sections/transfer_results.tex:87`, `supplement.tex:153–154,192` | MDEA–water is the only linear-in-temperature law; water–bicarbonate from MEA fit; water–carbonate from Held | Water–bicarbonate and water–carbonate are linear in T about 313.15 K. (k_0,a_1) respectively (0.1706931974, 0.00393118763 K⁻¹) and (−0.9705531093, 0.00196312605 K⁻¹). The MDEA–water law retains its 423 K reference. | Salt calibration, water–bicarbonate and water–carbonate law and 313.15 K entries. |
| `sections/epc_saft_equation_of_state.tex:96` | 2.948/3.655 Å segment; 5.108/5.641 Å volume equivalent | 2.948/3.647 Å; 5.108/5.628 Å. | DEA fixed cation and MDEA cation segment diameter. |
| `sections/data_methods.tex:9,18`, `supplement.tex:375` | 156 AMP observations, 47 loaded pressures, normalize over 47, 373/393 K Hartono and Tong excluded | 214 observations; loaded group 105 = 47 original Hartono + 18 Hartono + 40 Tong; normalize over 105. Five zero-loading Tong and 51 Kundu partial pressures remain comparisons. | AMP expanded free objective, contributions and deviations by group. |
| `sections/data_methods.tex:61`, `supplement.tex:289–290` | Cai 60.8% of 150.76; contributions 39.824 and 51.807, residual variance factor 1.169 | 39.750 and 51.795, 59.85% of 152.958, stage residual variance 1.18113896. | MEA objective, Cai contributions and MEA RSS/variance. |
| `sections/data_methods.tex:62`, `supplement.tex:291–293` | 62.797 / 62.656, 11.64→11.61%, 24.89→24.98%, 25.03→25.50% used as a sensitivity of the reported MEA model | Historical previous-set alternative-weight refit. Its 150.763 is the old standard-weight objective. Adopted standard-weight objective 152.958. | MEA objective; prior #420 alternative weights retained. |
| `sections/data_methods.tex:66`, `supplement.tex:547–548` | DEA objectives 8.082968228315, 8.082968228355, old fitted coordinates and deviations; 1,270 complete | Start-0 10.932834014425, start-1 10.932834014387 (selected), same 1e−10 tie rule. Adopted Lawson 36.63%, Carson 1.04%, 1,269 complete. Exact adopted coordinates in the paired parameter entries. | DEA objective tie tolerance, DEA candidates, DEA data and grid states, DEA fitted parameters. |
| `sections/data_methods.tex:67–73`, `sections/mea_system_modeling_results.tex:5–7,16,18,20,106–110`, `sections/conclusion.tex:13`, `supplement.tex:457–459` | 150.763 / 150.767 for two related starts; third restriction-row model; one bound; fitted water–bicarbonate; 16-to-11 restrictions alone define the reported model | Salt-anchored F4 cost 152.958 versus previous F2 150.763 (same 307 observations). Both salt laws held. Replace the old fitted coordinate with MEAH⁺–HCO₃⁻; it reaches +1, while MEAH⁺–carbamate remains at −1. The historical restrictions table keeps its old rows. The salt refit compares mapped F2 and salt-F4 starts under its own declaration. | MEA objective, fitted parameters, `MEA/selection.json` and `MEA/F4/uncertainty/profiles.json`. |
| `sections/data_methods.tex:91–92`, `supplement.tex:423–427,435,444–445` | MEA rank 10, 258 df, stage/all variance 1.16869941 / 1.01523840, multiplier 1.0729; MDEA 4.15061398 / 4.10533597 and maximum correlation 0.925 | MEA rank 9, 259 df, 1.18113896 / 1.02656493, multiplier 1.07265 with 268 responsive rows. MDEA rank 6, 272 df, 3.95337207 / 3.91024580, correlation 0.953 for k(MDEAH⁺–water) and cation energy. MEA profiles cover both active interactions. | MEA / MDEA RSS/variance; conditional covariance; MEA inward profiles. |
| `sections/mea_system_modeling_results.tex:17,19`, `supplement.tex:427` | Cai temperature RMSE 1.785 K; relative SE 6.0–16.9% (5.98–16.9% in supplement) | 1.783 K; 5.9–17.0% for the 47 fitted partial pressures. | MEA Cai temperature fitted rows and MEA pressure uncertainty. |
| `sections/mea_system_modeling_results.tex:44`, `supplement.tex:263` | AARD 95.0%, geometric mean 0.032 (0.0317), ratio range 0.004–0.182 | 89.90%, 0.06974, range 0.00951–0.33129. | MEA carbonate-pool predicted/observed geometric mean / min / max / AARD / bias. |
| `sections/mea_system_modeling_results.tex:46–47`, `sections/transfer_results.tex:218–220`, `supplement.tex:158,264–267,272` | Electrostatic arms 0.016–0.040, 0.0402, 0.0197, solvation changes +0.569/+15.037/−1.096, second pair +0.110/+0.108; volume-equivalent DEA 28.5→28.1% and MDEA 20.1→17.7% | Historical previous-set sensitivity; keep those denominators. The adopted baseline share ratio is 0.06974. | MEA carbonate-pool ratio; #423 arm replays and #405 diameter sensitivities retained in their original records. |
| `sections/mea_system_modeling_results.tex:77,94` | Kim 393.15 K RMSE 31.77 kJ/mol; Aronu 15/45/30 wt% 45.1/45.9/31.2% | 32.51 kJ/mol (20 intervals); 44.24/46.95/31.6%. | MEA Kim source intervals; MEA transfer and canonical-pressure Aronu cohorts. |
| `sections/mea_system_modeling_results.tex:108`, `sections/transfer_results.tex:188` | 19.4→33.5% for the 19 Ma’mun pressures or adopted 33.5% | Salt-anchored 38.36%, previous shared set 33.47%, historical 16-parameter fit 19.43% on the matched set. The handoff’s field named `prior_F2_Pa` reads the 16-parameter file. The generated table retains both older rows with their explicit source identities. | MEA Baygi matched pressure. |
| `sections/transfer_results.tex:6–9,33,39,48`, `supplement.tex:443,561,564–576` | Free/fixed objectives 61.2853/62.0651, −219 ± 81 K; 0.86 SE; fixed slope reported; 59.70/58.89 loaded cost; eight fitted coordinates | Free model: 76.3119, −51.998 K with 63 K conditional SE, nine fitted, two active bounds. Fixed sensitivity: 77.6428, +1.33094 objective, distance 1.55 SE below the free slope. Loaded costs fixed/free 74.01/73.60. Free k(AMPH⁺–water) −0.202 at 353.22 K and −0.187 at 393.15 K. AMP R4 constant SE 0.230. | AMP expanded free and −150 K sensitivity objectives, slopes, coordinates and contributions. Old fixed-slope scan and 353.22 K intervention are historical. |
| `sections/transfer_results.tex:14–24,34,36,179`, `sections/conclusion.tex:5`, `supplement.tex:395–398,530–537,565–573,579–598` | 73 confirmed, 20 unconfirmed, 363.15–393.20 K, 26.8–30 wt%, 0.400–0.966, six measured states; 14 of 15 matched-P checks; 1.212/1.238 MPa and −0.0199 vapor descent; 28.10/25.30 and 28.35/25.47% hot-pressure scores, 7+7 descents; all worked split and curvature numbers | Keep as historical 47-pressure results (including #432/#433 and the older-slope controls). Expanded free and fixed find zero native/supplied descents. At the historic feed, common pressure 2.037241 MPa gives 0/1 confirmed attempts per expanded model. Salt-anchored free/fixed bubble pressures 1.886313/1.793666 MPa. The 18 hot Hartono total pressures are fitted with 6.99/7.28% AARD, and 40 loaded Tong are fitted; five Tong binary pressures remain out of fit. | AMP expanded search outcomes; hot Hartono and Tong entries; AMP S14 replay and historical original AMP S14 split. |
| `sections/transfer_results.tex:43,91,112`, `supplement.tex:336` | Model lines and source panels from the older transfer figures | AMP panels are low-T Hartono, hot Hartono, Tong, Kundu. MDEA panels are Kuranov 413 K, corrected Kamps, Sedighi, Ermatchkov, Xiao, fitted Kuranov. Crosses are adopted predictions at measured conditions. Gap-onset figure includes both binary laws and original grid of gap thresholds. | AMP and MDEA deviations by group and MDEA CO₂-free onset brackets. No adopted off-observation transfer curves were retained. |
| `sections/transfer_results.tex:49` | AMP binary 1–3%; carbamate deviation compared to previous pressure score | 1.08% binary pressures, 4.55% binary vapor fractions, 26.83% carbamate fraction with signed bias +4.06%. | AMP expanded free binary and nmr entries. |
| `sections/transfer_results.tex:56–69`, `supplement.tex:450–453,522–524` | k = 0.7650, 0.1325, 1.0; correlations 0.960/−0.974; objective increases 1.023/0.024 under 1.3987; two splits (288.71 K/1.121 MPa and 373.15 K/203.127 MPa) and 0.391 mol energy test | Historical #417/#432/#433 comparison. Keep its metrics and tie the 1.3987 allowance to the earlier bound profiles. For the adopted set use the two salt laws and separate search outcomes. | MDEA full search, MDEA confirmed grid split; historical `tables/mdea-shared-control.tex` and #429 ledger. |
| `sections/transfer_results.tex:77,82–85,213`, `supplement.tex:553–558` | Selected 564.5; other 582.8; unbounded 479.4 and 14 of 78 gap descents presented as a refit of this model | 537.6588 adopted bound fit. Keep the unbounded-vs-bounded objective comparison and its 14 descents on the previous declaration. Adopted CO₂-free onset bracket limits print identically; keep the bound and bracket numbers with the binary onset readback. | MDEA objective, MDEA CO₂-free onset brackets; `campaign/fit-*/outcome.json.gz`; historic #411 controls. |
| `sections/transfer_results.tex:97–100,180`, `supplement.tex:513–515,525–527` | 1,099 unfinished, 870 pressure reference, no grid split; 27 vapor states, 23 native, 4 supplied-only, 16/27 converged and 24 two-phase results | Adopted 10,576 / 11,824 completed, 1,248 incomplete, 1,024 bubble-reference refusals, 75 descents, one confirmed grid split at 383.15 K, 121.309 MPa, loading 1.368, decrease 4.23349e−5 mol vs 9.24245e−10 mol numerical error. The 27-state classification counts are historical. | MDEA full search, incomplete causes, confirmed grid split. |
| `supplement.tex:516–521` | 262.862 MPa confirmed split, densities 22,214 / 25,053 mol/m³ and 4.387% dense fraction attributed to the reported set | Keep the split, 1.394e−3 mol Gibbs decrease and 7.60e−10 mol paired error, compositions and curvature with the previous shared set. Adopted at the same T/P/feed is unresolved. | MDEA 262.862 MPa worked state, attempts and Gibbs decreases. |
| `sections/transfer_results.tex:106–107,159,181` | 29 overpredicted, AARD = bias 30.6%; other fitted MDEA metrics 0.1–13.8%; outside-pressure source range 17.9–85.4% | The same 29 have AARD 12.49%, bias +11.26%. Drop “all overpredicted.” Other fitted MDEA metrics 0.1–13.9%. The checked nonfit range is 3.1–92.6% across the amine transfer groups. | MDEA Kuranov above 368 K and by-observable/source deviations. |
| `sections/transfer_results.tex:120–126,138–139,143–144`, `supplement.tex:507–509` | Binary refit 152→17.1, 0.8→9.5%, reactive 28.5→23.1, 53.9→62.9, 0.9→1.9%; correlation 0.974; one search unfinished | #425 comparison remains historical, both columns use previous shared set. DEA adopted correlation 0.97043; 1,269 of 1,271 searches complete. The old Lawson refusal persists, and one grid search at 363.15 K, loading 0.8, 3× bubble pressure is also incomplete. | DEA candidates, DEA refusals; DEA conditional-uncertainty record; #425 historical table. |
| `sections/transfer_results.tex:139`, `supplement.tex:206–207` | DEA Δln K₄ −1.309 ±0.618, ratio 0.270, δh −11968 ±1344 J/mol; AMP +1.233 ±0.265, ratio 3.433 | DEA −1.438 ±0.729, ratio 0.237, −11969 ±1628 J/mol. AMP +0.389 ±0.230, ratio 1.475, δh −5000 J/mol on lower bound. At 298.15/313.15/393.15 K the DEA shifts are −1.207/−1.438/−2.373 (SE 0.756/0.729/0.625); AMP +0.486/+0.389/+0.002. | DEA and AMP fitted R4 parameters and completed law; each transfer's `results/salt-anchored-435/hydrolysis/shift.json`. |
| `sections/transfer_results.tex:194,196–198,203`, `supplement.tex:618–619,655–658,676` | MDEA K82 19.53%, same-cohort fit/outside 19.1/22.1%, K66 20.09%, Ermatchkov 17.9%; Hong comparison 22.59/21.25% for MEA and six-source 20.97% | K82 8.75%; the 70 fitted subset 9.69% and 12 outside 3.32%; K66 10.12%, Ermatchkov 38.42%. MEA strict Hong overlap 24.97%, 145-row overlap 23.40%, 159 six-source 22.92%, Wagner 31.61% on 23. Use the regenerated Hong table for caloric/density comparisons. Published comparator values keep their own roles. | MDEA Kuranov matched pressure K82 and not fitted; MDEA Ermatchkov and Kuranov; MEA Hong matched pressure / density / heat. |
| `sections/transfer_results.tex:174–175` | About 25% for both bands; Cp/density 1.3/0.4%, minima −2.1/−1.1%; caloric source biases from old fit | Pressure 27.25% for 69 and 29.66% for 66. Stripper Cp/density 1.2/0.4%, minima −1.9/−1.1%. Heat underestimation 5.8/10.0/13.4% for Vinjarapu/Kim 2014/Kim–Svendsen. | MEA temperature band entries and band-point cohorts. |

## Additional supplement text

| Location | Previous wording or value | Replacement or disposition | #435 handoff entry or retained locator |
|---|---|---|---|
| `supplement.tex:209–212` | DEA carbamate uses 179.8579 K and MEA diameter 5.3480 Å × 1.1593; AMP described as using the same reported MEA basis | DEA now uses 204.0748 K and 5.2012 Å × 1.1593. AMP retains the previous F2 carbamate energy 179.8579 K, k = −0.0661 and 5.3480 Å diameter lower bound. Describe the older standard errors on that basis if retained. | MEA carbamate energy/diameter; DEA selected declaration; AMP free selected declaration and fitted carbamate bounds. |
| `supplement.tex:269–271` | Carbonate within bicarbonate pool 5.9e−6–0.039; pH 9.84→7.92, R1 10.63 vs R2 8.89; old electrode offsets | Adopted eight-state calculated range 1.61e−5–0.06444. pH 10.505→8.699 and 11.365 (raw R1) vs 9.621 (R2) at loading 0.30. The plotted-electrode offsets are historical read-offs. | MEA pH readback, carbonate-pool comparison and MEA activity entries. |
| `supplement.tex:331` | Böttinger: 7.2137/7.2136% amine; 11.1441/11.1435% inorganic pool (0.5/2.5 MPa) | 7.2136/7.2135% amine; 11.1935/11.1918% inorganic pool (0.5/2.5 MPa). | MDEA Böttinger deviations by source and state pressure. |
| `supplement.tex:399` | −81.553 kJ/mol and 84.628 J/(mol K), stencil difference about 4e−7 | −81.795 kJ/mol, 84.890 J/(mol K), analytical minus fine stencil −3.42e−7 J/(mol K), or 3.60322 kJ/(kg K) on solution mass. | MEA S15 heat, heat capacity and stencil entries. |
| `supplement.tex:407` | At pCO₂ 1.559 and 73,206 Pa, +0.00187 and +15.03 Pa; −81.553→−81.603 kJ/mol | At pCO₂ 1.562 and 87,678 Pa, +0.00198 and +4.84 Pa; −81.795→−81.850 kJ/mol. | MEA reaction reference and S15 system/fixed pressure heat; `MEA/F4/q4.json`. |
| `supplement.tex:499,530–536` | 6,121 MEA trials; AMP 7,301 prior bank, 93/93 recovery and 609/666 pressure matches attributed to comparison fit | MEA retains 991,602 supplied evaluations (6,121 × 162); AMP original-bank and search-recall numbers belong to the previous model. Use adopted expanded native/supplied tallies for the reported fit. | MEA F4 supplied trials; AMP expanded free and −150 K supplied-trial counts; #432 Q7 for original search. |

## Display evidence and limits

- #435 provides measured-state MDEA and AMP predictions, so those two figures use points at observed conditions. Their old off-observation curves have no adopted, like-for-like retained curves.
- The DEA binary refit comparison (#425), previous shared-parameter sweep (#417), electrostatic replays (#405/#423), and original 47-pressure AMP diagnostics (#432–#434) retain their original sources. The published comparison table retains the 16-parameter row on its original data basis.
- The historical S14 AMP table retains the original split; the supplement adds its common-pressure comparisons for the expanded models. The MEA S15 display uses the adopted reference state and common-molality readback. The MDEA 262.862 MPa case retains the historical split alongside the unresolved adopted replay.
- The source data inventory is regenerated as a standalone table. It has no active TeX input in this branch. The inventory check uses the Zotero bibliography export because it includes source keys beyond the manuscript bibliography.

## Regenerated files

Tables and inventory in `tables/`

- `amine-summary.tex`
- `bound_profiles.tex`
- `calibration-data.tex`
- `choice_cost.tex`
- `dea-binary-tradeoff.tex`
- `interaction_matrix.tex`
- `kim_alternatives.tex`
- `mdea-shared-control.tex`
- `mea_data.tex`
- `mea_reference_state.tex`
- `objective_groups.tex`
- `pressure_sources.tex`
- `published-models.tex`
- `reaction_equilibrium_constants.tex`
- `species_parameters.tex`
- `supplement-amp-ranges.tex`
- `supplement-carbonate-sensitivity.tex`
- `supplement-dea-ranges.tex`
- `supplement-hong-comparison.tex`
- `supplement-mdea-ranges.tex`
- `supplement-temperature-bands.tex`
- `supplement-transfer-bounds.tex`
- `supplement-transfer-data.tex`
- `supplement-transfer-parameters.tex`
- `supplement_check_values.tex`
- `supplement_correlations.tex`
- `supplement_data_inventory.tex`
- `supplement_fitted_parameters.tex`
- `supplement_interaction_matrix.tex`
- `supplement_mea_comparison.tex`
- `supplement_reaction_coefficients.tex`
- `supplement_shared_remaining.tex`
- `supplement_species_parameters.tex`
- `transfer-fitted.tex`
- `transfer-species.tex`

Figures in `figures/generated/`

- `amp-current-measured-model.pdf`
- `amp-splits.pdf`
- `concentration-pressure.pdf`
- `dea-current-binary-comparisons.pdf`
- `dea-current-measured-model.pdf`
- `dea-integral-heat-concentrations.pdf`
- `density-curves.pdf`
- `heat-of-absorption.pdf`
- `jakobsen-carbonate-share.pdf`
- `loaded-pressure-residuals.pdf`
- `mdea-current-measured-model.pdf`
- `mdea-gap-onset.pdf`
- `mea-water.pdf`
- `pressure-uncertainty.pdf`
- `pressure.pdf`
- `speciation.pdf`
- `split-energy.pdf`

The display checks also compare `tables/number-sources.json` and `builds/347-figure-hashes.json`. The species macros have no model-dependent results.
