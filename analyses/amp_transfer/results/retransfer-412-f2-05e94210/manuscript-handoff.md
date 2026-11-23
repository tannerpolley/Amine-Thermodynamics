# AMP manuscript handoff for issue 412

Candidate. Apply only after the owner adopts it. This list compares the active manuscript, which carries the #404 AMP values (commit `ff10e7cae`), with the #412 results. Locations are relative to `docs/scientific/latex`. Evidence paths are relative to this folder.

The handoff has two parts.

- **Part A** applies the owner's change of base (2026-11-23). The AMP carbamate dispersion energy and carbamate–water $k_{ij}$ now come from the 11-parameter MEA model (F2), not the 16-parameter calibration (F0). The main AMP fit is refitted with only these two inputs changed: same data, two starts, 7301-trial bank and 666-state search.
- **Part B** applies only if the owner also adopts the split-free set. That set has the AMPH⁺–water reciprocal-temperature slope fixed at −150 K. It replaces the interpolated stability-constrained alternative.

The #404 interpolated alternative was fitted on F0 and was not repeated on F2. If the owner keeps an interpolated alternative instead of Part B, it must first be rerun on F2. Its numbers below cannot simply be carried over.

## Part A: F2 main fit

Sources: [fit summary](main/fit-summary.json), [uncertainty](main/conditional-uncertainty.json), [parameters](main/parameters.json), [classification of the selected start 1](main/phase-classification-1.json.gz), [same-row deviations](same-row-deviations.csv) (case "F2 main against #404 main"), [source rows](source.json).

### Table 6, `tables/transfer-species.tex`

| Cell | Old (#404) | New (F2) |
|---|---:|---:|
| AMPH⁺ segment and Born diameters (Å) | 5.7699 | 5.7361 |
| AMPCOO⁻ segment and Born diameters (Å) | 6.4705 | 6.5000 (upper bound) |
| AMPCOO⁻ dispersion energy / k (K) | 183.0006 | 179.8579 |

Footnote g, “Dispersion energy of MEACOO⁻ in the 16-parameter calibration” → “Dispersion energy of MEACOO⁻ in the MEA model”. The rest of footnote g stands. Footnote b (DEA) is owned by the DEA issue.

### Table 7, `tables/transfer-fitted.tex`, AMP main column

| Coordinate | Value, #404 → F2 | Conditional SE, #404 → F2 |
|---|---:|---:|
| $k_{\mathrm{AMP,w}}$ at 313.15 K | −0.1301 → −0.1304 | 0.0062 → 0.0061 |
| $b_{\mathrm{AMP,w}}$ (K) | −54.316 → −55.119 | 16.343 → 16.177 |
| $k_{\mathrm{AMPH^+,w}}$ at 313.15 K | −0.2561 → −0.2573 | 0.0232 → 0.0222 |
| $b_{\mathrm{AMPH^+,w}}$ (K) | −214.681 → −219.251 | 87.987 → 80.991 |
| $k_{\mathrm{AMPH^+,CO_2}}$ | 0.7565 → 0.7550 | 0.0760 → 0.0763 |
| $\sigma_{\mathrm{AMPH^+}}$ (Å) | 5.7699 → 5.7361 | 0.7145 → 0.6122 |
| $\sigma_{\mathrm{AMPCOO^-}}$ (Å) | 6.4705 → **6.5000, upper bound** | 1.6648 → — |
| R4 constant $A_4$ | 11.5617 → 10.8085 | 4.5702 → 0.2452 |
| R4 $\delta h$ (J/mol) | −5000.0 (lower bound) → unchanged | — |

Mark the carbamate diameter as on a bound (superscript a).

### Table 8, `tables/amine-summary.tex`, AMP row

| Column | #404 | F2 |
|---|---:|---:|
| Active bounds | 1 | **2** |
| Loaded fitted pressure AARD (47) | 10.35 | 10.34 |
| All fitted pressure AARD (73) | 7.07 | 7.06 |
| Pressures not fitted AARD (114) | 34.22 | 34.12 |
| Searches completed | 666 | 666 |
| Unavailable | 0 | 0 |
| Confirmed splits | 73 | 73 |

### Table S5, `tables/supplement-transfer-parameters.tex`, AMP main block

| Key | Old | New |
|---|---:|---:|
| AMPH⁺ Born, Debye–Hückel and segment diameters | 5.769915428775273 | 5.736068960640369 |
| AMPH⁺ packing diameter | 5.07752557732224 | 5.047740685363525 |
| AMPCOO⁻ Born, Debye–Hückel and segment diameters | 6.4704647197605425 | 6.5 |
| AMPCOO⁻ packing diameter | 5.694008953389277 | 5.72 |
| AMPCOO⁻ dispersion energy (K) | 183.00063128808972 | 179.85787428794876 |
| AMPCOO⁻–H₂O $k_{ij}$ | −0.013004788810687472 | −0.06612124724836234 |
| CO₂–AMPH⁺ $k_{ij}$ | 0.75651013952477 | 0.7549810401144406 |
| AMP–H₂O $k_{ij}$ | −0.13010976132052726 | −0.13039635079612888 |
| AMP–H₂O slope (K) | −54.3159071695958 | −55.11900273267515 |
| AMPH⁺–H₂O $k_{ij}$ | −0.25613191165718885 | −0.2573330168187741 |
| AMPH⁺–H₂O slope (K) | −214.6805119041768 | −219.25134753987498 |
| R4 $a$ | 11.5616747761141 | 10.80848786427155 |
| R4 $b$ (K) | −1944.8382247863697 | unchanged |

In the Source column of both AMPCOO⁻ fixed inputs, “MEACOO⁻, 16-parameter calibration” → “MEACOO⁻, MEA model”.

### Tables S9 and S20, and the alternative sentences after S20

Generated from the same-row CSVs. The alternative columns apply only with Part B.

| Set | Rows | Main AARD, #404 → F2 | Main bias, #404 → F2 | Alternative AARD, #404 interpolated → fixed slope | Alternative bias |
|---|---:|---:|---:|---:|---:|
| Hartono binary bubble pressure | 26 | 1.14 → 1.14 | 1.10 → 1.10 | 1.08 → 1.03 | 1.05 → 1.03 |
| Hartono binary vapor AMP mole fraction | 26 | 3.71 → 3.69 | 2.03 → 2.03 | 3.77 → 5.90 | 1.49 → 1.46 |
| Supplemental Hartono total pressure | 18 | 28.12 → 28.10 | −28.12 → −28.10 | 24.35 → 28.35 | −24.35 → −28.35 |
| Kundu CO₂ partial pressure | 51 | 44.06 → 43.91 | 38.09 → 38.01 | 95.04 → 47.02 | 93.76 → 39.54 |
| Fitted Hartono total pressure | 47 | 10.35 → 10.34 | −1.22 → −1.21 | 20.20 → 10.49 | 14.12 → −1.56 |
| Ciftja carbamate fraction per analytical AMP | 57 | 26.23 → 25.55 | 2.92 → 3.70 | 29.88 → 23.82 | 21.19 → 2.45 |
| Loaded Tong total pressure | 40 | 28.23 → 28.16 | −12.12 → −12.16 | 37.01 → 27.98 | 4.05 → −12.54 |
| CO₂-free Tong bubble pressure | 5 | 3.67 → 3.65 | 2.48 → 2.47 | 3.74 → 3.98 | 2.46 → 2.48 |

| Point | Set | Range | Calculated / defined | AARD (%) |
|---|---|---|---:|---:|
| Main | Supplemental Hartono total pressure | R5 outside | 18/18 | 28.12 → 28.10 |
| Main | Supplemental Hartono total pressure | R4 inside / outside | 11/11, 7/7 | 26.41 → 26.39; 30.82 → 30.79 |
| Main | Kundu CO₂ partial pressure | R5 inside | 51/51 | 44.06 → 43.91 |
| Main | Kundu CO₂ partial pressure | R4 inside / outside | 11/11, 40/40 | 17.93 → 17.85; 51.24 → 51.08 |
| Main | Fitted Hartono total pressure | R5 inside | 47/47 | 10.35 → 10.34 |
| Main | Fitted Hartono total pressure | R4 inside / outside | 32/32, 15/15 | 11.14 → 11.12; 8.67 → 8.67 |
| Main | Ciftja carbamate fraction | R5 inside | 57/57 | 26.23 → 25.55 |
| Main | Ciftja carbamate fraction | R4 inside / outside | 16/16, 41/41 | 26.16 → 24.01; 26.25 → 26.15 |
| Main | Loaded Tong total pressure | R5 and R4, inside / outside | 17/17, 23/23 | 29.33 → 29.19; 27.42 → 27.40 |
| Alternative | Supplemental Hartono total pressure | R5 outside | 18/18 | 24.35 → 28.35 |
| Alternative | Supplemental Hartono total pressure | R4 inside / outside | 11/11, 7/7 | 21.47 → 26.52; 28.87 → 31.23 |
| Alternative | Kundu CO₂ partial pressure | R5 inside | 51/51 | 95.04 → 47.02 |
| Alternative | Kundu CO₂ partial pressure | R4 inside / outside | 11/11, 40/40 | 31.30 → 20.07; 112.57 → 54.43 |
| Alternative | Fitted Hartono total pressure | R5 inside | 47/47 | 20.20 → 10.49 |
| Alternative | Fitted Hartono total pressure | R4 inside / outside | 32/32, 15/15 | 19.92 → 11.46; 20.81 → 8.42 |
| Alternative | Loaded Tong total pressure | R5 and R4, inside / outside | 17/17, 23/23 | 53.66 → 28.56; 24.70 → 27.55 |

### Part A prose

| Location | Old | New |
|---|---|---|
| `main.tex` abstract, loaded-pressure sentence | 10.4 % (AMP) to 28.5 % (DEA) | 10.3 % (AMP). The DEA bound belongs to the DEA refit. |
| `sections/conclusion.tex` l. 9 | 10.4 % for AMP | 10.3 % |
| `submission/highlights.txt` l. 3 | 10.4–28.5 % | 10.3–28.5 %, subject to DEA |
| `sections/transfer_results.tex` l. 91 | 20.2 % against 10.4 % | Part B replaces the whole sentence. Without Part B, the 10.4 becomes 10.3, but the 20.2 is an F0 number that cannot stand on the F2 base. |
| `sections/transfer_results.tex` l. 20 | One of nine on a bound, carbamate diameter 6.47 Å (SE 1.66 Å) inside its bounds | Two of nine are on bounds: the R4 enthalpy increment at its lower bound and the carbamate diameter at its upper bound, 6.5 Å. |
| `sections/transfer_results.tex` l. 36–38 and Figure 7 caption | 92 detected instabilities, 73 confirmed, 19 not two distinct liquids | 93 detected, 73 confirmed, 20 unresolved. The range 363.15–393.20 K is unchanged. |
| `figures/generated/amp-splits.pdf` | #404 locations | Replot from `main/phase-classification-1.json.gz`, the selected start. |
| `sections/transfer_results.tex` l. 83 and Figure 10 | Carbamate fraction larger than fitted pressures, small bias | The statement still holds: 25.55 % AARD, +3.70 % bias. Replot Figure 10 from `main/curve-data.json`. |
| `supplement.tex` l. 206 | 183.0006 K and −0.0130 from the 16-parameter calibration, SE 0.1444 | 179.8579 K and −0.0661 from the MEA model, where the interaction has a conditional SE of 0.5092 and the energy one of 59.45 K |
| `supplement.tex` l. 374 | Diameter free, correlation 0.998 with $A_4$, SEs 4.57 and 1.66 Å | The carbamate diameter is on its upper bound, so it has no standard error. $A_4$ has a conditional SE of 0.245. The 0.998 degeneracy no longer appears among the free coordinates. |
| `supplement.tex` l. 446–450 | 92 instabilities, all outside R5 and 65 outside R4. Largest decrease at 1.215 MPa, densities 44,631 and 31,743 mol/m³ | 93, all outside R5 and 65 outside R4. Confirmed at 26.8–30.0 wt %, 363.15–393.20 K and 0.400–0.966 mol/mol. Largest decrease 0.01881 mol (numerical estimate 2.8 × 10⁻⁹) at 393.15 K, 30.0 wt %, 0.700 mol/mol and 1.212 MPa, with densities 44,899 and 31,612 mol/m³. |
| `supplement.tex` l. 480 | Objective 61.4227, relative difference 9 × 10⁻¹⁰, diameters differ by 0.0002 Å | 61.2853 for both starts, relative difference 7 × 10⁻¹². Both diameters are at the 6.5 Å upper bound, and start 1 is selected. |
| `supplement.tex` l. 481 | 3.5 Å floor sensitivity, < 0.001 percentage points, 73 splits | The floor sensitivity was not rerun on F2. With the diameter at its upper bound, the lower bound does not act. Remove the sentence or state that. |

The measured states keep the #404 pattern. At the selected F2 start, 6 measured states have confirmed splits (Hartono 2021 rows 55–57 at 373.0 K, Tong rows 29 and 32 at 373.2 K and row 44 at 393.2 K). Another 8 have unconfirmed instabilities (Hartono rows 53, 54, 63 and 64; Tong rows 27, 28, 30 and 31). All are comparison rows at 373–393 K. If the text names measured-state splits, use these.

## Part B: split-free set, AMPH⁺–water slope fixed at −150 K

Sources: [confirmation](slope-150/confirmation.json), [parameters](slope-150/parameters.json), [uncertainty](slope-150/conditional-uncertainty.json), [full search](slope-150/search-1.json.gz), [diagnosis probes and scans](diagnosis/), [same-row deviations](same-row-deviations.csv) (case "Slope -150 K against F2 main").

**Result.** The fit refits the other eight coordinates with $b_{\mathrm{AMPH^+,w}}$ fixed at −150 K, and two of them are on bounds. Both starts converge to cost 62.0651. The full 666-state search with the 7301-trial bank completes every state with 0 descents, measured states included. The smallest supplied-trial TPD is +1.66 × 10⁻⁴.

**Cause, for the methods and results text.** Every fitted CO₂-loaded row lies at 313–353 K. The fitted AMPH⁺–water slope raises $k_{\mathrm{AMPH^+,w}}$ from −0.178 at 353 K to −0.117 at 393 K. The weaker cation–water attraction then salts out a liquid rich in AMPH⁺, HCO₃⁻ and AMP, while carbamate stays at 10⁻⁴–10⁻³ mole fraction. Two changes above 353.22 K each remove every descent: holding that $k_{ij}$ at its 353.22 K value, or continuing the AMP dissociation law at constant enthalpy, which lowers ln K by 0.04 at 393 K. Holding R4 or moving the carbamate diameter to its floor leaves 90–93 descents. The scan also bounds the slope from the other side. Slopes of 0 to −100 K move the splits to 298–323 K, onto the fitted Ciftja NMR states. With F2, −125 and −150 K are split-free and −175 K leaves 5 grid descents at 383–393 K with τ ≈ −6 × 10⁻⁵.

### Table 7, alternative column (title “stability-constrained alternative” → “fixed-slope alternative”, or as the owner chooses)

| Coordinate | Value | Conditional SE |
|---|---:|---:|
| $k_{\mathrm{AMP,w}}$ | −0.1261 | 0.0055 |
| $b_{\mathrm{AMP,w}}$ (K) | −42.381 | 14.861 |
| $k_{\mathrm{AMPH^+,w}}$ | −0.2475 | 0.0083 |
| $b_{\mathrm{AMPH^+,w}}$ (K) | −150 (fixed) | — |
| $k_{\mathrm{AMPH^+,CO_2}}$ | 0.7821 | 0.0680 |
| $\sigma_{\mathrm{AMPH^+}}$ (Å) | 6.4694 | 0.3221 |
| $\sigma_{\mathrm{AMPCOO^-}}$ (Å) | 6.5000 (upper bound) | — |
| R4 $A_4$ | 10.8679 | 0.2654 |
| R4 $\delta h$ (J/mol) | −5000.0 (lower bound) | — |

The note “The stability-constrained alternative has no standard errors” becomes: the alternative is a converged fit with conditional standard errors, and its AMPH⁺–water slope is fixed.

### Table 8, alternative row

`AMP, fixed-slope alternative & 8 & 2 & 10.49 (47) & 7.12 (73) & 35.50 (114) & 666 & 0 & 0`. The old row was 9, 1, 20.20, 13.39, 59.51.

### Table S5, alternative block

| Key | Value |
|---|---:|
| $k_{\mathrm{AMP,w}}$ | −0.12612425937544733 |
| $b_{\mathrm{AMP,w}}$ (K) | −42.38099210214674 |
| $k_{\mathrm{AMPH^+,w}}$ | −0.2474860342099225 |
| $b_{\mathrm{AMPH^+,w}}$ (K) | −150 (fixed) |
| $k_{\mathrm{AMPH^+,CO_2}}$ | 0.7820806483424216 |
| $\sigma_{\mathrm{AMPH^+}}$ (Å) | 6.4693623248364664 |
| $\sigma_{\mathrm{AMPCOO^-}}$ (Å) | 6.5 |
| R4 $a$ | 10.867934092746673 |
| R4 $\delta h$ (J/mol) | −5000.0 |

### Part B prose

| Location | Old | New |
|---|---|---|
| `main.tex` abstract l. 97 | “an alternative set with none detected deviates by 20.2 %” | A set with the AMPH⁺–water temperature coefficient fixed has no detected instability and deviates by 10.5 %. |
| `sections/introduction.tex` l. 38 | “at least 73 splits for AMP, all above …” | Keep it, and add that fixing the extrapolated cation–water temperature coefficient removes them. |
| `sections/data_methods.tex` l. 101 and the interpolation sentence | The AMP alternative is the interpolated set from the penalty procedure | The AMP alternative refits the eight other coordinates with $b_{\mathrm{AMPH^+,w}}$ fixed at −150 K. It is a converged fit, not an interpolation. The MDEA interpolation text stays. |
| `sections/transfer_results.tex` l. 20 | Alternative carbamate diameter 5.98 Å | The alternative carbamate diameter is also at 6.5 Å. |
| `sections/transfer_results.tex` l. 39–40 | “they do not identify which model quantity produces the splits”, and “Fits with the stability penalty still leave states …” | The splits follow from the extrapolated AMPH⁺–water temperature coefficient (cause above). With that coefficient fixed at −150 K, the 666 searches detect no instability. |
| `sections/transfer_results.tex` l. 75 | The alternative is worse for Tong and Kundu and slightly better for Hartono 373–393 K | The alternative is worse for Kundu (47.02 against 43.91 %) and for Hartono 373–393 K (28.35 against 28.10 %), and slightly better for Tong (27.98 against 28.16 %). |
| `sections/transfer_results.tex` l. 91 | “Within AMP the trade-off is real … 20.2 % against 10.4 %” | Within AMP no material trade-off remains: the set without a detected instability deviates by 10.5 % against 10.3 % on the 47 fitted loaded pressures. |
| `sections/conclusion.tex` l. 15–16 | Alternative 20.2 %, and “None of the fits made here gives an AMP parameter set that both …” | The alternative with the fixed cation–water temperature coefficient has none detected at 10.5 %. **Delete the “None of the fits …” sentence.** |
| `supplement.tex` l. 400 | 19.92 / 20.81, 21.47 / 28.87, 31.30 / 112.57, 53.66 / 24.70 | 11.46 / 8.42, 26.52 / 31.23, 20.07 / 54.43, 28.56 / 27.55 |
| `supplement.tex` l. 482–488, the penalty and interpolation paragraph for AMP | The anchor, penalty stages, bisection, $t$ = 0.558556, cost 126.86 and loaded-pressure contribution 58.89 → 123.61 | Replace it with the fixed-slope fit: both starts give 62.0651. The full search with the 7301-trial bank finds 0 descents and a smallest supplied-trial TPD of +1.66 × 10⁻⁴. The slope scan gives −125 and −150 K split-free, −175 K with 5 grid descents, and 0 to −100 K with splits at 298–323 K. The loaded-pressure contribution to the objective rises from 58.89 at the F2 main fit to 59.70. The other contributions are binary pressure 0.013, binary vapor fraction 0.426 and carbamate fraction 1.925, [group costs](slope-150/group-costs.json). |
| `supplement.tex` l. 375 | “the stability-constrained AMP alternative has none” | The fixed-slope alternative has conditional standard errors (Table 7). |
| Dissertation, Sections 6.3 and 6.4 (another repository) | Limitation and future work: no accurate split-free AMP set | Out of scope here. The limitation is resolved for the model form, and the future-work item can be closed. |

Still to do when applying: `scripts/dea_displays.py` selects the AMP sources (now #404). Point it at this folder, update its assertions, and regenerate Tables 6–8, S5, S9 and S20, both AMP figures and `tables/number-sources.json`. No LaTeX source was changed in #412.
