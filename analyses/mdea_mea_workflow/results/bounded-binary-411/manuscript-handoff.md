# MDEA manuscript handoff for issue 411

## Basis

**Owner decision (2026-11-23).** The reported MDEA parameter set is the bounded fit committed in `576125550`. It replaces the interpolated set, because it is a reproducible least-squares minimum under one stated physical constraint, while the interpolated set minimizes nothing.

**Model and wheel.** The MDEA model, data roles, weights and wheel (1.3.1 `05e94210`) are those of the current paper. Only the fitting procedure and the parameter values change.

**Locations.** Line numbers refer to the merged tree `268f078a8` (`origin/main` at `271d4a5d4`). Paths are relative to `docs/scientific/latex` unless a path says otherwise. Evidence paths are relative to this folder.

**Procedure, for the methods text:**

- Of the eight fitted MDEA parameters, only $k_{\mathrm{MDEA,w}}$ acts on the CO₂-free solution.
- Its linear temperature law is written about 423 K, the highest temperature tested, instead of 313.15 K. This is the same law, so the model is unchanged: the replay objective of the earlier set changes by less than $10^{-12}$ relative.
- $k_{\mathrm{MDEA,w}}(423\ \mathrm{K})$ has an upper bound of −0.0671135.
  - The bound is $10^{-4}$ below the largest value without a gap in the lower convex envelope of the liquid Gibbs energy at 1.466 MPa (5490 compositions, all other parameters fixed).
  - That onset value rises almost linearly, from −0.1323 at 290 K to −0.0670 at 423 K (about $4.9\times10^{-4}$ K⁻¹).
  - The fitted slope is $1.209\times10^{-3}$ K⁻¹, so 423 K is the binding temperature. The fitted interaction lies below the onset value at all 33 tabulated temperatures from 290 to 423 K.
- The fit has no penalty rows and no interpolation.

**Three initial sets:**

| Initial set | Objective | Active bounds |
|---|---:|---|
| Start 1 | 564.4836961 | $k_{\mathrm{MDEA,w}}(423\ \mathrm{K})$, $k_{\mathrm{MDEAH^+,HCO_3^-}}=1$ |
| Start 3 | 564.4836961 (same solution) | same two |
| Start 2 | 582.7796881 | $k_{\mathrm{MDEA,w}}(423\ \mathrm{K})$, $k_{\mathrm{MDEAH^+,w}}$ |

- Starts 1 and 3 reach the same solution: the objectives agree to $8\times10^{-12}$ relative and every coordinate to $4.2\times10^{-6}$.
- All three converge on the optimizer tolerance.
- At both active bounds of the reported solution, the objective gradient points out of the box, so each bound holds the objective down.

**Cost of the constraint:**

- Without the bound, the fit from start 3 converges at an objective of 479.4428.
- At that solution, 14 of the 78 CO₂-free searches detect an instability, and the convex-envelope scan finds a gap starting between 413.05 and 413.15 K.
- The data's optimum therefore lies inside the two-liquid region, and keeping the CO₂-free solution single-phase raises the fitted objective by 85.0, from 479.4 to 564.5.
- This comparison comes from one initial set. It is not a global bound.

Evidence: [gap-onset table](critical-k.json), [fit summaries and endpoints](fits/), [selected endpoint](endpoint.json), [run comparison](comparison.json), [declaration](../../inputs/bounded-binary-411.json), [script](../../scripts/bounded_binary_411.py).

## Parameters and conditional standard errors

The standard errors are computed as in the current paper and for AMP: the covariance of the free coordinates, conditional on the coordinates on bounds and on all fixed values (`Route.uncertainty`). The residual variance is 4.1053.

| Parameter | Interpolated set (in the paper) | **Bounded fit** | SE, bounded fit |
|---|---:|---:|---:|
| $k_{\mathrm{MDEA,w}}$ | −0.1939 at 313.15 K (SE 0.0017) | **−0.0671 at 423 K, upper bound** | — |
| $10^{3}\,\mathrm{d}k_{\mathrm{MDEA,w}}/\mathrm{d}T$ (K⁻¹) | 1.1549 (0.0324) | **1.2092** | 0.0135 |
| $k_{\mathrm{MDEAH^+,CO_2}}$ | 0.2553 (0.0435) | **0.2526** | 0.0353 |
| $k_{\mathrm{MDEAH^+,w}}$ at 313.15 K | −0.0255 (0.1596) | **−0.0096** | 0.0106 |
| $b_{\mathrm{MDEAH^+,w}}$ (K) | −18.235 (4.480) | **−15.929** | 3.546 |
| $k_{\mathrm{MDEAH^+,HCO_3^-}}$ | 0.8912 (1.4196) | **1.0000, upper bound** | — |
| $\sigma_{\mathrm{MDEAH^+}}$ (Å) | 3.6430 (0.0781) | **3.6553** | 0.0374 |
| $u_{\mathrm{MDEAH^+}}/k_B$ (K) | 596.464 (345.268) | **635.490** | 43.905 |

On the same basis, $k_{\mathrm{MDEA,w}}$ at 313.15 K is −0.1999.

Conditional correlations of the six free coordinates. The largest magnitude is 0.925, between $k_{\mathrm{MDEAH^+,w}}$ and $u_{\mathrm{MDEAH^+}}$; the others are at most 0.55.

| | d$k_{\mathrm{MDEA,w}}$/d$T$ | $k_{\mathrm{MDEAH^+,CO_2}}$ | $k_{\mathrm{MDEAH^+,w}}$ | $b_{\mathrm{MDEAH^+,w}}$ | $\sigma_{\mathrm{MDEAH^+}}$ | $u_{\mathrm{MDEAH^+}}$ |
|---|---:|---:|---:|---:|---:|---:|
| d$k_{\mathrm{MDEA,w}}$/d$T$ | 1 | −0.032 | −0.055 | −0.141 | 0.024 | 0.012 |
| $k_{\mathrm{MDEAH^+,CO_2}}$ | | 1 | −0.011 | −0.210 | −0.020 | −0.219 |
| $k_{\mathrm{MDEAH^+,w}}$ | | | 1 | 0.421 | 0.547 | 0.925 |
| $b_{\mathrm{MDEAH^+,w}}$ | | | | 1 | 0.306 | 0.458 |
| $\sigma_{\mathrm{MDEAH^+}}$ | | | | | 1 | 0.469 |

The smallest column-normalized singular value is 0.0185.

[Parameter table](parameter-table.json) · [conditional uncertainty](conditional-uncertainty.json).

## Results that change

| Quantity | Interpolated set (in the paper) | **Bounded fit** |
|---|---:|---:|
| Fitted objective | 605.01 | **564.48** |
| Parameters on bounds | 0 | **2** |
| Fitted Kuranov loaded pressures, AARD (66) | 20.59 % | **20.09 %** |
| All fitted pressures, AARD (131) | 11.48 % | **11.24 %** |
| Pressures not fitted, AARD (175) | 22.58 % | **25.83 %** |
| Ermatchkov, 101 CO₂ partial pressures | 15.36 % (bias −1.4 %) | **17.89 % (bias −6.3 %)** |
| Ermatchkov inside / above R5 range | 15.52 / 15.01 % | **18.23 / 17.16 %** |
| Corrected Pérez-Salado Kamps, 28 | 25.29 % | **28.08 %** |
| Xiao, 20 | 20.68 % | **31.07 %** |
| Kuranov above R5 range (29 rows, all overpredicted) | 32.2 % | **30.6 %** |
| Fitted MDEA properties other than loaded pressures | 0.1–13.6 % | **0.1–13.8 %** |
| Pressures not fitted, all amines (main-text range) | 15.4–85.4 % | **17.9–85.4 %** |
| Searches / not finished / at grid states without a bubble pressure | 11824 / 1039 / 810 | **11824 / 1099 / 870** |
| Distinct states searched | 10870 | **10870** |
| Records with descent evidence / distinct measured-state calculations | 77 / 28 | **76 / 27** |
| Liquid–liquid splits found | 1 (grid) | **0** |
| CO₂-free searches at 1.466 MPa, 393–423 K | 78 finish, none unstable | **78 finish, none unstable** |

The following hold for the reported set:

- **The former split state is undecided, not removed.** The state is 363.15 K, 78.62 wt% unloaded MDEA, 1.368 mol/mol, at 1.05 times the bubble pressure. The bubble-pressure solve there now fails (`LOCAL_INFEASIBILITY`, residual 0.0406), so the search is unavailable and neither finds nor excludes a split.
- **The 76 records with descents are a subset of the earlier 77.** They are the same measured-state records, 27 distinct calculations. All 96 liquid-labelled witnesses in the 48 records labelled mixed coincide with a vapor-labelled witness in composition and packing fraction to $2.35\times10^{-12}$. That is the coincidence test the paper used before ($3.07\times10^{-12}$), and it identifies the instability as toward a vapor. The isotherm and pressure-closure checks were not repeated.
- **Four** of the 11 Böttinger states at 0.5 MPa now show the instability only through a trial composition from an earlier search. Before, there were three.
- **The breakdown by data set is unchanged:** 4 Sobrino densities, 11 Böttinger states at 0.5 MPa and 2 at 2.5 MPa, 5 Zheng heats, 5 Merkley heats.
- **Not recomputed:** the bubble-pressure ratio range 0.1733–0.9990 of those 27 states.
- **Newly unavailable:** 72 grid records became unavailable and 12 became available. Of the 72, 68 failed the bubble-pressure solve and 4 stalled just above the 10⁻¹⁰ row limit.

[Search summary](stability.json) · [deviations](deviations.json) · [data rows](data-rows.json) · [published comparisons](published-pressure-comparisons.json) · [summary row](summary-row.json).

## Display generator

`scripts/dea_displays.py` now reads `analyses/mdea_mea_workflow/results/bounded-binary-411/`:

- The parameter table has the $k_{\mathrm{MDEA,w}}$ row at 423 K. The two bounded values carry the on-bound mark and no standard error, and the table note is revised.
- The supplement parameter note says that MDEA–water is the value at 423 K.
- The summary row, published comparisons, deviations, data rows, pressure curves and stability counts are the new files. The pressure figure keeps the retained measured-point locations.
- The #343 split and penalty reads are gone. They are replaced by checks that:
  - the reported fit has 78/78 CO₂-free searches without an instability, no convex-envelope gap, and $k$ below the onset at every tabulated temperature;
  - the fit without the bound has 14 instabilities;
  - the former split state is unavailable.
- New checked prose values: the two objectives, `564.5` and `479.4`, and the largest MDEA correlation, `0.925`.
- `final_rerun_tables.py` reads only the MDEA R5 source range from the old folder. That range does not depend on the fit, so the script is unchanged.

Regenerated displays are not committed, because they disagree with the current prose. To regenerate them, run `python docs/scientific/latex/scripts/dea_displays.py` from the repository root.

With the regenerated displays, `--check` passes all 18 displays and fails only on these 12 prose fragments:

| File | Required fragment |
|---|---|
| `sections/conclusion.tex` | `20.1` |
| `sections/conclusion.tex` | `17.9--85.4` |
| `sections/conclusion.tex` | `17.9` |
| `sections/transfer_results.tex` | `17.9--85.4` |
| `sections/transfer_results.tex` | `0.1--13.8` |
| `sections/transfer_results.tex` | `their bias equals their AARD, 30.6` |
| `sections/transfer_results.tex` | `Of the \num{11824} MDEA searches, 1099 did not finish, 870 of them at grid states` |
| `submission/highlights.txt` | `17.9%` |
| `supplement.tex` | `564.5` |
| `supplement.tex` | `479.4` |
| `supplement.tex` | `0.925` |
| `supplement.tex` | `20.09` |

## Old → new, by location

The replacement prose below is a proposal for the Writer. Every number in it comes from the files above.

### Abstract and submission

| Location | Old | New |
|---|---|---|
| `main.tex:96` | For MDEA, no liquid--liquid gap of the \COtwo-free solution is detected at the reported parameters, interpolated toward a stability-penalized fit; one loaded-solution split remains, at \SI{262.9}{\mega\pascal}, far above process pressures. | For MDEA, an upper bound on the MDEA--water interaction keeps the \COtwo-free solution free of a calculated liquid--liquid gap, at the cost of a poorer fit, because the fitted data favor the gap; no loaded-solution split is found among the searches that finish. |
| `submission_metadata.yml:11` | same sentence as `main.tex:96`, plain text | same replacement, plain text (CO₂) |
| `submission/chemrxiv.md:13` | the MDEA sentence of the abstract, as in `main.tex:96` | same replacement, plain text |
| `submission_metadata.yml:75–77` | `scope: MDEA model, reported interpolated set`; `path: analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/parameter-table.json`; `sha256: 42d6aafe4dd9e167bab3ac724bdd51a9f96d5791c4751ad5d5a0af46e8b8f3e3` | `scope: MDEA model`; `path: analyses/mdea_mea_workflow/results/bounded-binary-411/parameter-table.json`; `sha256: a00d0b04b37a99fcc27727d95e325b213fb2e2e317594dcad6a4bbfebc72d0d3` |
| `submission/highlights.txt:4` | At the reported parameters, searches find a liquid split only for MDEA, at 262.9 MPa | Bounding one MDEA interaction removes the CO₂-free gap; the data favor the gap (79 characters) |
| `submission/highlights.txt:5` | On Ermatchkov data, which helped choose initial MDEA parameters: 15.4% vs set I 16.8% | On Ermatchkov data, which helped choose initial MDEA parameters: 17.9% vs set I 16.8% (the comparison no longer favors this work; the Writer may drop the highlight, but `--check` then needs `17.9%` removed from the stated list) |
| `submission/graphical_abstract.tex:19` | `Fitted pressures: \textbf{20.6\,\%}\\[1mm] One liquid--liquid split,\\ at 262.9\,MPa` | `Fitted pressures: \textbf{20.1\,\%}\\[1mm] \COtwo-free gap\\ bounded out` |
| `submission/cover_letter.md:11` | They find one loaded-solution split for MDEA, at 262.9 MPa, far above process pressures, and none for AMP once … | They find no liquid–liquid split for MDEA once its water interaction is bounded to keep the CO₂-free solution single-phase, a constraint that worsens the fit, and none for AMP once … |

`highlights.txt:3` (10.5–28.5 %) still holds: MDEA is 20.1 %.

### Introduction and methods

| Location | Old | New |
|---|---|---|
| `sections/introduction.tex:38` | …the searches detect no instability for DEA, one loaded-solution split for MDEA, at \SI{262.9}{\mega\pascal}, and none for AMP once … | …the searches detect no instability for DEA and no liquid--liquid split for MDEA, whose water interaction is bounded to keep the \COtwo-free solution single-phase, or for AMP once … |
| `sections/data_methods.tex:46` | Each fit is started from two initial parameter sets, and the converged solution with the lower objective value is reported, except for MDEA, whose reported set is interpolated (\cref{sec:methods-phase}); these are local solutions, not a global search. | Each fit is started from two initial parameter sets, three for MDEA, and the converged solution with the lower objective value is reported; these are local solutions, not a global search. |
| `sections/data_methods.tex:94–95` | If the penalized solution still shows an instability, parameter sets on the straight line … is taken. This interpolation between parameter sets does not give a converged fit. | Delete if no reported set is interpolated. MDEA no longer is. Whether the 16-parameter calibration was interpolated was **not checked here**; keep the two sentences only if it was. |
| `sections/data_methods.tex:99–100` | For MDEA the penalty is applied to 78 \COtwo-free MDEA--water states at \SI{1.466}{\mega\pascal} and 393--\SI{423}{\kelvin}, and the reported parameters are an interpolated set. The loaded MDEA states are not penalized, so a split found there is reported as a limitation. | For MDEA, only the MDEA--water interaction acts on the \COtwo-free solution. Its linear temperature law is written about \SI{423}{\kelvin}, the highest temperature tested, which leaves the model unchanged, and its value there is bounded above at $-0.0671$, $10^{-4}$ below the value at which a liquid--liquid gap first appears in the \COtwo-free solution at \SI{1.466}{\mega\pascal}. The fitted interaction lies below that onset value at every temperature from 290 to \SI{423}{\kelvin} (Section~\ref{supp-sec:s-mdea-bound}). The loaded MDEA states are not constrained, so a split found there would be reported as a limitation. |
| `sections/data_methods.tex:101` | For AMP neither the penalty nor an interpolation is used: … | For AMP neither the penalty nor a bound of this kind is used: … (optional; unchanged meaning) |

### Results

| Location | Old | New |
|---|---|---|
| `sections/transfer_results.tex:18` | The MDEA--water interaction and its temperature coefficient are well determined, whereas the cation--water and cation--bicarbonate interactions are not distinguishable from zero, and the standard error of the cation dispersion energy exceeds half its value. | The temperature coefficient of the MDEA--water interaction is well determined, and the interaction itself is held at its bound at \SI{423}{\kelvin}; the cation--bicarbonate interaction is at its upper bound, the cation--water interaction is not distinguishable from zero, and the cation dispersion energy has a standard error of 7\,\% of its value. |
| `sections/transfer_results.tex:19` | Because the reported MDEA set is interpolated (\cref{sec:methods-phase}), these standard errors are local values and do not describe a converged estimate. | The MDEA standard errors are conditional on the two parameters on bounds. |
| `sections/transfer_results.tex:29` | For MDEA the fit without the penalty gives a calculated liquid--liquid gap in \COtwo-free MDEA--water at \SI{1.466}{\mega\pascal} above about \SI{413}{\kelvin}; no measurement of liquid--liquid coexistence in this system was used. | For MDEA the fit without the bound converges with a calculated liquid--liquid gap in \COtwo-free MDEA--water at \SI{1.466}{\mega\pascal} above about \SI{413}{\kelvin}; no measurement of liquid--liquid coexistence in this system was used. |
| `sections/transfer_results.tex:30` | Each penalized fit still leaves a detected instability at 14 of the 78 penalized states, whereas at the reported interpolated set all 78 searches finish and none detects one. | The data's optimum therefore lies inside the gap: the bound raises the fitted objective from 479.4 to 564.5, from the same initial set. At the reported parameters, all 78 searches of the \COtwo-free solution at 393--\SI{423}{\kelvin} finish and none detects an instability. |
| `sections/transfer_results.tex:31` | In the loaded solution one liquid--liquid split is found and confirmed by a two-liquid equilibrium calculation, at \SI{363.15}{\kelvin}, 78.62 wt\% MDEA and \SI{262.9}{\mega\pascal}, where no measurement exists. | In the loaded solution no liquid--liquid split is found among the searches that finish. With an earlier MDEA parameter set, a split was found at \SI{363.15}{\kelvin}, 78.62 wt\% MDEA and 1.368 mol/mol; at the reported parameters no bubble pressure can be calculated at that state, so its search does not finish and a split there is neither found nor excluded. |
| `sections/transfer_results.tex:32` | At 27 measured states … toward a vapor … | unchanged: the same 27 distinct measured-state calculations (see above) |
| `sections/transfer_results.tex:33` | Of the \num{11824} MDEA searches, 1039 did not finish, 810 of them at grid states where no bubble pressure could be calculated. | Of the \num{11824} MDEA searches, 1099 did not finish, 870 of them at grid states where no bubble pressure could be calculated. |
| `sections/transfer_results.tex:49` | …all 29 pressures are overpredicted: their bias equals their AARD, 32.2\,\% … | …all 29 pressures are overpredicted: their bias equals their AARD, 30.6\,\% … |
| `sections/transfer_results.tex:71` | …the 101 \COtwo partial pressures of Ermatchkov et al.\ over MDEA, with little bias and nearly equal values inside and above the R5 range; … | …the 101 \COtwo partial pressures of Ermatchkov et al.\ over MDEA, with nearly equal values inside and above the R5 range but biases of opposite sign; … (inside −15.8 %, above +14.3 %, overall −6.3 %) |
| `sections/transfer_results.tex:77` | …deviate by 0.1--13.6\,\%, and every fitted species ratio is overpredicted. | …deviate by 0.1--13.8\,\%, and every fitted species ratio is overpredicted. (All 16 Jakobsen ratios are still overpredicted.) |
| `sections/transfer_results.tex:85` | …one loaded-solution split is found for MDEA at a pressure far above any measurement, and none is detected for AMP at its reported parameters. | …no liquid--liquid split is found for MDEA, whose \COtwo-free solution is kept single-phase by a bound, and none is detected for AMP at its reported parameters. |
| `sections/transfer_results.tex:103` | On their 101 \COtwo partial pressures the MDEA model deviates slightly less than their set I; … | On their 101 \COtwo partial pressures the MDEA model deviates slightly more than their set I; … |
| `sections/transfer_results.tex:104` | …far closer than the MDEA model, which was not. | unchanged (28.08 % against 1.9 and 3.5 %) |

### Conclusion

| Location | Old | New |
|---|---|---|
| `sections/conclusion.tex:9` | …20.6\,\% for MDEA … those not fitted by 15.4--85.4\,\% … | …20.1\,\% for MDEA … those not fitted by 17.9--85.4\,\% … |
| `sections/conclusion.tex:14` | For MDEA a calculated liquid--liquid gap of the \COtwo-free solution, found at 14 of 78 binary states after each penalized fit, is absent at the reported parameters, which are interpolated rather than converged; one loaded-solution split remains, at \SI{262.9}{\mega\pascal}. | For MDEA the fitted data favor a calculated liquid--liquid gap of the \COtwo-free solution: a bound on the MDEA--water interaction removes it and raises the fitted objective from 479.4 to 564.5. No loaded-solution split is found among the searches that finish, but the search at the state of an earlier split does not finish. |
| `sections/conclusion.tex:18` | …the MDEA model deviates by 15.4\,\%, against 16.8\,\% for their parameter set I; … | …the MDEA model deviates by 17.9\,\%, against 16.8\,\% for their parameter set I; … |

The prose check requires `479.4` and `564.5` only in the supplement. Using them in the results and conclusion is optional.

### Supplement

| Location | Old | New |
|---|---|---|
| `supplement.tex:380` | The MDEA standard errors are local values at an interpolated parameter set. | The MDEA standard errors are conditional on the two parameters on bounds, $k_{\mathrm{MDEA,w}}$ at 423 K and $k_{\mathrm{MDEAH^+,HCO_3^-}}$; the largest conditional correlation, 0.925, is between $k_{\mathrm{MDEAH^+,w}}$ and $u_{\mathrm{MDEAH^+}}$. |
| `supplement.tex:443` | Of the 1039 MDEA searches that did not finish, 810 are at grid states where no bubble pressure could be calculated. | Of the 1099 MDEA searches that did not finish, 870 are at grid states where no bubble pressure could be calculated. |
| `supplement.tex:444` | The MDEA liquid--liquid split at 363.15 K is at 1.05 times the calculated bubble pressure and has a tangent-plane distance of $-0.00262$ in units of $RT$. | No search that finishes finds a liquid--liquid split. One of those that do not finish is at 363.15 K, 78.62 wt\% MDEA and 1.368 mol/mol, at 1.05 times the bubble pressure, where an earlier MDEA parameter set gave a split with a tangent-plane distance of $-0.00262$ in units of $RT$; at the reported parameters the bubble-pressure calculation there does not converge. |
| `supplement.tex:445` | The 27 measured MDEA states with an instability toward a vapor have an assigned pressure of 0.1733--0.9990 times the calculated bubble pressure: four densities … | The 27 measured MDEA states with an instability toward a vapor are four densities … (drop the ratio range, which was not recomputed; the breakdown by set is unchanged) |
| `supplement.tex:446` | At three of the 11 species states at 0.5 MPa … | At four of the 11 species states at 0.5 MPa … |
| `supplement.tex:457` | `\subsection{Stability penalty and interpolation between parameter sets}` | `\subsection{Stability penalty and the MDEA bound}`, with `\label{sec:s-mdea-bound}` on the MDEA paragraph or the subsection |
| `supplement.tex:463–470` | `% P:supplement-interpolation` paragraph | Delete if no reported set is interpolated (see `data_methods.tex:94–95`; the 16-parameter calibration is not checked here). |
| `supplement.tex:473` | The MEA model required neither the penalty nor the interpolation. | The MEA model required no penalty. |
| `supplement.tex:474` | …neither the penalty nor the interpolation was used. | …no penalty was used. |
| `supplement.tex:476–482` | `% P:supplement-penalty-mdea`: the 78 penalized states, the scales, $t=0.8690$ and $0.8688$, the objectives 605.01, 622.50 and 504.47, the 1041 × 32 scan, no loaded penalty | For MDEA, the MDEA--water interaction $k_{\mathrm{MDEA,w}}(T)=k_{\mathrm{MDEA,w}}(423\ \mathrm{K})+(\mathrm{d}k_{\mathrm{MDEA,w}}/\mathrm{d}T)(T-423\ \mathrm{K})$ is the only fitted parameter that acts on the \COtwo-free solution. With all other parameters fixed, the largest value without a gap in the lower convex envelope of the liquid Gibbs energy over 5490 compositions at 1.466 MPa rises from $-0.1323$ at 290 K to $-0.0670$ at 423 K, and $k_{\mathrm{MDEA,w}}(423\ \mathrm{K})$ is bounded above at $-0.0671$, $10^{-4}$ below it. Of three initial parameter sets, two converge to the same solution, with an objective value on the fitted data of 564.5, and the third to 582.8; at the reported solution the bound and the upper bound of $k_{\mathrm{MDEAH^+,HCO_3^-}}$ are active. Without the bound, the fit from one of these initial sets converges at 479.4, with an instability at 14 of 78 \COtwo-free MDEA--water liquids at 1.466 MPa (393, 403, 413, 413.15, 422.04 and 423 K, each at MDEA mole fractions of 0.01, 0.02, 0.04, 0.06, 0.07, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20 and 0.24). At the reported parameters all 78 searches finish without a detected instability, a scan of the liquid Gibbs energy over 1041 compositions at each of 32 temperatures up to 422.04 K shows no gap, and the fitted interaction lies below the onset value at each of 33 temperatures from 290 to 423 K. No bound acts on the loaded MDEA states. |
| `supplement.tex:486` | For AMP neither the penalty nor an interpolation is used. | For AMP neither the penalty nor a bound of this kind is used. (optional) |
| `supplement.tex:519` | …the MDEA model deviates by 20.59\,\% … | …the MDEA model deviates by 20.09\,\% … |

### Other places

- **Tables and figure, regenerated, not committed:** `transfer-fitted`, `amine-summary`, `published-models`, `supplement-transfer-data`, `supplement-mdea-ranges`, `supplement-transfer-bounds`, `supplement-transfer-parameters`, `transfer-species`, `number-sources.json` and `mdea-current-measured-model.pdf`.
- **Equation text, unchanged:** `sections/epc_saft_equation_of_state.tex:41` writes $k_{ij}(T)=k_{ij}(T_{\mathrm{ref}})+(\mathrm{d}k_{ij}/\mathrm{d}T)(T-T_{\mathrm{ref}})$ without fixing $T_{\mathrm{ref}}$. The Writer may add "with $T_{\mathrm{ref}}=423$ K".
- **Nomenclature, unchanged:** `sections/nomenclature.tex:45` (penalty symbols) is still used by the 16-parameter calibration.

## Not verified

- Whether the 16-parameter calibration's reported set was interpolated. This decides whether the interpolation text can be deleted.
- A second initial set for the fit without the bound. The cost of the constraint, 85.0, is local.
- The isotherm and pressure-closure checks of the 27 vapor-directed states, and their bubble-pressure ratio range.
- Whether a split exists at the undecided state at 363.15 K.
