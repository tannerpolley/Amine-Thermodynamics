# Unloaded 30 wt% MEA heat-capacity slope (issue 284): water, MEA and excess separated

**Result.** The MEA–water excess carries the slope error. Over 313.15 → 353.15 K at 101325 Pa:
- the model's excess heat capacity falls by 0.119 kJ kg⁻¹ K⁻¹;
- the reference excess rises by 0.088–0.103, depending on which mixture and pure-MEA sources are combined.

The excess share of the mixture slope error is 1.08–1.11 for all four source pairings. Pure water's share is −0.10 to −0.11, the opposite sign. Pure MEA's share is −0.002 to +0.029: its slope agrees with both pure-MEA sources, but its level is about 8 % low.

The routing rule therefore sends the issue to Stage 2. Stage 2 (one added `k_ij` temperature-law coefficient) did not produce a fit: the selected coefficient a₂ is refused by the Engine (below). F2–F4 are not run. Nothing is adopted: `selected-current-best-parameters.json`, the Engine pin, the manuscript and `analyses/_cse-manuscript.json` are unchanged.

The evidence is numerical verification and a comparison with measurements at fixed final-set parameters. It is not validation.

## Inputs and method

- **Engine.** Wheel `8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069` (Engine `bc779473`), installed only in this worktree. Every JSON records it.
- **Parameters.** The final set `results/selected-current-best-parameters.json` (`00e77608…`), with the #260 IAPWS-95 water ideal-gas record.
- **Script.** [`scripts/cp_slope_284.py`](../../scripts/cp_slope_284.py), run from the repository root:
  - `reference` runs under the ePC-SAFT `.venv` (chemicals 1.5.2).
  - All other commands run under the worktree `.venv` with `agent-heavy`.
  - `present` reads retained files only.
- **Pure water.** [decomposition.json](decomposition.json) `water` against [IAPWS-95](iapws95-water.csv) ([provenance](iapws95-provenance.json); same module bytes as `density-cp-160`):
  - 298.15–368.15 K at 101325 Pa;
  - 298.15–393.15 K at 0.3 MPa.
- **Pure liquid MEA.** 298.15–393.15 K at 101325 Pa, split into ideal-gas and residual parts. The two sources were acquired for this issue ([sources](pure-mea-sources.csv), [provenance with PDF hashes, methods and uncertainty](source-provenance.json)):
  - **Maham et al. (1997)** (primary). Zotero `5NDWELSM`, Table 1 p.1747 and Table 2 Eq. 1: $c_p = 82.5 + 0.275\,T$ J mol⁻¹ K⁻¹, 299.1–397.8 K. Setaram C-80 heat-flow calorimeter, stated 0.9 %.
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

**The source disagreement lies entirely in the reference excess.** The pure-component references are common to both mixture sources, so the Hilliard–Concepción level difference appears only in the reference excess, as 0.17–0.18 kJ kg⁻¹ K⁻¹. Against Hilliard, the model excess is too high at every temperature. Against Concepción, it is too high below about 340 K and too low above.

![Heat capacity against temperature. (a) Pure water, model lines and IAPWS-95 points at 0.1 and 0.3 MPa. (b) Pure liquid MEA, model line and Maham 1997 (±0.9 %) and Chiu 1999 (±2 %) points. (c) Unloaded 30 wt% MEA–water, model line at Hilliard's composition and Hilliard, Concepción and Weiland points. (d) Excess heat capacity, model line and reference excess points for each mixture/pure-MEA source pair. Shading marks the 313.15–353.15 K slope interval. Model lines are retained 5 K evaluations; points are measurements or evaluated references.](heat-capacity-slope.png)

[plotted-values.csv](plotted-values.csv) retains every plotted value.

## Stage 2: not run to a fit

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

**a₁ is available at all 60 states.** One-iteration probes located the cause:
- fits with the 14 non-law coordinates on the same 354 rows run;
- fits with a₀ or s as law slots run;
- fits including a₂ stop.

**Where available, the Engine derivatives are correct.** They agree with central differences (h = 1 % of the bound) at unloaded Hilliard 313.15 and 333.15 K:
- a₂ within 1.3×10⁻⁹ relative;
- a₁ within 2.6×10⁻⁷ relative at 313.15, 333.15 and 353.15 K.

At 353.15 K the central difference for a₂ is −6.52×10⁶ J mol⁻¹ K⁻¹ per K⁻², and the Engine returns nothing.

**Disposition.** The owner chose (2026-11-09) to keep the issue's selection rule, not substitute a₁, and report F2–F4 as not run. The Engine use case (equilibrium Cp and its a₂ derivative) goes to the orchestrator to file.

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

## Falsifiers

| | Outcome |
|---|---|
| F1 | **Pass**: closure within 4.5×10⁻⁵ J mol⁻¹ K⁻¹, shares against both sources, excess the single carrier → Stage 2 |
| F2 | **Not run**: Engine refuses the a₂ equilibrium-Cp derivative (above) |
| F3 | **Not run**: same reason |
| F4 | **Not run**: same reason |

## Limits

- The Hilliard–Concepción level difference stays unresolved. It sits entirely in the reference excess.
- Hilliard's sample pressure is assumed to be 101325 Pa.
- Each reference excess combines three methods: the mixture calorimetry (Hilliard's DSC or Concepción's), IAPWS-95 water, and a heat-flow (Maham) or DSC (Chiu) pure-MEA measurement.
- The pure-MEA sources differ in level by about 0.7–1.3 % and in 313–353 K slope by 0.020 kJ kg⁻¹ K⁻¹. Both give the same carrier.
- The low pure-MEA level (about −8 %) is a separate discrepancy. This issue does not split it between the Zhang ideal-gas correlation and the residual; doing so routes to Design.
- The share rule's 0.5 threshold is a design choice.
- All results are at fixed final-set parameters; the shares are a decomposition of one record, not a fitted attribution.

## Files

- `stage2/p2/a6-spec.json` holds the #255 coordinates with MEA–water a₀ and s as law slots plus a₂.
- `stage2/p2/starts/` holds the converted final set and the converted #255 candidate.
- [logs](stage2/logs/) keeps every attempt:
  - `fit2-final-attempt-1-missing-origin.log`: the #255 driver takes coordinate origins from the specification's stored endpoint, which lacked the a₂ slot. The stored endpoint is now converted the same way, with a₂ = 0.
  - `fit2-final-attempt-2-engine-refusal.log`: the refusal above. The #255-candidate start was stopped before it began, because it would meet the same refusal.
- `fit2`, `assess2`, `select2` and `grid2` implement the rest of Stage 2 (penalty stage, retreat, #255 criteria 1–3, the #264 Cp tables and phase searches, F2–F4, selection, and the candidate's mixture sweep). Only `fit2` has run, and it stopped as above.
