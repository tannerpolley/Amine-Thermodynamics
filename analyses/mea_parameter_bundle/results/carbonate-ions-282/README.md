# Water–HCO₃⁻ and water–CO₃²⁻ anchored to sodium-salt osmotic data (issue 282): F1 passes as amended, F2 passes, MDEA pressures degrade

**Result.** With the water–HCO₃⁻ and water–CO₃²⁻ laws held at their salt-fitted values, one stable MEA record passes the #255 acceptance rules (F2). The optimizer drives MEAH⁺–HCO₃⁻ to its +1 bound and moves several other MEA-ion coordinates at the same time, which is consistent with the MEA-specific bicarbonate correction being taken up by that pair together with the other changed coordinates. The run does not isolate each coordinate's share. The record costs more than both references, and the shared laws make the MDEA pressures much worse.
- **F1 (salt reference).** It passes under the owner's 2026-11-09 amendment, without refitting:
  - NaHCO₃ AARD 0.163 % (≤ 1.5 %);
  - Na₂CO₃ AARD 5.111 % (≤ 6.5 %);
  - water–HCO₃⁻ at 313.15 K = 0.171 (< 0.5, not falsified).

  The water–Na⁺ and water–CO₃²⁻ intercepts sit on their −1 lower bounds. **Every result below is conditional on those two bound values.** Under F1 as first written, the run stopped here (PR #287); that record is kept.
- **Leverage (step 3).** With the salt laws substituted into the final set, the 307-row cost rises to 351.479. Setting MEAH⁺–HCO₃⁻ to +0.1 or −0.1 changes that cost by +15.445 and −15.299, against the 0.1 threshold. The coordinate has leverage and is fitted.
- **MEA refit (step 4).**
  - Two starts were qualified as retreat anchors. The substituted final set is admissible, so it is the anchor. The substituted #255 candidate is not, and the Engine refused its initial fit evaluation: **that start gives no candidate**.
  - From the substituted final set, both penalty stages converge with 6 enforced states still descending. The retreat finds an admissible point at t = 0.975693.
  - **Cost 150.0747**: +1.564 against the #255 candidate's 148.5105 and +1.191 against the final set's 148.8833 on the same wheel and inputs.
- **F2 (step 5): passed.** There is 0 resolved descent at all 1903 enforced, 576 offset and 162 census states, and every #255 group criterion is met.
  - MEAH⁺–HCO₃⁻ is **0.9757** at the candidate and **+1.0, the upper bound,** at the stage-1 endpoint.
  - Carbamate–MEAH⁺ (−1) and the R5 enthalpy-shift total (+10 000 J/mol) stay on their bounds.
- **Pool comparison (step 5).** The refit covers 17 of 19 Matin–Böttinger pool points at each of the three pressures, against 18 of 19 for the final set. The carbonate share F_C mean calc/obs rises from 0.073 to 0.103.
- **MDEA transfer (step 6).** At fixed MDEA-specific parameters, the four pressure AARDs rise from 19.1–28.3 % to 111–172 % under either R2 law, overpredicting at nearly every row (102–108 of 108). The MDEA-specific parameters were fitted with the old shared values, so this measures the mismatch, not the salt values.

Nothing is adopted: `selected-current-best-parameters.json`, the Engine pin, `docs/scientific/latex/` and `analyses/_cse-manuscript.json` are unchanged.

This is calibration and numerical verification against model-derived salt reference values (Peiper & Pitzer's Pitzer-model tables) and the 307 MEA rows. It is not validation, and passing F2 does not establish a physical MEAH⁺–HCO₃⁻ value.

## Inputs and method

- **Engine.** `main` `bc7794731e94be961d16028d3f4880c6718a93ad`, wheel SHA-256 `8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069`, installed in this worktree only. Every JSON result records the wheel.
- **Script.** [`carbonate_ions_282.py`](../../scripts/carbonate_ions_282.py): `qualify | salt | amend | scan | leverage | anchors | fit <final|candidate> | assess <final|candidate> | select | compare | mdea`. It reuses `stable_refit_255.py` by import. This build copied two sets of lines from #283's copy of that file, with identical text:
  - **retreat screening.** `admissible(..., suspects)` first searches the states that failed at the previous step, so a rejected step costs a few searches instead of a full 1903-state grid. The admissibility decision and t are unchanged.
  - **pool sizing.** Process pools and optimizer workers are sized from `AGENT_HEAVY_CORES`, the owner's 3-core cap per job (2026-11-09). Two retained runs did not use that sizing and asked for one worker per CPU: the salt fits, run before the cap, and the MDEA transfer, run inside `agent-heavy`'s 3-core quota (see the producer copy in `mdea-transfer/producers/`). The script now sizes both from `AGENT_HEAVY_CORES`; neither was rerun.

  Every step after `salt` runs only when `salt/summary.json` records F1 as passed. Each heavy step ran under `agent-heavy` at 3 cores; see [logs/](logs/).
- **Water and electrolyte model.** The selected record (`00e77608…`) reduced to water, Na⁺, Cl⁻, HCO₃⁻, CO₃²⁻ and OH⁻.
  - Na⁺ (2.8232 Å, 230 K) and Cl⁻ (2.7560 Å, 170 K) come from Held 2014 Table 2, strategy 2. They follow the record's ion conventions: packing diameter 0.88σ, Debye–Hückel diameter σ, Born diameter σ (a design choice), solvation factor 1 and ionic-region relative permittivity 8.
  - Cross interactions from Held 2014 Table 3: Na⁺–Cl⁻ 0.317, Na⁺–HCO₃⁻ −0.514, Na⁺–CO₃²⁻ −1.000 and Na⁺–OH⁻ 0.649. Cl⁻–water is −0.25.
  - HCO₃⁻, CO₃²⁻, OH⁻ and every other ion–water value are the record's.
- **Laws.** Each fitted law is $k(T)=a_0+a_1(T-298.15\ \mathrm K)$, in the Engine's `polynomial-plus-reciprocal-temperature` form with no 1/T term.
  - Water–Na⁺ holds Held's slope, $a_1=-0.007981$ K⁻¹.
  - Bounds (design choices): $a_0\in[-1,1]$ and $a_1\in[-0.02,0.02]$ K⁻¹. Starts are Held's values at 298.15 K: 0.00046, 0.00 and −0.25.
- **Data** ([inputs/](inputs/)).
  - [Hamer & Wu 1972 Table 16](inputs/hamer-wu-1972-nacl.csv): NaCl at 298.15 K, 0.1–1.0 mol/kg; residual scale 0.003.
  - [Peiper & Pitzer 1982 Table 6(a–e)](inputs/peiper-pitzer-1982-table6.csv): rows at 0.01–1.0 mol/kg nominal and 278.15–318.15 K, residual scale 0.01. That is 45 NaHCO₃ and 45 Na₂CO₃ fitted rows, plus 45 mixed rows as a comparison.
- **Transcription.** Both tables were transcribed from the page images of the Zotero PDFs, not from the Markdown reading copies. Hashes:
  - Peiper & Pitzer `8d713ff2…9702` (attachment X8GEDSJ2);
  - Hamer & Wu `a20e0029…4ca6` (attachment 5RS9QAMK).
- **Transcription checks.**
  - Each Peiper & Pitzer row is checked against its own printed water activity: $\phi=-\ln a_w/(M_w\sum_j m_j)$ agrees within print rounding at 133 of 135 rows. The other two, NaHCO₃ at 278.15 K and 0.1 and 0.8 mol/kg, sit at 1.10× and 1.07× the rounding bound. Both match the PDF text layer, so they are kept as printed.
  - The 45 NaHCO₃ rows also match the independent #122 transcription, `data/reference/MEA/observations/ionic_activity/peiper_pitzer_1982_nahco3_osmotic.csv`, exactly.
- **Observable.**
  - NaCl uses the Engine's two-ion formula path, `electrolyte(kind="osmotic_coefficient")`.
  - Carbonate rows use the Engine's `mixture_osmotic_coefficient` at the printed equilibrium ionic composition, with Na⁺ nominal and the minor anion set by charge balance (CO₃²⁻ for NaHCO₃ rows, OH⁻ for Na₂CO₃ rows).
  - The largest charge adjustment is 4×10⁻⁴ mol/kg.
  - Dissolved CO₂ is removed as ideal: $\phi_\mathrm{ion}=(\phi\sum m-m_\mathrm{H_2X})/\sum_\mathrm{ions}m$. Its largest share of Σm is 0.78 %, at 318.15 K and 1.0 mol/kg NaHCO₃.
  - Six mixed rows are unavailable, because charge closure gives a negative OH⁻.
  - At the fitted laws the formula path and the full-composition path give the same NaCl Φ within 2×10⁻¹⁶.
- **Cascade.** Each fit uses the Engine's least squares (`regression.fit`), run in order:
  - (1a) water–Na⁺ $a_0$ on NaCl;
  - (1b) water–HCO₃⁻ $a_0,a_1$ on NaHCO₃, with (1a) held;
  - (1c) water–CO₃²⁻ $a_0,a_1$ on Na₂CO₃, with (1a) and (1b) held.

  F1 is then scored on one combined document that holds all three final laws.

**Qualification (Method 1)** ([qualification/summary.json](qualification/summary.json)): the final set and the #255 candidate replay on this wheel with relative row and cost differences of 0.0 against the retained #255 rows (`qualification/final-replay.json`, `wide/replay.json`): 307/307 rows available, costs 148.883260 and 148.510546. Passed.

## Salt fits

| Fit | Iterations | Cost (start → end) | Endpoint | On a bound | Replay vs fit |
|---|---:|---|---|---|---:|
| [1a water–Na⁺](salt/1a-sodium.json) | 2 | 5035.6 → 110.80 | $a_0=-1.000$ | $a_0$ (lower) | 0 |
| [1b water–HCO₃⁻](salt/1b-bicarbonate.json) | 5 | 5.582 → 0.6067 | $a_0=0.11173$, $a_1=3.9312\times10^{-3}$ K⁻¹ | none | 1.3×10⁻¹¹ |
| [1c water–CO₃²⁻](salt/1c-carbonate.json) | 10 | 1025.3 → 411.79 | $a_0=-1.000$, $a_1=1.9631\times10^{-3}$ K⁻¹ | $a_0$ (lower) | 1.1×10⁻¹¹ |

**F1 on the combined document** ([salt/summary.json](salt/summary.json), [φ residuals](salt/phi-residuals.csv)):

| Rows | n | AARD % | Max % | AARD by T (278 / 288 / 298 / 308 / 318 K) | Gate |
|---|---:|---:|---:|---|---|
| NaCl, 298.15 K | 10 | 1.514 | 1.68 | — | no AARD gate; $a_0$ on bound fails F1 |
| NaHCO₃ | 45 | **0.163** | 0.47 | 0.225 / 0.121 / 0.129 / 0.113 / 0.228 | ≤ 1.5 %: pass |
| Na₂CO₃ | 45 | **5.111** | 8.28 | 4.62 / 5.13 / 5.36 / 5.35 / 5.09 | ≤ 1.5 %: **fail** |
| mixed (comparison) | 39 | 2.561 | 6.30 | 3.42 / 2.61 / 2.43 / 2.37 / 2.23 | not fitted |

**F1 gates, as written and as amended** ([salt/summary.json](salt/summary.json): `gates_as_written`, and `gates`, which the script's MEA guard reads). The amendment is the issue body's "Owner amendment to F1 (2026-11-09)". It sets Na₂CO₃ AARD ≤ 6.5 %, the worst comparable univalent-cation/bivalent-anion case in Held 2014 Table 5 (strategy 2, 298.15 K: Na₂SO₄ 2.41 %, K₂HPO₄ 4.95 %, Na₂HPO₄ 6.43 %). Coefficients on a bound become stated limits rather than gate failures. No fitted number changes; the amended gates are re-scored from the retained scores (`amend`, no fit, no prediction).

| Gate | Value | As written (first build) | Amended (owner, 2026-11-09) |
|---|---:|---|---|
| NaHCO₃ AARD | 0.163 % | ≤ 1.5 %: pass | ≤ 1.5 %: pass |
| Na₂CO₃ AARD | 5.111 % | ≤ 1.5 %: **fail** | ≤ 6.5 %: pass |
| Coefficients interior | 1a and 1c $a_0$ at −1 | **fail** | stated limits, not a gate |
| Water–HCO₃⁻ at 313.15 K | 0.171 | < 0.5: not falsified | < 0.5: not falsified |
| **F1** | | **failed** | **passed** |

**Stated limits carried by every later result.** Two salt-fit intercepts sit on their −1 lower bounds:
- water–Na⁺ $a_0$, against Held's ≈ 0.0005 at 298.15 K;
- water–CO₃²⁻ $a_0$.

The held water–HCO₃⁻ and water–CO₃²⁻ laws were fitted with water–Na⁺ there, so the leverage check, the MEA refit, F2 and the MDEA transfer below are all conditional on these two bound values.

**Fitted laws** ([salt/laws.csv](salt/laws.csv), 278.15–393.15 K in 5 K steps):

| Law (about 298.15 K) | About the record's 313.15 K | Value at 313.15 K |
|---|---|---:|
| water–Na⁺: $-1.000-0.007981\,(T-298.15)$ | $-1.11972-0.007981\,(T-313.15)$ | −1.1197 |
| water–HCO₃⁻: $0.11173+3.9312\times10^{-3}(T-298.15)$ | $0.17069+3.9312\times10^{-3}(T-313.15)$ | **0.1707** |
| water–CO₃²⁻: $-1.000+1.9631\times10^{-3}(T-298.15)$ | $-0.97055+1.9631\times10^{-3}(T-313.15)$ | −0.9706 |

The comparison curves are Held 2014 (HCO₃⁻ 0.00, CO₃²⁻ −0.25) and Wangler 2018 Table 6, read as polynomial orders. At 313.15 K, Wangler gives −0.100; the final set's bicarbonate–water k is 0.727 and the #255 candidate's 1.0. Extrapolated, the 1b law reaches 0.328 at 353.15 K and 0.485 at 393.15 K, against Wangler's −0.300 and −0.700.

![Left three panels: Peiper & Pitzer and Hamer & Wu osmotic coefficients on the ionic basis (points) and the combined-document model at the same rows (lines), by temperature. Right: fitted water–anion laws over 278–393 K with the fitted range shaded, against Held 2014, Wangler 2018, the final set and the #255 candidate.](salt/phi-molality.png)

**Why two intercepts sit on their bounds (diagnostics from the first build, not a fix).**
- **Direction toward the bound.** At 298.15 K, lowering the water–Na⁺ or water–CO₃²⁻ intercept through the five tested values (−1, −0.5, 0, 0.5 and 1), with the other coefficients fixed, raises φ toward the reference values at every sampled molality. This supports the direction toward the lower bound for those rows; it does not establish global optimality of the full temperature-dependent fit. ([salt/sensitivity.json](salt/sensitivity.json), `scan`, no fit.)
  - NaCl at 0.4 mol/kg: φ goes 0.790 → 0.905 as water–Na⁺ $a_0$ goes from +1 to −1, against 0.920 observed.
  - Na₂CO₃ at 0.1 mol/kg and 298.15 K: water–CO₃²⁻ $a_0$ moves φ only from 0.748 to 0.764, against 0.817.
- **Na₂CO₃ is low before k matters.**
  - The deficit is −1.1 % at 0.01 mol/kg, where k has almost no lever.
  - It grows to −8.1 % at 0.2 mol/kg, then shrinks to −4.0 % at 1.0 mol/kg.
  - This is consistent with the 2:1 electrostatic and Born treatment on this water, and with the fixed Na⁺–CO₃²⁻ = −1.000 (a bound value in Held 2014), carrying most of the error rather than water–CO₃²⁻. That is an inference: no term-by-term decomposition was run.
- **NaCl stays low at the bound.** It is −1.06 % at 0.1 mol/kg and −1.68 % at 0.5 mol/kg with water–Na⁺ at −1.
- **The water-model mismatch.** The record's water (m = 1.253, u/k = 432.4 K, ε^AB/k = 1757 K) differs from the Fuchs water that Held's ion parameters were fitted with. The Born-diameter choice for Na⁺/Cl⁻ is not from a source.

**Consequence.** The 1b water–HCO₃⁻ law (0.171 at 313.15 K) fits NaHCO₃ well, but it was fitted with water–Na⁺ pinned at its bound. Under the amendment that is a stated limit, not a stop. The salt-reference design is unchanged.

## Step 3: leverage of MEAH⁺–HCO₃⁻ (no fit)

[leverage.json](leverage.json). The start is the final set with water–HCO₃⁻ and water–CO₃²⁻ replaced by the salt laws, re-expressed about the record's 313.15 K: water–HCO₃⁻ $0.17069+3.931\times10^{-3}(T-313.15)$ and water–CO₃²⁻ $-0.97055+1.963\times10^{-3}(T-313.15)$. All 307 rows are available at each point.

| MEAH⁺–HCO₃⁻ | 307-row cost | Change | Norm of weighted-residual change |
|---:|---:|---:|---:|
| 0 | 351.4786 | — | — |
| +0.1 | 366.9232 | **+15.4446** | 0.789 |
| −0.1 | 336.1801 | **−15.2985** | 0.811 |

The statistic is max(|C(+0.1)−C(0)|, |C(−0.1)−C(0)|) = 15.445 ≥ 0.1, so the coordinate is not negligible and enters step 4. The central cost derivative is 153.7 per unit k. Fitted CO₂ partial pressures carry +14.69/−14.56 of the change, fitted phase mole fractions +0.83/−0.84, and every other group less than 0.14.

Substituting the laws alone raises the final set's cost from 148.883 to 351.479. Holding water–HCO₃⁻ at the salt value removes the fitted compensation, and the MEA rows must recover it elsewhere.

## Step 4: MEA refit

**Anchor qualification** ([anchors.json](anchors.json)). Each substituted start was checked on the unchanged 1903 enforced states and the 307 objective rows, with both salt laws held. The retreat in this script never returns the anchor itself: if no admissible point with t > 0 is found, the run has no candidate.

| Substituted start (MEAH⁺–HCO₃⁻ = 0) | Enforced states available | Resolved descent | 307 rows available | Cost | Admissible |
|---|---:|---:|---|---:|---|
| final set | 1903 / 1903 | 0 | yes | 351.4786 | **yes: the anchor** |
| #255 candidate | 1901 / 1903 | 0 | yes | 505.2343 | no |

The two states unavailable at the substituted candidate are `dense|0.25|333.15|1e-05|{1.05,3.0}`, which are 25 wt% MEA, 333.15 K and CO₂-free.

**Coordinates.** These are the #255 primary fit's (`a6`), minus water–HCO₃⁻, which is held. MEAH⁺–HCO₃⁻ is added as a constant k with bounds [−1, 1], scale 0.1 and start 0 ([a6-spec.json](a6-spec.json)). The penalty stages (s = 10⁻², then 3×10⁻³), the stop rule, the retreat and the lower-cost selection are #255's.

**Wall-time budget.** The #255 per-stage limit of 7200 s was sized for 32 cores. Under the 3-core cap the owner set 76 800 s (7200 × 32/3) for these two refits only, with every other control unchanged. Each stage ended on convergence, well inside that budget.

**Execution record.**
- The first final-start attempt was stopped by the harness's 2-hour shell limit, one second after its then-7200 s budget expired and before it wrote any output.
- The second attempt was killed by a machine reboot at about 14:42.
- Both logs are kept empty or partial under `logs/fit-final-attempt-*`. The retained run is `logs/fit-final.log`.

| Start | Stage | Status | Iterations | Wall time / s | Total cost (start → end) | 307-row cost | Enforced descent at endpoint |
|---|---|---|---:|---:|---|---:|---:|
| substituted final set | 0 (s = 10⁻²) | converged | 30 | 6736 | 351.479 → 149.974 | 149.9726 | 6 / 1903 |
| substituted final set | 1 (s = 3×10⁻³) | converged | 6 | 1861 | 149.989 → 149.984 | 149.9736 | 6 / 1903 |
| substituted #255 candidate | 0 | **initial_evaluation_failed** | 0 | 185 | — | — | — |

- **The candidate start.** The Engine refused the initial evaluation with first numerical failure `Stop.left_domain`. Its message reads "stalled: residual 1.10×10⁻⁷ against EQUILIBRIUM_ROW_RESIDUAL 1e-10 after 14 iterations". The failing row is the enforced state `dense|0.25|333.15|1e-05|1.05`, the same one the anchor qualification found unavailable. No stage returned an endpoint, so [candidate/retreat.json](candidate/retreat.json) records "no stage returned an available 307-row endpoint". **This start gives no candidate.** No other start, retry or fallback was added.
- **The final start.** Both stages converged. The stage endpoints replay their 307 predictions within 3.0×10⁻¹³ and 8.3×10⁻¹³. After stage 1 the stop rule had no further stage, so the run went to the retreat.

**Retreat** ([final/retreat.json](final/retreat.json)). It runs on the straight segment from the refreshed anchor, which is still admissible, to the stage-1 endpoint.
- Steps t = 1, 0.99 and 0.98 fail, with 6, 4 and 2 descent states; t = 0.97 is admissible.
- Ten bisection steps follow. Admissibility is not monotone in t, as in #255. The result is **t = 0.975693, at 307-row cost 150.0747**.
- Six of the 14 retreat points were rejected by the suspect screen alone, without a full grid.

**Coordinates** (final set → candidate; change in optimizer scales):

| Coordinate | Final set | Candidate | Change / scale | Stage-1 endpoint |
|---|---:|---:|---:|---|
| **MEAH⁺–HCO₃⁻ k** | — (0) | **0.97569** | +9.76 | **+1.0 (upper bound)** |
| MEAH⁺–water k | −0.5 (bound) | −0.11113 | +38.9 | |
| carbamate–water k | −0.00366 | −0.23152 | −22.8 | |
| MEAH⁺–water reciprocal-T slope / K | −41.62 | −3.687 | +3.8 | |
| MEAH⁺ segment diameter / Å | 5.35 | 4.6668 | −6.8 | |
| carbamate segment diameter / Å | 4.8661 | 5.4828 | +6.2 | |
| MEAH⁺ Born diameter / Å | 5.0 (bound) | 4.2865 | −7.1 | |
| carbamate Born diameter / Å | 5.0 (bound) | 4.99981 | −0.002 | |
| MEAH⁺ dispersion energy / K | 177.89 | 208.11 | +3.0 | |
| carbamate dispersion energy / K | 207.22 | 176.57 | −3.1 | |
| R5 aₖ / K | 3354.10 | 3115.82 | −3.0 | |
| MEA–water k; reciprocal-T slope / K | −0.0899; −8.057 | −0.0880; −5.540 | +0.19; +0.25 | |
| carbamate–MEAH⁺ k | −1 (bound) | −1 (bound) | 0 | −1 (bound) |
| R2 / R5 enthalpy-shift totals / J mol⁻¹ | −1363.9 / +10 000 | +1039.2 / **+10 000 (bound)** | | +1099.1 / +10 000 |

- **R2 law.** It changes from $a$ = 23.5855, $b$ = −11928.06 K to $a$ = 24.5085, $b$ = −12217.09 K ($c$ = −36.7816 unchanged). ln K is unchanged at 313.15 K and rises by 0.105 at 353.15 K and 0.188 at 393.15 K ([mdea-transfer/r2-laws.json](mdea-transfer/r2-laws.json)).
- **Coordinates on bounds.** At the candidate: carbamate–MEAH⁺ (−1) and the R5 shift total. At the stage-1 endpoint: MEAH⁺–HCO₃⁻ (+1) as well.

## Step 5: assessment (F2) and comparisons

**Acceptance against the final set** (same wheel and inputs; [final/assessment.json](final/assessment.json)):

| Group | n | Final set AARD % (within 2s) | Refit candidate | Rule | Pass |
|---|---:|---:|---:|---|---|
| fitted CO₂ partial pressure | 47 | 11.863 (47) | 12.149 (47) | rise ≤ 2 points (+0.287) | yes |
| Kiepe pressure | 39 | 2.667 (39) | 2.667 (39) | rise ≤ 2 points (0.000) | yes |
| fitted phase mole fraction | 94 | 7.103 (94) | 7.563 (93) | rise ≤ 2 points (+0.460) | yes |
| restored species | 7 | 9.002 (7) | 9.517 (7) | rise ≤ 2 points (+0.515) | yes |
| Jakobsen ratio | 6 | 17.514 (4) | 15.791 (4) | rise ≤ 2 points (−1.724) | yes |
| loaded density | 47 | 0.177 (44) | 0.151 (47) | count kept; AARD/RMSE ×0.853/×0.823 | yes |
| CO₂-free density | 5 | 0.028 (5) | 0.029 (5) | ×1.053/×1.050 | yes |
| fitted heat of absorption | 8 | 1.877 (8) | 1.983 (8) | ×1.056/×0.993 | yes |
| heat capacity | 4 | 2.846 (3) | 2.366 (3) | ×0.831/×0.875 | yes |
| Cai MEA–water VLE (reported only) | 50 | 1.480 (36) | 1.483 (36) | — | — |

**Stability at the candidate.** These are fresh Full searches.

| States | Count | Available | Resolved descent |
|---|---:|---:|---:|
| enforced | 1903 | 1903 | 0 |
| offset (held out) | 576 | 576 | 0 |
| census, liquid + vapor (held out) | 162 | 162 complete | 0 |
| the 5 #255-excluded states | 5 | 3 (the two 25 wt%, 313.15 K CO₂-free states unavailable; the 323.15 K pair and the 45 wt%, 383.15 K state are available) | 0 |

**F2: passed** ([selected.json](selected.json); only the final-start run has a candidate).
- The 307-row cost is 150.0747. That is +1.5641 against the #255 candidate's 148.5105 and +1.1914 against the final set's 148.8833. F2 has no cost criterion; the cost is reported.
- One fitted phase mole fraction leaves the 2s band (94 → 93). The AARD rule for that group does not count it.

**Carbonate and pool comparisons** (#266's retained records; compared, never fitted; [comparisons.json](comparisons.json)). At the final set, the `compare` command reproduces two references:
- #266's envelope count of 18/19 and its Matin AARD of 67.4145 %;
- the ten A7 F_C predictions, within 3×10⁻¹⁶ (mean calc/obs 0.0727222).

| Quantity | Final set | Final set with salt laws (no refit) | Refit candidate |
|---|---:|---:|---:|
| Matin points inside the Matin–Böttinger envelope, at 101325, 500000 and 2500000 Pa each | 18/19 | 17/19 | **17/19** |
| points outside (loading, mol CO₂/mol MEA) | 0.531 | 0.505, 0.531 | 0.505, 0.531 |
| Matin pool AARD at 101325 Pa | 67.41 % | 88.64 % | 69.63 % |
| Jakobsen pool AARD (24 states) | 22.00 % | 41.10 % | 25.79 % |
| F_C mean calc/obs (the 10 A7 states) | 0.0727 | 0.0072 | **0.1032** |
| S_pool mean calc/obs (24 states) | 0.1036 | 0.0563 | 0.0795 |
| Jakobsen 011 S_pool (source 0.75) | 0.0351 | 0.0122 | 0.0523 |
| Jakobsen 015 S_pool (source 0.0307) | 1.36×10⁻⁵ | 3.42×10⁻⁶ | 5.87×10⁻⁵ |

Both points outside the envelope are below its lower edge, at the two highest Matin loadings. The refit moves the carbonate share toward the sources, though it stays an order of magnitude low, and loses one high-loading pool point. Jakobsen 2005 warns that a species below about 10 % of a common NMR signal is hard to quantify; the carbonate share is a comparison only.

## Step 6: MDEA transfer

Method:
- **Producer.** #267's `transfer_probes.py` runs on A3 and B1. Water–HCO₃⁻ and water–CO₃²⁻ are replaced in each MDEA parameter document by the salt laws, with every other pair and all MDEA-specific parameters unchanged; [mdea-transfer/producers/](mdea-transfer/producers/) holds the substituted copy.
- **Cases.** The frozen final-set R2 law, then the refit candidate's R2 law.
- **Reference column.** It is #255's retained same-wheel final-set run (k = 0.727, frozen R2).

[mdea-transfer/summary.json](mdea-transfer/summary.json):

| Pressure AARD % (rows) | Final set | Salt laws, frozen R2 | Salt laws, refit R2 |
|---|---:|---:|---:|
| A3 Xiao (20) | 20.4 | **147.1** | **152.8** |
| A3 Ermatchkov (88) | 26.2 | **119.7** | **111.0** |
| B1 Xiao (20) | 28.3 | **137.7** | **143.0** |
| B1 Ermatchkov (88) | 19.1 | **172.2** | **158.6** |

- **Pressures.** All 108 states are available in every case, and the phase checks find no witness and nothing unresolved. The signed mean error equals or nearly equals the AARD: the model overpredicts at 102–108 of the 108 rows in each case, with mean ln(calc/obs) 0.58–0.92. Every case exceeds the MDEA workflow's two-AARD-point criterion by far.
- **What causes the rise.** No case separates water–HCO₃⁻ from water–CO₃²⁻; both laws change together.
- **The baseline.** The A3 and B1 MDEA-specific coordinates were fitted with water–HCO₃⁻ = 0.727 and water–CO₃²⁻ = −0.25. This rise therefore means those coordinates would need refitting for new shared values (out of scope). It does not refute the salt values.

| MDEA heat, 60 wt%, 1.121 MPa, 30-point grid / kJ mol⁻¹ | Final set | Salt laws, frozen R2 | Salt laws, refit R2 |
|---|---:|---:|---:|
| A3, 333.15 K | −76.27 | −50.00 | −48.06 |
| B1, 388.71 K | −64.13 | −39.35 | −40.35 |
| B1, 333.15 K | unavailable (Engine #1073) | unavailable | unavailable |

The 60- and 120-point grids agree with the 30-point values within 6×10⁻⁸ J/mol.

## Limits

- The Peiper & Pitzer values are Pitzer-model reference values (their §§2–4), not raw measurements.
- Dissolved CO₂ is treated as ideal in the φ conversion, and the printed compositions are charge-closed.
- With one chloride salt, the water–anion values depend on:
  - the Cl⁻–water = −0.25 convention;
  - Held's Na⁺ slope;
  - the Na⁺/Cl⁻ Born diameter.
- Na⁺–HCO₃⁻, Na⁺–CO₃²⁻ and Na⁺–OH⁻ are Held values fitted with the Fuchs water.
- The salt laws are fitted at 278–318 K; their values above 318 K, used throughout the MEA and MDEA calculations, are extrapolations.
- **Every result from step 3 on is conditional on two intercepts sitting on their −1 bounds:**
  - water–Na⁺, against Held's ≈ 0.0005 at 298.15 K;
  - water–CO₃²⁻.

  F1 passes only under the owner's 2026-11-09 amendment.
- **The refit.**
  - It is an admissible retreated record obtained from one converged penalty-fit run. It was reached by interpolation and bisection toward the fit endpoint, not optimized at that point, so local optimality is not established. The other start is refused by the Engine, so the two-start comparison has one member.
  - Three coordinates sit on bounds at the stage-1 endpoint and two at the candidate.
  - MEAH⁺–HCO₃⁻ reaches its +1 bound, and the candidate value 0.9757 is set by the retreat factor t. F2 therefore shows that a stable record exists with salt-anchored water–anion laws. It does not establish a physical MEAH⁺–HCO₃⁻ value.
- **Stability.** The searches are finite, at declared states, not a global certificate.
- **The acceptance rules** are repository policy.
- **Budget.** The 3-core cap changed only the wall-time budget, scaled by 32/3 and not binding. Worker counts do not change the calculation.
- **The carbonate share** is limited by common-signal NMR quantification. The Böttinger pressures for the envelope are scenarios, not measurements.
- **The MDEA transfer** holds the MDEA-specific parameters fixed. It does not separate the bicarbonate and carbonate laws, and it is not a refit.
