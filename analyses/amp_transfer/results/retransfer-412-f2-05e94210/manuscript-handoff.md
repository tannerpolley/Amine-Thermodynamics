# AMP manuscript handoff for issue 412

## Basis

**Owner decision (2026-11-23), recorded on #412.** The AMP result is now the split-free fit, with the AMPH⁺–water reciprocal-temperature slope fixed at −150 K. The fit with that slope free is the comparison. The paper mentions its splits above 353 K in one sentence. The interpolated stability-constrained alternative is withdrawn.

Every AMP fit here uses the carbamate inputs of the adopted MEA model (F2): carbamate dispersion energy 179.85787428794876 K and carbamate–water $k_{ij}$ −0.06612124724836234. The 16-parameter calibration (F0) values are no longer used.

Locations refer to the merged tree `2bc1298c9` (`origin/main` at `18e8ea642`, after #413), relative to `docs/scientific/latex` unless a path says otherwise. Every cited line was checked against that tree. Evidence paths are relative to this folder. The current manuscript carries the #404 values.

**The −150 K value is a choice.** It comes from a scan of fixed slopes on F2 and is not from a source:

- At −150 K, no instability was detected.
- −125 K was also screened without an instability, with the quick native search only.
- At −175 K, 5 grid instabilities remain.
- Nothing was run at −160 K, and nothing between −100 and −125 K on F2.
- Only −150 K had the full search with the 7301-trial bank.

The fitted value in the free fit is −219.25 K with a conditional SE of 80.99 K. −150 K lies 0.86 SE from it, and fixing it raises the cost by 0.78, from 61.2853 to 62.0651. The data do not distinguish the two slopes. The standard errors of the split-free fit are conditional on the fixed slope.

## Cause of the splits, for the results and supplement text

All values below are on F2 unless the text says otherwise.

- **Temperature range of the data.** Every fitted CO₂-loaded row lies at 313–353 K.
- **The extrapolated interaction.** With the slope fitted at −219.25 K, $k_{\mathrm{AMPH^+,w}}$ rises from −0.178 at 353 K to −0.115 at 393 K. The weaker cation–water attraction gives a second liquid rich in AMPH⁺, HCO₃⁻ and AMP, with carbamate at 10⁻⁴–10⁻³ mole fraction.
- **The slope is a sufficient cause, not the only one.** Each of two changes above 353.22 K removes every instability on its own: holding $k_{\mathrm{AMPH^+,w}}$ at its 353.22 K value, or holding the AMP dissociation law at its 353.22 K value. Continuing that law at constant enthalpy, which lowers ln K by 0.04 at 393 K, also removes them all.
- **The splits are marginal.** The smallest τ is about −0.006.
- **What does not matter.** Holding R4 at its 353.22 K value, or putting the carbamate diameter at its floor, leaves 93 and 90 of the 93 instabilities.
- **Scan below −150 K, old base only.** Slopes of 0, −50 and −100 K were scanned on the old F0 base only. They move the instabilities to 298–323 K, onto 57, 57 and 48 of the 57 fitted Ciftja NMR states.

Evidence: [probes, old base](diagnosis/f0-probes.json), [probes, F2](diagnosis/f2-probes.json), [scan with measured instabilities by set, old base](diagnosis/f0-scan.json), [scan, F2](diagnosis/f2-scan.json).

## Results that change

| Quantity | #404 main (in the paper) | Free fit, F2 (comparison) | **AMP model, slope −150 K** |
|---|---:|---:|---:|
| Objective | 61.4227 | 61.2853 | **62.0651** |
| Fitted coordinates | 9 | 9 | **8** (slope fixed) |
| Active bounds | 1 | 2 | **2** |
| Loaded fitted pressure AARD, 47 | 10.35 % | 10.34 % | **10.49 %** |
| All fitted pressures, 73 | 7.07 % | 7.06 % | **7.12 %** |
| Pressures not fitted, 114 | 34.22 % | 34.12 % | **35.50 %** |
| Instabilities / confirmed splits, 666 searches | 92 / 73 | 93 / 73 | **0 / 0** |

**The split-free fit.** The fit was warm-started from the F2 free fit and also started from declared start 1. Both endpoints reach 62.0651106 and are retained as [parameters](slope-150/parameters.json) and [start-1 endpoint](slope-150/start-1-parameters.json). The full 666-state search with the 7301-trial bank completes every state with 0 instabilities, including all 270 measured states. The smallest supplied-trial TPD is +1.66 × 10⁻⁴ ([confirmation](slope-150/confirmation.json)). The carbamate diameter is at its 6.5 Å upper bound, and the R4 enthalpy increment is at its lower bound. Further evidence: [uncertainty](slope-150/conditional-uncertainty.json), [group costs](slope-150/group-costs.json).

**The free fit (comparison).** Both declared starts converge to 61.2853 and agree to 7 × 10⁻¹². Start 1 is selected. Of 93 instabilities, 73 are confirmed and 20 unresolved. Confirmed splits lie at 26.8–30.0 wt%, 363.15–393.20 K and 0.400–0.966 mol/mol. The largest decrease is 0.01881 mol (numerical estimate 2.8 × 10⁻⁹), at 393.15 K, 30.0 wt%, 0.700 mol/mol and 1.212 MPa, with densities 44,899 and 31,612 mol/m³.

At measured states of the selected start ([measured states](main/measured-states.json)), all at 373–393 K and all comparison rows:

- **Confirmed splits (6):** Hartono et al. 2021 supplemental rows 9, 10 and 11 at 373 K; Tong et al. rows 10 and 13 at 373.2 K; Tong row 12 at 393.2 K.
- **Unconfirmed instabilities (8):** Hartono rows 7 and 8 at 373 K and rows 6 and 7 at 393 K; Tong rows 8, 9, 11 and 12 at 373.2 K.

Start 0 also confirms Tong row 9 at 373.2 K, which makes 7 confirmed. Use start 1. On `main`, the supplement places the three confirmed Hartono splits at “373–393 K”. On F2 all three are at 373 K.

## Tables

### Table 6, `tables/transfer-species.tex`

| Cell | Old | New |
|---|---:|---:|
| AMPH⁺ segment and Born diameters (Å) | 5.7699 | 6.4694 |
| AMPCOO⁻ segment and Born diameters (Å) | 6.4705 | 6.5000 (upper bound) |
| AMPCOO⁻ dispersion energy / k (K) | 183.0006 | 179.8579 |

Footnote g: “Dispersion energy of MEACOO⁻ in the 16-parameter calibration” → “Dispersion energy of MEACOO⁻ in the MEA model”.

### Table 7, `tables/transfer-fitted.tex`

Remove the alternative column. The caption becomes “Fitted parameters of the DEA, MDEA and AMP models with conditional standard errors”. The AMP rows become:

| Coordinate | Old value (SE) | New value (SE) |
|---|---:|---:|
| $k_{\mathrm{AMP,w}}$ at 313.15 K | −0.1301 (0.0062) | −0.1261 (0.0055) |
| $b_{\mathrm{AMP,w}}$ (K) | −54.316 (16.343) | −42.381 (14.861) |
| $k_{\mathrm{AMPH^+,w}}$ at 313.15 K | −0.2561 (0.0232) | −0.2475 (0.0083) |
| $b_{\mathrm{AMPH^+,w}}$ (K) | −214.681 (87.987) | **−150, fixed** (—) |
| $k_{\mathrm{AMPH^+,CO_2}}$ | 0.7565 (0.0760) | 0.7821 (0.0680) |
| $\sigma_{\mathrm{AMPH^+}}$ (Å) | 5.7699 (0.7145) | 6.4694 (0.3221) |
| $\sigma_{\mathrm{AMPCOO^-}}$ (Å) | 6.4705 (1.6648) | 6.5000, upper bound (—) |
| R4 $A_4$ | 11.5617 (4.5702) | 10.8679 (0.2654) |
| R4 $\delta h$ (J/mol) | −5000.0, lower bound | −5000.0, lower bound |

Note text: replace “AMP: the values are those of the fit without the stability penalty … The stability-constrained alternative … has no standard errors” with the following. AMP: $b_{\mathrm{AMPH^+,w}}$ is fixed at a value chosen from a scan (Section S…), and the standard errors are conditional on it. $\delta h$ is relative to the initial R4 correlation.

### Table 8, `tables/amine-summary.tex`

- AMP row → `AMP & 8 & 2 & $10.49$ (47) & $7.12$ (73) & $35.50$ (114) & 666 & 0 & 0`.
- Delete the alternative row and “and of the stability-constrained alternative for AMP” in the caption.
- In the note, drop “the values of the alternative in the last two pressure columns …”.

### Table S5, `tables/supplement-transfer-parameters.tex`

Delete the block “AMP: fitted values of the stability-constrained alternative”. In the AMP blocks:

| Key | Old | New |
|---|---:|---:|
| AMPH⁺ Born, Debye–Hückel and segment diameters | 5.769915428775273 | 6.4693623248364664 |
| AMPH⁺ packing diameter | 5.07752557732224 | 5.6930388458560905 |
| AMPCOO⁻ Born, Debye–Hückel and segment diameters | 6.4704647197605425 | 6.5 |
| AMPCOO⁻ packing diameter | 5.694008953389277 | 5.72 |
| AMPCOO⁻ dispersion energy (K) | 183.00063128808972 | 179.85787428794876 |
| AMPCOO⁻–H₂O $k_{ij}$ | −0.013004788810687472 | −0.06612124724836234 |
| CO₂–AMPH⁺ $k_{ij}$ | 0.75651013952477 | 0.7820806483424216 |
| AMP–H₂O $k_{ij}$ | −0.13010976132052726 | −0.12612425937544733 |
| AMP–H₂O slope (K) | −54.3159071695958 | −42.38099210214674 |
| AMPH⁺–H₂O $k_{ij}$ | −0.25613191165718885 | −0.2474860342099225 |
| AMPH⁺–H₂O slope (K) | −214.6805119041768, “This work” | −150, “Set in this work (scan)”, not bold |
| R4 $a$ | 11.5616747761141 | 10.867934092746673 |
| R4 $b$ (K) | −1944.8382247863697 | unchanged |

Source column of both AMPCOO⁻ fixed inputs: “MEACOO⁻, 16-parameter calibration” → “MEACOO⁻, MEA model”.

### Table S9, `tables/supplement-transfer-data.tex`

AMP rows, from [same-row deviations](same-row-deviations.csv), case “Slope -150 K against #404 main”:

| Set | Rows | AARD, #404 → new | Signed bias, #404 → new |
|---|---:|---:|---:|
| Hartono binary bubble pressure | 26 | 1.14 → 1.03 | 1.10 → 1.03 |
| Hartono binary vapor AMP mole fraction | 26 | 3.71 → 5.90 | 2.03 → 1.46 |
| Supplemental Hartono total pressure | 18 | 28.12 → 28.35 | −28.12 → −28.35 |
| Kundu CO₂ partial pressure | 51 | 44.06 → 47.02 | 38.09 → 39.54 |
| Fitted Hartono total pressure | 47 | 10.35 → 10.49 | −1.22 → −1.56 |
| Ciftja carbamate fraction per analytical AMP | 57 | 26.23 → 23.82 | 2.92 → 2.45 |
| Loaded Tong total pressure | 40 | 28.23 → 27.98 | −12.12 → −12.54 |
| CO₂-free Tong bubble pressure | 5 | 3.67 → 3.98 | 2.48 → 2.48 |

### Table S20, `tables/supplement-amp-ranges.tex`

| Set | Range | Calculated / defined | AARD (%), #404 → new |
|---|---|---:|---:|
| Supplemental Hartono total pressure | R5 outside | 18/18 | 28.12 → 28.35 |
| Supplemental Hartono total pressure | R4 inside | 11/11 | 26.41 → 26.52 |
| Supplemental Hartono total pressure | R4 outside | 7/7 | 30.82 → 31.23 |
| Kundu CO₂ partial pressure | R5 inside | 51/51 | 44.06 → 47.02 |
| Kundu CO₂ partial pressure | R4 inside | 11/11 | 17.93 → 20.07 |
| Kundu CO₂ partial pressure | R4 outside | 40/40 | 51.24 → 54.43 |
| Fitted Hartono total pressure | R5 inside | 47/47 | 10.35 → 10.49 |
| Fitted Hartono total pressure | R4 inside | 32/32 | 11.14 → 11.46 |
| Fitted Hartono total pressure | R4 outside | 15/15 | 8.67 → 8.42 |
| Ciftja carbamate fraction | R5 inside | 57/57 | 26.23 → 23.82 |
| Ciftja carbamate fraction | R4 inside | 16/16 | 26.16 → 25.16 |
| Ciftja carbamate fraction | R4 outside | 41/41 | 26.25 → 23.29 |
| Loaded Tong total pressure | R5 and R4 inside | 17/17 | 29.33 → 28.56 |
| Loaded Tong total pressure | R5 and R4 outside | 23/23 | 27.42 → 27.55 |

## Figures

- **`figures/generated/amp-current-measured-model.pdf`, Figure 10.** Replot from [curve data](slope-150/curve-data.json) and [data rows](slope-150/data-rows.json). The curve identities, stocks, temperatures and range marks are unchanged.
- **`figures/generated/amp-splits.pdf`, Figure 7.** It shows the AMP model's splits, and the AMP model now has none. With a one-sentence mention of the free fit, the figure and its reference at `sections/transfer_results.tex:38` would be removed. That is a Writer and owner choice. If it is kept, replot it from `main/phase-classification-1.json.gz`, captioned as the free fit with 73 confirmed and 20 unresolved.

## Prose, by location on the merged tree

| Location | Old | New |
|---|---|---|
| `main.tex:92` | AMP needs nine more parameters | Eight are fitted, and the AMPH⁺–water temperature coefficient is set from a scan. Same change at `sections/data_methods.tex:35`, `sections/conclusion.tex:8`, `submission_metadata.yml:7`, `submission/cover_letter.md:10` and `submission/graphical_abstract.tex:20` (“9 more parameters”). |
| `main.tex:95` | 10.4 % (AMP) | 10.5 % (AMP). The DEA end belongs to #413. |
| `main.tex:97` | “The AMP model has at least 73 calculated splits …; an alternative set with none detected deviates by 20.2 % …” | With the AMPH⁺–water temperature coefficient fixed at a value chosen from a scan, no instability is detected for AMP. A fit of that coefficient as well has calculated splits above 353 K at a similar deviation. |
| `sections/introduction.tex:38` | “at least 73 splits for AMP, all above …” | None for AMP once its cation–water temperature coefficient is fixed at a scanned value. Keep the free-fit splits only in the results sentence below. |
| `sections/data_methods.tex:35` | nine AMP parameters | Eight, with $b_{\mathrm{AMPH^+,w}}$ fixed at −150 K, a value chosen from a scan of fixed values (Section S…). |
| `sections/data_methods.tex:101` | AMP model is the fit without the penalty, with the interpolated alternative beside it | The AMP model refits the other eight parameters with $b_{\mathrm{AMPH^+,w}}$ fixed at −150 K. No penalty or interpolation is used for AMP. Line 98 stands. Keep the interpolation sentence for MDEA only. |
| `sections/transfer_results.tex:20` | One of nine on a bound; diameter 6.47 Å (SE 1.66 Å); alternative 5.98 Å | Two of the eight fitted AMP parameters are on bounds: the R4 enthalpy increment at its lower and the carbamate diameter at its upper bound, 6.5 Å. The standard errors are conditional on the fixed slope. |
| `sections/transfer_results.tex:36–41` | 92 instabilities, 73 confirmed, measured-state splits, “do not identify which model quantity …”, the penalty and alternative sentences | All 666 AMP searches finish without a detected instability, also with the 7301 trial compositions of earlier searches. **The one free-fit sentence:** fitted as well, the slope (−219 K, SE 81 K) gives at least 73 confirmed splits at 363.15–393.20 K, above the 353 K of the fitted loaded pressures, where the extrapolated cation–water interaction weakens. The cause detail belongs in the supplement (above). |
| `sections/transfer_results.tex:69`, Figure 10 caption | “the AMP model (lines)” | Unchanged wording; the model is now the fixed-slope fit. |
| `sections/transfer_results.tex:76` | The alternative versus the model, for Tong, Kundu and Hartono 373–393 K | Delete. There is no alternative. |
| `sections/transfer_results.tex:84` | Carbamate fraction deviates more than fitted pressures, small bias | Holds: 23.82 % AARD, +2.45 % bias. |
| `sections/transfer_results.tex:90` | “at least 73 splits are confirmed for AMP” | No instability is detected for AMP at the reported set. The free fit's splits are in Section 4.x. |
| `sections/transfer_results.tex:91` | DEA→MDEA→AMP closer as splits increase | Revise: AMP now has none, so the ordering no longer follows the split count. |
| `sections/transfer_results.tex:92` | “Within AMP the trade-off is real … 20.2 % against 10.4 %” | Within AMP the fitted loaded pressures deviate by 10.5 % at the fixed slope and 10.3 % with it fitted. Do not generalize. At −175 K 5 instabilities remain, and on the old base 0 to −100 K put instabilities on the fitted NMR states. |
| `sections/conclusion.tex:9` | 10.4 % for AMP | 10.5 %. The not-fitted range, 15.4–85.4 % after #413, still holds with the new AMP sets. |
| `sections/conclusion.tex:15–16` | 73 splits; alternative 20.2 %; “None of the fits made here gives …” | With the cation–water temperature coefficient fixed at a scanned value, the AMP model has no detected instability at 10.5 %, and fitting that coefficient brings splits above 353 K. **Delete** “None of the fits made here gives …”. |
| `submission/highlights.txt:3` | 10.4–28.5 % | 10.5–28.5 %, subject to #413 for DEA. |
| `submission/highlights.txt:4` | “at least 73 for AMP” | None for AMP at the reported parameters. |
| `submission_metadata.yml:10` | 10.4% (AMP) | 10.5% (AMP) |
| `submission_metadata.yml:12` | “The AMP model has at least 73 … alternative … 20.2%” | Same replacement as `main.tex:97`. |
| `submission_metadata.yml:79` | `analyses/amp_transfer/results/retransfer-404-05e94210/main/parameters.json` | `analyses/amp_transfer/results/retransfer-412-f2-05e94210/slope-150/parameters.json` |
| `submission_metadata.yml:80` | `af8e6b93…0c17a` | `5c0bf32b4945d3cfdfd9bdc713799b0956adc296bbd17ba3f2450e1433bc6006` |
| `submission_metadata.yml:83` | stability-constrained AMP alternative, `retransfer-404-05e94210/penalty-0/` | AMP fit with the AMPH⁺–water slope also fitted (`analyses/amp_transfer/results/retransfer-412-f2-05e94210/main/`) |
| `submission_metadata.yml:60`, `:82` | Name F0 only as the MEA comparison fit | **Unchanged.** |
| `submission/cover_letter.md:10` | 10.4 % (AMP); nine more parameters | 10.5 % (AMP); eight fitted and one set from a scan |
| `submission/cover_letter.md:11` | “at least 73 calculated splits for AMP. An alternative AMP parameter set with none detected deviates by 20.2 % …” | No instability is detected for AMP once its cation–water temperature coefficient is fixed at a scanned value. With that coefficient also fitted, AMP has splits above the measured temperature range at a similar deviation. Revise the last sentence (“what avoiding it costs”) accordingly. |
| `submission/graphical_abstract.tex:20` | 9 more parameters; 10.4 %; At least 73 splits; Alternative 20.2 % | 8 more parameters; 10.5 %; No instability detected |
| `supplement.tex:206` | 183.0006 K and −0.0130 from the 16-parameter calibration, SE 0.1444 | 179.8579 K and −0.0661, those of MEACOO⁻ in the MEA model, where the interaction has a conditional SE of 0.5092 and the energy one of 59.45 K |
| `supplement.tex:379` | Diameter free, correlation 0.998, SEs 4.57 and 1.66 Å | The carbamate diameter is on its upper bound and has no standard error. $A_4$ has a conditional SE of 0.265. All AMP standard errors are conditional on the fixed $b_{\mathrm{AMPH^+,w}}$. |
| `supplement.tex:380` | “the stability-constrained AMP alternative has none” | Delete that clause. |
| `supplement.tex:404–406` | Alternative inside/outside R4 (19.92 / 20.81, 21.47 / 28.87, 31.30 / 112.57, 53.66 / 24.70) and R5 (20.20, 95.04, 24.35 %) | Delete the paragraph, since there is no alternative. |
| `supplement.tex:451–457` | AMP search with 92 instabilities, 73 confirmed, measured-state counts and largest decrease | The 270 measured and 396 grid states are searched with 0 instabilities, also with the 7301-trial bank; smallest supplied-trial TPD +1.66 × 10⁻⁴. If the free fit is described beyond the main-text sentence, use the free-fit paragraph above, with the source rows as listed. |
| `supplement.tex:485–495`, the AMP penalty and interpolation paragraph | Two starts at 61.4227, the 3.5 Å sensitivity, anchor, penalty stages, bisection, $t$ = 0.558556, cost 126.86 and contribution 58.89 → 123.61 | Replace it with the fixed-slope fit. The fit was warm-started from the free fit and also started from declared start 1, and both reach 62.0651. It refits the eight other parameters. The slope value is a choice from the scan (see Basis), 0.86 SE from the fitted −219 K, at a cost 0.78 higher. The contribution of the fitted loaded pressures is 59.70, against 58.89 for the free fit. The cause paragraph above goes here. The 3.5 Å sensitivity was not rerun on F2, and with the diameter at its upper bound it does not apply. |

The DEA carbamate text (`supplement.tex:204`, Table 6 footnote b) belongs to #413.

## `scripts/dea_displays.py`: AMP part done (#412)

The script now reads `slope-150/` as the AMP model and `main/` (selected start 1) as the free-fit comparison: its splits figure, classification and slope. The reads of the #404 penalty, alternative, sensitivity and check files are gone. The AMP carbamate inputs are asserted against F2 and labelled “MEACOO⁻, MEA model”. The fixed slope is not bold, carries footnote b in Table 7, and is sourced “Set in this work (scan)” in S5.

The prose check now runs after the displays are written or compared and lists every missing value instead of stopping at the first one. Running the script without `--check` therefore regenerates the displays before the prose is revised.

**Regenerated displays are left uncommitted.** They show the new AMP model while the prose still has the #404 numbers. To regenerate them, run `.venv/bin/python docs/scientific/latex/scripts/dea_displays.py` from the repository root. That writes Tables 6–8 (`transfer-species`, `transfer-fitted`, `amine-summary`), `supplement-transfer-bounds`, `supplement-transfer-data`, `supplement-transfer-parameters`, `supplement-amp-ranges`, `number-sources.json`, `amp-current-measured-model.pdf` and `amp-splits.pdf`, the latter still drawn from the free fit's 93 states.

**Prose contract.** With the regenerated displays, `--check` passes all 18 displays and 49 source files. It then fails only on these 19 AMP prose fragments, each of which must appear verbatim in its file:

| File | Fragment |
|---|---|
| `main.tex` | `10.5` |
| `sections/conclusion.tex` | `10.5` |
| `submission/highlights.txt` | `10.5–28.5%` |
| `sections/transfer_results.tex` | `Two of the eight fitted AMP parameters` |
| `sections/transfer_results.tex` | `\SI{6.5}{\angstrom}` |
| `sections/transfer_results.tex` | `7301 trial compositions` |
| `sections/transfer_results.tex` | `at least 73 confirmed splits` |
| `sections/transfer_results.tex` | `10.5\,\%` and `10.3\,\%` (two fragments) |
| `supplement.tex` | `\SI{179.8579}{\kelvin}, and its interaction with water, $-0.0661$` |
| `supplement.tex` | `0.5092` (MEA SE of that interaction) |
| `supplement.tex` | `0.265` ($A_4$ SE) |
| `supplement.tex` | `62.0651` (objective of both starts) |
| `supplement.tex` | `0.78` (cost rise at the fixed slope) |
| `supplement.tex` | `59.70` (loaded-pressure contribution) |
| `supplement.tex` | `1.66\times10^{-4}` (smallest supplied-trial TPD) |
| `supplement.tex` | `-0.178` and `-0.115` ($k_{\mathrm{AMPH^+,w}}$ of the free fit at 353 and 393 K) |
| `supplement.tex` | `57, 57 and 48` (Ciftja states, old-base scan) |

Four more checked fragments already pass on today's text, so they are not proof that the revision is complete. Include them anyway:

- `0.86` (SE distance of the slope) and `58.89` (free-fit loaded contribution) occur elsewhere or in the old paragraph.
- `\SI{5.3480}{\angstrom}, as its lower bound` and the DEA/MEA values are unchanged.

The free-fit measured-state sentence (six confirmed, eight unconfirmed) is no longer checked, because the decision keeps the free fit to one sentence. If the Writer keeps it in the supplement, use the source rows above.
