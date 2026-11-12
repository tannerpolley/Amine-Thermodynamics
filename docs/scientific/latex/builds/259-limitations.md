# Part I revision, issue 259

The owner, as investigator, promoted notebook commit 186f361aff73a2dab0bcae10b48c2cd0db731f04 on 2026-11-12 for Part I manuscript use of Supported #255/#297 and #307 MEA evidence, retaining conditional-uncertainty, finite-search and source-conflict limits.

The later owner scope comment, issuecomment-6838067984, replaces the earlier amine-general scope. This revision uses MEA parameter document f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97, Engine 391dfe5d64ede5036bf160bc6ae037ad5e14af32, wheel 0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b. Historical comparisons keep their original identities. No thermodynamic calculation or parameter fit was run for this revision; display commands reduce and render retained values only.

| Listed statement | Disposition and evidence |
|---|---|
| Six bound parameters and conditional errors, abstract/results/conclusion/S8 | Restated with current identities: bicarbonate–water replaces MEAH diameter as bound coordinate. Three free standard errors exceed their point estimates. #307 adds 5.41–16.00% conditional pressure SE at 47 fitted states, full ranking and inward profiles. These are local conditional uncertainties, excluding model discrepancy and future noise. |
| Narrow bound restriction and density trade-off, results/conclusion/S11 | Removed as a current limitation. #255/#297 uses the original wide interval, MEAH diameter 4.904548 Å, observation cost 148.5105 against outgoing 148.8833, and 46/47 loaded densities within twice assigned scale. |
| Phase-search omissions, results/conclusion/S10 | Removed for the formerly excluded states: all five are available without descent. Current finite searches cover 1903 enforced, 576 offset and 162 census states without resolved descent. Finite numerical verification remains distinct from global stability and physical validation. |
| Water function below its source range, theory/S6 | Removed. #260/#297 water ideal-gas record covers 273.15–400 K against IAPWS-95, maximum relative heat-capacity fit error 6.50e-7. |
| Uncertainty not propagated to pressures, S8 | Removed. #307 propagates correlated covariance at the 47 retained calibration pressures. It supplies local parameter uncertainty, not future-observation intervals. |
| 15/45 wt% concentration transfer | Restated as measured fixed-parameter errors: 33.89% over 33 observations and 44.53% over 37; no new fit-quality threshold. |
| Bicarbonate/carbonate and 353 K speciation | Restated with current errors and source qualifications. Current Matin comparison AARD is 67.77%; Jakobsen carbonate calculated/observed mean is 0.0213, range 0.00195–0.0749. NMR and titration do not supply interchangeable observables, pressures and uncertainties. |
| Absorption heat at higher temperature | Restated with adopted-record Kim interval RMSEs 4.810, 7.535 and 25.204 kJ/mol at 313.15, 353.15 and 393.15 K (source-consistent rows). Full printed and additional-exclusion comparisons remain displayed in prose. Missing pressure histories and conflicting printed rows remain source limits. |
| Heat-capacity domain | Removed the implication that only four states have been assessed. #297 retains 51 broad Cp comparisons, AARD 2.39%; the fitted unloaded 318.15 K state remains +5.43%. These measured errors are shown without rejecting the fit by an agent-selected threshold. |
| Higher-temperature density | Restated as measured errors: all 50 loaded Han observations give AARD 0.479%, RMSE 6.04 kg/m³; maximum absolute error 13.35 kg/m³. The five excluded Amundsen observations remain displayed; Amundsen/Hartono source conflict remains. |
| R4/R5 above 323.15 K | Restated as source-law extrapolation: independent high-temperature reaction-constant data are missing from the adopted calibration. Pressure and caloric comparisons assess the completed model. |
| Permittivity temperature/loading transfer | Restated as a missing-data qualification: 14 unloaded 298.15 K calibration measurements do not determine temperature/loading dependence. No unpromoted perturbed dielectric model is substituted. |
| Untested transfer to other amines | Removed. Abstract and conclusion point to companion Part II on transfer of shared parameters to other amine classes. |
| MDEA demonstration and its limitations | Removed from Part I: discussion subsection/figure, abstract and conclusion sentences and supplement S12. MDEA retained studies remain unchanged; Part II is issue 320. No Part II numbers enter Part I. |

## Display and PDF checks

The existing table and figure commands now read adoption-297/paper-evidence and uncertainty-307, checking parameter and wheel identities and retained input hashes. Source-only and historical inputs remain separately bound. Supplement precedes main in the background agent-heavy build. Cross-document references require a second ordered pass on a fresh build directory.

The journal metadata and existing `verification-receipt.json` remain owned by issue 206 and were not refreshed. analyses/_cse-manuscript.json was untouched. The ignored user_preferences.md and literature shelf were absent in this worktree; the main checkout's literature shelf was consulted, and the missing Zhang 2011 reading copy was inspected through its live Zotero PDF (MMAGNPIH/M3QDCZM7, §3.3, Tables 9–11). No bibliography refresh was performed.

The two independent manuscript reviews are pending.
