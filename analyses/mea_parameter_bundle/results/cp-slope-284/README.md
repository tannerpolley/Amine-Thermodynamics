# Unloaded 30 wt% MEA heat-capacity slope (issue 284): water, MEA and excess separated

**Result.** The MEA–water excess carries the slope error. Over 313.15 → 353.15 K at 101325 Pa:
- the model's excess heat capacity falls by 0.119 kJ kg⁻¹ K⁻¹;
- the reference excess rises by 0.088–0.103, depending on which mixture and pure-MEA sources are combined.

The excess share of the mixture slope error is 1.08–1.11 for all four source pairings. Pure water's share is −0.10 to −0.11, the opposite sign. Pure MEA's share is −0.002 to +0.029: its slope agrees with both pure-MEA sources, but its level is about 8 % low.

The routing rule sends the issue to Stage 2. On the corrected Engine wheel, both authorized joint fits run but fail F2–F4 (current assessment below). The earlier Engine refusal is retained as history. Nothing is adopted: `selected-current-best-parameters.json`, the Engine pin, the manuscript and `analyses/_cse-manuscript.json` are unchanged.

Stage 1 is numerical verification and comparison with measurements at fixed final-set parameters. Stage 2 is calibration and numerical verification. Neither is validation.

## Inputs and method

- **Stage 1 Engine.** Wheel `8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069` (Engine `bc779473`), installed only in this worktree. Every JSON records it.
- **Parameters.** The final set `results/selected-current-best-parameters.json` (`00e77608…`), with the #260 IAPWS-95 water ideal-gas record.
- **Script.** [`scripts/cp_slope_284.py`](../../scripts/cp_slope_284.py), run from the repository root:
  - `reference` runs under the ePC-SAFT `.venv` (chemicals 1.5.2).
  - All other commands run under the worktree `.venv` with `agent-heavy`.
  - `present` reads retained files only.
- **Pure water.** [decomposition.json](decomposition.json) `water` against [IAPWS-95](iapws95-water.csv) ([provenance](iapws95-provenance.json); same module bytes as `density-cp-160`):
  - 298.15–368.15 K at 101325 Pa;
  - 298.15–393.15 K at 0.3 MPa.
- **Pure liquid MEA.** 298.15–393.15 K at 101325 Pa, split into ideal-gas and residual parts. The two sources were acquired for this issue ([sources](pure-mea-sources.csv), [provenance with PDF hashes, methods and uncertainty](source-provenance.json)):
  - **Maham et al. (1997)** (primary). Zotero `5NDWELSM`, Table 1 p.1748; Table 2 and Eq. (1), p.1748: $c_p = 82.5 + 0.275\,T$ J mol⁻¹ K⁻¹, 299.1–397.8 K. Setaram C-80 heat-flow calorimeter, stated 0.9 %.
  - **Chiu, Liu & Li (1999).** Zotero `DZAER4AP`, Table 2 p.633, 303.15–353.15 K. DSC, ±2 % accuracy and ±3 % including impurities.

  Hilliard (2008) §4.7.2 measured pure MEA but shows it only in Figure 4.7-3, so it is not used.
- **Mixture.** #264's unloaded row (10⁻⁶ mol CO₂ per mol MEA, liquid only) on the same grid, at two compositions:
  - Hilliard's 7 mol MEA/kg water, $w_\text{MEA}=0.29950$;
  - Concepción's $w_\text{MEA}=0.2997$.

  The grid reproduces #264's Hilliard rows exactly (relative difference 0). Concepción differs by 4.6–6.7×10⁻⁷ because #264 ran it at 100 000 Pa and this issue runs every state at 101325 Pa.
- **Excess.** $c_p^E=c_p-(1-w)c_{p,\text{W}}-w\,c_{p,\text{MEA}}$, mass basis.
  - The reference excess is measured mixture minus IAPWS-95 water minus pure-MEA source.
  - It is computed for each mixture source with each pure-MEA source.

## F1: closure, shares and routing

**Closure.** For pure water and pure MEA, the residual Cv is computed term by term (centred differences at fixed density, h = 0.025 K; #264 `calculate.py` lines 139–147) and summed. The sum matches the native residual Cv within 4.53×10⁻⁵ J mol⁻¹ K⁻¹. For the mixture the maximum difference is 3.84×10⁻⁵, asserted inside #264's `decompose`. Halving the step changes any term by at most 2.35×10⁻⁵. Every value passes 10⁻⁴ relative to |Cv_res| plus 10⁻⁴ J mol⁻¹ K⁻¹ absolute. **F1 closure: pass.**

**Slope over 313.15 → 353.15 K** ([shares.json](shares.json); kJ kg⁻¹ K⁻¹; error = model change − reference change):

| Part | Model change | Reference change | Slope error | Weighted error |
|---|---:|---:|---:|---:|
| water (IAPWS-95) | +0.0472 | +0.0173 | +0.0298 | +0.0209 (×0.7005) |
| MEA, Maham | +0.1814 | +0.1801 | +0.0013 | +0.0004 (×0.2995) |
| MEA, Chiu | +0.1814 | +0.2000 | −0.0186 | −0.0056 |
| mixture, Hilliard | −0.0312 | +0.1598 | −0.1910 | — |
| mixture, Concepción | −0.0313 | +0.1690 | −0.2003 | — |
| excess, Hilliard / Maham | −0.1186 | +0.0937 | −0.2123 | −0.2123 |
| excess, Hilliard / Chiu | −0.1186 | +0.0878 | −0.2064 | −0.2064 |
| excess, Concepción / Maham | −0.1187 | +0.1029 | −0.2215 | −0.2215 |
| excess, Concepción / Chiu | −0.1187 | +0.0969 | −0.2156 | −0.2156 |

| Mixture source / MEA source | Water share | MEA share | Excess share | Carrier |
|---|---:|---:|---:|---|
| Hilliard / Maham | −0.109 | −0.002 | **1.111** | excess |
| Hilliard / Chiu | −0.109 | +0.029 | **1.080** | excess |
| Concepción / Maham | −0.104 | −0.002 | **1.106** | excess |
| Concepción / Chiu | −0.104 | +0.028 | **1.076** | excess |

The weighted errors sum to the mixture error within 3×10⁻¹⁷ in every case.

**Routing.**
- The issue's rule: exactly one carrier with share ≥ 0.5 against both mixture sources.
- Applied here against both pure-MEA sources as well.
- Result: **excess → Stage 2.**

**Pure water** reproduces the water-124 comparison on the current record and wheel. From 313.15 to 353.15 K the model rises +0.047 and IAPWS-95 +0.017, at both 101325 Pa and 0.3 MPa. From 298.15 to 353.15 K at 101325 Pa, the model rises +0.071 and IAPWS-95 +0.015.

**Pure MEA.**
- Slope: of the model's +0.181 rise over 313–353 K, +0.125 is ideal-gas (Zhang, Que & Chen 2011 correlation) and +0.056 residual.
- Level: the model is low against both sources:

  | T / K | Model | Maham | Chiu |
  |---:|---:|---:|---:|
  | 313.15 | 2.539 | 2.761 (−8.0 %) | 2.78 (−8.7 %) |
  | 353.15 | 2.720 | 2.941 (−7.5 %) | 2.98 (−8.7 %) |

**What moves in the mixture.** At the Hilliard composition from 313.15 to 353.15 K, the term changes in kJ kg⁻¹ K⁻¹ are:
- hard-chain residual Cv +1.034;
- dispersion −1.188;
- association −0.231;
- pressure–volume coupling +0.307;
- MEA ideal +0.037;
- water ideal +0.009.

They sum to the −0.031 total. The model's mixture slope comes from near-cancellation of large residual terms.

## The +5.53 % at 318.15 K against Hilliard

[excess-by-temperature.csv](excess-by-temperature.csv) splits model − measured at each temperature into water, MEA and excess parts that sum exactly. Values are in kJ kg⁻¹ K⁻¹:

| State | Model − measured | Water part | MEA part (Maham / Chiu) | Excess part (Maham / Chiu) |
|---|---:|---:|---:|---:|
| Hilliard 313.15 K | +0.2353 (+6.36 %) | −0.0253 | −0.0665 / −0.0723 | +0.3271 / +0.3329 |
| **Hilliard 318.15 K** | **+0.2058 (+5.53 %)** | −0.0209 | −0.0665 / −0.0745 | **+0.2932 / +0.3012** |
| Hilliard 353.15 K | +0.0442 (+1.15 %) | −0.0044 | −0.0661 / −0.0779 | +0.1148 / +0.1265 |
| Concepción 313.15 K | +0.0609 (+1.57 %) | −0.0253 | −0.0665 / −0.0723 | +0.1527 / +0.1585 |
| Concepción 353.15 K | −0.1394 (−3.45 %) | −0.0044 | −0.0661 / −0.0779 | −0.0688 / −0.0570 |

**The excess alone is too high.** At 318.15 K the model excess is +0.251 kJ kg⁻¹ K⁻¹, against −0.042 (Hilliard − IAPWS-95 − Maham). That is about +0.29, or +7.9 % of the mixture value.

**The pure parts partly mask it.** The low pure-MEA level (−0.067 to −0.075) and pure water (−0.021) offset about 30 % of the excess error. Without them, the offset would be about +7.9 % rather than +5.53 %.

**Why the offset shrinks with temperature.** The model excess falls from +0.269 at 313.15 K to +0.151 at 353.15 K. The reference excess rises, from −0.058 to +0.036 with Hilliard, or from +0.117 to +0.220 with Concepción. The temperature-dependent part of the offset is therefore the excess slope.

**Source disagreement.** Using common pure-component reference functions, almost all of the 0.17–0.18 kJ kg⁻¹ K⁻¹ Hilliard–Concepción difference appears in the calculated reference excess. Their slightly different compositions contribute a weighted pure-reference difference of about −0.00024 to −0.00028 kJ kg⁻¹ K⁻¹. This is an algebraic allocation under the selected references; the experimental source disagreement remains unresolved. Against Hilliard, the model excess is too high at every temperature. Against Concepción, it is too high below about 340 K and too low above.

![Heat capacity against temperature. (a) Pure water, model lines and IAPWS-95 points at 0.1 and 0.3 MPa. (b) Pure liquid MEA, model line and Maham 1997 (±0.9 %) and Chiu 1999 (±2 %) points. (c) Unloaded 30 wt% MEA–water, final-set and inadmissible stage 2 retreated-record lines at Hilliard’s composition with Hilliard, Concepción and Weiland points. (d) Excess heat capacity, the same model records as lines and reference excess points for each mixture/pure-MEA source pair. Shading marks the 313.15–353.15 K slope interval. Model lines are retained 5 K evaluations; points are measurements or evaluated references.](heat-capacity-slope.png)

[plotted-values.csv](plotted-values.csv) retains every plotted value.

## Historical Stage 2 refusal on Engine bc779473

**Choosing the coefficient** ([stage2/p2/qualification/summary.json](stage2/p2/qualification/summary.json)). The bound-scaled finite-difference sensitivity of the model's 313 → 353 K change at the final set is:
- a₁ (bound ±10⁻³ K⁻¹): +0.0615;
- a₂ (bound ±2×10⁻⁵ K⁻²): −0.1714.

The issue's rule picks the larger, **a₂**: $k_{ij}(T)=a_0+a_2(T-313.15)^2+s(1/T-1/313.15)$.

**Zero-change replay.** The converted record with a₂ = 0 reproduces the 307 objective rows and the 60 #264 Cp rows with relative difference **0.0** at both starts:
- final set, cost 148.883260;
- #255 candidate, cost 148.510546.

**Engine refusal.** The fit `fit2 final` ([fit.json](stage2/p2/final/stage-0/fit.json), [log](stage2/logs/fit2-final-attempt-2-engine-refusal.log)) stops at its first Jacobian with `initial_evaluation_failed`, `invalid direction composition balance` (`Stop.left_domain`). The reported observation index equals the observation count, so it names no single row.

[stage2/p2/diagnosis.json](stage2/p2/diagnosis.json) differentiates each of the 60 #264 Cp observations with respect to the law slot alone, at the converted final set.

For **a₂**, 20 of 60 are available and 40 refused:
- 35 raise `ParameterError: invalid direction composition balance` or `… charge balance`;
- 5 return `ActionUnavailable`.

The refused states:
- unloaded Hilliard at 343.15 K and above;
- loaded Hilliard (α = 0.139 and 0.358) at 333.15 K and above;
- Weiland at 298.15 K, α = 0.4 and 0.5;
- Concepción at 353.15 K.

At Hilliard 353.15 K, unloaded (7 mol MEA/kg water, α = 10⁻⁶, 101325 Pa), the message is:
`reference_unavailable: phase[0]: supplied records inconsistent with reaction R3; residual 2.7389677383656975e-08; criterion 1.4901161193847656e-08; reference_completion rank 5/6; threshold 1.1102230246251565e-15`.

The other `ActionUnavailable` states give the same message with R1 at 343.15 and 348.15 K (residuals 1.85 and 2.74×10⁻⁸) and with R3 at 358.15 K (2.37×10⁻⁸).

The retained per-state probes show that a₁ derivatives are available at all 60 states, while a₂ derivatives are refused at 40. The full fit also stops at its first Jacobian. These observations isolate a₂ differentiation as a reproducible trigger; they do not establish the underlying Engine cause. The reference-completion message is an observed diagnostic, not proof that the physical state or supplied thermodynamic records are invalid.

**Where available, the Engine derivatives are correct.** They agree with central differences (h = 1 % of the bound) at unloaded Hilliard 313.15 and 333.15 K:
- a₂ within 1.3×10⁻⁹ relative;
- a₁ within 2.6×10⁻⁷ relative at 313.15, 333.15 and 353.15 K.

At 353.15 K the central difference for a₂ is −6.52×10⁶ J mol⁻¹ K⁻¹ per K⁻², and the Engine returns nothing.

**Disposition.** The owner chose (2026-11-09) to keep the issue's selection rule, not substitute a₁, and report F2–F4 as not run.

**Draft Engine use case — equilibrium heat-capacity derivative for the MEA–water quadratic interaction law**

**Exact declaration and inputs.** Use the converted final parameter document retained at `stage2/p2/starts/final.json`, the #255-bound chemistry and caloric declarations, and the #264 60-state Cp observations. The MEA–water `k_ij` declaration has temperature-law form `polynomial-plus-reciprocal-temperature`, reference temperature 313.15 K, power-zero coefficient −0.08990160794755829, power-two coefficient `pair/monoethanolamine/water/k_ij/a2` initially 0 K⁻², and reciprocal-temperature slope −8.057331218929972 K:

$$k_{ij}(T)=-0.08990160794755829+a_2(T-313.15)^2-8.057331218929972(1/T-1/313.15).$$

Activate a₂ through `ParameterFamily.TemperatureLawCoefficient`. A reproducing state is unloaded Hilliard at 353.15 K and 101325 Pa: 1 mol analytical MEA, water corresponding to 7 mol MEA/kg water, and 10⁻⁶ mol CO₂, with the declared nine-species liquid chemistry and neutral references.

**Quantity consumed.** MEA consumes the derivative of `equilibrium_isobaric_heat_capacity` with respect to a₂ through `regression.differentiate` for its parameter-fitting Jacobian. Native Cp predictions are converted to kJ/kg/K using the existing `feed_amount_mol/feed_mass_kg/1000` factor.

**Observed refusal.** Wheel SHA-256 `8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069` returns:

`reference_unavailable: phase[0]: supplied records inconsistent with reaction R3; residual 2.7389677383656975e-08; criterion 1.4901161193847656e-08; reference_completion rank 5/6; threshold 1.1102230246251565e-15`

**Proposed acceptance criterion.** At the converted final set, return available a₂ derivatives for all 60 declared Cp observations and permit the initial joint fitting Jacobian to evaluate while preserving the declared physical inputs and numerical tolerances. At unloaded Hilliard 313.15, 333.15 and 353.15 K, compare against centered differences with step 2×10⁻⁷ K⁻² and require relative discrepancy ≤3×10⁻⁷. The current centered difference at 353.15 K is −6.520096658×10⁶ J mol⁻¹ K⁻¹ per K⁻². Preserve zero-change predictions within the issue's 10⁻¹² relative criterion. This request concerns Engine differentiation; it makes no claim that the subsequent MEA fit will satisfy F2–F4.

**Fixed-parameter scans (diagnostic only; not fits or candidates).** One law coefficient is changed at otherwise fixed final-set parameters. Values are in kJ kg⁻¹ K⁻¹ at the Hilliard composition:

| Coefficient | Cp 313.15 K | Cp 353.15 K | 313 → 353 change | Hilliard 51 AARD |
|---|---:|---:|---:|---:|
| none (final set) | 3.932 | 3.901 | −0.031 | 2.44 % |
| a₂ = −2×10⁻⁷ K⁻² | 3.987 | 3.958 | −0.030 | 3.15 % |
| a₂ = −1×10⁻⁵ | 6.701 | 6.775 | +0.074 | 86.9 % |
| a₂ = −2×10⁻⁵ (bound) | 9.471 | 9.689 | +0.218 | 174 % |
| a₁ = −10⁻³ K⁻¹ (bound) | 3.773 | 3.688 | −0.085 | 6.13 % |
| a₁ = +10⁻³ (bound) | 4.121 | 4.161 | +0.040 | 10.0 % |

Curvature in $k_{ij}(T)$ moves the Cp level far more than its slope, because Cp contains $-RT^2(\partial a/\partial k)\,k''$. Alone, a₂ raises the slope only by raising the level, and the slope must rise while the Hilliard level must fall. Whether a₀ and s can compensate jointly inside their bounds is the question the fit was to answer; these scans do not answer it.

## Stage 2 on the corrected Engine wheel

The retained sensitivity rule keeps a₂: its bound-scaled slope sensitivity is −0.1714 versus +0.0615 for a₁. The fitted law is $k_{ij}(T)=a_0+a_2(T-313.15\,\mathrm{K})^2+s(1/T-1/(313.15\,\mathrm{K}))$. The earlier bc779473 refusal is historical; its records remain under `stage2/` in the results directory.

Both authorized joint fits fail F2, F3 and F4. Neither record is admissible for the issue. The selected law does not carry the required unloaded slope in these runs despite interior a₂. The two fits also refit the existing coordinates, so their changes cannot be attributed to a₂ alone. Nothing is adopted.

The wheel is from merged Engine main `391dfe5d64ede5036bf160bc6ae037ad5e14af32`, SHA-256 `0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`, installed only in this worktree. Step 0 passed: both 307-row replays agree within 10⁻⁸ relative, the stage 1 decomposition reproduces, and a₂ derivatives are available at all 60 Cp states and agree with centered differences within 3×10⁻⁷ at the three declared unloaded states. On takeover, zero-change replay again reproduced all 367 predictions exactly at both starts (maximum relative difference 0). See `stage2-391dfe5d/p2/qualification/`.

Both starts use the retained #255 controls: 180 iterations, function tolerance 10⁻⁶, gradient tolerance 10⁻⁸, parameter tolerance 10⁻¹⁰, penalty scales 0.01 then 0.003, and maximum elapsed time 76,800 seconds per stage. Runs used `agent-heavy`, with three workers derived from its core allowance. Each stage was saved before continuing. Iterations below are the Engine’s `iterations`, excluding the initial history point. Wall times are single-run elapsed times, not a performance comparison.

| Start | Stage | Iterations | Termination | Wall time / s | Data cost (354 rows) | Stability cost |
|---|---:|---:|---|---:|---:|---:|
| final | 0 | 57 | converged | 11931.811 | 183.710677 | 0.034060 |
| final | 1 | 14 | converged | 2939.356 | 183.785421 | 0.012986 |
| candidate | 0 | 50 | converged | 10619.032 | 183.708246 | 0.036457 |
| candidate | 1 | 11 | converged | 2509.156 | 183.785386 | 0.013017 |

The reported candidates are **admissible retreated records on the enforced grid**, not local optima. Their fresh assessment follows:

| Start | Retreat fraction t | #255 307-row cost | Total 354-row cost | Enforced descent | Offset descent | Census descent |
|---|---:|---:|---:|---:|---:|---:|
| final | 0.984462890625 | 149.302577 | 184.110315 | 0/1903 | 0/576 | 0/162 |
| candidate | 0.974853515625 | 149.190130 | 184.067010 | 0/1903 | 0/576 | 0/162 |

All enforced and offset states are available; both censuses are complete. The five originally excluded states are available without descent at both records. The reference final-set 307-row cost is 148.883260; neither retreated record improves it.

| Law coordinate | Final start | #255 candidate start | Bounds |
|---|---:|---:|---|
| a₀ | -0.0877559203819 | -0.0877693643621 | [-0.5, 0.5], both interior |
| s / K | -3.31071763699 | -3.34812784186 | [-1000, 1000], both interior |
| a₂ / K⁻² | 1.23625876088e-07 | 1.22406095462e-07 | [-2e-05, 2e-05], both interior |

Coordinates on bounds at the retreated records (reporting distance ≤10⁻⁹ × max(1, |bound|), in each coordinate’s native units; Born diameter is in Å):

- final: `pair/carbamate-anion/protonated-monoethanolamine/k_ij` = -1; `component/protonated-monoethanolamine/born_diameter` = 5. Total enthalpy shifts R2 = 9823.437352, R5 = 9220.786865 J/mol.
- candidate: `pair/carbamate-anion/protonated-monoethanolamine/k_ij` = -1; `component/protonated-monoethanolamine/born_diameter` = 5. Total enthalpy shifts R2 = 9732.923398, R5 = 9233.775129 J/mol.

**F2 — fail for both starts.** The accepted target is 0.164 ± 0.05 kJ kg⁻¹ K⁻¹. The unrounded source mean is 0.1644; either rounding gives the same decision.

| Start | Cp change, 313.15 → 353.15 K / kJ kg⁻¹ K⁻¹ | Difference from source mean |
|---|---:|---:|
| final | -0.02290303 | -0.18730303 |
| candidate | -0.02296632 | -0.18736632 |

**F3 — fail for both starts.** At 353.15 K both predictions are below Hilliard’s lower envelope edge. The envelope is a source range, not an uncertainty interval. All values are kJ kg⁻¹ K⁻¹ at the declared unloaded states.

| Temperature / K | Hilliard–Concepción envelope | Final start | #255 candidate start |
|---:|---|---:|---:|
| 313.15 | [3.6968, 3.8710] | 3.8476927 (inside) | 3.8484240 (inside) |
| 333.15 | [3.7862, 3.9570] | 3.8298585 (inside) | 3.8305571 (inside) |
| 353.15 | [3.8566, 4.0400] | 3.8247896 (outside) | 3.8254577 (outside) |

**F4 — fail for both starts.** #255 criteria 1–3 pass, the interaction-law coefficients are interior, and broad Cp error falls below its threshold, but each record has dense-liquid descent at two of the 60 #264 states: Weiland at 298.15 K, analytical loadings 0.4 and 0.5.

| Start | 60-row Cp AARD / % (limit 2.512) | Hilliard 51-row AARD / % (baseline 2.443) | #264 dense / gas / unresolved states |
|---|---:|---:|---|
| final | 2.139275 | 2.041159 | 2 / 13 / 0 of 60 |
| candidate | 2.139135 | 2.042228 | 2 / 13 / 0 of 60 |

AARD denotes average absolute relative deviation; RMSE denotes root-mean-square error. The #255 preservation checks against the final set are retained below. Pressure/species entries are AARD rises in percentage points (limit +2). Other entries are within-2-scale count, AARD ratio and RMSE ratio (counts must not fall; each ratio ≤1.25). Cai is reported only.

| Group | Final start | #255 candidate start |
|---|---|---|
| fitted CO2 partial pressure | +1.111119 points; pass | +0.999480 points; pass |
| Kiepe pressure | +0.000000 points; pass | +0.000000 points; pass |
| fitted phase mole fraction | +0.173007 points; pass | +0.154218 points; pass |
| restored species | +0.239663 points; pass | +0.269282 points; pass |
| Jakobsen ratio | +0.372606 points; pass | +0.186831 points; pass |
| loaded density | 44 → 47; 0.747241 / 0.733892; pass | 44 → 47; 0.738364 / 0.750125; pass |
| CO2-free density | 5 → 5; 1.142214 / 1.117909; pass | 5 → 5; 1.142349 / 1.117736; pass |
| fitted heat of absorption | 8 → 8; 0.911546 / 0.879082; pass | 8 → 8; 0.905586 / 0.874892; pass |
| heat capacity | 3 → 4; 0.743567 / 0.701607; pass | 3 → 4; 0.743622 / 0.702843; pass |

The 329-row #264 comparison table (307 original rows plus 22 integral heats) and 60 Cp rows are retained for the reference and both records as `comparison-264.json`. Every prediction is available. Cai’s two response quantities are reported separately for RMSE, since temperature and mole fraction have different units. Cai remains comparison-only.

| Record | Cai within 2 scales | Cai AARD / % | Cai temperature RMSE / K | Cai vapor fraction RMSE | Integral heat AARD / % | Integral heat RMSE / kJ mol⁻¹ CO₂ | Integral heat within 2 scales |
|---|---:|---:|---:|---:|---:|---:|---:|
| reference final set | 36/50 | 1.479929 | 1.787980 | 0.02037915 | 5.610977 | 6.567928 | 9/22 |
| final | 36/50 | 1.480991 | 1.783916 | 0.02033250 | 5.304628 | 6.345912 | 10/22 |
| candidate | 36/50 | 1.480984 | 1.783928 | 0.02033301 | 5.315508 | 6.360471 | 10/22 |

Under the issue’s failure meanings, F2 with interior a₂ means the chosen law did not carry the slope in these authorized joint fits; F3 and F4 failures make the records inadmissible. No second law or a₁ substitution was tried. `select2` retains the lower-cost candidate-start record solely for illustration when neither passes F4; `selected.json` explicitly records `admissible: false`. The selected grid and figure must not be read as parameter selection for use.

Evidence: calibration and numerical verification, not validation. Stability searches are finite tests at declared states, not a global guarantee. The unresolved source-level difference, assumed Hilliard pressure, mixed-source excess reference, and separate pure-MEA level discrepancy remain. This work estimates no parameter uncertainty, and joint changes do not isolate a₂. Delivered-result review is pending with the orchestrator; there is no manuscript promotion.

Retained evidence: `stage2-391dfe5d/p2/{final,candidate}/` contains the fit stages, retreat, 307-row replay, assessment, census, and `heat-capacity.json` (all 60 rows and phase-search records); `selected.json` and `selected-grid.json` retain the illustrative choice and continuous evaluations. Logs are in `stage2-391dfe5d/logs/`.

## Limits

- Using common pure-component reference functions, almost all of the 0.17–0.18 kJ kg⁻¹ K⁻¹ Hilliard–Concepción difference appears in the calculated reference excess. Their slightly different compositions contribute a weighted pure-reference difference of about −0.00024 to −0.00028 kJ kg⁻¹ K⁻¹. This is an algebraic allocation under the selected references; the experimental source disagreement remains unresolved.
- Hilliard's sample pressure is assumed to be 101325 Pa.
- Each reference excess combines mixture calorimetry—Hilliard's DSC or Concepción's flow calorimeter—an IAPWS-95 water calculation, and Maham's heat-flow or Chiu's DSC pure-MEA measurement.
- The pure-MEA sources differ in level by about 0.7–1.3 % and in 313–353 K slope by 0.020 kJ kg⁻¹ K⁻¹. Both give the same carrier.
- The low pure-MEA level (about −8 %) is a separate discrepancy. This issue does not split it between the Zhang ideal-gas correlation and the residual; doing so routes to Design.
- The share rule's 0.5 threshold is a design choice.
- Stage 1 uses fixed final-set parameters; the shares decompose one record, not a fitted attribution. Stage 2 refits coordinates jointly.

## Files

- `stage2/p2/a6-spec.json` holds the #255 coordinates with MEA–water a₀ and s as law slots plus a₂.
- `stage2/p2/starts/` holds the converted final set and the converted #255 candidate.
- [logs](stage2/logs/) keeps every attempt:
  - `fit2-final-attempt-1-missing-origin.log`: the #255 driver takes coordinate origins from the specification's stored endpoint, which lacked the a₂ slot. The stored endpoint is now converted the same way, with a₂ = 0.
  - `fit2-final-attempt-2-engine-refusal.log`: the refusal above. The #255-candidate start was stopped before it began, because it would meet the same refusal.
- `fit2`, `assess2`, `select2` and `grid2` implement the rest of Stage 2 (penalty stage, retreat, #255 criteria 1–3, the #264 Cp tables and phase searches, F2–F4, selection, and the candidate's mixture sweep). The bc779473 attempt stopped as above; the completed corrected-wheel execution is retained in `stage2-391dfe5d/`.
