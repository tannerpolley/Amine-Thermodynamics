# CO2 partial-pressure misfit on the 79 solved-pressure calibration states

2026-09-23. A bounded diagnosis. No physics, parameters or Engine code were changed.

## Question

The adopted record `selected-current-best-parameters.json` (SHA-256 `868a5018…fcb7be`) misses
the packet's own CO2 partial pressures. The RMS of ln(pred/obs) is 0.59 over 79 states. Which
dominates the misfit: (a) the data, (b) the reaction/reference chain, or (c) the fitted parameters?

## Outcome

**Mainly (c), with a measurable data floor from (a); (b) is refuted as the dominant cause.**

- **The shape comes from the model.** About 79% of the residual sum of squares is one loading
  pattern with no temperature trend. At every temperature from 40 to 120 °C, the model
  under-predicts pCO2 below loading 0.2 (mean ln −0.21). It over-predicts pCO2 by about 2× at
  loadings 0.3–0.5 (mean +0.75). It under-predicts again above 0.55 (mean −0.51).
- **No change to the R2/R4/R5 constants can make that shape.** Within a nominal source-sized
  bound of ±0.3 in ln K, the best correction only moves the RMS from 0.59 to 0.56. Even
  unbounded shifts of about −5.5 in ln K (a factor of about 250 in K) still leave an RMS of 0.47.
- **The fit did not target these states.** The fit that produced the adopted reaction values
  scored only 5 pCO2 rows, all Jou 1995 at 80 or 120 °C. Its coordinates were reaction
  enthalpies that preserve ln K at the 313.15 K pivot. It therefore could not act on the
  40 °C residuals, which are the largest.
- **The data set a floor of about 0.3 in ln.** Hilliard's observed pCO2 sits +0.17 in ln above
  Jou's at the same temperature and loading. The sources state a 2% relative loading
  uncertainty. On the steep part of the curve, that alone moves ln pCO2 by 0.28–0.31.
- **The migration does not explain the misfit.** The Engine wheel, dispersion rule and adapter
  changes are not the cause. Today's predictions match the adoption-time replay to an RMS of
  0.007 in ln.

## Identity and reproduction

| item | value |
|---|---|
| Engine wheel | `e9fb8a47e2f98a4f45c66b001836a4de68c7306ee20a9f50a891e940a2413e62` (main `7fa8aaf4`) |
| parameter record | `868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be` |
| state packet | `e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba` |
| producer | `../../../scripts/diagnose_pco2_misfit.py` (its SHA-256 is written into every CSV row) |
| inputs reused | `../reaction-temperature-fit/cold-start-sweep/cold-start-sweep.csv` (`main-cb16` rows); `../../reaction-temperature-fit/full-validation-targets.csv` (adoption-time replay, wheel `40fba7cf…`) |

Command, run single-threaded:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python analyses/mea_parameter_bundle/scripts/diagnose_pco2_misfit.py
```

The run makes 316 fresh solves: each of the 79 states at the adopted constants, then once each
with ln K raised by +0.05 for R2, R4 and R5. All solves are cold packet starts through
`shared_evaluation.evaluate_state`. The solve cache is kept in `/tmp`.

Coverage: all 79 base solves evaluated. Three perturbed solves are `non_evaluable`: 0126 for R4
and R5, and 0145 for R5. Their sensitivities are left blank, so the linear-correction rows use 77
states.

Files:

- `pco2-misfit-states.csv`: one row per state. Columns include the observed value, the fresh,
  sweep and adoption-time predictions, ln(pred/obs), d ln pCO2 / d ln K for R2/R4/R5, the
  Hilliard-over-Jou interpolation, the pCO2 effect of the 2% loading uncertainty, and the residual
  left after each linear correction.
- `pco2-misfit-summary.csv`: every aggregate quoted below.

## Evidence by hypothesis

The three kinds of evidence are kept separate:

- **Numerical verification:** solver agreement and reproduction.
- **Prediction:** the model's output compared with data.
- **Physical validation:** this work performs none, because every state is a calibration row.

### (c-i) Wheel, dispersion rule or adapter changed the model: **refuted** (numerical verification)

- The fresh solves reproduce the `main-cb16` sweep to an RMS of 2.8e-12 in ln.
- They match the adoption-time full replay (old adapter, wheel `40fba7cf…`) with mean ln −0.0030
  and RMS 0.0070 over 78 states. `vle_obs_0149` is absent from that replay.
- The ~0.3% offset is consistent with the R1/R3 shifts that the replay scored but the selected
  document omits (see `interpretation_correction` in `adoption-receipt.json`). It is negligible
  next to the misfit.
- The misfit therefore already existed at adoption. The adoption record agrees: its 143-row
  calibration pressure cohort had log10 RMSE 0.2366, which is ln RMSE 0.545.

### (c-ii) The fit did not target these rows: **supported** (retained record)

- `screen-receipt.json` scored 33 common targets: 5 pressure rows, 22 speciation rows and 6 heat
  rows. The 5 pressure rows are Jou `vle_obs_0206/0211/0227/0228/0232`, at 80 and 120 °C.
- The three families were given equal weight.
- The fit coordinates were reaction-enthalpy shifts at the 313.15 K pivot, which keep ln K at
  40 °C unchanged (`README.md` in `../../reaction-temperature-fit/`).
- So the loading dependence at 40–60 °C comes from the pre-existing residual EOS and ionic
  parameters, not from any pCO2 objective.

### (c-iii) The residual EOS/ionic model makes the wrong loading shape: **supported as dominant** (prediction)

Mean ln(pred/obs) by loading bin and temperature:

| loading | 40 °C | 60 °C | 80 °C | 100 °C | 120 °C |
|---|---:|---:|---:|---:|---:|
| < 0.2 | −0.19 | −0.26 | −0.28 | −0.27 | −0.07 |
| 0.2–0.3 | +0.28 | +0.37 | – | – | – |
| 0.3–0.5 | +0.78 | +0.94 | +0.68 | +0.72 | +0.54 |
| 0.5–0.55 | +0.31 | +0.21 | +0.37 | – | +0.12 |
| ≥ 0.55 | −0.88 | −0.46 | −0.61 | +0.03 | −0.48 |

Removing the five loading-bin means takes away 79% of the residual sum of squares. The RMS drops
from 0.59 to 0.27. Removing temperature means takes away 12%; removing source means takes away
13%.

The pattern has the same signs in both sources and at every temperature. The largest single
misses are:

- Jou 40 °C, loading 0.642: −1.62.
- Jou 60 °C, loading 0.389: +1.26.
- Hilliard 40 °C, loading 0.400: +1.03.

### (b) Reaction constants, R4/R5 extrapolation or the reference chain: **refuted as dominant** (prediction)

**Temperature.** Nothing grows with temperature. The misfit is largest at 40 °C, which is
inside every source range (293–323 K), and smallest at 120 °C (RMS 0.41). Extrapolating R4/R5
beyond 323 K would give a temperature-growing error; that is not seen.

**Sensitivities.** The mean d ln pCO2 / d ln K in each loading bin:

| loading | R2 | R4 | R5 |
|---|---:|---:|---:|
| < 0.2 | −1.00 | +0.92 | +1.02 |
| 0.2–0.3 | −1.00 | +0.81 | +1.10 |
| 0.3–0.5 | −0.96 | +0.31 | +1.05 |
| 0.5–0.55 | −0.92 | −0.24 | +0.96 |
| ≥ 0.55 | −0.84 | −0.49 | +0.84 |

R2 and R5 act almost uniformly across loading, so they only shift pCO2 up or down. R4
(carbamate reversion) is the one lever whose effect changes sign with loading, but it changes
sign only once, from + to −. The residual needs up, then down, then up. That shape lies outside
the span of these three constants.

**Linear corrections (prediction, 77 states):**

| correction | ln K shifts | RMS after |
|---|---|---:|
| ±0.3 ln K on R2, R4, R5 (nominal source-sized bound) | −0.19, −0.13, −0.30 | 0.558 |
| unbounded constant shifts on R2, R4, R5 | −5.56, −0.01, −5.44 | 0.467 |
| unbounded constant plus 1/T term, 6 coordinates | intercepts −12.1, +0.3, −11.3 | 0.363 |

The unbounded shifts are far outside the linear range and any source uncertainty. They are
reported only to show that the residual is mostly orthogonal to the reaction constants.

**Basis and units.** Checked, and consistent:

- The observed values are kPa × 1000, giving Pa.
- Loading is total CO2 per mol MEA in both sources and in the packet feed.
- Every state is 30 wt% MEA, which is 7 m in Hilliard.
- The vapor holds only molecular CO2. The target is y_CO2·P, the same quantity both sources
  report (Jou 1995 p. 142: CO2 partial pressure from the GC N2/CO2 ratio after subtracting the
  Raoult solvent pressure).

The CO2 physical-solubility path (the CO2–water EOS pair) was not perturbed; see Limits.

### (a) Data: **supported as a secondary contributor and floor** (observations)

**Between-source offset.** Jou's observed ln pCO2 was interpolated linearly in loading, at the
same temperature, to each Hilliard loading. Hilliard sits above Jou by mean +0.17 and RMS 0.23
over 31 states: +0.19 at 40 °C (24 states) and +0.13 at 60 °C (7 states).

The per-source difference in the misfit (+0.34 for Hilliard against +0.05 for Jou) comes mostly
from coverage, not from inconsistency between the sources. In the matched window (loading
0.15–0.52), the model over-predicts both sources: Hilliard +0.43 and Jou +0.62 at 40 °C. Jou's
mean is lower overall because it includes the under-predicted high-loading rows and the
80–120 °C rows.

Hilliard 2008 (§2.4.3, Fig. 2.4-5, printed p. 37) reports its 7 m MEA data as consistent with Jou
1995 at 40 and 60 °C.

**Scatter floor.** Two estimates agree:

- The stated loading uncertainty is 2% relative. Hilliard 2008 §2.3.4, printed pp. 28–29, gives
  vapor ±2% expanded and loading ±2% standard. Jou 1995 p. 141 gives ±3% for BaCO3 and ±2% for
  GC. Propagated through the observed local slope d ln p/dα, that is 0.04 in ln below loading
  0.3 and 0.28–0.31 above it (RMS 0.31 over all states).
- Differences in the residual between adjacent loadings within a (source, T) group give a
  scatter of at most 0.30 in ln. This is an upper bound, because model curvature is included.

Both match the 0.27 left after removing the loading-bin means. Some observed curves are
non-monotone, for example Jou 100 °C at loadings 0.571/0.589 (509/376 kPa) and Hilliard 40 °C
at 0.382–0.389.

**Benchmark.** Hilliard's own fitted eNRTL model gets pCO2 AARD of 30.0% on the Hilliard data
and 13.6% on Jou (Hilliard 2008 Table 13.4-6, printed p. 447). The present model gets 67% and
57%. The data therefore allow a fit about 2–4× better than the adopted record.

**Specific outliers.** No single state drives the result. The largest misses belong to the
systematic high- and mid-loading groups.

## Physical meaning

pCO2 in loaded MEA is set by how the CO2 is shared between carbamate, bicarbonate and molecular
CO2, weighted by activities. The observed misfit shape has three parts:

- Too little free CO2 at low loading.
- Too much in the carbamate plateau.
- Too little rise past loading 0.5, where bicarbonate and physical CO2 take over.

That points to how the model's non-ideality varies with composition (ionic strength and the
MEAH+/MEACOO−/HCO3− interactions) rather than to a single wrong equilibrium constant. A wrong
constant scales pCO2 almost uniformly, or monotonically in loading for R4.

The model is too flat in the plateau and too shallow at high loading. Because of that, the
enthalpy-only reaction fit could improve pressure RMSE only on average. Its record already notes
that the shifts "compensate other temperature-dependent model deficiencies".

## Limits

- The sensitivities are local finite differences (+0.05 ln K, forward), and the corrections are
  linear. The unbounded solutions extrapolate far past validity and only show direction.
- The ±0.3 ln K bound is nominal. Source uncertainties for R2, R4 and R5 were not transcribed.
- R1 and R3 were not perturbed. R1 is water autoprotolysis and R3 is bicarbonate/carbonate. At
  these states the adoption screen found them near-null (column norms 1.6e-5 and 0.0033 log10
  per kJ/mol).
- CO2 physical solubility (the CO2–water EOS pair and the neutral reference) and the residual
  ionic parameters were not perturbed. This diagnosis shows the residual lies outside the
  reaction span. It does not show that those parameters can close it.
- Jou's rows are N2-carrier measurements mapped onto a neutral-only bubble at a different total
  pressure (migration record, "Reactive VLE"). The Poynting-type effect is estimated below 0.01
  in ln at 200 kPa. This is an estimate, not a solve.
- All 79 rows are labelled calibration. The Jou group w=0.3/T=80 °C is a grouped-manifest
  validation reservation (a lineage conflict recorded in the migration record). Nothing here is
  independent validation.

## Next step that would resolve what remains

Run the same bounded falsifier with the residual EOS coordinates instead of ln K. Take d ln pCO2
over the 79 states with respect to:

- The CO2–water binary parameter.
- The MEAH+/MEACOO− dispersion or size parameters.
- The MEAH+–MEACOO− ion-pair interaction parameter.

Then check whether an up–down–up loading shape lies in their span.

- **If it does,** a pCO2-weighted refit of those parameters is the design question. Route that
  to `cse:design`, with speciation held as a constraint and Xu 2011 kept as the only held-out
  pressure block.
- **If it does not,** the ePC-SAFT ionic formulation (Born/permittivity or ion-pair treatment) is
  the limitation. Either way, about 0.3 in ln RMS is the data floor. No fit should be asked to go
  below it on these two sources.
