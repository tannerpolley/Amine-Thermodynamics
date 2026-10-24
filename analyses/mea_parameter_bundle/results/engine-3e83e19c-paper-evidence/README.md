# Engine 3e83e19c paper evidence and reported-record adoption

**The candidate is adopted byte for byte. All six assessment modes, 307-row replay identity, five curve families and the displayed-input inventory pass.** The former 100-line stop was superseded by the owner's 2026-10-24 authorization of 150 gross added executable lines. The completed change has 141 executable additions, including both `.py.txt` producers, plus one line updating the existing selected-record hash assertion (142 including that test). Deletions provide no credit. Independent delivered review remains for the parent; no merge or manuscript promotion is claimed.

## Numerical result and limits

The 307 objective rows have cost **148.87893934557388**; the common 149-row cost is **23.860996312136727**. The independent fresh replay has exact declarations and zero relative difference in every prediction, residual, weighted residual, row cost and summed cost against #212. All predictions and costs are finite; exactly zero values stay zero. [Replay identity](replay-identity.json) records all 307 ID-matched comparisons at the required relative tolerance of 1e-10 and absolute zero tolerance of 1e-300.

The [assessment completeness checks](assessment-completeness.json) cover 6 Cp proxy evaluations (4 displayed rows), 210 densities, 47 declared loaded-density replays, 22 heats, 10 carbonate shares and 375 admitted state calculations yielding 462 unique targets. Three canonical states remain explicitly inadmissible, as declared. There are no unavailable assessment rows. All four Cp rows pass their enthalpy and proxy interpretation checks, although one differs from the source by more than 3%. The fitted Vinjarapu and non-fitted Arcis heat RMSEs are 1.8350098647473438 and 8.115640714619083 kJ/mol CO2. Density scales retain their assigned source meanings; they are not uniformly measured uncertainties.

The [curve completeness checks](curve-completeness.json) cover all 5 families, **874 states and 2211 quantity rows**: pressure 380 states/rows; species 181 states/1448 rows; heat 93 states/rows; density 150 states/rows; MEA-water 70 states/140 rows. All 31 references and 150 midpoint checks pass. All 1829 fixed-grid quantity rows repeat exactly for the same new record. Old/new availability is compared separately at fixed declared-state keys: there are no missing keys or availability changes. Historical values are used only for this diagnostic, never as new displayed predictions. Species loading ends at 0.60. Species and density bubble pressures are complete; 13 species states and 8 density states lie below their bubble pressure and retain that indicator. No monotonic pressure-direction exception is found.

These results are fixed-parameter predictions, calibration comparisons and numerical verification. They do not establish independent physical validation, global phase stability, parameter uniqueness, prediction intervals, concentration transfer or process-use qualification. Conditional uncertainty remains conditional on fixed inputs, residual weights, active bounds and local linearization.

## Upstream gates and identities

[Gate verification](gate-verification.json) stands: 880 upstream hash checks (284 for #212, 54 for #213 and 542 for #214), with all three issues merged in base `74bb89a45987e0f1062edbcc32c723b8d20fcfde`. The immutable wheel is Engine commit `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, SHA-256 **`0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`**. All 12 installed Engine files match the wheel. Every calculation uses that installed wheel; no Engine source checkout is imported. The replay and display calls independently reverify it.

- #212: 44/47 loaded densities meet twice their row scale. Miss IDs are the permitted three; the largest absolute CO2-free error is 0.557484452458425 kg/m3, below 1 kg/m3.
- #213: all six exact computed limits pass. Its `limits.json` and density-free `parameters.csv` are bound below.
- #214: the reported record has no resolved descent at 162 complete states, with all 1458 scheduled trials. The comparison has 54 descent states and 143 descending trials; its 1458 trials are also complete. The finite search does not certify global stability. The 324-row two-fit export replaces the old 73-state block.

**Earlier selected-record dependency:** #212 and #213 read the old selected record through their former helper default without listing it in their provenance. Their emitted Engine inputs were shown identical with each supplied record. See [#214's dependency account](../engine-3e83e19c-phase-search/run-2/README.md) and `earlier-dependency.json`. The #213 helper hashes were checked at its merged commit `4e5e5f599c0a14253cae00fbbc7e87a34eee0de9`; #214 subsequently changed those helpers. Neither earlier issue was rerun here. The current assessment and curve producers pass the explicit mapping through those helpers.

## Execution, adoption and consumers

The order was assessments, assessment reduction, package point-data reduction, comparison-density export, water display, #212 imports, model curves, inventory, adoption and consumer updates. The independent replay ran as the point-data identity check. The six assessment timings are frozen separately in [assessments-timing.json](assessments-timing.json); [execution.json](execution.json) retains commands, timing, exit codes, transient user units and the one corrected temporary-sandbox omission. Calculations ran at niceness 10 with memory-sized process pools and one numerical-library thread per worker. No solver policy, bound, start or tolerance was changed. No fit, phase search or water refit was run.

The comparison export has all 47 loaded-density rows from #212's comparison declaration and hashed replay; it does not rescore or invoke the historical screening command. The water display evaluates 42 states of the unchanged water declaration, retaining its enthalpy finite differences, saturation checks, CSV and record-bound summary. The 11 [hashed display imports](display-imports.json) include 14 permittivity rows and their separate summary, both 14-row Arcis results, the 50-row constant-interaction Cai replay, comparison endpoint, reported/comparison scores and comparison replay, plus the three conditional uncertainty files. Conditional uncertainty was copied without recomputation.

[Adoption](adoption.json) records the exact replacement:

- Previous selected bytes: `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.
- New selected/candidate bytes: `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`.
- Candidate: `../engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json`.

Active consumers are updated: `render_parameter_tables.py`, `render_regression_overview.py`, `analysis.yaml`, `notebook.qmd`, `parameter-record-history.csv`, the existing hash assertion in `tests/test_source_corrections_152.py`, and `check_a7_selected.py`. The notebook renderer also refreshes its existing joint-calibration and high-temperature table blocks. All renderer values read the new package. The 153-quantity check passed before adoption on the explicit candidate and afterward through the adopted default, with worst relative difference 2.7277643719510691e-15. The selected-record domain/hash test passes (1 test, 3.57 s).

The historical `mea_association_volume.py`, `phase_extension_201.py` and `phase_regeneration_208.py` commands now bind the immutable old endpoint `../joint-recalibration-170/amendment-7/restricted-2/fit/usable-budget-endpoint.json`. Their old hash assertions and retained numerical outputs are unchanged.

The notebook uses current point-prediction figures and links the complete new curve data. Historical manuscript images are no longer displayed as current notebook results. Notebook validation and HTML rendering are retained under `/tmp/issue215-notebook-render`; port 8770 and its service are untouched. Manuscript source and manuscript generators remain for #211. Their old-package hash checks are unchanged and must still refuse mismatched inputs.

## Displayed-input inventory

[Inventory](inventory.json) lists **57 inputs: 52 on Engine 3e83e19c and 5 source-only; zero non-3e83e19c Engine-computed displayed inputs**. Every row below has its byte SHA-256. For every `3e83e19c` row, the producing wheel is the full pinned wheel hash above. Arithmetic reductions retain the producing calculation's wheel. Source-only values are density scales, source-density interpolation, source caloric/reaction coefficients, literature entries and nomenclature; they are unchanged. The literature/nomenclature row binds only the unchanged source strings in that generator, not its pending Engine-dependent branches. This inventory supplies #211's inputs; the existing manuscript generators still bind their historical package until #211 changes them.

| Display / table / figure input | Repository path | Byte SHA-256 | Producing Engine |
|---|---|---|---|
| Reported parameter, interaction, association, permittivity and reaction tables | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/reported-parameters.json` | `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91` | 3e83e19c |
| Comparison-fit parameter table | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/comparison-parameters.json` | `efb2a9abe3787410734394f5ee32e6eade42d7cb6f5ad23445a357423690b2f3` | 3e83e19c |
| Objective groups and fitted coordinate table | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/fit-summary.json` | `7968c9ce1ca9947d70795787afedccf4f90786a77196e890412a13871f37d0fb` | 3e83e19c |
| Conditional identification and uncertainty summary | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/conditional-uncertainty.json` | `07058e4cc7401bd0b8731989c531d25c0a6450df4087080d20679fa89f939538` | 3e83e19c |
| Conditional standard errors | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/conditional-standard-errors.csv` | `4cd6f82953a4f619dee0f1110558cd4c241278f2870a2ee5646cb487ec475e0d` | 3e83e19c |
| Conditional correlations | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/conditional-correlations.csv` | `cbb2a35a48285bd4b4cd8b6a0b6a27b1c13d46793ce31b86ef06003e0a71aed8` | 3e83e19c |
| All objective/source statistics; Cai and Kiepe figure points | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/fitted-rows.csv` | `e18efef61548d20e40578a2223cb203dd903ed288c02b94ab24009d6b861fb44` | 3e83e19c |
| Pressure figure point predictions | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/pressure-figure-data.csv` | `1dd662ce16fdaf808f11ddbff5de704e091fa8e3d4566a80c80cb89d7bb32a0b` | 3e83e19c |
| Species figure point predictions | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/species-figure-data.csv` | `161c1547191b09114bc60f3673f7470307d8939340cdfcad7cdaee810ac4bf21` | 3e83e19c |
| 19 Matin bicarbonate plus carbonate pools | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/pool-figure-data.csv` | `361dabafcdbb4ce6ca62607cf3981107141bae80f49e9f48016c27b7616a73ea` | 3e83e19c |
| Canonical pressure figure points and comparisons | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/canonical-pressure.csv` | `ba6c7b1dcf6f13955a5b2bb3d63cf9b7f6017d0dca1918ca990855f9e373dcf4` | 3e83e19c |
| Wagner pressure figure points and comparisons | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/wagner-pressure.csv` | `f724f4bf54f690be7d8e9f0ddfaa33eeaefa067412795e6f1c33f171d349fee5` | 3e83e19c |
| 15 and 45 wt% transfer comparisons | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/transfer.csv` | `287a8eca0b470e9be44a66b215aa0645beb7903554f1e621e57a3101cbd9adb1` | 3e83e19c |
| All 462 displayed/assessment state targets | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/state-targets.csv` | `3009346dd3bdaf8c5cc8282f10b220be37f05385775bfb874819bda460d79c9f` | 3e83e19c |
| Outside-fit and high-temperature statistics | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/state-summary.json` | `00ae69922c8fb8c10321090f1cf504f0546d6d38cfcee7b1811de54db8409b2b` | 3e83e19c |
| High-temperature comparison table | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/high-temperature-comparison.csv` | `ceb6978174ffff22efe93cb8eec6c71bca136beb9263e7b888695b41c47cf12d` | 3e83e19c |
| 22 heat figure points and heat/source tables | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/heat.csv` | `7cad1a82659d117f559ae2352e02efa529ac98e4d72d782e0767de8cb301a7eb` | 3e83e19c |
| 210 density figure points and density/source tables | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/density.csv` | `f1014fecaee1657d4a9e5994065ff48a1f3bfea4312c4159df02c9d7ed351055` | 3e83e19c |
| Four Hilliard heat-capacity figure/table points | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/cp.csv` | `3d075663fc04bbcb51057709ef2bebef9187f0340610b4b02378c2f959c666c6` | 3e83e19c |
| Ten carbonate-share comparisons | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/carbonate-share.csv` | `5c1af7ed002c4cb33a13474a9489da68f756a01a42d204acbab55205ae683ae0` | 3e83e19c |
| Density, caloric, Cp, carbonate and assessment summaries | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/summary.json` | `ad50d8f2698d87795ef6d870b93c92055f3774fbcea7383c9aa9acd5c4634602` | 3e83e19c |
| 324-row phase export, two fits at 162 states each | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/phase-family.csv` | `f9d4d8196f02bbb7510dc5bea879144c86f48f1f56e2ad2a9c269565c9ac6855` | 3e83e19c |
| 47 comparison-fit loaded-density errors | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/comparison-loaded-density-errors.csv` | `e5ef2ab55db3dbb1addd13982431a47da11646f2a6cd11a2b4f793a3eda5bd85` | 3e83e19c |
| 42-state water figure | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/water.csv` | `feee3080ff3cc5972c6b10deb86feee825902ca4647383a45c3558fbe213f2d0` | 3e83e19c |
| Water figure record identity and summary | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/water-summary.json` | `5968cb4af03c73cbfa05b9215f76b4e384c0a1d72d4bb25fc2e4f7dcce25ae39` | 3e83e19c |
| Water enthalpy finite-difference and saturation checks | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/water-checks.json` | `c6ac65a592715c11adde42f2f3af11f07a3704e082e2abac1f99db4131cda4f1` | 3e83e19c |
| 14 permittivity figure points | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/permittivity/rows.csv` | `ad0e49cc4aeeb18e442deeb48328e7d07eeead4e47853c9e4ddd24c7694f8503` | 3e83e19c |
| Permittivity figure identity and statistics | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/permittivity/summary.json` | `b707b7ff5edddd9e58049da48776a74fbd6faf3dc7736805fa48974676b385ef` | 3e83e19c |
| Both 14-row Arcis results and constant-interaction Cai cost | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/refit-display-summary.json` | `ed5f1c9216a3acba94e07643229c0df4ef1086803032f58d3879d2d6f524bedd` | 3e83e19c |
| 50-row constant-interaction Cai result | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/cai-constant-replay.json` | `bbdba85ee6aaca496e99c2e97a68de13f3e954fd4563659c037b3b3df768317e` | 3e83e19c |
| Reported-fit adopted objective/limits comparison | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/reported-score.json` | `a1aba0ded55be8d51efc88f259e9c36ca4d4a52ba33f20528ec8b5a3e66793e9` | 3e83e19c |
| Comparison-fit objective/limits comparison | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/comparison-score.json` | `b9e15f88f43b7b1decbf68ffdbaa0c30f5692f21fc2d53070c1aa24c7e80c7d9` | 3e83e19c |
| Comparison point declarations/predictions underlying exported density errors | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/comparison-full-replay.json` | `2887a71f05ef70647af232964b1aeef538555cd079b5acf66c8330f45ba795a7` | 3e83e19c |
| Independent 307-row replay identity verification | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/full-replay.json` | `aeb3331cf95cb174faa9cfa5891e887dbae0829448b5c67a2da17727ed386560` | 3e83e19c |
| pressure model curves | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/model-curves/pressure.csv` | `af6664e11702a23eea7e8d5d7f6b38ada7f351aaefa4e91f4d00d6234247349f` | 3e83e19c |
| species model curves | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/model-curves/species.csv` | `546e7415b5934e880ebfb077cada4f415fea6cbc2e968033a33f06e9cc2a22a8` | 3e83e19c |
| heat model curves | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/model-curves/heat.csv` | `e6e785e1a5e0ae1846e06aeecf22eb5091f0520197128f0c9d19d4ee777fa6b4` | 3e83e19c |
| density model curves | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/model-curves/density.csv` | `6b822d9080a69c85bf029199eaacbdc1d814f521e0fc530e0f4ac073030ec600` | 3e83e19c |
| mea-water model curves | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/model-curves/mea-water.csv` | `08c3388d573692677d73b7e1fb08d224431d951ea53b58805fa970e1781fe95a` | 3e83e19c |
| Curve references, sampling, repeat calculations, balances and availability | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/model-curves/summary.json` | `4319bb87f17f72b181facf8ac8b6793c6b6e9a330f2b21502a4068c4a18f3f10` | 3e83e19c |
| #213 computed limits | `analyses/mea_parameter_bundle/results/engine-3e83e19c-density-free/limits.json` | `5adb3c08282621bc33f0fd0e1c59a865f9c31d4149506df85948acef06fcdc41` | 3e83e19c |
| #213 density-free reference parameters | `analyses/mea_parameter_bundle/results/engine-3e83e19c-density-free/parameters.csv` | `0de35d543269c5b90665e09dadb1dc70e92e2506f4bbbdf225cdb24f02ad5996` | 3e83e19c |
| #214 phase-family.csv | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/phase-family.csv` | `f9d4d8196f02bbb7510dc5bea879144c86f48f1f56e2ad2a9c269565c9ac6855` | 3e83e19c |
| #214 reference-pressures.csv | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/reference-pressures.csv` | `b48914b3fe864979753668b69c8b33ae730613700bc0466462e03d39be37f9c2` | 3e83e19c |
| #214 states.csv | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/states.csv` | `2a6f75cee58080af8017309ba68d2f74debe0cf55e140182a7ae83767c347c7b` | 3e83e19c |
| #214 trials.csv | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/trials.csv` | `6244f0a6a819dae5321bf65a44192a2453abec3d43e91b879cee380566221e6f` | 3e83e19c |
| #214 split-confirmations.csv | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/split-confirmations.csv` | `035a31e81a2141d2385812314af0690e9e12c9108b68d67f546dacfa44547fe8` | 3e83e19c |
| #214 counts-by-temperature.csv | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/counts-by-temperature.csv` | `988893b55524a1518e919fe5bec7c1ed12a655267b95278363b1d71646037d63` | 3e83e19c |
| #214 outcomes-by-temperature.csv | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/outcomes-by-temperature.csv` | `6030a1b0bba9351d05cca971a325d42f5681dee8f11d9a5f218f80eba250e93e` | 3e83e19c |
| #214 summary.json | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/summary.json` | `8a86292f110e8d4891a8cef8edef1cf06794522145b5e022dd41e0c7bf3c9a88` | 3e83e19c |
| #214 validation.json | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/validation.json` | `aa6eb493a7409d7aa5a61079607773320798e05f316ff115af354308b9202032` | 3e83e19c |
| #214 provenance.json | `analyses/mea_parameter_bundle/results/engine-3e83e19c-phase-search/run-2/provenance.json` | `e67105602343bd23a79ebe03559bcb6568e7ec2b4a0ca2fc606148a9dfa3589e` | 3e83e19c |
| Source scales, caloric/reaction inputs or interpolated source-density differences | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/source-only/density-scales.json` | `ee61922f62b40e8a3f947e85bb9d0e1247ff5dd97e567e554f7b90e589dc95ce` | source-only |
| Source scales, caloric/reaction inputs or interpolated source-density differences | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/source-only/physical-ideal-gas-calorics.json` | `c94d504e68c6dc6e85d3d950cc51422499846729b1a06994b362040be991924a` | source-only |
| Source scales, caloric/reaction inputs or interpolated source-density differences | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/source-only/chemical_reaction_source_contract.json` | `39db0d7ef972dc7eb41328bdf2ec3f67f62c33fc2bf0fdc7bab471ade9aefb55` | source-only |
| Source scales, caloric/reaction inputs or interpolated source-density differences | `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/source-only/density-source-differences.json` | `3522ac77fe039ac5a807f80ded2e20d7e3a6f5e72790e0313395d38d51ba1fb0` | source-only |
| Unchanged literature comparison entries and nomenclature, only source strings | `docs/scientific/latex/scripts/final_rerun_tables.py` | `9cf407ff3852f5de8832b6c70b65875493badd70a58112f878cdf6f729dcb8ae` | source-only |

## Change accounting and remaining delivery

[Change accounting](change-accounting.json) uses the fixed base `74bb89a45987e0f1062edbcc32c723b8d20fcfde`. Executable `.py.txt` files are included despite the generic classifier calling them documents.

| Executable responsibility | Gross added lines |
|---|---:|
| Explicit mappings in shared evaluation, probe and observation producers | 21 |
| Assessment bindings, byte hashes and worker sizing | 12 |
| Assessment reduction and authoritative limits | 12 |
| Point-data bindings and imported conditional uncertainty | 22 |
| Curve bindings, same-record repetition and complete availability | 12 |
| Comparison-density export and water display | 45 |
| Active notebook/default consumers and historical command pins | 17 |
| **Executable total** | **141** |
| Existing selected-record hash assertion | **1** |
| **Conservative total including the test** | **142 / 150** |

The obsolete local conditional-uncertainty recomputation was removed; #212 owns the imported calculation. No persistent test was added. There is no scientific stop. The parent owns independent delivered review and integration; #211 owns manuscript input bindings, phase displays, limits table, numerical captions and prose. This branch is committed without merging.
